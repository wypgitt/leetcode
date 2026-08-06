# System Design: Rider–Driver Matching

> **Focus areas:** Geospatial indexing (geohash/S2/H3) · Location freshness · Matching / dispatch · Marketplace state · WebSockets · Idempotency · Surge coupling · ETA  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar load classes (location pings vs match requests), explicit marketplace invariants, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — core of the ride marketplace: turn a rider request into an accepted driver assignment under freshness, fairness, and failure

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

Goal: **bound the product**—matching is *not* the whole Uber app. It is the subsystem that, given a ride request and a live set of available drivers, produces a durable assignment (or clear failure) with marketplace-correct state transitions.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Match rider request → driver offer → accept/reject → trip assigned | Full trip lifecycle (pickup→dropoff) deep dive (sibling) |
| Location | Fresh driver positions for dispatch | Long-term heat-map analytics (sibling) |
| Pricing | Consumes surge / quote; does not invent ledger | Full payments / merchant payouts |
| Map | Uses ETA/routing providers | Building Google Maps |
| Scope | Marketplace matching + dispatch protocol | Driver earnings ML research |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who initiates match? | Rider requests a ride (pickup + dropoff + product type) | `RideRequest` entity with quote binding |
| F2 | Driver eligibility? | Online, available, product-capable, geo-near, not banned | Filter pipeline before score |
| F3 | How far to search? | Expanding radius / ring; city-dependent caps | Geospatial index + tiered rings |
| F4 | Offer model? | Push offer to N drivers sequentially or small batch; timeout | Offer state machine + leases |
| F5 | Accept semantics? | First valid accept wins; others cancelled | CAS on request; fencing |
| F6 | Reject / ignore? | Reject frees driver; timeout → next candidate | Re-dispatch loop |
| F7 | Location updates? | Drivers ping every 1–4s while online | Hot location store ≠ OLTP |
| F8 | ETA? | Show ETA to rider; use in scoring | Routing service / cache |
| F9 | Product types? | UberX, Comfort, XL, etc. | Capability tags on drivers |
| F10 | Surge / pricing? | Quote frozen at request; surge zone may influence supply | Bind `quote_id`; don't reprice mid-offer silently |
| F11 | Cancel? | Rider cancel before accept; driver cancel after accept (with policy) | State transitions + penalties hooks |
| F12 | Observability? | Match latency, accept rate, cancel rate, empty-match | Funnel metrics by city/cell |

**MVP functional scope (lock with interviewer):**

1. Rider creates **ride request** with pickup, optional dropoff, product, `quote_id`, idempotency key.
2. System finds **nearby available drivers** via geospatial index.
3. Rank candidates (distance/ETA, rating floor, idle time, fairness hooks).
4. **Offer** to top candidate(s) with timeout; push via realtime channel.
5. Driver **accept/reject**; first accept → durable **assignment**; cancel other offers.
6. Rider sees status: searching → offered (optional) → matched → (hand off to trip service).
7. Driver location freshness gate (stale drivers excluded).
8. Basic city/cell isolation; metrics + structured logs.

**Out of MVP (explicitly defer):**

