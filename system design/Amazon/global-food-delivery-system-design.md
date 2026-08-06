# System Design: Global Food Delivery System (Amazon Logistics / Marketplace)

> **Focus areas:** Marketplace matching · ETA · Geo cells · Multi-sided platform · Payments · Fraud · Catalog · Dispatch · Global vs local  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Locality-first architecture; deal-breaker: one global DB + worldwide courier search per order  
> **Interview theme:** Amazon SDE III / L6 — **Global food delivery** (Prime-style / Amazon Food marketplace)

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

Goal: design a **global food-delivery marketplace**—customers, restaurants, couriers—with ordering, payment, dispatch, ETA, tracking, and regional compliance.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | End-to-end food delivery platform | Single-restaurant POS only |
| Topology | City/region cells, global edge | One mega-region monolith |
| Match | Local courier↔order assignment | Worldwide courier scan |
| Success | Hot food on time, trust, unit economics | Raw order QPS vanity |
| Related | Restaurant registration = onboarding sibling | Don’t conflate full KYC portal hour |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Actors? | Customer, restaurant, courier, support | Separate apps + APIs |
| F2 | Order flow? | Browse→cart→pay→confirm→prep→pickup→deliver | State machine |
| F3 | Catalog? | Menus, modifiers, hours, OOS | Per-restaurant, regional |
| F4 | Pricing? | Item + fees + tax + tip + promotions | Quote service durable |
| F5 | Dispatch? | Assign courier near restaurant | Local matcher |
| F6 | Tracking? | Live map ETA | Pub/sub location |
| F7 | Payments? | Capture on delivery or on confirm (policy) | PSP + ledger |
| F8 | Ratings? | Multi-sided | Abuse controls |
| F9 | Global? | Multi-country | Cells + compliance packs |
| F10 | SLA? | Prep time + drive time ETAs | Prediction + buffers |
| F11 | Cancellations? | Policies by stage | Compensating txns |
| F12 | Support? | Chat/tools with order timeline | Omnichannel |

**MVP:** City launch: catalog, checkout, pay, restaurant accept, courier assign, track, complete, basic support.  
**Out:** Dark kitchen IoT, full advertising exchange, drone delivery, global single inventory.

### 1.2 NFRs

| NFR | Target |
|-----|--------|
| Checkout p99 | < 300–500ms (excl. PSP) |
| Dispatch assign | < 5–15s typical |
| Availability | 99.9%+ regional; degrade discovery before checkout break |
| Consistency | Order financials strongly consistent in home cell |
| Privacy | Location minimization; GDPR/CCPA packs |
| Freshness | Courier location seconds; menus minutes |

### 1.3 Cases

Happy: order→accept→assign→pickup→deliver→tip→rate.  
Edges: restaurant reject; no courier; weather surge; payment fail; courier drop; wrong address; allergy modifier miss; cross-border tourist card; city outage cell.

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Cities | 50 | 500 | 5K | 50K |
| Peak orders/s | 2K | 20K | 200K | 2M |
| Couriers online | 100K | 1M | 10M | 100M |
| Jump | Regional cells | Multi-country packs | Hierarchical dispatch | Platformized geo OS |

### 1.5 Repeat-back

“Multi-sided food delivery with **geo cells**, local dispatch, durable orders/payments, ETA/tracking—global product, local data plane.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Base |
|-------|------|
| Browse/search | 100K–1M QPS edge-cached |
| Checkout | 2K orders/s peak |
| Location updates | Couriers × 0.2–1 Hz → huge → sample |
| Dispatch compute | Per active order batch |
| Notifications | Multiplier on order events |

### 2.2 Storage

```text
Orders: 2K/s × 5KB × 86.4K ≈ 864GB/day raw → tier
Menus: millions items; versioned
Location: not long retention raw—aggregate/TTL
```

### 2.3 Bandwidth / location

```text
1M couriers × 0.2 Hz × 100B = 20MB/s → manageable with sampling
At 100×: geohash aggregation + interest-based subscription
```

