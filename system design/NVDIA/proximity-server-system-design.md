# System Design: Proximity Server

> **Focus areas:** Geo indexing (geohash/S2/H3) · Real-time location updates · Radius query · Privacy · Region sharding · Presence freshness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split update vs query load classes, honest geo index trade-offs, privacy as a deal-breaker, resolved ownership of location truth vs index

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

Goal: **bound the product**—what “nearby” means (users, devices, or resources), freshness SLOs, privacy constraints, and at which scale geo indexes must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What entities? | Users and/or devices/resources (cars, GPUs in edge sites, stores) | Unified `entity_id` + `entity_type`; indexes per type optional |
| F2 | Update model? | Clients push GPS/IP/geo periodically; server may derive coarse IP geo | Ingest path high write; last-known location |
| F3 | Query API? | “Find K nearest within radius R” + optional filters | Geo index + post-filter; distance compute |
| F4 | Real-time? | Seconds-level freshness for online presence | TTL on presence; pubsub optional for moving queries |
| F5 | Privacy? | Users opt-in; fuzzing; visibility rules (friends-only) | **Privacy filters are deal-breakers**; never return raw coords without policy |
| F6 | Offline handling? | Mark stale after T seconds/minutes | Soft-offline; exclude from “online nearby” |
| F7 | Geofences? | Optional: enter/exit notifications | Async fence evaluator; not MVP-critical |
| F8 | Multi-tenant? | B2B “nearby devices for fleet X” | `tenant_id` isolation on every key |
| F9 | Accuracy? | Phone GPS ~5–50m; IP geo city-level | Document precision; don’t overclaim |
| F10 | History? | Last location only MVP; trails Phase 2 | Separate cold store if needed |
| F11 | Ranking? | Distance primary; optional score (battery, load, affinity) | Retrieve candidates → rank |
| F12 | Write authz? | Entity can only update own location (or device cert) | mTLS / token scoped to entity |

**MVP functional scope (lock with interviewer):**

1. Upsert location `(entity_id, lat, lon, ts, accuracy, status)`.  
2. Query `nearby(lat, lon, radius_m, k, filters)` returning entities **authorized** for the requester.  
3. Presence TTL: stale entities excluded from online queries.  
4. Privacy modes: precise / city-fuzzed / friends-only / hidden.  
5. Multi-tenant isolation; basic rate limits.  
6. Metrics: update QPS, query p99, index lag, stale %.

**Out of MVP (explicitly defer):**

