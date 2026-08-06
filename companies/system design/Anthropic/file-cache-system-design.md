# System Design: File Cache

> **Focus areas:** Eviction · Concurrency · Invalidation · Consistency · Backing storage · Stampede control  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split metadata/data/path classes, explicit write-through vs write-back, resolved consistency model  
> **Interview theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — reliability, consistency, concurrency, cost; AI artifacts (model shards, prompt blobs, datasets) change size skew and fan-out, not the fundamentals

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

Goal: **bound the cache**—a distributed file/object cache in front of durable backing storage (S3-like / distributed FS), used by AI infra and general services: model weight shards, tokenizer files, prompt/system blobs, evaluation datasets, and ordinary build artifacts. Fundamentals first; AI context for skew and cost.

### 1.0 What this is / is not

| Dimension | **File cache (this doc)** | Not this |
|-----------|---------------------------|----------|
| Primary job | Accelerate repeated reads; optional write path | Source of truth forever |
| Success | Hit rate, p99 read, coherence under invalidation | Training correctness alone |
| Data | Opaque bytes + metadata (etag, version) | Full POSIX FS semantics MVP |
| Durability | Cache ephemeral; backing durable | Cache as only store (deal-breaker) |

**Scope statement:** Design a **file cache** with eviction, concurrency control, invalidation, consistency options, and clear backing-store integration—framed with AI artifact workloads where useful.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | `Get` / `Put` / `Delete` / `Invalidate` by key (path) | Object API not full POSIX MVP |
| F2 | Backing store? | Durable object store (S3 API) | Cache-aside or write-through |
| F3 | Hit path? | Serve from local SSD/NVMe or peer DRAM/SSD | Tiered cache |
| F4 | Eviction? | Size-bounded; policy configurable | LRU/LFU/Sieve + size awareness |
| F5 | Consistency? | Read-after-write for writer; eventual for others OK MVP | Version/etag; invalidation bus |
| F6 | Concurrency? | Many readers; single writer per key typical | Coalescing; singleflight; leases |
| F7 | Invalidation? | Explicit + TTL; optional version bump | Pub/sub + lazy check |
| F8 | Range reads? | Yes for large model shards | Range GET; partial populate |
| F9 | Pinning? | Pin hot model shards during rollout | Pin set outside eviction |
| F10 | Multi-tenant? | Namespaces / quotas per team | Quota enforcement |
| F11 | Checksums? | Verify on fetch from backing | Corrupt → refetch |
| F12 | Negative cache? | Cache 404 briefly | Stampede on missing keys |

**MVP functional scope:**

1. Get(key): memory → local disk → peer (optional) → backing; populate on miss.  
2. Put(key): write-through to backing + populate (or cache-aside Put to backing + invalidate).  
3. Delete/Invalidate(key): remove local + broadcast invalidation.  
4. Size-aware eviction (Sieve or LRU); pin API for critical artifacts.  
5. Singleflight / request coalescing on miss.  
6. Etag/version on entries; CAS optional on Put.  
7. Metrics: hit ratio, miss latency, eviction, stampede coalesces, corruptions.

**Out of MVP:**

