# System Design: Ticketmaster

> **Focus areas:** Reserved vs GA inventory · Seat holds · Waiting rooms · Payments · Flash-sale fairness · Idempotency  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct hold→pay→issue lifecycle, inventory locking arithmetic, deal-breakers for “read seat then update without fencing” fantasies  
> **Interview theme:** Meta L5+ high-contention commerce — Taylor Swift problem, queue admission, strong inventory + webhook-safe payments

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

Goal: **bound the product**—Ticketmaster-class ticketing: scarce **reserved seats** and **GA** pools, fair-enough **waiting rooms** under onsale spikes, time-boxed **holds**, **payments**, and ticket issuance—without double-selling or double-charging.

### 1.0 What this is / is not

| Dimension | **Ticketmaster (this doc)** | Not this |
|-----------|-----------------------------|----------|
| Primary job | Sell scarce tickets correctly under extreme spikes | Full venue IoT / turnstile hardware |
| Success | No double-sell; paid ⇒ issued ticket; fair-enough access | Perfect bot eradication |
| Inventory | Seat map + GA quantity pools | Infinite digital goods |
| Money | PSP intents/captures + refunds | Full bank ledger product |
| Access control | Waiting room / virtual queue | Open DB hammering |

**Scope statement:** Design Ticketmaster-like ticketing with reserved/GA inventory, holds, waiting rooms, payment, issuance—progressive scale with explicit contention control.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Reserved vs GA? | Both | Two inventory engines |
| F2 | Hold duration? | 5–10 minutes | TTL holds + sweeper |
| F3 | Payment? | Card via PSP; confirm via webhook | Idempotent pay↔issue |
| F4 | Onsale spike? | 100×–10,000× overnight | Waiting room mandatory |
| F5 | Fairness mode? | FIFO queue and/or lottery | Explicit policy knobs |
| F6 | Seat selection? | Map UI for reserved; qty for GA | Hold API atomic |
| F7 | Price levels / sections? | Yes | Inventory partitioned by section/price |
| F8 | Presale codes? | Yes | Entitlement before shopping |
| F9 | Transfer/resale? | Phase 1.5 | Ticket state machine hooks |
| F10 | Refunds/cancel? | Policy-based | Compensating transactions |
| F11 | Purchase limits? | Per user/event | Constraint at hold/pay |
| F12 | Delivery? | QR / wallet / PDF | Issue service |

**MVP functional scope:**

1. Promoter onboards venue + event + seat map / GA pools + prices.  
2. Onsale: users enter **waiting room** → receive shopping window token.  
3. Browse availability → **hold** seats/qty → checkout → **pay** → **issue**.  
4. Holds expire; inventory returns.  
5. Idempotent APIs; PSP webhook finalizes.  
6. Cancel/refund before event per policy.  
7. Anti-bot: device signals, CAPTCHA, queue tokens, purchase caps.  
8. Admin: release holds, comp tickets, audit trail.

**Out of MVP:**

- Full secondary marketplace (StubHub-class deep dive)  
- Dynamic pricing ML core  
- Season subscriptions / packages complexity  
- Offline box-office sync as primary path

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Inventory correctness | Never double-sell | Strong consistency per seat/pool shard |
| N2 | Payment safety | No silent double-charge; ticket iff paid | Idempotency keys + state machine |
| N3 | Spike survival | Onsale doesn’t melt DB | Queue admits; backends protected |
| N4 | Hold UX | Timer visible; fair expiry | TTL + server authority |
| N5 | Checkout latency | Snappy when admitted | p99 hold < 300–500ms |
| N6 | Availability | Onsale critical | Multi-AZ; degrade browse cache |
| N7 | Auditability | Who held/bought | Immutable event log |
| N8 | Abuse | Bots don’t vacuum inventory | Queue + limits + detection |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Onsale opens → waiting room → admit → pick seats → hold → pay → QR ticket.  
2. GA festival: select qty 2 → hold pool → pay → issue.  
3. Hold expires mid-checkout → user informed; seats released.  
4. Payment fails → hold remains until TTL or explicit release; no ticket.  
5. Refund → ticket voided → inventory may return (policy).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two users hold same seat | One wins atomic lock; other 409 |
| Double pay click | Idempotency → one PaymentIntent |
| Webhook before browser return | Issue still happens; UI reconciles |
| Webhook duplicate | Idempotent transition Paid→Issued |
| Waiting room abandonment | Token expires; next admitted |
| Bot farm in queue | CAPTCHA/device; purchase caps; velocity bans |
| Partial seat group (4 together) | Atomic multi-seat hold or reject |
| Clock skew on hold TTL | Server expiry only |
| PSP timeout | Query intent status; don’t double-create |
| Flash sold out | Waiting room shows sold out; no DB stampede |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Events active | 10K | 100K | 1M | 10M |
| Peak onsale arrivals/s | 50K | 500K | 5M | 50M |
| Admitted shoppers concurrent | 20K | 200K | 2M | 20M |
| Hold ops/s peak | 5K | 50K | 500K | 5M |
| Pay finalizations/s | 1K | 10K | 100K | 1M |
| Seat rows (mega venue) | 50K | 50K | 100K | 100K+ |
| Tickets issued / day | 2M | 20M | 200M | 2B |
| Waiting-room queue depth | 1M | 10M | 100M | 1B |
| Read availability QPS | 100K | 1M | 10M | 100M |

**What each jump forces:**

- **10×:** Virtual waiting room; inventory shard per event; Redis holds; CDN for event pages.  
- **100×:** Per-event cells; lottery/queue hybrid; GA counters in memory with WAL; read replicas for search.  
- **1,000×:** Global edge waiting rooms; hierarchical admission; inventory only in home cell; payments regional PSP routing.

### 1.5 Etc. (Constraints & Assumptions)

