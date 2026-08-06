# System Design: Generic Scalable Microservice (Amazon-Style Blueprint)

> **Focus areas:** Cell architecture · Data ownership · Async messaging · SLOs · Deploy · Observability · Multi-AZ/Region  
> **Style:** Amazon SDE III “design a scalable service” interview blueprint with progressive scale (10× → 100× → 1,000×)  
> **Amazon themes:** Single-threaded ownership · Customer impact · Operational excellence · Frugality · Mechanisms over intentions  
> **Quality bar:** Clear boundaries, explicit consistency, honest MVP vs extreme-scale paths, measurable SLOs

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

Goal: When the interviewer says **“design a scalable microservice”**, don’t invent a random product—**force a concrete domain**, then apply this Amazon-style blueprint. This doc uses a placeholder domain: **OrderIntent Service** (accepts intents, validates, persists, emits events)—patterns transfer to almost any Amazon service.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the service’s **single responsibility**? | Own one domain noun + lifecycle (e.g. OrderIntent) | Clear bounded context; no shared DB |
| F2 | Sync APIs? | CRUD + command APIs with idempotency | REST/gRPC; durable before ACK |
| F3 | Async? | Emit domain events; consume upstream events | SNS/SQS/EventBridge; outbox |
| F4 | Who are clients? | Internal services + limited external via gateway | AuthZ; SLAs per client class |
| F5 | Data ownership? | This service is source of truth for its entities | No foreign writes; anti-corruption layer |
| F6 | Consistency needs? | Strong within aggregate; eventual across services | Avoid distributed transactions |
| F7 | Multi-tenant? | Yes—retail accounts / seller ids | `tenant_id` everywhere; quotas |
| F8 | Admin / ops? | Replay events, repair tools, kill switches | Control plane + audit |
| F9 | Search / list? | Light list by key; heavy search elsewhere | Don’t turn service into ES |
| F10 | Multi-region? | DR required; active-active optional | Home region / cell story |
| F11 | Compliance? | PII, encryption, retention | KMS, scrubbing, TTLs |
| F12 | Evolution? | Versioned APIs & events | Compatibility windows |

**MVP functional scope (template):**

1. Define **aggregates** owned by the service; persist strongly consistent per aggregate.  
2. Expose **idempotent commands** and **reads** (read-your-writes on primary).  
3. Emit **domain events** via transactional outbox.  
4. Enforce authn/z, validation, quotas.  
5. Multi-AZ deployment with health checks, autoscaling, dashboards, alarms.  
6. Basic cell or shard plan documented even if not implemented day 1.

**Out of MVP:**

- Cross-service 2PC / XA transactions  
- Perfect global linearizability across regions  
- Universal query language over all fields  
- Shared libraries that create distributed monolith coupling  
- “Micro” services split so small that chatty coupling dominates

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target (baseline example) |
|---|----------|-----------------|---------------------------|
| N1 | Availability SLO? | Tier-1 internal | 99.9%–99.99% depending on criticality |
| N2 | Latency SLO? | Command p99 | < 100–300ms in-region (domain-dependent) |
| N3 | Durability? | No lost accepted writes | Sync persist + multi-AZ replication |
| N4 | RPO / RTO? | DR | RPO minutes→seconds; RTO tens of minutes (explicit) |
| N5 | Scalability? | Horizontal | Stateless app tier; partitioned data |
| N6 | Consistency? | Per-key strong | Conditional writes / transactions per aggregate |
| N7 | Operability? | One-pager + runbooks | Alarms actionable; on-call sustainable |
| N8 | Deploy safety? | Canary + rollback | < minutes to rollback |
| N9 | Cost? | Efficient at idle & peak | Autoscale; right-size storage class |
| N10 | Security? | Least privilege | IAM roles; secrets manager; private subnets |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client sends command with idempotency key → validate → persist → outbox event → 200.  
2. Read by id → primary/cache → response.  
3. Downstream consumes event → updates its projection.  
4. Canary deploy → metrics OK → full shift.  
5. Autoscaling on CPU/RPS/queue depth.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate command (same idempotency key) | Return original result |
| Partial failure after persist before ACK | Client retries; idempotent |
| Outbox publisher lag | Domain state OK; eventual consumers catch up; alarm on lag |
| Downstream poison event | DLQ; do not block publisher forever |
| Hot partition key | Split key design / secondary randomization |
| Dependency timeout | Fail fast / degrade per policy; bulkhead |
| Bad deploy | Canary abort; rollback |
| AZ loss | Multi-AZ continue; capacity headroom  N/(N-1) |
| Region loss | Failover runbook; home-cell promotion |
| Schema incompatible event | Versioning; consumer tolerant readers |
| Thundering retry | Jitter; retry budgets |
| Data corruption bug | Repair tool + event replay from snapshots |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak command QPS | 5K | 50K | 500K | 5M |
| Peak read QPS | 20K | 200K | 2M | 20M |
| Entities stored | 100M | 1B | 10B | 100B |
| Avg payload | 2 KB | 2 KB | 2–4 KB | 2–4 KB |
| Events emitted / s | 5K | 50K | 500K | 5M |
| Tenants | 100K | 1M | 10M | 100M |
| Cells | 1 | 1–3 | 10–30 | 100+ |
| On-call sev load | manageable | need automation | cell isolation critical | platformized ops |

