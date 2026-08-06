# System Design: Pizza Shop Software System

> **Focus areas:** Menu · Orders · Kitchen display · Prep stations · Delivery/pickup · Inventory ingredients · Promotions · Multi-store
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Local commerce ops system for a pizza chain (software that runs the shop)**

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

Goal: design the software that runs a **pizza shop / small chain**—take orders (online + POS), route to kitchen, track prep, manage toppings inventory, coordinate pickup/delivery, and keep customer promises under dinner rush.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Shop + kitchen + order execution | DoorDash-scale global logistics network alone |
| Inventory | Ingredient / dough / SKU truth at store | National FC warehouse system |
| Orchestration | Tickets, station timers, driver handoff | Corporate HR payroll |
| Amazon lens | Ops excellence, promise, ownership | Cute restaurant demo only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Channels? | POS, web, app, phone→POS | Unified order model |
| F2 | Menu? | Sizes, crusts, toppings, combos, dayparts | Configurable catalog |
| F3 | Modifiers? | Half-and-half, light cheese, gluten-free | Constraint rules |
| F4 | Kitchen? | KDS tickets by station (make/oven/cut) | Station routing |
| F5 | Promise time? | Quoted ready / delivery ETA | Promise engine |
| F6 | Payments? | Card, cash, gift card; tips | Payment intents |
| F7 | Delivery? | In-house drivers or 3P handoff | Dispatch abstraction |
| F8 | Inventory? | Toppings, dough balls, boxes | Decrement on make |
| F9 | Promos? | 2-for-1, coupons, loyalty | Promo engine rules |
| F10 | Multi-store? | Many stores; local kitchen truth | Store cells |
| F11 | Refunds/remakes? | Burnt pizza remake workflow | Exception states |
| F12 | SLA? | Hot & on-time; rush peaks Fri–Sat | Capacity-aware quoting |

**MVP scope:**

1. Unified order create from POS/online with idempotency key.
2. Menu + modifier validation before accept.
3. Kitchen ticket creation and station state (queued→prep→oven→ready).
4. Promise time quote based on kitchen load.
5. Payment capture / cash drawer basic.
6. Pickup ready notifications; simple delivery assignment.
7. Ingredient decrement + 86 (sold-out) flags.
8. Store dashboard: tickets open, late risk, 86 list.

**Out of MVP:** national dynamic pricing ML, autonomous delivery robots, multi-country tax engine perfection, active-active dual-writer kitchens for same ticket.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Order accept latency | p99 < 300ms after validate |
| N2 | KDS update | p99 < 1s perceived |
| N3 | Durability | No silent lost paid orders |
| N4 | Availability | Store can take POS orders if cloud flap (degrade) |
| N5 | Consistency | Strong per-store order ticket truth |
| N6 | Audit | Who voided/remade/refunded |
| N7 | Peak | Dinner rush 5–10× lunch |
| N8 | Correctness | Never cook unpaid / never lose paid |

### 1.3 Cases

**Happy:** Browse menu → customize pizza → pay → kitchen ticket → bake → ready → pickup/delivery complete.
**Edges:** sold-out topping mid-order; half-and-half rules; card decline after ticket; remake; driver no-show; store offline; double-submit order; coupon stack abuse; oven capacity saturation; allergy notes.

| Case | Behavior |
|------|----------|
| Double submit | Idempotency key → one order |
| 86 topping after cart | Revalidate; offer substitute or cancel line |
| Card capture fail | Don't start make line; hold/cancel ticket |
| Oven backlog | Lengthen quotes; throttle online if needed |
| Remake | New ticket linked; inventory + comps tracked |
| Store offline | POS local queue; sync with conflict rules |

### 1.4 Progressive scale

| Metric | Base (1 store) | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Stores | 1 | 10 | 100 | 1,000 |
| Orders / day / store | 200 | 300 | 400 | 500 |
| Peak orders / min / store | 2 | 4 | 6 | 8 |
| Menu SKUs | 80 | 100 | 120 | 150 |
| KDS events / day / store | 5K | 10K | 20K | 40K |
| Concurrent online sessions | 50 | 200 | 2K | 20K |
| Drivers (in-house) | 4 | 6 | 8 | 10 |
| Promo evaluations / day | 1K | 20K | 200K | 2M |

**Jumps:** 10× = multi-store platform + central menu; 100× = region capacity + franchise config; 1,000× = national chain ops, cell isolation, peak game days (Super Bowl).

