# System Design: Rate Limiter (Microsoft / Azure Platform)

> **Focus areas:** Token bucket · Sliding window · Hierarchical quotas · Reserve+settle · Hot keys · Fail-closed/static · Regional+global slices · Azure APIM / Front Door · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic; split check vs settle QPS; explicit overshoot ε; ownership of allow/deny; compliance-aware tenancy  
> **Interview theme:** Microsoft L61–L64 — shared **Rate Limiter** platform for Azure public APIs, Microsoft 365, Copilot/AI token budgets, and internal microservices

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

Goal: Design a **shared throttling platform** that enforces hierarchical RPM/TPM/concurrency (and cost-unit budgets such as AI tokens) with low-latency decisions, bounded overshoot under partitions, and explicit fail modes—used by Azure Resource Manager–style APIs, Microsoft Graph, Copilot backends, and first-party services.

### 1.0 What this is / is not

| Dimension | **Rate Limiter (this doc)** | Not this |
|-----------|-----------------------------|----------|
| Job | Allow/deny + remaining + Retry-After | Full API Gateway product |
| State | Counters / buckets / leases | Business entity DB |
| Billing | Usage events out | Invoice ledger / Commerce |
| Auth | Consumes identity | Replaces Entra |
| Microsoft lens | Azure subscription quotas, Graph throttling, Copilot TPM, abuse cost | Academic fairness alone |

### 1.1 Functional requirements

| # | Question | Expected answer | Design implication |
|---|----------|-----------------|--------------------|
| F1 | Who is limited? | Tenant, subscription, app, user, IP, operation, model | Composite hierarchical keys |
| F2 | Dimensions? | RPM, burst, concurrency, daily quota, TPM/cost units | Separate algorithms per dim |
| F3 | Hard vs soft? | Hard 429; soft headers/warn optional | Stable decision API |
| F4 | Unknown cost? | Reserve → settle (AI tokens, fanout) | Debt + TTL reclaim |
| F5 | Regional vs global? | Regional enforce; global contract caps | Slices + ε overshoot |
| F6 | Fairness? | No single tenant starves shared capacity | Weighted shares |
| F7 | Admin? | Boosts, bans, shadow policies | Versioned policy |
| F8 | Observability? | Deny reasons, hot keys, check latency | Bounded cardinality |
| F9 | SDK contract? | 429 + Retry-After + remaining + policy_version | Idempotent request_id |
| F10 | Integration? | APIM, Front Door, Envoy/sidecar, SDK | Multiple enforcement points |
| F11 | Compliance? | Audit denies for enterprise tenants | Retention policy |
| F12 | AI budgets? | Tokens/min, tokens/day, concurrent inferences | Cost-unit dimension |

**MVP:** check/reserve, settle, hierarchy, Redis/Lua (or equivalent) atomic update, policy control plane, fail-closed/static, hot-key playbook, metrics, Azure identity attributes on keys.

**Out of MVP:** Perfect global linearizability; replacing WAF volumetric DDoS; full commerce billing; GPU scheduling auctions.

### 1.2 Non-functional requirements

| # | Target |
|---|--------|
| N1 | check p99 < 5–10 ms in-region |
| N2 | Overshoot ≤ ε (e.g. 5–15%) under partition vs global cap |
| N3 | 99.99% decision availability with documented degrade |
| N4 | Never unbounded fail-open |
| N5 | Policy propagation seconds (not hours) |
| N6 | Multi-AZ Redis/state HA |
| N7 | Tenant isolation on hot paths |
| N8 | Clear `$ / M checks` economics |

### 1.3 Cases

**Happy:** allow within bucket; burst then 429; settle releases reserved tokens; boost overlay; hierarchical deny cites tightest key; Copilot TPM reserve→settle.