**What each jump forces:**

- **10×:** Caching; read replicas; queue consumers autoscaled; connection pools.  
- **100×:** Cells / shards by tenant or entity key; async everything non-critical; CQRS for hot reads.  
- **1,000×:** Cell router; per-cell datastores; hierarchical aggregations; strict dependency SLOs; self-service ops.

### 1.5 Etc. (Constraints & Assumptions)

- **Two-pizza team** owns this service end-to-end (code, data, SLO, on-call).  
- Prefer **mechanisms** (canary autos, idempotency mandatory) over “please be careful.”  
- Shared DB with other services is a **hard no**.  
- Events are part of the API surface—version them.  
- This blueprint is intentionally generic; plug in your domain nouns.

**Scope statement:**

> Design an Amazon-style scalable microservice with clear data ownership, sync command/query APIs, async event integration, multi-AZ reliability, cell-friendly scaling, SLOs, safe deploys, and deep observability—evolving from a single-cell baseline through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split read/write classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Commands (writes) | 5K QPS | 5M QPS | Durable + idempotent |
| Strong reads | 10K QPS | 10M QPS | Primary / quorum |
| Eventually consistent reads | 10K QPS | 10M QPS | Replicas / cache |
| Event publish | 5K QPS | 5M QPS | Outbox dispatcher |
| Event consume (inbound) | varies | varies | Bulkheads |

### 2.2 Storage

```text
100M entities × 2 KB = 200 GB baseline data
+ indexes (~50–100%) → ~300–400 GB
1,000×: 100B × 2 KB = 200 TB → must partition / cell; cold tiering
Write amp: consider DynamoDB WCU or Aurora IOPS explicitly in interview
```

### 2.3 Cache

```text
Hot keys: 1% of entities serve 50–80% reads (classic)
Cache working set baseline: 1M hot × 2 KB = 2 GB → easy
At 100×+: sharded Redis / DAX / application caches per cell
```

### 2.4 Event bus throughput

```text
5K events/s × 2 KB ≈ 10 MB/s
5M/s × 2 KB ≈ 10 GB/s → batching, compression, selective fan-out, archival
```

### 2.5 Capacity headroom

Multi-AZ: size for **losing one AZ** still meeting SLO (often ~30–50% extra).  
Cells: size each cell with headroom; whales get dedicated cells.

### 2.6 Critical bottlenecks (rank ordered)