- PSP (Stripe-like) exists; we orchestrate intents/webhooks.  
- Seat maps are mostly static per event version.  
- “Fair” ≠ perfect; state the policy (FIFO vs lottery).  
- Secondary resale is a separate product surface.  
- Legal/compliance (refund laws) noted but not lawyered here.

**Scope statement to repeat back:**

> Design Ticketmaster-class ticketing: reserved and GA inventory with atomic holds, waiting-room admission under onsale spikes, idempotent payment and issuance, and progressive scale through event-sharded inventory—never optimistic “check then update” without fencing.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Waiting room** | Enqueue/heartbeat/admit | 50K/s | 500K/s | Queue service / edge |
| **Browse availability** | Seat map / GA remaining | 100K/s | 1M/s | Cache + inventory read models |
| **Hold** | Lock seats/qty | 5K/s | 50K/s | Strong inventory |
| **Pay** | Intent + webhook | 1K/s | 10K/s | Payment orchestrator |
| **Issue** | Ticket create | 1K/s | 10K/s | Ticketing DB |
| **Search/discover** | Find events | high | ×10 | Search index (separate) |

**Anti-pattern:** treating waiting-room hits as inventory writes.

### 2.2 Taylor Swift arithmetic

```text
Stadium 50_000 seats
Fans trying: 5_000_000
Spike window: first 60s → ~83_000 arrivals/s if uniform (bursty higher)

If each try hits DB for seat rows:
  5e6 × few queries → meltdown

Must: waiting room admits only ~N concurrent shoppers
  e.g. admit_target = 20_000
  hold rate manageable; rest wait with tickets-in-line UX
```

### 2.3 Hold memory

```text
Hold record ~200B
200_000 concurrent holds → ~40MB (fine)
Seat lock bitmap for 50K seats → trivial
Problem is contention + correctness, not bytes
```

### 2.4 GA counter

```text
GA pool remaining = 10_000
HOLD decr by qty under fence
Expire incr back
Naive SQL UPDATE pools SET remaining = remaining - 2 WHERE remaining >= 2
  works at moderate QPS; at 100× use in-memory/Redis Lua + durable log
```

### 2.5 Payment amplification

```text
1% of admitted complete pay (brutal onsale)
20_000 admitted × 0.01 / minute ≈ not huge
Bottleneck often inventory before payment
Still: webhooks retry storms → idempotent handlers mandatory
```

### 2.6 Sold-out read storm

```text
After sellout, 1M users refresh map
Serve cached SOLD_OUT snapshot from edge; stop consulting seat DB
```

### 2.7 Storage growth (orders, tickets, audit)

```text
Order row ~1KB; ticket ~300B; audit event ~200B
Baseline mega-onsale: 50K orders × (1KB + 2×300B + 10×200B) ≈ ~175MB hot write — fine
Year of all events: 500M tickets × 300B ≈ 150GB tickets + larger audit

10× onsales concurrent: not storage — connection + lock contention
100×: archive past events to cold store; keep hot inventory in cell memory/Redis+WAL
1,000×: per-event cell lifecycle; delete seat maps after event+chargeback window

DEAL-BREAKER: unbounded audit in primary OLTP without partitioning by event_id/time
```

### 2.8 Memory footprints (queue + seat maps)

```text
Waiting room entry ~64–128B + session
5M queued × 128B ≈ 640MB — fits Redis if single event; at 100 events × 5M → cellize

Seat map client payload:
  50K seats × 4B state bitfield ≈ 200KB compressed sections
  Naive JSON seat objects 50K × 200B = 10MB — edge cache mandatory

Hold table in Redis:
  200K holds × 200B = 40MB + seat→hold index
```

### 2.9 Partition counts

```text
Inventory: 1 shard/cell per event_id (never split seats across cells)
Kafka payments/webhooks: partitions by order_id; 64→512 as PSP QPS grows
Queue Redis: key queue:{event_id}; cluster hash tags to co-locate
Orders DB: hash(order_id) or (event_id, order_id) compound for locality
```

### 2.10 Amplification & naive cost

| Naive | Amplification | Fix |
|-------|---------------|-----|
| Every queue heartbeat updates SQL | × heartbeats | Redis only; SQL on admit |
| Map pan → SQL seat query | × pan QPS | Snapshot read model |
| Hold = N single-seat txns | × seats | One atomic multi-seat txn |
| Webhook handler non-idempotent | × PSP retries | psp_event_id unique |
| No waiting room | × fans to inventory | Admit target concurrency |

```text
5M fans × 3 availability polls/s without edge = 15M QPS → impossible
With edge TTL 1s sold-out: origin ≈ #POPs refresh rate
```

### 2.11 Payment & hold TTL interaction math

```text
hold_ttl = 8 min; median pay time = 2 min
If admit 20K and 30% reach checkout: 6K concurrent checkouts
Stripe/PSP authorizations need headroom; expire holds before capture → refund/reconcile path

Worse case: all 20K hold until TTL → inventory thrash; UX: progressive warnings
```

### 2.12 Progressive BOTE summary

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Queue arrivals/s | 80K | 800K | 8M | edge-shed |
| Admit target | 20K | 50K | per-cell | hierarchical |
| Hold QPS | 5K | 50K | 500K | cell Lua+WAL |
| Availability origin | low | cache | edge | push SOLD_OUT |
| Double-sell tolerance | **0** | **0** | **0** | **0** |

**Pitch:** “Onsale is a load-shed + atomic inventory problem. Waiting room caps concurrency; holds are strongly consistent per event cell; payments are idempotent; availability is a cached lie until hold.”

---

## 3. High-Level Design

### 3.1 APIs

| Op | Semantics |
|----|-----------|
| `POST /v1/queue/entry` | Enter waiting room for `event_id` |
| `GET /v1/queue/status` | Position / ETA / admit token |
| `POST /v1/holds` | Atomic hold seats or GA qty (requires admit token) |
| `DELETE /v1/holds/{id}` | Release early |
| `GET /v1/events/{id}/availability` | Cached map/qty |
| `POST /v1/checkouts` | Start checkout on hold |
| `POST /v1/payments` | Create PSP intent (Idempotency-Key) |
| `POST /v1/webhooks/psp` | Payment events |
| `GET /v1/orders/{id}` | Order + tickets |
| `POST /v1/orders/{id}/refunds` | Policy refund |
| `WS/SSE /v1/queue/stream` | Position updates |