- Perfect global multi-hop batch matching (VRP) as default path
- Cross-city active-active dual writers on same request
- Full driver incentive optimization / earnings ML
- Airport queue / geofence specials (design hooks only)
- Exact road-network isochrones as sole index (approx first)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-first-offer? | Feels fast | p50 < 1s, p99 < 3–5s in-city (baseline) |
| N2 | Location freshness? | Dispatch on stale = bad UX / no-shows | Prefer ping age < 5–10s; hard exclude > 30–60s |
| N3 | Consistency of assignment? | No double-assign same request or driver | Strong CAS on request + driver lease |
| N4 | Availability? | City outage ≠ world outage | Cell/city isolation; degrade radius/product |
| N5 | Throughput? | See scale table | Split **ping QPS** vs **match QPS** |
| N6 | Geo accuracy? | Enough for dispatch rings | H3/S2 cell + haversine refine |
| N7 | Idempotency? | Double-tap request safe | `(rider_id, idempotency_key)` |
| N8 | Fairness? | Don't starve distant drivers forever | Rotating / idle-time boost in score |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Rider requests → candidates found → offer to D1 → accept → assignment → trip service notified.
2. D1 rejects → offer D2 → accept → assignment.
3. D1 timeout → offer D2 → accept.
4. No drivers in ring 1 → expand ring → match.
5. Rider cancels while searching → stop dispatch; cancel outstanding offers.
6. Surge: quote already includes surge; matching still runs; supply may be thin → longer search.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double request tap | Idempotency → same `request_id` |
| Two drivers accept same offer round | CAS: one wins; loser gets `ALREADY_MATCHED` |
| Driver accepts but went offline | Validate online+available at accept; else reject + re-dispatch |
| Stale location (GPS jump) | Freshness + max speed sanity; drop from index |
| Empty match (no supply) | Exhaust rings/time budget → `NO_DRIVERS`; suggest wait/retry |
| Hot downtown cell | Shard index; avoid single Redis key for city |
| Driver assigned elsewhere mid-offer | Driver lock / version check fails accept |
| Network partition to driver app | Offer timeout → next candidate |
| Clock skew on driver device | Server-side offer expiry; device clock not trusted |
| Quote expired | Fail request create; force re-quote |
| Pin in lake / unreachable | Validate map/snap; soft-fail UX |
| City New Year spike | Pre-scale cells; shed non-critical; widen match budget carefully |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Cities / cells | 50 | 500 | multi-region global | extreme global densification |
| Online drivers (peak) | 100K | 1M | 10M | 100M |
| Location pings / s | 50K | 500K | 5M | 50M |
| Ride requests / day | 5M | 50M | 500M | 5B |
| Peak match requests / s | ~200 | ~2K | ~20K | ~200K |
| Offers sent / s (peak) | ~500 | ~5K | ~50K | ~500K |
| Concurrent searching requests | 20K | 200K | 2M | 20M |
| Geo index cells touched / match | 7–20 | 7–20 | 7–30 | 7–40 |
| Avg candidates scored / match | 20–50 | 20–50 | 30–80 | 50–100 |

**What each jump forces:**

- **10×:** Sharded geo index by city/H3 parent; separate location plane from match OLTP; offer timeouts as first-class.
- **100×:** Match workers as fleets per cell; batch location writes; streaming fanout gateways; hotspot cells.
- **1,000×:** Hierarchical dispatch (local matcher → regional); approximate candidate retrieval; extreme ping aggregation; cell-level capacity admission.

### 1.5 Scope repeat-back

> Design rider–driver matching: durable ride requests, fresh geospatial driver supply, ranked offers with timeouts, exactly-one assignment via CAS/leases, realtime push to apps—starting at ~5M rides/day and scaling 10× / 100× / 1,000× with city/cell isolation. Not full trip completion or payments.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Driver location pings | 50K/s | 50M/s | Dominates; must be cheap path |
| Match / request create | 200/s | 200K/s | Durable write + dispatch kick |
| Geo queries (rings) | ~200–1K/s | ~200K–1M/s | Read-heavy on index |
| Offer push | 500/s | 500K/s | Realtime gateway |
| Accept/reject | ~300/s | ~300K/s | CAS hot path |
| Rider status poll/WS | 20K concurrent | 20M | Prefer WS/SSE over poll |

**Critical insight:** At scale, **location pings ≫ match QPS**. Never put pings through the same row-update path as assignment CAS.

### 2.2 Ping math

```text
Baseline: 100K online drivers × (1 ping / 2s) = 50K pings/s

Payload ~100–200 B → 50K × 150 B ≈ 7.5 MB/s (easy)

1,000×: 100M drivers × 0.5 ping/s = 50M pings/s
50M × 150 B ≈ 7.5 GB/s ingress cluster-wide → must be regional + sharded + batched
```

**Adaptive ping rate:** idle/far from demand → 4–10s; near high-demand / on offer → 1–2s. Cuts average QPS materially.

### 2.3 Match / offer math

