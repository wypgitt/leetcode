# LLD: Thread-Safe Buffered Writer

> **Focus areas:** Double-buffer swap · Background flush thread · writeMutex + conditions · FsyncPolicy · Backpressure · close() lifecycle · Large-write bypass
> **Style:** LLD interview (clarify → APIs → classes → invariants → pseudocode → race analysis → failure modes → tests → Q&A with answers)
> **Quality bar:** Explicit flush/fsync semantics; no data loss after close(); backpressure when both buffers full; only flusher touches OutputStream
> **Interview theme:** Databricks — storage/concurrency LLD (executor spill files, WAL batching)

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

Goal: Design a **thread-safe BufferedWriter** wrapping `OutputStream` / POSIX fd with a background flush thread, double-buffer swapping, configurable fsync, backpressure, and deterministic `close()`.

### 1.0 What this is / is not

| Dimension | This design | Not in scope |
|-----------|-------------|--------------|
| Scope | Single output stream wrapper | Full logging framework |
| Threads | Many producer threads + one flusher | Single-threaded only |
| Durability | Configurable fsync policy | Always sync every byte |
| Databricks lens | Executor spill / local WAL batching | Distributed object store |

### 1.1 Clarifying questions (say these first)

| # | Question | Typical answer | Design impact |
|---|----------|----------------|---------------|
| F1 | Underlying sink? | `FileOutputStream` / POSIX fd | Delegate `write` + `fsync` |
| F2 | Buffer size? | Fixed 64 KiB–4 MiB | Two equal-sized byte buffers |
| F3 | Thread safety? | Multiple threads call `write()` | `writeMutex` + condition variables |
| F4 | Flush thread? | Dedicated background thread drains flushing buffer | Swap when active full |
| F5 | Backpressure? | Block writers when both buffers busy | Document timeout option |
| F6 | fsync policy? | NEVER / ON_FLUSH / PERIODIC / ALWAYS | Latency vs durability tradeoff |
| F7 | `close()`? | Flush remaining, fsync per policy, join thread | Idempotent close |
| F8 | Partial application records? | Each `write()` copy is atomic into buffer | No torn user records inside buffer |
| F9 | Writes larger than buffer? | Bypass buffer; direct to sink | Avoid double copy |
| F10 | Error propagation? | First IO error sticky | All subsequent ops fail |
| F11 | Interrupt handling? | `write()` responds to thread interrupt | Restore interrupt flag |
| F12 | Metrics? | bytes_buffered, flush_count, blocked_time | Required for production |

**MVP scope:**

1. Double-buffer: **active** (writers append) + **flushing** (background drains).
2. `write(byte[])` copies into active buffer under `writeMutex`; swap when full.
3. Background **FlushWorker** writes flushing buffer to `OutputStream`, optional fsync.
4. **Backpressure:** writers block when active full and flushing not yet consumed.
5. `flush()` waits until active empty and flush thread idle.
6. `close()` sets closed flag, drains all data, joins flusher, closes sink.

**Out of MVP:** Compression, encryption, mmap I/O, multiple sink sharding.

### 1.2 Scope repeat-back (30 seconds)

> Thread-safe buffered writer: double-buffer swap, dedicated flush thread, four fsync policies, backpressure when both buffers full, large writes bypass the buffer, `close()` joins the flusher and surfaces sticky IO errors.

### 1.3 Core invariants (write on board before coding)

