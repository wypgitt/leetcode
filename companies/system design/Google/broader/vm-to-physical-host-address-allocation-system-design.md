# System Design: VM-to-Physical-Host Address Allocation

> **Focus areas:** VM placement · IP/MAC allocation · Bin-packing · Affinity/anti-affinity · Fragmentation · Inventory · Atomic reserve · Network identity lifecycle · Failure domains · Dual allocation (compute + address)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct packing vs fragmentation math, atomic IP+host reservation, deal-breakers for “DHCP race + schedule separately” without coordination  
> **Interview theme:** Google L5+ cloud/IaaS — place VMs on physical hosts and allocate network addresses without collisions, with packing efficiency and placement constraints

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

Goal: **bound the product**—given a VM request (CPU/RAM/disk/GPU, network, constraints), **select a physical host** and **allocate addresses** (MAC, private IP, optional public IP) **atomically**, minimizing fragmentation while honoring affinity/anti-affinity and failure domains.

### 1.0 What this is / is not

| Dimension | **VM→host + address allocation (this doc)** | Not this |
|-----------|-----------------------------------------------|----------|
| Primary job | Place VM + assign network identity | Guest OS image builder |
| Success | No double-book CPU/IP; high pack efficiency; fast allocate | Perfect oracle packing NP-hard always optimal |
| Address | VPC IP + MAC (+ EIP optional) | Global public IPv4 planning only |
| Scheduler link | Tightly coupled with inventory | Completely separate DHCP hope |
| Success metric | Allocation latency, utilization, move rate | VM app business logic |

**Scope statement:** Design the allocation control plane that jointly places VMs on hosts and assigns MAC/IP addresses under capacity, packing, and affinity constraints—at cloud scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is allocated? | Host slot (resources) + MAC + private IP; optional public IP | Composite allocation record |
| F2 | Network model? | VPC/subnet per tenant; overlay OK | IPAM per subnet |
| F3 | MAC uniqueness? | Cluster/fabric unique (or globally) | MAC pool / SPA |
| F4 | Placement constraints? | AZ, host affinity/anti-affinity, GPU, local SSD | Filter/score |
| F5 | Packing goal? | High utilization; leave room for large VMs | Fragmentation-aware score |
| F6 | Atomicity? | Don’t assign IP if place fails; no orphan IPs | Two-phase / single txn |
| F7 | Release? | On VM delete; reclaim after grace | Lifecycle state machine |
| F8 | Live migrate? | Optional Phase 1.5; keep IP/MAC | Move host binding |
| F9 | Reserved IPs? | User can reserve static private IP | Reservation objects |
| F10 | Dedicated hosts? | Yes for some tenants | Host partitions |
| F11 | Oversubscription? | CPU yes policy; mem careful; IP no | Policy knobs |
| F12 | Audit? | Who got which IP/host when | Append-only log |

**MVP functional scope:**

1. Inventory of hosts: capacity, allocs, labels, health, domain.  
2. IPAM: subnet free-lists / bitmaps; allocate/release IPv4 (v6 Phase 1.5).  
3. MAC allocator: unique MACs.  
4. Placement engine: filter → score → reserve host resources.  
5. **Atomic** commit: host + MAC + IP (+ ENI-like record).  
6. Affinity / anti-affinity groups.  
7. Release path with grace for DHCP/ARP safety.  
8. Multi-AZ; don’t place anti-affinity mates together.  
9. APIs for allocate / deallocate / describe.  
10. Metrics for fragmentation and pending capacity.

**Out of MVP:**

