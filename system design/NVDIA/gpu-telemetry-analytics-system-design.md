# System Design: GPU Telemetry Collection and Analytics

> **Focus areas:** High cardinality · Per-GPU metrics · Label explosion · Ingest · Downsampling · Aggregation · Alerting · Query path · Retention tiers  
> **Style:** Telemetry pipeline design with progressive scale on series count / points/sec (10× → 100× → 1,000×)  
> **Quality bar:** Correct cardinality arithmetic, explicit control of label sets, honest hot/warm/cold tiers, resolved ingest vs query ownership

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

Goal: **bound the telemetry system**—collect GPU metrics at useful fidelity for ops and ML platform teams **without** letting unbounded labels create a cardinality explosion that melts TSDB memory and query latency.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What metrics? | util%, mem used, temp, power, SM occupancy, ECC counts, NVLink bytes, clocks, XID errors | Typed metric catalog; not arbitrary strings from day 1 |
| F2 | Labels / dimensions? | gpu_uuid, node, sku, mig_profile, job_id, user, project, cell, cluster | **Controlled label set**; job/user often high-churn |
| F3 | Scrape vs push? | Agent on node scrapes DCGM/NVML → push or remote-write | Prefer agent push with batching at scale |
| F4 | Resolution? | 1–10s for hot debugging; 1m+ for fleet dashboards | Multi-resolution via downsampling |
| F5 | Alerting? | Temp/power/ECC/XID, util anomalies, silent GPU death | Alert on aggregated + exemplar raw |
| F6 | Who queries? | SRE dashboards, job UX (“your GPU util”), capacity planning, finops | Separate query SLOs by persona |
| F7 | Trace correlation? | Tie metrics to job_id / training run | Join path via controlled labels or side index |
| F8 | Logs/events? | XID, driver logs—optional sibling pipeline | Don’t stuff high-cardinality logs into TSDB |
| F9 | Multi-tenant? | Isolate projects; prevent one job’s labels from exploding shared TSDB | Quotas, relabel, drop |
| F10 | Retention? | Raw short; 1m medium; 1h/daily long | Hot/warm/cold tiers |
| F11 | Cardinality control? | Hard requirement | Allowlists, recording rules, aggregation gateways |
| F12 | Historical analytics? | Capacity trends, failure correlations | Columnar cold store / warehouse |

**MVP functional scope (lock with interviewer):**

1. Node GPU agent collects catalog metrics via DCGM/NVML every N seconds.  
2. Emit with **allowlisted labels** only; map job_id via control-plane/scheduler side channel when possible.  
3. Ingest gateway: auth, validate, relabel, shard by `hash(gpu_uuid)` or `node`.  
4. Hot TSDB for raw short retention; recording rules for common aggregates.  
5. Alertmanager-style rules on temp/ECC/XID/missing heartbeats.  
6. Query API + dashboards; exemplars for drill-down.  
7. Downsample to 1m / 1h; cold export to object storage.  
8. Cardinality governor: reject/drop series over budget.

**Out of MVP:**

- Full distributed tracing for every CUDA kernel.  
- Unlimited per-user custom metrics without review.  
- Perfect second-level retention for 1 year.  
- Cross-region active-active same series dual-write without conflict story.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest durability | Accept ⇒ mostly durable | ACK after WAL/Kafka; RPO seconds |
| N2 | Hot query latency | Dashboards interactive | p50 < 200ms, p99 < 2s for 1h range aggregates |
| N3 | Alert fire latency | Safety-critical | p99 < 1–2 min from condition true |
| N4 | Cardinality bound | Explicit budget | Per-tenant / global series caps |
| N5 | Availability | Ingest HA | 99.9%; degrade to local buffer on outage |
| N6 | Correctness | No silent unit confusion | Metric catalog with units |
| N7 | Multi-tenant isolation | Noisy neighbor | Quotas + shuffle shards |
| N8 | Cost | Linear-ish with series×retention | Force downsampling |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Agent scrapes 8 GPUs → batches → ingest → TSDB → dashboard shows util.  
2. ECC correctable rate rises → alert → page SRE with node/gpu links.  
3. User opens job page → query util by `job_id` for run duration.  
4. Nightly downsample raw → 1m; weekly to cold Parquet.  
5. Capacity planner queries 90-day 1h averages by SKU.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Job_id label on every 1s series for millions of short jobs | Cardinality bomb → relabel: drop job_id from raw; keep in exemplar/event |
| Tenant sends custom label `pod_template_hash` | Drop via allowlist |
| Agent burst after network partition | Backfill with rate limits; drop too-old points |
| TSDB shard hot (popular SKU) | Re-shard; aggregate gateway first |
| Alert flapping on temp near threshold | Hysteresis + for: duration |
| Missing metrics (GPU died) | Absent alert / heartbeat metric |
| Query scans 1e9 series | Reject / force aggregate metrics |
| Duplicate timestamps from retry | Idempotent upsert / last-write |
| MIG instances appear/disappear | Controlled `mig_profile` label; lifecycle GC series |

