# System Design: Scoped Delivery System

> **Focus areas:** Geospatial scoping · Courier dispatch · ETA · Idempotent assignment · Marketplace state machine · Real-time tracking · Capacity · Zone isolation  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — delivery within a **scoped** geography (city / region / geofence), not unbounded global logistics  
> **Quality bar:** Clear scope boundaries; dispatch ownership; no double-assign; progressive geo sharding

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

Goal: design a **scoped delivery** product—customers request pickup→dropoff within a bounded service area; couriers are matched, tracked, and paid; the system stays correct under retries and peak lunch/dinner.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Scope | City/region **service area** with geofences | Cross-continental freight / Amazon FC network |
| Actors | Customer, courier, optional merchant | Full Uber Eats restaurant OS (can touch) |
| Job | Create delivery → dispatch → track → complete | Pure chat or pure payments |
| Uber lens | Geo index, streaming locations, marketplace assignment | Academic TSP-only interview |

**“Scoped” means:** serviceability is constrained by **zones** (city cells). Orders outside scope are rejected early. Scaling = more zones + denser demand, not one global matcher.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | What is delivered? | Parcels / food / grocery—MVP: **point-to-point parcel** | Pickup & dropoff lat/lng + addresses |
| F2 | Who delivers? | Fleet of couriers (employee or gig) | Courier supply model + on-duty state |
| F3 | Scope? | Operate per **city/zone**; expand city-by-city | Zone as isolation cell |
| F4 | Request flow? | Quote → confirm → track → deliver → rate | Quote must be capacity-aware |
| F5 | Matching? | Auto-dispatch nearby available couriers | Geo index + offer/accept or auto-assign |
| F6 | Batching? | Optional multi-stop later | MVP single job per courier |
| F7 | Tracking? | Customer sees courier location + ETA | Streaming locations; map SDK |
| F8 | Payments? | Charge customer; pay courier | Idempotent payment intents |
| F9 | SLAs? | Pickup within X min; delivery window | SLA timers + breach handling |
| F10 | Cancellations? | Customer/courier/system cancel with policies | State machine + fees |
| F11 | Proof of delivery? | Photo / PIN / signature optional | Media + audit |
| F12 | Merchants? | Optional pickup at store | Merchant readiness hooks |

**MVP functional scope:**

1. Customer requests delivery with pickup/dropoff **inside a service zone**.  
2. System returns **quote** (price + ETA) if capacity allows.  
3. On confirm: create `Delivery` with idempotency key; authorize payment.  
4. **Dispatch** to eligible on-duty courier (offer or auto-assign—pick one).  
5. Courier navigates; app streams location; customer tracks.  
6. Complete with proof; capture payment; courier earnings event.  
7. Cancel/reassign paths; basic support tools.

**Out of MVP:** multi-hop relay, cross-zone handoff, full Amazon-style warehouses, drone delivery, perfect global optimization across all cities in one solver.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Quote latency | p99 < 300–500ms |
| N2 | Dispatch time to first offer | p50 < 5s, p99 < 30s (dense cities) |
| N3 | Location freshness | Courier location age p95 < 5–10s on map |
| N4 | Assignment correctness | **No double-assign** of same job |
| N5 | Payment | Idempotent; no silent double-charge |
| N6 | Availability | Zone can degrade; don’t take orders if dispatch broken |
| N7 | Scalability | Independent zone cells; lunch peak 5–10× |
| N8 | Audit | Full timeline for support/SEV |

### 1.3 Cases

**Happy:** Quote → confirm → assign → pickup → dropoff → paid → rated.  

**Edges:**

| Case | Behavior |
|------|----------|
| Pickup outside zone | Reject at quote |
| No couriers nearby | Quote unavailable / longer ETA / queue |
| Courier accepts then goes offline | Reaper + reassign |
| Double-tap confirm | Idempotency → one delivery |
| Payment auth fails | Don’t dispatch |
| Customer cancel after pickup | Policy fee; courier pay rules |
| Address ambiguous | Geocode confidence; confirm pin |
| GPS spoof / teleport | Sanity checks; fraud signals |
| Zone network partition | Fail closed on new confirms |
| Lunch rush | Surge pricing or ETA elongation |
| Proof upload fail | Retry; allow complete with note per policy |

### 1.4 Progressive scale

