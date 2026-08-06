# System Design: Large-Scale Nearby Users (Meta)

> **Focus areas:** Geo indexing · Proximity query · Privacy · Location update firehose · Sharding · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split location-update vs nearby-query planes, explicit privacy deal-breakers  
> **Interview theme:** Classic Meta/geo L5+ — “who’s nearby” at social scale without leaking precise location or melting a single region shard

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—a service that answers **“which users are near me?”** at Meta social scale, with continuous location updates, ranked nearby results, and strong privacy controls.

### 1.0 What this is / is not

| Dimension | **Nearby users (this doc)** | Not this |
|-----------|----------------------------|----------|
| Primary job | Index user locations; query k-nearest / radius | Full maps product / turn-by-turn nav |
| Success | Fresh, relevant nearby people; privacy-safe | Exact GPS of every stranger |
| Data plane | Location updates + geo index + query | Ride-sharing dispatch optimization |
| Query | Nearby list / map pins for opted-in users | Arbitrary historical trajectory analytics (Phase 2) |
| Correctness | Approximate distance OK; freshness SLO | Perfect continuum physics simulation |

**Scope statement:** Design a large-scale nearby-users system: opt-in location sharing, geo index, radius/kNN queries, ranking, privacy, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who appears nearby? | Opt-in users; optionally friends-only / friends-of-friends | Visibility ACL on index |
| F2 | Query types? | Radius (e.g. 1–50 km) and/or top-K nearest | Geo index supporting range + kNN |
| F3 | Update frequency? | App foreground frequent; background throttled | Adaptive update policy |
| F4 | Freshness? | Minutes OK for social; seconds for “live” mode | TTL + last_seen; stale filtering |
| F5 | Ranking? | Distance + friendship + activity + mutual friends | Candidate gen then rank |
| F6 | Privacy precision? | Fuzzy location / geohash precision reduction | Never store/query finer than policy |
| F7 | Offline users? | Show last known within TTL or hide | TTL eviction from hot index |
| F8 | Block / restrict? | Blocked users never appear either way | Filter with block graph |
| F9 | Map vs list? | Both; densify pins in crowded areas | Clustering at high zoom-out |
| F10 | Notifications? | “Friend nearby” optional Phase 1.5 | Geo fencing / rare alerts |
| F11 | Ghost mode? | Hide temporarily without full opt-out | Visibility flag |
| F12 | Age / safety? | Minors restricted | Policy gates |

**MVP functional scope:**

1. Opt-in users share coarse location with chosen audience (friends / friends+ / public-app feature set).  
2. Clients send location updates under adaptive policy.  
3. `GET nearby` returns ranked users within radius or top-K.  
4. Distance shown as bucketed (“<1 km”, “2–5 km”) not exact meters for strangers.  
5. Block, ghost mode, precision floor enforced.  
6. Stale users excluded via TTL.  
7. Basic densification/clustering for map view.

**Out of MVP:**

- Continuous trajectory storage / stalking timeline  
- Precise meter-level public location  
- Global “radar” for all 1B users in one query without radius  
- AR live-direction overlays  
- Guaranteed sub-second location sync worldwide

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Update ingest durability | No silent loss of last location | At-least-once; last-write-wins per user |
| N2 | Query latency | Snappy list/map | p99 < 100–200ms |
| N3 | Location freshness | Social OK | Index lag p99 < 30–60s; background looser |
| N4 | Availability | Feature critical when launched | 99.9% query; degrade with stale cache |
| N5 | Privacy | Non-negotiable | Precision floor; ACL; audit |
| N6 | Geo skew | Cities denser | Cell capacity; hotspot splits |
| N7 | Multi-region | Global | Users home in regional geo cells |
| N8 | Cost | Update firehose huge | Adaptive sampling; coarse cells |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User enables Nearby → sets audience Friends → app sends location every ~30s foreground.  
2. User opens Nearby map → query radius 5 km → sees friend pins + ranked list.  
3. Friend moves across town → update → disappears from 5 km result within freshness SLO.  
4. User enables Ghost mode → instantly removed from others’ results.  
5. User blocks someone → mutual exclusion on next query.  
6. Dense downtown → map shows clusters; zoom reveals individuals (if ACL allows).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| GPS spoof / teleport | Velocity sanity checks; anomaly quarantine |
| Update storm in stadium | Cap update rate; cell split; query sampling |
| User at cell boundary | Index in neighboring cells; query pads cells |
| Clock skew | Server receive time + client ts; LWW rules |
| Privacy precision mismatch | Server re-quantizes; never trust client fine GPS for storage |
| Opt-out race | Tombstone visibility; query filters |
| Cross-region travel | Migrate hot index entry to new geo cell |
| Friend-only ACL miss | Never return non-visible candidates |
| Zero results rural | Expand radius suggest; show last active friends elsewhere (product) |
| Battery saver mode | Client reduces update frequency; mark low-accuracy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Opt-in MAU | 50M | 500M | — | multi-B class |
| Peak concurrent sharers | 5M | 50M | 500M | 5B-class absurd → cell fabric |
| Location updates/s | 100K | 1M | 10M | 100M |
| Nearby queries/s | 50K | 500K | 5M | 50M |
| Avg candidates considered / query | 200–2K | similar | need tighter cells | hierarchical |
| Geo cell size (urban) | ~0.5–1 km | finer | dynamic | dynamic |
| Index entries | = active sharers | ×10 | ×100 | sharded world |
| Friendship edge checks / query | bounded | cache | bloom + cache | precomputed bitsets |

