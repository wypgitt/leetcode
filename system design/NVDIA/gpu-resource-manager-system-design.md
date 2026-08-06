# System Design: GPU Resource Manager (NVIDIA Job-Scheduling Interface)

> **Focus areas:** Gang scheduling · Fairness (WFQ / DRF) · Preemption · Binpack vs spread · Multi-SKU · Leases / heartbeats · MIG (optional) · Topology-aware placement (NVLink / IB)  
> **Style:** NVIDIA-flavored cluster scheduler interview — progressive scale 10× → 100× → 1,000× GPUs  
> **Quality bar:** Correct arithmetic, split control-plane vs GPU-time load classes, starvation prevention, resolved ownership of placement vs training/inference runtimes; credits/quotas optional but **fairness required**

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

Goal: **bound the GPU resource manager**—who consumes scarce NVIDIA accelerators, how fairness and gangs work, and which placement/preemption semantics are non-negotiable for training + inference fleets.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits jobs? | Training, inference replica deploys, eval/batch, interactive notebooks | Multiple queues/classes with different SLOs |
| F2 | Resource types? | GPU SKUs: A100-40/80, H100, H200, L40S, B200; CPU/RAM/NIC constrained | Inventory by SKU; not fungible across generations |
| F3 | Job shapes? | 1–N GPUs; multi-node training common; TP gangs for serving | **Gang scheduling** all-or-nothing |
| F4 | Fairness? | Weighted fair share by org/project; prevent starvation | WFQ + DRF-inspired dominant share |
| F5 | Credits/quotas? | Optional economic credits; **hard concurrency quotas** yes | Quotas required; ledger optional module |
| F6 | Priorities? | Interactive / inference SLA > training > best-effort | Priority bands + preemption rules |
| F7 | Preemption? | Yes for preemptible training/batch; not silent for SLA inference | Preemptible flag; grace + checkpoint hook |
| F8 | Placement? | Binpack util; spread HA inference; **topology-aware** for NVLink/IB | Policy per job class + topology DB |
| F9 | MIG? | Optional partitioning for small interactive on large GPUs | MIG profiles in inventory |
| F10 | Multi-region? | Capacity in several regions/cells | Federated / hierarchical schedulers |
| F11 | Leases? | Node agents heartbeat; reclaim on timeout | Fenced device leases + epochs |
| F12 | Observability? | Queue time, util, fragmentation, fairness debt, reclaim rate | Reason codes on every wait |

**MVP functional scope (lock with interviewer):**

1. Submit job/replica spec: image/command or serve config, GPU count/SKU, duration estimate, priority, preemptible, placement policy, topology prefs.  
2. **Admission** with project quotas (concurrency / GPU-count caps); optional credit reserve.  
3. Schedule with **gang semantics** and topology preferences (NVLink domain / IB leaf).  
4. **Lease + heartbeat** from node agents; reclaim on timeout.  
5. Preempt best-effort under pressure with grace signal.  
6. **Fairness** across projects via weighted shares (WFQ) + aging floors.  
7. Observe: queue time, GPU utilization, fragmentation, preemption waste.

**Out of MVP:**

- Fully automatic multi-cloud arbitrage  
- Perfect continuous defrag migration of non-preemptible jobs  
- Spot market dynamic pricing UI  
- Credits as the only fairness mechanism (weights required even if credits exist)  
- Custom FPGA/TPU heterogeneity (stick to NVIDIA GPUs)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Scheduling latency (decision) | Fast for interactive | p50 < 100ms, p99 < 1s when capacity free |
| N2 | Queue wait | Workload-dependent | Publish expected wait; inference pool separate |
| N3 | Utilization | High but not at fairness expense | 60–80% allocated GPU-time common healthy band |
| N4 | Correctness | No double-allocate GPU | Lease fencing; single allocator ownership per cell |
| N5 | Fairness | No permanent starvation | Floor share over sliding windows |
| N6 | Availability | Control plane HA | 99.9% submit/status; agents reconnect |
| N7 | Isolation | No cross-project GPU theft | cgroup/MIG/device plugin + authz |
| N8 | Topology quality | Large gangs get good domains | Soft/hard constraints explicit |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User submits 8×H100 training → quota OK → gang placed one NVLink/IB domain → leases → runs → complete → release.  
2. Inference replica TP=4 non-preemptible → spread across racks optional policy → steady heartbeats.  
3. Interactive 1×GPU (or MIG slice) → high priority → quick start; may preempt batch.  
4. Cluster full → job queued; fairness eventually starts it; reason code `WaitingFairShare` or `FragmentedCapacity`.  
5. Node dies → lease expires → reclaim → reschedule gang (fail or restart policy via caller).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Gang 64 GPUs but only 60 free scattered | Wait (don’t partial start) |
| Fragmentation: 1 GPU free on many nodes, need 8 on one | Binpack / defrag / wait |
| Topology-strict job, only cross-rack free | Wait or soft-fallback if allowed |
| Two schedulers bind same GPU | Prevent via leader + fencing—**P0** |
| Heartbeat miss (network blip) | Grace > RTT; Suspect state before reclaim |
| Preempt during non-checkpointable section | Grace signal; extend if policy; else kill |
| SKU mismatch (asked A100, only H100) | Optional upgrade with explicit user opt-in |
| Starvation of low weight org | Floor share / aging |
| MIG profile conflict on GPU | Don’t overcommit profiles; inventory accurate |
| Inference non-preemptible vs training demand | Protected reserved pools |
| Quota race two submits | Atomic admit against project counters |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPUs total | 1,000 | 10,000 | 100,000 | 1,000,000 |
| Nodes | 125 (8-GPU) | 1,250 | 12,500 | 125,000 |
| Concurrent jobs / replicas | 500 | 5,000 | 50,000 | 500,000 |
| Submits / day | 20K | 200K | 2M | 20M |
| Peak submit QPS | ~5 | ~50 | ~500 | ~5K |
| Scheduling decisions /s | ~20 | ~200 | ~2K | ~20K |
| Agent heartbeats /s | ~25–125 | ~250–1.25K | ~2.5K–12.5K | ~25K–125K |
| Orgs / projects | 100 | 1K | 10K | 100K |
| SKUs | 3 | 5 | 8 | 12+ |
| Regions / cells | 1 | 2 | 4 | 8+ |
| Topology domains tracked | ~100 | ~1K | ~10K | ~100K |

