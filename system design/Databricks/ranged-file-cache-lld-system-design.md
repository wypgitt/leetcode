# LLD: Concurrent Range-Aware Client-Side File Cache

> **Focus areas:** Byte-range caching · Chunk alignment · Singleflight coalescing · LRU eviction · Pinning/refcount · Epoch invalidation · Race analysis  
> **Style:** LLD interview (clarify → API → classes → concurrency → pseudocode → failure → complexity → Q&A with answers → edge cases)  
> **Quality bar:** Correct range math, singleflight per chunk, no I/O under lock, clear eviction vs pinned races  
> **Interview theme:** Databricks — storage client / Spark executor read-path caching

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Chunking & Range Math](#4-chunking--range-math)
5. [Concurrency Invariants & Lock Order](#5-concurrency-invariants--lock-order)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Race Analysis](#7-failure-modes--race-analysis)
8. [Complexity Analysis](#8-complexity-analysis)
9. [Tests & Edge Cases](#9-tests--edge-cases)
10. [Interviewer Q&A With Answers](#10-interviewer-qa-with-answers)
11. [Wrap-Up](#11-wrap-up)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design a **client-side cache** that serves arbitrary byte-range reads from remote files (object store / DFS), coalescing concurrent readers and minimizing duplicate GETs.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Library/cache in reader process | Full CDN or origin server |
| Access | `read(file, offset, len)` | POSIX full filesystem MVP |
| Remote | S3/HDFS-like range GET | Local disk only |
| Databricks lens | Executor footer/index caching | Full Delta Lake protocol |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | API? | `read(path, offset, length) -> bytes` | Assemble from chunks |
| F2 | Chunk size? | Fixed 1–4 MiB (configurable) | Align fetches to chunk boundaries |
| F3 | Consistency? | Immutable file version per read; optional ETag | Cache key includes version |
| F4 | Concurrent readers? | Many threads on one JVM/process | Locks + Futures + singleflight |
| F5 | Cache capacity? | Byte budget B (e.g. 512 MiB) | LRU eviction by bytes |
| F6 | Partial chunk at EOF? | Yes — last chunk may be short | `validLen <= chunkSize` |
| F7 | Prefetch? | Optional Phase 2 | Sequential hint |
| F8 | Write-through? | Read-only cache MVP | `invalidate(file)` on external change |
| F9 | Blocking vs async? | Blocking `read()` MVP; internal Futures | `readAsync` optional |
| F10 | Remote errors? | Retry N times then fail all waiters | Remove in-flight entry |
| F11 | Metrics? | hit/miss/coalesce/eviction | Required for prod tuning |
| F12 | Pinning? | Active reads pin chunks against eviction | refcnt on Chunk |

**MVP scope:**

1. Fixed-size chunk cache keyed by `(file_id, version, chunk_index)`.  
2. Range read splits into chunk reads; assembles caller buffer.  
3. In-flight map coalesces duplicate chunk fetches (singleflight).  
4. LRU eviction by bytes; pinned chunks not evictable.  
5. Thread-safe; explicit behavior on fetch failure.  
6. `invalidate(file)` bumps epoch; stale fetches don't pollute cache.

**Out of MVP:** disk-tier cache, cross-process shared cache, write-through, CDN edge nodes.

### 1.2 Scope repeat-back

> Concurrent range-aware file cache: chunk remote files at 1–4 MiB, coalesce in-flight GETs via singleflight, assemble arbitrary unaligned ranges, bound memory with LRU + pinning, invalidate by file epoch when metadata changes.

### 1.3 Back-of-envelope

```text
chunkSize = 1 MiB, capacity = 512 MiB → max ~512 resident chunks
Typical Parquet footer read: 64 KB spanning 1 chunk → 1 GET if miss
Scan reading 128 MiB sequential: 128 chunk fetches without cache; with 512 MiB cache ~50% reuse on second pass

Executor read QPS = 20,000 ranges/s (hot table)
Avg range touches 2 chunks, hit ratio 85%
Miss rate = 20K × 2 × 0.15 = 6,000 chunk GETs/s
Singleflight on hot footer (same chunk): 100 threads → 1 GET + 99 coalesced waits
Remote GET latency p99 = 50 ms → in-flight map size ≈ QPS_miss × latency ≈ 300 entries peak
Memory: 512 chunks × 1 MiB = 512 MiB data + ~50 MB map/LRU overhead
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class FileRef:
  string file_id          # stable path or UUID
  string version          # ETag, generation, or commit version
  long file_size          # known before read; from HEAD/listing

class Options:
  chunk_size_bytes: int = 1 << 20       # 1 MiB default; allow 1–4 MiB
  capacity_bytes: long = 512 << 20
  max_retries: int = 3
  fetch_timeout_ms: long = 30_000
  allow_soft_overfill: bool = true      # when all chunks pinned

class FileCache:
  FileCache(RemoteClient remote, Options opt)

  byte[] read(FileRef file, long offset, int length) throws IOException
  CompletableFuture<byte[]> readAsync(FileRef file, long offset, int length)

  void invalidate(FileRef file)           # bump epoch for file_id
  void invalidateAll()
  CacheStats stats()
  void close()

class RemoteClient:
  byte[] getRange(FileRef file, long offset, int length) throws IOException
  # underlying: HTTP Range, S3 GetObject range, HDFS pread, etc.

class CacheStats:
  hits, misses, coalesces, evictions, fetch_failures: long
  bytes_served, bytes_fetched: long
  stored_bytes, in_flight_count: long
```

### 2.2 Guarantees

| Property | MVP guarantee |
|----------|---------------|
| Correctness | Returned bytes equal remote content at fetch time for each chunk assembled |
| Coalescing | At most one remote fetch per `ChunkKey` in flight |
| Memory | `stored_bytes ≤ capacity` except documented soft overfill when all pinned |
| Thread safety | All public methods safe concurrently |
| Stale reads | Possible if file overwritten without version bump — caller must update `FileRef.version` |
| Invalidation | After `invalidate(f)`, new reads for `f` won't insert stale epoch data into cache |

### 2.3 Error semantics

```text
offset < 0 or length < 0     → IllegalArgumentException
offset >= file_size          → IllegalArgumentException (or empty read — pick throw)
offset + length > file_size  → clamp length to EOF (document this choice)
remote 404                   → FileNotFoundException
remote 5xx / timeout         → retry then IOException; fail all waiters on that chunk
after close()                → ClosedException
```

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Role |
|-------|------|
| `FileCache` | Public API; orchestrates plan → fetch → assemble |
| `ChunkKey` | Immutable `(fileId, version, chunkIndex)` — cache and in-flight key |
| `Chunk` | `byte[] data`, `int validLen`, `AtomicInteger pinCount`, `long fetchEpoch` |
| `ChunkStore` | `HashMap<ChunkKey, Chunk>` + LRU doubly-linked list; byte accounting |
| `InFlightRegistry` | `Map<ChunkKey, CompletableFuture<Chunk>>` — singleflight leader/waiters |
| `RemoteClient` | `getRange(file, offset, len)` — network I/O |
| `RangePlanner` | Split `[offset, offset+length)` into `(chunkIndex, sliceFrom, sliceTo)` segments |
| `FileEpochRegistry` | `Map<fileId, AtomicLong epoch>` — incremented on invalidate |
| `Evictor` | LRU victim selection skipping `pinCount > 0` |
| `Metrics` | atomics for hits, misses, coalesces |

### 3.2 Architecture diagram

```text
  Thread A ──┐
  Thread B ──┼──> FileCache.read(file, offset, len)
  Thread C ──┘           │
                         v
                   RangePlanner.plan()
                         │
            for each segment (chunkIdx, from, to):
                         │
                         v
                   getChunk(key) ──> cache hit? ──yes──> pin + slice
                         │ no
                         v
              InFlightRegistry.singleflight
                    │            │
               leader│            │waiter
                    v            v
              RemoteClient    future.get()
              .getRange()          │
                    │              │
                    v              v
              ChunkStore.put + LRU eviction
                         │
                         v
                   assemble slices → byte[] result
```

### 3.3 ChunkKey equality

```text
ChunkKey equals/hash:
  file_id, version, chunk_index

Why version in key:
  Same path different ETag → different cache entries
  Prevents serving bytes from old object generation after overwrite
```

---

## 4. Chunking & Range Math

### 4.1 Constants and helpers

```text
CHUNK_SIZE = options.chunk_size_bytes   # e.g. 1 << 20

chunk_index(offset) = offset / CHUNK_SIZE
chunk_start(idx) = idx * CHUNK_SIZE
chunk_end_exclusive(idx, file_size) = min(file_size, (idx + 1) * CHUNK_SIZE)
bytes_in_chunk(idx, file_size) = chunk_end_exclusive(idx, file_size) - chunk_start(idx)
```

### 4.2 Range planner

```text
class Segment:
  chunk_index: int
  slice_from: int    # offset within chunk data array
  slice_to: int      # exclusive

function plan(offset, length, file_size):
  if offset < 0 or length < 0: throw IllegalArgument
  if offset >= file_size: throw IllegalArgument   # or return []
  length = min(length, file_size - offset)        # clamp to EOF
  if length == 0: return []

  segments = []
  pos = offset
  end = offset + length
  while pos < end:
    idx = pos / CHUNK_SIZE
    cs = chunk_start(idx)
    ce = chunk_end_exclusive(idx, file_size)
    slice_from = pos - cs
    slice_to = min(ce, end) - cs
    segments.append(Segment(idx, slice_from, slice_to))
    pos = cs + slice_to
  return segments
```

### 4.3 Worked example (CHUNK=100 for illustration)

```text
file_size = 1000
read(offset=150, length=200)  → bytes [150, 350)

Segment 0: idx=1, cs=100, ce=200 → slice [50, 100)  → 50 bytes
Segment 1: idx=2, cs=200, ce=300 → slice [0, 100)   → 100 bytes
Segment 2: idx=3, cs=300, ce=400 → slice [0, 50)    → 50 bytes

Remote fetches (full chunk policy):
  getRange(100, 100)  # entire chunk 1
  getRange(200, 100)  # entire chunk 2
  getRange(300, 100)  # entire chunk 3 (only 50 bytes valid at EOF side)
```

### 4.4 Assembly

```text
function assemble(segments, chunks_by_index):
  total = sum(seg.slice_to - seg.slice_from for seg in segments)
  buf = new byte[total]
  dst = 0
  for seg in segments:
    chunk = chunks_by_index[seg.chunk_index]
    assert seg.slice_to <= chunk.validLen
    System.arraycopy(chunk.data, seg.slice_from, buf, dst, seg.slice_to - seg.slice_from)
    dst += seg.slice_to - seg.slice_from
  return buf
```

### 4.5 EOF last chunk

```text
file_size = 2_500_000, CHUNK = 1_048_576
chunk 0: [0, 1048576)
chunk 1: [1048576, 2097152)
chunk 2: [2097152, 2500000)  → validLen = 402_848

fetch length for chunk 2 = min(CHUNK, file_size - chunk_start(2)) = 402_848
store validLen on Chunk object — assembly bounds checks use validLen
```

---

## 5. Concurrency Invariants & Lock Order

### 5.1 Shared state

| Structure | Synchronization |
|-----------|-----------------|
| `ChunkStore` map + LRU list | `cache_mutex` (ReentrantLock) |
| `InFlightRegistry` | `cache_mutex` OR separate `inflight_mutex` |
| `FileEpochRegistry` | `ConcurrentHashMap<fileId, AtomicLong>` |
| Metrics counters | `LongAdder` / atomics |
| `RemoteClient` calls | **never under cache_mutex** |

### 5.2 Lock order (mandatory)

```text
If using two locks:
  inflight_mutex → cache_mutex   (never reverse)

Recommended MVP: single cache_mutex for map + LRU + inflight
  Critical section: lookup, insert inflight future, LRU touch — SHORT
  Remote GET: outside lock

FORBIDDEN:
  hold cache_mutex during remote.getRange()
  hold cache_mutex during future.get() wait
```

### 5.3 Core invariants

1. **Singleflight:** at most one in-flight fetch per `ChunkKey`.  
2. **Future lifecycle:** each in-flight entry completed exactly once (success or failure).  
3. **Failed fetch cleanup:** in-flight entry removed before retry allowed.  
4. **Pin invariant:** chunk with `pinCount > 0` not chosen as LRU victim.  
5. **Byte accounting:** `stored_bytes == sum(chunk.validLen)` for cached entries.  
6. **Epoch safety:** chunk cached only if `fetchEpoch == currentEpoch(fileId)` at insert time.  
7. **No partial cache:** don't insert chunk unless remote returned expected length (or valid EOF length).

### 5.4 Pinning model

```text
class Chunk:
  byte[] data
  int validLen
  AtomicInteger pinCount = 0

  pin():   pinCount.incrementAndGet()
  unpin(): pinCount.decrementAndGet()  // assert >= 0 in debug

read() path:
  chunks = []
  try:
    for seg in plan:
      c = getChunk(...)   # pins inside getChunk
      chunks.append(c)
    return assemble(segments, chunks)
  finally:
    for c in chunks: c.unpin()
```

**Why pin:** without pin, thread A could be assembling from `chunk.data` while evictor removes and recycles the array → use-after-free.

---

## 6. Algorithms & Pseudocode

### 6.1 read — top level

```text
function read(file, offset, length):
  segments = RangePlanner.plan(offset, length, file.file_size)
  pinned_chunks = new Map chunkIndex → Chunk
  try:
    for seg in segments:
      key = ChunkKey(file.file_id, file.version, seg.chunk_index)
      chunk = getChunk(key, file)
      pinned_chunks[seg.chunk_index] = chunk
    return assemble(segments, pinned_chunks)
  finally:
    for c in pinned_chunks.values(): c.unpin()
```

### 6.2 getChunk — singleflight (explicit leader/waiter)

```text
function getChunk(key, file):
  # Phase 1: cache hit or register waiter — under lock
  with cache_mutex:
    chunk = chunk_store.get(key)
    if chunk != null:
      metrics.hits++
      chunk_store.touch_lru(key)
      chunk.pin()
      return chunk

    fut = inflight.get(key)
    if fut == null:
      fut = new CompletableFuture()
      inflight.put(key, fut)
      leader = true
    else:
      metrics.coalesces++
      leader = false
    wait_future = fut

  # Phase 2: waiter path — no lock held
  if not leader:
    try:
      chunk = wait_future.get(timeout)
      chunk.pin()
      return chunk
    catch Exception e:
      throw propagate(e)

  # Phase 3: leader fetch — NO lock
  epoch_at_start = epoch_registry.get(key.file_id)
  try:
    metrics.misses++
    idx = key.chunk_index
    start = chunk_start(idx)
    fetch_len = bytes_in_chunk(idx, file.file_size)
    bytes = remote.getRange(file, start, fetch_len)   # RETRIES inside client
    if bytes.length != fetch_len: throw IOException("short read")

    new_chunk = Chunk(bytes, validLen=fetch_len, fetchEpoch=epoch_at_start)

    with cache_mutex:
      # epoch check: stale if invalidated during fetch
      if epoch_registry.get(key.file_id) == epoch_at_start:
        chunk_store.put_evicting_lru(key, new_chunk)
      inflight.remove(key)
      wait_future.complete(new_chunk)

    new_chunk.pin()
    return new_chunk

  catch Exception e:
    with cache_mutex:
      inflight.remove(key)
      wait_future.completeExceptionally(e)
    throw e
```

### 6.3 put_evicting_lru

```text
function put_evicting_lru(key, chunk):
  assert held cache_mutex
  old = map.get(key)
  if old != null:
    stored_bytes -= old.validLen
    remove_from_lru(old)
  map.put(key, chunk)
  insert_mru(key)
  stored_bytes += chunk.validLen

  while stored_bytes > capacity:
    victim_key = find_lru_unpinned()
    if victim_key == null:
      if allow_soft_overfill: break
      else: throw CacheFullException  # rare
    remove(victim_key)
    stored_bytes -= victim.validLen
    metrics.evictions++
```

### 6.4 invalidate with epoch

```text
function invalidate(file):
  epoch_registry.get(file.file_id).incrementAndGet()
  with cache_mutex:
    remove all ChunkKey where key.file_id == file.file_id
    # adjust stored_bytes for each removal
    # do NOT cancel in-flight remote calls — epoch gate on insert handles staleness
```

**Late leader completion after invalidate:**

```text
Leader started at epoch=5, invalidate bumps to 6 during fetch
Leader completes: epoch_at_start(5) != current(6) → skip cache insert
Still complete Future with fetched Chunk — waiters get bytes (may be stale relative to new epoch)
Caller responsibility: after invalidate, use new FileRef.version for subsequent reads
Optional stricter policy: if epoch mismatch, completeExceptionally(StaleCacheException)
```

### 6.5 ConcurrentHashMap computeIfAbsent variant (idiomatic Java)

```text
function getChunk_chm(key, file):
  with cache_mutex:
    hit = chunk_store.get(key)
    if hit: pin(hit); return hit

  fut = inflight.computeIfAbsent(key, k -> supplyAsync(() -> fetchAndInsert(k, file)))

  try:
    c = fut.get()
    c.pin()
    return c
  catch e:
    inflight.remove(key, fut)
    throw e

function fetchAndInsert(key, file):
  bytes = remote.getRange(...)
  chunk = Chunk(bytes)
  epoch = ...
  with cache_mutex:
    if epoch_ok: chunk_store.put_evicting_lru(key, chunk)
  return chunk
  # whenComplete: inflight.remove(key)
```

**Subtlety:** always `remove(key, fut)` in `whenComplete` to allow retry after failure.

### 6.6 close

```text
function close():
  closed = true
  with cache_mutex:
    inflight.values().forEach(f -> f.cancel(true))
    chunk_store.clear()
    inflight.clear()
  remote.close()  # if applicable
```

---

## 7. Failure Modes & Race Analysis

### 7.1 Race: concurrent same chunk

```text
Threads T1..T100 all read footer → same ChunkKey K

Timeline:
  T1: miss → creates Future F, leader=true
  T2..T100: miss → see F in inflight, leader=false, coalesce++
  T1: remote.getRange (no lock)
  T1: insert cache, complete F
  T2..T100: F.get returns same Chunk, pin, assemble

Invariant: exactly 1 remote GET (verify with mock counter)
```

### 7.2 Race: leader failure

```text
Leader L throws timeout after inflight registered

  with cache_mutex:
    inflight.remove(key)
    fut.completeExceptionally(e)

Waiters receive exception. Next reader finds inflight empty → new leader.

Trap: forgetting remove → permanent cache miss / hung waiters
Fix: try/finally on leader path always removes + completes Future
```

### 7.3 Race: invalidate during fetch

```text
Thread R: fetching chunk K for file F (epoch=3)
Thread I: invalidate(F) → epoch=4, cache entries for F removed

R completes:
  epoch_at_start=3 != current=4 → do NOT insert into cache
  complete Future with data anyway (or StaleCacheException — document choice)

Thread N reads after invalidate with new version:
  new ChunkKey(file, version', idx) → miss → fresh fetch
```

### 7.4 Race: eviction vs pinned chunk

```text
Thread A: getChunk → pinCount=1, assembling
Evictor: while over capacity, skip victims with pinCount>0
If all resident chunks pinned: soft overfill (stored_bytes > capacity) until unpins

Without pin: evictor could remove chunk while A reads data → corruption
```

### 7.5 Race: overlapping ranges different threads

```text
T1: read offset=0 len=2MiB   → chunks {0, 1}
T2: read offset=1MiB len=2MiB → chunks {1, 2}

Chunk 1 singleflight: one fetch serves both
Total remote GETs: 3 unique chunks (0,1,2), not 4
```

### 7.6 Failure table

| Failure | Behavior |
|---------|----------|
| Remote timeout | Retry up to max_retries; then fail Future, remove inflight |
| Partial HTTP body | IOException; do not cache |
| File size shrunk | getRange may fail; invalidate + refresh metadata |
| Wrong content length | Treat as error; no cache insert |
| Leader thread interrupted | completeExceptionally; remove inflight |
| All chunks pinned + at capacity | Soft overfill; metric alert |
| Thundering herd after error | No negative cache MVP → each retry may hit remote; optional short negative TTL |
| close() during read | ClosedException on new reads; in-flight may complete or cancel |

---

## 8. Complexity Analysis

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| plan(offset, len) | O(num_chunks) | O(num_chunks) segments | num_chunks ≤ ⌈len/chunkSize⌉ + 1 |
| read (all hit) | O(num_chunks × chunkSize) copy | O(result len) | dominated by memcpy |
| read (all miss) | O(num_chunks × (T_network + chunkSize)) | O(num_chunks × chunkSize) temp | network bound |
| getChunk hit | O(1) hash + LRU splice | O(1) | under cache_mutex |
| getChunk miss (waiter) | O(T_network) | O(1) | no lock during wait |
| eviction | O(victims) | O(1) | each victim O(1) LRU |
| invalidate(file) | O(keys for file) | O(1) | may scan map |
| singleflight coalesce | O(1) register | O(in_flight) entries | in_flight ≈ miss_qps × latency |

**Hot path:** cache hit avoids network entirely — target >80% hit rate on repeated scans.

---

## 9. Tests & Edge Cases

### 9.1 Functional tests

1. Aligned read exactly one chunk.  
2. Unaligned read spanning 3 chunks.  
3. EOF: last chunk `validLen < chunkSize`.  
4. `offset + length` clamped to file size.  
5. Zero-length read returns empty array.  
6. `offset == file_size` throws (if that policy chosen).  
7. invalidate → subsequent read refetches.  
8. Version change in FileRef → cache miss (different key).

### 9.2 Concurrency / coalescing tests

```text
test_singleflight_n_threads_same_chunk:
  mock remote counter
  50 threads read same footer range
  assert remote.getRange_call_count == 1
  assert stats.coalesces >= 49

test_overlapping_reads_share_middle_chunk:
  T1 read [0, 2MiB), T2 read [1MiB, 3MiB)
  assert chunk 1 fetched once

test_leader_failure_waiters_retry:
  remote fails first attempt
  assert inflight empty after failure
  second read succeeds, 2 remote calls total
```

### 9.3 Eviction / pinning tests

```text
test_pin_prevents_eviction:
  capacity = 1 chunk
  T1 slow assemble holding pin on chunk A
  T2 read chunk B → allowed soft overfill OR blocks per policy
  after T1 unpin, eviction reduces to capacity

test_lru_order:
  touch A, B, C with capacity 2 chunks → A evicted first
```

### 9.4 Invalidate / epoch tests

```text
test_invalidate_during_fetch:
  block remote until invalidate called
  assert completed chunk NOT in cache if epoch changed
  waiters still receive bytes or StaleException per policy

test_invalidate_removes_all_versions:
  cache keys (file,v1,0) and (file,v2,0) — define policy
  MVP: invalidate(file_id) removes all versions for that file_id
```

### 9.5 Edge cases matrix

| Edge | Expected behavior |
|------|-------------------|
| capacity = 0 | Every read misses cache; still coalesces in-flight |
| chunkSize = 4 MiB, read 1 byte | fetch full 4 MiB chunk (document amplification) |
| Huge length (> file) | clamp to EOF |
| Negative offset | IllegalArgument |
| Remote returns 416 | refresh size / invalidate |
| Double close() | idempotent |
| read after close() | ClosedException |
| Same chunk key, different version | separate entries |
| Mock slow remote + 100 waiters | 1 GET, 99 coalesced, no deadlock |

---

## 10. Interviewer Q&A With Answers

### Q1: Why fetch full chunks instead of exact sub-ranges?

**A:** Object stores (S3, ADLS) charge per request; range GET latency is similar for 4 KiB vs 1 MiB. Aligning to 1–4 MiB chunks amortizes request overhead and maximizes reuse when nearby bytes are read (footer + column chunk). Tradeoff: read amplification on tiny random reads — mitigate with smaller chunk size option or mini-cache for metadata.

### Q2: 1 MiB vs 4 MiB chunks?

**A:** 1 MiB: lower amplification for small random reads, more map entries for same capacity. 4 MiB: better sequential scan throughput, fewer GETs, higher memory churn per miss. For Parquet footers (~few KB), 1 MiB is fine. For large sequential scans, 4 MiB or adaptive sizing (Phase 2) wins. I'd default 1 MiB, make configurable.

### Q3: Why epoch instead of cancelling in-flight remote requests?

**A:** HTTP/S3 clients often can't cheaply cancel bytes on the wire. Epoch lets late responses discard cache insert without aborting TCP. Callers use updated `FileRef.version` for correctness. Optional: cancel Future if remote supports true cancellation.

### Q4: How does this relate to Spark / Databricks executors?

**A:** Executors read Parquet/ORC footers and column chunks from cloud storage via range GETs. This cache sits in the executor JVM: task threads reading the same file share cached chunks, cutting duplicate footer fetches from 400 tasks to 1. Similar to Hadoop FSDataInputStream cache but explicit chunk + singleflight design.

### Q5: compareTo OS page cache?

**A:** OS page cache is generic, per-node, evicted by kernel policy, no file version awareness. Our cache knows immutable file versions, coalesces JVM threads, respects executor memory budget, and integrates metrics. OS cache still helps — this is additive at application level.

### Q6: Hedged reads for slow GETs?

**A:** Phase 2: if p99 fetch > threshold, issue second hedged request; first response wins; cancel loser. Risk: amplifies load. Singleflight already prevents duplicate concurrent fetches for same chunk — hedging is for single slow leader, not herd.

### Q7: Should waiters block on `cache_mutex`?

**A:** No. Waiters block on `Future.get()` outside the lock. Only the leader does remote I/O. Mutex protects map/LRU/inflight metadata only — hold time microseconds.

### Q8: Connection pool sizing?

**A:** Max concurrent unique chunk fetches ≤ pool size. Rule of thumb: `pool = min(unique_miss_qps × p99_latency, num_cores × 4)`. Coalescing reduces effective concurrent fetches vs raw read QPS. Monitor in_flight gauge.

### Q9: Consistency when writer overwrites S3 object?

**A:** Without version in key, readers may see stale bytes. Require `FileRef.version` (ETag/generation). On overwrite, coordinator passes new version → natural cache miss. Call `invalidate(file)` on commit boundaries in Delta/Iceberg-style workflows.

### Q10: Disk-tier (SSD) cache beneath RAM?

**A:** Extension: hash chunk content → file on local NVMe; RAM holds index. On miss: check RAM → check disk → remote. Eviction spills to disk before remote re-fetch. Adds async I/O and checksum validation — mention as Phase 2, not MVP.

### Q11: Negative cache for 404?

**A:** Optional: cache "chunk not found" with short TTL (100 ms) to protect origin during metadata storms. MVP: no negative cache — simpler; 404 propagates immediately.

### Q12: Fairness when one scan wipes LRU?

**A:** Global LRU lets sequential scan of file A evict all hot metadata of file B. Mitigations: segmented LRU (SLRU), per-file byte cap (`min(global, per_file_max)`), or TinyLFU admission. Mention scan resistance — demand reads promote LRU; prefetch doesn't.

### Q13: Zero-copy with ByteBuffer?

**A:** Return `ReadOnlyByteBuffer` slices referencing chunk arrays with refcnt instead of `byte[]` copy. Caller must release buffer. Reduces CPU for large sequential reads — API change from MVP `byte[]`.

### Q14: readAsync implementation?

**A:** `return CompletableFuture.supplyAsync(() -> read(...), executor)` or non-blocking remote client. Internal singleflight unchanged — async waiters still join same Future. Don't duplicate fetch logic.

### Q15: How to test singleflight without flakiness?

**A:** Inject controllable `RemoteClient` with `CountDownLatch`: leader blocks in getRange until test releases; spawn N-1 waiters, assert 0 remote calls until release, then 1 call total. Deterministic, no sleeps.

**Common traps**

| Trap | Fix |
|------|-----|
| Cache arbitrary ranges as keys | Chunk-aligned ChunkKey |
| Remote GET under global lock | Unlock before I/O |
| Failed Future left in map | remove in finally/whenComplete |
| Evict while reader uses array | pin/refcount |
| Ignore file version | include in ChunkKey |

---

## 11. Wrap-Up

**Design summary**

- Fixed **1–4 MiB chunks**; `RangePlanner` splits arbitrary reads.  
- **Singleflight** via `InFlightRegistry` — one remote GET per `ChunkKey`.  
- **LRU eviction** by bytes; **pinCount** prevents evicting in-use chunks.  
- **Epoch invalidation** drops stale inserts after `invalidate(file)`.  
- **No I/O under lock** — leader fetches outside `cache_mutex`.

**MVP vs later**

| MVP | Later |
|-----|-------|
| RAM LRU + singleflight | Disk tier, SLRU/TinyLFU |
| Full chunk fetch | Sub-range fetch for tiny reads |
| byte[] return | ByteBuffer zero-copy |
| Blocking read | Async pipeline + prefetch |
| Per-process cache | Shared off-heap cache |

**Options defaults**

```text
chunk_size_bytes = 1 MiB
capacity_bytes = 512 MiB
max_retries = 3
fetch_timeout_ms = 30_000
allow_soft_overfill = true
```

**Metrics**

```text
hits, misses, coalesces, evictions, fetch_failures
bytes_served, bytes_fetched, stored_bytes, in_flight_count
```

**Top risks**

1. Holding lock during remote GET (deadlock under load)  
2. Not removing failed in-flight entries (stuck cache)  
3. Evicting pinned chunks (use-after-free)  
4. Ignoring version in ChunkKey (stale reads)

**Interview timing (45 min)**

| Min | Focus |
|-----|-------|
| 0–5 | API + chunk size choice |
| 5–12 | Range math + worked example |
| 12–25 | Singleflight pseudocode on board |
| 25–33 | LRU + pinning + eviction |
| 33–40 | Invalidate epoch + race stories |
| 40–45 | Tests + coalescing metric |

---

*End of LLD prep.*
