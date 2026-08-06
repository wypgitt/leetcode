# System Design: Global Food Delivery System

> **Focus areas:** Restaurant catalog · Courier matching · ETA · Payments · Order lifecycle · Multi-geo / multi-currency · Surge & fairness · Amazon / Uber Eats-style marketplace  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes, explicit invariants, Amazon themes (customer obsession, operational excellence, ownership, frugality)

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

Goal: **bound the marketplace**—diners discover restaurants, place orders, restaurants prepare food, couriers pick up and deliver, payments settle across parties, and the platform keeps **ETAs honest** across cities and countries.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are the actors? | Diners, restaurants, couriers, support, admins | Separate apps + identity; role authz |
| F2 | Core flow? | Browse → cart → checkout → restaurant accept → cook → courier assign → pickup → deliver → pay/payout | Order state machine is spine |
| F3 | Matching? | Assign courier to order (or batch); optimize ETA + cost + fairness | Matching service; not random |
| F4 | ETA? | Quote at browse/checkout; update live | ETA service with travel + prep models |
| F5 | Payments? | Auth at checkout; capture on deliver/hand-off; tips; refunds; restaurant/courier payouts | PCI-aware; ledger; PSP adapters |
| F6 | Catalog? | Menus, hours, modifiers, item availability | Menu service; eventual sync to search |
| F7 | Multi-geo? | Many cities/countries; local regs, currency, language | Geo cells; config per geo |
| F8 | Batching? | Courier may carry 2–3 orders | Batching in matcher |
| F9 | Scheduling? | ASAP + scheduled orders | Time-bucket scheduling |
| F10 | Ratings / trust? | Ratings for restaurant & courier; fraud | Trust signals in ranking/match |
| F11 | Live tracking? | Diner sees courier map | Location stream + fanout |
| F12 | Support? | Cancel, remake, refund, reassign | Ops tools + compensating txns |
| F13 | Discovery? | Search, cuisine filters, ranking | Search index per geo |
| F14 | Notifications? | Push/SMS/email on state changes | Async notify pipeline |
| F15 | Idempotency? | Checkout retries, webhook dupes | Keys everywhere money/state moves |

**MVP functional scope (lock with interviewer):**

1. Geo-scoped restaurant discovery + menu read.
2. Cart/checkout with price quote (items + fees + tax + tip).
3. Payment auth via PSP; order create durable.
4. Restaurant accept/reject + prep started/ready signals.
5. Courier matching for ASAP orders (single assignment MVP; batching Phase 2).
6. ETA quote + live updates.
7. Pickup → deliver → payment capture → basic payout records.
8. Cancel/refund paths for key states.
9. Push notifications for major transitions.
10. Basic fraud checks (velocity, stolen cards).

**Out of MVP (explicitly defer):**

- Perfect global active-active orders for one city
- Full grocery / retail multi-vertical
- Autonomous robots/drones
- Advanced ML batching across entire city as one MIP every second
- In-house acquiring bank

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Checkout latency? | Critical | p99 < 500ms in-region (excl. PSP) |
| N2 | Match latency? | After restaurant accept / ready policy | p99 < 5s assignment attempt |
| N3 | Location update? | Courier GPS | 1–5s sampling; fanout scalable |
| N4 | Availability? | Mealtime peaks | 99.9% order API; degrade non-critical |
| N5 | Consistency? | Money & order state | Strong per order; catalog eventual |
| N6 | Multi-region? | City home region | Home cell for order mutations |
| N7 | Durability? | Paid orders never lost | ACK after durable write |
| N8 | Compliance? | PCI, GDPR/CCPA, food regs, courier labor | Geo policy engine |
| N9 | Scalability | See table | Split browse/checkout/match/location QPS |
| N10 | Fairness | Couriers not starved; restaurants not buried | Rank + match constraints |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Diner orders ASAP → pay auth → restaurant accepts → courier assigned → pickup → deliver → capture → ratings.
2. Scheduled order for 19:00 → matcher runs near window → same flow.
3. Restaurant marks item 86’d → menu updates → carts validated at checkout.
4. Courier cancels → rematch within SLA → diner ETA updated.
5. Partial refund (missing item) → ledger adjustment + restaurant dispute path.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double checkout submit | Idempotency → one order |
| Restaurant never accepts | Timeout → cancel + auth void; suggest alternatives |
| Payment auth succeeds, DB fails | Reconcile with PSP; void or complete carefully |
| Courier GPS stale | ETA widens; maybe reassign |
| Surge demand, few couriers | Longer ETA / busy mode / delivery fee; never silent lie |
| Cross-border diner traveling | Serve local geo of delivery address |
| Menu price changed mid-cart | Reprice at checkout; require ACK |
| Split payment / gift card | Composite tender; careful capture |
| Restaurant offline mid-cook | Support playbook; refund/remake |
| Flash crowd after stadium event | Geo cell autoscale; match degrade to greedy |
| Tip adjust after deliver | Allowed window; payout adjustment |
| Chargeback | Ledger + evidence pack (timestamps, GPS breadcrumbs) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active cities | 50 | 200 | 1K | 5K |
| Restaurants | 100K | 1M | 10M | 50M |
| Couriers (MAU active) | 200K | 2M | 20M | 100M |
| Orders / day | 5M | 50M | 500M | 5B |
| Peak **browse/search QPS** | 50K | 500K | 5M | 50M |
| Peak **checkout QPS** | 2K | 20K | 200K | 2M |
| Peak **match decisions**/s | 1K | 10K | 100K | 1M |
| Peak **location updates**/s | 100K | 1M | 10M | 100M |
| Peak order events/s | 10K | 100K | 1M | 10M |
| Countries | 10 | 25 | 50 | 80+ |

