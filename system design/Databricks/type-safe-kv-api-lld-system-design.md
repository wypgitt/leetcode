# LLD: Generic Type-Safe Key-Value Store API

> **Focus areas:** TypeRegistry · TypeTag · Serializer · TypedBlob · Runtime type safety · Schema evolution
> **Style:** LLD interview (clarify → API → classes → concurrency invariants → pseudocode → failure/recovery → tests → Q&A)
> **Quality bar:** Compile-time types where possible; explicit TypeMismatch at runtime; no silent casts
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

Goal: Design a **generic KV store** where keys and values are typed (Java generics / C++ templates style), with **runtime schema checks** when types are erased at the storage boundary.

### 1.0 What this is / is not

| Dimension | This design | Not this |
|-----------|-------------|----------|
| Scope | Single-process typed KV facade | Full SQL catalog |
| Storage | `Map<K, TypedBlob>` with tag + bytes | Raw `Map<String, Object>` |
| Safety | `get(k, Class<V>)` throws `TypeMismatchException` | Silent `(V) object` cast |
| Threading | Concurrent put/get/remove | Single-threaded only |
| Persistence | Phase 2 (length-prefixed bytes) | Required for MVP |
| Databricks lens | Metadata / config store with mixed types | Delta table engine |

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Key/value types? | String keys; int, long, double, String, POJO | TypeRegistry + Serializer per type |
| F2 | Compile-time safety? | Yes for generic API; runtime for dynamic `Class<V>` | Two API surfaces |
| F3 | Wrong type on get? | Throw `TypeMismatchException` | Never deserialize wrong type |
| F4 | Thread safety? | Required | Striped locks or CHM + per-key lock |
| F5 | Null values? | Disallowed (use Optional empty) | Distinguish absent vs null |
| F6 | Max value size? | 1 MB serialized | Reject at put with InvalidArgument |
| F7 | Overwrite semantics? | put replaces entire entry atomically | New tag may differ from old |
| F8 | Type registration? | All types registered before serve | `registry.freeze()` |
| F9 | Schema evolution? | New TypeTag ids; old readers skip unknown | Version in tag optional |
| F10 | Iteration? | keys() / scan by prefix optional | Not MVP hot path |
| F11 | Polymorphic values? | One key one concrete type at a time | No silent upcast |
| F12 | Performance? | Millions ops/s in-memory | Serialize outside lock |

**MVP scope:**

1. Generic `TypedKVStore<K,V>` with compile-time `K,V` on put/get where possible.
2. `TypeRegistry` maps `TypeTag` ↔ `Serializer`.
3. Runtime storage: `ConcurrentHashMap<K, TypedBlob>`.
4. `Optional<V> get(K key, Class<V> type)` validates tag **before** deserialize.
5. Thread-safe put/get/remove with per-key linearization.
6. Explicit `TypeMismatchException` when stored tag ≠ requested type.

**Out of MVP:** Disk persistence, cross-process registry sync, distributed sharding.

### 1.2 Scope repeat-back

> Single-node typed KV: generic API surface, TypeRegistry, serializers, TypedBlob storage, runtime tag checks on dynamic get, thread-safe in-memory map, no silent type coercion.

### 1.3 Core invariant (lock early)

```text
For every successful get<K,V>(k, typeClass):
  stored.tag == registry.tagOf(typeClass)
  AND deserialize(stored.payload) yields value assignable to V

put<K,V>(k, v) atomically replaces prior value; blob.tag always matches serializer(V).
No get returns bytes deserialized into wrong type — tag check is mandatory gate.
```

---


## 2. APIs & Guarantees

### 2.1 Public API

