# System Design: Online Store (Amazon.com-style Retail)

> **Focus areas:** Catalog · Search/browse · Cart · Inventory · Checkout/orders · Payments · Fulfillment hooks · Multi-marketplace · Peak traffic · Trust  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split read vs buy paths, correct inventory reservation, explicit deal-breakers, progressive peak math  
> **Interview theme:** Amazon SDE III / L6 — **Retail Platform** — practical Amazon.com slice with ownership boundaries

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

Goal: **bound an online store**—browse/search, product detail, cart, inventory-aware checkout, order placement, and post-purchase hooks—without boiling the ocean into all of Amazon.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | End-to-end retail purchase path | Full warehouse robotics |
| Planes | Read catalog vs reserve/buy | Single monolith DB for everything |
| Success | Correct orders + availability honesty | Infinite SKU search relevance PhD |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who sells? | Amazon retail + marketplace sellers | Merchant_id on offers |
| F2 | Catalog? | Products (ASIN), offers, images, attrs | Catalog service + search index |
| F3 | Search/browse? | Query + category facets | Search cluster; browse caches |
| F4 | Cart? | Auth + anonymous merge | Cart service |
| F5 | Inventory? | Available qty; reserve at checkout | Inventory service with reservations |
| F6 | Pricing? | Offer price + promos hook | Price/promos service |
| F7 | Checkout? | Address, payment, place order | Orders + Payments orchestration |
| F8 | Payments? | Auth/capture via PSP | Idempotent payment intents |
| F9 | Fulfillment? | Create fulfillment orders | Async events to FC systems |
| F10 | Account? | Identity, addresses, orders history | Identity + order read models |
| F11 | Multi-marketplace? | amazon.com / .co.uk / … | Marketplace cells |
| F12 | Prime? | Shipping promise badges | Promise engine hook |

**MVP functional scope:**

1. Catalog read (PDP) + search/browse basic.  
2. Cart add/update/merge.  
3. Inventory reservation at checkout.  
4. Payment auth + order create (durable).  
5. Order history; cancel before ship (basic).  
6. Eventing to fulfillment.  
7. Marketplace-scoped data.

**Out of MVP:**

- Full advertising platform  
- Complete recommendation science  
- Warehouse robot control  
- Global multi-FC network optimization deep dive (mention hooks)  
- Fresh grocery cold chain specialty

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | PDP latency | Snappy | p99 < 200ms cached |
| N2 | Search latency | Interactive | p99 < 300ms |
| N3 | Checkout | Correct > ultra-low latency | p99 < 2–3s incl payment |
| N4 | Inventory honesty | Minimize oversell | Strong reserve path |
| N5 | Peak (Prime Day) | Survive 10–100× | Shed noncritical; protect buy |
| N6 | Durability | Orders never lost once placed | Quorum before ACK |
| N7 | Consistency | Read-your-writes orders | Order home shard |
| N8 | Security | PCI minimized; authz | Tokenized pay |

### 1.3 Cases

**Happy paths**

1. Search → PDP → add cart → checkout → pay → order confirmed → fulfillment event.  
2. Anonymous cart → login → merge.  
3. Payment fails → no order (or pending per policy).  
4. Cancel before shipment → release inventory + void/refund.  
5. Oversell race → one checkout wins reserve; other informed OOS.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double place order | Idempotency key |
| Inventory timeout | Fail purchase; don’t charge blindly |
| Payment unknown | Pending + inquire; no double auth |
| Search stale OOS | PDP/checkout authoritative |
| Hot ASIN | Shard inventory; cache PDP carefully |
| Seller suspension | Offer suppressed; in-flight orders policy |
| Region outage | Marketplace cell failover story |
| Cart giant | Cap lines; paginate |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| SKUs / offers | 50M | 100M | 300M | 500M+ |
| PDP QPS | 50K | 500K | 5M | 50M |
| Search QPS | 20K | 200K | 2M | 20M |
| Checkout QPS | 1K | 10K | 100K | 1M |
| Orders / day | 5M | 50M | 500M | 5B |
| Cart ops /s | 10K | 100K | 1M | 10M |
| Inventory reserve /s | 1K | 10K | 100K | 1M |
| Peak concurrent sessions | 2M | 20M | 200M | 2B |

