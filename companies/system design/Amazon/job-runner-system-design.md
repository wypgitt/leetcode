# System Design: Distributed Job Runner / Task Execution Platform

> **Focus areas:** Schedule · Queues · Workers · Retries · Idempotency · Priorities · DLQ · Leases · Multi-tenant fairness  
> **Style:** Amazon SDE III end-to-end design with progressive scale (10× → 100× → 1,000×)  
> **Amazon themes:** Customer impact by job class · Ownership of work · Operational excellence · Cost-aware elasticity · Cell isolation  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership of work, honest MVP vs extreme-scale paths

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

Goal: **bound “job runner”**—who submits work, delivery semantics, how failures are owned, and at which scale the design must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits jobs? | Internal Amazon services + partner teams; multi-tenant | Everything keyed by `tenant_id` / `account_id`; quotas from day 1 |
| F2 | Job types? | One-shot, delayed, cron/recurring; optional simple chains | Separate *job* (unit of work) from *schedule* (when to enqueue) |
| F3 | Payload size? | Typically <256 KB inline; larger via S3 pointer | Cap inline bytes; store object URI + checksum |
| F4 | Delivery semantics? | **At-least-once** execution; exactly-once *effects* via idempotency | Visibility timeouts / leases + retries; handlers must be idempotent |
| F5 | Retries? | Configurable max attempts, exponential backoff + jitter | Attempt history; poison → DLQ; classify retryable vs fatal |
| F6 | Timeouts / leases? | Worker must heartbeat or extend visibility; expiry → reclaim | Lease ownership is sacred; fencing tokens prevent split-brain |
| F7 | Priorities? | Critical / high / normal / low; optional weighted fair share | Separate queues or score-based dequeue; prevent starvation |
| F8 | Scheduling? | Delayed (`run_at`) + cron with timezone | Schedule materializer → enqueue; jitter midnight storms |
| F9 | Cancellation? | Cancel pending; best-effort cancel running (cooperative) | Cancel flag + lease revoke; worker polls cancel token |
| F10 | Results? | Status API + optional result blob / callback webhook | Durable status; result TTL; webhook at-least-once |
| F11 | Observability? | Per-job timeline, attempts, worker id, latency histograms | Correlate `job_id` / `attempt` / `tenant_id` / `trace_id` |
| F12 | Admin ops? | Pause queue, replay DLQ, redrive, drain tenant, kill switch | Control-plane APIs; audit log; Amazon operational excellence |

**MVP functional scope (lock with interviewer):**

1. Submit **one-shot** and **delayed** jobs with idempotency key.
2. Workers **lease** jobs, heartbeat/extend, complete/fail; lease expiry requeues.
3. Configurable **retries** with exponential backoff + jitter; DLQ after max attempts.
4. **Priorities** (at least 3 levels) with per-tenant rate limits / fair share.
5. Basic **cron schedules** that enqueue jobs (catch-up policy: skip missed or enqueue-once—pick one).
6. APIs: submit, get status, cancel, list attempts, get result; metrics + structured logs.
7. DLQ redrive and tenant pause for ops.

**Out of MVP (explicitly defer):**

- Full DAG workflow engine (mention as Phase 2; keep linear chains only if needed)
- Untrusted user code sandboxes (Lambda-like); start with trusted VPC workers
- Cross-region active-active mutation of the same job
- Exact wall-clock cron with zero drift under partitions
- Perfect exactly-once side effects without client idempotency

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Schedule latency (available → start)? | Near-interactive for critical | p50 < 1s, p99 < 5s in-region (baseline); relax low priority at 1000× |
| N2 | Durability? | No lost accepted jobs | Job durable **before** ACK; RPO ≈ 0 for accepted submits |
| N3 | Delivery? | At-least-once | Duplicate attempts possible; fencing + idempotency keys |
| N4 | Availability? | Control plane 99.9%+; workers elastic | Shed low-priority dequeue first under overload |
| N5 | Multi-tenancy fairness? | Noisy neighbor must not starve others | Shuffle sharding / weighted fair queues / quotas |
| N6 | Multi-region? | DR + optional regional workers | **Single-writer home cell** for job state; workers may be regional |
| N7 | Clock skew? | Don’t trust worker clocks for leases | Server-side lease expiry; opaque lease / fencing tokens |
| N8 | Throughput? | See scale table | Split **submit**, **dequeue**, **heartbeat**, **complete** QPS |
| N9 | Cost? | Elastic with demand | Autoscale workers; cold archive completed jobs |
| N10 | Customer impact? | Critical jobs (payments/fulfillment) vs batch | Separate queues, SLOs, pages by class |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client submits job with idempotency key → durable `PENDING` → worker leases → `RUNNING` → completes → `SUCCEEDED` (+ optional result).
2. Delayed job: `run_at=T+30m` → not visible until T → leased normally.
3. Cron: schedule fires → enqueue job (or skip if prior still running, per policy).
4. Retryable failure → backoff → new attempt with new lease → success.
5. Cancel pending → never runs; cancel running → worker sees cancel, stops cooperatively.
6. Poison job exhausts attempts → `DEAD` / DLQ → operator redrives after fix.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate submit (same idempotency key) | Return original `job_id`; do not create second job |
| Worker dies mid-run | Lease expires → job requeued (attempt++); fencing invalidates late complete |
| Slow worker / GC pause | Missed heartbeats → lease stolen; late complete rejected |
| Two workers claim same job | Impossible if lease CAS correct; if bug → fencing token wins |
| Poison message (always crashes) | Max attempts → DLQ; alert; manual redrive |
| Tenant floods critical queue | Quotas + fair-share; priority ≠ unlimited capacity |
| Cancel races complete | Terminal state via compare-and-set; first writer wins |
| Clock jump on worker | Irrelevant for lease truth; server owns expiry |
| Callback webhook fails | Retry webhook separately; do not re-run job body |
| Partial result write | Result store uses same fencing token; orphaned blobs GC’d |
| Control-plane failover | Fenced old primary; in-flight leases may expire and reclaim |
| Midnight cron storm | Jitter materialization; shard schedules; pre-spread `next_run_at` |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants / accounts | 1K | 10K | 100K | 1M |
| Jobs submitted / day | 10M | 100M | 1B | 10B |
| Peak **submit** QPS | ~500 | ~5K | ~50K | ~500K |
| Peak **dequeue/lease** QPS | ~500 | ~5K | ~50K | ~500K |
| Peak **heartbeat** QPS | ~2K | ~20K | ~200K | ~2M |
| Peak **complete/fail** QPS | ~500 | ~5K | ~50K | ~500K |
| Concurrent running jobs | 50K | 500K | 5M | 50M |
| Avg job duration | 30s | 30s | 20–60s | 20–60s |
| Cron schedules (active) | 100K | 1M | 10M | 100M |
| Delayed jobs waiting | 1M | 10M | 100M | 1B |
| Workers (fleet) | 1K | 10K | 100K | 1M |
| DLQ volume / day | 1K | 10K | 100K | 1M |