```text
class TypedKVStore<K> implements Closeable:
  TypedKVStore(TypeRegistry registry, StoreOptions opts)

  <V> void put(K key, V value) throws SerializationException, ClosedException
  <V> Optional<V> get(K key, Class<V> type) throws TypeMismatchException, SerializationException
  boolean remove(K key)
  boolean contains(K key)
  Set<K> keys()                    // snapshot; weak consistency OK
  void close()

class TypeRegistry:
  <T> void register(Class<T> type, Serializer<T> serializer)
  void register(TypeTag tag, Serializer<?> serializer)
  TypeTag tagOf(Class<?> type)
  Serializer<?> serializerFor(TypeTag tag)
  void freeze()                    // after this, no new registrations
  boolean isFrozen()

interface Serializer<T>:
  byte[] serialize(T value) throws SerializationException
  T deserialize(byte[] bytes) throws SerializationException

class TypedBlob:
  final TypeTag tag
  final byte[] payload            // treat as immutable after construction
  final long version              // optional; default 1

class TypeTag:
  final int id
  final String name               // e.g. "int", "com.app.UserProfile"
  final int schemaVersion

class StoreOptions:
  int maxEntryBytes = 1_048_576
  int lockStripes = 256
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
| Static type safety | `put(k, v)` + `get(k, same V.class)` cannot silently mismatch |
| Dynamic type safety | `get(k, Wrong.class)` throws TypeMismatch before deserialize |
| Single-key atomicity | put/remove replace entire blob atomically |
| Per-key linearizability | Ops on same key appear in some serial order |
| No silent coercion | Never auto-convert int→String or similar |
| Round-trip | After put, get with correct type returns equal value (`equals`) |
| Registry immutability | After freeze(), tag lookup is read-only |

### 2.3 Error model

```text
TypeMismatchException     — stored TypeTag ≠ requested Class<V>
SerializationException    — serialize/deserialize failure (corrupt bytes)
InvalidArgumentException  — null key, oversize payload, unregistered type
UnknownTypeTagException   — blob tag not in registry (migration needed)
ClosedException           — operation after close()
```

---


## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Responsibility |
|-------|----------------|
| `TypedKVStore<K>` | Public generic API; orchestrates serialize/lock/store |
| `TypeRegistry` | Class→TypeTag, TypeTag→Serializer; freeze gate |
| `TypeTag` | Stable runtime identity for a serialized type |
| `Serializer<T>` | Encode/decode value ↔ bytes |
| `TypedBlob` | Immutable stored record: tag + payload (+ version) |
| `StorageEngine<K>` | `ConcurrentHashMap<K, TypedBlob>` |
| `LockStripes` | `hash(key) % N` → stripe lock for per-key ops |
| `StoreMetrics` | puts/gets/mismatches/serialize latency |

### 3.2 ASCII architecture

```text
                    put(k, v)
Client ──────────────────────────────────────────────► TypedKVStore
                           │                              │
                           │                    tag = registry.tagOf(v.class)
                           │                    bytes = serializer.serialize(v)
                           │                              │
                           ▼                              ▼
                    TypeRegistry ◄─────────── StorageEngine
                    (tagOf, serializer)         K → TypedBlob(tag, bytes)

get(k, User.class):
  blob = map.get(k)
  if blob.tag != registry.tagOf(User.class): throw TypeMismatch
  return UserSerializer.deserialize(blob.payload)
```

### 3.3 Compile-time vs runtime safety

| Layer | Mechanism | What it prevents |
|-------|-----------|------------------|
| Compile-time (generics) | `<V> V get(K k, Class<V> c)` usage | Caller must supply type token |
| Runtime (TypeTag) | Compare `blob.tag` to `registry.tagOf(c)` | Wrong type after erasure |
| Storage boundary | Values always stored as bytes + tag | No raw Object in map |

**C++ template sketch:**

```text
template<typename V>
void put(K k, V v) {
  static_assert(Serializable<V>);
  map[k] = TypedBlob{ Tag<V>::id, serialize(v) };
}

template<typename V>
optional<V> get(K k) {
  auto& blob = map[k];
  if (blob.tag != Tag<V>::id) throw TypeMismatch;
  return deserialize<V>(blob.payload);
}
```

**Java erasure reality:** compile-time `V` is erased; `Class<V> type` parameter restores runtime check.

---


## 4. Core Data Structures & Algorithms

### 4.1 TypedBlob on-wire / in-memory layout

```text
On disk (Phase 2):
  [magic:2][tag_id:4][schema_ver:2][payload_len:4][payload:len][crc32:4]

In memory (MVP):
  TypedBlob { TypeTag tag; byte[] payload; long version; }
  payload is copied on put — callers cannot mutate stored bytes