### 3.2 Core schemas

```text
Event { event_id, venue_id, onsale_start, status, fairness_mode }
Section { section_id, event_id, type: RESERVED|GA }
Seat { event_id, seat_id, section_id, row, status: OPEN|HELD|SOLD }
GaPool { event_id, pool_id, remaining, total }
Hold { hold_id, user_id, event_id, expires_at, seat_ids[]|qty, state }
Order { order_id, hold_id, payment_id, state }
Ticket { ticket_id, order_id, seat_id|ga, barcode, state }
Payment { payment_id, idem_key, psp_intent, state }
QueueToken { token, event_id, user_id, admit_until }
```

**Order states:** `CREATED → AWAITING_PAYMENT → PAID → ISSUED → CANCELED/REFUNDED`

**Hold states:** `ACTIVE → CONSUMED | EXPIRED | RELEASED`

### 3.3 Inventory locking — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Optimistic check-then-update** | Simple | Double-sell races | **Deal-breaker** alone |
| **Row lock / txn per seat** | Correct | Hot row contention | Small scale reserved |
| **Conditional compare-and-set** | Correct | Need careful multi-seat | Good MVP |
| **Redis Lua atomic hold** | Fast | Durability story needed | Hot onsales |
| **Seat bitmap in memory + WAL** | Mega spikes | Complexity | 100×+ |
| **GA atomic DECR iff ≥ qty** | Perfect for pools | N/A for adjacent seats | GA |

**Chosen MVP:**

- **Reserved:** single DB transaction: lock seat rows (`WHERE status='OPEN'`) → set `HELD` + hold_id + expiry; multi-seat all-or-nothing.  
- **GA:** `UPDATE ga_pools SET remaining = remaining - :q WHERE pool_id=:p AND remaining >= :q`.  
- **10×+:** event-sharded inventory service; Redis hold + durable write-ahead for spikes.

### 3.4 Waiting room — Why X over Y

| Mode | Pros | Cons |
|------|------|------|
| **FIFO queue** | Intuitive fairness | Bots still join early; long waits |
| **Lottery** | Caps bot advantage of early join | Feels random |
| **Leaky admit** | Protects backend | Must tune rate |
| **Sticky shopping window** | Reduces churn | Hold inventory pressure |

**Chosen:** FIFO or lottery configurable per event + **leaky bucket admit rate** sized to inventory TPS capacity; admit token signed with expiry (e.g. 10–15 min shopping).

### 3.5 Payment orchestration

```text
Checkout:
  validate hold ACTIVE & owned
  create Order AWAITING_PAYMENT
  create PSP Intent with idempotency_key=order_id
  return client_secret

Webhook payment_intent.succeeded:
  transition Order → PAID (idempotent)
  issue tickets
  mark seats SOLD / GA finalize
  consume hold

Webhook failed / browser cancel:
  leave hold until TTL unless user releases
```

**Deal-breaker:** issuing tickets on client “payment success” callback without webhook/server confirmation.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Spike protection | Waiting room | Bound shoppers | Direct seat updates from world |
| Seat hold | Atomic txn / Lua | No double-sell | Check then update |
| Hold TTL | Server sweeper + lazy expiry | Prevent hoarding | Infinite holds |
| Payment | PSP + webhook idempotent | Money safety | Trust client only |
| Availability reads | Cached snapshots | Read storm | Live lock each seat on GET |
| Event isolation | Shard by event_id | Blast radius | One global seats table hotspot |

### 3.7 Consistency model

| Object | Model | Notes |
|--------|-------|-------|
| Seat/GA inventory | Strong linearizability in event cell | Double-sell = 0 |
| Hold expiry | Eventually released (bound TTL) | Lazy + sweeper |
| Availability snapshot | Eventual (seconds) | Never authoritative for purchase |
| Order/payment | Strong per order_id | Idempotent webhook apply |
| Queue position | Best-effort / rebuildable | Lottery redraw on disaster with comms |
| Ticket barcode | Strong unique | DB constraint |

**Deal-breaker:** “availability GET is strongly consistent so we don’t need holds”—browse traffic will destroy inventory.

### 3.8 API edge cases

| Case | Behavior |
|------|----------|
| Hold without admit token (onsale) | `403 NEED_QUEUE` |
| Hold expired mid-checkout | `409 HOLD_EXPIRED`; restart selection |
| Two users hold same seat | One `409 SEAT_TAKEN` |
| GA `qty > remaining` | `409 INSUFFICIENT` atomic |
| Webhook duplicate success | No-op; same tickets |
| Pay success after expire | Reconcile: refund or manual reseat policy |
| Over ticket limit / user | `403 LIMIT` |
| Sold-out event | Queue shows SOLDOUT; edge cache |
| Clock skew admit token | Server validates `exp`; reject stale |
| Partial multi-seat failure | All-or-nothing; no orphan holds |

### 3.9 Schema indexes

```text
seats: PK (event_id, seat_id); INDEX (event_id, status, section, row)
holds: PK (hold_id); UNIQUE (event_id, seat_id) WHERE active;
       INDEX (expires_at) WHERE status='ACTIVE'
ga_pools: PK (pool_id); CHECK (remaining >= 0)
orders: PK (order_id); UNIQUE (idempotency_key); INDEX (user_id, created_at)
payments: UNIQUE (psp_event_id); INDEX (order_id)
tickets: PK (ticket_id); UNIQUE (barcode); INDEX (order_id)
audit: INDEX (event_id, ts); PARTITION by day
```

### 3.10 HLD pitch (what to say)

