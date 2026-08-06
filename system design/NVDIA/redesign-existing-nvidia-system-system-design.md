# System Design: Redesign an Existing NVIDIA System

> **Focus areas:** Interview technique · Legacy pain points · Target architecture · Migration plan · Progressive scale · Trade-offs  
> **Primary narrative:** Modernize a **legacy GPU cluster job-submission + monitoring portal** (on-prem cron/SSH era → cloud-native control plane)  
> **Style:** Meta-style “redesign something you know” with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit assumptions, honest migration phases, no big-bang fantasy, clear MVP vs end-state

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

Goal: **pick a concrete NVIDIA-flavored surface**, state assumptions, show you can redesign under constraints—not invent a greenfield fantasy that ignores migration.

### 1.0 Interview technique (say this first)

When the interviewer says *“Redesign an existing NVIDIA system”*:

1. **Pick a known product surface** you can explain (recommend: GPU job portal / cluster submit + monitoring).  
2. **State assumptions** aloud: users, scale today, what “legacy” means.  
3. **Name pain points** before architecture.  
4. **Propose target** with explicit non-goals.  
5. **Migration plan** with coexistence—not flip-the-switch.  
6. **Trade-offs / deal-breakers** continuously.

**Alternates you could pick instead (mention, then discard):**

| Alternate | Why not primary here |
|-----------|----------------------|
| NGC-style model registry | Great, but less “ops portal” migration drama |
| Driver update distribution | Strong CDN/packaging story; different domain |
| GeForce Experience updater | Consumer-scale CDN; less cluster scheduling |

**Primary choice:** Legacy **GPU Cluster Job Submission & Monitoring Portal** (“ClusterPortal”) used by internal researchers and partners to submit training/inference jobs, view logs/metrics, and manage quotas.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who uses it today? | ML researchers, infra admins, some partners | Multi-tenant RBAC; audit |
| F2 | What does legacy do? | Web UI + scripts → SSH/node agent → local queue (Slurm-like); monitoring via Grafana scrape of static list | Split **control plane** from **data/compute plane** |
| F3 | Job types? | Single-node & multi-node GPU training; batch eval; interactive notebooks | Gang scheduling hooks; different SLOs |
| F4 | Must keep working during migration? | Yes—cannot freeze research for a quarter | Strangler fig; dual-submit adapters |
| F5 | Auth today? | Corporate SSO + scattered local accounts | Unify OIDC; deprecate local |
| F6 | Quotas? | Soft spreadsheet + admin scripts | First-class credit/quota service |
| F7 | Observability? | Partial; jobs “disappear”; logs on nodes | Central log/metrics with job_id correlation |
| F8 | APIs? | Mostly UI + ad-hoc SSH | Public API + UI; IaC-friendly |
| F9 | Multi-cluster? | Growing from 1 site to many | Federation / cell per cluster |
| F10 | Compliance? | Audit who ran what on which GPUs | Immutable audit log |

**MVP functional scope (lock with interviewer):**

1. **Submit / cancel / status** jobs via API + UI (parity with legacy happy path).  
2. **Quota check** before admit.  
3. **Unified identity** (SSO).  
4. **Live job list + basic GPU utilization** dashboards.  
5. **Log tail** and exit status.  
6. **Migration adapter** so legacy CLI still works.  
7. Admin: drain node, pause queue, redrive failed submits.

**Out of MVP:**

- Perfect topology-aware NVLink placement  
- Fully automatic multi-cloud burst  
- Replacing the underlying cluster OS scheduler in week one  
- Consumer-grade public SaaS multi-region active-active  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Availability of submit/status | Higher than legacy single VM | 99.9% control plane |
| N2 | Submit latency | Interactive | p99 < 2s admit decision (queue wait separate) |
| N3 | No lost accepted jobs | Durability | ACK only after durable log/DB |
| N4 | Migration risk | Low | Feature flags; dual-run; instant rollback |
| N5 | Scale growth | 10× GPUs in 18 months | Architecture ready for cells |
| N6 | Security | Least privilege to nodes | No SSH-as-a-service for users |
| N7 | UX parity | Must not regress core flows | Parity checklist gated |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User SSO → submit 8×GPU job → quota reserved → placed → runs → metrics/logs visible → completes → quota settled.  
2. Legacy CLI → adapter API → same control plane.  
3. Admin drains node → jobs rescheduled per policy → portal shows reason.  
4. User cancels → cooperative stop → terminal state.  
5. Dashboard shows cluster-wide free GPUs by SKU.

