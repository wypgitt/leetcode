# System Design: Room Reservation System (Calendar + Exclusive Rooms)

> **Focus areas:** Exclusive booking · Conflict detection · Recurrence · Optimistic/pessimistic locks · ACLs · Notifications · Idempotency · Building/floor inventory  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — Google Calendar **variant** emphasizing **resource locking** (meeting rooms)  
> **Quality bar:** Hard conflicts rejected; no double-book; clear relation to soft calendar events

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

Goal: design a **room reservation** system—employees book meeting rooms with exclusive occupancy, see availability, manage recurring reservations, and never double-book a room.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Core | Exclusive resource calendars (rooms) | Soft personal calendar only |
| Related | Shares recurrence/TZ with Google Calendar doc | Duplicate entire Calendar HLD blindly |
| Inventory | Buildings, floors, rooms, capacity, AV | Hotel revenue management full RMS |
| Uber lens | Consistency, locking, idempotency | Interior design |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Resources? | Rooms with capacity, AV, location | Room catalog |
| F2 | Booking? | Time range + room → confirm | Conflict check |
| F3 | Conflicts? | **Hard deny** overlaps | Locking/interval index |
| F4 | Recurring? | Weekly standups | Master + exceptions + conflict each instance window |
| F5 | Search? | Find room for N people at time T | Availability search |
| F6 | Permissions? | Who can book which building | ACL / policies |
| F7 | Check-in? | Optional release if no-show | Auto-release jobs |
| F8 | Invites? | Attach attendees / calendar event | Notify + optional calendar sync |
| F9 | Admin? | Block rooms for maintenance | Outages as busy |
| F10 | Waitlist? | Phase 2 | Defer |
| F11 | Display boards? | Outside-room tablet | Read API |
| F12 | Idempotency? | Retry-safe booking | Keys |

**MVP scope:**

1. Catalog: buildings/floors/rooms.  
2. Create/cancel/update bookings with **exclusive** overlap rejection.  
3. Availability search by time, capacity, filters.  
4. Recurring bookings with conflict detection strategy.  
5. ACLs by org/building.  
6. Reminders / confirmation notifications.  
7. Optional check-in + auto-release.

**Out of MVP:** AI room assignment optimization across campus, paid external booking marketplace, full hotel PMS.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Book latency | p99 < 300–500ms |
| N2 | Double-book | **0** successful overlaps |
| N3 | Read availability | p99 < 200–400ms |
| N4 | Durability | Accepted bookings durable |
| N5 | Consistency | Strong per room timeline |
| N6 | Scale | Global offices; peak :00 booking storms |

### 1.3 Cases

**Happy:** Search free room → book 10:00–11:00 → invite → check-in → end.  

| Case | Behavior |
|------|----------|
| Two users book same slot | One wins; other conflict error |
| Recurring conflicts mid-series | Reject series or skip conflicted instances—**pick policy** |
| Edit extend into next booking | Reject |
| Maintenance block | Appears busy |
| No-show | Auto-release after grace |
| DST recurring | TZ-correct expansion |
| Cancel recurrence this-only | Free that slot |
| Clock skew clients | Server time authorizes |
| Cross-building search | Parallel room checks |
| Storm at 9am | Queue/rate limit; keep correctness |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Rooms | 5K | 50K | 500K | 5M |
| Bookings / day | 100K | 1M | 10M | 100M |
| Peak book QPS | ~20 | ~200 | ~2K | ~20K |
| Availability searches / s | ~100 | ~1K | ~10K | ~100K |
| Buildings | 50 | 500 | 5K | 50K |
| Recurring series | 200K | 2M | 20M | 200M |

**Jumps:** 10× shard by building; 100× interval indexes + booking storms tooling; 1,000× hierarchical campuses + read replicas + search secondary index.

### 1.5 Scope repeat-back

> Exclusive meeting-room reservations with strong per-room conflict detection, recurrence-aware booking, availability search, ACLs, and optional check-in release—scaled by building/room shards without ever allowing double-book.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic

