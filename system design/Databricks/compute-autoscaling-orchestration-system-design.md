# System Design: Compute Autoscaling and Job Orchestration

> **Focus areas:** Clusters · Autoscaling · Queues · Fairness · Cold start · Cost · Databricks-like control plane  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct queueing math, explicit scale-up/down invariants, honest cold-start vs cost trade-offs, shuffle-aware lifecycle  
> **Interview theme:** Databricks — data platform control plane; Spark-style executors; SQL warehouses vs job clusters

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

Goal: design a **Databricks-like control plane** that accepts analytical jobs (Spark, SQL, Python), provisions elastic compute clusters, autoscales workers under queue pressure, enforces multi-tenant fairness and budgets, and minimizes cost without violating SLAs.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What compute modes? | **Job clusters** (ephemeral per run), **all-purpose clusters** (shared interactive), **SQL warehouses** (multi-tenant, low latency) | Different autoscaling policies and cold-start budgets per mode |
| F2 | Job submission? | REST/UI; DAG of tasks (notebook, JAR, Python wheel); cron schedules | Durable job registry; workflow engine with dependencies |
| F3 | Cluster shape? | Driver + N workers; min/max workers; instance types; spot/on-demand mix | Autoscaler bounds; gang scheduling for driver+initial workers |
| F4 | Autoscaling signals? | Pending tasks, executor CPU/memory, shuffle spill, queue wait time | Multi-signal controller; avoid oscillation |
| F5 | Queuing? | Jobs wait when quota/capacity exhausted; priority classes | Central scheduler + per-workspace queues |
| F6 | Fairness? | No single workspace monopolizes region capacity | Weighted fair queuing (WFQ) or dominant resource fairness (DRF) |
| F7 | Cold start? | Acceptable for batch (minutes); warehouses need seconds–tens of seconds | Instance pools; warm workers; pre-warmed AMIs |
| F8 | Scale-down? | Must not kill nodes holding shuffle blocks or active tasks | Decommission protocol; graceful drain |
| F9 | Spot/preemptible? | Cost savings with reclaim tolerance | Checkpoint + retry; mixed pools |
| F10 | Policies? | Max DBUs, max concurrent clusters, allowed instance SKUs, tags | Policy engine evaluated at schedule time |
| F11 | Secrets/init? | Mount secrets, init scripts, cluster libraries | Immutable cluster config snapshot at launch |
| F12 | Observability? | Job run history, cluster events, cost attribution | Event log + metrics; billing ledger |
| F13 | Multi-cloud? | AWS/Azure/GCP abstraction | Cloud adapter layer; not in MVP |
| F14 | Idempotent runs? | Re-run same job_id should not double-write without intent | Run_id fencing; idempotency tokens on side effects |

**MVP functional scope (lock with interviewer):**

1. `POST /jobs/{id}/runs` — enqueue run; allocate or attach cluster per policy.
2. Cluster manager launches driver + min workers via cloud API; registers with orchestrator.
3. Autoscaler loop: scale up when pending tasks > threshold for T seconds; scale down idle workers after drain window.
4. Global scheduler with per-workspace **fair share weights** and hard **quota caps**.
5. Instance pool: maintain N warm VMs; cluster attach reduces cold start from ~4 min → ~30–60s.
6. Job states: `QUEUED → STARTING → RUNNING → TERMINATING → SUCCEEDED | FAILED | CANCELED`.
7. Cost ledger: DBU/hour × node hours attributed to workspace/job/run.
8. Scale-down safety: mark node `DECOMMISSIONING`; block new tasks; wait for task completion or timeout; then terminate.

**Out of MVP (explicitly defer):**

