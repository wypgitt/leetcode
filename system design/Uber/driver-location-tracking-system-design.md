# System Design: Driver Location Tracking

> **Focus areas:** High-frequency GPS ingest · Geospatial indexing · Freshness SLAs · Fan-out to matching/ETA · Hot partitions · Offline detection · Privacy  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit freshness invariants, resolved ownership of “current location,” honest MVP vs city-scale paths  
> **Interview theme:** Uber — **real-time driver positions** that power matching, ETAs, heat maps, and rider maps

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

Goal: design the system that **ingests driver GPS pings**, maintains a **fresh, queryable location state**, and serves consumers (matching, ETA, rider map, analytics) under city and global scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Location ingest + current-state + geo queries | Full rider–driver matching algorithm |
| Truth | Latest accepted ping per driver (with quality filters) | Perfect ground-truth GPS physics |
| History | Short hot trail + optional cold archive | Full trip reconstruction product (hooks only) |
| Uber lens | Freshness, geo locality, cost of ping storm | Academic GIS textbook |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who sends locations? | Driver app (foreground/background) + occasional device SDKs | Mobile → ingest edge; batching on client |
| F2 | Ping rate? | ~1/s when online/en-route; lower when idle | Adaptive sampling; server rate limits |
| F3 | Payload? | lat, lng, heading, speed, accuracy, ts, trip_id?, battery | Cap size; drop bad accuracy |
| F4 | Consumers? | Matching, ETA, rider live map, heat map, safety | Split hot path vs analytics path |
| F5 | Queries? | Get driver; nearby drivers in radius/hex; bbox for map | Geo index + city/cell sharding |
| F6 | Offline? | No ping within T → offline / not matchable | Heartbeat/TTL on presence |
| F7 | History? | Last N minutes for map trail; longer for forensics | Hot ring buffer + cold store |
| F8 | Privacy? | Precise location only for active trip parties; retention limits | ACL + TTL + fuzz for idle |
| F9 | Ordering? | Late/out-of-order pings common | Event-time vs processing-time; drop stale |
| F10 | Multi-city? | Global; drivers rarely cross cities mid-session | Shard by city/geohash cell |
| F11 | Idempotency? | Retries from flaky mobile networks | `(driver_id, client_seq)` or `(driver_id, device_ts)` |
| F12 | Admin? | Force offline, inspect last ping, replay | Control plane + audit |

**MVP functional scope (lock with interviewer):**

1. Ingest location updates from online drivers with auth + rate limits.  
2. Maintain **current location** per driver with freshness TTL.  
3. Query: `getLocation(driverId)`, `nearby(lat,lng,radius,filters)`.  
4. Publish location change stream for matching/ETA (async).  
5. Mark driver offline on TTL expiry; optional short trail for active trips.  
6. Basic observability: ingest lag, freshness p99, geo-query latency.

**Out of MVP (explicitly defer):**

- Perfect map-matching to road graph for every ping  
- Cross-region active-active writes for the same driver  
- Full historical trip replay UI  
- ML-based spoofing detection beyond simple heuristics  
- Sub-meter indoor positioning

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest ack latency? | Fast enough not to drain battery with retries | p99 < 100–200ms edge→ack |
| N2 | Freshness for matching? | Stale drivers hurt marketplace | p99 age of used location < 3–5s online |
| N3 | Nearby query latency? | Matching critical path | p99 < 20–50ms in-region |
| N4 | Durability of current state? | Lose last few seconds OK; lose all presence bad | Hot store HA; rebuild from stream if needed |
| N5 | Availability? | City outage ≠ global outage | Cell isolation by city/region |
| N6 | Ordering? | Prefer freshest event-time | Drop ping if `device_ts` older than stored |
| N7 | Cost? | Ping volume dominates | Adaptive sampling + regional edge |
| N8 | Privacy / compliance? | GDPR/CCPA retention | TTL policies; purpose limitation |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Driver goes online → pings every 1–4s → current state updated → appears in nearby for matching.  
2. Rider on trip watches driver approach → map polls/subscribes → trail of last ~30–60s.  
3. Driver goes offline / app killed → TTL expires → removed from matchable set.  
4. Driver completes trip → still online → continues pings; trip_id cleared.  
5. Matching service asks nearby hex cells → filters by status/vehicle → returns candidates.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Out-of-order ping (old ts) | Reject if older than current; metric++ |
| GPS jump / teleport | Sanity filter (max speed); quarantine or snap |
| Spoofed location | Auth + anomaly heuristics; safety review hook |
| Hot downtown cell | Shard geo index; avoid single Redis key |
| Driver tunnels (no GPS) | Hold last + decay freshness; don’t fake movement |
| Clock skew on phone | Prefer server receive time for TTL; use device_ts for ordering with clamp |
| Duplicate retries | Idempotent upsert by seq/ts |
| Matching reads during failover | Serve slightly stale replica; never empty-all-cities |
| Privacy: idle driver | Coarser geo for analytics; precise only when needed |
| Burst reconnect after outage | Backpressure + jittered client retry |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 metro) | 10× | 100× | 1,000× |
|--------|-------------------|-----|------|--------|
| Online drivers (peak) | 50K | 500K | 5M | 50M |
| Ping rate (avg online) | 1/s | 0.5–1/s | adaptive | adaptive |
| Peak ingest QPS | 50K | 500K | 2–5M | 10–20M |
| Nearby queries QPS | 5K | 50K | 500K | 5M |
| Get-by-id QPS | 20K | 200K | 2M | 20M |
| Cities / cells | 1 | 20 | 200 | 2,000+ |
| Hot trail retention | 2 min | 5 min | 5 min | 5 min hot |
| Cold archive | optional | 7–30d | 30–90d sampled | sampled + legal hold |

