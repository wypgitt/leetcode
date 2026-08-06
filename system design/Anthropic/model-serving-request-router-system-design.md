# System Design: Model-Serving Request Router

> **Focus areas:** Sticky assignment · Backend capacity · Model compatibility · Overload shedding · Failover · KV-cache affinity  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar admit/dispatch/stream classes, explicit affinity vs load-balance tradeoffs, resolved overload policy (shed vs queue vs degrade)  
> **Interview theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — reliability, consistency, concurrency, cost, and where LLM serving changes constraints

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

Goal: **bound the router**—a control-plane + data-plane component that admits inference requests, selects a compatible healthy backend with capacity, optionally sticks follow-ups for KV-cache / session affinity, and fails over or sheds under overload. This is **not** training, not the model itself, and not the full product chat UX.

### 1.0 What this is / is not (say this early)

| Dimension | **Request router (this doc)** | Out of scope siblings |
|-----------|-------------------------------|------------------------|
| Primary job | Admit → place → stick / failover → complete | Token generation internals |
| Success metric | Low TTFT, high goodput, fair capacity use, safe failover | Model quality |
| State | Soft: affinity maps, capacity, circuit state | Durable chat history |
| Sticky why | KV-cache reuse, prefix cache, multi-turn continuity | Pure L7 round-robin CDN |
| Compatibility | Model id + version + capability matrix | Training checkpoint format |

**Scope statement:** Design the model-serving **request router** that sits between API/gateway and GPU/TPU inference backends—sticky assignment, capacity-aware placement, compatibility, overload, failover.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who calls the router? | API gateway / product BFF / batch jobs | Sync admit path + async batch class |
| F2 | What is a “backend”? | Inference replica / engine instance (vLLM-like, custom) with model weights loaded | Registry of endpoints + loaded models |
| F3 | Sticky sessions? | Prefer same backend for multi-turn / continued generation when KV cache helps | Affinity key + TTL + soft stickiness |
| F4 | Compatibility? | Request model version must match loaded weights; capability flags (tools, vision, long-ctx) | Compatibility matrix; reject or rewrite |
| F5 | Capacity signal? | Concurrent slots, GPU mem, queue depth, tokens in-flight | Multi-dimensional capacity model |
| F6 | Overload? | Shed / queue with deadline / degrade to smaller model | Explicit policy; never unbounded queue |
| F7 | Failover? | Backend die mid-stream → cancel or retry elsewhere (lose KV) | Circuit breakers; sticky invalidate |
| F8 | Fairness? | Tenant / tier quotas feed admission | Router enforces or trusts upstream limiter |
| F9 | Streaming? | Yes — router holds or proxies stream | Sticky for stream lifetime mandatory |
| F10 | Multi-model pools? | Many model versions co-exist; canary / shadow | Pool-aware routing; version pin |
| F11 | Health? | Active probes + passive error rates | Half-open circuits; drain |
| F12 | Observability? | Placement reason, cache hit hint, shed reason | Structured decision logs |

**MVP functional scope (lock with interviewer):**

1. Admit request with `model`, optional `affinity_key`, `max_tokens`, priority/tier.  
2. Resolve **compatible** backends from registry + capability matrix.  
3. Choose placement: **sticky if healthy+capacity**, else capacity-aware pick.  
4. Reserve slot (soft or hard) before forwarding; release on complete/fail.  
5. Proxy or hand off **streaming** response; stick for stream lifetime.  
6. **Overload:** queue with deadline OR shed 429/503 with Retry-After OR degrade (with notice flag).  
7. **Failover:** on backend failure before first token → retry other backend; mid-stream → fail incomplete (MVP).  
8. Circuit breakers + health; drain for deploy.  
9. Metrics: admit QPS, shed rate, sticky hit rate, TTFT, backend utilization.

**Out of MVP (explicitly defer):**

