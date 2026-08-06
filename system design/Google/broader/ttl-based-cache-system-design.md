# System Design: TTL-Based Cache

> **Focus areas:** Expiration strategies · Lazy vs active expiry · Memory management · Distributed TTL · Stampede · Clock skew  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct expiry semantics, split memory vs correctness, explicit stampede controls, deal-breakers for “perfect TTL with unsynced clocks + thundering herd ignored”  
> **Interview theme:** Google L5+ caching — TTL wheels, distributed coherence, progressive QPS/memory scale (complements broader distributed-cache doc; **deep on TTL**)

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the system**—a **TTL-centric cache** (single-node → distributed) where **time-to-live** is a first-class correctness and memory mechanism: **lazy vs active expiration**, **memory pressure interaction with TTL**, **distributed TTL semantics**, **stampede prevention**, and **clock skew**. Not a full DB; not only LRU without time.

### 1.0 What this is / is not

| Dimension | **TTL-based cache (this doc)** | Not this |
|-----------|--------------------------------|----------|
| Primary job | Serve Get/Set with expiry | Durable SoT |
| Success | Honor TTL (±skew tolerance); stable under expiry storms | Eternal perfect sync of all replicas’ wall clocks |
| Data | Opaque KV + deadline | Rich query engine |
| Expiry | Lazy + active hybrid | “Delete instantly worldwide” fantasy |
| Correctness | After TTL, Get miss (eventual across replicas) | Strict real-time global delete |

**Scope statement:** Design a TTL-based cache covering expiry algorithms, memory, distribution, stampede, and clock skew—scaling through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | `GET/SET/DEL` + `EXPIRE/TTL/PERSIST` | Redis-like |
| F2 | TTL units? | Seconds MVP; ms optional | Store deadline abs time |
| F3 | Lazy expire? | Yes on access | Check deadline on Get |
| F4 | Active expire? | Yes — reclaim memory | Sampling / timing wheel |
| F5 | Maxmemory? | Evict even before TTL | Policy interaction |
| F6 | Distributed? | Cluster with replicas | TTL replication semantics |
| F7 | Stampede? | Must address | Soft TTL / singleflight / jitter |
| F8 | Negative caching? | Yes for misses | Short TTL on empty |
| F9 | Sliding TTL? | Optional `TOUCH` / refresh on read | Product flag |
| F10 | Persistence? | Optional AOF/RDB Phase 2 | TTL restore rules |
| F11 | Multi-key expire? | `EXPIRE` per key MVP | No TX needed |
| F12 | Notify on expire? | Keyspace events Phase 1.5 | Pub/sub hook |

**MVP functional scope:**

1. Per-key absolute **deadline** (`expire_at`) or relative SET EX.  
2. **Lazy expiration** on read/write paths.  
3. **Active expiration** sweeper (sampling or timing wheel).  
4. Memory limit + eviction policy that **cooperates with TTL** (prefer expire-soon).  
5. Cluster: replicate SET+TTL; define skew tolerance.  
6. **Stampede controls**: probabilistic early expire / singleflight / jittered TTL.  
7. Metrics: expired/s, stale serves (if soft), heap, hit rate.

**Out of MVP:**

