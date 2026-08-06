# System Design: Compute-Cluster Control Plane (GPU Fleets)

> **Focus areas:** Inventory · Node lifecycle · Desired vs actual · Agents · Health/drain · Upgrades · Capacity · Multi-cell · RBAC · Control plane vs scheduler  
> **Style:** Cluster control-plane design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit SoT for desired/actual, resolved ownership vs schedulers, honest MVP vs extreme-scale paths

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

Goal: **bound the control plane**—it owns fleet inventory, node lifecycle, and desired↔actual reconciliation; it does **not** own job fairness, credit ledgers, or gang packing logic (those belong to schedulers that *consume* capacity the control plane publishes).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a “node”? | GPU server (DGX/HGX/OEM): CPUs, NICs, local SSD, 1–8+ GPUs, firmware stack | Inventory object with typed devices, not just hostname |
| F2 | Who joins the cluster? | Bare-metal provisioners, cloud VMs, self-registering agents | Bootstrap + enrollment + attestation hooks |
| F3 | Desired vs actual? | Desired: labels, cordon, drain, software version, taints; Actual: agent-reported state | Reconciliation loop is the core |
| F4 | What does the agent do? | Heartbeat, apply desired config, report GPU health, start/stop runtime hooks | Agent is trusted local executor; CP is SoT for desired |
| F5 | Health model? | Ready / NotReady / Suspect / Draining / Offline / Quarantined | Intermediate Suspect avoids mass reclaim on blips |
| F6 | Drain / cordon? | Cordon: no new work; Drain: evacuate workloads then mark empty | APIs for ops + upgrade automation |
| G7 | Upgrades? | Rolling OS/driver/CUDA/container-runtime; canary → wave | Disruption budgets; version pins per pool |
| F8 | Capacity view? | Free/allocated/unschedulable GPUs by SKU, cell, pool | Publish capacity snapshots for schedulers |
| F9 | Multi-cell? | Cells = failure/isolation domains (region/AZ/fabric) | Per-cell CP shards; global inventory index optional |
| F10 | RBAC? | Admins, pool owners, read-only SRE, automation SAs | Authz on every mutating API; audit log |
| F11 | Relation to scheduler? | Scheduler binds jobs to devices; CP owns node membership & health | Clear boundary: CP never runs job queues |
| F12 | APIs? | Register, patch desired, drain, list capacity, watch events | Declarative preferred; imperative drain ok |

**MVP functional scope (lock with interviewer):**

1. Node enrollment with identity (mTLS cert / SPIFFE) and inventory report (SKU, GPU UUIDs, driver).  
2. Desired-state store: labels, taints, cordon, target software channel, drain intent.  
3. Agent reconcile loop: apply desired → report actual + health.  
4. Health state machine with Suspect grace; mark NotReady → notify capacity consumers.  
5. Cordon + drain APIs with progress (evacuation callbacks or scheduler cooperation).  
6. Capacity index: per-cell free/allocated/unschedulable by SKU.  
7. RBAC + audit for admin ops; watch/stream for schedulers.  
8. Rolling upgrade workflow: select pool → canary → wave with disruption budget.

**Out of MVP:**

