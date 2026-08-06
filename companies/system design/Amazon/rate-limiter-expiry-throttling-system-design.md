# System Design: Rate Limiter / Expiry-Based Throttling Service

> **Focus areas:** Multi-tenant API quotas · Per-customer / per-API limits · Soft vs hard throttle · Expiry windows · Token bucket / sliding window · Redis · Hot keys · Fail open/closed · Hierarchical limits · Distributed enforcement  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Amazon SDE III — practicality, reliability, efficiency, operational ownership, explicit business trade-offs  
> **Quality bar:** Correct arithmetic, split check vs settle/renew QPS, explicit invariants, owned fail-mode policy

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound a multi-tenant throttling service**—who is limited, which dimensions, soft vs hard behavior, expiry/window semantics, and what happens when the limiter itself is unhealthy. At Amazon this is the kind of shared platform service that sits beside API Gateway / ALB / service mesh and protects downstream fleets and customer contracts.

### 1.0 What this is / is not

| Dimension | **Rate limiter / expiry throttle (this doc)** | Not this |
|-----------|-----------------------------------------------|----------|
| Primary job | Real-time admit/deny with quota + expiry windows | Billing ledger / invoice truth |
| Success | Bound overshoot, low check latency, clear Retry-After | Perfect global linearizability at ms RTT |
| Clients | Internal microservices + external multi-tenant APIs | Browser cookie rate UX only |
| Failure | Explicit fail-open / fail-closed / fail-static | Silent unbounded allow |

**Amazon framing to say out loud:** “This is an admission-control platform. Billing can consume the same usage events asynchronously, but the limiter owns *real-time* decisions and failure modes.”

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who is limited? | Customer account, API key, seller/partner, IP, service principal — hierarchical | Composite keys; evaluate hierarchy |
| F2 | Per what? | Per-API / operation, per-region, per-resource class (e.g. `PutObject` vs `List*`) | Dimensioned counters |
| F3 | Soft vs hard? | Soft: warn + degrade / delayed queue; hard: 429/503 | Decision enum + headers |
| F4 | Window types? | Fixed window, sliding window, token bucket burst, absolute expiry leases | Multiple algorithms behind one API |
| F5 | Bursting? | Yes within contract; sustained rate capped | Token bucket capacity + refill |
| F6 | Expiry throttle? | Time-boxed boosts, bans, trial windows, flash-sale caps | TTL’d policy overlays |
| F7 | Response contract? | Allow/deny + remaining + reset/Retry-After + reason | Stable header / proto schema |
| F8 | Multi-tenant isolation? | Noisy neighbor cannot steal others’ hard quotas | Per-tenant keys + cell isolation for whales |
| F9 | Admin / self-service? | Temporary boosts, shadow mode, kill-switch | Versioned policy control plane |
| F10 | Observability? | Deny rates, hot keys, limiter latency, overshoot | Low-cardinality metrics + sampled traces |
| F11 | Consistency of counters? | Strong-ish in-region; global eventual with bound | Regional Redis + slice sync |
| F12 | Idempotency? | Same request_id should not double-charge quota | Reservation / settle or idempotent debit |

**MVP functional scope (lock with interviewer):**

1. Synchronous `Check` / `Acquire` on the request path: hierarchical limits (customer → API key → API/operation).
2. Support **token bucket** (burst + sustained) and **sliding window counter** (clean “N per window”) plus **lease/expiry** throttles (ban, boost, trial).
3. Soft throttle (delay / mark / secondary queue) and hard throttle (deny) as policy outcomes.
4. Return remaining, reset hints, reason codes; emit usage events for analytics/billing.
5. Regional Redis-backed enforcement; config from a versioned control plane.
6. Explicit fail-closed / fail-static policy; never unbounded fail-open.
7. Hot-key protection for celebrity customers / viral APIs.

**Out of MVP (explicitly defer):**

- Perfect globally synchronous counters with <5ms cross-region RTT
- Complex auction / dynamic pricing of spare capacity (mention as adjacent)
- Full WAF / bot detection (edge complement, not core)
- Exactly-once billing without a separate ledger + reconciliation

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Check latency? | On admit path | p50 < 2ms in-AZ, p99 < 10ms |
| N2 | Accuracy / overshoot? | May slightly over-admit under partitions | Bound ε (e.g. ≤5–15% short windows) |
| N3 | Availability? | Limiter outage policy explicit | Prefer fail-closed for abuse/cost; document enterprise fail-static |
| N4 | Throughput? | See scale table — **check QPS** primary | Split check / renew / config |
| N5 | Multi-AZ / multi-region? | Yes | Regional hard enforce + global soft/hard via slices |
| N6 | Efficiency? | Minimize Redis RTTs and fanout | Lua / pipeline; local slices at 100× |
| N7 | Operability / ownership? | Clear on-call story | Shadow mode, canary enforce, kill-switch |
| N8 | Fairness under overload? | Protect small customers when shared capacity tight | Weighted shed; hard contracts first |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Request → AuthN identity → hierarchical Check → allow → downstream → (optional) settle/complete.
2. Burst within bucket → allow; sustained over refill → hard 429 with Retry-After.
3. Soft-throttle tier → allow with `X-Amzn-Throttle: soft` and longer queue / lower priority.
4. Time-boxed boost expires → overlay TTL ends → base policy resumes without deploy.
5. Admin kill-switch → deny reason `ban` within seconds via policy pub/sub.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Clock skew across limiter nodes | Use Redis `TIME` / server epoch for refill; don’t trust client clocks |
| Duplicate Check with same `request_id` | Return same decision/reservation within TTL |
| Acquire succeeds, caller dies | Lease TTL restores tokens / concurrency |
| Redis shard hot key (whale customer) | Local slices, sharded counters, dedicated cell |
| Region partition from global coordinator | Enforce regional slices; freeze growth; bound overshoot ε |
| Soft→hard transition mid-burst | Policy version stamped on decision; next check sees new version |
| Config push zeros limits by bug | Guardrails reject non-positive; last-known-good retained |
| Fail-open debate | Product: free/abuse fail-closed; enterprise fail-static with hard ceiling |
| Flash sale / Prime Day spike | Pre-split slices; shadow→canary; dedicated whale cells |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Customers / tenants | 100K | 1M | 10M | 100M |
| API keys / principals | 1M | 10M | 100M | 1B |
| Distinct APIs / ops with limits | 500 | 2K | 10K | 50K |
| Peak **check QPS** | 100K | 1M | 10M | **100M** |
| Peak soft-throttle decisions | 10K | 100K | 1M | 10M |
| Distinct hot keys / min | 20K | 100K | 500K | 2M |
| Config / policy updates / day | 5K | 50K | 500K | 5M |
| Regions | 3 | 5 | 8 | 15+ |
| Limiter cells | 1/region | few | many | many per region |