**Edges:** Redis partition; hot tenant; duplicate settle; lease expiry mid-flight; bad policy canary; clock skew; regional failover; AI cost underestimate; thundering herd after outage.

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Check QPS | 100K | 1M | 10M | 100M |
| Settle QPS | 80K | 800K | 8M | 80M |
| Distinct keys/min | 50K | 200K | 1M | 5M+ |
| Azure regions | 3 | 4 | 8 | 20+ / sovereign |
| Policy updates/day | 1K | 10K | 50K | 200K |

**Jumps:** Redis Cluster → hybrid local+regional → cell fleets + approx global + edge RPM.

### 1.5 Scope repeat-back

> Shared Microsoft/Azure rate-limiter service: hierarchical RPM/concurrency/cost units (incl. AI TPM), reserve+settle+TTL, regional enforcement with global slices and bounded ε, explicit fail-static ceilings, hot-key isolation, APIM/Front Door/SDK integration—scaling checks from ~100K/s to ~100M/s.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Check/reserve | 100K/s | 100M/s | Sync, latency-critical |
| Settle/release | 80K/s | 80M/s | Slightly async OK |
| Lease renew | 20K/s | 20M/s | Concurrency holds |
| Policy watch | Low | Low | Pub/sub |
| Global sync | 2–10K/s | 0.2–2M/s | Batched slice deltas |
| Usage events | ~check rate | Huge | Async bus |

### 2.2 Redis / state math

```text
100K checks × 1 Lua RTT ≈ 100K rps cluster-wide — comfortable with shards
100M checks → must hybrid local approximation + many cells
Ops/check goal: 1 RTT (pipeline/Lua), not 6 round-trips

Memory: 1M active keys × 256 B ≈ 256 MB + overhead → GB-class easy
Hot keys dominate CPU, not memory
```

### 2.3 Latency budget

```text
Edge / APIM             1–2 ms
Identity attribute cache 0.5 ms
Limiter Lua / local      1–3 ms
Header build             <1 ms
Total p99                ≤ 10 ms in-region
```

### 2.4 Token-bucket arithmetic (correctness)

```text
capacity C, refill rate R tokens/sec, last_ts T0, tokens K
now = server_time
K = min(C, K + R * (now - T0))
if K >= cost: K -= cost; allow
else: deny; Retry-After ≈ (cost - K) / R

Burst = C; sustained = R
Example: R=100/s, C=200 → 200 burst, then 100/s sustained
```

### 2.5 Sliding window arithmetic

```text
Fixed window: simple; boundary burst 2× possible
Sliding log: precise; memory heavy (store timestamps)
Sliding window counter: weight previous bucket + current
  count ≈ prev * (1 - elapsed/window) + curr
Trade precision vs memory vs CPU
```

### 2.6 Global slice math

```text
Global cap G = 1e6 RPM
Regions r1..rn with weights w_i, sum w = 1
Slice_i = G * w_i + burst_credit
Under partition: each region may admit Slice_i → overshoot ≤ sum(burst_credit)
Choose burst_credit so ε ≤ 10% of G
```

### 2.7 AI TPM example

```text
Reserve est_tokens=4000; settle actual=3200 → credit 800
If settle missing: TTL reclaim reservation
Underestimate chronic → debt on next requests
100K inferences/s × reserve ops ≈ need hybrid path early
```

### 2.8 Cost

Dominant: Redis CPU for hot keys + network RTT. +10% local allow-cache hit ≫ doubling cluster. Track `$ / M checks`.

---

## 3. High-Level Design

### 3.1 Components

| Component | Role |
|-----------|------|
| Front Door / WAF | Volumetric first line |
| APIM / Gateway | Policy attach; call limiter |
| Rate Limit Service | Decision orchestration |
| Redis Cluster (or Cosmos/KV counters) | Atomic buckets/leases |
| Local approx cache | Slice debit at extreme scale |
| Policy Control Plane | Versioned configs |
| Global Slice Coordinator | Regional shares |
| Hot-Key Cell Router | Isolate celebrities |
| Usage Events bus | Billing/analytics (async) |
| Admin / Portal | Boosts, bans, shadow |
| Observability | Metrics, audit |