### 1.4 Scales (Progressive) — series & points/sec

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPUs | 1,000 | 10,000 | 100,000 | 1,000,000 |
| Metrics / GPU (catalog) | 20 | 25 | 30 | 40 |
| Active jobs (label churn) | 500 | 5,000 | 50,000 | 500,000 |
| **Raw series (gpu×metric, no job)** | 20K | 200K | 2M | 20M |
| **Series if job_id on raw** | ~10M+ | ~100M+ | **billions** | impossible |
| Scrape interval | 5s | 5s | 10s | 10–15s |
| **Points/sec (raw, no job label)** | 4K | 40K | 200K | 1.3M–2M |
| Alert rules evaluated /s | 100 | 1K | 10K | 100K |
| Concurrent dashboard queries | 20 | 100 | 500 | 2K |
| Hot retention | 24h | 24h | 12–24h | 6–12h |
| Warm 1m retention | 30d | 30d | 60d | 90d |
| Cold retention | 1y | 1y | 2y | 3y |

**What each jump forces:**

- **10×:** Remote-write sharding; recording rules; label allowlists enforced.  
- **100×:** Aggregation gateway (pre-aggregate by node/sku); separate hot vs warm stores; cardinality governor.  
- **1,000×:** Hierarchical rollups; per-cell ingest; query federator; cold-only for long range; strict drop of high-churn labels on raw path.

### 1.5 Etc. (Constraints & Assumptions)

- Source of truth for **job placement** is scheduler/control plane—not the TSDB.  
- Agents trusted enough to emit metrics; still validate sizes and labels.  
- “Analytics” includes both **real-time ops** and **historical capacity**—different stores OK.  
- We optimize for **fleet health + job UX**, not CUDA kernel profiling (Nsight-class tools elsewhere).

**Scope statement:**

> Design a GPU telemetry and analytics pipeline that ingests per-GPU metrics (util, memory, temp, power, SM occupancy, ECC, NVLink) with controlled labels, survives progressive scale on series and points/sec via aggregation/downsampling/retention tiers, and provides alerting plus query paths without cardinality explosion from job/user dimensions.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Cardinality arithmetic (the interview centerpiece)

```text
Let G = GPU count
Let M = metrics per GPU (catalog)
Let L_job = active jobs attaching as labels on raw series

Naive raw series (identity labels only: gpu, node, sku):
  S_raw = G × M
  Baseline: 1000 × 20 = 20,000 series

If each point also labeled by job_id and jobs are short-lived:
  series ≈ G × M × (distinct job_ids in retention window)
  1000 GPUs × 20 × 500 jobs → 10,000,000 series  (already ugly)
  At 100× GPUs + 50K jobs → 100K × 30 × 50K = 1.5e11  (absurd)

Rule: NEVER put unbounded job_id/user on raw long-lived series identity.
```

**Deal-breaker:** treating “Prometheus labels are free” as true.

### 2.2 Points/sec

```text
points/s ≈ S_active / interval_seconds

Baseline raw: 20,000 series / 5s = 4,000 points/s
10×: 40,000 points/s
100× with 2M series / 10s = 200,000 points/s
1,000×: 20M series / 10s = 2,000,000 points/s

Payload ~20–40 B compressed/point → 2M × 30 B ≈ 60 MB/s ingest (manageable with shards)
Memory pain is usually INDEX of series, not raw byte rate alone
```

### 2.3 Series index memory (order of magnitude)

```text
TSDB series metadata often ~1–10 KB / series (varies wildly by impl)
Use 2 KB/series for interview math:

Baseline 20K × 2 KB ≈ 40 MB
100× 2M × 2 KB ≈ 4 GB per full replica set (plus inverted index)
1,000× 20M × 2 KB ≈ 40 GB → shard by cell / hash(gpu)

If job labels inflate to 200M series: 400 GB metadata → outage
```

