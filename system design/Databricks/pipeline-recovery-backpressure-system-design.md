# System Design: Pipeline Recovery and Backpressure

> **Focus areas:** Lag · DLQ · Replay · Degradation · Credit-based flow control · Retry storms  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct lag arithmetic, explicit bounded-buffer invariants, honest at-least-once semantics, controlled catch-up not infinite retry  
> **Interview theme:** Databricks — data platform reliability; streaming ingestion; ETL pipelines; Delta/Lakehouse sinks

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

Goal: design **cross-cutting backpressure and recovery** for multi-stage data pipelines (ingest → transform → sink) so overload produces **bounded latency and memory**, not cascading failure, unbounded lag, or silent data loss—and recovery after outages clears lag without melting downstream systems.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Pipeline types? | **Streaming** (Kafka/Kinesis), **micro-batch** (Structured Streaming), **batch ETL** (scheduled jobs) | Unified control plane; transport-specific adapters |
| F2 | Backpressure scope? | End-to-end: slow sink must slow upstream | Credit-based or pull-based flow control |
| F3 | Lag definition? | Consumer offset lag, stage queue depth, watermark delay | Standardized lag SLIs per pipeline |
| F4 | Retry policy? | Transient errors retry with backoff; permanent → DLQ | Bounded retries; jitter; poison detection |
| F5 | DLQ? | Quarantine bad records with payload + error context | Durable DLQ store; replay tooling |
| F6 | Replay? | Reprocess DLQ or offset range idempotently | Operator approval; rate-limited redrive |
| F7 | Degradation modes? | Shed load, skip enrichment, sample, delay non-P0 | Explicit mode flags visible to users |
| F8 | Prioritization? | P0 pipelines / tenants first under stress | Priority lanes + admission control |
| F9 | Autoscale hooks? | Signal autoscaler when lag sustained | Integration with compute orchestrator |
| F10 | Idempotent sink? | Upsert/Merge keys; dedupe by event_id | Document effectively-once requirements |
| F11 | Multi-tenant? | Per-tenant lag SLOs and fairness | Tenant-scoped credits and quotas |
| F12 | Observability? | Lag dashboards, mode indicators, DLQ age | Alert on SLO burn not just absolute lag |
| F13 | Kill switches? | Stop ingestion for broken pipeline | Circuit break entire pipeline graph |
| F14 | Schema evolution? | Bad schema → DLQ not infinite retry | Schema registry + compatibility checks |

**MVP functional scope (lock with interviewer):**

1. **Lag sensors** on each stage: Kafka consumer lag, internal queue depth, sink write p99.
2. **Credit-based admission** at pipeline ingress: producer receives credits; each record consumes 1 credit; credits replenished by downstream ack rate.
3. **Bounded buffers** between stages; on full buffer → propagate backpressure upstream (429 / pause poll).
4. **Retry controller:** max 5 attempts, exponential backoff with full jitter, classify transient vs permanent.
5. **DLQ topic/store** with `{pipeline_id, partition, offset, payload, error_code, ts, attempt}`.
6. **Degradation state machine:** `NORMAL → CONGESTED → SHED → PAUSED` with user-visible reason.
7. **Replay API:** `POST /pipelines/{id}/replay` with offset range or DLQ filter; rate cap enforced.
8. **Autoscaler webhook:** if lag > threshold for 10 min → scale consumers (bounded by sink capacity).

**Out of MVP (explicitly defer):**