- Full job scheduler / gang packing / credit ledger (sibling designs).  
- Automatic multi-cloud arbitrage of capacity.  
- Perfect topology discovery of every NVSwitch (hooks only).  
- Self-healing firmware flashing without human approval gates.  
- Global active-active dual-writer desired state for the same node.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Control-plane API latency | Interactive ops | p50 < 100ms, p99 < 1s for CRUD in-region |
| N2 | Agent → CP heartbeat | Frequent enough to reclaim | 5–15s interval; timeout 3–5× interval |
| N3 | Capacity freshness | Schedulers need recent view | p99 lag < 30s baseline; < 10s for hot cells at 10× |
| N4 | Consistency of desired | Single writer per node | Conditional updates / generation numbers |
| N5 | Availability | CP HA | 99.9%+ API; agents run offline-safe (last desired) |
| N6 | Scale | See progressive table | Split HB QPS from admin QPS from capacity watch QPS |
| N7 | Security | No rogue node joins | Enrollment attestation; RBAC; audit |
| N8 | Upgrade safety | No cluster wipe | Disruption budgets; canary; auto-pause on error rate |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New node boots → agent enrolls → inventory accepted → desired applied → Ready → appears in capacity.  
2. Admin cordons pool for maintenance → schedulers stop placing → drain completes → upgrade → uncordon.  
3. GPU ECC storm → agent reports unhealthy → node Quarantined → capacity removed → ticket opened.  
4. Scheduler watches capacity stream → sees free H100s in cell-a → places job (scheduler’s job).  
5. Rolling driver upgrade: canary 1% → pause check → wave 10% → complete.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Network blip, HB miss once | Stay Ready; enter Suspect only after grace |
| Split brain: two agents same node_id | Enrollment fencing; latest attested identity wins; revoke old |
| Desired update while agent offline | Persist desired; apply on reconnect; generation must match |
| Drain stuck (job won’t exit) | Timeout → force flag / escalate; never silent infinite drain |
| CP leader failover mid-drain | Drain intent durable; resume; don’t double-notify chaos |
| Mass HB loss (fabric outage) | Panic mode: don’t mark all NotReady instantly; staged |
| Rogue agent claims free GPUs | Authz + attested node identity; capacity only from enrolled |
| Scheduler and CP disagree on allocation | CP owns *schedulability*; scheduler owns *leases*—reconcile via device lease SoT pick |
| Partial inventory (GPU missing after reboot) | Mark degraded; quarantine until human/auto verify |
| Upgrade bricks node | Auto-stop wave; quarantine canary set; rollback channel |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPUs | 1,000 | 10,000 | 100,000 | 1,000,000 |
| Nodes (8-GPU) | 125 | 1,250 | 12,500 | 125,000 |
| Cells | 1 | 2–4 | 8–16 | 32–64 |
| Agents HB QPS (5s) | 25 | 250 | 2,500 | 25,000 |
| Agents HB QPS (1s) | 125 | 1,250 | 12,500 | 125,000 |
| Admin API QPS peak | ~10 | ~50 | ~200 | ~1K |
| Capacity watch clients | 5 | 50 | 200 | 1K |
| Desired updates / day | 1K | 10K | 100K | 1M |
| Drain ops / day | 20 | 200 | 2K | 20K |
| Upgrade waves / month | 2 | 4 | 8 | 16 |
| Pools / SKU classes | 5 | 15 | 40 | 100+ |

**What each jump forces:**

- **10×:** HA etcd/Raft for desired store; HB gateway separate from admin API; Suspect state.  
- **100×:** Multi-cell control planes; sharded agent gateways; capacity aggregators; disruption-budget automation.  
- **1,000×:** Hierarchical inventory (global index ← cell CP); HB aggregation; eventual capacity; cell autonomy under partition.

### 1.5 Etc. (Constraints & Assumptions)

- Nodes run a **first-party agent** (not untrusted user code).  
- Workloads may be K8s pods, custom runtimes, or bare processes—CP abstracts “evacuation” via callbacks / scheduler APIs.  
- **Single primary cloud or on-prem fabric per cell**; multi-region = multi-cell.  
- GPU UUID / PCI topology reported by agent; CP stores but may not fully validate NVLink maps in MVP.  
- Schedulers are **clients** of capacity + node events; they are not embedded in the CP binary.

**Scope statement:**

> Design a multi-cell compute-cluster control plane for GPU fleets: inventory enrollment, desired↔actual reconciliation via agents, health/drain/upgrade lifecycle, capacity publication for schedulers, RBAC/audit—scaling from ~1K to ~1M GPUs without the control plane owning job scheduling logic.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Agent heartbeats | 25–125/s | 25K–125K/s | Dominates; must be cheap |
| Desired-state patches | ~0.1/s avg | ~10–50/s | Spiky during upgrades |
| Drain / cordon ops | low | low–med | Ops-driven |
| Capacity watch fan-out | ~5 streams | ~1K streams | Aggregation + fan-out |
| Inventory full reports | rare | rare | On enroll / change |
| Admin list/get | ~10/s | ~1K/s | Cache |

**Deal-breaker:** designing the HB path as full OLTP row rewrites of entire node JSON every second on one Postgres primary.

### 2.2 Heartbeat bandwidth

```text
Baseline: 125 nodes × 1 HB / 5s = 25 HB/s
Payload: ~1–2 KB (health + free counts + versions) → 25–50 KB/s trivial

1,000× @ 5s: 125K nodes / 5 = 25K HB/s
25K × 1.5 KB ≈ 37.5 MB/s ingress → fine with sharded gateways

1,000× @ 1s: 125K HB/s × 1.5 KB ≈ 187 MB/s → still ok if sharded;
  but DB updates must be batched / column-hot / lease-extend style
```

### 2.3 Inventory storage

```text
Node record ~2–4 KB (metadata)
GPU device rows: 8 × ~200 B ≈ 1.6 KB
Baseline 125 nodes ≈ 0.5–1 MB (tiny)

1,000×: 125K nodes × 4 KB ≈ 500 MB metadata
Device rows: 1M GPUs × 200 B ≈ 200 MB
→ fits memory indexes per cell; global index is summary only
```

### 2.4 Capacity index math

```text
Per cell summary key: (cell, sku, pool) → {total, ready, allocated, unschedulable}
Update on: HB free-count change, bind/unbind event from scheduler, drain, health flip

Event rate roughly O(HB significant-diffs + scheduler bind events)
At 100K GPUs: bind events maybe hundreds/s; HB diffs lower if compressed
```

