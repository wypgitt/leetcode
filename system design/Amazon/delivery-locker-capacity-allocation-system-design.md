# System Design: Delivery Locker Capacity Allocation (Amazon)

> **Focus areas:** Locker sizes · Promised Delivery Date (PDD) · Soft/hard reservations · Expiration & reclaim · Cost minimization · Oversubscription · Marketplace fairness · Ops overrides  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Real arithmetic on capacity, spoilage, and last-mile cost; explicit deal-breakers  
> **Interview theme:** Amazon SDE III / L6 — logistics optimization with customer promise integrity

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

Goal: allocate **physical locker compartments** to inbound packages so Amazon meets **PDD**, maximizes successful pickup, and **minimizes cost** (failed delivery, reattempt, oversized spill to home delivery, idle capacity).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Capacity planning + reservation + assignment | Locker firmware / PIN UX alone |
| Decision | Which size, which locker site, when | Full carrier network design |
| Promise | PDD / pickup SLA integrity | Infinite inventory of lockers |
| Amazon lens | Cost, CX, utilization, ownership | Academic bin packing only |

**Related but separate:** `pickup-locker-software` (device/PIN/access). This doc owns **capacity allocation**.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What are we allocating? | Compartments by **size class** at locker sites | Size taxonomy + inventory |
| F2 | When reserved? | At order/checkout or at FC ship plan | Soft hold → hard reserve |
| F3 | PDD meaning? | Customer promised date for pickup-ready | Allocation must respect PDD |
| F4 | Package attributes? | Dims/weight, hazmat flags, cold-chain | Fit + constraint filters |
| F5 | Oversize? | Spill to home delivery or larger locker nearby | Costed fallback |
| F6 | Expiration? | Pickup window (e.g. 3 days) then reclaim | Timers + carrier return |
| F7 | Multi-package orders? | Prefer same site / adjacent compartments | Co-location objective |
| F8 | Reservation conflict? | Two ship plans → one slot | Atomic reserve / lease |
| F9 | Dynamic reallocation? | Yes before handoff to station | Rebinder with constraints |
| F10 | Ops override? | Mark compartment OOS, block site | Admin + audit |
| F11 | Forecasting? | Inbound demand by geo/day/size | Capacity planning job |
| F12 | Cost objective? | Min expected last-mile + failure cost | Explicit cost model |
| F13 | Fairness? | Prime vs non-Prime? usually promise-first | Policy knobs |
| F14 | Idempotency? | Ship plan retries safe | Reserve keys |

**MVP functional scope:**

1. Locker site + compartment inventory by size.  
2. Soft reservation at ship-promise time; hard reservation at sort/ship.  
3. Assignment algorithm: site + size respecting PDD.  
4. Expiration / reclaim pipeline.  
5. Fallback to alternate site or home delivery with cost.  
6. Ops OOS / blockage.  
7. Metrics: utilization, stockout, PDD miss, cost/package.  

**Out of MVP:**

- Full robotic locker internals  
- National carrier routing optimization (use as cost inputs)  
- Dynamic pricing of locker option to customers (can note)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Reserve latency | Checkout/ship path | p99 < 50–100 ms |
| N2 | Consistency | No double-book compartment | Strong for hard reserve |
| N3 | Availability | Degraded fallback OK | Prefer home delivery over wrong promise |
| N4 | Accuracy | Dims may be wrong | Tolerance + re-size flows |
| N5 | Scale | City → country → global | See scale table |
| N6 | Audit | Who reserved/released | Event log |
| N7 | Clock | Pickup expiry correct | NTP; site local time policy |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Customer selects Locker pickup → soft hold near address for PDD.  
2. FC ships → hard reserve compartment → label includes locker + size.  
3. Carrier densifies → injects package → compartment occupied → PIN notify.  
4. Customer picks up day 2 → release → capacity free.  
5. No pickup by expiry → reclaim → return-to-station → capacity free.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Soft hold expires before ship | Drop hold; re-reserve or fallback |
| Package doesn’t fit assigned size | Upsize if available; else reject to station/home |
| Site power outage | Mark site impaired; reallocate undelivered |
| Double ship-plan message | Idempotent reserve key |
| PDD today, site full | Costed alternate within radius or convert to home with messaging |
| Dims missing | Use historical ASIN dims + buffer |
| Cluster of apartments, one locker | Forecast + overflow policy |
| Hazmat not allowed | Constraint filter; never assign |
| Prime Day spike | Oversubscription policy with careful promises |
| Customer cancels | Release soft/hard per state machine |