- Continuous moving-query subscriptions at global scale (design hooks)  
- Full road-network / drive-time distance (use haversine/great-circle MVP)  
- Indoor centimeter RTLS  
- Historical trajectory analytics product  
- Perfect global strong consistency on every location write

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Query latency? | Interactive map/list | p50 < 50ms, p99 < 200ms in-region for R ≤ 5km, k ≤ 50 |
| N2 | Update latency? | Soft real-time | p99 < 100ms ACK; index visible < 1–2s typical |
| N3 | Freshness? | Online nearby | Location age < 30–60s for “live”; configurable |
| N4 | Availability? | Reads degrade gracefully | 99.9% query; stale-ok better than down |
| N5 | Privacy correctness? | No unauthorized disclose | Fail closed on visibility uncertainty |
| N6 | Accuracy honesty? | Don’t claim GPS if IP | Return `precision` class |
| N7 | Multi-region? | Users worldwide | **Shard by geo region/cell**; query fans to cells covering radius |
| N8 | Throughput? | See scale table | Split **update QPS** vs **query QPS** vs **fanout** |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Device heartbeats location every 10s → indexed → nearby query returns it within radius.  
2. User opts into friends-only → stranger query omits them even if physically close.  
3. Entity goes offline (no updates) → TTL expires → disappears from live results.  
4. Query near cell boundary → fan-out to neighboring geo cells → merge top-k.  
5. Tenant fleet query filters `entity_type=gpu_node` + `sku=H100` within 100km of office (enterprise angle).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Spoofed GPS | Authz + anomaly (teleport detection); optional trusted device attestation |
| Radius spans many cells | Bound max R; grid fan-out with budget; degrade |
| Hot downtown cell | Shard further; hot-key partitions; cache popular queries carefully |
| Entity teleports 1000km | Reject or mark suspicious; require confirm |
| Polar / dateline | Use library (S2/H3) that handles antimeridian |
| k=10000 request | Cap k; cursor/paginate |
| Privacy mode change | Immediate index update / tombstone precise cell |
| Stale replica shows old city | Prefer owner region; TTL bounds staleness |
| Empty desert query | Fast empty via sparse index; don’t scan world |
| Concurrent updates | Last-writer-wins by `ts` with server receive time tie-break |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active entities | 10M | 100M | 1B | 10B |
| Location updates / day | 50B | 500B | 5T | 50T |
| Peak **update** QPS | ~1M | ~10M | ~100M | ~1B |
| Peak **query** QPS | ~50K | ~500K | ~5M | ~50M |
| Avg update interval | 10–30s | 10–30s | 5–30s | adaptive |
| Avg radius | 1–5 km | 1–5 km | 0.5–10 km | mixed |
| Avg k | 20 | 20 | 50 | 50 |
| Regions / cells | 8 | 16 | 32 | 64+ |
| Geofences active | 100K | 1M | 10M | 100M |
| Tenants | 1K | 10K | 100K | 1M |

**What each jump forces:**

- **10×:** Geo-partitioned ingest; in-memory hot presence per cell; H3/S2 indexes.  
- **100×:** Adaptive update rates; query result caching with short TTL; fence evaluators as fleet.  
- **1,000×:** Hierarchical cells; edge PoPs for updates; massive fan-out control; privacy tokenization; cold/hot entity tiers.

**Note on 1B update QPS:** That is extreme (IoT planetary). Call it out; often real systems use **adaptive sampling** (move more → update more). Interviewer may reduce—still show the math.

### 1.5 Etc. (Constraints & Assumptions)

- Distance MVP = great-circle (haversine); not traffic-aware ETA.  
- Clients may lie about GPS—product/security policy decides trust.  
- “Nearby users” implies **GDPR/CCPA** sensitive data—minimize retention.  
- NVIDIA angle: same pattern as discovering nearby **edge GPU nodes / robotics devices / Omniverse collaborators**; privacy & tenancy still apply.

**Scope statement:**

> Design a multi-tenant proximity server that ingests high-rate location updates, indexes entities in geo cells (H3/S2/geohash), answers radius/k-NN queries with privacy filters and presence TTLs, and scales via regional geo-sharding from tens of millions to billions of entities without leaking unauthorized locations.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Location **updates** | ~1M/s | ~1B/s | Write-heavy; needs adaptive rates |
| Nearby **queries** | ~50K/s | ~50M/s | Read path; fan-out amplification |
| Presence **TTL sweeps** | proportional to entities | huge | Lazy expiry preferred |
| Geofence eval | subset of updates | | Async |
| History write | optional | | Cold path |

**Deal-breaker:** treating update QPS and query QPS as one “API QPS,” or ignoring query **fan-out** (one query → N cell lookups).

### 2.2 Update volume math

```text
10M entities × (1 update / 15s) ≈ 666K updates/s average
Peak 1.5× → ~1M/s (matches baseline table)

Payload ~100–200 B → 1M/s × 150 B ≈ 150 MB/s ingest
1,000× naive → 150 GB/s — impossible without sampling/edge aggregation

Adaptive policy example:
  stationary: update every 60–120s or on >50m move
  moving: every 5–10s
Effective rate often 5–10× lower than naive fixed interval
```

### 2.3 Storage

