# System Design: Social or Rideshare Platform (Facebook / Uber Style)

> **Focus areas:** Candidate choice · Matching · Geo · Dispatch · ETA · Consistency · Fairness · Progressive scale  
> **Primary deep dive:** **Rideshare** (Uber-like): matching, geo indexing, dispatch, ETA  
> **Secondary:** Short “if Facebook instead” appendix for feed/social  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct geo math intuition, explicit consistency for ride state, honest matching trade-offs, no magical global locks

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices) (includes **If Facebook instead**)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **choose quickly**, bound the product, and show progressive scale thinking. Interviewer often says: *“Design Facebook or Uber—your choice.”*

### 1.0 Choice framing (60 seconds)

| Option | Core hard problems | Pick when… |
|--------|--------------------|------------|
| **Rideshare (Uber)** | Geo, matching, dispatch, ETA, consistency of trip state | You want location + marketplace |
| **Social (Facebook)** | Feed fanout, graph, notifications, celebrity hot keys | You want read-heavy social graph |

**Recommendation for this doc / interview:** Pick **rideshare**—distinctive geo/matching; still general distributed systems. Mention you’d do feed fanout if they prefer social.

**Assumptions (state aloud):** City-scale MVP → country → multi-country; riders + drivers; cards already exist (payments as black box with webhooks).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are actors? | Riders, drivers, ops | Separate apps; roles |
| F2 | Core flow? | Request ride → match driver → pickup → trip → pay → rate | Ride state machine is sacred |
| F3 | Vehicle types? | Economy / XL / premium | Supply pools per type |
| F4 | Matching goal? | Fast pickup + fairness; not only minimize ETA | Multi-objective scorer |
| F5 | Driver location? | Frequent GPS updates when online | Geo index + streaming ingest |
| F6 | ETA? | Pickup ETA + trip ETA | Routing engine / approximations |
| F7 | Surge? | Optional pricing signal | Pricing service; not only matching |
| F8 | Cancel? | Rider/driver cancel with fees policy | Explicit transitions + billing hooks |
| F9 | History? | Trip receipts, maps | Durable trip store |
| F10 | Regions? | Expand city by city | City/region cells |
| F11 | Payments? | Capture after trip; tips | Orchestrate; PSP external |
| F12 | Safety? | Share trip, SOS | Location share + alerts |

**MVP functional scope (lock with interviewer):**

1. Driver go online/offline; stream location.  
2. Rider request ride with pickup/dropoff + product type.  
3. **Match** eligible nearby driver; offer → accept/reject.  
4. Navigate pickup → start trip → complete.  
5. Basic **ETA** for pickup.  
6. Cancel paths; trip history.  
7. Payments: authorize/capture via external PSP (stub OK).  
8. City-scoped operation.

**Out of MVP:**

- Shared rides / carpool optimization perfection  
- Autonomous vehicles  
- Multi-stop complex routing  
- Full fraud ML platform  
- Global active-active dual writers on same trip  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Match latency | Feels instant | p99 < 3–5s to first offer (city healthy supply) |
| N2 | Location freshness | Drivers moving | Location age < 5–10s typical for matching |
| N3 | Consistency | One driver ↔ one ride | Strong invariants on assignment |
| N4 | Availability | City ops continue if one AZ dies | Multi-AZ control plane |
| N5 | Geo accuracy | Good enough for dispatch | S2/H3 cells; routing approx OK early |
| N6 | Fairness | Drivers not starved; riders not stuck | Explicit policies |
| N7 | Scale path | 10× → 1000× | City sharding |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Driver online → locations stream → appears in geo index.  
2. Rider requests → match finds driver → offer → accept → assigned.  
3. Driver arrives → rider pickup → trip → dropoff → payment → ratings.  
4. No drivers → queue / expand radius / fail with message.  
5. Driver rejects → next candidate; track reject cooldown.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two riders matched to same driver | Fence assignment with compare-and-set; one wins |
| Driver accepts two offers (race) | Only one assignment valid; other re-match |
| Driver GPS stale | Exclude if last_seen > T; degrade |
| Rider cancels after accept | Release driver; fee policy async |
| Driver cancel after accept | Rematch rider; penalize driver |
| Network blip during offer | Offer TTL; idempotent accept |
| City hotspot stadium exit | Surge + widen radius + cap wait |
| Payment fails | Retry; debt state; don’t lose trip record |
| Clock skew on offer expiry | Server-side TTL authority |
| Cross-city trip | Cell ownership by pickup city or home policy |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 city) | 10× | 100× | 1,000× |
|--------|-------------------|-----|------|--------|
| Peak concurrent drivers online | 5K | 50K | 500K | 5M |
| Peak concurrent riders requesting | 1K | 10K | 100K | 1M |
| Rides / day | 200K | 2M | 20M | 200M |
| Location updates /s | 5K | 50K | 500K | 5M |
| Match attempts /s | 50 | 500 | 5K | 50K |
| Cities / cells | 1 | 10 | 100 | 1,000 |
| Peak API QPS | 10K | 100K | 1M | 10M |
| Avg trip duration | 15 min | 15 | 12–20 | 12–20 |

