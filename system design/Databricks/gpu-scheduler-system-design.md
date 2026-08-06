# System Design: GPU Scheduler

> **Focus areas:** GPU pools · Gang scheduling · Preemption · Fair share · Quotas · Job placement · Fragmentation · Multi-tenant
> **Style:** Cluster scheduler design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:**
> **Interview theme:** Databricks — GPU cluster scheduling for ML workloads; fairness, preemption, gang scheduling hooks Correct arithmetic, split control-plane vs GPU-time load classes, starvation prevention, resolved ownership of credit vs placement

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the scheduler**—who consumes scarce accelerators, how credits buy fairness, and which gang/preemption semantics are non-negotiable.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits jobs? | ML researchers, training pipelines, inference services, batch evals | Multiple queues/classes with different SLOs |
| F2 | Resource types? | GPU SKUs: A100-40, A100-80, H100, L40S; CPU/RAM/NIC also constrained | Inventory by SKU; not fungible across generations |
| F3 | Job shapes? | 1–N GPUs; multi-node training common | **Gang scheduling** all-or-nothing |
| F4 | Credits? | Orgs buy/earn credits; jobs spend GPU-seconds × SKU weight | Ledger + reservation + settle |
| F5 | Fairness? | Weighted fair share by org/project; prevent starvation | WFQs / dominant resource fairness variants |
| F6 | Priorities? | Interactive debug > training > best-effort batch | Priority bands + preemption rules |
| F7 | Preemption? | Yes for low priority; checkpoints assumed for training | Preemptible flag; grace period |
| F8 | Placement? | Binpack for utilization; spread for HA inference | Policy per job class |
| F9 | Multi-region? | Capacity in several regions; soft affinity | Federated schedulers or global queue |
| F10 | Quotas? | Hard concurrency + soft credit burn rate | Admission control before placement |

**MVP functional scope (lock with interviewer):**

1. Submit job spec: image, command, GPU count/SKU, duration estimate, priority, preemptible.  
2. Credit check + soft reservation at admit.  
3. Schedule onto nodes with gang semantics for multi-GPU.  
4. Lease + heartbeat from agents; reclaim on timeout.  
5. Preempt best-effort under pressure with grace.  
6. Fairness across projects via weighted shares + credits.  
7. Observe: queue time, GPU utilization, fragmentation, credit burn.

**Out of MVP:**

- Fully automatic multi-cloud arbitrage  
- Topology-aware NVLink/IB scheduling perfection (design hooks)  
- Spot market dynamic pricing UI  
- MPI co-design beyond “gang + same rack preference”

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Scheduling latency (decision) | Fast for interactive | p50 < 100ms, p99 < 1s for fit check when capacity free |
| N2 | Queue wait | Workload-dependent | Publish expected wait; interactive SLO separate |
| N3 | Utilization | High but not at fairness expense | 60–80% allocated GPU-time common healthy band |
| N4 | Correctness | No double-allocate GPU | Lease fencing; single allocator ownership |
| N5 | Credit integrity | No double spend / silent free GPUs | Ledger invariants; settle on terminal states |
| N6 | Availability | Control plane HA | 99.9% submit/status; agents reconnect |
| N7 | Isolation | No cross-project GPU theft | cgroup/MIG/device plugin + authz |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User submits 8×H100 training → credits reserved → gang placed on one fabric domain → runs → settle burn.  
2. Interactive 1×GPU notebook → high priority → quick start; may preempt batch.  
3. Cluster full → job queued; fairness eventually starts it.  
4. Node dies → lease expires → reschedule remaining gang (policy: fail or restart).  
5. User cancels → release reservation; partial credit refund policy.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Gang 64 GPUs but only 60 free scattered | Wait (don’t partial start) |
| Fragmentation: 1 GPU free on many nodes, need 8 on one | Binpack / defrag / wait |
| Credit race two submits | Atomic reserve in ledger |
| Underestimated duration | Soft continue if credits remain; else preempt/kill per policy |
| Heartbeat miss (network blip) | Grace > RTT; then reclaim |
| Preempt during non-checkpointable section | Grace signal; extend if policy; else kill |
| SKU mismatch (asked A100, only H100) | Optional upgrade path with higher credit weight |
| Starvation of low weight org | Floor share / aging |
| Split brain two schedulers | Single leader allocator per region/cell |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPUs total | 1,000 | 10,000 | 100,000 | 1,000,000 |
| Nodes | 125 (8-GPU) | 1,250 | 12,500 | 125,000 |
| Concurrent jobs | 500 | 5,000 | 50,000 | 500,000 |
| Submits / day | 20K | 200K | 2M | 20M |
| Peak submit QPS | ~5 | ~50 | ~500 | ~5K |
| Scheduling decisions /s | ~20 | ~200 | ~2K | ~20K |
| Orgs / projects | 100 | 1K | 10K | 100K |
| SKUs | 3 | 5 | 8 | 12+ |
| Regions | 1 | 2 | 4 | 8+ |
| Credit txs / day | ~100K | ~1M | ~10M | ~100M |

