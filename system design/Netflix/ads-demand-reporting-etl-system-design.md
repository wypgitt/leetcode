# System Design: Ads Demand Reporting ETL

> **Focus areas:** Billable facts · Warehouse staging · Late data · Idempotent aggregates · Advertiser API · Config lineage · SLA tiers
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS, explicit deal-breakers, Netflix 2025–26 interview themes
> **Interview theme:** Netflix Ads — ETL pipeline from raw delivery events to advertiser-ready demand reports with correct money and lineage

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

Goal: **bound **ads demand reporting ETL**—transform raw impression/click/quartile events into reconciled, advertiser-facing facts in the warehouse with idempotent rollups and config version lineage.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Batch + near-line ETL to warehouse | Real-time ad decision |
| Input | Kafka facts, settlement files | Trafficking CRUD |
| Output | Advertiser dashboards, invoices adjacency | Live cap counters |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Sources? | Impression, click, completion, viewability | Unified fact schema |
| F2 | Grains? | Hourly/daily by campaign/line/creative/geo | Rollup tables |
| F3 | Late data? | 7–30d acceptance window | Watermark + backfill jobs |
| F4 | Idempotency? | Replay safe | Merge keys on sinks |
| F5 | Money? | Integer micros; CPM calc | No float revenue |
| F6 | Lineage? | config_version on facts | Join to config dim |
| F7 | SLA? | Near-line 15m; daily T+1 finance | Tiered pipelines |
| F8 | Fraud? | Exclude flagged events | fraud_flag dimension |
| F9 | Recon? | Compare to pacing spend counters | Alert drift > threshold |
| F10 | Multi-tenant? | advertiser_id partition | RLS in warehouse |
| F11 | Deletes/GDPR? | Propagate tombstones | Aggregate adjustments |
| F12 | API? | Advertiser read aggregates | Read replica / OLAP |

**MVP functional scope (lock with interviewer):**

1. Ingest standardized BillableEvent schema from Kafka.
2. Hourly idempotent rollups to staging.
3. Daily finance-grade marts with T+1 SLA.
4. Late event backfill with merge into buckets.
5. Config version dimension table.
6. Recon job vs pacing spend.
7. Advertiser API with pagination.
8. GDPR delete propagation.

**Out of MVP (explicitly defer):**

- Sub-second advertiser UI at 1000×
- Real-time billing settlement as SoT
- ML anomaly as only QA

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
| --- | --- | --- | --- |
| N1 | Hot path latency? | See plane | p99 per budget table |
| N2 | Durability? | No lost facts | Quorum + outbox |
| N3 | Availability? | Critical tier | 99.9–99.99% |
| N4 | Idempotency? | Retries safe | Keys on all writes |
| N5 | Scale | Through 1000× | Progressive table |
| N6 | Consistency? | Plane-appropriate | Strong OLTP; eventual agg |
| N7 | Audit? | Compliance | Append-only 7y |
| N8 | Privacy? | Min PII | Hash identifiers |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Ingest standardized BillableEvent schema from Kafka.
2. Hourly idempotent rollups to staging.
3. Daily finance-grade marts with T+1 SLA.
4. Late event backfill with merge into buckets.
5. Config version dimension table.
6. Recon job vs pacing spend.

**Edge / failure cases**

| Case | Behavior |
| --- | --- |
| Duplicate client retry | Idempotent 200/409 |
| Downstream lag | Backpressure + DLQ |
| Regional outage | Failover bounded staleness |
| Hot key / shard | Isolate + partition key discipline |
| Bad deploy | Canary + rollback pointer |
| Late/arriving events | Watermark + reconcile |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
| --- | --- | --- | --- | --- |
| Peak write QPS | 100 | 1K | 10K | 100K |
| Peak read QPS | 1K | 10K | 100K | 1M |
| Distinct entities | 1M | 10M | 100M | 1B |
| Async events / s | 500 | 5K | 50K | 500K |
| Storage hot tier | 100 GB | 1 TB | 10 TB | 100 TB |

**Split classes:** raw ingest ≠ stream aggregate ≠ batch mart ≠ API read