### 1.4 Scales (Progressive)

| Metric | Baseline (metro) | 10× | 100× | 1,000× |
|--------|------------------|-----|------|--------|
| Locker sites | 1K | 10K | 100K | 1M |
| Compartments | 100K | 1M | 10M | 100M |
| Soft reserves / day | 200K | 2M | 20M | 200M |
| Hard reserves / day | 150K | 1.5M | 15M | 150M |
| Peak reserve QPS | 100 | 1K | 10K | 100K |
| Pickup scans / day | 140K | 1.4M | 14M | 140M |
| Expiry reclaim / day | 10K | 100K | 1M | 10M |
| Size classes | 5 | 6 | 8 | 10 |

**What each jump forces:**

- **10×:** Sharded inventory by geo; async forecast.  
- **100×:** Cell architecture per region; reservation leases; smarter overflow.  
- **1,000×:** Hierarchical capacity (cluster → site); ML demand; strict cost controllers.

### 1.5 Etc. (Constraints & Assumptions)

- Compartments are discrete size classes (XS/S/M/L/XL), not continuous 3D packing in MVP (optional deep dive).  
- **Never** confirm locker pickup if hard capacity cannot support PDD with high probability.  
- Cost includes: failed first delivery, locker reattempt, home delivery delta, customer apology, capacity idle opportunity.

**Scope statement:**

> Design Amazon locker **capacity allocation**: size-aware reservations tied to PDD, expiration/reclaim, and cost-minimizing fallback—from one metro (~100 reserve QPS) through 10× / 100× / 1,000× global sites with sharded inventory and strong no-double-book guarantees.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Soft reserve / quote | 100 | 100K | Checkout / promise |
| Hard reserve | 50 | 50K | Ship / sortation |
| Release / pickup | 40 | 40K | Customer pickup |
| Expiry scanner | 5 | 5K | Worker sweep |
| Ops mutate OOS | low | hundreds | Admin |
| Forecast jobs | batch | batch | Hourly/daily |

### 2.2 Capacity math (example metro)

```text
1,000 sites × 100 compartments = 100,000 compartments
Size mix: XS 30%, S 30%, M 25%, L 10%, XL 5%

Average dwell = 1.5 days (inject → pickup/expire)
Theoretical throughput ≈ 100,000 / 1.5 ≈ 66,700 packages/day
If demand 80,000/day → utilization pressure; need overflow policy

Unit check: 1e5 / 1.5 ≈ 6.67e4/day ✓
```

### 2.3 Reservation state storage

```text
Active reservation record ~300–500 B
Baseline concurrent soft+hard ≈ 200K × 400 B ≈ 80 MB (trivial)
1,000×: 200M × 400 B = 80 GB → shard by site/region
Event log 10× larger for audit
```

### 2.4 Cost model sketch

```text
C = C_home_delta + C_failed_attempt + C_expire_return + C_apology + C_idle

Example:
Home delivery delta vs locker: +$1.20
Failed locker inject reattempt: $2.50
Expire return: $3.00
Apology coupon expected: $1.00 * P(complaint)

Objective: minimize E[C] subject to P(PDD_miss) ≤ budget (e.g. 0.1%)
```

### 2.5 Oversubscription

```text
If P(no-show/cancel) = 8% before inject, soft holds may oversubscribe 1/(1-0.08)≈1.087
Hard reserves at inject time should NOT oversubscribe physical slots
(Unless multi-tenant time-slicing same day with high confidence — risky)
```

### 2.6 Critical bottlenecks