- Full SDN controller implementation details  
- IPv6-only world as required  
- Optimal ILP solver every request (heuristics OK)  
- Bare-metal provisioning factory  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Alloc latency | Interactive API | p50 < 100ms; p99 < 500ms–1s |
| N2 | Correctness | No IP/MAC/host double alloc | Strong via CAS/txn |
| N3 | Availability | Alloc path HA | Multi-AZ control plane |
| N4 | Utilization | Efficient packing | Track stranded capacity |
| N5 | Scale | Millions of VMs | Shard IPAM + placement |
| N6 | Churn | High create/delete | Avoid bitmap lock convoying |
| N7 | Safety reclaim | No premature IP reuse | Grace TTL |
| N8 | Explainability | Why pending | Events: no capacity / no IP |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Launch VM in subnet S, 4 vCPU 16GB → place host H → IP 10.0.2.15 → MAC → boot.  
2. Anti-affinity group of 3 → spread across hosts/racks.  
3. Delete VM → resources free → IP grace → reclaim.  
4. Reserved IP → place only where subnet/route OK → bind reserved.  
5. AZ outage → place in remaining AZs if policy allows.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| IP available but no host fit | Fail with `InsufficientCapacity` — don’t consume IP |
| Host fit but subnet exhausted | Fail `InsufficientIp` or pick other subnet if auto |
| Concurrent alloc same IP | CAS; one wins |
| Fragmentation: 1 vCPU free on many hosts | Large VM pending; defrag/migrate or reject |
| Unhealthy host | Filtered out |
| MAC pool exhaustion | Alert; expand OUI space |
| Dual-stack need | Allocate v4+v6 jointly |
| Orphan after crash mid-alloc | Transaction rollback / reconciler GC |
| Sticky IP on replace | Keep reservation; new host |
| Noisy placement flap | Soft sticky scores |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Hosts | 10K | 100K | 1M | 10M |
| Active VMs | 200K | 2M | 20M | 200M |
| Alloc QPS | 200 | 2K | 20K | 200K |
| Subnets | 50K | 500K | 5M | 50M |
| VPC tenants | 10K | 100K | 1M | 10M |
| IPs managed | 5M | 50M | 500M | billions (v6) |
| Affinity groups | 100K | 1M | 10M | huge |

**What each jump forces:**

- **10×:** Sharded IPAM; cached host views; async inventory.  
- **100×:** Placement workers by cell/AZ; subnet bitmaps in memory per shard.  
- **1,000×:** Hierarchical capacity; approximate scoring; cell-local allocators; CRDTs careful not for IPs.

### 1.5 Etc. (Constraints & Assumptions)

- Hypervisors report inventory via agents.  
- Overlay network means IP is logical; still must be unique in VPC.  
- Physical host has underlay IP separate from guest.  
- Address allocation includes **guest identity**, not TOR switch programming details (interface only).

**Scope statement to repeat back:**

> Design VM-to-physical-host placement plus IP/MAC allocation as one atomic control-plane operation, with bin-packing and affinity, IPAM that doesn’t race the scheduler, and progressive sharding to millions of hosts.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Host packing

```text
Host: 96 vCPU, 384 GB
VM mix avg: 4 vCPU, 16 GB → CPU binds at 24 VMs; mem would allow 24 — balanced
If VMs are 2 vCPU / 32 GB → mem binds earlier → stranded CPU (fragmentation)
```

### 2.2 Stranded capacity

```text
Free 2 vCPU × 50,000 hosts = 100K vCPU “free” but cannot place 16 vCPU VM
Metric: largest_contiguous_fit vs sum_free
```

### 2.3 Subnet bitmap

```text
/20 subnet = 4096 addresses; usable ~4091
Bitmap 4096 bits = 512 B — tiny
/16 = 64K bits = 8 KB — still tiny per subnet
5M subnets × 8 KB = 40 GB — shard by VPC
```

### 2.4 Alloc QPS & locking

```text
2K alloc/s; naive global lock — dies
Shard by subnet_id for IP; by cell for hosts
Target: lock scope = one subnet bitmap word stripe + one host record
```

### 2.5 MAC space

```text
Locally administered MACs: 2^46 theoretically
Cluster of 20M NICs — trivial
Still need uniqueness allocator (not random without collision detect)
```

### 2.6 Control plane state

```text
VM alloc record ~500 B × 20M = 10 GB metadata
Hosts 1M × 1 KB = 1 GB
Fits in distributed KV with care
```

---

## 3. High-Level Design

### 3.1 Composite allocation

```text
Allocation {
  vm_id
  host_id
  resources: {vcpu, mem, gpu, local_ssd}
  nic: {mac, subnet_id, private_ip, public_ip?}
  az, rack
  affinity_group_ids
  state: RESERVING|ACTIVE|RELEASING|FREED
  version
}
```

