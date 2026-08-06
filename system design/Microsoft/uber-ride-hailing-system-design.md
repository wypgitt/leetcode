# System Design: Uber / Ride-Hailing (Microsoft Interview Practice)

> **Focus areas:** Geo indexing · Driver location · Dispatch / matching · Trip state machine · Surge · ETA · Payments hooks · Realtime updates  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct geo + matching math, explicit consistency for trip assignment (no double-dispatch), deal-breakers for “SQL `ORDER BY distance` on all drivers every request”  
> **Interview theme:** Microsoft loop (team may ask domain problems) — ride-hailing is a classic marketplace + geo + realtime prompt; emphasize APIs, failure handling, and regional cells

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

Goal: **bound the product**—an Uber-class ride-hailing marketplace: riders request trips, drivers are matched nearby, locations stream in realtime, trips progress through a state machine, pricing/surge and payments are hooked, and the system survives city-scale peaks (rain, concerts, New Year).

### 1.0 What this is / is not

| Dimension | **Ride-hailing (this doc)** | Not this |
|-----------|-------------------------------|----------|
| Primary job | Match riders ↔ drivers; run trip lifecycle | Full autonomous robotaxi research |
| Success | Low match latency; fair dispatch; correct trip state | Perfect global traffic ML paper |
| Geo | Nearby driver query + ETA | Building Google Maps from scratch |
| Money | Pricing quote + payment capture hooks | Full ledger/banking core |
| Food delivery | Out of MVP (similar matching ideas) | Uber Eats deep dive |
| Microsoft lens | Clear APIs, reliability, regional ops | Must-use Azure brand names |

**Scope statement:** Design Uber-like ride request, geo-indexed driver locations, dispatch/matching, trip lifecycle, realtime tracking, and surge/pricing hooks—scaled through 10× / 100× / 1,000× with city/region cells.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Actors? | Riders, drivers, optional dispatch ops | Separate apps + roles |
| F2 | Request ride? | Pickup, dropoff, product type (UberX) | Trip request API + quote |
| F3 | Matching? | Nearby available drivers; offer / accept | Dispatch service + timeouts |
| F4 | Driver location? | Frequent GPS updates when online | Location stream + geo index |
| F5 | Tracking? | Rider sees driver approach; both see trip | Pub/sub / websocket |
| F6 | Trip states? | Requested→Matched→Arrived→Ongoing→Completed/Canceled | Explicit state machine |
| F7 | Pricing? | Upfront quote; surge multipliers | Pricing service; quote TTL |
| F8 | Payments? | Capture on complete; failure retry | Payment orchestrator hook |
| F9 | ETA? | Pickup ETA + trip ETA | Routing/ETA service (can stub) |
| F10 | Ratings? | After trip | Async ratings |
| F11 | History? | Past trips | Trip store |
| F12 | Pooling / shared? | Out of MVP or Phase 1.5 | Matching complexity |
| F13 | Scheduled rides? | Phase 1.5 | Scheduler |
| F14 | Safety? | SOS / share trip | Notifications + location share |

**MVP functional scope:**

1. Driver go online/offline; stream location.  
2. Rider gets upfront price quote (TTL).  
3. Rider requests trip; system matches a driver.  
4. Driver accepts/rejects with timeout; re-match on reject.  
5. Trip state machine through completion/cancel.  
6. Realtime location updates to rider during en-route/ongoing.  
7. Basic surge by geoshard demand/supply.  
8. Payment capture hook; trip history; ratings stub.

**Out of MVP:**