**What each jump forces:**

- **10×:** CDN/edge caches; cart Redis; search replicas; order DB shard.  
- **100×:** Marketplace cells; inventory shard by ASIN; checkout orchestration isolation; read models.  
- **1,000×:** Edge browse; approximate search tiers; inventory hierarchical; platform multi-tenant cells.

### 1.5 Constraints & Assumptions

- Protect **buy path** over browse personalization under shed.  
- Oversell is a trust incident—design reserves.  
- Repeat: *“Catalog/search/cart + inventory-reserved checkout + durable orders, cell by marketplace.”*

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Read vs write

Browse/PDP dominate QPS; checkout is smaller but higher stakes. Capacity plans must not conflate them.

### 2.2 Cache math

If PDP QPS 500K and cache hit 95%, origin 25K—architecture depends on hit rate honesty.

### 2.3 Order storage

5M orders/day × 5KB ≈ 25 GB/day raw; index carefully; cold archive.

### 2.4 Inventory

Hot ASINs need striped reservations or FC-level hierarchy; global single row counters die at 100×.

### 2.5 Cost levers

Edge cache, search tiering, async noncritical (recs/reviews), compress images, cell right-sizing. Track $/order and $/1K PDP.

---

## 3. High-Level Design

### 3.1 Service map

| Service | Owns |
|---------|------|
| Catalog | ASIN attributes, media refs |
| Offers/Pricing | Seller offers, price |
| Search | Index + query |
| Cart | Cart lines |
| Inventory | Availability + reservations |
| Promotions | Hook (see stacking doc) |
| Checkout Orchestrator | Saga/workflow |
| Payments | Payment intents |
| Orders | Order SoT |
| Fulfillment bridge | Events out |
| Identity | Users/sessions |

### 3.2 Checkout saga (happy)

```text
validate cart → price → reserve inventory → auth payment → create order
  → commit payment capture policy → emit fulfillment → clear cart
```

Compensations: release inventory, void auth, mark order failed.

### 3.3 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Inventory | Reserve before charge settle | Charge then hope stock |
| Orders | Durable SoT service | Orders only in payment PSP |
| Search | Eventual index | Strong consistent search for all reads |
| Peak | Shed recs/reviews first | Drop checkout randomly |
| Cells | Marketplace | One global mega-DB |

---

## 4. Architecture Diagram

```text
Client/CDN
   |-- Search --> Search Index <-- catalog change stream
   |-- PDP ----> Catalog + Offers + Promise + Reviews(async)
   |-- Cart ---> Cart Service (Redis/DB)
   |-- Checkout -> Orchestrator
                      |--> Inventory.reserve
                      |--> Promotions.quote
                      |--> Payments.auth
                      |--> Orders.create (SoT)
                      |--> Events --> Fulfillment / Email
```

**Marketplace cell:**