**What each jump forces:**

- **10×:** Leader-elected scheduler; sharded job queues per SKU; richer fairness.  
- **100×:** Cell/region federation; approximate packing heuristics; credit ledger service.  
- **1,000×:** Hierarchical scheduling (global admit → regional place); topology databases; aggressive fragmentation control.

### 1.5 Etc. (Constraints & Assumptions)

- Training jobs are **checkpointable** if preemptible.  
- Inference may require non-preemptible reservations.  
- Credits are **internal currency** mapped to GPU-seconds × SKU multiplier.  
- We schedule GPUs; cluster manager (K8s-like) starts pods—**allocator owns GPU binding**.

**Scope statement:**

> Design a credit-aware GPU scheduler for multi-tenant ML workloads: quotas and weighted fairness, all-or-nothing gang placement across SKUs, preemption with leases/heartbeats, binpack vs spread policies, and progressive scale from 1K to 1M GPUs without double-allocation or credit double-spend.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Job **submit/status** API | ~5/s peak | ~5K/s | Control plane |
| **Scheduling evaluations** | ~20/s | ~20K/s | Fit + fairness |
| Agent **heartbeats** | ~125/s (nodes) | ~125K/s | Distinct from submits |
| Credit **ledger txs** | ~10/s | ~10K/s | Reserve/settle |
| Actual **GPU work** | 1000 GPUs busy | 1M | Not request QPS |

**Deal-breaker:** conflating heartbeat QPS with submit QPS or “cluster QPS.”

### 2.2 Credit arithmetic

```text
SKU weights (example):
  L40S: 1.0 credit / GPU-hour
  A100-80: 1.5
  H100: 3.0

Job: 8×H100 × 10 hours = 8 × 10 × 3.0 = 240 credits

Org monthly grant: 10,000 credits
Max concurrent reserved: policy e.g. 20% of monthly in-flight
```

### 2.3 Utilization & fragmentation

```text
Cluster: 1000 GPUs
Allocated: 800 → 80% allocation
But effective MFU may be lower (application inefficiency—out of scope)

Fragmentation example:
  100 nodes × 8 GPU; free GPUs: 1 per node on 80 nodes = 80 free
  Largest gang fit: 1 (or few) → free≠allocatable for 8-GPU jobs
```

### 2.4 Heartbeat bandwidth

```text
125 nodes × 1 HB / 5s = 25 HB/s baseline (or 125/s if 1Hz)
1,000×: 125K nodes × 0.2 Hz = 25K HB/s
→ shard agents by cell; HB to local agent gateway not global monolith
```

### 2.5 Scheduling complexity

```text
Naïve: each schedule scan all nodes O(N)
At 12.5K nodes: need indexes by free GPU count / SKU / topology
Binpack: prefer most-full fit; Spread: prefer least-full
```

### 2.6 Preemption rate

```text
If interactive needs 5% of capacity bursts:
  expect preemption events proportional to oversubscription of preemptible pool
Track: preemptions/hour, wasted GPU-minutes since last checkpoint
```

---

## 3. High-Level Design

### 3.1 Job model

```text
Job:
  job_id, project_id, org_id
  sku, gpu_count, min_nodes, max_nodes
  gang: true/false
  priority: P0 interactive | P1 training | P2 batch
  preemptible: bool
  estimate_duration
  placement: binpack | spread | topology_prefer
  checkpoint_signal_timeout
```

**States:**