```text
I1. After successful close(), every byte accepted by write() before close is on the underlying sink per fsync policy.
I2. At most one thread writes to the underlying OutputStream — the FlushWorker.
I3. Swap of active ↔ flushing is atomic under writeMutex; writers never touch flushing while it holds data.
I4. First IOException is sticky; subsequent write/flush/close throw that error (or wrap it).
I5. Large writes (len > bufferSize) bypass the internal buffer after draining active.
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class BufferedWriter implements Closeable:
  BufferedWriter(OutputStream out, Options opts)

  void write(byte[] data, int off, int len) throws IOException
  void write(byte b) throws IOException
  void flush() throws IOException
  void close() throws IOException

class Options:
  int bufferSize = 65536                    // each of two buffers
  FsyncPolicy fsyncPolicy = ON_FLUSH
  long periodicFsyncIntervalMs = 1000       // PERIODIC only
  long writeTimeoutMs = Long.MAX_VALUE      // backpressure wait
  boolean fairLock = false                  // ReentrantLock fairness

enum FsyncPolicy:
  NEVER       // no fsync; crash may lose buffered bytes
  ON_FLUSH    // fsync after each buffer drain + flush()/close()
  PERIODIC    // fsync at most every T ms if pending data
  ALWAYS      // fsync after every buffer drain (slowest)
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
| Thread-safe writes | Concurrent `write()` from multiple threads |
| Byte ordering | Bytes appear on sink in program order of successful writes (inter-thread order follows lock acquisition) |
| `close()` durability | `close()` flushes all buffered bytes before returning |
| Single sink writer | Only FlushWorker calls `out.write()` |
| Backpressure | `write()` blocks (or times out) when active full and flushing occupied |
| Error sticky | First `IOException` poisons writer; later ops throw |
| Large-write bypass | Writes with `len > bufferSize` go direct to sink after active drain |
| Idempotent close | Second `close()` is no-op (or throws `ClosedException` — pick one, test it) |

### 2.3 Error model

```text
IOException        — underlying I/O failure (sticky after first)
ClosedException    — write/flush after close completed
TimeoutException   — write blocked longer than writeTimeoutMs
InvalidArgument    — negative len, null buffer, off+len overflow
InterruptedIOException — thread interrupted while waiting on condition
```

### 2.4 Durability semantics by policy

| Policy | Caller observes | Crash window |
|--------|-----------------|--------------|
| NEVER | Fast returns; data may sit in OS page cache | Lose unflushed buffer + maybe kernel cache |
| ON_FLUSH | `flush()` / `close()` ⇒ durable on local disk | Lose bytes since last drain unless flushed |
| PERIODIC | Bounded loss ≤ interval + one buffer | Lose since last periodic fsync |
| ALWAYS | Each drained buffer durable | Minimal; only in-flight active buffer |

---

## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class / module | Responsibility |
|----------------|----------------|
| `BufferedWriter` | Public API; owns lifecycle, error state, options |
| `ByteBufferSlot` | Fixed-size byte array + write cursor (`pos`) |
| `BufferPair` | Two slots: `active`, `flushing`; tracks which is writable |
| `FlushWorker` | Background thread: drain flushing → `out.write` → fsync |
| `WriteCoordinator` | Holds `writeMutex`, `flushDone`, `workAvailable`, `closed` |
| `FsyncScheduler` | PERIODIC policy timer / last-fsync timestamp |
| `StickyError` | Volatile `IOException firstError` checked on entry |
| `Metrics` | `blocked_writes`, `flush_latency_ms`, `bytes_written` |

### 3.2 ASCII architecture

```text
  Thread-1 ──┐
  Thread-2 ──┼── write() ──► [ writeMutex ] ──► active buffer (pos++)
  Thread-N ──┘                      │                    │
                                    │ active full        │
                                    ▼                    │
                              swap buffers ◄───────────────┘
                                    │
                                    ▼
                            flushing buffer ──signal──► FlushWorker
                                                              │
                                                              ▼
                                                    OutputStream.write()
                                                    optional fsync()
                                                              │
                                    flushDone signal ◄──────────┘
                                    (writers unblock)
```

### 3.3 State machine (buffer occupancy)

```text
States:
  S0: active has space, flushing empty        → writers proceed
  S1: active full, flushing empty              → swap → S2
  S2: active has space, flushing full           → flusher working; writers may fill active
  S3: active full, flushing full (not drained) → BACKPRESSURE: writers wait on flushDone
  S4: closed                                      → reject new writes; drain then join
```

---

## 4. Core Data Structures & Algorithms

### 4.1 Double-buffer layout

```text
class ByteBufferSlot:
  byte[] data          // length = Options.bufferSize
  int pos              // bytes written [0, pos)

