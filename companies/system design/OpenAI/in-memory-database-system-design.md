# System Design: In-Memory Database (Redis-like)

> **Focus areas:** Event loop · Data structures · TTL · Eviction · Persistence · Replication · Cluster · Transactions  
> **Style:** Build-from-scratch Redis-class system with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split ops/load classes, explicit durability/consistency trade-offs, resolved ownership of replication vs persistence

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

Goal: **bound the product**—what Redis-like capabilities we build, what consistency/durability we promise, and at which scale single-node vs cluster must hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the primary use? | Cache + fast KV + data structures (counters, queues, leaderboards) | Not a full SQL DB; optimize memory + ops/s |
| F2 | Data types? | String, Hash, List, Set, Sorted Set; Stream Phase 1.5 | Type-tagged values; encoding optimizations (ziplist/listpack) |
| F3 | TTL / expiry? | Per-key TTL; lazy + active expiration | Timing wheel or heap + sampling |
| F4 | Eviction? | When `maxmemory` hit: LRU/LFU/volatile/allkeys policies | Eviction is not TTL; separate mechanism |
| F5 | Persistence? | Optional RDB snapshots + AOF; configurable durability | Durability ≠ default; document RPO |
| F6 | Replication? | Async primary→replica; failover | Replica lag; split-brain fencing |
| F7 | Clustering? | Horizontal shard by key hash slots | 16384 slots (Redis-like); resharding |
| F8 | Transactions? | MULTI/EXEC optimistic; Lua atomic scripts | Single-thread semantics simplify |
| F9 | Pub/Sub? | Best-effort channels | Not durable; separate from KV durability |
| F10 | Client protocol? | RESP-like text/binary protocol over TCP | Pipelining, multiplexing |

**MVP functional scope (lock with interviewer):**

1. Single-node server: TCP protocol, GET/SET and core data structures.
2. Per-key TTL with lazy + active expiry.
3. `maxmemory` + eviction policy (at least `allkeys-lru`).
4. RDB snapshot **or** AOF (ship both conceptually; implement one deeply).
5. Async replication primary→replicas; info on failover.
6. Cluster mode design: hash slots, redirect (`MOVED`/`ASK`).
7. MULTI/EXEC + Lua atomicity model.
8. Metrics: memory, ops/s, hit rate, replication lag, evictions.

**Out of MVP (explicitly defer):**

- Strong multi-primary CRDTs
- Disk-native LSM hybrid (Redis on Flash / KeyDB specifics optional mention)
- Full Redis module ecosystem
- Exactly-once Pub/Sub
- SQL / secondary indexes as primary API
- Multi-key ACID across slots without hash tags

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency? | Sub-millisecond in-region | p50 < 0.5ms, p99 < 2ms for in-memory hits (same AZ) |
| N2 | Throughput? | Extremely high ops | Baseline 100K–1M ops/s per fat node (pipeline-dependent) |
| N3 | Durability? | Configurable | AOF everysec RPO≈1s; always RPO≈0 (fsync); RDB-only RPO=minutes |
| N4 | Availability? | HA with replicas | Automatic failover < 30s typical; accept brief write unavailability |
| N5 | Consistency? | Primary reads/writes linearizable per key (single primary) | Replica reads may lag (stale) |
| N6 | Memory efficiency? | Critical | Per-key overhead accounted; encodings matter |
| N7 | Scalability? | Vertical then horizontal | Cluster sharding; not naïve “more threads = more speed” |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. SET key value EX 60 → GET hits → expires → GET miss.  
2. Memory pressure → LRU evicts cold keys → hot keys retained.  
3. BGSAVE → RDB on disk; restart loads RDB.  
4. AOF rewrite; restart replays AOF.  
5. Replica syncs via full + partial resync; serves reads.  
6. Cluster: SET `{user:42}.profile` stays on same slot as related keys.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Hot key | Single slot/node bottleneck; application must shard key space |
| Big key (1GB hash) | Blocks; prefer size limits / gradual delete |
| Swap thrash | **Deal-breaker** for latency SLOs—never rely on OS swap |
| Primary crash before AOF fsync | Lose ≤ RPO window |
| Split brain two primaries | Fencing via quorum (Raft/Sentinel-like); clients must redirect |
| MULTI across slots | Reject or require hash tags; no silent partial |
| Replication backlog overflow | Fall back to full resync |
| Expiration storm | Active expiry sampling + lazy; spread load |
| Fork for BGSAVE on huge RSS | Copy-on-write memory spike—capacity plan |
| Client pipeline flood | Input buffer limits; maxclients |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Working set (useful data) | 64 GB | 640 GB | 6.4 TB | 64 TB |
| Keys | 100M | 1B | 10B | 100B |
| Ops/s (cluster aggregate) | 500K | 5M | 50M | 500M |
| Connections | 50K | 500K | 5M | 50M |
| Primary nodes | 1 | 3–6 | 50–100 | 500–1000 |
| Replicas / primary | 1 | 1–2 | 2 | 2+ |
| Network (assume 200B/op avg) | ~100 MB/s | ~1 GB/s | ~10 GB/s | ~100 GB/s |
| AOF disk write (everysec) | tens of MB/s | hundreds MB/s | GB/s class | sharded |