- Serverless SQL with sub-second autoscale (Phase 2 warehouse mode)
- Cross-region failover of running Spark stages
- GPU autoscaling with fractional devices
- Customer-owned VPC peering per tenant at 1,000× scale
- Perfect global bin-packing across clouds

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Control plane availability? | Scheduling must survive AZ loss | 99.95% API; scheduler HA with leader election |
| N2 | Schedule latency? | Accept run quickly | p99 < 500ms to persist QUEUED + return run_id |
| N3 | Batch cold start? | Minutes OK with pools | p50 attach-from-pool < 60s; bare VM p50 < 4 min |
| N4 | Warehouse cold start? | Interactive | p95 query start < 5s when warm; < 30s from idle |
| N5 | Autoscale reaction time? | Scale up before SLA miss | Detect backlog within 30s; add worker within 2–3 min (cloud limit) |
| N6 | Fairness | No starvation | Low-priority gets ≥5% capacity over 5-min window |
| N7 | Cost efficiency | Minimize idle worker hours | Target <15% idle worker time at steady state |
| N8 | Correctness | No lost tasks on scale-down | At-least-once task scheduling; idempotent stages |
| N9 | Throughput | See scale table | 100 concurrent cluster mutations/s region-wide at 100× |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Job submitted → passes policy → QUEUED → capacity available → cluster STARTING from pool → RUNNING → autoscale adds workers under load → job completes → cluster TERMINATING → billing finalized.
2. SQL warehouse idle → scale to min → query arrives → fast path on warm executor → scale out if concurrent queries exceed slot capacity.
3. Scheduled cron job → dedupe overlapping runs if prior still RUNNING (policy: skip or queue).
4. Workspace within fair share → jobs start in FIFO within share.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cloud API rate limit on RunInstances | Exponential backoff; queue cluster launches; surface `STARTING` delay |
| Spot reclaim mid-shuffle | Retry stage from lineage; prefer on-demand for shuffle-heavy stages |
| Autoscaler oscillation (flapping) | Hysteresis: scale-up threshold ≠ scale-down threshold; cooldown 120–300s |
| Scale-down with cached RDD/blocks | Spark decommission; if timeout, force kill and recompute lost partitions |
| Driver OOM | Fail run; optionally retry with larger driver policy |
| No quota left | QUEUED with reason; optional preemption of lower priority |
| Thundering herd (9am SLA jobs) | Stagger schedules; pool pre-warm; admission control |
| Noisy neighbor on shared warehouse | Query queue + per-workspace concurrency caps |
| Scheduler leader crash | Failover; reconcile in-flight leases |
| Duplicate run request | Idempotency key → same run_id |
| Cluster stuck STARTING | Watchdog after 10 min → FAIL + alert |
| Partial cluster (some workers failed launch) | Continue if ≥ min workers; else fail fast |
| Multi-task DAG failure | Fail dependent tasks; retry policy per task |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Workspaces | 50 | 500 | 5K | 50K |
| Concurrent job runs | 100 | 1K | 10K | 100K |
| Concurrent clusters | 200 | 2K | 20K | 200K |
| Worker VMs (peak) | 1K | 10K | 100K | 1M |
| Scheduler decisions / min | 500 | 5K | 50K | 500K |
| Autoscale evaluations / min | 2K | 20K | 200K | 2M |
| Cloud API mutations / min | 100 | 1K | 10K | 100K (must batch) |
| Regions | 1 | 2 | 5 | 15+ |
| Instance pool size / region | 50 | 200 | 2K | 20K |

**What each jump forces:**

- **10×:** Sharded scheduler; pool service per region; async cloud launcher workers; metrics pipeline.
- **100×:** Hierarchical scheduling (region → cell → workspace); bin-packing coordinator; predictive pool sizing; separate warehouse control plane.
- **1,000×:** Cell isolation per large tenant; aggregate autoscale signals; throttle cloud API via launch queues; cost-aware spot orchestration at fleet level.

### 1.5 Etc. (Constraints & Assumptions)

- Data plane is **Spark-like**: driver schedules tasks to executors; shuffle on local disk + external storage.
- Cloud VM boot + agent install dominates cold start unless pools used.
- **DBU** (Databricks Unit) is billing abstraction; design tracks node-hours × SKU multiplier.
- Control plane is **single region authoritative** per cell; cross-region is active-passive for metadata.
- Customers tolerate **eventual** cost reports; real-time estimates OK.

**Scope statement:**

> Design a multi-tenant compute orchestrator that queues jobs, provisions elastic Spark-style clusters with shuffle-safe autoscaling, enforces fair share and quotas, and trades cold-start latency against idle cost via instance pools—scaling from ~100 concurrent runs to 100K through hierarchical scheduling and API batching.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Queue wait vs capacity (baseline)

```text
Baseline: 100 concurrent runs, avg 20 workers/run at peak → 2,000 workers
Avg task duration (batch): 2 min
Arrival rate at peak: 30 runs/min
If mean service time 15 min/run (including cluster start):
  concurrent runs ≈ 30 × 15 = 450 needed at peak without queue
→ queueing is normal; scheduler must prioritize fairly
```

