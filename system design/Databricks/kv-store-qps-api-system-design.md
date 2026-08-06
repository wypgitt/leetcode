# System Design: KV Store with QPS API

> **Focus areas:** KV ops · Per-key QPS metrics · Sliding window · Sharding · Metrics aggregation · Hot keys · Linearizable per shard
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct shard math, explicit split between strong KV and eventual metrics, honest MVP vs extreme-scale paths, failure-first reasoning
> **Interview theme:** Databricks — distributed KV service with get/put/delete plus per-key QPS metrics API (HLD service view; companion LLD for single-node sliding window)

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

Goal: design a **distributed KV store** exposing `get` / `put` / `delete` on keys, plus a **QPS metrics API** that reports per-key request rates over configurable sliding windows. This is the **HLD service view**—how to shard, aggregate, and serve metrics at scale. The interviewer may pivot to the **single-node sliding-window implementation** in `kv-sliding-window-qps-lld-system-design.md`.

### 1.0 What this is / is not

| Dimension | This doc (HLD) | Not this |
|-----------|----------------|----------|
| Primary job | Distributed KV + per-key QPS reporting | Global rate limiter / billing meter |
| KV consistency | **Linearizable per shard** (per key home) | Cross-shard transactions |
| Metrics consistency | **Eventually consistent** (few-second lag OK) | Billing-grade exact counts |
| Window model | Sliding (1s, 1m, 5m) | Fixed calendar minute only |
| Counted ops | get, put (delete optional/configurable) | All HTTP traffic globally |
| Scale path | Sharded storage + stream rollup | Single in-memory node |
| Databricks lens | Hot-key detection, throttle hooks, storage service | Full observability SaaS |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | KV operations? | get, put, delete by string key | Standard map semantics; delete removes key |
| F2 | Value type? | Opaque bytes MVP; TTL optional Phase 2 | No schema enforcement in MVP |
| F3 | QPS API? | `GET /metrics/qps?key=&window=` returns ops/sec for that key | Dedicated metrics read path |
| F4 | Which ops count toward QPS? | get + put (delete usually excluded) | Configurable `OpKind` bitmask per tenant |
| F5 | Window sizes? | 1s, 1m (60s), 5m sliding | Multi-resolution rollup tables |
| F6 | QPS definition? | `count(events in window) / window_seconds` | Double ops/sec; document rounding |
| F7 | Missing key QPS? | Return 0.0 (no counter allocated) | Lazy counter creation on first counted op |
| F8 | Sharding? | Hash(key) → home shard | Single writer per key |
| F9 | Consistency for KV? | Linearizable reads/writes **within shard** | Raft or primary-backup per shard |
| F10 | Consistency for metrics? | Eventual; 1–5s lag acceptable | Separate pipeline; no blocking KV on metrics |
| F11 | Idempotency? | PUT/DELETE with client idempotency key | Dedupe table per shard |
| F12 | Auth / multi-tenant? | API keys; per-tenant key namespaces | AuthZ on every call; quota isolation |
| F13 | Admin? | List hot keys, shard map, lag dashboards | Ops APIs |
| F14 | Rate limiting? | Optional: throttle keys exceeding QPS threshold | Consumer of metrics; not MVP core |

**MVP functional scope (lock with interviewer):**

1. `GET /v1/kv/{key}` — read value; 404 if absent.  
2. `PUT /v1/kv/{key}` — upsert bytes; optional `Idempotency-Key` header.  
3. `DELETE /v1/kv/{key}` — remove key; idempotent (204 even if absent).  
4. `GET /v1/metrics/qps?key={key}&window={1s|60s|300s}` — per-key sliding-window QPS.  
5. Shard by `hash(key)`; home shard owns all KV mutations for that key.  
6. Each shard records local op events; stream aggregator rolls up to queryable store.  
7. Auth + per-tenant quotas on KV path.  
8. Observability: RED metrics, metrics pipeline lag, hot-key alerts.

**Out of MVP (explicitly defer):**

