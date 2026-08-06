# System Design: Distributed Multi-User Counter

> **Interview framing:** NVIDIA backend / cloud interviews (team-dependent). Counters appear in quotas, likes/reactions, GPU-seconds burn, API usage metering, and experiment dashboards. Interviewers probe **hot keys**, **approximate vs exact**, and **read-your-writes**—not only `INCR`.
> **Focus areas:** High write-rate counters · Sharding · Approximate vs exact · CRDTs (PN-Counter) · Redis/DB options · Read-your-writes · Hot-key fairness
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split write QPS from read QPS; honest error bounds for approximate designs; no single-row hotspot at 100×; clear RYW story

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the counter**—what is counted, exact vs approximate, increment/decrement, multi-user races, read freshness, and whether money-like correctness applies.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What are we counting? | Likes, views, API calls, GPU-seconds, download counts, experiment metrics | Different exactness & retention |
| F2 | Ops? | `incr`, optional `decr`, `get`, optional `reset`, batch incr | PN-Counter vs G-Counter |
| F3 | Exactness? | **Views:** approximate OK (±1–2%); **billing/quota:** exact or audited exact | Dual paths possible |
| F4 | Multi-user? | Huge concurrent increments on popular keys | Shard / CRDT / local agg |
| F5 | Users vs keys? | Many users → many keys; also celebrity hot keys | Two load patterns |
| F6 | Read path? | Show count on page; dashboards; rate limit checks | Cache + RYW rules |
| F7 | Idempotency? | Client retries must not double-count events | Idempotency keys / dedupe |
| F8 | Time series? | Sometimes need per-minute buckets | Rollups separate from live gauge |
| F9 | Multi-region? | Global counts with lag OK for social; stricter for quota | Home region or CRDT merge |
| F10 | Fairness? | Hot key must not starve other keys on same shard | Isolation / separate hot path |
| F11 | Authz? | Who can incr/get/reset | API keys / user auth |
| F12 | Analytics? | Top-K, histograms | Separate pipeline from online counter |

**MVP functional scope (lock with interviewer):**

1. API: `Incr(key, delta, idempotency_key?)`, `Decr` (or signed delta), `Get(key)`, `GetMany`.
2. Support high QPS increments with **sharded partial counters**.
3. Exact mode (stronger) and approximate mode (cheaper) as product flags per keyspace.
4. Read-your-writes for the incrementing user within a session (sticky or sync token).
5. TTL / archival policies for ephemeral keys.
6. Metrics: hot keys, error rate, lag of rollups.
7. Optional: sliding-window counts for rate limits (different structure).

**Out of MVP:**

- Perfect global linearizability for every `Get` at 1M write QPS on one key.  
- Ad-hoc SQL analytics on raw incr stream without a pipeline.  
- Negative counts if product forbids (define clamp policy).  
- Exactly-once without idempotency keys.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Incr latency | Fast | p99 < 10–50ms in-region |
| N2 | Get latency | Fast | p99 < 20ms (cached) |
| N3 | Durability | Mode-dependent | Exact: quorum/disk; Approx: lossy OK within bound |
| N4 | Accuracy (approx) | Document bound | e.g. ±1% or ±X absolute with high probability |
| N5 | Availability | Prefer availability for social counts | AP with merge; CP for billing |
| N6 | Hot key | Survive viral key | Special handling |
| N7 | Multi-tenant | Noisy neighbor isolation | Shuffle shards / per-tenant caps |
| N8 | Scale | See table | Split **incr QPS**, **get QPS**, **rollup QPS** |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User likes post → `Incr(like:post123)` → Get shows +1 (RYW).  
2. 50K users like celebrity post → sharded counters merge to one logical value.  
3. Quota service `Incr(gpu_seconds:org)` exact → enforce threshold.  
4. Views approximate → buffered local agg flush every 100ms.  
5. Idempotent retry of same event → count +1 once.  
6. Dashboard reads slightly lagged rollup for charts; online Get for badge.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double submit like button | Idempotency key / user×object unique |
| Decr below zero | Clamp 0 or allow negative—product |
| Redis node loss (approx) | Bound loss via flush frequency |
| Hot key thundering reads | Cache with jittered TTL; merge tree |
| Get during flush | Monotonicity policy: never go backwards if required |
| Multi-region incr | CRDT merge or home region |
| Reset races incr | Epoch/generation on key |
| Key cardinality explosion | TTL + namespace quotas |
| Billing dispute | Audit log of exact increments |
| Clock for windows | Server buckets; not client clock |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Logical keys | 10M | 100M | 1B | 10B |
| Active keys / day | 1M | 10M | 100M | 1B |
| Peak **incr** QPS (cluster) | 50K | 500K | 5M | 50M |
| Peak **get** QPS | 100K | 1M | 10M | 100M |
| Hottest single key incr QPS | 5K | 50K | 500K | 5M |
| Tenants | 1K | 10K | 100K | 1M |
| Regions | 1 | 2 | 4 | 8+ |
| Avg delta payload | 50 B | 50 B | 50 B | 50–100 B |
| Idempotency retain | 24h | 24h | 24–72h | 72h |
| Rollup flush | 1s | 1s | 100–500ms | 50–100ms batches |

