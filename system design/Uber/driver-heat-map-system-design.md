# System Design: Driver Heat-Map Analytics Dashboard

> **Focus areas:** Location stream ingest · H3 geo aggregation · Internal analytics privacy · Vector tile rendering · Freshness vs accuracy · Downsampling · Kafka · Flink/streaming aggregates · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar load classes (raw pings vs tile reads vs dashboard queries), explicit privacy invariants, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — turn high-volume driver GPS streams into an **internal operations heat-map dashboard** for supply visibility, planning, and incident response—not rider-facing maps or dispatch

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

Goal: **bound the product**—the heat map is *not* the whole Uber mobility stack. It is the subsystem that **ingests driver location events**, **aggregates them in geo-time buckets**, and **serves a low-latency internal dashboard** showing supply density, movement patterns, and anomalies—without exposing raw driver PII to unauthorized users.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Aggregate location stream → H3 heat tiles → internal dashboard | Rider-facing live map |
| Users | Ops, city managers, data analysts, incident response | Public internet |
| Location truth | Analytics snapshot with bounded staleness | Millisecond-fresh dispatch supply index |
| Privacy | Internal RBAC, no public API, aggregated counts | Driver identity lookup by default |
| Scope | Heat density, trends, compare windows | Full matching / pricing / trip lifecycle |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who consumes the heat map? | Internal Uber teams (ops, planning, SEV) via web dashboard | SSO/RBAC; audit every query |
| F2 | Data source? | Existing driver location ping stream (same as dispatch ingest) | Tap Kafka topic; don't duplicate mobile ingest |
| F3 | What is visualized? | Driver count / density per geo cell over time | H3 aggregation; optional status/product filters |
| F4 | Time windows? | Last 5m, 15m, 1h, 24h; scrubber / replay | Rolling tumbling/sliding windows |
| F5 | Zoom levels? | City → neighborhood → block | Multi-resolution H3 parent rollup |
| F6 | Filters? | City, product (UberX, Eats courier), online status | Dimension tags on events; pre-agg or filter-at-query |
| F7 | Compare mode? | Today vs last week same hour | Store historical rollups; time-shift query |
| F8 | Tile format? | Map overlay on internal basemap | MVT/PNG heat tiles or GeoJSON for MVP |
| F9 | Refresh rate? | Near-real-time (30–60s) for ops; slower OK for planning | Separate freshness tiers |
| F10 | Historical backfill? | Recompute from cold archive when logic changes | Batch Flink on object storage |
| F11 | Alerts? | Optional spike/drop in cell vs baseline | Side channel to monitoring; not core MVP |
| F12 | Export? | CSV/Parquet for analysts | Async export job; row-level access controls |

**MVP functional scope (lock with interviewer):**

1. **Ingest** driver location events from shared Kafka topic (read-only consumer group).
2. **Aggregate** counts per H3 cell at resolutions 7–9 with 1-minute tumbling windows.
3. **Roll up** parent H3 cells for low-zoom dashboard views.
4. **Serve** heat tiles / cell counts via internal API with city + time window params.
5. **Render** internal web dashboard with pan/zoom, time scrubber, basic filters (city, product).
6. **Privacy:** no driver IDs in API responses; RBAC on city access; audit logs.
7. Metrics: ingest lag, tile build latency, dashboard p99.

**Out of MVP (explicitly defer):**