1. Hot downtown sites (skew)  
2. Wrong dims → size thrash  
3. Soft-hold hoarding without TTL  
4. Cross-site transaction complexity  
5. PDD promise vs real capacity race  
6. Expiry worker lag → phantom full  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Site (id, geo, status, constraints)
Compartment (id, site_id, size_class, status: FREE|RESERVED|OCCUPIED|OOS)
SizeClass (XS…XL, max_dims, max_weight)
SoftReservation (order_id, site_id, size, pdd, expires_at, state)
HardReservation (package_id, compartment_id, lease)
Package (id, dims, weight, pdd, constraints)
AssignmentDecision (site, size, cost_estimate, fallback_chain)
```

### 3.2 Promise → soft → hard state machine

```text
QUOTE → SOFT_HELD → HARD_RESERVED → OCCUPIED → RELEASED
                 \→ SOFT_EXPIRED
                 \→ FALLBACK_HOME
HARD_RESERVED → RELEASED (cancel)
OCCUPIED → EXPIRED_RECLAIM → IN_RETURN
```

**Deal-breaker:** treating checkout selection as hard forever without TTL (capacity hoarding).

### 3.3 Sizing policy

| Strategy | Pros | Cons |
|----------|------|------|
| Exact size only | Simple | High reject |
| Allow upsize | Higher accept | Wastes large slots |
| 3D bin pack multi-package | Dense | Complexity / time |

**MVP choice:** size class fit + **controlled upsize** when E[cost] lower than fallback home.

```text
feasible = sizes where package_dims ≤ size.max * (1+tol)
pick argmin cost(site, size) among feasible
```

### 3.4 Site selection objective

```text
score = w1*distance_cost + w2*pdd_risk + w3*utilization_penalty
      + w4*colocation_bonus + w5*operational_risk
pick min score among candidates in radius R
```

**PDD risk:** probability site cannot accept by PDD given forecast occupancy.

### 3.5 Reservation algorithm (hard)

```text
Begin Tx (site shard):
  find FREE compartment matching size (or upsize policy)
  CAS status FREE → RESERVED with package_id, version
  write reservation record idempotency_key=package_id
Commit
On conflict: retry alternate compartment / size / site
```

Shard by `site_id` so most transactions are single-shard.

### 3.6 Expiration & reclaim

```text
OCCUPIED + now > pickup_deadline → mark EXPIRE_PENDING
Ops/carrier reclaim → IN_RETURN → compartment FREE
Notify customer; update promise systems
```

Sweeper: time-index / buckets per minute per site shard.

### 3.7 Cost minimization controller

Online decisions use approximate costs; offline tunes weights.

| Decision | Cost drivers |
|----------|--------------|
| Upsize local | Waste large capacity opportunity cost |
| Alternate site +0.8 mi | Customer friction + walk cost proxy |
| Convert to home | Delivery delta |
| Delay to next day | PDD miss penalty (usually forbidden) |

**Amazon practicality:** missing PDD is often **worse** than paying home delivery delta—encode as hard constraint then minimize cost.

### 3.8 Forecasting & capacity planning

```text
For each (site, day, size):
  demand_hat = f(seasonality, local orders, events)
  capacity = compartments * turnover_hat
  if demand_hat > capacity * safety:
    throttle locker option in checkout OR stage mobile lockers OR adjust promise
```

### 3.9 Trade-offs table

| Topic | Choice | Deal-breaker |
|-------|--------|--------------|
| Consistency | Strong per site for hard reserve | Eventually consistent double-book |
| Soft holds | TTL + oversubscribe lightly | Infinite soft holds |
| Geography | Geo shard / regional cells | Global lock on all lockers |
| Sizing | Classes + upsize | Perfect 3D NP-hard on checkout |
| Fallback | Home delivery | Silent fail / stuck promise |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Checkout / Promise Service
        |
        | quoteLocker(order, addr, pdd, package_est)
        v
+---------------------------+
| Allocation API            |
| (scoring + soft hold)     |
+-------------+-------------+
              |
              | shard by geo / site
              v
+---------------------------+     +------------------+
| Site Inventory Services   |---->| Reservation DB   |
| (FREE/RESERVED/OCCUPIED)  |     | (per cell)       |
+-------------+-------------+     +------------------+
              ^
              | hard reserve at ship
+-------------+-------------+
| FC / Sort / Ship Plan     |
+-------------+-------------+
              |
              v
+---------------------------+
| Carrier Inject / Pickup   |
| Events                    |
+-------------+-------------+
              |
              v
+---------------------------+     +------------------+
| Expiry / Reclaim Workers  |---->| Notifications    |
+---------------------------+     +------------------+

Offline:
  Demand Forecast → Capacity Controller → Checkout eligibility knobs
  Cost Model Trainer → weights for scorer
```

