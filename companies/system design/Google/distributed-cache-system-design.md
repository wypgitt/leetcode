# System Design: Distributed Cache

> **Focus areas:** Partitioning · Replication · Eviction · Hot keys · Consistency · Node membership  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Google L5+ — database choice, partitioning, ambiguity > reproducing Google internals

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

Goal: **bound the cache**—a **distributed in-memory (optionally SSD-tier) key-value cache** used to accelerate reads (and carefully manage writes) in front of durable databases or services. Emphasize **partitioning, replication, eviction, hot-key mitigation, consistency options, and membership**. This is **not** a durable primary store (unless interviewer explicitly wants Redis-as-DB—push back).

### 1.0 What this is / is not

| Dimension | **Distributed cache (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Low-latency Get/Set; absorb DB load | Source of truth / ACID OLTP |
| Success | Hit rate, p99 Get, stability under skew | Never lose writes (unless write-back WAL) |
| Data | Opaque KV + TTL/version | Rich secondary indexes MVP |
| Failure | Node loss ⇒ miss / rebuild | Data loss of SoT |

**Scope statement:** Design a **distributed cache** with consistent-hash partitioning, replication, eviction, hot-key handling, tunable consistency, and robust membership—scaling through progressive load jumps.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | `Get` / `Set` / `Del` / `GetMulti`; optional CAS | Memcached/Redis-like |
| F2 | Value size? | Mostly < 1 MB; reject huge | Memory slabs / size limits |
| F3 | TTL? | Yes, per-key; default TTL | Expiry wheel / lazy + active |
| F4 | Eviction? | When memory full | LRU/LFU/TinyLFU + TTL |
| F5 | Replication? | RF=3 typical for HA | Async or sync replica options |
| F6 | Consistency? | Tunable; often eventual OK | Document model; quorum optional |
| F7 | Write path? | Cache-aside common; mention WT/WB | Client library patterns |
| F8 | Hot keys? | Yes—must not melt one shard | Replication / local cache / coalesce |
| F9 | Transactions? | No multi-key TX MVP | Single-key atomicity |
| F10 | Persistence? | Optional AOF/snapshot Phase 2 | Memory-first MVP |
| F11 | Pub/sub inval? | Optional for WT coherence | Side channel |
| F12 | Multi-tenant? | Namespaces + quotas | Isolation / noisy neighbor |

**MVP functional scope:**

1. Clustered KV: Get/Set/Del with TTL; optional CAS (`version`/`cas_id`).  
2. Partitioning via **consistent hashing + virtual nodes**.  
3. Replication factor RF (default 3); failover on node death.  
4. Memory budgeting + eviction (LRU or TinyLFU admission + SLRU).  
5. Client routing (smart client or proxy).  
6. Hot-key mitigation: request coalescing, optional key replication / local L0.  
7. Membership via gossip or ZK/etcd; rebalance controlled.  
8. Metrics: hit rate, eviction, hot-key detectors, p99, memory.

**Out of MVP:**

- Multi-key serializable transactions  
- Full Redis data structures (streams, ZSET) unless asked—keep KV core  
- Cross-region strongly consistent active-active  
- Disk as primary SoT (that’s a DB)  
- Exactly-once write-back without WAL story  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Get latency | Memory path | p50 < 1ms; p99 < 5ms in-AZ |
| N2 | Availability | High for cache tier | 99.9%+; degrade to DB on miss |
| N3 | Durability | Cache ephemeral MVP | DB is SoT; optional WB WAL later |
| N4 | Hit rate | Workload dependent | Design for ≥80–95% when working set fits |
| N5 | Consistency | Tunable | Default: per-key RW to primary replica |
| N6 | Elasticity | Add/remove nodes | Controlled rebalance; minimize miss storm |
| N7 | Skew tolerance | Hot keys inevitable | Explicit mitigations |
| N8 | Operability | Clear ownership | Membership, dashboards, drain |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Cache-aside Get hit → return.  
2. Miss → singleflight to DB → Set → return.  
3. Set on primary → async replicate to RF-1 secondaries.  
4. Node drain → ownership migrates → clients update ring.  
5. Hot key detected → replicate to N nodes or enable client L0.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Thundering herd on miss | Singleflight / request coalescing |
| Hot key on one vnode | Detect; replicate; client cache; split key if logical |
| Network partition | Prefer AP for cache; stale reads possible; fencing on primary |
| Replica lag | Reads from primary for strong; replica for eventual |
| Memory pressure | Evict; reject Sets with OOM policy; shed load |
| Rebalance stampede | Rate-limited moves; handoff protocol |
| Split-brain primary | Membership epoch + lease / quorum |
| Huge value | Reject or spill to SSD tier (Phase 1.5) |
| Negative caching | Short TTL for DB 404 |
| Clock skew TTL | Prefer relative TTL + server expiry timestamp |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Nodes | 20 | 200 | 2K | 20K |
| Aggregate DRAM | 10 TB | 100 TB | 1 PB | 10 PB |
| Get QPS | 1M | 10M | 100M | 1B |
| Set QPS | 100K | 1M | 10M | 100M |
| Avg value | 1 KB | 1 KB | mixed | mixed |
| Working set | 5 TB | 50 TB | 500 TB | multi-PB (tiered) |
| Keys | 5B | 50B | 500B | 5T (meta sparse) |
| Hot key QPS (single) | 100K | 500K | 2M | 10M+ |
| Clusters / cells | 1 | 1–few | many | many global cells |

**What each jump forces:**

- **10×:** Proxies or smarter clients; pipeline/batch; hot-key service; careful rebalance.  
- **100×:** Cell/cluster sharding by keyspace or tenant; SSD tier; hierarchical L0 client caches.  
- **1,000×:** Federated cells; no single global ring; approximate global membership; heavy isolation.

### 1.5 Etc. (Constraints & Assumptions)

- **Clarify early:** cache-aside vs write-through vs write-back; consistency; value size; multi-AZ.  
- Keys hashed to partitions; apps should avoid unbounded cardinality explosions.  
- Prefer **immutable versions** or short TTL for coherence when DB updates.  
- Cache loss must not corrupt SoT.  
- Google interview flavor: tradeoffs and partitioning math > naming internal systems.

**Scope statement:**

> Design a distributed memory cache: consistent hashing with virtual nodes, RF replication, eviction under memory budgets, hot-key defenses, membership and rebalance, and explicit consistency/write-policy tradeoffs—scaling from tens of nodes to multi-cell deployments without pretending the cache is the database.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Get hit** | DRAM read | ~1M/s | ~10M/s | Cache nodes |
| **Get miss** | DB + fill | ~5–20% of Gets | ×10 | DB + network |
| **Set / fill** | Write memory + replica | ~100K/s | ~1M/s | Primaries |
| **Eviction** | Background / on-demand | continuous | — | CPU/mem |
| **Replication bytes** | RF-1 copies | Sets × value × (RF-1) | ×10 | NIC |
| **Membership gossip** | Heartbeats | trivial | watch fanout | Control |

**Anti-pattern:** one “QPS” mixing hits, misses, and multi-get fanout.

### 2.2 Memory budgeting

```text
Usable DRAM per node ≈ 0.7–0.8 × RAM  (OS, fragmentation, indexes)
20 nodes × 512 GB × 0.75 ≈ 7.5 TB usable ≈ order(10 TB) with headroom story

Per entry overhead:
  key 32B + value 1KB + meta 40–80B ≈ ~1.1 KB
5B keys × 1.1 KB = 5.5 TB → fits baseline if working set ≈ stored set
If working set 5 TB and RF=3 without shared storage:
  raw replica bytes 15 TB → need more nodes OR accept RF with primary-only storage + replica subset
```

**Say explicitly:** RF multiplies memory unless replicas are for HA of the same partitioned data (yes—RF=3 means ~3× memory for the keyspace). Working set W with RF=r needs ≈ `W * r / utilization` cluster DRAM.

### 2.3 Network

```text
1M Get/s × 1 KB = 1 GB/s aggregate response (plus headers)
Set 100K/s × 1 KB × (RF-1=2) repl = 200 MB/s replication
NIC 25–100 Gbps nodes: design shard so no node > ~50% NIC
```

### 2.4 Hot key amplification

```text
Key K at 500K QPS on one primary with 1 KB values ≈ 500 MB/s from one node → melts
Mitigations must move QPS off a single owner
```

### 2.5 Miss / stampede cost

```text
Without coalesce: 10K concurrent miss → 10K DB reads
With singleflight: 1 DB read; 10K waiters
DB connection pools saved = the product feature
```

### 2.6 Rebalance cost

```text
Add 10% capacity → move ~10% keys (with vnodes, smoother)
Moving 0.5 TB over 1 Gbps ≈ 4000+ s naive → rate-limit + parallel vnode handoff
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `Get(key)` | Value + version/TTL remaining or miss |
| `Set(key, value, ttl, cas?)` | Store; optional CAS |
| `Del(key)` | Delete + replicate delete |
| `GetMulti(keys[])` | Batch; group by partition |
| `Touch(key, ttl)` | Refresh expiry |
| `Incr` (optional) | Single-key atomic |

### 3.2 Write-path policies

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| **Cache-aside** | Simple; DB SoT clear | App must invalidate/Set | **MVP default** |
| **Write-through** | Cache warm on write | Write latency + coupling | Session / config |
| **Write-back** | Fast writes | Durability risk | Only with WAL + bounded RPO |
| Write-around | Avoid pollution | Cold after write | Large infrequent writes |

**Deal-breaker:** write-back marketed as “never lose data” without WAL, fsync policy, and replay.

### 3.3 Partitioning: consistent hashing + virtual nodes

```text
hash(key) → ring position
each physical node owns many vnodes (e.g. 100–200)
key → successor vnode owner = primary
next RF-1 distinct physical nodes = replicas
```

| Approach | Pros | Cons |
|----------|------|------|
| Mod-N hashing | Simple | Remap almost all keys on N±1 |
| **Consistent hash + vnodes** | Small remaps; balance | Implementation care |
| Range partitioning | Locality | Hot ranges; complex split |
| Proxy directory | Flexible | Extra hop / control plane |

**Chosen MVP:** consistent hashing with virtual nodes; smart client or thin proxy.

**Deal-breaker:** mod-N at 200 nodes with frequent scale events (miss storms).

### 3.4 Replication

| Mode | Latency | Consistency | Use |
|------|---------|-------------|-----|
| Async RF | Low Set | Replica stale window | **Default cache** |
| Sync to quorum | Higher Set | Stronger read options | Session critical |
| Chain replication | Ordered | Ops complexity | Optional |

**Failover:** membership detects death → promote secondary → bump epoch → clients refresh.

### 3.5 Consistency models

| Model | Guarantee | Cost |
|-------|-----------|------|
| Best-effort / eventual | Fast; stale OK | Cheapest |
| Primary reads | Read-your-writes if sticky | Primary load |
| Quorum R+W>RF | Stronger | Latency; still not DB |
| Linearizable | Hard | Usually wrong goal for cache |

**Chosen MVP:** write primary + async replicas; Get from primary by default; optional `Get(prefer_replica)` for read-heavy stale-OK keys.

### 3.6 Eviction policies

| Policy | Pros | Cons | Fit |
|--------|------|------|-----|
| LRU | Simple | Weak scan resistance | OK baseline |
| LFU | Frequency | Aging needed | Hot keys |
| **TinyLFU + SLRU** | Excellent admission | More moving parts | **Strong default** |
| TTL-only | Simple | No pressure handling | Insufficient alone |
| Random | Tiny CPU | Worse hit rate | Emergency OOM |

**Chosen:** size-aware eviction with TinyLFU admission (or segmented LRU) + TTL. Per-tenant quotas.

### 3.7 Hot-key mitigation

| Technique | How | Tradeoff |
|-----------|-----|----------|
| **Request coalescing** | Singleflight miss/Get | Helps misses more than hits |
| **Client L0 cache** | Process-local TTL cache | Stale; huge win for ultra-hot |
| **Replicate hot key to N nodes** | Read any copy | Coordination; memory |
| **Key splitting** | App shards logical key | Needs app cooperation |
| **Hedged reads** | Rare | Amplification risk |

### 3.8 Membership

| System | Pros | Cons | Use |
|--------|------|------|-----|
| **Gossip (SWIM)** | Scalable; no external dep | Convergence time | Large clusters |
| **ZK / etcd** | Strong membership view | External; watch storms | **MVP medium size** |
| Static config | Simple | Elasticity pain | Tiny |

**Chosen MVP:** etcd/ZK for cluster membership + shard map epoch; gossip optional at 100× for failure detection tip.

### 3.9 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| SoT | DB / backing | Cache ephemeral | Cache-only durable money |
| Partition | CH + vnodes | Elasticity | Mod-N remaps |
| RF | 3 async | HA without sync tax | RF=1 for critical sessions |
| Eviction | TinyLFU/SLRU | Hit rate under scan | Unbounded memory |
| Hot keys | L0 + replicate | Skew reality | “Hash will save us” |
| Writes | Cache-aside | Clear durability | Silent write-back |
| Membership | etcd map + epoch | Deterministic routing | Gossip-only without epoch fencing |

---

## 4. Architecture Diagram

```text
  App / Service
       |
       v
  +---------------------+
  | Client library      |
  | L0 local cache      |
  | singleflight        |
  | ring / shard map    |
  +----------+----------+
             |
      Get/Set by key hash
             |
     +-------+--------+
     |  Proxy (opt)   |  optional at 10× for polyglot clients
     +-------+--------+
             |
    +--------+---------+--------+
    v        v         v        v
  Node A   Node B    Node C   Node D   ...
  (vnode primaries + replicas)
    |        |
    +---+----+
        v
   Replication (async)
        |
        v
  +-----------+     +------------------+
  | etcd / ZK |     | Metrics/Hotkey   |
  | membership|     | detector service |
  +-----------+     +------------------+

  Miss path: Client -> Cache miss -> DB/backing -> Set -> return
```

**Get hit path:**

```text
Client.hash(key) -> primary node -> DRAM -> value
```

**Get miss + coalesce:**

```text
N waiters -> leader loads DB -> Set(primary) -> replicate -> release waiters
```

**Hot key path:**

```text
Detector flags key -> controller: replicate to N nodes / instruct clients L0 TTL
Subsequent Gets: any replica or L0
```

**Membership change:**

```text
Node down -> etcd epoch++ -> new shard map -> clients watch update
  -> handoff vnodes (rate-limited) -> old primary read-only then remove
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **DB/backing remains SoT** for cache-aside MVP.  
2. **Single-key operations atomic** on primary.  
3. **Shard map epoch fencing**—ignore requests with stale epoch.  
4. **Never return corrupt values**—CRC optional on value frames.  
5. **Replication deletes** propagate (or TTL heals).  
6. **Memory hard limit**—evict or reject; never OOM-kill silently as strategy.

#### 5.1.2 Data loss prevention

| Path | Risk | Mitigation |
|------|------|------------|
| Cache-aside Set loss | Stale miss | DB still correct |
| Write-through fail | Partial | Commit DB then cache; or TX outbox |
| Write-back | Node death loses writes | WAL to disk + RF; bounded RPO |
| Replica only | Stale read | Primary reads |

#### 5.1.3 Retries & idempotency

- Client retries Get freely (read-only).  
- Set with CAS for concurrency.  
- Idempotency-Key for write-through to DB.  
- Hedged Get only with server coalescing awareness.

#### 5.1.4 Rate limits & admission

- Per-tenant QPS and memory quotas.  
- Reject Sets when eviction can’t keep up (`OOM` / `busy`).  
- Miss admission: limit concurrent fills per node to protect DB.

#### 5.1.5 Thundering herd

| Scenario | Mitigation |
|----------|------------|
| Cold start miss storm | Singleflight; probabilistic early refresh |
| TTL aligned expiry | Jitter TTL |
| Hard fail node | Soft request hedging carefully; warmup |
| Rebalance | Rate-limited key move; dual-read during handoff |

#### 5.1.6 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Hot key | L0 + detect |
| 10× | Rebalance miss storm | Vnode handoff protocol |
| 100× | etcd watch overload | Sharded maps / gossip hybrid |
| 1,000× | Global ring myth | Cells; no single membership domain |

### 5.2 Scalability

#### 5.2.1 Traffic ups/downs

- Horizontal add nodes; vnode migration.  
- Autoscale carefully—cold nodes cause miss storms; pre-warm critical keys.  
- Read scale via replicas; write scale via more partitions.

#### 5.2.2 Storage / memory

| Scale | Strategy |
|-------|----------|
| Baseline | Pure DRAM |
| 10× | Tighter slabs; compression for cold-ish keys |
| 100× | SSD second tier (L2) for large/cold |
| 1,000× | Tiered + cell-local working sets |

#### 5.2.3 Parallelization

- Pipelining / batching on client connections.  
- GetMulti groups by partition → parallel RPCs.  
- Replica catch-up parallel per vnode.

#### 5.2.4 Progressive scale evolution

| Jump | Change |
|------|--------|
| →10× | Proxies; hot-key controller; pipelining; connection pools |
| →100× | Cells by tenant/key-range; SSD tier; client L0 ubiquitous |
| →1,000× | Federated cells; local membership; cross-cell only for rare global keys |

#### 5.2.5 Hot-key deep dive

```text
Detection: per-key QPS counters with Count-Min Sketch on each node
Threshold T: e.g. > 50K QPS or > 5% node CPU/NIC
Actions (escalation):
  1) Client L0 with short TTL (e.g. 50–200ms)
  2) Replicate key to R_hot additional nodes; client RR/random
  3) Application split (user shards) for logical hotspots
Cooldown: remove extra replicas when cool
```

#### 5.2.6 Consistency vs scale

Stronger quorum reads don’t scale as well as primary-or-replica choice. Prefer **short TTL + invalidation** over global linearizability.

### 5.3 Maintainability

#### 5.3.1 Operability

- Drain node: mark no new vnodes; migrate; quiesce.  
- Bounce: replica promotion tested.  
- Chaos: kill primary; assert failover < SLO; measure miss blip.

#### 5.3.2 Versioning & rollout

- Binary canary per cell.  
- Shard-map format versioned.  
- Client library compatibility N/N-1.

#### 5.3.3 Observability

| Metric | Why |
|--------|-----|
| `hit_ratio` | Effectiveness |
| `evict_qps` / `evict_bytes` | Pressure |
| `p99_get` / `p99_set` | SLO |
| `replica_lag` | Stale risk |
| `hot_keys` | Skew |
| `fill_coalesce_factor` | Stampede health |
| `rebalance_bytes` | Elasticity cost |
| `oom_reject` | Admission |

#### 5.3.4 Testing

- Jepsen-ish partition tests for epoch fencing.  
- Hot-key load tests.  
- Rebalance under traffic.  
- Eviction correctness (TTL + LRU interaction).  
- Multi-get correctness under partial failures.

#### 5.3.5 Config surface

```text
rf=3
vnode_count_per_node=128
eviction=tinylfu
max_value=1MB
default_ttl=300s
hot_key_qps_threshold=50000
l0_client_ttl_ms=100
fill_max_inflight_per_node=2000
```

---

## 6. Wrap-Up

### 6.1 What we designed

A **distributed cache** with consistent hashing and virtual nodes, RF replication, memory-budgeted eviction (TinyLFU/SLRU + TTL), cache-aside as default write policy, etcd/ZK membership with epoch fencing, and explicit hot-key / thundering-herd defenses—evolving from one cluster to multi-cell at extreme scale.

### 6.2 Invariants to memorize

| Invariant | Why |
|-----------|-----|
| Cache ≠ SoT (MVP) | Durability clarity |
| Vnodes for elasticity | Avoid mod-N storms |
| RF costs memory | Capacity planning |
| Hot keys need special case | Hashing doesn’t fix skew |
| Singleflight on miss | Protect DB |
| Epoch fencing | Split-brain safety |

### 6.3 What you'd say in the last 5 minutes

> “I’d clarify write policy and consistency first. Then: consistent hashing with vnodes, RF=3 async replication, primary reads by default, TinyLFU eviction under a hard memory budget, and hot-key playbook—client L0 plus dynamic replication. Membership via etcd with epoch fencing. At 100× we cell the ring; we never pretend a global linearizable cache at a billion QPS.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Partitioning & consistent hashing

**Q1: Why virtual nodes?**  
A: Better load balance; smoother moves; isolate noisy physical nodes.

**Q2: How many vnodes?**  
A: Tens–hundreds per node; trade memory of ring vs balance.

**Q3: Difference vs mod-N?**  
A: Mod-N remaps most keys on scale; CH remaps ~1/N.

**Q4: Where is the ring stored?**  
A: In clients and/or proxies; updated on membership epoch.

**Q5: Ketama vs rendezvous hashing?**  
A: Both fine; rendezvous easy for “top N replicas.”

### 7.2 Replication & CAP

**Q6: Why async replication for cache?**  
A: Set latency; stale OK if DB SoT.

**Q7: When sync quorum?**  
A: Session tokens where stale read breaks auth UX.

**Q8: CAP choice?**  
A: Usually AP + regenerate from DB; not CP money store.

**Q9: Read repair?**  
A: Optional; often TTL/expiry simpler for cache.

**Q10: Replica placement?**  
A: Distinct racks/AZs; never all RF on one host.

### 7.3 Eviction & memory

**Q11: LRU vs LFU?**  
A: LRU fails on scans; LFU needs aging; TinyLFU admits winners.

**Q12: How to size memory?**  
A: Working set × RF / utilization + headroom; measure hit rate curve.

**Q13: Slab allocators?**  
A: Reduce fragmentation (memcached-style); internal fragmentation tradeoff.

**Q14: TTL vs LRU interaction?**  
A: Lazy expiry on access + periodic sampling; LRU among live keys.

**Q15: What if Set when full?**  
A: Evict victims until fit or reject; never unbounded growth.

### 7.4 Hot keys

**Q16: Why doesn’t hashing fix hot keys?**  
A: Popularity is Zipfian on keys, not uniform on hash space.

**Q17: Client L0 risks?**  
A: Staleness; bound with short TTL + invalidation hooks.

**Q18: Dynamic replication protocol?**  
A: Controller updates “hot map”; clients fan-out reads; primary still owns writes.

**Q19: Count-Min Sketch?**  
A: Approximate frequency with tiny memory—good detector.

**Q20: Can you split a hot key?**  
A: Only if app semantics allow (e.g., counters → sharded counters + sum).

### 7.5 Consistency & write policies

**Q21: Cache-aside invalidation bug?**  
A: Race: update DB, then stale Set from concurrent reader—use version/CAS or delete-on-write.

**Q22: Write-through vs aside?**  
A: Through keeps warm; aside simpler and common.

**Q23: Write-back when?**  
A: Burst absorption with WAL; rare for general cache interviews unless asked.

**Q24: Read-your-writes?**  
A: Sticky to primary or client session remember version.

**Q25: CAS usage?**  
A: Lost-update prevention on concurrent Set.

### 7.6 Membership

**Q26: Gossip vs ZK?**  
A: Gossip scales detection; ZK/etcd gives linearizable config—hybrid common.

**Q27: What is an epoch?**  
A: Monotonic membership generation; fence old primaries.

**Q28: Split-brain primary?**  
A: Lease in etcd; minority can’t extend lease.

**Q29: Watch storms at 2K nodes?**  
A: Hierarchical maps; push shard deltas; avoid full-map payload every time.

**Q30: Graceful drain?**  
A: Remove from ring gradually; keep serving until handoff complete.

### 7.7 Thundering herd & stampedes

**Q31: Singleflight scope?**  
A: Per-process first; cluster-wide needs lease/coordinator.

**Q32: Probabilistic early expire?**  
A: Desynchronize TTL refresh under load (`xfetch`).

**Q33: Negative caching?**  
A: Cache misses briefly; prevent DB hammer on absent keys.

**Q34: Cache warming?**  
A: Preload critical keys before event; rate-limit.

### 7.8 Load balancing & clients

**Q35: Smart client vs proxy?**  
A: Smart=lower hop; proxy=polyglot + connection concentration.

**Q36: Connection explosion?**  
A: Proxies or mux; at 10× often needed.

**Q37: Longest connection / slow client?**  
A: Timeouts; backpressure; bounded queues.

**Q38: Multi-get partial failure?**  
A: Return partial + errors; client may fall back DB per key.

### 7.9 Algorithms & indexing

**Q39: Hash function?**  
A: xxHash/Murmur; cryptographic hash unnecessary.

**Q40: Expiry data structure?**  
A: Timing wheel / hierarchical wheel for large key counts.

**Q41: Scan-resistant eviction?**  
A: Probationary segment; TinyLFU admission.

**Q42: Compression?**  
A: CPU vs memory; value-size dependent.

### 7.10 DB & storage interplay

**Q43: What DB behind cache?**  
A: Whatever SoT is—SQL/KV; cache shouldn’t require a specific DB.

**Q44: Should cache persist?**  
A: Optional; persistence ≠ make it primary without consensus story.

**Q45: CDC invalidation?**  
A: Strong pattern: DB change stream → delete keys.

### 7.11 Interview craft

**Q46: How to open?**  
A: Clarify SoT, write policy, consistency, value sizes, QPS, working set, skew.

**Q47: Numbers that matter?**  
A: Working set × RF, QPS × value size, hot-key QPS, miss% × DB capacity.

**Q48: Common trap?**  
A: Designing Redis-cluster trivia without hot keys, eviction, or membership fencing.

**Q49: L5+ signal?**  
A: Progressive scale to cells; explicit deal-breakers; memory math.

**Q50: Related designs?**  
A: CDN edge cache, file cache, session store—same fundamentals, different skew.

---

### Appendix A — Consistent hashing sketch

```text
for node in nodes:
  for i in 0..V-1:
    ring[hash(node.id + ":" + i)] = node
primary(key) = first node clockwise from hash(key)
replicas = next distinct nodes clockwise
```

### Appendix B — Cache-aside pseudocode

```text
Get(k):
  v = cache.Get(k)
  if v: return v
  return singleflight(k):
    v = db.Get(k)
    if v: cache.Set(k, v, ttl=jitter(T))
    else: cache.SetNeg(k, short_ttl)
    return v

OnDbUpdate(k, new):
  db.Write(k, new)
  cache.Del(k)          # prefer delete over Set to avoid race
```

### Appendix C — Write-through / write-back

```text
WriteThrough(k,v):
  db.Write(k,v)         # success required
  cache.Set(k,v)

WriteBack(k,v):
  cache.SetDirty(k,v)   # WAL append
  ack client
  async flush db
```

### Appendix D — Hot-key escalation

| Level | Action | Staleness |
|-------|--------|-----------|
| L0 | Client TTL 50–200ms | Bounded |
| L1 | Extra read replicas N=2..10 | Write path still primary |
| L2 | App key split | Semantic |

### Appendix E — Memory worksheet

```text
DRAM_cluster_needed ≈ working_set_bytes * RF / 0.7
Example: WS=5TB, RF=3 → ~21 TB raw DRAM installed
```

### Appendix F — Progressive scale table

| Scale | Topology | Hot keys | Membership |
|-------|----------|----------|------------|
| Baseline | 1 ring | Manual L0 | etcd |
| 10× | Proxies | Detector + replicate | etcd + rate-limited rebalance |
| 100× | Cells | L0 default | Per-cell etcd |
| 1,000× | Many cells | App cooperation | Federated; no global ring |

### Appendix G — NFR card

```text
Get p99 < 5ms in-AZ
RF=3 async default
Hard memory limit + eviction
Singleflight misses
Hot-key playbook mandatory
Epoch-fenced membership
Cache ≠ SoT
```

### Appendix H — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just Redis Cluster” | Still need policies: eviction, hot keys, write path |
| “RF=1 is fine” | Node death ⇒ cold miss storm |
| “Strong consistency everywhere” | Wrong default for cache |
| “Hashing fixes skew” | Zipf keys disagree |

### Appendix I — Eviction comparison

| Property | LRU | LFU | TinyLFU+SLRU |
|----------|-----|-----|--------------|
| Scan resistance | Weak | Stronger | Strong |
| Complexity | Low | Med | Med |
| Practice | Ubiquitous | Common | Caffeine-like |

### Appendix J — Membership event timeline

```text
t0 node B fails health checks
t1 etcd session expires; epoch=42→43
t2 clients/proxies observe new map
t3 promote replicas of B’s vnodes
t4 re-replicate to restore RF
t5 miss ratio blip then recover
```

### Appendix K — Multi-get planning

```text
GetMulti(keys):
  group by primary
  parallel RPC per primary
  merge; for misses optional parallel DB (coalesced)
```

### Appendix L — Deal-breaker catalog

| Choice | Deal-breaker when |
|--------|-------------------|
| Write-back w/o WAL | Money/order writes |
| Mod-N hashing | Frequent resizing |
| No hot-key plan | Celebrity key traffic |
| Unbounded memory | Kernel OOM as policy |
| Cache as SoT | Durability requirements |

### Appendix M — Related systems

| System | Relation |
|--------|----------|
| CDN | Geo edge cousin |
| File cache | Large-object cousin |
| Redis/Memcached | Implementation analogs |
| DB buffer pool | Single-node cousin |

### Appendix N — Non-goals

- Cross-key serializability  
- Global linearizability at 1B QPS  
- Replacing the database  
- Perfect zero-stale under all partitions  

### Appendix O — Worked hot-key numbers

```text
Celebrity key 1M QPS × 500B = 500 MB/s
1 node 25 Gbps NIC theoretical ~3 GB/s raw—but CPU/RPC caps earlier
With 10-way read expand + L0 90% hit: origin node ~50–100K QPS survivable
```

### Appendix P — Rebalance handoff

```text
for vnode in moving:
  pause writes OR dual-write
  copy keys old → new
  flip map epoch for vnode
  catch-up tail
  decommission old
rate_limit copy MB/s
```

### Appendix Q — Observability red flags

| Signal | Meaning |
|--------|---------|
| hit_ratio ↓ + evict ↑ | Undersized memory |
| p99 ↑ one node | Hot shard / hot key |
| replica_lag ↑ | NIC/CPU saturation |
| fill_inflight ↑ | Miss storm / DB slow |
| oom_reject ↑ | Admission failing |

### Appendix R — Security / multi-tenant

- AUTH + TLS; per-tenant ACL prefixes.  
- Memory/QPS quotas.  
- Dangerous `FLUSH` admin-only.  
- No cross-tenant key access.

### Appendix S — 30s scale narrative

> Baseline: CH+vnodes, RF=3, cache-aside, TinyLFU, etcd epochs. 10× adds proxies and hot-key replication. 100× cells the cluster and adds SSD tiers. 1,000× is many cells—no single global ring—with L0 caches everywhere for Zipf traffic.

### Appendix T — Glossary

| Term | Meaning |
|------|---------|
| Vnode | Virtual node on hash ring |
| RF | Replication factor |
| Singleflight | Coalesce in-flight work |
| TinyLFU | Admission filter via approximate frequency |
| Epoch | Membership generation for fencing |
| Cache-aside | App reads DB on miss; cache filled by app |
| Write-back | Cache acknowledges early; flushes later |

### Appendix U — Interview whiteboard order

1. Requirements: SoT, write policy, consistency, sizes  
2. API + memory math (WS × RF)  
3. Consistent hashing + RF placement  
4. Get/Set paths + singleflight  
5. Eviction + TTL  
6. Hot keys  
7. Membership/failover  
8. 10×/100×/1000×  

### Appendix V — Sample error catalog

| Code | When |
|------|------|
| `MISS` | Not an error—caller fills |
| `CAS_FAIL` | Version mismatch |
| `OOM` / `BUSY` | Memory pressure reject |
| `NOT_PRIMARY` | Stale epoch / redirected |
| `VALUE_TOO_LARGE` | Over max_value |
| `TIMEOUT` | Peer/DB slow |

### Appendix W — Consistency cheatsheet

| Read mode | Stale window | Load |
|-----------|--------------|------|
| Primary | ~repl lag 0 for writes seen | Hot primary |
| Replica | Async lag | Scaled reads |
| Quorum | Low | Higher latency |
| L0 client | TTL bound | Best for ultra-hot |

### Appendix X — Why ambiguity > Google trivia

Interviewers score **clarifying questions, correct tradeoffs, and progressive scale**. Naming an internal system without explaining vnodes, RF memory multiply, and hot keys is weaker than a crisp generic design with numbers.

---

*End of Distributed Cache system design.*