**Critical insight:** The problem is **queueing + provisioning latency**, not "spin up infinite VMs instantly."

### 2.2 Cold start budget

```text
Bare EC2 m5.xlarge launch + agent + attach to cluster:
  API + boot: 60–90s
  Init scripts + libraries: 60–180s
  Total: 2–4 min typical

Instance pool attach (pre-booted VM):
  Assign from pool + agent handshake: 20–60s

Warehouse warm executor already registered:
  Query planning + slot assign: 1–5s
```

At **100×** with 10K concurrent cluster events:

```text
If 20% need net-new VMs/min = 2K launches/min ≈ 33/s
AWS RunInstances soft limits often ~few/sec/account/region → must shard accounts, batch, pools
```

### 2.3 Autoscale math

```text
Spark job: 400 tasks, 40 cores active → pending tasks pile on 10 executors (40 cores)
Rule: scale up if pending > 0 for 30s AND cpu < 70% (I/O bound) OR pending > cores for 10s
Add workers: min(ceil(pending/cores_per_worker), max_workers - current)

Scale down: idle executor (no tasks) for 300s AND shuffle blocks migrated
Remove 1 worker per 5 min max (hysteresis)
```

**Cost of wrong autoscale:**

```text
Worker m5.4xlarge ≈ $0.77/hr on-demand
1000 idle worker-hours/day wasted = $770/day/region
Spot at 60% discount still $308/day — autoscale correctness is a finance problem
```

### 2.4 Control plane storage

```text
Job run record ~2 KB (metadata, timestamps, cluster refs)
100K runs/day × 2 KB = 200 MB/day
Retain 1 year ≈ 73 GB + indexes → Postgres OK at 100×; tier to object storage at 1000×

Cluster event stream ~500 B/event, 50 events/cluster
20K clusters/day × 50 × 500 B ≈ 500 MB/day
```

### 2.5 Scheduler CPU

```text
500 scheduling decisions/min baseline
Each decision: fetch quotas, fair share calc, pick queue head → ~5–20 ms
Single leader handles 1000s/min; at 50K/min shard by region/cell
```

### 2.6 Bottlenecks (ranked)

1. Cloud API rate limits and launch latency  
2. Shuffle-unsafe scale-down causing recompute storms  
3. Scheduler hot spots (large workspace floods queue)  
4. Autoscaler flapping → cost + instability  
5. Instance pool exhaustion → cold start SLA miss  
6. Metadata DB write rate on high-churn serverless (1000×)  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Workspace          → tenant boundary; quotas; fair_share_weight
Job                → definition: tasks, schedule, cluster_policy_ref
Run                → instance of job; state machine; cluster_id
Cluster            → driver + workers; min/max; autoscale_policy
ClusterPolicy      → instance type, spot%, init scripts, max DBU
InstancePool       → warm VMs; idle TTL; replenishment target
Scheduler          → assigns runs to capacity; enforces fairness
ClusterManager     → cloud lifecycle: launch, drain, terminate
Autoscaler         → per-cluster loop: desired_workers = f(signals)
QuotaLedger        → DBU burn rate; hard stops
PlacementOptimizer → optional bin-packing across AZs / instance types
```

### 3.2 Options: central scheduler vs per-workspace agents

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Global central scheduler | Strong fairness | Single bottleneck | 1000× without sharding |
| B. Per-workspace isolated | Noisy neighbor isolated | Low utilization | Many small tenants |
| C. Two-level: global quota + local FIFO | Balanced | Complexity | Need strong fairness |
| D. Kubernetes-only (HPA) | Standard | No shuffle-aware drain; weak multi-tenant | Spark shuffle semantics |

**Chosen path:**

- **MVP:** Central scheduler + cluster manager + per-cluster autoscaler; instance pools.  
- **100×+:** Regional cells; hierarchical fair share; async cloud launcher queue; warehouse split control plane.

### 3.3 Latency budget (schedule → RUNNING)

```text
Schedule API path: 500ms total
  AuthZ/policy:        50ms
  Persist run QUEUED:  100ms
  Scheduler tick pick:  (async, 0–5s typical wait)
  Cluster STARTING:    30–240s (pool vs cold)
  Driver ready:        +30–60s
  First task running:  +10s
