# System Design: ML Training & Batch Inference Scheduler

> **Focus areas:** GPU cluster scheduling · Priority queues · Preemption · Data dependencies · Model registry · Batch inference DAG · Fair sharing · Cost caps
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS, explicit deal-breakers, Netflix 2025–26 interview themes
> **Interview theme:** Netflix ML Platform — schedule training and batch inference jobs across GPU pools with fairness, dependencies, and SLO-aware preemption

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

Goal: **bound **ML training and batch inference scheduler**—orchestrate DAGs of feature prep, training, evaluation, and batch scoring jobs on shared GPU/CPU fleets with priorities, quotas, and dependency-aware placement.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Schedule ML batch/train jobs | Online real-time inference serving |
| Resources | GPU, CPU, memory, disk | Full feature store design |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Job types? | Train, eval, batch infer, export | Unified job spec |
| F2 | Dependencies? | DAG edges | Scheduler topo sort |
| F3 | Priority? | Prod infer > research | Multi-queue preemption |
| F4 | Fair share? | Teams quotas | Weighted fair queue |
| F5 | GPU fraction? | MIG / whole GPU | Bin packing |
| F6 | Data locality? | Input shards near GPU | Affinity rules |
| F7 | Retries? | Transient fail | Idempotent job keys |
| F8 | Model registry? | Version artifacts | Post-train register hook |
| F9 | SLA? | Batch infer nightly windows | Deadline scheduling |
| F10 | Spot/preemptible? | Cost save | Checkpoint resume |
| F11 | Observability? | GPU util, queue wait | Dashboards |
| F12 | Isolation? | Teams cannot steal all GPUs | Hard caps |

**MVP functional scope (lock with interviewer):**

1. Job submission API with DAG.
2. Scheduler with priority queues.
3. GPU bin packing + affinity.
4. Checkpoint/resume on preempt.
5. Model registry integration.
6. Fair-share quotas per team.
7. Deadline-aware batch infer.
8. Metrics: queue time, utilization.

**Out of MVP (explicitly defer):**

- Interactive notebook scheduling
- AutoML without limits

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

1. Job submission API with DAG.
2. Scheduler with priority queues.
3. GPU bin packing + affinity.
4. Checkpoint/resume on preempt.
5. Model registry integration.
6. Fair-share quotas per team.

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

**Split classes:** submit API ≠ scheduler placement ≠ worker execution ≠ registry

**What each jump forces:**

- **10×:** Multi-queue preemption.
- **100×:** Global scheduler + regional GPU pools.
- **1,000×:** Gang scheduling + tiered spot/preempt.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-scale progressive design (10× → 100× → 1,000×).
- Sibling docs in INDEX.md for related systems.
- State invariants before drawing boxes.

**Scope statement:**

> Design **ML training/batch inference scheduler** with DAG dependencies, fair-share GPU scheduling, and checkpoint preemption — scaling to thousands of concurrent jobs.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Primary workload

```text
Jobs ~1K/day baseline; 10% GPU-long → 100 concurrent GPUs
Batch infer: 500M rows/night → shard into 10K tasks
Scheduler decisions ~10/s; workers pull tasks
```

### 2.2 Storage

```text
Hot OLTP/index: GB–TB tier
Object/log retention: PB class at 1000× with lifecycle
Idempotency TTL window drives KV size — plan explicitly
```

### 2.3 Bandwidth

```text
Egress dominates for fan-out and CDN paths
Ingress spikes during bulk/backfill — queue absorb
```

### 2.4 QPS classes (split)

| Class | Baseline | 100× | 1,000× | Notes |
|-------|----------|------|--------|-------|
| Sync writes | 100/s | 10K/s | 100K/s | sharded OLTP |
| Sync reads | 1K/s | 100K/s | 1M/s | cache + replica |
| Async consume | 500/s | 50K/s | 500K/s | partitioned |
| Batch/recon | 1/min | 10/min | 100/min | off-peak |

### 2.5 Latency budget

