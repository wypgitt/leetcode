# System Design: Ordered Distributed Message Log (Kafka-like)

> **Focus areas:** Topics/partitions · Total order per partition · ISR/quorum replication · Producer acks · Consumer groups · Offset commit · Retention · Exactly-once / idempotent producers  
> **Style:** End-to-end infrastructure design with progressive scale (10× → 100× → 1,000×)  
> **Microsoft themes:** Azure Event Hubs–like concepts · regional Azure cells · Entra auth · Capture to Blob · private networking · compliance retention

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

Goal: **bound the log product**—ordering scope (partition vs global), durability (acks), consumer model (push vs pull, groups), and retention. This is the backbone behind Event Hubs / Kafka-style systems Microsoft candidates often design for Azure data platforms.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Abstraction? | Topics composed of partitions; append-only log | Partition = ordered unit |
| F2 | Ordering? | **Total order per partition**; no global order | Key → partition hash |
| F3 | Produce API? | Append batch; optional key, headers | Leader append path |
| F4 | Consume API? | Pull by offset; consumer groups | Group coordinator; offset store |
| F5 | Delivery? | At-least-once default; idempotent producer optional | Dedup on producer id/seq |
| F6 | Durability? | Replicated; configurable acks | ISR / quorum |
| F7 | Retention? | Time and/or size; optional compact | Segment files + cleaner |
| F8 | Replay? | Consumers reset offsets | Immutable log within retention |
| F9 | Multi-tenant? | Namespaces / event hubs per tenant | Quota + isolation |
| F10 | Schema? | Optional registry; bytes in log | Don’t block broker on schema |
| F11 | Geo? | DR replicate; some want dual ingest | Home cluster + async mirror |
| F12 | Capture? | Archive to Blob/ADLS | Secondary pipeline |

**MVP functional scope (lock with interviewer):**

1. Create **topics** with `N` partitions and replication factor `R`.  
2. **Produce** records (key, value, headers) to partition leaders; ack on quorum/ISR.  
3. **Consume** by offset; **consumer groups** with balanced partition assignment.  
4. Commit offsets (auto/manual).  
5. Retention by time/size; read from earliest/latest.  
6. Basic authN/Z (Entra / SAS-like tokens).  
7. Metrics: lag, ISR health, produce p99.  
8. Idempotent producer (PID + sequence) as strong MVP+.

**Out of MVP (explicitly defer):**

- Perfect global total order across partitions  
- Server-side stream processing engine (Flink/Spark)  
- Transactions across topics (mention Kafka EOS transactions as extension)  
- Infinite retention without tiered storage  
- Active-active dual writers same partition without CRDT/merge story  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Produce latency | Low in-region | p50 < 10ms, p99 < 50ms with local quorum |
| N2 | Durability | No loss if ack=all and ISR healthy | RPO≈0 for acked produces |
| N3 | Availability | Tolerate broker loss | Continue if ISR majority/enough replicas |
| N4 | Throughput | MB/s–GB/s per cluster | Batching + sequential disk/SSD |
| N5 | Ordering | Strict per partition | Single writer leader per partition |
| N6 | Consumer lag SLO | Workload-specific | Alert on lag age |
| N7 | Multi-region | Async mirror default | Failover with offset translation story |
| N8 | Scale | Millions partitions cluster-wide at extreme | See scale table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Producer sends keyed messages → same partition → consumers see monotonic offsets.  
2. Consumer group of `M` members → partitions assigned → commit offsets → restart resumes.  
3. Broker dies → new leader elected from ISR → producers/consumers refresh metadata.  
4. Retention deletes old segments; consumers near head unaffected.  
5. Idempotent producer retries → no duplicates in log.  
6. Capture pipeline copies segments to Blob for cold analytics.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Producer timeout unclear | Retry with idempotent PID → safe; without → possible dupes |
| Leader fails before follower flush | If ack=all waited ISR, OK; if ack=1, possible loss |
| Consumer crash before commit | Reprocess → at-least-once |
| Rebalance mid-processing | Revoke → commit careful → new owner |
| Hot partition (bad key) | Throughput ceiling = one leader; need key redesign |
| ISR shrinks to 1 | Durability risk; alert; maybe reject ack=all |
| Offset commit fenced | Old gen commits rejected (epoch) |
| Slow consumer | Lag grows; retention may delete unread (policy) |
| Huge message | Cap (e.g. 1 MB); reject or overflow store |
| Clock skew retention | Use append timestamps carefully; prefer broker log time |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Namespaces / tenants | 100 | 1K | 10K | 100K |
| Topics | 1K | 10K | 100K | 1M |
| Partitions (cluster) | 10K | 100K | 1M | 10M |
| Brokers | 10 | 50 | 300 | 3K |
| Produce records/s | 1M | 10M | 100M | 1B |
| Produce GB/s | 1 | 10 | 100 | 1K |
| Consumer groups | 1K | 10K | 100K | 1M |
| Concurrent consumers | 5K | 50K | 500K | 5M |
| Retention hot | 7d | 7d | 3d hot + tier | tiered |
| Avg record size | 1 KB | 1 KB | 1 KB | 800 B |
| Geo mirrors | 1 | 2 | many | many |

