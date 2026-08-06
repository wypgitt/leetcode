# System Design: Real-Time Uber Eats Restaurant Metrics

> **Focus areas:** Event-time windows · Watermarks · Top-K menu items · Count-min sketch / heap / approximate structures · Exactly-once / idempotent updates · Serving store for dashboard · Order value rollups  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar load classes (order events vs dashboard reads vs top-K maintenance), explicit window semantics, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber Eats — give restaurant partners a **real-time dashboard** showing **order value** and **top-K menu items** over **1h / 1d / 1w** sliding windows with trustworthy aggregates under out-of-order events

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

Goal: **bound the product**—restaurant metrics is *not* the full Uber Eats marketplace. It is the subsystem that **consumes order lifecycle events**, maintains **rolling aggregates per restaurant** (GMV/order value, order count, top-K items), and **serves a low-latency partner dashboard** with correct semantics under retries, cancellations, and late events.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Per-restaurant metrics + top-K menu items over 1h/1d/1w | Full order placement / dispatch |
| Users | Restaurant owners/managers on partner portal | End consumers browsing feed |
| Windows | Event-time sliding/tumbling 1h, 1d, 1w | Unlimited ad-hoc SQL for analysts |
| Correctness | Idempotent updates; money-like order value | Approximate-only with no GMV truth |
| Scope | Dashboard metrics API | Payouts, tax, inventory ERP |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who views metrics? | Restaurant partner via web/mobile dashboard | Auth scoped to `restaurant_id` |
| F2 | Core metrics? | Total order value (GMV), order count, avg basket | Sum + count aggregators |
| F3 | Top-K items? | Top 10 (or K) menu items by quantity or revenue in window | Top-K structure per restaurant per window |
| F4 | Windows? | Last 1 hour, last 24 hours, last 7 days | Three parallel window pipelines or unified store |
| F5 | Event source? | `OrderPlaced`, `OrderCancelled`, `OrderAdjusted` events | Signed deltas; not poll DB |
| F6 | Item granularity? | `menu_item_id` + name snapshot | Key by item_id; store display name |
| F7 | Currency? | Single currency per restaurant/market | No FX in MVP |
| F8 | Refunds/adjustments? | Subtract or emit negative delta events | Idempotent adjustment handler |
| F9 | Near-real-time? | Dashboard updates within ~30–60s | Streaming + serving store |
| F10 | Historical compare? | vs yesterday / last week optional | Store completed windows |
| F11 | Multi-location? | Chain with many stores | `restaurant_id` partition; optional roll-up |
| F12 | Export? | CSV daily summary | Batch export async |

**MVP functional scope (lock with interviewer):**

1. Ingest **order events** from Kafka (`order.events` topic).
2. Compute **order value sum** and **order count** per restaurant for windows **1h, 1d, 1w** (event-time).
3. Maintain **top-10 menu items** by quantity (tie-break by revenue) per window.
4. Handle **cancel/adjust** events as negative deltas idempotently.
5. **Serving store** (Redis + OLAP) for dashboard GET APIs.
6. **Watermarks** with allowed lateness for out-of-order events (e.g. 5–15m).
7. Partner auth: restaurant can only read own metrics.

**Out of MVP (explicitly defer):**