**What each jump forces:**

- **10×:** Flink hourly; partition by campaign_id.
- **100×:** Separate finance mart; incremental dbt.
- **1,000×:** Regional marts merge; cold archive facts.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-scale progressive design (10× → 100× → 1,000×).
- Sibling docs in INDEX.md for related systems.
- State invariants before drawing boxes.

**Scope statement:**

> Design **ads demand reporting ETL** from event streams to warehouse marts with idempotent rollups, late data handling, and recon against pacing — scaling through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event volume derivation

```text
Ads-tier DAU (baseline)           = 5M
Sessions / DAU                    ≈ 3
Ads / session (mid-roll pods)     ≈ 3
Daily impressions                 = 5M × 3 × 3 = 45M / day
Average rate                      = 45M / 86,400 ≈ 520 / s
Peak factor (prime-time skew)     ≈ 10×
Peak billable events              ≈ 5,200 / s  →  round to 5K / s baseline
```

Each event carries: `event_id`, `impression_id`, `decision_id`, hierarchy ids, `geo`, `config_version`, `ts`, `viewability`, `fraud_flag` → **~500 B** serialized Avro/Protobuf.

```text
Kafka ingress (baseline)  = 5,000 / s × 500 B = 2.5 MB / s
At 100×                   = 250 MB / s  (~2 Gbps broker class)
At 1,000×                 = 2.5 GB / s  (regional Kafka + tiered compaction)
```

**Deal-breaker:** treating ingest QPS as advertiser API read QPS — they differ by ~3 orders of magnitude.

### 2.2 Rollup cardinality (hourly grain)

Dimensions: `(hour, campaign_id, line_id, creative_id, geo, config_version)`.

```text
Active campaigns (baseline)       ≈ 50,000
Lines / campaign (avg)            ≈ 3
Creatives / line (avg)            ≈ 5
Geo buckets (country/region)      ≈ 50
Naive cross product / hour        = 50K × 3 × 5 × 50 = 37.5M combos

Observed sparsity (only combos with ≥1 event) ≈ 0.1–0.3%
Effective hourly keys (baseline)  ≈ 37.5M × 0.002 ≈ 75K / hour
Flink state (72h watermark window) ≈ 75K × 72 ≈ 5.4M active keys
Value per key (counts + spend_micros + flags) ≈ 200 B
Flink keyed state (baseline)      ≈ 5.4M × 200 B ≈ 1.1 GB (+ replication)
```

At **100×** events but similar campaign count → keys grow with geo/creative fan-out, not linearly with impressions; expect **~500K–2M** active hourly keys.

### 2.3 Daily mart row count

```text
Grain: day × advertiser × campaign × line × creative × geo
Advertisers (baseline)            ≈ 2,000
Rows / advertiser / day (sparse)    ≈ 5,000
Daily mart rows                   ≈ 2K × 5K = 10M / day
Row width (measures + dims)       ≈ 300 B
Daily partition size              ≈ 10M × 300 B ≈ 3 GB / day
365-day hot retention             ≈ 1.1 TB (before compression)
```

Warehouse columnar compression (Parquet ~5×) → **~220 GB / year** hot tier for daily marts alone.

### 2.4 Revenue / spend math (integer micros)

```text
Avg CPM (baseline assumption)     = $25.00
CPM in micros                       = 25_000_000  (1 USD = 1e6 micros)
Spend per impression (CPM model)  = cpm_micros / 1000 = 25_000 micros

Daily gross (baseline)            = 45M impressions × 25,000 micros
                                  = 1.125e12 micros = $1.125M / day

Penny drift check at 45M rows:
  Float: 45M × 0.025 = 1,125,000.0000001 possible
  Integer: exact — finance requires micros + BIGINT SUM in warehouse
```

Recon tolerance: pacing ledger vs warehouse **±0.01%** of daily spend (~$112/day at baseline) before page.

### 2.5 Storage tiers (baseline)