### 2.5 Upgrade wave sizing

```text
Cluster 12,500 nodes; disruption budget 5% = 625 concurrent draining
Wave size 10% = 1,250 nodes
If drain+reboot = 20 min average → wave ≈ 1,250/625 × 20 min ≈ 40 min
Canary 1% = 125 nodes first
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Heartbeat amplification** into durable store  
2. **Watch fan-out** of capacity to many schedulers  
3. **Mass health flip** during network partitions  
4. **Drain coordination** with external schedulers  
5. **Desired-state hot keys** during fleet-wide label updates  
6. **Cross-cell global inventory** consistency illusions  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Cell          → isolation domain (region/AZ/fabric); owns local CP
Pool          → operational grouping (sku + purpose + upgrade channel)
Node          → machine identity + inventory + desired + actual + health
Device        → GPU (uuid, sku, pci, mig_profile?) under a Node
DesiredState  → labels, taints, cordon, channel/version, drain_intent
ActualState   → agent-reported versions, conditions, free resources
CapacitySlice → aggregated schedulable resources published to schedulers
Agent         → on-node reconciler + reporter
```

**Health state machine:**

```text
Enrolling → Ready ⇄ Suspect → NotReady → Offline
              ↓                 ↓
          Draining         Quarantined
              ↓
          Empty → (upgrade) → Ready
```

### 3.2 Desired vs actual (reconciliation)

| Field | Desired (CP SoT) | Actual (agent) | Reconcile action |
|-------|------------------|----------------|------------------|
| Cordon | bool | reflected | Agent refuses new local admits if cordoned |
| Drain | intent + deadline | evacuate progress | Agent/scheduler evacuate; CP watches |
| Software channel | `driver:535-stable` | installed versions | Agent downloads/applies or signals need reboot |
| Labels/taints | map | echoed | Informational + scheduler filters |
| Quarantine | reason code | conditions | Force unschedulable |

**Generation / resourceVersion:** every desired write bumps `generation`; agent ACKs `observed_generation`. Stale applies rejected.

**Deal-breaker:** two systems both mutate “is cordoned” without a single SoT.

### 3.3 Control plane vs scheduler (ownership)

| Concern | Owner | Notes |
|---------|-------|-------|
| Node membership / inventory | **Control plane** | Enroll, identity, SKU |
| Health / schedulability | **Control plane** | Ready/NotReady/Quarantine |
| Drain / upgrade orchestration | **Control plane** | With scheduler cooperation |
| Job queue / fairness / credits | **Scheduler** | Not in CP |
| Device lease / gang bind | **Scheduler** (or allocator) | CP must not double-bind |
| Capacity publication | **Control plane** | Inputs: health + optional lease callbacks |
| Process start (kubelet-like) | **Agent / runtime** | May be K8s; CP doesn’t embed job logic |

**Integration patterns:**

```text
A) Scheduler listens to CP capacity + node events; owns leases in its store
B) CP hosts a thin Allocation Mirror fed by scheduler callbacks (read model)
C) Shared device lease store (etcd) — pick ONE writer for binds
```

**Chosen:** Pattern A for clarity in interviews—**CP publishes schedulability; scheduler owns leases.** Optional mirror for admin UX.

**Contradiction trap:** K8s scheduler + external GPU allocator + CP all writing device ownership—pick one bind SoT.

### 3.4 Agent protocol

```text
EnrollRequest  { node_public_key, attestation, inventory_snapshot }
EnrollResponse { node_id, client_cert, initial_desired }

Heartbeat      { node_id, observed_generation, health, conditions[],
                 free_gpus_by_sku, versions, drain_progress }
HeartbeatOK    { desired_patch?, generation, lease_of_leadership_epoch? }

ApplyResult    { generation, success, error_code }

WatchDesired   long-poll / stream alternative to piggyback on HB
```

**Offline behavior:** agent keeps last desired; continues heartbeating when network returns; does not invent new identity.

### 3.5 Drain & cordon

```text
Cordon(node|pool): desired.schedulable=false
  → capacity index removes free; running jobs continue

Drain(node, deadline, force):
  1. Cordon
  2. Emit NodeDrainStarted
  3. Scheduler evacuates (preempt/reschedule) OR agent sends local SIGTERM policy
  4. Wait until allocated_gpus==0 OR deadline
  5. Mark Drained/Empty; allow upgrade reboot
```

**Disruption budget:** `maxUnavailable` per pool; drain admission rejects if budget exceeded.

### 3.6 Upgrades

```text
UpgradePlan:
  target_channel, canary_percent, wave_percent, pause_checks[],
  disruption_budget, auto_rollback_rules

Executor:
  select candidates → cordon+drain → apply → reboot → health gate → uncordon
  on error_rate > threshold → PAUSE + alert
```