- Sub-second rider-map freshness
- Individual driver drill-down (requires elevated break-glass role + separate service)
- Global active-active tile writes without home-region partitioning
- ML anomaly detection as hard dependency
- Perfect count accuracy at every zoom (approximate OK at extreme scale)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Dashboard tile latency? | Feels interactive when panning | p50 < 200ms, p99 < 1s in-region |
| N2 | Data freshness? | "Good enough for ops" | End-to-end lag p99 < 60s (baseline); < 30s stretch |
| N3 | Accuracy vs cost? | Aggregated counts ± small error OK at 100× | Exact at cell level baseline; HyperLogLog/ sampling at 1000× |
| N4 | Availability? | Internal tool; degrade gracefully | 99.9% dashboard read; stale tiles OK briefly |
| N5 | Throughput? | See scale table | Split **ping ingest**, **agg writes**, **tile reads** |
| N6 | Privacy / compliance? | Internal only; GDPR minimization | Aggregates only; TTL on raw; no export of driver_id |
| N7 | Durability of aggregates? | Rebuild from stream if needed | Kafka retention + object storage archive |
| N8 | Multi-tenant RBAC? | City/region scoped roles | Enforce at API + storage partition |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Driver pings → Kafka → Flink counts per H3 res-9 / 1m window → tile store → dashboard fetches tile for viewport → heat overlay renders.
2. User zooms out → API returns parent H3 resolution (res-7) pre-aggregated counts → fewer cells, faster paint.
3. User selects "last 15 minutes" → server sums rolling 15×1m buckets or serves pre-merged sliding window.
4. Ops compares Friday 6pm vs prior Friday → time-shift query on stored hourly rollups.
5. New city launch → enable consumer for city partition; empty tiles until data flows.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Late-arriving ping (event-time lag) | Watermark allows lateness window (e.g. 2–5m); update bucket or drop if too late |
| Duplicate ping (retry) | Idempotent `(driver_id, seq)` dedupe in stream or count driver once per window via state |
| GPS jump / bad accuracy | Filter accuracy > threshold; optional fraud quarantine stream |
| Hot downtown cell (millions pings/min) | Local combiner; count-min sketch; shard Flink subtask by H3 prefix |
| Flink job restart | Restore from checkpoint; at-least-once → idempotent upsert to tile store |
| User pans across city boundary | Fetch adjacent tiles; CDN cache by `(city,z,res,window)` |
| Stadium event spike | Pre-warm tiles; temporary finer resolution in geofence config |
| Privacy: analyst without city ACL | 403; no data leakage via tile URLs (signed, short TTL) |
| Backfill after H3 logic change | Batch job replays archive → new aggregate tables; blue/green tile version |
| Kafka retention expired | Historical windows served from S3/Parquet rollups only |
| Downsampled mode under load | Serve coarser resolution + "approximate" badge |
| Clock skew on device | Use server ingest time for window assignment if device_ts unreliable |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Cities / regions | 50 | 500 | multi-region global | extreme global |
| Online drivers (peak) | 100K | 1M | 10M | 100M |
| Location pings / s (global) | 50K | 500K | 5M | 50M |
| Distinct H3 cells/min (res-9, active) | ~50K | ~500K | ~5M | ~50M |
| 1m window updates / s (cell buckets) | ~1K | ~10K | ~100K | ~1M |
| Dashboard concurrent users | 200 | 2K | 20K | 200K |
| Tile requests / s (peak) | ~500 | ~5K | ~50K | ~500K |
| Aggregate storage (hot, 24h) | ~10 GB | ~100 GB | ~1 TB | ~10 TB |
| End-to-end freshness target | 60s | 45s | 30s | 30s (approx tier) |

**What each jump forces:**

- **10×:** Dedicated Flink job per region; tile cache (Redis/CDN); H3 parent rollups materialized.
- **100×:** Approximate distinct counting; ping sampling for analytics path; pre-render popular tiles.
- **1,000×:** Hierarchical aggregation tree; edge combiners; separate exact vs approximate serving tiers; aggressive downsampling default.

### 1.5 Scope repeat-back

> Design an **internal** driver heat-map system: consume location stream from Kafka, aggregate driver density in H3 cells with streaming windows, serve vector/raster tiles to an authenticated dashboard—with privacy (aggregates only), freshness vs accuracy trade-offs, downsampling at scale, and progressive architecture from ~50K pings/s to 50M pings/s. Not dispatch matching or rider maps.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Raw location pings (read) | 50K/s | 50M/s | Consumer group; don't write each ping to tile DB |
| Streaming aggregations | ~1K cell-updates/s | ~1M/s | After combiner; dominates write path |
| Tile / cell API reads | 500/s | 500K/s | Dashboard pan/zoom; cache heavily |
| Historical batch recompute | rare | weekly | Off hot path |
| Export jobs | ~10/day | ~1K/day | Async; object storage |

**Critical insight:** At scale, **raw ping volume ≫ tile read QPS**, but **aggregation write amplification** matters if you update one DB row per ping per cell. Always **pre-aggregate in stream** before touching serving store.

### 2.2 Ping math

```text
Baseline: 100K online drivers × (1 ping / 2s) = 50K pings/s

Payload ~100–200 B on wire → 50K × 150 B ≈ 7.5 MB/s Kafka ingress (one region cluster)

1,000×: 100M drivers × 0.5 ping/s = 50M pings/s
50M × 150 B ≈ 7.5 GB/s → must be multi-region Kafka + co-located Flink + sampling
```

**Analytics sampling (100×+):** Process 1-in-N pings for heat map only (dispatch still uses full stream). Cuts Flink state 10× with documented accuracy bounds.

### 2.3 H3 cell cardinality

```text
Res-9 hex edge ~174 m → dense city may have 10K–100K active cells/min
Each cell × 1m window × (count, metadata) ≈ 32–64 B in hot store

50K active cells × 64 B ≈ 3.2 MB per minute slice (trivial)
5M active cells × 64 B ≈ 320 MB/min → need partitioned tile store + rollup

Parent res-7: ~1/49 of res-9 cells (H3 parent fan-in) → fewer keys at low zoom
```

### 2.4 Tile storage math

```text
Tile key: (city_id, h3_res, window_start, layer)
Baseline 50 cities × 3 resolutions × 60 windows/hour × 24h ≈ 216K keys/day hot
Each tile ~2–20 KB (MVT) → ~4 GB/day hot cache working set

100× cities + finer geofences → CDN + object storage for warm tiles
```

### 2.5 Flink state