- Perfect mid-stream migration with KV transfer  
- Cross-region sticky without shared state (document home-region)  
- Optimal bin-packing of heterogeneous GPU SKUs (hooks only)  
- Speculative decoding orchestration across devices  
- Full RLHF / training job placement  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Admit latency? | Tiny vs TTFT | p99 admit < 5–20ms in-region |
| N2 | Sticky hit rate? | High when beneficial | ≥70–90% on multi-turn when backend healthy |
| N3 | Availability | Control plane critical | 99.99% admit path; degrade placement quality before total outage |
| N4 | Correctness | Never route incompatible model | Hard reject or controlled rewrite |
| N5 | Fairness | No noisy-neighbor starvation | Weighted fair admission by tier |
| N6 | Consistency of affinity | Soft OK | Eventual; wrong stick = miss, not corruption |
| N7 | Cost | GPU $ dominate | Maximize goodput & KV reuse; avoid thrash |
| N8 | Safety of shed | Prefer fail closed under unknown capacity | Don’t over-admit into OOM |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New request, no affinity → pick least-loaded compatible backend → stream → complete → release.  
2. Follow-up with same `affinity_key` → sticky hit → KV reuse → lower TTFT.  
3. Sticky target full → soft break stickiness → place elsewhere (log stick_break).  
4. Canary model version → small % traffic with pin; rest on stable.  
5. Backend draining → no new sticky; existing streams finish; affinity invalidated.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Affinity key maps to dead backend | Invalidate; re-place; optional sticky rewrite |
| Hot shard (celebrity affinity key) | Cap concurrency per key; spill; coalesce |
| Capacity signal stale | Conservative headroom; short TTL leases |
| Double admit (retry) | Idempotency-Key → one reservation |
| All backends circuit-open | Shed 503; optional queue with short deadline |
| Model version not loaded anywhere | 404/422 incompatible; don’t silent fallthrough |
| Mid-stream backend crash | Incomplete; client retry (new affinity) |
| Burst of long-context requests | Separate capacity dimension (KV bytes) |
| Priority inversion | High tier preemption / reserved pools |
| Registry split-brain | Prefer under-admit; fencing tokens on register |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak admit QPS | 5K | 50K | 500K | 5M |
| Peak concurrent streams | 50K | 500K | 5M | 50M |
| Backend replicas (fleet) | 500 | 5K | 50K | 500K |
| Distinct model versions live | 20 | 50 | 200 | 1K+ |
| Affinity map entries | 2M | 20M | 200M | 2B (sharded / TTL) |
| Capacity updates/s | 5K | 50K | 500K | 5M |
| Shed decisions/s (peak stress) | 500 | 5K | 50K | 500K |
| Router instances | 20 | 100 | 1K | multi-cell |

**What each jump forces:**

- **10×:** Central Redis/etcd affinity becomes hot → sharded affinity; local capacity cache.  
- **100×:** Cell / pool partitioning by model family; hierarchical routers.  
- **1,000×:** Region + cell; affinity mostly local; gossip capacity; global only for rare cross-cell.

### 1.5 Etc. (Constraints & Assumptions)

- GPU/TPU dollars dominate; router CPU is cheap relative to mis-placement.  
- **KV-cache affinity** is the main AI-specific constraint: stickiness is a **performance** feature, not a correctness requirement (except stream lifetime).  
- Compatibility is a **correctness** hard constraint.  
- Upstream may already rate-limit; router still must not over-admit backends.  
- Anthropic-style theme: treat this as classic load balancing + lease + circuit breaker with LLM capacity dimensions.

**Scope statement to repeat back:**

> Design a model-serving request router that admits inference requests, enforces model/capability compatibility, places onto capacity-aware backends with optional sticky assignment for KV-cache affinity, handles overload via bounded queue/shed/degrade, and fails over safely—scaling from thousands to millions of admits/s through cells, without pretending mid-stream KV migration is free.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Admit RPCs** | Sync place decision | ~5K/s | ~50K/s | Router CPU |
| **Affinity R/W** | Get/set sticky map | ~5–10K/s | ~50–100K/s | Redis / memory |
| **Capacity heartbeats** | Backend → router | ~5K/s | ~50K/s | Gossip / Redis |
| **Stream proxy bytes** | Tokens to client | Dominated by tokens | ×10 | Data plane |
| **Reservation CAS** | Slot lease | ~5K/s | ~50K/s | Local or Redis |
| **Decision logs** | Async analytics | ~5K/s | ~50K/s | Kafka |

**Anti-pattern:** one “QPS” that mixes admit, token stream, and heartbeat fan-in.

### 2.2 Capacity model (LLM-specific)