### 2.4 ETA latency budget

Match features 50ms → model 20ms → map ETA 50–100ms → buffer policy.

### 2.5 Bottlenecks

Hot cities lunch spike; location fanout; restaurant tablet flaky network; payment webhooks; support tools overload in outage.

---

## 3. High-Level Design

### 3.1 Core services

| Service | Role |
|---------|------|
| Edge/API gateway | Auth, routing to home city cell |
| Catalog | Menus, search, hours |
| Cart/Checkout | Quotes, inventory soft holds |
| Order | State machine source of truth |
| Payment | Intent, capture, refunds |
| Restaurant | Accept/reject, prep timers |
| Dispatch | Courier assignment |
| Location | Presence + geofence |
| Tracking/Notify | Customer updates |
| Pricing/Promo | Fees, surge, coupons |
| Fraud/Risk | Account/device/payment |
| Support | Tools + policies |

### 3.2 Order state machine

```text
CREATED → PAID → RESTAURANT_ACCEPTED → COURIER_ASSIGNED →
PICKED_UP → DELIVERED → COMPLETED
Any → CANCELLED (policy)
COURIER_ASSIGNED → REASSIGN on drop
```

### 3.3 Geo cell model

- **City/region cell** owns restaurants, couriers, active orders.  
- Global: identity, payment methods tokens, customer profile.  
- Cross-cell: rare; tourist ordering in visiting city uses that city cell.

### 3.4 Dispatch sketch

```text
active order near restaurant R
candidates = couriers in geohash ring, online, capacity, vehicle
score = ETA_to_R + load + acceptance_prob + fairness - decline_streak
assign with lease; courier accept/reject; timeout → next
```

### 3.5 Trade-offs

| Choice | Why |
|--------|-----|
| Cell-local orders | Latency + blast radius + compliance |
| Soft menu OOS | Reality of restaurants |
| Batch assign windows | Efficiency vs latency |
| Capture policy explicit | Finance correctness |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Customer App --> Edge --> City Cell:
   Catalog | Cart | Order | Pay Adapter | Tracking
                 |
                 +--> Restaurant Gateway
                 +--> Dispatch <--> Location
                 +--> Notify
