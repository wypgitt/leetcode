# LLD: KV Store with Hit Counter — Race Bug Analysis & Fix

> **Focus areas:** Buggy HashMap + hits++ · Fixed ConcurrentHashMap + AtomicLong · Lost-update timeline · N×M stress test
> **Style:** LLD interview (clarify → API → classes → concurrency invariants → pseudocode → failure/recovery → tests → Q&A)
> **Quality bar:** Show broken code first, prove under-count, then fix with atomics and CHM
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

Goal: Present a **buggy KV store with hit counter** (`hits++` on get, unsynchronized `HashMap`), demonstrate **lost updates**, then deliver a **fixed** design with `ConcurrentHashMap` and `AtomicLong`.

### 1.0 What this is / is not

| Dimension | This design | Not this |
|-----------|-------------|----------|
| Purpose | Teaching concurrency bugs + fixes | Production cache |
| Buggy version | Intentionally racy | Ship to prod |
| Hit rule | Increment on successful get (value present) | Increment on put |
| Fix | AtomicLong + CHM | "It works on my machine" |
| Databricks lens | Cache hit metrics on read path | Full observability stack |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | KV ops? | get, put, delete | get triggers hit |
| F2 | Hit on miss? | No | only non-null value |
| F3 | Counter scope? | Global hits MVP; per-key optional | AtomicLong global |
| F4 | Bug demonstration? | N threads × M gets → count << N×M | stress test |
| F5 | Map bug separate? | Yes — HashMap resize races | CHM for fixed |
| F6 | Double counting? | Separate bug: two increment sites | single increment site |
| F7 | put visibility? | Fixed: CHM happens-before | readers see latest |
| F8 | Performance? | AtomicLong vs synchronized | mention LongAdder |
| F9 | Testing? | CountDownLatch barrier | deterministic start |
| F10 | Interview flow? | Buggy → timeline → fix → test | 45 min arc |

**MVP scope:**

1. **BuggyKV**: `HashMap` + plain `long hits` with `hits++` on hit.
2. Stress: N threads, each M gets on same key → expect N×M, observe under-count.
3. **FixedKV**: `ConcurrentHashMap` + `AtomicLong.incrementAndGet()`.
4. Explain read-modify-write non-atomicity with timeline.
5. Optional per-key `ConcurrentHashMap<String, AtomicLong>`.

### 1.2 Scope repeat-back

> Buggy then fixed in-memory KV with global hit counter: document lost-update race on `hits++`, map corruption risk on HashMap, fix with atomics and CHM, prove with N×M stress test.

### 1.3 Core invariant (fixed version)

```text
After N threads each successfully get(sameKey) M times (key exists):
  globalHits.get() == N * M

get miss does not increment hits.
ConcurrentHashMap provides safe publication of put values to get threads.
```

---


## 2. APIs & Guarantees

### 2.1 Public API

```text
class BuggyKV:
  BuggyKV()
  byte[] get(String key)       // UNSAFE: hits++ if non-null
  void put(String key, byte[] value)
  void delete(String key)
  long getHitCount()           // racy read

class FixedKV:
  FixedKV()
  byte[] get(String key)       // globalHits.incrementAndGet() on hit
  void put(String key, byte[] value)
  void delete(String key)
  long getHitCount()
  long getKeyHitCount(String key)   // optional per-key

class FixedKVWithPerKeyHits extends FixedKV:
  // adds keyHits map of AtomicLong
```

### 2.2 Guarantees table

| Property | Buggy | Fixed |
|----------|-------|-------|
| Hit count under concurrency | **Best effort — wrong** | **Exact** N×M |
| KV thread safety | **Unsafe** HashMap | **CHM** linearizable per key |
| get miss | No increment | No increment |
| Visibility of put | Not guaranteed | happens-before via CHM |
| Double increment paths | Demo over-count bug | Single increment site |

### 2.3 Error model

```text
InvalidArgumentException — null key
Buggy: silent wrong hit counts (no exception)
Fixed: stress test assertion failure if regression
```

---


## 3. Class Diagrams & Responsibilities

### 3.1 Buggy architecture (intentionally wrong)

