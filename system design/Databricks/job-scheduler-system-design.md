Distributed Job Scheduler

> **Focus areas:** DAG/workflows · Leases/heartbeats · Retries · Priorities · Worker failure · Cron/delayed jobs · Multi-tenant fairness
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:**
> **Interview theme:** Databricks — general-purpose distributed scheduler; classic HLD with lease/fencing depth Correct arithmetic, explicit invariants, resolved ownership of work, honest MVP vs extreme-scale paths

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

Goal: **bound the product**—what “scheduler” means (single jobs vs workflows), delivery semantics, and at which scale the design must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits jobs? | Internal services + product teams; multi-tenant SaaS | Everything keyed by `tenant_id` from day 1; quotas + shuffle sharding |
| F2 | Job types? | One-shot tasks, delayed, cron/recurring, and **DAG workflows** (fan-out/fan-in) | Separate *job* (unit of work) from *workflow* (orchestration graph) |
| F3 | Payload size? | Typically <256 KB inline; larger via object storage pointer | Cap inline bytes; store blob URI + checksum |
| F4 | Delivery semantics? | **At-least-once** execution; exactly-once *effects* via idempotency | Leases + retries; client must be idempotent; optional dedupe window |
| F5 | Retries? | Configurable max attempts, backoff, retryable error classes | Attempt history; poison → DLQ; distinguish user fail vs infra fail |
| F6 | Timeouts / leases? | Worker must heartbeat; lease expiry → reclaim | Lease ownership is sacred; fencing tokens prevent split-brain work |
| F7 | Priorities? | High / normal / low; optional weighted fair share per tenant | Separate queues or score-based dequeue; avoid starvation |
| F8 | Dependencies? | Workflow steps wait on parents; join on all/any | Workflow engine + state machine; not ad-hoc polling in workers |
| F9 | Cancellation? | Cancel pending; best-effort cancel running (cooperative) | Cancel flag + lease revoke; running worker checks cancel token |
| F10 | Cron / schedules? | Cron expressions, timezone-aware, catch-up policy | Schedule → materialize next run(s); avoid thundering herd at `:00` |
| F11 | Observability? | Per-job timeline, attempts, worker id, latency histograms | Structured events; correlate `workflow_id` / `job_id` / `attempt` |
| F12 | Admin ops? | Pause queue, replay DLQ, redrive, drain tenant | Control plane APIs; audit log |

**MVP functional scope (lock with interviewer):**

1. Submit **one-shot** and **delayed** jobs with idempotency key.
2. Workers **lease** jobs, heartbeat, complete/fail; lease expiry requeues.
3. Configurable **retries** with exponential backoff + jitter; DLQ after max attempts.
4. **Priorities** (at least 2–3 levels) with per-tenant rate limits.
5. Basic **cron schedules** that enqueue jobs (catch-up: skip or enqueue-missed—pick one).
6. Simple **DAG workflows** (linear + fan-out/fan-in) with step dependencies.
7. APIs: submit, get status, cancel, list attempts; metrics + structured logs.

**Out of MVP (explicitly defer):**

- Distributed map-reduce / shuffle compute
- Cross-region active-active job mutation for the same workflow
- Exact wall-clock cron with zero drift under partitions (document best-effort)
- User-defined plugins running inside the control plane
- Perfect exactly-once side effects without client idempotency

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Schedule latency (available job → start)? | Near-interactive for high priority | p50 < 1s, p99 < 5s in-region (baseline); relax at 1000× for low priority |
| N2 | Durability? | No lost accepted jobs | Job durable **before** ACK; RPO ≈ 0 for accepted submits |
| N3 | Delivery? | At-least-once | Duplicate attempts possible; fencing + idempotency keys |
| N4 | Availability? | Control plane 99.9%+; workers elastic | Degrade low-priority dequeue first |
| N5 | Multi-tenancy fairness? | Noisy neighbor must not starve others | Shuffle sharding / weighted fair queues |
| N6 | Multi-region? | DR + optional regional workers | **Single-writer home cell** for workflow/job state; workers may be regional |
| N7 | Clock skew? | Don’t trust worker clocks for leases | Server-side lease expiry; workers use opaque lease tokens |
| N8 | Throughput? | See scale table | Split **submit QPS**, **dequeue QPS**, **heartbeat QPS**, **complete QPS** |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client submits job with idempotency key → durable `PENDING` → worker leases → `RUNNING` → completes → `SUCCEEDED`.
2. Delayed job: `run_at=T+30m` → not visible until T → leased normally.
3. Cron: schedule fires → enqueue job (or skip if prior still running, per policy).
4. DAG: step A succeeds → unlock B,C → both succeed → unlock join D → workflow `SUCCEEDED`.
5. Retryable failure → backoff → new attempt with new lease → success.
6. Cancel pending → never runs; cancel running → worker sees cancel, stops cooperatively.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate submit (same idempotency key) | Return original `job_id`; do not create second job |
| Worker dies mid-run | Lease expires → job requeued (attempt++); fencing token invalidates late complete |
| Slow worker / GC pause | Missed heartbeats → lease stolen; late complete rejected (`409` / fencing) |
| Two workers claim same job | Impossible if lease CAS is correct; if bug → fencing token wins |
| Poison message (always crashes) | Max attempts → `DEAD` / DLQ; alert; manual redrive |
| Workflow parent fails permanently | Mark dependents `CANCELLED` or `SKIPPED` per policy; workflow `FAILED` |
| Cron storm at midnight UTC | Jitter materialization; shard schedules; pre-spread `next_run_at` |
| Tenant floods high-priority | Quotas + separate fair-share; priority ≠ unlimited capacity |
| Cancel races complete | Terminal state via compare-and-set; first writer wins; loser no-op |
| Clock jump on worker | Irrelevant for lease truth; server owns expiry |
| Partial DAG fan-in | Join waits for required parents; timeout → fail/cancel policy |
| Resume after control-plane failover | Fenced old primary; in-flight leases may expire and reclaim—acceptable at-least-once |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants | 1K | 10K | 100K | 1M |
| Jobs submitted / day | 10M | 100M | 1B | 10B |
| Peak **submit** QPS | ~500 | ~5K | ~50K | ~500K |
| Peak **dequeue/lease** QPS | ~500 | ~5K | ~50K | ~500K |
| Peak **heartbeat** QPS | ~2K | ~20K | ~200K | ~2M |
| Peak **complete/fail** QPS | ~500 | ~5K | ~50K | ~500K |
| Concurrent running jobs | 50K | 500K | 5M | 50M |
| Avg job duration | 30s | 30s | 20–60s | 20–60s |
| Workflows / day | 1M | 10M | 100M | 1B |
| Avg steps / workflow | 5 | 5 | 8 | 10 |
| Cron schedules (active) | 100K | 1M | 10M | 100M |
| Delayed jobs waiting | 1M | 10M | 100M | 1B |
| Workers (fleet) | 1K | 10K | 100K | 1M |

