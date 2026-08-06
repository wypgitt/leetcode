# System Design: Discounts & Coupons Stacking (Amazon Pricing/Promotions)

> **Focus areas:** Promotion catalog · Eligibility · Stacking rules engine · Deterministic price calc · Idempotent apply · Fraud/abuse · Auditability · Checkout consistency · Experiments  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Deterministic totals, money-safe invariants, split browse vs checkout QPS, explicit deal-breakers  
> **Interview theme:** Amazon SDE III / L6 — **Retail Promotions** — correct stacking under Prime Day load with customer trust

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

Goal: **bound promotions**—who can stack which coupons/discounts, how we compute a **deterministic** payable total, and how we prevent abuse while staying fast on PDP/cart/checkout.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Eligibility + stacking + price explanation | Full catalog search |
| Planes | Read pricing vs reserve/commit at checkout | Random client-side discounts |
| Success | Correct total + explainability + fraud bounds | Max discount always |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Promotion types? | % off, fixed off, BOGO, free shipping, coupons, Prime deals | Typed promo engine |
| F2 | Stacking? | Rules: exclusivity groups, priority, max discount caps | Deterministic rule compiler |
| F3 | Surfaces? | PDP badge, cart estimate, checkout commit | Same engine library; different durability |
| F4 | Coupons? | Single/multi-use codes; personal coupons | Redemption ledger |
| F5 | Eligibility? | ASIN, category, seller, Prime, geo, new customer | Predicate eval + indexed candidates |
| F6 | Budget? | Seller/Amazon funded; campaign caps | Budget reservation |
| F7 | Explainability? | Line-item discount breakdown | Audit trail per calculation |
| F8 | Currency/tax? | Discount before/after tax policy by marketplace | Marketplace policy pack |
| F9 | Fraud? | Coupon stuffing, reseller abuse | Risk hooks + velocity |
| F10 | Experiments? | Promo messaging A/B | Sticky assignment; don’t break money |
| F11 | Clipping? | Optional clip coupon UX | User promo wallet |
| F12 | Returns? | Reversals restore coupon per policy | Compensating redemptions |

**MVP functional scope:**

1. Promo catalog + versioned stacking policy.  
2. Candidate generation for cart contents.  
3. Deterministic stacking evaluation → payable total + breakdown.  
4. Checkout **reserve → commit** for limited coupons/budgets.  
5. Idempotent apply by `checkout_attempt_id`.  
6. Audit log of calculation inputs/outputs.  
7. Basic fraud velocity checks.

**Out of MVP:**

- Arbitrary Turing-complete promo scripts in sellers’ hands  
- Cross-marketplace coupon roaming without cells  
- Perfect global budget exactness under partition (document approx vs reserved)  
- Full promotions ML personalization platform

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | PDP/cart latency | Interactive | p99 < 50–100ms estimate |
| N2 | Checkout commit | Money-critical | p99 < 200–300ms + strong correctness |
| N3 | Determinism | Same inputs → same total | Golden tests; version pin |
| N4 | Consistency | No oversell coupon uses | Single-writer redemption home |
| N5 | Availability | Degrade badges before wrong price | Fail closed on checkout calc errors |
| N6 | Audit | Reconstruct any charged total | Immutable calc log |
| N7 | Scale | Prime Day 100× | See table |
| N8 | Abuse | Coupon fraud bounded | Risk score gate |

### 1.3 Cases

**Happy paths**

