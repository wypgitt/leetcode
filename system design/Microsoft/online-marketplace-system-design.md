# System Design: Online Marketplace / Product Portal

> **Focus areas:** Multi-sided marketplace · Catalog & search · Inventory reservation · Checkout & payments · Seller tools · Trust & safety · Order lifecycle · Multi-tenant Azure cells  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split buyer/seller/order/search planes, explicit inventory reservation invariants, honest MVP vs extreme-scale paths  
> **Interview theme:** Microsoft — marketplace / product portal (Azure + commerce patterns); security, compliance, clean APIs, regional reliability

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

Goal: **bound the product**—a two-sided **online marketplace** where sellers list products, buyers browse/search/purchase, the platform mediates payments and fulfillment status, and trust/safety keeps fraud and abuse in check. Distinct from a single-merchant “online store”: many sellers, platform take rate, and stronger isolation/compliance needs (Microsoft lens: Entra ID for B2B sellers, Azure regions, auditability).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Multi-sided marketplace (buyers + sellers + platform) | Single-SKU catalog for one retailer |
| Inventory | Seller-owned stock with platform reservation | Pure dropship with zero stock truth |
| Payments | Platform-mediated (escrow / split payout) | Wallet-only crypto exchange |
| Search | Faceted product discovery | General web search engine |
| Microsoft lens | Multi-tenant SaaS cells, compliance, APIs | Academic e-commerce textbook only |
| Hard problem | Consistency of catalog ↔ inventory ↔ order under peak | Pixel-perfect UI |

**Scope statement:**

> Design a multi-tenant online marketplace supporting seller listings, buyer browse/search/cart/checkout, inventory reservation, payment capture + seller payouts, order lifecycle, reviews, and trust & safety—starting at ~10M GMV-capable scale and evolving through 10× / 100× / 1,000× with sharded catalog, search, and order cells.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who sells? | Third-party sellers + optional 1P | Seller accounts, KYC, payouts, quotas |
| F2 | Listing model? | Product + offer (seller price/stock/SLA) | Separate catalog product from seller offer |
| F3 | Inventory? | Soft reservation at checkout; confirm on pay | Reservation ledger + TTL |
| F4 | Cart? | Per-buyer cart across sellers | Cart service; split shipments OK |
| F5 | Checkout? | Atomic per order (or multi-seller parent/child) | Idempotent checkout; payment intent |
| F6 | Payments? | Card + wallet; platform holds then pays seller | PSP integration; ledger; payout schedule |
| F7 | Search? | Keyword + facets (price, brand, rating, ship) | Search index async from catalog |
| F8 | Reviews? | Verified purchase reviews | Moderation + abuse signals |
| F9 | Shipping? | Seller ships or platform 3PL hooks | Shipment tracking events |
| F10 | Returns? | Buyer-initiated RMA within window | Return state machine + refunds |
| F11 | Trust & safety? | Fraud, counterfeit, policy takedowns | Risk scoring + admin actions |
| F12 | Notifications? | Order/ship/refund email + push | Async notification bus |
| F13 | Seller tools? | Dashboard: listings, orders, analytics | Seller APIs + rate limits |
| F14 | Auth? | Buyers consumer IdP; sellers Entra/work | Separate identity planes OK |

**MVP functional scope (lock with interviewer):**

1. Sellers create **listings/offers** (title, images, price, stock, ship promise).
2. Buyers **browse/search**, view PDP, add to **cart**, **checkout** with payment.
3. **Reserve inventory** on checkout; release on timeout/cancel; decrement on capture.
4. **Order** state machine: `CREATED → PAID → FULFILLING → SHIPPED → DELIVERED → CLOSED` (+ cancel/refund paths).
5. Basic **seller payout** accrual (platform fee) — daily batch OK for MVP.
6. **Reviews** after delivery; basic report/moderation queue.
7. APIs for buyer, seller, admin; metrics + structured audit logs.

**Out of MVP (explicitly defer):**

