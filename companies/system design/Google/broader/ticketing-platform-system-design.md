# System Design: Ticketing Platform

> **Focus areas:** Ticket inventory · Seat holds · Payment · Fairness · Flash sales · Idempotency · Anti-bot  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct hold→pay→issue lifecycle, flash-sale load shedding, deal-breakers for “check seat then update without txn” fantasies  
> **Interview theme:** Google L5+ high-contention commerce — Taylor Swift problem, fairness vs throughput, strong inventory + idempotent payments

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

Goal: **bound the product**—an event **ticketing platform** that sells scarce seats under extreme flash-sale load, with holds, payments, issuance, fairness/anti-bot controls, and multi-venue events—without double-selling seats or double-charging cards.

### 1.0 What this is / is not

| Dimension | **Ticketing platform (this doc)** | Not this |
|-----------|-----------------------------------|----------|
| Primary job | Sell scarce tickets/seats correctly under spike | Full venue ops / turnstiles hardware deep dive |
| Success | No double-sell; fair-enough access; paid ⇒ ticket | Perfect bot elimination (arms race) |
| Inventory | Seat-level or GA quantity | Infinite digital goods |
| Money | Payment intent + capture + refunds | Full banking ledger (hooks to ledger) |
| Flash sales | Queue / lottery / rate limit | Naive open hammering DB |

**Scope statement:** Design a ticketing platform: inventory, seat holds, payment, fairness, flash sales, idempotency—with progressive scale and explicit contention control.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Reserved seating or GA? | Both; reserved seat maps + GA pools | Two inventory types |
| F2 | Hold time? | 5–10 minutes through checkout | Hold TTL + sweeper |
| F3 | Payment? | Card via PSP (Stripe-like); webhook confirm | Idempotent pay↔issue |
| F4 | Flash sale? | Yes — onsale spikes 100×–10,000× | Waiting room / queue |
| F5 | Fairness? | Best-effort fair; lottery or ordered queue | Explicit fairness mode |
| F6 | Transfer / resale? | Phase 1.5; MVP issue + cancel/refund | Ticket state machine |
| F7 | Multi-event / venue? | Yes platform | `event_id` tenancy |
| F8 | Delivery? | Mobile QR / Apple Wallet PDF | Issue service |
| F9 | Promo codes / tiers? | Presale codes; VIP; price levels | Entitlement checks |
| F10 | Refunds? | Policy-based | Compensating txns |
| F11 | Fraud / bots? | Aggressive | Device, queue, CAPTCHA, purchase limits |
| F12 | Accessibility seats? | Hold-back inventory | Separate pools |

**MVP functional scope:**

1. Event/venue onboarding with seat map or GA quantity.  
2. Onsale: authenticated users enter waiting room → shopping window.  
3. Select seats / qty → hold → pay → issue tickets.  
4. Idempotent APIs; webhook-driven finalization.  
5. Cancel/refund before event per policy.  
6. Purchase limits per user/event.  
7. Admin: release holds, comp tickets, audit.  
8. Notifications: confirmation, event reminder.

**Out of MVP:**

- Full secondary marketplace (StubHub-class)  
- Dynamic pricing ML as core  
- Physical box office offline-first sync deep dive (mention)  
- Complex season subscriptions (hooks)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Inventory correctness | Never double-sell seat | Strong consistency on seat/qty |
| N2 | Payment safety | No charge without ticket path; no ticket without pay | Exactly-once business via idempotency |
| N3 | Flash availability | Survive onsale | Queue admits; backend protected |
| N4 | Hold fairness | Holds expire; no hoarding | TTL + per-user caps |
| N5 | Latency (browse map) | Interactive | p99 < 300ms seat map reads |
| N6 | Latency (hold) | Interactive | p99 < 500ms |
| N7 | Audit | Dispute-ready | Immutable sale ledger events |
| N8 | Security | Anti-bot, PCI via PSP | No raw PAN storage |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User passes queue → picks seats A12–A13 → hold 8 min → pays → QR tickets.  
2. Hold expires → seats free → another user books.  
3. Payment fails → hold remains until TTL or immediate release policy.  
4. Refund 2 days later → seats return to inventory if policy allows.  
5. GA festival: qty hold of 2 → pay → issue.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two users hold same seat | Second hold fails CAS |
| Double-click pay | Idempotency-Key → one PaymentIntent |
| Webhook before client return | Issue tickets; client poll status |
| Webhook duplicate | Idempotent handler |
| Queue abandon | Token expires; must re-queue |
| Bot farm | Device attestation + purchase limits + queue lottery |
| Partial seat selection | Atomic multi-seat hold or none |
| Price change mid-hold | Lock price on hold |
| PSP outage | Queue pause admissions; fail soft |
| Clock skew TTL | Server expiry authoritative |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Events active | 1K | 10K | 100K | 1M |
| Peak onsale users | 100K | 1M | 10M | 100M |
| Admitted shoppers | 5K | 20K | 50K | 100K+ |
| Hold QPS peak | 500 | 5K | 20K | 50K |
| Pay QPS peak | 200 | 2K | 10K | 30K |
| Seats / mega-event | 50K | 50K | 100K | stadium+ |
| Ticket issue / day | 500K | 5M | 50M | 500M |
| Inventory shards | by event | by event+section | cell | global cells |

