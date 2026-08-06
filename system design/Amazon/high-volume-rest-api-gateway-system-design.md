# System Design: High-Volume REST API Gateway

> **Focus areas:** AuthN/Z · Rate limiting · Routing · Timeouts/retries · Caching · WAF · Quotas · Cell routing · Observability
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **High-volume REST API gateway** — public edge protecting origins

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

Goal: design a **high-volume REST API gateway** for auth, quotas, routing, safe retries, WAF, canaries, and cell-aware origin protection at Amazon scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | L7 edge policy + protection | All business logic |
| Scale | Fan-in millions RPS | Replace every mesh hop |
| Amazon lens | Noisy neighbor, abuse, edge SEVs | One NGINX |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Protocols? | HTTPS REST; optional gRPC up | TLS terminate |
| F2 | Auth? | JWT/API keys/IAM | Pluggable |
| F3 | Authz? | Route/tenant policies | Fail closed |
| F4 | Rate limit? | Key/tenant/IP burst | Distributed |
| F5 | Routing? | Path/host→service/cell | Config-driven |
| F6 | Caching? | Safe GET only | Auth-aware keys |
| F7 | Timeouts? | Per-route deadlines | Propagate cancel |
| F8 | Retries? | Idempotent + budgeted | Stop storms |
| F9 | WAF? | Schema/bot/body caps | Edge shed |
| F10 | Canary? | %/header/cell | Instant rollback |
| F11 | Quotas? | Soft/hard 429 | Product-facing |
| F12 | Obs? | Edge metrics+trace | Cardinality caps |

**MVP scope:**

1. TLS+validation
2. AuthN/Z
3. Per-tenant RL+429
4. Path routing
5. Timeouts+GET retries
6. Logs+golden signals
7. Canary config
8. WAF+body caps

**Out of MVP:** GraphQL federation; Global sticky all POSTs; Arbitrary edge scripting.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Edge add latency | p99 5–15ms excl upstream |
| N2 | Avail | 99.99% with shed |
| N3 | RL correctness | No shard shopping |
| N4 | Config rollback | <1 min |
| N5 | Security | Fail-closed |
| N6 | Multi-region | Regional edges |
| N7 | Cardinality | Bounded metrics |
| N8 | Throughput | 100K→100M RPS |

### 1.3 Cases

**Happy:** auth→quota→route→upstream; cache GET; canary; 429 retry-after.
**Edges:** key leak flood; hot tenant; brownout; retry storm; bad config; cache poison; smuggling.

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
| Edge RPS | 100K | 1M | 10M | 100M |
| Routes | 1K | 10K | 100K | 1M |
| Tenants/keys | 10K | 100K | 1M | 10M |
| Upstreams | 50 | 500 | 5K | 50K |
| Regions | 3 | 8 | 20 | 50+ |
| Config/day | 50 | 200 | 1K | 5K |

**Jumps:** 10× hybrid RL+cache; 100× PoPs+cells; 1,000× specialized edge+hierarchical quotas.

### 1.5 Scope repeat-back

> Regional high-volume REST gateway with auth, quotas, safe retries, WAF, canaries, cell routing.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 RPS

```text
100K×2KB≈1.6Gbps; nodes ~50–100K RPS class
```

### 2.2 RL store

```text
Updates≈RPS; local+global hybrid
```

### 2.3 Latency

```text
auth+RL+route few ms; upstream dominates
```

### 2.4 Logs

```text
sample; full only errors/canary
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
| Data | Per-request | Mostly stateless |
| Control | Routes/policies | Versioned |
| Quota | Distributed limits | Eventual budgets |
| Security | WAF/authz | Fail closed |
| Obs | Metrics/logs | Sampled |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Edge proxy** — Hot path
2. **Auth** — JWT/keys
3. **Quota** — Token buckets
4. **Route store** — xDS-like
5. **Discovery** — Upstreams/cells
6. **Cache** — Auth-aware GET
7. **WAF** — Abuse
8. **Canary ctrl** — Splits
9. **Key mgmt** — Rotation
10. **Log pipeline** — Sampled
11. **Outlier** — Eject bad
12. **Admin API** — Audited

### 3.3 API sketch

```text
PUT /v1/routes/{id}
PUT /v1/quotas/{tenant}
POST /v1/canaries
ANY https://api.example/{path}
```

### 3.4 State machine

```text
RECEIVED→AUTH→AUTHZ→QUOTA→ROUTE→UPSTREAM→RESPOND
Config DRAFT→CANARY→ACTIVE→ROLLBACK
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Gateway vs mesh | Edge+light mesh | Clear ownership |
| Global RL | Local+global | Avoid one Redis |
| Retry | Budgeted GET | Stop storms |
| Cache | Opt-in | Authz safety |
| Config | Streaming xDS | Fast rollback |