**Trade-off:** in-place driver upgrade vs immutable node image replace. Immutable is safer at 100×; in-place faster for MVP labs.

### 3.7 Multi-cell architecture

```text
Global (optional):
  Inventory Index (read-mostly summaries)
  Auth / RBAC / Audit spine
  Upgrade policy templates

Per Cell (authoritative):
  Desired Store
  Agent Gateway (HB)
  Capacity Aggregator
  Local Admin API
```

**Partition rule:** during cell↔global partition, **cell continues**; global index goes stale; no dual desired writers.

### 3.8 Capacity model

```text
schedulable_gpus = ready_gpus - cordoned - quarantined - draining_reserved
allocated_gpus   = sum(scheduler-reported leases)  # or mirrored
free_gpus        = schedulable - allocated
```

Publish:

| Stream | Content |
|--------|---------|
| Snapshot | periodic full per (cell,sku,pool) |
| Delta | node health flips, free-count changes |
| Events | DrainStarted, NodeQuarantined, UpgradeWavePaused |

**Deal-breaker:** advertising free GPUs on NotReady nodes.

### 3.9 RBAC & APIs

| Method | Path | Purpose | Roles |
|--------|------|---------|-------|
| POST | `/v1/nodes:enroll` | Agent enrollment | agent SA |
| GET | `/v1/nodes/{id}` | Inventory + desired/actual | read |
| PATCH | `/v1/nodes/{id}/desired` | Labels, channel, cordon | admin/pool-owner |
| POST | `/v1/nodes/{id}:drain` | Start drain | admin |
| POST | `/v1/nodes/{id}:quarantine` | Force out | admin/SRE |
| GET | `/v1/capacity` | Aggregates | scheduler SA |
| GET | `/v1/capacity:watch` | Stream | scheduler SA |
| POST | `/v1/upgradePlans` | Create plan | admin |
| GET | `/v1/audit` | Audit events | security |

Authz: `(principal, verb, resource, pool/cell)`. Audit every mutate.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Desired SoT | Cell CP store (etcd/Raft or SQL) | Single writer | Dual K8s annotations + ad-hoc DB |
| Heartbeats | Sharded gateway + hot lease columns | Scale HB | Monolithic JSON blob updates |
| Capacity | Aggregator read model | Fast watches | Schedulers scrape every node |
| Drain | CP intent + scheduler evacuate | Clear ownership | Agent kill -9 without budget |
| Upgrades | Canary + disruption budget | Safety | Fleet-wide simultaneous reboot |
| Multi-cell | Cell autonomy | Partition survival | Global chatty desired for every HB |

---

## 4. Architecture Diagram

### 4.1 End-to-end control plane

```text
+-------------+     +------------------+     +------------------+
| Admins / CI |---->| API Gateway+RBAC |---->| Desired Service  |
+-------------+     +--------+---------+     +--------+---------+
                             |                        |
                             v                        v
                    +--------+---------+     +--------+---------+
                    | Audit Log        |     | Desired Store    |
                    +------------------+     | (per cell HA)    |
                                             +--------+---------+
                                                      |
         +--------------------------------------------+------------------+
         |                                            |                  |
         v                                            v                  v
+------------------+                         +----------------+   +--------------+
| Agent Gateway    |<---- HB / apply --------| Node Agents    |   | Upgrade Ctrl |
| (sharded)        |                         | (per node)     |   +--------------+
+--------+---------+                         +----------------+
         |
         v
+------------------+     +------------------+     +------------------+
| Health Engine    |---->| Capacity Aggreg. |---->| Watch Fan-out    |
+------------------+     +--------+---------+     +--------+---------+
                                  |                        |
                                  v                        v
                           +---------------+        +--------------+
                           | Global Index  |        | Schedulers   |
                           | (optional)    |        | (clients)    |
                           +---------------+        +--------------+
```

### 4.2 Sequence: enroll → ready

```text
Agent                Agent GW              Desired Svc           Capacity
  |-- Enroll(attest, inventory) ->|             |                   |
  |                               |-- create -->|                   |
  |<- cert + desired -------------|             |                   |
  |-- Apply desired ------------->|             |                   |
  |-- HB Ready ------------------>|-- observe ->|                   |
  |                               |             |-- NodeReady ----->|
  |                               |             |                   |-- publish free++
```

### 4.3 Sequence: drain + upgrade

```text
Admin → API: Drain(node)
API → Desired: cordon=true, drain_intent=...
Capacity: free→0 (unschedulable)
Event → Scheduler: evacuate leases
Scheduler → preempt/reschedule → allocated→0
Agent HB: drain_progress=done
Upgrade Ctrl: apply channel → reboot → health gate
API: uncordon → Capacity free restored
```