**What each jump forces:**

- **10×:** Waiting room mandatory; inventory service per hot event; Redis+DB.  
- **100×:** Lottery/queue tokens; section sharding; PSP burst contracts.  
- **1,000×:** Regional onsale cells; static seat maps at edge; in-mem inventory leaders.

### 1.5 Etc. (Constraints & Assumptions)

- Ambiguity: **fairness definition** (FIFO queue vs lottery vs random jitter)—make explicit.  
- PSP handles PCI; we store tokens/intent ids.  
- Seat maps mostly static; inventory status dynamic.  
- Not designing full identity proofing KYC beyond anti-bot.

**Scope statement to repeat back:**

> Design a ticketing platform that protects scarce seat/GA inventory with holds, completes payment idempotently to issue tickets, survives flash onsales via waiting rooms and fairness modes, and scales by event/section partitioning—without double-sells or double-charges.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline flash | 10× | Plane |
|-------|------|----------------|-----|-------|
| **Waiting room** | Poll / WS status | 100K | 1M | Edge + queue svc |
| **Seat map reads** | Static + status overlay | 20K | 200K | CDN + status cache |
| **Holds** | Inventory mutate | 500 | 5K | Inventory leaders |
| **Payments** | PSP intents | 200 | 2K | Pay svc |
| **Webhooks** | PSP callbacks | ~pay | ×10 | Idempotent workers |
| **Issue / QR** | Ticket create | ~pay | ×10 | Issue svc |
| **Browse non-flash** | Normal | low | | Standard |

**Anti-pattern:** letting 1M users all hit hold API simultaneously.

### 2.2 Contention math

```text
Stadium 50K seats; onsale 10 minutes effective shopping for admitted
If 50K users admitted with avg 2 seats intent → intense
Single seat row hotspot: serialize via seat_id CAS or section partitions
GA counter: single Redis/DB key — use segmented counters then combine carefully OR one serial leader
```

### 2.3 Queue math

```text
Arrival 1M users in 60s
Admit rate 500 shoppers/s → 1000s to drain (~17 min) OR lottery sample 20K winners
Product choice changes architecture:
  ordered queue: fair FIFO, long wait UX
  lottery: fair random, predictable shopping cohort size
```

### 2.4 Hold memory

```text
20K active holds × 2 seats × metadata 1KB ≈ 40MB — trivial
Seat status bitset 50K seats × 2 bits ≈ 12.5KB per event — excellent for in-mem
```

### 2.5 Payment & webhook

```text
2K pays/s × webhook retry amplification 2× = 4K callbacks/s
Idempotency store must handle this; not a side SQLite
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/queue/enter` | Join waiting room for `event_id` |
| `GET /v1/queue/status` | Position / lottery result / admit token |
| `GET /v1/events/{id}/seatmap` | Static map (CDN) |
| `GET /v1/events/{id}/availability` | Section counts / bitset version |
| `POST /v1/holds` | Seats[] or GA qty + admit token + Idempotency-Key |
| `POST /v1/checkout` | Create payment for hold |
| `GET /v1/orders/{id}` | Status: held/paid/issued/failed |
| `POST /v1/orders/{id}/refund` | Policy refund |
| `POST /webhooks/psp` | Payment events |
| `GET /v1/tickets/{id}` | QR payload |

**Hold schema:**