- Cross-shard multi-key transactions  
- Global active-active writes on the same hot key  
- Billing-grade exact QPS (requires stronger metrics path)  
- Automatic shard split/merge (manual rebalancing at 10×)  
- Global aggregate QPS across all keys (expensive; HLL approximate Phase 2)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | KV read latency | Interactive | p99 < 10–20ms in-region (excluding cross-region) |
| N2 | KV write latency | Durable ACK | p99 < 30–50ms with RF=3 sync replicate |
| N3 | Metrics read latency | Observability | p99 < 50–100ms; stale label if lag > SLO |
| N4 | KV availability | Critical | 99.9% MVP; 99.99% at scale |
| N5 | Metrics availability | Best-effort | Degrade to shard-local estimate; never block KV |
| N6 | Throughput | See scale table | Horizontal shard scale |
| N7 | Durability (KV) | No silent loss after ACK | RPO=0 for acknowledged writes |
| N8 | Metrics accuracy | Approximate at scale | ±1s bucket error; exact on owning shard for hot keys |
| N9 | Multi-region | Single region MVP | Home cell per key namespace at 100× |
| N10 | Cost | Efficient at scale | Tiered metrics storage; pre-aggregate |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client PUT key `foo` → home shard durable write → ACK → metrics event emitted async → QPS visible within few seconds.  
2. Client GET key `foo` → linearizable read from shard leader → value returned; GET counted in QPS pipeline.  
3. Client DELETE key `foo` → key removed; QPS counter for `foo` may linger until idle TTL evicts metrics state.  
4. Client GET `/metrics/qps?key=foo&window=60s` → coordinator merges shard rollups → returns `{ qps, samples, as_of_ts }`.  
5. Retry PUT with same idempotency key → same response; no double effect.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Hot key (100k ops/s on one key) | Shard vertical scale + read replicas; coalesce metrics increments locally; optional key split namespace |
| Metrics lag spike | Return `as_of_ts` + `staleness_ms`; optional approximate mode; never slow KV path |
| Shard leader loss | Failover replica; brief unavailability; epoch fencing prevents split brain |
| Duplicate client retry | Idempotency returns first result |
| GET on missing key | 404; still counts toward QPS if configured |
| Clock skew across shards | Metrics use event ingest time at aggregator, not client time |
| Metrics query on cold key | 0.0 QPS; no cross-shard scan |
| Cross-shard metrics fan-out | Key maps to one home shard → single-shard metrics source of truth |
| Stream consumer lag | Backpressure metrics queries; scale consumers; alert |
| DELETE then immediate GET QPS | QPS may still reflect recent gets until window expires |

### 1.4 Progressive scale

| Metric | Baseline (1×) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Peak KV QPS | 50K | 500K | 5M | 50M |
| Unique keys (active/day) | 10M | 100M | 1B | 10B |
| Metrics events/s (get+put) | ~50K | 500K | 5M | 50M |
| Shards | 32 | 256 | 2K | 20K+ |
| Metrics rollup cardinality | 10M keys | 100M | 1B (sampled) | Tiered + sketches |
| Regions | 1 | 2 (DR) | 3 (home cells) | 5+ |
| p99 KV latency target | 20ms | 15ms | 10ms | 10ms + cell routing |
| Metrics lag SLO | 5s | 3s | 2s | 1s (regional) |

**What each jump forces:**

- **10×:** Horizontal shard expansion; dedicated metrics stream cluster; pre-aggregate per shard; bulkheads between KV and metrics paths.  
- **100×:** Async metrics only (never sync on request path); tiered rollup storage (1s hot, 1m warm); hot-key detection service; optional cells.  
- **1,000×:** Cell architecture; count-min sketch for cold keys; exact counters only for hot keys; federated metrics query; admission control on metrics API.

### 1.5 Scope repeat-back

> Design a **sharded KV store** with **linearizable get/put/delete per key** on the home shard, plus a **per-key sliding-window QPS metrics API** fed by a **local counters → stream → rollup** pipeline. Metrics are **eventually consistent** with explicit staleness semantics; KV is **strong per shard**. Scale from ~50K QPS through 10×/100×/1,000×. Hand off single-node sliding-window mechanics to the companion LLD.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic & concurrency

```text
Baseline peak KV QPS ≈ 50K (mix ~70% get, ~25% put, ~5% delete)
Counted for QPS metrics: get + put ≈ 95% × 50K ≈ 47.5K events/s

p99 KV service time ≈ 15ms (in-region, leader read/write)
Concurrency ≈ peak_qps × p99_latency_s ≈ 50,000 × 0.015 ≈ 750 in-flight requests
API tier: ~50 stateless nodes @ 1K RPS each with headroom
```

At **10×** (500K QPS): ~7,500 concurrent, 256 shards (~2K QPS/shard), metrics stream ~475K events/s. At **100×** (5M QPS): 2K shards, coalesce on shard before emit; top-K exact + CMS for tail keys.

### 2.2 Shard math

```text
Given:
  peak_qps = P
  target_qps_per_shard = T  (e.g. 2,000–5,000 for comfortable headroom)
  replication_factor = RF = 3

shard_count N = ceil(P / T)

Baseline: N = ceil(50,000 / 2,500) = 20 → round to 32 (power-of-two for consistent hash)
10×: N = ceil(500,000 / 2,500) = 200 → 256
100×: N = ceil(5,000,000 / 2,500) = 2,000

Per-shard storage (rough):
  active_keys_per_shard = total_active_keys / N
  avg_value_size = 1 KB (interview assumption unless specified)
  10M keys / 32 shards ≈ 312K keys/shard × 1 KB ≈ 300 MB data + indexes + WAL

Per-shard write bandwidth:
  writes_per_shard ≈ (put_rate / N) × avg_value_size
  12.5K put/s / 32 × 1 KB ≈ 400 MB/s cluster-wide puts → ~12 MB/s/shard (manageable)

Home shard for key k:
  shard_id = consistent_hash(k) mod N
  route via gateway directory (cached shard map, versioned)
```