```text
ADMITTED → QUEUED → BINDING → RUNNING → SUCCEEDED|FAILED|CANCELLED|PREEMPTED
              ↑                     |
              +------ requeue ------+
```

### 3.2 Credit ledger

**Operations:**

| Op | Meaning |
|----|---------|
| `Reserve(job, amount)` | Hold credits at admit (amount from estimate × weight) |
| `IncreaseReserve` | Duration extended |
| `Settle(job, actual)` | Burn actual; release unused hold |
| `Release` | Cancel before run |
| `TopUp` | Admin/purchase |

**Invariants:**

- `available = balance - reserved ≥ 0` always.  
- Reserve is atomic with admit (compare-and-swap).  
- Settle idempotent on `job_id`.  
- **No GPU bind without reserve** (or explicit free-tier flag).

**Ownership:** Ledger service owns money; scheduler owns machines; binding requires both.

### 3.3 Queues & fairness

**Queue structure:**

```text
per (region, sku):
  priority bands P0, P1, P2
  within band: weighted fair queue by project
```

**Weighted fair sharing:**

```text
project weight w_i (from credits purchased / admin)
fair share = w_i / Σw * cluster_gpu_capacity
deficit/lag counters (WFQ / DRF-inspired)
aging: wait_time boost to prevent starvation
```

**DRF note:** When jobs need GPU+CPU+RAM, dominant share can matter; MVP often GPU-dominant.

**Credits vs weights:**

| Mechanism | Role |
|-----------|------|
| Credits | Economic budget over time (who can run at all) |
| Weights / fair share | Instantaneous sharing of scarce capacity among eligible jobs |
| Priority bands | Latency class / preemption eligibility |

**Deal-breaker:** only FIFO ignoring weights → noisy-neighbor; only credits without floors → starvation when wealthy jobs hog.

### 3.4 Gang scheduling

```text
need = job.gpu_count
if cannot allocate ALL GPUs atomically:
  leave QUEUED  # never start partial gang
else:
  bind all devices in one transaction (etcd/DB conditional update)
  start all workers
```

**Multi-node:** allocate set of nodes with locality prefs (same rack/IB domain).

**All-or-nothing bind transaction:**

```text
TX:
  for device in chosen:
    if device.lease_owner != null: abort
    device.lease_owner = job_id; epoch++
COMMIT → launch
```

### 3.5 Placement: binpack vs spread

| Policy | Algorithm | Good for | Bad for |
|--------|-----------|----------|---------|
| **Binpack** | Prefer nodes with least remaining free that still fit | Training util; reduce fragments | Correlated failure |
| **Spread** | Prefer nodes with most free / across racks | Inference HA | Fragmentation |
| **Topology** | Minimize hop / same NVLink domain | Large training | May wait longer |

**Fragmentation fighting:**

- Prefer packing small jobs into leftovers only if they don’t block higher-priority gangs forever.  
- Optional **defrag**: drain soft jobs to coalesce free contiguous GPUs.  
- MIG/partitioning for small interactive slices on big GPUs (advanced).

### 3.6 Preemption policy

```text
when P0 needs capacity:
  candidates = running preemptible jobs in lower bands
  score by: credits weight, progress since checkpoint, size fit
  send SIGTERM-equivalent; grace G seconds
  if not exited: hard kill; mark PREEMPTED; settle partial; requeue optional
```

**Non-preemptible:** inference SLAs, paid reserved capacity.

**Starvation prevention:** limit fraction of cluster preemptible; guarantee floor share time windows.

### 3.7 Leases & heartbeats

```text
Node agent:
  heartbeat every T seconds with: free GPUs, running job health, versions
Scheduler:
  if now - last_hb > timeout: mark node Suspect → NotReady
  reclaim leases; reschedule gangs per policy
```

**Fencing:** device lease includes epoch; agent refuses old epoch binds.

### 3.8 Multi-SKU queues

- Separate free lists & queues per SKU.  
- Optional **substitution graph**: H100 can satisfy A100 request at higher credit rate if user opts in.  
- Don’t silently substitute—billing surprise is a deal-breaker.

### 3.9 Multi-region capacity

```text
Global Admit (credits + org policy)
   → choose region (affinity, capacity forecast, data locality)
      → Regional Scheduler (placement + leases)
```

**Avoid:** dual regional binders for same job without fencing.

