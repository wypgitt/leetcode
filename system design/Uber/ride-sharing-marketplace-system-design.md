# System Design: Uber Ride-Sharing Marketplace (End-to-End)

> **Focus areas:** Marketplace state machine · Dispatch/matching · Geospatial index · Surge pricing · Trip lifecycle · Payments · Realtime tracking · Idempotency · City cells  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — the “design Uber” question; breadth with sharp correctness on matching & money  
> **Quality bar:** Planes split; no double-assign; progressive city scale; honest MVP vs global optimizer

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

Goal: design the **ride-sharing marketplace**—riders request trips, drivers are matched, trips are tracked and completed, payments settle—under city-scale peaks, failures, and fraud.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Product | Entire rides marketplace (request→pay) | Only matching LLD / only payments |
| Scope | Multi-city platform | Building roads / maps from scratch |
| Depth | HLD with critical deep dives | Every ML pricing paper |
| Related | Matching, surge, trip SM, locations as subsystems | Treat each as separate interview unless asked |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Products? | UberX-like MVP; Pool/Reserve later | Product codes on trip |
| F2 | Request? | Pickup, dropoff, product → ETA/price → confirm | Quote binding |
| F3 | Matching? | Nearby drivers; offer/accept or auto | Dispatch service |
| F4 | Tracking? | Mutual location + ETA | Streaming locations |
| F5 | Trip states? | Full lifecycle to complete/cancel | Hard state machine |
| F6 | Pricing? | Upfront fare + surge | Pricing service |
| F7 | Payments? | Capture on complete; tips | Idempotent payments |
| F8 | Ratings? | Two-sided | After trip |
| F9 | Safety? | Share trip, SOS hooks | Safety services |
| F10 | Driver supply? | On-duty toggle; docs | Driver status |
| F11 | Multi-hop? | No MVP | Defer |
| F12 | Airport queues? | Phase 2 | Special zones |

**MVP scope:**

1. Rider sees ETA/price quote; confirms trip with idempotency.  
2. Payment method auth/hold.  
3. Dispatch matches eligible nearby driver (exclusive).  
4. Driver navigates; both track; trip completes.  
5. Fare capture; ratings.  
6. Cancels/reassigns with policies.  
7. Basic surge when demand≫supply.

**Out of MVP:** autonomous vehicles, global single optimization across all cities, full Uber Eats, complex pooling matching.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Quote p99 | < 500ms |
| N2 | Time-to-match (dense) | p50 < 15s, p99 < 60s |
| N3 | Location freshness | p95 < 5–10s |
| N4 | No double dispatch | Invariant |
| N5 | Payment correctness | No silent double charge |
| N6 | City isolation | Outage blast radius limited |
| N7 | Peak | Friday night / rain / stadium 5–20× |
| N8 | Audit | Full trip timeline |

### 1.3 Cases

**Happy:** Quote → confirm → match → pickup → dropoff → pay → rate.  

| Case | Behavior |
|------|----------|
| No drivers | Queue / longer ETA / fail quote |
| Driver cancel after accept | Re-dispatch; rider messaging |
| Rider cancel | Fee policy by state |
| Double confirm tap | One trip |
| Payment fail | No dispatch |
| GPS spoof | Fraud signals |
| Surge spike | Transparent multiplier |
| Driver offline mid-trip | Safety + reassign protocols |
| Stadium egress | Zone heat; batching ops tools |
| Split fare | Phase 2 |

### 1.4 Progressive scale

| Metric | 1 city | 10× | 100× | 1,000× |
|--------|--------|-----|------|--------|
| Cities | 1 | 10 | 100 | 1,000 |
| Trips / day | 200K | 2M | 20M | 200M |
| Peak requests / s | ~20 | ~200 | ~2K | ~20K |
| On-duty drivers | 5K | 50K | 500K | 5M |
| Location QPS | ~5K | ~50K | ~500K | ~5M |
| Concurrent trips | 10K | 100K | 1M | 10M |

**Jumps:** 10× multi-city platform; 100× city cells + geo shards; 1,000× product multiplicity + hierarchical dispatch + global platform ops.

### 1.5 Scope repeat-back

> Multi-city ride marketplace with quote/pricing, idempotent trip create + payment hold, geo dispatch without double-assign, streaming track, completion settlement, surge, and city-cell isolation—evolving from one city to 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Classes

| Class | 1-city peak | 100× | Notes |
|-------|-------------|------|-------|
| Quotes | 100/s | 10K/s | Cache maps/ETA |
| Confirms | 20/s | 2K/s | Durable |
| Dispatch decisions | 20/s | 2K/s | Bursty |
| Locations | 5K/s | 500K/s | Dominant |
| Track subscribers | 20K/s msgs | 2M/s | Fan-out |
| Payment ops | 20/s | 2K/s | Critical |

