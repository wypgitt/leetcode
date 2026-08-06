# System Design: OpenTable / Restaurant Reservations (Microsoft Interview Practice)

> **Focus areas:** Inventory of time slots · Double-booking prevention · Search / discovery · Holds & checkout · Waitlist · Restaurant ops · Consistency · Peak dinner rushes  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct slot inventory math, explicit locking/hold semantics, deal-breakers for “read available then write reservation without fencing,” honest search-vs-booking plane split  
> **Interview theme:** Microsoft loop (team may ask domain problems) — reservations exercise inventory contention, idempotency, and geo search; frame like a careful commerce/booking platform

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

Goal: **bound the product**—an OpenTable-class restaurant reservation marketplace: diners search restaurants, check availability for party size + time, place reservations without double-booking, manage cancels, and restaurants manage floor inventory / shifts. Optional waitlist and deposits.

### 1.0 What this is / is not

| Dimension | **Restaurant reservations (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Book scarce table-time inventory | Full POS / kitchen display deep dive |
| Success | No double books; fast search; reliable holds | Perfect global dining ML |
| Inventory | Slots / tables / party-size capacity | Airline seat maps identical (related ideas) |
| Payments | Optional deposit / no-show fee hooks | Full restaurant payroll |
| Delivery | Out of scope | Food delivery matching |
| Microsoft lens | Strong correctness, APIs, ops | Azure-only requirement |

**Scope statement:** Design OpenTable-like discovery + reservation booking with conflict-free inventory, holds, cancels, and restaurant management—scaled through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Actors? | Diners + restaurants (managers/hosts) | Two portals + roles |
| F2 | Search? | By city/neighborhood, cuisine, time, party size | Search index + availability overlay |
| F3 | Availability? | Slots for a date/time window | Inventory service |
| F4 | Book? | Reserve under name/phone/email | Booking txn + confirmation |
| F5 | Party size? | Affects which tables fit | Table combination / capacity model |
| F6 | Cancel / modify? | Yes with policies | State machine + release inventory |
| F7 | Holds? | Soft hold during checkout (e.g. 3–5 min) | Hold TTL + fencing token |
| F8 | Waitlist? | Phase 1.5 | Queue when full |
| F9 | Deposits / cards? | Optional Phase 1.5 | Payment hold hook |
| F10 | Restaurant admin? | Hours, tables, shifts, block times | Inventory config |
| F11 | Notifications? | Email/SMS confirm / remind | Notif service |
| F12 | Reviews? | Light MVP or Phase 1.5 | Separate |
| F13 | Experiences / events? | Out of MVP | Special inventory types |
| F14 | Walk-ins? | Host marks seated; reduces inventory | Ops API |

**MVP functional scope:**

1. Restaurant profile + table/slot configuration for service periods.  
2. Diner search by geo + filters (cached metadata).  
3. Availability query for restaurant + date + party size.  
4. Hold → confirm reservation (atomic inventory decrement).  
5. Cancel / modify with re-availability.  
6. Confirmations + reminders.  
7. Host view: upcoming covers; mark seated / no-show.  
8. Prevent double-booking under contention.

**Out of MVP:**

- Full multi-property custom CRM  
- Dynamic pricing optimization research  
- Table-side POS integration deep  
- Global waitlist ML seating oracle  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Booking correctness? | No double book | Strong invariant on inventory |
| N2 | Search latency? | Snappy | p99 < 200–300ms |
| N3 | Availability latency? | Interactive | p99 < 100–200ms |
| N4 | Hold→book? | Reliable | Idempotent; no lost holds |
| N5 | Availability? | High for dinner peak | 99.9%; degrade search ranking first |
| N6 | Consistency? | Booking strong; search eventual OK | See §3.8 |
| N7 | Scale? | Many restaurants globally | Shard by region / restaurant |
| N8 | Security? | PII of diners | Encrypt; least privilege |
| N9 | Audit? | Disputes / no-shows | Event log |
| N10 | Maintainability? | Clear planes | Search vs Inventory vs Booking |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Search “Italian Seattle 7pm party of 2” → results with availability badges.  
2. Select restaurant → see slot grid → hold 7:00pm → confirm → email.  
3. Cancel 24h prior → inventory released → another diner books.  
4. Host marks party seated → reservation completed.  
5. Restaurant blocks private event → slots removed from sale.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two diners confirm same last slot | One wins; other gets conflict + alternatives |
| Hold expires mid-form | UX refresh; re-hold |
| Double-click confirm | Idempotency-Key → one reservation |
| Party size 6 with only 2-tops | Table combine rules or reject |
| Timezone / DST | Store restaurant local TZ; UTC internally |
| No-show | Mark; optional fee; analytics |
| Overbook policy | Some restaurants allow controlled overbook % — explicit config |
| Search shows slot just taken | Availability eventual; confirm is source of truth |
| Restaurant connectivity offline | Local host mode Phase 1.5; cloud remains SoT for online book |
| Partial modify (time change) | Transactional release+reacquire or cancel+book |
| Blackout / holiday hours | Inventory generation skips |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Restaurants | 50K | 500K | 5M | 50M |
| MAU diners | 20M | 200M | 2B | extreme |
| Peak availability QPS | 20K | 200K | 2M | 20M |
| Peak booking confirm QPS | 500 | 5K | 50K | 500K |
| Reservations / day | 2M | 20M | 200M | 2B |
| Search QPS peak | 30K | 300K | 3M | 30M |
| Avg tables / restaurant | 20 | 20 | 20 | 20 |
| Slot granules | 15 min | 15 | 15 | 15 |

**What each jump forces:**

- **10×:** Separate search index vs booking DB; Redis holds; sharded inventory.  
- **100×:** Region cells; precomputed availability documents; read replicas; waitlist service.  
- **1,000×:** Per-restaurant partitions; edge caches for search; careful hot restaurant isolation (viral TikTok spot).

### 1.5 Etc. (Constraints & Assumptions)

- MVP models inventory as **bookable slots with capacity** (covers or table IDs)—start simple, mention table-combine as extension.  
- Search can be slightly stale; **confirm path never trusts search alone**.  
- Dinner peaks are spiky (Thu–Sat evenings).  
- Microsoft interviewers often compare this to ticket booking / hotel inventory—lean into **hold + commit**.

**Scope statement to repeat back:**

> Design OpenTable-like reservations: geo/cuisine search, availability for party size and time, TTL holds, atomic confirmations without double-booking, cancels, and restaurant ops—scaling search and inventory as separate planes, with strong fencing on the book path.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Peak baseline | Plane |
|-------|---------------|-------|
| Search | 30K QPS | Search index |
| Availability grid | 20K QPS | Inventory read models |
| Hold | 2K QPS | Inventory + Redis |
| Confirm | 500 QPS | Durable booking txn |
| Admin/ops | low | Config |
| Notifications | async | Notif |

**Critical insight:** Confirm QPS is tiny vs search, but **contention** on hot restaurants is the correctness challenge.

### 2.2 Inventory cardinality

```text
50K restaurants × 20 tables × (12 bookable hours/day × 4 slots/hour) 
  ≈ 50K × 20 × 48 ≈ 48M slot-table cells / day if naïvely materializing every table×slot

Smarter: materialize service periods + capacity pools
  50K × ~20 slots/evening × a few party-size buckets ≪ table×slot explosion

Still: availability docs per restaurant-day are the unit
50K restaurants × 1 hot day × ~1–5 KB compressed availability ≈ 50–250 MB — cacheable
```

### 2.3 Hot restaurant math

```text
Viral restaurant: 1 reservation every few seconds at open window
Or: 10K users refresh availability at 7:00 booking open (ticket-style)

Need:
  - cached availability reads
  - single-threaded or strongly consistent commit per inventory key
  - holds with TTL to avoid abandoned carts locking inventory forever
```

### 2.4 Hold economics

```text
Hold TTL = 3 minutes
If abandoned holds common, capacity looks lower than reality
Metrics: hold→confirm conversion; expire rate
Too long TTL → inventory starvation
Too short → UX rage
```

### 2.5 Storage

```text
2M reservations/day × 500 B ≈ 1 TB/year raw metadata
PII fields encrypted / tokenized
Events (audit) similar order
```

### 2.6 Search index size

```text
50K restaurant docs × 2 KB ≈ 100 MB — tiny
100× → 5M docs ≈ 10 GB + geo indices — still fine for ES/OpenSearch/Cognitive Search class
```

### 2.7 Peak dinner spike

```text
Assume 40% of daily bookings in 3 peak hours
2M/day → ~800K in 3h → ~75/s average; peak 5–10× in popular metros → hundreds/s confirms globally
Single hot venue still dominates local locks
```

### 2.8 Amplification

| Naive | Problem | Fix |
|-------|---------|-----|
| Search hits booking DB | Melt | Denormalized search + async availability badges |
| Check-then-book without txn | Double book | Conditional update / serializable slot row |
| Lock whole restaurant | Low concurrency | Lock slot bucket / table resource |
| Materialize all table×slot forever | Huge | Generate windows; capacity pools |

### 2.9 Progressive implications

| Concern | Baseline | 10× | 100× | 1,000× |
|---------|----------|-----|------|--------|
| Booking DB | Primary + replicas | shard by region | shard by restaurant_id | cells |
| Holds | Redis | clustered | per cell | hot-key isolation |
| Search | ES cluster | geo partitions | multi-region | edge cache |
| Availability | on read compute | precompute docs | push updates | incremental |

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
DINER                                   RESTAURANT HOST
+-----------------------------+         +--------------------------+
| Find: Seattle · 7:00 · 2    |         | Tonight · Floor          |
| [Map] list of restaurants   |         | 6:30 Smith 2 · seated    |
| Contoso Bistro  ★4.5        |         | 7:00 Lee 4 · confirmed   |
| 6:30  7:00  7:30            |         | Walk-in [+]  Block [+]   |
| [Hold 7:00] → details form  |         |                          |
| [Confirm reservation]       |         |                          |
+-----------------------------+         +--------------------------+
```

### 3.2 Inventory modeling options

| Model | Description | Pros | Cons | When |
|-------|-------------|------|------|------|
| **A. Capacity pool** | Each slot has `remaining_covers` | Simple | Weak table constraints | MVP |
| **B. Table objects** | Each table bookable; combine for parties | Realistic | Combinatorial | Better |
| **C. Hybrid (chosen)** | Pools by party-size band + optional table assign at seat | Practical | Assign complexity | **Choose** |

**MVP Hybrid:**

```text
For each restaurant, service, date, slot_time:
  inventory_units[party_band] = remaining reservations count
  OR remaining_covers with max_party rules

On confirm(party_size):
  decrement matching band if remaining > 0 (atomic)
Host seating later maps to physical tables (ops)
```

Mention full table-combine solver as Phase 1.5 for fine dining.

### 3.3 Domain model

```text
Restaurant
  ├── Location, cuisine, price_tier, TZ
  ├── Services (lunch/dinner hours)
  ├── InventoryConfig (slots, capacity, overbook_pct)
  └── Tables[] (ops)

Reservation
  ├── reservation_id, restaurant_id, diner_id
  ├── slot_start, party_size, state
  ├── hold_id?, version
  └── contact PII refs

Hold
  ├── hold_id, resource_key, expires_at, token
```

**Reservation states:**

```text
HELD → CONFIRMED → SEATED → COMPLETED
                 ↘ CANCELED
                 ↘ NO_SHOW
HELD → EXPIRED
```

### 3.4 API shape

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/search` | Restaurant search |
| GET | `/v1/restaurants/{id}` | Profile |
| GET | `/v1/restaurants/{id}/availability` | Slot grid |
| POST | `/v1/holds` | Create hold |
| POST | `/v1/reservations` | Confirm (idempotent) |
| DELETE | `/v1/reservations/{id}` | Cancel |
| PATCH | `/v1/reservations/{id}` | Modify |
| GET | `/v1/restaurants/{id}/bookings` | Host list |
| POST | `/v1/restaurants/{id}/blocks` | Block inventory |
| POST | `/v1/reservations/{id}/seat` | Mark seated |

### 3.5 Architecture options

| Option | Idea | Verdict |
|--------|------|---------|
| **A. Monolith SQL check-then-insert** | Racey under concurrency | Reject without row locks / constraints |
| **B. Eventual booking** | Conflict later | Bad UX for restaurants |
| **C. Hold service + atomic inventory + search plane (chosen)** | Correct + scalable reads | **Choose** |

**Deal-breakers:**

- Believing search availability is authoritative  
- No TTL on holds  
- Wide table locks for entire venue on every book  

### 3.6 Component architecture

```text
Diner / Host clients
        |
   API Gateway
        |
   +----+----+-----------+------------+
   v         v           v            v
Search    Availability  Hold/Book    Restaurant
Service   Read Models   Inventory    Admin
   |         ^           |            |
   ES/AI     |           v            v
           cache     Booking DB    Config DB
                     Redis holds
                     Kafka events → invalidate availability + search badges
```

### 3.7 Hold + confirm protocol (heart)

```text
resource_key = hash(restaurant_id, date, slot, party_band)

POST /holds:
  if remaining(resource_key) <= 0: 409 FULL
  create hold_id with TTL (3 min) decrementing remaining OR reserving soft count
  return hold_id, expires_at, hold_token

POST /reservations (Idempotency-Key, hold_id, hold_token):
  validate hold active & token
  BEGIN
    CAS/txn: finalize inventory (ensure reserved)
    insert reservation CONFIRMED
    mark hold consumed
  COMMIT
  emit ReservationConfirmed
  return confirmation
```

**Hold accounting strategies:**

| Strategy | Mechanism | Tradeoff |
|----------|-----------|----------|
| Soft hold counter | `holds` + `confirmed` ≤ capacity | Must expire holds correctly |
| Hard decrement on hold | Decrement immediately; increment on expire | Simpler remaining; need reliable expiry |
| Seat lock rows | Lock specific table rows | More realistic; less concurrency |

**Chosen for interview clarity:** hard decrement on hold + expiry worker / Redis TTL callback to increment back if not confirmed.

### 3.8 Search vs booking consistency

| Plane | Model | Staleness |
|-------|-------|-----------|
| Search badges (“7:00 available”) | Eventual | seconds–minutes OK |
| Availability grid | Read model; near-real-time | seconds OK |
| Hold/Confirm | Strong on inventory key | 0 dual books |

```text
on ReservationConfirmed / Cancel / HoldExpire:
  publish event
  availability worker updates restaurant-day doc
  search worker updates has_availability_tonight bit
```

### 3.9 Search design

Filters: geo radius, cuisine, price, time, party size.

```text
Query:
  1) geo filter restaurants in index
  2) filter by cuisine/price
  3) join/filter by availability read model for requested slot/party
  4) rank by rating, distance, availability richness
```

At scale, maintain `availability_bitmap` or slot lists per restaurant-day in KV for step 3.

### 3.10 Overbooking (optional config)

Some venues allow `capacity * (1+overbook_pct)`. Must be explicit; host handles risk. Default MVP: overbook_pct=0.

---

## 4. Architecture Diagram

### 4.1 Booking path

```text
Client                Hold Svc / Inventory           Booking DB
  |--POST /holds------------>|                          |
  |                    DEC remaining (atomic)           |
  |                    SET hold@TTL Redis               |
  |<-- hold_id --------------|                          |
  |--POST /reservations----->|                          |
  |                    validate hold                    |
  |                    txn confirm -------------------->|
  |                    consume hold                     |
  |<-- confirmation ----------|                          |
  |                    emit event → Availability / Search / Notif
```

### 4.2 Dual contention

```text
Diner A & Diner B hold last unit
  remaining starts at 1
  A hold → remaining 0
  B hold → 409 FULL  (or waitlist)
If A expires → remaining 1 → B can hold
If both somehow confirm: prevented by hold ownership + CAS on versioned inventory row
```

### 4.3 Regional cells

```text
          Global Identity / Diner profiles
                     |
      +--------------+--------------+
      v              v              v
   Cell USW       Cell USE       Cell EU
   restaurants    restaurants    restaurants
   booking DB     booking DB     booking DB
   search         search         search
```

Restaurant pinned to cell by geo.

---

## 5. Design Deep Dive

### 5.1 Reliability

| Failure | Mitigation |
|---------|------------|
| Confirm crash after inventory final | Idempotency-Key replay returns same reservation |
| Hold expiry vs confirm race | Single serialize on `resource_key` / transactional compare |
| Redis down | Fail holds closed or fall back to DB leases (degraded) |
| Availability worker lag | Users may see ghost slot; confirm fails gracefully with alternatives |
| Notif fail | Retry; booking still valid |
| Clock skew TTL | Server expiry; Redis PTTL |

**Degradation:**

1. Disable personalized ranker  
2. Serve coarser availability (“available tonight” only)  
3. Keep confirm path protected  
4. Read-only search if booking DB primary issues (no new holds)

**SLO examples:**

| SLO | Target |
|-----|--------|
| Zero confirmed double-books | hard invariant |
| Confirm p99 | < 300ms |
| Hold p99 | < 150ms |
| Search p99 | < 300ms |

### 5.2 Scalability

**Shard keys:** `restaurant_id` for inventory/bookings; search by region.

**Hot restaurant playbook:**

- Dedicated inventory partition  
- Short hold TTL  
- Rate limit availability spam  
- Queue / lottery for opening drops (rare)  
- Cache availability with request coalescing  

**Precompute availability:**

Nightly + incremental: generate slot structures for next N days from hours + capacity − bookings − blocks.

### 5.3 Maintainability

| Service | Owns |
|---------|------|
| Restaurant Catalog | Profiles, hours, tables config |
| Inventory | Remaining capacity, holds, blocks |
| Booking | Reservation lifecycle |
| Search | Indexed discovery |
| Notification | Email/SMS |
| Host Ops | Seating, walk-ins |

**Config-driven policies:** cancel windows, hold TTL, overbook %, party bands.

**Observability:**

| Metric | Why |
|--------|-----|
| Hold expire rate | TTL tuning |
| Confirm conflict rate | UX friction / stale search |
| Double-book attempts (should be 0 committed) | Correctness |
| Search→book conversion | Product |
| Peak slot contention | Capacity planning |

### 5.4 Table combination (deeper option)

```text
Tables: 4×2-top, 2×4-top
Party of 6 → need combine two tables adjacent
Matching is graph / constraints problem
MVP: party_band capacity approximates
Phase 1.5: assign tables at confirm or at seat time
```

Interview point: seating optimization can be **late-bound** at host seat time to keep online booking simpler.

### 5.5 Waitlist

```text
When FULL:
  enqueue WaitlistEntry(party, window, contact)
On cancel:
  offer next waitlist with short hold
```

Exactly-one offer to waitlist similar to ride-hail offers.

### 5.6 Timezones

Store `restaurant.timezone`. Slots generated in local time; persist `slot_start_utc` + local fields. DST transitions: regenerate affected days.

### 5.7 Security / PII

- Diner phone/email encrypted at rest  
- Hosts see only their restaurant bookings  
- Audit admin overrides  
- Rate-limit scraping of availability  

### 5.8 Multi-region

Restaurant cell is single-writer for inventory. Cross-region read replicas for profiles OK. Failover: promote booking primary with care (no dual writers).

---

## 6. Wrap-Up

### 6.1 Designed

OpenTable-like discovery + reservations with capacity inventory, TTL holds, atomic confirms, eventual search badges, host ops, and regional sharding.

### 6.2 Trade-offs

| Decision | Chose | Rejected | Why |
|----------|-------|----------|-----|
| Inventory | Capacity bands + atomic holds | Pure search SoT | Correctness |
| Search | Separate index | Query booking DB | Scale |
| Tables | Late bind seating | Full combine at book MVP | Complexity |
| Staleness | Eventual availability views | Strong global reads | Perf |
| Overbook | Config default 0 | Hidden overbook | Trust |

### 6.3 Risks

- Ghost availability UX  
- Hold abuse locking slots  
- Timezone bugs  
- Viral venue stampedes  

### 6.4 60-second pitch

> “I’d split search from inventory. Search and availability read models can be slightly stale. Booking uses TTL holds and atomic inventory updates per restaurant-slot-band so two diners can’t confirm the last table. Cancels emit events that restore capacity and refresh read models. We shard by restaurant/region and protect hot venues with coalesced reads and short holds.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Consistency & double-booking

**Q1. How do you prevent double-booking?**  
Atomic decrement / conditional update on versioned inventory row; holds fence capacity; idempotent confirm.

**Q2. Is serializable isolation required?**  
Per-resource linearizability suffices; not global serializability across all restaurants.

**Q3. What if hold expiry fires after confirm?**  
Hold state machine: `consumed` wins; expiry no-ops.

**Q4. Optimistic vs pessimistic locking?**  
Optimistic version CAS good; pessimistic row lock OK at low QPS per key.

### 7.2 Inventory modeling

**Q5. Covers vs tables?**  
Covers simpler; tables needed for fine dining / combinable rooms. Hybrid late-bind.

**Q6. How do blocks / private events work?**  
Block records subtract capacity or remove slots before generation.

**Q7. Turn times?**  
Slot spacing depends on expected dining duration; config per service.

### 7.3 Search

**Q8. Geo query implementation?**  
GeoHash/S2 + inverted filters in search engine; distance sort.

**Q9. How fresh must “available at 7pm” badge be?**  
Seconds–minutes; always revalidate on hold.

**Q10. Personalization?**  
Ranker hook; not on critical booking path.

### 7.4 Scale / geo

**Q11. Global vs regional?**  
Pin restaurant to region cell; diner can query cross-region read-only search.

**Q12. 5M restaurants?**  
Search sharding; inventory only for bookable partners; cold inactive venues archived.

**Q13. Ticket-style drop for famous venue?**  
Virtual waiting room; lottery; rate limit; longer cache of FULL.

### 7.5 Product edge cases

**Q14. Modify reservation?**  
Try hold new slot then release old in txn; else fail and keep old.

**Q15. Partial no-show (2 of 4)?**  
Ops marks; inventory usually already consumed.

**Q16. Deposits?**  
Payment auth on confirm; capture on no-show policy.

### 7.6 Microsoft-flavored

**Q17. Azure mapping?**  
App Service/AKS, Azure SQL/Cosmos, Cache for Redis, Cognitive Search, Event Hubs, Send Grid/SMS — optional.

**Q18. Multi-tenant restaurant SaaS?**  
`restaurant_id` tenancy; noisy neighbor limits; per-tenant encryption keys optional.

**Q19. Compliance?**  
PII retention; GDPR delete diner data with booking anonymization rules.

### 7.7 Traps

| Trap | Answer |
|------|--------|
| Search is source of truth | No |
| No holds, only confirm | Higher confirm conflicts; still need atomicity |
| Store inventory only in ES | No — ES not transactional ledger |
| Global lock | Unnecessary |

---

## 8. Appendices

### Appendix A — Glossary

| Term | Meaning |
|------|---------|
| Slot | Bookable time granule (e.g. 7:00) |
| Hold | Temporary capacity reservation |
| Covers | Number of diners |
| Party band | Size bucket (1–2, 3–4, 5–6) |
| Ghost availability | Stale “open” slot in UI |
| Overbook | Intentional capacity > physical |
| Service | Lunch/dinner period definition |

### Appendix B — Schema sketch

```sql
restaurants(restaurant_id, name, lat, lng, tz, cuisine, ...)
inventory_units(
  restaurant_id,
  service_date,
  slot_start_utc,
  party_band,
  capacity,
  held,
  confirmed,
  version,
  PRIMARY KEY (restaurant_id, service_date, slot_start_utc, party_band)
)
holds(hold_id, resource_key, expires_at, state, diner_id)
reservations(
  reservation_id, restaurant_id, diner_id,
  slot_start_utc, party_size, state,
  hold_id, created_at, version
)
blocks(restaurant_id, start_utc, end_utc, reason)
```

### Appendix C — Atomic SQL sketch

```sql
UPDATE inventory_units
SET held = held + 1, version = version + 1
WHERE restaurant_id=? AND service_date=? AND slot_start_utc=? AND party_band=?
  AND (confirmed + held) < capacity
  AND version=?;
-- rows_affected == 1 else conflict
```

### Appendix D — Availability JSON (read model)

```json
{
  "restaurant_id": "r_1",
  "date": "2026-08-06",
  "party_size": 2,
  "slots": [
    {"time": "18:30", "status": "open"},
    {"time": "19:00", "status": "limited"},
    {"time": "19:30", "status": "full"}
  ],
  "as_of": "2026-08-06T16:01:02Z"
}
```

### Appendix E — Capacity cheatsheet

| Metric | Baseline order |
|--------|----------------|
| Restaurants | 50K |
| Search QPS | 30K |
| Confirm QPS | 500 |
| Reservations/day | 2M |

### Appendix F — Hold TTL guidance

| UX | TTL |
|----|-----|
| Short form | 2–3 min |
| Long form + deposit | 5–10 min |
| Waitlist offer | 2 min |

### Appendix G — Interview checklist

- [ ] Separated search vs inventory  
- [ ] Defined inventory unit  
- [ ] Hold TTL + expiry  
- [ ] Atomic confirm / CAS  
- [ ] Idempotency  
- [ ] Stale availability UX  
- [ ] Cancel releases capacity  
- [ ] Hot restaurant story  
- [ ] Timezones  
- [ ] Host ops basics  

### Appendix H — Related prompts

- Ticketmaster-style events  
- Hotel booking  
- Scheduling / calendar  
- Shopping cart inventory  

### Appendix I — Event contracts

```json
{"type":"HoldCreated","hold_id":"h1","resource_key":"...","expires_at":"..."}
{"type":"ReservationConfirmed","reservation_id":"b1","restaurant_id":"r1","slot":"..."}
{"type":"ReservationCanceled","reservation_id":"b1"}
{"type":"HoldExpired","hold_id":"h1"}
```

### Appendix J — Ranking signals (search)

Distance, rating, availability density, price fit, cuisine match, bookability now.

### Appendix K — Failure UX copy (design note)

When confirm conflicts: “That time just went; here are nearby times 7:15 / 7:45.” Never silent fail.

### Appendix L — Progressive roadmap

| Phase | Add |
|-------|-----|
| MVP | Pools, hold/confirm, search |
| 1.5 | Waitlist, deposits, table assign |
| 2 | Experiences, SMS 2-way, CRM |
| 3 | Yield management / pricing |

### Appendix M — Why Microsoft asks this

Validates transactional thinking, stale-read UX, and multi-tenant SaaS boundaries—common in M365 scheduling cousins and commerce partners.

### Appendix N — Whiteboard order

1. Actors + MVP scope  
2. Inventory unit definition  
3. Hold/confirm sequence  
4. Search plane separate  
5. Scale: shard by restaurant; hot venue  

### Appendix O — Sample party bands

| Band | Party sizes |
|------|-------------|
| A | 1–2 |
| B | 3–4 |
| C | 5–6 |
| D | 7–8 (request/approve) |

Capacity configured per band per slot; large parties manual.

### Appendix P — No-show policy hook

```text
on mark_no_show:
  state=NO_SHOW
  optionally capture deposit
  analytics++; do not auto-release slot after start time
```

---

*End of OpenTable / restaurant reservations system-design prep doc (Microsoft interview practice).*