### 3.2 API

```text
POST /v1/allocations
  {vm_shape, subnet_id, az?, affinity?, anti_affinity?, reserved_ip?}
→ {host_id, mac, ip, allocation_id}

DELETE /v1/allocations/{id}
GET   /v1/allocations/{id}
POST  /v1/ips/reservations
```

### 3.3 Placement pipeline

```text
1. Validate request + quota
2. Build candidate filters:
   - AZ, host type, GPU, healthy, taints
   - anti-affinity exclude hosts
   - affinity prefer hosts
   - subnet reachability (same AZ as subnet)
3. Score packing + spread
4. Try reserve top candidates (CAS host capacity)
5. Allocate MAC + IP (or reserved IP bind)
6. Commit Allocation ACTIVE
7. On any fail: rollback prior steps
```

### 3.4 Packing scores — Why X over Y

| Strategy | Pros | Cons | Use |
|----------|------|------|-----|
| **Best fit** | Leaves large holes | Slightly more CPU | Large VM friendly |
| **Worst fit** | Spread small | Fragments large | Avoid for mixed |
| **First fit** | Fast | Worse util | Tiny clusters |
| **Most full (bin-pack)** | High util | Strands large shapes | Batch/stateless |
| **Dot-product / vector fit** | Multi-resource | Tunable | MVP score |

**MVP:** filter → score = `α·pack_tightness + β·affinity + γ·anti_frag_bonus - δ·failure_domain_risk`.

### 3.5 IPAM methods

| Method | Pros | Cons |
|--------|------|------|
| Free-list | Simple | Fragmented scans |
| Bitmap + find-first-zero | Fast, compact | Need locking stripes |
| Buddy / prefix | CIDR delegation | More complex |
| Random + probe | Low contention | Collisions retries |

**MVP:** bitmap per subnet with striped locks; reserved IPs marked allocated in bitmap.

### 3.6 Why X over Y (summary)

| Decision | Choice | Reject |
|----------|--------|--------|
| Host vs IP order | Reserve host then IP; txn rollback | DHCP first hope |
| Atomicity | Single allocation record + CAS | Best-effort glue |
| Packing | Vector best-fit heuristic | Always worst-fit |
| Scale | Shard subnet + cell | Global mutex |
| Reclaim | Grace period | Instant reuse |
| Anti-affinity | Hard filter | Soft only for HA groups |

---

## 4. Architecture Diagram

### 4.1 Control plane

```text
                   ┌────────────┐
   Compute API ──► │ Allocator  │
                   │ Orchestrator│
                   └──────┬─────┘
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │Placement │  │  IPAM    │  │ MAC Pool │
     │ Service  │  │ Service  │  │ Service  │
     └────┬─────┘  └────┬─────┘  └────┬─────┘
          │             │             │
          ▼             ▼             ▼
     Host Inventory  Subnet Bitmaps  MAC DB
          │
          ▼
     ┌────────────────────────────────┐
     │ Hypervisor Agents (capacity)   │
     └────────────────────────────────┘
```

### 4.2 Atomic allocate sequence

```text
Client → Orchestrator
  → Placement.Reserve(host H, resources)  # CAS capacity
  → MAC.Alloc()
  → IPAM.Alloc(subnet) or Bind(reserved)
  → Write Allocation(ACTIVE)
If IPAM fails: Placement.Release(H); MAC.Release(); error
```

### 4.3 Anti-affinity spread

```text
Group G: VMs want distinct hosts (or racks)

Host1: VM_a (G)     Host2: VM_b (G)     Host3: VM_c (G)
Request VM_d (G) → filter out Host1/2/3
```

### 4.4 Fragmentation picture

```text
Hosts:
H1: [████████░░] 8/10 full  ← small holes
H2: [████░░░░░░] 4/10
H3: [██████████] full

Large VM size 4: prefer H2 (best fit) not splitting hope across H1 holes
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No IP assigned to two ACTIVE allocations** in same VPC/subnet scope.  
2. **No MAC duplicates** in uniqueness domain.  
3. **Host allocated resources ≤ capacity** (modulo explicit oversubscribe policy).  
4. **Allocation is atomic** from client POV — no ACTIVE without all fields.  
5. **Anti-affinity hard constraints never violated** when `DoNotSchedule` mode.  
6. **Reclaim grace:** IP not reissued before TTL unless forced.

#### 5.1.2 Crash mid-allocation

```text
States: RESERVING_HOST → RESERVING_ADDR → ACTIVE
Reconciler:
  RESERVING_* older than T → rollback
  ACTIVE without agent confirm → retry push / mark ERROR
