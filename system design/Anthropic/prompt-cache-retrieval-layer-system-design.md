# System Design: Prompt Cache & Retrieval Layer

> **Focus areas:** Cache keys · Exact/prefix/semantic reuse · Model-version invalidation · Tenant privacy · Cost savings · Thundering herd · GPU efficiency  
> **Style:** End-to-end AI infra design with progressive scale (10× → 100× → 1,000×)  
> **Theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — caching, consistency, isolation, reliability, cost  
> **Quality bar:** Correct arithmetic on token/$ savings, explicit privacy isolation, invalidation invariants, no cross-tenant leakage deal-breakers

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

Goal: **bound the product**—a prompt caching and retrieval layer in front of (and inside) LLM inference that reduces repeated prefill cost, improves TTFT, and optionally reuses semantic results—without violating privacy or serving stale generations across model versions.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who consumes the cache? | Inference gateway / API (Messages API), internal agents, batch jobs | Library + sidecar/service; not a user-facing product |
| F2 | Cache types? | **Exact** full prompt; **prefix** (Anthropic-style prompt caching); **semantic** response reuse (optional, stricter) | Layered caches with different guarantees |
| F3 | What is cached? | KV cache blocks / prefill states for prefixes; optionally final responses for identical requests | Separate **KV/prefix** vs **response** stores |
| F4 | Multi-tenant? | Yes — API customers + internal | Hard isolation by `tenant_id` (+ workspace) in every key |
| F5 | Invalidation? | On model version, tokenizer, system prompt template, safety policy major, explicit TTL | Version in key; broadcast invalidate |
| F6 | Privacy? | Never serve tenant A’s cached prefix/response to B | Crypto + key isolation; no shared semantic across tenants |
| F7 | Sticky sessions? | Prefer route to node holding KV blocks | Consistent hashing / cache-aware scheduler |
| F8 | Observability? | Hit rate, savings $, TTFT delta, eviction causes | Metrics first-class |
| F9 | API shape? | Client marks cacheable breakpoints / `cache_control` | Explicit opt-in for billing clarity |
| F10 | Semantic reuse scope? | Phase 1.5; only for idempotent/safe GETlike prompts with policy | Conservative defaults; safety review |
| F11 | Batch vs interactive? | Both; batch loves cache; interactive needs TTFT | Shared layer, different SLOs |
| F12 | Retrieval? | Fetch prior prefix blocks + optional doc snippets for RAG-adjacent reuse | “Retrieval layer” = locate reusable compute/state |

**MVP functional scope (lock with interviewer):**

1. **Prefix prompt caching** (Anthropic-style): client marks cacheable prefix blocks; server stores KV/prefill artifacts keyed by hash + model version + tenant.
2. **Exact response cache** (optional MVP stub): identical request fingerprint → cached completion when policy allows (temp=0, no tools drift).
3. **Invalidation** on model/tokenizer/safety-template version changes.
4. **Tenant isolation** in keys, storage, and metrics.
5. **Cache-aware routing** hints to inference scheduler.
6. **Cost metering**: distinguish cached vs uncached input tokens for billing.
7. **Admin**: hit rates, force-purge by tenant/model, TTL config.

**Out of MVP (explicitly defer):**