**Virtual nodes:** use 100–200 vnodes per physical shard for even distribution when N is small.

### 2.3 Metrics pipeline bandwidth

```text
Event record (compact): { key_hash, key?, op, ts_ms, shard_id } ≈ 40–80 B

Baseline: 47.5K events/s × 64 B ≈ 3 MB/s ingress to stream
10×: 475K × 64 B ≈ 30 MB/s
100×: 4.75M × 64 B ≈ 300 MB/s — coalesce on shard to 1s buckets before emit:
       effective 100× reduction → ~3 MB/s rollups + hot-key side channel

Local coalescing (per shard, per second):
  Instead of 50K individual events/s/shard, emit 1 rollup msg/s/key with activity
  Worst case hot key: still 1 msg/s for that key from shard agent
```

### 2.4 Metrics storage

```text
Per-key rollup (exact, 1s resolution, 5m retention):
  5 windows × 8 B counter ≈ 40 B/key hot tier

Hot keys tracked exactly: top 10K per shard → 320K keys cluster @ 32 shards
  320K × 40 B ≈ 13 MB (trivial)

100× with 1B keys: cannot store all exact — CMS + periodic snapshot of top-K
  CMS: ~1–4 KB per sketch × shards; plus exact map for keys > threshold QPS
```

### 2.5 Latency budget — KV path (say aloud)

```text
GET /v1/kv/{key}  (p99 target 20ms)
  Gateway authZ + routing     2ms
  Shard leader read           5ms
  Optional: linearizable      +5ms (quorum read if required)
  Response serialize          1ms
  Headroom                    7ms

PUT /v1/kv/{key}  (p99 target 50ms)
  Gateway                     2ms
  Idempotency check (local)   3ms
  Leader WAL append           8ms
  Replicate to RF-1 followers 15ms
  Apply to storage engine     5ms
  ACK + async metrics hook    2ms (hook must not block)
  Headroom                    15ms
```

### 2.6 Latency budget — metrics path

```text
GET /v1/metrics/qps?key=foo&window=60s  (p99 target 100ms)
  Gateway + authZ               3ms
  Resolve home shard            1ms (cached)
  Query rollup store (regional) 10–30ms
  If cross-shard (shouldn't):   N × shard queries — avoid
  Merge + compute qps           2ms
  Headroom                      64ms

Staleness: as_of_ts = last rollup watermark; typical lag 1–5s baseline
```

### 2.7 Bottlenecks (ranked)

1. **Hot key on single shard** — serializes KV and inflates local metrics coalescer.  
2. **Metrics stream consumer lag** — unbounded lag → stale QPS; scale consumers + coalesce.  
3. **Shard leader CPU** — linearizable replication + storage engine on same node.  
4. **Metrics query on viral key** — everyone queries same QPS; cache at coordinator.  
5. **Cross-shard operations** — avoid; multi-key not in MVP.  
6. **Idempotency store growth** — TTL eviction required.

### 2.8 Cost / frugality

- Metrics must never be on the synchronous KV critical path (no double-write blocking).  
- Coalesce before stream at 10×+; raw per-op events only at small scale or for debug.  
- Exact per-key state only for hot keys; CMS/sketch for long tail at 100×.  
- Tier rollup retention: 1s buckets for 1h, 1m buckets for 7d.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency | Latency |
|-------|----------------|-------------|---------|
| **KV data plane** | get/put/delete values | **Linearizable per shard** | ms |
| **Metrics observation plane** | Count ops, sliding windows, QPS API | **Eventually consistent** | seconds lag OK |
| **Control plane** | Shard map, leader election, config | Strong / consensus | rare updates |
| **Idempotency plane** | Dedupe client retries | Per-shard strong | tied to KV |

**Deal-breaker:** requiring metrics to be linearizable with every KV op (would 2× write latency and couple failure domains).

**Interview signal:** say early — "KV truth is strong per shard; QPS is observability with bounded staleness."

### 3.2 Core abstractions

```text
Key            opaque string; tenant prefix optional
Value          byte[]
Shard          owns key range via consistent hash
ShardLeader    single writer for linearizable ops on shard
KVRecord       { key, value, version, updated_at }
OpEvent        { tenant, key, op_kind, ts_ingest, shard_id }
SlidingRollup  per (key, window) bucket counters — see LLD bucket model
MetricsView    { key, window, qps, op_count, as_of_ts, staleness_ms }
IdempotencyRecord { client_key, response_hash, expires_at }
```

### 3.3 Options & trade-offs — storage engine

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| Redis Cluster | Fast, familiar | Memory cost; persistence tuning | Durability RPO=0 strict |
| Raft + RocksDB per shard | Linearizable, durable | Ops complexity | MVP time-boxed |
| Dynamo-style (leader + async repl) | Proven at scale | Tunable consistency confusion | Need strict linearizable |

**Chosen MVP:** Raft group per shard + RocksDB. At 10×, managed Dynamo/Cassandra with LWT if interviewer accepts.