| Stage | Budget |
|-------|--------|
| Sync API | < 100ms p99 |
| Async visibility | < 15 min p95 |
| Batch SLA | T+1 or better |

### 2.6 Critical bottlenecks

1. Single global queue without partition keys
2. Lumping all QPS into one headline number
3. Sync call to slow warehouse on hot path
4. Missing idempotency on retries
5. No canary on config/schema changes

### 2.7 Cost intuition

```text
Track $/1M events and MTTR for rollbacks
Dominant cost usually hot storage + stream compute + egress
```

### 2.8 Deal-breaker

Lumping all QPS into one headline number

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
| JobDAG | nodes+edges |
| Task | runnable unit |
| Lease | worker hold |
| Quota | team limit |
| Artifact | model/data ref |

### 3.3 APIs (logical)

POST /jobs {dag, priority, team}; workers POST /heartbeat

### 3.4 Store choices

| Component | Choice | Rationale |
|-----------|--------|----------|
| OLTP/config | PostgreSQL | ACID + relations |
| Hot cache | Redis | p99 reads |
| Buffer | Kafka | Spike absorb |
| Warehouse | BigQuery/Snowflake | Reporting |
| Blobs | S3 + CDN | Fan-out |

### 3.5 Consistency model

- OLTP: strong per shard
- Async: at-least-once + idempotent sinks
- Cross-region: home affinity + bounded staleness

### 3.6 Failure policy

| Failure | Policy |
|---------|--------|
| Hot store timeout | Degrade per policy; never silent money loss |
| Broker lag | Scale consumers; delay reporting banner |
| Bad deploy | Canary rollback |
| Duplicate retry | Idempotent accept |

### 3.7 Security

RBAC, scoped tokens, audit append-only, rate limits on ingress.

### 3.8 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Correctness | Idempotency + recon |
| Latency | Cache + async where safe |
| Scale | Partition discipline |
| Ops | Canary + replay |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
Submit→Scheduler→Queue→Worker(GPU)→Registry/Store
```

### 4.2 Sequence: happy path

```text
Client→API: request
API→Store: validate + persist (idempotent)
API→Async: emit event
Worker→Sink: aggregate / fan-out
Client←API: 200/202
```

### 4.3 Sequence: failure/retry

```text
Client→API: retry same idempotency key
API→IdemStore: hit → return original
No double side effect
```

### 4.4 Sequence: scale-out

```text
Load↑ → autoscale API/consumers
Partition by hash(entity_id)
Hot tenant → isolate shard/cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Idempotent writes with client keys
2. Append-only audit for money/config facts
3. Hot path never blocks on warehouse
4. Explicit failure policies per plane
5. Version stamps on all derived artifacts
6. Split QPS classes in capacity planning
7. Reconciliation detects drift
8. Privacy: minimal PII on hot path

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Duplicate client retry | Idempotent 200/409 |
| Downstream lag | Backpressure + DLQ |
| Regional outage | Failover bounded staleness |
| Hot key / shard | Isolate + partition key discipline |

### 5.2 Scalability

| Scale | Changes |
|-------|--------|
| 1× | MVP single region |
| 10× | Cache + partition + outbox |
| 100× | Regional cells + replay |
| 1,000× | Tiered storage + approx where safe |

### 5.3 Maintainability

- Structured metrics without high-cardinality labels
- Shadow/dry-run modes for risky changes
- Replay and diff tooling for async pipelines
- Runbooks linked to SLO dashboards
- Feature flags for gradual enablement

### 5.4 Core algorithms

```text
function schedule():
  ready = topoSort(dag) where deps done
  pick = fairSharePick(ready, quotas)
  assign(pick, gpuBinPack)
```

### 5.5 Multi-region

| Data | Strategy |
|------|----------|
| Hot path | Regional cells + home affinity where needed |
| Config | Global SoT with cached replicas |
| Async | Partitioned logs; idempotent consumers |
| DR | RPO/RTO documented per plane |

### 5.6 Security & privacy

- RBAC on control APIs
- Minimize PII on hot path; hash identifiers
- Audit append-only for money/config changes
- Rate limits and abuse detection on public ingress