- Full POSIX (locks, mmap coherence cluster-wide)  
- Cross-region strong consistency  
- Erasure-coded cache tier  
- Automatic model-aware prefetch planner (hooks only)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Hit latency | Local SSD | p50 < 1ms meta+small; large sequential disk-bound |
| N2 | Miss latency | Dominated by backing | p99 miss ≈ backing + populate |
| N3 | Hit rate | Workload dependent | ≥80–95% for warm model shards |
| N4 | Durability | Cache loss OK | Backing 11-9s class |
| N5 | Consistency | Tunable | Document model; default: TTL + explicit inval |
| N6 | Availability | Cache down ≠ outage | Bypass to backing |
| N7 | Cost | SSD/$ vs egress | Reduce backing egress & origin load |
| N8 | Correctness | No silent corrupt serve | Checksums |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Warm Get → local hit → return bytes + etag.  
2. Miss → singleflight fetch backing → populate → return.  
3. Put write-through → backing OK → set cache → inval peers.  
4. Invalidate after dataset update → peers drop → next Get refetches.  
5. Pinned model shard survives eviction pressure.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Thundering herd on new model | Singleflight + optional early stampede tokens |
| Stale after Put without inval | Version check / write-through policy |
| Partial write populate | Temp file + atomic rename; never publish half |
| Disk full | Evict aggressively; shed peer fills; bypass |
| Corrupt SSD block | Checksum fail → delete → refetch |
| Backing 503 | Serve stale if policy allows (`stale-if-error`) |
| Huge file > cache | Range cache or bypass (don’t thrash) |
| CAS mismatch | 412; client retry |
| Negative cache poisoning | Short TTL; don’t pin negatives |
| Peer cache serves stale | Generation / inval epoch |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Nodes in cache fleet | 50 | 500 | 5K | 50K |
| Aggregate SSD | 500 TB | 5 PB | 50 PB | 500 PB |
| Get QPS (small meta) | 100K | 1M | 10M | 100M |
| Get GB/s (large) | 50 | 500 | 5K | 50K |
| Distinct keys working set | 10M | 100M | 1B | 10B |
| Median object | 256 KB | mixed | mixed | mixed |
| P99 object (model shard) | 5–20 GB | 20–40 GB | 40+ GB | larger |
| Invalidations/s | 100 | 1K | 10K | 100K |
| Backing egress saved | high | critical | critical | critical |

**What each jump forces:**

- **10×:** Consistent hashing / directories for ownership; peer fetch.  
- **100×:** Hierarchical (L1 node mem, L2 rack SSD, L3 regional); inval fanout trees.  
- **1,000×:** Cell-local caches; global inval approximate; heavy pinning catalogs for models.

### 1.5 Etc. (Constraints & Assumptions)

- Objects are immutable versions preferred (`key@version`); mutable keys need inval.  
- AI workloads: **heavy skew** (few huge hot shards) + long-tail tiny prompts.  
- Prefer **immutable content-addressed** blobs for model artifacts when possible.  
- Cache is performance; **backing remains SoT**.

**Scope statement:**

> Design a distributed file/object cache in front of durable backing storage: size-aware eviction, coalesced concurrent misses, invalidation/TTL consistency, optional write-through and CAS—serving AI artifacts and general files—scaling through tiers and cells without treating the cache as source of truth.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Meta Get** | etag/exists | ~100K/s | ~1M/s | Memory index |
| **Data Get small** | ≤1 MB | tens of K/s | ×10 | SSD |
| **Data Get large** | GB shards | GB/s sequential | ×10 | SSD/NIC |
| **Miss fill** | Backing fetch | << hit QPS | ×10 | Egress $ |
| **Inval messages** | Pub/sub | ~100/s | ~1K/s | Bus |
| **Eviction scans** | Background | continuous | — | CPU/disk |

**Anti-pattern:** one QPS for 100-byte JSON and 10 GB weight files.

### 2.2 Working set & hit rate

```text
Hot model shards: 10 models × 8 shards × 10 GB = 800 GB
Fleet SSD 500 TB → fits easily; hit rate limited by long-tail uniqueness
Prompt blobs: millions × 10–100 KB → metadata + small object cache matters
Dataset files: large sequential; may bypass or range-cache
```

### 2.3 Stampede amplification

```text
Without singleflight: N clients miss same key → N backing GETs
With singleflight: 1 fetch; N waiters
At 10K clients restarting: difference is outage vs blip
```

### 2.4 Invalidation fanout

```text
50 nodes × 100 inval/s = 5K msgs/s trivial
5K nodes × 10K inval/s = 50M msgs/s → need aggregation, bloom epochs, or key ownership
```

### 2.5 Cost sketch