### 4.2 Sequence: soft hold at checkout

```text
Checkout → Allocation.quote
  candidates = sites in radius
  filter constraints (hazmat, disabled)
  score by cost + pdd_risk
  try softHold(best, ttl=2h, key=order_id)
  return locker option + fee/promise
If softHold fails all → omit locker or show home-only
```

### 4.3 Sequence: hard reserve at ship

```text
ShipPlan(package) → Allocation.hardReserve
  if softHold valid → upgrade to hard compartment
  else re-score sites → CAS FREE compartment
  if fail → fallback home + rewrite label path
Emit Assigned(package, site, compartment, size)
```

### 4.4 Sequence: expiry

```text
Sweeper → due OCCUPIED
→ ExpiryTask → notify → carrier reclaim workflow
→ on empty scan: FREE + metrics(expire_count)
```

### 4.5 Hot site isolation

```text
Site shard overloaded → shed soft quotes first
Preserve hard reserves & pickup releases
Checkout sees reduced locker availability (honest)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **No double-book:** ≤1 active HARD/OCCUPIED owner per compartment.  
2. **PDD honesty:** don’t confirm locker if predicted fail > ε.  
3. **Soft TTL:** soft holds expire and release.  
4. **Idempotent reserve** by package_id / order_id.  
5. **Constraint safety:** hazmat/cold never assigned illegally.  
6. **Auditability:** every transition evented.  
7. **Fallback path exists** when locker impossible.  
8. **Expiry progresses** (no zombie OCCUPIED forever).  

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Site DB partition | Fail quotes for that shard; hard reserve retry/fallback |
| Wrong dims at inject | Upsize flow; station exception desk |
| Mass expiry backlog | Priority reclaim oldest; temp stop new soft holds |
| Ghost RESERVED (worker crash) | Lease timeout → FREE if not confirmed |
| Inventory drift vs physical | Cycle count reconciliation jobs |
| Clock skew expiry | Site-local deadline stored as absolute UTC + policy |

**Degradation**

| Mode | Behavior |
|------|----------|
| Forecast stale | Conservative capacity (lower oversubscribe) |
| Scorer down | Nearest-site greedy + home fallback |
| Notify down | Still reclaim; retry notify |

### 5.2 Scalability

**Sharding:** `cell = region`, within cell shard by `site_id` (hash) or geo-hash sticky.

**10× / 100× / 1,000×**

| Scale | Move |
|-------|------|
| 10× | Per-metro services; Redis/DB inventory |
| 100× | Regional cells; stream events; forecast service |
| 1,000× | Hierarchical cluster capacity; adaptive oversubscribe; edge quote cache of availability sketches |

**Availability sketches for quotes:**

```text
For fast quote: cached free_count[site][size] with short TTL
For hard reserve: always authoritative CAS
Accept rare quote→reserve miss → fallback
```

### 5.3 Maintainability

- Clear ownership: **Locker Capacity** team vs **Locker Device** team vs **Last Mile**.  
- Size taxonomy versioned (adding XXL).  
- Cost model parameters in config with experiment hooks (ties to A/B platform).  
- Simulation env for Prime Day.  
- Runbooks: site outage, snowstorm surge, device brick.

### 5.4 Allocation algorithm detail

**Candidate generation**

```text
1. Geo index: sites within R (e.g. 1.5–5 km policy)
2. Filter status=ACTIVE, constraints OK
3. For each site, best size = min feasible class with free_soft/free_hard
4. Score and pick top-K to try
```

**Try loop**

```text
for candidate in ranked:
  if soft: tryHold(candidate, ttl)
  if hard: tryCAS(candidate)
  on success return