```text
Per-key state for 1m tumbling count (exact):
active drivers in window could use HyperLogLog ~12 KB or driver_id bitmap (too heavy)

Better: count pings with local combiner OR HyperLogLog for distinct drivers
1M concurrent H3 keys × 128 B state ≈ 128 MB per subtask (manageable withrocksdb)

1,000×: 100M keys without rollup → TB state → MUST hierarchical aggregate + sampling
```

### 2.6 Latency budget (ping → visible tile)

```text
Kafka publish → consumer           5–20ms
Flink window + watermark hold      0–60s (product choice)
Aggregate flush to tile store        50–200ms
Tile API + CDN                       20–100ms
Browser render                       50–200ms
------------------------------------
Typical ops view: 30–90s after event (baseline)
```

**Deal-breaker for "instant" ops map:** Waiting for 1m window close *and* 5m watermark on every ping.

### 2.7 Bottlenecks (rank ordered)

1. **Per-ping OLTP writes** to tile database  
2. **Hot H3 cells** (stadium, airport) skew Flink subtasks  
3. **Unbounded state** for distinct driver counts per cell per day  
4. **Serving raw driver locations** to dashboard (privacy + bandwidth)  
5. **Global single Redis** for all tile keys  
6. **Re-aggregation on every pan** without pre-materialized tiles  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
LocationEvent   — driver ping on Kafka (read-only for this system)
GeoBucket       — (h3_cell, window_start, resolution, dims) → metric value
Tile            — pre-rendered map fragment for viewport + zoom + time
Rollup          — parent H3 aggregation for coarser zoom levels
DashboardQuery  — authenticated request for tiles/cells in bbox + time range
```

**Data flow (logical):**

```text
LocationEvent → validate/filter → assign h3_index →
  stream aggregate (1m windows) → merge to GeoBucket store →
  optional tile renderer → CDN → Dashboard
```

### 3.2 Ingest: tap, don't duplicate

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Mobile → heat-map API | Simple mentally | Duplicates dispatch ingest | Any real Uber scale |
| B. Kafka consumer on `driver.locations` | Single source of truth | Must handle skew | N/A — **default** |
| C. DB poll on location table | Easy prototype | Can't keep up at 50K/s | Baseline interview wrong path |
| D. S3 batch only | Cheap | Not near-real-time | Ops dashboard requirement |

**Chosen path:** **Kafka consumer group** `heat-map-aggregators` reading the same topic as dispatch (or compacted derived topic). Partition by `city_id|h3_prefix` for locality.

### 3.3 Geo aggregation: H3

| Resolution | Edge (approx) | Dashboard use |
|------------|---------------|---------------|
| 5 | ~8 km | Country/metro overview |
| 6 | ~3 km | Metro supply overview |
| 7 | ~1.2 km | City district |
| 8 | ~460 m | Neighborhood default |
| 9 | ~174 m | Dense downtown / zoomed in |
| 10 | ~66 m | Usually too chatty for heat map |

**Aggregation ops:**

```text
1. Parse lat/lng → h3_res9 = geoToH3(lat,lng,9)
2. Increment count for (h3_res9, window)
3. Async rollup to res8,res7 via H3ToParent
```

**Why H3 over geohash:** Uniform-ish hex shapes, easy parent rollup, Uber-native, k-ring for neighborhood context in drill-down tools.

### 3.4 Streaming engine: Flink aggregates

**Window type:**

| Window | Use |
|--------|-----|
| Tumbling 1m | Primary bucket for ops |
| Sliding 15m (step 1m) | "Last 15 min" view — or compute at query from 1m buckets |
| Daily rollup job | Compare week-over-week |

**Event time + watermarks:**

```text
event_ts = coalesce(device_ts_clamped, ingest_ts)
watermark = max_event_ts - allowed_lateness (e.g. 2m baseline, 5m global)

