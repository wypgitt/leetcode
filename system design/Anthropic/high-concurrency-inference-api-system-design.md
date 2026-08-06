# System Design: High-Concurrency Inference API

> **Focus areas:** Dynamic batching · Parallel workers · Queueing · Admission control · Latency-versus-throughput  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct GPU/token arithmetic, split admit/queue/prefill/decode load classes, explicit SLO tradeoffs, Anthropic serving flavor (Claude models, long context, safety cancel hooks)

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

Goal: **bound the product**—the **Inference Gateway / serving plane** that turns admitted Claude requests into tokens under high concurrency: continuous/dynamic batching, worker pools, queues, admission control, and an explicit latency–throughput Pareto frontier. This sits **behind** Chat and the Developer API.

### 1.0 Inference API vs adjacent systems (say this early)

| Dimension | **High-Concurrency Inference (this doc)** | **Developer API** | **GPU Batch Inference** |
|-----------|-------------------------------------------|-------------------|-------------------------|
| Caller | Internal Chat / API edge | External customers | Offline / async jobs |
| Latency SLO | Interactive TTFT + TPS | Same via this plane | Minutes OK |
| Batching | Continuous / dynamic micro-batches | N/A (client) | Large static/dynamic batches |
| Queue | Short deadline queues | 429/529 at edge | Deep queues OK |
| Success metric | Tokens/s **and** p99 TTFT | Correct auth/bill | $/token minimized |

**Scope statement:** Design the high-concurrency inference serving plane—not API keys, not training, not offline batch-only.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the API? | Internal: `Generate(stream)` / cancel / health | gRPC/HTTP2 internal |
| F2 | Models? | Haiku/Sonnet/Opus; multi-version coexist | Per-model pools |
| F3 | Batching? | Yes — continuous batching for decode | Scheduler + KV manager |
| F4 | Prefill vs decode? | Split or unified with chunked prefill | Different bottlenecks |
| F5 | Queueing? | Per-model/priority queues with deadlines | Avoid unbounded wait |
| F6 | Admission control? | Based on KV memory, queue depth, GPU util | Reject early (529) |
| F7 | Priorities? | Pro/Chat vs free vs batch bleed | Weighted fair queues |
| F8 | Cancel? | Client stop / safety abort | Remove from batch ASAP |
| F9 | Long context? | 100K–200K+ class | KV capacity first-class |
| F10 | Prompt cache? | Prefix cache across requests | Sticky routing + cache mgr |
| F11 | Multi-tenant isolation? | Soft fair share; hard caps | Noisy neighbor controls |
| F12 | Observability? | Per-request trace; pool metrics | SLO dashboards |

**MVP functional scope (lock with interviewer):**

1. Internal streaming generate RPC with cancel.
2. **Admission control** on KV memory + queue deadline + concurrency.
3. **Dynamic/continuous batching** for decode; chunked prefill.
4. Parallel GPU workers behind a scheduler per model pool.
5. Priority classes (interactive paid / interactive free / background).
6. Prefix-cache aware routing hooks.
7. Backpressure to edge as 529 / queue-full.
8. Health, drain, and rolling model deploy.

**Out of MVP (explicitly defer):**