fallback home
```

**Colocation:** if order has multiple packages, try same site with multi-CAS (same shard) or accept split with penalty.

### 5.5 PDD risk model (practical)

```text
occupancy_hat(pdd) = current_committed + inbound_forecast - outbound_forecast
p_fail = sigmoid(occupancy_hat / capacity - 1)
reject locker option if p_fail > threshold
```

Conservative under uncertainty—Amazon promise integrity > utilization bragging.

### 5.6 Monitoring

| Metric | Why |
|--------|-----|
| Utilization by size | Imbalance → resize fleet |
| Soft hold expire rate | Hoarding / TTL tune |
| Quote→hard success | Sketch accuracy |
| PDD miss | Customer promise |
| Fallback-to-home rate | Capacity gaps |
| Expiry rate | Friction / reminders |
| Cost/package | Business KPI |
| Double-book attempts | Serious bug |

### 5.7 Security & abuse

- Authz on ops OOS  
- Prevent reservation spam (rate limits per order/account)  
- Don’t leak exact empty maps broadly (theft/risk)—exposing availability carefully  

---

## 6. Wrap-Up

### 6.1 What we designed

A locker **capacity allocation** system: size-aware **soft/hard reservations**, **PDD-honest** quoting, **expiration/reclaim**, and **cost-minimizing** fallbacks, sharded by site/region for global scale.

### 6.2 Key decisions worth defending

1. Soft TTL + hard CAS (no hoarding, no double-book)  
2. PDD as constraint, cost as objective  
3. Size classes + controlled upsize  
4. Site-shard strong consistency  
5. Cached sketches for quote, authoritative hard reserve  
6. Home delivery fallback over false promise  
7. Explicit ownership across capacity vs device vs last mile  

### 6.3 Risks & follow-ups

- Dims quality  
- Extreme skew downtown  
- Multi-package atomicity  
- Continuous 3D packing later  
- Mobile / temporary lockers  

### 6.4 Closer

> **Amazon Locker Capacity:** keep promises first, then minimize last-mile cost—reserve with leases, expire cleanly, fall back honestly, shard by site.

---

## 7. Deeper / Related Interview Questions

**Q1. Soft vs hard reservation—why both?**

**A:** Checkout needs a probabilistic hold early; physical commitment should happen when package is real. Soft TTL prevents hoarding; hard CAS prevents double-book.

**Q2. How do you avoid double-booking?**

**A:** Compartment row version / CAS in a site-local strongly consistent store. Idempotency key = package_id. Never rely on “read free count then write” without CAS.

**Q3. What’s the objective function?**

**A:** Minimize expected cost (home delta, reattempts, expiry returns, apology) subject to PDD miss ≤ budget. Not pure max utilization.

**Q4. Why size classes instead of raw 3D?**

**A:** Latency and ops simplicity at quote time. 3D packing can enhance station inject, but checkout needs fast class fit + upsize policy.

**Q5. How does PDD enter allocation?**

**A:** Forecast occupancy at PDD; if risk high, don’t offer locker (or offer alternate day/site). Never spend capacity you won’t have.

**Q6. Oversubscription safe?**

**A:** Soft layer only, based on cancel/no-ship rates, with safety margin. Hard physical slots not oversubscribed.

**Q7. Hot site thrashing?**

**A:** Utilization penalty in score; throttle checkout eligibility; suggest nearby sites; expand capacity planning.

**Q8. Package doesn’t fit at inject?**

**A:** Exception path: upsize CAS, else divert to counter/home; feed dims learning loop.

**Q9. How do expirations scale?**

**A:** Per-shard time wheels / due indexes; workers pull due set; avoid `SELECT * WHERE expiry < now` globally.

**Q10. Multi-package same order?**

**A:** Prefer same site; multi-compartment transaction on one shard; if impossible, minimize split cost or force home.

**Q11. Consistency across sites for one order?**

**A:** Avoid 2PC across sites. Pick primary site first; only split with compensation logic.

**Q12. What if allocation service is down?**

**A:** Degrade: hide locker option or route new packages home; don’t invent reservations.

**Q13. Cost of idle XL compartments?**

**A:** Opportunity cost in upsize decisions—upsizing XS into XL may be expensive at peak. Dynamic opportunity cost from shadow prices.

**Q14. Forecast wrong—what happens?**

**A:** Conservative thresholds; realtime free_count feedback; incident response to convert promises early.

**Q15. How is this different from hotel room allocation?**

**A:** Similar yield ideas, but coupled to logistics PDD, carrier inject uncertainty, and physical dims—plus Amazon-scale geo sharding.

**Q16. Idempotent ship retries?**

**A:** hardReserve(package_id) returns existing assignment if present.

**Q17. Customer changes pickup site after ship?**

**A:** Policy-limited: release+re-reserve if not yet injected; after inject, usually locked.

**Q18. Security of compartment maps?**

**A:** Internal systems only; customer sees site + PIN, not which adjacent cells empty.

**Q19. Cold chain?**

**A:** Separate constrained inventory pool; different expiry; often smaller network.

**Q20. Prime Day strategy?**

**A:** Pre-block capacity for promised demand; reduce soft oversubscribe; surge home fallback; staff reclaim.

**Q21. Metric you’d show VP?**

**A:** PDD miss BPS, fallback rate, cost/package, expiry %, utilization by size, quote→inject success.

**Q22. Deal-breaker designs?**

**A:** Global mutex; no TTL soft holds; eventually consistent double-book; maximize fill without PDD constraint; no home fallback.

**Q23. How to model distance cost?**

**A:** Walk-meters → CX friction $ proxy + accessibility; not only haversine—parking/building access matters in policy tables.

**Q24. Reservation leases?**

**A:** HARD_RESERVED with lease until inject confirm; if inject never comes, lease expires → FREE.

**Q25. Interaction with inventory of products?**

**A:** Orthogonal: product inventship promises interact via promise engine; locker capacity is a constraint in promise.

**Q26. Geo replication of site DB?**

**A:** Single-writer home for site shard; read replicas for analytics. Cross-region assign rare.

**Q27. Can we reassign after hard reserve before inject?**

**A:** Yes, binder job may optimize densification if state still RESERVED; must be atomic move.

**Q28. Fraudulent holds?**

**A:** Rate limit; require order authenticity; cancel releases; anomaly detection on hold patterns.

**Q29. Why reclaim latency matters?**

**A:** Phantom OCCUPIED reduces capacity → false stockouts → unnecessary home delivery spend.

**Q30. Simulate capacity?**

**A:** Discrete-event sim with demand traces; tune oversubscribe & upsize thresholds before peak events.

**Q31. ASIN dim catalog wrong—system impact?**

**A:** Buffer margins; learn residuals; quarantine pathological ASINs from locker eligibility.

**Q32. Partial site outage (half modules down)?**

**A:** Mark compartments OOS; recompute free_count; optionally stop new soft holds if below threshold.

**Q33. How to explain upsize to cost auditors?**

**A:** Show E[C_upsize] < E[C_home] with opportunity cost term; log decision features.

**Q34. Queue at popular lockers?**

**A:** CX externalities; may include congestion penalty in score using pickup scan rates.

**Q35. Data model for compartment?**

**A:** Key (site_id, compartment_id), size, status, version, package_id nullable, updated_at.

**Q36. Batch reclaim vs realtime?**

**A:** Realtime event when deadline hits + safety sweeper. Dual path prevents missed TTL.

**Q37. Cross-border lockers?**

**A:** Cells by country; customs constraints; usually separate networks.

**Q38. Mobile lockers / seasonal?**

**A:** Sites with temporary capacity calendar; forecast includes pop-ups.

**Q39. What belongs in LLD vs HLD here?**

**A:** HLD: state machine, sharding, cost/PDD. LLD: CAS API, tables, sweeper, device events—point to locker software doc for PIN path.

**Q40. Ownership who is paged on double-book?**

**A:** Locker Capacity oncall—this is a Sev-ish correctness bug; device team only if scan events duplicate.

**Q41. How do you price opportunity cost of XL?**

**A:** Shadow price ≈ expected overflow cost if XL scarce; update hourly from dual of capacity constraints in planning LP.

**Q42. Linear program for planning?**

**A:** Offline: allocate expected demand to sites/sizes minimizing cost with capacity constraints. Online: greedy score approximating dual prices.

**Q43. What if carrier arrives out of order?**

**A:** Package has reserved compartment; inject scans package→compartment. Order of trucks irrelevant if reservations held.

**Q44. Cancellation storms?**

**A:** Burst releases; OK for capacity. Soft-hold churn may stress DB—batch writes / events.

**Q45. Read-your-writes for ops dashboard?**

**A:** Ops reads from site primary; analytics can lag.

**Q46. Privacy?**

**A:** Package↔customer mapping in order systems; capacity service can store opaque package tokens.

**Q47. Testing strategy?**

**A:** Property tests: no double-book; soft TTL releases; idempotent hard reserve; chaos site kill.

**Q48. When to refuse upsize?**

**A:** When XL utilization high and home delta cheap; or when XL needed for guaranteed large inbound.

**Q49. Connection to A/B platform?**

**A:** Experiment with reminder timing (expiry rate), radius R, upsize aggressiveness—guardrail PDD miss.

**Q50. Summarize in 3 sentences.**

**A:** Soft-hold with TTL for promises, hard CAS for physical truth, PDD as constraint. Score sites/sizes by expected cost with forecast risk. Fall back to home rather than break promises; shard by site for scale.

**Q51. Inventory reconciliation?**

**A:** Periodic compare device-reported OCCUPIED vs DB; open tickets on drift; auto-safe FREE only with dual evidence.

**Q52. Why not Mongo eventual for compartments?**

**A:** Double-book risk unacceptable; use strongly consistent per-shard store (SQL/Spanner/Dynamo conditional writes).

**Q53. DynamoDB sketch?**

**A:** PK=site_id, SK=compartment_id; condition attribute_not_exists or version match; GSI on status+size for find-free (careful hot partitions—prefer size-specific free lists).

**Q54. Free-list design?**

**A:** Maintain FREE sets per (site, size) for O(1) pop; repair on drift.

**Q55. How large is radius R?**

**A:** Policy by locale (urban 0.5–1.5 km, suburban larger); product UX research + cost.

**Q56. Missed PDD severity?**

**A:** Often Sev for promise systems; capacity must page when miss BPS spikes.

**Q57. Can AI dims scanning help?**

**A:** Yes at FC—feed allocation; still keep buffers.

**Q58. Interview whiteboard order?**

**A:** Sizes & states → soft/hard → PDD constraint → cost score → shard → expiry → scale jumps.

**Q59. Biggest business trade-off?**

**A:** Utilization vs promise integrity vs CX walking distance. Amazon typically ranks promise/CX above squeezing last % utilization.

**Q60. Final deal-breakers?**

**A:** No TTL; eventual double-book; ignore PDD; no fallback; global lock; maximize fill only.

---

## 8. Appendices

### Appendix A — API sketch

```text
POST /v1/quote   { order_id, addr, pdd, packages[] }
POST /v1/soft-hold { order_id, site_id, size, ttl }
POST /v1/hard-reserve { package_id, order_id? }
POST /v1/release { package_id, reason }
POST /v1/ops/oos { compartment_id, reason }
```

### Appendix B — State machine

```text
FREE → SOFT (logical count) → HARD(RESERVED) → OCCUPIED → FREE
                 ↘ expired