```text
5M rides/day ÷ 86400 ≈ 58 requests/s average
Peak ~3–5× → ~200–300/s (baseline matches table)

Each request: 1–5 offers until accept (assume avg 2)
→ ~400–600 offer events/s peak baseline

Concurrent searching:
If median time-to-match = 15s at 200/s arrival:
200 × 15 = 3,000 — table 20K allows long-tail + empty search budgets
```

### 2.4 Geo index memory

```text
Per online driver in hot store:
driver_id, lat, lng, cell_id, ts, status, product_bits ≈ 64–128 B

100K × 128 B ≈ 12.8 MB (trivial)
10M × 128 B ≈ 1.28 GB (shard across nodes)
100M × 128 B ≈ 12.8 GB + index overhead → still fine if sharded by city/H3

Cell → set(driver_id):
Dense downtown H3 cell may hold thousands of drivers → don't put whole city in one key
```

### 2.5 Latency budget (request → first offer)

```text
API auth + validate quote     20–40ms
Write request (durable)       20–50ms
Geo candidates                10–40ms
Score + rank                  5–20ms
Create offer + push           20–80ms
------------------------------------
Target p50 < 1s with headroom
p99 dominated by overload / cold cells / routing ETA calls
```

**Deal-breaker for p99:** synchronous long road-ETA to 100 candidates on every match.

### 2.6 Bottlenecks (rank ordered)

1. **Ping write amplification** if treated as OLTP  
2. **Hot geo cells** (downtown / stadium)  
3. **Offer storms** (broadcast to too many drivers)  
4. **Double-accept races** under retries  
5. **Routing/ETA dependency** latency  
6. **City-wide monolith** key (one Redis for SF)

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
RideRequest  — rider intent + quote binding + state
DriverSupply — online drivers with fresh location + capabilities
CandidateSet — geo-retrieved + filtered drivers
Offer        — time-bounded proposal to a driver (lease)
Assignment   — durable match (request ↔ driver) — exactly one
```

**Request state machine (matching slice):**

```text
CREATED → SEARCHING → OFFERING → MATCHED
                 ↘ EXPIRED / CANCELLED / NO_DRIVERS
OFFERING → SEARCHING (reject/timeout, retry)
MATCHED → (trip service owns IN_TRIP …)
```

**Offer state machine:**

```text
PENDING → ACCEPTED | REJECTED | EXPIRED | CANCELLED
```

**Driver dispatch lock:**

```text
AVAILABLE → OFFERED → ASSIGNED
OFFERED → AVAILABLE (reject/expire)
```

### 3.2 Geospatial index options

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Geohash prefix | Simple, Redis-friendly | Polar distortion; prefix edge issues | Need precise equal-area cells globally |
| B. S2 cells | Equal-ish area, Google battle-tested | Learning curve | Team can't operate cell math |
| C. H3 hex | Uber-native, k-ring neighbors natural | Hex mental model | N/A for Uber interview—strong choice |
| D. PostGIS only | Rich queries | Won't survive ping QPS alone | Using PG as sole hot location store at 100× |

**Chosen path:**

- **Hot supply index:** H3 (or S2) cell → set of `driver_id`, updated on ping; store last lat/lng/ts in Redis/Memcached/in-memory shard.  
- **Refine:** haversine / cheap distance; optional ETA for top-K only.  
- **Cold / analytics:** stream pings to Kafka → heat map sibling system.

**Neighbor search:** H3 `kRing(cell, k)` expanding k=0..Kmax until enough candidates or budget exhausted.

### 3.3 Matching strategies

| Strategy | Pros | Cons | Use |
|----------|------|------|-----|
| 1-by-1 sequential offer | Simple, less driver spam | Higher TTM | MVP default |
| Small batch (N=2–3) | Faster fill | Multi-accept race care | Dense cities |
| Batch global match | Efficiency | Complexity, latency | 100× research / idle rebalance |
| Auction / bid | Market efficiency | UX + gaming | Usually out of MVP |

**MVP choice:** sequential or tiny batch with **short offer TTL** (5–15s), server-authoritative expiry.

### 3.4 Scoring (explainable)

```text
score = w1 * f(eta_or_distance)
      + w2 * idle_time_boost
      + w3 * rating_floor_gate (hard filter if below)
      + w4 * acceptance_likelihood (optional)
      - w5 * cancel_risk
      + fairness_noise/rotation
