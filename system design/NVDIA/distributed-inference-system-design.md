# System Design: Distributed Inference Across GPU Nodes

> **Focus areas:** Continuous batching · KV cache · Tensor-parallel serving · Request routing · PagedAttention-style memory · SLA latency · Autoscaling · Multi-model · Speculative decoding (optional)  
> **Style:** NVIDIA-flavored ML systems interview — progressive scale on QPS / latency / model size (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic on tokens/s, KV bytes, batching efficiency; split control-plane vs token-generation load; honest TTFT vs TPOT; resolved ownership of routing vs replica state

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

Goal: **bound the inference product**—interactive LLM serving vs offline batch, latency SLOs (TTFT/TPOT), and which multi-GPU / multi-node techniques are in scope on NVIDIA hardware.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who calls the API? | Apps, agents, internal tools; multi-tenant | Authz, quotas, fair scheduling of requests |
| F2 | Model sizes? | 7B–70B common; 100B+ needs multi-GPU | TP / PP serving; not all models single-GPU |
| F3 | APIs? | Chat/completions streaming + non-streaming | SSE/gRPC streams; cancel mid-decode |
| F4 | Latency SLO? | Interactive: low TTFT + stable TPOT | Continuous batching + admission control |
| F5 | Batching? | Continuous / in-flight batching required | Iteration-level scheduler (vLLM-style) |
| F6 | KV cache? | Yes; prefix reuse nice-to-have | Paged KV; optional prefix cache |
| F7 | Multi-model? | Many models/LoRAs per cluster | Model registry + replica sets + affinity |
| F8 | Scaling? | Autoscale replicas on load / queue | HPA on tokens/s, queue depth, KV pressure |
| F9 | Routing? | Least-load / cache-aware / model-aware | Gateway + replica load signals |
| F10 | Multi-node? | TP across GPUs/nodes for large models | NCCL for TP; careful placement |
| F11 | Speculative decoding? | Optional stretch | Draft+verify path; quality/latency trade |
| F12 | Observability? | TTFT, TPOT, tokens/s, KV hit, OOM, preemptions | Cardinality-safe telemetry |

**MVP functional scope (lock with interviewer):**

1. OpenAI-compatible (or similar) **completions/chat** API with streaming.  
2. Model deployment: register weights → launch **replica** (1 GPU or TP group).  
3. **Continuous batching** decode loop with paged KV cache.  
4. Request **admission** under max KV / max batched tokens.  
5. Gateway routes by model to healthy replicas; health checks.  
6. Autoscale replica count (manual OK for tiny MVP; hooks required).  
7. Metrics + structured traces per request_id.

**Out of MVP:**

- Perfect global KV memory sharing across all nodes  
- Cross-region active-active sticky sessions for prefix cache  
- Full LoRA multiplexing of thousands of adapters without design  
- Guaranteed bit-identical outputs under speculative decoding  
- Training-time features (grad, checkpoint train)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT (time to first token) | Interactive | p50 < 200–500ms, p99 < 1–2s (in-region, warm) |
| N2 | TPOT (time per output token) | Smooth stream | p50 ~ model capability; p99 < 2–3× p50 |
| N3 | Availability | Serving HA | 99.9% API; multi-replica |
| N4 | Correctness | Tokenization + stop rules | Deterministic under temp=0 + fixed seeds (best effort) |
| N5 | Isolation | Noisy neighbor limited | Per-tenant QPS/concurrency tokens |
| N6 | Efficiency | High GPU util without SLO breach | Batch tokens high; KV fragmentation low |
| N7 | Scale | See table | From 10 to 100k+ QPS class fleets |
| N8 | Cold start | Model load time bounded | Large models: minutes; use pool warming |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client streams chat → gateway auth → replica admits → prefill → decode loop emits tokens → finish → usage accounting.  
2. Short prompt hits **prefix cache** → faster TTFT.  
3. Load rises → autoscaler adds replicas → gateway registers → traffic spreads.  
4. Client cancel → abort sequence; free KV blocks.  
5. Multi-GPU TP replica serves 70B model with single logical replica endpoint.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| KV memory full | Reject new admits (429/503) or preempt lowest-priority request |
| Mega prompt exceeds max seq | 400 validation; don’t OOM mid-prefill |
| Replica crash mid-stream | Client error/retry; no silent corruption; gateway marks unhealthy |
| Hot key / viral prompt | Prefix cache helps; still need more replicas for decode |
| Tenant flood | Fair queues / token buckets; protect others’ TTFT |
| TP rank death | Fail whole replica (gang); restart replica set |
| Slow tokenize / safety filter | Count in TTFT; isolate on CPU pool if needed |
| Speculative reject storm | Fall back to normal decode; watch verify accept rate |
| Heterogeneous SKUs | Separate pools; don’t mix TP across SKUs |
| Rolling weight update | New revision replicas; drain old; pin traffic by % |

### 1.4 Scales (Progressive)

Axes: **QPS · concurrent streams · model size · tokens/s fleetwide**.

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak request QPS | 50 | 500 | 5,000 | 50,000 |
| Concurrent active generations | 500 | 5,000 | 50,000 | 500,000 |
| Avg input tokens | 1,000 | 1,000 | 1,500 | 2,000 |
| Avg output tokens | 300 | 300 | 400 | 500 |
| Models served | 5 | 20 | 100 | 500 |
| Replica GPUs (fleet) | 64 | 640 | 6,400 | 64,000 |
| Largest model | 7B (1×GPU) | 70B (2–8×TP) | 70B–405B | MoE / multi-node PP |
| Tokens/s fleet (out) | ~20K | ~200K | ~2M | ~20M |
| Gateway RPS | 50 | 500 | 5K | 50K |
| KV pool GB (fleet) | ~2 TB | ~20 TB | ~200 TB | ~2 PB |

**What each jump forces:**

- **10×:** Continuous batching mandatory; paged KV; horizontal replicas; basic autoscaling.  
- **100×:** Cache-aware routing; disagg prefill/decode optional; multi-model bins; stronger admission.  
- **1,000×:** Hierarchical gateways; pooled KV tiers; speculative decoding; topology-aware TP; telemetry aggregation; cell isolation per tenant/model family.

### 1.5 Etc. (Constraints & Assumptions)

- NVIDIA GPUs (A100/H100/L40S etc.); TensorRT-LLM / vLLM-like engines are acceptable mental models.  
- **Synchronous token generation** on GPU; CPU does tokenize/detokenize/orchestration.  
- We schedule **requests onto replicas**, not training gangs—but large TP replicas still need **gang placement** from GPU RM.  
- Networking: NVLink inside TP node(s); IB if multi-node TP/PP.  
- “QPS” alone is misleading—**tokens/s and KV bytes** drive capacity.

**Scope statement:**

> Design a multi-tenant distributed LLM inference system on NVIDIA GPUs: gateway routing, continuous batching with paged KV cache, tensor-parallel replicas for large models, SLA-aware admission and autoscaling, multi-model serving, and progressive scale from tens to tens of thousands of QPS with explicit TTFT/TPOT math.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| **API / gateway** | 50 RPS | 50K RPS | Control + streaming fanout |
| **Prefill compute** | Burst on prompt | Huge | Compute-bound; TTFT driver |
| **Decode compute** | Steady tokens | Huge | Memory-bandwidth bound often |
| **KV cache memory** | Grows with concurrency × seq | Dominant capacity | Often limits concurrency first |
| **TP collectives** | Per layer decode | Critical for multi-GPU | Latency jitter |
| **Telemetry** | Per-request | Cardinality risk | Sample traces |

**Deal-breaker:** sizing only on QPS while ignoring **output tokens × concurrent × KV**.

### 2.2 KV cache arithmetic (critical)

```text
KV bytes ≈ 2 × layers × num_kv_heads × head_dim × seq_len × bytes_per_elem × batch_or_pages
(For MHA; GQA/MQA reduce num_kv_heads)

Example (order-of-magnitude interview):
7B-class model: ~0.5–1 MB per token of KV (varies widely—state assumptions!)
Better: derive from config.

Suppose: 32 layers, GQA with 8 kv heads, dim 128, FP16:
per token = 2 × 32 × 8 × 128 × 2 ≈ 131 KB per token

1k concurrent seqs × avg 2k tokens resident ≈ 2e6 tokens × 131 KB ≈ 262 GB KV
→ many GPUs of memory just for KV
```

**PagedAttention-style:** allocate KV in blocks (e.g. 16–64 tokens); reduce fragmentation; share prefix pages.

### 2.3 Throughput: prefill vs decode

```text
Prefill: highly parallel matmuls; high tokens/s/GPU possible
Decode: 1 token/step/seq; often memory-bound; batching many seqs raises util

Effective output tokens/s/GPU depends on:
  - model size / SKU bandwidth
  - batch size (#seqs)
  - avg context length (KV read grows)

Interview honesty:
  H100 70B TP=2 might do hundreds of output tokens/s aggregated under good batching—
  quote a working assumption and stick to it for capacity.
```

Example capacity sketch:

```text
Assume 1 GPU serves 7B at ~3000 output tokens/s at good batch
Baseline fleet 64 GPU → ~192k tokens/s theoretical
Needed: 50 QPS × 300 out ≈ 15k tokens/s → OK headroom
At 1,000×: 50k QPS × 500 out = 25M tokens/s → need ~8k+ GPUs at that efficiency
(Real: efficiency drops with long context → more GPUs)
```

### 2.4 Latency budget

```text
TTFT ≈ queue_wait + tokenize + prefill(time) + first_decode_overhead
prefill_time ≈ f(prompt_tokens, batch_interference)

TPOT ≈ decode_iteration_time (affected by batch size & KV length)

SLO control knobs:
  - max batched tokens / max #seqs
  - prefill chunking
  - separate prefill/decode pools (disagg)
  - admission thresholds
```

### 2.5 Streaming bandwidth

```text
50k concurrent streams × 40 tokens/s × 4 B/token ≈ 8 MB/s  (tiny)
Metadata/heartbeats dominate more than token payload at gateway—
connection count / HTTP2 or gRPC concurrency is the real issue
```

### 2.6 Multi-GPU TP latency

```text
Each decode layer may AllReduce/AllGather activations across TP ranks
TP=8 across NVLink: OK
TP across nodes: add IB latency → TPOT jitter; prefer NVLink domains
```

### 2.7 Critical bottlenecks (rank ordered)

1. **KV memory / fragmentation** limiting concurrency  
2. **Decode memory bandwidth** under long contexts  
3. **Head-of-line** from giant prefills blocking interactive TTFT  
4. **Hot model** replica imbalance  
5. **TP collective jitter** on bad topology  
6. **Autoscaler lag** → SLO burn during spikes  
7. **Telemetry/log cardinality**  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
ModelRevision   → weights + tokenizer + config + parallel plan
Replica         → one schedulable serving unit (1 GPU or TP gang)
Engine          → continuous batching loop + paged KV manager
Scheduler       → picks prefills/decodes each iteration under budgets
Gateway         → auth, route, stream, retry/cancel
Admission       → max KV blocks, max waiting queue, tenant tokens
Autoscaler      → replicas = f(queue, tokens/s, KV pressure, lag)
PrefixCache     → optional shared pages by prompt hash (per replica or pool)
```

**Request states:**

```text
RECEIVED → WAITING → PREFILL → DECODING → COMPLETED
               │         │          │
               +---- REJECTED / CANCELLED / PREEMPTED
```

### 3.2 Options: engine architecture

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Static batching | Simple | Bad TTFT/util | Interactive SLOs |
| B. Continuous batching + paged KV | High util + good latency | Complexity | — **MVP choice** |
| C. Disagg prefill/decode | Isolates TTFT vs TPOT | Network KV transfer | Ignoring transfer costs |
| D. One request per GPU | Predictable | Awful cost | Cost-sensitive serving |

**Chosen path:** B for MVP; mention C at 100× for SLO isolation.

### 3.3 Continuous batching loop

```text
loop iteration:
  1. Free finished sequences; reclaim KV blocks
  2. Admit waiting requests if KV blocks + budget allow
  3. Build batch: mix prefills (chunked) + decodes
  4. Execute model step (TP collectives inside)
  5. Sample next tokens; append; emit to streams
  6. Apply stop / max_tokens / cancel
```

**Budgets:** `max_num_seqs`, `max_num_batched_tokens`, `max_kv_blocks`.

### 3.4 Paged KV memory (PagedAttention-style)

```text
Logical KV[seq, layer, pos] → physical BlockPool pages
Block table per sequence
Prefix sharing: identical early pages refcount++

Alloc on prefill/decode growth
Free on complete/cancel/preempt
Defrag: optional compaction when fragmentation high
```

**Invariant:** never overwrite a page still referenced; refcount = 0 ⇒ free.

### 3.5 Tensor-parallel serving

```text
Replica = gang of TP ranks
Gateway sees one replica_id endpoint (leader or shard-aware stub)
Internal: NCCL TP groups; same iteration lockstep
Failure of any rank → replica unhealthy → restart gang
```

| Placement | Guidance |
|-----------|----------|
| TP≤8 | Prefer single HGX/DGX NVLink domain |
| Larger | Multi-node TP/PP only with topology-aware RM |
| PP serving | Possible for huge models; adds pipeline bubbles/latency |

### 3.6 Request routing

| Policy | Use | Notes |
|--------|-----|-------|
| Random / RR | Stateless baseline | Ignores load |
| Least outstanding tokens | Default good | Needs load metrics |
| KV / prefix-aware | Hot prompts | Sticky by hash prefix |
| Latency-aware | SLO classes | Separate pools P0/P1 |
| Model/revision pin | Multi-model | Hard constraint |

**Deal-breaker:** routing to replicas without knowing **KV pressure** → cascading OOMs/rejects.

### 3.7 Multi-model serving

```text
Cluster:
  Pool_A: model Llama-70B-TP4 replicas
  Pool_B: many 7B single-GPU replicas
  Pool_C: LoRA-enabled base + adapters

Gateway route key = (model_id, revision, lora_id?)
Bin-pack small models via MIG or multi-model per GPU only if engine supports safe isolation
```

**MVP:** one model per replica process; many replicas. Multi-model-per-GPU as optimization.

### 3.8 SLA, fairness, admission

```text
Tenant token bucket: QPS + concurrent streams + max tokens/min
Priority bands: interactive > batch offline
Admission:
  if free_kv_blocks < estimate(prompt, max_new): queue or reject
  if wait_queue > Qmax: reject fast (fail-fast better than unbounded TTFT)
Preempt:
  kill lowest priority / farthest from finish to free KV under pressure
```

### 3.9 Autoscaling

```text
signals:
  - waiting_queue_depth
  - ttft_p99
  - gpu_busy / tokens_per_sec
  - kv_utilization
  - gateways 5xx/429 rate

actions:
  scale_out replicas (cold start aware)
  scale_in with idle hysteresis
  prefer scale pool for hot models first
```

**Cold start:** keep min replicas warm; use smaller speculative pools for spiky models.

### 3.10 Speculative decoding (optional)

```text
Draft model (small) proposes K tokens
Target model verifies in parallel-ish
Accept prefix until mismatch; emit accepted

Good: higher tokens/s when accept rate high
Bad: extra compute if accept rate low; complexity
```

Expose as optimization after MVP SLOs met.

### 3.11 Ownership & invariants

| Concern | Owner |
|---------|-------|
| Client API / auth | Gateway |
| Which replica | Router | 
| Request admission & batching | Engine scheduler |
| KV pages | KV block manager |
| GPU devices | GPU RM leases for replica gangs |
| Autoscale decisions | Autoscaler + RM capacity |
| Model artifacts | Registry / object store |

**Invariants:**

1. A KV block has well-defined refcount; no use-after-free.  
2. TP replica ranks share one iteration clock—no partial serve.  
3. Cancel frees KV eventually (bounded).  
4. Streaming never emits tokens after client cancel ACK path completes.  
5. Router never sends to NOT_READY replicas.

### 3.12 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Batching | Continuous + paged KV | Util + latency | Static batch only |
| Large models | TP replica gang | Fits weights | Silently CPU offload in hot path |
| SLO protection | Admission + max batch tokens | Bound TTFT | Infinite queue |
| Scale | Horizontal replicas | Simple | One mega multi-tenant engine process only |
| Prefix cache | Per-replica then pooled | Incremental | Global coherent KV fantasy day 1 |
| Metrics | Hierarchical | Cardinality | Per-token Prometheus labels |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
+----------+     +----------------+     +------------------+
| Clients  |---->| API Gateway    |---->| Router / LB      |
+----------+     | auth,quota,SSE |     +--------+---------+
                 +----------------+              |
                      |                          v
                      |              +-----------+------------+
                      |              |  Model A replicas      |
                      |              |  [Eng|KV|TP ranks...]  |
                      |              +-----------+------------+
                      |                          |
                      v                          v
                 +-------------+      +----------+-----------+
                 | Autoscaler  |<---->| GPU Resource Manager |
                 +-------------+      +----------------------+
                      |
                      v
                 +-------------+      +----------------------+
                 | Registry    |      | Weights / Adapters   |
                 +-------------+      +----------------------+
```

### 4.2 Inside a replica engine

```text
              +---------------- Waiting Queue ----------------+
              |  reqs admitted by tenant + KV estimator       |
              +----------------------+------------------------+
                                     v
+------------------+      +----------+-----------+      +---------------+
| Tokenizer/Safety |----->| Iteration Scheduler  |----->| Sampler/Detok |
+------------------+      | prefill+decode batch |      +-------+-------+
                          +----------+-----------+              |
                                     |                          v
                          +----------+-----------+      +-------+-------+
                          | Model Exec (TP/NCCL) |      | Stream Sender |
                          +----------+-----------+      +---------------+
                                     |
                          +----------+-----------+
                          | Paged KV Block Pool  |
                          +----------------------+
```

### 4.3 Sequence: streaming request

```text
Client → Gateway: POST /v1/chat/completions (stream)
Gateway → Router: pick replica (model, load, cache)
Gateway → Replica: forward
Replica: enqueue → admit → prefill → send first token (TTFT)
loop: decode → token → gateway → client
end / cancel → free KV → usage metrics
```

### 4.4 Sequence: scale out

```text
Autoscaler: ttft_p99 high + queue depth high
  → RM.RequestGang(TP plan)
  → launch replica → load weights → READY
  → Router add endpoint
  → waiting queue drains
```

### 4.5 Disaggregated prefill/decode (100× sketch)

```text
Gateway → Prefill Pool (fat compute) → KV transfer → Decode Pool (latency)
Trade-off: transfer bandwidth/latency vs isolation benefits
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | No serve on incomplete TP gang | RM gang + replica READY gate |
| R2 | KV refcounts safe | Block manager unit tests / asan-style chaos |
| R3 | Cancel eventually frees memory | Reaper on disconnect |
| R4 | Health false → no route | Active HC + outlier detection |
| R5 | Weight revision pinned per replica | Immutable revision id |
| R6 | Tenant cannot exceed quota | Gateway token buckets |

**Failure modes**

| Failure | Behavior |
|---------|----------|
| Replica OOM | Mark unhealthy; restart; tighten admission |
| NCCL TP error | Fail replica; reschedule gang |
| Gateway crash | Stateless OK if streams reset; clients retry |
| Weight download fail | Don’t READY; alert |
| Thundering retries | Idempotency limited for chat; backoff + hedges carefully |
| Prefix cache corruption | Checksums/version; hard disable cache |

**Partial response ethics:** if crash mid-stream, client sees error; do not claim complete.

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | 1–N replicas, simple RR, continuous batching |
| 10× | Load-aware routing; autoscale; paged KV; tenant fairness |
| 100× | Cache-aware routing; model cells; prefill chunking; optional disagg |
| 1,000× | Hierarchical gateways; pooled caches; speculative decoding; SKU pools; metric aggregation |

**Horizontal vs vertical**

- More replicas: scale QPS for models that fit.  
- More TP: fit larger models / sometimes throughput—but collectives cost.  
- Longer context: KV dominates—scale memory or restrict max_len.

**Hot model pattern:** dedicated pool with faster scale-out; cold models scale-to-min.

### 5.3 Maintainability

- Engine version skew: router can pin capabilities (`supports_prefix_cache`).  
- Canary new engine on % traffic.  
- Replay harness: capture request → compare tokens under temp=0.  
- Load generator: Zipf prompt prefixes, long-tail outputs.  
- Reason codes: `KvExhausted`, `TenantThrottled`, `PrefillTooLong`, `ReplicaDraining`.

**Observability**

| Metric | Level |
|--------|-------|
| TTFT / TPOT histograms | model, tenant tier (not raw user) |
| tokens/s in/out | replica |
| KV used / fragmentation | replica |
| Batch size / scheduled tokens | replica |
| Prefix hit rate | model pool |
| 429/503 rates | gateway |

### 5.4 Prefill/decode interference

Giant prefills inflate iteration time → hurt TPOT for everyone.

**Mitigations:**

1. Chunked prefill (limit prefill tokens per iteration).  
2. Separate priority: bound prefill slots.  
3. Disagg pools at 100×.  
4. Cap `max_prompt_tokens` by product tier.

### 5.5 Paged KV fragmentation & preemption

```text
fragmentation_ratio = 1 - (largest_allocatable_seq_tokens / free_tokens_equiv)

When high:
  - prefer admit shorter jobs
  - compact if supported
  - preempt low priority long contexts
```

Preempt victims: farthest from completion among low priority, or longest idle interactive.

### 5.6 Cache-aware routing

```text
key = hash(normalized_prefix_tokens[:L])
prefer replicas with hot key OR highest free KV among cache hits
fallback: least-load replica; optionally warm cache asynchronously
```

Consistency: prefix cache is **performance**, not correctness—miss always safe.

### 5.7 Multi-LoRA (stretch)

```text
Base weights resident; LoRA adapters swapped/batched
Batching constraint: group compatible adapters or fused kernels
Memory: adapter cache with LRU
Routing: pin heavy adapters to dedicated replicas
```

### 5.8 Autoscaler control loop

```text
every T seconds:
  for pool in pools:
    desired = max(min_replicas,
                  f(queue_depth, ttft_p99, kv_util, predicted_load))
    desired = min(desired, max_replicas, rm_free_capacity)
    if desired > current: scale_out with rate limit
    if desired < current: scale_in only if idle for hysteresis window
```

Avoid flapping: cooldown, EMA signals, separate scale-in/out thresholds.

### 5.9 Security & multi-tenancy

- Authn/z per API key → tenant.  
- Prompt/PII logging policies.  
- Cross-tenant KV page sharing **only** for identical public prefix content with care (usually share within tenant).  
- Model access ACLs.  
- Output filtering hooks async/sync per policy.

### 5.10 NVIDIA stack notes (interview flavor)

- Engines: TensorRT-LLM, vLLM, Triton + TensorRT, custom—architecture similar.  
- Use **CUDA graphs** for decode steady-state where batch shape allows.  
- **FP8 / BF16** weights on H100 for throughput.  
- MIG: small models isolation on large GPUs (optional).  
- NCCL for TP; NVLink placement via GPU RM.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. SLOs: TTFT vs TPOT; tokens not just QPS.  
2. Replica engine: continuous batching + paged KV.  
3. Gateway routing + admission/fairness.  
4. TP gangs for large models.  
5. Autoscale + progressive disagg/speculative.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Gateway, continuous batching, paged KV, health routing, quotas |
| 10× | Autoscale, load-aware routing, chunked prefill |
| 100× | Prefix cache routing, model cells, optional disagg |
| 1,000× | Hierarchical edge, speculative decoding, pooled KV tiers |

### 6.3 Top risks

1. KV exhaustion → cascading latency.  
2. Prefill/decode interference.  
3. Ignoring token math in capacity plans.  
4. TP across slow fabric.  
5. Autoscaler cold-start lag.

### 6.4 One-sentence design

> A gateway-routed fleet of NVIDIA inference replicas that continuously batch requests over paged KV memory, scale TP gangs for large models, admit traffic under explicit TTFT/TPOT SLOs, and grow from single-digit to massive QPS by splitting pools, caches, and control-plane cardinality carefully.

---

## 7. Deeper / Related Interview Questions

### 7.1 Latency & SLOs

**Q: TTFT vs TPOT—what moves each?**  
A: TTFT: queue + prefill (+ tokenize). TPOT: decode iteration time under batch/KV length.

**Q: Why does larger batch hurt TPOT?**  
A: Longer kernels / more memory traffic per iteration; trade util vs latency.

**Q: How to protect interactive from batch jobs?**  
A: Separate pools or priority admission with reserved decode slots.

**Q: What does p99 TTFT blow up mean?**  
A: Queueing, huge prefills, KV thrash, cold starts, bad routing.

### 7.2 KV cache & paging

**Q: Why paging?**  
A: Variable seq lengths fragment contiguous allocators; pages + block tables raise concurrency.

**Q: How big is KV?**  
A: Derive from layers, kv heads, dim, dtype, seq—don’t memorize one number; show formula.

**Q: Prefix caching correctness?**  
A: Safe if token prefix identical and model/revision match; privacy constraints apply.

**Q: What if page pool fragments?**  
A: Reject/preempt/compact; track fragmentation metric.

### 7.3 Batching

**Q: Continuous vs static batching?**  
A: Continuous admits new seqs each iteration—much better for interactive.

**Q: Chunked prefill?**  
A: Split long prompt across iterations to bound interference.

**Q: Max batched tokens role?**  
A: Primary knob for latency/throughput balance.

### 7.4 Parallelism in serving

**Q: TP vs replica scale-out?**  
A: TP fits model / sometimes throughput; scale-out increases concurrent capacity for models that already fit.

**Q: PP for inference?**  
A: Useful for huge models; adds pipeline latency—use carefully for interactive.

**Q: Can different requests share TP groups differently?**  
A: Replica plan is fixed; requests don’t each pick TP.

**Q: What if one TP rank dies?**  
A: Whole replica fails; restart gang.

### 7.5 Routing & multi-model

**Q: Least connections enough?**  
A: Prefer outstanding tokens + KV pressure.

**Q: Sticky sessions?**  
A: Helpful for prefix cache; hurt balance if too sticky—use soft affinity.

**Q: Thousands of models?**  
A: Can’t keep all resident; hierarchical loading, scale-to-zero, multi-tier storage.

### 7.6 Autoscaling

**Q: Scale on GPU util alone?**  
A: Insufficient—queue depth and TTFT matter; util can be high while SLO fails or low while KV full.

**Q: Cold start minutes for 70B?**  
A: Keep warm mins; predictive scale; progressive weight fetch / mmap tricks.

**Q: Flapping?**  
A: Hysteresis + cooldowns + EMA.

### 7.7 Speculative decoding

**Q: When does it win?**  
A: High draft accept rate; enough spare compute.

**Q: Failure mode?**  
A: Low accept → wasted compute; disable via flag.

**Q: Does it change API?**  
A: Shouldn’t; internal optimization.

### 7.8 Fairness & multi-tenant

**Q: One tenant monopolizes batch?**  
A: Per-tenant caps on seqs and tokens/iteration.

**Q: Credits?**  
A: Optional metering on tokens; fairness required even without credits.

**Q: Preempt a generation?**  
A: Yes under KV pressure for low priority; client sees error/retryable.

### 7.9 Reliability drills

**Q: Gateway loses stream state?**  
A: Client reconnect semantics; for chat, often re-issue (non-idempotent)—document.

**Q: Half of replicas unhealthy?**  
A: Router drains; autoscale; brownout low priority.

**Q: Weight checksum mismatch?**  
A: Refuse READY; alert supply chain.

### 7.10 Comparison traps

**Q: Is this just Kubernetes + Flask?**  
A: No—iteration scheduler + KV manager dominate design.

**Q: Same as training system?**  
A: Share GPU RM/NCCL skills; serving is latency/batching/KV, not checkpointed Adam steps.

**Q: Why not one sequence per GPU for SLO?**  
A: Cost explosion; continuous batching with budgets is the industry pattern.

### 7.11 Extra interviewer traps (high value)

- Capacity from **tokens/s + KV bytes**, not QPS alone.  
- Show **KV per-token formula**.  
- TTFT vs TPOT knobs.  
- Chunked prefill motivation.  
- TP gang failure semantics.  
- Admission fail-fast vs infinite queue.  
- Prefix cache as performance not correctness.  
- Autoscaler signals beyond GPU %.  
- Telemetry cardinality.  
- Disagg KV transfer cost honesty.  
- MIG when / when not.  
- Cancel → KV free.  
- Hot model pool isolation.  
- Why RR routing fails under KV pressure.  
- Speculative decoding accept rate.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
CREATE TABLE model_revisions (
  model_id TEXT NOT NULL,
  revision TEXT NOT NULL,
  weights_uri TEXT NOT NULL,
  parallel_plan JSONB NOT NULL,
  max_seq_len INT NOT NULL,
  PRIMARY KEY (model_id, revision)
);

CREATE TABLE replicas (
  replica_id UUID PRIMARY KEY,
  model_id TEXT NOT NULL,
  revision TEXT NOT NULL,
  state TEXT NOT NULL, -- loading|ready|draining|dead
  gpu_ids JSONB NOT NULL,
  endpoint TEXT NOT NULL,
  kv_total_blocks INT NOT NULL,
  kv_free_blocks INT NOT NULL,
  outstanding_tokens INT NOT NULL DEFAULT 0
);

CREATE TABLE tenant_quotas (
  tenant_id UUID PRIMARY KEY,
  max_qps DOUBLE PRECISION,
  max_concurrent INT,
  max_tokens_per_min INT,
  priority_band INT
);
```

### 8.2 API checklist

- [ ] `POST /v1/chat/completions` (+ stream)  
- [ ] `POST /v1/completions`  
- [ ] Auth + tenant quotas  
- [ ] Cancel / disconnect propagation  
- [ ] Admin: load/unload model revision  
- [ ] Admin: drain replica  
- [ ] Metrics: TTFT/TPOT/tokens/KV  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| TTFT | Time to first token |
| TPOT | Time per output token |
| Continuous batching | Dynamic join/leave of seqs each iteration |
| Prefill | Process prompt tokens |
| Decode | Generate output tokens step-by-step |
| KV cache | Cached key/value tensors per token |
| PagedAttention | Block-paged KV allocation |
| TP replica | Tensor-parallel gang serving one model copy |
| Prefix cache | Reuse KV pages for shared prompt prefixes |
| Disagg | Split prefill & decode onto different pools |
| Speculative decoding | Draft+verify acceleration |
| Admission control | Accept/queue/reject under resources |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Continuous batching, paged KV, gateway, health |
| 10× | Autoscale, load-aware routing, tenant fairness |
| 100× | Prefix-aware routing, chunked prefill, model cells |
| 1,000× | Hierarchical gateways, disagg/speculative, metric aggregation |

### 8.5 Estimation cheat-sheet

```text
out_tokens/s_needed ≈ QPS × avg_out_tokens
KV_bytes ≈ concurrent_seqs × avg_resident_tokens × bytes_per_token_kv

TTFT ≈ queue + prefill(prompt, interference)
TPOT ≈ iteration_time(batch, kv_len)

replicas ≈ ceil(needed_tokens_per_s / tokens_per_s_per_replica)
           and also ceil(needed_kv / kv_per_replica)

free_gpu_mem ≠ allocatable_kv  (fragmentation, weights, activations)

TP across NVLink ≫ TP across loose IB for TPOT
```

### 8.6 Scheduler pseudocode

```text
def iteration():
  reclaim_finished()
  while waiting and can_admit(waiting[0]):
     admit(waiting.pop())
  batch = build_batch(max_seqs, max_batched_tokens)
  logits = model_exec(batch)  # TP inside
  for seq, tok in sample(logits):
     emit(seq, tok)
     if finished(seq): complete(seq)
```

### 8.7 Interview “say this” summary (60 seconds)

> I’d serve LLMs with a streaming gateway in front of NVIDIA replicas running continuous batching over a paged KV cache. Capacity is tokens/s and KV memory, not QPS. Large models use TP gangs on NVLink; routing is load- and KV-aware with tenant admission for SLOs; we autoscale pools and only then add prefix cache, disagg prefill/decode, and speculative decoding.

### 8.8 Reliability test plan

1. Kill replica mid-stream → client error; router failover for new reqs.  
2. Fill KV → admits reject with 429; no host OOM killer death spiral.  
3. Cancel storm → KV returns to baseline.  
4. Rolling revision → mixed traffic correct model ids.  
5. TP rank kill → replica NOT_READY; RM relaunches gang.  

### 8.9 Observability SLOs

| SLO | Example |
|-----|---------|
| TTFT p99 (interactive) | < 2s warm |
| TPOT p99 / p50 | < 3× |
| 429 under normal capacity | < 1% |
| Replica READY after scale-out | tracked |
| Prefix hit rate | informational |

### 8.10 Related systems map

```text
Client → Gateway → Router → Replica Engine (batch + KV + TP)
                     ↑           ↓
                 Autoscaler ← metrics
                     ↓
                   GPU RM
```

### 8.11 Extra traps

| Trap | Pushback |
|------|----------|
| Size only on QPS | Ignore tokens & KV |
| Infinite queue to “never 429” | TTFT → ∞ |
| Global shared KV day 1 | Consistency/privacy/latency fantasy |
| RR despite KV hot spots | OOM/reject cascades |
| Brochure tokens/s | Hold batch/context constant |
| Training-style DP AllReduce every token | Wrong serving mental model |
| Per-token metrics globally | Cardinality melt |

### 8.12 Brownout policy card

```text
Level 0: normal
Level 1: reject batch/offline tier
Level 2: reduce max_batched_tokens; disable prefix fill-ins
Level 3: preempt low priority generations
Level 4: shed load at gateway (503) with retry-after
```

### 8.13 Speculative decoding notes

```text
accept_rate = accepted_draft_tokens / drafted_tokens
speedup ≈ (1 + accept_rate × (K factors)) under ideal—measure, don’t claim constants
Turn off if accept_rate < threshold or CPU/GPU draft bottleneck
```

---

*End of design doc. Open with §1 TTFT/TPOT + KV scope; whiteboard §3.3–3.8 batching/KV/routing/TP; close with bottlenecks §2.7 and traps §7.11.*