**What each jump forces:**

- **10×:** More partitions; batching; dedicated controllers; offset store scaled.  
- **100×:** Tiered storage (local SSD + Blob); partition-aware balancers; cell/clusters per tenant tier; quota enforcement.  
- **1,000×:** Hierarchical clusters (federation), metadata service scale-out, diskless/tier-first designs, careful consumer group coordinator sharding.

### 1.5 Etc. (Constraints & Assumptions)

- Ordering **only** within partition unless interviewer demands global (then single partition—scale trade-off).  
- Pull model for consumers (Kafka/Event Hubs style).  
- Disk sequential write is friend; random metadata is enemy.  
- Microsoft talk track: Event Hubs namespaces, throughput units/PUs, Capture, Azure Monitor, Private Link.

**Scope statement:**

> Design a multi-tenant ordered distributed message log: partitioned append-only topics, replicated leaders, producer acks, consumer groups with offset commits, retention/tiering, and progressive scale from ~1M to ~1B records/s—aligned with Azure Event Hubs / Kafka semantics.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS / bandwidth classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Produce records/s | 1M | 1B | Batch to reduce RPCs |
| Produce GB/s | 1 | 1K | Dominates cost |
| Fetch GB/s | ~1–3× produce | fanout | Multiple consumer groups |
| Offset commits/s | 10K | 10M | Coalesce! |
| Metadata requests | 1K | 1M | Cache aggressively |
| Replication ingress | ≈ produce × (R-1) | huge | Network planning |

**Critical:** Replication multiplies network. `R=3` ⇒ ~2× extra cross-rack bytes on produce path for followers.

### 2.2 Partition & leader math

```text
Baseline 1M records/s across 10K partitions ≈ 100 records/s/partition average
Hot key: one partition might take 50K+/s → ceiling from single leader disk/CPU

Per-broker: 10 brokers × balanced → 1K partitions each
Each partition leader sequential write; many partitions → page cache / SSD IOPS care
```

### 2.3 Storage

```text
Baseline: 1 GB/s × 86400 ≈ 86.4 TB/day ingest
Retain 7 days: ≈ 605 TB raw (pre-replication)
×3 replication ≈ 1.8 PB disk — painful
→ tiered: keep 24h local, older to Blob (1×) + optional EC

1,000×: 1 TB/s × 86400 = 86.4 PB/day → must have tiering + short hot retention
Unit check: 1 GB/s × 86400 = 86.4 TB/day ✓
```

### 2.4 Consumer fanout

```text
3 consumer groups reading full stream ≈ 3× fetch bandwidth
At 100 GB/s produce, 300 GB/s fetch + replication — network fabric is king
```