```text
[www.amazon.com cell] [www.amazon.co.uk cell]
 each: catalog shard view, inventory, orders, carts
 global: identity federation, payment tokens (careful), seller master hooks
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. No successful order without durable Orders write.  
2. No charge without inventory reservation (policy-appropriate).  
3. Idempotent checkout attempts.  
4. Cart merge doesn’t duplicate lines incorrectly.  
5. Oversell bounded by reservation mechanism.  
6. Marketplace isolation for catalog legality/price.  
7. Payment uncertain → inquire, don’t double.

### 5.2 Inventory reservation

```text
AVAILABLE -= qty (reserved)
RESERVATION(ttl) tied to checkout_attempt
on commit: RESERVED → SOLD
on expire/cancel: return AVAILABLE
```

Shard key `asin` or `asin+fc`. Hierarchical: FC pools → marketplace aggregate for promise.

### 5.3 Catalog & search

Catalog OLTP/DBMS for writers; change stream to search index (OpenSearch/solr-class). PDP may read materialized docs from cache. Eventual consistency OK for search; PDP offer service more authoritative for buy.

### 5.4 Cart

Auth carts in DB; anonymous in Redis/cookie hybrid; merge rules documented (qty caps). Optimistic concurrency on version.

### 5.5 Orders SoT

Order state machine: PENDING_PAYMENT → PLACED → PAYMENT_CAPTURED → FULFILLING → SHIPPED → DELIVERED / CANCELED / RETURNED. Append-only events + current snapshot.

### 5.6 Progressive scale

| Jump | Move |
|------|------|
| 10× | CDN, cart Redis, order shard by customer, search replicas |
| 100× | Marketplace cells; inventory stripes; checkout fleet; CQRS order reads |
| 1,000× | Edge browse; search tiers; inventory hierarchy; platformization |

### 5.7 Peak shedding (Prime Day)

Priority: checkout/inventory/payments > PDP core > search > recs/reviews/personalization. Feature flags; static assets; pre-warm caches; load-test.

### 5.8 Data model sketch

```text
products(asin, attrs, media)
offers(offer_id, asin, seller_id, price, condition)
inventory(asin, fc_id, available, reserved)
reservations(res_id, asin, qty, exp, state)
carts(cart_id, user_id?, version)
cart_lines(cart_id, offer_id, qty)
orders(order_id, user_id, state, marketplace)
order_lines(...)
payments(payment_id, order_id, state, psp_refs)
```

### 5.9 Security & trust

- AuthN/Z; CSRF; bot management on checkout  
- PCI scope minimization  
- Fraud scoring hook  
- Privacy of order history  
- Seller impersonation prevention  

---

## 6. Wrap-Up

### 6.1 What we designed

Online store planes: catalog/search, cart, inventory reservations, checkout saga, payments, orders SoT, fulfillment events, marketplace cells, peak shedding.

### 6.2 Key decisions

1. Split read vs buy paths  
2. Reserve inventory in checkout saga  
3. Durable Orders SoT  
4. Idempotent payments  
5. Shed noncritical before buy path  
6. Marketplace cells at 100×  

### 6.3 Risks

- Oversell under bugs  
- Search/PDP staleness confusion  
- Saga complexity / partial failures  
- Hot ASIN contention  
- Cross-cell identity  

### 6.4 Closer

> **Online Store**: explicit planes, inventory-safe checkout, durable orders, peak shedding, ownership, progressive scale, customer trust.

---

## 7. Deeper / Related Interview Questions — Online Store

**Q1. Why not one PostgreSQL for everything?**

**A:** Different scaling/consistency needs; blast radius; ownership. Use DB per service with clear contracts.

**Q2. How do you prevent charging for OOS items?**

**A:** Reserve inventory before/within payment authorization workflow; compensate on failure; never capture blindly.

**Q3. Search says in stock, checkout says no—OK?**

**A:** Yes under races; minimize; honest UX; search eventual.

**Q4. How to shard orders?**

**A:** Typically `customer_id` or `order_id` with secondary indexes; cell by marketplace first.

**Q5. Cart at 1M ops/s?**

**A:** Redis/memory + async durability for anon; careful merge; not all ops hit disk.

**Q6. Exactly-once order placement?**

**A:** Effectively-once via idempotency keys + durable state; not magic.

**Q7. Multi-FC promise dates?**

**A:** Promise service reads inventory hierarchy; separate deep dive—hook only unless asked.

**Q8. Deal-breaker?**

**A:** Charge then check stock; or single global DB; or drop checkout under load before shedding recs.


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

## More Interview Q&A — Online Store

**Q1. Why saga not 2PC?**

**A:** 2PC fragile across payments/inventory; saga+compensations practical.

**Q2. How long reservation TTL?**

**A:** Minutes aligned to checkout UX; too long starves stock.

**Q3. Guest checkout?**

**A:** Supported; idempotency + fraud tighter.

**Q4. Order id generation?**

**A:** Time-sortable unique; avoid DB sequence hotspot.

**Q5. Multi-offer same ASIN?**

**A:** Offer_id in cart lines; inventory often at offer/FC.

**Q6. Returns?**

**A:** Separate service; compensating inventory/payment.

**Q7. International duties?**

**A:** Marketplace/policy; don’t invent global tax engine live.

**Q8. Why CQRS for orders?**

**A:** Write path simple; history/search different shape.

**Q9. Session stickiness?**

**A:** Prefer stateless JWT/session store; not sticky checkout app servers required.

**Q10. Image of architecture rule?**

**A:** Boxes with ownership + arrows for sync vs async.

**Q11. How to test checkout?**

**A:** Contract tests + chaos compensations + idempotency fuzz.

**Q12. Soft vs hard OOS?**

**A:** Promise engine may soft-block; inventory reserve hard.

**Q13. Marketplace seller API limits?**

**A:** Quotas; abuse; catalog ingestion separate doc.

**Q14. Data residency?**

**A:** EU cell keeps EU customer orders.

**Q15. Metric that proves scale jump worked?**

**A:** Checkout success rate + oversell rate + unit cost.

**Q16. Deal-breaker restated?**

**A:** Charge without reserve; monolith; shed buy first.

## Deep Technical Addenda — Online Store


### Fragmented PDP assembly

Edge builds page from fragments: product, offer, promise, ads, recs—with independent TTLs and budgets. Critical fragments have fallbacks.

### Inventory hierarchy

```text
FC on-hand → FC sellable → Marketplace aggregate → Badge approx
```

Checkout reserves at the level required for promise accuracy.

### Outbox pattern

Orders DB transaction writes order + outbox row; publisher relays to bus; consumers (fulfillment, email) idempotent.

### Identity merge

Anonymous → authenticated merge must be secure against cart hijack (hold tokens).

### Peak playbook

Pre-warm; freeze noncritical deploys; raised autoscaling; dependency SLOs; war room metrics: reserve deny, payment pending age, place_order p99.

### Relationship to sibling docs

Promos → discounts-coupons doc; email → email-delivery doc; warehouse → warehouse doc. In interview, mention boundaries instead of designing all.


## Tradeoff Matrices — Online Store

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

## Operability Addenda — Online Store

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

## Worked Capacity Narrative — Online Store

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/async/edge lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Online Store

Amazon interviews reward explicit trust reasoning: wrong charges, undelivered critical mail, broken promotions, unfair games, privacy leaks, or silent data loss are not “ops issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Online Store

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, partitioned queues, edge/client head  
- **1,000×:** platform multi-tenant cells, approximate algorithms, specialized fleets  

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Online Store
### S1. Catalog writers

Seller/retail pipelines; validation; version attrs.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Offer selection

Buy-box like logic simplified; eligibility.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Session identity

Anonymous id → user bind; secure cookies.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Price freshness

Short TTL on price fragments; checkout reprice.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Tax/shipping

Marketplace calculators as deps with budgets.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Outbox events

OrderPlaced reliable emit; consumers idempotent.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Read models

Order history CQRS; not same as write path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Image/media

CDN; not on critical order path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S9. Reviews async

Degrade empty reviews OK.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S10. Bot management

Challenge suspicious checkout/search scrapers.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S11. DR/failover

Cell runbooks; RPO/RTO for orders.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S12. Observability

Funnel conversion; reserve deny rate; payment pending age.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S13. Data retention

Orders legal retention; PII minimization.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S14. Seller suspension

Offer kill list nearline; fulfillment policy.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S15. Platform APIs

Internal service contracts versioned.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S16. Load testing

Prime Day rehearsal; dependency latency injection.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Interview Cards — Online Store

### Card 1: Read vs buy split

Cache browse; strong-ish checkout; different SLOs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 2: Inventory reserve

TTL reservations; commit/release; hot ASIN stripes.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 3: Checkout saga

Ordered steps + compensations; idempotent attempt ids.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 4: Orders SoT

Durable state machine; events for fulfillment.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 5: Payments uncertainty

Pending + inquire; no double auth.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 6: Cart merge

Explicit rules; version checks; qty caps.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 7: Search eventual

Change stream index; PDP/offer authoritative for buy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 8: Peak shedding

Protect buy path; kill recs/reviews first.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 9: Marketplace cells

Failure isolation; legal/price boundaries.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 10: Idempotent place order

Client key; server dedupe.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 11: CDN/edge PDP

Cache keys include offer version; purge on price-critical changes carefully.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 12: Fraud hook

Pre-auth risk; step-up; fail closed high risk.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 13: Cancel/release

Before ship cancel releases inventory + payment void/refund.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 14: Cost lever #1

Edge cache hit rate + search tiering.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 15: Deal-breaker

Pay-then-stock; monolith mega-DB; shed checkout first.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

### Card 16: Ownership map

Name two-pizza owners per service in interview.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for online store.

## Related Deep Dive Q&A — Online Store

**RQ1. Why does 'Inventory reservation' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Inventory reservation'. Name who pages and what artifact version you roll back.

**RQ2. How would you test 'Inventory reservation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Inventory reservation'.

**RQ3. What regresses if 'Inventory reservation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Inventory reservation'.

**RQ4. Why does 'Checkout saga' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Checkout saga'. Name who pages and what artifact version you roll back.

**RQ5. How would you test 'Checkout saga' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Checkout saga'.

**RQ6. What regresses if 'Checkout saga' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Checkout saga'.

**RQ7. Why does 'Orders durability' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Orders durability'. Name who pages and what artifact version you roll back.

**RQ8. How would you test 'Orders durability' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Orders durability'.

**RQ9. What regresses if 'Orders durability' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Orders durability'.

**RQ10. Why does 'Search eventual' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Search eventual'. Name who pages and what artifact version you roll back.

**RQ11. How would you test 'Search eventual' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Search eventual'.

**RQ12. What regresses if 'Search eventual' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Search eventual'.

**RQ13. Why does 'Cart scale' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Cart scale'. Name who pages and what artifact version you roll back.

**RQ14. How would you test 'Cart scale' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Cart scale'.

**RQ15. What regresses if 'Cart scale' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Cart scale'.

**RQ16. Why does 'Peak shedding' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Peak shedding'. Name who pages and what artifact version you roll back.

**RQ17. How would you test 'Peak shedding' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Peak shedding'.

**RQ18. What regresses if 'Peak shedding' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Peak shedding'.

**RQ19. Why does 'Marketplace cells' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Marketplace cells'. Name who pages and what artifact version you roll back.

**RQ20. How would you test 'Marketplace cells' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Marketplace cells'.

**RQ21. What regresses if 'Marketplace cells' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Marketplace cells'.

**RQ22. Why does 'Payment inquire' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Payment inquire'. Name who pages and what artifact version you roll back.

**RQ23. How would you test 'Payment inquire' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Payment inquire'.

**RQ24. What regresses if 'Payment inquire' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Payment inquire'.

**RQ25. Why does 'Hot ASIN' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Hot ASIN'. Name who pages and what artifact version you roll back.

**RQ26. How would you test 'Hot ASIN' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Hot ASIN'.

**RQ27. What regresses if 'Hot ASIN' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Hot ASIN'.

**RQ28. Why does 'Idempotent order' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Idempotent order'. Name who pages and what artifact version you roll back.

**RQ29. How would you test 'Idempotent order' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Idempotent order'.

**RQ30. What regresses if 'Idempotent order' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Idempotent order'.

**RQ31. Why does 'CDN PDP' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'CDN PDP'. Name who pages and what artifact version you roll back.

**RQ32. How would you test 'CDN PDP' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'CDN PDP'.

**RQ33. What regresses if 'CDN PDP' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'CDN PDP'.

**RQ34. Why does 'Fraud gate' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Fraud gate'. Name who pages and what artifact version you roll back.

**RQ35. How would you test 'Fraud gate' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Fraud gate'.

**RQ36. What regresses if 'Fraud gate' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Fraud gate'.

**RQ37. Why does 'Cancel release' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Cancel release'. Name who pages and what artifact version you roll back.

**RQ38. How would you test 'Cancel release' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Cancel release'.

**RQ39. What regresses if 'Cancel release' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Cancel release'.

**RQ40. Why does 'Outbox fulfillment' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Outbox fulfillment'. Name who pages and what artifact version you roll back.

**RQ41. How would you test 'Outbox fulfillment' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Outbox fulfillment'.

**RQ42. What regresses if 'Outbox fulfillment' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Outbox fulfillment'.

**RQ43. Why does 'Buy-box offer' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Buy-box offer'. Name who pages and what artifact version you roll back.

**RQ44. How would you test 'Buy-box offer' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Buy-box offer'.

**RQ45. What regresses if 'Buy-box offer' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Buy-box offer'.

**RQ46. Why does 'Unit cost' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Unit cost'. Name who pages and what artifact version you roll back.

**RQ47. How would you test 'Unit cost' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Unit cost'.

**RQ48. What regresses if 'Unit cost' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Unit cost'.

## Narrative Walkthrough — Online Store

### Walkthrough beat 1

Customer searches ‘usb-c cable’, hits cached SERP, opens PDP (CDN+origin fragment assembly), adds to cart (Redis). Latency story for browse vs the upcoming buy path.

### Walkthrough beat 2

Checkout starts: orchestrator validates cart, reprices, reserves inventory for hot ASIN (stripe), auths payment, writes PLACED order, emits outbox, emails via email platform. If payment pending, order waits—no fulfillment yet.

### Walkthrough beat 3

Prime Day shed: personalization off, reviews deferred, search degraded to fewer facets, checkout fleets scaled. Call out customer obsession: better honest ‘try again’ than wrong charge.

## Scenario Runbooks — Online Store

### SEV: oversell wave

1. Pause affected ASINs.
2. Inspect reservation bugs / TTL too long.
3. Stop captures on oversold; customer messaging.
4. Fix stripes; add invariant monitors.

### Payment PSP outage

1. Prefer fail with message for new checkouts.
2. Inquire in-flight pendings.
3. Don’t dual-auth on retry without keys.
4. Status page; protect inventory holds TTLs.

### Search index lag viral ASIN

1. Accept browse staleness; boost PDP authority.
2. Priority reindex path for viral ASINs.
3. Communicate CS macros.

## Appendices — Online Store

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
| ASIN | Amazon Standard Identification Number |
| Offer | Sellable price/condition from a seller |
| Reserve | Hold stock for checkout attempt |
| Buy path | Cart/checkout/order critical path |
| Cell | Marketplace failure domain |

### B — Oncall checklist
- [ ] SLOs green / error budget known
- [ ] Rollback armed
- [ ] Kill switches known
- [ ] Cost dashboards
- [ ] Privacy/safety/trust tested
- [ ] DLQ/backlog within budget
- [ ] Recent deploys identified

### C — Topic closer checklist
- [ ] Split browse vs buy
- [ ] Inventory reserve in saga
- [ ] Durable Orders SoT
- [ ] Idempotent payments
- [ ] Peak shedding order
- [ ] Marketplace cells

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

> **Online Store**: explicit planes, SLOs, ownership, progressive scale (10×/100×/1,000×), customer trust, unit economics.

---

## Extra Drill Tables — Online Store

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

*End of Online Store system design prep doc.*
