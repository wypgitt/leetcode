# LLD: Durable Append-Only Event Writer

> **Focus areas:** Append-only log · CRC records · Group commit · committed_seq watermark · Tail readers · Segment rotation · Recovery truncate · Concurrent producers
> **Style:** LLD interview (clarify → APIs → classes → invariants → pseudocode → race analysis → failure modes → tests → Q&A with answers)
> **Quality bar:** ACK only after durable commit per policy; readers never see torn records; recovery truncates incomplete tail
> **Interview theme:** Databricks — WAL / audit log / transaction log segment

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Core Data Structures & Algorithms](#4-core-data-structures--algorithms)
5. [Concurrency Invariants & Lock Order](#5-concurrency-invariants--lock-order)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Race Analysis & Linearization Points](#7-race-analysis--linearization-points)
8. [Failure Modes & Recovery](#8-failure-modes--recovery)
9. [Tests & Edge Cases](#9-tests--edge-cases)
10. [Scalability Notes (Single-Node)](#10-scalability-notes-single-node)
11. [Wrap-Up](#11-wrap-up)
12. [Deeper Interview Q&A (With Answers)](#12-deeper-interview-qa-with-answers)
13. [Appendices](#13-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: Design an **append-only durable event log** with CRC-protected records, concurrent producers, group commit batching, tail readers blocked until new commits, segment rotation, and recovery that truncates torn writes at the log tail.

### 1.0 What this is / is not

| Dimension | This design | Not in scope |
|-----------|-------------|--------------|
| Scope | Single-node append log | Distributed Kafka cluster |
| Access | Append + tail read | Random update/delete in place |
| Durability | Group commit + fsync batches | Memory-only queue |
| Databricks lens | WAL segment / delta log file | Full table format |

### 1.1 Clarifying questions

| # | Question | Typical answer | Design impact |
|---|----------|----------------|---------------|
| F1 | Record format? | Length + payload + CRC32 | Detect torn tail |
| F2 | Producers? | Many threads append | Serialize append path |
| F3 | Readers? | Tail followers only | Block on `committed_seq` |
| F4 | Group commit? | Batch fsync every N ms or M bytes | Throughput vs latency |
| F5 | Rotation? | New segment file at size threshold | Pointer file `CURRENT` |
| F6 | Recovery? | Scan segments; truncate bad tail | Set `nextSeq` watermark |
| F7 | Ordering? | Total order by monotonic sequence | No gaps in committed prefix |
| F8 | Max record size? | 1 MiB | Reject oversize at append |
| F9 | ACK semantics? | Return after record durable per policy | Wait on commit future |
| F10 | Reader start? | `LATEST` or explicit seq | Catch-up from committed watermark |
| F11 | Crash during rotate? | Old segment complete; new may be partial | fsync order + recovery |
| F12 | Empty payload? | Allowed (heartbeat records) | len=0 valid |

**MVP scope:**

1. Append assigns monotonic `seq`; encodes `[magic|seq|len|payload|crc]`.
2. **GroupCommitter** batches fsync; advances **`committed_seq`** watermark.
3. **TailReader** reads up to `committed_seq`; blocks on condition for new commits.
4. **SegmentRotator** rolls to `events-NNNNNN.log` at size limit after fsync.
5. **Recovery** scans in order, verifies CRC, truncates torn last record.
6. Concurrent producers **serialize** on `appendMutex` (single-writer to active segment buffer).

### 1.2 Scope repeat-back

> Append-only durable event log: CRC records, group commit with `committed_seq` watermark, concurrent producers serialized on append lock, tail readers block until commit, segment rotation, recovery truncates incomplete tail record.

### 1.3 Core invariants

```text
I1. Every ACKed append has a complete record (header+payload+CRC) fsync'd per group commit policy.
I2. TailReaders observe only records with seq <= committed_seq; never torn bytes.
I3. Sequence numbers are strictly increasing; committed prefix has no holes.
I4. Recovery truncates any incomplete or CRC-failing tail before serving traffic.
I5. Rotation fsync-closes current segment before switching CURRENT pointer.
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class DurableEventWriter implements Closeable:
  static open(Path logDir, Options opts) -> DurableEventWriter

  AppendResult append(byte[] payload) throws IOException
  void flush() throws IOException              // force group commit now
  TailReader newTailReader(ReaderStart start)
  long committedSequence()                     // watermark
  void close()

class TailReader:
  LogRecord next(long timeoutMs) throws IOException
  long currentSequence()                       // last delivered seq

class LogRecord:
  long sequence
  byte[] payload
  long wallTimeNanos

class AppendResult:
  long sequence
  long byteOffsetInSegment

class ReaderStart:
  enum { BEGINNING, LATEST, AT_SEQUENCE }
  long sequence   // when AT_SEQUENCE

class Options:
  long segmentMaxBytes = 128 * 1024 * 1024
  int groupCommitMaxBytes = 1024 * 1024
  long groupCommitMaxIntervalMs = 5
  int maxRecordBytes = 1024 * 1024
  boolean syncAppend = true                    // wait for commit before return
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
| Durability | `append()` returns only after record ≤ `committed_seq` and batch fsync'd (default) |
| Total order | Sequences monotonic; committed set is prefix `[1..committed_seq]` |
| Reader safety | No partial records visible |
| Concurrent append | Thread-safe; linearizable seq assignment |
| Recovery | Reopen rebuilds state; truncates torn tail |
| Rotation | Seq continuous across segment boundary |

### 2.3 Error model

```text
IOException         — disk full, fsync failure
InvalidArgument     — null payload disallowed if spec says; oversize payload
ClosedException     — after close
CorruptionError     — CRC fail mid-file (non-tail) — fatal, manual intervention
TimeoutException    — TailReader.next timeout
```

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Responsibility |
|-------|----------------|
| `DurableEventWriter` | Lifecycle, append API, reader factory |
| `SegmentWriter` | Encode record, append to active segment buffer + fd |
| `LogRecordEncoder` | `[magic|seq|len|payload|crc32]` layout |
| `SequenceGenerator` | `nextSeq` atomic counter |
| `GroupCommitter` | Batch queue, fsync loop, advance `committed_seq` |
| `CommitNotifier` | `Condition` broadcast to TailReaders |
| `TailReader` | Follows watermark; reads from segment files |
| `SegmentRotator` | Size check, fsync, open next segment |
| `RecoveryManager` | Scan, CRC verify, truncate, rebuild watermarks |
| `Manifest` | `CURRENT` pointer file, segment index |

### 3.2 ASCII architecture

```text
Producer threads
       │
       ▼ (appendMutex serializes)
  SegmentWriter ──encode──► active segment buffer ──► fd.write
       │                           │
       │ register(seq)             │
       ▼                           ▼
  GroupCommitter ◄── batch full / timer
       │
       ├── fd.fsync()
       ├── committed_seq = max seq in batch
       └── CommitNotifier.signalAll()
                 │
                 ▼
           TailReader.next() unblocks
```

### 3.3 On-disk layout

```text
logDir/
  CURRENT                 # text: active segment filename
  events-000001.log
  events-000002.log
  ...

Segment file (append-only):
  [record][record][record]...
```

---

## 4. Core Data Structures & Algorithms

### 4.1 Record binary layout

```text
Offset  Size  Field
0       4     magic = 0xEVNT (constant)
4       8     sequence (int64, little-endian)
12      4     payload_length (uint32)
16      L     payload bytes
16+L    4     crc32 of bytes [4 .. 16+L)  // seq+len+payload

Total record size = 20 + L
```

**CRC scope:** `sequence || payload_length || payload` — detects torn length or partial payload.

### 4.2 In-memory commit state

```text
atomic/long nextSeq              // next sequence to assign (starts at 1 after recovery)
volatile long committed_seq      // max seq durable on disk
volatile long assigned_seq       // max seq written to fd (may be > committed)

GroupCommitBatch:
  long firstSeq
  long lastSeq
  int byteCount
  List<CompletableFuture<Void>> waiters
```

### 4.3 Group commit trigger

```text
on append registered:
  batch.byteCount += recordSize
  batch.lastSeq = seq
  if batch.byteCount >= groupCommitMaxBytes:
    signal committer
  if now - batchStart >= groupCommitMaxIntervalMs:
    signal committer
```

### 4.4 Segment rotation

```text
if currentSegmentBytes + recordSize > segmentMaxBytes:
  groupCommitter.flushSync()           // fsync pending including this record
  fsync and close current fd
  newName = events-{N+1:06d}.log
  open new fd append-only
  atomic write CURRENT tmp + rename
  readers follow CURRENT for seq > old segment max
```

### 4.5 TailReader indexing

```text
TailReader holds:
  long readSeq                    // next seq to deliver (starts at start+1)
  SegmentCursor cursor            // file + offset for readSeq

SegmentIndex maps seq ranges → (file, baseOffset)  // built at recovery
```

### 4.6 Recovery algorithm (high level)

```text
1. List segment files in numeric order
2. committed = 0; nextSeq = 1
3. For each segment:
     offset = 0
     while can read header:
       if incomplete header or payload: truncate at offset; goto done
       if crc fail: truncate at offset; goto done
       committed = record.seq; offset += recordSize
     if truncated: rewrite segment file length
4. nextSeq = committed + 1
5. Open or create CURRENT segment for append
```

### 4.7 Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| append (amortized) | O(L) + O(fsync/batch) | L = payload size |
| group commit | O(batch bytes) fsync | dominant cost |
| tail read (ready) | O(L) | sequential read |
| recovery | O(total log bytes) | startup once |

---

## 5. Concurrency Invariants & Lock Order

### 5.1 Shared state

| State | Protection |
|-------|------------|
| Append path (encode + fd write + batch register) | `appendMutex` |
| `GroupCommitter` batch list | `commitMutex` |
| `committed_seq` | updated under `commitMutex`; read volatile |
| `TailReader.readSeq` | reader-local; no lock |
| Segment rotation | `appendMutex` (exclusive with append) |
| Reader registry | `CopyOnWriteArrayList` or synchronized set |

### 5.2 Lock order

```text
appendMutex → (release) → committer may fsync without appendMutex
Never hold appendMutex during fsync — blocks all producers.

Rotation: appendMutex → flush committer → fsync → switch fd → release
```

### 5.3 Invariants table

| # | Invariant |
|---|-----------|
| I1 | Seq assigned under appendMutex before bytes hit fd. |
| I2 | `committed_seq` advances only after successful fsync of all records ≤ seq. |
| I3 | TailReader delivers record only if `seq <= committed_seq`. |
| I4 | At most one torn record at file tail; recovery truncates it. |
| I5 | Rotation never cuts a record across segments — rotate only between records. |
| I6 | Group commit never ACKs batch without including fsync completion. |

### 5.4 Producer vs reader visibility

```text
Happens-before: fsync completes → committed_seq store → CommitNotifier.signal
Readers read committed_seq after wakeup; load record from disk (or shared read buffer)
```

---

## 6. Algorithms & Pseudocode

### 6.1 open / recovery

```text
function open(logDir, opts):
  RecoveryManager.recover(logDir) → (committed_seq, nextSeq, segmentIndex)
  writer = new DurableEventWriter(...)
  writer.committed_seq = committed_seq
  writer.nextSeq = nextSeq
  writer.segment = openOrCreateCurrent(logDir)
  writer.startGroupCommitterThread()
  return writer
```

### 6.2 append(payload)

```text
function append(payload):
  validate len <= maxRecordBytes
  if closed: throw ClosedException

  appendMutex.lock()
  try:
    seq = nextSeq.getAndIncrement()
    encoded = LogRecordEncoder.encode(seq, payload, now())
    maybeRotateBeforeWrite(len(encoded))
    segmentWriter.write(encoded)           // buffered write to fd
    assigned_seq = seq
    future = groupCommitter.register(seq, encoded.length)
  finally:
    appendMutex.unlock()

  if opts.syncAppend:
    future.get()                         // waits until committed_seq >= seq
  return AppendResult(seq, offset)
```

### 6.3 GroupCommitter loop

```text
function committerLoop():
  while !stopped:
    batch = waitForBatch(timeout = groupCommitMaxIntervalMs)
    if batch empty: continue

    commitMutex.lock()
    try:
      segmentWriter.flushBufferToKernel()  // write() not fsync yet
      fd.fsync()
      committed_seq = batch.lastSeq
      completeAll(batch.waiters)
      CommitNotifier.signalAll()
      resetBatch()
    catch IOException e:
      failAll(batch.waiters, e)
      writer.enterStickyFailure(e)
    finally:
      commitMutex.unlock()
```

### 6.4 register(seq, bytes)

```text
function register(seq, bytes):
  commitMutex.lock()
  try:
    currentBatch.add(seq, bytes, future)
    if shouldFlush(currentBatch):
      commitCond.signal()
    return future
  finally:
    commitMutex.unlock()
```

### 6.5 TailReader.next(timeoutMs)

```text
function next(timeoutMs):
  deadline = mono + timeoutMs
  lock(readerLock):
    while true:
      if readSeq < committed_seq:
        if readSeq not in current segment:
          cursor = segmentIndex.locate(readSeq)
        record = readAndVerifyCrc(cursor, readSeq)
        readSeq++
        return record
      if readSeq > committed_seq:
        throw IllegalState   // bug
      remaining = deadline - mono
      if remaining <= 0: throw TimeoutException
      CommitNotifier.await(remaining)
```

### 6.6 readAndVerifyCrc

```text
function readAndVerifyCrc(cursor, expectedSeq):
  header = read(cursor, 16)
  if incomplete: throw EOFInternal  // should not happen if seq <= committed
  len = parseLen(header)
  body = read(cursor, len + 4)
  if crc mismatch: throw CorruptionError
  if parseSeq(header) != expectedSeq: throw OrderingError
  return LogRecord(...)
```

### 6.7 rotate()

```text
function maybeRotateBeforeWrite(incomingBytes):
  // caller holds appendMutex
  if segment.bytes + incomingBytes <= segmentMaxBytes:
    return
  groupCommitter.flushSync()    // includes pending records
  segment.fsync(); segment.close()
  newId = segment.id + 1
  newSegment = Segment.open(logDir, newId)
  writeCurrentPointerAtomically(newSegment.name)
  segment = newSegment
```

### 6.8 recovery scan (detailed)

```text
function recoverSegment(file):
  offset = 0
  fileLen = file.length()
  lastGoodOffset = 0
  lastGoodSeq = 0

  while offset + 20 <= fileLen:
    magic = readInt(offset)
    if magic != MAGIC: break
    seq = readLong(offset+4)
    len = readInt(offset+12)
    recordEnd = offset + 20 + len
    if recordEnd > fileLen: break          // torn record — incomplete payload/CRC
    crcStored = readInt(recordEnd - 4)
    crcCalc = crc32(file, offset+4, 12+len)
    if crcStored != crcCalc: break       // torn or corrupt tail
    lastGoodSeq = seq
    lastGoodOffset = recordEnd
    offset = recordEnd

  if lastGoodOffset < fileLen:
    file.truncate(lastGoodOffset)
  return lastGoodSeq
```

### 6.9 close()

```text
function close():
  appendMutex.lock()
  closed = true
  appendMutex.unlock()

  groupCommitter.stopAndFlushSync()
  segment.fsync(); segment.close()
  CommitNotifier.signalAll()   // wake readers to observe closed
```

### 6.10 flush() (public)

```text
function flush():
  groupCommitter.flushSync()   // force immediate fsync of pending batch
```

---

## 7. Race Analysis & Linearization Points

### 7.1 Concurrent producers — serialize append

| Time | Thread P1 | Thread P2 |
|------|-----------|-----------|
| t0 | appendMutex.lock | blocked |
| t1 | seq=5, write fd | blocked |
| t2 | register batch | blocked |
| t3 | unlock | lock |
| t4 | | seq=6, write fd |

**Linearization:** mutex order defines seq assignment order. No duplicate seq.

### 7.2 Reader vs committer

| Time | Committer | TailReader R |
|------|-----------|--------------|
| t0 | fsync in progress | readSeq=10, committed_seq=9, wait |
| t1 | fsync done; committed_seq=12 | sleeping |
| t2 | signalAll | wake |
| t3 | | sees committed_seq=12; reads 10,11,12 |

**Bug if reader reads before fsync:** observes record then crash loses it — **violates I1**. Fix: reader predicate `readSeq <= committed_seq` only.

### 7.3 Append returns before commit (async mode)

If `syncAppend=false`, `append()` linearizes at fd write, not durability. Document API. Default `syncAppend=true` for interview.

### 7.4 Rotation vs reader

Reader holds cursor in segment-000001.log. Rotator closes 000001 after fsync, opens 000002.

Reader finishing seq 1000 in file 1 while seq 1001 starts file 2: **SegmentIndex** maps seq → file; reader relocates cursor when `readSeq` crosses boundary.

Race: reader opens file 1 while rotator renames — open segments read-only by path; rotation only after fsync so file 1 immutable.

### 7.5 Crash during torn write

Crash after writing length field but before payload:

```text
... [magic ok][seq ok][len=100][40 bytes partial] EOF
```

Recovery: `recordEnd > fileLen` → truncate to offset before this record; `committed_seq` from prior record.

### 7.6 Group commit partial batch

Two appends in batch; crash after fsync — both durable. Crash before fsync — neither ACKed if syncAppend; reader never sees them; recovery truncates if partial write torn.

### 7.7 committed_seq watermark monotonicity

Commit thread must assign `committed_seq = batch.lastSeq` atomically after fsync — never regress. Single committer thread simplifies.

---

## 8. Failure Modes & Recovery

| Scenario | On failure | Recovery |
|----------|------------|----------|
| Crash mid-record | Torn tail | Truncate to last good CRC |
| Crash after fd write, before fsync | Record not ACKed | Truncate if torn; else full record replay |
| Crash during rotate | Old segment complete | Open CURRENT; truncate new if partial |
| CRC mismatch mid-file | Data corruption | Fatal — restore from replica (out of MVP) |
| Disk full | append throws | No ACK; sticky failure optional |
| Slow reader | Segments accumulate | Retention / backpressure Phase 2 |
| Commit thread die | Appends hang on future | Health check; fail writer |

### 8.1 Recovery narrative (whiteboard)

1. Start from oldest segment `events-000001.log`.
2. Scan records sequentially; stop at first incomplete or CRC failure.
3. Truncate file at last good offset.
4. Repeat for all segments; global `committed_seq` = max seq across segments.
5. Set `nextSeq = committed_seq + 1`.
6. Open `CURRENT` for new appends or create if missing.

### 8.2 CURRENT pointer atomicity

```text
write CURRENT.tmp
fsync CURRENT.tmp
rename CURRENT.tmp → CURRENT
fsync directory
```

Crash leaves old CURRENT — safe. Never points to half-written segment name.

---

## 9. Tests & Edge Cases

### 9.1 Functional tests

| # | Test | Expected |
|---|------|----------|
| T1 | Single append + reader | Round-trip payload |
| T2 | 1000 records order | seq 1..1000 in order |
| T3 | Empty payload | len=0, CRC valid |
| T4 | Max size payload | Accepted |
| T5 | Max+1 payload | InvalidArgument |
| T6 | Recovery clean close | All records readable |
| T7 | Rotation at boundary | seq continuous across files |
| T8 | Reader LATEST | Skips history; sees new only |
| T9 | flush() forces commit | Reader unblocks without batch fill |

### 9.2 Concurrency tests

```text
test_concurrent_append_unique_seq():
  32 threads × 1000 appends
  assert seq set size == 32000
  assert committed_seq == 32000 after flush

test_reader_never_sees_uncommitted():
  inject delay in committer fsync
  reader blocked until commit; never read partial file
```

### 9.3 Recovery / torn tail tests

| Setup | Expected |
|-------|----------|
| Truncate last 3 bytes of segment | Recovery truncates last record |
| Corrupt CRC at tail | Same |
| Corrupt CRC mid-file | CorruptionError (policy) |
| Kill during append simulation | Reopen; prefix intact |

### 9.4 Group commit timing

```text
test_interval_commit:
  small appends, batch bytes high, interval 50ms
  append returns within ~interval even if batch not full
```

---

## 10. Scalability Notes (Single-Node)

| Knob | Effect |
|------|--------|
| `groupCommitMaxBytes` ↑ | Higher throughput; longer latency |
| `groupCommitMaxIntervalMs` ↓ | Lower latency; more fsyncs |
| `segmentMaxBytes` | Balance file count vs recovery scan |
| NVMe vs HDD | fsync rate dominates |

**Single-partition total order** — like one Kafka partition. Scale-out = shard logs by partition key (Phase 2), not in this LLD.

**Bottleneck:** `appendMutex` + disk fsync. Mitigation: group commit (already), async append API for fire-and-forget producers with callback.

---

## 11. Wrap-Up

**Design summary**

- Append-only segments with CRC records.
- Producers serialized on `appendMutex`; seq monotonic.
- GroupCommitter batches fsync; `committed_seq` watermark.
- TailReaders block until `readSeq <= committed_seq`.
- Rotation between records after fsync.
- Recovery truncates torn tail; rebuilds watermarks.

**Top risks**

1. ACK before fsync (breaks durability story).
2. Reader reads beyond committed watermark.
3. Rotation without fsync — gap or torn segment switch.

**MVP vs later**

| MVP | Phase 2 |
|-----|---------|
| Single log directory | Partitioned logs |
| Blocking tail reader | Snapshot + catch-up |
| Retention manual | Checkpoint-driven deletion |

---

## 12. Deeper Interview Q&A (With Answers)

**Q1: How is this different from Kafka?**

**A:** Single-node, single partition total order, no ZooKeeper/broker cluster. Same ideas: append log, sequential read, batching. This LLD focuses on fsync group commit and recovery truncate on one machine.

**Q2: Why CRC over entire record?**

**A:** Detects torn writes after crash (partial length/payload) and bit rot. Recovery truncates at first failure at tail; mid-file failure indicates corruption.

**Q3: Why serialize appends if group commit already batches?**

**A:** Seq assignment and fd write ordering must be deterministic without gaps. Parallel writes to same fd complicate ordering and torn buffer flushes. Single append lock is clear; Phase 2 can use a lock-free queue feeding one writer thread.

**Q4: What is `committed_seq` vs `assigned_seq`?**

**A:** `assigned_seq` — last seq written to OS buffers. `committed_seq` — last seq fsync'd and safe for readers/ACK. Readers and sync append wait on `committed_seq`.

**Q5: Can readers lag indefinitely?**

**A:** Yes — tail follow is intentional. Retention policy must not delete segments readers still need (Phase 2).

**Q6: How does group commit improve throughput?**

**A:** One fsync amortizes many appends. 5 ms window × 10k small appends → one disk sync instead of 10k.

**Q7: Recovery truncate vs mid-file CRC fail?**

**A:** Tail truncate assumes crash during write. Mid-file CRC fail implies corruption — cannot silently truncate middle; abort and restore backup.

**Q8: How to fence old writers after reopen?**

**A:** Single process MVP — file lock on logDir. Multi-process: store epoch in manifest; reject appends with stale epoch.

**Q9: Empty segment after truncate?**

**A:** Valid — `committed_seq=0`, `nextSeq=1`. Reader at BEGINNING blocks until first commit.

**Q10: Does rotation create seq gap?**

**A:** No — seq is global across segments. Rotation is invisible to seq ordering.

**Q11: TailReader at LATEST after recovery?**

**A:** `readSeq = committed_seq + 1` — waits for next append; does not replay history.

**Q12: Integration with Databricks WAL?**

**A:** Transaction log records appended as events; group commit matches delta log flush intervals; segment files align with checkpoint boundaries.

---

## 13. Appendices

### A. Record hex example

```text
magic     EVNT
seq       0x000000000000000A  (10)
len       0x00000003
payload   41 42 43            ("ABC")
crc32     0x????????
```

### B. Complexity summary

| Operation | Time |
|-----------|------|
| append | O(L) amortized + fsync/batch |
| next (ready) | O(L) |
| recovery | O(total bytes) |

### C. Thread-safety checklist

- [ ] appendMutex for seq + fd write
- [ ] committed_seq after fsync only
- [ ] Reader waits on committed watermark
- [ ] Rotation fsync before CURRENT update
- [ ] Recovery truncate before accept appends

### D. Whiteboard timing (45 min)

| Phase | Minutes |
|-------|---------|
| Clarify + record format | 5 |
| API + watermark | 8 |
| append + group commit pseudocode | 12 |
| Recovery truncate | 8 |
| Tail reader + rotation | 7 |
| Q&A | 5 |

---

*End of LLD prep.*