```

Hard filters before score: product, available, fresh ping, not offered elsewhere, geofence OK, docs OK.

**Deal-breaker:** only distance, forever → unfairness + ping-pong.

### 3.5 Assignment correctness

**Invariant:** A `RideRequest` has at most one `MATCHED` driver; a driver has at most one active assignment.

```text
Accept path:
1. Validate offer_id + not expired (server time)
2. CAS request: OFFERING → MATCHED if still OFFERING and offer matches
3. CAS driver: OFFERED → ASSIGNED if version matches
4. If either fails → compensate / re-dispatch
5. Outbox event: MatchCommitted
6. Cancel sibling offers async
```

Use **single-writer shard** keyed by `request_id` (and driver lock store keyed by `driver_id`).

### 3.6 Realtime delivery

| Channel | Role |
|---------|------|
| Driver WS/persistent connection | Offers, cancel, force-busy |
| Rider WS | Status: searching / matched / driver ETA |
| Push fallback (FCM/APNs) | Offline / WS dead |
| Polling | Degrade only |

**Ownership:** Match service mutates state; **Realtime Gateway** fans out. Don't embed WS in match monolith forever—split at 10×.

### 3.7 Location freshness plane

```text
Driver App → Location Ingest Gateway → 
  (1) update hot supply index (cell move = remesh)
  (2) append to log (Kafka) for analytics / recovery
```

**TTL:** index entries expire if no ping within T; sweeper removes ghosts.

### 3.8 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Ping store | Sharded in-memory / Redis | QPS + TTL | Update Postgres row per ping |
| Match truth | OLTP / strongly consistent store | Assignment integrity | Kafka-only "match topic" as SoR |
| Geo | H3 + k-ring | Natural expand | Linear scan all city drivers |
| Offers | Short TTL leases | Bound inconsistency | Infinite wait on one driver |
| ETA | Top-K only + cache | p99 | Sync ETA for 200 drivers |
| Multi-region | City home cell | Avoid dual assign | Active-active same request |

### 3.9 Coupling to siblings

| Sibling | Interaction |
|---------|-------------|
| Trip lifecycle | Consumes `MatchCommitted` |
| Surge / pricing | Quote before request; optional supply signal out |
| Notifications | Offer push / SMS fallback |
| Heat map | Reads ping stream; not on match critical path |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Rider App                         Driver App
      |                                  |
      | WS/HTTPS                         | WS + location pings
      v                                  v
+-----------+                     +------------------+
| API Gate  |                     | Location Ingest  |
+-----+-----+                     +--------+---------+
      |                                    |
      v                                    v
+----------------+                 +------------------+
| Ride Request   |                 | Hot Supply Index |
| Service        |                 | (H3/Redis shard) |
+--------+-------+                 +--------+---------+
         |                                  |
         v                                  |
+----------------+                          |
| Matching /     |<-------------------------+
| Dispatch Engine|   candidates
+--------+-------+
         |
         +--> Offer Manager (TTL, cancel)
         |
         +--> Assignment Store (CAS) --> Outbox --> Trip Service
         |
         v
+------------------+
| Realtime Gateway |---- offers/status ---> Apps
+------------------+

Kafka/Pulsar: location events, match events (async analytics, not SoR for assign)
```

### 4.2 Sequence: happy match

```text
Rider          RequestSvc       Matcher          Supply         Driver
  |--create-->    |               |                |              |
  |<-req_id--     |--SEARCHING--> |                |              |
  |               |               |--kRing+get---> |              |
  |               |               |<-candidates----|              |
  |               |               |--score/rank--->|              |
  |               |               |--Offer(D1)-------------------->|
  |               |               |                |              |
  |               |               |<-------------Accept(D1)-------|
  |               |               |--CAS MATCHED-->|              |
  |<-matched----- |<--event-------|                |              |
```

