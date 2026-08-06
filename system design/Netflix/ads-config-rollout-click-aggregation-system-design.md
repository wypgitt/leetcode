# System Design: Ads Config Rollout & Click Aggregation

> **Focus areas:** Versioned global config · Canary / staged rollout · Config propagation to decision nodes · Click event ingestion · Idempotent aggregation · Reporting freshness vs correctness
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS (config read vs click ingest vs aggregate), explicit deal-breakers, Netflix Ads 2025–26 interview themes
> **Interview theme:** Netflix Ads — ship ads configuration safely worldwide while aggregating billions of clicks for advertiser reporting

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

Goal: **safely roll out versioned ads configuration globally** (targeting rules, caps, pacing knobs, creative mappings) and **aggregate click events** into durable reporting facts without double-counting or losing attribution to config versions.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Config publish + canary + click aggregation pipeline | Full ad decision / auction engine |
| Config | Ads serving knobs, line items, eligibility | Billing contracts / CRM |
| Clicks | Server-validated click beacons → aggregates | Impression counting (sibling) |
| Rollout | Progressive % / region / tenant canary | Feature flags for unrelated product |
| Reporting | Near-real-time click totals + config version lineage | Advertiser UI wireframes |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is config? | Campaign/line/creative metadata, caps refs, pacing, geo, segment bindings | Versioned blob + relational SoT |
| F2 | Who publishes? | Ads ops / automated trafficking API | RBAC + audit trail |
| F3 | Rollout model? | Canary by region, % traffic, or account allowlist | Rollout controller + sticky assignment |
| F4 | Rollback? | Instant revert to prior version | Immutable versions; pointer swap |
| F5 | Decision node freshness? | Seconds to low minutes acceptable with version stamp | Push + pull hybrid; TTL caches |
| F6 | Click definition? | User-initiated on interactive ad unit; debounced | Schema + fraud filters |
| F7 | Click attribution? | Tie to impression_id, decision_id, config_version | Join keys on event |
| F8 | Aggregation grain? | Hourly + daily by campaign/line/creative/geo | Rollups + idempotent reduce |
| F9 | Late clicks? | Accept within 7–30d window; rest to quarantine | Watermark + reconciliation |
| F10 | Cross-region? | Global config; regional click ingest | Multi-region Kafka + global warehouse |
| F11 | Config validation? | Schema + referential integrity before publish | Compiler / linter gate |
| F12 | Observability? | Per-version error rates, canary diff metrics | Shadow compare + dashboards |

**MVP functional scope (lock with interviewer):**

1. Immutable config versions with monotonic `config_version` and content hash.
2. Publish pipeline: validate → compile → store → notify decision fleet.
3. Canary rollout: 1% → 10% → 50% → 100% with automatic rollback on SLO breach.
4. Decision nodes pull/subscribe; every ad response includes `ads_config_version`.
5. Click ingestion API with auth, schema validation, idempotency on `click_id`.
6. Stream to aggregation: minute/hour buckets keyed by campaign dimensions.
7. Reporting tables: clicks, unique_clickers (approx), config_version lineage.
8. Ops dashboard: active version map, canary cohort metrics, lag alarms.

**Out of MVP (explicitly defer):**

