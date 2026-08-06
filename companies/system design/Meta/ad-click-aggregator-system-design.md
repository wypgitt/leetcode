# System Design: Ad Click Aggregator

> **Focus areas:** High-rate ingest · Dedup · Stream aggregation · Advertiser analytics · Exactly-once business · Hot keys  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split click ingest vs query planes, explicit deal-breakers for “UNIQUE(click_id) in OLTP at 5M/s” fantasies  
> **Interview theme:** Meta L5+ ads infra — fraud-aware counting, windowed aggregates, advertiser-facing freshness SLOs

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

Goal: **bound the product**—an **ad click aggregator** that ingests massive click (and optionally impression) streams, **deduplicates**, aggregates by advertiser/campaign/ad/creative/time, and serves **analytics dashboards** with clear freshness and correctness SLOs—without pretending every raw click is a primary-key OLTP row forever.

### 1.0 What this is / is not

| Dimension | **Ad click aggregator (this doc)** | Not this |
|-----------|------------------------------------|----------|
| Primary job | Ingest → dedup → aggregate → serve stats | Full ads auction / ranking / billing ledger deep dive |
| Success | Accurate-enough counts; low fraud pollution; fresh dashboards | Perfect forensic replay UI MVP |
| Ingest | Multi-million events/s class at scale | Batch nightly only (hooks OK) |
| Query | Campaign metrics by time range / dims | Arbitrary data-science SQL warehouse (export OK) |
| Money | Feeds billing; not full invoicing product | Double-entry finance system |

**Scope statement:** Design Meta-style ad click aggregation: high-rate ingest, dedup, stream windows, advertiser analytics—with progressive scale and explicit fraud/dedup tradeoffs.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Events? | Clicks MVP; impressions Phase 1.5 | Schema with `event_type` |
| F2 | Dedup key? | `click_id` / `(user,ad,ts_bucket)` policy | Dedup store with TTL |
| F3 | Dimensions? | advertiser, campaign, ad, country, platform | Aggregate key design |
| F4 | Time grains? | 1m, 1h, 1d | Rollups |
| F5 | Freshness? | Minutes for dashboards; seconds for alerts | Stream + micro-batch |
| F6 | Fraud? | Filter bots / invalid traffic | Fraud score pipeline |
| F7 | Query API? | Timeseries + totals + breakdowns | OLAP / pre-agg store |
| F8 | Export? | CSV / warehouse sync Phase 1.5 | Batch sink |
| F9 | Attribution? | Last-click light MVP optional | Separate from raw counts |
| F10 | Realtime alerts? | Spike / budget pace Phase 1.5 | Threshold jobs |
| F11 | Multi-region? | Yes global ads | Regional agg → global |
| F12 | Historical restate? | Yes when fraud model updates | Reprocess from log |

**MVP functional scope:**

1. Ingest click events via edge collectors → durable log.  
2. Validate schema; enrich geo/platform.  
3. **Dedup** within TTL window.  
4. Fraud/invalid filter (rules MVP).  
5. Stream aggregate counts/sum spend signals by dims × time buckets.  
6. Serve advertiser analytics API: range queries, group-by campaign/ad.  
7. Roll up 1m → 1h → 1d.  
8. Late event handling with bounded lateness.  
9. Basic admin: replay, drop bad traffic segments.

**Out of MVP:**

- Full auction + pacing controller  
- Complex multi-touch attribution graph  
- Perfect ML fraud as sole gate  
- Pixel-perfect identity graph across devices  
- Advertiser UI pixel design

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability | No silent loss after ACK | Kafka multi-AZ |
| N2 | Dedup correctness | Near-exact within TTL | ≤0.1% dup residual target |
| N3 | Dashboard freshness | Near realtime | p99 lag < 1–5 min |
| N4 | Query latency | Interactive | p99 < 200–500ms pre-agg |
| N5 | Ingest availability | Critical | 99.99% edge receive |
| N6 | Privacy | Ads + user data sensitive | Aggregation; minimize raw retention |
| N7 | Multi-tenant isolation | One advertiser can’t see another | AuthZ on query |
| N8 | Restate ability | Replay from log | Immutable raw log retention policy |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User clicks ad → pixel/SDK event → ingest → dedup → agg → dashboard +1.  
2. Advertiser opens campaign last 24h chart → pre-agg 1h buckets merge.  
3. Burst campaign → streaming windows keep up; query still hits rollups.  
4. Late click (+30s) → still counted within lateness; updates bucket.  
5. Fraud rule marks datacenter IP → invalid; excluded from billable.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate `click_id` retries | Dedup drop; metric `dup_dropped` |
| Missing `click_id` | Synthesize weak key or reject per policy |
| Hot ad_id skew | Salted aggregation; hierarchical combine |
| Clock skew from clients | Server receive time + client ts policy |
| Kafka lag spike | Serve last rollup; alert freshness SLO |
| Fraud model false positive | Restate job; quarantine flag not hard-delete raw |
| Query huge range unagg | Reject or force downsampled |
| Advertiser IDOR | Strict tenant authZ |
| Poison event schema | DLQ; don’t block partition forever |
| Reprocess doubles counts | Versioned agg store / idempotent upsert |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak clicks/s | 100K | 1M | 10M | 100M |
| Peak impressions/s (later) | 1M | 10M | 100M | 1B |
| Distinct ads active | 1M | 5M | 20M | 50M+ |
| Advertisers | 100K | 500K | 2M | 10M |
| Dedup TTL | 24h | 24h | 24–48h | policy |
| Agg keys / minute | 5M | 50M | 500M | hierarchical |
| Dashboard QPS | 5K | 50K | 500K | 5M |
| Raw retention | 7–30d | 7–30d | 3–7d hot | tiered |
| Fraud checks/s | 100K | 1M | 10M | 100M |