### 4.3 Sequence: double accept race

```text
Driver A                Assignment Store              Driver B
  |--Accept offer1----->|                               |
  |                     | CAS OK → MATCHED              |
  |<-OK-----------------|                               |
  |                     |<--Accept offer1 (stale)-------|
  |                     | CAS FAIL                      |
  |                     |-- 409 ALREADY_MATCHED ------->|
```

### 4.4 Sequence: stale driver excluded

```text
Matcher -> Supply.get(cell)
Supply filters: now - ping_ts <= freshness_threshold
Ghost drivers with expired TTL already removed by sweeper
```

### 4.5 City / cell topology

```text
Global Edge / Gateways (active-active)
        |
        v
City Cell (home for requests in city_id)
  - Request + Assignment DB shard
  - Match workers
  - Supply index shards by H3 parent
        |
        +--> fail independently from other cities
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Idempotent request create** on `(rider_id, idempotency_key)`.  
2. **At most one MATCHED** driver per request (CAS).  
3. **At most one active assignment** per driver (driver version / lock).  
4. **Offer expiry is server-side**; client clock irrelevant.  
5. **Stale accept rejected** after expire or cancel.  
6. **Location freshness** enforced at candidate selection *and* accept.  
7. **Outbox** for `MatchCommitted` so trip service eventually sees commit.  
8. **Cancel searching** stops new offers; best-effort cancel in-flight.  
9. **Ping path failure** must not block accept CAS path (separate planes).  
10. **Fencing:** offer_id UUID; accept must present it.

### 5.2 Scalability

| Scale | Architecture moves |
|-------|--------------------|
| 1× | Modular services; Redis H3 index per city; PG requests; sequential offers |
| 10× | Shard supply by H3 parent; match worker pool; WS gateway split; Kafka pings |
| 100× | Hotspot cell splitting; batch ping writes; ETA cache; tiny-batch offers in dense zones |
| 1000× | Hierarchical local matchers; ping aggregation; admission control per cell; approximate retrieval |

### 5.3 Maintainability

- Matching **policy as config** (weights, ring sizes, TTLs) per city.  
- **Shadow scoring**: log top-K alternate ranks without changing prod.  
- Contract tests for state machine transitions.  
- Chaos: kill match worker mid-offer; verify timeout path.  
- Clear SEV ownership: matching vs trip vs location ingest.

### 5.4 Progressive scale playbook

**Baseline:** One cell per major city; Redis sets per H3 res-8/9; offer TTL 10s; freshness 15s.

**10×:**  
- Ping pipeline: UDP/HTTP → ingest → Redis pipeline MSET + cell SADD/SREM.  
- Request store sharded by `city_id`.  
- Realtime gateway c4k connections per node.

**100×:**  
- Stadium mode: temporary micro-cells, longer rings, batch offers N=3.  
- Candidate service caches cell membership.  
- Match engine becomes actor-per-request or partition consumer.

**1,000×:**  
- Don't globally optimize every request; **local greedy** with periodic rebalancing.  
- Drivers stream deltas; index stores coarse cell + precise lat only on query refine.  
- Multi-layer: edge eligibility → regional matcher → city assignment store.

### 5.5 Geospatial deep dive

**H3 resolution choice:**

| Res | Edge length (approx) | Use |
|-----|----------------------|-----|
| 7 | ~1.2 km | Coarse rings / sparse suburbs |
| 8 | ~460 m | Default city dispatch |
| 9 | ~174 m | Dense downtown |
| 10 | ~66 m | Too fine for membership churn |

**Cell churn:** on ping, if `h3(new) != h3(old)`, SREM old / SADD new. High churn at boundaries → sticky hysteresis (only move if >X meters into new cell).

**Edge of hex:** always k-ring ≥1 when rider near boundary; refine by distance.

### 5.6 Empty match & search budget

```text
deadline = now + search_budget (e.g. 30–120s)
while now < deadline and state=SEARCHING:
  candidates = expand_rings()
  if candidates: offer loop
  else: sleep/backoff, widen product?, signal surge