### 2.4 Storage retention

```text
Raw 24h at 4K points/s × 30 B × 86400 ≈ 10 GB / day baseline (compressed better)
1,000× raw: 2M points/s × 30 B × 86400 ≈ 5.2 PB/day if kept—impossible
→ MUST downsample; keep raw short; 1m/1h for long

1m rollup: 60× fewer points than 1s; 6× fewer than 10s raw
```

### 2.5 Alert evaluation cost

```text
Rules on aggregates (per node/sku) not per job series
Baseline: hundreds of rules × scrape eval
1,000×: evaluate on rollup stream / recording rules, not raw 20M series
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Cardinality explosion** (labels)  
2. **Series churn** (create/destroy)  
3. **Hot query fan-out** without pre-aggregation  
4. **Ingest shard imbalance**  
5. **Alert eval on raw**  
6. **Backfill storms** after outages  

---

## 3. High-Level Design

### 3.1 Metric catalog (controlled schema)

| Metric | Type | Unit | Typical labels (raw) |
|--------|------|------|----------------------|
| `gpu_utilization` | gauge | percent | gpu_uuid, node, sku, mig |
| `gpu_memory_used_bytes` | gauge | bytes | same |
| `gpu_temperature_celsius` | gauge | C | same |
| `gpu_power_watts` | gauge | W | same |
| `gpu_sm_occupancy` | gauge | percent | same |
| `gpu_ecc_correctable_total` | counter | count | same |
| `gpu_ecc_uncorrectable_total` | counter | count | same |
| `gpu_nvlink_rx/tx_bytes_total` | counter | bytes | same + link_id (bounded) |
| `gpu_xid_errors_total` | counter | count | same + xid (careful) |
| `agent_heartbeat` | gauge | 1 | node |

**Allowlist:** only these names + approved label keys. Unknown dropped or quarantined.

### 3.2 Label tiers (cardinality control strategy)

| Tier | Labels | Where attached | Retention |
|------|--------|----------------|-----------|
| **Identity (raw)** | gpu_uuid, node, sku, cell, mig_profile | Every raw point | Short hot |
| **Join (side)** | job_id, user, project | Side index / exemplar / event stream | Job lifetime |
| **Fleet aggregate** | sku, cell, pool | Recording rules | Long |
| **Forbidden on raw** | pod_hash, container_id, request_id, full image digest | — | — |

**Job correlation patterns:**

```text
A) Exemplars: rare annotated points with job_id
B) Span table: (job_id, gpu_uuid, start, end) in OLTP/SQL — query joins
C) Separate “job metrics” stream with aggressive aggregation (avg util over job)
```

**Chosen:** B + C—span index from scheduler events; job-level rollups; raw stays identity-only.

### 3.3 Ingest pipeline

```text
GPU Agent (DCGM/NVML)
  → local buffer (disk spool)
  → Ingest Gateway (mTLS, authz, schema validate, relabel, cardinality check)
  → Kafka / Pulsar (topic by cell or hash)
  → TSDB Writers (hot)
  → Aggregation workers → Warm store
  → Cold exporter → Object storage (Parquet)
```

**Options for hot store:**

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Prometheus + remote-write | Familiar | Cardinality footguns | Unbounded labels |
| B. VictoriaMetrics / Mimir / Thanos | Scale features | Ops complexity | Team can’t run |
| C. Custom wide-table | Control | Build cost | Underestimate index |
| D. Warehouse only | Cheap long-term | Bad alerting latency | Using for pages |

**Chosen path:** Agent → Kafka → **Mimir/VM-like hot TSDB** + recording/aggregate gateway; cold Parquet for analytics.

### 3.4 Downsampling & aggregation

```text
Raw (5–15s) ──retention 6–24h──► discard
       │
       ├── recording: avg/max by (node, sku) every 30s
       ├── 1m rollup: avg/max/p95 → warm 30–90d
       └── 1h rollup → cold months–years
```

**Counter handling:** store increases carefully; downsample with `increase()`/`rate()` semantics, not naive avg of counter values.

### 3.5 Cardinality governor

```text
On ingest:
  1. Drop non-allowlisted labels
  2. Enforce max series per (tenant, metric)
  3. Enforce max churn (new series/min)
  4. If over budget: drop lowest-priority metrics first; alert platform owners
  5. Never accept arbitrary user labels on raw path