**What each jump forces:**

- **10×:** Redis Cluster / sharded counters; local aggregation.  
- **100×:** Hot-key adaptive splitting; approx path; dedicated get caches.  
- **1,000×:** Hierarchical aggregation trees; regional CRDTs; stream + OLAP for analytics.

### 1.5 Etc. (Constraints & Assumptions)

- “Counter” here is an **online serving** primitive; heavy analytics is a pipeline.  
- NVIDIA angle: **GPU-seconds**, **API metering**, **job success counts**, experiment metrics—call out exactness.  
- Users are concurrent; **single DB row `UPDATE`** dies on hot keys.  
- Retries happen—**idempotency** is part of the design.

**Scope statement:**

> Design a distributed multi-user counter service supporting extremely high increment rates (including hot keys), with explicit approximate vs exact modes, PN-Counter/CRDT or sharded partial sums, Redis/DB trade-offs, read-your-writes, and fairness so celebrity keys do not melt shared shards—evolving from 50K to 50M incr QPS through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Incr writes | 50K QPS | 50M QPS | Dominates design |
| Get reads | 100K QPS | 100M QPS | Cache heavily |
| Flush/rollup writes | 5K QPS | 5M QPS | Aggregated |
| Idempotency lookups | ~50K QPS | ~50M QPS | Soften with hash partitions |
| Admin/reset | low | low | Separate |

**Deal-breaker:** Capacity planning only on “100K QPS” without separating hottest-key vs aggregate.

### 2.2 Hot key math

```text
Celebrity key: 50K incr/s at 10× table cell… baseline hottest 5K/s
If each incr is a Redis INCR to ONE key: single key throughput may be OK at 5K,
but at 500K/s one key → MUST striping / local agg.

Stripe into N partials:
  chosen N so per-partial QPS ≈ target_safe (e.g. 10K)
  N ≈ hot_qps / 10K
  At 500K/s → N ≈ 50 partial keys; Get sums 50 (or tree)
```

### 2.3 Bandwidth

```text
50M incr/s × 50 B ≈ 2.5 GB/s ingress at 1000×
Network OK with LBs; storage engine must batch
```

### 2.4 Memory (Redis)

```text
10M keys × 128 B ≈ 1.28 GB (tight; real higher with overhead)
1B keys → ~100GB+ → not one instance; shard + eviction/TTL
Hot partials: keep in memory; cold exact in DB
```

### 2.5 Aggregation error (approx)

```text
Local buffer flush every T=100ms, crash loses ≤ buffer
If rate r=10K/s on node, max loss ≈ r×T = 1,000 counts per crash
Relative error depends on magnitude; for large counters often <<1%
For tiny counters, absolute error dominates → use exact mode
```

### 2.6 Critical bottlenecks

