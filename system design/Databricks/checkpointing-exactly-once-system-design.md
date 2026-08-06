# System Design: Checkpointing and Exactly-Once Stream Processing

> **Focus areas:** Checkpoints · Epochs · Idempotent sinks · WAL · Recovery · End-to-end EOS · Spark/Flink · Delta sink  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct semantics (at-least-once vs effectively-once vs EOS), explicit commit ordering, honest crash-point analysis, measurable checkpoint overhead  
> **Interview theme:** Databricks — stream processing correctness on the lakehouse

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

## 1. Clarify Requirements (Interview Q&A)

Goal: design **checkpointing** so a distributed stream processor achieves **end-to-end exactly-once effects** into durable sinks (Delta Lake, Kafka, DB)—meaning each input event contributes to sink state **at most once** under failures and retries, without silent loss.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the product? | Managed stream job: read Kafka/Pulsar → stateful transforms → write Delta tables | Need source offsets + operator state + sink commit in one protocol |
| F2 | Sources? | Kafka with consumer groups; replay from offset | Offset is part of checkpoint; EOS requires transactional or idempotent offset commit |
| F3 | Processing model? | Micro-batch (Spark SS) or continuous (Flink) | Barrier alignment vs epoch batching; different checkpoint latency profiles |
| F4 | Stateful ops? | Aggregations, joins, dedup windows | RocksDB-like state backend; incremental checkpoints |
| F5 | Sink? | **Delta Lake** primary; optionally Kafka/DB | Delta txn + file layout; idempotency via `(job_id, epoch_id)` |
| F6 | Checkpoint? | Periodic consistent snapshot of `{offsets, operator state, sink staging metadata}` | Coordinator + durable metadata store |
| F7 | Recovery? | Restart from last **completed** checkpoint; replay in-flight epoch safely | Distinguish completed vs in-progress epochs |
| F8 | Late data? | Allowed within watermark; side outputs optional | Watermark independent of checkpoint boundary |
| F9 | Delivery guarantee target? | **End-to-end EOS** to sink (not just internal) | Sink must participate in commit protocol |
| F10 | Fallback mode? | Configurable at-least-once for legacy sinks | Document duplicate risk; compensating dedup downstream |
| F11 | Schema evolution? | State serde versioned; compatible upgrades | Checkpoint includes serializer version |
| F12 | Multi-sink? | Same job writes Delta + metrics topic | Avoid naive 2PC; outbox or primary+async secondary |
| F13 | Savepoints? | Manual trigger for upgrade/migration | Separate from automatic checkpoints; operator-triggered |
| F14 | Observability? | Checkpoint duration, size, failures, lag | Alert on checkpoint timeout → backpressure |

**MVP functional scope (lock with interviewer):**

1. Single streaming job: Kafka source → map/filter/aggregate → Delta sink.
2. **Epoch/microbatch model:** read batch → compute → stage sink write → atomically commit `{offsets + state + sink}`.
3. Checkpoint every **10–60 s** (configurable); recovery resumes from last successful checkpoint.
4. Idempotent sink writes keyed by `(application_id, epoch_id, partition)`.
5. Operator state stored in embedded KV (RocksDB) with incremental checkpoint to durable blob store.
6. WAL for checkpoint metadata on coordinator (Postgres/etcd-style) — small, strongly consistent.
7. At-least-once internal transport with **effectively-once** sink via idempotency.

**Out of MVP (explicitly defer):**

