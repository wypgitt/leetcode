# System Design: Kafka-like Distributed Message Queue

> **Focus areas:** Topics/partitions · Log segments · Producer acks · Consumer groups · Offsets · Replication · ISR · Rebalance · Retention
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct ordering/durability semantics, explicit leader/follower story, honest at-least-once vs exactly-once trade-offs
> **Interview theme:** Databricks — log-based messaging backbone for pipelines and microservices

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

Goal: **bound a Kafka-like distributed commit log**—topics, partitions, replication, consumer groups, and retention—without hand-waving ordering or durability.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Core model? | Append-only **log per partition**; topics split into partitions | Partition = unit of parallelism + ordering |
| F2 | Producers? | Many services publish events | Idempotent producer optional |
| F3 | Consumers? | **Consumer groups** with partition assignment | One active consumer per partition in group |
| F4 | Ordering? | **Per-partition total order** | Key-based routing to partition |
| F5 | Delivery? | At-least-once default; exactly-once with transactions/idempotency | Offset commit semantics |
| F6 | Retention? | Time and/or size based; compacted topics optional | Segment files + GC |
| F7 | Replication? | N replicas per partition; leader serves reads/writes | ISR, min.insync.replicas |
| F8 | Ack levels? | `acks=0/1/all` | Latency vs durability trade-off |
| F9 | Replay? | Consumers reset offset or new group reads from earliest | Offset store |
| F10 | Multi-tenant? | Many topics; quotas | Throttle produce/fetch |
| F11 | Schema? | Out of MVP or registry hook | Avro/Protobuf Phase 2 |
| F12 | Admin? | Create topic, alter partitions, ACLs | Control plane metadata |

**MVP functional scope:**

1. Create/delete topics; configure partition count and replication factor.  
2. Produce to partition (key hash or explicit partition).  
3. Fetch by offset; consumer groups with cooperative assignment.  
4. Replicate logs leader → followers; ISR-based commit.  
5. Offset commit (auto/manual); at-least-once consume.  
6. Retention by time/size; delete obsolete segments.  
7. Basic quotas and metrics.

**Out of MVP:** Kafka Connect, Streams, tiered storage to S3 at infinite scale, cross-cluster mirrorMaker full product.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Produce latency | Interactive for acks=1 | p99 < 10–50ms in-region |
| N2 | Durability | No loss if acks=all and min ISR met | RPO ≈ 0 for committed records |
| N3 | Throughput | MB/s per broker scales horizontally | Partition count drives parallelism |
| N4 | Availability | Survive broker loss with RF≥3 | Leader election < seconds |
| N5 | Ordering | Per-partition | Never global order |
| N6 | Consumer lag | Observable | Lag metrics per group/partition |
| N7 | Rebalance | Minimal duplicate processing | Cooperative sticky assignor |
| N8 | Storage | Local SSD per broker | Log segments + index |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Producer sends with `acks=all` → leader appends → replicates to ISR → ACK.  
2. Consumer group joins → coordinator assigns partitions → fetch loop → commit offset.  
3. Broker dies → controller elects new leader from ISR → producers/consumers metadata refresh.  
4. Retention expires old segments → disk reclaimed.  
5. Compacted topic retains latest key per record key.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Leader fails before replicate | Uncommitted if acks=all; lost if acks=1 only to leader |
| Follower falls out of ISR | min.insync.replicas may block produce |
| Producer retry without idempotence | Duplicates possible |
| Consumer crash after process, before commit | At-least-once redelivery |
| Rebalance during processing | Revoke → commit → assign; cooperative protocol |
| Hot partition | Single partition bottleneck; split keyspace |
| Unclean election (allow.leader.election.without.isr) | Possible data loss — forbid for strict durability |
| Disk full on broker | Stop accepts; alert; expand/reassign |
| Zombie consumer (long GC) | Session timeout → partition reassigned |
| Message too large | Reject at produce |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Brokers | 10 | 50 | 500 | 5K |
| Topics | 1K | 10K | 100K | 1M |
| Partitions (total) | 5K | 50K | 500K | 5M |
| Peak produce QPS | 100K msg/s | 1M | 10M | 100M |
| Peak throughput | 1 GB/s | 10 GB/s | 100 GB/s | 1 TB/s (tiered) |
| Consumer groups | 500 | 5K | 50K | 500K |
| Retention (avg) | 7 days | 7 days | 14 days | tiered cold |
| Replication factor | 3 | 3 | 3 | 3 + cross-AZ |

