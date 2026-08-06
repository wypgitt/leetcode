#!/usr/bin/env python3
"""Generate priority Databricks system design docs (skip if exist)."""
from pathlib import Path
from _gen_helpers import APPENDIX_X, OUT, write

TAIL_HLD = (OUT / "_TAIL_HLD.md").read_text()

def hld_header(title, focus, theme):
    return f"""# System Design: {title}

> **Focus areas:** {focus}
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, honest MVP vs extreme-scale paths, failure-first reasoning
> **Interview theme:** Databricks — {theme}

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

"""

def lld_header(title, focus, theme):
    return f"""# LLD: {title}

> **Focus areas:** {focus}
> **Style:** LLD interview (clarify → complexity → classes → algorithms/pseudocode → concurrency → failure modes → tests → Q&A)
> **Quality bar:** Explicit invariants, lock ordering, no hand-wavy concurrency, runnable pseudocode
> **Interview theme:** Databricks — {theme}

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Data Structures & On-Disk Layout](#4-data-structures--on-disk-layout)
5. [Concurrency Invariants](#5-concurrency-invariants)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Tests & Edge Cases](#8-tests--edge-cases)
9. [Scalability Notes (Single-Node / Library Scope)](#9-scalability-notes-single-node--library-scope)
10. [Wrap-Up](#10-wrap-up)
11. [Deeper / Related Interview Questions](#11-deeper--related-interview-questions)
12. [Appendices](#12-appendices)

---

"""

def gen_if_missing(name, body):
    path = OUT / name
    if path.exists():
        n = path.read_text().count("\n")
        print(f"SKIP {name}: {n} lines (exists)")
        return n
    return write(name, body)

# ── persistent-inmemory-cache LLD ────────────────────────────────────────────

