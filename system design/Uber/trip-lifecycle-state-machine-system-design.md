# System Design: Trip Lifecycle & State Machine

> **Focus areas:** Marketplace trip FSM · Idempotent transitions · Dual-sided consents · Timers/SLA · Cancel/refund hooks · Exactly-once effects · Multi-product trips  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit states/events, illegal transitions rejected, timer ownership clear, money side-effects fenced  
> **Interview theme:** Uber — **trip as a durable state machine** coordinating rider, driver, pricing, matching, payments

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design the **system of record for a trip’s lifecycle**—from request through matching, pickup, en-route, completion/cancel—with **strict transition rules**, timers, and integration events to pricing, dispatch, notifications, and payments.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Trip FSM + durable trip entity | Matching algorithm internals |
| Truth | Trip state & participants | GPS trail store (consumes location) |
| Money | Emit fare/payment commands | Card network |
| Uber lens | Correctness under retries | UML-only academic FSM |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | States? | Requested→…→Completed/Canceled | Explicit enum + version |
| F2 | Who transitions? | Services + user actions via API | Authz per event |
| F3 | Matching? | External matcher proposes driver | Offer sub-state or sibling entity |
| F4 | Multi-offer? | Sequential or parallel offers | Offer FSM linked to trip |
| F5 | Timers? | Offer timeout, arrival SLA, cancel windows | Timer service / wheel |
| F6 | Idempotency? | Mobile retries galore | event_id / command_id |
| F7 | History? | Full transition audit | Event log |
| F8 | Products? | Ride, shared, reserved | Product-specific extensions |
| F9 | Shared rides? | Multiple riders | Trip legs / parties model |
| F10 | Terminal money? | Complete → finalize fare → capture | Outbox to payments |
| F11 | Support ops? | Force cancel, reassign | Admin commands audited |
| F12 | Notifications? | On key transitions | Domain events |

**MVP scope:**

1. Create trip with bound quote.  
2. Matching offers driver; accept/reject/timeout.  
3. States: `REQUESTED`, `MATCHING`, `DRIVER_ASSIGNED`, `DRIVER_ARRIVED`, `IN_TRIP`, `COMPLETED`, `CANCELED`.  
4. Cancel reasons with fee policy hooks.  
5. Durable event log + idempotent commands.  
6. Outbox events for notify/pay/analytics.

**Out of MVP:** multi-hop airport shuttles, full shared-ride optimization, cross-region active-active trip writes.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Transition latency | p99 < 100–200ms |
| N2 | Durability | No lost accepted transitions |
| N3 | Consistency | Single-writer per trip_id |
| N4 | Availability | City cell isolation |
| N5 | Audit | Every transition explainable |
| N6 | Clock | Server timers; don’t trust client |
| N7 | Exactly-once effects | Outbox + idempotent consumers |
| N8 | Scale | See table |

### 1.3 Cases

**Happy:** Request → match → assign → arrive → start → complete → pay.  
**Edges:** offer timeout; driver cancel after assign; rider cancel fee windows; double-complete; reassign; payment fail after complete; reserved no-show; concurrent arrive/cancel; app kill mid-transition.

| Case | Behavior |
|------|----------|
| Duplicate complete | Idempotent; same terminal receipt |
| Offer accept after timeout | Reject; trip still MATCHING |
| Driver and rider cancel race | CAS version; one wins; other 409 |
| Matcher assigns busy driver | Guard with driver presence lease |
| Payment capture fail | Trip COMPLETED; payment retry state separate |
| Illegal transition | 409 / 422; no partial side effects |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Trips created / day | 1M | 10M | 100M | 1B |
| Peak create QPS | 100 | 1K | 10K | 100K |
| Peak transitions / s | 500 | 5K | 50K | 500K |
| Concurrent active trips | 50K | 500K | 5M | 50M |
| Offers / trip avg | 1.3 | 1.5 | 2 | 2+ |
| Cities | 1–5 | 50 | 500 | 2000+ |

**Jumps:** 10× shard by city/trip_id; 100× event-sourced trip log + timers fleet; 1,000× cell isolation, hierarchical services, strict outbox partitioning.

### 1.5 Scope repeat-back

> Durable trip lifecycle service: single-writer state machine per trip, offer subcycle, server-side timers, idempotent commands, outbox domain events to payments/notifications/analytics—scaled by city/trip shards.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Transition volume

```text
1M trips/day × ~8 transitions ≈ 8M events/day
Peak 5× → transition QPS ~500 (matches table)

1000×: 1B trips/day × 8 = 8B events/day ≈ 90K/s avg; peak ~0.5M/s
```

### 2.2 Storage