- Multi-tenant self-serve config UI
- Real-time sub-second advertiser dashboards at 1,000×
- ML-driven auto-canary without human gate
- Client-trusted click counts as billing SoT
- Active-active config writes without CRDT merge policy

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Config propagation latency? | Most nodes within 30–120s | p99 publish→serve < 2 min |
| N2 | Click ingest latency? | Async OK | p99 ACK < 50ms; E2E aggregate < 15 min |
| N3 | Rollback time? | Immediate pointer revert | < 30s global effective |
| N4 | Duplicate clicks? | Idempotent | At-least-once safe; exactly-once in aggregates |
| N5 | Availability config read? | Critical for ads tier | 99.95% with last-known-good cache |
| N6 | Click loss? | Minimal | < 0.01% with outbox + DLQ |
| N7 | Scale | Through 1000× clicks | See scale table |
| N8 | Audit | Who changed what when | Immutable audit log 7y retention |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Trafficker publishes v8842 → validation passes → canary 1% → metrics green → full rollout.
2. Decision node receives push → refreshes local snapshot → serves ads stamped v8842.
3. User clicks interactive ad → player sends click beacon → ingest ACK → aggregate increments.
4. Reporting job materializes hourly click totals by campaign for advertiser API.
5. Rollback: ops reverts pointer to v8841 → nodes refresh → new decisions use old config.
6. Shadow mode: compile v8842 but only compare metrics without serving.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Bad config breaks parsing | Validation blocks publish; prior version remains active |
| Canary shows CTR anomaly | Auto-halt rollout; page on-call; optional auto-rollback |
| Node misses push notification | Pull fallback on TTL expiry; stale cache bounded |
| Duplicate click_id retry | Idempotency store returns OK without double count |
| Click arrives before impression in warehouse | Late join via decision_id; quarantine if orphan > policy |
| Clock skew on click ts | Server receive time authoritative for bucketing |
| Partial regional rollout stuck | Per-region rollout state machine; independent rollback |
| Config version mismatch in decision debug | Sampled logging; tracing by version |
| Aggregation lag spike | Backpressure ingest; scale consumers; SLA dashboard |
| Fraud burst on click endpoint | Rate limit + bot score; don't pollute aggregates |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ads-tier DAU | 5M | 50M | 200M | 500M+ |
| Decision nodes | 200 | 2K | 10K | 50K |
| Config reads / s (cached) | 20K | 200K | 2M | 20M |
| Config publishes / day | 500 | 2K | 10K | 50K |
| Peak click beacons / s | 500 | 5K | 50K | 500K |
| Distinct config versions / month | 2K | 10K | 50K | 200K |
| Aggregate rows / day | 10M | 100M | 1B | 10B |
| Click idempotency keys (TTL window) | 50M | 500M | 5B | 50B |

**Split classes:** config publish ≠ config read (decision) ≠ click ingest ≠ stream aggregate ≠ warehouse ETL.

**What each jump forces:**

- **10×:** Compiled config snapshots on CDN/object store; decision sidecars; Kafka partitioning by campaign_id.
- **100×:** Regional config distribution hubs; click ingest edge POPs; Flink/Spark streaming aggregates; version-indexed caches.
- **1,000×:** Hierarchical config diff (only deltas); approximate unique clickers (HLL); tiered storage for idempotency; separate hot/cold aggregate paths.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like AVOD: server-side ad decision; clicks on interactive formats (pause ads, product tiles).
- Config SoT in relational store; compiled artifact in object storage for fast fan-out.
- Clicks are **measurement facts**, not eligibility inputs on hot path (except optional fraud blocklist async).
- Sibling docs: frequency capping, pacing, ads data model, demand reporting ETL.

**Scope statement:**

> Design a **versioned ads config rollout system** with canary controls and fast rollback, plus a **click aggregation pipeline** that ingests idempotent click events and produces reporting-ready aggregates stamped with config lineage — scaling from ~500 clicks/s through 10× / 100× / 1,000× with explicit split of config-plane vs data-plane QPS.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Config read amplification

```text
Peak ad decisions = 20,000 / s (baseline)
Each decision loads compiled config snapshot (cached locally)
Cache miss rate ~0.1% → 20 remote fetches/s per cluster
Snapshot size ~2–5 MB compiled; delta patches ~50 KB at 100×
```

**Deal-breaker:** fetching full relational config per request from Postgres.

### 2.2 Click ingest rate

```text
CTR on interactive units ~0.5–2% of impressions
Impressions ~5K/s baseline → clicks ~25–100/s (use 500/s peak with bursts)
Click payload ~500 B → 500 × 500 B ≈ 250 KB/s ingress
At 1000×: 500K clicks/s → 250 MB/s → shard by campaign_id hash
```