```

Say aloud: **API ACK is fast; RUNNING is async** — client polls or webhooks.

### 3.4 Autoscaling policy (sketch)

```text
every 30s for each RUNNING cluster:
  signals = {pending_tasks, active_tasks, executor_cpu_p95, shuffle_spill_gb, queue_time_p95}
  desired = current_workers

  if pending_tasks > 0 for 2 consecutive samples:
    desired += ceil(pending / tasks_per_worker_capacity)
  if executor_cpu_p95 > 85% for 5 min AND pending == 0:
    desired += 1  # CPU bound

  desired = clamp(desired, min_workers, max_workers)

  if desired > current:
    launch_workers(desired - current)  # respect cooldown
  elif desired < current:
    pick (current - desired) idle executors → decommission → terminate after drain
```

**Deal-breaker:** Scale down without decommission on Spark — causes shuffle fetch failures.

### 3.5 Fairness: weighted fair queuing

```text
Each workspace w has weight w_i (sum to 100)
Virtual finish time: F_i = S_i + size_i / w_i
Pick run with min F_i among QUEUED (approximate WFQ)

Hard quota: if workspace DBU_rate > cap → pause dequeuing
Preemption (optional): kill lowest priority RUNNING to free quota for P0
```

Alternative **DRF** when jobs request heterogeneous resources (CPU vs GPU vs memory).

### 3.6 Instance pools and cold start

```text
Pool maintains target_idle VMs per instance_type/AZ
On cluster start:
  if pool.available >= min_workers:
    assign from pool (fast path)
  else:
    launch via cloud API (slow path) + async replenish pool

Replenish rate limited to avoid API storms
Pool max age: recycle VM every 24–72h for patch hygiene
```

### 3.7 Cost controls

| Mechanism | Purpose |
|-----------|---------|
| Autoscale min/max | Cap burst cost |
| Spot ratio policy | Savings with reclaim rules |
| Idle cluster timeout | Terminate all-purpose after N min idle |
| DBU budget alerts | Soft notify at 80%; hard stop at 100% |
| Tag-based chargeback | team, cost_center on every VM |
| Right-sizing recommender | Offline: "job X always uses 10% CPU — lower SKU" |

### 3.8 Job cluster vs SQL warehouse

| Dimension | Job cluster | SQL warehouse |
|-----------|-------------|---------------|
| Lifetime | Per run | Long-lived |
| Autoscale signal | Spark task backlog | Query queue depth / slots |
| Cold start tolerance | Higher | Lower |
| Multi-tenant | Single job | Many concurrent queries |
| Scale-to-zero | After job | After idle timeout (minutes) |

Warehouse uses **slot** model: M concurrent queries × slots/query → scale executors to meet p95 queue time < 2s.

### 3.9 API shape (MVP)

```text
POST /api/2.1/jobs/runs/submit
  {job_id | one_time_task, cluster_spec | existing_cluster_id, idempotency_token}
  → {run_id, state=QUEUED}

GET /api/2.1/jobs/runs/get?run_id=
  → {state, cluster_id, start_time, termination_reason}

POST /api/2.1/clusters/create
  {min_workers, max_workers, autoscale, instance_pool_id, policy_id}

GET /api/2.1/clusters/events?cluster_id=
  → scale events, lifecycle

POST /api/2.1/instance-pools/create
  {target_idle, instance_type, max_capacity}
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Latency vs cost | Pools + min_workers=0 for batch | Save idle $ | Zero min for latency-critical warehouse |
| Spot vs stability | 50% spot for batch ETL | Cost | Spot for shuffle-heavy without checkpoint |
| Fairness vs utilization | WFQ + quotas | Enterprise tenants | Pure FIFO |
| Strong preemption | Off MVP | Complexity | Without priority classes |
| Sync cluster create API | 202 + poll | Cloud is slow | Block until RUNNING |

---

## 4. Architecture Diagram

### 4.1 End-to-end control plane

