Serving Infrastructure Throttle / Safety

> **Focus areas:** Admission control · RPM/TPM/concurrency · Token bucket · Load shed · Circuit break · SLO guardrails
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:**
> **Interview theme:** Databricks — serving safety and admission control under overload; protect dependencies and SLOs

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

Goal: **bound the product**—what dimensions we limit, how streaming tokens settle, regional vs global coordination, and failure behavior under limiter outages.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who is limited? | User, API key, org/project, model, IP (abuse) — hierarchical | Composite keys; hierarchical budgets |
| F2 | Limit dimensions? | **RPM** (requests/min), **TPM** (tokens/min in+out), **concurrency** (in-flight requests) | Separate counters/algorithms per dimension |
| F3 | Hard vs soft limits? | Hard 429 for paid tiers; soft warnings optional; free tier hard | Decision returns allow/deny + headers |
| F4 | Streaming tokens? | Output tokens unknown at admit | **Reserve** estimate → **settle** actual on completion |
| F5 | Fairness goal? | No single org monopolizes a model region; within org, fair across keys | Weighted fair share / deficit counters |
| F6 | Regional vs global? | Regional enforcement for latency; global caps for org contracts | Local decision + async/global reconciliation |
| F7 | Bursting? | Token bucket with burst; not pure hard window only | Bucket capacity + refill rate |
| F8 | Response contract? | `429` + `Retry-After` + remaining quota headers | Stable header schema; idempotent checks |
| F9 | Admin overrides? | Temporary boosts, bans, shadow mode | Config service + versioned policies |
| F10 | Observability? | Per-org deny rates, hot keys, limiter latency | Metrics without high-cardinality explosion |
| F11 | Shadow / dry-run? | Roll out new limits in observe mode | Dual-run decision without enforce |
| F12 | Billing interaction? | Limiter ≠ billing ledger; may share usage events | Append-only usage for billing separate |

**MVP functional scope (lock with interviewer):**

1. Check/allow API before inference admit: RPM + TPM (in estimate) + concurrency.
2. Return allow/deny with remaining and reset hints.
3. **Reserve** tokens at admit; **settle** on terminal (success/fail/cancel).
4. Hierarchical limits: `org → project → api_key` (+ per-model).
5. Regional limiter pods with Redis (or equivalent); config from control plane.
6. Fail-closed for free/abuse-sensitive; configurable fail-open for enterprise critically discussed.
7. Hot-key protection and basic fairness under overload.

**Out of MVP (explicitly defer):**

- Perfect globally synchronous counters with <5ms RTT worldwide (impossible honestly)
- Complex auction-based GPU scheduling (mention as adjacent)
- User-facing “buy burst credits” marketplace
- Exactly-once settle across all failure modes without reconciliation sweeper

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Check latency? | In admit path | p50 < 2ms in-region, p99 < 10ms (local/Redis) |
| N2 | Accuracy? | May slightly over-admit under partitions | Bound overshoot (e.g. ≤5–15% short windows) with reconciliation |
| N3 | Availability? | Limiter outage policy explicit | Prefer fail-closed for abuse; document enterprise exceptions |
| N4 | Throughput? | See scale table — **check QPS** primary | Split check / settle / config |
| N5 | Fairness under overload? | Proportional shares | Weighted algorithms; not pure FIFO |
| N6 | Multi-region? | Yes | Regional hard enforcement + global soft/hard sync |
| N7 | Consistency? | Not linearizable globally | Per-key strong-ish in region; global eventual |
| N8 | Safety vs revenue? | Prevent runaway cost | Over-admit bounded; never unbounded fail-open |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Request arrives → identity resolved → check RPM/TPM/concurrency → reserve → allow → inference → settle actual tokens → release concurrency.
2. Burst within bucket → allow; sustained over refill → 429 with Retry-After.
3. Org near global cap → regional limiters shed proportionally.
4. Admin boost → config version bump → limiters pick up within seconds.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Streaming 10× longer than estimate | Settle may go negative remaining; debt / throttle next requests; optional hard cancel mid-stream if policy |
| Duplicate settle | Idempotent `request_id` settle |
| Check succeeds, inference never starts | Lease TTL releases reservation + concurrency |
| Redis shard hot key (celebrity org) | Key-specific mitigations: local shard, coarse buckets, request coalescing |
| Region partition from global coordinator | Enforce regional caps; freeze global boosts; bound overshoot |
| Clock skew | Prefer Redis server time / logical epochs; don’t trust client |
| Config push fails | Last-known-good policy; alert; don’t zero limits |
| Fail-open debate | Product: free tier fail-closed; enterprise may fail-open to regional static defaults with hard ceiling |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Orgs | 10K | 100K | 1M | 10M |
| API keys | 100K | 1M | 10M | 100M |
| Peak **check QPS** | 50K | 500K | 5M | **50M** |
| Peak **settle QPS** | 40K | 400K | 4M | 40M |
| Peak concurrent in-flight requests | 20K | 200K | 2M | 20M |
| Distinct hot keys / min | 10K | 50K | 200K | 1M |
| Config updates / day | 1K | 10K | 100K | 1M |
| Regions | 2 | 3 | 5 | 10+ |
| Models with separate quotas | 10 | 20 | 50 | 100 |