- Cross-job transactional exactly-once (global 2PC)
- Active-active dual-writer same Delta table without coordination
- Sub-millisecond continuous processing (Flink-style unaligned checkpoints at scale)
- Automatic infinite state compaction / TTL for all operator types
- Exactly-once side effects to arbitrary HTTP APIs without partner idempotency

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Recovery time (RTO)? | Minutes acceptable for batch analytics | Restore checkpoint ≤ 2–5 min for 100 GB state |
| N2 | Recovery point (RPO)? | Zero duplicate **effects** in sink | Last completed epoch only |
| N3 | Checkpoint overhead? | Low vs processing | ≤ 5–10% CPU/IO at baseline; bounded pause |
| N4 | End-to-end latency? | Seconds to minutes | Microbatch trigger 1–30 s; watermark-driven windows |
| N5 | Throughput? | 100K–1M events/s baseline | Scale horizontally by Kafka partitions |
| N6 | State size? | 10 GB–1 TB per job | Incremental + async upload checkpoints |
| N7 | Availability? | Job restarts automatically | HA driver/coordinator; checkpoint store 99.99% |
| N8 | Correctness | No silent loss; no duplicate sink rows | Formal commit order documented |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Epoch *e* completes: process batch → write Delta staging files → commit Delta txn with epoch marker → persist checkpoint `{offsets_e, state_e, sink_commit_e}` → advance consumer offsets.
2. Crash after checkpoint committed → restart → load checkpoint *e* → skip re-processing offsets ≤ *e* (already committed to sink).
3. Crash mid-epoch *e+1* before checkpoint → restart from *e* → re-process *e+1* → sink idempotency dedupes duplicate staging write.
4. Stateful aggregation: key *K* updated in epoch; state snapshot includes *K*; recovery restores *K* without replaying entire history.
5. Watermark advances; late events beyond allowed lateness dropped to side output — checkpoint captures watermark.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Crash after sink write, before offset commit | On replay, sink sees same `epoch_id` → no duplicate visible rows |
| Crash after offset commit, before checkpoint metadata | Worst case re-process batch; sink idempotent |
| Duplicate epoch commit attempt | Sink rejects or ignores second commit with same `(job, epoch)` |
| Checkpoint store unavailable | Pause processing; do not commit partial epoch |
| State backend corruption | Fail job; restore from previous checkpoint; alert |
| Kafka rebalance during epoch | Fence old consumer generation; abort in-flight epoch |
| Slow checkpoint (state huge) | Backpressure; extend epoch interval; async incremental |
| Two drivers (split brain) | Fencing token on checkpoint write; newer epoch wins |
| Delta concurrent writer conflict | Optimistic concurrency; retry epoch commit |
| Schema change mid-job | Savepoint + state migration or allow incompatible restart |
| Poison message | DLQ after N failures; checkpoint excludes poison from main offset advance policy (configurable) |

### 1.4 Scales (Progressive)

| Metric | Baseline (1×) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Input events/s (peak) | 100K | 1M | 10M | 100M |
| Kafka partitions / job | 64 | 256 | 2K | 20K |
| Operator state (GB) | 10 | 100 | 1 TB | 10 TB |
| Checkpoint interval | 30 s | 30 s | 10–15 s | 5–10 s (async) |
| Checkpoint size (full) | 2 GB | 20 GB | 200 GB | 2 TB (incremental dominant) |
| Workers / executors | 20 | 200 | 2K | 20K |
| Delta files / epoch | 200 | 2K | 20K | 200K (need compaction) |
| Jobs in cluster | 50 | 500 | 5K | 50K (multi-tenant) |
| Checkpoint metadata QPS | 50 / 30s ≈ 2 | 500 jobs | 5K | 50K (sharded coord) |

**What each jump forces:**

- **10×:** Incremental checkpoints; parallel state upload; per-partition checkpoint subtasks; RocksDB tuning.
- **100×:** Distributed checkpoint storage sharding; unaligned or aligned barriers with timeout; state backend tiering (local SSD + cloud); compaction service for Delta.
- **1,000×:** Cell-per-tenant isolation; checkpoint coordinator federation; avoid stop-the-world barriers; erasure-coded checkpoint blobs; separate control plane.

### 1.5 Etc. (Constraints & Assumptions)

- Kafka provides **ordered per-partition** logs and consumer groups with offset commits.
- Delta Lake supports **ACID transactions** on metadata; object store holds data files.
- Network and nodes fail; **no perfect synchrony**; clocks skew for metrics only—not for correctness.
- "Exactly-once" means **exactly-once side effects in the sink**, not exactly-once network delivery (internal at-least-once is normal).