**What each jump forces:**

- **10×:** Geo sharding; cache menus; async payments webhooks; match workers per city.
- **100×:** City cells; CQRS browse vs order; location mesh / hierarchical fanout; payout batching; multi-PSP.
- **1,000×:** Hierarchical geos; approximate ETA; courier presence indexes; marketplace fairness controllers; edge CDNs for catalog; strong cell isolation.

### 1.5 Etc. (Constraints & Assumptions)

- Map/ETA travel times from a distance matrix / OSRM-like service (can be internal).
- PSP handles card data (tokenization); we store tokens + ledger.
- Couriers are gig or employed depending on geo—policy differences matter.
- Amazon flavor: reliability of promise (ETA), selection, and operational excellence at meal peaks.

**Scope statement:**

> Design a global food-delivery marketplace connecting diners, restaurants, and couriers with durable orders, geo-scoped discovery, courier matching, honest ETAs, and payment/payout ledgers—baseline ~5M orders/day scaling through 10× / 100× / 1,000× via city/home-cell architecture.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Browse/search | 50K/s | 50M/s | Cache + CDN + geo index |
| Menu reads | 20K/s | 20M/s | Highly cacheable |
| Checkout / order create | 2K/s | 2M/s | Strong writes |
| Restaurant actions | 1K/s | 1M/s | Accept/ready |
| Match decisions | 1K/s | 1M/s | CPU + geospatial |
| Location updates | 100K/s | 100M/s | Dominant; special path |
| Tracking fanout reads | 20K/s | 20M/s | Websocket/SSE |
| Payment webhooks | 2K/s | 2M/s | Idempotent |
| Notifications | 5K/s | 5M/s | Async |

**Critical insight:** At 1,000×, **location updates (~100M/s)** dwarf checkouts. Never put raw GPS into the order OLTP path.

### 2.2 Concurrent orders & couriers

```text
Baseline 5M orders/day ÷ 86400 ≈ 58 orders/s average
Peak ~10× lunch/dinner → ~600/s (table 2K checkout includes retries/cart)

Active delivering concurrently:
If avg delivery duration 40 min = 2400s
600 completions/s × 2400 ≈ 1.44M in-flight globally at peak — heavy
Per city much smaller: 50 cities uneven; top city maybe 10–20% → design per city cell
```

### 2.3 Storage

```text
Order row ~2 KB; events ~500 B × 10 = 5 KB
5M/day × 7 × 7 KB ≈ 245 GB hot week

1,000×: 5B/day × 7 × 7 KB ≈ 245 TB hot — shard by geo/time; cold archive

Menu: 100K restaurants × 200 items × 500 B ≈ 10 GB
1,000× 50M × 200 × 500 B ≈ 5 PB if naive → normalize, CDN, per-geo indexes, don’t replicate all menus everywhere
```

**Unit check:** 5B × 7 KB = 35 PB/day would be wrong for “hot week.” Per day: 5e9 × 7e3 = 3.5e13 B = **35 TB/day**. ×7 ≈ **245 TB**. Correct.

