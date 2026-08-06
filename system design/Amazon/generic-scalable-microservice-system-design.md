# System Design: Generic Scalable Microservice

> **Focus areas:** Service template · APIs · Data ownership · Idempotency · Outbox · Caching · Cells · SLOs · Operability · Multi-tenant
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **Generic scalable microservice blueprint** — Amazon two-pizza service standards

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-q&a)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design a **generic scalable microservice** template: clear API/data ownership, idempotent writes, outbox events, caching, cells, SLOs, and operability—usable as the default Amazon service shape.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Production microservice blueprint | Entire product portfolio |
| Scope | One bounded context + data store | Shared DB spaghetti |
| Amazon lens | Ownership, SLOs, deploy safety | Framework religion wars |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | API style? | REST/JSON + optional RPC | Versioned contracts |
| F2 | Data? | Service-owned store | No shared tables |
| F3 | Writes? | Idempotent + validation | Exactly-once effects via keys |
| F4 | Events? | Outbox → bus | No dual-write lies |
| F5 | Reads? | Query APIs + cache | CQRS optional |
| F6 | Auth? | IAM/JWT principal | Authz in service |
| F7 | Multi-tenant? | tenant_id everywhere | Quotas |
| F8 | Config? | Dynamic + typed | Safe defaults |
| F9 | Deploy? | Pipeline+canary | Instant rollback |
| F10 | Deps? | Timeouts/retries/circuit | Bulkheads |
| F11 | Obs? | Golden signals+traces | Bounded cardinality |
| F12 | Admin? | Break-glass audited | Least privilege |

**MVP scope:**

1. CRUD/query APIs
2. Owned DB schema
3. Idempotent writes
4. Transactional outbox
5. Cache for hot reads
6. Authn/z hooks
7. Health/ready
8. Canary deploy
9. SLOs+dashboards
10. Load-shed hooks

**Out of MVP:** Multi-region active-active same-row writes; Universal workflow engine inside every service; Shared monolith DB.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Latency | Class-based p99 targets |
| N2 | Avail | 99.9–99.99% by criticality |
| N3 | Durability | RPO≈0 for accepted writes |
| N4 | Deploy | Canary <1h to full |
| N5 | Deps | Timeout budgets |
| N6 | Tenancy | Isolation+quotas |
| N7 | Security | Least privilege |
| N8 | Cost | Unit cost dashboard |

### 1.3 Cases

**Happy:** write→durable+outbox→read-your-write; cache hit; canary ok; dependency timeout degrade.
**Edges:** dual write bug; hot partition; dependency retry storm; poison event; schema migrate fail; thundering herd cache.

| Case | Behavior |
|------|----------|
| Duplicate request | Idempotent key returns same result |
| Partial failure mid-path | Compensate or retry with fencing/CAS |
| Hot partition / noisy neighbor | Shuffle shard + fair-share quotas |
| Region / AZ loss | Cell failover; degrade non-critical |
| Clock skew | Server-side truth; opaque tokens |
| Poison input | Quarantine/DLQ; never silent drop of accepted work |
| Authz miss | Fail closed; audit |
| Traffic surge 10× | Shed by priority; preserve SLO class |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| QPS | 5K | 50K | 500K | 5M |
| Entities | 50M | 500M | 5B | 50B |
| Tenants | 100 | 1K | 10K | 100K |
| Events/day | 20M | 200M | 2B | 20B |
| Instances | 20 | 200 | 2K | 20K |
| Regions | 1 | 2 | 5 | 10+ |

**Jumps:** 10× cache+shard; 100× cells+async; 1,000× specialization+edge offload.

### 1.5 Scope repeat-back

> Service blueprint with owned data, idempotent APIs, outbox, cache, cell-ready operability and SLOs.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 QPS classes

```text
Split read/write; design for 10× write peak
```

### 2.2 Storage

```text
Row size×count + indexes + event log retention
```

### 2.3 Cache

```text
Hit ratio target 80%+ hot keys; stampede locks
```

### 2.4 Events

```text
Outbox poll/CDC throughput ≥ write QPS
```

### 2.X Bottlenecks

(1) Hot keys/partitions (2) synchronous fan-out (3) durable write path (4) auth/token validation (5) downstream blast radius (6) not abstract QPS alone.

### 2.Y Cost / frugality