### 2.3 Idempotency storage

```text
TTL window 30 days for click_id dedupe
500 clicks/s × 86400 × 30 ≈ 1.3B keys at baseline if 100% unique — too big
Reality: partition TTL 7d hot + bloom prefilter; ~50M working set baseline
Key size ~40 B → ~2 GB × replication 3 ≈ 6 GB cluster
```

### 2.4 Aggregation write rate

```text
Roll up to minute buckets: campaign × line × creative × geo ≈ 50K active combos
Updates/minute ≈ 50K (merge in stream processor)
Hourly materialization → 50K rows/hour to warehouse
At 100×: 5M combos → hierarchical rollup (campaign first)
```

### 2.5 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Config publish | 0.01/s | 0.1/s | 0.5/s | human + API bounded |
| Config fetch (miss) | 20/s | 200/s | 2K/s | CDN-backed |
| Decision local read | 20K/s | 2M/s | 20M/s | in-memory snapshot |
| Click ingest POST | 500/s | 50K/s | 500K/s | regional |
| Stream aggregate updates | 50K/min | 5M/min | 50M/min | partitioned |
| Rollout controller eval | 1/s | 10/s | 100/s | metrics-driven |

### 2.6 Latency budget

| Stage | Budget |
|-------|--------|
| Click ingest ACK | < 50ms p99 |
| Idempotency check | < 5ms |
| Kafka produce | < 10ms |
| Aggregate visible (near-line) | < 15 min p95 |
| Config canary step | 5–30 min observation |
| Global rollback effective | < 30s |

### 2.7 Critical bottlenecks

1. Publishing uncompiled relational joins on every decision node refresh.
2. Single global Kafka topic for all clicks without partition key discipline.
3. Canary metrics contaminated by seasonality without cohort control.
4. Idempotency store unbounded TTL → cost explosion.
5. Treating config rollout and click pipeline as one QPS number in interviews.

### 2.8 Cost intuition

```text
Dominant: Kafka retention + stream compute + idempotency KV
Config: object storage + CDN negligible vs click path
Track: $/1B clicks ingested; $/config publish; canary rollback MTTR
```

---

## 3. High-Level Design

### 3.1 Two subsystems

```text
A) Config Control Plane: Author → Validate → Compile → Version → Rollout → Fan-out
B) Click Data Plane: Beacon → Ingest → Dedupe → Stream → Aggregate → Warehouse
```

Linked by **config_version** on every click event and decision record.

### 3.2 Config entities

| Entity | Role |
|--------|------|
| `ConfigDraft` | Mutable work-in-progress |
| `ConfigVersion` | Immutable published artifact + metadata |
| `CompiledSnapshot` | Decision-optimized blob (indexes, adjacency) |
| `RolloutPlan` | Stages: canary %, regions, allowlists |
| `ActivePointer` | Current prod version per scope (global/region) |
| `AuditEntry` | Who/when/why for every change |

### 3.3 Click entities

| Entity | Role |
|--------|------|
| `ClickEvent` | Raw fact from player |
| `IdempotencyRecord` | click_id → applied |
| `MinuteAggregate` | Partial combiner state |
| `HourlyClickFact` | Warehouse-facing rollup |
| `ConfigLineage` | version → hash → publish ts |

### 3.4 Config publish API (logical)

```text
PublishConfig(draft_id, rollout_plan) → ConfigVersion
Steps:
  1. Lint: schema, dangling refs, cap rule sanity
  2. Compile: flatten hierarchy, build indexes
  3. Persist version row + upload snapshot to object store
  4. Create RolloutPlan instance (default 1→10→50→100)
  5. Notify Rollout Controller + pub/sub invalidate
```

### 3.5 Decision node config load

```text
On start / TTL / push:
  resolve ActivePointer → fetch CompiledSnapshot(version)
  atomic swap in-memory pointer
  expose ads_config_version in health + decisions
```

### 3.6 Click ingest API (logical)