**What each jump forces:**

- **10×:** Leader-elected scheduler; sharded queues per SKU; richer fairness; topology index.  
- **100×:** Cell/region federation; approximate packing heuristics; HB aggregation; optional credit ledger service.  
- **1,000×:** Hierarchical scheduling (global admit → regional place); topology service; aggressive fragmentation control; MIG pools at volume.

### 1.5 Etc. (Constraints & Assumptions)

- Training jobs are **checkpointable** if marked preemptible.  
- Inference replicas may require **non-preemptible** reservations / protected pools.  
- Credits are **optional**; if present, map to GPU-seconds × SKU weight—but **WFQ/DRF fairness still required**.  
- We schedule GPUs; cluster manager (K8s-like) may start pods—**allocator owns GPU binding SoT**.  
- NVIDIA topology: NVLink/NVSwitch domains inside nodes/HGX; InfiniBand/RoCE across nodes.

**Scope statement:**

> Design an NVIDIA GPU resource manager for multi-tenant ML: weighted fairness (WFQ/DRF), all-or-nothing gang placement across SKUs with topology awareness, preemption with leases/heartbeats, binpack vs spread policies, optional MIG and credits—scaling from 1K to 1M GPUs without double-allocation or permanent starvation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Job **submit/status** API | ~5/s peak | ~5K/s | Control plane |
| **Scheduling evaluations** | ~20/s | ~20K/s | Fit + fairness + topology |
| Agent **heartbeats** | ~25–125/s | ~25K–125K/s | Distinct from submits |
| Quota / credit txs | ~10/s | ~10K/s | Admit/release/settle |
| Actual **GPU work** | 1000 GPUs busy | 1M | Not request QPS |

**Deal-breaker:** conflating heartbeat QPS with submit QPS or “cluster QPS.”

### 2.2 Quota & optional credit arithmetic

```text
Project quota examples:
  max_concurrent_gpus = 256
  max_running_jobs = 50
  floor_share = 5% of cell GPU-hours / week
  weight w_i = 1.0 default (or purchased tier)

Optional credits:
  L40S: 1.0 credit / GPU-hour
  A100-80: 1.5
  H100: 3.0
  Job: 8×H100 × 10 hours = 8 × 10 × 3.0 = 240 credits
```

**Fairness without credits still works** via weights + floors; credits add economic budget.

### 2.3 Utilization & fragmentation

```text
Cluster: 1000 GPUs
Allocated: 800 → 80% allocation
But free≠allocatable:

Fragmentation example:
  100 nodes × 8 GPU; free GPUs: 1 per node on 80 nodes = 80 free
  Largest gang fit on one node: 1
  fragmentation_ratio ≈ 1 - (max_fitable_gang_gpus / free_gpus)
```

Topology fragmentation:

```text
Need 64 GPUs in ≤2 IB leaves; free 64 GPUs scattered over 20 leaves
→ capacity exists, topology-fit fails
```

### 2.4 Heartbeat bandwidth

```text
125 nodes × 1 HB / 5s = 25 HB/s baseline
1,000×: 125K nodes × 0.2 Hz = 25K HB/s
→ shard agents by cell; HB to local agent gateway not global monolith
Payload: free GPUs, lease epochs, XID flags, MIG profiles, NIC health
```

### 2.5 Scheduling complexity

