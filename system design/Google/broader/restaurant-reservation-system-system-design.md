# System Design: Restaurant Reservation System

> **Focus areas:** Seat/table inventory · Availability search · Overbooking · Waitlist · Notifications · Multi-restaurant tenancy · Strong booking consistency  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct inventory math under concurrency, explicit hold→confirm→seat lifecycle, deal-breakers for “optimistic SQL UPDATE everywhere” fantasies  
> **Interview theme:** Classic Google L5+ marketplace inventory — ambiguous “table vs covers,” double-booking prevention, multi-tenant isolation, and flash dinner rushes

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

Goal: **bound the product**—a multi-restaurant **reservation platform** that answers “can I book N guests at restaurant R at time T?”, holds inventory safely under concurrency, supports waitlists and overbooking policy, and notifies guests/restaurants—without pretending every restaurant has identical seating models.

### 1.0 What this is / is not

| Dimension | **Restaurant reservation (this doc)** | Not this |
|-----------|---------------------------------------|----------|
| Primary job | Book covers/tables at a time slot with correctness | Full POS / kitchen display / menu CMS |
| Success | No double-book of scarce inventory; high confirm rate | Perfect real-time table turn prediction ML as MVP |
| Inventory | Soft blocks (holds) → hard bookings → seated/no-show | Infinite oversell without policy |
| Multi-tenant | Many restaurants, isolation + custom policies | Single famous restaurant only |
| Search | Availability by cuisine/geo/time/party size | Generic Yelp social graph |

**Scope statement:** Design a restaurant reservation system: availability, inventory (seats/tables), overbooking, waitlist, notifications, multi-restaurant tenancy—with progressive scale and explicit consistency for bookings.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Book what—tables or covers? | Both: capacity in **covers**; optional table assignment | Dual model: soft capacity + optional hard table map |
| F2 | Time granularity? | Slot every 15–30 min; duration by party size | Slot grid + duration rules |
| F3 | Hold vs confirm? | Soft hold 5–10 min then confirm (card/deposit optional) | Hold TTL + confirm API |
| F4 | Overbooking? | Restaurant-configurable % or never | Policy engine per restaurant |
| F5 | Waitlist? | Yes when full; auto-offer on cancel/no-show | Waitlist queue + notify |
| F6 | Multi-restaurant? | Marketplace: search across many | Tenant isolation; search index |
| F7 | Modifications / cancel? | Yes with cutoffs and fees | State machine + refund hooks |
| F8 | Notifications? | SMS/email/push for confirm, remind, waitlist offer | Async notify pipeline |
| F9 | Walk-ins? | Restaurant marks walk-in consuming inventory | Staff API / tablet |
| F10 | Deposits / payment? | Optional for premium; MVP can stub | Payment intent optional |
| F11 | Recurring / large parties? | Large parties special path; recurring out | Party size tiers |
| F12 | Admin / analytics? | Covers booked, no-show rate | Metrics + reporting store |

**MVP functional scope:**

1. Restaurant onboarding: hours, slot size, capacity (covers), optional floorplan tables.  
2. Guest search: by location/cuisine/time/party → availability.  
3. Hold inventory for TTL; confirm booking; cancel/modify within policy.  
4. Per-restaurant overbooking policy (off by default).  
5. Waitlist when unavailable; offer with short accept window.  
6. Notifications: confirm, reminder (T−24h, T−2h), waitlist offer, cancel.  
7. Staff ops: seat, no-show, walk-in, block times (private event).  
8. Multi-tenant auth: restaurant staff vs guest vs platform admin.

**Out of MVP:**

