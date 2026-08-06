# System Design: Top-K Movies / Series Dashboard (Hourly)

> **Focus areas:** Streaming ingest · Event-time windows · Sliding/tumbling top-K · Approximate vs exact · Late data · Dashboard freshness · Minute-level viewing events  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — realtime analytics / top-K over streams (same muscles as restaurant metrics & trending)  
> **Quality bar:** Correct window semantics; honest approx math; late-event policy; not “GROUP BY in OLTP”

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

Goal: ingest **minute-level (or finer) viewing events** and power a dashboard of **top-ten movies/series** over recent time windows (e.g. last hour), correctly under late events and extreme scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Streaming top-K analytics + dashboard API | Full Netflix catalog CMS |
| Metric | Watch-starts, watch-minutes, or unique viewers—**pick** | Recommendations ML (sibling) |
| Latency | Seconds–minutes freshness | Billing-grade exact ledger |
| Uber lens | Event-time, windows, skew, approximate structures | Pixel-perfect BI warehouse only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Event meaning? | `play_start` / heartbeat watch-minutes | Define metric clearly |
| F2 | Top-K by what? | **Watch-minutes** in window (or starts) | Aggregation key `(title_id)` |
| F3 | Windows? | Last **1 hour** primary; optional 1d/1w | Sliding or hopping |
| F4 | K? | Top 10 (extendable to 50) | Heap / sketches |
| F5 | Dimensions? | Global + optional geo/device | Separate keyed streams |
| F6 | Dashboard? | Polling or push refresh every few seconds | Materialized top-K store |
| F7 | Late events? | Allowed with watermark grace | Retract/update policy |
| F8 | Dedup? | At-least-once ingest → idempotent aggregate | Event_id dedupe window |
| F9 | Catalog join? | Title metadata for display | Cached dimension join |
| F10 | Historical? | Trend chart Phase 1.5 | Hot realtime + warm store |
| F11 | Exact vs approx? | Exact for top-10 if feasible; approx at 1000× | Count-Min / SpaceSaving |
| F12 | Abuse? | Bot plays filtered | Fraud signals pre-agg |

**MVP scope:**

1. Ingest viewing events with `event_time`, `title_id`, `user_id`, `watch_seconds`.  
2. Maintain **top-10 by watch-minutes over last 1 hour** (event time).  
3. Dashboard API returns ranked list + scores + freshness timestamp.  
4. Handle late events within grace (e.g. 5–15 min).  
5. Idempotent processing for retries.  
6. Basic global board; optional one dimension (country).

**Out of MVP:** personalized top-K per user, perfect global exactly-once with zero approx, full warehouse modeling class, ML recs.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Dashboard freshness | < 10–30s end-to-end typical |
| N2 | Ingest durability | Accepted events not lost |
| N3 | Correctness | Event-time windows; documented late policy |
| N4 | Availability | Dashboard degrade to last good snapshot |
| N5 | Cost | Stream compute dominated—budget sketches at scale |
| N6 | Scale | See table; partition by title hash / time |

### 1.3 Cases

**Happy:** Plays stream in → window aggregates update → top-10 API shows new leader within seconds.  

| Case | Behavior |
|------|----------|
| Duplicate event | Dedupe by `event_id` / idempotency store |
| Late by 2 min | Included if within watermark grace; board updates |
| Late beyond grace | Side output / warm correction job; not realtime |
| Popular title hotspot | Key fan-out / local top-N merge |
| Catalog rename | Dimension join by `title_id` stable |
| Clock skew producer | Prefer event_time from client carefully; server receive_time for watermark bounds |
| Dashboard poll storm | Cache top-K blob; CDN/edge |
| Poison event | DLQ; don’t stall partition forever |
| Empty window night | Return empty/sparse with confidence |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Events / day | 500M | 5B | 50B | 500B |
| Peak event QPS | ~20K | ~200K | ~2M | ~20M |
| Unique titles | 100K | 200K | 500K | 1M |
| Distinct users / day | 5M | 50M | 200M | 500M |
| Dashboard QPS | 100 | 1K | 10K | 50K |
| Windows | 1h | 1h+1d | +1w | multi + geo |
| Allowed E2E lag | 30s | 20s | 15s | 10–30s (approx OK) |

**Jumps:** 10× = partitioned stream jobs; 100× = two-stage top-K merge; 1,000× = approximate heavy-hitters + hierarchical aggregation.

### 1.5 Scope repeat-back