### 2.5 Memory

```text
Page cache for hot segments: tens–hundreds GB per broker
Producer/consumer connection buffers
Group coordinator state: groups × members — shard coordinators
```

### 2.6 Critical bottlenecks

1. Hot partitions / poor keys  
2. Replication bandwidth & slow followers (ISR thrash)  
3. Offset commit storms  
4. Rebalances (stop-the-world)  
5. Metadata storms on large clusters  
6. Disk fill from retention misconfig  
7. Small-record overhead without batching  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Namespace/Tenant → Topic → Partition → Segment files → Records
Broker (node) hosts replica replicas of partitions
Leader replica serves produce/fetch; followers replicate
Consumer Group → members → assigned partitions → offsets
Controller / Cluster coordinator manages leadership
```

**Record:**

```text
offset (per partition, monotonic)
timestamp
key, value, headers
optional producer_id, seq for idempotence
```

### 3.2 Options: coordination & leadership

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. ZooKeeper/old Kafka controller | Known | Ops complexity | Greenfield Microsoft stack preference |
| B. **Built-in Raft controllers (KRaft-like)** | Self-contained | Implementation complexity | — |
| C. External etcd | Clean | Another system | Latency/ops |
| D. Azure fabric naming | Cloud-native | Less portable | On-prem requirement |

**Chosen:** Internal **controller quorum** (Raft) for topic metadata + leadership; data plane uses **partition replica leader + ISR/quorum** (can also be Raft per partition—trade-offs below).

### 3.3 Options: replication per partition

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Leader/follower + ISR (Kafka classic) | High throughput | Mental model for unclean election | Unclean leader election ON in prod blindly |
| B. Raft per partition | Stronger mental model | More chatty; many Raft groups | Millions of partitions with heavy Raft overhead untuned |
| C. Quorum write to any | Flexible | Ordering harder | Need total order |

**Chosen path:** **Leader + ISR** with `min.insync.replicas` and `acks=all` for durable topics; controller assigns leaders. Optionally note Event Hubs uses quorum/epoch fencing conceptually similar.

### 3.4 Produce path

```text
1) Producer refreshes metadata: key→partition→leader broker
2) Send batch to leader
3) Leader appends to log (WAL/segment), assigns offsets
4) Leader waits until ISR replicas ack (if acks=all)
5) Respond to producer with base offset
```

**Idempotent producer:**

```text
PID + epoch + per-partition sequence
Leader rejects duplicates / out-of-order seq gaps per policy
```

### 3.5 Consume path & groups

```text
Group coordinator (per group hash):
  members heartbeat
  assign partitions (range, sticky, cooperative)
  store committed offsets

Consumer:
  fetch(partition, offset, max_bytes) from leader
  process
  commit offset (or auto)