**What each jump forces:**

- **10×:** Redis Cluster; pipelining; local token caches with sync; header-only path optimization.
- **100×:** Hybrid local+global; key sharding; regional coordinators; settle async batching where safe.
- **1,000×:** Hierarchical aggregation, approximate global counters (e.g. gossip/epidemic or central shards), hot-key isolation, cell-based limiter fleets, careful fail modes.

### 1.5 Etc. (Constraints & Assumptions)

- Limiter sits **in front of / beside Inference Gateway admit**.
- Inference produces actual token usage asynchronously (streaming).
- Identity from API key → org/project resolved with caching.
- We design the **rate limiter subsystem**, not full billing.

**Scope statement:**

> Design a distributed LLM API rate limiter enforcing hierarchical RPM/TPM/concurrency with reserve+settle for streaming, regional enforcement plus global caps, explicit fail-open/closed policy, and fairness under hot keys—baseline ~50K check QPS scaling to ~50M.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 1,000× | Notes |
|-------|------|----------|--------|-------|
| **Check / reserve** | Sync admit path | 50K/s | 50M/s | Latency-critical |
| **Settle / release** | Terminal usage | 40K/s | 40M/s | Can be slightly async |
| **Heartbeat concurrency refresh** | Long streams | ~10K/s | ~10M/s | Optional lease renew |
| **Config watch** | Policy updates | low | still low vs checks | Pub/sub |
| **Global sync** | Cross-region deltas | ~1–5K/s | ~0.1–1M/s | Batched |

**Anti-pattern:** treating settle as free or merging into “50K QPS” without streaming renewals.

### 2.2 Redis ops math

```text
Naive check: MULTI/EXEC with 3–6 Redis ops (RPM, TPM in, concurrency, maybe model)
50K checks/s × 4 ops ≈ 200K Redis ops/s → single well-tuned shard cluster possible
50M × 4 = 200M ops/s → many clusters + local approximation mandatory

Pipeline + Lua scripts: 1 RTT per check (good)
```

### 2.3 Token bucket state size

```text
Per key state: ~64–128 B (tokens, ts, concurrency)
100K keys → ~10 MB
100M keys → ~10 GB (+ replication) — shard by key hash; TTL idle keys
```

### 2.4 Overshoot budget

```text
Regional local cache admits with sync every 50ms
If 10K QPS on one org and sync lag 50ms → ~500 requests uncertainty
At 1K tokens reserve each → 500K tokens uncertainty — must size local slices accordingly
```

**Design:** give each regional limiter a **slice** of the global budget; refill slices from coordinator.

### 2.5 Header / response overhead

```text
Check path should be memory-only after Redis; avoid DB.
p99 10ms leaves little room for cross-region sync on the hot path — don’t.
```