**What each jump forces:**

- **10×:** Shard by geohash/city; separate ingest from query; Kafka (or equivalent) fan-out.  
- **100×:** Regional cells; adaptive client sampling; memory-first current-state; analytics off hot path.  
- **1,000×:** Hierarchical geo indexes, edge ingest PoPs, presence gossip/aggregation, strict cost controls on ping rate.

### 1.5 Etc. (Constraints & Assumptions)

- Drivers are **mobile clients** with flaky networks; expect retries and gaps.  
- **Matching owns offer logic**; this system owns location truth + geo retrieval.  
- Single primary cloud per region; multi-AZ; **driver home region** by city.  
- Location is PII/sensitive → encrypt in transit; access-controlled at rest.  
- “Real-time” means **seconds**, not milliseconds of exchange co-lo.

**Scope statement:**

> Design a globally sharded driver-location service that ingests high-frequency GPS pings, maintains freshness-bounded current positions, answers nearby/get queries for marketplace consumers, and evolves from one metro (~50K online drivers) through 10× / 100× / 1,000× with geo cells, adaptive sampling, and split hot/analytics planes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Ingest math

```text
Baseline: 50K online × 1 ping/s = 50K QPS
Payload ~150–250 B JSON (or ~80–120 B binary) → use 200 B

Ingress: 50K × 200 B = 10 MB/s ≈ 860 GB/day raw pings (one city)

10×: 500K QPS → 100 MB/s
100× with adaptive 0.5/s avg: 5M drivers × 0.5 = 2.5M QPS → 500 MB/s
1000× adaptive 0.3/s: 50M × 0.3 = 15M QPS → 3 GB/s  → needs edge + sampling
```

**Critical insight:** At global scale you **cannot** store or fan-out every raw ping to every consumer. Current-state upsert + selective stream topics + downsampled archives.

### 2.2 Storage (current state)

```text
Per driver hot record ~200–400 B (id, lat, lng, heading, speed, ts, status, version)
50K → ~20 MB
5M → ~2 GB
50M → ~20 GB  (fits memory if sharded; still shard for locality & blast radius)
```

### 2.3 Geo index memory

```text
Geohash precision ~7–8 (~150m–40m) or H3 res 8–9
Inverted index: cell → set(driver_id)
50K drivers × ~16–32 B overhead ≈ few MB
Plus secondary indexes by status/vehicle
```

### 2.4 Query fan-out

```text
Nearby radius 1–3 km → O(10–100) cells typically
Each cell set lookup + filter → target < 50ms including network inside cell
Matching may issue hundreds of nearby/s per city at peak
```

### 2.5 Bandwidth to consumers

```text
If every ping broadcast to 5 consumer groups: 5× ingest — too expensive
Prefer: (a) current-state pull, (b) compact deltas on trip channels, (c) sampled city streams
```

### 2.6 Bottlenecks (ranked)

