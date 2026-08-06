# LLD / OOD: Randomized Set

> **Focus areas:** O(1) insert/remove/getRandom · Array+HashMap · Swap-delete · Uniform RNG  
> **Style:** Object-oriented interview design (clarify → NFRs → cases → classes → APIs → state machines → concurrency → extensibility → deep dive → wrap-up → Q&A)  
> **Quality bar:** Clear responsibilities, race-safe critical sections, extensibility without rewrite, honest complexity  
> **Interview theme:** Uber — **RandomizedSet data structure LLD**

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

Goal: design a structure supporting insert, delete, getRandom in average O(1).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | RandomizedSet ADT | Distributed set |
| Ops | insert/remove/getRandom | Range queries |
| Uber lens | Correct uniform O(1) | Trick only |

### 1.1 Clarifying questions (ask aloud)

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Insert? | bool new | Set |
| F2 | Remove? | bool existed | Swap-del |
| F3 | getRandom? | uniform | RNG |
| F4 | Dupes? | no | Set |
| F5 | Empty get? | throw | Policy |
| F6 | Thread-safe? | ask | Optional |
| F7 | Seed? | inject RNG | Tests |
| F8 | Generics? | later | Nice |
| F9 | size? | O(1) | Yes |
| F10 | null? | disallow | Policy |
| F11 | clear? | optional | O(n) |
| F12 | persist? | out | - |

**MVP scope:**

1. O(1) avg insert/remove/getRandom
2. Uniform
3. No dupes
4. Injectable Random

**Out of MVP:**

- Weighted random
- Lock-free exotic

### 1.2 Scope repeat-back

> Array + index map RandomizedSet with swap-remove; optional sync wrapper.

---

## 2. Non-Functional Requirements

| # | NFR | Target | Why |
|---|-----|--------|-----|
| N1 | Time | avg O(1) | Req |
| N2 | Uniform | equal p | Correct |
| N3 | Memory | O(n) | OK |
| N4 | Testable | RNG inject | Quality |
| N5 | Safety | document races | Honest |
| N6 | Simple | readable | Interview |
| N7 | No hidden scans | critical | Perf |
| N8 | API clear | bool returns | UX |

### 2.1 Progressive scale (object-system view)

| Metric | Base | 10× | 100× |
|--------|----------|----------|----------|
| n | 1K | 100K | 10M |
| ops/s | high | high | cache |
| threads | 1 | 8 | 64 |

---

## 3. Cases

### 3.1 Happy paths

1. insert 1,2,3 random ~uniform
2. remove 2 -> {1,3}
3. dup insert false

### 3.2 Edge / failure cases

| Case | Behavior |
|------|----------|
| remove miss | false |
| empty random | throw |
| remove last | ok |
| swap self | ok |
| rng bias | nextInt(size) |

---

## 4. Object Model & Class Diagrams

### 4.1 Responsibilities

RandomizedSet owns vals[] + idx map; Random abstracted.

### 4.2 Class diagram (ASCII)

```text
RandomizedSet<T>
- vals:List
- idx:Map
- rng
+ insert/remove/getRandom
```

### 4.3 Key classes (details)

remove: swap with last, update idx, pop. getRandom: vals[rng.nextInt(n)].

---

## 5. Public APIs / Interfaces

```text
boolean insert(v); boolean remove(v); T getRandom();
```



---

## 6. State Machines

Invariant: idx[v]=i iff vals[i]=v

---

## 7. Concurrency & Consistency

MVP single-thread; synchronized wrapper optional.

**Invariants**

Bijection vals<->idx; no holes; empty getRandom invalid

---

## 8. Extensibility

Generics; separate WeightedRandomizedSet

---

## 9. Design Deep Dive

### 9.1 Correctness under race

Property test set(vals)==idx.keys after random ops

### 9.2 Performance

Hash avg O(1); array helps locality

### 9.3 Persistence mapping (if asked)

Snapshot vals; rebuild idx

### 9.4 Failure handling

Empty->IllegalStateException

---

## 10. Wrap-Up

> RandomizedSet = list + value->index map; swap-delete; nextInt(size).

**What interviewers listen for**

- Clear entity boundaries and ownership of mutations
- Explicit concurrency story (locks/CAS/sharding)
- Extensibility via strategy/policy objects
- APIs that are idempotent where retries happen
- Honest MVP vs over-engineering

---

## 11. Deeper / Related Interview Questions

### List only?

**Q: Why not?**  
A: remove O(n)

### Map only?

**Q: Why not?**  
A: no O(1) uniform

---

## 12. Appendices

### 12.1 Remove

swap last; update idx; pop

### 12.2 Complexity

all avg O(1)

### 12.3 Tests

freq/empty/dup

### 12.4 Checklist

swap, index, nextInt

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

*End of randomized set LLD.*

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