```text
HoldRequest {
  event_id,
  mode: "SEAT"|"GA",
  seat_ids?: [],
  qty?: n,
  admit_token,
  price_tier,
  idempotency_key
}
```

### 3.2 Data model

| Entity | Key | Notes |
|--------|-----|-------|
| Event | `event_id` | onsale windows, fairness mode |
| Seat | `(event_id, seat_id)` | section, row, attributes |
| InventorySeat | `(event_id, seat_id)` | FREE/HELD/SOLD + version |
| GAPool | `(event_id, pool_id)` | remaining qty |
| Hold | `hold_id` | seats/qty, ttl, price lock, user |
| Order | `order_id` | payment_intent, status |
| Ticket | `ticket_id` | issued artifact |
| IdempotencyRecord | `(user, key)` | response snapshot |
| QueueToken | `token` | admit expiry |
| SaleEvent | append log | audit |

**Order state machine:**

```text
HOLD_CREATED → PAYMENT_PENDING → PAID → ISSUED
              ↘ HOLD_EXPIRED / CANCELED
PAID → REFUND_PENDING → REFUNDED (inventory release policy)
```

### 3.3 Flash sale admission — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Open hammering** | Simple | Melts DB | **Deal-breaker** |
| **FIFO virtual queue** | Familiar fairness | Long waits; bots hold place | Classic |
| **Lottery / random admit** | Caps shoppers; fair-ish | Anger at “luck” | **Strong for mega** |
| **Sliding window rate limit** | Easy | Not fair under bots | Supplement |
| **Pre-assigned shopping slots** | Predictable | Complex UX | Presales |

**Chosen MVP:** Waiting room + **configurable** FIFO or lottery; admit token (JWT/macaron) short-lived required on hold.

### 3.4 Inventory — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **DB row per seat txn** | Correct | Hot contention | Small events |
| **Section partition leaders** | Scales | Ops complexity | **Hot events** |
| **In-mem bitset + WAL** | Ultra fast | Failover story needed | Mega onsale |
| **GA DECR atomic** | Simple | Hot key | GA pools |
| **Soft reserve without TTL** | — | Hoarding | **Deal-breaker** |

**Chosen:**

1. Seat: conditional update `FREE→HELD` with version; multi-seat in one txn/partition.  
2. Mega-event: **section inventory service** (leader) with snapshot+log.  
3. GA: atomic counter with hold reservations table.

### 3.5 Payment & idempotency

```text
Client checkout with Idempotency-Key
  -> create Order PAYMENT_PENDING
  -> PSP CreateIntent(idempotency_key)
  -> client confirms card
  -> webhook payment_intent.succeeded
  -> transition PAID → issue tickets (idempotent)
  -> release path on fail
```

**Deal-breaker:** issuing tickets in client callback only (webhook must also finalize).

### 3.6 Fairness & anti-bot controls

| Control | Purpose |
|---------|---------|
| Queue / lottery | Cap concurrency |
| Admit token binding | user+device+event |
| Purchase limits | Per event / face-value |
| CAPTCHA / attestation | Bot friction |
| Velocity checks | Resale rings |
| Presale codes | Fan club fairness |
| Seat hold caps | Max seats held |

### 3.7 Why X over Y (summary table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Flash protection | Waiting room | Protect inventory plane | Open hold API to millions |
| Inventory SoT | Event/section service | Correctness | CDN availability as SoT |
| Multi-seat hold | Atomic all-or-nothing | UX | Partial holds silent |
| Payment finalize | Webhook + idempotency | Reliability | Client-only confirm |
| Seat map | Static CDN + status overlay | QPS | Dynamic render all SVG server-side each time |
| Fairness | Explicit mode | Product honesty | Claiming perfect fairness with open rate limits |

---

## 4. Architecture Diagram

```text
  Users ---> Edge ---> Waiting Room / Lottery Service
                         | admit_token
                         v
                   +-----+------+
                   | API Gateway|
                   +--+--+---+--+
                      |  |   |
         seatmap CDN <-+  |   +-> Checkout / Payment Service ---> PSP
                          v
                   +------+-------+
                   | Inventory    |  (per event / section leaders)
                   | Hold Manager |
                   +------+-------+
                          |
                          v
                   +------+-------+     +--------------+
                   | Orders DB    |---->| Ticket Issue |
                   | + outbox     |     +--------------+
                   +------+-------+
                          |
                          v
                   Kafka: sale.events -> Notify, Analytics, Audit
```