```text
Backend capacity is multi-dimensional:
  C_slots   = max concurrent sequences
  C_kv      = KV-cache memory budget (bytes)
  C_tok_in  = prefill tokens/s headroom
  C_tok_out = decode tokens/s headroom

Request demand:
  D_slots = 1
  D_kv    ≈ layers × heads × dim × dtype × (prompt+max_new)  (order-of)
  D_prefill ≈ prompt_tokens
  D_decode  ≈ expected_output_tokens (or reserved max)

Admit iff residual capacity ≥ demand + safety_headroom
```

**Interview line:** least-connections is insufficient; a short chat and a 100K-context request are not equal “connections.”

### 2.3 Sticky value math

```text
Assume sticky hit saves S ms TTFT (prefill avoided / partial) and T GPU-ms.
Sticky hit rate H.
Value ≈ H × (S latency + T $) − affinity_store_cost

If H drops due to thrash (constant rebalance), value → negative.
Prefer soft stickiness + hysteresis over aggressive rebalance.
```

### 2.4 Hot-shard math

```text
If affinity_key = user_id for a viral account:
  demand can exceed single backend C_slots
Must: spill (break stick), shard key (conversation_id), or coalesce
Never pin unlimited load to one replica because of celebrity key
```

### 2.5 Overload math

```text
Arrival λ, service μ (completions/s), queue with deadline D
If λ > μ: either shed (ρ_shed = λ−μ) or queue until wait > D then shed
Interactive SLO: prefer shed early over multi-second queues
Batch class: separate deeper queues OK
```

### 2.6 Storage for affinity

```text
Entry ~128 B (key, backend_id, gen, expiry)
2M entries ≈ 256 MB (+ Redis overhead → ~0.5–1 GB)
At 200M entries → shard; TTL aggressive (minutes–hours)
```

---

## 3. High-Level Design

### 3.1 Placement in the stack

```text
Client → Edge/API GW → [Quota] → Request Router → Inference Backend
                              ↘ Decision log / metrics
Backend registry ← heartbeats / control plane
Affinity store  ↔ router
```

### 3.2 Domain model

```text
Request
  model_id, model_version_constraint (pin | range | latest_compatible)
  affinity_key? (conversation_id / session_id / prefix_hash)
  priority / tenant / tier
  prompt_tokens_est, max_new_tokens
  capabilities_needed[] (tools, vision, ...)
  idempotency_key?
  stream: bool

Backend
  id, pool, addr
  loaded: [{model_version, capabilities, weights_gen}]
  capacity: {slots, kv_free, tok_in, tok_out}
  health: {state, ewma_error, last_probe}
  drain: bool

PlacementDecision
  backend_id | shed | queue
  reason: sticky_hit | least_loaded | fallback | degrade
  stick_break?: bool
  reserved_lease_id
```

### 3.3 Compatibility matrix

| Request asks | Backend offers | Result |
|--------------|----------------|--------|
| Exact version pin | Same version loaded | OK |
| `latest` in family | Newest healthy in family | OK if policy allows drift |
| Needs vision | Text-only weights | Reject / route other pool |
| Context 200K | Max 32K engine | Reject |
| Tools schema v2 | Engine tools v1 | Reject or rewrite adapter |

**Deal-breaker:** silent route to wrong weights (wrong answers, safety regressions). Prefer hard fail with clear error.

### 3.4 Placement strategies (tradeoff table)

| Strategy | Pros | Cons | When |
|----------|------|------|------|
| Round-robin | Simple | Ignores load & KV | Never alone for LLM |
| Least connections | Easy | Unequal token load | Weak baseline |
| Least-loaded (multi-dim) | Matches capacity | Needs fresh signals | **Default cold place** |
| Consistent hashing | Stable mapping | Hot keys; ignore load | Prefix cache sharding |
| **Sticky + least-loaded spill** | KV reuse + safety | Affinity state | **Chosen MVP** |
| Power of two choices | Low coordination | Weaker sticky | Mega scale cold path |
| Central optimizer | Globally best | Latency / SPOF | Offline / batch |

**Chosen:** soft sticky affinity with TTL; on miss or unhealthy/full → multi-dimensional least-loaded among compatible; hysteresis before breaking stick for rebalance.