### 3.10 APIs

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/jobs` | Submit (idempotency key) |
| GET | `/v1/jobs/{id}` | Status, placement, credits |
| POST | `/v1/jobs/{id}:cancel` | Cancel |
| POST | `/v1/jobs/{id}:signal` | Checkpoint complete, etc. |
| GET | `/v1/capacity` | Free/queued by SKU |
| GET | `/v1/credits` | Balance/reserved |
| POST | `/v1/credits/topup` | Admin |

---

## 4. Architecture Diagram

### 4.1 Control plane

```text
+-------------+     +------------------+     +-----------------+
| Users / CI  |---->| API Gateway      |---->| Job Service     |
+-------------+     +--------+---------+     +--------+--------+
                             |                        |
                             v                        v
                    +--------+---------+     +--------+--------+
                    | Credit Ledger    |     | Scheduler Leader|
                    +------------------+     +--------+--------+
                                                      |
                     +--------------------------------+----------------+
                     v                                v                v
              Queue Shards                      Placement         Node View
              (sku,priority)                    Engine            (allocations)
                                                     |
                                                     v
                                              +------+------+
                                              | Node Agents |
                                              +-------------+
```

### 4.2 Sequence: admit + gang bind

```text
Client → API: CreateJob(8xH100)
API → Ledger: Reserve(240 credits)  # estimate
Ledger → OK hold_id
API → Scheduler: Enqueue(job)
Scheduler: fairness says runnable; search placement
Scheduler: TX bind 8 devices same topology
Scheduler → Agents: Start(job, lease_epoch)
Agents → HB running
Job ends → Scheduler → Ledger: Settle(actual)
```

### 4.3 Sequence: preemption

```text
P0 job needs 2 GPUs; none free
Scheduler: select preemptible P2 job Jlow on node
Agent: Preempt(Jlow, grace=30s)
Jlow checkpoints / exits
Scheduler: unbind → bind P0 → start
Jlow: PREEMPTED; optional auto-requeue; settle partial credits
```

### 4.4 Credit state machine

```text
balance ──TopUp──► balance
   │
   ├──Reserve──► reserved↑ available↓
   │               │
   │               ├──Settle burn──► reserved↓ balance↓
   │               └──Release────────► reserved↓ available↑
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | A GPU device has ≤1 lease owner | Conditional bind TX; epoch fencing |
| R2 | Gang either fully bound or not running | Atomic multi-device bind |
| R3 | No bind without credit reserve (policy) | Admit gate |
| R4 | Credit reserve/settle idempotent | `job_id` keys |
| R5 | Dead agent → devices reclaimed | HB timeout + fence |
| R6 | Single scheduler leader per cell | Raft/etcd election |
| R7 | Preempt only eligible jobs | Flags + policy engine |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| Scheduler leader crash | Follower elects; state in etcd/DB; agents continue |
| Ledger down | Fail admit; running jobs continue; settle queue |
| Agent flapping | Intermediate Suspect state; avoid mass preemption |
| Partial gang start bug | **P0 incident**—integration tests must catch |
| Clock skew on leases | Use leader monotonic time / logical timeout |

### 5.2 Scalability

**1×:** Monolithic scheduler + Postgres ledger; 1K GPUs fine.

**10×:** Leader election; queue by SKU; indexed free-GPU heaps.

**100×:** Regional cells; sharded job stores; approximate fair-share counters; optimistic binding with conflict retry.

**1,000×:** Hierarchical global queueing; capacity forecasts; topology service; per-cell allocators; HB aggregators.

**Backpressure:** if BINDING backlog high, stop starting more until agents catch up.

### 5.3 Maintainability

- Deterministic simulator for packing/fairness.  
- Shadow scheduling for policy changes.  
- Clear reason codes: `InsufficientCredits`, `FragmentedCapacity`, `WaitingForGang`, `Preempted`.  
- Audit log for every bind/preempt/settle.

### 5.4 Ownership resolution (contradictions to avoid)

| Concern | Owner |
|---------|-------|
| Who can afford to run | Credit ledger |
| Who runs next among eligible | Fairness / queues |
| Where it runs | Placement engine |
| What is allocated now | Allocation map (leader) |
| Process lifecycle | Node agent / kubelet-like |
| Refund policy | Product + ledger config |