**What each jump forces:**

- **10×:** Geohash/S2 cells + Redis/KV geo; adaptive updates; query candidate cap.  
- **100×:** Regional geo cells; hotspot split; ranker separate from index; privacy audit pipeline.  
- **1,000×:** Hierarchical spatial index; edge query caches; update aggregation per microcell; extreme densification.

### 1.5 Etc. (Constraints & Assumptions)

- Not designing full Messenger/Facebook app — only nearby subsystem.  
- Graph service provides friends / blocks (with caching).  
- Clients may lie about GPS — server must enforce policy and sanity.  
- “Nearby” is **opt-in**; default off or friends-only depending on product.  
- Distance UX prefers **buckets** over precise meters for non-close-friends.

**Scope statement to repeat back:**

> Design a large-scale nearby-users service: opt-in adaptive location updates into a sharded geo index, privacy-preserving precision, ACL-aware radius/kNN queries with ranking, and progressive scale through geo cells and hotspot splits—without building a full maps stack.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Location updates** | GPS→server | ~100K/s | ~1M/s | Ingest + index write |
| **Index writes** | Cell membership upsert | ~100K/s | ~1M/s | Geo store |
| **Nearby queries** | Radius/kNN | ~50K/s | ~500K/s | Query + rank |
| **Graph lookups** | Friends/blocks | amplified | cache | Graph cache |
| **Privacy/policy** | Quantize/ACL | on path | on path | Sync cheap |
| **Alerting (opt)** | Geofence | low | medium | Async |

**Anti-pattern:** treating updates and queries as one QPS number.

### 2.2 Update firehose math

```text
5M concurrent sharers
If every 10s update: 5e6 / 10 = 500K updates/s → above baseline; need adaptive policy

Adaptive example:
  moving fast: 15–30s
  slow/stationary: 2–5 min
  background: 5–15 min
Effective average interval ~60–120s → 5M/90 ≈ 55K u/s (plausible baseline)

Deal-breaker: fixed 1Hz updates for all opt-in users at Meta scale
```

### 2.3 Geo cell cardinality

```text
Earth land urban concentration: most queries in tiny fraction of cells
S2 / geohash level choosing ~1km cells:
  Active cells << total cells
Store: user_id -> (cell, lat_q, lng_q, ts, visibility, precision)

Dense cell (stadium): 50K users in one cell
  Query must not scan 50K blindly without caps / subcells
```

### 2.4 Query cost

```text
Radius 5km → cover ~O(10–30) cells depending on level
Each cell return top M by recency (e.g. 200)
Merge → candidate set C
Filter ACL → rank top K (20–50)

CPU: distance compute on C (haversine) cheap if C <= few thousand
Problem is oversized C in dense areas → subcells + early prune
```

### 2.5 Storage

```text
50M opt-in × 128 B index record ≈ 6.4 GB — tiny
Problem is write QPS + hot cells + query fanout, not raw GB
History trajectories: DO NOT store in MVP (privacy + cost)
```

### 2.6 Privacy quantization

```text
Raw GPS ~1–10m accuracy
Store/query at geohash length L equivalent to ~500m–1km for “friends of friends”
Close friends maybe finer (product)
Distance display: bucketed
Never return raw lat/lng of strangers to clients
```

### 2.7 Geohash / S2 level selection arithmetic

```text
Want cell ~1 km edge in mid-latitudes
Geohash length 6 ≈ 1.2 km × 0.6 km (order-of-mag)
S2 level 13–14 similar ballpark — pick one library and stick
Radius 5 km → cover cells ≈ πr² / cell_area ≈ 3.14*25 / ~0.7 ≈ ~100? too many
  → use coarser parent for cover then refine, or level with ~4–9 km² cells
Practical: cover 10–40 cells with ring padding, not hundreds
If cover > C_max: widen quantization / force cluster API
```

### 2.8 Shard map math