**What each jump forces:**

- **10×:** Queue sharding; Redis/DB hybrid for leases; separate heartbeat path from submit path.
- **100×:** Tenant cells / shuffle shards; workflow state machine service; delayed-job wheel or time-index partitions; cron materializers as a fleet.
- **1,000×:** Hierarchical schedulers (global → shard → local); per-tenant isolation; regional worker pools against home-cell control plane; heartbeat aggregation; cold archival of completed jobs.

### 1.5 Etc. (Constraints & Assumptions)

- **We build the control plane + worker protocol**, not every job’s business logic.
- Workers are **trusted compute** in our VPC (or sandboxed runners Phase 2).
- **Single primary cloud**, multi-AZ; multi-region with **home cell** for job/workflow metadata.
- Job payloads may contain PII → encrypt at rest; scrub logs.
- “Exactly-once” means **exactly-once *business effect*** via idempotent handlers, not “run body once in the universe.”

**Scope statement:**

> Design a multi-tenant distributed job scheduler supporting one-shot, delayed, cron, and DAG workflows with lease-based execution, at-least-once delivery, retries/DLQ, priorities and fairness—starting at ~10M jobs/day and evolving through 10× / 100× / 1,000× with sharded queues and home-cell single-writer state.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split write classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Submit / enqueue | 500 QPS | 500K QPS | Durable write + idempotency lookup |
| Lease / dequeue | 500 QPS | 500K QPS | CAS update hot path |
| Heartbeat | 2K QPS | 2M QPS | Dominates at scale; must be cheap |
| Complete / fail | 500 QPS | 500K QPS | Terminal transition + unlock children |
| Cron tick / materialize | ~50 QPS avg | ~50K QPS | Spiky at minute boundaries |
| Status read API | 1K QPS | 1M QPS | Cache aggressively |

**Critical insight:** At 1,000×, **heartbeats (~2M QPS)** can exceed submit+complete combined. Design heartbeat as a separate, sharded, lossy-but-safe path (batched or lease-extent refresh), not as full row updates in OLTP for every pulse.

### 2.2 Concurrent work & worker math

```text
Baseline: 10M jobs/day ÷ 86400 ≈ 116 jobs/s average
Peak ≈ 4–5× average → ~500 jobs/s (matches table)

Concurrent ≈ arrival_rate × duration
500 jobs/s × 30s ≈ 15,000  → table says 50K peak with burst/longer tails
(Use p99 duration for capacity, not only mean.)

If p99 duration = 120s at peak 500/s:
500 × 120 = 60,000 concurrent → provision workers for that + headroom
```

At **1,000×**:

```text
Peak start rate ~500K/s × 30s mean ≈ 15M concurrent
If each worker runs 10 jobs (threaded/async): need ~1.5M worker-slots
→ auto-scale worker pools; never assume a fixed 1K-node fleet
```

### 2.3 Storage