> Streaming top-K movies/series dashboard over event-time windows (hourly), with idempotent ingest, watermarks/late handling, materialized leaderboard reads, and progressive approximation as event rates grow to millions/sec.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic

```text
Baseline peak 20K events/s
If each event ~200 B: 20K × 200 = 4 MB/s ingest
100×: 2M × 200 B = 400 MB/s
1000×: 20M × 200 B = 4 GB/s → multi-region ingress + batching
```

### 2.2 State size (exact sliding 1h)

```text
Need per-title counts in window.
Titles 100K active: trivial.
If using per-minute buckets × 60:
100K × 60 × 16 B ≈ 96 MB counters—fine

At 1M titles × 60 × geo=100:
1e6 × 60 × 100 × 16 B ≈ 96 GB → shard; drop cold combos
```

### 2.3 Dashboard

```text
Top-10 payload ~2 KB; 10K QPS → 20 MB/s easy with cache
Never compute top-K from raw events on request
```

### 2.4 Bottlenecks

1. Hot partition for mega-hit premiere  
2. Exact unique-viewer HyperLogLog cost if metric is UV  
3. Late-data reordering buffers  
4. Dashboard thundering without cache  
5. Join explosion with huge dimension fan-out  

---

## 3. High-Level Design

### 3.1 Metric definition (lock early)

| Metric | Pros | Cons |
|--------|------|------|
| Play starts | Simple | Gameable; short previews |
| Watch-minutes | Better engagement | Needs heartbeats |
| Unique viewers | Nice dashboard | Needs HLL / UV store |

**MVP pick:** **watch-minutes** from periodic heartbeats (e.g. every 60s) with `watch_seconds` delta.

### 3.2 Window types

| Type | Semantics | Use |
|------|-----------|-----|
| Tumbling 1h | [12:00,13:00) | Simple hourly boards |
| Sliding 1h hop 1m | Last 60 minutes | “Live” dashboard |
| Session | Per user watch | Not top-K global |

**MVP:** Sliding 1h with 1-minute hops (or continuous with minute buckets).

### 3.3 Processing architecture options

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Batch every minute SQL | Simple | Lag; costly scans | Claiming sub-10s at 2M/s |
| B. Stream processor (Flink/Spark Streaming) | Event-time native | Ops | — |
| C. Kafka Streams app | Lightweight | Very large state care | — |
| D. Redis INCR + ZSET | Fast MVP | Late events hard; memory | Exact late retract at 1000× |

**Chosen path:**

- **MVP:** Event log (Kafka) → stream job with **minute buckets** + heap/ZSET per window → Redis/DB **leaderboard snapshot**.  
- **100×+:** Two-stage aggregation; approx heavy-hitters if needed.

### 3.4 Exact top-K with minute buckets

```text
For each minute m, key title_id → minutes_watched
Last 60 minutes score(title) = sum(bucket[m-59..m])
Maintain:
  - bucket maps (sharded)
  - global sorted structure OR periodic recompute top-K from actives
Optimization: keep per-shard local top-K; merge to global every few seconds
```

### 3.5 Approximate structures (1000×)

| Structure | Use |
|-----------|-----|
| Count-Min Sketch | Approx counts; then track candidates |
| SpaceSaving / Misra-Gries | Heavy hitters |
| HLL | Unique viewers |
| t-digest | Latency-like distributions (less for top-K titles) |

**Deal-breaker:** Selling CMS sketch as exact billing.

### 3.6 Late data & watermarks

```text
watermark ≈ max_event_time - skew - grace
Allowed lateness L: update buckets if event_time >= watermark - L
Else: late side-output → cold corrector (hourly reconcile)
```

### 3.7 Idempotency

```text
event_id UUID from client/session sequence
Processor dedupe store: Bloom + short KV TTL (e.g. 2h) OR Kafka EOS transactional sink
At-least-once → aggregates use additive deltas with dedupe
```

### 3.8 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Query path | Materialized top-K | Fast | Ad-hoc scan raw |
| Time | Event-time + watermark | Correctness | Processing-time only pretending event-time |
| Hot keys | Local top + merge | Scale | Single global Redis INCR hotspot |
| Exactness | Exact MVP; approx later | Honesty | Fake exact at 20M/s |
| Catalog | Cached dim join | UX | Sync join to OLTP catalog each event |

### 3.9 Components

1. Client / player event SDK  
2. Ingest gateway / Kafka topics  
3. Stream top-K jobs (sharded)  
4. Bucket state store  
5. Leaderboard merger  
6. Snapshot store (Redis)  
7. Dashboard API  
8. Catalog cache  
9. Late-event corrector  
10. Observability (lag, watermark)  

