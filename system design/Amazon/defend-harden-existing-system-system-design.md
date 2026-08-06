# System Design: Defend & Harden an Existing System — Inventory Reservation

> **Focus areas:** Reverse-design a “you built it” service · Isolation · Circuit breakers · Overload shedding · Backpressure · Recovery · Monitoring/SLOs · Ownership · Progressive hardening 10×→1,000×  
> **Style:** Interview format where you **defend** Inventory Reservation under failure & growth  
> **Quality bar:** Concrete failure modes, real capacity math, explicit deal-breakers, Amazon operational ownership  
> **Interview theme:** Amazon SDE III / L6 — “Walk me through a system you built; how would you harden it?”

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

Goal: act as the **owner** of an existing **Inventory Reservation** service (cart/checkout holds units so oversell is controlled). Reverse-design it briefly, then **defend and harden** for isolation, overload, breakers, recovery, and monitoring.

### 1.0 Framing this interview type

| Dimension | What interviewers want | Anti-pattern |
|-----------|------------------------|--------------|
| Ownership | You know failure modes & knobs | Only happy-path boxes |
| Practicality | Incremental hardening | Rewrite fantasy |
| Reliability | Customer impact ordered | Ignore commerce realities |
| Breadth | Isolation→overload→recover→observe | Only “add Redis” |

**Assumed system you “built”:** Inventory Reservation Service (IRS) used by Cart, Checkout, and Fulfillment planning.

### 1.1 Functional Requirements (existing system)

| # | Question | Answer (system as built) | Implication |
|---|----------|--------------------------|-------------|
| F1 | What does it do? | Soft-reserve units for ASIN+FC (or network) with TTL | Reserve/release/confirm APIs |
| F2 | Clients? | Cart, Checkout, Promise, internal tools | Multi-caller isolation needed |
| F3 | Semantics? | Soft hold → confirm on order place → consume on ship | State machine |
| F4 | Oversell policy? | Prefer under-promise; rare races bounded | Conditional writes |
| F5 | Idempotency? | Yes on reserve/confirm keys | Client retries safe |
| F6 | Query stock? | Available = on_hand - reserved - safety | Read path separate |
| F7 | Multi-FC? | Reserve at chosen FC or soft network | Shard key matters |
| F8 | Admin? | Adjust safety stock, break glass release | Audited |

**Hardening scope (this interview’s FR):**

1. Isolate noisy clients / hot ASINs.  
2. Circuit breakers to dependencies and from clients.  
3. Overload detection + load shedding.  
4. Graceful degradation modes.  
5. Recovery runbooks & automated remediation.  
6. Monitoring, SLOs, error budgets.  
7. Scale story 10× / 100× / 1,000× without rewrite myths.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Reserve latency | Checkout-critical | p99 < 30–50 ms in-region |
| N2 | Availability | High | 99.99% for reserve API (cell-local) |
| N3 | Correctness | No silent double-sell beyond budget | Conditional inventory updates |
| N4 | Durability | Holds survive process crash | Store-backed |
| N5 | Isolation | One client/ASIN can’t melt service | Fairness + limits |
| N6 | Recoverability | Minutes, not hours | Playbooks + toggles |
| N7 | Observability | Golden signals + business | SLO dashboards |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Add-to-cart → `Reserve(asin, qty, ttl=20m, key)` → OK.  
2. Checkout → `Confirm(order_id)` → held inventory committed.  
3. Cancel/TTL → release → available increases.  
4. Read available for PDP/promise.

**Edge / failure cases to harden**

| Case | Risk | Hardening |
|------|------|-----------|
| Hot ASIN (Prime Day deal) | Hot partition | Shard + cache + admission |
| Cart retry storm | Amplification | Idempotency + client token bucket |
| Checkout dependency timeout | Threads pile up | Bulkheads + breakers |
| Downstream Dynamo/DB brownout | Latency contagion | Timeouts, shed, degrade |
| Poison request (bad qty) | Worker waste | Validation + DLQ for async |
| Clock skew TTL | Early/late release | Absolute expiry server-side |
| Split brain multi-region | Double reserve | Single-writer home cell |
| Thundering herd recovery | Re-crash | Staggered admission |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Reserve QPS | 20K | 200K | 2M | 20M |
| Confirm QPS | 5K | 50K | 500K | 5M |
| Distinct ASINs hot/hour | 100K | 500K | 2M | 10M |
| Hot ASIN peak QPS | 2K | 20K | 100K | 500K |
| Callers (services) | 10 | 30 | 80 | 200 |
| Inventory rows | 500M | 2B | 10B | 50B+ |