```text
Naïve: each schedule scan all nodes O(N)
At 12.5K nodes: need indexes:
  - per SKU free-count buckets
  - topology domain free maps
  - reserved/draining flags
Binpack: prefer most-full fit; Spread: prefer least-full / anti-affinity
Gang + topology: candidate generation then score
```

### 2.6 Preemption waste

```text
wasted_gpu_hours ≈ sum over preemptions (time_since_checkpoint × gpus)
Track separately from utilization—high util with high waste is still bad
```

### 2.7 Critical bottlenecks (rank ordered)

1. **Fragmentation** blocking large gangs  
2. **Topology-unaware packing** destroying training MFU / inference TPOT  
3. **Heartbeat path** melting control plane at 1000×  
4. **Starvation** of large jobs or low-weight projects  
5. **Dual allocators** (K8s default + custom) double-binding  
6. **Mass reclaim** on network blips  

---

## 3. High-Level Design

### 3.1 Job / allocation model

```text
AllocationRequest (Job or Replica):
  req_id, project_id, org_id
  sku, gpu_count, mig_profile?
  gang: true
  priority: P0 interactive | P1 inference-SLA | P2 training | P3 batch
  preemptible: bool
  placement: binpack | spread | topology_prefer
  topology: { strict: bool, max_domains: n, prefer_nvlink: true }
  estimate_duration
  checkpoint_signal_timeout
```

**States:**

```text
ADMITTED → QUEUED → BINDING → RUNNING → SUCCEEDED|FAILED|CANCELLED|PREEMPTED
              ↑                     |
              +------ requeue ------+
```

### 3.2 Queues & fairness (required)

**Queue structure:**

```text
per (cell, sku):
  priority bands P0..P3
  within band: weighted fair queue by project
```

**Weighted fair sharing (WFQ):**

```text
project weight w_i
virtual_time advances as service / w_i
among runnable heads, pick lowest virtual_time
aging: wait_time boost to prevent starvation
floor_share: min GPU-time over window T
ceiling: max burst concurrency
```

**DRF (Dominant Resource Fairness) note:**

```text
When jobs need GPU + CPU + RAM + NIC:
  dominant_share_i = max(gpu_i/G, cpu_i/C, mem_i/M)
  prefer project with lowest dominant share
MVP: GPU-dominant often enough; mention DRF when multi-resource contention appears
```

| Mechanism | Role |
|-----------|------|
| Quotas | Hard caps (concurrency / GPUs) |
| Weights / WFQ / DRF | Instantaneous sharing among eligible |
| Priority bands | Latency class / preemption eligibility |
| Credits (optional) | Economic budget over time |
| Reserved pools | Latency insurance for inference/interactive |

**Deal-breaker:** FIFO-only ignoring weights → noisy-neighbor; credits-only without floors → starvation.

### 3.3 Gang scheduling

```text
need = req.gpu_count
if cannot allocate ALL GPUs atomically under topology constraints:
  leave QUEUED  # never start partial gang
else:
  bind all devices in one transaction (etcd/DB conditional update)
  return Allocation{devices[], lease_epoch}
  caller starts workers/replicas
```

**Multi-node:** allocate node set with locality prefs (same NVLink domain for small; same IB leaf/rail for large).

**All-or-nothing bind transaction:**

```text
TX:
  for device in chosen:
    if device.lease_owner != null: abort
    device.lease_owner = req_id; epoch++
COMMIT → launch authority to agents
```

### 3.4 Placement: binpack vs spread vs topology

| Policy | Algorithm | Good for | Bad for |
|--------|-----------|----------|---------|
| **Binpack** | Prefer nodes with least remaining free that still fit | Training util; reduce fragments | Correlated failure |
| **Spread** | Prefer nodes with most free / across racks | Inference HA replicas | Fragmentation |
| **Topology** | Minimize domains / prefer NVLink for TP packs | Large training / TP serve | May wait longer |

**Scoring sketch:**

```text
score = w_fit * fit_quality
      + w_topo * topology_locality
      + w_pack * packing_tightness   # or spread_score
      - w_frag * fragmentation_impact
      - w_risk * correlated_failure_risk
```

**Fragmentation fighting:**

- Don’t place small jobs such that they permanently block higher-priority gangs (gang-aware reservation).  
- Optional **defrag**: drain soft jobs to coalesce free contiguous GPUs.  
- MIG for small interactive slices on big GPUs.

### 3.5 Topology database

```text
region → cell → zone → ib_leaf / rack → nvlink_domain → node → gpu
Optional: NIC rail maps for multi-rail IB
```

**Placement preferences:**

1. Same NVLink domain for ≤8 GPU TP-style packs on HGX-class.  
2. Same rack / IB leaf for multi-node gangs.  
3. Same zone; avoid cross-zone unless capacity forces.  

`topology_strict: true` → wait rather than bad fit for large training.

### 3.6 Preemption policy

```text
when higher band needs capacity:
  candidates = running preemptible jobs in lower bands
  score victims by:
    - progress since checkpoint (prefer recent ckpt)
    - weight / floor debt
    - size fit for requester
    - avoid brand-new jobs (warmup amortization)
  send preempt signal; grace G seconds
  if not exited: hard kill; mark PREEMPTED; release leases; requeue optional
```