```

**Budget example:**

```text
Baseline global raw budget: 100K series (headroom over 20K)
Per project job-rollup budget: 50K series
Reject with actionable error metrics: cardinality_dropped_total
```

### 3.6 Alerting

| Alert | Signal | Notes |
|-------|--------|-------|
| GPUHighTemp | temp > thresh for 5m | Hysteresis |
| ECCUncorrectable | increase > 0 | Page |
| XIDFatal | xid in fatal set | Correlate node |
| GPUMissing | absent `agent_heartbeat` or util series | Distinguish agent vs GPU |
| PowerCapThrottle | clocks/power limits | Capacity impact |
| UtilStuckZero on RUNNING job | join span index | Avoid false positives on idle pools |

**Eval path:** alert on **recording rules / aggregates**, attach exemplar link to raw gpu_uuid.

### 3.7 Query path

```text
Dashboards / API
  → Query Frontend (authz, cache, range split, tenant routing)
  → Hot TSDB (recent raw + short rollups)
  → Warm store (1m)
  → Cold query engine (Parquet/warehouse) for long ranges
```

**Rules:**

- Default UI queries aggregates.  
- Drill-down to gpu_uuid raw only for short windows.  
- Reject queries estimated to touch > N series without aggregation.

### 3.8 Retention tiers

| Tier | Resolution | Retention | Store | Use |
|------|------------|-----------|-------|-----|
| Hot | raw scrape | 6–24h | TSDB | Debug, pages |
| Warm | 1m | 30–90d | TSDB/rollup | Job UX, SRE |
| Cold | 1h / daily | 1–3y | Object+columnar | Capacity, finops |
| Events | XID/log | 30–90d | Log store | Forensics |

### 3.9 Multi-cell & multi-tenant

```text
Per cell: agents → cell ingest → cell hot TSDB
Global: query federator + cold warehouse
Tenant: project_id on rollups; authz at query frontend
Shuffle shard noisy tenants’ ingest
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| job_id on raw | Side index + job rollups | Cardinality | Label on every series |
| Ingest buffer | Kafka | Backpressure, replay | Sync write only to TSDB |
| Long-range query | Cold columnar | Cost | Raw TSDB forever |
| Alerting | On aggregates | Eval cost | Scan 20M series |
| Custom metrics | Approval + budget | Safety | Free-for-all labels |
| Scrape interval at 1000× | 10–15s raw | Cost | 1s fleet-wide forever |

---

## 4. Architecture Diagram

### 4.1 End-to-end pipeline

```text
+------------------+     +------------------+     +------------------+
| GPU Agents       |---->| Ingest Gateway   |---->| Kafka (sharded)  |
| DCGM/NVML        |     | validate/relabel |     +--------+---------+
+------------------+     | cardinality gov  |              |
                         +------------------+              v
                                              +------------------+
                                              | Hot TSDB Writers |
                                              +--------+---------+
                                                       |
         +---------------------------------------------+------------------+
         |                       |                     |                  |
         v                       v                     v                  v
+----------------+     +----------------+     +----------------+  +--------------+
| Recording /    |     | Alert Evaluator|     | Query Frontend |  | Cold Exporter|
| Aggregate GW   |     +--------+-------+     +--------+-------+  +------+-------+
+--------+-------+              |                      |                 |
         |                      v                      v                 v
         v               +-------------+        +-------------+   +-------------+
+----------------+       | Pager/Slack |        | Dashboards  |   | Parquet/WH  |
| Warm Rollups   |       +-------------+        | Job UX API  |   +-------------+
+----------------+                              +-------------+

Scheduler/CP ── job span events ──► Span Index (job↔gpu time ranges)
```

### 4.2 Sequence: ingest point

```text
Agent → scrape NVML → {gpu_uuid, metric, value, ts, labels_allowlisted}
Agent → batch compress → Gateway
Gateway → auth → schema → drop bad labels → cardinality check
Gateway → Kafka topic cell-a-partition(hash(gpu))
Writer → WAL → TSDB head → ACK (async path: spool if Kafka down)
```

### 4.3 Sequence: job util query