**Scope statement:**

> Design checkpointing for a Kafka→stateful→Delta streaming job with periodic epochs, incremental operator state snapshots, and atomic commit of `{source offsets, state, sink}`—evolving from ~100K events/s and 10 GB state through 10× / 100× / 1,000× while keeping checkpoint overhead bounded and recovery correct.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event throughput vs epoch size

```text
Baseline: 100K events/s, epoch every 30 s
Events per epoch = 100K × 30 = 3M events
Avg payload 500 B → 3M × 500 B ≈ 1.5 GB raw input / epoch (before aggregation)

If aggregation 100:1 → sink ~15 MB / epoch (plus Parquet overhead ~2×)
```

At **100×**:

```text
10M events/s × 10 s epoch = 100M events/epoch
Even with heavy aggregation, shuffle + state touch dominates — not raw ingress bytes
Must partition by Kafka key; 2K partitions → ~50K events/s/partition peak
```

### 2.2 State and checkpoint I/O

```text
State size S = 10 GB (baseline)
Full checkpoint every 30 s → 10 GB / 30s ≈ 333 MB/s upload sustained — heavy

Incremental checkpoint assuming 5% churn/epoch:
  Δstate ≈ 0.05 × 10 GB = 500 MB / epoch → 500 MB / 30s ≈ 17 MB/s — manageable

At 100× with S = 1 TB, 5% incremental → 50 GB / 15s ≈ 3.3 GB/s aggregate across workers
  → requires parallel sub-checkpoints per RocksDB instance + dedicated network
```

**Critical insight:** Checkpoint cost scales with **state churn**, not just state size — design for incremental + async.

### 2.3 Checkpoint metadata WAL

```text
Checkpoint record ~2 KB (offsets map, epoch id, sink txn id, state blob pointers)
50 jobs × 1 checkpoint / 30s ≈ 1.7 metadata writes/s — trivial for Postgres/etcd

At 1,000×: 50K jobs → 1.7K writes/s — shard coordinator by tenant/cell
```

### 2.4 Delta sink write amplification

```text
200 Parquet files / epoch × 128 MB target → up to 25 GB staged (upper bound before compaction)
Small files problem: run OPTIMIZE / auto-compaction async — not on critical commit path

Commit path: _delta_log JSON entries only (~KB) — must be atomic with epoch marker
```

### 2.5 Recovery time budget

```text
Download state 10 GB @ 200 MB/s ≈ 50 s
Restore RocksDB + replay WAL segments ≈ 30–90 s
Total RTO ~2–3 min baseline — acceptable

1 TB state @ 100× without tiering → hours — unacceptable
  → keep hot state local; checkpoint to S3 incremental; lazy restore
```

### 2.6 Bottlenecks (ranked)

