# System Design: Ecommerce Order-Event Ingestion API

> **Focus areas:** High-volume event ingest · Idempotency · Ordering · Schema evolution · Consumers (fulfillment, analytics, notifications) · Progressive scale (10× → 100× → 1,000×)  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership  
> **Quality bar:** Split ingress vs fan-out QPS, effectively-once effects, per-key ordering, contract-safe evolution, consumer isolation

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

Goal: **design a high-volume order-event ingestion API**—producers (checkout, payments, FC systems) emit order lifecycle events; the platform durably ingests, deduplicates, orders, and fans out to fulfillment, analytics, and notifications without corrupting downstream state.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who produces events? | Checkout/Order service, Payments, Fulfillment centers, Returns | Multi-producer; authN/Z per producer |
| F2 | Event types? | Placed, Paid, Allocated, Shipped, Delivered, Cancelled, Refunded, … | Versioned event envelope + type |
| F3 | API style? | HTTPS ingest (+ optional Kafka internal) | Public/private ingest gateway |
| F4 | Idempotency? | Mandatory—retries everywhere | Idempotency keys / event_id |
| F5 | Ordering? | Per `order_id` (or customer) causal order | Partition by order_id |
| F6 | Delivery to consumers? | At-least-once; consumers idempotent | Durable bus + offsets |
| F7 | Consumers? | Fulfillment, Analytics, Notifications (email/SMS/push) | Isolated consumer groups |
| F8 | Schema evolution? | Additive compatible changes frequent | Schema registry; compat checks |
| F9 | Query API? | Get events by order_id for support | Hot store / log indexed |
| F10 | Backfill / replay? | Yes for analytics & new consumers | Retain log; replay tooling |
| F11 | PII? | Addresses/emails in some events | Redaction / tokenization policies |
| F12 | Sync vs async ACK? | ACK after durable accept, not after all consumers | Ingress durability ≠ fan-out complete |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/order-events` ingest with auth, validation, idempotency.  
2. Durable log/bus partitioned by `order_id`.  
3. Per-key ordering guarantees.  
4. Consumer groups: Fulfillment, Analytics, Notifications.  
5. Schema registry + evolution rules.  
6. Replay/backfill for a consumer from offset/time.  
7. Observability: lag, dup rate, poison messages.  
8. Scale 10× / 100× / 1,000× with cells and tiered storage.

**Out of MVP (explicitly defer):**

- Exactly-once *network* delivery to all consumers (we do effectively-once effects)  
- Cross-order global total order  
- Complex CEP / “join all streams in SQL” as ingest path  
- Replacing Order SoT DB with the event log alone (event log complements SoT)  
- Multi-hop global active-active without conflict story  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest latency | ACK durable | p99 < 50–100ms in-region |
| N2 | Durability | No silent loss after 200 | Quorum / multi-AZ commit |
| N3 | Ordering | Per order_id | Same partition key |
| N4 | Idempotency window | ≥ 24–72h (defend choice) | Dedup store aligned |
| N5 | Fan-out lag | Fulfillment near-real-time | p99 lag < 5–30s steady |
| N6 | Availability | Ingest critical | 99.99% goal; shed noncritical producers |
| N7 | Retention | Analytics days–weeks hot; cold longer | Tiered storage |
| N8 | Schema safety | No breaking prod push | Registry CI gate |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Order service emits `OrderPlaced` → ingest 200 → fulfillment consumes → create FC work.  
2. Payment emits `OrderPaid` → notifications email “confirmed”.  
3. FC emits `OrderShipped` with tracking → notifications + analytics.  
4. Retry of same `event_id` → 200 with same result; no double ship side effects.  
5. New analytics consumer replays from T−7d.  
6. Schema add field `gift_message_present` → old consumers ignore.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate POST | Idempotent success |
| Same event_id different body | 409 conflict |
| Out-of-order arrive (Shipped before Paid) | Buffer / stateful consumer / reject per policy |
| Poison malformed payload | DLQ + alarm; don’t block partition forever |
| Consumer crash mid-process | At-least-once redelivery; idempotent handler |
| Hot order_id (many updates) | Partition hotspot; key design / fan-out |
| Schema incompatible deploy | Registry rejects; producer blocked |
| Analytics lag hours | Isolate; don’t slow fulfillment group |
| PII in wrong field | Ingest validator / redaction filter |
| Replay duplicates | Consumers keyed by event_id |
| Burst Prime Day | Autoscale ingest; backpressure producers |
| Clock skew on event_time | Use ingest_time + producer event_time; order by seq |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Orders / day | 5M | 50M | 500M | 5B |
| Events / order (avg) | 6 | 6 | 8 | 10 |
| Peak ingest events/s | 5K | 50K | 500K | 5M |
| Producers | 20 | 50 | 200 | 1K |
| Consumer groups | 3 | 8 | 20 | 50+ |
| Fan-out msgs/s | 15K | 150K | 1.5M | 15M+ |
| Hot store retention | 7d | 14d | 7d hot + cold | hierarchical |
| Dedup entries | 1B | 10B | 100B | tiered TTL |
| Schema versions active | 10 | 30 | 100 | 300 |

**What each jump forces:**

- **10×:** Kafka/Kinesis-class bus; Redis/Dynamo dedup; consumer isolation; schema registry.  
- **100×:** Ingest cells; tiered dedup; parallel fulfillment queues; cold object log.  
- **1,000×:** Hierarchical topics; edge ingest; bloom+remote dedup; stream SQL for analytics only.

### 1.5 Etc. (Constraints & Assumptions)

- Order **SoT remains Order DB**; this platform is the **event highway**.  
- Prefer **producer-assigned `event_id` (UUIDv7/ULID)** + `order_id` + `sequence` / `causation`.  
- Notifications are **lossy-tolerant** vs fulfillment (**not**); still idempotent.  
- “Exactly-once” means **exactly-once business effect**, not single HTTP delivery.

**Scope statement:**

> Design an ecommerce order-event ingestion API that durably accepts high-volume lifecycle events with idempotency and per-order ordering, evolves schemas safely, and fans out to fulfillment, analytics, and notification consumers—from ~5K events/s through 10× / 100× / 1,000× with isolated consumer groups and replay.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Meaning | Baseline | 10× |
|-------|---------|----------|-----|
| **Ingress accepts** | HTTP → durable log | 5K/s | 50K/s |
| **Dedup checks** | Same as ingress | 5K/s | 50K/s |
| **Log writes** | Partition appends | 5K/s | 50K/s |
| **Fulfillment consume** | Critical group | 5K/s | 50K/s |
| **Notifications** | Soft | 5K/s | 50K/s |
| **Analytics** | Soft / batch OK | 5K/s + replay | bursty |
| **Support GetEvents** | Low QPS | 100/s | 1K/s |

Fan-out ≈ ingress × (#groups). At 3 groups, bus deliver ~15K/s baseline.

### 2.2 Payload & bandwidth

```text
Avg event 1–3 KB JSON (with address snapshot maybe 5 KB)
50K evt/s × 2 KB = 100 MB/s ingress
× 3 groups ≈ 300 MB/s out (before compression)
Compression + binary (Avro/Protobuf) → 3–5× less
```

### 2.3 Dedup storage

```text
event_id ~ 16–20 B + metadata ~50 B ≈ 80 B
50K/s × 86400 × 80 B ≈ 345 GB/day
TTL 72h → ~1 TB dedup store at 10× — plan Dynamo/Redis cluster or RocksDB local+remote
```

### 2.4 Partition count

```text
Target per-partition peak ~1000–2000 evt/s
50K/s → 25–50 partitions minimum; use 200–500 for headroom & rebalance
Key = order_id (or hash)
```

### 2.5 Consumer lag budget

```text
Fulfillment: process p99 < 200ms; parallelism = partitions
If lag > 30s → page on-call for that group only
Analytics: lag hours OK; separate SLO
```

---

## 3. High-Level Design

### 3.1 Components

| Component | Role |
|-----------|------|
| **Ingest Gateway** | TLS, auth, rate limit, validate envelope |
| **Schema Registry** | Compat checks; version assignment |
| **Idempotency / Dedup Service** | event_id uniqueness window |
| **Ordering Sequencer (optional)** | Per-order monotonic seq if producers weak |
| **Durable Log (Kafka/Kinesis/Pulsar)** | Partitioned append store |
| **Router / Dispatcher** | Consumer groups / topics |
| **Fulfillment Workers** | Critical path side effects |
| **Notifications Workers** | Email/SMS/push |
| **Analytics Pipeline** | Sink to lake/warehouse |
| **DLQ + Replay Tools** | Poison + backfill |
| **Event Hot Index** | Get-by-order_id for support |

### 3.2 Event envelope

```text
OrderEvent {
  event_id: ULID              # producer-generated, globally unique
  event_type: "OrderPlaced"
  event_version: 3            # schema version for this type
  order_id: string
  customer_id: string
  marketplace_id: string
  producer: "checkout-service"
  producer_time: iso8601
  sequence: int64             # per-order monotonic from producer if available
  causation_id / correlation_id
  payload: { ... typed ... }
  headers: { tracing, pii_class }
}
```

### 3.3 API

```text
POST /v1/order-events
Authorization: Bearer <producer token>
Idempotency-Key: <event_id>          # or body.event_id authoritative
Content-Type: application/json