HARD → FREE (cancel/lease expiry)
OCCUPIED → FREE (pickup)
OCCUPIED → EXPIRE → FREE (reclaim)
FREE → OOS → FREE
```

### Appendix C — Worked capacity example

```text
Site: 80 compartments (S=30,M=30,L=15,XL=5)
Dwell 1.5d → capacity ≈ 53.3 pkg/day
Inbound forecast 60 → shortfall 6.7
Actions: throttle option 10%, overflow to site 800m away, or home
```

### Appendix D — Cost numeric example

```text
Upsize S→M: opportunity $0.40, CX $0
Alternate site: CX $0.70
Home: $1.20
Choose upsize if M not scarce; else alternate if CX acceptable; else home
```

### Appendix E — Event log schema

```json
{"type":"HARD_RESERVED","package_id":"P","site":"S","comp":"C","ts":"...","actor":"ship_plan"}
```

### Appendix F — Interview 45-min checklist

1. Clarify PDD, sizes, soft/hard (6 min)  
2. State machine + invariants (8 min)  
3. Scoring/cost (7 min)  
4. Sharding/CAS (7 min)  
5. Expiry + fallback (5 min)  
6. Scale + Prime Day (5 min)  
7. Metrics/ownership (4 min)

### Appendix G — Progressive scale cheatsheet

| Scale | Sites | Reserve QPS | Upgrade |
|-------|-------|-------------|---------|
| Base | 1K | 100 | Single metro cluster |
| 10× | 10K | 1K | Geo shards |
| 100× | 100K | 10K | Regional cells |
| 1,000× | 1M | 100K | Hierarchical sketches |

### Appendix H — Free-list repair

```text
On CAS failure storm:
  rebuild FREE set from compartment table for site
  metric repair_count