**What each jump forces:**

- **10×:** Flink/streaming mandatory; Bloom/Rocks dedup; rollup tables; no OLTP per click.  
- **100×:** Regional ingest+agg cells; global merge for rollups; hot-key salting; columnstore.  
- **1,000×:** Hierarchical dims; approximate early counts + exact settle; edge aggregation; aggressive raw tiering.

### 1.5 Etc. (Constraints & Assumptions)

- Auction/serving path emits events; we design aggregation analytics plane.  
- Billing may consume our **billable click** stream—keep join keys stable.  
- Client clocks lie; define event-time policy.  
- GDPR/CCPA: raw click retention limits; prefer aggregates.  
- “Exact” means business-exact after settle, not microsecond global linearizability.

**Scope statement to repeat back:**

> Design an ad click aggregator: durable high-rate ingest, TTL dedup, fraud filtering, stream window aggregation into advertiser analytics with rollups—scaling 10× / 100× / 1,000× via regional cells and hierarchical merges, never inserting every click as a forever-unique OLTP row on the hot path.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Edge ingest** | HTTP/SDK beacons | 100K/s | 1M/s | Edge collectors |
| **Kafka produce** | Raw clicks | 100K/s | 1M/s | Log |
| **Dedup checks** | Membership | 100K/s | 1M/s | Bloom/Rocks |
| **Agg updates** | Keyed state | ~tens of K–M keys/s | ×10 | Flink |
| **Rollup writes** | OLAP upserts | much smaller | ×10 | Druid/ClickHouse/Pinot |
| **Query reads** | Dashboards | 5K/s | 50K/s | OLAP + cache |

**Anti-pattern:** one QPS number for beacons + SQL dashboard queries.

### 2.2 Payload & bandwidth

```text
Click event ~200–500B after enrichment
100K/s × 300B = 30 MB/s ≈ 1 PB/year order raw (before compression/replication)
10× → 300 MB/s
100× → 3 GB/s → regional cells + compression + short raw TTL mandatory
```

### 2.3 Dedup memory

```text
Naive Redis SET of click_id for 24h:
  100K/s × 86400 ≈ 8.64B ids/day
  16B id hash × 8.64B ≈ 138 GB/day equivalent footprint (plus Redis overhead) — painful

Better:
  Partitioned Bloom (false positive ε) + short exact store for recent
  Or RocksDB keyed state in Flink with TTL
  Or Cassandra/Dynamo with TTL on click_id (at 100× cost careful)

DEAL-BREAKER: single Redis instance exact SET for global 24h at 1M/s
```

### 2.4 Aggregation cardinality

```text
dims: campaign × country × platform × minute
1e6 campaigns × 200 countries × 5 platforms = insane if dense
Reality sparse: only keys with traffic exist
Still: hot campaigns explode minute keys — rollups + top-N patterns
```

### 2.5 Query amplification

```text
Advertiser refreshes charts every 10s × 50K concurrent users = 5K QPS
Pre-agg 1m buckets: query merges ~60–1440 rows not scan raw clicks
Raw scan of 1h clicks for one campaign at 100× = deal-breaker interactive path
```

### 2.6 Fraud cost

```text
If fraud features need 10µs/event → 100K/s needs ~1 core theoretical; real >> with IO
Batch features async; rules inline; heavy ML nearline
```

### 2.7 Storage growth (raw + rollups)

```text
Raw clicks: 100K/s × 200B × 86400 ≈ 1.73TB/day compressed ~0.5–0.8TB
10×: ~17TB/day raw → object store tiers mandatory (hot 3–7d, warm 90d, cold)
100×: ~173TB/day → sample debug fields; columnar Parquet; never OLTP for raw
1,000×: ~1.7PB/day → regional lakes + lifecycle; billing uses rollups not raw scans

Rollups 1m grain:
  campaigns C × minutes/day × dims
  Example: 1M campaigns × 1440 × 8 dims-sparse ≈ careful cardinality control
  Pre-agg saves interactive queries from scanning TB → MB
```

### 2.8 Dedup memory / partition counts

```text
Exact dedup TTL 24h: 100K/s × 86400 × 16B ≈ 138GB cluster-wide (sharded by hash(click_id))
10×: ~1.4TB → RocksDB/Flink state + Bloom filter front
100×: hierarchical: Bloom → local LRU exact → remote

Kafka partitions: ≥ click_qps/1K; key hash(click_id) for dedup locality
  baseline 128–256; 100×: 2K–8K or per-cell topics
Hot campaign salt: campaign_id|salt to avoid single partition firehose
```