### 2.2 Matching math

```text
Request → radius search 2–5 km → tens of candidates → score → offer K=3–10
Offer TTL 15s; accept CAS
Concurrent trips 10K; each needs location stream + map
```

### 2.3 Storage

```text
Trip row ~2 KB; 200K/day → 400 MB/day metadata
Locations: 5K/s × 150 B ≈ 750 KB/s → ~65 GB/day raw → TTL/downsample
```

### 2.4 Bottlenecks

1. Downtown geo hotspots  
2. Matching under supply shock  
3. Payment provider  
4. Location fan-out  
5. Monolithic global matcher (anti-pattern)

---

## 3. High-Level Design

### 3.1 Planes

| Plane | SoT | Notes |
|-------|-----|-------|
| Trip lifecycle | Trip service DB | Strong per trip |
| Dispatch | Offer/assign records | CAS exclusive |
| Location | Geo index + stream | Freshness, not money |
| Pricing | Quote records | Bound on confirm |
| Payments | Payment intents | Idempotent |
| Map/ETA | Routing providers | Cached |
| Notifications | Best-effort + important durable | |

**Deal-breaker:** Location store as trip SoT; or pricing without quote bind.

### 3.2 Trip state machine

```text
QUOTED → REQUESTED → MATCHING → MATCHED → DRIVER_ARRIVING → ARRIVED
→ IN_TRIP → COMPLETED → PAID
Any → CANCELLED (policy)
MATCHED → MATCHING on driver cancel (re-dispatch)
```

### 3.3 Matching options

| Mode | Pros | Cons |
|------|------|------|
| Auto-assign | Fast | Driver rejects |
| Offer/accept | Choice | Latency |
| Batch matching | Efficiency | Complexity |

**MVP:** Score candidates; offer top-K; first accept wins CAS; else expand radius / wait.

### 3.4 Surge

```text
zone_cell demand / supply → multiplier m in [1, m_max]
quote uses m; show transparency
update every 30–60s; hysteresis to avoid flicker
```

### 3.5 Payments flow

```text
confirm → create trip → auth/hold estimated fare
complete → compute final fare → capture
cancel → void/partial capture per policy
idempotency keys on all money ops
```

### 3.6 Trade-offs

| Topic | Choice | Why | Deal-breaker |
|-------|--------|-----|--------------|
| Isolation | City/zone cells | Blast radius | One global lock |
| Assign | CAS + epoch | Correctness | Best-effort notify |
| Locations | Separate ingest | Scale | Trip row updates |
| Upfront pricing | Quote snapshot | Trust | Silent reprice |
| Pooling | Defer | Complexity | Forced in MVP |

### 3.7 Components

1. Rider API  
2. Driver API / gateway  
3. Quote & Pricing (+ surge)  
4. Trip Service  
5. Dispatch / Matching  
6. Location Ingest & Geo Index  
7. Tracking Fan-out  
8. Payments  
9. Notifications  
10. Ratings / Safety  
11. Maps/ETA adapter  
12. Fraud / Risk  
13. Config (cities, products)  

---

## 4. Architecture Diagram

```text
Rider App                         Driver App
   |                                  |
   v                                  v
Rider Gateway                    Driver Gateway
   |                                  |
   +--> Pricing/Surge <--> Zone metrics <--+-- Location Ingest --> Geo Index
   |                                  |
   +--> Trip Service <--------> Dispatch (city shards)
   |         |                        |
   |         +------ offers/CAS ------+
   |         |
   |         +--> Payments
   |         +--> Timeline/Outbox --> Notify
   |
   +--> Track WS <--- pub/sub by trip_id
```

### 4.1 Confirm → match

```text
Rider confirm → Trip REQUESTED → Payment hold OK → MATCHING
Dispatch: geo candidates → offers → Accept CAS → MATCHED
Push both sides; start tracking topics
```

### 4.2 Complete → pay

```text
Driver complete → fare calc (distance/time/surge/tolls)
→ Payments capture idempotent → PAID → ask ratings
```

### 4.3 City cell