202/200 Accepted { event_id, ingest_time, partition, offset? }

GET /v1/orders/{order_id}/events?cursor=
  → support / debug (authz)

POST /v1/admin/replay
  { consumer_group, from_time|offset, to, filter }
```

**Response codes**

| Code | Meaning |
|------|---------|
| 200 | Duplicate idempotent hit (same body) |
| 202 | Newly accepted durable |
| 400 | Validation failure |
| 401/403 | Auth |
| 409 | Same event_id, different body |
| 413 | Payload too large |
| 429 | Rate limited / backpressure |
| 503 | Bus degraded; producer should retry |

### 3.4 Idempotency design

```text
DedupRecord {
  pk: event_id
  request_hash
  order_id
  ingest_time
  partition, offset
  ttl
}
```

Flow:

1. Compute hash(body canonical).  
2. Conditional put `event_id` if absent → proceed append.  
3. If present and hash matches → return prior ACK.  
4. If present and hash differs → 409.  

**At 100×:** local bloom filter → remote Dynamo; TTL 72h; cold “exists” via log offset index optional.

### 3.5 Ordering design

**Guarantee:** For a given `order_id`, consumers see a **total order** consistent with producer `sequence` (or ingest sequencer).

Mechanics:

1. Partition key = `order_id` (all events for order on one partition).  
2. Producer includes `sequence` monotonic per order.  
3. Consumer applies in `sequence` order; buffer gaps with timeout policy.  
4. If producers can’t sequence, ingest service assigns `ingest_seq` per key via lightweight sequencer (Redis INCR / Kafka transactions careful).

**Out-of-order policy (pick & defend):**

- **Fulfillment:** buffer gap ≤ N seconds; else DLQ for manual / state reconcile with Order SoT.  
- **Notifications:** best-effort; skip obsolete (Shipped after Cancelled suppressed by state machine).  
- **Analytics:** sort by sequence in micro-batch.

### 3.6 Fan-out topology

```text
Ingest → topic order.events.v1 (partitioned by order_id)
            ├─ consumer.fulfillment
            ├─ consumer.notifications
            └─ consumer.analytics

