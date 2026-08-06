"""KV race repair LLD topic."""

from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices

register("kv-race-repair-lld-system-design.md", lambda: build_doc([
    header(
        "KV Store with Hit Counter — Race Bug Analysis & Fix",
        "Lost updates · Double counting · Read-modify-write races · AtomicLong · synchronized · compare-and-swap",
        "Document buggy implementation first, then fixed version with proof sketches",
    ),
    section_1(
        goal="Present a **buggy KV + hit counter** with documented races (lost updates, double counting), then a **fixed design** using atomics / synchronized blocks.",
        what_is="""| Scope | In-memory KV + global/per-key hits | Distributed cache |
| Bug story | Intentional data races for teaching | Production-ready from day one |
| Fix | atomics or synchronized | Hope compiler fixes it |
| Databricks lens | Metrics on cache paths | Full observability stack |""",
        fr_rows=[
            ("KV ops?", "get (increments hits), put, delete", "Hit on get only MVP"),
            ("Counter scope?", "Global hit count + optional per-key", "Document which is buggy"),
            ("Buggy version?", "Plain int++ without sync", "Show lost updates"),
            ("Concurrency?", "Many threads get same hot key", "Demonstrate under-count"),
            ("Fixed version?", "AtomicLong or synchronized increment", "Exact count"),
            ("KV map?", "HashMap unsafe → ConcurrentHashMap", "Separate issues"),
            ("get miss?", "No hit increment", "Define clearly"),
            ("put?", "No hit increment", "Only get counts"),
            ("Testing?", "Deterministic stress + expected count", "Latch barrier test"),
            ("Performance?", "Atomics vs lock", "Measure hot key"),
            ("Double counting bug?", "Separate bug: increment twice paths", "Show duplicate"),
            ("Interview flow?", "Buggy → symptoms → fix → tests", "Timeboxed"),
        ],
        mvp=[
            "Buggy: `hits++` on get without synchronization; HashMap for KV.",
            "Demonstrate lost updates with N threads × M gets.",
            "Fixed: `AtomicLong hits` or `synchronized(incLock){hits++}`.",
            "KV: ConcurrentHashMap; per-key hits optional AtomicLong map.",
            "Explain read-modify-write non-atomicity.",
            "Tests prove fixed version reaches N×M hits.",
        ],
        scope="Buggy then fixed KV with hit counter: document races (lost updates, double count), fix with atomics/synchronized, prove with concurrency tests.",
        invariant="""After N threads each call get on same existing key M times (no failures):
  hit counter == N * M (fixed implementation).
get miss does not increment hits.
KV returns latest put value without lost puts on distinct keys (ConcurrentHashMap).""",
    ),
    section_2(
        api="""class BuggyKV:
  byte[] get(String key)      // hits++ UNSAFE
  void put(String key, byte[] v)
  long getHitCount()

class FixedKV:
  byte[] get(String key)      // hits.incrementAndGet()
  void put(String key, byte[] v)
  long getHitCount()
  long getKeyHits(String key) // optional per-key""",
        guarantees=[
            ("Fixed: hit count exact", "Under concurrent gets, no lost updates"),
            ("Fixed: KV thread-safe", "ConcurrentHashMap linearizable per key"),
            ("Buggy: best effort", "Under-count or corrupt (demo only)"),
            ("get miss", "No hit increment both versions"),
            ("put visibility", "Fixed: happens-before via CHM"),
        ],
        errors="""Null key → InvalidArgument
Buggy: potential infinite loops none; silent wrong counts""",
    ),
    section_3(
        classes=[
            ("BuggyKV", "Demonstrates races"),
            ("FixedKV", "Correct atomics/sync"),
            ("AtomicLong globalHits", "Lock-free counter"),
            ("ConcurrentHashMap", "Thread-safe KV"),
            ("HitCounterStriped", "Optional per-key atomics"),
        ],
        diagram="""BUGGY:
  get → map.get → hits++ (RMW race: read old, add 1, write — lost updates)

FIXED:
  get → map.get → globalHits.incrementAndGet()  // single atomic op""",
    ),
    section_4("""### 4.1 Lost update pattern

```text
Thread A: read hits=5
Thread B: read hits=5
Thread A: write hits=6
Thread B: write hits=6   // expected 7 — LOST UPDATE
```

### 4.2 Double counting pattern (separate bug)

```text
get() calls recordHit() twice (e.g. metrics + global) without dedup → 2x count
Fix: single increment site or idempotent token
```

### 4.3 Fixes compared

| Fix | Pros | Cons |
|-----|------|------|
| synchronized(lock){hits++} | Simple | Contention on hot counter |
| AtomicLong | Scalable increment | Still one hot key bottleneck |
| LongAdder | High contention aggregate | Eventually consistent sum |
| Per-shard counters | Reduce contention | Sum on read |

| Op | Buggy | Fixed |
|----|-------|-------|
| get hit inc | RMW race | O(1) atomic |"""),
    section_5(
        "| Buggy HashMap | unsafe |\n| Fixed CHM | safe |\n| AtomicLong hits | CAS loop internal |",
        ["Exactly one increment per successful get hit.", "No increment on miss.", "Atomic increment is total ordering for counter.", "CHM get/put per-key atomic.", "No duplicate increment paths in fixed code."],
        "Buggy: no order. Fixed: CHM op then atomic inc (inc even if value null? only if hit — define miss)",
    ),
    section_6([
        ("BUGGY get", """v = map.get(key)   // unsafe HashMap
if v != null:
  hits = hits + 1    // LOST UPDATES
return v"""),
        ("FIXED get", """v = map.get(key)
if v != null:
  globalHits.incrementAndGet()
return v"""),
        ("FIXED synchronized alt", """synchronized(hitLock):
  hits++
// works but serializes all hits"""),
        ("stress test", """put key
barrier.start(N threads)
each: for i in 0..M-1: get(key)
barrier.await()
assert fixed.getHitCount() == N*M
// buggy often << N*M"""),
        ("double count bug demo", """get(key):
  metrics.inc()   // path 1
  hits++          // path 2  — double count if both fire
// fix: single increment"""),
    ]),
    section_7([
        ("Lost updates", "Under-count", "Atomics"),
        ("Double increment paths", "Over-count", "Single increment site"),
        ("HashMap infinite loop JDK8", "Rare resize bug", "CHM"),
        ("Hot key counter", "Contention", "LongAdder"),
        ("64-bit counter overflow", "Theoretical", "Document long"),
    ]),
    section_8(
        ["single thread exact count", "miss no increment", "put then get increments once"],
        ["N threads M gets fixed == N*M", "buggy << expected", "TSan on buggy shows races"],
        None,
    ),
    section_9("LongAdder for global hits; sharded counters; combine with sliding-window QPS doc."),
    section_10(
        ["Show buggy RMW first", "Fix with AtomicLong or sync", "CHM for KV", "Stress test proves fix"],
        [("AtomicLong global", "LongAdder / sharded"), ("Hit on get only", "Weighted hits")],
        ["Fixing only map not counter", "incrementAndGet after null check wrong place", "Double increment in two helpers"],
    ),
    section_11(
        ["Why not volatile?", "LongAdder vs AtomicLong?", "Can we lock per key only?", "Happens-before story?", "JUnit latch test?"],
        [("volatile fixes it", "RMW still racy"), ("synchronized on whole get", "Too coarse but correct")],
    ),
    section_12(common_appendices("kv-race-repair", extra=[
        ("F. Side-by-side diff", """| Buggy | Fixed |
| HashMap | ConcurrentHashMap |
| hits++ | hits.incrementAndGet() |"""),
    ])),
]))
