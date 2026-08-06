# System Design: Uber Eats (Food Delivery Marketplace)

> **Focus areas:** Multi-sided marketplace · City/geo cells · Order FSM · Dispatch & matching · ETA · Payments · Menu catalog · Fraud · Notifications · Peak lunch/dinner
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Locality-first; durable order+payment before cook; dispatch leases; deal-breaker = one global DB + worldwide courier search
> **Interview theme:** Microsoft loop (public-bank style) — **Uber Eats at scale**; map answers to Azure cells, Event Hubs, Cosmos/SQL, identity if interviewer steers enterprise

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

Goal: design **Uber Eats-class food delivery**—customers browse restaurants, place orders, restaurants prepare food, couriers pick up and deliver, with live tracking, payments, ratings, and city-scale peak reliability.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | End-to-end food marketplace | Single restaurant POS / kitchen IoT |
| Topology | City/region cells + global control plane | One mega-region monolith |
| Matching | Local courier ↔ order near restaurant | Worldwide courier scan per order |
| Success | Hot food on time, trust, unit economics | Raw QPS vanity metrics |
| Related | Ride-hailing shares geo/dispatch bones | Don’t paste UberX driver pool blindly |
| Microsoft angle | Cells, idempotent APIs, Event Hubs patterns | Not “host on Azure” checklist theater |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Actors? | Customer, restaurant, courier, support, ops | Separate apps + APIs + roles |
| F2 | Core flow? | Browse → cart → quote → pay → restaurant accept → prep → dispatch → pickup → deliver → tip/rate | Explicit order FSM |
| F3 | Catalog? | Menus, modifiers, hours, OOS, photos | Per-restaurant, city-scoped, CDN for media |
| F4 | Pricing? | Items + fees + tax + tip + promos + surge delivery | Durable quote pin at checkout |
| F5 | Dispatch? | Assign courier near restaurant; reassign on failure | Local matcher + leases |
| F6 | Tracking? | Live map, ETAs, status push | Location sampling + pub/sub |
| F7 | Payments? | Auth/capture policy; refunds; payouts | PSP + internal ledger |
| F8 | Search? | Restaurant/dish discovery by geo + rank | Edge cache + city index |
| F9 | Ratings? | Multi-sided reviews | Abuse / retaliation controls |
| F10 | Cancellations? | Stage-dependent policies | Compensating transactions |
| F11 | Scheduling? | ASAP + scheduled orders | Late dispatch window |
| F12 | Support? | Timeline, chat, comps | Omnichannel tools |
| F13 | Multi-city? | Launch city-by-city | Cell packaging + compliance packs |
| F14 | Group orders? | Optional / defer MVP | Cart merge complexity |

**MVP scope:**

1. City launch: restaurant onboarding (basic), menus, discovery nearby.  
2. Cart + tax/fee quote + payment authorization.  
3. Restaurant accept/reject with timers.  
4. Courier presence + local dispatch with lease.  
5. Pickup confirmation → delivery confirmation.  
6. Live status + coarse tracking.  
7. Refunds / cancel policy engine (basic).  
8. Ratings + basic fraud signals.  
9. Support order timeline.

**Out of MVP:** dark-kitchen IoT, advertising exchange, drones/robots, full loyalty OS, global single inventory, perfect multi-hop batching optimizer as day-1.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Checkout p99 (excl. PSP) | < 300–500ms |
| N2 | Restaurant notify → accept UX | Seconds; timer typically 1–5 min |
| N3 | Dispatch assign typical | < 5–15s when supply healthy |
| N4 | Location freshness | Seconds (sampled); not sub-100ms |
| N5 | Availability | 99.9%+ per city cell; degrade discovery before breaking checkout |
| N6 | Consistency | Order + money strongly consistent in home city cell |
| N7 | Privacy | Minimize location retention; GDPR/CCPA/local packs |
| N8 | Peak elasticity | Lunch/dinner 5–20× off-peak; weather/events spikes |
| N9 | Idempotency | Safe client retries on pay/order/dispatch |
| N10 | Audit | Order timeline reconstructable for disputes |

### 1.3 Cases

**Happy:** browse → order → pay auth → restaurant accept → courier assign → pickup → deliver → capture → tip → rate.

**Edges:** restaurant reject/timeout; no courier; payment fail after accept race; courier drop mid-trip; wrong address; allergy/modifier miss; weather surge; OOS after pay; double-tap checkout; tablet offline; chargeback; tourist foreign card; city cell outage; scheduled order too early/late; batching delay makes food cold; phantom “delivered”; promo abuse; courier–restaurant collusion.

| Case | Behavior |
|------|----------|
| Restaurant timeout | Auto-cancel or reassign restaurant (policy); refund/void auth |
| No courier | Expand radius / surge / wait queue; cancel with apology after SLA |
| Payment auth fail | Never cook |
| Courier disconnect | Re-lease order; preserve prep state |
| Double submit | Idempotency key → same order_id |
| OOS mid-prep | Partial fulfill / substitute / cancel+refund paths |
| Cell outage | Fail closed for that city; don’t dual-write active-active |