> “Three planes: waiting room (shed), inventory (strong per event_id cell), money (idempotent PSP). Browse is cached and wrong by design; truth is the hold. GA is atomic DECR; reserved is multi-seat all-or-nothing. Tickets only after PAID webhook. Scale by cellizing hot events, not by optimistic UI locks.”

---

## 4. Architecture Diagram

```text
                         +------------------------+
   Users --------------> | Edge / CDN / WAF       |
                         | static event pages     |
                         +-----------+------------+
                                     |
                                     v
                         +-----------+------------+
                         | API Gateway + Auth     |
                         +-----------+------------+
                                     |
         +---------------------------+-----------------------------+
         |                           |                             |
         v                           v                             v
 +----------------+        +------------------+          +------------------+
 | Waiting Room   |        | Catalog / Browse |          | Checkout / Pay   |
 | Queue service  |        | availability     |          | Order service    |
 | admit tokens   |        | cache            |          | PSP adapter      |
 +--------+-------+        +--------+---------+          +--------+---------+
          |                         |                             |
          | admit                   | read model                  | intents
          v                         v                             v
 +----------------+        +------------------+          +------------------+
 | Queue store    |        | Availability     |          | PSP (external)   |
 | Redis lists/   |        | snapshots        |          | webhooks ------+ |
 | lottery bags   |        +--------+---------+          +----------------+ |
 +----------------+                 ^                                      |
                                    | invalidate                           |
                                    |                                      v
                           +--------+---------+                   +--------+--------+
                           | Inventory Svc    |<---- holds -------| Hold Manager    |
                           | event-sharded    |                   | TTL / sweeper   |
                           | seats + GA       |                   +--------+--------+
                           +--------+---------+                            |
                                    |                                      |
                                    v                                      v
                           +--------+---------+                   +--------+--------+
                           | Inventory DB /   |                   | Orders + Tickets|
                           | Redis+WAL        |                   | durable store   |
                           +------------------+                   +--------+--------+
                                                                       |
                                                                       v
                                                              +--------+--------+
                                                              | Issue / Barcode |
                                                              | Notify (email)  |
                                                              +-----------------+

   Admin / Promoter console ---> Event config + seat maps + onsale controls
   Anti-bot / Device graph -----> Queue entry + purchase attempts
```

**Onsale path:**

```text
POST /queue/entry
  -> anti-bot score
  -> enqueue (FIFO) or lottery ticket
  -> heartbeat while waiting
  -> admit when capacity slot free
  -> signed admit_token {event_id, user_id, exp}
```

**Hold path:**

```text
POST /holds (admit_token, seats|qty)
  -> verify token
  -> enforce purchase limits
  -> inventory.atomic_hold
  -> return hold_id + expires_at
```

**Pay + issue:**

```text
POST /payments (order_id, idem_key)
  -> PSP intent
Webhook succeeded
  -> PAID + issue tickets + SOLD
  -> async email/wallet push
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **A seat is in at most one of OPEN / HELD / SOLD** (GA: remaining never negative).  
2. **Hold expiry eventually returns inventory** (lazy + active sweeper).  
3. **Tickets issued only from PAID orders.**  
4. **Idempotency keys** make payment & issue safe under retries.  
5. **Admit token required** for hold during onsale mode.  
6. **Audit log** for hold/pay/issue/refund.

#### 5.1.2 Data loss

| Component | Durability |
|-----------|------------|
| Inventory transitions | DB txn or Redis+WAL replay |
| Orders/payments | Multi-AZ SQL |
| Queue positions | Redis OK if rebuildable; accept re-lottery on disaster with comms |
| Tickets | Durable; barcodes unique constrained |

**Deal-breaker:** Redis-only seats with no recovery story for SOLD.

#### 5.1.3 Idempotency matrix

| API | Key | Effect |
|-----|-----|--------|
| Create hold | `Idempotency-Key` or client hold key | Same hold returned |
| Create payment | `order_id` | One PSP intent |
| Webhook | `psp_event_id` | Exactly-once business apply |
| Issue | `order_id` | One ticket set |

#### 5.1.4 Retry & reconciliation

```text
Browser loses connection after pay:
  GET /orders/{id} reconciles from PSP intent status
Cron reconciler:
  PAID without tickets → issue
  Intent succeeded but order AWAITING → transition
  ACTIVE holds past TTL → release
```

#### 5.1.5 Rate limits

| Limit | Where |
|-------|-------|
| Queue entry / device / IP | Waiting room |
| Holds / user / event | Inventory |
| Payment attempts / order | Pay |
| Availability GET | Edge (cheap) |

#### 5.1.6 Failure modes by scale

| Scale | Failure | Mitigation |
|-------|---------|------------|
| Baseline | Double-click pay | Idempotency keys |
| 10× | Sweeper lag → ghost holds | Lazy expiry on touch + indexed sweeper |
| 100× | Inventory primary failover mid-hold | Fenced leader; WAL replay; reject split-brain |
| 1,000× | Edge queue vs origin desync | Signed admit from authoritative issuer; short TTL |

#### 5.1.7 Retries & backoff

```text
Hold 409 SEAT_TAKEN → client picks new seats (no blind retry same ids)
PSP create intent network fail → retry same idempotency_key
Webhook 5xx → PSP exponential retry; handler must be idempotent
Availability 503 → serve last SOLD_OUT/edge stale
```

#### 5.1.8 Data-loss prevention

1. SOLD transitions durable before ticket issue ACK.  
2. Redis inventory requires WAL/snapshot + rebuild from audit for SOLD.  
3. Never delete payment rows; soft-state refunds.  
4. Barcode uniqueness enforced in DB.  
5. Queue loss ≠ inventory loss (comms + lottery redraw OK).

#### 5.1.9 Consistency under partition

```text
Two inventory replicas accepting holds → DOUBLE SELL risk → single leader per event cell
Checkout cannot talk to inventory: fail closed (no optimistic sell)
Waiting room partitioned: pause admits rather than open floodgates
```

**Deal-breaker:** multi-master seat rows with last-write-wins.

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Jump | Change |
|------|--------|
| Baseline | SQL seats + GA; Redis queue; PSP; one region |
| **10×** | Event shard; availability cache; signed admit tokens; webhook workers |
| **100×** | Inventory cell per hot event; Redis Lua holds + WAL; lottery mode; WS queue status |
| **1,000×** | Edge waiting rooms; home inventory cell; hierarchical admit; archive past events |

#### 5.2.2 Sharding key

```text
Primary: event_id → inventory cell
Users global; orders by order_id with event_id secondary
Never shard seat hold across cells for one event
```

#### 5.2.3 Adjacent seats / best available

```text
Algorithm: precompute blocks or scan row runs of OPEN seats length >= qty
Hold atomically all ids in one txn
At 100×: maintain interval trees / free-run indexes per row in memory
```

#### 5.2.4 Waiting room implementation

**FIFO:**

```text
Redis list or stream per event
position ≈ queue_index - admitted_index
admit rate R/s controlled by inventory health + target concurrency
```

**Lottery:**

```text
Users register interest before T0
At T0 assign random ranks / draw batches
Reduces early-bot advantage
```

#### 5.2.5 Availability read model

```text
Push snapshots every 1–5s during onsale:
  section fill %; GA remaining; seat bitmaps coarse