**Non-preemptible:** inference SLA replicas, paid reserved capacity, interactive protected pool.

**Starvation prevention:** limit fraction of cluster that is always-preemptible; guarantee floor share windows.

### 3.7 Leases & heartbeats

```text
Node agent:
  heartbeat every T with: inventory, running lease health, GPU errors, MIG state
Scheduler:
  if now - last_hb > timeout: mark node Suspect → NotReady
  reclaim leases; notify job controllers; reschedule per policy
```

**Fencing:** device lease includes epoch; agent refuses old epoch binds; scheduler leader epoch on bind RPCs.

### 3.8 Multi-SKU & optional substitution

- Separate free lists & queues per SKU.  
- Optional **substitution graph**: H100 can satisfy A100 request if user opts in (cost/weight may change).  
- Don’t silently substitute—billing/perf surprise is a deal-breaker.

### 3.9 MIG (optional)

```text
GPU can be whole or partitioned into MIG profiles (e.g. 1g.10gb …)
Inventory tracks profile slots
Small interactive notebooks → MIG binpack
Training/inference large → full GPU / multi-GPU gangs
Constraint: cannot place full-GPU job on already MIG-sliced device without reclaim
```

### 3.10 Optional credit ledger

If interviewer wants credits (OpenAI-style add-on):

| Op | Meaning |
|----|---------|
| `Reserve(req, amount)` | Hold at admit |
| `Settle(req, actual)` | Burn actual GPU-seconds × weight |
| `Release` | Cancel before/during |

**Invariant:** no bind without reserve when credits enabled; settle idempotent on `req_id`.

**Ownership:** Ledger owns money; scheduler owns machines; binding requires quota (+ reserve).

### 3.11 Multi-region / cells

```text
Global Admit (quota + policy + optional credits)
   → choose cell (affinity, capacity forecast, data locality)
      → Cell Scheduler (placement + leases + topology)
```

**Avoid:** dual cell binders for same req without fencing.

### 3.12 APIs

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/allocations` | Request GPUs (idempotency key) |
| GET | `/v1/allocations/{id}` | Status, devices, reason codes |
| POST | `/v1/allocations/{id}:cancel` | Cancel |
| POST | `/v1/allocations/{id}:preempt_ack` | Caller finished grace |
| GET | `/v1/capacity` | Free/queued by SKU/topology |
| GET | `/v1/fairness` | Share vs usage |
| POST | `/v1/credits/topup` | Optional admin |

### 3.13 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Device SoT | Cell scheduler leader | No double bind | K8s + custom both binding |
| Fairness | WFQ + floors (+ DRF if needed) | Multi-tenant ML | Global FIFO |
| Gangs | Atomic multi-device bind | Training/TP correctness | Partial start |
| Topology | Indexed domains | MFU / TPOT | Random node pick |
| HB scale | Cell-local aggregators | 1000× nodes | One global HB DB |
| Small jobs | MIG or binpack leftovers | Util | Shattering large domains carelessly |

---

## 4. Architecture Diagram

### 4.1 Control plane

```text
+-------------+     +------------------+     +-----------------+
| Train/Infer |---->| API Gateway      |---->| Admit Service   |
| Controllers |     +--------+---------+     | quotas[/credits]|
+-------------+              |               +--------+--------+
                             |                        |
                             v                        v
                    +--------+---------+     +--------+--------+
                    | Fairness Queues  |     | Scheduler Leader|
                    | (sku, priority)  |     | (per cell)      |
                    +------------------+     +--------+--------+
                                                      |
                     +--------------------------------+----------------+
                     v                                v                v
              Topology DB                        Placement         Allocation
              (NVLink/IB)                        Engine            Map (leases)
                                                     |
                                                     v
                                              +------+------+
                                              | Node Agents |
                                              | (NVIDIA)    |
                                              +-------------+
```

### 4.2 Sequence: admit + gang bind

```text
Caller → API: CreateAllocation(8xH100, topology_prefer)
API → Admit: quota check (+ optional Reserve credits)
Admit → OK
API → Scheduler: Enqueue(req)
Scheduler: fairness says runnable; search placement w/ topology
Scheduler: TX bind 8 devices same domain
Scheduler → Agents: Bind(req, lease_epoch)
Agents → HB running
Caller starts training/inference runtime
End → Scheduler unbind → Settle/release quota
```

### 4.3 Sequence: preemption

```text
P0 needs 2 GPUs; none free
Scheduler: select preemptible P3 victim
Agent: Preempt(victim, grace=30s)
Victim checkpoints / exits
Scheduler: unbind → bind P0 → notify caller
Victim: PREEMPTED; optional auto-requeue; quota released for unused
```

### 4.4 Topology-aware pack

```text
Request: 16 GPUs, prefer 2×8 NVLink domains on same IB leaf
Candidate generation:
  list leaves with ≥16 free matching SKU
  within leaf, pick nodes maximizing NVLink packing