---

## 4. Architecture Diagram

```text
Players --> Ingest API --> Kafka (view-events)
                              |
                              v
                    +------------------+
                    | Stream TopK Job  |  (event-time, watermarks)
                    | shard by title   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
      Minute Bucket State            Local Top-K
              |                             |
              +-------------+---------------+
                            v
                   Global Merger (periodic)
                            v
                   Redis Leaderboard Snapshot
                            v
                      Dashboard API --> UI
                            ^
                      Catalog Cache
```

### 4.1 Event → board sequence

```text
heartbeat(event_id, title, watch_sec, event_time)
  → Kafka
  → job dedupe
  → add to minute bucket
  → update local candidate heap
  → merger publishes top-10 snapshot {as_of, watermark, ranks[]}
```

### 4.2 Late event

```text
if event_time in grace: update bucket + mark dirty window → merger refresh
else: side_output → async reconcile (may fix warm store, not always live board)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Accepted ingest durable in log before ACK.  
2. Processing idempotent w.r.t. `event_id`.  
3. Dashboard reads **snapshots**, not in-flight inconsistent heaps.  
4. Watermark monotonic per stream partition (careful with idle sources).  
5. Poison events isolated.  
6. Snapshot includes `as_of` + `watermark` for honesty.  
7. Reconcile job can rebuild from Kafka/raw buckets for a window.  
8. Metric definition versioned (`metric_v1`).  

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Kafka + one Flink job; Redis ZSET; exact buckets |
| 10× | Partition jobs; multi-consumer; cache API |
| 100× | Two-stage merge; geo dimensions; state RocksDB tuning |
| 1000× | Approx heavy-hitters; hierarchical merge; region local boards |

### 5.3 Maintainability

- Schema registry for events.  
- Metric definition as config.  
- Replay from Kafka for bugfix.  
- Canary consumer group on subset partitions.  
- Golden tests for late/watermark.

### 5.4 Progressive scale

**1×:** Single cluster; exact minute buckets; top-10 global.  
**10×:** Sharded state; dashboard CDN cache.  
**100×:** Multi-window; country boards; merger service.  
**1000×:** Sketches; premieres isolation; multi-region.

### 5.5 Hot title premiere

Drop of a hit show → one `title_id` dominates QPS.

Mitigations: sub-shard by `user_id % N` then combine; write buffers; separate “hot key” pipeline.

### 5.6 Deal-breakers

| Temptation | Failure |
|------------|---------|
| SQL full scan each request | Meltdown |
| Processing-time as “last hour” | Wrong under backlog |
| No dedupe with at-least-once | Inflated ranks |
| Exact UV with Set per title at 1000× | Memory blowup |
| Hide watermark from API | Misleading ops |

---

## 6. Wrap-Up

### 6.1 Designed

Streaming minute-bucket aggregates with event-time watermarks, sharded local top-K + global merge, materialized dashboard snapshots, late-event grace + reconcile, progressive approximation.

### 6.2 Decisions to defend

1. Lock metric = watch-minutes  
2. Event-time sliding hour via minute buckets  
3. Materialized leaderboard reads  
4. Idempotent stream processing  
5. Two-stage merge for hot keys  
6. Honest approx at extreme scale  
7. Snapshot metadata (`as_of`, watermark)  

### 6.3 Risks

- Watermark stalls on dead partition  
- Bot inflation  
- Catalog inconsistency  
- Merger lag  
- Replay cost  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Metric + window + K |
| 5–15 | Ingest + buckets |
| 15–28 | Top-K algorithm + merge |
| 28–38 | Late data + idempotency |
| 38–45 | Scale approx + traps |

### 6.5 Closer

> **Top-K movies:** event-time minute buckets, sharded heavy-hitter merge, snapshot dashboard, late grace with reconcile—approx only when exact state can’t fit.

---

## 7. Deeper / Related Interview Questions

### 7.1 Windows

**Q: Sliding vs tumbling?**  
A: Sliding for live “last hour”; tumbling for “hour-of-day leaderboard.”

**Q: Hop size trade-off?**  
A: 1-minute hop: good UX; more compute than 5-minute hop.

### 7.2 Algorithms

**Q: How to maintain top-10 efficiently?**  
A: Min-heap of size K for candidates; or Redis ZSET; or merge local tops.

**Q: Why not sort all titles every second?**  
A: O(N log N) waste; only actives matter.

**Q: Count-Min error?**  
A: Over-estimate; use for candidate generation then exact recount on candidates if needed.

### 7.3 Late data

**Q: What is a watermark?**  
A: Lower bound on event_time completeness (with assumptions).

**Q: Retracting counts?**  
A: If needed, store bucket deltas; late same event_id shouldn’t double—dedupe first.

### 7.4 Exactly-once

**Q: Kafka transactions EOS?**  
A: Possible; still design idempotent sinks. Don’t handwave.

### 7.5 Uniques

**Q: Top titles by UV?**  
A: HLL per title per minute bucket; merge HLLs—memory heavier than sums.

### 7.6 Dashboard

**Q: Push or poll?**  
A: Poll cached snapshot every 5s fine; SSE optional.

### 7.7 Fraud

**Q: Farmed plays?**  
A: Filter before agg: velocity, device reputation, completion ratio.

### 7.8 Interview traps

| Trap | Pushback |
|------|----------|
| “Redis INCR is the design” | Late/event-time missing |
| Ignore hot keys | Premiere SEV |
| Exact Set UV at 20M/s | Impossible cheaply |
| No watermark discussion | Junior signal |

### 7.9 Metrics

| Metric | Why |
|--------|-----|
| Ingest lag | Pipeline health |
| Watermark lag | Correctness UX |
| Snapshot age | Dashboard SLO |
| Dedupe hit rate | Retry storm |
| Hot partition CPU | Scale |

### 7.10 Uber cousins

Same pattern as **realtime restaurant metrics** and **sliding-window top-K**—reuse vocabulary (watermarks, merge, snapshots).

---

## 8. Appendices

### 8.1 Event schema

```json
{
  "event_id": "uuid",
  "user_id": "u",
  "title_id": "t",
  "watch_seconds": 60,
  "event_time": "RFC3339",
  "country": "US",
  "device": "ios",
  "metric_v": 1
}
```

### 8.2 API checklist

- [ ] `GET /v1/topk?window=1h&k=10&country=US`  
- [ ] Response includes `as_of`, `watermark`, `metric`, ranks  
- [ ] Admin `POST /v1/rebuild?window_start=`  
- [ ] Ingest `POST /v1/events` (or agent→Kafka)  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Event time | When watch happened |
| Processing time | When job saw it |
| Watermark | Completeness belief |
| Heavy hitter | High-frequency key |
| Snapshot | Materialized top-K view |
| Hop | Sliding step |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Kafka, minute buckets, Redis top-K, dedupe |
| 10× | Sharded jobs, API cache |
| 100× | Local top merge, multi-window |
| 1000× | Sketches, hierarchical agg, hot-key path |

### 8.5 Merger pseudocode

```text
every 2s:
  locals = collect(shard_local_topk[1..N], k*M)
  global = top_k(sum_by_title(locals), k)
  write_snapshot(global, now, min_watermark)