- Full POS / check payment / tip splitting  
- Dynamic pricing yield management (mention Phase 2)  
- Perfect ML turn-time prediction as sole inventory source  
- Social features (follow chefs, reviews beyond hooks)  
- Cross-city “dining experiences” marketplace extras

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Booking correctness | No silent double-book of same table/cover beyond policy | Strong consistency on inventory mutate |
| N2 | Hold fairness | Concurrent bookers don’t both confirm same seat | Conditional write / lock / compare-and-set |
| N3 | Search latency | Feels snappy | p99 < 200–300ms availability search |
| N4 | Confirm latency | Interactive | p99 < 500ms including inventory txn |
| N5 | Availability | Dinner rush critical | 99.9% booking API; degrade search cache OK |
| N6 | Notify reliability | Reminder delivery important | At-least-once + idempotent send |
| N7 | Multi-tenant isolation | Restaurant A never sees B’s PII/bookings | Tenant_id on every row + authz |
| N8 | Audit | Disputes (“I had a booking”) | Immutable booking event log |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Guest searches Sat 7pm party of 4 near SOMA → sees Restaurant X → hold → confirm → SMS.  
2. Guest cancels 6h before → inventory released → waitlist #1 gets offer → accepts → booked.  
3. Staff marks no-show after grace → inventory freed for walk-in / waitlist.  
4. Private event blocks 6–10pm → search shows unavailable.  
5. Overbooking 5% enabled → slight oversell; staff manages with bar seating.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two guests hold last table | Both may hold briefly if overbook policy; only one confirms if capacity=1; else CAS fails |
| Hold expires mid-checkout | Confirm rejected with `HOLD_EXPIRED`; restart search |
| Clock skew on slots | Server-authoritative slot IDs; never trust client “epoch” alone |
| Restaurant timezone DST | Store `tz` per restaurant; slots in local wall time + UTC instant |
| Payment fails after hold | Release hold; don’t leave orphan confirmed |
| Waitlist stampede on cancel | Serialize offers (one at a time) or short exclusive offer |
| Partial network retry confirm | Idempotency-Key → same booking_id |
| Floorplan table conflict | If hard-assigned, lock table_id; if soft covers, assign later |
| Party size 12 | Route to large-party workflow / manual approve |
| Multi-location brand | `brand_id` + `restaurant_id`; inventory per location |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Restaurants | 5K | 50K | 500K | 5M |
| Bookings / day | 200K | 2M | 20M | 200M |
| Peak confirm QPS | 100 | 1K | 10K | 100K |
| Search QPS | 2K | 20K | 200K | 2M |
| Slots queried / search | 20–50 | 50 | 50–100 | cached facets |
| Waitlist offers / day | 20K | 200K | 2M | 20M |
| Notify msgs / day | 1M | 10M | 100M | 1B |
| Geo markets | 20 | 50 | 200 | global |
| DB shards (booking) | 1–4 | 16–64 | 256+ | cell / market |

**What each jump forces:**

- **10×:** Shard by `restaurant_id`; search index (ES/OpenSearch) separate from booking OLTP; Redis for hot-slot counters.  
- **100×:** Market cells; read replicas for search facets; waitlist as queue service; notify via dedicated bus.  
- **1,000×:** Geo-partitioned cells; inventory in-memory / Spanner per cell; global search federated; no single booking DB.

### 1.5 Etc. (Constraints & Assumptions)

- Ambiguity to resolve early: **covers-only vs table assignment**. MVP: covers capacity with optional table map.  
- Restaurants own policy (overbook %, cancel cutoff); platform enforces.  
- Guests may be anonymous until confirm (email/phone).  
- “Availability” is approximate for browse; **authoritative on hold/confirm**.  
- Not designing full CRM/loyalty (hooks only).

**Scope statement to repeat back:**

> Design a multi-restaurant reservation platform that searches availability, holds and confirms cover/table inventory under concurrency, supports configurable overbooking and waitlists, notifies guests and staff, and scales from single-market OLTP to geo-partitioned cells—without double-booking beyond policy.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Search** | Availability browse | ~2K QPS | ~20K | Search index + cache |
| **Hold** | Soft inventory | ~150/s | ~1.5K | OLTP / Redis |
| **Confirm** | Hard booking | ~100/s | ~1K | Strong OLTP txn |
| **Cancel / modify** | Release | ~30/s | ~300 | OLTP + events |
| **Staff seat/no-show** | Ops | ~50/s | ~500 | OLTP |
| **Notify** | SMS/email/push | bursty | ×10 | Async bus |
| **Waitlist offer** | Serialize offers | low | higher | Queue + timer |