class BufferPair:
  ByteBufferSlot active
  ByteBufferSlot flushing
  boolean flushingReady   // true when flushing.pos > 0 and not yet taken by worker

active.remaining() = bufferSize - active.pos
active.full()      = active.pos == bufferSize
flushing.empty()   = flushing.pos == 0
```

**Swap invariant:** swap only when `active.full() && flushing.empty() && !flushingReady`.

### 4.2 Copy into active buffer

```text
function copyIntoActive(src, off, len):
  while len > 0:
    n = min(len, active.remaining())
    System.arraycopy(src, off, active.data, active.pos, n)
    active.pos += n
    off += n; len -= n
    if active.full():
      trySwapAndWakeFlusher()
```

### 4.3 Large-write bypass

When `len > bufferSize`:

```text
1. Hold writeMutex
2. If closed or sticky error → throw
3. Drain active buffer via swap+wait until empty (same as flush partial)
4. Release writeMutex BEFORE direct IO (optional optimization: keep lock to preserve strict ordering — see race section)
5. FlushWorker must not overlap: wait until flushing empty and worker idle
6. out.write(src, off, len) directly
7. applyFsyncPolicy() if ALWAYS or PERIODIC due
8. Reacquire lock for return
```

**Why bypass:** copying a 10 MiB write into 64 KiB buffer would require many swaps and an extra memcpy.

### 4.4 fsync policy implementation

```text
function applyFsyncAfterDrain():
  switch fsyncPolicy:
    NEVER:    return
    ON_FLUSH: out.fsync()
    PERIODIC: if now - lastFsyncMs >= interval: out.fsync(); lastFsyncMs = now
    ALWAYS:   out.fsync()
```

PERIODIC also runs a watchdog in FlushWorker loop: if data pending and interval elapsed, fsync even if buffer not full (requires tracking `dirtySinceLastFsync`).

### 4.5 Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| `write` (fits in active) | O(n) copy | n = len |
| `write` (fills buffer) | O(bufferSize) + wait | may trigger swap |
| `write` (large bypass) | O(n) IO | no extra copy |
| `flush` | O(buffered) + IO | waits for worker |
| `close` | O(buffered) + join | one-time |

Space: **2 × bufferSize** heap + one flush thread stack.

---

## 5. Concurrency Invariants & Lock Order

### 5.1 Shared state

| Field | Protection | Notes |
|-------|------------|-------|
| `active`, `flushing` cursors | `writeMutex` | Writers + coordinator |
| `flushingReady`, worker idle flag | `writeMutex` | Signals conditions |
| `closed` | `writeMutex` | Set once in close |
| `firstError` | write under mutex; read volatile | Sticky IO |
| `FlushWorker` thread handle | main thread only | join in close |

### 5.2 Condition variables

| Condition | Waiters | Signaler | Predicate |
|-----------|---------|----------|-----------|
| `workAvailable` | FlushWorker | writers after swap | `flushingReady \|\| closed` |
| `flushDone` | writers in backpressure, `flush()` | FlushWorker after drain | `flushing.empty() && !flushingReady` |

Always wait in **`while (!predicate)`** loop — spurious wakeups.

### 5.3 Lock order (mandatory — state on whiteboard)

```text
Rule L1: Only one lock: writeMutex (ReentrantLock).
Rule L2: Never call out.write / out.fsync while holding writeMutex.
         FlushWorker: take buffer state under lock → release → IO → reacquire → signal.