- Real-time collaborative bidding / auctions (unless asked)
- Perfect global inventory across all warehouses with CAP-perfect ATP
- Full advertising marketplace / sponsored listings ranking
- Live video shopping
- Cross-border tax engine completeness (stub VAT/GST hooks)
- Active-active multi-region writes for the same order

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Browse/PDP latency? | Snappy | p50 < 100ms, p99 < 300ms cached paths |
| N2 | Search latency? | Interactive | p99 < 200–400ms in-region |
| N3 | Checkout durability? | No double-charge; no silent lost orders | Idempotent; durable before ACK |
| N4 | Inventory correctness? | Over-sell rare; never unbounded | Reservation + fencing; compensate on race |
| N5 | Availability? | Browse 99.9%+; checkout degrade gracefully | Read path cache; write path cell HA |
| N6 | Consistency? | Strong for payment/inventory; eventual for search | Split consistency by plane |
| N7 | Multi-tenancy? | Marketplace is one platform; sellers are tenants of seller plane | Quotas, isolation for seller APIs |
| N8 | Compliance? | PCI via PSP; PII encryption; audit | No raw PAN storage; GDPR/CCPA delete hooks |
| N9 | Multi-region? | DR + regional browse; orders home-celled | Single-writer home cell per order shard |
| N10 | Peak? | Holiday / flash sale 10–50× browse; 5–20× checkout | Soft limits + queueing at checkout |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seller creates offer → catalog indexed → appears in search → buyer purchases → paid → seller ships → delivered → review → payout.
2. Multi-seller cart → platform creates parent order + child orders per seller → independent fulfillments.
3. Checkout timeout → reservation expires → stock returned → payment intent cancelled.
4. Partial cancel before ship → refund + restock; after ship → return flow.
5. Fraud score high → hold fulfillment pending review; auto-release or cancel + refund.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click checkout | Idempotency key returns same `order_id` |
| Two buyers race last unit | One wins reservation CAS; other `409 OUT_OF_STOCK` |
| Payment succeeds, order write fails | Reconciliation job matches PSP intent → create/repair order or auto-refund |
| Payment fails after reserve | Release reservation; order `PAYMENT_FAILED` |
| Seller deletes listing mid-cart | Checkout validates offer active; fail line item |
| Search stale vs catalog | Eventual; PDP reads source-of-truth offer service |
| Flash sale stampede | Checkout admission queue; browse from cache/CDN |
| Seller oversells via API race | Reservation ledger is authority—not seller’s local counter alone |
| Chargeback | Freeze payout; dispute workflow; clawback ledger |
| GDPR delete buyer | Anonymize PII; retain financial ledger per retention law |
| Split brain order cell | Epoch fence; single writer; compensating payments |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active buyers (MAU) | 5M | 50M | 500M | 5B (global mega) |
| Active sellers | 50K | 500K | 5M | 50M |
| Active offers / SKUs | 10M | 100M | 1B | 10B |
| Browse QPS (peak) | 20K | 200K | 2M | 20M |
| Search QPS (peak) | 5K | 50K | 500K | 5M |
| Checkout starts / day | 500K | 5M | 50M | 500M |
| Peak checkout QPS | ~50 | ~500 | ~5K | ~50K |
| Orders / day | 200K | 2M | 20M | 200M |
| Catalog update QPS | 200 | 2K | 20K | 200K |
| Review writes / day | 50K | 500K | 5M | 50M |
| Image/blob storage | 200 TB | 2 PB | 20 PB | 200 PB |
| GMV / day (illustrative) | $20M | $200M | $2B | $20B |

**What each jump forces:**

- **10×:** Cache PDP/offer aggressively; search cluster; shard orders by `buyer_id` or `order_id`; reservation service separate from catalog.
- **100×:** Seller cells; search sharding by category/hash; checkout admission; CQRS read models; payout ledger service; fraud real-time path.
- **1,000×:** Regional marketplace cells; catalog partitioning; multi-PSP; hierarchical inventory (FC-level); edge browse; flash-sale dedicated pools.

### 1.5 Etc. (Constraints & Assumptions)

- **We build the marketplace platform**, not the seller’s warehouse WMS (hooks only).
- Payments via **external PSP** (Stripe/Adyen-like); we own **merchant-of-record ledger** semantics.
- Images on **object storage + CDN**; never through app servers as origin bytes at scale.
- **Single primary cloud (Azure-shaped)** multi-AZ; multi-region with **home cell** for order/payment state.
- Currency: start single currency; multi-currency as Phase 2 with FX snapshot at checkout.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split read/write classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Browse/PDP reads | 20K QPS | 20M QPS | Cache/CDN dominated |
| Search | 5K QPS | 5M QPS | Separate search tier |
| Cart mutations | 500 QPS | 500K QPS | Sticky session or cart store |
| Checkout / reserve | 50 QPS | 50K QPS | Hottest correctness path |
| Catalog writes (sellers) | 200 QPS | 200K QPS | Async index |
| Payment webhooks | 30 QPS | 30K QPS | Idempotent consumers |
| Tracking events | 100 QPS | 100K QPS | Append-only |