### 3.5 Consistent hashing vs least-loaded

| | Consistent hash | Least-loaded |
|--|-----------------|--------------|
| Sticky naturally | Yes (key→ring) | Needs side map |
| Hot key | Bad (pile-on) | Can avoid if not sticky |
| Load awareness | Weak unless virtual nodes + feedback | Strong |
| KV affinity | Good for prefix_hash | Good with explicit map |
| Failover | Remap neighbors | Pick any healthy |

**Deal-breaker for pure consistent hash:** one viral conversation_id melts one backend.  
**Hybrid:** hash to a **preference ordered list**; walk list until capacity fits (bounded probes).

### 3.6 Overload policies

| Policy | UX | Risk | Choice |
|--------|-----|------|--------|
| Unbounded queue | Delayed | Memory blowup | **Deal-breaker** |
| Bounded queue + deadline | Wait then 503 | Fairness tuning | Interactive optional |
| Immediate shed | Fast fail | Retries amplify | With Retry-After |
| Degrade model | Continuity | Quality/trust | With `degraded=true` |
| Reserved pools by tier | Protects paid | Fragmentation | **Yes** |

**MVP:** tier reserved pools + short deadline queue (e.g. 100–500ms) + shed + optional degrade flag for Auto tier only.

### 3.7 Failover matrix

| Failure moment | Action |
|----------------|--------|
| Before forward | Pick next backend |
| After reserve, before first token | Release; retry ≤N other backends |
| After first token (streaming) | Abort stream; mark incomplete; **no** silent backend hop (KV lost) |
| Backend flapping | Circuit open; probe half-open |
| Region loss | Fail to regional shed; don’t cross-region sticky without design |

### 3.8 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/route` | Admit + place (returns backend or stream proxy) |
| POST | `/v1/reserve` | Reserve only (for split data plane) |
| POST | `/v1/complete` | Release reservation |
| GET | `/v1/backends` | Admin list |
| POST | `/v1/backends/{id}/drain` | Deploy drain |
| GET | `/v1/affinity/{key}` | Debug sticky |

```http
POST /v1/route
Idempotency-Key: ...
{
  "model": "claude-sonnet-x",
  "version": "2026-05-01",
  "affinity_key": "conv_...",
  "tier": "priority",
  "est_prompt_tokens": 4096,
  "max_new_tokens": 2048,
  "capabilities": ["tools"],
  "stream": true
}
```

### 3.9 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker alternative |
|----------|--------|-----|--------------------------|
| Stickiness | Soft map + TTL | KV win without hard correctness | Hard pin forever → imbalance |
| Placement | Multi-dim least-loaded | Tokens ≠ connections | RR → OOM / latency cliffs |
| Overload | Shed + short queue | Protect TTFT | Infinite queue |
| Mid-stream FO | Fail incomplete | Honest; KV not portable MVP | Silent hop → garbage tokens |
| Compatibility | Hard matrix | Safety/quality | Best-effort wrong model |
| State store | Sharded Redis + local cache | Scale admits | Single global lock |

---

## 4. Architecture Diagram

```text
                         +------------------+
   Clients / BFF         |   Quota / Auth   |
        |                +--------+---------+
        v                         |
+-------+--------+                |
|  Request Router Fleet (stateless-ish)    |
|  - admit + compatibility                 |
|  - sticky lookup                         |
|  - capacity-aware place                  |
|  - circuit / shed / degrade              |
+---+------+------+--------+---------------+
    |      |      |        |
    |      |      |        +--> Decision log (Kafka)
    |      |      +----------> Metrics
    |      v
    |  +------------------+
    |  | Affinity Store   |  key -> {backend, gen, exp}
    |  | (sharded Redis)  |
    |  +------------------+
    |      ^
    |      | invalidate on drain/fail
    v      |
+---+------+------------------------------+
| Backend Registry / Capacity View         |
|  heartbeats: slots, kv_free, errors      |
+---+----------+------------+--------------+
    |          |            |
    v          v            v
[Pool: Sonnet] [Pool: Haiku] [Pool: Opus/Canary]
   |              |              |
   +-- GPU/TPU inference replicas (streaming)
```

**Stream path (MVP coupled proxy):**