1. Cart with Prime deal + coupon → stack rules allow → total shown → checkout commits redemptions.  
2. Exclusive coupon blocks percentage deal → explanation shows why.  
3. Coupon exhausts mid-checkout → clear error; suggest remove code.  
4. Return restores single-use coupon if policy allows.  
5. Budget hit → promo stops appearing; in-flight reserves honored until TTL.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double checkout submit | Idempotency → one commit |
| Race two users last coupon | One wins reserve; other fails |
| Clock skew on promo window | Server time SoT; buffer |
| Stale PDP badge vs checkout | Checkout recompute authoritative |
| Stacking cycle / ambiguity | Deterministic priority sort; golden tests |
| Negative total | Clamp + alert; never pay customer |
| Seller cancels promo | Version bump; checkout uses pinned snapshot |
| Fraud ring | Risk decline; step-up auth |
| Partial shipment tax | Marketplace policy pack |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active promos | 100K | 1M | 10M | 100M |
| Cart price QPS | 20K | 200K | 2M | 20M |
| Checkout commit QPS | 2K | 20K | 200K | 2M |
| Coupon redemptions / day | 20M | 200M | 2B | 20B |
| Avg ASINs / cart | 3 | 3 | 3 | 3 |
| Avg candidate promos / cart | 20 | 30 | 50 | 80 |
| Rule eval CPU µs / cart | 500 | 500 | 400 | 300 |
| Fraud checks /s | 2K | 20K | 200K | 2M |

**What each jump forces:**

- **10×:** In-memory promo index; compiled rule packs; Redis coupon counters.  
- **100×:** Marketplace cells; promo shard by ASIN/category; reserve TTLs; read replicas for browse.  
- **1,000×:** Hierarchical candidate retrieval; edge badge caches; approximate browse budgets; SW redemption cells.

### 1.5 Constraints & Assumptions

- Money path fail-closed.  
- Browse badges may be eventually consistent; checkout recomputes.  
- Amazon marketplace funding (Amazon vs seller) must be accounted.  
- Repeat: *“Deterministic stacking engine with reserve/commit redemptions and auditable totals.”*

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | QPS nature | Consistency |
|-------|------------|-------------|
| Badge/PDP | Extremely high, cacheable | Eventual OK |
| Cart estimate | High | Read-your-writes nice |
| Checkout commit | Lower but critical | Strong |

### 2.2 Compute

At 2M cart QPS × 50 candidates × 10µs ⇒ huge if naive. Need inverted indexes (ASIN→promos), prefiltered eligibility, compiled rules, caching of non-personalized layers.

### 2.3 Coupon counters

Hot coupon codes = hot keys. Shard by `coupon_id`; use striped counters or hierarchical budgets for mega-coupons; reserve with TTL.

### 2.4 Cost

Track $/1K cart evaluations and redemption conflict rate. Caching badges is the #1 browse cost lever.

---

## 3. High-Level Design

### 3.1 Components

1. **Promo Catalog** — versioned promotions + funding.  
2. **Stacking Policy Compiler** — exclusivity groups, priorities, caps → deterministic program.  
3. **Candidate Index** — ASIN/category/segment → promo ids.  
4. **Pricing Engine Library** — pure function `(cart, promos, userctx, policy_ver) → quote`.  
5. **Coupon Service** — codes, limits, reserve/commit/release.  
6. **Budget Service** — campaign spend caps.  
7. **Checkout Orchestrator** — pin versions; reserve; place order; commit.  
8. **Audit Log** — inputs hash + breakdown.  
9. **Fraud/Risk** — velocity, device, coupon stuffing.  
10. **Experiment hooks** — messaging only unless explicitly money-safe.

### 3.2 Quote vs commit

```text
Browse/Cart:  estimate_quote()  // no durable side effects
Checkout:     pin → reserve → place_order → commit | release
```

### 3.3 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Authority | Server recompute at checkout | Trust client total |
| Stacking | Deterministic compiled policy | Undefined “best discount” race |
| Coupons | Reserve/commit | Best-effort decrement |
| Badges | Cache OK | Cache without checkout revalidate |
| Failure | Fail closed checkout | Charge wrong total |

---

## 4. Architecture Diagram

```text
PDP/Cart UI --> Pricing API --> Candidate Index --> Engine(quote)
                                      ^
                              Promo Catalog (ver)
                                      ^
Checkout --> Orchestrator --> pin(policy_ver, promo_set)
                    |              |
                    v              v
              Coupon Reserve   Budget Reserve
                    |              |
                    v              v
                 Place Order (Orders)
                    |
                    v
              Commit redemptions + Audit log
                    |
              Fraud hooks (pre-reserve)
```

**Stacking pipeline:**