```text
Job row ~1–2 KB metadata (without large payload)
Baseline retained “active + recent complete” 7 days:
10M/day × 7 × 1.5 KB ≈ 105 GB metadata

1,000×: 10B/day × 7 × 1.5 KB ≈ 105 TB metadata (hot/warm)
Plus payload blobs if inline avoided: object storage separate

Attempt history: ~200–500 B × attempts
If avg 1.2 attempts: +20–40% 

Workflow state: 1B workflows/day × 10 steps × ~500 B ≈ 5 TB/day raw events
→ retain hot 7–30 days; archive to object storage / columnar
```

**Unit check:** 10B jobs/day × 1.5 KB = 15 PB/day would be wrong if we said that for metadata—**15 TB/day**, not PB. 10B × 1.5e3 B = 1.5e13 B = **15 TB/day**. Over 7 days ≈ **105 TB**. Correct.

### 2.4 Bandwidth

```text
Submit payload avg 5 KB (pointer-heavy):
500K QPS × 5 KB ≈ 2.5 GB/s ingress at 1000×  → substantial but fine with LB+region

Heartbeat tiny (~100–200 B):
2M QPS × 150 B ≈ 300 MB/s

Result payloads often stay in object storage; control plane carries pointers.
```

### 2.5 Memory (hot structures)

```text
Ready-queue index in memory (job_id + priority + run_at): ~64–128 B / ready job
1M ready → ~64–128 MB / shard
1B delayed waiting cannot all be in RAM → time-partitioned disk index + “due” window in memory

Lease table: 50M running × 128 B ≈ 6.4 GB cluster-wide (sharded)
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Heartbeat amplification** at high concurrency  
2. **Hot tenant / hot queue partition** (noisy neighbor)  
3. **Cron/delayed materialization storms**  
4. **Workflow join fan-in** thundering (unlock storms)  
5. **Idempotency lookup** under submit storms  
6. **DLQ / poison** blocking a partition if not isolated  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Schedule  → (cron/delay rules) → enqueues Job(s)
Workflow  → graph of Steps; each Step creates/awaits Job(s)
Job       → unit of work; attempts; lease; terminal state
Attempt   → one execution try under a fencing token / lease_id
Worker    → process that leases jobs for queues it can serve
```

**State machine (job):**

```text
PENDING → READY → LEASED/RUNNING → SUCCEEDED
                      ↓
                   FAILED_RETRYABLE → (backoff) → READY
                      ↓
                   FAILED_PERMANENT / DEAD / CANCELLED
```

### 3.2 Options: where is the queue?

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Postgres `SKIP LOCKED` | Simple, transactional, great MVP | Heartbeat/update contention at 100×+ | Heartbeat QPS melts primary |
| B. Redis lists/ZSET + durable log | Fast dequeue | Durability/consistency care; Redis loss risk | Accepting job ACK without disk durability |
| C. Kafka / Pulsar as backlog | Huge throughput, replay | Not a natural delayed/priority scheduler alone | Needing rich per-job lease UX only in Kafka |
| D. Hybrid: durable DB/log + **in-memory scheduler shards** | Best at scale | Operational complexity | Team cannot operate sharded control plane |

**Chosen path:**

- **MVP / baseline:** Postgres (or Cockroach/Spanner-style) for job rows + `FOR UPDATE SKIP LOCKED` dequeue per queue shard; Redis optional for rate limits.  
- **100×+:** Hybrid — **durable job store** + **sharded scheduler brokers** that own ready sets; Kafka for async side-effects (notify, metrics), not as sole source of lease truth.

### 3.3 Lease & fencing (resolve ownership)

**Invariant:** At most one **valid** lease owner at a time for a job attempt; stale owners cannot commit success.

```text
1. Dequeue: CAS job from READY → RUNNING with lease_id=UUID, lease_until=now+L, worker_id, attempt=n
2. Heartbeat: if lease_id matches, extend lease_until
3. Complete: if lease_id matches AND state=RUNNING → SUCCEEDED; else reject
4. Reaper: if now > lease_until AND state=RUNNING → READY (attempt stays or ++ per policy), new lease_id later
```

**Stolen work:** Reaper “steals” by invalidating lease; old worker’s complete fails fencing check. **This is at-least-once**, not exactly-once run.

**Deal-breaker:** Completing without checking `lease_id` / fencing token.

### 3.4 Exactly-once vs at-least-once

| Layer | Guarantee |
|-------|-----------|
| Submit API | Idempotent create via `(tenant_id, idempotency_key)` |
| Execution | **At-least-once** (retries + lease reclaim) |
| Side effects | **Effectively once** if worker handler is idempotent (dedupe key = `job_id` or `idempotency_key`) |

Do **not** claim broker-level exactly-once for arbitrary user code.

### 3.5 Priorities & fairness

| Approach | Use when |
|----------|----------|
| Separate queues (P0/P1/P2) | Simple; risk starvation of P2 |
| Weighted fair queueing per tenant | Multi-tenant SaaS default |
| Shuffle sharding | Noisy tenants; assign each tenant to N random shards |

**Starvation control:** reserve capacity % for low priority; aging boost; tenant tokens.

**Deal-breaker:** Global single FIFO for all tenants at 100×+.

### 3.6 Delayed jobs & cron