- Optimal global multi-region GPU marketplace
- Speculative decoding deep optimization (mention as accelerator)
- Training/inference colocated scheduling
- Customer-visible batch API semantics (sibling)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT (short ctx) | Interactive | p50 < 200–400ms in-pool; p99 < 1–2s excl. overload |
| N2 | Decode TPS/user | Smooth stream | ≥ 20–50 tok/s typical Sonnet-class (hardware-dep.) |
| N3 | Throughput | Maximize GPU efficiency | High utilization without SLO breach |
| N4 | Fairness | No single tenant starves pool | Weighted fair share |
| N5 | Cancel latency | Stop feels instant | Sequence removed ≤ 100–300ms |
| N6 | Availability | Pool-level | 99.9% with regional failover |
| N7 | Isolation | Soft | KV/page caps per tenant class |
| N8 | Deploy safety | No thundering herd | Drain + canary |
| N9 | Memory safety | Never OOM kill node silently | Admit by KV bytes |
| N10 | Cost | $/MTok competitive | Batching + cache |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Short prompt → admit → prefill → decode streamed → release KV.  
2. Many concurrent decodes → continuous batch packs GPU → high util.  
3. Long prompt → chunked prefill → then decode; TTFT larger but bounded.  
4. Prefix cache hit → skipped prefill FLOPs → fast TTFT.  
5. Overload → admission rejects new low-priority; paid interactive continues.  
6. Cancel mid-decode → KV freed; batch continues for others.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| KV memory exhaustion | Admit fail; don’t OOM |
| Mega-context request | Dedicated long-ctx pool or reject if no slot |
| Hot cache key stampede | Sticky + cache replication / fanout limit |
| Worker crash mid-generate | Client retry policy; request incomplete |
| Queue deadline exceeded | Fail 529 before GPU; don’t hold forever |
| Priority inversion | Aging / deficit counters |
| Prefill-heavy storm | Prefill rate limiter; protect decode TPS |
| Safety abort | Same as cancel + reason code |
| Model rollout bad | Canary auto-rollback on TTFT/error |
| Straggler token | Watchdog; repartition carefully |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPU workers (single region) | 200 | 2K | 20K | multi-region 200K-class |
| Peak admits/s | 10K | 100K | 1M | 10M |
| Peak concurrent sequences | 50K | 500K | 5M | 50M |
| Peak decode tok/s | 1M | 10M | 100M | 1B |
| Peak prefill tok/s | 4M | 40M | 400M | 4B |
| Scheduler decisions/s | ~50–200K | ~0.5–2M | tens of M | hierarchical sched |
| Queue depth (interactive) | < 1–2K | sharded | hierarchical | regional meshes |
| Prefix cache entries | millions | tens of M | distributed | multi-tier |

**What each jump forces:**

- **10×:** Separate prefill/decode pools; sharded schedulers; KV paged memory.  
- **100×:** Hierarchical admission; per-tenant fair queues; cache-aware consistent hashing; multi-region pools.  
- **1,000×:** Federation of regional inference fabrics; global load direction at edge; SLO classes as products.

### 1.5 Etc. (Constraints & Assumptions)

- Hardware: NVIDIA-class GPUs (interview: abstract to H100-ish); tensor parallel for large models.
- Requests already auth’d/quota’d by edge.
- Safety classifiers may cancel generations mid-flight.
- Ordinary DS fundamentals (queues, LB, hashing, backpressure) inside GPU constraints.

**Scope statement to repeat back:**

> Design a high-concurrency Claude inference plane with KV-aware admission, deadline queues, continuous batching across parallel GPU workers, priority fairness, cancel, and prompt-cache routing—explicitly managing the latency–throughput tradeoff from baseline through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Admits** | New generate requests | 10K/s | Gateway |
| **Scheduler ticks** | Batch formation | 50–200K/s | Scheduler |
| **Prefill tokens** | Prompt processing | ~4M tok/s | Prefill GPUs |
| **Decode tokens** | Output generation | ~1M tok/s | Decode GPUs |
| **KV alloc/free** | Sequence lifecycle | ~10–20K/s | KV manager |
| **Cache lookup** | Prefix hash | ~10K/s | Cache index |
| **Cancel ops** | Stops / safety | fraction | Control |
| **Metric export** | Per-pool | continuous | Obs |

**Anti-pattern:** one “inference QPS” number without tokens or concurrency.

### 2.2 Latency vs throughput intuition

```text
Batch size B (concurrent sequences in one decode step):
  GPU efficiency ↑ with B (better matmul shapes)
  Per-user TPS ↓ as B grows (time-sliced)
  TTFT may worsen if prefill waits for large batches

Interview curve:
  Small B → great latency, poor $/token
  Large B → great throughput, bad interactive UX
  Control knobs: max_batch_tokens, max_wait_ms, priority lanes
```

### 2.3 GPU arithmetic (order-of-magnitude)