### 3.2 APIs

```text
POST /v1/check
  { key, dims[], cost_est, request_id, tenant, region }
  → { decision: allow|deny, remaining, reset_ms, retry_after_ms,
      policy_version, reason_code }

POST /v1/settle
  { request_id, actual_cost }

POST /v1/heartbeat
  { lease_id }   # concurrency

POST /v1/shadow_check  # decide without enforce
```

**HTTP client contract:**

```text
429 Too Many Requests
Retry-After: <seconds>
X-RateLimit-Limit / Remaining / Reset
x-ms-ratelimit-policy-version
x-ms-ratelimit-reason: subscription|user|op|tpm
```

### 3.3 Algorithms — Why X over Y

| Algorithm | Pros | Cons | Best for |
|-----------|------|------|----------|
| **Token bucket** | Burst + smooth refill | Less intuitive fairness | **Default APIs** |
| Leaky bucket | Smooth egress | Less client burst | Gateways shaping |
| Fixed window | Simple | Boundary double-burst | Coarse quotas |
| **Sliding window counter** | Better fairness | Approx | Strict RPM fairness |
| Sliding log | Precise | Memory | Low-volume precision |
| Concurrency leases | Caps in-flight | Needs TTL reclaim | Expensive ops / AI |

**Chosen:** Token bucket for RPM/burst; sliding window optional for strict fairness SKUs; concurrency leases for in-flight; cost-unit buckets for TPM; hierarchy = AND across dims (remaining = min).

**Deal-breaker:** single global Redis key for all traffic; or silent unbounded fail-open.

### 3.4 Placement — Why X over Y

| Placement | Pros | Cons |
|-----------|------|------|
| Only edge | Cheap | Coarse; misses app-level keys |
| Only service mesh | Per-service | Inconsistent enterprise UX |
| **Central RL + edge** | Shared truth + volumetric | Extra hop |
| Library-only | Fast | Multi-host unfair |

**Chosen:** Edge volumetric + gateway/sidecar check against shared RL service; SDK optional for service-to-service.

### 3.5 State store — Why X over Y

| Store | Pros | Cons |
|-------|------|------|
| **Redis Cluster + Lua** | Atomic multi-key, low ms | Hot shard risk |
| Special KV counters | Fits Azure stack | Need atomic primitives |
| Local memory only | Fast | Unfair multi-instance |
| DB row locks | Familiar | Too slow at 100K+ |

**Chosen:** Redis-class atomic scripts at baseline; hybrid local+slice at 100×+.

### 3.6 Tradeoffs summary

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Algorithm | Bucket + optional sliding | Burst + fairness options | Fixed window only forever |
| Global | Slices + ε | No cross-region RTT on hot path | Linearizable global check |
| Fail mode | Fail-static / closed | Abuse safety | Unbounded open |
| Cost ops | Reserve+settle | AI tokens unknown a priori | Always exact pre-debit |
| Hot keys | Cells | Zipf | Hope |
| Billing | Async events | Limiter ≠ ledger | Synchronous billing on check |

---

## 4. Architecture Diagram

```text
 Client / SDK
     |
     v
 Front Door (volumetric) --> APIM / Gateway --> Downstream Azure / M365 service
                               |
                               v
                        Rate Limit Service
                         |         |         |
                         v         v         v
                   Redis Cluster  Local     Hot-Key
                   (Lua buckets)  approx    Cells
                         |
                         v
                   Usage Events --> Analytics / Commerce (async)

 Policy Control Plane --pub/sub--> Limiters (policy_version)
 Global Coordinator <--> regional slice deltas (async)
 Entra / identity attributes --> key material (tenant, app, user)
```

**Degrade path:** Redis errors → fail-static ceiling (authenticated) or fail-closed (anonymous) → shed noncritical classes → cell isolate → edge-only RPM.

---

## 5. Design Deep Dive

### 5.1 Reliability (R)

**Invariants:**