Clients do not lock on browse
Exact truth only at hold time
```

**Deal-breaker:** generating full seat JSON from DB on every map pan at 1M QPS.

#### 5.2.6 Multi-section GA + reserved hybrid

Many events mix VIP reserved + GA pit. Treat each pool as separate inventory partition under same `event_id` cell; checkout can include multiple holds linked to one order (single txn across partitions in-cell).

#### 5.2.7 Hot-key handling

| Hot key | Fix |
|---------|-----|
| Single `event_id` row for GA | Counter in Redis Lua / memory; not one SQL row hotspot without care |
| Popular section | Partition free-run indexes by section |
| Global `orders` sequence | UUIDs / snowflake; no global autoincrement bottleneck |
| Queue key | Already per-event; OK |

#### 5.2.8 Cache hierarchy

```text
Edge: event page, SOLD_OUT banner, coarse availability
API memory: admit rate config, shopping rules
Redis: queue, holds, GA counters (optional), session
Inventory primary: seat truth
CDN: static maps/assets — not personalized holds
```

#### 5.2.9 Queue backpressure

```text
If hold_success_ratio ↓ or inventory p99 ↑ → reduce admit_rate
If payment PSP degraded → shrink shopping window / pause admits
Never “catch up” by admitting faster than inventory TPS
```

#### 5.2.10 Path evolution 10× / 100× / 1,000×

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Queue | Redis FIFO | Lottery+WS | Edge waiting room |
| Hold | SQL txn | Redis Lua+WAL | Memory bitmap+WAL |
| Availability | 1–5s snapshot | Section bitmaps | Push edge |
| Pay | Webhook workers | Sharded appliers | Same + multi-PSP |
| Issue | Sync after pay | Async outbox | Cell-local issuer |

#### 5.2.11 Parallelization

```text
Do NOT parallelize hold of same seat across workers without fencing
Parallel OK: webhook processing across orders; availability snapshot builders;
best-available search within one request (single-threaded hold apply)
```

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
event.fairness_mode: fifo|lottery
event.admit_rate_per_s: 200
event.shopping_window_s: 600
event.hold_ttl_s: 480
event.max_tickets_per_user: 4
event.onsale_mode: true
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `queue_depth` | UX / PR |
| `admit_rate` | Protection |
| `hold_success_ratio` | Contention |
| `inventory_remaining` | Sellout |
| `payment_webhook_lag` | Issue delay |
| `double_sell_guard_trips` | Must be 0 |
| `hold_expire_total` | Hoarding/friction |

#### 5.3.3 Testing

- Concurrent hold same seat (fuzz).  
- GA remaining never negative under parallel.  
- Webhook duplicates / out-of-order.  
- TTL release returns seat to OPEN.  
- Chaos: kill inventory primary mid-hold.

#### 5.3.4 Operability

- Panic button: pause admits; read-only sold-out.  
- Shadow inventory for reseat tools.  
- Feature flag lottery vs FIFO.  
- Postmortem dumps: audit log by event_id.

#### 5.3.5 SLIs

| SLI | Target sketch |
|-----|---------------|
| Double-sell count | **0** |
| Hold p99 latency | < 100–200ms in-cell |
| Admit token issue p99 | < 50ms |
| Webhook→ticket lag p99 | < 30s |
| Availability staleness | < 5s during onsale |

#### 5.3.6 Migrations & flags

```text
fairness_mode, admit_rate, hold_ttl, max_per_user, inventory_backend=sql|redis_wal
Migrate seat map versions with event_id pin; never mutate sold seats’ geometry silently
Dual-write audit to cold store before dropping hot partitions
```

#### 5.3.7 Multi-region ops

```text
Hot event inventory: single home region/cell (strong)
Catalog/browse: global read replicas + edge
Payments: PSP global; order home follows event cell
Failover inventory: planned freeze admits → promote secondary from WAL → resume
```

#### 5.3.8 Testing & replay

- Deterministic concurrency tests: 10K goroutines one seat.  
- Chaos: kill leader mid-Lua; ensure no double SOLD.  
- Replay audit → rebuild remaining == truth.  
- Game day: Taylor-scale waiting room + sellout edge.

### 5.4 Inventory algorithms deep dive

#### 5.4.1 Reserved multi-seat atomic hold

```text
BEGIN;
SELECT * FROM seats WHERE event_id=? AND seat_id IN (...) FOR UPDATE;
-- all must be OPEN
UPDATE seats SET status='HELD', hold_id=?, exp=? WHERE ...;
INSERT hold ...;
COMMIT;
```

Deadlock avoidance: sort `seat_id` ascending before lock.

#### 5.4.2 Best-available

```text
Per row: maintain free intervals [start,end]
Find first interval with length >= qty (or score by centrality)
Atomically hold chosen ids; on conflict retry next candidate
```

#### 5.4.3 GA Lua sketch

```text
if redis.call('GET', pool) >= qty then
  redis.call('DECRBY', pool, qty); write WAL; return OK
