# System Design: Job Runner

> **Focus areas:** Queues · Leases/heartbeats · Retries/DLQ · Priorities · Cron/delayed · DAG · Multi-tenant fairness · Fencing
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **Job runner / distributed execution** — at-least-once work with ownership clarity

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

Goal: design an internal **job runner**: durable accept, lease to workers, heartbeat, retry, DLQ, priorities, cron/delayed, optional DAG—Amazon bar on ownership and noisy neighbors.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Leased unit of work with attempts | Interactive long HTTP request |
| Semantics | At-least-once; exactly-once effects via idempotency | Magic exactly-once |
| Amazon lens | Ownership, DLQ, fair share, peak | crontab on one host |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Who submits? | Internal multi-tenant services | tenant_id + quotas |
| F2 | Job types? | One-shot, delayed, cron, DAG steps | Job vs workflow split |
| F3 | Payload? | <256KB inline else object ref | Caps + checksum |
| F4 | Delivery? | At-least-once | Leases + idempotent workers |
| F5 | Retries? | Max attempts, backoff classes | DLQ poison |
| F6 | Leases? | Heartbeat; expiry reclaim | Fencing sacred |
| F7 | Priorities? | H/N/L + fair share | No starvation |
| F8 | Dependencies? | DAG fan-out/fan-in | Workflow SM |
| F9 | Cancel? | Pending hard; running cooperative | Cancel + lease |
| F10 | Cron? | TZ-aware catch-up policy | Jitter materialize |
| F11 | Observability? | Per-attempt timeline | Correlate ids |
| F12 | Admin? | Pause, redrive, drain | Audited control plane |

**MVP scope:**

1. Submit one-shot/delayed with idempotency key
2. Lease/heartbeat/complete with fencing
3. Retries + DLQ
4. Priorities + per-tenant limits
5. Basic cron with catch-up policy
6. Simple DAG linear + fan-in/out
7. Status/cancel/list attempts APIs + metrics

**Out of MVP:** Map-reduce shuffle; Active-active same workflow writers; User plugins in control plane.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Schedule latency | p50<1s p99<5s high-pri |
| N2 | Durability | ACK only after durable |
| N3 | Delivery | At-least-once + fencing |
| N4 | Availability | 99.9%+ control plane |
| N5 | Fairness | Noisy neighbor bounded |
| N6 | Multi-region | Home-cell single-writer |
| N7 | Clocks | Server owns lease expiry |
| N8 | Throughput | Split submit/dequeue/HB/complete QPS |

### 1.3 Cases

**Happy:** submit→lease→run→succeed; delayed/cron; DAG unlock; retry success; cancel pending.
**Edges:** worker death; GC pause steal; poison; cron herd; tenant flood; cancel/complete race.

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
| Submit QPS | 1K | 10K | 100K | 1M |
| Workers | 5K | 50K | 500K | 5M |
| Jobs/day | 50M | 500M | 5B | 50B |
| Cron schedules | 100K | 1M | 10M | 100M |
| Open workflows | 100K | 1M | 10M | 100M |
| Tenants | 100 | 1K | 10K | 100K |

**Jumps:** 10× sharded queues+fairness; 100× cells+regional workers; 1,000× hierarchical schedulers.

### 1.5 Scope repeat-back

> Multi-tenant job runner with durable accept, leased ownership, retries/DLQ, priorities, cron/DAG, fencing—scaled by shards/cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 QPS split

```text
Submit 1K/s; HB from 5K workers/5s≈1K/s; peak 5–10×
Partition for 10K submit class early
```

### 2.2 Storage

```text
Job ~1KB; 50M/day×7d hot = tens of GB meta + blob pointers
```

### 2.3 Latency

```text
Lease CAS path p99 50–200ms; HB cheaper than complete
```

### 2.4 Backlog

```text
Alert on age not only depth; shed low-pri when age SLO burns
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
| Control | Schedules, quotas, admin | Versioned config |
| Queue/lease | Ready set, HB, reclaim | Strong per shard |
| Workflow | DAG joins | Strong per home |
| Worker | Side effects | At-least-once |
| Obs | Timelines/metrics | Sampled |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Submit API** — Idempotent durable enqueue
2. **Job Store** — State/attempts/leases
3. **Ready Queues** — Priority/tenant shards
4. **Lease Manager** — CAS + fencing
5. **Cron Scheduler** — Jittered materialization
6. **Workflow Engine** — Unlock children
7. **Workers** — Pull/execute/complete
8. **DLQ** — Poison + redrive
9. **Quota Service** — Fair share
10. **Admin** — Pause/drain/replay
11. **Outbox** — Status stream
12. **Timeline** — Attempt history

### 3.3 API sketch

```text
POST /v1/jobs {tenant_id,type,payload_ref,run_at,priority,idempotency_key}
GET /v1/jobs/{id}
POST /v1/jobs/{id}/cancel
POST /v1/workers/lease|heartbeat|complete
POST /v1/dlq/{id}/redrive
```

### 3.4 State machine

```text
PENDING→READY→RUNNING→SUCCEEDED|CANCELLED
FAIL_RETRY→READY (backoff)→DLQ
Workflow BLOCKED→READY on parents
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Pull vs push | Pull/lease | Natural backpressure |
| Exactly-once | At-least-once+idempotency | Honest under failure |
| Cron catch-up | Skip missed default | Avoid herds |
| DAG scope | Simple graphs only | Defer BPM |
| Queue tech | Owned partitioned store | Operational clarity |

