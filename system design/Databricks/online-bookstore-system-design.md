# System Design: Online Bookstore

> **Focus areas:** Catalog · Search · Cart · Checkout · Inventory · Orders · Payments · Reviews
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit latency budgets, honest partial-failure semantics, clear buy-path consistency  
> **Interview theme:** Databricks — classic HLD; commerce flows with inventory consistency

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

Goal: **bound an online bookstore**—browse/search owned catalog, cart, checkout against warehouse inventory, payment saga, and order tracking without overselling or double-charging.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the product? | Intermediary: customer names a book + max bid; we query many partner bookstores | Fan-out aggregation is the core, not a catalog we own |
| F2 | How many sellers? | **50–200** partner APIs at baseline; grow to thousands | Connection pools, per-seller adapters, circuit breakers |
| F3 | Lookup key? | ISBN / title+author; assume **ISBN** for MVP | Normalize keys; fuzzy search Phase 2 |
| F4 | Quote semantics? | Return lowest available price among responders within deadline | Define **deadline** and **partial result** policy explicitly |
| F5 | Bid logic? | If `min_price ≤ bid` → place order with that seller; elif inventory exists → return min price; else unavailable | Three terminal outcomes; need atomic buy path |
| F6 | Inventory truth? | Sellers are source of truth; our cache may be stale | Re-validate price/inventory at checkout |
| F7 | Payment? | We charge customer; we pay seller (or seller bills us) | Saga / outbox; never assume 2PC across partners |
| F8 | Idempotency? | Customer retries must not double-order | `(customer_id, idempotency_key)` on quote+order |
| F9 | Auth / sellers? | API keys, rate limits, SLAs differ per seller | Seller registry with budgets and timeouts |
| F10 | Notifications? | Sync API for quote; async for order status OK | Status store + webhook/email optional |
| F11 | Admin? | Onboard seller, disable circuit-open sellers, refunds | Control plane separate from data path |
| F12 | Currency? | USD MVP; multi-currency later | Store money as integer cents + currency |

**MVP functional scope (lock with interviewer):**

1. `POST /quotes` — catalog read + inventory reserve for ISBN, aggregate within overall deadline.
2. Cart CRUD; checkout reserves inventory with TTL then payment auth/capture saga.
3. Search via OpenSearch index (async); PDP validates stock from DB at checkout.
4. Circuit breaker + retry (bounded) for transient seller errors.
5. Cache hot ISBNs with TTL; request coalescing under thundering herd.
6. Order path: re-check winning seller, charge customer, place seller order with idempotency keys.
7. Crash-safe saga with durable state machine; compensate on partial failure.

**Out of MVP (explicitly defer):**