else return FAIL end
```

### 5.5 Anti-bot & fairness (Meta flavor)

```text
Defense in depth: WAF, device attestation, CAPTCHA at queue entry,
purchase limits, resale policy hooks, velocity on accounts
FIFO helps humans feel fair; lottery reduces bot early-bird — say both
```

### 5.6 Progressive architecture evolution

| Stage | Queue | Inventory | Money |
|-------|-------|-----------|-------|
| MVP | Redis FIFO | SQL seats/GA | PSP webhook |
| Scale | Admit controller | Event shard | Idempotent workers |
| Mega | Edge room + lottery | Redis+WAL cell | Multi-PSP |
| Global | Hierarchical admit | Home cell | Reconcile fleet |

---

## 6. Wrap-Up

### 6.1 What we designed

A **Ticketmaster-class** system: waiting-room gated shopping, atomic reserved/GA holds with TTL, idempotent payment webhooks, and ticket issuance—event-sharded inventory that survives onsale stampedes.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Fairness | FIFO vs lottery — product choice |
| Browse vs hold | Cache for browse; strong for hold |
| Redis inventory | OK with WAL/rebuild; not ephemeral-only for SOLD |
| Client pay success | Insufficient alone |
| Global seats table | Deal-breaker at spike |

### 6.3 30-second scale narrative

> Baseline: SQL atomic holds + Redis waiting room + PSP webhooks. 10× event shards and availability snapshots. 100× hot-event inventory cells with Lua/WAL and lottery options. 1,000× edge queues and home-cell inventory with hierarchical admission.

### 6.4 Deal-breakers checklist

- Check seat availability then update without atomic predicate.  
- No waiting room on mega-onsale.  
- Issue tickets on client-side payment callback only.  
- Infinite holds without TTL.  
- Live DB seat locks on every map tile render.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & clarifying

**Q1: Reserved vs GA differences?**  
A: Reserved needs per-seat identity and often adjacency; GA is a counter (sometimes with area caps). Same hold/pay/issue shell, different lock primitives.

**Q2: Why holds exist?**  
A: Users need time to pay without someone sniping the seat mid-checkout; holds are short leases.

**Q3: Is FIFO truly fair?**  
A: Only among those who can join the queue; bots join early. Lottery or ID verification improves fairness.

**Q4: Accessible seating?**  
A: Separate pools with eligibility checks; don’t dump into general scramble.

**Q5: Presales?**  
A: Entitlement codes/artist fan clubs gate queue entry or admit priority.

### 7.2 Inventory & locking

**Q6: How do you atomic multi-seat hold in SQL?**  
A: `SELECT ... FOR UPDATE` seats ordered by `seat_id` to avoid deadlock; verify all OPEN; update to HELD; insert hold row; commit.

**Q7: Deadlock prevention?**  
A: Always lock seat IDs in sorted order across transactions.

**Q8: Redis Lua hold sketch?**  
A: Script checks each seat key == OPEN, sets HELD with hold_id+TTL, writes hold hash; returns fail if any miss. Persist to DB async with care—or use Redis as cache in front of DB with two-phase.

**Q9: Why lazy expiry + sweeper?**  
A: Lazy on access fixes hot paths; sweeper catches abandoned seats without traffic.

**Q10: Can you oversell with replicas?**  
A: Yes if writes go to multiple primaries—**single writer per event shard**.

### 7.3 Waiting rooms & load shedding

**Q11: How to compute ETA?**  
A: `(position / admit_rate)` smoothed; show bands not false precision.

**Q12: Heartbeats?**  
A: Require periodic heartbeat or lose place (anti-idle); balance UX vs bot automation.

**Q13: Edge waiting rooms?**  
A: Enqueue at edge POPs; admit decisions coordinated with home capacity budgets via global counters.

**Q14: What if queue Redis dies?**  
A: Fail closed (pause onsale) or rehydrate from durable log; communicate; avoid silent inventory free-for-all.

**Q15: CAPTCHA where?**  
A: On queue entry and sometimes on admit; minimize on every click.

### 7.4 Payments & money

**Q16: Authorization vs capture?**  
A: Auth at checkout; capture on issue—or capture immediately per policy. State both; refunds differ.

**Q17: Webhook before redirect?**  
A: Common—UI must poll order status; backend webhook is source of truth.

**Q18: Exactly-once issue?**  
A: Idempotent `issue(order_id)` with unique constraints on tickets.

**Q19: Partial capture / multi-ticket fail?**  
A: All-or-nothing issue in one txn; if barcode system fails, retry without recharging.

**Q20: Chargebacks?**  
A: Mark tickets void; operational process; inventory rarely returned last-minute—policy.

### 7.5 Data modeling & indexing

**Q21: Indexes for seats?**  
A: PK `(event_id, seat_id)`; secondary `(event_id, status, section_id, row)` for best-available scans—careful hotspot updates on status.

**Q22: Bitmap alternative?**  
A: In-memory bitset per section for OPEN seats; durable txn log—great at 100×.

**Q23: Order history by user?**  
A: `(user_id, created_at)` index; tickets by `order_id`.

**Q24: Avoid hot event row?**  
A: Don’t store `tickets_sold` on single event row updated every sale; use counters service / aggregate async.

### 7.6 Hashing, LB, cells

**Q25: Why shard by event_id?**  
A: Natural isolation; one hot concert doesn’t lock another; colocate seats/holds/orders for that event.

**Q26: Load balance APIs?**  
A: Stateless API tier; sticky only if needed for WS queue status.

**Q27: Hot section within event?**  
A: Sub-shard sections if needed; multi-seat across section shards needs distributed txn—prefer keep one event = one cell until forced.

### 7.7 Algorithms

**Q28: Best available seats?**  
A: Optimize for togetherness (same row contiguous), then distance to stage; precompute ranked groups offline for popular qty (2/4).

**Q29: Lottery implementation?**  
A: Assign `random()` rank at entry; admit ascending; or batch draw every T seconds from waiting set.

**Q30: Anti-scalping purchase limits?**  
A: Per-user/event caps; payment fingerprint; account age; transfers delayed—arms race.

### 7.8 Failure drills

**Q31: Inventory primary fails mid-txn?**  
A: ACID abort; client retries idempotently; seats remain OPEN.

**Q32: Sweeper bug expires paid hold?**  
A: State machine: CONSUMED holds immune; sweeper only ACTIVE past TTL.

**Q33: Double webhook success?**  
A: `psp_event_id` unique table; second is no-op.

**Q34: User pays but hold expired?**  
A: Auth hold still ACTIVE before pay create; if expired, refuse payment create; if race, auto-refund path—explicit design.

### 7.9 Estimation

**Q35: Admit rate sizing?**  
A: `admit ≈ hold_tps_capacity × shopper_success_fraction^{-1}` roughly; tune from metrics.

**Q36: 50K seats sold in 10 minutes?**  
A: ~83 sales/s average; peaks higher; trivial for payments, hard for fairness/UX.

**Q37: Queue depth 10M memory?**  
A: 10M × 50B ≈ 500MB/event—OK; store compact user refs.

### 7.10 Alternatives & deal-breakers

**Q38: Only use Kafka as inventory?**  
A: Event sourcing possible; harder for low-latency CAS holds—usually OLTP/Redis for locks + log for audit.

**Q39: Optimistic UI without server hold?**  
A: Deal-breaker for scarce seats.

**Q40: Meta interview closer?**  
A: “I’d protect the inventory with a waiting room, make holds atomic with TTL, and finalize tickets only through idempotent payment state machines—then shard by event for the Taylor Swift jump.”

---

### 7.11 Extra depth

**Q41: How do comps/admin seats work?**  
A: Admin path reserves without queue; still atomic status transition; full audit.

**Q42: Flash dual-price tiers?**  
A: Separate pools; avoid moving seats between pools without txn.

**Q43: Mobile wallet delivery failure?**  
A: Tickets exist server-side; retry push; PDF fallback.

**Q44: Cross-event cart?**  
A: Out of MVP; distributed holds across events cells are painful.

**Q45: Timezone onsale?**  
A: Store absolute UTC `onsale_start`; display local.

**Q46: Seat map versioning?**  
A: Immutable `map_version`; holds reference version; publishes cut over.

**Q47: Read-your-holds consistency?**  
A: Hold create returns truth from primary; map snapshot may lag—OK.

**Q48: GDPR delete user?**  
A: Anonymize PII on orders; legal retention for tickets often required—compliance mode.

**Q49: Observability of double-sell?**  
A: Unique constraint on `tickets.seat_id` where active; metric on constraint violations = page severity.

**Q50: Shortest verbal design?**  
A: Waiting room → atomic hold → idempotent pay webhook → issue; shard by event; cache browse.

---

## Appendix A — End-to-end sequence (reserved seat purchase)

```text
1. User enters waiting room for event_id (anti-bot scored)
2. Queue service assigns position / lottery ticket; heartbeats
3. Admit controller grants signed admit_token until T_exp
4. Client loads availability snapshot (CDN/cache)
5. POST /holds {seat_ids[]} with admit_token + Idempotency-Key
6. Inventory: sorted FOR UPDATE seats; all OPEN → HELD; hold TTL
7. POST /checkouts → order AWAITING_PAYMENT bound to hold
8. POST /payments → PSP Intent (idempotent by order_id)
9. Client confirms card; PSP sends webhook succeeded
10. Order → PAID → issue tickets; seats → SOLD; hold CONSUMED
11. Email/wallet delivery async; GET /orders shows QR payloads
```

## Appendix B — GA atomic update

```sql
UPDATE ga_pools
SET remaining = remaining - :qty, version = version + 1
WHERE pool_id = :pool AND remaining >= :qty AND event_id = :e;

