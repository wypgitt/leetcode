# System Design: Robo-Taxi Marketplace

> **Focus areas:** Riders · Autonomous fleet · Matching · Dispatch · Dynamic pricing · Safety · Geo indexing · ETA  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct trip lifecycle under geo churn, split QPS (location vs match vs trip), explicit safety/deal-breakers, no “global lock all cars” fantasies

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

Goal: **bound a robo-taxi marketplace**—riders request trips, an autonomous fleet is matched and dispatched, pricing and ETAs are quoted, safety/compliance gates hold—without designing full AV stack perception/planning silicon.

### 1.0 What this is / is not

| Dimension | **Robo-taxi marketplace (this doc)** | Not this |
|-----------|--------------------------------------|----------|
| Primary job | Match riders ↔ AV fleet; run trip lifecycle | On-vehicle autonomy stack (LiDAR/ML) |
| Success | Low pickup ETA; safe completes; correct fare | Perfect city-scale traffic simulation |
| Supply | Company-owned / partner AV fleets | Classic human driver marketplace only |
| Money | Fare quote, auth, capture, tips, refunds | Full bank ledger product |
| Geo | Indexing, geofences, routing providers | Build Google Maps from scratch |

**Scope statement:** Design a robo-taxi marketplace covering rider requests, fleet state, matching, dispatch, pricing, safety gates, and geo—at progressive 10×/100×/1,000× city scale with Amazon-style operational ownership.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who supplies cars? | **Platform-operated AV fleet** (+ partner fleets Phase 1.5) | Fleet manager owns vehicle state |
| F2 | Rider apps? | Request ride, track, pay, rate, SOS | Trip API + realtime tracking |
| F3 | Vehicle modes? | Idle, en-route pickup, on-trip, charging, maintenance, OOO | Explicit vehicle state machine |
| F4 | Matching? | Nearest feasible AV by ETA, battery, geofence, vehicle class | Match service + geo index |
| F5 | Dispatch? | Commands to vehicle agent; acknowledgements | Durable command + ack protocol |
| F6 | Pricing? | Base + distance/time + surge + tolls + parking wait | Quote snapshot at accept |
| F7 | Safety? | SOS, remote assist, geofence compliance, incident workflow | Safety service overrides match |
| F8 | Autonomy ops? | Remote specialists for stuck vehicles | Human-in-loop queue |
| F9 | Charging? | Battery SoC constraints; depot charging | Energy-aware matching |
| F10 | Multi-city? | Launch city cells; expand | City/region partition |
| F11 | Shared rides? | Phase 1.5 pooling | Match scoring hooks |
| F12 | Payments? | PSP auth on match/start; capture on complete | Idempotent trip fares |

**MVP functional scope (lock with interviewer):**

1. Rider: quote → request → matched → wait → board → trip → pay → receipt.  
2. Fleet: ingest vehicle telemetry (location, SoC, status) at high frequency.  
3. Match: select best available AV under constraints; exclusive assignment.  
4. Dispatch: send pickup/dropoff missions; handle ack/nack/timeouts.  
5. Pricing: upfront quote with surge; finalize with adjustments (tolls).  
6. Safety: SOS, trip share, geofence deny, remote assist escalate.  
7. Ops: vehicle OOO, charging schedule thin, incident tickets.  
8. City-scale peak (rain/airport rush) with graceful degrade.

**Out of MVP (explicitly defer):**