```

| Field | Size | Purpose |
|-------|------|---------|
| tag_id | 4 bytes | Lookup serializer in registry |
| schema_ver | 2 bytes | POJO evolution |
| payload | variable | Serializer output |
| crc32 | 4 bytes | Detect corruption (Phase 2) |

### 4.2 TypeRegistry internals

```text
class TypeRegistry {
  Map<Class<?>, TypeTag> classToTag
  Map<TypeTag, Serializer<?>> tagToSerializer
  Map<Integer, TypeTag> idToTag
  boolean frozen

  register(Class<T> c, Serializer<T> ser):
    assert !frozen
    tag = new TypeTag(nextId++, c.getName(), 1)
    classToTag.put(c, tag)
    tagToSerializer.put(tag, ser)
}
```

**Freeze semantics:** after `freeze()`, any `register()` throws. Ensures stable tag ids for running process.

### 4.3 Serializer implementations

| Type | Encoding | serialize cost |
|------|----------|----------------|
| int | 4-byte big-endian | O(1) |
| long | 8-byte BE | O(1) |
| double | 8-byte IEEE754 BE | O(1) |
| String | `[utf8_len:4][utf8 bytes]` | O(n) |
| POJO | JSON or Protobuf | O(n); prefer protobuf in prod |

### 4.4 Complexity

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| put | O(1) avg + O(payload) serialize | O(payload) | Replace whole blob |
| get (hit) | O(1) avg + O(payload) deserialize | O(1) | Tag check O(1) |
| remove | O(1) avg | — | |
| keys() | O(n) | O(n) | Snapshot |
| register | O(1) | O(types) | Once at startup |

### 4.5 Type overwrite example

```text
put("config", 42)           → blob.tag = INT
put("config", "prod")       → blob.tag = STRING  // tag changes; legal
get("config", Integer.class) → TypeMismatchException  // correct failure
get("config", String.class)  → "prod"
```

---


## 5. Concurrency Invariants & Race Analysis

### 5.1 Shared state

| State | Structure | Protection |
|-------|-----------|------------|
| KV map | `ConcurrentHashMap<K, TypedBlob>` | CHM + stripe lock for put/get sequence |
| TypeRegistry | frozen immutable maps | safe publication after freeze |
| Metrics | `LongAdder` counters | atomics |
| closed flag | `volatile boolean` | checked at op entry |

### 5.2 Lock order (mandatory)

```text
1. Never hold stripe lock during deserialize of large POJO if avoidable:
     serialize OUTSIDE lock
     lock(stripe(key)): map.put(key, blob)
     deserialize OUTSIDE lock after get

2. Never acquire two key stripes in one op (no multi-key transactions MVP)

3. Registry never locked with stripe locks (registry is read-only post-freeze)
```

### 5.3 Invariants table

| # | Invariant |
|---|-----------|
| I1 | Stored tag always matches serializer used at put time |
| I2 | TypedBlob.payload treated immutable after publish to map |
| I3 | Tag comparison happens before any deserialize call |
| I4 | put/remove on same key are linearizable |
| I5 | close() happens-before rejected ops |
| I6 | No partial blob visible (build blob, then single map put) |

### 5.4 Race scenarios

**R1 — Concurrent put same key (last writer wins):**

```text
Thread A: put(k, int 1)   ─┐
Thread B: put(k, int 2)   ─┼─► map holds one blob; tag=int; value 1 OR 2
                           └─  Both legal; client sees last linearized put
```

**R2 — get during put (safe with stripe lock):**

```text
Without lock: get might read torn blob (tag from A, bytes from B) — BUG
Fix: lock(stripe(k)) covers read blob + put replace as atomic w.r.t. same key
Alternative: immutable TypedBlob swap — CHM put is atomic reference swap
  if blob is immutable and replaced wholesale, CHM alone suffices
```

**R3 — Type mismatch must not deserialize:**

```text
Thread: get(k, String.class) while stored tag is INT
  CORRECT: compare tags → throw TypeMismatch → never call StringSerializer
  WRONG: deserialize first → garbage / security gadget risk
```

**R4 — Registry drift (multi-process, Phase 2):**

Two processes with different tag id assignments → misinterpret bytes. Mitigation: stable string name in TypeTag + handshake at startup; not MVP.

---


## 6. Algorithms & Pseudocode

### 6.1 put

```text
function put(key, value):
  if closed: throw ClosedException
  if key == null: throw InvalidArgument
  tag = registry.tagOf(value.getClass())
  serializer = registry.serializerFor(tag)
  payload = serializer.serialize(value)        // outside lock
  if payload.length > maxEntryBytes: throw InvalidArgument
  blob = new TypedBlob(tag, copy(payload), version=1)
  lock(stripe(key)):
    map.put(key, blob)                         // linearization point
  metrics.putSuccess(tag)