1. **Datastore hot partitions** — key design.  
2. **Synchronous dependency chains** — latency & availability multiplication.  
3. **Chatty over-fetch** — API design.  
4. **Event fan-out cost** — filter / shard topics.  
5. **Deploy coupling** — library version hell.  
6. **Thundering herds** on cache expiry / failover.  
7. **On-call toil** at 100× without automation.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| **Aggregate** | Consistency boundary (e.g. OrderIntent) |
| **Command** | State-changing request (idempotent) |
| **Query** | Read model access |
| **Domain event** | Fact that happened (immutable) |
| **Outbox** | Durable “event to publish” with state txn |
| **Inbox** | Deduped consumer side |
| **Cell** | Independent deployable slice of data+compute |
| **Anti-corruption layer** | Translate foreign models |
| **SLO / Error budget** | Operating contract |

### 3.2 Sync path

```text
API → AuthZ → Validate → Idempotency →
  Transaction {
    apply command to aggregate
    write outbox
  } → Response
```

Read path: API → AuthZ → cache → DB (replica policy) → response.

### 3.3 Async path

```text
Outbox poller / txn CDC → Event bus (SNS/EventBridge/Kafka)
  → Subscribers (SQS per consumer) → Inbox dedupe → handler
```

Prefer **per-consumer queues** so one slow consumer doesn’t block others.

### 3.4 Data ownership rules (Amazon-critical)

1. Only this service writes its tables.  
2. Others read via **APIs or events**, not SQL joins across ownership.  
3. Foreign keys across services are **logical ids**, not DB constraints.  
4. If you need another service’s data, cache a projection you can afford to be stale—or call sync with budget.

### 3.5 Storage options

| Store | When |
|-------|------|
| **DynamoDB** | Key-value / wide access patterns known; extreme scale |
| **Aurora / RDS** | Richer queries; transactional aggregates |
| **S3** | Blobs, archives, large payloads |
| **Elasticsearch/OpenSearch** | Search projections (derived) |
| **ElastiCache/Redis** | Hot keys, locks carefully |

Pick from **access patterns first**, not fashion.

### 3.6 Cell architecture

```text
tenant_id or entity_id → cell_id (lookup / consistent hash)
Each cell: compute + datastore + queues + configs
Router at edge knows mapping
No synchronous cross-cell transactions
```

Benefits: blast radius, scaling whales, fair deploy risk.  
Costs: ops complexity, cross-cell queries hard (usually forbidden).

### 3.7 Consistency menu (say aloud)

| Pattern | Use |
|---------|-----|
| Single-aggregate ACID / conditional write | Default commands |
| Saga / workflow | Cross-service business process |
| Outbox + at-least-once events | Integration |
| CQRS read models | Hot/complex reads |
| Idempotency keys | Client retries |
| Optimistic concurrency (`version`) | Lost-update prevention |

Avoid: 2PC across services.

### 3.8 Dependency & resilience policy

- Timeouts on every sync call.  
- Retries only with idempotency / budgets.  
- Circuit breakers + bulkheads.  
- Fallback: stale cache / default / fail.  
- Critical vs non-critical dependencies classified.

### 3.9 Deploy & release

| Mechanism | Purpose |
|-----------|---------|
| Immutable artifacts | Reproducible |
| Canary | Small % traffic / cells |
| Automated rollback | Error-rate / latency gates |
| Feature flags | Decouple deploy from release |
| Schema expand/contract | Safe migrations |
| One-box / baking | Amazon-style bake time |

### 3.10 Trade-off tables

| Concern | Choice | Why |
|---------|--------|-----|
| Sync vs async | Async for non-user-critical fan-out | Availability |
| Monolith vs micro | Start modular monolith if team tiny; split on seams | Cognitive load |
| SQL vs Dynamo | Access patterns | Correctness of scale story |
| Cache | Cache-aside + TTL + stampede control | Simplicity |
| Multi-region | Active-passive first | Correctness |
| Cells | Introduce at 100× or for isolation needs | Complexity tax |

---

## 4. Architecture Diagram

### 4.1 End-to-end single cell