**What each jump forces:**

- **10×:** More brokers; partition count planning; dedicated controllers.  
- **100×:** Rack awareness; quotas; separate fetch/produce paths; compression default.  
- **1,000×:** Tiered storage; brokerless ingestion edges; metadata sharding (KRaft/Kafka improvements); cell-based clusters.

### 1.5 Etc. (Constraints & Assumptions)

- **We build the log platform**, not every microservice's business logic.  
- Consumers must be **idempotent** for at-least-once.  
- Clock skew irrelevant for ordering—**offset** is truth.  
- Single cluster MVP; federation Phase 2.

**Scope statement:**

> Design a Kafka-like distributed log with partitioned topics, leader-based replication, consumer groups, configurable acks, retention, and progressive scale from ~100K msg/s to 100M+ via partitioning and tiered storage.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Throughput per partition

```text
Single partition sequential write ~ tens to low hundreds MB/s on NVMe (order of 50–200 MB/s practical with replication overhead)
If need 10 GB/s aggregate → need ~50–200 partitions minimum (spread across brokers)
```

### 2.2 Storage

```text
1 KB avg message × 100K msg/s = 100 MB/s ingest
× 86400 × 7 days ≈ 60 TB/week raw
× RF=3 replication ≈ 180 TB/week cluster-wide before compression
With compression ratio 3× → ~60 TB/week
```

### 2.3 Broker count sketch

```text
Each broker handle ~500 partitions comfortably (rule-of-thumb; tune)
500K partitions / 500 per broker = 1000 brokers at 100× scale
```

### 2.4 Metadata load

```text
Controller / KRaft quorum handles partition leadership, ISR changes
Avoid 5M partitions on single controller — shard metadata (Kafka KRaft improvements)
```

### 2.5 Network

```text
Produce 1 GB/s × RF=3 fan-in to followers ≈ 3 GB/s replication traffic per broker class — plan bisection bandwidth
```

### 2.6 Bottlenecks (ranked)

1. Hot partitions / skewed keys  
2. Replication lag under burst  
3. Consumer rebalance storms  
4. Disk IO on fetch (page cache helps)  
5. Coordinator for large groups  
6. Segment file count if small messages  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Topic            → named stream; N partitions
Partition        → ordered immutable log of records
Record           → key, value, timestamp, headers, offset
LogSegment       → append-only file + offset index
Broker           → hosts partition replicas
Leader           → serves produce/fetch for partition
Follower         → pulls from leader
ISR              → in-sync replica set
Controller       → leader election, metadata
ConsumerGroup    → group id + members + assigned partitions
Offset           → monotonic position per partition consumption
Coordinator      → group membership + offset commits
```

### 3.2 Options: pull vs push

| Option | Pros | Cons |
|--------|------|------|
| Pull (Kafka) | Consumer controls pace; natural backpressure | Poll latency |
| Push | Lower latency | Harder slow-consumer handling |

**Chosen:** Pull fetch API with long polling.

### 3.3 Replication protocol (high level)

```text
Producer → Leader:
  append to local log
  wait for followers in ISR to replicate up to required offset
  ACK based on acks setting

Follower → Leader:
  fetch replication stream (like consumer)
  update log + high-watermark
```

**High watermark:** offset of last record replicated to all ISR.

### 3.4 Producer ack semantics

| acks | Meaning | Durability |
|------|---------|------------|
| 0 | Fire-and-forget | May lose |
| 1 | Leader persisted | Lose if leader dies before replicate |
| all | All ISR ack | Strongest with min.insync.replicas |

### 3.5 Consumer offset commit

```text
auto commit: periodic (at-least-once; may duplicate on crash)
manual commit: after processing (still at-least-once unless transactional)
exactly-once: idempotent producer + transactional consume-transform-produce (advanced)
```

### 3.6 Partitioning keys

```text
partition = hash(key) mod num_partitions
null key → round-robin or sticky partitioner
Hot key → one hot partition — detect via metrics; split topic or salt keys
```

### 3.7 Log segment structure

```text
segment file: base_offset.log
index: sparse offset → file position
timeindex: timestamp → offset (retention by time)
Active segment accepts appends; sealed segments immutable
```

### 3.8 Compaction vs delete retention

```text
delete: drop segments older than retention.ms/bytes
compact: keep latest record per key; tombstone deletes key
Use compacted topics for changelog/metadata (connect offsets, KV changelog)
```

---

## 4. Architecture Diagram

### 4.1 Component diagram

```text
                    +----------------+
                    | Admin / CLI    |
                    +-------+--------+
                            |
                    +-------v--------+
                    | Controller     |
                    | (metadata)     |
                    +-------+--------+
                            |
     Producers              |              Consumers
        |                   |                   |
        v                   v                   v