**Anti-pattern:** one “QPS” mixing CDN search and Spanner booking txns.

### 2.2 Inventory key cardinality

```text
Restaurants 5K × open 10h × slots/30min = 20 slots/day × 5K = 100K slot-days / day
With party-size buckets or tables: × ~10 → ~1M inventory keys / day active
At 5M restaurants: billions of historical keys → partition + TTL cold storage

Hot keys: popular restaurant Saturday 7–8pm (tiny keyspace, high contention)
```

### 2.3 Contention math (dinner rush)

```text
Famous restaurant: 80 covers, 2-hour turns, 7pm slot
Effective bookable parties ≈ 20 tables of 4
Concurrent browsers 5K, confirmers 50 in same 10s window
→ Need optimistic CAS or row lock on inventory row(s); not “read then write” app logic
```

### 2.4 Search amplification

```text
Search: 50 restaurants × 8 slots checked = 400 availability probes if naive
With precomputed availability bitmaps / counters per (restaurant, slot, party_bucket):
  1 index query + 50 doc fetches ≪ 400 OLTP reads
Never hit booking primary for every browse at 100×
```

### 2.5 Notification volume

```text
200K bookings/day × ~5 msgs (confirm, 2 reminders, thank-you, optional) ≈ 1M msgs/day
At 100×: 100M/day → dedicated notification service, templates, provider pools, suppress dupes
```

### 2.6 Storage

```text
Booking row ~1 KB; 200K/day × 365 × 3y ≈ 200GB hot-ish + indexes
Events log 5× → ~1TB / 3y baseline
PII: encrypt phone/email; retention policy
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/search?lat&lng&time&party&cuisine=` | Ranked restaurants + availability summary |
| `GET /v1/restaurants/{id}/availability?date&party` | Slot grid with remaining capacity |
| `POST /v1/holds` | `{restaurant_id, slot_start, party_size, Idempotency-Key}` → hold_id, ttl |
| `POST /v1/holds/{id}/confirm` | Guest info (+ payment) → booking_id |
| `POST /v1/bookings/{id}/cancel` | Policy-checked cancel |
| `PATCH /v1/bookings/{id}` | Modify time/party (re-inventory) |
| `POST /v1/waitlist` | Join waitlist for restaurant/time window |
| `POST /v1/waitlist/{id}/accept` | Accept offer |
| `POST /staff/restaurants/{id}/seat` | Mark seated |
| `POST /staff/.../noshow` | No-show + release |
| `POST /staff/.../blocks` | Private event blocks |
| `GET /v1/bookings/{id}` | Guest/staff view |

**Hold request schema:**

```text
HoldRequest {
  restaurant_id,
  slot_start_utc,
  duration_min,      // or derived
  party_size,
  table_pref?,       // outdoor, booth
  channel: "app"|"web"|"staff",
  idempotency_key
}
```

### 3.2 Data model

| Entity | Key | Notes |
|--------|-----|-------|
| Restaurant | `restaurant_id` | tz, geo, policies JSON |
| FloorplanTable | `(restaurant_id, table_id)` | capacity min/max, joinable |
| InventorySlot | `(restaurant_id, slot_start)` | `capacity`, `booked`, `held`, `overbook_limit` |
| Hold | `hold_id` | ttl, party, slot, status |
| Booking | `booking_id` | confirmed; FK restaurant; state |
| WaitlistEntry | `waitlist_id` | priority, window, status |
| BookingEvent | `(booking_id, version)` | append-only audit |
| Block | `(restaurant_id, range)` | private events |

**State machine (booking):**

```text
HELD → CONFIRMED → SEATED → COMPLETED
                 ↘ CANCELED
CONFIRMED → NO_SHOW
HELD → EXPIRED
WAITLISTED → OFFERED → ACCEPTED→CONFIRMED | LAPSED
```