```text
Assume decode ~5,000 tok/s/GPU effective at healthy batching (model-dep.)
Need 1M tok/s → 1M/5K = 200 decode GPUs

Prefill ~20,000 tok/s/GPU effective
Need 4M tok/s → 4M/20K = 200 prefill-equivalent GPUs

Long-context note:
  KV bytes ≈ layers × kv_heads × dim × dtype × seq_len × batch
  If one 200K-ctx sequence consumes ~N GB, concurrent long seqs per GPU ≪ short seqs
  Capacity is often MEMORY-bound before FLOP-bound
```

### 2.4 Concurrent sequences vs QPS

```text
Little’s Law: concurrency ≈ arrival_rate × residency_time
If 10K admits/s and avg generation lasts 2s of decode+queue
  concurrency ≈ 20K sequences (order)
Matches “peak concurrent sequences” planning better than QPS alone
```

### 2.5 Queueing delay budget

```text
Interactive p99 TTFT budget 1.5s
Breakdown example:
  edge+safety 50ms
  admit+route 20ms
  queue wait ≤ 300ms (hard deadline low-pri shorter/longer by class)
  prefill 200–800ms (length-dependent)
  first token decode 20–50ms

If queue wait > deadline → reject; do not inflate prefill batch wait unboundedly
```

### 2.6 Cost implications

```text
GPU hour ≈ $X (use interviewer number, e.g. $2–4/GPU-hr illustrative)
200 GPUs × $3 × 24 × 30 ≈ $4.3M/month region
+10% utilization from better batching → ~$430K/month — worth scheduler investment
Bad admission (OOM thrash) can destroy effective throughput >20%
```

### 2.7 Scheduler decision rate

```text
If decode step ~10–20ms and 200 workers each step
  decisions ≈ 200 × 50–100/s ≈ 10–20K/s centralized — OK baseline
At 20K GPUs, centralized scheduler dies → shard by model+cell
```

---

## 3. High-Level Design

### 3.1 Domain model

```text
ModelPool (model_version, region, hardware SKU)
  ├── Workers[] (GPU node / TP group)
  ├── Scheduler (batch former)
  ├── KV Memory Manager (pages/blocks)
  ├── Prefix Cache Manager
  └── Queues by PriorityClass

Request / Sequence
  ├── request_id, priority, deadline
  ├── input tokens / cache refs
  ├── state: queued|prefilling|decoding|done|cancelled|rejected
  ├── kv_lease
  └── stream sink
```

### 3.2 Internal API

```protobuf
rpc Generate(GenerateRequest) returns (stream GenerateEvent);
rpc Cancel(CancelRequest) returns (CancelResponse);
rpc PoolStats(PoolStatsRequest) returns (PoolStats);
```

`GenerateRequest`: model_version, tokens/refs, max_tokens, priority, deadline, cache_key, params (temp…).

### 3.3 Dynamic / continuous batching

**Idea:** at each decode step, run a batch of sequences that still need a next token; add/remove sequences between steps (Orca-style continuous batching).

| Approach | Latency | Throughput | Complexity | Deal-breaker |
|----------|---------|------------|------------|--------------|
| Static batch wait-for-N | Poor TTFT | Good | Low | Interactive chat |
| No batching (batch=1) | Best latency | Terrible $/tok | Low | Cost at scale |
| **Continuous batching (chosen)** | Good | Good | Med-high | Ignoring KV fragmentation |
| Prefill-only batching | Medium | Medium | Med | Decode inefficiency remains |

**Knobs:**

- `max_num_seqs`  
- `max_num_batched_tokens`  
- `max_wait_ms` for prefill coalescing  
- separate limits for prefill vs decode  

### 3.4 Prefill vs decode pools

| Strategy | Pros | Cons |
|----------|------|------|
| Unified workers | Simple | Prefill storms tank TPS |
| **Split pools (chosen at 10×)** | Isolation | Cross-handoff KV |
| Chunked prefill on decode workers | Smoother | Scheduling complexity |

**Handoff:** prefill produces KV → decode worker continues (same worker preferred to avoid KV transfer). Often: same worker does chunked prefill then decode; split pools for *disaggregated* serving at large scale.

### 3.5 Queueing design

```text
Edge → Admission → Priority queues → Workers

Priority classes:
  P0 interactive paid / critical
  P1 interactive free
  P2 background / batch bleed
```