**What each jump forces:**

- **10×:** Redis Cluster; Lua atomic multi-dimension checks; identity/policy caches; shadow mode.
- **100×:** Hybrid local + regional slices; Kafka/Kinesis usage bus; hot-key cells; global coordinator.
- **1,000×:** Cell-based limiter fleets, approximate global aggregation, edge/API-GW coarse filters, dedicated whale tenancy.

### 1.5 Etc. (Constraints & Assumptions)

- Limiter sits **beside or behind** API Gateway / service mesh admit — before expensive downstream work.
- Identity already resolved (or cached) to customer + key + operation.
- We design the **throttling subsystem**, not full IAM or billing.
- Amazon interview signal: own the operational failure modes and cost/efficiency story, not just algorithms.

**Scope statement:**

> Design a distributed, multi-tenant rate limiting and expiry-based throttling service enforcing hierarchical per-customer / per-API soft and hard limits with token-bucket and sliding-window semantics, regional Redis enforcement plus global budget slices, explicit fail-open/closed/static policy, and hot-key isolation—baseline ~100K check QPS scaling to ~100M.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 1,000× | Notes |
|-------|------|----------|--------|-------|
| **Check / acquire** | Sync admit path | 100K/s | 100M/s | Latency-critical |
| **Complete / settle** | Optional release / actual cost | 80K/s | 80M/s | Slightly async OK |
| **Lease renew** | Long-held concurrency / leases | ~20K/s | ~20M/s | Optional |
| **Config watch** | Policy versions | low | still ≪ checks | Pub/sub |
| **Global slice sync** | Cross-region deltas | ~2–10K/s | ~0.2–2M/s | Batched |

**Anti-pattern:** quoting one “100K QPS” without separating check, renew, and config planes.

### 2.2 Redis ops math

```text
Naive hierarchical check: customer + key + API = 3 dimensions
Each dimension: refill + debit (Lua) → aim for 1 RTT via single Lua script

100K checks/s × 1 RTT Lua ≈ 100K scripts/s → multi-shard Redis Cluster feasible
100M × 1 = 100M scripts/s → hybrid local slices mandatory; pure central Redis fantasy

Pipeline independent dimensions carefully; hierarchical fail-fast can skip work after first deny
```

### 2.3 State size

```text
Per key state: ~64–128 B (tokens, ts, window counters, soft flags)
1M active keys → ~100 MB
100M active keys → ~10–12 GB (+ replicas) — shard by key hash; TTL idle keys
Policy overlays (boost/ban): TTL’d keys; small relative to counters
```

### 2.4 Overshoot / slice uncertainty

```text
Node-local debit with sync every 50ms
If one customer drives 20K QPS and sync lag = 50ms → ~1,000 request uncertainty
At hierarchical depth 3, worst-case overshoot stacks unless slices are sized with headroom

Design: sum(regional_slices) ≤ global_cap × (1 + ε); ε e.g. 5–10%
```

### 2.5 Soft-throttle economics

```text
Soft throttle is not free: delayed work still consumes queue memory + worker time
Cap soft-admitted outstanding work per customer (concurrency lease), else soft becomes DoS
```

### 2.6 Hot key extreme

```text
1 customer = 15% of 100M checks/s → 15M checks/s on few keys
Single Redis hash slot melts at ~O(100K–few 100K) Lua/s (order-of-magnitude, HW-dependent)
→ local hybrid + sharded counters + dedicated cell required
```

### 2.7 Storage & network (efficiency)

```text
Response headers ~200–400 B; prefer proto for internal mesh to cut bytes
Cross-region sync must be batched deltas, not per-check — efficiency Leadership Principle signal
```

---

## 3. High-Level Design

### 3.1 Where it sits

```text
Client → API Gateway / Mesh → AuthN/Z → [Throttle / Rate Limit SVC] → Downstream service
                                         ↘ hard deny 429/503
                                         ↘ soft: mark / delay / low-priority queue

Control plane: Policy CFG (versions) → Limiter pods (watch)
Data plane: Redis Cluster (buckets) + optional Global Coordinator (slices)
Usage: decisions/events → Kinesis/Kafka → metrics, billing hooks, anomaly
```