→ NO_DRIVERS
```

Don't busy-spin; exponential backoff on empty rings to save CPU.

### 5.7 Surge interaction

- Matching **does not invent price**.  
- Thin supply → longer TTM → product may raise surge on *next* quote.  
- Optional: matching emits `supply_demand_signals` async to pricing.

### 5.8 Idempotency & retries

| Operation | Key |
|-----------|-----|
| Create request | `Idempotency-Key` |
| Accept | `offer_id` + driver auth (accept is CAS) |
| Cancel | `request_id` + rider auth; cancel is idempotent terminal |

### 5.9 Failure modes & degradations

| Failure | Degrade |
|---------|---------|
| ETA service down | Score by haversine; show approximate ETA |
| Redis shard loss | Rebuild from recent Kafka pings; brief empty match↑ |
| Match worker down | Another worker continues via request partition |
| WS down | Push notify; driver opens app |
| PG primary failover | Brief elevate TTM; no dual-assign if fenced |

### 5.10 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Ping → Postgres | Melts; stale under load |
| Broadcast offer to 50 drivers | Spam + multi-accept chaos |
| No offer TTL | Stuck requests |
| Active-active dual assign writers | Double dispatch SEV |
| Match truth in Kafka only | Hard CAS; murky ownership |
| Ignore freshness | Pickup ghosts / no-shows |
| Sync 100 ETAs | p99 death |

---

## 6. Wrap-Up

### 6.1 Designed

Rider–driver matching with durable requests, H3 supply index, freshness gates, ranked time-bounded offers, CAS assignment, realtime fanout, city/cell scale path.

### 6.2 Decisions to defend

1. Split **location plane** vs **assignment plane**  
2. **H3 k-ring** retrieval + distance refine  
3. **Short offer leases** + server expiry  
4. **CAS** for exactly-one match  
5. Sequential / tiny-batch offers (not city-wide spam)  
6. **Idempotent** request create  
7. ETA only on top-K  
8. City **home cell** single-writer for request state  

### 6.3 Risks

- Hotspot cells (events)  
- GPS spoofing / jumps  
- Fairness vs efficiency tension  
- Dependency on routing  
- Offer timeout tuning (too short → spam; too long → TTM)

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope matching vs full Uber; invariants |
| 5–12 | Estimates: pings vs matches |
| 12–25 | HLD: index, offer, CAS |
| 25–35 | Freshness, races, WS |
| 35–45 | Scale 10×/100×/1000×, deal-breakers |

### 6.5 Closer

> **Rider–driver matching**: fresh geospatial supply, time-bounded offers, exactly-one CAS assignment, pings off the critical OLTP path, city cells, progressive scale without dual-writers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Geospatial

**Q: Geohash vs H3 vs S2?**  
A: All fine if you can expand neighbors. H3 k-rings are ergonomic; S2 common; geohash needs careful 8-neighbor. Pick one and discuss boundary.

**Q: Why not "SELECT * FROM drivers WHERE distance < 5km"?**  
A: At ping QPS and online cardinality, you need an index of presence by cell, not repeated full scans.

**Q: How to handle hex boundary?**  
A: Always include k-ring; refine by true distance; optional hysteresis on cell membership.

**Q: What resolution?**  
A: City-dependent; denser → finer. Start res 8–9; measure candidate set size.

### 7.2 Location freshness

**Q: What if ping delay is 20s?**  
A: Exclude from dispatch; optionally still show coarse presence for heat maps.

**Q: Adaptive ping rate?**  
A: Yes—battery + cost. Higher rate when offered / moving / in surge zones.

**Q: GPS spoofing?**  
A: Max speed checks, sensor fusion signals, fraud scores—hard filter if extreme.

### 7.3 Matching algorithms

**Q: Stable marriage / Hungarian?**  
A: Beautiful theory; often too slow/global for interactive dispatch. Use local greedy + periodic batch rebalance.

**Q: Should we optimize total wait or individual?**  
A: Product choice; state trade-off. Marketplace often minimizes rider ETA with fairness constraints.

**Q: Batch matching every 2s?**  
A: Helps efficiency in dense cities; adds latency. Hybrid: interactive offer + background optimize.

### 7.4 Consistency & races

**Q: Two accepts same millisecond?**  
A: CAS on request row/partition; one wins; loser 409.

**Q: Driver matched on two requests?**  
A: Driver lock version; second assign fails; repair.

**Q: Exactly-once match event?**  
A: Outbox + consumer idempotency on `assignment_id`.

### 7.5 Realtime

**Q: WebSocket vs poll?**  
A: WS/SSE for offers; poll as degrade. Sticky sessions or connection registry `driver_id → gateway_node`.

**Q: Offer delivered twice?**  
A: Idempotent offer_id; UI dedupe; accept once.

### 7.6 Queues & streams

**Q: Kafka for matching loop?**  
A: Good for pings/events; awkward as sole offer state machine. Prefer request actor / DB state + stream notifications.

**Q: Partition key?**  
A: Pings by `city|h3_parent`; match events by `request_id` or `city_id`.

### 7.7 Caching

**Q: Cache ETAs?**  
A: Yes for popular OD pairs / road segments; short TTL; never cache assignment.

**Q: Cache candidate lists?**  
A: Very short TTL (1–2s) in dense cells to absorb storms—risk of slight staleness.

### 7.8 Multi-region / geo

**Q: Rider in city A, data in city B?**  
A: Route request to **city home cell** by pickup geofence.

**Q: DR failover?**  
A: Fence epoch; in-flight offers expire; rebuild supply from pings.

### 7.9 Marketplace product

**Q: Airport queues?**  
A: Separate FIFO / lot logic; don't use naive distance from terminal pin.

**Q: Shared rides / pool?**  
A: Different matcher (insert into routes); out of MVP but mention hook.

**Q: Preferred driver?**  
A: Soft boost if nearby; don't wait forever.

### 7.10 Algorithms & data structures

**Q: Structure for cell → drivers?**  
A: Redis SET or sharded in-memory hashset; secondary hash `driver → metadata`.

**Q: Priority among candidates?**  
A: Heap / partial sort top-K; no need full sort of city.

**Q: Bloom filter use?**  
A: Optional negative cache for "no drivers in coarse cell" with short TTL.

### 7.11 Reliability drills

**Q: Kill Redis shard?**  
A: Fail matches in that geo slice; rebuild from stream; alert.

**Q: Offer timeout storm after outage?**  
A: Jitter re-dispatch; cap concurrent offers per city.

### 7.12 Interview traps

| Trap | Pushback |
|------|----------|
| One global Redis list of all drivers | Hot key death |
| "Kafka exactly-once matching" | Assignment needs CAS |
| Ignore ping vs match QPS split | Failed estimate |
| Broadcast to all drivers in city | Spam + races |
| Microservices per driver | Absurd |
| Perfect global optimum each request | Latency / complexity lie |

### 7.13 Metrics

| Metric | Why |
|--------|-----|
| Time-to-first-offer | UX |
| Time-to-match | UX |
| Accept rate | Offer quality |
| Empty-match rate | Supply |
| Ping age at match | Freshness |
| Double-assign incidents | Correctness (must be ~0) |
| Offer cancel latency | Cleanup |
| Hot cell match p99 | Scale |

### 7.14 Comparison

**Q: vs food delivery dispatch?**  
A: Similar geo+offer; more multi-order batching / merchant prep constraints.

**Q: vs dating "match"?**  
A: Different—no realtime geo supply leases.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- ride_requests
(request_id UUID PK,
 rider_id UUID,
 city_id TEXT,
 pickup_lat, pickup_lng, pickup_h3,
 dropoff_lat, dropoff_lng,
 product_type TEXT,
 quote_id UUID,
 state TEXT,
 matched_driver_id UUID NULL,
 idempotency_key TEXT,
 search_deadline TIMESTAMPTZ,
 created_at, updated_at,
 UNIQUE(rider_id, idempotency_key))

-- offers
(offer_id UUID PK,
 request_id UUID,
 driver_id UUID,
 seq INT,
 state TEXT,
 expires_at TIMESTAMPTZ,
 created_at)

-- assignments
(assignment_id UUID PK,
 request_id UUID UNIQUE,
 driver_id UUID,
 offered_at, matched_at)

-- drivers_hot (Redis hash; not PG at scale)
-- driver_id → {lat,lng,h3,ts,status,products,version}
```