### 3.3 Inventory model — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Covers counter only** | Simple; flexible seating | May over-assign uncombinable tables | MVP default |
| **Hard table assignment at book** | Exact physical plan | Fragmentation; lower utilization | Fine dining |
| **Covers now, assign at seat** | Best utilization | Guest can’t pick table early | High-volume |
| **Combinable table graph** | Optimal packing | NP-hard-ish; complex | Phase 1.5 for premium |

**Chosen MVP:**

1. **Primary inventory:** `(restaurant_id, slot_start)` covers: `remaining = capacity + overbook_allowance - booked - held`.  
2. Optional **table constraints**: filter by max table size / outdoor count as secondary counters.  
3. **Assignment:** best-effort at confirm or at seat time.  
4. **Deal-breaker:** assigning overlapping times to same `table_id` without exclusion.

### 3.4 Concurrency — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **DB row lock / txn** | Correct | Hot row contention | Single popular restaurant |
| **Optimistic CAS version** | Scalable enough | Retry UX | **Strong MVP** |
| **Redis DECR with TTL holds** | Fast | Dual SoT risk | Cache of counters + async reconcile **careful** |
| **Spanner / TrueTime txn** | Global strong | Cost/complexity | Multi-region 100× |
| **Ignore races** | — | Double book | **Deal-breaker** |

**Chosen:** OLTP transactional CAS on inventory row(s); Redis optional for browse counters (eventually consistent); **confirm always hits source of truth**.

### 3.5 Overbooking & waitlist

```text
overbook_limit = floor(capacity * policy.overbook_pct)  // e.g. 0.05
max_sellable = capacity + overbook_limit
can_hold(party) iff held + booked + party <= max_sellable
  AND secondary constraints (outdoor, etc.)

Waitlist:
  on cancel/no-show/expire → enqueue offer to next eligible entry
  offer_ttl 5–15 min exclusive OR parallel with accept races (prefer exclusive)
```

**Deal-breaker:** overbooking without restaurant-visible risk dashboard / staff tools.

### 3.6 Search architecture

```text
Browse path (approx OK):
  Geo index → candidate restaurants → cached availability digests
Confirm path (authoritative):
  Hold/Confirm services → Booking DB
```

### 3.7 Why X over Y (summary table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Inventory SoT | OLTP booking DB | Strong correctness | Search index as inventory authority |
| Browse availability | Precomputed digests | QPS | Per-search lock inventory |
| Hold | Soft with TTL | Checkout UX | Infinite soft holds |
| Multi-tenant key | `restaurant_id` shard | Isolation + locality | Global unpartitioned bookings table |
| Notify | Async outbox | Don’t block confirm | Sync SMS in DB txn |
| Waitlist | Exclusive offer | Fairness | Blast all waitlisters same seat |

---

## 4. Architecture Diagram

```text
                 +------------------+
  Guests ------> |  Edge / API GW   |
  Staff  ------> |  AuthZ           |
                 +--------+---------+
                          |
        +-----------------+------------------+
        |                 |                  |
        v                 v                  v
 +-------------+  +--------------+   +---------------+
 | Search Svc  |  | Booking Svc  |   | Staff Ops Svc |
 | (approx)    |  | hold/confirm |   | seat/noshow   |
 +------+------+  +------+-------+   +-------+-------+
        |                |                   |
        v                v                   v
 +-------------+  +--------------+   +---------------+
 | OpenSearch  |  | Booking OLTP |   | same OLTP     |
 | + Redis     |  | (sharded)    |   |               |
 | avail cache |  | + outbox     |   |               |
 +-------------+  +------+-------+   +---------------+
                         |
                         | events
                         v
              +----------+-----------+
              | Kafka / PubSub       |
              | booking.events       |
              +----+----------+------+
                   |          |
                   v          v
           +-----------+  +-------------+
           | Notify    |  | Search      |
           | Service   |  | Indexer     |
           +-----------+  +-------------+
                   |
                   v
           SMS / Email / Push
```

**Hold → Confirm path:**