| Metric | Base (1 city) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Cities / zones | 1 | 10 | 100 | 1,000 |
| Deliveries / day | 50K | 500K | 5M | 50M |
| Peak creates / s | ~5 | ~50 | ~500 | ~5K |
| On-duty couriers | 2K | 20K | 200K | 2M |
| Location updates / s | ~2K | ~20K | ~200K | ~2M |
| Concurrent active jobs | 3K | 30K | 300K | 3M |
| Dispatch decisions / s | ~5 | ~50 | ~500 | ~5K |

**Jumps:** 10× = multi-city platform; 100× = zone cells + geo shards; 1,000× = hierarchical dispatch, stronger fraud, heterogeneous vehicle types.

### 1.5 Scope repeat-back

> Scoped (zone-bounded) courier delivery: quote → idempotent order → geo-aware dispatch without double-assign → realtime track → complete/pay—scaled by adding zone cells and sharding geo indexes, with payments and assignment as correctness-critical paths.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event classes

| Class | Base peak | 100× | Notes |
|-------|-----------|------|-------|
| Quote | 20/s | 2K/s | Read-heavy geo + pricing |
| Confirm / create | 5/s | 500/s | Durable + payment auth |
| Dispatch offers | 10/s | 1K/s | Bursty |
| Location updates | 2K/s | 200K/s | Dominates bandwidth |
| Track reads (WS/map) | 5K/s | 500K/s | Cache last location |
| Completes | 5/s | 500/s | Payment capture |

**Insight:** Location stream ≫ order creates. Separate **ingest plane** from **order OLTP**.

### 2.2 Geo math

```text
City ~500 km²; courier density 2K on-duty
Location every 4s → 2000/4 = 500 updates/s? Table says 2K—assume 1Hz for active / 0.25Hz idle mix
Active on job ~30% at 1 Hz + idle 70% at 0.2 Hz:
0.3*2000*1 + 0.7*2000*0.2 = 600 + 280 = 880/s → order-of 1K; peaks higher near downtown

Dispatch radius search r=3km:
Candidates often tens; rank top K=5–20 for offers
```

### 2.3 Storage

```text
Delivery row ~1–2 KB; 50K/day × 365 ≈ 18–36 GB/year/city metadata
Location ping ~100–200 B; retain raw 24–72h hot; downsample for history
2K couriers × 0.5 Hz × 150 B × 86400 ≈ 13 GB/day raw locations/city → TTL aggressively
```

### 2.4 Latency budget (quote)

```text
Geocode (cached) + zone check + ETA model + price + capacity signal
50 + 20 + 80 + 30 + 40 ≈ 220ms p50 target; p99 < 500ms with timeouts
```

### 2.5 Bottlenecks

1. Hot downtown geo tiles at lunch  
2. Location ingest + fan-out to tracking clients  
3. Dispatch thundering when courier supply low  
4. Payment provider latency  
5. Single global matcher (anti-pattern at 100×)

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Order / Delivery | Lifecycle state | Strong per `delivery_id` |
| Dispatch / Assignment | Offers & locks | Strong; fencing tokens |
| Location | Courier positions | Eventually; freshness SLO |
| Pricing / Quote | Quotes & surge | Soft-state; bind on confirm |
| Payments | Auth/capture | Idempotent ledger |
| Zone config | Geofences, hours | Config as data |

**Deal-breaker:** Using the location stream store as the system of record for assignment.

### 3.2 Delivery state machine

```text
QUOTED → CONFIRMED → DISPATCHING → ASSIGNED → AT_PICKUP → PICKED_UP
      → AT_DROPOFF → DELIVERED → SETTLED
Any non-terminal → CANCELLED (policy)
ASSIGNED → REASSIGNING on courier fail
```

### 3.3 Dispatch options

| Option | Pros | Cons | When |
|--------|------|------|------|
| A. Auto-assign nearest | Fast | Courier rejection / ignore | Dense employee fleets |
| B. Offer blast to K | Choice | Latency; pile-on | Gig couriers |
| C. Auction / score | Flexible | Complexity | 100×+ |

**MVP pick:** Offer to top-K scored couriers with **short TTL**; first accept wins via CAS; others get revoke.

**Invariant:** At most one `ASSIGNED` courier per delivery; accept uses compare-and-set + fencing.

### 3.4 Geospatial index

| Option | Pros | Cons |
|--------|------|------|
| Geohash + Redis | Fast radius | Rebalance; hot tiles |
| S2 / H3 cells | Uniform-ish | Learning curve |
| Quadtree service | Flexible | Ops |

