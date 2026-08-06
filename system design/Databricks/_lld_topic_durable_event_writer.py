"""Durable event writer LLD topic."""

from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices

register("durable-event-writer-lld-system-design.md", lambda: build_doc([
    header(
        "Durable Append-Only Event Writer",
        "Group commit · CRC records · Log rotation · Tail readers · Concurrent producers · Recovery truncate",
        "Ack after durable append per policy; torn records truncated on recovery",
    ),
    section_1(
        goal="Design an **append-only event log** with concurrent producers, group commit, tail readers, CRC-protected records, file rotation, and recovery that truncates torn writes.",
        what_is="""| Scope | Single-node append log | Distributed Kafka |
| Model | Producer append + tail read | Random update |
| Durability | Group commit + fsync batches | Memory-only |
| Databricks lens | WAL / audit log / delta log segment | Full table format |""",
        fr_rows=[
            ("Record format?", "Length + payload + CRC32", "Detect torn tail"),
            ("Producers?", "Many threads append", "Mutex or lock-free queue to appender"),
            ("Readers?", "Tail followers read new records", "No random seek MVP"),
            ("Group commit?", "Batch fsync every N ms or M bytes", "Throughput vs latency"),
            ("Rotation?", "New file when segment hits size", "Atomic switch pointer"),
            ("Recovery?", "Replay from start; truncate bad tail", "Idempotent open"),
            ("Ordering?", "Total order by sequence number", "Monotonic seq per log"),
            ("Max record?", "e.g. 1MB", "Reject oversize"),
            ("Retention?", "Segments deleted after checkpoint", "Phase 2"),
            ("Duplicate append?", "Each append unique seq", "Idempotent client keys Phase 2"),
            ("Reader lag?", "Blocking readNext(timeout)", "Condition notify on append"),
            ("Crash during rotate?", "Old segment complete; new maybe partial", "Manifest fsync order"),
        ],
        mvp=[
            "Append API assigns monotonic sequence; writes length+payload+CRC.",
            "Group commit thread batches fsync.",
            "TailReader reads from last consumed seq; blocks for new records.",
            "Segment rotation at size threshold; current segment pointer atomic.",
            "Recovery scans segments, verifies CRC, truncates torn last record.",
            "Concurrent producers serialize append to log mutex or single writer thread.",
        ],
        scope="Append-only durable event log: CRC records, group commit, concurrent producers, tail readers, rotation, recovery truncates incomplete records.",
        invariant="""Every ACKed append has a complete record (len+payload+CRC) durable per fsync policy.
Readers never observe partial records; seq strictly increases with no gaps in committed prefix.
Recovery truncates any incomplete tail record before serving traffic.""",
    ),
    section_2(
        api="""class DurableEventWriter:
  open(path, Options) -> DurableEventWriter
  AppendResult append(byte[] payload) throws IOException
  void flush()                           // force group commit fsync
  TailReader tailReader(startSeq=latest)
  void close()

class TailReader:
  LogRecord next(long timeoutMs) throws IOException  // blocks
  long currentSeq()

class LogRecord:
  long sequence
  byte[] payload
  long timestamp

class AppendResult:
  long sequence
  long offsetInSegment""",
        guarantees=[
            ("Durability", "ACK after record in group commit batch fsync (default)"),
            ("Total order", "Sequences monotonic; committed prefix contiguous"),
            ("Reader safety", "No torn records visible"),
            ("Concurrent append", "Thread-safe; linearizable seq assignment"),
            ("Recovery", "Reopen rebuilds seq; truncates bad tail"),
            ("Rotation atomicity", "Readers switch to new segment without gap in seq"),
        ],
        errors="""IOException — disk full, fsync fail
InvalidArgument — empty or oversize payload
ClosedException — after close
CorruptionError — CRC fail mid-log (unrecoverable without truncate)
TimeoutException — reader wait timeout""",
    ),
    section_3(
        classes=[
            ("DurableEventWriter", "Append API, lifecycle"),
            ("SegmentWriter", "Current file append + CRC encode"),
            ("GroupCommitter", "Batch fsync scheduler"),
            ("SequenceGenerator", "Monotonic seq (atomic long)"),
            ("TailReader", "Follows committed watermark"),
            ("SegmentRotator", "Roll files at size"),
            ("Recovery", "Scan, verify CRC, truncate"),
            ("LogRecordEncoder", "len|payload|crc layout"),
            ("ReaderRegistry", "Notify on new commit"),
        ],
        diagram="""Producers → append lock → SegmentWriter → buffer
                              ↓
                       GroupCommitter → fsync batch
                              ↓
                       notify TailReaders
Recovery: scan segments → verify CRC → truncate tail → set seq watermark""",
    ),
    section_4("""### 4.1 On-disk record

```text
[ magic:4 ][ seq:8 ][ len:4 ][ payload:len ][ crc32:4 ]
CRC covers seq+len+payload
```

### 4.2 Group commit

```text
pending_bytes += record_size
if pending_bytes >= batch_bytes OR elapsed >= window_ms:
  fsync(current_segment_fd)
  committed_seq = last_seq_in_batch
  notify all TailReaders
```

| Op | Time | Notes |
|----|------|-------|
| append (amortized) | O(payload) + fsync/batch | Group commit |
| tail read | O(1) if ready | Else block |
| recovery | O(file size) scan | Startup |

### 4.3 Rotation

When segment size > limit: fsync, atomic rename/pointer to new segment file `log.N+1`, readers follow current pointer."""),
    section_5(
        "| append path | logMutex or single writer queue |\n| committed_seq | volatile/atomic |\n| reader wait | condition per TailReader |",
        ["Seq assigned before write visible to readers.", "Readers read only up to committed_seq.", "CRC verified before reader delivery.", "One incomplete record at end truncated on recovery.", "Rotation only after fsync current segment.", "Group commit never skips fsync for ACKed batch."],
        "append: logMutex → encode → buffer → register batch → (release before fsync if async commit thread)",
    ),
    section_6([
        ("append", """validate(payload)
lock(logMutex):
  seq = nextSeq++
  bytes = encode(seq, payload)  // includes CRC
  segment.write(bytes)
  batcher.register(seq)
unlock
waitForCommit(seq)  // or async future per policy
return AppendResult(seq)"""),
        ("group commit loop", """loop:
  wait until batch ready or timeout
  fd = current_segment
  fsync(fd)
  committed = last_seq
  notify readers up to committed"""),
        ("recovery", """seq = 0
for each segment file in order:
  offset = 0
  while offset + header <= file.size:
    rec = read_record(offset)
    if crc bad: break  // truncate here
    seq = max(seq, rec.seq)
    offset = next
  truncate file at offset
set nextSeq = seq + 1"""),
        ("tailReader next", """lock:
  while current < committed_seq:
    rec = read from segment at current
    current++
    return rec
  await(newCommit, timeout)"""),
        ("rotate", """fsync current
close current fd
open log.(N+1)
atomic store current_segment"""),
    ]),
    section_7([
        ("Crash mid-record", "Torn tail", "Recovery truncate"),
        ("Crash after write before fsync", "Record maybe lost", "Not ACKed if wait commit"),
        ("Crash during rotate", "Old complete", "Open newer partial → truncate"),
        ("CRC mismatch mid-file", "Corruption", "Fail or truncate policy"),
        ("Disk full", "append fails", "No ACK"),
        ("Reader slow", "Segments retained", "Backpressure policy Phase 2"),
    ]),
    section_8(
        ["append/read round trip", "multiple records order preserved", "oversize rejected", "recovery after clean close", "rotate boundary seq continuous", "empty payload allowed if spec says"],
        ["concurrent append unique seqs", "readers see committed only", "no duplicate seq"],
        [("Truncate last 3 bytes", "Recovery", "Prior prefix intact"), ("Kill during fsync", "Inject", "ACK only if committed")],
    ),
    section_9("Group commit window tuning; multiple segments; separate disk for log; sharded logs per partition at scale."),
    section_10(
        ["CRC + length records", "Group commit for throughput", "Tail readers on committed watermark", "Recovery truncates torn tail"],
        [("Single log", "Partitioned logs"), ("Blocking tail", "Catch-up snapshot reader")],
        ["ACK before fsync", "Reader reads uncommitted buffer", "Rotation without fsync"],
    ),
    section_11(
        ["vs Kafka?", "vs WAL in KV store?", "How fence old writers?", "Checksum scope bytes?", "Concurrent readers lag?", "Idempotent append keys?"],
        [("write without CRC", "Always CRC"), ("Reader sees pre-fsync", "Committed watermark only")],
    ),
    section_12(common_appendices("durable-event-writer")),
]))