```

### 6.2 get with Class<V> type check

```text
function get(key, typeClass):
  if closed: throw ClosedException
  if key == null or typeClass == null: throw InvalidArgument
  blob = map.get(key)
  if blob == null: return Optional.empty()
  expectedTag = registry.tagOf(typeClass)
  if blob.tag.id != expectedTag.id:           // or !blob.tag.equals(expectedTag)
    metrics.typeMismatch(blob.tag, typeClass)
    throw new TypeMismatchException(key, blob.tag, typeClass)
  serializer = registry.serializerFor(expectedTag)
  value = serializer.deserialize(blob.payload) // outside lock if copy bytes under lock
  return Optional.of(value)
```

### 6.3 remove / contains / keys

```text
function remove(key):
  lock(stripe(key)):
    prev = map.remove(key)
  return prev != null

function contains(key):
  return map.containsKey(key)

function keys():
  return Collections.unmodifiableSet(new HashSet<>(map.keySet()))
```

### 6.4 Bootstrap registry

```text
registry = new TypeRegistry()
registry.register(int.class, IntSerializer.INSTANCE)
registry.register(String.class, StringSerializer.INSTANCE)
registry.register(UserProfile.class, new ProtobufSerializer<>(UserProfile.parser()))
registry.freeze()
store = new TypedKVStore<>(registry, opts)
```

### 6.5 Generic helper (Java)

```text
class TypedKVStore<K> {
  <V> V getOrThrow(K key, Class<V> type) {
    return get(key, type).orElseThrow(() -> new KeyNotFoundException(key));
  }

  <V> void put(K key, V value) {
    put(key, value, (Class<V>) value.getClass());  // capture runtime class
  }
}
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

| Scenario | On failure | Mitigation |
|----------|------------|------------|
| Wrong type get | TypeMismatchException | Caller uses correct Class or handles |
| Corrupt payload bytes | SerializationException | Remove entry or quarantine key |
| Unknown tag in blob | UnknownTypeTagException | Migration tool rewrites tags |
| Oversize value at put | InvalidArgument | Client splits or compresses |
| Unregistered type at put | IllegalStateException | Register before freeze |
| Concurrent puts same key | LWW | Document; use versioning if needed |
| Deserialize before tag check | Security / logic bug | Code review + unit test |
| Mutable byte[] shared | Reader sees writer mutation | Always copy on put |



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

1. `put("a", 42)` then `get("a", Integer.class)` → `42`
2. `put("a", 42)` then `get("a", String.class)` → `TypeMismatchException`
3. Overwrite: `put("k", 1)` then `put("k", "x")` → int get fails, string get OK
4. Round-trip POJO: equals after serialize cycle
5. `remove("k")` then `get` → empty Optional
6. Null key → InvalidArgument
7. Payload > maxEntryBytes → InvalidArgument
8. get missing key → Optional.empty(), not exception
9. Register after freeze → throws
10. Unknown tag blob (injected) → UnknownTypeTagException

### 8.2 Concurrency tests

- N threads put distinct keys → all retrievable
- N threads put same key → no torn blobs; each get returns valid int or string
- N threads get with wrong type → all throw TypeMismatch, no deserialize side effects
- TSan / Helgrind clean on 32-thread mixed workload

### 8.3 Type safety tests

```text
@Test void mismatch_throws_before_deserialize() {
  store.put("k", 100);
  Serializer<?> spy = spy(StringSerializer.INSTANCE);
  registry.replaceForTest(String.class, spy);  // test hook
  assertThrows(TypeMismatchException.class, () -> store.get("k", String.class));
  verify(spy, never()).deserialize(any());
}
```

### 8.4 Property / invariant checks

```text
@RepeatedTest(100)
void random_ops_match_serial_model() {
  SerialTypedKVModel model = new SerialTypedKVModel();
  runParallelRandomOps(store, model, threads=8, ops=5000);
  assertEquals(model.snapshot(), store.debugSnapshot());
}
```



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