```text
Backing egress $E per GB
Hit rate H, traffic T GB/s → save ≈ H × T × E
SSD fleet cost vs egress: usually cache wins for hot AI shards
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `Get(key, range?)` | Return bytes + etag/version |
| `Put(key, bytes, cas_etag?)` | Write policy dependent |
| `Delete(key)` | Backing delete + inval |
| `Invalidate(key)` | Cache drop only |
| `Pin/Unpin(key)` | Eviction immunity |
| `Stat(key)` | Size, etag, hotness |

### 3.2 Write path options

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| **Cache-aside** | Simple; app writes backing | App must inval | Common |
| **Write-through** | Cache warm; simpler client | Put latency = backing | **MVP default** |
| **Write-back** | Fast Put | Durability risk; complexity | Only with WAL + bounded |
| Write-around | Avoid cache pollution | Cold read after write | Large one-shot writes |

**Deal-breaker:** write-back without durability story for “file store” expectations. For **cache**, prefer write-through or cache-aside.

**Chosen MVP:** immutable keys → Put to backing then populate; mutable keys → write-through + invalidate generation bump.

### 3.3 Eviction policies

| Policy | Pros | Cons | AI fit |
|--------|------|------|--------|
| LRU | Simple | Scan-resistant weak | OK small objects |
| LFU / TinyLFU | Frequency | Complexity; aging | Hot shards |
| **Sieve** | Simple, scan-resistant | Newer | **Good default** |
| Size-aware / GDSF | Fair vs large | Tuning | Mixed sizes |
| Segmented LRU | Probation | More knobs | CDN-like |

**Chosen:** size-aware **Sieve** (or SLRU) + **pin set** for active model versions. Never evict pinned. Optional Two-Q for scan resistance on dataset crawls.

### 3.4 Consistency models

| Model | Guarantee | Cost |
|-------|-----------|------|
| TTL-only | Stale up to TTL | Cheap |
| Explicit inval | Fast drop | Fanout |
| Version check on Get | Lazy coherence | Stat to backing occasional |
| Lease + revoke | Stronger | Coordinator |
| Strong linearizability | Hard | Not MVP for multi-node cache |

**Chosen:** etag/version per object; explicit invalidation bus + short TTL safety net; optional `Get` revalidate if `max_age` exceeded (`stale-while-revalidate` optional).

### 3.5 Concurrency primitives

| Primitive | Role |
|-----------|------|
| Singleflight / waitgroup | One miss fill per key |
| Mutex per key shard | Local index updates |
| CAS etag | Lost-update prevention on Put |
| Lease (optional) | Exclusive populate or write |
| Atomic rename | Publish complete objects only |

### 3.6 Placement / ownership

| Strategy | Pros | Cons |
|----------|------|------|
| Replicated everywhere hot | Simple hits | Waste SSD |
| Consistent hash ownership | Capacity efficient | Hop on miss |
| **Hybrid: local + hashed L2** | Hot local, shared L2 | Complexity |

**Chosen:** L1 on each compute node (local SSD); optional L2 owned by consistent hash for large shards; backing L3.

### 3.7 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| SoT | Backing store | Cache loss OK | Cache-only durable |
| Eviction | Sieve + pins | Scan + hot models | Pure LRU thrash on scans |
| Writes | Write-through / aside | Clear durability | Silent write-back loss |
| Miss storm | Singleflight | Cost/stability | N× origin |
| Large files | Range / bypass | Avoid thrash | Cache whole 40GB×N blindly |
| Consistency | Version + inval | Practical | Pretend linearizable cheaply |

---

## 4. Architecture Diagram

```text
  Train/Infer/Jobs / API workers
           |
           v
  +--------------------+     pin catalog (model rollout)
  | Cache Client Lib   |<-------------------------
  | singleflight, etag |
  +---------+----------+
            |
   +--------+---------+
   | L1 Local Cache   |  mem index + NVMe
   | eviction / pins  |
   +--------+---------+
            | miss
            v
   +--------------------+
   | L2 Peer / Hash Tier|  (optional) large objects
   +----------+---------+
              | miss
              v
   +----------+---------+
   | Backing Object Store|  SoT (S3 API)
   +--------------------+

   Invalidation: publisher → bus (NATS/Kafka/Redis pub) → nodes drop key/epoch