| Queue discipline | Pros | Cons |
|------------------|------|------|
| FIFO | Simple | Unfair to short jobs |
| SJF | Good latency | Starvation |
| **Weighted fair + aging (chosen)** | Balanced | Tunable complexity |
| EDF by deadline | Good SLO | Needs good deadlines |

**Deadline:** if `now > deadline` while queued → reject `OVERLOADED`. Never start GPU work that already missed.

### 3.6 Admission control

Admit iff:

1. Queue depth / predicted wait < class threshold  
2. KV memory headroom ≥ estimated `seq_len_max × bytes_per_token`  
3. Tenant concurrency < cap  
4. Pool not draining  

| Signal | Action |
|--------|--------|
| KV high | Reject long-ctx first; then free tier |
| Prefill util high | Slow admit / reject | 
| Decode util high | Allow short max_tokens preferentially |
| Cache hit likely | Prefer admit (cheap) |

**Deal-breaker:** admitting until CUDA OOM — causes multi-tenant brownout.

### 3.7 Parallel workers & load balancing

```text
Router → consistent hash(cache_key) among warm workers
       → else least-loaded / power-of-two-choices on KV free memory
```

| LB | When |
|----|------|
| Least tokens in-flight | Default |
| Consistent hash cache | Prefix hit path |
| Random PO2 | High scale simplicity |
| Sticky session | Streaming cancel locality |

**Tensor parallel groups** appear as one “worker” logical unit.

### 3.8 Latency–throughput control plane

Expose pool mode:

| Mode | max_wait_ms | max_batch | Use |
|------|-------------|-----------|-----|
| Low-latency | 0–5ms | smaller | Chat peak UX |
| Balanced | 10–20ms | medium | Default |
| Throughput | 50ms+ | large | Off-peak efficiency / batch bleed |

Auto-tune toward SLO: if TTFT p99 breaches → shrink wait/batch; if util < target and SLO ok → grow.

### 3.9 Cancel & safety abort

```text
Cancel(request_id) → mark sequence → on next step boundary drop from batch → free KV pages
Safety classifier → same path with reason=safety
```

Must not wait for full `max_tokens` to free memory.

### 3.10 Prefix cache

```text
cache_key = hash(model_version, prefix_tokens)
Lookup → worker with KV prefix resident (if any)
Miss → prefill → optionally retain prefix under LRU/TTL
```

**Tradeoff:** cache memory vs free KV for live sequences. Admission includes cache pressure policy.

### 3.11 Component trade-offs

| Component | Options | Choice | Deal-breaker |
|-----------|---------|--------|--------------|
| Scheduler | Central vs sharded | Central per pool shard | One global scheduler at 100× |
| KV manager | Contiguous vs paged | **Paged blocks** | Fragmentation OOM |
| Queue store | In-memory vs Redis | **In-memory per shard** + edge backoff | Redis on every token |
| Stream | Push gRPC | **gRPC streaming** | Buffering all tokens in scheduler |
| Autoscaling | GPU slow scale | Admit+queue first; scale secondary | Believing GPU scales like CPU |

**Alternatives considered:**

- Kubernetes default LB alone → ignores KV/cache.  
- Pure request FIFO without deadlines → meltdown UX.  
- Always disaggregate prefill/decode at MVP → premature complexity.

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+------------------+     +------------------------+
| Chat / Dev API   |---->| Inference Gateway      |
| Edge             |     | auth'd Generate/Cancel |
+------------------+     +-----------+------------+
                                     |
                         +-----------v------------+
                         | Admission Controller   |
                         | KV headroom, deadlines |
                         +-----------+------------+
                                     |
                         +-----------v------------+
                         | Priority Queues        |
                         | P0 / P1 / P2           |
                         +-----------+------------+
                                     |
                         +-----------v------------+
                         | Scheduler Shards       |
                         | continuous batching    |
                         +--+----------+----------+
                            |          |
              +-------------v--+    +--v--------------+
              | Prefill path   |    | Decode path     |
              | (chunked)      |    | continuous batch|
              +--------+-------+    +--------+--------+
                       |                     |
                       +----------+----------+
                                  v
                       +----------+----------+
                       | GPU Workers (TP)    |
                       | KV Block Manager    |
                       | Prefix Cache        |
                       +---------------------+