```text
candidates → filter eligibility → sort by priority → apply stack groups
 → enforce exclusivity → apply caps → tax/shipping policy → Quote
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Checkout total recomputed server-side; client price advisory only.  
2. Same pinned inputs → same total (golden vectors).  
3. Coupon residual uses never go negative.  
4. Reserves TTL so crashes don’t leak inventory of codes.  
5. Audit can reconstruct charged breakdown.  
6. Marketplace policy packs isolate tax/stacking law differences.  
7. Never create negative payable without explicit store-credit path.

### 5.2 Stacking algorithm (interview-friendly)

1. Generate candidates from cart lines + user + clipped coupons.  
2. Filter by time window, geo, Prime, category, seller.  
3. Sort by `(priority, promo_id)` stable.  
4. Greedily apply within exclusivity group rules (or ILP for small N—usually greedy+groups enough).  
5. Apply cart-level caps (max % off).  
6. Emit per-line allocation for funding/tax.  
7. Hash inputs → `quote_id`.

Call out: NP-hard optimal stacking exists; Amazon picks **deterministic published rules**, not silent max-save search that surprises sellers.

### 5.3 Coupon reserve/commit

```text
RESERVE(coupon, user, qty, ttl) -> reservation_id | DENIED
COMMIT(reservation_id, order_id)
RELEASE(reservation_id)
```

Single-writer shard per `coupon_id` (or coupon+user for personal). Idempotent keys everywhere.

### 5.4 Hot coupon problem

Mega influencer code: striped counters `coupon_id#shard`; aggregate remaining; accept bounded race with overbook margin **or** hierarchical limiter (global token bucket + local). Prefer slight under-utilization vs over-redemption for trust.

### 5.5 Progressive scale

| Jump | Move |
|------|------|
| 10× | Compiled policy; Redis reserves; badge CDN cache |
| 100× | Marketplace cells; ASIN promo inverted index shards; audit cold tier |
| 1,000× | Edge estimate caches; approx browse budgets; redemption platform cells |

### 5.6 Fraud

- Per-user/device coupon velocity  
- New-account exploit detection  
- Reseller patterns  
- Step-up / block  

Fail closed on checkout when risk service times out for high-risk coupons; soft on plain Prime badges optional.

### 5.7 Returns & compensation

Policy table: restore coupon? restore budget? partial return discount clawback. Emit compensating ledger events; never silent.

### 5.8 Data model sketch

```text
promotions(promo_id, ver, type, predicates, benefit, funding, stack_group, priority)
stack_policies(policy_id, ver, rules_blob)
coupons(code_hash, promo_id, limits, per_user_limits)
reservations(res_id, coupon_id, user_id, exp, state)
redemptions(order_id, coupon_id, user_id, ts)
quotes(quote_id, input_hash, breakdown_json, ver, ts)
```

### 5.9 Explanation UX

Customers see: “Prime Deal −$X”, “Coupon SAVE10 −$Y”, “Items not eligible…”. Sellers see funding. Internal: full predicate traces for support.

---

## 6. Wrap-Up

### 6.1 What we designed

Promo catalog, candidate index, deterministic stacking engine, quote/commit path, coupon/budget reserves, fraud hooks, audit, progressive scale.

### 6.2 Key decisions

1. Server-authoritative checkout recompute  
2. Deterministic stacking (not opaque max)  
3. Reserve/commit for limited resources  
4. Badge cache ≠ money path  
5. Fail closed on calc/risk uncertainty at checkout  
6. Marketplace policy packs  

### 6.3 Risks

- Hot coupon contention  
- Rule complexity explosions  
- Seller confusion on funding  
- Experimentation accidentally changing money  
- Clock/window edge bugs  

### 6.4 Closer

> **Discounts & Coupons Stacking**: deterministic engine, reserve/commit, audit, fraud bounds, ownership, progressive scale, customer trust on price.

---

## 7. Deeper / Related Interview Questions — Discounts Stacking

**Q1. Why not always give the customer the maximum mathematical discount?**

**A:** Seller contracts, funding, exclusivity, and legal constraints. Published deterministic rules beat surprise optimization that breaks contracts.

**Q2. PDP shows $10 off but checkout is $0 off—OK?**