| Tier | Size |
|------|------|
| Kafka raw (90d) | ~2 TB |
| Flink state (72h) | ~1 GB |
| Daily marts (1y) | ~1 TB |
| Dedup KV (30d) | ~830 GB |

### 2.6 QPS classes (split — do not blend)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Kafka consume (ingest) | 5K/s | 500K/s | 5M/s | partition by `campaign_id` |
| Flink keyed upsert | 5K/s | 500K/s | 5M/s | stateful; not same as API |
| Hourly merge to WH | 75K keys/h → ~21/s | 500/s | 5K/s | micro-batch commits |
| Daily dbt job | 10M rows/batch | 1B rows | 10B rows | off-peak; not online |
| Advertiser API read | 1K/s origin | 10K/s | 100K/s | CDN/cache 10× front |
| Recon batch | 1 run/night | hourly sample | continuous | async only |
| GDPR purge jobs | ~100 profiles/day | 10K/day | 100K/day | rare but heavy |

### 2.7 Latency budget

| Stage | Budget | Consumer |
|-------|--------|----------|
| Event → staging visibility | < 15 min p95 | Ops trafficking dashboard |
| Hourly rollup freshness | < 60 min p95 | Internal pacing adjacency |
| Advertiser API (cached) | < 200 ms p99 | External UI |
| Finance daily mart | T+1 by 06:00 UTC | ERP / invoicing |
| Late backfill merge | < 4 h after arrival | Corrected reports |

**Never** put warehouse query on ad-decision path — decision SoT is live counters, not marts.

### 2.8 Critical bottlenecks

1. Hot mega-campaign partition in Flink.  
2. Double-count on replay without dedup.  
3. Float CPM math.  
4. Sync WH on API path.  
5. Closing buckets before late window ends.

### 2.9 Cost intuition & deal-breaker

```text
Track $/1M events, reconcile_diff_usd, dup_rate_ppm
Deal-breaker: one blended QPS for ingest + API + batch
```

---

## 3. High-Level Design

### 3.1 Planes

```text
Control Plane: config, validation, publish, audit
Data Plane: hot read/write serving path
Async Plane: logs, aggregation, recon, batch
```

### 3.2 Core entities

| Entity | Role |
|--------|------|
| BillableEvent | Raw fact |
| HourlyRollup | Near-line aggregate |
| DailyMart | Finance/advertiser |
| ConfigDim | Version lineage |
| ReconDiff | Drift tracking |

### 3.3 APIs (logical)

```text
POST /internal/events (from bus)
GET /advertisers/{id}/reports?from&to&grain
Jobs: backfill, recon, gdpr_purge
```

### 3.4 Store choices

| Component | Choice | Rationale |
|-----------|--------|----------|
| Stream buffer | Kafka | Immutable fact log |
| Stream compute | Flink | Stateful dedupe + rollup |
| Config | PostgreSQL | Campaign SCD |
| API cache | Redis | Advertiser aggregates |
| Warehouse | BigQuery/Snowflake | Marts + MERGE |
| Dedup KV | RocksDB / Redis | event_id TTL 30d |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
Kafka→Flink→Staging→dbt→Mart→Advertiser API
         ↘ Recon → Pacing counters
```

### 4.2 Sequence: event ingest → staging

```text
ImpressionSvc→Kafka: BillableEvent(event_id, ...)
Flink→DedupStore: seen(event_id)?
  no → rollup hourly bucket → micro-batch MERGE staging_hourly
  yes → drop
Watermark closes hour → MERGE fact_impression_hourly
```

### 4.3 Sequence: late event backfill

```text
Late event arrives (ts in closed hour)
Flink→reopen bucket → emit delta to staging
dbt/MERGE→fact_impression_hourly (is_late=true)
Advertiser API→returns data_freshness_ts + optional correction banner
```

### 4.4 Sequence: advertiser report read

```text
Client→API: GET /reports?advertiser_id&from&to
API→Redis: cache key (advertiser, day range)
  hit → return
  miss → WH query mart_advertiser_daily (RLS) → populate cache → return