### 1.5 Scope repeat-back

> Per-store pizza execution with unified orders, kitchen tickets, promise quoting, payments, inventory/86, pickup/delivery handoff—scaled across stores as cells—optimized for on-time hot food without losing paid orders.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
200 orders/day ≈ 0.002/s avg; dinner peak 10× for 2h
Each order: ~10–30 state events (pay, ticket, station, ready, deliver)
⇒ ~2K–6K events/day/store; 1,000 stores ⇒ millions/day platform
```

### 2.2 Storage

```text
Order row ~2–5 KB with lines/modifiers
200 orders × 365 ≈ 70K orders/year/store → tens of MB
1,000 stores → tens of GB hot; events/logs larger
Receipts/images in object store
```

### 2.3 Latency budget (accept order)

```text
API → validate menu → promo → pay auth → persist → enqueue KDS
50 + 40 + 40 + 100 + 30 + 40 ≈ ~300ms p99 target
```

### 2.4 Bottlenecks

(1) oven/station capacity not HTTP (2) menu/promo misconfig (3) payment latency (4) offline sync (5) driver scarcity (6) 86 races.

### 2.5 Cost / frugality

Labor and food waste dominate; software that reduces remakes and idle oven time pays for itself. Avoid always-on video analytics in MVP.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Catalog / Menu | Items, modifiers, prices, 86 | Strong per store publish |
| Order Ledger | Customer order truth + pay state | Strong per order |
| Kitchen Work | Tickets/stations | Strong per ticket |
| Promise / Capacity | Quotes and throttles | Eventually advisory + hard caps |
| Dispatch | Driver/3P assignment | Lease-based |

**Deal-breaker:** mixing kitchen speculative timers with payment truth—never cook as if paid when payment is pending without explicit policy.

### 3.2 Components

1. **Menu Service** — catalog, modifiers, dayparts, 86 flags
2. **Order Service** — create/validate/idempotent accept
3. **Pricing / Promo Service** — coupons, loyalty, tax lines
4. **Payment Adapter** — auth/capture/void/refund
5. **Kitchen Ticket Service** — station routing + state
6. **Promise / ETA Service** — load-based quotes
7. **Inventory / Prep Service** — dough, toppings counts
8. **Dispatch Service** — drivers or 3P
9. **Notification Service** — SMS/push ready
10. **POS Sync / Edge Agent** — offline degrade
11. **Store Ops Dashboard** — late risk, 86, thruput
12. **Config / Franchise Admin** — menu publish by store

### 3.3 Core API (sketch)

```text
POST /v1/orders
  {idempotency_key, store_id, channel, lines[], promos[], pay_method}
→ {order_id, promise_ts, pay_status, ticket_ids[]}
Idempotent on idempotency_key
PATCH /v1/tickets/{id}/state  {from, to, station, actor}
POST /v1/menu/{store}/eighty_six  {sku, until}
```

### 3.4 State machine

```text
ORDER: CREATED → PAID → IN_KITCHEN → READY → OUT_FOR_DELIVERY → COMPLETED
                 ↘ PAYMENT_FAILED / CANCELLED
                 ↘ REMake_LINKED
TICKET: QUEUED → MAKING → OVEN → CUT_BOX → READY → HANDED_OFF
              ↘ VOID / REMAKE
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Cloud vs edge POS | Edge agent + cloud SoT with offline queue | Dinner rush cannot die on WAN |
| Fire on auth vs capture | Policy flag; default auth+capture for card | Fraud vs speed |
| Shared menu | Central template + store overrides | Franchise reality |
| Delivery | Abstract courier port | In-house and 3P coexist |
| Inventory precision | Decrement estimates + periodic counts | Perfect gram-tracking overkill MVP |

---

## 4. Architecture Diagram

```text
[Customer App/POS] -> API Gateway -> Order Service -> Payment
                                      |
                                      v
                               Kitchen Ticket Service -> KDS Screens
                                      |
 Menu/86 <------------------> Promise/ETA
                                      v
                               Dispatch -> Driver/3P
                                      v
                               Notifications / Receipts

Edge POS Agent <--sync--> Order Ledger (store cell)
```

### 4.1 Primary sequence

```text
Validate lines + modifiers against menu version
Evaluate promos → price quote
Payment auth/capture (idempotent)
Persist order PAID; emit OrderPaid
Create tickets routed to stations
KDS displays; cooks advance states
READY → notify; assign driver if delivery
Complete; inventory adjustments finalized
```