### 5.7 Observability

| Metric | Use |
|--------|-----|
| p99 latency by plane | SLO tracking |
| Error rate delta post-deploy | Canary gates |
| Lag / queue depth | Async health |
| Drift / recon diff | Money & facts correctness |

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|--------|
| One database for all planes | Latency meltdown |
| Skip idempotency | Double counts / charges |
| No partition key | Hot shard |
| Sync warehouse on hot path | p99 explosion |

### 5.9 Progressive scale deep dive

**1× baseline**
Single region MVP with core invariants and metrics.

**10×**
Introduce caching, idempotency store, Kafka/outbox, autoscale consumers.

**100×**
Regional isolation, dedicated hot pools, replay tooling, recon batches.

**1,000×**
Edge pre-aggregation, HLL/approx, cold archive, sharded control plane.

### 5.10 Testing strategy

1. Unit: pure logic (validators, compilers, aggregators)
2. Integration: store + idempotency + outbox
3. Chaos: regional fail, cache cold, broker lag
4. Load: 10× burst on hottest class only
5. Recon: batch compare SoT vs derived views

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
| --- | --- |
| Scheduling | Fair-share multi-queue |
| Fault | Checkpoint resume |
| Isolation | Team quotas |

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

### 7.1 GPU

**Q: Fragmentation?**
A: Bin pack + defrag jobs.

### 7.X Traps

**Q: One QPS number?**
A: Split write/read/async/batch.

**Q: Skip idempotency?**
A: Retries corrupt state.

---


## 5.11 GPU bin packing

```text
Task GPU memory need: 24 GB (A10) vs 80 GB (A100)
Bin pack tasks onto nodes; defragment via low-priority reschedule windows
Gang scheduling: train workers need N GPUs same node → all-or-nothing queue
```

## 5.12 Checkpoint / preemption

```text
On SIGTERM (spot preempt):
  flush checkpoint to object store every K steps
  release lease; requeue task with checkpoint_uri
Resume: restore weights; continue from step K
```

## 5.13 Fair share formula

```text
effective_priority = base_priority × (1 / (1 + recent_gpu_hours_team))
Teams over quota get demoted until window resets
Prod batch infer jobs: priority floor above research
```

## 7.9 Scheduler questions

**Q: Kubernetes enough?**  
A: K8s handles placement; still need DAG-aware scheduler layer for dependencies and fair-share — don't rely on default kube-scheduler alone.

**Q: Data locality?**  
A: Schedule task on node with input shard cached; affinity weights in scoring.


## 8. Appendices

### A1. Core schema sketch

```text
| Entity | Role |
|--------|------|
| JobDAG | nodes+edges |
| Task | runnable unit |
| Lease | worker hold |
| Quota | team limit |
| Artifact | model/data ref |
```

### A2. Launch checklist

- [ ] Idempotency verified
- [ ] Canary rollback tested
- [ ] Recon job scheduled
- [ ] Split QPS on dashboard

### A3. Glossary

| Term | Meaning |
|------|--------|
| SoT | Source of truth |

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

> **ML Training & Batch Inference Scheduler** — clarify planes, idempotency, progressive scale, recon.

### A7. Related systems map