Global: Identity | Wallet Tokens | Fraud | Config | Analytics
PSP <--> Payment Service (home cell ledger)
```

### 4.2 Sequence: place order

```text
App -> Checkout: quote
App -> Pay: authorize
App -> Order: create(PAID)
Order -> Restaurant: notify
Restaurant -> Order: ACCEPT
Order -> Dispatch: need_courier
Dispatch -> Courier: offer
Courier -> Order: ASSIGNED
... pickup ... deliver ...
Order -> Pay: capture
```

### 4.3 Sequence: no courier

```text
Dispatch timeouts → expand radius / surge / batch
If exhausted: delay prep signal OR cancel with refund per policy
```

### 4.4 Multi-region

Active-active edge; **single-writer home cell per order**; DR runbooks per city.

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Paid order has durable ledger entry before restaurant notify.  
2. At most one assigned courier at a time (lease).  
3. Cancel/refund paths idempotent.  
4. Customer never sees delivered without terminal state rules.  
5. Cell isolation: no cross-city courier steal.

### 5.2 Scalability

- Shard keys: `city_id` then `order_id`.  
- Catalog CDN + edge; personalized thin layer.  
- Location: geohash indexes; subscribers only for relevant orders.  
- Dispatch workers per city queue.

### 5.3 Maintainability

- Order FSM table-driven.  
- Country **compliance packs** (tax, data residency, labor rules).  
- Feature flags per city launch.

### 5.4 ETA system

Components: prep time model, courier travel (map + traffic), handoff buffer, confidence intervals. Show P50 ETA; ops monitors bias.

### 5.5 Payments & fraud

Auth at checkout; capture on deliver or restaurant accept (choose & state). Refunds compensating. Fraud: velocity, device, promo abuse, courier–customer collusion.

### 5.6 Progressive scale

| Jump | Change |
|------|--------|
| 10× | City cells, cache menus, sample locations |
| 100× | Hierarchical dispatch zones; edge quotes |
| 1,000× | Platform geo-OS; on-device browse catalogs |

### 5.7 Deal-breakers

| Deal-breaker | Why |
|--------------|-----|
| Global courier search | Latency/cost explosion |
| Single global order DB | Residency + blast radius |
| Fire-and-forget pay | Money SEVs |
| No reassign path | Stuck food |

---

## 6. Wrap-Up

### 6.1 Decisions

Geo cells; order FSM; local dispatch leases; durable pay before prep; ETA models; compliance packs; degrade discovery first.

### 6.2 Risks

Lunch storms; restaurant tablet reliability; map ETA bias; fraud rings; labor/regulatory shocks; tip/wage policy changes.

### 6.3 45-minute plan

Actors/flow → estimates → cell HLD → order/pay/dispatch deep dive → scale/compliance → traps.

### 6.4 Closer

> **Global Food Delivery**: local cells, durable orders/payments, leased dispatch, ETA/tracking, compliance packs—global UX, local data plane, unit economics explicit.

---

## 7. Deeper / Related Interview Questions

**Q1. Why cells by city?**  
**A:** Locality of supply/demand; legal; blast radius; latency.

**Q2. Batching orders for one courier?**  
**A:** Yes with ETA degradation caps; multi-objective.

**Q3. Restaurant goes offline mid-prep?**  
**A:** Cancel/reassign policy; refund; customer notify.

**Q4. Exactly-once order?**  
**A:** Idempotency keys on checkout; at-least-once events downstream.

**Q5. Surge pricing?**  
**A:** Caps, communication, fairness; regulatory sensitivity.

**Q6. Menu consistency?**  
**A:** Versioned menus; quote pins version.

**Q7. Cross-border payment?**  
**A:** Local PSP rails; currency by city; tax engine.

**Q8. Difference vs restaurant registration?**  
**A:** Registration onboards merchants; this runs marketplace ops.

**Q9. Tracking battery drain?**  
**A:** Adaptive location frequency by phase.

**Q10. Trap: Mongo worldwide mega-cluster?**  
**A:** Push cells + residency.

---

## 8. Appendices

### 8.1 Schema sketches

```text
Order(order_id, city_id, customer_id, restaurant_id, state, quote_id, ...)
OrderItem(order_id, item_id, mods, price)
CourierAssignment(order_id, courier_id, lease_exp, state)
MenuVersion(restaurant_id, version, blob_ref)
Payment(intent_id, order_id, state, amounts)
```

### 8.2 Pseudocode: dispatch

```text
function assign(order):
  for ring in expand(geohash(restaurant), max_r):
     cands = queryOnline(ring).filter(capable)
     ranked = score(cands, order)
     for c in ranked:
        if tryLease(c, order, ttl=20s): offer(c); return
  escalate(order)