- Exactly synchronized global expiry to the millisecond  
- SQL-style TTL on secondary indexes  
- Guaranteed expire notifications without loss  
- Infinite keys with zero active expiry (leak)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Get latency | Memory path | p99 < 1–5ms in-AZ |
| N2 | Expiry accuracy | Best-effort | Lazy exact; active within seconds typical |
| N3 | Memory | Hard cap | Never OOM kill preferred — eviction |
| N4 | Stampede | Controlled | Origin QPS bounded on hot key expiry |
| N5 | Availability | High | Replica failover |
| N6 | Clock | Tolerant | Monotonic + skew bounds documented |
| N7 | Throughput | High SET/GET | Millions ops/s cluster |
| N8 | Operability | Tunables | Expire cycle CPU budget |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `SET k v EX 60` → Get hits → after 60s Get miss.  
2. Idle expired keys reclaimed by active sweeper.  
3. Hot key near expiry → soft TTL revalidate singleflight.  
4. Replica receives SET+PXAT → expires consistently enough.  
5. Memory full → evict volatile-TTL keys first.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Clock jump forward | Keys appear expired early — use monotonic where possible |
| Clock jump backward | Keys live longer — cap max TTL; detect jumps |
| Expire stampede same second | Jitter TTLs; staggered active expire |
| Lazy-only never accessed | Memory leak without active expire |
| Active expire CPU pegged | Budget ms/cycle; adaptive |
| Replica skew | Document window; optional `PXAT` absolute |
| Negative cache too long | Wrong; keep short + purge on write |
| Sliding TTL thundering | Refresh coalescing |
| Persist restart | Rebuild deadlines from RDB/AOF |
| TTL=0 / negative | Reject or immediate del |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ops/s cluster | 100K | 1M | 10M | 100M |
| Keys | 50M | 500M | 5B | 50B |
| Expiring keys % | 40% | 40–60% | 60% | 70% |
| Expire events/s | 20K | 200K | 2M | 20M |
| Hot keys | 100 | 1K | 10K | 100K |
| Nodes | 6 | 30 | 200 | 2K |
| Avg TTL | 5 min | mix | mix | multi-tier |
| Value size avg | 1 KB | 1 KB | 1–2 KB | tiered |
| Soft-TTL revalidations/s | 1K | 10K | 100K | 1M |

**What each jump forces:**

- **10×:** Timing wheel or efficient active expire; jitter; singleflight library.  
- **100×:** Sharded expire workers; hierarchical wheels; replica PXAT; memory policies.  
- **1,000×:** Tiered TTL (L1 local / L2 cluster), approximate expiry structures, origin shields.

### 1.5 Etc. (Constraints & Assumptions)

- DB/origin is SoT; cache TTL is **freshness bound**, not durability.  
- Clients may be many languages — server enforces TTL.  
- Absolute expiry (`expire_at`) preferred on the wire for replicas.

**Scope statement to repeat back:**

> Design a TTL-based cache with lazy+active expiry, memory-aware reclamation, distributed TTL semantics under clock skew, and stampede-resistant refresh—scaling keys and expire rates through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **GET** | Reads | 80K/s | 800K/s | Data |
| **SET** | Writes + TTL | 20K/s | 200K/s | Data |
| **Active expire** | Deletes | 20K/s | 200K/s | Background |
| **Revalidation** | Origin fetches | 1K/s | 10K/s | Origin shield |
| **Replication** | Binlog/ops | ~writes | × | Intra-cluster |

### 2.2 Memory metadata

```text
Per key overhead beyond value:
  key str + hash entry + expire_at (8B) + LRU bits ≈ 50–100B+
50M keys × 80B = 4 GB metadata alone
Expiring subset needs wheel/heap slots — budget explicitly
```

### 2.3 Active expire cost

```text
Naive: min-heap of all TTLs → O(log N) set, good pop, memory heavy
Sampling (Redis-style): each cycle random sample expired-prone keys
Timing wheel: O(1) insert/delete buckets by tick — strong at high expire rates

At 2M expires/s: heap churn painful → wheels or approximate buckets
```

### 2.4 Stampede amplification

```text
Hot key TTL 60s, 50K QPS on key
Without protection: at expiry, 50K origin hits in one RTT window
With singleflight: 1 origin hit
With jitter ±10%: expiry spread over 6s → ~8K/s peak theoretical if naïve; still need singleflight
```

### 2.5 Clock skew