```

### 4.2 Request lifecycle sequence

```text
Edge                Admit              Queue/Sched           Worker GPU
  |                   |                    |                    |
  | Generate          |                    |                    |
  |------------------>|                    |                    |
  |                   | check KV/queue     |                    |
  |                   |-------------------->|                    |
  |                   |                    | form batch         |
  |                   |                    |------------------->|
  |                   |                    | prefill chunks     |
  | first token       |                    |<-------------------|
  |<-------------------------------------------------------------|
  | deltas...         |                    | decode steps       |
  |<-------------------------------------------------------------|
  |                   |                    | free KV on end     |
  | done              |                    |                    |
  |<-------------------------------------------------------------|
```

### 4.3 Overload data flow

```text
Load ↑ → queue wait ↑ → Admit rejects P2 then P1
      → edge returns 529 / Retry-After
      → Auto mode in Chat routes to Haiku pool
      → GPU util stays in safe band; TTFT for P0 preserved
```

### 4.4 Cancel path

```text
Client Stop → Edge Cancel → Scheduler marks seq
  → next decode barrier drops seq
  → KV blocks → free list
  → stream trailers cancelled
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Data loss / incomplete generations

Inference plane is **not** the system of record for chat text. Orchestrators checkpoint tokens. Worker death → `incomplete`; upper layer retries or shows partial.

**Invariant:** cancel and complete both free KV (no leaks).

#### 5.1.2 Retries

- Safe before first token under idempotent `request_id` if edge agrees.  
- After tokens emitted: no silent second generation without upper-layer new turn.  
- Worker retry within pool only for pure infra failures pre-stream.

#### 5.1.3 Rate limiting / admission as reliability

Admission **is** the reliability mechanism for multi-tenant GPUs. Prefer early 529 to cascading latency.

#### 5.1.4 Idempotency

`request_id` uniquely identifies a generation lease. Duplicate Generate with same id attaches to existing stream or returns conflict.

#### 5.1.5 Backpressure

```text
Worker overloaded → scheduler slows dequeue
Queue at max → admit rejects
Edge translates to customer/product degradation
```

Never infinite buffer in gateway memory.

#### 5.1.6 Rolling deploys

Drain: stop admits to worker → finish in-flight → unload model → deploy → warm cache → rejoin. Canary on TTFT/error/$tok.

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Scale | Scheduler | Memory | Routing | Pools |
|-------|-----------|--------|---------|-------|
| Baseline | 1 scheduler/model | Paged KV | Least-load | Unified workers |
| **10×** | Shard by hash(request) | Aggressive paging | Cache hash | Split prefill/decode |
| **100×** | Hierarchical (meta + leaf) | Multi-tier cache | Regional meshes | SLO classes |
| **1,000×** | Federated regional fabrics | Cross-node KV rare/expensive | Global director at edge | Hardware SKU heterogeneity |

#### 5.2.2 Traffic ups/downs

- Diurnal: shrink throughput mode at peak UX hours; expand batching overnight.  
- Viral spikes: shed P2/P1; scale GPUs (slow); borrow from batch fleet if preemption APIs exist.

#### 5.2.3 Parallelization dimensions

1. Data parallel: many workers same model.  
2. Tensor parallel: within worker for large models.  
3. Pipeline parallel: optional for huge models (latency cost).  
4. Request parallel: continuous batch sequences.  
5. Chunked prefill parallel with decode (careful QoS).

#### 5.2.4 Storage (weights & cache)

- Model weights on local NVMe; lazy load.  
- Prefix cache in GPU mem + optional CPU/NVMe secondary.  
- Not using Postgres for token paths.

#### 5.2.5 What breaks at each jump

| Jump | Breaks | Fix |
|------|--------|-----|
| 10× | Central scheduler CPU; KV frag | Shard; paged KV |
| 100× | Prefill storms; hot cache workers | Disaggregate; replicate cache; fair queues |
| 1,000× | Cross-region sticky dreams | Regionalize; edge directs new sessions |

### 5.3 Maintainability

#### 5.3.1 Versioning

