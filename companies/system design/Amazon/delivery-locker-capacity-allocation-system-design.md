# System Design: Delivery Locker Capacity Allocation

> **Focus areas:** Mixed locker sizes · Predicted delivery date (PDD) · Soft/hard reservations · Expiration & reclaim · Cost minimization · Overbooking · Station inventory · Customer experience (missed pickup / reattempt)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes (quote vs reserve vs event), explicit invariants, Amazon themes (practicality, reliability, ownership, business trade-offs)

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

Goal: **bound the product**—when capacity is promised for a locker delivery, how mixed compartment sizes are allocated against predicted delivery dates, how reservations expire, and how we minimize cost (failed deliveries, courier reattempts, wasted compartments) without stranding customers.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a locker station? | Physical site with many compartments of sizes S/M/L/XL (and maybe fridge later) | Station inventory model; size classes; geo index for selection |
| F2 | When do we allocate? | At checkout (offer locker option), at ship/sort planning, and at last-mile handoff | Multi-stage: **quote → soft reserve → hard reserve → occupy → release** |
| F3 | Predicted delivery date? | Carrier/promise engine gives PDD (date or datetime window) | Capacity buckets by **station × size × date (or window)** |
| F4 | Mixed sizes? | Package dimensions → minimum fitting size; can upsize if cheaper overall | Fit function + upsize policy with cost weights |
| F5 | Reservation hold time? | Soft hold during checkout (minutes); hard hold until delivery day + pickup SLA | TTL leases; state machine; reclaim sweeper |
| F6 | Expiration? | Customer pickup SLA (e.g. 3 days) then return-to-station / refund path | Occupy TTL; notifications; expiration jobs |
| F7 | Overbooking? | Limited intentional overbook based on no-show / early-pickup / cancel rates | Probabilistic capacity; risk controls by station |
| F8 | Cost to minimize? | Failed locker delivery, courier wait, reattempt to home, idle compartments, upsizing waste | Explicit cost function in allocator; not “first fit” only |
| F9 | Selection UX? | Customer picks station near address; or Amazon suggests cheapest/feasible | Availability API with alternatives ranked by cost/distance |
| F10 | Package arrives early/late vs PDD? | Early: may wait in trailer/cage or occupy if reserved; late: replan | Flexibility buffers; reallocation APIs |
| F11 | Multi-package orders? | Same station preferred; may need multiple compartments | Bundle allocation / adjacent preference optional |
| F12 | Failures at door? | Locker full/broken → redirect home or alternate station | Compensating transactions; courier app fallback |
| F13 | Who owns capacity? | Last-mile / Locker platform team; stations ops own hardware health | Clear ownership + ops tooling for outages |
| F14 | Idempotency? | Checkout retries, carrier scans duplicate | Idempotent reserve/confirm with keys |
| F15 | International / 3P lockers? | Maybe later; Amazon Lockers first | Adapter interface; MVP first-party |

**MVP functional scope (lock with interviewer):**

1. Station catalog with compartment counts by size; online/offline status.
2. **Availability quote** for `(station, package_dims, pdd)` → feasible sizes + soft quote token.
3. **Soft reserve** (checkout TTL, e.g. 15 min) then **hard reserve** on order confirm / ship commit.
4. **Occupy** on successful stow; **release** on pickup / expiration / cancel.
5. **Expiration sweeper** reclaiming unused reserves and expired occupies.
6. **Upsize** when exact size unavailable if policy says so.
7. **Cost-aware ranking** of stations/sizes (distance + expected failure + upsize penalty).
8. Courier / station event ingestion (stow, pickup, fault).
9. Ops kill: mark station/size offline → exclude from new allocations.

**Out of MVP (explicitly defer):**

- Dynamic pricing of locker slots as a marketplace
- Perfect multi-stop courier route optimization (adjacent problem)
- Fridge/hazmat special chains
- Guaranteed atomic allocation across all 3P locker networks
- ML package-dimension prediction from ASIN alone without carrier dims (nice later)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Quote latency? | Checkout critical | p50 < 50ms, p99 < 200ms in-region |
| N2 | Reserve correctness? | No double-book same compartment | Strong consistency **per station shard**; never two hard reserves on one unit capacity without overbook math |
| N3 | Availability? | Checkout degradation OK with fallback to home delivery | Quote fail-open to “locker unavailable”; never fail paid order creation wrongly |
| N4 | Durability? | Confirmed reservations durable | ACK only after durable write |
| N5 | Pickup UX? | Codes work; capacity accurate enough | Stale free-count bounded; reconcile with station telemetry |
| N6 | Throughput? | See scale | Split **quote QPS**, **reserve QPS**, **event QPS**, **sweeper QPS** |
| N7 | Consistency** | Cross-region | Station home region / cell; customers quoted from nearest |
| N8 | Cost / efficiency | High utilization without CX pain | Track utilization, overbook incidents, redirect rate |
| N9 | Audit | Dispute “I reserved” | Event log of capacity transitions |
| N10 | Time zones | PDD local to station | Store UTC + station TZ; bucket by **station-local date** |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Customer selects Locker X at checkout for package needing M on PDD=Thu → soft reserve M@X@Thu → payment OK → hard reserve → package ships → arrives Thu → courier stows → occupy → customer picks up Fri → release.
2. Exact M full → allocator offers L (upsize) with small fee/cost penalty → customer accepts → reserve L.
3. Soft reserve expires (abandoned cart) → sweeper frees capacity before PDD.
4. Customer doesn't pick up in 3 days → expire occupy → ops/return flow → capacity free.
5. Station size M marked fault → capacity reduced → new quotes exclude; existing hard reserves may replan.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click checkout reserve | Idempotency key → one reservation |
| Soft reserve not confirmed | TTL expiry; capacity returns to pool |
| PDD slips by +2 days | Move hard reserve to new date bucket or re-quote; notify |
| Package arrives when reserved day compartment still occupied | Overflow cage / reattempt / alternate compartment; incident metric |
| Overbook triggers and locker truly full | Courier fallback to home delivery; costly—bound overbook |
| Station power outage | Offline flag; stop new reserves; existing occupies stay physical |
| Clock skew on TTL | Server-side expiry timestamps; sweeper uses DB time |
| Split shipment multi-PDD | Separate reservations per package |
| Dimension wrong (too big) | Stow fails → event → release reserve → replan home |
| Inventory drift (telemetry vs system) | Periodic reconciliation; trust physical scan on conflict for occupy |
| Thundering herd sweeper at midnight | Shard by station; jitter leases |
| Holiday PDD bunching | Capacity calendars; throttle overbook; suggest alternate dates/stations |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Locker stations | 10K | 50K | 200K | 1M |
| Compartments total | 1M | 10M | 100M | 1B |
| Peak **quote QPS** | 5K | 50K | 500K | **5M** |
| Peak **reserve/confirm QPS** | 500 | 5K | 50K | 500K |
| Peak **station events**/s | 1K | 10K | 100K | 1M |
| Active reservations | 2M | 20M | 200M | 2B |
| Avg packages / station / day | 40 | 80 | 120 | 150 |
| Geos / countries | 5 | 10 | 20 | 30+ |