**Critical insight:** Browse can be **400×** checkout. Optimize and scale them independently. Never put PDP behind the same lock path as inventory reservation.

### 2.2 Order & reservation math

```text
Baseline: 200K orders/day ÷ 86400 ≈ 2.3 orders/s average
Peak ≈ 20× average for flash hours → ~50 checkout QPS (matches table)

Reservation hold time T = 15 minutes
Concurrent reservations ≈ checkout_start_rate × T
At 50/s × 900s ≈ 45,000 open reservations (baseline peak)
At 1000×: 50K/s × 900s ≈ 45M open reservations → sharded reservation store
```

### 2.3 Catalog & search storage

```text
Offer document ~2–4 KB (title, attrs, price, stock summary)
10M offers × 3 KB ≈ 30 GB (primary)
1000×: 10B × 3 KB ≈ 30 TB primary metadata

Search index amplification ~2–5× → plan 60–150 TB index at 1000×
Images: avg 5 images × 200 KB = 1 MB/offer
10M × 1 MB = 10 TB; 10B × 1 MB = 10 PB (object storage + CDN)
```

**Unit check:** 10B offers × 3 KB = 30×10^12 B = **30 TB**, not 30 PB. Correct.

### 2.4 Bandwidth

```text
PDP JSON ~5 KB cached:
20K QPS × 5 KB ≈ 100 MB/s origin (much less with CDN HIT)

Image via CDN: browser traffic dominates public internet, not origin
Checkout payloads small (~2–10 KB) but expensive in DB locks
```

### 2.5 Payment & ledger volume

```text
Ledger entries: ~5–15 per order lifecycle (auth, capture, fee, payout, tax…)
200K orders/day × 10 ≈ 2M ledger rows/day
1000×: 2B rows/day → append-only ledger partitions + cold archive
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Inventory reservation hot keys** (viral SKU / flash sale)
2. **Search index lag vs price/stock truth**
3. **Checkout + payment reconciliation** under PSP latency
4. **Seller API noisy neighbors** writing catalog storms
5. **Review/fraud write amplification**
6. **Multi-seller order fan-out** coordination

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Seller / Buyer accounts
Product (canonical) ──1:N──> Offer (seller, price, stock, SLA)
Cart (buyer) ──lines──> Offer refs
Order (parent) ──children──> Order per seller (optional model)
Reservation ──holds──> Offer stock units with TTL
PaymentIntent / LedgerEntry
Shipment / Return / Review
```

**Why Product vs Offer:** Same ISBN/UPC may be sold by many sellers at different prices/stock. Search ranks **offers** (or buy-box winner) while PDP can show offer comparison.

### 3.2 Options: order model

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Single order, multi-line any seller | Simple | Messy fulfillment ownership | Strong per-seller SLAs |
| B. Parent + child orders per seller | Clean payouts/fulfillment | More IDs | Interviewer wants extreme simplicity only |
| C. Cart checkout as atomic all-or-nothing across sellers | Easy UX | Bad when one seller OOS | Large multi-seller carts |

**Chosen path:** **Parent order + child orders per seller** at 10×+; MVP may start single-seller-only then extend.

### 3.3 Inventory reservation (resolve ownership)

**Invariant:** Sellable stock ≥ 0; reserved + available + sold accounting reconciles; at most `stock` simultaneous sold+reserved.

```text
available = on_hand - reserved - damaged
checkout: CAS reserve N units if available >= N → Reservation(ttl)
pay success: reserved → sold (decrement on_hand / commit)
timeout/cancel: reserved → available
```

**Deal-breaker:** Decrement stock only on “add to cart” without TTL (cart abandonment freezes inventory forever).

### 3.4 Consistency by plane

| Plane | Consistency | Store |
|-------|-------------|-------|
| Offer price/stock truth | Strong (per offer shard) | Reservation + offer OLTP |
| Order / payment | Strong (home cell) | Order DB + ledger |
| Search index | Eventual | Search cluster |
| Reviews aggregates | Eventual | Counter service / index |
| Browse CDN | Eventual | Cache with short TTL on price |

### 3.5 Payments & payouts

```text
Buyer pays platform (PSP PaymentIntent)
Platform ledger: liability to seller = (goods - fees - holds)
Payout batch: eligible settled orders → seller transfer
Chargeback: reverse ledger; block payout; investigation
```

**Never** treat PSP webhook as non-idempotent. Key by `payment_intent_id` + event id.

### 3.6 Search & catalog pipeline

```text
Seller write → Offer Service (OLTP) → event (OfferChanged)
  → Search Indexer → Search cluster
  → Cache invalidation (PDP keys)
  → Recommendation features (async)
```