```text
city_id / dispatch_cell owns matcher + on-duty set
platform services (payments, identity) shared with tenancy keys
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Idempotent trip create.  
2. Payment hold before matching (or explicit risk exception).  
3. Exclusive driver assignment via CAS + `assign_epoch`.  
4. Legal state transitions only.  
5. Driver heartbeat on active trip; miss → protocols.  
6. Fare computation deterministic from trip meter events.  
7. Outbox timeline for every transition.  
8. City dispatch degrade → stop new requests in that city.  
9. Fraud checks on complete (teleport).  
10. Rider/driver authz on track channel.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | One city; Redis geo; PG trips; Stripe-like |
| 10× | Multi-city config; shared location bus |
| 100× | Cells; surge; ETA ML; payment partitioning |
| 1000× | Hierarchical matching; product lines; global ops |

### 5.3 Maintainability

- Product & city config as data.  
- Matcher scorer versioning + simulation.  
- Game-day peak drills.  
- Clear SEV ownership per plane.  

### 5.4 Progressive scale narrative

**1×:** Modular monolith possible; simple nearest driver.  
**10×:** Standardized city onboarding; shared platform.  
**100×:** Cell isolation; stream processing for metrics/surge; richer fraud.  
**1000×:** Airport queues, pooling, reserved rides as add-on systems; still cell-local dispatch.

### 5.5 Matching score sketch

```text
score = w1*eta + w2*(1-accept_prob) + w3*fairness_idle + w4*rating_penalty
filters: product, seats, directionality optional, not banned
```

### 5.6 Re-dispatch

```text
on driver_cancel or timeout:
  increment assign_epoch; clear driver; MATCHING
  notify rider; preserve quote constraints within policy
  max_redispatch then cancel with apology credits
```

### 5.7 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Dual assign | Two drivers one rider |
| Global matcher | Outage & latency |
| GPS into trip OLTP | Melt |
| Non-idempotent pay | Double charge |
| Ignore city closed | Unsafe / unservable |
| Client-side matching | Cheating |

---

## 6. Wrap-Up

### 6.1 Designed

End-to-end rides marketplace: pricing/surge quotes, idempotent trips + payment holds, geo dispatch with exclusive assign, location streaming/tracking, completion settlement, ratings/safety hooks, city cells.

### 6.2 Decisions to defend

1. Plane separation  
2. City/zone cells  
3. CAS assignment + epochs  
4. Quote binding + surge transparency  
5. Locations off OLTP  
6. Idempotent payments  
7. Fail closed per city  

### 6.3 Risks

- Supply shocks  
- Map/ETA provider  
- Payment blips  
- Fraud rings  
- Regulatory per city  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | MVP scope; defer pool |
| 5–15 | Trip SM + payments |
| 15–28 | Matching + geo |
| 28–36 | Tracking + surge |
| 36–45 | Cells, peaks, traps |

### 6.5 Closer

> **Uber marketplace:** city-cell dispatch with exclusive CAS matching, bound quotes/surge, streaming locations on a separate plane, idempotent money, full trip state machine—scale by cells not a global lock.

---

## 7. Deeper / Related Interview Questions

### 7.1 Matching

**Q: Batch vs 1:1 matching?**  
A: Batch can raise efficiency/pooling; harder. MVP 1:1 greedy with good scoring.

**Q: How large K for offers?**  
A: Small (3–5) to avoid pile-on; expand if needed.

**Q: Idle fairness?**  
A: Boost long-idle drivers; avoid starvation.

### 7.2 Geospatial

**Q: H3 resolution?**  
A: City-dependent; balance candidate set size vs query count.

**Q: One-way roads / ETA?**  
A: Use routing ETA not haversine for production ranking.

### 7.3 Pricing

**Q: Upfront vs post-trip?**  
A: Upfront trust; final may adjust tolls/wait—policy disclosure.

**Q: Surge oscillation?**  
A: Hysteresis + max step change.

### 7.4 Consistency

**Q: Two drivers accept?**  
A: CAS one winner; revoke loser.

**Q: Rider sees matched before driver?**  
A: Atomic transition then notify; tolerate seconds of skew.

### 7.5 Payments

**Q: Auth amount?**  
A: Estimate + buffer; incremental auth if needed.

**Q: Tips?**  
A: Separate capture or adjustment; idempotent tip_id.

### 7.6 Safety

**Q: Share trip?**  
A: Time-boxed tokenized track link.  
**Q: SOS?**  
A: Priority notify + location snapshot—partner integrations.

### 7.7 Peaks

**Q: Concert lets out?**  
A: Predict; pre-position; surge; temporary geofence pickup points; ops tooling.

### 7.8 Interview traps

| Trap | Pushback |
|------|----------|
| Design only UI screens | Need planes |
| ML matching before CAS story | Wrong order |
| One DB for everything forever | Won’t scale locations |
| “Kafka assigns drivers” | Still need exclusive state |

### 7.9 Metrics

| Metric | Why |
|--------|-----|
| Mean time to match | Liquidity |
| Dispatch cancel rate | Health |
| ETA error | Trust |
| Surge awareness | Transparency |
| Payment success | Revenue |
| Safety incidents | Non-negotiable |

### 7.10 Subsystem map for interviewers

If they narrow: go deeper on matching **or** payments **or** locations—keep interfaces clean so you can zoom.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
trips(
  trip_id UUID PK,
  idempotency_key TEXT UNIQUE,
  city_id TEXT,
  rider_id UUID,
  driver_id UUID NULL,
  product TEXT,
  state TEXT,
  assign_epoch INT,
  quote_id UUID,
  pickup GEO, dropoff GEO,
  fare_snapshot JSONB,
  payment_intent_id TEXT,
  created_at, updated_at)

trip_events(trip_id, ts, type, actor, payload)

offers(offer_id, trip_id, driver_id, expires_at, state)

driver_sessions(driver_id, city_id, on_duty, last_cell, last_pos, updated_at)

quotes(quote_id, rider_id, price, surge_m, eta_s, expires_at, inputs_hash)
```