On window close: emit GeoBucket; late events within lateness update bucket (retraction or upsert)
```

**KeyBy:** `city_id + h3_cell + dim_hash` to spread hot cities.

**Local combiner:** `aggregateByKey` with in-memory counters before checkpoint flush.

### 3.5 Freshness vs accuracy trade-offs

| Mode | Freshness | Accuracy | When |
|------|-----------|----------|------|
| Exact 1m tumbling | ~60s lag | Exact counts | Baseline / dense audit |
| Partial window preview | ~5–10s | Under-count until close | "Live preview" layer |
| Sampled pings (1:10) | Same | ±√N error | 100× cost control |
| HyperLogLog distinct | ~60s | ~1–2% error | Distinct driver density |
| Count-min sketch | ~60s | Upper bound bias | Heavy hitter cells |

**Product pattern:** Show **two layers** — fast approximate preview + authoritative 1m layer (slightly stale).

**Deal-breaker:** Claiming exact distinct drivers per cell per minute at 50M pings/s without approximation.

### 3.6 Downsampling strategy

```text
Level 1: Client ping rate (dispatch owns; analytics may sample tagged subset)
Level 2: Stream sample (hash(driver_id) % N == 0)
Level 3: Coarser H3 at low zoom (always serve parent cells)
Level 4: Temporal downsampling (store 1m hot, 5m warm, 1h cold)
Level 5: Top-K cells only for anomaly alerts (ignore long tail zeros)
```

### 3.7 Tile rendering vs raw cell API

| Approach | Pros | Cons | MVP |
|----------|------|------|-----|
| A. JSON cell list for bbox | Simple | Heavy payload large bbox | ✓ MVP |
| B. MVT vector tiles | Mapbox-native, compact | Pipeline complexity | Phase 2 |
| C. Pre-rendered PNG heat | Easy CDN | Fixed style | Optional |
| D. Client-side heat from cells | Flexible | Moves compute to browser | OK for internal |

**Chosen path:** MVP **GeoJSON/cell API**; scale path **MVT tiles** pre-rendered on bucket close.

### 3.8 Privacy (internal)

```text
Invariants:
- Heat-map API returns (h3_cell, count, optional normalized intensity) — NO driver_id
- RBAC: user.scopes includes city_id
- Signed tile URLs (TTL 5–15 min); no guessable sequential IDs
- Audit: log (user, bbox, time, cells_returned)
- Raw stream access: separate break-glass role + justification ticket
- Retention: 1m buckets 7–30d; raw pings per company policy (not owned here)
- Aggregates ≥ k-anonymity threshold: suppress cell if count < 5 (configurable)
```

**Deal-breaker:** Dashboard click → list driver names in cell without elevated audit.

### 3.9 Serving store

| Store | Role |
|-------|------|
| Redis / DynamoDB | Hot current windows (last 1–2h) |
| ClickHouse / Druid / Pinot | Analytics queries, compare windows |
| S3 + Parquet | Cold archive, backfill |
| CDN | Immutable rendered tiles |

**Write pattern:** Idempotent upsert `(cell, window) → count` from Flink sink.

**Read pattern:** Tile API queries by `(city, res, time_range, bbox)` → merge cells → return.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Ingest | Kafka consumer | Scale + replay | Direct DB scrape |
| Geo | H3 multi-res | Parent rollup | Lat/lng brute bucket |
| Stream | Flink event-time | Watermarks/lateness | Cron batch only |
| Counts | Exact → HLL at scale | Cost | Store every ping row |
| Serving | Pre-agg buckets | Read cheap | Scan raw pings per pan |
| Privacy | Aggregates + RBAC | Compliance | Return driver pins |
| Preview | Partial window | Freshness | Block UI until 1m close |
| Tiles | MVT + CDN | Pan/zoom perf | Return 1M JSON points |

### 3.11 Coupling to siblings

| Sibling | Interaction |
|---------|-------------|
| Driver location tracking | Produces Kafka topic we consume |
| Rider–driver matching | Same ping stream; not on our critical path |
| Surge / pricing | May consume our aggregates async (supply density) |
| Dispatch supply index | Separate hot Redis; fresher than heat map |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Driver App                Location Ingest (sibling)
      |                              |
      |  pings                       v
      |                      +----------------+
      |                      | Kafka          |
      |                      | driver.locations|
      +--------------------->| (partitioned)  |
                               +-------+--------+
                                       |
                    +------------------+------------------+
                    |                  |                  |
                    v                  v                  v
            +---------------+  +---------------+  +---------------+
            | Dispatch /    |  | Flink Heat    |  | Cold Archive  |
            | Matching      |  | Aggregator    |  | (S3/Parquet)  |
            | (hot supply)  |  +-------+-------+  +---------------+
            +---------------+          |
                                       v
                               +---------------+
                               | GeoBucket     |
                               | Store         |
                               | Redis/CH/Pinot|
                               +-------+-------+
                                       |
                               +-------+-------+
                               | Tile Builder  |
                               | (MVT optional)|
                               +-------+-------+
                                       |
                                       v
                               +---------------+
                               | CDN / API     |
                               +-------+-------+
                                       |
                                       v
                               +---------------+
                               | Internal      |
                               | Heat-Map UI   |
                               | (SSO/RBAC)    |
                               +---------------+
```

### 4.2 Sequence: ping to tile

```text
Ping        Kafka       Flink           BucketStore     TileAPI      Dashboard
 |--loc----->|            |                  |              |             |
 |           |--event--->|                  |              |             |
 |           |            |--window agg---->|              |             |
 |           |            | (watermark)      |              |             |
 |           |            |--upsert count--->|              |             |
 |           |            |                  |              |             |
 |           |            |                  |<--get bbox---|             |
 |           |            |                  |--cells------>|             |
 |           |            |                  |              |--render---->|
```

### 4.3 Sequence: zoom level change

```text
User zoom out → Dashboard requests res=7 instead of res=9
TileAPI → fetch parent rollups (pre-materialized) OR sum children server-side
Return fewer polygons → faster paint
```

### 4.4 Sequence: late event handling