1. Full synchronous checkpoints blocking epoch commit  
2. Sink commit before offset commit (duplicate) or reverse (loss)  
3. Hot keys blowing state per subtask  
4. Delta small-file storm at high partition count  
5. Barrier alignment straggler (Flink-style) stalling entire job  
6. Coordinator split-brain without fencing  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Epoch              → monotonic batch id e = 0,1,2,... for a job run
Checkpoint         → durable record: {epoch, source_offsets, state_handles, sink_commit_id, watermark}
StateBackend       → per-subtask RocksDB: keyed operator state
CheckpointStorage  → S3/GCS for state blobs; small metadata in SQL/etcd
SinkCommitter      → Delta txn: add files + epoch marker in _delta_log
JobDriver          → orchestrates read→process→commit; single writer for epoch advance
FencingToken       → (job_id, attempt_id) incremented on failover — rejects stale commits
IdempotencyKey     → (application_id, epoch_id, partition_id, sink_object)
```

### 3.2 Delivery semantics ladder (say aloud)

| Level | Meaning | Typical mechanism |
|-------|---------|-------------------|
| At-most-once | May lose records | Commit offset before process |
| At-least-once | May duplicate effects | Commit offset after process; no idempotent sink |
| Effectively-once | Duplicates exist internally but sink dedupes | Idempotent sink + deterministic writes |
| End-to-end EOS | Sink sees each logical event once | Atomic {offset, state, sink} commit + idempotent sink |

**Interview precision:** Kafka consumer offset commit and Delta file write are **different systems** — EOS requires a **protocol** linking them.

### 3.3 Options: commit ordering

| Option | Order | Pros | Cons | Verdict |
|--------|-------|------|------|---------|
| A. Offset before sink | Offsets → sink | Never re-read | **Loss** on crash after offset | Reject |
| B. Sink before offset, no idempotency | Sink → offsets | No loss | **Duplicates** on replay | Reject for EOS |
| C. Sink before offset + idempotent sink | Sink → offsets; replay safe | EOS effects | Must design idempotency keys | **MVP** |
| D. Two-phase commit (Kafka txn + Delta) | Single atomic | Strong | Complex; limited sink support | Flink+Kafka txn path |
| E. Outbox to commit queue | Process → outbox → single committer | Clean separation | Extra component | 100×+ |

**Chosen path:**

- **MVP (Spark-like microbatch):** For epoch *e*: process → stage Delta write with `epoch=e` → commit Delta txn → write checkpoint with offsets through *e* → commit Kafka offsets. Idempotent sink handles replay of *e*.
- **Flink-like continuous:** Chandy-Lamport barriers align operators; snapshot state asynchronously; sink uses two-phase commit hook at barrier.

### 3.4 Epoch lifecycle (microbatch)

```text
States per epoch e:
  OPEN       → reading and processing
  STAGING    → sink files written, not yet committed
  COMMITTED  → checkpoint persisted; offsets advanced
  ABORTED    → failure; will retry from last COMMITTED

Protocol:
  1. Read Kafka [offset_{e-1}, offset_e) per partition
  2. Compute with state_{e-1} → state_e, output batches
   3. Write Parquet to temp paths tagged epoch=e
  4. DeltaSink.commit(files, epoch=e)  -- txn
  5. Upload incremental state snapshot for e
  6. CheckpointCoordinator.persist({e, offsets, state handles, delta_txn})
  7. KafkaConsumer.commit(offsets_e)
```

**Invariant:** Step 6 must be **durable** before step 7 ACK to processing layer; if 7 fails, replay safe via idempotency.

### 3.5 Idempotent Delta sink design

```text
Each epoch write produces files:
  s3://table/_staging/job123/epoch=e/part=p/file.parquet

Delta commit adds:
  - dataFiles with tags {app_id, epoch, partition}
  - txn app_id + epoch in metadata OR separate _commits table

On replay of epoch e:
  if commit_record exists for (app_id, e): skip file add (or verify same file list)
  else: commit

Duplicate rows prevented by:
  - deterministic aggregation keys + overwrite mode, OR
  - merge key includes event_id, OR
  - epoch-level replace partition for idempotent microbatch upsert
```

**Deal-breaker:** Append-only sink without dedup keys — cannot EOS with replay.

### 3.6 Stateful operator checkpoint (RocksDB)

```text
Per subtask:
  RocksDB local SSD
  Periodic incremental SST upload → checkpoint store
  Checkpoint manifest: list of SST + sequence number + changelog offset

Recovery:
  Download SSTs → open RocksDB
  Optionally replay changelog from Kafka (if changelog enabled) for fine RPO