- Exactly-once end-to-end without idempotent sink
- Automatic DLQ replay without human approval for PII pipelines
- Cross-region active-active lag coordination
- ML predictive lag forecasting
- Self-healing schema inference on poison messages

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Memory bound? | No unbounded in-process queues | Max buffer per stage = 2× steady throughput × p99 stage latency |
| N2 | Lag SLO (streaming)? | Business-dependent | p95 lag < 5 min baseline; alert at 15 min |
| N3 | Recovery time? | After sink fix, clear backlog | Catch-up at ≤1.5× steady produce rate without SLO violation |
| N4 | DLQ latency to quarantine | Fast poison isolation | Permanent failure → DLQ within 60s |
| N5 | Availability | Pipeline pauses rather than OOM | 99.9% control plane; data plane degrades gracefully |
| N6 | Replay safety | No duplicate side effects | Idempotent sink or explicit dedupe store |
| N7 | Fairness | Tenant A flood doesn't starve B | Min 10% egress bandwidth per tenant under congestion |
| N8 | Control loop stability | No retry storm | Retry QPS ≤ 20% of healthy throughput |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Steady state: credits flow producer → stage1 → stage2 → sink; lag flat near zero.
2. Transient sink 503: retries succeed within budget; lag spike clears in minutes; no DLQ.
3. Consumer scale-out: autoscaler adds workers; lag decreases; credits increase upstream.
4. Scheduled batch catch-up: replay throttled to sink capacity; completes overnight.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Sink permanently slow (10×) | Enter CONGESTED → reduce credits → SHED low priority → pause if needed |
| Poison message (bad JSON) | 1–2 retries → DLQ; partition processing continues |
| Retry storm amplifying load | Retry budget token bucket; separate retry lane |
| Consumer stuck (no heartbeat) | Rebalance; lag attributed; alerts |
| Duplicate replay | Sink merge on event_id; metrics track replay duplicates suppressed |
| Upstream push (HTTP) ignores 429 | Hard disconnect; client must retry with backoff |
| Kafka partition skew | Hot partition triggers partition split / keyed reroute |
| Schema break mid-stream | Incompatible → DLQ batch; pipeline PAUSED until schema fixed |
| Catch-up faster than sink | Throttle replay/catch-up rate dynamically |
| DLQ full | Block pipeline (fail closed) or spill to cold storage with paging |
| Clock skew in lag metrics | Use broker/log append time; not client clock |
| Partial batch failure | Structured Streaming: commit good rows; bad → DLQ per row |
| Multi-hop pipeline one stage down | Upstream buffers bounded then backpressure entire graph |
| Autoscale adds consumers but sink fixed | Detect ** ineffective scale**; stop scaling; degrade instead |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Pipelines (active) | 100 | 1K | 10K | 100K |
| Peak records / s (platform) | 50K | 500K | 5M | 50M |
| Partitions (total) | 500 | 5K | 50K | 500K |
| Lag events / day (spikes) | 10 | 100 | 1K | 10K |
| DLQ records / day | 1K | 10K | 100K | 1M |
| Replay jobs / month | 20 | 200 | 2K | 20K |
| Control plane decisions / min | 1K | 10K | 100K | 1M |
| Tenants | 50 | 500 | 5K | 50K |

**What each jump forces:**

- **10×:** Per-pipeline controllers sharded; centralized metrics; standardized DLQ format.
- **100×:** Hierarchical control (platform → cell → pipeline); tenant credit pools; replay queues.
- **1,000×:** Cell isolation; aggregate lag rollups; automated catch-up throttling; DLQ tiered storage.

### 1.5 Etc. (Constraints & Assumptions)

- Delivery semantics: **at-least-once** default; effectively-once requires idempotent sink + dedupe.
- Kafka-style transports: consumer **pull** gives natural backpressure via `max.poll.records` and pause.
- HTTP push sources need explicit **429/503 + Retry-After**.
- Sinks (Delta, Snowflake, JDBC) often have **hard write TPS** limits.
- Operators accept **paused** pipelines over **wrong data** or **OOM crashes**.

**Scope statement:**

> Design a pipeline reliability control plane that measures lag, applies credit-based backpressure end-to-end, isolates poison messages in a DLQ, supports rate-limited replay, and degrades gracefully—scaling from ~100 pipelines to 100K via sharded controllers and tenant-fair catch-up throttling.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Lag growth when sink is saturated

```text
Produce rate P = 10,000 records/s
Sink capacity C = 8,000 records/s (sustained)
Net lag growth = P - C = 2,000 records/s

After 30 min outage recovery starting at lag L0 = 0:
  During outage (30 min): lag += P × 1800 = 10K × 1800 = 18M records
  Catch-up at 1.2×C without new produce: time = 18M / (1.2×8000) ≈ 1875s ≈ 31 min
  If produce continues during catch-up: need throttle or scale sink
```

**Critical insight:** Catch-up rate must be **explicitly budgeted**; autoscaling consumers alone does not help if sink is the bottleneck.

### 2.2 Buffer sizing

```text
Stage latency p99 = 2s
Steady throughput = 5,000 rec/s
Minimum buffer to avoid stall under burst factor 2:
  B = 2 × 5000 × 2 = 20,000 records

At 1 KB/record → 20 MB in-memory per stage (fine)
At 100×: 50K rec/s → 200K buffer → 200 MB (still OK per stage; many stages → GB without bounds)
→ enforce global memory budget per pipeline
```