**Flash path:**

```text
Enter queue -> (FIFO position | lottery)
  -> when admitted: token(exp=10–15m shopping)
  -> load seatmap CDN
  -> poll availability overlay (section counts)
  -> POST hold (token required)
  -> checkout -> PSP
  -> webhook -> issue
```

**Hold path (seats):**

```text
validate admit_token + purchase_limit
BEGIN / leader apply:
  for seat in seats:
    if status!=FREE: abort
    status=HELD; hold_id; exp
  write Hold; lock prices
COMMIT
schedule expire(hold_id)
```

**Payment webhook path:**

```text
verify PSP signature
idempotency on event_id
if succeeded && order pending:
  mark PAID
  issue tickets for held seats -> SOLD
  emit TicketIssued
if failed:
  optional release hold early
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. Seat never `SOLD` to two orders.  
2. `ISSUED` tickets ⇒ `PAID` order (or admin comp with audit).  
3. Hold expiry releases seats exactly once.  
4. Idempotency keys uniquely determine checkout result.  
5. Admit token required during onsale window.  
6. Money movements audited (intent id, amounts).

#### 5.1.2 Exactly-once business logic

| Problem | Pattern |
|---------|---------|
| Double pay click | Idempotency-Key → same intent |
| Double webhook | Upsert by `psp_event_id` |
| Pay success / issue crash | Outbox / retry until ISSUED |
| Refund race | State machine guards |

#### 5.1.3 Inventory leader failover

```text
Section leader in-mem bitset
  -> WAL / Raft / commit to Spanner every N ms