**Delayed:** store `run_at`; index `(queue, run_at)` or ZSET per shard; **sweeper** moves due jobs to READY in batches.

**Cron:**

```text
schedules table: cron_expr, timezone, next_run_at, policy (skip|enqueue_missed|catch_up_limited)
materializer workers: claim due schedules with lease → compute next → enqueue job → update next_run_at
```

**Thundering herd mitigation:** spread `next_run_at` with deterministic jitter; shard by `schedule_id`; limit catch-up depth (e.g. max 3 missed).

### 3.7 DAG workflows vs single jobs

**Single job:** one state machine, enough for many products.

**Workflow:**

```text
WorkflowInstance (state: RUNNING|SUCCEEDED|FAILED|CANCELLED)
  StepInstance[] with deps: depends_on[], join_rule=ALL|ANY
  Each runnable step → Job
  On job terminal → workflow engine advances graph
```

**Ownership of advancement:** **Workflow engine** (control plane), not random workers, unlocks children. Workers only complete jobs; they do not directly mutate sibling steps.

**Why:** Prevents lost-updates and dual-advancement under retries.

### 3.8 Retries, backoff, DLQ

```text
backoff = min(cap, base * 2^attempt) + random_jitter
retryable: worker timeout, 5xx from dependency, explicit RetryableError
non-retryable: validation errors, 4xx business reject → FAILED_PERMANENT
max_attempts exceeded → DEAD + DLQ topic/table
```

### 3.9 Multi-region clarity

| Plane | Mode |
|-------|------|
| Worker compute | Regional OK (run near data/deps) |
| Job/workflow metadata writes | **Single-writer home cell** per tenant (or per workflow) |
| Submit API gateways | Active-active globally; forward writes to home cell |
| Reads (status) | Local cache / async replica; read-your-writes via home or sync token |

**Deal-breaker:** Active-active dual writers on the same `job_id` without a conflict story (money-like correctness for leases).

### 3.10 Trade-off tables (memory / cache / queue / DB)

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Durable truth | DB / replicated log | ACK ⇒ durable | Redis-only accept |
| Ready set | Memory per scheduler shard | Low latency dequeue | Full table scan each poll |
| Heartbeats | Sharded lease store / batched extend | Survives 2M QPS | Row update in monolithic PG |
| Payloads | Object storage > threshold | Keep OLTP slim | 10 MB inline JSON in PG |
| Metrics | Async pipeline | Don’t block complete path | Sync ES write on complete |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                    +------------------+
   Clients/Services |  API Gateway     |  (active-active)
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
     +----------------+            +----------------+
     | Submit Service |            | Query Service  |
     | (idempotent)   |            | (status/list)  |
     +--------+-------+            +--------+-------+
              |                             |
              v                             v
     +--------------------------------------+
     |     Job Store (home cell, sharded)   |
     |  jobs | attempts | workflows | cron  |
     +------------------+-------------------+
                        |
         +--------------+------------------+
         |              |                  |
         v              v                  v
 +--------------+ +-----------+   +----------------+
 | Scheduler    | | Workflow  |   | Cron/Delay     |
 | Shards       | | Engine    |   | Materializers  |
 | (ready/lease)| |           |   |                |
 +------+-------+ +-----+-----+   +--------+-------+
        |               |                  |
        |               +--------+---------+
        |                        |
        v                        v
 +----------------------------------------+
 |     Lease / Heartbeat Plane (sharded)  |
 +------------------+---------------------+
                    |
                    v
            +---------------+         +----------+
            | Worker Fleets |-------->| DLQ /    |
            | (regional OK) | complete| Redrive  |
            +---------------+         +----------+
                    |
                    v
            External deps / side effects
            (must be idempotent)
```

### 4.2 Sequence: lease → heartbeat → complete

```text
Worker                Scheduler Shard           Job Store
  |                         |                      |
  |-- Lease(queue, n) ----->|                      |
  |                         |-- CAS READY→RUNNING->|
  |                         |<- job + lease_id ----|
  |<- jobs -----------------|                      |
  |                         |                      |
  |-- Heartbeat(lease_id) ->|                      |
  |                         |-- extend if match -->|
  |<- OK -------------------|                      |
  |                         |                      |
  |-- Complete(lease_id)--->|                      |
  |                         |-- CAS terminal ----->|
  |                         |-- enqueue unlock --->| (workflow engine async)
  |<- ACK -------------------|                      |
```

### 4.3 Sequence: worker failure / stolen work

```text
Worker A (dead)     Reaper              Worker B
     |                 |                    |
  (no heartbeat)       |                    |
     |                 |-- lease expired -->|
     |                 |-- RUNNING→READY -->|
     |                 |                    |
     |                 |      B leases new lease_id2
     |                                     |
  A wakes, Complete(lease_id1) -----> REJECT (fencing)
  B Completes(lease_id2) ----------> SUCCEEDED
```

### 4.4 Sequence: DAG fan-out / fan-in

```text
Submit Workflow W
  Engine: create steps A,B,C,D
  A ready → job A
  A succeeds → unlock B,C (ALL deps of D not met yet)
  B succeeds
  C succeeds → unlock D
  D succeeds → W SUCCEEDED