- Cross-tenant shared semantic cache of user content
- Perfect global KV migration live between regions
- Caching tool-call side effects
- Learned eviction beyond LRU/LFU + size

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Lookup latency? | Tiny vs prefill | p99 < 5–20ms local; < 50ms remote metadata |
| N2 | TTFT improvement? | Material on long prefixes | 2–10× on large cached prefixes (workload-dependent) |
| N3 | Consistency? | Never wrong-tenant; never wrong-model | Linearizability of isolation invariants |
| N4 | Availability? | Cache miss must not fail request | Fail-open to full prefill |
| N5 | Durability of KV? | Ephemeral OK | Warm Redis/local GPU mem; rebuild on miss |
| N6 | Security? | No cross-tenant read | Keyed isolation + optional encryption per tenant |
| N7 | Cost transparency? | Bill cached tokens cheaper | Metering accurate ± billing SLO |
| N8 | Stampede? | Popular prefixes | Singleflight / request coalescing |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Enterprise sends 50K-token policy prefix + short user Q → first call writes cache → subsequent calls hit prefix → fast TTFT + cheaper input.
2. Same workspace agents share a long tool schema prefix within tenant.
3. Model upgrade → automatic miss → rebuild under new version key.
4. Exact cache hit on temp=0 classification prompt → skip GPU entirely (policy allow).
5. Ops purges tenant on offboarding → all keys gone.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cache store down | Miss path; full prefill; alert |
| Partial prefix hit | Use longest matching cached prefix; prefill remainder |
| Model version skewer | Key includes version; no silent hit across versions |
| Tenant key collision bug | **Incident**; defense: keyed hash + authz check on read |
| Thundering herd on cold popular prefix | Singleflight leader fills; waiters attach |
| Semantic false reuse | Only if enabled; similarity + policy; prefer exact/prefix |
| Huge prefix exceeds cache budget | Admit by priority; reject cache write; still serve |
| Prompt with PII in prefix | Still tenant-isolated; TTL; optional customer “no-store” |
| Tools nondeterminism | Disable response cache when tools/network involved |
| Clock skew TTL | Store absolute expiry; loose sync OK for ephemeral |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| QPS (inference requests) | 5K | 50K | 500K | 5M |
| Cache lookups/s | 5K | 50K | 500K | 5M |
| Prefix write rate | 500/s | 5K/s | 50K/s | 500K/s |
| Unique hot prefixes | 100K | 1M | 10M | 100M |
| Avg cached prefix tokens | 8K | 8–16K | 8–32K | 8–32K |
| KV memory fleet | 5 TB | 50 TB | 500 TB | multi-PB equiv (tiered) |
| Exact response entries | 1M | 10M | 100M | 1B |
| Tenants | 1K | 10K | 100K | 1M |
| Hit rate (prefix token) | 40% | 50% | 55% | 60% (optimistic) |
| Regions | 1 | 2 | 4 | 8+ |

**What each jump forces:**

- **10×:** Distributed metadata; GPU-local KV + remote block store; singleflight.
- **100×:** Hierarchical cache (L1 GPU, L2 host, L3 remote); tenant fair eviction; region stickiness.
- **1,000×:** Prefix block CDN-like distribution; heavy quantization of KV; semantic layer carefully capped.

### 1.5 Etc. (Constraints & Assumptions)

- Aligns with **Anthropic prompt caching** mental model: cacheable **prefixes**, billed differently; breakpoints explicit.
- KV cache is **model-version specific** and generally **not** portable across architectures.
- Response caching is a **stricter** product decision than prefix KV caching.
- Layer sits beside Inference Gateway / scheduler; fail-open.

**Scope statement:**

> Design a prompt cache and retrieval layer supporting tenant-isolated prefix (KV) caching with explicit breakpoints, exact response caching under policy, model-version invalidation, cache-aware routing, stampede control, and accurate cost metering—scaling lookups and KV storage through 10× / 100× / 1,000× while never cross-contaminating tenants or model versions.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline peak | 10× | Notes |
|-------|---------------|-----|-------|
| Metadata lookup | 5K/s | 50K/s | Redis/cluster |
| KV block read | 2K/s hits | 20K/s | Local+remote |
| KV block write | 500/s | 5K/s | Async OK |
| Exact response get | 1K/s | 10K/s | Optional |
| Invalidation fanout | rare bursts | bursts | Pub/sub |
| Metering events | ~QPS | ×10 | Kafka |

### 2.2 Cost savings math (say precisely)

```text
Assume:
  Input price uncached: $3 / 1M tokens
  Input price cached:   $0.30 / 1M tokens  (10× cheaper — illustrative)
  Output: unchanged

Request: 20K prefix + 500 suffix in; 400 out
Uncached input cost ∝ 20.5K tokens
Cached input cost ∝ 0.3×20K + 1.0×500 = 6K + 500 = 6.5K effective-bill tokens
Savings ≈ (20.5K - 6.5K) / 20.5K ≈ 68% of input bill on hit

At 5K QPS × 50% prefix-hit × 20K prefix tokens:
  Cached tokens/s = 5e3 × 0.5 × 2e4 = 5e7 tokens/s
  If discount $2.7 / 1M on those → $0.135 /s → ~$11.7K / day order
Tune numbers with interviewer; show the formula.
```

### 2.3 Prefill compute savings

```text
Prefill FLOPs roughly ∝ tokens × model_dim factors
Hitting 20K-token prefix may cut TTFT from e.g. 2–4s → few hundred ms
GPU goodput: more capacity for unique suffixes / outputs
```