```

Changelog pattern (100×): dual-write updates to Kafka compacted topic → faster recovery than full SST.

### 3.7 Spark Structured Streaming vs Flink (comparison)

| Aspect | Spark SS (microbatch) | Flink (continuous) |
|--------|----------------------|---------------------|
| Unit of work | Epoch / trigger interval | Event-time windows + barriers |
| Checkpoint | Batch commit at end of microbatch | Aligned barrier snapshots |
| EOS to Delta | foreachBatch + idempotent epoch | TwoPhaseCommitSinkFunction |
| Latency floor | Trigger interval (e.g., 1 s) | ms–s with low interval |
| Straggler impact | Epoch stretches | Barrier alignment pause |
| Mental model for interview | **Epoch table** | **Barrier flow** |

Both need: **idempotent sink + durable checkpoint linking offsets**.

### 3.8 WAL on coordinator

```text
Coordinator WAL (Postgres or Raft log):
  INSERT checkpoint(job_id, epoch, offsets_json, state_ptrs, sink_txn, fencing_token)

Rules:
  - Monotonic epoch per (job_id, attempt_id)
  - Reject commit if fencing_token < latest
  - Readers always load max(epoch) where status=COMMITTED
```

Analogous to NameNode edit log — small, strongly consistent metadata only.

### 3.9 Watermarks vs checkpoints

```text
Watermark: event-time progress for window closing — computed continuously
Checkpoint: fault-tolerance boundary — persisted periodically

They are orthogonal:
  - Checkpoint can capture current watermark in metadata
  - Late events after watermark go to side output; do not block checkpoint
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Checkpoint frequency | 30 s baseline | Balance RTO vs overhead | Every batch full snapshot |
| Sink idempotency | Epoch-keyed Delta txn | Replay-safe | Blind append |
| Offset commit | After sink+checkpoint | No loss | Before sink |
| State | RocksDB incremental | Scale state size | Full memory only |
| Multi-sink | Primary Delta + async metrics | Avoid 2PC | Dual transactional sinks |
| Internal messaging | At-least-once | Industry standard | Assume network EOS |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Kafka                         Job Driver / Checkpoint Coordinator
  Topics                              |
    |                                 | WAL (checkpoints)
    v                                 v
+----------+    +----------------+   +------------------+
| Partition| -> | Stream Workers | ->| Checkpoint Meta  |
| readers  |    | (stateful ops) |   | DB (Postgres)    |
+----------+    +-------+--------+   +------------------+
                        |                      ^
                        | state snapshots      |
                        v                      |
                +---------------+              |
                | Checkpoint    |--------------+
                | Blob Store    |   (pointers)
                | (S3/GCS)      |
                +---------------+
                        |
                        v
                +---------------+
                | Delta Lake    |
                | (sink table)  |
                +---------------+
```

### 4.2 Sequence: successful epoch commit

```text
Driver          Workers           Delta Sink       CheckpointDB     Kafka
  |--open e---->|                   |                |                |
  |<-processed--|                   |                |                |
  |--stage write------------------->|                |                |
  |<-txn ok------------------------|                |                |
  |--upload state blobs----------->|                |                |
  |--persist checkpoint--------------------------->|                |
  |<-fsync ok--------------------------------------|                |
  |--commit offsets------------------------------------------------->|
  |<-ok------------------------------------------------------------|
  | mark epoch e COMMITTED          |                |                |
```

### 4.3 Sequence: crash and recovery

```text
Driver crash after Delta commit, before checkpoint persist:

New Driver (attempt_id++)
  load last checkpoint epoch=e-1
  replay epoch e:
    DeltaSink.commit(epoch=e) → already committed → no-op idempotent
    persist checkpoint for e
    commit offsets
```

### 4.4 Flink-style barrier alignment (alternative diagram)

```text
Source --barrier e--> Op1 --barrier e--> Op2 --barrier e--> Sink
          |                  |                  |
     snapshot          snapshot           preCommit(e)
                                              commit(e) on checkpoint complete

Aligned: all inputs wait at barrier — pause on straggler
Unaligned: buffer in-flight; snapshot channel state — faster but larger checkpoints
```

### 4.5 Failure matrix (crash point → outcome)

```text
                    | Loss? | Dup sink rows? | Fix                          |