```text
UI: GET util for job J
API → Span Index: gpus=[g1..g8], [t0,t1]
API → Query Frontend: avg(gpu_utilization{gpu_uuid=~"g1|..."}[t0:t1])
     or prefer job_rollup_util{job_id=J} if present
Return timeseries + per-gpu breakdown (short range only)
```

### 4.4 Sequence: cardinality attack

```text
Misconfigured agent adds label request_id=uuid each scrape
Gateway: label not allowlisted → drop
Metric cardinality_dropped_total{reason="label"} ++
Alert: IngestDropSpike for cluster
Series index unaffected
```

### 4.5 Downsample flow

```text
Raw samples (hot)
   │
   ├─ every 1m: aggregate by (gpu_uuid, metric) → warm
   ├─ every 1h: aggregate by (sku, cell, metric) → cold fleet
   └─ GC raw older than HotRetention
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Raw series identity ⊆ allowlisted labels | Gateway relabel |
| R2 | Accept only catalog metric names (or quarantined) | Schema registry |
| R3 | Per-tenant series budget enforced | Governor |
| R4 | Alerts don’t require unbounded series scans | Recording rules |
| R5 | Agent outage doesn’t lose all data | Local spool + retry |
| R6 | Counter resets handled in rate rules | `rate`/`increase` semantics |
| R7 | Authz on query (no cross-project job peek) | Query frontend |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| Kafka down | Agent spool to disk; restart replay; drop if spool full (metric) |
| Hot TSDB shard loss | Replicate; repair from Kafka retention |
| Governor false positive | Allow emergency override with audit |
| Wrong units in catalog | Versioned catalog; dual-publish migration |
| Span index lag | Job UX falls back to time-bounded gpu filter |

### 5.2 Scalability

**1×:** Single Prometheus + Grafana; 20K series fine; still enforce allowlists (habit).

**10×:** Remote-write to HA TSDB; Kafka; recording rules; basic governor.

**100×:** Cell ingest; aggregate gateway; warm rollups; query frontend cache; strict no job_id on raw.

**1,000×:** Hierarchical rollups (gpu→node→sku→cell→global); federated query; cold warehouse default for >7d; 10–15s scrape; exemplar sampling.

**Backpressure:**

- Gateway returns 429 → agent increases batching / interval temporarily.  
- Kafka lag alert → autoscale writers; load-shed low-priority metrics (SM occupancy first, keep temp/ECC).  
- Query admission control for heavy ranges.

### 5.3 Maintainability

- Versioned **metric catalog** checked into git.  
- Recording rule coverage tests (unit + replay).  
- Cardinality dashboards as first-class SRE view.  
- “Why was my series dropped?” self-service reasons.  
- Chaos: kill gateway, fill spool, verify recovery.

### 5.4 Ownership resolution

| Concern | Owner |
|---------|-------|
| Metric definitions | Telemetry platform + HW ops |
| Label allowlist | Telemetry platform |
| Job↔GPU spans | Scheduler / control plane events |
| Alert routing | SRE |
| Long-term capacity analytics | Data/finops on cold store |
| On-node scrape | GPU agent |

**Contradiction trap:** using TSDB as SoT for “what job ran where”—that’s the scheduler.

### 5.5 High-cardinality deep dive

**Explosion sources:**

1. `job_id` / `run_id` / `user_email` on raw  
2. `link_id` unbounded or per-packet  
3. `xid` as label with huge fan-out without aggregation  
4. Auto-discovered custom metrics from sidecars  
5. Histogram unbounded dynamic labels  

**Controls ranked:**

1. Allowlists (prevent)  
2. Aggregate gateways (reduce)  
3. Budgets + load-shed (contain)  
4. Quarantine topic for bad producers (isolate)  

### 5.6 Node failure & silent GPU death

```text
Signals:
  - absent(agent_heartbeat)
  - absent(gpu_utilization) while node Ready in CP
  - xid / ecc spikes
  - util stuck + power ~ idle unexpectedly during RUNNING job (join spans)

CP health vs telemetry:
  CP NotReady is control decision
  Telemetry informs CP/SRE but should not alone flap cordon without policy