```text
class BuggyKV {
  Map<String, byte[]> map = new HashMap<>();   // NOT thread-safe
  long hits = 0;                              // NOT volatile, NOT atomic

  byte[] get(String key) {
    byte[] v = map.get(key);
    if (v != null) {
      hits++;                                 // LOST UPDATE RACE
    }
    return v;
  }
}
```

### 3.2 Fixed architecture

```text
class FixedKV {
  ConcurrentHashMap<String, byte[]> map = new ConcurrentHashMap<>();
  AtomicLong globalHits = new AtomicLong();

  byte[] get(String key) {
    byte[] v = map.get(key);
    if (v != null) {
      globalHits.incrementAndGet();           // single atomic RMW
    }
    return v;
  }
}
```

### 3.3 Side-by-side

| Component | Buggy | Fixed |
|-----------|-------|-------|
| Map | HashMap | ConcurrentHashMap |
| Counter | long hits++ | AtomicLong |
| Increment | read-modify-write | incrementAndGet |
| Stress N=32,M=10k | often 50k–200k not 320k | exactly 320000 |

---


## 4. Core Data Structures & Algorithms

### 4.1 Lost update pattern (the core bug)

`hits++` compiles to:

```text
LOAD hits → register
ADD register, 1
STORE register → hits
```

Two threads interleave:

```text
Time | Thread A        | Thread B        | hits (memory)
-----|-----------------|-----------------|---------------
t0   | LOAD → 5        |                 | 5
t1   |                 | LOAD → 5        | 5
t2   | ADD → 6         |                 | 5
t3   |                 | ADD → 6         | 5
t4   | STORE 6         |                 | 6
t5   |                 | STORE 6         | 6  ← expected 7
```

**One increment lost.** With N threads, loss rate scales — observed count ≪ N×M.

### 4.2 Double counting pattern (separate bug)

```text
byte[] get(String key) {
  byte[] v = map.get(key);
  if (v != null) {
    metrics.recordHit(key);    // path 1
    hits++;                    // path 2  → 2× increment per get
  }
  return v;
}
```

Fix: **single increment site** or idempotent hit token per request.

### 4.3 HashMap resize race (separate from counter)

JDK HashMap concurrent put/get during resize can infinite loop (Java 7) or lost entries (undefined). **Even fixing hits++ is insufficient** without CHM.

### 4.4 Fix options compared

| Fix | Correctness | Contention on hot counter |
|-----|-------------|---------------------------|
| `hits++` | **No** | N/A |
| `volatile` + `hits++` | **No** — RMW still racy | N/A |
| `synchronized(lock){hits++}` | **Yes** | Serializes all hits |
| `AtomicLong.incrementAndGet()` | **Yes** | CAS retry under contention |
| `LongAdder.increment()` | **Yes** (sum eventually) | Lower contention |
| Sharded counters[256] | **Yes** | Partition by key hash |

### 4.5 C++ equivalent

```text
std::atomic<int64_t> hits;
void on_hit() { hits.fetch_add(1, std::memory_order_relaxed); }
```

Relaxed order sufficient for counter; CHM equivalent: `concurrent_hash_map`.

---


## 5. Concurrency Invariants & Race Analysis

### 5.1 Buggy violations

| # | Violation |
|---|-----------|
| B1 | Non-atomic RMW on shared `hits` |
| B2 | HashMap concurrent mutation without sync |
| B3 | No happens-before between put and get |
| B4 | Plain read of `hits` in getHitCount may see stale value |

### 5.2 Fixed invariants

| # | Invariant |
|---|-----------|
| F1 | Exactly one atomic increment per successful get hit |
| F2 | No increment on miss (null value) |
| F3 | CHM get/put per-key atomicity |
| F4 | globalHits monotonically non-decreasing |
| F5 | increment happens-after map.get confirms non-null |
| F6 | Single increment site in codebase |

### 5.3 Lost update timeline (whiteboard)

Draw horizontal timelines for threads A and B:

```text
        A: ──LOAD(5)────ADD──STORE(6)──────────────►
        B: ────────LOAD(5)────ADD──STORE(6)────────►
hits:   5 ──────────────────────────────────────► 6 (not 7)
```

Ask interviewer: "Expected 7; observed 6 — classify as lost update."

### 5.4 JMM happens-before (Java)