- Full search/ranking UI, recommendations, reviews
- Perfect real-time inventory across all sellers
- Cross-region active-active order mutation for same `order_id`
- Multi-hop marketplace (sellers of sellers)
- Exactly-once money movement without partner idempotency

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Quote latency? | Interactive | p50 < 300ms, p99 < 1.5s end-to-end (incl. fan-out) |
| N2 | Fan-out deadline? | Bound tail | Overall **800ms–1.2s** budget; per-seller 200–400ms |
| N3 | Availability? | Quote path degrade gracefully | Serve partial/stale with freshness label; never hang |
| N4 | Correctness (buy)? | No double charge / double order | Idempotent saga; fencing of order attempts |
| N5 | Seller fairness? | Respect rate limits | Token buckets per seller; adaptive concurrency |
| N6 | Freshness? | Quote may be slightly stale | TTL cache; hard revalidate before charge |
| N7 | Throughput? | See scale table | Split quote QPS vs order QPS |
| N8 | Durability? | Accepted orders durable | Order state persisted before ACK |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. All sellers respond fast → pick min in-stock price → if ≤ bid → order succeeds → return `ORDER_PLACED`.
2. Prices all > bid → return `PRICE_ABOVE_BID` with min observed.
3. No seller has stock (or all timeout with zero successes) → `UNAVAILABLE`.
4. Cache hit for ISBN within TTL → fan-out reduced or skipped for cold path; still revalidate on buy.
5. Customer retries same idempotency key → same quote/order result.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Seller slow | Per-seller timeout; exclude from aggregation |
| Seller 5xx / network error | Retry once with jitter if budget remains; else skip |
| Seller circuit open | Skip immediately; schedule half-open probe |
| 0 of N respond | `UNAVAILABLE` or `DEGRADED` with reason; do not invent prices |
| Stale cache below bid, live price above | Revalidate fails → return updated price, no charge |
| Crash after charge, before seller order | Resume saga: place seller order or refund |
| Crash after seller order, before ACK | Idempotent seller call; return existing `order_id` |
| Two sellers same price | Deterministic tie-break (seller priority, latency, SLA score) |
| Hot ISBN thundering herd | Coalesce in-flight fan-outs; single upstream wave |
| Seller returns $0.01 anomaly | Sanity bounds vs historical; quarantine |
| Partial order cancel | Compensating refund + seller cancel API if available |
| Bid race (price moves mid-fanout) | Buy path always re-quotes winning seller |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Sellers (partners) | 100 | 200 | 1K | 5K |
| Quote QPS (peak) | 500 | 5K | 50K | 500K |
| Order QPS (peak) | 50 | 500 | 5K | 50K |
| Avg sellers contacted / quote | 80 | 100 | 150 | 200 (sampled) |
| Downstream calls / s | 40K | 500K | 7.5M | 100M (must reduce) |
| Unique ISBNs / day | 2M | 10M | 50M | 200M |
| Hot ISBN fraction | 1% of traffic → 100 titles | same skew | heavier skew | extreme skew |
| Cache hit ratio (target) | 70% | 80% | 85% | 90%+ with coalescing |
| Regions | 1 | 1–2 | 3 | 5+ active-active quotes |

**What each jump forces:**

- **10×:** Connection pools + async fan-out workers; Redis cache; per-seller rate limiters; coalescing.
- **100×:** Seller call reduction via cache+sampling; sharded quote services; Kafka for order saga; regional caches.
- **1,000×:** Do **not** fan out to all sellers every request—tiered sellers, predictive routing, pre-aggregation feeds; cell architecture.

### 1.5 Etc. (Constraints & Assumptions)

- We **do not** hold inventory; sellers do.
- Partner APIs are **HTTP**, heterogeneous, sometimes flaky.
- Money amounts in **integer cents**.
- Clocks: use server monotonic for deadlines; wall clock for TTLs persisted.
- Single primary cloud MVP; multi-region for quote reads later with **home cell for orders**.

**Scope statement:**

> Design a book-price aggregator that fans out to 50–200 warehouse inventory under a hard latency budget, aggregates partial results, caches/coalesces aggressively, and places orders via a crash-safe charge→order saga with idempotency—evolving from ~500 quote QPS through 10× / 100× / 1,000× by reducing fan-out amplification.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Downstream amplification (the real cost)

```text
Baseline peak quote QPS = 500
Sellers contacted / quote = 80
Raw downstream = 500 × 80 = 40,000 calls/s

If p50 seller latency = 80ms, concurrent in-flight ≈ 40,000 × 0.08 = 3,200
Provision HTTP client pools and thread/event-loop capacity for ~2× peak.
```

At **100×** without mitigation:

```text
50K × 150 = 7.5M calls/s  → impossible / ruinously expensive
Must cut via cache hits, coalescing, seller tiering, async feeds
```

**Critical insight:** The design problem is **amplification control**, not “draw an API gateway.”

### 2.2 With cache + coalescing