```text
Shard by hash(cell_id) or by S2 face/region ranges
Urban skew: top 1% cells hold huge user fraction
Dynamic split: cell → 4 children when cardinality > 5K active
Query fanout rises with children; cap recurse depth
```

### 2.9 Query radius cost curve

```text
r=1km:  small cover, friends OK
r=5km:  default product
r=25km: candidate explosion in cities → require friends-first or clusters
r=100km: map cluster mode only; no individual stranger pins
API enforces max radius by audience type
```

### 2.10 Update vs query ratio

```text
Baseline: ~100K updates/s vs ~50K queries/s
Index write must be O(1)/update (delete old cell + insert new if changed)
Cell-change rate: if 20% updates cross cell → 20K leave + 20K join/s
Stay-in-cell: in-place upsert LWW by ts only
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `PUT /v1/location` | Update location; client accuracy; mode foreground/bg |
| `POST /v1/nearby/query` | `{lat,lng,radius_m,limit,audience}` → ranked users |
| `GET /v1/nearby/map?bbox=` | Clustered pins for viewport |
| `PUT /v1/nearby/settings` | audience, ghost, precision preference (bounded) |
| `DELETE /v1/location` | Opt-out / clear |
| `POST /internal/reindex` | Repair |

**Location update schema:**

```text
LocationUpdate {
  user_id,
  lat, lng,           // client claim
  accuracy_m,
  client_ts,
  speed_mps?,
  mode: fg|bg,
  request_id
}
```

**Nearby result item:**

```text
NearbyUser {
  user_id,
  distance_bucket,
  last_active_bucket,
  mutual_friends_count?,
  // NO raw lat/lng for non-entitled viewers
  approx_point?,      // only if policy allows coarse pin
}
```

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| User location | `user_id` | quantized lat/lng, cell_id, ts, precision, audience |
| Cell index | `cell_id` → members | set/ZSET of user_ids by ts |
| Settings | `user_id` | ghost, audience, max_precision |
| Tombstone | `user_id` | opted_out_ts |
| Query cache | `geo_quota_key` | short TTL lists for popular tiles |

### 3.3 Geo index — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Geohash grid + neighbors** | Simple; good sharding | Boundary issues; fixed cells | Strong MVP |
| **S2 / H3 cells** | Better sphere math | Learning curve | **Preferred at scale** |
| Quadtree / R-tree single node | Flexible | Hard to shard | Small systems |
| Postgres `earthdistance` | Easy | Won’t scale write firehose alone | Prototype |
| Redis GEO | Convenient ops | Memory/hotspot limits | Medium / regional |
| Elasticsearch geo | Rich queries | Ops + cost | Secondary search |

**Chosen MVP:** **S2/H3 cell index** in a distributed KV (or Redis Cluster per region):

1. Map quantized lat/lng → `cell_id`.  
2. Upsert user into cell membership (ZSET score = last_ts).  
3. On move across cells: delete from old, add to new.  
4. Query: cover radius with cells (+ ring), fetch candidates, refine.

**Deal-breaker:** one global sorted array of all users by latitude scanned per request.

### 3.4 Update path

```text
PUT /location
  -> auth
  -> load settings (ghost? audience?)
  -> sanity: jump detection, accuracy floor
  -> quantize to policy precision
  -> compute cell_id
  -> LWW upsert user_location if client_ts/server_ts newer
  -> update cell index (remove old cell if changed)
  -> ACK