**What each jump forces:**

- **10×:** Shard capacity by `station_id`; Redis/Dynamo for hot counters; not one Postgres rowset for world.
- **100×:** Regional cells; calendar materialization; probabilistic overbook models; event-sourced transitions; CQRS quote vs reserve.
- **1,000×:** Hierarchical geo indexes, approximate quotes with final conditional reserve, station-level actors, aggressive TTL hygiene, cost model online learning.

### 1.5 Etc. (Constraints & Assumptions)

- Promise/PDD engine exists upstream (we consume `pdd` + confidence).
- Package dimensions available at allocate time (from FC / ASIN dims + packing).
- Courier app can report stow success/fail with compartment id.
- Home delivery is always the economic backup—locker is an optimization.

**Scope statement:**

> Design Amazon Locker capacity allocation: quote and reserve mixed-size compartments against predicted delivery dates with soft/hard leases, expiration/reclaim, and a cost-minimizing allocation policy—correct under retries and station faults—baseline ~5K quote QPS / 10K stations scaling toward ~5M quote QPS / ~1M stations.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 1,000× | Latency | Notes |
|-------|------|----------|--------|---------|-------|
| **Quote / availability** | Read-mostly feasibility + rank | 5K/s | 5M/s | Critical | Cacheable aggregates |
| **Soft reserve** | Hold capacity briefly | 1K/s | 1M/s | Critical | Conditional write |
| **Hard reserve / confirm** | Durable commit | 500/s | 500K/s | Important | Strong per station |
| **Station events** | Stow/pickup/fault | 1K/s | 1M/s | Important | Idempotent apply |
| **Sweeper / expiry** | Reclaim TTLs | 200/s | 200K/s | Batch | Sharded |
| **Replan / PDD change** | Move buckets | 50/s | 50K/s | Best-effort | |

**Anti-pattern:** one “Locker API QPS” number that mixes reads and conditional writes.

### 2.2 Capacity model size

```text
Station: 100 compartments, 4 sizes → track counts per size per day horizon
Horizon H = 14 days of PDD buckets
Counters per station: 4 sizes × 14 days = 56 counter keys
10K stations × 56 ≈ 560K keys — trivial
1M stations × 56 = 56M keys × ~64 B ≈ 3.5 GB — fine in sharded Redis/Dynamo
```

Also track **physical compartment state** (which unit free/occupied)—needed for stow assignment:

```text
1M compartments × 100 B ≈ 100 GB globally → shard by station; not global monolith
```

### 2.3 Quote fanout math

```text
Naive: checkout asks “lockers near me” → 20 candidates × counter reads
5K QPS × 20 = 100K counter reads/s — OK with pipeline/cache
5M QPS × 20 = 100M reads/s — need geo prefilter + cached availability bitmaps + conditional reserve only on chosen station
```

### 2.4 Reservation write math

```text
Hard reserves 500/s × 1 KB row ≈ 0.5 MB/s — easy
At 500K/s → 500 MB/s writes — shard heavily; avoid cross-station TX
```

### 2.5 Bandwidth / events

```text
Event ~300 B
1K/s → 300 KB/s
1M/s → 300 MB/s into Kafka — standard partitioning by station_id
```

### 2.6 Cost function sketch (interview-friendly)

```text
cost(assign) =
  w_dist * travel_penalty(customer, station)
+ w_upsize * (size_used - size_needed)
+ w_fail * p_stow_fail(station, size, day)
+ w_overbook * overbook_risk
+ w_cx * expected_pickup_friction

Choose argmin cost among feasible (station, size) with capacity_available > 0 (or overbook budget)
```

### 2.7 Overbooking intuition

```text
If historical no-show/cancel before stow = 8% for station S on weekdays,
can sell ~1 / (1-0.08) ≈ 1.087× physical slots in soft+hard pre-stow layer
BUT bound by pain of failure: if redirect-to-home costs $X, cap expected failures
```

### 2.8 TTL / sweeper

```text
Soft TTL 15 min; active soft reserves 2M → expiries ~2M/15min ≈ 2.2K/s average
Use time-bucketed expiry indexes or DynamoDB TTL + stream — don't full-scan
```

---

## 3. High-Level Design

### 3.1 Capacity lifecycle

```text
FREE → SOFT_RESERVED → HARD_RESERVED → OCCUPIED → FREE
                ↘ expired                ↘ cancel
HARD_RESERVED → REPLANNED (PDD move)
OCCUPIED → EXPIRED_PENDING_RETURN → FREE
Station FAULT reduces FREE effective capacity
```

### 3.2 Two layers of inventory (important)

| Layer | Meaning | Store |
|-------|---------|-------|
| **Calendar counters** | How many of size M still sellable for date D at station S | Redis / Dynamo counters |
| **Compartment ledger** | Physical doors: id, size, state, reservation_id | DynamoDB / SQL per station shard |

**Quote** uses counters (fast).  
**Stow** assigns a concrete compartment from ledger.  
**Invariant:** `sum(ledger free of size) + inflight ≈ counter` with reconciliation.

Why split? Checkout shouldn't lock a specific door 4 days early (doors fail; cleaning; flexible stow). Reserve **count by size×date**; bind door late.

### 3.3 Components