### 4.4 Sequence: mass HB loss (panic mode)

```text
t0: fabric blip, 40% agents miss HB
Health Engine: mark Suspect (not NotReady)
t0+grace: still missing → NotReady in rate-limited batches
Capacity: degrade gradually; alert
t1: fabric restores → HB resumes → Ready (generation check)
NO: instant flip of entire cell to Offline
```

### 4.5 Multi-cell

```text
                 +-------------------------+
                 | Global Inventory Index  |
                 | Auth / Policy templates |
                 +-----------+-------------+
                             | summaries only
       +---------------------+---------------------+
       v                     v                     v
  Cell A CP             Cell B CP             Cell C CP
  agents A              agents B              agents C
  schedulers A          schedulers B          schedulers C
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | One authoritative desired generation per node | Conditional patch on `generation` |
| R2 | Only enrolled attested agents report for `node_id` | mTLS / SPIFFE; enrollment revoke |
| R3 | NotReady/Quarantined ⇒ not advertised as free | Capacity aggregator filters |
| R4 | Drain intent durable across CP failover | Persist before ACK |
| R5 | Disruption budget never silently exceeded | Admission check on drain/upgrade |
| R6 | Single writer for desired per node | Cell home; no dual-active writers |
| R7 | Scheduler leases not forged by CP | CP doesn’t mint job leases |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| CP leader crash | Elect; rebuild indexes from store; agents continue |
| Agent crash | Runtime may keep jobs; HB stops → Suspect → NotReady → scheduler reclaim |
| Agent GW shard loss | Agents reconnect to other shards; sticky sessions optional |
| Capacity aggregator lag | Schedulers see stale free—prefer under-advertise than over-advertise |
| Upgrade wave bug | Auto-pause; quarantine; rollback channel |

**Over-advertise free capacity** is worse than under-advertise: causes bind failures and user pain.

### 5.2 Scalability

**1×:** Monolithic CP + Postgres/etcd; 125 agents fine.

**10×:** HA store; separate HB gateway; health engine with Suspect; watch via long-poll.

**100×:** Cell CPs; sharded gateways; capacity aggregators; rate-limited health transitions; pool-scoped admin ops.

**1,000×:** Hierarchical summaries; HB aggregation (agent → rack proxy → cell); eventual global index; cell-local schedulers only.

**Backpressure:**

- If desired apply backlog high, slow upgrade executor.  
- If watch consumers lag, drop coalesced deltas (send snapshot repair).  
- If HB storm, sample free-count diffs; full report on change only.

### 5.3 Maintainability

- Explicit reason codes: `Cordoned`, `DrainTimeout`, `GPULost`, `DriverMismatch`, `AttestationFailed`.  
- Deterministic upgrade simulator (disruption budget math).  
- Shadow capacity: compare scheduler free vs CP free; alert drift.  
- Audit viewer for “who drained node X.”  
- Version the agent protocol; support N and N-1.

### 5.4 Ownership resolution (contradictions to avoid)

| Concern | Owner |
|---------|-------|
| Is node in cluster? | Control plane |
| Is node schedulable? | Control plane health + cordon |
| Which job holds GPU? | Scheduler / allocator |
| Who evacuates on drain? | Scheduler (primary) + agent assist |
| Who picks next job? | Scheduler |
| Who rolls drivers? | Upgrade controller in CP |
| Who bills GPU-seconds? | Credit/ledger service (elsewhere) |

**Contradiction trap:** CP “allocates GPUs” in the same PR as “schedules jobs”—split the narrative in the interview.

### 5.5 Node failure deep dive

```text
Detection: HB timeout → Suspect → NotReady
Notification: NodeNotReady event → schedulers
Reclaim: scheduler expires device leases (fencing epochs)
Reschedule: policy-dependent (fail job vs restart from checkpoint)
CP role: accurate health + inventory; NOT checkpoint orchestration
```

**Flapping:** require N-of-M successful HBs to return Ready; dampen.

### 5.6 Fairness — what CP does and doesn’t do

Control plane enables fairness **inputs** but does not implement WFQ:

- Pools and taints isolate interactive vs batch hardware.  
- Quotas on drain/upgrade prevent ops from starving a tenant pool.  
- Capacity slices per pool let schedulers apply weighted fair share.  

**Deal-breaker:** claiming CP “guarantees fair GPU time” without a scheduler fairness design.

### 5.7 Security & multi-tenancy

- Enrollment attestation (TPM/cloud identity).  
- Pool-scoped RBAC; deny cross-pool drain.  
- Secrets for agent bootstrap short-lived.  
- Audit immutability (WORM / SIEM).  
- Separation: tenant job credentials never stored in CP desired for other tenants.

### 5.8 Consistency model

| Data | Model |
|------|-------|
| Desired state | Strong (linearizable) per cell |
| Heartbeat / actual | Eventually consistent; last-write per agent session |
| Capacity aggregates | Eventually consistent; prefer monotonic unschedulable flips |
| Global index | Cached eventually; not SoT |

### 5.9 K8s relationship (common interview fork)

| Mode | Description |
|------|-------------|
| CP *is* extended K8s | CRDs for NodePool/GPUDevice; agents ≈ daemonset; use apiserver |
| CP *beside* K8s | Own desired store; integrate via device plugin + node labels |
| CP *without* K8s | Custom runtime; still same reconcile pattern |

**Say in interview:** reconcile pattern is isomorphic to controllers; GPU fleet specifics are inventory, drain budgets, and capacity publication.

### 5.10 Observability for whiteboards

| Dashboard | Metrics |
|-----------|---------|
| Fleet | nodes by health; GPUs ready/allocated/unschedulable |
| Agent | HB lag p99; apply failure rate |
| Drain | active drains; timeout rate; budget usage |
| Upgrade | wave progress; rollback count; canary error rate |
| Drift | scheduler free vs CP free |
| API | mutate QPS; authz denials |

### 5.11 API idempotency

- `Enroll` with node key → same `node_id`.  
- `Drain` with `drain_id` idempotency key.  
- Desired patch with `If-Match: generation`.  

### 5.12 Capacity under multi-SKU

```text
Index keys: (cell, pool, sku, mig_profile?)
Don’t sum A100 + H100 into “GPUs” for scheduling truth
Publish fragmentation hints optional (largest free contiguous)—or leave to scheduler
```

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Boundary: CP vs scheduler.  
2. Node model + desired/actual + generation.  
3. Agent HB + health state machine (Suspect).  
4. Capacity aggregator + watches.  
5. Drain / upgrade + disruption budgets.  
6. Multi-cell + HB sharding at scale.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Enroll, desired store, agent reconcile, cordon/drain, capacity API, RBAC |
| 10× | HA, HB gateway, Suspect, watches |
| 100× | Cells, upgrade controller, disruption budgets, drift detection |
| 1,000× | Hierarchical index, HB aggregation, cell autonomy, snapshot repair |

### 6.3 Top risks

1. Over-advertising free GPUs.  
2. Dual writers on device leases (CP vs scheduler).  
3. Mass NotReady on network blip.  
4. Drain without disruption budget.  
5. Upgrade wave without canary/auto-pause.  
6. HB path melting the desired store.

### 6.4 One-sentence design

> A cell-local, desired-state control plane that enrolls GPU nodes, reconciles via attested agents, publishes honest capacity, and orchestrates drain/upgrade under disruption budgets—while leaving job fairness and device leases to schedulers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Scope & boundaries

**Q: Is this Kubernetes?**  
A: Same reconcile pattern; may be built on K8s or beside it. Interview cares about inventory, health, capacity, drain—not memorizing CRD names.

**Q: Why not put scheduling inside the control plane?**  
A: Different scale drivers and failure domains; fairness/credits/gangs evolve faster; keep CP stable.

**Q: What is the system of record for “GPU free”?**  
A: Schedulability from CP health/cordon; allocation from scheduler leases; free = schedulable − allocated (with clear merge).

### 7.2 Desired vs actual

**Q: What if actual cannot reach desired?**  
A: Condition `Progressing=False` with reason; alert; don’t lie Ready.

**Q: How do you prevent lost updates?**  
A: `generation` / `If-Match`; reject stale patches.

**Q: Agent applies old desired after newer one?**  
A: Agent must ignore lower generation; CP may send full desired snapshot.

### 7.3 Heartbeats & health

**Q: Why Suspect?**  
A: Avoid thundering reclaim on transient loss; protects training jobs.

**Q: How to tune HB timeout?**  
A: ≫ RTT/blip; ≪ acceptable waste holding leased GPUs on dead nodes.

**Q: What goes in a HB vs full inventory?**  
A: HB = diffs + health; full inventory on enroll/change.

**Q: 125K HB/s into Postgres?**  
A: No—shard gateways, batch writes, hot columns, or in-memory lease plane with periodic flush.

### 7.4 Drain & upgrades

**Q: Cordon vs drain?**  
A: Cordon blocks new; drain evacuates existing.

**Q: Who kills the job on drain?**  
A: Prefer scheduler preemption policy; agent force as last resort with audit.

**Q: How do disruption budgets work?**  
A: Cap concurrent unavailable nodes per pool; drain admission control.

**Q: Canary failing—what happens?**  
A: Pause plan; quarantine canaries; rollback channel; page humans.

### 7.5 Multi-cell & partitions

**Q: Active-active desired for one node?**  
A: No—home cell single writer.

**Q: Global inventory during partition?**  
A: Stale read-only; cells keep operating.

**Q: Cross-cell drain?**  
A: Authz + explicit multi-cell admin tool; don’t cascade automatically.

### 7.6 Scheduler integration

**Q: How does the scheduler learn capacity?**  
A: Watch API / snapshots; optionally push bind callbacks to mirror.

**Q: Can CP preempt jobs?**  
A: It can request drain; preemption policy lives in scheduler.

**Q: Race: CP says free, scheduler binds, node dies?**  
A: Normal—lease timeout + fencing; eventual consistency of free.

### 7.7 Security

**Q: Rogue machine joins?**  
A: Attestation + enrollment approval + short-lived certs.

**Q: Tenant admin drains another pool?**  
A: RBAC deny; audit.

**Q: Agent compromise?**  
A: Limit blast to node; don’t trust agent for other nodes’ inventory; rotate.

### 7.8 Reliability drills

**Q: Two CP leaders?**  
A: Election + epoch fencing on mutations.

**Q: Half the fleet loses HB?**  
A: Panic mode; staged NotReady; don’t free all leases instantly without rate limits.

**Q: Desired store corruption?**  
A: Backups; immutable audit; rebuild from last good + agent observed.

### 7.9 Comparison traps

**Q: vs Borg/Omega/Kubernetes?**  
A: Same bones (desired state, agents). Emphasize GPU inventory, drain budgets, capacity honesty, cell autonomy.

**Q: vs cloud autoscaler?**  
A: Autoscaler changes *count*; CP manages *lifecycle of existing* heterogeneous GPU nodes + upgrades.

**Q: vs telemetry system?**  
A: Telemetry is metrics/logs analytics; CP is control loop for membership/desired. They integrate but aren’t the same.

### 7.10 Algorithms & data structures

**Q: How to index capacity?**  
A: In-memory maps `(sku,pool)→counters` + node sets; rebuild from store on failover.

**Q: How to select upgrade candidates?**  
A: Priority queue by age/version skew within budget constraints.

**Q: Watch fan-out at 1K clients?**  
A: Coalesce deltas; snapshot + catch-up; shard aggregators.

### 7.11 Fairness & pools

**Q: How do pools help fairness?**  
A: Hardware isolation for interactive vs batch; schedulers apply WFQ inside pools.

**Q: Ops unfairness?**  
A: Upgrade budgets per pool so one tenant’s maintenance doesn’t consume all disruption.

### 7.12 Interview traps (high value)

- Split HB QPS from admin QPS.  
- Name the SoT for desired vs leases.  
- Suspect before NotReady.  
- Under-advertise free > over-advertise.  
- Disruption budget on drain/upgrade.  
- Cell autonomy under partition.  
- CP does not implement gang scheduling.  
- Generation / If-Match on desired.  
- Attestation on enroll.  
- Drift detection vs scheduler.  
- Panic mode on mass HB loss.  
- Immutable vs in-place upgrades trade-off.  
- Why capacity watches not scrape.  
- Quarantine vs NotReady.  
- Idempotent drain IDs.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- nodes
(node_id UUID PK,
 cell_id TEXT,
 pool_id TEXT,
 state TEXT,              -- enrolling|ready|suspect|notready|draining|quarantined|offline
 generation BIGINT,
 observed_generation BIGINT,
 cordon BOOLEAN,
 drain_intent JSONB,
 labels JSONB,
 taints JSONB,
 channel TEXT,
 last_hb_at TIMESTAMPTZ,
 attestation_id TEXT,
 created_at, updated_at)

-- devices
(device_id TEXT PK,       -- gpu uuid
 node_id UUID,
 sku TEXT,
 pci_addr TEXT,
 mig_profile TEXT NULL,
 health TEXT,
 UNIQUE(node_id, pci_addr))

-- capacity_slices
(cell_id, pool_id, sku,
 total INT, ready INT, allocated INT, unschedulable INT,
 updated_at)

-- audit_events
(id, actor, verb, resource, before JSONB, after JSONB, at)

-- upgrade_plans
(plan_id, pool_id, target_channel, state, canary_pct, wave_pct,
 disruption_budget, created_by, created_at)
```