### 2.3 Retry amplification

```text
Healthy throughput 10K/s, transient error rate 1%
Naive immediate retry → +100/s retries (OK)

If sink down and all 10K/s retry every 1s:
  → 10K retries/s + 10K new = 20K effective (meltdown)

Cap retry rate at 10% of baseline = 1K/s
Excess failures → DLQ or delay with visibility
```

### 2.4 DLQ storage

```text
1K poison records/day × 10 KB avg = 10 MB/day baseline
100×: 100K/day × 10 KB ≈ 1 GB/day
Retain 90 days ≈ 90 GB → S3 + index in Postgres
```

### 2.5 Control plane load

```text
100 pipelines × 1 lag sample/s = 100 samples/s
Each controller PID/AIMD update ~1 ms → single host OK to 10K pipelines with batching
100×: 10K pipelines → shard controllers 100/ shard leader
```

### 2.6 Credit rate math

```text
Sink ack rate A = 8,000/s
Credit refill (ingress): α × A, α ∈ [0.5, 1.0] (leave headroom)
If lag L > L_target: α reduced proportionally (AIMD)
If lag critical: α = 0 → PAUSED
```

### 2.7 Bottlenecks (ranked)

1. Sink write capacity (uncoordinated consumer scale-out)  
2. Unbounded retries amplifying overload  
3. Hot partition lag masking as healthy average  
4. DLQ replay overwhelming sink during incident  
5. Missing idempotency on replay → duplicate business rows  
6. Push producers ignoring backpressure signals  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Pipeline           → DAG of stages; SLO; priority; tenant_id
Stage              → consumer/processor; inbound/outbound buffers
LagSensor          → emits lag_seconds, queue_depth, sink_p99 per stage
CreditController   → grants/revokes credits on ingress edges
RetryPolicy        → max_attempts, backoff, error taxonomy
DLQStore           → durable quarantine + metadata index
DegradeManager     → NORMAL|CONGESTED|SHED|PAUSED transitions
ReplayJob          → scoped redrive with rate limit + audit
AdmissionGate      → token bucket at pipeline entry
AutoscalerBridge   → lag signals → compute orchestrator
```

### 3.2 Options: backpressure mechanisms

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Bounded queues + block | Simple | Blocks threads | Async/event-loop pipelines |
| B. Kafka pause/resume | Native pull | Kafka-only stages | HTTP ingress |
| C. Credit-based end-to-end | Propagates globally | Protocol needed | Can't modify producers |
| D. Drop on overload | Never OOM | Data loss | Finance/audit pipelines |
| E. Scale-out only | Easy story | Sink-limited | Fixed sink TPS |

**Chosen path:**

- **MVP:** Credit-based ingress + bounded inter-stage buffers + Kafka pause + retry/DLQ.  
- **100×+:** Hierarchical controllers; tenant credit pools; dedicated replay service with global throttle.

### 3.3 Credit-based flow control

```text
Each edge (A → B) has credit counter C_AB max = buffer_size
B acks processed records → increment credits at A
A may not emit unless credit > 0
Ingress adapter translates credits to:
  - Kafka: max.poll.records dynamic
  - HTTP: 200 with credits in header / 429 when 0
  - Internal: async channel capacity
```

**Refill AIMD on lag:**

```text
every 10s:
  if lag_p95 < target: α = min(α + 0.05, 1.0)      # additive increase
  if lag_p95 > 2×target: α = max(α × 0.5, 0.1)    # multiplicative decrease
  credits_per_sec = α × measured_sink_throughput
```

### 3.4 Retry and DLQ policy

```text
on failure(record, error):
  if permanent(error): dlq(record, error); ack offset (skip poison)
  elif attempts >= MAX: dlq(record, error); ack
  else:
    if retry_bucket.try_consume():
      schedule_retry(record, backoff(attempts))
    else:
      defer_or_dlq(record)  # visibility timeout
```

**Permanent errors:** schema validation, constraint violation, auth 401, file not found (config).

**Transient:** 503, timeout, throttling 429 from sink.

### 3.5 Degradation state machine

```text
NORMAL:
  full enrichment; all priority classes served

CONGESTED (lag > warn OR buffer > 70%):
  reduce α; alert; autoscaler hook