### 2.4 Location bandwidth

```text
Update 100 B × 100M/s = 10 GB/s globally — needs hierarchical aggregation
Per city: if 1% of load → 1M/s × 100 B = 100 MB/s — still chunky; sample & geohash reduce
```

### 2.5 Matching compute

```text
Each match: query k candidate couriers (e.g. 30) + score
1K matches/s × 30 = 30K score ops/s — easy
1M/s × 30 = 30M — need geo indexes, caching travel times, approximate scoring
```

### 2.6 Money math

```text
Ledger entries ~4–8 per order (auth, capture, restaurant payable, courier payable, fees, tax)
5M × 6 ≈ 30M ledger rows/day baseline
Must be append-only, idempotent, reconcilable with PSP
```

---

## 3. High-Level Design

### 3.1 Domain entities

| Entity | Notes |
|--------|-------|
| Diner, Restaurant, Courier | Identities + roles |
| RestaurantOutlet | Geo point, hours, prep stats |
| Menu/Item/Modifier | Versioned prices |
| Cart / Quote | Ephemeral priced snapshot |
| Order | Durable state machine |
| Assignment | Order ↔ courier binding |
| PaymentIntent / LedgerEntry | Money truth |
| ETAEstimate | Quote + live |
| GeoCell / CityConfig | Policies, currency, PSP |

### 3.2 Service map

| Service | Role |
|---------|------|
| API Gateway / BFF | Diner/restaurant/courier apps |
| Catalog & Menu | Source of truth menus |
| Search / Discovery | Geo ranked listings |
| Quote / Pricing | Fees, tax, promotions |
| Order Service | State machine |
| Payment Service | PSP + ledger |
| Restaurant Hub | Accept/ready/86 |
| Matching Service | Assignment / batching |
| ETA Service | Prep + travel |
| Location Service | Courier presence |
| Tracking Fanout | Diner live map |
| Notification | Push/SMS |
| Payout | Settlements |
| Fraud / Risk | Scores |
| Support Ops | Tools |
| Config / Policy | Per-geo rules |

### 3.3 Order state machine (spine)

```text
CREATED → PAYMENT_AUTHORIZED → SENT_TO_RESTAURANT → ACCEPTED → PREPARING
 → READY_FOR_PICKUP → COURIER_ASSIGNED → AT_RESTAURANT → PICKED_UP
 → ARRIVING → DELIVERED → CAPTURED → CLOSED

Any eligible state → CANCELLED → VOID/REFUND paths
ACCEPTED → RESTAURANT_CANCELLED (competing path)
COURIER_ASSIGNED → COURIER_REASSIGN (loop)
```

### 3.4 Home cell principle

```text
delivery_address / outlet geo → city_id → home_region
All order mutations in home_region
Browse can be served from edge/CDN globally
Payments: regional PSP endpoints; ledger in home cell
```

### 3.5 Progressive architecture

| Scale | Shape |
|-------|-------|
| 1× | Modular monolith per region; Postgres; Redis; one PSP |
| 10× | Microservices; Kafka order events; city partitions |
| 100× | City cells; location subsystem separate; CQRS catalog |
| 1000× | Hierarchical presence; approx match; multi-PSP; cell mesh |

---

## 4. Architecture Diagram

### 4.1 Logical architecture

```text
  Diner App     Restaurant App     Courier App
      │              │                 │
      └──────────────┼─────────────────┘
                     ▼
              ┌─────────────┐
              │ API Gateway │
              └──────┬──────┘
     ┌───────────────┼──────────────────────────┐
     ▼               ▼                          ▼
┌─────────┐   ┌────────────┐             ┌────────────┐
│ Search  │   │  Catalog   │             │   Order    │
│ Discovery│   │   Menu     │             │  Service   │
└────┬────┘   └─────┬──────┘             └─────┬──────┘
     │              │        events            │
     │              ▼                          ▼
     │         ┌─────────┐              ┌────────────┐
     │         │  Quote  │◄────────────►│  Payment   │
     │         │ Pricing │              │  + Ledger  │
     │         └─────────┘              └────────────┘
     │                                        │
     │         ┌────────────┐          ┌──────┴──────┐
     │         │ Restaurant │          │  Matching   │
     │         │    Hub     │─────────►│  Service    │
     │         └────────────┘          └──────┬──────┘
     │                                        │
     │         ┌────────────┐          ┌──────┴──────┐
     └────────►│    ETA     │◄────────►│  Location   │
               │  Service   │          │  Presence   │
               └─────┬──────┘          └──────┬──────┘
                     │                        │
                     ▼                        ▼
               ┌────────────┐          ┌────────────┐
               │ Tracking   │          │  Notify    │
               │  Fanout    │          │            │
               └────────────┘          └────────────┘
```

