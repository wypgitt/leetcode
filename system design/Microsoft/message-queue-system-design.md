# System Design: Message Queue

> **Focus areas:** Producer/consumer · Topics & queues · Ack/visibility · At-least-once · Ordering & partitions · Retries/DLQ · Fan-out · Backpressure · Multi-tenant fairness · Durability  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct delivery semantics, explicit ordering boundaries, honest exactly-once discussion, deal-breakers for “infinite invisible queue on one disk”  
> **Interview theme:** Microsoft — Service Bus / Event Hubs / Azure Queue–shaped messaging primitives; clean API + reliability

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

Goal: **bound the product**—a **managed message queue / pub-sub messaging service** that accepts producer publishes, durably stores messages, and delivers to competing consumers and/or fan-out subscriptions with configurable ack, retry, DLQ, and optional ordering—at cloud scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Durable messaging between services | RPC replacement for all sync calls |
| Shape | Queues + topics/subscriptions (hybrid) | Only Kafka log OR only SQS—mention both modes |
| Delivery | At-least-once default; exactly-once *effects* via idempotency | Magical exactly-once for arbitrary side effects |
| Ordering | Per key / per partition / per session | Global total order for all messages |
| Microsoft lens | Service Bus + Event Hubs concepts | Database CDC product alone |

**Scope statement:**

> Design a multi-tenant cloud message queue supporting point-to-point queues and pub-sub topics, durable storage, visibility-timeout or cursor ack modes, retries/DLQ, optional per-key ordering, competing consumers, and fair multi-tenant isolation—from ~100K msg/s through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Queue vs topic? | Both: queue (competing) + topic (fan-out subs) | Unified log + consumer groups OR SB-like entities |
| F2 | Delivery? | At-least-once | Ack + retry; idempotent consumers |
| F3 | Ack model? | Visibility timeout (SQS-like) and/or offset commit (Kafka-like) | Support one primary in MVP; discuss both |
| F4 | Ordering? | Optional per `session_id` / partition key | Partitioned logs |
| F5 | Priority? | Optional | Separate queues or priority lanes |
| F6 | Delay / scheduled? | Yes | Delay wheel / time index |
| F7 | TTL / expiry? | Yes | Drop or DLQ expired |
| F8 | Size? | ≤256 KB–1 MB; larger via claim check | Enforce limits |
| F9 | Replay? | Topic retention allows replay | Log retention policy |
| F10 | DLQ? | After max deliveries | Poison isolation |
| F11 | Filtering? | SQL-like filter on properties | Subscription rules |
| F12 | Transactions? | Optional send/settle tx | Complexity—Phase 2 |
| F13 | Auth? | Entra / SAS / RBAC per namespace | Multi-tenant security |
| F14 | Admin? | Peek, purge, metrics, scale units | Control plane |

**MVP functional scope:**

1. Namespace → Queue and Topic+Subscription entities.  
2. `Send` / `Receive+Delete` or `Receive` + `Complete` with visibility timeout.  
3. Competing consumers on a queue/subscription.  
4. Retry with delivery count; DLQ.  
5. Optional **session/partition key** ordering.  
6. Basic fan-out topic to N subscriptions (copy or shared log—pick).  
7. Metrics: backlog, age of oldest, throughput; authz.

**Out of MVP:**

- Cross-region active-active dual-write same queue  
- Exactly-once without consumer idempotency  
- Infinite retention free  
- Server-side stream processing engine (use consumers)  
- Global total ordering  

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Durability | ACK send only after fsync/quorum |
| N2 | Availability | 99.9%+ multi-AZ |
| N3 | Send latency | p50 < 10ms, p99 < 50ms in-region (small msg) |
| N4 | Receive latency | Idle wake p99 < 100ms long-poll |
| N5 | Throughput | Progressive table |
| N6 | Fairness | Noisy tenant cannot starve others |
| N7 | Ordering | Within partition/session only |
| N8 | Max message | Hard limit + claim-check pattern |
| N9 | Multi-region | DR failover; optional geo-replication |
| N10 | Observability | Backlog, delivery count, DLQ rate |

### 1.3 Cases

**Happy paths**