1. Idempotent check/settle by `request_id` within TTL.  
2. Lease TTL reclaim → concurrency never stuck forever.  
3. `policy_version` monotonic on responses.  
4. No unbounded fail-open.  
5. Deny never requires cross-region RTT.  
6. Overshoot ≤ ε under coordinator partition.  
7. Hierarchy: allow iff all ancestor dims allow.

**Failure table:**

| Failure | Behavior |
|---------|----------|
| Redis shard down | Fail-static for affected key ranges; alert |
| Coordinator lag | Admit within slice+credit; freeze raises |
| Duplicate settle | Idempotent no-op |
| Clock skew | Server TIME only |
| Bad policy push | Shadow + canary; instant rollback by version |
| Hot key melt | Cell redirect; coarser bucket |

### 5.2 Scalability (S)

| Scale | Architecture |
|-------|--------------|
| 1× | Regional RL + Redis Lua |
| 10× | Cluster, pipeline, identity cache, deny short-circuit |
| 100× | Hybrid local buckets + regional slices + Kafka settles |
| 1,000× | Many cells, approx global, edge RPM, AI TPM cells |

**Hot keys:** dedicated shard/cell; local token cache with sync; coalesce; coarser buckets for flash events.

**Hierarchy performance:** multi-key Lua in one RTT; or ordered locks carefully; cache allow for parent dims with short TTL when safe.

### 5.3 Maintainability (M)

Shadow policies; canary cells; load-test hot tenants; metrics without high-cardinality labels; runbooks for partition and zero-limit bugs; SDK contract versioning; PIM for admin boosts.

### 5.4 Token bucket vs sliding window (deep)

**Token bucket** favors API UX with burst (mobile clients, retries).  
**Sliding window** favored when auditors demand “≤ N per rolling minute” with low boundary error.  
Hybrid: bucket for soft RPM; sliding for hard contractual caps.

### 5.5 Reserve + settle (AI / Copilot)

```text
check(cost_est) -> reservation_id
work()
settle(actual) -> adjust bucket
timeout -> sweeper releases reservation
debt if actual > est chronically
```

Never block settle on billing systems.

### 5.6 Fail modes (explicit matrix)

| Identity | Default on store failure |
|----------|--------------------------|
| Anonymous / suspicious | Fail-closed |
| Authenticated standard | Fail-static low ceiling |
| Critical first-party | Fail-static higher ceiling + page |
| Admin break-glass | Explicit override audited |

### 5.7 Microsoft / Azure integration notes

- Map keys from `subscriptionId`, `tenantId`, `clientId`, `operationId`.  
- Align reason codes with Graph/ARM throttling mental model.  
- Front Door for L3/L4 volumetric; RL for application semantics.  
- Sovereign clouds: separate coordinators; no cross-cloud slice sync if forbidden.  
- Audit logs for enterprise deny investigation (sampled + always for admin).

### 5.8 Consistency honesty

Per-key regional ≈ sequential via Lua. Global eventual with ε. Dashboards may disagree with live remaining by seconds.

---

## 6. Wrap-Up

### 6.1 What we designed

Microsoft/Azure-grade rate limiter with hierarchy, reserve+settle, Redis→hybrid→cells progressive scale, fail-static ceilings, hot-key isolation, APIM/Front Door integration, AI TPM support.

### 6.2 Key decisions worth defending

1. Split dimensions (RPM / concurrency / cost).  
2. Reserve+settle+TTL.  
3. No global RTT on hot path.  
4. Fail-closed/static never unbounded open.  
5. Hot keys first-class.  
6. Limiter ≠ billing.  
7. Shadow/canary `policy_version`.  
8. 1000× forces hybrid, not bigger Redis alone.

### 6.3 Risks & follow-ups

Chronic underestimate; Redis hot shard; coordinator lag; fail-static abuse; settle lag; policy fanout bugs; cardinality explosions.

### 6.4 Closer