-- 0 rows ⇒ sold out / insufficient; do not insert hold
```

Redis Lua equivalent: check counter, DECRBY, write hold hash with PEXPIRE.

## Appendix C — Hold expiry algorithm

```text
Active sweeper:
  every few seconds, claim expired ACTIVE holds via
  SELECT ... WHERE expires_at < now LIMIT N FOR UPDATE SKIP LOCKED
  release seats/GA; mark EXPIRED

Lazy check:
  on hold read / checkout: if expired → release path

Paid/Consumed holds never expire-release seats.
```

## Appendix D — Waiting room admit controller

```text
target_concurrent_shoppers = f(inventory_tps, checkout_latency, cart_conversion)
admit_rate = PID or simple leaky bucket toward target
on inventory lag / error budget burn → reduce admit_rate
on sellout → admit_rate = 0; broadcast SOLD_OUT snapshot
shopping_window = 10–15m; token HMAC(event, user, exp, nonce)
```

## Appendix E — Seat adjacency (best available)

```text
Input: section, qty q
Scan each row's OPEN runs (interval merge)
Candidate = contiguous run length ≥ q minimizing distance(stage)
Atomic hold exact seat_ids chosen
If race fails, retry next candidate ≤ K times then 409
```

Precompute popular q∈{1,2,3,4} bundles offline for mega-onsales.

## Appendix F — Payment reconciliation state machine

```text
Order:
  CREATED → AWAITING_PAYMENT → PAID → ISSUED
                     syn          ↓
                  CANCELED ←—— REFUNDED

Payment:
  INTENT_CREATED → SUCCEEDED | FAILED | CANCELED