```

**Rebalance goals:** minimize stop-the-world; prefer sticky/cooperative assignment.

### 3.6 Ordering guarantees (precision)

| Guarantee | True? |
|-----------|-------|
| Per-partition total order | Yes |
| Per-key order if same partition | Yes (if key hashing stable) |
| Cross-partition order | No |
| Causal global order | No without single partition |

**Deal-breaker claim:** “Kafka guarantees global ordering.”

### 3.7 Exactly-once reality

| Layer | Guarantee |
|-------|-----------|
| Idempotent produce | No dupes in log from retries |
| At-least-once consume | Default |
| EOS consume-process-produce | Needs transactions / idempotent sinks |
| Effectively once apps | Idempotent handlers + stored offsets carefully |

Do **not** claim end-to-end exactly-once for arbitrary consumers without extra protocol.

### 3.8 Retention & tiering

```text
Hot: local SSD segments
Warm/Cold: Azure Blob via tiered storage / Capture
Compaction (optional): keep latest key only (changelog topics)
Delete: by time/size on non-compacted topics
```

### 3.9 Multi-region

| Mode | Use |
|------|-----|
| Async mirror (geo-replication) | DR, analytics elsewhere |
| Active-passive failover | Promote mirror; consumers switch |
| Active-active produce | Avoid same partition dual-write |

**Offset translation:** mirrored clusters may remap offsets—use offset mapping or time-based reset.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Order unit | Partition | Scale via parallelism | Global single log |
| Durability | acks=all + min ISR | Safe | acks=0 for money events |
| Offset store | Compacted internal topic / table | Durable | Memory-only commits |
| Hot retention | Hours–days local | Cost | Infinite local disk |
| Batching | Producer & broker | Throughput | 1 record = 1 RPC at 1B/s |
| Multi-tenant | Namespaces + quotas | Isolation | Shared unconstrained topics |

---

## 4. Architecture Diagram

### 4.1 Cluster end-to-end

```text
 Producers (apps)                 Consumers (groups)
        |                                |
        v                                v
 +--------------+                 +--------------+
 | Gateways /   |                 | Gateways /   |
 | Endpoints    |                 | Endpoints    |
 +------+-------+                 +------+-------+
        |                                |
        +---------------+----------------+
                        v
              +------------------+
              | Broker Fleet     |
              | leaders/followers|
              +--------+---------+
                       |
         +-------------+-------------+
         v             v             v
   Segment Disk    Controller    Offset Coord
   (+ tier Blob)   Quorum (Raft)  / Group Coord
```

### 4.2 Produce sequence (acks=all)

```text
Producer → Leader: AppendBatch
Leader → Followers: Replicate
Followers → Leader: Ack
Leader → Producer: OffsetOK
```

### 4.3 Consumer group rebalance

```text
JoinGroup → SyncGroup → Assignment
Heartbeat loop
Revoke on leave → commit → new assignment
```

### 4.4 Leader failover

```text
Controller detects broker death
Picks new leader from ISR (highest HW/epoch rules)
Bumps leader epoch
Producers metadata refresh → fence old leader
```

### 4.5 Cells at 100×+

```text
 Tenant A → Cluster Cell 1 (region West US)
 Tenant B → Cluster Cell 2
 High-volume tenant → dedicated cell
 Mirror → East US DR cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Data loss prevention

- Durable ack only after ISR quorum on durable topics.  
- `min.insync.replicas >= 2` for production.  
- Disable unclean leader election for critical topics (prefer availability loss over silent loss).  
- Checksums on records/segments.  
- Controller metadata Raft-durable.

#### 5.1.2 Retries

- Producer retries with backoff + idempotence.  
- Consumer retries processing independently of fetch.  
- Replication backoff for stuck followers; shrink ISR if needed (alert!).

#### 5.1.3 Fencing

- **Leader epoch** on every append; old leader fenced.  
- **Producer epoch** for idempotent producers.  
- **Member generation / group epoch** fences old consumers’ offset commits.

#### 5.1.4 Rate limits & quotas

- Produce bytes/s per tenant/producer.  
- Fetch bytes/s per consumer group.  
- Request rate limits to protect brokers.  
- Partition count quotas per topic/namespace.

#### 5.1.5 Failure modes

| Failure | Mitigation |
|---------|------------|
| Leader crash | Elect from ISR; epoch++ |
| Slow follower | Remove from ISR; alert durability |
| Disk full | Block produce; expand/tier/delete |
| Split brain | Epoch fencing |
| Coordinator fail | Elect new coordinator; groups rejoin |
| Poison huge payload | Reject at produce |

### 5.2 Scalability

#### 5.2.1 Scale traffic up/down

- Add brokers; reassign partitions (throttled).  
- Increase partitions for more parallelism (**note:** key ordering across old/new needs care—prefer plan partitions ahead).  
- Autoscale fetchers/gateways.  
- Shrink: drain partitions, decommission brokers.

#### 5.2.2 Storage scale

