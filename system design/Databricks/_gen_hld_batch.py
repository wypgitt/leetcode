#!/usr/bin/env python3
"""Generate missing Databricks HLD docs from references + custom content."""
from pathlib import Path
from _gen_helpers import APPENDIX_X, OUT, write

ROOT = OUT.parent

def adapt(src_rel, dst_name, title_override=None, theme_line=None, focus_line=None):
    src = ROOT / src_rel
    if not src.exists():
        raise FileNotFoundError(src)
    text = src.read_text()
    # Normalize header block for Databricks
    if title_override and text.startswith("# System Design:"):
        first_nl = text.index("\n")
        text = f"# System Design: {title_override}" + text[first_nl:]
    if theme_line:
        text = text.replace(
            "**Interview theme:** Amazon SDE III / L6 — **Dropbox-like file storage / sync** — reliable sync at consumer+enterprise scale",
            theme_line,
        )
        text = text.replace(
            "**Interview theme:** Classic Meta/infra storage interview — API compatibility with S3 mental model, 11-nines thinking, multipart, and listing realities",
            theme_line,
        )
        if "**Interview theme:**" not in text[:800]:
            # inject after quality bar
            needle = "> **Quality bar:**"
            idx = text.find(needle)
            if idx >= 0:
                end = text.find("\n\n", idx)
                text = text[:end] + f"\n> **Interview theme:** Databricks — {theme_line.split('—',1)[-1].strip()}" + text[end:]
    if focus_line and "> **Focus areas:**" in text[:600]:
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith("> **Focus areas:**"):
                lines[i] = f"> **Focus areas:** {focus_line}"
                break
        text = "\n".join(lines)
    # Append Databricks tail if missing Appendix X
    if "## Appendix X — Extended Interview Drill" not in text:
        if "*End of" not in text[-200:]:
            text = text.rstrip() + "\n\n" + APPENDIX_X + "\n"
        stem = dst_name.replace("-system-design.md", "").replace("-", " ")
        text = text.rstrip() + f"\n\n*End of {stem} HLD prep.*\n"
    return text

def gen_if_missing(name, body):
    path = OUT / name
    if path.exists():
        n = path.read_text().count("\n")
        print(f"SKIP {name}: {n} lines (exists)")
        return n
    return write(name, body)


def job_scheduler():
    t = adapt(
        "OpenAI/distributed-job-scheduler-system-design.md",
        "job-scheduler-system-design.md",
        title_override="Distributed Job Scheduler",
        focus_line="DAG/workflows · Leases/heartbeats · Retries · Priorities · Worker failure · Cron/delayed jobs · Multi-tenant fairness",
    )
    if "**Interview theme:**" not in t[:900]:
        t = t.replace(
            "> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership of work, honest MVP vs extreme-scale paths\n",
            "> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership of work, honest MVP vs extreme-scale paths\n> **Interview theme:** Databricks — general-purpose distributed scheduler; classic HLD with lease/fencing depth\n",
        )
    t = t.replace("*End of distributed job scheduler prep.*", "*End of job scheduler HLD prep.*")
    return t


def s3_object_storage():
    t = adapt(
        "Meta/s3-like-object-storage-system-design.md",
        "s3-object-storage-system-design.md",
        title_override="S3-like Object Storage",
        theme_line="**Interview theme:** Databricks — lakehouse object storage foundation; metadata/data plane split, multipart, durability",
        focus_line="Bucket/key model · Multipart upload · Metadata vs data plane · Durability · Replication · Consistency · Listing · GC",
    )
    t = t.replace("S3-like Object Storage", "S3-like Object Storage")
    t = t.replace("*End of s3-like object storage prep.*", "*End of s3 object storage HLD prep.*")
    if "*End of" not in t[-120:]:
        t = t.rstrip() + "\n\n*End of s3 object storage HLD prep.*\n"
    return t


def dropbox_file_sync():
    t = adapt(
        "Amazon/dropbox-like-file-storage-system-design.md",
        "dropbox-file-sync-system-design.md",
        title_override="Dropbox File Sync",
        theme_line="**Interview theme:** Databricks — file sync, chunking, metadata correctness; pairs with ranged-file-cache LLD",
        focus_line="Chunking · Dedup · Sync protocol · Metadata · Sharing · Versioning · Conflict · Multi-device",
    )
    t = t.replace("Dropbox-like File Storage", "Dropbox File Sync")
    t = t.replace("*End of dropbox-like file storage prep.*", "*End of dropbox file sync HLD prep.*")
    return t