**What each jump forces:**

- **10×:** Replication + Sentinel/Raft failover; pipelining norms; eviction tuning.  
- **100×:** Hash-slot cluster; proxy or smart clients; resharding ops.  
- **1,000×:** Multi-cluster cells; rack/AZ awareness; hot-key detection; tiered storage optional.

### 1.5 Etc. (Constraints & Assumptions)

- **We design a Redis-like server**, not “use managed Redis.”  
- **Memory is the source of truth** for serving; disk is for durability/recovery.  
- **Single-threaded command execution** is the default mental model (I/O threads optional).  
- **Clients** may be dumb (ask cluster) or use a proxy.

**Scope statement:**

> Design an in-memory database: single-threaded (or logically single-writer) command execution, rich data structures, TTL and eviction, optional RDB/AOF persistence, async replication with failover, and hash-slot clustering—starting at ~64GB / 500K ops/s and scaling through 10× / 100× / 1,000× with clear durability and split-brain invariants.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| **Reads** (GET, etc.) | ~400K/s | ~400M/s | Often 80%+ of traffic |
| **Writes** (SET, INCR) | ~100K/s | ~100M/s | Drive AOF/replication |
| **Expirations** processed | ~10K/s | ~10M/s | Bursty |
| **Evictions** | variable | variable | Under memory pressure |
| **Replica traffic** | ≈ write rate × replicas | same | Amplification |
| **Pub/Sub messages** | separate | separate | Don’t mix into KV SLOs |

### 2.2 Memory accounting

```text
Naive: 100M keys × 16B key × 64B value = ~8 GB payload
Reality: per-key overhead (allocator, dict entry, TTL) often +50–100 B
→ 100M × 80 B overhead ≈ 8 GB overhead alone
SDS/string encodings, jemalloc bins, fragmentation (1.2–1.5×)

Capacity rule:
  provisioned RAM ≥ working_set × fragmentation × (1 + CoW_headroom)
  CoW_headroom during BGSAVE/AOF rewrite: often +20–100% transient
```

At **64 TB** useful data (1,000×):

```text
Need ~500–1000 nodes × 64–128 GB — cluster mandatory
Per-node hot key still limited by single core / single slot owner
```

### 2.3 Throughput vs threading

```text
Single-threaded Redis-class: ~100K–1M+ ops/s depending on payload & pipeline
Pipelining 10 commands: amortizes syscall/network → multiplies effective ops

1M ops/s × 200 B ≈ 200 MB/s ≈ 1.6 Gbps (payload only)
Cluster 500M ops/s → terabit-class fabric across fleet
```