1. **Ingest storm** in dense cities (NYC/SF Friday night)  
2. **Hot geo cells** (airport, stadium)  
3. **Fan-out cost** if naive pub/sub of all pings  
4. **Stale reads** after partition / client background limits  
5. **Clock/order** bugs causing “teleport” UX  
6. **Retention cost** if keeping full history forever  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Ping            → validated location event from a driver device
DriverPresence  → online/offline + last_seen + matchable flag
CurrentLocation → latest accepted ping fields + version/fencing
GeoCell         → geohash / H3 index bucket containing driver ids
LocationStream  → durable log of accepted updates (for rebuild + consumers)
```

### 3.2 Options: where is current state?

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Postgres rows | Simple | Write QPS melts at 50K+/s | City peak ingest |
| B. Redis / Memcached cluster | Fast upsert + TTL | Must design durability/rebuild | No rebuild path + data loss amnesia |
| C. Cassandra / Scylla | High write throughput | Geo queries awkward alone | Nearby without secondary geo index |
| D. Hybrid: Redis current + Kafka log + geo index shards | Scales; rebuildable | Ops complexity | Team cannot operate shards |

**Chosen path:**

- **MVP:** Redis (or similar) for `driver→location` + `cell→drivers`; Kafka for async consumers; Postgres optional for sparse durable snapshots.  
- **100×+:** **Regional location cells** owning shards of geo space; edge ingest; memory-first presence; Kafka (or Pulsar) as rebuild + analytics source.

### 3.3 Write path (ingest)

```text
1. Driver app batches 1–N pings → TLS → Ingest Edge (city/region PoP)
2. Authn (driver token), authz, schema validate, rate limit
3. Quality filters: accuracy, max speed, bounding box for city
4. Order check: accept if device_ts >= current.ts (or seq > current.seq)
5. Upsert CurrentLocation; refresh TTL; update GeoCell membership if cell changed
6. Append to LocationStream (async, batched)
7. ACK client (do not block ACK on all consumers)
```

**Invariant:** A driver has **at most one** current location record per region; cell indexes are eventually consistent with that record within tens of ms.

### 3.4 Read path (nearby)

```text
1. Convert (lat,lng,radius) → set of cells (k-ring / geohash neighbors)
2. Scatter to shard owners for those cells (usually same city cell)
3. Union driver ids → batch get locations → filter status, freshness, vehicle
4. Rank/truncate (distance) → return
```

**Deal-breaker:** Global scan of all drivers; or single Redis `KEYS` / unbounded sets without sharding.

### 3.5 Freshness & offline

| Mechanism | Role |
|-----------|------|
| Client ping interval | Produces heartbeats |
| Server TTL on presence | Offline if silent |
| Matching freshness gate | Ignore drivers with age > threshold |
| Explicit offline API | Fast removal on driver toggle |

```text
presence_ttl = max(3 × expected_ping_interval, 10s)  // tune per status
matchable   = online AND accuracy_ok AND age < match_sla
```

### 3.6 Geo index choice

| Index | Use when |
|-------|----------|
| Geohash | Simple, good MVP |
| H3 | Stable hex neighbors; Uber-familiar |
| S2 | Google-style spherical cells |
| R-tree in one process | Single-box MVP only |

**MVP:** H3 or geohash length 7–8; store drivers in cell sets; on move, `SREM` old / `SADD` new.

### 3.7 Stream vs pull consumers

| Consumer | Pattern |
|----------|---------|
| Matching | Pull nearby on demand + small cache; optional dirty notifications per cell |
| Rider map (on trip) | Subscribe to `trip_id` channel / narrow driver stream |
| ETA | Pull + route service; not every ping |
| Heat map / analytics | Sampled stream → Flink/Spark | 

**Deal-breaker:** Pushing every city ping to every rider app.

### 3.8 Sharding & multi-region

```text
driver_id → city_id (from last known / session) → region cell
geo queries always scoped to city/region (product constraint)
cross-city: rare; migrate presence record with fencing epoch
```

| Plane | Mode |
|-------|------|
| Ingest | Regional / edge |
| Current state writes | Single-writer shard for driver |
| Nearby | Local to city cell |
| Analytics | Async multi-region lake |

### 3.9 API sketch

```text
POST /v1/drivers/{id}/locations
  body: {lat, lng, heading, speed, accuracy, device_ts, seq, trip_id?}
  → 202/204

GET  /v1/drivers/{id}/location
  → {lat, lng, ts, age_ms, status}

POST /v1/locations/nearby
  body: {lat, lng, radius_m, filters..., limit}
  → {drivers: [...]}