```text
Assume 80% cache hit (serve from Redis without fan-out)
Assume 50% of misses coalesce into shared in-flight requests
Effective fan-out rate ≈ 50K × 0.20 × 0.50 = 5K quote-waves/s at 100×
× 150 sellers = 750K calls/s  → still high; add tiering:

Tier A (top 20 sellers by fill rate): always
Tier B: sample 30
Tier C: only if A+B insufficient
Avg contacted → ~40 → 200K calls/s — manageable with regional pools + HTTP/2
```

### 2.3 Bandwidth & payload

```text
Seller response ~500 B JSON
200K calls/s × 500 B ≈ 100 MB/s ingress aggregated (100× tiered)
Quote API response ~1 KB; 50K QPS × 1 KB ≈ 50 MB/s egress
```

### 2.4 Storage

```text
Order row ~1 KB; 5K orders/s × 86400 ≈ 432M orders/day at 100×
× 1 KB ≈ 432 GB/day raw; retain hot 90 days → tens of TB + archive

Price cache: hot keys in Redis
1M hot ISBNs × 20 sellers × 128 B ≈ 2.5 GB — fine
```

### 2.5 Money path QPS

```text
Orders ≪ quotes (funnel). Baseline 50 order QPS; durability & saga matter more than raw QPS.
Payment provider limits may cap order QPS before our CPU does.
```

### 2.6 Bottlenecks (ranked)

1. Downstream call amplification / seller rate limits  
2. Tail latency from slow sellers (without deadlines)  
3. Hot ISBN stampedes  
4. Order saga crash consistency  
5. Connection pool exhaustion  
6. Cache stampede on expiry  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
SellerRegistry     → endpoints, timeouts, rate limits, weights, circuit state
CheckoutRequest       → isbn, bid_cents, customer_id, idempotency_key, deadline
SellerOffer        → seller_id, price_cents, in_stock, retrieved_at, freshness
OrderResult        → UNAVAILABLE | ABOVE_BID | ORDER_PLACED
OrderSaga          → state machine: VALIDATING → CHARGING → ORDERING → DONE | COMPENSATING
PriceCache         → isbn → offers[] with TTL
InFlightCoalescer  → isbn → Future<QuoteAggregation>
```

### 3.2 Options: sync fan-out vs pre-aggregation

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Sync fan-out per quote | Fresh; simple MVP | Amplification; tail latency | 100×+ without cache |
| B. Async crawl / feed into DB | Cheap reads | Stale; feed lag | Bid requires near-live buy |
| C. Hybrid: cache+feeds + on-demand fan-out for miss/buy | Balanced | More moving parts | Team cannot operate hybrid |
| D. Customer waits for all sellers | Complete | Violates latency SLO | p99 deadline exists |

**Chosen path:**

- **MVP:** Async fan-out with overall deadline + Redis TTL cache + coalescing; buy path revalidates winner.  
- **100×+:** Hybrid — seller feeds for Tier A/B inventory snapshots; on-demand fan-out for misses and checkout revalidation; saga service for orders.

### 3.3 Latency budget (say aloud)

```text
Total budget: 1000ms
  Auth/validate:     20ms
  Cache lookup:      5ms
  Fan-out wait:      800ms  (wall clock; parallel)
  Aggregate/rank:    10ms
  (Optional) buy path separate API or same request + extra 1–2s budget
```

**Never** set per-seller timeout = total budget; use `per_seller = min(seller_sla, remaining_budget)`.

### 3.4 Aggregation policy

```text
offers = successful responses with in_stock=true AND price in [min_sane, max_sane]
if offers empty:
  if any response said out_of_stock and no errors-only: UNAVAILABLE
  else: UNAVAILABLE_OR_DEGRADED (include error_ratio)