Prefer cheaper read paths over linear DB growth; measure unit cost per successful customer action; sample observability firehoses.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| API | Request/response | Strong per request |
| Data | Source of truth | Strong per key/shard |
| Async | Outbox/events | At-least-once |
| Cache | Performance | Eventual |
| Control | Config/deploy | Versioned |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **API handlers** — Validate/authz
2. **Domain service** — Business rules
3. **Repository** — Data access
4. **DB** — Owned store
5. **Outbox/CDC** — Events
6. **Cache** — Hot reads
7. **Client SDKs** — Typed deps
8. **Auth filter** — Principal
9. **Quota** — Fair use
10. **Health** — Probes
11. **Admin** — Break-glass
12. **Obs agents** — Metrics/traces

### 3.3 API sketch

```text
POST /v1/{resources} Idempotency-Key
GET /v1/{resources}/{id}
PATCH /v1/{resources}/{id}
GET /v1/{resources}?cursor=
POST /v1/admin/...
```

### 3.4 State machine

```text
Resource: CREATED→ACTIVE→UPDATED→DELETED(soft/hard)
Deploy: BUILD→CANARY→PROMOTE→ROLLBACK
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Sync vs async | Sync ACK + async fanout | Customer clarity |
| Shared DB | Never | Ownership |
| Cache | Aside + TTL | Simple |
| ORM | Thin repo | Control SQL |
| Cells early | Hook points day 1 | Avoid rewrite |

---

## 4. Architecture Diagram

```text
Clients->API->Domain->DB
DB->Outbox->Bus->Consumers
API->Cache; ControlPlane->Deploy/Canary; DepClients->Bulkheads
```

### 4.1 Write

```text
Auth→validate→idempotency→txn write+outbox→ACK
```

### 4.2 Read

```text
Auth→cache→DB→fill cache
```

### 4.3 Dep call

```text
Budgeted timeout; circuit; degrade
```

### 4.N Cell / blast-radius model

```text
Each cell = failure domain (AZ-set or region slice)
No synchronous cross-cell locks on hot path
Control plane pushes config; data plane serves locally
Shuffle sharding for multi-tenant isolation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Service owns its data
2. Accepted write durable before ACK
3. Outbox coupled to write txn
4. Idempotent mutating APIs
5. Dep calls budgeted
6. Canary before 100%
7. Tenant isolation checks
8. PII classified

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular single service+PG |
| 10× | Read cache+shard keys |
| 100× | Cells+async consumers |
| 1000× | Split read models+edge |

### 5.3 Maintainability

- Contract tests
- Migration playbooks
- Load tests in CI
- Runbooks linked

### 5.4 Progressive scale narrative

**1×:** Single region
**10×:** Cache+replicas
**100×:** Cells
**1000×:** Domain split

### 5.5 Outbox

Same txn as write; publisher relays; consumers idempotent.

### 5.6 Idempotency

Persist key→response; TTL windows.

### 5.7 Hot keys

Shard/salting; cache; backpressure.

### 5.8 Schema evolve

Expand/contract; dual-read; never hard break.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| Shared tables | Coupling SEVs |
| Dual write w/o outbox | Lost events |
| Unbounded retries | Storms |
| No canary | Instant SEV |
| God service | Unownable |
| Sync fanout 20 deps | Latency death |

---

## 6. Wrap-Up

### 6.1 Designed

Scalable microservice blueprint: owned data, idempotent APIs, outbox, cache, budgets, canaries, cell hooks.

### 6.2 Decisions to defend

1. Owned datastore
2. Outbox not dual-write
3. Idempotency keys
4. Timeout budgets
5. Cache-aside
6. Canary deploys
7. Tenant_id day 1
8. SLO classes

### 6.3 Risks

- Chatty APIs
- Hot partitions
- Event backlog
- Schema debt
- Dependency coupling

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Bounded context |
| 5–15 | Data+API |
| 15–25 | Outbox+idempotency |
| 25–35 | Cache+deps |
| 35–45 | Cells+ops |

### 6.5 Closer

> **Generic Scalable Microservice**: own your data, idempotent writes, outbox events, budgeted deps, canaries, cell-ready—operable by a two-pizza team.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Bounded context?

One domain; clear APIs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Why outbox?

Avoid dual-write loss.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Idempotency window?

Keyed store + TTL.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Cache invalidation?

TTL+event; accept brief stale.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Pagination?

Cursors not deep offset.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Migrations?

Expand/contract.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Circuit breaker?