### 8.2 API checklist

- [ ] `POST /nodes:enroll`  
- [ ] `GET/PATCH /nodes/{id}` / desired  
- [ ] `POST /nodes/{id}:cordon|:uncordon|:drain|:quarantine`  
- [ ] `GET /capacity` + `WATCH`  
- [ ] `POST /upgradePlans` + pause/resume  
- [ ] `GET /audit`  
- [ ] Agent: Heartbeat, ApplyResult  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Desired state | CP-authored target config for a node |
| Actual state | Agent-reported observed config/health |
| Generation | Monotonic desired version |
| Cordon | Block new scheduling |
| Drain | Evacuate workloads then empty |
| Suspect | Intermediate health after HB misses |
| Quarantine | Forced unschedulable for safety |
| Cell | Failure/isolation domain with local CP |
| Pool | Upgrade/ops grouping of nodes |
| Disruption budget | Max concurrent unavailable in pool |
| Capacity slice | Aggregated schedulable counters |
| Enrollment | Attested join of a node/agent |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Desired store, agent HB, cordon/drain, capacity API, RBAC |
| 10× | HA, HB gateway, Suspect, watches |
| 100× | Multi-cell, upgrade controller, budgets, drift alerts |
| 1000× | Hierarchical index, HB aggregation, snapshot repair, cell autonomy |