```text
Event ts=T (within lateness) arrives at T+90s
Flink: update bucket (T window) via allowedLateness side output OR retractions
BucketStore: idempotent upsert with version/window_seq
Dashboard: optional subtle "correcting" indicator; suppress if k-anonymity broken
```

### 4.5 Regional topology

```text
                    Global SSO / Dashboard CDN
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
   Region US              Region EU             Region APAC
   Kafka + Flink           Kafka + Flink         Kafka + Flink
   Bucket shard            Bucket shard          Bucket shard
        |                     |                     |
        +---------------------+---------------------+
                              |
                    Federated query router
                    (user city → home region)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Read-only ingest:** Never block dispatch path; consumer lag is our problem.  
2. **Idempotent sink writes:** `(h3_cell, window_start, res, dims)` upsert safe under at-least-once Flink.  
3. **Event-time correctness:** Watermarks + lateness; document max correction delay.  
4. **Privacy floor:** Suppress cells with count < k.  
5. **RBAC enforced server-side:** Never rely on client-side city filter alone.  
6. **Checkpoint recovery:** Flink restores window state; sinks reconcile via upsert.  
7. **Tile immutability:** Published tile for closed window is immutable; corrections bump `version`.  
8. **No driver PII in aggregate tables.**  
9. **Consumer group isolation:** Heat-map lag doesn't steal partitions from critical consumers (separate group).  
10. **Backfill reproducibility:** Versioned aggregation logic (`agg_version` in bucket metadata).

### 5.2 Scalability

| Scale | Architecture moves |
|-------|--------------------|
| 1× | Single Flink job; Redis buckets; GeoJSON API; 1m exact counts |
| 10× | Regional Flink; parent rollups async; CDN tile cache; ClickHouse for history |
| 100× | Ping sampling; HyperLogLog option; dedicated tile builder fleet; hotspot cell sharding |
| 1000× | Hierarchical aggregation tree; approximate default tier; pre-render top metros; edge combiners |

### 5.3 Maintainability

- **Aggregation config as code:** resolutions, windows, k-anonymity, sample rate per city.  
- **Blue/green agg version:** Run v2 job shadow; compare counts; cutover.  
- **Dashboard feature flags:** preview layer, compare mode.  
- **Runbooks:** consumer lag, Flink checkpoint failure, tile stale SEV.  
- **Contract tests:** H3 parent sum ≈ child sum (within filter effects).

### 5.4 Progressive scale playbook

**Baseline (50K pings/s):**

- One Flink job per region; Kafka partitions = 48–96.  
- Tumbling 1m exact counts (ping-weighted or distinct via small state).  
- Redis hash: `cell:window → count`, TTL 48h.  
- Internal React map; GeoJSON polygons from H3 boundary API.

**10× (500K pings/s):**

- Scale Flink parallelism = partition count; rocksdb incremental checkpoints.  
- Materialize res-7/8 rollups on each 1m close.  
- Tile builder writes MVT to S3; CloudFront in front.  
- ClickHouse for "compare last week" queries.

**100× (5M pings/s):**

- Analytics sample rate 1:5–1:10 (configurable per city).  
- HyperLogLog for "unique drivers" layer.  
- Hot cell detection → auto coarsen resolution in preview layer.  
- Separate **exact** job for compliance cities (small subset).

**1,000× (50M pings/s):**

- **Two-tier pipeline:** edge combiner (count per cell per 10s) → regional Flink (1m merge).  
- Default dashboard = approximate; exact drill-down async job.  
- Global partition by `h3_prefix|city` into 10K+ Flink subtasks.  
- Aggressive CDN pre-warm for top 100 viewports.

### 5.5 H3 aggregation deep dive

**Parent rollup correctness:**

```text
For count of pings: parent_count = SUM(child_counts)
For distinct drivers: parent_distinct ≠ SUM(child_distinct); use HLL merge at parent
```

**Boundary effects:** Driver on hex edge appears in one res-9 cell; parent rollup still correct. k-ring **not** needed for heat density (unlike dispatch).

**Cell suppression (k-anonymity):**

```text
if count < K: return null or coarsen to parent until count >= K or res_min reached
```

### 5.6 Flink implementation sketch

```text
stream
  .assignTimestampsAndWatermarks(event_ts, lateness=2min)
  .keyBy(city, h3_res9, product)
  .window(TumblingEventTimeWindows.of(Time.minutes(1)))
  .allowedLateness(2.minutes)
  .aggregate(CountAggregator)  // or HLL
  .addSink(IdempotentBucketSink)
```

**Side output for very-late events:** route to batch correction job.

### 5.7 Tile rendering pipeline

```text
On window close for city C:
  1. Read all cells res=R for window W
  2. Normalize intensity: log scale or percentile clip (p99 cap)
  3. Generate MVT layers OR heat PNG
  4. Upload s3://tiles/{city}/{R}/{W}/{x}/{y}.mvt
  5. Invalidate CDN surrogate keys