### 2.6 Hot key extreme

```text
1 org = 20% of traffic at 50M checks/s → 10M checks/s on few keys
→ single Redis key melts; need key splitting (sharded counters) or local enforcement with slice
```

---

## 3. High-Level Design

### 3.1 Where it sits

```text
Client → API Gateway → AuthN/Z → [Rate Limiter] → Inference Admit → Model Serving
                              ↘ deny 429
Settle path: Inference terminal → usage event → Rate Limiter settle → (billing ledger async)
```

### 3.2 Limit dimensions & keys

```text
Key examples:
  rpm:org:{org}:model:{m}
  tpm:org:{org}:model:{m}
  conc:org:{org}:model:{m}
  rpm:key:{api_key}:model:{m}
  tpm:project:{proj}:model:{m}
```

**Hierarchical evaluation order (typical):**

1. Ban / kill-switch  
2. API key limits  
3. Project limits  
4. Org limits  
5. Global model capacity fair-share (optional)  
6. IP/abuse limits (parallel)

Deny on first failing dimension (or evaluate all for richer headers—product choice; MVP: fail-fast).

### 3.3 Algorithms (trade-off table)

| Algorithm | Pros | Cons | Best for |
|-----------|------|------|----------|
| **Fixed window** | Simple | Boundary burst 2× | Rough analytics |
| **Sliding window log** | Accurate | Memory heavy | Low cardinality |
| **Sliding window counter** | Good approx | Approximation error | RPM |
| **Token bucket (chosen for RPM/TPM)** | Burst + sustained clear | Needs careful refill | API quotas |
| **Leaky bucket** | Smooth egress | Less intuitive burst | Gateways |
| **Concurrency semaphore** | Exact in-flight | Needs reliable release | Conc limits |
| **GEDF / weighted fair** | Fairness | Complex | Shared model capacity |

**Choice:**

- **RPM / TPM:** token bucket (or sliding window counter) via Redis Lua.  
- **Concurrency:** atomic incr with TTL lease + explicit release.  
- **Global fairness:** weighted slice allocation across orgs/regions.

### 3.4 Reserve + settle (streaming)

```text
Admit:
  estimate_tokens = f(prompt_tokens, max_output_tokens, historical avg)
  reserve TPM by estimate_tokens
  incr concurrency
  if any fail → rollback and 429

In-flight (optional):
  renew concurrency lease every T seconds

Terminal:
  settle TPM: actual = input + output
  delta = actual - reserved
  apply delta (may consume more or credit back)
  decr concurrency
  idempotent on request_id
```

**Deal-breakers:**

- Charging only `max_output_tokens` without settle → chronic under-utilization or chronic over-admit.  
- No TTL on reservations → leaks permanently reduce capacity.  
- Non-idempotent settle → double release → over-admit.

### 3.5 Redis vs local+global hybrid

| Approach | How | Pros | Cons | When |
|----------|-----|------|------|------|
| **A. Redis-only sync** | Every check hits Redis | Simple accuracy | Hot keys; 1000× hard | Baseline–10× |
| **B. Local only** | Per-node counters | Fast | Wildly wrong multi-node | Single node only |
| **C. Hybrid (chosen at 100×+)** | Local buckets refilled from regional Redis slices; Redis from global coordinator | Extra scale | Overshoot control complexity | High QPS |
| **D. Edge approximate** | CDN/edge limits | Absorbs L7 abuse | Weak for TPM settle | Supplement only |

**Choice:** Redis Lua for baseline; evolve to **hybrid slices** before 1000×.

### 3.6 Regional + global coordination

```text
Global Coordinator (per model or per cell)
  └── allocates budget slices → Regional Limiters
         └── (optional) node-local caches from regional Redis

Usage deltas → Regional aggregators → Global (batched)
```

| Cap type | Enforcement | Sync |
|----------|-------------|------|
| Regional RPM/TPM | Hard in-region | Redis strong-ish |
| Global org contract | Soft/hard via slices | Batch 100ms–1s |
| Emergency kill | Hard push | Pub/sub seconds |

