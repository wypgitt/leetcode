# System Design: Rate Limiter / Expiry Throttling (Amazon Platform)

> **Focus areas:** Token bucket · Sliding window · Hierarchical quotas · Reserve+settle · Hot keys · Fail-closed/static · Expiry leases · Regional+global slices · Shadow policy
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic; split check vs settle QPS; explicit overshoot ε; ownership of allow/deny
> **Interview theme:** Amazon SDE III / L6 — shared **Rate Limiter / expiry throttling** platform for retail APIs, seller APIs, and internal services

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

Goal: A **shared throttling platform** that enforces hierarchical RPM/TPM/concurrency (and expiry-based leases) with low-latency decisions, bounded overshoot under partitions, and explicit fail modes—used by Amazon.com APIs, Marketplace seller APIs, and internal microservices.

### 1.0 What this is / is not
| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Allow/deny + remaining + Retry-After | Full API Gateway product |
| State | Counters/buckets/leases | Business entity DB |
| Billing | Usage events out | Invoice ledger |
| Amazon lens | Customer experience under throttle, abuse cost, Prime Day | Academic fairness alone |

### 1.1 Functional requirements
| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Who limited? | Account, seller, API key, IP, ASIN (flash) | Composite hierarchical keys |
| F2 | Dimensions? | RPM, burst, concurrency, daily quota, TPM-like cost units | Separate algorithms |
| F3 | Hard vs soft? | Hard 429; soft headers/warn optional | Stable decision API |
| F4 | Unknown cost? | Reserve → settle | Debt + TTL reclaim |
| F5 | Expiry throttling? | Time-boxed boosts, bans, flash windows | Lease/TTL first-class |
| F6 | Fairness? | No single seller starves marketplace APIs | Weighted shares under overload |
| F7 | Regional/global? | Regional enforce; global contract caps | Slices + ε |
| F8 | Admin? | Boosts, bans, shadow | Versioned policy |
| F9 | Observability? | Deny reasons, hot keys, check latency | Careful cardinality |
| F10 | SDK contract? | 429 + Retry-After + remaining | Idempotent request_id |

**MVP:** check/reserve, settle, hierarchy, Redis Lua, policy control plane, fail-closed/static, hot-key playbook, metrics.
**Out:** Perfect global linearizability; auction GPU scheduling; replacing WAF.

### 1.2 NFRs
| # | Target |
|---|--------|
| N1 | check p99 < 5–10ms in-region |
| N2 | Overshoot ≤ ε (e.g. 5–15%) under partition |
| N3 | 99.99% decision availability with documented degrade |
| N4 | Never unbounded fail-open |
| N5 | Policy propagation seconds |

### 1.3 Cases
Happy: allow within bucket; burst then 429; settle releases; boost overlay; hierarchical deny.
Edges: Redis partition; hot seller; duplicate settle; lease expiry mid-flight; bad policy canary; clock skew; Prime Day.

### 1.4 Progressive scale
| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Check QPS | 100K | 1M | 10M | 100M |
| Settle QPS | 80K | 800K | 8M | 80M |
| Distinct keys/min | 50K | 200K | 1M | 5M+ |
| Regions | 3 | 4 | 6 | 10+ |

Jumps: Redis Cluster → hybrid local+regional → cell fleets + approx global.

### 1.5 Scope repeat-back
> Shared Amazon rate-limiter/expiry-throttling service: hierarchical RPM/concurrency/cost units, reserve+settle+TTL, regional enforcement with global slices, explicit fail-static ceilings, hot-key isolation—scaling checks from ~100K/s to ~100M/s.

---
## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes
| Class | Base | 1,000× | Notes |
|-------|------|--------|-------|
| Check/reserve | 100K/s | 100M/s | Sync, latency-critical |
| Settle/release | 80K/s | 80M/s | Slightly async OK |
| Lease renew | 20K/s | 20M/s | Long holds |
| Policy watch | low | low | Pub/sub |
| Global sync | 2–10K/s | 0.2–2M/s | Batched |