### 3.2 Limit dimensions & hierarchy

```text
Key examples:
  tb:rpm:cust:{c}:api:{op}
  tb:rpm:key:{k}:api:{op}
  sw:req:cust:{c}:api:{op}:{window}
  lease:conc:cust:{c}:api:{op}
  overlay:boost:cust:{c}:api:{op}     # TTL expiry throttle overlay
  overlay:ban:cust:{c}                # TTL ban
  slice:{region}:cust:{c}:api:{op}
```

**Hierarchical evaluation order (typical Amazon multi-tenant API):**

1. Kill-switch / ban overlay  
2. Account / customer hard limits  
3. API key / principal limits  
4. Per-API / operation limits  
5. Regional / cell capacity fair-share (optional)  
6. IP / edge abuse (parallel, often at GW)

Deny/soft on first failing dimension (MVP fail-fast). Optionally evaluate all for richer headers (costlier).

### 3.3 Algorithms (trade-off table)

| Algorithm | Pros | Cons | Best for |
|-----------|------|------|----------|
| **Fixed window** | Simple | Boundary burst ≈ 2× | Coarse analytics |
| **Sliding window log** | Accurate | Memory heavy | Low cardinality |
| **Sliding window counter** | Good approx, cheap | Approximation error | “N requests / window” contracts |
| **Token bucket (chosen default)** | Burst + sustained clear | Refill care; clock source | API quotas, TPS/TPM-like |
| **Leaky bucket** | Smooth egress | Less intuitive burst | Gateway shaping |
| **Concurrency lease** | Exact in-flight | Needs reliable release/TTL | Soft queues, expensive ops |
| **Absolute expiry overlay** | Simple boosts/bans | Must compose with base | Trials, incidents, flash events |

**Choice:**

- **Default sustained + burst:** token bucket via Redis Lua.  
- **Strict contractual windows:** sliding window counter.  
- **Soft throttle concurrency:** atomic incr with TTL lease + explicit release.  
- **Expiry throttles:** TTL’d overlay keys composed at check time.

### 3.4 Soft vs hard throttle

| Mode | Semantics | Downstream effect | When |
|------|-----------|-------------------|------|
| **Hard** | Deny now | 429/503 + Retry-After | Contract ceiling, abuse, free tier |
| **Soft** | Allow with mark | Lower priority queue, added delay, degraded feature | Good customers near limit; protect fleet |
| **Shadow** | Compute only | Metrics; no enforce | Rollouts |
| **Fail-static** | Local ceiling | Degraded enforce | Limiter store unhealthy |

**Deal-breakers:**

- Soft without a concurrency/outstanding cap → turns into unbounded load.  
- Hard deny without Retry-After / reason → support nightmare; ownership fail.  
- Soft that silently drops correctness requirements (payments) — product must opt-in per API class.

### 3.5 Expiry-based throttling

```text
Base policy (versioned, long-lived)
  ⊕ Overlay(boost|ban|trial|event) with absolute expiry / TTL
  ⊕ Emergency kill-switch (pub/sub, short TTL heartbeat)

Check uses effective_limit = f(base, overlays)
When overlay expires, next Check naturally sees base — no deploy required
```

| Overlay type | Example | Storage |
|--------------|---------|---------|
| Boost | +50% TPS for 2h during incident mitigation | `overlay:boost:*` TTL |
| Ban | Block key for 15m after abuse signal | `overlay:ban:*` TTL |
| Trial | New seller 100 TPS for 7 days | TTL or absolute `exp_ms` |
| Event cap | Flash sale SKU API 5K TPS until `T_end` | absolute expiry |

### 3.6 Redis vs local+global hybrid

| Approach | How | Pros | Cons | When |
|----------|-----|------|------|------|
| **A. Redis-only sync** | Every check hits Redis Lua | Simple accuracy | Hot keys; 1000× hard | Baseline–10× |
| **B. Local only** | Per-node counters | Fast | Wrong under multi-node | Single node / edge coarse |
| **C. Hybrid (chosen at 100×+)** | Local buckets refilled from regional slices | Scale | Overshoot control | High QPS |
| **D. Edge approximate** | GW/WAF coarse RPM | Absorbs L7 junk | Weak for hierarchical contracts | Supplement |

**Choice:** Redis Lua baseline; evolve to **hybrid slices** before 1000×. Edge coarse filter is additive, not a substitute for tenant contracts.

### 3.7 Regional + global coordination

```text
Global Coordinator (per cell / API class)
  └── allocates budget slices → Regional Limiters (Redis)
         └── (100×+) node-local caches from regional slice

Usage deltas → Regional aggregators → Global (batched 100ms–1s)
```

| Cap type | Enforcement | Sync |
|----------|-------------|------|
| Regional TPS/window | Hard in-region | Redis strong-ish |
| Global customer contract | Soft/hard via slices | Batch 100ms–1s |
| Emergency kill | Hard push | Pub/sub seconds |

**Overshoot invariant:** `sum(regional_slices) ≤ global_cap × (1 + ε)`.

### 3.8 Fail open vs fail closed

| Mode | Behavior | Use |
|------|----------|-----|
| **Fail closed** | On store error → 429/503 | Abuse-prone, free tier, cost control |
| **Fail open** | Allow freely | **Avoid unbounded** — Amazon reliability trap |
| **Fail static** | Cached policy + local ceiling | Enterprise availability compromise |

**Resolved policy (defend this):**

