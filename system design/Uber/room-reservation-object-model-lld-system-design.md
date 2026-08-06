# LLD / OOD: Room Reservation Object Model

> **Focus areas:** OOP model · Rooms · Reservations · Guests · Billing hooks · Policies · State  
> **Style:** Object-oriented interview design (clarify → NFRs → cases → classes → APIs → state machines → concurrency → extensibility → deep dive → wrap-up → Q&A)  
> **Quality bar:** Clear responsibilities, race-safe critical sections, extensibility without rewrite, honest complexity  
> **Interview theme:** Uber — **object model for room reservation (hotel/meeting hybrid interview variant)**

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

Goal: design a clean object model for reserving rooms with guests, date ranges, statuses, and pluggable pricing/cancellation policies.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | OOD reservation model | Full hotel HLD |
| Domain | Rooms + reservations | Payment PSP |
| Uber lens | Extensible policies | Anemic DTO dump |

### 1.1 Clarifying questions (ask aloud)

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Room types? | standard/suite | Type+inventory |
| F2 | Reserve? | date range guest | Reservation |
| F3 | Overbook? | no MVP | Hard inventory |
| F4 | Cancel policy? | pluggable | Strategy |
| F5 | Price? | nightly+fees | PricingPolicy |
| F6 | Guests? | primary+list | Guest |
| F7 | Check-in/out? | states | FSM |
| F8 | Multi-room? | yes | Lines |
| F9 | Idempotency? | yes | Keys |
| F10 | Search? | availability | Service |
| F11 | History? | yes | Events |
| F12 | Taxes? | hook | Policy |

**MVP scope:**

1. Room + RoomType inventory
2. Create reservation holding rooms
3. Cancel with policy fee
4. Check-in/out transitions
5. Availability search
6. Thread-safe allocate

**Out of MVP:**

- Channel manager OTA sync
- Dynamic RM AI
- Full folio accounting

### 1.2 Scope repeat-back

> Object model for room reservations with inventory exclusion, policies, and reservation lifecycle.

---

## 2. Non-Functional Requirements

| # | NFR | Target | Why |
|---|-----|--------|-----|
| N1 | No oversell | hard | Money/trust |
| N2 | Allocate latency | low ms | UX |
| N3 | Extensibility | policies | Interview |
| N4 | Audit | who/when | Support |
| N5 | Idempotency | retries | OK |
| N6 | Clear FSM | illegal reject | Correct |
| N7 | Testability | clock/policy inject | Quality |
| N8 | Scale | multi-property later | Honest |

### 2.1 Progressive scale (object-system view)

| Metric | Base | 10× | 100× |
|--------|----------|----------|----------|
| Rooms | 100 | 1K | 10K |
| Reservations/day | 50 | 500 | 5K |
| Concurrent allocates | 5 | 50 | 500 |

---

## 3. Cases

### 3.1 Happy paths

1. Search 2 nights -> reserve suite -> check-in -> check-out.
2. Cancel before window -> refund policy.

### 3.2 Edge / failure cases

| Case | Behavior |
|------|----------|
| Double allocate race | one wins |
| Cancel after check-in | reject/policy |
| Zero nights | reject |
| Hold expiry | release inventory |
| Idempotent create | same res |
| Over capacity guests | warn/reject |

---

## 4. Object Model & Class Diagrams

### 4.1 Responsibilities

ReservationService allocates via InventoryLedger; PricingPolicy quotes; CancellationPolicy fees; Reservation FSM.

### 4.2 Class diagram (ASCII)

```text
Property 1-* Room
RoomType
Reservation 1-* ReservationLine->Room
Guest
PricingPolicy / CancellationPolicy
InventoryLedger
```

### 4.3 Key classes (details)

**InventoryLedger** tracks room-night availability with CAS.
**Reservation** aggregate root with lines and status.
**Policies** pure functions of reservation+time.

---

## 5. Public APIs / Interfaces

```text
searchAvailability / createReservation / cancel / checkIn / checkOut
```



---

## 6. State Machines

HELD->CONFIRMED->CHECKED_IN->CHECKED_OUT; HELD/CONFIRMED->CANCELED

---

## 7. Concurrency & Consistency

CAS on room-night keys; reservation version; hold TTL reaper.

**Invariants**

- No two active reservations own same room-night
- Illegal transitions rejected
- Money ops idempotent keys

---

## 8. Extensibility

New RoomType; new PricingPolicy; deposit policies without rewriting aggregate

---

## 9. Design Deep Dive

### 9.1 Correctness under race

Allocate uses transactional compare on inventory keys for each night.

### 9.2 Performance

Availability bitsets per room-type/day; don't scan all reservations.

### 9.3 Persistence mapping (if asked)

reservations, lines, inventory_ledger(room_id,date,status,res_id)

### 9.4 Failure handling

Hold expires -> release; payment fail -> cancel hold

---

## 10. Wrap-Up

> Reservation aggregate + inventory ledger CAS + pluggable pricing/cancel policies + explicit FSM.

**What interviewers listen for**

- Clear entity boundaries and ownership of mutations
- Explicit concurrency story (locks/CAS/sharding)
- Extensibility via strategy/policy objects
- APIs that are idempotent where retries happen
- Honest MVP vs over-engineering

---

## 11. Deeper / Related Interview Questions

### Hotel vs meeting?

**Q: Difference?**  
A: Nightly inventory vs interval booking—same exclusion idea.

### Overbooking?

**Q: MVP?**  
A: Defer; hard inventory.

---

## 12. Appendices

### 12.1 FSM

HELD->CONFIRMED->CHECKED_IN->CHECKED_OUT

### 12.2 Ledger

room_id+date unique owner

### 12.3 Pseudocode

hold nights CAS->create res

### 12.4 Checklist

FSM, CAS, policies

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

*End of room reservation object model LLD.*

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