**A:** Possible under races/expiry; minimize with short badge TTL + checkout explanation. Money path is checkout.

**Q3. How do you unit test stacking?**

**A:** Golden carts with expected totals across policy versions; fuzz random carts for negatives/invariants.

**Q4. Coupon oversell SEV?**

**A:** Yes—customer trust + seller funding. Use reserves; page on negative residuals; compensate.

**Q5. Where does tax apply relative to discounts?**

**A:** Marketplace policy pack; engine must be parameterized—don’t hardcode US assumptions.

**Q6. How do BOGO and %off interact?**

**A:** Explicit group rules; define benefit application order; golden tests.

**Q7. Personalization of promos?**

**A:** Candidate gen can personalize; stacking still deterministic on chosen candidates; careful fairness/legal.

**Q8. Deal-breaker?**

**A:** Trusting client totals; or best-effort coupon decrements without reserve/commit.


## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + Amazon ownership lens |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive (reliability/scale/trust) |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact; lock MVP; split load classes; name pager owners; refuse deal-breakers.

---

## 10. Operability

### Golden signals
Latency, traffic, errors, saturation, freshness/backlog, trust incidents.

### Rollback ladder
Flag off → revert artifact → shed/reduce load → cell isolate → postmortem with trust section.

### Kill switches
Disable optional stage; freeze nearline; revert pointer; shed traffic; isolate cell/tenant.

### Security/privacy baseline
Authn/z, PII TTLs, encryption, cell isolation, signed artifacts, abuse limits, audit trails.

### Cost worksheet
Dominant cost driver; fastest unit-cost lever; 10× cost with/without architectural jump.

```text
instances ≈ peak_QPS × cpu_sec / (cores × util)
```

### Progressive scale
10× cache/shard/async; 100× cells/partition/edge; 1,000× approximate/platform/multi-tenant cells.

### Cross-team deps
Identity, catalog/inventory, payments, notifications, experimentation, logging — each with failure mitigation.

## More Interview Q&A — Discounts & Coupons Stacking

**Q1. Integer money?**

**A:** Always minor units; banker’s rounding policy explicit.

**Q2. Why greedy stacking?**

**A:** Explainability + performance; document optimality gap.

**Q3. Distributed locks on coupons?**

**A:** Prefer single-writer shard + reserve records over cluster locks.

**Q4. How to roll out rule changes?**

**A:** Canary marketplaces; shadow compare totals; bake.

**Q5. Flash deals inventory?**

**A:** Separate from coupons—coordinate with inventory reservations.

**Q6. Code guessing?**

**A:** Rate limit; long codes; hash storage; anomaly detection.

**Q7. Offline stores?**

**A:** Different cell; don’t assume same stacking law.

**Q8. Gift & promo interaction?**

**A:** Define pipeline stages clearly in interview.

**Q9. What if engine versions disagree mid-cart?**

**A:** Pin at checkout start; cart estimates may refresh.

**Q10. CS tool?**

**A:** Replay engine on stored inputs; never hand-edit totals silently.

**Q11. ML ranking of promos?**

**A:** Can rank candidates; must not violate exclusivity.

**Q12. Multi-use vs single-use?**

**A:** Different counter schemas; per-user tables.

**Q13. Idempotency key scope?**

**A:** User+cart+attempt; include hashed coupon set.

**Q14. Data retention?**

**A:** Audit kept for finance windows; PII minimized.

**Q15. Global coupon across marketplace?**

**A:** Usually no—cells/policy packs.

**Q16. Deal-breaker restated?**

**A:** Client SoT totals; non-reserved coupon decrements.

## Deep Technical Addenda — Discounts & Coupons Stacking


### Rule compilation

Authors write structured rules; compiler validates cycles, exclusivity overlaps, and produces a versioned artifact stored in object store + metadata registry. Runtime loads artifact by pin.

### Allocation to lines

Cart-level discounts allocated to lines for tax/funding using deterministic proportional rules; store allocations in audit.

### Shadow evaluation

New policy_ver runs in shadow on sampled checkouts; compare totals; alert on divergence beyond epsilon.

### Budget hierarchies