**Legacy pain cases (motivate redesign)**

| Pain | Symptom | Root |
|------|---------|------|
| Single portal VM | Outage = no submits | No HA |
| SSH credential sprawl | Audits fail; lateral movement | Users land on nodes |
| Spreadsheet quotas | Oversubscription fights | No atomic ledger |
| Static monitoring targets | Missing new nodes | No service discovery |
| Logs on disk of node | Job finished → logs gone | No central retention |
| Manual multi-cluster | Humans pick cluster badly | No federation |
| UI-only | No automation | No API |

**Edge / failure cases (target system)**

| Case | Behavior |
|------|----------|
| Control plane AZ loss | Multi-AZ API; jobs on cluster continue; status may lag briefly |
| Cluster agent partition | Jobs keep running; status stale; reconcile on reconnect |
| Double submit (user retry) | Idempotency key |
| Quota race | Atomic reserve |
| Partial gang start | Forbidden; wait or fail cleanly |
| Migration dual-write conflict | Legacy path ownership until cutover flag |
| User still has SSH | Break-glass only; audited |

### 1.4 Scales (Progressive)

| Metric | Legacy baseline | 10× | 100× | 1,000× |
|--------|-----------------|-----|------|--------|
| GPUs | 512 | 5K | 50K | 500K |
| Clusters / sites | 1 | 3 | 15 | 50+ |
| Jobs submitted / day | 2K | 20K | 200K | 2M |
| Concurrent jobs | 200 | 2K | 20K | 200K |
| Portal QPS (API) | 20 | 200 | 2K | 20K |
| Active users | 200 | 2K | 10K | 50K |
| Log volume / day | 500 GB | 5 TB | 50 TB | 500 TB |
| Metrics points /s | 50K | 500K | 5M | 50M |
| Admins | 5 | 15 | 40 | 100 |

**What each jump forces:**

- **10×:** HA control plane; agent fleet; central logs; real quotas.  
- **100×:** Multi-cluster federation; sharded telemetry; cell’d metadata.  
- **1,000×:** Hierarchical scheduling views; regional portals; sampling + tiered storage for telemetry.

### 1.5 Etc. (Constraints & Assumptions)

- We **do not** rip out Slurm/Kubernetes in day one; we **wrap** and gradually own more.  
- Researchers need **CLI parity** during migration.  
- “NVIDIA system” here is a **plausible internal platform** inspired by DGX/cluster ops—not a claim about a specific secret product.  
- Compute stays in cluster sites; portal/control plane may be regional cloud or on-prem HA.

**Scope statement:**

> Redesign a legacy single-VM GPU job submission and monitoring portal into a multi-AZ control plane with API-first job lifecycle, quota ledger, agent-based cluster integration, centralized observability, and a strangler-fig migration that keeps research unblocked while scale grows 10× → 100× → 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Job submit/cancel/status | 20 QPS | 20K QPS | Control plane |
| Scheduler decisions | ~5/s | ~5K/s | May stay in cluster mgr |
| Agent heartbeats | ~64/s (nodes) | ~60K/s | Distinct plane |
| Log ingest | ~50 MB/s | ~50 GB/s | Heaviest data path |
| Metrics ingest | 50K pts/s | 50M pts/s | Downsample |
| UI dashboard reads | 50 QPS | 5K QPS | Cache aggregates |

**Deal-breaker:** Designing the redesign as if **log ingest** were the same problem as **submit API**.

### 2.2 Capacity narrative