```text
POST /holds
  -> validate restaurant open + party rules
  -> BEGIN TXN
       read InventorySlot WHERE restaurant_id, slot FOR UPDATE / CAS version
       if remaining >= party: held += party; insert Hold(ttl)
  -> COMMIT
  -> return hold_id, expires_at

POST /holds/{id}/confirm
  -> BEGIN TXN
       validate hold active
       held -= party; booked += party
       insert Booking CONFIRMED
       outbox NotifyConfirm
  -> COMMIT
  -> idempotent on Idempotency-Key
```

**Cancel → Waitlist path:**

```text
Cancel booking
  -> booked -= party
  -> emit InventoryFreed
  -> Waitlist Worker: pick FIFO/priority next
  -> create exclusive Offer(ttl)
  -> notify guest
  -> on accept: hold+confirm fast path or direct confirm
```

**Search path:**

```text
GET /search
  -> geo filter candidates (index)
  -> join cached AvailabilityDigest (bitmap / min party remaining)
  -> rank (distance, rating, availability)
  -> NOT an inventory lock
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **For any slot:** `booked + held ≤ capacity + overbook_allowance` (enforced in txn).  
2. **Confirmed booking** always has matching `booked` increment (or compensating event).  
3. **Hold expiry** releases `held` exactly once (idempotent sweeper).  
4. **Idempotency-Key** on confirm → at-most-one booking.  
5. **Tenant isolation:** every query constrained by `restaurant_id` + authz.  
6. **Notify-at-least-once** with dedupe key `(booking_id, template_id)`.

#### 5.1.2 Hold expiry

```text
Options:
A) TTL field + periodic sweeper (every 10s) — simple
B) Delay queue (Kafka/Cloud Tasks) per hold — precise
C) Redis EXPIRE callback — fast but dual SoT

MVP: B with sweeper backup
Sweeper SQL: UPDATE holds SET status=EXPIRED WHERE expires_at < now() AND status=HELD
             then decrement inventory held (CAS)
```

**Deal-breaker:** expired holds that never release inventory (“leaked seats”).

#### 5.1.3 Dual-write search vs OLTP

| Pattern | Notes |
|---------|-------|
| Outbox → indexer | Booking DB commit includes outbox row; publisher drains |  
| Digest recompute | Nightly full + incremental on events |  
| Drift repair | Periodic reconcile job counts vs digests |

Browse may show “available” that fails on hold → UX: “just taken, pick another.”

#### 5.1.4 Payment + booking atomicity

```text
If deposits required:
  1) hold inventory
  2) create payment intent
  3) on payment success webhook: confirm (idempotent)
  4) on fail/timeout: release hold
Never confirm before payment auth when policy requires deposit
```

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Hot restaurant row | Fine-grained slot rows; short txns |
| 10× | Sweeper lag | Partition sweepers by restaurant hash |
| 100× | Cross-region latency | Market-local booking cells |
| 1,000× | Search drift | Cell digests + chaos reconcile |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| Shard bookings by `hash(restaurant_id)` | All inventory for a restaurant co-located |
| Search index by geo shards / markets | Local queries |
| Notify by region providers | Compliance + throughput |
| Waitlist by `restaurant_id` | Fair local queues |

**Never shard a single restaurant’s slot inventory across DBs** — breaks txn atomicity.

#### 5.2.2 Hot restaurant pattern

```text
Restaurant R Saturday 7pm is hot:
  - Inventory row(s) under high CAS contention
  - Mitigate: shard by slot_start (already); optional party-size buckets
  - In-memory inventory service for VIP restaurants (sticky) with WAL to DB
  - Request coalescing on availability GET