### 2.4 Memory footprint

```text
KV cache size rough: 2 * layers * tokens * dim_head * bytes * ...
Interview-friendly: "tens of MB per 1K tokens per request" order — calibrate
8K prefix × 100K hot keys → if 50 MB each → 5 PB impossible
  → must store shared prefixes once; shard; tier; limit residency
Reality: few thousand ultra-hot prefixes dominate hit rate (Zipf)
Design for Zipf: replicate hot, spill cold
```

### 2.5 Lookup SLA budget

```text
Interactive TTFT budget 500ms
Cache metadata+fetch budget ≤ 20–50ms
Else miss faster than slow remote fetch (hedge)
```

---

## 3. High-Level Design

### 3.1 Mental model: three layers

```text
L0 Exact Response Cache  (optional, strongest reuse, strict policy)
L1 Prefix / KV Cache     (Anthropic-style; primary)
L2 Semantic Reuse        (Phase 1.5; similarity → prior answer; risky)
```

| Layer | Key basis | Reuses | Risk |
|-------|-----------|--------|------|
| Exact response | Full request fingerprint | Output tokens | Stale/wrong if nondeterministic |
| Prefix KV | Hash(prefix blocks)+model+tenant | Prefill state | Low if versioned |
| Semantic | Embedding near-dup | Prior output | High; privacy + correctness |

### 3.2 Anthropic-style prefix caching

```text
Messages with cache_control breakpoints:
  [System big] cacheable
  [Tools schema] cacheable
  [Docs] optional cacheable
  [User turn] usually not

Server:
  tokenize → split at breakpoints → hash each block chain
  lookup longest-prefix hit for (tenant, model_version, block_hashes…)
  load KV / continue prefill from breakpoint
  stream decode as usual
  write new blocks asynchronously
```

**Billing:** report `cache_read_input_tokens`, `cache_creation_input_tokens`, `input_tokens`.

### 3.3 Cache key design

```text
PrefixKey =
  hash(
    tenant_id,
    workspace_id?,
    model_version,
    tokenizer_version,
    safety_template_version,
    block_hash_chain,   # cumulative hashes of cacheable blocks
    dtype_kv_layout     # implementation tag
  )

ResponseKey =
  hash(
    PrefixKey inputs +,
    full message list hash,
    decoding_params,    # temp, top_p, max_tokens, seed
    tool_config_hash,
    api_policy_flags
  )
```

**Invariant:** `tenant_id` is not optional. Missing tenant → reject.

### 3.4 Privacy isolation

| Mechanism | Purpose |
|-----------|---------|
| Key prefix `tenant_id` | Namespace |
| AuthZ check on read | Defense in depth |
| Per-tenant encryption keys (optional) | Confidentiality at rest |
| No cross-tenant semantic index | Prevent side channels |
| Metrics aggregated | Don’t leak prompt content |
| Customer no-store / zero-retention | Skip writes |

**Deal-breaker:** any design that “shares popular system prompts across tenants” for user-supplied content without cryptographic/tenant boundary. Platform-owned public templates may be global; **customer content never is**.

### 3.5 Invalidation

| Event | Action |
|-------|--------|
| New `model_version` | Natural miss (key change) |
| Tokenizer change | Version bump in key |
| Safety system template major | Version bump |
| Explicit purge API | Delete by tenant/prefix/model |
| TTL expiry | Lazy delete |
| Vulnerability / data purge | Active fanout delete |

Prefer **versioned keys** over chasing deletes for model rolls. Active purge for privacy offboarding.

### 3.6 Retrieval layer responsibilities

```text
On request:
  1. Normalize messages + breakpoints
  2. Retrieve ResponseKey hit? (policy) → return
  3. Retrieve longest PrefixKey hit → location (node, block_ids)
  4. Scheduler places request on node with blocks (or fetch remote)
  5. Inference resumes
  6. Async write new blocks / response
```

“Retrieval” here means **retrieving reusable compute state**, not document RAG (though RAG doc prefixes benefit heavily).

### 3.7 Thundering herd / singleflight

```text
Cold key K popular:
  Waiters enter singleflight group(K)
  Leader does prefill + cache write
  Followers attach to same prefill result OR wait for KV publish then resume
Timeout → followers fall back to independent prefill (duplicate work OK)
```

### 3.8 API shape (gateway-facing)