```text
Legacy: 512 GPUs, ~8 GPUs/node → 64 nodes
Heartbeats 1/5s → ~13 HB/s (or 64/s at 1Hz)—trivial
Jobs 2K/day → ~0.023/s avg; peaks ~1–5/s

10×: 5K GPUs → ~625 nodes; still fine for control plane
100×: 50K GPUs → ~6K nodes; need sharded agent gateways
1000×: 500K GPUs → ~60K nodes; regional agent planes mandatory
```

### 2.3 Logs

```text
Per job avg log 250 MB (training chatty)
2K jobs/day × 250 MB = 500 GB/day baseline (matches table)
1000×: 2M jobs/day × 250 MB = 500 PB/day if naïve—UNACCEPTABLE

Reality check / redesign force:
  - Cap default retention + sampling
  - Users opt into verbose
  - Average must drop (e.g. 25–50 MB with rotation) OR
  - Most jobs short inference with MB-level logs
Interview move: split “debug training” vs “prod inference” retention classes
Assume at 1000× blended avg 50 MB → 100 TB/day still huge → tiered storage + cold archive
```

**Unit discipline:** Call out that unconstrained per-job logs dominate cost; redesign must include **telemetry economics**.

### 2.4 Metadata storage

```text
Job record ~2 KB
Retain hot 90 days:
Baseline: 2K/day × 90 × 2 KB ≈ 360 MB (tiny)
1000×: 2M/day × 90 × 2 KB ≈ 360 GB hot metadata—fine if sharded
```

### 2.5 Migration traffic

```text
During dual-run:
  100% legacy submits mirrored async to new plane (shadow)
  Or % cutover: 10% → 50% → 100% by org/project
Shadow compare: status mismatches / hour as KPI
```

### 2.6 Critical bottlenecks

1. **Log/metrics firehose** after “centralize everything”  
2. **Agent reconnect storms** after control-plane blip  
3. **Quota ledger contention** on hot projects  
4. **Legacy SSH escape hatches** undermining security redesign  
5. **Big-bang cutover** without parity  

---

## 3. High-Level Design

### 3.1 Legacy architecture (as-is)

```text
[User laptop]
   |  (SSO to portal VM—sometimes)
   v
[Single Portal VM]----SSH/keys---->[Login node]---->[Slurm/local scheduler]
   |                                    |
   |                                    +--> compute nodes (jobs + local logs)
   +--> static Prometheus targets / Grafana on same VM
   +--> quotas.xlsx / admin scripts
```

**Why it worked at 512 GPUs:** human scale, tribal knowledge, heroes on-call.

**Why it fails next:** HA, audit, multi-cluster, automation, security.

### 3.2 Target architecture (to-be)

```text
                    +-------------------------+
   Users/CI/CLI --> | Edge + SSO (OIDC)       |
                    +-----------+-------------+
                                |
                    +-----------v-------------+
                    | Portal API (stateless,  |
                    | multi-AZ) + Web UI      |
                    +-----------+-------------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
 +--------------+      +----------------+      +----------------+
 | Job Service  |      | Quota Ledger   |      | Observability  |
 | (lifecycle)  |      | (reserve/settle)|     | Gateway        |
 +------+-------+      +--------+-------+      +--------+-------+
        |                       |                       |
        v                       v                       v
 +--------------+      +----------------+      +----------------+
 | Cluster      |      | Audit Log      |      | Logs/Metrics   |
 | Federation   |      |                |      | Lake + Index   |
 +------+-------+      +----------------+      +----------------+
        |
        v
 +--------------+     +------------------+
 | Agents per   |---->| Cluster Manager  |
 | node/cluster |     | (Slurm/K8s)      |
 +--------------+     +------------------+
```

### 3.3 Options: how radical is the redesign?

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Lift-and-shift VM to bigger VM | Fast | Repeats failure | Interview ends—no learning |
| B. Wrap legacy scheduler; new control plane | Incremental; safe | Two systems for a while | Eternal dual forever without kill plan |
| C. Replace scheduler immediately with custom | “Clean” | Research stops; risk | No migration story |
| D. Full SaaS rewrite offline | Pretty slides | Misses parity | Cannot cut over |

**Chosen:** **B — strangler fig**: new API/UI/quotas/observability; adapters to existing cluster managers; retire portal VM and SSH paths gradually.