```

### 4.5 Scale cells

```text
Global Directory: tenant → home cell
Cell Z:
  API slice | Job store shard set | Scheduler shards | Workflow engine
Workers: may pull from Cell Z remotely or run in-region with RPC to Z
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable:** no ACK until job row (or equivalent log record) is persisted/quorum-written.  
2. **Lease fencing:** completes require current `lease_id`.  
3. **Terminal monotonicity:** once `SUCCEEDED`/`DEAD`/`CANCELLED`, no return to `RUNNING` without explicit admin redrive (new attempt identity).  
4. **Idempotent submit:** `(tenant_id, idempotency_key)` unique.  
5. **Workflow single advancer:** step transitions serialized per `workflow_id` (lock, actor, or ordered partition).  
6. **At-least-once visibility:** reclaim after lease expiry will re-run handlers.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Scheduler shard crash | Jobs remain in store; another shard or restart reloads ready set from DB index |
| Split-brain primary | Fencing token / epoch on cell leadership |
| Poison job | Max attempts → DLQ; do not block partition |
| Downstream outage | Retryable fail + backoff; circuit-break tenant optional |
| Clock skew | Server time for leases; NTP still hygiene |

**Cancel vs resume**

- **Cancel:** cooperative; sets `cancel_requested`; worker checks between units of work; force-fail when lease ends if still running.  
- **Resume/redrive:** admin or API creates **new attempt** (or resets to READY) with audit; never silently revive `SUCCEEDED`.

### 5.2 Scalability

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| 1× | Monolithic API + PG `SKIP LOCKED` + worker pool |
| 10× | Queue shards by `hash(tenant_id, queue)`; Redis rate limits; async workflow unlock |
| 100× | Scheduler broker tier; heartbeat plane; shuffle sharding; cron materializer fleet |
| 1000× | Cells; hierarchical scheduling; regional workers; archive completed jobs; batched heartbeats |

**Heartbeat scaling techniques**

- Extend lease less frequently (e.g. every L/3)  
- Batch heartbeats from worker process (many jobs / RPC)  
- Keep lease state in memory on owning scheduler shard + periodic WAL  
- Separate RT store (Redis Cluster) with careful durability story for lease only—not for job accept

**Fairness / noisy tenants**

- Shuffle shard: tenant → 2 random shards of 32; overload isolates  
- Per-tenant concurrent caps + submit tokens  
- Priority queues **inside** tenant fair share  

### 5.3 Maintainability

- Versioned worker protocol (`protocol_version`)  
- Job type registry: `handler_name` → library version; canary workers  
- Dead letter tooling: inspect, redrive, skip  
- Migration: dual-write job store only with explicit cutover checklist  
- Chaos: kill workers, pause heartbeats, partition scheduler shards  

**Observability (must-have)**

- Metrics: submit rate, lease latency, running gauge, claim storms, DLQ depth, cron lag (`now - next_run_at`)  
- Trace: `job_id`, `attempt`, `lease_id`, `workflow_id`, `step_id`  
- Timeline UI: state transitions with timestamps and actor (worker/reaper/admin)

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× — “correct MVP”**

```text
API + Postgres
SUBMIT: INSERT job idempotent
LEASE:  SELECT ... FOR UPDATE SKIP LOCKED WHERE state=READY AND run_at<=now()
HB:     UPDATE lease_until WHERE lease_id=?
COMPLETE: UPDATE state WHERE lease_id=?
Cron: every minute SELECT schedules WHERE next_run_at<=now()
Workers: pull loop
```

Bottleneck you’ll hit first: **SKIP LOCKED contention** + heartbeat updates on popular queues.

**10× — shard queues & async unlock**

- Shard key `hash(tenant_id, queue_name) % N`.  
- Workflow unlock via outbox → consumers (don’t hold TX while unlocking 1k children).  
- Redis token buckets for submit & concurrent running.  
- Ready-set optional cache per shard with DB rebuild.

**100× — scheduler brokers + heartbeat plane**

- Scheduler process owns in-memory ready heaps for its shards; DB is durability + rebuild.  
- Heartbeats never touch the main OLTP primary at raw pulse rate—batch to lease plane.  
- Shuffle sharding for noisy tenants.  
- Cron materializers horizontally scaled; `FOR UPDATE SKIP LOCKED` on schedules.

**1000× — cells + hierarchy**

```text
Global directory: tenant → cell
Cell: local job store + schedulers + workflow engine
Regional worker pools: pull jobs for tenants whose deps are local; else RPC to cell
Archive: SUCCEEDED jobs >30d → object storage; API fetch hydrates
Hierarchical admission: cell admission control → shard → tenant
```

### 5.5 Stolen work & idempotency patterns (handlers)

| Handler pattern | How to be safe under steal |
|-----------------|----------------------------|
| DB upsert by `job_id` | Natural idempotent |
| Emit Kafka message | Use `job_id` as key + producer idempotence |
| Call external HTTP | External idempotency key = `job_id` |
| Send email | Store `email_sent(job_id)` unique before send |
| Charge card | **Never** without payment-style uncertainty protocol |