### 1.4 Progressive scale

| Metric | Base (1 metro) | 10× | 100× | 1,000× |
|--------|----------------|-----|------|--------|
| Cities / cells | 1–5 | 50 | 500 | 5,000+ |
| Peak orders/s (global) | 50 | 500 | 5K | 50K+ |
| Couriers online | 5K | 50K | 500K | 5M+ |
| Menu read QPS (edge) | 10K | 100K | 1M | 10M+ |
| Location updates (raw) | 5K/s | 50K/s | 500K/s | sample+agg |
| Restaurants | 2K | 20K | 200K | 2M+ |
| Jump theme | Single-city solid | Multi-city cells | Country packs + hierarchical dispatch | Geo platform OS |

**Jumps:** 10× = cell packaging + shared platform; 100× = compliance packs, multi-country payments, dispatch hierarchy; 1,000× = marketplace OS (ads, logistics platformization), extreme peak tooling.

### 1.5 Scope repeat-back

> Multi-sided food delivery with **geo/city cells**, durable order+payment, restaurant accept timers, **local dispatch with leases**, ETA/tracking with sampled locations, refunds/fraud/support—global product, local data plane. Progressive scale from one metro to thousands of cities.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Base (busy metro) | Notes |
|-------|-------------------|-------|
| Browse/search | 10K–100K QPS edge-cached | Cacheable; city shard |
| Checkout / order create | 50–200/s peak city | Must be durable |
| Restaurant tablet polls/push | Order events × restaurants | Prefer push |
| Courier location | Online × 0.2–1 Hz raw | Sample to 0.05–0.2 Hz |
| Dispatch compute | Per open order batch every few seconds | Hot path CPU |
| Notifications | 5–15× order events | Coalesce |

### 2.2 Order math

```text
City peak: 100 orders/s × 86400 ≈ theoretical 8.6M/day if sustained
Real: lunch 2h + dinner 3h dominate → e.g. 300K–1M orders/day/city at scale
Each order: ~20–80 state transitions/events → millions of events/day/city
```

### 2.3 Location bandwidth (deal-breaker trap)

```text
50K couriers × 1 Hz × 100 B ≈ 5 MB/s = 40 Mbps continuous (one city)
Global 5M × 1 Hz → absurd; MUST sample, geohash coalesce, push only deltas
Matcher needs coarse presence grids, not raw GPS firehose to every service
```

### 2.4 Storage

```text
Order row + lines: ~2–10 KB
300K orders/day × 5 KB ≈ 1.5 GB/day/city hot
Events/timeline: 5–20× → several GB/day
Menus: small relative; media in object storage + CDN
Location history: aggressive TTL (hours–days) unless dispute hold
```

### 2.5 Latency budgets

```text
Checkout: API gateway → cart validate → quote pin → order insert → pay auth → outbox
Budget excl PSP: 50+80+50+100+50 ≈ 330ms p99 target
Dispatch tick: load open orders + candidates in geocell → score → lease write < 100–300ms/tick
```

### 2.6 Bottlenecks

(1) Courier supply in geo microcells (2) restaurant accept latency (3) payment PSP (4) location firehose if unsampled (5) notification storms (6) hot restaurant / stadium events (7) not “HTTP QPS” alone.

### 2.7 Cost / unit economics (interview signal)

Labor (courier) + payment fees + promo + support dominate COGS. Software that reduces ETAs, idle miles, and cancel rate pays for itself. Don’t optimize DB CPU while burning courier wait time.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Order / Money | Order FSM, quotes, payment intents, refunds | Strong in city cell |
| Catalog / Discovery | Menus, search, rankings | Read-heavy; eventual OK |
| Dispatch / Presence | Courier availability, leases, assignment | Strong lease; presence eventual |
| Tracking / ETA | Locations, ETAs, customer map | Eventual; sampled |
| Notifications | Push/SMS/email | At-least-once; coalesce |
| Identity / Accounts | Users, roles, devices | Strong authn; global directory |
| Fraud / Trust | Risk scores, holds | Async with sync gates at pay |
| Payouts | Restaurant/courier settlements | Strong ledger; batch |

**Deal-breaker:** mixing analytics counters with order balance; or running matcher on a global unpartitioned courier table.

### 3.2 Components