### 4.2 City cell

```text
                Global Config / Identity
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
     Cell NYC        Cell London     Cell Tokyo
     orders*         orders*         orders*
     match*          match*          match*
     presence*       presence*       presence*
     ledger*         ledger*         ledger*

* = single-writer home for that city
Browse replicas/CDN everywhere
```

### 4.3 Matching loop

```text
Order becomes matchable (policy: on ACCEPT or on READY)
  → Match Planner enqueues job (city partition)
  → Candidate index: couriers in geohash rings near pickup
  → Score: ETA, acceptance likelihood, batch fit, fairness, cost
  → Offer to courier(s) OR auto-assign (geo policy)
  → On accept: Assignment durable; others fenced
  → On timeout: next candidate / expand radius / surge UX
```

### 4.4 Payment sequence

```text
Checkout:
  QuoteSnap → Create Order(CREATED) → PSP Auth → PAYMENT_AUTHORIZED
Delivered:
  Capture → CAPTURED → enqueue payout lines
Cancel:
  Void or partial refund → ledger compensating entries
Webhook:
  Idempotent apply by psp_event_id
```

---

## 5. Design Deep Dive

### 5.1 Marketplace truth vs projections

| Truth (strong) | Projection (eventual) |
|----------------|----------------------|
| Order state | Diner activity feed |
| Ledger balances | Restaurant analytics dashboards |
| Assignment binding | “Couriers near you” map heat |
| Menu source versions | Search documents |

Browse/search may lag; **checkout must revalidate** menu version + hours + availability.

### 5.2 Quote snapshots

```text
quote_id → {items, prices, fees, tax, tip, currency, menu_versions[], expires_at}
checkout must reference unexpired quote_id
if menu version drift → 409 REPRICE
```

Prevents “$12 UI → $18 charge” CX disasters (Amazon: customer trust).

### 5.3 Matching deep dive

**Objective (illustrative):**

```text
score = -w_eta * eta_to_diner
        -w_late * p_late
        -w_dist * deadhead_meters
        +w_batch * batch_synergy
        +w_fair * courier_fairness_boost
        -w_cancel * p_courier_cancel
```

**Policies:**

- Auto-assign vs offer-accept differs by country labor rules.
- Batching: constrain max detour & food wait time (cold food).
- Fairness: long-idle couriers get boost; avoid starvation.

**Data structures:**

- Geo-hash / H3 index of online couriers
- Optional: city grid aggregates for rough ETA
- Travel time cache: origin-dest cell pairs

### 5.4 ETA model

```text
eta_total ≈ wait_for_restaurant_accept
          + prep_time
          + courier_to_restaurant
          + wait_at_restaurant
          + restaurant_to_diner
          + buffers (weather, surge)
```

Show **ranges** under uncertainty; update on events (accept, ready, GPS). Never shrink ETA aggressively without evidence (trust).

### 5.5 Location service (scale-critical)

```text
Courier device → Location Ingest (city topic)
  → Presence Index (hot state: last_pt, speed, accuracy, ts)
  → optional downsample for tracking subscribers
  → NOT written into Order row each second
```

Fanout:

```text
Order tracking channel subscribers (usually 1–3)
Pull/push from presence by courier_id every 1–2s
At 1000× use hierarchical PubSub / MQTT-like / interest fanout
```

### 5.6 Payments & ledger

Principles:

1. **Idempotency keys** on auth/capture/refund  
2. Append-only **ledger** as internal money truth  
3. PSP is external; reconcile daily  
4. Never “update balance in place” without journal  

```text
LedgerEntry(order_id, party, amount, currency, type, psp_ref, idem_key)
Parties: DINER, PLATFORM, RESTAURANT, COURIER, TAX
```

Payouts: aggregate payable entries → transfer files / PSP payouts (batch).

### 5.7 Multi-geo concerns