- Full AV perception/planning stack  
- City-wide traffic light control  
- Human driver hybrid deep marketplace incentives  
- Cross-city long-haul autonomous trucking  
- Perfect multi-region active-active trip writes  
- Cryptocurrency fares

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Match latency | Interactive request | p50 < 1s, p99 < 3s |
| N2 | Location freshness | Accurate ETAs | Vehicle loc p95 age < 3–5s |
| N3 | Assignment exclusivity | No double-book vehicle | Strong lease/lock on vehicle |
| N4 | Trip durability | Never lose active trip | Quorum before rider “matched” |
| N5 | Availability | City rides critical | 99.9% request path; degrade surge UI first |
| N6 | Safety override | Hard stop beats marketplace | Safety plane can cancel missions |
| N7 | Auditability | Incidents explainable | Immutable trip + command log |
| N8 | Geo scale | Millions of loc updates/s at 1000× | Sharded geo + downsample |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Rider quotes A→B → sees ETA/price → requests → match AV → dispatch pickup → vehicle arrives → PIN/BLE unlock → trip → dropoff → fare capture.  
2. Vehicle low battery mid-idle → excluded from match → routes to charger.  
3. Surge at airport → higher quote → more pull from nearby idle / reposition.  
4. Rider cancels before pickup → cancellation fee policy; vehicle released.  
5. Remote assist unsticks vehicle at driveway → trip resumes.  
6. Geofence: no service zone → quote fails closed.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two riders match same car | Vehicle lease fencing; one wins |
| Dispatch ack timeout | Retry/reassign; rider updated |
| Vehicle goes OOO mid-approach | Rematch; apology + fare protect |
| Telemetry stale | Mark uncertain; don’t match stale supply |
| Rider no-show | Wait timer; cancel; fee |
| SOS pressed | Halt mission policy; notify safety; optional 911 partner |
| Pricing quote expires | Requote; don’t silently raise after accept without consent |
| Toll unknown at quote | Estimate + finalize true-up with cap/policy |
| Multi-stop | Waypoints in mission; pricing additive |
| Cell handover (city border) | Trip stays on home city cell until complete |
| Payment auth fails | No match dispatch / cancel assignment |
| Storm surge + demand spike | Cap wait; suggest later; prioritize safety over GMV |
| Remote assist queue overload | Prioritize in-trip hazards over idle stuck |
| Map provider outage | Cached tiles + degraded routing; widen ETA |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 city) | 10× | 100× | 1,000× |
|--------|-------------------|-----|------|--------|
| Cities | 1 | 5 | 30 | 200+ |
| Vehicles | 1K | 10K | 100K | 1M |
| Peak trip requests/s | 50 | 500 | 5K | 50K |
| Peak matches/s | 40 | 400 | 4K | 40K |
| Loc updates/s | 5K | 50K | 500K | 5M |
| Active trips | 2K | 20K | 200K | 2M |
| Remote assist seats | 20 | 100 | 1K | 5K+ |
| Geofence polygons | 100 | 1K | 10K | 100K |
| Pricing quote QPS | 200 | 2K | 20K | 200K |

**Split planes:** telemetry ingest ≠ matching ≠ trip state ≠ payments ≠ assist chat/video.

**What each jump forces:**

- **10×:** Geo shards (H3/S2); Kafka telemetry; match workers per city; Redis vehicle leases.  
- **100×:** City cells; hierarchical geo; surge controller; assist workforce routing.  
- **1,000×:** Multi-continent cells; edge loc gateways; predictive repositioning; safety regional SOC.

### 1.5 Etc. (Constraints & Assumptions)

- Vehicle **onboard computer** executes missions; cloud is marketplace + ops.  
- Routing/ETA via **map provider** (or internal) behind interface.  
- PIN/QR/BLE unlock for boarding—identity bound to trip.  
- Money: integer cents; quote_id immutable snapshot.  
- Single-writer **trip home** in city cell.  
- Regulatory: logs retention; geofence compliance mandatory.

**Scope statement:**

> Design a robo-taxi marketplace: rider trip lifecycle, fleet telemetry, geo-aware matching, durable dispatch, dynamic pricing, and safety overrides—from one-city ~1K vehicles through 10× / 100× / 1,000× with sharded geo, exclusive vehicle leases, and split realtime planes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Telemetry** | loc/SoC/status | 5K/s | 5M/s | Ingest + geo |
| **Quotes** | price/ETA reads | 200/s | 200K/s | Pricing + routing cache |
| **Requests/matches** | strong assign | 50/s | 50K/s | Match + lease |
| **Trip updates** | state transitions | 100/s | 100K/s | Trip service |
| **Rider track** | push/poll | 2K/s | 2M/s | CQRS realtime |
| **Assist** | human sessions | 5/s | 500/s | Safety ops |

### 2.2 Telemetry math

```text
1K vehicles × update every 2s ⇒ 500 updates/s average
Design peak 5K/s with bursts (reconnect storms)

Payload ~100–200 bytes ⇒ baseline ~1 MB/s
1000× ⇒ multi-GB/s → edge aggregation + downsample idle cars
```

### 2.3 Matching cost

```text
Naive: scan all idle vehicles O(V) — dies fast
Geo: query k rings of H3 cells → candidates 10–50
Score: ETA + SoC + class + reposition cost
Lock winner with lease TTL; confirm dispatch ack
```

