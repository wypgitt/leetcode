# System Design: Redundant Cloud-Compute Cluster

> **Focus areas:** Job scheduling · Replication / redundancy · Failure domains · Autoscaling · Placement · Health checking · Preemption · Multi-AZ/region · Resource fragmentation · Control vs data plane  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct capacity math, explicit failure-domain replication, scheduler fairness vs packing, deal-breakers for “single master + hope” at fleet scale  
> **Interview theme:** Google L5+ Borg/Kubernetes-class — run customer compute with high availability, efficient packing, and graceful failure across machines, racks, and zones

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

Goal: **bound the product**—a **redundant cloud-compute cluster** that accepts jobs/services, **schedules** them onto machines, maintains **redundancy across failure domains**, **autoscale**s capacity, and stays operable under partial outages.

### 1.0 What this is / is not

| Dimension | **Redundant cloud-compute cluster (this doc)** | Not this |
|-----------|------------------------------------------------|----------|
| Primary job | Schedule & run containers/VMs with HA policies | Build the guest OS or customer app |
| Success | Utilization + availability + fair latency to schedule | Perfect bin-pack with zero fragmentation forever |
| Control plane | Highly available scheduler/API | Single laptop minikube |
| Failure model | Machine, rack, AZ, (region) | Ignore correlated failures |
| Workloads | Mix: services (long) + batch (finite) | Only serverless functions (related, out of MVP) |

**Scope statement:** Design a multi-tenant compute cluster with scheduling, placement constraints, health-driven replacement, autoscaling, and redundancy across failure domains—progressive to mega-cluster scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Workload unit? | Containers (K8s-like) + optional VMs | Pod/alloc abstraction |
| F2 | Redundancy model? | N replicas; spread across domains | Topology-aware anti-affinity |
| F3 | Job types? | Stateless services + batch + stateful (PVC hooks) | Separate queues / priority |
| F4 | Scheduling API? | Declare CPU/mem/GPU, constraints, replicas | Declarative DesiredState |
| F5 | Autoscaling? | Cluster node autoscaling + HPA-like replica | Two loops |
| F6 | Health? | Liveness/readiness; replace unhealthy | Node + pod health planes |
| F7 | Preemption? | Yes — production > batch | Priority + PDB |
| F8 | Multi-AZ? | Yes within region MVP; multi-region Phase 1.5 | Failure domain labels |
| F9 | Multi-tenant? | Yes — quotas, isolation | Namespaces + cgroup/hypervisor |
| F10 | Rolling updates? | Surge / maxUnavailable | Deployment controller |
| F11 | Spot/preemptible? | Optional cheaper pool | Taints/tolerations |
| F12 | Observability? | Metrics, logs, events for schedule decisions | Audit why pending |

**MVP functional scope:**

1. API: create/update/delete Deployments/Jobs with resource requests/limits.  
2. Scheduler binds pods to nodes respecting resources + spread.  
3. Kubelet-like agent runs/reconciles pods; reports health.  
4. Controllers maintain replica counts; replace dead pods.  
5. Node autoscaler adds/removes nodes from pools.  
6. Failure domains: at least `node`, `rack`, `zone`.  
7. Priority/preemption for production vs batch.  
8. Quotas per tenant; basic network/storage hooks.  
9. Control plane HA (multi-master etcd-like).

**Out of MVP:**