**Chosen:** H3/S2 cell → courier sets in memory/Redis per **zone**; dispatch workers own zone shards.

### 3.5 Idempotency & payments

```text
Confirm: Idempotency-Key → create delivery_id once
Payment auth: key = delivery_id or client key
Capture on DELIVERED (or policy); refunds on cancel paths
```

### 3.6 Trade-offs

| Topic | Choice | Why | Deal-breaker |
|-------|--------|-----|--------------|
| Matcher scope | Per-zone | Isolation | One global lock/matcher |
| Location SoT | Ephemeral index + log | Hot path | Update delivery row every ping |
| Assignment | CAS + offer TTL | No double-assign | “Just notify both” |
| Quote binding | Snapshot on confirm | Price honesty | Reprice silently after confirm |
| Tracking fan-out | Pub/sub by delivery | Scale | Polling DB locations |
| ETA | Model + traffic signal | UX | Haversine-only in dense cities long-term |

### 3.7 Components

1. **Gateway / API**  
2. **Zone Service** — serviceability geofences  
3. **Quote / Pricing**  
4. **Delivery Service** — state machine  
5. **Dispatch Service** — geo candidates + offers  
6. **Courier Gateway** — offers, accept, job UI  
7. **Location Ingest** — streaming positions  
8. **Tracking / Fan-out** — customer realtime  
9. **Payments**  
10. **Notifications**  
11. **Support / Timeline**  
12. **Fraud / Trust**  

---

## 4. Architecture Diagram

```text
Customer App          Courier App
    |                     |
    v                     v
 API Gateway         Courier Gateway
    |                     |
    +-- Quote/Pricing     +-- Location Ingest ---> Geo Index (per zone)
    |                     |
    +-- Delivery Service <----+ Dispatch Service (zone shards)
    |         |               |
    |         +--- offers/assign CAS
    |         |
    +-- Payments
    |
    +-- Tracking Pub/Sub --> Customer map WS
    |
    +-- Timeline / Support events
```

### 4.1 Confirm + dispatch sequence

```text
Customer   DeliverySvc   Payments   Dispatch   GeoIndex   Courier
   |--confirm---------->|           |          |          |
   |                    |--auth---->|          |          |
   |                    |--DISPATCHING-------->|          |
   |                    |           |--query-->|          |
   |                    |           |<-cands---|          |
   |                    |           |--offer---------------------->|
   |                    |           |<--accept CAS-----------------|
   |                    |<-ASSIGNED-|          |          |
   |<-push assigned-----|           |          |          |
```

### 4.2 Location → track

```text
Courier --ping--> Ingest --> validate --> Geo Index update
                              \-> stream topic delivery_id --> Track WS --> Customer
```

### 4.3 Zone cell

```text
Each city/zone = dispatch + geo + on-duty pool isolation
Cross-zone: reject or explicit handoff product (out of MVP)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Confirm is idempotent; one `delivery_id` per key.  
2. Payment auth precedes dispatch (or reserved credit).  
3. Assignment CAS: only one winner; losers revoked.  
4. Courier lease/heartbeat on active job; expiry → reassign.  
5. Location spoof checks; impossible jumps flagged.  
6. State transitions via allowed edges only.  
7. Customer cancel and courier cancel have explicit money outcomes.  
8. Timeline events for every material transition (outbox).  
9. Zone closed → no new confirms.  
10. Tracking lag never corrupts assignment truth.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | One city; Redis geo; single dispatch service; PG deliveries |
| 10× | Multi-zone config; shared platform; per-zone queues |
| 100× | Zone cells; H3 shards; location stream bus; payment isolation |
| 1000× | Hierarchical dispatch; vehicle classes; ML ETA; fraud platform |

### 5.3 Maintainability

- Zone config as data (polygons, hours, fees).  
- Dispatch scorer plugins (distance, rating, continuity).  
- Simulation for lunch-peak.  
- Canary a zone before global matcher changes.  
- Contract tests for state machine.

### 5.4 Progressive scale

**1×:** Monolith OK; Redis `GEOSEARCH`; offer top-5; Stripe-like payments.  
**10×:** Zone router; standardized courier app protocol; shared location ingest.  
**100×:** Cells; stream processing for ETA; surge; dead-zone detection.  
**1000×:** Multi-modal (bike/car); batching; relay; country-level compliance packs.

### 5.5 Matching score (sketch)

```text
score = w1*eta_to_pickup + w2*acceptance_prob + w3*fairness + w4*rated
filter: on_duty, vehicle_ok, not_busy, within_radius, docs_ok
```

### 5.6 Reassign protocol

```text
on courier_heartbeat_miss OR cancel OR force_reassign:
  if state in {ASSIGNED..PICKED_UP} per policy:
    CAS clear assignment with reason
    increment reassign_count
    go DISPATCHING (or CANCEL if undeliverable)
    notify customer ETA change