**Buy box (optional):** rules engine picks winning offer (price, score, stock, Prime-like SLA).

### 3.7 Trust & safety

```text
Signals: velocity, device graph, payment risk, listing text/image match, return rate
Online: risk score at checkout / listing publish
Offline: model training; manual review queues; policy takedowns
```

### 3.8 Multi-region clarity

| Plane | Mode |
|-------|------|
| Browse/PDP | Active-active regional caches + CDN |
| Search | Regional indexes; async replication |
| Checkout/Order/Payment | **Single-writer home cell** by `order_id` / buyer shard |
| Seller catalog writes | Home cell per seller |
| DR | Fence old epoch; reconcile in-flight payments |

### 3.9 API surface (sketch)

```text
Buyer:  POST /cart/items, POST /checkout, GET /orders/{id}
Seller: PUT /offers/{id}, GET /seller/orders, POST /shipments
Admin:  POST /moderation/actions, POST /payouts/run
Internal: payment webhooks, indexer events
```

All mutating buyer/seller APIs: **Idempotency-Key** + authz.

### 3.10 Microsoft / Azure flavor

- **Entra ID** for seller/partner tenants; consumer IdP for buyers (or Entra External ID).
- **Azure Front Door / CDN** for static + PDP edge caching.
- **Service Bus / Event Hubs** for catalog and order events.
- **Azure SQL / Cosmos** (or Postgres-shaped) for order/offer shards; **Cognitive Search / ES** for product search.
- **Key Vault** for secrets; managed identities for service auth.
- Compliance: PCI SAQ-A via PSP; data residency regions for EU sellers/buyers.

---

## 4. Architecture Diagram

### 4.1 Baseline (MVP → 10×)

```text
                   ┌──────────── CDN / Edge ────────────┐
Buyers/Sellers → API Gateway → Auth (Entra/IdP)
                      │
        ┌─────────────┼──────────────┬─────────────┐
        ▼             ▼              ▼             ▼
   Catalog/Offer   Cart/Checkout   Search API    Seller API
        │             │              ▲             │
        │             ▼              │             │
        │      Reservation Svc       │             │
        │             │              │             │
        │             ▼              │             │
        │         Order Svc ──► Payment Adapter ─► PSP
        │             │              │
        │             ▼              ▼
        │         Ledger/Payout   Webhook Consumer
        │             │
        └──── events ─┴──► Bus ──► Indexer ──► Search Cluster
                              └──► Notify / Fraud / Analytics
        Images → Object Storage → CDN
```

### 4.2 Scale-out (100× → 1,000×)

```text
                    Regional Edge (browse)
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        Read Models / CDN         Checkout Admission
              │                         │
              ▼                         ▼
     Sharded Offer Cells        Order Home Cells (by shard)
              │                         │
              ▼                         ▼
     Reservation Shards          Ledger Partitions
              │                         │
              └──────── Event Fabric ───┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      Search Cells   Fraud Platform  Payout Workers
```

### 4.3 Checkout sequence (happy path)

```text
Client          API        Cart      Reserve     Order      Payment
  │              │          │          │          │          │
  ├─ checkout ──►│          │          │          │          │
  │              ├─ validate cart ────►│          │          │
  │              ├─ reserve lines ───────────────►│          │
  │              │          │          ├─ CAS OK ─┤          │
  │              ├─ create order (PENDING_PAYMENT) ─────────►│
  │              ├─ create PaymentIntent ───────────────────►│
  │◄─ client_secret / redirect ───────┤          │          │
  │              │          │          │          │◄─ webhook paid
  │              │          │          │◄─ commit reserve    │
  │              │          │          │   order=PAID        │
```

### 4.4 Flash-sale path

```text
Edge cache PDP (stock shown as "approximate")
   → Checkout Admission Queue (token bucket / waitroom)
   → Hot-SKU reservation partition (in-memory + WAL)
   → Order create async if needed (claim check)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Idempotency & exactly-once effects

| Operation | Key | Effect |
|-----------|-----|--------|
| Checkout | `(buyer_id, idempotency_key)` | One order |
| Payment webhook | `(provider, event_id)` | One state transition |
| Reserve | `reservation_id` | CAS stock |
| Seller create offer | `(seller_id, idempotency_key)` | One offer |

**Claim:** Platform provides **exactly-once business effect** for payments/orders via idempotent handlers; transport is at-least-once.

#### 5.1.2 Reservation reaper

```text
Reaper scans reservation partitions where expires_at < now AND state=OPEN
  → CAS to EXPIRED
  → increment available
  → mark order PAYMENT_EXPIRED if still pending