```text
Client ←—SSE/gRPC stream—→ Router instance A ←—→ Backend B
         (connection sticky to router A for stream lifetime)
```

**Phase-2 split:** Router returns `backend_addr` + capability token; data plane connects direct; router only control plane.

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Compatibility invariant:** never forward to backend lacking required model/capabilities.  
2. **Reservation invariant:** in-flight streams ≤ sum of reserved slots (+ bounded oversubscribe policy).  
3. **Stream affinity invariant:** a live stream does not change backend mid-response.  
4. **Failover honesty:** mid-stream failure surfaces incomplete; no silent wrong continuation.  
5. **Shed before melt:** when capacity unknown/unhealthy, fail closed on admit.

#### 5.1.2 Circuit breakers

```text
Closed --(error rate | latency | probe fail)--> Open
Open --(cooldown)--> Half-open --(probe OK)--> Closed
                     Half-open --(fail)--> Open
```

Per-backend and per-pool breakers. Affinity entries pointing to Open backends are ignored (soft miss).

#### 5.1.3 Leases / reservations

```text
Reserve(backend, demand) -> lease_id, expiry
Heartbeat/extend while streaming
Complete/Abort -> release
Expiry sweeper frees zombies (client disconnect without complete)
```

**Oversubscribe policy:** optional small % for short decode-only if KV fits—document risk.

#### 5.1.4 Sticky consistency

Affinity is **soft state**. Wrong entry ⇒ performance miss, not incorrect tokens (compatibility still checked on use). Use generation numbers: drain bumps backend gen; sticky entries with old gen ignored.

#### 5.1.5 Idempotency

Client retries use `Idempotency-Key`. Router stores decision briefly (lease + backend). Prevents double-reservation storms.

#### 5.1.6 Failure modes & progressive scale

| Scale | Reliability focus |
|-------|-------------------|
| Baseline | Single Redis OK; in-process capacity cache |
| 10× | Redis cluster; router peer miss → recompute |
| 100× | Cell isolation; blast radius = cell |
| 1,000× | Region autonomy; global control plane read-mostly |

#### 5.1.7 Deploy / drain

```text
drain=true → no new sticky, no new cold place
existing streams finish (timeout)
affinity invalidated
unregister when zero in-flight
```

### 5.2 Scalability

#### 5.2.1 Router horizontal scale

Routers are mostly stateless: affinity + capacity externalized. Any router can admit. Stream-proxy mode pins connection to one router instance (connection-level stickiness via L4/L7).

#### 5.2.2 Affinity store scaling

| Scale | Design |
|-------|--------|
| Baseline | One Redis; TTL 30–60 min |
| 10× | Shard by `hash(affinity_key)` |
| 100× | Per-cell affinity; key includes `cell_id` |
| 1,000× | Mostly local memory + async backup; accept higher miss |

#### 5.2.3 Capacity view scaling

Heartbeats at 1–2 Hz × 500 backends = cheap. At 500K backends: hierarchical aggregators (rack/pool → cell router), push deltas, EWMA locally.

#### 5.2.4 Hot keys

- Cap in-flight per `affinity_key`.  
- Spill to other backends when sticky full.  
- Prefer `conversation_id` over `user_id` for stick key.  
- Optional: sticky to **set** of N backends (bounded fan).

#### 5.2.5 Pool partitioning

Partition by model family / SKU / region:

```text
Router → Pool Router (Sonnet) → replicas
       → Pool Router (Haiku)
```

Reduces compatible-candidate scan from O(fleet) to O(pool).

#### 5.2.6 Cost

| Lever | Effect |
|-------|--------|
| Sticky KV reuse | Less prefill GPU-time |
| Avoid thrash rebalance | Stable caches |
| Shed early | Protect goodput of in-flight |
| Right-size pools | Don’t idle huge models for tiny traffic |
| Batch vs interactive isolation | Prevent batch from stealing decode slots |

**AI infra twist:** a “balanced” CPU load balancer that ignores KV can **increase** $ by forcing constant prefills.

#### 5.2.7 Progressive scale changes

| Jump | Change |
|------|--------|
| →10× | Sharded affinity; power-of-two among top candidates |
| →100× | Cells; pool routers; capacity aggregators |
| →1,000× | Region cells; eventual capacity gossip; affinity mostly local |