### 3.4 Options & trade-offs — metrics aggregation

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| Sync increment on KV path | Simplest mentally | Adds latency; failure coupling | Any production scale |
| Async local counter → periodic flush | Fast KV | Lost counts on crash | Billing |
| **Async local counter → stream → rollup** | Decoupled; durable stream | Seconds lag | Need instant QPS |

**Chosen:** local counters on shard leader → coalesced stream → rollup workers → query store.

### 3.5 Options & trade-offs — sliding window at scale

| Option | Pros | Cons | When |
|--------|------|------|------|
| Timestamp ring per key (LLD) | Exact within cap | Memory per key | Single node / hot keys |
| 1s bucket counters (LLD default) | O(60) per key | ±1s boundary | Shard-local agent |
| Stream-time tumbling + sliding query | Centralized | Query cost | Flink/Kafka Streams at 100× |
| Count-min sketch | Fixed memory | Approximate | Cold key tail |

**Chosen:** **1s buckets on shard agent** (matches LLD); rollup service merges cross-shard isn't needed because key has single home shard. Regional aggregator holds materialized views for query.

### 3.6 Consistency model (explicit)

```text
KV operations (get/put/delete):
  Linearizable within home shard for a given key.
  Implementation: Raft leader serializes all mutations; reads from leader or quorum-read if required.
  Cross-shard: no guarantees (not in scope).

Metrics (QPS):
  Eventually consistent with typical lag 1–5s.
  An op counted at time T appears in QPS API after ingest + rollup watermark ≥ T.
  DELETE does not rewind historical counts in the window (counts reflect ops that occurred).
  Missing key → qps = 0.0 (no state).

Client-visible contract:
  GET /kv/{key} after successful PUT returns new value (read-your-writes if sticky to leader/session).
  GET /metrics/qps may return data up to staleness_ms behind real time; response includes as_of_ts.
```

### 3.7 API shape

```text
# KV
GET    /v1/kv/{key}                    → 200 { value, version } | 404
PUT    /v1/kv/{key}                    → 200 { version }
       Headers: Idempotency-Key (optional), Content-Type: application/octet-stream
DELETE /v1/kv/{key}                    → 204
HEAD   /v1/kv/{key}                    → 200 metadata only (optional)

# Metrics
GET    /v1/metrics/qps?key={key}&window={1s|60s|300s}&op_mask={get,put}
       → 200 {
            key, window_sec, qps, op_count,
            as_of_ts, staleness_ms,
            precision: "exact"|"approximate",
            shard_id
          }

# Admin (Phase 2)
GET    /v1/admin/hot-keys?limit=100&window=60s
GET    /v1/admin/shards
GET    /v1/health
```

**GET /metrics/qps semantics:**

- `qps = op_count_in_window / window_sec` (double).  
- `op_count` = raw count of get+put (per `op_mask`) with timestamps in `(now - window, now]` per rollup watermark.  
- `as_of_ts` = last aggregated bucket boundary (ISO8601).  
- `staleness_ms = now - as_of_ts` (approximate pipeline lag).  
- `precision=exact` when served from shard-local bucket counters; `approximate` when from CMS/sketch tier.  
- Stronger guarantee: **monotonic non-increasing op_count** only after buckets age out of window (prune), not between consecutive queries during lag.

### 3.8 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| KV consistency | Linearizable per shard | Correctness for state | Eventual KV everywhere |
| Metrics consistency | Eventual + staleness header | Decouple from KV latency | Blocking KV on metrics ACK |
| Sharding | Consistent hash, single home | Simple routing | Range shards without split |
| Hot keys | Replicas + cache + metrics coalesce | Protect shard leader | Ignore hot key |
| Idempotency | Per-shard store with TTL | Safe retries | None for mutations |
| Window impl | 1s buckets (LLD aligned) | Memory bounded | Unbounded timestamp lists at scale |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                    ┌─────────────────────────────────────────────┐
                    │              Clients / SDKs                 │
                    └───────────────┬─────────────────────────────┘
                                    │ HTTPS/gRPC
                                    v
                    ┌─────────────────────────────────────────────┐
                    │  API Gateway (authZ, rate limit, routing)   │
                    └───────┬─────────────────────┬─────────────────┘
                            │                     │
              KV path       │                     │  Metrics path
                            v                     v
              ┌─────────────────────┐   ┌─────────────────────┐
              │  KV Router          │   │  Metrics Coordinator │
              │  (shard map cache)  │   │  (cache hot QPS)     │
              └─────────┬───────────┘   └──────────┬──────────┘
                        │                          │
         ┌──────────────┼──────────────┐           │
         v              v              v           v
    ┌─────────┐   ┌─────────┐   ┌─────────┐  ┌──────────────┐
    │ Shard 0 │   │ Shard 1 │   │ Shard N │  │ Rollup Store │
    │ Raft    │   │ Raft    │   │ Raft    │  │ (TSDB/KV)    │
    │ + LSM   │   │ + LSM   │   │ + LSM   │  └──────▲───────┘
    │ + local │   │ + local │   │ + local │         │
    │ metrics │   │ metrics │   │ metrics │         │
    └────┬────┘   └────┬────┘   └────┬────┘         │
         │             │             │              │
         └─────────────┴─────────────┴──────────────┘
                              │
                              v
                    ┌─────────────────────┐
                    │  Metrics Stream     │
                    │  (Kafka/Pulsar)     │
                    └──────────┬──────────┘
                               v
                    ┌─────────────────────┐
                    │  Rollup Workers     │
                    │  (sliding windows)  │
                    └─────────────────────┘