Never synchronous WH on impression ingest path
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **event_id dedup** — replays must not double-count revenue.  
2. **Integer micros** — no float on money path.  
3. **config_version** on every fact — lineage for incidents.  
4. **Hot path ≠ warehouse** — ad decision never waits on ETL.  
5. **Recon gate** before finance close.  
6. **Split QPS classes** in capacity plans.  
7. **Late data MERGE** — buckets reopen idempotently.  
8. **RLS** — advertisers see only their rows.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Kafka duplicate | Dedup drop |
| Flink lag | Ops banner; finance uses T+1 batch |
| WH unavailable | API serves cached mart + stale banner |
| Bad deploy | Canary rollback; replay idempotently |
### 5.4 Exact algorithm: idempotent hourly rollup

```text
function processEvent(event, state, dedupStore):
  if event.fraud_flag == FRAUD: return  // excluded from billable rollup
  if dedupStore.seen(event.event_id): return DUPLICATE

  bucket_key = (
    floor_hour(event.ts),
    event.campaign_id, event.line_id, event.creative_id,
    event.geo, event.config_version
  )
  agg = state.get(bucket_key) or emptyAgg()

  agg.impressions += 1
  if event.viewable: agg.viewable_impressions += 1
  agg.spend_micros += cpmSpend(event)   // integer only
  agg.last_event_ts = max(agg.last_event_ts, event.ts)
  agg.distinct_impressions.add(event.impression_id)  // or HLL at 100×

  state.put(bucket_key, agg)
  dedupStore.mark(event.event_id, ttl=30d)
  emitToStaging(bucket_key, agg)  // micro-batch commit
```

```text
function cpmSpend(event):
  // Lookup rate from config dim at event.config_version — never float
  rate = configDim.cpmMicros(event.line_id, event.config_version)
  return rate / 1000   // per-impression micros; BIGINT math
```

### 5.5 Watermark + late-data merge

```text
WATERMARK_DELAY = 72 hours   // accept late events into closed buckets

function onWatermark(hour_ts):
  for bucket in buckets where bucket.hour_ts < now - WATERMARK_DELAY:
    close(bucket)            // mark immutable for near-line tier
    writeToWarehouse(bucket)

function onLateEvent(event):
  bucket = bucketKey(event)
  if bucket.isClosed:
    bucket.reopen()          // idempotent MERGE in warehouse
    flag is_late = true
  reprocess(event)           // same rollup logic; MERGE adds deltas
```

Closing buckets too early loses late events permanently unless backfill scans raw Kafka — expensive at 100×.

### 5.6 Warehouse MERGE (dedupe effect)

```sql
MERGE INTO fact_impression_hourly t
USING staging_hourly s
ON t.hour_ts = s.hour_ts AND t.campaign_id = s.campaign_id
   AND t.line_id = s.line_id AND t.creative_id = s.creative_id
   AND t.geo = s.geo AND t.config_version = s.config_version
WHEN MATCHED THEN UPDATE SET
  impressions = t.impressions + s.impressions_delta,
  viewable_impressions = t.viewable_impressions + s.viewable_delta,
  spend_micros = t.spend_micros + s.spend_micros_delta,
  is_late = GREATEST(t.is_late, s.is_late)
WHEN NOT MATCHED THEN INSERT (...);
```

Replay safety: staging carries **deltas** keyed by `(event_id batch)` or recomputes bucket from raw with same dedup table.

### 5.7 Nightly recon vs pacing ledger

```text
function recon(day):
  wh = SUM(spend_micros) FROM mart_advertiser_daily WHERE dt = day
  pacing = SUM(spend_micros) FROM pacing_ledger WHERE dt = day
  diff_pct = abs(wh - pacing) / max(pacing, 1) * 100

  for campaign in top_campaigns_by_spend:
    campaign_diff = wh[c] - pacing[c]
    if abs(campaign_diff) > CAMPAIGN_EPSILON: emit recon_pacing_diff row

  if diff_pct > 0.01%: page_oncall()
```

Root causes to classify: clock skew buckets, fraud exclusion mismatch, config_version join miss, duplicate impression_id in one pipeline only.

### 5.8 GDPR tombstone propagation