### 5.3 Maintainability

#### 5.3.1 Decision explainability

Every admit emits:

```text
{request_id, model, candidates_n, chosen, reason, sticky_hit,
 stick_break, residual_capacity_snapshot, shed_class?}
```

On-call debugs “why was I not sticky?” from logs, not folklore.

#### 5.3.2 Compatibility as data

Matrix in versioned config (or service catalog). Routers watch updates; canaries for new model versions. Bad matrix deploy = instant pages—use progressive rollout + dual-read.

#### 5.3.3 Testing

- Deterministic simulator: backends with fake capacity; replay traces.  
- Chaos: kill backend mid-stream; assert incomplete not corrupt.  
- Load: hot-key and thundering-herd affinity invalidation.  
- Compatibility fuzz: random capability sets.

#### 5.3.4 Operability

Dashboards: sticky hit %, shed by reason, circuit opens, KV OOM near-misses, p99 admit, TTFT by sticky vs cold.  
Alerts: shed > threshold, registry freshness lag, affinity error rate.

#### 5.3.5 Safe evolution

Phase 1: coupled stream proxy.  
Phase 2: control-plane only + signed placement token.  
Phase 3: optional KV migration for rare failover (expensive; justify).

---

## 6. Wrap-Up

### 6.1 What we designed

A **model-serving request router** that:

- Enforces **model/capability compatibility** as a hard constraint.  
- Places with **multi-dimensional capacity** (slots, KV, prefill/decode).  
- Uses **soft sticky assignment** for KV-cache affinity with spill on overload/hot keys.  
- Handles overload via **reserved pools, short queues, shed, optional degrade**.  
- Fails over **before first token**; mid-stream failures are honest incompletes.  
- Scales via **sharding, cells, pool routers**, with progressive 10×/100×/1,000× story.

### 6.2 Key tradeoffs (memorize)

| Topic | Stance |
|-------|--------|
| Sticky vs balance | Soft sticky + spill beats hard pin or pure RR |
| Hash vs load | Hybrid preference list > pure consistent hash |
| Queue vs shed | Bounded deadline; interactive sheds early |
| Mid-stream FO | Don’t fake it without KV move |
| Cost | Placement quality = GPU $ |

### 6.3 Interview closing line

> “This is classic admission control, leases, and circuit breakers—the AI twist is that capacity is KV- and token-shaped, and stickiness is an optimization with real dollars attached, not a correctness crutch.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Sticky sessions & affinity

**Q1: Why sticky for LLM serving?**  
A: Prefill is expensive; KV / prefix cache on a backend makes follow-ups cheaper and faster. Stickiness raises cache hit rate.

**Q2: Is sticky required for correctness?**  
A: No for multi-turn if you resend history (stateless API). Yes for a single in-flight stream. Soft stick is performance.

**Q3: Affinity key choice?**  
A: Prefer `conversation_id` or `prefix_hash` over `user_id` to avoid celebrity hot shards.

**Q4: How long should affinity TTL be?**  
A: On the order of conversation idle timeout (minutes–hours). Too long → tombstones and imbalance; too short → miss.

**Q5: What if sticky backend is busy but others idle?**  
A: Spill with hysteresis; log `stick_break`. Optionally keep sticky if queue wait < threshold.

**Q6: Consistent hashing alone?**  
A: Stable but hot keys and blind to load. Use as preference order, not sole decider.

**Q7: Sticky across regions?**  
A: Avoid MVP. Home region for conversation; cross-region = cold place + higher latency.

**Q8: How do you invalidate sticky on deploy?**  
A: Drain + generation bump; entries with stale gen ignored.

**Q9: Can two routers disagree on sticky?**  
A: Yes briefly; both re-check backend health/capacity. Worst case duplicate cold place—acceptable.

**Q10: Prefix-cache aware routing?**  
A: Affinity key = hash of shared system prompt / tool schema; many users map to same warm backends—watch hot sets.

### 7.2 Capacity & placement

**Q11: Why not least-connections?**  
A: Connections ≠ KV bytes ≠ prefill cost. Multi-dim residual capacity needed.

**Q12: How fresh must capacity be?**  
A: Sub-second to few seconds with headroom. Stale optimistic → OOM; stale pessimistic → underutilization.

