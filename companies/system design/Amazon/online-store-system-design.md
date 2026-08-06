# System Design: Online Store (Amazon-lite Ecommerce)

> **Focus areas:** Catalog · Cart · Checkout · Multi-warehouse inventory · Payments hooks · Order management · Search · Thin recommendations · Fulfillment handoff  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split browse vs cart vs checkout vs inventory QPS, explicit money/inventory invariants, resolved ownership of reservation & order state

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

Goal: **bound an Amazon-lite commerce platform**—browseable catalog, durable cart, correct checkout under inventory contention, payment orchestration hooks, multi-warehouse allocation, searchable products, thin personalization—not a full marketplace + ads + Prime Video stack.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who sells? | **1P retailer first** (we own inventory); marketplace sellers Phase 2 | Single inventory owner MVP; seller hooks later |
| F2 | Catalog? | Products, SKUs/ASINs, variants, images, attributes, categories | Catalog service + CDN media; versioned attributes |
| F3 | Browse / detail? | Home, category, PDP with price + availability | Read-heavy; cache aggressively |
| F4 | Cart? | Authenticated + guest merge on login; multi-item; quantity | Cart service; soft availability checks |
| F5 | Checkout? | Address, shipping method, tax, payment, place order | Orchestrated checkout; strong inventory reservation |
| F6 | Inventory? | Multi-warehouse; reserve on place-order (or soft hold); prevent oversell | Reservation + commit; FC allocation |
| F7 | Payments? | PSP hooks (auth/capture); we don’t store PAN | Payment adapter + idempotency; webhook reconcile |
| F8 | Orders? | Lifecycle: placed → paid → allocated → shipped → delivered / cancelled | Order state machine + events |
| F9 | Search? | Keyword + filters (price, brand, prime-eligible stub) | Search index (ES/OpenSearch); not SQL `LIKE` |
| F10 | Recommendations? | **Thin**: “frequently bought together”, “related”, homepage rails | Offline batch + serving cache; not ML platform deep dive |
| F11 | Promotions? | Simple coupon / percentage off MVP | Pricing engine thin; stack rules deferred |
| F12 | Returns? | Phase 1.5: initiate return; restock event | Order extensions; inventory adjust |

**MVP functional scope (lock with interviewer):**

1. Catalog CRUD (internal) + customer browse/PDP.  
2. Cart add/update/remove; guest→user merge.  
3. Checkout: address, shipping estimate, tax stub, payment auth, place order.  
4. Multi-warehouse inventory: availability view + **hard reservation** at order place.  
5. Order management APIs + async fulfillment handoff events.  
6. Search indexing from catalog changes.  
7. Thin recommendations from co-purchase / similar-item offline jobs.  
8. Payment PSP integration (authorize → capture on ship or on place—pick & defend).

**Out of MVP (explicitly defer):**

- Full 3P marketplace (offers, seller scoring, A9 ads)  
- Complex promotion stacking / lightning deals platform  
- Perfect global active-active inventory writes  
- Same-day delivery optimization / last-mile routing deep dive  
- Full returns/refunds/chargebacks ops console  
- Voice commerce / Alexa ordering

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Browse latency | Snappy PDP/search | p50 < 100ms cached, p99 < 300ms in-region |
| N2 | Checkout correctness | No double charge; no silent oversell | Strong invariants on payment + reservation |
| N3 | Cart durability | Don’t lose cart on refresh | Durable store; eventual OK across devices |
| N4 | Availability | Prime Day class events | 99.9%+ browse; checkout degrade gracefully |
| N5 | Consistency | Catalog eventual OK; inventory/checkout strong where it matters | Split consistency by plane |
| N6 | Auditability | Order money & inventory explainable | Event log + order history immutable-ish |
| N7 | Efficiency | Cache hit ratio; avoid chatty checkout | Batch availability; denormalize read models |
| N8 | Operability | Own the pager | Metrics, SLOs, kill switches, feature flags |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Search → PDP → add to cart → checkout → pay auth → inventory reserved → order `PLACED` → capture/fulfillment events.  
2. Guest cart → login → merge → checkout.  
3. Multi-item order allocated across 2 warehouses → split shipments.  
4. Catalog update → search reindex → PDP cache invalidate.  
5. Cancel before ship → release reservation → void/refund payment path.  
6. Thin recs: PDP “related” from similar embeddings / co-purchase table.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click Place Order | Idempotency key → one order |
| Stock races (2 buyers, 1 unit) | Only one reservation wins; other fails with refresh |
| Payment auth succeeds, reserve fails | Void/cancel auth; no orphan order |
| Reserve succeeds, payment fails | Release reservation; order `PAYMENT_FAILED` |
| PSP webhook late / duplicate | Idempotent apply by PSP event id |
| Warehouse offline | Allocate to alternate FC; or delay promise |
| Price change mid-checkout | Reprice at place-order; show confirmation if delta |
| Cart item discontinued | Soft remove / block at checkout |
| Search lag after price change | Accept short stale; critical price from pricing SoT at checkout |
| Flash sale thundering herd | Queue / admission control; inventory cache + reservation DB |
| Partial cancel of multi-line order | Line-level state; release per SKU reservation |
| Split shipment tracking | Shipment entities under order |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active customers | 10M | 100M | 1B | 10B accounts* |
| DAU | 2M | 20M | 200M | 2B* |
| SKUs | 10M | 50M | 200M | 500M+ |
| Warehouses (FCs) | 20 | 50 | 200 | 500+ |
| Browse/PDP QPS (peak) | 50K | 500K | 5M | 50M |
| Search QPS (peak) | 20K | 200K | 2M | 20M |
| Cart ops/s | 5K | 50K | 500K | 5M |
| Checkout place-order/s | 500 | 5K | 50K | 500K |
| Inventory reserve ops/s | 1K | 10K | 100K | 1M |
| Orders / day | 1M | 10M | 100M | 1B |
| Catalog updates / day | 1M | 5M | 20M | 50M+ |