```

### 5.7 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Global single dispatcher lock | Latency + outage blast radius |
| Assign without CAS | Double courier pickup |
| Update SQL row per GPS ping | OLTP melt |
| Quote without zone check | Unservable orders |
| Capture payment before deliver with no cancel story | Support hell |
| Ignore idempotency | Double charge / double job |

---

## 6. Wrap-Up

### 6.1 Designed

Zone-scoped delivery marketplace: serviceability → quote → idempotent confirm + pay auth → geo dispatch with exclusive assign → streaming track → complete/settle—with planes split and zone cells for scale.

### 6.2 Decisions to defend

1. Zone as isolation cell  
2. Planes: order / dispatch / location / payments  
3. Offer+CAS exclusive assignment  
4. Location ephemeral index + stream  
5. Idempotent confirm & payments  
6. Fail closed when dispatch unhealthy  
7. Timeline/outbox for support  

### 6.3 Risks

- Supply droughts  
- GPS noise / tunnels  
- Payment provider blips  
- Hot downtown tiles  
- Fraudulent couriers  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Define scoped zones + MVP parcel |
| 5–15 | State machine + idempotent confirm/pay |
| 15–28 | Geo index + dispatch CAS |
| 28–38 | Location streaming + tracking |
| 38–45 | Scale by cells; peaks; traps |

### 6.5 Closer

> **Scoped delivery:** zone-bounded serviceability, exclusive CAS dispatch, streaming locations off the OLTP path, idempotent money, progressive multi-city cells.

---

## 7. Deeper / Related Interview Questions

### 7.1 Geospatial

**Q: Geohash vs S2/H3?**  
A: All fine if you can radius query and rehash on move; H3 k-ring is interview-friendly.

**Q: Hot tile downtown?**  
A: Subdivide cells; shard couriers; rate-limit map updates; separate read replicas for track.

**Q: Pickup on zone boundary?**  
A: Explicit polygon rules; buffer; reject ambiguous.

### 7.2 Dispatch

**Q: First-accept vs auto-assign?**  
A: Trade courier UX vs speed; employee fleets lean auto; gig lean offers.

**Q: Prevent offer pile-on?**  
A: Small K; short TTL; revoke losers instantly; cooldown.

**Q: Fairness vs efficiency?**  
A: Add idle-time boost; avoid always favoring closest same courier.

### 7.3 Consistency

**Q: Two couriers accept same ms?**  
A: CAS on `delivery.assignee`; one wins; other gets `409` + revoke UI.

**Q: Exactly-once dispatch?**  
A: Exactly-once **assignment effect** via CAS; offers are at-least-once.

### 7.4 Tracking

**Q: How many map subscribers?**  
A: Pub/sub per `delivery_id`; don’t scan DB.

**Q: ETA jumps?**  
A: Smooth; hysteresis; traffic model; communicate delays.

### 7.5 Payments

**Q: When to capture?**  
A: Usually on DELIVERED; auth at confirm; cancel releases auth.

**Q: Partial refund after complaint?**  
A: Separate adjustment ledger; don’t rewrite capture blindly.

### 7.6 Peaks

**Q: Lunch 10×?**  
A: Elongate ETA; surge; prioritize pickups; pause non-critical features; scale dispatch workers per zone.

### 7.7 Fraud

**Q: Fake GPS complete?**  
A: Geofence checks at pickup/dropoff; PIN; photo; device signals; anomaly models.

### 7.8 Multi-city

**Q: Share couriers across cities?**  
A: Rare; usually zone-bound. If airport zones overlap, explicit multi-zone eligibility.

### 7.9 Interview traps

| Trap | Pushback |
|------|----------|
| Solve world TSP for MVP | Overkill |
| One Redis as money SoT | No |
| Put matcher in client | Cheatable |
| Store all pings forever hot | Cost bomb |
| “Kafka exactly-once assigns couriers” | Still need CAS |

### 7.10 Metrics

| Metric | Why |
|--------|-----|
| Time-to-assign | Liquidity |
| Pickup ETA error | Trust |
| Cancel rate post-assign | Health |
| Double-assign attempts (should be 0 wins) | Correctness |
| Location age p95 | Track UX |
| Quote→confirm conversion | Product |

### 7.11 Related Uber systems

Maps to **ride-sharing marketplace** and **delivery dispatch**, but scoped delivery emphasizes **zone serviceability + parcel proof** over seats/surge complexity—reuse location + dispatch patterns.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
deliveries(
  delivery_id UUID PK,
  idempotency_key TEXT UNIQUE,
  zone_id TEXT,
  state TEXT,
  customer_id UUID,
  courier_id UUID NULL,
  assign_epoch INT,
  pickup GEO, dropoff GEO,
  quote_snapshot JSONB,
  payment_intent_id TEXT,
  created_at, updated_at)

delivery_events(delivery_id, ts, type, actor, payload) -- timeline

courier_session(courier_id, zone_id, on_duty, vehicle, last_cell, last_latlng, updated_at)

offers(offer_id, delivery_id, courier_id, expires_at, state) -- UNIQUE active constraints via CAS
```