```text
function onProfileDelete(profile_id):
  emit TombstoneEvent(profile_id, ts=now)
  // Stream consumer:
  for fact in facts WHERE subject_hash = H(profile_id):
    emit AggregateAdjustment(-impressions, -spend_micros) to affected buckets
  // Batch repair: scan 30d partitions, subtract, mark gdpr_purged
```

Never delete raw audit log without legal hold check — often **anonymize** subject fields instead.

### 5.9 Scale-specific architecture (not generic stubs)

**1× baseline (~5K events/s)**  
Single-region Kafka (32 partitions). Flink job with RocksDB state; hourly micro-batch to BigQuery staging. dbt daily mart T+1. Dedup in Flink + `event_id` PK in staging. Recon nightly sample 100% spend.

**10× (~50K events/s)**  
Dedicated hot-campaign isolation: `hash(campaign_id) % N` routes mega-campaigns to over-provisioned subtasks. Separate **gross** vs **billable** rollups (fraud tagged at ingest). Advertiser API fronted by Redis cache of pre-aggregated `(advertiser, day)` totals. Idempotency store sharded by `event_id` hash.

**100× (~500K events/s)**  
Regional ingest cells write to cell-local staging; **consolidation job** merges with idempotent keys (no double SUM). Finance mart in separate WH project with signed checksums. HLL for `unique_reach` in ops tier only — finance uses exact dedupe tables. Continuous recon sample every hour on top 1% spend campaigns.

**1,000× (~5M events/s)**  
Lakehouse raw zone (Iceberg/Delta) as immutable SoT; stream for near-line only. Cold archive facts to object storage; marts query last 13 months hot. Schema evolution via registry; backfill as Spark jobs with partition pruning. Multi-currency FX join in batch only with explicit `fx_version`.

### 5.10 Multi-region

| Data | Strategy |
|------|----------|
| Raw Kafka | Regional ingest; mirror to global lake for DR |
| Flink state | Cell-local; no cross-cell state sharing |
| Staging / marts | Global WH with `region` partition; consolidate idempotently |
| Config dim | Global SoT; versioned snapshots to all cells |
| DR | RPO 15 min (Kafka mirror); RTO 4 h for mart rebuild from raw |

Cross-region duplicate ingest (failover replay) must dedupe on `event_id` globally — not `(region, event_id)`.

### 5.11 Warehouse schema & grain design

| Table | Grain | Keys | Refresh |
|-------|-------|------|---------|
| `fact_impression_hourly` | hour × campaign × line × creative × geo | `(hour_ts, campaign_id, line_id, creative_id, geo, config_version)` | Stream MERGE |
| `fact_click_hourly` | same + click measures | + `impression_id` join key | Sibling pipeline |
| `dim_campaign` | SCD2 | `(campaign_id, valid_from)` | Daily snapshot |
| `dim_config_version` | version snapshot | `config_version` | On publish |
| `recon_pacing_diff` | day × campaign | spend WH vs pacing ledger | Nightly |

**Late data policy:** accept events up to 30 days; `is_late` flag; backfill reopens closed hour buckets idempotently.

### 5.12 Finance vs advertiser SLA tiers

| Tier | Freshness | Correctness | Consumer |
|------|-----------|-------------|----------|
| Near-line ops | 15 min p95 | Approx uniques OK (HLL) | Trafficking dashboards |
| Advertiser API | 1–4 h | Idempotent merges | External reporting |
| Finance close | T+1 | Integer micros; recon signed-off | ERP / invoicing |

Never use near-line tier for invoicing without reconciliation gate.

### 5.13 ETL sequence (batch + stream)

```text
Kafka BillableEvent → Flink (dedupe event_id) → staging_hourly
Flink watermark close → MERGE fact_impression_hourly
dbt: staging → mart_advertiser_daily (partition dt, advertiser_id)
Nightly recon: SUM(spend_micros) WH vs pacing_ledger ± ε
GDPR: tombstone stream → aggregate adjustment job → mart correction
```

### 5.14 Deal-breaker gallery (demand ETL)