### 2.9 Amplification & naive cost

| Naive | Cost | Fix |
|-------|------|-----|
| Query raw clicks interactive | TB scan | Rollup store |
| Global exact dedup one Redis | Memory wall | Sharded TTL state |
| Sync fraud ML on ingest | Latency blowup | Rules inline; ML nearline |
| Per-event DB insert | OLTP death | Kafka + stream agg |
| Unbounded group_by dims | Cardinality bomb | Allowlist dims + top-N |

```text
Advertiser UI poll 10s × 50K = 5K QPS — cache metric panels by (tenant, query_hash, grain)
```

### 2.10 Early vs settled cost math

```text
Early count lag 10–60s; settled after watermark + fraud
If 2% clicks invalidated late, dashboards must show both or users scream “numbers moved”
Restate job: recompute [T0,T1] → versioned rollup; queries pin version or “latest settled”
```

### 2.11 Progressive BOTE card

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Click/s | 100K | 1M | 10M | 100M |
| Dedup state | ~140GB | ~1.4TB | cells | cells+Bloom |
| Raw/day | ~1.7TB | ~17TB | ~170TB | PB |
| Query path | rollups | +cache | Pinot/CH cells | edge cubes |

**Pitch:** “Ingest is at-least-once; business exactly-once via click_id dedup; serve rollups not raw; fraud splits early vs settled.”


---

## 3. High-Level Design

### 3.1 APIs

| Op | Semantics |
|----|-----------|
| `POST /v1/events/clicks` (edge) | Batch beacon ingest |
| `GET /v1/metrics?advertiser=&range=&grain=&group_by=` | Timeseries aggregates |
| `GET /v1/campaigns/{id}/metrics` | Campaign detail |
| `GET /v1/health/freshness` | Watermarks per pipeline |
| `POST /admin/reprocess` | Time-range restatement |
| `POST /admin/invalidation_rules` | Fraud/invalid rules |

**Click event schema:**

```text
ClickEvent {
  click_id,            // uuid from serving
  impression_id?,
  advertiser_id,
  campaign_id,
  ad_id,
  creative_id?,
  user_token_hashed,   // privacy-preserving
  ts_client,
  ts_receive,          // set at edge
  country, platform, ip_asn,
  bid_signal?, cost_micros?,
  page_url_hash?,
  fraud_features...
}
```

### 3.2 Data model (serving)

| Table / segment | Key | Value |
|-----------------|-----|-------|
| `agg_1m` | `(campaign_id, country, platform, minute)` | clicks, invalid, cost |
| `agg_1h` / `agg_1d` | rolled keys | same |
| `dedup_*` | `click_id` | TTL marker |
| `raw_clicks` log | offset | immutable events |
| `pipeline_watermark` | `job` | event-time |

### 3.3 Dedup — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **SQL UNIQUE** | Exact | Won’t ingest-scale | **Deal-breaker** hot path |
| **Redis SET TTL** | Simple | Memory at scale | Baseline small |
| **Bloom filter** | Tiny memory | False positives drop good clicks | Early filter stage |
| **Flink keyed state TTL** | Scalable exact-ish | State backend sizing | **Strong MVP** |
| **Two-level Bloom→exact** | Cost/accuracy | Complexity | 100× |

**Chosen:** keyed dedup state on `click_id` with TTL (e.g. 24h) in stream job; optional front Bloom to cut obvious dups; metrics for FP.

### 3.4 Aggregation — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Update OLTP counters live** | Simple | Hot rows; lose detail | Toy |
| **Stream window keyed agg** | Fresh; scalable | State ops | **MVP** |
| **Micro-batch every 1m** | Simple ops | Higher lag | OK for some grains |
| **Lambda (stream+batch)** | Restate friendly | Two pipelines | 100× settle |
| **Query raw always** | Flexible | Too slow/expensive | **Deal-breaker** dashboards |

### 3.5 Fraud / invalid traffic

```text
Inline rules (cheap):
  - bad ASN / datacenter
  - impossible geo teleport
  - duplicate click patterns
  - malformed / missing fields

Nearline:
  - ML score join within minutes
  - move counts from billable → invalid buckets (restate)
```

**Deal-breaker:** claiming 0% fraud with only a regex on UA.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Raw storage | Kafka + cold object | Replay | Forever hot OLTP clicks |
| Dedup | Stream state TTL | Scale | Global SQL unique |
| Serve | Rollups OLAP | Query SLA | Scan raw per chart |
| Time | Event-time + watermark | Late clicks | Pure processing-time only |
| Regions | Local agg + merge | Bandwidth | Single global counter host |
| Money path | Versioned billable counts | Restate | Mutate in place without versions |

### 3.7 Consistency model

| Object | Model | Notes |
|--------|-------|-------|
| Ingest ACK | At-least-once after Kafka | Client retries OK |
| Dedup | Exactly-once billable per click_id TTL | Bounded window |
| Early metrics | Eventually consistent seconds–minutes | Soft |
| Settled metrics | Watermark-closed | Billing grade |
| Fraud labels | Append/restate | Versioned |

**Deal-breaker:** billing off early counts without settled/restate story.