### 2.2 Redis math
```text
100K checks × 1 Lua RTT ≈ 100K rps cluster-wide (comfortable with shards)
100M checks → must hybrid local approximation + many cells
Ops/check goal: 1 RTT (pipeline/Lua), not 6 round-trips
```

### 2.3 Latency budget
Edge 1–2ms; identity cache 0.5ms; Lua 1–3ms; header build <1ms → **p99 ≤ 10ms**.

### 2.4 Cost
Dominant: Redis memory + CPU for hot keys. +10% local allow cache hit ≫ doubling cluster size. Track `$ / M checks`.

---
## 3. High-Level Design

**Components:** Edge/WAF, API Gateway, Rate Limit Service, Redis Cluster, Policy Control Plane, Usage Events bus, Global Slice Coordinator, Hot-Key Cell Router, Admin/Config UI, Observability.

**APIs:**
```text
POST /v1/check  {key, dims, cost_est, request_id} → allow|deny + remaining + reset + policy_version
POST /v1/settle {request_id, actual_cost}
POST /v1/heartbeat {lease_id}  # concurrency
```

**Algorithms:**
```text
token_bucket: tokens = min(cap, tokens + refill*(now-ts)); allow if tokens>=need
concurrency: incr if < max; lease TTL
hierarchy: allow iff all ancestors allow; remaining = min(dims)
```

**Tradeoffs:** accuracy vs latency (slices); fail-static vs availability; local approx vs fairness; limiter ≠ billing.

---
## 4. Architecture Diagram

```text
 Client / SDK
     |
     v
 Edge (volumetric) --> API Gateway --> Rate Limit Service
                              |              |
                              |              +--> Redis Cluster (Lua buckets/leases)
                              |              +--> Local approx cache (slice debit)
                              |              +--> Hot-Key Cells
                              v
                         Downstream services
                              |
                         Usage Events --> Billing / Analytics
 Policy Control Plane --> pub/sub --> Limiters (policy_version)
 Global Coordinator <--> regional slice deltas (async)
```

Degrade path: Redis errors → fail-static ceiling (auth) or fail-closed (anon) → shed noncritical classes → cell isolate.

---
## 5. Design Deep Dive

### 5.1 Reliability (R)
Invariants: idempotent check/settle by request_id; lease TTL reclaim; policy_version monotonic; no unbounded fail-open; deny never needs cross-region RTT; overshoot ≤ ε.
Sweeper repairs expired leases; property tests for negative concurrency.

### 5.2 Scalability (S)
| Scale | Architecture |
|-------|--------------|
| 1× | Regional RL + Redis Lua |
| 10× | Cluster, pipeline, identity cache, deny short-circuit |
| 100× | Hybrid local buckets + regional slices + Kafka settles |
| 1,000× | Many cells, approx global, edge RPM, ASIN hot cells |

### 5.3 Maintainability (M)
Shadow policies; canary cells; load-test hot keys; metrics without high-cardinality labels; runbooks for partition and zero-limit bugs; SDK contract versioning.

### 5.4 Expiry throttling deep dive
Boosts/bans/flash windows are TTL keys. Flash ASIN caps: short TTL buckets recreated each window; pre-warm before deal start; avoid thundering herd with jittered client retries.

### 5.5 Consistency honesty
Per-key regional ≈ sequential via Lua. Global eventual with ε. Clients may see dashboard ≠ live remaining.

---
## 6. Wrap-Up

### 6.1 What we designed
Amazon-grade rate limiter/expiry throttler with hierarchy, reserve+settle, Redis→hybrid→cells progressive scale, fail-static ceilings, hot-key isolation.

### 6.2 Key decisions worth defending
1. Split dimensions (RPM/concurrency/cost)
2. Reserve+settle+TTL
3. No global RTT on hot path
4. Fail-closed/static never unbounded open
5. Hot keys first-class
6. Limiter ≠ billing
7. Shadow/canary policy_version
8. 1000× forces hybrid, not bigger Redis alone

### 6.3 Risks & follow-ups
Chronic underestimate; Redis hot shard; coordinator lag; fail-static abuse; settle lag.

