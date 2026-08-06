# LLD: In-Memory KV Store with Per-Key Sliding-Window QPS

> **Focus areas:** 60s sliding window · Ring buffer vs bucketed counters · getQps hooks · Lazy per-key counters · Prune logic
> **Style:** LLD interview (clarify → API → classes → concurrency invariants → pseudocode → failure/recovery → tests → Q&A)
> **Quality bar:** Accurate per-key QPS without lost updates; O(60) bucket memory or capped ring per key
> **Interview theme:** Databricks — signature storage/concurrency LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Core Data Structures & Algorithms](#4-core-data-structures--algorithms)
5. [Concurrency Invariants & Race Analysis](#5-concurrency-invariants--race-analysis)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Tests & Edge Cases](#8-tests--edge-cases)
9. [Complexity & Scalability Notes](#9-complexity--scalability-notes)
10. [Wrap-Up](#10-wrap-up)
11. [Interviewer Q&A (with Answers)](#11-interviewer-qa-with-answers)
12. [Appendices](#12-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: Design an **in-memory KV store** with **per-key sliding-window QPS** over a **60-second window**, exposing `getQps(key)` and recording ops on **`get`** and **`put`**.

### 1.0 What this is / is not

| Dimension | This design | Not this |
|-----------|-------------|----------|
| Scope | Single-node KV + metrics | Cluster-wide rate limiter service |
| Window | 60s **sliding** | Fixed calendar minute |
| Counted ops | get + put (configurable mask) | All HTTP traffic globally |
| Structure | Ring buffer of timestamps OR 1s buckets | Single global counter |
| Databricks lens | Hot-key detection / throttle hooks | Full billing pipeline |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | KV ops? | get, put, delete | Standard map semantics |
| F2 | Window size? | 60 seconds | prune events ≤ now−60000ms |
| F3 | QPS definition? | count(window) / 60.0 | double ops/sec |
| F4 | Which ops count? | get and put | Bitmask enum OpKind |
| F5 | Per-key state? | Lazy create on first op | `computeIfAbsent` |
| F6 | Precision? | 1s buckets MVP; ring optional | memory vs accuracy tradeoff |
| F7 | Thread safety? | Required | per-key lock or synchronized counter |
| F8 | Clock? | `System.currentTimeMillis()` or nano | document NTP jump policy |
| F9 | delete(key)? | Remove value + QPS state | both maps |
| F10 | Hot key 100k ops/s? | Ring cap or bucket only | document bias when ring drops |
| F11 | getQps missing key? | return 0.0 | no counter allocated |
| F12 | Global aggregate QPS? | Phase 2 | sum expensive; HLL approximate |

**MVP scope:**

1. `ConcurrentHashMap` for key → value.
2. `ConcurrentHashMap` for key → `SlidingWindowCounter`.
3. On get/put: record timestamp (ring) or increment bucket.
4. `getQps(key)` prunes stale data, returns `count / 60.0`.
5. Lazy counter allocation.
6. Thread-safe increments — no lost updates.

### 1.2 Scope repeat-back

> In-memory KV with per-key 60s sliding-window QPS: bucketed counters default, ring buffer alternative for exact capped history, hooks on get/put, lazy counters, explicit prune on read and amortized on write.

### 1.3 Core invariant

```text
getQps(k) == (number of recorded get/put ops for k with timestamp in (now−60000ms, now]) / 60.0

Counter updates atomic w.r.t. op recording — no lost increments under concurrent ops on same key.
Prune removes only events with timestamp ≤ now − windowMs.
```

---


## 2. APIs & Guarantees

### 2.1 Public API

```text
class KVWithQps:
  KVWithQps(QpsOptions opts)

  Optional<byte[]> get(String key)
  void put(String key, byte[] value)
  void delete(String key)
  double getQps(String key)              // ops per second over 60s window
  long getOpCount(String key)              // raw count in window
  QpsStats stats()                         // aggregate metrics
  void shutdown()

class QpsOptions:
  long windowMs = 60_000
  int bucketSeconds = 1                    // 60 buckets
  int ringCapacity = 0                     // 0 = buckets only; >0 enables ring
  EnumSet<OpKind> countedOps = {GET, PUT}
  long idleKeyTtlMs = 0                    // 0 = no TTL

enum OpKind { GET, PUT, DELETE }

class SlidingWindowCounter:
  void recordOp(long nowMs, OpKind kind)
  long count(long nowMs)
  double qps(long nowMs)
  void prune(long nowMs)
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
| KV correctness | Standard hash map get/put/delete |
| QPS accuracy (buckets) | ±1s boundary error |
| QPS accuracy (ring) | Exact within capacity cap |
| Thread safety | Concurrent get/put/getQps |
| Monotonicity | Count non-increasing only after prune evicts stale |
| Lazy init | No counter until first counted op on key |
| delete cleanup | Removes value and counter entry |

### 2.3 Error model

```text
InvalidArgumentException  — null key, null value if disallowed
ClosedException           — after shutdown
```

---


## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Responsibility |
|-------|----------------|
| `KVWithQps` | Facade wiring KV ops + QPS hooks |
| `ValueStore` | `ConcurrentHashMap<String, byte[]>` |
| `QpsTracker` | `ConcurrentHashMap<String, SlidingWindowCounter>` |
| `SlidingWindowCounter` | Ring or bucket logic for one key |
| `BucketCounter` | 60 × atomic long, second index |
| `TimestampRing` | Circular buffer of event ms |
| `PrunePolicy` | When to call prune (on read, write, both) |
| `QpsMetrics` | hot keys, prune latency, tracked keys |

### 3.2 Data flow

```text
put(key, val):
  valueStore.put(key, val)
  counter = qpsTracker.computeIfAbsent(key, SlidingWindowCounter::new)
  counter.recordOp(now, PUT)

get(key):
  val = valueStore.get(key)
  counter = qpsTracker.computeIfAbsent(key, SlidingWindowCounter::new)
  counter.recordOp(now, GET)
  return val

getQps(key):
  c = qpsTracker.get(key)
  if c == null: return 0.0
  lock(c): c.prune(now); return c.count(now) / 60.0
```

---


## 4. Core Data Structures & Algorithms

### 4.1 Bucketed counters (MVP default)

```text
windowMs = 60000
bucketCount = 60
bucketWidthMs = 1000

fields:
  buckets[60] : AtomicLong
  lastPrunedSecond : long

recordOp(nowMs):
  sec = nowMs / 1000
  idx = sec % 60
  buckets[idx].incrementAndGet()
  maybePrune(sec)

prune(nowMs):
  cutoffSec = (nowMs - windowMs) / 1000
  for each bucket index i:
    bucketSec = deriveSecondForIndex(i)  // track epoch alignment
    if bucketSec <= cutoffSec: buckets[i].set(0)

count(nowMs):
  prune(nowMs)
  return sum(buckets)
```

**Epoch alignment trick:** store `baseSecond = now/1000` at creation; bucket `i` represents second `baseSecond - (60-i)`. Simpler MVP: on each prune, zero buckets older than cutoff using `(currentSecond - bucketSecond + 60) % 60`.

### 4.2 Timestamp ring (exact, capped)

```text
ring : long[capacity]   // event timestamps ms
head : int              // next write index
size : int              // valid entries ≤ capacity

recordOp(nowMs):
  if size < capacity:
    ring[head] = nowMs; head = (head+1) % capacity; size++
  else:
    // ring full — drop oldest (advance implicit tail) or reject
    ring[head] = nowMs; head = (head+1) % capacity  // overwrite oldest

prune(nowMs):
  cutoff = nowMs - windowMs
  while size > 0 and ring[(head - size + cap) % cap] < cutoff:
    size--

count: return size after prune
```

### 4.3 Ring vs buckets comparison

| Approach | Memory/key | Accuracy | Hot-key behavior |
|----------|------------|----------|------------------|
| 1s buckets | ~60 × 8 B + overhead | ±1s | Stable memory |
| Timestamp ring | 8 × capacity B | Exact if no drop | Cap truncates oldest |
| Hybrid | buckets + promote to ring | Best of both | Phase 2 |

### 4.4 Complexity

| Op | Buckets | Ring |
|----|---------|------|
| recordOp | O(1) | O(1) |
| prune (lazy) | O(60) worst | O(dropped) |
| getQps | O(60) + O(1) sum | O(capacity) worst |

Amortized: prune every op → expensive; **lazy prune** on getQps and every 1s on write path.

### 4.5 QPS formula

```text
elapsed = min(windowMs, now - firstOpTime)  // optional: avoid divide-by-60 when window partially filled
qps = count / (windowMs / 1000.0)

MVP simplification (interview): always divide by 60.0 even if key is new → document slight underestimate for first minute.
```

---


## 5. Concurrency Invariants & Race Analysis

### 5.1 Shared state

| State | Structure | Protection |
|-------|-----------|------------|
| Values | CHM | CHM intrinsic |
| Counters map | CHM | computeIfAbsent atomic |
| Each counter | buckets[] or ring | `synchronized(counter)` or ReentrantLock |

### 5.2 Lock order

```text
Option A (recommended MVP):
  lock(counter for key K):
    valueStore op (fast)
    recordOp

Option B:
  valueStore op without counter lock
  then counter.recordOp — risk: QPS lags KV by one op interleaving
  Acceptable for metrics; document approximate ordering

Never hold two counter locks.
```

### 5.3 Invariants

| # | Invariant |
|---|-----------|
| I1 | Every counted get/put calls recordOp exactly once |
| I2 | prune only removes timestamps ≤ now − windowMs |
| I3 | count never negative |
| I4 | delete removes counter entry — getQps returns 0 |
| I5 | Bucket index derived from consistent clock reading per op |
| I6 | No lost increments (use AtomicLong per bucket) |

### 5.4 Race: lost increment (WRONG vs RIGHT)

**WRONG (plain int bucket):**

```text
Thread A: read buckets[5] = 10
Thread B: read buckets[5] = 10
Thread A: write 11
Thread B: write 11   // lost update — true QPS was 12 events
```

**RIGHT:**

```text
buckets[idx].incrementAndGet()
```

### 5.5 Race: getQps during burst of puts

Without prune lock, getQps might read partial prune. Fix: `synchronized(counter)` around prune+count.

Timeline:

```text
t=0   puts record in bucket 5
t=1   getQps starts prune (needs lock)
t=2   put waits on lock
t=3   getQps finishes count=1
t=4   put records — next getQps sees 2
```

Linearizable w.r.t. counter if recordOp and getQps share lock.

---


## 6. Algorithms & Pseudocode

### 6.1 put with QPS hook

```text
function put(key, value):
  if shutdown: throw ClosedException
  counter = qpsTracker.computeIfAbsent(key, k -> new SlidingWindowCounter(opts))
  lock(counter):
    valueStore.put(key, value)
    if COUNT_PUT in opts.countedOps:
      counter.recordOp(currentTimeMs(), PUT)
```

### 6.2 get with QPS hook

```text
function get(key):
  counter = qpsTracker.computeIfAbsent(key, ...)
  lock(counter):
    value = valueStore.get(key)
    if COUNT_GET in opts.countedOps:
      counter.recordOp(currentTimeMs(), GET)
    return Optional.ofNullable(value)
```

### 6.3 getQps with prune

```text
function getQps(key):
  counter = qpsTracker.get(key)
  if counter == null: return 0.0
  now = currentTimeMs()
  lock(counter):
    counter.prune(now)
    return counter.count(now) / (opts.windowMs / 1000.0)
```

### 6.4 Bucket recordOp + prune

```text
function recordOp(nowMs, kind):
  sec = nowMs / 1000
  idx = (int)(sec % bucketCount)
  buckets[idx].incrementAndGet()
  lastSeenSecond = max(lastSeenSecond, sec)
  if nowMs - lastPruneMs > 1000:
    prune(nowMs)
    lastPruneMs = nowMs

function prune(nowMs):
  cutoffSec = (nowMs - windowMs) / 1000
  curSec = nowMs / 1000
  for s from lastPrunedSecond+1 to curSec:
    if s <= cutoffSec:
      idx = (int)(s % bucketCount)
      buckets[idx].set(0)
  lastPrunedSecond = curSec
```

### 6.5 delete

```text
function delete(key):
  valueStore.remove(key)
  qpsTracker.remove(key)
```

### 6.6 Lazy counter lifecycle

```text
// Counter created on first get/put for key — not on getQps alone
// Optional idle TTL sweeper (Phase 2):
background every T seconds:
  for (key, counter) in qpsTracker:
    if counter.isIdle(idleTtl): qpsTracker.remove(key)
```


### 6.A Linearization points (say aloud)

```text
put: linearizes at map.replace(key, blob) under per-key lock
get: linearizes at tag check + deserialize after blob read
getQps: linearizes at prune+count under counter lock
get (hit counter): linearizes at incrementAndGet after successful map lookup
```

### 6.B Shutdown / close path

```text
close():
  closed = true (volatile)
  reject new ops with ClosedException
  optional: drain metrics, snapshot counters
  release thread pools if any background prune workers exist
```

### 6.C Metrics hook points

```text
on_op_start(op_type, key)
try:
  execute core logic
  on_op_success(op_type, latency_ms)
catch (e):
  on_op_error(op_type, e.class)
  rethrow
```

### 6.D Property-test skeleton

```text
@RepeatedTest(200)
void concurrent_random_ops():
  replay_model = SerialModel()
  run_random_ops_parallel(store, replay_model)
  assert store_state == replay_model.state
  assert counters == replay_model.counters
```


## 7. Failure Modes & Recovery

| Scenario | Effect | Mitigation |
|----------|--------|------------|
| Ring overflow on hot key | Oldest events dropped | QPS underestimate; cap + metric |
| Clock jump forward | Stale buckets | Full prune; temporary dip |
| Clock jump backward | Events look "future" | Clamp timestamps to now |
| Lazy counter leak | Memory for idle keys | TTL sweeper Phase 2 |
| Forgot prune | Over-count | Always prune in getQps |
| Lost bucket increment | Under-count QPS | AtomicLong buckets |
| delete then getQps | 0 | Counter removed |



### 7.A Dependency / resource failure matrix

| Resource | Symptom | Mitigation | Client impact |
|----------|---------|------------|---------------|
| Memory pressure | OOM on large values | max_entry_bytes cap | InvalidArgument |
| Lock contention | p99 latency spike | Striped locks / atomics | Slower, still correct |
| Registry misconfig | UnknownTypeTag at read | freeze() + integration tests | Fail fast at startup |
| Clock jump (QPS) | Stale or inflated QPS | monotonic clock + full prune | Temporary metric skew |

### 7.B Recovery narrative (whiteboard)

1. Identify whether failure is **logic** (bug) vs **resource** (OOM, timeout).
2. For logic bugs: reproduce with stress test; fix invariant violation.
3. For resource: apply backpressure; bound structures; alert on threshold.
4. Verify with TSan + deterministic replay test before closing incident.


## 8. Tests & Edge Cases

### 8.1 Functional tests

1. New key: `getQps(k) == 0`
2. 60 puts in 1 second, wait 0s → `getQps ≈ 60/60 = 1.0` (bucket) or 1.0 (ring)
3. 60 puts in 1s, wait 61s, prune → `getQps == 0`
4. delete key → getQps 0; get returns empty
5. Only get ops counted if mask = GET only
6. Window boundary: op at t=0, query at t=60001 → not counted

### 8.2 Concurrency tests

```text
@Test void concurrent_puts_same_key_exact_count() {
  String key = "hot";
  int N = 50, M = 2000;
  ExecutorService pool = Executors.newFixedThreadPool(N);
  CountDownLatch start = new CountDownLatch(1);
  for (int t = 0; t < N; t++)
    pool.submit(() -> { start.await(); for (int i=0;i<M;i++) store.put(key, b); });
  start.countDown();
  pool.shutdown(); pool.awaitTermination(30, SECONDS);
  assertEquals(N * M, store.getOpCount(key));
}
```

### 8.3 Ring vs bucket equivalence (approximate)

Run 1000 random ops; compare bucket QPS vs ring QPS; assert within 5% for steady load.

### 8.4 Prune correctness

Insert synthetic timestamps; call prune; assert all remaining > cutoff.



### 8.A Stress harness (JUnit-style)

```text
@Test
void stress_concurrent_ops() throws Exception {
  int N = 32, M = 10_000;
  ExecutorService pool = Executors.newFixedThreadPool(N);
  CountDownLatch start = new CountDownLatch(1);
  CountDownLatch done = new CountDownLatch(N);
  AtomicReference<Throwable> err = new AtomicReference<>();
  for (int t = 0; t < N; t++) {
    pool.submit(() -> {
      try {
        start.await();
        for (int i = 0; i < M; i++) randomOp();
      } catch (Throwable e) { err.compareAndSet(null, e); }
      finally { done.countDown(); }
    });
  }
  start.countDown();
  assertTrue(done.await(60, SECONDS));
  assertNull(err.get());
  assertInvariants();
}
```

### 8.B Golden replay

Capture op log from failing stress run; replay single-threaded through reference model; diff final state.

### 8.C Fuzz dimensions

Null keys, max-size payloads, rapid open/close, type overwrite on same key, clock skew injection (QPS).


## 9. Complexity & Scalability Notes

Memory: `keys × (60 × 8 bytes)` for buckets + CHM overhead. 1M keys ≈ 480 MB bucket arrays — need idle eviction at scale.

Integrate with rate limiter:

```text
if (store.getQps(key) > limit) throw RateLimitedException;
store.put(key, value);  // record after or before — document policy
```



### 9.A Load assumptions (state numbers)

```text
distinct_keys     = 1_000_000
hot_key_fraction  = 0.001        # 1000 keys at 10× average rate
peak_get_qps      = 200_000
peak_put_qps      = 20_000
avg_value_bytes   = 256
window_seconds    = 60
```

### 9.B Bottleneck table

| Symptom | Likely cause | Next lever |
|---------|--------------|------------|
| p99 get latency | lock stripes too few | increase stripe count |
| QPS prune slow | O(window) per getQps | amortize prune on write path |
| hit counter hot | single AtomicLong | LongAdder or sharded counters |
| memory growth | idle QPS counters | TTL eviction for cold keys |

### 9.C Scale path

| Multiplier | Move |
|------------|------|
| 10× | striped locks; pre-serialize outside lock |
| 100× | shard store by key hash; aggregate metrics async |
| 1000× | partition cells; approximate global QPS with HLL |


## 10. Wrap-Up

**Design summary**

- KV store + **parallel QpsTracker** map
- **Bucketed counters** for O(60) memory; **ring** for exact capped history
- **recordOp** on get/put hooks; **prune** on getQps (and amortized on write)
- **AtomicLong** buckets prevent lost updates

**MVP vs later**

| MVP | Later |
|-----|-------|
| 1s buckets | Hybrid hot-key ring |
| divide by 60 always | elapsed-aware QPS |
| no idle eviction | TTL sweeper |

**Top risks**

1. Lost updates on non-atomic bucket increment
2. Forgetting prune → inflated QPS
3. Ring drop on hot key silently under-reports

---

## 11. Interviewer Q&A (with Answers)

### Q1. Ring buffer vs bucketed counters?

Buckets: fixed 60×8 bytes, O(60) prune, ±1s error. Ring: O(capacity) memory, exact event times, but drops oldest when full. MVP buckets; ring for hot-key drill-down.

### Q2. Why lazy counters?

Avoid allocating SlidingWindowCounter for keys never accessed. create on first get/put via computeIfAbsent.

### Q3. Should getQps alone create a counter?

No — otherwise scanners inflate memory. Return 0 if absent.

### Q4. Where to call prune?

Mandatory on getQps; amortize on write every ~1s to keep getQps O(1) amortized.

### Q5. How handle 100k QPS on one key?

Buckets still O(1) record; ring would spin — use buckets only. Optionally sample (1/10 events) Phase 2.

### Q6. Compare to leaky bucket rate limiter?

Sliding window counts actual ops in interval; leaky bucket smooths allowance. QPS here is observability, not enforcement — but can feed limiter.

### Q7. Monotonic clock?

`System.nanoTime()` for intervals; wall clock for bucket alignment. Document NTP jump: full prune.

### Q8. Global QPS?

Sum per-key is expensive; maintain separate LongAdder for global or HLL sketch.

### Q9. Thread safety for two maps?

Per-key counter lock ties KV op + recordOp; or accept benign reordering between maps.

### Q10. delete semantics?

Remove from both maps immediately; subsequent getQps=0.

### Q11. Double-count delete?

MVP: delete not counted; mask OpKind if product wants.

### Q12. Integration test for 60s window?

Use injectable Clock; fake time advance 61s — deterministic, no sleep.

### Q13. Bucket alignment at second boundary?

Ops at 999ms and 1000ms land in adjacent buckets — acceptable ±1s error.

### Q14. Memory bound?

idleKeyTtl sweeper; cap max tracked keys with LRU eviction of counters.

### Q15. Interview sound bite?

`getQps = prune + count / 60`; hooks on get/put; AtomicLong buckets for correctness.

## 12. Appendices

### A. Complexity summary

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| put / get (KV) | O(1) avg + serialize | O(1) per entry | Hash map |
| get with type check | O(1) + deserialize | O(1) | Tag compare first |
| getQps | O(B) buckets or O(K) ring | O(B) or O(K) per key | B=60 buckets |
| hit increment | O(1) atomic | O(1) | AtomicLong |
| scan keys() | O(n) | O(n) output | Not hot path |

### B. Thread-safety checklist

- [ ] Per-key or striped lock order documented
- [ ] No deserialize before TypeTag validation
- [ ] Counter updates use atomics or hold same lock as value op
- [ ] CHM used for concurrent map (never raw HashMap in fixed version)
- [ ] TSan-clean on N-thread stress tests
- [ ] close() rejects new ops and is idempotent

### C. Interview timing (45 min)

| Phase | Minutes | Deliverable |
|-------|---------|-------------|
| Clarify + scope | 5 | FR table + invariant |
| API + classes | 8 | Public surface on board |
| Data structures | 10 | Ring vs buckets / TypeTag layout |
| Pseudocode | 12 | put/get/getQps or buggy→fixed |
| Concurrency / races | 5 | Timeline or lock order |
| Tests + wrap | 5 | N×M stress + 3 unit tests |

### D. Metrics

```text
typed_kv_ops_total{op=put|get|remove}
typed_kv_type_mismatch_total{type=...}
typed_kv_serialize_bytes{op=put}
qps_per_key{key=...}           # cardinality caution
qps_prune_duration_ms
kv_hit_count
kv_hit_race_undercount         # buggy demo only
```

### E. Related Databricks LLDs

| Doc | Relationship |
|-----|--------------|
| durable-embedded-kv-store | Persistence beneath typed blobs |
| kv-sliding-window-qps | Metrics hooks on get/put |
| kv-race-repair | Correct counter patterns for cache hits |
| persistent-inmemory-cache | Eviction + typed values |

### F. Glossary

| Term | Definition |
|------|------------|
| TypeTag | Stable runtime id identifying serialized type |
| TypedBlob | Stored record: tag + immutable payload bytes |
| Sliding window | Count ops in (now−W, now] |
| Lost update | RMW race where concurrent writes drop increments |
| Linearizable | Ops appear atomic in some serial order |

### G. Injectable clock test

```java
Clock clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
store = new KVWithQps(opts.withClock(clock));
store.put("k", bytes);
assertEquals(1.0/60, store.getQps("k"), 1e-6);
clock.advance(61, SECONDS);
assertEquals(0.0, store.getQps("k"), 1e-6);
```

### H. OpKind bitmask

```text
enum OpKind { GET(1), PUT(2), DELETE(4);
boolean counts = mask.contains(kind);
```
---

*End of LLD prep.*