- Intercity / airport complex products deep optimization  
- Multi-stop / package delivery  
- Full fraud ML  
- Driver incentives platform  
- Perfect map tiles hosting  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Match latency? | Feels quick | p99 match offer < 5–15s typical city |
| N2 | Location freshness? | Driver dot moves | Location update ingest p99 < 100–200ms; display lag < 1–3s |
| N3 | Double dispatch? | Never two drivers for one trip | Strong assignment invariant |
| N4 | Availability? | City must work in peak | 99.9% request path; degrade noncritical |
| N5 | Geo accuracy? | Good enough for dispatch | ~50–100m; map-matched later |
| N6 | Scalability? | Many cities independently | Cell per city/region |
| N7 | Durability? | No lost completed trips | Durable trip ledger |
| N8 | Security? | PII / location sensitive | AuthZ; audit; retention |
| N9 | Fairness? | Drivers not starved unfairly | Matching policy explainable |
| N10 | Maintainability? | Clear planes | Location vs Dispatch vs Trip vs Payments |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Driver online → location updates → appears in geo index.  
2. Rider quote → request → match → driver accepts → en route → arrive → start → complete → pay → rate.  
3. Surge in busy downtown → higher quote → still match.  
4. Rider cancels before accept → release hold.  
5. Driver rejects → offer next candidate.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two drivers accept same offer | Only one wins; other gets “already taken” |
| Rider requests twice quickly | Idempotency; one active trip |
| Driver GPS jumps / tunnels | Smooth / ignore outliers; last-known |
| No drivers nearby | Expand radius / wait / fail with UX |
| Payment fails at end | Retry; debt state; allow appeals |
| App crash mid-trip | Resume from durable trip state |
| Cell phone offline briefly | Queue location; reconnect sync |
| Surge oscillation | Dampen; time-bucketed multipliers |
| Hot concert venue pin | Geoshard hotspot; isolate matching |
| Wrong-way / long ETA | Reprice policy? usually stick to quote |
| Fraudulent GPS spoof | Signals; out of MVP deep dive |
| Dispatch timeout | Requeue request; notify rider |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 large city) | 10× | 100× | 1,000× |
|--------|-------------------------|-----|------|--------|
| Cities / cells | 1 | 10 | 100 | 1,000 |
| DAU riders | 1M | 10M | 100M | 1B class |
| Concurrent online drivers | 50K | 500K | 5M | 50M |
| Peak trip requests / s | 500 | 5K | 50K | 500K |
| Location updates / s | 100K | 1M | 10M | 100M |
| Peak matches attempted / s | 500 | 5K | 50K | 500K |
| Active trips | 20K | 200K | 2M | 20M |
| GPS point size | ~50–100 B | — | — | — |

**What each jump forces:**

- **10×:** City sharding; Redis geo / S2 indexes; async dispatch; websocket gateways.  
- **100×:** Multi-city cells; location stream partitions; matching workers per geoshard; surge service.  
- **1,000×:** Global directory; heterogeneous city configs; edge gateways; strict hot-geohash isolation; ML ETA fleet.

### 1.5 Etc. (Constraints & Assumptions)

- Maps/routing can be an external ETA/distance provider with a stub interface.  
- Payments are an orchestrator calling a PSP (Stripe-like), not a bank.  
- One active trip per rider MVP.  
- Matching is offer-based (driver accepts) unless interviewer wants auto-assign.  
- Microsoft interviewers often push on **race conditions** (double accept) and **geo index choice**.

**Scope statement to repeat back:**

> Design Uber-like ride-hailing: driver location streaming into a geo index, request/quote, dispatch with exactly-one assignment, trip state machine, realtime tracking, and surge hooks—scaled by city cells—without scanning all drivers in SQL for every request.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| Location ingest | Driver GPS | 100K/s | Location |
| Trip requests | Ride requests | 500/s | Trip / Dispatch |
| Matching compute | Candidate search + offers | ~500–2K/s | Dispatch |
| Realtime fanout | Rider/driver updates | ~50K–200K msg/s | Gateway |
| Quotes / pricing | Fare quotes | ~1–2K/s | Pricing |
| Payments | Completions | ~100–500/s | Payments |

**Anti-pattern:** treating location QPS and trip QPS as the same bottleneck.