1. Producer send → durable → consumer receive → process → complete → deleted/advanced.  
2. Consumer crash after receive → visibility expires → redelivery.  
3. Topic with 3 subscriptions → each gets copy (or shared log with 3 groups).  
4. Session-ordered messages for `session=order-123` processed serially.  
5. Poison message exceeds max delivery → DLQ → alert.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate send | Producer idempotency id → one message |
| Consumer completes twice | Second complete no-op |
| Slow consumer | Backlog grows; scale consumers; optional throttle producers |
| Hot partition key | Ordering locality vs throughput trade-off |
| Broker disk full | Reject sends; alert; backpressure |
| Split brain primary | Quorum / epoch fence |
| Filter excludes all | Message drained for that sub; not for others |
| Clock skew delay messages | Server time for schedule |
| Giant message | Reject or claim-check pointer |
| Rebalance storm | Cooperative sticky assignment |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Namespaces / tenants | 5K | 50K | 500K | 5M |
| Queues+topics | 100K | 1M | 10M | 100M |
| Send QPS | 100K | 1M | 10M | 100M |
| Receive/settle QPS | 100K | 1M | 10M | 100M |
| Avg message size | 2 KB | 2 KB | 2 KB | 2 KB |
| Ingress MB/s | 200 | 2K | 20K | 200K |
| Concurrent consumers | 50K | 500K | 5M | 50M |
| Retention (topics) | 1–7d | 7d | 7–30d | tiered |
| Backlog messages | 100M | 1B | 10B | 100B |

```text
Ingress check: 100K msg/s × 2 KB = 200 MB/s baseline ✓
1000×: 100M × 2 KB = 200 GB/s → many cells / partitions
```

**What each jump forces:**

- **10×:** Partitioned brokers; separate control/data; long-poll fanout optimization.  
- **100×:** Tenant cells / shuffle shards; tiered storage; coordinated consumer groups.  
- **1,000×:** Hierarchical clusters; cold storage for retention; per-tenant isolation pools.

### 1.5 Etc.

- Prefer **Azure Service Bus** semantics for queues/sessions/topics and **Event Hubs** for high-throughput partitioned logs—design can unify under “entities on partitioned durable logs.”  
- Consumers are external; we provide SDKs/protocol.  
- Exactly-once side effects remain consumer responsibility.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Throughput classes

| Class | Baseline | 1000× |
|-------|----------|-------|
| Send | 100K/s | 100M/s |
| Receive | 100K/s | 100M/s |
| Complete/ack | 100K/s | 100M/s |
| Control (create entity) | low | still low vs data |

### 2.2 Storage

```text
Backlog 100M × 2 KB = 200 GB (baseline peak backlog)
Retained topic 100K/s × 2 KB × 86400 × 7d ≈ 100K*2000*86400*7
= 2e5 * 8.64e4 * 7 ≈ 1.21e11 * 7 ≈ 8.5e11 B ≈ 850 GB / week per 100K/s stream
At 1000× ingress: ~850 TB/week per similar retention → tiered storage mandatory
```

### 2.3 Fan-out cost

```text
Topic with S subscriptions:
If copy-per-sub: storage × S (Service Bus classic mental model)
If shared log + consumer groups: storage × 1, read amplification × S
Prefer shared log at high S and high throughput.
```

### 2.4 Memory

```text
Hot cache of next messages per partition; consumer fetch buffers
Avoid loading entire backlog into RAM
```

### 2.5 Critical bottlenecks

1. **Hot partitions** (skewed keys)  
2. **Small-message QPS** (header overhead)  
3. **Fan-out read amplification**  
4. **Metadata entity explosion** (millions of queues)  
5. **Disk / fsync latency**  
6. **Rebalance / lock contention** on competing consumers  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Namespace (tenant boundary)
  Queue  → competing consumers, optional sessions
  Topic  → Subscriptions (filters) → competing consumers per sub