Per dependency bulkhead.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Multi-tenant?

tenant_id + quotas.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Cells?

Partition key→cell.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Read-your-write?

Sticky/session or sync path.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: PII?

Classify+encrypt+audit.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: SLOs?

Per API class.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Load shed?

Drop noncritical first.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Testing?

Contract+chaos deps.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

Shared DB or dual-write.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

$/successful mutation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

---

## 8. Appendices

### A. Glossary

| Term | Meaning |
|------|---------|
| Cell | Isolated failure domain for blast-radius control |
| Fence / fencing token | Invalidates stale writers after lease steal |
| Idempotency key | Client key making retries safe |
| Outbox | Durable event publish coupled to DB commit |
| Shuffle sharding | Map tenants to overlapping server subsets |
| SLO / error budget | Reliability contract; burn rate drives decisions |
| Unit cost | $ per successful customer action |
| DLQ | Dead-letter queue for poison / exhausted retries |
| Control vs data plane | Config/orchestration vs hot-path serving |
| Progressive scale | Explicit 10×/100×/1,000× architecture jumps |

### B. Ownership matrix

| Concern | Owns | Pages when |
|---------|------|------------|
| Hot-path latency/errors | Serving team | p99 / 5xx burn |
| Durability / data loss risk | Storage/data team | RPO/RTO alarms |
| Abuse / security | Trust & safety / AppSec | exploit or abuse spike |
| Cost regression | Serving + FinOps | unit-cost burn |
| Downstream dependency | Owning service | dependency SEV |

### C. Metrics that matter

- Success rate by criticality class
- Latency histograms (p50/p90/p99) on customer-visible path
- Queue lag / backlog age
- Retry / duplicate attempt rate
- Cache hit ratio where applicable
- Error budget burn rate
- Unit cost trend
- Cell imbalance / hot partition indicators

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope & non-goals |
| 5–12 | Back-of-envelope math |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive invariants & failures |
| 35–45 | Progressive scale, ownership, SEV |

---

## 10. Operability

### Golden signals

p99 by route, 5xx, dep errors, outbox lag, cache hit, canary burn, quota 429, unit cost

### Rollback ladder

canary revert→feature flag off→scale read replicas→shed→cell isolate

### Kill switches

disable endpoint; reject tenant; stop consumers; cache bypass/force; read-only mode

### Security / privacy

IAM; encrypt at rest; authz checks; secrets manager; PII scrubbing in logs

### Cost worksheet

DB IOPS+instances; raise cache hit; batch events; rightsize

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Platform/runtime, IAM, bus, DB platform, observability, client teams

---

## More Interview Q&A — Generic Scalable Microservice

**Q1. SQL vs Dynamo?**

**A:** Access pattern driven.

**Q2. CQRS when?**

**A:** When read models diverge.

**Q3. Sync fanout?**

**A:** Prefer events.

**Q4. Hard delete?**

**A:** Soft then GC; legal holds.

**Q5. API versioning?**

**A:** Additive first.

**Q6. GraphQL?**

**A:** BFF optional; not core.

**Q7. Sidecar mesh?**

**A:** Timeouts still yours.

**Q8. Local transactions across services?**

**A:** No; sagas/outbox.

**Q9. Load test?**

**A:** CI soak + pre-peak.

**Q10. What not?**

**A:** Shared library that owns DB schemas.

**Q11. How do you canary this?**

**A:** Percent or cell-scoped; auto-rollback on SLO burn.

**Q12. What is the SEV1 customer line?**

**A:** State impact, blast radius, mitigation, next update ETA.

**Q13. How do you test failure?**

**A:** Game day: kill AZ, dependency timeout, duplicate inject.

**Q14. What is read-your-write strategy?**

**A:** Sticky session, sync path, or version tokens as needed.

**Q15. How do you bound cardinality?**

**A:** Allowlists, quotas, deliberate metric labels.

**Q16. What is the degrade mode?**

**A:** Shed noncritical; preserve integrity/security path.

**Q17. How do you handle poison?**

**A:** Quarantine/DLQ; alert owner; capped redrive.

**Q18. What is multi-region story?**

**A:** Home cell writes; regional reads/failover documented.

**Q19. How do you prevent noisy neighbors?**

**A:** Quotas + shuffle sharding + fair queues.

**Q20. What would you not build in MVP?**

**A:** Multi-region active-active same-row writes.

---

## Worked Capacity Narrative — Generic Scalable Microservice