```

### 5.7 Fairness / multi-tenant noisy neighbor

- Ingest quotas per project (points/s, new series/min).  
- Query concurrency limits per tenant.  
- Shuffle sharding writers.  
- Priority: safety metrics (temp/ECC) > util > experimental.

### 5.8 Consistency & clocks

- Prefer scrape timestamp from agent monotonic + node clock with max skew clamp.  
- Gateway rejects points too far in future/past.  
- Downsample windows aligned in UTC; document lookback.

### 5.9 Security

- mTLS agents; rotate.  
- Query authz on project/cell.  
- Scrub possible PII in forbidden labels (emails).  
- Cold bucket encryption; lifecycle policies.

### 5.10 Observability of the observability system

| Dashboard | Metrics |
|-----------|---------|
| Ingest | points/s, lag, drop reasons |
| Cardinality | series count, churn/min, top offenders |
| Query | latency, series touched, cache hit |
| Alert | fire rate, flapping, eval duration |
| Spool | agent disk usage |

### 5.11 Progressive resolution policy

```text
Interactive debug (P0 incident): allow 1–5s raw for affected nodes only (dynamic config)
Normal fleet: 10–15s
Warm: 1m
Cold: 1h
Never: 1s raw for 1M GPUs retained for weeks
```

### 5.12 Analytics use cases mapped to tiers

| Use case | Tier |
|----------|------|
| Page on ECC | Hot + alert rules |
| Job page util chart | Warm job rollup / span join |
| SKU capacity trend 6m | Cold |
| NVLink imbalance debug | Hot raw short window |
| Finops GPU-hours | Cold + scheduler billing (better SoT) |

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Catalog + allowlisted labels; show cardinality math.  
2. Ingest path agent → gateway → Kafka → TSDB.  
3. Governor + no job_id on raw; span index.  
4. Downsample tiers + query frontend.  
5. Alerting on aggregates.  
6. Scale jumps 10×/100×/1000×.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Agent, catalog, gateway allowlist, hot TSDB, basic alerts, 1m rollup |
| 10× | Kafka, HA TSDB, governor, recording rules |
| 100× | Cell ingest, aggregate GW, span index, warm/cold |
| 1,000× | Federated query, hierarchical rollups, load-shed priorities |

### 6.3 Top risks

1. job_id on raw series.  
2. Unbounded custom labels.  
3. Alert eval on raw at 1000×.  
4. Keeping raw forever.  
5. Using TSDB as job inventory SoT.  
6. Backfill stampede.

### 6.4 One-sentence design

> A catalog-constrained GPU telemetry pipeline that keeps raw series identity small, correlates jobs via side indexes and rollups, and scales points/sec through Kafka, aggregation gateways, and hot/warm/cold retention—so cardinality stays a budget, not an accident.

---

## 7. Deeper / Related Interview Questions

### 7.1 Cardinality

**Q: What is cardinality here?**  
A: Number of unique time series (metric × label-set).

**Q: Why is job_id dangerous?**  
A: Short-lived values create endless new series; index memory and compaction die.

**Q: How do you still show per-job util?**  
A: Span index join or precomputed job rollup metrics with TTL.

**Q: What’s a safe label?**  
A: Low-cardinality, long-lived: sku, cell, node, gpu_uuid (gpu_uuid scales with fleet but bounded by G).

**Q: Is gpu_uuid itself a problem at 1M?**  
A: Manageable with sharding; it’s O(G×M), not O(G×M×jobs).

### 7.2 Ingest

**Q: Push or pull?**  
A: At GPU fleet scale, push/remote-write from agents with spool is typical; pull Prometheus scrape OK at small scale.

**Q: Exactly-once ingest?**  
A: At-least-once + idempotent timestamps; duplicates OK for gauges.

**Q: What if agent is down?**  
A: Absent metrics + CP health; spool if process up but network down.

### 7.3 Downsampling

**Q: Can you avg a counter?**  
A: No—use increase/rate then aggregate.

**Q: Why multiple resolutions?**  
A: Cost/latency trade-off; dashboards rarely need 5s data from last year.

**Q: When raw is required?**  
A: Incident debug short windows; keep hot retention.

### 7.4 Alerting

**Q: Alert on every GPU series?**  
A: Prefer node/sku aggregates + “any GPU above thresh” recording rules.

**Q: Flapping?**  
A: `for:` duration, hysteresis, inhibit during drain/upgrade.

**Q: Missing data alerts?**  
A: Heartbeat metrics; distinguish scrape fail vs true zero util.

### 7.5 Query

**Q: User queries 90 days at 5s?**  
A: Rewrite to cold 1h; or reject.

**Q: Federated query cost?**  
A: Push aggregates upward; don’t scatter-gather raw globally.

**Q: Cache key?**  
A: Canonicalized promql/expression + range + step + tenant.

### 7.6 Multi-tenant & fairness

**Q: Noisy project?**  
A: Ingest quotas; drop; quarantine; contact owners.

**Q: Cross-tenant leakage?**  
A: Authz in query frontend; no shared unrestricted Grafana admin for tenants.

### 7.7 Failure & ops

**Q: Kafka lag storm?**  
A: Autoscale; load-shed low-priority metrics; keep ECC/temp.

**Q: TSDB OOM?**  
A: Usually cardinality—emergency drop rules; block new series.

**Q: Clock skew?**  
A: Clamp; reject futures; monitor offset.

### 7.8 Comparison traps

**Q: vs logging everything?**  
A: Logs ≠ metrics; XID to log pipeline; metrics stay numeric series.

**Q: vs tracing CUDA?**  
A: Different product; sampling profilers not fleet TSDB.

**Q: vs control plane health?**  
A: CP owns Ready/NotReady decisions; telemetry informs.

**Q: Why not SQL wide table only?**  
A: Alerting/realtime worse; hybrid is fine.

### 7.9 Estimation drills

**Q: 100K GPUs × 30 metrics × 10s interval → points/s?**  
A: Series=3M; points/s=3e6/10=300K.

**Q: Add 50K job_ids on raw—series?**  
A: Roughly 3M × active label combinations—order 1e11 risk; refuse design.

**Q: Memory for 20M series at 2KB?**  
A: ~40GB metadata order-of-magnitude → shard.

### 7.10 Interview traps (high value)

- Show S = G×M before labels.  
- Prove job_id explosion math.  
- Allowlist labels.  
- Side index for jobs.  
- Hot/warm/cold.  
- Alert on rollups.  
- Load-shed priority (ECC > util).  
- Counter vs gauge downsample.  
- Reject huge queries.  
- Cardinality governor metrics.  
- Cell-local ingest.  
- Don’t use TSDB as scheduler SoT.  
- Spool on disconnect.  
- Histogram label caution.  
- Absent vs zero.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- metric_catalog
(metric_name TEXT PK,
 type TEXT, -- gauge|counter|histogram
 unit TEXT,
 description TEXT,
 allowed_labels TEXT[],
 priority INT)  -- load-shed order

-- series_budget
(tenant_id, scope, max_series, max_churn_per_min)

-- job_gpu_spans
(job_id UUID,
 gpu_uuid TEXT,
 node_id TEXT,
 start_ts TIMESTAMPTZ,
 end_ts TIMESTAMPTZ NULL,
 PRIMARY KEY(job_id, gpu_uuid, start_ts))

-- ingest_drop_log (sampled)
(ts, agent_id, reason, metric_name, label_key)
```