- Sub-second websocket tick-by-tick (30–60s refresh OK)
- Exact global top-K across all restaurants
- Complex funnel (views → cart → order)
- ML forecasting
- Cross-region active-active writes on same restaurant aggregate without home cell

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Dashboard read latency? | Snappy partner UX | p50 < 100ms, p99 < 500ms |
| N2 | Freshness? | "Real-time enough" | Metrics lag p99 < 60s behind event time |
| N3 | Correctness (GMV)? | Must match finance eventually | Exact sums; idempotent event keys |
| N4 | Top-K accuracy? | Exact top-10 for single restaurant OK at baseline | Approx at 1000× with error bounds |
| N5 | Availability? | Degrade read stale; don't lose writes | 99.9% API; durable log |
| N6 | Throughput? | See scale table | Split **order events**, **agg updates**, **dashboard reads** |
| N7 | Multi-tenant isolation? | Restaurant A never sees B | Partition + authZ |
| N8 | Event ordering? | Out-of-order common | Event-time + watermarks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Order placed → event on Kafka → Flink updates 1h/1d/1w sums + item counts → dashboard polls → shows updated GMV and top items.
2. Order cancelled within window → cancel event subtracts value and decrements item counts; top-K recomputed.
3. Partner switches window tab (1h → 1d → 1w) → API reads pre-materialized aggregates; no full replay.
4. Midnight boundary → event-time windows roll; completed 1d window archived.
5. Same order event retried → idempotency key prevents double count.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate `OrderPlaced` | Dedupe by `event_id` or `(order_id, event_type)` |
| Late event after watermark | Side output to correction job OR extend lateness (config) |
| Partial order (items added later) | `OrderAdjusted` delta events |
| Item renamed | Metrics keyed by `menu_item_id`; display latest name in serving layer |
| Hot restaurant (viral) | Shard by restaurant_id; local top-K heap |
| Flink restart | Checkpoint restore; sink idempotent |
| Negative basket after cancel | Clamp item counts at zero; audit anomaly |
| Clock skew on POS integration | Server `event_ts` authoritative |
| Week window timezone | Restaurant local TZ for 1d/1w boundaries |
| Top-K tie | Secondary sort by revenue, then item_id |
| Menu item deleted | Historical metrics retain item_id |
| Dashboard poll storm | CDN/edge cache 15–30s per restaurant |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active restaurants | 100K | 1M | 10M | 100M |
| Orders / day (global) | 5M | 50M | 500M | 5B |
| Peak order events / s | ~200 | ~2K | ~20K | ~200K |
| Line items / order (avg) | 3 | 3 | 3 | 3 |
| Item events / s | ~600 | ~6K | ~60K | ~600K |
| Dashboard DAU (partners) | 50K | 500K | 5M | 50M |
| Metrics reads / s | ~500 | ~5K | ~50K | ~500K |
| Restaurants with >1K orders/day | 1K | 10K | 100K | 1M |
| Max menu items / restaurant | 500 | 500 | 1K | 2K |
| Window state keys | ~300K | ~3M | ~30M | ~300M |

**What each jump forces:**

- **10×:** Flink per region; Redis serving; idempotent sink; parallel 1h/1d/1w operators.
- **100×:** Approximate top-K (Count-Min + heap) for mega-restaurants; pre-aggregate item counts in combiner.
- **1,000×:** Tiered exact vs approx; home-cell restaurant sharding; async correction for late events; read replicas + aggressive cache.

### 1.5 Scope repeat-back

> Design **real-time Uber Eats restaurant metrics**: consume order events, compute **order value** and **top-K menu items** over **1h / 1d / 1w event-time windows** with watermarks, **idempotent exactly-once business effect**, serve from a **dashboard store**—scaling from ~200 events/s to ~200K events/s. Not order taking, dispatch, or payouts.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Order header events | ~200/s | ~200K/s | Sum/count per restaurant |
| Line-item events | ~600/s | ~600K/s | Top-K driver |
| Aggregate state updates | ~200/s × 3 windows | huge | Combine per event |
| Dashboard reads | ~500/s | ~500K/s | Cache per restaurant |
| Late correction | ~1% events | ~2K/s | Side output path |

**Critical insight:** **Line items dominate cardinality** for top-K, not order headers. Optimize item-level aggregation early; don't scan all items on dashboard read.

### 2.2 Order volume math

```text
5M orders/day ÷ 86400 ≈ 58 orders/s average
Peak ~3–5× → ~200 orders/s (baseline)

3 line items/order → ~600 item events/s

1,000×: 5B orders/day → ~58K orders/s avg, ~200K/s peak
→ 600K item events/s peak
```

### 2.3 State per restaurant

```text
Exact top-10 per window: min-heap size 10 × metadata ~100 B → trivial
Exact all-item counts for top-K correctness: 500 items × (count, revenue) × 16 B ≈ 8 KB
× 3 windows ≈ 24 KB / restaurant in Flink state (baseline exact path)

Hot restaurant 50K items/day → 500 distinct items active in 1w window → still ~8 KB

100M restaurants × 24 KB → 2.4 TB (impossible global) → only active restaurants in state; rest cold zero
Active 1M restaurants × 24 KB ≈ 24 GB Flink state (10× scale OK sharded)
```

### 2.4 Serving store size

```text
Per restaurant serving record:
  gmv_1h, count_1h, top10_1h (10 × item json) ≈ 2 KB
  × 3 windows ≈ 6 KB

100K restaurants × 6 KB ≈ 600 MB Redis (baseline)
1M restaurants × 6 KB ≈ 6 GB (10× — shard Redis)
```

### 2.5 Bandwidth

```text
Order event ~500 B – 2 KB (with items inline or referenced)
200/s × 1 KB ≈ 200 KB/s Kafka (baseline)
200K/s × 1 KB ≈ 200 MB/s (1000× — multi-region Kafka)
```

### 2.6 Latency budget (event → dashboard)

```text
Kafka publish                    5–20ms
Flink processing + watermark    0–60s (window + allowed lateness policy)
Sink to Redis                    10–50ms
Dashboard poll (30s interval)    0–30s
API read Redis                   1–10ms
------------------------------------
Partner sees update: ~30–90s typical (baseline)
```