**What each jump forces:**

- **10×:** Queue sharding; separate heartbeat path; Redis/Dynamo hybrid for leases; priority queues isolated.
- **100×:** Tenant cells / shuffle shards; delayed-job time-index partitions; cron materializers as a fleet; heartbeat aggregation.
- **1,000×:** Hierarchical schedulers (global → shard → local); per-tenant isolation; regional worker pools against home-cell control plane; cold archival; DLQ partitioned by tenant/class.

### 1.5 Etc. (Constraints & Assumptions)

- **We build the control plane + worker protocol**, not every job’s business logic.
- Workers are **trusted compute** in VPC (or sandboxed runners Phase 2).
- **Single primary cloud (AWS)**, multi-AZ; multi-region with **home cell** for job metadata.
- Job payloads may contain PII → encrypt at rest; scrub logs; IAM least privilege to result buckets.
- “Exactly-once” means **exactly-once business effect** via idempotent handlers, not “run body once in the universe.”
- Amazon ownership: on-call owns **customer impact by job class**, not just “queue lag green.”

**Scope statement:**

> Design a multi-tenant distributed job runner supporting one-shot, delayed, and cron jobs with lease-based execution, at-least-once delivery, retries/DLQ, priorities and fairness—starting at ~10M jobs/day and evolving through 10× / 100× / 1,000× with sharded queues and home-cell single-writer state.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split write classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Submit / enqueue | 500 QPS | 500K QPS | Durable write + idempotency lookup |
| Lease / dequeue | 500 QPS | 500K QPS | CAS / conditional update hot path |
| Heartbeat / extend | 2K QPS | 2M QPS | Dominates at scale; must be cheap |
| Complete / fail | 500 QPS | 500K QPS | Terminal transition + optional result |
| Cron materialize | ~50 QPS avg | ~50K QPS | Spiky at minute boundaries |
| Status reads | 2K QPS | 2M QPS | Cacheable; eventually consistent OK |

### 2.2 Concurrent work & worker math

```text
Concurrent running ≈ submit_rate × avg_duration
Baseline: 500 jobs/s × 30s = 15,000  → design for 50K headroom (spikes, retries)
1,000×:   500K/s × 30s = 15M        → design for ~50M with long-tail jobs

Heartbeats: if lease=30s and heartbeat every 10s:
  heartbeat_QPS ≈ concurrent_running / 10
  Baseline: 50K/10 = 5K (order matches table with mix of short jobs)
  At 1,000×: 50M/10 = 5M → MUST aggregate or lengthen lease for low priority
```

**Worker fleet:**

```text
Jobs/s per worker ≈ concurrency_per_worker / avg_duration
If 10 concurrent slots/worker, 30s jobs → ~0.33 jobs/s/worker
Baseline 500 jobs/s → ~1,500 workers busy + idle buffer → ~2–3K fleet practical
Autoscale on queue depth + lease age p99, not CPU alone
```

### 2.3 Storage

| Store | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Active job metadata | ~50M rows hot (pending+running+recent) | ~50B historical; hot slice sharded | Keep hot window (e.g. 7–30d) in primary store |
| Completed archive | 10M/day × 2 KB ≈ 20 GB/day | 20 TB/day | S3/Glacier; query via Athena/Spark |
| Delayed index | 1M waiting × 200 B ≈ 200 MB | 200 GB | Time-bucket partitions |
| Cron schedules | 100K × 1 KB ≈ 100 MB | 100 GB | Sharded by schedule_id |
| Result blobs | optional; 10–100 KB avg | Object store only | Never in queue body at scale |
| Idempotency keys | TTL 24–72h | Partitioned by tenant hash | DynamoDB / Redis+DB |