```text
RecordClick(click_id, impression_id, decision_id, creative_id, ts, config_version) → 202
Steps:
  1. AuthN device/session token
  2. SETNX click_id in idempotency KV (TTL 7–30d)
  3. Enrich: geo, profile hash, fraud score async
  4. Produce to Kafka topic clicks.v1 keyed by campaign_id
  5. ACK fast; never block on warehouse
```

### 3.7 Rollout controller

| Stage | Gate metrics |
|-------|--------------|
| 1% canary | Error rate, null ad rate, latency vs control |
| 10% | CTR variance, revenue proxy, cap block rate delta |
| 50% | Regional parity checks |
| 100% | Promote pointer; archive rollout |

Automatic rollback if any hard SLO breached for N consecutive windows.

### 3.8 Aggregation logic

```text
Flink job:
  keyBy(campaign_id, line_id, creative_id, geo, hour_bucket)
  aggregate: count, sum, approx_distinct(profile_hash)
  emit to sink: OLAP staging + metrics bus
Idempotent sinks: upsert on (grain keys + hour)
```

### 3.9 Store choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Config SoT | PostgreSQL | ACID, relations, audit |
| Compiled blobs | S3/GCS + CDN | Fan-out bandwidth |
| Node cache | In-memory + optional local disk | Zero RTT hot path |
| Idempotency | Redis / DynamoDB TTL | Fast SETNX |
| Click log | Kafka | Durable buffer |
| Aggregates | Flink → BigQuery/Snowflake | Reporting |

### 3.10 Failure policy

| Failure | Policy |
|---------|--------|
| Config fetch fail at node | Serve last-known-good; alert if stale > TTL |
| Bad canary detected | Auto rollback pointer; freeze publish |
| Click ingest overload | 429 + client retry; never drop without DLQ |
| Kafka unavailable | Spool to regional outbox; backpressure |
| Aggregate lag | Scale consumers; delayed reporting banner |

### 3.11 Consistency model

- Config versions are **immutable**; `ActivePointer` is linearizable per scope.
- Clicks: **at-least-once** ingest, **exactly-once** aggregates via idempotency + idempotent sink.
- Cross-region: eventual config convergence bounded by push+pull; clicks land in region then replicate.

### 3.12 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Config delivery | Push notify + pull snapshot |
| Rollout | Automated canary with human gate at 50% |
| Click ACK | Fast after Kafka ack |
| Uniques | HLL in stream; exact in batch reconcile |
| Version stamp | Mandatory on click + decision |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     publish      +------------------+
| Trafficking |----------------->| Config Service   |
| UI / API    |                  +--------+---------+
+-------------+                           |
                                          | compile + version
                                          v
+-------------+     pointer      +------------------+     CDN fan-out
| Rollout     |<---------------->| Config Store     |------------------+
| Controller  |     metrics      | (PG + Object)    |                  |
+------+------+                  +------------------+                  |
       |                                                                  v
       |                                         +----------------+  +----------------+
       |                                         | Ad Decision    |  | Ad Decision    |
       |                                         | Node (snap vN) |  | Node (snap vN) |
       |                                         +--------+-------+  +--------+-------+
       |                                                  |                    |
+------+------+   click beacon                           |                    |
| Metrics /   |                                           |                    |
| Observability|<-----------------------------------------+--------------------+
+-------------+

+--------+  click POST   +----------------+   produce   +-------+
| Player |-------------->| Click Ingest   |------------>| Kafka |
+--------+               +-------+--------+             +---+---+
                                   |                          |
                                   v                          v
                          +--------+--------+        +--------+--------+
                          | Idempotency KV  |        | Flink Aggregator|
                          +-----------------+        +--------+--------+
                                                               |
                                                               v
                                                      +--------+--------+
                                                      | Warehouse /     |
                                                      | Reporting API   |
                                                      +-----------------+