```

### 8.6 Bucket key design

```text
key = (window_type, minute_ts, title_id, dim?)
value = int_minutes
TTL = 2h for 1h window
```

### 8.7 Interview “say this” (60s)

> Ingest watch heartbeats to Kafka; aggregate watch-minutes into event-time minute buckets with watermarks and idempotent dedupe; maintain sharded local top-K and merge to a cached snapshot the dashboard reads; use sketches only when exact state won’t fit; expose freshness metadata.

### 8.8 Reliability tests

1. Duplicate event_id → count once.  
2. Late +5 min within grace → rank updates.  
3. Late +2h → not in live board; reconcile path.  
4. Kill job → restore from Kafka/state.  
5. Hot title → no single-partition death.  

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Snapshot age p99 | < 30s |
| Ingest ACK p99 | < 100ms |
| Lost accepted events | ≈0 |
| Rank stability jitter | Documented |

### 8.10 Approx error communication

```text
API field: "approximation": "none"|"cms"|"spacesaving"
"error_bound": "..."
Never silently approx
```

### 8.11 Related systems map

```text
Events → Kafka → Stream Agg → Snapshots → Dashboard
                      ↓
                 Late side-output → Reconcile
```

### 8.12 Unit checks

```text
2M events/s × 200 B = 400 MB/s
60 minute buckets × 500K titles × 8 B ≈ 240 MB counter state (order-of) before dimensions
```

### 8.13 Fraud filter placement

```text
SDK → edge filters (cheap) → Kafka → stream filters (richer) → agg
Don’t remove fraud post-dashboard only
```

### 8.14 Multi-window storage

| Window | Bucket grain | Retain |
|--------|--------------|--------|
| 1h | 1 min | ~2h |
| 1d | 5–15 min | ~2d |
| 1w | 1h | ~8d |

### 8.15 Extra traps

| Trap | Pushback |
|------|----------|
| Top-K in MySQL trigger | No |
| Client computes global top | Cheat/spam |
| One ZSET forever without TTL | Memory leak |

### 8.16 Watermark idle problem

```text
Idle partition stops advancing watermark → stall
Idle-source heartbeats / withIdleness in Flink-like systems
```

### 8.17 Catalog join

```text
Enrich at snapshot serve time from cached title metadata
Avoid per-event RPC to catalog service
```

### 8.18 Comparison table: exact vs approx

| Criterion | Exact buckets | SpaceSaving |
|-----------|---------------|-------------|
| Memory | O(active titles × buckets) | O(k_candidates) |
| Error | 0 (modulo late) | Bounded oversights |
| When | ≤100× typical | 1000× / many dims |

---

---

## Part II — LLD / Object Model

### 9.1 Responsibilities

| Class | Owns |
|-------|------|
| `ViewEvent` | Immutable ingest record (`event_id`, `title_id`, `watch_seconds`, `event_time`) |
| `DedupeStore` | `(event_id)` seen window ~2h |
| `MinuteBucket` | `(minute_ts, title_id) -> watch_minutes` additive counter |
| `WindowAggregator` | Sliding 1h = sum last 60 minute buckets |
| `LocalTopK` | Min-heap / ZSET of size K per shard |
| `GlobalMerger` | Periodic merge of shard locals → snapshot |
| `LeaderboardSnapshot` | Immutable ranked list + metadata |
| `DashboardService` | Read-only serve from latest snapshot |
| `LateEventRouter` | Grace vs side-output decision |
| `CatalogEnricher` | Join title metadata at serve time |

### 9.2 Class diagram

```text
StreamProcessor
  --> DedupeStore
  --> MinuteBucketStore
  --> WindowAggregator
  --> LocalTopK
       |
       v
