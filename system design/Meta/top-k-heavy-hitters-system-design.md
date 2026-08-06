# System Design: Top-K Heavy Hitters

> **Focus areas:** Streaming heavy-hitters · Count-Min / Space-Saving / HeavyKeeper · Exact candidate refinement · Hot-key salting · Mergeable sketches · Approximate vs exact SLOs  
> **Style:** End-to-end Meta-style streaming design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split ingest vs query planes, explicit error bounds, deal-breakers for “exact global top-K at millions/s”  
> **Interview theme:** Classic Meta L5+ streaming + aggregation — find keys whose frequency exceeds a threshold / return top-K under adversarial cardinality

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

Goal: **bound the product**—a real-time **top-K heavy hitters** service that continuously identifies the most frequent keys in a high-volume event stream, with bounded memory, bounded error, and a low-latency query API.

### 1.0 What this is / is not

| Dimension | **Top-K heavy hitters (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Find keys with freq ≥ φN or top-K by count | Full analytics warehouse / BI SQL |
| Success | Fresh, memory-bounded, auditable error | Perfect historical exact counts for all keys |
| Data plane | Stream ingest + continuous aggregation | Nightly batch-only MapReduce (hooks OK) |
| Query | Read top-K / is-heavy? / estimate(key) | Arbitrary ad-hoc joins |
| Correctness | Approx OK with documented ε, δ | Exact for every key worldwide MVP |

**Scope statement:** Design a top-K / heavy-hitters platform: multi-window frequency tracking, approximate sketches + exact hot-set refinement, merge across shards, spam/gaming resistance for open key spaces, progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a “key”? | Hashtag, URL, user_id, content_id, IP, search query — lock one | Event schema with `key`, `weight`, `ts`, `shard_hint` |
| F2 | Top-K or threshold φ? | Both: top-K display + heavy if count ≥ φN | Heap of candidates + φ threshold check |
| F3 | Time windows? | Tumbling/sliding: 1m, 5m, 1h (lock 2–3) | Parallel window state; different freshness |
| F4 | Exact counts? | Approx OK if error bounded; exact for displayed K | Sketch long-tail + exact for candidates |
| F5 | Query API? | `GET /topk`, `GET /estimate/{key}`, `GET /is_heavy` | Cacheable read path for top-K snapshots |
| F6 | Weighted events? | Optional weight (likes, bytes, revenue) | `ZINCR`-style weight in sketch/exact |
| F7 | Dedup / abuse? | Same actor flooding one key should not dominate | Per-actor contribution caps |
| F8 | Freshness? | Seconds–minutes for short windows | Streaming job; publish every T seconds |
| F9 | Multi-tenant? | Yes — separate namespaces / apps | `(tenant, key)` composite; quota per tenant |
| F10 | History? | Snapshots for charts Phase 1.5 | Periodic snapshot store |
| F11 | Delete / forget key? | GDPR erase rare; suppress key common | Tombstone + policy filter at publish |
| F12 | Admin ops? | Reset window, pin/suppress key | Control plane separate from ingest |

**MVP functional scope:**

1. Ingest keyed events into a durable log (Kafka/Pulsar).  
2. Maintain rolling top-K for windows: **1m, 5m, 1h**.  
3. Support `estimate(key)` with documented error bounds.  
4. Identify heavies where estimated count ≥ φ · N_window.  
5. Approximate heavy-hitters with bounded memory; exact counters for top candidates.  
6. Publish versioned top-K snapshots to a low-latency read store.  
7. Multi-tenant namespace isolation + per-tenant rate limits.

**Out of MVP:**

- Exact counts for every key in the universe  
- Sub-second strongly consistent global top-K  
- Full ML anomaly detection (mention as Phase 2)  
- Cross-key joins / secondary indexes  
- Perfect delete-within-window for GDPR at stream speed (hooks only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest durability | No silent loss after ACK | Kafka multi-AZ; at-least-once |
| N2 | Query latency (top-K) | Feels instant | p99 < 20–50ms origin; CDN for public |
| N3 | Estimate latency | Inline / cache | p99 < 10–30ms |
| N4 | Freshness (1m window) | Near-real-time | End-to-end lag p99 < 5–15s |
| N5 | Memory bound | Fixed per shard | O(ε⁻¹ log δ⁻¹) or O(K/φ) not O(cardinality) |
| N6 | Approx error | Documented | Relative ε for counts; no false negatives for φ-heavies (Space-Saving style) where claimed |
| N7 | Availability (read) | Critical dashboards | 99.9%+ stale-if-error |
| N8 | Multi-region | Global tenants | Regional shards + hierarchical merge |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Events for `key=A` surge → enters candidate set → appears in top-K within publish interval.  
2. Client `GET /topk?window=5m&tenant=ads` → snapshot hit → ranked list.  
3. `GET /estimate/A` → exact if candidate else CMS/HeavyKeeper estimate.  
4. Key cools off → slides out of heap → demoted from exact map after grace.  
5. Admin suppresses toxic key → filtered from published board next cycle.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cardinality explosion (billions of unique keys) | Sketches only; never materialize all keys |
| Hot key thundering herd (one key 40% traffic) | Salt hot keys; local partials + periodic combine |
| Clock skew / late events | Event-time + watermark; bounded lateness |
| Shard offline | Serve last good snapshot; mark degraded |
| Kafka lag spike | Query serves last publish; SLO burn alert |
| Tie scores | Deterministic tie-break (key lex + prior rank) |
| Oscillation near K boundary | Hysteresis / sticky rank |
| Weight=0 or negative | Reject at ingest validation |
| Tenant quota exceeded | Drop/sample with metric; fair share |
| Replay after bugfix | Idempotent `event_id`; rebuild from log |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak events/s | 100K | 1M | 10M | 100M |
| Distinct keys / day | 50M | 500M | 5B | 50B |
| Tenants | 100 | 1K | 10K | 100K |
| Windows | 3 | 3–4 | 4–5 | 5+ |
| Top-K (display) | 100 | 100 | 100–1K | hierarchical |
| Candidate set C | 1K–5K | 5K–20K | 20K–100K | per-cell |
| Query QPS (top-K) | 5K | 50K | 500K | 5M |
| Estimate QPS | 20K | 200K | 2M | 20M |
| Publish interval | 5–10s | 2–5s | 1–2s | ≤1s + deltas |
| Stream cores (order) | 200 | 2K | 20K | cell fleets |

**What each jump forces:**

- **10×:** Partition by `hash(key)`; sketches mandatory; CDN/cache for top-K; hot-key salting.  
- **100×:** Regional aggregator cells; merge only top-C per cell; separate exact path for ultra-hot keys.  
- **1,000×:** Hierarchical merge (rack→AZ→region→global); approx everywhere except pinned hot set; query fully edge-served.

### 1.5 Etc. (Constraints & Assumptions)

- Upstream producers already emit normalized keys (we are not the entire social graph).  
- **Event-time** preferred; processing-time OK if interviewer agrees for MVP.  
- Top-K is a **derived** view — not a source of truth for billing without audit path.  
- Open key space (users can invent keys) → memory bound is non-negotiable.  
- Public top-K boards are cacheable; per-key estimate may be tenant-authenticated.

**Scope statement to repeat back:**

> Design a top-K heavy-hitters service that maintains rolling frequency rankings over multiple windows via a streaming pipeline with mergeable approximate sketches, exact candidate refinement, hot-key salting, multi-tenant isolation, and a cacheable query path—scaling through 10× / 100× / 1,000× with sharded aggregation then hierarchical merge.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Ingest events** | Keyed observations | ~100K/s | ~1M/s | Kafka |
| **State updates** | Sketch / exact upserts | ~100K/s | ~1M/s | Flink state / Redis |
| **Publish writes** | Top-K snapshots | tenants×windows / T | ×10 | Redis / Memcache |
| **Top-K reads** | Snapshot GET | ~5K/s | ~50K/s | Edge + Redis |
| **Estimate reads** | Point query | ~20K/s | ~200K/s | Local sketch replica / RPC |
| **Admin / policy** | Suppress / reset | low | low | Control plane |

**Anti-pattern:** one “QPS” mixing Kafka produce, RocksDB state, and CDN GETs.

### 2.2 Cardinality & memory

```text
Naive exact: 50M distinct keys/day × 16B (key hash + count) ≈ 800 MB just counts
× 3 windows × 100 tenants × replication → tens–hundreds of GB if lucky
At 5B distinct/day exact → DEAL-BREAKER (tens of TB+ with indexes)

Conclusion: exact maps for all keys × all windows × tenants = impossible
Must use: fixed-memory sketches + exact only for candidate / hot set
```

### 2.3 Sketch sizing (Count-Min)

```text
CMS: width w = ⌈e/ε⌉, depth d = ⌈ln(1/δ)⌉
ε=0.001, δ=1e-4 → w≈2718, d≈10 → ~27K counters
× 8B = ~216 KB per sketch instance
× shards × windows × tenants (or shared pooled) — still far cheaper than exact

Space-Saving / Misra-Gries: O(1/ε) counters for ε-approx frequent items
For φ-heavies with ε=φ/2: ~2/φ counters — e.g. φ=0.001 → ~2K counters
```

### 2.4 Query amplification

```text
Dashboard polls every 10s × 10K viewers = 1K QPS if uncached origin
With edge TTL 5s on top-K: origin ≈ #boards / TTL
Estimate QPS harder — colocate sketch replicas or RPC to owning shard
```

### 2.5 Merge cost (shard → global)

```text
Each shard publishes top-C candidates (C=2000) per window every T seconds
Global merge input = shards × C
100 shards × 2000 = 200K rows / T — trivial vs raw 1M events/s
Key idea: never ship all key counts to a central aggregator
```

### 2.6 Hot-key math

```text
If one key is 30% of 1M events/s = 300K updates/s to one partition
Single RocksDB key hotspot → latency collapse
Salt into N=16–64 partial counters; combine on read/publish
Partial counter combine latency: N Redis/Rocks gets ≪ 300K single-key writes
```

### 2.7 HeavyKeeper / Space-Saving memory worksheet

```text
HeavyKeeper (interview sizing):
  buckets B ≈ 65536, rows d ≈ 2–4, fingerprint+count ≈ 8–12B each
  mem ≈ B × d × 12B ≈ 3–6 MB per (tenant, window, shard) instance
  Plus exact candidate map: C=5K × (24B key hash + 16B meta) ≈ 200 KB

Space-Saving for φ-heavies:
  counters m = ⌈1/ε⌉ with ε ≈ φ/2
  φ=0.001 (0.1% of stream) → m ≈ 2000 counters × 32B ≈ 64 KB
  Guarantee: any item with freq > φN reported; counts within εN

Per-shard total (sketch + exact + window buckets for candidates):
  ~10–20 MB × 3 windows × 128 shards ≈ 4–8 GB fleet RAM — tractable
Compare exact-all at 5B keys: petabyte class — deal-breaker
```

### 2.8 Window-bucket memory

```text
Sliding 5m with 15s buckets → 20 buckets
If EVERY key kept 20 counters: cardinality × 20 × 8B → explosion
Only allocate ring buffers for candidate/hot keys (C≈2K–20K)
Long-tail: single CMS covering whole window OR decay score without buckets

Candidate bucket RAM:
  10K candidates × 20 buckets × 8B = 1.6 MB per shard/window — fine
```

### 2.9 Bandwidth: ingest vs merge vs query

```text
Ingest: 1M events/s × 80B ≈ 80 MB/s ≈ 0.64 Gbps into Kafka (plus replication×3)
Merge: 128 shards × 2K candidates × 40B / 5s ≈ 2 MB/s — noise vs ingest
Query boards: edge-absorbed; origin publish 100 tenants × 3 windows / 5s ≈ 60 writes/s
Estimate API: colocate CMS replicas; avoid cross-AZ RPC per keystroke-equivalent
```

### 2.10 Progressive capacity table

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Kafka ingest | 0.1M/s | 1M/s | 10M/s | 100M/s cell-sharded |
| Flink cores (order) | 50 | 500 | 5K | cell fleets |
| Sketch RAM total | ~10 GB | ~100 GB | ~1 TB | hierarchical / pooled |
| Exact candidates/shard | 2K | 5K | 20K | threshold-promoted |
| Merge rows/interval | 50K | 200K | 2M (tree) | tree only |
| Board origin QPS | 50 | 200 | edge | edge push |

**Anti-patterns (BOTE):**
- Sizing only “query QPS” while Kafka is the real firehose  
- Assuming CMS width for ε=1e-6 on every shard without RAM budget  
- Planning global merge of raw events instead of top-C  

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/topk?tenant=&window=&k=` | Versioned ranked list `{key, count_est, rank}` |
| `GET /v1/estimate/{key}?tenant=&window=` | Point estimate + error metadata |
| `GET /v1/is_heavy/{key}?phi=` | Boolean + estimate vs threshold |
| `POST /internal/events` | Prefer bus; HTTP for backfill/test |
| `POST /admin/suppress` | Policy suppress key |
| `POST /admin/reset_window` | Rebuild / clear window state |
| `GET /v1/health/freshness` | Lag / last publish watermark |

**Event schema (ingest):**

```text
HeavyHitterEvent {
  event_id,          // idempotency
  tenant_id,
  key: string,       // normalized
  weight: float,     // default 1.0
  ts_event,          // event time
  actor_id?,         // for contribution caps
  attrs?: map        // optional dimensions (not in MVP keys)
}
```

### 3.2 Data model (read side)

| Entity | Key | Value |
|--------|-----|-------|
| Board snapshot | `(tenant, window, version)` | sorted top-K JSON |
| Exact hot count | `(tenant, window, key)` | exact count / score |
| Sketch blob | `(tenant, window, shard)` | CMS / HeavyKeeper bytes |
| Watermark | `(job, shard)` | last event-time processed |
| Policy | `(tenant, key)` | suppress / pin |
| Snapshot history | `(tenant, window, ts)` | charts |

### 3.3 Algorithms — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Exact hashmap** | Precise | Unbounded memory | Hot candidate set only |
| **Count-Min Sketch** | Fixed memory; mergeable | Over-estimate; needs heap for identity | Long-tail frequency + estimate API |
| **Space-Saving / Misra-Gries** | Finds φ-heavies; simple | Under/over nuances; merge trickier | Classic heavy-hitters teaching answer |
| **HeavyKeeper** | Strong accuracy on heavies | Slightly more complex | **Strong production MVP** |
| **HyperLogLog** | Uniques | Not frequency | Optional unique-actor feature |
| Redis `ZINCRBY` all keys | Simple ops | Won’t scale open cardinality | Tiny tenants / demos only |

**Chosen MVP:**

1. **Per-shard stream job:** HeavyKeeper (or CMS + Space-Saving heap) for observations.  
2. Maintain **exact counters** for current top-C candidates + keys crossing threshold.  
3. **Global / cross-shard merge:** exact merge of candidate lists (not “merge all sketches into one truth” for top-K identity).  
4. Optional **CMS sidecar** for `estimate(key)` on long-tail keys.  
5. Optional **HLL** per candidate for unique actors.

### 3.4 Windowing — Why X over Y

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| **Tumbling** | Simple; cheap | Boundary artifacts | 1h MVP |
| **Sliding (bucketed)** | Smooth UX | More state | 1m / 5m |
| **EMA decay** | Continuous | Harder “window” semantics | Phase 1.5 alternative |
| **Session** | Burst grouping | Not global top-K | Out of scope |

**Chosen:**

| Window | Implementation |
|--------|----------------|
| 1m | Sliding with 5–10s sub-buckets; sum last N |
| 5m | Sliding with 15–30s buckets |
| 1h | Tumbling 1m rolls + sum of 60; or EMA with advertised half-life |

**Deal-breaker:** claiming true per-event sliding windows for all keys at 10M events/s without bucketing/approx.

### 3.5 Pipeline topology

```text
Producers → validate/normalize → Kafka (keyed by hash(tenant,key))
  → Shard Flink jobs (sketch + exact candidates)
  → Candidate / board publish topic
  → Merger (per tenant or hierarchical)
  → Board store + sketch replicas
  → Top-K API / Estimate API → Clients
```

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| All-key storage | Sketches + candidate exact | Cardinality | Exact Redis ZSET for all keys |
| Aggregation | Shard first, merge top-C | Network/CPU | Central counter for every event |
| Stream engine | Flink / Dataflow | Event-time, state | Cron-only for 1m freshness |
| Query top-K | Versioned snapshot | Read QPS | Live full scan on each GET |
| Estimate long-tail | CMS replica | Cheap point query | Exact map lookup for cold keys |
| Hot keys | Salting + exact sidecar | Hotspot | Single partition key at 300K/s |

### 3.7 Deal-breakers & interview landmines

| Claim | Why it fails | Say instead |
|-------|--------------|-------------|
| “Merge all CMS then take top-K” | Sketch merge ≠ heavy identity; false heavies | Merge **candidate lists** with exact/refined counts |
| “Exact global top-K at 10M/s” | Memory + hotspot | Approx discovery + exact refinement for C |
| “Redis ZINCRBY for every key” | Open cardinality | Redis for boards + hot set only |
| “Compute top-K on each GET” | CPU + consistency flicker | Versioned snapshots + CDN |
| “Top-K from each shard → global top-K” | Misses globally heavy, locally mid-rank keys | Top-**C** with C ≫ K × fan-in heuristic |
| “Ignore actor caps” | Spam dominates | Cap + optional HLL uniques |

### 3.8 Consistency model (derived data)

```text
Boards are derived, eventually consistent with the event log.
Readers see: last published version (monotonic version per tenant×window).
Never: read-your-writes on arbitrary keys unless estimate API hits exact store.
Degraded mode: serve last-good board + watermark lag header.
```

**Anti-pattern:** promising linearizable exact counts for all keys under approximate sketches.

---

## 4. Architecture Diagram

```text
                         +------------------+
   Dashboards/Apps ----> |  Query API       |-----> Edge cache (top-K boards)
                         |  /topk /estimate |-----> Estimate routers
                         +--------+---------+
                                  |
                                  v
                         +--------+---------+
                         | Board + Exact    |  Redis / Memorystore
                         | Hot Store        |  versioned snapshots
                         +--------+---------+
                                  ^
                                  | publish
           +----------------------+----------------------+
           |                                             |
           v                                             v
  +------------------+                         +------------------+
  | Hierarchical     |<---- top-C candidates --| Shard Aggregators|
  | Merger           |                         | Flink / Dataflow |
  +--------+---------+                         +--------+---------+
           |                                             ^
           |                                             | consume
           |                                    +--------+---------+
           |                                    | Kafka            |
           |                                    | events.keyed     |
           |                                    | (tenant,key hash)|
           |                                    +--------+---------+
           |                                             ^
           |                                             |
           |                                    +--------+---------+
           |                                    | Ingest Gateway   |
           |                                    | validate, normalize
           |                                    | actor caps, quotas
           |                                    +------------------+
           v
    Policy / Admin (suppress, pin, reset)
    Hot-key detector → salt map → rebalance hints
```

**Ingest path:**

```text
Event arrives
  -> validate tenant, key, weight
  -> normalize key (casefold / NFKC as policy)
  -> apply actor contribution cap (pre-agg or in job)
  -> produce Kafka(event_id, tenant, key, weight, ts)
  -> ACK independently of top-K lag
```

**Shard aggregate path:**

```text
Kafka -> Flink keyBy(tenant, hash(key) % P)  // or salted hot key
  -> update HeavyKeeper / CMS
  -> if candidate or threshold crossed: exact[key] += weight
  -> every T sec: extract top-C -> Candidate topic + local board
```

**Merge path:**

```text
All shard candidate snapshots for tenant
  -> outer join by key
  -> count = Σ shard_exact (or re-estimate carefully)
  -> top-K heap + hysteresis + policy filter
  -> publish Board version++
```

**Estimate path:**

```text
GET /estimate/{key}
  -> if in exact hot store: return exact
  -> else route to owning shard CMS replica / ask aggregator
  -> return {estimate, epsilon, source}
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **At-least-once ingest** after Kafka ACK; processing idempotent on `event_id` (TTL dedup).  
2. **Published boards are versioned**; atomic swap — readers never see partial JSON.  
3. **Policy suppress always wins** over score.  
4. **Freshness watermark exposed**; never claim live when lag > SLO.  
5. **Memory per shard bounded** by sketch config + capped exact map size.  
6. **Shard failure ≠ empty top-K** — last good + `degraded=true`.

#### 5.1.2 Exactly-once vs at-least-once

| Mode | Approach | Tradeoff |
|------|----------|----------|
| At-least-once + idempotent | Dedup `event_id` short TTL | Simpler; tiny overcount if miss |
| Flink exactly-once | Checkpoint + transactional sink | Heavier ops |
| MVP recommendation | At-least-once + dedup window; atomic board publish | Practical L5 answer |

**Deal-breaker:** double-counting the same viral event into a heavy without any dedup story when duplicates are common.

#### 5.1.3 Late events & watermarks

```text
watermark = max_event_ts - allowed_lateness
late but in lateness: update correct bucket
too late: side output → metric / optional correction job
```

Bound lateness for 1m windows or state explodes.

#### 5.1.4 Oscillation / boundary flicker

Keys near rank K flicker in/out every publish.

Mitigations:

- Maintain candidate set C ≫ K  
- Hysteresis: must beat rank-K by margin μ to enter; must fall below K+μ to exit  
- EMA smooth counts before ranking  
- Sticky rank for small deltas

#### 5.1.5 Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Kafka lag | Consumer lag metrics | Autoscale; serve stale boards |
| State backend OOM | Container kill / GC | Cap exact map; enlarge sketch only with budget |
| Merger crash | Heartbeat / version stall | Hot standby; last-good boards |
| Poison key (huge string) | Ingest validation | Max key length; hash storage |
| Skewed partitions | Hot-key detector | Salt + split |

### 5.2 Scalability

#### 5.2.1 Partitioning

```text
Primary key: hash(tenant_id, key) → Kafka partition / Flink key
Hot key override: (tenant, key, salt) for N salts
Tenant isolation: separate topic or key prefix; quotas prevent noisy neighbor
```

**Salting correctness:**

```text
On update: weight goes to salt = hash(event_id) % N  (or round-robin)
On publish: count(key) = Σ_s partial[key, s]   // exact partials
On estimate: sum CMS estimates across salts OR maintain unsalt CMS sidecar
Never salt into independent top-K without combine — each salt sees 1/N frequency
```

#### 5.2.2 CMS / HeavyKeeper / Space-Saving math (deep)

**Count-Min Sketch**

```text
Parameters (ε, δ):
  width w = ⌈e/ε⌉
  depth d = ⌈ln(1/δ)⌉
Point query: ĥ(x) = min_i CMS[i][h_i(x)]
Guarantee: ĥ(x) ≤ f(x) + ε‖f‖₁ with probability ≥ 1-δ
Always ĥ(x) ≥ f(x) (over-estimate only from hash collisions)

Interview sizing example:
  ε=0.0001, δ=1e-6 → w≈27183, d≈14 → ~380K counters × 8B ≈ 3 MB
  At ‖stream‖=1e9, additive error ≈ 1e5 — OK to find 1e-3 heavies if refined
```

**Why CMS alone doesn’t give top-K identity:** CMS answers “how often for key x?” but does not enumerate which keys are heavy. Pair with:
- Heap of keys that ever crossed a threshold, or  
- Space-Saving / HeavyKeeper structure that retains candidate identities.

**Space-Saving / Misra-Gries**

```text
Maintain m counters of (key, count)
On existing key: increment
On new key if free slot: insert
On new key if full: decrement all counters by 1; evict zeros; insert (variant-dependent)
Space-Saving keeps estimated counts with known error bounds for φ-heavies
Memory O(m); pick m ≈ 1/ε
Merge of two Space-Saving summaries is non-trivial — prefer merge of exact candidates
```

**HeavyKeeper (production-leaning pitch)**

```text
Fingerprint in bucket + count; on collision, probabilistically decay loser
True heavies survive decay; mice get eroded → fewer false heavies than CMS+heap
Still promote survivors into exact map for displayed top-K
```

**Mergeability matrix**

| Structure | Mergeable? | Use for global top-K? |
|-----------|------------|------------------------|
| CMS | Yes (cellwise sum) | Frequency estimate only — **not** identity of top-K |
| HLL | Yes | Uniques feature |
| Exact candidate maps | Yes (sum by key) | **Yes — primary merge input** |
| Space-Saving | Awkward / lossy | Prefer not as sole global merge |
| HeavyKeeper | Implementation-specific | Usually extract top-C then merge exactly |

**Deal-breaker to miss:** “I’ll merge CMS sketches across regions and sort cells” — cells aren’t keyed by item identity.

#### 5.2.3 Sliding window buckets (deep)

```text
window W=5m, bucket b=15s → n = W/b = 20
Per candidate key: ring[20], head index, score = sum(ring)

On event in current bucket: ring[head] += w
On bucket advance:
  head = (head+1) % n
  ring[head] = 0   // expired slot cleared
  publish uses sum(ring)

Tumbling alternative for 1h:
  60 × 1m maps (or sketch per minute) → sum last 60
  Cheaper semantics explanation: "last 60 complete minutes"
```

**Long-tail without buckets:** EMA `score *= exp(-λΔt); score += w` — advertise as heat, not exact window count.

#### 5.2.4 Hierarchical / regional merge correctness

```text
Leaf shards → AZ merger (top-C1)
  → Region merger (top-C2)
  → Global merger (top-K)

C1 ≥ C2 ≥ K; inflate C at leaves so true global heavies aren't lost
Rule of thumb: C_leaf ≥ K × #children × safety (or use φ threshold promotion)
```

**False-negative scenario (must discuss):**

```text
K=100, 100 shards, each shard truncates to top-100 before merge
A key with equal count on all shards ranks ~150 locally everywhere
→ never enters any shard top-100 → absent from global — WRONG

Fix options:
  1) C_shard ≫ K (e.g. 2K–20K)
  2) φ-threshold promotion: emit any key with count ≥ φ · shard_volume
  3) Random sample channel of mid-tier keys (lossy but catches some)
  4) Hierarchical with larger C at each level
```

**Correctness property (sufficient condition, heuristic):**  
If global top-K cutoff is S, and a key’s mass is concentrated in ≤ r regions, each region’s C must include all keys above ~S/r. Validate offline with exact replay samples.

**Deal-breaker:** merging only top-K from each shard into global top-K.

#### 5.2.5 Estimate serving at scale

| Approach | Pros | Cons |
|----------|------|------|
| RPC to owning Flink task | Fresh | Coupled to job; failover hard |
| Replicated CMS snapshots | Scalable reads | Slightly stale |
| Exact-only for candidates | Precise | Long-tail unknown / approximate |

**Chosen:** periodic CMS snapshot to estimate replicas; exact store for candidates.

```text
Estimate API routing:
  1) exact hot store HIT → return exact, error=0
  2) else CMS replica for shard(tenant,key) → return ĥ, ε, δ, as_of
  3) optional: if ĥ > promote_threshold, async promote to exact tracking
```

#### 5.2.6 Progressive scale playbook

| Scale | Must add |
|-------|----------|
| Baseline | Kafka + Flink + Redis boards |
| 10× | Sketches everywhere; CDN; salting |
| 100× | Cells; candidate bus; estimate replicas |
| 1,000× | Hierarchical merge; edge push; tenant cells |

| Jump | Concrete change | Anti-pattern if skipped |
|------|-----------------|-------------------------|
| →10× | CMS/HK + candidate exact; board CDN | Exact ZSET for all keys |
| →100× | Per-cell Kafka + merger on candidates | Single global Flink |
| →1,000× | Tree merge; tenant cells; edge board push | All-to-one merger |

### 5.3 Maintainability

#### 5.3.1 Config as code

```text
tenant_tier: {K, C, ε, δ, windows, publish_ms, lateness, per_actor_cap}
algo_version: heavykeeper:v3
board metadata must echo algo_version + config_hash
```

- Canary new algo on shadow tenants before cutover  
- Feature-flag hysteresis μ and C independently of sketch ε  

#### 5.3.2 Observability

| Signal | Why |
|--------|-----|
| Ingest QPS / lag | Pipeline health |
| Exact map size | Memory pressure |
| Board version age | Freshness SLO |
| Estimate error audit | Sample exact vs approx offline |
| Hot-key salt map size | Skew |
| Tenant quota drops | Fairness |
| Merge candidate recall proxy | Offline: % of true top-K present in ∪ shard top-C |
| Rank flicker rate | UX / hysteresis tuning |

#### 5.3.3 Offline audit (trust but verify)

```text
Daily/hourly job:
  sample N keys + all displayed top-K keys
  compute exact counts from log for window
  compare to board/estimate
  alert if relative error > budget for keys with count ≥ T
```

#### 5.3.4 Testing strategy

- Golden streams with known top-K → assert recall of φ-heavies  
- Adversarial cardinality generators (zipf + uniform flood)  
- Chaos: kill merger, stall Kafka, skew partitions  
- Property tests: Space-Saving guarantees where claimed  
- Merge simulation: plant a globally heavy, locally mid-rank key — must appear  

#### 5.3.5 Operability runbooks

1. Lag burn → scale consumers / reduce per-event work.  
2. Memory burn → shrink exact C, tighten TTL, check hot keys.  
3. Wrong top-K → audit suppress list, hysteresis, merge C too small.  
4. Rebuild → replay Kafka from offset with new job version into shadow; atomic pointer swap.

### 5.4 Algorithm selection playbook (topic deep dive)

| Goal | Prefer | Avoid |
|------|--------|-------|
| Point estimate any key | CMS replica | Scanning logs online |
| Discover heavies | HeavyKeeper or SS + heap | CMS alone |
| Displayed top-K accuracy | Exact map for candidates | Pure sketch ranks |
| Unique actors | HLL on candidates | Exact set of all users |
| Multi-tenant fairness | Quotas + separate sketches | Shared heap without caps |

**Promotion state machine:**

```text
OBSERVED (sketch only)
  -> count_est ≥ T_promote or in SpaceSaving survivors
  -> CANDIDATE (exact counter + optional bucket ring)
  -> in global top-K after merge
  -> DISPLAYED
  -> falls below T_demote for M publishes
  -> CANDIDATE → (optional) sketch-only
```

### 5.5 Multi-tenant & noisy-neighbor controls

```text
Per-tenant:
  ingest quota (events/s)
  max exact map size
  max sketch memory
  max boards / windows
Isolation:
  separate Flink slot sharing groups OR separate clusters for whale tenants
Noisy neighbor symptom: one tenant fills RocksDB → others lag
Mitigation: hard caps + kill-switch drop-tail for offender
```

### 5.6 Anti-patterns checklist

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| Exact-all keys | OOM / $$ | Sketches + C |
| Merge CMS for top-K identity | Wrong leaders | Candidate merge |
| Truncate to K at leaves | Missing globals | C ≫ K |
| No hot-key salt | Partition meltdown | Salt + combine |
| Live top-K on GET | p99 blowup | Snapshots |
| No dedup under at-least-once | Inflated heavies | event_id TTL |
| Raw count under spam | Bought top-K | Actor caps + trust |
| One global QPS number | Wrong capacity plan | Split load classes |

---

## 6. Wrap-Up

### 6.1 Design summary

A **top-K heavy-hitters** platform ingests keyed events into Kafka, aggregates per shard with **fixed-memory sketches** plus an **exact candidate set**, publishes versioned boards via a **hierarchical merger**, and serves top-K from cache while routing long-tail estimates to sketch replicas. Scale comes from **never materializing all keys** and **never shipping raw counts globally**.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Approx vs exact | Approx long-tail, exact hot | Bounded error on cold keys |
| Freshness vs cost | Publish every few seconds | Seconds of staleness |
| Merge fan-in | Top-C not top-K | Extra network, correct recall |
| Dedup window | Finite TTL | Rare double-count |

### 6.3 Deal-breakers (say out loud)

1. Exact Redis ZSET for every key at open cardinality.  
2. Merging only top-K per shard into global top-K.  
3. Single partition for a key that is 30% of traffic without salting.  
4. Computing top-K with a full scan on every query.  
5. Ranking solely by raw count under adversarial actors with no caps.

### 6.4 What to say in 45 minutes

1. Clarify key type, K vs φ, windows, error, freshness.  
2. Cardinality math → reject all-exact.  
3. Draw Kafka → shard Flink → merge → Redis → API.  
4. Deep dive HeavyKeeper/CMS + exact candidates + salting.  
5. Hierarchical merge recall argument.  
6. Walk 10×/100×/1,000×.  
7. List deal-breakers + observability.

### 6.5 Next steps / Phase 2

- ML-based anomaly downweight for gaming  
- Multi-dimensional heavy hitters (key × country) with careful explosion control  
- Exact audit path for billed metrics  
- Adaptive ε based on tenant SLA tier  

---

## 7. Deeper / Related Interview Questions

### Q1. What is a heavy hitter?

**A:** A key whose frequency is at least φ · N in a stream of N items (0 < φ < 1). Top-K returns the K highest-frequency keys (related but not identical when ties / thresholds matter).

### Q2. Why can’t we store exact counts for all keys?

**A:** Open key spaces produce hundreds of millions to billions of distinct keys/day. Exact maps grow with cardinality, blow memory/SSD, and make merges O(universe). Sketches bound memory to O(1/ε) or O(K/φ).

### Q3. Explain Count-Min Sketch briefly.

**A:** A d×w array of counters. Each item hashes to one cell per row and increments. Point query takes the **minimum** across rows — an overestimate with error ≤ εN with probability ≥ 1−δ when sized properly.

### Q4. Why minimum, not average, in CMS?

**A:** Each row independently overestimates due to collisions; the minimum is the least-overestimated (still ≥ true count). Average doesn’t preserve the one-sided error guarantee as cleanly for the classic bound.

### Q5. How do you find *which* keys are heavy with CMS alone?

**A:** CMS alone doesn’t retain identities of all keys. Pair with a heap / Space-Saving / HeavyKeeper that tracks candidate identities, or maintain a separate candidate set of keys that looked frequent recently.

### Q6. Space-Saving vs Misra-Gries?

**A:** Both track O(1/ε) counters for frequent items. Misra-Gries decrements all on overflow (classic); Space-Saving replaces the minimum counter and inherits its count (common in practice). Both give guarantees on over/under estimation with careful analysis.

### Q7. Why HeavyKeeper over CMS+heap?

**A:** HeavyKeeper uses fingerprinting + exponential decay on collisions to reduce errors specifically on heavy keys — often better recall/precision for top-K under the same memory. CMS remains great for mergeable long-tail estimates.

### Q8. Can you merge two Count-Min sketches?

**A:** Yes, if same w, d, and hash seeds: cell-wise sum. Merged sketch estimates the concatenated stream. This is why CMS is popular for distributed aggregation of *estimates*.

### Q9. Why is merging sketches insufficient alone for global top-K?

**A:** Merged CMS gives estimates for keys you query, but you still need a candidate identity set. If each shard only knows its local heavies, a globally heavy key that is middling everywhere can be missing from all candidate sets if C is too small.

### Q10. How large should candidate set C be vs K?

**A:** C ≫ K. For hierarchical merge, inflate: roughly ensure a true global top-K key is likely in some child’s top-C. Using φ-threshold promotion (`count ≥ φ · N_local`) is safer than blind top-K truncation.

### Q11. How do you handle hot keys?

**A:** Detect keys with update rate above threshold; salt into N partial keys `(key, salt)`; aggregate partials at publish/estimate time. Alternatively, isolate ultra-hot keys on dedicated tasks.

### Q12. At-least-once processing — won’t counts inflate?

**A:** Yes without care. Dedup on `event_id` with a TTL bloom/cache, or use transactional sinks with exactly-once. For dashboards, small overcount may be OK; for billing, need stronger idempotency/audit.

### Q13. Sliding vs tumbling windows for top-K?

**A:** Tumbling is cheaper and simpler; sliding (via buckets) is smoother for UX. Implement sliding as sum of last N tumbling sub-buckets rather than per-event expiry structures for all keys.

### Q14. How do you expose error to API clients?

**A:** Return `{estimate, epsilon, method, as_of}`. For exact candidates, `epsilon=0` / `method=exact`. Document that CMS estimates are upper bounds in expectation.

### Q15. False negatives on φ-heavies — when can you claim none?

**A:** Algorithms like Misra-Gries/Space-Saving can guarantee that every true φ-heavy appears in the structure (with count error bounds). CMS alone does not identify them without a candidate mechanism. Be precise about which guarantee you claim.

### Q16. Multi-tenant noisy neighbor?

**A:** Per-tenant quotas on ingest; separate sketch budgets; fair-share scheduler in Flink; isolate huge tenants to dedicated clusters/cells.

### Q17. How do you test approximate correctness?

**A:** Offline: generate streams with planted heavies; measure recall@K and count relative error. Online: shadow exact counters on a sampled key subspace; track p95 error.

### Q18. What if the interviewer demands exact top-K?

**A:** Exact top-K for the **displayed** set is achievable by promoting candidates to exact counters and verifying with a second pass / audit sample. Exact for the entire universe is the deal-breaker — push back with memory math.

### Q19. How does GDPR delete interact with sketches?

**A:** Sketches generally can’t delete a single key’s contribution cleanly (CMS is not deletable without extra structure). Options: TTL windows (natural expiry), keyed exact store for PII keys, or accept approximate residual and rely on short windows.

### Q20. Estimate API routing?

**A:** Consistent hash `(tenant,key)` → shard owning the CMS replica. For salted hot keys, sum partial estimates. Cache negative/long-tail estimates briefly.

### Q21. Difference between this and “trending hashtags”?

**A:** Trending adds velocity, trust, spam, regional boards, and product ranking. Heavy-hitters is the core frequency substrate; trending is a product scoring layer on top.

### Q22. How do you prevent rank flicker?

**A:** Hysteresis bands, EMA smoothing, sticky ranks, larger candidate sets, and publish-interval batching so you don’t re-rank on every event.

### Q23. Batch MapReduce every minute vs streaming?

**A:** Batch can hit 1m freshness for some SLOs but struggles with 1m sliding + low lag under spike load. Streaming with incremental state is the better default for seconds-level freshness; batch for historical rebuilds.

### Q24. How do you size Flink parallelism?

**A:** Start from peak events/s / per-core sustainable rate (benchmark). Account for state access, salting fanout, and checkpoint I/O. Leave headroom for skew.

### Q25. What breaks at 1,000×?

**A:** Single merger, single Kafka cluster, exact maps, estimate RPCs to busy tasks, and global all-to-one candidate flood. Need hierarchical merge, cell fabric, edge-served boards, and tenant isolation.

### Q26. Weighted heavy hitters?

**A:** Increment by `weight` instead of 1. Same sketches work. Cap per-actor weighted contribution to prevent pay-to-win / spam with huge weights.

### Q27. How do you do hierarchical merge without losing globals?

**A:** Promote by threshold φ_local or take top-C with C scaled by fan-in; optionally send sketch digests for verification; never truncate to K at leaves.

### Q28. Redis everywhere — why not?

**A:** Redis ZINCRBY is fine for small closed key sets. Open cardinality → memory death, hot keys, expensive backups, and painful multi-window fanout. Use Redis for **boards + hot exact**, not the universe.

### Q29. How do you version algorithm changes?

**A:** Dual-run shadow pipelines; boards carry `algo_version`; cut traffic when error KPIs match; keep rebuild-from-log capability.

### Q30. Give a 60-second algorithm pitch.

**A:** “We can’t store all keys. Each shard runs HeavyKeeper/CMS with an exact map for candidates. Every few seconds we publish top-C. A merger aggregates candidates into versioned top-K snapshots. Queries hit snapshots; point estimates hit CMS replicas. Hot keys are salted. That’s how we get bounded memory, high recall for heavies, and scalable reads.”

### Q31. Walk through CMS (ε, δ) sizing aloud.

**A:** width ⌈e/ε⌉, depth ⌈ln(1/δ)⌉, memory ≈ w·d·8B. State the over-estimate guarantee vs ‖stream‖₁. Then say displayed top-K still uses exact candidates.

### Q32. What’s the difference between φ-heavy hitters and top-K?

**A:** φ-heavy means frequency > φN (property of the stream). Top-K is rank-based and may include keys below φ if K is large / stream flat. Algorithms often target φ-heavies; product wants top-K — maintain C ≥ K and refine.

### Q33. Can two regions’ HeavyKeepers be merged bytewise?

**A:** Don’t assume yes. Extract top-C (or exact candidate maps) and merge by key. Treat sketch merge as frequency-assist only if the implementation documents mergeability.

### Q34. How do window buckets interact with sketches?

**A:** Prefer bucket rings only on the candidate set. Long-tail uses a per-window CMS or EMA. Allocating buckets for every key reintroduces cardinality explosion.

### Q35. How do you prove merge C is large enough?

**A:** Offline: from logged exact counts, measure recall of true global top-K inside ∪ shard top-C over time; alert if recall dips; ratchet C or add φ-promotion.

### Q36. Actor contribution caps — where enforced?

**A:** Ideally in the stream job keyed by (tenant, key, actor) with TTL state, or pre-agg gateway. Caps must be window-aware (stricter on 1m than 1h).

### Q37. How does suppress interact with estimates?

**A:** Boards filter suppressed keys. Estimate API may return `suppressed=true` or refuse — product call. Internal counters can continue for abuse analytics.

### Q38. What belongs in board metadata?

**A:** version, watermark, published_at, degraded, algo_version, config_hash, optional error_budget note. Clients/debuggers need provenance.

### Q39. Stream processing vs micro-batch every 10s?

**A:** Micro-batch can hit 1m freshness if lag is OK; streaming wins when event-time, hot-key handling, and sub-10s boards matter. Don’t pretend cron alone meets aggressive SLOs.

### Q40. How do you handle key cardinality spikes (scraping)?

**A:** Ingest admission control; max key length; hash storage; sketch fixed memory absorbs mice; exact map hard-capped with LRU/evict-lowest.

### Q41. Multi-window: one job or many?

**A:** One job updating multiple window states per event is CPU-efficient; separate jobs isolate failures. MVP: one job, multiple window operators sharing keyed stream.

### Q42. What are the top 5 anti-patterns to recite?

**A:** (1) Exact-all keys, (2) CMS-merge as top-K, (3) leaf truncate to K, (4) no hot-key salt, (5) live full top-K on every read.

### Q43. Estimate API SLA vs board SLA?

**A:** Boards are snapshot-fresh (seconds). Estimates may be sketch-stale by snapshot period; document `as_of`. Don’t use estimates for billing without exact path.

### Q44. How do you narrate 10× / 100× / 1,000× in 20 seconds?

**A:** “10×: sketches + salt + CDN boards. 100×: cells and candidate bus. 1,000×: hierarchical merge and edge push — never centralize raw events.”

### Q45. GDPR delete of a key — what happens?

**A:** Exact maps and boards can drop the key. Sketches cannot surgically delete — wait for window expiry / rebuild from privacy-filtered log. Design retention windows accordingly.

---

### Appendix A — NFR card

```text
Ingest durable (Kafka multi-AZ)
1m board lag p99 < 15s
Top-K query p99 < 50ms cached
Memory O(sketch + C) not O(cardinality)
Suppress wins
No all-exact open keyspace
```

### Appendix B — Board JSON schema

```json
{
  "tenant": "ads",
  "window": "5m",
  "version": 90211,
  "published_at": "2026-08-06T06:00:05Z",
  "watermark": "2026-08-06T05:59:55Z",
  "degraded": false,
  "algo": "heavykeeper:v3",
  "items": [
    {"rank": 1, "key": "campaign_42", "count": 1844221, "exact": true}
  ]
}
```

### Appendix C — CMS parameter cheat sheet

| ε | δ | w≈ | d≈ | counters |
|---|---|----|----|----------|
| 0.01 | 1e-3 | 272 | 7 | ~1.9K |
| 0.001 | 1e-4 | 2719 | 10 | ~27K |
| 0.0001 | 1e-5 | 27183 | 12 | ~326K |

### Appendix D — Hot-key salting

```text
if hot(key):
  salt = hash(event_id) % N
  partial = (tenant, key, salt)
else:
  partial = (tenant, key, 0)

# publish:
exact[key] = Σ_s exact[(key,s)]
```

### Appendix E — Progressive scale table

| Scale | Ingest | Agg | Merge | Read |
|-------|--------|-----|-------|------|
| Baseline | 1 Kafka | 1 Flink pool | Single merger | Redis |
| 10× | Partition surge | Sketch+exact | Merger HA | CDN |
| 100× | Regional Kafka | Cells | Hierarchical | Estimate replicas |
| 1,000× | Cell fabric | Leaf fleets | Tree merge | Edge push |

### Appendix F — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just use Redis” | Cardinality × windows × tenants |
| “Exact is required” | Exact for displayed K after promotion |
| “Batch is fine” | Conflicts with 1m lag SLO |
| “Merge sketches only” | Missing candidate identity / recall |

### Appendix G — Glossary

| Term | Meaning |
|------|---------|
| Heavy hitter | Key with frequency ≥ φN |
| Candidate set C | Keys eligible for exact refinement |
| Watermark | Event-time progress marker |
| Salting | Split hot key into N partials |
| Board | Published top-K snapshot |
| ε, δ | CMS error / failure probability |

### Appendix H — 30m interview checklist

1. Clarify key, K/φ, windows, error, freshness.  
2. Estimate events/s & cardinality → reject all-exact.  
3. Draw Kafka → shard agg → merge → Redis → API.  
4. Deep dive sketch + exact + hot-key.  
5. Hierarchical merge recall.  
6. Walk 10×/100×/1,000×.  
7. List deal-breakers.

### Appendix I — Worked example

```text
Baseline 100K events/s
Assume 5% of keys are “active”; still millions distinct/day
HeavyKeeper few MB/shard × 128 shards — fine
Publish every 5s: 100 tenants × 3 windows × 2KB ≈ 600 KB / 5s
Merge 128 × 2000 = 256K candidate rows / 5s — easy
Query 5K QPS boards → CDN
```

### Appendix J — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Strongly consistent global top-K? | No — derived, versioned, eventual |
| Estimate read-your-write? | Not required for MVP dashboards |
| Suppress latency | Next publish ≤ interval |

### Appendix K — Pseudocode

```text
def on_event(e):
  if seen(e.event_id): return
  mark_seen(e.event_id)
  k = salt_key(e.tenant, e.key, e.event_id)
  sketch.update(k, e.weight)
  if is_candidate(e.key) or sketch.estimate(e.key) >= promote_threshold:
    exact[e.key] += e.weight
    touch_candidate(e.key)

def publish(tenant, window):
  cands = top_C(exact, C)
  board = merge_policy_hysteresis(cands, K)
  atomic_swap(snapshot[tenant, window], board)
```

### Appendix L — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| Scuba / ODS-like | Debugging / metrics adjacent |
| Kafka / Scribe | Transport |
| TAO-ish caches | Not a fit for open cardinality counts |
| Edge / CDN | Board distribution |

### Appendix M — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Sketches, CDN, salting |
| 100× | Cells, estimate replicas, anomaly hooks |
| 1,000× | Tree merge, edge push, tenant cells |

### Appendix N — Interview whiteboard script (12 steps)

1. Ask: key type, top-K vs φ, windows, approx OK?, freshness.  
2. Write scale table (events/s, cardinality).  
3. Show memory blowup for exact maps.  
4. Propose Kafka → shard agg → merge → board store.  
5. Pick HeavyKeeper/CMS + exact candidates.  
6. Explain why merge top-C not top-K.  
7. Hot-key salting sketch.  
8. Publish interval + hysteresis.  
9. Estimate API path.  
10. Failure: lag, degraded boards.  
11. 10×/100×/1,000×.  
12. Deal-breakers recap.

### Appendix O — Error audit sample plan

```text
daily job:
  sample S keys from boards + random long-tail
  compute exact count from replay window (or dual-write sample)
  measure relative_error = |est - exact| / max(exact,1)
  alert if p95 error > SLO for heavies
```

### Appendix P — Tenant isolation patterns

| Pattern | Pros | Cons |
|---------|------|------|
| Shared cluster, tenant key prefix | Cheap | Noisy neighbor |
| Separate sketch budget per tenant | Fairer | Config complexity |
| Dedicated cell for whales | Strong isolation | Cost |

**MVP:** shared + quotas; migrate whales at 100×.

### Appendix Q — Capacity worksheet

```text
events_per_sec = ______
windows = ______
shards = ______
sketch_bytes = ______
exact_candidates_C = ______
memory ≈ shards × (sketch_bytes × windows + C × 32B × windows) × replication
publish_rows_per_sec ≈ tenants × windows × C / publish_interval
```

### Appendix R — FAQ rapid-fire

| Q | A |
|---|---|
| Redis ZSET? | Only hot set |
| Exact global? | Exact for displayed K |
| Merge sketches for top-K identity? | Not sufficient alone |
| Sliding per event? | Bucketed sliding |
| GDPR delete in CMS? | Prefer TTL windows |

---

*End of Top-K Heavy Hitters system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Change | Why |
|------|--------|-----|
| →10× | Sketches + candidate exact; CDN boards; hot-key salt | Cardinality + skew |
| →100× | Cells; candidate bus; estimate replicas | Blast radius |
| →1,000× | Hierarchical merge; edge board push; tenant cells | Merger & noisy neighbor |

### 8.2 Algorithm card

```text
CMS: point estimates, mergeable, no identity alone
Space-Saving/Misra-Gries: φ-heavies with O(1/ε) counters
HeavyKeeper: better heavy precision under collisions
Exact map: displayed candidates / hot keys
Global top-K: merge top-C candidates — NOT CMS cells
```

### 8.3 Merge correctness card

```text
C ≫ K at leaves; φ-promotion; never truncate to K before global merge
Offline recall audit of true top-K ⊆ ∪ shard top-C
```

### 8.4 Anti-patterns

1. Exact-all keys  
2. CMS-merge as top-K identity  
3. Leaf top-K only  
4. No salting  
5. Live full top-K on GET  
6. No dedup under at-least-once  