```text
Replica A clock +200ms vs B
PX relative SET replicated as remaining TTL → drift compounds
Better: replicate absolute unix_ms expire_at; each node compares local clock
Still: skew ⇒ early/late expiry window — document ±skew SLO
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `SET key val [EX sec\|PX ms\|EXAT\|PXAT]` | Store with deadline |
| `GET key` | Lazy expire check |
| `TTL/PTTL key` | Remaining; −1 no TTL; −2 missing |
| `EXPIRE/PEXPIRE/EXPIREAT` | Set deadline |
| `PERSIST key` | Remove TTL |
| `DEL key` | Explicit delete |
| `GET` soft-TTL variant (app) | May return stale + async refresh |

### 3.2 Data model

| Structure | Purpose |
|-----------|---------|
| Hash table `key → {val, expire_at, flags}` | Primary |
| Timing wheel / sparsetable | Active expire |
| Optional min-heap | Exact next-expire (small sets) |
| Replica backlog | Propagate SET/DEL/EXPIRE |
| Singleflight map | In-flight origin fills |
| Negative cache entries | Miss markers with short TTL |

```text
Entry {
  value,
  expire_at_ms,  // 0 = no TTL
  created_at,
  flags: SOFT | NEGATIVE | VOLATILE
}
```

### 3.3 Lazy vs active — Why X over Y

| Strategy | Pros | Cons | When |
|----------|------|------|------|
| **Lazy only** | Cheap | Idle keys leak memory | Tiny / all keys hot |
| **Active only** | Memory tight | CPU; may lag accuracy | Memory-critical |
| **Hybrid** | Best of both | Complexity | **MVP pick** |
| **TTL scan full DB** | Simple | O(N) disaster | Never at scale |

**Lazy:** on Get/Set/TTL, if `now >= expire_at` → delete → miss.  
**Active:** background job deletes expired; frees memory for cold keys.

### 3.4 Active expiry structures — Why X over Y

| Structure | Insert | Pop due | Memory | Scale |
|-----------|--------|---------|--------|-------|
| **Min-heap by deadline** | log N | log N | high | Medium |
| **Redis sampling** | O(1) | probabilistic | low | Good general |
| **Hierarchical timing wheel** | O(1) | O(1) amort | medium | **High expire rates** |
| **Sorted set (score=expire)** | log N | log N | high | Small/medium |

**Chosen MVP:** sampling + lazy; upgrade to **timing wheel** at 100× expire/s.

### 3.5 Stampede controls — Why X over Y

| Technique | Pros | Cons |
|-----------|------|------|
| **Singleflight / request coalescing** | Bound origin to 1 | Needs coordination per node |
| **TTL jitter** | Spread expiry | Alone insufficient for mega-hot keys |
| **Soft TTL (stale-while-revalidate)** | UX smooth | Serves stale |
| **Probabilistic early expiration** | XFetch algorithm | Tuning |
| **Locking in Redis** | Simple | Failure stuck locks |

**Chosen:** jitter at SET + singleflight on miss + optional soft TTL for hottest tier.

**XFetch probabilistic early expire (interview signal):**

```text
# On Get, if remaining TTL small, probabilistically treat as expired
# P = exp(-remaining / beta) style — one client rebuilds early
```

### 3.6 Distributed TTL semantics

| Approach | Behavior |
|----------|----------|
| Replicate relative TTL | Receiver applies `now+ttl` — skew/delay errors |
| Replicate absolute `expire_at` | **Preferred** |
| Logical expiry version | App-level |
| Central expire service | Anti-pattern hotspot |

**Replica read:** may return key another replica already expired within skew window — acceptable for cache.

### 3.7 Memory + TTL interaction

| Policy | Idea |
|--------|------|
| `volatile-ttl` | Evict keys with TTL, earliest deadline first |
| `volatile-lru` | Among TTL keys, LRU |
| `allkeys-lru` | Ignore TTL preference |
| `noeviction` | SET errors when full |

**Chosen default:** `volatile-ttl` or TinyLFU admission + TTL-aware victim.

**Deal-breaker:** no active expire + no eviction ⇒ OOM.

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Expiry | Hybrid lazy+active | Correct + memory | Lazy-only at large idle |
| Active DS | Sample → wheel | CPU/mem balance | Full table scan |
| Wire TTL | Absolute expire_at | Skew/delay | Relative only across replicas |
| Stampede | Jitter+singleflight(+soft) | Origin protect | Naïve synchronized TTL |
| Clocks | Monotonic + jump detect | Sanity | Trust wall only blindly |
| Eviction | TTL-aware | Free soon-dead first | Random among immortal keys only |

---

## 4. Architecture Diagram

```text
                         +----------------------+
   Clients ------------> |  Cache Proxy / Smart |
                         |  Client (optional)   |
                         +----------+-----------+
                                    |
                                    v
              +---------------------+---------------------+
              |           Cluster / Shard Router          |
              +-----+-----------------------------+-------+
                    |                             |
                    v                             v
           +--------+--------+           +--------+--------+
           | Node shard 1    |           | Node shard 2    |
           |-----------------|           |-----------------|
           | KV Hash         |           | KV Hash         |
           | Timing Wheel    |           | Timing Wheel    |
           | Lazy checks     |           | Lazy checks     |
           | Singleflight    |           | Singleflight    |
           | Repl log        |           | Repl log        |
           +--------+--------+           +--------+--------+
                    |                             |
                    +-------------+---------------+
                                  v
                         +--------+--------+
                         | Origin / DB     |  (on miss / revalidate)
                         | + request coalesce
                         +-----------------+

   Clock: NTP + monotonic for intervals
   Metrics: expired_total, stampede_prevented, skew_ms