```

### Appendix I — Constraints catalog

| Constraint | Example |
|------------|---------|
| Hazmat | Lithium limits |
| Temperature | Grocery totes |
| Weight | Door mechanism |
| Accessibility | ADA compartments subset |

### Appendix J — Failure injection

1. Kill site primary mid-CAS  
2. Inject dim mismatch  
3. Sweeper delay 1h  
4. Soft-hold thundering herd  
5. Split-brain clock  

### Appendix K — Ownership map

| Concern | Owner |
|---------|-------|
| Allocation correctness | Locker Capacity |
| PIN/access | Locker Device |
| Inject transport | Last Mile |
| Promise messaging | Promise/CX |

### Appendix L — SQL sketch

```sql
compartments(site_id, compartment_id, size, status, version, package_id)
reservations(package_id PK, site_id, compartment_id, state, pdd, expires_at)
soft_holds(order_id PK, site_id, size, expires_at)
```

### Appendix M — Quote availability sketch

```text
Redis: free:site123:M = 7 (TTL 30s)
Quote uses sketch; Hard uses DB CAS
```

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| PDD | Promised Delivery Date |
| Soft hold | Non-exclusive/time-limited intent |
| Hard reserve | Physical compartment CAS |
| Upsize | Larger class than minimum fit |
| Reclaim | Remove expired package |

### Appendix O — Related systems

| System | Link |
|--------|------|
| Pickup locker software | Device/PIN |
| Promise engine | Customer dates |
| Last mile | Carrier execute |
| A/B platform | Policy experiments |

### Appendix P — Risk register

| Risk | Mitigation |
|------|------------|
| Dims wrong | Learning + buffers |
| Skew | Throttle + expand |
| Drift | Reconciliation |
| Overpromise | PDD risk gate |

### Appendix Q — Math: utilization vs throughput

```text
throughput ≈ N_comp / dwell
If expiry rises, dwell↑ → throughput↓ → vicious cycle
Reminders / shorter windows (CX trade) can stabilize
```

### Appendix R — One-page recap

```text
Quote with PDD risk → soft TTL hold → hard CAS at ship
Score cost under promise constraint → fallback home
Expire/reclaim to protect capacity → shard by site
```

### Appendix S — Sample interviewer dialogue

> **I:** Do we optimize utilization?  
> **You:** Utilization is instrumental; objective is cost under PDD/CX constraints. I’d rather underfill than miss promises.

### Appendix T — Closing template

> “I’d separate soft holds from hard CAS reservations, treat PDD as a hard honesty constraint, minimize expected last-mile cost with size upsize and nearby fallbacks, expire cleanly, and shard inventory by site—degrading to home delivery rather than double-booking or lying about capacity.”

---

*End of Delivery Locker Capacity Allocation system design.*
