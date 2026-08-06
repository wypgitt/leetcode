"""KV sliding window QPS LLD topic."""

from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices

register("kv-sliding-window-qps-lld-system-design.md", lambda: build_doc([
    header(
        "In-Memory KV Store with Per-Key Sliding-Window QPS",
        "60s sliding window · Ring buffer timestamps · Bucketed counters · getQps hooks on get/put",
        "Accurate QPS per key without lost updates; O(window/bucket) memory per active key",
    ),
    section_1(
        goal="Design an **in-memory KV store** with a **per-key sliding-window QPS counter** (60s window), exposing `getQps(key)` and hooks on `get`/`put`.",
        what_is="""| Scope | Single-node KV + metrics | Distributed rate limiter |
| Window | 60s sliding | Fixed calendar minute only |
| Structure | Ring buffer of timestamps OR bucketed counts | Global single counter |
| Databricks lens | Hot-key detection / throttling hooks | Full billing pipeline |""",
        fr_rows=[
            ("KV ops?", "get, put, delete", "Standard map"),
            ("QPS window?", "60 seconds sliding", "Evict stale events"),
            ("Count what?", "get and put each increment", "Configurable ops mask"),
            ("getQps(key)?", "Returns ops in last 60s / 60", "Double or int QPS"),
            ("Per-key state?", "Lazy create on first op", "Cleanup idle keys"),
            ("Precision?", "Event timestamps ms OR 1s buckets", "Trade memory vs accuracy"),
            ("Thread safety?", "Required", "Per-key locks or stripes"),
            ("Clock?", "System nano/ms monotonic", "No NTP jump handling MVP"),
            ("Memory bound?", "Cap events per key or max keys", "Evict oldest"),
            ("delete key?", "Removes KV + QPS state", "Immediate"),
            ("Hot key?", "Millions ops/min on one key", "Ring size cap"),
            ("Global QPS?", "Optional aggregate", "Phase 2"),
        ],
        mvp=[
            "ConcurrentHashMap key → value.",
            "ConcurrentHashMap key → SlidingWindowCounter.",
            "On get/put: record timestamp in ring or increment bucket.",
            "getQps(key) prunes stale events and returns count/60.0.",
            "Lazy allocation of counter on first access.",
            "Thread-safe without lost updates (atomics or synchronized per key).",
        ],
        scope="In-memory KV with per-key 60s sliding-window QPS: ring buffer or bucketed counters, getQps API, hooks on get/put, thread-safe.",
        invariant="""getQps(k) returns (number of recorded get/put ops for k with timestamp in (now-60s, now]) / 60.
Counter updates are atomic with respect to op recording; no lost increments under concurrent ops on same key.
Pruning removes only events older than window.""",
    ),
    section_2(
        api="""class KVWithQps:
  Optional<byte[]> get(String key)
  void put(String key, byte[] value)
  void delete(String key)
  double getQps(String key)           // ops per second over 60s window
  long getOpCount(String key)          // raw count in window
  QpsStats stats()

class SlidingWindowCounter:
  void recordOp(long nowMs)
  double qps(long nowMs)
  long count(long nowMs)
  void prune(long nowMs)""",
        guarantees=[
            ("KV correctness", "Standard map semantics"),
            ("QPS accuracy", "Within bucket granularity; exact with timestamp ring"),
            ("Thread safety", "Concurrent get/put/getQps"),
            ("Monotonic count", "Ops never decrease before prune evicts stale"),
            ("Lazy init", "No counter until first op on key"),
            ("delete cleanup", "Removes counter state"),
        ],
        errors="""InvalidArgument — null key
KeyNotFound — optional for get
ClosedException — after shutdown""",
    ),
    section_3(
        classes=[
            ("KVWithQps", "Facade: KV + QPS hooks"),
            ("ValueStore", "Map key → value"),
            ("QpsTracker", "Map key → SlidingWindowCounter"),
            ("SlidingWindowCounter", "Ring or buckets for one key"),
            ("TimestampRing", "Fixed-capacity circular array of event times"),
            ("BucketCounter", "60 x 1s buckets rolling"),
            ("Metrics", "hot keys, prune time"),
        ],
        diagram="""get/put → ValueStore
         ↘ recordOp → SlidingWindowCounter (per key)
getQps → prune stale → count / 60""",
    ),
    section_4("""### 4.1 Timestamp ring (exact)

```text
ring[size=1024]  // cap events per key
head index, count valid entries
recordOp(t): ring[head++] = t; if full drop oldest or expand policy
prune(t): remove entries < t - 60000
qps = valid_count / 60.0
```

### 4.2 Bucketed (memory friendly)

```text
buckets[60]  // one per second
second = nowMs / 1000
recordOp: buckets[second % 60]++
prune: zero buckets older than window
count = sum(buckets)
```

| Approach | Space/key | Accuracy |
|----------|-----------|----------|
| Ring | O(events) capped | Exact within cap |
| Buckets | O(60) | ±1s granularity |

| Op | Time | Notes |
|----|------|-------|
| get/put | O(1) KV + O(1) record | |
| getQps | O(window) prune worst case | Amortized with lazy prune |"""),
    section_5(
        "| ValueStore | CHM |\n| QpsTracker | CHM key → counter |\n| Each SlidingWindowCounter | synchronized or lock striping |",
        ["recordOp called for every counted op.", "getQps prunes before count.", "No negative counts.", "delete removes both maps' entries.", "Ring indices consistent under lock.", "Lazy create counter once per key."],
        "lock(keyStripe): value op + recordOp together OR record after value with same stripe",
    ),
    section_6([
        ("put with hook", """lock stripe(key):
  store.put(key, value)
  counter = qpsTracker.computeIfAbsent(key, SlidingWindowCounter::new)
  counter.recordOp(nowMs())
unlock"""),
        ("getQps", """c = qpsTracker.get(key)
if c == null: return 0
lock(c):
  c.prune(nowMs())
  return c.count() / 60.0"""),
        ("bucket recordOp", """s = nowMs / 1000
buckets[s % 60].incrementAndGet()
lastSecond = s"""),
        ("ring prune", """cutoff = nowMs - 60000
while tail valid and ring[tail] < cutoff: tail++; count--"""),
        ("delete", """store.remove(key)
qpsTracker.remove(key)"""),
    ]),
    section_7([
        ("Ring overflow hot key", "Drop oldest or cap QPS estimate", "Document bias"),
        ("Clock jump forward", "Prune all", "Temporary QPS dip"),
        ("Clock jump backward", "Reject old timestamps or clamp", "Define policy"),
        ("Lazy counter leak", "Idle keys retain memory", "TTL eviction Phase 2"),
        ("Race getQps during put", "Count includes op if linearized after record", "Per-key lock"),
    ]),
    section_8(
        ["put/get round trip", "getQps zero on new key", "60 ops in 60s → ~1 QPS", "delete clears QPS", "key not found getQps=0"],
        ["concurrent puts same key counter exact", "concurrent getQps during puts", "many keys parallel"],
        None,
    ),
    section_9("Bucketed counters at high key cardinality; approximate HLL for global; shard store by key at 100×."),
    section_10(
        ["KV + per-key sliding window", "Ring or bucket tradeoff", "Hooks on get/put", "Thread-safe increments"],
        [("In-memory 60s", "Distributed rate limit"), ("Exact ring", "Count-min sketch approximate")],
        ["Lost updates on counter", "Global lock on all ops", "Forgot prune on getQps"],
    ),
    section_11(
        ["Ring vs buckets?", "How handle 100k QPS on one key?", "Integrate with rate limiting?", "Monotonic clock?", "Compare to leaky bucket?"],
        [("Global counter only", "Per-key required"), ("Integer division QPS", "Use double or specify rounding")],
    ),
    section_12(common_appendices("kv-sliding-window-qps")),
]))