**What each jump forces:**

- **10×:** Shard geo by city/hex; separate location ingest plane.  
- **100×:** Multi-city cells; match workers per cell; ETA cache; fairness queues.  
- **1,000×:** Regional cells; hierarchical geo; approximate matching; heavy downsampling of locations for distant viewers.

### 1.5 Etc. (Constraints & Assumptions)

- Map tiles / turn-by-turn may use external provider; we own **dispatch truth**.  
- Payments via Stripe-like PSP.  
- One active trip per driver; one active request per rider (MVP).  
- **NVIDIA interview context:** still a valid general DS question; show geo + marketplace skill.

**Scope statement:**

> Design a rideshare marketplace: drivers stream locations into a geo index; riders request trips; a matcher offers and assigns drivers under strong assignment invariants; ETA guides UX; system scales from one city to ~1000 cities via cell sharding, with progressive techniques for location firehose, matching fairness, and consistency.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Location updates | 5K/s | 5M/s | Dominates ingest |
| Ride request / match | 50/s | 50K/s | Critical path |
| Trip state transitions | ~100/s | ~100K/s | Strong consistency needs |
| ETA queries | 200/s | 200K/s | Cacheable short TTL |
| Receipts / history reads | 500/s | 500K/s | Read replicas OK |
| Payments webhooks | low | higher | Async |

**Critical insight:** **Location QPS ≫ match QPS**. Design a specialized location pipeline; do not write every GPS ping as a row in the primary OLTP trips DB.

### 2.2 Location math

```text
5K online drivers, update every 1s → 5K/s baseline
If update every 4s: 1.25K/s (trade freshness)

Payload ~100 B → 5K/s × 100 B = 500 KB/s (tiny bandwidth)
At 5M/s × 100 B = 500 MB/s → still OK with regional ingest, but CPU/index update dominates

Index cost: each update = delete old cell membership + insert new (or update pointer)
```

### 2.3 Matching math

```text
Peak requests 50/s baseline
Each match: query K hex rings, score M candidates (e.g. 20), offer 1
CPU bound more than IO if geo index in memory/Redis

1000×: 50K matches/s → must be sharded by city/cell; no global matcher
```

### 2.4 Storage

```text
Trip record ~2–5 KB
200K rides/day × 5 KB ≈ 1 GB/day baseline
1000×: 200M/day × 5 KB ≈ 1 TB/day → partition by date/city; cold archive

Location history: usually NOT full fidelity forever
  retain raw 24–72h for safety/dispute; downsample for analytics
```

### 2.5 ETA

```text
Naïve: call external routing every request → expensive + rate limited
Cache: (origin_hex, dest_hex, minute_of_day) → ETA with TTL
Fallback: haversine / road-speed heuristic when cache cold
```

### 2.6 Critical bottlenecks

1. **Location ingest + geo index updates**  
2. **Double-assign races under hotspot**  
3. **Hot stadium hex** overwhelming one shard  
4. **Chatty ETA provider calls**  
5. **Cross-cell trips / cell rebalancing**  

---

## 3. High-Level Design