| Temptation | Failure |
|------------|---------|
| Double-count on Kafka replay | Inflated advertiser bills |
| Float CPM math | Penny drift at billions of rows |
| No config_version on facts | Cannot explain delivery incident |
| Blocking ad decision on warehouse | Wrong latency class |
| One DB for ingest + API + finance | Latency + blast radius |

### 5.15 Testing strategy

1. Unit: `cpmSpend`, watermark close, MERGE delta math  
2. Integration: Flink dedup + staging PK collision  
3. Replay: re-consume 7d Kafka → identical mart checksum  
4. Chaos: broker lag, WH unavailable (API serves stale cache banner)  
5. Recon: inject 0.02% drift → page fires  
6. Load: 10× burst on single mega-campaign partition only

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
| --- | --- |
| Ingest | Kafka + schema registry |
| Rollups | Flink idempotent upsert |
| Finance | Daily batch dbt |
| Recon | Nightly diff vs pacing |

### 6.2 Risks

1. Hot key tenant
2. Idempotency TTL too short
3. Canary false positive rollback
4. Cross-region staleness beyond SLA
5. Recon lag undetected

### 6.3 45-minute plan

| Min | Focus |
| --- | --- |
| 0–5 | Clarify planes + split QPS |
| 5–15 | Entities + APIs + stores |
| 15–25 | Hot path + idempotency |
| 25–35 | Async + recon |
| 35–45 | Scale table + deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Pipeline architecture

**Q: Batch vs stream for ads reporting?**  
A: **Stream** (Flink) for near-line ops (~15 min). **Batch** (dbt) for finance T+1 with signed recon. MVP can be batch-only; Netflix-scale needs both with explicit SLA separation.

**Q: Why not query raw Kafka for advertiser API?**  
A: Scan cost, no SCD joins, no RLS — marts exist for bounded tenant queries.

### 7.2 Late data & watermarks

**Q: How handle events arriving 3 days late?**  
A: Keep hourly buckets **open** for `WATERMARK_DELAY` (e.g. 72h). Late event triggers MERGE delta into closed bucket; set `is_late=true`. Beyond 30d → quarantine DLQ for manual review.

**Q: Event-time vs processing-time?**  
A: **Event-time** for bucketing (advertiser expects delivery by air date). Processing-time only for ops lag metrics.

**Q: Can we ever "finalize" a day before late window ends?**  
A: Finance can **freeze** a preliminary number with banner "subject to adjustment"; true close only after watermark + recon pass.

### 7.3 Money & billing correctness

**Q: Float or decimal for CPM?**  
A: **Integer micros** end-to-end. `spend_micros = impressions × cpm_micros / 1000` with BIGINT. Float loses pennies at 45M+ rows/day.

**Q: Gross vs billable impressions?**  
A: Maintain parallel rollups. Fraud-tagged events count in gross ops dashboards; finance/invoicing uses billable only. Recon checks both paths.

**Q: Multi-currency?**  
A: Store `currency` + `spend_micros` in local currency at ingest; FX conversion in **batch only** with explicit `fx_version` and date — never on stream hot path.

### 7.4 Idempotency & replay

**Q: Kafka at-least-once — how avoid double count?**  
A: `event_id` dedup in Flink state + PK in staging + MERGE semantics (deltas, not blind INSERT).

**Q: Replay 7 days of Kafka after bug fix?**  
A: Idempotent MERGE from recomputed staging; compare mart checksum before/after; do not DELETE rows unless full rebuild approved.

**Q: Exactly-once in Flink?**  
A: End-to-end exactly-once to WH is hard; **effectively-once** via dedup keys is the practical interview answer.

### 7.5 Config lineage

**Q: Why config_version on every fact?**  
A: When trafficking changes CPM mid-hour, you can explain spend split across versions and debug "why did spend jump?" without guessing.

**Q: SCD Type 2 for campaigns?**  
A: Yes for dims; facts carry version at event time. Join `dim_campaign` on `(campaign_id, event_ts BETWEEN valid_from AND valid_to)`.

### 7.6 Reconciliation

