# System Design: Facebook Travel Booking

> **Focus areas:** Marketplace booking · Inventory sync · Payments · Fraud · Partner APIs · Idempotency · Search/ranking · Cancellation · Multi-party state machine · Trust & safety · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split search/booking/payment/partner planes, explicit consistency for inventory, deal-breakers for “double-book the hotel” fantasies  
> **Interview theme:** Meta L5+ marketplace — social discovery + real booking money path; integrity (fraud, fake listings) matters as much as latency

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—a **travel booking** surface on Facebook that lets users discover stays/flights/experiences (social + ads + organic), hold inventory, pay, and receive confirmation—without becoming a full GDS or airline host.

### 1.0 What this is / is not

| Dimension | **Facebook Travel Booking (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Discover → quote → reserve → pay → confirm travel products | Own all hotel PMS / airline inventory |
| Success | Successful bookings, low fraud, partner SLA, social conversion | Perfect global fare shopping like Kayak alone |
| Inventory | Aggregated via partners (OTA/hotel chains); soft holds | Single source of truth for every room worldwide |
| Social | FB graph, Groups, Reels, ads drive demand | Rebuild Instagram travel feed from scratch |
| Payments | Meta Pay / PSP + partner settlement | Become a bank |
| Trust | Fake listings, payment fraud, account takeover | Ignore integrity |

**Scope statement:** Design a travel-booking feature for Facebook users: search/browse, quote, hold, book, pay, cancel/refund, partner sync, fraud controls, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What can users book? | Hotels MVP; flights/experiences Phase 1.5 | Product-type plugins; hotel first |
| F2 | Who holds inventory? | Partners (OTA/chains); Meta is marketplace | Partner adapters; never invent rooms |
| F3 | Search inputs? | Destination, dates, guests, filters, price | Search index + live quote path |
| F4 | Social angle? | Friends who visited, Group posts, ads, Messenger share | Graph features for ranking; deep links |
| F5 | Booking flow? | Search → details → quote → hold → pay → confirm | Explicit state machine |
| F6 | Soft hold TTL? | 10–15 min typical | Hold store + expiry workers |
| F7 | Payments? | Card / Meta Pay; 3DS where required | PSP integration; PCI out of Meta vault if possible |
| F8 | Cancellations? | Partner policy-driven refunds | Policy engine + refund async |
| F9 | Confirmations? | In-app + email; voucher/QR | Notification + document store |
| F10 | Multi-currency? | Yes for markets | FX at quote lock + settlement |
| F11 | Fraud / fake hotels? | Critical — Trust & Safety | Listing verification + booking fraud scores |
| F12 | Admin / partner ops? | Partner portal, dispute, inventory refresh | Control plane separate |

**MVP functional scope:**

1. Search hotels by destination + dates + guests; ranked results.  
2. Property detail page with rooms, photos, reviews (partner + FB social signals).  
3. Live **quote** (price/availability) from partner; lock price for short TTL.  
4. **Hold** inventory; **book** after payment authorization.  
5. Confirmation, voucher, calendar/Messenger share.  
6. Cancel/refund per policy; status APIs.  
7. Partner webhook ingest for booking updates.  
8. Fraud checks on listing + user + payment.  
9. Basic social: “friends stayed here”, share itinerary.

**Out of MVP:**

- Full NDC airline shopping for all carriers  
- Meta-owned hotel PMS  
- Complex multi-city packages (hooks only)  
- Fully offline agents / call-center booking  
- Crypto payments

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Search latency | Feels snappy | p99 < 300–500ms (cached facets); live quote separate |
| N2 | Quote freshness | Accurate enough to book | Quote age < 60–120s or revalidate |
| N3 | Booking success after pay auth | No silent loss | Exactly-once booking intent; partner idempotency keys |
| N4 | Double-booking | Must not oversell Meta-side hold | Hold + partner confirm; compensate on failure |
| N5 | Payment durability | Auth/capture ledgered | Append-only payment events |
| N6 | Availability | Browse OK degraded; book path critical | 99.9% book API; search stale OK |
| N7 | Fraud false negative | High cost | Multi-layer checks; step-up |
| N8 | Compliance | PCI, GDPR, travel regs | Tokenized cards; geo data residency hooks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User searches “Tokyo Apr 10–14, 2 adults” → ranked hotels → opens property → live quote → hold → pay → partner confirm → voucher.  
2. Friend share deep link → land on property → book.  
3. User cancels within free window → refund initiated → status updated.  
4. Partner pushes rate change → search index updated asynchronously.  
5. Ad click → travel landing → same book path with attribution.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Partner quote fails mid-flow | Fail soft; suggest alternates; no charge |
| Hold expires during pay | Re-quote; never capture without valid hold |
| Partner confirms after timeout | Reconciliation job; user notified if late confirm/fail |
| Payment auth OK, partner book fail | Void/refund; apology + retry inventory |
| Duplicate submit (double tap) | Idempotency key on book intent |
| Price change after quote | Revalidate; require user ack if delta > threshold |
| Fake listing / scam hotel | T&S takedown; block book; clawback |
| ATO booking to mule address | Device/session risk; step-up auth |
| Partial multi-room book | All-or-nothing MVP; saga compensate |
| Currency mismatch | Lock FX at quote; settle in partner currency |
| Webhook out of order | Versioned booking status; monotonic state machine |
| Partner rate limit | Circuit breaker; cache search; degrade live quote |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU using Travel surface | 5M | 50M | 500M | global FB travel |
| Search QPS (peak) | 5K | 50K | 500K | 5M |
| Live quote QPS | 500 | 5K | 50K | 500K |
| Holds created / day | 200K | 2M | 20M | 200M |
| Completed bookings / day | 50K | 500K | 5M | 50M |
| Peak book TPS | 20 | 200 | 2K | 20K |
| Partner integrations | 20 | 50 | 200 | 500+ |
| Properties indexed | 2M | 5M | 20M | 50M+ |
| Payment events / day | 150K | 1.5M | 15M | 150M |
| Fraud checks / book | 1 pipeline | +ML | +graph | cell-local T&S |

**What each jump forces:**

- **10×:** Search cache + CQRS; partner connection pools; booking saga hardened.  
- **100×:** Regional booking cells; partner shard adapters; async quote fanout; fraud feature store.  
- **1,000×:** Multi-geo settlement; inventory predictive cache; hierarchical partner gateways; edge search.

### 1.5 Etc. (Constraints & Assumptions)

- Meta does **not** own hotel inventory; partners are SoT for availability.  
- Social graph is a **ranking/attribution** input, not inventory.  
- PCI: prefer PSP tokenization; Meta stores payment tokens/refs only.  
- Booking is a **distributed saga** across Meta, PSP, partner.  
- Integrity (fake listings, payment fraud) is in-scope for Meta Trust & Safety.

**Scope statement to repeat back:**

> Design Facebook Travel Booking: social-aware hotel search, live partner quotes, time-bounded holds, idempotent pay-and-book saga, cancellations, partner sync, and fraud/T&S controls—scaling browse and book paths independently through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Search reads** | Destination/date queries | ~5K QPS | ~50K | Search index + cache |
| **Detail reads** | Property pages | ~2K QPS | ~20K | CDN + property store |
| **Live quotes** | Partner availability/price | ~500 QPS | ~5K | Quote service + partners |
| **Holds** | Soft inventory locks | ~10/s | ~100/s | Hold DB |
| **Book + pay** | Money path | ~20 TPS | ~200 TPS | Booking saga |
| **Webhooks** | Partner status | ~50/s | ~500/s | Ingest bus |
| **Fraud score** | Per book / high-risk browse | ~30/s | ~300/s | T&S |

**Anti-pattern:** one “QPS” mixing CDN property images, Elasticsearch search, and Stripe captures.

### 2.2 Search index size

```text
2M properties × ~5 KB denormalized doc = ~10 GB raw
+ room types, photos refs, geo → ~50–100 GB indexed
Trivial for ES/OpenSearch cluster; photos on CDN/object store separately
At 20M properties: still low TBs — search not the hard part; live quote & book are
```

### 2.3 Quote amplification

```text
Search returns 50 hotels; naive live-quote all 50 on every search
= 5K search/s × 50 = 250K partner calls/s → DEAL-BREAKER

Must: cache search with stale prices bands; live-quote only top-N on viewport
      or quote-on-detail; batch partner multi-get; TTL cache by (property, dates, guests)
```

### 2.4 Hold & book storage

```text
200K holds/day × 15 min TTL → steady ~2K active holds (200K × 15/1440)
Bookings retained 7 years compliance: 50K/day × 365 × 7 × 5 KB ≈ 640 GB metadata
Payment event log larger; fine for OLTP + cold archive
```

### 2.5 Money path latency budget

```text
User click Book → total p99 < 8–12s perceived
  Meta validate + fraud: 200–500ms
  PSP auth: 1–3s
  Partner book: 1–5s
  Persist + notify: 200ms
Async: capture, voucher PDF, email, attribution
```

### 2.6 Fraud cost intuition

```text
50K bookings/day × $200 AOV = $10M GMV/day
0.5% fraud without controls = $50K/day loss → justifies heavy T&S
False positives also hurt conversion — tune with step-up not hard block when unsure
```

### 2.7 Booking funnel math (say out loud)

```text
Baseline daily (order-of-magnitude):
  Search sessions:           5M
  Detail views:              1M   (20% of search)
  Live quotes:               400K  (40% of detail)
  Holds created:             200K  (50% of quote)
  Pay attempts:              80K   (40% of hold)
  Confirmed bookings:        50K   (62.5% of pay attempt)
  Cancel within 48h:         5K    (10% of confirmed)

Conversion levers ≠ one “QPS”:
  search→detail: ranking + social + price band honesty
  quote→hold: quote latency / sold-out rate
  hold→pay: UX + trust badges + payment methods
  pay→confirm: partner SLA + fraud false-positive rate

Integrity events along funnel (baseline/day):
  listing trust checks on detail:     ~1M (cached)
  fraud score on pay attempt:         ~80K
  step-up challenges:                 ~4K (5%)
  hard blocks:                        ~800 (1%)
  listing suspensions (async):        ~50–200
  chargeback / dispute tickets:       ~100–300
```

**Interview punchline:** browse QPS is cheap; **money-path TPS × partner RTT × fraud** is the hard plane. Quote amplification (Section 2.3) is the classic deal-breaker math.

### 2.8 Partner SLA & timeout budget

```text
Partner p95 RTT quote: 800ms; book: 2s; timeout budget: 5s
At 500 quote/s with 20% miss cache:
  open partner calls ≈ 100/s
  if top partner is 40% of traffic → 40/s to one egress pool — size CB/bulkhead

PARTNER_UNKNOWN rate target: < 0.5% of books
Each UNKNOWN holds auth ~15–60 min → working capital / auth expiry risk
At 20 book TPS × 0.5% = 0.1 UNKNOWN/s ≈ 6/min — reconciler must keep up
```

### 2.9 Integrity / T&S event volume

```text
Per confirmed booking emit integrity envelope:
  {user, device, listing_trust, pay_risk, graph_cluster_flags, decision}
80K pay attempts/day × ~2 KB envelope ≈ 160 MB/day (hot)
Feature store online reads: ~100–300/s at peak book — trivial vs ads delivery
Photo reverse-image jobs: batch on new listings (thousands/day) not per search
```

### 2.10 100× funnel stress check

```text
100×: 5M bookings/day, 2K book TPS peak
Auth-then-capture PSP: 2K auth/s — need multi-MID / regional PSPs
Partner gateway: bulkheads per partner; no single adapter thread pool
Fraud: feature store + model cells; human review only high-AOV / high-risk
Search 500K QPS: 100% cached cards; live quote never on SERP
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/travel/search` | Destination, dates, guests, filters → ranked property cards |
| `GET /v1/travel/properties/{id}` | Detail + rooms + social signals |
| `POST /v1/travel/quotes` | Live price/availability for property+rooms |
| `POST /v1/travel/holds` | Create soft hold (TTL) |
| `POST /v1/travel/bookings` | Idempotent book with `Idempotency-Key` |
| `GET /v1/travel/bookings/{id}` | Status / voucher refs |
| `POST /v1/travel/bookings/{id}/cancel` | Cancel + refund policy |
| `POST /internal/partners/webhooks/{partner}` | Partner status updates |
| `GET /v1/travel/itineraries/{id}` | Shareable itinerary |

**Core schemas:**

```text
QuoteRequest { property_id, room_id?, check_in, check_out, guests, currency }
Quote { quote_id, price, currency, taxes, cancel_policy, expires_at, partner_ref }

Hold { hold_id, quote_id, user_id, expires_at, status }

BookingIntent {
  intent_id,          // idempotency
  hold_id, user_id,
  payment_method_ref,
  guest_details,
  status: CREATED|PAY_AUTH|PARTNER_PENDING|CONFIRMED|FAILED|CANCELLED
}
```

### 3.2 Data model

| Entity | Store | Key | Notes |
|--------|-------|-----|-------|
| Property catalog | Search index + KV | `property_id` | Denormalized for search |
| Quote | Redis / KV TTL | `quote_id` | Short-lived |
| Hold | OLTP | `hold_id` | Expiry index |
| Booking | OLTP | `booking_id` / `intent_id` | State machine |
| Payment ledger | Append-only | `payment_event_id` | Auth/capture/void/refund |
| Partner mapping | OLTP | `(partner, partner_booking_id)` | Reconciliation |
| Fraud features | Feature store | `user_id` / `listing_id` | Nearline + online |
| Itinerary docs | Object store | `booking_id` | PDF/QR |

### 3.3 Booking state machine

```text
CREATED
  -> PAY_AUTHORIZED          (PSP auth success)
  -> PARTNER_PENDING         (call partner book)
  -> CONFIRMED               (partner ack)
  -> CANCELLED               (user/policy)
FAILED                       (any terminal fail; compensate)

Illegal: CONFIRMED -> PAY_AUTHORIZED
Monotonic version++; webhooks apply only if version newer / allowed transition
```

### 3.4 Why X over Y — inventory & consistency

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Live partner always** | Accurate | Latency; partner rate limits | Detail/quote/book |
| **Cache availability only** | Fast search | Stale sold-out | Search cards with band prices |
| **Meta-owned inventory DB** | Control | Lie about rooms we don’t own | **Deal-breaker as SoT** |
| **Soft hold at Meta + partner hold** | UX timer | Two-phase complexity | **MVP book path** |
| **Pessimistic global lock** | No double book Meta-side | Doesn’t stop other OTAs | Insufficient alone |

**Chosen MVP:**

1. Search from **cached catalog** + approximate price bands.  
2. Detail triggers **live quote** (cached ≤60–120s by key).  
3. Hold creates Meta hold + partner hold/reservation if API supports.  
4. Book = pay auth → partner confirm → capture (or auth-only then capture on confirm).  
5. Compensation saga on partial failure.

**Deal-breaker:** deducting inventory only in Meta Redis while partner still sells the room elsewhere—and claiming strong correctness.

### 3.5 Why X over Y — payments

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Auth then capture on confirm | Don’t take money if partner fails | Auth expiry windows | **Strong default** |
| Capture immediately | Simple | Refunds on partner fail | Avoid MVP |
| Partner collects payment | Less PCI | Worse unified UX / disputes | Some partners only |
| Meta Pay wallet | Conversion | Region coverage | Where available |

### 3.6 Why X over Y — search ranking

| Signal | Role |
|--------|------|
| Price / value | Core |
| Review score | Quality |
| Distance / geo | Relevance |
| Friend stayed / liked | Social graph boost |
| Ad bid / campaign | Sponsored slots separated |
| Listing trust score | T&S downrank/block |
| Conversion rate | Learning-to-rank Phase 1.5 |

**Deal-breaker:** mixing paid ads into organic rank without disclosure labels.

### 3.7 Pipeline topology

```text
FB app → API Gateway → Travel BFF
  → Search Service (index)
  → Quote Service → Partner Gateway → Hotel/OTA APIs
  → Hold Service → Booking Orchestrator
       → Payments Service → PSP
       → Fraud Service → T&S
       → Partner book
  → Notification + Itinerary
Partner webhooks → Ingest → Booking updater
Catalog sync jobs → Property index
```

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Inventory SoT | Partner | We don’t own rooms | Meta-only stock DB |
| Search vs quote | Split planes | Amplification | Live-quote all search results |
| Book path | Saga + idempotency | Distributed failure | Single local TX across PSP+partner |
| Pay | Auth-then-capture | Avoid unpaid failures charging | Capture-first |
| Fraud | Inline + async review | Money + trust | No checks for “growth” |
| Social | Rank features | Meta differentiator | Require friends to book |

### 3.9 Compliance, payments, and trust planes

Marketplace booking sits at the intersection of **PCI**, **consumer travel regs**, **privacy**, and **Meta Integrity**. Call these out in HLD before deep dive.

| Plane | Obligation | Design hook |
|-------|------------|-------------|
| **PCI / payments** | No raw PAN in Meta vault if avoidable | PSP tokens; network tokens; 3DS/SCA orchestration |
| **GDPR / CCPA** | Purpose limitation; deletion | Booking retention vs marketing; DSAR joins |
| **Travel / consumer** | Clear cancel policy, price transparency | Policy snapshot at book; price-change ack |
| **Tax / invoicing** | VAT/occupancy where Meta is MoR | MoR vs agent-model flag per partner/market |
| **Sanctions / KYC** | Block prohibited counterparties | Listing + payee screening |
| **Integrity / T&S** | Fake listings, payment fraud, ATO | Inline score + async listing ops |
| **Ads attribution** | Privacy-preserving conversion | Aggregated / delayed conversion APIs |

**Merchant-of-record fork (ask interviewer):**

| Model | Meta role | Disputes | UX |
|-------|-----------|----------|-----|
| **Agent / marketplace** | Facilitates; partner charges or Meta passes through | Partner-heavy | Harder unified support |
| **Meta MoR** | Meta charges user; settles to partner | Meta owns chargebacks | Cleaner UX; heavier finance/compliance |

**MVP interview default:** Meta orchestrates payment (tokenized PSP) with explicit MoR per market—document which markets are MoR vs partner-collect.

**Trust UX (Meta flavor):**

- Show **listing trust** subtly (verified property) without teaching attackers the model.  
- Social proof (“friends visited”) only under privacy ACL.  
- Sponsored hotels **labeled**; never silently blended as organic (Ads Integrity adjacency).  
- Fraud step-up copy is generic (“confirm it’s you”), not “we think this hotel is fake.”

**Deal-breaker:** optimizing conversion by disabling fraud checks on “trusted FB login” alone—login ≠ payment integrity.

### 3.10 Consistency matrix (browse vs money)

| Data | Consistency | Rationale |
|------|-------------|-----------|
| Search price bands | Eventual (minutes–hours) | Amplification / partner cost |
| Live quote | Strong enough for TTL | User commits on this number |
| Hold | Cell-local strong | Timer UX + race control |
| Booking status | Strong in cell + UNKNOWN | Money path |
| Partner webhook view | At-least-once → idempotent apply | External SoT |
| Social features | Eventual | Ranking only |
| Fraud features | Online fresh for pay; nearline for graph | Split planes |

---

## 4. Architecture Diagram

```text
 +-------------+     +------------------+     +-------------------+
 | FB Client / |---->| API Gateway/BFF  |---->| Search Service    |
 | Messenger   |     +--------+---------+     | (OpenSearch/TAO  |
 +-------------+              |               |  cache + index)   |
        |                     |               +--------+----------+
        |                     |                        ^
        |                     v                        | sync
        |            +--------+---------+     +--------+----------+
        |            | Quote Service    |     | Catalog Pipelines |
        |            | cache + revalid  |     | partner feeds     |
        |            +--------+---------+     +-------------------+
        |                     |
        |                     v
        |            +--------+---------+     +-------------------+
        |            | Partner Gateway  |---->| OTA / Hotel APIs  |
        |            | adapters, CB, RL |     +-------------------+
        |            +--------+---------+
        |                     ^
        |                     |
        v                     v
 +------+------+     +--------+---------+     +-------------------+
 | Hold Service| <-> | Booking Orch.    |---->| Payments + PSP    |
 +-------------+     | state machine    |     +-------------------+
                     +--------+---------+
                              |
              +---------------+---------------+
              v               v               v
     +--------+----+  +------+-----+  +------+------+
     | Fraud / T&S |  | Notify    |  | Itinerary   |
     | listing+pay |  | email/push |  | PDF/QR store|
     +-------------+  +------------+  +-------------+

 Partner webhooks ---> Kafka ---> Booking Updater ---> Booking OLTP
 Graph / Ads --------> Ranking features (offline/nearline)
```

**Search path:**

```text
GET /search
  -> parse geo + dates
  -> query index (filters)
  -> hydrate social features (friends_visited)
  -> apply T&S listing filters
  -> return cards with price_band (not guaranteed live)
```

**Quote → Hold → Book path:**

```text
POST /quotes -> Partner Gateway -> Quote{expires}
POST /holds  -> validate quote -> partner hold? -> Hold{TTL}
POST /bookings (Idempotency-Key)
  -> fraud score
  -> PSP authorize
  -> partner confirm booking
  -> mark CONFIRMED / compensate
  -> capture payment (policy)
  -> emit notifications + voucher
```

**Failure compensate:**

```text
if partner_fail after auth: void/refund + release hold + FAILED
if capture_fail after confirm: retry capture; finance queue; booking still CONFIRMED
if webhook CONFIRMED after local FAILED: reconcile → support queue / auto-heal if money OK
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No charge without intent ledger entry.**  
2. **No CONFIRMED without partner confirmation reference** (or explicit offline exception queue).  
3. **Idempotency-Key** makes duplicate POST /bookings safe.  
4. **Hold expiry** cannot be extended silently past partner validity.  
5. **State transitions monotonic** per booking version.  
6. **T&S block wins** over conversion optimization.

#### 5.1.2 Saga & compensation

| Step | Success | Compensate |
|------|---------|------------|
| Create intent | Persist CREATED | Mark FAILED |
| Fraud | Allow / step-up / deny | Deny → FAILED |
| Pay auth | Auth id | Void auth |
| Partner book | Partner booking id | Cancel partner reservation |
| Capture | Capture id | Refund |
| Voucher | Object written | Regenerate |

**Deal-breaker:** dual-write booking+payment without outbox/events — lost updates under crash.

#### 5.1.3 Idempotency

```text
Idempotency-Key = client-generated UUID per submit
Server stores: key -> booking_intent_id + response hash
TTL: 24–72h
Retries return same booking; never create second partner booking for same key
Partner side: send partner_idempotency_key = intent_id
```

#### 5.1.4 Partner uncertainty (timeout)

```text
Partner call timeout 5s
  -> state PARTNER_UNKNOWN
  -> poll partner + wait webhook
  -> do NOT immediately re-book (risk double reservation)
  -> user sees “confirming…”
  -> SLA: resolve < 15–60 min via reconcilers
```

**Deal-breaker:** blind retry partner book on timeout without idempotency — double bookings.

#### 5.1.5 Webhook ordering

```text
Apply if event.version > local OR event.allowed(transition)
Store raw webhook for audit
Signature verify HMAC/mTLS
```

### 5.2 Scalability

#### 5.2.1 Progressive scale

| Scale | Search | Quote | Book | Partners |
|-------|--------|-------|------|----------|
| Baseline | 1 ES cluster + Redis | In-process cache | Single region OLTP | 20 adapters |
| 10× | Sharded index; CDN details | Quote cache tier; bulk APIs | Read replicas; outbox | Pooling / CB |
| 100× | Geo index cells | Regional quote workers | Booking cells by user geo | Partner gateway mesh |
| 1,000× | Edge search approx | Predictive cache + push rates | Multi-region active-active intents | Hierarchical aggregators |

#### 5.2.2 Hot destinations

```text
“Paris in summer” search storms
  -> cache key: geo_hash × date_bucket × guests_bucket × filter_hash
  -> longer TTL on search cards; short on quotes
  -> rate-limit aggressive scrapers
  -> pre-warm top destinations
```

#### 5.2.3 Cell architecture (100×+)

```text
Cell = { booking OLTP, hold, orchestrator, local Kafka }
Route by user_id or home_region
Partner gateway may be global with regional egress IPs
Payment ledger dual-written to global finance bus
```

#### 5.2.4 Quote cache key design

```text
key = hash(property_id, room_id, check_in, check_out, guests, currency, rate_plan)
TTL 60–120s
Negative cache short TTL on 404/sold-out
Stampede: singleflight / request coalescing per key
```

### 5.3 Maintainability

#### 5.3.1 Partner adapter pattern

```text
interface PartnerAdapter {
  search(delta sync) / getProperty
  quote(req) -> Quote
  hold(req) -> HoldRef
  book(req, idemKey) -> BookRef
  cancel(ref) -> CancelRef
  mapWebhook(payload) -> CanonicalEvent
}
```

New partner = new adapter + contract tests; orchestrator unchanged.

#### 5.3.2 Schema / versioning

- Canonical booking model versioned (`booking_schema_v3`).  
- Partner payloads stored raw + mapped.  
- Feature flags for capture-on-confirm vs auth-only per market.

#### 5.3.3 Observability

| Metric | Why |
|--------|-----|
| Quote latency / error by partner | SLA |
| Book conversion funnel | Product |
| Partner unknown rate | Reliability |
| Fraud block / challenge rate | Integrity |
| Refund latency | Support |
| Search p99 | UX |
| Idempotent replay count | Client bugs |

#### 5.3.4 Trust & Safety maintainability

- Listing verification workflow (business docs, domain, photo reuse detection).  
- Shared **Integrity Feature Store** with Ads/Payments.  
- Human review queues for high-risk properties.  
- Clear severity: block book vs downrank vs label.

### 5.4 Inventory search deep dive

#### 5.4.1 Index vs live availability

Search is a **discovery index**, not a reservation system.

| Concern | Search index | Live quote |
|---------|--------------|------------|
| Freshness | Minutes–hours OK | Seconds–2 min |
| Source | Partner catalog feeds + scraped deltas | Partner availability API |
| Failure mode | Stale band / sold-out on click | Soft fail + alternates |
| Scale | Millions QPS with cache | Hundreds–thousands QPS |

**Indexing pipeline:**

```text
Partner feed (full/incremental)
  -> normalize PropertyCanonical
  -> enrichment (geo, amenities, photo refs, listing_trust)
  -> social nearline features join (friends_visited_count, group_pop)
  -> OpenSearch/TAO document upsert
  -> invalidate CDN detail keys on major edits
```

#### 5.4.2 Query planning

```text
parse(destination) -> geo_cell / place_id
filters: stars, amenities, price_band, guest capacity
must: date-aware capacity hint (coarse) OR defer sold-out to quote
rank = f(price_value, quality, distance, social, trust, LTR)
sponsored slots: separate retrieval + auction; labeled
```

**Geo:** geohash/S2 cells for “near downtown”; don’t scan worldwide then filter.

#### 5.4.3 Price bands & honesty

```text
price_band = percentile cached rates over similar stay lengths
display: “from $X” with “prices vary; confirm on next step”
metric: quote_delta_vs_band; if >20% systemic → refresh feed / partner SLA
```

**Deal-breaker:** showing a live $99 that is actually $249 without forcing re-ack — regulatory + trust.

#### 5.4.4 Hot destination storms

Pre-warm top destinations; longer TTL on SERP cards; short TTL on quotes; bot/scraper rate limits (shared with Bot Detection platform); singleflight per cache key.

### 5.5 Booking saga / 2PC-ish deep dive

#### 5.5.1 Why not classic 2PC

```text
2PC needs:
  - XA-capable resource managers
  - short lock times
  - reliable coordinator
PSP + Hotel APIs provide none of these over the public internet
→ Saga with explicit compensation is the only honest design
```

Call it “**2PC-ish**” only in the interview sense: **prepare** (hold + auth) then **commit** (partner book + capture), with **abort** compensations—not XA.

#### 5.5.2 Orchestration styles

| Style | Pros | Cons | When |
|-------|------|------|------|
| Orchestrator service | Clear state machine | Single service ownership | **MVP** |
| Choreography (events only) | Loose coupling | Harder UNKNOWN handling | Partial notify/finance |
| Temporal/Cadence workflows | Retries/timers built-in | Platform dependency | 100×+ nice-to-have |

#### 5.5.3 Step graph (canonical)

```text
1 CREATE_INTENT (idempotency reserved)
2 VALIDATE_HOLD (not expired; owned by user)
3 FRAUD_GATE (allow | challenge | deny)
4 PSP_AUTHORIZE
5 PARTNER_BOOK (idempotent key = intent_id)
6 MARK_CONFIRMED
7 PSP_CAPTURE (sync or async)
8 EMIT_OUTBOX (notify, voucher, attribution, finance)
```

Compensation reverse order on failure after step 4.

#### 5.5.4 PARTNER_UNKNOWN protocol

```text
on timeout:
  state = PARTNER_UNKNOWN
  do NOT void auth immediately (might be booked)
  do NOT re-book
  schedule: poll partner.get(idem) @ 30s, 2m, 10m...
  accept webhook with same idem
  SLA clock → escalate support + auto-decision policy:
    if partner confirms: finalize
    if partner unknown past T: void + apologize + investigate
```

#### 5.5.5 Outbox & crash safety

```text
Begin TX:
  update booking row
  insert outbox_event
Commit
Publisher: at-least-once to Kafka
Consumers: idempotent by event_id
```

**Deal-breaker:** “fire HTTP notify then update DB” — lost confirms under crash.

### 5.6 Payments deep dive

#### 5.6.1 Auth-then-capture timeline

```text
T0: authorize for quote.total (incl. taxes estimate)
T1: partner confirmed
T2: capture (full or partial if tax adjust)
Auth window: typically 7 days cards — book path must finish ≪ window
If confirm delayed past auth expiry: re-auth or fail with clear UX
```

#### 5.6.2 Ledger invariants

```text
For intent_id:
  sum(AUTH) >= sum(CAPTURE) + sum(VOID_remaining)
  sum(CAPTURE) >= sum(REFUND)
Append-only PaymentEvent; corrections = new events
```

#### 5.6.3 SCA / 3DS placement

Prefer challenge **before** partner book when risk high (avoid orphan holds). If regulation forces challenge mid-flow, extend hold TTL only if partner allows; else re-quote after SCA.

#### 5.6.4 Settlement & MoR

```text
User charged in charge_currency
Partner owed per contract (net rates / commission)
Finance batch: booking_id → payable line
Disputes: chargeback webhook → freeze itinerary flags → evidence pack
```

### 5.7 Cancellations & refunds deep dive

#### 5.7.1 Policy snapshot

At `CONFIRMED`, persist immutable `CancelPolicySnapshot` (free window, tiers, no-show). User-facing cancel UI reads snapshot only.

#### 5.7.2 Cancel saga

```text
CANCEL_REQUESTED
  -> compute refund_amount from snapshot + now()
  -> partner.cancel(idempotent)
  -> on partner OK: PSP refund (idempotent refund_id)
  -> CANCELLED
  -> if partner fail: CANCEL_UNKNOWN → reconcile (similar to book UNKNOWN)
```

#### 5.7.3 Partial / special cases

| Case | Behavior |
|------|----------|
| Partial stay used | Partner-reported; support tools; not auto full refund |
| No-show | Partner event; apply snapshot penalty |
| Partner bankrupt / force majeure | Ops playbook; goodwill credits |
| Chargeback after stay | Finance + T&S; may ban user |

**Deal-breaker:** live-fetching partner’s current policy for an old booking and reducing refund rights silently.

### 5.8 Partner APIs deep dive

#### 5.8.1 Adapter contract

```text
quote / hold / book / cancel / get / mapWebhook
Errors normalized:
  RETRYABLE_TIMEOUT | FATAL_BUSINESS | SOLD_OUT | AUTH | RATE_LIMIT
```

#### 5.8.2 Gateway policies

| Control | Setting |
|---------|---------|
| Timeout | 3–5s book; 2–3s quote |
| Retries | 0 on book/hold except orchestrator idempotent replay |
| Circuit breaker | Per partner; open → fail book closed; search degrade to cache |
| Bulkhead | Thread/pool isolation per partner |
| Egress | Regional IPs; secret rotation |
| Contract tests | Sandbox fixtures in CI |

#### 5.8.3 Webhook security & ordering

HMAC or mTLS; replay window; store raw payload; apply via versioned state machine; never trust webhook alone without signature.

#### 5.8.4 Multi-partner fanout search (optional)

Some OTAs allow meta-search; prefer **catalog sync** for SERP and **single partner** on book path for the chosen offer to avoid dual-hold hell.

### 5.9 Idempotency deep dive

#### 5.9.1 Keys at every hop

| Hop | Key |
|-----|-----|
| Client → Meta | `Idempotency-Key` header |
| Meta intent | `intent_id` (= server UUID bound to key) |
| PSP | `psp_idempotency = intent_id + op` |
| Partner | `partner_idempotency = intent_id` |
| Refund | `refund_id` |

#### 5.9.2 Store semantics

```text
IdemRecord { key, request_hash, response_body, intent_id, expires_at }
If key reuse with different body hash → 409 Conflict
TTL 24–72h (client retries); booking itself retained years
```

#### 5.9.3 Exactly-once effect

Transport is at-least-once; **effect** is exactly-once via keys + state machine guards (`CONFIRMED` ignores duplicate partner success).

### 5.10 Fraud & integrity deep dive (Meta T&S)

| Attack | Signal | Action |
|--------|--------|--------|
| Stolen cards | BIN/velocity/device | Step-up 3DS; block |
| Friendly fraud | History / dispute rate | Delay capture; review |
| Fake luxury listing | Photo reverse image; new partner | Suspend listing |
| Promo abuse | Graph clusters of accounts | Limit incentives |
| ATO | Session anomaly | Re-auth |
| Price scraping | Bot scores | Rate limit; CAPTCHA |
| Mule guest profiles | Repeated guest/PII patterns | Review / block |

**Score fusion (MVP):**

```text
risk = w1*payment_risk + w2*account_age_risk + w3*listing_trust_inv
     + w4*device_rep + w5*velocity + w6*graph_promo_cluster
if risk > block: deny
elif risk > challenge: 3DS / OTP
else: allow
```

**Listing integrity workflow:** verify business identity → payee KYC → photo cluster → dispute rate → `listing_trust`; below threshold → not bookable (stronger than downrank).

Cross-Meta: reuse **Integrity Feature Store** (device rep, account integrity) with Ads/Checkout—online features only, no Hive joins on book path.

### 5.11 Social differentiation (Meta-specific)

| Feature | Implementation |
|---------|----------------|
| Friends visited | Graph expand (privacy-checked) → feature |
| Share itinerary | Canonical URL + OG preview; ACL on guests |
| Groups recommendations | Nearline popularity in travel Groups |
| Reels destination tags | Content understanding → search query suggest |
| Ads → book attribution | Click id through to booking; conversion API |

Privacy: never leak friend identity beyond allowed edges; aggregate when needed (“12 friends interested”).

### 5.12 Failure drills (practice aloud)

| Drill | Expected system behavior |
|-------|--------------------------|
| PSP timeout after auth unknown | Retrieve Intent by idem; don’t double auth |
| Partner 500 after book accepted upstream | PARTNER_UNKNOWN; poll; no second book |
| Hold expiry during 3DS | Fail soft; re-quote; never capture |
| Kafka outage after CONFIRMED | Outbox drains later; user already has confirmation page from sync path |
| Search cluster down | Degrade to cached top destinations / partner deep links |
| Fraud model down | Rules-only; stricter on high AOV; never silent allow-all |
| Webhook storm | Partition by booking_id; backpressure; signature verify cheap first |
| Regional cell loss | Partner SoT reconcile; restore from backups + partner reports |

### 5.13 Progressive scale narrative (nested)

| Jump | Search | Quote/Hold | Book/Pay | Integrity |
|------|--------|------------|----------|-----------|
| **→10×** | SERP cache, CDN details | Singleflight quotes | Outbox + CB | Shared payment risk |
| **→100×** | Geo index cells | Regional quote workers | Booking cells by user | Fraud feature store + listing ops |
| **→1,000×** | Edge approx search | Predictive rate cache | Active-active intents + global finance bus | Cell-local T&S + hierarchical partners |

---

## 6. Wrap-Up

### 6.1 What we designed

A Meta travel marketplace path: **cached social-aware search**, **live partner quotes**, **TTL holds**, **idempotent pay-and-book saga**, **partner webhooks**, and **T&S fraud/listing integrity**—with progressive scaling that keeps browse QPS off the money path.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Stale search prices | Faster browse | Requote on detail |
| Auth-then-capture | Safer | Auth window complexity |
| Partner SoT | Correct rooms | Latency / uncertainty |
| Inline fraud | Less loss | Conversion friction |
| Saga not 2PC | Practical | Compensation code |

### 6.3 Deal-breakers (say out loud)

1. Meta Redis as sole inventory SoT.  
2. Live-quoting every search result at peak QPS.  
3. Retry partner book on timeout without idempotency.  
4. Capture payment before partner confirm (unless explicit product choice with instant refund).  
5. No fraud/listing trust layer on a money surface.  
6. Ads silently injected as organic results.  
7. Classic XA/2PC across PSP + hotel APIs.  
8. Recomputing cancel policy live after book without user notice.  
9. Fail-open “allow all payments” when fraud model is down.

### 6.4 10× / 100× / 1,000× story

- **10×:** Cache + singleflight quotes; harden saga/outbox; CDN details.  
- **100×:** Regional cells; partner gateway mesh; fraud feature store.  
- **1,000×:** Edge search; predictive rates; global finance bus; hierarchical partner aggregation.

### 6.5 Failure-drill one-liners

| Drill | One-liner |
|-------|-----------|
| Double-tap book | Idempotency-Key |
| Partner hang | PARTNER_UNKNOWN ≠ retry book |
| Auth OK, book fail | Void + release |
| Search storm | Cached bands; quote on detail |
| Fake hotel | listing_trust blocks bookability |

### 6.6 Interview closing line

> “Browse is an eventually consistent catalog with social ranking; booking is a financially correct saga against partner truth—with idempotency, compensation, and Trust & Safety as first-class dependencies.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & scope

**Q1: Why not build a full OTA?**  
A: Meta’s advantage is demand + social graph + ads; supply complexity and contracts favor partners as SoT. Building PMS/GDS is out of scope and slows MVP.

**Q2: Hotels only MVP — how do flights differ?**  
A: Flights need GDS/NDC, fare rules, ancillaries, stricter ticketing time limits; reuse saga but different adapters and hold semantics (often minutes, not 15m hotel holds).

**Q3: What must you clarify in first 5 minutes?**  
A: Supply ownership, products in MVP, hold TTL, payment responsibility, fraud bar, social features in/out, geo markets.

**Q4: Marketplace vs reseller?**  
A: Marketplace: Meta mediates; partner fulfills. Reseller: Meta merchant of record. Affects disputes, PCI, refunds—lock this with interviewer.

### 7.2 Consistency & booking correctness

**Q5: How do you prevent double booking?**  
A: Idempotent partner keys + Meta hold + never blind-retry on timeout; reconcile PARTNER_UNKNOWN; partner remains final availability SoT.

**Q6: Is the hold strongly consistent globally?**  
A: Meta hold is strongly consistent in its cell DB; cross-OTA oversell still possible; UX honesty + fast revalidation matter more than pretending global mutex.

**Q7: Outbox pattern role?**  
A: Persist booking state change + event in one DB TX; publisher pushes to Kafka for notify/finance—avoids lost messages after commit.

**Q8: What if webhook says cancelled after user checked in?**  
A: State machine guards; impossible transitions → freeze + human ops; don’t auto-refund blindly.

**Q9: Exactly-once booking?**  
A: Exactly-once *effect* via idempotency keys end-to-end; transport is at-least-once.

### 7.3 Payments

**Q10: Auth vs capture timing?**  
A: Prefer auth on submit, capture on partner confirm (or delayed capture). Balances user charge timing vs partner uncertainty.

**Q11: Partial capture / multi-room?**  
A: MVP all-or-nothing; Phase 2 line-item captures with finance ledger.

**Q12: 3DS / SCA?**  
A: Trigger on risk or regulation (EU); challenge path in orchestrator before partner book to avoid holding inventory through long challenges when possible—or hold longer.

**Q13: Refund idempotency?**  
A: refund_id keys; PSP idempotent refund; ledger append-only.

### 7.4 Search & ranking

**Q14: Why price bands on search?**  
A: Avoid partner call storms; bands from cached rates; exact on quote.

**Q15: How to use social graph safely?**  
A: Privacy-aware edges only; compute features offline/nearline; show aggregates when individual friends opt out.

**Q16: Personalization vs cold start?**  
A: Geo + price + quality priors; explore/exploit; ads separate.

**Q17: Ranking abuse (fake reviews)?**  
A: Review integrity scores; downweight new/untrusted; photo reuse detection.

### 7.5 Partners & scale

**Q18: Circuit breaker strategy?**  
A: Per-partner error rate + latency; fail open to cache for search; fail closed for book if no alternate.

**Q19: How many partner calls per booking?**  
A: Quote + hold + book (+ cancel) — budget timeouts; coalesce where APIs allow.

**Q20: Multi-region partner credentials?**  
A: Egress cells with regional secrets; don’t ship keys to every monolith replica.

**Q21: Catalog sync vs live API?**  
A: Sync for content/search; live for bookable price/availability.

### 7.6 Fraud & Trust & Safety

**Q22: Fake hotel listing attack?**  
A: Verify business identity, payment beneficiary KYC, reverse image, domain age, guest dispute rate; suspend bookability first.

**Q23: Why is travel high fraud?**  
A: High AOV, international, irreversible stays, stolen cards, mule accounts.

**Q24: Graph features for promo abuse?**  
A: Shared devices/payment instruments, invite clusters, identical itineraries — cluster detection.

**Q25: False positive management?**  
A: Soft challenges; trusted user allowlists; manual review SLA for false blocks.

**Q26: Cross-Meta signals?**  
A: Reuse account integrity, device reputation, payment risk from Ads/Checkout—via feature store, not ad-hoc DB joins in request path.

### 7.7 Reliability ops

**Q27: Disaster recovery for bookings?**  
A: Multi-AZ OLTP; backup; partner is external SoT—reconcile from partner reports after Meta outage.

**Q28: Chaos: payment succeeded, DB down before persist?**  
A: PSP webhook + idempotent intent recovery; never rely only on sync response.

**Q29: Hot key property (viral Reel)?**  
A: Cache detail; rate-limit quote; shard holds by hold_id not property_id.

### 7.8 Product & UX

**Q30: Show sold-out after search click?**  
A: Expected with cached search; smooth UX with alternates; measure quote-fail rate.

**Q31: Messenger booking?**  
A: Same APIs; thread-scoped share cards; auth via FB login.

**Q32: Calendar export?**  
A: ICS from itinerary service; not core consistency path.

### 7.9 Estimation drills

**Q33: Partner QPS if live-quoting top 10 per search at 50K search/s?**  
A: 50K×10 = 500K QPS — impossible; proves cache/viewport quoting.

**Q34: Active holds at 2M holds/day, 15 min TTL?**  
A: 2M × 15/1440 ≈ 20.8K active holds — small for Redis/OLTP.

**Q35: Storage for 5M bookings/day × 5 KB × 1 year?**  
A: 5e6×365×5e3 ≈ 9.125e12 B ≈ **9.1 TB**/year metadata — fine with cold tier.

### 7.10 Alternatives & deal-breakers

**Q36: Only use partner widget iframe?**  
A: Fastest MVP but weak Meta UX, ranking, fraud control, attribution—mention as baseline then replace money path.

**Q37: Single DB transaction across systems?**  
A: Impossible across PSP/partner — saga required.

**Q38: Eventual consistency for booking status OK?**  
A: For notify/search indexes yes; for money+confirm state, cell-local strong + explicit UNKNOWN.

### 7.11 Interview craft

**Q39: How to open?**  
A: Clarify supply, MVP product, money flow, fraud — then draw browse vs book planes.

**Q40: What impresses L5+?**  
A: Quote amplification math, PARTNER_UNKNOWN, idempotency, auth-vs-capture, T&S listing fraud, progressive cells.

**Q41: Common mistake?**  
A: Designing only Elasticsearch search and hand-waving payment/partner failures.

**Q42: Closing metrics?**  
A: Book success rate, partner unknown rate, fraud loss bps, search→book conversion, p99 quote latency.

### 7.12 Saga, idempotency & partners (extra)

**Q43: Walk the happy-path saga in 30 seconds.**  
A: Create intent under Idempotency-Key → validate hold → fraud gate → PSP auth → partner book with same idem → CONFIRMED → capture → outbox notify/voucher. Any fail after auth voids/refunds and releases hold.

**Q44: How is this “2PC-ish” without XA?**  
A: Prepare resources (hold + auth) then commit (partner book + capture); abort compensates. No distributed locks across PSP/hotel—timeouts become PARTNER_UNKNOWN with reconcile, not prepare-blocked forever.

**Q45: Client retries POST /bookings three times—what happens?**  
A: Same Idempotency-Key returns same intent/response; partner and PSP see one logical op. Different body with same key → 409.

**Q46: Partner supports hold but not idempotent book—what do you do?**  
A: Treat as high-risk adapter: stricter timeouts, single-flight per intent, reconcilers mandatory, maybe avoid that partner for Meta money path until fixed. Don’t pretend exactly-once.

**Q47: How do cancellations interact with unsettled capture?**  
A: If auth-only, void; if captured, refund; if capture in-flight, CANCEL_UNKNOWN-style reconcile. Policy snapshot still governs refundable amount.

### 7.13 Compliance, MoR & Meta T&S

**Q48: MoR vs partner-collect—what changes in the diagram?**  
A: MoR: Meta PSP + settlement + chargebacks. Partner-collect: Meta may only create reservation; payment webhooks thinner; disputes route to partner; still need listing integrity.

**Q49: What Integrity signals are Meta-specific vs generic OTA?**  
A: Social graph promo clusters, FB/IG account integrity priors, device reputation shared with ads fraud, Reels-driven traffic anomaly, Messenger share abuse—plus standard card/listing fraud.

**Q50: Give three failure drills you’d run before launch.**  
A: (1) Partner timeout after possible book—no double book. (2) PSP webhook after DB blip—intent recovers. (3) Fraud model outage—rules fail-safe, no allow-all on high AOV.

**Q51: Funnel metric that diagnoses quote amplification bugs?**  
A: `partner_quote_qps / search_qps` — if this approaches N (results per page), you’re live-quoting the SERP; fix caching/viewport quoting.

**Q52: What must never be eventually consistent?**  
A: Payment ledger effects and booking money-state transitions in the owning cell. Search bands and social badges can be eventual.

---

### Appendix A — Booking intent pseudocode

```text
def create_booking(user, hold_id, pay_ref, idem_key):
  if seen(idem_key): return prior_response
  intent = insert(CREATED, idem_key)
  hold = lock_hold(hold_id, user)
  if hold.expired: return Gone
  risk = fraud.score(user, hold, pay_ref)
  if risk.deny: return fail(intent, FRAUD)
  if risk.challenge: return challenge_response(intent)
  auth = psp.authorize(pay_ref, hold.price, idem=intent.id)
  if !auth.ok: return fail(intent, PAY)
  intent.state = PAY_AUTHORIZED
  try:
    pref = partner.book(hold.partner_ref, idem=intent.id)
    intent.state = CONFIRMED
    intent.partner_booking_id = pref
    psp.capture(auth.id, idem=intent.id)  # or async
    emit(CONFIRMED)
  except Timeout:
    intent.state = PARTNER_UNKNOWN
    enqueue_reconcile(intent)
  except PartnerFail as e:
    psp.void(auth.id)
    release_hold(hold)
    intent.state = FAILED
  store_idem(idem_key, intent)
  return intent
```

### Appendix B — Hold expiry worker

```text
every 10s:
  for hold in holds where expires_at < now and status=ACTIVE:
    status=EXPIRED
    try partner.release(hold.partner_ref)
    metric(hold_expired)
```

### Appendix C — Quote singleflight

```text
def get_quote(key, fetcher):
  if cache[key]: return cache[key]
  return coalesced_fetch(key, fetcher, ttl=90s)
```

### Appendix D — Canonical booking statuses

| Status | User-visible | Money | Partner |
|--------|--------------|-------|---------|
| CREATED | Starting | — | — |
| PAY_AUTHORIZED | Processing | Auth | — |
| PARTNER_PENDING / UNKNOWN | Confirming | Auth | In flight |
| CONFIRMED | Confirmed | Captured/pending | Booked |
| FAILED | Failed | Void/refund | None/cancelled |
| CANCELLED | Cancelled | Refunded per policy | Cancelled |

### Appendix E — Search document schema

```json
{
  "property_id": "p_123",
  "name": "Hotel Example",
  "geo": {"lat": 35.6, "lon": 139.7},
  "stars": 4,
  "price_band_usd": {"min": 120, "max": 180},
  "amenities": ["wifi", "pool"],
  "listing_trust": 0.92,
  "popularity": 0.8,
  "partner_ids": ["ota_a:555"]
}
```

### Appendix F — Partner gateway policies

```text
timeout_ms: 3000–5000
retries: 0 on book/hold (idempotent replay only by orchestrator)
retries: 2 on safe GET quote with backoff
circuit_breaker: open after 50% errors in 30s sliding
bulkhead: separate thread pools per partner
```

### Appendix G — Finance ledger events

```text
PaymentEvent { id, intent_id, type: AUTH|CAPTURE|VOID|REFUND, amount, currency, psp_ref, ts }
Invariant: sum(CAPTURE) - sum(REFUND) <= AUTH for intent
```

### Appendix H — Privacy checks for social features

```text
friends_visited(property):
  candidates = graph.friends(user) ∩ visitors(property)
  filter by visibility / interaction preference
  if count < 3: show aggregate only
  else: show up to N faces with ACL
```

### Appendix I — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Quote cache, outbox, CDN, CB |
| 100× | Regional booking cells, fraud store, partner mesh |
| 1,000× | Edge search, predictive rates, global finance |

### Appendix J — NFR card

```text
Search p99 < 500ms cached
Quote revalidate < 120s age
Book path durable + idempotent
No Meta-only inventory SoT
Auth then capture default
T&S can block book
```

### Appendix K — Cancellation policy snapshot

```text
At book time persist:
  free_cancel_until
  penalties[]
  refund_dest
Never re-read live partner policy for that booking without user notice
```

### Appendix L — Reconciliation job

```text
for intent in PARTNER_UNKNOWN and age > 2m:
  status = partner.get(idem=intent.id)
  if confirmed: finalize_confirm(intent)
  if not_found: void_and_fail(intent)
  if pending: continue until SLA then escalate
```

### Appendix M — Listing integrity signals

| Signal | Source |
|--------|--------|
| Photo cluster hash | CV pipeline |
| Business KYC | Partner onboarding |
| Bounce / chargeback | Payments |
| NLP scam phrases | Content scan |
| Geo mismatch | Maps |

### Appendix N — API error codes (book)

| Code | Meaning |
|------|---------|
| `QUOTE_EXPIRED` | Re-quote |
| `HOLD_EXPIRED` | Re-hold |
| `FRAUD_DENIED` | Block |
| `FRAUD_CHALLENGE` | Step-up |
| `PARTNER_UNAVAILABLE` | Retry later / alts |
| `PAYMENT_FAILED` | Change method |
| `IDEMPOTENT_REPLAY` | Same booking returned |

### Appendix O — Ads attribution

```text
ad_click_id -> session -> booking_id
conversion event to Ads with privacy delay / aggregated reporting as required
Do not optimize ads solely on hold creation — use CONFIRMED
```

### Appendix P — Multi-currency

```text
display_currency = user preference
charge_currency = partner/PSP supported
lock fx_rate_id on quote
settlement reports in partner currency + Meta books FX gain/loss
```

### Appendix Q — Comparison: sync book vs async confirm

| Mode | UX | Risk |
|------|----|------|
| Sync wait partner | Clear success/fail | Timeouts |
| Async confirm | Faster return | UNKNOWN state UX |
| Hybrid | Wait up to N sec then UNKNOWN | **MVP recommended** |

### Appendix R — Data retention

| Data | TTL |
|------|-----|
| Quotes | minutes |
| Holds | hours |
| Bookings | years (legal) |
| Payment events | years |
| Webhook raw | 30–90d hot; cold archive |
| Search logs | short + aggregate |

### Appendix S — 30m interview checklist

1. Clarify supply, MVP hotels, money flow, fraud.  
2. Split search vs quote vs book load.  
3. Draw gateway, saga, PSP, partner, T&S.  
4. Deep dive idempotency + PARTNER_UNKNOWN.  
5. Social features + privacy.  
6. Walk 10×/100×/1,000×.  
7. List deal-breakers.

### Appendix T — Worked example numbers

```text
Baseline: 5K search/s, 500 quote/s, 20 book/s
Quote cache 80% hit → partner quote ~100/s
20 partners uneven: top partner 40/s — OK
Book saga DB writes ~100/s including events — trivial
At 100×: 2K book/s → shard intents by user_id; partner gateway bulkheads critical
```

### Appendix U — Why not two-phase commit?

```text
PSP and Hotel APIs are not XA participants
2PC across internet partners = DEAL-BREAKER (availability, locks, timeouts)
Saga + idempotency is the industry pattern
```

### Appendix V — Glossary

| Term | Meaning |
|------|---------|
| Soft hold | Temporary reservation with TTL |
| Saga | Sequence + compensations |
| MoR | Merchant of Record |
| Price band | Approximate cached price range |
| PARTNER_UNKNOWN | Timeout ambiguity state |
| Listing trust | T&S score for property |

### Appendix W — Cell routing

```text
route(user_id) -> cell = hash(user_id) % N  // or geo home
sticky: booking_id -> cell map
cross-cell rare (admin); avoid for MVP
```

### Appendix X — Notify templates

```text
CONFIRMED: voucher link, dates, address, cancel policy
FAILED_AFTER_AUTH: money returned ETA
CANCELLED: refund amount / timeline
```

### Appendix Y — What changes at each scale (quick card)

| Scale | Browse | Money path |
|-------|--------|------------|
| 10× | Cache/CDN | Outbox + CB |
| 100× | Geo index | Booking cells |
| 1,000× | Edge approx | Active-active + global finance |

### Appendix Z — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| TAO/graph | Social signals |
| Ads | Demand + attribution |
| Meta Pay / PSP | Payments |
| Integrity/T&S | Fraud & fake listings |
| Messenger | Share / support |
| Kafka/async | Webhooks & outbox |

---

*End of Facebook Travel Booking system design.*