```text
Hot presence record ~128–256 B (id, cell, lat, lon, ts, flags)
10M × 200 B ≈ 2 GB (fits memory per region shards)
1B × 200 B ≈ 200 GB cluster-wide hot
10B × 200 B ≈ 2 TB hot → sharded heavily; cold entities on disk

Secondary geo index: entity_id in cell sets
If avg 1 cell membership: similar order

History 30d at 1 update/min: enormous → usually don’t store full trails MVP
```

### 2.4 Query fan-out

```text
H3 resolution ~9: hex edge ~174m
Radius 2km → covers O(100–200) cells depending on packing
Radius 50km → thousands of cells → MUST cap or use coarser res

Strategy:
  choose resolution so expected cells in R is ~10–100
  for large R: coarse index first, then refine
```

**Unit check:** Don’t claim “one Redis GET” for 50km radius over dense city.

### 2.5 Distance compute

```text
Candidate set after cell union: often 100–5000 entities
Haversine per candidate: cheap (microseconds)
Bottleneck is gathering candidates across shards, not CPU math
```

### 2.6 Hotspot cities

```text
If 5% of entities in one metro:
Baseline 10M → 500K in metro
Sharded by H3 parent; further split hot parents by hash(entity_id)
```

### 2.7 Critical bottlenecks (rank ordered)

1. **Update ingest** without adaptive sampling  
2. **Hot geo cells** (downtown)  
3. **Query fan-out** for large radius  
4. **Privacy filter** applied too late (leak in logs)  
5. **Cross-region queries** spanning oceans (should be rare—cap R)  
6. **Thundering herd** reconnect storms after outage  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Entity:
  entity_id, tenant_id, type, privacy_mode, acl_version

LocationFix:
  lat, lon, accuracy_m, source (gps|ip|manual), client_ts, recv_ts

Presence (hot):
  entity_id → {cell_id, lat, lon, ts, status: ONLINE|STALE|HIDDEN}

GeoIndex:
  cell_id → set/map of entity_ids (or pointers)
```

**State:** last-known location with TTL; not a full CRDT trajectory.

### 3.2 Options: geo index

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Geohash prefixes | Simple; ZSET tricks in Redis | Cell distortion; boundary pain | Needing uniform cells globally |
| B. Google S2 | Equal-area-ish cells; solid libs | Learning curve | Team refuses non-latlon thinking |
| C. Uber H3 | Hex neighbors clean; res ladder | Dependency; pentagons rare | None for most proximity |
| D. R-tree in PostGIS | Rich queries | Hard at 1M update/s | Hot presence at IoT scale |
| E. Quadtree custom | Full control | Reinventing | Timeboxed interview without lib |

**Chosen path:**

- **MVP:** H3 (or S2) cell membership + Redis/memory sets per cell + Postgres/KV for entity metadata/privacy.  
- **Large R:** hierarchical resolution (coarse → fine).  
- **PostGIS:** fine for baseline millions with moderate update rates; not for 100M update/s.

### 3.3 Update path (ownership)

**Invariant:** Presence service owns **hot location truth** per entity; geo index is derived and must be updated atomically enough to avoid double-cell ghosts (best-effort with repair).

```text
1. Authn entity
2. Validate coords + teleport check (distance vs Δt)
3. Compute cell_id = H3(lat, lon, res)
4. Load previous presence
5. If cell changed: remove from old cell; add to new
6. Write presence record with ts
7. ACK
8. Optional: emit event for fences / subscribers
```

**LWW:** accept update if `client_ts` ≥ stored (with max skew clamp using `recv_ts`).

### 3.4 Query path

```text
1. Authn requester; load visibility scope (friends, tenant, public)
2. Bound radius ≤ Rmax (e.g. 50km for user apps)
3. cells = cover(disk(lat,lon,R), res)
4. Fan-out Get entities in cells (parallel to cell owners)
5. Filter: privacy + ACL + freshness + tenant + attributes
6. Compute distance; take top-k
7. Response: entity stubs + distance (+ fuzzed coords per policy)
```

**Deal-breaker:** returning precise lat/lon when privacy_mode says city-level.

### 3.5 Privacy model

| Mode | Index behavior | Query return |
|------|----------------|--------------|
| HIDDEN | Not in geo index | Never |
| FRIENDS | Indexed | Only if friendship edge |
| TENANT | Indexed | Same tenant + role |
| FUZZED | Indexed at coarse cell | Coarse location / distance band |
| PRECISE | Fine cell | Precise if authorized |

**Ownership:** Policy engine applies **before** serialization; logs store IDs not coords by default.

### 3.6 Sharding by region

```text
World → Region (US-EAST, EU, ...) → H3 parent partitions → hot subshards