Optional: type-filter topics via stream router for efficiency at 100×
  order.events.placed / shipped / ...
```

**Isolation:** separate consumer groups; fulfillment lag never pauses analytics commits differently—each tracks own offsets.

### 3.7 Schema evolution

| Change | Compatibility | Action |
|--------|---------------|--------|
| Add optional field | Backward+forward | Allowed |
| Remove field | Breaking | New event_version; dual publish |
| Change field type | Breaking | New version |
| Rename | Breaking | Dual-write fields |
| New event_type | Additive | Register + consumers opt-in |

**Registry gate in CI:** producer artifacts must pass compat vs `prod` branch.

Payload formats: start JSON; move to **Avro/Protobuf** at 10× for size/CPU; keep JSON debug mirror optional.

### 3.8 Consumer patterns

**Fulfillment (critical)**

```text
on event:
  if seen(event_id): return
  load aggregate projection / call FC API idempotently
  apply state machine transition
  commit offset after side effect durable (or outbox)
```

**Notifications (soft)**

```text
on event:
  template map by event_type
  dedup on (event_id, channel)
  send; allow drop under shed
```

**Analytics (soft)**

```text
micro-batch → Parquet → S3/lake
partition by date + marketplace
late events via sequence reconcile
```

### 3.9 Relationship to Order SoT

```text
Order DB (SoT) --outbox--> Ingest API / bus
FC systems -------API----> Ingest API
Payments --------API----> Ingest API