**Overshoot invariant:** sum(regional_slices) ≤ global_cap × (1 + ε); ε configured (e.g. 5%).

### 3.7 Fail open vs fail closed

| Mode | Behavior | Use |
|------|----------|-----|
| **Fail closed** | On limiter store error → 503/429 | Free tier, abuse-prone, cost control |
| **Fail open** | Allow with static default / last-known | Enterprise availability — **with hard local ceiling** |
| **Fail static** | Use cached policy + local token bucket only | Compromise |

**Resolved policy (defend this):**

- Default **fail-closed** on Redis errors for check/reserve.  
- Enterprise tier may **fail-static** (local ceiling = min(last_known, contract_burst)), never unbounded open.  
- Settles can queue; concurrency may soft-leak until sweeper—bound with TTLs.

### 3.8 Fairness vs throughput

| Strategy | Idea | Trade-off |
|----------|------|-----------|
| Pure hard quotas | Each org isolated | Simple; unused capacity idle |
| Work-conserving reallocation | Unused slices to needy orgs | Higher throughput; complexity; gaming |
| Weighted fair under overload | When model capacity < demand | Protects small orgs |

**Choice:** hard contracts + **optional work-conserving** spare capacity; under model overload, weighted fair admit lottery.

### 3.9 API / check interface

```http
POST /internal/v1/ratelimit/check
{
  "request_id": "req_...",
  "identity": {"org_id":"...","project_id":"...","api_key_id":"..."},
  "model": "gpt-4o",
  "estimated_input_tokens": 1200,
  "max_output_tokens": 2048,
  "stream": true
}

→ 200 {
  "allowed": true,
  "reservation_id": "rsv_...",
  "limits": {
    "rpm": {"remaining": 400, "reset_ms": 12000},
    "tpm": {"remaining": 80000, "reset_ms": 12000},
    "concurrency": {"remaining": 8}
  }
}

→ 429 {
  "allowed": false,
  "reason": "tpm_org",
  "retry_after_ms": 350,
  ...
}
```

```http
POST /internal/v1/ratelimit/settle
{
  "request_id": "req_...",
  "reservation_id": "rsv_...",
  "actual_input_tokens": 1180,
  "actual_output_tokens": 932,
  "status": "completed"
}
```

### 3.10 Hot keys

Mitigations (layered):

1. **Shard counter:** `tpm:org:X:model:m:{0..N-1}` — check random shard or all (costly); better: **local slice** so Redis key is per region.  
2. **Coalesce:** batch incr by 10ms window per key on node.  
3. **Coarse buckets** for mega tenants.  
4. **Dedicated limiter cell** for top talkers.  
5. **Cache deny** briefly when remaining=0 (careful with reset).

---

## 4. Architecture Diagram

### 4.1 System context

```text
+-----------+    +-------------+    +------------------+    +--------------+
| Clients   |--->| API Gateway |--->| Rate Limit SVC   |--->| Inference GW |
+-----------+    +-------------+    | (regional)       |    +--------------+
                                    +--------+---------+
                                             |
                    +------------------------+------------------------+
                    v                        v                        v
             +-------------+          +-------------+          +--------------+
             | Redis Cluster|          | Policy CFG  |          | Global Coord |
             | (buckets)    |          | (versions)  |          | (slices)     |
             +-------------+          +-------------+          +--------------+
                    ^
                    | settle
             +------+------+
             | Usage Events|
             | (Kafka/bus) |
             +-------------+
```

### 4.2 Check sequence

```text
GW                 LimitSvc              Redis               Global(opt)
 |--check---------->|                      |                    |
 |                  |--load policy (mem)--->|                    |
 |                  |--Lua reserve-------->|                    |
 |                  |<--allow/deny---------|                    |
 |                  |--(async) usage hint---------------------->|
 |<--200/429--------|                      |                    |
```

### 4.3 Settle sequence