+-------+------+    +-------+------+    +-------+------+
| Producer SDK |    | Broker cluster|    | Consumer SDK|
+-------+------+    | (leaders +    |    +-------+------+
        |           |  followers)   |            |
        +---------->|               |<-----------+
                    +-------+--------+
                            |
                    +-------v--------+
                    | Coordinator    |
                    | (groups/offset)|
                    +----------------+
```

### 4.2 Produce sequence

```text
Producer       Leader           Followers
   |--Produce-->|                |
   |            |--append local->|
   |            |--replicate---->| fetch/copy
   |            |<-ISR ack-------|
   |<-ACK-------|                |
```

### 4.3 Consumer group rebalance

```text
Consumer       Coordinator        Broker
   |--JoinGroup->|                 |
   |<-Assign-----|                 |
   |--Sync------>|                 |
   |--Fetch---------------------->|
   |--CommitOffset->|             |
```

### 4.4 Leader failure

```text
Broker3 (leader P5) dies
Controller detects via ZK/KRaft heartbeat
Elect P5 leader from ISR on Broker7
Update metadata; producers refresh metadata
Unclean election OFF → only ISR candidates
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Committed record (acks=all, min ISR) survives loss of any single broker in ISR set (with RF=3).  
2. Per-partition offsets monotonic; consumers never see gap without explicit transaction abort.  
3. Leader only serves committed records to consumers? (Kafka: consumers may read uncommitted depending config — clarify).  
4. ISR membership changes are metadata-durable before relying on new quorum.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Broker disk corrupt | RF replica promote; restore from replica |
| Split brain leader | Controller epoch + leader epoch fencing |
| Producer duplicate | Idempotent producer PID + sequence |
| Consumer duplicate | Idempotent handler + store processed IDs |
| Rebalance duplicate | Cooperative revoke; commit before release |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | 3–10 brokers; RF=3; ZK or KRaft |
| 10× | Rack awareness; more partitions; compression |
| 100× | Dedicated controllers; quotas; mirror to DR cluster |
| 1000× | Tiered storage; multiple clusters; metadata sharding |

**Hot partition mitigation:** split topic; change key; custom partitioner; async aggregation upstream.

### 5.3 Maintainability

- Rolling broker upgrades with controlled leader migration.  
- Topic config changes (retention, RF) via admin API.  
- Metrics: under-replicated partitions, ISR shrink rate, produce/fetch latency, log flush time.  
- Chaos: kill leader, fill disk, slow follower.

### 5.4 Progressive scale deep dive

**1× MVP:** Single cluster, produce/fetch, RF=3, consumer groups, offset in internal topic `__consumer_offsets`.

**10×:** Increase partitions; broker isolation; separate min.insync per topic class.

**100×:** Multi-AZ racks; strict unclean.leader=false; canary releases.

**1000×:** Tiered storage to object store; read path from cache; federation between cells.

### 5.5 Exactly-once sketch (follow-up)

```text
Transactional producer:
  begin txn → send batches → send offsets to txn → commit txn
Consumer read-process-write in same txn (Kafka Streams pattern)
Requires broker txn coordinator + state log
```

### 5.6 Comparison to log-based lakehouse

Databricks Delta/Iceberg sit **on object storage** with transaction log—similar **append-only log** mental model but optimized for batch analytics not sub-second streaming fan-out. Mention complement: MQ for real-time; lakehouse log for table history.

### 5.7 Leader election deep dive

```text
KRaft (modern): metadata quorum elects partition leaders; brokers vote; no ZooKeeper
On broker failure: controller detects; elect new leader from ISR; producers refresh metadata

unclean.leader.election.enable=false:
  if no ISR available → partition offline (prefer availability trade vs data loss)
```

### 5.8 Consumer rebalance cooperative protocol

```text
Revoke partitions → commit offsets → assign new partitions → resume fetch
Sticky assignor minimizes movement; cooperative avoids stop-the-world
Session timeout > processing time + heartbeat interval
```

### 5.9 Idempotent producer

```text
Producer ID (PID) + sequence per partition
Broker dedupes within session window
Enables safe retries without duplicate records in log
```

### 5.10 Dead-letter pattern