On failover: reload last snapshot + replay WAL
Accept brief unavailable (fail holds) over double-sell
```

**Deal-breaker:** eventual-consistent seat status that can sell twice.

#### 5.1.4 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Hold sweeper lag | Delay queue + backup scan |
| 10× | Queue stampedes | Edge poll coalescing; WS fanout care |
| 100× | PSP rate limits | Smooth admit rate to pay capacity |
| 1,000× | Cross-region | Onsale pinned to primary region |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| `event_id` | Isolate hot onsale |
| `section_id` | Parallelize seat locks |
| Orders by `order_id` / `user_id` | Checkout store |
| Queue by `event_id` | Admission |

**Hot event cell:** dedicated inventory + queue + API pool.

#### 5.2.2 Availability overlay

```text
Don't send 50K seat statuses every poll
Send: section remaining counts + version
OR compact bitset deltas
Client paints gray sold seats from last overlay
```

#### 5.2.3 GA segmented counters (careful)

```text
Naive: one KEY remaining-- 
Hot: shard reservations into N stripes with reserved budget
OR single-threaded leader DECR (simpler correctness)
Prefer correctness over clever striping unless proven
```

#### 5.2.4 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Waiting room; event-pinned inventory; CDN maps |
| →100× | Lottery; section leaders; pay smoothing |
| →1,000× | Regional onsale cells; bitset leaders; edge queue |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
event.onsale: {
  fairness: "lottery"|"fifo",
  admit_target_concurrent: 20000,
  hold_ttl_sec: 480,
  max_tickets_per_user: 4,
  presale_codes: [...],
  accessible_pool: 200
}
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `queue_depth` | UX / rage |
| `admit_rate` | Protection |
| `hold_conflict_rate` | Contention |
| `payment_success_rate` | Funnel |
| `issue_lag_ms` | After pay |
| `double_sell_guard` (should be 0) | Integrity |
| `refund_inventory_released` | Leak |

#### 5.3.3 Testing

- Concurrent hold same seat (exactly one wins).  
- Webhook replay storms.  
- Hold expire vs pay race (define winner policy).  
- Queue token reuse / steal.  
- Chaos kill inventory leader mid-hold.

#### 5.3.4 Operability

- Kill switch: pause admits.  
- Manual comp / void.  
- Rebuild availability from orders+holds.  
- Shadow fairness modes.

---

## 6. Wrap-Up

### 6.1 What we designed

A **ticketing platform** that funnels flash demand through waiting rooms, holds seat/GA inventory under strong consistency, completes **idempotent payment→issuance**, and scales via event/section cells—not an open DB pounded by millions of browsers.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Flash | Queue/lottery before inventory |
| Inventory | Strong; leaders OK | |
| Payment | Webhook + idempotency | |
| Seat map | CDN static + overlay | |
| Fairness | Explicit product mode | |
| GA striping | Prefer simple atomicity | |

### 6.3 30-second scale narrative

> Baseline: queue + transactional holds + PSP webhooks + ticket issue. 10× dedicates hot-event inventory and CDN maps. 100× uses lottery and section leaders, smoothing admits to PSP capacity. 1,000× pins onsales to regional cells with in-mem bitsets—correctness over clever eventual inventory.

### 6.4 Deal-breakers checklist

- No waiting room on mega onsale.  
- Double-sell via non-atomic multi-seat.  
- Client-only payment finalization.  
- Holds without TTL.  
- Availability CDN as write authority.  
- Ignoring idempotency on pay/webhook.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: What does fairness mean?**  
A: Ask interviewer—FIFO vs lottery vs verified fan. Document tradeoffs.

**Q2: Reserved vs GA?**  
A: Different inventory primitives; support both.

**Q3: Transferable tickets?**  
A: State transfer with fraud controls; secondary market Phase 1.5.

**Q4: Paper tickets?**  
A: Issue PDF; still unique ticket_id barcode.

**Q5: Season tickets?**  
A: Inventory bundles; different product.

### 7.2 Inventory & concurrency

**Q6: How to hold multiple seats atomically?**  
A: Single txn / single leader apply covering all seat_ids; abort if any taken.

**Q7: Optimistic vs pessimistic?**  
A: Both OK; version CAS common; explain abort UX “seats taken.”

**Q8: Why bitsets?**  
A: Tiny, fast for stadium-scale seat state in memory.

**Q9: Hold vs cart?**  
A: Hold is inventory-grade reservation; cart may be pre-hold UI.

**Q10: Expire vs pay race?**  
A: Define: if PAID webhook arrives, re-check seats; if already free & taken by other, refund+apologize (rare) OR expiry waits for pay terminal state with grace.

### 7.3 Payments

**Q11: Why Idempotency-Key?**  
A: Network retries must not create two intents/orders.

**Q12: Auth vs capture?**  
A: Auth at checkout; capture on issue or immediate capture—product/finance.

**Q13: Partial refunds?**  
A: Per-ticket refund; release those seats if allowed.

**Q14: PCI?**  
A: PSP elements/tokenization; never store PAN.

### 7.4 Flash sales & queues

**Q15: FIFO bottlenecks?**  
A: Bots join early; need bot fight + maybe lottery.

**Q16: Lottery fairness?**  
A: Equal chance among eligible; optional weight for verified fans.

**Q17: How to size admit cohort?**  
A: Based on inventory QPS + PSP + hold TTL economics.

**Q18: WebSocket vs poll for queue?**  
A: Poll with exponential backoff at edge; WS careful with fanout.

### 7.5 Anti-bot & fraud

**Q19: Device fingerprint enough?**  
A: No; layered: queue, CAPTCHA, limits, anomaly, partner intel.

**Q20: Purchase limits bypass?**  
A: Collusion rings—graph features, payment instrument limits.

**Q21: Scalping?**  
A: Transfer delays, ID checks, official resale Phase 2.

### 7.6 Distributed systems

**Q22: Why pin onsale region?**  
A: Avoid cross-region conflict latency; replicate tickets read-only after.

**Q23: Read replicas for seat status?**  
A: OK for overlay with version lag; holds always primary/leader.

**Q24: Outbox?**  
A: Order PAID + TicketIssued events reliable to notify/analytics.

### 7.7 Estimation drills

**Q25: 1M users poll every 2s?**  
A: 500K QPS—impossible on origin; edge cache queue status by segment.

**Q26: Bitset size 100K seats?**  
A: ~12–25KB; replicate easily.

**Q27: Section shard count?**  
A: Tens of sections → tens of leaders; parallel holds.

### 7.8 Alternatives & deal-breakers

**Q28: Only Redis without WAL?**  
A: Risk of lose-state double-sell after crash—need durability story.

**Q29: SQL for everything including queue polls?**  
A: Melts; separate queue plane.

**Q30: NFT tickets?**  
A: Optional delivery; doesn’t change inventory correctness needs.

### 7.9 Interview craft

**Q31: How to open?**  
A: Seating type, flash, fairness mode, hold TTL, payment, idempotency, anti-bot.

**Q32: What impresses L5+?**  
A: Waiting room math, section leaders, pay/issue idempotency, expire races, deal-breakers.

**Q33: Common mistake?**  
A: Designing seat DB schema only; ignoring 1M waiting users.

---

### Appendix A — Seat CAS

```text
UPDATE inventory SET status='HELD', hold_id=?, exp=?, ver=ver+1
WHERE event=? AND seat=? AND status='FREE' AND ver=?
```

### Appendix B — Multi-seat hold

```text
txn:
  locks seats sorted by seat_id  # deadlock avoid
  if all FREE: mark HELD else rollback