```

**Failure mode:** Reaper lag → temporary under-sell (safer than oversell). Alert on lag.

#### 5.1.3 Payment reconciliation

Nightly + continuous matcher:

```text
PSP intents (paid) − Orders (paid) = discrepancies
→ auto-repair: create missing order from cart snapshot OR refund
→ page humans above threshold $
```

**Deal-breaker:** Ignoring reconciliation because “webhooks are reliable.”

#### 5.1.4 Failure modes & degradation

| Failure | Degradation |
|---------|-------------|
| Search down | Browse categories + direct PDP by ID; disable search bar gracefully |
| Reservation shard down | Fail checkout for SKUs on shard; browse OK |
| PSP down | Queue checkout; or fail closed with clear UX |
| Indexer lag | Stale search; PDP truth holds |
| Fraud service down | Fail-open with lower limits OR fail-closed for high value—pick explicitly |

#### 5.1.5 Multi-AZ / DR

- Order/ledger sync replication in-region (RPO≈0 for committed).
- Cross-region async; failover fences cell epoch; duplicate webhook handling required.

### 5.2 Scalability

#### 5.2.1 Sharding keys

| Entity | Shard key | Notes |
|--------|-----------|-------|
| Offer / reservation | `offer_id` | Hot SKU → local replica tricks / queue |
| Order | `order_id` or `buyer_id` | Prefer order_id for write spread |
| Seller catalog | `seller_id` | Noisy seller isolation |
| Search | Hash(offer) or category | Fan-out query merge |
| Ledger | `seller_id` + time | Payout locality |

#### 5.2.2 Hot SKU strategies

1. **Admission control** (waitroom) before reserve.  
2. **Partitioned counters** (striped reservations) for mega-SKUs.  
3. **Pre-created allotments** (lottery / queue positions) for drops.  
4. **Cache stock as approximate**; never trust cache for commit.

#### 5.2.3 Read path

```text
CDN → edge cache (HTML/JSON) → regional offer read replica / materialized PDP
Cache keys: offer:{id}, pdp:{product_id}, bust on OfferChanged
TTL short for price (e.g. 10–60s) + explicit purge
```

#### 5.2.4 Search scaling

- Async indexer from events; exactly-once indexing via event offsets + version on offer.
- **Versioned documents:** ignore stale index updates (`doc.version < event.version`).
- At 1000×: tiered indexes (hot categories), vector optional Phase 2.

#### 5.2.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Modular monolith or few services; SQL; Redis cache; one search cluster |
| 10× | Reserve service; CDN; order idempotency; webhook workers |
| 100× | Shards/cells; admission; ledger service; fraud online |
| 1000× | Regional cells; hot-SKU specials; multi-PSP; archive |

### 5.3 Maintainability

#### 5.3.1 Service boundaries

| Service | Owns | Does not own |
|---------|------|--------------|
| Catalog/Offer | Listing truth | Payments |
| Reservation | Stock accounting | Search ranking |
| Order | Lifecycle | Seller KYC |
| Payment/Ledger | Money movement | Shipping labels |
| Search | Index & query | Price authority |
| T&S | Risk decisions | Checkout UX |

#### 5.3.2 Data contracts

Events: `OfferChanged`, `OrderPaid`, `ShipmentCreated`, `ReservationExpired` with schema registry + backward-compatible evolution.

#### 5.3.3 Observability

| SLO | Target (baseline) |
|-----|-------------------|
| PDP p99 | < 300ms |
| Search p99 | < 400ms |
| Checkout success (technical) | > 99% |
| Reserve conflict rate | monitored |
| Webhook processing lag | < 30s p99 |
| Index lag | < 60s p99 |

Traces: `checkout_id` / `order_id` / `payment_intent_id` correlation.

#### 5.3.4 Admin / ops

- Pause seller, takedown offer, freeze payouts, redrive indexer, manual refund with audit.

### 5.4 Security & compliance (Microsoft emphasis)

- Authn/z on every API; seller cannot mutate others’ offers (`seller_id` from token).
- Encrypt PII at rest; tokenize payment via PSP; Key Vault for secrets.
- Audit log for admin and payout operations (immutable).
- Data residency: pin buyer PII and orders to region when required.
- Abuse rate limits on seller publish and review write.

### 5.5 Buy box & ranking (interview depth)

```text
score = w1*(-price_norm) + w2*seller_rating + w3*ship_speed + w4*stock_health - w5*risk
constraints: in_stock, policy_ok, not_frozen
```

Recalculate async on offer change; PDP reads winner pointer with failover to next offers.

### 5.6 Returns & refunds

```text
DELIVERED → ReturnRequested → Approved → InTransit → Received → Refunded
Partial refunds: line-level ledger entries
Restock: optional; quality check gate
```

### 5.7 Notifications

Outbox pattern from Order service → Notify workers (email/push/SMS). At-least-once; user preferences; template versioning.

---

## 6. Wrap-Up

### 6.1 What we designed

A **two-sided marketplace** with separated **catalog/offer**, **reservation**, **order/payment ledger**, and **search** planes; strong consistency where money and stock matter; eventual consistency for discovery; progressive sharding and flash-sale admission at extreme scale; Microsoft-aligned identity, regional cells, and auditability.

### 6.2 Key invariants

1. Inventory accounting reconciles (`on_hand = available + reserved + sold_pending_ship` per chosen model).  
2. Idempotent checkout and payment effects.  
3. Search is never stock/payment authority.  
4. Order money movements are ledgered.  
5. Single-writer home cell for order mutations.

### 6.3 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| Product vs Offer | Split | Multi-seller reality |
| Search consistency | Eventual | Scale browse/search |
| Cart reserve | At checkout not add | Avoid inventory freeze |
| Multi-seller order | Parent/child | Clean fulfillment/payouts |
| Hot SKU | Admission + striped counters | Prevent DB melt |

### 6.4 60-second pitch

> We separate browse/search from reservation and checkout. Offers own commercial truth; reservations CAS stock with TTL; orders and ledgers are strongly consistent in a home cell; payments are idempotent via PSP webhooks plus reconciliation; search and CDN are eventual. At scale we shard offers/orders, add checkout admission for flash sales, and isolate noisy sellers—while Entra-auth’d seller APIs and audit trails meet enterprise compliance expectations.

### 6.5 Risks / follow-ups

- Cross-border tax & duties engine  
- Advertising / sponsored rank integrity  
- Warehouse ATP integration  
- Real-time messaging support chat  

---

## 7. Deeper / Related Interview Questions

### 7.1 Inventory

**Q: Reserve on add-to-cart?**  
A: Usually no—abandonment freezes stock. Reserve at checkout with TTL; cart is intent only.

**Q: How to avoid oversell?**  
A: Atomic reservation CAS per offer shard; compensate if payment fails; never trust cache for commit.

**Q: Hot SKU with 1M QPS interest?**  
A: Waitroom + striped counters / pre-allotment; approximate stock on PDP.

**Q: Multi-warehouse ATP?**  
A: Phase 2—reservation service talks to regional ATP; promise based on fulfillable node.

### 7.2 Orders & payments

**Q: Exactly-once payment?**  
A: Idempotent intent + webhook dedupe + reconciliation. Don’t claim transport exactly-once.

**Q: Payment paid but order insert fails?**  
A: Reconciliation repairs or refunds; outbox/inbox patterns reduce window.

**Q: Multi-seller payment split?**  
A: One buyer charge; internal ledger splits; payouts per seller child order.

**Q: Partial capture?**  
A: Line-level captures when items ship; auth hold strategies vary by PSP.

### 7.3 Search & catalog

**Q: Strongly consistent search?**  
A: Costly; keep eventual; PDP reads OLTP truth for buy decisions.

**Q: How to handle deleted offers still in search?**  
A: Version + tombstones; query filters `status=ACTIVE`; periodic reindex.

**Q: Faceted search at 1B docs?**  
A: Sharded inverted index; doc values for facets; pre-agg for popular facets.

### 7.4 Trust & safety

**Q: Fake reviews?**  
A: Verified purchase only for “verified” badge; velocity limits; ML + graph features; manual queue.

**Q: Counterfeit listings?**  
A: Brand registry, image/text matching, takedown workflow, seller strikes.

**Q: Account takeover at checkout?**  
A: Risk-based step-up auth; device signals; freeze fulfillment on suspicion.

### 7.5 Scale & cells

**Q: Why home cell for orders?**  
A: Avoid dual-writer split brain on payment state.

**Q: Can browse be global active-active?**  
A: Yes—caches/indexes. Checkout writes still pinned.

**Q: Noisy seller API?**  
A: Per-seller quotas; shuffle shard; separate write pools.

### 7.6 Consistency puzzles

**Q: Buyer sees in-stock, checkout OOS?**  
A: Expected under eventual stock display; UX messaging + alternatives.

**Q: Double reservation same buyer retries?**  
A: Idempotency key returns same reservation/order.

**Q: Clock skew on reservation TTL?**  
A: Server-side expiry only; clients don’t decide truth.

### 7.7 Marketplace economics

**Q: When is seller paid?**  
A: After delivery window / dispute window; holdbacks for new sellers.

**Q: Platform fee changes?**  
A: Fee snapshot at order time in ledger; don’t recompute historically.

### 7.8 Microsoft-specific

**Q: How would you use Azure?**  
A: Front Door/CDN, AKS services, Event Hubs, Azure SQL/Cosmos shards, Cognitive Search, Key Vault, Entra ID for sellers.

**Q: Enterprise B2B marketplace differences?**  
A: Purchase orders, negotiated pricing, tenant isolation, stronger audit—extend offer model with contract prices.

### 7.9 Comparison

**Q: vs single-merchant store?**  
A: Multi-seller isolation, buy box, split orders/payouts, heavier T&S.

**Q: vs auction system?**  
A: Fixed-price offers here; auctions need bid integrity and different consistency.

**Q: vs classifieds (no payments)?**  
A: We own checkout/ledger; classifieds often contact-only.

### 7.10 Reliability drills

**Q: Kill reservation shard mid-checkout?**  
A: Checkout fails for affected SKUs; retries after failover; no silent success.

**Q: Duplicate webhooks?**  
A: Dedupe table; second event no-ops.

**Q: Indexer poison message?**  
A: DLQ; don’t block entire pipeline; alert on lag.

### 7.11 Algorithms & data structures

**Q: Reservation store?**  
A: Row per offer with version + reserved_count; or striped counters aggregated.

**Q: Idempotency store?**  
A: Unique `(actor_id, key)` → resource id with TTL optional.

**Q: Search ranking?**  
A: BM25 + business features; buy-box separate from browse rank.

### 7.12 Interview traps

| Trap | Pushback |
|------|----------|
| Global lock on checkout | Won’t scale |
| Search as inventory truth | Oversell |
| Store PAN in DB | PCI nightmare |
| Reserve forever in cart | Dead inventory |
| 10B×3KB=30PB | **30TB** |
| Active-active order writers | Split-brain money |

### 7.13 UX vs correctness

**Q: Show exact stock count?**  
A: Often “low stock” / approximate; exact count is abuse + hot-key magnet.

**Q: Atomic multi-seller checkout?**  
A: Prefer per-seller children with partial success policy disclosed in UX.

### 7.14 Analytics

**Q: Real-time seller dashboards?**  
A: Event stream → OLAP; not OLTP count(*).

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- sellers(seller_id, tenant_status, kyc_status, payout_account_ref, ...)
-- buyers(buyer_id, ...)
-- products(product_id, title, brand, attrs_json, ...)
-- offers(
--   offer_id PK, product_id, seller_id, price_cents, currency,
--   on_hand INT, reserved INT, status, version, updated_at)

-- reservations(
--   reservation_id PK, order_id, offer_id, qty, state,
--   expires_at, version)

-- orders(
--   order_id PK, parent_order_id NULL, buyer_id, seller_id NULL,
--   state, idempotency_key, currency, totals..., home_cell,
--   UNIQUE(buyer_id, idempotency_key))

-- order_lines(order_id, offer_id, qty, price_snapshot_cents, ...)
-- payments(payment_id, order_id, provider_ref, state, ...)
-- ledger_entries(entry_id, seller_id, order_id, type, amount, created_at)
-- shipments(shipment_id, order_id, tracking, state, ...)
-- reviews(review_id, order_line_id, rating, text, status)
```