Consumers must NOT invent order existence contradicting SoT.
Reconciler: compare bus projection vs Order DB periodically.
```

### 3.10 Progressive architecture

| Scale | Design |
|-------|--------|
| 1× | API + Kafka 1 cluster; Redis dedup; 3 groups |
| 10× | Multi-AZ; schema registry; DLQ; hot index |
| 100× | Ingest cells; tiered dedup; type topics; cold log |
| 1,000× | Geo ingest; hierarchical buses; stream mesh |

### 3.11 Trade-offs

| Decision | Pros | Cons | Pick |
|----------|------|------|------|
| ACK after log write | Fast producer | Consumers lag independently | Yes |
| Partition by order_id | Per-order order | Hot orders | Yes |
| Dedup before append | Less bus dup | Dedup store scale | Yes |
| Exactly-once bus TX | Fancy | Complexity | Optional later |
| Sync notify in ingest | Simple | Kills latency/avail | No |
| Global total order | Simple mental | Kills scale | No |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Checkout/Order   Payments   FC / Returns
        │            │            │
        └────────────┼────────────┘
                     ▼
            ┌─────────────────┐
            │ Ingest Gateway  │  auth · validate · ratelimit
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ Schema Registry │── reject incompatible
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ Dedup Store     │── 409 on hash mismatch
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ Durable Log     │  PK = order_id
            │ (Kafka-class)   │
            └────────┬────────┘
         ┌───────────┼───────────┐
         ▼           ▼           ▼
   Fulfillment  Notifications  Analytics
   workers       workers        lake sink
         │           │           │
         ▼           ▼           ▼
      FC APIs     Email/SMS    Warehouse
         │
         └── DLQ ← poison / gap timeout
```

### 4.2 Ingest sequence

```text
Producer          Gateway          Dedup           Log
   │  POST event    │               │              │
   │────────────────►│               │              │
   │                 │── check ─────►│              │
   │                 │◄─ new/dup ────│              │
   │                 │── append ───────────────────►│
   │                 │◄─ offset ────────────────────│
   │◄── 202 ─────────│               │              │
```

### 4.3 Per-order ordering

```text
order_id=O1 events → Partition 17: [seq1 Placed][seq2 Paid][seq3 Shipped]
Consumer buffer: if seq3 arrives before seq2 → wait; apply seq2 then seq3
```

### 4.4 Replay

```text
Admin → Replay Controller → read log from offset/time
                         → filter event_types
                         → write to replay topic OR reset consumer group
Consumer uses event_id dedup to stay safe
```

### 4.5 Cell / multi-cluster