`AtomicLong.incrementAndGet()` establishes happens-before with subsequent `get()`. Plain `hits++` has **no** such guarantee — another thread may never see updates correctly even without concurrent increments.

### 5.5 Ordering: check null before increment

```text
v = map.get(key)
if (v != null) hits.increment()

// CORRECT: miss does not increment
// WRONG: increment then discover null — over-count miss as hit
```

---


## 6. Algorithms & Pseudocode

### 6.1 BUGGY get (do not ship)

```text
function get(key):
  if key == null: throw InvalidArgument
  v = map.get(key)              // HashMap — unsafe concurrent
  if v != null:
    hits = hits + 1             // LOST UPDATES — three-step RMW
  return v

function getHitCount():
  return hits                   // racy read — may see torn 64-bit on 32-bit JVM
```

### 6.2 FIXED get (AtomicLong)

```text
function get(key):
  if key == null: throw InvalidArgument
  v = map.get(key)              // ConcurrentHashMap
  if v != null:
    globalHits.incrementAndGet()
  return v

function getHitCount():
  return globalHits.get()
```

### 6.3 FIXED synchronized alternative

```text
function get(key):
  v = map.get(key)
  if v != null:
    synchronized(hitLock):
      hits++
  return v
// Correct but serializes all hit increments — OK interview mention
```

### 6.4 Per-key hits (extension)

```text
function get(key):
  v = map.get(key)
  if v != null:
    globalHits.incrementAndGet()
    keyHits.computeIfAbsent(key, k -> new AtomicLong()).incrementAndGet()
  return v
```

### 6.5 N×M stress test

```text
function stress_test_fixed():
  N = 32
  M = 10_000
  key = "hot"
  store.put(key, bytes("x"))

  latch = CountDownLatch(N)
  start = CountDownLatch(1)
  for t in 1..N:
    spawn thread:
      start.await()
      repeat M times: store.get(key)
      latch.countDown()
  start.countDown()
  latch.await(timeout=60s)

  expected = N * M
  actual = store.getHitCount()
  assert actual == expected : "got " + actual

function stress_test_buggy():
  same setup
  actual = buggy.getHitCount()
  // assert actual < expected * 0.9 typically — demonstrates bug
  log("buggy: expected=%d actual=%d lost=%d", expected, actual, expected-actual)
```

### 6.6 LongAdder variant (high contention)