### 8.2 API checklist

- [ ] `POST /offers` / `PATCH /offers/{id}` (seller)
- [ ] `GET /products/{id}` / `GET /offers/{id}` (buyer)
- [ ] `GET /search?q=&filters=`
- [ ] `POST /cart/items`, `GET /cart`
- [ ] `POST /checkout` + Idempotency-Key
- [ ] `POST /payments/webhooks/{provider}`
- [ ] `POST /orders/{id}/shipments`
- [ ] `POST /returns`
- [ ] `POST /reviews`
- [ ] Admin moderation + payout run

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Offer | Seller-specific sellable listing |
| Buy box | Winning offer selection |
| Reservation | Time-bounded stock hold |
| Home cell | Single-writer region for order/payment |
| Ledger | Append-only money truth |
| Admission / waitroom | Rate-limit entry to checkout for hot demand |
| Parent/child order | Split fulfillment by seller |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Offer+order SQL, basic search, PSP, TTL reserve |
| 10× | CDN, webhook workers, cache, outbox events |
| 100× | Sharded reserve/order, fraud online, ledger svc |
| 1000× | Regional cells, hot-SKU pools, multi-PSP, archive |

### 8.5 State machines

**Order:**

```text
CREATED → PENDING_PAYMENT → PAID → FULFILLING → SHIPPED → DELIVERED → CLOSED
                ↓               ↓
         PAYMENT_FAILED    CANCELLED / REFUNDING → REFUNDED
```