- Tiered storage to Blob.  
- Compaction for changelog topics.  
- Segment rolling by size/time.  
- Separate disks for data vs OS.

#### 5.2.3 Parallelization

- Parallelism = partition count (for ordered processing).  
- Consumer instances ≤ partitions for active owners (more = idle).  
- Produce parallel across partitions freely.

#### 5.2.4 Progressive evolution

| Scale | Architecture |
|-------|--------------|
| 1× | Single cluster, RF=3, local disk, one controller quorum |
| 10× | Many brokers, quotas, monitoring ISR, batching defaults |
| 100× | Tiered storage, multi-cluster cells, dedicated noisy tenants |
| 1000× | Federated routing, diskless/tier-first, coordinator sharding, geo hierarchy |

### 5.3 Maintainability

- Clear APIs: Admin (topics), Produce, Fetch, Group.  
- Compatibility: evolving record formats with magic bytes.  
- Operability: preferred replica election, controlled shutdown, throttle reassignment.  
- Observability: under-replicated partitions, produce/fetch latency, lag by group.  
- Naming: `namespace.topic` multi-tenant hygiene.  
- Chaos: kill leaders, truncate network, fill disks in staging.

---

## 6. Wrap-Up

**Built:** A Kafka/Event Hubs–class ordered log—partitioned topics, leader/ISR replication, producer acks + idempotence, consumer groups with fenced offset commits, retention/tiering, and cell-based multi-tenant scale on Azure.

**Memorable lines:** Order is per partition; durability is acks+ISR; fanout and replication dominate cost; hot keys kill you; fencing epochs everywhere.

---

## 7. Deeper / Related Interview Questions

### 7.1 Ordering & keys

**Q: How to preserve order for a user?**  
A: Use `user_id` as key so all go to one partition.

**Q: Why not one partition always?**  
A: Throughput ceiling; no parallel consumers.

**Q: Increase partitions later?**  
A: Old keys may map differently if hash uses partition count—plan capacity; use sticky partitioning schemes carefully.

### 7.2 Acks & durability

**Q: acks=0/1/all?**  
A: 0 fire-and-forget; 1 leader only; all ISR—choose by loss tolerance.

**Q: Unclean leader election?**  
A: Availability vs durability; off for money/ledger topics.

### 7.3 Exactly-once

**Q: Is Kafka exactly-once?**  
A: Idempotent produce + transactions for read-process-write; consumers still need care. Prefer precise language.

**Q: Duplicate consumer processing?**  
A: If crash before offset commit → yes. Make handlers idempotent.

### 7.4 Memory / storage

**Q: Keep all data in RAM?**  
A: No—page cache helps hot tail; storage is disk/object.

**Q: RocksDB on broker?**  
A: Optional for state stores in processors; not required for raw log.

**Q: Offset commit every message?**  
A: Deal-breaker at scale—batch commits; accept reprocess window.

### 7.5 DB comparisons

**Q: Why not store messages in SQL?**  
A: Sequential log + fanout consumers + retention GC outperform row stores for this workload.

**Q: vs Service Bus queues?**  
A: Queues: competing consumers, per-message ack, richer messaging patterns. Logs: replay, high throughput, partition order.

**Q: vs Event Grid?**  
A: Event Grid is reactive delivery; not a durable multi-consumer replay log.

### 7.6 Load balancing & hashing

**Q: Partition assignment strategies?**  
A: Range, sticky, cooperative sticky; avoid ping-pong rebalances.

**Q: Consistent hashing for keys?**  
A: Kafka uses `hash(key) % N` typically—not consistent hashing; changing N reshuffles.

### 7.7 Algorithms

**Q: How is high watermark computed?**  
A: Min offset among ISR replicas’ caught-up points (classic model).

**Q: Zero-copy sendfile?**  
A: Brokers often optimize fetch path with sendfile/page cache.