### 2.4 Storage

| Data | Volume sketch | Retention |
|------|---------------|-----------|
| Trip records | ~5–20 KB | Years (compliance) |
| Telemetry raw | huge | Hot minutes; downsample |
| Commands/acks | small | 90d+ |
| Incidents | medium | Long legal hold |
| Fare ledger lines | small | Accounting retention |

### 2.5 Surge economics

```text
utilization = active_trips / deployable_vehicles
if ETA_p50 > target or utilization > u*: multiply fare
Cap surge; communicate clearly; never bait-and-switch after accept
```

### 2.6 Bandwidth / maps

Routing calls dominate quote cost—cache OD pairs short TTL; batch.  
Rider map: vehicle loc throttled (1–2s); don’t stream 10Hz to phones.

---

## 3. High-Level Design

### 3.1 UX / actor surfaces

| Surface | Actor | Needs |
|---------|-------|-------|
| Rider app | Rider | Quote, request, track, pay, SOS |
| Vehicle agent | AV | Telemetry up; missions down |
| Ops console | Fleet ops | OOO, depots, health |
| Remote assist | Safety specialist | Cameras/teleop stub, resolve |
| City admin | Launch team | Geofences, hours, caps |

### 3.2 Domain model

```text
City(city_id, cell, timezone, geofence_service_area)
Vehicle(vehicle_id, city_id, class, status, soc, pose, version)
Rider(rider_id, payment_methods, trust_score_thin)
Trip(trip_id, rider_id, vehicle_id?, state, quote_snapshot, waypoints[])
Quote(quote_id, origin, dest, price_cents, eta_s, expires_at, surge_m)
Assignment(trip_id, vehicle_id, lease_until, state)
Mission(command_id, vehicle_id, type, payload, ack_state)
Incident(trip_id?, vehicle_id, severity, workflow)
```

**Trip state machine:**

```text
REQUESTED → MATCHING → MATCHED → EN_ROUTE_PICKUP → ARRIVED
  → IN_TRIP → COMPLETING → COMPLETED
  * → CANCELLED / FAILED / SAFETY_HOLD
```

**Vehicle state machine:**

```text
OFFLINE → IDLE → ASSIGNED → EN_ROUTE_PICKUP → ON_TRIP
IDLE → CHARGING | MAINTENANCE | OOO
ON_TRIP → IDLE | CHARGING
SAFETY_HOLD can interrupt most states
```

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| Gateway / API | Auth, rate limits |
| Quote | ETA + price snapshot |
| Trip | Lifecycle, idempotency |
| Match | Candidate search + score + lease |
| Fleet / Telemetry | Ingest, vehicle SoT projection |
| Geo Index | H3/S2 presence |
| Dispatch | Mission commands + ack/retry |
| Pricing / Surge | Multipliers, caps |
| Safety | SOS, geofence, assist |
| Payments | PSP |
| Tracking RM | Rider-facing positions |
| Repositioner | Idle balancing (thin) |

### 3.4 Geo indexing

- Partition by **city_id** first (hard boundary).  
- Inside city: **H3** (or S2) cells at res chosen for ~100–500m.  
- Vehicle presence: update cell membership on move; idle indexed; on-trip optional.  
- Match query: origin cell + k-ring; expand if insufficient supply.  
- Geofences: service area, no-go, airport queues, school zones—evaluate on quote & dispatch.

### 3.5 Matching & exclusive assignment

```text
1. Validate quote unexpired + payment preauth OK
2. Create trip REQUESTED
3. Query geo candidates (filters: status=IDLE, soc>=min, class, geofence)
4. Rank by pickup ETA, soc surplus, fairness/reposition
5. Try lease vehicle (CAS status IDLE→ASSIGNED, lease_id=trip_id)
6. On success: MATCHED; dispatch pickup mission
7. On fail: next candidate; else widen search / FAIL_NO_SUPPLY
```

**Lease TTL:** if dispatch never acks, expire lease → rematch.

### 3.6 Dispatch protocol

```text
Cloud → Vehicle: Mission{command_id, trip_id, pickup, dropoff, constraints}
Vehicle → Cloud: ACK | NACK(reason) | PROGRESS | COMPLETE
Uncertainty: timeout → inquire vehicle; if unreachable SAFETY/OOO playbook
Idempotent command_id; vehicle ignores duplicates
```