| Concern | Approach |
|---------|----------|
| Currency | Order locked currency; FX only in reporting |
| Tax | Geo tax engine at quote time |
| Language | Catalog translations; device locale |
| Labor law | Match mode config per city |
| Data residency | Keep PII/orders in region |
| Alcohol | Age gates / banned hours config |

### 5.8 Failure handling & compensations

| Failure | Compensation |
|---------|--------------|
| Restaurant reject | Void auth; recommend alts |
| Courier no-show | Rematch; ETA rewrite |
| Food spilled | Remake or refund; courier incident |
| PSP down | Fail checkout closed; or delayed retry queue with clear UX |
| Matching backlog | Expand radius; busy banner; pause scheduled intake |

### 5.9 Fraud & abuse

- Card velocity / device fingerprint
- Promo abuse (new accounts)
- Courier GPS spoofing heuristics
- Restaurant collusion / fake orders
- Enumeration of order ids (UUIDs + authz)

### 5.10 Notifications

Event-driven from order stream; templates per geo/language; preference center; SMS costly—use push first.

### 5.11 Search / discovery

```text
Index doc: restaurant_id, geo, cuisine, rating, ETA_proxy, price_band, boosts
Query: lat/lng + filters → ranked list
Personalization optional; always re-check open/available at click
```

### 5.12 Consistency patterns

- Order: optimistic locking `version` on transitions  
- Assignment: conditional write `courier_id IS NULL`  
- Menu: version vectors; checkout validates  
- Presence: last-write-wins with timestamp + accuracy  

### 5.13 Observability

| Metric | SLO use |
|--------|---------|
| Checkout success rate | Revenue |
| Auth→Accept latency | Restaurant ops |
| Time-to-assign | Matching health |
| ETA error (signed) | Trust |
| Contactless deliver rate | CX |
| Refund rate | Quality |
| Location freshness p95 | Tracking |

### 5.14 10× / 100× / 1,000× changes

**10×:** Kafka, Redis presence, city partitions, menu CDN.

**100×:** Cell per metro; match workers sticky to city; travel-time matrices; payout batching; multi-PSP failover.

**1,000×:** Presence hierarchical aggregation; approximate candidate retrieval (ANN/geo); quote caching; browse fully edge; order cells autoshard; fairness controllers as separate feedback loops.

### 5.15 Amazon-flavored priorities

1. **Customer obsession:** honest ETA, easy refunds when we fail  
2. **Ownership:** clear pages for checkout vs match vs payments  
3. **Frugality:** don’t stream GPS through OLTP  
4. **Dive deep:** mealtime incident reviews with timelines  
5. **Deliver results:** on-time %, cost per delivery, selection  

### 5.16 Security

- OAuth / tokens per app role  
- Field-level encrypt PII  
- PCI SAQ-A via PSP tokens  
- Least privilege service-to-service mTLS  

### 5.17 Testing

- State machine property tests (illegal transitions impossible)  
- Idempotent payment webhook fuzz  
- Match simulation digital twin city  
- Chaos: kill matcher → backlog & recovery  

### 5.18 Batching (Phase 2 detail)

```text
Eligible if:
  same courier
  pickup proximity
  dropoff detour < X minutes
  food wait < Y minutes
  dietary/temp constraints OK
Score batch vs two singles; pick lower expected lateness cost
```

### 5.19 Restaurant capacity

Throttle orders when prep queue long; signal via `prep_load`; discovery can demote busy restaurants; better than mass late orders.

### 5.20 Data model sketch (order)

```text
Order {
  order_id, city_id, diner_id, restaurant_id,
  state, version,
  quote_id, currency, amounts...,
  courier_id?, assignment_id?,
  promise_eta, live_eta,
  timestamps...,
  idempotency_key
}
```

---

## 6. Wrap-Up

### 6.1 Design summary

A **city-home-cell food delivery platform** with durable orders, geo discovery, quote snapshots, PSP+ledger payments, restaurant ops hub, courier matching, specialized location/ETA planes, and progressive scale from 5M to 5B orders/day.

### 6.2 Top tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Global vs city cell writes | City home cell |
| Accurate GPS in OLTP vs side presence | Side presence |
| Auto-assign vs offer | Config per geo |
| Exact match MIP vs scored candidates | Scored + heuristics |
| Capture on deliver vs pickup | Deliver (diner protection) |

### 6.3 Risks