| Knob | Effect |
|------|--------|
| lockStripes 256→4096 | ↓ contention, ↑ memory |
| Primitive-only fast path | Separate `IntObjectHashMap` for int values |
| Protobuf vs JSON | ↓ CPU and bytes on wire |
| Copy payload on get | Safety vs zero-copy mmap Phase 2 |

Specialized maps at 10×: if 80% values are int, shard `Map<K,Integer>` alongside generic blob map.



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

- Every value stored as **TypedBlob** with **TypeTag** + bytes
- **TypeRegistry** resolves Class ↔ tag ↔ Serializer; frozen at startup
- **get(k, Class<V>)** compares tags then deserializes — never silent cast
- Compile-time generics help API ergonomics; runtime tag is source of truth

**MVP vs later**

| MVP | Later |
|-----|-------|
| In-memory CHM | Append-only log + mmap |
| Runtime Class get | C++ concepts-only static API |
| Copy bytes on write | Zero-copy ByteBuffer with refcount |

**Top risks**

1. Deserializing before tag check (security + correctness)
2. Mutable shared byte[] visible to callers
3. Registry tag id drift across processes

---

## 11. Interviewer Q&A (with Answers)

### Q1. Why not `Map<String, Object>`?

Object erases type at storage boundary. A caller doing `(User) map.get(k)` can fail with `ClassCastException` far from the bug, or worse succeed with wrong shape. TypedBlob + TypeTag fails fast at the store boundary with a structured TypeMismatch carrying expected vs actual tag.

### Q2. Where does compile-time safety end?

Java/C# generics erase at runtime. `TypedKVStore<String, User>` prevents mixing call sites at compile time, but the map still stores bytes. Without TypeTag, two call sites could disagree. Runtime check on `get(k, User.class)` closes the erasure gap.

### Q3. Protobuf vs custom Serializer?

Protobuf gives schema evolution, compact encoding, and cross-language tags. Custom serializers suit primitives (fixed-width int). Interview answer: primitives hand-rolled; POJOs Protobuf; register both in TypeRegistry.

### Q4. How handle schema evolution?

Bump `schemaVersion` in TypeTag. Serializer reads version byte prefix: v1 fields optional in v2. Unknown fields skipped. Never reuse tag id for different type.

### Q5. Avoid reflection on hot path?

Register explicit Serializer instances at startup. For POJO, generated protobuf code — no Class.forName per op. Reflection only in test fixtures.

### Q6. Polymorphic types (Shape → Circle)?

Store concrete tag only (Circle). If polymorphism needed, wrap union enum + blob or store canonical JSON with `$type` field — explicit, not implicit Object cast.

### Q7. Thread-safe registry?

Register on main thread before freeze; after freeze immutable — no locks on read path. Dynamic plugin load requires classloader-aware registry (Phase 2).

### Q8. Security concerns?

Never deserialize untrusted bytes without tag whitelist and size cap. TypeMismatch gate prevents invoking wrong deserializer. Consider disabling Java serialization entirely.

### Q9. put then get different type — expected?

Yes — throw TypeMismatch. Client must know current type via schema registry or convention.

### Q10. Compare to JDBC ResultSet getInt/getString?

Same pattern: column has type; getter must match or error. TypedKV generalizes to any registered Serializer.

### Q11. C++ vs Java interview delivery?

C++: templates give static tag via `Tag<V>::id`. Java: pair generic API with `Class<V>`. Both store tagged bytes underneath.

### Q12. How test TypeMismatch?

Spy serializer; verify deserialize never called when tags differ.

### Q13. Performance of tag check?

Single int compare — negligible vs deserialize. Primitive serializers avoid allocation.

### Q14. Optional empty vs null value?

MVP: no null values; absent key = Optional.empty(). Avoids null/type confusion.

### Q15. Linearization point for put?

CHM put of immutable TypedBlob reference (or stripe lock release after put). State aloud in interview.

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

### G. Example TypeTag table

| id | name | schemaVersion |
|----|------|---------------|
| 1 | int | 1 |
| 2 | long | 1 |
| 3 | String | 1 |
| 4 | com.app.UserProfile | 2 |

### H. TypeMismatchException fields

```text
class TypeMismatchException {
  K key;
  TypeTag storedTag;
  Class<?> requestedClass;
  // message: "key foo: stored INT, requested String"
}
```
---

*End of LLD prep.*