Global campaign → marketplace → ASIN caps. Browse uses cached remaining; checkout reserves exact.

### Abuse playbooks

Coupon farming with many accounts: device graphs, payment instrument links, gradual limits.

### Interview whiteboard tip

Draw estimate path vs commit path as two arrows sharing an engine library box—this single picture often wins the room.


## Tradeoff Matrices — Discounts & Coupons Stacking

### Consistency vs latency

| Choice | Latency | Correctness | Use when |
|--------|---------|-------------|----------|
| Sync durable then serve | Higher | Stronger | Money/trust/enforcement paths |
| Serve then async durable | Lower | Risk window | Non-money UX with repair |
| Cached eventual | Lowest | Stale OK | Read-heavy dashboards / portals |

### Exact vs approximate

| Choice | Cost | UX risk | Use when |
|--------|------|---------|----------|
| Exact | High at scale | Low confusion | Checkout, ledger, rating |
| Approximate labeled | Lower | Need UX copy | Analytics, spectate fan-out |
| Hierarchical | Medium | Ops complexity | Multi-region aggregates |

### Availability vs correctness

| Choice | Availability | Correctness | Use when |
|--------|--------------|-------------|----------|
| Fail closed | Lower during dep outage | Safer trust | Fraud, consent, money |
| Fail open degrade | Higher | Risk wrong UX | Optional personalization |
| Shed load | Partial | Protects core | Peak storms |

## Operability Addenda — Discounts & Coupons Stacking

### Deploy pipeline

```text
build artifact → static validation → shadow → canary → bake → full
                     ↓ fail              ↓ guardrail fail
                  reject              auto rollback
```

### Guardrail examples

- p99 latency regression > threshold  
- error/empty/fallback rate rise  
- safety/privacy/trust denials anomaly  
- cost/unit-economics spike  
- backlog/DLQ growth beyond budget  

### Kill switches (name them in interview)

1. Disable optional stage / feature flag  
2. Freeze nearline updates  
3. Revert artifact pointer / config version  
4. Shed traffic / reduce concurrency / reduce K  
5. Cell isolation / pause tenant or marketplace  

### Oncall first five minutes

1. Check golden signals and recent deploys  
2. Confirm blast radius (cell / marketplace / tenant)  
3. Engage kill switch if customer-trust burning  
4. Preserve evidence (logs, samples, config versions)  
5. Customer messaging path if trust incident  

### Cost worksheet

Speak: peak demand → per-node capacity → headroom 2–3× → cache/async/edge lever → what 10× does → architectural jump that bends the curve.

## Worked Capacity Narrative — Discounts & Coupons Stacking

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/async/edge lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Discounts & Coupons Stacking

Amazon interviews reward explicit trust reasoning: wrong charges, undelivered critical mail, broken promotions, unfair games, privacy leaks, or silent data loss are not “ops issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Discounts & Coupons Stacking

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, partitioned queues, edge/client head  
- **1,000×:** platform multi-tenant cells, approximate algorithms, specialized fleets  

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Discounts & Coupons Stacking
### S1. Pure pricing function

Engine as library; no hidden I/O; all inputs explicit.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Candidate indexing

Inverted ASIN/category indexes; segment bitsets.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Policy compiler

Human rules → deterministic program; versioned artifacts.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Idempotent checkout

checkout_attempt_id guards reserves and orders.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Clock windows

Server time; start/end buffers; leap smear awareness.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Multi-currency

Minor units integers; FX out of engine if possible.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Seller funding ledger

Allocate discount to Amazon vs seller buckets.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Clip wallet

User clipped coupons as candidate source.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S9. Gift cards interaction

Order of application documented; not ad hoc.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S10. Partial shipment

Recalc remaining discounts carefully.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S11. Promo conflicts UI

Explain suppressed promos to reduce CS load.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S12. Chaos testing

Reserve expiry mid-commit; dual submit; catalog version bump.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S13. Cell isolation

Marketplace cells for catalog + redemptions.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S14. Approx browse budgets

At 1,000× badges use cached remaining; commit exact.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S15. Security of codes

Store code hashes; rate-limit guessing.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S16. Platformization