**Deal-breaker for "instant" (<1s) without stating partial aggregates:** Full 1w window recomputed on each order.

### 2.7 Bottlenecks (rank ordered)

1. **Recompute top-K from scratch** on every read  
2. **No idempotency** on duplicate order events (GMV double-count)  
3. **Processing-time windows** (wrong during lag)  
4. **Per-item OLTP row update** in Postgres at 600K/s  
5. **Global single Redis** for all restaurants  
6. **Exact item map** for 100K menu items in one restaurant without approximation  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
OrderEvent      — OrderPlaced | Cancelled | Adjusted (with idempotency key)
LineItem        — (menu_item_id, qty, line_revenue)
RestaurantAgg   — per (restaurant_id, window_type) → gmv, count, top_k
WindowSpec      — 1h, 1d, 1w in restaurant local TZ (event-time)
ServingSnapshot — materialized read model for dashboard API
```

**Event example:**

```json
{
  "event_id": "evt_uuid",
  "order_id": "ord_uuid",
  "restaurant_id": "rest_uuid",
  "event_type": "ORDER_PLACED",
  "event_ts": "2026-08-06T18:04:12Z",
  "currency": "USD",
  "order_value_cents": 4599,
  "items": [
    {"menu_item_id": "mi_1", "name": "Burrito", "qty": 2, "revenue_cents": 2598},
    {"menu_item_id": "mi_2", "name": "Soda", "qty": 1, "revenue_cents": 2001}
  ]
}
```

### 3.2 Window semantics (event-time)

| Window | Definition | Notes |
|--------|------------|-------|
| 1h | Sliding last 60 minutes event-time | Updates continuously |
| 1d | Sliding last 24h OR tumbling calendar day local TZ | Clarify with interviewer |
| 1w | Sliding last 7×24h OR calendar week local TZ | Heavier state |

**MVP recommendation:** **Sliding event-time windows** for 1h/1d/1w (simpler UX: "last 24 hours" always). Calendar day/week as Phase 2 via secondary tumbling sink.

**Watermarks:**

```text
watermark = max_observed_event_ts - allowed_lateness
allowed_lateness: 5m (baseline) – 15m (global pipelines)

Late events within lateness: update aggregates + top-K
Beyond lateness: route to async correction or drop with audit
```

### 3.3 Aggregation: order value

```text
On ORDER_PLACED:  gmv += order_value_cents; count += 1
On CANCELLED:     gmv -= order_value_cents; count -= 1 (clamp >= 0)
On ADJUSTED:      gmv += delta_cents; items delta separately
```

**Idempotency:**

```text
ProcessedEvents store (RocksDB / Redis bloom + KV):
  if seen(event_id): skip
  else apply delta; mark event_id with TTL >= max window + lateness