```text
See Section 4 diagram for ML Training & Batch Inference Scheduler
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Hot p99 | < 100ms |

### A9. Worked numeric example

See Section 2 back-of-envelope for ML Training & Batch Inference Scheduler baseline numbers.

### A10. Pseudo-SQL / DDL

```sql
-- See entity sketch in A1
```

### A11. Ownership

| Concern | Owner |
|---------|-------|
| Service | Platform team |

### A12. Progressive checklist

| Scale | Must have |
|-------|----------|
| 1× | MVP invariants + metrics |
| 10× | Idempotency + cache + partition discipline |
| 100× | Regional cells + replay tooling |
| 1,000× | Tiered hot/cold + approximations where safe |

### A13. Naive design comparison

| Naive | Why it fails |
|-------|--------------|
| One DB for everything | Wrong latency class |
| No idempotency | Retries corrupt state |
| Single global queue | Hot key meltdown |
| Skip canary/validation | Fleet-wide incidents |

### A14. On-call cheat sheet

1. Check error rate delta vs deploy
2. Check lag on async plane
3. Verify idempotency / dedupe store health
4. Roll back pointer/config if SLO breach
5. Page if money/facts drift exceeds threshold

### A15. Sample debug record

```text
{
  "trace_id": "tr_abc",
  "entity_id": "ent_xyz",
  "version": 42,
  "region": "us-west-2",
  "outcome": "OK"
}
```

### A16. Cost worksheet

```text
dominant = hot_storage + stream_compute + cross_region_egress
track $/1M events and MTTR for rollbacks
```

### A17. Explicit non-goals

- Perfect global strong consistency on all reads
- Building all sibling systems in one interview
- Client-trusted counts as billing SoT

### A18. Interview rubric

- Clarify planes and split QPS
- State invariants early
- Progressive scale table
- Deal-breaker gallery
- Wrap with risks + test plan

### A19. Migration / rollout notes

Dual-write or shadow-read when replacing SoT; never big-bang cutover without recon period.

### A20. Further reading (siblings)

See INDEX.md for related Netflix docs: recommendations, event logging, ads reporting ETL.

### A21. Job DAG model

```text
Job {job_id, type: TRAIN|BATCH_INFER, project, priority, resources{gpu,cpu,mem},
     input_uris[], output_uri, retry_policy, timeout, depends_on[]}
Scheduler: topological waves; lease workers; checkpoint artifacts
```

### A22. Fair-share & preemption

```text
Queues: prod-critical > experimentation > ad-hoc
Preempt low priority mid-epoch only if checkpointed
 guaran tee min share per team to avoid starvation
```

### A23. Gang scheduling for multi-GPU

All-or-nothing placement for distributed training; avoid partial allocates that deadlock.

### A24. Batch inference path

```text
Partition input by key → map workers → write sharded outputs → commit manifest
Idempotent task ids; exactly-once effect via output overwrite + manifest CAS
```

### A25. Spot / preemptible GPUs

Checkpoint every N steps; lease TTL; restore on new node; cost vs runtime trade.

### A26. Feature/data validation gates

Block train job if training data schema drift or null rates exceed thresholds (fail closed for prod models).

### A27. Model artifact registry

```text
model_version → weights uri, metrics, training job_id, approval state
Serving pin reads registry; rollback = pointer move
```

### A28. Failure drills

1. Master scheduler failover — leases fenced.  
2. Worker death — reregister task.  
3. Output disk full — fail task, not silent truncate.  
4. Dependency cycle — reject submit.  
5. Queue hog — fair-share throttle.

### A29. Metrics

`queue_wait`, `gpu_util`, `job_success`, `preempt_rate`, `checkpoint_age`, `infer_throughput`

### A30. 60-second summary

> Scheduler runs **DAG jobs** for train + batch infer with **leases, gang scheduling, fair-share, checkpoints**, artifact registry for publish/rollback — GPUs are the scarce resource; idempotent outputs are the correctness resource.

### A31. Progressive scale

| Scale | Must |
|-------|------|
| 1× | Single queue + k8s jobs |
| 10× | Fair-share + checkpoints |
| 100× | Multi-cluster; gang; spot |
| 1,000× | Hierarchical quotas; multi-region capacity |

### A32. On-call

1. GPU idle + queue deep → placement bug.  
2. Checkpoint storm → storage.  
3. Prod train blocked → data gate.

### A33. Rubric

- Leases/fencing  
- Gang scheduling  
- Fair-share  
- Idempotent infer  
- Registry rollback  

### A34. Non-goals

Building PyTorch; online feature store deep dive; autoserving traffic router.

### A35. API sketch

```text
POST /v1/jobs
GET  /v1/jobs/{id}
POST /v1/jobs/{id}/cancel
POST /v1/models/{id}/publish
```

---

*End of document — Netflix system design interview prep: ML Training & Batch Inference Scheduler.*