### 3.1 Brief social vs rideshare (then commit)

```text
Social:   graph + feed fanout + media + notifications
Rideshare: geo supply + matching marketplace + trip FSM + ETA
```

**Commit:** rideshare deep dive below; social in Appendix 8.x.

### 3.2 Core abstractions

```text
DriverSession: driver_id, city, status(online/busy/offline), last_location, product
RideRequest: request_id, rider_id, pickup, dropoff, product, state
Offer: offer_id, request_id, driver_id, expires_at
Trip: trip_id, driver_id, rider_id, state, timestamps, fare_ref
GeoCell: H3/S2 id → set of available driver_ids
```

**Trip / request state machine:**

```text
REQUESTED → MATCHING → OFFERED → ACCEPTED → ARRIVED → IN_TRIP → COMPLETED
                ↘         ↘ REJECTED/EXPIRED → MATCHING
                ↘ CANCELLED
```

### 3.3 Options: geo index

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. R-tree in one process | Simple | Not multi-AZ scale | Multi-city 100× |
| B. Redis GEO / sorted sets | Fast MVP | Shard pain; memory | 5M updates/s single Redis |
| C. H3/S2 cell → drivers map | Natural sharding | Cell boundary edge | Ignoring ring search |
| D. Quadtree service fleet | Flexible | Ops complexity | Overbuilding MVP |

**Chosen path:**

- **MVP:** H3 hex cells in Redis per city; ring search k=0..n.  
- **100×+:** sharded cell store by city / hex range; in-memory matchers per cell with durable trip store.

### 3.4 Options: matching

| Option | Pros | Cons |
|--------|------|------|
| Broadcast to all nearby | Simple | Driver spam; races |
| Sequential offer to best | Controlled | Slower match |
| Concurrent offers to top N | Faster | Need careful accept fencing |
| Batch auction window | Fairness | Latency |

**Chosen MVP:** Score top candidates; **sequential offer** with short TTL; on expire/reject, next. At high load hotspots, optional concurrent offers with CAS assign.

### 3.5 Matching score (multi-objective)

```text
score = w1 * pickup_eta
      + w2 * driver_fairness_penalty  # recently idle preferred
      + w3 * cancel_rate_penalty
      + w4 * product_match
      + w5 * heading_alignment
```

**Fairness:** track driver idle time / completion count in window; boost starved drivers; avoid always giving stadium exits to same cars.

**Deal-breaker:** Always nearest-only → some drivers never earn; riders at edges wait forever without radius expansion policy.

### 3.6 Dispatch & assignment invariants

**Invariant A:** A driver has at most one `ACCEPTED/IN_TRIP` assignment.  
**Invariant B:** A request has at most one accepted driver.  
**Invariant C:** Accept is compare-and-set on both driver and request rows/records.

```text
accept(offer):
  txn:
    if offer.expired: fail
    if request.state != OFFERED: fail
    if driver.state != OFFERED_TO_HIM: fail
    CAS request → ACCEPTED(driver)
    CAS driver → BUSY(trip)
```

### 3.7 ETA service

| Phase | Method |
|-------|--------|
| Pickup ETA | Route driver → pickup (cached / heuristic) |
| Trip ETA | Route pickup → dropoff with traffic |
| Quote fare | Distance/time × pricing |

**Deal-breaker:** Blocking match on slow external Maps call without timeout/fallback.

### 3.8 Location ingest plane

```text
Driver app → API Gateway → Location Ingest (validate, throttle)
   → city Kafka topic / Kinesis
   → Geo Updater workers → Cell index + last_loc cache
Match reads index; does not require synchronous write-through to OLTP
```

**Throttling:** max 1 Hz sustained; allow burst; drop/coalesce outdated points per driver (keep latest).

### 3.9 City / cell sharding

```text
city_id → home cell control plane
Within city: partition by H3 parent (coarse) for match workers
Driver updates routed by city from GPS
Rider request pinned to pickup city
```