Message { id, body, properties, session_id?, enqueue_time, delivery_count }
Cursor / Lock Token
DLQ entity
```

### 3.2 Options: storage engine

| Option | Pros | Cons | When |
|--------|------|------|------|
| A. SQL table as queue | Easy MVP | Limited throughput | Tiny scale |
| B. Partitioned append log (Kafka-like) | Throughput, replay | Harder delay/priority | High volume topics |
| C. Per-message store + indices (SB-like) | Sessions, defer, fancy features | Harder extreme throughput | Enterprise features |
| D. Hybrid | Log for transport + feature layer | Complexity | Cloud product reality |

**Chosen path:**

- **MVP:** Partitioned durable log + consumer group offsets for topics; queue as single-group log OR message store with visibility.  
- **Feature pack:** sessions, scheduled, filters via side indices / feature broker nodes.  
- **Extreme throughput entities:** Event Hubs–style pure partitions.

### 3.3 Delivery semantics

| Guarantee | Mechanism |
|-----------|-----------|
| At-least-once | Redeliver until complete |
| At-most-once | Auto-complete on receive (rare; document data loss) |
| Effectively-once | At-least-once + idempotent consumer + dedupe id |

**Deal-breaker:** Claiming broker exactly-once for arbitrary consumer code.

### 3.4 Ack models

**Visibility timeout (queue style):**

```text
Receive → lock message until T
Complete → remove
Abandon → unlock
Expired lock → visible again; delivery_count++
```

**Offset commit (log style):**

```text
Fetch batch → process → commit offset
Crash before commit → reprocess from last offset
```

Interview: pick primary; show you understand both.

### 3.5 Ordering

```text
partition = hash(session_id or partition_key) % N
within partition: total order
across partitions: no order
sessions: sticky lock to one consumer while active (Service Bus sessions)
```

### 3.6 Retries & DLQ

```text
max_delivery_count = K
on lock expiry or abandon: delivery_count++
if delivery_count > K: dead-letter (reason, description)
Admin: redrive DLQ → main with care
```

Backoff: client-side or broker-scheduled defer (Feature).

### 3.7 Competing consumers & fairness

- Multiple receivers on same queue: each message to **one** consumer.  
- Load balance via lock steals / partition assignment.  
- **Tenant fairness:** token buckets on send; separate IO pools; shuffle shard noisy neighbors.

### 3.8 Multi-region

| Mode | Behavior |
|------|----------|
| Single active region | DR async replica; failover fence |
| Geo-replication | Active/passive or active/active with **different namespaces**; avoid dual-write one entity |

### 3.9 API sketch

```text
PUT  /ns/{ns}/queues/{q}/messages
POST /ns/{ns}/queues/{q}/messages:receive  (long poll)
POST /ns/{ns}/queues/{q}/messages/{lock}/complete
POST .../abandon  .../deadletter
CRUD entities; peek; metrics
```

Protocol: AMQP 1.0 (Service Bus) and/or Kafka protocol for EH-like—mention.

### 3.10 Microsoft mapping

| Concept | Azure analog |
|---------|--------------|
| Queue + sessions | Service Bus Queue |
| Topic/Subscription | Service Bus Topic |
| High-throughput partitions | Event Hubs |
| Simple poke queue | Storage Queue |

Design interview: show when you’d pick each.

---

## 4. Architecture Diagram

### 4.1 Control vs data

```text
                    Control Plane
            (entities, RBAC, quotas, placement)
                        │
                        ▼
Producer → Frontend Gateway → Partition Leaders (data plane)
                                   │
                                   ▼
                            Durable Log / Store (multi-AZ quorum)
                                   │
                                   ▼
Consumer ← Frontend / Brokers ← Cursors / Locks
                                   │
                                   ▼
                                 DLQ
```

### 4.2 Topic fan-out options

```text
Option Copy:
  Topic publish → write N subscription queues

Option Shared Log:
  Topic publish → one log
  Sub G1 offset, Sub G2 offset, ...
```

### 4.3 Receive with visibility

```text
Consumer long-poll
  → broker finds visible msg on assigned partitions
  → CAS lock (invisible until T) + lock_token
  → return message
Consumer complete(lock_token)
  → verify → delete / mark consumed
```

### 4.4 Scale cells

```text
Tenant → Cell (cluster)
Cell → namespaces → entities → partitions across brokers
Frontend routers cache placement
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Produce durability