```text
                    +------------------+
  UI / SDK / CLI -->| API Gateway      |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
 +---------------+   +---------------+   +---------------+
 | Job Service   |   | Cluster Svc   |   | Policy/Quota  |
 | (runs, DAG)   |   | (CRUD, events)|   | Service       |
 +-------+-------+   +-------+-------+   +-------+-------+
         |                   |                   |
         v                   v                   |
 +---------------+           |                   |
 | Workflow      |           |                   |
 | Engine        |           |                   |
 +-------+-------+           |                   |
         |                   |                   |
         v                   v                   v
 +======================================================+
 |           Scheduler (leader-elected)                 |
 |  WFQ queues per workspace | quota check | pick run   |
 +==========================+==========================+
                            |
              +-------------+-------------+
              |                           |
              v                           v
     +----------------+          +----------------+
     | Cluster Manager|          | Instance Pool  |
     | (launch/drain) |<-------->| Service        |
     +--------+-------+          +----------------+
              |
              v
     +----------------+
     | Cloud Adapter  |----> AWS / Azure / GCP APIs
     +----------------+
              |
              v
     +----------------+          +----------------+
     | Data Plane     |          | Autoscaler     |
     | Driver/Workers |<---------| Controller     |
     | (Spark/etc.)   |  metrics | (per cluster)  |
     +----------------+          +----------------+
              |
              v
     +----------------+
     | Metrics + Billing|
     | Ledger           |
     +----------------+
```

### 4.2 Sequence: job run with pool attach

```text
Client       JobSvc      Scheduler    ClusterMgr    Pool      Cloud
  |--submit-->|            |             |           |         |
  |<-run_id---|            |             |           |         |
  |            |--enqueue-->|             |           |         |
  |            |            |--allocate->|           |         |
  |            |            |             |--claim-->|         |
  |            |            |             |<-VMs-----|         |
  |            |            |             |--start driver------>|
  |            |<-RUNNING---|             |           |         |
  |--poll----->|            |             |           |         |
```

### 4.3 Sequence: scale-down with drain

```text
Autoscaler    Driver       Worker-X      ClusterMgr
  |--decom X->|            |             |
  |           |--migrate shuffle blocks-->|
  |           |--wait tasks complete----->|
  |<-done-----|            |             |
  |--terminate-------------------------->|
```

If drain timeout (10 min): force kill; driver marks lost blocks; stages retry.

### 4.4 Fair share scheduling tick

```text
every 1s (leader):
  for each regional cell:
    candidates = head of each workspace queue with quota_remaining
    pick run = argmin virtual_finish_time
    if capacity_available(cell):
      assign cluster slot; transition QUEUED → STARTING
    else:
      break
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Run state durability:** QUEUED/RUNNING transitions persisted before side effects (launch VM).  
2. **At-most-one active scheduler leader** mutating assignments (etcd/ZK lease).  
3. **Scale-down safety:** no terminate until decommission complete OR explicit force with retry budget.  
4. **Idempotent cloud calls:** client token on RunInstances; reconcile on duplicate.  
5. **Quota enforcement:** cannot STARTING if hard cap exceeded (race: reserve quota slot first).  
6. **Run fencing:** stale driver heartbeats cannot report complete after new attempt started.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Scheduler leader dies | Standby takeover; replay unassigned QUEUED |
| Cluster manager crash mid-launch | Reconciler polls cloud tags; complete or rollback |
| Driver lost | Mark run FAILED; retry per policy; release workers |
| Worker spot reclaim | Replace worker; retry tasks; prefer on-demand for driver |
| Cloud API 503 storm | Launch queue with backoff; shed low priority |
| Autoscaler split-brain | Single owner per cluster_id via lease |
| DB unavailable | Read-only mode; no new runs; running continue |
| Pool exhausted | Fall back to cold launch; alert ops |

**Split-brain driver scenario:**

```text
Old driver heartbeat missed → run marked FAILED
New driver started for retry run_id+attempt
Old driver must fail fencing token check on complete RPC
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Monolithic scheduler leader; Postgres metadata; single region |
| 10× | Scheduler sharded by workspace hash; pool service; Kafka cluster events |
| 100× | Regional cells; dedicated cloud launcher workers; warehouse autoscaler separate |
| 1000× | Large-tenant dedicated cells; predictive scaling; aggregated metrics rollup |

**Cloud API batching (100×+):**

```text
Launch requests → regional queue → worker batch size 10 every 2s
Prioritize: warehouse > interactive > batch
Track API quota tokens per account/AZ
```

**Hierarchical scheduling:**

```text
Global → region cell → (optional) dedicated enterprise cell
Each level has capacity budget; spillover queues upward
```

### 5.3 Maintainability

