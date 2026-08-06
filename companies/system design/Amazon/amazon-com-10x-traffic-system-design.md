# System Design: Amazon.com at 10× Traffic (and 100× / 1,000×)

> **Focus areas:** Web tier · Multi-layer caching · Catalog · Search · Cart/checkout path · CDN · Cell architecture · Prime Day readiness · Progressive scale (10× → 100× → 1,000×)  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, blast-radius thinking  
> **Quality bar:** Split browse vs search vs cart vs checkout QPS, explicit consistency planes, cell ownership, Prime Day runbooks, deal-breakers called out

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

Goal: **bound “scale Amazon.com to 10×”**—not rebuild every retail subsystem, but show how traffic, cache, cells, and critical paths (browse → search → PDP → cart → checkout) survive a step-function load increase and what breaks at 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is “Amazon.com”? | Retail storefront: browse, search, PDP, cart, checkout; not Video/Ads deep dive | Scope to storefront plane |
| F2 | What does 10× mean? | Peak QPS and concurrent users ~10× today’s assumed baseline | Capacity + architecture, not just “add boxes” |
| F3 | Regions? | Multi-region retail presence; start from one primary + replicas | Cells + DNS/geo routing |
| F4 | Catalog? | Hundreds of millions of ASINs; media heavy | CDN + catalog read models |
| F5 | Search? | Keyword + facets; relevance matters | Separate search tier; not SQL |
| F6 | Cart? | Auth + guest; durable across devices | Cart service; merge on login |
| F7 | Checkout? | Must stay correct under load | Strong path; admission control |
| F8 | Prime Day? | Planned peak >> normal 10×; flash deals | Load shedding, pre-warm, deal isolation |
| F9 | Personalization? | Homepage rails / recs present but degradable | Soft dependencies |
| F10 | Payments? | Existing PSP path; must not double-charge | Idempotency; don’t redesign PSP |
| F11 | Marketplace? | 1P + 3P offers exist; treat offer aggregation as dependency | Offer service as read dependency |
| F12 | Success metric? | Revenue + availability SLOs; oversell ≈ 0 | Explicit SLOs and kill switches |

**MVP functional scope (lock with interviewer):**

1. Scale **browse / PDP / search / cart / checkout** paths for 10× peak.  
2. Multi-layer **CDN + edge + service cache** with clear invalidation.  
3. **Catalog** and **search** as read-mostly scaled tiers.  
4. Protect **checkout** with admission control, idempotency, inventory reservation.  
5. Introduce **cell architecture** for blast radius at 10×→100×.  
6. **Prime Day readiness**: capacity plan, pre-warm, degrade ladder, runbook.  
7. Observability: per-path SLOs, load-shed metrics, hot-ASIN isolation.

**Out of MVP (explicitly defer):**