**Cross-city:** rare; treat as special; don’t dual-own.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Location store | Cell index + latest KV | Match performance | All pings in Postgres |
| Matching | Sequential offer MVP | Simpler races | Fire-and-forget broadcast without fencing |
| Consistency | CAS trip/driver | No double assign | Best-effort memory map only |
| ETA | Cache + heuristic fallback | Latency | Sync Google call inline always |
| Scale | City cells | Natural boundaries | One global matcher |
| Fairness | Idle boost + radius policy | Marketplace health | Pure nearest forever |

---

## 4. Architecture Diagram

### 4.1 End-to-end rideshare

```text
 Rider App          Driver App
     |                   |
     v                   v
 +---------+       +-------------+
 | API GW  |       | Loc Gateway |
 +----+----+       +------+------+
      |                   |
      |                   v
      |            +--------------+
      |            | Loc Ingest   |--> Kafka --> Geo Index Updaters
      |            +--------------+              (per city shard)
      |
      +--> Ride Service <--> Trip Store (strong assign)
      |         |
      |         +--> Matcher Workers (per city/hex group)
      |         |         |
      |         |         +--> Geo Index (read)
      |         |         +--> Offer Service (TTL)
      |         |
      |         +--> ETA Service (cache + router)
      |         +--> Pricing / Surge
      |         +--> Payments Orchestrator → PSP
      |
      +--> Notification / Push
      +--> History / Receipts read models
```

### 4.2 Match sequence

```text
Rider         RideSvc          Matcher           GeoIndex        Driver
  |--request-->|                 |                  |              |
  |            |--match job----->|                  |              |
  |            |                 |--query rings---->|              |
  |            |                 |<-candidates------|              |
  |            |                 |--score/rank------|              |
  |            |                 |--create offer------------------>|
  |            |                 |                  |   accept/rej |
  |            |<-accepted-------|<--------------------------|
  |            |--CAS assign-----|                  |              |
  |<-driver----|                 |                  |              |
```

### 4.3 Double-accept race

```text
Driver A gets offer for Request R (also sequential—shouldn't dual)
Bad broadcast design:
  A and B accept R simultaneously
Correct:
  CAS on R: only first accept wins
  Loser gets "already matched"; driver returns to available
```

### 4.4 Hotspot stadium

```text
Hex H hot:
  match worker for H overloaded
Mitigations:
  - subsplit hex
  - queue requests fair
  - surge pricing signal
  - expand search rings carefully
  - cap concurrent offers per driver
```

### 4.5 Multi-city