Score vs alternatives; bind TX
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | A GPU device has ≤1 lease owner | Conditional bind TX; epoch fencing |
| R2 | Gang either fully bound or not running | Atomic multi-device bind |
| R3 | Quota counters never negative / over max | Atomic admit |
| R4 | Dead agent → devices reclaimed | HB timeout + fence |
| R5 | Single scheduler leader per cell | Raft/etcd election |
| R6 | Preempt only eligible jobs | Flags + policy engine |
| R7 | Leader binds carry leader epoch | Agents reject stale |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| Scheduler leader crash | Follower elects; rebuild indexes; agents continue |
| Admit/quota store down | Fail new admits; running OK |
| Agent flapping | Suspect state; avoid mass preemption |
| Partial gang start bug | **P0 incident**—tests must catch |
| Clock skew on leases | Leader monotonic / logical timeout |
| Network partition HB loss | Staged reclaim; panic dampeners |

### 5.2 Scalability

**1×:** Monolithic scheduler + Postgres quotas; 1K GPUs fine.

**10×:** Leader election; queue by SKU; indexed free-GPU heaps; topology views.

**100×:** Regional cells; sharded request stores; approximate fair-share counters; optimistic binding with conflict retry; HB gateways.

**1,000×:** Hierarchical global queueing; capacity forecasts; dedicated topology service; per-cell allocators; HB aggregators; MIG fleet features.

**Backpressure:** if BINDING backlog high, stop starting more until agents catch up.

### 5.3 Maintainability

- Deterministic simulator for packing/fairness/topology.  
- Shadow scheduling for policy changes.  
- Clear reason codes: `InsufficientQuota`, `FragmentedCapacity`, `TopologyUnsatisfied`, `WaitingForGang`, `WaitingFairShare`, `Preempted`.  
- Audit log for every bind/preempt/release.  
- Chaos: kill leader, drop HB, fill fragmentation scenarios.

### 5.4 Ownership resolution

| Concern | Owner |
|---------|-------|
| Who may run (caps) | Admit / quota (+ optional credits) |
| Who runs next among eligible | Fairness / queues |
| Where it runs | Placement engine |
| What is allocated now | Allocation map (cell leader) |
| Process lifecycle | Node agent / kubelet-like + job controller |
| Checkpoint on preempt | Training/inference runtime (not RM) |
| Refund/settle policy | Product + optional ledger |

**Contradiction trap:** K8s default scheduler + external GPU allocator both binding—pick one SoT for device leases.

### 5.5 Starvation & large-gang policy

**Problems:**

1. High-weight org always wins → floors.  
2. Large gangs wait forever behind small jobs → gang-aware reservation / blocking.  
3. Interactive/inference hogs → reserved pools %.  
4. Topology-strict jobs wait forever → publish wait forecasts; optional soft fallback.

**Mechanisms:**

- **Floor share:** min % over sliding window.  
- **Ceiling:** max burst concurrency.  
- **Aging:** priority boost with wait.  
- **Reservation for gangs:** speculative hold of freeing GPUs for short window.  
- **Pinned holes:** keep intentional contiguous free for upcoming high-prio gangs.

### 5.6 Checkpoint-aware preemption scoring

```text
victim_score = gpu_hours_since_checkpoint × weight_factor × (1 - priority_band_norm)
prefer victims with recent checkpoints and low weight
avoid victims in first few minutes after start
never preempt non-preemptible inference without policy exception
```

Emit: `wasted_gpu_hours_on_preempt`.

### 5.7 Reserved pools vs on-demand

| Pool | Use | Preemptible? |
|------|-----|--------------|
| Interactive reserved (5–10%) | Notebooks, debug | No |
| Inference SLA reserved | Online replicas | No |
| Training on-demand | Default gangs | Optional |
| Batch scavenger | Best-effort | Yes |

Quotas/weights still apply inside pools; reservation buys **latency**, not infinite capacity.

### 5.8 Control-plane HA details

- Scheduler leader in etcd/Raft; allocation map versioned per device.  
- On failover: rebuild in-memory indexes from store; new binds wait until ready.  
- **Fencing:** leader epoch in every bind RPC.  
- Queue durable—leader crash must not lose ADMITTED requests.

### 5.9 Observability for interview whiteboards

| Dashboard | Metrics |
|-----------|---------|
| Capacity | free/allocated by SKU/cell; topology-fit free |
| Fairness | GPU-time by project vs weight; oldest queued age; floor debt |
| Health | pending binds, preempt/hour, reclaim/hour, Suspect nodes |
| Fragmentation | max fitable gang vs free GPUs |
| Nodes | HB lag, XID rates, drain flags, MIG occupancy |

### 5.10 Interface to training & inference systems