### 3.4 Core domain model

```text
Organization → Project → QuotaAccount
User (SSO) → Membership/Role
Cluster → Node → Device(GPU SKU)
Job → Attempts → Events
Artifact (image, checkpoint ref)
```

**Job state machine:**

```text
ACCEPTED → QUEUED → SCHEDULED → RUNNING → SUCCEEDED
                              ↘ FAILED / CANCELLED / PREEMPTED
```

### 3.5 Quota ledger (new)

```text
reserve(project, sku, gpus, est_seconds) → reservation_id
on terminal: settle(actual_gpu_seconds) / release
invariant: reserved + settled accounting; no silent free GPUs
```

**Deal-breaker:** UI checkbox “quota OK” without atomic reserve.

### 3.6 Agent & cluster integration

| Approach | Use |
|----------|-----|
| Cluster-level integrator | Talk Slurm REST / K8s API; fewer agents |
| Per-node agent | Rich metrics, log ship, drain | 

**MVP:** cluster integrator + node telemetry agents.  
**Security:** agents mTLS to control plane; users never SSH by default.

### 3.7 Observability redesign

```text
Logs:   job stdout/stderr → agent → Kafka/Firehose → hot index (7–30d) → cold object
Metrics: node/GPU exporters → scrape or push → downsample → dashboards by job_id/cluster
Trace:  optional for control-plane requests
```

**Correlation mandatory:** `job_id`, `project_id`, `cluster_id`, `node_id`.

### 3.8 Migration strategy (strangler)

| Phase | Action | Rollback |
|-------|--------|----------|
| 0 | Parity inventory; shadow metrics | n/a |
| 1 | New control plane HA; read-only dashboards beside legacy | Keep legacy |
| 2 | Dual-submit adapter: legacy CLI → new API → old scheduler | Feature flag off |
| 3 | Quotas enforced in new plane; legacy spreadsheet read-only | Disable enforce |
| 4 | UI cutover by org; APIs default | DNS/flag back |
| 5 | Disable SSH user path; break-glass only | Emergency re-enable |
| 6 | Decommission portal VM | — |

**Shadow mode:** copy submits into new system without affecting scheduling; compare states.

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Scheduler | Keep Slurm/K8s initially | Risk reduction | Custom scheduler year-0 |
| Portal HA | Stateless API multi-AZ | Survive VM death | Bigger single VM |
| Quotas | Ledger service | Correctness | Spreadsheet forever |
| Logs | Tiered + caps | Cost | Infinite hot Elasticsearch |
| Migration | Strangler + flags | Continuous delivery | Big-bang weekend |
| SSH | Remove from default UX | Security | “Just give users nodes” |

---

## 4. Architecture Diagram

### 4.1 As-is vs to-be (interview whiteboard)

```text
AS-IS                              TO-BE
-----                              -----
User → PortalVM → SSH → Slurm      User → SSO → API/UI → JobSvc → Federation → ClusterMgr
             ↘ Grafana static                ↘ QuotaLedger
                                             ↘ Obs Gateway → Lake
                                             ↘ Agents (mTLS)
```

### 4.2 Submit sequence (target)

```text
UI/CLI        API         JobSvc        Quota       Federation     ClusterMgr
  |            |            |             |             |              |
  |--submit--> |--authz---->|--reserve--->|             |              |
  |            |            |<--ok--------|             |              |
  |            |            |--durable job------------->|              |
  |            |            |-------------place-------->|----create--->|
  |            |            |<------------ack-----------|<-------------|
  |<-job_id----|<-----------|             |             |              |
```

### 4.3 Monitoring path

```text
Node Agent → metrics/logs → Obs Gateway → Kafka
                              |           |
                              v           v
                         Prom/TSDB    Log Index + Object cold
                              |
                              v
                         Portal dashboards (query by job_id)
```

### 4.4 Migration dual-path

```text
Legacy CLI ──┐
             ├──> Adapter ──> New API ──> Cluster (same Slurm)
New UI/CLI ──┘         │
                       └──> Shadow compare service
Legacy Portal VM (read-only dashboards) until phase 4
```