```text
Baseline 20 book/s peak; 100 search/s
Each book: conflict check + insert + notify
Each search: filter candidate rooms × interval overlap tests
```

### 2.2 Interval density

```text
Room busy ~8 meetings/day × 5K rooms = 40K intervals/day active
Hot room day view: ~12 intervals—trivial
Search "any room in building at T for 1h": check hundreds of rooms—index needed
```

### 2.3 Storage

```text
Booking ~500 B; 100K/day → 50 MB/day
Recurrence masters + exceptions dominate complexity more than bytes
```

### 2.4 Bottlenecks

1. Hot room (exec boardroom) race  
2. Recurring series validation cost  
3. Wide availability scans  
4. :00 reminder/booking storms  
5. Calendar sync feedback loops  

---

## 3. High-Level Design

### 3.1 Core invariant

> For any room, accepted bookings’ time intervals (materialized instances in scope) are **pairwise non-overlapping** (except zero-duration edges policy).

### 3.2 Locking strategies

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. DB exclusion constraint | Simple strong | Sharding care | Ignoring races |
| B. Serializable tx + range locks | Correct | Perf under storm | — |
| C. Room mutex lease in Redis + DB | Fast | Lease bugs | Completing without DB conflict proof |
| D. Occupancy calendar CRDT | — | Soft conflicts | **Hard** exclusivity required |

**Chosen:** **Per-room single-writer shard** + transactional conflict check (Postgres exclusion constraint `tstzrange` OR explicit overlap query under row lock on `room_id`).

```sql
-- conceptual
EXCLUDE USING gist (room_id WITH =, during WITH &&)
```

### 3.3 Relationship to personal calendar

```text
Booking confirmed → create/attach calendar event for organizer/attendees (async)
Calendar event edits that change time must call back into reservation service
Room resource calendar may be the SoT for room busy
```

**Deal-breaker:** Two writers (Calendar + Rooms) both invent room truth without coordination.

### 3.4 Recurrence + exclusivity

| Policy | Behavior |
|--------|----------|
| All-or-nothing | Validate next N months; reject if any conflict |
| Skip conflicts | Book non-conflicting instances; report skips |
| Truncate | Book until first conflict |

**MVP pick:** All-or-nothing for horizon H (e.g. 6 months); expand & conflict-check instances in batches inside tx/chunked saga with reservation holds.

**Holds:** For long validation, place short **tentative holds** (leases) then commit—or validate in one shot if H small.

### 3.5 Availability search

```text
Input: building_ids, start, end, min_capacity, equipment[]
Candidate rooms = catalog filter
For each room (parallel, limited): NOT exists booking overlapping [start,end)
Rank by capacity fit / proximity
Cache negative? careful with races—search is advisory; book still authoritative
```

### 3.6 Check-in & auto-release

```text
Booking starts soon → require check-in by T+grace
Else job marks RELEASED; free interval; notify
Idempotent release
```

### 3.7 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Conflict SoT | Room booking store | Hard exclusivity | Soft calendar warn only |
| Concurrency | Room row/shard lock | Simple correctness | Last-write-wins |
| Search | Filter + overlap checks | Accurate | Trust search without recheck on book |
| Recurrence | Horizon validate | Bound work | Infinite expand |
| Multi-region | Home cell per building | Avoid dual book | Active-active room writers |

### 3.8 Components

1. Catalog Service (buildings/rooms)  
2. Reservation Service (book/cancel/update)  
3. Conflict / Interval Index  
4. Availability Search  
5. Recurrence Expander  
6. ACL / Policy  
7. Check-in / Auto-release workers  
8. Notification  
9. Calendar Sync Adapter  
10. Room Display API  

---

## 4. Architecture Diagram

```text
Clients (Web, Tablet, Slack bot)
            |
            v
       API Gateway
            |
   +--------+--------+--------------+
   v        v        v              v
Catalog  Reserve  Availability   Check-in
            |        ^
            v        |
     Room Booking Store (shard by building/room)
            |
            +--> Outbox --> Notify / Calendar Sync
            +--> Auto-release workers
```