\*1,000× is Amazon-class thought experiment—cells, regionalization, and approximate indexes dominate.

**What each jump forces:**

- **10×:** CDN + multi-layer cache; cart/order services split; Kafka order events; search cluster; reservation DB sharding by SKU.  
- **100×:** Regional cells for checkout; inventory shard by SKU or FC; search federated; flash-sale isolation; CQRS read models.  
- **1,000×:** Homepage/search edge; catalog partitions; inventory hierarchical (FC → region → global promise); chaos-tested payment/inventory sagas; cell-based blast radius.

### 1.5 Etc. (Constraints & Assumptions)

- Currency in **minor units** (integer cents); never float.  
- Primary markets: multi-region possible, start **one region** then expand.  
- Tax/shipping: stubs OK if interfaces clear.  
- Capture timing: **auth at place, capture on ship** (Amazon-like) unless interviewer prefers auth+capture.  
- Recommendations “thin” = serving layer + offline features, not training infra deep dive.

**Scope statement:**

> Design an Amazon-lite online store: catalog, cart, checkout, multi-warehouse inventory reservation, PSP payment hooks, order lifecycle, search, and thin recommendations—correct under contention and scaled from ~1M orders/day through 10× / 100× / 1,000× with split consistency planes and cell-friendly ownership.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (deal-breaker if mixed)

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Browse/PDP** | Cached reads | 50K/s | 50M/s | CDN + edge cache |
| **Search** | Query + facets | 20K/s | 20M/s | Search tier |
| **Cart** | R/W small docs | 5K/s | 5M/s | Cart DB |
| **Checkout** | Place order | 500/s | 500K/s | Checkout + saga |
| **Inventory reserve** | Conditional decrement | 1K/s | 1M/s | Inventory shards |
| **Payment** | Auth/capture/webhook | ~500–2K/s | ~500K–2M/s | Payment svc |
| **Catalog publish** | Index/update | ~10/s avg | bursty | Async pipelines |
| **Recs serve** | Homepage/PDP rails | 10K/s | 10M/s | Feature cache |

**Anti-pattern:** one “site QPS” number used for checkout DB sizing.

### 2.2 Read amplification

```text
PDP pageview ≈ 1 product + 1 price + 1 availability + 1 recs rail + images (CDN)
If uncached microservice fan-out: 5–15 deps → latency & failure risk
Design: BFF or aggregated PDP read model; cache 30–120s; invalidate on critical updates
```

### 2.3 Storage

```text
Catalog: 10M SKUs × 5 KB attrs ≈ 50 GB (+ images in object storage TBs)
Carts: 2M active × 2 KB ≈ 4 GB hot
Orders: 1M/day × 3 KB ≈ 3 GB/day metadata (+ events)
Inventory rows: SKUs × FCs = 10M × 20 = 200M rows (~100 B) ≈ 20 GB
Search index: often 2–5× catalog text size → plan 100–250 GB baseline
```

### 2.4 Inventory contention math

```text
Hot SKU flash sale: 50K buyers / 10s for 1K units
Reserve QPS on that SKU shard spike → single-key hotspot
Mitigations: token buckets / lottery admission; sharded soft counters + final reserve;
  pre-create inventory leases; don’t put hot SKU on overloaded general DB
```

### 2.5 Checkout saga cost

```text
Place order path:
  validate cart + reprice
  + create order (PENDING)
  + reserve inventory (N lines)
  + payment auth
  + commit order PLACED
  + emit events
Latency budget: p99 ~2–5s excluding 3DS user time
```

### 2.6 Bandwidth / CDN