- Global multi-region active-active single cluster (federation Phase 2)  
- Perfect gang scheduling for all MPI (support subset)  
- Live VM migration as only HA story  
- Customer-facing serverless + this cluster as one design  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Control plane availability | Survive AZ loss | 99.99% API; etcd quorum |
| N2 | Schedule latency | Interactive feel for small pods | p50 < 1s; p99 < 5–10s baseline |
| N3 | Detection of dead node | Bound blast | ≤ 30–60s to mark NotReady |
| N4 | Replacement time | New pod scheduled + started | SLO by class (prod < few min) |
| N5 | Utilization | Efficient packing | 60–80% CPU allocatable (policy) |
| N6 | Isolation | No noisy neighbor crush | Limits + optionally hypervisor |
| N7 | Scalability | Large fleets | Hierarchical / sharded scheduler at 100× |
| N8 | Consistency | Desired→actual converge | Level-triggered reconciliation |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Deploy web svc 3 replicas, anti-affinity zone → scheduled 1 per AZ → healthy.  
2. Load ↑ → HPA replicas 3→12 → pending → node autoscaler adds nodes → bind.  
3. Node dies → NotReady → pods rescheduled to other domains → capacity OK.  
4. Batch job preempted by prod → batch requeued → finishes later.  
5. Rolling update surge 1 → new pods up → old terminated.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| etcd quorum loss | API read-only/unavailable; agents keep running last desired |
| Split brain | Raft/etcd prevents dual writers |
| All replicas one rack (bug) | Topology spreader + admission validation |
| GPU fragmentation | Bin-pack / topology aware; dedicated pools |
| Thundering herd reschedule | Rate-limit eviction; jitter |
| Bad readiness always fail | CrashLoop backoff; don’t infinite node scale |
| Autoscaler flap | Cooldown; stabilization window |
| Disk pressure | Evict lowest priority; node taint |
| Kernel panic correlated (bad image) | Canary node pools; surge |
| Pending forever | Events: unschedulable reasons; quota vs capacity |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Nodes | 500 | 5K | 50K | 500K |
| Pods | 10K | 100K | 1M | 10M |
| Schedules/s peak | 50 | 500 | 5K | 50K |
| Deployments | 2K | 20K | 200K | 2M |
| Zones | 3 | 3–4 | 6+ | many cells |
| Tenants | 50 | 500 | 5K | 50K |
| Control plane QPS | 1K | 10K | 100K | cell-local APIs |
| Node check-ins/s | 500 | 5K | 50K | sharded |

**What each jump forces:**

- **10×:** Priority queue scheduler optimizations; watch caching; zone spread enforced.  
- **100×:** Scheduler sharding / gang of schedulers; cell architecture; hierarchical autoscaling.  
- **1,000×:** Cluster federation / Borg-like cells; no single global scheduler; push health aggregation.

### 1.5 Etc. (Constraints & Assumptions)

- Machines heterogeneous pools: general, memory, GPU.  
- Network/storage exist as plugins (CNI/CSI); design interfaces, not full SDN.  
- Power/rack topology known via cluster inventory.  
- “Redundant” means **workload HA policies + control plane HA**, not RAID on one box.

**Scope statement to repeat back:**

> Design a redundant cloud-compute cluster: HA control plane, topology-aware scheduler, health-driven reconciliation, dual autoscaling (pods + nodes), preemption, and progressive scale from hundreds to hundreds of thousands of nodes via cells/sharding.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Capacity

```text
Node: 64 cores, 256 GB RAM
Allocatable ≈ 60 cores, 240 GB (system reserved)
Pods avg request: 0.5 CPU, 2 GB → CPU binds first → ~120 pods/node theoretical
Practical with fragmentation + daemonsets ≈ 60–90 pods/node
500 nodes → ~30K–45K pods
```

### 2.2 Redundancy tax

```text
Service wants 3 replicas across 3 zones
Failure of 1 AZ: still 2/3 capacity
If each replica needs 2 CPU: reserve 6 CPU across zones
N+1 vs N+2: cost vs availability tradeoff — make explicit
```

**Overprovision for HA:**

```text
To survive 1 AZ loss (3 AZ equal): need capacity_per_AZ ≥ total/2
because remaining 2 AZs must hold 100% after evacuation
More precisely: peak after failover ≤ sum(capacity of surviving domains)
```

### 2.3 Scheduler throughput

```text
Feasible node filter + score on 5K nodes ≈ heavy if naive O(nodes) each pod
500 schedules/s × 5K node scores = 2.5M score ops/s — need caching, sampling, sharding
Trick: keep feasible sets; equivalence classes of nodes; random subset scoring
```

### 2.4 Health traffic

```text
Kubelet heartbeat every 10s
5K nodes → 500 heartbeats/s — easy
50K nodes → 5K/s — still OK; 500K → shard by cell
Pod probes local to node — don’t centralize HTTP probes for 1M pods
```

### 2.5 etcd / state size

```text
Pod object ~2 KB; 1M pods → 2 GB — near etcd practical limits
At 100×+: split stores / cells / compacted status
```

### 2.6 Autoscaler reaction

```text
Scale-up: cloud VM provision 1–5 min
Pending pods should be scheduled only after Ready
Stabilization: avoid scale-down if delete would reschedule churn
```

---

## 3. High-Level Design

### 3.1 Control vs data plane