### 2.2 Location update math

```text
Online drivers = 50,000
Update frequency = 2 s (or 4 s) when idle; 1–2 s when on trip
Updates/s ≈ 50_000 / 2 = 25_000  (idle-only)
Often higher with on-trip + product → design for ~100K/s peak city

Payload ~80 B → 100K × 80 ≈ 8 MB/s ingest (easy for Kafka)
Hard part: updating geo index cheaply + fanout to interested riders
```

At **100× (10M drivers online globally):** ~10M/2 = 5M updates/s → partition by city/geoshard mandatory.

### 2.3 Request & match math

```text
Peak requests = 500/s in one city
For each request:
  geo search K candidates (e.g. 20–50)
  rank by ETA / rating / idle time
  offer to top 1 (or batch of 1–3 sequentially)

Geo search must be O(log n) / grid lookup, not O(n)
```

### 2.4 Geo index memory

```text
Driver record in memory index:
  driver_id, lat, lng, status, product, last_ts ≈ 64–128 B
50K drivers × 128 B ≈ 6.4 MB — tiny per city

1000 cities × 50K = 50M drivers × 128 B ≈ 6.4 GB — still OK if sharded by city
```

### 2.5 Active trip state

```text
20K active trips × 1 KB state ≈ 20 MB
Plus websocket subscriptions rider↔trip, driver↔trip
```

### 2.6 Surge / demand metering

```text
City divided into S2 cells / geohashes at ~1 km
For each cell every 10–30s:
  demand = requests
  supply = online idle drivers
  multiplier = f(demand/supply) clamped
```

### 2.7 Bandwidth / realtime

```text
Rider tracking driver: push location every 1–2s
20K active trips × 0.5–1 update/s × 100 B ≈ 1–2 MB/s city — fine
Gateway connections: riders + drivers online
```

### 2.8 Storage

```text
Trips/day city: assume 2M
Trip row ~1–2 KB → 2–4 TB/year/city raw with history
Location breadcrumbs: usually sampled / TTL short (hours) unless compliance
Don’t store every GPS point forever in MVP
```

### 2.9 Matching latency budget

```text
Budget 5s p99 to first offer:
  validate + quote check     50–100ms
  geo candidates             10–50ms
  rank + filters             10–50ms
  offer push to driver       50–200ms
  driver think time          5–15s (dominant — product)
System match compute should be << human accept time
```

### 2.10 Amplification & pitfalls

| Naive | Problem | Fix |
|-------|---------|-----|
| `SELECT * FROM drivers ORDER BY distance` | Full scan | Geo hash / S2 / Redis GEO |
| Update SQL row every GPS ping | Write melt | In-memory index + periodic snapshot |
| Match without lock | Double dispatch | Conditional assign / lease |
| Global matching queue | Cross-city latency | City cell |
| Store all GPS forever | Cost | TTL / sample |

### 2.11 Progressive scale table

| Concern | Baseline | 10× | 100× | 1,000× |
|---------|----------|-----|------|--------|
| Location bus | Kafka city | multi-city | global + cells | edge ingest |
| Geo index | Redis GEO / memory | sharded hashes | per cell | hierarchical |
| Dispatch | service + DB leases | workers/geoshard | many cells | policy engine |
| Realtime | WS gateway | sticky | geo/event router | edge WS |

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
RIDER                              DRIVER
+----------------------+           +----------------------+
| Map · pickup pin     |           | Go Online            |
| Dropoff              |           | Map · heat/surge     |
| UberX $14.20  4 min  |           | Incoming request     |
| [Request]            |           | $8.40  3 min away    |
| Driver approaching   |           | [Accept] [Reject]    |
| Trip in progress     |           | Navigate to pickup   |
+----------------------+           +----------------------+
```

### 3.2 Domain model

```text
Rider / Driver (User roles)
DriverSession (online, product types, city_id)
DriverLocation (ephemeral)
Trip
  trip_id, rider_id, driver_id?, state, pickup, dropoff
  quote_id, prices, timestamps, cancel_reason
