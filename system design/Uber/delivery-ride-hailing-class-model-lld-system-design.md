# LLD / OOD: Delivery / Ride-Hailing Class Model

> **Focus areas:** Domain OOP · Trip/Delivery · Driver/Courier · Matching hooks · States · Money ports  
> **Style:** Object-oriented interview design (clarify → NFRs → cases → classes → APIs → state machines → concurrency → extensibility → deep dive → wrap-up → Q&A)  
> **Quality bar:** Clear responsibilities, race-safe critical sections, extensibility without rewrite, honest complexity  
> **Interview theme:** Uber — **unified class model for ride-hailing and delivery marketplace entities**

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

Goal: design an extensible class model covering ride-hailing and delivery: users, vehicles/couriers, trips/orders, offers, and payment hooks.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Domain class model | Full microservice HLD |
| Variants | Ride + delivery | Airline |
| Uber lens | Shared abstractions | Copy-paste two apps |

### 1.1 Clarifying questions (ask aloud)

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Actors? | Rider/Diner/Driver/Courier/Merchant | Roles |
| F2 | Jobs? | RideTrip vs DeliveryTask | Polymorphism |
| F3 | Matching? | Offer hooks | Interfaces |
| F4 | Location? | Locatable | Interface |
| F5 | Pricing? | Quote hook | Interface |
| F6 | States? | FSM | Per type |
| F7 | Payments? | Payable port | Interface |
| F8 | Vehicles? | capacity/mode | Entity |
| F9 | Ratings? | optional | Entity |
| F10 | Ids? | strong ids | Values |
| F11 | Time? | clock | Inject |
| F12 | Extensibility? | new modes | Strategy |

**MVP scope:**

1. User/Role model
2. Location + Vehicle
3. Trip and DeliveryTask under DispatchableJob
4. Offer accept/reject
5. Guarded transitions
6. Fare/PaymentPort interfaces

**Out of MVP:**

- Full ORM framework
- UI
- ML matching internals

### 1.2 Scope repeat-back

> OOD model unifying ride and delivery jobs with shared dispatch/payment ports and specialized lifecycles.

---

## 2. Non-Functional Requirements

| # | NFR | Target | Why |
|---|-----|--------|-----|
| N1 | Clear responsibilities | SOLID | Interview |
| N2 | Safe transitions | reject illegal | Correct |
| N3 | Extensibility | new job type | OCP |
| N4 | Testability | fake ports | Quality |
| N5 | Concurrency | per-job lock | Honest |
| N6 | No god class | split | Design |
| N7 | Idempotent commands | retries | Mobile |
| N8 | Readable diagrams | ASCII | Comm |

### 2.1 Progressive scale (object-system view)

| Metric | Base | 10× | 100× |
|--------|----------|----------|----------|
| Entity types | tens | tens | +subtypes |
| Core flows | book/match/complete | same | same |
| Workers conceptually | drivers/couriers | same | same |

---

## 3. Cases

### 3.1 Happy paths

1. Rider request -> offer -> start -> complete -> pay
2. Diner order -> courier -> pickup -> deliver -> pay

### 3.2 Edge / failure cases

| Case | Behavior |
|------|----------|
| Illegal transition | exception |
| Double accept | CAS winner |
| Cancel mid-job | policy |
| Offline worker | ineligible |
| Payment fail | payment state separate |

---

## 4. Object Model & Class Diagrams

### 4.1 Responsibilities

DispatchableJob aggregate; MatchingPort; PaymentPort; LocationPort; RideTrip vs DeliveryTask.

### 4.2 Class diagram (ASCII)

```text
User <|- Rider, Driver, Courier, Merchant
DispatchableJob <|- RideTrip, DeliveryTask
Offer -> Job + Worker
PaymentPort, PricingPort, LocationPort
```

### 4.3 Key classes (details)

**DispatchableJob**: status, assign, apply(Command).
**RideTrip** vs **DeliveryTask** specialize stops/parties.
**Offer** fences assignment.
**Ports** quote/capture/nearby.

---

## 5. Public APIs / Interfaces

```text
request(jobSpec); offer(job,worker); handle(command); PaymentPort.capture(...)
```



---

## 6. State Machines

Ride: REQUESTED->MATCHING->ASSIGNED->ARRIVED->IN_TRIP->COMPLETED
Delivery: PENDING->OFFERING->ASSIGNED->AT_PICKUP->PICKED_UP->DELIVERED
Offer: PENDING->ACCEPTED|REJECTED|EXPIRED

---

## 7. Concurrency & Consistency

Single-writer per job (version CAS). Offer accept CAS assignee.

**Invariants**

- At most one assignee
- Idempotent commands
- Payment via idem keys

---

## 8. Extensibility

New job subtype + StateMachine; reuse ports.

---

## 9. Design Deep Dive

### 9.1 Correctness under race

acceptOffer CAS if MATCHING and offer valid -> ASSIGNED

### 9.2 Performance

In-proc model; map to sharded services at scale.

### 9.3 Persistence mapping (if asked)

jobs, offers, users; status+version; outbox for ports

### 9.4 Failure handling

PaymentPort down -> PAYMENT_PENDING; do not uncomplete

---

## 10. Wrap-Up

> Unified DispatchableJob for rides/deliveries with Offer fencing, typed FSMs, and pricing/payment/location ports.

**What interviewers listen for**

- Clear entity boundaries and ownership of mutations
- Explicit concurrency story (locks/CAS/sharding)
- Extensibility via strategy/policy objects
- APIs that are idempotent where retries happen
- Honest MVP vs over-engineering

---

## 11. Deeper / Related Interview Questions

### One FSM?

**Q: Share?**  
A: Shared ideas; product states via strategy

### Matching where?

**Q: Where?**  
A: MatchingPort/service

---

## 12. Appendices

### 12.1 Commands

Arrive/Complete with idem

### 12.2 CAS accept

version check

### 12.3 Classes

User, RideTrip, DeliveryTask, Offer, Ports

### 12.4 Checklist

polymorphism, FSM, CAS, ports

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

*End of delivery / ride-hailing class model LLD.*

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