### 3.8 API edge cases

| Case | Behavior |
|------|----------|
| Duplicate click_id | Count once billable |
| Late event after watermark | Side output / restate bucket |
| Cross-tenant query | 403 |
| Huge group_by cardinality | Reject / top-N |
| Freshness endpoint | Expose lag; don’t hide |
| Invalid traffic | Counted separately; not billable |
| Clock skew edge | Receive-time bound + event-time |

### 3.9 Serving schema indexes

```text
rollups_1m: PK (tenant_id, campaign_id, ts_minute, dim_hash)
  INDEX (tenant_id, ts_minute) 
  projections: sum(clicks), sum(billable), sum(cost_micros), HLL(users)
raw_debug: object store only; indexed via manifest partitions date/campaign
dedup_state: key click_id; TTL 24–72h; sharded
```

### 3.10 HLD pitch

> “Edge collect → Kafka → stream dedup + rules → early rollups; nearline fraud → settled rollups. Query Pinot/CH/Druid cubes. Never interactive raw scans. Multi-tenant authZ on every metric read.”


---

## 4. Architecture Diagram

```text
  Apps / Mobile / Web pixels
           |
           v
  +--------------------+
  | Edge Collectors    |  validate, set ts_receive, batch compress
  | (PoP / region)     |
  +---------+----------+
            |
            v
  +--------------------+
  | Kafka: clicks.raw  |  partitions by hash(click_id) or campaign
  +---------+----------+
            |
            v
  +--------------------+
  | Stream Jobs        |
  | 1) schema+enrich   |
  | 2) dedup TTL       |
  | 3) fraud rules     |
  | 4) keyed aggregate |
  +---------+----------+
            |
            +-------------------+--------------------+
            |                   |                    |
            v                   v                    v
   +----------------+   +----------------+   +------------------+
   | Rollup sink    |   | Billable topic |   | DLQ / invalid    |
   | 1m segments    |   | for billing    |   | traffic          |
   +--------+-------+   +----------------+   +------------------+
            |
            v
   +----------------+       +------------------+
   | OLAP store     |<----->| Rollup compactor |
   | Pinot/CH/Druid |       | 1m→1h→1d         |
   +--------+-------+       +------------------+
            |
            v
   +----------------+       +------------------+
   | Metrics API    |------>| Advertiser UI    |
   | authZ tenant   |       | dashboards       |
   +----------------+       +------------------+

   Control: watermarks, reprocess, rule config, freshness SLO board
```

**Ingest path:**

```text
Beacon batch → edge ACK (buffer durably)
  → Kafka (at-least-once)
  → processing idempotent on click_id
```

**Aggregate path:**

```text
keyBy(campaign_id, country, platform, window_start)
  -> incr clicks / cost
  -> emit upsert to OLAP / serving topic
```

**Query path:**

```text
AuthZ advertiser_id
  -> plan grain (1m/1h/1d) from range
  -> scatter-gather segments
  -> return series
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **ACK only after durable log accept** (or edge WAL).  
2. **Dedup window documented**; outside TTL duplicates may count (rare).  
3. **Billable vs invalid** separated; raw retained for restate.  
4. **Tenant isolation** on every query.  
5. **Watermark exposed**; dashboards can show “data through T”.  
6. **Reprocess is versioned** (pipeline_version / settle_version).

#### 5.1.2 Data loss & duplication

| Mode | Behavior |
|------|----------|
| At-least-once ingest | Dup click_ids expected → dedup |
| Lost without ACK | Client retries |
| Sink dual-write | Idempotent upsert by agg key + version |
| Exactly-once Flink | Checkpoints + transactional sink where supported |

**Deal-breaker:** at-least-once without any dedup story while promising exact billing counts.

#### 5.1.3 Idempotency

```text
click_id is the idempotency key for counting
agg upserts use (dims, bucket, pipeline_version) as primary
reprocess writes to new version then atomic pointer swap for serving
```

#### 5.1.4 Retry & DLQ

- Poison messages → DLQ after N fails; alert.  
- Transient OLAP sink fail → restart from checkpoint.  
- Edge buffer spills to disk if Kafka down briefly.

#### 5.1.5 Rate limiting

| Limit | Purpose |
|-------|---------|
| Per-IP beacon rate | Abuse |
| Per-publisher inject | Partner abuse |
| Query QPS / advertiser | Noisy neighbor |
| Reprocess concurrency | Protect cluster |

#### 5.1.6 Failure modes by scale

| Scale | Failure | Mitigation |
|-------|---------|------------|
| Baseline | Duplicate beacons | click_id dedup |
| 10× | Hot campaign partition | Salting |
| 100× | State backend OOM | Bloom+Rocks; cellize |
| 1,000× | Cross-region double count | Home region + idempotent merge |

#### 5.1.7 Retries / backoff / DLQ

```text
Edge → Kafka: retry with jitter; drop only after N with metric (rare)
Stream operator fail: checkpoint restore; idempotent sink upsert
Poison event: DLQ + skip; don’t stall watermark forever
Query 429 on heavy tenants: fair scheduling
```

#### 5.1.8 Data-loss prevention

1. Kafka multi-AZ; producer acks=all.  
2. Rollup sinks idempotent upsert by primary key.  
3. Raw durable before ACK to SDK when possible (or accept small loss with product OK).  
4. Restate from raw for billing disputes.  
5. Never “delete invalid” without archive.

#### 5.1.9 Consistency under partition

```text
Two regions ingest same click_id: dedup home by hash(click_id) OR include region in id
Split-brain rollup writers: single sink leader per key range
Serve stale early metrics with freshness banner if merger lags
```

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Jump | Change |
|------|--------|
| Baseline | Kafka + Flink + ClickHouse/Pinot; Redis Bloom optional |
| **10×** | Rocks TTL dedup; 1m rollups; query cache; partition tuning |
| **100×** | Regional pipelines; hot-key salting; hierarchical rollups; settle batch |
| **1,000×** | Edge partial agg; approximate early + daily exact settle; column tiers |

#### 5.2.2 Partitioning

```text
Kafka: hash(click_id) for dedup locality OR hash(campaign_id) for agg locality
Tradeoff: pick based on stage
  - dedup stage prefers click_id
  - may repartition by campaign for agg