```

### 4.2 Sequence: config publish & canary

```text
Ops→ConfigSvc: Publish(draft, rollout_plan)
ConfigSvc→PG: validate + insert config_versions row
ConfigSvc→ObjectStore: put compiled snapshot
ConfigSvc→RolloutCtrl: start canary 1%
RolloutCtrl→DecisionFleet: update canary assignment map
DecisionNodes: fetch snapshot if version assigned
RolloutCtrl→Metrics: compare canary vs control 15 min
RolloutCtrl→ActivePointer: promote 10%→...→100% or rollback
```

### 4.3 Sequence: click ingest to aggregate

```text
Player→Ingest: POST /clicks {click_id, impression_id, ...}
Ingest→IdemKV: SETNX click_id
  if duplicate → 200 OK noop
Ingest→Kafka: produce ClickEvent
Ingest→Player: 202 Accepted
Flink←Kafka: consume, keyBy, tumbling window 1m
Flink→Warehouse: upsert hourly facts
```

### 4.4 Sequence: rollback

```text
On-call→RolloutCtrl: Rollback(scope, to_version=v8841)
RolloutCtrl→ActivePointer: CAS swap global pointer
RolloutCtrl→PubSub: invalidate all nodes
DecisionNodes: pull v8841 snapshot within seconds
Metrics: tag post-rollback cohort separately
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Immutable config versions** — never mutate published artifacts.
2. **Idempotent click ingest** by `click_id`.
3. **ActivePointer CAS** — rollback is pointer swap, not delete.
4. **Every click carries config_version** for lineage debugging.
5. **Canary never skips validation** — bad compile cannot reach 1%.
6. **Last-known-good** on decision nodes if fetch fails.
7. **DLQ for unparseable clicks** — don't poison aggregate job.
8. **Audit trail append-only** for compliance.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Partial node fleet on old version | Bounded by TTL; monitor version dispersion |
| Canary SLO false positive | Hysteresis + multi-window confirm before rollback |
| Duplicate Kafka delivery | Idempotent sink keys prevent double aggregate |
| Click flood attack | Rate limit; exclude from billing aggregates via fraud flag |
| Object store outage | Nodes serve cached; block new publishes |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Single PG + S3 + Kafka cluster; Flink small |
| 10× | CDN for snapshots; regional ingest; partition Kafka by campaign |
| 100× | Config delta patches; multi-region active pointers; Flink autoscale |
| 1,000× | Edge click aggregation; HLL uniques; cold storage for idempotency |

### 5.3 Maintainability

- Config linter with human-readable errors for traffickers.
- Shadow compile: diff vN vs vN+1 index sizes and rule counts.
- Replay tool: re-aggregate clicks from Kafka for date range.
- Metrics: `config_version_dispersion`, `click_ingest_p99`, `aggregate_lag_min`, `canary_rollback_count`.
- No per-advertiser high-cardinality alert labels.

### 5.4 Exact algorithm: publish

```text
function publish(draft_id, rollout):
  draft = loadDraft(draft_id)
  errors = lint(draft)
  if errors: return REJECT(errors)
  compiled = compile(draft)  // indexes, adjacency lists
  version = nextVersion()
  hash = sha256(compiled)
  store.put(version, compiled, hash)
  audit.append(PUBLISH, version, actor)
  rolloutCtrl.start(version, rollout)
  return version
```

### 5.5 Exact algorithm: canary assignment

```text
function assignedVersion(request_context):
  if request_context.account in rollout.allowlist: return rollout.candidate
  bucket = hash(stable_user_id) % 10000
  if bucket < rollout.percent * 100: return rollout.candidate
  return activePointer.prod
```

### 5.6 Exact algorithm: click ingest

```text
function recordClick(event):
  if not auth.valid(event.token): return 401
  if not schema.valid(event): return 400
  if not idem.setnx(event.click_id, ttl=30d): return 202 DUPLICATE
  event.server_ts = now()
  kafka.produce(key=event.campaign_id, value=event)
  return 202 ACCEPTED
```

### 5.7 Config compilation