### 4.2 Isolation cell

```text
Each store = isolation cell for kitchen tickets + local inventory
No synchronous cross-store ticket locks
Platform routes customer to store; store executes
Central: menu templates, loyalty, settlements
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Paid order cannot be silently dropped—at-least-once ticket creation with outbox.
2. Idempotent order create on client key.
3. Ticket state transitions validated (no OVEN→QUEUED).
4. 86 checks at accept time; late 86 triggers customer messaging workflow.
5. Refunds/voids require reason + actor.
6. Remake links to original for cost/audit.
7. Promise changes after accept are explicit (delay SMS), not silent.
8. Offline POS sync is ordered per store with conflict policy.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith per store; one PG; one KDS |
| 10× | Multi-store tenants; central menu; shared auth |
| 100× | Store-sharded orders; regional promise; courier partners |
| 1000× | National peak command; franchise hierarchy; chaos drills for Super Bowl |

### 5.3 Maintainability

- Menu/version as data; avoid hardcoding toppings.
- Station routing rules configurable.
- Contract tests for payment adapter.
- Canary menu publish to one store.
- Kitchen load simulator for ETA model changes.

### 5.4 Progressive scale

**1×:** Single store, simple ETA = base + N*minutes, human dispatch.
**10×:** Standard store package; central catalog; shared promo service.
**100×:** Load-based promise, 86 propagation, 3P courier SLA integration.
**1000×:** Multi-brand, franchise roles, extreme peak tooling, advanced waste analytics.

### 5.6 Kitchen capacity & promise

Model oven slots and make-line throughput. Quote = f(open tickets, station backlog, historical bake time). Cap online intake when projected late rate exceeds threshold—Amazon-style customer promise over blind accept.

Separate **quoted promise** (customer-facing) from **internal target**. Track miss rate by daypart.

### 5.7 Modifier & half-and-half rules

Represent pizza as structured lines with segments. Validation grammar prevents illegal combos (e.g., incompatible crust/size). Version menu so in-flight orders keep accepted snapshot.

### 5.8 Offline POS

Edge agent stores accepted cash/card-offline per policy. On reconnect, replay with idempotency keys. Conflict: cloud cancel vs local cook—human PS workflow. Never invent second payment capture.

### 5.9 Inventory & 86 races

Optimistic 86: accept if flag clear; compensate if depleted mid-prep. Periodic count adjusts. Hot toppings (pepperoni) are not a distributed systems excuse for wrong tickets—process discipline matters.

### 5.10 Exactly-once kitchen start

Outbox: OrderPaid → TicketCreate. Consumers idempotent on order_id. KDS reconnect must refresh snapshot not only stream gaps.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Cook before payment without policy | Theft / chargeback chaos |
| Lost paid order on restart | SEV customer trust |
| Global lock across stores | Outage blast radius |
| ETA as constant ignoring backlog | Chronic lateness |
| Promo engine mutating paid price silently | Audit nightmare |
| Dual active writers on same ticket without CRDT/merge rules | Split-brain kitchen |

---

## 6. Wrap-Up

### 6.1 Designed

Per-store pizza execution: menu/86, idempotent orders, payments, kitchen tickets, promise quoting, inventory, dispatch, edge POS sync—scaled by store cells.

### 6.2 Decisions to defend

1. Store cell isolation for kitchen truth
2. Idempotent order + payment keys
3. Planes: catalog / order / kitchen / promise / dispatch
4. Capacity-aware promise
5. Outbox to KDS
6. Menu version snapshot on accept
7. Explicit remake/void audit
8. Courier port abstraction

### 6.3 Risks

- WAN flap during rush
- Oven as true bottleneck mis-modeled
- Coupon abuse
- Driver scarcity evenings
- Franchise config drift

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope shop software vs global delivery marketplace |
| 5–15 | Order+payment+idempotency |
| 15–25 | Kitchen tickets + stations |
| 25–35 | Promise/86/inventory + offline |
| 35–45 | Multi-store scale, peak, ownership |

### 6.5 Closer

> **Pizza Shop Software System**: store-cell kitchen truth, idempotent paid orders, capacity-aware promises, KDS outbox, 86 discipline, progressive multi-store scale, clear ownership when dinner rush breaks.

---

## 7. Deeper / Related Interview Questions

### 7.1 Orders & payments

**Q: Cash order flow?**
A: POS create → PAID_CASH → tickets; drawer reconciliation end of day.

**Q: Card auth then void?**
A: If cancelled pre-make, void/refund via payment adapter idempotent refund_key.

**Q: Split tender?**
A: Multiple pay lines; order PAID only when covered.

**Q: Tip after?**
A: Capture adjustment or separate tip charge per processor rules.

### 7.2 Kitchen

**Q: How route complex order?**
A: Pizza→make/oven; wings→fry; drinks→pack station; assemble at cut.

**Q: Burnt pizza?**
A: Remake ticket; comp reason; inventory waste code.

**Q: Station screen crash?**
A: Reload snapshot by store_id; state in service not only browser.

**Q: Priority tickets?**
A: VIP/late risk sort; fairness caps so starvation doesn't hit normal queue.

### 7.3 Promise & capacity

**Q: Customer asks 'how long?'**
A: Promise service using backlog + bake model; pad for honesty.

**Q: Should we stop online orders?**
A: Throttle when predicted miss > SLO; keep phone/POS per policy.

**Q: Delivery ETA vs ready time?**
A: Ready + dispatch + travel; separate fields.

### 7.4 Menu & promos

**Q: Half pepperoni half veg?**
A: Segmented toppings model; price = max/sum policy configurable.

**Q: Coupon stack?**
A: Explicit stack rules; reject silent double dips.

**Q: Happy hour price?**
A: Daypart price list; snapshot at accept.

### 7.5 Multi-store

**Q: Customer nearest store?**
A: Geo + hours + capacity; not only distance.

**Q: Cross-store transfer mid-bake?**
A: No—cancel/recreate; food doesn't teleport.

**Q: Franchisee custom topping?**
A: Store override SKU with brand approval workflow.

### 7.6 Failure modes

**Q: Payment succeeds, DB write fails?**
A: Idempotent reconcile with processor; outbox/inbox pattern.

**Q: Duplicate KDS ticket?**
A: Upsert on order_id+station.

**Q: Driver steals order?**
A: Handoff scan/photo optional; ops process.

### 7.7 Interview traps

**Q: Design Uber Eats instead?**
A: Clarify scope—shop system can integrate courier.

**Q: Microservices per topping?**
A: Absurd.

**Q: Eventual kitchen state via Kafka only?**
A: Need authoritative ticket store + idempotency.

**Q: Ignore oven capacity?**
A: Deal-breaker for promise.

### 7.8 Metrics

| Metric | Why |
|--------|-----|
| On-time ready % | Customer promise |
| Order accept p99 | Channel UX |
| Remake rate | Quality/waste |
| Ticket age p95 | Kitchen health |
| 86 false-accept rate | Inventory discipline |
| Offline sync lag | Edge health |
| Promo discount leakage | Margin |
| Driver accept latency | Delivery |

### 7.9 Ownership

**Q: Who pages for late-ready spike?**
A: Store ops + kitchen software oncall; promise model owner if quote bug.

**Q: Who pages for double charges?**
A: Payments + Order service IC.

### 7.10 Progressive drill

**10×:** package store software; central menu
**100×:** sharding, courier SLA, franchise config
**1,000×:** national peak command; multi-brand

---

## 8. Appendices

### 8.1 Schema sketches

```text
stores(store_id, tz, capacity_cfg)
menu_items(item_id, version, attrs)
store_menu(store_id, item_id, price, eighty_six)
orders(order_id, store_id, state, promise_ts, pay_state, idem_key UNIQUE)
order_lines(order_id, line_id, sku, modifiers_json, price)
tickets(ticket_id, order_id, station, state, version)
inventory_balances(store_id, sku, qty, version)
dispatches(dispatch_id, order_id, courier_ref, state)
audits(id, actor, action, ref, ts)
```

### 8.2 API checklist

- [ ] Idempotent order create
- [ ] Ticket state transition
- [ ] Eighty-six set/clear
- [ ] Promise quote
- [ ] Payment capture/refund
- [ ] Dispatch assign
- [ ] POS sync batch

### 8.3 Oncall checklist

- [ ] Late-risk wallboard
- [ ] Payment error rate
- [ ] KDS connectivity
- [ ] Offline sync backlog
- [ ] 86 inconsistency reports
- [ ] Promo misprice alerts
- [ ] Rollback menu publish

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| KDS | Kitchen Display System |
| 86 | Sold out / unavailable |
| Daypart | Menu/price by time window |
| Remake | Rework ticket for quality fail |
| Promise | Customer-facing ready/deliver time |
| Edge agent | In-store POS sync process |
| Cell | Store isolation boundary |

### 8.5 Deal-breaker one-liners

- Kafka as only order truth without DB constraints
- Start make line on unpaid by default
- Cross-store synchronous ticket locks
- Constant ETA ignoring backlog

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Order ledger | Order Platform |
| Kitchen tickets | Store Execution |
| Promise/ETA | Promise Science + Eng |
| Payments | Payments |
| Menu publish | Catalog |
| Dispatch | Logistics adapter team |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | 1 app+PG, 2 KDS tablets |
| 10× | Tenant monolith, Redis sessions |
| 100× | Shard by store_id, regional API |
| 1000× | Cell per store DB pool, national CC |

### 8.8 Failure injection

1. Kill Order DB primary — failover; POS degrade mode.
2. Duplicate order POST — idempotent.
3. KDS websocket die — snapshot refresh.
4. Payment timeout — unknown state machine + reconcile.
5. Bad menu canary — rollback store publish.
6. Courier API down — pickup-only mode / queue.

---

## Interview Traps

**Trap: Jump to microservice mesh before order invariants**
Signal: L6 shows paid-order durability first

**Trap: Design ML topping recommender in minute 5**
Signal: Wrong priority vs kitchen truth

**Trap: Global ACID across 1,000 stores**
Signal: Blast radius / latency

**Trap: Treat delivery marketplace as MVP**
Signal: Scope creep

---

## Flash Cards

### Card 1: Idempotent order

Client key unique; retries safe.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Order Platform

### Card 2: Store cell

Kitchen truth local; no cross-store locks.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Store Execution

### Card 3: Promise vs backlog

Quote from capacity; throttle online.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Promise

### Card 4: Outbox to KDS

OrderPaid → tickets at-least-once + upsert.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Payments

### Card 5: 86 race

Revalidate; compensate mid-prep.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Catalog

### Card 6: Offline POS

Queue + reconcile; no double capture.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Logistics

### Card 7: Remake audit

Linked ticket + waste reason.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Store Ops

### Card 8: Menu snapshot

Accepted version frozen on order.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Order Platform

### Card 9: Payment unknown

Reconcile with processor.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Store Execution

### Card 10: Oven bottleneck

Model slots; not only CPU.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Promise

### Card 11: Promo stack rules

Explicit allow/deny matrix.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Payments

### Card 12: Courier port

In-house and 3P behind interface.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Catalog

### Card 13: Late SMS

Promise slip is a first-class event.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Logistics

### Card 14: Deal-breaker

Lose paid orders; cook unpaid blindly.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Store Ops

### Card 15: Metrics

On-time %, remake %, accept p99.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Order Platform

### Card 16: Super Bowl

Freeze risky; scale partitions; staff.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Store Execution

---

## Scenario Runbooks

### R1 — Late-ready spike
Check oven backlog; extend quotes; throttle online; staff make line; verify no KDS outage.

### R2 — Double charge reports
Halt captures if systemic; reconcile processor; patch idempotency; customer refunds.

### R3 — Store offline
Confirm edge agent; local POS mode; sync when up; PS conflicts.

### R4 — 86 incorrect
Clear/set flags; recount toppings; notify open carts.

### R5 — Courier outage
Switch pickup emphasis; queue deliveries; message customers.

---

## Extended Rapid Q&A

**Q: Why snapshot menu version?**
A: Price/modifier disputes after publish.

**Q: Can kitchen edit toppings?**
A: With audit; may requote if unpaid policy.

**Q: Gift cards?**
A: Tender type in payment lines.

**Q: Allergy notes?**
A: First-class order attribute surfaced on KDS prominently.

**Q: Why not CRUD order.status only?**
A: Need event history + idempotent transitions.

**Q: Tax?**
A: Line-level tax calc service; store nexus config.

**Q: Loyalty points?**
A: Post-complete earn; redeem at price time.

**Q: Who sets oven count?**
A: Store config; promise model reads it.

**Q: Mobile web vs app?**
A: Same Order API.

**Q: First dashboard widget?**
A: Late risk + 86 list.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Single global kitchen DB | Latency/outage blast |
| Fire tickets pre-payment always | Losses |
| ETA constant 30 min | Chronic misses |
| No idempotency keys | Duplicate pizzas/charges |
| Microservice per station hardware | Ops nightmare |

---

## LLD Touch (optional)

Classes: `Store`, `MenuVersion`, `Order`, `OrderLine`, `Ticket`, `Station`, `PromiseQuote`, `PaymentIntent`, `EightySixFlag`, `Dispatch`, `EdgeSyncCursor`. Patterns: Idempotency key, Outbox, State machine, Strategy (pricing), Ports/Adapters (courier, pay).

---

## 60-second Narrative

"We isolate each store as a cell for kitchen and inventory truth. Orders are idempotent and payment-safe; tickets reach KDS via outbox. Promises come from real oven/make capacity, not vibes. 86 and remakes are explicit. At chain scale we shard by store, centralize menu/promos, and run peak like Super Bowl with freezes and wallboards. Success is on-time hot food, zero lost paid orders, and clear SEV ownership."

---

## Extra Depth: Station Timing Science

Measure transition histograms make→oven→ready; feed promise model; detect slow station (new cook training) vs systemic oven saturation.

## Extra Depth: Franchise Hierarchy

Brand → franchisee → store. Permissions for menu overrides, comps, refunds. Audit everything money-touching.

## Extra Depth: Peak Game Day

Pre-scale order partitions; simplify menu; freeze promo experiments; staff PS; practice IC communications.

## Extra Depth: Food Safety Notes

Time-in-danger-zone tracking for hold shelf; auto-discard workflow; not only thruput.

## Extra Depth: Observability

Wide events: order_id, store_id, ticket_id, state latency. High-cardinality topping_id aggregated carefully.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How do you handle half-and-half pricing disputes?**
A: Snapshot menu/price version at accept; show line math on receipt; comps go through audited remake/void.

**Q: What if loyalty points redeem and card both fail partially?**
A: Order PAID only when tenders cover total; otherwise cancel or hold without kitchen fire.

**Q: How isolate franchisee data?**
A: Store cell ACL; franchisee can see only their stores; brand admins audited.

**Q: Drive-through channel?**
A: Same Order API with channel=DRIVE_THRU; KDS routing may prioritize.

**Q: Gluten-free contamination workflow?**
A: Special ticket flag + station procedure; not only a modifier string.

**Q: Why not put ETA in the client only?**
A: Clients lie/skew; promise service is SoT for quoted time.

**Q: Inventory cycle count for dough?**
A: Scheduled counts adjust balances; large variance pages ops.

**Q: Catering large orders?**
A: Capacity reservation SKU; may require lead time and manager approve.

**Q: Gift card liability?**
A: Tender + ledger in payments; not kitchen concern.

**Q: How test promise model?**
A: Replay historical ticket timelines in sim before publish.

**Q: What is the SEV definition for lost paid order?**
A: Sev-1 customer trust; IC Order+Payments; make-good + root cause.

**Q: Can cooks mark READY early?**
A: Allowed but late-risk metrics catch gaming; optional photo/pack scan.

**Q: Third-party aggregator double menu?**
A: Channel-specific menu publish; avoid two SoTs—adapters push from ours.

**Q: How do tips affect kitchen?**
A: They don't; separate pay line.

**Q: Alcohol SKU constraints?**
A: Age check workflow at handoff; inventory separate.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT order | Order ledger + pay state |
| Kitchen | Ticket state machine |
| Promise | Capacity-aware |
| Scale | Store cells |
| Peak | Throttle + freeze + staff |
| Kill | Lost paid orders; ignore oven |

---

*End of Pizza Shop Software System design notes (Amazon SDE III prep).*


---

## Extra Depth Pack (Interview Expansion)

### E1: Drill scenario

**Setup:** At progressive scale jump, a failure mode appears that was rare at 1×.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible error rate rises.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Roll back last risky config if correlation exists.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; ownership clear.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E2: Drill scenario

**Setup:** At progressive scale jump, a failure mode appears that was rare at 1×.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible error rate rises.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Roll back last risky config if correlation exists.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; ownership clear.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E3: Drill scenario

**Setup:** At progressive scale jump, a failure mode appears that was rare at 1×.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible error rate rises.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Roll back last risky config if correlation exists.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; ownership clear.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E4: Drill scenario

**Setup:** At progressive scale jump, a failure mode appears that was rare at 1×.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible error rate rises.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Roll back last risky config if correlation exists.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; ownership clear.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