```text
Trip row ~1–2 KB; event ~200–500 B × 8 ≈ 2–4 KB/trip
1M/day → ~4 GB/day hot
1000× → ~4 TB/day → tiered storage; hot active + recent terminal
```

### 2.3 Timers

```text
Active offers ~ concurrent matching trips
50K active × 1 timer = trivial
5M active timers → dedicated timer wheels / delay queues sharded
```

### 2.4 Bottlenecks

1. Hot trip_id partitions under retry storms  
2. Timer thundering herds (stadium start)  
3. Dual writes without outbox  
4. Cross-service sync calls on transition critical path  
5. Admin force operations bypassing invariants  

---

## 3. High-Level Design

### 3.1 Canonical state machine (MVP rides)

```text
REQUESTED
   → MATCHING
       → DRIVER_ASSIGNED (offer accepted)
           → DRIVER_ARRIVED
               → IN_TRIP
                   → COMPLETED
       → CANCELED
   → CANCELED

DRIVER_ASSIGNED → CANCELED / REMATCHING→MATCHING (policy)
```

**Offer sub-FSM:** `PENDING → ACCEPTED|REJECTED|EXPIRED|WITHDRAWN`.

### 3.2 Command vs event

```text
Command (API): StartTrip, Arrive, Complete, Cancel...
  → validate authz + precondition
  → append Event
  → update projection (trip row)
  → outbox SideEffect
```

### 3.3 Options: persistence

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Row + status enum | Simple | Weaker audit | Need disputes years later w/o events |
| B. Event sourced | Perfect audit | Harder reads | Team can’t operate |
| C. Row + append event log | Pragmatic | Dual write risk | No transactional outbox |

**Chosen:** **Transactional trip row + event log + outbox** in one DB partition (or equivalent ACID store) per shard.

### 3.4 Single-writer invariant

```text
shard = hash(trip_id) or city_id + hash(trip_id)
all mutations for trip go to owning shard / actor
optimistic version column OR serial event numbers
```

### 3.5 Timers

```text
Schedule(timer_id=offer:{id}, due=now+T, command=ExpireOffer)
On fire: send command with fencing timer_generation
Cancel timer on accept
```

**Deal-breaker:** Client-side-only timeouts as source of truth.

### 3.6 Side effects

| Transition | Effects |
|------------|---------|
| Assigned | Notify rider/driver; lock driver |
| Arrived | Notify rider |
| InTrip | Start billing clock hooks |
| Completed | Fare finalize; payment capture; unlock driver |
| Canceled | Fee; release driver; notify |

Use **outbox** so DB commit and emit are atomic.

### 3.7 API sketch

```text
POST /trips {quote_id, ...} → trip_id
POST /trips/{id}/commands/{command_type}
  Idempotency-Key: ...
  body: {expected_version?, payload}
GET  /trips/{id}
GET  /trips/{id}/events
```

### 3.8 Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Rich FSM | Correctness vs product flexibility |
| Sync matching call | Simpler vs coupling/latency |
| Rematch in-place | UX continuity vs state complexity |
| Event sourcing pure | Audit vs operational cost |

---

## 4. Architecture Diagram

```text
  Rider/Driver Apps
          |
          v
     API Gateway
          |
          v
  +-------------------+     +------------------+
  | Trip Command Svc  |---->| Matching / Offer |
  | (per-city shard)  |     +------------------+
  +---------+---------+
            |
            v
  +-------------------+
  | Trip Store (ACID) |
  | row + events     |
  | + outbox          |
  +---------+---------+
            |
            v
     Outbox Relay → Kafka topics: trip.events
            |
    +-------+--------+----------+
    v       v        v          v
 Notify   Payments  Analytics  Location/ETA
            |
            v
       Timer Service ---- commands ---> Trip Command Svc
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- **Idempotency keys** on all commands.  
- **Optimistic concurrency** (`version` / `event_seq`).  
- **Fenced timers** (`timer_gen`).  
- **Outbox** for at-least-once publish; consumers idempotent on `event_id`.  
- Illegal transitions leave no partial external effects (validate before side effects).  
- Payment failures do not un-complete trip; enter `payment_status` subfield.

### 5.2 Scalability

- Shard by city then trip_id.  
- Keep transition path free of heavy sync dependencies (async notify).  
- Hot celebrity stadium: more shards; timer jitter.  
- Archive terminal trips from primary after N days to cold store; keep summary.

### 5.3 Maintainability

- Transition table as data/code reviewed carefully.  
- Product flags for experimental states.  
- Projection rebuild from events for a trip.  
- Chaos: duplicate commands, late timers, matcher lies.

### 5.4 Consistency boundaries

| Entity | Writer |
|--------|--------|
| Trip state | Trip service |
| Driver busy lock | Presence/dispatch with trip fencing |
| Quote bind | Pricing on create |
| Payment intent | Payments on outbox command |

**Saga style:** trip completion emits `CaptureFare`; compensation via refunds, not silent state rewind without audit.

### 5.5 Cancel policy hooks

```text
Cancel(actor, reason, ts):
  window = policy.Window(trip.state, trip.timestamps)
  fee = policy.Fee(window, reason)
  transition → CANCELED
  outbox CancelFee / ReleaseDriver / Notify