Rough metadata size per job: **0.5–2 KB** (ids, state, attempts, pointers).  
Baseline 10M jobs/day × 1 KB = **~10 GB/day** metadata growth before compaction/archive.

### 2.4 Bandwidth

| Path | Baseline | Notes |
|------|----------|-------|
| Submit payload | 500 × 10 KB ≈ 5 MB/s | Mostly small; large → S3 |
| Worker fetch payload | similar | Cache hot templates/config separately |
| Heartbeat | 2K × 200 B ≈ 0.4 MB/s | Tiny; count of RPCs hurts more than bytes |
| Result upload | lower QPS, larger bodies | Direct to S3 with job-scoped credentials |

At 1,000×, **RPC rate** (heartbeats) is the bottleneck long before raw bandwidth.

### 2.5 Memory (hot structures)

| Structure | Purpose | Scale note |
|-----------|---------|------------|
| Per-shard ready queues | Priority heaps / FIFO shards | Keep in memory of queue brokers or Redis |
| Lease table | job_id → fencing, expiry, worker | Hot; must fit shard working set |
| Idempotency cache | recent keys | LRU + durable store |
| Cron next-fire index | schedule → next_run_at | Partitioned; not one giant heap |
| Fairness tokens | tenant credits / weights | Local to dequeue scheduler |

### 2.6 Critical bottlenecks (rank ordered)

1. **Heartbeat / lease extend QPS** — dominates; redesign first at 100×+.
2. **Lease CAS contention** on hot shards — shard by `job_id` / queue partition.
3. **Idempotency lookup** on submit — keyed store with TTL; avoid global lock.
4. **Cron materialization spikes** — jitter + precompute windows.
5. **DLQ / poison amplification** — separate worker pools; circuit break bad handlers.
6. **Status read storms** after fan-out submits — cache + eventual consistency.
7. **Cross-tenant noisy neighbor** — fair dequeue + quotas before bigger boxes.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| **Tenant / Account** | Isolation + quota boundary |
| **Job** | Unit of work with payload pointer, state, attempts |
| **Attempt** | One leased execution; has fencing token |
| **Queue / Topic** | Logical lane by priority × class (critical/batch) |
| **Schedule** | Cron or delayed rule that enqueues jobs |
| **Lease** | Time-bounded ownership of an attempt |
| **DLQ** | Dead-letter lane after max attempts or fatal error |
| **Worker** | Process that leases and executes handlers |
| **Idempotency key** | Client-supplied dedupe for submit |
| **Result** | Optional output blob + status |

**Job state machine (simplified):**

```text
PENDING → LEASED/RUNNING → SUCCEEDED
                ↓
             FAILED_RETRYABLE → (backoff) → PENDING
                ↓
             FAILED_FATAL / DEAD (DLQ)
PENDING → CANCELLED
RUNNING → CANCELLED (cooperative)
```

### 3.2 Options: where is the queue?

| Option | Pros | Cons | When |
|--------|------|------|------|
| **SQS / managed queue** | Ops-light, visibility timeout, DLQ native | Weaker fair-share; less DAG-friendly | MVP / many Amazon teams |
| **DynamoDB as queue** | Strong conditional writes; TTL | Hot partitions; scan cost | Lease-centric control plane |
| **Kafka / Kinesis** | High throughput log | Harder lease/reclaim semantics | Event fan-out, not classic job lease |
| **Custom broker + DB** | Full control of priorities/fairness | You own the pain | 100×+ multi-tenant fairness |

**Recommendation (Amazon interview):** Start with **durable job store (DynamoDB/Aurora) + SQS for wake-ups**, or SQS as primary queue with job metadata in DynamoDB. At 100× fairness needs, add **sharded fair schedulers** in front of workers.

### 3.3 Lease & fencing (resolve ownership)

Invariant: **at most one valid owner** for a running attempt.

```text
Lease record:
  job_id, attempt, fencing_token (monotonic), worker_id,
  lease_expires_at (server time), heartbeat_at

Acquire: conditional update WHERE state=PENDING AND (no lease OR lease expired)
Heartbeat: conditional update WHERE fencing_token=T AND worker_id=W AND expiry>now → extend
Complete: conditional update WHERE fencing_token=T → SUCCEEDED
Late complete with stale T → reject (409)
```

Visibility-timeout (SQS-style) is a lease with fewer heartbeats; long jobs **must** extend.

### 3.4 Exactly-once vs at-least-once

| Layer | Promise |
|-------|---------|
| Submit API | Idempotent create via `(tenant, idempotency_key)` |
| Execution | **At-least-once** attempts |
| Side effects | Caller handler uses **business idempotency key** (often job_id + attempt or client key) |
| Results / webhooks | At-least-once delivery; consumers dedupe |

Say aloud: *“We won’t claim exactly-once runs; we make duplicates safe.”*

### 3.5 Priorities & fairness