```

**Put write-through:**

```text
Client -> Cache API -> write backing (success) -> write L1 -> publish inval(epoch++) -> ack
```

**Get miss coalesce:**

```text
N waiters -> leader fetches backing -> checksum -> atomic publish -> release waiters
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Never serve corrupt bytes** (checksum fail ⇒ delete + refetch).  
2. **Never publish partial object** (temp + rename / generation).  
3. **Pinned keys not evicted**.  
4. **Bypass available** if cache unhealthy.  
5. **Backing wins** on coherence conflict when revalidate enabled.

#### 5.1.2 Populate safety

```text
fetch -> write tmp -> fsync -> checksum verify -> rename to final -> index publish
crash mid-fetch: tmp GC; index never pointed at incomplete
```

#### 5.1.3 Stampede & thundering herd

- Singleflight per key.  
- Optional probabilistic early expire (`x-expire-jitter`) to desync.  
- Negative caching with short TTL.  
- Soft request hedging only for latency-critical small meta (careful with ×2 load).

#### 5.1.4 Stale-if-error

If backing down and we have etag-fresh-enough entry: serve stale with header `stale=true`. Policy per namespace (models: careful; ephemeral prompts: OK).

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Disk full | Reserved headroom; eviction |
| 10× | Inval loss | TTL safety net |
| 100× | Bus overload | Epoch bloom invalidation |
| 1,000× | Global sync myth | Cell-local coherence |

### 5.2 Scalability

#### 5.2.1 Metadata index

In-memory map key → `{path, size, etag, ref, sieve_state, pin}`. At 10M keys × ~200B ≈ 2 GB/node—OK. At 1B keys → sharded metadata / sparse indexes.

#### 5.2.2 Large object strategy

| Approach | When |
|----------|------|
| Whole-object cache | ≤ few GB; hot |
| Chunk/range cache | Multi-GB shards; partial read |
| Bypass | Cold sequential dataset scan |
| Pin + pre-warm | Rolling model deploy |

#### 5.2.3 Invalidation at scale

| Scale | Mechanism |
|-------|-----------|
| Baseline | Pub/sub per key |
| 10× | Sharded channels |
| 100× | Invalidation epochs + bloom per epoch |
| 1,000× | Cell buses; cross-cell lazy revalidate |

#### 5.2.4 Peer fill (L2)

Consistent hash: owner holds large object. Non-owner miss: get from owner if hot else backing. Avoid all nodes pulling origin for same shard (classic AI deploy storm).

#### 5.2.5 Progressive scale

| Jump | Change |
|------|--------|
| →10× | L2 hash tier; inval shards |
| →100× | Hierarchical tiers; epoch inval |
| →1,000× | Cells; pre-warm service for models; local SoT replicas optional |

#### 5.2.6 Cost controls

- Deduplicate content-addressed blobs (`sha256:...`).  
- Compress warm small prompts if CPU-cheap.  
- Track egress avoided vs SSD $.  
- Quota per tenant to stop cache pollution.

### 5.3 Maintainability

#### 5.3.1 Namespace config

```text
ns:models   ttl=inf, pin_allowed=true, stale_if_error=false, write=immutable
ns:prompts  ttl=1h,  pin_allowed=false, write=through
ns:datasets ttl=1d,  range=true, bypass_scan=true
```

#### 5.3.2 Observability

hit_ratio{ns}, coalesce_count, evict_bytes, pin_count, checksum_fail, inval_lag, backing_qps, p99_get{hit|miss}.

#### 5.3.3 Testing

- Fault inject corrupt bytes.  
- Concurrent Put/Get/Inval linearizability tests on single node.  
- Stampede: 10K parallel Get miss.  
- Eviction: verify pins survive.

#### 5.3.4 Operability

Drain node: stop fills; redirect; empty optional. Pre-warm API for model rolls. Chaos: kill inval bus—assert TTL bounds staleness.

---

## 6. Wrap-Up

### 6.1 What we designed