SHED (lag > critical OR sink error rate > 20%):
  drop/skip optional enrichment stages
  serve P0 only; P2 gets 429 at ingress

PAUSED (lag > max OR DLQ blocked OR operator):
  stop ingress credits = 0; drain buffers safely
  visible status: "Paused: sink unavailable"
```

### 3.6 Replay design

```text
POST /pipelines/{id}/replay
  {source: DLQ | OFFSET_RANGE, filter, max_rate, dry_run, approver_id}

Replay worker:
  read at ≤ max_rate
  re-validate schema
  write sink with same idempotency key event_id
  mark DLQ entry REPLAYED or FAILED
Audit log every replay job
```

**Deal-breaker:** Unbounded replay after incident without sink capacity check.

### 3.7 Autoscale integration

```text
if lag_p95 > T for 10 min AND sink_p99 healthy AND consumer_cpu > 70%:
  emit scale_out signal (add N workers)
if lag high BUT sink at limit:
  do NOT scale; enter CONGESTED instead
if lag low for 30 min:
  scale_in
```

### 3.8 Multi-tenant fairness

```text
Platform egress budget E tokens/s shared
Tenant i weight w_i
Max tenant share in SHED: max_i ≤ 0.5 × E (prevent monopolization)
Min guarantee: each tenant ≥ 0.1 × E / N_active unless P0 override
```

### 3.9 API shape (MVP)

```text
GET /pipelines/{id}/health
  → {mode, lag_p95, buffer_pct, credits_rate, dlq_depth}

POST /pipelines/{id}/pause | /resume
  → operator override

POST /pipelines/{id}/replay
  → {replay_job_id, estimated_records, max_rate}

GET /dlq?pipeline_id=&since=
  → paginated poison records (RBAC)

POST /pipelines/{id}/config/degrade
  → {shed_stages[], priority_filters}
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Loss vs lag | Pause/shed before drop | Auditability | Silent drop of billing events |
| Retry vs DLQ | Bounded retries | Stop amplification | Infinite retry on poison |
| Catch-up speed | Throttle to sink | Stability | Full blast replay |
| Lag metric | Max partition lag | Catch hot spots | Consumer group avg only |
| Push vs pull ingress | Credits + 429 | Explicit pressure | Hope client behaves |

---

## 4. Architecture Diagram

### 4.1 End-to-end pipeline with control plane

```text
                        +----------------------+
                        | Pipeline Control     |
                        | Plane (controllers)  |
                        +----------+-----------+
                                   | credit rates, mode
     +-----------------------------+-----------------------------+
     |                             |                             |
     v                             v                             v
+----------+    credits      +-----------+    credits      +-----------+
| Ingress  |---------------> | Stage 1   |---------------> | Stage 2   |
| Adapter  |                 | Process   |                 | Process   |
+----+-----+                 +-----+-----+                 +-----+-----+
     |                             |                             |
     | Kafka pause / HTTP 429      | bounded queue               |
     v                             v                             v
 [Source Bus]                  [Buffer]                      [Buffer]
                                   |                             |
                                   +-------------+---------------+
                                                 v
                                          +-------------+
                                          | Sink Writer |
                                          | (Delta/JDBC)|
                                          +------+------+
                                                 |
                    +----------------------------+----------------------------+
                    |                            |                            |
                    v                            v                            v
             +------------+              +---------------+            +---------------+
             | Lag Metrics|              | DLQ Store     |            | Replay Service|
             | TSDB       |              | (S3+index)    |            | (rate limit)  |
             +------------+              +---------------+            +---------------+
                    |
                    v
             +---------------+
             | Autoscaler    |
             | Bridge        |
             +---------------+
```

### 4.2 Sequence: congestion propagates upstream

```text
Sink        Stage2       Controller    Stage1       Ingress      Producer
  |--slow-->|            |             |            |            |
  |         |--buffer full----------->|             |            |
  |         |            |--reduce credits--------->|            |
  |         |            |             |--pause poll----------->|
  |         |            |             |            |--429----->|
  |         |            |--mode=CONGESTED-------- dashboard     |
```

### 4.3 Sequence: poison message to DLQ

```text
Stage1      RetrySvc     DLQ         OffsetCommit
  |--fail-->|            |             |
  |         |--retry 1-->|             |
  |--fail-->|            |             |
  |         |--retry 2-->|             |
  |--fail-->|            |             |
  |         |--permanent classify       |
  |         |--write------------------->|
  |         |--commit offset------------------------>|
  |         |            |             | (continue partition)
```

