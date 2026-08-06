# System Design: Distributed Key-Value Database (Meta)

> **Focus areas:** Partitioning · Replication · Consistency · Compaction · Hot keys · Multi-tenant serving · Progressive scale  
> **Style:** End-to-end infrastructure design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split read/write/compaction/admin planes, explicit CAP/consistency deal-breakers  
> **Interview theme:** Classic Meta infra L5+ — design a KV store in the spirit of TAO/ZippyDB/RocksDB-on-fleet (without claiming any one internal name as exact)

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

Goal: **bound the product**—a **distributed key-value database** for large online social/infra workloads: low-latency `Get`/`Put`/`Delete`, optional TTL, range scans limited or out of MVP, tunable consistency, and operability at Meta scale.

### 1.0 What this is / is not

| Dimension | **Distributed KV DB (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Durable low-latency KV serving | Full SQL relational engine |
| Success | p99 Get low-ms; durable Puts; high availability | Arbitrary secondary indexes / joins |
| Data plane | Replicated partitions (shards/ranges) | Data warehouse analytics |
| Query | Point get/put/delete; limited prefix/range | Ad-hoc OLAP SQL |
| Correctness | Tunable; define quorum/leader model explicitly | Magic “CA always” on async network |

**Scope statement:** Design a distributed key-value store: sharding, replication, storage engine, consistency, failure handling, hot keys, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | `Get`, `Put`, `Delete`, optional `CAS` / `TTL` | Simple client API + version |
| F2 | Value size? | Typically < few KB–MB; large values via pointer | Size limits; blob offload |
| F3 | Range scan? | Prefix scan Phase 1.5 or limited | Ordered keys (LSM/ranges) vs hash-only |
| F4 | Consistency? | Leader quorum strong for primary; eventual replicas OK | Consensus / Raft per shard |
| F5 | TTL? | Yes — sessions, caches, ephemeral | Tombstones + compaction |
| F6 | Transactions? | Single-key atomic MVP; multi-key Phase 2 | Keep MVP honest |
| F7 | Multi-tenant? | Namespaces / tables | Quota isolation |
| F8 | Secondary index? | Out of MVP | App-maintained |
| F9 | Backup / restore? | Yes — PITR-ish or snapshots | Backup plane |
| F10 | Change feed? | CDC optional Phase 1.5 | WAL tail |
| F11 | Cross-region? | Async replica + regional primary | RPO/RTO explicit |
| F12 | Client features? | Hedged reads; retries; locality | Smart client / proxy |

**MVP functional scope:**

1. `Put(key, value, ttl?)`, `Get(key)`, `Delete(key)`, optional `CompareAndSet`.  
2. Keys namespaced; values opaque bytes with size limit (e.g. 1 MB).  
3. Cluster sharded into partitions with **leader + followers**.  
4. Strong consistency on linearizable path via leader quorum; read-your-write options.  
5. Durability: WAL + replicated log before ACK (sync replica count configurable).  
6. Membership / rebalancing; failure detection; leader election per shard.  
7. TTL expiry best-effort via compaction.  
8. Metrics, admin APIs, backups.

**Out of MVP:**

- Full SQL / joins / multi-row ACID across shards  
- Global secondary indexes  
- Perfect cross-region synchronous commit for all writes (latency deal-breaker)  
- Unlimited value sizes  
- Active-active multi-writer same key across regions without conflict story

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Get latency | Online path | p50 < 1–3ms regional; p99 < 10–20ms |
| N2 | Put latency | Durable | p50 < 3–5ms; p99 < 20–40ms (same region) |
| N3 | Durability | No ack loss | Replicated WAL fsync policy explicit |
| N4 | Availability | Zone failure OK | 99.99% with 3 AZ |
| N5 | Consistency | Tunable | Default leader strong; stale read replica optional |
| N6 | Throughput | Massive | Millions ops/s cluster-wide |
| N7 | Operability | Rebalance without long downtime | Online shard move |
| N8 | Multi-tenant fairness | Noisy neighbor control | Quotas / isolation |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client `Put` → proxy routes to shard leader → WAL replicate quorum → ACK → memtable.  
2. Client `Get` → leader (strong) or follower (eventual) → return value/version.  
3. Node dies → lease expires → new leader → continue.  
4. TTL key expires → invisible on Get; space reclaimed on compaction.  
5. Admin splits hot range → two shards → rebalance peers.  
6. Cross-region async replica lags; failover with RPO > 0 acknowledged.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Hot key | Cache; striping; client backoff; split if range | 
| Network partition | Raft majority wins; minority unavailable |
| Slow follower | Remove from quorum / catch-up snapshot |
| Giant value | Reject or blob pointer |
| Clock skew | Logical term/index; no NTP trust for safety |
| Split brain | Quorum + fencing tokens |
| Compaction storm | Throttle; prioritized WALs |
| Rebalance mid-write | Dual-route / blocking handoff carefully |
| CAS conflict | Return failure; client retry |
| Disk full | Shed writes; alert; reject Puts |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Cluster usable data | 1 PB | 10 PB | 100 PB | Exabyte class |
| Shards / ranges | 1K | 10K | 100K | 1M+ |
| Nodes | 100 | 1K | 10K | 100K cells |
| Peak Get QPS | 5M | 50M | 500M | multi-cell |
| Peak Put QPS | 1M | 10M | 100M | multi-cell |
| Avg value size | 1 KB | 1 KB | 1–2 KB | mixed |
| Replication factor | 3 | 3 | 3–5 | 3 + regional |
| Regions | 1–2 | 2–3 | many | cell fabric |
| p99 Get (regional) | <15ms | <15ms | cells local | edge+cells |

**What each jump forces:**

- **10×:** Automatic split/merge; compaction IO budgets; proxy routing layers.  
- **100×:** Regional cells; hierarchy of control plane; hot-key service; tenant isolation.  
- **1,000×:** Many independent KV cells; global directory; no single cluster brain.

### 1.5 Etc. (Constraints & Assumptions)

- Commodity servers with NVMe + DRAM; LSM-style local engine OK.  
- Datacenter network: RDMA optional; don’t require it for MVP design.  
- Clients may be within Meta compute fleet (low RTT) or via proxies.  
- We design **general KV**, not the entire social graph product (graph can sit above).

**Scope statement to repeat back:**

> Design a distributed key-value database with sharded replicated partitions, leader-based strong writes, LSM storage, TTL, online rebalance, hot-key defenses, and progressive scale to multi-cell deployments—without pretending to be a distributed SQL database.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Point Get** | Read path | 5M/s | Leader/follower + cache |
| **Point Put/Delete** | Write path | 1M/s | WAL + replicate |
| **Compaction** | Background IO | bursty | Storage engine |
| **Rebalance / snapshot** | Ops | episodic | Admin |
| **Backup** | Snapshots/WAL ship | continuous | Backup |
| **Control plane** | Membership | low QPS | Critical correctness |

### 2.2 Capacity math

```text
1 PB data × RF=3 → 3 PB raw (plus overhead ~1.3–2× with LSM) → plan ~4–6 PB disk
Avg 1 KB value → ~1e12 keys order (upper) — often fewer larger values

DRAM cache: if 5% working set hot: 0.05 × 1 PB = 50 TB DRAM cluster-wide
  → caching tier / memcache aside often used in front of KV at Meta
```

### 2.3 Shard sizing

```text
Target shard data: 10–50 GB (so rebuild/move minutes–hours not days)
1 PB / 20 GB = 50K shards — heavy; often larger shards 100–200 GB with care
Baseline 1K–10K shards more operable; split as growth

Write QPS per shard: 1M puts / 1K shards = 1K puts/s/shard — OK
Hot key can concentrate >> that → special handling
```

### 2.4 WAL disk bandwidth

```text
1M puts/s × (1KB value + 100B overhead) ≈ 1.1 GB/s cluster ingest
With RF=3 cross-node: ~3.3 GB/s network+disk before batching
Batching + parallel shards makes this feasible on 100-node cluster
```

### 2.5 Latency budget (same AZ)

```text
Proxy route           0.1–0.3ms
Leader in-mem         0.05ms
WAL group commit      0.5–2ms
Replicate RT          0.3–1ms (same DC)
Total Put p50         few ms
Get DRAM hit          <1ms
Get SSD               1–5ms
```

### 2.6 Cross-region sync tax

```text
USW ↔ USE RTT ~60–70ms
Sync RF across coasts → Put p50 > 70ms — often unacceptable for social online path
Hence: regional primary + async DR (RPO minutes) OR sync only within region
```

**Deal-breaker:** promising sync triple-replicate across continents at single-digit ms Put latency.

### 2.7 Consistent hashing / directory arithmetic

```text
Virtual nodes: 100–200 vnodes / physical node → smoother balance
1K nodes × 128 vnodes = 128K ring points
Directory size: shard_id → {peers, epoch, key_range} small enough to cache on clients
At 50K shards: directory ~ tens of MB — push versioned snapshots; watch diffs
Reshard move: 20 GB shard at 200 MB/s ≈ 100s + catch catch-up — schedule throttled
```

### 2.8 Quorum latency math

```text
RF=3, W=2, R=1 (Dynamo-style) or Raft majority (=2 of 3)
Same-AZ RTT 0.2–0.5ms; majority Put ≈ WAL + 1 peer ACK
Cross-AZ in region +1–2ms
p99 dominated by slow disk fsync / noisy neighbor — isolate WAL devices
```

### 2.9 Compaction write amp

```text
LSM write amp often 10–30× depending levels / compaction style
1M puts/s × 1KB × 15 amp ≈ 15 GB/s cluster disk write — capacity plan!
Throttle compaction vs foreground; debt metric alerts before latency cliff
```

### 2.10 Tombstone storage tax

```text
Delete-heavy workloads: tombstones retained until compaction proves no older reader needs them
If TTL storm: same issue
Budget: tombstone bytes and count per shard; force compact when exceeded
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `Put(ns, key, value, ttl?, expect_ver?)` | Upsert; optional CAS |
| `Get(ns, key, consistency?)` | Value + version / not_found |
| `Delete(ns, key, expect_ver?)` | Tombstone |
| `GetPrefix(ns, prefix, limit)` | Optional ordered scan |
| `Admin: split/merge/move/snapshot` | Control plane |

**Key design:**

```text
FullKey = hash(ns) | ns | user_key   # or ordered ns encoding
Version = (term, index) or monotonic epoch-seq per shard
```

### 3.2 Cluster architecture

```text
Smart Client / Proxy
  -> Shard Directory (key -> shard -> leader)
  -> Shard Leader
       -> WAL replicate to followers (Raft/Paxos)
       -> Storage Engine (RocksDB/LSM)
```

### 3.3 Partitioning — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Hash shards** | Even load | Weak range scan | Point-heavy MVP |
| **Range shards** | Prefix/scan; locality | Hot ranges | Ordered keys needed |
| Consistent hashing ring | Simple mental model | Rebalance quirks | OK with virtual nodes |
| Directory-based map | Explicit moves | Directory dependency | **Meta-style operable** |

**Chosen:** **Range-partitioned shards** with a **shard map** (directory), hash-prefix optional for tenant mixing:

- Supports future prefix scans.  
- Hot ranges can split.  
- Directory caches on clients with epoch fencing.

**Deal-breaker:** static modulo hashing with no rebalance story at 10× growth.

**Expanded partitioning narratives:**

1. **Hash-only without directory:** cannot split a hot key range or move one tenant cleanly; rebalance becomes “rebuild ring and pray.”  
2. **One giant Raft group for all keys:** throughput ceiling = one leader’s disk; Meta-scale needs **many independent shards**.  
3. **Range without split tooling:** celebrity key prefixes (`user:celeb:…`) melt a single shard — splits are mandatory ops.

### 3.4 Replication & consensus — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Raft per shard** | Understandable leadership | Many groups overhead | **Strong MVP** |
| Multi-Paxos | Proven | Complexity | Fine alternative |
| Leaderless quorum (Dynamo) | High write avail | Conflicts; read repair | If AP preferred |
| Primary-backup custom | Simple | Subtle failovers | Risky unless careful |
| Async only | Fast | Data loss | Cache not DB |

**Chosen:** **Raft (or equiv) per shard**, RF=3 across AZs:

- Put ACK after majority durable log.  
- Get default from leader (linearizable option).  
- Optional follower reads with `max_staleness`.

**Deal-breaker:** “eventual consistency is fine” without telling clients when they see stale social ACL/counters.

### 3.5 Storage engine — Why X over Y

| Engine | Pros | Cons | When |
|--------|------|------|------|
| **LSM (RocksDB)** | High write throughput | Compaction IO | **Default choice** |
| B-Tree | Read-friendly | Write amp random | Read-heavy small |
| In-memory + snap | Fast | Cost | Pure cache |
| Custom bitcask | Simple | Compaction/range | Teaching designs |

**Chosen:** LSM per node with:

- Memtable + WAL  
- SST levels  
- Tombstones for delete/TTL  
- Rate-limited compaction

### 3.6 Caching

Often a **look-aside cache** (memcache/Redis) sits in front for ultra-hot Gets. KV remains source of truth.

| Layer | Role |
|-------|------|
| Client cache | Rare; careful TTL |
| Proxy cache | Optional |
| Off-box memcache | Hot keys |
| Block cache in RocksDB | SST blocks |

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Partition | Range + directory | Split/scan | Static hash no move |
| Consensus | Raft per shard | Clear durability | Hope-based replication |
| Engine | LSM | Write-heavy social | Unbounded B-Tree random write |
| Cross-region | Async DR | Latency | Sync cross-coast “strong + fast” |
| Hot key | Cache + stripe | Skew | Ignore Zipf |
| Multi-key txn | Out of MVP | Honesty | Hidden 2PC complexity |

---

## 4. Architecture Diagram

```text
                     +-------------------+
   Apps ---------->  | Proxies / Clients |
                     +---------+---------+
                               |
                               v
                     +---------+---------+
                     | Shard Directory   |
                     | (keyrange→shard)  |
                     +---------+---------+
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
     +-------------+    +-------------+    +-------------+
     | Shard A     |    | Shard B     |    | Shard C     |
     | L F F       |    | L F F       |    | L F F       |
     +------+------+    +------+------+    +------+------+
            |                  |                  |
            v                  v                  v
       RocksDB/LSM          RocksDB            RocksDB
       WAL+SST              WAL+SST            WAL+SST

   Control Plane: membership, scheduler, rebalancer, config
   Backup Plane: snapshot + WAL archive
   Observability: metrics, tracing, slow query / hot key
```

**Put path:**

```text
Client Put
  -> resolve shard (cached map + epoch)
  -> send to leader
  -> append Raft log
  -> majority disk/WAL ack
  -> apply to memtable
  -> respond version
```

**Get path (linearizable):**

```text
Client Get
  -> leader
  -> ReadIndex / lease read
  -> memtable/block cache/SST
  -> return
```

**Follower stale read:**

```text
Get(consistency=eventual, max_stale=100ms)
  -> nearest follower if lag OK else forward leader
```

**Split path:**

```text
Admin/auto: choose split key
  -> quiesce or dual-route
  -> create new Raft group
  -> update directory epoch++
  -> clients refresh on mismatch
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Acked Put is in majority WAL** for the shard’s primary region.  
2. **Directory epoch fencing** — stale clients don’t write wrong leaders forever.  
3. **Single leader per shard term** — Raft.  
4. **Tombstones eventually compacted** but Get respects deletion before space reclaim.  
5. **Backup doesn’t mutate serving truth**.

#### 5.1.2 Failure handling

| Failure | Mechanism |
|---------|-----------|
| Leader crash | Election; clients refresh |
| AZ loss | Remaining majority (RF=3 across AZs) |
| Disk corruption | Checksums; restore from peers/backup |
| Lost minority | Catch-up via snapshot + log |
| Directory outage | Cached maps continue; updates blocked eventually — make directory HA |

#### 5.1.3 Consistency options (be explicit)

| Mode | Implementation | Use |
|------|----------------|-----|
| Linearizable Get/Put | Leader + Raft | ACL, critical metadata |
| Lease reads | Leader lease | Lower Get latency |
| Bounded stale | Follower lag check | Feed-ish reads |
| Dirty local | Local mem only | Never for durable API |

**Deal-breaker:** claiming linearizable reads from async cross-region replicas.

#### 5.1.4 CAS / versions

```text
Put(key, val, expect=v)
  if current.ver != v: fail
  else commit v+1

Prevents lost updates on single key without full txn.
```

### 5.2 Scalability

#### 5.2.1 Rebalancing

| Operation | Notes |
|-----------|-------|
| Split | Hot/large range → 2 |
| Merge | Tiny cold ranges |
| Move | Copy SST/snapshot to new nodes; cutover |

Use **epoch** on shard map; clients retry on `WRONG_SHARD` / `STALE_EPOCH`.

#### 5.2.2 Hot keys

| Technique | When |
|-----------|------|
| Front cache | Read-hot |
| Request coalescing | Same key stampede |
| Key striping `key#n` | Write-hot counters (app-level) |
| Dedicated hot shard / node | Extreme |
| Rate limit per key | Abuse |

KV alone can’t fix chatty apps — expose metrics so apps stripe counters.

#### 5.2.3 Compaction & write amp

```text
Write amplification LSM levels ~10–30× possible if untuned
Budget compaction IO per disk
Prefer leveling vs universal based on workload
Separate WAL disk / NVMe namespaces if needed
```

#### 5.2.4 Multi-tenant isolation

| Tool | Effect |
|------|--------|
| Per-ns quotas (QPS, storage) | Fairness |
| Separate disk groups | Noisy neighbor |
| Priority queues | Control vs user |
| Hedged / admission | Overload |

#### 5.2.5 Progressive scale map

| Scale | Topology |
|-------|----------|
| Baseline | One regional cluster, 3 AZ |
| 10× | Many proxies; auto-split; compaction governor |
| 100× | Multiple regional cells; async DR |
| 1,000× | Cell fabric + global routing directory |

### 5.3 Maintainability

#### 5.3.1 Control plane vs data plane

Keep Raft shards for data; **do not** put every Put through a global monolithic lock service.

Directory/membership HA using its own consensus cluster (small).

#### 5.3.2 Observability

| Signal | Why |
|--------|-----|
| Put/Get latency histograms per shard | SLO |
| Raft lag | Stale risk |
| Compaction debt | Impending latency cliff |
| Hot key top-N | Skew |
| Disk WAL latency | fsync health |
| Split/move success | Operability |

#### 5.3.3 Upgrades

- Rolling follower first; leader transfer; binary dual-running.  
- Soft feature flags for storage format versions.  
- Snapshot backward compatible.

#### 5.3.4 Testing

- Jepsen-style partition tests.  
- Chaos kill leaders.  
- Soak compaction under load.  
- Verify CAS under concurrency.

### 5.4 Durability details

```text
group commit:
  batch many Puts into one fsync
  trade latency vs throughput

fsync policy:
  ALWAYS on WAL before majority ack (default durable)
  or PERIODIC for softer durability tiers (explicit API)
```

Offer durability tier only if product needs — don’t silently lose data.

### 5.5 Delete & TTL

```text
Delete = tombstone with version
TTL = expire_ts in metadata
Get checks expire
Compaction drops expired/tombstoned when safe (snapshot isolation vs open reads)
```

### 5.6 Snapshot & backup

```text
Periodic SST snapshot + WAL shipping to object store
Restore: create shard from snapshot, replay WAL
Cross-region DR: async replica apply
RPO = lag; RTO = promote runbook
```

### 5.7 Client smarts

| Behavior | Purpose |
|----------|---------|
| Cache shard map | Perf |
| Retry with backoff | Transient |
| Hedged get | Tail latency |
| Locality prefer AZ | Latency |
| Idempotency tokens | Safe retries on Put if app needs |

### 5.8 Consistent hashing & directory deep dive

#### 5.8.1 Directory as source of truth

```text
shard_map_epoch E
key → find range R where start ≤ key < end → shard_id
shard_id → {leader, followers, voters}
Clients cache map; on NOT_LEADER / MAP_STALE refresh
Fencing: requests carry map_epoch; reject if too old for writes
```

#### 5.8.2 Ring vs explicit ranges

| Model | Use |
|-------|-----|
| Consistent hash ring | Even point keys; weaker scans |
| Explicit ranges + splits | Ordered keys; operable moves |
| Hybrid: hash(user) then range | Multi-tenant isolation |

**Interview preference for Meta KV:** directory + ranges (or hash buckets with directory), not “only buzzword consistent hashing” without membership.

#### 5.8.3 Rebalance

```text
split(shard): pick mid key → two Raft groups; directory atomic swap
move(shard): add learner → catch up → promote → remove old
Throttle bytes/s; never move all hot shards same hour
```

### 5.9 Replication & quorum deep dive

#### 5.9.1 Raft put path

```text
client → leader
leader append WAL
parallel send AppendEntries
majority durable → apply to state machine → ACK
followers apply async after commit index
```

#### 5.9.2 Quorum choices

| Mode | W/R | Property |
|------|-----|----------|
| Raft majority | implicit | Linearizable with leader reads |
| Dynamo W=2,R=2,RF=3 | explicit | Quorum intersection; conflict resolve |
| R=1 follower | fast | Stale bounded |

#### 5.9.3 Leader failure

```text
Election ≤ election timeout
Clients retry; idempotent app tokens if duplicate Put risk
Uncommitted entries may be lost — never ACK before majority
```

### 5.10 Compaction deep dive

#### 5.10.1 Why LSM needs governance

Unchecked compaction steals disk bandwidth → Put/Get p99 explode. Treat compaction as a **scheduled resource** with debt SLOs.

#### 5.10.2 Policies

```text
leveled: lower read amp, steady write amp
universal: burstier; sometimes for write-heavy
space amp vs write amp tradeoff explicit
```

#### 5.10.3 IO governor

```text
if foreground_latency > SLO: reduce compaction threads
if debt > D_max: prioritize compaction (accept write slowdown)
never both full rebalance + full compact + backup on same node
```

### 5.11 Tombstones & TTL deep dive

#### 5.11.1 Delete semantics

```text
Delete writes tombstone version V
Get sees tombstone → not_found
Compaction drops key when all older versions obsolete AND no snapshot needs them
```

#### 5.11.2 TTL

```text
expire_ts stored with value
Lazy: Get filters expired
Eager: compaction / TTL scanner drops
Clock: use shard hybrid logical or carefully synced wall clock; document skew tolerance
```

#### 5.11.3 Tombstone storms

Bulk delete namespaces → generate huge tombstone volume → schedule ranged delete / compaction jobs; quota per tenant delete rate.

### 5.12 Hot keys & multi-tenant

```text
Detect QPS/byte outliers
Mitigations: client-side cache, request coalescing, key salting (app-level),
  admission control, dedicated hot shard isolation
Tenant quotas: QPS, storage, compaction debt share
```

### 5.13 Progressive scale (10× / 100× / 1,000×)

| Jump | Topology | Engine | Consistency story |
|------|----------|--------|-------------------|
| →10× | More shards; splits | Compaction governors | Same Raft |
| →100× | Regional cells | Tiered storage | Async DR explicit RPO |
| →1,000× | Hierarchical directories | Cold EC/object tier | Per-cell autonomy |

**Narrative:** scale is shard count + IO governance + hot-key policy; not “bigger single Raft group.”

### 5.14 Failure drills

| Drill | Expected |
|-------|----------|
| Kill leader | Elect; brief elevate errors; no ACK loss |
| Disk stall | Isolate node; thrash alerts |
| Directory outage | Cached map serves reads briefly; writes careful |
| Compaction debt cliff | Autothrottle puts; page oncall |

### 5.15 Read path consistency matrix

| API option | Served from | Stale bound | Use |
|------------|-------------|-------------|-----|
| `linearizable` | Leader (or quorum read) | 0 | ACL, counters needing truth |
| `bounded_stale_ms=T` | Follower with lag≤T | T | Timeline reads |
| `eventual` | Any replica | unbounded | Best-effort cache fill |

**Deal-breaker:** defaulting all Gets to arbitrary followers while selling “strong KV” for payment-adjacent keys.

### 5.16 Write path edge cases

#### 5.16.1 CAS / expect_ver

```text
Put(k, v, expect_ver=V)
  if current.ver != V → CAS_FAILED (no write)
  else commit V' = V+1
Used for: inventory, config, session fencing
```

#### 5.16.2 Large values

```text
Reject over max_value_size (e.g. 1 MB) at API
Or chunk externally (object storage) and store pointer in KV
Don't turn KV into blob store accidentally
```

#### 5.16.3 Multi-key transactions

Out of MVP. Mention: per-key linearizability ≠ multi-key atomicity; use app-level saga or separate txn layer.

### 5.17 Cross-region evolution detail

| Scale | Pattern | RPO | Put latency |
|-------|---------|-----|-------------|
| Baseline | 3 AZ one region | disk loss only | few ms |
| 10× | same + backups to object store | minutes (backup) | few ms |
| 100× | async regional replica | seconds–minutes | few ms local |
| 1,000× | active-active per cell; conflict avoid by key affinity | cell-local | few ms; cross-cell explicit |

**Affinity rule:** keys owned by a home region/cell; cross-cell access is forward, not dual-master every key.

### 5.18 Interview “why not Redis Cluster only?”

| Need | Redis-like | This KV |
|------|------------|---------|
| Durable majority WAL | optional/AOF nuances | core |
| Large dataset >> RAM | painful | LSM on disk |
| Operable splits | limited | directory first-class |
| Multi-tenant quotas | add-on | designed-in |

Redis/Memcached remain **cache plane** in front; don't confuse planes.

---

## 6. Wrap-Up

### 6.1 Design summary

A Meta-scale **KV database**:

1. **Range-sharded** data with a **versioned directory**.  
2. **Raft leaders** per shard; majority WAL durability.  
3. **LSM** storage with TTL/tombstones and compaction budgets.  
4. Tunable reads (linearizable vs bounded stale).  
5. Online split/move; hot-key defenses; multi-tenant quotas.  
6. Regional cells + async DR at large scale.

### 6.2 Key tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Consistency vs latency | Strong in-region; async cross-region |
| Range vs hash | Ranges + splits |
| Compaction vs write amp | Governor + tuning |
| Operability vs perfection | Explicit RPO on DR |

### 6.3 Deal-breakers

- Sync cross-continent majority at ms latency.  
- No rebalance/split plan.  
- Leaderless conflicts without app story.  
- Ignoring compaction debt.  
- Promising distributed multi-key ACID in MVP silently.

### 6.4 30-minute checklist

1. Clarify API, consistency, TTL, size, regions.  
2. Estimate data, QPS, shard size, WAL GB/s.  
3. Draw directory → Raft shard → LSM.  
4. Failover + split + hot key.  
5. Cross-region RPO.  
6. Scale jumps.  
7. Deal-breakers.

---

## 7. Deeper / Related Interview Questions

### 7.1 API & data model

**Q1: Why not SQL?**  
A: Many online workloads need predictable point access and operability; SQL is a different system (or layer).

**Q2: Value size limit rationale?**  
A: Large values hurt latencies/compactions; blob store + pointer pattern.

**Q3: Single-key CAS vs multi-key txn?**  
A: CAS covers many counters/config cases; multi-key needs 2PC/Percolator — Phase 2.

**Q4: Namespaces?**  
A: Tenant isolation, quotas, key encoding; optional separate clusters for ultra tenants.

**Q5: Why return versions on Get?**  
A: Enable CAS and cache validation.

### 7.2 Sharding & routing

**Q6: Hash vs range partitioning?**  
A: Hash balances; range enables scans and hotspot splits. Directory-based ranges preferred here.

**Q7: How do clients find leaders?**  
A: Cached shard map; on error refresh from directory; epoch fencing.

**Q8: What is a good shard size?**  
A: Tens–hundreds of GB trade move time vs Raft group count; avoid millions of tiny idle groups without hierarchy.

**Q9: Virtual nodes?**  
A: Help consistent hashing; with directory ranges you split explicitly instead.

**Q10: How to avoid directory bottleneck?**  
A: HA consensus cluster; client cache; directory not on Put data path beyond lookup.

### 7.3 Consensus & consistency

**Q11: Why Raft per shard not one Raft for whole DB?**  
A: Throughput; blast radius; parallel leadership.

**Q12: ReadIndex vs lease reads?**  
A: ReadIndex safe with round; leases faster but need time bounds — discuss carefully.

**Q13: Can followers serve Gets?**  
A: Yes with staleness bound; not linearizable unless techniques applied.

**Q14: Split brain prevention?**  
A: Majority quorum + term fencing; clients don’t accept lower terms.

**Q15: What happens in minority partition?**  
A: Writes fail; reads may be rejected for strong mode.

### 7.4 Storage engine

**Q16: Why LSM for social writes?**  
A: Sequential WAL + amortized SST writes handle high put rates better than random B-Tree.

**Q17: Compaction debt symptoms?**  
A: Read latency ↑, disk busy, space amplification ↑ — throttle writes, add disks, tune levels.

**Q18: How do TTLs work?**  
A: Expire metadata; Get hides; compaction drops.

**Q19: Memtable flush vs fsync?**  
A: Durability from WAL; memtable is performance; crash replay WAL.

**Q20: Checksums?**  
A: Per block/record; detect bitrot; restore from replica.

### 7.5 Hot keys & overload

**Q21: Read hot key?**  
A: Coalesce + memcache + leader cache.

**Q22: Write hot counter?**  
A: Application striping `counter#0..N` + periodic rollup; or specialized counter service.

**Q23: Admission control?**  
A: Per-ns and per-disk token buckets; shed low priority.

**Q24: Thundering herd after outage?**  
A: Client jitter; proxy coalescing; cache stampede locks.

**Q25: Hedged requests risk?**  
A: Amplification; use only on p99 tails with cancellation.

### 7.6 Multi-region & DR

**Q26: Sync cross-region?**  
A: High latency; rarely default for user-facing Puts.

**Q27: Async DR RPO?**  
A: Seconds–minutes lag; communicate product impact.

**Q28: Failover steps?**  
A: Stop writes old; promote DR; directory update; accept RPO loss window.

**Q29: Multi-master same key?**  
A: Conflicts (LWW/CRDT) — usually avoid for strong KV; use home region.

**Q30: Follow-the-sun tenants?**  
A: Per-ns primary region; migrate with planned cutover.

### 7.7 Operations

**Q31: Online schema?**  
A: Opaque values — app evolves; storage format versioned.

**Q32: Backup consistency?**  
A: Per-shard snapshot at Raft index; restore set of shard snapshots + indexes.

**Q33: How to test rebalance?**  
A: Shadow traffic; verify checksums; dual read.

**Q34: Noisy neighbor?**  
A: Quotas, separate pools, IO weights.

**Q35: Rolling upgrade order?**  
A: Followers → transfer leadership → old leader.

### 7.8 Alternatives & deal-breakers

**Q36: Pure Dynamo AP design?**  
A: Valid if interviewer wants AP; then discuss vector clocks/repair — different product promises.

**Q37: Redis Cluster as DB?**  
A: Great cache; durability/operability semantics differ; not automatic substitute for WAL Raft KV.

**Q38: One RocksDB on one giant machine?**  
A: Capacity/availability ceiling; no AZ tolerance.

**Q39: Store everything in MySQL?**  
A: Possible substrate; still need sharding layer — you’re designing that layer.

**Q40: Exact global total order of all keys’ writes?**  
A: Unnecessary and unscalable; per-shard order enough.

### 7.9 Interview craft

**Q41: How to open?**  
A: API, consistency, size, QPS, regions, TTL, scan need — lock MVP.

**Q42: Numbers that matter?**  
A: Data size × RF, ops/s, shard count, WAL GB/s, RTT, hot key skew.

**Q43: L5+ impress?**  
A: Explicit consistency modes, compaction budgets, directory epochs, cross-region RPO honesty, hot-key striping.

**Q44: Common mistake?**  
A: Drawing boxes without quorum ack semantics; or ignoring compaction/hot keys.

**Q45: How does this relate to TAO/memcache?**  
A: Social graph/cache layers sit above; KV/DB provides durable point storage primitives.

---

### Appendix A — Key encoding

```text
[ns_len][ns][user_key]
optional hash prefix for scatter: [hash8][ns][user_key]
```

### Appendix B — Raft put pseudocode

```text
onPut(k,v):
  assert leader
  e = log.append(Put(k,v))
  wait majority commit
  apply(e)
  return e.ver
```

### Appendix C — Get linearizable

```text
onGet(k):
  confirm leadership (ReadIndex/lease)
  return store.get(k)
```

### Appendix D — Split

```text
choose splitKey
create shard' with peers
copy data >= splitKey
publish map epoch+1
reject old routes with STALE
```

### Appendix E — TTL

```text
record {v, expire_at, ver}
get: if now >= expire_at: not_found
compact: drop if expire_at < now - grace
```

### Appendix F — NFR card

```text
In-region Put p99 < 40ms durable majority
Get p99 < 20ms leader
RF=3 AZ
Async DR RPO explicit
Online split/move
```

### Appendix G — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Auto-split, compaction governor |
| 100× | Regional cells, tenant quotas |
| 1,000× | Cell fabric, global directory |

### Appendix H — Error codes

| Code | Meaning |
|------|---------|
| NOT_FOUND | Missing/expired |
| CAS_FAILED | Version mismatch |
| NOT_LEADER | Refresh map |
| STALE_EPOCH | Directory refresh |
| OVER_QUOTA | Tenant limit |
| TOO_LARGE | Value size |
| UNAVAILABLE | No quorum |

### Appendix I — Latency budget table

| Step | ms |
|------|-----|
| Route | 0.2 |
| Raft replicate | 0.5–1 |
| WAL group commit | 0.5–2 |
| Apply | 0.1 |
| Total Put | ~2–5 |

### Appendix J — Compaction IO governor

```text
if compaction_io > budget:
  slow flushes / writes
alert on debt hours-to-drain
```

### Appendix K — Hot key playbook

```text
1 detect top keys
2 cache Gets
3 ask app to stripe writes
4 isolate shard
5 rate limit
```

### Appendix L — Backup pipeline

```text
shard snapshot @ index I
upload SSTs
tail WAL > I to object storage
restore = snapshot + replay
```

### Appendix M — Directory schema

```text
Shard { id, start_key, end_key, peers[], leader_hint, epoch }
```

### Appendix N — Worked example

```text
1M puts/s × 1KB = 1 GB/s data
RF3 → 3 GB/s cluster write path before amp
100 nodes → 30 MB/s/node average — OK
10 hot shards taking 50% → need split/cache
```

### Appendix O — Consistency cheatsheet

| Need | Mode |
|------|------|
| Password/ACL | Linearizable |
| Async counters display | Bounded stale |
| Cross-region display | Eventual + home write |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Shard / range | Key interval ownership |
| Raft term | Leadership epoch |
| WAL | Write-ahead log |
| SST | Sorted string table |
| Tombstone | Delete marker |
| Directory epoch | Map version |

### Appendix Q — Comparison: Dynamo vs Raft-KV

| | Dynamo-style | Raft-KV (this) |
|--|--------------|----------------|
| Write avail | Higher under partition | Majority required |
| Conflicts | App/VC/CRDT | Leader serializes |
| Ops model | Repair anti-entropy | Leader catch-up |
| Fit | Shopping cart AP | Strong metadata |

### Appendix R — Security

```text
TLS mutual auth clients
AuthZ per namespace
Encryption at rest
Audit admin ops
```

### Appendix S — Failure drill

| Drill | Expect |
|-------|--------|
| Kill leader | Elect < few sec |
| Kill AZ | Continue on 2 |
| Fill disk | Reject writes |
| Stall compaction | Alert; throttle |

### Appendix T — Client retry

```text
retryable: NOT_LEADER, UNAVAILABLE, timeout
not retryable without care: CAS_FAILED (app logic)
use jittered exponential backoff
```

### Appendix U — Why group commit

```text
fsync per Put at 1M/s impossible on one disk
batch 100 Puts / fsync → 10K fsync/s still hard
hence many shards × group commit
```

### Appendix V — 30m checklist compact

```text
API/consistency → Math → Directory+Raft+LSM → Failover
→ Hot key → DR RPO → Scale → Deal-breakers
```

---

*End of Distributed Key-Value Database system design.*
