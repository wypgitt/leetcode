# LLD / OOD: Meeting Room Scheduler

> **Focus areas:** Rooms by size · Booking history · Conflict detection · Concurrency · Extensible policies  
> **Style:** Object-oriented interview design (clarify → NFRs → cases → classes → APIs → state machines → concurrency → extensibility → deep dive → wrap-up → Q&A)  
> **Quality bar:** Clear responsibilities, race-safe critical sections, extensibility without rewrite, honest complexity  
> **Interview theme:** Uber — **OOD for booking meeting rooms with capacity and history**

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Non-Functional Requirements](#2-non-functional-requirements)
3. [Cases](#3-cases)
4. [Object Model & Class Diagrams](#4-object-model--class-diagrams)
5. [Public APIs / Interfaces](#5-public-apis--interfaces)
6. [State Machines](#6-state-machines)
7. [Concurrency & Consistency](#7-concurrency--consistency)
8. [Extensibility](#8-extensibility)
9. [Design Deep Dive](#9-design-deep-dive)
10. [Wrap-Up](#10-wrap-up)
11. [Deeper / Related Interview Questions](#11-deeper--related-interview-questions)
12. [Appendices](#12-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design an object-oriented meeting room scheduler that books rooms by size/capacity, prevents conflicts, keeps history, and stays race-safe under concurrent booking attempts.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | In-memory/service OOD booking | Full Google Calendar distributed HLD |
| Entities | Room, Booking, User | Video meeting media |
| Uber lens | Concurrency + clean classes | SQL-only without objects |

### 1.1 Clarifying questions (ask aloud)

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Rooms? | id, capacity, location attrs | Room registry |
| F2 | Book? | user, room, interval | allocate API |
| F3 | Conflict? | No overlap | interval checks |
| F4 | Find? | Smallest fitting room | strategy |
| F5 | History? | Past bookings | store |
| F6 | Cancel? | Yes | state |
| F7 | Idempotency? | client key | dedupe |
| F8 | Timezone? | UTC internals | policy |

**MVP scope:**

1. Add rooms with capacity.
2. Book(room|auto, start, end, user) with conflict detection.
3. Suggest smallest room that fits party size.
4. Cancel booking; list history by room/user.
5. Thread-safe booking under concurrent requests.

**Out of MVP:**

- Recurrence RRULE complete
- Cross-building graph optimization

### 1.2 Scope repeat-back

> OOD scheduler: rooms, bookings, conflict-safe allocation strategies, history—concurrency via per-room locks/CAS.

---

## 2. Non-Functional Requirements

| # | NFR | Target | Why |
|---|-----|--------|-----|
| N1 | Conflict safety | no double book | invariant |
| N2 | Latency | in-process p99 low ms | indexes |
| N3 | Extensibility | new strategies | interfaces |
| N4 | History | queryable | append log |
| N5 | Idempotency | retries | keys |
| N6 | Scale rooms | 1 → 10k | shard by building later |

### 2.1 Progressive scale (object-system view)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Rooms | 50 | 500 | 5K | 50K |
| Bookings/day | 200 | 2K | 20K | 200K |
| Concurrent bookers | 10 | 100 | 1K | distributed |
| History retain | 90d | 1y | tiered | tiered |

---

## 3. Cases

### 3.1 Happy paths

1. Find room for 6 people 10–11 → book smallest capacity≥6 free.
2. Cancel frees slot for others.
3. History lists past meetings in room.
4. Idempotent retry returns same booking id.

### 3.2 Edge / failure cases

| Case | Behavior |
|------|----------|
| Overlap same room | reject |
| end <= start | validate |
| capacity insufficient | reject/find other |
| Concurrent two books | one wins |
| Cancel twice | idempotent |
| Past booking mutate | forbid |

---

## 4. Object Model & Class Diagrams

### 4.1 Responsibilities

- `RoomRepository` stores rooms.
- `BookingService` orchestrates validate/allocate/persist.
- `AvailabilityIndex` interval structures per room.
- `AllocationStrategy` chooses room.
- `Booking` entity with state.
- `Clock` for now().

### 4.2 Class diagram (ASCII)

```text
+----------------+      +------------------+
| BookingService |----->| AllocationStrategy|
+----------------+      +------------------+
        |                        ^
        v                        | SmallestFitStrategy
+---------------+         +---------------------+
| RoomInventory |         | AvailabilityIndex   |
+---------------+         +---------------------+
        |
        v
   Room / Booking entities
```

### 4.3 Key classes (details)

**BookingService.book**: validate range → strategy.select → lock room → recheck overlap → append booking.

**AvailabilityIndex**: per room sorted intervals or tree; `canFit` / `add` / `remove`.

**Booking**: id, roomId, userId, start, end, status ACTIVE|CANCELED, idempotencyKey.

---

## 5. Public APIs / Interfaces

```text
book(req: BookRequest) -> Booking
cancel(bookingId, userId) -> void
findAvailable(capacity, start, end) -> List[Room]
history(roomId|userId, range) -> List[Booking]
addRoom(room) -> Room
```



---

## 6. State Machines

Booking: ACTIVE → CANCELED

```text
ACTIVE --cancel--> CANCELED
```

Illegal: cancel→active; overlap add while ACTIVE.

---

## 7. Concurrency & Consistency

Per-room ReentrantLock (or DB row CAS). Optimistic: read version intervals → write if unchanged.

**Invariant:** For each room, ACTIVE bookings are pairwise non-overlapping.

**Invariants**

- `start < end`
- ACTIVE bookings non-overlapping per room
- capacity ≥ partySize when assigned
- idempotencyKey unique success

---

## 8. Extensibility

- New `AllocationStrategy` (prefer floor, equipment).
- Policy objects for max duration / buffer times.
- Notification listener on booking events.

---

## 9. Design Deep Dive

### 9.1 Correctness under race

```text
lock(room):
  if overlaps(active[room], [start,end]): throw Conflict
  active.add(booking)
unlock
```
Interleave two threads without lock → double book; lock/CAS prevents.

### 9.2 Performance

Sorted interval list binary search for day; for heavy rooms use interval tree. Index bookings by user in secondary map.

### 9.3 Persistence mapping (if asked)

Tables `rooms(id,capacity,...)`, `bookings(...)` with exclusion constraint `USING gist (room_id, tsrange)` if Postgres; map objects 1:1.

### 9.4 Failure handling

Clock skew → inject Clock; partial failure after lock → transaction; idempotency store survives retries.

---

## 10. Wrap-Up

> Scheduler OOD centers on BookingService + per-room availability index with strategy-based room selection, race-safe locks/CAS, and cancel/history—extend via strategies not god-classes.

**What interviewers listen for**

- Clear entity boundaries and ownership of mutations
- Explicit concurrency story (locks/CAS/sharding)
- Extensibility via strategy/policy objects
- APIs that are idempotent where retries happen
- Honest MVP vs over-engineering

---

## 11. Deeper / Related Interview Questions

### Concurrency

**Q: Two users same slot?**  
A: Per-room lock/CAS; loser Conflict.

### Strategy

**Q: Why strategy pattern?**  
A: Swap smallest-fit vs preference without rewriting service.

### Scale & multi-region

**Q: How do you shard?**  
A: City/region cell first, then hash entity id within the cell.

**Q: Active-active writes for the same entity?**  
A: Avoid; home-cell single-writer with fencing on failover.

**Q: What do you shed first under load?**  
A: Non-critical analytics/marketing; protect money, safety, and trip-critical paths.

---

## 12. Appendices

### 12.1 BookRequest

userId, partySize, start, end, roomId?, idemKey

### 12.2 Overlap

`a.start < b.end && b.start < a.end`

### 12.3 Tests

concurrent booking property test

### 12.4 Complexity

check overlap O(log n) with tree; O(n) sorted merge OK MVP

### Interview checklist

- [ ] Clarified entities and MVP
- [ ] Class diagram with responsibilities
- [ ] APIs + idempotency
- [ ] State machine(s)
- [ ] Concurrency invariants
- [ ] Extensibility hooks
- [ ] Pseudocode for critical path
- [ ] Edge cases covered

---

*End of meeting room scheduler LLD.*

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.

### Observability hooks in LLD

- Counters: allocation_conflict_total, illegal_transition_total, reject_full_total
- Histograms: allocate_latency_ms, command_latency_ms
- Structured logs with entity ids (room_id, booking_id) — never secrets
- Trace spans around lock acquisition when debugging deadlocks
- Debug dump API gated for admin: current in-memory maps sizes

### Extensibility checklist

- New strategy implements interface; old callers unchanged
- New entity subtype doesn’t break persistence polymorphism carelessly
- Feature flags for risky behavior changes
- Serialization versioning for stored objects
- Avoid god-classes: split services vs entities vs strategies

### Testing strategy

| Layer | What |
|-------|------|
| Unit | Pure domain rules, pricing/allocation math, FSM transitions |
| Concurrency | Two threads racing the same resource; CAS outcomes |
| Property | Idempotent commands; invariants hold after random ops |
| Integration | Repository + service with embedded DB/fake clock |
| Soak | Long run for leak / timer correctness |

Prefer a **FakeClock** for scheduler tests; never sleep in unit tests.