Quote (ttl, surge, amount)
Offer (trip_id, driver_id, expires_at, state)
PaymentIntent (trip_id, status)
```

### 3.3 Trip state machine

```text
CREATED → REQUESTING → OFFERING → MATCHED → DRIVER_ARRIVING
 → DRIVER_ARRIVED → IN_TRIP → COMPLETED
                  ↘ CANCELED (from several states)
OFFERING → (timeout/reject) → REQUESTING (rematch) → EXPIRED/NO_DRIVERS
```

**Invariants:**

1. At most one `driver_id` assigned in `MATCHED+` for a trip.  
2. Driver has at most one active assigned trip.  
3. State transitions validated server-side; clients cannot skip arbitrarily.  
4. Payment capture only from `COMPLETED` (or policy exceptions).

### 3.4 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/drivers/session` | Go online |
| DELETE | `/v1/drivers/session` | Go offline |
| POST | `/v1/drivers/location` | Batch location update |
| POST | `/v1/quotes` | Upfront quote |
| POST | `/v1/trips` | Request trip (idempotent) |
| POST | `/v1/trips/{id}/cancel` | Cancel |
| POST | `/v1/offers/{id}/accept` | Driver accept |
| POST | `/v1/offers/{id}/reject` | Driver reject |
| POST | `/v1/trips/{id}/events` | arrived / start / complete |
| GET | `/v1/trips/{id}` | Trip snapshot |
| WS | `/v1/realtime` | Locations + trip events |

### 3.5 Architecture options

| Option | Idea | Pros | Cons | Verdict |
|--------|------|------|------|---------|
| **A. Single SQL** | Drivers table + distance query | Simple | Cannot scale location | Reject at city peak |
| **B. Push all locations to all riders** | Broadcast | — | Impossible | Deal-breaker |
| **C. Geo index + dispatch service (chosen)** | Memory/Redis geo; trip DB for truth | Standard | Ops complexity | **Choose** |
| **D. Fully decentralized P2P match** | Devices match | — | Trust/safety | Reject |

### 3.6 Component architecture

```text
Rider/Driver Apps
      |  HTTPS + WSS
      v
API Gateway / Edge
      |
      +--> Trip Service (state machine, durable)
      +--> Dispatch / Matching Service
      +--> Location Service (ingest + geo index)
      +--> Pricing / Surge Service
      +--> ETA / Routing Adapter
      +--> Payment Orchestrator
      +--> Notification Service
      |
Kafka: location, trip_events, offers
Redis: geo index, offer locks, surge multipliers
Postgres/Spanner/Cosmos: trips, users, payments refs
```

### 3.7 Geo indexing (core)

#### Options

| Approach | How | Pros | Cons |
|----------|-----|------|------|
| **Redis GEO** | `GEOADD` / `GEOSEARCH` | Fast, simple | Memory; city shard |
| **S2 / Geohash grids** | Drivers in cell sets | Controllable | More code |
| **Quadtree custom** | In-process | Flexible | Rebuild / HA |
| **PostGIS** | SQL geo | Familiar | Write-heavy GPS |

**Choice:** Redis GEO or in-memory geohash rings **per city cell**, updated on location ingest; durable trip state elsewhere.

```text
on_location(driver_id, lat, lng, ts, status):
  if stale(ts): ignore
  if outlier(prev, lat,lng): soft-ignore / map-match later
  geo.upsert(city, driver_id, lat, lng)
  meta.set(driver_id, {status, product, ts})
  if driver.on_trip: publish to trip subscribers only
```

**Nearby search:**

```text
candidates = geo.search(pickup, radius_m=3000, count=50)
filter status==IDLE and product matches and not banned
rank by ETA (or haversine as stub) + score
```