**Reservation:** `OPEN → COMMITTED | EXPIRED | RELEASED`

### 8.6 Event list

| Event | Producer | Consumers |
|-------|----------|-----------|
| OfferChanged | Catalog | Search, cache, recommendations |
| OrderPaid | Order | Seller notify, fraud, analytics |
| ReservationExpired | Reserve | Order, notify |
| ShipmentUpdated | Fulfillment | Buyer notify, order state |
| PayoutSettled | Ledger | Seller dashboard |

### 8.7 Flash-sale runbook

1. Pre-warm caches & reservation partitions.  
2. Enable waitroom with estimated wait.  
3. Cap per-buyer purchase quantity.  
4. Disable nonessential writes (reviews) if needed.  
5. Watch reserve conflict rate, checkout p99, PSP errors.  
6. Post-sale reconciliation mandatory.

### 8.8 Fraud signal examples

- New seller + high velocity listings  
- Shipping address ≠ billing + high value  
- Many accounts one device  
- Sudden return rate spike  
- Card testing patterns (micro auths)

### 8.9 Interview “say this” summary (60 seconds)

> Marketplace with Product/Offer split, checkout-time reservations with TTL, idempotent orders/payments with ledgered payouts, eventual search, and sharded cells at scale—browse separated from stock/money truth.