### 2.4 Persistence I/O

```text
AOF everysec: write stream ≈ write_ops × avg_cmd_size
100K write/s × 100 B ≈ 10 MB/s — easy
10M write/s × 100 B ≈ 1 GB/s — needs fast disks + rewrite strategy

RDB every 5 min of 64 GB:
  serialize ~64 GB; network/disk bound; CoW during fork
```

### 2.5 Replication backlog

```text
backlog size ≥ peak_write_bytes_per_sec × max_disconnect_seconds
e.g. 50 MB/s × 120 s ≈ 6 GB backlog to allow partial resync
Else full resync (expensive): transfer entire dataset
```

### 2.6 TTL wheel sizing

```text
Keys with TTL: say 50% of 100M = 50M
Timing wheel vs random sampling (Redis active expire):
  sampling avoids huge timer structures; amortized CPU
```

---

## 3. High-Level Design

### 3.1 Process architecture

```text
+----------------------------------------------------------+
|                     Server Process                        |
|  +-------------+   +------------------+   +------------+ |
|  | I/O (epoll) |-->| Command execute  |-->| Dict + DS  | |
|  | accept/read |   | (single thread)  |   | TTL tables | |
|  +-------------+   +---------+--------+   +------+-----+ |
|        ^                     |                   |       |
|        |                     v                   v       |
|   Client TCP           Replication feed    Eviction/Expire|
|                        AOF / RDB hooks                   |
+----------------------------------------------------------+
```

### 3.2 Single-threaded vs multi-threaded

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **A. Single-thread execute** | No lock; simple atomicity; predictable | One core bound; big-key stalls | Classic Redis; **default choice** |
| **B. I/O threads + single execute** | Parallel read/write syscalls | Still one execute core | High connection counts |
| **C. Sharded event loops (shared-nothing)** | Multi-core | Cross-shard txn hard; more complexity | KeyDB-like / custom |
| **D. Fine-grained locks** | Parallel | Deadlocks, complexity, cache-line contention | Rarely worth it for Redis API |

**Choice: A (+ optional I/O threads).** Horizontal scale via **cluster slots**, not mutexes.

**Deal-breaker:** claiming multi-thread shared dict without a locking story, or promising multi-key transactions across threads without definition.

### 3.3 Core data structures

```text
dict: hash table key → robj (type-tagged)
  String: SDS / int encoding
  Hash: hashtable or listpack (small)
  List: quicklist
  Set: hashtable or intset
  ZSet: skiplist + dict
```

**Skiplist for ZSET:** O(log N) by score; dict for O(1) member→score.

**Memory encodings:** small hashes/sets use compact encodings; convert when thresholds exceeded.

### 3.4 TTL / expiration

**Mechanisms:**

1. **Lazy:** on access, if `now ≥ expire_at`, delete.  
2. **Active:** periodic sampling of keys with TTL; delete expired.  
3. **Optional timing wheel / min-heap:** more precise; memory cost.

**Redis-like active expire:** each cycle sample N keys from expires dict; if > fraction expired, continue (adaptive).

**Trade-offs:**

| | Lazy only | Active sampling | Exact timers |
|--|-----------|-----------------|--------------|
| CPU | Low | Medium | Medium-high |
| Memory of stale keys | Can linger | Bounded | Minimal linger |
| Precision | Access-dependent | Probabilistic | High |

**Expires vs eviction:** TTL is semantic lifetime; eviction is memory pressure. A key can be evicted before TTL.

### 3.5 Eviction policies

| Policy | Behavior | Use |
|--------|----------|-----|
| `noeviction` | Reject writes when full | Prefer fail loud |
| `allkeys-lru` | Evict least recently used among all | General cache |
| `volatile-lru` | LRU among keys with TTL | Mixed durable+cache |
| `allkeys-lfu` | Least frequently used | Skewed popularity |
| `volatile-ttl` | Evict nearest TTL | Short-lived cache |
| ARC (mention) | Adaptive LRU/LFU | Advanced; more state |