min_offer = min(offers) with deterministic tie-break
if min_offer.price <= bid: proceed to buy path (or return quote-only if two-phase API)
else: PRICE_ABOVE_BID(min_offer)
```

**Partial results:** Document `responded=73/100`, `freshness=max(retrieved_at)`.

### 3.5 Circuit breaker & rate limits

| Mechanism | Purpose |
|-----------|---------|
| Token bucket per seller | Honor partner QPS |
| Bulkhead (separate pools) | One bad seller cannot exhaust all threads |
| Circuit breaker | Fail-fast when error rate/latency trips |
| Adaptive concurrency (AIMD) | Limit in-flight per seller by RTT/errors |

**Deal-breaker:** Shared unbounded thread pool for all sellers.

### 3.6 Cache & coalescing

```text
Key: isbn (and optionally region/currency)
Value: list of recent offers + cached_at
TTL: 30–120s for quotes; shorter for volatile sellers
Negative cache: short TTL for UNAVAILABLE to protect sellers

Coalesce:
  if inflight[isbn] exists: await same Future
  else: create Future, fan-out, complete all waiters
Singleflight must release on failure so retries can proceed.
```

**Stampede on TTL expiry:** probabilistic early refresh or soft-TTL + hard-TTL.

### 3.7 Buy path consistency (order + payment)

Partners will not do distributed transactions with us. Use a **saga**:

```text
States:
  CREATED
  REVALIDATED
  CUSTOMER_CHARGED
  SELLER_ORDERED
  COMPLETED
  COMPENSATING
  COMPENSATED
  FAILED
```

**Preferred order (defend it):**

1. Revalidate winning seller (price ≤ bid, in stock).  
2. **Charge customer** with idempotency key `order_id` (or auth hold).  
3. Place seller order with seller idempotency key `order_id`.  
4. Mark `COMPLETED`.  

**If crash after charge, before seller order:** resume → place seller order; if seller fails permanently → **refund**.  
**If charge fails:** stop; no seller order.  
**Alternative (inventory-scarce books):** seller reserve first, then charge, then confirm—more complex; mention as Phase 2.

**Deal-breaker:** Charge and order as fire-and-forget without durable state.

### 3.8 API shape (MVP)

```text
POST /v1/quotes
  {isbn, bid_cents, currency, idempotency_key}
  → {status, min_price_cents?, order_id?, freshness, stats}

GET /v1/orders/{order_id}
  → {state, amounts, seller_id, timestamps}

POST /v1/orders/{order_id}/cancel  (best effort)
```

Two-phase optional: `POST /quotes` then `POST /orders` with `quote_id` for clearer UX.

### 3.9 Multi-region

| Plane | Mode |
|-------|------|
| Quote/fan-out | Active-active regional; local caches |
| Order saga writes | **Home cell** per `customer_id` or `order_id` |
| Payment | Region pinned by provider constraints |
| Seller calls | Often global endpoints; egress from nearest region |

### 3.11 Owned inventory (not marketplace fan-out)

```text
ProductCatalog  → SKU metadata, list price (Postgres + CDN)
InventoryService → warehouse_id + sku → available_count (SoT for stock)
CartService     → user_id → line items (Redis + DB for auth users)
CheckoutSaga    → RESERVING → PAYING → PAID → FULFILLING → SHIPPED
SearchIndex     → denormalized docs (OpenSearch, eventual)
```

**Reserve at checkout start:**

```text
UPDATE inventory SET available = available - qty, version = version + 1
WHERE sku = ? AND available >= qty AND version = ?
```

TTL 15m on reservation; sweeper releases abandoned carts.

### 3.12 API surface

```text
GET  /v1/products/{sku}
GET  /v1/search?q=&page=
POST /v1/cart/items
POST /v1/checkout  { idempotency_key }
GET  /v1/orders/{id}
POST /v1/orders/{id}/cancel  (before ship)
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Freshness vs cost | TTL cache + revalidate on buy | Quotes cheap; money correct | Serving buy from stale cache |
| Completeness vs latency | Deadline + partial | Hit p99 | Wait for all sellers |
| Durability of quote | Optional | Quotes recomputable | Blocking quote on durable write |
| Durability of order | Required before ACK | Money | ACK then async persist |
| Fan-out all sellers | Only baseline | Simple | 1000× without sampling |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                 +------------------+
  Clients -----> | API Gateway      |
                 +--------+---------+
                          |
            +-------------+-------------+
            |                           |
            v                           v
   +----------------+          +------------------+
   | Quote Service  |          | Order Saga Svc   |
   | (stateless)    |          | (home-celled)    |
   +--------+-------+          +--------+---------+
            |                           |
     +------+------+                    |
     |             |                    v
     v             v             +--------------+
 +--------+   +----------+       | Orders DB    |
 | Redis  |   | Coalescer|       | + Outbox     |
 | Price  |   | (single  |       +------+-------+
 | Cache  |   |  flight) |              |
 +--------+   +----+-----+              v
                   |             +--------------+
                   v             | Payment +    |
         +----------------+      | Seller APIs  |
         | Fan-out Worker |      +--------------+
         | Pool / async   |
         +--------+-------+
                  |
      +-----------+-----------+
      v           v           v
   Seller A    Seller B    Seller N
   (bulkheads, breakers, rate limits)

         Seller Feed Ingestors (100×+)
                  |
                  v
           Snapshot Store / Cache warmers