```

#### 5.2.3 Availability digest

```text
AvailabilityDigest[restaurant][date] = {
  slots: [{start, remaining_covers, max_party_ok}]
  version
}
Update on every confirmed/cancel/hold change (async)
Browse reads digest; Hold reads OLTP
```

#### 5.2.4 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Shard OLTP; Redis digests; OpenSearch; outbox |
| →100× | Market cells; waitlist service; notify fleet; hot in-mem inventory |
| →1,000× | Global cell fabric; federated search; Spanner/cell CQRS; edge digests |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
restaurant.policies: {
  slot_minutes: 15,
  default_duration: {2:90, 4:105, 6:120},
  hold_ttl_sec: 600,
  overbook_pct: 0.0,
  cancel_cutoff_hours: 2,
  waitlist_offer_ttl_sec: 600,
  noshow_grace_min: 15
}
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `hold_success_rate` | UX / contention |
| `confirm_cas_retries` | Hotspot |
| `inventory_leak_suspect` | held stuck |
| `search_hold_mismatch` | digest drift |
| `waitlist_offer_accept_rate` | fairness/product |
| `notify_delivery_latency` | reminders |
| `noshow_rate` | overbook tuning |

#### 5.3.3 Testing

- Concurrent hold stress on last seat (property: ≤ max_sellable confirms).  
- Hold expiry race with confirm.  
- Idempotent confirm replay.  
- DST slot generation.  
- Tenant isolation authz tests.  
- Waitlist exclusive offer races.

#### 5.3.4 Operability

- Shadow digests vs OLTP.  
- Feature flag overbook %.  
- Replay booking.events to rebuild digests.  
- Admin “force release hold.”

---

## 6. Wrap-Up

### 6.1 What we designed

A **multi-restaurant reservation platform** with approximate browse availability, strongly consistent hold/confirm inventory (covers + optional tables), configurable overbooking, waitlist offers, async notifications, and scale via `restaurant_id` sharding → market cells—not a single global SQL table with optimistic app-level checks.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Browse vs book | Approx digest vs authoritative txn |
| Covers vs tables | Covers MVP; tables for fine dining |
| Overbook | Policy-gated; staff-visible |
| Holds | TTL + idempotent expire |
| Search SoT | Never |
| Shard key | `restaurant_id` |

### 6.3 30-second scale narrative

> Baseline: sharded OLTP for holds/confirms, Redis/OpenSearch digests for search, outbox to notify and index. 10× forces digest caches and hot-row discipline. 100× splits market cells and dedicated waitlist/notify. 1,000× is geo cell fabric with federated search—correctness always on the booking txn, never on the search index.

### 6.4 Deal-breakers checklist

- Search index as inventory authority.  
- Confirm without idempotency.  
- Leaking expired holds.  
- Unpartitioned global bookings hot table.  
- Waitlist stampede confirming same seat N times.  
- Ignoring restaurant timezone/DST.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Table vs covers—what do you pick in interview?**  
A: State ambiguity; propose covers + optional table map; ask which restaurants need hard assignment.

**Q2: How long is a reservation?**  
A: Duration by party size and restaurant type; blocks consecutive slots.

**Q3: Do you support bar vs dining room?**  
A: Separate inventory pools / sections.

**Q4: Experiences / prix-fixe seatings?**  
A: Special event SKUs with fixed capacity—like blocks.

**Q5: Guest no account?**  
A: Book with phone/email; link account later.

### 7.2 Consistency & inventory

**Q6: How do you prevent double booking?**  
A: Transactional CAS/lock on inventory row; check `booked+held+party ≤ max_sellable`.

**Q7: Why holds?**  
A: Checkout time; payment; reduce abandon burning inventory—TTL critical.

**Q8: Optimistic vs pessimistic?**  
A: Either works; discuss retry UX and deadlock; Spanner/serializable also fine.

**Q9: Can Redis be SoT?**  
A: Risky dual write; possible with careful WAL/single writer per restaurant; prefer DB SoT at L5 unless justifying in-mem cell.

**Q10: Read-your-hold?**  
A: Confirm must read same shard/primary; session stickiness optional.

### 7.3 Overbooking & yield

**Q11: How to set overbook %?**  
A: Historical no-show rate with safety margin; start 0; staff override.

**Q12: Overbook + waitlist interaction?**  
A: Overbook sells ahead; waitlist fills releases; don’t double-count.

**Q13: Large party blocks many 2-tops?**  
A: Combinable tables or section capacity; fragmentation problem—call out.

### 7.4 Waitlist

**Q14: FIFO or priority?**  
A: Product: VIP, party-size fit, loyalty; document fairness.

**Q15: Exclusive offer vs blast?**  
A: Exclusive reduces double accept; slightly lower fill rate.

**Q16: Offer expires?**  
A: Short TTL; cascade to next.

### 7.5 Search

**Q17: Why not query OLTP for search?**  
A: QPS and lock contention; digests/index for browse.

**Q18: Ranking signals?**  
A: Distance, availability, rating, commission (disclose ethically), historical conversion.

**Q19: Stale “available”?**  
A: Accept; hold fails gracefully; refresh digest ASAP.

### 7.6 Notifications

**Q20: Reminder storm?**  
A: Schedule relative to `slot_start`; cancel on cancel event; idempotent keys.

**Q21: SMS cost at 1,000×?**  
A: Prefer push; SMS for high-value; region providers; quiet hours.

### 7.7 Multi-tenant & security

**Q22: Isolation?**  
A: `tenant_id`/`restaurant_id` on rows; authz middleware; no cross-tenant queries.

**Q23: Staff roles?**  
A: Owner, manager, host; scoped tokens.

**Q24: PII?**  
A: Encrypt; minimize; retention; GDPR delete → tombstone booking stats.

### 7.8 Estimation drills

**Q25: Hot row QPS?**  
A: Single restaurant 7pm may see tens of confirms/s; design short txns + maybe in-mem.

**Q26: Digest size?**  
A: 5K restaurants × 30 days × 20 slots × 8B ≈ tens of MB—fine in Redis cluster.

**Q27: Shard count at 500K restaurants?**  
A: 256–1024 shards; restaurants per shard ~500–2K.

### 7.9 Alternatives & deal-breakers

**Q28: Only calendar SaaS per restaurant?**  
A: Doesn’t give marketplace search/waitlist platform.

**Q29: Event sourcing only?**  
A: Great audit; still need strong snapshot for inventory speed.

**Q30: Microservices per entity prematurely?**  
A: Start modular monolith for booking+inventory; split notify/search early.

### 7.10 Interview craft

**Q31: How to open?**  
A: Clarify covers vs tables, hold TTL, overbook, waitlist, multi-restaurant, consistency bar.

**Q32: What impresses L5+?**  
A: Browse/book split, CAS invariants, leaked-hold story, shard-by-restaurant, waitlist fairness, progressive cells.

**Q33: Common mistake?**  
A: Treating availability search as source of truth; ignoring TTL holds; ignoring timezones.

---

### Appendix A — Inventory CAS pseudocode

```text
def try_hold(rest, slot, party, ttl, idemp):
  if seen(idemp): return prior
  txn:
    inv = get(rest, slot)
    if inv.booked + inv.held + party > inv.capacity + inv.overbook:
      abort FULL
    inv.held += party
    inv.version += 1
    put Hold(id, exp=now+ttl, party, version_seen=inv.version)
  return Hold