**Expanding radius:** 1km → 2km → 5km with time budget.

### 3.8 Matching / dispatch (core)

#### Offer-based protocol

```text
on_trip_requested(trip):
  while trip.state == REQUESTING and not expired:
    cands = geo_nearby(trip.pickup, filters)
    cands = rank(cands, trip)
    for d in cands:
      if try_reserve_driver(d, trip, lease=15s):
         send_offer(d, trip)
         wait accept/reject/timeout
         if accept and cas_assign(trip, d):
            release others; return MATCHED
         else:
            release_driver(d)
    expand radius / wait backoff
  fail NO_DRIVERS
```

#### Exactly-once assignment

| Technique | Mechanism |
|-----------|-----------|
| Driver lease | Redis `SET driver:{id}:busy NX EX 15` |
| Trip CAS | `UPDATE trips SET driver_id=?, state=MATCHED WHERE id=? AND state=OFFERING AND driver_id IS NULL` |
| Offer id | Unique; accept only if offer active |

**Deal-breaker:** “send offer to 20 drivers at once without fencing” → multiple accepts → chaos. If batching offers, still only one CAS wins; others revoked immediately.

#### Auto-assign variant

System assigns best driver without accept (some markets). Still need atomic reserve. Faster UX; less driver choice.

### 3.9 Pricing & surge

```text
quote:
  base = pricing.model(distance, time, product)
  surge = surge_service.multiplier(geocell(pickup), now)
  total = base * surge
  store quote with TTL (e.g. 2 min) and quote_id
request must reference valid quote_id (or requote)
```

Surge computation is eventually consistent over 10–30s windows; avoid updating every GPS ping.

### 3.10 Realtime tracking

```text
Trip channel: trip:{trip_id}
  subscribers: rider, driver, optional share-link viewers
Location updates for assigned driver → publish to trip channel
Trip state changes → publish events
```

Do **not** bind rider to raw citywide location firehose.

### 3.11 Consistency model

| Data | Consistency |
|------|-------------|
| Trip assignment | Strong (CAS / txn) |
| Trip state transitions | Strong on trip record |
| Driver location | Ephemeral eventual; last-write-wins with ts |
| Surge | Eventual / windowed |
| Payments | Strong orchestrated state + PSP |

---

## 4. Architecture Diagram

### 4.1 End-to-end request path

```text
Rider App                Driver App
   |                         |
   | POST /quotes            | POST /location  (frequent)
   v                         v
Pricing Svc              Location Ingest → Kafka → Geo Index Updaters
   |
   | POST /trips
   v
Trip Svc ──► Dispatch Svc ──► GEOSEARCH → rank → Offer
   |                              |
   |                              +--> Driver WS: incoming offer
   |                              |
   |◄──── accept CAS assign ──────+
   |
   +--> Trip state MATCHED
   +--> Realtime: both subscribe trip:{id}
   +--> On complete → Payment Orchestrator
```

### 4.2 City cell architecture

```text
                 Global User Directory / Auth
                           |
       +-------------------+-------------------+
       v                   v                   v
   Cell Seattle        Cell NYC            Cell London
   - Location idx      - Location idx      - ...
   - Dispatch          - Dispatch
   - Trip DB shard     - Trip DB shard
   - Surge             - Surge
   - WS gateways       - WS gateways
```

Cross-city trips rare in MVP; airport edge cases use cell routing rules.

### 4.3 Double-accept fencing

```text
Offer to Driver A and B (sequential preferred)
       |
Accept A arrives ---- CAS trip SET driver=A WHERE driver IS NULL → OK
Accept B arrives ---- CAS fails → 409 ALREADY_MATCHED → notify B revoke
```

---

## 5. Design Deep Dive

### 5.1 Reliability