```text
-- hot TSDB identity labels (example)
gpu_utilization{gpu_uuid, node, sku, cell, mig_profile}

-- warm job rollup
job_gpu_util_avg{job_id, project, sku}  // TTL with job + grace
```

### 8.2 API checklist

- [ ] Agent remote-write / push API  
- [ ] Query: range/instant with authz  
- [ ] Admin: catalog CRUD, budgets  
- [ ] Alerts: rule CRUD, silence  
- [ ] Job UX: `GET /jobs/{id}/gpu-metrics`  
- [ ] Cardinality: top offenders report  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Series | Unique metric + label-set identity |
| Cardinality | Count of series |
| Churn | Rate of series creation/destruction |
| Recording rule | Precomputed aggregate timeseries |
| Exemplar | Trace/job annotation on a sample |
| Rollup / downsample | Lower resolution aggregate |
| Governor | Ingest admission for cardinality |
| Hot/warm/cold | Retention tiers |
| Span index | job↔gpu time range table |
| Load-shed | Drop low-priority metrics under pressure |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Catalog, allowlist, basic TSDB, alerts |
| 10× | Kafka, HA, governor, recording rules |
| 100× | Cell ingest, span index, warm/cold, query frontend |
| 1000× | Hierarchical rollups, federation, priority load-shed |

### 8.5 Agent emit sketch

```text
Batch {
  agent_id, node_id, cell,
  samples: [
    { name: "gpu_utilization", labels: {gpu_uuid, sku, mig_profile},
      type: gauge, value: 0.82, ts: 1710000000 }
  ]
}
```

### 8.6 Cardinality worked examples