**What each jump forces:**

- **10×:** Bulkheads per caller; timeouts; basic breakers; SLO dashboards.  
- **100×:** Cell architecture; hot-key sharding; adaptive concurrency; chaos tests.  
- **1,000×:** Hierarchical admission; request coalescing; maybe eventual read caches with careful truth path.

### 1.5 Scope statement

> Reverse-design Inventory Reservation, then harden it: bulkhead isolation, circuit breakers, overload shedding, degradation, recovery, and monitoring—defending correctness (bounded oversell) and checkout latency from baseline ~20K reserve QPS through 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Reserve | 20K | 20M | Write-heavy |
| Release/TTL | 15K | 15M | Includes expiry |
| Confirm | 5K | 5M | Critical |
| Available reads | 100K | 100M | Cacheable |
| Admin | tiny | tiny | |

**Critical:** Reads can be 5–10× writes—protect write path from read stampede with caches that don’t lie about reserve truth.

### 2.2 Latency budget (reserve)

```text
Ingress + authz     2–3 ms
Idempotency lookup  1–3 ms
Conditional write   5–15 ms
Response            1 ms
Total p99 target    ≤ 30–50 ms

Dependency timeout budget: 20–25 ms (fail fast vs pileup)
```

### 2.3 Hot ASIN math

```text
Deal ASIN: 50K reserve attempts/s globally
If 1 shard: 50K QPS to one partition → meltdown
Shard by hash(asin, salt_bucket) into N=32 logical shards → ~1.6K QPS each
Still hot → local admission + coalesce identical reads; serialize writes per (asin,shard)
```

### 2.4 Thread / concurrency pileup

```text
Service: 200 instances × 200 workers = 40,000 in-flight max
If each waits 2s on DB: can accept only 40,000/2 = 20,000 QPS before saturation
At 20K baseline OK; at brownout (p99 2s) → collapse without shedding
Need: concurrency caps, timeouts 50ms, shed when in-flight high
```

### 2.5 Storage

```text
Row: asin+fc, on_hand, reserved, version ~100–200 B
500M rows × 200 B = 100 GB raw (+ indexes)
Reservations active: 50M × 150 B = 7.5 GB
```

### 2.6 Critical bottlenecks (defend these)

1. Hot partition ASINs  
2. Dependency latency contagion  
3. Retry amplification  
4. Shared thread pools across callers  
5. Multi-region dual-write fantasies  
6. Cache stampede on available()  

---

## 3. High-Level Design

### 3.1 Existing system (reverse-design)

```text
Clients → API Gateway → IRS Stateless Fleet
                           |
                           +→ Idempotency Store
                           +→ Inventory Store (conditional updates)
                           +→ TTL / expiry workers
                           +→ Event bus (reserved/released/confirmed)

Reserve:
  if idem_hit: return prior
  CAS reserved' = reserved + qty if on_hand - reserved - safety >= qty
  write reservation record expires_at
Confirm:
  mark reservation CONFIRMED; keep reserved until consume or convert
Release/TTL:
  decrement reserved; delete/cancel reservation
```

### 3.2 Hardening architecture (target)

| Layer | Control |
|-------|---------|
| Edge | Per-caller auth, WAF, TLS |
| Ingress | Rate limits, concurrency tokens |
| Service | Bulkheads, timeouts, breakers |
| Data | Hot-key shards, conditional writes |
| Async | Bounded queues, DLQ |
| Ops | Feature toggles, kill switches |

### 3.3 Isolation (bulkheads)

```text
Caller bulkheads: Cart | Checkout | Promise | Internal
  - separate concurrency pools / queues
  - separate rate limits (Checkout > Cart fairness policy)
  - separate circuit breakers to store

ASIN bulkheads:
  - hot-key detector → dedicated lane / stricter admission
```

**Deal-breaker:** one shared unbounded executor for all callers into one DB pool.

### 3.4 Circuit breakers

| Breaker | Opens when | Effect |
|---------|------------|--------|
| IRS → Inventory Store | error/latency rate high | Fail fast; degrade mode |
| Edge → IRS (per cell) | cell unhealthy | Shift traffic / shed |
| Client SDK → IRS | IRS errors | Client local degrade (cached available?) carefully |