| Plane | Components | HA needs |
|-------|------------|----------|
| Control | API, scheduler, controllers, autoscaler, etcd | Multi-AZ quorum |
| Data | Node agents, pods, CNI, CSI | Workload replicas + restart |

**Critical:** Data plane should continue running if control plane is briefly down (last applied desired state).

### 3.2 API (declarative)

```text
POST /apis/apps/v1/namespaces/{ns}/deployments
POST /apis/batch/v1/jobs
POST /apis/v1/pods (rarely direct)
GET  /apis/v1/nodes
GET  /apis/v1/events
```

Pod spec essentials:

```text
resources.requests/limits
nodeSelector / affinity / antiAffinity
topologySpreadConstraints
priorityClassName
tolerations
probes: liveness, readiness, startup
```

### 3.3 Desired state reconciliation

```text
Deployment.DesiredReplicas = 3
ReplicaSet ensures 3 Pod objects
Scheduler binds nodeName
Node agent starts container
Probes → Ready
If node dead → Pod deleted/recreated (per policy) → scheduler again
```

Level-triggered: controllers always drive actual → desired; no fragile edge-only workflows.

### 3.4 Scheduler pipeline

```text
1. Pop pod from queue (priority)
2. Filter: resource fit, taints, affinity, PV topology
3. Score: least/most requested, balance, topology spread, affinity prefer
4. Bind / reserve (optimistic) + conflict retry
5. Optional: preempt victims if pending high priority
```

### 3.5 Failure domains

```text
topology.kubernetes.io/zone
topology.kubernetes.io/rack   # custom
kubernetes.io/hostname
```

Spread example:

```text
maxSkew=1
topologyKey=zone
whenUnsatisfiable=DoNotSchedule  # for prod HA
```

### 3.6 Why X over Y

| Decision | Choice | Reject |
|----------|--------|--------|
| State store | Quorum (etcd/Raft) | Single SQL primary for control |
| Scheduling | Shared-state scheduler + optimistic bind | Central lock per node forever |
| HA workloads | Replicas + spread | “Live migrate everything” |
| Scale | Cells/shards at large | One global scheduler to 500K nodes |
| Health | Node heartbeat + local probes | Central probe all pods |
| Autoscaling | Separate node + replica loops | Only one dimension |

---

## 4. Architecture Diagram

### 4.1 Cluster overview

```text
                    ┌─────────────────────────────┐
   Clients/CI ───►  │ API Servers (HA, LB)        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │ Quorum Store (etcd)          │
                    └──────────────┬──────────────┘
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
     Scheduler(s)           Controllers              Autoscalers
     (filter/score)      (Deploy, Job, Node)      (pod HPA, nodes)
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │ watches / binds
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
   ┌─────────┐               ┌─────────┐               ┌─────────┐
   │ Zone A  │               │ Zone B  │               │ Zone C  │
   │ Nodes   │               │ Nodes   │               │ Nodes   │
   │ +agent  │               │ +agent  │               │ +agent  │
   └─────────┘               └─────────┘               └─────────┘
```

### 4.2 Placement across failure domains

```text
Service S replicas=6, spread zones (maxSkew=1)

   AZ-a: ■ ■        AZ-b: ■ ■        AZ-c: ■ ■
   rack1 rack2      rack1 rack2      rack1 rack2

Prefer also rack diversity when zone-satisfied
```

### 4.3 Failover timeline

```text
t0  node kernel panic
t10 missed heartbeats
t30 Node NotReady (threshold)
t30+ pods marked for reschedule (tolerate NotReady briefly for blips)
t35 new pods Pending → Bound on healthy nodes
t60+ Ready; load balancer removes old endpoints earlier on probe fail
```

### 4.4 Cell architecture (100×+)