- **Priority lanes:** `CRITICAL`, `HIGH`, `NORMAL`, `LOW` — separate queues or weighted pop.
- **Fairness:** deficit round-robin / weighted fair queuing per tenant within a lane.
- **Quotas:** submit QPS, concurrent running, payload bytes/day.
- **Starvation control:** reserve % of worker slots for lower priorities; aging boost.

Priority ≠ skip the line forever: a LOW job from a well-behaved tenant should still make progress.

### 3.6 Delayed jobs & cron

**Delayed:** store in time-index (`run_at` buckets). Sweepers promote to ready queue when due.  
**Cron:** schedule row with `next_run_at`; materializers compute next fires with timezone + jitter.

Catch-up policy (pick one, document):

1. **Skip missed** — good for periodic snapshots.  
2. **Enqueue once for missed window** — good for billing ticks.  
3. **Enqueue all missed** — usually wrong (thundering herd).

### 3.7 Retries, backoff, DLQ

```text
backoff = min(max_backoff, base * 2^attempt) + random_jitter
retryable: timeouts, 429/503 from deps, explicit RetryableException
fatal: validation errors, 4xx business, unauthorized handler
after max_attempts OR fatal → DLQ (DEAD) + metric + optional ticket
```

DLQ is a **first-class product surface**: redrive, quarantine, sample payloads (redacted), owner routing.

### 3.8 Multi-region clarity

| Mode | Behavior |
|------|----------|
| **Active-passive DR** | Home region owns writes; standby replicates metadata |
| **Regional workers** | Workers in many regions; lease against home cell |
| **Cell architecture** | Tenants pinned to cells; no cross-cell job mutation |

Avoid dual-active writers for the same `job_id`.

### 3.9 Callbacks & results

- Result written to S3 under `s3://results/{tenant}/{job_id}` with fencing metadata in DynamoDB.
- Webhooks: separate delivery system (at-least-once, signed, retries, DLQ of their own).
- Do not block worker slot on slow customer webhook—async.

### 3.10 Trade-off tables

| Concern | Choice | Why |
|---------|--------|-----|
| Queue | SQS + metadata DB | Fast MVP; Amazon-native; DLQ built-in |
| Lease truth | DB conditional writes | Clear fencing |
| Heartbeats | Dedicated path / longer leases for batch | Protect control plane |
| Archive | S3 + lifecycle | Cost at 1000× |
| Fairness | Sharded WFQ at 100× | SQS alone insufficient |
| Cron | Materializer fleet | Avoid single scheduler SPOF |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                    +------------------+
  Clients/Services  |  API Gateway /   |
  ----------------->|  Job Runner API  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
     +----------------+            +----------------+
     | Idempotency +  |            | Schedule / Cron|
     | Job Metadata   |            | Materializer   |
     | (Dynamo/Aurora)|            +--------+-------+
     +--------+-------+                     |
              |                             | enqueue due jobs
              v                             v
     +------------------------------------------+
     |     Ready Queues (by priority × shard)   |
     |   CRITICAL | HIGH | NORMAL | LOW | DLQ   |
     +--------------------+---------------------+
                          |
                          | lease / visibility
                          v
                 +------------------+
                 |  Worker Fleet    |
                 |  (ASG / Karpenter)|
                 +--------+---------+
                          |
            +-------------+-------------+
            |             |             |
            v             v             v
       Handlers      Result Store   Webhook Bus
       (business)       (S3)        (async)
```

### 4.2 Sequence: lease → heartbeat → complete

```text
Worker                Queue/Lease Svc           Metadata DB
  |                         |                        |
  |-- Lease(queue) -------->|                        |
  |                         |-- CAS acquire -------->|
  |                         |<-- job + fence T ------|
  |<-- job, T, lease_ms ----|                        |
  |                         |                        |
  |-- Heartbeat(T) -------->|-- CAS extend --------->|
  |<-- OK ------------------|<-----------------------|
  |                         |                        |
  |  (execute handler)      |                        |
  |                         |                        |
  |-- Complete(T, result) ->|-- CAS succeed -------->|
  |                         |-- store result ptr --->|
  |<-- 200 -----------------|                        |
```

### 4.3 Sequence: worker failure / stolen work

```text
Worker A (dead)     Lease Svc / DB              Worker B
  |                      |                         |
  |  (no heartbeat)      |                         |
  |                      |-- lease expired --------|
  |                      |                         |
  |                      |<-- Lease(job) ----------|
  |                      |-- CAS new fence T2 -----|
  |                      |------------------------>| job + T2
  |                      |                         |
  |-- Complete(T1) ----->| reject stale fence      |
  |<-- 409 --------------|                         |
  |                      |<-- Complete(T2) --------|
  |                      |-- SUCCEEDED ------------|
```

### 4.4 Sequence: delayed → ready → DLQ

```text
Submit(run_at=T+1h) → DELAYED index
         |
         v  (sweeper at T)
      READY queue → worker fails retryable → backoff → READY
         |
         +→ max attempts → DLQ → operator redrive → READY
```

### 4.5 Scale cells

```text
                 +---------------- Global Router ----------------+
                 |  tenant_id → cell (consistent hash / table)   |
                 +------+-------------+-------------+------------+
                        |             |             |
                        v             v             v
                     Cell A        Cell B        Cell C
                  (API+DB+Q+     (API+DB+Q+     (API+DB+Q+
                   workers)       workers)       workers)