### 4.5 Multi-cluster federation

```text
Global Directory: project → preferred clusters
Federation:
  - capacity snapshots per cluster (SKU free, queue pressure)
  - placement policy: affinity, data locality, quota site limits
Cluster cells: local agents + local log buffers (store-and-forward)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable job record** before user ACK.  
2. **Quota reserve atomic** with job accept (or compensating release on failure).  
3. **Single logical orchestrator per job** (no dual submit to two clusters without fencing).  
4. **Agents authenticated**; users not ambient root on nodes.  
5. **Migration flags** default safe; shadow ≠ prod until promoted.  
6. **Terminal states monotonic** (with explicit redrive making new attempt).

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| API AZ down | Multi-AZ; client retry + idempotency |
| Cluster manager down | Queue in control plane; backpressure status |
| Agent crash | Job process may continue; reconcile via ClusterMgr API |
| Obs pipeline down | Local disk buffer on agent; restart replay |
| Wrong cutover flag | Instant revert; dual path kept until soak |

**Cancel / stop / resume**

- Cancel: API → ClusterMgr cancel; state `CANCELLED`.  
- Stop node: drain via admin API; agents deny new; running policy migrate/kill.  
- Resume: new attempt or requeue—never silently un-fail without audit.

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Replace portal VM with HA API+UI; one cluster integrator; central logs modest |
| 10× | Autoscale API; Kafka for obs; quota service; SSO everywhere |
| 100× | Multi-cluster federation; sharded job store; regional obs; agent gateways |
| 1000× | Hierarchical capacity service; sampling; cold-tier defaults; project cells |

**Agent reconnect storm**

```text
After outage, agents MUST jitter reconnect (0–jitter_max)
Gateway admission tokens; exponential backoff
Priority: cluster integrators first, then node agents
```

### 5.3 Maintainability

- **Parity test suite:** top 50 user journeys automated against staging cluster.  
- **Contract tests:** adapter CLI ↔ API.  
- **Versioned agents** with canary.  
- **Runbooks:** cutover, rollback, break-glass SSH.  
- **Data migration:** export historical jobs from legacy DB/files into archive store.

**Observability of the redesign itself**

- Migration KPIs: % traffic on new path, shadow mismatch rate, SSH ticket count, portal VM CPU (should fall).  

### 5.4 Progressive scale deep dive

**1× — “make it correct & HA”**

```text
- Multi-AZ Portal API + UI
- Job service + Postgres
- Quota ledger tables
- One Slurm integrator
- Vector/FluentBit agents → object + small ES/OpenSearch
- SSO only
- Legacy VM still up for rollback
```

**10× — “make it operable”**

- Kafka; downsample metrics  
- Project-level RBAC  
- Idempotent submit  
- Shadow dual-run for 2 weeks  

**100× — “make it multi-cluster”**

- Federation service + capacity snapshots  
- Job store shard by project  
- Per-site obs collectors  
- Placement policies  

**1000× — “make it economical”**

- Default log sampling; verbose opt-in  
- Tiered metrics (raw short, rollups long)  
- Regional control planes with global directory  
- Auto cell assignment for projects  

### 5.5 Security redesign (often the real win)

| Legacy | Target |
|--------|--------|
| User SSH to login node | API/CLI only |
| Shared accounts | SSO + short-lived tokens |
| Keys on portal VM | Agent mTLS / SPIFFE |
| Ad-hoc sudo | Break-glass JIT with audit |

**Deal-breaker:** New pretty UI that still hands out SSH keys by default.

### 5.6 UX / API parity list (gate cutover)

- [ ] Submit job with image, gpus, command, env  
- [ ] Priority / partition selection  
- [ ] Cancel  
- [ ] List my jobs / project jobs  
- [ ] Tail logs  
- [ ] GPU util chart for job  
- [ ] Quota remaining view  
- [ ] Admin drain node  

### 5.7 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| Bigger single VM | Same SPOF |
| Big-bang cutover weekend | Unknown unknowns |
| Custom scheduler day one | Melts trust |
| Infinite hot logs | Budget death |
| Dual forever | Complexity tax |
| Ignore CLI users | Shadow IT SSH returns |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Product pick | GPU job submit + monitoring portal |
| Approach | Strangler fig around existing cluster mgr |
| Control plane | Stateless HA API + durable job/quota |
| Security | SSO + agents; SSH break-glass only |
| Obs | Central, tiered, correlated by job_id |
| Migration | Shadow → % cutover → retire VM |

### 6.2 Top risks

1. Parity gaps driving users back to SSH  
2. Observability cost explosion  
3. Quota races / double cluster submit  
4. Agent storms  
5. Organizational: admins bypass new path  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Pick system; assumptions; legacy pain |
| 5–12 | As-is vs to-be; MVP parity |
| 12–22 | Job lifecycle + quotas + agents |
| 22–30 | Observability economics |
| 30–40 | Migration phases + rollback |
| 40–45 | Scale jumps + trade-offs |

---

## 7. Deeper / Related Interview Questions

### 7.1 Interview meta

**Q: Why this system vs NGC registry?**  
A: Richer migration + HA + security story; still NVIDIA-plausible; scheduling + portal + telemetry intersect.

**Q: What if interviewer pushes driver distribution?**  
A: Pivot: CDN, signing, staged rings, telemetry of success rates—same structure: as-is pain → to-be → migrate.

**Q: How personal should “existing system” be?**  
A: Prefer public-knowledge shaped narrative; state assumptions; don’t invent confidential internals.

### 7.2 Migration

**Q: Strangler vs branch-by-abstraction?**  
A: Same family—route traffic gradually through new modules; keep old until KPIs pass.

**Q: How long dual-run?**  
A: Until shadow mismatch < threshold for N weeks and parity tests green—not a calendar fetish.

**Q: Data backfill?**  
A: Historical jobs to cold archive; hot path only needs recent + active.

**Q: How to stop SSH regression?**  
A: Measure SSH sessions; require ticket; revoke default keys; exec via audited API if needed.

### 7.3 Scheduling boundary

**Q: Do we replace Spawner/Slurm?**  
A: Not in MVP. Own **admit, quota, UX, multi-cluster policy**; delegate place/execute.

**Q: When build custom scheduler?**  
A: When federation policies cannot be expressed; after control plane trust earned.

**Q: Gang scheduling?**  
A: Require all-or-nothing via ClusterMgr features; portal must not pretend partial.

### 7.4 Quotas & fairness

**Q: Soft vs hard quotas?**  
A: Hard at admit for GPUs; soft for fair-share within queue—say which.

**Q: Preemption?**  
A: Policy on job class; portal surfaces signals; ClusterMgr executes.

**Q: Credits vs concurrency caps?**  
A: Both: concurrency protects live capacity; credits protect budget over time.

### 7.5 Observability

**Q: Push vs pull metrics?**  
A: Pull for node exporters classic; push/gateway for ephemeral; hybrid OK.

**Q: How to keep log cost sane?**  
A: Default retention short; sampling; per-project budgets; verbose opt-in; cold object storage.

**Q: Job finished, node gone—logs?**  
A: Ship during run; flush on completion hook; don’t rely on node disk.

### 7.6 Reliability

**Q: Control plane down—do GPUs idle?**  
A: Running jobs continue; new submits fail closed; status stale until recovery.

**Q: Split brain two portals?**  
A: Single writer for job id space; fencing epoch on cutover.

**Q: Idempotent submit?**  
A: `(project, idempotency_key) → job_id`.

### 7.7 Security

**Q: Multi-tenant isolation on shared cluster?**  
A: Project namespaces; device plugins; network policies; no cross-project filesystem by default.

**Q: Supply chain for images?**  
A: Allowlist registries; sign/scan; portal stores digest not `:latest` mutable tag alone.

### 7.8 Product / UX

**Q: Interactive notebooks vs batch?**  
A: Different SLOs and preemption classes; same job model with `mode=interactive|batch`.

**Q: How show ETA to start?**  
A: Queue position + historical wait by SKU/partition—approximate, labeled as estimate.

### 7.9 Scale

**Q: 60K agents to one gateway?**  
A: No—shard gateways by cluster; hierarchical HB aggregation.

**Q: Global UI over 50 clusters?**  
A: Aggregate capacity views; drill-down to cluster cell; don’t store all raw metrics globally forever.

### 7.10 Alternate redesign sketches (short)

**NGC-style model registry**

- Pain: monolith artifact DB; slow scans; unclear provenance.  
- Target: content-addressed blobs, metadata index, signing, replication.  
- Migrate: dual-publish; redirect pulls by %; verify digests.

**Driver update distribution**

- Pain: giant monolithic downloads; weak staging.  
- Target: delta packages, signed manifests, ring deployments, success telemetry.  
- Migrate: parallel channels; fleet cohorts.

### 7.11 Organizational deal-breakers

**Q: Admins insist on SSH?**  
A: Provide audited `exec` API + break-glass; measure; don’t pretend policy exists without enforcement.

**Q: Each cluster is a special snowflake?**  
A: Integrator interface; adapters per cluster type; don’t require homogeneity day one.

### 7.12 Metrics for success of redesign

| KPI | Direction |
|-----|-----------|
| Submit availability | ↑ |
| Time-to-first-schedule visibility | ↑ |
| SSH interactive sessions | ↓ |
| Shadow mismatch rate | ↓ → 0 |
| Mean time to find failed job logs | ↓ |
| Over-quota incidents | ↓ |

### 7.13 Interview traps

| Trap | Pushback |
|------|----------|
| Greenfield only | Ask about migration |
| Ignore researchers’ CLI | Adapter required |
| “We’ll centralize all logs forever hot” | Cost math |
| Custom scheduler first | Risk |
| No assumptions stated | Interviewer fills badly |

### 7.14 Consistency of job state

**Q: Cluster says RUNNING, DB says QUEUED?**  
A: Reconciler loop; ClusterMgr is truth for execution; control plane converges; surface `last_reconciled_at`.

### 7.15 Say-aloud redesign thesis

> Legacy portal VM + SSH + spreadsheet quotas cannot survive multi-cluster GPU growth. Wrap the existing scheduler with a HA API, ledger, and agents; strangler-migrate users; centralize observability with economic caps; kill SSH defaults.

---

## 8. Appendices

### 8.1 Parity checklist (printable)

- [ ] Auth SSO  
- [ ] Submit/cancel/status  
- [ ] CLI adapter  
- [ ] Quotas visible + enforced  
- [ ] Logs tail + download  
- [ ] GPU metrics by job  
- [ ] Admin drain  
- [ ] Audit export  
- [ ] Multi-cluster list (phase 2+)  

### 8.2 Schema sketches

```sql
jobs(job_id, project_id, cluster_id, state, sku, gpu_count,
     idempotency_key, created_by, created_at, ...)