```

Alternative: **delta journal** in OLTP with unique `(event_id)` constraint at sink.

### 3.4 Top-K menu items

| Approach | Pros | Cons | When |
|----------|------|------|------|
| A. Min-heap size K per window | Exact top-K; small memory | Need item count updates O(log K) | MVP default |
| B. HashMap all items + periodic prune | Exact | O(items) memory | Menu ≤ 500 items |
| C. Count-Min Sketch + min-heap | Sublinear memory | Approx counts | 1000× mega menus |
| D. Space-Saving algorithm | Heavy hitters | Approx | Streaming literature |
| E. Batch recompute hourly | Simple | Stale | Not "real-time" |

**MVP chosen path:** **HashMap(item_id → {qty, revenue})** in Flink state for active window; on trigger emit top-K via partial sort or heap. For 500 items, brute force top-10 every N seconds is fine.

**Scale path:** **Count-Min Sketch** for frequency + **min-heap of K candidates** validated with exact counters for heap members only.

### 3.5 Count-Min Sketch + heap (100× deep dive)

```text
1. CMS increment on each line item (qty)
2. Maintain min-heap of K candidates by estimated count
3. On query/trigger: re-estimate heap members with CMS; swap if better candidates found
4. Optional exact map for items in heap only (small)
Error bound ε: choose width w = ceil(e/ε), depth d = ceil(ln(1/δ))
```

**When exact required:** GMV sums always exact (long/int); top-K may be approximate at extreme scale with UI disclaimer.

### 3.6 Exactly-once / idempotent updates

| Layer | Guarantee |
|-------|-----------|
| Kafka → Flink | At-least-once + checkpoint |
| Flink state | Exactly-once with checkpointing |
| Flink → sink | **Idempotent upsert** on `(restaurant_id, window)` |
| Business effect | **Effective exactly-once** if `event_id` deduped |

**Pattern:**

```text
1. Dedupe event_id in state (TTL = window_size + lateness + buffer)
2. Apply delta to gmv/count/item map atomically in keyed operator
3. Sink snapshot with monotonic version
```

**Deal-breaker:** Rely on "Kafka exactly-once" alone without idempotent `event_id` handling across redeploys.

### 3.7 Serving store for dashboard

| Component | Role |
|-----------|------|
| Redis (primary) | Latest snapshot per `(restaurant_id)` — all windows + top-K JSON |
| DynamoDB / Cassandra | Optional durable mirror |
| ClickHouse / Pinot | Historical trends, compare yesterday |
| API cache | 15–30s CDN edge for GET |

**Read API returns precomputed snapshot — never scans Kafka on read path.**

```json
{
  "restaurant_id": "rest_uuid",
  "as_of_event_ts": "2026-08-06T18:04:00Z",
  "windows": {
    "1h": {"gmv_cents": 125000, "order_count": 42, "top_items": [...]},
    "1d": {"gmv_cents": 890000, "order_count": 310, "top_items": [...]},
    "1w": {"gmv_cents": 5200000, "order_count": 1800, "top_items": [...]}
  }
}
```

### 3.8 Parallel window computation

| Option | Pros | Cons |
|--------|------|------|
| Single operator maintains 3 maps | One pass per event | Larger state |
| Fork stream to 3 keyed windows | Isolated checkpoint | Triple sink merge |
| Lambda: 1h stream + batch 1d/1w | Cheaper long windows | Two systems |

**MVP:** Single keyed process function updates all three window states per event (simplest mentally in interview).

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Time semantics | Event-time + watermark | Correct under delay | Processing-time |
| GMV | Exact int64 sums | Money trust | Float aggregates |
| Top-K baseline | HashMap + heap | Exact for ≤500 SKUs | Full table scan on read |
| Top-K 1000× | CMS + heap | Memory bound | Exact billion SKUs |
| Dedup | event_id TTL set | Effective exactly-once | Hope no duplicates |
| Serving | Redis snapshot | Read p99 | Query Flink state |
| Windows | Sliding 1h/1d/1w | Partner language | Only batch daily |
| TZ | Restaurant local | Calendar day truth | UTC only globally |

### 3.10 Coupling to siblings

| Sibling | Interaction |
|---------|-------------|
| Order service | Source of truth events |
| Payouts / ledger | Finance reconciliation async; not inline |
| Restaurant portal | Reads metrics API |
| Inventory | Out of scope |
| Recommendations | May consume aggregates offline |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Consumer App          Order Service                Partner Dashboard
       |                      |                              |
       | place order          |                              |
       v                      v                              |
  +-----------+        +---------------+                      |
  | Checkout  |------->| Order OLTP    |                      |
  +-----------+        +-------+-------+                      |
                               |                              |
                               | publish                      |
                               v                              |
                       +---------------+                      |
                       | Kafka         |                      |
                       | order.events  |                      |
                       +-------+-------+                      |
                               |                              |
              +----------------+----------------+             |
              |                |                |             |
              v                v                v             |
      +---------------+ +-------------+ +-------------+     |
      | Flink Metrics | | Finance     | | Data Lake   |     |
      | Aggregator    | | Reconcile   | | (archive)   |     |
      +-------+-------+ +-------------+ +-------------+     |
              |                                              |
              v                                              |
      +---------------+                                      |
      | Serving Store |<-------------------------------------+
      | Redis + OLAP  |        GET /metrics (auth restaurant)
      +---------------+
```

### 4.2 Sequence: order placed → dashboard

```text
OrderSvc     Kafka      Flink           DedupState      Redis       Dashboard
   |--evt--->|           |                 |              |             |
   |         |--consume->|                 |              |             |
   |         |           |--seen?--------->|              |             |
   |         |           |<-no-------------|              |             |
   |         |           |--update agg---->|              |             |
   |         |           |--mark event_id->|              |             |
   |         |           |--snapshot--------------------->|             |
   |         |           |                 |              |<--poll------|
   |         |           |                 |              |--JSON------>|
```

### 4.3 Sequence: cancel event (negative delta)

```text
Cancel evt with same order_id reference
Dedup by new event_id (cancel is new event, not duplicate place)
Subtract gmv + decrement item qty (clamp 0)
Recompute top-K heap from item map
Upsert Redis snapshot version++
```

### 4.4 Sequence: late event within allowed lateness

```text
Watermark at T-5m; event arrives with event_ts T-3m
Still within allowed lateness → apply to sliding window state
Update Redis; dashboard next poll reflects correction
Optional: emit partner notification if GMV change > threshold
```

### 4.5 Home-cell sharding