```text
LongAdder hits = new LongAdder();
on hit: hits.increment()
read: hits.sum()
// sum may lag slightly during concurrent add — OK for metrics dashboard
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

| Scenario | Buggy behavior | Fixed behavior |
|----------|------------------|----------------|
| Lost updates | Under-count | Exact count |
| Double increment paths | Over-count | Prevented by design |
| HashMap corruption | Rare crash/hang | CHM avoids |
| Hot key counter CAS spin | N/A | Accept or use LongAdder |
| 64-bit counter overflow | Theoretical | Document long range |
| Reading hits during writes | Torn read possible | AtomicLong.get safe |



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

1. Single-thread: put + get → hit count 1
2. get miss → hit count 0
3. Multiple gets → count equals get count
4. delete + get miss → no increment

### 8.2 N×M concurrency test (fixed)

```text
@Test
void fixed_kv_hit_count_exact_under_contention() throws Exception {
  FixedKV kv = new FixedKV();
  kv.put("k", new byte[]{1});
  int N = 64, M = 5000;
  ExecutorService ex = Executors.newFixedThreadPool(N);
  CountDownLatch go = new CountDownLatch(1);
  CountDownLatch done = new CountDownLatch(N);
  for (int i = 0; i < N; i++) {
    ex.submit(() -> {
      go.await();
      for (int j = 0; j < M; j++) kv.get("k");
      done.countDown();
    });
  }
  go.countDown();
  assertTrue(done.await(30, TimeUnit.SECONDS));
  assertEquals((long) N * M, kv.getHitCount());
}
```

### 8.3 Buggy demonstration test

```text
@Test
void buggy_kv_under_counts() throws Exception {
  BuggyKV kv = new BuggyKV();
  kv.put("k", new byte[]{1});
  // same N×M stress
  long actual = kv.getHitCount();
  assertTrue(actual < N * M * 0.95, "buggy should under-count; got " + actual);
}
```

### 8.4 TSan / JCStress

Run buggy under ThreadSanitizer — expect data race reports on `hits` and possibly HashMap internals.

### 8.5 Regression guard

CI runs fixed N×M test; fails if someone reintroduces plain `hits++`.



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

| Op | Buggy | Fixed |
|----|-------|-------|
| get | O(1) | O(1) map + O(1) atomic inc |
| put | O(1) unsafe | O(1) CHM |
| getHitCount | O(1) racy | O(1) atomic read |

At extreme QPS on one key, `AtomicLong` CAS retries → consider `LongAdder` or sharded counters.

Combine with kv-sliding-window-qps doc: hits are lifetime total; QPS is 60s window — orthogonal metrics.



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

**Interview arc**

1. Write **BuggyKV** with HashMap + `hits++`
2. Draw **lost update timeline** — two LOADs same value
3. Run **N×M stress** — count ≪ expected
4. Fix map → **ConcurrentHashMap**; fix counter → **AtomicLong**
5. Re-run stress — **exact N×M**
6. Mention **LongAdder** if interviewer asks scale

**Top traps**

1. Fixing only map but leaving `hits++`
2. Using `volatile` and claiming it fixes RMW
3. Incrementing on miss
4. Two increment sites (metrics + global)

---

## 11. Interviewer Q&A (with Answers)

### Q1. Why doesn't volatile fix hits++?

volatile ensures visibility of writes, not atomicity of read-modify-write. Two threads can still read same value, increment, and write back same result — lost update remains.

### Q2. AtomicLong vs synchronized?

Both correct for global counter. synchronized serializes increments; AtomicLong uses CAS — better under moderate contention. Interview: start AtomicLong; mention synchronized as simpler alternative.

### Q3. LongAdder vs AtomicLong?

LongAdder stripes increments across cells — lower contention at very high rates; sum() on read is slightly more expensive. Use for metrics where exact momentary value less critical.

### Q4. Must we fix HashMap too?

Yes. Even correct counter with racy map → lost entries, crashes. ConcurrentHashMap is parallel fix.

### Q5. Increment before or after null check?

After — only count hits. Increment before wastes count on miss if logic wrong.

### Q6. Per-key vs global hits?

Global: one AtomicLong. Per-key: CHM of AtomicLong with computeIfAbsent — watch memory for high cardinality keys.

### Q7. Can we lock per key only?

Yes: `synchronized(key.intern())` dangerous; use striped locks or concurrent map of counters.

### Q8. Happens-before story?

CHM put happens-before CHM get seeing entry. AtomicLong increment happens-before getHitCount reading value.

### Q9. C++ interview?

atomic<int64_t> + concurrent_hash_map; same lost-update diagram.

### Q10. Double counting example?

metrics.inc() + hits++ in two helpers called from get — fix: one line incrementAndGet.

### Q11. 32-bit JVM torn reads?

Plain long read without volatile/atomic may read torn bits — another reason for AtomicLong.

### Q12. Test flake?

Buggy test may rarely pass — run multiple iterations or assert actual < expected * 0.99.

### Q13. JUnit latch pattern?

start gate ensures all threads race simultaneously — maximizes lost updates for demo.

### Q14. Production follow-up?

Expose hit ratio = hits / (hits+misses); combine with sliding-window QPS for hot keys.

### Q15. Interview close sentence?

We reproduced under-count with N×M stress, traced to non-atomic RMW on hits++, fixed with AtomicLong and CHM, verified exact count.

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

### G. Side-by-side diff

```diff
- Map<String, byte[]> map = new HashMap<>();
- long hits = 0;
+ ConcurrentHashMap<String, byte[]> map = new ConcurrentHashMap<>();
+ AtomicLong globalHits = new AtomicLong();

  byte[] get(String key) {
    byte[] v = map.get(key);
    if (v != null) {
-     hits++;
+     globalHits.incrementAndGet();
    }
    return v;
  }
```

### H. Lost update probability sketch

Under high contention, lost updates scale with overlapping RMW windows.
Empirically with N=32, M=10000, buggy often reports 150k–280k vs expected 320k.
Not a formal proof — sufficient for interview demonstration.
---

*End of LLD prep.*