```

### Appendix B — Confirm pseudocode

```text
def confirm(hold_id, guest, idemp):
  txn:
    h = get_hold(hold_id)
    if h.status != HELD or h.expired: abort
    inv = get(h.rest, h.slot)
    inv.held -= h.party
    inv.booked += h.party
    b = insert Booking(CONFIRMED, ...)
    h.status = CONVERTED
    outbox(NotifyConfirm, b.id)
  return b
```

### Appendix C — Slot generation

```text
for date in range:
  local_open, local_close = hours(rest, date)
  t = local_open
  while t + min_duration <= local_close:
    emit slot(utc(t, rest.tz))
    t += rest.slot_minutes
handle DST by using timezone library, not fixed offsets
```

### Appendix D — Table packing (Phase 1.5)

```text
Tables with capacity; joinable edges
Bin-pack parties into tables minimizing waste
NP-hard → heuristics: best-fit decreasing; reserve large tables for large parties
```

### Appendix E — Waitlist worker

```text
on InventoryFreed(rest, slot, covers):
  while covers > 0:
    e = next_waitlist(rest, slot_window, party<=covers)
    if not e: break
    offer(e, ttl)
    wait accept or lapse
    if accepted: covers -= e.party
```

### Appendix F — Outbox pattern

```text
txn:
  mutate booking
  insert outbox(payload, topic)