```

**Intensity normalization:** Raw counts skewed by downtown; use **per-city percentile** for color scale consistency.

### 5.8 Freshness vs accuracy product modes

| Layer | Update cadence | Data |
|-------|----------------|------|
| Live preview | 5–10s | Partial current window, sampled |
| Standard | 1m | Closed tumbling window |
| Historical | 5m/1h | Batch compacted |

UI badge: "Standard data through 12:04 UTC (45s ago)".

### 5.9 Failure modes & degradations

| Failure | Degrade |
|---------|---------|
| Flink lagging | Show stale timestamp; extend cache TTL |
| Redis hot shard down | Serve previous window tiles; alert |
| Kafka replay storm | Throttle sink; scale Flink |
| CDN miss | Origin tile API slower; still functional |
| Sampling enabled | Show "approximate" ribbon |
| RBAC service down | Fail closed (503) |

### 5.10 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Write DB row per ping | Storage + write death |
| No watermarks | Silent wrong windows |
| Return driver lat/lng in API | Privacy SEV |
| Single global Flink job | Checkpoint + skew failure |
| Recompute heat from scratch on pan | Latency death |
| Exact distinct at 50M/s | State explosion |
| Public unauthenticated tile URL | Data leak |

---

## 6. Wrap-Up

### 6.1 Designed

Internal driver heat-map: Kafka ingest, Flink H3 aggregation with event-time windows, freshness/accuracy tiers, downsampling, tile/cell serving store, RBAC dashboard—scaling from 50K to 50M pings/s.

### 6.2 Decisions to defend

1. **Tap Kafka** — don't duplicate mobile ingest  
2. **H3 multi-resolution** with parent rollups  
3. **Stream pre-aggregate** before serving store  
4. **Event-time + watermarks** for correct windows  
5. **Privacy:** aggregates only, k-anonymity, audit  
6. **Two-layer freshness** (preview + authoritative)  
7. **Approximation path** at 100×+ (HLL, sampling)  
8. **Regional isolation** with federated dashboard queries  

### 6.3 Risks

- Hot cell skew in Flink  
- Late data correcting visible tiles (ops confusion)  
- Sampling vs exact expectations mismatch  
- Parent/child distinct count semantics  
- Internal tool still a sensitive data surface (RBAC bugs)

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: internal analytics vs dispatch map |
| 5–12 | Estimates: pings vs cell updates vs tile reads |
| 12–22 | HLD: Kafka → Flink → H3 → store → tiles |
| 22–32 | Freshness vs accuracy, privacy, downsampling |
| 32–40 | Diagram + scale 10×/100×/1000× |
| 40–45 | Deal-breakers, sibling boundaries |

### 6.5 Closer

> **Driver heat map**: consume the location stream, **aggregate in H3** with streaming windows, trade freshness vs accuracy with preview layers, **downsample** at scale, serve **tiles to an internal RBAC dashboard**—never put raw pings on the read path or expose driver identity by default.

---

## 7. Deeper / Related Interview Questions

### 7.1 Stream processing

**Q: Kafka vs Flink vs Spark Streaming?**  
A: Kafka = transport; Flink = continuous event-time windows with low latency; Spark micro-batch OK for minutes+ latency. Heat map ops dashboard → Flink.

**Q: Why event time not processing time?**  
A: Mobile delays; processing time skews windows during lag spikes.

**Q: Allowed lateness vs watermark?**  
A: Watermark = progress; lateness = how long to accept updates to closed windows.

**Q: Exactly-once?**  
A: Flink EOS to sink with transactional/idempotent upsert; counts should be correct after reconciliation.

### 7.2 H3 / geo

**Q: H3 vs geohash vs S2 for heat maps?**  
A: H3 hex shapes look better for heat; easy parent rollup; geohash rectangular artifacts; S2 also fine.

**Q: Which resolution at zoom 12?**  
A: Map zoom → pick res via table; precompute mapping.

**Q: Distinct drivers vs ping counts?**  
A: Pings show activity intensity; distinct shows supply headcount; distinct needs HLL or state.

### 7.3 Privacy

**Q: Is aggregated heat map PII?**  
A: Can be sensitive in sparse areas; apply k-anonymity + internal-only + audit.

**Q: Can ops drill to drivers?**  
A: Separate break-glass tool with justification; not default heat-map click.

### 7.4 Tiles & rendering

**Q: MVT vs heat PNG?**  
A: MVT scalable styling; PNG simpler but fixed. Internal Mapbox → MVT.

**Q: CDN cache key?**  
A: `(city, res, window, layer, agg_version)` — immutable once window closed.

### 7.5 Freshness vs accuracy

**Q: 5s freshness requirement?**  
A: Partial window + sampled stream; label approximate; don't fake exact.

**Q: How to preview current minute?**  
A: Emit rolling partial aggregates every 5s from in-flight window state.

### 7.6 Downsampling

**Q: Sample pings or cells?**  
A: Sample pings (hash driver_id) for global accuracy; drop long-tail rural cells at low zoom.

**Q: Bias from sampling?**  
A: Uniform hash sampling unbiased for counts; document confidence interval.

### 7.7 Storage

**Q: Redis vs ClickHouse vs Pinot?**  
A: Redis hot last hour; OLAP for historical compare; Pinot/Druid for sub-second slice dashboards at scale.

**Q: How long retain 1m buckets?**  
A: 7–30d hot; roll to 5m/1h forever in cold store.

### 7.8 Scale

**Q: 50M pings/s Flink state?**  
A: Edge pre-aggregate; HLL; hierarchical; can't keep per-driver bitmap per cell.

**Q: Hot key downtown?**  
A: Custom partitioner; local combiner; split pseudo-cells only if desperate (rare for heat).

### 7.9 Reliability

**Q: Flink fails mid-window?**  
A: Checkpoint restore; reprocess Kafka from checkpoint offset; idempotent sink.

**Q: Duplicate Kafka messages?**  
A: Dedupe by `(driver_id, seq)` in Flink state OR count pings idempotently with seq set (expensive).

### 7.10 Product / ops

**Q: Heat map vs supply index?**  
A: Supply index = fresh dispatch (Redis, seconds); heat map = aggregated analytics (minutes, historical).

**Q: Use for surge?**  
A: Async signal of density imbalance; not sole surge input.

### 7.11 Algorithms & data structures

**Q: Count-min sketch use?**  
A: Heavy hitter cells; approximate frequency; not primary exact counter.

**Q: HyperLogLog merge for parent cell?**  
A: Merge HLL registers from children for approximate distinct at parent.

**Q: Top-K hottest cells?**  
A: Heap of size K per city per window for alerting — sibling to full tile render.

### 7.12 Interview traps

| Trap | Pushback |
|------|----------|
| Store every ping in Postgres | Won't scale |
| Poll drivers for heat map | Wrong direction |
| Show driver dots on internal map by default | Privacy |
| No watermarks | Wrong windows |
| One resolution globally | Bad UX zoom |
| Block dispatch on heat-map lag | Separate consumer group |

### 7.13 Metrics

| Metric | Why |
|--------|-----|
| Consumer lag | Freshness |
| Flink checkpoint duration | Recovery risk |
| Window emit delay | SLA |
| Tile API p99 | UX |
| Cell suppression rate | Privacy tuning |
| Sample rate / error estimate | Accuracy trust |
| Hot cell skew | Flink rebalance |

### 7.14 Comparison

**Q: vs driver location tracking sibling?**  
A: Sibling owns ingest + current location; we consume stream for aggregates.

**Q: vs Google Maps traffic layer?**  
A: Similar tile aggregation pattern; we're supply density not road speeds.

**Q: vs crime heat maps?**  
A: Similar k-anonymity concerns; we're real-time streaming not batch daily.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- geo_buckets (ClickHouse / Pinot / DynamoDB item)
(city_id TEXT,
 h3_index BIGINT,
 resolution SMALLINT,
 window_start TIMESTAMPTZ,
 window_size_sec INT,
 product_type TEXT,
 metric_type TEXT,  -- 'ping_count' | 'unique_drivers_hll'
 metric_value BIGINT,
 hll_state BLOB NULL,
 agg_version INT,
 updated_at TIMESTAMPTZ,
 PRIMARY KEY (city_id, h3_index, resolution, window_start, product_type, metric_type))

-- tile_manifest
(city_id, resolution, window_start, layer,
 s3_path TEXT, checksum, created_at, agg_version)

-- audit_log
(user_id, action, city_id, bbox, time_range, ts)
```