GlobalMerger --> LeaderboardSnapshotStore --> DashboardService
                      ^
               CatalogEnricher
LateEventRouter --> SideOutputSink (reconcile job)
```

### 9.3 Window aggregator

```text
class SlidingHourAggregator:
  buckets: Map[MinuteTs, Map[TitleId, int]]

  def add(event: ViewEvent):
    m = floor_minute(event.event_time)
    buckets[m][event.title_id] += event.watch_seconds
    evict buckets older than now-2h

  def score(title_id) -> int:
    return sum(buckets[m][title_id] for m in last_60_minutes())
```

### 9.4 Local top-K maintenance

```text
class LocalTopK:
  heap: MinHeap size K  # min at root = K-th largest

  def consider(title_id, score):
    if score > heap.min_score or heap.size < K:
      heap.upsert(title_id, score)
```

Merger combines **candidate sets** from each shard (top 2K each), re-sums scores, extracts global top K.

### 9.5 Late event policy object

```text
class LateEventPolicy:
  grace: Duration

  def route(event) -> LIVE | RECONCILE:
    if event.event_time >= watermark - grace: return LIVE
    return RECONCILE
```

### 9.6 Snapshot immutability

```text
class LeaderboardSnapshot:
  ranks: List[RankEntry]  # frozen at publish
  as_of: Instant
  watermark: Instant
  metric_version: int
  approximation: NONE | CMS | SPACESAVING
```

Dashboard reads never mutate snapshot; publish new version every 2–5s.

### 9.7 Concurrency

- Stream partition = single-threaded processing per key subset → no cross-partition locks.  
- Merger single leader with fencing epoch; followers standby.  
- Dedupe store: partition-local Bloom + KV; false positive → slight undercount acceptable vs double count.

### 9.8 Extensibility

- `MetricStrategy` interface: `WatchMinutes`, `PlayStarts`, `UniqueViewers(HLL)`  
- `WindowSpec` tumbling vs sliding hop config  
- `DimensionKey` for country/device boards without rewriting core aggregator

### 9.9 Unit tests

1. Same `event_id` twice → one bucket increment.  
2. Event at minute boundary → correct bucket.  
3. Merger with skewed shard tops → correct global rank.  
4. Watermark advance → late within grace updates snapshot.

### 9.10 Interview LLD closer

> Model events as immutable; buckets as additive state; top-K as mergeable summaries; snapshots as the only dashboard read surface—keeps streaming math testable without a database GROUP BY on every poll.

---

*End of top-K movies dashboard system design.*