### 4.4 Sequence: controlled replay

```text
Operator    ReplaySvc    DLQ        Stage2      Sink
  |--POST-->|            |            |           |
  |         |--validate sink capacity------------>|
  |         |--read batch----------------------->|
  |         |            |--process-->|           |
  |         |            |            |--merge-->|
  |         |--mark REPLAYED---------->|           |
  |<-progress report-----|            |           |
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Bounded memory:** no unbounded queue; block/shed/pause instead.  
2. **Poison isolation:** permanent failures reach DLQ; do not block partition forever.  
3. **Retry cap:** platform-wide retry QPS ≤ f(healthy_throughput).  
4. **Idempotent replay:** same `event_id` → same sink row (merge/upsert).  
5. **Offset commit after durable side effect OR DLQ** (at-least-once safe).  
6. **Mode transitions durable:** PAUSED survives controller restart.  
7. **Catch-up throttle:** replay + live produce ≤ sink budget.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Sink down | CONGESTED → PAUSED; buffer then stop ingress |
| Retry storm | Retry token bucket; separate retry topic |
| Controller crash | Stateless controller + desired state in store; reconcile |
| DLQ write fail | Fail pipeline closed; page immediately |
| Hot partition | Alert; optional key splitting; manual rebalance |
| Duplicate replay job | Idempotent replay_job_id; dedupe store |
| Schema registry down | Treat as transient briefly; then PAUSE |
| Metrics gap | Fail-safe: assume congested if blind |
| Autoscale runaway | Max workers cap; sink-aware guard |

**Offset commit protocol (say aloud):**

```text
process batch:
  transform records
  try sink write (bulk)
  on success: commit offsets
  on partial failure: split batch; good commit; bad → retry/DLQ individually
never commit before sink ack unless at-most-once explicitly allowed
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Per-pipeline sidecar controller; shared metrics; Postgres DLQ index |
| 10× | Controller shards by pipeline_id; Kafka DLQ topic; replay workers pool |
| 100× | Cell-level egress budget; lag rollup hierarchy; S3 DLQ payloads |
| 1000× | Tenant cells; global catch-up coordinator; sampled lag for long-tail pipelines |

**Partition-level control (100×):**

```text
Credits may be per-partition if skew detected:
  lag_p99_partition >> lag_median → reduce credits that partition only
Avoid starving healthy partitions
```

**Effective scale-out check:**

```text
if added_workers last 20 min AND lag not improving AND sink_p99 up:
  declare scale_ineffective; stop autoscale; degrade
```

### 5.3 Maintainability

- Standard **error taxonomy** (`TRANSIENT`, `PERMANENT`, `UNKNOWN`).  
- **Runbooks:** lag spike, DLQ growth, replay procedure, schema break.  
- **Game days:** sink 50% throttle; verify PAUSED in 5 min.  
- **Golden replay tests:** fixed event log → expected sink rows.  
- Dashboards: lag heatmap by partition, mode timeline, retry rate, DLQ age.

**Metrics:**

```text
pipeline_lag_seconds{pipeline,partition,quantile}
buffer_utilization_ratio{stage}
credit_rate{edge}
retry_attempts_total{pipeline,error_class}
dlq_depth{pipeline}
degrade_mode{pipeline}  # enum gauge
replay_rate{job_id}
sink_write_p99{pipeline}
catch_up_eta_seconds
```

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Structured Streaming job + custom lag poller
Credit: dynamic maxOffsetsPerTrigger from controller HTTP
DLQ: Kafka topic dlq.{pipeline_id}
Manual pause/resume API
Replay: CLI script with --max-rate
```

**10×**

- Dedicated control plane service  
- AIMD credit refill per pipeline  
- Autoscaler webhook to compute orchestrator  
- DLQ UI with sample payload (PII masked)  

**100×**

- Tenant credit pools at cell ingress  
- Global replay scheduler (one big replay at a time per sink)  
- Priority queues: P0 pipelines immune to SHED  
- Anomaly: retry_rate > 5× baseline → auto PAUSE  

**1000×**

- Long-tail pipelines use **sampled lag** (statistical)  
- DLQ cold tier Glacier; hot index only  
- Self-service replay with approval workflow  
- Cross-cell spillover with explicit billing  

### 5.5 Kafka-specific backpressure

```text
consumer.pause(partitions where local_buffer > high_watermark)
consumer.resume when buffer < low_watermark
max.poll.records = f(credits)
fetch.min.bytes tuned with latency trade-off
```

**Consumer rebalance storm:** static membership or cooperative sticky assignor; pause during rebalance.

### 5.6 HTTP push ingress

```text
POST /ingest
  if credits <= 0: 429 Retry-After: 5
  else: accept batch; credits -= batch_size
  async ack after durable enqueue to bus