```text
process record:
  try N times
  on failure: produce to topic.DLQ with headers {original_topic, offset, error}
main consumer commits offset after DLQ handoff (policy: skip poison)
```

### 5.11 Tiered storage (1000×)

Sealed segments migrate to S3; fetch path reads local cache → object store; retention effectively unlimited with cost trade.

### 5.12 Monitoring checklist

| Metric | Alert |
|--------|-------|
| under_replicated_partitions | > 0 sustained |
| consumer_lag | SLO breach |
| isr_shrinks_rate | broker/network issues |
| request_queue_size | overload |

---

## 6. Wrap-Up

**Summary:** Partitioned append-only logs with leader replication and ISR; producers choose ack durability; consumers pull with offset tracking; controller handles metadata; retention via segments; scale by partitions and brokers.

**MVP vs later**

| MVP | Later |
|-----|-------|
| acks=1/ all | Transactions |
| Local retention | Tiered storage |
| Basic groups | Static membership / KIP improvements |

**Top risks:** hot keys; unclean election; offset commit before process; rebalance storms.

---

## 7. Deeper / Related Interview Questions

1. Why pull vs push consumers?  
2. How does leader election work (KRaft vs ZooKeeper)?  
3. What happens if all ISR followers die?  
4. Idempotent producer internals (PID, sequence).  
5. Log compaction vs delete retention use cases.  
6. How to design dead-letter topic pattern?  
7. Compare Kafka vs Pulsar vs NATS JetStream.  
8. How many partitions is too many?  
9. Cross-region replication (active-passive).  
10. Ordering guarantees with retry and multiple producers?

**Interviewer traps**

| Trap | Answer |
|------|--------|
| "Global order across topic" | Only per-partition |
| "Exactly-once without effort" | Idempotency + transactions |
| "Skip replication for speed" | State RF and acks trade-off |
| "One giant partition" | Bottleneck |

---


### 7.1 Log platform follow-ups

**Q: Why pull vs push consumers?**  
A: Pull lets consumer control pace and natural backpressure; push overloads slow consumers.

**Q: What if all ISR followers die?**  
A: With min.insync.replicas and unclean.leader=false, partition goes offline rather than lose data.

**Q: Exactly-once without transactions?**  
A: Not really — at-least-once + idempotent consumer processing is default honest answer.

**Q: How many partitions is too many?**  
A: When metadata/controller overhead and file handle count hurt; rule-of-thumb hundreds per broker, tune.

**Q: Hot partition mitigation?**  
A: Split topic, salt keys, upstream aggregation, or dedicated overweight partition.

**Q: KRaft vs ZooKeeper?**  
A: KRaft embeds metadata quorum in brokers; removes ZK ops burden.

**Q: Consumer stuck processing?**  
A: max.poll.interval.ms exceeded → rebalance; size processing or increase interval.

**Q: Log compaction use case?**  
A: Changelog topics; KV store rebuild from compacted topic.

**Q: MirrorMaker cross-DC?**  
A: Active-passive replication; offset mapping; not active-active same group easily.

**Q: Producer compression?**  
A: lz4/zstd default at scale; CPU vs bandwidth trade.

## 8. Appendices

### A. Pseudocode — produce to leader

```text
function produce(topic, partition, batch, acks):
  leader = metadata.leader(topic, partition)
  append_result = leader.log.append(batch)
  if acks == 0: return OK
  if acks == 1: return OK after local persist
  wait until all ISR replicas >= append_result.offset
  return OK
```

### B. Pseudocode — consumer fetch loop

```text
function consume_loop(assignments):
  while running:
    for (topic, part) in assignments:
      resp = broker.fetch(part, offset=committed[part])
      for record in resp.records:
        process(record)
      committed[part] = resp.next_offset
    coordinator.commit(committed)
```

### C. Metrics checklist

```text
under_replicated_partitions
offline_partitions_count
produce_latency_ms
fetch_consumer_lag
isr_shrinks_per_sec
log_flush_rate
request_queue_size
```

### D. Config cheat sheet

```text
replication.factor=3
min.insync.replicas=2
unclean.leader.election.enable=false
retention.ms=604800000
compression.type=lz4
```

### E. Related Databricks docs

- `batch-streaming-ingestion-system-design.md`  
- `pipeline-recovery-backpressure-system-design.md`  
- `lakehouse-object-storage-system-design.md`  



*End of kafka-like message queue HLD prep.*

---

## 5A. Checkpointing & effectively-once (merged)

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
