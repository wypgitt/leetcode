# LLD: Crash- and Power-Loss-Safe Embedded KV Store

> **Focus areas:** WAL · fsync / group commit · torn writes · checksums · memtable + index · compaction · concurrency · recovery  
> **Style:** LLD interview (clarify → API → classes → concurrency → failure → pseudocode → complexity → Q&A with answers → edge cases)  
> **Quality bar:** Explicit durability invariant, linearization vs crash boundary, concrete lock order, crash-point matrix  
> **Interview theme:** Databricks — signature storage/concurrency LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [On-Disk Layout & WAL](#4-on-disk-layout--wal)
5. [Concurrency Invariants & Lock Order](#5-concurrency-invariants--lock-order)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes, Recovery & Crash-Point Matrix](#7-failure-modes-recovery--crash-point-matrix)
8. [Complexity Analysis](#8-complexity-analysis)
9. [Tests & Edge Cases](#9-tests--edge-cases)
10. [Interviewer Q&A With Answers](#10-interviewer-qa-with-answers)
11. [Wrap-Up](#11-wrap-up)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design a **single-node embedded** key-value store where acknowledged writes survive process crash and power loss (within stated `fsync` policy).

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Scope | One process, one data directory | Distributed Redis/Cassandra |
| API | `get` / `put` / `delete` (+ optional CAS) | SQL, multi-key txn MVP |
| Durability | ACK ⇒ durable per policy | Best-effort cache |
| Databricks lens | WAL, fsync, recovery, races | Premature Raft |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Single-node or distributed? | **Single-node** | No consensus |
| F2 | Key/value types? | Bytes; bounded size (e.g. ≤1MB) | Length-delimited records |
| F3 | Ops? | get, put, delete; optional scan/CAS | Start point ops |
| F4 | Durability? | Acknowledged put must survive power loss | WAL + fsync/group commit |
| F5 | Read-your-writes? | Yes in-process | Update mem index after durable |
| F6 | TTL / LRU? | Optional Phase 2 | Separate from durability core |
| F7 | Concurrent clients? | Multi-threaded | RW locks / striping |
| F8 | Range scans? | Nice-to-have | LSM or sorted segment later |
| F9 | Compression? | Optional | After correctness |
| F10 | Encryption? | Optional at rest | Envelope keys Phase 2 |
| F11 | Max data size? | Fits disk; working set may exceed RAM | Values on disk OK |
| F12 | Crash model? | Fail-stop; disks may tear last write | Checksums + truncation |

**MVP scope:**

1. Persistent `put`/`delete`/`get` with last-writer-wins.  
2. WAL records with CRC; recovery replays.  
3. Explicit `SyncMode`: `EVERY_WRITE` vs `GROUP_COMMIT`.  
4. In-memory index: key → (file_id, offset, length) or key → value for hot set.  
5. Compaction/snapshot to bound WAL growth.  
6. Thread-safe API with documented linearization points.

**Out of MVP:** multi-key transactions, distributed replication, full RocksDB clone.

### 1.2 Scope repeat-back

> Single-node embedded KV: byte keys/values, WAL-backed durability for acknowledged writes, crash recovery with checksummed records, concurrent get/put, and compaction—tuning fsync policy for latency vs throughput.

### 1.3 Durability contract (lock early)

```text
SyncMode.EVERY_WRITE:
  put returns ⇒ record in WAL durable on stable storage (fsync per record)

SyncMode.GROUP_COMMIT:
  put returns ⇒ record durable in same fsync batch as all other ACKed puts in that batch
  (leader thread batches appends, single fsync, then ACKs entire batch)

Interview default: ACK only after fsync completes — RPO=0 for ACKed writes.
Never ACK before durability if you claim power-loss safety.
```

### 1.4 Back-of-envelope (single node)

```text
Assume: 4KB avg value, 10K puts/s peak, 100K gets/s peak

WAL append: ~4KB + 32B header ≈ 4.032 KB/put
EVERY_WRITE fsync: ~1–5 ms/fsync on NVMe → 200–1000 puts/s (fsync bound)
GROUP_COMMIT 2ms window: batch ~20K puts → amortized fsync → 10K+ puts/s

Index: HashMap O(1); 1M keys × (32B key ptr + 24B Location) ≈ 56 MB RAM
WAL growth without compaction: 10K/s × 4KB × 3600 ≈ 144 GB/hour — compaction mandatory
Recovery: replay 8 GB WAL @ 500 MB/s scan ≈ 16s cold start; snapshot cuts tail
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
enum SyncMode { EVERY_WRITE, GROUP_COMMIT }

class Options:
  path: string
  sync_mode: SyncMode = GROUP_COMMIT
  group_window_ms: int = 2
  max_key_bytes: int = 4096
  max_value_bytes: int = 1_048_576
  wal_rotate_bytes: int = 64 << 20
  compaction_threshold_ratio: float = 4.0

class KVStore:
  static open(path, options) -> KVStore
  get(key: Bytes) -> Optional[Bytes]
  put(key: Bytes, value: Bytes) -> void
  delete(key: Bytes) -> void
  compare_and_swap(key, expected_seq: uint64, new_value: Bytes) -> bool
  flush() -> void                    # force pending group commit fsync
  compact() -> void                  # optional manual trigger
  stats() -> Stats
  close() -> void

class Stats:
  puts, gets, deletes: uint64
  wal_bytes, live_bytes: uint64
  fsync_count, fsync_latency_p99_us: uint64
  recovery_ms: uint64
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
| Single-key atomicity | Yes for put/delete |
| Durability | ACKed writes survive crash (per SyncMode) |
| Consistency after crash | Prefix of WAL up to last complete CRC-valid record |
| Isolation | Concurrent gets see linearizable single-key ops |
| Ordering | Per-key last-writer-wins by WAL sequence number |
| Multi-key atomicity | No (MVP) |

### 2.3 Error model

```text
InvalidArgument   — empty key, oversized value
CorruptionError   — checksum failure beyond repair point
IOError           — disk full (ENOSPC), permission denied
ClosedError       — ops after close()
CasFailed         — expected_seq mismatch
```

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Responsibility |
|-------|----------------|
| `KVStore` | Public API facade; lifecycle; orchestrates write/read paths |
| `Options` | sync mode, max sizes, wal dir, compaction thresholds |
| `WalWriter` | Append records to active WAL file; rotate at size |
| `WalRecord` | Encode/decode; CRC32 over (seq, op, key, value) |
| `MemIndex` | `HashMap<Bytes, IndexEntry>` — key → Location or inline value |
| `IndexEntry` | seq, kind(PUT/DEL), Location or cached bytes |
| `Location` | wal_file_id, offset, length |
| `GroupCommitter` | Batch pending records; fsync; complete Futures |
| `Compactor` | Rewrite live keys to snapshot; publish manifest |
| `Manifest` | snapshot path, active wal files, next_seq, compaction watermark |
| `Recovery` | Replay WAL/segments; rebuild index; truncate torn tail |
| `LockManager` | `log_mutex` + `index_rwlock` with strict order |
| `Metrics` | append latency, fsync latency, recovery time |

### 3.2 ASCII class diagram

```text
+-------------------+
|     KVStore       |
+---------+---------+
          |
          +--> WalWriter (append, rotate)
          +--> GroupCommitter (batch fsync)
          +--> MemIndex (ConcurrentHashMap or guarded HashMap)
          +--> Manifest (atomic publish via rename)
          +--> Compactor (background thread)
          |
          +--> log_mutex      (serializes WAL append + fsync ordering)
          +--> index_rwlock   (protects index snapshot for compaction)

WalRecord on disk:
  magic:4 | length:4 | seq:8 | op:1 | key_len:4 | key | val_len:4 | val | crc32:4
```

### 3.3 Ownership & lifecycle

- `KVStore` owns directory FDs, `GroupCommitter` thread, optional `Compactor` thread.  
- Compaction writes new snapshot file; old WAL segments deleted only after manifest publish + fsync.  
- `close()` flushes group commit, fsyncs manifest, joins background threads.

---

## 4. On-Disk Layout & WAL

### 4.1 Directory layout

```text
datadir/
  CURRENT                 # single line: active MANIFEST filename
  MANIFEST-000042         # JSON or binary: snapshot, wal list, next_seq
  wal/
    wal-000001.log
    wal-000002.log
  snap/
    snap-000010.dat       # optional snapshot: count + repeated (key_len,key,val_len,val)
```

### 4.2 Record format

```text
magic:     4 bytes  "DKV1"
length:    4 bytes  uint32  (bytes from seq through value, excluding magic/length/crc)
seq:       8 bytes  uint64  monotonic, never reused after recovery
op:        1 byte   PUT=1 DELETE=2
key_len:   4 bytes  uint32
key:       key_len bytes
value_len: 4 bytes  uint32  (0 for DELETE)
value:     value_len bytes
crc32:     4 bytes  CRC32C over bytes [seq .. value inclusive]
```

**Why length + CRC:** detect torn writes at end of file; recovery truncates to last good record.

### 4.3 Write path (logical)

```text
put(k, v):
  validate sizes
  rec = WalRecord.put(next_seq++, k, v)
  append rec to WAL buffer
  fsync per SyncMode policy
  update MemIndex[k] = IndexEntry(rec)
  return   # only after fsync (or group fsync) completes
```

**Linearization vs durability:**

- **Durability point:** after successful `fsync` of the record (or batch containing it).  
- **Linearization point for readers:** index update **after** durability if ACK waits for fsync.  

Never ACK, never publish to index before durability if you claim power-loss safety for ACKs.

### 4.4 Read path

```text
get(k):
  with index read lock (or lock-free CHM read):
    entry = MemIndex.get(k)
    if absent or entry.kind == DELETE: return None
    if entry.has_inline_value: return entry.value
    else: read wal/segment at entry.location; verify crc; return bytes
```

### 4.5 Compaction / snapshot

```text
1. Pause or snapshot-copy MemIndex under read lock
2. Write snap-N.dat: magic | count | for each live key: key_len | key | val_len | val
3. fsync snap-N.dat
4. Write MANIFEST.tmp: { snapshot: snap-N, wal_start_seq: S, next_seq: current }
5. fsync MANIFEST.tmp; rename to MANIFEST-(N+1); fsync directory
6. Write CURRENT.tmp; fsync; rename CURRENT; fsync directory
7. Delete wal files with all records seq <= S (after grace period)
```

**Invariant:** old WAL/snap files remain until manifest publish succeeds.

### 4.6 WAL rotation

When active WAL exceeds `wal_rotate_bytes`:

```text
fsync current wal
open wal-(id+1).log
update manifest.wal_files append new file
fsync manifest + directory
```

Recovery replays all WAL files listed in manifest in order.

---

## 5. Concurrency Invariants & Lock Order

### 5.1 Shared mutable state

| State | Protected by |
|-------|--------------|
| WAL append offset, next_seq assignment | `log_mutex` |
| WAL file buffer / fd | `log_mutex` |
| MemIndex map | `index_rwlock` (many readers) or single `rwlock` |
| GroupCommitter pending queue | `committer_mutex` (internal to GroupCommitter) |
| Manifest pointer | atomic load of immutable Manifest object |
| Compaction in-progress flag | `compaction_mutex` |

### 5.2 Core invariants

1. **Seq monotonic:** each WAL record has unique increasing `seq`; `next_seq = max(replayed_seq) + 1` after recovery.  
2. **ACK ⇒ durable:** no return from put/delete until sync policy satisfied.  
3. **Index ⊆ durable:** index never points at undurable record for ACKed ops.  
4. **Per-key LWW:** higher seq wins after recovery.  
5. **No torn visible records:** readers only decode CRC-valid records.  
6. **Compaction safety:** live keys in index always reachable from manifest-listed files.

### 5.3 Lock order (mandatory — say on whiteboard)

```text
ALLOWED acquisition order (always increasing):
  (1) stripe_lock(key)     — optional, only if using key striping for CAS
  (2) log_mutex            — WAL append + fsync
  (3) index_write_lock     — update MemIndex after durable append

FORBIDDEN:
  index_write_lock → log_mutex   (deadlock + violates log-before-index)
  compaction_mutex → log_mutex while holding index_write_lock inverted

Reads (get):
  index_read_lock ONLY — never acquire log_mutex
  OR ConcurrentHashMap.get without lock if index updates publish with happens-before via log_mutex unlock

Group commit path:
  producer: log_mutex → append to buffer → enqueue to GroupCommitter → wait on Future
  committer thread: dequeue batch → log_mutex → fsync → release → index updates
```

**Why this order:** WAL is source of truth; index is derived cache. Log must be durable before index reflects write. Readers never block writers on log_mutex.

### 5.4 SyncMode concurrency comparison

| Aspect | EVERY_WRITE | GROUP_COMMIT |
|--------|-------------|--------------|
| Lock hold during fsync | Yes, under log_mutex | Committer thread holds log_mutex for fsync |
| Producer wait | fsync inline | Future.wait() until batch fsync |
| Index update timing | Immediately after fsync, same thread | After batch fsync, may batch index updates |
| Throughput | fsync-bound (~1K/s) | Amortized fsync (~10–50×) |
| p99 put latency | ~fsync latency | ~group_window + fsync |

### 5.5 get during put — race analysis

```text
Thread W (put k=v2):  append WAL → fsync → index[k]=v2 → return ACK
Thread R (get k):     index read → sees v1 or v2, never corrupt bytes

Allowed: R sees stale v1 while W still in fsync (linearizable at durability boundary)
Forbidden: R sees v2, W crashes before fsync, W already returned ACK

Implementation: index update AFTER fsync; ACK AFTER index update (both after fsync)
```

### 5.6 delete vs get race

```text
delete(k) writes DELETE record seq=N+1, fsync, index[k]=TOMBSTONE
get(k) after delete linearization: returns None
get(k) concurrent with delete: returns old value or None, never partial delete
```

---

## 6. Algorithms & Pseudocode

### 6.1 put — EVERY_WRITE

```text
function put(key, value):
  validate(key, value)
  rec = WalRecord(PUT, next_seq++, key, value)
  with log_mutex:
    offset = wal.append(rec)
    wal.fsync()
    loc = Location(wal.id, offset, rec.on_disk_size)
    with index_write_lock:
      index.put(key, IndexEntry(rec.seq, PUT, loc))
  metrics.record_put()
```

### 6.2 put — GROUP_COMMIT

```text
class GroupCommitter:
  mutex, cond
  pending: List[(WalRecord, Promise)]
  window_ms, max_batch_bytes

  function submit(rec) -> Result:
    p = new Promise()
    with mutex:
      pending.append((rec, p))
      if should_flush(): signal committer
    return p.wait()

  function commit_loop():
    loop:
      sleep(window_ms) or wait signal
      with mutex:
        batch = take_pending()
      if batch empty: continue
      with log_mutex:
        for rec,_ in batch: wal.append(rec)
        wal.fsync()
      with index_write_lock:
        for rec,_ in batch:
          index.put(rec.key, IndexEntry.from(rec))
      for _,p in batch: p.complete(OK)

function put(key, value):
  rec = WalRecord(PUT, allocate_seq(), key, value)  # seq assigned under log_mutex
  group_committer.submit(rec)
```

**Seq assignment:** allocate `next_seq` inside `log_mutex` during append to preserve total order matching WAL order.

### 6.3 get

```text
function get(key):
  with index_read_lock:  # or lock-free CHM
    entry = index.get(key)
    if entry == null or entry.kind == DELETE: return None
    if entry.inline_value != null: return entry.inline_value
    loc = entry.location
  # I/O outside index lock
  bytes = wal.read_at(loc)  # verifies CRC on read
  return bytes
```

### 6.4 delete

```text
function delete(key):
  rec = WalRecord(DELETE, next_seq++, key, empty)
  # identical to put path but op=DELETE, index stores TOMBSTONE
  durable_append(rec)
  index.put(key, IndexEntry(rec.seq, DELETE, null))
```

### 6.5 Recovery — torn write safe iteration

```text
function recover(dir):
  manifest = load_current_manifest()  # read CURRENT → MANIFEST-N
  index = new HashMap()
  max_seq = 0

  if manifest.snapshot != null:
    index = load_snapshot(manifest.snapshot)
    max_seq = manifest.snapshot_max_seq

  for wal_path in manifest.wal_files ordered:
    for record, truncated in iterate_records_safe(wal_path):
      if truncated:
        log.warn("truncated torn tail at", wal_path)
      if record.seq <= max_seq: continue  # already in snapshot
      apply_record(index, record)
      max_seq = max(max_seq, record.seq)

  next_seq = max_seq + 1
  return KVStore(index, next_seq, manifest)

function iterate_records_safe(path):
  offset = 0
  file_len = filesize(path)
  while offset + MIN_HEADER <= file_len:
    magic = read_u32(path, offset)
    if magic != MAGIC: break
    length = read_u32(path, offset + 4)
    record_size = 4 + 4 + length + 4  # magic + length field + payload + crc
    if offset + record_size > file_len:
      truncate_file(path, offset)  # torn write — incomplete record
      yield TRUNCATED; break
    payload = read(path, offset + 4, length)
    crc_stored = read_u32(path, offset + 4 + length)
    if crc32c(payload) != crc_stored:
      truncate_file(path, offset)  # corrupted tail
      yield TRUNCATED; break
    yield decode_record(payload), false
    offset += record_size

function apply_record(index, rec):
  if rec.op == PUT:
    index[rec.key] = IndexEntry(rec.seq, PUT, loc_from(rec))
  elif rec.op == DELETE:
    index[rec.key] = IndexEntry(rec.seq, DELETE, null)
  # LWW: replay order matches seq order; later records overwrite
```

### 6.6 Compaction

```text
function compact():
  if compaction_in_progress: return
  with compaction_mutex:
    snapshot_index = copy_index_under_read_lock()
    live_count = count_non_tombstone(snapshot_index)
    write_snapshot_file(snapshot_index, path=snap-NEW.dat)
    fsync(snap-NEW.dat)
    new_manifest = manifest.copy()
    new_manifest.snapshot = snap-NEW.dat
    new_manifest.snapshot_max_seq = max_seq_in(snapshot_index)
    new_manifest.wal_files = [current_wal_only]  # or wal files after snapshot seq
    publish_manifest_atomic(new_manifest)
    schedule_delete_old_files(old_wal, old_snap)
```

### 6.7 compare_and_swap

```text
function compare_and_swap(key, expected_seq, new_value):
  with stripe_lock(key):           # (1)
    with log_mutex:                # (2) — only if not already held; CAS is rare path
      entry = index.get(key)
      cur_seq = entry?.seq ?? 0
      if cur_seq != expected_seq: return false
      rec = WalRecord(PUT, next_seq++, key, new_value)
      wal.append(rec); wal.fsync()
    with index_write_lock:         # (3)
      index.put(key, IndexEntry.from(rec))
    return true
```

### 6.8 Atomic manifest publish

```text
function publish_manifest(m):
  tmp = "MANIFEST-" + m.seq + ".tmp"
  write_all(tmp, serialize(m))
  fsync(tmp)
  rename(tmp, "MANIFEST-" + m.seq)
  fsync_directory(datadir)
  write_atomic("CURRENT", "MANIFEST-" + m.seq)
```

---

## 7. Failure Modes, Recovery & Crash-Point Matrix

### 7.1 Crash-point matrix

| # | Crash point | On disk state | Client saw | After recovery | Correct? |
|---|-------------|---------------|------------|----------------|----------|
| C1 | Before WAL buffer write | unchanged | no ACK | key absent or old value | ✓ |
| C2 | After write(), before fsync | record in OS page cache | no ACK | record lost; old value | ✓ |
| C3 | After fsync, before index update | record durable | no ACK yet | replay restores index | ✓ |
| C4 | After index update, before ACK return | record durable | no ACK | data present | ✓ (extra durable) |
| C5 | After ACK returned | record durable | ACK | data present | ✓ |
| C6 | Mid-record write (torn) | partial last record | no ACK | truncate tail; prior prefix intact | ✓ |
| C7 | CRC corrupt tail | bad bytes at end | no ACK | truncate at last good CRC | ✓ |
| C8 | During compaction seg write | old manifest current | reads OK | old data intact | ✓ |
| C9 | After new manifest fsync | new snapshot + wal | reads OK | new view; old files GC later | ✓ |
| C10 | Disk full mid-append | partial or none | IOError, no ACK | no partial ACKed state | ✓ |
| C11 | Bitrot in old segment | CRC fail on read | get throws CorruptionError | alert; restore from backup | ✓ |

### 7.2 fsync folklore (state precisely)

```text
write() / pwrite():
  Copies to kernel page cache. NOT durable on power loss.

fsync(fd) / fdatasync(fd):
  Flushes file data to stable storage (disk/SSD with write cache disabled or FUA).
  fdatasync skips metadata unless needed; for WAL payload either works if file size stable.

fsync(directory_fd):
  Required after rename()/create() to persist directory entry.
  Pattern: write file → fsync(file) → rename → fsync(dir)

rename():
  Atomic on POSIX for same filesystem — readers see old or new name, never garbled.

O_SYNC / O_DSYNC:
  Every write() blocks until durable. Simpler than manual fsync but less batching control.

Group commit:
  Amortizes fsync cost; ACK latency = batch window + fsync time.
  All puts in batch must ACK together after fsync — never ACK subset early.

SSD write cache:
  Without fsync, power loss can lose "written" data still in drive cache.
  Interview answer: "We fsync the WAL fd; we don't rely on write() return alone."
```

### 7.3 Power loss vs kill -9

Both must be safe for ACKed writes. Power loss stresses hardware durability; kill -9 stresses crash without flushing userspace buffers—but kernel may have persisted page cache if fsync completed. Torn last record still possible at sector boundary; length+CRC handles it.

### 7.4 Recovery procedure (operator / open path)

```text
1. Read CURRENT → find MANIFEST-N
2. If CURRENT missing/corrupt: scan newest valid MANIFEST-* by seq
3. Load snapshot if manifest.snapshot set
4. Replay WAL files in manifest.wal_files order
5. Truncate torn tail on last WAL file
6. Set next_seq = max(replayed seq) + 1
7. Open for traffic; schedule compaction if wal_bytes > threshold
8. Log recovery_ms metric
```

### 7.5 ENOSPC (disk full)

```text
on ENOSPC during wal.append:
  do NOT update index
  do NOT ACK client
  return IOError
  optional: trigger emergency compaction if live_bytes << wal_bytes
```

---

## 8. Complexity Analysis

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| put (EVERY_WRITE) | O(\|key\|+\|val\|) + T_fsync | O(1) index | fsync dominates |
| put (GROUP_COMMIT) | O(\|key\|+\|val\|) + T_fsync/batch | O(batch) pending | amortized fsync |
| get (cache hit) | O(\|key\|) hash | O(1) | inline value: O(1) |
| get (cache miss) | O(\|key\|+\|val\|) read + CRC | O(1) | disk bound |
| delete | same as put | O(1) | tombstone retained |
| recovery | O(wal_bytes + snap_bytes) | O(keys) index | linear scan |
| compaction | O(live_bytes) write | O(keys) temp | background |
| iterate_records | O(file_size) | O(1) | per WAL file |

**Bottleneck:** fsync latency and frequency, not CPU. Group commit trades tail latency for throughput.

---

## 9. Tests & Edge Cases

### 9.1 Functional tests

1. put/get/delete happy path.  
2. Overwrite same key — LWW by seq.  
3. get missing key → None/null.  
4. Empty value allowed (distinct from delete — document semantics).  
5. Large value at max_value_bytes boundary.  
6. Reopen store after close — data present.  
7. CAS success when expected_seq matches; fail when stale.

### 9.2 Crash injection tests

| Test | Method | Expect |
|------|--------|--------|
| Crash after fsync | LD_PRELOAD hook / fault after fsync | data present after reopen |
| Crash before fsync | inject fault before fsync | data absent if no ACK |
| Torn last record | truncate WAL by 3 bytes | recovery truncates; prefix intact |
| Crash during compaction | kill mid-snapshot write | old manifest valid |
| Double recovery | reopen twice | idempotent state |
| Group commit partial batch | crash after fsync before index | replay fixes index |

### 9.3 Concurrency tests

```text
test_concurrent_puts_different_keys:
  N threads × 10K random keys → no corruption; all ACKed keys readable

test_concurrent_puts_same_key:
  M threads overwrite key K → final value equals some ACKed put

test_get_during_put:
  readers never see torn/partial values; CRC always valid

test_lock_order_stress:
  ThreadSanitizer / Helgrind clean
```

### 9.4 Property invariants (assert in tests)

```text
∀ ACKed put(k,v): ∃ WAL record (k,v,seq) with valid CRC AND index[k].seq >= seq
∀ key k: index[k].seq == max(seq in WAL for k) after recovery
stored_keys == count of non-tombstone entries with seq > snapshot watermark
```

### 9.5 Edge cases checklist

| Edge | Behavior |
|------|----------|
| Empty key | InvalidArgument |
| Key at max_key_bytes | OK |
| Key at max_key_bytes + 1 | InvalidArgument |
| Value size 0 | OK (empty string) |
| delete then get | None |
| delete then put same key | new seq wins |
| Reopen while another process holds lock | IOError / flock |
| WAL rotation mid-put | atomic within log_mutex |
| Compaction during heavy writes | old WAL retained until manifest swap |
| Recovery with empty datadir | fresh store, next_seq=1 |
| Duplicate recovery after truncate | idempotent |

---

## 10. Interviewer Q&A With Answers

### Q1: Why not just `fwrite` and assume the OS saves you?

**A:** `write()`/`fwrite()` return when data reaches the kernel page cache, not stable storage. Power loss or `kill -9` can lose cached pages. For ACKed durability we append to WAL then `fsync(fd)`. The ACK boundary is after fsync (or group fsync), not after write().

### Q2: Group commit vs `O_SYNC` on every write?

**A:** `O_SYNC` forces durability per write() call — simple but no batching, typically ~1–5 ms per op on NVMe. Group commit batches many records into one fsync, improving throughput 10–50× at the cost of tail latency up to `group_window_ms`. Both achieve RPO=0 if we ACK only after fsync. I'd default to group commit for write-heavy workloads; EVERY_WRITE for lowest latency / debugging.

### Q3: How does this differ from RocksDB WAL + memtable?

**A:** Same core pattern: append-only WAL for durability, in-memory index for fast reads. RocksDB adds immutable memtables, SST levels, bloom filters, and leveled compaction — far more complex. Our MVP is Bitcask-like: hash index + WAL + periodic snapshot. RocksDB optimizes for range scan and write amplification; we optimize for interview clarity and single-key ops.

### Q4: Redo logging or undo logging?

**A:** **Redo logging.** WAL records describe forward operations (PUT/DELETE). Recovery replays them into an empty or snapshot index. We don't need undo because we never overwrite old WAL records in place — append-only. DELETE is a redo record (tombstone), not an undo of prior PUT bytes.

### Q5: Can readers mmap segments while compaction deletes files?

**A:** Not in MVP if we delete aggressively. Production pattern: reference-count open file handles; compaction deletes only when refcnt=0. Or: immutable snapshot files + readers hold generation token; compactor removes files from manifest but unlinks after grace period.

### Q6: Exact bytes covered by CRC?

**A:** CRC32C over `[seq:8 | op:1 | key_len:4 | key | value_len:4 | value]`. Magic and outer length field are not in CRC — length detects truncation before CRC check. Stored CRC is last 4 bytes of record.

### Q7: Should DELETE reclaim disk immediately?

**A:** No — DELETE appends tombstone to WAL and marks index entry deleted. Old value bytes remain in WAL until compaction/snapshot rewrites only live keys and truncates old WAL. Immediate reclaim would require random rewrite — violates append-only durability story.

### Q8: Can you lose data with flush() but no fsync?

**A:** Yes. `flush()` typically means fflush() — userspace buffer to kernel. Without fsync, power loss can still lose data. Our `flush()` API explicitly forces group commit fsync, not merely fflush.

### Q9: What if seq numbers collide after crash?

**A:** On recovery, scan all records and set `next_seq = max(seq) + 1`. Persist `next_seq` in manifest after compaction. Never reuse seq — it defines LWW ordering.

### Q10: Why log_mutex AND index lock — why not one lock?

**A:** Single global lock is correct but serializes all puts and gets. Separating allows concurrent gets (index read lock) while one writer fsyncs. Critical rule: index write happens after durable log; lock order prevents inversion. For MVP interview, a single `RWLock` (writes exclusive) is acceptable if you explain the upgrade path.

### Q11: fsync on ext4 vs APFS?

**A:** Both honor fsync for file data on properly configured storage. ext4: journal mode affects metadata; use fsync on WAL fd. APFS: copy-on-write helps atomicity of replace; still fsync file before rename for manifest publish. Directory fsync after rename is recommended on both. Don't rely on platform-specific "safe without fsync" folklore.

### Q12: How would you add prefix scan?

**A:** Replace hash index with sorted map (std::map, skip list) or maintain separate sorted index. WAL replay still works; compaction writes sorted snapshot. Cost: O(log N) insert vs O(1). Mention as Phase 2 — not MVP.

### Q13: Detect silent bitrot?

**A:** CRC on read catches corruption. Background scrubber re-reads WAL/snapshot blocks, verifies CRC, alerts on mismatch. Requires backup/replica for repair — out of single-node MVP scope but worth mentioning.

### Q14: Encrypt values at rest?

**A:** Encrypt value bytes before append; store ciphertext in WAL. CRC covers ciphertext. Key management via envelope encryption (KEK/DEK) — Phase 2. Index still maps key → location; encryption transparent to index structure.

### Q15: Integrate with persistent LRU cache on top?

**A:** Lower layer is this KV store (durability). Upper layer cache calls get/put; on put ACK from KV store, update cache. Cache eviction does not delete from KV unless explicit delete API. See `persistent-inmemory-cache-lld-system-design.md` for eviction + WAL ordering above this store.

**Common traps**

| Trap | Strong answer |
|------|---------------|
| "Write to file = durable" | fsync / group commit |
| Jump to Raft | prompt is single-node |
| Ignore torn writes | length + CRC + truncate |
| Update map then log | order is log then map |
| ACK before fsync | violates durability contract |

---

## 11. Wrap-Up

**Design summary**

- Append-only **WAL** with **length + CRC32C** for torn-tail detection and truncation.  
- **ACK after fsync** — `EVERY_WRITE` or batched `GROUP_COMMIT`.  
- **MemIndex** rebuilt on recovery; snapshot/compaction bounds WAL growth.  
- Strict **lock order**: `log_mutex` before index write; reads avoid log lock.  
- **Crash-point matrix** drives test design; fsync folklore stated precisely.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Hash index + WAL | LSM levels, bloom filters |
| RWLock / log_mutex | Key striping + immutable memtables |
| Snapshot compaction | Background leveled compaction |
| Bytes API | Typed serializers, column families |

**Options defaults**

```text
max_key_bytes = 4096
max_value_bytes = 1_048_576
sync_mode = GROUP_COMMIT
group_window_ms = 2
wal_rotate_bytes = 64 MiB
compaction_threshold_ratio = 4.0
```

**Metrics**

```text
put_latency_ms{quantile}, fsync_latency_ms, wal_bytes, live_bytes
recovery_ms, compaction_seconds, corruption_count
```

**Top risks**

1. Publishing index before fsync  
2. Forgetting directory fsync after manifest rename  
3. Compaction deleting live WAL before manifest publish  
4. Deadlock from inverted lock order (index → log)

**Interview timing (45 min)**

| Min | Focus |
|-----|-------|
| 0–5 | Clarify API + durability contract |
| 5–12 | WAL record format on board |
| 12–20 | Write path + SyncMode |
| 20–28 | Recovery + torn write truncate |
| 28–35 | Lock order + concurrency |
| 35–42 | Compaction + crash matrix |
| 42–45 | Tests + one tradeoff |

---

*End of LLD prep.*