> **Rate Limiter**: explicit planes, SLOs, ownership, progressive scale, Azure tenancy keys, bounded ε, customer-trust fail modes.

---

## 7. Deeper / Related Interview Questions

**Q1. Token bucket or sliding window?**

**A:** Bucket for bursty Azure APIs; sliding when contractual fairness is strict. Defend hybrid.

**Q2. Where does the limiter sit?**

**A:** Beside APIM/gateway/mesh—before expensive business logic, storage fanout, and GPU/AI inference.

**Q3. Unknown cost ops?**

**A:** Reserve estimate → settle actual; debt; TTL reclaim.

**Q4. Fail open or closed?**

**A:** Fail-closed for anon; fail-static ceilings for authed. Never unbounded open.

**Q5. Hierarchy enforcement?**

**A:** Allow iff all dims allow; atomic multi-key Lua; deny cites tightest key.

**Q6. Clock skew?**

**A:** Redis/server TIME; ignore client clocks.

**Q7. Hot celebrity tenant?**

**A:** Dedicated cell; local cache; coalesce; coarser buckets.

**Q8. Idempotent retries?**

**A:** `request_id` reservation replay within TTL.

**Q9. Multi-region truth?**

**A:** Regional hard + global slices with ε; not linearizable worldwide.

**Q10. Headers contract?**

**A:** 429, Retry-After, Limit/Remaining/Reset, policy_version, reason.

**Q11. Shadow mode?**

**A:** Dual-run without enforce; compare; promote.

**Q12. Limiter vs billing?**

**A:** Separate SoT; append-only usage events; reconciliation sweeper.

**Q13. Local in-process enough?**

**A:** First line only; shared store for multi-host fairness.

**Q14. Lua vs app CAS?**

**A:** Lua/single RTT for atomic multi-counter updates.

**Q15. Deal-breaker?**

**A:** Single global counter key, or silent fail-open.

**Q16. Copilot TPM specifics?**

**A:** Cost-unit bucket; reserve/settle; per-model dims; concurrency for in-flight inferences.

**Q17. Observability cardinality?**

**A:** No raw tenant_id on Prometheus; exemplars + sampled logs.

**Q18. Thundering herd after outage?**

**A:** Jittered Retry-After; client SDKs; token recovery rate limits.

**Q19. Who pages on deny spike?**

**A:** Config change → policy owner; Redis/latency → limiter platform.

**Q20. How to test ε?**

**A:** Chaos partition coordinator; measure regional admit vs ε.

**Q21. Fixed window boundary burst?**

**A:** At minute boundary can admit ~2×; use sliding or bucket to avoid.

**Q22. Weighted fairness?**

**A:** Under overload, allocate shares by tenant tier; protect SMBs from whales.

**Q23. Distributed locks for limiter?**

**A:** Usually wrong—use atomic counters/scripts, not coarse locks.

**Q24. Rate limit by IP behind NAT?**

**A:** IP dims are coarse; prefer authenticated keys; IP as abuse signal only.

**Q25. Policy propagation races?**

**A:** Versioned policies; decisions stamp version; rollback by pin.

---

## 8. Appendices

### A — Glossary

| Term | Meaning |
|------|---------|
| Slice | Regional share of a global cap |
| ε / overshoot | Bound beyond global truth under partition |
| Fail-static | Admit using hard-coded ceiling without Redis |
| Lease | TTL'd concurrency/reservation |
| Policy_version | Monotonic config stamp |
| TPM | Tokens per minute (AI) |
| Cell | Failure-isolated limiter fleet |
| Deal-breaker | Unbounded fail-open or single global counter |

### B — Oncall checklist

- [ ] check_p99 / deny_ratio  
- [ ] Last-known-good policy armed  
- [ ] Fail-static ceilings documented  
- [ ] Hot-key cells ready  
- [ ] Global coordinator lag SLO  
- [ ] Settle backlog  

### C — Redis key schema