```text
Inference --terminal--> UsageBus --> LimitSvc.settle
LimitSvc --Lua settle idempotent--> Redis
LimitSvc --delta--> Regional aggregator --> Global slices adjust
```

### 4.4 Hybrid local refill (100×+)

```text
Node local bucket (org, model)
  refill from Regional Redis slice every T ms
Regional Redis slice
  refill/adjust from Global Coordinator every U ms
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Idempotent check with reservation_id** tied to `request_id` (replay returns same decision within TTL).  
2. **Idempotent settle** — at-most-once economic effect per `request_id`.  
3. **Reservation TTL** — always reclaim.  
4. **Concurrency lease TTL** — always reclaim.  
5. **No unbounded fail-open.**  
6. **Policy version monotonic** — decisions stamp `policy_version`.  
7. **Overshoot bounded** by slice math (document ε).  
8. **Deny must not require cross-region RTT.**

**CAS-ish Lua sketch (conceptual):**

```lua
-- reserve TPM token bucket + concurrency
if redis.call('EXISTS', ban_key)==1 then return deny end
-- refill bucket based on now
-- if tokens >= need and conc < max then
--   tokens -= need; conc += 1; set reservation; return allow
-- else return deny
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Regional Rate Limit service + Redis; Lua atomicity; Postgres/config for policies |
| 10× | Redis Cluster; pipeline; identity cache; deny short-circuit cache |
| 100× | Hybrid local buckets; regional slices; Kafka settles; hot-key cells |
| 1,000× | Many limiter cells; approximate global; gossip or sharded global coordinators; edge RPM for abuse |

**Check QPS path optimization:**

- Auth identity cached.  
- Policy in memory (watch).  
- Single Redis RTT Lua.  
- Optional local allow if remaining ≫ need (debit locally, sync async)—only with slice accounting.

### 5.3 Maintainability

- Shadow mode for new limits.  
- Property tests: never negative concurrency; settle idempotent; TTL reclaim.  
- Load test hot keys explicitly.  
- Metrics: `check_latency`, `deny_ratio{reason,model,tier}`, `redis_error`, `overshoot_estimate`, `settle_lag`.  
- No `org_id` in Prometheus labels at high cardinality—use exemplars/logs sampling.

### 5.4 Fairness deep dive

Under model capacity C and demand from orgs with weights w_i:

```text
share_i = C * w_i / sum(w)
admit with probability or token rate matching share when congested
idle capacity redistributed (work-conserving) if enabled
```

**Strict fairness vs throughput:** work-conserving increases throughput but can surprise “empty” orgs when spare vanishes—document.

### 5.5 Streaming debt

If `actual >> reserved`:

1. Apply debt to bucket (may go to zero / negative credit).  
2. Next checks pay debt first.  
3. Optional: if debt > hard threshold, signal Inference GW to cancel stream (product).  
4. Abuse heuristics if chronic underestimate gaming.

### 5.6 Consistency model (honest)

- **Linearizable global TPM:** not on hot path.  
- **Per-region Redis key:** approximately sequential via Lua.  
- **Cross-region:** eventual with bounded overshoot.  
- Clients must tolerate 429s even if “dashboard says remaining.”

---

## 6. Wrap-Up

### 6.1 What we designed

A **distributed LLM API rate limiter** enforcing hierarchical RPM/TPM/concurrency with **reserve+settle** for streaming tokens, Redis Lua atomicity evolving to **hybrid local+regional+global slices**, explicit **fail-closed/fail-static** (never unbounded open), hot-key mitigations, and fairness under overload—scaling checks from ~50K/s to ~50M/s.

### 6.2 Key decisions worth defending