### 8.2 API checklist

- [ ] `POST /v1/quotes`  
- [ ] `POST /v1/deliveries` + Idempotency-Key  
- [ ] `POST /v1/deliveries/{id}/cancel`  
- [ ] Courier: `POST /offers/{id}/accept|reject`  
- [ ] `POST /v1/locations` (courier stream)  
- [ ] WS `/v1/track/{delivery_id}`  
- [ ] `POST /v1/deliveries/{id}/complete` + proof  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Zone / scope | Serviceable geofenced cell |
| Offer TTL | Time courier has to accept |
| Assign epoch | Fencing counter for reassigns |
| Geo index | Hot positions for candidates |
| Quote snapshot | Bound price/ETA at confirm |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Zone check, state machine, Redis geo, CAS assign, payments |
| 10× | Multi-zone platform, shared ingest |
| 100× | Zone cells, stream bus, surge/ETA ML |
| 1000× | Batching/multi-modal, fraud platform |

### 8.5 Dispatch CAS pseudocode

```text
accept(offer_id, courier_id):
  offer = get(offer_id)
  if offer.expired or offer.courier_id != courier_id: reject
  tx:
    d = get_delivery(offer.delivery_id)
    if d.state != DISPATCHING: reject
    d.state = ASSIGNED
    d.courier_id = courier_id
    d.assign_epoch += 1
    mark offer ACCEPTED; revoke siblings
  push revoke to losers
```

### 8.6 Location validation

```text
if distance(prev, new) / dt > vmax_vehicle: flag / clamp
if outside zone+buffer while on job: flag
downsample for non-active couriers
```

### 8.7 Interview “say this” (60s)

> Scoped by city zones: quote only if serviceable; confirm idempotently with payment auth; dispatch via geo index with exclusive CAS assignment; stream locations on a separate plane for tracking; scale by zone cells—not one global matcher.

### 8.8 Reliability tests

1. Dual accept → one assignee.  
2. Courier kill mid-job → reassign.  
3. Replay confirm → one delivery.  
4. Zone disable → quotes fail.  
5. Location flood → ingest holds; orders still correct.  

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Quote p99 | < 500ms |
| Assign p50 | < 5s (dense) |
| Track location age p95 | < 10s |
| Double-assign success | 0 |
| Payment duplicate charge | 0 |

### 8.10 State transition table (excerpt)

| From | To | Actor |
|------|----|-------|
| QUOTED | CONFIRMED | customer |
| CONFIRMED | DISPATCHING | system |
| DISPATCHING | ASSIGNED | courier accept / system |
| ASSIGNED | PICKED_UP | courier |
| PICKED_UP | DELIVERED | courier |
| * | CANCELLED | policy |

### 8.11 Related systems map

```text
Quote → Delivery SM → Payments
           ↓
        Dispatch ← Geo Index ← Location Ingest
           ↓
        Tracking Fan-out → Customer
```

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| Haversine ETA forever | Bad UX in traffic |
| Customer picks courier from full list | Privacy + gaming |
| Store payment PAN | PCI nightmare—tokenize |
| Cross-zone silent hop | Scope violation |