**Contradiction trap:** K8s default scheduler + external GPU allocator both binding—pick one SoT for device leases.

### 5.5 Starvation & fairness deep dive

**Problems:**

1. High-weight org always wins → floors.  
2. Large gangs wait forever behind small jobs → gang-aware reservation / blocking.  
3. Interactive hogs → separate reserved pool %.  

**Mechanisms:**

- **Floor share:** min % over sliding window.  
- **Ceiling:** max burst concurrency.  
- **Aging:** priority boost with wait.  
- **Reservation for gangs:** speculative hold of freeing GPUs for short window.

### 5.6 Estimation vs actual billing

```text
Reserve on estimate_duration
Meter actual GPU-seconds from bind→unbind
Settle = min(policy_max, actual) × weight
If actual >> estimate: warn; require top-up or preempt
```

### 5.7 Security & multi-tenancy

- Project authz on submit.  
- Image allowlists.  
- Network policies between jobs.  
- Prevent credit transfer exploits; admin roles audited.

---


### 5.8 Topology-aware placement (IB / NVLink)

Large training jobs suffer if workers span slow network domains. Maintain a topology DB:

```text
region → zone → rack → nvlink_domain → node → gpu
```

**Placement preferences (soft then hard):**

1. Same NVLink domain for ≤8 GPU jobs on DGX-class nodes.  
2. Same rack / IB leaf for multi-node.  
3. Same zone; avoid cross-zone unless capacity forces.  

**Trade-off:** stricter topology → longer queue waits. Expose `topology_strict: bool` on job spec.

### 5.9 Reserved pools vs on-demand

| Pool | Use | Preemptible? |
|------|-----|--------------|
| Interactive reserved (5–10%) | Notebooks, debug | No |
| Training on-demand | Default gangs | Optional |
| Batch scavenger | Best-effort | Yes |

Credits still apply inside reserved pools; reservation buys **latency**, not free compute (unless product says otherwise).

### 5.10 Checkpoint-aware preemption scoring

```text
victim_score = gpu_hours_since_checkpoint × weight_factor × (1 - priority_band_norm)
prefer victims with recent checkpoints and low weight
avoid victims in first few minutes after start (warmup amortization)
```

Emit metrics: `wasted_gpu_hours_on_preempt`.

### 5.11 Control-plane HA details

- Scheduler leader in etcd/Raft; allocation map stored as versioned keys per device.  
- On failover: rebuild in-memory indexes from store; agents continue; new binds wait until leader ready.  
- **Fencing:** leader epoch in every bind RPC; agents reject stale leaders.  
- Job queue durable in DB/Kafka—leader crash must not lose ADMITTED jobs.

### 5.12 Observability for interview whiteboards

| Dashboard | Metrics |
|-----------|---------|
| Capacity | free/allocated GPUs by SKU/region; fragmentation ratio |
| Fairness | GPU-time by project vs weight; oldest queued age |
| Health | pending binds, preempt/hour, reclaim/hour |
| Money | credits burned/held; reject reasons |
| Nodes | HB lag, GPU error rates, drain flags |

**Reason codes on jobs** make support and UX explain “why waiting.”

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Job state machine + credit reserve/settle.  
2. Queues by SKU/priority + weighted fairness.  
3. Gang atomic bind + fragmentation.  
4. Preemption + leases.  
5. Scale: cells, HB fan-in, hierarchical admit.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Reserve/settle, single-region scheduler, gang, LRU-ish binpack, preempt P2 |
| 10× | HA leader, SKU queues, aging fairness |
| 100× | Multi-region federation, topology prefs, defrag |
| 1,000× | Hierarchical scheduling, HB aggregation, forecasts |

### 6.3 Top risks

1. Partial gang starts.  
2. Double bind on leader failover.  
3. Credit double-spend races.  
4. Starvation of large jobs via fragmentation.  
5. Silent SKU substitution.

### 6.4 One-sentence design

> A leader-owned, credit-gated GPU allocator that fairly queues multi-SKU gangs, binds devices atomically under leases, preempts with policy, and scales by regional cells—keeping money (ledger) and machines (placement) consistent at the admit/bind boundary.

---

## 7. Deeper / Related Interview Questions

### 7.1 Credits & quotas