```text
  Clients / Peer Services
            |
            v
     +-------------+
     | API / gRPC  |
     +------+------+
            |
            v
     +-------------+     +---------------+
     | Service App |---->| Cache (Redis) |
     | (stateless) |     +---------------+
     +------+------+
            |
            +-------------------+
            |                   |
            v                   v
     +-------------+     +---------------+
     | Primary DB  |     | Outbox table  |
     | (owned)     |     +-------+-------+
     +-------------+             |
                                 v
                         +---------------+
                         | Event Bus     |
                         +-------+-------+
                                 |
                 +---------------+---------------+
                 v               v               v
              Consumer A     Consumer B       DLQ
```

### 4.2 Sequence: idempotent command + outbox

```text
Client        API          DB(+Outbox)      Publisher      Bus
  |--Cmd+Key-->|             |                |            |
  |            |-- begin --->|                |            |
  |            |   write agg+| outbox row     |            |
  |            |<-- commit --|                |            |
  |<-- 200 ----|             |                |            |
  |            |             |<-- poll -------|            |
  |            |             |-- mark sent -->|-- publish >|
```

### 4.3 Cell architecture

```text
              +------------- Cell Router --------------+
              |  map(tenant/entity) → cell             |
              +------+-------------+-------------+-----+
                     |             |             |
                     v             v             v
                  Cell 1        Cell 2        Cell N
               API+DB+Q+Cache  API+DB+Q+Cache ...
```

### 4.4 Multi-AZ

```text
        Region
    +-----AZ-a-----+   +-----AZ-b-----+   +-----AZ-c-----+
    | app instances|   | app instances|   | app instances|
    +--------------+   +--------------+   +--------------+
              \             |              /
               \            v             /
                +----- Datastore multi-AZ -----+
```

### 4.5 Dependency bulkheads