| Failure | Mitigation |
|---------|------------|
| Dispatch worker crash | Trip stays REQUESTING; another worker resumes; offers expire via TTL |
| Redis geo loss | Rebuild from recent location stream (seconds); drivers refresh ASAP |
| Trip DB failover | Multi-AZ; idempotent event apply |
| Driver accept network retry | Idempotent accept by offer_id |
| Payment PSP down | Complete trip; payment retry queue; user messaging |
| WS gateway death | Clients reconnect; resume trip snapshot via GET |
| Kafka lag on locations | Drop/coalesce old points; keep latest per driver |

**Degradation order:**

1. Coalesce location updates (lower frequency)  
2. Simplify ranking (distance only)  
3. Disable noncritical surge animations / heatmaps  
4. Stretch match SLA messaging  
5. Stop taking new requests only if trip durability at risk  

**Exactly-one assignment tests:** chaos two accepts; verify single winner.

### 5.2 Scalability

**Partition keys**

| Stream | Key |
|--------|-----|
| Location updates | `city_id:geohash` or `driver_id` with city router |
| Trip | `city_id` + `trip_id` |
| Offers | `driver_id` |
| Surge | `city_id:cell_id` |

**Hot geohash (stadium):**

- Dedicated matching workers  
- Smaller offer timeouts  
- Cap candidates  
- Possibly staging lots / virtual pickup pins (product)  

**Location write coalescing:**

```text
Ingest buffer per driver: keep latest point every 1s flush
GEOADD latest only — intermediate points optional for path polish
```

**Horizontal WS:** sticky sessions by `user_id`; pubsub (Redis) for trip channels across gateways.

### 5.3 Maintainability

| Service | Owns |
|---------|------|
| Location | Ingest, geo index, freshness SLOs |
| Dispatch | Matching policies, offers, leases |
| Trip | State machine source of truth |
| Pricing | Quotes, surge multipliers |
| ETA | Adapter to maps provider |
| Payments | Capture/refund workflows |
| Realtime | Gateway + channel routing |

**Policy as data:** cancel fees, offer timeouts, max radius — config per city.

**Observability KPIs**

| KPI | Why |
|-----|-----|
| Match rate | Supply/demand health |
| Time-to-match p95 | UX |
| Cancel rate after match | Quality |
| Location staleness | Index health |
| Double-assign attempts | Bug detector |
| Payment success | Revenue |

### 5.4 ETA & ranking

MVP ranking score:

```text
score = w1*(1/eta) + w2*rating + w3*idle_time_fairness - w4*cancel_rate
```

ETA from routing provider; fallback haversine / speed estimate if budget tight in interview.

### 5.5 Cancellations & money

| Who / when | Effect |
|------------|--------|
| Rider before match | Free |
| Rider after match (grace) | Maybe free |
| Rider after grace | Cancel fee hook |
| Driver cancel | Penalties / re-match |

Keep fee policy outside core state machine transitions.

### 5.6 Security & privacy

- Location is sensitive PII — encrypt in transit; retain breadcrumbs short  
- Share-trip links: capability tokens, revoke on complete  
- AuthZ: only rider/driver of trip see precise track  
- Rate-limit location posts; detect spoof heuristics  

### 5.7 Multi-region / cell failover

Active-active for same city is hard (split brain matching). Prefer:

- **Single active matching cell per city**  
- Warm standby in paired AZ/region  
- Failover: promote standby; drivers re-online refresh geo  

---

## 6. Wrap-Up

### 6.1 Designed

Ride-hailing with geo-indexed driver locations, quote/surge, dispatch with atomic assignment, trip state machine, realtime trip channels, and city-cell scaling.

### 6.2 Trade-offs

| Decision | Chose | Rejected | Why |
|----------|-------|----------|-----|
| Geo | Redis/memory GEO per city | SQL full scan | Scale |
| Match | Offer + CAS | Unguarded multi-offer | Exactly one driver |
| Location | Ephemeral index | Durable every ping | Cost |
| Architecture | City cells | One global matcher | Latency/isolation |
| Maps | Adapter stub | Build maps | Scope |