```text
Leader append → replicate to followers (quorum) → ACK producer
RPO≈0 for ACKed sends within AZ quorum model
```

#### 5.1.2 Fencing

Broker primary epoch; stale leaders cannot ACK. Consumers’ lock tokens include epoch.

#### 5.1.3 Consumer failure

Visibility timeout / uncommitted offsets cause redelivery—**duplicates expected**.

#### 5.1.4 Poison messages

Bounded redelivery → DLQ; never block partition forever (skip poison in log mode with careful offset policy / quarantine topic).

#### 5.1.5 Failure modes

| Failure | Behavior |
|---------|----------|
| Leader crash | Elect new; producers retry (idempotent send) |
| Disk failure | Rebuild from replicas |
| Consumer stuck | Lock expires; scale out / page |
| Metadata store down | No new entities; data plane continues |

### 5.2 Scalability

#### 5.2.1 Partitioning

More partitions → more parallelism; too many → metadata/memory cost. Autoscale partition counts for EH-like; SB entities may scale via messaging units / cells.

#### 5.2.2 Batching

Producers batch; consumers prefetch. Critical for small messages.

#### 5.2.3 Tiered storage

Hot SSD log segments; cold object storage for old retention; read path hydrates.

#### 5.2.4 Progressive scale

| Scale | Must have |
|-------|-----------|
| 1× | Multi-AZ log, ack, DLQ, basic queues |
| 10× | Many partitions, long-poll, quotas |
| 100× | Cells, tiered storage, session features |
| 1000× | Hierarchical routing, cold tier, isolation pools |

### 5.3 Maintainability

- Clear entity model; strong metrics (backlog age!).  
- Schema for message properties; filter language versioned.  
- Chaos: kill leaders; verify no lost ACKed messages.  
- SDK guidance: idempotency keys, timeout tuning.

### 5.4 Security

- RBAC: send vs listen vs manage.  
- Encryption at rest; TLS; optional CMEK.  
- Auth isolation per namespace; prevent cross-tenant receive.  
- Thundering auth cache for tokens.

### 5.5 Ordering vs throughput

Document the trade: single session key ⇒ serial bottleneck; advise key design (`order_id` not `tenant_id` alone if huge).

### 5.6 Transactions (advanced)

Send via transactional outbox from producer DB; broker-side commit with dual receive rarely needed—prefer outbox pattern.

### 5.7 Backpressure

| Signal | Action |
|--------|--------|
| Partition lag | Autoscale consumers |
| Broker IO saturation | Throttle sends (429) |
| Tenant quota | Reject/slow that tenant |

---

## 6. Wrap-Up

### 6.1 What we designed

A **cloud message queue / pub-sub** with durable quorum logs (or message store), at-least-once delivery via locks/offsets, DLQ, optional per-key ordering, topic fan-out, multi-tenant quotas/cells, and Azure Service Bus / Event Hubs–aligned mental models.

### 6.2 Key invariants

1. Send ACK ⇒ durable quorum.  
2. Delivery at-least-once unless explicitly at-most-once mode.  
3. Ordering only within partition/session.  
4. Poison isolated via DLQ.  
5. No cross-tenant access.

### 6.3 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| Semantics | At-least-once | Practical |
| Fan-out | Shared log at scale | Cost |
| Features vs throughput | Split entity types | SB vs EH |
| Global order | No | Scale |
| Exactly-once | Consumer idempotency | Honesty |

### 6.4 60-second pitch

> Producers append to partitioned durable logs with quorum ACK. Consumers compete via lock tokens or offset commits—at-least-once with redelivery and DLQ. Ordering is per partition key/session. Topics fan out via shared log consumer groups (or copies for feature-rich subs). Multi-tenant cells and quotas stop noisy neighbors. We don’t claim magical exactly-once; we provide the primitives for effectively-once applications.

### 6.5 Risks / follow-ups

- Cross-region active-active  
- Server-side stream SQL  
- Very large message claim-check integration  
- Schema registry  

---

## 7. Deeper / Related Interview Questions

### 7.1 Semantics

**Q: Why not exactly-once?**  
A: Side effects outside the broker can’t be controlled; provide idempotency + dedupe windows; Kafka EOS is transactional within its ecosystem—discuss limits.