1. **Single logical hot key**  
2. **Get summing too many stripes synchronously**  
3. **Idempotency store** at write QPS  
4. **Global secondary indexes** (top-K) on write path  
5. **Cross-region chatty merges**  
6. **Fairness:** hot key occupying shard CPU  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Keyspace       → tenant + name prefix + mode (exact|approx)
LogicalCounter → key → value (int/long)
Partial        → stripe of logical counter (shard id)
Idempotency    → (keyspace, idem_key) → applied delta
WindowCounter  → optional time-bucketed counts
Aggregator     → merges partials / CRDT payloads
```

### 3.2 Options: storage & algorithms

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. SQL `UPDATE` one row | Exact, simple | Hot row lock death | Hot keys / high QPS |
| B. Redis `INCR` | Fast exact in-memory | Durability/failover care; hot key limits | Billing without AOF/replication story |
| C. **Sharded partial sums** | Scales hot keys | Get must assemble; complexity | Forgetting adaptive stripe count |
| D. **CRDT PN-Counter** | Multi-region merge | Metadata size; not money ledger alone | Needing strict audit without log |
| E. Stream + materialize | Huge ingest | Read lag | RYW without sticky session |
| F. Approximate sketches (HLL, Count-Min) | Cardinality / heavy hitters | Not exact values | “How many likes exactly?” |

**Chosen path:**

- **Approx / social:** local aggregation → Redis partials → periodic durable snapshot.  
- **Exact / quota:** idempotent durable log or transactional store with **striped locks** + synchronous quorum; or per-user unique constraints for likes.  
- **Multi-region eventual:** PN-Counter CRDT merge for non-billing metrics.

### 3.3 G-Counter vs PN-Counter

```text
G-Counter: each replica only increments its slot; value = sum(slots)
PN-Counter: P (positive G) and N (negative G); value = sum(P) - sum(N)
```

Use PN when decrements exist (unlikes). Use G when monotonic.

**Deal-breaker:** Decrementing a G-Counter by writing negative without N vector—breaks CRDT merge.

### 3.4 Sharding strategies

| Strategy | Mechanism |
|----------|-----------|
| Key hash | `hash(logical_key) % N` for cold keys |
| Stripe hot | `hash(logical_key, stripe_i)` for i in 0..S-1; pick stripe by `hash(user)` or random |
| Adaptive | Controller increases S when QPS/latency high |
| Tenant cell | Tenant → cell; noisy tenant isolated |

**Get:**

```text
sum = Σ partial[i]   # or tree reduce
cache final with short TTL; invalidate/jitter
```

### 3.5 Approximate vs exact (resolve product)

| Mode | Write path | Read path | Failure semantics |
|------|------------|-----------|-------------------|
| Exact | Quorum / WAL before ACK | Read quorum or primary | No loss after ACK |
| Approx | Buffer → async flush | Sum partials + buffers optional | Bounded loss on crash |
| Hybrid | Exact for money; approx for views | Separate keyspaces | Don’t mix |

**Interview win:** Ask which keys need auditability.

### 3.6 Idempotency & exactly-once effects

```text
Incr(key, delta, idem_key):
  if seen(idem_key): return previous result
  apply delta
  remember idem_key → result (TTL)