ETA trust erosion; payment reconciliation gaps; matcher unfairness; mealtime thundering herds; menu price drift.

---

## 7. Deeper / Related Interview Questions

### 7.1 Framing

**Q: Marketplace or 3-sided platform?**  
A: Three sides (diner/restaurant/courier) + platform policies; design incentives explicitly.

**Q: What’s the system of record for money?**  
A: Internal ledger reconciled to PSP—not the PSP UI.

**Q: What’s hardest at scale?**  
A: Location plane + mealtime peaks + multi-geo policy—not CRUD menus.

**Q: Amazon vs Uber Eats differences?**  
A: Similar marketplace; Amazon may emphasize Prime bundling, logistics shared services, stricter promise culture.

**Q: MVP cut line?**  
A: Single-assign ASAP in one region; batching/scheduled/global later.

### 7.2 Orders & state

**Q: Why version on order?**  
A: Fence concurrent restaurant/courier/support transitions.

**Q: Illegal transition attempt?**  
A: 409; log; metrics.

**Q: Long-running cook?**  
A: Timers; risk ETA; support SLA.

**Q: Exactly-once order create?**  
A: Idempotency key from client; durable dedupe.

**Q: Event sourcing orders?**  
A: Optional; event log + snapshot common; full ES not mandatory.

### 7.3 Matching

**Q: Greedy nearest courier?**  
A: Baseline; suboptimal under batching & fairness.

**Q: How large candidate set?**  
A: 20–50 typically; expand on failure.

**Q: Offer timeout?**  
A: 15–30s; cascading offers with fencing.

**Q: Avoid ping-pong reassigns?**  
A: Cooldown; max reassign count; cost of churn in score.

**Q: Multi-order batch NP-hard?**  
A: Yes—heuristics, insertion, local search; time-box.

**Q: Starving couriers?**  
A: Fairness term; rotating priority; monitor idle time Gini.

**Q: Restaurant wait vs diner wait?**  
A: Multi-objective; food quality constraint on max wait.

### 7.4 ETA

**Q: Why ETAs go wrong?**  
A: Prep variance, parking, weather, batching detours, optimistic models.

**Q: Train prep time?**  
A: Per restaurant/item histograms + online features.

**Q: Show exact minute?**  
A: Prefer range; update cadence.

**Q: ETA regression after feature launch?**  
A: Shadow models; online eval of signed error.

### 7.5 Location

**Q: Write GPS into Postgres per ping?**  
A: No—presence service / Redis / specialized store.

**Q: 100M updates/s?**  
A: Sample, compress, geo aggregates, city cells, edge ingest.

**Q: Spoofed GPS?**  
A: Sensor consistency, jump detection, attestation where possible.

**Q: Privacy?**  
A: Share location only for active jobs; retention limits.

### 7.6 Payments

**Q: Auth vs capture?**  
A: Auth holds funds; capture finalizes—timing policy matters.

**Q: Partial capture?**  
A: Supported for missing items; ledger lines.

**Q: Webhook before local write visible?**  
A: Idempotent applicator; state machine guards.

**Q: Double refund?**  
A: Idempotency key; ledger unique constraints.

**Q: Multi-currency order?**  
A: Don’t; lock one currency per order.

**Q: Tips after delivery?**  
A: Adjustment window; payout delta.

**Q: Chargebacks?**  
A: Evidence: timestamps, GPS, photos, chat logs.

### 7.7 Catalog & search

**Q: Menu consistency at checkout?**  
A: Version check against quote.

**Q: 86 item propagation?**  
A: Push invalidation; short TTL cache.

**Q: Search ranking abuse (SEO)?  
A: Fraud/quality signals; paid placement disclosed.

**Q: Huge photo assets?**  
A: CDN; not in order path.

### 7.8 Multi-geo

**Q: Cross-city order?**  
A: Unusual; delivery address defines city cell.

**Q: Data residency?**  
A: Keep personal order data in-region.

**Q: Local holidays?**  
A: City config calendars for hours/fees.

**Q: Active-active two regions one city?**  
A: Avoid dual writers; RPO/RTO DR instead.

### 7.9 Reliability

**Q: Matcher down at dinner?**  
A: Queue backlog; greedy nearest failover; busy UX.

**Q: Kafka lag on order events?**  
A: Notify/ETA delayed; core transitions still sync API.