### 8.2 API checklist

- [ ] `POST /v1/ride-requests` + Idempotency-Key  
- [ ] `POST /v1/ride-requests/{id}/cancel`  
- [ ] `GET /v1/ride-requests/{id}`  
- [ ] Driver: `POST /v1/offers/{id}/accept`  
- [ ] Driver: `POST /v1/offers/{id}/reject`  
- [ ] Driver: `POST /v1/locations` (ping; or binary UDP)  
- [ ] WS: rider `/ws/ride/{id}`; driver `/ws/driver`  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| H3 k-ring | Hex neighborhood around a cell |
| Offer lease | Time-bounded exclusive proposal |
| Freshness | Max age of location ping for eligibility |
| Home cell | Single-writer city/region for request state |
| Supply index | Hot structure of online drivers by cell |
| CAS | Compare-and-set for state transitions |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | H3 index, offer TTL, CAS match, idempotent create |
| 10× | Sharded supply, WS gateway, Kafka pings |
| 100× | Hotspot mode, ETA cache, match fleets |
| 1000× | Hierarchical dispatch, ping aggregation, cell admission |

### 8.5 Scoring sketch

```text
hard_filter(d):
  online and available and product_ok and ping_age < T and not locked

soft_score(d):
  0.55 * inv_eta(d) + 0.20 * idle_boost(d) + 0.15 * rating + 0.10 * fairness
```