Noisy tenant pinned/isolated; blast radius = cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Failure modes & mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| API / metadata DB down | Cannot accept jobs | Multi-AZ; cell failover; 503 with retry-after |
| Queue lag | Delayed execution | Autoscale workers; shed LOW first |
| Worker crash | At-least-once redelivery | Lease expiry + fencing |
| Poison job | Worker crash loop | Max attempts → DLQ; per-handler circuit breaker |
| Bad deploy of handler | Mass failures | Canary workers; version pin; kill switch |
| Clock skew | Wrong lease expiry | Server time only; NTP on hosts still for logs |
| Thundering cron | Queue melt | Jitter; shard materializers; admission control |
| DLQ ignored | Silent customer harm | SLO on DLQ age; page owner |
| Duplicate side effects | Double charge / email | Handler idempotency keys |
| Region loss | Control plane down | Home-cell failover runbook; RPO/RTO explicit |

#### 5.1.2 Consistency model

- Submit idempotency: **strong** per home cell for `(tenant, key)`.
- Job state: **monotonic** transitions via conditional writes.
- Status reads: **read-after-write** on primary; replicas OK for dashboards.
- Cross-region: **eventual** for DR replicas; no dual writers.

#### 5.1.3 Exactly-once vs at-least-once

Promises:

1. Accepted jobs are durable and will be attempted until success, cancel, or DLQ.  
2. Duplicates may occur on crash windows.  
3. Fencing prevents *two valid successes* from stale owners.  
4. Business effects require handler-level idempotency.

#### 5.1.4 Amazon ownership themes

- **Customer Impact:** Separate alarms for `CRITICAL` fulfillment jobs vs batch analytics.  
- **Correctness:** Stolen-work double-apply is a Sev-equivalent to data corruption for payments.  
- **Operational excellence:** Runbooks for “lease storm”, “DLQ spike”, “cron herd”, “cell hot partition”.  
- **Frugality:** Don’t keep completed jobs in Dynamo forever; lifecycle to S3.  
- **Bias for action:** Kill switches per tenant/handler without waiting for full deploy.

### 5.2 Scalability

#### 5.2.1 Progressive scale changes

| Scale | Change |
|-------|--------|
| 1× | Single region, SQS + Dynamo, one worker pool per priority |
| 10× | Queue shards; heartbeat service; separate status read path |
| 100× | Cells by tenant; fair schedulers; cron fleet; archive pipeline |
| 1,000× | Hierarchical scheduling; heartbeat aggregation; regional workers; tenant isolation cells |

#### 5.2.2 Sharding keys

| Data | Shard key | Rationale |
|------|-----------|-----------|
| Job metadata | `hash(tenant_id, job_id)` | Even spread; tenant affinity optional |
| Ready queues | `priority + shard_id` | Parallel dequeue |
| Idempotency | `hash(tenant_id, key)` | Localize dedupe |
| Cron | `hash(schedule_id)` | Parallel materialize |
| DLQ | `tenant_id` | Ops ownership |

Avoid sharding only by `tenant_id` if one tenant is huge—use **shuffle shards**.

#### 5.2.3 Heartbeats at 1,000×

Options:

1. Lengthen leases for LOW/batch (trade reclaim latency).  
2. Local lease manager per worker node batching extends.  
3. Hierarchical: worker → node agent → shard service.  
4. Adaptive heartbeat interval based on job class.

#### 5.2.4 Multi-tenant fairness

- Admission control on submit.  
- Concurrent running caps per tenant.  
- Weighted fair dequeue inside each priority.  
- Bad tenant → automatic throttle + optional dedicated isolation pool.

### 5.3 Maintainability

#### 5.3.1 Configuration as data

Retry policies, timeouts, concurrency, cron catch-up, webhook URLs—versioned config, not code deploys for every tweak.

#### 5.3.2 Handler lifecycle

- Handlers registered with version; jobs pin `handler@version` or `latest` policy.  
- Canary % of leases to new version.  
- Rollback = traffic shift, not schema nightmare.

#### 5.3.3 Observability (must-have metrics)

| Metric | Why |
|--------|-----|
| Submit success / idempotent hit rate | API health |
| Queue depth & age p50/p99 by priority | Customer latency |
| Lease steal rate | Worker health / lease too short |
| Attempt count histogram | Poison / dependency issues |
| DLQ count & age | Ops backlog |
| Per-tenant fair-share denial | Noisy neighbor |
| Handler error rate by version | Bad deploy |
| Complete latency vs enqueue latency | SLO burn |

Traces: `trace_id` from submit through attempts. Logs: never payload secrets.

#### 5.3.4 Testing & game days

- Lease expiry / fencing tests.  
- Duplicate submit tests.  
- Cron storm simulation.  
- Cell eviction / failover game day.  
- Poison message + DLQ redrive drill.

#### 5.3.5 Security & compliance

- IAM roles per worker task family.  
- Encrypt payloads at rest (KMS).  
- Tenant isolation in result bucket prefixes.  
- Audit: who redrove DLQ, who paused tenant.  
- PII scrubbing in debug tools.

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× MVP:** API + Dynamo job table + SQS queues (priority) + workers + DLQ + basic cron table + CloudWatch.  

