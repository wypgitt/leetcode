"""BufferedWriter LLD topic."""

from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices

register("buffered-writer-lld-system-design.md", lambda: build_doc([
    header(
        "Thread-Safe Buffered Writer",
        "Buffer swap · Background flush thread · fsync policy · Backpressure · close() lifecycle",
        "Explicit flush/fsync semantics; no data loss after close(); backpressure when buffer full",
    ),
    section_1(
        goal="Design a **thread-safe BufferedWriter** wrapping `File`/`OutputStream` with a background flush thread, buffer swapping, and deterministic `close()`.",
        what_is="""| Scope | Single file/output stream wrapper | Full logging framework |
| Threads | Many producers, one flusher | One writer thread only |
| Durability | Configurable fsync policy | Always sync every byte MVP |
| Databricks lens | Executor spill / WAL batching | Distributed file system |""",
        fr_rows=[
            ("Underlying sink?", "FileOutputStream / POSIX fd", "Delegate write+fsync"),
            ("Buffer size?", "Fixed e.g. 64KB–4MB", "Two buffers swap"),
            ("Thread safety?", "Multiple threads call write()", "Mutex + condition vars"),
            ("Flush thread?", "Background drains active buffer", "Swap when full or timer"),
            ("Backpressure?", "Block or timeout when both buffers full", "Document policy"),
            ("fsync policy?", "NEVER / ON_FLUSH / PERIODIC / ALWAYS", "Latency vs durability"),
            ("close()?", "Flush remaining, fsync per policy, join thread", "Idempotent close"),
            ("Partial writes?", "Atomic append to buffer or block", "No torn application records in buffer"),
            ("Metrics?", "bytes_buffered, flush_count, wait_time", "Required for interview"),
            ("Error propagation?", "First IO error sticky; fail subsequent writes", "Surface to all waiters"),
            ("Interrupt handling?", "write() responds to interrupt", "Restore interrupt flag"),
            ("Zero-copy?", "Optional direct buffer slice", "Copy into internal buffer MVP"),
        ],
        mvp=[
            "Double-buffer: active (writers) + flushing (background).",
            "`write(byte[])` copies into active buffer under lock; swap when full.",
            "Background thread writes flushing buffer to `OutputStream`, optional fsync.",
            "Backpressure: writers block when active full and flush in progress.",
            "`flush()` waits until active empty and flush complete.",
            "`close()` sets closed flag, flush all, join flusher, close sink.",
        ],
        scope="Thread-safe buffered writer: double-buffer swap, dedicated flush thread, fsync policy, backpressure on full buffers, close joins thread and drains.",
        invariant="""After close() returns successfully, all bytes accepted by write() before close are on the underlying sink per fsync policy.
No byte accepted by write() is lost unless process killed before flush completes and policy allows loss.
At most one thread writes to the underlying OutputStream (the flusher).""",
    ),
    section_2(
        api="""class BufferedWriter implements Closeable:
  BufferedWriter(OutputStream out, Options opts)

  void write(byte[] data, int off, int len) throws IOException
  void write(byte b) throws IOException
  void flush() throws IOException          // drain active → sink (+ fsync per policy)
  void close() throws IOException          // flush + join + close out

class Options:
  int bufferSize = 65536
  FsyncPolicy fsyncPolicy = ON_FLUSH
  long periodicFsyncMs = 0
  long writeTimeoutMs = Long.MAX_VALUE

enum FsyncPolicy:
  NEVER, ON_FLUSH, PERIODIC, ALWAYS""",
        guarantees=[
            ("Thread-safe writes", "Concurrent write() safe"),
            ("Ordering", "Bytes appear on sink in write linearization order per thread interleaving"),
            ("close durability", "close() flushes all buffered bytes before returning"),
            ("Single sink writer", "Only flush thread calls out.write"),
            ("Backpressure", "write blocks (or times out) when buffers saturated"),
            ("Error sticky", "First IOException poisons writer; subsequent ops throw"),
        ],
        errors="""IOException        — underlying I/O failure (sticky)
ClosedException    — write/flush after close
TimeoutException   — write blocked too long (if configured)
InvalidArgument    — negative len, null buffer""",
    ),
    section_3(
        classes=[
            ("BufferedWriter", "Public API; coordinates buffers"),
            ("BufferPair", "active + flushing byte buffers"),
            ("FlushWorker", "Background thread loop"),
            ("Options", "buffer size, fsync, timeouts"),
            ("WriteLock", "Protects buffer state + swap"),
            ("FlushCond", "Writers wait; flusher signals"),
            ("Metrics", "blocked_writes, flush_latency"),
        ],
        diagram="""Thread A,B,C --write()--> [active buffer] --swap full-->
                              |                    |
                              v                    v
                         block if full      [flushing buffer]
                                                   |
                                            FlushWorker thread
                                                   v
                                            OutputStream + fsync""",
    ),
    section_4("""### 4.1 Double-buffer swap

```text
active:   writers append here (mutex held)
flushing: flusher drains to OutputStream (ownership transferred on swap)

when active.remaining == 0:
  wait until flushing empty (prior flush done)
  swap(active, flushing)
  signal flusher
```

| Op | Time | Notes |
|----|------|-------|
| write (fits) | O(n) copy | n = len |
| write (triggers swap) | O(bufferSize) + wait | Backpressure |
| flush | O(buffered) | Wait flush thread |
| close | O(buffered) + join | |

### 4.2 fsync policies

| Policy | When fsync | Durability |
|--------|------------|------------|
| NEVER | Never | Process crash may lose buffered |
| ON_FLUSH | flush()/close/buffer drain | ACK after flush durable |
| PERIODIC | Every T ms if data pending | Bounded loss window |
| ALWAYS | After each buffer drain | Slowest; strongest |

### 4.3 Backpressure model

Writers block when: `active full AND flushing not yet consumed`.
Optional timeout → TimeoutException."""),
    section_5(
        "| active/flushing state | writeMutex |\n| closed/error | atomic/volatile |\n| flush thread | joins on close |",
        ["Only flusher touches OutputStream.", "Swap is atomic under writeMutex.", "closed=true rejects new writes.", "Error bit set on first IO failure.", "flush() waits for empty active + idle flusher.", "No swap with uninitialized flushing buffer."],
        "writeMutex only; never hold during out.write (flusher releases before IO)",
    ),
    section_6([
        ("write", """lock(writeMutex):
  if closed or error: throw
  while len > 0:
    while active has space < need and not closed:
      if active full: trySwapAndSignalFlusher()
      else: break inner
    if active full: await(flushDone)  // backpressure
    copy min(need, active.space) into active
    len -= copied
unlock"""),
        ("flush worker loop", """while not shutdown:
  lock(writeMutex):
    while flushing empty and not shutdown:
      await(workAvailable)
    buf = take flushing buffer
  unlock
  out.write(buf)
  if fsyncPolicy matches: out.fsync()
  lock: mark flushing slot empty; signal writers
on shutdown: drain any remaining active+flushing"""),
        ("close", """lock: closed = true; signal flusher
flush()  // wait all data out
shutdown flusher; join()
out.close()"""),
        ("trySwap", """assert active full and flushing empty
swap(active, flushing)
flusher.notify()"""),
    ]),
    section_7([
        ("Crash before flush", "Bytes maybe lost", "Document fsync policy"),
        ("Disk full on flush", "Sticky IOException", "Propagate to writers"),
        ("Close during write", "Write fails or completes per lock order", "Define: close waits writers"),
        ("Flusher thread die", "Writers block forever", "join + watchdog; fail writer"),
        ("Spurious wakeup", "while loop on condition", "Correctness preserved"),
        ("Double close", "Idempotent second close", "No double join"),
    ]),
    section_8(
        ["Small writes coalesce in buffer", "Large write > buffer size", "flush empties active", "close persists all accepted bytes", "fsync ON_FLUSH after flush", "timeout on blocked write"],
        ["Many threads small writes", "fill buffer triggers single flush", "no torn buffer state", "TSan clean"],
        [("Kill before close", "Inject", "Data loss bounded by policy"), ("Kill after close", "Inject", "All accepted bytes durable if ALWAYS/ON_FLUSH")],
    ),
    section_9("""| Knob | Effect |
|------|--------|
| buffer 64K→4M | ↑ throughput ↓ latency |
| NEVER fsync | ↑ QPS; crash loss |
| Multiple writers | lock contention; shard writers Phase 2 |
| DirectByteBuffer | reduce copies at 100× |"""),
    section_10(
        ["Double-buffer + single flusher thread", "Backpressure when saturated", "close flush+join", "fsync policy explicit"],
        [("Single file", "Sharded files per partition"), ("Block backpressure", "Drop policy with metrics")],
        ["Write under lock to OutputStream", "Forgot join on close", "No sticky error propagation"],
    ),
    section_11(
        ["vs BufferedOutputStream?", "When fsync?", "How handle write > buffer?", "Fairness among blocked writers?", "Zero-copy?", "Periodic fsync vs group commit?"],
        [("flush()=fsync always", "State policy"), ("Unbounded queue", "Backpressure required")],
    ),
    section_12(common_appendices("buffered-writer")),
]))