- `model_version` immutable per pool.  
- Multiple versions run in parallel during rollout.  
- Scheduler protocol versioned for workers.

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| TTFT p50/p99 by class | Latency SLO |
| Tokens/s/GPU | Efficiency |
| Batch size hist | Tuning |
| KV used % | Admission |
| Queue wait | Overload |
| Cancel latency | UX/safety |
| Cache hit rate | Cost |
| OOM / admit rejects | Health |

Distributed traces: edge request_id → sequence_id → worker_id.

#### 5.3.3 SLOs

| SLO | Target |
|-----|--------|
| P0 TTFT p99 (short) | < 1–2s when not region-down |
| P0 queue deadline miss | < 1% |
| KV leak | ~0 (gauge sequences vs blocks) |
| Unexpected 5xx | < 0.1% |
| Drain time | bounded |

#### 5.3.4 Config & ops

- Hot knobs: max_batch_tokens, wait_ms, class weights.  
- Feature flags for disaggregated prefill.  
- Runbooks: hot worker, KV fragmentation, thundering cache, bad canary.

#### 5.3.5 Safety ops

- Abort channel from safety fleet with high priority.  
- Audit counts of safety cancels vs user cancels.

---

## 6. Wrap-Up

### 6.1 Summary talking points

1. **KV-aware admission** beats heroic retries after OOM.  
2. **Continuous batching** is the core efficiency lever for decode.  
3. **Deadline queues + priorities** protect interactive Claude UX.  
4. **Latency–throughput knobs** are explicit product/ops modes.  
5. **Cache-aware routing** cuts prefill cost for Anthropic long prompts.  
6. Scale by sharding schedulers and regionalizing pools—not one mega-brain.  
7. Cancel/safety abort is a first-class memory-freeing path.

### 6.2 Risk register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Prefill storm | TPS collapse | Chunking, split pools, admit |
| KV fragmentation | False full | Paged allocator |
| Hot cache worker | Tail latency | Replicate / rebalance |
| Unbounded queue | UX death | Deadlines |
| Priority inversion | Paid hurt | Aging, weights |
| Scheduler bug | Fleet outage | Canary, rapid rollback |
| Disagg KV transfer cost | Regression | Same-worker preference |

### 6.3 Phased rollout

| Phase | Ship |
|-------|------|
| MVP | Continuous batching, admit by KV+queue, priorities, cancel |
| 1.5 | Prefix cache sticky routing; chunked prefill; auto SLO tuner |
| 2 | Disaggregated prefill/decode; multi-region; hierarchical sched |
| 3 | Federated fabric; preemptible batch borrow; speculative decoding |

---

## 7. Deeper / Related Interview Questions

### Q1. Why continuous batching over waiting for a full batch?

**A:** Interactive TTFT cannot wait to fill large batches. Continuous batching keeps GPU busy with whatever sequences are active, adding new ones between steps.

### Q2. What memory structure do you use for KV?

**A:** Paged block allocator (vLLM-style): sequences hold block tables; frees coalesce; reduces fragmentation vs contiguous reservations.

### Q3. How does Little’s Law guide GPU count?

**A:** Concurrent sequences ≈ admits/s × residency. Memory per sequence × concurrency ⇒ minimum GPUs. Often tighter than FLOP-derived counts for long context.

### Q4. FIFO vs weighted fair queuing?

**A:** FIFO lets huge tenants or long prefills block others. WFQ/deficit round-robin allocates service shares by priority class and tenant.

### Q5. Where is consistent hashing used?

**A:** `cache_key → worker` for prefix locality. Also `model_version+shard → scheduler`. Rebalance with virtual nodes when workers drain.

### Q6. What’s the deal-breaker for max_wait_ms=100 on chat?

**A:** Adds up to 100ms artificial TTFT for coalescing—often unacceptable for Haiku-class “snappy” UX. Use tiny waits or wait only under low load.

### Q7. How do you prevent prefill from starving decode?

**A:** Reserve decode capacity; limit concurrent prefill tokens/GPU; chunked prefill interleaved; or physical pool split.

### Q8. Algorithm for admission under mixed short/long contexts?