```

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Cell | City/region failure domain |
| Lease | Temporary courier assignment claim |
| Quote | Pinned price snapshot |
| Surge | Demand/supply price or pay adjustment |
| Prep timer | Restaurant cooking estimate |

### 8.4 Progressive checklist

10× cells; 100× zone hierarchy; 1,000× geo platform.

### 8.5 Reliability tests

1. Double checkout click → one order.  
2. Courier crash → reassign.  
3. Pay auth fail → no restaurant notify.  
4. Cell outage → other cities healthy.

### 8.6 60s closer

> Customers browse edge-cached catalogs, checkout creates a durable paid order in the city cell, restaurant accepts, dispatch leases a local courier, tracking streams ETA, capture/refund follow policy—global product with local single-writer cells.

---

## Deep Technical Notes — Global Food Delivery

### Quote pinning

Checkout persists `quote_id` with line items, fees, tax, currency, menu version. Order creation must match quote hash.

### Restaurant accept SLA

Timer T; auto-cancel or auto-accept per contract. Measure accept latency as marketplace health.

### Courier fairness

Avoid always assigning nearest star courier; include earnings fairness / idle time in score with guardrails on ETA.

### Location privacy

Customers see coarse courier position until near dropoff; retain minimal history.

### Notifications

Push + SMS fallback; prefer event coalescing (“Out for delivery”) over GPS spam.

### Multi-hop / batch

Model courier route as small VRP; cap added delay (e.g., +8 min) else single order.

### City launch checklist

Supply density, courier pool, maps quality, PSP, tax, support language, fraud baselines.

## Interview Cards — Global Food Delivery

### Card 1: Cell key?

City/region; order home cell single-writer.

### Card 2: Pay before cook?

Durable auth/ledger before restaurant notify.

### Card 3: Dispatch lease?

Prevent double assign; timeout reoffer.

### Card 4: Location scale?

Sample + geohash subscribe.

### Card 5: Batching?

Allowed under ETA caps.

### Card 6: Menu OOS?

Soft; restaurant can mark; quote version.

### Card 7: Compliance pack?

Tax/residency/labor per country.

### Card 8: Deal-breaker?

Global courier search / global order monolith.

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Marketplace scope |
| 5–12 | Numbers + cells |
| 12–22 | HLD diagram |
| 22–35 | Order/pay/dispatch/ETA |
| 35–45 | Fraud, scale, traps |

## 10. Operability

### Golden signals

Order success, accept rate, assign time, delivery ETA error, cancel rate, pay success, cell health, courier online.

### Rollback ladder

Flag off batching → revert dispatch scorer → pause city promotions → cell isolate.

### Kill switches

Disable surge; disable batching; force manual support assign; freeze new restaurants; shed browse personalization.

### Security/privacy

PCI via PSP; PII TTLs; location minimization; partner data contracts.

### Cost worksheet

```text
Maps ETA + SMS + PSP fees + courier pay dominate
Lever: reduce eta API calls via cache; notification coalescing
```

### Cross-team deps

Identity, PSP, Maps, Fraud, Comms, Catalog, Support, Restaurant Onboarding.

---

## More Interview Q&A — Global Food Delivery

**Q1. Soft hold inventory?**  
**A:** Menu items rarely true inventory; restaurant accept is real gate.

**Q2. Tip handling?**  
**A:** Policy by market; ledger separate from merchandise.

**Q3. Scheduled orders?**  
**A:** Create early; dispatch near time; inventory/menu revalidate.

**Q4. Group orders?**  
**A:** Multi-customer cart complexity—defer or limited MVP.

**Q5. Courier pay model?**  
**A:** Influences accept rates; system exposes offer value.

**Q6. Weather?**  
**A:** ETA inflation; surge; pause zones.

**Q7. Allergy correctness?**  
**A:** Modifiers + restaurant confirm; trust SEV if wrong.

**Q8. Hot path datastore?**  
**A:** Cell-local orders DB (SQL/Dynamo); Redis presence.

**Q9. Analytics lag?**  
**A:** Async events; not on checkout critical path.

**Q10. Black Friday restaurant?**  
**A:** City load test; queue accept; cap active orders per shop.

**Q11. Active-active orders?**  
**A:** No—single-writer cell.

**Q12. Customer moves cities?**  
**A:** Browse switches cell by lat/lng or address.

**Q13. Chat support during outage?**  
**A:** Read-only timeline from durable store; scripts.

**Q14. Promo stacking?**  
**A:** Rules engine; fraud on referral loops.

**Q15. Map provider outage?**  
**A:** Cached routes / haversine degrade; flag.

**Q16. What is unit economy metric?**  
**A:** Contribution per order after courier+promo+PSP+support.

---

## Deep Technical Addenda

### Idempotency keys

`Idempotency-Key` on create order & pay; store response for 24h.

### Outbox for restaurant notify

Order txn writes outbox; publisher pushes to restaurant channel; retry/DLQ.

### Presence service

Courier `online` with heartbeat; dead after missed N; remove from dispatch.

### ETA bias monitoring

Track signed error; recalibrate per city/hour-of-week.

### Chargeback flow

Evidence pack: timeline, GPS crumbs (minimized), photos if any, chat logs.

## Tradeoff Matrices — Global Food Delivery

### Assign speed vs batch efficiency

| Choice | ETA | Cost | Use |
|--------|-----|------|-----|
| Instant single | Best | Higher | VIP / sparse |
| Short batch window | Good | Better | **Default lunch** |
| Long batch | Poor UX | Best cost | Avoid |

### Capture timing

| Choice | Risk | UX |
|--------|------|-----|
| Auth@order capture@deliver | Restaurant risk | Flexible cancel |
| Capture@accept | Clearer cook | Harder cancel |

### Consistency

| Data | Model |
|------|-------|
| Order/pay | Strong in cell |
| Menu | Esc read |
| Courier loc | Ephemeral eventual |

## Operability Addenda

### Deploy pipeline

```text
service → unit/contract → city canary → bake → region → global flags
```

### Guardrails

- Pay success drop  
- Assign p99  
- ETA abs error  
- Cancel spike  
- Fraud score anomalies  

### Kill switches

1. Disable batching  
2. Disable surge  
3. Pause city  
4. Force support dispatch  
5. Shed noncritical browse ML  

## Worked Capacity Narrative

Orders/s × write amp; couriers × location Hz with sampling; show cell sharding bends failure domain; lunch 10× needs queue+batch not bigger single matcher.

## Customer-Trust Paragraph

Wrong allergy handling, phantom “delivered,” or silent overcharge are trust SEVs. Prefer delayed assignment messaging over lying ETAs. Refunds idempotent and fast when we fail.

## Progressive Scale Recap

- **10×:** city cells, menu CDN, location sampling  
- **100×:** zone hierarchy, edge quotes, compliance packs  
- **1,000×:** geo platform multi-tenant cells  

---

## Supplemental Depth Pack — Global Food Delivery

### S1. Home cell

Order sticky to city cell.
**Metric:** `cross_cell_write_attempts`.

### S2. Pay durability

Ledger before notify.
**Metric:** `notify_before_pay`.

### S3. Assignment lease

One courier.
**Metric:** `double_assign`.

### S4. Quote pin

Hash match.
**Metric:** `quote_mismatch`.

### S5. Location sampling

Phase-based Hz.
**Metric:** `loc_bytes_per_courier`.

### S6. ETA calibration

Bias dashboards.
**Metric:** `eta_signed_error`.

### S7. Cancel idempotency

Refund once.
**Metric:** `double_refund`.

### S8. Unit economics

Contribution/order.
**Metric:** `contrib_per_order`.

## Scenario Runbooks

| Scenario | Action |
|----------|--------|
| City cell down | Failover DR; pause marketing; support script |
| PSP outage | Queue orders or pause checkout; message |
| Map outage | Degrade ETA; haversine |
| Fraud storm | Tighten rules; freeze promos |
| Weather event | Surge+pause zones |
| Lunch meltdown | Expand batch; raise courier pay; cap restaurants |

## Rapid-Fire Q&A — Global Food Delivery

**Q:** Shard? **A:** City cell.  
**Q:** Global DB? **A:** No.  
**Q:** Dispatch? **A:** Local lease+score.  
**Q:** Pay? **A:** Durable before cook.  
**Q:** Location? **A:** Sampled geohash.  
**Q:** Batch? **A:** ETA-capped.  
**Q:** Menu? **A:** Versioned.  
**Q:** ETA? **A:** Prep+drive+buffer.  
**Q:** Fraud? **A:** Velocity+collusion.  
**Q:** Compliance? **A:** Packs.  
**Q:** Reassign? **A:** Yes on drop.  
**Q:** Tip? **A:** Ledger policy.  
**Q:** Search? **A:** Edge+cell.  
**Q:** Idempotent? **A:** Checkout keys.  
**Q:** Outbox? **A:** Restaurant notify.  
**Q:** Presence? **A:** Heartbeat.  
**Q:** Deal-breaker? **A:** Global courier scan.  
**Q:** 10×? **A:** Cells+cache.  
**Q:** 100×? **A:** Zones.  
**Q:** Metric? **A:** OTA success+ETA error+contrib.  
**Q:** Allergy? **A:** Trust SEV.  
**Q:** Surge? **A:** Capped+clear UX.  
**Q:** Scheduled? **A:** Late dispatch.  
**Q:** Group order? **A:** Defer.  
**Q:** Active-active order? **A:** No.  
**Q:** Tourist? **A:** Visit city cell.  
**Q:** Tablet flaky? **A:** Offline accept queue.  
**Q:** Chargeback? **A:** Evidence pack.  
**Q:** SMS cost? **A:** Coalesce.  
**Q:** Maps cost? **A:** Cache routes.  
**Q:** Fairness? **A:** In score.  
**Q:** Cancel stages? **A:** Policy table.  
**Q:** Ratings abuse? **A:** Filters.  
**Q:** Dark kitchen? **A:** Out MVP.  
**Q:** Drone? **A:** Out.  
**Q:** Registration doc? **A:** Sibling.  
**Q:** Route opt doc? **A:** Courier multi-stop sibling.  
**Q:** Ownership? **A:** Order+Dispatch oncalls.  
**Q:** Lunch spike? **A:** Batch+pay courier.  
**Q:** Phantom delivered? **A:** GPS/photo policy.  
**Q:** Currency? **A:** Per city.  
**Q:** Tax? **A:** Engine in quote.

## Narrative Walkthrough — Global Food Delivery

### Beat 1

Bound marketplace; list actors; reject global monolith.

### Beat 2

Estimate orders + location bandwidth; introduce sampling.

### Beat 3

Draw city cell + global identity/pay tokens.

### Beat 4

Order FSM + pay durability + outbox.

### Beat 5

Dispatch lease loop + batching tradeoff.

### Beat 6

ETA + tracking privacy.

### Beat 7

Fraud, compliance packs, progressive scale.

### Beat 8

Close with trust + unit economics + deal-breakers.

## Pre-Onsite Checklist — Global Food Delivery

- [ ] Cell story  
- [ ] Order states  
- [ ] Pay-before-cook  
- [ ] Dispatch lease  
- [ ] Location sampling math  
- [ ] Progressive scale  
- [ ] Deal-breakers  
- [ ] 60s closer  

### Extra drill

Draw FSM in 45s.

### Extra drill

Location MB/s math.

### Extra drill

Dispatch pseudocode from memory.

### Extra drill

Quote pin fields.

### Extra drill

Cancel/refund matrix.

### Extra drill

Compliance pack contents.

### Extra drill

Batching ETA cap rationale.

### Extra drill

PSP outage runbook.

### Extra drill

Fraud collusion signals.

### Extra drill

Allergy SEV narrative.

### Extra drill

Surge ethics/regulation.

### Extra drill

Presence heartbeat params.

### Extra drill

Outbox vs dual-write.

### Extra drill

Maps degrade mode.

### Extra drill

City launch checklist.

### Extra drill

Tip ledger separation.

### Extra drill

Scheduled order timing.

### Extra drill

Fairness vs ETA tension.

### Extra drill

Kill switches list.

### Extra drill

1000× platform vision.

### Extra drill

Unit contrib formula.

### Extra drill

Idempotency key TTL.

### Extra drill

Restaurant accept timer.

### Extra drill

Reassign loop.

### Extra drill

Edge browse vs cell checkout.

### Extra drill

Data residency note.

### Extra drill

Support timeline sources.

### Extra drill

Interview trap: global matcher.

### Extra drill

60s closer memorization.

### Extra drill

Compare to ride-sharing.

### Extra drill

Compare to retail Amazon.com.

### Extra drill

Notification coalescing.

### Extra drill

Menu CDN invalidation.

---

*End of global food delivery system design.*