### 3.7 Pricing

- Components: base, per-min, per-km, booking fee, surge, tolls estimate, wait time.  
- **Upfront pricing:** bind `quote_id` into trip; finalize within policy bands.  
- Surge: computed from demand/supply tiles; smooth to avoid flicker.  
- Promo codes: thin adjustment post-quote.

### 3.8 Safety plane

- **Hard geofence deny** before match.  
- SOS: trip → `SAFETY_HOLD`; notify specialists; optional mission pause.  
- Remote assist: prioritized queue; audit every command.  
- Safety can **preempt** marketplace optimization—say this aloud.  
- Rider verification: OTP/PIN at door.

### 3.9 Payments

- Auth hold on request/match; capture on complete; void/cancel fees.  
- Idempotency on trip fare finalization.  
- Refunds for AV failure (vehicle OOO)—policy engine.

### 3.10 API sketch

```text
POST /v1/quotes
POST /v1/trips                     Idempotency-Key
POST /v1/trips/{id}/cancel
GET  /v1/trips/{id}
POST /v1/trips/{id}/sos
POST /v1/vehicles/telemetry        (mTLS vehicle identity)
POST /v1/vehicles/{id}/missions/{cmd}/ack
WS   /v1/trips/{id}/track
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
 Rider App          Vehicle Agents           Ops / Assist
     │                    │                       │
     ▼                    ▼                       ▼
 ┌──────────┐      ┌─────────────┐         ┌────────────┐
 │ API GW   │      │ Telemetry GW│         │ Safety GW  │
 └────┬─────┘      └──────┬──────┘         └─────┬──────┘
      │                   │                      │
      ▼                   ▼                      ▼
  Quote/Trip         Fleet Projector        Safety Svc
      │                   │                      │
      └────────► Match ◄──┘                      │
                 │                               │
                 ▼                               │
              Dispatch ──────────────────────────┘ (preempt)
                 │
                 ▼
         City Event Bus (Kafka)
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
   Tracking   Pricing   Analytics
   ReadModel  /Surge    /Incidents
```

### 4.2 Match + dispatch sequence

```text
Rider     Trip      Match     Geo      Fleet     Dispatch   Vehicle
  |--req--▶|--create▶|         |        |          |          |
  |        |         |--cand--▶|        |          |          |
  |        |         |--lease----------▶|          |          |
  |        |◀-MATCHED|         |        |          |          |
  |        |--------------------------------------▶|--mission▶|
  |        |          |        |        |          |◀--ACK----|
  |◀-push--|          |        |        |          |          |
```

### 4.3 Telemetry path

```text
Vehicle → edge ingest → validate cert → topic telemetry.raw
       → fleet projector (latest pose/soc/status)
       → geo index updater (cell membership)
       → downsample → cold storage
Rider track reads projector/CQRS, not raw topic
```

### 4.4 Safety preempt

```text
SOS → Safety locks trip + vehicle
   → Dispatch cancel/pause mission
   → Assist session opens
   → Resolution: resume | rematch | end trip + refund policy
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **At most one active assignment per vehicle.**  
2. **At most one active vehicle per trip** (until rematch formalized).  
3. **Matched ⇒ durable trip + lease** before rider notified.  
4. **Commands idempotent** by `command_id`.  
5. **Stale telemetry ⇒ not matchable.**  
6. **Quote binding** prevents silent price bait-and-switch.  
7. **Safety HOLD overrides** match/dispatch optimizers.  
8. **Payment auth before costly dispatch** (or immediate cancel if fail).  
9. **City cell single-writer** for trip.  
10. **Integer money**; deterministic fare finalize function.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | One city; Redis geo; PG trips; modular match |
| 10× | H3 shards; Kafka; match workers; lease in Redis+DB |
| 100× | Multi-city cells; surge tiles; assist routing; edge ingest |
| 1000× | Continental cells; hierarchical geo; predictive reposition; SOC |

**Hot cells (airports):** dedicated matchers, queue lots, walking ETAs, special geofences.

### 5.3 Maintainability

- Vehicle agent contract tests (simulators)  
- Deterministic match golden files  
- Trip timeline for support/regulators  
- Feature flags: pause city, cap fleet, disable pooling  
- Map provider adapter isolation  

### 5.4 Progressive scale (1× → 1000×)

**1× — one city, 1K vehicles**

- Redis `GEOSEARCH` or H3 sets; Postgres trips.  
- Match in app servers with vehicle row locks.  
- Third-party routing.  
- Manual ops for charging.

**10×**

- Telemetry pipeline; projector; geo service.  
- Async match workers; lease TTLs.  
- Surge service; airport geofences.  
- Remote assist staffing model.

**100×**

- City cells independent blast radius.  
- Tile-based surge + reposition jobs.  
- Partner fleet adapter (same mission protocol).  
- Automated incident classification thin.

**1000×**

- Global rider identity; local trip homes.  
- Edge telemetry aggregation (idle at 10–30s).  
- Predictive demand (events/weather).  
- Multi-region safety operations centers.

### 5.5 Matching deep dive

**Scoring sketch:**

```text
score = w1*pickup_eta + w2*dropoff_eta_penalty + w3*(soc_min - soc)
      + w4*reposition_debt_credit + w5*vehicle_class_mismatch