```

**Deal-breaker:** leaking IPs on every client timeout without reconciler.

#### 5.1.3 Inventory consistency

Agents heartbeat capacity; allocator uses **optimistic CAS** on `host.version`. Stale score OK; bind fails → try next candidate.

#### 5.1.4 Failure domains

```text
Place replicas across: host → rack → AZ
Anti-affinity topology key configurable
Spare capacity math same as compute cluster doc
```

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Double IP | Bitmap CAS |
| 10× | Inventory lag | CAS retry; shorter TTL cache |
| 100× | Hot subnet lock | Stripe bitmap; IP random in free windows |
| 1,000× | Global placement view impossible | Cell-local + hierarchical |

### 5.2 Scalability

#### 5.2.1 Placement at large

Techniques:

- Equivalence classes of hosts.  
- Sample N candidates to score.  
- Maintain free-resource indexes: `skip lists by free_cpu`.  
- Cell/AZ parallel allocators with subnet affinity.

#### 5.2.2 Fragmentation controls

| Technique | Effect |
|-----------|--------|
| Best-fit scoring | Preserve large holes |
| Size-based host pools | Separate whale shapes |
| Live migrate defrag | Expensive; scheduled |
| Admission deny small into last large hole | Policy |

#### 5.2.3 IPAM sharding

```text
Shard key = hash(vpc_id) or subnet_id
All IP ops for subnet on one shard owner
Cross-subnet alloc = independent
```

#### 5.2.4 Affinity indexing

```text
anti_affinity_group → set(host_ids used)
filter candidates not in set
For rack diversity: set(rack_ids)
```

#### 5.2.5 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Sharded IPAM; host indexes |
| →100× | Cell allocators; sampling |
| →1,000× | Hierarchy; pool specialization; async defrag jobs |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
oversubscribe_cpu: 1.5
oversubscribe_mem: 1.0
ip_reclaim_grace_s: 300
placement_candidate_sample: 100
score_weights: {pack:0.6, affinity:0.2, spread:0.2}
mac_oui: "02:a1:b2"
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `alloc_latency` | SLO |
| `alloc_fail{reason}` | Capacity vs IP vs constraint |
| `cas_retries` | Contention |
| `stranded_cpu` | Fragmentation |
| `subnet_free_ips` | Exhaustion |
| `ip_grace_queue` | Reclaim health |
| `anti_affinity_violations` | Should be 0 |

#### 5.3.3 Testing

- Concurrent alloc stress on one subnet.  
- Crash injection mid-state machine.  
- Fragmentation scenarios with whale VMs.  
- Anti-affinity property tests.  
- Reconciler orphan cleanup.

#### 5.3.4 Ops

- Subnet expansion / secondary CIDR.  
- Drain host: move or block new allocs.  
- Manual IP quarantine.  
- Rebuild bitmap from allocation table (source of truth dual-check).

---

## 6. Wrap-Up

### 6.1 What we designed

An **atomic VM placement + address allocation** control plane: inventory-aware bin-packing with affinity, IPAM bitmaps, MAC pools, lifecycle grace, and **sharded/cell** scaling—so compute and network identity never race.

### 6.2 Memorize tradeoffs

| Topic | Tradeoff |
|-------|----------|
| Pack tight vs preserve holes | Util vs whale schedulability |
| Sample vs full scan | Latency vs optimality |
| IP grace | Safety vs exhaustion under churn |
| CPU oversubscribe | Density vs noisy neighbor |
| Coupled vs separate DHCP | Correctness vs modularity illusion |
| Migrate defrag | Efficiency vs disruption |

### 6.3 30-second scale narrative

Baseline: monolithic allocator, bitmap IPAM.  
10×: shard IPAM + host indexes.  
100×: cell-local placement.  
1,000×: hierarchical capacity & specialized pools.

### 6.4 Deal-breakers checklist

- Schedule host and DHCP independently without atomicity/rollback.  
- Instant IP reuse → silent cross-talk.  
- Global lock on all allocations.  
- Ignoring anti-affinity for “HA” VMs.  
- Sum of free resources as proof a large VM fits.  
- Random MACs without uniqueness tracking at scale (birthday).  

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Is IP per VM or per NIC?**  
A: Per NIC/ENI; VM may have multiple — allocate set.

**Q2: Public IP in scope?**  
A: Optional pool; often separate EIP attachment.

**Q3: Who programs the network?**  
A: Allocator publishes desired; SDN agent converges.

### 7.2 Placement & packing

**Q4: Best fit vs worst fit?**  
A: Best fit often reduces fragmentation for mixed sizes.

**Q5: Multi-dimensional packing?**  
A: Vector resources; score by leftover norm / alignment.

**Q6: Why sampling hosts OK?**  
A: Equivalence + randomness; retry on CAS fail.

**Q7: Affinity vs anti-affinity?**  
A: Affinity colocate (cache/license); anti-affinity HA spread.

**Q8: Gang place multi-VM?**  
A: All-or-nothing reservation set; avoid partial.

### 7.3 IPAM & MAC

**Q9: Bitmap vs free-list?**  
A: Bitmap great for dense IPv4 subnets; find free bit fast.

**Q10: Reserved IP?**  
A: Mark bit allocated; bind on VM create; fail if placed wrong AZ.

**Q11: Why MAC allocate centrally?**  
A: Uniqueness, audit, anti-spoof allowlists.

**Q12: IPv6?**  
A: Huge space — may allocate /128 from prefix pools differently than dense bitmaps.

### 7.4 Atomicity & lifecycle

**Q13: Order of host vs IP?**  
A: Either OK with rollback; commonly host then IP (IP scarcer in subnet).

**Q14: Grace period reason?**  
A: Stale ARP/conntrack; delayed packets; security.

**Q15: Reconciler role?**  
A: Cleanup RESERVING orphans; repair bitmap drift.

### 7.5 Scale & cells

**Q16: Why shard by subnet?**  
A: Natural contention boundary for IPAM.

**Q17: Cross-AZ subnet?**  
A: Usually subnet is AZ-scoped in clouds — place accordingly.

**Q18: 200K alloc/s?**  
A: Cell-local; almost no global coordination; batch agent invent.

### 7.6 Estimation drills

**Q19: Free 1G across 1000 hosts vs 1TB VM?**  
A: Sum free irrelevant; need one host fit.

**Q20: /24 subnet how many VMs?**  
A: ≤ 251 usable typical — plan subnet size vs fleet.

**Q21: Birthday collision 1M random 32-bit?**  
A: High collision risk — don’t random IPs without tracking.

### 7.7 Alternatives & deal-breakers

**Q22: Pure Kubernetes scheduling?**  
A: Similar filters/scores; still need IPAM integration (CNI).

**Q23: Central SQL with SELECT FOR UPDATE on subnets?**  
A: Works small; shard later; acknowledge limits.

**Q24: Client-chosen IP?**  
A: Only within reservation/authorization; still server validates CAS.

### 7.8 Interview craft

**Q25: How to open?**  
A: Joint host+address atomic alloc; constraints; packing; scale shards.

**Q26: What impresses L5+?**  
A: Fragmentation metrics, rollback state machine, anti-affinity, grace, cell story.

**Q27: Common mistake?**  
A: Beautiful bin-pack slides with hand-waved DHCP uniqueness.

---

### Appendix A — Host CAS

```text
UPDATE hosts SET free_cpu=free_cpu-?, free_mem=free_mem-?, ver=ver+1
WHERE id=? AND ver=? AND free_cpu>=? AND free_mem>=? AND healthy=1
```

### Appendix B — Bitmap alloc

```text
idx = find_first_zero_bit(bitmap[subnet])
if idx < 0: fail
if cas_set_bit(subnet, idx): return offset_to_ip(idx)
else retry
```

### Appendix C — Rollback

```text
on_fail:
  if ip: release_or_grace(ip)
  if mac: free(mac)
  if host_reserved: restore capacity CAS
  allocation.state = FAILED