```http
POST /v1/messages
{
  "model": "claude-X",
  "system": [{"type":"text","text":"....", "cache_control":{"type":"ephemeral"}}],
  "messages": [...],
  "temperature": 0
}
```

Response usage:

```json
{
  "usage": {
    "input_tokens": 20500,
    "cache_creation_input_tokens": 20000,
    "cache_read_input_tokens": 0,
    "output_tokens": 400
  }
}
```

Admin:

| Method | Path | Purpose |
|--------|------|---------|
| DELETE | `/internal/cache/tenants/{id}` | Purge tenant |
| POST | `/internal/cache/invalidate` | By model/version |
| GET | `/internal/cache/stats` | Hit rates |

### 3.9 Trade-offs table

| Decision | Options | Choice |
|----------|---------|--------|
| Response cache default | on/off | Off unless temp=0 & safe |
| KV store | GPU-only vs distributed | Hierarchical L1/L2/L3 |
| Semantic | yes/no MVP | Defer; design hooks |
| Fail mode | fail-open/closed | **Fail-open** miss |
| Cross-region KV | replicate vs sticky | Sticky home region MVP |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-----------+    +------------------+    +---------------------+
| Clients   |--->| Inference        |--->| Prompt Cache        |
| (API)     |    | Gateway          |    | Controller          |
+-----------+    +--------+---------+    +----------+----------+
                          |                         |
                          |                 +-------+--------+
                          |                 | Metadata Index |
                          |                 | (Redis/etcd)   |
                          |                 +-------+--------+
                          v                         |
                 +----------------+                 v
                 | Scheduler      |<----hints--+----+
                 | (cache-aware)  |            |
                 +--------+-------+            v
                          |           +----------------+
         +----------------+           | Block Store L3 |
         v                            | (remote KV)    |
+-------------------+                 +----------------+
| Inference Node    |
|  L1 GPU KV        |
|  L2 Host DRAM     |
|  Engine           |
+-------------------+

Side path:
 Gateway → Exact Response Cache (Redis/CDN-ish) → short-circuit
 Metering → Kafka → Billing
 Invalidate bus → all controllers
```

### 4.2 Lookup sequence

```text
Gateway
  → build keys
  → ResponseCache.get → HIT? return
  → PrefixCache.longest_hit
  → schedule(node)
  → engine.load_blocks / prefill_tail
  → decode
  → async write
  → meter
```

### 4.3 Isolation diagram

```text
Tenant A keys ----\          /---- Nodes pool A-affinity optional
                   > Index  <
Tenant B keys ----/          \---- Never returns A blocks to B request
AuthZ(tenant) checked on every block fetch
```

---

## 5. Design Deep Dive

### 5.1 Reliability

| Failure | Behavior |
|---------|----------|
| Metadata Redis down | Miss; continue |
| Block fetch corrupt | Checksum fail → miss; report |
| Leader crash in singleflight | Waiters timeout → solo prefill |
| Partial write | Publish only after checksum; readers never see half blocks |
| Version skew deploy | Keys include layout version |

**Checksums:** every block has `crc/sha`; engine verifies on load.

**Idempotent writes:** same PrefixKey rewrite OK (same bytes).

### 5.2 Scalability

**Hierarchical cache:**

```text
L1: per-GPU resident KV (hottest)
L2: host/node shared memory / NVMe
L3: remote block store (optional compressed/quantized)
Metadata: global sharded Redis
```

**Placement:**

- Consistent hash `(tenant, prefix_hash)` → preferred node set.
- Scheduler scores nodes: cache affinity + load + GPU mem.
- Steal/fetch remote blocks if affinity overloaded.

**Eviction:**

- Global token budget per tenant (fairness).
- LFU/LRU within tier; protect pinned platform templates.
- Prefer evicting large cold prefixes first.

**100×:** shard metadata by tenant; region-local L3.  
**1,000×:** KV quantization; prefix block streaming; admission control on writes.

### 5.3 Maintainability

- Clear module boundaries: keying, metadata, block IO, scheduler hooks, metering.
- Compatibility tests when KV layout changes (layout version bump).
- Chaos: kill L3 mid-fetch.
- Dashboards: hit rate by tenant percentile (watch whales).

### 5.4 Exact vs prefix vs semantic (depth)

**Exact response cache**

- Pros: skip GPU; max savings.  
- Cons: wrong if nondeterminism, time-dependent tools, safety policy change mid-TTL.  
- Allow only: `temperature=0`, no live tools, pinned model, short TTL, tenant-scoped.

**Prefix KV**

- Pros: works with unique suffixes; core product.  
- Cons: memory heavy; sticky routing complexity.

**Semantic**

- Pros: paraphrase hits.  
- Cons: privacy (embedding index), correctness, safety.  
- If ever: threshold high; human-eval offline; never cross-tenant; disable for high-risk classifiers.

### 5.5 Cost & metering

```text
On each request emit:
  tenant, model, cache_read_tokens, cache_write_tokens, uncached_input, output