---

## 4. Architecture Diagram

```text
Client->Submit->JobStore->ReadyQueues->LeaseManager->Workers
Cron->Submit; Workflow<->JobStore; DLQ<-max attempts; Outbox->Obs
```

### 4.1 Lease

```text
Pick READY by pri+fairness; CAS+fencing; HB; complete or 409 stale
```

### 4.2 Retry

```text
attempt++; backoff READY; >max → DLQ
```

### 4.3 DAG

```text
Parent terminal unlocks children; join timeout policy
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

1. Durable before ACK
2. Valid fencing required to complete
3. Lease expiry requeues
4. Max attempts → DLQ
5. CAS terminals for cancel/complete
6. Quotas on submit+dequeue
7. Admin audited
8. Workflow from durable terminals only

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single region DB queues |
| 10× | Shard + fair share + DLQ playbooks |
| 100× | Cells + regional workers |
| 1000× | Hierarchical schedulers + chaos |

### 5.3 Maintainability

- Job type registry as data
- Canary per shard
- DLQ replay tools
- Workflow fixtures

### 5.4 Progressive scale narrative

**1×:** Monolith + simple cron + linear DAG
**10×:** Partitions + quotas
**100×:** Cells + DR
**1000×:** Specialized pools

### 5.5 Fencing

Token per lease; reclaim bumps token; stale complete rejected.

### 5.6 Fairness

Shuffle shard tenants; WFQ; priority ≠ infinite capacity.

### 5.7 Cron storms

Jitter next_run_at; shard scanners; explicit catch-up.

### 5.8 Effects

attempt_id + idempotency_key for worker-side dedupe.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| No fencing | Double side effects |
| ACK before durable | Lost jobs |
| Global lock queue | Peak meltdown |
| Priority w/o fairness | Noisy neighbor |
| Infinite retries | Poison melts fleet |
| Worker clock leases | Split brain |

---

## 6. Wrap-Up

### 6.1 Designed

Durable multi-tenant job runner with leases/fencing, retries/DLQ, priorities, cron, simple DAG, cells.

### 6.2 Decisions to defend

1. At-least-once+fencing
2. Pull leases
3. Plane split
4. Fair shuffle shard
5. DLQ redrive
6. Home-cell writer
7. Cron jitter
8. Idempotent submit

### 6.3 Risks

- HB storms
- Hot tenants
- Join storms
- Lease bugs
- DLQ neglect

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Semantics |
| 5–15 | Lease+fencing |
| 15–25 | Fair queues |
| 25–35 | DLQ/cron/DAG |
| 35–45 | Cells+ownership |

### 6.5 Closer

> **Job Runner**: durable accept, fenced leases, fair queues, retries/DLQ, cron/DAG, cells—never silent loss of accepted work.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: At-least-once vs exactly-once

Promise at-least-once; effects via idempotency+fencing.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Fencing tokens

Stop stale completes after reclaim.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Pull vs push

Pull for backpressure.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Fairness

Quotas+shuffle+WFQ.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Cron herd

Jitter+shard scanners.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Poison jobs

DLQ+alert+capped redrive.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: DAG joins

Timeout/cancel policy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Cancel races

CAS terminal.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Multi-region

Home-cell single-writer.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Heartbeat tuning

Fraction of lease; tolerate GC.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Payload size

Inline small; object large.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Pager ownership

Job-type owner vs platform.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Idempotent submit

Same key→same job_id.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Starvation

Aging/reserved low-pri capacity.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Mid-effect crash

Idempotent workers.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Deal-breaker

ACK-before-durable or no fencing.

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

submit success, lease latency, HB fail, backlog age, DLQ rate, stale complete rejects, throttle counts, $/job

### Rollback ladder

disable types → pause low-pri → revert scheduler → isolate cell → careful redrive

### Kill switches

pause tenant/type; stop cron; shed low-pri; emergency cancel filter

### Security / privacy

IAM; encrypt payloads; tenant checks; audit admin; SSRF allowlists

### Cost worksheet

Worker compute + store IOPS dominate; coalesce jobs; short success retention; sample traces

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

IAM, object store, metrics, capacity, job-type owners

---

## More Interview Q&A — Job Runner

**Q1. SQS enough?**

**A:** MVP often yes; custom DAG/fairness may need job store.

**Q2. Lease length?**

**A:** p99 runtime + margin.

**Q3. Exactly-once myth?**

**A:** Design for duplicates.

**Q4. Sticky workers?**

**A:** Optional; reclaim still works.

**Q5. Batch dequeue?**

**A:** Yes with max in-flight.

**Q6. GPU pools?**

**A:** Capability matching.

**Q7. Spot interrupt?**

**A:** Reclaim + checkpoint optional.

**Q8. Cardinality?**

**A:** Metric on job_type not job_id.

**Q9. Rate limit submit?**

**A:** 429 + retry-after.

**Q10. What not to build?**

**A:** Full BPM UI in MVP.

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

**A:** Map-reduce shuffle.

---

## Worked Capacity Narrative — Job Runner

Split QPS into submit/dequeue/HB/complete. Size shards so one tenant cannot pin all. Backlog age by priority is capacity truth.

## Customer-Trust Paragraph — Job Runner

Lost jobs and duplicate side effects destroy trust. Fencing + durable ACK are customer-obsession features.

## Progressive Scale Recap — Job Runner

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Job Runner

### S1. Lease & fencing

CAS lease + fencing; stale completes rejected.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Durable submit

Commit before ACK.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Retry & DLQ

Bounded attempts + quarantine.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Fair queues

Quotas + shuffle sharding + WFQ.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Cron materialization

Jittered next_run; catch-up policy.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. DAG orchestration

Durable terminals unlock children.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Worker failure

HB miss reclaim; idempotent effects.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Progressive cells

Home-cell writer; scale by cells.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Job Runner

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Lease reclaim storm | Raise TTL; scale managers | Delay | Fix HB |
| DLQ explosion | Pause type; patch | Degrade | Redrive cap |
| Hot tenant | Tighten quota | Others safe | Outreach |
| Cron herd | Disable; respread | Spike cleared | Jitter default |
| Control plane down | Data plane continues | No new submits | Fail over |
| Duplicate effects | Stop type; reconcile | Trust risk | Audit idempotency |


## Rapid-Fire Q&A — Job Runner

**RQ1. Why does 'Lease & fencing' matter in an L6 interview?**

**A:** CAS lease + fencing; stale completes rejected. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Lease & fencing' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Lease & fencing' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Durable submit' matter in an L6 interview?**

**A:** Commit before ACK. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Durable submit' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Durable submit' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Retry & DLQ' matter in an L6 interview?**

**A:** Bounded attempts + quarantine. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Retry & DLQ' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Retry & DLQ' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Fair queues' matter in an L6 interview?**

**A:** Quotas + shuffle sharding + WFQ. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Fair queues' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Fair queues' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Cron materialization' matter in an L6 interview?**

**A:** Jittered next_run; catch-up policy. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Cron materialization' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Cron materialization' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'DAG orchestration' matter in an L6 interview?**

**A:** Durable terminals unlock children. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'DAG orchestration' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'DAG orchestration' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Worker failure' matter in an L6 interview?**

**A:** HB miss reclaim; idempotent effects. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Worker failure' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Worker failure' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Progressive cells' matter in an L6 interview?**

**A:** Home-cell writer; scale by cells. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Progressive cells' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Progressive cells' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Job Runner

### Walkthrough beat 1

Submit with idempotency_key; durable PENDING; return job_id.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Worker leases with fencing_token; heartbeats.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Worker dies; reclaim; late complete 409.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Retryable fail→backoff→success; timeline shows attempts.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Poison→DLQ; owning team alerted.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Cron jitters enqueue; skip-if-running policy.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

DAG A→(B,C)→D succeeds.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× shard+fair; 100× cells; 1,000× specialized pools.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Job Runner

- [ ] Can explain **Lease & fencing** with numbers and a deal-breaker
- [ ] Can explain **Durable submit** with numbers and a deal-breaker
- [ ] Can explain **Retry & DLQ** with numbers and a deal-breaker
- [ ] Can explain **Fair queues** with numbers and a deal-breaker
- [ ] Can explain **Cron materialization** with numbers and a deal-breaker
- [ ] Can explain **DAG orchestration** with numbers and a deal-breaker
- [ ] Can explain **Worker failure** with numbers and a deal-breaker
- [ ] Can explain **Progressive cells** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Lease reclaim storm**
- [ ] Has a 30-second runbook for **DLQ explosion**
- [ ] Has a 30-second runbook for **Hot tenant**
- [ ] Has a 30-second runbook for **Cron herd**
- [ ] Has a 30-second runbook for **Control plane down**
- [ ] Has a 30-second runbook for **Duplicate effects**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Job Runner to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Job Runner: 1× → 10× break → 100× cells → 1,000× specialization.

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


*End of document — Job Runner (SDE III)*