**Q: Compaction algorithm?**  
A: Keep last record per key; dirty ratio triggers cleaner.

### 7.8 Multi-tenant Azure

**Q: Noisy neighbor?**  
A: Throughput quotas, separate TU/PU, dedicated clusters for whales.

**Q: Private networking?**  
A: Private Link / VNet inject endpoints.

**Q: Capture to Blob?**  
A: Async archival; don’t block produce on Capture lag (buffer/alert).

### 7.9 Rebalance pain

**Q: Stop-the-world rebalance?**  
A: Use cooperative assignment; increase session timeouts carefully; static membership where available.

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| Global ordering at high QPS | Single partition ceiling |
| acks=1 for payments | Loss window |
| Offset in Redis only | Durability/consistency risk |
| Consumer count ≫ partitions always helps | Idle consumers |
| 1 GB/s × day = 1 GB | **~86 TB/day** |
| Active-active same partition | Split brain / order break |

### 7.11 Related Microsoft systems

**Q: Event Hubs vs Kafka protocol?**  
A: Event Hubs provides Kafka-compatible endpoints; designing “message log” maps cleanly.

**Q: Where does this sit under Fabric / analytics?**  
A: Ingest spine → Stream Analytics / Spark / Flink consumers.

---

## 8. Appendices

### 8.1 API checklist

- [ ] Admin: create/delete topic, describe, alter config  
- [ ] `Produce(topic, partition|key, batch)`  
- [ ] `Fetch(topic, partition, offset, max_bytes)`  
- [ ] Group: Join/Sync/Heartbeat/Leave  
- [ ] `CommitOffsets` / `FetchOffsets`  
- [ ] Metadata refresh  
- [ ] Mirror / Capture config  

### 8.2 Schema / record layout sketch

```text
RecordBatch {
  baseOffset, partitionLeaderEpoch,
  records: [{ offsetDelta, timestamp, key, value, headers,
              producerId, producerEpoch, seq }]
}
Segment: *.log + *.index + *.timeindex
```

### 8.3 Invariants

1. Offsets strictly increasing per partition for acknowledged records.  
2. Only leader accepts produces for a partition epoch.  
3. Consumers never read above high watermark (durability visibility).  
4. Group generation fences stale commits.  
5. Idempotent seq prevents duplicate appends from same PID/epoch.  
6. ISR membership changes are controller-authorized.

### 8.4 Progressive scale playbook

| Scale | Must have |
|-------|-----------|
| 1× | Partitions, RF=3, acks=all, groups, retention |
| 10× | Quotas, idempotent producers, ISR alerts |
| 100× | Tiered storage, cells, throttle reassignment |
| 1000× | Federation, coordinator shards, tier-first |

### 8.5 Producer settings worksheet

```text
acks=all
enable.idempotence=true
linger.ms=5..20
batch.size=64KB..512KB
max.in.flight.requests.per.connection=5 (with idempotence)
retries=BIG
```

### 8.6 Consumer settings worksheet

```text
enable.auto.commit=false (for critical)
max.poll.interval.ms tuned to processing
session.timeout / heartbeat balanced
fetch.min.bytes / max.wait.ms for efficiency
```

### 8.7 Capacity worksheet

```text
partitions >= max(target_parallel_consumers, produce_rate / per_part_rate)
disk_hot ≈ ingest_rate × hot_retention × RF
disk_cold ≈ ingest_rate × cold_retention × (1 or EC)
nic_per_broker ≥ (produce + fetch_fanout + replication) / brokers × headroom
```

### 8.8 Offset commit store options

| Option | Notes |
|--------|-------|
| Internal compacted topic | Kafka classic `__consumer_offsets` |
| Table in meta DB | Event Hubs–like control plane |
| Client-managed | App DB; broker unaware |

### 8.9 Leadership election sketch

```text
on broker failure:
  for each partition whose leader was broker:
    candidates = ISR
    pick by replica priority / offset / rack awareness
    leader_epoch++
    notify brokers + metadata version++
```