POST /v1/drivers/{id}/offline
```

### 3.10 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Memory current-state | Speed vs must rebuild from log |
| Drop stale pings | Correctness vs “smooth” UI interpolation (client can interpolate) |
| Adaptive sampling | Cost/battery vs freshness |
| Cell notifications | Faster matching vs stream load |
| Strongly ordered per driver | Needs single-writer shard |

---

## 4. Architecture Diagram

```text
                     +----------------------+
                     |   Driver Mobile App  |
                     |  (adaptive sampling) |
                     +----------+-----------+
                                | HTTPS / HTTP3
                                v
                     +----------------------+
                     |   Edge / Ingest GW   |
                     | auth, RL, validate   |
                     +----------+-----------+
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
        +----------------+            +------------------+
        | Location Shard |            |  Kafka / Log     |
        | CurrentLocation|            | location.accepted|
        | GeoCell index  |            +--------+---------+
        | Presence TTL   |                     |
        +--------+-------+                     |
                 |                             |
       +---------+---------+                   |
       |                   |                   v
       v                   v          +------------------+
 +-----------+      +------------+    | Stream processors|
 | Matching  |      | ETA / Maps|    | heat, archive,  |
 | (nearby)  |      | (get/sub)  |    | anomaly, heatmap |
 +-----------+      +------------+    +------------------+

City/Region Cell boundary ================================
Failover: promote replica shard; clients jitter reconnect
```

**Trip-scoped fan-out (narrow):**

```text
Location Shard --(driver on trip)--> Trip Presence Channel --> Rider App WS
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Failures to design for**

| Failure | Mitigation |
|---------|------------|
| Shard crash | Replicas; rebuild from Kafka compacted topic `driver→latest` |
| Kafka lag | Ingest still ACKs after local write; consumers catch up; alert on lag |
| Poison ping | Schema + quarantine topic; don’t block partition |
| Split brain shard | Fencing token / epoch on shard leadership |
| Redis flush | Rebuild from compacted log; matching degrades briefly |
| Mobile offline | TTL offline; no speculative positions in matching |

**Delivery semantics**

- Ingest: **at-least-once** from client; upsert idempotent by seq/ts.  
- Current state: **latest-wins** by event time.  
- Downstream: at-least-once; consumers idempotent.

**Deal-breaker:** ACK before the shard durable/replica policy you claim; or matching on unauthenticated pings.

### 5.2 Scalability

**Techniques**

1. **Shard by geo cell / city**, not by random driver alone (keeps nearby local).  
2. **Adaptive sampling:** idle 4–10s; on-trip 1s; stopped-at-light can coalesce.  
3. **Binary protocols** (protobuf) at high QPS.  
4. **Cell-dirty notifications** instead of full ping streams to matching.  
5. **Read replicas** for get-by-id; nearby on primary-ish in-memory owners.  
6. **Hot-key split:** airport cell → subcells at higher resolution.

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| Baseline | 1 city Redis cluster + Kafka + ingest GW |
| 10× | Many cities; per-city Redis; shared Kafka with partitions by city |
| 100× | Regional cells; edge PoPs; compacted topics; sampling policies |
| 1,000× | Hierarchical H3; presence aggregation; strict per-status budgets |

### 5.3 Maintainability

- Clear **ownership:** Location service owns presence; Matching owns offers; Map owns rendering.  
- **Versioned ping schema**; reject unknowns carefully (forward compatible).  
- **Feature flags** for filter thresholds (max speed, accuracy).  
- **Replay tooling:** rebuild geo index from compacted log for a city.  
- **SLOs:** ingest success, freshness age histogram, nearby p99, offline false-positive rate.  
- **Load tests** with stadium egress traces (hot cells).

### 5.4 Consistency model (resolved)

| Read | Consistency |
|------|-------------|
| getLocation | Read-after-write for that driver via shard primary |
| nearby | **Timeline consistency** ≈ hundreds of ms; may miss just-moved driver briefly |
| Rider trip map | Prefer primary / sticky; allow client interpolation |

**Invariant:** Never return another driver’s location for an id; never enlarge ACL (rider sees driver only on shared trip / allowed states).

### 5.5 Privacy & safety

- Encrypt in transit; field-level access logs.  
- Retention: hot seconds–minutes; cold sampled; legal holds separate.  
- Fuzz locations for non-essential analytics.  
- Spoofing: impossible jumps, mock-location flags, device attestation hooks (Phase 2).

### 5.6 Interaction with matching (boundary)

```text
Matching should NOT require 1:1 ping stream.
Pattern:
  - periodic or event-driven "cell dirty"
  - nearby query pulls fresh enough set
  - cache candidates for 1–2s with invalidation on cell dirty
```

---

## 6. Wrap-Up

**What to say in 60 seconds**