```

For likes: unique `(user_id, object_id)` may replace generic idem keys.

### 3.7 Read-your-writes (RYW)

Options:

1. **Sticky session** to replica that took write.  
2. **Sync token / version** returned by Incr; Get with `min_version`.  
3. **Client adds local +1** optimistic until server Get catches up.  
4. **Read from leader** for that key’s stripe (costly).  

**Chosen MVP:** return `version` from Incr; Get supports `If-Version-≥`; client optimistic UI for likes.

### 3.8 Fairness under hot keys

- Detect hot keys (QPS histogram).  
- Move to dedicated stripe set / dedicated shard.  
- Per-key rate limits for abusive incr.  
- Separate thread pools / queues so cold keys progress.  
- Admission control on hottest keys before shared Redis CPU melts.

### 3.9 Redis vs DB trade-offs

| Concern | Redis | DB (Postgres/NewSQL) | Hybrid |
|---------|-------|----------------------|--------|
| Incr QPS | Excellent | Poor for hot row | Redis online + DB snapshot |
| Durability | AOF/REPL tunable | Strong | Flush checkpoints |
| Complex query | Weak | Strong | Analytics pipeline |
| Cost at 1B keys | Memory $$ | Cheaper cold | Tiered |

**Deal-breaker:** Redis without persistence story when claiming exact billing.

### 3.10 Trade-off summary table

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Hot keys | Adaptive striping | Survive celebrity | Single INCR key |
| Approx | Local agg | Cut QPS 10–100× | Claiming exact |
| Exact likes | Unique pair | Natural idempotent | Only Redis INCR |
| Multi-region | PN-Counter or home | Merge vs CP | Dual primary SQL |
| RYW | Version token + optimistic | UX | Always stale Get |
| Analytics | Kafka → OLAP | Don’t block incr | Sync ES on incr |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Clients / Services / GPU agents
              |
              v
      +---------------+
      | API Gateway   |  authz, rate limit, mode route
      +-------+-------+
              |
       +------+------+
       |             |
       v             v
 +-----------+  +--------------+
 | Exact Path|  | Approx Path  |
 | (WAL/Quorum|  | (local agg → |
 |  striped) |  |  flush)      |
 +-----+-----+  +------+-------+
       |               |
       +------+--------+
              |
              v
     +------------------+
     | Counter Store    |
     | Redis cluster /  |
     | partial keys +   |
     | CRDT payloads    |
     +--------+---------+
              |
       +------+------+
       |             |
       v             v
 +-----------+  +-------------+
 | Get Cache |  | Durable Log |
 | (optional)|  | / Snapshots |
 +-----------+  +------+------+
                       |
                       v
                 Kafka → Rollups / OLAP
                       |
                       v
                 Ops Dashboard (hot keys, lag)
```

### 4.2 Sequence: sharded incr + get

```text
Client          API              Partial Stripe k        Aggregator
  |-- Incr ---->| hash → stripe k -->|
  |             | INCR partial_k ---->|
  |<- version --|<--------------------|
  |-- Get ----->|                    |
  |             |-- MGET partials ------------------> sum
  |<- value ----|<-----------------------------------|
```

### 4.3 Sequence: approx local aggregation

```text
API node local map: key → buffered_delta
every 100ms or 1000 events:
  flush pipeline INCRBY to Redis partials
on crash: lose buffer (bounded)
Get: Redis sum (+ optionally add local buffer for RYW on same node)
```

### 4.4 Sequence: PN-Counter multi-region

```text
Region A: P[A] += d
Region B: P[B] += e
Merge: value = Σ P[*] - Σ N[*]
Gossip / async replication of vectors
```

### 4.5 Hot-key adaptive split

```text
Controller observes key QPS > threshold
  increase stripes S→2S
  new incr go to expanded set
  old partials remain; Get sums all generations
  optional compaction job merges stripes offline
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Exact mode ACK ⇒ durable delta** (quorum/WAL).  
2. **Idempotent Incr** when idem_key provided.  
3. **Approx error bounded** by flush policy; documented.  
4. **Monotonicity (optional product):** Gets never decrease except explicit Decr/reset—flush ordering matters.  
5. **Generation on reset:** incr with old gen ignored.  
6. **Tenant isolation** on key prefixes.  

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Redis primary failover | Wait for sync; exact mode may reject during election |
| Flush loss | Accept for approx; alert on node kill rate |
| Split brain stripes | Epoch in key names; generation |
| Under-count after merge bug | Auditor vs durable log sample |
| Idempotency TTL expire too soon | Align with retry window |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Redis INCR + PG backup nightly; idempotency table |
| 10× | Redis Cluster; stripe popular; local agg for views |
| 100× | Hot-key service; hierarchical get cache; Kafka audit |
| 1000× | Regional CRDT; aggregation trees; keys tiered cold/warm |

**Get scaling**

- Cache summed value with TTL 100–500ms for hot keys (approx OK).  
- For exact: cache with version; invalidate on incr via pubsub (careful thundering).  
- Tree reduce: leaf partials → mid aggregators → root for extreme S.

**Write scaling**

- Local agg cuts Redis QPS.  
- Pipeline/batch INCRBY.  
- Partition idempotency store.

### 5.3 Maintainability

- Keyspace configs in registry (`mode`, `stripe_default`, `ttl`).  
- Chaos: kill flushers, failover Redis, skew clocks for windows.  
- Replay from Kafka to rebuild.  
- Hot-key dashboard for operators.  
- Clear SLOs per keyspace class.

**Observability**

- Metrics: incr QPS, get QPS, flush lag, stripe count per hot key, approx loss estimates, cache hit, idempotency hit rate.  
- Traces: `key`, `stripe`, `idem_key`, `version`.  
- Alerts: hot key CPU, failover, negative clamps.

### 5.4 Progressive scale deep dive

**1× MVP**

```text
INCR key in Redis
AOF everysec for approx-ish durability
PG unique (user,object) for likes exact
GET from Redis
```

Bottleneck: celebrity key + Redis single instance memory.

**10×**

- Cluster; hash tags carefully.  
- Stripe `key#s{i}`.  
- Local agg microservice sidecars.  