```

### 4.2 Sequence: PUT with async metrics

```text
Client          Gateway       Shard Leader       Followers      Metrics Agent    Stream
  |--PUT foo---->|              |                  |                |              |
  |              |--route------>|                  |                |              |
  |              |              |--WAL append----->|                |              |
  |              |              |--replicate------>|--ack---------->|              |
  |              |              |--apply KV       |                |              |
  |              |              |--recordOp(local)|                |              |
  |<--200 OK-----|<-------------|                  |                |              |
  |              |              |--async flush------------------->|              |
  |              |              |                  |                |--batch emit->|
  |              |              |                  |                |              |
  |--GET qps---->|              |                  |                |              |
  |              |--coordinator query rollup store (may lag 1-5s)                   |
  |<--{qps, as_of_ts}----------------------------------------------------------------|
```

**Critical:** `recordOp` is **in-memory on leader** after KV apply; stream emit is **async**. Crash between apply and emit loses at most coalesce window (1s) of metrics — acceptable for observability, not for billing.

### 4.3 Sequence: GET (linearizable read)

```text
Client       Gateway      Shard Leader
  |--GET foo->|
  |           |--route---->|
  |           |           |--linearizable read (leader or quorum)
  |           |           |--recordOp(GET) local metrics
  |<--200------|<----------|
```

Optional: follower reads with `read_consistency=eventual` for lower latency if interviewer allows; default MVP is leader read for linearizability.

### 4.4 Sequence: metrics query path

```text
Client       Gateway    Metrics Coord    Rollup Store    (optional Shard Agent)
  |--qps?key=foo&window=60s-->|
  |           |--authZ-->|
  |           |           |--resolve home shard for foo
  |           |           |--query (shard_id, key, window)
  |           |           |<--{ buckets, watermark }
  |           |           |--compute qps = sum/count / 60
  |<--200 { qps, as_of_ts, staleness_ms }--|
```

For **hot keys**, coordinator caches response 500ms–1s to prevent metrics API becoming its own hot spot.

### 4.5 Hot key response (graduated)

Read replicas → near-leader cache → metrics coalesce (1 event/s/key) → app-level key split → dedicated hot-shard migration → write rate limit. See §5.9.

---

## 5. Design Deep Dive

### 5.1 Reliability — KV invariants

1. **Single home shard** per key at any epoch; routing table versioned.  
2. **Linearizable ordering** of all mutations to a key via Raft leader serialization.  
3. **ACK only after durable** — WAL fsync + RF-1 ack (or quorum).  
4. **Idempotent mutations** — same `Idempotency-Key` → same effect and response.  
5. **Delete is idempotent** — deleting absent key succeeds.  
6. **Metrics never block KV ACK** — async hook with bounded memory coalescer.  
7. **Leader epoch fencing** — stale leaders cannot commit after partition heals.

### 5.2 Reliability — metrics invariants

1. **At-least-once** delivery on stream; rollup workers idempotent by `(shard, key, bucket_ts)`.  
2. **Monotonic bucket counts** within a bucket second until window prune evicts.  
3. **`as_of_ts` never claims fresher than watermark** — honest staleness.  
4. **Home shard authoritative** for key metrics — no cross-shard merge for single-key QPS.  
5. **Crash loss bounded** — at most 1 coalesce interval of metrics events (configurable).

### 5.3 Sharding deep dive

```text
Routing:
  shard_id = jump_consistent_hash(key, num_shards)
  Gateway caches shard map { shard_id → { leaders[], replicas[] } } version=V
  On shard migration: dual-route during handoff; keys versioned

Replication:
  RF=3 per shard across AZs
  Leader handles all writes + linearizable reads
  Followers: catch-up replay; promote on leader failure (Raft election ~1–3s)

Rebalancing (10×+):
  Add shards: consistent hash minimizes movement (~1/N keys move)
  Migrate key range: copy snapshot + replay WAL delta + cutover epoch

Shard count formula (repeat for interview):
  N = ceil(peak_qps / target_per_shard_qps)
  target_per_shard_qps = 2K–5K typical; lower if large values or hard durability
```

**Virtual nodes:** 128 vnodes/shard → even load when N=32; monitor shard size variance σ < 10%.

### 5.4 Linearizable per shard — how

```text
Raft group per shard:
  Client PUT → leader appends to log → replicate → commit → apply to RocksDB
  Client GET (linearizable) → leader read after commit index OR ReadIndex quorum

Why per-shard not global:
  Global serializability requires cross-shard 2PC — latency + availability cost
  Key-value workloads: 99.9% ops single-key