**Q: Credits vs quotas vs priorities—how do they differ?**  
A: Credits = budget over time; quotas = concurrency/rate caps; priorities = scheduling/preemption class. Use all three.

**Q: When do you reserve credits?**  
A: At admit, based on estimate × SKU weight; settle on terminal state.

**Q: What if estimate is wrong?**  
A: Soft extend with top-up; or preempt when reserve exhausted—product choice.

**Q: How to prevent double spend?**  
A: Atomic ledger rows keyed by job_id; conditional updates on available balance.

**Q: Refunds on preemption?**  
A: Charge for used GPU-seconds only; release unused reserve; optional SLA credits.

### 7.2 Fairness

**Q: FIFO enough?**  
A: No—unequal project sizes and large gangs need WFQ/DRF + aging.

**Q: How does weighted fair queue work at a high level?**  
A: Each project accumulates virtual time inversely to weight; lowest virtual time runs next among runnable.

**Q: What is starvation?**  
A: Runnable job never starts; fix with floors and aging.

**Q: DRF vs GPU-only fair share?**  
A: DRF when CPU/RAM bottleneck; many ML clusters GPU-dominant so GPU share suffices MVP.

### 7.3 Gang scheduling

**Q: Why all-or-nothing?**  
A: Distributed training can’t make progress with incomplete worker sets; partial start wastes GPUs.

**Q: How to bind atomically across nodes?**  
A: Central allocation TX on leader state store; agents only start after commit; epochs fence.

**Q: Gang vs gang-scheduling with placeholders?**  
A: Placeholders/reservations can coalesce capacity; careful to not hold forever.

**Q: What if one worker dies mid-training?**  
A: Policy: fail job, or elastic restart from checkpoint; release/rebind GPUs.

### 7.4 Placement & fragmentation

**Q: Binpack or spread?**  
A: Binpack for batch training utilization; spread for HA replicas; choose per job.

**Q: Free GPUs but job won’t schedule—why?**  
A: Fragmentation, SKU mismatch, topology constraints, credit holds, affinity.

**Q: How to measure fragmentation?**  
A: Largest contiguous free gang fitable vs total free GPUs ratio.

**Q: Defragmentation strategies?**  
A: Prefers packing; migrate/preempt soft jobs; leave intentional holes for upcoming gangs (reservation).

### 7.5 Preemption & leases

**Q: Who is preemptible?**  
A: Jobs that opt in / low priority bands; never silent preempt of reserved inference without contract.

**Q: Grace period purpose?**  
A: Checkpoint & flush; reduce wasted compute.

**Q: Heartbeat timeout tuning?**  
A: >> network blip RTT; << acceptable waste on dead node holding GPUs.

**Q: Fencing stale agents?**  
A: Lease epoch; ignore start requests with old epoch; generation numbers.

### 7.6 Multi-region & SKUs

**Q: Global queue or per-region?**  
A: Global admit + regional place common; data locality may pin region.

**Q: Can H100 satisfy A100 request?**  
A: Only with explicit substitution + pricing; else no.

**Q: How to forecast wait time?**  
A: Queue ahead × historical service rates by SKU/size class.

### 7.7 Reliability drills

**Q: Two leaders allocate same GPU?**  
A: Prevent with election + fencing token; conditional writes on device version.

**Q: Ledger settles twice?**  
A: Idempotent settle by job_id.

**Q: Mass node HB loss (network)**  
A: Don’t reclaim all immediately; panic button; staged Suspect.

**Q: Poison job crashloop burning credits?**  
A: Retry budgets; backoff; auto-pause project; alerts.

### 7.8 Comparison traps

**Q: How is this different from Kubernetes default scheduler?**  
A: Credits, multi-tenant ML fairness, first-class gangs, GPU fragmentation, preemption economics.

**Q: How is this different from Yarn/Mesos?**  
A: Similar bones; GPU SKUs + credit ledger + training gang semantics are the differentiators to emphasize.

**Q: Why not auction every GPU-second?**  
A: Complexity & UX; credits + fair share approximates markets for MVP.

### 7.9 Algorithms

**Q: What data structure for free nodes?**  
A: Per-SKU buckets by free count; segment trees / fenwick optional; topology graphs for IB domains.