reservations(id, project_id, job_id, resources, state)
job_events(job_id, ts, type, detail)
clusters(cluster_id, site, type, endpoint)
audit(id, actor, action, at, payload)
```

### 8.3 API checklist

- [ ] `POST /v1/jobs` + Idempotency-Key  
- [ ] `GET /v1/jobs/{id}`  
- [ ] `POST /v1/jobs/{id}/cancel`  
- [ ] `GET /v1/projects/{id}/quota`  
- [ ] `GET /v1/jobs/{id}/logs`  
- [ ] `GET /v1/clusters`  
- [ ] Admin: `POST /v1/nodes/{id}/drain`  

### 8.4 Agent protocol sketch

```text
Register(cluster, node, devices[], version)
Heartbeat(node, alloc[], capacity[], agent_seq)
ShipLogs(job_id, seq, chunks[])
ShipMetrics(samples[])
Reconcile(job_id) → desired state
```

### 8.5 Migration runbook (condensed)

1. Deploy control plane dark.  
2. Connect integrator read-only.  
3. Enable shadow submits.  
4. Fix mismatches.  
5. Cut 5% project traffic.  
6. Expand; freeze legacy writes.  
7. Decommission VM.  

### 8.6 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | HA API, durable jobs, SSO, one integrator, basic central logs |
| 10× | Quotas enforced, Kafka obs, shadow cutover |
| 100× | Federation, sharded metadata, site collectors |
| 1000× | Hierarchical HB, tiered telemetry defaults, regional cells |

### 8.7 Glossary

| Term | Meaning |
|------|---------|
| Strangler fig | Grow new system around old; route away gradually |
| Shadow mode | Dual-process without owning prod effects |
| Federation | Multi-cluster placement/policy layer |
| Break-glass | Emergency privileged access with audit |
| Reconciler | Loop converging desired vs observed job state |

### 8.8 Interview “say this” summary (60 seconds)

> I’d redesign our legacy GPU job portal: replace the single VM and SSH workflow with a multi-AZ API control plane, atomic quotas, and mTLS agents wrapping the existing scheduler. Migrate via strangler—shadow, percent cutover, CLI adapter—so research never stops. Centralize logs/metrics with retention economics. Scale out with federation and sharded telemetry as GPU count grows 10×/100×/1000×.

### 8.9 Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Parity miss | M | H | Checklist + beta orgs |
| Log cost | H | H | Caps + tiers |
| Dual-submit bug | M | H | Fencing + flags |
| Admin bypass | H | M | Measure SSH; policy |
| Agent storm | M | M | Jitter + admission |

### 8.10 Observability SLOs

| SLO | Target |
|-----|--------|
| Submit API availability | 99.9% |
| Shadow mismatch | < 0.1% jobs |
| Log durability for accepted jobs | > 99.9% complete shipping |
| Status freshness | p99 < 30s under normal agents |

### 8.11 As-is pain → to-be feature map

| Pain | Feature |
|------|---------|
| Portal VM SPOF | Stateless multi-AZ API |
| SSH sprawl | API/CLI + break-glass |
| Spreadsheet quotas | Ledger |
| Missing node metrics | Discovery + agents |
| Lost logs | Ship during run + cold store |
| One cluster | Federation |

### 8.12 Capacity worksheet (telemetry)

```text
choose avg_log_MB_per_job such that
  jobs/day * avg_log_MB = daily_ingest_MB