### 8.5 Agent protocol sketch

```text
EnrollRequest  { attestation, inventory: {sku, gpus[], nics[], boot_id} }
EnrollResponse { node_id, cert, desired, generation }

Heartbeat      { node_id, observed_generation, conditions[],
                 free: [{sku, count}], versions, drain_progress }
HeartbeatOK    { generation, desired_fragment?, backoff_ms }

ApplyResult    { generation, ok, reason }
```

### 8.6 Drain state machine

```text
IDLE → CORDONED → DRAINING → DRAINED → UPGRADING → READY
                      ↓
                 DRAIN_TIMEOUT → FORCE_DRAIN → DRAINED
                      ↓
                 CANCELLED (uncordon if policy)
```

### 8.7 Capacity advertisement policy

```text
if health in {Ready} and not cordon and not quarantine and not draining:
  advertise free = max(0, local_free_estimate)
else:
  advertise free = 0

prefer: free_advertised <= true_free   # never tease schedulers
```

### 8.8 Interview “say this” summary (60 seconds)

> Cell-local desired-state control plane for GPU fleets: attested agents reconcile generation-versioned desired config, report health with Suspect grace, and feed a capacity aggregator that under-advertises free GPUs. Drain and upgrades run under disruption budgets. Schedulers consume watches and own device leases—the control plane does not implement job fairness or gang packing. At scale, shard HB gateways and federate cells with a read-mostly global index.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| HB updates full node JSON on one DB | Shard + hot path design |
| Instant mass NotReady | Suspect + rate limit |
| CP binds GPUs and schedules jobs | Split ownership |
| Over-advertise capacity | Prefer under-advertise |
| Fleet reboot without canary | Disruption budget + pause |
| Dual-active desired writers | Home cell SoT |
| Fairness “solved” by labels alone | Need scheduler WFQ |