```

---

## 5. Design Deep Dive

### 5.1 Storing deadlines

```text
Prefer expire_at_ms (absolute) in entry
SET EX sec → expire_at = now_ms + sec*1000
TTL command → max(0, expire_at - now_ms)/1000
```

**Sliding TTL:** on Get, optionally `expire_at = now + window` — expensive write amplification; coalesce.

### 5.2 Lazy expiration path

```text
def get(key):
  e = table.get(key)
  if e is None: return miss
  if e.expire_at and monotonic_wall() >= e.expire_at:
    table.delete(key); wheel.remove(key)
    return miss
  if soft and near_expire(e):
    maybe_async_revalidate(key)
  return e.value
```

### 5.3 Timing wheel

```text
Hierarchical wheel:
  ticks: 1s, 1m, 1h buckets
  insert key into bucket by expire_at
  on tick: expire all in due bucket → delete

O(1) insert; good for massive expires/s
Tradeoff: accuracy to tick granularity (1s OK for many apps)
```

### 5.4 Redis-style sampling (classic interview)

```text
each cycle (budgeted):
  sample N keys from expire dict
  delete expired
  if expired_ratio > 0.25: run another cycle
Adapt N to CPU budget
```

### 5.5 Stampede deep dive

**Problem:** synchronized TTL on popular keys.

**Mitigations layered:**

1. **Jitter:** `ttl' = ttl * U(0.9, 1.1)`  
2. **Singleflight:** `loading[key]` mutex / group  
3. **Soft-TTL:** serve stale for `stale_win` while refresh  
4. **XFetch:** probabilistic early recompute  
5. **Origin shield / coalescing proxy** at 100×  

```text
def get_or_load(key):
  v = cache.get(key)
  if v.ok: return v
  return singleflight.do(key, lambda: origin.load(key) |> cache.set)
```

### 5.6 Clock skew deep dive

| Issue | Mitigation |
|-------|------------|
| Wall clock step | Detect jump; prefer `CLOCK_MONOTONIC` for durations |
| Cross-node skew | NTP; replicate `expire_at`; document ±Δ |
| Leap seconds | Use UTC ms carefully; prefer monotonic deadlines from set time |
| Container time namespace | Caution with freezes — monotonic helps |

**Interview honesty:** cache TTL cannot be more precise than clock sync + tick.

### 5.7 Distributed replication of TTL

```text
Primary SET key val PXAT t
Replicate: {op:SET, key, val, expire_at:t}
Replica applies same expire_at
DEL on expire may not replicate if lazy-only — or replicate DEL for sync
Active expire on each node independently OK if absolute timestamps
```

**Failover:** new primary inherits entries with absolute deadlines.

### 5.8 Negative caching

```text
On origin miss: SET key NEG_MARKER EX 5–30s
Protects origin from repeated misses
Invalidate NEG on write path (CDC / app DEL)
```

### 5.9 Persistence interactions (Phase 1.5)

| Format | TTL restore |
|--------|-------------|
| RDB | Store expire_at; discard already past on load |
| AOF | Replay SET+Expire |

### 5.10 Reliability

| Failure | Mitigation |
|---------|------------|
| Expire storm CPU | Budget; adaptive sampling; wheel |
| Origin down | Soft serve stale; error if no stale |
| Node kill | Replicas; accept TTL skew window |
| Clock desync | Alert skew_ms; pause aggressive expiry optional |
| Memory pressure | Evict + expire cooperate |