Billing pipeline aggregates
Fraud: detect anomalous “write-only” patterns burning creation credits
```

**Write amplification:** clients re-sending huge prefixes with tiny mutations should still hit long common chain—educate with docs; optional server normalization.

### 5.6 Thundering herd detail

```text
singleflight.Do(key):
  if inflight: wait(cond, timeout)
  else: mark inflight; prefill; publish; broadcast

Hedged request: if wait > T_hedge, start parallel prefill (cap duplicates)
```

Also coalesce identical ResponseKey interactive requests.

### 5.7 Security deep dive

- Side channel: timing of hits might leak whether a prefix exists **within tenant**—usually acceptable; cross-tenant timing must not leak.
- Shared GPU memory scrubbing between tenants on context switch.
- Encrypt L3 blocks with tenant DEK.
- Audit purge operations.
- Prompt injection into cached system prefixes: treat as content; safety still runs on full assembled request.

### 5.8 Interaction with continuous batching

```text
Cached prefix hits let decode start earlier → better interactive batching mix
Engine must support loading external KV into running schedules
Padding/layout alignment constraints → part of layout_version
```

### 5.9 Multi-region

- MVP: **home region** cache; cross-region miss (full prefill) rather than sync KV.
- DR: no durable dependency; cold start OK.
- Global customers: replicate **platform** templates only.

### 5.10 Privacy-preserving analytics

```text
Store: hit/miss counters, token histograms, sizes
Don’t store: raw prompts in metrics systems
Debug: customer-authorized replay tools with ACL
```

---

## 6. Wrap-Up

### 6.1 What we designed

A **prompt cache & retrieval layer** centered on tenant-isolated, model-versioned **prefix KV caching** with explicit breakpoints, optional exact response short-circuit, fail-open misses, cache-aware scheduling, singleflight stampede control, and billing-grade metering—plus a cautious path toward semantic reuse.

### 6.2 Progressive scale

| Scale | Change |
|-------|--------|
| Baseline | Redis metadata + node L1/L2 KV |
| 10× | Singleflight; affinity scheduling; purge APIs |
| 100× | L3 remote blocks; tenant fair eviction; multi-region sticky |
| 1,000× | Quantized KV; Zipf-aware replication; strict semantic caps |

### 6.3 Deal-breakers

1. Cross-tenant cache hit.  
2. Hit across `model_version` / tokenizer mismatch.  
3. Fail-closed cache outage taking down inference.  
4. Response cache on tool-using nondeterministic calls by default.  
5. Billing that can’t distinguish cache read vs write tokens.

### 6.4 Closing line

> Prefix keys carry tenant and model version; misses fail open; hits save prefill and dollars; herds singleflight; customer content never becomes a global shared brain.

---

## 7. Deeper / Related Interview Questions

### 7.1 Why not cache only exact full prompts?

**A:** User suffixes change constantly; prefix reuse captures the bulk tokens (system, tools, docs). Exact-only leaves money on the table.

### 7.2 How do breakpoints work?

**A:** Client marks cacheable segments; server hashes cumulative prefixes; longest valid cached chain loads; remainder prefills.

### 7.3 What goes into the cache key?

**A:** Tenant, model version, tokenizer, safety template version, block hash chain, KV layout—not just raw text.

### 7.4 How do you invalidate on model roll?

**A:** New version ⇒ new keys (implicit). Active purge optional for disk. Don’t rely on TTL alone for correctness.

### 7.5 Fail-open vs fail-closed?

**A:** **Fail-open** to full prefill for availability. Privacy violations are the opposite class—there fail closed (deny hit).

### 7.6 How do you prevent thundering herds?

**A:** Singleflight per key, wait timeouts, hedged prefills with caps, pre-warm hot enterprise prefixes.

### 7.7 Semantic cache risks?

**A:** Wrong answer reuse, cross-user leakage via embeddings, safety bypass. Keep opt-in, tenant-scoped, high threshold, no tools.

### 7.8 How does this interact with safety classifiers?

**A:** Safety still runs on full request/response. Cache does not skip policy. Policy version in key prevents stale allow.

### 7.9 GPU memory pressure?

**A:** Admission control on writes; fair per-tenant budgets; evict cold; prefer L2/L3 spill; never OOM-kill interactive unfairly.

### 7.10 Cache-aware scheduling vs load balancing?

**A:** Score hybrid: `affinity_score * w1 - load * w2`. Pure affinity creates hotspots; pure load destroys hit rate.

### 7.11 How do you bill fairly?

**A:** Meter creation vs read tokens separately; publish prices; include in usage objects; audit pipeline.

### 7.12 Can two workspaces in one tenant share?

**A:** Product choice: default isolate by workspace; allow explicit share for org-managed prefixes.

### 7.13 Zero-retention customers?

**A:** `no-store` flag: skip writes; still allow ephemeral in-request reuse only if policy says; typically disable durable cache.

### 7.14 How large a prefix before diminishing returns?

**A:** Diminishing on memory; still valuable for TTFT. Cap max cacheable prefix; document sweet spots (e.g. 2K–100K+).

### 7.15 Partial hits?

**A:** Longest prefix match; prefill from breakpoint; write extended chain.

### 7.16 Does temperature affect prefix KV?

**A:** KV for prefix prefill generally OK across temps; **response** cache must include decoding params.

### 7.17 Cross-region replication of KV?

**A:** Expensive and version-fragile. Prefer sticky region; accept miss on failover.

### 7.18 How to test for cross-tenant leakage?

**A:** Chaos/prop tests: random tenants, assert no foreign key read; red-team timing; code audit of key builder.

### 7.19 Exact cache and streaming?

**A:** On hit, replay streamed tokens from stored sequence or send as one chunk per product UX; preserve event shape if clients depend.

### 7.20 What metrics matter most?

**A:** Token hit rate, request hit rate, TTFT delta, $ saved, eviction causes, singleflight wait, error/miss reasons.

### 7.21 Zipf workloads?

**A:** Tiny head of prefixes → most savings. Replicate head; don’t over-invest in long-tail residency.

### 7.22 Prompt mutation anti-patterns?

**A:** Putting timestamps/nonces in system prefix kills hits. Keep dynamic data after breakpoint.

### 7.23 Relation to RAG?

**A:** Retrieved docs as cacheable mid-prefixes help multi-turn; doc updates need version in block hash (content hash handles).

### 7.24 KV quantization?

**A:** At extreme scale, store compressed KV with quality evals; layout_version changes invalidate.

### 7.25 Multi-modal prefixes?

**A:** Image embeddings/KV heavier; separate caps; often less reusable; key must include media hashes.

### 7.26 Batch inference interaction?

**A:** Huge wins when many jobs share schemas; pre-warm; prioritize write once read many.

### 7.27 Legal hold / purge?

**A:** Purge APIs by tenant; verify via metadata scan; document async L3 delete completion.

### 7.28 Can cache hide a model bug after fix?

**A:** Response cache TTL + version pins. Prefix KV with new model version auto-misses. Flush response cache on emergency.

### 7.29 Why layout_version in key?

**A:** Engine changes (packing, dtype) make old KV unreadable or wrong—force miss.

### 7.30 Summarize Anthropic angle

**A:** Prompt caching is an economic and latency feature with **privacy as a hard invariant**—ordinary cache keys, TTLs, and singleflight, applied to GPU KV and token billing.

### 7.31 Hedge vs wait on singleflight?

**A:** Wait up to T; hedge if leader slow; bound duplicate prefills (e.g. max 2).

### 7.32 Metadata store choice?

**A:** Redis cluster for TTL/speed; persistent records optional for analysis not correctness.

### 7.33 How to expose UX to developers?

**A:** `cache_control` breakpoints; usage fields; docs on structuring prompts; dashboard hit rates.

### 7.34 Fairness across tenants?

**A:** Per-tenant memory quotas; prevent one whale pinning fleet KV; burst credits.

### 7.35 Cold start after deploy?

**A:** Expected miss storm; pre-warm top prefixes; scale GPU for rollout windows.

### 7.36 Security of block store?

**A:** AuthZ, encryption, checksums, network policy only from inference plane.

### 7.37 Idempotency of client retries?

**A:** Same key writes fine; response cache helps identical retries; ensure at-most-one side effects elsewhere.

### 7.38 What not to cache?

**A:** Secrets flagged no-store, live tool results, personalized highly sensitive turns (policy), cross-tenant anything.

### 7.39 How does this affect eval platforms?

**A:** Evals with shared rubrics save huge $ via prefix cache; pin versions so results stay reproducible.

### 7.40 One-liner

**A:** Versioned, tenant-keyed prefix KV with fail-open misses, stampede control, and honest billing—semantic reuse only with a seatbelt.

---

## Appendix A: Key schema examples

```text
pfx:v1:{tenant}:{model}:{tok}:{safety}:{layout}:{cumhash}
rsp:v1:{tenant}:{model}:{fullhash}:{decodehash}
```

## Appendix B: Usage accounting fields

| Field | Meaning |
|-------|---------|
| `input_tokens` | Total input seen |
| `cache_creation_input_tokens` | Written to cache |
| `cache_read_input_tokens` | Read from cache |
| `output_tokens` | Generated |

## Appendix C: Admission control policy

```text
admit_write if:
  size <= max_prefix
  tenant_used + size <= tenant_quota
  global_used + size <= global_quota
  priority >= min_priority OR expected_reuse high