```

---

## 6. Wrap-Up

> Trip service is the **single-writer FSM** for marketplace journeys. Commands are idempotent, timers are server-owned, side effects go through **outbox events**, and money capture is downstream—not a reason to corrupt trip terminal state. Scale with city/trip shards; evolve shared-ride as party/leg extensions, not by forking core blindly.

---

## 7. Deeper / Related Interview Questions

### 7.1 FSM design

**Q: Offer as part of trip state or separate?**  
A: Prefer separate `Offer` entity; trip stays `MATCHING` until accepted—cleaner parallel offers.

**Q: How many states is too many?**  
A: Keep core < ~12; put nuance in attributes (`cancel_reason`, `payment_status`).

**Q: Rematch vs new trip?**  
A: Product choice; rematch preserves trip_id/quote policy carefully.

### 7.2 Concurrency

**Q: Two completes?**  
A: First CAS wins; second idempotent success if same actor/payload; else 409.

**Q: Driver arrives after rider cancel?**  
A: Cancel wins if version advanced; arrive rejected; notify driver.

### 7.3 Timers

**Q: Delay queue vs Redis ZSET vs dedicated wheel?**  
A: MVP ZSET/SQS delay; 100×+ sharded timer service with lease.

**Q: Late timer after accept?**  
A: Timer generation mismatch → no-op.

### 7.4 Money

**Q: Complete before payment success?**  
A: Yes; payment is separate state machine. Don’t block physical trip completion on PSP.

**Q: Refunds?**  
A: New commands producing payment refund intents; don’t delete history.

### 7.5 Multi-region

**Q: Rider abroad requesting city trip?**  
A: Trip home = city region; API routed accordingly.

**Q: Active-active trip mutations?**  
A: Avoid; home cell single writer.

### 7.6 Shared rides

**Q: Model?**  
A: `Trip` + `Stop`/`Leg` + `Party`; state is product of legs—start simple with sequential stops.

### 7.7 Support tools

**Q: Force complete?**  
A: Admin command with reason + dual control; still append events.

### 7.8 Comparison

**Q: vs workflow engine (Temporal)?**  
A: Viable for timers/sagas; still need clear domain model. Many companies use custom FSM + outbox for core trips.

### 7.9 Observability

**Q: Stuck in MATCHING?**  
A: Metrics on state age; alerts; automatic expire/cancel policies.

### 7.10 Interview traps

**Q: Store only current state?**  
A: Insufficient for disputes; keep event history.

**Q: Call payments synchronously inside DB transaction?**  
A: No—timeouts/locks; use outbox.

---

## 8. Appendices

### 8.1 Transition table (excerpt)

| From | Event | To | Guards |
|------|-------|-----|--------|
| REQUESTED | StartMatching | MATCHING | quote bound |
| MATCHING | OfferAccepted | DRIVER_ASSIGNED | offer valid |
| MATCHING | CancelByRider | CANCELED | — |
| DRIVER_ASSIGNED | Arrive | DRIVER_ARRIVED | actor=driver |
| DRIVER_ARRIVED | Start | IN_TRIP | geofence optional |
| IN_TRIP | Complete | COMPLETED | actor=driver/system |
| DRIVER_ASSIGNED | Cancel | CANCELED/MATCHING | policy |

### 8.2 Schemas

```sql
trips(
  trip_id UUID PRIMARY KEY,
  city_id TEXT,
  state TEXT,
  version BIGINT,
  rider_id UUID,
  driver_id UUID NULL,
  quote_id UUID,
  product_id TEXT,
  created_at, updated_at
);

trip_events(
  trip_id UUID,
  seq BIGINT,
  event_type TEXT,
  actor_type TEXT,
  actor_id UUID,
  payload JSONB,
  command_id UUID,
  at TIMESTAMPTZ,
  PRIMARY KEY(trip_id, seq)
);

outbox(
  id UUID PRIMARY KEY,
  topic TEXT,
  key TEXT,
  payload JSONB,
  created_at TIMESTAMPTZ
);