Rule L3: close() acquires writeMutex to set closed before join; no invert with worker IO.
Rule L4: checkStickyError() at start of write/flush under lock.
```

**Why release lock before IO:** flusher blocked on disk would stall all writers forever.

### 5.4 Invariants table

| # | Invariant |
|---|-----------|
| I1 | Only FlushWorker invokes `out.write` / `out.fsync`. |
| I2 | `active.pos` and `flushing.pos` mutated only under `writeMutex`. |
| I3 | `flushingReady` implies `flushing.pos > 0`. |
| I4 | Writers block in S3 until worker clears flushing slot. |
| I5 | After `closed=true`, no new bytes accepted; drain proceeds. |
| I6 | Swap exchanges buffer objects or resets cursors — never copies twice. |

---

## 6. Algorithms & Pseudocode

### 6.1 Fields (Java-like)

```text
class BufferedWriter:
  final OutputStream out
  final Options opts
  final ReentrantLock writeMutex
  final Condition workAvailable
  final Condition flushDone
  BufferPair buffers
  volatile IOException stickyError
  volatile boolean closed
  Thread flushThread
  long lastFsyncMs
  boolean dirtySinceLastFsync
```

### 6.2 Constructor — start flusher

```text
BufferedWriter(out, opts):
  validate bufferSize > 0
  this.out = out
  writeMutex = new ReentrantLock(opts.fairLock)
  workAvailable = writeMutex.newCondition()
  flushDone = writeMutex.newCondition()
  buffers = new BufferPair(opts.bufferSize)
  flushThread = new Thread(this::flushWorkerLoop, "buffered-writer-flusher")
  flushThread.setDaemon(false)   // ensure drain on JVM exit if close called
  flushThread.start()
```

### 6.3 write(data, off, len)

```text
function write(data, off, len):
  validate bounds; if len == 0: return
  if len > opts.bufferSize:
    return writeLargeBypass(data, off, len)

  writeMutex.lock()
  try:
    checkClosedAndSticky()
    remaining = len
    cursor = off
    while remaining > 0:
      while active.full():
        trySwapAndWakeFlusher()
        if flushing not drained:
          awaitFlushDoneWithTimeout()
      checkClosedAndSticky()
      chunk = min(remaining, active.remaining())
      copy into active at chunk
      remaining -= chunk
      cursor += chunk
      if active.full():
        trySwapAndWakeFlusher()
  finally:
    writeMutex.unlock()
```

### 6.4 trySwapAndWakeFlusher()

```text
function trySwapAndWakeFlusher():
  // caller holds writeMutex
  if !active.full(): return
  if !flushing.empty() || flushingReady:
    return   // backpressure path will wait
  swap(active, flushing)   // or flip indices + reset pos
  flushingReady = true
  dirtySinceLastFsync = true
  workAvailable.signal()
```

### 6.5 flushWorkerLoop()

```text
function flushWorkerLoop():
  while true:
    writeMutex.lock()
    try:
      while !flushingReady && !closed:
        workAvailable.await()
      if closed && !flushingReady && active empty:
        break   // exit loop
      if !flushingReady:
        // closed: swap remaining active if any
        if active.pos > 0:
          swap active/flushing; flushingReady = true
        else:
          continue
      localBuf = takeFlushingBuffer()   // resets flushing slot; flushingReady=false
    finally:
      writeMutex.unlock()

    try:
      out.write(localBuf.data, 0, localBuf.pos)
      applyFsyncAfterDrain()
      recordMetrics()
    catch IOException e:
      setStickyError(e)

    writeMutex.lock()
    try:
      flushDone.signalAll()
    finally:
      writeMutex.unlock()
```

### 6.6 flush()

```text
function flush():
  writeMutex.lock()
  try:
    checkClosedAndSticky()
    while active.pos > 0 || flushingReady || !flushing.empty():
      if active.pos > 0 && !flushingReady && flushing.empty():
        trySwapAndWakeFlusher()
      awaitFlushDoneWithTimeout()
    if fsyncPolicy == ON_FLUSH || fsyncPolicy == ALWAYS:
      // worker already fsync'd on drains; force if dirty periodic
      forceFsyncIfDirty()
  finally:
    writeMutex.unlock()
```

### 6.7 close()

```text
function close():
  writeMutex.lock()
  if closed:
    writeMutex.unlock(); return
  closed = true
  workAvailable.signalAll()
  writeMutex.unlock()

  flush()                    // drain active + flushing

  writeMutex.lock()
  workAvailable.signalAll()
  writeMutex.unlock()

  flushThread.join()         // worker observes closed and exits

  if stickyError != null:
    try: out.close()
    catch IOException e: addSuppressed
    throw stickyError
  out.close()