**Q: PSP outage?**  
A: Fail closed checkout; status banner; retry later.

**Q: Hot restaurant thundering herd?**  
A: Capacity throttle; cache; queue at restaurant hub.

### 7.10 Security & trust

**Q: Authorize courier to see diner phone?**  
A: Masked number / proxy calling.

**Q: Enumerate restaurants’ private margins?**  
A: Authz; separate confidential APIs.

**Q: Insider refund abuse?**  
A: Dual control; audit; anomaly detection.

### 7.11 Observability drills

**Q: Debug “courier assigned but diner sees none”?**  
A: Fanout lag; wrong city channel; app cache; assignment fenced.

**Q: Debug spike in late deliveries?**  
A: ETA model, traffic, batching detour, restaurant prep, weather.

**Q: Debug checkout 500s?**  
A: Distinguish quote, order write, PSP; dependency map.

### 7.12 Comparisons

**Q: vs ridesharing?**  
A: Extra restaurant prep uncertainty; food wait constraints; two pickups (store+diner).

**Q: vs Amazon retail delivery?**  
A: Hot food SLA minutes not days; courier marketplace; restaurant side.

**Q: vs grocery?**  
A: Heavier substitution logic; larger baskets; different batching.

### 7.13 Product edge cases

**Q: Contactless drop-off?**  
A: Photo proof; geofence; tip still allowed.

**Q: Leave at door in apartment?**  
A: Access instructions; courier app checklist.

**Q: Allergies?**  
A: Notes best-effort; legal disclaimers; not guaranteed in MVP.

**Q: Group orders?**  
A: Multiple diners one delivery; cart merge complexity—defer or limited.

### 7.14 Arithmetic traps

**Q: 5B orders/day × 7 KB = ?**  
A: ~35 TB/day.

**Q: 100M loc/s × 100 B = ?**  
A: 10 GB/s.

**Q: Average vs peak lunch?**  
A: Always provision on peak; say 5–15× average depending on geo.

### 7.15 Org / ownership

**Q: Who owns ETA errors?**  
A: ETA science for model; matching if detours; restaurant ops if prep; platform for plumbing.

**Q: Payment dispute page?**  
A: Payments + support; order timeline evidence from order platform.

### 7.16 Fairness & ethics

**Q: Dark kitchens ranking?**  
A: Disclose; quality control.

**Q: Courier over-assignment?**  
A: Cap concurrent; labor policy.

**Q: Surge pricing honesty?**  
A: Clear fees; no hidden bait ETA.

### 7.17 API design

**Q: Checkout API essentials?**  
A: quote_id, idempotency_key, tender, delivery_address, tip.

**Q: Restaurant accept API?**  
A: order_id, version, estimated_prep_minutes.

**Q: Courier accept offer?**  
A: offer_id, fencing token.

### 7.18 Scaling presence index

**Q: Redis GEO enough?**  
A: To mid scale yes; at extreme use sharded H3 + cell local memory + tiered accuracy.

**Q: Memory for 20M couriers online?**  
A: 20M × 100 B = 2 GB raw—fine globally; shard per city for write QPS.

### 7.19 DR

**Q: Region fail?**  
A: Promote city cell replica; fence old; in-flight payments reconcile; expect some rematches.

### 7.20 Closing

**Q: One-week peak readiness?**  
A: Load test city cells, matcher failover, payment idempotency, ETA honesty banners, restaurant capacity throttles—not a rewrite.

---

## 8. Appendices

### 8.1 Schemas

```text
Orders (Dynamo/Aurora sharded by city)
  PK: ORDER#<id>  or city_id + order_id
  attrs: state, version, parties, amounts, etas, courier_id, timestamps

Assignments
  PK: ORDER#<id>
  attrs: courier_id, offer_id, state, fencing_token

Ledger
  PK: LEDGER#<id>
  GSI: order_id, party_id
  attrs: amount, currency, type, idem_key, psp_ref

Menus
  PK: REST#<id> SK: ITEM#<id>#VER#<n>

Presence (Redis)
  courier_id → {lat, lng, ts, acc, status, city_id}
  GEO index per city
```

### 8.2 Invariants

| Invariant | Rule |
|-----------|------|
| Single active courier | ≤1 ASSIGNED courier per order |
| Money conservation | Ledger sum per order explains tender & payables |
| Quote bind | Capture amounts ≤ authorized / per policy |
| Versioned transitions | CAS on order.version |
| Geo home | Mutations in home cell only |