Shared promotions platform with team quotas.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Interview Cards — Discounts & Coupons Stacking

### Card 1: Server-authoritative totals

Checkout recomputes; client advisory only.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 2: Deterministic stacking

Stable sort + exclusivity groups + caps; golden vectors.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 3: Reserve/commit coupons

TTL reservations; idempotent commit; no negative residuals.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 4: Quote pinning

Pin policy_ver + promo set for the checkout attempt.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 5: Badge cache strategy

CDN/edge for browse; short TTL; never skip revalidate.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 6: Hot coupon striping

Striped counters or hierarchical buckets; prefer under-redeem.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 7: Fraud fail-closed

High-risk coupons deny on risk timeout.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 8: Audit reconstructability

Persist input hash + breakdown with order.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 9: Marketplace packs

Tax/stacking law differences per marketplace cell.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 10: Budget reservation

Campaign spend caps with TTL; browse approx OK.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 11: Returns compensation

Explicit restore policies; compensating events.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 12: Exclusivity groups

Prevent undefined double dips; document seller rules.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 13: Experiment safety

Don’t mutate money in unchecked experiments.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 14: Cost lever #1

Cache badges + index candidates; avoid full promo scans.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 15: Deal-breaker

Client price as SoT; or non-deterministic ‘max save’ without rules.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

### Card 16: Prime Day posture

Pre-warm indexes; shed badge personalization; protect commit path.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for discounts stacking.

## Related Deep Dive Q&A — Discounts & Coupons Stacking

**RQ1. Why does 'Deterministic engine' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Deterministic engine'. Name who pages and what artifact version you roll back.

**RQ2. How would you test 'Deterministic engine' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Deterministic engine'.

**RQ3. What regresses if 'Deterministic engine' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Deterministic engine'.

**RQ4. Why does 'Reserve/commit' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Reserve/commit'. Name who pages and what artifact version you roll back.

**RQ5. How would you test 'Reserve/commit' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Reserve/commit'.

**RQ6. What regresses if 'Reserve/commit' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Reserve/commit'.

**RQ7. Why does 'Badge vs checkout' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Badge vs checkout'. Name who pages and what artifact version you roll back.

**RQ8. How would you test 'Badge vs checkout' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Badge vs checkout'.

**RQ9. What regresses if 'Badge vs checkout' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Badge vs checkout'.

**RQ10. Why does 'Hot coupons' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Hot coupons'. Name who pages and what artifact version you roll back.

**RQ11. How would you test 'Hot coupons' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Hot coupons'.

**RQ12. What regresses if 'Hot coupons' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Hot coupons'.

**RQ13. Why does 'Fraud gates' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Fraud gates'. Name who pages and what artifact version you roll back.

**RQ14. How would you test 'Fraud gates' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Fraud gates'.

**RQ15. What regresses if 'Fraud gates' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Fraud gates'.

**RQ16. Why does 'Audit logs' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Audit logs'. Name who pages and what artifact version you roll back.

**RQ17. How would you test 'Audit logs' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Audit logs'.

**RQ18. What regresses if 'Audit logs' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Audit logs'.

**RQ19. Why does 'Marketplace packs' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Marketplace packs'. Name who pages and what artifact version you roll back.

**RQ20. How would you test 'Marketplace packs' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Marketplace packs'.

**RQ21. What regresses if 'Marketplace packs' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Marketplace packs'.

**RQ22. Why does 'Budget caps' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Budget caps'. Name who pages and what artifact version you roll back.

**RQ23. How would you test 'Budget caps' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Budget caps'.

**RQ24. What regresses if 'Budget caps' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Budget caps'.

**RQ25. Why does 'Exclusivity groups' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Exclusivity groups'. Name who pages and what artifact version you roll back.

**RQ26. How would you test 'Exclusivity groups' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Exclusivity groups'.

**RQ27. What regresses if 'Exclusivity groups' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Exclusivity groups'.

**RQ28. Why does 'Returns restore' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Returns restore'. Name who pages and what artifact version you roll back.

**RQ29. How would you test 'Returns restore' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Returns restore'.