```text
Training controller / Inference autoscaler
   → Allocations API (gang, topology, preemptible)
   ← device list + lease_epoch
   → runtime uses devices; heartbeats via agents
   → on preempt signal: checkpoint / drain
   → Release
```

RM does **not** run NCCL or KV caches— it supplies **correct, fenced GPUs**.

### 5.11 Security & multi-tenancy

- Project authz on submit.  
- Image allowlists.  
- Network policies between jobs.  
- Prevent quota/credit exploits; admin roles audited.  
- Node agent attested; bind RPCs mTLS.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Allocation state machine + quotas (credits optional).  
2. Queues by SKU/priority + WFQ/DRF fairness.  
3. Gang atomic bind + fragmentation + topology.  
4. Preemption + leases/epochs.  
5. Scale: cells, HB fan-in, hierarchical admit.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Quotas, single-cell scheduler, gang, binpack, preempt P3, WFQ+aging |
| 10× | HA leader, SKU queues, topology prefs, spread policy |
| 100× | Multi-cell federation, defrag, MIG pools, HB gateways |
| 1,000× | Hierarchical scheduling, topology service, forecasts, credit ledger optional |

### 6.3 Top risks

1. Partial gang starts.  
2. Double bind on leader failover.  
3. Starvation of large topology-strict jobs.  
4. Silent SKU substitution.  
5. Mass reclaim on flaky network.  
6. Dual allocator with K8s.

### 6.4 One-sentence design

> A leader-owned, fairness-first NVIDIA GPU allocator that queues multi-SKU gangs under WFQ/DRF, binds devices atomically with topology awareness and leases, preempts with policy, and scales by cells—keeping quotas (and optional credits) consistent with machine assignment at the admit/bind boundary.

---

## 7. Deeper / Related Interview Questions

### 7.1 Fairness & quotas

**Q: Credits vs quotas vs priorities vs weights?**  
A: Credits = optional budget over time; quotas = hard caps; priorities = preemption/latency class; weights = fair share among eligible. Use quotas+weights+priorities; credits optional.

**Q: FIFO enough?**  
A: No—unequal projects and large gangs need WFQ/DRF + aging.

**Q: How does WFQ work at high level?**  
A: Each project accumulates virtual time inversely to weight; lowest virtual time runs next among runnable.

**Q: What is starvation?**  
A: Runnable job never starts; fix with floors and aging.

**Q: DRF vs GPU-only fair share?**  
A: DRF when CPU/RAM/NIC bottleneck; many ML cells are GPU-dominant so GPU share suffices for MVP.

### 7.2 Gang scheduling

**Q: Why all-or-nothing?**  
A: Distributed training and TP inference can’t progress with incomplete worker sets; partial start wastes GPUs.

**Q: How to bind atomically across nodes?**  
A: Central allocation TX on leader state store; agents only start after commit; epochs fence.

**Q: Placeholders / reservations?**  
A: Coalesce capacity for large gangs; don’t hold forever—TTL reservations.

**Q: What if one worker dies mid-job?**  
A: RM reclaims device; job controller decides fail vs elastic restart—not RM’s training logic.

### 7.3 Placement & fragmentation

**Q: Binpack or spread?**  
A: Binpack for batch training utilization; spread for HA inference replicas; choose per request.

**Q: Free GPUs but job won’t schedule—why?**  
A: Fragmentation, SKU mismatch, topology constraints, quota, fairness debt, affinity.

**Q: How to measure fragmentation?**  
A: Largest topology-feasible free gang vs total free GPUs.

**Q: Defragmentation strategies?**  
A: Packing bias; preempt soft jobs; intentional holes; MIG hygiene.

### 7.4 Topology (NVIDIA-specific)

**Q: Why NVLink domains matter?**  
A: TP training/serving assumes high BW/low latency; IB is slower—bad TP placement tanks MFU/TPOT.

**Q: Strict vs prefer?**  
A: Strict waits; prefer falls back with score penalty—product choice for job class.

**Q: Multi-rail IB?**  
A: Track rails; avoid mapping all heavy DP traffic onto one rail.

**Q: Same rack vs same leaf?**  
A: Model your fabric; leaf often the relevant failure/BW domain.

### 7.5 Preemption & leases

**Q: Who is preemptible?**  
A: Opt-in / low bands; never silent preempt of SLA inference without contract.

**Q: Grace period purpose?**  
A: Checkpoint & flush; reduce wasted compute.

**Q: Heartbeat timeout tuning?**  
A: >> network blip; << acceptable waste on dead node holding GPUs.

**Q: Fencing stale agents/leaders?**  
A: Lease epoch + leader epoch; ignore old binds.

### 7.6 MIG & SKUs

**Q: When mention MIG?**  
A: Many small interactive jobs on large GPUs; isolation better than time-slicing alone.

**Q: Can H100 satisfy A100 request?**  
A: Only with explicit substitution + accounting; else no.