```

#### 5.2.3 Hot campaign / viral ad

```text
Detect key rate > threshold
  -> salt key into N subkeys
  -> periodic combine to campaign total
  -> OLAP still stores campaign-level after combine
```

#### 5.2.4 Late data & watermarks

```text
allowed_lateness = 2–15 minutes (product)
within: update bucket
beyond: side output → occasional correction channel or drop+metric
Billing settle: T+1h / T+1d exact job reconciles
```

#### 5.2.5 Lambda architecture lite

```text
Speed layer: stream 1m approx/early billable
Batch layer: daily recompute from raw with latest fraud model
Serving: prefer settled when available; else early
```

#### 5.2.6 Multi-region

| Path | Strategy |
|------|----------|
| Ingest | Regional Kafka |
| Dedup | Regional (click_id rarely crosses); global dedup only if needed via id design |
| Rollups | Regional segments + query fanout OR merged global store async |
| Query | Route to regions holding data; or replicated OLAP |

#### 5.2.7 Cache hierarchy

```text
Edge beacon: batching only
Query: panel cache (tenant, hash) 5–30s
Rollup store memory columns
Raw lake: cold
```

#### 5.2.8 Backpressure

```text
Kafka lag > SLO → scale consumers; shed non-billable debug fields
Fraud nearline lag → early still serves; settled delayed (explicit)
```

#### 5.2.9 Path evolution

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Ingest | more partitions | regional Kafka | geo cells |
| Dedup | sharded Redis/Rocks | Flink state | hierarchical Bloom |
| Agg | 1m rollups | real-time cubes | pre-cubes at edge |
| Query | cache | replica fans | tenant isolation pools |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
dedup_ttl_h: 24
allowed_lateness_s: 120
grains: [1m, 1h, 1d]
fraud_rules_version: 42
pipeline_version: 7
raw_retention_d: 14
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `ingest_events_per_s` | Load |
| `kafka_lag` | Freshness |
| `dedup_drop_ratio` | Retries/fraud |
| `invalid_ratio` | Traffic quality |
| `watermark_delay` | SLO |
| `olap_upsert_fail` | Serving gaps |
| `query_p99_ms` | UX |

#### 5.3.3 Testing

- Duplicate injection tests.  
- Late event tests around watermark.  
- Hot-key chaos.  
- Reprocess produces stable version swap.  
- AuthZ negative tests across tenants.

#### 5.3.4 Operability

- Shadow pipeline `v_next` compare counts.  
- Kill-switch fraud rule.  
- Backfill tooling with rate limit.  
- Data quality monitors (null dims, negative cost).

### 5.4 Stream semantics deep dive

```text
Watermark = max_event_ts - allowed_lateness
Early emit: speculative aggregates
Settled: on watermark close + fraud join
Exactly-once sink: upsert keys (tenant, campaign, minute, dims)
```

### 5.5 Fraud pipeline

```text
Inline: IP/UA/velocity/bot lists (µs–ms)
Nearline: graph/device clusters (minutes)
Offline: model training; feed lists back
Invalid retained for forensics; billable flag false
```

### 5.6 Progressive evolution table

| Stage | Dedup | Agg | Serve |
|-------|-------|-----|-------|
| MVP | Redis TTL | Flink 1m | SQL rollup |
| Prod | Rocks/Flink | +fraud join | Pinot/CH |
| Scale | Cells | hierarchical | multi-tenant QoS |


---

## 6. Wrap-Up

### 6.1 What we designed

An **ad click aggregator**: edge ingest → Kafka → dedup + fraud → stream rollups → OLAP analytics API, with reprocess/settle for billing-grade numbers—not a giant unique-constrained SQL table of every click.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Exact vs early | Early stream + settle batch |
| Dedup | Stream TTL state; Bloom assist |
| Query | Always pre-agg for interactive |
| Regions | Ingest/agg local; query fanout/merge |
| Fraud | Rules inline; ML nearline + restate |

### 6.3 30-second scale narrative

> Baseline: Kafka + Flink dedup/agg into OLAP rollups. 10× forces state-backend dedup and strict rollups. 100× regional cells + hot-key salting + settle jobs. 1,000× edge partial aggregation and hierarchical dims with short raw retention.

### 6.4 Deal-breakers checklist

- OLTP UNIQUE per click at millions/s.  
- Dashboard scans of raw click logs.  
- No dedup under at-least-once.  
- Single global hot counter machine.  
- In-place mutation without versions when restating fraud.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & clarifying

**Q1: Click vs impression volume?**  
A: Impressions often 10–100× clicks; design schema for both but scale memory/cost differently (sampling impressions possible).

**Q2: What is billable click?**  
A: Survived dedup + invalid filters + maybe viewability rules—define explicitly with advertisers.

**Q3: Do you show real-time pacing?**  
A: Soft realtime from speed layer; budget controllers may need separate low-latency path.

**Q4: Attribution out of scope?**  
A: Keep join keys (`campaign_id`, `click_id`); attribution service consumes billable stream later.

**Q5: Privacy constraints?**  
A: Hash tokens; aggregate; short raw TTL; careful with IP retention.

### 7.2 Dedup & hashing

**Q6: Why hash click_id for partitions?**  
A: Uniformity; same id → same dedup state partition.

**Q7: Bloom false positive impact?**  
A: Dropping a real click undercounts—set ε tiny or use Bloom only as positive filter before exact check.

**Q8: Dedup without click_id?**  
A: Weak key `(user_hash, ad_id, seconds_bucket)` increases collision risk—product decision.

**Q9: Distributed Bloom?**  
A: Partitioned Blooms per Kafka partition align with keyed state—avoid one mega Bloom.

**Q10: Memory of exact TTL map?**  
A: Show math; argue RocksDB state or truncated hashes (64-bit with birthday math disclosed).

### 7.3 Stream processing

**Q11: Tumbling vs sliding for ads?**  
A: Tumbling 1m buckets standard for rollups; sliding rarely needed for dashboards.

**Q12: Event-time vs receive-time?**  
A: Billing often receive-time or serving-time; fraud may need client ts anomalies—state policy.

**Q13: Exactly-once sinks?**  
A: Idempotent upserts with deterministic keys often enough; transactional sinks reduce duplicates under failure.

**Q14: State backend choice?**  
A: RocksDB for large TTL dedup; memory only for tiny demos.

**Q15: Watermark stalls?**  
A: Idle partitions need heartbeat watermarks or processing-time fallback with care.

### 7.4 Storage & indexing

**Q16: Why Pinot/ClickHouse/Druid?**  
A: Columnar, inverted/sorted dims, rollup aggregation, fast timeseries—fit advertiser analytics.

**Q17: Primary index for rollups?**  
A: Sort/key by `advertiser_id, campaign_id, time` for tenant-localized scans.

**Q18: Star tree / skip aggregates?**  
A: Precompute common group-bys to accelerate high-cardinality queries.

**Q19: Raw in S3 + Athena?**  
A: Good for restate/data science; not interactive dashboard path.

**Q20: Cardinality explosion control?**  
A: Limit group-by dims; force rollup; sample debug logs.

### 7.5 Fraud & integrity

**Q21: Classic click fraud patterns?**  
A: Bots, incentivized farms, competitor click bombing, injected beacons—combine rules+ML.

**Q22: Can fraud filter be async?**  
A: Yes—early counts + negative corrections; billing settle waits.

**Q23: Click bombing one ad?**  
A: Rate caps per user/IP/ASN; anomaly z-scores on campaign.

**Q24: Why keep invalid events?**  
A: Training + dispute + restate; store cheaply cold.

### 7.6 Query & multi-tenancy

**Q25: Prevent cross-advertiser reads?**  
A: AuthN + AuthZ predicate forced in query planner (`advertiser_id = token.aid`).

**Q26: Noisy neighbor queries?**  
A: Per-tenant concurrency; cost-based rejection of huge scans.

**Q27: Cache keys?**  
A: `(tenant, metric, range, grain, group_by)` short TTL; invalidate on settle version bump.

**Q28: Pagination of breakdowns?**  
A: Top-K by clicks with approximate first pass.

### 7.7 Load balancing & fanout

**Q29: Edge collector LB?**  
A: GeoDNS / anycast to PoPs; buffer to regional Kafka.

**Q30: Query fanout across regions?**  
A: Merge timeseries by timestamp; watch partial region failures → degraded flag.

**Q31: Hot partition fix?**  
A: Salting; split campaign; increase partitions carefully (order not needed for counts).

### 7.8 Algorithms & math

**Q32: HLL for unique users?**  
A: Yes for reach metrics; not for billable clicks (need exact-ish counts).

**Q33: Count-Min for ads?**  
A: Rarely for billing; maybe abuse detection sketches.

**Q34: Birthday paradox on 64-bit ids?**  
A: At 1e10 ids, collision probability still tiny for random UUIDs; truncated hashes need math disclosure.

**Q35: Merge rollups correctness?**  
A: Sum clicks/cost merges; unique users need HLL merge not sum.

### 7.9 Estimation drills

**Q36: Dedup storage 1M/s × 24h × 16B?**  
A: 1e6×86400×16 ≈ 1.38e12 B ≈ **1.38 PB**—argue compacted state / Bloom / shorter TTL / 8B keys.

**Q37: 10M/s × 200B bandwidth?**  
A: 2 GB/s raw; with ×3 replication and burst headroom, multi-PB/day class—cells mandatory.

**Q38: Query merge 7d of 1m buckets one campaign?**  
A: 7×1440=10080 rows—fine; 7d of raw clicks at 1K/s = 604e6 rows—not fine.

### 7.10 Alternatives & deal-breakers

**Q39: Only batch every hour?**  
A: Fails freshness SLO for always-on advertisers; OK for some reports.

**Q40: Meta closer sentence?**  
A: “I’d separate ingest/dedup/agg from query, use stream state for TTL dedup, serve pre-aggregated rollups, and run a settle/reprocess path for fraud-updated billable counts—sharding regionally as click QPS jumps 10×→1000×.”

---

### 7.11 Extra depth

**Q41: Cost_micros summing race?**  
A: Additive aggregates are commutative; use sealed buckets post-watermark for settle.

**Q42: Exactly-once vs financial exact?**  
A: Financial exact is business reconcile + contracts, not Flink checkpoint magic alone.

**Q43: SDK batching vs loss?**  
A: Batch with size/time flush; on fail exponential retry with click_id.

**Q44: Clock jump at edge?**  
A: Monotonic receive processors; alert NTP.

**Q45: Multi-currency cost?**  
A: Store currency + normalized USD micros carefully; don’t sum mixed FX blindly.

**Q46: Campaign hierarchy (portfolio)?**  
A: Roll up along tree async; don’t explode stream keys for all ancestors inline without care.

**Q47: Debug “why was click invalid?”**  
A: Sample invalid reasons to side store; not every event full feature dump.

**Q48: GDPR delete user?**  
A: Raw delete/TTL; aggregates anonymized—legal design with counsel.

**Q49: Can Kafka compaction replace dedup?**  
A: Compaction by click_id possible for latest, not for counting once semantics by itself.

**Q50: What’s first cut if 45 minutes?**  
A: Event schema, dedup TTL strategy, rollup grains, OLAP query path, watermark freshness—say auction out of scope.

---

## Appendix A — End-to-end sequence (billable click)

```text
1. Serving systems assign click_id; client/SDK fires beacon
2. Edge collector validates schema, sets ts_receive, ACKs after WAL/Kafka
3. Stream enrich: geo, ASN, platform normalize
4. Dedup: if click_id seen in TTL → drop (metric dup)
5. Fraud rules: maybe mark invalid_reason
6. keyBy(campaign, country, platform, minute) incr billable|invalid, cost
7. Sink upsert into OLAP rollup segment (pipeline_version)
8. Emit billable click to billing topic if valid
9. Advertiser UI queries Metrics API → authZ → merge buckets → chart
```

## Appendix B — Dedup state sketch (Flink)

```text
KeyedState<click_id, Boolean> seen with TTL = 24h
processElement(e):
  if state.get(e.click_id) != null: metrics.dup++; return
  state.put(e.click_id, true)
  out.collect(e)