```text
Inbound QPS
   |
   +-- thread/conn pool → Dependency Critical (checkout)
   +-- separate pool    → Dependency NonCrit (recommendations)
   +-- async only       → Analytics
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Failure modes & mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Instance crash | In-flight requests fail | Stateless; client retry + idempotency |
| AZ outage | Capacity loss | Multi-AZ; N-1 capacity |
| DB failover | Brief errors/latency | Backoff; hedged reads carefully |
| Cache down | Latency ↑ load on DB | Fail open to DB with shed; warm |
| Event bus outage | Consumer lag | Buffer outbox; alarm; do not lose writes |
| Poison message | Consumer loop | DLQ + alert owner |
| Bad deploy | Error spike | Canary + auto rollback |
| Dependency Sev | Latency/errors | Breaker; degrade |
| Data bug | Wrong state | Repair + replay tooling |
| Region loss | Hard outage | DR runbook; periodic failover tests |

#### 5.1.2 Consistency model

- Commands: **strong** per aggregate / key.  
- Cross-service: **eventual** via events.  
- Reads: choose RY W vs eventually consistent explicitly per API.  
- Idempotency records: strong with TTL.

#### 5.1.3 Exactly-once vs at-least-once

Service promises:

1. Accepted commands persist.  
2. Events delivered **at-least-once**.  
3. Consumers must be idempotent (inbox).  
4. Exactly-once *effect* is an application property.

#### 5.1.4 Amazon ownership themes

- **Single-threaded ownership:** your team owns the SLO—no “thrown over wall.”  
- **Customer impact:** map metrics to customer journeys (checkout vs reporting).  
- **Correctness mechanisms:** idempotency required by platform libraries.  
- **Operational excellence:** runbooks, game days, error budgets.  
- **Frugality:** cells and caches sized from measurements, not guesses forever.  
- **Dive deep:** hot key, partition imbalance, retry amplification.

### 5.2 Scalability

#### 5.2.1 Progressive scale changes

| Scale | Change |
|-------|--------|
| 1× | Single cell, multi-AZ, cache-aside, outbox |
| 10× | Read replicas / DAX; consumer autoscaling; tighter pools |
| 100× | Shard/cell by tenant; CQRS for hot queries; async noncritical |
| 1,000× | Many cells; router; per-cell everything; platform automation |

#### 5.2.2 Sharding / cell keys

Good keys: high cardinality, even access, align with ownership (`tenant_id`, `order_id`).  
Bad keys: low cardinality status fields; monotonically increasing without salt for writes.

Whales: isolate to dedicated cell; don’t let one seller melt a shared shard.

#### 5.2.3 CQRS when needed

When read patterns diverge (dashboards, search), build **projections** updated by events.  
Projection lag is an SLO (“search freshness p99 < 30s”), not an accident.

#### 5.2.4 Backpressure

- Shed load at API (503 + Retry-After) before DB melts.  
- Queue-based consumers pull at sustainable rates.  
- Prefer load shedding over unbounded queue growth for sync UX paths.

### 5.3 Maintainability

#### 5.3.1 Code & API evolution

- Version APIs (`/v1`, `/v2`) with overlap windows.  
- Events: additive fields first; consumers ignore unknown (tolerant readers).  
- Expand/contract DB migrations.  
- Avoid distributed monolith via shared DB libraries.

#### 5.3.2 Testing strategy

| Layer | What |
|-------|------|
| Unit | Domain invariants |
| Contract | API/event schemas |
| Integration | DB + outbox |
| Load | Hot keys, failover |
| Game day | AZ loss, dependency fail, poison |

#### 5.3.3 Observability (golden)

| Type | Examples |
|------|----------|
| Metrics | QPS, latency, error, saturation; DB WCU/CPU; queue lag; idempotent hit rate |
| Logs | Structured; request_id; no secrets |
| Traces | Command → DB → publish |
| Alarms | SLO burn; lag; canary fail |
| Dashboards | Customer journey oriented |

#### 5.3.4 SLO / error budgets

Example:

- Availability 99.9% → error budget 0.1%.  
- When budget burned: freeze features, focus reliability.  
- Separate **cause** (dependency) vs **customer-facing** SLO.

#### 5.3.5 Security

- Private subnets; Security Groups least privilege.  
- IAM task roles.  
- KMS encryption.  
- Secrets Manager; rotation.  
- AuthZ at API; audit privileged ops.  
- PII minimization; retention jobs.

### 5.4 Progressive scale deep dive

**MVP:** One service, Aurora/Dynamo, Redis cache, outbox→SNS→SQS, multi-AZ ECS/EKS/Lambda*, canary deploy, CloudWatch+X-Ray, runbooks.  

**10×:** Connection pool discipline; cache stampede locks; consumer concurrency autoscaling; adaptive load shedding.  

**100×:** Cells; per-cell datastores; router; CQRS projections; synthetic canaries per cell; self-service repair tools.  

**1,000×:** Cell platform (paved road); automated rebalancing; hierarchical aggregations for global metrics; dedicated isolation for top tenants; multi-region active-active only where conflict-free.

\*Compute choice depends on latency/cold-start/workload shape.

### 5.5 Outbox vs CDC

| Approach | Pros | Cons |
|----------|------|------|
| Transactional outbox table | Exact with app txn | Publisher component to run |
| DB CDC (DMS/streams) | Less app code | Harder exactly-with-business-event semantics |

Interview default: **outbox** for domain events.

### 5.6 Library vs service coupling

Prefer:

- Published **OpenAPI / event schemas**.  
- Thin clients generated.  
- No shared ORM entities across teams.

### 5.7 Deal-breaker gallery

| Deal-breaker | Fix |
|--------------|-----|
| Shared database across services | APIs + events |
| No idempotency on commands | Mandatory keys |
| Sync chain of 8 services | Collapse / async |
| Unbounded retries | Budgets + jitter |
| Single AZ | Multi-AZ always |
| Global lock for correctness | Per-key concurrency |
| Search-in-primary-DB at scale | Projection |
| Undocumented SLO | Write SLO first |

---

## 6. Wrap-Up

### 6.1 Key decisions

1. Bounded context with exclusive data ownership.  
2. Idempotent commands; transactional outbox events.  
3. Stateless compute; multi-AZ; horizontal scale.  
4. Explicit consistency & dependency policies.  
5. Cells for blast radius at high scale.  
6. Canary deploys + feature flags + expand/contract schema.  
7. SLOs, error budgets, journey-oriented observability.

### 6.2 Top risks

| Risk | Mitigation |
|------|------------|
| Distributed monolith | Ownership rules; reviews |
| Hot partitions | Key redesign; isolation |
| Event poisoning | DLQ + owners |
| Dependency amplification | Timeouts/bulkheads |
| Deploy regressions | Canary gates |
| On-call toil | Automation; cells |

### 6.3 45-minute interview plan

| Minutes | Focus |
|---------|-------|
| 0–5 | Clarify domain noun, ownership, sync/async |
| 5–12 | Estimation: QPS, storage, events |
| 12–22 | HLD: API, DB, cache, outbox, bus |
| 22–32 | Reliability: idempotency, multi-AZ, deps |
| 32–40 | Scale: cells, CQRS, 1000× |
| 40–45 | SLO, deploy, ops wrap-up |

### 6.4 60-second pitch

> “I’d define a clear bounded context with exclusive data ownership, expose idempotent command/query APIs, and publish domain events through a transactional outbox. The app tier is stateless and multi-AZ; data is partitioned for scale and eventually cell-routed for blast radius. Dependencies have timeouts, bulkheads, and explicit degrade modes. We operate with SLOs and error budgets, canary deploys, and journey-level dashboards—so the team owns customer impact end-to-end.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Boundaries & ownership

1. How do you choose service boundaries?  
2. What symptoms indicate a distributed monolith?  
3. When is a modular monolith better?  
4. How do you prevent “just join their table”?  
5. Anti-corruption layer examples.  
6. Who owns the canonical Customer name field?

### 7.2 Consistency & data

7. Aggregate design for your domain?  
8. Optimistic vs pessimistic concurrency.  
9. Outbox pattern step-by-step.  
10. Inbox / consumer idempotency.  
11. Saga vs 2PC—when saga breaks down?  
12. Read-your-writes across replicas—how?  
13. TTL and soft-delete strategies.  
14. Repair tools after a logic bug.

### 7.3 APIs & idempotency

15. Idempotency key storage and TTL.  
16. PUT vs POST semantics for creates.  
17. Pagination under concurrent writes.  
18. Error model for clients (retryable?).  
19. gRPC vs REST for internal APIs.  
20. Bulk APIs vs chatty APIs.

### 7.4 Async & events

21. At-least-once implications for consumers.  
22. Ordering guarantees—what can you promise?  
23. Fan-out topics vs per-consumer queues.  
24. Poison message handling.  
25. Event versioning strategies.  
26. CDC vs outbox trade-offs.  
27. Backfill / replay design.  
28. Exactly-once processing myths.

### 7.5 Scale & cells

29. How do you pick a cell key?  
30. Cell migration steps for a tenant.  
31. Cross-cell query—why avoid?  
32. Hot neighbor / whale isolation.  
33. Shuffle sharding vs dedicated cells.  
34. Global secondary indexes at scale.  
35. Cache stampede controls.  
36. Estimating WCU/RCU or IOPS.

### 7.6 Resilience

37. Timeout budgeting across a call graph.  
38. Retry amplification across layers.  
39. Circuit breaker configuration.  
40. Load shedding strategies.  
41. Multi-AZ capacity planning.  
42. Dependency classification matrix.  
43. Brownout vs blackout handling.  
44. Chaos engineering minimum set.

### 7.7 Deploy & change management

45. Expand/contract schema example.  
46. Canary analysis signals.  
47. Feature flag vs config vs code.  
48. Breaking event changes—how to roll out.  
49. Blue/green vs rolling vs canary.  
50. One-box testing value.

### 7.8 Observability & SLOs

51. Write an SLO for this service.  
52. Error budget policy.  
53. Customer-impact metrics vs system metrics.  
54. Trace sampling that still catches Sevs.  
55. Queue lag SLO vs API SLO.  
56. High-cardinality label dangers.  
57. On-call health metrics (pages/week).

### 7.9 Security & compliance

58. Least-privilege IAM for tasks.  
59. Encrypting PII fields.  
60. Audit logs for admin repair tools.  
61. Tenant isolation bugs—tests?  
62. Dependency supply chain.  
63. Secrets rotation without downtime.

### 7.10 Amazon leadership / ownership

64. Your dependency has a Sev—what do you do?  
65. How do you say no to a cross-service DB join request?  
66. Error budget exhausted—product wants feature?  
67. Cost +50% after launch—investigation plan.  
68. Define operational excellence for a new service.  
69. Mentoring juniors on idempotency mechanisms.

### 7.11 Interview traps

70. Jumping to Kubernetes details before ownership.  
71. Ignoring estimation.  
72. Promising global strong consistency cheaply.  
73. No idempotency story.  
74. Shared database “for speed.”  
75. Sync call graph depth ignored.  
76. No deploy/rollback story.  
77. Observability as afterthought.  
78. Cells mentioned without routing/migration pain.  
79. Equating microservices with scalability (architecture ≠ QPS).  
80. Hand-waving multi-region conflict resolution.

### 7.12 Comparison questions

81. This blueprint vs serverless-only design.  
82. DynamoDB vs Aurora for your access patterns.  
83. Kafka vs SNS/SQS for Amazon shops.  
84. Mesh retries vs app retries ownership.  
85. BFF vs domain microservice responsibilities.

---

## 8. Appendices

### 8.1 Schema sketches (example OrderIntent)

```text
OrderIntent {
  intent_id, tenant_id, version,
  state, customer_id, items[],
  amounts, created_at, updated_at,
  idempotency_key
}