```text
Global API Gateway (partner auth)
        |
        v
Directory: restaurant_id → home_region
        |
   +----+----+----+
   |    |    |    |
  US   EU  APAC ...
 Flink Flink Flink
 Redis Redis Redis
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Idempotent events:** Each `event_id` processed at most once for effect.  
2. **GMV exactness:** Integer cents; no floats; monotonic snapshot versions.  
3. **Cancel correctness:** Cancel without matching place → audit + no-op or dead letter.  
4. **Window boundaries:** Event-time defined; watermarks documented to partners ("data through …").  
5. **AuthZ:** Token `restaurant_id` must match resource.  
6. **At-least-once ingress safe:** Dedup makes business effect exactly-once.  
7. **Top-K deterministic ties:** qty desc, revenue desc, item_id asc.  
8. **State TTL:** Expire dedup keys after `window_max + lateness + buffer`.  
9. **Flink checkpoint** before sink ack (two-phase commit sink optional).  
10. **Reconciliation job** compares stream GMV vs OLTP daily.

### 5.2 Scalability

| Scale | Architecture moves |
|-------|--------------------|
| 1× | Single Flink job; Redis serving; exact top-K hashmap |
| 10× | Shard by restaurant_id; parallel Kafka partitions; Redis cluster |
| 100× | CMS+heap for top-K on large menus; separate hot restaurant isolation |
| 1000× | Home-cell regions; approx top-K tier; async late correction; read replicas |

### 5.3 Maintainability

- **Window config externalized:** lateness, slide, TZ policy.  
- **Schema registry** for order events with compatibility mode.  
- **Shadow job** on staging comparing top-K vs brute force batch.  
- **Versioned snapshots** (`metrics_schema_version`).  
- **Runbooks:** duplicate GMV alert, Flink lag, Redis failover.

### 5.4 Progressive scale playbook

**Baseline (~200 order events/s):**

- Kafka 24 partitions; Flink parallelism 24; keyBy `restaurant_id`.  
- In-process maps: `gmv`, `count`, `item_id → {qty,revenue}` for 1h/1d/1w.  
- Emit Redis snapshot every 5–10s or on count-change threshold.  
- Dashboard poll 30s.

**10× (~2K/s):**

- Scale partitions to 192+; RocksDB incremental checkpoints.  
- Redis cluster hash-tagged by restaurant.  
- ClickHouse sink for historical compare.  
- API cache 15s.

**100× (~20K/s):**

- Mega-restaurant flag: dedicated partition or sub-task.  
- Count-Min Sketch for item frequency; exact map only for top-50 candidates.  
- Separate **correction** job for late events beyond lateness.  
- Preaggregate line items in order service (single event with array) to cut fan-out.

**1,000× (~200K/s):**

- Regional home cells; no cross-region restaurant state.  
- Two-tier: fast 1h exact + 1d/1w rolled up from hourly tumbling buckets.  
- Approx top-K with UI badge; finance GMV still exact from order header path.  
- Dashboard websocket optional for hot accounts only.

### 5.5 Sliding window implementation options

**Option A — Flink native sliding event-time windows:**

```text
.window(SlidingEventTimeWindows.of(Time.hours(24), Time.minutes(1)))
```

Many panes → high state; use only if parallelism + rocksdb tuned.

**Option B — Custom process function with ring buffer of minute buckets:**

```text
Maintain 1440 minute buckets for 1d window
On event: increment bucket[minute(event_ts)]
Sum = Σ buckets in range [now-24h, now]
```

Memory: 1440 × 8 B × metrics per restaurant — acceptable.

**Option C — Hierarchical rollups:**

```text
1m tumbling exact → merge to 1h → merge to 1d → merge to 1w
Query sum last 24h = sum last 1440 1m buckets
Top-K: merge item counts from 1m buckets (exact if buckets store item maps — heavy)
OR recompute top-K from 1h item maps only (lighter)
```

**Interview recommendation:** Describe **minute-bucket ring buffer** for sums + **item HashMap** maintained incrementally (not recomputing from Kafka on read).

### 5.6 Top-K algorithms detail

**Exact (baseline):**

```text
Map<item_id, {qty, revenue, name}>
After each update (or every 5s):
  candidates = sort by qty desc, take 10  // 500 log 500 cheap
OR min-heap size 10 keyed by qty
```

**Heap update on qty change:**

```text
If item not in heap and qty > heap.min: push, pop min
If item in heap: update, heapify
```

**CMS + heap (scale):**

```text
cms.add(item_id, qty)
for each candidate in heap: est = cms.estimate(item_id)
 periodically scan heavy hitters from CMS table to refresh heap
```

### 5.7 Idempotency store design

```text
Key: event_id
Value: processed_at
TTL: max(1w) + allowed_lateness + 1d buffer ≈ 8–10d