- Default **fail-closed** on Redis errors for Check/Acquire.  
- Enterprise may **fail-static** with `ceiling = min(last_known, contract_burst)` — never unbounded open.  
- Completes/settles can queue; concurrency soft-leaks until sweeper — bound with TTLs.  
- Document per API class (checkout vs browse) — ownership means product-signed matrix.

### 3.9 Fairness vs efficiency

| Strategy | Idea | Trade-off |
|----------|------|-----------|
| Pure hard quotas | Isolation | Unused capacity idle |
| Work-conserving spare | Reallocate idle slices | Utilization ↑; gaming risk |
| Weighted shed under overload | Protect small tenants | Complexity |

**Choice:** hard contracts + optional work-conserving spare; under cell overload, weighted soft→hard shed.

### 3.10 API / check interface

```http
POST /internal/v1/throttle/check
{
  "request_id": "req_...",
  "identity": {"customer_id":"...","api_key_id":"...","principal":"..."},
  "api": "Orders.Create",
  "cost": 1,
  "mode_hint": "standard"
}

→ 200 {
  "decision": "allow",            // allow | soft | deny
  "reservation_id": "rsv_...",
  "policy_version": 184422,
  "limits": {
    "customer_tps": {"remaining": 420, "reset_ms": 800},
    "key_tps": {"remaining": 80, "reset_ms": 800},
    "api_window": {"remaining": 900, "reset_ms": 12000}
  },
  "soft": {"delay_ms": 0, "priority": "normal"}
}

→ 429 {
  "decision": "deny",
  "reason": "customer_tps",
  "retry_after_ms": 250,
  ...
}
```

```http
POST /internal/v1/throttle/complete
{
  "request_id": "req_...",
  "reservation_id": "rsv_...",
  "status": "success",            // success | cancel | error
  "actual_cost": 1
}
```

### 3.11 Hot keys

Layered mitigations:

1. **Regional keys** already split celebrity load.  
2. **Local hybrid slices** so Redis isn’t hit every check.  
3. **Sharded counters** `...:{0..N-1}` with careful aggregation.  
4. **Coalesce** debits in 5–10ms node windows for mega tenants.  
5. **Dedicated limiter cell** for top talkers (Prime Day whales).  
6. **Cache deny** briefly when remaining=0 (invalidate on boost/reset).

### 3.12 Why X over Y (Amazon decision table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Algorithm default | Token bucket + SW counter | Burst + contractual windows | Fixed window only for paid contracts |
| Store | Redis Cluster + Lua | Latency + atomic multi-key dims | Per-check SQL updates |
| Soft throttle | Mark + capped concurrency | Protect fleet without instant 429 | Soft without outstanding cap |
| Global sync | Slices + ε | Honesty about RTT | Sync global on every check |
| Failure | Fail-closed / fail-static | Reliability + cost ownership | Unbounded fail-open |
| Rollout | Shadow → canary → enforce | Operational ownership | Big-bang quota cut |

---

## 4. Architecture Diagram

### 4.1 System context

```text
+----------+     +---------------+     +-------------------+     +-------------+
| Clients  |---->| API GW / Mesh |---->| Throttle Service  |---->| Downstream  |
+----------+     +---------------+     | (regional pods)   |     +-------------+
                                       +---------+---------+
                                                 |
               +---------------------------------+---------------------------------+
               v                                 v                                 v
        +--------------+                 +---------------+                 +----------------+
        | Redis Cluster|                 | Policy CFG    |                 | Global Coord   |
        | buckets/TTL  |                 | versions/ACL  |                 | slices/ε       |
        +--------------+                 +---------------+                 +----------------+
               ^
               | complete / usage
        +------+-------+
        | Kinesis/Bus  |
        +--------------+
```

### 4.2 Check sequence

```text
GW/Mesh            ThrottleSvc           Redis              Global(opt)
 |--check---------->|                      |                    |
 |                  |--policy (mem/LRU)--->|                    |
 |                  |--Lua acquire-------->|                    |
 |                  |<--allow/soft/deny----|                    |
 |                  |--(async) usage--------------------------->|
 |<--200/429--------|                      |                    |
```

### 4.3 Soft-throttle path

```text
Check → decision=soft → Mesh marks request → Priority queue / delayed executor
                     → concurrency lease held until Complete or TTL
```

### 4.4 Hybrid local refill (100×+)

```text
Node local bucket (customer, api)
  refill from Regional Redis slice every T ms
Regional Redis slice
  adjust from Global Coordinator every U ms
```

### 4.5 Expiry overlay composition