A **file cache** with tiered storage, size-aware eviction (Sieve + pins), singleflight miss coalescing, write-through/cache-aside paths, etag/version invalidation, and backing-store as SoT—applied to AI artifacts without inventing a new consistency fantasy.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| LRU vs Sieve/LFU | Prefer scan-resistant + pins for models |
| Write-back | Avoid unless WAL |
| Strong consistency | Expensive; version+inval enough MVP |
| Huge files | Range/pin/bypass — don’t thrash |
| Stampede | Singleflight mandatory |

### 6.3 Closing line

> “It’s a classic multi-tier cache with leases and invalidation—the AI twist is object size skew and deploy-time fan-out, which makes pinning, singleflight, and peer fill dollars-and-outage critical.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Eviction

**Q1: LRU vs LFU?**  
A: LRU simple but fails under scans; LFU needs aging; Sieve/SLRU often better defaults.

**Q2: How do you handle mixed sizes?**  
A: Charge eviction by bytes; avoid one 20GB object nuking thousands of small hot keys unfairly—use ranked score size×recency or separate slabs.

**Q3: What is pinning?**  
A: Explicit immunity from eviction for active model versions; unpin on rollback.

**Q4: Scan resistance?**  
A: Dataset iteration shouldn’t evict model shards—probation segment or Sieve.

**Q5: TinyLFU?**  
A: Admission filter using approximate frequencies; good at high QPS small objects.

### 7.2 Concurrency

**Q6: Singleflight?**  
A: Collapse concurrent misses into one fill; waiters share result.

**Q7: Per-key mutex deadlock?**  
A: Shard locks; never lock key A then B in arbitrary order without ordering rule.

**Q8: CAS?**  
A: Put with `If-Match: etag`; prevents lost updates on mutable keys.

**Q9: Leases?**  
A: Exclusive right to populate/write for TTL; prevents duplicate fills under partition (with fencing).

**Q10: Readers during eviction?**  
A: Refcount or generation; don’t delete underlying blob until refs zero.

### 7.3 Invalidation & consistency

**Q11: TTL vs push inval?**  
A: TTL bounds; push speeds coherence. Use both.

**Q12: Lost invalidation?**  
A: TTL safety; periodic revalidate for critical ns; epoch numbers.

**Q13: Read-your-writes?**  
A: Writer updates local L1 before ack; or client sticky to writer node.

**Q14: Immutable content-addressed?**  
A: Best for models—`sha256` keys never inval; new version new key.

**Q15: stale-while-revalidate?**  
A: Serve stale, refresh async; good for prompts; careful for safety-critical configs.

### 7.4 Write policies

**Q16: Why write-through?**  
A: Durability clear; cache warm; Put slower.

**Q17: When write-back?**  
A: Bursty writes with WAL to SSD + flush; risk on node death—usually wrong for “files.”

**Q18: Write-around?**  
A: Large ETL output won’t be reread soon—skip cache pollution.

### 7.5 Backing storage

**Q19: What if backing is strongly consistent?**  
A: Cache still needs inval; backing consistency ≠ cache coherence.

**Q20: Multipart / range?**  
A: Align chunks; cache per chunk key `key#part`.

**Q21: Checksums?**  
A: Store crc/sha in metadata; verify on fill and optionally on read sample.

### 7.6 AI infra specifics

**Q22: Model roll storm?**  
A: Pre-warm + pin + peer fill; rate-limit origin.

**Q23: Tokenizer/prompt blobs?**  
A: Tiny, ultra-hot—memory L0 cache in process + L1.

**Q24: Dataset training reads?**  
A: Sequential, poor hit rate—bypass or specialized data loader cache.

**Q25: Multi-region training?**  
A: Regional caches; cross-region miss expensive; replicate hot snapshots.

### 7.7 Scalability

**Q26: 100M QPS meta?**  
A: Client-side cache; sharded meta; RPC batching.

**Q27: 50 PB SSD?**  
A: Cells; hierarchical namespaces; cold tier HDD optional.

**Q28: Inval at 100K/s?**  
A: Bloom epochs; don’t send per-key to all nodes.

### 7.8 Failure & ops