else: serve without write
```

## Appendix D: Longest-prefix algorithm

```text
hashes = cumulative_block_hashes(blocks)
for i from n downto 1:
  if metadata.exists(key(hashes[i])): return i
return 0
```

## Appendix E: Scheduler score

```text
score = w_aff * cache_hit_tokens(node)
      - w_load * node_queue_wait
      - w_mem * kv_pressure
      + w_locality * rack_bonus
```

## Appendix F: Invalidation bus messages

```json
{"type":"purge_tenant","tenant_id":"..."}
{"type":"purge_model","model_version":"..."}
{"type":"bump_safety","safety_template_version":"..."}
```

## Appendix G: Semantic layer hooks (Phase 1.5)

```text
embed(normalized_prompt) → ANN within tenant
if sim > τ AND policy_allows AND model_version match:
  return prior response with provenance header
else miss
```

## Appendix H: Failure injection matrix

| Chaos | Expect |
|-------|--------|
| Redis down | Miss path OK |
| Corrupt block | Miss + metric |
| Slow L3 | Hedge prefill |
| AuthZ deny | Never return data |
| Burst cold key | Singleflight |

## Appendix I: Cost worksheet template

```text
daily_requests = _
hit_rate = _
avg_prefix = _
uncached_price = _
cached_price = _
savings = daily_requests * hit_rate * avg_prefix/1e6 * (uncached_price-cached_price)
```

## Appendix J: Hot prefix pre-warm

```text
nightly job:
  top_k prefixes by hits
  for each: schedule dummy prefill on N nodes (tenant platform only)