```text
rl:{tenant}:{key}:rpm -> token bucket hash
rl:{tenant}:{key}:conc -> int + lease set
rl:{tenant}:{key}:tpm -> cost bucket
rl:{tenant}:{key}:ban -> TTL flag
rl:req:{request_id} -> reservation
rl:policy:{id} -> versioned blob ref
```

### D — Scale checklist

10× cluster; 100× hybrid; 1,000× cells+approx; measure ops/check.

### E — Estimation cheat-sheet

```text
redis_ops ≈ check_qps × rtt_ops_per_check
cells ≈ peak_check_qps / per_cell_budget
ε ≈ sum(regional_burst_credits) / global_cap
```

### F — Closer checklist

- [ ] Hierarchy + deny reason  
- [ ] Reserve/settle/TTL  
- [ ] Fail mode explicit  
- [ ] Hot-key story  
- [ ] Progressive scale  
- [ ] Azure identity key material  

---

## Deep Technical Notes — Rate Limiter

### Lua atomicity

Single SCRIPT for refill+debit+concurrency. Return structured allow/deny. Avoid multi-RTT WATCH storms.

### Slice accounting

Coordinator assigns `slice_i`; limiter refuses when `local_debit ≥ slice + burst_credit`; gossip adjustments; emergency freeze.

### SDK contract

Idempotency keys for mutating APIs; Retry-After jitter; distinguish 429 vs 503.

### APIM integration

Policy calls RL; cache allow briefly for ultra-hot GETs only if ε allows; never cache deny forever.

### Property tests

Never negative concurrency; settle ≤ 1 effect; hierarchy remaining = min; ban short-circuit; TTL reclaim within T+δ.

### Multi-tenant Azure

Subscription throttling: fairness so mega-tenants cannot starve others on shared backends—weighted shares + dedicated cells.

### Settlement pipeline

```text
settle events -> Kafka/Event Hubs -> adjusters -> Redis
OR sync settle for small actuals
At 100× prefer async settle with reservation holds
```

---

## Interview Cards — Rate Limiter (Microsoft)

### Card 1: Token bucket or sliding window?

Bucket for burst; sliding for strict fairness; hybrid common.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Map to ARM/Graph throttling UX and Copilot TPM.

### Card 2: Where does it sit?

APIM/gateway/mesh before expensive work.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Front Door volumetric vs app RL split.

### Card 3: Reserve+settle?

Required for unknown AI cost; TTL reclaim; debt.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Copilot/inference economics.

### Card 4: Fail open/closed?

Never unbounded open; static ceilings by class.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Abuse + enterprise trust.

### Card 5: Hierarchy?

AND across dims; cite tightest; one RTT Lua.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** subscription → app → user → op.

### Card 6: Clock skew?

Server time only.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Multi-region Redis TIME discipline.

### Card 7: Hot keys?

Cells; local approx; coalesce.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Viral tenant / launch day.

### Card 8: Idempotency?

request_id replay.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Azure client retry guidelines.

### Card 9: Multi-region?

Slices + ε; no global RTT.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Sovereign cloud isolation.

### Card 10: Headers?

429 + Retry-After + remaining + reason.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Consistent with public Azure API norms.

### Card 11: Shadow?

Dual-run; promote by version.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Safe policy rollout.

### Card 12: Limiter ≠ billing?

Async usage events; reconcile later.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Commerce correctness separate.

### Card 13: Local only?

Insufficient for multi-host fairness.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** App Service / K8s replica reality.

### Card 14: Deal-breaker?

Global single key; unbounded fail-open.

**Follow-ups:** 10× break? Who pages? Fallback? Metric?

**Microsoft angle:** Interviewers reward explicit refusal.

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + hierarchy keys (Azure identity) |
| 5–12 | Estimation + bucket math + ε |
| 12–22 | HLD + ASCII + APIs |
| 22–35 | R/S/M: fail modes, hot keys, reserve/settle |
| 35–45 | Tradeoffs & Q&A |

---

## 10. Operability

### Golden signals