**Q: Pacing ledger vs warehouse — which is SoT?**  
A: **Neither alone.** Pacing is real-time spend control; warehouse is audit/billing. Nightly recon detects drift; finance signs off warehouse after recon gate.

**Q: What tolerance before page?**  
A: Example: **0.01%** of daily spend global; **$50** absolute per campaign — tune with finance.

### 7.7 Privacy & GDPR

**Q: Delete user — rewrite history?**  
A: Tombstone stream → subtract aggregates from affected buckets; anonymize raw facts per policy.

**Q: Can advertisers query profile-level data?**  
A: No — aggregates only; RLS on `advertiser_id`.

### 7.8 API & serving

**Q: Sub-second advertiser dashboard?**  
A: Pre-aggregate in mart + Redis cache; paginate drill-down.

**Q: Stale data banner?**  
A: Return `data_freshness_ts` when `etl_lag > SLA`.

### 7.9 Click / viewability joins

**Q: Orphan clicks?**  
A: Quarantine table — may indicate tracking bug.

**Q: Viewability billing?**  
A: Store gross + viewable; billing uses viewable if contract requires.

### 7.10 Interview traps

**Q: "One QPS number"?**  
A: Split ingest / stream / API / batch.

**Q: "WH query in ad decision"?**  
A: Wrong plane.

### 7.11 Metrics that page

**Q: Top alerts?**  
A: `reconcile_diff_usd`, `etl_lag_minutes`, `dup_rate_ppm`, Flink checkpoint failures.

---

## 8. Appendices

### A1. BillableEvent schema

```text
BillableEvent {
  event_id: UUID,              // dedup PK
  impression_id: UUID,
  decision_id: UUID,
  advertiser_id, campaign_id, line_id, creative_id,
  geo: ISO-3166-2,
  config_version: int64,
  ts_event: timestamp,
  ts_ingest: timestamp,
  viewability: { viewable: bool, duration_ms: int },
  fraud_flag: CLEAN | SUSPECT | FRAUD,
  cpm_micros: int64,
  currency: ISO-4217,
  subject_hash: bytes          // GDPR purge key — not in advertiser marts
}
```

### A2. Launch checklist

- [ ] `event_id` dedup verified under Kafka replay  
- [ ] Integer micros end-to-end — no float in Flink/dbt  
- [ ] Watermark delay ≥ business late-data SLA  
- [ ] Recon job scheduled + paging thresholds signed by finance  
- [ ] Split QPS dashboard (ingest / API / batch)  
- [ ] RLS on marts by `advertiser_id`  
- [ ] Canary Flink job with rollback pointer tested  
- [ ] GDPR tombstone subtract job dry-run complete  

### A3. Glossary

| Term | Meaning |
|------|--------|
| SoT | Source of truth — raw Kafka + immutable lake |
| MERGE | Idempotent upsert in warehouse |
| Watermark | Time horizon before bucket close |
| Billable | Excludes fraud-flagged events |
| config_version | Trafficking snapshot id at event time |
| micros | Millionths of currency unit (integer money) |

### A4. Interviewer traps

| Trap | Pushback |
|------|----------|
| Monolith DB | Split planes |

### A5. Reliability test plan

1. Idempotent retry returns same result
2. Canary/rollback under load
3. Regional failover with bounded staleness
4. Replay job produces identical aggregates
5. Chaos on hottest dependency
6. Scale test on split QPS class

### A6. 60-second summary

> Ads demand reporting is a **watermarked, idempotent ETL** from Kafka facts to **hourly staging + daily finance marts**. Split **ingest QPS from API QPS**; use **integer micros**; **dedupe on event_id**; **MERGE late data**; **recon nightly vs pacing** before finance close. Never block ad decision on warehouse.

### A7. Related systems map