**100×**

- Adaptive striping controller.  
- Version tokens for RYW.  
- Exact path via durable log (Kafka) + materializer for billing.  
- Fair scheduling queues.

**1000×**

```text
Region local PN payloads
Global approximate query via merge
Billing remains home-region exact ledger (not pure CRDT)
Cold keys evicted to DB; hydrate on demand
Aggregation trees for 5M QPS hot keys
```

### 5.5 Fairness deep dive

```text
Shared shard thread handling 100K cold keys + 1 hot key
Risk: hot key occupies CPU / event loop
Mitigations:
  - dedicated connection pool for hot keys
  - separate Redis DB/cluster tier for hot
  - token bucket per key
  - worker queue isolation (sidekiq-style queues)
```

**Deal-breaker:** Assuming Cluster hash slots alone solve hot keys—**same slot still hot** if one key.

### 5.6 Rate-limit windows vs gauges

| Use | Structure |
|-----|-----------|
| Lifetime likes | Gauge counter |
| API requests / minute | Sliding window / fixed buckets |
| Concurrent leases | Different service (not this) |

Don’t overload one counter API for all semantics without bucket keys (`key:yyyyMMddHHmm`).

### 5.7 Consistency multi-region

| Approach | Semantics |
|----------|-----------|
| Home region | Stronger reads if read home; higher latency cross-region |
| CRDT merge | Eventual; always mergeable; good for views |
| Async replicate Redis | Possible loss / lag; document |

**Billing:** home-region ledger. **Views:** CRDT/approx.

### 5.8 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| One SQL row | Lock contention |
| “Redis is always exact” | Durability/loss window |
| No idempotency | Double counts |
| Global lock for RYW | Kills throughput |
| Top-K on write path | Melts incr |
| Hash slots fix hot key | Still one key |
| PN-Counter for money without audit | Disputes |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Hot keys | Adaptive striping + isolation |
| Modes | Exact vs approx keyspaces |
| Multi-region | CRDT for soft; home for billing |
| RYW | Version token + optimistic UI |
| Idempotency | Required for retries / likes |
| Analytics | Async pipeline |
| Store | Redis partials + durable snapshots/log |

### 6.2 Top risks

1. Hot key under-designed  
2. Claiming exact with lossy flush  
3. Missing idempotency  
4. Get fan-out over thousands of stripes  
5. Fairness collapse on shared shards  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Exact vs approx; ops; multi-region |
| 5–12 | API + idempotency + RYW |
| 12–22 | HLD Redis/DB + striping |
| 22–32 | Hot keys + fairness + CRDT |
| 32–40 | Scale path 10×–1000× + math |
| 40–45 | Failures + billing vs views |

---

## 7. Deeper / Related Interview Questions

### 7.1 Exactness

**Q: When is approximate unacceptable?**  
A: Billing, quotas that gate money/GPU access, compliance—use exact + audit.

**Q: How to quantify approx error?**  
A: Bound by flush interval × rate + replica loss; measure with shadow exact sampling.