```

Front Bloom (optional): if definitely not present → skip exact lookup cost; if maybe → exact state.

## Appendix C — Rollup compaction

```text
Every hour:
  read sealed 1m buckets for hour H
  sum into 1h row
  mark 1m sealed immutable
Every day:
  sum 24×1h into 1d
Query planner:
  range picks largest grain that fits freshness needs
```

## Appendix D — Watermark policy card

```text
event_time = coalesce(ts_serving, ts_receive)
watermark = max_event_time - allowed_lateness
allowed_lateness MVP = 2m (dashboards) ; settle = 24h
out-of-orderness histogram monitored
idle sources emit keep-alive for watermark progress
```

## Appendix E — Query planner examples

```text
Q: last 60m by campaign, grain auto
  → use 1m buckets; ~60 rows merge

Q: last 90d totals
  → 1d grain; reject group_by ultra-high-card dim without limit

Q: breakdown by country for 7d
  → 1h or 1d; top countries approximate first OK
```

## Appendix F — Hot key salting

```text
if rate(campaign_id) > threshold:
  subkey = hash(click_id) % N
  agg_key = (campaign_id, subkey, dims...)
every Ts: combine subkeys → campaign totals for sink
```

## Appendix G — Restate / settle workflow

```text
1. Freeze early serving pointer optional
2. Launch batch job over raw S3/Kafka freeze range with fraud_rules_vNext
3. Write aggregates to pipeline_version = vNext
4. Validate vs shadow diff within ε
5. Atomic swap serving pointer to vNext
6. Emit correction deltas to billing if contract requires
```

## Appendix H — Tenant authZ enforcement

```text
token → advertiser_ids allowset
planner injects predicate advertiser_id IN allowset
no client-supplied advertiser override without check
admin cross-tenant roles audited
```

## Appendix I — Capacity worksheet

```text
peak_clicks_per_s = ______
bytes_per_event = ______
kafka_bandwidth ≈ peak × bytes × replication
dedup_ids_per_ttl = peak × ttl_s
dedup_GB ≈ ids × 8..16B × overhead
olap_1m_keys_per_min ≈ distinct dim tuples / min
dashboard_qps = ______
```

## Appendix J — Progressive scale checklist

| Scale | Must say |
|-------|----------|
| Baseline | Kafka + stream dedup/agg + OLAP rollups |
| 10× | Rocks TTL dedup; sealed buckets; query cache |
| 100× | Regional cells; salting; settle batch |
| 1,000× | Edge partial agg; hierarchical dims; short raw TTL |

## Appendix K — Deal-breaker checklist

1. OLTP UNIQUE(click_id) at millions/s  
2. Dashboard scans of raw clicks  
3. At-least-once with zero dedup  
4. Single global counter host  
5. In-place restate without versions  
6. Cross-tenant queries without forced predicate  
7. Summing HLLs for unique users  

## Appendix L — Fraud rule examples (MVP)

```text
deny if asn in datacenter_list
deny if clicks_per_user_ad_minute > K
deny if ua empty AND ip_reputation bad
deny if geo teleport > X km in T seconds (same user_token)
soft_invalid if ml_score > θ (nearline)
```

## Appendix M — Metrics that page someone

| Metric | Page if |
|--------|---------|
| kafka_lag | > freshness SLO budget |
| dedup_state_lag | checkpoint stuck |
| invalid_ratio | sudden cliff / spike unexplained |
| olap_upsert_errors | > ε |
| query_p99 | > SLA |
| watermark_delay | stalled |

## Appendix N — Early vs settled counts (product copy)

```text
UI badge: "Partial — data through 14:03 UTC"
After settle: "Finalized for billing"
Discrepancy FAQ prepared for advertisers
```

## Appendix O — Meta interview closing

> “I’d ingest clicks through regional edge into Kafka, dedup with TTL stream state, filter invalid traffic, aggregate into time-bucketed rollups for advertiser queries, and run a versioned settle/reprocess path for fraud updates—never putting every click in a forever-hot OLTP unique table.”

## Appendix P — 30-minute interview checklist

1. Clarify events, dedup TTL, grains, freshness, fraud, billing join.  
2. BOTE: events/s, dedup memory, rollup cardinality, query QPS.  
3. Draw edge → Kafka → dedup/fraud/agg → OLAP → API.  
4. Deep dive dedup + watermarks + hot keys.  
5. Scale 10×/100×/1,000×.  
6. Deal-breakers.

## Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Dedup TTL | Window where click_id counted once |
| Rollup | Pre-aggregated time bucket row |
| Watermark | Event-time progress marker |
| Settle | Later authoritative recompute |
| Billable | Counts eligible for money |
| Invalid IVT | Invalid traffic excluded |
| Salting | Split hot keys into subkeys |

## Appendix R — Schema evolution

```text
Add optional fields with defaults; never reuse field numbers/names
pipeline_version bumps when aggregation semantics change
dual-write period comparing v_n vs v_n+1
```

## Appendix S — Privacy notes

```text
Prefer hashed user tokens over raw IDs in aggregates
Minimize IP retention; ASN may suffice for fraud
Respect retention deletes on raw; aggregates anonymized
Document join keys shared with billing
```

## Appendix T — Comparison: stream-only vs lambda

| | Stream-only | Stream + settle |
|--|-------------|-----------------|
| Freshness | Best | Best + final |
| Fraud restate | Hard | Natural |
| Ops | One pipeline | Two |
| Meta ads style | Rare alone | **Common** |

---

## Appendix U — Anti-patterns (deepened)

| Anti-pattern | Why | Instead |
|--------------|-----|---------|
| Bill from early only | Numbers move / disputes | Settled + version |
| Interactive raw scans | Cost/latency | Rollups |
| One global dedup keyspace | Hotspot/OOM | Shard click_id |
| Drop invalid forever | No forensics | Soft flag + archive |
| Sync heavy ML ingest | Lag | Nearline |
| Cross-tenant cache keys | Leak | Tenant in key |
| Ignore watermark stall | Silent wrong | Freshness SLI |
| Unbounded dims | Cardinality bomb | Allowlist |

## Appendix V — 90s pitch

> “Ad click aggregator: durable ingest, click_id dedup for billable exactly-once, stream rollups for early, fraud+watermark for settled, OLAP cubes for queries. Scale with salting, state sharding, regional cells—never raw SQL at 1M clicks/s.”




## Appendix W — Numeric drills & deal-breakers card

```text
100K click/s × 200B = 20MB/s ≈ 1.7TB/day raw
Dedup 24h × 16B ≈ 138GB @ 100K/s; 10× → 1.4TB state
Query: merge 1440 minute buckets not scan 360M events/hour/campaign
DEAL-BREAKERS: bill early-only; raw interactive; unsalt hot campaign; cross-tenant cache
```

### Extra maintainability: multi-region ops

| Concern | Approach |
|---------|----------|
| Ingest | Regional collect → regional Kafka |
| Dedup | Keyed by click_id home hash |
| Query | Fanout merge with tenant authZ |
| Restate | Per-region then global settle job |


*End of Meta system design: Ad Click Aggregator.*
