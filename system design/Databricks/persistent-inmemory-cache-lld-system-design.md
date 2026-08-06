# LLD: Single-Node Persistent In-Memory Cache

> **Focus areas:** HashMap+LRU · Byte capacity · WAL · TTL · Eviction · Group commit · Crash recovery · Concurrency
> **Style:** LLD interview (clarify → APIs → classes → concurrency invariants → pseudocode → failure/recovery → race analysis → tests → Q&A)
> **Quality bar:** Explicit locks/linearization, WAL-before-publish ordering, runnable pseudocode, named race tests
> **Interview theme:** Databricks — signature cache+WAL LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Core Data Structures & WAL Format](#4-core-data-structures--wal-format)
5. [Concurrency Invariants & Lock Order](#5-concurrency-invariants--lock-order)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Race Scenario Analysis](#8-race-scenario-analysis)
9. [Tests & Edge Cases](#9-tests--edge-cases)
10. [Complexity & Performance Notes](#10-complexity--performance-notes)
11. [Interviewer Q&A (With Answers)](#11-interviewer-qa-with-answers)
12. [Appendices](#12-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design an **in-memory LRU cache** bounded by **total byte capacity** that **survives process crash** via a write-ahead log (WAL), supports optional TTL, and is safe under multi-threaded access.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Scope | Single-process cache + local WAL | Distributed Redis cluster |
| Capacity | Total bytes (weighted LRU) | Unlimited heap |
| Durability | ACKed puts/deletes durable across crash | Best-effort only |
| Eviction | LRU by recency (get + put refresh) | LFU/ARC unless extended |
| Databricks lens | Executor metadata cache, block cache segment | Full table format |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Operations? | `get`, `put`, `delete` | Core API surface |
| F2 | Capacity unit? | Max **bytes**, not entry count | Track per-entry size; weighted eviction |
| F3 | Eviction policy? | LRU | Doubly linked list + HashMap |
| F4 | Recency update? | Both get and put on hit refresh LRU | Move node to MRU on get |
| F5 | TTL? | Optional per put (`ttlMs`) | Lazy expire on access + periodic sweep |
| F6 | Durability scope? | ACK after WAL record durable per policy | WAL before in-memory publish |
| F7 | Log evictions? | **Yes** — EVICT records in WAL | Recovery must not resurrect evicted keys |
| F8 | Log deletes? | **Yes** — DELETE tombstones | Replay removes key |
| F9 | Concurrency? | Multi-threaded readers/writers | Single cache mutex MVP |
| F10 | Value type? | Opaque byte[] + size | No serialization framework in MVP |
| F11 | Sync mode? | Group commit OK (batch fsync) | Latency vs throughput knob |
| F12 | Recovery? | Replay WAL from checkpoint/snapshot | Block live traffic until replay done |
| F13 | Null keys/values? | Disallowed | Validate at API boundary |
| F14 | Stats? | hits, misses, evictions, bytes_used | Atomic counters |
| F15 | Scan/iterate? | Out of MVP | Would need snapshot iterator |

**MVP scope:**

1. Byte-capacity LRU with O(1) get/put/delete amortized.
2. WAL records: PUT, DELETE, EVICT with CRC + length framing.
3. Group-commit thread batches fsync; `put`/`delete` ACK after commit barrier.
4. Crash recovery replays WAL into empty map+LRU; truncate torn tail record.
5. Thread-safe via one `ReentrantReadWriteLock` or single `mutex` (pick one, document).
6. Optional TTL: store expiry epoch ms; lazy check on get; background sweeper.

**Out of MVP:** distributed replication, snapshot compaction worker, off-heap storage, scan API.

### 1.2 Non-functional requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | get latency (no fsync) | p99 < 1–5 µs in-proc (lock held briefly) |
| N2 | put latency (sync) | p99 bounded by group commit window (1–10 ms) |
| N3 | Durability | Zero loss of ACKed writes on single-node crash |
| N4 | Recovery time | O(WAL bytes) scan; acceptable for MB–GB logs |
| N5 | Memory | `used_bytes ≤ capacity` after each op completes |
| N6 | Correctness | Linearizable ops under documented lock |

### 1.3 Scope repeat-back

> Single-node persistent LRU cache: byte capacity, get/put/delete, optional TTL, WAL logs all mutating ops including evictions, group-commit fsync, crash recovery via replay, thread-safe with explicit lock order.

### 1.4 Core invariant card (write on board first)

```text
INV-1: used_bytes ≤ capacity_bytes at operation completion.
INV-2: HashMap keys == LRU list nodes (bijection while not expired/deleted).
INV-3: A client-visible ACK on put/delete implies WAL record is in committed prefix.
INV-4: After recovery, in-memory state == replay(WAL) with same capacity/TTL rules.
INV-5: EVICT in WAL ⇒ key absent after replay; DELETE ⇒ key absent; PUT ⇒ key present with value.
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class PersistentCache:
  static PersistentCache open(String walPath, CacheOptions opts) throws IOException
  Optional<byte[]> get(String key)
  void put(String key, byte[] value) throws IOException          // no TTL
  void put(String key, byte[] value, long ttlMs) throws IOException
  boolean delete(String key) throws IOException                   // false if absent
  CacheStats stats()
  void flush() throws IOException                                 // force group commit
  void close() throws IOException                                 // flush + stop threads

class CacheOptions:
  long capacityBytes = 64 * 1024 * 1024
  GroupCommitPolicy commitPolicy = GroupCommitPolicy(5ms, 64KB)
  boolean ttlEnabled = true
  long ttlSweepIntervalMs = 1000
  int maxKeyBytes = 4096
  int maxValueBytes = 4 * 1024 * 1024

class CacheStats:
  long hits, misses, evictions, puts, deletes
  long usedBytes, capacityBytes
  long walBytesAppended, lastCommitSeq
```

### 2.2 Semantics

| Operation | Behavior | Durability |
|-----------|----------|------------|
| `get(k)` | Return value if present and not expired; refresh LRU; no WAL | Not durable (read-only) |
| `put(k,v)` | Upsert; evict LRU until fits; WAL PUT (+ EVICT chain) | ACK after commit |
| `delete(k)` | Remove if present; WAL DELETE | ACK after commit |
| `flush()` | Force pending WAL batch fsync | Barrier |
| `close()` | flush, stop committer, fsync directory optional | Clean shutdown |

**Miss semantics:** absent key, expired key, or deleted key → `Optional.empty()`; count miss.

**Update semantics:** put on existing key replaces value bytes, adjusts `used_bytes` delta, refreshes LRU, one PUT record (value replacement logged).

### 2.3 Error model

| Exception | When |
|-----------|------|
| `IllegalArgumentException` | null key/value, oversize key/value, negative ttl |
| `IOException` | WAL append/fsync failure, disk full |
| `IllegalStateException` | ops after `close()` |

### 2.4 Guarantees table

| Property | Guarantee |
|----------|-----------|
| Capacity | Never exceeds `capacityBytes` after op completes |
| Durability | ACKed mutating op survives crash (committed WAL prefix) |
| LRU | Evicts least recently used among non-expired entries |
| Linearizability | All ops linearizable under single cache lock |
| Recovery | Reopen reproduces same logical keyset as committed WAL |
| TTL | Expired entries behave as absent; lazy + sweeper |

---

## 3. Class Diagrams & Responsibilities

### 3.1 Component diagram

```text
+------------------------------------------------------------------+
|                        PersistentCache                            |
|  get / put / delete / stats / flush / close                       |
+--------+-------------+-------------+--------------+-------------+
         |             |             |              |
         v             v             v              v
   +-----------+  +----------+  +-----------+  +--------------+
   | CacheCore |  | WalWriter|  | GroupComm |  | RecoveryEngine|
   | map+LRU   |  | append   |  | fsync thr |  | replay scan   |
   | TTL index |  | encode   |  | batch     |  | truncate tail |
   +-----------+  +----------+  +-----------+  +--------------+
         |
         v
   +-----------+
   | LRUList   |  doubly linked list of CacheNode
   +-----------+
```

### 3.2 Class responsibility table

| Class | Responsibility |
|-------|----------------|
| `PersistentCache` | Public API; orchestrates lock, WAL, recovery gate |
| `CacheCore` | HashMap + LRU + byte accounting + TTL checks |
| `CacheNode` | key, value[], valueBytes, expiryEpochMs (0=none), lruLinks |
| `LRUList` | MRU at head, LRU at tail; O(1) move/remove |
| `WalWriter` | Append framed records; assign monotonic seq |
| `WalRecordEncoder` | PUT/DELETE/EVICT/CHECKPOINT → bytes + CRC32 |
| `GroupCommitter` | Background: drain pending batch, fsync, bump watermark |
| `RecoveryEngine` | Scan WAL, apply to empty core, set replay watermark |
| `TtlSweeper` | Periodic: expire entries under lock, WAL EVICT each |
| `CacheStatsCollector` | Atomics for hits/misses (or under lock MVP) |

### 3.3 CacheNode fields

```text
class CacheNode:
  String key
  byte[] value
  int valueBytes          // cached len(value)
  long expiryEpochMs      // 0 means no TTL
  CacheNode prev, next    // LRU list links
  long lastWalSeq         // seq of last PUT affecting this key (debug)
```

### 3.4 Lock ownership

```text
PersistentCache:
  ReentrantReadWriteLock rwLock   // OR single ReentrantLock mutex (simpler MVP)
  WalWriter wal                   // has walMutex for buffer only
  GroupCommitter committer
  volatile RecoveryState state    // REPLAYING | LIVE
```

**MVP recommendation:** single `cacheMutex` for all map/LRU/TTL + synchronous WAL append under same lock (simplest linearization story). Group commit thread only fsyncs already-encoded buffer chunks — producer holds `cacheMutex` until record copied to commit queue.

---

## 4. Core Data Structures & WAL Format

### 4.1 LRU + map

```text
HashMap<String, CacheNode> index
LRUList lru                         // head=MRU, tail=LRU
long usedBytes                      // sum of valueBytes + key overhead policy
long capacityBytes
```

**Byte accounting policy (state explicitly):**

```text
entry_bytes = key.utf8.length + value.length + NODE_OVERHEAD (e.g. 48)
usedBytes += entry_bytes on insert
usedBytes -= old_entry_bytes on update/delete/evict
```

### 4.2 WAL record layout

```text
[ magic:4 'PCWL' ]
repeat until EOF:
  [ len:4 u32 BE ]          // payload length excluding CRC
  [ type:1 ]                // 1=PUT 2=DELETE 3=EVICT 4=CHECKPOINT
  [ seq:8 u64 BE ]          // monotonic per file
  [ payload: len-9 bytes ]
  [ crc32:4 ]               // CRC over type+seq+payload

PUT payload:
  [ keyLen:2 ][ keyBytes ][ valueLen:4 ][ valueBytes ][ ttlMs:8 i64, 0=none ]

DELETE payload:
  [ keyLen:2 ][ keyBytes ]

EVICT payload:
  [ keyLen:2 ][ keyBytes ]

CHECKPOINT payload:
  [ appliedSeq:8 ][ usedBytes:8 ][ entryCount:4 ]
```

**Why log EVICT:** if we only log PUT/DELETE, after crash an entry could reappear because recovery never saw its eviction (classic bug).

### 4.3 Group commit queue

```text
class CommitBatch:
  byte[] buffer
  long firstSeq, lastSeq
  CountDownLatch ackLatch       // producers await until fsync done

GroupCommitter loop:
  batch = drainPending(maxBytes, maxWaitMs)
  if batch empty: continue
  file.write(batch.buffer); file.fsync()
  committedSeq = batch.lastSeq
  batch.ackLatch.countDown()    // unblock waiting producers
```

### 4.4 TTL index (optional Phase-1.5)

```text
Min-heap keyed by expiryEpochMs → CacheNode*
On sweeper tick: while heap.min.expiry <= now: evict + WAL EVICT
On get hit: lazy delete if expired
```

---

## 5. Concurrency Invariants & Lock Order

### 5.1 Invariants (expanded)

| ID | Invariant |
|----|-----------|
| I1 | `usedBytes ≤ capacityBytes` after every completed `put`/`delete`/sweep |
| I2 | Every key in `index` appears exactly once in `lru` |
| I3 | No duplicate keys in `index` |
| I4 | `committedSeq` never decreases; ACK only after `seq ≤ committedSeq` |
| I5 | During `REPLAYING`, reject or block live mutating ops |
| I6 | WAL append order matches logical mutation order seen by single lock |
| I7 | EVICT records persisted before removing node from memory (WAL-first) |

### 5.2 Lock order (acyclic)

```text
Order (must never invert):
  L1: cacheMutex        — protects index, lru, usedBytes, stats hot path
  L2: walBufferMutex    — protects in-memory encode buffer (if split)
  L3: commitQueueMutex  — pending batches list

Allowed:
  cacheMutex → walBufferMutex → enqueue batch → wait on latch (release cacheMutex while waiting)

Forbidden:
  hold commitQueueMutex while acquiring cacheMutex
  hold walBufferMutex while waiting on cacheMutex in opposite order
```

**Simpler MVP (recommended on whiteboard):** one `cacheMutex`; WAL encode + enqueue synchronous; producer waits on latch **without** holding mutex if latch wait is outside lock:

```text
put():
  lock(cacheMutex)
  plan mutations + encode to localBytes
  unlock(cacheMutex)
  committer.submit(localBytes)   // may block until fsync
  lock(cacheMutex)
  apply mutations to map/LRU
  unlock(cacheMutex)
```

This is **WAL-before-publish** — durable before visible. Interviewer gold.

### 5.3 Read/write policy

| Approach | get | put/delete | Notes |
|----------|-----|------------|-------|
| Single mutex | lock | lock | Simplest story |
| RW lock | shared lock + LRU move | exclusive | LRU move on get needs write lock in strict LRU |
| Striped locks | per-bucket | per-bucket | Hard with global byte capacity |

**Say:** MVP uses one mutex; mention striped/sharded as 10× optimization.

### 5.4 Recovery gate

```text
enum RecoveryState { REPLAYING, LIVE, CLOSED }

open():
  state = REPLAYING
  RecoveryEngine.replay(walPath) → builds shadow CacheCore OR applies to live core
  state = LIVE
  start GroupCommitter + TtlSweeper

put/delete while REPLAYING:
  throw IllegalStateException OR block until LIVE (pick throw for tests)
```

---

## 6. Algorithms & Pseudocode

### 6.1 put(key, value, ttlMs)

```text
function put(key, value, ttlMs):
  require state == LIVE
  validate key, value non-null; within size limits
  entryBytes = byteCost(key, value)

  lock(cacheMutex)
  old = index.get(key)
  deltaBytes = entryBytes - (old ? byteCost(old) : 0)
  evictions = planEvictions(deltaBytes)     // list of keys to evict, LRU order
  recBytes = encodePut(key, value, ttlMs)
  for evKey in evictions:
    recBytes += encodeEvict(evKey)
  unlock(cacheMutex)

  committer.appendAndAwaitFsync(recBytes)   // durable barrier

  lock(cacheMutex)
  for evKey in evictions:
    removeNodeLocked(evKey)                 // memory only; WAL already has EVICT
  if old != null:
    updateNodeLocked(old, value, ttlMs)
    lru.moveToHead(old)
  else:
    node = newNode(key, value, ttlMs)
    index.put(key, node); lru.addHead(node); usedBytes += entryBytes
  stats.puts++
  unlock(cacheMutex)
```

### 6.2 planEvictions (locked)

```text
function planEvictions(deltaBytes):
  evictKeys = []
  projected = usedBytes + deltaBytes
  while projected > capacityBytes and lru.tail != null:
    tail = lru.tail
    evictKeys.add(tail.key)
    projected -= byteCost(tail)
  return evictKeys
```

### 6.3 get(key)

```text
function get(key):
  require state == LIVE
  lock(cacheMutex)
  node = index.get(key)
  if node == null:
    stats.misses++; unlock(); return None
  if ttlEnabled and node.expiryEpochMs > 0 and now() >= node.expiryEpochMs:
    // lazy expiry — treat as miss but optionally sync EVICT
    scheduleOrInlineExpire(node)            // MVP: inline expire+WAL under lock OR async
    stats.misses++; unlock(); return None
  lru.moveToHead(node)
  stats.hits++
  unlock()
  return Some(copy(node.value))             // defensive copy optional
```

**Lazy expire durability choice:**

- **Strict:** expire path also WAL EVICT + fsync (slow on hot read path).
- **Pragmatic:** memory-only remove on get; sweeper WAL EVICT; risk: crash before log → zombie entry returns. **Interview:** pick strict for durable TTL removal, or accept bounded staleness.

### 6.4 delete(key)

```text
function delete(key):
  lock(cacheMutex)
  node = index.get(key)
  if node == null: unlock(); return false
  rec = encodeDelete(key)
  unlock()

  committer.appendAndAwaitFsync(rec)

  lock(cacheMutex)
  removeNodeLocked(key)
  stats.deletes++
  unlock()
  return true
```

### 6.5 removeNodeLocked

```text
function removeNodeLocked(key):
  node = index.remove(key)
  if node == null: return
  lru.remove(node)
  usedBytes -= byteCost(node)
```

### 6.6 evictOneLocked (used by sweeper)

```text
function evictOneLocked(node):
  rec = encodeEvict(node.key)
  unlock(cacheMutex)
  committer.appendAndAwaitFsync(rec)
  lock(cacheMutex)
  removeNodeLocked(node.key)
  stats.evictions++
```

### 6.7 GroupCommitter thread

```text
function committerLoop():
  while running:
    batch = waitForBatch(maxWaitMs, maxBatchBytes)
    if batch == null: continue
    try:
      walFile.write(batch.bytes)
      walFile.fsync()
      committedSeq = batch.lastSeq
      for latch in batch.producerLatches: latch.countDown()
    catch IOException:
      markCacheReadOnly(); propagate error
```

### 6.8 Recovery replay

```text
function recover(walPath, core):
  seq = 0
  for record in scanRecords(walPath):
    if not verifyCrc(record): truncateFileAt(record.offset); break
    seq = record.seq
    switch record.type:
      case PUT:
        core.applyPutReplay(record.key, record.value, record.ttlMs)
      case DELETE:
        core.removeIfPresent(record.key)
      case EVICT:
        core.removeIfPresent(record.key)
      case CHECKPOINT:
        // optional fast-path validation only
  core.rebuildLruFromMapPolicy()    // if replay didn't maintain LRU order, rebuild MRU arbitrary
  return seq
```

**LRU on replay:** WAL total order defines insertion sequence; for LRU fidelity, either log LRU touches (not done) or accept that recovered LRU order is **put-order approx** — say aloud: recency metadata not fully durable unless GETs logged (usually not).

### 6.9 open() lifecycle

```text
function open(walPath, opts):
  cache = new PersistentCache(opts)
  cache.state = REPLAYING
  cache.committer = startCommitter(walPath)
  lastSeq = recover(walPath, cache.core)
  cache.nextSeq = lastSeq + 1
  cache.state = LIVE
  cache.sweeper = startTtlSweeper(cache)
  return cache
```

---

## 7. Failure Modes & Recovery

### 7.1 Crash-point matrix

| Crash point | On disk | In memory | After restart |
|-------------|---------|-----------|---------------|
| A: before WAL append | old record | old | unchanged |
| B: WAL buffered, not fsync | maybe partial record | old | truncate torn tail |
| C: after fsync, before apply | new record durable | old | replay applies new |
| D: mid-eviction chain fsync | partial chain | old | replay completes evictions |
| E: after apply, before ACK | durable | new | replay idempotent apply |
| F: during recovery | WAL intact | partial replay | restart recovery from scratch |

### 7.2 Torn WAL tail

```text
scan until CRC fail or EOF mid-record
truncate file to last valid record end
continue replay
```

### 7.3 Disk full on append

```text
append fails → do NOT apply memory mutation → return IOException to client
cache may enter read-only mode if policy says so
```

### 7.4 Duplicate replay idempotency

```text
PUT replay: upsert value (same result)
DELETE/EVICT replay: remove if present (same result)
Multiple identical PUTs: last wins — acceptable
```

### 7.5 Recovery vs live traffic

**Rule:** `state != LIVE` rejects mutators; readers optional (return empty during replay).

```text
// BAD: accept puts during replay → diverge from WAL order
// GOOD: gate until replay completes; or single-threaded open before serving
```

### 7.6 Checkpoint (optional acceleration)

Periodic CHECKPOINT record + optional snapshot file of map (Phase 2). MVP: WAL-only replay OK for interview.

---

## 8. Race Scenario Analysis

### 8.1 get vs put (same key)

| Timeline | Thread G (get) | Thread P (put) | Outcome |
|----------|----------------|----------------|---------|
| 1 | lock; read v1 | blocked | G returns v1 |
| 2 | unlock | lock; WAL; apply v2 | linear order G before P |
| 3 | lock; miss | lock; apply v2 | G sees v2 or miss then P completes |

**Invariant:** linearizable under `cacheMutex` + WAL-before-publish.

**Test:** `test_get_put_same_key_linearizable`

### 8.2 put vs eviction (capacity full)

| Timeline | Thread P1 (put big) | Thread P2 (put other) |
|----------|----------------------|------------------------|
| 1 | plan evict key X | blocked |
| 2 | WAL PUT+EVICT(X) fsync | blocked |
| 3 | apply; X gone | lock; plan own evictions |

**Bug if:** P1 evicts X in memory before WAL EVICT fsync → crash resurrects X while Y also present → over capacity.

**Fix:** WAL-before-publish for eviction chain.

**Test:** `test_put_eviction_wal_before_memory`

### 8.3 concurrent puts same key

| Timeline | P1 put(k,v1) | P2 put(k,v2) |
|----------|--------------|--------------|
| 1 | encode; fsync seq=10 | blocked |
| 2 | apply v1 | encode; fsync seq=11 |
| 3 | | apply v2 |

**Result:** v2 wins; both WAL records present; replay last PUT wins.

**Alternate interleaving:** both plan under lock sequentially — no lost update.

**Test:** `test_concurrent_put_same_key_last_writer_wins`

### 8.4 recovery vs live traffic

| Timeline | Recovery | Client put |
|----------|----------|------------|
| 1 | replay half | put accepted? |
| **Bad** | | put interleaves → map diverges from WAL |
| **Good** | REPLAYING blocks puts | |

**Test:** `test_put_rejected_during_recovery`

### 8.5 get refreshes LRU while evictor runs

Single mutex serializes — get moves node to head before evictor reads tail — no race.

**Test:** `test_get_moves_mru_before_concurrent_put_evicts`

### 8.6 group commit batch interleaving

Two puts enqueue records; one fsync batch — both must ACK only after fsync; neither visible until respective apply phase after latch.

**Test:** `test_group_commit_batch_ack_after_fsync`

---

## 9. Tests & Edge Cases

### 9.1 Functional tests

| Test name | Setup | Assert |
|-----------|-------|--------|
| `test_put_get_hit` | put k1 | get returns v1 |
| `test_get_miss_unknown` | empty | miss |
| `test_delete_then_miss` | delete k | get miss |
| `test_update_existing_increases_bytes` | larger value | usedBytes correct |
| `test_capacity_one_overwrite` | cap fits 1 entry | second put evicts first |

### 9.2 Eviction tests

| Test name | Setup | Assert |
|-----------|-------|--------|
| `test_lru_evicts_tail` | fill A,B; get A; put C | B evicted |
| `test_eviction_logged_in_wal` | parse WAL | EVICT record present |
| `test_recovery_respects_evict` | put→evict→crash→open | evicted key absent |

### 9.3 Durability tests

| Test name | Setup | Assert |
|-----------|-------|--------|
| `test_crash_after_fsync_before_apply` | inject crash hook | replay shows key |
| `test_crash_before_fsync_no_apply` | fail before apply | key absent after reopen |
| `test_torn_tail_truncated` | corrupt last byte | recovery succeeds |

### 9.4 Concurrency tests

| Test name | Setup | Assert |
|-----------|-------|--------|
| `test_stress_mixed_get_put` | N threads, 10s | invariants I1–I3 |
| `test_concurrent_put_same_key_last_writer_wins` | 2 threads | final value consistent |
| `test_no_used_bytes_drift` | random ops | usedBytes == sum(entries) |

### 9.5 TTL tests

| Test name | Setup | Assert |
|-----------|-------|--------|
| `test_ttl_expired_get_miss` | ttl=1ms | after sleep miss |
| `test_sweeper_removes_expired` | no access | key gone + WAL EVICT |

### 9.6 Edge cases checklist

- Empty value byte[] allowed? **Yes** if spec allows zero-length values.
- Key exactly at maxKeyBytes — accept; maxKeyBytes+1 — reject.
- Put same value as existing — still WAL PUT (durability refresh) or skip if equal? **Log** for simplicity.
- capacityBytes = 0 — reject at open or all puts fail evict loop — **reject at open**.
- Huge single value > capacity — reject put upfront.
- Recovery with duplicate DELETE — idempotent OK.

---

## 10. Complexity & Performance Notes

### 10.1 Time complexity

| Operation | Time | Notes |
|-----------|------|-------|
| get | O(1) avg | HashMap + list splice |
| put | O(1 + E) | E = evictions needed; rare amortized small |
| delete | O(1) | |
| evict one | O(1) | |
| recovery | O(R) | R = WAL records |
| TTL sweep | O(k log n) | k expired; heap |

### 10.2 Space

```text
O(number of entries) for map + list nodes + value bytes
WAL disk: sum of record sizes (unbounded unless compaction)
```

### 10.3 fsync bottleneck

Group commit amortizes fsync — throughput ↑, p99 put latency ↑ slightly.

```text
sync_put_qps ≈ 1 / (group_commit_window + fsync_cost)
async batch 64KB ~ 1 fsync per 64KB
```

### 10.4 When single mutex hurts

Many reader threads + strict LRU (get takes write lock) → consider approximate LRU or per-node seq counters (Phase 2).

---

## 11. Interviewer Q&A (With Answers)

| # | Question | Strong answer |
|---|----------|---------------|
| Q1 | Why WAL-before-publish? | If memory updated first and crash before log, data is lost while client might have been told success — violates durability. |
| Q2 | Why log EVICT? | Otherwise after crash replay replays PUTs but not evictions → over capacity / resurrected keys. |
| Q3 | Do GETs go to WAL? | Usually no — recency not durable; accept approximate LRU after recovery or add optional touch log. |
| Q4 | Group commit vs per-op fsync? | Group commit batches fsync for throughput; ACK waits on batch latch — still durable when fsync completes. |
| Q5 | How handle concurrent puts on same key? | Serialize under mutex; WAL total order; last apply wins; replay consistent. |
| Q6 | Read-write lock for gets? | Strict LRU needs move-to-head on get → write lock anyway; RW lock doesn't help much. |
| Q7 | Byte capacity vs entry count? | Byte capacity matches memory pressure; requires planEvictions by byte delta. |
| Q8 | Snapshot + WAL? | Snapshot for fast recovery; WAL for incremental — checkpoint record marks applied seq. |
| Q9 | Compare to Redis AOF? | Same idea: log mutating ops; we add EVICT + byte LRU semantics. |
| Q10 | Idempotent client retries? | Without idempotency keys duplicate PUTs replay fine; use client token in WAL for exactly-once Phase 2. |
| Q11 | fsync policy on directory? | `open(walDir)` fsync after create for crash-safe file creation — mention if asked. |
| Q12 | CRC scope? | CRC over type+seq+payload detects torn writes. |
| Q13 | Memory fragmentation? | byte[] churn; pool buffers Phase 2; off-heap DirectByteBuffer Phase 3. |
| Q14 | TTL lazy vs proactive? | Lazy on get cheap; sweeper prevents unbounded dead keys occupying capacity. |
| Q15 | Can get block on fsync? | Not in MVP — get doesn't WAL; optional strict expire may — call out trade-off. |

**Common traps**

| Trap | Wrong | Right |
|------|-------|-------|
| Update map before WAL | crash loses data | WAL fsync then apply |
| Skip EVICT log | overfill after recovery | log every eviction |
| get without lock | torn LRU | hold mutex |
| ACK before fsync | false durability | await commit latch |

---

## 12. Appendices

### A. Options defaults (interview)

```text
capacityBytes     = 64 MiB
groupCommitMaxMs  = 5
groupCommitMaxBytes = 65536
maxKeyBytes       = 4096
maxValueBytes     = 4 MiB
ttlSweepIntervalMs = 1000
walFileName       = "cache.wal"
```

### B. Metrics

```text
cache_hits_total
cache_misses_total
cache_puts_total
cache_deletes_total
cache_evictions_total
cache_used_bytes
cache_commit_latency_ms{quantile}
cache_recovery_seconds
cache_wal_bytes_total
```

### C. Minimal Java-like sketch

```text
class PersistentCache {
  final ReentrantLock lock = new ReentrantLock();
  final Map<String, Node> map = new HashMap<>();
  final DoublyLinkedList lru = new DoublyLinkedList();
  final WalWriter wal;
  final GroupCommitter committer;
  long usedBytes;
  volatile State state = REPLAYING;

  Optional<byte[]> get(String k) { lock.lock(); try { ... } finally { lock.unlock(); } }
  void put(String k, byte[] v) throws IOException { /* WAL-before-publish */ }
}
```

### D. Related docs

| Doc | Relationship |
|-----|--------------|
| `durable-event-writer-lld-system-design.md` | WAL framing + group commit patterns |
| `durable-embedded-kv-store-lld-system-design.md` | Persistent KV without LRU eviction |
| `buffered-writer-lld-system-design.md` | Buffered append path |

### E. Whiteboard timing (45 min)

5 clarify · 8 API/classes · 12 pseudocode+WAL order · 8 races · 5 recovery · 5 tests · 7 Q&A

### F. Glossary

| Term | Meaning |
|------|---------|
| WAL-before-publish | Durable log record committed before in-memory visibility |
| Group commit | Batch multiple records under one fsync |
| Watermark | `committedSeq` — records ≤ watermark durable |
| Tombstone | DELETE record removing key on replay |
| Lazy expiry | Check TTL only on access |

---

*End of LLD prep.*