**10×:** Add shard attribute to queues; move status reads to cache; isolate heartbeats; add fair-share v1 (token buckets).  

**100×:** Cell router; per-cell data plane; delayed job partitions; materializer autoscaling; archive completed jobs nightly; shuffle sharding for whales.  

**1,000×:** Global admission; per-tenant isolation cells for top N; heartbeat aggregation; regional execution with home metadata; hierarchical queue brokers; SLO-based load shedding.

### 5.5 Stolen work & idempotency patterns (handlers)

Patterns to say in interview:

1. **Upsert by natural key** — `PUT /orders/{id}` style.  
2. **Idempotency store** — record `(key) → response` before side effect commit.  
3. **Outbox** — handler writes intent; async publisher.  
4. **Fencing on downstream** — pass fencing token to storage conditional write.

### 5.6 DLQ design

DLQ message contains: job_id, last error class, attempt history pointer, payload pointer, tenant owner, first/last failure times.  
Redrive resets attempt counter **or** continues—policy flag.  
Never auto-delete poison without retention for forensics.

### 5.7 Multi-region failure story

1. Home region A degraded → DNS/cell router fails over to B (warm standby).  
2. In-flight leases in A expire; workers in B reclaim.  
3. At-least-once duplicates possible across failover—handlers must tolerate.  
4. Cron materializers leader-elected per cell.

### 5.8 Deal-breaker gallery (quick reference)

| Deal-breaker | Fix |
|--------------|-----|
| No fencing → double complete | Monotonic fencing tokens |
| Heartbeat on same path as submit | Split services |
| Single global cron thread | Sharded materializers |
| Priority without fairness | WFQ + quotas |
| Infinite retries | Max attempts + DLQ |
| Payload in hot DB forever | S3 pointers + archive |
| Status polling stampedes | Cache / push events |
| Dual-active multi-region writes | Home cell single writer |

---

## 6. Wrap-Up

### 6.1 Key decisions

1. At-least-once execution + idempotent handlers; durable before ACK.  
2. Lease + fencing as the ownership primitive.  
3. Priority queues with tenant fair-share and quotas.  
4. First-class DLQ with redrive and ownership.  
5. Cell architecture for blast-radius and scale.  
6. Heartbeat path designed as its own scalability problem.  
7. Cron/delayed via materializers and time indexes, not worker sleep.

### 6.2 Top risks

| Risk | Mitigation |
|------|------------|
| Duplicate side effects | Handler idempotency standards + review |
| Heartbeat melt | Aggregation / lease classes |
| Noisy neighbor | Quotas + shuffle shards + isolation |
| DLQ neglect | Age SLO + paging |
| Cron storms | Jitter + admission |
| Hot partitions | Better shard keys; split tenants |

### 6.3 45-minute interview plan

| Minutes | Focus |
|---------|-------|
| 0–5 | Clarify FR/NFR, at-least-once, priorities, DLQ |
| 5–10 | Estimation: split QPS; heartbeat dominance |
| 10–20 | HLD: API, metadata, queues, workers, DLQ |
| 20–30 | Deep dive: leases/fencing, retries, fairness |
| 30–40 | Scale 100×/1000× cells; failure stories |
| 40–45 | Wrap: SLOs, ops, risks |

### 6.4 60-second pitch

> “I’d build a multi-tenant job runner where submits are durably recorded with idempotency keys, workers lease work with fencing tokens, and failures retry with backoff into a DLQ. Priorities are separate lanes with fair-share so one tenant can’t starve others. Heartbeats are a first-class load path. We scale via queue shards and tenant cells, keep a single-writer home cell for job state, and measure customer impact by job class—not just queue depth.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Semantics & correctness

1. Why is exactly-once execution across processes unrealistic?  
2. How do fencing tokens prevent split-brain completes?  
3. What is the difference between job idempotency and handler idempotency?  
4. How do you make a non-idempotent email send safer under retries?  
5. When is at-most-once acceptable for jobs?  
6. How do you ensure monotonic job state transitions?  
7. What happens if complete and cancel race?  
8. How do you dedupe webhook deliveries?

### 7.2 Leases, heartbeats, theft

9. Visibility timeout vs explicit lease + heartbeat—trade-offs?  
10. How long should a lease be relative to p99 job duration?  
11. What metrics indicate leases are too short? Too long?  
12. How do you reclaim work safely after GC pauses?  
13. Design heartbeat aggregation for 2M QPS.  
14. Should workers trust local clocks for expiry?  
15. How do you fence S3 result writes from stale workers?  
16. What if the lease service itself is partitioned?

### 7.3 Queues & priorities

17. Separate queues vs one queue with priority scores?  
18. How do you prevent LOW starvation?  
19. Implement weighted fair queuing across tenants.  
20. When does SQS become insufficient?  
21. How do you shard queues without reordering guarantees breaking callers?  
22. Dead-letter vs retry topic—what belongs where?  
23. How do poison messages affect shared worker pools?

### 7.4 Delayed & cron