**Q: Multi-SKU fairness?**  
A: Weights per SKU class or normalize by GPU-hour weight; avoid comparing raw counts across SKUs blindly.

### 7.7 Multi-region

**Q: Global queue or per-cell?**  
A: Global/hierarchical admit + cell place common; data locality may pin cell.

**Q: How to forecast wait time?**  
A: Queue ahead × historical service rates by SKU/size/topology class.

### 7.8 Reliability drills

**Q: Two leaders allocate same GPU?**  
A: Election + fencing token; conditional writes on device version.

**Q: Mass node HB loss**  
A: Don’t reclaim all immediately; Suspect; staged; operator panic button.

**Q: Poison job crashloop burning quota?**  
A: Retry budgets in caller; RM can rate-limit restarts; auto-pause project.

**Q: Quota double-spend?**  
A: Atomic counters keyed by req_id / CAS.

### 7.9 Comparison traps

**Q: How is this different from Kubernetes default scheduler?**  
A: First-class gangs, GPU fragmentation, NVIDIA topology, multi-tenant ML fairness, preemption economics, optional credits.

**Q: vs Yarn/Mesos?**  
A: Similar bones; GPU SKUs + NVLink/IB topology + training/inference gang semantics are the differentiators.

**Q: Why not auction every GPU-second?**  
A: Complexity & UX; weights + quotas approximate markets for MVP.

**Q: Same as OpenAI credits scheduler?**  
A: Same skeleton; NVIDIA interview stresses topology, MIG, and fairness even when credits are optional.

### 7.10 Algorithms

**Q: Data structures for free nodes?**  
A: Per-SKU buckets by free count; topology domain free maps; optional segment trees; bitsets for small cells.

**Q: Complexity of placement?**  
A: Aim sublinear via indexes; avoid O(nodes) scan each decision at 100×+.

**Q: How to pick preempt victims?**  
A: Minimize wasted progress; maximize freed fit; prefer low weight / recently checkpointed; skip non-preemptible.

### 7.11 Extra interviewer traps (high value)

- Split heartbeat QPS from submit QPS.  
- Show fragmentation vs free GPU counts.  
- What is the SoT for device ownership?  
- Partial gang start—why forbidden?  
- How do weights and quotas interact?  
- What fences an old scheduler leader?  
- How do you prevent large-job starvation?  
- Binpack vs spread for inference replicas?  
- Topology-strict wait vs bad fit.  
- Idempotency key on allocate—why?  
- How do you reclaim GPUs from a dead node?  
- Why not shard scheduler by GPU id randomly?  
- MIG—when mention?  
- How do you test fragmentation policies?  
- What utilization is “good” under gang constraints?  
- Dual allocator with K8s device plugin races.  
- Reserved inference pool vs on-demand training.  
- Optional credits must not replace fairness floors.

---

## 8. Appendices

### 8.1 Example schemas

```sql
CREATE TABLE projects (
  project_id UUID PRIMARY KEY,
  org_id UUID NOT NULL,
  weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  max_concurrent_gpus INT NOT NULL,
  floor_share DOUBLE PRECISION NOT NULL DEFAULT 0,
  credit_balance NUMERIC -- nullable if credits unused
);

CREATE TABLE allocation_requests (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL,
  sku TEXT NOT NULL,
  gpu_count INT NOT NULL,
  priority INT NOT NULL,
  preemptible BOOLEAN NOT NULL,
  placement TEXT NOT NULL,
  topology JSONB NOT NULL,
  state TEXT NOT NULL,
  reason_code TEXT,
  estimate_seconds INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE devices (
  id TEXT PRIMARY KEY, -- node:gpu_index
  node_id TEXT NOT NULL,
  sku TEXT NOT NULL,
  nvlink_domain TEXT NOT NULL,
  ib_leaf TEXT NOT NULL,
  mig_profile TEXT, -- null if full GPU
  lease_req_id UUID,
  lease_epoch BIGINT NOT NULL DEFAULT 0,
  state TEXT NOT NULL -- free|leased|draining|suspect
);

CREATE TABLE quota_ledger (
  project_id UUID PRIMARY KEY,
  reserved_gpus INT NOT NULL DEFAULT 0,
  running_gpus INT NOT NULL DEFAULT 0
);
```

### 8.2 Allocation spec example

```json
{
  "project_id": "p_123",
  "resources": {"sku": "H100", "gpus": 16, "cpus": 128, "mem_gb": 1024},
  "gang": true,
  "priority": "P2",
  "preemptible": true,
  "placement": "binpack",
  "topology": {"strict": true, "prefer_nvlink": true, "max_ib_leaves": 1},
  "estimate_seconds": 36000,
  "cell_prefer": ["us-east-1a"]
}
```

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Gang scheduling | All-or-nothing multi-GPU/multi-node start |
| WFQ | Weighted fair queueing |
| DRF | Dominant Resource Fairness |
| Binpack | Fill nodes tightly |
| Spread | Distribute for HA |
| Lease / epoch | Fenced ownership of a device |
| Preemption | Kill/pause lower priority to free capacity |
| Floor share | Minimum fair capacity over time |
| Fragmentation | Free GPUs unusable for large/topology-fit gangs |
| NVLink domain | High-BW intra-node/HGX GPU interconnect group |
| IB leaf | InfiniBand fabric domain for multi-node |
| MIG | Multi-Instance GPU partitioning |
| Cell | Regional scheduling domain |
| Suspect | Node HB degraded before reclaim |