> We ingest authenticated, rate-limited GPS pings into **regional geo-sharded** location cells that keep an in-memory **current location + cell index** with TTLs for presence. Nearby and get APIs serve matching/ETA; Kafka carries accepted updates for rebuild and analytics. We drop stale/out-of-order pings, adapt sampling by driver state, and narrow fan-out for on-trip rider maps. Scale from one metro to global by splitting cities/cells, adding edge ingest, and aggressively controlling ping cost—not by putting 15M QPS into a single Redis.

**MVP → next**

1. MVP: Redis + geohash + Kafka + nearby/get.  
2. Next: H3, adaptive sampling, compacted rebuild, trip channels.  
3. Later: edge PoPs, hot-cell splits, stronger anti-spoof.

**Risks**

| Risk | Mitigation |
|------|------------|
| Cost explosion | Sampling + regionalization |
| Stale matching | Freshness SLA + TTL |
| Hot cells | Hierarchical resolution |
| Privacy incident | ACL + TTL + audit |

---

## 7. Deeper / Related Interview Questions

### 7.1 Ingest & mobile

**Q: Why not WebSocket always?**  
A: Long-lived WS work well for on-trip; HTTP/2 or QUIC batching often enough for pings; choose per platform battery constraints.

**Q: Client batching vs freshness?**  
A: Batch 1–2s max when on-trip; larger batches when idle. Server still enforces matchability age.

**Q: How do you ack?**  
A: Ack after shard accept (memory + replication factor policy). Don’t wait for heat-map pipeline.

### 7.2 Geo indexing

**Q: Geohash vs H3?**  
A: Both fine; H3 has cleaner k-rings; geohash has boundary issues—always query neighbors.

**Q: Radius query correctness?**  
A: Cover circle with cells, fetch, then precise haversine filter; don’t trust cell alone.

**Q: Airport hotspot?**  
A: Increase resolution; shard set; cache static polygon filters (terminals).

### 7.3 Ordering & time

**Q: Device time vs server time?**  
A: Server time for TTL/presence; device time/seq for last-writer among pings; clamp future timestamps.

**Q: Exactly-once ingest?**  
A: No—idempotent upsert. Exactly-once *effects* for billing don’t belong here.

### 7.4 Scale jumps

**Q: 50K QPS Redis enough?**  
A: Yes with pipelining/sharding; 5M QPS needs many shards + edge + sampling.

**Q: Can Kafka be the current state?**  
A: Compacted topic as **source of rebuild**, not for low-latency nearby cell sets.

### 7.5 Product edges

**Q: Driver in elevator / tunnel?**  
A: Keep last location with growing age; matching may pause offers; UI shows uncertain.

**Q: Multi-device login?**  
A: Single active device session; fencing by session epoch.

**Q: Privacy for idle drivers on heat maps?**  
A: Aggregate/hex counts only; never individual precise points in analytics dashboards.

### 7.6 Comparison

**Q: vs raw “store in DB and query `WHERE distance < r`”?**  
A: Won’t meet latency/QPS; need geo index + hot memory.

**Q: vs pub/sub every ping to matching?**  
A: Explodes; use pull nearby + dirty signals.

### 7.7 Reliability drills

**Q: Redis cluster loses a shard**  
A: Fail matching for that geo slice or rebuild from compacted Kafka; don’t serve other drivers’ data.

**Q: Replay storm**  
A: Rebuild tool rate-limited; prefer compact-latest over full history replay.

### 7.8 Metrics that matter

- `location_age_ms` p50/p99 for matchable drivers  
- `ingest_qps` / `drop_stale_qps` / `drop_accuracy_qps`  
- `nearby_latency_ms` / `nearby_result_size`  
- `hot_cell_cardinality`  
- `presence_false_offline_rate` (complaints / trip issues)

### 7.9 Security

**Q: Can a rider query arbitrary nearby drivers?**  
A: Product ACL: matching service privileged; riders get trip-scoped driver only.

**Q: Encrypted payload fields?**  
A: TLS everywhere; at-rest encryption on stores; minimize cold retention of precise trails.

### 7.10 Interview arithmetic traps

**Q: 1M drivers × 1 ping/s × 1 KB = ?**  
A: 1 GB/s — usually payload is ~100–200 B; also adaptive rate < 1/s. Challenge oversized assumptions.

**Q: Store 30 days of all pings at 5M QPS?**  
A: 5M × 200 B × 86400 × 30 ≈ 2.6×10^15 B ≈ **2.6 PB**/month-class — usually unacceptable; sample/compress/TTL.