Entity home: usually region of last location (or account home)
Updates route to region owning current cell
Queries cover cells → may fan across 1–few regions only (R capped)
```

**Cross-region:** entity flight from US→EU: migration protocol moves presence; brief dual-read OK.

### 3.7 Freshness & TTL

```text
ONLINE if now - ts <= soft_ttl (e.g. 60s)
STALE if soft_ttl < age <= hard_ttl (e.g. 15m): optional “last seen”
Remove from live index after hard_ttl (lazy on read + periodic GC)
```

**Lazy expiry:** on cell scan, drop stale; don’t rely only on global sweeper.

### 3.8 Real-time subscriptions (Phase 1.5)

```text
Client subscribes: watch(center, R) or watch(entity)
Server: register watcher on cells; on update intersecting, push delta
Scale killer: millions of watchers × dense updates
Mitigations: coarse cells, coalesce, edge fanout, cap subscriptions
```

MVP can be **poll nearby every N seconds**; mention push as extension.

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Index | H3/S2 cells | Neighbor clarity + hierarchy | Pure lat sorted scan |
| Hot store | Memory/Redis per shard | Update/query speed | Disk row per update at 1M/s |
| Distance | Haversine MVP | Simple | Ignoring boundary cells |
| Privacy | Filter pre-return | Safety | Client-side filter only |
| Large R | Coarse-then-fine | Control fan-out | Fixed fine res worldwide |
| Consistency | LWW presence | Matches location | Strict serializability globally |

### 3.10 APIs

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/v1/entities/{id}/location` | Upsert fix |
| POST | `/v1/nearby` | Radius/k query |
| GET | `/v1/entities/{id}/location` | Authorized get |
| PUT | `/v1/entities/{id}/privacy` | Mode change |
| POST | `/v1/geofences` | Phase 1.5 |
| GET | `/v1/health/cells/{id}` | Ops |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Devices/Apps                    Query clients
      |                               |
      v                               v
 +-----------+                  +-----------+
 | Ingest GW |                  | Query GW  |
 | auth, RL  |                  | auth, RL  |
 +-----+-----+                  +-----+-----+
       |                              |
       v                              v
 +-------------+                +--------------+
 | Location    |                | Nearby       |
 | Service     |                | Service      |
 +------+------+                +------+-------+
        |                              |
        v                              v
 +--------------+   cells    +------------------+
 | Presence +   |<---------->| Geo Index Shards |
 | Privacy meta |            | (H3/S2 sets)     |
 +------+-------+            +--------+---------+
        |                             |
        v                             v
 +--------------+            +----------------+
 | Event bus    |            | Friend/ACL     |
 | fences/sub   |            | Service        |
 +--------------+            +----------------+