States: CLOSED → OPEN → HALF_OPEN (probe).

**Checkout policy:** if reserve unavailable, prefer **fail closed on oversell risk** (don’t sell unconstrained) but UX may show “try again” vs oversell.

### 3.5 Overload & load shedding

```text
Admission controller:
  if in_flight > HPA_high OR cpu > 80% OR store_p99 > SLO:
     shed low-priority (browse reserve prefetch)
     keep Checkout confirm/reserve
  return 429 with Retry-After + jitter
```

Priority (example):

1. Confirm / Release (correctness)  
2. Checkout Reserve  
3. Cart Reserve  
4. Speculative prefetch  

### 3.6 Backpressure

- Bounded queues between API and store workers  
- When queue full → shed, don’t OOM  
- Clients must honor 429 (SDK retries with jitter, capped)

### 3.7 Degradation modes

| Mode | Behavior | Risk |
|------|----------|------|
| A Normal | Full CAS reserve | — |
| B Read-only available | Soft deny new reserves | Lost conversion |
| C TTL extend only | Maintain holds, no new | Cart freeze |
| D Emergency safety bump | Increase safety stock | Under-sell |
| E Cell evacuate | Shift traffic | Capacity |

**Deal-breaker:** “degrade” by skipping CAS and always OK (oversell storm).

### 3.8 Recovery

1. Stop the bleed (shed, open breakers, disable prefetch).  
2. Stabilize store (scale, failover, kill bad deploy).  
3. Drain backlog with **admission ramp** (0→100% over minutes).  
4. Reconcile reservations vs orders (audit job).  
5. Postmortem + error budget consume.

### 3.9 Monitoring & SLOs

**SLOs**

| SLO | Target |
|-----|--------|
| Reserve availability | 99.99% |
| Reserve p99 latency | < 50 ms |
| Oversell incidents | ~0 (budgeted tiny BPS) |
| Idempotent replay success | 100% |

**Golden signals:** latency, traffic, errors, saturation (+ business: reserve_fail_rate, hot_asin_qps, breaker_open, shed_rate, ttl_lag).

---

## 4. Architecture Diagram

### 4.1 Hardened end-to-end

```text
Cart / Checkout / Promise
        |
        | (SDK: timeouts, retry jitter, caller_id)
        v
+-------------------------+
| Edge / Gateway          |
| authz, per-caller RPS   |
+-----------+-------------+
            v
+-------------------------+
| Admission Controller    |
| priority + load shed    |
+-----------+-------------+
            v
+-------------------------+
| IRS Fleet (cells)       |
| bulkheads per caller    |
| breaker to store        |
+-----+---------+---------+
      |         |
      v         v
Idempotency   Inventory Store (sharded by asin/fc)
 Store              |
                    +→ Hot-key lanes
                    +→ TTL workers (leased)

Events → Bus → Consumers (analytics, reconciliation)

Control Plane: toggles, safety_stock, kill switches, dashboards
```

### 4.2 Sequence: brownout

```text
Store p99 ↑ → breaker OPEN on Cart bulkhead
Checkout bulkhead still CLOSED (separate)
Admission sheds Cart reserves with 429
Checkout continues
On HALF_OPEN probe OK → gradual restore Cart
```

### 4.3 Sequence: hot ASIN

```text
Detector: ASIN qps > threshold
→ split logical shards / serialize writers
→ coalesce available() reads
→ optional per-ASIN rate limit with fair queue
Checkout reserved priority lane
```

### 4.4 Sequence: bad deploy recovery