def persistent_cache_lld():
    return lld_header(
        "Persistent Concurrent In-Memory Cache with LRU Eviction",
        "LRU · TTL · WAL snapshot · Concurrent get/put · Eviction under load · Crash recovery · Striped locks",
        "signature storage/concurrency LLD — cache that survives restarts",
    ) + r"""
## 1. Clarify Requirements (Interview Q&A)

Goal: design a **thread-safe in-memory cache** with LRU eviction, optional TTL, and **persistence** so a process restart can reload hot entries without cold-starting every dependency.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Scope | Single process library | Distributed Redis cluster |
| API | get/put/delete + TTL | SQL queries |
| Durability | Best-effort snapshot + WAL for hot set | Every read durable |
| Databricks lens | Executor-side metadata cache, block cache | Full RocksDB |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Distributed or local? | **Local in-process** | No Raft |
| F2 | Key/value types? | String/bytes; bounded value size | Length-prefixed records |
| F3 | Eviction? | **LRU by entry count or bytes** | Doubly-linked list + hash map |
| F4 | TTL? | Per-key optional expiry | Lazy + proactive sweep |
| F5 | Persistence? | Periodic snapshot + append WAL for mutations | Recovery on open |
| F6 | Concurrency? | Many reader threads + writers | RW locks or striping |
| F7 | Max capacity? | N entries or B bytes | Evict on insert |
| F8 | Crash model? | Process crash; disk may tear last record | Checksum + truncate |
| F9 | Negative cache? | Optional | Tombstone entries |
| F10 | Metrics? | hit/miss/eviction/latency | Required |
| F11 | Write-through? | No external store MVP | Cache-only |
| F12 | CAS/version? | Optional compare-and-swap | Version field per entry |

**MVP scope:**

1. `get` / `put` / `delete` with LRU eviction by bytes budget.  
2. Optional per-key TTL with lazy expiration on read + background sweeper.  
3. Append-only WAL for puts/deletes; periodic snapshot of live entries.  
4. Thread-safe with documented lock ordering.  
5. Recovery: replay WAL after loading latest snapshot.  
6. Stats: hits, misses, evictions, current bytes.

**Out of MVP:** distributed invalidation, encryption, multi-key transactions.

### 1.2 Scope repeat-back

> Single-node concurrent LRU cache with byte budget and optional TTL, persisted via snapshot + WAL for fast warm restart—thread-safe with explicit eviction and recovery semantics.

### 1.3 Durability contract

```text
put returns ⇒ entry visible to subsequent gets in this process (linearizable per key)
put returns ⇒ WAL record durable per SyncPolicy (EVERY_WRITE or GROUP_COMMIT)
Snapshot is a checkpoint; WAL entries after snapshot replay on startup
Evicted entries may disappear from memory but tombstone in WAL prevents resurrection of stale snapshot rows
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class PersistentCache:
  open(path, Options) -> PersistentCache
  get(key: Bytes) -> Optional[Bytes]
  put(key: Bytes, value: Bytes, ttl_ms: Optional[int]) -> void
  delete(key: Bytes) -> void
  compare_and_swap(key, expected_ver, new_value) -> bool   # optional
  flush() -> void          # fsync WAL + optional snapshot
  stats() -> CacheStats
  close() -> void
```

### 2.2 Guarantees

| Property | Guarantee |
|----------|-----------|
| Per-key linearizability | Yes for get/put/delete on same key |
| LRU correctness | Evicted key absent until re-inserted |
| TTL | Expired keys behave as miss (lazy); sweeper bounds memory |
| Durability | Configurable: ACK after WAL durable (recommended) |
| Max size | Hard cap; put may evict multiple entries |
| Iteration | Not required MVP |

### 2.3 Error model

```text
InvalidArgument  — empty key, oversize value
CapacityError    — cannot evict enough (if pinned entries — N/A MVP)
IOError          — disk full
ClosedError      — after close()
CasFailed        — version mismatch
```

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Responsibility |
|-------|----------------|
| `PersistentCache` | Facade; coordinates cache + persistence |
| `LruCache` | In-memory hash map + LRU list |
| `CacheEntry` | key, value, expiry, version, list node |
| `Wal` | Append PUT/DEL/TTL records; fsync policy |
| `SnapshotWriter` | Serialize live entries to snapshot file |
| `SnapshotLoader` | Load snapshot into LruCache |
| `Recovery` | Find latest snapshot + replay WAL |
| `EvictionPolicy` | LRU by bytes (default) |
| `TtlSweeper` | Background thread removes expired |
| `LockTable` | Striped RW locks per key hash bucket |
| `Metrics` | hits, misses, evictions, wal latency |

### 3.2 ASCII class diagram

```text
+-------------------+
| PersistentCache   |
+---------+---------+
          |
    +-----+-----+------------+
    |           |            |
+---v---+   +---v---+    +---v---+
|LruCache|  |  Wal  |    |Recovery|
+---+---+--+  +---+---+    +-------+
    |   |
+---v---v---+
| CacheEntry |
+------------+
```

### 3.3 Lock hierarchy (critical for interview)

```text
Order (always acquire ascending):
  1. global_metadata_mutex   (snapshot, stats, open/close)
  2. bucket_lock[i]          (per stripe for key ops)
  3. lru_list_mutex          (structural changes to LRU links)
  4. wal_mutex               (single writer to WAL)

Rule: never hold wal_mutex while waiting on bucket_lock
Rule: promote to write lock only when mutating entry or LRU position
```

---

## 4. Data Structures & On-Disk Layout

### 4.1 In-memory structures

```text
HashMap<key_hash, CacheEntry*>
DoublyLinkedList LRU ordered by recency (head = MRU, tail = LRU)

CacheEntry:
  key: Bytes
  value: Bytes
  expiry_unix_ms: Optional
  version: uint64
  byte_size: int   # key+value+overhead
  lru_node: ListNode
```

### 4.2 WAL record format

```text
[WALRecord]
  magic: u32
  crc32: u32
  seq: u64
  op: u8   # PUT=1, DEL=2, CLEAR=3
  key_len: u32
  key: bytes
  value_len: u32   # 0 for DEL
  value: bytes
  ttl_ms: u64      # 0 = none
  padding to 8-byte align
```

### 4.3 Snapshot format

```text
[SnapshotHeader] version, entry_count, total_bytes, created_seq
repeat entry_count:
  [EntryRecord] key_len, key, value_len, value, expiry, version
[SnapshotFooter] crc32 of body
```

### 4.4 File layout

```text
data_dir/
  wal.log
  wal.log.old
  snapshot-000042.bin
  snapshot-000043.bin
  MANIFEST  -> points to latest snapshot seq + wal offset
```

---

## 5. Concurrency Invariants

### 5.1 Invariants (always true)

1. Sum of `entry.byte_size` ≤ `max_bytes` (after any op completes).  
2. LRU list contains exactly the keys in the hash map.  
3. An expired entry is indistinguishable from miss on `get` (may linger until sweep).  
4. WAL `seq` strictly increases; each mutation has one WAL record before visibility (if sync-on-write).  
5. No lock inversion: bucket → lru → wal ordering.

### 5.2 Read path concurrency

```text
get(key):
  bucket = stripe(key)
  bucket.rlock()
  entry = map.get(key)
  if entry expired: bucket.runlock(); return miss
  if entry: promote LRU (needs upgrade to wlock on lru_list only — use per-entry seqlock or combine locks)
  bucket.runlock()
  return entry.value
```

**Interview simplification:** single `cache_mutex` RWLock for MVP; optimize to striping when asked.

### 5.3 Write path concurrency

```text
put(key, value):
  wal.append(PUT) ; wal.sync()        # durability barrier
  bucket.wlock()
  upsert entry; adjust bytes
  while bytes > max: evict_lru_tail()
  promote_to_mru(entry)
  bucket.wunlock()
```

### 5.4 Eviction vs concurrent get

Eviction removes tail under `lru_list_mutex` + bucket lock for victim key.  
Get on victim: either sees entry (before eviction) or miss (after)—no torn reads if values immutable.

---

## 6. Algorithms & Pseudocode

### 6.1 put with LRU eviction

```text
function put(key, value, ttl_ms):
  size = sizeof(key) + sizeof(value) + overhead
  if size > max_bytes: raise InvalidArgument

  rec = WalRecord(PUT, key, value, ttl_ms, seq=next_seq())
  wal.append(rec)
  wal.sync()                    # EVERY_WRITE policy

  lock bucket(key)
  entry = map.get(key)
  if entry:
    total_bytes -= entry.byte_size
    entry.value = value
    entry.expiry = now + ttl_ms
    entry.version++
  else:
    entry = new CacheEntry(key, value, ttl_ms)
    map[key] = entry
  total_bytes += entry.byte_size
  move_to_mru(entry)

  while total_bytes > max_bytes:
    victim = lru_tail()
    remove(victim)              # also append DEL to WAL optional batched
    wal.append(DEL, victim.key)
  unlock bucket(key)
  wal.sync()                    # if evictions must survive crash
```

### 6.2 get with TTL lazy expire

```text
function get(key):
  lock bucket(key) for read
  entry = map.get(key)
  if entry is null:
    stats.miss++; return null
  if entry.expiry != null and now > entry.expiry:
    upgrade to write
    remove(entry)               # lazy delete
    wal.append(DEL, key)        # optional async batch
    stats.miss++; return null
  move_to_mru(entry)
  stats.hit++
  return entry.value
```

### 6.3 Snapshot + WAL truncation

```text
function checkpoint():
  lock global_metadata
  snap_seq = wal.current_seq()
  entries = snapshot_live_map_copy()   # brief pause or copy-on-write
  write snapshot file snap_seq
  manifest = {snapshot: snap_seq, wal_offset: wal.size()}
  atomic_rename(manifest)
  wal.rotate()                         # new wal.log
  unlock global_metadata

background every T minutes or when wal > 64MB
```

### 6.4 Recovery

```text
function recover(path):
  manifest = read_manifest()
  cache = empty
  if manifest.snapshot:
    cache.load(manifest.snapshot)
  for rec in wal.from(manifest.wal_offset):
    if rec.crc bad: stop at last good
    apply(rec, cache)           # PUT upsert; DEL remove
  return cache
```

### 6.5 TTL sweeper

```text
function sweeper_loop(interval):
  while running:
    sleep(interval)
    now = clock()
    for entry in map.snapshot():   # avoid long hold
      if entry.expiry and now > entry.expiry:
        lock bucket(entry.key)
        if still expired: remove(entry)
        unlock
```

---

## 7. Failure Modes & Recovery

| Failure | Behavior |
|---------|----------|
| Crash after WAL append, before mem update | Recovery replays PUT/DEL |
| Crash after mem update, before WAL | If sync-before-mem: not possible; if wrong order: **bug** — always WAL first |
| Torn WAL record | CRC fail → truncate to last complete |
| Snapshot corrupt | Fall back to previous snapshot + longer WAL replay |
| Disk full on WAL | put returns IOError; cache unchanged |
| Eviction during recovery replay | Byte budget re-applied after full replay |
| Clock jump breaks TTL | Use monotonic for relative TTL; wall clock documented |

**Deal-breaker:** Update memory before durable WAL without stating data-loss window.

---

## 8. Tests & Edge Cases

### 8.1 Unit tests

1. Put/get/delete basic; miss on unknown key.  
2. LRU: insert A,B,C over capacity 2 → A evicted.  
3. Get promotes to MRU; changes eviction order.  
4. TTL expires → get miss.  
5. Concurrent puts same key → last writer wins; no corruption.  
6. Concurrent get/put stress (threads=32, ops=1M).  
7. Recovery: put 100 keys, kill, reopen → all present.  
8. Recovery with evictions in WAL → correct final set.  
9. Oversize value rejected.  
10. CAS success/failure paths.

### 8.2 Property tests

- Byte invariant after random op sequences.  
- Recovery ∘ (ops) ≡ in-memory state at checkpoint seq.

### 8.3 Crash injection

- Kill after WAL write, before mem (should appear after restart).  
- Kill mid-snapshot (ignore partial snapshot).

---

## 9. Scalability Notes (Single-Node / Library Scope)

| Concern | Approach |
|---------|----------|
| Lock contention | Sharded buckets (256+ stripes) |
| WAL throughput | Group commit batch ≤5ms |
| Snapshot pause | Copy map under RCU or double-buffer |
| Large values | Cap value size; count bytes not entries |
| Many TTL keys | Heap of expiry + sweeper |

At **100×** QPS within one JVM/process: striping + group commit.  
Not sharding across nodes—that is a different problem (distributed cache).

---

## 10. Wrap-Up

**Summary:** Hash map + doubly-linked LRU for O(1) get/put/evict; WAL-before-mutation for durability; snapshot for bounded recovery time; striped locks for concurrency; TTL via lazy delete + sweeper.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Single RW lock acceptable | Striped locks |
| EVERY_WRITE fsync | Group commit |
| Full snapshot | Incremental + compaction |
| No compression | Value compression |

**Top risks:** wrong lock order; mem-before-WAL; LRU bugs on promote/evict; recovery applying stale snapshot over newer WAL incorrectly.

---

## 11. Deeper / Related Interview Questions

1. Why doubly-linked list vs heap for LRU?  
2. How does group commit change ACK semantics?  
3. Compare to Caffeine/Guava cache + separate persistence.  
4. How to make snapshot without stopping writers?  
5. W-TinyLFU vs LRU for skewed workloads?  
6. How would you add distributed invalidation pub/sub?  
7. Memory overhead per entry?  
8. How to detect and repair LRU list corruption?  
9. Relationship to `durable-embedded-kv-store` doc?  
10. Negative caching and thundering herd on miss?

**Interviewer traps**

| Trap | Answer |
|------|--------|
| "Use std::list::splice" | OK in C++; still explain invariants |
| "Skip WAL, snapshot only" | State RPO window |
| "Global mutex is fine" | OK for MVP; name striping path |
| "TTL only on read" | Sweeper needed for cold keys |

---

## 12. Appendices

### A. Pseudocode — striped get/put

```text
class StripedCache:
  buckets = array[256] of {map, rwlock}

  function stripe(key): return hash(key) % 256

  function get(key):
    b = buckets[stripe(key)]
    b.rlock()
    try: return b.map.get(key)?.value
    finally: b.runlock()
```

### B. Metrics

```text
cache_hits_total
cache_misses_total
cache_evictions_total
cache_bytes_current
wal_append_latency_ms
snapshot_duration_ms
recovery_duration_ms
```

### C. Complexity

```text
get/put/delete amortized O(1)
evict while loop: O(k) evictions
recovery O(wal_records + snapshot_entries)
snapshot O(n log n) if sorting; O(n) if streaming map
```

### D. Related Databricks docs

- `durable-embedded-kv-store-lld-system-design.md` — full LSM/WAL depth  
- `ranged-file-cache-lld-system-design.md` — byte-range coalescing  
- `mpmc-queue-lld-system-design.md` — background flush workers  

""" + APPENDIX_X + "\n\n*End of persistent in-memory cache LLD prep.*\n"