1. **API Gateway / BFF** — customer, restaurant, courier apps.  
2. **Identity Service** — accounts, sessions, device attestation hooks.  
3. **Catalog Service** — restaurants, menus, modifiers, hours, OOS.  
4. **Discovery / Search** — geo + text + ranker.  
5. **Cart & Quote Service** — pin prices/fees/tax.  
6. **Order Service** — FSM source of truth.  
7. **Payment Service** — PSP orchestration + ledger entries.  
8. **Restaurant Ops Service** — accept/reject, prep timers, tablet sessions.  
9. **Presence Service** — courier online + coarse geohash.  
10. **Dispatch Service** — matching, leases, reassign.  
11. **Tracking / ETA Service** — routes, ETAs, map payloads.  
12. **Notification Service** — multi-channel, templates, coalesce.  
13. **Fraud Service** — sync score at checkout; async monitors.  
14. **Support Tools** — timeline, comps, privilege actions.  
15. **City Cell Directory** — maps lat/lng / city_id → cell.  
16. **Config / Experimentation** — fees, radii, feature flags.  
17. **Analytics / Lake** — outbox → events (non-authoritative).

### 3.3 Order state machine

```text
DRAFT → PENDING_PAYMENT → PAID_AUTHORIZED → AWAITING_RESTAURANT
  → ACCEPTED → IN_PREP → READY_FOR_PICKUP → COURIER_ASSIGNED
  → AT_RESTAURANT → PICKED_UP → EN_ROUTE → DELIVERED → COMPLETED
Cancel/Refund branches from most non-terminal states
Exception: FAILED_PAYMENT, RESTAURANT_REJECTED, UNDELIVERABLE, CHARGEBACK_HOLD
```

### 3.4 APIs (sketch)

```text
POST /v1/orders
  Idempotency-Key: <client_key>
  {restaurant_id, items[], quote_id, dropoff, tip_intent}

POST /v1/orders/{id}/restaurant/accept
POST /v1/orders/{id}/restaurant/reject

POST /v1/dispatch/leases
  {order_id, courier_id, lease_token, ttl_s}  # internal

POST /v1/couriers/presence
  {lat, lng, heading, ts, battery, status}

GET  /v1/orders/{id}/tracking
POST /v1/payments/intents
POST /v1/orders/{id}/cancel
```

### 3.5 Quote pin

Checkout freezes: item prices, modifiers, fees, tax jurisdiction, promo id, currency, delivery estimate band. Order references `quote_id`. Stale quote → refresh. Prevents “$12 UI → $18 charge” SEVs.

### 3.6 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Cell granularity | City / metro first | Match supply locality + ops |
| Pay vs cook | Auth before accept; capture policy configurable | Don’t cook free food |
| Dispatch | Continuous local matcher + exclusive lease | Avoid double assign |
| Batching couriers | Optional multi-stop with ETA cold-food cap | Economics vs quality |
| Presence store | Redis/Memorystore geohash grids | Hot, ephemeral |
| Order DB | SQL per cell (Postgres/Cloud SQL/Azure SQL) | FSM + money |
| Active-active orders | No for same order | Split-brain refunds hell |
| Menu CDN | Yes for reads | Scale browse |
| ETA model | Heuristic MVP → ML | Ship buffer honesty |
| Offline tablet | Short offline accept queue | Cap duration; sync carefully |

---

## 4. Architecture Diagram

### 4.1 Context

```text
[Customer App]──┐
[Restaurant App]┼──► Edge/CDN/BFF ──► City Cell (home for order)
[Courier App]───┘         │              │
                          │              ├─ Order + Payment + Ledger
[Global Identity]◄────────┤              ├─ Catalog replica / source
[PSP / Maps / Push]◄──────┤              ├─ Dispatch + Presence
                          │              ├─ Tracking/ETA
                          └──────────────┴─ Outbox → Event bus → Notify/Fraud/Analytics

City Directory: (geo) → cell_id
```

### 4.2 City cell internals

```text
                ┌──────── Catalog ────────┐
Browse ────────►│  Search / Rank / CDN    │
                └────────────┬────────────┘
                             ▼
Checkout ──► Quote ──► Order Service ◄──► Payment / Ledger
                │            │
                │            ▼ outbox
                │       Event Hub/Kafka
                │            │
                ▼            ├──► Notify
         Restaurant Ops      ├──► Fraud
                │            ├──► Support index
                ▼            └──► Lake
         READY_FOR_PICKUP
                │
                ▼
         Dispatch ◄──► Presence (geohash)
                │
                ▼
         Tracking/ETA ──► Customer map
```

### 4.3 Dispatch lease loop

```text
every T ms:
  open = orders in {ACCEPTED..READY..} needing courier
  for order in priority(open):
    candidates = presence.query(restaurant_geohash, radius, capacity)
    score = ETA + fairness + batch_fit + rating + reject_rate
    if try_lease(order, best, ttl):
      notify courier
      await accept/decline
```

### 4.4 Payment sequence

```text
quote_pin → create_order(PENDING_PAYMENT) → create_payment_intent
 → PSP auth → mark PAID_AUTHORIZED → outbox RestaurantNotify
 → on capture policy (delivery or accept) → CAPTURED
 → refunds as compensating ledger entries
```