check_p99, deny_ratio, redis_p99, settle_lag, coordinator_lag, hot_key_qps, policy_version_skew, fail_static_rate.

### Rollback ladder

Pin previous policy_version → disable new dims → fail-static → edge-only → cell isolate.

### Kill switches

Global freeze raises; per-tenant ban; disable AI reserve path (fail closed); stop shadow flood.

### Security / privacy

Authz on admin; audit boosts/bans; no PII in metric labels; residency for audit logs.

### Cost worksheet

Redis CPU + cells vs abuse cost / GPU burn prevented. Lever: local hit rate + deny short-circuit.

### Progressive scale

10× cluster; 100× hybrid; 1,000× cells+edge.

### Cross-team deps

APIM, Front Door, Entra, Commerce, AI platform, service owners.

---

## More Interview Q&A — Rate Limiter

**Q1. How do you compute Retry-After?**

**A:** From deficit/refill rate; jitter; cap upper bound; different for bans.

**Q2. Soft limit vs hard?**

**A:** Soft: headers + metrics; hard: 429. Enterprise may want soft then hard.

**Q3. Distributed tracing?**

**A:** Span limiter decision; exemplar on deny spikes; careful sampling.

**Q4. Can clients trust Remaining?**

**A:** Best-effort; races exist under concurrency; document.

**Q5. Rate limit webhooks egress?**

**A:** Same platform; different keys; protect downstream partners.

**Q6. IPv6 / NAT?**

**A:** Prefer auth keys; IP as secondary signal.

**Q7. Cron amplify at minute 0?**

**A:** Jitter schedules; bucket smooths; sliding helps contractual.

**Q8. Multi-key transactions across Redis slots?**

**A:** Hash tags to colocate hierarchy keys; or approximate parent cache.

**Q9. Cold start empty buckets?**

**A:** Start full (burst) or empty—product choice; document.

**Q10. Penalty boxes?**

**A:** Ban TTL keys for abuse; escalate to WAF.

**Q11. Exactly-once settle?**

**A:** At-least-once with idempotent apply.

**Q12. How to capacity-plan Redis?**

**A:** Peak check QPS × ops × headroom; CPU for hot keys separate from memory.

**Q13. Graph API compatibility?**

**A:** Reason codes and headers familiar to Graph clients; don’t invent alien UX.

**Q14. Long-running uploads?**

**A:** Concurrency lease + chunked RPM; heartbeat.

**Q15. What proves ε held?**

**A:** Chaos tests + production overshoot dashboard vs global telemetry.

**Q16. Policy as code?**

**A:** GitOps configs; signed publish; versioned artifacts.

**Q17. Multi-cloud clients?**

**A:** Still regional enforce; identity is Entra; slices per cloud boundary.

**Q18. Cost of fail-static too high?**

**A:** Tune ceilings; temporary; page humans; never infinite.

**Q19. Unit test time?**

**A:** Inject fake clock; property test refill math.

**Q20. Closing pitch?**

**A:** “Hierarchical Azure-aware limiter, atomic regional decisions, global slices with ε, reserve/settle for AI, explicit fail-static—not a bigger Redis key.”

---

## Progressive Architecture Jump Cards

### 1× MVP

APIM → RL service → Redis Lua; token bucket + concurrency; policy pub/sub; fail-static.

### 10×

Redis Cluster; pipelines; identity attr cache; hot-key dashboards; shadow policies.

### 100×

Local approx debit; Event Hubs settles; slice coordinator; tenant cells for whales.

### 1,000×

Edge RPM; many cells; approx global; AI TPM specialized cells; sovereign coordinators.

---

## Failure Scenario Scripts

**A — Redis hotspot:** Detect; migrate key to cell; coarsen bucket; page.

**B — Coordinator partition:** Hold slice+credit; freeze increases; measure ε.

**C — Bad policy (limit=0):** Canary deny spike; auto-rollback version; incident.

**D — Settle pipeline down:** Reservations TTL reclaim; admit conservative; backlog replay.