- **Policy as code:** cluster policies versioned; runs snapshot policy_id.  
- **Simulation:** replay last week's metrics through new autoscale algorithm offline.  
- **Feature flags:** canary autoscale v2 on 5% clusters.  
- **Runbooks:** pool exhaustion, API throttle, shuffle retry storm.  
- **Chaos:** kill random workers; revoke spot; partition scheduler.

**Key metrics:**

```text
queue_wait_seconds{workspace,priority}
cluster_start_duration_seconds{pool_hit}
autoscale_events_total{direction}
idle_worker_ratio
dbu_burn_rate{workspace}
spot_reclaim_rate
scheduler_tick_lag
cloud_api_throttle_count
```

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Postgres: jobs, runs, clusters
Single scheduler leader (Raft/etcd)
Cluster manager: sync launch N workers
Autoscaler: poll Spark REST / metrics agent every 30s
Manual instance pool target
```

**10×**

- Shard scheduler in-memory queues; sticky workspace routing  
- Async launch workers via SQS/Kafka  
- Pool replenishment controller  
- Spot with 30% cap  

**100×**

- Cell per region; WFQ at cell boundary  
- Bin-pack: prefer filling existing clusters before new  
- Warehouse slot autoscaler decoupled  
- Cost anomaly detector (2× baseline DBU → page)  

**1000×**

- Dedicated cells for top-50 tenants  
- Fleet-level spot diversification  
- ML predictor for pool size from calendar + history  
- Metadata tiering: hot Postgres, cold S3 for old runs  

### 5.5 Gang scheduling and dependencies

Multi-task job DAG:

```text
Task B depends on A
Scheduler starts A; on SUCCESS enqueues B
Shared cluster if policy allows else new cluster per task
Gang: driver + min_workers must launch together — pool reserves min_workers batch
```

**Deal-breaker:** Start driver without any worker when min_workers > 0.

### 5.6 Bin packing sketch

```text
Score placing run R on cluster C:
  + affinity if same workspace (reuse)
  + savings if C has spare executor slots
  - penalty if causes new VM launch
Only pack interactive workloads; batch isolation often safer
```

### 5.7 Spot / preemptible strategy

```text
Driver: on-demand always
Workers: spot up to policy %
On reclaim notice (2 min AWS):
  decommission worker; launch replacement (spot or on-demand if reclaim rate high)
Shuffle-heavy stage: temporarily shift to on-demand
```

### 5.8 SQL warehouse autoscale (Phase 2)

```text
Signals: query_queue_depth, active_queries, executor_slots_used
Scale out: queue_depth > 0 for 5s → add executor pod/VM
Scale in: idle slots > 50% for 10 min → remove one
Min clusters: 0 or 1 (serverless) with aggressive pool
```

### 5.9 Data model (sketch)

```text
workspaces(id, fair_share_weight, dbu_cap, state)
jobs(id, workspace_id, task_dag_json, schedule_cron, policy_id)
runs(id, job_id, attempt, state, cluster_id, idempotency_token, queued_at, started_at)
clusters(id, run_id?, min_w, max_w, current_w, state, pool_id, policy_snapshot)
cluster_events(id, cluster_id, ts, type, detail_json)
instance_pools(id, region, instance_type, target_idle, available)
quota_reservations(workspace_id, run_id, dbu_rate, expires_at)
```

---

## 6. Wrap-Up

**Design summary**

- **Separate concerns:** API/job registry vs scheduler vs cluster lifecycle vs autoscale loops.  
- **Queueing is first-class:** WFQ + quotas; honest about cloud launch latency.  
- **Autoscale with hysteresis** and **shuffle-safe drain** — cost optimization must not destroy running work.  
- **Instance pools** are the primary cold-start lever; bare VM launch is fallback.  
- Scale via **cells, sharded schedulers, and launch queues** — not infinite synchronous RunInstances.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Job clusters + basic pools | Serverless SQL warehouse |
| Central WFQ scheduler | Hierarchical + preemption |
| Rule-based autoscale | ML-assisted right-sizing |
| Single cloud region | Multi-cloud adapter |

**Top risks**

1. Cloud API limits blocking morning SLA wave  
2. Autoscale flapping burning budget  
3. Unsafe scale-down causing massive stage retries  
4. Scheduler becoming bottleneck / unfair under load  

**What I'd measure first in production**

- Queue wait p95 by priority, pool hit rate, cluster start duration, idle worker ratio, DBU per successful run, spot reclaim impact on runtime.

---

## 7. Deeper / Related Interview Questions

1. How does weighted fair queuing differ from strict priority queues?  
2. When would you preempt a running job vs queue the new one?  
3. Compare Kubernetes HPA to custom Spark-aware autoscaling.  
4. How to size instance pools given diurnal batch patterns?  
5. Gang scheduling: launch all workers at once or incrementally?  
6. How to handle a workspace that submits 10K runs in one API burst?  
7. Driver high availability — worth it for batch?  
8. Multi-AZ clusters: net benefit vs shuffle cross-AZ cost?  
9. How to attribute shared warehouse DBU across queries?  
10. Bin packing jobs on shared clusters — security isolation concerns?  
11. Autoscale on CPU vs pending tasks — when do they disagree?  
12. How to test autoscale algorithms without production spend?  
13. Spot capacity insufficient in AZ — fallback strategy?  
14. Compare YARN Capacity Scheduler to this design.  
15. How does Databricks serverless hide cold start differently?

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "Just use K8s HPA" | No shuffle drain; weak fairness |
| "Scale to zero immediately after job" | Terminate only after driver confirms |
| "Infinite retries on spot loss" | Cap retries; shift SKU |
| "One global FIFO queue" | Enterprise fairness requirements |
| "Sync API until cluster ready" | 202 + poll; pools |

---

## 8. Appendices

### A. Pseudocode — scheduler tick

```text
function scheduler_tick(cell):
  if not leader(): return
  capacity = cell.available_slots()
  while capacity > 0:
    runs = [peek_queue(w) for w in cell.workspaces if quota_ok(w)]
    if runs.empty(): break
    run = argmin(runs, key=virtual_finish_time)
    if not quota_reserve(run.workspace): continue
    pop_queue(run.workspace)
    async cluster_manager.start(run)
    run.state = STARTING
    db.save(run)
    capacity -= estimated_slots(run)