--------------------|-------|----------------|------------------------------|
Before process      | No    | No             | Retry epoch                  |
After process, before sink | No | Maybe     | Replay epoch; idempotent sink|
After sink, before ckpt | No | Maybe       | Replay; sink dedupe          |
After ckpt, before offset | No | Maybe    | Replay; sink dedupe          |
After full commit   | No    | No             | —                            |
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Monotonic epochs:** committed epoch ids strictly increase per job attempt.  
2. **Single committer:** only one active driver advances epochs (fencing).  
3. **Commit order:** sink durable before checkpoint offsets claim success for that epoch.  
4. **Idempotent sink:** `(app_id, epoch)` commit is safe to retry.  
5. **Checkpoint atomicity:** metadata record appears atomically (WAL fsync or Raft).  
6. **No offset skip without sink:** offsets for epoch *e* not committed unless sink *e* is committed.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Worker lost mid-epoch | Driver recomputes epoch from last checkpoint |
| Checkpoint blob partial upload | Manifest checksum; ignore incomplete |
| Delta txn conflict | Retry with same epoch id; deterministic file set |
| Kafka consumer rebalance | Stop epoch; fence old generation |
| Stale driver writes | Fencing token on checkpoint row |
| State corruption | Restore previous checkpoint; halt if both bad |

**Kafka EOS note (advanced):**

```text
Kafka transactions (read-process-write Kafka):
  beginTxn → consume → produce → sendOffsetsToTxn → commitTxn
Pairs with external sink only if sink participates in same logical epoch — else use idempotent sink pattern above
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Single driver; RocksDB per executor; S3 checkpoints; 30 s epoch |
| 10× | Incremental checkpoints; parallel upload; 256 partitions |
| 100× | Changelog state backend; async checkpoint; dedicated coord shard; Delta OPTIMIZE |
| 1000× | Cell isolation; unaligned checkpoints; tiered checkpoint store; epoch coalescing |

**Partitioning:** Kafka partition = parallelism unit; state keyed by business key must align or shuffle.

**Hot key mitigation:** Salting in pre-aggregate; local combiner; separate hot-key operator.

### 5.3 Maintainability

- **Explicit epoch metrics** on dashboard: duration, records, state delta, commit latency.  
- Savepoints for code deploy; checkpoints automatic.  
- Schema registry for state migration.  
- Chaos tests: kill driver at each protocol step.  
- Golden replay: fixed Kafka topic slice → same Delta output hash per epoch.

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Spark SS trigger=30s:
  foreachBatch { (df, batchId) =>
    process(df)
    writeDelta(df, epoch=batchId)  // idempotent
    // checkpoint handled by SS offset log + custom epoch store
  }
Checkpoint store: Postgres row per batchId
State: RocksDB on executors
```

**10×**

- Incremental RocksDB checkpoint uploads in background thread pool.  
- Increase partitions to 256; tune `maxOffsetsPerTrigger`.  
- Delta `autoCompact` post-commit async.

**100×**

- Changelog topic for state (compacted Kafka).  
- Checkpoint coordinator sharded by `job_id % N`.  
- Unaligned checkpoints if Flink; or increase microbatch interval with admission control.  
- Separate compaction service for Delta tables.

**1000×**

- Multi-tenant cells; quota on checkpoint storage GB/day.  
- Federated metadata; no global stop-the-world.  
- Approximate / sampled state for non-critical operators (with documented semantics).

### 5.5 Delta sink deep dive

```text
Table layout:
  /year/month/day/partition=.../file.parquet

Epoch commit protocol:
  1. Write files to temp prefix staging/job/epoch/
  2. BEGIN Delta txn
  3. ADD files + userMetadata {app_id, epoch, attempt}
  4. COMMIT if no conflicting epoch metadata
  5. Move visibility to readers

Merge/Upsert idempotency:
  MERGE INTO target USING batch
  ON target.event_id = batch.event_id
  WHEN NOT MATCHED THEN INSERT
  -- replays of same event_id are no-ops
```

**Small file control:** target 128–256 MB files; bin-pack within epoch; async OPTIMIZE.

### 5.6 Recovery algorithm (pseudocode narrative)