```text
Producer region US  → Ingest Cell US → Bus US
Producer region EU  → Ingest Cell EU → Bus EU
Analytics global    → replicate cold sink
Fulfillment         → regional (residency)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. **Durability before ACK** — quorum append.  
2. **Idempotent ingest** — event_id primary.  
3. **Hash mismatch → 409** — never silent overwrite.  
4. **Per-order partition affinity** — ordering foundation.  
5. **Consumer idempotency** — side effects keyed by event_id.  
6. **Fulfillment state machine** — reject illegal transitions.  
7. **DLQ for poison** — no infinite stall without alarm.  
8. **Offset commit after durable side effect** (or transactional outbox pattern).  
9. **PII policy enforced at ingest.**  
10. **Schema registry is authoritative** for produce.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Kafka broker loss | ISR/multi-AZ; producer retry |
| Dedup store outage | Fail closed (503) or carefully degrade with risk flag |
| Consumer bug loops | DLQ + circuit breaker; poison pill skip with audit |
| Gap in sequence | Buffer + reconcile with Order SoT |
| Duplicate FC create | FC API idempotency key = event_id |
| Notification double send | Dedup table per channel |
| Replay storm | Rate-limit replay; isolated cluster |

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Single Kafka; Redis dedup; 3 groups |
| 10× | More partitions; schema registry; horizontal ingest; DLQ |
| 100× | Cells; tiered dedup; topic split by type; cold S3 log |
| 1,000× | Geo routing; hierarchical aggregation for analytics; edge validate |

**Hot keys:** celebrity orders with dozens of status pings—batch updates; coalesce; ensure partition capacity.

**Backpressure:** gateway returns 429 when bus produce latency spikes; producers exponential backoff with jitter.

**Autoscaling:** ingest on CPU/RPS; consumers on lag.

### 5.3 Maintainability / operability

- Contract tests producer ↔ schema.  
- Canary consumers on shadow topic.  
- Chaos: kill consumers; bus brownout; dedup latency inject.  
- Runbooks: DLQ drain, replay, gap reconcile.  
- Feature flags: drop notification types under shed.  
- Clear ownership: ingest platform vs consumer teams (Amazon “two-pizza” + platform).

### 5.4 Consistency & delivery semantics

| Layer | Semantics |
|-------|-----------|
| Producer → Ingest | At-least-once HTTP |
| Ingest append | Effectively-once via dedup |
| Bus → Consumer | At-least-once |
| Consumer side effect | Effectively-once via event_id |
| Cross-consumer | Independent; no distributed TX required |

**Ordering vs availability:** if sequencer unavailable, either fail ingest (strict) or accept ingest-time order with producer sequence preferred when present—**say which**.

### 5.5 Idempotency deep dive

**Why not only Kafka log compaction?** Compaction ≠ request dedup for ACK semantics; producers need immediate idempotent HTTP behavior.

**Idempotency-Key header vs body event_id:** body `event_id` is source of truth; header must match if both sent.

**Window:** 24–72h covers payment/FC retries; beyond window rare—Order SoT reconcile handles.

### 5.6 Ordering deep dive

**Producer sequence:**

```text
Order service: seq = atomic incr per order_id in Order DB outbox row
FC: may use FC local seq per order; ingest normalizes to global per-order stream via type priority + time
```

**Conflict example:** `Cancelled` vs `Shipped` race—consumer consults Order SoT or prefers terminal precedence rules documented in state machine.

### 5.7 Schema evolution deep dive

**Compat modes:** BACKWARD (new reader old data) common for consumers; producers often need FORWARD. Use FULL for shared topics when possible.

**Dual-publish:**

```text
emit OrderShipped v2 + v3 during migration
consumers prefer v3; analytics reads both into unified model
```

**Payload size limits:** e.g. 256 KB; large labels/PDFs as URIs not inline.

### 5.8 Consumer isolation deep dive

- Separate **thread pools / clusters** for fulfillment.  
- Quotas so analytics replay cannot starve ISR disk.  
- Notifications shed first under bus stress.  
- SLOs per group, not one global lag number.

### 5.9 Security

- mTLS or signed tokens per producer.  
- Per-event-type authz (FC can’t emit OrderPaid).  
- Encrypt bus at rest; PII fields tagged; analytics scrubbed topic optional.  
- Audit log of admin replay.

### 5.10 Observability

| Metric / alarm | Why |
|----------------|-----|
| `ingest_accept_rate` / `p99` | Producer UX |
| `dedup_hit_rate` | Retry health |
| `conflict_409_rate` | Producer bugs |
| `bus_produce_p99` | Durability path |
| `consumer_lag{group}` | Fan-out health |
| `dlq_depth` | Poison |
| `schema_reject_rate` | Contract breaks |
| `replay_events_s` | Ops safety |
| `gap_timeout_count` | Ordering pain |
| `notification_dedup_rate` | Double-send risk |

---

## 6. Wrap-Up

### 6.1 What we designed

A **durable order-event ingestion platform**: authenticated high-QPS API, schema-validated envelopes, idempotent accept, per-`order_id` ordered log, and isolated consumers for fulfillment, analytics, and notifications—with replay, DLQ, and a clear scale path to 100× / 1,000×.

### 6.2 Key decisions worth defending

1. **ACK after durable log, not after consumers.**  
2. **event_id idempotency + body hash.**  
3. **Partition by order_id** for ordering.  
4. **At-least-once + consumer idempotency** = effectively-once effects.  
5. **Schema registry CI gate.**  
6. **Consumer group isolation** (fulfillment ≠ analytics).  
7. **DLQ + SoT reconcile** for gaps/poison.  
8. **Order DB remains SoT**; bus is highway.  
9. **Replay-safe by event_id.**  
10. **Shed notifications before fulfillment.**

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Dedup store hotspot | Shard by event_id; tiered bloom |
| Hot order partitions | Coalesce; monitor |
| Illegal transition races | State machine + SoT |
| Schema break sneak-in | Registry + canary |
| PII leakage to lake | Scrub topic / tokenization |
| Replay doubles side effects | Strict consumer dedup |

### 6.4 How to present in 45 minutes

1. Producers/consumers + semantics (7 min)  
2. Numbers + partition math (5 min)  
3. Ingest path + idempotency + ordering (12 min)  
4. Fan-out + schema evolution (8 min)  
5. Failure/DLQ/replay + scale jumps (8 min)  
6. Q&A (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 API & ingest

**Q1: 200 vs 202 on accept?**  
A: 202 for new durable accept; 200 for idempotent replay; be consistent and document.

**Q2: Why not clients write Kafka directly?**  
A: Auth, schema, dedup, multi-protocol, evolution control, abuse protection.

**Q3: Payload includes full address every time—costly?**  
A: Allow refs + version for updates; require snapshot on Placed; later events lighter.

**Q4: How to rate-limit producers?**  
A: Per-producer quotas; fairness; burst tokens; 429 with Retry-After.

### 7.2 Idempotency

**Q5: Is Kafka offset enough for idempotency?**  
A: No for HTTP retries before offset assigned; need event_id store.

**Q6: Two producers accidentally reuse event_id.**  
A: 409; operational alert; IDs must be globally unique (ULID + producer namespace optional).

**Q7: Dedup TTL expired, event retried?**  
A: May re-append; consumers still dedup; ideally producers don’t retry that late—reconcile.

### 7.3 Ordering

**Q8: Do we need total order across all orders?**  
A: No—kills scale; per-order suffices for commerce lifecycle.

**Q9: Shipped arrives before Paid.**  
A: Buffer; or mark pending; or reject to DLQ; fulfillment must not ship unpaid without policy exception (e.g., invoice terms).

**Q10: Multiple FC events concurrent.**  
A: Line-level event keys; partition still order_id; sequence includes line_id dimension.

### 7.4 Consumers

**Q11: Commit offset before or after side effect?**  
A: After durable side effect (or outbox). Before ⇒ loss on crash.

**Q12: Analytics wants different partitioning.**  
A: Consume then re-key to lake partitions; don’t change ingest key.

**Q13: Notifications double email.**  
A: `(event_id, channel)` unique send record.

**Q14: How does fulfillment stay correct under redelivery?**  
A: FC API idempotency keys; local processed-events table.

### 7.5 Schema

**Q15: Can we delete a field used by one lagging consumer?**  
A: Not until consumer upgraded; use compatibility + migration windows.

**Q16: JSON vs Avro?**  
A: JSON for MVP velocity; Avro/Proto at scale for size and compat tooling.

**Q17: Event_type explosion?**  
A: Prefer stable types + versioned payload; don’t create `OrderShipped_v2` as new type name without need.

### 7.6 Replay & ops

**Q18: Replay last 24h for one consumer.**  
A: Reset offsets or replay topic; rate-limit; monitor side-effect dedup.

**Q19: DLQ drain strategy.**  
A: Classify; fix consumer; redrive; skip poison with ticket.

**Q20: Bus full disk.**  
A: Retention policies; throttle producers; shed analytics retention first.

### 7.7 Scale prompts

**Q21: 500K evt/s—bottleneck?**  
A: Dedup store, partition count, schema validation CPU, single-region NIC—cells + binary codec.

**Q22: Multi-region active-active ingest?**  
A: Hard for per-order order—prefer regional home for order_id; cross-region replicate async for analytics.

---

## 8. Appendices

## Appendix A — Example event payloads

```json
{
  "event_id": "01J8Z3...",
  "event_type": "OrderPlaced",
  "event_version": 3,
  "order_id": "111-222",
  "customer_id": "C123",
  "marketplace_id": "ATVPDKIKX0DER",
  "producer": "checkout",
  "producer_time": "2026-08-06T01:00:00Z",
  "sequence": 1,
  "payload": {
    "currency": "USD",
    "totals": {"grand_cents": 4599},
    "lines": [{"asin": "B00", "qty": 1, "unit_price_cents": 3999}],
    "shipping_address": {"country": "US", "postal": "98101"}
  }
}
```

```json
{
  "event_id": "01J8Z9...",
  "event_type": "OrderShipped",
  "event_version": 2,
  "order_id": "111-222",
  "sequence": 4,
  "payload": {
    "shipment_id": "S99",
    "carrier": "UPS",
    "tracking": "1Z...",
    "line_ids": [1]
  }
}
```

## Appendix B — State machine (consumer view)

```text
PLACED → PAID → ALLOCATED → SHIPPED → DELIVERED
PLACED → CANCELLED
PAID → REFUND_STARTED → REFUNDED
Illegal examples: DELIVERED → PLACED; SHIPPED → PLACED
```

## Appendix C — Scale checklist

- [ ] event_id required  
- [ ] Dedup + hash conflict 409  
- [ ] Partition key = order_id  
- [ ] ACK after durable append  
- [ ] Schema registry gated  
- [ ] Fulfillment/notify/analytics isolated  
- [ ] DLQ + alarms  
- [ ] Replay runbook  
- [ ] PII policy  
- [ ] Consumer idempotency  

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Effectively-once | No duplicate business effect |
| Dedup window | TTL for event_id records |
| Consumer group | Independent offset cursor |
| DLQ | Dead-letter queue |
| Sequence gap | Missing per-order seq |
| Registry | Schema compatibility authority |
| Outbox | DB→bus reliable publish pattern |

## Appendix E — Estimation cheat-sheet

```text
events/s ≈ orders/s × events_per_order × peak_factor
partitions ≈ events/s / 1000
dedup_bytes/day ≈ events/s × 86400 × ~80B
fanout ≈ events/s × groups
```

## Appendix F — Degrade ladder

| Level | Action |
|-------|--------|
| L1 | Shed noncritical event types (browsing telemetry if mixed—prefer separate) |
| L2 | Pause analytics consumers |
| L3 | Shed notifications |
| L4 | 429 producers with lower priority |
| L5 | Regional cell shed / admit only Paid/Shipped |

## Appendix G — Authz matrix

| Producer | Allowed types |
|----------|---------------|
| checkout | OrderPlaced, OrderCancelled(pre-pay) |
| payments | OrderPaid, Refund* |
| fulfillment | Allocated, Shipped, Delivered |
| returns | Return* |
| admin | replay only, not forge Paid |

## Appendix H — Invariant tests

1. Duplicate POST → one log record effect.  
2. Hash mismatch → 409.  
3. All events for order land on same partition.  
4. Consumer redrive → no double FC work.  
5. Incompatible schema → produce reject.  
6. Analytics lag doesn’t increase fulfillment lag.  

## Appendix I — Hot index for support

```text
ORDER_EVENTS#{order_id} → list (event_id, type, ingest_time, offset)
Write async from log; support GET uses this, not full bus scan
```

## Appendix J — Replay API sketch

```text
POST /v1/admin/replay
{
  "group": "analytics",
  "from": "2026-08-01T00:00:00Z",
  "to": "2026-08-02T00:00:00Z",
  "event_types": ["OrderPlaced", "OrderShipped"],
  "rate_limit_per_sec": 10000
}
```

## Appendix K — Ownership

| Concern | Owner |
|---------|-------|
| Ingest API + dedup + bus | Events platform team |
| Schemas for OrderPlaced | Order service + platform |
| Fulfillment consumer | FC software team |
| Notifications templates | Comms team |
| Lake schemas | Analytics engineering |

## Appendix L — Interview closing line

> “We ACK only after durable, idempotent append; we order by order_id partitions; we evolve via a registry; and we isolate fulfillment from analytics so Prime Day fan-out stress sheds the soft path first—effectively-once side effects, not fairy-tale exactly-once networks.”

---


## Appendix M — Producer SDK guidelines

1. Generate `event_id` before first send; reuse on retry.  
2. Include monotonic `sequence` per `order_id` from Order DB outbox when possible.  
3. Treat 503/429 as retryable with jittered exponential backoff.  
4. Treat 409 as a **bug** — log loudly; do not retry different body.  
5. Prefer binary codec in SDK while keeping JSON for local debug fixtures.  
6. Bound payload size; put blobs in object storage and send URIs.  
7. Propagate trace headers for end-to-end latency charts.  
8. Unit-test schema fixtures against registry in CI.

## Appendix N — Consumer SDK guidelines

1. Dedup table keyed by `event_id` (TTL ≥ bus retention or longer).  
2. Apply state machine; ignore/illegal → metric + optional DLQ.  
3. Commit offsets only after durable side effects.  
4. Implement graceful shutdown (finish in-flight, then commit).  
5. Expose `lag`, `process_p99`, `dup_skip_rate` metrics by default.  
6. Support replay by being side-effect idempotent.  
7. Separate retryable vs non-retryable exceptions.  
8. Never call ingest API from consumer for “fixups” without rate limits.

## Appendix O — Gap / out-of-order playbook

```text
if incoming.seq == expected:
  apply; expected++
  while buffer has expected: apply