```text
effective = base_policy[version]
if overlay.ban active (now < exp): DENY(ban)
if overlay.boost active: limit *= boost.factor
if overlay.event_cap active: limit = min(limit, event_cap)
then run token-bucket / sliding-window against effective
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Idempotent Check** for same `request_id` within reservation TTL.  
2. **Idempotent Complete** — at-most-once economic effect per `request_id`.  
3. **Reservation / concurrency TTL** — always reclaim; no permanent leaks.  
4. **No unbounded fail-open.**  
5. **Policy version monotonic** — decisions stamp `policy_version`.  
6. **Overshoot bounded** by slice math (document ε).  
7. **Deny / soft must not require cross-region RTT on hot path.**  
8. **Soft outstanding capped** per customer/API.  
9. **Guardrails** reject non-positive limits and accidental zeroing.

#### 5.1.2 Lua acquire sketch (conceptual)

```lua
-- compose overlays → effective limits
-- refill token bucket using redis TIME
-- sliding window counter update
-- if hard exceeded → DENY
-- if soft band → ALLOW_SOFT + incr lease
-- else ALLOW + debit
-- SET reservation {request_id} with PEXPIRE
```

#### 5.1.3 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Redis blip | Fail-closed / fail-static matrix |
| 10× | Hot customer key | Regional keys + deny cache |
| 100× | Global coordinator lag | Freeze slice growth; regional hard caps |
| 1,000× | Meta-QPS from retries | Retry-After + jitter; edge coarse RPM |

#### 5.1.4 Retries & client contract

- Clients honor `Retry-After` with jitter (ownership: publish SDK guidance).  
- Distinguish `soft` (may proceed degraded) vs `deny` (must back off).  
- Hedged retries without idempotency keys double-debit — require `request_id`.

#### 5.1.5 Data loss / correctness

| Path | Risk | Mitigation |
|------|------|------------|
| Lost Complete | Capacity stuck | Lease TTL sweeper |
| Double Complete | Over-admit | `settled:{request_id}` flag |
| Lost Check after allow | Downstream ran | OK; Complete optional for cost=1 RPM |
| Policy lost | Wrong limits | Last-known-good; alert; never empty |

### 5.2 Scalability

#### 5.2.1 Progressive architecture

| Scale | Architecture |
|-------|--------------|
| **1×** | Regional Redis Lua; hierarchy; soft/hard; TTL overlays; fail-closed |
| **10×** | Redis Cluster; policy cache; shadow; metrics cardinality discipline |
| **100×** | Hybrid local slices; usage bus; hot-key cells; global coordinator |
| **1,000×** | Multi-cell fleets; approximate global; edge coarse; whale tenancy |

#### 5.2.2 Sharding strategy

- Shard Redis by hash of limit key (customer/api).  
- Avoid single key for global “platform TPS” — use hierarchical aggregation / approximate.  
- Cell by tenant hash or API class at 100×+.

#### 5.2.3 Efficiency levers (Amazon signal)

- 1 RTT Lua vs chatty GET/SET.  
- Fail-fast hierarchy.  
- Local deny cache when remaining=0.  
- Batch global sync.  
- Internal protobuf > verbose JSON headers on mesh.

### 5.3 Maintainability / operability

#### 5.3.1 Control plane

- Versioned policies in DynamoDB / S3+CDN + push via pub/sub.  
- Shadow → canary → enforce playbook.  
- Kill-switch with dual-publish rollback.  
- Config guardrails + approval for massive cuts.

#### 5.3.2 Observability

| Signal | Why |
|--------|-----|
| `decision_allow/soft/deny` by api class (low card) | Product health |
| `check_latency_p99` | Path budget |
| `redis_error_rate` | Fail-mode trigger |
| `overshoot_estimate` | Slice honesty |
| `hot_key_score` | Cell isolation trigger |
| `policy_version_lag` | Push health |

Avoid per-customer metric labels at high cardinality — sample / top-K.

#### 5.3.3 Ownership narrative

- On-call owns fail-mode matrix and Prime Day runbooks.  
- SLO: check p99, error rate, overshoot ε, deny correctness under chaos.  
- Load-test hot keys and partition from global coordinator before peak events.

### 5.4 Consistency model

| Scope | Model |
|-------|-------|
| Single Redis key / Lua | Atomic |
| In-region multi-key hierarchy | Atomic in one script when co-located / hashed together carefully |
| Cross-region | Eventual via slices; bounded ε |
| Policy | Monotonic versions; brief dual-running OK in shadow |

**Do not claim** linearizable global TPS.

### 5.5 Security & abuse

- Authenticate internal Check API (mTLS).  
- Prevent customers from forging identity dimensions.  
- Edge RPM before auth DB to stop credential stuffing cost.  
- Ban overlays from trusted abuse pipeline only.  
- Audit policy changes.

### 5.6 Multi-AZ / multi-region

- Redis with Multi-AZ / cluster replicas; limiter pods in ≥3 AZs.  
- Prefer in-AZ Redis affinity for p99.  
- Region hard enforce; global contract via coordinator.  
- AZ failure: pods + Redis failover; fail-static if store unavailable beyond budget.

---

## 6. Wrap-Up

### 6.1 Amazon narrative (60–90s)

> “I’d clarify hierarchy (customer → key → API), soft vs hard outcomes, and fail-mode policy first—especially that we never unbounded fail-open. I’d estimate check QPS separately from completes and sync traffic. HLD: regional Throttle service with Redis Lua token buckets and sliding windows, TTL overlays for expiry boosts/bans, hierarchical evaluation, and soft throttle with capped concurrency. Global contracts use budget slices with an explicit overshoot ε—not a cross-region lock on the hot path. At 100× we go hybrid local+Redis and isolate whale keys into cells. Operability is part of the design: shadow→canary→enforce, kill-switch, and a signed fail-closed/fail-static matrix by API class.”

### 6.2 Decision summary

| Area | Decision |
|------|----------|
| Algorithms | Token bucket default; sliding window for strict windows; leases for soft/conc |
| Storage | Redis Cluster + Lua; hybrid slices at 100× |
| Hierarchy | Customer → key → API; fail-fast |
| Soft/hard | Policy outcomes; soft capped |
| Expiry | TTL/absolute overlays composed at check |
| Failure | Fail-closed default; enterprise fail-static ceiling |
| Scale path | Cluster → hybrid → cells / whales |

### 6.3 What interviewers listen for

- Practical soft vs hard semantics (not buzzwords).  
- Honest global consistency + ε.  
- Hot keys and Prime Day ownership.  
- Fail-mode matrix with product buy-in.  
- Efficiency (RTT, cardinality, sync batching).

---

## 7. Deeper / Related Interview Questions

### 7.1 Algorithms

**Q1: Token bucket vs sliding window — when each?**  
A: Bucket for burst+sustained TPS; sliding window when contract is “N per calendar/window” with less boundary abuse than fixed window.

**Q2: Why not fixed window alone?**  
A: Boundary burst up to ~2×; bad for paid fairness optics.

**Q3: How do you compute Retry-After for token bucket?**  
A: `(need - tokens) / refill_rate`, ceil to ms; use server time.

**Q4: Sliding window counter approximation error?**  
A: Weighted previous+current buckets; document bound; OK for many API contracts.

**Q5: Leaky vs token bucket?**  
A: Leaky smooths egress; token bucket matches API burst mental model better.

**Q6: Cost field > 1?**  
A: Batch/bulk APIs debit `cost`; reserve ≥ cost; soft bands scale with cost.

**Q7: Concurrent requests racing the same key?**  
A: Lua atomicity; without Lua, optimistic CAS loops under contention.

**Q8: Why Redis TIME?**  
A: Avoid multi-node wall-clock skew breaking refill.

### 7.2 Hierarchy & multi-tenant

**Q9: Evaluate all dimensions or fail-fast?**  
A: Fail-fast cheaper; evaluate-all richer headers — pick per latency budget.

**Q10: Noisy API key inside a customer?**  
A: Per-key limits inside customer; customer cap still protects platform.

**Q11: Shared platform capacity vs customer contracts?**  
A: Contracts hard; optional weighted fair for spare/overload.

**Q12: Cross-API fair share for one customer?**  
A: Optional parent budget; careful not to serialize unrelated APIs unnecessarily.

**Q13: Multi-tenant Redis isolation?**  
A: Key prefixes + cell isolation for whales; ACL for control plane.

### 7.3 Soft vs hard

**Q14: Is soft throttle just a warning header?**  
A: No—must change admission (delay/priority/concurrency) or it’s theater.

**Q15: When is soft inappropriate?**  
A: Payments / inventory mutate paths that need hard admission clarity.

**Q16: Soft→hard flapping?**  
A: Hysteresis bands; sticky soft for short TTL; versioned policy.

**Q17: How does soft interact with autoscaling?**  
A: Soft absorbs spikes; if soft queue depth high, scale + tighten soft band.

### 7.4 Expiry overlays

**Q18: Boost expires mid-request?**  
A: Decision stamped at Check; in-flight OK; next Check uses new effective limit.

**Q19: Absolute vs TTL expiry?**  
A: TTL simple; absolute needed for aligned event ends across regions.

**Q20: Clock skew on absolute expiry?**  
A: Coordinator issues `exp_ms` from trusted clock; store compares Redis TIME.

**Q21: Overlay storm (millions of bans)?**  
A: Shard overlay keys; bloom/approximate deny cache at edge for IP bans.

### 7.5 Fail modes

**Q22: Redis down — what do you do?**  
A: Fail-closed default; enterprise fail-static with ceiling; never infinite allow.

**Q23: Why is unbounded fail-open a deal-breaker?**  
A: Downstream melt + cost blowup; violates reliability ownership.

**Q24: Global coordinator down?**  
A: Hold last slices; freeze growth; regional hard caps remain.

**Q25: Partial Redis cluster failure?**  
A: Only affected hash slots degrade; others healthy; avoid global fail-open.

**Q26: Poison Lua deploy?**  
A: Versioned scripts; canary; instant rollback; shadow compare.

### 7.6 Hot keys & performance

**Q27: Hashing doesn’t fix celebrity customers — why?**  
A: Popularity is Zipfian on tenant keys, not uniform on hash space.

**Q28: Local deny cache risks?**  
A: Stale allow after boost — bound TTL and invalidate on policy version.

**Q29: Pipelining vs Lua?**  
A: Lua for atomic multi-dimension; pipeline for independent abuse IP checks.

**Q30: Meta-retry storms after mass 429?**  
A: Retry-After + jitter; SDK defaults; edge shed.

**Q31: Dedicated whale cell criteria?**  
A: Top-K by check QPS / deny errors / revenue-critical launches.

### 7.7 Global / multi-region

**Q32: Strong global TPS at ms latency?**  
A: Not honestly worldwide; use slices + ε.

**Q33: Active-active limiters?**  
A: Yes regionally; global coordination is soft state.

**Q34: Customer pinned to region?**  
A: Improves accuracy; multi-region traffic needs slice split by share.

**Q35: How to test overshoot under partition?**  
A: Chaos: cut coordinator; measure excess vs ε; verify freeze behavior.

### 7.8 Product / Amazon leadership

**Q36: How do you roll out a 50% quota cut?**  
A: Shadow → canary → widen; watch support + error budgets; fast rollback version.

**Q37: Bias for action vs measuring twice?**  
A: Shadow mode lets you move fast without customer pain.

**Q38: Frugality / efficiency?**  
A: Minimize RTTs; batch sync; low-card metrics; edge coarse filter.

**Q39: Customer obsession on 429s?**  
A: Clear reasons, Retry-After, soft path where safe, self-service boosts.

**Q40: Who owns the fail-mode matrix?**  
A: Limiter service + API product owners sign per API class.

### 7.9 Comparison traps

**Q41: Is Envoy/GW rate limit enough?**  
A: Good for coarse RPM/IP; multi-tenant hierarchical soft/hard + overlays + global slices need domain service.

**Q42: Same as billing?**  
A: No—billing is append-only actuals; limiter is real-time admission.

**Q43: Same as concurrency control in DB?**  
A: Different — this is distributed quota across fleets.

**Q44: Guava/local RateLimiter?**  
A: Fine single node; wrong for multi-tenant distributed contracts.

### 7.10 Extra interviewer traps (high value)

- What’s the difference between soft throttle and fail-open?  
- How do you reclaim capacity if the caller dies after allow?  
- Why is global sync not on the check path?  
- What’s your overshoot bound and how derived?  
- How do hot keys break Redis Cluster hash slots?  
- Soft without outstanding cap — why fatal?  
- How do expiry overlays compose with hierarchical hard limits?  
- Which dimension drives Retry-After when several trip?  
- How do you prevent config push from zeroing production limits?  
- What changes at 100M check QPS that Redis-only can’t solve?  
- How do you keep metrics from melting Prometheus with per-customer labels?  
- Sliding window vs token bucket for seller Partner API contracts?  
- How do you handle leap seconds / large time steps?  
- What’s the blast radius of a bad deny-all policy?  
- How does this interact with idempotent client retries?  
- AZ vs region failure: different playbooks?  
- When would you choose DynamoDB atomic counters instead of Redis? (hint: usually won’t for this QPS)  
- How do you load-test Prime Day without harming prod?  
- Exact semantics of `cost` for batched APIs?  
- How do you explain ε overshoot to a business partner?

### 7.11 Related designs

**Q45: LLM TPM limiter?**  
A: Same bones + reserve/settle for streaming tokens.  
**Q46: Inventory hold?**  
A: Different — reservation against stock SoT, not TPS.  
**Q47: WAF bot limits?**  
A: Edge complement; weaker identity; higher false soft.

---

## Appendices

### Appendix A — Redis key schema

```text
pol:ver                                   # policy version hint
tb:rpm:{scope}:{id}:api:{op}              # hash: tokens, ts_ms
sw:{scope}:{id}:api:{op}:{win}            # hash: prev_count, curr_count, win_start
lease:conc:{scope}:{id}:api:{op}          # int + PEXPIRE
rsv:{request_id}                          # hash: debits, decision, exp
settled:{request_id}                      # flag TTL
overlay:boost:{scope}:{id}:api:{op}       # hash: factor, exp_ms
overlay:ban:{scope}:{id}                  # flag TTL / exp_ms
slice:{region}:{scope}:{id}:api:{op}      # regional slice budget
deny_cache:{key}                          # short TTL local/redis
```

### Appendix B — Lua acquire pseudocode

```text
function acquire(keys, cost, request_id):
  if EXISTS ban_overlay: return DENY("ban")
  effective = apply_boost(base_limits)
  refill_tb(tb_key, now)
  update_sliding(sw_key, now)
  if hard_exceeded(effective, cost): return DENY(reason)
  if in_soft_band(effective, cost):
     if conc = INCR(lease) > soft_conc_max: DECR; return DENY("soft_cap")
     SET rsv...; return SOFT
  debit tb/sw by cost
  SET rsv...; return ALLOW