**Q: Complexity of placement?**  
A: Aim sublinear via indexes; avoid O(nodes) scan each decision at 100×+.

**Q: How to pick preempt victims?**  
A: Minimize killed GPU-hours of progress; maximize freed fit; prefer low weight / recently checkpointed.

### 7.10 Extra interviewer traps (high value)

- Split heartbeat QPS from submit QPS.  
- Show credit math for multi-GPU × hours × weight.  
- What is the SoT for device ownership?  
- Partial gang start—why forbidden?  
- How do credits and fair-share interact?  
- What fences an old scheduler leader?  
- How do you prevent large-job starvation?  
- Binpack vs spread for inference replicas?  
- Idempotency key on submit—why?  
- What happens when estimate << actual?  
- How do you reclaim GPUs from a dead node?  
- Why not shard scheduler by GPU id randomly?  
- MIG/partitioning—when mention?  
- How do you test fragmentation policies?  
- What utilization is “good” vs overcommitted myth?

---

## Appendix A — Example schemas

```sql
CREATE TABLE credit_accounts (
  project_id UUID PRIMARY KEY,
  balance NUMERIC NOT NULL,
  reserved NUMERIC NOT NULL DEFAULT 0,
  weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  CHECK (balance >= 0 AND reserved >= 0 AND balance >= reserved)
);

CREATE TABLE credit_ledger (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID NOT NULL,
  job_id UUID,
  op TEXT NOT NULL, -- topup|reserve|settle|release
  amount NUMERIC NOT NULL,
  idempotency_key TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL,
  sku TEXT NOT NULL,
  gpu_count INT NOT NULL,
  priority INT NOT NULL,
  preemptible BOOLEAN NOT NULL,
  state TEXT NOT NULL,
  estimate_seconds INT NOT NULL,
  reserved_credits NUMERIC NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE devices (
  id TEXT PRIMARY KEY, -- node:gpu_index
  node_id TEXT NOT NULL,
  sku TEXT NOT NULL,
  lease_job_id UUID,
  lease_epoch BIGINT NOT NULL DEFAULT 0,
  state TEXT NOT NULL -- free|leased|draining
);
```

## Appendix B — Job spec example

```json
{
  "project_id": "p_123",
  "image": "ghcr.io/acme/train:1.2",
  "command": ["python", "train.py"],
  "resources": {"sku": "H100", "gpus": 8, "cpus": 64, "mem_gb": 512},
  "gang": true,
  "priority": "P1",
  "preemptible": true,
  "placement": "binpack",
  "estimate_seconds": 36000,
  "region_prefer": ["us-east-1"]
}
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Ledger reserve/settle, single scheduler, gang bind, preempt P2 |
| 10× | HA leader, SKU queues, WFQ+aging |
| 100× | Regional cells, topology, fragmentation metrics/defrag |
| 1,000× | Hierarchical admit, HB aggregation, capacity forecasting |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Gang scheduling | All-or-nothing multi-GPU/multi-node start |
| Credit | Internal currency for GPU-time × SKU weight |
| Reserve | Hold credits before/during run |
| Settle | Finalize burn on completion |
| Binpack | Fill nodes tightly |
| Spread | Distribute for HA |
| Lease / epoch | Fenced ownership of a device |
| Preemption | Kill/pause lower priority to free capacity |
| Floor share | Minimum fair capacity over time |
| Fragmentation | Free GPUs unusable for large gangs |
| DRF | Dominant Resource Fairness |
| Cell | Regional scheduling domain |

## Appendix E — Estimation cheat-sheet

```text
credits ≈ gpus × hours × sku_weight

heartbeat_qps ≈ nodes / hb_interval
submit_qps ≠ heartbeat_qps ≠ gpu_count

free_gpus ≠ allocatable_for_gang_size_k
  fragmentation_ratio ≈ 1 - (max_fitable_gang_gpus / free_gpus)

utilization = allocated_gpus / total_gpus
(healthy often 60–80% under gang constraints)

1,000 GPUs → 1,000,000 GPUs is 1,000× on inventory
control plane QPS scales with nodes/jobs, not MFU
```

---

*End of design doc. Open with §1 credits+gang scope; whiteboard §3.2–3.6 ledger/fairness/gang/preempt; close with invariants §5.1 and traps §7.*