```

### 4.2 Sequence: quote with deadline

```text
Client          QuoteSvc          Cache        Coalescer       Sellers
  |--Quote------>|                 |              |              |
  |              |--get isbn------>|              |              |
  |              |<-miss-----------|              |              |
  |              |--singleflight----------------->|              |
  |              |                 |              |--parallel--->|
  |              |                 |              |<-partial-----|
  |              |                 |              | (deadline)   |
  |              |<-offers---------|--------------|              |
  |              |--set cache----->|              |              |
  |<-result------|                 |              |              |
```

### 4.3 Sequence: buy saga resume after crash

```text
Saga Worker         Orders DB        Payment         Seller
  |--load CHARGED-->|                 |               |
  |                 |                 |               |
  |--PlaceOrder(idem=order_id)----------------------->|
  |<-OK-----------------------------------------------|
  |--COMPLETE------>|                 |               |
```

If seller fails permanently:

```text
  |--Refund(idem=order_id-refund)---->|               |
  |--COMPENSATED--->|                 |               |
```

### 4.4 Coalescing under stampede

```text
1000 clients ask ISBN=X at once
  → 1 in-flight fan-out Future
  → 999 await
  → 1 wave to sellers
  → broadcast result (+ populate cache)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Deadline monotonicity:** fan-out never exceeds client/server budget.  
2. **No phantom offers:** only offers from successful, schema-valid responses.  
3. **Idempotent order:** `(customer_id, idempotency_key)` → at most one charged order.  
4. **Saga durability:** state transitions persisted before side effects that are hard to reverse; or use outbox carefully.  
5. **ACK ⇒ durable order intent** at least in `CREATED` with intent logged.  
6. **Revalidate before money:** never charge solely on cached quote.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Seller partition | Timeout + skip; circuit open |
| Redis down | Bypass cache; degrade QPS with admission control |
| Quote svc crash mid-fanout | Client retry; coalescer state local → retry OK |
| Saga worker crash | Another worker resumes from DB state |
| Payment ambiguity (unknown) | Query payment by idempotency key; never double-charge |
| Seller order ambiguity | Query/list by idem key; reconcile job |
| Poison ISBN (always times out) | Negative cache; isolate |

**Payment uncertainty protocol (must say):**