| Component | Role |
|-----------|------|
| **Station Catalog** | Geo, hours, sizes, status, TZ |
| **Availability / Quote Service** | Rank feasible stations/sizes for request |
| **Reservation Service** | Soft/hard reserve, confirm, cancel, replan |
| **Capacity Counter Store** | Atomic decr/incr by station×size×day |
| **Compartment Ledger** | Per-door state; late binding |
| **Expiry / Sweeper** | TTL reclaim; pickup SLA expiry |
| **Event Ingest** | Courier stow/pickup/fault; customer pickup |
| **Cost / Policy Engine** | Weights, overbook limits, upsize rules |
| **PDD Listener** | Promise changes → replan |
| **Ops Console** | Offline station/size; audit; incidents |
| **Notification** | Pickup codes, expiry warnings (integrate, don't own full SES) |

### 3.4 APIs

```text
GET  /v1/stations/nearby?lat=&lng=&radius=
POST /v1/capacity/quote
     { packages: [{dims, weight}], pdd, customer_geo, candidates[]? }
  → { offers: [{station_id, size, cost_score, quote_token, expires_at}] }

POST /v1/reservations/soft
     { quote_token, idempotency_key, order_draft_id }
  → { reservation_id, expires_at }

POST /v1/reservations/{id}/confirm   # hard reserve
POST /v1/reservations/{id}/cancel
POST /v1/reservations/{id}/replan    { new_pdd }

# Internal / courier
POST /v1/stations/{id}/events/stow
     { reservation_id, package_id, compartment_id?, ts, idempotency_key }
POST /v1/stations/{id}/events/pickup
POST /v1/stations/{id}/events/fault

# Ops
POST /v1/stations/{id}/offline
PATCH /v1/stations/{id}/capacity   # maintenance
```

### 3.5 Data models

**Station**

```text
Station {
  station_id, geo, address, tz,
  status: ONLINE|DEGRADED|OFFLINE,
  compartments: [{ compartment_id, size, hardware_status }],
  overbook_policy_id,
  pickup_sla_hours: 72
}
```

**Capacity bucket (counter)**

```text
CapacityBucket {
  pk: station_id,
  sk: SIZE#M#DATE#2026-08-07,  # station-local date
  sellable: int,     # physical_free_adjusted * overbook - sold
  hard_reserved: int,
  soft_reserved: int,
  occupied: int,     # optional denorm
  version: int       # optimistic concurrency
}
```

**Reservation**

```text
Reservation {
  reservation_id,
  state: SOFT|HARD|OCCUPIED|CANCELLED|EXPIRED|FAILED_STOW,
  station_id, size, pdd_local_date,
  package_id, order_id,
  customer_id,
  soft_expires_at, pickup_expires_at?,
  compartment_id?,   # set on stow
  idempotency_key,
  cost_score_at_quote,
  created_at, updated_at
}
```

**Compartment**

```text
Compartment {
  station_id, compartment_id, size,
  state: FREE|RESERVED_TEMP|OCCUPIED|FAULT|MAINTENANCE,
  reservation_id?, package_id?,
  updated_at, version
}
```

### 3.6 Allocation algorithm

```text
function quote(req):
  candidates = geo_index.k_nearest(req.geo, k=30) filter ONLINE
  needed = min_fit_size(req.dims)
  offers = []
  for s in candidates:
    for size in sizes >= needed:   # exact then upsize
      bucket = counter(s, size, req.pdd_local)
      if bucket.sellable <= 0: continue
      score = cost(s, size, needed, bucket, req)
      offers.append(Offer(s, size, score))
  return top_n(offers, by=score asc)

function soft_reserve(offer, idem_key):
  # atomic: DEC sellable IF sellable > 0; INC soft_reserved
  # write Reservation SOFT with TTL
  # return reservation_id

function confirm(res_id):
  # soft → hard: DEC soft_reserved; INC hard_reserved (same bucket)
  # extend durability; clear soft TTL

function stow(station, reservation, package):
  # pick concrete FREE compartment of size (or allowed upsize)
  # CAS FREE → OCCUPIED
  # reservation → OCCUPIED; set pickup_expires_at
  # adjust counters (hard_reserved--, occupied++)

function pickup(...):
  # OCCUPIED → FREE; counters--; notify complete
```

### 3.7 Atomic counter patterns

**DynamoDB conditional update (good default for Amazon interview):**

```text
Update CapacityBucket
  SET sellable = sellable - 1, soft_reserved = soft_reserved + 1
  IF sellable > 0 AND version = :v
```

**Redis Lua (hot stations):**

```text
if tonumber(redis.call('GET', key)) > 0 then
  redis.call('DECR', key)
  return 1
else return 0 end
```

Durability: Redis needs AOF/replication + async DB write of reservation; **source of truth for money path** should be durable reservation record—counters can rebuild from reservations + ledger.

**Deal-breaker:** decrementing counters without durable reservation row → lost money promises.

### 3.8 Trade-off tables

| Decision | A | B | Choose | Deal-breaker |
|----------|---|---|--------|--------------|
| Early bind door | Reserve specific door at checkout | Reserve size×date count; bind at stow | **Late bind** | Early bind brittle + fragmentation |
| Counter store | SQL alone | Dynamo/Redis + durable reservation | **Hybrid** | SQL hotspot at 100× |
| Overbook | Never | Controlled | **Controlled + capped** | Either low util or CX disasters |
| Quote accuracy | Strong read your writes global | Slightly stale + conditional reserve | **Stale OK** | Perfect global freshness impossible |
| Upsize | Never | Always if any larger free | **Cost-weighted** | Blind upsize starves XL packages |
| Rollback | 2PC across stations | Single-station atomicity | **Single station** | Cross-station 2PC latency/fragility |
| Fail quote | Error checkout | Offer home only | **Home fallback** | Lost conversion |

### 3.9 Why choose X over Y (storage)

| Need | Choice | Why |
|------|--------|-----|
| Geo search stations | Elasticsearch / geo hash in Dynamo / Redis GEO | kNN for quote candidates |
| Counters | DynamoDB or Redis Cluster | Conditional atomics; shard by station |
| Reservations | DynamoDB (PK reservation_id, GSI by order/package) | Scale + TTL |
| Compartment ledger | DynamoDB PK=station_id, SK=compartment_id | Station locality; transactional writes with TransactWrite where needed |
| Event log | Kafka | Replay, analytics, audit |
| Analytics utilization | S3/warehouse | Cheap scans |

**SQL still useful:** catalog + policy config low-QPS strongly consistent admin.

### 3.10 Cost minimization — business framing

Amazon cares about:

1. **Customer** got package conveniently (satisfaction, Prime promise).
2. **Courier time** at locker (queueing = money).
3. **Failed stow** → reattempt / ship to home (high cost).
4. **Utilization** of expensive locker real estate.
5. **Support contacts** from expired packages / wrong codes.

Allocator is a **policy engine** with knobs owned by last-mile finance/ops—not a pure greedy bin packer.

```text
Example weights (illustrative):
  redirect_home_cost = $4.00
  upsize_M_to_L = $0.15 opportunity
  extra_km for customer = $0.05 * km (CX proxy)
  overbook_fail_prob * redirect_home_cost added to score
```

### 3.11 Mutually interacting constraints

- Selling all M for early PDDs with upsizing from S can block true M packages later → **keep contingency** or limit upsize %.
- Soft reserves inflate sellout → short TTLs + cart limits.
- Long pickup SLA reduces turnover → capacity planning (ops) vs allocation (this system).

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Customer App / Checkout
        │
        ▼
 ┌──────────────┐    geo     ┌─────────────────┐
 │ Quote Service│───────────►│ Station Catalog │
 └──────┬───────┘            └────────┬────────┘
        │                             │
        │ read counters               │
        ▼                             ▼
 ┌──────────────┐   atomic    ┌─────────────────┐
 │ Capacity     │◄────────────│ Reservation Svc │◄── confirm / cancel / replan
 │ Counters     │  decr/incr  └────────┬────────┘
 │ (Redis/DDB)  │                      │ durable rows
 └──────────────┘                      ▼
                              ┌─────────────────┐
                              │ Reservations DB │
                              └────────┬────────┘
                                       │
        PDD Service ──changes─────────►│ replan
                                       │
 Courier App / Locker HW               │
        │ events                       ▼
        ▼                     ┌─────────────────┐
 ┌──────────────┐            │ Compartment     │
 │ Event Ingest │───────────►│ Ledger          │
 │ (Kafka)      │            └────────┬────────┘
 └──────┬───────┘                     │
        │                             │
        ▼                             ▼
 ┌──────────────┐            ┌─────────────────┐
 │ Sweepers     │──expire───►│ Notification /  │
 │ (TTL reclaim)│            │ Ops / Analytics │
 └──────────────┘            └─────────────────┘
```

### 4.2 Per-station shard view

```text
                    Station S123 cell
 ┌──────────────────────────────────────────────┐
 │ Counters:  M@D1 sellable=12  L@D1=4  ...     │
 │ Ledger:    C01 FREE M | C02 OCCUPIED | ...   │
 │ Actor/lock optional: serialize stow storms   │
 └──────────────────────────────────────────────┘
         ▲ single-writer semantics per station
```

### 4.3 Sequence: checkout → stow → pickup

```text
Checkout          Quote         Reserve          Carrier/Courier      Locker
   |                |              |                    |                |
   |--quote-------->|              |                    |                |
   |<--offers-------|              |                    |                |
   |--soft----------+------------->|                    |                |
   |<--res_id-------|--------------|                    |                |
   |--confirm-------|------------->|                    |                |
   |                |              | ... days ...       |                |
   |                |              |<--stow attempt-----|                |
   |                |              |--assign door-------|--------------->|
   |                |              |<--stowed-----------|<---- lock -----|
   |                |              |                    |   customer pickup
   |                |              |<--pickup event-----|<---------------|
   |                |              |--release-----------|                |
```

### 4.4 Failure: full at stow

```text
Courier stow fail (no FREE door)
  → Event FAILED_STOW
  → Reservation compensating: HARD → FAILED_STOW
  → Counter release / adjust
  → Workflow: redirect home OR alternate station re-reserve
  → Metric: stow_fail_cost++
  → Possibly tighten overbook for station
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No silent double sell:** conditional decrement must prevent `sellable < 0` (except explicit overbook ledger).
2. **Durable promise:** customer-visible hard reserve ⇒ reservation row exists before ACK.
3. **Late bind doors:** hard reserve does not require `compartment_id` until stow.
4. **Idempotent events:** same `idempotency_key` / event id applied once.
5. **TTL monotonicity:** soft expiry server-authored; sweeper is authoritative reclaim.
6. **Station offline:** no new soft/hard; existing occupies remain until physical clear.
7. **Counter rebuildability:** counters recomputable from reservations + ledger snapshots.

#### 5.1.2 Data loss prevention

| Risk | Mitigation |
|------|------------|
| Reserve ACK before durable write | Write reservation first (PENDING_DEC) or TransactWrite counter+row |
| Redis counter loss | Rebuild from DB; Redis as acceleration with periodic checkpoint |
| Lost stow event | Courier retry; locker HW outbox; reconcile daily |
| Sweeper double-free | Conditional state transitions only SOFT→EXPIRED if still SOFT |
| Split brain station cell | Home cell epoch fencing for station shard |

#### 5.1.3 Idempotency

```text
soft_reserve(idempotency_key=order_draft+package)
  → store mapping key → reservation_id

stow(event_id)
  → processed_events set / conditional reservation state OCCUPIED only from HARD

pickup(event_id) similarly
```

#### 5.1.4 Retries & timeouts

- Quote: retryable read; no side effects.
- Soft reserve: client retries with same idempotency key.
- Confirm: conditional SOFT→HARD; retry safe.
- Stow: if timeout unknown, query reservation state before re-assigning door (avoid two doors).

#### 5.1.5 Circuit breakers

- If Capacity Counter store unhealthy: fail quote to home delivery; **do not** invent capacity.
- If single station hot errors: mark DEGRADED; remove from suggestions.
- Kafka ingest lag: backpressure courier? Prefer buffer; stow can proceed offline with later sync if HW supports local accept—product call (MVP: online confirm).

#### 5.1.6 Reconciliation

```text
Every N minutes per station:
  expected_free = physical_count - occupied - maintenance
  counter_sellable_rebuild = f(expected_free, hard, soft, overbook)
  if drift > threshold: alert; prefer ledger+reservations as truth; fix counters
```

Amazon interview gold: **admit drift**, show repair path—don't claim perfect dual writes forever.

#### 5.1.7 Time & PDD

- Bucket key uses **station-local date** of PDD.
- Early arrival: policy `allow_early_stow` if FREE door and either same reservation or pool; may consume future bucket → move accounting.
- Late arrival: `replan` API shifts hard reserve to new date if capacity; else fallback workflow.

---

### 5.2 Scalability

#### 5.2.1 Shard key design

| Entity | Shard key | Reason |
|--------|-----------|--------|
| Counters / ledger | `station_id` | All contention local to station |
| Reservation | `reservation_id` (+ GSI `station_id`, `order_id`) | Global lookup by tracking id |
| Events Kafka | `station_id` | Ordered processing per station |
| Geo index | region cells | Quote prefilter |

**Consistent hashing:** `station_id → capacity service shard / cell`. Virtual nodes for station count growth. Hot downtown station: vertical scale + Redis for counters; rare “station actor” single-thread stow queue.

#### 5.2.2 Progressive evolution

**Baseline**

- DynamoDB reservations + counters; geo via Elastic.
- Single region; sweeper Lambda/cron per shard.
- Cost weights in config.

**10×**

- Redis counters in front of Dynamo; write-through reservation.
- Quote cache: `station+size+date → sellable` with 5–30s TTL + conditional reserve.
- Station status pub/sub.

**100×**

- Regional cells (NA/EU/IN…).
- CQRS: read replicas / cached bitmaps for “has_any_capacity”.
- Overbook model offline training → online caps.
- Stream processing for utilization dashboards.

**1,000×**

- Hierarchical geo (city hubs).
- Approximate quote (bloom/bitsets of availability) + definitive reserve.
- Per-station actors (Kalix/Akka/Temporal) for ledger.
- Dynamic horizon materialization only for dates with demand.

#### 5.2.3 Traffic patterns

| Pattern | Response |
|---------|----------|
| Prime Day quote spike | Cache candidates; shed fancy ranking; keep conditional reserve correct |
| Evening pickup surge | Event path autoscale; quotes unaffected |
| Monday PDD bunching | Calendar smoothing in promise engine; allocator shows alternates |
| New station launch | Cold counters from catalog bootstrap |

#### 5.2.4 Parallelization

- Quotes across candidate stations: parallel counter gets with hedged timeouts.
- Sweepers: partition `station_id % N`.
- Replan storms after weather: rate-limit per station; queue.

#### 5.2.5 Storage evolution

```text
Keep hot: next 14 days counters
Warm: reservation rows until pickup+30d
Cold: event archive S3
Physical ledger: forever small; 1B compartments sharded
```

---

### 5.3 Maintainability

#### 5.3.1 Ownership (Amazon)

| Surface | Owner |
|---------|-------|
| Allocator / counters / reservations | Locker Capacity Platform |
| Hardware / door firmware | Locker Devices |
| Promise PDD | Promise / Speeds team (API contract) |
| Courier workflows | Last Mile Ops Eng |
| Cost weights / overbook caps | Capacity Science + Ops Finance |
| Customer notifications | Messaging platform integration |

**Oncall:** capacity page for sellable drift / reserve error spikes; devices for fault rates; joint runbooks for “station full storm”.

#### 5.3.2 Deploy

- Policy config (weights, TTLs, overbook) via dynamic config — no redeploy.
- Schema for reservation states: expandable enums; backward compatible event versions.
- Canary new allocator scoring on % traffic shadow (log would-choose vs did-choose).

#### 5.3.3 Observability

| Metric | Why |
|--------|-----|
| `quote_p99` | Checkout UX |
| `reserve_fail_soldout` | True sellout vs bug |
| `stow_fail_full` | Overbook / drift pain |
| `counter_drift` | Integrity |
| `soft_expire_rate` | Cart abandonment hygiene |
| `pickup_expire_rate` | CX + capacity waste |
| `upsize_rate` | Policy tuning |
| `redirect_home_rate` | Primary cost KPI |
| `utilization_by_size` | Planning |

**Tracing:** `order_id` / `reservation_id` / `package_id` / `station_id` correlation.

#### 5.3.4 Multi-team contracts

```text
PDD event schema { package_id, old_pdd, new_pdd, confidence }
Stow event schema { package_id, station_id, result, compartment_id, ts, event_id }
```

Versioned; consumers tolerate unknown fields.

#### 5.3.5 Business trade-offs to verbalize

| Knob | Tighten | Loosen |
|------|---------|--------|
| Overbook | Fewer redirects; lower util | Higher util; more pain |
| Soft TTL | Free capacity faster; more re-quote | Better CX in slow checkout |
| Upsize | Protect large doors | Higher accept rate |
| Pickup SLA | Faster turnover | Harsher CX |
| Quote cache TTL | Fresher; more load | Faster; rare false offer then reserve fail |

---

## 6. Wrap-Up

### 6.1 Interview narrative

> “I'd model locker capacity as **station-sharded size×date counters** with **late-bound compartments**. Checkout gets a cost-ranked quote, takes a **soft lease**, then **hard reserve** on confirm. Atomic conditional decrements prevent oversell; Redis/Dynamo for counters; durable reservation rows are the promise of record. Couriers bind a physical door at stow; pickups and TTL sweepers return capacity. We minimize expected cost—distance, upsize, failure probability—not just first-fit. Overbooking is explicit and capped. If capacity systems fail, we fall back to home delivery rather than inventing slots. Ownership splits platform, devices, and last-mile ops with clear KPIs: redirect rate, drift, utilization.”

### 6.2 Emphasize for Amazon

1. **Customer promise** vs **operational cost** — name both.
2. **Failure modes** — full at stow, PDD slip, station fault.
3. **Idempotency** on reserve and courier events.
4. **Sharding by station** — natural boundary.
5. **Late binding** doors — practical ops reality.
6. **Measurable knobs** — overbook, TTL, upsize.

### 6.3 Likely interviewer probes

- “Do you reserve a specific box at order time?” → Prefer not.
- “How do you not double-book?” → Conditional sellable--; durable row.
- “What if counters wrong?” → Reconcile from ledger; trust physical at stow.
- “Optimize only utilization?” → No—redirect cost dominates.
- “Cross-station transaction for multi-package?” → Prefer same station one TX shard; else saga with compensation.

---

## 7. Deeper / Related Interview Questions

### 7.1 Modeling & algorithms

**Q: Bin packing exact compartments early?**  
A: NP-hard flavor + brittle; use size classes + late bind.

**Q: First-fit vs best-fit vs cost score?**  
A: Cost score; best-fit (smallest fitting) often good default inside cost function.

**Q: How to min-fit size?**  
A: Package L×W×H sorted vs compartment opening + volume constraints; orientation rules.

**Q: Multi-package same station?**  
A: Try allocate all; if fail mid-way, compensate released soft reserves (saga).

**Q: Hungarian algorithm for N packages × M stations?**  
A: Overkill for checkout p99; greedy + local search enough; batch optimizer offline for planning.

**Q: Overbook math?**  
A: Erlang-like or simple `sellable = floor(physical * (1+o) - committed)`; cap expected shortfall.

### 7.2 Memory / storage

**Q: Store 14 days × all stations in one Redis?**  
A: Shard; 56M keys OK distributed; not one instance.

**Q: Memory for geo index?**  
A: Keep station centroids in memory per region (~1M × 32 B ≈ 32 MB) + disk index.

**Q: Reservation row size?**  
A: ~500 B–1 KB; 200M active ≈ 100–200 GB — Dynamo territory.

**Q: Keep forever events?**  
A: Hot Kafka retention days; cold S3; analytics warehouse.

### 7.3 Databases

**Q: DynamoDB vs SQL for counters?**  
A: Dynamo scales per station PK; SQL OK baseline few K stations; hot rows hurt Postgres.

**Q: Single table design?**  
A: PK=station, SK types `META`, `COMP#id`, `CAP#size#date`, `RES#id` possible—but reservations also need global id lookup → separate table/GSI.

**Q: Redis alone as SoT?**  
A: Risky for confirmed customer promises; AOF still weaker ops story than Dynamo—use Redis acceleration.

**Q: Transactions?**  
A: Dynamo `TransactWriteItems` for counter + reservation insert; watch 100-item limits; keep scope one station.

**Q: GSI storm?**  
A: Sparse GSIs for `order_id`, `package_id`; avoid hot GSI PKs.

### 7.4 Indexing

**Q: Geo hash precision?**  
A: ~4–5 km cells for locker density; query 9 neighbors.

**Q: Index for sweeper?**  
A: `soft_expires_at` ordered set per shard or Dynamo TTL + streams; secondary index `state=SOFT AND expires_at < now`.

**Q: Query reservations by station/day?**  
A: GSI `station_id + pdd_date` for ops.

### 7.5 Load balancing

**Q: LB quote service?**  
A: Stateless horizontal; cache sticky optional; regional.

**Q: Hot station shard?**  
A: Isolate to fatter nodes; queue stow; don't put all stations' counters on few keys—already per station.

**Q: Consistent hashing stations to nodes?**  
A: Yes for stateful actors; virtual nodes; rebalance carefully with ownership transfer.

### 7.6 Hashing & IDs

**Q: reservation_id?**  
A: ULID/UUID; opaque.

**Q: Idempotency key design?**  
A: `order_id + package_id + action`; store mapping with TTL > max retry window.

**Q: Hash package to station?**  
A: Not for CX—customer chooses; hashing useful for internal test sharding only.

### 7.7 Concurrency

**Q: Two couriers stow two packages one door?**  
A: CAS on compartment state FREE→OCCUPIED with version; loser picks another door.

**Q: Soft reserve race sellable=1?**  
A: Conditional update; one wins; loser gets sold out → re-quote.

**Q: Confirm after soft expired?**  
A: Reject; client must new quote.

### 7.8 Expiration

**Q: DynamoDB TTL enough?**  
A: Eventually consistent expiry (up to 48h delay possible historically)—**not** sole mechanism for soft 15-min holds. Use sweeper + `expires_at` index for soft; TTL OK for cleanup of dead rows.

**Q: Pickup expiry?**  
A: Job schedules at `stow_time + sla`; notify T-24h; expire → ops task + counter release when physically cleared.

**Q: Who frees counter on expire?**  
A: Sweeper conditional transition; if already confirmed/stowed, no-op.

### 7.9 PDD & promise

**Q: PDD is a window not a date?**  
A: Bucket by earliest feasible date or by window id; be consistent; capacity for peak day in window.

**Q: Promise engine overbook vs locker overbook?**  
A: Separate layers; promise shouldn't sell locker without allocator ACK (or soft).

**Q: Weather delay storm?**  
A: Bulk replan API with rate limits; prioritize premium / perishable.

### 7.10 Cost & business

**Q: Is distance always primary?**  
A: No—near station with 40% stow fail may be worse than +2 km reliable station.

**Q: Charge customer for locker?**  
A: Product policy; allocator still internal cost even if free to customer.

**Q: Optimize courier route + locker?**  
A: Separate system; allocator exposes station capacity; routing consumes.

**Q: KPI for success?**  
A: Stow success %, redirect rate, utilization, pickup on-time %, support contacts / 1K deliveries.

### 7.11 Failure & CX

**Q: Code doesn't open?**  
A: Devices team; capacity remains OCCUPIED until cleared; support tools force release with audit.

**Q: Customer wants extend pickup?**  
A: Extend `pickup_expires_at` if policy; may cost turnover—limit extensions.

**Q: Station permanently closed with packages?**  
A: Ops workflow; reservations → FAILED; customer reship; capacity zeroed.

### 7.12 Scalability traps

**Q: Global lock for allocation?**  
A: No—station shard only.

**Q: Quote reads all stations worldwide?**  
A: Geo bound; k=20–50 max.

**Q: Materialize 365 days × 1M stations?**  
A: Wasteful; materialize horizon H (14–21); create buckets lazily on first sell.

### 7.13 Algorithms for upsizing starvation

**Q: How to avoid eating all XL?**  
A: Cap fraction of XL used as upsize; reserve contingency for true XL demand; price upsize cost high in score.

**Q: Protection inventory?**  
A: `sellable_upsize` vs `sellable_exact` pools—or dynamic threshold by forecast.

### 7.14 Comparison questions

**Q: vs hotel room allocation?**  
A: Similar date buckets; lockers add physical late bind + courier failure modes + mixed sizes.

**Q: vs airline overbooking?**  
A: Similar math; bump cost is redirect home / reattempt; CX sensitive similarly.

**Q: vs warehouse bin assignment?**  
A: Warehouse often early-binds bins; lockers prefer late bind due to customer pickup uncertainty.

### 7.15 Security & abuse

**Q: Hold all lockers via soft reserves?**  
A: Rate limit per customer; captcha/fraud; short TTL; max concurrent softs.

**Q: Enumerate reservation ids?**  
A: UUIDs; authz on read; pickup codes separate high-entropy.

### 7.16 Observability drills

**Q: Debug “capacity was free but reserve failed”?**  
A: Trace quote token time, cache staleness, concurrent sells, station offline flip, size mismatch.

**Q: Debug counter drift?**  
A: Recompute from reservations in HARD/SOFT + ledger FREE; show delta dashboard.

### 7.17 Consistency models

**Q: Read-after-write soft reserve for same session?**  
A: Yes—return reservation from write path; don't rely on cached sellable for that token.

**Q: Cross-region customer traveling?**  
A: Station home region owns capacity; quote RPC to home; latencies OK at human checkout.

### 7.18 Interview arithmetic traps

**Q: 5K quotes × 20 stations = ?**  
A: 100K counter reads/s.

**Q: 1M stations × 4 sizes × 14 days keys = ?**  
A: 56M keys.

**Q: Soft TTL sweep 2M / 15 min = ?**  
A: ~2.2K expiries/s average—not millions if uniform.

**Q: Claiming 0 redirects with 20% overbook?**  
A: Implausible; show expected shortfall.

### 7.19 Redis specifics

**Q: Lua vs WATCH/MULTI?**  
A: Lua atomic preferred for decr-if-positive.

**Q: Hot key single station counter?**  
A: One key per station×size×date is fine at station QPS (tens/sec); if needed split with hierarchical counters (rare).

**Q: Redis Cluster slot & station?**  
A: Hash tag `{station_id}size#date` to keep station keys co-located for multi-key lua if required.

### 7.20 Kafka / events

**Q: Why not sync HTTP only from locker?**  
A: Buffer through Kafka for retry, fanout to analytics/ops, replay after bugfix.

**Q: Ordering?**  
A: Per station partition; stow before pickup ordering matters; use state machine guards if out of order.

**Q: Exactly-once?**  
A: Idempotent consumers; don't promise magical EoS across all sinks.

### 7.21 Testing

**Q: Property tests?**  
A: Never negative sellable; conservation: free+soft+hard+occ+fault = physical.

**Q: Load test?**  
A: Hot station contention; quote cache stampede; sweeper backlog.

**Q: Chaos?**  
A: Kill Redis → degrade to Dynamo conditionals; kill sweeper → soft leak until restart (monitor).

### 7.22 Org / ownership

**Q: Who gets paged for Prime Day sold-out false positives?**  
A: Capacity platform if counter/cache bug; Ops if true demand; Promise if PDD bunching.

**Q: Feature toggle new cost model?**  
A: Shadow + canary; owner = capacity science; platform owns safety rails.

---

## 8. Appendices

### 8.1 Schema sketches

```text
DynamoDB Reservations
  PK: RES#<reservation_id>
  attrs: state, station_id, size, pdd_date, package_id, order_id,
         soft_expires_at, pickup_expires_at, compartment_id, version, idem_key
  GSI1: order_id → reservation_id
  GSI2: station_id + pdd_date
  GSI3: idem_key

DynamoDB StationLedger
  PK: STATION#<station_id>
  SK: COMP#<compartment_id>
  attrs: size, state, reservation_id, version

  SK: CAP#<size>#<date>
  attrs: sellable, soft, hard, occupied, version

  SK: META
  attrs: status, tz, overbook_cap, updated_at
```

```sql
-- admin/catalog (Aurora)
stations(station_id, geo, tz, status, address, ...)
compartment_templates(station_id, compartment_id, size)
policies(policy_id, weights_json, overbook_json, soft_ttl_sec, pickup_sla_hours)
```

### 8.2 State machine

```text
SOFT:
  confirm → HARD
  cancel/expire → EXPIRED (counter++)
HARD:
  stow_ok → OCCUPIED
  cancel → CANCELLED
  replan → HARD (new date) atomic move
  stow_fail → FAILED_STOW
OCCUPIED:
  pickup → COMPLETED (free door)
  pickup_expire → EXPIRED_OCCUPIED → (physical clear) FREE
```

### 8.3 Invariants tests

| Test | Assert |
|------|--------|
| Conservation | Per station size: free+soft+hard+occ+fault = physical |
| Conditional sell | Parallel N=sellable+10 reserves → successes == sellable (+overbook cap) |
| Idempotent soft | 100× same key → 1 row |
| Soft expire | After TTL, confirm fails; sellable restored once |
| Stow CAS | Two stows one door → one win |
| Offline | Quote excludes; existing OCCUPIED untouched |
| Replan | Old date hard--; new date hard++ atomic or compensate |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Size×date counters, soft/hard, late bind, sweeper, home fallback |
| 10× | Station sharding, Redis accel, quote cache, idempotent events |
| 100× | Regional cells, overbook caps, reconciliation, cost canaries |
| 1000× | Approx quotes, station actors, lazy calendars, learned risk |

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| PDD | Predicted / promised delivery date (station-local bucket) |
| Soft reserve | Short-lived checkout hold |
| Hard reserve | Committed allocation pre-stow |
| Late bind | Choose physical door at stow time |
| Upsize | Use larger compartment than minimum fit |
| Overbook | Sell > physical based on expected free-up |
| Sellable | Remaining allocatable units in bucket |
| Redirect | Fallback to home (or alternate) on failure |
| Drift | Counter vs ledger disagreement |

### 8.6 Estimation cheat-sheet

```text
Counter keys ≈ stations × sizes × horizon_days
Quote reads ≈ quote_qps × candidate_k
Soft expiry rate ≈ active_soft / soft_ttl_sec
Reservation storage ≈ active_res × 1KB
Never: one global SQL row for “all M lockers in US”
```

### 8.7 Cost score pseudocode

```text
def cost(station, size, needed, bucket, req):
  dist = haversine(req.geo, station.geo)
  upsize = SIZE_RANK[size] - SIZE_RANK[needed]
  p_fail = model.stow_fail(station, size, req.pdd)  # or historical
  o_risk = max(0, -bucket.sellable_physical_implied) * REDIRECT_COST
  return (
    W_DIST * dist +
    W_UP * upsize +
    W_FAIL * p_fail * REDIRECT_COST +
    W_OVER * o_risk +
    W_UTIL * utilization_penalty(bucket)  # optional prefer filling slow stations
  )
```

### 8.8 Atomic reserve pseudocode

```text
def soft_reserve(station, size, date, idem_key, ttl):
  if mapping.exists(idem_key): return mapping.get(idem_key)
  res_id = new_id()
  ok = counters.cond_decr_sellable(station, size, date)
  if not ok: raise SoldOut
  try:
    db.put_reservation(res_id, SOFT, expires=now+ttl, idem_key, ...)
    mapping.put(idem_key, res_id)
    return res_id
  except:
    counters.incr_sellable(...)  # compensate
    raise
```

Better: Dynamo transaction put+decr.

### 8.9 Reconciliation algorithm

```text
physical = count(ledger where status != FAULT/MAINT broken)
occ = count(OCCUPIED)
hard = count(res HARD for future dates...)  # careful multi-date
# For each date bucket:
#   committed = hard+soft for that date
#   sellable_target = overbook_adjust(physical - occ) - committed_other_dates_policy
# Compare to stored sellable; fix + alert if |delta| > ε
```

Document that multi-date sharing of physical pool is the subtle point: physical doors are shared across dates—**capacity is not independent per day**.

### 8.10 Shared pool vs per-day illusion (critical)

```text
Reality: 10 M doors today.
You cannot sell 10 for Monday and 10 for Tuesday as if 20 physical.
Model options:
  1) Single pool + expected occupancy curve by day (advanced)
  2) Conservative: sellable(day) based on forecast occupied that day
  3) Simple MVP: assume turnover — each day horizon uses forecasted free =
       physical - E[occupied(day)] - safety_stock
```

**Say this in interview:** date buckets must be tied to a forecast of physical free, not naive independent counters totaling > physical.

### 8.11 Interview “say this” (60 seconds)

> Station-sharded size×date sellable counters tied to forecasted free doors; soft then hard leases with durable reservations; late-bind compartments at stow with CAS; TTL sweepers; cost-ranked quotes with capped overbook; home-delivery fallback; reconcile drift; optimize redirect cost not vanity utilization.

### 8.12 Reliability test plan

1. Parallel reserve contention on sellable=1.  
2. Crash after counter decr before row write → compensate/rebuild.  
3. Duplicate stow events → one occupy.  
4. Soft TTL expiry vs confirm race → single winner.  
5. Station offline mid-checkout → reserve reject / home.  
6. PDD +2 days replan under load.  
7. Counter drift injection → reconciler fixes + alert.  

### 8.13 Observability SLOs

| SLO | Target |
|-----|--------|
| Quote p99 | < 200ms |
| Soft reserve p99 | < 150ms |
| Stow event apply p99 | < 300ms |
| Counter drift (p99 stations) | < 1 compartment-equivalent |
| Redirect-home rate | Below ops threshold (e.g. < 0.5%) |
| Soft leak (expired not freed in 60s) | ~0 |

### 8.14 API error codes

```text
200 OK
409 SOLD_OUT
409 STATE_CONFLICT      # confirm after expire
404 STATION_OFFLINE
404 RESERVATION_NOT_FOUND
422 PACKAGE_TOO_LARGE
503 CAPACITY_BACKEND_UNAVAILABLE  # client should offer home
```

### 8.15 Related systems map

```text
Checkout → Quote/Reserve → Promise(PDD)
                ↓
         Capacity Platform ← Locker Devices (telemetry)
                ↓
         Last Mile Courier App
                ↓
         Notifications / Support Tools / Finance KPIs
```

### 8.16 Policy knobs cheat-sheet

| Knob | Default sketch |
|------|----------------|
| soft_ttl | 15 min |
| pickup_sla | 72 h |
| horizon_days | 14 |
| candidate_k | 20 |
| max_upsize_steps | 1–2 |
| overbook_cap | 0–10% by station tier |
| quote_cache_ttl | 10 s |
| safety_stock | 1–2 per size |

### 8.17 FAQ quick hits

| Question | Answer |
|----------|--------|
| Bind door at checkout? | No (MVP) |
| Source of truth? | Reservation + ledger; counters derived/accelerated |
| Fail open invent capacity? | Never |
| Global TX? | No |
| Independent day counters sum > physical? | Design bug — use forecasted free |
| Primary KPI? | Redirect / failed stow cost + CX |

### 8.18 Worked numeric example

```text
Station S: 20M, 40L, 10XL (70 doors)
Forecast occupied on Thu: 25 doors mixed → free ≈ 45
Safety stock 5 → base_sellable_pool ≈ 40
Allocator distributes pool across sizes using composition forecast:
  e.g. sellable M Thu=18, L=16, XL=6 (sum 40)

Package needs M; sellable M=18 → offer M cost=1.2
If M=0 but L=16 → offer L cost=1.2 + upsize 0.15 + ...

Soft reserve M: sellable 18→17, soft++
Abandon: 15 min later sweeper 17→18
```

### 8.19 Extra Amazon leadership notes

- Write **runbooks** for stow-fail storms (disable overbook, freeze soft, prefer home).
- Show **cost of ownership**: who gets the ticket when counters drift.
- Prefer boring reliability over clever global optimization in a 45-minute interview.

---

*End of delivery locker capacity allocation system design.*