```text
Error spike → auto rollback / toggle feature off
Shed to protect store
Reconciliation job: reservations vs order service
Ramp traffic 10%→50%→100%
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Conditional inventory:** never increase reserved past available.  
2. **Idempotency:** same key → same effect.  
3. **TTL progress:** expires are eventually released.  
4. **Single-writer home** per (asin, fc) inventory truth.  
5. **Caller isolation:** failure contained in bulkhead.  
6. **Timeout everywhere** (no unbounded wait).  
7. **Shed > melt** under overload.  
8. **No oversell degrade mode.**  
9. **Audit** of admin/break-glass.  
10. **Reconciliation** catches drift.

**Failure playbook (defend in interview)**

| Failure | Customer impact | Action |
|---------|-----------------|--------|
| Store outage | Can’t reserve | Fail closed; show retry; protect oversell |
| Hot deal | Latency/errors on ASIN | Hot-key playbook |
| Retry storm | Amplifies outage | Cap retries; 429 |
| TTL worker lag | Ghost reserved | Scale workers; lease reclaim |
| Poison confirm | Order stuck | DLQ + manual | 
| Region down | Local checkout fail | Cell failover if active-passive home |

### 5.2 Scalability

| Scale | Hardening move |
|-------|----------------|
| 10× | Timeouts, pools, breakers, basic hot-key cache for reads |
| 100× | Cells; per-caller budgets; adaptive concurrency (AIMD); chaos |
| 1,000× | Hierarchical admission; ASIN virtual nodes; maybe partitioned confirm |

**Adaptive concurrency (AIMD):**

```text
if latency < SLO: concurrency_limit += a
else: concurrency_limit *= b  (e.g. 0.9)
in-flight gated by limit
```

### 5.3 Maintainability & ownership

Amazon signal: **you own it in prod.**

| Artifact | Purpose |
|----------|---------|
| Runbooks | Hot ASIN, brownout, oversell investigation |
| Dashboards | SLO + business |
| Toggles | Disable prefetch, raise safety stock |
| Game days | Breaker drills |
| Error budgets | Freeze risky features when burned |
| Oncall rotation | Named |

### 5.4 Correctness under retries

```text
Reserve(key=cart_line_1, asin, qty, ttl)
Confirm(key=order_id)
```

Store idempotency records with result payload. TTL on idempotency keys > max client retry window.

### 5.5 Multi-region

**Chosen:** regional cells with **home cell** for inventory rows (asin+fc mapped to region of FC). Cross-region reserve rare; don’t active-active dual write.

**Deal-breaker:** multi-master invent counts without CRDT discipline (oversell).

### 5.6 Security

- Authn/z per caller  
- Quantity caps  
- Admin break-glass dual control  
- PII minimization (cart tokens not raw customer in IRS)

### 5.7 Testing the hardened system

- Load tests with hot-key skew (Zipf)  
- Chaos: latency injection to store  
- Differential tests on CAS logic  
- Replay production traffic shadows  

---

## 6. Wrap-Up

### 6.1 What we designed

A defense plan for **Inventory Reservation**: reverse-designed soft-hold CAS service, then hardened with **bulkheads, breakers, admission control, degradation without oversell, recovery ramps, and SLO-centric monitoring**.

### 6.2 Key decisions worth defending

1. Fail closed on inventory truth; never “always OK” degrade  
2. Per-caller bulkheads (Checkout ≠ Cart)  
3. Timeouts + shedding beat infinite retries  
4. Hot-key as first-class design  
5. Home-cell single-writer inventory  
6. Idempotency everywhere  
7. Ownership via runbooks, toggles, error budgets  

### 6.3 Risks & follow-ups

- Available() cache lying  
- Confirm/reserve atomicity with order service (saga)  
- Global SKU vs FC-level complexity  
- Extreme deal events  

### 6.4 Closer

> **Defend Inventory Reservation:** protect oversell invariants first, isolate blast radius second, shed to survive overload, recover with ramps—and prove it with SLOs you can operate at 3 a.m.

---

## 7. Deeper / Related Interview Questions

**Q1. How is this interview different from greenfield design?**

**A:** Start from existing constraints and production scars. Propose incremental hardening with measurable SLOs, not a clean-slate rewrite.

**Q2. What’s your top reliability risk?**

**A:** Latency contagion from the inventory store under hot-key skew, amplified by retries—fixed with timeouts, bulkheads, shedding, hot-key lanes.

**Q3. Fail open or closed?**

**A:** For reserve correctness, **fail closed** (deny reserve) rather than sell unconstrained. Fail open only for non-authoritative reads with clear UX.

**Q4. How do circuit breakers interact with bulkheads?**

**A:** Breakers per dependency **and** per bulkhead. Cart can be OPEN while Checkout remains CLOSED→healthy.

**Q5. How do you detect overload?**

**A:** Saturation signals: in-flight, queue depth, CPU, store p99, heap. Not just error rate (slow death).

**Q6. What do you shed first?**

**A:** Speculative/cart prefetch; preserve confirm & checkout reserve; always preserve release to avoid ghost holds if possible.

**Q7. Idempotency vs exactly-once?**

**A:** At-least-once clients + idempotent handlers. Exactly-once across network isn’t claimed.

**Q8. Hot ASIN strategy?**

**A:** Virtual shards, fair queues, read coalescing, priority lanes, maybe pre-split before big deals.

**Q9. How do you avoid retry storms?**

**A:** SDK: capped exponential backoff + jitter; honor Retry-After; idempotency keys; server 429 early.

**Q10. TTL worker falls behind—what happens?**

**A:** Available understated (under-sell). Scale workers, partition leases, alert on expiry lag histogram.

**Q11. How do you reconcile drift?**

**A:** Periodic job joins reservations, orders, inventory ledger; open tickets; never silent auto-decrement without rules.

**Q12. Why cells?**

**A:** Blast-radius containment; deploy safety; regional independence for FC-local inventory.

**Q13. Shared DB pool problem?**

**A:** One pool lets Cart starve Checkout. Separate pools/quotas per bulkhead.

**Q14. What metrics prove hardening worked?**

**A:** Reduced multi-caller brownouts, lower p99 during chaos, shed_rate correlated with survival, oversell BPS unchanged.

**Q15. Deal-breaker “improvements”?**

**A:** Cache authoritative reserved counts without write-through; multi-master writes; remove TTLs; infinite retries; shared unbounded queues.

**Q16. How do you capacity plan 10×?**

**A:** Load test Zipf traffic; size for hot keys not averages; reserve headroom for confirm priority.

**Q17. Interaction with shopping cart service?**

**A:** Cart owns UX/lines; IRS owns inventory truth. Cart must handle 429/timeouts without duplicate holds (idem keys).

**Q18. Confirm fails after payment?**

**A:** Saga/compensation with order service—out of MVP but mention: reserve extended, async confirm, break-glass.

**Q19. Security abuse—reserve all stock?**

**A:** Per-account quantity caps; fraud signals; rate limits; shorter TTL on suspicious sessions.

**Q20. Observability must-haves?**

**A:** Red/golden signals, breaker state, shed cause codes, hot ASIN top-N, oversell probes, version/deploy markers.

**Q21. Canary vs big bang deploy?**

**A:** Canary cells; auto rollback on SLO burn; feature toggles for risky logic.

**Q22. What belongs in a runbook?**

**A:** Symptoms, dashboards, toggles, escalate paths, customer messaging, recovery ramp, reconciliation.

**Q23. Adaptive concurrency vs static pool?**

**A:** Static under-utilizes or over-admits; AIMD tracks dependency health.

**Q24. How do you test breakers?**

**A:** Game day latency injection; verify Cart sheds while Checkout lives; verify recovery HALF_OPEN.

**Q25. Why not just “scale horizontally forever”?**

**A:** Hot keys and dependency saturation don’t dissolve with more stateless pods alone.

**Q26. Error budgets?**

**A:** If availability SLO burned, freeze features, focus reliability; Amazon-like operational maturity signal.

**Q27. Poison pill messages?**

**A:** For async paths: quarantine after N fails; don’t block partition.

**Q28. Clock skew on TTL?**

**A:** Server sets `expires_at`; workers use store time; clients don’t decide expiry truth.

**Q29. Read-your-writes for confirm?**

**A:** Confirm hits primary/home; don’t confirm against stale replica.

**Q30. What’s your 60-second pitch?**

**A:** Soft-reserve CAS inventory with TTL; harden via caller bulkheads, breakers, admission priority, hot-key controls, fail-closed degrade, recovery ramps, SLO ops.

**Q31. How do you prioritize hardening work?**

**A:** Rank by customer $ impact × likelihood: hot-key+timeouts first, then isolation, then fancy optimizers.

**Q32. Multi-tenant fairness among sellers?**

**A:** Marketplace ASINs still share IRS; fairness by caller and hot-key, not seller CPU—seller isolation is different system.

**Q33. Do you place IRS behind GraphQL BFF?**

**A:** Optional; still need server-side bulkheads—BFF doesn’t remove storms.

**Q34. Queue-everything design?**

**A:** Async reserve hurts checkout UX; keep sync path with strict timeouts; async for reconciliation/events.

**Q35. How to explain oversell bound?**

**A:** Races only within CAS conflicts; with single-writer home and correct conditions, oversell ≈ bug/ops error, not expected mode.

**Q36. Safety stock role?**

**A:** Absorbs uncertainty (damage, theft, late cancels); emergency raise is a degrade lever.

**Q37. Dependency on identity service?**

**A:** Cache tokens; short timeout; don’t let auth outage hold DB connections.

**Q38. What if leadership wants active-active global?**

**A:** Push back with oversell risk; offer cell-local + careful routing; CRDTs for counts are hard with reservations.

**Q39. Shadow mode for new CAS logic?**

**A:** Dual-run compare; don’t affect production; promote after parity.

**Q40. Biggest lesson as owner?**

**A:** Load averages lie; skew kills; retries amplify; isolation is a feature; oversell fail-closed is a product decision you must defend.

**Q41. How do you measure blast radius?**

**A:** % checkout sessions failing, % ASINs impacted, #cells unhealthy, $ GMV at risk.

**Q42. Backfill after outage?**

**A:** Don’t mass auto-reserve; let customers retry; reconcile confirmed orders carefully.

**Q43. Why separate idempotency store?**

**A:** Different TTL/access patterns; but can be colocated—defend either with clear key design.

**Q44. Thread per request vs event loops?**

**A:** Either OK with concurrency caps; problem is unbounded wait, not paradigm.

**Q45. How does HPA interact with shedding?**

**A:** Shed first (seconds); scale out next (minutes); prevent auto-scale flapping with cooldown.

**Q46. Client-side caching of reserves?**

**A:** Dangerous for truth; OK for display-only available with max-stale.

**Q47. What dashboards for exec vs oncall?**

**A:** Exec: availability, GMV impact, oversell. Oncall: breakers, hot keys, queue depth, deploy.

**Q48. Can IRS own “promise dates”?**

**A:** No—promise uses available+capacity elsewhere; IRS owns holds. Clear boundaries = maintainability.

**Q49. Interview red flag answers?**

**A:** “Just Kubernetes”; “eventual consistency fine for inventory”; “retry until success”; “global lock”.

**Q50. Final checklist before you say “production ready”?**

**A:** SLOs+alerts, breakers/bulkheads, hot-key tested, runbooks, toggles, canary, reconciliation, load test Zipf, fail-closed degrade verified.

**Q51. How to handle dependent failure of event bus?**

**A:** Core reserve path must not require bus ACK; emit async with outbox; analytics lag OK.

**Q52. Capacity of TTL sweep?**

**A:** Due-index per shard; N workers; lag SLO e.g. p99 < 5s.

**Q53. Version mismatches in CAS?**

**A:** Retry with backoff capped; if conflict storms on hot ASIN, fair queue.

**Q54. Why jitter on everyone retrying at minute boundaries?**

**A:** Avoid synchronized cart TTL refresh storms—stagger TTLs.

**Q55. Documenting architecture decisions?**

**A:** ADRs for fail-closed, cell home, bulkhead priorities—helps future you defend choices.

**Q56. Cost vs reliability trade?**

**A:** Extra replicas/pools cost money; cheaper than oversell + outage. Quantify.

**Q57. What changes at 1,000× besides shards?**

**A:** Organizational: platformized admission, stronger cells, dedicated deal war-rooms automation.

**Q58. How to onboard a new caller safely?**

**A:** New bulkhead with low quota; integrate SDK; load test; raise quota gradually.

**Q59. When is rewrite justified?**

**A:** After exhaustion of hardening (e.g., store engine fundamentally wrong)—rare; interview prefers harden-first.

**Q60. Summarize Amazon bar.**

**A:** Ownership, customer impact, mechanisms that work under stress, and honest trade-offs—not buzzwords.

---

## 8. Appendices

### Appendix A — API sketch

```text
POST /v1/reservations {key, asin, fc, qty, ttl_sec}
POST /v1/reservations/confirm {key, order_id}
POST /v1/reservations/release {key}
GET  /v1/availability {asin, fc}
```

### Appendix B — CAS pseudocode

```text
tx:
  row = read(asin, fc)
  avail = row.on_hand - row.reserved - safety
  if avail < qty: abort OUT_OF_STOCK
  row.reserved += qty
  row.version += 1
  write if version matches
  insert reservation(key, ...)