**Q29: SSD dies?**  
A: Mark node degraded; bypass; rebuild empty; no data loss (SoT backing).

**Q30: How to debug stale?**  
A: etag timeline; inval lag metrics; client-seen version.

**Q31: Poison entry?**  
A: Checksum + admin purge API + version bump.

### 7.9 Alternatives & deal-breakers

**Q32: Just use CDN?**  
A: Great for public/geo; less ideal for private multi-GB training shards & custom pin.

**Q33: OS page cache only?**  
A: No cluster coherence, no pin API, no metrics—insufficient alone.

**Q34: Redis for file bytes?**  
A: DRAM $; size limits; OK for small prompts not model shards.

### 7.10 Interview craft

**Q35: How to open?**  
A: Clarify SoT, consistency, object size mix, write path—then split load classes.

**Q36: What numbers matter?**  
A: Working set vs SSD, hit rate, miss egress $, stampede factor, inval fanout.

---

### Appendix A — Eviction sketch (Sieve-like)

```text
on access: mark visited
on evict need:
  hand moves around queue
  if visited: clear visited; skip
  else if not pinned: evict
```

### Appendix B — Singleflight

```text
Get(key):
  if hit: return
  dups = group.Do(key, fill)
  return dups.result
fill:
  bytes = backing.Get(key)
  verify
  publish atomic
  return bytes
```

### Appendix C — Progressive scale table

| Scale | L1 | L2 | Inval | Pins |
|-------|----|----|-------|------|
| Baseline | Local NVMe | — | Pub/sub | Manual |
| 10× | Local | Hash peer | Sharded | Pre-warm |
| 100× | Mem+SSD | Rack | Epoch bloom | Catalog service |
| 1,000× | Cell | Regional | Cell bus | Global pin DB read-mostly |

### Appendix D — Metrics

| Metric | Why |
|--------|-----|
| hit_ratio | Effectiveness |
| origin_qps | Stampede / miss |
| coalesce_factor | Singleflight health |
| evicted_bytes | Pressure |
| stale_serve | Coherence trade |
| checksum_fail | Integrity |
| pin_bytes | Capacity planning |

### Appendix E — NFR card

```text
Hit p50 small < 1ms
Miss dominated by backing
No silent corruption
Bypass if cache down
Pinned models survive eviction
Inval + TTL bound staleness
```

### Appendix F — Worked numbers

```text
Hot set 800 GB model shards
50 nodes × 10 TB = 500 TB >> hot set
Deploy 10K GPU workers × miss without coalesce = 10K × 10 GB origin = disaster
With peer L2 + singleflight: ~replica_count fills
Invalidation 100/s × 50 nodes = 5K/s messages OK
```

### Appendix G — Consistency cheatsheet

| Pattern | Stale window |
|---------|--------------|
| TTL 5 min | ≤5 min |
| Push inval | RTT + process |
| Immutable keys | 0 (new key) |
| Version check each Get | ~0 after Stat |

### Appendix H — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just LRU” | Scans + size skew |
| “Redis” | Too small/$$$ for shards |
| “Strong consistency everywhere” | Cost; use immutable + inval |
| “Cache is durable” | No—backing is |

### Appendix I — Related systems

| System | Relation |
|--------|----------|
| File store | May be backing or sibling |
| Model registry | Emits pin/pre-warm |
| CDN | Edge cousin |
| FS (Lustre/GPFS) | Different POSIX goals |

### Appendix J — Non-goals

- POSIX flock across cluster  
- Exactly-once write-back  
- Global linearizability at 100M QPS  
- Training data loader feature completeness  

### Appendix K — Mutable vs immutable policy

```text
Immutable (recommended for weights):
  Put(sha) once; Get(sha); never overwrite

Mutable (prompts drafts):
  Put(key) version++; inval; CAS optional
```

### Appendix L — Client library responsibilities

- Local process LRU (L0)  
- Singleflight  
- Hedged retries careful  
- Pass etag / prefer immutable URLs  
- Metrics propagation  

### Appendix M — 30s scale narrative