---

## 8. Appendices

### 8.1 Schema sketches

```text
CurrentLocation
  driver_id         PK
  lat, lng
  heading, speed
  accuracy_m
  device_ts
  server_ts
  seq
  status            // online, on_trip, offline
  trip_id           nullable
  cell_id           // H3/geohash
  version           // fencing
  session_epoch

GeoCellMembers
  cell_id → set(driver_id)

Presence
  driver_id → expiry_at, matchable
```

```sql
-- optional durable snapshot / audit
driver_location_snapshot(
  driver_id UUID,
  lat DOUBLE, lng DOUBLE,
  cell_id TEXT,
  server_ts TIMESTAMPTZ,
  PRIMARY KEY (driver_id)
);
```

### 8.2 Pseudocode: accept ping

```text
function AcceptPing(driver_id, ping, auth):
  assert auth.driver_id == driver_id
  RateLimit(driver_id)
  if ping.accuracy > MAX_ACCURACY: return Drop("accuracy")
  if FutureSkew(ping.device_ts): clamp or Drop
  cur = Store.Get(driver_id)
  if cur and NotNewer(ping, cur): return Drop("stale")
  if cur and SpeedTeleport(cur, ping): return Drop("teleport") // or quarantine
  new_cell = Cell(ping.lat, ping.lng)
  Store.Upsert(driver_id, ping, new_cell)
  if cur.cell != new_cell:
    Geo.Remove(cur.cell, driver_id)
    Geo.Add(new_cell, driver_id)
  RefreshTTL(driver_id, TTLFor(ping.status))
  Stream.AppendAsync(Accepted(driver_id, ping))
  return ACK
```

### 8.3 Pseudocode: nearby

```text
function Nearby(lat, lng, radius_m, filters, limit):
  cells = CoverCircle(lat, lng, radius_m)
  ids = Union(Geo.Members(cells))
  locs = Store.BatchGet(ids)
  out = []
  now = ServerNow()
  for loc in locs:
    if loc.age(now) > filters.max_age: continue
    if not MatchFilters(loc, filters): continue
    d = Haversine(lat, lng, loc.lat, loc.lng)
    if d <= radius_m: out.append(loc, d)
  return TopByDistance(out, limit)
```

### 8.4 Client sampling policy (example)

| Driver state | Interval | Notes |
|--------------|----------|-------|
| Online idle | 4s | Coalesce if moved < 10m |
| Approaching offer | 2s | |
| On trip | 1s | |
| Background OS-limited | best effort | Server TTL relaxed slightly |

### 8.5 Compaction topic

```text
topic location.driver.compacted
key = driver_id
value = latest AcceptedPing | Tombstone(offline)
retention = compact
```

Used for shard rebuild on failover.

### 8.6 ACL matrix

| Caller | get | nearby | raw stream |
|--------|-----|--------|------------|
| Matching service | yes | yes | cell-dirty |
| ETA service | yes | limited | no |
| Rider app | trip driver only | no | trip channel |
| Analytics | no precise | no | sampled |
| Driver app | self | no | no |

### 8.7 SLO dashboard (starter)

| SLO | Target |
|-----|--------|
| Ingest availability | 99.9% per region |
| Matchable freshness p99 | < 5s |
| Nearby p99 | < 50ms city-local |
| Wrong-driver disclosures | 0 |
| Rebuild time for city shard | < 5–10 min |

### 8.8 Failure injection list

- Kill location shard primary  
- Partition ingest GW from Redis  
- Publish poisoned GPS jumps  
- Stadium 20× cell density  
- Client clock +2 hours  
- Kafka pause 15 minutes  

### 8.9 Glossary

| Term | Meaning |
|------|---------|
| Matchable | Online + fresh + eligible for offers |
| Cell dirty | Signal that a geo cell’s membership changed |
| Compacted log | Kafka log retaining latest per driver key |
| Adaptive sampling | Dynamic ping interval by state/battery/speed |

### 8.10 Interview checklist

- [ ] Bound ping rate and payload size  
- [ ] State freshness TTL + offline  
- [ ] Geo index + precise filter  
- [ ] Stale/out-of-order handling  
- [ ] Shard by city/geo  
- [ ] Separate hot path from analytics  
- [ ] Narrow trip fan-out  
- [ ] Rebuild story after memory loss  
- [ ] Privacy ACL + retention  
- [ ] Cost math at 100× / 1000×  

---

*End of driver location tracking system design.*