**E — Abuse fail-static:** Lower ceiling; enable WAF; ban keys.

---

## Worked Example — Subscription Hierarchy

```text
Keys checked (AND):
  sub:{subId}:rpm           R=10000/s C=20000
  app:{appId}:rpm           R=1000/s  C=2000
  op:Write:rpm              R=200/s   C=400
  user:{oid}:rpm            R=50/s    C=100

Request cost=1
Allow only if all debit; Remaining = min(remainings)
Deny reason = dim with zero remaining
```

---

## Worked Example — AI TPM

```text
Model gpt-X tenant T:
  tpm bucket R=120000 tokens/min, C=240000
  concurrency max=50 leases

check(est=4000) -> allow, reservation 4k, leases++
inference returns actual=3500
settle -> credit 500; leases--
if crash: TTL 60s releases lease + tokens
```

---

## Ownership & SEV Model

| Symptom | Primary | Secondary |
|---------|---------|-----------|
| Redis latency | Limiter platform | — |
| Deny spike after config | Policy owner | Platform |
| ε breach | Platform | Capacity |
| Commerce mismatch | Commerce | Platform events |
| AI GPU burn despite limits | AI platform + Limiter | Cost under-estimate |

---

## Sample 60-Second Pitch

> We build a shared rate-limit service used by APIM and sidecars. Decisions are hierarchical across subscription, app, user, and operation—and include cost-unit budgets for AI. Regionally we atomically update token buckets and leases in Redis via Lua in one RTT. Globally we assign slices with a bounded overshoot ε so the hot path never waits on cross-region consensus. Unknown costs use reserve and settle. On store failure we fail-static or fail-closed—never unbounded open. At extreme scale we add local approximation and cells, especially for hot tenants and TPM.

---

## Appendix G — Anti-patterns

1. One Redis key for the world.  
2. Fail-open with no ceiling.  
3. Sync billing on check path.  
4. Client-clock windows.  
5. Per-user Prometheus labels.  
6. Caching deny forever.  
7. Global lock per request.  
8. Ignoring settle idempotency.

---

## Appendix H — Mock pushbacks

**Push:** “Make it strongly consistent globally.”  
**Reply:** “Here’s RTT; we use slices and ε instead.”

**Push:** “Fail-open for availability.”  
**Reply:** “Availability of abuse isn’t a feature; fail-static.”

**Push:** “Just use APIM built-in.”  
**Reply:** “Edge policies are necessary but not sufficient for hierarchical AI/cost dims across services.”

**Push:** “Numbers?”  
**Reply:** Walk §2 bucket and slice math.

---

## Appendix I — Definition of done

- [ ] p99 check < 10 ms under target QPS  
- [ ] Chaos Redis + coordinator tests  
- [ ] Shadow→enforce policy path  
- [ ] Hot-key runbook drilled  
- [ ] SDK header contract documented  
- [ ] Fail-static matrix signed off  
- [ ] ε dashboard live  

---

## Appendix J — Algorithm cheat sheet (whiteboard)

```text
TOKEN_BUCKET:
  tokens = min(C, tokens + R*(now-ts))
  allow if tokens >= cost else deny

SLIDING_COUNTER:
  est = prev*(1 - t/W) + curr
  allow if est + cost <= limit

CONCURRENCY:
  if active < max: active++; lease=TTL; allow
  else deny
  on end/TTL: active--

HIERARCHY:
  allow = AND(dims); remaining = MIN(dims.remaining)
```

---

## Appendix K — Comparison table (say crisply)

| Concern | Token bucket | Sliding window | Concurrency |
|---------|--------------|----------------|-------------|
| Burst | Excellent | Moderate | N/A |
| Fairness rolling | Good | Excellent | N/A |
| Memory | Low | Medium | Low |
| AI tokens | Cost bucket | Optional | In-flight |
| Implementation | Easy Lua | Medium | Easy + TTL |

---

*End of Microsoft Rate Limiter system design prep.*