```text
Region
  ├── Cell 1 (≤ ~10K nodes): own etcd + schedulers
  ├── Cell 2
  └── Cell 3
Federation / Cluster Registry routes tenants to cells
No single scheduler sees 500K nodes
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Quorum store: majority writes** — never dual-active divergent desired state.  
2. **Workload HA ≠ control plane HA** — declare both.  
3. **Topology spread for prod** — admission can require `DoNotSchedule` skew.  
4. **Agents are authoritative for local runtime truth**; control plane is desired.  
5. **Preemption respects PodDisruptionBudgets** where possible.  
6. **Autoscaler must not thrash** (cooldowns).

#### 5.1.2 Control plane HA

```text
3 or 5 etcd members across AZs
N API servers stateless behind LB
Leaders for controllers via leases
Scheduler leader or sharded non-overlapping partitions
```

**Deal-breaker:** one scheduler laptop + NFS etcd as “HA design.”

#### 5.1.3 Node failure detection

| Signal | Use |
|--------|-----|
| Heartbeat lease | Soft NotReady |
| Node problem detector | Kernel/docker dead |
| Network partition | Avoid false mass eviction — use quorum of observations |

False positive mass eviction is worse than slow detection — **tune gracefully**.

#### 5.1.4 Replication patterns

| Pattern | When |
|---------|------|
| Stateless N replicas + LB | Default web/api |
| Active/standby + lock | Stateful singleton |
| StatefulSet + PV | Identity + disk |
| Multi-AZ DB outside cluster | Don’t pretend pod restart = data HA |

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Master loss | Multi-master quorum |
| 10× | etcd size | Compact; CRD careful; status separate |
| 100× | Scheduler hotspot | Shard by namespace/hash |
| 1,000× | Region blast | Cells + regional isolation |

### 5.2 Scalability

#### 5.2.1 Packing vs spread

```text
Bin-pack (most requested): high util, risk correlated failure on fat nodes
Spread (least requested / topology): better HA, more fragmentation
Prod: topology first, then pack within domain
Batch: pack hard for util
```

#### 5.2.2 Fragmentation

```text
Free 1 CPU on 100 nodes ≠ 100 CPU gang job
Mitigate: pools, defrag drains, gang schedulers, VM sizes standardized
GPU: MIG/partition awareness; don’t treat as generic CPU
```

#### 5.2.3 Scheduler performance techniques

- Equivalence sets of identical nodes.  
- Cache predicate results.  
- Score random 5% sample when cluster huge.  
- Queue with backoff for unschedulable.  
- Optimistic binding + conflict retry.

#### 5.2.4 Autoscaling dual loop

```text
Replica autoscaler: metrics → desired replicas
Node autoscaler: pending pods → simulate schedule → add nodes of right pool
Scale-down: empty/underutilized nodes; honor PDBs; cordon+drain
```

#### 5.2.5 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Event-driven controllers; priority queue; zone enforced |
| →100× | Scheduler shards; etcd limits force cell thinking |
| →1,000× | Cells/federation; hierarchical capacity; local APIs |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
node_pools: [general, memory, gpu]
heartbeat_period: 10s
node_notready_timeout: 40s
scheduler_percentage_nodes_to_score: 30
autoscaler_scale_down_delay: 10m
max_pending_before_scale_up: 1
prod_priority: 1000
batch_priority: 100
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `scheduler_pending_pods` | Capacity/quota issues |
| `scheduler_attempts` | Performance |
| `node_notready_count` | Fleet health |
| `pod_restart_rate` | App/node issues |
| `cluster_cpu_allocatable_util` | Efficiency |
| `autoscaler_nodes_added` | Cost/reactiveness |
| `preemptions_total` | Priority pressure |
| `unschedulable_reasons` | Debug |

**Explainability:** every pending pod has Events: `FailedScheduling: 0/500 nodes...`.

#### 5.3.3 Testing

- Chaos: kill nodes, AZ dark, etcd member down.  
- Soak: schedule churn.  
- Topology property tests: never all replicas one zone.  
- Autoscaler simulation offline.

#### 5.3.4 Ops

- Cordon/drain for maintenance.  
- Canary node pools for kernel upgrades.  
- Cluster backup of etcd.  
- Feature gates for scheduler plugins.

---

## 6. Wrap-Up

### 6.1 What we designed

A **Borg/K8s-class redundant compute cluster**: HA quorum control plane, topology-aware scheduling, health reconciliation, dual autoscaling, preemption, and **cell sharding** for mega scale—separating control-plane HA from workload replication across failure domains.

### 6.2 Memorize tradeoffs

| Topic | Tradeoff |
|-------|----------|
| Pack vs spread | Util vs blast radius |
| Detect fast vs false eviction | Availability oscillation |
| Redundancy tax | Cost vs AZ survival |
| Monolith scheduler vs shards | Simplicity vs scale |
| Preemption | Prod latency vs batch completion |
| Optimistic bind | Throughput vs retries |

### 6.3 30-second scale narrative

Baseline: 500 nodes, one logical cluster, HA masters.  
10×: optimize scheduler + strict topology.  
100×: shard schedulers / approach cells.  
1,000×: federated cells; no global single brain.

### 6.4 Deal-breakers checklist

- Single master / single AZ etcd as HA.  
- All replicas scheduled without topology constraints.  
- Central health-probing millions of pods.  
- Autoscaler without cooldown (flapping).  
- Treating pod restart as durable state HA.  
- One scheduler scoring all 500K nodes naively each bind.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: VMs or containers?**  
A: Containers MVP; VMs as another runtime class — same scheduling ideas.

**Q2: What does redundant mean?**  
A: Control plane quorum + workload replicas across failure domains + replacement automation.

**Q3: Multi-tenant isolation level?**  
A: Namespace quotas + cgroups; hypervisor for hostile tenants.

### 7.2 Scheduling

**Q4: Filter vs score?**  
A: Filter hard constraints; score soft preferences; pick best.

**Q5: How to enforce zone spread?**  
A: TopologySpreadConstraints / anti-affinity hard.

**Q6: Optimistic vs pessimistic binding?**  
A: Optimistic high throughput; retry on conflict.

**Q7: Gang scheduling?**  
A: All-or-nothing for distributed training; special plugin; avoid head-of-line blocking.

**Q8: Affinity to data?**  
A: PV zone topology; schedule pod where volume is.

### 7.3 Failure & HA

**Q9: Node vs pod failure?**  
A: Pod crash → restart in place; node death → reschedule elsewhere.

**Q10: Control plane down — do workloads stop?**  
A: No; agents keep last desired; new changes blocked.

**Q11: Correlated kernel bug?**  
A: Canary pools; maxUnavailable; diverse kernels hard.

**Q12: PDB vs urgent drain?**  
A: PDB blocks voluntary; involuntary node death may violate — design for that.

### 7.4 Autoscaling & capacity

**Q13: HPA vs cluster autoscaler?**  
A: HPA changes replicas; CA changes nodes for pending/util.

**Q14: How much spare capacity for AZ loss?**  
A: Remaining domains must fit evacuated load; often ~50% headroom with 3 AZ.

**Q15: Scale-to-zero?**  
A: Batch/event OK; not for latency-critical prod without idle pods/warm pool.

### 7.5 Multi-tenancy & fairness

**Q16: Fair sharing?**  
A: Weighted fair queue / DRF for multi-resource; quotas hard caps.

**Q17: Noisy neighbor?**  
A: Limits, CPU CFS, optionally dedicated nodes.

**Q18: Preemption storm?**  
A: Bound victims; backoff; priority bands.

### 7.6 Estimation drills

**Q19: etcd with 2M pods × 2KB?**  
A: ~4GB — too big; split cells/status.

**Q20: Heartbeats 100K nodes / 10s?**  
A: 10K/s — shard acceptors.

**Q21: Why sampling nodes to score?**  
A: Diminishing returns; randomness + equivalence classes suffice.

### 7.7 Alternatives & deal-breakers

**Q22: Mesos / Nomad / Borg?**  
A: Same themes: two-level or shared-state scheduling; know tradeoffs.

**Q23: Only VM ASGs without scheduler?**  
A: Coarse; poor packing/bin constraints; OK for simple fleets.

**Q24: Serverless instead?**  
A: Different product; still needs regional compute under the hood.

### 7.8 Interview craft

**Q25: How to open?**  
A: Workload types, HA domains, multi-tenant, scale — then control vs data plane.

**Q26: What impresses L5+?**  
A: Failure-domain math, scheduler scaling story, explicit deal-breakers, packing vs spread.

**Q27: Common mistake?**  
A: Drawing 20 microservices but never explaining bind/filter/score or AZ spare capacity.

---

### Appendix A — Scheduler pseudocode

```text
def schedule(pod):
  nodes = filter(pod, all_nodes)
  if not nodes and pod.priority high:
    nodes = preempt_for(pod)
  if not nodes: return Pending
  scored = score(pod, sample(nodes))
  return bind(pod, best(scored))