**Q: At-most-once use case?**  
A: Metrics where loss OK; rare for business workflows.

**Q: Duplicate after complete?**  
A: Shouldn’t if complete durable; network retry of complete is idempotent.

### 7.2 Ordering

**Q: Total global order?**  
A: Single partition only—throughput limited; usually wrong.

**Q: Sessions in Service Bus?**  
A: Sticky exclusive receiver per session id; great for workflow affinity.

**Q: Hot key?**  
A: Break key space; accept less order; or dedicated partition with scaled processing elsewhere.

### 7.3 Storage

**Q: Queue as DB table?**  
A: OK for low QPS; `SKIP LOCKED` pattern; won’t hit 100K+/s easily.

**Q: Kafka vs SB?**  
A: Kafka/EH: streaming throughput/replay; SB: enterprise sessions, filters, defer, transactions-ish features.

### 7.4 DLQ

**Q: Automatic redrive?**  
A: Careful—can recreate outage; rate-limit; require poison fix.

**Q: DLQ ordering?**  
A: Usually not critical; treat as quarantine.

### 7.5 Fan-out

**Q: 1000 subscriptions?**  
A: Shared log; filters pushdown; watch cursor metadata cost.

**Q: Filtering cost?**  
A: Evaluate on broker may burn CPU—index properties or client filter trade-off.

### 7.6 Scale

**Q: Millions of queues?**  
A: Metadata-heavy; many “queues” should be logical sessions on fewer topics; or hierarchy.

**Q: 200 GB/s ingest?**  
A: Many cells, batching, large pages, disk/NIC planning, tenant isolation.

### 7.7 Multi-region

**Q: Active-active queue?**  
A: Hard for single competing consumer semantics; prefer geo pair failover or merge with ids.

### 7.8 Reliability drills

1. Kill leader after ACK → still durable.  
2. Kill leader before ACK → producer retries with idempotency.  
3. Consumer freeze → lock timeout redeliver.  
4. Poison → DLQ; partition progresses.  
5. Disk full → fail send loudly.

### 7.9 Microsoft-specific

**Q: When Event Hubs vs Service Bus?**  
A: EH for high ingest telemetry; SB for business commands, sessions, request/reply, topics with rich filters.

**Q: AMQP vs Kafka protocol?**  
A: SB AMQP; EH Kafka protocol support—SDK choice.

### 7.10 Comparison

**Q: vs RPC?**  
A: Decoupling, buffering, load leveling, fan-out, retries.  

**Q: vs job scheduler?**  
A: Queue is transport; scheduler owns leases/DAG/cron (related but distinct).

### 7.11 Interview traps

| Trap | Pushback |
|------|----------|
| Global FIFO at 1M/s | Impossible practically |
| Exactly-once magic | Effects need idempotency |
| Infinite in-memory queue | Durability lie |
| One partition always | Hotspot or under-scale |
| 100K×2KB=200GB/s | **200MB/s** |

### 7.12 Client patterns

**Q: Outbox?**  
A: DB TX writes outbox row; publisher relay to queue—prevents lost sends.

**Q: Inbox / dedupe?**  
A: Consumer stores processed message ids.

**Q: Prefetch?**  
A: Improves throughput; increases duplicate window on crash.

### 7.13 Priority queues

**Q: How?**  
A: Separate entities per priority or multi-level dispatch; avoid starvations with aging.

### 7.14 Delayed messages

**Q: Implementation?**  
A: Time wheel / scheduled index until visible; not scanning all messages.

---

## 8. Appendices

### 8.1 Schema sketches

```text
namespaces(ns_id, tenant_id, quota)
entities(entity_id, ns_id, type, config)
partitions(entity_id, partition_id, leader, high_watermark)
messages_log(segment files: offset → bytes)
cursors(group_id, partition_id, offset)
locks(message_id, lock_token, expires_at, delivery_count)
dlq(message_id, reason, dead_at)
idempotency(producer_id, seq → message_id)
```

### 8.2 API checklist