### 4.1 Book sequence

```text
book(room, start, end, idem_key):
  authz
  begin tx
    lock room shard
    if overlap exists: abort CONFLICT
    insert booking CONFIRMED
  commit
  async notify + calendar
```

### 4.2 Race

```text
User A and B same slot:
 both tx; one lock wins; other sees overlap → 409
```

### 4.3 Recurring book

```text
expand instances for horizon → sort by room/time
acquire locks in global room order (avoid deadlock)
if any overlap: abort
else insert series + instances (or master + materialized window)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. No two CONFIRMED bookings overlap on same room.  
2. Idempotent create returns same `booking_id`.  
3. Tentative holds expire (leases) and never strand rooms.  
4. Cancel frees interval atomically.  
5. Auto-release only when policy says no-show.  
6. ACL checked on book and read.  
7. Maintenance blocks behave as bookings/outages.  
8. Home-cell single writer per room.  
9. Calendar sync failures don’t unlock exclusivity (retry outbox).  
10. Server timestamps for boundaries.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG exclusion; one region |
| 10× | Shard by `building_id` |
| 100× | Materialized occupancy windows; search indexes; storm limits |
| 1000× | Campus cells; read replicas; tentative hold service |

### 5.3 Maintainability

- Room attributes as data  
- Policy engine (who books VIP rooms)  
- Golden concurrency tests  
- Deadlock-ordered locking documented  

### 5.4 Progressive scale

**1×:** Single PG; gist exclusion; simple search.  
**10×:** Multi-office sharding; calendar sync.  
**100×:** Check-in sensors/QR; analytics on utilization.  
**1000×:** Global company; regional cells; advanced find-time across attendees+rooms (bridges calendar free/busy).

### 5.5 Deadlock avoidance

When booking multi-room (rare) or validating many rooms: **sort `room_id` ascending** before locking.

### 5.6 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Soft conflict only | Double meetings |
| Check overlap without lock | Race double-book |
| Infinite RRULE materialize | Meltdown |
| Search result as reservation | TOCTOU gap |
| Dual-active multi-region writers | Split brain book |

---

## 6. Wrap-Up

### 6.1 Designed

Exclusive room reservations with per-room transactional conflict detection, availability search that re-validates on book, recurrence horizon checks, ACLs, check-in auto-release, calendar sync via outbox, building-level sharding.

### 6.2 Decisions to defend

1. Hard exclusivity invariant  
2. Room-shard locks / exclusion constraints  
3. Idempotent booking  
4. Search advisory + book authoritative  
5. Recurrence horizon policy  
6. Hold leases if needed  
7. Single-writer home cell per room  

### 6.3 Risks

- Booking storms  
- Recurrence edge cases  
- Calendar sync loops  
- VIP policy complexity  
- Sensor check-in reliability  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Hard vs soft calendar |
| 5–18 | Conflict/locking |
| 18–28 | Search + book API |
| 28–38 | Recurrence + check-in |
| 38–45 | Scale shards; traps |

### 6.5 Closer

> **Room reservation:** strong per-room interval exclusivity under transactional locks, horizon-bounded recurrence, availability search with TOCTOU-safe confirm, and building shards—never confuse with soft personal calendar conflicts.

---

## 7. Deeper / Related Interview Questions

### 7.1 Concurrency

**Q: Optimistic vs pessimistic?**  
A: ETag alone insufficient without conflict predicate; need overlap check under mutual exclusion per room.

**Q: Postgres exclusion constraints?**  
A: Excellent interview answer for MVP correctness.

### 7.2 Intervals

**Q: Half-open intervals?**  
A: Use `[start,end)` so 10–11 and 11–12 don’t conflict.

**Q: Timezones?**  
A: Store UTC instants; room TZ for display; all-day rare for rooms.

### 7.3 Recurrence

**Q: Instance conflict 3 months out?**  
A: Horizon policy; or materialize window + background validator.

**Q: This-and-future edit?**  
A: Split series; reconflict-check.

### 7.4 Search

**Q: Fast find across 10k rooms?**  
A: Prefilter catalog; maintain free/busy bitmaps per room per day; still recheck on book.

**Q: Bitmap approach?**  
A: 15-min slots × day; good for search candidates.

### 7.5 Check-in

**Q: Abuse early check-in?**  
A: Allow only from T-start−δ; geofence tablet.

### 7.6 Calendar bridge

**Q: Which is SoT for room?**  
A: Reservation service. Calendar mirrors.

### 7.7 Interview traps

| Trap | Pushback |
|------|----------|
| Same design as Messenger | Wrong problem |
| Soft warn only | Fails exclusivity |
| Global lock all rooms | Unnecessary |
| Materialize 10 years | No |
| Believe search cache alone | Race |

### 7.8 Metrics

| Metric | Why |
|--------|-----|
| Conflict rate | UX contention |
| Book p99 | Performance |
| Utilization | Real estate |
| Auto-release count | No-show health |
| Double-book attempts caught | Correctness |

### 7.9 vs Google Calendar doc

Calendar allows overlapping personal events; **this system forbids room overlaps**. Reuse RRULE/TZ/notify; specialize locking.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
buildings(building_id, campus, tz, home_cell)
rooms(room_id, building_id, floor, capacity, attributes jsonb)

bookings(
  booking_id UUID PK,
  room_id,
  organizer_id,
  during tstzrange, -- [start,end)
  state TEXT, -- TENTATIVE|CONFIRMED|CANCELLED|RELEASED
  series_id UUID NULL,
  idempotency_key TEXT UNIQUE,
  etag INT,
  check_in_at TIMESTAMPTZ NULL
)

-- exclusion for CONFIRMED only via partial constraint / careful states
```