### 8.2 API checklist

- [ ] `POST /v1/quotes`  
- [ ] `POST /v1/trips` + Idempotency-Key  
- [ ] `POST /v1/trips/{id}/cancel`  
- [ ] Driver `POST /offers/{id}/accept`  
- [ ] `POST /v1/locations`  
- [ ] WS track `/v1/trips/{id}/stream`  
- [ ] `POST /v1/trips/{id}/complete`  
- [ ] `POST /v1/trips/{id}/tip`  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Dispatch cell | Matching isolation unit |
| Assign epoch | Fencing for re-dispatch |
| Surge multiplier | Demand/supply price factor |
| Upfront fare | Bound quote price |
| On-duty | Eligible for offers |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Trip SM, geo match, pay hold, track |
| 10× | Multi-city, shared platform |
| 100× | Cells, surge, fraud, stream metrics |
| 1000× | Product variants, hierarchical match, ops |

### 8.5 Accept CAS

```text
tx:
  if trip.state!=MATCHING: fail
  if offer expired: fail
  trip.driver_id = driver
  trip.state = MATCHED
  trip.assign_epoch += 1
  accept offer; revoke others
```

### 8.6 Location path

```text
Driver ping → validate → geo upsert → if on trip: publish trip topic
Rider map subscribes trip topic (authz)
Downsample idle drivers
```

### 8.7 Interview “say this” (60s)

> City-cell marketplace: bind quote with surge; create trip idempotently with payment hold; match via geo index and exclusive CAS offers; stream locations separately for tracking; settle on complete; scale by adding cells and sharding geo—not one global matcher.

### 8.8 Reliability tests

1. Dual accept → one driver.  
2. Payment timeout → no match.  
3. Driver cancel → re-dispatch.  
4. Replay confirm → one trip.  
5. City dispatch down → quotes fail closed.  

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Quote p99 | < 500ms |
| Match p50 dense | < 15s |
| Double assign | 0 |
| Track age p95 | < 10s |
| Duplicate capture | 0 |

### 8.10 Surge computation sketch

```text
for cell in city:
  demand = ride_requests_last_5m
  supply = on_duty_idle + arriving
  ratio = demand / max(supply, eps)
  m = clamp(f(ratio), 1, m_max)
  smooth(m_prev, m)
```

### 8.11 Fare components

```text
fare = base + time * rate + distance * rate + booking_fee
       + surge_extra + tolls + wait_fees - promos
```

### 8.12 Related systems map

```text
Pricing → Trip SM → Payments
             ↓
          Dispatch ← Geo ← Locations
             ↓
          Track / Notify / Safety / Ratings
```

### 8.13 Brownout order

```text
1. Reduce map polish / non-critical pushes
2. Pause promo codes adding demand
3. Broaden matching radius earlier
4. Stop new requests if matching broken
```

### 8.14 Regulatory notes (interview awareness)

- Local licenses, airport permits, data residency  
- Receipt requirements  
- Don’t claim one legal model worldwide  

### 8.15 vs Delivery / Eats

| | Rides | Eats/Delivery |
|-|-------|---------------|
| Parties | Rider-driver | User-courier-merchant |
| Inventory | Seats/time | Food prep + courier |
| Proof | Less PIN | Often PIN/photo |

### 8.16 Extra traps

| Trap | Pushback |
|------|----------|
| Haversine forever | ETA wrong |
| Store PAN | PCI |
| Perfect world optimizer MVP | Time sink |
| Ignore idempotency | SEV money |