```text
Images dominate bytes; API JSON is small.
Assume 80–90%+ page bytes from CDN.
API fleet sized on request rate + CPU for search/checkout, not image GB.
```

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
+------------------------------------------------------------------+
| Amazon-lite          [Search____________] [Cart 3] [Account]     |
+-------------------+----------------------------------------------+
| Categories        |  Homepage rails (recs thin)                  |
|  Electronics      |  Deal of the day                             |
|  Home             |  +----------------------------------------+  |
|                   |  | PDP: Title, Price, In stock, Qty, Buy |  |
| Orders            |  | Ships from FC near you               |  |
|                   |  | Related items | FBT                     |  |
+-------------------+----------------------------------------------+
```

### 3.2 Domain model

```text
Product / ASIN
 ├── title, brand, category_path, attributes, media_refs
 ├── status: ACTIVE|INACTIVE
 └── version

Offer / Price (MVP: 1P offer)
 ├── asin, price_cents, currency, list_price
 └── effective_window

InventoryPosition
 ├── asin, warehouse_id
 ├── on_hand, reserved, available (= on_hand - reserved)
 └── version (optimistic)

Cart
 ├── cart_id, user_id? | guest_id
 └── lines[]: asin, qty, added_price_snapshot?

Order
 ├── order_id, user_id, status
 ├── lines[]: asin, qty, price_cents, warehouse_id?
 ├── payment_intent_id
 ├── reservations[]
 ├── shipments[]
 └── idempotency_key

Reservation
 ├── reservation_id, order_id, asin, warehouse_id, qty, expires_at, status
```

**Ownership (resolved):**

| Concern | Source of truth |
|---------|-----------------|
| Product attributes | **Catalog service** |
| Customer-facing price at buy | **Pricing** (checkout reprice) |
| Sellable quantity | **Inventory** (reservation ledger) |
| Cart contents | **Cart service** |
| Order lifecycle | **Order service** |
| Payment economic effect | **Payment service** + PSP + ledger hooks |
| Search documents | **Derived** from catalog/price/availability projections |
| Recommendations | **Derived** offline features + online cache |

**Deal-breakers:**

- Trusting cart cached “in stock” as commit.  
- Decrementing inventory without reservation identity / idempotency.  
- Dual-writing order status in three DBs without an owner.  
- Floating-point money.

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| API Gateway / BFF | Auth, aggregation, rate limits |
| Catalog | Product SoT; publish events |
| Pricing | Price reads; checkout reprice |
| Inventory | Availability, reserve/release/commit |
| Cart | Cart CRUD + merge |
| Checkout | Orchestrate place-order saga |
| Order | Order aggregate + state machine |
| Payment | PSP adapter, webhooks, idempotency |
| Search | Indexer + query API |
| Recs | Thin serve API |
| Fulfillment Adapter | Emit/receive warehouse WMS events |
| Notification | Email/push on order events |

### 3.4 Catalog

```text
Internal write → Catalog DB → outbox → Kafka topic catalog.changes
  → Search indexer
  → PDP cache invalidation
  → Recs feature refresh (async)
```

**Read path:** CDN/edge → catalog cache → DB. Version in cache keys / `ETag`.

| Approach | Pros | Cons |
|----------|------|------|
| Monolithic product table | Simple | Hot updates, wide rows |
| **Product + media refs + attrs JSON (chosen MVP)** | Flexible attrs | Careful indexing |
| Full CQRS read models early | Scale | Ops cost early |

### 3.5 Cart

```text
AddItem:
  validate ASIN active
  soft-check availability (advisory)
  upsert line qty
  TTL for guest carts (e.g. 30d)
Merge on login:
  union lines; qty policy = sum capped by max_qty
```

**Store:** DynamoDB / keyed document by `cart_id` or `user_id` — single-partition cart.

**Consistency:** cart may show stale stock; **checkout** enforces truth.

### 3.6 Multi-warehouse inventory

**Available** = `on_hand - reserved` (per ASIN×FC). Customer promise may show **sum across FCs** near customer, or regional pool.

**Reservation protocol (place order):**

```text
For each line (greedy or optimizer):
  1. Choose FC(s) by proximity + stock + capacity score
  2. Reserve(asin, fc, qty, order_id, idempotency) → CAS decrement available / increment reserved
  3. On any failure → compensating release of prior lines
  4. TTL on reservation (e.g. 15–30 min) if payment incomplete
On payment success → reservation COMMITTED (tied to order)
On ship → on_hand -= qty; reserved -= qty (or commit earlier on place)
On cancel → release reserved
```

| Allocation strategy | Pros | Cons |
|---------------------|------|------|
| Single FC per order | Simple packing | May fail more often |
| **Split across FCs (chosen)** | Higher fill rate | Multi-shipment UX |
| Regional soft pool then FC assign async | Smooth checkout | Risk of promise miss |

**Hot SKU:** isolate keys; optional inventory token pre-allocation for lightning deals.

### 3.7 Checkout saga

**Chosen choreography/orchestration:** Checkout **orchestrator** (sync entry) + durable steps / outbox.

```text
PlaceOrder(idempotency_key):
  if exists order for key → return it
  lock cart snapshot
  reprice + validate address
  create Order PENDING
  ReserveInventory
  Payment.Authorize
  mark Order PLACED (or AWAITING_PAYMENT→PLACED)
  clear cart lines
  emit OrderPlaced