---

## 4. Architecture Diagram

```text
Clients->PoP Gateway->Auth->Quota->Router->Upstream cells
WAF->Gateway; ControlPlane=>fleet; QuotaStore<->shards
```

### 4.1 Request

```text
TLS→WAF→Auth→Quota→Upstream+deadline→filters
```

### 4.2 429

```text
Deny before origin; Retry-After
```

### 4.3 Canary

```text
Burn→percent=0→LKG
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

1. No unauth to protected up
2. No RL bypass via shards
3. Monotonic config+LKG
4. Retries within deadline
5. No secrets in logs
6. Canary auto-stop
7. Body caps
8. Bounded metric labels

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Regional fleet+Redis RL |
| 10× | Hybrid RL+cache+outlier |
| 100× | PoPs+cells+shuffle |
| 1000× | Specialized edge+HW TLS |

### 5.3 Maintainability

- Route-as-code
- Shadow policies
- Mandatory canary
- Schema contracts

### 5.4 Progressive scale narrative

**1×:** JWT+API keys
**10×:** Hybrid RL
**100×:** Global PoPs
**1000×:** Policy compilers

### 5.5 Distributed RL

Local buckets + global reconcile; hash keys; soft vs hard.

### 5.6 Retry budgets

Deadline; idempotent only; max 1–2.

### 5.7 Auth cache

Short TTL; revocation list.

### 5.8 Cache safety

Never cache private; normalize headers.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| POST retries w/o idempotency | Dup orders |
| One global Redis RL | Meltdown |
| Cache private | Leak SEV |
| Config w/o canary | Global SEV |
| Fail-open authz | Breach |
| Unbounded bodies | OOM |

---

## 6. Wrap-Up

### 6.1 Designed

High-volume REST edge: authn/z, hierarchical quotas, safe retries, WAF, canary config, cell routing.

### 6.2 Decisions to defend

1. Hybrid RL
2. Budgeted retries
3. Canary+LKG
4. Auth-aware cache
5. Cell routing
6. Fail-closed
7. Sampled logs
8. Outlier eject

### 6.3 Risks

- Retry storms
- Key leaks
- Config SEVs
- Hot tenants
- Cardinality

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope |
| 5–15 | Auth+quota |
| 15–25 | Route/timeouts |
| 25–35 | WAF/cache/canary |
| 35–45 | PoP/cells |

### 6.5 Closer

> **High-Volume REST API Gateway**: edge protecting origins with auth, fair quotas, safe retries, canaries, cells.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Business logic location

Upstreams; gateway is policy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: RL at 1M RPS

Local+global; shard by key.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Retry storms

Deadlines+idempotent caps.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: JWT vs SigV4

External JWT/keys; internal SigV4 optional.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Cache safety

Explicit public GET only.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Bad canary

Auto 0% + LKG.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Smuggling

Normalize/reject ambiguous.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Sticky POST

Avoid; use idempotency.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: 429 ownership

Infra vs tenant abuse.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: gRPC

Transcode or separate.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Body limits

Per route class.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: mTLS upstream

Yes in VPC.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: IP allowlists

Optional enterprise.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: GraphQL

Usually separate.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker

Fail-open or unbudgeted retries.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost

$/MReq + egress + WAF.

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

RPS, edge p99 add, 4xx/5xx, 429, upstream p99, canary burn, RL bypass, $/MReq

### Rollback ladder

canary 0→revert routes→disable cache→shed→block keys

### Kill switches

disable route; global throttle; deny tenant; disable retries; WAF lockdown

### Security / privacy

TLS; fail-closed; redact secrets; rotate keys; block SSRF/metadata

### Cost worksheet

Edge compute+egress; raise cache hit; sample logs; shed bots early

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Identity, service owners, WAF, DNS/PoP, capacity, SDKs

---

## More Interview Q&A — High-Volume REST API Gateway

**Q1. Envoy vs custom?**

**A:** Mature data plane; own control policies.

**Q2. 429 vs 503?**

**A:** 429 quota; 503 capacity.

**Q3. Idempotency-Key?**

**A:** Pass through.

**Q4. Websockets?**

**A:** Often separate gateway.

**Q5. Bot management?**

**A:** Reputation/challenges.

**Q6. Shadow traffic?**

**A:** Replay to canary.

**Q7. Per-IP limits?**

**A:** Yes; careful with NAT.

**Q8. HTTP/3?**

**A:** PoP feature over time.

**Q9. Config blast?**

**A:** Cell-scoped pushes.

**Q10. What not?**

**A:** Lua free-for-all on edge.

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

**A:** GraphQL federation.

---

## Worked Capacity Narrative — High-Volume REST API Gateway

Size by peak RPS/node. Auth/RL memory first-class. Shed at edge before origins melt.

## Customer-Trust Paragraph — High-Volume REST API Gateway

Gateway bugs are company-wide SEVs: leaks, auth bypass, duplicate POSTs.

## Progressive Scale Recap — High-Volume REST API Gateway

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — High-Volume REST API Gateway

### S1. Fail-closed authz

No protected upstream without principal+policy.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Hierarchical RL

Local+global; no shard shopping.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Deadline retries

Safe methods only.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Auth-aware cache

Never cache private accidentally.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Canary config

Auto rollback on burn.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Origin protection

Timeouts, eject, caps, WAF.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Cell routing

Limit blast radius.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Cardinality control

Bounded labels; sample logs.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — High-Volume REST API Gateway

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Origin brownout | Tighten; eject; cache | Degrade | Scale origin |
| 429 storm | Find bad client | Throttled | Quota review |
| Auth outage | Fail closed | Hard down | Failover cache |
| Bad config | Rollback LKG | Brief errors | Tighten canary |
| Key leak | Revoke+WAF | Abuse stopped | Rotation |
| Cache leak | Disable+purge | Trust risk | Audit Vary |


## Rapid-Fire Q&A — High-Volume REST API Gateway

**RQ1. Why does 'Fail-closed authz' matter in an L6 interview?**

**A:** No protected upstream without principal+policy. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Fail-closed authz' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Fail-closed authz' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Hierarchical RL' matter in an L6 interview?**

**A:** Local+global; no shard shopping. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Hierarchical RL' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Hierarchical RL' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Deadline retries' matter in an L6 interview?**

**A:** Safe methods only. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Deadline retries' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Deadline retries' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Auth-aware cache' matter in an L6 interview?**

**A:** Never cache private accidentally. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Auth-aware cache' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Auth-aware cache' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Canary config' matter in an L6 interview?**

**A:** Auto rollback on burn. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Canary config' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Canary config' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Origin protection' matter in an L6 interview?**

**A:** Timeouts, eject, caps, WAF. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Origin protection' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Origin protection' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Cell routing' matter in an L6 interview?**

**A:** Limit blast radius. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Cell routing' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Cell routing' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Cardinality control' matter in an L6 interview?**

**A:** Bounded labels; sample logs. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Cardinality control' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Cardinality control' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — High-Volume REST API Gateway

### Walkthrough beat 1

GET with API key; quota; cell route; edge add ~8ms.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Hot tenant 429; origins protected.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

POST not retried by gateway; idempotency passed through.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Canary burns; auto revert LKG.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

WAF blocks giant invalid body.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Outlier ejects bad AZ.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Public GET cached safely.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× RL/cache; 100× PoP/cells; 1,000× specialized edge.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — High-Volume REST API Gateway

- [ ] Can explain **Fail-closed authz** with numbers and a deal-breaker
- [ ] Can explain **Hierarchical RL** with numbers and a deal-breaker
- [ ] Can explain **Deadline retries** with numbers and a deal-breaker
- [ ] Can explain **Auth-aware cache** with numbers and a deal-breaker
- [ ] Can explain **Canary config** with numbers and a deal-breaker
- [ ] Can explain **Origin protection** with numbers and a deal-breaker
- [ ] Can explain **Cell routing** with numbers and a deal-breaker
- [ ] Can explain **Cardinality control** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Origin brownout**
- [ ] Has a 30-second runbook for **429 storm**
- [ ] Has a 30-second runbook for **Auth outage**
- [ ] Has a 30-second runbook for **Bad config**
- [ ] Has a 30-second runbook for **Key leak**
- [ ] Has a 30-second runbook for **Cache leak**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining High-Volume REST API Gateway to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for High-Volume REST API Gateway: 1× → 10× break → 100× cells → 1,000× specialization.

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


*End of document — High-Volume REST API Gateway (SDE III)*