### 8.2 Kafka message (input)

```json
{
  "driver_id": "d_uuid",
  "city_id": "sf",
  "lat": 37.7749,
  "lng": -122.4194,
  "device_ts_ms": 1730000000123,
  "ingest_ts_ms": 1730000000456,
  "seq": 99102,
  "accuracy_m": 8.5,
  "status": "AVAILABLE",
  "products": ["uberx"]
}
```

Heat-map pipeline **does not echo driver_id** to serving layer.

### 8.3 API checklist

- [ ] `GET /v1/heat/cells?city&bbox&res&from&to&product` (RBAC)  
- [ ] `GET /v1/heat/tiles/{z}/{x}/{y}.mvt?city&window&layer` (signed URL)  
- [ ] `GET /v1/heat/compare?city&window&offset_days`  
- [ ] `GET /v1/health/freshness` — last closed window per city  
- [ ] `POST /v1/export` — async analyst export (elevated role)  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| H3 | Uber hex hierarchical geospatial index |
| GeoBucket | Aggregated metric for cell + time window |
| Watermark | Flink progress marker for event time |
| k-anonymity | Suppress buckets with count < K |
| MVT | Mapbox Vector Tile |
| Allowed lateness | Late event correction window |
| Preview layer | Fast approximate partial window |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Kafka consume, Flink 1m, H3 res 7–9, Redis buckets, RBAC |
| 10× | Regional Flink, MVT tiles, CDN, parent rollups |
| 100× | Sampling, HLL, ClickHouse history, hotspot handling |
| 1000× | Edge combiner, approximate default, hierarchical agg |