compensate on failure:
  release reserves; void auth if open; Order FAILED
```

**Payment capture policy (defend one):**

> **Auth at place; capture when shipment created** (or per shipment). Aligns cash with fulfillment; requires auth hold lifetime management.

### 3.8 Order management

```text
PENDING → PLACED → ALLOCATED → PARTIALLY_SHIPPED → SHIPPED → DELIVERED
                 ↘ CANCELLED
                 ↘ PAYMENT_FAILED
```

Shipments are children; line items track `qty_shipped`. External WMS updates via events → Order applies transitions with CAS.

### 3.9 Payments hooks

```text
Checkout → PaymentService.CreateIntent(order_id, amount, idem_key)
  → PSP Authorize
Webhooks → verify signature → apply (AUTHORIZED|FAILED|CAPTURED|REFUNDED)
Capture trigger ← Fulfillment ShipmentCreated
```

Ledger/reconciliation can be thin hooks to a payments platform design; in this interview emphasize **idempotency + no double capture**.

### 3.10 Search

```text
Indexer consumes catalog.changes + price + availability digests
Document: asin, title, brand, category, price, rating_stub, in_stock_bool, vectors?
Query: BM25 + filters + simple rank (price, popularity)
```

| Choice | When |
|--------|------|
| OpenSearch/ES | Default ecommerce search |
| SQL | Only tiny catalogs — reject at Amazon scale |
| Vespa/candidate + ranker | 100×+ quality push |

**Availability in search:** eventually consistent boolean / coarse; PDP/checkout use inventory service.

### 3.11 Thin recommendations

```text
Offline (Spark/batch):
  co-purchase pairs, similar items (title/attrs), popular in category
Serve:
  key-value get related:{asin} → list of asins
  hydrate from catalog cache
Homepage:
  user segment rails (optional) from recent categories
```

**Not in MVP:** real-time bandits, full two-tower training platform—mention as Phase 2.

### 3.12 API sketch

```text
GET  /v1/products/{asin}
GET  /v1/search?q=&filters=
POST /v1/cart/items
POST /v1/checkout/orders   Idempotency-Key: ...
GET  /v1/orders/{id}
POST /v1/payments/webhooks/{psp}
GET  /v1/recs/related/{asin}
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
                    +---------------------------+
                    | CDN (images, static)      |
                    +-------------+-------------+
                                  |
+----------+     +----------------v----------------+
| Clients  |---->| Edge / API GW / BFF             |
+----------+     +----+------+------+------+-------+
                      |      |      |      |
          +-----------+  +---+  +---+  +---+-----------+
          v              v      v      v               v
     +---------+   +------+ +-----+ +--------+   +---------+
     | Catalog |   |Search| |Cart | |Checkout|   |  Recs   |
     +----+----+   +--+---+ +--+--+ +---+----+   +----+----+
          |           ^      |          |             ^
          |           |      |          v             |
          |      indexers    |    +-----+------+      |
          |           |      |    | Order Svc  |      |
          v           |      |    +-----+------+      |
     +----+----+      |      |          |             |
     | Kafka   |------+------+----------+-------------+
     | events  |             |          |
     +----+----+             |          v
          |                  |    +-----+------+
          v                  |    | Payment    |-----> PSP
     +---------+             |    +-----+------+
     |Inventory|<------------+          |
     | (FCs)   |             reserve    v
     +----+----+                   +----+-----+
          |                        | Fulfill  |
          v                        | Adapter  |
     +---------+                   +----------+
     | WMS/FC  |
     +---------+
```

### 4.2 Place-order sequence

```text
Client   Checkout   Inventory   Payment   Order   Cart
  |--PlaceOrder------>|          |         |       |
  |                   |--create PENDING----------->|
  |                   |--ReserveLines--->|         |
  |                   |<--OK-------------|         |
  |                   |--Authorize------>|         |
  |                   |<--AUTH OK--------|         |
  |                   |--CAS PLACED-------------->|
  |                   |--clear---------------------->|
  |                   |--emit OrderPlaced (Kafka)  |
  |<--order_id--------|          |         |       |
```

### 4.3 Failure compensate

```text
Checkout: Payment fails after reserve
  → ReleaseInventory(order_id)
  → Order = PAYMENT_FAILED
  → return retryable error

Checkout: Reserve fails after partial lines
  → Release partial
  → no payment call
  → fail with out-of-stock details
```

### 4.4 Multi-warehouse allocation sketch

```text
Customer zip Z
Order lines: (SKU1×2, SKU2×1)

Candidate FCs ranked by distance(Z)+load
  FC_A: SKU1=5, SKU2=0
  FC_B: SKU1=1, SKU2=4

Allocation:
  SKU1×2 → FC_A
  SKU2×1 → FC_B