### 6.3 Risks

- Supply imbalance / long waits  
- GPS quality  
- Fraud  
- Payment retries  
- Hotspot events  

### 6.4 60-second pitch

> “I’d split location, dispatch, and trip truth. Drivers stream GPS into a per-city geo index. Requests create durable trips; dispatch searches nearby idle drivers, leases one, offers, and CAS-assigns so two accepts can’t both win. Realtime updates ride on trip channels, not city firehoses. Surge is windowed per geocell. We scale by city cells and protect hot stadium hashes.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Geo

**Q1. Redis GEO vs S2 cells?**  
GEO: simple radius queries. S2: better control for surge tiles, ring search, custom memory stores. Either fine if sharded by city.

**Q2. How to handle antimeridian / poles?**  
Library projection issues; for city cells mostly irrelevant; mention awareness.

**Q3. Map matching?**  
Snap to roads async; dispatch can use raw GPS with smoothing.

**Q4. How often should drivers ping?**  
1–4s tradeoff battery vs freshness; adaptive by state (idle vs approaching).

### 7.2 Matching

**Q5. Sequential vs parallel offers?**  
Sequential: simpler exactly-one, higher latency. Parallel: faster fill, need revoke + CAS. Explain choice.

**Q6. Fairness to drivers?**  
Idle time, earnings balancing — policy weights; avoid always nearest if it starves others.

**Q7. Pooling (shared rides)?**  
Insert matching complexity: vehicle capacity, detour bounds, combinatorial — Phase 1.5.

**Q8. What if geo index says idle but driver started another trip?**  
Lease + status check; version tokens on driver session.

### 7.3 Consistency

**Q9. Prove no double dispatch.**  
Driver lease NX + trip CAS; property test.

**Q10. Rider double-submit?**  
Idempotency-Key → same trip_id.

**Q11. Clock skew on offer expiry?**  
Server expiry timestamps; drivers get `expires_at_server`.

### 7.4 Scale / geo distribution

**Q12. 1000 cities?**  
Cell per city; global auth/profile; local matching.

**Q13. Driver crosses city boundary?**  
Re-register session in new cell; move location stream.

**Q14. Global dashboard?**  
Aggregate metrics async; not on request path.

### 7.5 Pricing / payments

**Q15. Quote vs final price?**  
Upfront model locks quote; route changes policy-dependent.

**Q16. Payment capture failures?**  
State `COMPLETED_UNPAID`; retry; block new rides optionally.

**Q17. Surge feedback loop?**  
Dampen; max multiplier; communicate UX.

### 7.6 Microsoft-flavored

**Q18. Map to Azure?**  
Event Hubs, Redis Cache, AKS, Cosmos/SQL, SignalR/WebPubSub, Front Door — optional mapping.

**Q19. How do you operate dispatch?**  
City config, feature flags, kill switches for matching variants, shadow policies.

**Q20. LLD follow-up?**  
They may ask class model for Trip/Offer — keep state machine clean (see related LLD doc in bank).

### 7.7 Traps

| Trap | Answer |
|------|--------|
| Store GPS in SQL row updates | No — stream + memory index |
| Broadcast all driver points to all riders | No — trip channel |
| Eventual assignment OK | No — strong for assign |
| One global Redis | No — per city at scale |

---

## 8. Appendices

### Appendix A — Glossary

| Term | Meaning |
|------|---------|
| Dispatch | Matching riders to drivers |
| Geo index | Spatial index of driver positions |
| Offer | Time-bounded proposal to a driver |
| Surge | Demand/supply price multiplier |
| Cell | Independent city/region deployment unit |
| Lease | Short-lived reservation of driver |
| CAS | Compare-and-set conditional update |
| ETA | Estimated time of arrival |

### Appendix B — Schema sketch