### 8.3 Scale checklist

| Scale | Must |
|-------|------|
| 1× | Order SM, payments, basic match, ETA, menu |
| 10× | City partitions, Kafka, presence Redis |
| 100× | Cells, batching, multi-PSP, travel matrices |
| 1000× | Hierarchical location, approx match, edge catalog |

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Home cell | Region/city writer for orders |
| Quote snapshot | Priced immutable cart view |
| Deadhead | Courier travel without order |
| 86 | Item unavailable |
| Capture | Finalize payment |
| Presence | Live courier location state |
| Batching | Multi-order courier route |

### 8.5 Estimation cheat-sheet

```text
loc_bandwidth = updates/s × bytes
hot_order_storage ≈ orders/day × retention_days × bytes/order
candidate_ops ≈ matches/s × k
in_flight ≈ peak_complete/s × duration_s
```

### 8.6 API sketch

```text
GET  /v1/restaurants/search?lat&lng
GET  /v1/restaurants/{id}/menu
POST /v1/quotes
POST /v1/orders  (Idempotency-Key)
POST /v1/orders/{id}/accept   # restaurant
POST /v1/orders/{id}/ready
POST /v1/offers/{id}/accept   # courier
POST /v1/orders/{id}/deliver
POST /v1/payments/webhooks/psp
GET  /v1/orders/{id}/tracking
```

### 8.7 Sample score weights

```text
w_eta=1.0 w_late=3.0 w_dist=0.2 w_batch=0.8 w_fair=0.5 w_cancel=2.0
```

### 8.8 State transition table (excerpt)

| From | To | Actor |
|------|----|-------|
| CREATED | PAYMENT_AUTHORIZED | Payment |
| PAYMENT_AUTHORIZED | SENT_TO_RESTAURANT | Order |
| SENT_TO_RESTAURANT | ACCEPTED | Restaurant |
| READY_FOR_PICKUP | COURIER_ASSIGNED | Matcher |
| PICKED_UP | DELIVERED | Courier |
| * | CANCELLED | Policy |

### 8.9 Risks register

| Risk | Mitigation |
|------|------------|
| ETA trust | Ranges + continuous eval |
| Payment drift | Daily reconcile |
| Matcher unfairness | Fairness metrics |
| Peak outage | Cell isolation |
| Menu drift | Quote versions |

### 8.10 SLOs

| SLO | Target |
|-----|--------|
| Checkout p99 (excl PSP) | < 500ms |
| Assign p99 after matchable | < 5s |
| ETA abs error median | < 5 min |
| Location freshness p95 | < 10s |
| Duplicate captures | 0 |

### 8.11 Decision log

| Decision | Pick | Why |
|----------|------|-----|
| Write boundary | City cell | Scale + residency |
| GPS path | Presence service | QPS |
| Money | Ledger + PSP | Audit |
| Match | Scored candidates | Practical |
| Capture time | On deliver | Diner protection |

### 8.12 Related systems

- Restaurant registration / onboarding (sibling doc)
- Route optimization for courier batches
- Fraud platform
- Notification platform
- Maps / distance matrix

### 8.13 Incident timeline template

```text
T0 diner checkout
T1 restaurant accept
T2 first assign
T3 pickup
T4 deliver
Compare promised ETA vs actual; annotate reassigns & waits
```

### 8.14 Amazon narrative (2 min)

> “I’d design global food delivery as a **city-home-cell marketplace**. Browse and menus are cache-friendly and edge-served; orders, payments, and matching are strongly consistent inside the city cell. The order state machine is the spine; a ledger is the money truth; courier GPS lives in a specialized presence plane because it can be 100× the checkout QPS. Matching scores ETA, cost, batching, and fairness under geo policy. At 1,000× we add hierarchical location and approximate candidate retrieval—without ever lying about ETA.” 

### 8.15 Checkpoint

1. Split QPS classes?  
2. Home cell for orders?  
3. Quote versioning?  
4. Ledger idempotency?  
5. Presence not OLTP?  
6. Honest ETA under surge?  

### 8.16 Extensions

- Group ordering  
- Loyalty / Prime benefits  
- Retail convenience stores  
- Drone / robot handoff  
- Carbon-aware batching  

---

*End of document — Global Food Delivery (Amazon SDE III system design)*