Read-your-writes:
  Sticky session to leader OR read from leader always MVP
  Token in response: { leader_id, commit_index } for follower redirect

Comparison to Dynamo:
  Dynamo: eventual default; LWT for conditional single-key
  This design: default linearizable on home shard — stronger, simpler interview story
```

### 5.5 Metrics pipeline — local counters → stream → rollup

**Stage 1 — Local counters (shard leader process)**

```text
Component: MetricsAgent per shard (in-process with leader)

On each counted op (get/put) AFTER KV apply:
  counter = slidingWindows.computeIfAbsent(key, SlidingWindowCounter::new)
  counter.recordOp(now_ms, op_kind)   // 1s bucket model — see LLD

Memory control:
  idle_key_ttl = 10m → evict counter if no ops
  max_keys_tracked_per_shard = 1M → LRU evict cold counters (QPS returns 0 until ops resume)

Coalesce flush (every 1s):
  for each key with delta since last flush:
    emit MetricRollupEvent { shard_id, key, bucket_ts, get_count, put_count }
  clear deltas
```

Aligns with LLD `BucketCounter`: 60 buckets × 1s for 60s window; extend to 300 buckets or hierarchical rollup for 5m window.

**Stage 2 — Stream (durable bus)**

```text
Topic: kv-metrics-rollups (partition by hash(key) for ordering per key)
Retention: 24–72h for replay
Compression: zstd
At-least-once produce; broker acks

Baseline: ~32 shards × ~1 flush/s × avg_active_keys_per_flush
  If 10K keys/shard active/s → 320K msgs/s — still heavy
  Optimize: only emit keys with non-zero delta (typically far fewer)
  10×: coalesce to per-shard aggregate + hot-key side topic
```

**Stage 3 — Rollup workers**

```text
Consumer group: rollup-workers
For each MetricRollupEvent:
  idempotent upsert into RollupStore:
    table: key_metrics (shard_id, key, bucket_ts, get_cnt, put_cnt)
    PRIMARY KEY (shard_id, key, bucket_ts)

Sliding window query for window=60s at query time:
  sum(get_cnt + put_cnt) for bucket_ts in (watermark - 60s, watermark]
  qps = sum / 60.0

Watermark:
  global_watermark = min(last_processed_ts) across partitions — lag metric
  per-shard watermark for partial degradation
```

**Stage 4 — Query store**

```text
Options:
  MVP: Redis/Scylla keyed by (shard_id, key) with recent bucket columns
  100×: ClickHouse/Timescale for analytics; cache hot keys in Redis

Materialized views:
  mv_qps_60s refreshed every 1s for keys in top-K hot set
```

### 5.6 GET /metrics/qps — full semantics

**Request**

```http
GET /v1/metrics/qps?key=customer%2Ffoo&window=60s&op_mask=get,put
Authorization: Bearer ...
```

| Param | Values | Default |
|-------|--------|---------|
| key | URL-encoded string | required |
| window | `1s`, `60s`, `300s` | `60s` |
| op_mask | comma-separated `get`,`put`,`delete` | `get,put` |

**Response 200**

```json
{
  "key": "customer/foo",
  "window_sec": 60,
  "qps": 142.35,
  "op_count": 8541,
  "op_breakdown": { "get": 7200, "put": 1341 },
  "as_of_ts": "2026-08-06T12:34:56Z",
  "staleness_ms": 2300,
  "precision": "exact",
  "shard_id": 17
}
```

**Errors**

| Code | When |
|------|------|
| 400 | Invalid window or malformed key |
| 401/403 | Auth failure / key not in tenant namespace |
| 404 | Never for missing key — return qps=0 (200) unless product says otherwise |
| 429 | Metrics API rate limit (especially per-key polling) |
| 503 | Rollup store unavailable; optional degraded shard-local proxy |

**Consistency wording for clients:**

> QPS reflects operations that completed successfully on the KV path. Due to async aggregation, values may lag real time by `staleness_ms`. For keys with zero recent activity, `qps=0` even if key exists in KV.

### 5.7 Eventual metrics vs strong KV — why both

| Dimension | KV | Metrics |
|-----------|-----|---------|
| Purpose | Source of truth for values | Observability / throttling input |
| User expectation | Read-after-write | Near-real-time dashboard |
| Failure impact | Must fail closed / retry | Degrade gracefully |
| Implementation | Sync replicate | Async stream |
| Lost on crash | Unacceptable | Bounded loss OK |
| Cross-region | Strong in home cell | Aggregated with lag |

**Anti-pattern:** synchronously replicate metrics with KV before ACK — couples tail latency, doubles failure modes, doesn't help KV correctness.

**When to strengthen metrics:** billing, SLO enforcement with financial impact → add outbox on KV path, exactly-once stream processing, longer retention — separate "Billing Meter" service consuming same events.

### 5.8 Sliding windows at scale

**Single-node (LLD reference):**

```text
BucketCounter: 60 × 1s atomic buckets
recordOp: increment bucket[sec % 60]
getQps: prune buckets older than window; sum / 60.0
See: kv-sliding-window-qps-lld-system-design.md
```

**Distributed mapping:**

| LLD concept | HLD service mapping |
|-------------|---------------------|
| `SlidingWindowCounter` per key | `MetricsAgent` on shard leader |
| `recordOp` on get/put | Hook after KV apply |
| `getQps(key)` | `GET /metrics/qps` reads rollup store, not direct shard call |
| `BucketCounter` 60×1s | Same structure locally; flushed to stream |
| Ring buffer exact mode | Hot-key tier only (top 10K keys) |
| `delete(key)` clears counter | Optional: emit tombstone; idle TTL evicts |

**Multi-resolution:**

```text
1s buckets retained 1 hour → window=1s queries
Roll up to 1m buckets hourly → window=300s and long trends
Query router picks resolution based on window param
```

### 5.9 Hot keys

**Detection signals:**

- Shard CPU / Raft commit queue depth  
- MetricsAgent key delta >> peers  
- Stream partition skew  
- `GET /metrics/qps` cache miss storm on one key

**Mitigation ladder:**

| Level | Action |
|-------|--------|
| L1 | Read replicas for GET; leader stays write owner |
| L2 | Near-leader read cache (versioned); short TTL 100ms |
| L3 | Metrics coalesce: 1 event/s/key regardless of op rate |
| L4 | Coordinator cache for QPS API |
| L5 | Tenant namespaced key splitting (app-level sharding) |
| L6 | Control-plane key migration to dedicated shard |

**Metrics hot key paradox:** monitoring a hot key's QPS can itself become hot — **pre-aggregate at shard**, **cache at coordinator**, **rate-limit** per-key metrics queries (e.g. max 1 req/s/client/key).

### 5.10 Idempotency

```text
PUT / DELETE with header Idempotency-Key: uuid
Shard leader:
  lookup (tenant, idempotency_key) in TTL store (24h)
  if hit: return stored response
  else: execute op, store response hash + status, return