lower is better; reject if pickup_eta > max or soc < trip_energy*margin
```

**Fairness:** avoid starving distant idle cars forever—occasional reposition missions.

**Pooling (Phase 1.5):** detour constraints; shared fare split rules—don’t invent mid-interview unless asked.

### 5.6 Dispatch uncertainty

```text
send_mission(cmd):
  persist PENDING
  send to vehicle
  on ACK: IN_PROGRESS
  on timeout: inquire; if offline → break lease → rematch
Never send conflicting missions without cancel fence
```

### 5.7 Pricing & surge

- Compute supply/demand per H3 tile.  
- Surge multiplier smoothed (EMA).  
- Hard caps + regulation hooks.  
- Quote TTL 30–120s.  
- Finalize: `min(max(actual, quote*(1-ε)), quote*(1+δ)+tolls)`—policy explicit.

### 5.8 Safety & compliance

| Control | Mechanism |
|---------|-----------|
| Service boundary | Polygon contains origin/dest |
| No-go | Reject routes intersecting |
| SOS | Priority workflow + mission policy |
| Audit | Append-only command & state log |
| Privacy | Loc retention limits; rider anonymization in analytics |
| Remote commands | mTLS + dual control for dangerous acts |

### 5.9 Observability (ops bar)

| SLO | Signal |
|-----|--------|
| Match success rate | exclude user cancels |
| Pickup ETA error | predicted vs actual |
| Telemetry freshness | p95 age |
| Dispatch ack latency | vehicle connectivity |
| Safety MTTA | assist answer time |
| Cancellation after match | vehicle/ops fault rate |

**Kill switches:** pause matching citywide; freeze surge; force charging; disable new requests.

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Match without vehicle lease | Double booking |
| Use stale GPS | Ghost cars |
| Optimize GMV over SOS | Safety incident |
| Global lock all vehicles | Latency death |
| Reprice after accept silently | Trust/legal |
| Active-active trip writes | Split brain missions |
| Stream raw 10Hz to all riders | App/battery meltdown |

---

## 6. Wrap-Up

### 6.1 What we designed

A city-cell robo-taxi marketplace: quotes, exclusive geo matching, durable dispatch with acks, surge pricing, telemetry-projected fleet state, and a safety plane that preempts optimization—scaled via H3 sharding and progressive cells.

### 6.2 Key decisions worth defending

| Topic | Decision |
|-------|----------|
| Partition | City cell + H3 geo |
| Exclusivity | Vehicle lease + CAS |
| Telemetry | Projector; don’t match raw stream |
| Price | Upfront quote snapshot |
| Safety | Separate preempt plane |
| Maps | Provider interface + cache |

### 6.3 Risks

1. Connectivity black holes → mass rematch  
2. Map outage → ETA collapse  
3. Airport geofence complexity  
4. Assist staffing under multi-incident  
5. Surge PR/regulatory blowback  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: marketplace not AV stack |
| 5–15 | Trip + vehicle state machines |
| 15–25 | Geo match + leases |
| 25–35 | Dispatch uncertainty + pricing |
| 35–45 | Safety, scale, telemetry planes |

---

## 7. Deeper / Related Interview Questions

### 7.1 Matching

**Q: Nearest car by Haversine enough?**  
A: No—use routable ETA; rivers/one-ways matter.

**Q: How to avoid double assign?**  
A: Atomic lease (`IDLE→ASSIGNED` with trip id); competing matchers retry.

**Q: Should we match before payment auth?**  
A: Prefer auth/hold first or speculative hold with tight timeout.

### 7.2 Geo & telemetry

**Q: Redis GEO vs H3?**  
A: Both OK; H3 nicer for surge tiles & rings; defend ops.

**Q: Update frequency?**  
A: Dynamic: idle 5–10s; en-route 1–2s; edge aggregate at scale.

**Q: Clock skew on vehicles?**  
A: Server receive time + vehicle monotonic; reject ancient samples.

### 7.3 Dispatch

**Q: Vehicle NACKs pickup?**  
A: Release lease; rematch; log fault code.

**Q: Can cloud teleoperate?**  
A: Assist plane; not normal match path; heavy auth.

### 7.4 Pricing

**Q: Upfront vs post-trip?**  
A: Upfront for trust; true-up tolls/wait within policy.

**Q: Surge fairness?**  
A: Caps, communication, no mid-trip surprise multiplier.

### 7.5 Safety

**Q: Marketplace vs safety conflict?**  
A: Safety wins; kill match; compensate rider.

**Q: False SOS?**  
A: Still treat seriously; abuse scoring thin after.

### 7.6 Charging & energy

**Q: Match low SoC car to long trip?**  
A: Energy model rejects; send to charger instead.

**Q: Who decides charging?**  
A: Policy engine: SoC, demand forecast, depot capacity.

### 7.7 Scale & cells

**Q: Cross-city trip?**  
A: Rare MVP; if allowed, home cell owns until handoff protocol—defer.

**Q: 5M loc/s?**  
A: Edge gateways, idle downsample, partitioned projectors.

### 7.8 Failure injection

| Inject | Expect |
|--------|--------|
| Lose 20% vehicles connectivity | Rematch in-flight pickups; widen ETA |
| Pricing service down | Last-good surge caps; or pause quotes |
| Match stampede | Per-city queues; jitter |
| Map ETA timeouts | Fallback heuristic; flag degraded |

### 7.9 Amazon-flavored probes

**Q: Customer obsession when AV fails?**  
A: Fast rematch, fare waive, clear status, incident learning.

**Q: Ownership of safety SLO?**  
A: Safety service pages; marketplace cannot override.

**Q: Frugality on maps?**  
A: Cache OD; don’t route-spam every telemetry tick.

### 7.10 Comparison traps

| Trap | Better |
|------|--------|
| “Just Uber” | Fleet ownership + mission ack + energy + remote assist |
| “Kafka is SoT for vehicles” | Projector with versioned state |
| “Global optimizer each second” | Local match + periodic reposition |
| “Blockchain dispatch” | No |

### 7.11 Extra traps

**Q: Rider moves pickup pin after match?**  
A: Allowed within radius with vehicle replan; else cancel/recreate.

**Q: Two apps one account double request?**  
A: Idempotency + single active trip constraint.

**Q: How is PIN safe?**  
A: Short-lived; bound to trip; rate-limited; rotate on rematch.

### 7.12 Progressive scale Q&A

**Q: First bottleneck?**  
A: Telemetry + naive geo scans.  
**Q: 100×?**  
A: City cell isolation and airport hotspots.  
**Q: 1000×?**  
A: Edge ingest + predictive supply; compliance sprawl.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
trips(
  trip_id PK,
  city_id,
  rider_id,
  vehicle_id NULL,
  state,
  quote_id,
  origin_geo,
  dest_geo,
  price_cents_quote,
  price_cents_final NULL,
  version,
  idempotency_key UNIQUE,
  created_at
);

vehicles(
  vehicle_id PK,
  city_id,
  status,
  soc,
  lat, lng,
  h3_cell,
  lease_trip_id NULL,
  lease_until NULL,
  pose_version,
  last_telemetry_at
);

missions(
  command_id PK,
  vehicle_id,
  trip_id,
  type,
  payload_json,
  ack_state,
  created_at
);

quotes(
  quote_id PK,
  rider_id,
  price_cents,
  eta_s,
  surge_m,
  expires_at,
  route_fingerprint
);

incidents(
  incident_id PK,
  trip_id NULL,
  vehicle_id,
  severity,
  state,
  created_at
);
```