### 8.4 Progressive scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Quotas, single scheduler, gang bind, WFQ, preempt P3 |
| 10× | HA leader, SKU queues, topology prefs, aging floors |
| 100× | Cells, HB gateways, defrag, MIG pools |
| 1,000× | Hierarchical admit, topology service, forecasts, optional credits |

### 8.5 Estimation cheat-sheet

```text
optional_credits ≈ gpus × hours × sku_weight

heartbeat_qps ≈ nodes / hb_interval
submit_qps ≠ heartbeat_qps ≠ gpu_count

free_gpus ≠ allocatable_for_gang_size_k
free_gpus ≠ topology_feasible_k
  fragmentation_ratio ≈ 1 - (max_fitable_gang_gpus / free_gpus)

utilization = allocated_gpus / total_gpus
(healthy often 60–80% under gang+topology constraints)

1,000 GPUs → 1,000,000 GPUs is 1,000× on inventory
control plane QPS scales with nodes/jobs, not MFU
```

### 8.6 Fairness pseudocode

```text
def pick_next(sku):
  for band in P0..P3:
    runnable = projects_with_waiting_jobs(band, sku) and under_ceiling
    if not runnable: continue
    # enforce floors first if project below floor and has demand
    ensure_floors(runnable)
    return min(runnable, key=lambda p: p.virtual_time)
```

### 8.7 Placement pseudocode

```text
def place(req):
  candidates = index.lookup(sku=req.sku, free>=..., topo=req.topology)
  scored = [score(c, req) for c in candidates]
  for c in sorted(scored):
    if bind_tx(c.devices, req.id): return c
  return None  # remain queued; set reason_code
```

### 8.8 Interview “say this” summary (60 seconds)

> I’d build a cell-leader NVIDIA GPU resource manager: admit under project quotas, fairly dequeue with WFQ and floors, atomically gang-bind devices with NVLink/IB topology awareness, fence ownership with lease epochs and agent heartbeats, and preempt only eligible workloads. Binpack training, spread HA inference, optional MIG for slices and optional credits for budgeting—but fairness stays mandatory as we scale from thousands to a million GPUs.

### 8.9 Reliability test plan

1. Kill scheduler leader mid-bind → no double lease; fencing holds.  
2. Kill node agent → Suspect → reclaim → caller notified.  
3. Fragmentation scenario → reason `FragmentedCapacity`; defrag/preempt soft jobs.  
4. Topology-strict vs scattered free → wait, don’t bad-pack.  
5. Preempt grace → checkpoint hook invoked; waste metrics recorded.  
6. Dual-submit idempotency key → one allocation.

### 8.10 Observability SLOs

| SLO | Example |
|-----|---------|
| Decision latency when free | p99 < 1s |
| Wrong double-bind | **0** |
| Starvation (floor breach) | alert |
| Mass reclaim events | alert |
| Pending BINDING age | bounded |

### 8.11 Related systems map

```text
Train Controller / Infer Autoscaler
        ↓ Allocations API
 Admit (quota[/credits]) → Fair Queues → Cell Scheduler Leader
                                ↓
                     Topology DB + Placement
                                ↓
                          Node Agents (NVIDIA)
                                ↓
                     Training runtimes / Inference engines
```

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| FIFO multi-tenant | Starvation / noisy neighbor |
| Credits replace fairness | Wealthy hog still needs floors |
| Partial gang start | Wasted GPUs / broken NCCL |
| Random placement | Topology performance collapse |
| HB updates on global OLTP at 100k nodes | Melt |
| K8s + custom dual bind | Split brain devices |
| Silent SKU upgrade | Wrong perf/cost |
| 80% util ⇒ healthy always | Ignore fragmentation & waste |

### 8.13 Reason code card

```text
InsufficientQuota
InsufficientCredits (optional)
FragmentedCapacity
TopologyUnsatisfied
WaitingFairShare
WaitingForGangReservation
SkuUnavailable
NodeSuspect
Preempted
BindingTimeout
```

### 8.14 Reserved pool math

```text
cell_gpus = G
inference_reserved = 0.2G
interactive_reserved = 0.05G
on_demand = G - reserved

Admission to reserved pools still checks project ACLs + local pool free list
On-demand cannot steal reserved unless policy panic brownout
```

---

*End of design doc. Open with §1 gang+fairness+topology scope; whiteboard §3.2–3.7 WFQ/gang/topology/preempt/leases; close with invariants §5.1 and traps §7.11.*