enterprise: customer-initiated warm endpoint
```

## Appendix K: TTL defaults (illustrative)

| Class | TTL |
|-------|-----|
| Ephemeral prefix | 5–60 min |
| Enterprise pinned | hours (paid) |
| Exact response | 30–300 s |
| Semantic | short + strict |

## Appendix L: Observability red flags

- Hit rate ↓ after deploy → layout/version bug  
- One tenant 90% KV → fairness fail  
- cache_creation ≫ cache_read → breakpoint misuse  
- Cross-version hits > 0 → **sev-1**  

## Appendix M: Node lifecycle

```text
Node join → announce capacity
Node drain → stop new affinity; keep serving; blocks age out
Node death → metadata entries expire; rebuild on demand
```

## Appendix N: Client best practices (teach in interview)

1. Stable system + tools before breakpoint  
2. Dynamic user content after  
3. Don’t put `now()` in cached prefix  
4. Reuse same model string  
5. Watch usage fields in staging  

## Appendix O: Whiteboard checklist

1. Layers: response / prefix / semantic  
2. Key fields including tenant + model  
3. Fail-open  
4. Singleflight  
5. Hierarchy L1/L2/L3  
6. Invalidation via versioning  
7. Metering  
8. Deal-breaker: cross-tenant  

---

*End of document — Prompt Cache & Retrieval Layer (Anthropic interview prep)*