Include X-Credits-Remaining header for client adaptation
```

Clients must implement **exponential backoff** on 429 — document in SDK.

### 5.7 Structured Streaming / micro-batch

```text
Trigger interval 1s normal; 10s when CONGESTED
maxFilesPerTrigger / maxOffsetsPerTrigger = credit budget
Watermark delay may increase under SHED (allow lateness trade-off)
```

### 5.8 DLQ schema and replay safety

```text
dlq_record {
  id, pipeline_id, stage, source_partition, source_offset,
  event_id, payload_b64, error_code, error_detail, attempts,
  first_seen, last_seen, replay_status
}
PII fields encrypted; RBAC on read
Replay requires role replay_admin + ticket_id for SOX tenants
```

### 5.9 Comparison: TCP backpressure analogy

| TCP | Pipeline analogue |
|-----|-------------------|
| Receive window | Credit count |
| ACK | Sink write ack / offset commit |
| Congestion avoidance (AIMD) | Lag-based α adjustment |
| Drop packet | DLQ (intentional quarantine, not silent loss) |
| Zero window | PAUSED mode |

Use analogy briefly — then note **application-level semantics** differ (retries, DLQ, idempotency).

### 5.10 Data model (sketch)

```text
pipelines(id, tenant_id, dag_json, slo_lag_sec, priority, mode)
stages(id, pipeline_id, type, config_json)
lag_samples(pipeline_id, partition, ts, lag_sec, depth)  -- TSDB
credit_policies(pipeline_id, edge, alpha, max_buffer)
dlq_index(id, pipeline_id, event_id, s3_key, error_code, replay_status)
replay_jobs(id, pipeline_id, spec_json, rate, state, approver)
audit_log(ts, actor, action, pipeline_id, detail)
```

---

## 6. Wrap-Up

**Design summary**

- Treat backpressure as **closed-loop control**: sensors → credit rate → ingress → lag feedback.  
- **Never retry unbounded**; poison goes to **DLQ** with audit trail.  
- **Recovery = throttled catch-up**, not max consumer count.  
- **Degrade explicitly** (CONGESTED/SHED/PAUSED) with user-visible modes.  
- **Replay is a first-class batch job** with rate limits and idempotent sinks.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Per-pipeline AIMD credits | Global tenant fairness pools |
| Manual replay approval | Workflow automation with guardrails |
| Kafka + HTTP ingress | Universal connector SDK |
| Rule-based degrade | ML lag forecasting |

**Top risks**

1. Scaling consumers without sink headroom  
2. Retry storms during partial outages  
3. Hot partition hidden by average lag  
4. Replay duplicate data without idempotency keys  

**What I'd measure first in production**

- Max partition lag, mode transition count, retry/DLQ ratio, sink p99 vs consumer count, replay job completion vs ETA, credit α over time.

---

## 7. Deeper / Related Interview Questions

1. How is credit-based flow control different from Kafka consumer pause?  
2. When do you commit offsets — before or after sink write?  
3. How to achieve effectively-once with at-least-once delivery?  
4. What goes in DLQ vs infinite retry — decision tree?  
5. How to replay without doubling chargeable sink writes?  
6. Compare backpressure to rate limiting at API gateway only.  
7. How to handle cascading pipeline DAG (A→B→C) under sink failure?  
8. Watermark vs processing-time lag — which SLO?  
9. How to test retry storm prevention in CI?  
10. Fairness when one tenant's poison fills shared DLQ?  
11. Should P0 preempt bandwidth from P2 automatically?  
12. Interaction with Delta Lake optimistic concurrency on replay?  
13. How long to keep DLQ records for compliance?  
14. Push vs pull ingress for mobile telemetry — design credits.  
15. Databricks job failure vs pipeline lag — different systems?

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "Add more Kafka consumers" | Sink capacity first |
| "Unbounded queue for catch-up" | Bounded + throttle |
| "Retry forever on error" | DLQ + cap |
| "Drop records to fix lag" | Shed optional stages; pause before drop |
| "Exactly-once everywhere" | Idempotent sink + dedupe; honest semantics |

---

## 8. Appendices

### A. Pseudocode — credit controller (AIMD)

```text
function controller_tick(pipeline):
  lag = max_partition_lag(pipeline)
  sink_ok = sink_error_rate(pipeline) < 0.05
  target = pipeline.slo_lag_sec

  if lag > 10 * target or not sink_ok:
    pipeline.mode = PAUSED
    pipeline.alpha = 0
  elif lag > 2 * target:
    pipeline.mode = SHED
    pipeline.alpha = max(pipeline.alpha * 0.5, 0.1)
  elif lag > target:
    pipeline.mode = CONGESTED
    pipeline.alpha = max(pipeline.alpha * 0.7, 0.2)
  else:
    pipeline.mode = NORMAL
    pipeline.alpha = min(pipeline.alpha + 0.05, 1.0)

  throughput = measured_sink_throughput(pipeline)
  pipeline.credit_rate = pipeline.alpha * throughput
  apply_credit_rate(pipeline, pipeline.credit_rate)
  db.save(pipeline)