### 8.17 Driver app critical UX states

```text
Offline | Online Idle | Offer Incoming | En Route Pickup | Waiting
| En Route Dropoff | Completing | Problem
```

### 8.18 Timeline events (minimum)

```text
QUOTE, REQUEST, HOLD_OK, OFFER, MATCH, ARRIVE, START, COMPLETE,
FARE, CAPTURE, CANCEL, REDISPATCH, SAFETY_SHARE
```

### 8.19 Unit check

```text
500K loc/s × 150 B = 75 MB/s → ~6.5 TB/day raw without TTL—must downsample
```

---

---

## Part II — LLD / Object Model

### 9.1 Domain entities

| Entity | Responsibility |
|--------|----------------|
| `Trip` | Lifecycle state, rider, driver, quote binding, assign_epoch |
| `Quote` | Frozen price inputs + surge + expiry |
| `Offer` | Time-bounded driver proposal with CAS accept |
| `DriverSession` | On-duty, location ref, product capabilities |
| `PaymentIntent` | Hold/capture/void with idempotency |
| `TripTimeline` | Append-only domain events (outbox) |
| `DispatchCell` | Scoped matcher operating on geo supply |
| `SurgeZone` | Cell demand/supply metrics → multiplier |

### 9.2 Class diagram (core)

```text
TripService --> TripRepository
            --> PaymentService
            --> DispatchClient
            --> TripTimelineOutbox

DispatchService --> GeoSupplyIndex
                  --> OfferRepository
                  --> ScoringStrategy
                  --> RealtimeNotifyClient

PricingService --> SurgeEngine
                 --> QuoteRepository
                 --> RoutingEtaClient

PaymentService --> PSPAdapter
                 --> IdempotencyStore
```

### 9.3 Trip state machine (explicit)

```text
enum TripState {
  QUOTED, REQUESTED, MATCHING, MATCHED,
  DRIVER_ARRIVING, ARRIVED, IN_TRIP,
  COMPLETED, PAID, CANCELLED
}

class Trip {
  transition(to: TripState, actor, reason): Result
  // illegal transitions throw; persisted with version CAS
}
```

### 9.4 Confirm trip sequence (objects)

```text
ConfirmTripCommand(rider_id, quote_id, idempotency_key)
  TripService:
    quote = QuoteRepo.get(quote_id) // must be valid, unexpired
    if idempotent hit: return existing trip
    payment = PaymentService.authorizeHold(quote, idempotency_key)
    trip = Trip.create(quote, rider_id)
    trip.transition(REQUESTED)
    DispatchClient.startMatching(trip.id)
    return trip
```

### 9.5 Accept offer (CAS)

```text
AcceptOfferCommand(driver_id, offer_id):
  tx:
    offer = OfferRepo.lock(offer_id)
    trip = TripRepo.lock(offer.trip_id)
    assert trip.state == MATCHING
    assert offer.notExpired()
    assert driver eligible + online
    trip.driver_id = driver_id
    trip.transition(MATCHED)
    trip.assign_epoch += 1
    OfferRepo.revokeOthers(trip.id, except=offer_id)
    Outbox.publish(TripMatched)
```

### 9.6 Payment idempotency

```text
interface PaymentService {
  Result authorizeHold(Quote q, IdempotencyKey k);
  Result capture(TripId t, Money finalFare, IdempotencyKey k);
  Result voidOrAdjust(TripId t, Policy p, IdempotencyKey k);
}
// PSP calls wrapped; store (k -> payment_op_id) forever
```

### 9.7 Dispatch scoring strategy

```text
interface CandidateScorer {
  double score(Driver d, Trip t, Eta eta);
}
class WeightedScorer implements CandidateScorer { ... }
// Extensibility: plug AirportQueueScorer, FairnessBooster without Trip changes
```

### 9.8 Location decoupling

```text
// Trip row stores driver_id only — NOT lat/lng
LocationIngest --> GeoSupplyIndex.update(driver_id, pos)
TrackingService.subscribe(trip_id) --> stream filtered by trip participants
```

### 9.9 Testing matrix

| Scenario | Expected |
|----------|----------|
| Double confirm | One trip |
| Two accepts | One MATCHED |
| Accept expired offer | Fail |
| Complete without IN_TRIP | Illegal transition |
| Capture retry | One charge |

### 9.10 Interview LLD closer

> Trip is the aggregate root with a strict state machine; dispatch and payments are separate services with idempotent commands; location never bloats the trip row—this keeps the “design Uber” answer object-oriented without a god class.

---

*End of ride-sharing marketplace system design.*