### 8.2 API checklist

| API | Idempotent | Notes |
|-----|------------|-------|
| Create quote | Yes (optional key) | TTL’d |
| Create trip | Yes | Binds quote |
| Cancel trip | Yes | Fee policy |
| Telemetry | At-least-once | Version/pose |
| Mission ack | Yes | command_id |
| SOS | Yes | Opens incident |

### 8.3 State transition checklist

```text
Trip: REQUESTED→MATCHING→MATCHED→EN_ROUTE_PICKUP→ARRIVED→IN_TRIP→COMPLETED
Cancel gates: before IN_TRIP (fees vary); SAFETY_HOLD special
Vehicle: IDLE↔ASSIGNED; ASSIGNED→IDLE on cancel/fail; SAFETY_HOLD anytime
```

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Lease | Exclusive short lock of vehicle to trip |
| Projector | Latest vehicle state from telemetry stream |
| H3/S2 | Hierarchical geo indexing |
| Surge | Demand/supply price multiplier |
| Remote assist | Human helps stuck AV |
| Mission | Dispatch command to vehicle |
| SoC | Battery state of charge |
| Cell | City deployment/failure domain |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Lease matching, trip SM, basic geo |
| 10× | Telemetry pipeline, surge, dispatch ack | 
| 100× | City cells, airport logic, assist scale |
| 1000× | Edge downsample, predict reposition, global ops |