### 8.2 API checklist

- [ ] `GET /rooms/search?start&end&capacity&building`  
- [ ] `POST /bookings` + Idempotency-Key  
- [ ] `PATCH /bookings/{id}` + If-Match  
- [ ] `POST /bookings/{id}/cancel`  
- [ ] `POST /bookings/{id}/check-in`  
- [ ] `GET /rooms/{id}/availability?from&to`  
- [ ] Admin maintenance blocks  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Hard conflict | Overlap forbidden |
| Hold / tentative | Short lease before confirm |
| Horizon | Max recurrence validate window |
| Auto-release | Free no-show rooms |
| Exclusion constraint | DB-enforced non-overlap |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Exclusion/lock, idempotent book, search |
| 10× | Building shards, ACL, notify |
| 100× | Bitmaps, check-in jobs, storm control |
| 1000× | Campus cells, find-time across people+rooms |

### 8.5 Conflict check SQL sketch

```sql
SELECT 1 FROM bookings
WHERE room_id=$1 AND state='CONFIRMED'
  AND during && tstzrange($2,$3,'[)')
FOR UPDATE; -- with room lock strategy
```

### 8.6 Deadlock-safe multi-lock

```text
rooms_sorted = sort(room_ids)
for r in rooms_sorted: lock(r)
validate all
insert all
```

### 8.7 Interview “say this” (60s)

> Rooms are exclusive resources: shard by building/room, enforce non-overlapping `[start,end)` under transactional locks or gist exclusion; availability search is advisory; booking rechecks; recurrence validated within a horizon; tentative holds expire; calendar sync is outbox mirror—not a second SoT.

### 8.8 Reliability tests

1. Parallel book same slot → one success.  
2. Extend into next meeting → conflict.  
3. Recurring into maintenance → reject/skip per policy.  
4. Idempotent retry → one booking.  
5. No-show auto-release frees slot.  

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Successful double-book | 0 |
| Book p99 | < 500ms |
| Search p99 | < 400ms |
| Hold leak (stuck tentative) | ≈0 |

### 8.10 Occupancy bitmap

```text
day D room R: bitset of 96 slots (15-min)
search: rooms where bits over range all 0
on book: set bits in same tx as interval row
```

### 8.11 State machine

```text
TENTATIVE → CONFIRMED → (CANCELLED | RELEASED | COMPLETED)
TENTATIVE → EXPIRED
```