```

### 3.5 Query path

```text
POST /nearby/query
  -> auth + rate limit
  -> quantize querier location (don't need finer than policy)
  -> cells = cover(radius)
  -> candidates = ∪ topM(cell) by freshness
  -> filter: TTL, ghost, audience ACL, blocks, age policy
  -> compute distance on quantized points
  -> rank(distance, graph features, activity)
  -> bucket distances
  -> return K
```

### 3.6 Ranking

```text
score = w_d * dist_score
      + w_f * is_friend
      + w_m * mutual_friends_norm
      + w_a * recency_score
      - w_b * ignore_signals
```

Candidate generation is geo; ranking blends social graph.

### 3.7 Privacy controls — Why X over Y

| Control | Mechanism |
|---------|-----------|
| Opt-in | No index entry otherwise |
| Audience ACL | friends / FoF / list |
| Precision floor | server quantize |
| Ghost | remove from cell index immediately |
| Distance buckets | hide meters |
| Rate limit queries | anti-harvesting |
| No trajectory MVP | reduce stalking surface |

**Deal-breaker:** returning exact lat/lng of all nearby strangers to any client.

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Index | S2/H3 cells + KV | Shardable | Single R-tree server |
| Updates | Adaptive client + LWW | Battery + QPS | 1Hz global |
| Privacy | Quantize + ACL + buckets | Safety | Exact public GPS |
| Query | Cell cover → filter → rank | Scale | Haversine vs all users |
| Dense areas | Subcell split + caps | Hotspots | Unbounded cell scan |
| History | Don’t store MVP | Privacy/cost | Full breadcrumb DB |
| Shard key | cell_id (geo) | Query locality | Shard only by user_id |
| Radius | Product-capped by audience | Cost/privacy | Unlimited stranger pins |
| Map API | Clusters at low zoom | Payload | 10K pins one response |
| Ghost | Immediate cell delete | Safety | TTL eventual only |

**Expanded deal-breakers:**

1. **1Hz GPS for all sharers** — ingest melts; battery murder.  
2. **Raw stranger coordinates** — creepy + harvesting.  
3. **No stadium plan** — one cell scan dominates fleet CPU.  
4. **Ghost as best-effort TTL** — safety incident if ex still sees you.

---

## 4. Architecture Diagram

```text
  Mobile clients (adaptive location SDK)
           |
           | HTTPS
           v
  +------------------+
  | API Gateway      |
  | auth, ratelimit  |
  +--------+---------+
           |
           v
  +------------------+         +------------------+
  | Location Service |-------->| Settings / ACL   |
  | update + query  |         | ghost, audience  |
  +--------+---------+         +------------------+
           |
     +-----+--------------------------+
     |                                |
     v                                v
 +-----------+                  +----------------+
 | Geo Index |                  | User Location  |
 | cells→ZSET|                  | KV (LWW)       |
 | regional  |                  +----------------+
 +-----+-----+
       |
       v
 +----------------+     +------------------+
 | Ranker         |---->| Graph Cache      |
 | dist + social  |     | friends/blocks   |
 +----------------+     +------------------+

 Optional:
 Anomaly service <-- updates
 Tile cache <-- popular map queries
 Migration worker <-- cross-region moves
```

**Update path:**

```text
Client adaptive tick
  -> PUT /location
  -> sanity + quantize
  -> upsert KV
  -> cell add/remove
```

**Query path:**

```text
POST /nearby/query
  -> cover cells
  -> fetch candidates (capped)
  -> ACL + block filter
  -> rank + bucket
  -> respond
```

**Dense cell split:**

```text
If cell cardinality > T:
  split to children cells (finer S2 level)
  reindex members asynchronously
  queries use finer cover in that area
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **LWW per user location** — one latest winning update.  
2. **Ghost/opt-out is immediate** — user not returned after ACK of hide.  
3. **ACL is deny-by-default** for non-entitled audience.  
4. **Stored precision ≤ policy max** always.  
5. **Query never depends on client-supplied neighbor list**.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Geo index partial write (KV ok, cell fail) | Transactional outbox / repair reconciler |
| Regional cell overload | Shed updates (increase client interval); split cells |
| Graph cache stale blocks | Short TTL; safety-prefer fail closed on block miss if uncertain |
| Clock / teleport | Reject impossible jumps; quarantine |
| Query thundering herd on event | Tile result cache |

#### 5.1.3 Consistency

Nearby is **eventual**. A user may appear up to freshness SLO after moving.  
Ghost should be **stronger**: write path deletes cell membership before ACK when possible.

```text
ghost_on:
  settings.ghost = true
  remove from cell index
  clear or mark user_location hidden
  ACK
```

### 5.2 Scalability

#### 5.2.1 Sharding

| Shard key | Purpose |
|-----------|---------|
| `cell_id` | Index partitions by geography |
| `user_id` | User location record |
| Region/DC | Users typically query locally |

Avoid sharding nearby index only by `user_id` — queries are geographic.

#### 5.2.2 Hotspot stadium problem

```text
Problem: 80K people in one cell, all querying
Fixes:
  1) finer cells automatically
  2) candidate cap per cell with diverse sampling
  3) prefer friends subgraph first (intersect friends in bbox)
  4) short TTL tile cache for map clusters
  5) query rate limits per user
```

**Friends-first candidate gen (important Meta twist):**

```text
candidates = geo_candidates ∩ (friends ∪ FoF)   # if audience friends
OR geo_candidates filtered by audience for broader modes
```

For friends-only nearby, you can also:

```text
Fetch online/fresh friends' cells from friends' location store (batch)
Filter by distance
```

At large friend counts (5K), still need geo pruning.

#### 5.2.3 Adaptive update policy

| Context | Interval | Precision |
|---------|----------|-----------|
| Foreground moving | 15–30s | medium |
| Foreground still | 2–5 min | medium |
| Background | 5–15 min | coarse |
| Ghost / battery | pause | — |
| Significant movement API | event-driven | medium |

Server may return `next_update_sec` hint.

#### 5.2.4 Progressive scale

| Scale | Index | Updates | Queries |
|-------|-------|---------|---------|
| Baseline | Redis GEO/S2 per region | Adaptive | Cell cover |
| 10× | KV sharded by cell | Server backpressure hints | Graph cache |
| 100× | Dynamic cell split | Update aggregators | Tile cache + ranker |
| 1,000× | Hierarchical spatial | Microcell gossip | Edge caches |

### 5.3 Maintainability

#### 5.3.1 Components

| Component | Role |
|-----------|------|
| Location Service | API |
| Geo Index | Cell membership |
| Settings Service | Privacy knobs |
| Ranker | Blend features |
| Anomaly | Spoof detection |
| Reconciler | Repair cell/user drift |

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| Updates/s by region/cell | Hotspots |
| Impossible jump rate | Spoofing |
| Query p99 + candidate set size | Perf |
| ACL filter drop rate | Privacy correctness |
| Ghost apply latency | Safety SLO |
| Cell cardinality histogram | Split triggers |

#### 5.3.3 Privacy review hooks

- Log access patterns for harvesting detection (careful with logs themselves).  
- Differential query rate limits.  
- Regular precision audits.

### 5.4 Distance & cover math

```text
Haversine on quantized centers is OK for ranking
For cell cover: use library (S2 Cap / H3 ring)
Always pad by 1 ring to avoid boundary misses
radius_m effective = radius_m + quantization_error
```

### 5.5 Map clustering

```text
For bbox queries at low zoom:
  return clusters {cell_id, count, centroid_coarse}
Don’t return thousands of user pins
On zoom-in: fetch individuals (ACL applied)
```

### 5.6 Cross-region travel

```text
If user_location.region != cell.region:
  write new region index
  async delete from old
  queries in old may be stale briefly — OK within SLO
```

### 5.7 Security anti-harvesting

| Attack | Defense |
|--------|---------|
| Grid scraping queries | Rate limit; anomaly; CAPTCHA; legal |
| Sybil accounts | Trust scores |
| Precision attack via many queries | Quantize response; buckets; noise optional |
| Friend graph abuse | Same as social platform controls |

### 5.8 Geohash / S2 indexing deep dive

#### 5.8.1 Why cells beat raw R-tree at this QPS

```text
Updates are point upserts at 100K/s — cell KV / wide-column wins
Queries are radius covers — discrete cell fanout predictable
R-tree/PostGIS OK at smaller scale; harder to shard hot cities
```

#### 5.8.2 Index records

```text
user_location:
  user_id → {cell_id, lat_q, lng_q, ts, accuracy_m, visibility, precision_tier}

cell_members:
  cell_id → sorted set / list of (user_id, ts, coarse_rank_key)
  capped; overflow → subcells
```

#### 5.8.3 Cover algorithm

```text
1. Quantize query center to policy precision
2. Compute covering cells for radius + pad ring
3. Bound |cells| ≤ C_max else upgrade to cluster mode
4. Parallel fetch members with per-cell limit M
5. Merge → distance filter → ACL → rank → top K
```

#### 5.8.4 Boundary correctness

Users near edges must be found: always pad; distance filter removes false positives from pad.

### 5.9 Sharding deep dive

#### 5.9.1 Strategies

| Strategy | Pros | Cons |
|----------|------|------|
| hash(cell_id) | Simple | Adjacent cells scatter (OK) |
| Geo ranges (S2 Hilbert) | Locality for bbox | Hot urban ranges |
| Region cells (metro) | Isolation | Cross-metro travel |

**MVP:** hash(cell) + special casing for mega-cells via split.

#### 5.9.2 Hotspot stadium

```text
Detect cell cardinality > T
 → split to children
 → queries recurse children with tighter M
 → friends-first: retrieve friends in bbox from graph index first (small)
 → strangers sampled / clustered
```

#### 5.9.3 Consistency of membership

```text
Update txn/order:
  read old cell for user
  if cell changed: delete from old, insert new, update user_location
  LWW by client_ts/server_ts policy
Reconciler scans mismatches periodically
```

### 5.10 Privacy deep dive

#### 5.10.1 Precision tiers

| Audience | Stored precision |
|----------|------------------|
| Close friends | finer (e.g. ~100–200m) |
| Friends | ~500m–1km |
| Friends-of-friends | coarser |
| Public (if ever) | very coarse + clusters |

Server enforces max precision; client preference can only coarsen.

#### 5.10.2 Ghost / opt-out

```text
Ghost: immediate remove from cell_members + flag
SLO: invisible to new queries < few seconds global
In-flight responses may still include briefly — document
```

#### 5.10.3 Response shaping

```text
Return: user_id, display, distance_bucket, last_active_bucket
Never: raw lat/lng for non-self
Optional fuzz for stalking resistance
```

### 5.11 Update rates deep dive

#### 5.11.1 Adaptive policy

```text
interval = f(speed, battery, app_state, cell_density_hint)
server may send min_interval in response (backpressure)
Ignore updates that don't move > movement_threshold_m
```

#### 5.11.2 Spoof / teleport

```text
if distance(old,new)/Δt > v_max_human: reject or mark anomalous
don't update cell; challenge / degrade trust
```

### 5.12 Query radius product rules

| Audience | Max radius | Default |
|----------|------------|---------|
| Friends | 50km | 5km |
| FoF | 25km | 5km |
| Map browse | bbox zoom-limited | clusters |

### 5.13 Progressive scale (10× / 100× / 1,000×)

| Jump | Index | Updates | Queries |
|------|-------|---------|---------|
| →10× | Shard by cell | Adaptive enforced | Graph cache |
| →100× | Dynamic cell split | Aggregators / batch | Tile + ranker |
| →1,000× | Hierarchical spatial | Microcell gossip | Edge caches |

### 5.14 Failure drills

| Drill | Expected |
|-------|----------|
| Shard loss | Replica promote; brief stale nearby |
| Ghost lag | Alert on apply latency SLO burn |
| Stadium surge | Auto-split + cluster mode |
| Scraping anomaly | Rate limit + temporary captcha |

### 5.15 Worked query example

```text
User U at quantized (lat_q,lng_q), audience=friends, r=5km, limit=20
1. Load friend set F (|F|=400) from graph cache
2. Cover cells C for radius (18 cells)
3. For each cell: fetch members ∩ candidates; prefer F first
4. If friends-in-cover < 20, optionally add FoF per settings
5. Distance bucket + recency rank → top 20
6. Response omits raw coordinates; includes buckets only
Stadium variant: step 3 capped per cell; return clusters for overflow
```

### 5.16 Progressive scale narrative (long form)

- **→10×:** Adaptive updates enforced; cell sharding; graph cache on query path.  
- **→100×:** Dynamic cell split; tile caches; ranker service; anomaly/spoof.  
- **→1,000×:** Hierarchical spatial index; edge query caches; microcell gossip for dense venues — privacy floor unchanged.

---

## 6. Wrap-Up

### 6.1 Design summary

**Nearby users** is a geo-index + privacy product:

1. Adaptive location updates with LWW and sanity checks.  
2. S2/H3 cell index sharded by geography.  
3. Queries: cover → capped candidates → ACL/blocks → rank → distance buckets.  
4. Ghost/opt-out immediate; precision floor server-side.  
5. Dense hotspots via cell split, friends-first pruning, tile caches.  
6. Scale with regional geo cells and hierarchical indexes.

### 6.2 Key tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Freshness vs battery/QPS | Adaptive updates |
| Precision vs privacy | Quantize + buckets |
| Completeness vs latency | Candidate caps |
| Global index vs cells | Regional geo cells |

### 6.3 Deal-breakers

- Exact public GPS for strangers.  
- 1Hz updates for all users.  
- Scan-all-users haversine.  
- Ignoring dense-cell cardinality.  
- Storing full trajectories in MVP without extreme controls.

### 6.4 30-minute checklist

1. Clarify audience, radius, freshness, privacy.  
2. Estimate update firehose → adaptive policy.  
3. Draw update → quantize → cell index; query cover→rank.  
4. Dense stadium + friends-first.  
5. Ghost/ACL.  
6. 10×/100×/1,000×.  
7. Deal-breakers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & privacy

**Q1: Why bucket distances?**  
A: Reduces precision leakage and stalking UX; enough for social decisions.

**Q2: Friends-only vs public nearby?**  
A: Friends-only much smaller candidate sets and safer; public needs stronger anti-harvesting.

**Q3: Is Ghost mode different from opt-out?**  
A: Ghost is temporary hide; settings retained; opt-out clears sharing commitment.

**Q4: Should clients send exact GPS?**  
A: They may measure exact, but server stores/returns quantized; never trust client as source of truth for others’ precision.

**Q5: Minors?**  
A: Policy may disable or restrict to guardians/friends with coarser precision; often feature-gated.

### 7.2 Geo indexing

**Q6: Geohash vs S2 vs H3?**  
A: All fine if you handle neighbors; S2/H3 nicer on sphere and hierarchical splits. Pick one and know boundary rings.

**Q7: How do you handle users on cell edges?**  
A: Index by home cell; query covers neighboring cells; optionally duplicate into edge halo (costly).

**Q8: Redis GEOSEARCH enough?**  
A: Good MVP regionally; at 100× prefer KV cell membership with explicit control + dynamic split.

**Q9: Why not PostGIS only?**  
A: Harder to scale write firehose and multi-region; great for analytics/secondary.

**Q10: kNN vs radius?**  
A: Radius natural for maps; kNN needs expanding rings until K satisfied or cap.

### 7.3 Updates & freshness

**Q11: Last-write-wins with late packets?**  
A: Compare `client_ts` with skew bound; ignore ancient; prefer server_ts for ties.

**Q12: How to detect teleport spoofing?**  
A: max speed gate: distance/time > threshold → reject/quarantine.

**Q13: Battery impact?**  
A: Significant-change API, adaptive intervals, coarse bg precision — discuss as first-class.

**Q14: What if update arrives to wrong region?**  
A: Route by geo to owning cell; or write locally + forward; reconciler cleans.

**Q15: Do we need exactly-once updates?**  
A: No — LWW last location; idempotent upserts suffice.

### 7.4 Query & ranking

**Q16: Walk nearby query steps.**  
A: Cover cells → fetch capped members → freshness filter → ACL/blocks → distance → rank → bucket → return.

**Q17: Friends-first optimization?**  
A: Intersect geo candidates with friends set; or fetch friends’ locations in batch and filter by distance — excellent when audience is friends.

**Q18: Mutual friends expensive?**  
A: Precompute/cached counts; don’t BFS per candidate uncached at query p99.

**Q19: How to rank in a festival with 10K people?**  
A: Prioritize friends/FoF; sample others; cluster map; never return 10K rows.

**Q20: Caching queries?**  
A: Cache coarse tile clusters; personalize list less cacheable; cache graph features.

### 7.5 Scale & hotspots

**Q21: Stadium hotspot plan?**  
A: Split cells, cap candidates, friends-first, tile cache, query rate limits, update backpressure.

**Q22: Update aggregators at 1,000×?**  
A: Microcell leaders batch membership changes; users send to edge; edge aggregates still/moving.

**Q23: Memory of cell ZSETs?**  
A: Dominated by dense cells; bound membership with TTL eviction; inactive drop.

**Q24: Multi-region active-active?**  
A: Location home by current geo region; queries local; global user directory points to region.

**Q25: What breaks first?**  
A: Dense urban query fanout and update hotspots — not average storage GB.

### 7.6 Security & abuse

**Q26: Harvesting nearby users repeatedly?**  
A: Per-user query quotas; anomaly detection; reduce precision; legal/ToS; device trust.

**Q27: Can I triangulate with many observers?**  
A: Hard problem; precision floors + buckets + rate limits mitigate; assume determined attackers — minimize data.

**Q28: Fake GPS to enter private spaces?**  
A: Sanity + optionally trusted device signals; never grant physical access via this API alone.

**Q29: Block synchronization lag?**  
A: Prefer fail-safe: if block unknown, exclude; refresh caches aggressively for safety-critical edges.

**Q30: Logging locations?**  
A: Minimize; encrypt; short retention; separate from product index; compliance heavy.

### 7.7 Alternatives & deal-breakers

**Q31: Broadcast location to all friends continuously?**  
A: N² blowup; use pull query + optional rare push alerts instead.

**Q32: Store every location every second in OLAP?**  
A: Privacy nightmare and cost; not MVP nearby.

**Q33: Client-side only nearby via Bluetooth?**  
A: Different product (ambient discovery); doesn’t replace server geo for km-scale.

**Q34: Exact kNN worldwide?**  
A: Nonsense at scale; always bound radius/cells.

### 7.8 Interview craft

**Q35: How to open?**  
A: Opt-in audience, radius, freshness, privacy precision, update rate — then firehose math.

**Q36: Numbers that matter?**  
A: Concurrent sharers, update interval → u/s, query QPS, dense cell cardinality, candidate cap.

**Q37: L5+ impress?**  
A: Adaptive updates, quantization, cell split, friends-first, anti-harvesting, ghost immediacy.

**Q38: Common mistake?**  
A: Redis GEO demo without privacy or hotspot plan; or global scan jokes that become the design.

**Q39: Related systems?**  
A: Find My / Snap Map-like features; rideshare supply heatmaps differ (fleet vs people privacy).

**Q40: Push “friend nearby” notifications?**  
A: Geofence asynchronously; heavy debounce; friends-only; easy to get creepy — product caution.

**Q41: How does bbox map query differ from radius?**  
A: Cover cells in rectangle; cluster by cell at low zoom; same ACL filters.

**Q42: Consistency of distance shown to two users?**  
A: May differ slightly due to quantization and freshness; OK.

**Q43: Why server returns `next_update_sec`?**  
A: Closed-loop backpressure when cells hot or battery policy centralized.

**Q44: CRDT locations?**  
A: Overkill; LWW sufficient for single latest point.

**Q45: Online/offline presence vs location?**  
A: Related but distinct; presence may be WebSocket; location TTL overlaps but privacy differs.

---

### Appendix A — Quantization

```text
def quantize(lat, lng, precision_m):
  # snap to grid ~ precision_m
  return lat_q, lng_q, cell_id(lat_q, lng_q)
```

### Appendix B — Cell cover

```text
def cover(lat, lng, radius_m):
  cells = s2_cover(lat, lng, radius_m + pad)
  return cells
```

### Appendix C — LWW upsert

```text
def upsert(u, upd):
  cur = kv.get(u)
  if cur and not newer(upd, cur): return
  old_cell = cur.cell if cur else None
  new = quantize(...); new.cell = ...
  kv.put(u, new)
  if old_cell != new.cell:
    cell_rm(old_cell, u)
  cell_add(new.cell, u, new.ts)
```

### Appendix D — Query pseudocode

```text
def nearby(q):
  cells = cover(q.lat, q.lng, q.radius)
  cand = []
  for c in cells:
    cand += cell_top(c, M)
  cand = unique(cand)
  cand = filter_ttl_acl_blocks(cand, q.user)
  scored = rank(cand, q)
  return buckets(topK(scored))
```

### Appendix E — Velocity check

```text
if prev and dist(prev, new) / dt > MAX_SPEED * slack:
  anomaly(user); reject or coarse-only
```

### Appendix F — Distance buckets

```text
< 500m; 500m–1km; 1–2; 2–5; 5–10; 10+
```

### Appendix G — Adaptive interval

```text
if speed > 2 m/s: 20s
elif foreground: 120s
else: 600s
server may multiply by backpressure factor
```

### Appendix H — NFR card

```text
Query p99 < 200ms
Update lag < 60s typical
Ghost immediate
Precision floor enforced
No trajectory MVP
Dense cell split
```

### Appendix I — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Adaptive updates, graph cache |
| 100× | Dynamic split, tile cache, ranker |
| 1,000× | Hierarchical index, edge aggregates |

### Appendix J — Settings schema

```text
NearbySettings {
  enabled,
  audience: friends|fof|everyone_feature,
  ghost,
  max_precision_m,
  notifications_enabled
}
```

### Appendix K — Cluster response

```json
{
  "clusters": [{"cell": "...", "count": 120, "lat_q": 0, "lng_q": 0}],
  "users": []
}
```

### Appendix L — Sharding map

| Data | Shard |
|------|-------|
| user_location | user_id |
| cell_index | cell_id |
| settings | user_id |
| tile_cache | tile_id |

### Appendix M — Failure repair

```text
reconciler:
  for user in sample:
    if membership cells != user.cell:
      fix
```

### Appendix N — Worked example

```text
5M sharers, avg interval 100s → 50K upd/s
Query 50K/s × 20 cells × 100 members scanned = 100M membership touches/s worst
→ must cap M, cache tiles, friends-first reduce
```

### Appendix O — Comparison: friends-first vs geo-first

| | Friends-first | Geo-first |
|--|---------------|-----------|
| Audience friends | Excellent | OK |
| Public mode | Incomplete | Needed |
| Cost | Graph batch | Cell scan |
| Hybrid | **Best** | **Best** |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Cell | S2/H3/geohash region |
| Quantize | Snap/reduce precision |
| Ghost | Temporary hide |
| LWW | Last write wins |
| Cover | Cells intersecting radius/bbox |
| Tile | Map viewport cache key |

### Appendix Q — Related systems

| System | Relation |
|--------|----------|
| Graph service | Friends/blocks |
| Presence | Online signals |
| Push notif | Optional nearby alerts |
| Integrity | Spoof/spam |

### Appendix R — Creepiness checklist

```text
default friends-only?
bucket distances?
no trajectory?
rate limit queries?
ghost easy?
clear UX disclosure?
```

### Appendix S — API errors

| Code | Meaning |
|------|---------|
| 403 | Feature disabled / forbidden |
| 429 | Update or query rate |
| 422 | Impossible location / bad coords |
| 503 | Index degraded |

### Appendix T — Rank features

| Feature | Source |
|---------|--------|
| Distance | Geo |
| Is friend | Graph |
| Mutuals | Graph cache |
| Recency | last_ts |
| Affinity | Social ranker optional |

### Appendix U — Cell split trigger

```text
if cell.size > T for age > X:
  split to children
  migrate members
  mark parent as redirect
```

### Appendix V — 30m checklist compact

```text
Privacy → Firehose math → Cell index → Query cover
→ Stadium → Ghost → Scale jumps → Deal-breakers
```

---

*End of Large-Scale Nearby Users system design.*