Reconciler rules:
  SUCCEEDED ∧ order AWAITING → mark PAID + issue
  PAID ∧ no tickets → issue
  ACTIVE hold ∧ expires → release (unless order PAID in flight — fence)
```

## Appendix G — Idempotency keys catalog

| Operation | Key | Store |
|-----------|-----|-------|
| Queue entry | `(event_id, user_id)` session | Redis |
| Hold create | Client `Idempotency-Key` | Inventory DB |
| Payment create | `order_id` | Payments DB |
| Webhook apply | `psp_event_id` | Unique table |
| Issue tickets | `order_id` | Tickets unique |

## Appendix H — Onsale day runbook

```text
T-24h: load test admit+hold; pin config
T-2h: scale queue + inventory cells; prewarm caches
T-30m: enable waiting room mode; disable heavy search
T-0: monitor queue_depth, hold_success, remaining, webhook_lag
Sellout: freeze map to SOLD_OUT; shed holds; keep order reads
Post: drain expires; financial reconcile; export audit
```

## Appendix I — Failure matrix

| Failure | User-visible | System action |
|---------|--------------|---------------|
| Queue Redis down | Pause entry | Fail closed |
| Inventory primary down | Hold errors | Failover; block admits |
| PSP down | Checkout retry | Holds keep TTL |
| Webhook delayed | “Processing” | Reconciler polls PSP |
| Sweeper bug | — | Page; pause sweeper |

## Appendix J — Data retention

```text
Active inventory: until event + grace
Orders/tickets: years (legal)
Queue positions: hours
Payment raw webhooks: 90d+
Audit log: long-term immutable
PII minimization on exports
```

## Appendix K — Progressive scale checklist

| Scale | Must say |
|-------|----------|
| Baseline | SQL atomic holds + Redis queue + PSP webhooks |
| 10× | Event shard; availability snapshots; admit tokens |
| 100× | Hot-event cells; Lua/WAL; lottery option |
| 1,000× | Edge queues; hierarchical admit; home inventory |

## Appendix L — Deal-breaker checklist

1. Check-then-update seats without fencing  
2. No waiting room on mega-onsale  
3. Issue on client payment callback only  
4. Infinite holds  
5. Live DB lock on every map tile GET  
6. Multi-primary writers for same event inventory  
7. Ignoring webhook idempotency  

## Appendix M — FIFO vs lottery script (say aloud)

> “FIFO matches mental model but rewards bots that join early. Lottery reduces that advantage but feels random. I’d make it a per-event config and always couple either mode with a leaky admit rate sized to inventory TPS.”

## Appendix N — Sample metrics dashboard

```text
queue_depth{event}
admit_rate{event}
hold_qps{result=ok|conflict|expired_token}
ga_remaining{pool}
seats_open{section}
payment_success_ratio
issue_lag_ms
double_sell_violations  # must be 0
```

## Appendix O — Meta interview closing

> “I’d put a waiting room in front of Ticketmaster-scale onsales, make reserved and GA holds atomic with TTLs, finalize tickets only through idempotent payment webhooks, and shard inventory by event so a stadium spike can’t take down the platform.”

## Appendix P — 30-minute interview checklist

1. Clarify reserved vs GA, hold TTL, fairness mode, refunds.  
2. BOTE: arrivals/s vs admit target vs hold TPS.  
3. Draw edge → queue → inventory → pay → issue.  
4. Deep dive atomic hold + webhook issue.  
5. Scale narrative 10×/100×/1,000×.  
6. Deal-breakers.

## Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Hold | Short lease on inventory before pay |
| GA | General admission quantity pool |
| Admit token | Signed permission to shop |
| Waiting room | Virtual queue protecting backends |
| PSP | Payment service provider |
| Comp | Admin-issued ticket |
| Fence | Version/CAS guard against races |

## Appendix R — Anti-bot layers (defense in depth)

```text
1. WAF / IP reputation at edge
2. Device attestation / risk score at queue entry
3. CAPTCHA on suspicious sessions
4. Purchase limits per user/event/payment instrument
5. Velocity checks on holds
6. Manual / ML scalper clusters post-hoc
```

Never claim 100% bot immunity.

## Appendix S — Why availability is a snapshot

```text
Browse QPS >> Hold QPS
Snapshot lag of 1–5s acceptable; truth is hold result
Clients must handle 409 conflict gracefully (seat taken)
Sold-out edge object prevents origin meltdown after sellout
```

## Appendix T — Anti-patterns

| Anti-pattern | Failure | Instead |
|--------------|---------|---------|
| No waiting room | Inventory death | Admit-rate gate |
| Check-then-act seats | Double-sell | Atomic txn/Lua |
| Trust client pay OK | Free tickets | Webhook + reconcile |
| Infinite holds | Hoarding | TTL + sweeper |
| Live SQL map at 1M QPS | Outage | Edge snapshots |
| Multi-master seats | Double-sell | Single cell leader |
| Redis SOLD without WAL | Amnesia | Durable transitions |
| Faster admit to “catch up” | Cascading failure | Backpressure admit_rate |
| Global seats table | Hotspot | event_id shard |
| Optimistic UI sold | Support nightmare | Hold-first UX |

## Appendix U — 90s interview pitch

> “Ticketmaster is load shedding plus atomic inventory. Waiting room bounds shoppers; event_id cells own seat/GA truth; holds TTL; payments idempotent via PSP webhooks; tickets only after PAID. Availability is a cached snapshot—409s are normal. At scale: edge queues, Redis+WAL inventory, lottery fairness, zero tolerance for double-sell.”

## Appendix V — Numeric drills

```text
5M fans / 60s ≈ 83K arrivals/s → waiting room mandatory
Admit 20K; hold ~200B × 200K = 40MB
50K seats JSON naïve 10MB → bitfield/sections + edge
GA DECR at 50K/s needs in-memory/Lua not hot SQL row alone
Double-sell SLO = 0 forever
```

---

*End of Meta system design: Ticketmaster.*