### 8.12 Related systems map

```text
Search → Reserve (lock+conflict) → Booking Store
                              ↓
                         Outbox → Calendar Sync / Notify
                              ↓
                         Auto-release worker
```

### 8.13 Policy examples

| Policy | Rule |
|--------|------|
| Max duration | ≤ 2h without approval |
| Advance book | ≤ 30 days |
| VIP room | Role allowlist |
| Back-to-back buffer | Optional 5–15 min |

### 8.14 Extra traps

| Trap | Pushback |
|------|----------|
| Redis lock without DB conflict proof | Unsafe |
| Floating local times | DST bugs |
| Client-generated unique slot IDs as only guard | Spoofable |

### 8.15 Room display board

```text
GET current/next booking for room_id
Signed device token bound to room
Offline: show last cache + "connectivity issue"
```

### 8.16 Unit check

```text
20K book/s at 1000× with exclusion indexes: shard heavily; not one PG
```

### 8.17 LLD pointer

Object-model / scheduler LLD variants may exist separately; this HLD owns distributed conflict story.

### 8.18 Brownout

```text
Under storm: prefer correctness; shed search fanout; queue books; never disable conflict checks
```

---


### 8.19 Booking storm playbook

```text
Symptom: p99 book latency ↑; conflict rate ↑ at :00
Actions:
  1. Ensure shard by building (no single PG)
  2. Rate-limit search fanout first
  3. Keep conflict checks—never disable
  4. Jitter client retries
  5. Pre-warm hot building caches for read paths
```

### 8.20 Tentative hold protocol

```text
1. Client requests hold(room, start, end, ttl=60s) with idempotency key
2. Server locks room; if free, insert TENTATIVE with lease_until
3. Client confirms → CAS TENTATIVE→CONFIRMED before lease expiry
4. Reaper expires TENTATIVE → frees interval
Invariant: CONFIRMED still non-overlapping; TENTATIVE counts as busy for others
```

### 8.21 Calendar sync outbox

```text
booking_confirmed → outbox row {booking_id, op=UPSERT_EVENT}
worker: create/update calendar event with external_event_id
on failure: retry with backoff; booking remains SoT
booking_cancelled → outbox CANCEL_EVENT
Loop prevention: ignore calendar webhooks that originated from our sync token
```

### 8.22 Availability bitmap details

```text
slot_size = 15 min
bits_per_day = 24*4 = 96
book [10:00,11:00) sets bits for slots 40..43 (example)
search requires all bits in range clear
maintenance blocks set bits too
Partial slot bookings: round policy documented (expand to covering slots for search; exact range in booking row)
```

### 8.23 ACL matrix

| Principal | View free/busy | Book | Admin block |
|-----------|----------------|------|-------------|
| Employee | Own building | Yes if policy | No |
| Floor coordinator | Building | Yes | Limited |
| Facilities | Campus | Yes | Yes |
| External guest | No | No | No |

### 8.24 Recurrence conflict report UX

```json
{
  "status": "rejected",
  "policy": "all_or_nothing",
  "conflicts": [
    {"instance_start": "...", "overlapping_booking_id": "..."}
  ]
}
```

### 8.25 Interview comparison table

| Aspect | Personal Calendar | Room Reservation |
|--------|-------------------|------------------|
| Overlap | Allowed | Forbidden |
| SoT | User calendars | Room booking store |
| Primary risk | Wrong TZ | Double-book |
| Locking | ETag on event | Room interval exclusion |

### 8.26 Utilization analytics (read path)

```text
CDC bookings → warehouse
metrics: hours_booked / hours_available by room/day
does not affect transactional conflict path
```

### 8.27 Multi-room booking (rare)

```text
Book room A + overflow B atomically:
  sort(A,B) lock order
  conflict check both
  insert both with group_id
  cancel group cancels all
```

### 8.28 Tablet check-in security

```text
Device cert bound to room_id
check-in endpoint requires device identity matches booking.room_id
prevents remote fake check-in from phone (optional policy)
```


*End of room reservation system design.*