1. **Split RPM / TPM / concurrency** — different algorithms & failure modes.  
2. **Reserve + settle + TTL** — streaming reality.  
3. **No cross-region sync on check hot path.**  
4. **Slice-based global caps** with explicit overshoot ε.  
5. **Fail-closed default; enterprise fail-static ceiling.**  
6. **Idempotent request_id** for check/settle.  
7. **Hot keys are a first-class design problem.**  
8. **Limiter ≠ billing ledger** — share events, separate SoT.  
9. **Shadow mode** for policy rollout.  
10. **Correct 1000× math** forces hybrid, not bigger Redis alone.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Chronic reserve underestimate | Better estimators; debt cancel policy |
| Redis hot shard | Key split / dedicated cells |
| Global coordinator lag | Adaptive slice sizes; emergency regional freeze |
| Fail-static abuse | Tight ceilings + anomaly detection |
| Settle lag | Backpressure metrics; sweeper SLOs |

### 6.4 How to present in 45 minutes

1. Dimensions + hierarchy (5 min)  
2. Numbers: check vs settle; 50M ops problem (5 min)  
3. Token bucket + reserve/settle (10 min)  
4. Regional/global slices + fail modes (10 min)  
5. Hot keys + fairness (5 min)  
6. Q&A (remaining)

---

## 7. Deeper / Related Interview Questions

### 7.1 Algorithms

**Q: Token bucket vs sliding window for RPM?**  
A: Bucket gives clean burst+refill; sliding window counter also fine. Fixed window alone has boundary double-burst—avoid as sole algorithm.

**Q: How do you implement refill without races?**  
A: Redis Lua: read tokens+ts, refill by elapsed×rate, cap burst, debit, write—single atomic script.

**Q: Why not DB counters?**  
A: Latency and lock contention; OLTP DB is wrong for 50K–50M check QPS.

**Q: Approximate counting (Count-Min / HyperLogLog)?**  
A: Useful for abuse analytics, not for authoritative paid TPM contracts.

### 7.2 Streaming & settle

**Q: What if output is unbounded?**  
A: Cap `max_output_tokens` at admit; hard stop generation at cap; settle actual ≤ cap (+input).

**Q: Mid-stream cancel?**  
A: Settle partial actual; release concurrency; idempotent.

**Q: Duplicate settle from retries?**  
A: `request_id` unique constraint / Redis SETNX settled flag.

**Q: Reserve 0 for tiny requests?**  
A: Still concurrency+RPM; TPM reserve minimum 1 or prompt tokens.

### 7.3 Failure modes

**Q: Redis down — what do you do?**  
A: Fail-closed default; enterprise fail-static with ceiling; never infinite allow.

**Q: Global coordinator down?**  
A: Hold last slices; optionally tighten (freeze growth); regional hard caps remain.

**Q: Clock skew across limiter nodes?**  
A: Refill based on Redis TIME; avoid node wall clocks for bucket math.

**Q: Poison Lua / bad deploy?**  
A: Versioned scripts; canary; instant rollback to prior sha; shadow compare.

### 7.4 Fairness & product

**Q: Fairness vs utilization?**  
A: Hard quotas waste spare; work-conserving helps utilization; under congestion use weights.

**Q: One noisy API key in an org?**  
A: Per-key limits inside org; org-level still protects platform.

**Q: Should 429s be retryable blindly?**  
A: Honor `Retry-After`; jitter; distinguish soft vs hard ban.

### 7.5 Multi-region

**Q: Can we have strong global TPM?**  
A: Not at ms latency worldwide. Use slices + bounded overshoot; batch reconcile.

**Q: Active-active limiters?**  
A: Yes regionally; global coordination is soft state.

**Q: User pinned to region?**  
A: Helps accuracy; multi-region keys need slice split by traffic share.

### 7.6 Hot keys & performance

**Q: Single org at 20% traffic melts a key — fix?**  
A: Regional keys already split load; add local hybrid; dedicated cell; sharded counters with careful read.

**Q: Pipelining vs Lua?**  
A: Lua for atomic multi-dimension; pipeline for independent keys (IP + org) carefully ordered.

**Q: Cache denies?**  
A: Yes briefly when remaining=0; invalidate on policy boost / reset boundary.

### 7.7 Headers & API design

**Q: Which rate limit headers?**  
A: Remaining/reset per dimension or synthetic primary; document; don’t lie wildly vs internal state.