→ two reservations → potentially two shipments
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Idempotent PlaceOrder** — same key, same `order_id`, no double charge.  
2. **Reservation before customer promise of purchase completion** — don’t mark PLACED without stock or payment policy satisfied.  
3. **Compensating actions** — every reserve has release; every auth has void/expiry path.  
4. **Single writer per order_id** for status transitions (CAS / conditional updates).  
5. **Inventory CAS** on `(asin, warehouse_id, version)` or atomic `available >= qty`.  
6. **Payment webhooks idempotent** by PSP event id.  
7. **Money in integer cents**; totals recomputed server-side.  
8. **Browse failure ≠ checkout corruption** — degrade recs/search before inventory correctness.  
9. **Outbox/events** for OrderPlaced at-least-once; consumers idempotent.  
10. **Reservation TTL sweeper** — prevents permanent stock lock on abandoned checkouts.

**Amazon interview signal:** say what you **page on** (reserve error rate, payment pending age, oversell count=0, checkout p99).

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Modular monolith or few services; Postgres; Redis cache; one search cluster |
| 10× | Split cart/order/inventory; Kafka; CDN; shard inventory by asin hash; read replicas catalog |
| 100× | Regional checkout cells; search clusters per region; hot-SKU isolation; CQRS PDP; cart by user shard |
| 1,000× | Cell architecture (blast radius); hierarchical inventory promise; edge browse; marketplace-ready offer service |

**Caching tiers:**

```text
L1: CDN (images, some SSR)
L2: Edge/API cache (PDP JSON)
L3: Service Redis (price, availability digest)
L4: DB
Checkout: bypass stale availability; hit Inventory SoT
```

**Prime Day / flash sale playbook:**

- Admission control on PlaceOrder.  
- Pre-warm caches; freeze nonessential writes.  
- Separate pool for deal ASINs.  
- Synthetic load tests on reservation path.  
- Kill switches: disable recs, reviews, personalized homepage.

### 5.3 Maintainability

- Explicit order & payment state machines in code + docs.  
- Contract tests on catalog → search projection.  
- Chaos: kill checkout mid-saga → sweeper reconciles.  
- Schema evolution via versioned events.  
- Feature flags for capture-on-ship vs capture-on-place.  
- Avoid unbounded `SELECT *` product joins on checkout.

### 5.4 Consistency spectrum (say this aloud)

| Data | Model | Why |
|------|-------|-----|
| Catalog title/images | Eventual | Speed |
| Search index | Eventual (seconds–minutes) | Scale |
| Recs | Eventual (hours OK) | Batch |
| Cart | Strong per cart key | UX |
| Inventory reservation | Strong / conditional | Oversell |
| Order status | Strong per order | Support/truth |
| Payment | Strong + PSP reconcile | Money |

### 5.5 Inventory deep dive — oversell prevention

**Wrong:** `read available; if >0; write available-1` without atomicity.  
**Right:** single-key atomic update:

```text
UPDATE inventory SET reserved = reserved + :q, version = version + 1
WHERE asin=:a AND warehouse_id=:w AND (on_hand - reserved) >= :q AND version=:v
```

Or Redis Lua for hot path with periodic DB reconcile (defend carefully—DB remains authority for finance-grade).

**Cross-FC transactions:** avoid distributed 2PC across all FCs. Prefer:

1. Reserve sequentially with compensation, or  
2. Per-line independent reservations under orchestrator, or  
3. Saga with timeout.

### 5.6 Guest cart merge

```text
on_login:
  guest = load(guest_id)
  user = load(user_id) or empty
  merged = merge_policy(guest, user)
  save(user); delete/expire guest
  audit merge for support
```

Conflict policy: sum qty, cap at `max_per_item`, prefer user price freshness at checkout reprice.

### 5.7 Search indexing lag

Accept PDP price from Pricing service; search may show stale price briefly. At checkout, **reprice** and confirm if changed > threshold.

### 5.8 Observability (Amazon ops bar)

| Metric / alarm | Why |
|----------------|-----|
| `checkout_success_rate` | Revenue |
| `inventory_oversell_count` | Must be ~0 |
| `reservation_latency_p99` | Contention |
| `payment_pending_age` | Stuck money |
| `order_stuck_in_state` | Fulfillment bugs |
| `search_latency_p99` + relevance offline eval | UX |
| `cache_hit_ratio` | Cost/latency |
| `saga_compensation_rate` | Fragility |

---

## 6. Wrap-Up

### 6.1 What we designed

An **Amazon-lite online store** with catalog, durable cart, checkout saga (reprice → reserve → pay → place), multi-warehouse inventory reservations, PSP payment hooks, order lifecycle + fulfillment events, search projections, and thin recommendations—scaled by splitting read/write planes and isolating flash-sale inventory hotspots.

### 6.2 Key decisions worth defending