**Q13: Oversubscribe?**  
A: Small controlled oversubscribe for decode-only if KV fits; never for huge prefill without check.

**Q14: Power of two choices?**  
A: Sample 2 (or k) candidates; pick better residual. Scales with less global knowledge.

**Q15: Bin packing long-context?**  
A: Treat KV bytes as first-class; may reserve “long-ctx pools” to avoid fragmenting many GPUs.

### 7.3 Compatibility

**Q16: What goes in the matrix?**  
A: Model version, max context, modalities, tool protocol, quantization, tokenizer gen, safety profile id.

**Q17: Latest vs pin?**  
A: Enterprise pins versions; consumer Auto may float within approved set. Document drift.

**Q18: Canary routing?**  
A: Weight % to canary pool; sticky must pin to canary once chosen for session consistency.

**Q19: Silent fallback to smaller model?**  
A: Only if product allows and response marks `degraded`. Otherwise 503.

### 7.4 Overload & fairness

**Q20: Shed vs queue?**  
A: Interactive: short wait then shed. Batch: deeper queues. Unbounded = outage.

**Q21: Retry storms?**  
A: Idempotency, Retry-After, jitter, server-side admit tokens.

**Q22: Tier fairness?**  
A: Reserved capacity pools + weighted fair queue among admitted waiters.

**Q23: Priority preemption?**  
A: Hard—preempting mid-decode wastes work. Prefer admission-time reservation; preemption only for extreme.

**Q24: Load shed signals?**  
A: Pool utilization, KV pressure, p99 TTFT, queue wait, error rate.

### 7.5 Failover & reliability

**Q25: Mid-stream GPU fault?**  
A: Abort; client retries full request; sticky invalidated. Don’t continue on another GPU without state.

**Q26: Circuit breaker vs retry?**  
A: Breaker stops herd on sick backend; limited retries on other backends before first token.

**Q27: Split-brain registry?**  
A: Fencing tokens on register; under-admit; generation numbers.

**Q28: Router crash during stream (proxy mode)?**  
A: Stream dies; incomplete. Phase-2 direct-to-backend survives router death.

### 7.6 Cost & AI infra

**Q29: How does router save money?**  
A: Higher KV hit rate, fewer OOMs, less thrash, shed before useless queueing burns GPUs.

**Q30: Mis-routing cost example?**  
A: Breaking stick every turn on a 20K prompt chat ≈ re-prefill every turn → order-of-magnitude GPU waste.

**Q31: Batch vs online on same hardware?**  
A: Isolate pools or use preemption-safe scheduling; batch can fill valleys but must not steal interactive SLO.

### 7.7 Scalability scenarios

**Q32: 100× backends?**  
A: Hierarchical capacity; pool routers; don’t O(N) scan fleet per request.

**Q33: 5M admits/s?**  
A: Cells; local affinity; minimal Redis; approximate capacity; bloom for negative cache.

**Q34: Multi-tenant noisy neighbor?**  
A: Per-tenant caps at admit; separate pools for abusive tenants.

### 7.8 Consistency edge cases

**Q35: Affinity says B1, B1 drained?**  
A: Miss path; place B2; update affinity.

**Q36: CAS on reservation?**  
A: Backend or router CAS residual; conflicting admits retry place.

**Q37: Clock skew on lease expiry?**  
A: Monotonic lease ids + backend-local expiry; sweeper tolerant.

### 7.9 Alternatives & deal-breakers

**Q38: Why not DNS round-robin to GPUs?**  
A: No capacity, no compatibility, no sticky, no shed—deal-breaker.

**Q39: Why not Kubernetes Service only?**  
A: Useful L4; insufficient LLM placement intelligence.

**Q40: Service mesh least-request?**  
A: Better than RR; still weak on KV/compatibility—use as transport, not policy brain.

### 7.10 Behavioral / communication

**Q41: How do you start the interview?**  
A: Clarify sticky purpose, compatibility hard/soft, overload policy, stream ownership—then estimate admit vs stream classes separately.

**Q42: What do you escalate when unsure?**  
A: Whether mid-stream failover is in scope; whether degrade is allowed; home-region assumption.

---

### Appendix A — Placement pseudocode

