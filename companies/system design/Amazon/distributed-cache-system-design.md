# System Design: Distributed Cache (ElastiCache-Class)

> **Focus areas:** Partitioning · Consistent hashing · Replication · Eviction (LRU/LFU/TTL) · Hot keys · Cache stampede · Consistency (aside/through/write-back) · Membership · Multi-AZ  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Amazon SDE III — practicality, reliability, efficiency, operational ownership (ElastiCache / DynamoDB Accelerator–class thinking without trivia dump)  
> **Quality bar:** Working-set × RF memory math, explicit write-policy deal-breakers, hot-key + stampede playbooks, Multi-AZ membership fencing

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound a distributed in-memory (optionally SSD-tier) key-value cache** that accelerates reads—and carefully manages writes—in front of durable databases or services. Emphasize **partitioning, replication, eviction, hot keys, stampede control, consistency/write policies, membership, and Multi-AZ**. This is **not** a durable primary store unless the interviewer explicitly wants “Redis as DB”—push back and separate concerns.

### 1.0 What this is / is not

| Dimension | **Distributed cache (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Low-latency Get/Set; absorb DB load | Source of truth / ACID OLTP |
| Success | Hit rate, p99 Get, stability under skew & AZ loss | Never lose durable writes (unless write-back + WAL) |
| Data | Opaque KV + TTL/version | Rich secondary indexes in MVP |
| Failure | Node loss ⇒ miss / rebuild from SoT | Data loss of SoT |

**Amazon framing:** “Think ElastiCache-class: Multi-AZ, clear customer isolation, operational runbooks, efficiency of memory and NIC—not a substitute for DynamoDB/Aurora.”

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | `Get` / `Set` / `Del` / `GetMulti`; optional CAS | Memcached/Redis-like |
| F2 | Value size? | Mostly < 1 MB; reject/spill huge | Slabs / size limits |
| F3 | TTL? | Per-key; default TTL | Expiry wheel; lazy + active |
| F4 | Eviction? | When memory full | LRU / LFU / TinyLFU + TTL |
| F5 | Replication? | RF=3 typical; Multi-AZ | Async default; sync optional |
| F6 | Consistency? | Tunable; often eventual OK | Document model; primary reads |
| F7 | Write path? | Cache-aside common; WT/WB discussed | Client library patterns |
| F8 | Hot keys? | Yes—must not melt one shard | L0 / replicate / coalesce |
| F9 | Stampede? | Miss storms on expiry / failover | Singleflight; jitter; neg-cache |
| F10 | Transactions? | No multi-key TX MVP | Single-key atomicity |
| F11 | Persistence? | Optional AOF/snapshot Phase 2 | Memory-first MVP |
| F12 | Multi-tenant? | Namespaces + memory/QPS quotas | Noisy-neighbor isolation |
| F13 | Multi-AZ? | Required for production HA | Replica placement + failover |
| F14 | Invalidation? | TTL + explicit Del; optional CDC | Coherence story |

**MVP functional scope:**

1. Clustered KV: Get/Set/Del with TTL; optional CAS (`version` / `cas_id`).  
2. Partitioning via **consistent hashing + virtual nodes**.  
3. Replication factor RF (default 3) across AZs; failover on node death.  
4. Memory budgeting + eviction (LRU baseline or TinyLFU + SLRU).  
5. Client routing (smart client or proxy).  
6. Hot-key mitigation: request coalescing, client L0, optional dynamic replication.  
7. Stampede controls: singleflight, TTL jitter, negative caching, fill admission.  
8. Membership via etcd/ZK (or equivalent control plane) with **epoch fencing**; Multi-AZ.  
9. Metrics: hit rate, eviction, hot-key detectors, p99, memory, replica lag.

**Out of MVP:**

- Multi-key serializable transactions  
- Full Redis data structures (streams, ZSET) unless asked—keep KV core  
- Cross-region strongly consistent active-active  
- Disk as primary SoT (that’s a database)  
- Exactly-once write-back without WAL + bounded RPO story  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Get latency | Memory path | p50 < 1ms; p99 < 5ms in-AZ |
| N2 | Availability | High for cache tier | 99.9%+; degrade to DB on miss |
| N3 | Durability | Cache ephemeral MVP | DB is SoT; optional WB WAL later |
| N4 | Hit rate | Workload dependent | Design for ≥80–95% when WS fits |
| N5 | Consistency | Tunable | Default: per-key RW to primary |
| N6 | Elasticity | Add/remove nodes | Controlled rebalance; minimize miss storm |
| N7 | Skew tolerance | Hot keys inevitable | Explicit mitigations |
| N8 | Multi-AZ | Survive AZ loss | RF across AZs; paced failover |
| N9 | Efficiency | Memory + NIC | Utilization targets; avoid over-replication waste |
| N10 | Operability | Clear ownership | Drain, dashboards, customer quotas |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Cache-aside Get hit → return.  
2. Miss → singleflight to DB → Set → return.  
3. Set on primary → async replicate to RF−1 secondaries in other AZs.  
4. Node drain → ownership migrates → clients update ring epoch.  
5. Hot key detected → replicate to N nodes and/or enable client L0.  
6. TTL expiry with jitter → staggered refresh, no herd.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Thundering herd on miss | Singleflight / request coalescing; fill rate limit |
| Hot key on one vnode | Detect; L0; replicate; split key if logical |
| Network partition | Prefer AP for cache; stale reads possible; fence primary with lease |
| Replica lag | Reads from primary for stronger freshness; replica for stale-OK |
| Memory pressure | Evict; reject Sets with OOM/BUSY; shed fills |
| Rebalance stampede | Rate-limited vnode handoff; dual-read window |
| Split-brain primary | Membership epoch + lease / quorum |
| AZ failure | Promote replicas in surviving AZs; restore RF |
| Huge value | Reject or spill to SSD tier (Phase 1.5) |
| Negative caching | Short TTL for DB 404 / empty |
| Clock skew TTL | Relative TTL + server expiry timestamp |
| Cache-aside race | Update DB then Del (not Set) to avoid stale fill |
| Write-back node death | WAL + RF or accept RPO — must be explicit |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Nodes | 20 | 200 | 2K | 20K |
| AZs / region | 3 | 3 | 3+ | multi-region cells |
| Aggregate DRAM | 10 TB | 100 TB | 1 PB | 10 PB |
| Get QPS | 1M | 10M | 100M | 1B |
| Set QPS | 100K | 1M | 10M | 100M |
| Avg value | 1 KB | 1 KB | mixed | mixed |
| Working set | 5 TB | 50 TB | 500 TB | multi-PB (tiered) |
| Keys | 5B | 50B | 500B | 5T (meta sparse) |
| Hot key QPS (single) | 100K | 500K | 2M | 10M+ |
| Clusters / cells | 1 | 1–few | many | many global cells |
| Tenants (if multi-tenant) | 1K | 10K | 100K | 1M+ |

**What each jump forces:**

- **10×:** Proxies or smarter clients; pipeline/batch; hot-key service; careful Multi-AZ rebalance.  
- **100×:** Cell/cluster sharding by keyspace or tenant; SSD tier; hierarchical L0 client caches.  
- **1,000×:** Federated cells; no single global ring; approximate global membership; heavy isolation.

### 1.5 Etc. (Constraints & Assumptions)

- **Clarify early:** cache-aside vs write-through vs write-back; consistency; value size; Multi-AZ; multi-tenant.  
- Keys hashed to partitions; apps should avoid unbounded cardinality explosions.  
- Prefer **delete-on-write** or versioned values for coherence when DB updates.  
- Cache loss must not corrupt SoT.  
- Amazon signal: Multi-AZ placement, noisy-neighbor quotas, efficiency of memory (RF multiplies cost), ownership of failover runbooks.

**Scope statement:**

> Design a distributed memory cache with consistent hashing and virtual nodes, Multi-AZ RF replication, eviction under hard memory budgets, hot-key and stampede defenses, membership with epoch fencing, and explicit consistency/write-policy tradeoffs—scaling from tens of nodes to multi-cell deployments without pretending the cache is the database.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Get hit** | DRAM read | ~1M/s | ~10M/s | Cache nodes |
| **Get miss** | DB + fill | ~5–20% of Gets | ×10 | DB + network |
| **Set / fill** | Write memory + replica | ~100K/s | ~1M/s | Primaries |
| **Eviction** | Background / on-demand | continuous | — | CPU/mem |
| **Replication bytes** | RF−1 copies | Sets × value × (RF−1) | ×10 | NIC / AZ |
| **Membership** | Heartbeats / watches | trivial | watch fanout | Control |
| **Hot-key L0** | Client local | absorbs Zipf | critical at 100× | App hosts |

**Anti-pattern:** one “QPS” mixing hits, misses, multi-get fanout, and replication traffic.

### 2.2 Memory budgeting (say this out loud)

```text
Usable DRAM per node ≈ 0.7–0.8 × RAM  (OS, fragmentation, indexes, replication buffers)
20 nodes × 512 GB × 0.75 ≈ 7.5 TB usable ≈ order(10 TB) with headroom story

Per entry overhead:
  key 32B + value 1KB + meta 40–80B ≈ ~1.1 KB
5B keys × 1.1 KB = 5.5 TB → fits baseline if working set ≈ stored set

RF=3 means ~3× memory for the keyspace (replicas hold copies):
  DRAM_cluster_needed ≈ working_set_bytes × RF / utilization
  Example: WS=5TB, RF=3, util=0.7 → ~21 TB installed DRAM
```

**Efficiency / frugality signal:** RF is a reliability tax on memory spend—defend RF=3 for Multi-AZ HA; don’t silently assume RF=1 in prod.

### 2.3 Network

```text
1M Get/s × 1 KB = 1 GB/s aggregate response (+ headers)
Set 100K/s × 1 KB × (RF-1=2) repl = 200 MB/s replication
Cross-AZ replication may cost more (bandwidth $$$ + latency) — place RF across AZs but keep primary-Get in-AZ when possible
NIC 25–100 Gbps nodes: design shard so no node > ~50% NIC
```

### 2.4 Hot key amplification

```text
Key K at 500K QPS on one primary with 1 KB values ≈ 500 MB/s from one node → melts
Mitigations must move QPS off a single owner (L0, replicate, split)
Hashing alone never fixes Zipfian popularity
```

### 2.5 Miss / stampede cost

```text
Without coalesce: 10K concurrent miss → 10K DB reads
With singleflight: 1 DB read; 10K waiters
Aligned TTL expiry on popular key → same herd — add jitter / probabilistic early refresh
DB connection pools saved = the product feature
```

### 2.6 Rebalance / AZ failover cost

```text
Add 10% capacity → move ~10% keys (vnodes smoother than mod-N)
Moving 0.5 TB over 1 Gbps ≈ 4000+ s naive → rate-limit + parallel vnode handoff
AZ loss: promote many vnodes at once — pace restores of RF; expect miss ratio blip
```

### 2.7 Multi-get fanout

```text
GetMulti(100 keys) across 20 primaries → up to 20 RPCs
Batch/group by primary; bound parallelism; partial failure returns mixed results
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

**Deal-breaker:** write-back marketed as “never lose data” without WAL, fsync policy, Multi-AZ replay, and explicit RPO.

**Cache-aside race (classic):**

```text
Writer: DB.update(k) then cache.Del(k)     # prefer Del over Set
Reader: Get miss → DB.read (old?) → Set    # still possible; use version/CAS or CDC Del
```

### 3.3 Partitioning: consistent hashing + virtual nodes

```text
hash(key) → ring position
each physical node owns many vnodes (e.g. 100–200)
key → successor vnode owner = primary
next RF-1 distinct physical nodes (prefer other AZs) = replicas
```

| Approach | Pros | Cons |
|----------|------|------|
| Mod-N hashing | Simple | Remap almost all keys on N±1 |
| **Consistent hash + vnodes** | Small remaps; balance | Implementation care |
| Range partitioning | Locality | Hot ranges; complex split |
| Proxy directory | Flexible | Extra hop / control plane |

**Chosen MVP:** consistent hashing with virtual nodes; smart client or thin proxy.

**Deal-breaker:** mod-N at hundreds of nodes with frequent scale events (miss storms).

### 3.4 Replication & Multi-AZ

| Mode | Latency | Consistency | Use |
|------|---------|-------------|-----|
| Async RF | Low Set | Replica stale window | **Default cache** |
| Sync to quorum | Higher Set | Stronger read options | Session-critical |
| Chain replication | Ordered | Ops complexity | Optional |

**Placement invariant:** for each vnode, place replicas in **distinct AZs** when RF ≤ #AZs; never stack all RF on one AZ.

**Failover:** membership detects death → promote secondary → bump epoch → clients refresh → re-replicate to restore RF.

### 3.5 Consistency models

| Model | Guarantee | Cost |
|-------|-----------|------|
| Best-effort / eventual | Fast; stale OK | Cheapest |
| Primary reads | Read-your-writes if sticky | Primary load |
| Quorum R+W > RF | Stronger | Latency; still not DB |
| Linearizable | Hard | Usually wrong goal for cache |

**Chosen MVP:** write primary + async replicas; Get from primary by default; optional `Get(prefer_replica)` for read-heavy stale-OK keys; client L0 with short TTL for ultra-hot.

### 3.6 Eviction policies

| Policy | Pros | Cons | Fit |
|--------|------|------|-----|
| LRU | Simple | Weak scan resistance | OK baseline |
| LFU | Frequency | Aging needed | Hot keys |
| **TinyLFU + SLRU** | Excellent admission | More moving parts | **Strong default** |
| TTL-only | Simple | No pressure handling | Insufficient alone |
| Random | Tiny CPU | Worse hit rate | Emergency OOM |

**Chosen:** size-aware eviction with TinyLFU admission (or segmented LRU) + TTL. Per-tenant memory quotas for multi-tenant.

**TTL mechanics:** lazy expiry on access + periodic sampling / timing wheel; jitter on Set to desynchronize.

### 3.7 Hot-key mitigation

| Technique | How | Tradeoff |
|-----------|-----|----------|
| **Request coalescing** | Singleflight miss/Get | Helps misses more than hits |
| **Client L0 cache** | Process-local TTL cache | Stale; huge win for ultra-hot |
| **Replicate hot key to N nodes** | Read any copy | Coordination; memory |
| **Key splitting** | App shards logical key | Needs app cooperation |
| **Hedged reads** | Rare | Amplification risk |

### 3.8 Cache stampede controls

| Technique | Mechanism | When |
|-----------|-----------|------|
| **Singleflight** | One fill per key in-flight | Miss herds |
| **TTL jitter** | `ttl' = ttl × U(0.9, 1.1)` | Aligned expiry |
| **Probabilistic early refresh** | xfetch-style | Hot keys near expiry |
| **Negative caching** | Short TTL empty | Missing keys hammering DB |
| **Fill admission** | Max concurrent DB fills / node | Protect SoT |
| **Soft request hedging** | Careful | Only with coalescing awareness |

### 3.9 Membership

| System | Pros | Cons | Use |
|--------|------|------|-----|
| **Gossip (SWIM)** | Scalable; no external dep | Convergence time | Large clusters tip |
| **ZK / etcd** | Strong membership view | External; watch storms | **MVP medium size** |
| Static config | Simple | Elasticity pain | Tiny |
| Managed control plane | Amazon operational fit | Less “build it” | ElastiCache-like |

**Chosen MVP:** etcd/ZK (or service-owned control plane) for cluster membership + shard map **epoch**; gossip optional at 100× for failure detection tip. Primaries hold **leases** to prevent split-brain.

### 3.10 Client vs proxy

| Mode | Pros | Cons | When |
|------|------|------|------|
| Smart client | Lowest hop | Polyglot cost | Homogeneous fleets |
| Proxy | Connection mux; polyglot | Extra hop / capacity | **10× often** |
| Hybrid | L0 in app + proxy | Complexity | 100× Zipf |

### 3.11 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| SoT | DB / backing | Cache ephemeral | Cache-only durable money |
| Partition | CH + vnodes | Elasticity | Mod-N remaps |
| RF | 3 async Multi-AZ | HA without sync tax | RF=1 for critical sessions |
| Eviction | TinyLFU/SLRU + TTL | Hit rate under scan | Unbounded memory |
| Hot keys | L0 + replicate | Skew reality | “Hash will save us” |
| Stampede | Singleflight + jitter | Protect DB | Aligned TTL only |
| Writes | Cache-aside | Clear durability | Silent write-back |
| Membership | etcd map + epoch | Deterministic fencing | Gossip-only without epoch |
| AZ | Distinct replica AZs | Survive AZ loss | All replicas one AZ |

---

## 4. Architecture Diagram

### 4.1 System context

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
     |  Proxy (opt)   |  optional at 10× for polyglot / mux
     +-------+--------+
             |
    +--------+---------+--------+
    v        v         v        v
  Node A   Node B    Node C   Node D   ...   (spread across AZ-a/b/c)
  (vnode primaries + replicas)
    |        |
    +---+----+
        v
   Replication (async, cross-AZ)
        |
        v
  +-----------+     +------------------+
  | etcd / ZK |     | Metrics/Hotkey   |
  | membership|     | detector service |
  +-----------+     +------------------+

  Miss path: Client -> Cache miss -> DB/backing -> Set -> return
```

### 4.2 Get hit path

```text
Client.hash(key) -> primary node (prefer in-AZ) -> DRAM -> value
```

### 4.3 Get miss + coalesce (stampede)

```text
N waiters -> leader loads DB (singleflight) -> Set(primary) -> replicate -> release waiters
If fill_inflight > limit: shed / wait / return miss to caller with backoff
```

### 4.4 Hot key path

```text
Detector flags key -> controller: replicate to N nodes / instruct clients L0 TTL
Subsequent Gets: L0 or any hot replica; Writes: still primary (+ invalidate L0 via short TTL)
```

### 4.5 Membership / AZ failure

```text
t0 AZ-a nodes fail health / leases expire
t1 etcd epoch++ ; new shard map
t2 promote replicas in AZ-b/c for affected vnodes
t3 clients/proxies observe map; traffic shifts
t4 re-replicate to restore RF across remaining AZs (rate-limited)
t5 miss ratio blip then recover; DB absorbs temporary miss spike (admission!)
```

### 4.6 Rebalance handoff

```text
for vnode in moving:
  pause writes OR dual-write
  copy keys old → new (rate-limited MB/s)
  flip map epoch for vnode
  catch-up tail
  decommission old
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **DB/backing remains SoT** for cache-aside MVP.  
2. **Single-key operations atomic** on primary.  
3. **Shard map epoch fencing** — ignore requests with stale epoch; `NOT_PRIMARY` redirect.  
4. **Never return corrupt values** — optional CRC on value frames.  
5. **Replication deletes** propagate (or TTL heals).  
6. **Memory hard limit** — evict or reject; never OOM-kill as strategy.  
7. **Replica AZ diversity** — RF placement spans AZs.  
8. **Primary lease** — minority partition cannot extend lease.  
9. **Fill admission** — protect SoT under miss storms.

#### 5.1.2 Data loss prevention

| Path | Risk | Mitigation |
|------|------|------------|
| Cache-aside Set loss | Stale miss | DB still correct |
| Write-through fail | Partial | Commit DB then cache; or outbox |
| Write-back | Node/AZ death loses dirty | WAL to disk + RF; bounded RPO |
| Replica-only read | Stale | Primary reads / version checks |

#### 5.1.3 Retries & idempotency

- Client retries Get freely (read-only).  
- Set with CAS for concurrency.  
- Idempotency-Key for write-through to DB.  
- Hedged Get only with server coalescing awareness.  
- On `NOT_PRIMARY`, refresh map and retry once.

#### 5.1.4 Rate limits & admission

- Per-tenant QPS and memory quotas (noisy neighbor).  
- Reject Sets when eviction can’t keep up (`OOM` / `BUSY`).  
- Miss admission: limit concurrent fills per node/cluster.  
- Replication backpressure: slow Sets or shed replicas temporarily with alert.

#### 5.1.5 Thundering herd / stampede

| Scenario | Mitigation |
|----------|------------|
| Cold start miss storm | Singleflight; probabilistic early refresh; warmup |
| TTL aligned expiry | Jitter TTL |
| Hard fail node / AZ | Paced promotion; fill admission; optional critical-key warmup |
| Rebalance | Rate-limited key move; dual-read during handoff |
| Celebrity key expiry | Early refresh + L0 |

#### 5.1.6 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Hot key | L0 + detect |
| 10× | Rebalance miss storm | Vnode handoff protocol |
| 100× | etcd watch overload | Sharded maps / gossip hybrid |
| 1,000× | Global ring myth | Cells; no single membership domain |
| Any | AZ loss | Cross-AZ RF + paced RF restore |

### 5.2 Scalability

#### 5.2.1 Traffic ups/downs

- Horizontal add nodes; vnode migration.  
- Autoscale carefully—cold nodes cause miss storms; pre-warm critical keys.  
- Read scale via replicas / L0; write scale via more partitions.  
- Cells by tenant or keyspace at 100×+.

#### 5.2.2 Storage / memory

| Scale | Strategy |
|-------|----------|
| Baseline | Pure DRAM |
| 10× | Tighter slabs; compression for cold-ish keys |
| 100× | SSD second tier (L2) for large/cold |
| 1,000× | Tiered + cell-local working sets; no global monolith |

#### 5.2.3 Efficiency levers (Amazon signal)

- Right-size RF vs hit-rate value.  
- Avoid storing megavalues that destroy packing.  
- Client L0 reduces cross-AZ Get traffic for Zipf.  
- Pipeline / GetMulti grouping.  
- Eviction quality beats “buy more RAM” as first answer—but measure hit-rate curves.

### 5.3 Maintainability / operability

#### 5.3.1 Control plane operations

- Drain node / AZ for maintenance.  
- Controlled rescale with rate limits.  
- Hot-key controller with kill-switch (stop replicating).  
- Tenant quota changes versioned.  
- Chaos: kill primary, kill AZ, partition etcd — game days.

#### 5.3.2 Observability

| Signal | Why |
|--------|-----|
| `hit_ratio` | Capacity / eviction health |
| `get_p99` / per-node | Hot shard detection |
| `evict_rate` | Memory pressure |
| `replica_lag` | NIC/CPU / AZ issues |
| `fill_inflight` | Stampede / DB slow |
| `oom_reject` | Admission failing |
| `epoch` / map freshness | Membership health |
| `hot_key_score` top-K | Skew ops |

#### 5.3.3 Ownership narrative

- On-call owns Multi-AZ failover runbooks and DB protection (fill admission).  
- SLO: Get p99, hit ratio, error rate, failover RTO, miss-storm boundedness.  
- Customer-facing: clear max item size, TTL semantics, eviction under quota.

### 5.4 Consistency deep dive

| Pattern | Coherence tip |
|---------|---------------|
| Cache-aside | Del-on-write; versions; CDC invalidation |
| Write-through | DB success required before/with cache Set |
| Write-back | WAL + fsync policy + replay; Multi-AZ dirty replication |
| L0 client | Short TTL; optional version check against primary |

**Read-your-writes:** sticky routing to primary or client remembers `version` after Set.

### 5.5 Security & multi-tenant

- AUTH + TLS; per-tenant ACL prefixes / namespaces.  
- Memory and QPS quotas; noisy-neighbor isolation.  
- Dangerous `FLUSH` admin-only with audit.  
- No cross-tenant key access.  
- Encryption at rest if persistence enabled.

### 5.6 Multi-AZ / multi-region

| Scope | Approach |
|-------|----------|
| Multi-AZ | RF across AZs; primary preference in-AZ; cross-AZ async repl |
| Multi-region | **Cells per region**; no single global ring; optional async warm of select keys |
| Active-active global | Usually wrong for general cache without conflict story |

**Cost note:** cross-AZ bytes are not free—keep Get primary in-AZ; accept repl cost for HA.

---

## 6. Wrap-Up

### 6.1 Amazon narrative (60–90s)

> “I’d clarify that the DB remains source of truth, pick cache-aside as default, and lock Multi-AZ RF and consistency expectations. Memory math is working set × RF / utilization—replication is an explicit cost. I’d partition with consistent hashing and vnodes, async RF=3 across AZs, primary reads by default, TinyLFU/SLRU eviction under a hard memory budget, and a stampede playbook—singleflight, TTL jitter, fill admission. Hot keys get client L0 plus dynamic replication because hashing won’t save us from Zipf. Membership uses an epoch-fenced shard map with primary leases so we don’t split-brain on AZ failure. At 100× we cell the ring and add SSD tiers; we never pretend a global linearizable cache at a billion QPS.”

### 6.2 Decision summary

| Area | Decision |
|------|----------|
| SoT | Backing DB |
| Write policy | Cache-aside MVP |
| Partition | Consistent hash + vnodes |
| RF | 3 async, Multi-AZ placement |
| Reads | Primary default; replica/L0 optional |
| Eviction | TinyLFU/SLRU + TTL + quotas |
| Stampede | Singleflight + jitter + fill admission |
| Hot keys | L0 + replicate + detect |
| Membership | etcd/ZK map + epoch + leases |
| Scale path | Proxies → cells → federated |

### 6.3 What interviewers listen for

- Memory × RF arithmetic.  
- Hot keys ≠ partitioning problem alone.  
- Stampede / DB protection.  
- Multi-AZ placement + fencing.  
- Write-back honesty (WAL/RPO).  
- Progressive scale to cells.

---

## 7. Deeper / Related Interview Questions

### 7.1 Partitioning & consistent hashing

**Q1: Why virtual nodes?**  
A: Better load balance; smoother moves; isolate noisy physical nodes.

**Q2: How many vnodes?**  
A: Tens–hundreds per node; trade ring memory vs balance.

**Q3: Difference vs mod-N?**  
A: Mod-N remaps most keys on scale; CH remaps ~1/N.

**Q4: Where is the ring stored?**  
A: In clients and/or proxies; updated on membership epoch.

**Q5: Ketama vs rendezvous hashing?**  
A: Both fine; rendezvous easy for “top N replicas.”

**Q6: How do you place replicas across AZs?**  
A: Walk ring for distinct physical nodes constrained to different AZs.

**Q7: What if #AZs < RF?**  
A: Best-effort diversity; acknowledge correlated risk; consider RF=#AZs.

### 7.2 Replication & CAP

**Q8: Why async replication for cache?**  
A: Set latency; stale OK if DB SoT.

**Q9: When sync quorum?**  
A: Session tokens where stale read breaks auth UX.

**Q10: CAP choice?**  
A: Usually AP + regenerate from DB; not CP money store.

**Q11: Read repair?**  
A: Optional; often TTL/expiry simpler for cache.

**Q12: Replica lag spike cross-AZ?**  
A: NIC/CPU; throttle Sets; alert; temporary primary-only reads.

**Q13: Does RF improve hit rate?**  
A: No for capacity of unique keys—replicas duplicate bytes; RF is HA.

### 7.3 Eviction & memory

**Q14: LRU vs LFU?**  
A: LRU fails on scans; LFU needs aging; TinyLFU admits winners.

**Q15: How to size memory?**  
A: Working set × RF / utilization + headroom; measure hit-rate curve.

**Q16: Slab allocators?**  
A: Reduce fragmentation (memcached-style); internal fragmentation tradeoff.

**Q17: TTL vs LRU interaction?**  
A: Lazy expiry on access + periodic sampling; LRU among live keys.

**Q18: What if Set when full?**  
A: Evict victims until fit or reject; never unbounded growth.

**Q19: Per-tenant eviction?**  
A: Quotas so one tenant can’t evict everyone’s working set.

### 7.4 Hot keys

**Q20: Why doesn’t hashing fix hot keys?**  
A: Popularity is Zipfian on keys, not uniform on hash space.

**Q21: Client L0 risks?**  
A: Staleness; bound with short TTL + invalidation hooks.

**Q22: Dynamic replication protocol?**  
A: Controller updates “hot map”; clients fan-out reads; primary still owns writes.

**Q23: Count-Min Sketch?**  
A: Approximate frequency with tiny memory—good detector.

**Q24: Can you split a hot key?**  
A: Only if app semantics allow (e.g., counters → sharded counters + sum).

**Q25: Hot key after AZ failover?**  
A: Promoted primary may melt—pre-enable L0 / extra replicas for known celebrities.

### 7.5 Consistency & write policies

**Q26: Cache-aside invalidation bug?**  
A: Race: update DB, then stale Set from concurrent reader—use version/CAS or delete-on-write (+ CDC).

**Q27: Write-through vs aside?**  
A: Through keeps warm; aside simpler and common.

**Q28: Write-back when?**  
A: Burst absorption with WAL; rare for general cache interviews unless asked.

**Q29: Read-your-writes?**  
A: Sticky to primary or client session remember version.

**Q30: CAS usage?**  
A: Lost-update prevention on concurrent Set.

**Q31: CDC invalidation?**  
A: Strong pattern: DB change stream → Del keys.

### 7.6 Membership & Multi-AZ

**Q32: Gossip vs ZK/etcd?**  
A: Gossip scales detection; etcd gives linearizable config—hybrid common.

**Q33: What is an epoch?**  
A: Monotonic membership generation; fence old primaries.

**Q34: Split-brain primary?**  
A: Lease in etcd; minority can’t extend lease.

**Q35: Watch storms at 2K nodes?**  
A: Hierarchical maps; push shard deltas; avoid full-map payload every time.

**Q36: Graceful drain?**  
A: Remove from ring gradually; keep serving until handoff complete.

**Q37: AZ failure vs node failure?**  
A: AZ fails many nodes correlated—pace promotions; protect DB with fill admission; expect larger miss blip.

**Q38: Cross-region cache?**  
A: Separate cells; don’t stretch one RF ring across oceans for MVP.

### 7.7 Thundering herd & stampedes

**Q39: Singleflight scope?**  
A: Per-process first; cluster-wide needs lease/coordinator.

**Q40: Probabilistic early expire?**  
A: Desynchronize TTL refresh under load (`xfetch`).

**Q41: Negative caching?**  
A: Cache misses briefly; prevent DB hammer on absent keys.

**Q42: Cache warming?**  
A: Preload critical keys before event; rate-limit.

**Q43: Stampede on deploy?**  
A: Rolling warm; don’t bounce all clients’ L0 simultaneously.

### 7.8 Load balancing & clients

**Q44: Smart client vs proxy?**  
A: Smart=lower hop; proxy=polyglot + connection concentration.

**Q45: Connection explosion?**  
A: Proxies or mux; at 10× often needed.

**Q46: Longest connection / slow client?**  
A: Timeouts; backpressure; bounded queues.

**Q47: Multi-get partial failure?**  
A: Return partial + errors; client may fall back DB per key.

**Q48: In-AZ preference?**  
A: Route Get to primary if in-AZ; else nearest; measure cross-AZ tax.

### 7.9 Algorithms & indexing

**Q49: Hash function?**  
A: xxHash/Murmur; cryptographic hash unnecessary.

**Q50: Expiry data structure?**  
A: Timing wheel / hierarchical wheel for large key counts.

**Q51: Scan-resistant eviction?**  
A: Probationary segment; TinyLFU admission.

**Q52: Compression?**  
A: CPU vs memory; value-size dependent.

### 7.10 DB & storage interplay

**Q53: What DB behind cache?**  
A: Whatever SoT is—DynamoDB/Aurora/SQL/KV; cache shouldn’t require a specific DB.

**Q54: Should cache persist?**  
A: Optional; persistence ≠ make it primary without consensus story.

**Q55: ElastiCache vs DAX vs app cache?**  
A: ElastiCache-class general KV; DAX DynamoDB-specific; app L0 always complementary for Zipf.

**Q56: Is Redis Cluster “the design”?**  
A: Implementation analog—still need eviction policy, hot keys, stampede, Multi-AZ fencing story.

### 7.11 Interview craft & Amazon themes

**Q57: How to open?**  
A: Clarify SoT, write policy, consistency, value sizes, QPS, working set, skew, Multi-AZ.

**Q58: Numbers that matter?**  
A: Working set × RF, QPS × value size, hot-key QPS, miss% × DB capacity, cross-AZ repl bytes.

**Q59: Common trap?**  
A: Redis-cluster trivia without hot keys, eviction, stampede, or membership fencing.

**Q60: L6/SDE III signal?**  
A: Progressive scale to cells; explicit deal-breakers; memory math; owned AZ failover + DB protection.

**Q61: Frugality?**  
A: RF tax acknowledged; L0 reduces network; right-size values; don’t over-replicate cold keys.

**Q62: Ownership?**  
A: Runbooks for AZ loss, rebalance, hot-key controller; SLOs on miss storms.

**Q63: Related designs?**  
A: CDN edge cache, session store, device shadow cache—same fundamentals, different skew/TTL.

**Q64: When is cache the wrong tool?**  
A: Strong multi-key transactions; huge working set with low reuse; write-heavy without WT/WB plan.

### 7.12 Extra interviewer traps (high value)

- Does RF=3 triple your hit rate? (No—triples memory for HA.)  
- Walk the cache-aside race after DB update.  
- What happens to DB when an AZ of cache dies?  
- Why jitter TTLs?  
- Write-back without WAL — why deal-breaker?  
- How do you fence a primary in a minority partition?  
- Hot key at 2M QPS — concrete mitigation ladder.  
- Mod-N vs CH during Black Friday scale-out.  
- How do tenant quotas interact with global eviction?  
- GetMulti fanout and partial failure semantics.  
- Should cross-region be one ring?  
- How do you rate-limit rebalance?  
- Negative caching vs “always hit DB for 404.”  
- CAS vs Del-on-write.  
- What metric proves you need more DRAM vs better eviction?  
- Proxy connection mux math.  
- SSD tier when and why latency changes.  
- How do you test failover without torching prod?  
- Encryption/TLS CPU impact on p99.  
- Why “hashing fixes skew” is a failing answer.

---

## Appendices

### Appendix A — Consistent hashing sketch

```text
for node in nodes:
  for i in 0..V-1:
    ring[hash(node.id + ":" + i)] = node
primary(key) = first node clockwise from hash(key)
replicas = next distinct nodes clockwise with AZ diversity constraints
```

### Appendix B — Cache-aside pseudocode

```text
Get(k):
  if v = L0.get(k): return v
  v = cache.Get(k)
  if v: L0.set(k,v, short_ttl); return v
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
  wal.append(k,v)       # fsync policy explicit
  cache.SetDirty(k,v)
  ack client
  async flush db (+ Multi-AZ dirty repl if required by RPO)
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
Per-tenant quota_bytes ⊆ cluster; enforce on Set
```

### Appendix F — Progressive scale table

| Scale | Topology | Hot keys | Stampede | Membership |
|-------|----------|----------|----------|------------|
| Baseline | 1 ring, 3 AZ | Manual L0 | Singleflight | etcd + leases |
| 10× | Proxies | Detector + replicate | + fill admission | etcd + rate-limited rebalance |
| 100× | Cells | L0 default | Cell-local | Per-cell etcd |
| 1,000× | Many cells | App cooperation | Federated | No global ring |

### Appendix G — NFR card

```text
Get p99 < 5ms in-AZ
RF=3 async Multi-AZ default
Hard memory limit + eviction
Singleflight misses + TTL jitter
Hot-key playbook mandatory
Epoch-fenced membership + primary leases
Fill admission protects DB
Cache ≠ SoT
```

### Appendix H — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just Redis Cluster” | Still need policies: eviction, hot keys, stampede, Multi-AZ fencing |
| “RF=1 is fine” | Node/AZ death ⇒ cold miss storm |
| “Strong consistency everywhere” | Wrong default for cache |
| “Hashing fixes skew” | Zipf keys disagree |
| “Write-back is faster, so default” | Durability/RPO must be explicit |

### Appendix I — Eviction comparison

| Property | LRU | LFU | TinyLFU+SLRU |
|----------|-----|-----|--------------|
| Scan resistance | Weak | Stronger | Strong |
| Complexity | Low | Med | Med |
| Practice | Ubiquitous | Common | Caffeine-like |

### Appendix J — Membership event timeline

```text
t0 node B fails health checks
t1 etcd session/lease expires; epoch=42→43
t2 clients/proxies observe new map
t3 promote replicas of B’s vnodes (AZ-aware)
t4 re-replicate to restore RF (rate-limited)
t5 miss ratio blip then recover; fill admission holds DB
```

### Appendix K — Multi-get planning

```text
GetMulti(keys):
  group by primary
  parallel RPC per primary (bounded)
  merge; for misses optional parallel DB (coalesced per key)
  return partial results + per-key errors
```

### Appendix L — Deal-breaker catalog

| Choice | Deal-breaker when |
|--------|-------------------|
| Write-back w/o WAL | Money/order writes |
| Mod-N hashing | Frequent resizing |
| No hot-key plan | Celebrity key traffic |
| Unbounded memory | Kernel OOM as policy |
| Cache as SoT | Durability requirements |
| All replicas one AZ | “Multi-AZ” marketing only |
| No fill admission | AZ failover melts DB |

### Appendix M — Related systems

| System | Relation |
|--------|----------|
| ElastiCache | Managed analog |
| DAX | DynamoDB-specific accelerator |
| CDN | Geo edge cousin |
| File cache | Large-object cousin |
| Redis/Memcached | Implementation analogs |
| DB buffer pool | Single-node cousin |

### Appendix N — Non-goals

- Cross-key serializability  
- Global linearizability at 1B QPS  
- Replacing the database  
- Perfect zero-stale under all partitions  
- One global ring across all regions  

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
prefer off-peak; never move entire AZ at once without pacing
```

### Appendix Q — Observability red flags

| Signal | Meaning |
|--------|---------|
| hit_ratio ↓ + evict ↑ | Undersized memory / bad eviction |
| p99 ↑ one node | Hot shard / hot key |
| replica_lag ↑ | NIC/CPU / AZ saturation |
| fill_inflight ↑ | Miss storm / DB slow |
| oom_reject ↑ | Admission failing |
| epoch flapping | Control plane instability |

### Appendix R — Security / multi-tenant

- AUTH + TLS; per-tenant ACL prefixes.  
- Memory/QPS quotas.  
- Dangerous `FLUSH` admin-only.  
- No cross-tenant key access.  
- Audit admin ops.

### Appendix S — 30s scale narrative

> Baseline: CH+vnodes, RF=3 Multi-AZ, cache-aside, TinyLFU, singleflight+jitter, etcd epochs+leases. 10× adds proxies, hot-key replication, stricter fill admission. 100× cells the cluster and adds SSD tiers + default L0. 1,000× is many cells—no single global ring—with L0 everywhere for Zipf traffic.

### Appendix T — Glossary

| Term | Meaning |
|------|---------|
| Vnode | Virtual node on hash ring |
| RF | Replication factor |
| Singleflight | Coalesce in-flight work |
| TinyLFU | Admission filter via approximate frequency |
| Epoch | Membership generation for fencing |
| Cache-aside | App reads DB on miss; cache filled by app |
| Write-through | Write DB and cache together |
| Write-back | Cache acknowledges early; flushes later |
| Stampede | Miss herd amplifying DB load |
| L0 | Process-local cache tier |

### Appendix U — Interview whiteboard order

1. Requirements: SoT, write policy, consistency, sizes, Multi-AZ  
2. API + memory math (WS × RF)  
3. Consistent hashing + RF/AZ placement  
4. Get/Set paths + singleflight  
5. Eviction + TTL jitter  
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
| `FILL_THROTTLED` | Miss admission shedding |

### Appendix W — Consistency cheatsheet

| Read mode | Stale window | Load |
|-----------|--------------|------|
| Primary | ~repl lag 0 for writes seen | Hot primary |
| Replica | Async lag | Scaled reads |
| Quorum | Low | Higher latency |
| L0 client | TTL bound | Best for ultra-hot |

### Appendix X — Stampede worksheet

```text
Popular key TTL=60s, 50K QPS, no jitter
→ every 60s potentially 50K aligned refreshes
With singleflight: 1 fill / process; still storm across 5K hosts → need cluster coalesce or early refresh
With jitter ±10%: expiry spread over ~12s → peak refresh ~50K/12 ≈ 4K/s (order-of-magnitude)
Fill admission caps DB QPS regardless
```

### Appendix Y — Multi-AZ placement example

```text
AZs: a, b, c; RF=3
vnode V primary on node in AZ-a
replicas: one in AZ-b, one in AZ-c
AZ-a down → promote AZ-b (or AZ-c) via epoch; recreate third replica when capacity allows
```

### Appendix Z — Why Amazon flavor ≠ ElastiCache trivia

Interviewers score **clarifying questions, correct tradeoffs, memory math, Multi-AZ ownership, and progressive scale**. Naming product features without explaining vnodes, RF memory multiply, stampede admission, and hot keys is weaker than a crisp generic design with numbers and deal-breakers.

---

*End of Distributed Cache system design. Open with §1 SoT + write policy + Multi-AZ; whiteboard §2.2 memory math + §3 partitioning/replication; close with stampede/hot-key playbooks and §7 traps.*