- [ ] Create/delete queue/topic/subscription  
- [ ] Send / batch send  
- [ ] Receive (long poll) / peek  
- [ ] Complete / abandon / deadletter / renew lock  
- [ ] Manage sessions  
- [ ] Metrics & purge  
- [ ] Auth RBAC  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Visibility timeout | Invisibility window after receive |
| Delivery count | Redelivery attempts |
| Competing consumers | One message → one worker |
| Consumer group | Shared progress on a log |
| Session | Ordered sticky key |
| DLQ | Dead-letter queue |
| Claim check | Big payload in blob; message has pointer |
| Quorum ACK | Majority durable before producer ACK |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Durable multi-AZ, ack, DLQ |
| 10× | Partitions, quotas, batching |
| 100× | Cells, tiered storage, filters/sessions |
| 1000× | Hierarchical clusters, isolation pools |

### 8.5 Delivery state machine (queue style)

```text
AVAILABLE → LOCKED → DELETED(completed)
               ↓
            AVAILABLE (timeout/abandon) → ... → DEAD
```

### 8.6 Producer idempotency

```text
Send(MessageId=U, payload)
Broker stores MessageId unique within TTL/namespace
Retry same MessageId → same success, no dup
```

### 8.7 When to use what (Azure)

| Workload | Pick |
|----------|------|
| Order commands, sessions | Service Bus |
| Telemetry firehose | Event Hubs |
| Simple async poke low volume | Storage Queue |
| Request/reply | SB sessions / reply queues |

### 8.8 Interview “say this” summary

> Durable partitioned messaging with quorum ACK, at-least-once via locks/offsets, DLQ, per-key ordering, shared-log fan-out, tenant cells—and honest exactly-once boundaries.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| Long visibility timeout = safety | Increases lag on crash |
| Prefetch huge | Duplicate blast radius |
| One DLQ for all tenants | Isolation/privacy issues |
| Synchronous mirror cross-region on every send | Latency hit |

### 8.10 Reliability test plan

1. Dual complete with same lock → one effect.  
2. Kill consumer after receive → redelivery.  
3. Max delivery → DLQ.  
4. Leader failover → no loss of ACKed sends.  
5. Hot key → observable skew metrics.

### 8.11 Observability SLOs

| SLO | Example |
|-----|---------|
| Send p99 | < 50ms |
| ACK durability | 100% of ACKed |
| Redelivery rate | monitored |
| Oldest message age | alert thresholds |
| DLQ rate | < X% |

### 8.12 Related systems map

```text
Producers → Gateway → Partition Leaders → Quorum Log
Consumers → Gateway → Locks/Cursors → Process → Complete
                              ↓
                             DLQ / Metrics / Admin
```

### 8.13 Message property filters (example)

```text
subscription rule: color = 'red' AND priority > 3
evaluated at dispatch time
```

### 8.14 Backlog math

```text
backlog_growth_rate = produce_rate - consume_rate
time_to_drain = backlog / (consume - produce) if consume > produce
```

### 8.15 Claim-check pattern

```text
Producer → put blob → send message {blob_uri, checksum, ttl}
Consumer → download blob → process → delete blob optional
```

### 8.16 Capacity cheat-sheet

```text
MB/s = msg/s × avg_size
partitions ≈ target_parallelism
consumers ≈ partitions (log style) or scale with lock model
```

### 8.17 Session processing sketch

```text
AcceptNextSession → exclusive lock on session_id
Receive messages for session in order
Complete each; release session when idle
```

### 8.18 Geo-DR sketch

```text
Primary entity → async replicate to secondary namespace
Failover: DNS/connection string flip; fence primary epoch
At-least-once duplicates possible → consumers idempotent
```

### 8.19 Comparison table

| System | Order | Replay | Features |
|--------|-------|--------|----------|
| Storage Queue | No | Limited | Simple |
| Service Bus | Sessions | Limited | Rich |
| Event Hubs | Partition | Yes | Throughput |
| Kafka | Partition | Yes | Ecosystem |

### 8.20 Final deal-breakers

1. ACK send without durability  
2. Infinite silent data loss mode sold as durable  
3. Global ordering requirement at scale  
4. Exactly-once claims for arbitrary side effects  
5. No DLQ / poison handling  

---

*End of message queue system design.*