Backend: RocksDB state in Flink (preferred) OR Redis SET with TTL per event
Memory at 200/s × 86400 × 10d ≈ 172M keys → too big for naive SET at 1000×
→ Bloom filter + compacted KV with TTL compaction (RocksDB)
```

At **1000×**, rely on **Kafka compacted idempotency topic** + RocksDB incremental cleanup.

### 5.8 Serving store schema (Redis)

```text
Key: metrics:{restaurant_id}
Hash fields:
  version, as_of_ts,
  gmv_1h, cnt_1h, top_1h_json,
  gmv_1d, cnt_1d, top_1d_json,
  gmv_1w, cnt_1w, top_1w_json

Write: atomic MULTI/EXEC or single JSON blob SET
Read: single GET → parse
TTL: none (always latest); historical in OLAP
```

### 5.9 Failure modes & degradations

| Failure | Degrade |
|---------|---------|
| Flink lag | Serve stale `as_of_ts`; banner on dashboard |
| Redis down | Failover replica; read from OLAP slower |
| Duplicate storm | Dedup protects GMV |
| Late events flood | Increase lateness temporarily; correction queue |
| Mega-restaurant skew | Isolate operator chain |
| Event schema break | Schema registry reject; dead letter |

### 5.10 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Compute metrics on dashboard read from raw orders DB | Latency + load death |
| Processing-time windows | Wrong GMV during lag |
| Float money | Rounding disputes |
| No cancel handling | Inflated GMV |
| Top-K full recompute from Kafka each poll | Impossible |
| Global Redis single key per day | Hot key |
| Claim exact top-K at 600K item events/s without approx | Memory lie |

---

## 6. Wrap-Up

### 6.1 Designed

Real-time Uber Eats restaurant metrics: Kafka order events, Flink event-time sliding windows with watermarks, exact GMV + idempotent dedup, top-K via HashMap/heap (CMS at scale), Redis serving snapshots, partner dashboard API—scaling 200/s → 200K/s.

### 6.2 Decisions to defend

1. **Event-time + watermarks** for 1h/1d/1w  
2. **Idempotent `event_id` dedup** for effective exactly-once  
3. **Pre-materialized serving store** — no read-time aggregation  
4. **Exact GMV**, approximate top-K only at extreme scale  
5. **Incremental top-K** maintenance, not scan-all  
6. **Negative deltas** for cancel/adjust  
7. **Restaurant-scoped partitioning** + home cell at 1000×  
8. **Minute-bucket or sliding state** with clear lateness policy  

### 6.3 Risks

- Sliding 1w state cost per restaurant  
- Late corrections confusing partners  
- Top-K approx vs exact expectations  
- Timezone calendar vs sliding ambiguity  
- Reconciliation drift vs finance ledger

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: partner metrics, not orders |
| 5–12 | Estimates: orders vs line items vs reads |
| 12–22 | HLD: events → Flink → windows → Redis |
| 22–32 | Top-K structures, idempotency, watermarks |
| 32–40 | Scale + deal-breakers |
| 40–45 | Wrap + Q&A hooks |

### 6.5 Closer

> **Restaurant metrics**: consume **order events**, maintain **exact GMV** and **top-K items** in **event-time sliding windows** with **watermarks**, dedupe for **exactly-once effect**, push **snapshots to Redis** for a fast partner dashboard—scale with **CMS+heap** when item cardinality explodes.

---

## 7. Deeper / Related Interview Questions

### 7.1 Windowing

**Q: Tumbling vs sliding vs session?**  
A: Sliding for "last 1h/1d/1w"; tumbling for hourly archives; session irrelevant here.

**Q: Calendar day vs sliding 24h?**  
A: Product choice; sliding simpler streaming; calendar needs TZ tumbling.

**Q: How handle 1w window state?**  
A: Minute buckets (10K buckets) or hierarchical 1h rollups; don't store every order.

### 7.2 Watermarks

**Q: What if event is 1 hour late?**  
A: Beyond lateness → correction job or drop; partner sees `as_of` timestamp.

**Q: Idle restaurants?**  
A: Watermark advances with global clock; no events → no updates (fine).

### 7.3 Top-K

**Q: Min-heap vs full sort?**  
A: 500 items → full sort OK; streaming infinite → heap or CMS.

**Q: Top-K by revenue vs quantity?**  
A: Clarify product; support both or primary qty with revenue tie-break.

**Q: Count-min sketch accuracy?**  
A: Overestimate; use for candidates; verify top-K edges exactly.

### 7.4 Exactly-once

**Q: End-to-end exactly-once?**  
A: Business exactly-once via idempotent `event_id`; Kafka EOS + 2PC sink optional.

**Q: Duplicate cancel?**  
A: Separate event_id; second cancel no-op.

### 7.5 Serving

**Q: Redis vs Postgres?**  
A: Redis for latest snapshot latency; OLAP for history.

**Q: WebSocket vs poll?**  
A: Poll 30s MVP; WS for premium tier.

### 7.6 Scale

**Q: 600K item events/s top-K?**  
A: CMS + heap; hierarchical minute buckets; approximate UI.

**Q: Hot restaurant partition?**  
A: Dedicated subtask; optional async micro-batch for item updates.

### 7.7 Correctness

**Q: GMV includes tax/tip?**  
A: Clarify with interviewer; consistent with finance events.

**Q: Partial refund one item?**  
A: `OrderAdjusted` line-item deltas.

### 7.8 Comparison

**Q: vs sliding-window top-K generic?**  
A: Same algorithms; this adds money sums, partner auth, cancel semantics.

**Q: vs batch daily report?**  
A: Batch simpler; requirement here is near-real-time.

### 7.9 Data structures summary

| Structure | Use |
|-----------|-----|
| int64 sum | GMV exact |
| HashMap | Item qty/revenue exact |
| Min-heap K | Top-K maintenance |
| Count-Min Sketch | Approx frequency |
| Ring buffer minutes | Sliding sum |
| Bloom filter | Dedup auxiliary |

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| Query orders table on each dashboard load | Doesn't scale |
| Ignore cancels | Wrong GMV |
| Processing time | Wrong under lag |
| Float dollars | Use cents |
| One global top-K | Per restaurant |
| Recompute 1w from scratch each event | O(orders) death |

### 7.11 Metrics

| Metric | Why |
|--------|-----|
| Dedup rate | Duplicate detection |
| Flink lag | Freshness |
| GMV reconciliation delta | Money trust |
| Top-K drift vs batch | Approx validation |
| Snapshot write p99 | Serving path |
| Per-restaurant event skew | Hotspot |

### 7.12 Flink vs Spark

**Q: Why Flink?**  
A: Event-time windows, low latency, stateful exactly-once; Spark Structured Streaming OK at 30s+ micro-batch.

### 7.13 Multi-restaurant chains

**Q: Roll up to brand?**  
A: Separate aggregate keyed by `brand_id` or batch roll-up from store metrics.

### 7.14 Security

**Q: Partner A sees B?**  
A: Auth token restaurant scope; row-level security in API.

---

## 8. Appendices

### 8.1 Event types

```text
ORDER_PLACED    — initial positive
ORDER_CANCELLED — full negative (same order_value + items)
ORDER_ADJUSTED  — partial delta on value/items
ORDER_COMPLETED — optional; metrics may use PLACED only
```

### 8.2 Schema: serving snapshot

```sql
-- redis blob or dynamo item
restaurant_id (PK)
version BIGINT
as_of_event_ts TIMESTAMPTZ
gmv_1h_cents BIGINT
order_count_1h INT
top_items_1h JSON  -- [{menu_item_id, name, qty, revenue_cents}, ...]
-- repeat for 1d, 1w
updated_at TIMESTAMPTZ
```

### 8.3 Schema: dedup / idempotency

```text
event_id UUID PK
restaurant_id
processed_at
expire_at  -- TTL index
```

### 8.4 API checklist

- [ ] `GET /v1/restaurants/{id}/metrics?windows=1h,1d,1w`  
- [ ] `GET /v1/restaurants/{id}/metrics/history?granularity=1h&from&to`  
- [ ] `GET /v1/health/metrics-freshness`  
- [ ] Auth: OAuth partner token scoped to restaurant  

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| GMV | Gross merchandise value (order value sum) |
| Watermark | Flink event-time progress |
| Allowed lateness | Late event acceptance window |
| CMS | Count-Min Sketch |
| Sliding window | Last N time continuously |
| Effective exactly-once | Idempotent deduped effect |

### 8.6 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Kafka, Flink, dedup, exact top-K, Redis snapshot |
| 10× | Partition scale, Redis cluster, ClickHouse history |
| 100× | CMS+heap mega-restaurants, correction job |
| 1000× | Home cell, hourly rollups for 1w, approx top-K tier |

### 8.7 Window config

```text
windows = [1h, 1d, 1w]
allowed_lateness = 10m
dedup_ttl = 8d
snapshot_emit_interval = 5s
dashboard_poll = 30s
currency = integer cents
top_k = 10
```

### 8.8 Top-K tie-break

```text
sort by qty DESC, revenue_cents DESC, menu_item_id ASC
take 10
```

### 8.9 Minute ring buffer (1d window)

```text
buckets[1440] each: {gmv_delta, count_delta, item_map_ref or merged later}
on event at minute m: update buckets[m % 1440]
rolling sum: iterate last 1440 minutes relative to watermark time
```

### 8.10 Count-Min Sketch params example

```text
ε = 0.001, δ = 0.01
w ≈ 1000, d ≈ 5 → ~5K counters per restaurant per CMS
Mergeable for parallel ingestion
```

### 8.11 Interview "say this" (60 seconds)

> Partners need **order value** and **top-10 items** for **last 1h, 1d, 1w**. We ingest **order events from Kafka**, use **Flink event-time sliding windows** with **watermarks**, **dedupe by event_id** for exactly-once GMV, maintain **item counts** in state and a **min-heap** for top-K, and write **snapshots to Redis** for fast dashboard reads—scaling with **minute buckets** and **Count-Min Sketch** when needed.

### 8.12 Reliability test plan

1. Duplicate `OrderPlaced` → GMV unchanged after first.  
2. Place + cancel → net zero GMV and items.  
3. Late event within lateness → metrics corrected.  
4. Restaurant A token → cannot read B metrics.  
5. Flink restart → no double GMV (checkpoint + dedup).  
6. Top-K ties broken deterministically.  
7. Mega-restaurant load test → skew handled.

### 8.13 Reconciliation job

```text
Daily: SUM(order_value) from OLTP vs metrics stream snapshot 1d
Tolerance 0; alert on mismatch → replay events for restaurant
```

### 8.14 Related systems map

```text
Consumer → Order Service → Kafka order.events
                              ├→ Flink Metrics → Redis → Partner Dashboard
                              ├→ Finance / Ledger
                              └→ Data Lake