1. **Split consistency** — eventual catalog/search; strong inventory/order/payment.  
2. **Hard reservation at place-order** with TTL + compensation.  
3. **Idempotent checkout** + single-writer order transitions.  
4. **Auth at place, capture on ship** (or stated alternative).  
5. **Multi-FC allocation with split shipments** for fill rate.  
6. **Search/recs derived** — never SoT for price/stock at buy.  
7. **PDP aggregation + cache**; checkout hits SoT.  
8. **Hot-SKU / Prime Day admission control**.  
9. **Integer money**; server reprice.  
10. **Cell-friendly ownership** for 100×–1,000×.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Oversell under Redis drift | DB authority; reconciliation |
| Saga stuck half-done | Sweepers + ops tooling |
| Auth hold expires pre-ship | Re-auth or capture policy change |
| Search relevance | Ranking iteration offline |
| Marketplace 3P | Offer service + seller inventory |
| Global active-active inventory | Avoid; home region / CRDT carefully |

### 6.4 How to present in 45 minutes

1. Requirements + consistency spectrum (6 min)  
2. Numbers with split classes (4 min)  
3. HLD boxes + ownership table (7 min)  
4. Checkout saga + inventory reservation (12 min)  
5. Search/recs thin + scale jumps (8 min)  
6. Invariants, alarms, Q&A (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Catalog & PDP

**Q: Why not read catalog directly from DB at Amazon scale?**  
A: Read amplification and latency; cache + CDN + read models. Writes go through catalog SoT + events.

**Q: How do you handle large attribute schemas?**  
A: Typed core columns + JSON attributes; search indexes selected fields; avoid SELECT * wide scans.

**Q: Image storage?**  
A: Object storage + CDN; catalog stores URLs/ids; transformations via image service.

**Q: How fast must catalog→PDP reflect a title change?**  
A: Seconds–minutes OK; use versioned cache bust. Price/stock more urgent at checkout.

### 7.2 Cart

**Q: Redis-only cart?**  
A: Risk of loss; use durable store (Dynamo/Postgres) + optional Redis cache. Guests need TTL.

**Q: Multi-device cart sync?**  
A: User cart keyed by user_id; last-write or CRDT-lite merge; checkout always resnapshots.

**Q: Why soft availability on add-to-cart?**  
A: UX hint only; hard enforce at reservation to reduce false declines early without locking stock too soon.

### 7.3 Inventory & warehouses

**Q: How do you prevent oversell?**  
A: Atomic conditional reserve; compensation; TTL sweeper; measure `oversell_count`.

**Q: Why not 2PC across warehouses?**  
A: Fragility/latency; saga + compensate is the commerce pattern.

**Q: How do you pick a warehouse?**  
A: Score distance, stock, capacity, SLA; allow split shipments; explain customer promise dates.

**Q: Safety stock?**  
A: Keep buffer in `on_hand` accounting or separate `non_sellable`; don’t sell damaged units.

**Q: Inventory sync from WMS?**  
A: WMS events adjust `on_hand`; conflict rules when reserved > on_hand → escalate / cancel lines.

**Q: Flash sale 1K units / 100K users?**  
A: Admission tokens; single hot key isolation; fair lottery; don’t melt general inventory cluster.

### 7.4 Checkout & orders

**Q: Orchestration vs choreography?**  
A: Orchestrator for place-order clarity; async choreography after PLACED for fulfillment.

**Q: Exactly-once order create?**  
A: Idempotency key unique constraint; retries return same order.

**Q: Price change during checkout?**  
A: Reprice server-side; if delta > ε, return confirmation payload.

**Q: Cancel after PLACED?**  
A: If not shipped, release reserve + void/refund; state CANCELLED.

**Q: Partial shipment?**  
A: Shipment entities; order `PARTIALLY_SHIPPED`; capture per shipment policy.

### 7.5 Payments

**Q: Capture on place vs ship?**  
A: Ship aligns cash & goods; needs longer auth holds. Place is simpler; higher refund ops. Pick & defend.

**Q: PSP timeout unknown?**  
A: Persist PENDING; inquire; **do not** blind second auth without idempotency guard.

**Q: Webhook before sync response?**  
A: Converge via state machine; both paths idempotent.

**Q: PCI?**  
A: Hosted fields / PSP tokens; never log PAN; minimize SAQ scope.

### 7.6 Search & recs

**Q: Why not SQL LIKE for search?**  
A: Ranking, facets, typo tolerance, scale—use dedicated index.

**Q: How do facets stay correct with stock?**  
A: Approximate OK; or periodic availability digests; don’t join inventory OLTP on every query at 100×.

**Q: Thin vs full recommender?**  
A: Serve co-purchase/similar from KV; mention two-tower / realtime as next stage without boiling the ocean.

**Q: Cold start SKU?**  
A: Category popular + content similar; explore traffic.

### 7.7 Scale & cells

**Q: What breaks at 10×?**  
A: Single DB for inventory/orders; uncached PDP fan-out; sync search writes.

**Q: What is a cell?**  
A: Self-contained slice (e.g. regional checkout + order + payment home) limiting blast radius.

**Q: Cross-region inventory?**  
A: Prefer regional promise; global sync eventual; avoid multi-region single-row contention.

**Q: How do you load test?**  
A: Separate browse vs checkout scenarios; hot ASIN tests; saga failure injection.

### 7.8 Failure injection (drill)

1. Inventory DB replica lag → checkout reads primary for reserve.  
2. Kafka down → outbox buffers; place-order still commits critical path sync parts.  
3. PSP down → fail closed new auths; browse OK.  
4. Search cluster red → degrade to category browse / cached queries.  
5. Cart store partition → sticky retries; don’t create duplicate orders.  
6. Reservation TTL too short → cancels in-flight pay → tune vs auth duration.  
7. WMS double-ship event → idempotent shipment apply.  
8. Poison catalog message → DLQ; indexer lag alarm.  
9. Clock skew on TTL sweeper → use DB absolute expiry timestamps.  
10. Thundering herd cache expiry → soft TTL / singleflight stampede control.

### 7.9 Amazon Leadership-flavored probes

**Q: Customer Obsession — oversell vs deny?**  
A: Deny at checkout with clear UX beats shipping apology; measure promise accuracy.

**Q: Ownership — who pages on stuck PLACED?**  
A: Order/checkout owning team; runbooks for payment vs inventory vs WMS.

**Q: Frugality — cache everything?**  
A: Cache reads; never cache away money/inventory correctness.

**Q: Dive Deep — prove no oversell?**  
A: Invariant tests + metric = 0 + reconciliation audits.

### 7.10 Comparison traps

**Q: Is this just a CRUD app?**  
A: Contention, sagas, dual SoT risks, and scale jumps dominate.

**Q: Same as payments platform design?**  
A: Overlap at PSP hooks; this interview centers catalog→cart→inventory→order.

**Q: Same as inventory-only interview?**  
A: Embed inventory in full purchase path; don’t ignore checkout idempotency.

**Q: Why not one mega Postgres?**  
A: Works at 1×; blast radius & hot keys force split before 100×.

### 7.11 Extra interviewer traps (high value)

- When is stock “real”?  
- What is durable before you return `order_id`?  
- How do you merge guest carts without duplicating lines wrongly?  
- Auth succeeded, reserve failed — what happens to money?  
- How do split shipments affect capture?  
- Why is search not the price SoT?  
- How do you shard inventory to avoid hot ASIN meltdown?  
- Reservation TTL vs payment hold lifetime mismatch?  
- How do you cancel one line of a multi-line order?  
- What kill switches exist for Prime Day?  
- How do recs fail without breaking PDP?  
- Integer cents vs float — show a rounding example.  
- How do you evolve to marketplace offers?  
- What is the deal-breaker in “decrement stock in app code with read-modify-write”?  
- How do you reconcile WMS on_hand with reserved?

### 7.12 Progressive scale Q&A

**Q: Baseline enough for monolith?**  
A: Yes if modular boundaries clear; still design events + idempotency early.

**Q: 10× first split?**  
A: Inventory + orders + search out of browse path; add Kafka.

**Q: 100×?**  
A: Regional cells; hot SKU service; PDP CQRS; payment home cell.

**Q: 1,000×?**  
A: Edge browse; hierarchical inventory; marketplace; automated capacity; cell isolation.

---

## 8. Appendices

## Appendix A — Example schemas

```sql
CREATE TABLE products (
  asin TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  brand TEXT,
  category_path TEXT[],
  attrs JSONB NOT NULL DEFAULT '{}',
  status TEXT NOT NULL,
  version BIGINT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prices (
  asin TEXT PRIMARY KEY,
  currency CHAR(3) NOT NULL,
  price_cents BIGINT NOT NULL,
  list_price_cents BIGINT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE inventory (
  asin TEXT NOT NULL,
  warehouse_id TEXT NOT NULL,
  on_hand INT NOT NULL,
  reserved INT NOT NULL,
  version BIGINT NOT NULL,
  PRIMARY KEY (asin, warehouse_id),
  CHECK (on_hand >= 0 AND reserved >= 0 AND reserved <= on_hand)
);

CREATE TABLE carts (
  cart_id UUID PRIMARY KEY,
  user_id UUID,
  guest_id TEXT,
  version BIGINT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cart_lines (
  cart_id UUID NOT NULL REFERENCES carts(cart_id),
  asin TEXT NOT NULL,
  qty INT NOT NULL CHECK (qty > 0),
  PRIMARY KEY (cart_id, asin)
);

CREATE TABLE orders (
  order_id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  status TEXT NOT NULL,
  currency CHAR(3) NOT NULL,
  total_cents BIGINT NOT NULL,
  idempotency_key TEXT NOT NULL UNIQUE,
  payment_intent_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version BIGINT NOT NULL
);

CREATE TABLE order_lines (
  order_id UUID NOT NULL,
  line_id UUID NOT NULL,
  asin TEXT NOT NULL,
  qty INT NOT NULL,
  price_cents BIGINT NOT NULL,
  warehouse_id TEXT,
  PRIMARY KEY (order_id, line_id)
);

CREATE TABLE reservations (
  reservation_id UUID PRIMARY KEY,
  order_id UUID NOT NULL,
  asin TEXT NOT NULL,
  warehouse_id TEXT NOT NULL,
  qty INT NOT NULL,
  status TEXT NOT NULL, -- OPEN|COMMITTED|RELEASED|EXPIRED
  expires_at TIMESTAMPTZ NOT NULL,
  UNIQUE (order_id, asin, warehouse_id)
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Catalog, cart, checkout saga, atomic reserve, PSP hooks, order SM, basic search, thin recs KV |
| 10× | CDN/cache, Kafka outbox, service split, inventory shard, search cluster, idempotency store |
| 100× | Regional cells, hot-SKU path, CQRS PDP, admission control, shipment-level capture |
| 1,000× | Edge browse, hierarchical promise, marketplace offers, cell blast-radius isolation |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| ASIN | Product identifier (Amazon-style) |
| FC | Fulfillment center / warehouse |
| Reservation | Soft-lock of stock for an order |
| Available | on_hand − reserved |
| Saga | Multi-step txn with compensations |
| Outbox | DB-reliable event publish pattern |
| BFF | Backend-for-frontend aggregation |
| Capture-on-ship | Charge when fulfillment starts |
| Hot SKU | Extreme contention inventory key |
| Cell | Independent deployable blast-radius unit |

## Appendix D — Estimation cheat-sheet

```text
browse_QPS >> cart_QPS >> checkout_QPS
inventory_rows ≈ skus × warehouses
orders/day × KB ≈ order_storage/day

reserve_peak ≈ checkout_peak × avg_lines × retry_factor

Do not size checkout DB from homepage QPS.
Do not use float for money.
```

## Appendix E — Place-order state machine

```text
                    +----------+
                    | PENDING  |
                    +----+-----+
                         |
            reserve+auth OK
                         v
                    +----------+     cancel/fail
                    | PLACED   |-------------------+
                    +----+-----+                   |
                         |                         v
                   allocate/WMS              +-----------+
                         v                   | CANCELLED |
                  +-----------+              +-----------+
                  | ALLOCATED |
                  +-----+-----+
                        |
              ship events (partial OK)
                        v
              PARTIALLY_SHIPPED → SHIPPED → DELIVERED
```

## Appendix F — Compensation matrix

| Failed step | Compensate |
|-------------|------------|
| Reprice/validate | No side effects |
| Order create | Mark FAILED / delete PENDING |
| Partial reserve | Release reserved lines |
| Payment auth fail | Release all reserves |
| Payment auth unknown | Inquire; hold reserves until resolve/TTL |
| Post-place emit fail | Outbox retry; order already PLACED |
| Capture fail after ship | Retry capture; ops queue; goods already moving |

## Appendix G — Availability promise sketch

```text
promise(asin, zip, qty):
  candidates = FCs delivering to zip within SLA
  total_avail = sum(available(asin, fc) for fc in candidates)
  if total_avail < qty: OUT_OF_STOCK
  else: ETA = min ship_estimate among FCs that can cover qty (greedy)
```

Customer-facing “In stock” uses promise(); checkout uses reserve().

## Appendix H — Thin recs feature tables

```text
related_items(asin) → [asin_1, asin_2, ...]   -- content/collab
fbt(asin) → [asin_a, asin_b]                  -- frequently bought together
popular_in_category(cat) → [asins...]

Serving: GET related → hydrate titles/prices from catalog cache
Fallback: popular_in_category if related empty
```

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Double PlaceOrder same key | One order, one auth |
| Two buyers, one unit | One PLACED, one OOS |
| Auth OK, reserve fail | Auth voided/cancelled; no PLACED |
| Reserve OK, auth fail | Reserves released |
| Webhook duplicate | Single apply |
| Reservation TTL | Stock returned; order not PLACED |
| Split FC allocate | Two reservations; order OK |
| Search stale price | Checkout reprice wins |
| Recs down | PDP 200 without rails |
| WMS double event | Idempotent shipment state |

## Appendix J — Prime Day runbook (interview gold)

1. Freeze risky deploys; enable deal ASIN pool.  
2. Raise admission limits gradually; watch reserve p99.  
3. Disable noncritical personalization if CPU tight.  
4. Pre-scale payment + inventory shards.  
5. Dashboard: oversell=0, checkout success, PSP error budget.  
6. Rollback flags ready for new pricing promotions.

## Appendix K — Evolution to marketplace (hook)

```text
Offer becomes SoT for price/seller/condition
Inventory may be seller-fulfilled or FBA
Order line gains seller_id; payments → split settlement later
Search ranks offers; PDP shows multi-offer
MVP 1P design keeps Offer interface thin to allow this
```

---

*End of design doc. Open with §1 consistency spectrum + MVP scope; whiteboard §3.6–3.7 inventory + checkout saga; close with invariants in §5.1 and traps in §7.11.*