### 8.6 Window config

```text
tumbling_1m.primary = true
allowed_lateness = 2m
preview_emit_interval = 5s
sample_rate.default = 1.0
sample_rate.100x = 0.1
k_anonymity = 5
```

### 8.7 H3 resolution vs map zoom (example)

| Map zoom | H3 res (urban) |
|----------|----------------|
| 10–11 | 7 |
| 12–13 | 8 |
| 14–15 | 9 |
| 16+ | 10 (optional) |

### 8.8 Intensity normalization

```text
intensity(cell) = log(1 + count) / log(1 + p99_city_count)
clip to [0, 1] for color scale
```

### 8.9 Interview "say this" (60 seconds)

> Heat map is **internal analytics**, not dispatch. We **consume driver locations from Kafka**, aggregate **counts in H3 cells** using **Flink event-time windows** with watermarks, write **pre-aggregated buckets** to a serving store, and render **tiles** for an SSO dashboard. We protect privacy with **aggregates only**, k-anonymity, and RBAC. At scale we **downsample** and use **HLL**—with a fast approximate preview layer if ops needs fresher data.

### 8.10 Reliability test plan

1. Consumer lag spike → dashboard shows stale badge.  
2. Late event within lateness → bucket corrected; idempotent sink.  
3. Duplicate ping seq → no double count (if dedupe enabled).  
4. User without city scope → 403.  
5. Cell count = 3 → suppressed or coarsened.  
6. Flink restart from checkpoint → no duplicate permanent inflation (upsert).  
7. Zoom out → parent rollup matches sum of children (ping counts).

### 8.11 Related systems map

```text
Driver App → Location Ingest → Kafka ─┬→ Dispatch/Matching (hot)
                                       ├→ Heat Map Flink → Buckets → Tiles → Dashboard
                                       └→ Cold Archive (S3)
```

### 8.12 Flink sink idempotency

```text
UPSERT geo_buckets SET metric_value = EXCLUDED.metric_value
WHERE agg_version <= EXCLUDED.agg_version
-- or use (cell, window) version column monotonic
```

### 8.13 Cost controls

| Knob | Savings |
|------|---------|
| Sample rate | Linear on Flink CPU/state |
| Coarser default res | Fewer keys |
| Shorter hot retention | Storage |
| Pre-render only top cities | Tile CPU |

### 8.14 Extra traps

| Trap | Pushback |
|------|----------|
| Heat map drives dispatch directly | Wrong coupling; too stale |
| 5M drivers = 5M cell updates/s | Aggregate first |
| Ignore distinct vs ping semantics | Wrong ops conclusions |
| Public CDN without auth | Leak |

### 8.15 Unit check reminders

```text
100K drivers × 0.5 ping/s = 50K pings/s (not 100K/s unless 1 ping/s)
1m window close → minimum ~60s lag for authoritative layer
H3 res-9 cell ~174 m edge — know order of magnitude
```

### 8.16 Sample Flink pseudo-code

```java
DataStream<LocationEvent> events = kafkaSource(...);

events
  .filter(e -> e.accuracy_m < 100)
  .assignTimestampsAndWatermarks(
      WatermarkStrategy.<LocationEvent>forBoundedOutOfOrderness(Duration.ofMinutes(2))
        .withTimestampAssigner((e, ts) -> e.eventTs()))
  .map(e -> new KeyedCell(e.cityId, h3.geoToH3(e.lat, e.lng, 9), e.product))
  .keyBy(KeyedCell::key)
  .window(TumblingEventTimeWindows.of(Time.minutes(1)))
  .allowedLateness(Time.minutes(2))
  .aggregate(new PingCountAggregator())
  .sinkTo(idempotentBucketSink());
```

### 8.17 Dashboard UX notes

- Time scrubber snaps to closed minutes for authoritative layer.  
- Legend shows count scale and sample rate if applicable.  
- City selector respects SSO scopes.  
- "Compare" overlays ghost layer from historical rollup.

### 8.18 Backfill job

```text
S3 archive → Spark/Flink batch → write agg_version=2 buckets → flip router
Dual-read v1/v2 during validation; diff report per city
```

### 8.19 Observability dashboards

- Flink: records in/out, checkpoint, backpressure, skew.  
- Kafka: consumer lag by partition.  
- Tile API: p50/p99, cache hit rate.  
- Business: top cells delta vs yesterday.

### 8.20 Security checklist

- [ ] SSO + MFA for production dashboard  
- [ ] Service accounts for automation scoped to city  
- [ ] Signed tile URLs short TTL  
- [ ] No driver_id in bucket/tile payloads  
- [ ] Audit exports  
- [ ] Pen test internal API annually  

---

*End of driver heat-map system design.*