**Reliability principles:**

1. Never rely on lazy alone for memory.  
2. Bound origin with singleflight.  
3. Absolute deadlines on the wire.  
4. CPU budget for expire cycles.  
5. Metrics for expired vs evicted.

### 5.11 Scalability

| Scale | Tactic |
|-------|--------|
| 10× | Hybrid expire; jitter; client singleflight |
| 100× | Wheels; shard expire; soft TTL tier; origin shield |
| 1,000× | Local L1 TTL caches; approximate membership for due sets; tiered storage |

**Expire sharding:** each node handles its key range — natural.

### 5.12 Maintainability

| Practice | Why |
|----------|-----|
| Tunables: sample rate, tick, jitter | Ops without redeploy |
| Exhaustive clock jump tests | Prevent silent bugs |
| Chaos: expire storms | Capacity validation |
| Clear semantics doc | App developers set TTLs wisely |
| Separate soft vs hard TTL APIs | Avoid accidental stale |

### 5.13 Soft TTL vs hard TTL

```text
hard_deadline: cannot serve after (security tokens)
soft_deadline: try refresh; may serve stale until hard
Example: soft=30s hard=5m for HTML fragments
Never soft-stale for authz decisions
```

### 5.14 Progressive scale

**Baseline:** single primary+replicas, lazy+sample expire, relative EX.

**10×:** PXAT, jitter, singleflight library standards.

**100×:** timing wheels, soft TTL, shield service, skew monitors.

**1,000×:** multi-tier caches with independent TTLs; probabilistic structures; global origin coalescers.

---

## 6. Wrap-Up

### 6.1 Design summary

A **TTL-first cache** using **absolute deadlines**, **lazy+active hybrid expiry** (sampling → timing wheels), **TTL-aware eviction**, **distributed PXAT replication**, and **layered stampede control** under **explicit clock-skew limits**.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Lost |
|----------|--------|------|
| Accuracy vs CPU | Tick granularity | Perfect ms active delete |
| Stale vs stampede | Soft TTL optional | Always fresh |
| Relative vs absolute | Absolute on wire | Simpler SET EX only |
| Heap vs wheel | Wheel at scale | Exact ordered deletes cheaply |

### 6.3 Deal-breakers

1. Lazy-only expiry at large idle key cardinality.  
2. Synchronized TTLs without jitter/singleflight on hot keys.  
3. Relative TTL replication without skew analysis.  
4. Full-keyspace scan expire loops.  
5. Soft-stale for security-critical data.  
6. Claiming ms-global synchronized expiry.

### 6.4 Progressive scale one-liner

> **Lazy+sample → PXAT+jitter+singleflight → timing wheels & soft TTL → multi-tier approximate expiry at planet QPS.**

### 6.5 Reliability / Scalability / Maintainability

```text
Reliability: hybrid expire, origin coalesce, skew alerts, eviction safety
Scalability:  wheels, shards, shields, L1/L2 TTL tiers
Maintainability: tunables, semantics docs, clock/chaos tests
```

---

## 7. Deeper / Related Interview Questions

### 7.1 Expiry mechanics

**Q1: Lazy vs active?**  
A: Lazy correctness on access; active reclaims cold expired memory.

**Q2: Why timing wheel?**  
A: O(1) scheduling of massive expirations vs heap log N.

**Q3: Redis expires how?**  
A: Lazy + adaptive sampling — cite as prior art.

**Q4: Can expired keys still appear in KEYS scan?**  
A: Briefly until lazy/active hits — document.

**Q5: TTL accuracy SLO?**  
A: Lazy exact; active within tick/sample lag.

### 7.2 Stampede

**Q6: What is thundering herd?**  
A: Many clients miss simultaneously → origin overload.

**Q7: Singleflight vs lock?**  
A: Singleflight coalesces; distributed lock across nodes needs care.

**Q8: XFetch?**  
A: Probabilistically expire early so one client rebuilds before hard expiry.

**Q9: Jitter enough alone?**  
A: No for extreme hot keys.

### 7.3 Clocks & distribution

**Q10: Why PXAT?**  
A: Absolute deadline survives replication delay.