**Q: Can we be eventually exact?**  
A: Yes—async durable log reconciles; online Get may lag.

### 7.2 CRDTs

**Q: Explain PN-Counter**  
A: P and N G-Counters per replica; merge takes element-wise max; value Psum−Nsum.

**Q: Does CRDT prevent double-like by one user?**  
A: No—need a set/unique constraint for “liked users,” not only a counter.

**Q: Metadata overhead?**  
A: One integer per replica per counter; many counters × many replicas → watch memory.

### 7.3 Redis specifics

**Q: INCR atomicity?**  
A: Single-key atomic on node; not cross-key transactional without Lua/Multi caveats.

**Q: Persistence?**  
A: AOF everysec can lose ≤1s; always for exact billing prefer stronger.

**Q: Cluster hot slot?**  
A: Striping must use different keys (different slots); hash tags can worsen—avoid tagging all stripes together.

### 7.4 Hot keys

**Q: Random stripe vs user-hash stripe?**  
A: User-hash helps RYW locality; random better balances if users skewed.

**Q: How many stripes?**  
A: `ceil(peak_qps / per_key_budget)`; adaptive.

**Q: Get too slow?**  
A: Cache sum; hierarchical reduce; read approx.

### 7.5 RYW & freshness

**Q: User doesn’t see their like?**  
A: Optimistic UI or version token; sticky to write replica.

**Q: Monotonic reads?**  
A: Never serve cached value older than client token; version checks.

### 7.6 Idempotency

**Q: TTL for idem keys?**  
A: ≥ max client retry window (e.g. 24–72h).

**Q: Huge cardinality of idem keys?**  
A: Shard; bloom + store; for likes use natural unique pairs.

### 7.7 Fairness & multi-tenant

**Q: Noisy tenant?**  
A: Per-tenant QPS caps; shuffle shards; noisy cell.

**Q: Priority of incr?**  
A: Billing path separate queue from best-effort views.

### 7.8 NVIDIA-flavored

**Q: Count GPU-seconds?**  
A: Exact ledger from scheduler settle events (idempotent job_id); not lossy page-view path.

**Q: Count inference requests?**  
A: Approx OK for dashboards; exact for billed tiers—dual.

### 7.9 Comparison

**Q: vs Kafka + Flink?**  
A: Great for analytics; add online serving store for low-latency Get.

**Q: vs DynamoDB atomic counters?**  
A: Similar hot partition issues; still need striping.

### 7.10 Windows & rate limits

**Q: Implement 1000 req/min?**  
A: Fixed buckets or sliding log; not a single lifetime counter.

**Q: Clock skew?**  
A: Bucket on server time.

### 7.11 Reliability drills

**Q: Kill aggregator mid-flush?**  
A: At-least-once flush with idempotent INCRBY batches carefully—or accept dup risk only in approx with corrective reconciliation.

**Q: Negative count?**  
A: Clamp; alert; audit.

### 7.12 Arithmetic traps

**Q: 50M QPS × 50 B?**  
A: **2.5 GB/s** ingress.

**Q: Stripe count for 5M/s hot key at 10K/s per partial?**  
A: **500 stripes**—then you need aggregation tree / cached sum, not 500 serial Redis round-trips on Get.

### 7.13 Top-K

**Q: Maintain top-1000 on write?**  
A: Approximate heavy-hitters (Count-Min + heap) async; don’t do global sort per incr.

### 7.14 Reset / TTL

**Q: TTL delete vs zero?**  
A: TTL removes key; Get returns 0; ensure stripes share TTL policy.

**Q: Reset with in-flight incr?**  
A: Bump generation; ignore old gen.

### 7.15 One-line correctness

> Separate exact vs approx; stripe hot keys; idempotent incr; RYW via versions/optimism; never claim one Redis key survives 1M QPS alone.

---

## 8. Appendices

### 8.1 Schema sketches