```

### 4.2 Sequence: update

```text
Device → Ingest: PUT location (lat,lon,ts)
Ingest → Location Svc (region of cell)
Location: teleport check OK
Location: cell' = H3(...)
if cell' != cell:
  Index.remove(entity, cell)
  Index.add(entity, cell')
Presence.set(entity, fix)
→ ACK
→ emit LocationChanged (async)
```

### 4.3 Sequence: nearby query

```text
Client → Nearby: {lat, lon, r=2000, k=20}
Nearby → cover cells (incl. boundary ring)
Nearby → parallel mget cell sets (shards)
Nearby → ACL/privacy filter
Nearby → distances → top 20
→ return [{id, dist, fuzzed_point?}]
```

### 4.4 Sequence: boundary fan-out

```text
Query center near cell edge
cover() includes neighbors across shard A and B
merge candidates → global top-k
```

### 4.5 Region cells

```text
[ EU Cell ]   [ US Cell ]   [ APAC Cell ]
 each: ingest + presence + geo shards
Directory: cell_id → region
Rare multi-region query if R spans (usually capped)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Authz on write:** entity token cannot update another entity.  
2. **Privacy fail-closed:** if ACL service uncertain, omit entity.  
3. **TTL bound:** live queries never return arbitrarily old “online” without labeling stale.  
4. **Cell membership ≤ 1 fine cell** for precise mode (no duplicates across cells after repair).  
5. **Tenant isolation:** no cross-tenant candidates.  
6. **LWW by timestamp** with skew guards.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Index remove fails after cell move | Periodic reconcile from presence SoT |
| Shard down | Query degrades partial; show degraded flag |
| ACL service down | Fail closed (empty/omit) not fail open |
| Update storm after outage | Backpressure + jittered client retry |
| Clock skew on devices | Clamp future ts; prefer recv_ts for TTL |

**Cancel vs resume**

- **Hide/opt-out:** privacy HIDDEN removes from index immediately.  
- **Resume sharing:** re-add on next update.  
- **Delete entity:** tombstone + purge index + retention job.

### 5.2 Scalability

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| 1× | API + Redis H3 sets + Postgres metadata; single region |
| 10× | Geo regions; sharded cells; adaptive updates |
| 100× | Hot-cell split; query caches; fence fleet; friend-graph cache |
| 1000× | Edge ingest; hierarchical index; subscription coalescing; cold tier |

**Adaptive update control**

```text
server returns next_update_hint_sec based on speed & density
dense stadium: longer hints / coarser cells for FUZZED
moving highway: shorter hints
```

**Query cache:** key = `(quantized_cell, r_bucket, filter_hash)` TTL 1–5s; careful with privacy (cache per visibility cohort, not global).

### 5.3 Maintainability

- Versioned H3 resolution config with dual-index during migrations.  
- Reconciler job: presence → rebuild cell membership.  
- Chaos: kill shard, partition ACL, flood teleport spoof.  
- Reason codes: `RadiusTooLarge`, `StaleExcluded`, `Forbidden`, `DegradedPartial`.

**Observability**

- Update QPS by region/cell; query p99; candidates scanned; filter drop rates; TTL expiry rate; teleport rejects.  
- Heatmaps of cell cardinality (ops).  
- Audit privacy mode changes.

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× — correct MVP**

```text
PUT location → Redis HASH presence
H3 cell → Redis SET of entity_ids
POST nearby → SMEMBERS cells → filter → sort by distance
Postgres: profiles, privacy, friendships
```

Bottleneck: hot SET downtown; large R; ACL joins.

**10× — regionalize**

- Route by cell→region.  
- Pipeline updates; batch index ops.  
- Friend IDs cached in memory for query path.

**100× — hierarchy & hints**

- Coarse H3 for wide search; fine for dense.  
- `next_update_hint` to cut write QPS.  
- Partial query results with `truncated:true` under overload.

**1000× — planetary IoT**

```text
Edge PoP aggregates stationary devices
Central cells hold mobiles + indexes
Hierarchical admission on query fan-out budget
Privacy tokens / k-anonymity for FUZZED
Cold entities (inactive 24h) evicted to disk index
```

### 5.5 Geo boundary correctness

**Problem:** entity in cell A, query disk covers only cell B visually but distance < R.

**Fix:** `polyfill` / `gridDisk` covering the search circle, not single cell of the center alone.

**Antimeridian:** convert via H3/S2 APIs; never hand-roll ±180 without tests.

### 5.6 Ranking beyond distance

```text
score = dist_km + w1*load + w2*(1-trust) + w3*staleness
for resources (GPU nodes): prefer low load within R
for people: prefer friends / affinity
```

Retrieve **candidate multiplier** (e.g. 5k) then rank—don’t geo-filter after global scan.

### 5.7 Security & privacy deep dive

- Store precise coords encrypted at rest; decrypt in query service with need-to-know.  
- FUZZED: snap to coarse H3 + random jitter within cell; stable per day to avoid tracking via jitter changes—or intentional churn trade-off.  
- Rate-limit queries that sweep grids (stalking pattern).  
- GDPR: delete location history; export.  
- **Deal-breaker:** “we’ll filter on the client.”

### 5.8 Ownership resolution

| Concern | Owner |
|---------|-------|
| Last lat/lon truth | Presence store |
| Cell membership | Geo index (derived) |
| Who can see whom | ACL/privacy service |
| Region routing | Cell→region directory |
| Fence triggers | Async evaluators |

**Contradiction trap:** two writers updating presence and index independently without reconcile → ghosts/duplicates.

### 5.9 Geofences (extension)

```text
Fence: polygon / H3 set + enter/exit webhooks
On LocationChanged: check fences for entity
Dedupe triggers with hysteresis hysteresis_m
Delivery: at-least-once webhook with idempotency key
```

### 5.10 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| Client-only privacy filter | Trivial leak |
| Single global Redis | Hotspots + blast radius |
| Fine H3 for 100km R | Fan-out explosion |
| Sync fence webhooks on update | Update p99 dies |
| Ignore boundary cells | False negatives |
| Fail open on ACL errors | Privacy incident |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Index | H3/S2 cells with hierarchical res |
| Hot path | Presence + in-memory/Redis cell sets |
| Query | Cover circle → fan-out → privacy filter → top-k |
| Freshness | TTL soft/hard with lazy expiry |
| Scale | Geo region shards + hot-cell split |
| Privacy | Server-side fail-closed modes |

### 6.2 Top risks

1. Update QPS without adaptive sampling  
2. Large-radius fan-out  
3. Privacy bugs  
4. Cell boundary false negatives  
5. Downtown hot shards  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Entities, radius, privacy, freshness |
| 5–12 | API + presence model + TTL |
| 12–22 | H3/S2 index + query algorithm |
| 22–32 | Sharding, fan-out, hotspots, estimates |
| 32–40 | Privacy + spoofing + failure modes |
| 40–45 | Subscriptions/fences + wrap |

---

## 7. Deeper / Related Interview Questions

### 7.1 Geo indexes

**Q: Geohash vs S2 vs H3?**  
A: Geohash simplest but rectangular distortion; S2/H3 better neighbors & hierarchy. Pick one, show boundary cover.

**Q: What resolution?**  
A: Match median query radius and density. Res too fine → huge fan-out; too coarse → heavy post-filter.

**Q: How do you handle k-NN not radius?**  
A: Expanding ring search over cell neighbors until k satisfied or max R.

**Q: Why not PostGIS alone?**  
A: Great at moderate QPS; at huge update rates, memory cell indexes win.

### 7.2 Correctness

**Q: False negatives near edges?**  
A: Always polyfill the search disk; test fixtures on boundaries and dateline.

**Q: Duplicate entities in two cells?**  
A: Reconcile from presence; query dedupe by entity_id.

**Q: Clock skew?**  
A: Clamp; TTL based on recv_ts; reject absurd future.

### 7.3 Privacy

**Q: Can fuzzing be reversed?**  
A: Coarse cells + low update rate + k-anonymity help; never promise anonymity if precise mode was ever shared with attacker.

**Q: Friends-only at scale?**  
A: Precompute bloom/bitset of friend ids per user; intersect candidates.

**Q: Logging?**  
A: Log entity ids and cell ids; avoid precise coords in plain logs.

### 7.4 Scale

**Q: 1M updates/s to one Redis?**  
A: No—shard by cell/region; batch; adaptive rates.

**Q: Query cache and privacy?**  
A: Cache key must include viewer cohort or only cache public entities.

**Q: Stadium 100k people?**  
A: Coarser cells, sampling returns, higher `next_update_hint`, paginate.

### 7.5 Multi-region

**Q: Who owns an entity?**  
A: Region of current cell (or pinned home). Migration on sustained cell region change.

**Q: Cross-ocean radius?**  
A: Reject—product nonsense for “nearby”; force smaller R.

### 7.6 Security

**Q: GPS spoofing?**  
A: Attestation, velocity checks, trusted sensors for high-security tenants; consumer apps best-effort.

**Q: Stalking via API?**  
A: Rate limits, anomaly detection, friends-only defaults, audit.

### 7.7 NVIDIA-flavored variants

**Q: Nearby GPU capacity?**  
A: Entities = edge nodes with attributes (SKU, free GPUs); rank by distance + capacity; still geo-shard.

**Q: Robotics devices in warehouse?**  
A: Smaller R, higher res, local region only; UWB/indoor later.

**Q: Omniverse session discovery?**  
A: Proximity + ACL + latency (not just distance)—multi-signal rank.

### 7.8 Comparison

**Q: vs Redis GEORADIUS?**  
A: Fine MVP; at 100× need sharding, privacy, adaptive updates, hierarchical cover.

**Q: vs Kafka+Flink geofencing only?**  
A: Different product—events vs interactive nearby query.

### 7.9 Algorithms

**Q: Haversine vs Vincenty?**  
A: Haversine enough for city-scale; note error margins.

**Q: Covering radius with hexes?**  
A: `gridDisk` / fill polygon of circle approximation; include margin for accuracy.

**Q: Top-k merge from shards?**  
A: Each shard returns local top-k; merger heap to global top-k (need local k or careful bounds).

### 7.10 Interview trap: units

**Q: 10M entities updating every 15s → QPS?**  
A: 10M/15 ≈ **6.7e5/s ≈ 667K/s**, not 10M/s.

**Q: Fan-out ignored?**  
A: Always estimate cells × entities-per-cell scanned.

### 7.11 Reliability drills

**Q: ACL timeout?**  
A: Omit (fail closed); metric `acl_degraded`.  
**Q: Index loss?**  
A: Rebuild from presence snapshot.  
**Q: Thundering reconnect?**  
A: Jitter; exponential backoff; server hints.

### 7.12 Product edges

**Q: IP geo fallback?**  
A: Mark `precision=city`; don’t mix into precise neighbor lists without label.  
**Q: Battery life?**  
A: Significant motion APIs; server `next_update_hint`.  
**Q: Airplane mode restore?**  
A: Burst update; teleport check may soft-fail with “verify.”

---

## 8. Appendices

### 8.1 Schema sketches

```text
presence (hot KV):
  entity_id → {
    tenant_id, lat, lon, accuracy_m,
    cell_id, res, ts_recv, privacy_mode,
    status, attrs_ref
  }

geo_index:
  cell_id → SET entity_id  (or ZSET score=geohash for debug)

entity_meta (SQL/KV):
  entity_id, tenant_id, type, privacy_mode, acl_version, created_at

friendship:
  user_a, user_b

geofence:
  fence_id, tenant_id, cell_cover[], webhook, hysteresis_m
```

### 8.2 API checklist

- [ ] `PUT /v1/entities/{id}/location`  
- [ ] `POST /v1/nearby` with radius, k, filters  
- [ ] Privacy mode update  
- [ ] Admin cell stats  
- [ ] Optional geofence CRUD  
- [ ] Optional subscribe/watch  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Cell | H3/S2/geohash discrete area |
| Cover | Set of cells intersecting search disk |
| Presence | Hot last-known location |
| Soft TTL | Online freshness bound |
| Hard TTL | Remove from live index |
| FUZZED | Coarse/noisy location for privacy |
| Fan-out | Query parallel fetches across cells/shards |
| Reconcile | Rebuild index from presence SoT |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | H3+Redis sets, TTL, privacy modes, haversine top-k |
| 10× | Regional shards, teleport checks, adaptive hints |
| 100× | Hot-cell split, hierarchical res, query cohort cache |
| 1000× | Edge ingest aggregation, cold tier, subscription coalescing |

### 8.5 Nearby request sketch

```json
{
  "lat": 37.386,
  "lon": -122.084,
  "radius_m": 2000,
  "k": 20,
  "filters": {"type": "user", "online_only": true},
  "viewer_id": "u123"
}
```

### 8.6 H3 resolution cheat sheet (approx)

| Res | Edge length | Use |
|-----|-------------|-----|
| 7 | ~1.2 km | Coarse city |
| 8 | ~460 m | Neighborhood |
| 9 | ~174 m | Default urban nearby |
| 10 | ~66 m | Dense venues |

Pick using density experiments, not dogma.

### 8.7 Teleport check

```text
max_speed_m_s = 90  # ~320 km/h margin for cars/planes policy-specific
if distance(old, new) > max_speed * Δt * slack:
  reject or require attestation
```

### 8.8 Interview “say this” summary (60 seconds)

> High-rate location ingest into a presence store with H3/S2 cell indexes sharded by geo region; nearby queries polyfill the search radius, fan out to cell shards, then **privacy/ACL filter before return**; TTLs define online; adaptive update hints control write amplification; never fail open on visibility; large radii use hierarchical cells to bound fan-out.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| Client-side privacy | Leak |
| Single cell lookup | Boundary false negatives |
| Fixed 1Hz global updates | Melts ingest |
| PostGIS at 1M writes/s | Wrong tool alone |
| Global query cache | Cross-user leak |
| 10M/15s = 10M QPS | **~667K QPS** |

### 8.10 Reliability test plan

1. Move entity across cell boundary → one membership.  
2. ACL service timeout → entity omitted.  
3. Disable sharing → immediate disappearance.  
4. Query on dateline/poles → correct cover.  
5. Kill geo shard → degraded flag, not wrong privacy.

### 8.11 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Update ACK p99 | < 100ms |
| Nearby p99 (R≤5km,k≤50) | < 200ms |
| Index visibility lag p95 | < 2s |
| Privacy incidents | 0 |
| Teleport reject rate | monitored |

### 8.12 Related systems map

```text
Ingest → Location Service → Presence SoT
                         ↘ Geo Index shards
Query → Nearby Service → cover cells → merge/rank
                      → ACL/Privacy
Updates → Event bus → Geofence workers → Webhooks
```

### 8.13 Rank merge sketch

```text
for shard in shards:
  cands += shard.top(m)  # m >= k
dedupe by entity_id
filter privacy
return global_top_k_by_distance(cands)
```

### 8.14 Storage tiers

| Tier | Contents | TTL |
|------|----------|-----|
| Hot memory | Online precise presence | minutes–hours |
| Warm KV | Recent stale | days |
| Cold object | Optional history | policy |
| Forbidden | Raw trails without need | — |

### 8.15 NVIDIA interview angle

Proximity appears in Exponent-style NVIDIA generalist lists. Tie to **edge resource discovery** (nearest inference node) while still nailing classic geo index + privacy. Show you can estimate fan-out and avoid fail-open ACL—same rigor as multi-tenant GPU fleets.

### 8.16 Push subscription cost model

```text
watchers W, update rate U intersecting, notify size S
notify QPS ≈ U_intersecting
If W=10M and each sits in dense cells, coalescing mandatory:
  per-cell pubsub topics + client filters
  max notify rate per watcher
```

### 8.17 Failure: partial cell results

```text
If 1 of 40 cells fails:
  return results_from_39 + degraded=true
  OR fail entire query for safety-critical tenants
Product choice—document it
```

---

*End of proximity server system design.*