**RQ30. What regresses if 'Returns restore' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Returns restore'.

**RQ31. Why does 'Prime Day shed' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Prime Day shed'. Name who pages and what artifact version you roll back.

**RQ32. How would you test 'Prime Day shed' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Prime Day shed'.

**RQ33. What regresses if 'Prime Day shed' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Prime Day shed'.

**RQ34. Why does 'Golden tests' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Golden tests'. Name who pages and what artifact version you roll back.

**RQ35. How would you test 'Golden tests' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Golden tests'.

**RQ36. What regresses if 'Golden tests' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Golden tests'.

**RQ37. Why does 'Seller funding' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Seller funding'. Name who pages and what artifact version you roll back.

**RQ38. How would you test 'Seller funding' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Seller funding'.

**RQ39. What regresses if 'Seller funding' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Seller funding'.

**RQ40. Why does 'Idempotent apply' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Idempotent apply'. Name who pages and what artifact version you roll back.

**RQ41. How would you test 'Idempotent apply' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Idempotent apply'.

**RQ42. What regresses if 'Idempotent apply' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Idempotent apply'.

**RQ43. Why does 'Policy versioning' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Policy versioning'. Name who pages and what artifact version you roll back.

**RQ44. How would you test 'Policy versioning' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Policy versioning'.

**RQ45. What regresses if 'Policy versioning' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Policy versioning'.

**RQ46. Why does 'Cost of eval' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Cost of eval'. Name who pages and what artifact version you roll back.

**RQ47. How would you test 'Cost of eval' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Cost of eval'.

**RQ48. What regresses if 'Cost of eval' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Cost of eval'.

## Narrative Walkthrough — Discounts & Coupons Stacking

### Walkthrough beat 1

Customer clips SAVE10 and opens cart with a Prime-eligible ASIN. Pricing API fetches candidates from inverted index, runs deterministic engine, returns breakdown in 40ms. No reserves yet. Call out advisory vs authoritative.

### Walkthrough beat 2

At checkout, orchestrator pins policy_ver=112, reserves coupon and budget, recomputes quote, places order, commits. If reserve fails, UX removes coupon with explanation. Watch redemption conflict rate and commit p99.

### Walkthrough beat 3

Prime Day: badge cache hit rate saves browse; commit fleets scaled; risk velocity tightens on viral codes. If stacking bug ships, kill switch reverts policy artifact pointer—not ‘add servers’.

## Scenario Runbooks — Discounts & Coupons Stacking

### SEV: negative order totals

1. Disable suspect policy version via kill switch.
2. Find golden test gap; freeze new promos.
3. Reconcile affected orders; compensate customers.
4. Add invariant CI: payable >= 0 (unless store credit path).

### Viral coupon oversold

1. Pause coupon; inspect counter stripes.
2. Halt accepts; reconcile reservations.
3. Customer messaging; honor committed orders.
4. Move mega-coupons to hierarchical limiter.

### Seller funding dispute

1. Pull quote audit for order_id.
2. Show allocation lines; policy version.
3. If engine bug, compensate seller ledger.

## Appendices — Discounts & Coupons Stacking

### A — Glossary
| Term | Meaning |
|------|---------|
| Cell | Failure-isolated unit (marketplace/region/tenant) |
| Nearline | Minutes-latency path |
| Canary | Partial bake of artifact |
| Deal-breaker | Non-negotiable bad design |
| Two-pizza | Ownership team with pager |
| SoT | Source of truth |
| DLQ | Dead-letter queue |
| PIT | Point-in-time (features/state) |
| Stack group | Exclusivity/priority partition for promos |
| Reserve | Soft hold on coupon/budget with TTL |
| Quote pin | Frozen inputs for a checkout attempt |
| Funding | Who pays for the discount |
| Golden vector | Fixture cart with expected total |

### B — Oncall checklist
- [ ] SLOs green / error budget known
- [ ] Rollback armed
- [ ] Kill switches known
- [ ] Cost dashboards
- [ ] Privacy/safety/trust tested
- [ ] DLQ/backlog within budget
- [ ] Recent deploys identified