Compiler outputs:
- Inverted indexes: segment_id → line items
- Cap rule index by scope
- Creative metadata map
- Validation bitmaps for geo/device

Compilation time budget: seconds, not minutes — precompute heavy joins offline.

### 5.8 Click fraud & quality

| Signal | Action |
|--------|--------|
| Bot score high | Tag `fraud_flag`; exclude from advertiser totals |
| Click faster than human (<200ms from impression) | Drop at ingest |
| Duplicate device burst | Rate limit |
| Missing impression_id | Quarantine bucket for manual review |

### 5.9 Multi-region

| Data | Strategy |
|------|----------|
| ActivePointer | Global control plane; optional regional overrides |
| Snapshots | Replicated object store + CDN |
| Clicks | Regional ingest → global Kafka mirror or aggregate per region then merge |
| Idempotency | Regional KV; cross-region duplicate rare — accept or global idem at 100× |

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Edit published version in place | Unreproducible incidents; audit fail |
| Skip canary for 'tiny' changes | Tiny schema typo takes down decision fleet |
| Sync warehouse write on click POST | Latency meltdown |
| Global click topic no partition key | Hot campaign melts single partition |
| Use clicks to cap frequency live | Wrong latency class; use impressions sibling |
| One blended QPS in interview | Miss config vs click split |

### 5.11 Progressive scale deep dive

**1× (~500 clicks/s, 500 publishes/day)**
Single region; nightly batch reconcile; manual canary promotion.

**10×**
CDN snapshots; automated canary gates; Flink on K8s; idempotency Redis cluster.

**100×**
Delta config patches; regional rollout controllers; click ingest autoscale; separate fraud pipeline.

**1,000×**
Edge pre-aggregate minute counters; tiered idempotency (bloom + KV); config sharded by publisher/market; HLL uniques standard.

### 5.12 Security & privacy

- Config APIs require ops RBAC; MFA for production pointer changes.
- Click payloads minimize PII — use hashed profile_id.
- Advertisers never receive raw click streams — aggregates only.
- Audit logs immutable (WORM bucket or append-only table).

### 5.13 Rollout playbook