set retention_hot_days, cold_days
cost ≈ hot_store + cold_store + index_rate
if cost > budget: reduce avg_log_MB (sampling) or hot days
```

### 8.13 Alternate opener scripts

**If registry:**  
> “I’d redesign model registry around content-addressed artifacts and signed metadata…”

**If drivers:**  
> “I’d redesign driver distribution with signed manifests, delta updates, and staged fleets…”

Then still do pain → target → migrate → scale.

### 8.14 Control-plane vs data-plane

```text
Control plane: submit, quota, status, UI, federation decisions
Data plane: GPU job processes, node agents shipping bytes
Never push training tensors through portal API
```

### 8.15 Failure drill list

1. Kill portal AZ.  
2. Partition agents.  
3. Quota service timeout (fail closed).  
4. Cutover flag revert mid-day.  
5. ClusterMgr slow—backpressure user messaging.  

### 8.16 Related systems map

```text
SSO → Portal API/UI → Job Service → Federation → ClusterMgr → GPUs
                   ↘ Quota Ledger
                   ↘ Audit
Agents → Obs Gateway → Kafka → TSDB / Log Index / Object
Migration Adapter ← Legacy CLI
```

### 8.17 Extra traps

| Trap | Pushback |
|------|----------|
| Redesign without as-is | Start with pains |
| No migration | Strangler required |
| Infinite hot logs | Economics |
| Replace scheduler first | Wrap first |
| Assume zero CLI users | Adapter |

### 8.18 Sample placement policy (100×)

```text
for job in accepted:
  candidates = clusters with SKU free & project allowed
  score = w1*queue_wait_est + w2*data_locality + w3*cost
  pick min score; reserve quota site limits; submit
```

### 8.19 What “done” looks like

- Legacy portal VM powered off.  
- >95% submits via new API.  
- SSH only break-glass.  
- Quotas enforced.  
- Researchers prefer new UI/CLI.  
- On-call pages from control-plane SLOs, not “VM disk full.”  

---

*End of redesign-existing-NVIDIA-system system design.*