### 8.10 Reliability test plan

1. Kill agent → Suspect → NotReady → capacity free=0 → scheduler reclaim.  
2. Split-brain old CP primary → epoch fence.  
3. Drain timeout → force path audited.  
4. Canary error spike → upgrade auto-pause.  
5. Fabric blip 40% HB loss → no instant cluster-wide Offline.  
6. Stale desired apply → generation reject.  

### 8.11 Observability SLOs

| SLO | Example target |
|-----|----------------|
| HB processing lag | p99 < 2s |
| Desired apply success | > 99.9% (non-quarantine) |
| Capacity watch lag | p99 < 10s (100×) |
| Drain completion (cooperative) | p50 within deadline |
| Upgrade auto-pause on error | < 5 min detection |

### 8.12 Related systems map

```text
Provisioner → Enroll → Desired Store ← Upgrade Controller
                 ↑↓
            Agent Gateway ←→ Node Agents
                 ↓
           Health Engine → Capacity Aggregator → Schedulers
                 ↓
              Audit / RBAC
```

### 8.13 Example desired document

```json
{
  "node_id": "n-9f2a",
  "generation": 42,
  "pool": "h100-training",
  "cordon": false,
  "taints": [{"key": "sku", "value": "H100", "effect": "NoScheduleUnlessTolerated"}],
  "channel": "driver-535-stable",
  "drain": null,
  "labels": {"topology.rack": "r12", "cell": "us-east-a"}
}
```

### 8.14 Example capacity snapshot

```json
{
  "cell": "us-east-a",
  "slices": [
    {"pool": "h100-training", "sku": "H100", "total": 8000, "ready": 7920,
     "allocated": 7100, "unschedulable": 80, "free": 740}
  ],
  "as_of": "2026-08-06T08:00:00Z"
}
```

### 8.15 Disruption budget worked example

```text
Pool size: 1,000 nodes
maxUnavailable: 5% → 50
Active drains: 40
New drain request for 20 nodes → admit only 10 (or reject batch)
Upgrade wave must serialize behind budget
```

---

*End of design doc. Open with §1 CP vs scheduler boundary; whiteboard §3.2–3.8 reconcile/capacity/drain; close with invariants §5.1 and traps §7.12.*