### 8.10 Extra traps

| Trap | Pushback |
|------|----------|
| Monolithic stock++/-- without CAS | Lost updates |
| Fee recomputed later | Accounting drift |
| Global sequential order IDs as hotspot | Use UUIDs / snowflakes per cell |
| Synchronous index on seller write | Seller API latency melt |

### 8.11 Reliability test plan

1. Double checkout with same idempotency key → one order.  
2. Two buyers, one unit → one win, one OOS.  
3. Webhook duplicate → one transition.  
4. Kill indexer → checkout still works; search stale.  
5. Reservation reaper → stock returns after TTL.  
6. PSP paid / order missing → recon repairs or refunds.

### 8.12 Observability SLOs

| SLO | Example |
|-----|---------|
| Checkout success (excl. OOS) | > 99.5% |
| Reserve p99 | < 100ms in-region |
| Index lag p99 | < 60s |
| Payout correctness | 100% reconciling |

### 8.13 Related systems map

```text
Seller → Catalog/Offer → Events → Search/Cache
Buyer → Cart → Checkout → Reserve → Order → Payment/Ledger
                         ↓
                      Fulfillment → Returns → Reviews
                         ↓
                      Fraud / Notify / Analytics
```

### 8.14 Capacity cheat-sheet

```text
Concurrent reservations ≈ peak_checkout_start_rate × ttl_seconds
Search nodes ≈ qps × cost_per_query / budget_per_node
CDN hit ratio dominates browse cost more than app tier count
```

### 8.15 Distinct from “online store”

| Online store | Marketplace |
|--------------|-------------|
| One merchant inventory | Many sellers |
| One catalog owner | Product + Offer |
| Simple payout | Split ledger / holdbacks |
| Lighter T&S | Counterfeit, multi-seller fraud |

### 8.16 Sample reservation CAS (pseudo)

```text
UPDATE offers SET reserved = reserved + :qty, version = version + 1
WHERE offer_id = :id AND version = :v AND (on_hand - reserved) >= :qty
```

### 8.17 Payout eligibility rules (example)

- Child order DELIVERED  
- No open dispute  
- Past holdback window (e.g. 7–14 days)  
- Seller KYC cleared  
→ accumulate `ledger available_balance` → transfer batch

### 8.18 Multi-currency note

Snapshot FX rate and buyer charge currency at PaymentIntent creation; seller payout currency may differ with separate FX ledger entries—Phase 2.

### 8.19 GDPR / CCPA checklist

- [ ] Export buyer data  
- [ ] Delete/anonymize PII  
- [ ] Retain immutable financial records per law  
- [ ] Seller data residency controls  

### 8.20 Final deal-breakers list

1. Cache as inventory authority  
2. Non-idempotent payment webhooks  
3. Cart reservations without TTL  
4. Dual-writer active-active orders  
5. Storing raw card data  

---

*End of online marketplace system design.*