```text
if charge response unknown:
  do NOT retry with new idempotency key
  retrieve_charge(idempotency_key)
  if success → continue saga
  if failed → mark FAILED
  if still unknown → retry retrieve with backoff; alert
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Quote svc + async HTTP fan-out + Redis + Postgres orders |
| 10× | Shard quote pods; per-seller limiters; coalescing; pool tuning |
| 100× | Seller feeds + tiered fan-out; saga service; Kafka outbox; regional cache |
| 1000× | Cells; pre-aggregated price index; ML/heuristic seller routing; stream ingestion |

**Seller tiering algorithm (sketch):**

```text
score(seller, isbn) = fill_rate * w1 + latency_score * w2 + price_competitiveness * w3
Always query top K by score + exploration sample ε
```

**Admission control:** if in-flight fan-outs > threshold, serve cache-only or `503` with Retry-After for low-priority traffic.

### 5.3 Maintainability

- Seller **adapter interface**: `search(isbn)->Offer`; per-seller openapi/fixtures.  
- Contract tests for schema drift.  
- Canary new adapter at 1% traffic.  
- Chaos: inject seller latency, kill saga workers, partition Redis.  
- Metrics: per-seller success rate, p99, circuit state, coalesce ratio, cache hit, saga lag, refund rate.

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Quote API:
  validate → cache get → (miss) fan-out N sellers with Promise.allSettled + timeout
  → aggregate → cache set → if buy: start saga synchronously or async with 202
Orders DB: Postgres state machine
Payment + Seller: HTTP with idempotency keys
```

**10×**

- Event-loop fan-out (not 1 thread per seller per request).  
- Redis cluster for cache.  
- Bulkheads sized by seller SLA class.  
- Soft TTL refresh.

**100×**

- Kafka topic `order.saga.commands` + workers.  
- Feed ingest for top sellers every 1–5 min.  
- Quote cells by geographic region.  
- Sampled fan-out + exploration.

**1000×**

- Price index service (inverted by ISBN) updated continuously.  
- Fan-out becomes exception path.  
- Global seller capacity planner.  
- Home-cell orders; quote any region.

### 5.5 Ranking & sanity checks

```text
sane(price):
  if price <= 0: reject
  if price > 10 * historical_p95: quarantine for human/ML review
  currency mismatch: reject
```

Tie-break: lower price → higher seller trust score → lower p99 latency → `seller_id` lex.

### 5.6 Exact API semantics for three outcomes

| Outcome | HTTP | Body highlights |
|---------|------|-----------------|
| Order placed | 200 | `status=ORDER_PLACED`, `order_id`, `charged_cents` |
| Above bid | 200 | `status=PRICE_ABOVE_BID`, `min_price_cents`, `freshness` |
| Unavailable | 200 | `status=UNAVAILABLE`, `responded/total` |
| Client error | 400 | bad ISBN/bid |
| System overload | 503 | Retry-After |

Using 200 for business outcomes avoids conflating “no stock” with transport failure.

### 5.7 Data model (sketch)

```text
sellers(seller_id, base_url, timeout_ms, qps_limit, weight, status)
offers_cache: Redis HASH isbn → JSON offers
orders(order_id, customer_id, isbn, bid_cents, seller_id, price_cents,
       state, idempotency_key, payment_ref, seller_ref, version, updated_at)
order_events(order_id, ts, from_state, to_state, detail)  -- audit
idempotency(customer_id, key, order_id, response_hash)
```

### 5.8 Client cancellation

If client disconnects mid-quote: cancel fan-out futures where possible; do **not** start buy path. Coalesced waiters may still need the result—reference-count waiters before canceling the upstream wave.

### 5.8 Checkout saga (reserve → pay → fulfill)

```text
States: CART_VALIDATED → INVENTORY_RESERVED → PAYMENT_AUTHORIZED → PAYMENT_CAPTURED → FULFILLING → SHIPPED

Reserve (per SKU, conditional):
  UPDATE inventory SET available = available - qty, version = version + 1
  WHERE sku = ? AND warehouse = ? AND available >= qty AND version = ?

Payment uncertainty:
  if capture response unknown → inquiry by (order_id) idempotency key
  never double-capture with new key

Release path:
  reservation TTL 15m; sweeper returns stock; order → EXPIRED
```

**Deal-breaker:** decrement inventory only in cache; oversell under race.

### 5.9 Flash-sale hot SKU