**Approximate LRU:** sample random keys, evict best candidate (cheap vs true LRU list).

**LFU:** decaying counters; careful about counter saturation.

**Deal-breaker:** swapping to disk silently—latency collapses. Set `maxmemory` and monitor evictions/sec.

### 3.6 Persistence: RDB vs AOF

| | RDB | AOF |
|--|-----|-----|
| Format | Point-in-time binary dump | Append command log |
| Restore speed | Fast | Slower (replay); rewrite compacts |
| RPO | Last snapshot | fsync policy: always / everysec / no |
| Cost | Fork CoW spikes | Disk bandwidth; rewrite CoW |
| Corruption | Whole file | Truncate last incomplete command |

**fsync policies:**

| Policy | RPO | Latency impact |
|--------|-----|----------------|
| `always` | ≈0 | High (fsync/cmd) |
| `everysec` | ≈1s | Small (default sweet spot) |
| `no` | OS dependent | Lowest |

**Ownership:** persistence is for **recovery of a node**; replication is for **HA**. Do not assume replica = durable (replica may be in-memory only).

**Combined:** RDB+AOF hybrid (AOF after RDB base) for faster restart—optional advanced.

**AOF rewrite:** background process produces compacted AOF without stopping serving; atomic swap.

### 3.7 Replication

```text
Primary --async commands--> Replica1
        --async commands--> Replica2

Bootstrap:
  1) Full sync: RDB/stream snapshot + buffer of commands during snapshot
  2) Continue incremental stream
Partial resync: if replica offset within backlog, replay backlog only
```

**Consistency:** asynchronous → acknowledge write to client before replica apply (default). Optional WAIT N for bounded durability to replicas.

**Failover (Sentinel/Raft-like):**

1. Quorum of monitors detects primary down.  
2. Elect replica with best offset / priority.  
3. Promote; fence old primary (epoch/config epoch).  
4. Clients update topology.

**Split brain deal-breaker:** two writable primaries accepting writes without epoch fencing → divergent datasets.

### 3.8 Cluster hashing slots

```text
slot = CRC16(key) mod 16384
Hash tag: key "{user:42}.orders" → hash only "user:42"
→ multi-key ops must share slot
```

**Client protocol:**

- `MOVED slot node` — permanent redirect  
- `ASK slot node` — temporary during migration  

**Resharding:** migrate keys slot-by-slot; during migrate, `ASK` to target.

**Gossip / bus:** nodes exchange cluster state; not for data path.

### 3.9 Transactions & Lua

**MULTI/EXEC:** queue commands; execute sequentially uninterruptible (single thread). Optimistic: WATCH keys → abort if modified.

**Lua:** script runs atomically; multi-key OK **only if same slot** in cluster.

**Not relational ACID across arbitrary keys in cluster**—state this explicitly.

### 3.10 Client protocol & pipelining

```text
RESP-like:
  *2\r\n$3\r\nGET\r\n$3\r\nkey\r\n

Pipeline: send many commands without waiting → high ops/s
Mux: many logical clients per connection (optional) or many conns
```

**Timeouts, client output buffer limits** prevent slow consumers from OOM’ing server.

---

## 4. Architecture Diagram

### 4.1 Single node

```text
 Clients
    |
    v
+--------------------+
| TCP + RESP decode  |
+---------+----------+
          v
+--------------------+
| Event loop execute |
|  - call commands   |
|  - touch LRU/LFU   |
|  - expire lazy     |
+----+------+--------+
     |      |     \
     v      v      v
  Dict   Expires  Replication backlog
     |
     +--> AOF buffer --> disk
     +--> RDB fork child
```

### 4.2 HA pair / quorum