```text
function route(req):
  if not idempotency_begin(req): return prior_decision
  candidates = compatible(registry, req.model, req.caps)
  if candidates empty: return Reject(incompatible)

  if req.affinity_key:
    b = affinity.get(req.affinity_key)
    if b in candidates and healthy(b) and can_admit(b, req) and not b.drain:
      lease = reserve(b, req)
      if lease: return Place(b, sticky_hit)

  // cold / spill
  ordered = rank_by_residual(candidates)  // or power-of-two
  for b in ordered:
    if can_admit(b, req):
      lease = reserve(b, req)
      if lease:
        affinity.set(req.affinity_key, b, ttl) if key
        return Place(b, reason)
  return overload_policy(req)  // queue | shed | degrade
```

### Appendix B — Progressive scale checklist

| Scale | Affinity | Capacity | Router topology | Overload |
|-------|----------|----------|-----------------|----------|
| Baseline | Redis | Heartbeat all | Flat fleet | Shed + short queue |
| 10× | Shard Redis | Cached EWMA | Flat + local cache | + tier pools |
| 100× | Per-cell | Aggregators | Pool routers | Cell-local shed |
| 1,000× | Local-first | Gossip | Region × cell | Regional degrade playbooks |

### Appendix C — Metrics that matter

| Metric | Why |
|--------|-----|
| sticky_hit_rate | KV economics |
| stick_break_rate | Pressure / thrash |
| shed_rate{reason} | Overload truth |
| admit_p99 | Control plane health |
| ttft{sticky\|cold} | Prove sticky value |
| kv_oom_near_miss | Capacity model bugs |
| circuit_open_count | Dependency health |
| incompatible_reject | Matrix / client bugs |

### Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Prefill | Process prompt tokens into KV |
| Decode | Autoregressive token generation |
| KV cache | Per-sequence attention state on device |
| Soft sticky | Preference, may spill |
| Headroom | Reserved unused capacity against staleness |
| Drain | Stop new admits; finish in-flight |

### Appendix E — Sample NFR card (hand to interviewer)

```text
Admit p99 < 15ms in-region
Sticky hit ≥ 80% when backends stable
Never route incompatible version
Interactive queue wait ≤ 300ms else 503
Mid-stream FO: incomplete (MVP)
Availability admit 99.99% (degraded placement OK)
```

### Appendix F — Common interviewer pushbacks

| Pushback | Response |
|----------|----------|
| “Just use least connections” | Show KV/token counterexample |
| “Sticky is mandatory” | Soft sticky; correctness = compatibility + stream pin |
| “Retry on other GPU mid-stream” | Need state move; MVP honesty |
| “Queue everyone” | Interactive SLO; GPU $ burned waiting |
| “Global consistent hash” | Hot keys + cross-region tax |

### Appendix G — Worked baseline numbers

```text
Peak admit 5,000 /s
Avg stream duration 8s → concurrent ≈ 5,000 × 8 = 40,000 (~50K order)
500 backends → ~100 streams/backend avg if uniform
Reality skewed → need capacity-aware + sticky spill
Affinity 2M keys × 128B ≈ 256MB raw
Heartbeat 500 backends × 2/s = 1,000/s trivial
Decision log 5,000/s × 500B ≈ 2.5 MB/s ≈ 200 GB/day order
```

### Appendix H — 10× / 100× / 1,000× narrative (30s)

> At 10× we shard affinity and cache capacity. At 100× we cell by model pool so blast radius and candidate sets shrink. At 1,000× affinity and capacity become regional-local; the router optimizes goodput and KV reuse, not perfect global balance—because GPU dollars and TTFT punish thrash more than mild imbalance.

### Appendix I — Related systems map

| System | Relation |
|--------|----------|
| API rate limiter | Upstream of router; different constraint |
| GPU scheduler | Assigns replicas to pools; slower control loop |
| Chat product | Supplies affinity_key; handles incomplete UX |
| Model registry | Source of truth for compatibility |
| Observability | Consumes decision logs |

### Appendix J — Explicit non-goals

- Training job scheduling  
- Weight download / model conversion  
- Safety classifier content policy (may be separate hop)  
- Billing ledger (meter downstream)  
- Guaranteed exactly-once token delivery across FO  

---

*End of Model-Serving Request Router system design.*