### 6.4 Closer
> **Rate Limiter / Expiry Throttling**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Rate Limiter

**Q1. Token bucket or sliding window?**

**A:** Bucket for burst + refill on Amazon storefront APIs; sliding/log window when precise fairness matters (e.g., expensive report generation). Defend hybrid.

**Q2. Where does the limiter sit?**

**A:** Beside API Gateway / service mesh admit—before expensive business logic and datastore fanout.

**Q3. How do you handle unknown cost ops?**

**A:** Reserve estimate → settle actual; debt on next requests; optional cancel if debt exceeds hard threshold.

**Q4. Fail open or closed?**

**A:** Default fail-closed for anonymous/abuse; authenticated critical paths may fail-static with hard ceiling. Never unbounded open.

**Q5. How is hierarchy enforced?**

**A:** Check child then parent remaining; atomic multi-key Lua or ordered locks; deny cites tightest key.

**Q6. Clock skew?**

**A:** Use Redis TIME / server epoch; ignore client clocks for window math.

**Q7. Hot celebrity key?**

**A:** Dedicated shard/cell, local token cache with sync, request coalescing, coarser buckets.

**Q8. Idempotent retries?**

**A:** request_id reservation; replay returns same decision within TTL.

**Q9. Multi-region truth?**

**A:** Regional hard enforcement + global soft/hard slices with bounded overshoot; not linearizable worldwide.

**Q10. Headers contract?**

**A:** HTTP 429, Retry-After, X-RateLimit-Limit/Remaining/Reset, policy_version.

**Q11. Shadow mode?**

**A:** Dual-run decide without enforce; compare; promote.

**Q12. Limiter vs billing?**

**A:** Separate SoT; share append-only usage events; billing reconciliation sweeper.

**Q13. Local in-process limits enough?**

**A:** Only as first line; need shared store for multi-host fairness.

**Q14. Lua vs app CAS?**

**A:** Lua/single RTT preferred for atomic multi-counter updates.

**Q15. What is the deal-breaker?**

**A:** Single global Redis key for all traffic, or silent fail-open with no ceiling.

**Q16. Prime Day plan?**

**A:** Pre-split hot keys, raise cache TTLs on config, preload policies, load-test celebrity sellers.

**Q17. Observability cardinality?**

**A:** No org_id on Prometheus; use exemplars and sampled logs.

**Q18. Thundering herd after outage?**

**A:** Jittered Retry-After; client SDKs; token recovery rate limits.

**Q19. Who pages on deny spike?**

**A:** If config change: Policy owner. If Redis/latency: Limiter Platform.

**Q20. How to test overshoot bound?**

**A:** Chaos partition global coordinator; measure regional admit vs ε.


---
## 8. Appendices

### A — Glossary
| Term | Meaning |
|------|---------|
| Slice | Regional share of a global cap |
| ε / overshoot | Bound on admit beyond global truth under partition |
| Fail-static | Admit using hard-coded ceiling without Redis |
| Lease | TTL'd concurrency/reservation record |
| Policy_version | Monotonic config stamp on decisions |
| Cell | Failure-isolated limiter fleet |
| Deal-breaker | Unbounded fail-open or single global counter |
| Two-pizza | Ownership team with pager |

### B — Oncall checklist
- [ ] check_p99 / deny_ratio dashboards green
- [ ] Last-known-good policy armed
- [ ] Fail-static ceilings documented per class
- [ ] Hot-key cells pre-provisioned for events
- [ ] Global coordinator lag SLO

### C — Redis key schema
```text
rl:{key}:rpm -> token bucket hash
rl:{key}:conc -> int + lease set
rl:{key}:ban -> TTL flag
rl:req:{request_id} -> reservation
rl:policy:{id} -> versioned blob ref
```

### D — Scale checklist
10× cluster; 100× hybrid; 1,000× cells+approx; always measure ops/check.

### E — Estimation cheat-sheet
```text
redis_ops ≈ check_qps × rtt_ops_per_check
cells ≈ peak_check_qps / per_cell_budget
```