# ── mpmc-queue LLD ───────────────────────────────────────────────────────────

def mpmc_queue_lld():
    return lld_header(
        "Thread-Safe Bounded MPMC Queue with Timeouts and Fairness",
        "MPMC · Bounded buffer · Condition variables · Backpressure · Timed offer/poll · Shutdown · Lock ordering",
        "classic concurrency LLD — bounded queue used in schedulers and pipelines",
    ) + r"""
## 1. Clarify Requirements (Interview Q&A)

Goal: implement a **bounded multi-producer multi-consumer queue** supporting blocking, timed, and non-blocking `offer`/`poll`, with clean shutdown and no lost wakeups.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Scope | In-process library | Distributed Kafka |
| Pattern | MPMC bounded ring buffer | Unbounded linked queue only |
| Fairness | FIFO global order | Strict per-producer fairness (optional) |
| Databricks lens | Executor task queues, pipeline buffers | Full Disruptor clone |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | MPMC or SPSC? | **MPMC** | Need mutex or CAS ring |
| F2 | Bounded? | **Yes** capacity N | Backpressure |
| F3 | Blocking API? | offer/poll + timeout | condition vars |
| F4 | Element type? | Generic T | std::optional or pointer |
| F5 | Shutdown? | close() wakes waiters | poison pill or flag |
| F6 | Fairness? | Global FIFO | Single deque + lock |
| F7 | Performance target? | Correctness first; ~1M ops/s aspirational | CAS ring Phase 2 |
| F8 | Spurious wakeup? | Handle via loop | while !condition wait |
| F9 | null elements? | Disallowed or use optional | Sentinel |
| F10 | Metrics? | size, waits, drops | Optional |
| F11 | Priority? | No MVP | Separate queue |
| F12 | Weak consistency size()? | Approximate OK | Document |

**MVP scope:**

1. Fixed capacity ring buffer or deque.  
2. `offer(e)` / `poll()` blocking; `try_offer` / `try_poll` non-blocking.  
3. `offer(e, timeout)` / `poll(timeout)`.  
4. `close()` → unblock waiters; polls return empty.  
5. Thread-safe; no lost elements; FIFO order.  
6. Document memory visibility (happens-before on handoff).

**Out of MVP:** lock-free Michael-Scott queue (mention as upgrade).

### 1.2 Scope repeat-back

> Bounded MPMC queue with blocking/timed ops, FIFO ordering, clean shutdown, mutex + condition variable implementation with correct happens-before on element transfer.

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class BoundedMpmcQueue<T>:
  BoundedMpmcQueue(capacity: int)

  # blocking
  void offer(T item) throws ClosedException, InterruptedException
  T poll() throws ClosedException, InterruptedException

  # timed
  bool offer(T item, duration timeout)
  optional<T> poll(duration timeout)

  # non-blocking
  bool try_offer(T item)
  optional<T> try_poll()

  void close()
  bool is_closed()
  int approximate_size()
```

### 2.2 Guarantees

| Property | Guarantee |
|----------|-----------|
| FIFO | Items consumed in enqueue order |
| Bounded | size ≤ capacity at all times |
| Safety | No duplicate consume; no lost item after successful offer |
| Close | Waiters wake; offer fails; poll drains then empty |
| Linearization | offer and poll each linearizable |

---

## 3. Class Diagrams & Responsibilities

| Class | Responsibility |
|-------|----------------|
| `BoundedMpmcQueue<T>` | Public API |
| `RingBuffer<T>` | Storage slots + head/tail indices |
| `QueueLock` | mutex + not_empty + not_full condvars |
| `ClosedFlag` | atomic bool; set on close |
| `WaitStats` | blocked producers/consumers |

```text
+---------------------+
| BoundedMpmcQueue<T> |
+----------+----------+
           |
    +------+------+
    | RingBuffer  |
    | head, tail  |
    | count       |
    +-------------+
    | mutex       |
    | not_full    |
    | not_empty   |
    +-------------+
```

---

## 4. Data Structures & On-Disk Layout

In-memory only.

```text
buffer: array[T] size=capacity
head: int   # next dequeue index
tail: int   # next enqueue index
count: int  # items in queue  (or use head/tail diff with power-of-two mask)

Invariant: count == (tail - head) mod capacity logic
Alternative: std::deque + mutex (simpler interview, O(1) amortized)
```

**Ring buffer index math (power-of-two capacity C):**

```text
mask = C - 1
push at tail & mask
pop from head & mask
full when count == C
empty when count == 0
```

---

## 5. Concurrency Invariants

1. `0 ≤ count ≤ capacity`.  
2. `count` items logically between head and tail.  
3. After successful `offer`, item visible to next `poll`.  
4. On `close`, no new offers succeed; polls drain existing.  
5. **Lock held** during buffer mutation; condvar wait releases lock.

**Happens-before:** unlock after write slot → lock before read slot ensures visibility.

### 5.1 Lock ordering

Single mutex for MVP — no ordering issues.  
If split locks (not recommended): always `queue_mutex` only.

### 5.2 Lost wakeup prevention

```text
wait loop:
  lock()
  while count == capacity and not closed:
    not_full.wait(lock)
  if closed: unlock; throw
  enqueue
  not_empty.signal()
  unlock()
```

Use `while` not `if` for spurious wakeups.

---

## 6. Algorithms & Pseudocode

### 6.1 offer (blocking)

```text
function offer(item):
  lock(mutex)
  while count == capacity:
    if closed: unlock(); throw Closed
    not_full.wait(mutex)
  buffer[tail] = item
  tail = (tail + 1) % capacity
  count++
  not_empty.signal()      # wake one consumer
  unlock(mutex)
```

### 6.2 poll (blocking)

```text
function poll():
  lock(mutex)
  while count == 0:
    if closed: unlock(); return EMPTY
    not_empty.wait(mutex)
  item = buffer[head]
  head = (head + 1) % capacity
  count--
  not_full.signal()       # wake one producer
  unlock(mutex)
  return item
```

### 6.3 timed offer

```text
function offer(item, timeout):
  deadline = now + timeout
  lock(mutex)
  while count == capacity:
    if closed: unlock(); throw Closed
    remaining = deadline - now
    if remaining <= 0: unlock(); return false
    not_full.wait_for(mutex, remaining)
  enqueue(item)
  not_empty.signal()
  unlock(mutex)
  return true
```

### 6.4 close

```text
function close():
  lock(mutex)
  closed = true
  not_full.broadcast()
  not_empty.broadcast()
  unlock(mutex)
```

### 6.5 Optional: lock-free sketch (follow-up)

```text
# Michael & Scott MPMC extension or bounded array with CAS slots
# slot.state: EMPTY → WRITING → READY → READING → EMPTY
# Per-slot seq for ABA avoidance
```

---

## 7. Failure Modes & Recovery

| Issue | Mitigation |
|-------|------------|
| Spurious wakeup | while loops |
| InterruptedException | Restore interrupt flag; exit op |
| close during offer | Check closed in loop; fail fast |
| use-after-poll | Move semantics; clear slot optional |
| Thundering herd on broadcast | signal one; broadcast only on close |

No persistence — crash loses queued items (state this explicitly).

---

## 8. Tests & Edge Cases

1. Single producer/consumer sequential.  
2. MPMC stress 8×8 threads, 1M items — verify count 0 at end.  
3. Capacity 1 boundary — block/unblock both sides.  
4. Timed offer timeout when full.  
5. Timed poll timeout when empty.  
6. close wakes blocked producers and consumers.  
7. try_offer on full returns false immediately.  
8. FIFO order preserved under contention.  
9. No deadlock with concurrent close.  
10. Interrupted waiting thread exits cleanly.

---

## 9. Scalability Notes (Single-Node / Library Scope)

| Approach | When |
|----------|------|
| mutex + deque | Interview MVP; clarity |
| ring + condvar | Lower overhead |
| Disruptor / LMAX | 10M+ ops/s single JVM |
| separate SPSC queues per shard | Reduce MPMC contention |

For Databricks scheduler fan-in: many producers (API threads), many consumers (workers) — bounded queue provides **backpressure** when workers saturated.

---

## 10. Wrap-Up

**Summary:** One mutex protecting ring buffer + count; `not_full`/`not_empty` condition variables; while-loops for spurious wakeups; close broadcasts to unblock; timed waits via `wait_for`.

**Trade-offs**

| Mutex queue | Lock-free |
|-------------|-----------|
| Simple to prove | Higher throughput |
| Good enough many cases | Complex memory ordering |

---

## 11. Deeper / Related Interview Questions

1. signal vs broadcast performance?  
2. Why not unbounded queue? (OOM risk)  
3. Implement SPSC without locks?  
4. Compare Java `ArrayBlockingQueue` vs `LinkedBlockingQueue`.  
5. Backpressure strategies upstream when offer times out?  
6. Fairness vs throughput in thread pools?  
7. How would you add priority lanes?  
8. Memory barriers in lock-free ring?  
9. Poison pill shutdown pattern vs close flag?  
10. Use in job scheduler worker pool?

---

## 12. Appendices

### A. Full class sketch (Java-like)

```text
class BoundedMpmcQueue<T> {
  final Object[] buf;
  int head, tail, count;
  final ReentrantLock lock = new ReentrantLock();
  final Condition notFull = lock.newCondition();
  final Condition notEmpty = lock.newCondition();
  volatile boolean closed = false;
  // methods as pseudocode above
}
```

### B. Metrics

```text
queue_depth
offer_wait_time_ms
poll_wait_time_ms
offer_timeouts_total
closed_rejections_total
```

### C. Complexity

```text
offer/poll O(1)
contention O(threads) blocking
```

""" + APPENDIX_X + "\n\n*End of MPMC queue LLD prep.*\n"


DOCS = [
    ("persistent-inmemory-cache-lld-system-design.md", persistent_cache_lld),
    ("mpmc-queue-lld-system-design.md", mpmc_queue_lld),
]

if __name__ == "__main__":
    for name, fn in DOCS:
        gen_if_missing(name, fn())