```

### Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Redis Lua TB+SW, hierarchy, soft/hard, TTL overlays, fail-closed, headers |
| 10× | Cluster, policy cache, shadow, metrics discipline, Multi-AZ |
| 100× | Hybrid slices, usage bus, hot-key cells, global coordinator |
| 1,000× | Multi-cell, approximate global, edge coarse, whale tenancy |

### Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Soft throttle | Admit with degradation / delay / lower priority |
| Hard throttle | Deny (429/503) |
| Overlay | Time-bounded policy modifier (boost/ban/event) |
| Slice | Regional allocation of a global budget |
| Fail-static | Degraded local enforce with ceiling |
| Overshoot ε | Allowed temporary global exceedance |
| Hot key | Disproportionate traffic on few Redis keys |
| Lease | TTL’d concurrency / reservation hold |
| Work-conserving | Reallocate unused capacity |

### Appendix E — Estimation cheat-sheet

```text
check_QPS ≠ complete_QPS ≠ renew_QPS ≠ sync_QPS
redis_scripts ≈ check_QPS   (Lua 1 RTT target)
state_bytes ≈ active_keys × 128 B
local_uncertainty ≈ local_QPS × sync_interval
sum(slices) ≤ global_cap × (1+ε)
100M check/s → hybrid + cells mandatory
```

### Appendix F — Worked numeric examples

#### F.1 Token bucket refill

```text
Customer TPS limit: 5_000/s, burst 20_000
refill = 5000 tokens/s; capacity = 20000
Request cost 1 at tokens=100 → retry_after ≈ (1-100)? allow : ...
If tokens=0: retry_after ≈ 1/5000 s = 0.2 ms → practically ms ceil + jitter
```

#### F.2 Regional slices

```text
Global customer cap G = 1_000_000 req/min
Regions us-east 50%, eu 30%, apac 20% → slices 500K / 300K / 200K per min
ε = 5% → sum ≤ 1.05M
Coordinator down → freeze at last slices; no growth
```

#### F.3 Soft band

```text
Hard 5000 TPS; soft starts at 80% = 4000 TPS
Between 4000–5000: ALLOW_SOFT with delay_ms = f(utilization), conc_max=200
Above 5000: DENY
Without conc_max, soft queue grows without bound under retry storms
```

#### F.4 Hot-key math

```text
Whale 2M check/s; single Lua key ~O(100–300K)/s ⇒ need ≥10× local/regional split
Prime Day: pre-create whale cell and pin top sellers
```

### Appendix G — Decision header contract

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 1
X-Amzn-Throttle-Decision: deny
X-Amzn-RequestId: req_...
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1710000012
X-RateLimit-Reason: customer_tps
X-Amzn-Policy-Version: 184422
```