```

### 6.8 writeLargeBypass(data, off, len)

```text
function writeLargeBypass(data, off, len):
  writeMutex.lock()
  try:
    checkClosedAndSticky()
    while active.pos > 0 || flushingReady:
      trySwapAndWakeFlusher()
      awaitFlushDoneWithTimeout()
  finally:
    writeMutex.unlock()

  // IO outside lock — worker idle, active empty
  try:
    out.write(data, off, len)
    dirtySinceLastFsync = true
    applyFsyncAfterDrain()
  catch IOException e:
    setStickyError(e); throw e
```

### 6.9 Sticky error helpers

```text
function setStickyError(e):
  writeMutex.lock()
  try:
    if stickyError == null: stickyError = e
    flushDone.signalAll()
    workAvailable.signalAll()
  finally:
    writeMutex.unlock()

function checkClosedAndSticky():
  if stickyError != null: throw stickyError
  if closed: throw new ClosedException()
```

---

## 7. Race Analysis & Linearization Points

### 7.1 Scenario: two writers fill buffer simultaneously

| Time | Thread A | Thread B | active.pos |
|------|----------|----------|------------|
| t0 | lock | blocked | 0 |
| t1 | copy 32 KiB | blocked | 32768 |
| t2 | copy 32 KiB → full | blocked | 65536 |
| t3 | swap, signal | blocked | 0 |
| t4 | unlock | lock | 0 |
| t5 | | copy | 32768 |

**Result:** No lost bytes; order A then B in buffer. **Linearization point:** lock acquisition order for writes that fit in same buffer generation.

### 7.2 Scenario: backpressure (both buffers full)

| Time | Writer W | FlushWorker F |
|------|----------|---------------|
| t0 | fills active, swap | draining flushing |
| t1 | fills active again | still IO |
| t2 | active full, flushingReady | — |
| t3 | wait on flushDone | — |
| t4 | — | completes IO, signalAll |
| t5 | wakes, swap | — |

**Invariant preserved:** writer cannot swap into flushing while F still holds unread data.

### 7.3 Scenario: close() vs in-flight write

```text
close sets closed=true under lock, then flush().
Writer in write(): either completes before closed check or throws ClosedException.
Define: close() waits for flush — any write that started before closed flag may finish copy.
```

Test: thread A blocked in backpressure; main calls close → A must not hang forever (flushDone broadcast + closed).

### 7.4 Scenario: sticky error during flush

Worker catches IO exception → setStickyError → signalAll waiters.
Writers in `awaitFlushDone` wake, check sticky, throw.
Subsequent write/flush/close all fail fast with same exception.

### 7.5 Scenario: large bypass vs flusher

Without draining active first, flusher and main thread could interleave on `OutputStream` — **violates I1**.

**Fix:** large bypass waits until `active.pos == 0 && !flushingReady` under lock before direct write.

### 7.6 PERIODIC fsync race

Writer adds bytes, swap, worker drains but interval not elapsed — no fsync yet.
Crash → records since last fsync lost. **Document** for callers; `flush()` forces fsync when ON_FLUSH/PERIODIC policy requires.

### 7.7 Linearization summary

| Operation | Linearization point |
|-----------|---------------------|
| `write` (buffered) | Successful copy into active under lock |
| `write` (bypass) | Successful `out.write` |
| `flush` | Observing flushing empty and active empty after waits |
| `close` | Setting `closed=true` (reject point for new ops) + join completes |

---

## 8. Failure Modes & Recovery

| Scenario | Behavior | Mitigation |
|----------|----------|------------|
| Process crash before flush | Buffered bytes lost | fsync policy documents window |
| Disk full on flush | Sticky IOException | Propagate; stop accepting writes |
| Slow disk | Writers block (backpressure) | Timeout + metric alert |
| Flush thread dies unexpectedly | Writers block forever | Uncaught handler sets sticky error; join in close |
| Spurious condition wakeup | while-loop predicate | Correctness preserved |
| Double close | Idempotent no-op | Test explicitly |
| Interrupt during await | Exit with InterruptedIOException | Restore interrupt flag |
| Partial OutputStream write | Sticky error; buffer state may be inconsistent | Assume sink handles or mark corrupted |

### 8.1 close() lifecycle diagram

```text
close called
  ├─ lock: closed=true; signal worker
  ├─ flush(): swap active → wait flushDone until all drained
  ├─ signal worker shutdown
  ├─ join(flushThread)
  ├─ if stickyError: close out; rethrow
  └─ out.close()