IdempotencyRecord {
  tenant_id, key, response_hash, intent_id, expires_at
}

Outbox {
  id, aggregate_id, event_type, payload, created_at, published_at?
}
```

### 8.2 API checklist

| API | Notes |
|-----|-------|
| `POST /v1/intents` | Idempotency-Key |
| `GET /v1/intents/{id}` | RY W option |
| `POST /v1/intents/{id}/cancel` | Conditional on version |
| `GET /v1/tenants/{id}/intents` | Paginated; bounded |
| Admin repair | Audited |

### 8.3 Event catalog (example)

| Event | When |
|-------|------|
| `IntentAccepted` | After durable create |
| `IntentCancelled` | After cancel |
| `IntentExpired` | TTL workflow |

Consumers: fulfillment, analytics, notifications (async).

### 8.4 SLO worksheet

| SLI | SLO | Window |
|-----|-----|--------|
| Successful commands / total | 99.9% | 28d |
| Command latency p99 | ≤ 200ms | 28d |
| Outbox publish lag p99 | ≤ 5s | 7d |
| Poison / DLQ age | ≤ 1h for Sev pages | continuous |

### 8.5 Dependency matrix

| Dependency | Critical? | Timeout | Fallback |
|------------|-----------|---------|----------|
| Own DB | Yes | 50ms | Fail |
| Auth/policy | Yes | 20ms | Fail closed |
| Pricing | Sometimes | 100ms | Cached price / fail |
| Recommendations | No | 50ms | Empty list |
| Analytics | No | n/a | Async only |

### 8.6 Glossary

| Term | Definition |
|------|------------|
| Bounded context | Domain model boundary |
| Aggregate | Consistency unit |
| Outbox | DB-backed pending events |
| Cell | Isolated slice of the service |
| Error budget | Allowed unreliability |
| Expand/contract | Safe schema migration pattern |
| Bulkhead | Resource isolation |
| Tolerant reader | Ignore unknown fields |

### 8.7 Progressive scale checklist

- [ ] Ownership declared  
- [ ] Idempotency on commands  
- [ ] Outbox/events  
- [ ] Multi-AZ + N-1 capacity  
- [ ] Timeouts/bulkheads on deps  
- [ ] SLO + dashboards  
- [ ] Canary + rollback  
- [ ] Hot-key plan  
- [ ] Cell story for 100×  
- [ ] Repair/replay tools  

### 8.8 Deploy checklist

- [ ] Automated tests gate  
- [ ] Canary % + cell bake  
- [ ] Latency/error abort  
- [ ] Feature flags for risky behavior  
- [ ] Schema expand first  
- [ ] Dashboards linked in CR  

### 8.9 Interview “say this” summary

> Own one bounded context, idempotent writes, outbox events, multi-AZ stateless compute, partition then cell, timeouts everywhere, SLOs with error budgets, canaries—customer impact owned by the team.

### 8.10 Operator runbooks (titles)

- DB failover  
- Cache outage  
- Outbox lag  
- DLQ spike  
- Dependency breaker open  
- Bad canary rollback  
- Cell hot partition  
- Region DR promote  

### 8.11 Reliability test plan

1. Kill 1 AZ — SLO holds with headroom.  
2. Duplicate command storm — no double apply.  
3. Block event bus — writes still ACK; lag alarms.  
4. Poison event — DLQ; other events progress.  
5. Canary bad build — auto rollback.  
6. Hot key load — isolation or shed without total outage.

### 8.12 Worked scale example (100×)

```text
5K → 500K command QPS
If Dynamo: partition by tenant+id; estimate peak WCUs
Cells: start ~20 cells × 25K QPS each with headroom
Events 500K/s: batch publish; shard streams
Reads 2M QPS: cache + replicas + CQRS for lists
```

### 8.13 Worked scale example (1,000×)

```text
5M command QPS → hundreds of cells / dedicated platforms
Router + metadata service for assignments
No cross-cell joins; global analytics via async pipelines
Ops must be automated (cell lifecycle APIs)
```

### 8.14 Pseudocode: command with outbox

```text
function AcceptIntent(cmd):
  existing = Idempotency.Get(cmd.tenant, cmd.key)
  if existing: return existing.response
  txn:
    agg = apply(cmd)
    Outbox.Add(IntentAccepted(agg))
    Idempotency.Put(cmd.tenant, cmd.key, response)
  return response