### F — Topic closer checklist
- [ ] Hierarchy + deny reason
- [ ] Reserve/settle/TTL
- [ ] Fail mode explicit
- [ ] Hot-key story
- [ ] Progressive scale

## Deep Technical Notes — Rate Limiter

### Lua atomicity
Single SCRIPT for refill+debit+concurrency. Return structured allow/deny. Avoid multi-RTT WATCH storms.

### Slice accounting
Coordinator assigns slice_i; limiter refuses when local_debit ≥ slice + burst_credit; gossip adjustments; emergency freeze.

### SDK contract
Idempotency keys mandatory for mutating APIs; Retry-After jitter; distinguish 429 vs 503.

### Flash-deal ASIN limits
Pre-create keys; pin; separate class from user RPM; coordinate with inventory service—not a substitute for stock.

### Property tests
Never negative conc; settle ≤ 1 effect; hierarchy remaining = min; ban short-circuit; TTL reclaim within T+δ.

### Multi-tenant marketplace
Seller APIs: fairness so mega-sellers cannot starve SMBs under shared backend capacity—weighted shares.

## Interview Cards — Rate Limiter

### Card 1: Token bucket or sliding window?

Bucket for burst + refill on Amazon storefront APIs; sliding/log window when precise fairness matters (e.g., expensive report generation). Defend hybrid.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Where does the limiter sit?

Beside API Gateway / service mesh admit—before expensive business logic and datastore fanout.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: How do you handle unknown cost ops?

Reserve estimate → settle actual; debt on next requests; optional cancel if debt exceeds hard threshold.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Fail open or closed?

Default fail-closed for anonymous/abuse; authenticated critical paths may fail-static with hard ceiling. Never unbounded open.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: How is hierarchy enforced?

Check child then parent remaining; atomic multi-key Lua or ordered locks; deny cites tightest key.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Clock skew?

Use Redis TIME / server epoch; ignore client clocks for window math.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Hot celebrity key?

Dedicated shard/cell, local token cache with sync, request coalescing, coarser buckets.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Idempotent retries?

request_id reservation; replay returns same decision within TTL.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Multi-region truth?

Regional hard enforcement + global soft/hard slices with bounded overshoot; not linearizable worldwide.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Headers contract?

HTTP 429, Retry-After, X-RateLimit-Limit/Remaining/Reset, policy_version.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Shadow mode?

Dual-run decide without enforce; compare; promote.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Limiter vs billing?

Separate SoT; share append-only usage events; billing reconciliation sweeper.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Local in-process limits enough?

Only as first line; need shared store for multi-host fairness.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Lua vs app CAS?

Lua/single RTT preferred for atomic multi-counter updates.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: What is the deal-breaker?

Single global Redis key for all traffic, or silent fail-open with no ceiling.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Prime Day plan?

Pre-split hot keys, raise cache TTLs on config, preload policies, load-test celebrity sellers.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.


## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + Amazon ownership lens |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive R/S/M (fail modes, hot keys, slices) |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact; lock MVP; split check/settle; name pager owners; refuse unbounded fail-open.

---
## 10. Operability

### Golden signals
check_latency, traffic, deny_ratio, redis_errors, overshoot_estimate, settle_lag.

### Rollback ladder
Shadow off → revert policy_version → fail-static → shed classes → cell isolate → postmortem.

### Kill switches
Disable optional dims; freeze boosts; edge shed; isolate marketplace cell.

### Security/privacy
Authn for admin; no PII in keys beyond hashed account ids; audit sampled decisions.

### Cost worksheet
Dominant: Redis. Lever: local approx hit rate. 10× cost with/without architectural jump.

```text
instances ≈ peak_QPS × cpu_sec / (cores × util)
```

### Progressive scale
10× cluster/pipeline; 100× hybrid/slices; 1,000× cells/approx/edge.

### Cross-team deps
Identity, Gateway, WAF, Billing events, Inventory flash — each with failure mitigation.

---
## More Interview Q&A — Rate Limiter

**Q1. Fixed window boundary burst?**