def gpu_scheduler():
    t = adapt(
        "OpenAI/gpu-scheduler-credits-system-design.md",
        "gpu-scheduler-system-design.md",
        title_override="GPU Scheduler",
        theme_line="**Interview theme:** Databricks — GPU/ML compute scheduling; fairness, preemption, gang scheduling hooks",
        focus_line="GPU pools · Gang scheduling · Preemption · Fair share · Quotas · Job placement · Fragmentation · Multi-tenant",
    )
    t = t.replace("GPU Scheduler (Credits & Fair Share)", "GPU Scheduler")
    t = t.replace("*End of gpu scheduler credits prep.*", "*End of gpu scheduler HLD prep.*")
    if "**Interview theme:**" not in t[:900]:
        t = t.replace(
            "> **Quality bar:**",
            "> **Interview theme:** Databricks — GPU cluster scheduling for ML workloads\n> **Quality bar:**",
            1,
        )
    return t


def kafka_mq():
    return f"""# System Design: Kafka-like Distributed Message Queue

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

{APPENDIX_X}

*End of kafka-like message queue HLD prep.*
"""


def visa_payment_routing():
    return f"""# System Design: Visa-like Payment Routing Network

> **Focus areas:** Authorization routing · Issuer/acquirer · BIN lookup · Idempotency · Ledger · Settlement · Fraud hooks · PCI boundaries · Multi-region
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct money arithmetic (integer minor units), explicit auth/capture/settlement, no double-charge under retries
> **Interview theme:** Databricks — high-reliability financial routing; saga + idempotency patterns

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

Goal: **bound a card-payment routing network**—route authorization requests from merchants/acquirers to the correct issuer, handle declines, idempotency, and async settlement—without storing raw PAN in logs.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Role? | **Network/router** like Visa—connect acquirers to issuers | Not full issuer core banking |
| F2 | Flow? | Auth → (optional capture) → clearing/settlement | State machine |
| F3 | Routing key? | PAN/BIN → issuer institution | BIN table + rules |
| F4 | Idempotency? | Same merchant ref must not double auth | Idempotency store |
| F5 | Amount? | Integer minor units + currency | No floats |
| F6 | Declines? | Structured response codes | Mapping table |
| F7 | Refunds/reversals? | Partial/full reversal APIs | Linked txn ids |
| F8 | Fraud? | Score/hold hooks | Pre-auth fraud service |
| F9 | PCI? | Tokenized PAN; HSM for crypto ops | Segmented zones |
| F10 | Multi-currency? | FX at settlement or auth | Rate service |
| F11 | Offline issuer? | Stand-in processing optional | Policy + risk |
| F12 | Reporting? | Merchants need status + settlement files | Batch exports |

**MVP functional scope:**

1. `POST /authorize` — route to issuer, return approve/decline.  
2. BIN-based routing table with health overrides.  
3. Idempotent requests via `(merchant_id, idempotency_key)`.  
4. `capture`, `void`, `refund` linked to auth.  
5. Durable txn log; async settlement batching.  
6. Basic fraud pre-check hook (sync timeout budget).  
7. Tokenized PAN handling; no PAN in app logs.

**Out of MVP:** Full chip/PIN crypto in HSM; cross-border licensing matrix; crypto stablecoin rails.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Auth latency | Interactive POS/ecom | p99 < 300–500ms end-to-end |
| N2 | Availability | Critical | 99.99% auth API |
| N3 | Durability | No lost approved auths | Persist before issuer ACK to merchant |
| N4 | Correctness | No double charge | Idempotency + ledger |
| N5 | Throughput | See scale table | Horizontal stateless routers |
| N6 | Compliance | PCI DSS segmentation | Token vault, audit |
| N7 | Audit | Immutable txn history | Append-only log |
| N8 | DR | Active-passive or active-active read | Home region for txn writer |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Merchant auth $50 → BIN routes to Issuer A → approve → auth code returned.  
2. Capture later for $50 → settlement batch includes txn.  
3. Partial capture $30 of $50 auth.  
4. Void before capture releases hold.  
5. Refund after capture links to original.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate auth retry | Return original result |
| Issuer timeout | Retry idempotent to issuer if safe; else unknown → inquiry |
| Unknown auth result | Do not auto retry new auth; reconciliation job |
| Partial issuer outage | Route backup link if configured; else decline |
| Amount mismatch capture | Reject capture > authorized |
| Currency mismatch | Decline |
| Fraud service slow | Fail open vs closed — **pick closed** for interview |
| Settlement file duplicate | Idempotent settlement ingestion |
| Clock skew | Network time for batch windows |
| Token expired | Decline with code |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak auth QPS | 5K | 50K | 500K | 5M |
| Issuers connected | 500 | 2K | 10K | 50K |
| Merchants | 100K | 1M | 10M | 100M |
| Daily txns | 50M | 500M | 5B | 50B |
| Auth payload | ~1 KB | same | same | same |
| Settlement batch size | Hourly files | same | streaming | streaming |
| Regions | 1 | 2 | 5 | global |

**What each jump forces:**

- **10×:** Shard idempotency store; connection pools to issuers; rate limits.  
- **100×:** Geo routing; stand-in policies; async settlement pipeline.  
- **1,000×:** Cell architecture per region; hierarchical BIN tables; edge auth caching for repeat merchants.

### 1.5 Etc.

- Money as **int64 minor units**.  
- **No float** anywhere.  
- PCI: PAN only in vault/HSM enclave.  
- Scope: routing network, not merchant POS hardware.

**Scope statement:**

> Design a Visa-like payment router authorizing card transactions with BIN-based issuer routing, idempotent APIs, durable txn state, fraud hooks, and batch settlement—scaling from ~5K auth QPS with strict no-double-charge semantics.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Auth QPS and connections

```text
Baseline 5K auth QPS
Avg issuer RTT 80ms → concurrent connections ≈ 5K × 0.08 = 400 per issuer class (pooled)
1000 issuers — connection pool per issuer institution, not per txn thread
```

### 2.2 Storage

```text
Txn record ~2 KB with metadata
50M txns/day × 2 KB ≈ 100 GB/day
7 years retention regulatory → compress + cold archive → PB scale
Hot store 90 days ≈ 9 TB
```

### 2.3 Bandwidth

```text
5K QPS × 1 KB req + 1 KB resp ≈ 10 MB/s
500K QPS → 1 GB/s — need regional edge aggregation
```

### 2.4 Settlement

```text
50M txns/day batch files — stream to warehouse; not on auth hot path
```

### 2.5 Bottlenecks

1. Issuer tail latency  
2. Idempotency hot keys (same merchant retries)  
3. BIN table update propagation  
4. Fraud sync path  
5. Ledger write contention for high-volume merchant  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
AuthorizationRequest   → merchant, token_pan, amount, currency, idempotency_key
RoutingDecision        → issuer_endpoint, protocol, timeout
IssuerAdapter          → ISO8583/JSON mapping per issuer
Transaction            → state machine + auth_code + links
IdempotencyRecord      → key → response snapshot
SettlementBatch        → cleared txns for net settlement
BinRange               → start_bin, end_bin → issuer_id
FraudDecision          → allow/deny/review
LedgerEntry            → double-entry audit (optional MVP hook)
```

### 3.2 Auth state machine

```text
INIT → FRAUD_CHECK → ROUTING → ISSUER_PENDING → APPROVED | DECLINED | UNKNOWN
CAPTURE: AUTHORIZED → CAPTURED → SETTLED
VOID: AUTHORIZED → VOIDED
REFUND: CAPTURED → REFUND_PENDING → REFUNDED
```

### 3.3 Routing table

```text
Longest-prefix match on BIN (6–8 digits)
Overrides: issuer maintenance → secondary route or decline
Health: circuit breaker per issuer link
```

### 3.4 Idempotency

```text
Key = (merchant_id, idempotency_key)
On duplicate: return stored response including auth_code
TTL ≥ max merchant retry window (24–72h)
```

### 3.5 Options: sync vs async issuer

| Mode | When |
|------|------|
| Sync HTTP/ISO | MVP auth |
| Async callback | Slow issuers Phase 2 |

**Chosen:** Sync with tight timeout + inquiry for unknown.

### 3.6 Capture vs auth

```text
Auth holds limit on issuer side (days)
Capture confirms amount ≤ authorized
Multi-capture partial until auth exhausted
```

### 3.7 PCI architecture

```text
Merchant → Tokenization gateway → Router sees tokens only
HSM zone for translate/detokenize at issuer boundary if needed
Logs: txn_id, token_id, last4, never PAN
```

---

## 4. Architecture Diagram

### 4.1 Components

```text
Merchant/POS → Acquirer Gateway → +------------------+
                                   | Auth API         |
                                   +--------+---------+
                                            |
                    +-----------------------+----------------------+
                    |                       |                      |
             +------v------+        +-------v-------+      +-------v------+
             | Idempotency |        | Router/BIN    |      | Fraud Scoring|
             | Store       |        | Service       |      | Service      |
             +-------------+        +-------+-------+      +--------------+
                                            |
                                    +-------v-------+
                                    | Issuer        |
                                    | Adapters      |
                                    +-------+-------+
                                            |
                                    +-------v-------+
                                    | Issuer banks  |
                                    +---------------+

        Settlement Worker ← Txn Log → Data warehouse / files
```

### 4.2 Auth sequence

```text
Acquirer     AuthAPI      Fraud      Router      Issuer
  |--auth--->|            |           |           |
  |          |--score---->|           |           |
  |          |<-allow-----|           |           |
  |          |--route BIN------------>|           |
  |          |                       |--auth---->|
  |          |                       |<-code-----|
  |          |--persist txn---------|           |
  |<-200-----|            |           |           |
```

### 4.3 Unknown result recovery

```text
Worker polls issuer inquiry API with original stan/id
Update txn APPROVED/DECLINED
Notify acquirer via webhook if still pending
Never issue second auth with new idempotency key for same purchase
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. At most one **approved** auth per `(merchant_id, idempotency_key)`.  
2. Capture sum ≤ authorized amount.  
3. Approved txn persisted **before** returning approve to merchant.  
4. Ledger entries balanced if ledger enabled.

**Payment uncertainty protocol**

```text
if issuer response unknown:
  mark UNKNOWN
  do NOT return approve/decline blindly
  run inquiry with same txn reference
  merchant retry with SAME idempotency key → return cached final state
```

### 5.2 Scalability

| Scale | Approach |
|-------|----------|
| 1× | Monolith router + Postgres txns + Redis idempotency |
| 10× | Stateless API pods; shard idempotency by merchant hash |
| 100× | Regional cells; issuer connection pools; async settlement |
| 1000× | Hierarchical routing; edge BIN cache; dedicated fraud ML async |

### 5.3 Maintainability

- Issuer adapter plugin interface.  
- BIN file daily import with versioned rollout.  
- Simulation environment with recorded issuer fixtures.  
- Metrics: approve rate, latency by issuer, unknown rate, fraud block rate.

### 5.4 Progressive scale

**1×:** Sync auth, Postgres, Redis idempotency, nightly settlement CSV.

**10×:** Kafka txn event bus; fraud async for low-risk merchants.

**100×:** Multi-region active-passive; stand-in rules documented.

**1000×:** Cell per continent; regulatory data residency.

### 5.5 Fraud hook

```text
Sync budget 50ms:
  if fraud timeout → decline (fail closed)
Optional: step-up 3DS flow async — out of MVP
```

### 5.6 Settlement

```text
End of day: aggregate CAPTURED txns per merchant/issuer
Net settlement files; idempotent file ingestion
Disputes/chargebacks separate workflow
```

---

## 6. Wrap-Up

**Summary:** Tokenized auth API → fraud → BIN router → issuer adapter → durable txn log with idempotency; capture/void/refund as linked state transitions; settlement off hot path.

**Top risks:** unknown auth handling; double capture; issuer timeout storms; PCI scope creep.

---

## 7. Deeper / Related Interview Questions

1. Auth vs capture vs sale (single message).  
2. How BIN table updates propagate globally?  
3. Stand-in processing risks?  
4. Exactly-once settlement with at-least-once files?  
5. Compare to Stripe Connect model.  
6. ISO8583 vs REST issuer adapters.  
7. Handle partial approvals?  
8. Multi-currency DCC flow.  
9. Chargeback lifecycle.  
10. PCI SAQ levels for components.

**Interviewer traps**

| Trap | Answer |
|------|--------|
| Store PAN in DB | Token vault + scope |
| Float dollars | Integer minor units |
| Retry new idempotency on unknown | Inquiry + same key |
| Skip durable write before ACK | Never |

---

## 8. Appendices

### A. Pseudocode — authorize

```text
function authorize(req):
  cached = idem.get(req.merchant, req.idem_key)
  if cached: return cached

  fraud = fraud.check(req) with timeout 50ms
  if fraud.deny: return decline(FRAUD)

  issuer = router.lookup_bin(req.token_bin)
  txn = db.create(PENDING, req)

  try:
    resp = issuer.auth(req, timeout=200ms)
  catch Timeout:
    txn.state = UNKNOWN; db.save(txn)
    return pending_unknown(txn.id)

  txn.apply(resp)
  db.save(txn)
  idem.put(req.merchant, req.idem_key, txn.response)
  return txn.response
```

### B. Data model sketch

```text
transactions(txn_id, merchant_id, idem_key, amount, currency, state,
             issuer_id, auth_code, parent_txn_id, created_at)
bin_ranges(prefix, issuer_id, priority)
issuer_endpoints(issuer_id, url, protocol, timeout_ms, cb_state)
idempotency(merchant_id, key, txn_id, response_json, expires_at)
```

### C. Metrics

```text
auth_latency_ms{{issuer}}
auth_approve_rate
auth_unknown_rate
idem_hit_rate
issuer_circuit_open
settlement_lag_hours
```

{APPENDIX_X}

*End of visa payment routing HLD prep.*
"""


if __name__ == "__main__":
    jobs = [
        ("job-scheduler-system-design.md", job_scheduler),
        ("s3-object-storage-system-design.md", s3_object_storage),
        ("dropbox-file-sync-system-design.md", dropbox_file_sync),
        ("gpu-scheduler-system-design.md", gpu_scheduler),
        ("kafka-like-message-queue-system-design.md", kafka_mq),
        ("visa-payment-routing-system-design.md", visa_payment_routing),
    ]
    for name, fn in jobs:
        gen_if_missing(name, fn())
