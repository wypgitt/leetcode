# LLD: Thread-Safe Bounded MPMC Queue (Timeouts + Shutdown)

> **Focus areas:** Ring buffer · Mutex · Conditions · Monotonic timeouts · MPMC · FIFO · Shutdown · signal vs signalAll
> **Style:** LLD interview (clarify → APIs → classes → concurrency invariants → pseudocode → failure modes → race analysis → tests → Q&A)
> **Quality bar:** Explicit lock/condition predicates, while-loop waits, monotonic deadline math, named concurrency tests
> **Interview theme:** Databricks — concurrency / backpressure LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Ring Buffer Layout & Invariants](#4-ring-buffer-layout--invariants)
5. [Concurrency Invariants & Lock Policy](#5-concurrency-invariants--lock-policy)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Shutdown Semantics](#7-failure-modes--shutdown-semantics)
8. [Race Scenario Analysis](#8-race-scenario-analysis)
9. [Tests & Edge Cases](#9-tests--edge-cases)
10. [Complexity & Design Alternatives](#10-complexity--design-alternatives)
11. [Interviewer Q&A (With Answers)](#11-interviewer-qa-with-answers)
12. [Appendices](#12-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: implement a **bounded multi-producer multi-consumer (MPMC) queue** with blocking operations, **timeouts**, strict **FIFO** ordering, and clean **shutdown** that unblocks all waiters.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Scope | In-process bounded queue | Distributed message broker |
| Ordering | Total FIFO | Priority / LIFO |
| Blocking | Timed wait with timeout | Busy spin only |
| Items | Non-null references | Null sentinel without explicit API |
| Databricks lens | Executor task queue, backpressure buffer | Kafka topic |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | API shape? | `enqueue(item, timeout)`, `dequeue(timeout)`, `shutdown()` | Timed blocking |
| F2 | Capacity? | Fixed at construction; never changes | Ring buffer size N |
| F3 | Null items? | **Disallowed** | Validate; throw NPE/IAE |
| F4 | FIFO? | Strict insertion order | Single head/tail |
| F5 | Producers/consumers? | Many of each (MPMC) | One mutex MVP |
| F6 | Timeout semantics? | Return false / empty on timeout | Monotonic clock |
| F7 | Timeout=0? | Try once, no block | Non-blocking try |
| F8 | Timeout=∞? | Block until success or shutdown | `Long.MAX_MS` or overload |
| F9 | Shutdown? | Idempotent; wake all waiters | `ClosedException` or sentinel |
| F10 | After shutdown? | Enqueue fails; dequeue drains then fails | `closed` flag |
| F11 | Fairness? | Best-effort FIFO among waiters | Optional fair lock |
| F12 | Interrupt? | Propagate `InterruptedException` | `Thread.interrupted` policy |
| F13 | size()? | Approximate or exact under lock | Document snapshot |
| F14 | Peek? | Out of MVP | Would need extra API |
| F15 | Close vs shutdown? | Same — `shutdown()` once | No reopen MVP |

**MVP scope:**

1. Fixed-capacity ring buffer backing store.
2. `ReentrantLock` + `notFull` + `notEmpty` conditions.
3. `enqueue` / `dequeue` with monotonic deadline timeouts.
4. `shutdown()` sets `closed`, `signalAll` both conditions.
5. Null items rejected.
6. Named tests for full/empty boundary, shutdown, spurious wakeup.

**Out of MVP:** lock-free Michael-Scott queue, weakly consistent iterators, priority lanes.

### 1.2 Non-functional requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | enqueue/dequeue hot path | O(1) after acquiring lock |
| N2 | Correctness | Linearizable successful ops |
| N3 | No lost wakeups | while-loop + signal discipline |
| N4 | Shutdown latency | All blocked threads wake ≤ ms |
| N5 | Memory | O(capacity) array + O(waiters) threads |

### 1.3 Scope repeat-back

> Bounded MPMC FIFO queue: ring buffer, mutex + two conditions, timed wait using monotonic clock, null disallowed, shutdown unblocks waiters and rejects new enqueues after close.

### 1.4 Core invariant card

```text
INV-1: 0 ≤ count ≤ capacity at all times.
INV-2: Elements in buffer[head..) in FIFO order; count items logically present.
INV-3: Successful enqueue happens iff !closed and space available before timeout.
INV-4: Successful dequeue happens iff !closed or draining remaining and item available.
INV-5: Waiters always re-check predicate in while loop after wakeup.
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
class BoundedMpmcQueue<T>:
  BoundedMpmcQueue(int capacity, QueueOptions opts)
  boolean enqueue(T item, long timeoutMs) throws InterruptedException, ClosedException
  Optional<T> dequeue(long timeoutMs) throws InterruptedException, ClosedException
  int size()                              // snapshot under lock
  int remainingCapacity()
  boolean isClosed()
  void shutdown()                         // idempotent

class QueueOptions:
  boolean fairLock = false                // ReentrantLock(fairLock)
  boolean signalAllOnShutdown = true
  boolean drainOnClose = true           // dequeue can drain existing after close
```

### 2.2 Semantics table

| Method | Success | Timeout | Shutdown |
|--------|---------|---------|----------|
| `enqueue(x, t)` | true if item queued | false if space not available in time | throw `ClosedException` if closed before enqueue |
| `dequeue(t)` | `Optional.of(item)` | `Optional.empty()` if no item in time | after close: drain if policy; then throw or empty |
| `shutdown()` | — | — | wake all; set closed |

**Null policy:** `enqueue(null)` → `NullPointerException` immediately (before lock).

**Interrupt policy:** if interrupted while waiting on condition, clear interrupt or propagate per language — Java: throw `InterruptedException`.

### 2.3 Guarantees

| Property | Guarantee |
|----------|-----------|
| FIFO | Items dequeued in same order enqueued |
| Bounded | `size() ≤ capacity` always |
| Safety | No duplicate consume; no lost item |
| Linearizability | Each successful enqueue/dequeue linearizes at lock release point |
| Shutdown | No indefinite block after `shutdown()` (assuming timeout or wake) |

### 2.4 Error / return model

```text
ClosedException extends Exception   // queue shut down and op cannot complete
// OR use Optional.empty() + isClosed() — pick one; document

Interview pick: throw ClosedException on enqueue after close;
dequeue after drained + closed → throw ClosedException
timeout → false / Optional.empty() without exception
```

---

## 3. Class Diagrams & Responsibilities

### 3.1 Structure

```text
+---------------------------------------------------+
|              BoundedMpmcQueue<T>                   |
|  enqueue / dequeue / shutdown / size               |
+----------+----------------------------------------+
           |
           v
+---------------------------------------------------+
|  lock: ReentrantLock                               |
|  notFull: Condition                                |
|  notEmpty: Condition                               |
|  buffer: Object[]  (ring)                          |
|  head: int   // dequeue index                      |
|  tail: int   // enqueue index                      |
|  count: int                                        |
|  capacity: int                                     |
|  closed: boolean                                   |
+---------------------------------------------------+
```

### 3.2 Field semantics

```text
capacity = buffer.length          // fixed
count    = number of valid items
head     = index of next dequeue
tail     = index of next enqueue

empty: count == 0
full:  count == capacity
```

### 3.3 Helper methods (private)

| Method | Role |
|--------|------|
| `awaitNanos(notFull, deadlineNs)` | timed wait with remaining budget |
| `enqueueLocked(item)` | assume lock held, not full, not closed |
| `dequeueLocked()` | assume lock held, not empty |
| `signalAfterEnqueue()` | `notEmpty.signal()` or signalAll |
| `signalAfterDequeue()` | `notFull.signal()` |
| `shutdownLocked()` | set closed; signalAll both |

---

## 4. Ring Buffer Layout & Invariants

### 4.1 Index advancement

```text
function advance(i):
  return (i + 1) % capacity

enqueueLocked:
  buffer[tail] = item
  tail = advance(tail)
  count++

dequeueLocked:
  item = buffer[head]
  buffer[head] = null          // GC help / null out slot
  head = advance(head)
  count--
  return item
```

### 4.2 Why null-out dequeue slot

Prevents memory leak if T holds references; also detects misuse if null appears (shouldn't if enqueue rejects null).

### 4.3 capacity edge cases

| capacity | Behavior |
|----------|----------|
| 0 | reject at construction `IllegalArgumentException` |
| 1 | classic ping-pong; full/empty flip often — good test |
| large | modulo cheap |

### 4.4 size and remainingCapacity

```text
size(): lock; return count; unlock
remainingCapacity(): lock; return capacity - count; unlock
```

Snapshot — may stale before caller acts (document).

### 4.5 Diagram (capacity=4)

```text
enqueue order: A B C
buffer indices: [ A B C _ ]
head=0 (A), tail=3, count=3

after dequeue A:
[ _ B C _ ] head=1, tail=3, count=2
```

---

## 5. Concurrency Invariants & Lock Policy

### 5.1 Mutex-only MVP

All producers and consumers contend on **one** `ReentrantLock`. Simple linearization story.

```text
Linearization point: successful enqueue/dequeue completes before unlock
```

### 5.2 Condition predicates

| Condition | Wait when | Signal when |
|-----------|-----------|-------------|
| `notFull` | `count == capacity && !closed` | after dequeue frees slot |
| `notEmpty` | `count == 0 && !(closed && drainDone)` | after enqueue adds item |

**Always:**

```text
while (predicate) { await with timeout }
// NOT if (predicate) once
```

### 5.3 Monotonic clock for timeouts

```text
deadlineNs = System.nanoTime() + timeoutMs * 1_000_000L

loop:
  if predicate false: break success path
  remaining = deadlineNs - System.nanoTime()
  if remaining <= 0: return timeout
  notFull.awaitNanos(remaining)   // may spurious wakeup → loop
```

**Never use** `System.currentTimeMillis()` for timeout math — NTP jumps cause hangs or early timeout.

### 5.4 Fair lock option

```text
lock = new ReentrantLock(fairLock)   // opts.fairLock

fair=true  → lower throughput, bounded starvation among threads
fair=false → default barging; higher throughput; possible starvation (rare)
```

**Interview:** start non-fair; mention fair flag if interviewer asks about starvation.

### 5.5 signal vs signalAll strategy

| Event | MVP choice | Rationale |
|-------|------------|-----------|
| one enqueue | `notEmpty.signal()` | wakes one consumer |
| one dequeue | `notFull.signal()` | wakes one producer |
| shutdown | `signalAll` both | all waiters must re-check closed |
| many waiters same condition | signal OK if one slot/item | signalAll safer but thundering herd |

Section 11 expands comparison.

---

## 6. Algorithms & Pseudocode

### 6.1 enqueue(item, timeoutMs)

```text
function enqueue(item, timeoutMs):
  if item == null: throw NullPointerException
  if timeoutMs < 0: throw IllegalArgumentException

  deadlineNs = nanoTime() + toNanos(timeoutMs)
  lock.lock()
  try:
    while count == capacity and not closed:
      remaining = deadlineNs - nanoTime()
      if remaining <= 0:
        return false                    // timeout
      if not notFull.awaitNanos(remaining):
        return false                    // timeout (await false)
    if closed:
      throw ClosedException()
    // space available
    buffer[tail] = item
    tail = (tail + 1) % capacity
    count++
    notEmpty.signal()                   // wake one consumer
    return true
  finally:
    lock.unlock()
```

### 6.2 dequeue(timeoutMs)

```text
function dequeue(timeoutMs):
  if timeoutMs < 0: throw IllegalArgumentException

  deadlineNs = nanoTime() + toNanos(timeoutMs)
  lock.lock()
  try:
    while count == 0:
      if closed:
        throw ClosedException()         // nothing left to drain
      remaining = deadlineNs - nanoTime()
      if remaining <= 0:
        return Optional.empty()
      if not notEmpty.awaitNanos(remaining):
        return Optional.empty()
    item = buffer[head]
    buffer[head] = null
    head = (head + 1) % capacity
    count--
    notFull.signal()
    return Optional.of(item)
  finally:
    lock.unlock()
```

### 6.3 Alternate dequeue policy after shutdown (drain mode)

```text
while count == 0 and not closed:
  await ...
if count == 0 and closed:
  throw ClosedException()
// else dequeue even if closed but count > 0
```

Allows consumers to drain buffered work after shutdown signal — common pattern.

### 6.4 shutdown()

```text
function shutdown():
  lock.lock()
  try:
    if closed: return
    closed = true
    notEmpty.signalAll()
    notFull.signalAll()
  finally:
    lock.unlock()
```

Idempotent; safe to call multiple times.

### 6.5 tryEnqueue / tryDequeue (timeout=0)

```text
enqueue(item, 0):
  lock; if count==capacity or closed: return false/throw; else insert; unlock
```

No await branch taken when space/item immediately available.

### 6.6 await helper with spurious wakeup

```text
function awaitUntil(notFull, deadlineNs):
  while true:
    remaining = deadlineNs - nanoTime()
    if remaining <= 0: return false
    notFull.awaitNanos(remaining)
    // spurious or signal → return to caller while-loop
    return true    // actually caller while re-checks predicate
```

Spurious wakeup: `await` returns without signal — outer `while` re-evaluates `count==capacity`.

### 6.7 InterruptedException path

```text
catch InterruptedException:
  lock.unlock in finally via lock API
  throw InterruptedException          // Java: preserve interrupt status per spec
```

Do not swallow interrupt — tests depend on it.

---

## 7. Failure Modes & Shutdown Semantics

### 7.1 Shutdown vs blocked producers

| State | Producer blocked on full | After shutdown |
|-------|--------------------------|----------------|
| | waiting on notFull | wake; see closed; throw ClosedException |
| | not yet enqueued | never enters queue |

### 7.2 Shutdown vs blocked consumers

| State | Consumer blocked on empty | After shutdown |
|-------|---------------------------|----------------|
| drain=true | waiting | if items remain, dequeue succeeds; else ClosedException |
| drain=false | waiting | immediate ClosedException on wake |

### 7.3 Timeout vs signal race

```text
Thread C: waiting on notEmpty, 100ms left
Thread P: enqueue → signal
Thread C: wakes, sees count>0, dequeues — success (not timeout)
```

If signal after timeout check but before await — OK; await returns immediately if condition already true? **Still need while loop** — Mesa semantics.

### 7.4 Lost wakeup prevention

Lost wakeup happens if `if (empty) await` without loop and signal occurs between check and await.

**Fix:** always `while` + hold lock across check/wait.

### 7.5 Exception safety

If `enqueueLocked` throws after slot reserved — use complete-or-rollback inside lock; MVP ops don't throw mid-mutation except OOM.

---

## 8. Race Scenario Analysis

### 8.1 Full boundary — two producers

| Step | P1 | P2 | count |
|------|----|----|-------|
| 1 | lock; see full | blocked | cap |
| 2 | await notFull | blocked | cap |
| 3 | consumer dequeues; signal | blocked | cap-1 |
| 4 | P1 wakes; enqueue; unlock | lock; enqueue | cap |

Only one slot — one producer succeeds first — OK.

**Test:** `test_two_producers_one_slot_serializes`

### 8.2 Empty boundary — two consumers

Symmetric to 8.1.

**Test:** `test_two_consumers_one_item_serializes`

### 8.3 shutdown vs blocked waiters

| Step | Consumer C | Main |
|------|------------|------|
| 1 | lock; count==0; await notEmpty | |
| 2 | | shutdown(); signalAll |
| 3 | wake; count==0; closed → ClosedException | |

**Test:** `test_shutdown_unblocks_blocked_dequeue`

### 8.4 timeout vs signal

| Step | C (dequeue 50ms) | P |
|------|------------------|---|
| 1 | waiting | |
| 2 | | enqueue at 40ms; signal |
| 3 | success dequeue | |

Opposite:

| Step | C | P |
|------|---|---|
| 1 | timeout at 10ms → empty | enqueue at 20ms |

**Test:** `test_signal_before_timeout_succeeds`
**Test:** `test_timeout_before_enqueue_returns_empty`

### 8.5 spurious wakeup

Simulate by wrapping condition in test double that returns without state change — consumer must not dequeue from empty.

**Test:** `test_spurious_wakeup_rechecks_predicate`

### 8.6 enqueue after shutdown

| Step | P | |
|------|---|---|
| 1 | | shutdown |
| 2 | enqueue → ClosedException | |

**Test:** `test_enqueue_after_shutdown_throws`

### 8.7 drain after shutdown

| Step | | C1 | C2 |
|------|---|----|----|
| 1 | enqueue A,B; shutdown | | |
| 2 | | dequeue A | dequeue B |
| 3 | | dequeue → ClosedException | |

**Test:** `test_drain_remaining_after_shutdown`

### 8.8 fair vs non-fair lock

Under extreme contention, fair lock approximates FCFS among lock waiters; non-fair may starve — document as best-effort.

**Test:** `test_fair_lock_no_indefinite_starvation_soft` (statistical)

---

## 9. Tests & Edge Cases

### 9.1 Functional

| Test | Action | Expect |
|------|--------|--------|
| `test_fifo_order` | enqueue 1,2,3 | dequeue 1,2,3 |
| `test_capacity_one` | alt enqueue/dequeue | no overlap |
| `test_null_enqueue_rejected` | enqueue(null) | NPE before block |
| `test_try_enqueue_timeout_zero_full` | full queue | false |

### 9.2 Timeout

| Test | Action | Expect |
|------|--------|--------|
| `test_dequeue_timeout_empty` | no producer | empty ≤ timeout |
| `test_enqueue_timeout_full` | full | false |
| `test_monotonic_deadline_not_wall_clock` | mock nanoTime | no false timeout on clock jump |

### 9.3 Shutdown

| Test | Action | Expect |
|------|--------|--------|
| `test_shutdown_idempotent` | shutdown x2 | no throw |
| `test_shutdown_unblocks_blocked_enqueue` | full + blocked producer | ClosedException |
| `test_drain_remaining_after_shutdown` | see 8.7 | |

### 9.4 Concurrency stress

| Test | Action | Expect |
|------|--------|--------|
| `test_mpmc_stress_1m_ops` | P×C threads | FIFO per consumer pair; count never negative |
| `test_invariant_count_bounds` | random ops | 0≤count≤cap |
| `test_no_duplicate_dequeue` | hash items | each id once |

### 9.5 Interrupt

| Test | Action | Expect |
|------|--------|--------|
| `test_interrupt_during_dequeue` | interrupt waiter | InterruptedException |

### 9.6 Edge matrix

| Edge | Handling |
|------|----------|
| capacity=0 | reject ctor |
| timeoutMs=Long.MAX_VALUE | practical infinite block |
| shutdown during enqueue critical section | closed visible before or after — still safe |
| many signalAll on shutdown | thundering herd OK at shutdown |
| item reference aliasing | queue stores references — caller mutating object is their bug |

---

## 10. Complexity & Design Alternatives

### 10.1 Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| enqueue | O(1) | plus lock wait |
| dequeue | O(1) | plus lock wait |
| shutdown | O(W) | W = waiters awakened |
| space | O(capacity) | array |

### 10.2 vs `java.util.concurrent.ArrayBlockingQueue`

JDK queue is close cousin — interview wants you to derive conditions yourself.

| Feature | Our API | ArrayBlockingQueue |
|---------|---------|-------------------|
| Timeout | explicit ms | `offer/poll(timeout, unit)` |
| Shutdown | explicit | no direct shutdown — use poison |
| Fair lock | option | optional ctor param |

### 10.3 Lock-free MPMC (Phase 2 mention)

Michael-Scott queue — unbounded linked; bounded lock-free harder (array + CAS slots). Higher throughput, no mutex, complex memory ordering.

**When to pivot:** interviewer asks for max QPS microbenchmark.

### 10.4 Separate locks for head/tail

Two-lock queue (not MPMC safe for one buffer) — classic **not** applicable to single ring MPMC without careful design — stick one lock.

### 10.5 Backpressure story

When full, producers block or timeout — natural backpressure for executor pipelines.

---

## 11. Interviewer Q&A (With Answers)

| # | Question | Strong answer |
|---|----------|---------------|
| Q1 | Why while not if around await? | Mesa semantics — spurious wakeups and state changes between check and wait require re-check loop. |
| Q2 | signal vs signalAll on enqueue? | `signal` wakes one consumer — sufficient when one item added; `signalAll` causes thundering herd. |
| Q3 | When signalAll? | On shutdown all waiters must re-evaluate closed predicate — use signalAll both conditions. |
| Q4 | Monotonic vs wall clock? | `nanoTime` immune to NTP adjustments; wall clock can cause incorrect timeouts. |
| Q5 | Fair lock trade-off? | Fair `ReentrantLock(true)` reduces starvation, increases lock handoff overhead. |
| Q6 | What linearization point? | Successful op completes before releasing mutex — ops appear atomic. |
| Q7 | Poison pill vs shutdown? | Poison requires sentinel values; shutdown flag avoids null sentinel and unifies wake logic. |
| Q8 | Can dequeue return empty after shutdown? | If drain policy and items remain, return items until empty then throw/empty. |
| Q9 | Memory visibility? | Lock unlock/lock establishes happens-before; fields updated only under lock. |
| Q10 | Lost wakeup scenario? | `if empty await` without loop — fix with while + hold lock. |
| Q11 | Why null-out slot on dequeue? | Prevent strong refs; catch accidental null enqueue if policy violated. |
| Q12 | size() exact? | Exact under lock at instant of read; stale immediately after unlock. |
| Q13 | Performance bottleneck? | Single mutex; scale via sharded queues (N queues hash item key). |
| Q14 | Compare to BlockingQueue? | Same building blocks; show you know condition predicates. |
| Q15 | JCStress / TSAN? | Model tests for linearizability and no double consume under race. |

**signal vs signalAll summary table**

| Scenario | signal | signalAll |
|----------|--------|-----------|
| 1 enqueue, 1 consumer waiting | ✅ preferred | works, wasteful |
| 1 dequeue, 1 producer waiting | ✅ preferred | wasteful |
| shutdown | ❌ may leave waiters | ✅ required |
| many consumers, many items enqueued one-by-one | repeated signal per enqueue | unnecessary herd |

**Traps**

| Trap | Wrong | Right |
|------|-------|-------|
| `if (full) await` | lost wakeup | `while (full) await` |
| wall clock timeout | time jump bugs | nanoTime deadline |
| signal before state change | waiter misses | mutate buffer then signal |
| forget signal on shutdown | hung threads | signalAll |

---

## 12. Appendices

### A. Options defaults (interview)

```text
capacity          = 1024   // must be > 0
fairLock          = false
drainOnClose      = true
signalAllOnShutdown = true
defaultTimeoutMs  = 0 for try; Long.MAX_VALUE for block overload
```

### B. Metrics (if wrapped in service)

```text
queue_depth
queue_enqueue_timeouts_total
queue_dequeue_timeouts_total
queue_closed_total
queue_waiters{condition=notFull|notEmpty}
```

### C. Minimal Java-like sketch

```text
class BoundedMpmcQueue<T> {
  final Object[] buf;
  final ReentrantLock lock;
  final Condition notFull, notEmpty;
  int head, tail, count;
  boolean closed;

  boolean enqueue(T item, long timeoutMs) throws InterruptedException {
    Objects.requireNonNull(item);
    long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(timeoutMs);
    lock.lockInterruptibly();
    try {
      while (count == buf.length && !closed) {
        if (!awaitNanos(notFull, deadline)) return false;
      }
      if (closed) throw new ClosedException();
      buf[tail] = item;
      tail = (tail + 1) % buf.length;
      count++;
      notEmpty.signal();
      return true;
    } finally { lock.unlock(); }
  }
}
```

### D. Related docs

| Doc | Relationship |
|-----|--------------|
| `buffered-writer-lld-system-design.md` | Producer backpressure patterns |
| `chat-deletion-concurrent-sends-lld-system-design.md` | Condition/wait discipline |
| `durable-event-writer-lld-system-design.md` | Tail reader blocking |

### E. Whiteboard timing (45 min)

5 clarify · 8 API/fields · 12 enqueue/dequeue pseudocode · 10 races · 5 shutdown · 5 tests · 5 Q&A

### F. Glossary

| Term | Meaning |
|------|---------|
| Mesa semantics | Signal does not instantly transfer lock; waiter re-checks predicate |
| Spurious wakeup | await returns without matching signal — harmless with while |
| Thundering herd | signalAll wakes many threads; most go back to sleep |
| drainOnClose | Consumers may dequeue remaining items after shutdown |

---

*End of LLD prep.*