```

### 8.15 Pseudocode: consumer inbox

```text
function OnEvent(e):
  if Inbox.Seen(e.id): return
  txn:
    handle(e)
    Inbox.Mark(e.id)
```

### 8.16 Final trap table

| Trap | Correction |
|------|------------|
| Shared DB | Owned APIs/events |
| No SLO | Write SLIs first |
| Micro = fast | Measure; design access patterns |
| Multi-region active-active for mutable aggregates | Conflict story required |
| “We’ll retry until success” | Budgets + DLQ |
| Skip estimation | Do QPS/storage/events |

### 8.17 Amazon bar reminders

- Start with customer / client journeys.  
- Mechanisms for idempotency and canaries.  
- Own on-call reality.  
- Cells as blast radius, not buzzword.  
- Data ownership is non-negotiable.

### 8.18 Related paved-road map (AWS-shaped)

| Concern | Common tool |
|---------|-------------|
| Compute | ECS/EKS/Lambda |
| Data | DynamoDB/Aurora |
| Cache | ElastiCache/DAX |
| Bus | SNS/SQS/EventBridge |
| Edge | ALB/API GW |
| Obs | CloudWatch/X-Ray/OTel |
| Deploy | CodeDeploy/pipelines |
| Secrets | Secrets Manager/KMS |

### 8.19 One-page design template (fill-in)

```text
Service name:
Owns (aggregates):
Does not own:
Commands:
Queries:
Events published:
Events consumed:
SLOs:
Sync dependencies:
Async dependencies:
Data store + key:
Cell key:
Top risks:
Kill switches:
```

### 8.20 When interviewer keeps it abstract

Ask:

1. What noun do we own?  
2. Who calls us sync vs async?  
3. Latency/availability tier?  
4. Multi-tenant?  
5. Multi-region needed?  

Then execute this blueprint with their answers.

---

*End of document — Generic Scalable Microservice Blueprint (Amazon SDE III)*