| Technique | Purpose |
|-----------|---------|
| Per-SKU queue at checkout | Serialize reserves on one row |
| Split inventory across virtual pools | Reduce single-row contention |
| Early "join waitlist" | Shed load before payment path |
| CDN for static PDP | Keep reads off OLTP |

### 5.10 Search vs catalog consistency

CDC from `products`/`inventory` → OpenSearch. PDP reads **Postgres SoT** for price/stock badge; search may lag minutes. Checkout always revalidates inventory from SoT — never trust search index for purchase decision.

### 5.11 Multi-region (Phase 2)

| Plane | Mode |
|-------|------|
| Catalog/browse | Active-active + CDN |
| Cart | Home region per user_id |
| Orders/inventory writes | **Home cell** per customer or warehouse region |
| Payment | PSP region constraints |

### 5.12 Failure modes table

| Failure | Mitigation | User-visible |
|---------|------------|--------------|
| Reserve fails (OOS) | Abort checkout | OUT_OF_STOCK |
| Pay timeout | PENDING_PAYMENT + inquiry job | "Processing" |
| Crash after reserve | Resume pay or release | Retry safe |
| Search down | Browse via DB SKU lookup | Degraded search |
| Hot SKU lock timeout | Queue + retry | Wait or try later |

### 5.13 Sequence: checkout with idempotency

```text
Client          Checkout           Inventory        Payment
  |--checkout-->|                  |                |
  |             |--reserve SKU---->|                |
  |             |<-OK--------------|                |
  |             |--auth/capture------------------->|
  |             |<-OK------------------------------|
  |             |--commit reserve->|                |
  |<-order_id---|                  |                |
  | (retry)     |--idem hit------>|                |
  |<-same order-|                  |                |
```

---

## 6. Wrap-Up

**Design summary**

- Parallel fan-out with **hard deadlines**, bulkheads, and circuit breakers.  
- **Cache + singleflight** to tame amplification and hot keys.  
- Aggregate **partial results** with explicit freshness.  
- Buy path: **revalidate → charge → seller order** as a durable, idempotent saga with compensation.  
- Scale by **reducing fan-out** (feeds, tiering), not by infinitely scaling HTTP storms.

**MVP vs later**

| MVP | Later |
|-----|-------|
| On-demand fan-out + Redis | Seller feeds + price index |
| Sync saga in API or simple worker | Kafka saga + cells |
| All sellers every miss | Tiered/sampled sellers |
| USD / ISBN | Multi-currency, search |

**Top risks**

1. Amplification melting warehouse inventory  
2. Tail latency without deadlines  
3. Double charge under payment uncertainty  
4. Serving buys from stale cache  

**What I'd measure first in production**

- Per-seller error/latency, cache hit, coalesce ratio, effective calls per quote, saga time-in-state, refund rate.

---

## 7. Deeper / Related Interview Questions

1. How do you pick per-seller timeout vs overall deadline dynamically?  
2. Soft TTL vs hard TTL for price cache—tradeoffs?  
3. Would you use gRPC/HTTP/2 multiplexing to sellers?  
4. How does request coalescing interact with different bids on same ISBN?  
5. Auth-hold (authorize) vs capture payment—when?  
6. How to detect seller price scraping bans / CAPTCHA?  
7. Design seller feed ingestion with schema evolution.  
8. How to A/B test aggregation policies without harming conversion?  
9. Exactly-once seller order when seller has no idempotency API?  
10. Multi-item cart across sellers—distributed saga?  
11. How to rank “best” offer beyond lowest price (shipping, trust)?  
12. Legal/compliance: storing prices, audits, tax.  
13. Hot-key protection beyond coalescing (replica cache, request hedging).  
14. Hedged requests: duplicate call to same seller—good idea?  
15. Compare this to airfare aggregators (Priceline-style).  

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| “Just call all APIs with threads” | Budgets, pools, bulkheads, event loop |
| “Cache prices forever” | TTL + revalidate on buy |
| “2PC across sellers” | Saga + idempotency |
| “Exactly-once fan-out” | At-least-once with coalescing keys |
| Jump to Kafka for quotes | Quotes are sync latency path; Kafka for saga/feeds |