```text
          +-----------+
          | Sentinel/ |
          | Raft quorum|
          +-----+-----+
                | elect / fence
     +----------+----------+
     v                     v
+---------+           +---------+
| Primary | --repl--> | Replica |
+---------+           +---------+
```

### 4.3 Cluster

```text
Smart Client / Proxy
    |  (slot map)
    +-----+------+------+
    v     v      v      v
  N1    N2     N3     N4   (each owns slot ranges)
  |r    |r     |r     |r
  R1    R2     R3     R4
```

### 4.4 Sequence: SET with AOF everysec + replica

```text
Client → Primary: SET k v
Primary: update dict, update expire if any
Primary: append AOF buffer; add to repl backlog
Primary → Client: OK
Primary → Replica: SET k v (async)
Every ~1s: fsync AOF
```

### 4.5 Sequence: failover

```text
Sentinels: ping timeout → SDOWN → quorum ODOWN
Elect leader Sentinel → pick best replica
Replica: SLAVEOF NO ONE (epoch N+1)
Old primary returns: reconfigure as replica (fence)
Clients: refresh topology; retry writes
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Single writer per key/slot | Primary-only writes; epoch fencing |
| R2 | Commands on a node execute atomically w.r.t. each other | Single-thread execute |
| R3 | AOF/RDB recovery yields prefix-consistent state | fsync + truncate torn writes |
| R4 | Replica does not acknowledge as durable unless WAIT/policy says so | Document RPO |
| R5 | Failover never leaves two writable primaries in same epoch | Quorum + epoch |
| R6 | Cluster multi-key ops only same slot | Reject CROSSSLOT |
| R7 | maxmemory policies prevent unbounded RSS growth | Eviction / OOM errors |

**Degradations:**

| Failure | Behavior |
|---------|----------|
| Disk full (AOF) | Stop writes or disable AOF per policy; alert |
| Replica lag high | Serve reads with stale warning; don’t promote lagging replica |
| Hot big-key | Latency spike; ops kill / migrate / split |
| Network partition | Quorum minority refuses writes |

### 5.2 Scalability

**1×:** One primary + one replica; RDB/AOF; LRU.

**10×:** Vertical upgrade; I/O threads; Sentinel; connection pooling on app side.

**100×:** Cluster mode 50–100 primaries; smart clients; slot migration tooling; per-slot metrics.

**1,000×:** Multiple clusters by application cell; AZ-aware replica placement; proxies for dumb clients; hot-key splitting at app layer; optional RDMA/large pages tuning.

**Ownership resolution:**

| Concern | Owner |
|---------|-------|
| Command atomicity | Execute thread |
| Durability RPO | AOF/RDB config |
| HA promotion | Sentinel/Raft control plane |
| Slot ownership | Cluster config epoch |
| Memory limit | Eviction policy |
| Cross-slot logic | Application / hash tags |

### 5.3 Maintainability

- Clear metrics: `used_memory`, `frag_ratio`, `ops/s`, `evicted_keys`, `expired_keys`, `aof_delayed_fsync`, `repl_lag_bytes`, `blocked_clients`.  
- Big-key scanner offline.  
- Chaos: kill primary, disk stall injection.  
- Compatibility: protocol versioning.  
- Avoid unbounded `KEYS *` in prod—provide SCAN.

### 5.4 Concurrency model details

Even with single-thread execute:

- **Background threads/processes:** BGSAVE, AOF rewrite, async unlink (free large objects), I/O threads.  
- **Non-blocking deletes:** UNLINK vs DEL for big values.  
- **Copy-on-write:** understand RSS spikes during fork.

### 5.5 Memory fragmentation

- Allocator bins; active defrag optional.  
- Monitor `frag_ratio`; restart/reshard if pathological.  
- Encoding choices reduce pointers.

### 5.6 Security (brief)

- AUTH / ACLs per user; TLS; disable dangerous commands (`FLUSHALL`, `CONFIG`) in prod or rename; bind private nets; protect-mode.

---


### 5.5 Client libraries & smart routing

Dumb clients send commands to any node and follow `MOVED`/`ASK`. Smart clients cache slot maps and pipeline to the correct primary. Proxies (Twemproxy-like or cluster-aware sidecars) help legacy apps but add hop latency and can obscure CROSSSLOT errors—prefer smart clients at 100×+.

**Connection pooling math:**

```text
App instances 200 × pool 50 = 10,000 conns to a 6-node cluster
→ ~1.6K conns/node; ensure maxclients and file descriptors headroom
Multiplexed protocols / pipelining reduce conn count needs
```

### 5.6 Hot keys & big keys (operational deep dive)

| Symptom | Diagnosis | Mitigation |
|---------|-----------|------------|
| One CPU 100%, others idle | Hot key / hot slot | Split key, local cache, read replicas for reads |
| Latency spikes on DEL/HGETALL | Big key | UNLINK; scan-based delete; size caps |
| Full resync storms | Replica flaps + small backlog | Larger backlog; stabilize network; diskless sync |
| Sudden RSS climb | CoW during rewrite + write spike | Pause rewrite; rate-limit writes; more RAM |

**Hot-key detection:** track top-N command targets in a decaying sketch; alert when a key exceeds QPS threshold.

### 5.7 Consistency models clients should assume

| Read target | Consistency |
|-------------|-------------|
| Primary | Linearizable per key (single writer) |
| Replica | Eventually consistent; lag = bytes/time behind |
| WAIT N | Durability to N replicas acknowledged (still not multi-key ACID) |
| Cluster MGET scatter | Non-atomic snapshot across slots |

**Read-your-writes:** route user’s reads to primary (or session sticky to primary) after write.

### 5.8 Pub/Sub vs Streams (scope clarity)

**Pub/Sub:** fire-and-forget; no backlog persistence; offline subscribers miss messages. Use for ephemeral notifications.

**Streams (Phase 1.5):** persistent log with consumer groups—closer to Kafka-lite. Do not promise Kafka replacement at 1,000× without storage engineering.

### 5.9 Security hardening checklist

1. Bind private network / VPC only.  
2. AUTH ACLs with least privilege (no `FLUSHALL` for app users).  
3. TLS in transit.  
4. Disable/rename dangerous commands.  
5. Encrypt RDB/AOF at rest (disk/volume encryption).  
6. Audit `CONFIG SET` access.

### 5.10 Progressive scale playbook (node → cluster → cells)

```text
1×:  primary + replica, AOF everysec, allkeys-lru
10×: Sentinel/Raft failover tested monthly; connection pools standardized
100×: cluster slots; reshard runbooks; per-slot dashboards; CROSSSLOT CI checks
1,000×: app cells each with own cluster; global router by tenant; hot-key SWAT process
```

**Migration without downtime:** dual-write or live reshard slot-by-slot; verify checksum sampling; cut reads last.

---

## 6. Wrap-Up

### 6.1 Interview whiteboard order

1. Event loop + dict + type objects.  
2. TTL + eviction distinction.  
3. AOF everysec vs RDB; RPO.  
4. Async replication + failover fencing.  
5. Hash slots + CROSSSLOT.  
6. Scale story: vertical → replica → cluster → cells.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Single node, strings+hashes, TTL, LRU, AOF everysec |
| 10× | Replicas + quorum failover |
| 100× | Slot cluster + reshard |
| 1,000× | Multi-cluster cells, hot-key ops |

### 6.3 Top risks

1. Treating async replica as durable.  
2. Split brain on failover.  
3. Fork CoW OOM during BGSAVE.  
4. Hot keys / big keys.  
5. Cross-slot transactions assumed to work.

### 6.4 One-sentence design

> A single-writer, memory-first datastore with approximate TTL/eviction, configurable AOF/RDB durability, async replicas under quorum fencing, and hash-slot clustering for horizontal ops—scaled by shards, not shared-memory threads.

---

## 7. Deeper / Related Interview Questions

### 7.1 Concurrency & event loop

**Q: Why single-threaded?**  
A: Avoids lock complexity; makes MULTI/Lua atomic; uses epoll for concurrency of connections. Scale out with cluster.

**Q: Does single-threaded mean one core for everything?**  
A: Execute path yes; bio threads for fsync/close/unlink; child processes for rewrite/save; optional I/O threads.

**Q: How do you use multiple cores?**  
A: Sharding (cluster), multiple instances per machine (different ports), or shared-nothing multithreaded designs with trade-offs.

**Q: What happens with a slow command?**  
A: Head-of-line blocking; hence big-key hazards; prefer O(1)/O(log N) commands.

### 7.2 Data structures

**Q: Why skiplist for ZSET not only heap?**  
A: Need rank ranges + member lookup; skiplist+dict gives both.

**Q: Hash collision DoS?**  
A: SipHash-like keyed hashing; randomized seed.

**Q: Int encoding?**  
A: Store integers as packed objects to save memory.

### 7.3 TTL & eviction

**Q: Difference between EXPIRE and eviction?**  
A: EXPIRE is application TTL; eviction is maxmemory pressure.

**Q: How Redis expires keys without checking all?**  
A: Lazy on access + active sampling each tick.

**Q: True LRU vs approximate?**  
A: True LRU linked list expensive; sampling approximates with low overhead.

**Q: LFU vs LRU?**  
A: LFU better for looping scans that pollute LRU; LRU simpler for temporal locality.

**Q: Expired keys still in RDB?**  
A: Depends on save path—typically skip already expired; document behavior.

### 7.4 Persistence

**Q: AOF everysec vs always?**  
A: everysec ≈1s RPO, good latency; always ≈fsync per command, safer, slower.

**Q: Why fork for BGSAVE?**  
A: Point-in-time consistent snapshot via CoW without stopping the world (mostly).

**Q: What if fork fails / CoW blows memory?**  
A: Disable heavy saves under pressure; use replicas for backups; AOF rewrite caution; upgrade RAM.

**Q: AOF rewrite algorithm?**  
A: Child reads current dataset, writes compacted SET commands; parent buffers increments; concatenate & swap.

**Q: Is fsync on replica enough for durability?**  
A: Only if you WAIT for replicas + their fsync policy; default client OK ≠ durable.

### 7.5 Replication & HA

**Q: Full vs partial resync?**  
A: Partial if offsets in backlog; else full snapshot transfer.

**Q: How to avoid split brain?**  
A: Quorum election + config epoch; old primary demoted; clients use uptodate topology.

**Q: Can replicas take writes?**  
A: Not in primary-replica Redis model; use cluster shards for write scale.

**Q: READONLY on replica?**  
A: Stale reads OK for cache-aside; bad for read-your-writes unless routed to primary.

**Q: Diskless replication?**  
A: Stream snapshot over socket without writing RDB on primary disk—useful when disk slow.

### 7.6 Cluster

**Q: Why 16384 slots?**  
A: Fixed map size; gossip-friendly; balances granularity vs metadata.

**Q: Hash tags?**  
A: Force related keys to same slot for multi-key ops.

**Q: MOVED vs ASK?**  
A: MOVED updates client map; ASK is temporary during migration.

**Q: Cross-slot MGET?**  
A: Client scatters or proxy; not atomic.

**Q: Resharding impact?**  
A: Migrating slots add latency; throttle; avoid during peak if possible.

### 7.7 Transactions & Lua

**Q: Is MULTI ACID isolation?**  
A: Atomic execution vs other commands on node; not isolation like MVCC SQL; WATCH is optimistic.

**Q: Why Lua?**  
A: Server-side atomic custom ops; reduce RTT; must be deterministic for replication.

**Q: Lua and cluster?**  
A: All keys same slot; declare keys upfront.

### 7.8 Memory & performance

**Q: How to estimate memory for N keys?**  
A: Payload + per-key overhead + allocator frag + TTL structs + admin buffers.

**Q: Pipelining vs multiplexing?**  
A: Pipeline batches commands on one conn; both reduce RTT effects.

**Q: Huge client output buffer?**  
A: Slow consumer; limit and disconnect to protect server.

**Q: Hot key mitigation?**  
A: Local cache; key splitting; read replicas for read-heavy; application-level partitioning.

### 7.9 Comparison traps

**Q: Redis vs Memcached?**  
A: Redis richer types, persistence, replication; Memcached simpler multithreaded slab cache.

**Q: Redis vs RocksDB / KV on disk?**  
A: Different latency/durability class; Redis memory-first.

**Q: Why not make Redis always durable like Postgres?**  
A: Defeats low-latency mission; offer configurable RPO instead.

### 7.10 Extra interviewer traps (high value)

- What is your RPO with AOF everysec?  
- Does replica acknowledgement happen before client OK? (No, by default.)  
- What fences an old primary after failover?  
- Why is `KEYS *` dangerous?  
- How does CoW cause OOM during BGSAVE?  
- Eviction of a key with TTL—bug or OK?  
- How do you delete a 5GB hash safely?  
- What breaks MULTI across two slots?  
- How large a replication backlog do you need?  
- What’s the difference between logical OPS and network PPS?  
- How do you handle clock jumps for TTL? (use monotonic expire timestamps carefully; usually absolute unix time with caveats)  
- Can Pub/Sub replace Kafka? (No—not durable.)  
- How do you capacity-plan for fragmentation?  
- What metrics page you on at 3am?  
- When do you choose LFU over LRU?

---

## Appendix A — Command surface (MVP)

```text
SET/GET/DEL/EXISTS/EXPIRE/TTL/INCR
HSET/HGET/HGETALL
LPUSH/RPOP/LRANGE
SADD/SISMEMBER/SMEMBERS
ZADD/ZRANGE/ZRANK
MULTI/EXEC/WATCH/DISCARD
EVAL (Lua)
INFO / MEMORY / SCAN
REPLICAOF / PSYNC
CLUSTER KEYSLOT / NODES
```

## Appendix B — Config knobs

```text
maxmemory 64gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
save 900 1   # RDB conditions (if enabled)
repl-backlog-size 1gb
tcp-backlog 511
timeout 0
maxclients 50000
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Event loop, dict, TTL, LRU, AOF everysec |
| 10× | Replicas, quorum failover, pipelining standards |
| 100× | Hash-slot cluster, smart clients, reshard tooling |
| 1,000× | Cells/multi-cluster, AZ placement, hot-key ops |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| RESP | Redis Serialization Protocol style |
| RDB | Point-in-time snapshot |
| AOF | Append-only file of commands |
| CoW | Copy-on-write after fork |
| Hash slot | Cluster partition unit |
| Hash tag | Substring that determines slot |
| Partial resync | Replay from backlog without full snapshot |
| Epoch | Fencing generation for primaryship |
| Approximate LRU | Sample-based eviction |
| CROSSSLOT | Error for multi-key across slots |

## Appendix E — Estimation cheat-sheet

```text
Memory ≈ payload + (keys × per_key_overhead) × frag_factor × CoW_headroom

ops/s_node: often 100K–1M (payload & pipeline dependent)
cluster_ops ≈ sum over primaries (hot keys skew this)

AOF_MB/s ≈ write_ops × avg_cmd_size / 1e6

Replica amplification ≈ writes × number_of_replicas

RPO(everysec) ≈ 1s; RPO(always) ≈ 0; RPO(RDB-only) ≈ minutes

Never equate "has replica" with "durable"
```

---

*End of design doc. Open with §1 durability/HA goals; whiteboard §3.2 threading + §3.6 persistence + §3.7/3.8 HA/cluster; close with invariants §5.1 and traps §7.*