```

### B. Pseudocode — autoscaler

```text
function autoscaler_loop(cluster):
  lease = acquire_lease(cluster.id)
  while cluster.state == RUNNING:
    m = fetch_metrics(cluster)
    desired = compute_desired(m, cluster.policy)
    if desired > cluster.workers:
      cluster_manager.add_workers(cluster, desired - cluster.workers)
    elif desired < cluster.workers:
      victims = pick_idle_executors(cluster, cluster.workers - desired)
      for v in victims:
        driver.decommission(v)
        wait_drain(v, timeout=10m)
        cluster_manager.terminate(v)
    sleep(30s)
```

### C. Pseudocode — pool replenish

```text
function replenish(pool):
  deficit = pool.target_idle - pool.available_count()
  if deficit <= 0: return
  batch = min(deficit, MAX_LAUNCH_BATCH, api_tokens())
  for i in 1..batch:
    vm = cloud.launch(instance_type=pool.type, tags=pool.tags)
    pool.register_idle(vm)
```

### D. Metrics checklist

```text
job_queue_wait_seconds{workspace,priority}
cluster_start_seconds{pool_hit,instance_type}
workers_current vs workers_desired
autoscale_scale_up_total / scale_down_total
shuffle_block_migration_seconds
spot_reclaim_total
dbu_rate{workspace,sku}
scheduler_leader_election_age
cloud_run_instances_errors
idle_cluster_count
```

### E. Capacity cheat sheet

```text
peak_workers ≈ concurrent_runs × avg_workers_per_run
pool_target ≈ expected_starts_per_min × attach_time_min × safety_factor
launch_workers_needed ≈ (peak_workers - pool_available) / attach_time
scheduler_shards ≈ peak_decisions_per_min / 3000
metadata_write_qps ≈ (runs_started + state_changes) / 60
```

### F. Clarifying questions cheat sheet (30 seconds)

1. Job cluster vs warehouse vs all-purpose?  
2. Fairness requirements across workspaces?  
3. Cold start SLA and spot tolerance?  
4. Scale-down: shuffle recomputation acceptable?  
5. Peak concurrent runs and workers?  
6. Hard budget caps or soft alerts?

### G. Related Databricks follow-ups

- Executor registration handshake LLD  
- DBU metering agent on each VM  
- Notebook command scheduling vs job task scheduling  
- Unity Catalog cluster init credential pass-through  

---

*End of compute autoscaling and job orchestration HLD prep.*