```text
Redis:
  c:{keyspace}:{key}#s{i} → integer
  c:{keyspace}:{key}#meta → JSON {stripes, gen, mode}
  idem:{keyspace}:{idem} → 1 (TTL)

Postgres (exact likes):
  likes(user_id, object_id, created_at) PRIMARY KEY (user_id, object_id)
  counters_snapshot(key, value, updated_at)

Kafka:
  incr_events(key, delta, idem, ts, tenant)
```

### 8.2 API checklist

- [ ] `POST /v1/counters/{key}/incr`  
- [ ] `POST /v1/counters/{key}/decr`  
- [ ] `GET /v1/counters/{key}` (`min_version` optional)  
- [ ] `GET /v1/counters:batchGet`  
- [ ] `POST /v1/counters/{key}/reset`  
- [ ] Admin: hot-key status, force split  
- [ ] Keyspace config CRUD  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Partial / stripe | Shard of one logical counter |
| PN-Counter | CRDT supporting increments & decrements |
| Exact mode | Durable ACK semantics |
| Approx mode | Bounded-loss aggregation |
| RYW | Read-your-writes session guarantee |
| Generation | Epoch after reset |
| Hot key | Extreme QPS logical key |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Redis INCR, idempotency, basic Get |
| 10× | Cluster, striping, local agg |
| 100× | Adaptive hot-key, version RYW, audit log |
| 1000× | Regional CRDT, agg trees, tiered storage |

### 8.5 Stripe pick algorithm

```text
stripe = hash(user_id | request_id) % S
# or random(S) for max balance
key = f"{logical}#g{gen}#s{stripe}"
```

### 8.6 Interview “say this” summary (60 seconds)

> Distributed counters with exact vs approximate keyspaces; hot keys via adaptive striping and isolation; PN-Counters or home-region ledgers for multi-region; idempotent increments; RYW with versions/optimistic UI; Redis for online partials plus durable log/snapshots—never a single row for celebrity keys.

### 8.7 Extra traps

| Trap | Pushback |
|------|----------|
| Single SQL row | Hot lock |
| Exact + lossy flush | Contradiction |
| No idempotency | Double count |
| Hash slot = hot fix | Still one key |
| 500 MGET sync Get | Too slow—cache/tree |
| CRDT replaces like-set | Users need uniqueness |

### 8.8 Reliability test plan

1. Retry same idem_key → +1 once.  
2. Kill flusher → approx loss within bound.  
3. Split hot key → QPS spreads; Get correct sum.  
4. Failover Redis → exact mode behavior documented.  
5. Reset + incr race → generation wins.  
6. Multi-region merge PN → convergent value.

### 8.9 Observability SLOs

| SLO | Example |
|-----|---------|
| Incr p99 (exact) | < 50ms |
| Incr p99 (approx) | < 10ms |
| Get p99 hot | < 20ms |
| Approx loss / crash | ≤ budget |
| Hot-key CPU isolation | cold key p99 intact |

### 8.10 Related systems map

```text
API → Exact / Approx paths → Striped store → Get cache
                ↓
         Idempotency store
                ↓
         Kafka → OLAP / audit
                ↓
         Hot-key controller
```

### 8.11 Error budget examples

```text
Views: ±1% monthly OK
Quota GPU-seconds: 0 loss after ACK; reconcile daily
Likes: exact via unique pair; counter is derived
```

### 8.12 Local aggregation pseudocode

```text
on Incr(key,d):
  buf[key] += d
  maybe_ryw_local[key] += d
  if should_flush(): flush()

flush():
  pipeline INCRBY for each buf entry to chosen stripe
  clear buf
```

### 8.13 Hierarchical get

```text
Level0: partials
Level1: cached sums of groups of 32
Root: cached total with TTL + version
Invalidate upward on flush (rate-limited)
```

### 8.14 Fairness checklist

- [ ] Hot-key detection  
- [ ] Dedicated stripes / pool  
- [ ] Per-key rate limit  
- [ ] Separate queues  
- [ ] Tenant caps  

### 8.15 NVIDIA bridge lines

- Metering GPU-seconds = exact ledger from scheduler events.  
- Telemetry event counts = approx OK.  
- Hot keys resemble popular models / viral jobs—plan striping early.

---

*End of distributed multi-user counter system design.*