```text
Global Directory: city → cell endpoints
Cell NYC: loc ingest + geo + match + trip store partition
Cell SF: ...
Payments / user identity: global with regional data residency care
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **At most one active assignment** per driver and per request.  
2. **Offer TTL server-authoritative.**  
3. **Trip durable** before charging and before “you’re matched” UX settles.  
4. **Location coalescing** never reorders to older point for a driver.  
5. **Cancel** releases supply via explicit state transition.  
6. **Payments** idempotent by `trip_id`.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Matcher crash | Request re-enters MATCHING; offers expire |
| Geo index loss | Rebuild from last_loc snapshot / re-ingest |
| Driver app kill | Heartbeat offline → remove from index |
| Partial CAS failure | Txn / saga with compensating release |
| Push notify drop | Polling fallback on apps |
| Kafka lag | Match uses slightly stale supply; widen freshness checks |

**Cancel vs rematch**

- Rider cancel in OFFERED/ACCEPTED: release driver; fee rules async.  
- Driver cancel: rider → MATCHING again; driver penalty counters for fairness.

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | One city; Redis GEO/H3; monolith RideSvc OK; Postgres trips |
| 10× | Location Kafka; match workers; ETA cache |
| 100× | Many cities; per-city cells; hex subshards; read models |
| 1000× | Regions; hierarchical H3; approximate kNN; aggressive coalesce |

**Location 5M/s techniques**

- Coalesce to 1 Hz per driver max.  
- Update index only on cell change OR every N seconds.  
- Shard Kafka by `city|hex_parent`.  
- Memory-optimized cell sets (roaring bitmaps / integer ids).

**Matching fairness at scale**

- Per-driver offer rate limits.  
- Idle-time boost.  
- Rider wait-time boost (aging).  
- Avoid locking a driver in offer ping-pong (max rejects → cooldown).

### 5.3 Maintainability

- Versioned offer protocol.  
- City config as data (radii, TTLs, weights).  
- Simulation harness: replay locations + requests.  
- Chaos: kill matcher, partition geo Redis, delay Kafka.  
- Clear ownership: Trip Store is source of truth for assignment; geo index is derived supply view.

### 5.4 Progressive scale deep dive

**1× — one city MVP**

```text
Ride API + Postgres
Redis: H3 cell → drivers; driver → last_loc
Matcher loop in service
Offer TTL 15s
ETA: haversine + avg speed; optional Maps
Push: FCM/APNs
```

**10×**

- Async location pipeline.  
- Separate matcher tier.  
- Surge calculator.  
- Connection pools / HA Redis.

**100×**

- City cells.  
- Hex-group matchers.  
- Trip store partitioned by city_date.  
- ETA tile cache.  
- Fraud signals basic.

**1000×**

```text
Regional super-cells containing many cities
Global user profile service
Local trip truth
Location sampling for non-matching consumers (ETA heatmaps)
Marketplace ML ranker service beside rules
```

### 5.5 Consistency model (be explicit)

| Data | Model |
|------|-------|
| Trip assignment | Strong (CAS/txn) |
| Driver location | Eventually consistent; freshness bound |
| ETA | Approximate |
| Fare quote vs final | Quote advisory; final computed at complete |
| History read model | Eventual from trip events |

**Why location can be eventual:** matching checks `last_seen_at`; stale drivers excluded. Wrong cell briefly → miss candidate, next loop finds—not double assign.

### 5.6 Matching fairness deep dive

**Rider fairness**

- Aging: longer wait → expand radius / boost priority.  
- Cap unmatched wait; communicate.  
- Don’t starve suburban rings when downtown demand high—policy capacity reserves optional.

**Driver fairness**

- Idle boost.  
- Limit consecutive snipes by same driver on rich hex via fairness penalty.  
- Transparent earnings zones (product).  

**Marketplace health metrics**

- Match rate, time-to-accept, cancel rate, driver utilization, rider wait p95.

### 5.7 ETA deep dive

```text
pickup_eta = route(driver, pickup) or heuristic
if traffic_model: adjust
confidence based on location freshness + GPS accuracy
UI: show range when uncertain
```

**Trip ETA updates:** recompute periodically IN_TRIP; push to rider.

### 5.8 Payments integration (bounded)

```text
ACCEPTED: optional auth hold
COMPLETED: capture final fare (idempotent key trip_id)
FAILED payment: retry + dunning; trip still COMPLETED_ARCHIVED
```

Do not design full ledger unless asked—mention idempotency.

### 5.9 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| GPS rows in OLTP at 5M/s | Melts DB |
| Broadcast offers without CAS | Double assign |
| Global single matcher | Hotspot + latency |
| Nearest-only forever | Unfair / brittle |
| Match blocked on Maps API | Outage = no rides |
| Active-active trip writers | Split-brain trips |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Product | Rideshare primary |
| Geo | H3/S2 cells, sharded by city |
| Location | Async ingest; coalesce |
| Match | Scored sequential offers + CAS assign |
| Consistency | Strong assignment; eventual locations |
| Scale | City/hex cells → regions |
| Fairness | Idle/wait aging + policies |

### 6.2 Top risks

1. Double dispatch under races  
2. Location plane lag → bad matches  
3. Hotspot hex meltdown  
4. Unfair marketplace dynamics  
5. Over-coupling to external Maps  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–3 | Choose rideshare; scope MVP |
| 3–10 | Actors, FSM, NFRs, scale table |
| 10–20 | HLD: loc + match + trip store |
| 20–30 | CAS assign, offers, fairness |
| 30–40 | ETA, hotspots, 10×/100×/1000× |
| 40–45 | Trade-offs; mention social alternate briefly |

---

## 7. Deeper / Related Interview Questions

### 7.1 Choice & scope

**Q: Why Uber over Facebook?**  
A: Geo + marketplace invariants are crisp; still covers sharding, consistency, realtime.

**Q: Can you do both?**  
A: Not in 45 minutes. Pick one; appendix the other.

### 7.2 Geo

**Q: H3 vs geohash vs S2?**  
A: All fine; hex neighbors cleaner for rings; pick one and know ring search.

**Q: Cell boundary problem?**  
A: Search k rings; duplicate edge drivers OK; dedupe by driver_id.

**Q: How large cells?**  
A: Trade index update churn vs candidate set size; often ~hundreds of meters in dense cities.

**Q: Earth distance?**  
A: Haversine for heuristic; routing for ETA when needed.

### 7.3 Matching

**Q: Batch auction vs sequential?**  
A: Auction can be fairer under contention; sequential simpler; hybrid at hotspot.

**Q: How many candidates?**  
A: Top 20–50 from rings; score; offer 1 (or N with fencing).

**Q: What if no drivers?**  
A: Expand radius, wait queue, suggest later, or fail—product choice.

**Q: Pool / shared rides?**  
A: Extra optimization (matching riders together)—defer; mention complexity.

### 7.4 Consistency & races

**Q: Exactly-once accept?**  
A: Idempotent accept API + CAS; duplicate accept returns same trip.

**Q: Driver offline during offer?**  
A: Heartbeat; offer fails; rematch.

**Q: Two data centers assign same trip?**  
A: Single home cell for city; no dual writers.

### 7.5 Location firehose

**Q: Update every 1s always?**  
A: Coalesce; send on movement threshold or 1–4s; more frequent when IN_TRIP for rider tracking.

**Q: Rebuild index after Redis loss?**  
A: Drivers republish; seed from last_loc durable snapshot if maintained.

**Q: Privacy?**  
A: Retain minimally; encrypt; access control for safety share.

### 7.6 ETA & maps

**Q: Build own router?**  
A: MVP use vendor; cache; long-term optional own graph for cost.

**Q: Inaccurate ETA?**  
A: Show uncertainty; learn bias; don’t overpromise.

### 7.7 Fairness & marketplace

**Q: Surge unethical?**  
A: Interview: explain as balancing supply; mention caps/comms; matching still needs fairness.

**Q: Driver starvation?**  
A: Idle boost; monitor utilization Gini-like metrics.

**Q: Rider always cancelled on?**  
A: Reputation; lower priority; fraud checks.

### 7.8 Payments & trust

**Q: When charge?**  
A: Capture at complete; auth earlier optional.

**Q: Dispute GPS path?**  
A: Retain trip path for X days; support tooling.

### 7.9 Scale

**Q: 5M location/s to one Redis?**  
A: Impossible—shard by city/hex; multiple clusters.

**Q: Global dashboard of all drivers?**  
A: Aggregates only; not raw global query.

**Q: Rebalance cities across cells?**  
A: Directory cutover with drain; fencing epoch.

### 7.10 Reliability drills

**Q: Matcher down 2 minutes?**  
A: Requests queue; SLOs miss; location still updates; recover rematch.

**Q: Half drivers GPS bad?**  
A: Accuracy filters; fallback map matching.

### 7.11 Security & safety

**Q: Fake GPS?**  
A: Heuristics, sensor fusion, fraud scores; not perfect MVP.

**Q: Share trip?**  
A: Tokenized link with TTL; limited location reveal.

### 7.12 Social comparison prompts

**Q: How would feed differ?**  
A: See Appendix—fanout-on-write vs read; celebrity; ranking.

**Q: Which is harder?**  
A: Depends—social read amplification vs rideshare realtime consistency.

### 7.13 Interview traps

| Trap | Pushback |
|------|----------|
| Design payments whole time | Stub PSP |
| Ignore double-assign | CAS story |
| Put GPS in SQL primary | Separate plane |
| Perfect global optimization | Heuristics + shards |
| No fairness talk | Marketplace dies |

### 7.14 Algorithms cheat-sheet

- H3 ring search `k`  
- Haversine  
- Token bucket for location  
- Min-heap / top-K score  
- CAS / optimistic locking  
- TTL offers via wheel / Redis key expiry + callback  

### 7.15 Say-aloud thesis

> City-sharded rideshare: async location → H3 geo index; matcher scores nearby supply with fairness; offers with TTL; strong CAS assignment in trip store; ETA cached with fallback; scale by city/hex cells so location firehose and match CPU never hit one box.

---

## 8. Appendices

### 8.1 API checklist (rideshare)

- [ ] `POST /rides` request  
- [ ] `POST /rides/{id}/cancel`  
- [ ] `POST /offers/{id}/accept`  
- [ ] `POST /offers/{id}/reject`  
- [ ] `POST /drivers/location`  
- [ ] `POST /drivers/status` online/offline  
- [ ] `GET /rides/{id}`  
- [ ] `GET /rides/{id}/eta`  
- [ ] `POST /trips/{id}/complete`  

### 8.2 Schema sketches

```sql
ride_requests(request_id, rider_id, city, pickup, dropoff, product, state, ...)
offers(offer_id, request_id, driver_id, expires_at, state)
trips(trip_id, request_id, driver_id, rider_id, state, fare_cents, ...)
drivers(driver_id, city, status, last_lat, last_lng, last_seen_at, ...)
-- geo index often Redis, not SQL
```

### 8.3 Redis geo layout

```text
cell:{city}:{h3}:avail → SET driver_id
driver:{id}:loc → {lat,lng,ts,h3,status}
offer:{id} → {request,driver,exp} EX TTL
```

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | FSM, Redis H3, CAS assign, basic ETA |
| 10× | Kafka locations, matcher workers, surge |
| 100× | City cells, hex shards, ETA cache |
| 1000× | Regions, hierarchical geo, ML ranker hooks |

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| H3/S2 | Hierarchical spatial index cells |
| Offer | Time-bounded proposal to a driver |
| CAS assign | Atomic claim of request+driver |
| Coalesce | Keep latest location, drop intermediates |
| Aging | Boost long-waiting riders/drivers |
| Home cell | Owning control plane for a city |

### 8.6 Interview “say this” summary (60 seconds)

> I’d design Uber-like rideshare: drivers stream GPS into a city-sharded H3 geo index; a matcher scores nearby drivers with ETA and fairness, sends TTL offers, and commits assignment with CAS so two riders never get the same driver. Locations are eventual and coalesced; trip state is strongly consistent. Scale out by city and hex shards; cache ETAs; handle hotspots with surge and subsharding.

### 8.7 Reliability test plan

1. Dual accept race → one winner.  
2. Matcher kill → rematch after TTL.  
3. Stale GPS → excluded.  
4. Stadium load → p99 match degrades gracefully.  
5. Payment webhook retry → single capture.  

### 8.8 Observability SLOs

| SLO | Example |
|-----|---------|
| Time to first offer | p95 < 5s (healthy supply) |
| Assign conflict rate | ~0 after CAS |
| Location freshness for matched drivers | < 10s |
| Kafka loc lag | < 2s p99 |
| Cancel after accept | monitored |

### 8.9 Fairness policy examples

```text
driver_score_idle = f(seconds_idle)  # higher better for matching?
Actually: lower pickup_eta better; add penalty = -alpha * seconds_idle
rider_aging: after 60s wait, expand ring k+=1
max_offers_per_driver_per_hour = Cap
```

### 8.10 Related systems map

```text
Driver loc → Ingest → Kafka → Geo Index
Rider request → RideSvc → Matcher → Offers → CAS Trip Store
                → ETA → Pricing → Payments
                → Push