Scoped to (tenant, idempotency_key) — not automatically keyed by resource key
```

### 5.11 Failure modes

| Failure | KV behavior | Metrics behavior |
|---------|-------------|------------------|
| Leader crash | Failover 1–3s unavail | Coalesce buffer loss ≤1s |
| Network partition (minority) | Minority can't commit | Minority stops emitting |
| Stream broker down | KV unaffected | Lag grows; serve stale with high staleness_ms |
| Rollup worker stuck | KV unaffected | Alert; replay from offset |
| Hot shard overload | Rate limit / 503 selective | Approximate QPS; cache |
| Idempotency store full | Evict oldest; risk duplicate if retry after evict | N/A |
| Clock jump on shard | NTP resync | Use ingest-time at aggregator |

### 5.12 Scalability — progressive scale narrative

**1× MVP (monolithic-ish)**

```text
8–32 shards on 3 AZs
Single Kafka cluster; 1 rollup consumer group
Exact bucket counters for all active keys on shard (≤1M keys/shard)
Gateway + router co-located
```

**10×**

```text
256 shards; horizontal API tier
Metrics: coalesce flush; partition stream by hash(key)
Rollup store: Scylla/Redis cluster
Hot-key admin API
Read replicas per shard
Shard map service with watch notifications
```

**100×**

```text
2K+ shards; cell per region (home cell owns key namespace prefix)
Metrics: dual path — hot exact + cold CMS sketch
Flink continuous sliding window for regional aggregates
Metrics query federation across cells (key routing knows home cell)
Admission control: per-tenant metrics query budget
```

**1,000×**

```text
20K shards; multi-cell global
KV: follow Dynamo/Cassandra patterns with LWT where needed
Metrics: sampling for tail keys; exact tier for top 0.01%
Global hot-key detection ML (optional mention)
Edge caching of QPS for CDN-like viral keys
```

### 5.13 Maintainability, security & ops

- Schema versioning for rollup events; replay from stream retention; chaos tests (leader kill → KV strong, metrics gap bounded).  
- Dashboards: `metrics_pipeline_lag_ms`, `shard_qps_variance`, `hot_key_count`, `idempotency_hit_rate`.  
- Tenant key prefix + AuthZ; quotas on KV and metrics poll rate; TLS + SSE at rest.  
- Optional throttle (Phase 2): hot-key topic → gateway token bucket; hysteresis to avoid feedback loops.

### 5.14 Comparison to LLD pivot

Interview flow often starts HLD (this doc) then pivots:

> "Implement the sliding window counter on a single node."

**Handoff map:**

| HLD topic | LLD doc section |
|-----------|-----------------|
| Per-key sliding window | §4 BucketCounter / TimestampRing |
| recordOp on get/put | §3 data flow |
| getQps semantics | §2 API `getQps(key)` |
| Thread safety | §5 concurrency invariants |
| delete clears state | §6 delete pseudocode |
| Hot key 100k ops/s | §7 ring overflow / bucket only |

**What changes at HLD layer:** routing, replication, async flush, rollup store, API envelope with `as_of_ts`, hot-key caching — not the bucket math itself.

**What NOT to re-implement in HLD interview:** full Raft log details unless asked — point to shard leader + linearizable.

**Data model:** shard-local `kv_store` + idempotency TTL; rollup `key_metrics(shard_id, key, bucket_ts, get_cnt, put_cnt)`; optional `qps_cache` for hot keys.

---

## 6. Wrap-Up

**Design summary**

- **Sharded KV** with **consistent-hash home shard** and **Raft-linearizable** get/put/delete per key.  
- **Metrics plane** separate: **local 1s bucket counters → coalesced stream → rollup workers → query store**.  
- **`GET /metrics/qps`** returns sliding-window QPS with honest **`as_of_ts` / `staleness_ms`**; **eventually consistent** vs **strong KV**.  
- **Hot keys:** read replicas, coalesced metrics, coordinator cache, graduated migration.  
- **LLD pivot:** single-node bucket/ring logic in `kv-sliding-window-qps-lld-system-design.md`.

**MVP vs later**

| MVP | Later |
|-----|-------|
| 32 shards, single region | Cells, 2K+ shards, multi-region home |
| Exact buckets for active keys | CMS for cold tail |
| Metrics lag 1–5s OK | Sub-second for SLO tier |
| Read-only metrics API | Throttle enforcement |
| Manual rebalancing | Automated split/merge |

**Top risks**

1. Hot key saturates shard leader — detect early.  
2. Treating metrics as billing-exact without stronger pipeline.  
3. Coupling metrics to KV ACK — tail latency explosion.  
4. Metrics query storm on viral key — cache + rate limit.  
5. Ignoring idempotency — retry duplicates corrupt state.

**What I'd measure first**

`shard_leader_commit_latency_p99`, `metrics_consumer_lag_ms`, `hot_key_qps_max`, `kv_error_rate`, `metrics_query_cache_hit_rate`.

---

## 7. Deeper / Related Interview Questions

1. Consistent hashing when adding shards?  
2. Raft vs primary-backup for linearizable KV?  
3. Why not Redis INCR globally for QPS?  
4. Exactly-once metrics — worth it?  
5. Cross-region QPS for remote home key?  
6. Sliding vs fixed window for alerting?  
7. Shard split without downtime?  
8. Timestamp ring vs buckets at service scale?  
9. Multi-tenant noisy neighbor on shared shard?  
10. Billing-grade meter as separate service?

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| Sync metrics with KV ACK | Couples latency; async with staleness header |
| Global QPS counter | Doesn't scale; per-key home shard |
| Strong metrics everywhere | Overkill; define use case |
| Skip hot key story | Shard leader melts |
| Cross-shard linearizable KV | 2PC cost; out of scope |
| Unbounded per-key timestamp ring at scale | Use buckets + CMS tail |

---

### 7.1 Core follow-ups (with answers)

**Q: QPS metric accuracy?**  
A: **Eventually consistent** aggregates with typical 1–5s lag. Exact **1s bucket** arithmetic on home shard; rollup store sums buckets. Response includes `as_of_ts` and `staleness_ms`. Hot keys served from exact tier; cold tail may use approximate CMS at 100×.

**Q: Sliding window at scale?**  
A: Same **1s bucket model** as LLD on each shard's `MetricsAgent`. Local `recordOp` on every get/put; **coalesced flush to stream**; rollup workers maintain queryable bucket history. Query computes sum over last N seconds / N. See `kv-sliding-window-qps-lld-system-design.md` for single-node prune/record semantics.

**Q: Hot key on metrics?**  
A: **Coalesce** to 1 rollup event/s/key on shard; **cache** QPS at coordinator; **rate-limit** per-key metrics polling. Detection via shard skew + stream partition lag. KV mitigations: read replicas, near-leader cache.

**Q: Strong consistency for put/get?**  
A: **Linearizable within home shard** via Raft leader + durable WAL. Not cross-shard. Metrics intentionally weaker — async, observability-only.

**Q: How is this different from the LLD?**  
A: HLD adds sharding, stream rollup, REST API with `as_of_ts`, hot-key ops. LLD implements `SlidingWindowCounter` in one process. Pivot: implement LLD after HLD boxes.

**Q: Read-your-writes for metrics after PUT?**  
A: **Not guaranteed** for QPS; KV yes with sticky leader. Optional `?consistency=leader` hits shard agent directly.

**Q: Idempotency interaction with QPS?**  
A: Only **accepted** ops count; idempotent retry must not double-count.

**Q: Shard math quick formula?**  
A: `N = ceil(peak_qps / 2500)` → power of 2; 50K → 32 shards; split hot shards independently.

**Q: Testing / kv-race-repair relation?**  
A: Property-test bucket sums; chaos leader kill; LLD unit tests for concurrent `recordOp`. Race-repair LLD fixes single-node lost updates; HLD adds idempotent rollup + at-least-once stream.

*End of KV Store with QPS API HLD prep.*