```

### B. Pseudocode — retry with cap

```text
function handle_failure(record, err):
  record.attempts += 1
  if is_permanent(err) or record.attempts >= MAX_ATTEMPTS:
    dlq.put(record, err)
    commit_offset(record)
    return
  if not retry_bucket.try_acquire():
    schedule_later(record)  # visibility timeout
    return
  delay = full_jitter(base=2^record.attempts * 100ms, cap=5m)
  retry_queue.schedule(record, delay)
```

### C. Pseudocode — replay job

```text
function run_replay(job):
  capacity = sink.available_tps() * 0.5  # leave headroom for live
  rate = min(job.max_rate, capacity)
  for batch in dlq.read(job.filter, rate_limit=rate):
    for rec in batch:
      if not schema_valid(rec): mark_failed(rec); continue
      sink.merge(rec, key=rec.event_id)
      dlq.mark_replayed(rec)
    job.progress += len(batch)
    if lag_live.pipeline > slo: rate *= 0.5  # yield to live traffic
```

### D. Metrics checklist

```text
pipeline_lag_max_seconds{pipeline,partition}
pipeline_lag_p95_seconds{pipeline}
buffer_depth{stage}
credit_rate_current{edge}
ingress_requests_429_total{pipeline}
retry_queue_depth{pipeline}
dlq_ingress_rate{pipeline}
dlq_age_p95_seconds
degrade_mode{pipeline}
replay_jobs_active
sink_write_errors_total{code}
autoscaler_signals_total{action}
catch_up_eta_seconds
```

### E. Capacity cheat sheet

```text
buffer_records = 2 * peak_rps * stage_p99_sec
retry_max_rps = 0.1 * healthy_rps
catch_up_time ≈ backlog_records / (sink_tps * catch_up_factor - live_produce_rps)
dlq_storage_gb ≈ daily_poison * avg_record_bytes * retention_days / 1e9
controller_shards ≈ num_pipelines / 500
```

### F. Clarifying questions cheat sheet (30 seconds)

1. Streaming vs batch vs micro-batch?  
2. At-least-once OK? Idempotent sink?  
3. Can we pause ingress? Drop anything?  
4. Sink TPS limit and scale path?  
5. Priority tiers and tenant fairness?  
6. DLQ replay approval requirements?

### G. Runbook snippets

```text
Symptom: lag_p95 > 15 min
  1. Check sink_write_p99 and error rate
  2. If sink limited → PAUSE replay jobs; reduce α
  3. If consumer CPU low → not consumer-bound; fix sink
  4. If hot partition → inspect key skew

Symptom: dlq_depth spike
  1. Sample top error_code
  2. Schema break → PAUSE pipeline; fix registry
  3. Transient → fix root cause; replay with max_rate
```

### H. Related Databricks follow-ups

- Structured Streaming `maxOffsetsPerTrigger` as credit actuator  
- Delta merge idempotency for bronze→silver replay  
- DLT (Delta Live Tables) expectation rules vs DLQ  
- Autoscaling cluster on streaming lag metric  

---

*End of pipeline recovery and backpressure HLD prep.*