### 4.5 Failure domains

```text
Global control plane down → existing city cells still take orders if configs cached
City cell DB down → that city degraded/offline; others healthy
PSP down → pause new checkouts; don’t accept new cook work without auth
Maps down → flat ETAs / last-known routes; still deliver with degraded UX
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No cook without payment authorization** (policy-enforced).  
2. Order transitions are **idempotent** and validated by FSM guards.  
3. **Exactly one courier lease** owner at a time (fencing token / version).  
4. Money movements are **ledger entries**; PSP webhooks reconciled.  
5. Outbox/events are **at-least-once**; consumers idempotent.  
6. Cancellations apply **stage policies**; never silent money loss.  
7. Support privileged actions are audited.  
8. Location stored with purpose limitation + TTL.  
9. Cell fencing: order home cell is sticky.  
10. Quote pin referenced; price integrity checks at pay.

### 5.2 Scalability playbook

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith per city OK; Postgres; Redis presence; heuristic ETA |
| 10× | Split Order/Dispatch/Catalog; cell template; shared identity; CDN menus |
| 100× | Hierarchical geo dispatch; country payment packs; menu search platform; ML ETA |
| 1000× | Multi-hop logistics platform; ads; dark stores; cell autosplit; chaos peak drills |

### 5.3 Maintainability

- FSM + policy tables as data (cancel reasons, timers).  
- Dispatch scoring plugins with shadow mode.  
- Contract tests for PSP webhooks.  
- City launch checklist as code.  
- Canary a new matcher in one geohash.  
- Feature flags for fees/surge ethics constraints.  
- Golden path load tests: lunch spike replay.

### 5.4 Progressive scale narratives

**1× (one metro):** Single cell DB; monolithic services OK; manual restaurant onboarding; radius dispatch; Stripe-like PSP; Firebase-ish push; ops Slack channel.

**10× (multi-city):** Cell packaging; city directory; config service; shared catalog pipeline; regional maps keys; on-call per region; standardized tablet app.

**100× (multi-country):** Compliance packs (tax, labor, data residency); multi-PSP; FX; localized menus; hierarchical dispatch (zone → city); fraud model per country; support language routing.

**1000× (platform):** Cells autosplit by load; marketplace ads; courier incentives OS; simulation digital twin for cities; multi-stop batching at scale; partner APIs; extreme observability + cost attribution per order.

### 5.5 Dispatch deep dive

**Problem:** Assign available couriers to orders minimizing late deliveries and idle time without double-assign.

**Lease protocol:**

```text
lease_key = order_id
value = {courier_id, token, version, exp}
Write if version == expected OR not exists (CAS)
Courier accept must present token
Expiry → order returns to open pool
```

**Scoring signals:** distance/ETA to restaurant; current load; destination alignment for batching; acceptance probability; fairness (starvation); vehicle type; restaurant handshake history.

**Batching:** only if predicted food wait < cold threshold (e.g. 4–8 min) and dropoffs cluster. Interview: name the cold-food constraint explicitly.

**Starvation:** long-waiting orders get priority boost; don’t let greedy ETA starve outer neighborhoods forever without product policy.

### 5.6 Presence & location sampling

- Heartbeat every 2–5s to presence; store geohash precision ~6–7.  
- Downstream tracking samples 0.2 Hz moving / slower idle.  
- Matcher reads grids: `geo:city:gh:courier_set`.  
- Drop accuracy under tunnels; smooth client-side; server trusts with outlier filters.  
- Privacy: customer sees courier location only after assign / pickup policy; fuzz if required.

### 5.7 ETA

```text
prep_eta = f(restaurant historical, cart size, time-of-day, load)
drive_to_rest = maps/osrm
drive_to_drop = maps/osrm
buffer = honesty buffer (weather, risk)
total = prep_ready_time + max(0, courier_to_rest - remaining_prep) + drive_to_drop + buffer
```

Show ranges early (“25–35 min”) to reduce anger; update on state changes.

### 5.8 Payments & ledger

| Concept | Role |
|---------|------|
| PaymentIntent | PSP object; auth/capture/cancel |
| LedgerEntry | Internal immutable money movement |
| Payout batch | Restaurant/courier settlements |
| Tip | Separate line; courier-bound |
| Refund | Compensating entries + PSP refund |

**Webhook handler:** verify signature; idempotent by `event_id`; drive order transitions carefully (don’t double-capture).

**Chargeback:** freeze evidence pack (timeline, GPS crumbs, photos if policy); finance workflow.

### 5.9 Catalog & OOS

- Restaurant is source for OOS toggles; propagate via pub/sub + short TTL cache.  
- Race: item OOS after quote → checkout validate fails soft with alternatives.  
- Photos/CDN; virus scan on upload.  
- Hours + holiday calendars in config; discovery filters closed restaurants.

### 5.10 Fraud & trust

Sync gates: velocity, new accounts, stolen cards, promo stacking, impossible travel.  
Async: collusion graphs (courier↔restaurant), GPS spoofing, fake deliveries.  
Actions: step-up auth, hold payout, force photo POD, ban.

### 5.11 Notifications

Order events → templates → channel preference → coalesce (don’t SMS every GPS tick). Priority: accept needed > ETA slip > marketing. Budget SMS costs.

### 5.12 Multi-region / cells

- Order sticky to `home_cell` from restaurant/city.  
- Customer traveling: browse local cell; identity global.  
- Failover: warm standby per cell; RPO minutes on events; fence old primary.  
- Avoid active-active multi-writer for same order_id.

### 5.13 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Global courier search | Latency + thundering herd + wrong locality |
| Cook before pay auth | Loss / fraud |
| No dispatch lease | Double assign SEVs |
| Unsampled GPS to Kafka forever | Cost melt + lag |
| Active-active order writes | Split-brain money |
| ETA without buffer | Trust collapse |
| Analytics DB as order source of truth | Corruption |
| Infinite batching | Cold food / refunds |

### 5.14 Microsoft / Azure mapping (optional polish)

| Concern | Azure-oriented building block |
|---------|-------------------------------|
| Cell compute | AKS / Service Fabric / App Service |
| Order DB | Azure SQL / Postgres Flexible |
| Presence | Azure Cache for Redis |
| Events | Event Hubs / Service Bus |
| Objects | Blob + CDN Front Door |
| Secrets | Key Vault |
| Identity | Entra External ID (if consumer) |
| Observability | Azure Monitor + OpenTelemetry |

Don’t let brand names substitute for invariants.

### 5.15 Lunch spike runbook

1. Pre-scale dispatch/order pods by schedule + predictive.  
2. Widen sampling / shed noncritical notifications.  
3. Increase matcher tick efficiency; cap candidate set.  
4. Surge pricing / incentives if policy allows.  
5. Pause experiments.  
6. Protect checkout SLO with load shed on browse personalization.  
7. War room: city dashboards (accept rate, assign time, ETA slip, cancel).

### 5.16 Consistency matrix

| Data | Model |
|------|-------|
| Order state / money | Strong, cell primary |
| Menu reads | Eventual + TTL |
| Courier presence | Eventual ephemeral |
| Tracking map | Eventual |
| Ratings | Eventual; moderated |
| Fraud scores | Async with sync thresholds |

### 5.17 API idempotency

`Idempotency-Key` on create order / pay / cancel. Store `(key, response)` TTL 24h. Retries return same `order_id`. Critical for mobile networks.

### 5.18 Restaurant accept timer

```text
on PAID_AUTHORIZED: start timer T
notify restaurant
if accept → ACCEPTED
if reject/timeout → cancel policy + void/refund + customer notify
optional: secondary restaurant marketplace retry (rare; usually cancel)
```

### 5.19 Undeliverable / contactless

Courier can’t find customer → call/chat → wait policy → return-to-restaurant or safe drop rules by city regulation. Document liability.

### 5.20 Observability

RED metrics on checkout/dispatch; business SLIs: % delivered on-time, assign latency p95, restaurant accept rate, cancel rate, refund rate, courier utilization. TraceId across order_id. High-cardinality caution on `restaurant_id` metrics.

---

## 6. Wrap-Up

### 6.1 Designed

City-cell food marketplace: catalog/discovery, quote-pin checkout, order FSM + payments ledger, restaurant accept, local dispatch leases, sampled presence/tracking/ETA, notifications, fraud, support—scaled by cells and progressive platformization.

### 6.2 Decisions to defend

1. Geo/city cells; no global matcher  
2. Pay auth before cook  
3. Exclusive courier leases  
4. Quote pin integrity  
5. Location sampling math  
6. Outbox/event-driven side effects  
7. FSM + policy tables  
8. Active-active avoidance for orders  
9. Cold-food cap on batching  
10. Unit economics awareness

### 6.3 Risks

- Supply/demand imbalance in micro-geos  
- PSP or maps dependency  
- Tablet offline / restaurant reliability  
- Fraud novelty  
- Peak novelty failure modes  
- Regulatory labor/data constraints

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Actors, MVP, cell topology |
| 5–12 | Estimates: orders + GPS bandwidth |
| 12–22 | Order FSM + pay + quote |
| 22–32 | Dispatch lease + presence |
| 32–40 | ETA, cancel/refund, fraud |
| 40–45 | Scale jumps, deal-breakers, closer |

### 6.5 Closer

> **Uber Eats:** local city cells, durable order+money before cook, exclusive dispatch leases, sampled location—not a firehose—honest ETAs, progressive multi-city scale, and explicit deal-breakers against global monoliths and double-assigns.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & scope

**Q: How is this different from Uber rides?**  
A: Food has restaurant prep as critical path; cold-food constraint; three-sided marketplace; catalog/menus; different cancellation economics. Geo/dispatch rhymes but scoring differs.

**Q: Why not one global database?**  
A: Locality of supply, blast radius, data residency, operational ownership, write hotspots. Browse can be edge-global; checkout/dispatch are cell-local.

**Q: MVP cut line?**  
A: One city, ASAP orders, single courier assign, basic refunds; defer group orders, ads, drones.

### 7.2 Estimation traps

**Q: What’s the first math you show?**  
A: Peak orders/s AND courier GPS MB/s if unsampled—forces architecture.

**Q: How many events per order?**  
A: Tens of FSM/notification/tracking events; plan event bus capacity.

### 7.3 Dispatch

**Q: How avoid two couriers for one order?**  
A: CAS lease with version/token; accept requires token; TTL reclaim.

**Q: What if leased courier never responds?**  
A: Lease expiry → reenter pool; optionally nack faster on app decline.

**Q: Batching two orders?**  
A: Only if restaurant proximity + dropoff cluster + cold threshold; recompute ETA.

**Q: Fairness vs ETA?**  
A: Priority score includes wait time; product policy for underserved areas.

### 7.4 Payments

**Q: Auth vs capture?**  
A: Auth at checkout; capture on deliver (or accept)—state policy; void on early cancel.

**Q: PSP webhook duplicate?**  
A: Idempotent `event_id` processing.

**Q: Partial refund after modifier miss?**  
A: Ledger compensating entry + PSP partial refund; timeline note.

### 7.5 Catalog

**Q: Menu consistency under chef toggle OOS?**  
A: Source restaurant → invalidate cache; checkout revalidates.

**Q: Search ranking signals?**  
A: Distance, ETA, rating, price, conversion, availability, personalization (careful cold start).

### 7.6 Tracking & privacy

**Q: When to show courier location?**  
A: After assignment/pickup per policy; fuzzing optional; TTL retention.

**Q: GPS spoofing?**  
A: Device signals, impossible travel, photo POD, payout holds.

### 7.7 Failure drills

**Q: City DB primary dies?**  
A: Failover to standby; fence; reconnect; some in-flight outbox replay; communicate city outage.

**Q: Dispatch service dead?**  
A: Orders can still accept/prep; queue assigns; page on-call; manual tools last resort.

**Q: Notification outage?**  
A: In-app poll; restaurant tablets poll fallback; SMS for critical path only.

### 7.8 Scale jumps

**Q: 10×?** Multi-city cell template. **100×?** Country packs + hierarchical dispatch. **1000×?** Platform logistics + autosplit cells.

### 7.9 Fraud

**Q: Promo abuse?**  
A: Device/account graphs, payment risk, velocity, unique entity constraints.

**Q: Fake delivery?**  
A: Geofence at dropoff, customer confirm, photo, courier pattern mining.

### 7.10 Product edges

**Q: Scheduled orders?**  
A: Create early; dispatch late relative to prep; don’t assign courier 3 hours early.

**Q: Group order?**  
A: Cart host + locks; single pay; defer unless interviewer insists.

**Q: Alcohol / age-restricted?**  
A: ID check workflow; courier training; regional compliance pack.

### 7.11 Microsoft-flavored follow-ups

**Q: How would you run this on Azure?**  
A: Map cells to regions/resource groups; SQL + Redis + Event Hubs; Front Door; Key Vault; still defend invariants first.

**Q: How do you design APIs for mobile flaky nets?**  
A: Idempotency keys, etags/versions, resumable uploads for photos, conflict policies.

**Q: Observability standard?**  
A: OpenTelemetry traces with `order_id` baggage; SLIs/SLOs; cell dashboards.

### 7.12 Rapid-fire answers

| Q | A |
|---|---|
| Global matcher? | No |
| Active-active order? | No |
| GPS 1Hz global Kafka? | No — sample |
| Cook before pay? | No |
| Lease? | Yes exclusive |
| Quote pin? | Yes |
| Cell unit? | City/metro |
| Cold food? | Hard constraint |
| Tablet flaky? | Short offline queue |
| Chargeback? | Evidence pack |
| Tip? | Separate ledger line |
| Surge ethics? | Policy + regulation |
| Maps down? | Degrade ETA |
| Idempotency TTL? | ~24h |
| Presence store? | Redis geohash |
| Order store? | SQL cell primary |
| Outbox? | Yes |
| Dual-write DB+bus? | Avoid |
| Search leak closed restaurant? | Filter hours/OOS |
| Ownership? | Order + Dispatch oncalls |

### 7.13 Interviewer traps (high value)

- Can two couriers pick up the same order?  
- What is durable before the restaurant starts cooking?  
- Show GPS bandwidth math.  
- What happens when lease expires mid-route?  
- How do you prevent checkout price drift?  
- Why not Cassandra for orders on day one?  
- How do you cancel after pickup?  
- What do you shed first at lunch peak?  
- How does a tourist’s payment flow?  
- How do you reprocess webhooks safely?  
- When is batching disallowed?  
- What is the blast radius of a bad matcher deploy?  
- How do you test dispatch deterministically?  
- What is your SEV definition for cold food at scale?

---

## 8. Appendices

### Appendix A — Example schemas

```sql
CREATE TABLE orders (
  order_id UUID PRIMARY KEY,
  city_id TEXT NOT NULL,
  customer_id UUID NOT NULL,
  restaurant_id UUID NOT NULL,
  state TEXT NOT NULL,
  quote_id UUID NOT NULL,
  currency CHAR(3) NOT NULL,
  dropoff_lat DOUBLE PRECISION,
  dropoff_lng DOUBLE PRECISION,
  courier_id UUID,
  lease_version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE order_items (
  order_id UUID NOT NULL,
  line_id UUID NOT NULL,
  item_id UUID NOT NULL,
  qty INT NOT NULL,
  price_cents INT NOT NULL,
  modifiers_json JSONB,
  PRIMARY KEY (order_id, line_id)
);

CREATE TABLE ledger_entries (
  entry_id UUID PRIMARY KEY,
  order_id UUID,
  party TEXT NOT NULL, -- customer|restaurant|courier|platform
  amount_cents INT NOT NULL,
  reason TEXT NOT NULL,
  psp_ref TEXT,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE idempotency_keys (
  scope TEXT NOT NULL,
  key TEXT NOT NULL,
  response_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (scope, key)
);

CREATE INDEX orders_open_dispatch ON orders (city_id, state, created_at)
  WHERE state IN ('ACCEPTED','IN_PREP','READY_FOR_PICKUP');
```

### Appendix B — Dispatch pseudocode

```python
def dispatch_tick(city):
    orders = load_open_orders(city, limit=N)
    for o in prioritize(orders):
        cands = presence.nearby(o.restaurant_geohash, r=o.radius, k=50)
        cands = filter_capacity_and_constraints(cands, o)
        if not cands:
            widen_or_surge(o)
            continue
        best = max(cands, key=lambda c: score(c, o))
        if lease.try_acquire(o.order_id, best.courier_id, ttl=15):
            notify_courier(best, o)
```

### Appendix C — Cancel / refund matrix (simplified)

| State | Customer cancel | Money |
|-------|-----------------|-------|
| PENDING_PAYMENT | Yes | No capture |
| PAID_AUTHORIZED / AWAITING_RESTAURANT | Yes | Void auth |
| ACCEPTED / IN_PREP | Policy / fee | Partial–full refund |
| PICKED_UP | Rare / support | Case-by-case |
| DELIVERED | No (dispute flow) | Chargeback/comp |

### Appendix D — City launch checklist

- [ ] Cell provisioned (DB, Redis, bus)  
- [ ] Tax/fee config  
- [ ] PSP country support  
- [ ] Maps/routing  
- [ ] Push credentials  
- [ ] Support playbooks localized  
- [ ] Fraud rules baseline  
- [ ] Restaurant supply threshold  
- [ ] Courier supply threshold  
- [ ] Dashboards + alerts  
- [ ] Load test lunch profile  
- [ ] Kill switches documented  

### Appendix E — SLIs / SLOs

| SLI | SLO example |
|-----|-------------|
| Checkout success | 99.5% excl. PSP declines |
| Auth→accept notify p95 | < 2s |
| Assign time p95 | < 15s (healthy supply) |
| On-time delivery | ≥ 85–90% within promise band |
| Double-assign rate | ~0 |
| Refund correctness | 100% ledger match |

### Appendix F — Kill switches

- Pause new orders city-wide  
- Disable promotions  
- Disable batching  
- Widen/narrow radius  
- Force photo POD  
- Shed SMS to push-only  
- Freeze matcher experiments  

### Appendix G — Narrative walkthrough (interview beats)

1. Bound marketplace + actors; reject global monolith.  
2. Estimates: orders/s + GPS bandwidth.  
3. Draw city cell + global identity/PSP.  
4. Order FSM + quote + pay durability + outbox.  
5. Dispatch lease loop + scoring.  
6. ETA + tracking privacy.  
7. Fraud, cancellations, progressive scale.  
8. Closer with deal-breakers + unit economics.

### Appendix H — Pre-onsite checklist

- [ ] Cell story  
- [ ] Order states drawn  
- [ ] Pay-before-cook  
- [ ] Dispatch lease  
- [ ] Location sampling math  
- [ ] Quote pin  
- [ ] Progressive 10×/100×/1000×  
- [ ] Deal-breakers  
- [ ] 60s closer  
- [ ] Cancel matrix  
- [ ] Lunch spike shed list  

### Appendix I — Extra drills

1. Draw FSM in 45s.  
2. GPS MB/s math aloud.  
3. Dispatch pseudocode from memory.  
4. Quote pin fields list.  
5. Cancel/refund matrix.  
6. PSP outage runbook.  
7. Fraud collusion signals.  
8. Allergy SEV narrative.  
9. Batching ETA cap rationale.  
10. Idempotency key lifecycle.  
11. Restaurant accept timer.  
12. Reassign loop.  
13. Edge browse vs cell checkout.  
14. Data residency note.  
15. Tip ledger separation.  
16. Scheduled order timing.  
17. Fairness vs ETA tension.  
18. Maps degrade mode.  
19. Support timeline sources.  
20. Compare to ride-sharing.  
21. Compare to Amazon retail.  
22. Notification coalescing.  
23. Menu CDN invalidation.  
24. Chargeback evidence pack.  
25. 1000× platform vision.  
26. Unit contribution formula.  
27. Presence heartbeat params.  
28. Outbox vs dual-write.  
29. Stadium event hotspot plan.  
30. 60s closer memorization.

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| Cell | Failure/isolation domain, usually city/metro |
| Lease | Exclusive time-bounded assignment right |
| Quote pin | Frozen price/fee snapshot |
| POD | Proof of delivery |
| OOS | Out of stock |
| Outbox | DB-transactional event publication pattern |
| Geohash | Spatial index encoding |
| SLI/SLO | Service level indicator/objective |

### Appendix K — Ownership model

| Area | Primary | Secondary |
|------|---------|-----------|
| Order FSM | Order oncall | Payments |
| Dispatch | Dispatch oncall | Presence |
| Catalog | Catalog | Discovery |
| Fraud | Trust & Safety | Payments |
| City launch | Ops eng | All of above |

### Appendix L — Sample scoring function

```text
score = w1*(-eta_to_restaurant)
      + w2*(-eta_to_dropoff_if_batched)
      + w3*acceptance_prob
      + w4*fairness_boost(wait)
      + w5*(-cancel_risk)
      + w6*batch_affinity
```

Tune via offline replay; online bandit optional at 100×.

### Appendix M — Event types (sample)

`OrderCreated`, `PaymentAuthorized`, `RestaurantNotified`, `RestaurantAccepted`, `PrepStarted`, `ReadyForPickup`, `CourierLeased`, `CourierArrivedRestaurant`, `PickedUp`, `Delivered`, `PaymentCaptured`, `Refunded`, `Cancelled`, `EtaUpdated`.

### Appendix N — Security notes

- IDOR checks on all order_id access by role.  
- Signed URLs for POD photos.  
- PII minimization in logs.  
- Partner API keys scoped per restaurant chain.  
- Rate limit accept/reject and presence posts.  
- Device integrity signals for courier apps where available.

### Appendix O — Comparison table

| System | Shared | Different |
|--------|--------|-----------|
| Uber Rides | Geo, dispatch leases | No prep; two-sided |
| DoorDash | Same category | Ops details / market |
| Amazon retail | Orders/payments | Inventory warehouses vs food ETA |
| Uber Eats ads | Marketplace | Separate auction design |

### Appendix P — 60-second closer (memorize)

> We partition by city cell so matching and money stay local. Checkout pins a quote and authorizes payment before the restaurant cooks. Dispatch grants exclusive leases to couriers from a sampled presence grid—never a global GPS firehose. ETAs include honesty buffers and cold-food caps for batching. Side effects go through outbox consumers. We scale by cloning cells, then country packs, then platformization—without ever making the order FSM active-active across regions.

### Appendix Q — Common mistakes

1. Jumping to microservices before cell story.  
2. Ignoring GPS bandwidth.  
3. No idempotency on checkout.  
4. Matcher without leases.  
5. Treating ETA as point value without uncertainty.  
6. Putting all reads/writes in one global Cosmos container “with partition key userId”.  
7. Skipping fraud until prompted.  
8. No cancel/refund thinking.  
9. Overbuilding ML day one.  
10. Forgetting restaurant as a real-time participant.

### Appendix R — Stretch: multi-stop courier

At 100×, courier may carry 2–3 orders. Model as path optimization with constraints: bag capacity, cold times, dropoff priorities. Keep lease on each order; reoptimize on delays; customer ETA updates mandatory.

### Appendix S — Stretch: marketplace incentives

Courier bonuses for undersupplied geohashes; restaurant funded delivery fee discounts; budget caps; fraud on incentive farming—needs separate ledger & controls.

### Appendix T — References to sibling prompts

- Ride-hailing system design (dispatch cousin)  
- Notification system (edge storms)  
- Payment processing (ledger cousin)  
- Proximity service (presence cousin)

---

*End of Uber Eats system design prep doc.*