elif incoming.seq > expected:
  buffer for T_gap (e.g. 5–30s)
  if timeout: fetch Order SoT snapshot; reconcile; DLQ residual
elif incoming.seq < expected:
  drop as duplicate/stale (metric)
```

Document per consumer whether gaps are fatal (fulfillment) or soft (analytics).

## Appendix P — Topic topology options

| Topology | When | Trade-off |
|----------|------|-----------|
| Single `order.events` | MVP–10× | Simple; large fan-in |
| Split by domain (`order.lifecycle`, `order.payments`) | 10×–100× | Clearer authz |
| Split by type | 100×+ filter efficiency | More ops surface |
| Compacted changelog + full log | Projections | Dual maintenance |

**Recommendation:** single lifecycle topic to 10×; add payment/returns topics when authz or volume demands.

## Appendix Q — Capacity worksheet (fill in interview)

```text
Peak orders/s: ____
Events/order: ____
Peak events/s: ____
Groups: ____
Fanout msgs/s: ____
Partitions (= events/s / 1000 × headroom): ____
Dedup TTL hours: ____
Dedup GB ≈ events/s × 86400 × TTL/24 × 80B / 1e9: ____
Fulfillment lag SLO: ____
Notification shed threshold lag: ____
```

## Appendix R — Sample alarms (PagerDuty-ish)

| Alarm | Threshold | Team |
|-------|-----------|------|
| ingest_p99 > 100ms for 5m | warn | platform |
| ingest_p99 > 250ms for 5m | page | platform |
| fulfillment_lag > 30s | page | fulfillment+platform |
| dlq_depth > 100 | page | owning consumer |
| schema_reject_rate > 1% | warn | producer owner |
| 409_rate spike | warn | producer owner |
| dedup_store_throttle | page | platform |

## Appendix S — Comparison: push webhooks vs pull bus

| | Webhooks to consumers | Central bus |
|--|-----------------------|-------------|
| Coupling | High | Low |
| Retry storm | Consumer endpoints melt | Bus absorbs |
| Ordering | Hard | Natural per partition |
| Replay | Ad hoc | First-class |
| Amazon fit | Poor at this scale | **Preferred** |

Ingest API may still **accept** HTTP from producers; fan-out should be bus/pull.

## Appendix T — End-to-end tracing story

```text
trace_id on PlaceOrder
  → outbox event headers
  → ingest span (validate, dedup, append)
  → consumer span (fulfillment apply)
  → FC API span
```

Dashboard: p99 PlaceOrder→FulfillmentApply; break down by stage to find regressions.

## Appendix U — Multi-tenant marketplace note

If 3P sellers emit events, isolate:

- Separate producer credentials and quotas.  
- Validate seller owns `order_id` / ASIN.  
- Consider separate topics to protect 1P fulfillment latency.  
- Scrub seller PII before analytics lake.

## Appendix V — What “done” looks like in the loop

You can draw:

1. Envelope + API codes  
2. Dedup + partition key  
3. Three consumers with different SLOs  
4. Schema expand/contract example  
5. One failure table (dup, gap, poison, lag)

…and defend effectively-once **effects** without claiming magic exactly-once RPC.

---

*End of ecommerce order-event ingestion API system design.*