**Q11: Monotonic vs wall?**  
A: Durations/monotonic; deadlines need shared wall ≈ UTC.

**Q12: Replica serves expired key?**  
A: Possible within skew — cache OK.

**Q13: NTP failure mode?**  
A: Jump detection; page ops; freeze expire optional.

### 7.4 Memory

**Q14: Evict vs expire?**  
A: Expire is semantic time; evict is pressure — both free memory.

**Q15: Why volatile-ttl?**  
A: Prefer removing soon-worthless keys.

**Q16: Metadata overhead?**  
A: Dominates tiny values — sometimes coalesce / slab.

### 7.5 Product semantics

**Q17: Sliding sessions in cache?**  
A: Refresh TTL on access carefully; write amp.

**Q18: Negative caching dangers?**  
A: Masks new writes — must invalidate.

**Q19: Soft TTL for HTML?**  
A: Great; not for permissions.

### 7.6 Estimation drills

**Q20: Expire/s if 500M keys avg TTL 250s uniform?**  
A: 500M/250 ≈ 2M expires/s — need wheels.

**Q21: Stampede Q without singleflight?**  
A: ≈ concurrent waiters on key ≈ QPS × RTT.

### 7.7 Alternatives & deal-breakers

**Q22: Central expire worker for cluster?**  
A: Hotspot / SPOF — per-shard expire better.

**Q23: App-only TTL ignore server?**  
A: Inconsistent; server should enforce.

**Q24: GC-only memory free?**  
A: Language GC ≠ key expiry semantics.

### 7.8 Interview craft

**Q25: Opening?**  
A: Hybrid expiry, absolute deadlines, stampede, skew — then API.

**Q26: L5+ signals?**  
A: Wheel vs sample, XFetch, PXAT, soft vs hard, expire storm CPU budget.

**Q27: Common mistake?**  
A: Only talking LRU; ignoring TTL storms and clocks.

---

### Appendix A — Lazy get

```text
def get(k):
  e = m[k]
  if not e: return None
  if e.expire_at and now() >= e.expire_at:
    del m[k]
    return None
  return e.val
```

### Appendix B — Sampling expire

```text
def active_expire_cycle(budget_ms):
  start = now()
  while now()-start < budget_ms:
    sample = random_keys(expire_index, N)
    expired = 0
    for k in sample:
      if due(k): del_key(k); expired += 1
    if expired/N < 0.25: break
```

### Appendix C — Timing wheel sketch

```text
class Wheel:
  buckets: array<list<key>>
  tick_ms
  insert(key, expire_at):
    idx = (expire_at // tick_ms) % len(buckets)
    buckets[idx].append(key)
  on_tick(t):
    for key in buckets[t % len]:
      if due(key): del_key(key)
```

### Appendix D — Singleflight

```text
inflight = map()
def load(key):
  if key in inflight: return inflight[key].wait()
  fut = Future()
  inflight[key] = fut
  try:
    v = origin.get(key)
    cache.set(key, v, ttl_jitter(TTL))
    fut.set(v)
  finally:
    del inflight[key]
  return v
```

### Appendix E — XFetch early expire

```text
def should_early_expire(remaining, beta=1.0):
  # remaining in (0, ttl]
  return random() < exp(-remaining / (beta * ttl_or_delta))
```

### Appendix F — Progressive scale table

| Scale | Expiry | Stampede | Dist |
|-------|--------|----------|------|
| Baseline | Lazy+sample | Jitter | Relative EX |
| 10× | +PXAT | +singleflight | Abs deadlines |
| 100× | Wheels | +soft TTL | Shield |
| 1,000× | Tiered approx | Global coalesce | Multi-tier |

### Appendix G — NFR card

```text
Lazy exact expiry on access
Active reclaim with CPU budget
Hot-key origin ≤ 1 inflight / node
Document clock skew window
volatile-ttl under pressure
```

### Appendix H — Eviction vs expire metrics

| Metric | Meaning |
|--------|---------|
| `expired_keys` | TTL natural |
| `evicted_keys` | Memory pressure |
| `hit_rate` | Effectiveness |
| `origin_qps` | Stampede indicator |
| `expire_cycle_ms` | CPU cost |