> Baseline: local NVMe + write-through + singleflight. 10× adds hashed L2 so model deploys don’t melt origin. 100× needs epoch invalidation and namespaces. 1,000× is cell-local caches with catalogs for pins—coherence is mostly immutable keys, not global locks.

### Appendix N — Pseudocode Put CAS

```text
Put(key, bytes, prev_etag):
  backing.PutIfMatch(key, bytes, prev_etag) or fail 412
  local.publish(key, bytes, new_etag)
  bus.invalidate(key, new_etag)
  return new_etag
```

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Singleflight | Coalesce in-flight work by key |
| Pin | Non-evictable residency |
| Epoch inval | Versioned generation for bulk drop |
| Write-through | Persist origin before/with cache update |
| Sieve | Eviction algorithm with visited bit |

### Appendix P — LRU vs LFU vs Sieve comparison (interview table)

| Property | LRU | LFU / TinyLFU | Sieve |
|----------|-----|---------------|-------|
| Implementation | Easy | Moderate | Easy |
| Scan resistance | Weak | Stronger | Stronger |
| Aging / decay | Implicit | Needs explicit | Visited bit |
| Large-object fairness | Needs size awareness | Same | Same |
| Production use | Ubiquitous | Caffeine-like | Emerging default |

**Interview pick:** size-aware Sieve or SLRU + pin set for model namespaces; TinyLFU admission for small-object namespaces (prompts).

### Appendix Q — Stampede scenarios & mitigations

| Scenario | Without mitigation | With mitigation |
|----------|--------------------|-----------------|
| New model deploy, 10K workers | 10K origin GETs | Singleflight + L2 peer + pre-warm |
| TTL aligned expiry | Synchronized miss | Jittered TTL / early expire |
| Negative key hot-miss | Origin hammer | Short negative cache |
| Backing blip | Retry storm | stale-if-error + Retry-After |

### Appendix R — Consistency worked examples

**Example 1 — Immutable weights**

```text
Put(sha256=abc) once to backing
All caches Get(sha256=abc)
No invalidation ever for that key
New model = new sha
```

**Example 2 — Mutable prompt template**

```text
Writer Put(key=prompt/x) etag=1 -> etag=2, write-through
Publish inval(key, etag=2)
Peer with etag=1 drops on inval (or TTL)
Writer always sees etag=2 from local L1 (read-your-write)
```

**Example 3 — Lost inval**

```text
Peer misses inval message
TTL 5 min bounds staleness
Critical ns: Get revalidate if age > 30s (Stat backing)
```

### Appendix S — Capacity planning worksheet

```text
Inputs:
  hot_set_bytes (models + prompts)
  replica_factor (how many nodes should hold hot set)
  growth_margin (e.g. 2×)
SSD_needed ≈ hot_set_bytes × replica_factor × growth_margin

Example:
  hot_set 2 TB, replica 3, margin 2 → 12 TB fleet minimum usable
  Provision 50–100 TB for long tail + spikes
```

### Appendix T — API error catalog

| Code | When |
|------|------|
| 404 | Missing backing (after negative TTL) |
| 412 | CAS mismatch |
| 413 | Object too large for cache path (bypass required) |
| 507 | Disk full / quota |
| 503 | Cache degraded; client may bypass |
| 560 (custom) | Checksum failure after retries |

### Appendix U — Deep dive: leases for exclusive populate

```text
Miss path:
  try AcquireLease(key, ttl=30s, owner=node_id)
  if won: fill from backing; Publish; Release
  if lost: Wait(key) or Get from lease owner peer
Partition risk: fencing token on lease; backing etag wins
```

Use leases when singleflight is multi-process (not only in-proc).

### Appendix V — What AI infra changes (and what it doesn’t)

| Changes | Doesn’t change |
|---------|----------------|
| Object size skew (GB shards) | Need for SoT backing |
| Deploy fan-out storms | Checksums / atomic publish |
| Pin catalogs for rollouts | Invalidation + TTL fundamentals |
| Egress $ sensitivity | Concurrency / stampede control |

---

*End of File Cache system design.*