**A:** Admit spike at window edge—mitigate with sliding window or staggered buckets / dual counters.

**Q2. Distributed fairness under overload?**

**A:** Weighted fair share / deficit round-robin on congested models or shared backends.

**Q3. Concurrency vs RPM?**

**A:** Concurrency caps in-flight cost; RPM caps arrival rate—both needed for slow handlers.

**Q4. TTL too short?**

**A:** False reclaim → over-admit; too long → under-utilization. Tie TTL to p99 handler latency × safety factor.

**Q5. Config push failure?**

**A:** Last-known-good; alert; never zero-out limits on empty fetch.

**Q6. Edge WAF vs app limiter?**

**A:** Edge for volumetric abuse; app for business quotas—both.

**Q7. Exact global sync <5ms?**

**A:** Refuse—physics. Offer slices + ε.

**Q8. Per-SKU limits?**

**A:** Yes for flash deals; key by ASIN with aggressive hot-key design.

**Q9. SDK best practices?**

**A:** Honor Retry-After, exponential backoff + jitter, idempotency keys.

**Q10. Canary bad policy?**

**A:** Auto rollback if deny_ratio delta exceeds threshold on canary cell.

**Q11. Multi-tenant cells?**

**A:** Cell per marketplace/partition; no cross-cell shared hot keys.

**Q12. Graceful degrade list?**

**A:** Shed reads/reports first; protect checkout/payments.

**Q13. Audit requirements?**

**A:** Sampled decision logs with policy_version for disputes.

**Q14. Redis MEMORY pressure?**

**A:** Evict cold keys carefully—active limiter keys must not random-evict; use dedicated instance class.

**Q15. gRPC vs HTTP?**

**A:** Same semantics; map to status RESOURCE_EXHAUSTED + metadata.

**Q16. Cron job storms?**

**A:** Separate quota class for batch; smooth with token drip.

**Q17. IPv6 / NAT shared IP?**

**A:** Prefer account keys; IP as abuse signal only.

**Q18. Secondary indexes cost?**

**A:** Don’t store per-request rows in SQL for hot path.

**Q19. Property tests?**

**A:** Never negative concurrency; settle idempotent; TTL reclaim; hierarchy monotonic.

**Q20. Cost KPI?**

**A:** check_µs and redis_ops_per_check; target single RTT.

**Q21. How do boosts work?**

**A:** Temporary policy overlays with expiry; versioned.

**Q22. Ban lists?**

**A:** EXISTS ban_key short-circuit before arithmetic.

**Q23. Sticky sessions help?**

**A:** Slightly for local approx; still need shared truth.

**Q24. Does Mesh ratelimit replace this?**

**A:** Mesh coarse RPM; business TPM/hierarchy still needed.


## Deep Technical Addenda — Rate Limiter

### Worked Prime Day example
Celebrity ASIN flash: 500K check/s on one key. Single Redis shard melts. Mitigation: key-split into N partial buckets + admit if sum tokens; or dedicated cell with in-memory bucket synced every 50ms; edge coarse RPM first.

### Hierarchy numeric example
User 100 RPM, Seller parent 10K RPM, Marketplace 1M RPM. User at 100 → deny user even if seller remaining huge. Remaining headers show min across dims.

### Fail-static numeric ceiling
If Redis down, authenticated checkout class admits ≤ 20% of historical p95 with token drip in process memory—hard stop beyond. Anonymous deny.

## Tradeoff Matrices — Rate Limiter

| Choice | Pros | Cons | Amazon pick |
|--------|------|------|-------------|
| Exact global | Fair contracts | Impossible latency | Slices+ε |
| Fail-open | Availability | Cost blowup | Fail-static/closed |
| Pure sliding log | Precise | Memory/CPU | Bucket+selective sliding |
| Mesh-only limits | Simple | Weak business hierarchy | Mesh + app limiter |

## Operability Addenda — Rate Limiter

Pages: check_p99 burn; redis_error rate; overshoot > 2ε; policy push fail; settle_lag SLO.