```

### 8.11 Extra traps

| Trap | Pushback |
|------|----------|
| SQL GPS forever | Separate plane |
| No CAS | Double assign |
| Global matcher | Shard by city |
| Nearest-only | Fairness |
| Sync Maps always | Cache/fallback |
| 5M×100B=5MB/s | **500 MB/s** |

### 8.12 Capacity worksheet

```text
drivers_online * (1/update_period_s) = loc_qps
loc_qps * bytes = loc_bandwidth
matches_per_s * candidates_examined * cost = matcher_cpu
Ensure matcher_cpu sharded by #hex_groups
```

### 8.13 Offer state machine

```text
CREATED → SENT → ACCEPTED
                → REJECTED
                → EXPIRED
```

Server expires via TTL worker; client clock irrelevant.

### 8.14 — If Facebook instead (social feed appendix)

Use this if interviewer prefers social, or as contrast.

#### 8.14.1 Clarify (short)

| FR | Social MVP |
|----|------------|
| Post | Text/image to friends |
| Feed | Reverse chron or ranked home feed |
| Graph | Follow/friend edges |
| Like/comment | Engagement |
| Notify | Friend posts / likes |

NFR: read-heavy; p99 feed < 200–300ms; celebrity fanout.

#### 8.14.2 Estimation flash

```text
500M DAU baseline interview numbers (adjust as told)
Avg 50 feed reads/day → huge QPS
Fanout-on-write fails for celebrities (100M followers)
→ hybrid: fanout normal users; pull for celebs
```

#### 8.14.3 HLD sketch

```text
Client → API → Post Service → Kafka
                    → Fanout Workers → User Timeline Redis/Cassandra