### Appendix I — Soft TTL response headers (HTTP analogy)

```text
Cache-Control: max-age=30, stale-while-revalidate=60
# Maps to soft=30 hard=90 mental model
```

### Appendix J — Clock jump handler

```text
if wall_delta > THRESH and mono_delta small:
  alert("clock jump")
  # recompute or clamp expire_at relative to mono offset table
```

### Appendix K — Common pushbacks

| Pushback | Response |
|----------|----------|
| “LRU enough” | Idle expired keys; freshness SLAs |
| “Expire thread deletes all due exactly” | CPU; use wheel/sample |
| “NTP perfect” | Still skew; design tolerance |
| “Disable TTL jitter” | Stampede risk |

### Appendix L — Related systems

| System | Relation |
|--------|----------|
| Redis expires | Prior art sampling |
| CDN Cache-Control | Soft/hard analogy |
| Guava / Caffeine | Local TTL + early expire ideas |
| Memcached | Lazy-ish + LRU |

### Appendix M — Glossary

| Term | Meaning |
|------|---------|
| Lazy expire | Delete on access when due |
| Active expire | Background reclaim |
| Timing wheel | Bucketed timer structure |
| Soft TTL | Serve stale while refresh |
| Singleflight | Coalesce concurrent loads |
| PXAT | Expire at absolute ms |

### Appendix N — Worked stampede example

```text
Key QPS 50K, origin latency 20ms
No protect: ~50K simultaneous origin on expiry boundary
Singleflight: 1 in-flight; others wait ~20ms
Jitter 10% on 60s TTL: spread 6s — still spikes without coalesce
```

### Appendix O — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Is expiry atomic cluster-wide? | No |
| Read-your-write TTL update? | Same primary yes |
| Stale after EXPIRE? | Until lazy/active/replica apply |
| Soft serve after hard? | No |

### Appendix P — 30m checklist

1. Clarify accuracy, memory, distributed, stampede.  
2. Hybrid lazy+active.  
3. Absolute deadlines.  
4. Stampede triad.  
5. Clock skew honesty.  
6. Eviction interaction.  
7. Scale 10×/100×/1,000×.  
8. Deal-breakers.

### Appendix Q — API examples

```text
SET session:123 data PXAT 1735689600000
GET session:123
TTL session:123
EXPIRE session:123 3600
```

### Appendix R — Near-expire revalidation

```text
if e.expire_at - now < soft_window:
  trigger_async_refresh(key)  # singleflight
return e.val  # possibly soft
```

### Appendix S — Hierarchical wheel sizes

```text
wheel_sec: 256 buckets × 1s
wheel_min: 64 × 256s
cascade on tick — like Netty HashedWheelTimer / Kafka rework ideas
```

### Appendix T — Why not DB TTL alone?

```text
DB TTL (e.g. Dynamo) good; cache TTL still needed for hot path latency
Different layers different TTLs
```

### Appendix U — Multi-tier TTL example

```text
L1 process: TTL 5s
L2 Redis: TTL 60s
L3 CDN: TTL 30s + SWR
Origin: SoT
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Jitter, PXAT, singleflight |
| 100× | Wheels, soft TTL, shields |
| 1,000× | Tiered TTL, approx due sets |

### Appendix W — Testing matrix

| Test | Expect |
|------|--------|
| Lazy due key | Miss |
| Idle expired | Active frees |
| Clock +1h | Keys expire; alert |
| Hot expiry | Origin QPS ~1 |
| Mem full | Evict volatile |

### Appendix X — Negative cache

```text
SET miss:user:9 __NIL__ EX 10
```

### Appendix Y — Opening script

> “I'll design a TTL-centric cache: absolute deadlines, lazy+active hybrid expiry, timing wheels at scale, PXAT replication under clock skew, and stampede protection via jitter, singleflight, and optional soft TTL.”

### Appendix Z — Interview contrast card

| Topic | LRU-only cache | TTL-based (this) |
|-------|----------------|------------------|
| Freshness | Indirect | Explicit deadline |
| Idle garbage | Evict pressure | Active expire |
| Stampede | Miss storms | First-class |
| Clocks | Minor | Central |

---

*End of TTL-Based Cache system design.*