**Rule:** Control plane guarantees fencing of *completion*; handler guarantees fencing of *effects*.

### 5.6 Workflow engine internals

```text
onJobTerminal(job):
  lock workflow_id  # partition actor or DB lock
  step = step_of(job)
  mark step terminal
  if workflow canceling: skip unlocks; maybe compensate
  else:
    for child in children(step):
      if join_satisfied(child): enqueue child job
    if all_terminal(workflow): mark workflow terminal
  unlock
```

**Concurrency:** one advancer per workflow prevents double-enqueue of children.

**Large fan-out:** `enqueue children` in pages of 500 with continuation tasks.

### 5.7 Multi-region failure story

1. Home cell AZ outage → multi-AZ survives.  
2. Region loss → promote DR cell with new epoch; fence old.  
3. In-flight workers with old epoch leases fail completes; jobs reclaim.  
4. Duplicate side effects possible → handlers idempotent.  
5. Cron materializers in old region must stop (epoch).  

### 5.8 Deal-breaker gallery (quick reference)

| Temptation | Why it fails |
|------------|--------------|
| ACK before disk | Lost jobs under crash |
| Complete without lease_id | Split-brain success |
| Workers mutate DAG freely | Duplicate children |
| Single global queue | Noisy neighbor + HOL |
| Redis as only SoT | Durability/compliance issues |
| Active-active job writers | Conflicting state |
| Sync ES index on complete | Tail latency melt |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Semantics | At-least-once execution + idempotent effects |
| Ownership | Lease + fencing token; reaper steals on expiry |
| Orchestration | Workflow engine advances DAG (not workers) |
| Queue | PG MVP → sharded scheduler hybrid at scale |
| Multi-region | Active-active gateways; single-writer home cell |
| Fairness | Weighted fair share + shuffle sharding |

### 6.2 Top risks

1. Heartbeat path under-designed → DB melt  
2. Claiming exactly-once without handler idempotency  
3. Cron storms  
4. Noisy tenant without isolation  
5. Dual-advancing workflows under retries  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Requirements: jobs vs DAG, semantics, multi-tenant |
| 5–12 | API + state machine + lease invariants |
| 12–22 | HLD + dequeue/retry/DLQ |
| 22–32 | Scale: heartbeats, sharding, fairness, delayed/cron |
| 32–40 | Workflows + failure/fencing scenarios |
| 40–45 | Multi-region + wrap trade-offs |

---

## 7. Deeper / Related Interview Questions

### 7.1 Semantics & correctness

**Q: How do you get exactly-once?**  
A: You generally don’t for arbitrary code. Provide at-least-once + idempotency keys + fencing so **effects** apply once.

**Q: Is lease expiry safe if the worker is still running?**  
A: It can duplicate work. Choose L ≫ heartbeat interval; handlers must tolerate duplicates; fencing blocks stale completes.

**Q: Should complete be synchronous with side effects?**  
A: Prefer: worker does side effect idempotently, then complete; or outbox pattern inside worker’s own DB. Control plane should not run business side effects.

**Q: What if complete is lost after side effect?**  
A: Classic dual-write. Use idempotent effect keyed by `job_id`/`attempt`, or transactional outbox in the worker domain DB, then complete.

### 7.2 Leases, heartbeats, theft

**Q: Heartbeat every 1s for 50M jobs?**  
A: Impossible as chatty row updates. Batch, lengthen lease, shard lease owners, heartbeat only running jobs on that worker.

**Q: Stolen work while both still run?**  
A: Both may execute; only one lease_id completes; require idempotent side effects.

**Q: How long should lease L be?**  
A: Balance detection vs false theft: e.g. 30–60s with heartbeat every 10s; tune on GC/p99 pause data.

**Q: Who runs the reaper?**  
A: Scheduled reapers per shard with `SKIP LOCKED` on expired rows; or scheduler shard owns expiry heap.

### 7.3 Queues & priorities

**Q: Redis vs Kafka vs DB?**  
A: DB for MVP correctness; Kafka for huge append/async; Redis for hot ready-sets with durable backup; hybrid wins at scale.

**Q: Avoid low-priority starvation?**  
A: Reserved capacity, aging, weighted drains—not pure strict priority.

**Q: Per-tenant queues explosion?**  
A: Don’t create physical queue per tenant. Logical fair queues over shared shards.

### 7.4 Delayed & cron

**Q: Billion delayed jobs in a ZSET?**  
A: No single ZSET. Time-partition (e.g. per hour buckets) + load only near-due window into memory.

**Q: Catch-up after scheduler downtime?**  
A: Policy: skip, enqueue once, or bounded catch-up. Document; unlimited catch-up can stampede.

**Q: Timezone / DST?**  
A: Store TZ on schedule; use zone-aware library; materializer computes next with DST rules; test around transitions.

### 7.5 Workflows / DAG

**Q: Why not let workers enqueue children?**  
A: Dual writers + retries create duplicate children. Central workflow engine (or single partition actor) advances graph.