```text
Shadow compile → 1% canary 15m → 10% 1h → 50% (human OK) → 100%
Rollback: pointer revert + node invalidate + postmortem template
Freeze publishes during major events (Super Bowl) unless emergency
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Config mutability | Immutable versions + pointer |
| Delivery | Compiled snapshot via CDN + local cache |
| Rollout | Percent canary with auto-rollback |
| Click path | Fast ACK + Kafka + stream aggregate |
| Dedupe | click_id SETNX + idempotent sink |
| Lineage | config_version on all events |

### 6.2 Risks

1. Version dispersion during rollout causing inconsistent user experience
2. Canary metrics misinterpretation → false rollback or missed bad deploy
3. Idempotency TTL too short → double-count in reports
4. Config snapshot too large for edge nodes
5. Click aggregate lag eroding advertiser trust

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Split config plane vs click data plane |
| 5–15 | Versioning, compile, pointer rollback |
| 15–25 | Canary assignment + metrics gates |
| 25–35 | Click ingest idempotency + Kafka + Flink |
| 35–45 | Scale table; deal-breakers; lineage |

---

## 7. Deeper / Related Interview Questions

### 7.1 Config semantics

**Q: Why immutable versions?**
A: Reproducibility, rollback, audit; edits create new version.

**Q: Why compile?**
A: Decision path needs O(1) indexes, not SQL joins at 20K QPS.

**Q: Global vs regional config?**
A: Mostly global snapshot; regional pointer for market-specific launches.

### 7.2 Rollout

**Q: How pick canary cohort?**
A: Stable hash on profile_id; avoid session churn flip-flop.

**Q: Auto vs manual promote?**
A: Auto through 10%; human gate at 50% for major releases.

**Q: Rollback impact on in-flight sessions?**
A: New decisions pick new version; mid-pod uses decision-time version.

### 7.3 Clicks

**Q: Click vs impression?**
A: Impression = view; click = interaction; different pipelines, join in reporting.

**Q: Why not increment caps on click?**
A: Caps on impressions per product policy; clicks too sparse for freq caps.

**Q: Late clicks?**
A: Backfill aggregates with idempotent upsert; watermark in stream job.

### 7.4 Consistency

**Q: Exactly-once clicks?**
A: End-to-end via idempotency + idempotent sink; at-least-once Kafka OK.

**Q: Config stale read?**
A: Bounded TTL; stamp version on response for debug.

### 7.5 Store

**Q: Why Kafka not direct DB?**
A: Spike buffering; multiple consumers (agg, fraud, debug).

**Q: Why object store for config?**
A: Large blob fan-out cheaper than DB replication to 10K nodes.

### 7.6 Ops

**Q: Emergency rollback?**
A: Pointer CAS + pub/sub; don't delete bad version (forensics).

**Q: Replay aggregates?**
A: Reset sink partition + replay Kafka with same idempotency keys.

### 7.7 Privacy

**Q: Advertiser sees user clicks?**
A: No — campaign-level aggregates; GDPR delete propagates to aggregates.

### 7.8 Interview traps

**Q: 'Just use feature flags'**
A: Flags lack compile validation, audit, and ads-specific lineage.

**Q: 'Batch clicks hourly only'**
A: OK for MVP; state freshness SLA for dashboards.

**Q: 'One Postgres for everything'**
A: Config SoT yes; not click hot path.

### 7.9 Metrics

**Q: What pages on?**
A: Canary error delta; config fetch fail rate; aggregate lag > SLA; idempotency KV memory.

### 7.10 Comparison

**Q: vs blue/green fleet?**
A: Pointer + snapshot swap similar; canary % finer than full fleet swap.

**Q: vs web analytics pipeline?**
A: Stricter idempotency + billing adjacency; lower latency ACK.

---

## 8. Appendices

### A1. ConfigVersion schema

```text
ConfigVersion {
  version: int64,
  content_hash: sha256,
  compiled_uri: string,
  parent_version: int64?,
  published_at: timestamp,
  published_by: actor_id,
  rollout_state: ACTIVE|CANARY|ROLLED_BACK|ARCHIVED,
  schema_version: int
}
```

### A2. RolloutPlan schema

```text
RolloutPlan {
  plan_id,
  target_version,
  stages: [{percent, min_duration_min, slo_gates[]}],
  allowlist_account_ids[],
  region_scope: GLOBAL|REGional[],
  auto_rollback: bool
}
```

### A3. ClickEvent schema

```text
ClickEvent {
  click_id,           // ULID
  impression_id,
  decision_id,
  campaign_id, line_item_id, creative_id,
  profile_hash,
  device_id,
  ads_config_version,
  client_ts,
  server_ts,
  geo, device_type,
  fraud_score?,
  interactive_unit_type
}
```

### A4. Launch checklist

- [ ] Config linter covers dangling line items
- [ ] Canary auto-rollback tested
- [ ] Node LKG cache chaos tested
- [ ] Click idempotency TTL signed off
- [ ] Aggregate replay runbook
- [ ] Version dispersion dashboard
- [ ] Audit log retention verified

### A5. Glossary

| Term | Meaning |
|------|--------|
| ActivePointer | Current production config version handle |
| CompiledSnapshot | Decision-optimized config blob |
| Canary | Subset traffic on candidate version |
| LKG | Last-known-good cached snapshot |
| Lineage | Traceability via config_version |

### A6. Interviewer traps

| Trap | Pushback |
|------|----------|
| Mutate version in place | Immutable + pointer |
| Clicks on decision path | Async measurement |
| No canary | Fleet-wide blast radius |
| Single QPS number | Split planes |

### A7. Reliability test plan

1. Publish bad schema → rejected.
2. Canary breach → auto rollback < 60s.
3. Duplicate click_id → single aggregate count.
4. Node offline during publish → LKG serves.
5. Kafka replay → aggregates unchanged.
6. 10× click spike → autoscale ingest + lag bounded.

### A8. 60-second summary

> **Config rollout** = immutable versions, compiled snapshots, canary pointer promotion, fast rollback. **Click aggregation** = idempotent ingest, Kafka buffer, stream rollups with config lineage — never block ads decision on either path; scale by CDN fan-out, partition discipline, and split QPS classes.

### A9. Related systems map

```text
Trafficking API → Config Service → Object Store/CDN → Decision Nodes
Player → Click Ingest → Kafka → Flink → Warehouse → Advertiser Reporting
Rollout Controller ↔ Metrics ↔ ActivePointer
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Publish→99% nodes fresh | < 2 min |
| Rollback effective | < 30s |
| Click ingest p99 | < 50ms |
| Aggregate freshness p95 | < 15 min |
| Canary false rollback rate | < 5% of rollouts |