```

### Appendix C — Lottery admit

```text
eligible = users who entered by T0
winners = sample(eligible, N)
tokens[winners] = sign(user, event, exp)
```

### Appendix D — Webhook idempotency

```text
if seen(psp_event_id): return 200
apply transition
store psp_event_id
```

### Appendix E — Issue tickets

```text
for line in order:
  ticket_id = new_id()
  qr = sign(ticket_id, event, seat)
  status SOLD
```

### Appendix F — Expire hold

```text
if order not PAID/ISSUED and now>exp:
  CAS HELD->FREE if hold_id matches
```

### Appendix G — Admit token

```text
MAC(user_id, event_id, exp, nonce)
hold API rejects missing/expired/mismatched
```

### Appendix H — Progressive scale

| Scale | Queue | Inventory | Pay |
|-------|-------|-----------|-----|
| Baseline | FIFO | DB seats | PSP |
| 10× | Edge status | Event service | burst |
| 100× | Lottery | Section leaders | smooth |
| 1,000× | Regional | Bitset Raft | multi-PSP |

### Appendix I — Order JSON

```json
{
  "order_id": "o_1",
  "event_id": "e_9",
  "status": "ISSUED",
  "seats": ["A-12", "A-13"],
  "payment_intent": "pi_123",
  "tickets": ["t_1", "t_2"]
}
```

### Appendix J — NFR card

```text
no double-sell
idempotent pay/issue
hold TTL
waiting room on flash
audit log
purchase limits
```

### Appendix K — Price lock

```text
Hold stores unit_price_cents
Checkout uses locked price
Ignore later tier changes
```

### Appendix L — Accessibility pool

```text
separate pool_id
eligible users only
don't release to general until policy time
```

### Appendix M — Refund

```text
txn:
  mark tickets VOID
  refund PSP idempotent
  if before cutoff: seats FREE
```

### Appendix N — Comparison fairness

| Mode | Fair? | Throughput control | Bot resistance |
|------|-------|--------------------|----------------|
| Open | No | No | No |
| FIFO queue | Better | Yes | Medium |
| Lottery | Good random | Yes | Better with entry caps |
| Verified fan | Policy fair | Yes | Stronger |

### Appendix O — Seatmap delivery

```text
CDN: map.json + assets (immutable version)
API: availability v={n}, sections[{id, free}]
```

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Hold | Temporary seat reservation |
| Admit token | Proof of passing waiting room |
| GA | General admission quantity pool |
| Issue | Create redeemable ticket |
| Overlay | Dynamic availability layer |

### Appendix Q — Worked flash example

```text
1M enter lottery; pick 20K winners
20K browse; 5K holds/min peak
PSP 2K pays/s capacity → admit shopping rate tuned so pay Q ≈ capacity
```

### Appendix R — Consistency

| Question | Answer |
|----------|--------|
| Overlay lag OK? | Yes seconds |
| Hold strong? | Yes |
| Ticket after pay | Durable issue retry |

### Appendix S — 30m checklist

1. Clarify seating, flash, fairness, pay, holds.  
2. Split queue vs inventory vs pay QPS.  
3. Draw waiting room → hold → PSP → issue.  
4. Deep dive CAS/leader + idempotency + expire race.  
5. Anti-bot layers.  
6. Scale story.  
7. Deal-breakers.

### Appendix T — Comp tickets

```text
admin comp: issue without pay with reason code; audit
still consumes inventory
```

### Appendix U — Presale

```text
code -> entitlement
queue separate or priority lane
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Waiting room, CDN maps |
| 100× | Lottery, section leaders |
| 1,000× | Regional cells, bitset HA |

---

*End of Ticketing Platform system design.*