Dashboards: heatmap of top deny keys (sampled); cell health; coordinator lag.

## Worked Capacity Narrative — Rate Limiter

At 10M check/s with 1 Lua RTT and 50K ops/s per shard equivalent budget, you need hundreds of shards **or** hybrid local admission. Interviewers want the jump called out before you claim “Redis Cluster scales forever.”

## Customer-Trust Paragraph — Rate Limiter

Bad throttling is a trust incident: false 429s block checkout; missing limits let scrapers degrade Prime Day. Put customer impact next to fail-mode choice.

## Progressive Scale Recap — Rate Limiter

- **10×:** Redis Cluster, pipeline, caches
- **100×:** hybrid local+regional slices, async settle
- **1,000×:** cells, approx global, edge RPM, hot-key platforms

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Rate Limiter

### S1. Token-bucket vs sliding window

Token bucket for bursty API traffic with refill; sliding window log for precise per-minute fairness on expensive ops. Hybrid is common: bucket for RPM, fixed window with grace for daily quotas.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S2. Hierarchical keys

Limit by account → seller → API key → IP. Child cannot exceed parent remaining. Deny reason names the tightest dimension.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S3. Fail-closed vs fail-open

Abuse/anonymous: fail-closed. Checkout-critical authenticated paths: fail-static with hard regional ceiling—never unbounded open.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S4. Hot-key isolation

Celebrity sellers and Prime Day SKUs pin to dedicated Redis slots or local cells; coalesce checks; never one shard for all.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S5. Expiry & lease reclaim

Reservations and concurrency leases always TTL; sweeper reclaims; settle idempotent by request_id.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S6. Regional + global caps

Enforce in-region; async global slice reconciliation with bounded overshoot ε; no cross-region RTT on hot path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S7. Shadow & canary policies

New limits run observe-only; promote with policy_version stamp; rollback is pointer flip.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S8. Ownership boundary

Limiter owns allow/deny arithmetic; product owns policy numbers; billing is a separate ledger consuming usage events.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?


## Scenario Runbooks — Rate Limiter

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Redis cluster partition | Fail-static regional ceilings; freeze boosts | Bounded overshoot, not free-for-all | Postmortem + slice resize |
| Prime Day hot key | Pin key; local approximation; shed noncritical | Checkout protected | Hot-key cell playbook |
| Policy bug zero limits | Last-known-good policy; halt pushes | Avoid mass 429 | Canary gates |
| Clock skew storm | Prefer Redis server time | Correct windows | NTP/time SLO |
| Settle lag spike | Backpressure; sweeper SLO page | Debt not lost | Async settle path |
| Abuse flood | Edge RPM + CAPTCHA escalate | Protect core APIs | WAF + limiter tandem |


## Rapid-Fire Q&A — Rate Limiter

**RQ1. Why does 'Token-bucket vs sliding window' matter in an L6 interview?**

**A:** Token bucket for bursty API traffic with refill; sliding window log for precise per-minute fairness on expensive ops. Hybrid is common: bucket for RPM, fixed window with grace for daily quotas. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Token-bucket vs sliding window' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Token-bucket vs sliding window' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Hierarchical keys' matter in an L6 interview?**

**A:** Limit by account → seller → API key → IP. Child cannot exceed parent remaining. Deny reason names the tightest dimension. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Hierarchical keys' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Hierarchical keys' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Fail-closed vs fail-open' matter in an L6 interview?**

**A:** Abuse/anonymous: fail-closed. Checkout-critical authenticated paths: fail-static with hard regional ceiling—never unbounded open. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Fail-closed vs fail-open' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Fail-closed vs fail-open' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Hot-key isolation' matter in an L6 interview?**

**A:** Celebrity sellers and Prime Day SKUs pin to dedicated Redis slots or local cells; coalesce checks; never one shard for all. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Hot-key isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Hot-key isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Expiry & lease reclaim' matter in an L6 interview?**

**A:** Reservations and concurrency leases always TTL; sweeper reclaims; settle idempotent by request_id. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Expiry & lease reclaim' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Expiry & lease reclaim' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Regional + global caps' matter in an L6 interview?**