### A11. Worked numeric example

```text
v8841 active, publish v8842
Canary 1%: hash(profile)%100 < 1 → v8842 else v8841
Click from v8842 decision: click.config_version=8842
Aggregate hour bucket: (campaign K, hour H) count += 1 WHERE version=8842
Rollback: pointer=8841; new clicks on 8841 decisions only
```

### A12. Pseudo-SQL config versions

```sql
CREATE TABLE config_versions (
  version BIGINT PRIMARY KEY,
  content_hash BYTEA NOT NULL,
  compiled_uri TEXT NOT NULL,
  published_at TIMESTAMPTZ NOT NULL,
  published_by TEXT NOT NULL,
  rollout_state TEXT NOT NULL
);
CREATE TABLE active_pointer (
  scope TEXT PRIMARY KEY,
  version BIGINT REFERENCES config_versions(version)
);
```

### A13. Ownership

| Concern | Owner |
|---------|-------|
| Config service + rollout | Ads Control Plane |
| Click ingest + aggregates | Ads Measurement |
| Compiled snapshot format | Ads Serving |
| Advertiser reporting API | Ads Data |
| Fraud scoring | Trust & Safety |

### A14. Progressive checklist

| Scale | Must have |
|-------|----------|
| 1× | Versioning, canary manual, click dedupe, hourly agg |
| 10× | CDN snapshots, auto canary gates, Flink |
| 100× | Delta patches, regional ingest, replay tooling |
| 1,000× | Edge pre-agg, HLL uniques, sharded pointers |

### A15. Naive design comparison

| Naive | Why it fails |
|-------|--------------|
| SQL poll for config | Latency + load |
| Push JSON diffs without compile | Decision CPU explodes |
| Direct INSERT click to warehouse | Spikes kill DB |
| No idempotency | Retries double revenue |

### A16. On-call cheat sheet

1. Check `config_version_dispersion` max-min.
2. If error spike post-publish → rollback pointer.
3. Click lag → scale Flink; check Kafka consumer lag.
4. Idempotency memory → verify TTL job.
5. Freeze publishes if rollback loop detected.

### A17. Sample click debug record

```text
{
  "click_id": "clk_abc",
  "decision_id": "dec_xyz",
  "ads_config_version": 8842,
  "campaign_id": "k_1",
  "fraud_flag": false,
  "aggregate_bucket": "2026-08-06T15"
}
```

### A18. Interaction with frequency caps

Config rollout changes which cap rules exist; cap **counts** live in sibling counter store. Version stamp links 'which rules were active' not 'how many impressions'.

### A19. Cost worksheet

```text
kafka_storage ≈ clicks_per_day × bytes × retention_days
flink_cu ≈ peak_events/s × processing_cost
idem_kv ≈ active_keys × 40B × repl
config_cdn ≈ snapshots × size × regions (usually small)
```

### A20. Explicit non-goals

- Real-time bid adjustments from click stream
- Replacing ads trafficking CRM
- Client-side config as source of truth
- Sub-second global strong consistency on ActivePointer

---

*End of document — Netflix system design interview prep.*
