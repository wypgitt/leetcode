# System Design: Ticketing System (Events / Travel)

> **Focus areas:** Inventory · Seat holds · Checkout · Flash sales · Fairness · Waiting rooms · Payments · Issuance  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct hold→pay→issue lifecycle, inventory fencing arithmetic, flash-sale fairness knobs, deal-breakers for “SELECT seat then UPDATE” races

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

Goal: **bound a high-contention ticketing platform**—events/concerts primary, travel-shaped inventory optional—scarce seats/GA pools, time-boxed holds, checkout, flash-sale fairness—without building the entire secondary marketplace or airline PSS.

### 1.0 What this is / is not

| Dimension | **Ticketing system (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Sell scarce tickets correctly under spikes | Full StubHub resale economy |
| Success | No double-sell; paid ⇒ issued; fair-enough access | Perfect bot eradication |
| Inventory | Seat maps + GA quantity pools | Infinite digital goods |
| Money | PSP auth/capture + refunds | Full bank ledger product |
| Access | Waiting room / virtual queue | Open DB hammering |

**Scope statement:** Design a ticketing system for events (and travel-like seat inventory) with holds, checkout, flash sales, and fairness controls—progressive 10×/100×/1,000× with Amazon-style operational ownership.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Events or travel? | **Events/concerts MVP**; travel seat maps same patterns | Event + venue + performance |
| F2 | Reserved vs GA? | Both | Two inventory engines |
| F3 | Hold duration? | 5–10 minutes | TTL holds + sweeper |
| F4 | Payment? | Card via PSP; webhook confirm | Idempotent pay↔issue |
| F5 | Flash sale / onsale? | 100×–10,000× spike | Waiting room mandatory |
| F6 | Fairness? | FIFO queue and/or lottery | Explicit policy knobs |
| F7 | Seat selection? | Map UI reserved; qty GA | Atomic hold API |
| F8 | Price levels? | Sections/price types | Partition inventory |
| F9 | Presale codes? | Yes | Order of entitlement |
| F10 | Limits? | Per user/event caps | Enforce at hold & pay |
| F11 | Transfer/refund? | Policy-based Phase 1 / 1.5 | Ticket state machine |
| F12 | Delivery? | QR / wallet / PDF | Issue service |

**MVP functional scope (lock with interviewer):**

1. Promoter onboards venue + event + seat map / GA pools + prices.  
2. Onsale: users enter **waiting room** → shopping window token.  
3. Browse availability → **hold** seats/qty → checkout → **pay** → **issue**.  
4. Holds expire; inventory returns.  
5. Idempotent APIs; PSP webhooks finalize.  
6. Purchase limits; basic anti-bot (CAPTCHA, device, queue tokens).  
7. Cancel/refund before event per policy.  
8. Admin: release holds, comp tickets, audit.

**Out of MVP:**

- Full secondary marketplace deep dive  
- Dynamic pricing ML core  
- Season subscriptions / packages complexity  
- Airline interline / codeshare  
- Perfect global active-active seat writes  
- NFT tickets as primary

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Inventory correctness | Never double-sell | Strong per seat/pool shard |
| N2 | Payment safety | Ticket iff paid; no double charge | Idempotency + state machine |
| N3 | Spike survival | Onsale doesn’t melt DB | Queue admits; backends protected |
| N4 | Hold UX | Timer visible; fair expiry | Server-authoritative TTL |
| N5 | Fairness transparency | Explainable admission policy | FIFO/lottery metrics |
| N6 | Availability | Browse degraded OK; checkout correct | 99.9% issue path when admitted |
| N7 | Audit | Who held/bought/comp’d | Immutable event log |
| N8 | Latency | Hold p99 interactive | p99 < 300–500ms in-region after admit |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Queue → admit → pick seats → hold → pay → issue QR.  
2. GA: hold quantity from pool → pay → issue.  
3. Hold expires unpaid → seats free → next shopper.  
4. Presale code unlocks early window.  
5. Partial section sell-out → map shows taken; best-available API.  
6. Refund before event → void ticket barcode; inventory optionally restock.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two users hold same seat | One wins atomic fence; other fails |
| Pay succeeds, issue fails | Retry issue; ticket owed; never silent drop |
| Issue succeeds, webhook dup | Idempotent; one ticket set |
| Hold extends forever | Forbid; max extensions policy |
| Bot farm in queue | CAPTCHA, device reputation, purchase caps |
| Flash sale thundering herd | Waiting room; sticky admit tokens |
| Price change mid-hold | Freeze price in hold snapshot |
| Seat killed by production | Admin release + notify holders |
| User exceeds cap via alts | Limits + fraud graph thin; not perfect |
| PSP timeout | Uncertainty inquire; hold TTL buffer |
| Best-available race | Server allocates atomically |
| Cross-region active-active | Avoid for seat SoT; home shard |
| Lottery vs FIFO complaints | Publish policy; metrics; support macros |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Events on sale concurrent | 10 | 100 | 1K | 10K |
| Peak queue arrivals/s | 50K | 500K | 5M | 50M |
| Admits/s (shopping) | 500 | 5K | 50K | 500K |
| Hold ops/s | 1K | 10K | 100K | 1M |
| Checkout/pay QPS | 200 | 2K | 20K | 200K |
| Seats per mega-event | 100K | 100K | 100K | 100K+ |
| Ticket issue/s | 200 | 2K | 20K | 200K |
| Browse availability QPS | 10K | 100K | 1M | 10M |

**Split classes:** queue arrive ≠ admit ≠ hold ≠ pay ≠ issue ≠ browse map.

**What each jump forces:**

- **10×:** Waiting room service; seat shard by section; Redis holds + DB commit; Kafka orders.  
- **100×:** Event cells; edge queue; CQRS availability; webhook fleets.  
- **1,000×:** Global edge admission; hierarchical inventory; mega-onsale war rooms; chaos drills.

### 1.5 Etc. (Constraints & Assumptions)

- Money integer cents; hold freezes price.  
- Server time for TTL (not client).  
- Travel mode: same hold/pay/issue; inventory key = `flight_cabin_seat` or OD+train car—patterns reuse.  
- Fairness ≠ zero bots; reduce industrial resale.  
- Single-writer home for seat/pool shard.

**Scope statement:**

> Design a ticketing platform with reserved/GA inventory, TTL holds, waiting-room flash-sale admission, checkout/payment, and issuance—correct under extreme contention from baseline mega-onsales through 10× / 100× / 1,000× with sharded fencing and explicit fairness policy.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Queue arrive** | enter waiting room | 50K/s | 50M/s | Edge admission |
| **Admit** | grant shop tokens | 500/s | 500K/s | Queue controller |
| **Availability browse** | map/GA reads | 10K/s | 10M/s | CQRS cache |
| **Hold** | strong write | 1K/s | 1M/s | Inventory shards |
| **Pay** | PSP | 200/s | 200K/s | Checkout |
| **Issue** | tickets | 200/s | 200K/s | Issue svc |

### 2.2 Taylor-Swift math (mega onsale)

```text
1M users hammer at t=0
Without queue: 1M × (map poll + hold attempts) melts everything
With queue: admit 500 shoppers/s × 8 min hold window ≈ 240K concurrent shoppers max theoretical
Tune admit rate to inventory service capacity, not vanity

Inventory: 100K seats → most queue users lose; fairness about equal chance / time order
```

### 2.3 Hold storage

```text
Hold record ~200–500 B
200K concurrent holds × 500 B ≈ 100 MB — tiny
Correctness & hotspot rows dominate, not GB
```

### 2.4 Seat map payload

```text
100K seats × status byte-ish + section meta → compress; send section tiles not whole venue every time
CDN immutable geometry; only status layer dynamic
```

### 2.5 Bandwidth / CDN

Geometry static on CDN.  
Status: bloom/bitmaps or section snapshots with version.  
Clients subscribe to section versions after admit—not global 10Hz.

### 2.6 Payment & hold TTL coupling

```text
hold_ttl = 8 min
pay_uncertainty_buffer = 2 min
sweeper must not release until pay terminal OR ttl passed without pending pay
State: HELD | CHECKOUT_LOCKED | SOLD | EXPIRED
```

---

## 3. High-Level Design

### 3.1 UX surfaces

| Surface | Actor | Needs |
|---------|-------|-------|
| Fan app/web | Buyer | Queue, map, checkout, tickets |
| Promoter portal | Organizer | Event setup, onsale config |
| Box office | Staff | Comp, override, pickup |
| Support | Agents | Refunds, hold release |
| Ops war room | Platform | Onsale health, kill switches |

### 3.2 Domain model

```text
Venue(venue_id, seat_map_geometry)
Event(event_id, venue_id, start_ts)
Performance / OnsaleWindow(rules, presale, public)
Seat(seat_id, section, row, number, status FREE|HELD|SOLD|BLOCKED)
GaPool(pool_id, capacity, held, sold)
Hold(hold_id, user_id, seats[]|qty, expires_at, price_snapshot, state)
Order(order_id, hold_id, payment_id, state)
Ticket(ticket_id, order_id, seat_id|ga, barcode, state)
QueueEntry(user_id, event_id, position|lottery_score, state)
AdmitToken(token, user_id, event_id, expires_at)
```

**Order state machine:**

```text
HOLD_CREATED → CHECKOUT → PAYMENT_PENDING → PAID → ISSUED
  → CANCELLED / REFUNDED / EXPIRED_HOLD
```

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| Catalog | Events, maps, prices |
| Waiting Room | Admission fairness |
| Availability RM | Cached seat/GA views |
| Inventory | Atomic holds/sales |
| Checkout | Orchestrate pay |
| Payment | PSP adapter |
| Issue | Barcodes/wallets |
| Limits / Fraud | Caps, device, velocity |
| Admin | Comp, release, audit |
| Notification | Email/push tickets |

### 3.4 Waiting room & fairness

**Modes (pick & defend):**

1. **FIFO virtual queue** — arrival order; classic.  
2. **Lottery** — random scores; reduces bot advantage on early connect.  
3. **Hybrid** — lottery into ordered waves.

**Mechanics:**

- Edge accepts `enqueue` cheaply (token bucket / challenge).  
- Controller admits at rate `R` matching inventory/checkout capacity.  
- Admit token (signed JWT/session) required for hold APIs.  
- Heartbeat/idle expire shopping window.  
- Transparent position/ETA optional (careful with gaming).

### 3.5 Inventory: reserved seats

```text
FREE --hold--> HELD --pay--> SOLD
HELD --ttl--> FREE
SOLD --refund policy--> FREE|BLOCKED
BLOCKED: production holds / kills
```

**Atomic hold:**

```text
UPDATE seats SET status='HELD', hold_id=:h, expires=:t
WHERE seat_id IN (...) AND status='FREE';
-- affected == requested else rollback
```

Shard by `event_id + section` to reduce hot rows; mega GA pools separate.

### 3.6 Inventory: GA pools

```text
available = capacity - held - sold
atomic: if available >= qty then held += qty
```

Same hold TTL / checkout lifecycle.

### 3.7 Checkout & payments

1. Validate admit token + hold ownership + unexpired.  
2. Transition hold → `CHECKOUT_LOCKED` (pause sweeper release).  
3. Create payment intent with idempotency key = `order_id`.  
4. On PSP success / webhook → mark `PAID` → issue tickets → mark seats `SOLD`.  
5. On failure → unlock hold or expire.  
6. Uncertainty: inquire PSP; do not double-capture; do not release seats if payment possibly succeeded.

### 3.8 Flash sales / onsale controls

- Presale cohorts with codes / loyalty.  
- Announce time + queue open earlier than inventory open.  
- Kill switches: pause admits, extend holds globally, freeze map writes.  
- Best-available allocator for mobile simplicity.  
- Price tiers hard-bound in hold snapshot.

### 3.9 Anti-bot (thin but real)

- Queue tokens bound to device / login.  
- CAPTCHA on enqueue/admit.  
- Purchase caps per user/event/payment instrument.  
- Velocity on holds.  
- Not a silver bullet—say so.

### 3.10 API sketch

```text
POST /v1/events/{id}/queue/enter
GET  /v1/events/{id}/queue/status
POST /v1/events/{id}/holds              Idempotency-Key + Admit-Token
POST /v1/holds/{id}/checkout
POST /v1/orders/{id}/pay
GET  /v1/orders/{id}/tickets
POST /v1/admin/holds/{id}/release
GET  /v1/events/{id}/map/section/{sec}  (availability)
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
        Fans (spike)
            │
            ▼
     ┌──────────────┐
     │ Edge / CDN   │  static map geometry, WAF
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │ Waiting Room │  enqueue + admit rate R
     └──────┬───────┘
            ▼ admit token
     ┌──────────────┐     ┌─────────────┐
     │ API Gateway  │────▶│ Availability│──▶ cache/CDN status
     └──────┬───────┘     └─────────────┘
            ▼
     ┌──────────────┐
     │ Inventory    │  seat/GA shards
     └──────┬───────┘
            ▼
     Checkout ──▶ Payment ──▶ PSP
            │
            ▼
         Issue + Notify
            │
            ▼
         Event Bus (orders, inventory, audit)
```

### 4.2 Hold → pay → issue

```text
Client     Inventory    Checkout     Payment      PSP      Issue
  |--hold--▶|--HELD----▶|            |            |         |
  |--pay----------------▶|--lock----▶|--intent---▶|         |
  |                     |            |◀-ok/wh----|         |
  |                     |--PAID----------------------------▶|--tickets
  |◀------tickets-------|            |            |         |
```

### 4.3 Waiting room

```text
Arrive → challenge → enqueue(FIFO pos | lottery score)
Controller loop: grant next N tokens each tick
Shop: hold/pay only with valid token
Token expire → back of line or drop (policy)
```

### 4.4 Expiry sweeper

```text
sweeper:
  find HELD where expires_at < now AND state != CHECKOUT_LOCKED
  transition FREE; emit HoldExpired
checkout_locked with pay pending past max: inquire PSP then expire or issue
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Seat/GA unit in at most one HELD/SOLD** owner.  
2. **Paid ⇒ issued tickets** (async retry OK; never abandon).  
3. **Idempotent hold/checkout/pay/issue.**  
4. **Hold TTL server-side**; client timer cosmetic.  
5. **Admit token required** for mutating shopping APIs during onsale.  
6. **Price frozen** in hold.  
7. **Webhook event_id unique apply.**  
8. **Caps enforced** at hold and pay.  
9. **Single-writer shard** for seat rows / GA pool.  
10. **Integer money.**

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG seats; Redis queue; monolith |
| 10× | Waiting room fleet; section shards; Kafka |
| 100× | Event cells; edge enqueue; CQRS availability bitmaps |
| 1000× | Global edge admit; war-room automation; hierarchical GA |

**Hot section rows:** serialize holds per section partition; use batched best-available.

### 5.3 Maintainability

- Inventory property tests (no double sell)  
- Onsale replays in staging with traffic shadows  
- Support tooling: hold inspector, force release  
- Feature flags: lottery↔FIFO, admit rate, CAPTCHA strength  
- Clear promoter configs versioned  

### 5.4 Progressive scale (1× → 1000×)

**1×**

- Single region; Postgres `SELECT FOR UPDATE` holds.  
- Redis list queue.  
- Stripe-class PSP.  
- Manual war room.

**10×**

- Dedicated waiting room.  
- Seat shards by section.  
- Outbox issue; webhook workers.  
- Availability materializations.

**100×**

- Cell per mega-event.  
- Edge queue termination.  
- Bitmap/CRDT-ish status layers carefully (status cache eventual; hold strong).  
- Automated admit-rate controllers (feedback from hold p99/errors).

**1000×**

- Worldwide edge.  
- Inventory hierarchical (venue→section→seat).  
- Partner box-office offline sync Phase 2.  
- Continuous chaos for onsale day.

### 5.5 Fairness deep dive

| Policy | Pros | Cons |
|--------|------|------|
| FIFO | Intuitive | Bots early TCP win |
| Lottery | Equalizes arrival gaming | Feels random “unfair” |
| Hybrid waves | Tunable | Complex comms |

**Must measure:** bot purchase rate, time-to-admit Gini, sell-through, refund/fraud.

### 5.6 Payment uncertainty × holds

```text
if PSP unknown:
  keep CHECKOUT_LOCKED
  inquire with backoff
  if success: issue
  if fail: release
  if unknown past hard deadline: manual ops queue (rare) — never silent release if money maybe taken
```

### 5.7 Availability cache

- Cache may show FREE seat already HELD—hold API is SoT.  
- Prefer slightly stale “maybe free” over selling taken seats.  
- Versioned section snapshots; clients refetch on hold conflict.

### 5.8 Travel variant (pattern reuse)

- Inventory key: `cabin + seat` or `fare_class pool` (more airline complexity).  
- Same hold/pay/issue; add segments; GDS integration deferred.  
- Flash “sale fares” still need waiting rooms on viral routes.

### 5.9 Observability

| SLO | Signal |
|-----|--------|
| Double-sell | Must be 0 |
| Hold success p99 | capacity tuning |
| Admit utilization | queue health |
| Pay→issue latency | ticket owed time |
| Expiry correctness | sweeper lag |
| Cap breaches | fraud |

**Kill switches:** stop admits; read-only map; extend all TTLs; pause onsale.

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Read seat then write without fence | Double sell |
| No waiting room | Meltdown + unfair |
| Client TTL authority | Stolen holds |
| Release seats while PSP unknown | Money taken, no ticket / double sell |
| Active-active seat SoT | Split brain |
| Cache as SoT | Oversell |
| Infinite hold extensions | Inventory hostage |

---

## 6. Wrap-Up

### 6.1 What we designed

A high-contention ticketing system: waiting-room fairness, atomic seat/GA holds with TTL, checkout locked against premature expiry, PSP-safe pay→issue, flash-sale ops controls—and progressive sharding/cells for mega-onsales.

### 6.2 Key decisions

| Topic | Decision |
|-------|----------|
| Spike | Waiting room + admit rate |
| Inventory | Atomic fence; section shards |
| Money×hold | CHECKOUT_LOCKED + inquire |
| Fairness | Explicit FIFO/lottery knobs |
| Availability | Eventual cache; strong hold |
| Multi-region | SW seat home |

### 6.3 Risks

1. Bot industrial scale  
2. PSP uncertainty near TTL  
3. Hot section contention  
4. Fairness PR  
5. Cache false free seats (UX friction OK)  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: scarce tickets + flash sales |
| 5–15 | Waiting room fairness |
| 15–25 | Atomic holds + TTL |
| 25–35 | Pay/issue uncertainty |
| 35–45 | Scale shards, deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Holds & inventory

**Q: Why not cart without hold?**  
A: UX races; holds are the reservation.

**Q: Adjacent seats?**  
A: Transactionally hold set; best-available algorithms search contiguous.

**Q: GA oversell?**  
A: Conditional increment; same as inventory reservation.

### 7.2 Waiting room

**Q: Where is queue stored?**  
A: Redis/clusters by event; durable log optional for audit.

**Q: Disconnects?**  
A: Token/session resume; position policy explicit.

**Q: Is lottery fairer?**  
A: Against latency arms races yes; communicate clearly.

### 7.3 Payments

**Q: Ticket before capture?**  
A: Prefer paid/authorized then issue; auth hold sufficient if policy says.

**Q: Partial cart seats?**  
A: All-or-nothing hold sets MVP.

### 7.4 Flash sales

**Q: How set admit rate R?**  
A: Feedback from hold/checkout error latency; start conservative.

**Q: Presale leaks?**  
A: Code entitlements; rate limits; audit.

### 7.5 Fairness & bots

**Q: Can we eliminate bots?**  
A: No—raise cost; caps; queue; legal.

**Q: Multiple accounts?**  
A: Graph signals; payment instrument limits; imperfect.

### 7.6 Issuance

**Q: PDF vs rotating QR?**  
A: Rotating QR reduces screenshot transfer abuse.

**Q: Issue retry?**  
A: Idempotent `ticket_id`s; at-least-once until done.

### 7.7 Scale & sharding

**Q: Shard key?**  
A: `event_id` then `section_id`; GA pool id.

**Q: Cross-section transaction?**  
A: Avoid multi-shard holds; or ordered two-phase carefully—prefer same shard picks.

### 7.8 Failure injection

| Inject | Expect |
|--------|--------|
| Inventory shard down | Pause admits to that section; others live |
| Queue Redis failover | Freeze admits briefly; no seat corruption |
| PSP 5s timeout | Lock hold; inquire |
| Sweeper stopped | Alerts before inventory hostage forever |

### 7.9 Amazon-flavored probes

**Q: Customer obsession?**  
A: Transparent queue policy; don’t bait empty maps; fast ticket delivery.

**Q: Ownership?**  
A: Onsale war-room runbook with named pages.

**Q: Frugality?**  
A: CQRS bitmaps before rewriting seats into special DB day one.

### 7.10 Comparison traps

| Trap | Better |
|------|--------|
| “Like ecommerce SKU” | Seats are unique scarce rows |
| “Kafka assigns seats” | DB/atomic store fences |
| “Eventual consistency OK for sell” | No for SOLD |
| “Blockchain tickets MVP” | Unnecessary |

### 7.11 Extra traps

**Q: Extend hold on payment page?**  
A: Limited extensions; detect abuse.

**Q: Best available returns different seats on retry?**  
A: Idempotency key returns same hold.

**Q: Comp tickets vs capacity?**  
A: Comp decrements inventory via admin path with audit.

### 7.12 Progressive scale Q&A

**Q: First break?**  
A: Unqueued traffic + seat row contention.  
**Q: 100×?**  
A: Edge admit + event cells.  
**Q: 1000×?**  
A: Global edge + automated rate control + ops.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
seats(
  event_id,
  seat_id,
  section_id,
  status, -- FREE/HELD/SOLD/BLOCKED
  hold_id NULL,
  expires_at NULL,
  PRIMARY KEY(event_id, seat_id)
);

ga_pools(
  pool_id PK,
  event_id,
  capacity,
  held,
  sold
);

holds(
  hold_id PK,
  event_id,
  user_id,
  state,
  expires_at,
  price_cents,
  payload_json,
  idempotency_key UNIQUE
);

orders(
  order_id PK,
  hold_id UNIQUE,
  user_id,
  state,
  payment_id NULL,
  idempotency_key UNIQUE
);

tickets(
  ticket_id PK,
  order_id,
  event_id,
  seat_id NULL,
  pool_id NULL,
  barcode,
  state
);

queue_entries(
  event_id,
  user_id,
  score_or_pos,
  state,
  PRIMARY KEY(event_id, user_id)
);
```

### 8.2 API checklist

| API | Idempotent | Strong |
|-----|------------|--------|
| Enqueue | Yes | Durable entry |
| Hold | Yes | Yes |
| Checkout/pay | Yes | Yes |
| Issue | Yes | Yes |
| Availability | N/A | Eventual OK |

### 8.3 State transition checklist

```text
Seat: FREE→HELD→SOLD; HELD→FREE; SOLD→FREE/BLOCKED on refund/kill
Hold: CREATED→CHECKOUT_LOCKED→PAID→CLOSED; CREATED→EXPIRED
Order: PENDING→PAID→ISSUED; PENDING→FAILED
Ticket: ISSUED→VOID on refund
```

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Hold | Time-boxed reservation |
| Waiting room | Virtual queue before shopping |
| Admit token | Proof of admission |
| GA | General admission capacity pool |
| Best available | Server picks seats |
| Flash sale / onsale | Spike sale window |
| Sweeper | Expires holds |
| Fence | Atomic compare-and-set sell path |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Atomic holds, TTL, basic queue |
| 10× | Waiting room fleet, shards, webhooks |
| 100× | Event cells, edge enqueue, CQRS maps |
| 1000× | Global edge, auto admit control, chaos |

### 8.6 Hold pseudocode

```text
function hold(user, event, seats, idem, token):
  assert valid_admit(token, user, event)
  assert under_cap(user, event, seats)
  if seen(idem): return prior
  tx:
    n = fence_hold(seats, hold_id, ttl)
    if n != len(seats): rollback; CONFLICT
    write hold(price_snapshot)
  invalidate availability cache async
  return hold
```

### 8.7 Waiting room controller

```text
every tick:
  R = control_loop(error_rate, p99_hold, checkout_sat)
  grant tokens to next R entries (FIFO or by lottery score)
  expire idle shoppers
```

### 8.8 Compensation matrix

| Step | Failure | Action |
|------|---------|--------|
| Hold | Pay never starts | TTL release |
| Pay unknown | — | Lock + inquire |
| Pay fail | — | Release |
| Pay ok / issue fail | — | Retry issue |
| Refund | — | Void ticket; restock policy |

### 8.9 Onsale runbook (interview gold)

1. T-24h: load test; freeze configs.  
2. T-0 queue open: watch enqueue rate, challenge solve time.  
3. Inventory open: watch hold conflict %, pay success, issue lag.  
4. If inventory errors spike: lower R.  
5. If queue huge & inventory remains: raise R carefully.  
6. Sell-out: stop admits; drain checkouts; postmortem bots/caps.

### 8.10 Reliability / chaos drills

| Drill | Pass |
|-------|------|
| Double hold same seat | One winner |
| Webhook storm | One issue |
| Sweeper pause | Alert; no silent permanent hold without ops |
| Queue partition | No seat corruption |

### 8.11 Interview “say this” (60s)

> Ticketing is scarce inventory under flash-sale spikes. Protect with a waiting room that admits only as fast as hold/checkout can correctly run. Seats/GA use atomic fences and TTL holds; checkout locks holds during PSP uncertainty; paid always issues. Availability caches are advisory. Fairness is an explicit FIFO/lottery policy with caps—not perfect bot extinction. Shard by event/section; never multi-master seat writes.

### 8.12 Extra traps

- Selling from CDN status without fence  
- One Redis counter for all sections worldwide  
- Letting clients choose `expires_at`  
- Issuing tickets before durable PAID  

### 8.13 Related systems map

| System | Overlap |
|--------|---------|
| Online store | Checkout saga |
| Pizza shop | Reservation patterns |
| Payments | Idempotency/webhooks |
| Rate limiter | Admit/enqueue |
| Ticketmaster Meta doc | Sibling depth |

### 8.14 Estimation cheat-sheet

```text
concurrent_shoppers ≈ admit_rate × avg_shop_seconds
hold_qps ≈ shoppers × actions/s
need_shards ≈ hot_hold_qps / per_shard_capacity
```

### 8.15 Leadership mapping

| Principle | Move |
|-----------|------|
| Customer Obsession | Clear queue rules; guaranteed issue if paid |
| Ownership | Onsale war room |
| Dive Deep | Hold/pay/issue timeline |
| Frugality | Tune R before buying magic DBs |
| Earn Trust | No silent oversell |

### 8.16 Travel addendum (short)

For trains/flights: replace seat map with cabin maps / FABs; fare classes as GA-like pools; still waiting rooms on flash deals; GDS as external inventory adapter with same uncertainty rules as PSP (inquire, don’t double book).

### 8.17 Idempotency matrix

| Operation | Key | Replay result |
|-----------|-----|---------------|
| Enter queue | user+event | Same entry |
| Hold | Idempotency-Key | Same hold |
| Pay | order_id | Same payment |
| Issue | order_id | Same tickets |
| Refund | refund_key | Same refund |

### 8.18 Bitmap availability sketch

```text
section bitmap bit=1 FREE (approx)
on hold: clear bit async
on conflict: client refetch
SoT remains seat rows
```

---

*End of ticketing system design — Amazon SDE III prep artifact.*