**A:** Estimate KV bytes; maintain free-block watermark; reject or redirect long-ctx to dedicated pool when watermark low; always keep reserve for P0 short chats.

### Q9. How do tensor-parallel workers change LB?

**A:** LB unit is the TP group, not each GPU. Health of any member fails the group.

### Q10. What happens on worker crash mid-stream?

**A:** Stream errors; upper layer marks incomplete. Don’t auto-retry decode mid-tokens without product policy. Free cluster-level leases via heartbeat timeout.

### Q11. How is this different from a generic web request queue?

**A:** Cost dominated by GPU memory residency and batched matmuls; holding a request is expensive; reject early. Tokens/s and KV%, not only QPS.

### Q12. Speculative decoding — where does it fit?

**A:** Accelerator on decode TPS; complicates batching (draft+verify). Mention as Phase 3; doesn’t replace admission/batching fundamentals.

### Q13. How do you measure GPU efficiency in interview terms?

**A:** Model FLOP utilization, achieved tok/s vs theoretical, idle time from waiting, KV fragmentation waste, cache hit rate.

### Q14. Why not Redis-backed queues for sequences?

**A:** Extra RTT and serialization on the hottest path. Keep queues in scheduler memory; use Redis/edge for **admission counters** if multi-gateway.

### Q15. Fanout of a single popular system prompt?

**A:** Prefix cache helps; but one worker hotspot needs replication of prefix blocks or multi-worker warm set; rate-limit identical mega-prefixes from one tenant.

### Q16. How do you set deadlines?

**A:** Class-based: P0 300–500ms queue; P1 1s; P2 seconds–minutes. Deadline = enqueue_time + class_budget; optionally shorten when pool hot.

### Q17. What’s a good data structure for ready sequences?

**A:** Per-class deques + heap by deadline for EDF checks; bitmap/set of sequences ready for next decode step inside worker.

### Q18. How does cancel interact with CUDA graphs?

**A:** Graphs prefer static shapes; continuous batching already reshapes often. Cancel between steps; accept some graph replay cost for flexibility—or pad to buckets.

### Q19. Multi-region active-active inference?

**A:** Hard for sticky prefix cache. Typically regional pools; edge pins session/request to region; failover loses cache warmth.

### Q20. How do you capacity-plan Opus vs Haiku?

**A:** Separate pools; different KV footprints and tok/s; don’t assume one GPU count formula. Route Auto using pool pressure signals.

### Q21. What observability cardinality traps exist?

**A:** Per-prompt or per-user metrics explode. Stick to pool/class/tenant-bucket aggregates; sample traces.

### Q22. How do you test the latency–throughput controller?

**A:** Replay production traces; sweep max_batch/wait; plot Pareto of p99 TTFT vs tok/s/$; pick default operating point; chaos prefill storms.

### Q23. DB usage in inference plane?

**A:** Almost none on path. Maybe control DB for pool config. Request logs async.

### Q24. How do safety classifiers hook in without killing TPS?

**A:** Upper layer lag-buffers tokens; abort RPC into inference is rare but must be fast. Don’t run heavy classifiers on GPU workers themselves.

### Q25. What is head-of-line blocking here?

**A:** Giant prefill at front of FIFO blocks short queries. Mitigate with chunking, size-based lanes, or separate prefill workers.

### Q26. Horizontal scaling limits?

**A:** Scheduler coordination, cache locality, model weight distribution bandwidth, and networking for disagg KV. Pure “add GPUs” works until those bind.

### Q27. How do you implement fair share across tenants?

**A:** Deficit counters per tenant on decode steps or tokens; unused credit decays; cap reservation so idle tenants don’t hold KV forever.

### Q28. Why paged KV is a systems, not ML, win?

**A:** It’s memory allocation + fragmentation + sharing prefixes—classic OS paging ideas applied to attention caches.

### Q29. Cost narrative for executives?

**A:** Every +5% batching efficiency or +10% cache hit is millions/year; admission control prevents worse losses from thrash.

### Q30. Staff closing line?

**A:** “This is distributed systems: admission, scheduling, memory management, and fairness—where the ‘CPU’ is a GPU and the ‘RSS’ is KV cache.”

---

*End of High-Concurrency Inference API system design.*