24. Data structure for millions of delayed jobs?  
25. How do you avoid midnight UTC thundering herds?  
26. Catch-up policies: skip vs enqueue-once vs all?  
27. Timezone and DST edge cases for cron?  
28. How do materializers elect leaders / shard work?  
29. What if `next_run_at` update fails after enqueue (duplicate fires)?  
30. How do delayed jobs interact with priority?

### 7.5 Retries & DLQ

31. Exponential backoff with jitter—why jitter?  
32. Which errors are retryable vs fatal?  
33. Should attempt count increment on lease steal?  
34. DLQ retention and PII concerns?  
35. Redrive semantics: reset attempts or continue?  
36. How do you auto-pause a handler on error spike?  
37. Partial batch failure handling?

### 7.6 Multi-tenant & 1000×

38. Shuffle sharding explained with an example.  
39. How do you isolate a whale tenant?  
40. Admission control vs backpressure vs load shedding.  
41. Cell migration for a tenant—steps and risks.  
42. How do quotas interact with CRITICAL priority?  
43. Estimate heartbeat QPS at 50M concurrent jobs.  
44. Hierarchical schedulers—what state lives where?

### 7.7 Multi-region

45. Why home-cell single-writer for job metadata?  
46. Regional workers with remote leases—latency impact?  
47. RPO/RTO for active-passive DR.  
48. Split-brain across regions—how prevented?  
49. Should cron fire in every region or only home?

### 7.8 Observability & ops

50. Define SLOs for a job runner (availability vs latency vs freshness).  
51. Which dashboard page separates customer impact classes?  
52. How do you trace a job across retries?  
53. Game-day scenarios you’d run quarterly.  
54. What alerts page a human at 3am vs ticket?

### 7.9 Security

55. How do workers get least-privilege access to payloads?  
56. Multi-tenant result bucket isolation.  
57. Abuse: tenant submits infinite heavy jobs—controls?  
58. Audit requirements for DLQ redrive.  
59. Encrypting job payloads with per-tenant KMS keys.

### 7.10 Algorithms & data structures

60. Time-wheel vs bucketed time index for delayed jobs.  
61. Consistent hashing for cell assignment.  
62. Deficit round-robin for fairness.  
63. CAS loops and contention backoff.  
64. Approximate queue age without scanning.

### 7.11 Reliability drills

65. Simulate worker death mid-handler—expected outcomes?  
66. Simulate duplicate submit storm.  
67. Simulate dependency 503 for one handler type.  
68. Simulate cell DB hotspot.  
69. Simulate clock jump on 10% of workers.

### 7.12 Comparison questions

70. Job runner vs SQS alone—what do you still build?  
71. Job runner vs Step Functions / workflow engine?  
72. Job runner vs Kafka consumer groups?  
73. Job runner vs cron on every box (legacy)?  
74. Compared to AWS Batch / ECS scheduled tasks?

### 7.13 Amazon leadership / ownership

75. Critical payment jobs delayed—what do you do first?  
76. How do you define ownership between platform team and handler owners?  
77. A tenant burns DLQ—product vs engineering response?  
78. Cost regression after 10× traffic—how investigate?  
79. Why might “queue depth OK” still be a customer Sev?

### 7.14 Interview traps

80. Lumping all QPS into one number.  
81. Claiming exactly-once without defining effects.  
82. Ignoring heartbeats in capacity planning.  
83. Priority without anti-starvation.  
84. Single global scheduler thread.  
85. Storing huge payloads inline forever.

---

## 8. Appendices

### 8.1 Schema sketches

```text
Job {
  job_id, tenant_id, idempotency_key,
  queue_class, priority,
  state, attempt, max_attempts,
  payload_inline?, payload_s3?,
  run_at, created_at, updated_at,
  handler_name, handler_version,
  last_error_class, dlq_at?,
  result_s3?, callback_url?
}

Attempt {
  job_id, attempt_n, fencing_token,
  worker_id, leased_at, lease_expires_at,
  heartbeat_at, finished_at, status, error?
}

Schedule {
  schedule_id, tenant_id, cron_expr, timezone,
  next_run_at, catch_up_policy, handler_name,
  enabled, jitter_seconds
}

IdempotencyRecord {
  tenant_id, key, job_id, status_code, body_hash, expires_at
}
```

### 8.2 API checklist

| API | Notes |
|-----|-------|
| `POST /v1/jobs` | Idempotency-Key header |
| `GET /v1/jobs/{id}` | Status + attempts summary |
| `POST /v1/jobs/{id}/cancel` | Conditional |
| `GET /v1/jobs/{id}/attempts` | Debug |
| `GET /v1/jobs/{id}/result` | Presigned GET |
| `POST /v1/schedules` | Cron create |
| `POST /v1/dlq/{id}/redrive` | Admin + audit |
| `POST /v1/tenants/{id}/pause` | Ops |

### 8.3 Glossary

| Term | Definition |
|------|------------|
| Lease | Time-bounded exclusive ownership of an attempt |
| Fencing token | Monotonic id invalidating stale owners |
| DLQ | Dead-letter queue for exhausted/fatal jobs |
| Materializer | Component that turns schedules into jobs |
| Cell | Isolated blast-radius unit (data + compute) |
| Shuffle shard | Tenant maps to multiple random shards for isolation |
| Fair share | Algorithm ensuring tenants get proportional service |
| Visibility timeout | SQS-style lease without explicit heartbeats |