```text
onJobStart(job_id):
  attempt = newAttempt()
  fencing = (job_id, attempt)
  cp = loadLatestCommittedCheckpoint(job_id)
  if cp is null: epoch = 0; offsets = earliest
  else: epoch = cp.epoch + 1; offsets = cp.offsets; restoreState(cp.handles)

loop:
  batch = readKafka(offsets, limit=epochSize)
  newState, output = compute(batch, state)
  stageSink(output, epoch, fencing)
  commitSink(epoch, fencing)          // idempotent
  handles = uploadStateDelta(newState)
  persistCheckpoint(epoch, offsets', handles, fencing)
  commitKafkaOffsets(offsets')
  epoch++
```

### 5.7 Multi-sink caution

```text
Primary: Delta (transactional idempotent)
Secondary: metrics Kafka topic

Pattern:
  write metrics to internal log table in same Delta txn OR
  emit metrics after checkpoint (at-least-once metrics OK)

Do NOT 2PC Delta + Postgres without proven coordinator
```

### 5.8 Testing fault injection

| Inject at | Expected |
|-----------|----------|
| After read | Reprocess same batch; no sink change |
| After sink commit | Checkpoint retry; no duplicate rows |
| Before offset commit | Replay; idempotent sink |
| Kill 50% workers | Epoch retries or task retry within epoch |
| Corrupt checkpoint N | Restore N-1; alert |

---

## 6. Wrap-Up

**Design summary**

- **Exactly-once is a commit protocol**, not a magic flag — link Kafka offsets, operator state, and Delta txn with epoch ids.  
- **Idempotent sink** (Delta epoch marker or merge keys) makes replay safe.  
- **Incremental checkpoints** + WAL metadata keep overhead bounded as state grows.  
- Spark microbatch epochs and Flink barriers differ in latency profile; **same correctness building blocks**.  
- Failures between steps are handled by **monotonic epochs + fencing + deduping sink**.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Microbatch epochs 30 s | Continuous + unaligned checkpoints |
| Delta idempotent commit | Kafka txn read-write loops |
| Full incremental RocksDB | Changelog + local recovery |
| Single coordinator | Sharded coordinator / cells |

**Top risks**

1. Committing offsets before sink (silent loss)  
2. Non-idempotent append sink under replay  
3. Full checkpoint stalls pipeline  
4. Split-brain driver double-commit  
5. Delta small-file / metadata explosion  

**What I'd measure first in production**

- Checkpoint duration p99, state bytes uploaded, epoch commit latency, replay count, duplicate detection rate in sink audits, consumer lag vs checkpoint lag.

---

## 7. Deeper / Related Interview Questions

1. Walk through crash after Delta commit but before Kafka offset commit — outcome?  
2. How does Spark Structured Streaming achieve EOS to Delta specifically?  
3. Explain Chandy-Lamport barriers and aligned vs unaligned checkpoints in Flink.  
4. Kafka transactions vs external sink — what's the gap?  
5. How do idempotency keys differ from transactional writes?  
6. Savepoint vs checkpoint — when use each?  
7. Can you get EOS with an HTTP webhook sink?  
8. How does watermark interact with epoch boundaries for session windows?  
9. State schema evolution — what happens on incompatible change?  
10. Dual sink Delta + Elasticsearch — design?  
11. Effectively-once vs exactly-once — pedantic difference?  
12. How to bound checkpoint size with unbounded state (e.g., distinct count)?  
13. RocksDB vs heap state backend tradeoffs?  
14. How does Delta time travel help debug duplicate epochs?  
15. End-to-end EOS across **two** streaming jobs chained by Kafka?  

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "Kafka EOS means everything EOS" | External sink needs its own idempotency/txn |
| "Commit offset first for performance" | Causes loss — never for analytics correctness |
| "Checkpoints are just offsets" | Must include operator state for stateful jobs |
| "Exactly-once delivery internally" | Internal at-least-once + idempotent sink is the practical pattern |
| "Disable checkpoint for speed" | At-least-once duplicates or manual offset pain |

---

## 8. Appendices