Celeb posts → skip full fanout; mark in celeb index
Feed read: merge timeline + pull celeb + rank
Graph service: friends/follows
Media: object storage + CDN
Notification service async
```

#### 8.14.4 Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Fanout-on-write | Fast read | Celeb explosion |
| Fanout-on-read | Write cheap | Slow read merge |
| Hybrid | Practical | Complexity |

**Deal-breaker:** Fanout 100M writes synchronously on publish.

#### 8.14.5 Consistency

- Likes counters approximate OK.  
- “Remove post” eventual disappearance from caches.  
- Privacy checks on read path mandatory.

#### 8.14.6 Scale jumps

- **10×:** Shard timelines by user.  
- **100×:** Ranker service; multi-region read replicas.  
- **1000×:** Edge caches; interest graphs; heavy ML rank.

#### 8.14.7 60-second social summary

> Hybrid feed: write fanout for normal friend graphs into sharded timelines; celebrities pulled at read; ranker merges; media on CDN; notifications async—optimize the read path without melting on celebrity posts.

#### 8.14.8 When to pivot mid-interview

If interviewer says “actually do Facebook,” reuse: clarify → estimate → HLD → deep dive celebrity + ranking → wrap. Don’t finish Uber forcibly.

### 8.15 Rideshare vs social comparison table

| Dimension | Rideshare | Social |
|-----------|-----------|--------|
| Hot data | Locations + trips | Timelines + graph |
| Consistency | Strong assign | Mostly eventual |
| Hard QPS | Loc ingest | Feed reads |
| Hotspot | Stadium hex | Celebrity |
| Core algo | Geo match | Fanout/rank |

### 8.16 Sample match pseudocode

```text
function match(request):
  cells = rings(h3(pickup), k=0..K)
  cands = []
  for cell in cells:
    for d in geo.avail(cell):
      if fresh(d) and product_ok(d) and not busy(d):
        cands.append(d)
  rank = sort(cands, by=score)
  for d in rank:
    if create_offer(request, d, ttl=15s):
      return OFFERED
  return NO_SUPPLY  # or enqueue expand
```

### 8.17 Failure budget narrative

```text
If geo Redis shard down:
  fail matches in those hexes OR degraded wider heuristic
  page on-call; riders see delay

If payment PSP down:
  complete trip; queue capture; message rider later
```

### 8.18 Security checklist

- [ ] Auth per app role  
- [ ] Rate limit location / request spam  
- [ ] Encrypt location in transit  
- [ ] Minimize retention  
- [ ] Audit ops access to trip paths  

### 8.19 City launch checklist

- [ ] Cell deployed  
- [ ] Hex resolution tuned  
- [ ] Driver supply seeded  
- [ ] Pricing tables  
- [ ] SOS / support tooling  
- [ ] Load test stadium scenario  

### 8.20 Final contrast line for interview close

> If you had asked for Facebook, I’d hybrid-fanout feeds; for Uber, I shard geo and CAS-dispatch—both are marketplace+scale problems with different hot paths.

---

*End of social-or-rideshare platform system design.*