publisher:
  poll outbox -> Kafka -> mark published
```

### Appendix G — Availability digest

```text
digest[rest][date].slots[i].remaining =
  capacity + overbook - booked - held
version++
index document: {rest_id, geo, next_available, rating}
```

### Appendix H — Progressive scale table

| Scale | OLTP | Search | Notify | Hot path |
|-------|------|--------|--------|----------|
| Baseline | 1–4 shards | OpenSearch | 1 worker pool | DB CAS |
| 10× | 64 shards | + Redis digest | bus | retries |
| 100× | market cells | federated | multi-provider | in-mem VIP |
| 1,000× | cell fabric | edge facets | global notify | cell-local |

### Appendix I — Booking JSON

```json
{
  "booking_id": "b_123",
  "restaurant_id": "r_9",
  "slot_start": "2026-08-09T02:00:00Z",
  "party_size": 4,
  "status": "CONFIRMED",
  "guest": {"phone_hash": "..."},
  "version": 3
}
```

### Appendix J — NFR card

```text
booked+held <= capacity+overbook (invariant)
confirm p99 < 500ms
search p99 < 300ms
hold TTL enforced
idempotent confirm
tenant isolation
```

### Appendix K — Failure UX

| Failure | UX |
|---------|-----|
| FULL on hold | Show alternatives nearby/time |
| HOLD_EXPIRED | Restart hold |
| PAYMENT_FAILED | Seats released; retry |
| OFFER_LAPSED | Back to waitlist position policy |

### Appendix L — Geo search

```text
geohash / S2 cells -> candidate ids
filter open_now / cuisine
sort distance + availability_score
```

### Appendix M — No-show handling

```text
at slot_start + grace:
  if not SEATED: mark NO_SHOW
  release remaining time inventory optional
  feed overbook model
```

### Appendix N — Multi-restaurant brand

```text
brand_id
  restaurant_id (location)
inventory always at restaurant_id
search may group by brand
```

### Appendix O — Comparison: covers vs tables

| Property | Covers | Tables |
|----------|--------|--------|
| Utilization | Higher | Lower if rigid |
| Correctness complexity | Medium | High |
| Guest preference | Weak | Strong |
| MVP | Yes | Optional |

### Appendix P — Security

| Threat | Control |
|--------|---------|
| Enumerate bookings | opaque IDs + auth |
| Staff cross-tenant | authz checks |
| Hold hoarding | per-user hold caps |
| Scraping availability | rate limits |

### Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Cover | One guest seat |
| Hold | Soft reservation with TTL |
| Overbook | Sell above physical capacity |
| Digest | Cached availability summary |
| Offer | Exclusive waitlist chance |

### Appendix R — Worked example

```text
Rest capacity 80 covers, overbook 5% → max 84
held 10, booked 70 → remaining 4
Party 5 → FULL
Cancel party 4 → booked 66 → waitlist party 4 offered
```

### Appendix S — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Is search strongly consistent? | No |
| Is confirm? | Yes on shard primary |
| Cross-restaurant atomic book? | Not required |
| Reminder after cancel? | Suppress via event |

### Appendix T — 30m interview checklist

1. Clarify covers/tables, hold, overbook, waitlist, multi-tenant.  
2. Split browse vs book load.  
3. Draw API + OLTP + search + outbox + notify.  
4. Deep dive CAS inventory + expiry.  
5. Waitlist fairness.  
6. Walk 10×/100×/1,000×.  
7. Deal-breakers.

### Appendix U — Modify booking

```text
modify(party', slot'):
  txn:
    release old inventory
    acquire new inventory
    if fail: abort keep old
    version++
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Shards, digests, OpenSearch |
| 100× | Market cells, waitlist svc |
| 1,000× | Cell fabric, federated search |

---

*End of Restaurant Reservation System system design.*