**A:** Enforce in-region; async global slice reconciliation with bounded overshoot ε; no cross-region RTT on hot path. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Regional + global caps' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Regional + global caps' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Shadow & canary policies' matter in an L6 interview?**

**A:** New limits run observe-only; promote with policy_version stamp; rollback is pointer flip. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Shadow & canary policies' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Shadow & canary policies' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Ownership boundary' matter in an L6 interview?**

**A:** Limiter owns allow/deny arithmetic; product owns policy numbers; billing is a separate ledger consuming usage events. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Ownership boundary' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Ownership boundary' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Rate Limiter

### Walkthrough beat 1

Customer hits Add-to-Cart API; edge resolves identity; Rate Limit service runs Lua token-bucket+concurrency reserve; response stamps policy_version and remaining headers. Watch check_p99 and deny_ratio{reason}.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Streaming or long checkout hold: concurrency lease heartbeats; on success settle tokens; on abandon TTL reclaim. Degradation: if Redis slow, fail-static ceiling for authenticated checkout only.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Seller API batch upload hits org TPM; hierarchical deny names org dimension; Retry-After computed from refill. Metric: hierarchical_deny_share.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Global contract cap: regional limiters debit local slices; coordinator reconciles every few seconds. Overshoot ε documented. Never block admit on global RTT.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Config canary: 1% shadow→enforce; compare deny deltas; rollback via config pointer. Ownership: Limiter Platform pages latency; Policy owners page deny spikes from bad configs.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

10×: Redis Cluster + pipeline. 100×: hybrid local buckets. 1,000×: cell fleets + approximate global. State what breaks if you only add Redis nodes.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

SEV: fail-open unbounded would burn downstream Dynamo/S3 and customer trust via outage—explicitly refuse.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

Close with unit economics: check_cost_per_M and overshoot_ε as first-class KPIs alongside availability.

Call out one tradeoff you are making (latency vs correctness, exact vs approximate, availability vs abuse protection) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Rate Limiter

- [ ] Can explain **Token-bucket vs sliding window** with numbers and a deal-breaker
- [ ] Can explain **Hierarchical keys** with numbers and a deal-breaker
- [ ] Can explain **Fail-closed vs fail-open** with numbers and a deal-breaker
- [ ] Can explain **Hot-key isolation** with numbers and a deal-breaker
- [ ] Can explain **Expiry & lease reclaim** with numbers and a deal-breaker
- [ ] Can explain **Regional + global caps** with numbers and a deal-breaker
- [ ] Can explain **Shadow & canary policies** with numbers and a deal-breaker
- [ ] Can explain **Ownership boundary** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Redis cluster partition**
- [ ] Has a 30-second runbook for **Prime Day hot key**
- [ ] Has a 30-second runbook for **Policy bug zero limits**
- [ ] Has a 30-second runbook for **Clock skew storm**
- [ ] Has a 30-second runbook for **Settle lag spike**
- [ ] Has a 30-second runbook for **Abuse flood**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Rate Limiter to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


*End of document — Rate Limiter / Expiry Throttling (Amazon Platform) (SDE III)*


## Whiteboard Numeric Drills — Rate Limiter Expiry Throttling

### Drill A — 10× jump
State the baseline bottleneck metric, the mechanism that breaks first when traffic rises 10×, and the concrete architectural jump (not “add servers”). Name the dashboard panel that confirms the jump worked.

### Drill B — 100× jump
Explain which consistency/freshness/accuracy ε you accept at 100× and how the customer is informed or protected. Tie to a kill switch.

### Drill C — 1,000× jump
Describe cell isolation, approximate algorithms, or edge offload. Call the unit-cost metric (`$/M requests` or equivalent) and what linear scaling would have cost.

### Drill D — Ownership one-liner
Who pages for latency vs correctness vs policy? What artifact (config pointer, model version, ring map) do you revert?

### Drill E — Deal-breaker refusal
In one sentence, refuse the classic bad design for this topic and replace it with the Amazon-bar alternative.