```text
Impression Service → Kafka (BillableEvent)
Kafka → Flink (dedupe, rollup) → WH staging
dbt → mart_advertiser_daily → Advertiser API
Pacing Ledger ← nightly recon → WH marts
Ads Config → dim_config_version (SCD)
Frequency Cap counters → sibling (live SoT, not WH)
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Near-line freshness p95 | < 15 min |
| Advertiser API p99 | < 200 ms (cached) |
| Finance mart availability | T+1 by 06:00 UTC |
| Recon diff (global) | < 0.01% daily spend |
| dup_rate_ppm post-replay | < 1 |

### A9. Worked numeric example

```text
Campaign C, CPM = $30.00 → cpm_micros = 30_000_000
Hour 2026-08-06T20:00Z: 3 viewable impressions (e1–e3), 1 fraud (excluded)

Billable: impressions=3, spend_micros = 3 × 30_000 = 90_000 ($0.09)
Late e4 at T+36h: MERGE → spend_micros = 120_000 ($0.12), is_late=true
Recon: pacing 1_125_000_000 vs mart 1_124_880_000 → diff $0.12, no page
```

### A10. DDL sketch

```sql
CREATE TABLE fact_impression_hourly (
  hour_ts TIMESTAMP, campaign_id STRING, line_id STRING,
  creative_id STRING, geo STRING, config_version INT64,
  impressions INT64, viewable_impressions INT64,
  spend_micros INT64, is_late BOOL, updated_at TIMESTAMP,
  PRIMARY KEY (hour_ts, campaign_id, line_id, creative_id, geo, config_version)
);
CREATE TABLE staging_event_dedup (
  event_id STRING PRIMARY KEY, ingested_at TIMESTAMP
) WITH (expiration = INTERVAL '30' DAY);
```

### A11. Ownership

| Concern | Owner |
|---------|-------|
| Flink ingest + dedup | Ads Data Platform |
| dbt marts + finance close | Ads Analytics + Finance |
| Advertiser API | Ads Reporting |
| Recon + paging | Finance + SRE |

### A12. Naive design comparison

| Naive | Why it fails |
|-------|--------------|
| Nightly batch only | 15 min ops SLA impossible |
| No event_id dedup | Replay double-bills |
| Float revenue | Penny drift at scale |
| WH on ad decision | p99 meltdown |

### A16. Cost worksheet

```text
kafka_gb_month     = events/day × 500B × retention_days / 1e9
flink_vcpu_month   = partitions × avg_cpu × hours × $/vcpu-h
wh_storage_tb      = mart_rows/day × row_bytes × retention / 1e12 × compression
wh_scan_cost       = advertiser_queries × bytes_scanned/query × $/TB

Example baseline:
  kafka 90d ≈ 2 TB → ~$400/mo (tiered)
  flink 32 slots ≈ $8K/mo
  WH 1 TB hot ≈ $23/TB/mo
  Track reconcile_diff_usd — money bugs >> infra cost
```

### A17. Explicit non-goals

- Real-time billing as sole SoT (pacing sibling)  
- Sub-second advertiser UI at 1,000× without pre-aggregation  
- Blocking ad decision on warehouse freshness  

### A18. Interview rubric

- [ ] Split QPS classes with numbers  
- [ ] Integer micros + penny drift example  
- [ ] Watermark + late MERGE  
- [ ] Recon vs pacing with tolerance  
- [ ] Plane separation (decision ≠ ETL)  
- [ ] GDPR aggregate adjustment  

### A19. On-call cheat sheet

1. Check `etl_lag_minutes` vs deploy time.  
2. Check `reconcile_diff_usd` — page if over threshold.  
3. Verify Flink checkpoint success rate.  
4. Compare mart row count vs prior day (3σ).  
5. If dup_rate spike → pause consumer, fix dedup, replay idempotently.  
6. Roll back dbt/Flink version pointer before full reprocess.

### A20. Sample recon diff record

```text
{
  "dt": "2026-08-06",
  "campaign_id": "camp_8841",
  "wh_spend_micros": 1124880000,
  "pacing_spend_micros": 1125000000,
  "diff_micros": -120000,
  "diff_pct": 0.0107,
  "classified_cause": "LATE_EVENT_MERGE_PENDING"
}
```

---

*End of document — Netflix system design interview prep: Ads Demand Reporting ETL.*