When soft:

```http
HTTP/1.1 200 OK
X-Amzn-Throttle-Decision: soft
X-Amzn-Throttle-DelayMs: 35
X-Amzn-Throttle-Priority: low
```

Authoritative `Retry-After` = soonest reset that clears the denying dimension.

### Appendix H — Policy rollout playbook

1. **Shadow:** compute + metrics only.  
2. **Canary enforce:** 1% keys / 1% traffic.  
3. **Widen** watching deny_ratio, latency, tickets, revenue-critical paths.  
4. **Emergency kill-switch:** pub/sub ban/freeze with version bump.  
5. **Rollback:** prior `policy_version` dual-published ≤ T seconds.

### Appendix I — Invariant test checklist

| Test | Expect |
|------|--------|
| Duplicate Complete | No double release |
| Reservation TTL | Capacity restored without Complete |
| Soft without Complete | Lease expires; outstanding drops |
| Redis error free tier | Deny/503 — not allow |
| Config zeroed by bug | Rejected by guardrails |
| Cross-region partition | Overshoot ≤ ε for window |
| Overlay expiry | Base limits resume next Check |
| Hot key cell move | No thundering reconnect |

### Appendix J — Fail-mode matrix (sign with product)

| API class | Redis errors | Coordinator down | Notes |
|-----------|--------------|------------------|-------|
| Browse / search | Fail-static ceiling | Hold slices | Availability bias |
| Cart add | Fail-static tight | Hold | |
| Checkout / pay | Fail-closed | Hold + alert | Correctness/cost bias |
| Partner bulk ingest | Fail-closed | Hold | Abuse/cost |
| Internal health | Allowlist bypass | n/a | Carefully gated |

