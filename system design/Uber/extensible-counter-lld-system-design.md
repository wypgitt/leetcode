# LLD / OOD: Extensible Counter System

> **Focus areas:** Counters · Inc/dec · Reset · Listeners · Persistence hooks · Concurrency · Pluggable backends  
> **Style:** Object-oriented interview design (clarify → NFRs → cases → classes → APIs → state machines → concurrency → extensibility → deep dive → wrap-up → Q&A)  
> **Quality bar:** Clear responsibilities, race-safe critical sections, extensibility without rewrite, honest complexity  
> **Interview theme:** Uber — **extensible counter LLD with policies and observers**

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

Goal: design an extensible counter system supporting inc/dec/get/reset with pluggable storage, bounds, and event listeners.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Counter OOD | Distributed metrics platform full |
| Ops | inc/dec/get/reset | Time-series DB |
| Uber lens | Extensibility+threads | Toy ++ only |

### 1.1 Clarifying questions (ask aloud)

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Multi counters? | named | Registry |
| F2 | Step? | delta | API |
| F3 | Bounds? | min/max optional | Policy |
| F4 | Reset? | yes | Op |
| F5 | Listeners? | onChange | Observer |
| F6 | Persist? | interface | Store |
| F7 | Atomic? | yes | Concurrency |
| F8 | TTL? | optional | Policy |
| F9 | Namespaces? | yes | Key |
| F10 | Init? | configurable | Factory |
| F11 | Batch? | optional | API |
| F12 | Consistency? | strong local | Doc |

**MVP scope:**

1. CounterRegistry get-or-create
2. Atomic increment/decrement/get
3. Optional bounds policy
4. Reset
5. Listener callbacks
6. In-memory store + Store interface

**Out of MVP:**

- Global CRDT counters
- Prometheus remote write

### 1.2 Scope repeat-back

> Extensible counters with atomic ops, bounds, observers, and swappable persistence.

---

## 2. Non-Functional Requirements

| # | NFR | Target | Why |
|---|-----|--------|-----|
| N1 | Atomicity | no lost updates | Correct |
| N2 | Extensibility | stores/policies | Interview |
| N3 | Perf | low contention | Scale |
| N4 | Listener safety | no deadlock | Care |
| N5 | Testability | fake store | Quality |
| N6 | API clarity | named | UX |
| N7 | Memory | many counters | OK |
| N8 | Fail semantics | surface errors | Honest |

### 2.1 Progressive scale (object-system view)

| Metric | Base | 10× | 100× |
|--------|----------|----------|----------|
| Counters | 100 | 10K | 1M |
| Incr/s | 10K | 100K | 1M |
| Listeners/counter | 0-3 | 0-3 | 0-3 |

---

## 3. Cases

### 3.1 Happy paths

1. inc rides x3 -> get=3
2. bounded rejects overflow
3. listener records

### 3.2 Edge / failure cases

| Case | Behavior |
|------|----------|
| dec below min | reject/clamp |
| unknown | create or error |
| listener throws | isolate |
| concurrent inc | atomic |
| store fail | exception |
| reset notify | yes |

---

## 4. Object Model & Class Diagrams

### 4.1 Responsibilities

Counter, BoundsPolicy, CounterStore, CounterRegistry, CounterListener.

### 4.2 Class diagram (ASCII)

```text
CounterRegistry->Counter
Counter->AtomicLong + BoundsPolicy + Listeners
CounterStore interface
```

### 4.3 Key classes (details)

**inc(delta)**: bounds; CAS; notify.
**Registry**: concurrent map.
**Store**: optional write-through.

---

## 5. Public APIs / Interfaces

```text
long inc(name,delta=1); long dec; long get; void reset; void addListener
```



---

## 6. State Machines

N/A; optional monotonic policies

---

## 7. Concurrency & Consistency

AtomicLong/CAS; ConcurrentHashMap; listeners outside locks.

**Invariants**

- Within bounds if enforced
- Successful inc += delta
- Listener errors don't corrupt value

---

## 8. Extensibility

New CounterStore; SlidingWindowCounter; AsyncListenerDispatcher

---

## 9. Design Deep Dive

### 9.1 Correctness under race

CAS retry; sum of deltas = final under no reset

### 9.2 Performance

No global lock; stripe hot counters; async listeners optional

### 9.3 Persistence mapping (if asked)

Store.save(name,value,version); write-behind optional

### 9.4 Failure handling

Listener exception isolated; store outage fails write-through

---

## 10. Wrap-Up

> Extensible counters: registry of atomic counters with bounds, observers, swappable stores.

**What interviewers listen for**

- Clear entity boundaries and ownership of mutations
- Explicit concurrency story (locks/CAS/sharding)
- Extensibility via strategy/policy objects
- APIs that are idempotent where retries happen
- Honest MVP vs over-engineering

---

## 11. Deeper / Related Interview Questions

### synchronized long?

**Q: Why AtomicLong?**  
A: Scales better

### Distributed?

**Q: Different?**  
A: Redis INCR / CRDT

---

## 12. Appendices

### 12.1 CAS inc

compareAndSet loop

### 12.2 Listener

onChange(name,old,new)

### 12.3 Stores

Memory/Jdbc

### 12.4 Checklist

atomic, bounds, listeners, SPI

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

*End of extensible counter system LLD.*

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