### 8.6 Match pseudocode

```text
function match(trip, quote):
  for radius in [1,2,3,5]:
    cands = geo.idle(trip.origin, radius).filter(constraints)
    for v in rank(cands):
      if fleet.try_lease(v, trip.id, ttl):
         dispatch.pickup(v, trip)
         return MATCHED
  return NO_SUPPLY
```

### 8.7 Fare finalize sketch

```text
final = quote.price
final += tolls_actual - tolls_est
final += wait_fee(policy)
final = clamp(final, quote.price * (1-eps), quote.price * (1+delta) + tolls_actual)
```

### 8.8 Telemetry validation

```text
accept if:
  cert vehicle_id matches
  pose_version > last OR (version==last and richer)
  timestamp within skew window
  jump distance physically plausible
else quarantine + metrics
```

### 8.9 Airport hotspot pattern

- Dedicated pickup zones as graph nodes  
- Walker ETA from curb pin to zone  
- Queue vehicles in virtual lanes  
- Match to zone not raw GPS scramble  

### 8.10 Reliability / chaos drills

| Drill | Pass |
|-------|------|
| Kill match workers | Queue backlog; no double lease |
| Network partition 10% fleet | Rematch; rider messaging |
| Surge controller bug | Cap kill switch |
| SOS storm | Prioritization; marketplace pause optional |

### 8.11 Interview “say this” (60s)

> Robo-taxi marketplace in city cells. Telemetry projects fleet state into H3 geo. Matching exclusively leases idle vehicles by ETA/SoC, then durable dispatch with ack/timeout rematch. Upfront quotes with surge tiles. Safety SOS preempts missions. Split planes for loc vs match vs trips; progressive scale via shards and edge downsample—not a global optimizer.

### 8.12 Extra traps

- Storing every telemetry point forever at full rate  
- Letting rider clients pick `vehicle_id`  
- Surge without caps  
- Using eventually consistent inventory of cars for assignment  

### 8.13 Related systems map

| System | Overlap |
|--------|---------|
| Ride-sharing | Matching/pricing |
| Pizza delivery | Dispatch thin lessons |
| IoT fleet | Telemetry ingest |
| Payments | Auth/capture |
| Maps platforms | Routing/ETA |

### 8.14 Estimation cheat-sheet

```text
loc/s ≈ vehicles × (1/interval) × active_fraction_factor
match/s ≈ request/s × attempts
candidates ≈ vehicles_per_km2 × πr^2
```

### 8.15 Leadership mapping

| Principle | Move |
|-----------|------|
| Customer Obsession | Rematch + fare protect on AV fault |
| Ownership | Safety SLO distinct pager |
| Dive Deep | Trip/command audit timeline |
| Invent & Simplify | Lease+H3 before fancy global MIP |
| Are Right, A Lot | Measure ETA error; fix models |

### 8.16 Partner fleet adapter (Phase 1.5)

Same mission protocol; adapter translates; leases still platform-authoritative or dual-ack—call out complexity; prefer platform-operated MVP.

---

*End of robo-taxi marketplace system design — Amazon SDE III prep artifact.*