### 8.4 Progressive scale checklist

- [ ] Split QPS classes in estimation  
- [ ] Heartbeat plan at 100×+  
- [ ] DLQ + redrive + owner  
- [ ] Priority + fairness  
- [ ] Cron jitter  
- [ ] Cell story  
- [ ] Handler idempotency standard  
- [ ] Archive / cost story  
- [ ] Multi-region home cell  
- [ ] Customer-impact SLOs by class  

### 8.5 Worker protocol sketch

```text
loop:
  job = Lease(queue, worker_id)
  if job is null: idle backoff; continue
  cancel_watch = start_cancel_poller(job.id, job.fence)
  try:
    while not done:
      extend_lease(job.id, job.fence)
      progress = handler.run(job, cancel_watch)
    Complete(job.id, job.fence, result)
  except Retryable as e:
    Fail(job.id, job.fence, retryable=True, error=e)
  except Fatal as e:
    Fail(job.id, job.fence, retryable=False, error=e)
```

### 8.6 Priority + fairness interaction

```text
Worker slot free:
  1) Pop CRITICAL if tenant under concurrent cap
  2) Else HIGH with WFQ among tenants
  3) Else NORMAL / LOW with reserved floor percentages
Aging: LOW waiting > threshold gets temporary boost
```

### 8.7 Delayed job storage design

```text
Buckets: delayed/{yyyyMMddHH}/{shard}/job_id
Sweeper: for each due bucket, promote to ready (conditional state DELAYED→PENDING)
Promotion must be idempotent (conditional update)
```

### 8.8 Interview “say this” summary (60 seconds)

> Durable submit with idempotency, lease+fence workers, at-least-once with DLQ, priorities with fair-share, cells for scale, heartbeats as their own problem, cron via materializers—customer impact by job class.

### 8.9 Extra traps

| Trap | Reality |
|------|---------|
| “Redis list is enough” | Loses durable lease semantics under failure unless carefully designed |
| “Exactly-once queue” | Brokers don’t make your side effects exactly-once |
| “Global fair queue” | Doesn’t scale; shard fairness |
| “Workers sleep until run_at” | Doesn’t survive deploys; use delayed index |

### 8.10 Reliability test plan

1. Kill 10% workers during peak—no lost jobs; steal rate temporary bump.  
2. Double-complete with stale fence—rejected.  
3. Idempotent submit replay—same job_id.  
4. Cron storm—admission holds latency SLO for CRITICAL.  
5. DLQ redrive after handler fix—success.  
6. Region failover game day—documented RTO.

### 8.11 Observability SLOs

| SLO | Target (baseline) |
|-----|-------------------|
| Submit availability | 99.9% |
| CRITICAL time-to-start p99 | < 5s |
| NORMAL time-to-start p99 | < 30s |
| No lost accepted jobs | 100% (RPO 0) |
| DLQ age p99 | < 24h for owned queues |
| Poison rate | < 0.01% jobs |

### 8.12 Related systems map

| System | Relation |
|--------|----------|
| SQS / SNS | Transport / wake-up |
| Step Functions | Workflow layer above jobs |
| EventBridge Scheduler | Cron alternative |
| Lambda | Sandbox worker option |
| Amazon SQS DLQ | Pattern inspiration |
| Amazon SWF (legacy) | Historical lessons on leases |

### 8.13 Pseudocode: submit idempotency

```text
function Submit(tenant, key, jobSpec):
  existing = Idempotency.Get(tenant, key)
  if existing: return existing.response
  job = Job.CreatePending(jobSpec)  // durable
  if jobSpec.run_at > now:
    DelayedIndex.Add(job)
  else:
    ReadyQueue.Enqueue(job)
  Idempotency.Put(tenant, key, job.id)
  return job.id
```

### 8.14 Pseudocode: lease acquire

```text
function Lease(queue, worker):
  job = ReadyQueue.Receive(queue)  // visibility/lease started
  token = Metadata.CasAcquire(job.id, worker, lease_ms)
  if not token:
    // lost race or already terminal
    return null
  return {job, fence: token}
```

### 8.15 Operator runbooks (titles)

- CRITICAL queue age breach  
- Lease steal rate spike  
- DLQ spike for handler X  
- Cron materializer lag  
- Cell hot partition  
- Tenant throttle storm  
- Failover to DR region  

### 8.16 Final trap table

| If interviewer hears… | Correct to… |
|-----------------------|-------------|
| “Exactly-once jobs” | “At-least-once runs; exactly-once effects via idempotency” |
| “We’ll poll DB every ms” | “Wake queues + sharded sweepers” |
| “One Redis queue” | “Shards + metadata + fencing” |
| “Priority fixes fairness” | “Priority + WFQ + quotas” |
| “Multi-region active-active” | “Home cell single-writer” |

### 8.17 Amazon bar reminders

- Write down customer impact classes early.  
- Quantify heartbeats.  
- Own DLQ, don’t orphan it.  
- Talk cells and blast radius.  
- End with risks and kill switches.

---

*End of document — Distributed Job Runner / Task Execution Platform (Amazon SDE III)*