**Q: Fan-in correctness?**  
A: Deterministic counters or set-of-finished-parents with CAS; only transition when join rule satisfied.

**Q: Large fan-out (1 parent → 100k children)?**  
A: Don’t unlock inline in one TX; chunk child creation; rate-limit explosion; consider map framework instead of naive DAG.

**Q: Saga / compensate?**  
A: On failure, engine schedules compensating jobs; mark workflow `COMPENSATING` → `FAILED`/`COMPENSATED`.

### 7.6 Multi-tenant & 1000×

**Q: Noisy neighbor?**  
A: Shuffle sharding, concurrent caps, submit quotas, separate noisy cell.

**Q: 500K submit QPS to one Postgres?**  
A: Won’t work. Shard job store by tenant/cell; partition queues; maybe log-oriented accept path.

**Q: Global priority across 1M workers?**  
A: Approximate via local weighted scheduling + admission; perfect global order is not required and not scalable.

### 7.7 Multi-region

**Q: Active-active job execution state?**  
A: Avoid dual writers. Home cell owns mutations; workers elsewhere RPC/lease from home or from regional replica only if design includes regional ownership transfer.

**Q: DR failover**  
A: Fence old cell epoch; promote; expired leases reclaim; expect duplicate runs in flight—handlers idempotent.

### 7.8 Observability & ops

**Q: How to debug “job stuck”?**  
A: Show state, lease_until, worker, last heartbeat, attempt, reaper actions; lag metrics on ready age.

**Q: SLOs?**  
A: Time-to-lease for READY jobs by priority; success rate; DLQ rate; cron lag.

**Q: Redrive DLQ safely?**  
A: New attempt id; rate-limited; require terminal `DEAD`; audit who redrove.

### 7.9 Security

**Q: Multi-tenant isolation?**  
A: Authz on every API; workers only pull authorized queues; encrypt payloads; no cross-tenant job ids guessable (UUIDs).

**Q: Hostile worker?**  
A: Mutual TLS, attested workers, scoped tokens per queue; sandbox user code if untrusted.

### 7.10 Algorithms & data structures

**Q: Data structure for ready queue?**  
A: Per-shard priority heap / multi-level queues keyed by `(priority, enqueue_time)`.

**Q: Idempotency store?**  
A: Unique constraint or KV `(tenant_id, key) → job_id` with TTL for ephemeral keys if product allows.

**Q: Rate limit?**  
A: Token bucket per tenant/queue in Redis; fail-open vs fail-closed is a product choice (prefer fail-closed for fairness).

**Q: Consistent hashing uses?**  
A: Tenant → scheduler shard; schedule_id → materializer; workflow_id → engine partition.

### 7.11 Reliability drills

**Q: Scheduler memory loss?**  
A: Rebuild ready set from durable index (`state=READY` or `RUNNING` expired).

**Q: Thundering reclaim after outage?**  
A: Jittered requeue; max reclaim rate; priority for old jobs carefully to avoid meltdown.

**Q: Workflow engine poison?**  
A: Partition DLQ; don’t block all workflows on one bad definition—type-level circuit break.

### 7.12 Comparison questions

**Q: How is this different from cron + SQS?**  
A: Unified leases, DAG orchestration, fairness, delayed/cron integration, attempt model, fencing—not just a queue.

**Q: vs Celery / Sidekiq?**  
A: Similar concepts; at 1000× need sharded control plane, cell isolation, heartbeat plane, explicit workflow engine.

**Q: vs Temporal / Cadence?**  
A: Those specialize in durable workflow execution history. This design can converge: event-sourced workflow history vs declarative step table—call the trade-off.

**Q: Should jobs be stored in Kafka forever?**  
A: Kafka as buffer yes; as system of record for mutable leases/priorities is awkward. Prefer job store + streams for notifications.

### 7.13 Priority & delayed interaction

**Q: High-priority job delayed to future—does it jump ahead when due?**  
A: When it becomes READY, it competes by priority among READY jobs—not against still-delayed jobs.

**Q: Can delayed jobs stampede?**  
A: Yes—smooth with per-shard due sweeps and admission caps.

### 7.14 Cancel / stop / resume (resolved)

**Q: Cancel vs stop worker vs resume?**  
A:  
- **Cancel job:** terminal intent; pending won’t run; running cooperative stop.  
- **Worker stop/drain:** stop leasing; finish or requeue owned leases.  
- **Resume:** only via redrive/new attempt—not automatic un-cancel.

### 7.15 Interview trap: units

**Q: 10B jobs/day × 1.5 KB = ?**  
A: **15 TB/day**, not 15 PB. 10B×1.5KB=15×10^12 B=15 TB.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- jobs
(job_id UUID PK,
 tenant_id UUID,
 queue TEXT,
 idempotency_key TEXT NULL,
 state TEXT,
 priority INT,
 run_at TIMESTAMPTZ,
 lease_id UUID NULL,
 lease_until TIMESTAMPTZ NULL,
 worker_id TEXT NULL,
 attempt INT,
 max_attempts INT,
 payload_ref TEXT,
 workflow_id UUID NULL,
 step_id UUID NULL,
 created_at, updated_at,
 UNIQUE(tenant_id, idempotency_key))

