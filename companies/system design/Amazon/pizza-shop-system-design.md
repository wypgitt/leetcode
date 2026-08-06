# System Design: Pizza Shop Software Platform

> **Focus areas:** Orders · Kitchen display (KDS) · Delivery/pickup · Topping inventory · Peak Friday-night scale · Real-time prep state  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct order→kitchen→fulfillment lifecycle, inventory arithmetic under contention, split QPS (customer vs KDS vs dispatch), explicit deal-breakers for “poll everything” fantasies

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

Goal: **bound a multi-location pizza-shop software platform**—customer ordering, kitchen display, pickup/delivery orchestration, topping/ingredient inventory that doesn’t oversell during Friday-night peaks—not a full DoorDash marketplace or POS hardware deep dive.

### 1.0 What this is / is not

| Dimension | **Pizza shop platform (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Take orders correctly; cook in sequence; fulfill pickup/delivery | Full gig-marketplace matching deep dive |
| Success | No silent lost orders; kitchen sees truth; inventory doesn’t go negative | Perfect culinary recipe ML |
| Inventory | Toppings, dough, boxes, drinks—store-local | Global Amazon FC network |
| Money | PSP checkout + refunds | Full double-entry bank product |
| Real-time | KDS + driver ETA updates | Video streaming kitchen cams |

**Scope statement:** Design pizza-shop software covering online/in-store orders, kitchen display, pickup & delivery handoff, topping inventory, and Friday-night peak scale—with progressive 10×/100×/1,000× thinking and Amazon-style operational ownership.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Single shop or chain? | **Multi-store chain** (dozens → thousands) | Store as tenancy/partition key |
| F2 | Order channels? | App/web + in-store POS + phone (agent) | Unified Order API; channel metadata |
| F3 | Menu? | Pizzas (size/crust/toppings), sides, drinks; store hours & modifiers | Catalog service; store overrides |
| F4 | Customization? | Half-and-half, extra cheese, remove toppings, special instructions | Line-item option model; price rules |
| F5 | Kitchen display? | Real-time tickets; bump when done; station routing (make/oven/cut/box) | Push to KDS; store-local fanout |
| F6 | Fulfillment? | Pickup + delivery (own drivers and/or 3P) | Fulfillment mode + dispatch adapter |
| F7 | Inventory? | Toppings/ingredients decrement; 86 items when out | Soft/hard inventory per store SKU |
| F8 | Payments? | Card via PSP; tip; refunds/voids | Idempotent pay; capture on complete or auth at place |
| F9 | Promises? | Quote prep + delivery ETA at checkout | Promise engine from queue depth + distance |
| F10 | Loyalty/promos? | Simple coupons MVP | Pricing hook; stack deferred |
| F11 | Staff roles? | Manager, cook, driver, cashier | AuthZ by store + role |
| F12 | Reporting? | Sales, waste, prep times, late orders | Event stream → warehouse |

**MVP functional scope (lock with interviewer):**

1. Store-scoped menu + hours + delivery radius.  
2. Place order (pickup/delivery) with toppings customization; payment auth.  
3. Inventory check/reserve for constrained toppings at place-order.  
4. Push order to **Kitchen Display System**; bump stations; mark ready.  
5. Pickup handoff or delivery dispatch (own fleet stub + 3P adapter).  
6. Customer status: `CONFIRMED → PREPARING → BAKING → READY → OUT_FOR_DELIVERY → DELIVERED`.  
7. 86 / restock flows for managers.  
8. Friday-night peak: queueing, backpressure, graceful ETA degradation.

**Out of MVP (explicitly defer):**

- Full DoorDash-class multi-restaurant marketplace  
- Dynamic pricing ML / demand shaping platform  
- IoT oven telemetry as SoT  
- Franchise royalty billing deep dive  
- Perfect multi-region active-active order writes per store  
- Voice ordering / Alexa as primary channel

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Place-order latency | Interactive checkout | p50 < 300ms, p99 < 1s excl. PSP |
| N2 | KDS freshness | Cooks see new tickets fast | p99 push < 2s from confirm |
| N3 | Order durability | Never lose paid order | Quorum commit before ACK |
| N4 | Inventory correctness | No silent negative toppings | Strong per-store SKU reservation |
| N5 | Peak availability | Friday 6–9pm must survive | 99.9% place-order; degrade ETA/promos first |
| N6 | Consistency | Menu eventual OK; orders/inventory strong | Split planes |
| N7 | Multi-store isolation | Store A blast ≠ Store B | Cell/partition by `store_id` |
| N8 | Operability | Own the pager | SLOs, kill switches, store-level feature flags |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Customer builds pizza → checkout → pay auth → inventory reserved → order `CONFIRMED` → KDS ticket → make/oven/cut → `READY` → pickup or driver assign → deliver → capture tip/payment finalize.  
2. In-store POS order → same kitchen queue with priority flag.  
3. Manager 86s mushrooms → menu modifier disabled → open carts warned at checkout.  
4. Delivery: geocode address → radius check → quote ETA → dispatch on `READY`.  
5. Customer cancels before kitchen starts → release inventory + void/refund.  
6. Half-and-half pizza priced correctly; allergy note surfaces on KDS.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click Place Order | Idempotency key → one order |
| Pepperoni race (last portion) | One reservation wins; other fails with refresh |
| Payment succeeds, reserve fails | Void auth; no orphan kitchen ticket |
| Reserve succeeds, payment fails | Release inventory; order `PAYMENT_FAILED` |
| KDS tablet offline | Buffer + replay; audible/SMS fallback for store |
| Oven backlog spike | Promise engine stretches ETA; optional pause online orders |
| Driver no-show | Reassign; customer notified; SLA clock |
| Address outside radius | Reject at quote; suggest pickup |
| Special instructions abuse | Length limits; no PII in kitchen print if policy |
| Partial refund (missing topping) | Line adjust + inventory not restocked if cooked |
| Store closed mid-checkout | Reject place; cart kept |
| Split payment / gift card | Phase 1.5; MVP single tender |
| 3P courier API timeout | Retry with idempotency; fallback own driver / pickup offer |
| Menu price change mid-cart | Reprice at place; confirm if delta |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Stores | 50 | 500 | 5K | 50K |
| Peak orders/min (chain) | 200 | 2K | 20K | 200K |
| Peak place-order QPS | ~20 | ~200 | ~2K | ~20K |
| Peak KDS events/s | ~100 | ~1K | ~10K | ~100K |
| Concurrent kitchen tablets | 200 | 2K | 20K | 200K |
| Menu SKUs (global) | 500 | 1K | 2K | 5K |
| Store-local inventory SKUs | ~80 | ~80 | ~100 | ~120 |
| Delivery tracking updates/s | 50 | 500 | 5K | 50K |
| Friday peak vs weekday | 5–8× | 5–8× | 5–8× | 5–8× |
| Avg toppings/order | 3–4 | 3–4 | 3–4 | 3–4 |

**Split write classes (deal-breaker if mixed):** place-order ≠ KDS bump ≠ inventory adjust ≠ driver GPS pings ≠ analytics.

**What each jump forces:**

- **10×:** Store-partitioned order DB; Kafka order events; Redis inventory cache + DB SoT; websocket/SSE gateway for KDS.  
- **100×:** Regional cells; per-store hot partitions; promise service; 3P dispatch fleets; CQRS customer tracking.  
- **1,000×:** Edge menu/CDN; store cells; hierarchical inventory (store → region supply); chaos-tested Friday playbooks; cell blast-radius isolation.

### 1.5 Etc. (Constraints & Assumptions)

- Money in **integer minor units**; never float.  
- Inventory units: grams/portions as integers (e.g., pepperoni “shots”).  
- One **home region** for a store’s order writes (single-writer store home).  
- Drivers: MVP own fleet + pluggable 3P; matching algorithm thin.  
- Kitchen stations configurable per store but same event model.  
- Clocks: server time for SLA; tablets sync NTP.

**Scope statement:**

> Design a multi-store pizza-shop platform: menu, customized orders, topping inventory reservation, kitchen display with station bumps, pickup/delivery fulfillment, payment hooks, and Friday-night peak survival—from ~50 stores through 10× / 100× / 1,000× with store-partitioned ownership and split real-time planes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (deal-breaker if mixed)

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Browse/menu** | Cached reads | 2K/s | 2M/s | CDN + edge |
| **Place order** | Strong write | 20/s | 20K/s | Order + inventory |
| **KDS push/bump** | Store fanout | 100/s | 100K/s | Realtime gateway |
| **Driver GPS** | High-churn loc | 50/s | 50K/s | Location pipeline |
| **Customer track** | Poll/push status | 500/s | 500K/s | Read models |
| **Inventory adjust** | Manager/receive | 5/s | 5K/s | Inventory service |

### 2.2 Friday-night math

```text
50 stores × 8 orders/min peak ≈ 400 orders/min ≈ 6.7/s average chain
Design peak ~20/s with headroom (bursts, retries, POS+online)

Each order:
  1 place + payment
  1 inventory reserve (N topping lines)
  ~5–15 KDS state events (create, station bumps, ready)
  ~10–60 GPS pings if delivery (15–40 min trip)
→ realtime events ≫ place-order QPS
```

### 2.3 Storage

| Data | Size sketch | Retention |
|------|-------------|-----------|
| Order + lines | ~2–5 KB | Hot 90d; cold archive |
| KDS events | ~200 B × 10 | 7–30d operational |
| Inventory ledger | ~100 B/adjust | 1y+ audit |
| Menu versions | small | forever (versioned) |
| Driver tracks | high volume | downsample after 48h |

```text
Baseline 50 stores × 400 orders/day × 3 KB ≈ 60 MB/day orders
10× → 600 MB/day; 100× → 6 GB/day — trivial vs realtime fanout cost
```

### 2.4 Inventory contention

Hot toppings (pepperoni, mozzarella) on Friday:

```text
Reserve path must be O(1) per store-SKU under concurrency.
Optimistic UI availability ≠ commit reservation.
Cache can be wrong low/high; DB reservation is SoT.
```

### 2.5 Promise / ETA economics

```text
prep_seconds ≈ base_make + (queue_pizzas × marginal) + oven_factor
delivery_seconds ≈ drive_time(distance, traffic) + handoff
quote = now + prep + delivery + buffer
buffer grows with queue variance (p95, not mean)
```

### 2.6 Bandwidth / realtime

KDS: small JSON tickets over websocket; prefer store-scoped channels.  
Customer app: status push or 5–15s poll with ETag—not 1Hz hammer.  
Driver GPS: 2–5s while `OUT_FOR_DELIVERY`; batch/compress.

---

## 3. High-Level Design

### 3.1 UX surfaces

| Surface | Actors | Needs |
|---------|--------|-------|
| Customer app/web | Diners | Menu, cart, checkout, tracking |
| POS | Cashiers | Fast ticket entry, cash/card |
| KDS tablets | Kitchen | Tickets, bump, recall, 86 badges |
| Manager console | GMs | 86, hours, labor, overrides |
| Driver app | Couriers | Offer, navigate, complete |
| Ops admin | Chain ops | Multi-store health, kill switches |

### 3.2 Domain model

```text
Store(store_id, region, timezone, geo, hours, delivery_config)
MenuItem / Modifier / Recipe(components → ingredient_sku, qty)
Cart → Order(order_id, store_id, channel, fulfillment, status, promise_at)
OrderLine(item, options[], qty, price_cents, special_instructions)
InventoryItem(store_id, sku, on_hand, reserved, safety_stock)
Reservation(order_id, sku, qty, state)
KitchenTicket(order_id, stations[], priority, bumped_at)
Fulfillment(pickup|delivery, driver_id?, courier_ext_id?, eta)
Payment(intent_id, auth, capture, tip)
```

**Order state machine (simplified):**

```text
DRAFT → PENDING_PAYMENT → CONFIRMED → IN_KITCHEN → READY
  READY → PICKED_UP (pickup)
  READY → DISPATCHED → OUT_FOR_DELIVERY → DELIVERED
  * → CANCELLED / REFUNDED (policy gates)
```

### 3.3 Service map

| Service | Responsibility | Consistency |
|---------|----------------|-------------|
| Catalog/Menu | Items, modifiers, store overrides | Eventual + CDN |
| Cart | Session carts | Durable eventual |
| Order | Place, state machine, idempotency | Strong per order |
| Inventory | Reserve/commit/release per store-SKU | Strong per shard |
| Promise | ETA quotes | Soft real-time |
| Kitchen | Tickets, stations, bumps | Strong per store queue |
| Fulfillment/Dispatch | Assign drivers / 3P | Strong per order |
| Payment | PSP adapter | Idempotent money |
| Notification | Push/SMS | At-least-once |
| Tracking Read Model | Customer-visible status | Eventual CQRS |

### 3.4 Menu & customization

- Global recipe templates; store can disable/86 toppings.  
- Price rules: base + size + topping count tiers + half-and-half max(halfA, halfB) or sum—**pick & defend**.  
- Version menu: `menu_version` stamped on order for audit.  
- Allergen flags denormalized onto KDS ticket.

### 3.5 Inventory (toppings)

**Model:** `available = on_hand - reserved` (never sell `available < need`).

**Flows:**

1. **Quote/availability:** read cache OK.  
2. **Place order:** transactional reserve (or conditional update).  
3. **Kitchen start / complete:** optional commit from reserved → consumed.  
4. **Cancel before consume:** release reserved.  
5. **Receive stock / waste / 86:** manager adjustments with reason codes.

**86:** when `available <= 0` or manager force → publish menu disable event → edge cache invalidate for that store topping.

### 3.6 Kitchen Display System

- On `CONFIRMED`, emit `KitchenTicketCreated` → store channel.  
- Stations: Make → Oven → Cut/Box (configurable).  
- Bump = state transition with actor + timestamp (prep analytics).  
- Priority: dine-in/POS vs delivery SLA risk (aging tickets highlight).  
- Offline: local queue with reconnect replay; never invent order IDs client-side.

### 3.7 Fulfillment: pickup vs delivery

**Pickup:** notify customer at `READY`; QR/code handoff optional.  
**Delivery:**

1. Geocode + radius + fee quote at checkout.  
2. On `READY` (or parallel when oven starts—trade-off), create dispatch job.  
3. Assign own driver (nearest available) or call 3P API with idempotency key.  
4. Track GPS → customer map.  
5. Complete → capture remaining / tip finalize.

### 3.8 Payment hooks

- Auth at place; capture on `DELIVERED`/`PICKED_UP` (or auth+capture—defend).  
- Tips: auth with tip estimate or re-auth; industry pattern: incremental auth.  
- Refunds: partial line vs full; inventory restock only if not consumed.

### 3.9 Promise engine

Inputs: store queue depth, historical prep curves by hour/DOW, driver availability, distance/traffic.  
Output: `promise_at` + confidence band.  
Under overload: widen band, pause online, or cap cart complexity (max pizzas).

### 3.10 API sketch

```text
POST   /v1/stores/{id}/carts/{cart_id}/items
POST   /v1/stores/{id}/orders                    Idempotency-Key
GET    /v1/orders/{id}
POST   /v1/orders/{id}/cancel
GET    /v1/stores/{id}/menu
POST   /v1/stores/{id}/inventory/adjust
POST   /v1/kitchen/tickets/{id}/bump
POST   /v1/fulfillment/{order_id}/assign
POST   /v1/payments/...                          (PSP-backed)
WS     /v1/stores/{id}/kds/stream
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
                    ┌─────────────┐
   Customer/POS ───▶│ API Gateway │─── rate limit / auth
                    └──────┬──────┘
           ┌───────────────┼────────────────┐
           ▼               ▼                ▼
      Menu/CDN         Order Svc        Cart Svc
           │               │
           │               ├──────────▶ Inventory Svc (store shard)
           │               ├──────────▶ Payment Adapter ──▶ PSP
           │               └──────────▶ Promise Svc
           │
           ▼
      Kafka / Event Bus
      topics: orders, inventory, kitchen, fulfillment, payments
           │
     ┌─────┴──────┬────────────┬──────────────┐
     ▼            ▼            ▼              ▼
  Kitchen      Dispatch     Tracking       Analytics
  Fanout       Workers      Read Model     Warehouse
     │            │
     ▼            ▼
  KDS WS      Driver App / 3P Courier
  Gateway
```

### 4.2 Place-order sequence

```text
Client                  Order                 Inventory           Payment            Bus
  |--place(idem)------▶|                      |                   |                  |
  |                    |--reserve------------▶|                   |                  |
  |                    |◀--ok-----------------|                   |                  |
  |                    |--auth-----------------------------------▶|                  |
  |                    |◀--authorized-----------------------------|                  |
  |                    |--commit CONFIRMED---|                   |                  |
  |                    |----------------------------------------▶| KitchenTicket   |
  |◀--201 order--------|                      |                   |                  |
```

### 4.3 Failure compensate

```text
If payment fails after reserve: release inventory; mark PAYMENT_FAILED
If payment succeeds, kitchen publish fails: outbox retry (order durable first)
If bump arrives for unknown ticket: reject; alert (never invent)
If 3P dispatch uncertain: inquire by idempotency; don't double-create
```

### 4.4 Friday-night control plane

```text
Load shedder (per store):
  if kitchen_queue > threshold OR payment_error_rate high:
     disable complex customizations OR pause online OR stretch ETA
Admission: token bucket per store on place-order
KDS: coalesce bursts; backpressure slow tablets
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Paid/confirmed order ⇒ durable row** before client 2xx.  
2. **Idempotent place-order** (`Idempotency-Key` + body hash).  
3. **Inventory: no negative available** under concurrency.  
4. **Kitchen ticket exists iff order CONFIRMED** (outbox).  
5. **Valid state transitions only** (CAS / version).  
6. **Money: no double capture**; PSP webhooks idempotent.  
7. **Cancel before consume ⇒ inventory released exactly once**.  
8. **Store single-writer home** for orders/inventory.  
9. **KDS at-least-once delivery + idempotent apply** of ticket versions.  
10. **Integer money & inventory units**.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; PG by store_id index; Redis pubsub KDS |
| 10× | Order/inventory services; Kafka; WS gateway; per-store partitions |
| 100× | Regional cells; hot-store isolation; CQRS tracking; dispatch fleets |
| 1000× | Store cells; edge menu; supply-chain inventory hierarchy; global ops mesh |

**Hot store problem:** stadium Friday—dedicated partition, higher KDS capacity, optional read replicas for tracking only.

### 5.3 Maintainability

- Contract tests for POS + KDS clients  
- Deterministic inventory property tests  
- Order timeline UI for support (“why late?”)  
- Feature flags: pause delivery, force pickup-only  
- Recipe/version migration playbooks  

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× (~50 stores)**

- Modular monolith; Postgres; Stripe-class PSP.  
- Redis for menu cache + KDS pub/sub.  
- Cron inventory low-stock alerts.  
- Single region.

**10× (~500 stores)**

- Extract Order, Inventory, Kitchen Fanout.  
- Outbox → Kafka.  
- Websocket tier sticky by `store_id`.  
- Promise service from queue metrics.

**100× (~5K stores)**

- Cells by geo region; store home cell.  
- Sharded inventory (`hash(store_id)`).  
- Multi-courier routing; driver supply forecasting thin.  
- Auto pause online per store on SLO breach.

**1000× (~50K stores)**

- Edge config/menu; cell blast radius.  
- Regional supply planning feeding store on_hand.  
- Real-time ops control tower.  
- Chaos drills every “Super Bowl Sunday” class event.

### 5.5 Inventory deep dive — oversell prevention

```text
BEGIN;
SELECT available FROM inv WHERE store=? AND sku=? FOR UPDATE; -- or atomic UPDATE
UPDATE inv SET reserved = reserved + :q
 WHERE store=? AND sku=? AND (on_hand - reserved) >= :q;
-- rows_affected == 1 else fail
INSERT reservation(...);
COMMIT;
```

Alternatives: Redis Lua reserve + async DB reconcile—**only if** you accept reconcile complexity; interview-strong answer prefers DB SoT for scarce toppings.

### 5.6 KDS delivery semantics

- Ticket document version increments on each bump.  
- Clients ACK versions; server replays gaps on reconnect.  
- Don’t use “query all open orders every second” as primary—kill the DB on Friday.  
- Print bridge: optional local agent; same event stream.

### 5.7 Dispatch thin design

Score drivers: distance, load, shift, late risk.  
Offer timeout → next driver.  
3P: create delivery with idempotency key = `order_id`.  
Uncertainty: poll 3P status; customer sees coarse ETA.

### 5.8 Observability (Amazon ops bar)

| SLO | Signal |
|-----|--------|
| Place-order success | 99.9% excl. customer errors |
| Confirm→KDS visible | p99 < 2s |
| Prep time vs promise | bias + p95 error |
| Inventory conflict rate | spikes ⇒ bad cache or understock |
| Late delivery % | dispatch + traffic |

**Kill switches:** pause online ordering per store; disable delivery; simplify menu; shed GPS precision.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Global inventory table without store key | Hot rows + wrong store stock |
| KDS polls SQL every 500ms | Friday meltdown |
| Float cheese grams | Drift / exploits |
| ACK order before durable | Lost paid pizza |
| Blind retry 3P create | Double courier cost |
| Active-active order writes | Duplicate kitchen tickets |
| Cache as inventory SoT | Oversell pepperoni |

---

## 6. Wrap-Up

### 6.1 What we designed

A multi-store pizza platform: menu/custom orders, strong topping reservation, kitchen display via event fanout, pickup/delivery fulfillment, payment hooks, promise ETAs, and Friday-night load controls—with store-partitioned single-writer homes.

### 6.2 Key decisions worth defending

| Topic | Decision |
|-------|----------|
| Tenancy | `store_id` partition / cell |
| Inventory | DB reservation SoT; cache advisory |
| Kitchen | Push tickets + versioned bumps |
| Money | PSP auth at place; capture on complete |
| Realtime | Split GPS/KDS/customer planes |
| Peak | Per-store admission + promise degrade |

### 6.3 Risks & follow-ups

1. KDS offline during peak  
2. Inventory cache lying  
3. 3P courier uncertainty  
4. Promise underestimation → refunds/CS load  
5. Hot stadium store saturation  

### 6.4 How to present in 45 minutes

| Min | Focus |
|-----|-------|
| 0–5 | Scope: multi-store, orders, KDS, inventory, peak |
| 5–15 | Order state machine + place-order saga |
| 15–25 | Inventory reservation + 86 |
| 25–35 | KDS realtime + fulfillment |
| 35–45 | Friday scale, SLOs, deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Orders & idempotency

**Q: Customer double-submits checkout?**  
A: `Idempotency-Key` returns same `order_id`; no second kitchen ticket.

**Q: POS vs online same kitchen?**  
A: Unified order model; channel + priority fields.

**Q: When is order “real”?**  
A: After durable `CONFIRMED` (payment authorized + inventory reserved)—not on cart.

### 7.2 Inventory & toppings

**Q: Soft hold in cart?**  
A: Optional short TTL soft hold; hard reserve at place. Don’t soft-hold forever.

**Q: Recipe uses 40g pepperoni—track grams or shots?**  
A: Integer base units; convert recipe to base units server-side.

**Q: Waste / remake?**  
A: Adjustment ledger with reason; remake may skip re-charge policy.

**Q: Cross-store transfer of toppings?**  
A: Phase 1.5 supply movement; still per-store on_hand.

### 7.3 Kitchen display

**Q: Websocket vs SSE vs poll?**  
A: WS/SSE push per store; poll only fallback.

**Q: Station routing for half-and-half?**  
A: One ticket with two make lines or linked tickets—consistent bump rules.

**Q: Recall after bump?**  
A: Allowed transitions with audit; inventory already consumed—manager override.

### 7.4 Delivery & pickup

**Q: Assign driver before pizza ready?**  
A: Early assign reduces wait but burns driver time—threshold by prep ETA.

**Q: Batch multiple orders per driver?**  
A: Small batching by proximity/route; watch food quality SLA.

**Q: Geofence proof of delivery?**  
A: Optional; photo/signature Phase 1.5.

### 7.5 Payments & tips

**Q: Tip after delivery?**  
A: Incremental auth or delayed capture adjustment within PSP rules.

**Q: Refund missing topping after bake?**  
A: Partial refund; no inventory restock.

### 7.6 Promise / ETA

**Q: Mean vs p95?**  
A: Quote with buffer from p95 queue delay; show range under load.

**Q: Traffic provider down?**  
A: Haversine + historical speed fallback; widen ETA.

### 7.7 Scale & cells

**Q: Why not one global orders table forever?**  
A: Works early; hot stores and regional latency force `store_id` cells.

**Q: Multi-region active-active for a store?**  
A: Avoid for writes; RPO≠0 kitchen duplicates. Single home cell.

### 7.8 Failure injection (drill)

| Inject | Expect |
|--------|--------|
| Inventory DB latency | Shed place-order; keep KDS on open orders |
| Kafka down | Outbox piles; KDS lag alert; don’t ACK new confirms if policy strict |
| PSP timeout | Uncertainty inquire; no double auth |
| All drivers busy | Pickup offer / 3P / pause delivery |
| Tablet fleet disconnect | Local cache + SMS to store phone |

### 7.9 Amazon Leadership-flavored probes

**Q: Customer obsession—late pizza?**  
A: Transparent ETA updates, proactive refunds thresholds, root-cause prep metrics.

**Q: Frugality—do we need Kafka day one?**  
A: Start outbox+worker; introduce bus when fanout fans out.

**Q: Ownership—who pages?**  
A: Per-service SLOs; store-level vs platform-level runbooks.

### 7.10 Comparison traps

| Trap | Better |
|------|--------|
| “It’s just Uber Eats” | You own kitchen + inventory; not only marketplace |
| “Mongo for everything” | Inventory needs conditional atomic updates |
| “Microservices first” | Modular monolith until seams hurt |
| “Exact GPS every second for all” | Only active deliveries; downsample |

### 7.11 Extra interviewer traps (high value)

**Q: How do you prevent two KDS from bumping differently?**  
A: Single writer per ticket version; bumps serialised on order/ticket row.

**Q: Cart reserved mushrooms for 2 hours?**  
A: Don’t—soft TTL seconds/minutes max; hard at pay.

**Q: Is menu CDN consistency required for price?**  
A: Checkout reprices from SoT; CDN OK for browse.

### 7.12 Progressive scale Q&A

**Q: What breaks first at 10×?**  
A: KDS polling and inventory row contention on hot toppings.

**Q: At 100×?**  
A: Cross-region latency if store home wrong; dispatch API rate limits.

**Q: At 1000×?**  
A: Ops control plane and cell isolation—not pizza math.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- orders
orders(
  order_id PK,
  store_id,
  user_id NULL,
  channel,
  status,
  fulfillment_type,
  promise_at,
  menu_version,
  price_cents,
  tip_cents,
  idempotency_key UNIQUE,
  version,
  created_at
);

order_lines(
  line_id PK,
  order_id,
  item_id,
  payload_json, -- modifiers
  qty,
  line_price_cents
);

inventory(
  store_id,
  sku,
  on_hand,
  reserved,
  safety_stock,
  PRIMARY KEY(store_id, sku)
);

reservations(
  reservation_id PK,
  order_id,
  store_id,
  sku,
  qty,
  state, -- HELD|COMMITTED|RELEASED
  UNIQUE(order_id, sku)
);

kitchen_tickets(
  ticket_id PK,
  order_id UNIQUE,
  store_id,
  status,
  station,
  version,
  priority,
  created_at
);

fulfillments(
  order_id PK,
  driver_id NULL,
  external_delivery_id NULL,
  status,
  eta
);
```

### 8.2 API checklist

| API | Idempotent? | Strong consistency? |
|-----|-------------|---------------------|
| Place order | Yes | Yes |
| Cancel | Yes | Yes |
| Inventory adjust | Yes (key) | Yes |
| KDS bump | Yes (ticket version) | Yes |
| Dispatch create | Yes | Yes |
| Menu read | N/A | Eventual OK |

### 8.3 State transition checklist

```text
PENDING_PAYMENT → CONFIRMED | PAYMENT_FAILED
CONFIRMED → IN_KITCHEN → READY
READY → PICKED_UP | DISPATCHED
DISPATCHED → OUT_FOR_DELIVERY → DELIVERED
CANCELLED from {PENDING_PAYMENT, CONFIRMED, IN_KITCHEN?} per policy
```

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| 86 | Mark item/topping unavailable |
| KDS | Kitchen Display System |
| Bump | Advance ticket station/state |
| Promise | Quoted ready/delivery time |
| Soft hold | Temporary cart reservation |
| Hard reserve | Checkout inventory lock |
| Outbox | DB-txn + async publish pattern |
| Cell | Failure-isolated deployment shard |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Durable orders, basic KDS, inventory atomicity |
| 10× | Event bus, WS gateway, per-store partitions |
| 100× | Regional cells, auto pause, CQRS tracking |
| 1000× | Edge menu, supply hierarchy, chaos Friday drills |

### 8.6 Place-order saga (compensation matrix)

| Step done | Later fails | Compensate |
|-----------|-------------|------------|
| Reserve | Payment | Release reserve |
| Payment | Persist confirm | Void/refund + release if needed |
| Confirm | KDS publish | Outbox retry (no cancel) |
| KDS | Dispatch | Retry dispatch; order still READY |
| Dispatch | Deliver | Reassign / refund policy |

### 8.7 KDS ticket payload sketch

```json
{
  "ticket_id": "t_123",
  "order_id": "o_9",
  "version": 3,
  "station": "OVEN",
  "priority": "SLA_RISK",
  "lines": [
    {"name": "Large Pepperoni", "mods": ["extra cheese"], "allergy": ["dairy"]}
  ],
  "fulfillment": "DELIVERY",
  "promise_at": "2026-08-06T19:25:00-07:00"
}
```

### 8.8 Inventory reservation pseudocode

```text
function reserve(store, order_id, lines, idem_key):
  if seen(idem_key): return prior_result
  sort lines by sku  # deadlock avoidance
  tx:
    for line in lines:
      ok = atomic_reserve(store, line.sku, line.qty)
      if not ok: rollback; return SOLD_OUT
    write reservations
  return OK
```

### 8.9 Friday-night runbook (interview gold)

1. Watch: place-order error rate, KDS lag, promise bias, inventory conflicts.  
2. If KDS lag > 5s: scale fanout; shed non-critical GPS.  
3. If inventory conflicts spike: audit cache; check supplier short.  
4. If kitchen queue > N: pause online or delivery-only stretch.  
5. Comms: banner “45–60 min”; proactive coupons threshold.  
6. Postmortem: prep staffing vs demand forecast.

### 8.10 Reliability / chaos drills

| Drill | Pass criteria |
|-------|---------------|
| Kill inventory primary | Failover < RTO; no negative stock |
| Partition KDS gateway | Reconnect replay; no duplicate cook |
| PSP latency 5s | Timeouts orderly; uncertainty protocol |
| Burst 10× orders 10 min | Admission; p99 place within SLO or clean shed |

### 8.11 Interview “say this” summary (60 seconds)

> Multi-store pizza platform partitioned by store. Place-order saga: idempotent pay + hard topping reservation, then outbox to kitchen. KDS is push/versioned, not SQL poll. Delivery is thin dispatch with 3P idempotency. Friday peaks: per-store admission, promise degrade, kill switches. Single-writer store homes; split QPS classes; integer money/inventory.

### 8.12 Extra traps

- Using customer GPS as order SoT  
- Printing PII on kitchen tickets carelessly  
- Shared Redis key `pepperoni` without store id  
- Capturing payment before knowing store can make pizza  

### 8.13 Related systems map

| System | Relation |
|--------|----------|
| Online store | Cart/checkout patterns |
| Ticketing | Holds vs inventory reserves |
| Dispatch/logistics | Driver assignment |
| Payment platform | Auth/capture/refund |
| Realtime chat | WS fanout lessons |

### 8.14 Estimation cheat-sheet

```text
orders/s ≈ stores × orders_per_store_per_min / 60
kds_events/s ≈ orders/s × ~10
gps/s ≈ active_deliveries × (1/ping_interval)
storage/day ≈ orders/day × 3KB
```

### 8.15 Menu versioning note

Stamp `menu_version` + price snapshot on order lines so later menu edits don’t rewrite history. Support disputes with immutable line payload.

### 8.16 Leadership principle mapping (Amazon interview seasoning)

| Principle | Design move |
|-----------|-------------|
| Customer Obsession | Honest ETAs, proactive remediation |
| Ownership | Clear SLO pagers per plane |
| Dive Deep | Order timeline + inventory ledger |
| Frugality | Monolith→services when measured |
| Bias for Action | Kill switches over perfect prediction |

---

*End of pizza-shop system design — Amazon SDE III prep artifact.*