### 8.6 Offer timing

```text
offer_ttl_ms = 8000  # dense
offer_ttl_ms = 12000 # sparse
max_offers = 10
search_budget_ms = 60000
```

### 8.7 Location ping message

```json
{
  "driver_id": "d_...",
  "lat": 37.77,
  "lng": -122.41,
  "ts_device": 1730000000123,
  "heading": 90,
  "speed_mps": 4.2,
  "status": "AVAILABLE",
  "products": ["uberx"]
}
```

Server stamps `ts_server`; uses that for freshness.

### 8.8 Interview “say this” (60 seconds)

> Matching is a marketplace state machine on top of a **hot geospatial supply index**. Pings are a separate high-QPS plane. We retrieve drivers by H3 rings, filter on freshness, score a small set, send **short-TTL offers**, and commit **exactly one assignment** with CAS. Cities are cells; we scale by sharding supply and matchers—not by putting pings in Postgres.

### 8.9 Reliability test plan

1. Double accept → one MATCHED.  
2. Driver kill mid-offer → timeout → next driver.  
3. Stale ping > threshold → excluded.  
4. Idempotent re-create request.  
5. Redis cell shard loss → rebuild from Kafka; elevated empty-match.  
6. Clock skew on device → server expiry still works.

### 8.10 Related systems map

```text
Quote/Surge → Ride Request → Matcher ← Hot Supply (H3)
                               ↓
                            Offers → Realtime Gateway → Apps
                               ↓
                         Assignment → Trip Lifecycle
                               ↓
                         Events → Analytics / Heat map
```

### 8.11 Extra traps

| Trap | Pushback |
|------|----------|
| PG per ping | QPS melt |
| No freshness | Ghost drivers |
| Global optimal solver always | Miss TTM SLO |
| Dual region writers | Double assign |
| 5M rides/day ⇒ 5M QPS | Confuse day vs second |

### 8.12 Unit check reminders

```text
5M rides/day ÷ 86400 ≈ 58/s avg, not 5M/s
100K drivers × 1 ping/2s = 50K/s, not 100K/s
```

---

*End of rider–driver matching system design.*