-- workflow_instances / step_instances
-- schedules(cron_expr, tz, next_run_at, policy, tenant_id)
-- attempts(job_id, attempt, lease_id, worker_id, started_at, ended_at, error)
-- dlq(job_id, reason, dead_at, payload_ref)
```

### 8.2 API checklist

- [ ] `POST /jobs` + Idempotency-Key  
- [ ] `GET /jobs/{id}`  
- [ ] `POST /jobs/{id}/cancel`  
- [ ] Worker: `Lease`, `Heartbeat`, `Complete`, `Fail`  
- [ ] `POST /workflows`  
- [ ] `POST /schedules`  
- [ ] Admin: pause queue, redrive DLQ  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Lease | Time-bounded ownership of a running attempt |
| Fencing token | `lease_id` proving ownership at complete |
| Ready | Eligible to be leased now |
| DLQ | Dead-letter queue for exhausted attempts |
| Shuffle sharding | Map tenant to random subset of shards for isolation |
| Home cell | Single-writer region/cell for tenant job state |
| Materializer | Component that turns cron/delay into READY jobs |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | PG + SKIP LOCKED, leases, retries, idempotent submit |
| 10× | Queue shards, rate limits, basic workflows |
| 100× | Scheduler tier, heartbeat plane, shuffle sharding, cron fleet |
| 1000× | Cells, regional workers, archive, hierarchical scheduling |

### 8.5 Worker protocol sketch

```text
LeaseRequest  { worker_id, queues[], max_jobs, capabilities[] }
LeaseResponse { jobs: [{job_id, lease_id, attempt, payload_ref, deadline}] }

Heartbeat     { worker_id, leases: [{lease_id, job_id}] }
HeartbeatOK   { extend_until } | { rejected: [lease_id] }

Complete      { job_id, lease_id, result_ref }
Fail          { job_id, lease_id, error_class, message, retryable:bool }
CancelWatch   { job_id } → { cancel_requested:bool }
```

### 8.6 Workflow DAG examples

**Linear:** `A → B → C`

**Fan-out/fan-in:**

```text
      A
     / \
    B   C
     \ /
      D
```

**Join rules:** `D` runs when `ALL(B,C)` succeeded; if `B` permanent-fails → workflow FAILED (or run compensate).

**Map-style caution:** exploding to 100k children belongs in a map/reduce framework with chunking—not naïve per-node rows without bulk APIs.

### 8.7 Priority + fairness interaction

```text
capacity_per_shard = C
reserve_low = 0.1C
for each tenant token bucket:
  dequeue high until tenant/global caps
  ensure low gets reserve_low over time window
aging: priority_score = base_priority + age_seconds / aging_constant
```

Priority never bypasses **tenant concurrent cap**.

### 8.8 Delayed job storage design

```text
Partitions by run_at bucket (e.g. 1-minute or 5-minute keys)
Hot window loader: for buckets in [now, now+W], load into memory ZSET/heap
Sweeper: move due → READY in batches of K with jitter
```

Billion delayed jobs: almost all cold on disk/object index; only near-due hot.

### 8.9 Interview “say this” summary (60 seconds)

> Multi-tenant scheduler with durable jobs, lease+fencing for workers, at-least-once execution and idempotent side effects; retries with backoff and DLQ; delayed/cron materializers with jitter; DAG workflows advanced by a **central engine**; priorities under weighted fair share and shuffle sharding; heartbeats scaled as their own plane; gateways active-active but job state **single-writer home cell**.

### 8.10 Extra traps

| Trap | Pushback |
|------|----------|
| Redis-only accept | Durability lie |
| Workers unlock DAG children | Duplicate graph edges under retry |
| Exactly-once without idempotency | False claim |
| Global FIFO | Noisy neighbor |
| Heartbeat row updates at 2M QPS on one PG | Melt |
| 10B×1.5KB=15PB/day | **15TB/day** |

### 8.11 Reliability test plan

1. Kill worker holding leases → reclaim after L; fencing rejects late complete.  
2. Split-brain old primary → epoch fence.  
3. Poison job → DLQ; partition progresses.  
4. Cron midnight spike → jittered materialization holds.  
5. Cancel vs complete race → single terminal CAS winner.  

### 8.12 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Ready→lease latency P0 | p99 < 2s |
| Ready→lease latency P2 | p99 < 60s |
| Duplicate success rate (fenced rejects) | monitored |
| DLQ rate | < 0.1% attempts |
| Cron lag | p99 < 30s |

### 8.13 Related systems map

```text
API → Job Store ← Cron/Delay Materializers
         ↑↓
   Scheduler Shards ←→ Lease/Heartbeat Plane
         ↓
      Workers → Side effects (idempotent)
         ↑
   Workflow Engine (graph advance)
         ↓
      DLQ / Admin Redrive / Metrics
```

---

*End of distributed job scheduler system design.*