**Q: Should check be side effect free?**  
A: No—reserve is a side effect. Provide dry-run/shadow for tools.

**Q: Idempotency of check?**  
A: Same `request_id` returns same reservation within TTL; different body hash → conflict.

### 7.8 Security & abuse

**Q: Credential stuffing RPM?**  
A: IP + key + anomaly; edge limits before auth DB.

**Q: Slow-loris concurrency holds?**  
A: Concurrency leases with TTL; max stream duration; gateway timeouts.

**Q: Gaming estimator to reserve low?**  
A: Minimum reserve; debt; cancel; abuse scores.

### 7.9 Algorithms & data structures

**Q: Data structure for buckets?**  
A: Hash per key: `{tokens, updated_at_ms, conc}`; TTL idle.

**Q: Global fair share structure?**  
A: Weighted deficit round-robin or token rates per org; hierarchical CRF-like ideas for advanced.

**Q: How to compute Retry-After?**  
A: Time until bucket has enough tokens for need: `(need - tokens) / refill_rate`.

### 7.10 Comparison traps

**Q: Is this Kong/Envoy rate limit enough?**  
A: Good for RPM/IP; LLM needs TPM + streaming settle + hierarchical org contracts + global slices.

**Q: Same as API Gateway throttle?**  
A: Gateway is a deployment point; domain logic is TPM/reserve/settle/fairness.

**Q: Same as billing?**  
A: No—billing is append-only ledger of actuals; limiter is real-time admission control.

### 7.11 Extra interviewer traps (high value)

- What exactly is reserved before first token?  
- How do you release capacity if the worker dies after allow?  
- Why is global sync not on the check path?  
- What’s your overshoot bound and how derived?  
- Fail-open without a ceiling — why is that a deal-breaker?  
- How do you handle settle arriving twice?  
- How do hot keys break Redis Cluster?  
- RPM remaining vs TPM remaining — which drives Retry-After?  
- How do you roll out a 50% quota cut safely? (shadow → enforce)  
- How do you prevent meta-QPS meltdown from check storms?  
- What’s the difference between concurrency and RPM?  
- How do you test overshoot under partition?  
- Why Lua not optimistic GET/SET?  
- How does work-conserving interact with contracted minimums?  
- At 50M check QPS, what’s impossible about single-region Redis?

---

## Appendix A — Redis key schema

```text
pol:ver                          # global policy version cache hint
ban:org:{org}                    # TTL ban flag
tb:rpm:{scope}:{id}:{model}      # hash: tokens, ts
tb:tpm:{scope}:{id}:{model}      # hash: tokens, ts
sem:conc:{scope}:{id}:{model}    # int + expire
rsv:{request_id}                 # hash: reserved, scopes, exp
settled:{request_id}             # flag TTL
slice:{region}:{org}:{model}:tpm # regional slice budget
```

## Appendix B — Lua reserve pseudocode

```text
function reserve(keys, need_tpm, rpm_cost=1):
  if banned: return DENY("ban")
  refill(rpm_key); refill(tpm_key)
  conc = INCR(conc_key); PEXPIRE(conc_key, lease)
  if conc > max_conc: DECR; return DENY("concurrency")
  if rpm.tokens < 1 or tpm.tokens < need_tpm:
     DECR conc; return DENY(...)
  rpm.tokens -= 1; tpm.tokens -= need_tpm
  SET rsv{request_id} ...
  return ALLOW
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Redis Lua RPM/TPM/conc, reserve+settle, TTLs, fail-closed, headers |
| 10× | Cluster, identity/policy cache, metrics, shadow mode |
| 100× | Hybrid local slices, Kafka settle, hot-key cells, global coordinator |
| 1,000× | Multi-cell limiters, approximate global, edge abuse RPM, dedicated whale cells |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| RPM | Requests per minute |
| TPM | Tokens per minute (in+out) |
| Reserve | Hold estimated TPM (+conc) at admit |
| Settle | Adjust to actual usage at terminal |
| Slice | Regional allocation of a global budget |
| Fail-static | Degraded local enforce with ceiling |
| Overshoot ε | Allowed temporary global exceedance |
| Hot key | Disproportionate traffic on few Redis keys |
| Work-conserving | Reallocate unused capacity |

## Appendix E — Estimation cheat-sheet

```text
check_QPS ≠ settle_QPS ≠ renew_QPS
redis_ops ≈ check_QPS × ops_per_check  (Lua can make ops_per_check ≈ 1 RTT)