```

### Appendix B — Topology spread

```text
skew(zone) = count(zone) - min_count
require skew ≤ maxSkew for DoNotSchedule
```

### Appendix C — Node conditions

```text
Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable
taints based on conditions → NoSchedule / NoExecute
```

### Appendix D — Priority classes

```text
system-critical: 2000000000
prod: 1000
batch: 100
besteffort: 0
```

### Appendix E — Autoscaler simulation

```text
for pending in pods:
  if any node fits: continue
  pick node_type that would fit
  propose +1 node
group proposals; call cloud API
```

### Appendix F — Drain sequence

```text
cordon → evict pods honoring PDB → wait → terminate instance
timeout → force for maintenance with escalation
```

### Appendix G — Progressive scale table

| Scale | Control plane | Scheduler | Cells |
|-------|---------------|-----------|-------|
| Baseline | 1 cluster HA | 1–2 schedulers | No |
| 10× | Tuned etcd | Plugins + cache | No |
| 100× | Watch pressure | Shards | Emerging |
| 1,000× | Per-cell | Per-cell | Yes |

### Appendix H — Resource model

```text
requests → scheduling & bin-pack
limits → runtime isolation
best-effort / burstable / guaranteed QoS
```

### Appendix I — Event examples

```text
FailedScheduling: 0/500 nodes are available: 400 Insufficient cpu,
  100 node(s) didn't match pod affinity/anti-affinity