```text
Example A — GOOD raw:
  G=10,000; M=25; S=250,000
  interval=10s → 25,000 points/s

Example B — BAD raw with job label:
  active jobs in 24h retention touching GPUs: 100,000 distinct job_ids
  if series per (gpu, metric, job): unbounded explosion
  even if only “current job” label flips: high churn kills TSDB

Example C — Job rollup approach:
  S_job = active_jobs × metrics_job (~5) ≈ 500K series at 100× jobs
  TTL destroy after job end + 24h → bounded
```

### 8.7 Alert rule sketches

```text
ALERT GPUEccUncorrectable
IF increase(gpu_ecc_uncorrectable_total[10m]) > 0
FOR 0m
LABELS { severity="page" }

ALERT GPUTempHigh
IF max by (node, gpu_uuid) (gpu_temperature_celsius) > 85
FOR 5m
LABELS { severity="ticket" }

ALERT GPUTelemetryAbsent
IF absent(agent_heartbeat) == 1
FOR 3m
```

### 8.8 Interview “say this” summary (60 seconds)

> Per-GPU metrics with a strict catalog and allowlisted identity labels; job correlation via scheduler span index and TTL’d job rollups—not raw job_id labels. Ingest through validated gateways and Kafka into hot TSDB, with governors against cardinality. Downsample to warm 1m and cold 1h/Parquet. Alert on aggregates; query frontend enforces authz and rejects unbounded scans. Scale by cells, aggregation gateways, and load-shedding low-priority metrics first.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| job_id on raw | Explosion math |
| Unlimited custom metrics | Budget + approval |
| Raw forever | Cost; tiers |
| Alert on 20M series | Recording rules |
| TSDB as job SoT | Scheduler owns placement |
| Avg of counters | Wrong semantics |
| 1s scrape at 1M GPUs | Points/sec + retention death |
| Global single Prometheus | Shard/cell |

### 8.10 Reliability test plan

1. Inject forbidden labels → dropped; series count stable.  
2. Kill Kafka → agent spool → recovery without huge gaps (or known drop metrics).  
3. Fire ECC synthetic → alert within SLO.  
4. Query 180d raw → rewritten/rejected to cold.  
5. Tenant churn storm → governor engages; safety metrics retained.  
6. Counter reset → rate rules stay sane.

### 8.11 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Ingest gateway success | > 99.9% |
| Kafka lag | < 60s p99 steady |
| Alert fire latency (ECC) | p99 < 2m |
| Dashboard query (1h aggregate) | p99 < 2s |
| Cardinality budget headroom | > 20% |

### 8.12 Related systems map

```text
GPU Agent → Gateway/Governor → Kafka → Hot TSDB → Alerting
                 │                        ↓
                 │                  Query Frontend → UI
                 ↓                        ↓
           Span Index ← Scheduler   Warm/Cold Stores
```

### 8.13 Estimation cheat-sheet

```text
S_raw ≈ G × M_catalog          # identity labels only
PPS   ≈ S_raw / interval
S_blowup ≈ S_raw × distinct_high_churn_label_values  # AVOID

mem_index ≈ S × few_KB
storage_raw_day ≈ PPS × bytes/point × 86400

prefer under-scrape + rollups over unbounded labels
```

### 8.14 Label allowlist (example)

```text
ALLOWED_RAW: gpu_uuid, node, sku, cell, pool, mig_profile, link_id
ALLOWED_ROLLUP: project, sku, cell, pool
ALLOWED_JOB_METRIC: job_id, project, sku
FORBIDDEN: user_email, request_id, pod_template_hash, image_id, cmdline
```

### 8.15 Priority load-shed order

```text
P0 keep: ecc_uncorrectable, xid, temperature, agent_heartbeat, power
P1 keep: utilization, memory_used
P2 shed first: sm_occupancy, nvlink detailed, experimental histograms
```

### 8.16 Query rewrite examples

```text
# User asks:
rate(gpu_nvlink_rx_bytes_total{job_id="J"}[5m])  # job_id not on raw

# Frontend:
lookup spans → gpu set G
query rate(gpu_nvlink_rx_bytes_total{gpu_uuid=~"G"}[5m]) over job window
# or job_nvlink_rx_rollups{job_id="J"}
```

---

*End of design doc. Open with §2.1 cardinality math; whiteboard §3.2–3.8 labels/ingest/tiers; close with traps §7.10.*