state_bytes ≈ active_keys × 128 B

local uncertainty ≈ local_QPS × sync_interval
slice sizing must absorb uncertainty

50M check/s → hybrid mandatory; pure single Redis cluster fantasy
```

## Appendix F — Worked numeric examples (interview whiteboard)

### F.1 Token bucket refill

```text
TPM limit: 1_000_000 tokens/min  → refill_rate = 1_000_000/60 ≈ 16,667 tok/s
Burst (bucket size): 200_000 tokens (policy)
Request reserves 8,000 tokens:
  if tokens >= 8000: tokens -= 8000; allow
  else: retry_after ≈ (8000 - tokens) / 16667 seconds
```

### F.2 Regional slices for a global TPM cap

```text
Global org TPM cap G = 10_000_000 / min
Regions: us, eu, apac with traffic shares 50%, 30%, 20%
Base slices: 5.0M, 3.0M, 2.0M / min
ε overshoot budget 5% → sum(slices) ≤ 10.5M
Idle reallocation (work-conserving): unused eu capacity may boost us temporarily,
but never exceed G×(1+ε) for more than one sync window without clawback.
```

### F.3 Streaming debt

```text
Reserved output estimate: 2_000
Actual output: 6_000
Debt = 4_000 tokens applied to bucket immediately on settle
Next request needs 1_000 but bucket at 200 → deny until refill covers debt+need
Optional: if debt > 50_000 mid-flight, Inference GW receives cancel signal
```

### F.4 Hot-key shard math

```text
Org generates 2M check/s; single Redis key Lua max ~100–300K ops/s (order, hardware-dependent)
Need ≥ 10 regional/local slices or hybrid local debit to survive
Never put global celebrity org on one Cluster hash slot without isolation plan
```

## Appendix G — Decision header contract

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 1
X-RateLimit-Limit-Requests: 5000
X-RateLimit-Remaining-Requests: 0
X-RateLimit-Reset-Requests: 1710000012
X-RateLimit-Limit-Tokens: 1000000
X-RateLimit-Remaining-Tokens: 1200
X-RateLimit-Reset-Tokens: 1710000012
X-RateLimit-Limit-Concurrency: 100
X-RateLimit-Remaining-Concurrency: 0
X-RateLimit-Reason: tpm_org
```

Document which dimension is authoritative for `Retry-After` when multiple trip (prefer soonest reset that unblocks the denying dimension).

## Appendix H — Policy rollout playbook

1. **Shadow:** compute decision, emit metrics, do not enforce.  
2. **Canary enforce:** 1% keys / 1% traffic.  
3. **Widen** while watching deny_ratio, support tickets, revenue impact.  
4. **Emergency kill-switch:** pub/sub `ban` / `freeze_slices` with version bump.  
5. **Rollback:** prior `policy_version` remains in memory on all nodes ≤ T seconds via dual-publish.

## Appendix I — Invariant test checklist

| Test | Expect |
|------|--------|
| Duplicate settle | Second settle no-ops; concurrency not double-released |
| Reservation TTL | After TTL, tokens/concurrency restored without settle |
| Partial settle after cancel | Actual tokens applied; concurrency 0 |
| Redis error free tier | Deny/503 — not allow |
| Config zeroed by bug | Guardrails reject non-positive limits on push |
| Cross-region partition | Overshoot ≤ ε for configured window |
| Hot key cell migration | No thundering reconnect of check path |

---

*End of design doc. Open with §1 dimensions + fail policy; whiteboard §3.4 reserve/settle + §3.6 slices; close with invariants in §5.1 and traps in §7.*