```

### 8.2 Caller responsibilities

- Call `close()` before process exit for durability.
- Choose fsync policy matching business requirements (audit log → ON_FLUSH or ALWAYS).
- Handle sticky IO: replace sink or abort task.

---

## 9. Tests & Edge Cases

### 9.1 Functional tests

| # | Test | Expected |
|---|------|----------|
| T1 | Single-thread small writes | Coalesced in buffer; one flush on full |
| T2 | `flush()` mid-buffer | Active drained; file length matches |
| T3 | Write exactly `bufferSize` | Single swap; file size correct |
| T4 | Write `bufferSize + 1` | Swap + 1 byte or bypass policy |
| T5 | Write `2 * bufferSize + 100` | Bypass path invoked; no OOM |
| T6 | `close()` without prior flush | All bytes durable per ON_FLUSH |
| T7 | fsync NEVER | No fsync syscall (mock counting) |
| T8 | fsync ALWAYS | fsync after each drain |
| T9 | Empty write | No-op |
| T10 | Second close | Idempotent |

### 9.2 Concurrency tests

```text
test_many_threads_small_writes():
  N=16 threads, each writes 1 MiB in 64-byte chunks
  join all; close()
  assert file.length == N * 1_MiB
  SHA256 matches golden

test_backpressure_no_deadlock():
  slow OutputStream (inject 100ms per write)
  writers still complete; blocked_writes metric > 0

test_TSAN_clean:
  run under ThreadSanitizer 60s — no reports
```

### 9.3 Failure injection

| Injection | Assert |
|-----------|--------|
| IOException on 3rd flush | Sticky; subsequent write throws same |
| Interrupt writer in await | InterruptedIOException |
| Timeout 100ms on saturated buffer | TimeoutException |

### 9.4 Property-based test sketch

```text
@RepeatedTest(200)
random_threads_random_chunk_sizes():
  serial_model = ByteArrayOutputStream()
  parallel BufferedWriter to temp file
  assert file_bytes == serial_model.toByteArray()