---


### 7.1 Bookstore commerce

**Q: Flash sale hot SKU?**  
A: Per-SKU checkout queue or split pools; never unbounded concurrent reserve on one row.

**Q: Guest cart merge on login?**  
A: Union line items; revalidate inventory; dedupe SKU qty with max policy.

**Q: Search shows in-stock but checkout fails?**  
A: Search lags; PDP/checkout reads SoT; acceptable if checkout is authoritative.

**Q: Multi-warehouse inventory?**  
A: Route reserve to nearest warehouse with stock; split shipment Phase 2.

## 8. Appendices

### A. Pseudocode — fan-out with deadline

```text
function quote(isbn, bid, deadline):
  cached = cache.get(isbn)
  if cached and not cached.expired:
    return decide(cached.offers, bid)

  return coalescer.do(isbn, () => fanout(isbn, deadline))

function fanout(isbn, deadline):
  sellers = registry.healthy()
  tasks = []
  for s in sellers:
    tasks.add(async:
      with bulkhead(s), limiter(s):
        return await s.search(isbn).timeout(min(s.timeout, remaining(deadline)))
    )
  results = await allSettled(tasks, until=deadline)
  offers = [sanitize(r) for r in results if r.ok and r.in_stock]
  cache.set(isbn, offers, ttl=ttl_for(isbn))
  return offers

function decide(offers, bid):
  if not offers: return UNAVAILABLE
  best = min(offers, key=tiebreak)
  if best.price <= bid: return maybe_order(best, bid)
  return ABOVE_BID(best.price)
```

### B. Pseudocode — saga step

```text
function advance(order_id):
  o = db.lock(order_id)
  match o.state:
    case CREATED:
      offer = revalidate(o.seller_id, o.isbn)
      if offer.price > o.bid or not offer.in_stock:
        o.state = FAILED; return
      o.state = REVALIDATED; db.save(o)
    case REVALIDATED:
      pay = payment.charge(o.customer_id, o.price, idem=o.order_id)
      if pay.unknown: return  # retry later
      if pay.failed: o.state = FAILED; return
      o.payment_ref = pay.ref; o.state = CUSTOMER_CHARGED; db.save(o)
    case CUSTOMER_CHARGED:
      so = seller.place_order(..., idem=o.order_id)
      if so.unknown: return
      if so.failed:
        o.state = COMPENSATING; db.save(o); return
      o.seller_ref = so.ref; o.state = COMPLETED; db.save(o)
    case COMPENSATING:
      payment.refund(idem=o.order_id+"/refund")
      o.state = COMPENSATED; db.save(o)
```

### C. Metrics checklist

```text
quote_latency_ms{quantile}
fanout_sellers_contacted
fanout_sellers_success
cache_hit_ratio
coalesce_join_ratio
seller_circuit_state
seller_qps_throttle_drops
order_state_age_seconds
payment_unknown_count
refund_total
```

### D. Capacity cheat sheet

```text
in_flight ≈ qps_effective_fanout × avg_seller_latency
connections ≥ in_flight / multiplex_factor
redis_ops ≈ quote_qps × (1 + miss_ratio)
db_ops_orders ≈ order_qps × (~5 state updates)
```

### E. Clarifying questions cheat sheet (30 seconds)

1. How many sellers? Latency budget?  
2. Quote-only or also place order?  
3. Partial results OK?  
4. Cache freshness tolerance?  
5. Payment provider + idempotency support?  
6. Expected QPS and hot-ISBN skew?

### F. Related Databricks follow-ups

- Persistent price cache with LRU + WAL (LLD pivot)  
- Thread-safe coalescing map `(isbn → Future)`  
- Sliding-window QPS metrics per seller  
- MPMC queue for fan-out tasks  

---

*End of book-price aggregator HLD prep.*