### 8.13 Lunch-peak playbook

```text
1. Detect zone utilization > threshold
2. Surge or ETA padding
3. Prioritize short hops
4. Pause promotions that add demand
5. Scale dispatch + ingest
6. Communicate delays in-app
```

### 8.14 Proof of delivery options

| Method | Pros | Cons |
|--------|------|------|
| PIN | Simple | Share risk |
| Photo | Evidence | Privacy |
| Signature | Formal | UX friction |
| Contactless note | COVID-era | Disputes |

---


### 8.15 Courier on-duty session lifecycle

```text
OFFLINE → ON_DUTY (choose zone) → IDLE → OFFERED → EN_ROUTE_PICKUP → AT_PICKUP
        → EN_ROUTE_DROPOFF → AT_DROPOFF → IDLE
Heartbeat every H seconds while ON_DUTY; miss → mark suspicious → eventually OFFLINE
Cannot hold >1 exclusive ASSIGNED job in MVP (batching later)
```

### 8.16 Pricing sketch

```text
price = base + distance_rate * km + time_rate * eta_min + surge_multiplier + tolls_est
quote_id binds inputs hash + expiry (e.g. 2–5 min)
confirm must present quote_id; server revalidates soft (tolerance) or rejects expired
```

### 8.17 Idempotency matrix

| API | Key | Replay result |
|-----|-----|---------------|
| Create delivery | Idempotency-Key | Same delivery_id |
| Accept offer | offer_id + courier_id | Same assign epoch |
| Complete | delivery_id + proof_hash | Same settled |
| Payment auth | payment_intent_id | Same intent |

### 8.18 Geo index operations

```text
on_ping(courier_id, lat, lng, ts):
  cell = h3(lat,lng, res)
  if cell != prev_cell: remove from prev; add to cell set
  store last_pos[courier_id] = {lat,lng,ts,cell}
  if active_delivery: publish to track topic

candidates(pickup, r):
  cells = k_ring(h3(pickup), k_for_radius(r))
  union couriers in cells; filter distance <= r and eligibility
  rank top K
```

### 8.19 Failure modes catalog

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Dispatch backlog | offer_queue_lag | Shed non-critical; elongate ETA |
| Payment timeout | client timeout | Confirm stays pending_payment; no dispatch |
| Ingest overload | drop idle pings first | Keep on-job pings |
| Hot cell | tile QPS | Split resolution; shard |
| Courier ghost accept | no movement | Soft cancel + reassign |

### 8.20 Support timeline events (minimum)

```text
QUOTED, CONFIRMED, PAYMENT_AUTHORIZED, OFFER_SENT, ASSIGNED, REASSIGNED,
ARRIVED_PICKUP, PICKED_UP, ARRIVED_DROPOFF, DELIVERED, PAYMENT_CAPTURED,
CANCELLED, REFUNDED, FRAUD_FLAG
```

### 8.21 Capacity signal for quotes

```text
utilization = active_jobs / on_duty_couriers (zone)
if utilization > U_high: inflate ETA or refuse new quotes
if utilization < U_low: promotions OK
Signal computed from zone metrics every few seconds—not per-request full scan
```

### 8.22 Security notes

- Courier app attest / signed location optional at 100×
- PII: addresses encrypted at rest; minimize support tool exposure
- Signed proof URLs short-lived
- Rate-limit quote API against scraping merchant demand

### 8.23 Comparison: scoped delivery vs ride-sharing

| Dimension | Scoped delivery | Rides |
|-----------|-----------------|-------|
| Seats | Parcel | Rider seats |
| Stops | Pickup+dropoff (+merchant) | Similar |
| Proof | PIN/photo common | Less |
| Batching | Natural later | Pool products |
| Scope | Zone hard boundary | Similar city ops |

### 8.24 Interview unit-check drill

```text
200K location/s × 150 B = 30 MB/s ≈ 2.6 TB/day if uncompacted
→ downsample + TTL mandatory; saying "store forever in PG" fails the interview
```

### 8.25 Brownout order

```text
1. Reduce map update frequency for customers
2. Pause marketing push that creates demand
3. Disable non-critical ratings prompts mid-trip
4. Stop taking new quotes if assign p99 catastrophic
NEVER: double-assign to "catch up"
```


*End of scoped delivery system design.*