```

### Appendix C — Priority shedding matrix

| Load | Prefetch | Cart | Checkout | Confirm |
|------|----------|------|----------|---------|
| Green | allow | allow | allow | allow |
| Yellow | shed | limit | allow | allow |
| Red | shed | shed | limit | allow |
| Black | shed | shed | shed | allow if possible |

### Appendix D — SLO dashboard widgets

1. Success rate  
2. p50/p99 latency  
3. In-flight / pool usage  
4. Breaker states  
5. Shed counts by reason  
6. Hot ASIN top-10  
7. TTL lag  
8. Oversell probes  

### Appendix E — Runbook: store brownout

```text
1. Confirm store p99 / errors
2. Open Cart breaker if not auto
3. Enable shed mode YELLOW/RED
4. Page store owners
5. Disable nonessential deploys
6. When healthy: HALF_OPEN → ramp
7. Reconcile
```

### Appendix F — Progressive hardening roadmap

| Phase | Deliverables |
|-------|--------------|
| 0 | Timeouts, metrics |
| 1 | Caller bulkheads, 429 |
| 2 | Breakers, hot-key detection |
| 3 | Cells, adaptive concurrency |
| 4 | Chaos + error budgets |

### Appendix G — Interview 45-min checklist

1. Frame ownership + system purpose (4 min)  
2. Reverse-design APIs/state (7 min)  
3. Failure modes (6 min)  
4. Isolation/breakers/shed (10 min)  
5. Recovery + monitoring (7 min)  
6. Scale 10×–1000× (6 min)  
7. Trade-offs close (5 min)

### Appendix H — Worked overload math

```text
Timeout 50ms, 10K workers cluster
Max theoretical QPS if all wait full timeout: 10k / 0.05 = 200K
If useful work only 20K QPS with 5ms store, fine
If store 100ms, capacity collapses to 10k/0.1 = 100K theoretical but client timeouts fire—shed earlier at in-flight target
```

### Appendix I — Toggle catalog

| Toggle | Use |
|--------|-----|
| `prefetch_reserve` | Off in incidents |
| `safety_stock_bonus` | +N units |
| `cart_admit_pct` | Ramp |
| `cell_drain` | Evacuate |

### Appendix J — Event types

```text
RESERVED | RELEASED | CONFIRMED | EXPIRED | SHED | BREAKER_OPEN
```

### Appendix K — Common interviewer traps

| Trap | Answer |
|------|--------|
| Add more pods | Hot key remains |
| Cache reserved | Truth risk |
| Fail open | Oversell |
| Global lock | Won’t scale |
| Rewrite in Kafka | Sync checkout needs sync path |

### Appendix L — Reconciliation sketch

```text
For reservations CONFIRMED: must match order lines
For ACTIVE past TTL: should be EXPIRED
For reserved sum vs ledger: investigate deltas
```

### Appendix M — SDK requirements

```text
timeouts, retries<=2 with jitter, idempotency keys,
caller_id, honor 429, metrics from client side
```

### Appendix N — Hot-key playbook

```text
1. Identify ASIN
2. Enable dedicated lane / lower cart admit
3. Pre-split shards if planned
4. Comms with retail deal owners
5. Post-event resize
```

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Bulkhead | Isolated resource pool |
| Shed | Refuse work to survive |
| CAS | Conditional update |
| Home cell | Single-writer locality |
| Error budget | Allowed unreliability |

### Appendix P — Related Amazon systems

| System | Boundary |
|--------|----------|
| Cart | UX lines |
| Checkout | Order place |
| Promise | Dates |
| FC inventory ledger | On-hand truth source |

### Appendix Q — Sample narrative (use in interview)

> “I owned IRS for checkout soft-holds. Biggest Sev was a hot ASIN where shared pools let retries melt Dynamo and Checkout failed with Cart. We bulkheaded callers, put 50ms timeouts, priority shedding, and hot-key fair queues. Oversell stayed fail-closed. Recovery used admission ramps and reconciliation.”

### Appendix R — Threats to correctness

1. Dual writers  
2. Stale confirm  
3. TTL not firing  
4. Negative qty bugs  
5. Admin misuse  

### Appendix S — One-page hardened recap

```text
Auth → admit/shed → bulkheaded IRS → CAS store
Breakers + timeouts + hot-key lanes
Degrade: deny reserve, never fake OK
Recover: ramp + reconcile
Observe: SLOs + business metrics
```

### Appendix T — Closing template

> “I’d defend Inventory Reservation by keeping CAS fail-closed semantics, isolating callers and hot keys, failing fast with breakers, shedding low-priority load, and recovering with measured ramps—operated via SLOs, toggles, and runbooks I’d be proud to own oncall.”

---

*End of Defend & Harden Existing System (Inventory Reservation) system design.*