```

### Appendix D — Score function

```text
pack = 1 - remaining_norm_after(vm) / remaining_norm_before
aff = +1 if meets prefer affinity
spread = +1 if increases domain diversity for group
score = w1*pack + w2*aff + w3*spread
```

### Appendix E — State machine

```text
NONE → RESERVING_HOST → RESERVING_ADDR → ACTIVE → RELEASING → FREED
                         ↘ FAIL_ROLLBACK
```

### Appendix F — Anti-affinity filter

```text
forbidden_hosts = union(hosts_of_group(g) for g in req.anti_affinity)
candidates = candidates - forbidden_hosts
```

### Appendix G — Progressive scale table

| Scale | Placement | IPAM |
|-------|-----------|------|
| Baseline | Central | Central bitmaps |
| 10× | Indexed hosts | Sharded subnets |
| 100× | Per AZ/cell | Per cell |
| 1,000× | Hierarchical | Prefix delegation |

### Appendix H — Public IP (EIP)

```text
Allocate private first
Attach EIP from regional pool → NAT/floating mapping
Release EIP independent lifecycle optional
```

### Appendix I — Agent inventory

```json
{"host":"h1","free_cpu":16,"free_mem_gb":64,"gpus_free":1,"ver":9}
```

### Appendix J — NFR card

```text
Atomic alloc
No double IP/MAC/host
p99 < 1s
IP grace
Fragmentation metrics
Shard subnet + cell
```

### Appendix K — Dual-stack

```text
Reserve host once
Alloc v4 + v6 in same txn
Rollback both if either fails
```

### Appendix L — Dedicated host

```text
Tenant owns host; placement restricted to dedicated set
IPAM still VPC-based
```

### Appendix M — Common pushbacks

| Pushback | Answer |
|----------|--------|
| “CNI handles IP” | Still need uniqueness + place coupling at IaaS |
| “Optimal solver” | Heuristic + pools; ILP offline |
| “Random is fine” | Collisions + fragmentation blindness |

### Appendix N — Related systems (conceptual)

- Borg/Omega placement  
- AWS EC2 + VPC IPAM ideas  
- OpenStack Nova + Neutron  

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| IPAM | IP address management |
| ENI | Elastic network interface |
| Stranding | Free but unusable resources |
| Grace | Delay before IP reuse |
| SPA | Scalable MAC assignment |

### Appendix P — Worked example

```text
Request: 8 vCPU, 32 GB, subnet subnet-1 (AZ-a), anti-affinity G
Candidates in AZ-a with free≥8/32, not hosting G: H7,H9
Score best-fit → H9
CAS reserve H9 → IP 10.1.4.22 → MAC 02:... → ACTIVE
```

### Appendix Q — Consistency cheatsheet

| Resource | Mechanism |
|----------|-----------|
| Host capacity | CAS version |
| IP bit | CAS set bit |
| Allocation | Durable record |
| Agent view | Eventual; bind checks |

### Appendix R — 30m interview checklist

1. Joint alloc problem statement.  
2. Filter/score/reserve.  
3. IPAM + MAC.  
4. Atomic state machine.  
5. Affinity + fragmentation.  
6. Shard/cells scale.  
7. Deal-breakers.  

### Appendix S — Reconciler

```text
for alloc in RESERVING older than T:
  rollback(alloc)
for bit set in bitmap without ACTIVE/RESERVED:
  clear after verify (drift repair)
```

### Appendix T — What changes at each scale

| Scale | Key change |
|-------|------------|
| 10× | Shard IPAM |
| 100× | Cell placement |
| 1,000× | Hierarchy + pools |

### Appendix U — Security

- Anti-spoof: fabric allows only allocated MAC/IP  
- Tenant isolation in VPC  
- Audit every alloc/release  

### Appendix V — Defrag job

```text
Identify hosts with high stranding
Propose live migrates of small VMs to consolidate holes
Respect anti-affinity & PDBs
```

---

*End of VM-to-physical-host address allocation system design.*