### C — Topic closer checklist
- [ ] Deterministic stacking + golden tests
- [ ] Server checkout recompute
- [ ] Reserve/commit coupons & budgets
- [ ] Audit reconstructability
- [ ] Fraud fail-closed on risk coupons
- [ ] Progressive scale 10×/100×/1,000×

### D — Metric dictionary (speak these)

| Metric | Why it matters |
|--------|----------------|
| p99 latency by class | Split interactive vs async |
| Error / reject rate | Customer pain |
| Backlog age / DLQ depth | Hidden debt |
| Unit cost ($/1K ops) | Frugality |
| Trust incident count | Leadership principle signal |
| Cache hit rate | Scale lever |
| Cell saturation | Isolation health |

### E — Failure injection catalog

| Inject | Expect |
|--------|--------|
| Dependency timeout | Deadline shed / fallback |
| Dual publish / retry storm | Idempotent no double effect |
| Hot partition | Reshard / isolate |
| Clock skew | Bounded error or fail closed |
| Region loss | Cell failover story |
| Poison message | DLQ, not partition death |

### F — Amazon leadership-principle hooks

| Principle | How it shows in this design |
|-----------|------------------------------|
| Customer Obsession | Explicit trust fail-closed/open |
| Ownership | Named two-pizza + pager |
| Invent & Simplify | Prefer fewer planes with clear contracts |
| Frugality | Unit-cost levers before linear scale-out |
| Dive Deep | Metrics + invariants + runbooks |
| Bias for Action | Kill switches and rollback ladder |
| Earn Trust | Auditability, no silent money/promo bugs |

### G — One-breath closer

> **Discounts & Coupons Stacking**: explicit planes, SLOs, ownership, progressive scale (10×/100×/1,000×), customer trust, unit economics.

---

## Extra Drill Tables — Discounts & Coupons Stacking

### Load class split (say this early)

| Class | Example | SLO style | Consistency |
|-------|---------|-----------|-------------|
| Interactive read | Browse / status | Tight p99 | Eventual often OK |
| Interactive write | Checkout / move / reserve | Tight + correct | Stronger |
| Async | Email send / analytics | Freshness budgets | At-least-once |
| Control plane | Config / templates / rules | Correct rollout | Versioned artifacts |

### Ownership RACI sketch

| Concern | Responsible | Accountable | Consulted |
|---------|-------------|-------------|-----------|
| Serving path | Owning service team | Eng manager / PE | Dep teams |
| Trust policy | Safety/privacy/fraud | Director-level policy | Legal |
| Cost | Owning team | Sr. leadership | Capacity |
| Incident | Primary oncall | Secondary / IC | Comms |

### Progressive scale interview lines (memorize)

| Jump | Line to say |
|------|-------------|
| 10× | “Cache, shard, async offload, and budgets—not just more boxes.” |
| 100× | “Cells and partitioned queues; isolate blast radius by marketplace/tenant.” |
| 1,000× | “Approximate where labeled, platformize shared fleets, specialize hot paths.” |

### Anti-patterns whiteboard list

| Anti-pattern | Why it fails Amazon bar |
|--------------|-------------------------|
| One shared FIFO for all classes | Priority inversion / trust SEVs |
| Client as source of truth | Fraud + desync |
| Silent money/promo repair | Earn Trust violation |
| Global mega-model/mega-DB | Blast radius + ownership soup |
| Linear scale-only story | Misses frugality / invent & simplify |

### Sample metric alerts

| Alert | Severity hint |
|-------|---------------|
| Core p99 burn 15m | Page |
| Trust invariant flip | Page immediately |
| DLQ growth 3× baseline | Ticket → page if txn class |
| Unit cost +40% week | Capacity review |
| Cell imbalance | Rebalance job |

### Design review checklist (L6)

- [ ] Load classes split with numbers
- [ ] Invariants written as tests
- [ ] Fail-closed vs fail-open named
- [ ] Kill switches named
- [ ] 10×/100×/1,000× jumps named
- [ ] Deal-breakers refused
- [ ] Two-pizza owners named
- [ ] Customer-trust SEV defined

*End of Discounts & Coupons Stacking system design prep doc.*