idempotency(
  scope TEXT,
  key TEXT,
  response_ref TEXT,
  PRIMARY KEY(scope, key)
);
```

### 8.3 Pseudocode: handle command

```text
function Handle(trip_id, cmd):
  return withTransaction(shard(trip_id)):
    if seen(cmd.idempotency_key): return prior
    trip = lockTrip(trip_id)
    assertCanTransition(trip, cmd)
    ev = nextEvent(trip, cmd)
    trip.apply(ev)
    insertEvent(ev)
    insertOutbox(project(ev))
    saveIdempotency(...)
    return trip
```

### 8.4 Domain events (Kafka)

```text
trip.requested, trip.matching_started, trip.driver_assigned,
trip.driver_arrived, trip.started, trip.completed, trip.canceled,
offer.created, offer.expired, offer.accepted
```

### 8.5 Timer types

| Timer | Default (illustrative) |
|-------|------------------------|
| Offer expiry | 15s |
| Matching overall | 2–5 min |
| Arrival wait cancel window | product-specific |
| Reserved pickup | scheduled |

### 8.6 Authz matrix

| Actor | Arrive | Start | Complete | Cancel |
|-------|--------|-------|----------|--------|
| Rider | no | no | limited | yes (policy) |
| Driver | yes | yes | yes | yes (policy) |
| System | yes | yes | yes | yes |
| Support | force* | force* | force* | force* |

### 8.7 Payment coupling

```text
COMPLETED event → FareFinalize → PaymentCaptureCommand(idempotent trip_id)
payment.failed → trip.payment_status=FAILED_RETRYABLE (trip state remains COMPLETED)
```

### 8.8 Metrics

- `transition_latency_ms`  
- `illegal_transition_count`  
- `state_age_seconds{state}`  
- `timer_fire_lag_ms`  
- `outbox_lag_ms`  
- `idempotent_hit_ratio`  

### 8.9 Failure injection

- Duplicate Complete with different timestamps  
- ExpireOffer after Accept  
- Outbox relay down 10 min  
- Matcher assigns same driver to two trips  
- Clock jump on timer node  

### 8.10 Interview checklist

- [ ] Explicit states + illegal rejection  
- [ ] Idempotent commands  
- [ ] Version CAS  
- [ ] Server timers with fencing  
- [ ] Outbox side effects  
- [ ] Cancel fee hooks  
- [ ] Payment decoupled  
- [ ] Audit events  
- [ ] City/trip sharding  
- [ ] Rematch/offer model clarity  

---

## 9. Extended Deep Dive (Interview Amplifiers)

### 9.1 Why trip is the system of record

Matching, pricing, notifications, and payments are satellites. If those disagree, **trip events** decide what happened for support and safety. Therefore mutations are single-writer per `trip_id` with monotonic `seq`/`version`.

### 9.2 Offer parallelism

```text
Trip MATCHING
  Offer1 PENDING
  Offer2 PENDING  // optional parallel
On first ACCEPTED: withdraw others; trip → DRIVER_ASSIGNED
```

Keep offers as child entities so trip state stays readable.

### 9.3 Rematch policy

After driver cancel, either:
- rematch in-place (same trip_id, new offer cycle), or
- cancel + new trip.

In-place rematch preserves quote binding policies carefully—document whether price can change.

### 9.4 Geofence start/complete (optional)

Optional guards: start only near pickup; complete near dropoff. Soft vs hard enforcement is product/safety specific. Never rely solely on client assertions.

### 9.5 Outbox event catalog

```text
trip.requested, trip.matching_started, trip.driver_assigned,
trip.driver_arrived, trip.started, trip.completed, trip.canceled,
offer.created, offer.accepted, offer.expired, offer.withdrawn
```

Consumers: notify, payments, analytics, safety, ETA.

### 9.6 Payment decoupling detail

```text
COMPLETED → FareFinalizeCommand → PaymentCapture (idempotent by trip_id)
payment failure ≠ uncomplete trip
trip.payment_status tracks money separately
```

### 9.7 Support force actions

Admin commands still append events with `actor_type=SUPPORT`, reason codes, and dual-control for irreversible money-impacting forces.

### 9.8 Stuck-state detector

Alert on `state_age_seconds{MATCHING|DRIVER_ASSIGNED}` beyond SLO. Auto-expire matching; page on assigned-without-arrive anomalies.

### 9.9 Shared ride extension sketch

```text
Trip
  parties[]
  stops[] (pickup/dropoff sequence)
  leg_state derived from stop progress
```

Do not explode core FSM into dozens of product-specific enums on day one.

### 9.10 Reliability drills

- Duplicate Complete commands
- ExpireOffer after Accept (timer fence)
- Outbox relay down
- Matcher assigns busy driver (presence lease)
- Concurrent rider cancel + driver arrive

*End of trip lifecycle state machine system design.*

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).