```

### 8.15 Flink pseudo-code

```java
stream
  .assignTimestampsAndWatermarks(
      WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofMinutes(10))
        .withTimestampAssigner((e, ts) -> e.eventTs()))
  .keyBy(OrderEvent::restaurantId)
  .process(new RestaurantMetricsFunction()); // updates 1h/1d/1w + dedup

class RestaurantMetricsFunction extends KeyedProcessFunction<...> {
  Map<String, Long> seenEvents; // TTL managed
  MetricsState state1h, state1d, state1w;

  void processElement(OrderEvent e, Context ctx, Collector<Snapshot> out) {
    if (seenEvents.contains(e.eventId())) return;
    seenEvents.put(e.eventId(), ctx.timestamp());
    Delta d = toDelta(e);
    state1h.apply(d); state1d.apply(d); state1w.apply(d);
    if (shouldEmit()) out.collect(buildSnapshot());
  }
}
```

### 8.16 Cancel delta example

```text
Place:  gmv +4599, burrito qty +2
Cancel: gmv -4599, burrito qty -2 (clamp min 0)
Top-K: burrito may drop from top 10
```

### 8.17 Extra traps

| Trap | Pushback |
|------|----------|
| 5M orders/day = 5M QPS | Divide by 86400 |
| Store all orders in Flink state | Keep aggregates only |
| Top-K across all restaurants | Per restaurant scope |
| Skip watermark discussion | Interview expects event-time |

### 8.18 Unit check reminders

```text
5M orders/day ÷ 86400 ≈ 58/s avg, peak ~200/s
3 items/order → ~600 item events/s at baseline peak
GMV in cents as int64 — $1M/day/restaurant fits easily
```

### 8.19 Observability

- Flink: lag, checkpoint, state size per operator  
- Business: restaurants with zero metrics unexpectedly  
- Dedup: duplicate rate from upstream  
- API: p99 read, cache hit  

### 8.20 Partner UX copy

```text
"Metrics reflect orders through 18:04 UTC (typically 30–60s delay)."
"Top items ranked by quantity sold."
```

### 8.21 Historical compare query (OLAP)

```sql
SELECT hour, sum(gmv_cents)
FROM restaurant_metrics_hourly
WHERE restaurant_id = ? AND hour BETWEEN ? AND ?
GROUP BY hour
```

### 8.22 Space-Saving vs CMS

| Algo | Notes |
|------|-------|
| Space-Saving | Tracks K heavy hitters with error guarantees |
| CMS | Smaller; overcount; needs heap validation |

Use Space-Saving when K fixed and stream infinite.

### 8.23 Order event partitioning

```text
Kafka key = restaurant_id
→ all events for one restaurant ordered per partition (if single producer per order)
→ simplifies keyed state consistency
```

### 8.24 Partial emit strategy

```text
Emit Redis snapshot when:
  - 5s timer fires OR
  - gmv delta > $X since last emit OR
  - top-K membership changed
Reduces write QPS while keeping UX fresh
```

---

*End of real-time restaurant metrics system design.*