- Redesigning A9 ads auction / full marketplace seller tooling  
- Last-mile logistics / FC robotics  
- Building a new payment processor  
- Perfect global active-active inventory writes  
- Full Prime Video / Alexa commerce stack  
- Training new recommendation models (serving + degrade only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Browse latency | Snappy PDP | p50 < 80ms edge-hit; p99 < 250ms in-region |
| N2 | Search latency | Interactive | p50 < 100ms; p99 < 400ms |
| N3 | Checkout correctness | No double charge / silent oversell | Strong invariants; effectively-once place-order |
| N4 | Availability | Retail critical | 99.95%+ browse; checkout 99.9%+ with degrade |
| N5 | Consistency | Split by plane | Eventual catalog/search; strong cart/checkout |
| N6 | Blast radius | Cell failure ≠ global outage | Cell isolation + sticky routing |
| N7 | Efficiency | Cost at 10× | Cache hit ≥ 90% browse; avoid chatty fan-out |
| N8 | Operability | Own the pager | SLOs, kill switches, Prime Day war room |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Geo DNS → CDN → edge → storefront BFF → cached PDP → add cart → checkout → place order.  
2. Search query → search tier → result cards from catalog cache → PDP.  
3. Homepage with personalized rails; miss falls back to popular/default.  
4. Catalog update → invalidate PDP cache keys → search reindex lag seconds–minutes.  
5. Prime Day deal ASIN: isolated inventory pool + higher cache TTLs on static media.  
6. Region failover for browse; checkout sticky to home cell.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| CDN origin storm after deploy | Stagger purge; soft TTL + stale-while-revalidate |
| Search cluster hot shard | Query fan-out limits; replica promote; shed facets |
| Cart DB hotspot (celebrity deal) | Shard by customer; deal SKUs not in cart key |
| Checkout thundering herd | Token bucket / lottery admission; queue UX |
| Inventory race on 1-unit deal | Atomic reservation; loser gets “sold out” |
| Personalization down | Serve non-personalized homepage |
| One cell down | Route new sessions away; drain sticky traffic |
| Payment PSP slow | Timeouts + pending state; no blind double auth |
| Cache stampede on cold key | Singleflight / request coalescing |
| Bad deploy raises error rate | Auto rollback + feature flags |
| Cross-region cart merge lag | Eventual device sync; checkout revalidates |

### 1.4 Scales (Progressive)

| Metric | Baseline (1×) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Peak browse/PDP QPS | 100K | 1M | 10M | 100M |
| Peak search QPS | 40K | 400K | 4M | 40M |
| Peak cart ops/s | 10K | 100K | 1M | 10M |
| Peak place-order/s | 1K | 10K | 100K | 1M |
| Concurrent sessions | 5M | 50M | 500M | 5B* |
| SKUs / ASINs | 100M | 200M | 400M | 500M+ |
| Catalog updates/day | 5M | 20M | 50M | 100M+ |
| Edge POPs | 50 | 80 | 150 | 200+ |
| Retail cells | 4 | 12 | 40 | 100+ |
| Cache hit ratio (browse) | 85% | 92% | 95% | 97%+ |

\*1,000× is a thought experiment: edge-first browse, hierarchical cells, approximate indexes.

**What each jump forces:**

- **10×:** Horizontal web tier, CDN hardening, Redis fleets, search cluster growth, checkout admission, basic cells.  
- **100×:** Strict cell ownership, regional search, hot-ASIN isolation, CQRS read models, chaos-tested degrade ladder.  
- **1,000×:** Edge compute for PDP assembly, hierarchical inventory promise, global traffic director, marketplace-scale offer sharding.

### 1.5 Etc. (Constraints & Assumptions)

- Baseline numbers are **interview-assumed**, not leaked internal Amazon figures—state that aloud.  
- Money in **integer minor units**; server recomputes totals.  
- Soft deps (recs, reviews, “customers also bought”) must fail open.  
- Hard deps (auth for checkout, inventory reservation, payment) fail closed with clear UX.  
- Prefer **evolving** existing Amazon-shaped architecture over greenfield fantasy.

**Scope statement:**

> Scale an Amazon.com-class retail storefront to 10× peak traffic (and discuss 100× / 1,000×): web/BFF tier, CDN and multi-layer caches, catalog and search read paths, durable cart, protected checkout, cell architecture for blast radius, and Prime Day operational readiness—with split consistency planes and explicit degrade ladders.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (deal-breaker if mixed)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Browse/PDP** | Cached reads, media | 100K/s | 1M/s | CDN + edge |
| **Search** | Query + facets | 40K/s | 400K/s | Search tier |
| **Cart** | Small doc R/W | 10K/s | 100K/s | Cart DB |
| **Checkout** | Orchestrated writes | 1K/s | 10K/s | Order/inventory |
| **Catalog publish** | Writes / invalidations | ~100/s | ~500/s | Catalog SoT |
| **Personalization** | Soft read | 50K/s | 500K/s | Recs cache |

Never capacity-plan “1M QPS Amazon” as one number—**checkout is ~1% of browse**.

### 2.2 Bandwidth & payload

```text
PDP JSON ~ 20–40 KB compressed
HTML shell ~ 30–80 KB
Images: 200KB–2MB each → CDN, not origin

At 1M PDP QPS × 30 KB ≈ 30 GB/s edge egress (mostly CDN)
Origin should see ~5–10% after cache ⇒ 1.5–3 GB/s origin (still huge → more edge)

Search response ~ 8–15 KB × 400K/s ≈ 3–6 GB/s
Cart payload ~ 2–5 KB — DB bound, not net bound
```

### 2.3 Cache math

```text
Assume 92% CDN/edge hit on browse at 10×:
  Origin QPS ≈ 1M × 0.08 = 80K/s  (still needs app cache + coalescing)

Service Redis hit 80% of remaining:
  Catalog/DB QPS ≈ 80K × 0.20 = 16K/s  (feasible with shards + replicas)

Without cache: 1M → DB = instant meltdown. Cache is not optional.
```

### 2.4 Checkout capacity

```text
10K place-order/s peak
Each place-order:
  1 idempotency check
  1–N inventory reserves
  1 payment auth
  1 order write + outbox
  ~5–15 downstream events

Inventory reserve ops ≈ 2–3× place-order (multi-line) ⇒ ~25–30K/s
Shard inventory by ASIN hash; isolate deal ASINs.
```

### 2.5 Storage rough order

| Store | 10× order of magnitude | Notes |
|-------|------------------------|-------|
| Catalog metadata | 10s of TB | Versioned attrs |
| Media (S3/CloudFront) | EB-class globally | Immutable objects |
| Search index | 10s–100s TB | Sharded |
| Cart | TBs | TTL + active set |
| Orders | 10s TB/year growth | Partition by time + customer |
| Session/edge | ephemeral | Sticky cookies / tokens |

### 2.6 Servers (interview sketch)

```text
Web/BFF: 1M RPS cached-heavy → mostly edge; origin fleet ~5–20K cores depending on language/efficiency
Search: 400K QPS → large OpenSearch/ES fleet; fan-out limited
Cart: DynamoDB-class or sharded Redis+DB; 100K ops easy if key-partitioned
Checkout: smaller fleet but higher CPU per request; autoscale on place-order queue depth
```

**State aloud:** numbers guide architecture choices; exact headcount is ops, not the interview.

---

## 3. High-Level Design

### 3.1 Planes of the system

| Plane | Responsibility | Consistency | Scale lever |
|-------|----------------|-------------|-------------|
| **Edge / CDN** | Static + cacheable HTML/JSON/media | TTL / SWR | POPs, purge policy |
| **Browse / BFF** | Assemble page; orchestrate reads | Eventual OK | Stateless HPA |
| **Catalog** | Product SoT + read models | Strong write / eventual read | Shards + CQRS |
| **Search** | Index + query | Eventual | Cluster + regions |
| **Cart** | Per-customer durable cart | Strong per cart key | Shard by customer_id |
| **Checkout** | Place order saga | Strong | Cells + admission |
| **Inventory** | Reservation / availability | Strong per ASIN shard | Hot-key isolation |
| **Orders** | Lifecycle SoT | Strong per order | Partition + events |
| **Personalization** | Rails / ranking soft | Eventual | Cache + degrade |

### 3.2 Component ownership

```text
Client (Web/App)
    → DNS / Traffic Director (geo + cell)
    → CDN / Edge (CloudFront-class)
    → Storefront BFF / Page Service
         ├─ Catalog Read API (cached)
         ├─ Pricing / Offers (cached + checkout SoT)
         ├─ Availability digest (cached; SoT at checkout)
         ├─ Search Service
         ├─ Recommendations (soft)
         ├─ Reviews summary (soft)
         └─ Cart Service
    → Checkout Orchestrator (hard path)
         ├─ Idempotency Store
         ├─ Inventory Reservation
         ├─ Payments Adapter
         ├─ Order Service + Outbox
         └─ Tax/Shipping stubs
    → Event Bus (order events → fulfillment, analytics, email)
```

### 3.3 Request paths

**Browse / PDP (read-heavy)**

1. Edge cache key: `(asin, marketplace, locale, layout_version, experiment_bucket?)`.  
2. Miss → BFF fetches catalog projection + price digest + availability digest in parallel (bounded fan-out).  
3. Soft deps with short timeouts; omit rails on failure.  
4. Response cached with SWR; authenticity of price at buy deferred to checkout.

**Search**

1. Query normalize → cache popular queries.  
2. Search cluster returns ASIN list + facets.  
3. Hydrate cards from catalog cache (batch get).  
4. Never treat search price as checkout SoT.

**Cart**

1. Keyed by `customer_id` or `guest_id`.  
2. Add/update merges line items; soft availability hint only.  
3. On login: merge guest→user with audit.

**Checkout / place-order**

1. Admission token / rate limit per customer + global.  
2. Idempotency key required.  
3. Reprice + tax + shipping.  
4. Reserve inventory (atomic).  
5. Payment auth.  
6. Persist order + outbox; return order_id.  
7. Compensate on partial failure.

### 3.4 Caching strategy (multi-layer)

| Layer | Content | TTL | Invalidation |
|-------|---------|-----|--------------|
| L0 CDN media | Images, JS, CSS | Long / immutable hashed | Deploy new hash |
| L1 CDN/edge page | PDP shell/JSON | 30s–5m + SWR | Purge by ASIN tag |
| L2 BFF local | Hot ASIN | 1–10s | Process TTL |
| L3 Redis | Catalog/price/avail digests | 10s–5m | Pub/sub invalidate |
| L4 DB replicas | SoT reads | N/A | Replication lag |

**Rules:**

- Cache **digests**, not unbounded graphs.  
- **Singleflight** on L3 miss.  
- Checkout **bypasses** stale availability for reservation.  
- Negative cache short TTL for missing ASINs (bot protection).

### 3.5 Cell architecture

A **cell** is a self-contained slice of storefront + cart + checkout + order for a partition of customers (and sometimes marketplaces).

```text
Traffic Director
  → Cell A (customers hash 0–25%)
  → Cell B (25–50%)
  → Cell C (50–75%)
  → Cell D (75–100%)
Shared: CDN, global catalog publish, search (regional), media
```

**Why cells at 10× (and mandatory by 100×):**

- Blast radius: bad deploy / noisy neighbor limited.  
- Capacity planning per cell.  
- Sticky sessions for checkout consistency.  
- Parallel progressive delivery of releases.

**What is shared vs cell-local:**

| Shared (global/regional) | Cell-local |
|--------------------------|------------|
| Media CDN | Cart DB partition |
| Catalog publish pipeline | Checkout orchestrator |
| Search index (regional) | Order writes for cell customers |
| Identity provider | Idempotency store |
| Payment PSP | Cell metrics / alarms |

### 3.6 Catalog & search at scale

**Catalog:** write path (sellers/internal) → versioned product documents → project to:

- PDP read model (Dynamo/Cassandra/MySQL shard)  
- Search indexer  
- Offer/price service  
- Availability aggregator

**Search:** OpenSearch/ES or Amazon-internal equivalent; inverted index sharded by term; document keyed by ASIN+marketplace. Indexing lag acceptable; relevance offline-evaluated.

### 3.7 Cart / checkout path protection

```text
Browse overload  → shed recs, reviews, personalization
Search overload  → shed facets, reduce page size, cache hits
Cart overload    → scale shards; reject bots
Checkout overload→ admission control; virtual waiting room; protect inventory/payment
```

**Never** let browse autoscale policies starve checkout capacity pools—**separate compute pools**.

### 3.8 Progressive evolution

| Scale | Architecture move |
|-------|-------------------|
| 1× | Regional monolith/services; Redis; one search cluster |
| 10× | CDN+SWR; cart/order split; Kafka; 4–12 cells; checkout admission |
| 100× | Strict cell routing; regional search; hot-ASIN cells; edge PDP assembly |
| 1,000× | Hierarchical traffic director; approximate global indexes; inventory promise hierarchy |

### 3.9 API sketch (storefront)

```text
GET  /v1/product/{asin}?marketplace=...
GET  /v1/search?q=&facet=...
POST /v1/cart/items
GET  /v1/cart
POST /v1/checkout/quote
POST /v1/checkout/place   Idempotency-Key: ...
GET  /v1/orders/{order_id}
```

### 3.10 Trade-offs table

| Decision | Pros | Cons | Pick |
|----------|------|------|------|
| Edge-cache PDP JSON | Huge scale | Stale price/avail | Yes + checkout revalidate |
| Cells by customer | Blast radius | Cross-cell features harder | Yes at 10×+ |
| Shared search | Simpler relevance | Noisy neighbor | Regional shared OK |
| Separate checkout pool | Protects revenue | Cost | Yes |
| Soft-fail recs | Availability | Less conversion | Yes |
| Active-active inventory | Fancy | Oversell risk | No for MVP |

---

## 4. Architecture Diagram

### 4.1 End-to-end storefront

```text
                     ┌─────────────────────────────────────────┐
  Users ──DNS/Geo──► │              CDN / Edge POPs            │
                     │  media · HTML · PDP JSON · SWR          │
                     └──────────────────┬──────────────────────┘
                                        │ miss / dynamic
                     ┌──────────────────▼──────────────────────┐
                     │         Traffic Director / Cell Router   │
                     └───────────┬─────────────┬───────────────┘
                                 │             │
                    ┌────────────▼──┐     ┌────▼────────────┐
                    │  Cell A BFF   │     │  Cell B BFF     │
                    │  Cart/Checkout│     │  Cart/Checkout  │
                    └──────┬────────┘     └────┬────────────┘
                           │                   │
        ┌──────────────────┼───────────────────┼──────────────────┐
        │                  │                   │                  │
   ┌────▼────┐      ┌──────▼──────┐     ┌──────▼──────┐    ┌─────▼─────┐
   │ Catalog │      │   Search    │     │ Inventory   │    │ Payments  │
   │  Read   │      │  (regional) │     │ Reservation │    │  Adapter  │
   └────┬────┘      └──────┬──────┘     └──────┬──────┘    └─────┬─────┘
        │                 │                    │                 │
   ┌────▼────┐      ┌─────▼─────┐        ┌─────▼─────┐     ┌─────▼─────┐
   │ Redis   │      │  Index    │        │ Shard DBs │     │   PSP     │
   │ digests │      │  Cluster  │        │ (ASIN)    │     │           │
   └─────────┘      └───────────┘        └───────────┘     └───────────┘

   Order Service ──outbox──► Event Bus ──► Fulfillment / Email / Analytics
```

### 4.2 Cache hierarchy

```text
Client
  → L0 immutable assets (hash URLs)
  → L1 edge PDP (ASIN tags)
  → L2 in-process BFF
  → L3 Redis digests (catalog/price/avail)
  → L4 read replicas / Dynamo
Checkout → skip L1/L2 for money & reservation; hit SoT
```

### 4.3 Place-order sequence

```text
Client          BFF/Checkout      Idempotency    Inventory     Payments      Orders
  │  place        │                  │              │             │            │
  │──────────────►│                  │              │             │            │
  │               │── begin ────────►│              │             │            │
  │               │◄─ new/existing ──│              │             │            │
  │               │── reserve ─────────────────────►│             │            │
  │               │◄─ ok / soldout ─────────────────│             │            │
  │               │── auth ─────────────────────────────────────►│            │
  │               │◄─ ok / fail ─────────────────────────────────│            │
  │               │── create order + outbox ─────────────────────────────────►│
  │◄── 200 order_id──────────────────────────────────────────────────────────│
```

### 4.4 Prime Day traffic shaping

```text
Internet → WAF/Bot → Edge → Waiting Room (optional)
              → Browse pool (elastic)
              → Search pool (elastic)
              → Checkout pool (reserved capacity)
              → Deal ASIN inventory shards (isolated)
```

### 4.5 Failure domains

```text
AZ failure     → multi-AZ cells
Cell failure   → traffic director shifts hash ranges
Search failure → cached popular queries; degrade facets
Recs failure   → default homepage
Inventory hot  → isolate ASIN; queue deals
PSP failure    → pending + retry/inquire; no double auth
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. **Idempotent PlaceOrder** — same key ⇒ same `order_id`; no double charge.  
2. **Browse failure ≠ checkout corruption** — degrade soft deps first.  
3. **Reservation atomicity** — CAS / conditional decrement; oversell count ≈ 0.  
4. **Compensation** — every reserve has release; every auth has void/expiry path.  
5. **Single-writer order transitions** — conditional status updates.  
6. **Cell stickiness for in-flight checkout** — don’t migrate mid-saga without drain.  
7. **Cache never SoT for money/stock at purchase**.  
8. **At-least-once outbox**; consumers idempotent.  
9. **Admission control before** expensive inventory/payment work.  
10. **Deploy safety** — canaries per cell; auto rollback on SLO burn.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Origin stampede | SWR, singleflight, collapser |
| Redis fleet loss | Fail to replica; short TTL DB; shed noncritical |
| Search red | Serve cache; reduce features |
| Cart partition loss | Multi-AZ; restore from snapshots; accept rare cart loss ≪ order loss |
| Checkout dependency timeout | Fail fast; compensate; user retry with same key |
| Poison deploy | Cell canary + automated hold |

**Amazon interview signal:** name what you **page on**—`checkout_success_rate`, `inventory_oversell_count`, `edge_origin_error_rate`, `cell_availability`, `place_order_p99`.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Multi-AZ services; Redis; one regional search; vertical-ish checkout |
| 10× | CDN+SWR; separate pools; cart shard; Kafka; 4–12 cells; deal isolation |
| 100× | Strict cells; regional search; edge assembly; hot-ASIN special clusters |
| 1,000× | Hierarchical cells; global traffic policy; promise hierarchy for inventory |

**Hot keys**

- Celebrity/deal ASIN PDP: replicate read models; don’t share lock with inventory.  
- Inventory for deal ASIN: dedicated shard / token bucket of purchase slots.  
- Viral search query: result cache with jittered TTL.

**Partitioning**

| Entity | Partition key | Notes |
|--------|---------------|-------|
| Cart | customer_id | Cell-aligned |
| Order | customer_id or order_id hash | Cell-aligned writes |
| Inventory | asin | Hot ASIN isolation |
| Catalog | asin | Global read replicas |
| Search | term shards | Regional clusters |

**Autoscaling signals**

- Browse: RPS + p99 + cache hit  
- Search: queue latency + heap  
- Checkout: in-flight sagas + reserve latency (not just CPU)

### 5.3 Maintainability / operability

- Explicit **degrade ladder** documented and flag-driven.  
- Per-cell dashboards + global rollup.  
- Contract tests: catalog → search projection; price digest schema.  
- Chaos: kill recs, kill one cell, inject PSP latency.  
- Schema evolution via versioned PDP JSON and events.  
- Prime Day **freeze windows** for risky deploys.  
- Capacity reviews with load-test artifacts, not vibes.

**Kill switches (interview gold)**

1. Disable personalization  
2. Disable reviews on PDP  
3. Disable nonessential facets  
4. Enable waiting room  
5. Freeze catalog noncritical updates  
6. Shed search autocomplete  
7. Read-only mode for wishlists / lists  
8. Block bot ASNs more aggressively  

### 5.4 Consistency spectrum

| Data | Model | Why |
|------|-------|-----|
| Media / title | Eventual | CDN |
| Search index | Eventual | Scale |
| Recs | Hours OK | Batch |
| Cart | Strong per key | UX |
| Price at checkout | Strong reprice | Money |
| Inventory reserve | Strong | Oversell |
| Order | Strong per id | Support |

### 5.5 CDN & cache deep dive

**Stale-while-revalidate:** serve stale for T2 while refreshing—critical for Prime Day origin protection.

**Surrogate keys / tags:** purge `asin:B00…` across pages that embed it.

**Cookie / experiment bucketing:** include only coarse buckets in cache key; avoid personal cache explosion. Personalize via late fragment or client fetch.

**Thundering herd:**

```text
on miss:
  if singleflight(key) won:
      fetch origin; fill cache
  else:
      wait or serve stale
```

### 5.6 Cell routing deep dive

```text
cell = hash(customer_id) % N_cells
sticky cookie / token encodes cell
new customers assigned via consistent hash ring
rebalance: drain cell (no new checkouts) → migrate carts → shift ring
```

**Anti-pattern:** routing by ASIN for checkout—customer cart spans many ASINs; **customer-based cells** win.

### 5.7 Search deep dive

- Query cache for head queries.  
- Tiered clusters: head vs long-tail indexes optional at 100×.  
- Hydration batch-get from catalog cache (not N keyed RPCs).  
- Relevance changes via index-time features + limited query-time rerank; rerank is CPU-heavy—budget it.  
- Fail open to “popular in category” if cluster brownout.

### 5.8 Cart / checkout deep dive

**Cart:** DynamoDB-style single-item aggregate or Redis+durable; size limits; optimistic concurrency version.

**Checkout saga:**

```text
BEGIN idempotency
REPRICE
RESERVE inventory (multi-line, compensate on fail)
AUTH payment
PERSIST order + OUTBOX
COMMIT idempotency → order_id
```

Timeouts: inventory 50–100ms p99 target; payment 1–3s; total UX budget communicated.

### 5.9 Prime Day readiness

**T−90d:** capacity model from last year × growth; load tests on reservation path.  
**T−30d:** game days; kill switch drills; freeze calendars.  
**T−7d:** pre-warm caches; pin deal ASIN replicas; raise limits with PSP.  
**T−0:** war room; watching `checkout_success_rate`, origin RPS, oversell=0.  
**T+1d:** blameless review; tune TTLs and admission.

### 5.10 Observability

| Metric / alarm | Why |
|----------------|-----|
| `edge_cache_hit_ratio` | Cost/latency |
| `origin_rps` | Stampede detector |
| `search_p99` / error rate | UX |
| `cart_op_p99` | Hot partitions |
| `checkout_success_rate` | Revenue |
| `inventory_oversell_count` | Must be ~0 |
| `admission_reject_rate` | Capacity truth |
| `cell_availability` | Blast radius |
| `soft_dep_fallback_rate` | Degrade health |
| `saga_compensation_rate` | Fragility |

---

## 6. Wrap-Up

### 6.1 What we designed

A plan to run an **Amazon.com-class storefront at 10× traffic**, with a clear story for 100× / 1,000×: edge-first browse, multi-layer caches, scaled catalog/search, durable cart, protected checkout, customer-hashed **cells**, and a Prime Day operational program—without pretending one “QPS number” covers the site.

### 6.2 Key decisions worth defending

1. **Split QPS classes** — browse ≫ search ≫ cart ≫ checkout.  
2. **CDN + SWR + singleflight** — origin protection.  
3. **Cache digests; checkout SoT** — correctness.  
4. **Separate compute pools** — never starve checkout.  
5. **Customer-based cells** — blast radius.  
6. **Admission control** on place-order.  
7. **Hot-ASIN isolation** for deals.  
8. **Soft-fail personalization/reviews**.  
9. **Idempotent checkout + atomic reserve**.  
10. **Prime Day as a program**, not a hope.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Cache stampedes after bad purge | Tag purge + SWR + coalescing |
| Cell rebalance mid-checkout | Drain protocol |
| Search relevance under shed | Offline eval + cached head queries |
| Oversell on deal shards | Tokens / atomic slots; game day |
| PSP latency spike | Pending + inquire; capacity reserved |
| Cost explosion at 10× | Hit-ratio SLOs; media tiering |

### 6.4 How to present in 45 minutes

1. Clarify scope + split planes (6 min)  
2. Numbers with browse vs checkout (5 min)  
3. HLD + cache layers + cells (10 min)  
4. Checkout protection + inventory (10 min)  
5. Prime Day + degrade ladder (7 min)  
6. Invariants / Q&A (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Traffic & edge

**Q1: Why not cache personalized homepages at CDN?**  
A: Cache key explosion and privacy. Cache shell + late-load personalized fragments; or anonymized segment buckets only.

**Q2: How do you purge millions of PDPs after a price crawl?**  
A: Surrogate keys; event-driven invalidate of digests; accept short staleness; checkout reprices.

**Q3: Client says origin RPS 10× after a deploy—what happened?**  
A: Cache key change, dropped `Cache-Control`, version bump in all URLs, or disabled SWR. Roll back; restore keys.

**Q4: How does bot traffic change 10× planning?**  
A: WAF, bot scores, JS challenges; don’t scale checkout from bot browse.

### 7.2 Caching

**Q5: Stampede on one ASIN—walk through mitigation.**  
A: Singleflight, probabilistic early expire, replica reads, sticky negative cache.

**Q6: Is Redis required if CDN hit is 95%?**  
A: Still yes for hydration/search card batch and non-CDN API clients; CDN ≠ service cache.

**Q7: Consistency of availability in cache?**  
A: Digest with short TTL; checkout hits reservation SoT; UX may show “only 3 left” slightly stale.

### 7.3 Cells

**Q8: Why not cell-by-ASIN?**  
A: Cart/checkout are customer-centric; ASIN cells explode cross-cell transactions.

**Q9: How many cells at 10×?**  
A: Start 4–12; enough for canaries and blast radius, not so many that ops overhead dominates.

**Q10: Cross-cell gift cards / shared wallets?**  
A: Shared money services with their own single-writer homes; not stuffed into storefront cell DBs.

### 7.4 Search

**Q11: Search p99 explodes—first moves?**  
A: Shed facets, reduce size, disable heavy rerank, serve query cache, check hot shard.

**Q12: Index lag vs incorrect price—customer angry.**  
A: Apologize via reprice at checkout; search not SoT; SLO on index lag for critical fields optional.

### 7.5 Cart & checkout

**Q13: Guest cart merge races.**  
A: Versioned merge; audit; prefer deterministic policy; checkout revalidates lines.

**Q14: Payment auth succeeds, reserve fails.**  
A: Void/cancel auth; no PLACED order; metrics on this path.

**Q15: Exactly-once place-order?**  
A: Effectively-once via idempotency key + unique constraints; at-least-once events downstream.

### 7.6 Prime Day

**Q16: Waiting room fair?**  
A: Token lottery / virtual queue; prioritize Prime if product requires; communicate ETA; never silent drop.

**Q17: Deal ASIN sells out in 2s—system healthy?**  
A: Yes if oversell=0, checkout success for winners, losers get clear sold-out, no cascade.

**Q18: What do you load test?**  
A: Reservation path, idempotency store, payment timeouts, cache miss storms, cell failure.

### 7.7 Operability

**Q19: One cell’s checkout_success_rate drops 5%—actions?**  
A: Page; shift traffic; check deploy/deps; don’t globally restart all cells.

**Q20: How is this different from “just Kubernetes HPA”?**  
A: HPA doesn’t fix cache stampedes, hot keys, or oversell; architecture > replica count.

### 7.8 100× / 1,000× prompts

**Q21: What breaks first at 100× if you only did 10×?**  
A: Shared search noisy neighbors, cell count too low, purge storms, inventory hot keys, cross-region identity latency.

**Q22: Edge compute for PDP assembly—when?**  
A: When origin BFF CPU/network becomes the limiter after cache; push hydration to POP with regional data plane.

---

## 8. Appendices

## Appendix A — Example cache keys

```text
pd:v3:{marketplace}:{locale}:{asin}:{layout}
price:{marketplace}:{asin}
avail:{asin}:{region}
search:q:{marketplace}:{hash(query)}:{facets_hash}
cart:{customer_id}
idem:place:{customer_id}:{key}
```

## Appendix B — Scale checklist

- [ ] Split QPS classes documented  
- [ ] CDN SWR + surrogate keys  
- [ ] Singleflight on L3  
- [ ] Separate checkout pool  
- [ ] Cells with sticky routing  
- [ ] Hot-ASIN inventory isolation  
- [ ] Idempotent place-order  
- [ ] Degrade ladder flags  
- [ ] Prime Day game day completed  
- [ ] Oversell metric ≈ 0  

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| ASIN | Amazon product identifier |
| BFF | Backend-for-frontend / page service |
| Cell | Blast-radius-limited deployment slice |
| SWR | Stale-while-revalidate |
| Digest | Compact cached projection of entity fields |
| Admission control | Shed/queue before expensive work |
| Outbox | DB-consistent event publication pattern |
| Soft dependency | Fail open |
| Hard dependency | Fail closed |

## Appendix D — Estimation cheat-sheet

```text
Browse : Search : Cart : Checkout ≈ 100 : 40 : 10 : 1  (order of magnitude)
10× browse with 92% edge hit → 8% origin
Checkout 10K/s → inventory ~25K/s reserves
Never plan DB for full browse QPS
```

## Appendix E — Degrade ladder

| Level | Action | User impact |
|-------|--------|-------------|
| L1 | Disable recs / “sponsored” | Less personalization |
| L2 | Disable reviews / Q&A | Cleaner PDP |
| L3 | Search: no facets / autocomplete | Coarser findability |
| L4 | Waiting room for checkout | Delay |
| L5 | Freeze noncritical writes | Seller tooling lag |
| L6 | Browse-only mode | No new orders (extreme) |

## Appendix F — Place-order state sketch

```text
STARTED → REPRICED → RESERVED → PAYMENT_AUTHED → PLACED
                ↘︎ compensate ↙
         PAYMENT_FAILED / REJECTED_SOLD_OUT / CANCELLED
```

## Appendix G — Cell drain protocol

1. Mark cell `DRAINING` — no new sessions.  
2. Allow in-flight checkouts to complete (TTL).  
3. Block new place-order; redirect carts carefully.  
4. Reassign hash range.  
5. Observe dual-running metrics.  
6. Decommission.

## Appendix H — Prime Day runbook (interview gold)

| Time | Action |
|------|--------|
| T−90d | Capacity + PSP limits |
| T−30d | Game day; chaos |
| T−7d | Pre-warm; pin deals |
| T−1d | Freeze risky deploys |
| T−0 | War room; watch SLOs |
| T+2h | Spot tune admission |
| T+1d | Review; action items |

## Appendix I — Invariant tests

1. Double place with same key → one order.  
2. Two buyers one unit → one win.  
3. Recs 100% error → PDP still 200.  
4. Cell kill → error budget burn limited to cell %.  
5. Cache purge storm → origin RPS under cap.  
6. Payment timeout → no double auth on retry.  

## Appendix J — Ownership matrix

| Concern | Owner service |
|---------|---------------|
| PDP cached bytes | Edge + Catalog Read |
| Query relevance | Search |
| Cart lines | Cart |
| Stock truth at buy | Inventory |
| Money movement | Payments + Order |
| Blast radius | Traffic Director + Cell ops |

## Appendix K — Evolution hooks

- Marketplace offer service as first-class dependency  
- Edge worker PDP assembly  
- Hierarchical inventory promise (FC → region → global)  
- Per-deal purchase slot service  
- Multi-marketplace cell topologies  

## Appendix L — Sample SLO dashboard

```text
browse_availability{cell}           99.95%
search_p99_ms                       < 400
checkout_success_rate               > 99.5% (ex-soldout)
inventory_oversell_count            = 0
edge_cache_hit_ratio                > 0.90
admission_reject_rate               informational + alarm on spike
soft_dep_fallback_rate              < 5% steady
```

## Appendix M — Interview closing line

> “At 10× we don’t invent a new Amazon—we protect the revenue path, push browse to the edge, isolate blast radius with cells, and treat Prime Day as an operational product with admission control and a degrade ladder.”

---

*End of Amazon.com 10× traffic system design.*