TriggeredScaleUp: pod pending → added 2 nodes pool=general
```

### Appendix J — NFR card

```text
etcd multi-AZ quorum
prod topology DoNotSchedule
node NotReady detection bound
dual autoscaling with cooldowns
pending pod explainability
cell plan beyond ~50K nodes
```

### Appendix K — GPU placement

```text
GPU nodes tainted
jobs tolerate gpu=true
avoid fragmenting 8-GPU nodes with 1-GPU jobs if policy packs
consider MIG / time-slicing explicitly
```

### Appendix L — Stateful caution

```text
Replicas ≠ data durability
Use managed DB / StatefulSet+PV + backups
Failover may be attach volume in same AZ only
```

### Appendix M — Common pushbacks

| Pushback | Answer |
|----------|--------|
| “K8s already exists” | Interview wants principles: schedule, domains, scale |
| “Just use ASG” | Misses packing, topology, multi-tenant fairness |
| “Global single cluster” | etcd/scheduler limits → cells |

### Appendix N — Related Google systems (conceptual)

- Borg / Omega / Kubernetes lineage  
- Autopilot-style managed control  
- Bin-packing research (DRF, etc.) |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Allocatable | Resources after system reserve |
| PDB | PodDisruptionBudget |
| Taint/toleration | Node repulsion / permission |
| Cell | Independent cluster shard |
| Equivalence class | Nodes identical for scheduling |

### Appendix P — Worked example

```text
Deploy API: 6 replicas, 2 CPU each, spread 3 AZ
Need 12 CPU / AZ normally (2 per AZ… wait: 6/3=2 pods × 2 CPU = 4 CPU/AZ)
Survive AZ loss: 4 pods on 2 AZ → 8 CPU/AZ required post-failover
Provision spare accordingly or accept degraded capacity
```

### Appendix Q — Consistency cheatsheet

| Object | Semantics |
|--------|-----------|
| Desired replicas | Strong in etcd |
| Pod status | Eventual from agents |
| Bind | Atomic nodeName set |
| Metrics HPA | Eventually consistent |

### Appendix R — 30m interview checklist

1. Clarify workloads + domains.  
2. Control vs data plane.  
3. Scheduler filter/score/bind.  
4. Health + reschedule timeline.  
5. Autoscaling dual loop.  
6. Capacity math for AZ loss.  
7. Scale to cells; deal-breakers.  

### Appendix S — Preemption sketch

```text
victims = lowest priority on candidate nodes
while need resources:
  pick victim set minimizing PDB harm
evict → reschedule preemptor
```

### Appendix T — What changes at each scale

| Scale | Key change |
|-------|------------|
| 10× | Scheduler perf + topology hard |
| 100× | Shards / etcd pressure |
| 1,000× | Cells/federation |

### Appendix U — Multi-region Phase 1.5

```text
Control plane per region
Global: capacity broker + DNS/anycast services
Avoid single etcd across continents
```

### Appendix V — Security basics

- Authn/z on API; admission webhooks  
- Runtime sandbox; secrets encryption  
- Node identity (SPIFFE-like)  

---

*End of redundant cloud-compute cluster system design.*