### 8.10 Hot partition mitigations

1. Better keys / salting with care for order.  
2. Split entity into subkeys if order allows.  
3. Dedicated partitions for whales.  
4. Application-level sharding of entity ids.

### 8.11 SLO examples

| SLO | Target |
|-----|--------|
| Produce p99 (acks=all, in-AZ) | < 50 ms |
| Under-replicated partitions | 0 steady-state |
| Unclean elections | 0 |
| Consumer lag age (critical) | < 60 s |

### 8.12 Interview 60-second summary

> Append-only **partitioned log** with a **single leader** per partition for total order. Replicate to ISR; ack produces on quorum for durability. Consumers pull by offset in **groups** with fenced commits. Scale out by partitions and brokers; control hot keys; tier cold data to Blob. Multi-region via mirror, not dual-active writers. On Azure, this is the Event Hubs mental model.

### 8.13 Related systems map

```text
Producers → Leaders → Followers (ISR)
                ↓
             Segments → Tier/Blob
                ↓
 Consumers ← Fetch ← Leaders
     ↓
 Group Coord / Offsets
```

### 8.14 Security checklist

- [ ] Entra / SAS auth  
- [ ] TLS in transit  
- [ ] Encryption at rest  
- [ ] ACLs per topic  
- [ ] Private Link  
- [ ] Audit admin ops  

### 8.15 Failure injection plan

1. Kill partition leader → epoch fence → no split brain.  
2. Block follower → ISR shrink → alert; with min ISR produce may fail (good).  
3. Slow rebalance → cooperative assignment validation.  
4. Fill disk → produce fails loudly.  
5. Duplicate produce retry with PID → one record.

### 8.16 Glossary

| Term | Meaning |
|------|---------|
| Partition | Totally ordered log slice |
| Offset | Monotonic index in partition |
| ISR | In-sync replicas set |
| Leader epoch | Fencing token for leadership |
| HW / HWM | High watermark (committed visibility) |
| Consumer group | Competing/collaborative consumers set |
| Rebalance | Redistribute partitions among members |
| Tiered storage | Hot local + cold object |

### 8.17 Comparison matrix

| System | Order | Replay | Competing consume |
|--------|-------|--------|-------------------|
| This log | Per partition | Yes | Via groups |
| Queue | Per queue approx | Limited | Natural |
| Pub/Sub push | Per topic approx | Limited | Filters |

### 8.18 Transactions extension (mention only)

```text
Atomic writes across partitions + offset commits in one txn
Requires txn coordinator + control records
Heavy; only if interviewer pushes EOS pipelines
```

### 8.19 Multi-cluster routing

```text
Client → Routing layer (namespace → cluster cell)
Whales → dedicated cell
DR → mirror cell (read-only until promote)
```

### 8.20 Math traps cheat sheet

```text
1 MB/s × 1 day = 86.4 GB
1 GB/s × 1 day = 86.4 TB
1 TB/s × 1 day = 86.4 PB
RF=3 triples hot disk
3 consumer groups ≈ 3× read amplify
```

### 8.21 Rack awareness

```text
Place replicas in different AZs/racks
Prefer leader in same AZ as majority producers when possible
Never all ISR in one rack
```

### 8.22 Message size & batching policy

| Size | Policy |
|------|--------|
| ≤ 1 MB | Normal |
| > 1 MB | Reject or externalize to Blob + pointer record |
| Tiny 100 B | Must batch aggressively |

### 8.23 Controller responsibilities

- Topic create/delete  
- Partition reassignment  
- Leader election  
- Cluster membership  
- Preferred leader restoration  

Keep controllers **out of** data path for produce/fetch.

### 8.24 Why sequential logs win

- Append throughput  
- Cheap replication  
- Natural replay  
- Simple mental model for offset cursors  

Trade-off: not a good primary store for point mutates (use compacted changelog + state store).