```

---

## 10. Scalability Notes (Single-Node)

| Knob | Effect |
|------|--------|
| bufferSize 64 KiB → 4 MiB | Fewer syscalls; higher memory; longer backpressure bursts |
| NEVER fsync | Highest throughput; crash loses data |
| fairLock=true | Fairness among writers; lower throughput |
| Multiple BufferedWriter instances | Scale with partitions (one spill file per thread) |

**Databricks spill context:** sort operators write runs to local SSD; BufferedWriter amortizes fsync across many sort threads writing different files — not one global writer.

**Bottleneck at extreme QPS:** lock contention on `writeMutex`. Mitigation: shard writers per file (already one file per spill run).

---

## 11. Wrap-Up

**Design summary**

- Double-buffer with single FlushWorker — only flusher touches sink.
- `writeMutex` + `workAvailable` + `flushDone` conditions.
- Four fsync policies with explicit durability windows.
- Backpressure when active full and flushing not drained.
- Large writes bypass internal buffer after drain.
- `close()` sets closed, flush, join, sticky IO propagation.

**Top interviewer risks**

1. Calling `out.write` from writer thread (breaks I1).
2. Forgetting `join()` on close (leaked thread, partial data).
3. No sticky error — silent partial failure after first IO error.

**MVP vs later**

| MVP | Phase 2 |
|-----|---------|
| Block backpressure | Drop policy + metric for overload |
| Fixed buffer size | Adaptive buffer sizing |
| File OutputStream | WritableByteChannel / direct buffers |

---

## 12. Deeper Interview Q&A (With Answers)

**Q1: How is this different from `BufferedOutputStream`?**

**A:** `BufferedOutputStream` is not thread-safe and flushes synchronously on the calling thread when the buffer fills. Our design moves IO to a background thread, supports concurrent writers with backpressure, configurable fsync policies, and explicit close/join semantics.

**Q2: When would you pick each fsync policy?**

**A:** NEVER for temporary scratch files where recomputation is cheap. ON_FLUSH for spill files read after task completion. PERIODIC for logs tolerating sub-second loss. ALWAYS for small critical metadata files where latency is acceptable.

**Q3: How do you handle a write larger than the buffer?**

**A:** Drain active (and wait for flushing empty), release lock, write directly to `OutputStream`, apply fsync per policy. Avoids copying large arrays through a small buffer.

**Q4: What if both buffers are full and the disk is slow?**

**A:** Writers block on `flushDone` until FlushWorker completes IO. Optional `writeTimeoutMs` throws `TimeoutException`. Metrics expose `blocked_writes` for alerting.

**Q5: Can two threads call `flush()` concurrently?**

**A:** Yes — both block under `writeMutex` until buffers drain. Idempotent result: empty active and idle worker.

**Q6: Why not use a lock-free queue of buffers?**

**A:** Valid Phase 2 for many buffers; double-buffer is simpler, fixed memory, and sufficient for interview. Lock-free adds ABA and reclamation complexity.

**Q7: Does `write()` guarantee durability?**

**A:** Only per policy. NEVER does not. ON_FLUSH after explicit `flush()`/`close()`. ALWAYS after each drain containing the byte.

**Q8: What happens on interrupt during backpressure wait?**

**A:** `await` throws interrupted; we convert to `InterruptedIOException`, restore interrupt flag, exit without partial accept (bytes not copied remain unwritten).

**Q9: Fairness among blocked writers?**

**A:** Optional `ReentrantLock(true)`. Default non-fair is faster; fairness reduces starvation risk for equal-sized writers.

**Q10: How do you test sticky IO?**

**A:** Mock `OutputStream` throws on Nth write; assert all subsequent ops throw same exception and flusher exits cleanly on close.

**Q11: Periodic fsync without full buffer?**

**A:** FlushWorker tracks `dirtySinceLastFsync` and time; if interval elapsed, fsync file descriptor even if active not full (may require draining active first for completeness).

**Q12: Integration with Databricks executor spill?**

**A:** Each spill thread gets its own BufferedWriter on a temp file; close with ON_FLUSH before registering file with shuffle reader; avoids fsync per small write from many threads.

---

## 13. Appendices

### A. Complexity summary

| Operation | Time | Space |
|-----------|------|-------|
| Buffered write | O(n) amortized | O(bufferSize) |
| Large bypass | O(n) IO | O(1) extra |
| flush / close | O(pending + IO) | — |

### B. Thread-safety checklist

- [ ] Lock released before disk IO
- [ ] Condition waits use while-loop
- [ ] close joins flusher
- [ ] Sticky error broadcast to all waiters
- [ ] TSan clean on stress harness

### C. Minimal Java skeleton

```java
class BufferedWriter implements Closeable {
  private final ReentrantLock lock = new ReentrantLock();
  private final Condition work = lock.newCondition();
  private final Condition done = lock.newCondition();
  // active/flushing ByteBuffer, flush thread, stickyError, closed
  void write(byte[] b, int off, int len) { /* §6.3 */ }
  void flushWorkerLoop() { /* §6.5 */ }
  public void close() { /* §6.7 */ }
}
```

### D. Whiteboard timing (45 min)

| Phase | Minutes |
|-------|---------|
| Clarify + invariants | 5 |
| API + class diagram | 8 |
| Pseudocode write/swap/close | 15 |
| Race analysis | 7 |
| Tests + fsync policies | 5 |
| Q&A | 5 |

---

*End of LLD prep.*