```sql
trips(
  trip_id PK,
  city_id,
  rider_id,
  driver_id NULL,
  state,
  pickup_lat, pickup_lng,
  dropoff_lat, dropoff_lng,
  quote_id,
  price_cents,
  surge_multiplier,
  created_at, updated_at,
  version
)

offers(
  offer_id PK,
  trip_id,
  driver_id,
  state, -- pending|accepted|rejected|expired|revoked
  expires_at
)

driver_sessions(
  driver_id PK,
  city_id,
  status, -- offline|idle|busy
  products,
  session_version
)

quotes(
  quote_id PK,
  rider_id,
  payload_json,
  expires_at
)
```

### Appendix C — Rank pseudocode

```text
function rank(cands, trip):
  scored = []
  for d in cands:
    eta = eta_service.estimate(d.loc, trip.pickup)
    s = 0.5*(1/(eta+1)) + 0.2*d.rating/5 + 0.2*normalize(d.idle) - 0.1*d.cancel_rate
    scored.append((s,d))
  return sort_desc(scored)
```

### Appendix D — Location message

```json
{
  "driver_id": "d_1",
  "city_id": "sea",
  "lat": 47.606,
  "lng": -122.332,
  "ts": 1735689600123,
  "status": "idle",
  "accuracy_m": 12
}
```

### Appendix E — Capacity cheatsheet (large city baseline)

| Metric | Order |
|--------|-------|
| Online drivers | 50K |
| Location QPS | 100K |
| Request QPS | 500 |
| Active trips | 20K |
| Geo memory | <10 MB |

### Appendix F — Expanding radius policy

| Attempt | Radius | Wait |
|---------|--------|------|
| 1 | 1.5 km | 0s |
| 2 | 3 km | 3s |
| 3 | 5 km | 5s |
| 4 | fail / schedule retry | — |

### Appendix G — Interview checklist

- [ ] Locked MVP (no eats/pooling unless asked)  
- [ ] Location QPS math  
- [ ] Geo index choice  
- [ ] Double-dispatch fencing  
- [ ] Trip state machine  
- [ ] Realtime channel scope  
- [ ] Surge as separate plane  
- [ ] City cell scaling  
- [ ] Degradation story  
- [ ] Payment hook, not bank  

### Appendix H — Related prompts

- Uber Eats at scale  
- Robo-taxi marketplace (Amazon bank)  
- Ride-sharing class + DB LLD  
- Notification system  
- Presence API  

### Appendix I — Offer sequence diagram

```text
Dispatch          Redis Lease        Driver         Trip DB
   |--SET NX busy-->|                  |              |
   |--WS offer-----+------------------>|              |
   |               |                  |--accept------>|
   |               |                  |               |--CAS assign
   |<------------- accept ok -------------------------|
   |--revoke others / publish MATCHED---------------->|
```

### Appendix J — What to draw first on whiteboard

1. Apps → API → Trip / Dispatch / Location  
2. Geo index box  
3. State machine  
4. CAS assign callout  
5. City cell box for scale  

### Appendix K — Sample NFRs card

```text
Match p95 < 8s (with supply)
Location display lag < 2s
Assignment correctness = 100% (no dual drivers)
Trip durable after state change ACK
```

### Appendix L — Cancel race

If rider cancels while driver accepting: cancel transition CAS from OFFERING/REQUESTING; accept CAS fails; driver notified.

### Appendix M — Why Microsoft asks this

Tests marketplace races, geo, realtime, and operational cells—skills transfer to Azure mobility partners, Maps integrations, or any regional matching system.

### Appendix N — Progressive roadmap

| Phase | Add |
|-------|-----|
| MVP | X product, offer match, surge v1 |
| 1.5 | Scheduled, airport queues, shared |
| 2 | ML ETA, fraud, incentives |
| 3 | Multi-modal / robotaxi hooks |

---

*End of Uber / ride-hailing system-design prep doc (Microsoft interview practice).*