---



### 8.25 Consumer lag & backpressure

```text
lag_messages = log_end_offset - consumer_committed_offset
lag_time ≈ time(log_end) - time(committed)

Alerts:
  lag_time > SLO → scale consumers / fix hot partition / slow handler
Backpressure:
  if disk tiering lag or ISR degraded → throttle produce (better than silent loss)
```

**Never** solve lag only by skipping commits— that loses process tracking.

### 8.26 Exactly-once pipeline pattern (app level)

```text
consume record
process → write sink with idempotency key = topic-partition-offset
after sink ACK → commit offset
```

Or transactional produce to output topic + offset commit in one Kafka transaction (advanced).

### 8.27 Compacted topic use cases

| Use case | Why compaction |
|----------|----------------|
| Consumer offsets | Latest per group-partition key |
| Changelog for KTables | Latest state per key |
| Config bus | Latest config per entity |

**Trade-off:** Compaction is not delete-by-time alone; dual cleanup policies available (`compact,delete`).

### 8.28 Serde & schema evolution

- Brokers treat payloads as opaque bytes (good).  
- Schema Registry (Avro/Protobuf/JSON Schema) outside broker path.  
- Compatibility: FORWARD / BACKWARD / FULL—product choice.  
- **Deal-breaker:** Broker parses and validates every schema on produce at 1B/s.

### 8.29 Rack / AZ placement example

```text
RF=3, cluster across AZ1, AZ2, AZ3
replica 0 → AZ1, replica 1 → AZ2, replica 2 → AZ3
min.insync.replicas=2
acks=all
→ survives one AZ loss without data loss (usually)
```

If two AZs die, availability suffers—honest CAP talk.

### 8.30 Mirror / DR runbook

```text
1) Continuous async replicate topics to DR cluster
2) Monitor mirror lag
3) On disaster: stop producers; wait mirror drain OR accept RPO=lag
4) Promote DR; update DNS / connection strings
5) Consumers reset using timestamps or offset maps
6) Prevent old primary from accepting writes (fence)
```

### 8.31 Quotas detailed

| Quota | Protects |
|-------|----------|
| Produce byte rate / tenant | Noisy neighbor |
| Produce request rate | Controller/broker CPU |
| Fetch byte rate / group | Network fairness |
| Partition creation count | Metadata explosion |
| Connection count | FD exhaustion |

Fail policy: `throttle` (preferred) vs `reject`.

### 8.32 Interview 5-minute outline

1. Partition = order unit.  
2. Leader/ISR produce path + acks.  
3. Consumer groups + commits + fencing.  
4. Retention/tiering math.  
5. Hot keys + scale cells.  
6. Event Hubs mapping on Azure.

### 8.33 Anti-patterns checklist

- [ ] One topic one partition for “simplicity” at high QPS  
- [ ] acks=0 for critical ledger events  
- [ ] Auto-commit + non-idempotent side effects  
- [ ] Unlimited retention on SSD  
- [ ] Rebalance storms ignored  
- [ ] Dual-active multi-region producers same key space  

### 8.34 Throughput worksheet (per partition)

```text
seq_write_MB_s_per_leader ≈ disk_or_nic_limit
records_s ≈ seq_write_MB_s × 1e6 / avg_record_bytes
cluster_records_s ≈ records_s × num_partitions × balance_factor(0.5..0.8)
```

If measured hot partition ≪ average, fix keys before adding brokers.

### 8.35 Header conventions (app)

```text
traceparent / correlation_id
content-type
producer timestamp vs broker timestamp
idempotency-key (app-level, in addition to PID)
```

### 8.36 When NOT to use an ordered log

- Low-volume request/response RPC  
- Large file transfer (use Blob)  
- Soft real-time fanout to millions of mobile devices (use notification system)  
- Strict queue with per-message visibility timeout as primary UX (consider queue product)

---

*End of ordered distributed message log system design.*