### Appendix K — Soft throttle executor sketch

```text
on SoftDecision(req):
  enqueue(priority=low, not_before=now+delay_ms)
  hold lease until handler Complete or TTL
worker:
  pull when due → call downstream → Complete(success|error)
overflow:
  if queue_depth > max: convert new soft to DENY (shed)
```

### Appendix L — Sliding window counter sketch

```text
win = floor(now / W)
weight = (now % W) / W
effective = prev_count * (1 - weight) + curr_count
if win != stored_win: prev=curr; curr=0; stored_win=win
if effective + cost > limit: DENY else curr += cost
```

### Appendix M — Observability red flags

| Signal | Meaning |
|--------|---------|
| deny_ratio ↑ all tenants | Bad policy / shared outage |
| check_p99 ↑ | Redis/hot key / GC |
| redis_error ↑ | Fail-mode engaged |
| soft_queue_depth ↑ | Soft absorbing; may need scale/shed |
| policy_version_lag ↑ | Push broken |
| overshoot > ε | Slice bug / coordinator lag |

### Appendix N — Deal-breaker catalog

| Choice | Deal-breaker when |
|--------|-------------------|
| Unbounded fail-open | Any cost/abuse-sensitive API |
| Soft w/o outstanding cap | Incident load amplification |
| Fixed window only | Paid fairness complaints |
| Global lock on check path | p99 / multi-region |
| Per-customer Prometheus labels | Metrics meltdown |
| No Retry-After | Retry storms |
| SQL counters at 1M+ QPS | Latency + contention |

### Appendix O — 30s scale narrative

> Baseline: regional Redis Lua, hierarchical TB+SW, soft/hard, TTL overlays, fail-closed. 10× adds cluster, shadow, Multi-AZ discipline. 100× hybrid slices + whale cells + global coordinator. 1,000× multi-cell fleets, edge coarse filters, approximate global — still no cross-region lock on the hot path.

### Appendix P — Interview whiteboard order

1. Clarify hierarchy, soft/hard, fail modes, windows  
2. QPS split + Redis math  
3. HLD placement + hierarchy  
4. Algorithms + overlays  
5. Fail-open/closed/static  
6. Hot keys + slices  
7. 10×/100×/1000×  
8. Operability playbook  

### Appendix Q — Sample reason codes

| Reason | Meaning |
|--------|---------|
| `customer_tps` | Account bucket exhausted |
| `key_tps` | API key bucket |
| `api_window` | Per-operation window |
| `soft_cap` | Soft outstanding exceeded |
| `ban` | Overlay ban |
| `cell_overload` | Shared capacity shed |
| `store_unavailable` | Fail-closed path |

### Appendix R — Why Amazon flavor ≠ pure algorithm quiz

Interviewers score **clarifying questions, owned failure modes, efficiency, and progressive scale**. Naming “token bucket in Redis” without soft-cap, overlays, ε overshoot, and Prime Day hot keys is weaker than a crisp operational design with numbers.

### Appendix NFR card

```text
Check p50 < 2ms, p99 < 10ms in-AZ
Hierarchy: customer → key → API
Soft capped + hard deny
TTL/absolute expiry overlays
sum(slices) ≤ global×(1+ε)
Fail-closed / fail-static — never unbounded open
Hot-key playbook mandatory
Shadow → canary → enforce
```

---

*End of design doc. Open with §1 hierarchy + soft/hard + fail policy; whiteboard §3 algorithms/overlays/slices; close with invariants in §5.1 and traps in §7.*