Separate read/write capacity. Outbox lag is a first-class capacity signal. Load-shed before cascading failure.

## Customer-Trust Paragraph — Generic Scalable Microservice

Wrong data and lost events break customers. Ownership clarity prevents SEV finger-pointing.

## Progressive Scale Recap — Generic Scalable Microservice

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Generic Scalable Microservice

### S1. Data ownership

No shared tables across services.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Idempotent writes

Keys make retries safe.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Transactional outbox

Events tied to commits.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Dependency budgets

Timeouts/retries/circuits.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Cache strategy

Aside+TTL; stampede control.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Canary deploys

Automatic rollback on burn.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Multi-tenant isolation

tenant_id+quotas.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Cell readiness

Partition blast radius.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Generic Scalable Microservice

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| DB overload | Shed reads; scale; cache | Latency | Query fix |
| Event lag | Scale publishers | Stale downstream | Backpressure |
| Bad deploy | Rollback canary | Brief errors | Test gap |
| Dep outage | Circuit; degrade | Partial | Failover |
| Hot key | Salt/split | Hotspot eased | Model fix |
| Poison event | DLQ consumer | Gap | Fix+redrive |


## Rapid-Fire Q&A — Generic Scalable Microservice

**RQ1. Why does 'Data ownership' matter in an L6 interview?**

**A:** No shared tables across services. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Data ownership' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Data ownership' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Idempotent writes' matter in an L6 interview?**

**A:** Keys make retries safe. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Idempotent writes' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Idempotent writes' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Transactional outbox' matter in an L6 interview?**

**A:** Events tied to commits. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Transactional outbox' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Transactional outbox' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Dependency budgets' matter in an L6 interview?**

**A:** Timeouts/retries/circuits. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Dependency budgets' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Dependency budgets' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Cache strategy' matter in an L6 interview?**

**A:** Aside+TTL; stampede control. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Cache strategy' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Cache strategy' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Canary deploys' matter in an L6 interview?**

**A:** Automatic rollback on burn. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Canary deploys' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Canary deploys' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Multi-tenant isolation' matter in an L6 interview?**

**A:** tenant_id+quotas. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Multi-tenant isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Multi-tenant isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Cell readiness' matter in an L6 interview?**

**A:** Partition blast radius. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Cell readiness' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Cell readiness' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Generic Scalable Microservice

### Walkthrough beat 1

POST create with Idempotency-Key; txn+outbox; 201.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

GET hits cache; miss loads DB.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Retry same key returns same body.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Consumer processes outbox idempotently.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Dep slows; circuit opens; degrade.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Canary fails SLO; auto rollback.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Tenant floods; quota 429.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× cache/shard; 100× cells; 1,000× split read models.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Generic Scalable Microservice

- [ ] Can explain **Data ownership** with numbers and a deal-breaker
- [ ] Can explain **Idempotent writes** with numbers and a deal-breaker
- [ ] Can explain **Transactional outbox** with numbers and a deal-breaker
- [ ] Can explain **Dependency budgets** with numbers and a deal-breaker
- [ ] Can explain **Cache strategy** with numbers and a deal-breaker
- [ ] Can explain **Canary deploys** with numbers and a deal-breaker
- [ ] Can explain **Multi-tenant isolation** with numbers and a deal-breaker
- [ ] Can explain **Cell readiness** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **DB overload**
- [ ] Has a 30-second runbook for **Event lag**
- [ ] Has a 30-second runbook for **Bad deploy**
- [ ] Has a 30-second runbook for **Dep outage**
- [ ] Has a 30-second runbook for **Hot key**
- [ ] Has a 30-second runbook for **Poison event**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Generic Scalable Microservice to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Generic Scalable Microservice: 1× → 10× break → 100× cells → 1,000× specialization.

### Extra drill

Name three wallboard metrics before a peak event and the action each triggers.

### Extra drill

Write the SEV1 one-liner: impact, blast radius, mitigation, next update ETA.

### Extra drill

Defend your consistency choice: what is lost if weakened, and who notices first.

### Extra drill

Cost challenge: cut 30% without violating the top SLO—what do you shed first?

### Extra drill

Security challenge: compromised credential—how do least privilege, fencing, and audit limit damage?

### Extra drill

Multi-tenant challenge: one tenant sends 100×—show fair-share math and protected queues.


*End of document — Generic Scalable Microservice (SDE III)*