### A. Pseudocode — epoch commit (microbatch)

```text
function runEpoch(epoch, offsets_in, state_in, fencing):
  batch = kafka.read(offsets_in, limits)
  state_out, output = operators.compute(batch, state_in)

  files = delta.stage(output, path=staging(job, epoch))
  delta.commit(files, metadata={app_id, epoch, fencing})  // idempotent

  handles = checkpointStore.uploadIncremental(state_in, state_out, epoch)
  checkpointDb.persist(job, epoch, offsets_out(batch), handles, fencing)
  kafka.commitOffsets(offsets_out(batch))
  return epoch + 1, offsets_out, state_out
```

### B. Pseudocode — idempotent Delta commit

```text
function deltaCommit(app_id, epoch, files, fencing):
  if metadataTable.exists(app_id, epoch):
    existing = metadataTable.get(app_id, epoch)
    assert existing.files == files
    return OK  // replay

  with delta.transaction(table):
    if txn.conflict(): return RETRY
    txn.addFiles(files, userMetadata={app_id, epoch, fencing})
    txn.commit()
  metadataTable.put(app_id, epoch, files)
```

### C. Failure matrix (expanded)

| Step crashed | On restart | Sink rows | Offsets |
|--------------|------------|-----------|---------|
| During compute | Recompute same epoch | None new | Unchanged |
| After stage, before Delta commit | Restage or reuse staged | None committed | Unchanged |
| After Delta commit | Idempotent commit | Correct once | May replay |
| After checkpoint | Idempotent | Correct once | Advance |

### D. Metrics checklist

```text
epoch_duration_seconds{quantile}
checkpoint_upload_bytes
checkpoint_duration_seconds
state_backend_sst_count
delta_commit_latency_ms
kafka_consumer_lag
duplicate_epoch_skipped_total
fencing_rejected_commits_total
recovery_time_seconds
```

### E. Capacity cheat sheet

```text
incremental_upload_Bps ≈ (state_GB × churn_ratio) / checkpoint_interval_s
metadata_WAL_qps ≈ num_jobs / checkpoint_interval_s
delta_files_per_day ≈ epochs_per_day × files_per_epoch × tables
recovery_seconds ≈ state_GB / download_Bps + rocksdb_open_seconds
```

### F. Clarifying questions cheat sheet (30 seconds)

1. Source (Kafka?) and sink (Delta?) — confirm end-to-end scope.  
2. Stateful or stateless operators?  
3. Latency target — microbatch OK?  
4. State size and churn?  
5. At-least-once fallback acceptable for any sink?  
6. Multi-sink or single?

### G. Spark vs Flink EOS one-liners

```text
Spark SS: WAL on offset log + idempotent foreachBatch sink + checkpoint directory
Flink: barrier snapshot + TwoPhaseCommitSinkFunction + checkpoint to distributed storage
Both: replay from last completed checkpoint; sink must tolerate epoch retry
```

### H. Related Databricks follow-ups

- Durable embedded KV / RocksDB LLD (`durable-embedded-kv-store-lld-system-design.md`)  
- Delta transaction log design  
- Persistent cache with WAL for executor shuffle  
- MPMC work queue for checkpoint upload workers  

### I. Glossary

| Term | Meaning |
|------|---------|
| Epoch | Logical batch id for idempotent commit unit |
| Barrier | Control record synchronizing operator snapshots (Flink) |
| Changelog | Compacted Kafka topic mirroring state updates |
| Fencing token | Prevents stale primary from committing |
| Effectively-once | Duplicates possible internally; sink dedupes |
| Savepoint | User-triggered checkpoint for upgrade/migrate |

### J. Load math template

```text
events_per_epoch = rate × trigger_interval
state_delta ≈ state_size × update_fraction_per_epoch
checkpoint_egress_Mbps = (state_delta_bytes × num_workers) / interval × 8 / 1e6
min_partitions ≈ peak_rate / per_partition_throughput
```

---

*End of checkpointing and exactly-once HLD prep.*
