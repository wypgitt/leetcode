# System Design: GPU Batch Inference System

> **Focus areas:** Combine requests efficiently · Batch ≈ single-request GPU cost · Throughput economics · Queueing · Reliability · Cost  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct batching arithmetic, split submit/schedule/execute/result load classes, explicit when batching helps vs hurts, Anthropic flavor (Claude models, safety, prompt caching, Messages/Batch API)

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

Goal: **bound the product**—a **GPU batch-inference system** that **combines many requests** into efficient GPU executions when a well-formed batch costs nearly the same as one request (matmul-bound decode/prefill shapes), delivering high throughput and low $/token for async/offline workloads—distinct from interactive continuous-batching chat serving.

### 1.0 Batch inference vs interactive inference (say this early)

| Dimension | **GPU Batch Inference (this doc)** | **High-Concurrency Interactive** |
|-----------|------------------------------------|----------------------------------|
| Latency SLO | Minutes to hours OK | Sub-second TTFT |
| Batching style | Form large batches; wait OK | Continuous micro-batches; tiny waits |
| API shape | Job submit / poll / webhook / S3 results | Streaming generate |
| Cost goal | Minimize $/MTok | Meet latency SLO then efficiency |
| Queue depth | Deep OK | Deadline-short |
| Preemption | Batch preemptible by interactive | Interactive protected |

**Anthropic product hook:** Message Batches-style API for Claude—developers submit arrays of requests, retrieve results later, pay lower effective rates via efficiency + product pricing.

**Scope statement:** Design GPU batch inference that packs work for efficiency—not the interactive SSE path.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits? | Developers via Batch API; internal eval/pipelines | Auth via API keys; job ACLs |
| F2 | Job model? | Create batch of N requests; get results later | Durable job + per-item state |
| F3 | How combine? | Pack compatible requests into GPU batches | Compatibility dimensions |
| F4 | Why cheaper? | Better GPU util; product discount | Throughput scheduling |
| F5 | Models? | Haiku/Sonnet/Opus versions | Per-model batch fleets |
| F6 | Input/output sizes? | Large JSONL / object storage | Not all payloads in PG |
| F7 | Completion notify? | Poll + optional webhook | At-least-once webhook |
| F8 | Partial results? | Per-item success/fail | Item-level idempotency |
| F9 | Priority? | Standard vs rush; interactive preemption | Separate queues / capacity |
| F10 | Safety? | Same policy as online (possibly async) | Classify per item |
| F11 | Caching? | Shared prefixes across batch items | Pack by prefix |
| F12 | Cancel? | Cancel remaining items | Cooperative cancel |

**MVP functional scope (lock with interviewer):**

1. Submit batch job (inline small or object-store JSONL).  
2. Durable persistence of job + items; idempotent submit.  
3. **Packer/scheduler** groups compatible items into GPU batches.  
4. Workers execute batches; write per-item results.  
5. Poll job status; download results; optional webhook.  
6. Safety per item; usage/billing per item.  
7. Capacity isolation from interactive pools (or preemptible borrow).  
8. Retries for transient GPU failures; dead-letter poison items.

**Out of MVP (explicitly defer):**

- Exact cost parity guarantees vs theoretical optimum packing  
- Cross-region batch migration mid-job  
- Customer CUDA kernels  
- Training mixed with batch inference  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Job latency | Async | p50 hours-scale OK; SLO by tier (e.g. 24h) |
| N2 | Item throughput | Maximize tok/s/GPU | High util ≥ 70–85% target |
| N3 | Durability | No lost accepted items | Durable before ACK |
| N4 | Exactly-once effects? | At-least-once exec; idempotent results | Exactly-once *billing* via item_id |
| N5 | Availability | Job control plane high | Workers can drain |
| N6 | Cost | Primary success metric | $/MTok vs interactive |
| N7 | Isolation | Don’t wreck chat | Separate pools / preemption |
| N8 | Scale of items | Millions/day → billions | Object storage + queues |
| N9 | Safety completeness | Every item checked | No “batch skip safety” |
| N10 | Observability | Job + fleet | Progress %, GPU efficiency |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Submit 10K Messages requests as a batch → packed by model → GPUs run fat batches → results JSONL ready → webhook.  
2. Many items share system prompt → prefix-aware packing → huge cache/prefill savings.  
3. Mixed success: 9990 ok, 10 content-policy fails → job completed with per-item errors.  
4. Interactive spike → preempt batch workers → batch resumes later.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate submit | Idempotency-Key → same batch_id |
| Poison item (OOM length) | Fail item; continue job |
| Worker death mid-batch | Re-queue incomplete items (idempotent) |
| Webhook endpoint down | Retry with backoff; poll still works |
| Incompatible packing (diff models) | Never co-batch; separate lanes |
| Huge output explosion | Per-item max_tokens; disk quotas |
| Cancel job | Stop scheduling remaining; keep finished results |
| Safety brownout | Pause job or fail closed high-sev items |
| Billing dispute | item_id usage events immutable |
| Hot org fills fleet | Fair share across orgs |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Batches submitted/day | 5K | 50K | 500K | 5M |
| Items/day | 50M | 500M | 5B | 50B |
| Peak items enqueued/s | 5K | 50K | 500K | 5M |
| GPU workers (batch fleet) | 100 | 1K | 10K | 100K-class |
| Peak batched tok/s | 2M | 20M | 200M | 2B |
| Result bytes/day | 10 TB | 100 TB | 1 PB | retention-capped |
| Packer decisions/s | 1K | 10K | 100K | hierarchical |
| Webhooks/day | 5K | 50K | 500K | dedicated delivery |

**What each jump forces:**

- **10×:** Object-store IO path; packer service; per-org fair queues; result partitioning.  
- **100×:** Hierarchical jobs (shards); multi-region batch fleets; prefix clustering at scale; preemptible capacity markets.  
- **1,000×:** Cell-based batch fabrics; cold result tiers; global fair share; specialized long-context batch pools.

### 1.5 Etc. (Constraints & Assumptions)

- “Batch costs nearly the same as one request” refers to **GPU kernel efficiency** for compatible shapes—not that N requests are free. Wall-clock for the batch grows; **amortized FLOPs/$** improve.  
- Interactive Claude traffic may preempt.  
- Safety and billing still apply per item.  
- Ordinary job-scheduling fundamentals inside GPU constraints.

**Scope statement to repeat back:**

> Design an Anthropic-style GPU batch inference system: durable multi-item jobs, compatibility-aware packing so GPUs run efficient large batches, async results via storage/webhooks, per-item safety and billing, fair multi-tenant scheduling, and isolation/preemption relative to interactive serving—scaled through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Job submits** | Control plane writes | ~tens–hundreds/s | API/PG |
| **Item ingest** | Expand to items | ~5K/s | Ingest workers |
| **Packer** | Form GPU batches | ~1K batches/s | Packer |
| **GPU execute** | Tokens processed | ~2M tok/s | Batch GPUs |
| **Result writes** | Object store PUTs | ~5K–50K/s | Results |
| **Status polls** | Customer polls | cacheable | Edge cache |
| **Webhooks** | Delivery attempts | ~burst | Dispatcher |
| **Usage events** | Per item | ~item complete rate | Billing bus |
| **Safety** | Per item | ~item rate | Safety fleet |

**Anti-pattern:** treating “batch QPS” as the GPU throughput metric.

### 2.2 Why batching saves money (arithmetic)

```text
Interactive decode with small effective batch B_i → util U_i (e.g. 35%)
Batch decode with large B_b → util U_b (e.g. 80%)

Effective tok/s/GPU ≈ peak × util
Cost per MTok ≈ GPU_$/hr / (tok_per_hr)

If U_b / U_i ≈ 80/35 ≈ 2.3×
→ ~2.3× more tokens per GPU-hour → ~57% lower raw GPU $/MTok
(before packing inefficiencies, padding waste, storage, safety)

Padding waste matters:
  If batch pads to max seq len in batch, short requests pay FLOPs for pads
  Pack by similar length to keep waste <10–20%
```

### 2.3 “Batch ≈ one request” — precise claim

```text
For GEMM-heavy decode steps, launching a kernel for batch B
often has similar overhead to batch 1; FLOPs scale ~linear in B,
but overhead amortization + better tensor shapes → near-linear throughput
until memory bandwidth / KV capacity binds.

NOT true when:
  - sequences vastly different lengths (padding blowup)
  - different models/versions
  - different precision / LoRA adapters (if any)
  - KV memory forces B tiny
```

### 2.4 Job sizing math

```text
50M items/day / 86400 ≈ 578 items/s average
Peak 5K items/s (bursty ingest)

If avg 2K tokens in + 500 out = 2.5K tok/item
Tokens/day ≈ 50M × 2.5K = 125B tokens/day
≈ 1.45M tok/s average

At 20K tok/s/GPU effective batch util → GPUs ≈ 1.45M/20K ≈ 73 GPUs average
Peak 2M tok/s → ~100 GPUs — matches baseline fleet order
At 100× items: thousands of GPUs — need multi-region
```

### 2.5 Storage math

```text
Input ~2 KB/item average × 50M = 100 TB/day raw in (or less if refs)
Output ~1 KB/item × 50M = 50 TB/day
Retention 30 days → multi-PB — lifecycle policies mandatory at 100×

Control plane: store pointers, not full payloads, for large batches
```

### 2.6 Packing efficiency

```text
Ideal speedup limited by:
  compatibility fragmentation
  length padding waste W
  safety serial bottlenecks
  result IO

Effective efficiency ≈ U_gpu × (1-W) × (1-overhead)
Interview: show you optimize packing keys, not only “make batch bigger”
```

### 2.7 Cost implications

```text
If interactive $/MTok_gpu = $1.00 equivalent
Batch efficiency 2× → $0.50
Pass some savings to customers as Batch API discount; keep margin for storage/ops

Eval fleets (internal) may consume vast batch capacity — chargeback via same metering
```

---

## 3. High-Level Design

### 3.1 Domain model

```text
BatchJob
  ├── batch_id, org_id, project_id
  ├── model_version (or per-item model if allowed)
  ├── status: validating|in_progress|canceling|ended
  ├── item_counts {pending,succeeded,errored,canceled}
  ├── input_uri / inline_ref
  ├── output_uri
  ├── idempotency_key
  └── created_at, completed_at, expires_at

BatchItem
  ├── item_id (custom_id)
  ├── request payload ref
  ├── status + error
  ├── result ref
  ├── usage
  └── attempt_count

GPUBatch (internal)
  ├── gpu_batch_id
  ├── model_version
  ├── packing_key (length_bucket, prefix_hash, params_hash)
  ├── item_ids[]
  └── worker_id, state
```

### 3.2 API shape (customer)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/messages/batches` | Create batch |
| GET | `/v1/messages/batches/{id}` | Status |
| GET | `/v1/messages/batches/{id}/results` | Results stream/JSONL |
| POST | `/v1/messages/batches/{id}/cancel` | Cancel remaining |

```http
POST /v1/messages/batches
Idempotency-Key: ...
{
  "requests": [
    {"custom_id": "req-1", "params": {"model":"claude-...", "messages":[...], "max_tokens":256}},
    {"custom_id": "req-2", "params": {...}}
  ]
}
```

Large jobs: upload JSONL to object storage; pass `input_file_id`.

### 3.3 Compatibility & packing keys

Co-batch only if equal on:

| Dimension | Why |
|-----------|-----|
| `model_version` | Weights differ |
| Sampling params bucket | Temp/top_p graphs |
| Tensor parallel shape | Worker type |
| Prefix hash (optional soft) | Cache synergy |
| Length bucket | Reduce padding |

| Packing strategy | Pros | Cons | Deal-breaker |
|------------------|------|------|--------------|
| FIFO ignore compat | Simple | Terrible util | Mixed models in one kernel |
| Exact match all fields | Safe | Over-fragmented | Tiny batches forever |
| **Bucketing + compat key (chosen)** | Balance | Tuning | Unbounded wait for perfect pack |

**Wait policy:** `max_wait_for_pack` (e.g. 100ms–few seconds for online-batch hybrid; seconds–minutes for offline) vs `min_batch_size` targets.

### 3.4 Why “combine requests” works on GPUs

```text
Single request decode step: GPU underfilled
B requests, same model, padded to L_max:
  Attention/MLP operate on [B, L, D] — high utilization
Cost(batch B) ≈ Cost(1) + marginal_per_item  (overhead amortized)
⇒ Prefer B as large as KV memory allows within length bucket
```

**Tradeoff table:**

| Larger B | Effect |
|----------|--------|
| + | Higher util, lower $/tok |
| − | More padding if lengths diverge; longer wall time to form batch; bigger blast radius on failure |

### 3.5 Scheduler / queues

```text
Items ready → per (org fair queue) → global packers by packing_key
           → GPUBatch tasks → worker queues
```

| Discipline | Use |
|------------|-----|
| Fair share per org | Multi-tenant |
| Size-aware packing | Length buckets |
| Deadline/aging | 24h SLO jobs escalate |
| Preemptible lane | Yield to interactive |

### 3.6 Execution workers

```text
Worker pulls GPUBatch
  → allocate KV for B seqs
  → prefill (possibly cached by prefix)
  → decode to max_tokens / EOS per item (continuous batching inside the batch job is OK)
  → stream results to result writer
  → ack items
```

**Note:** Internally you may still use continuous batching engines; the *product* is async batch. Difference is admission waits for fat packs and deeper queues.

### 3.7 Results & notifications

| Approach | Pros | Cons |
|----------|------|------|
| Poll only | Simple | Customer load |
| **Poll + webhook (chosen)** | UX | Delivery retries |
| Push to customer S3 | Enterprise | IAM complexity |

Results JSONL lines keyed by `custom_id`. Immutable after item success.

### 3.8 Safety & abuse

- Run input classifiers before GPU or on GPU-adjacent safety workers.  
- Output classifiers before persisting results (async latency OK → can be stricter).  
- Org rate limits on items/day; payload size caps.  
- Don’t let batch become free jailbreak farm—same policy stack.

### 3.9 Billing

```text
Per item usage event on terminal state
Batch discount pricing version
Failed policy items: bill 0 or input-only per policy — document
Retries: bill once per successful generation; failed infra retries not double-billed
```

### 3.10 Isolation from interactive

| Strategy | Pros | Cons |
|----------|------|------|
| Hard separate GPU pools | Safety for chat | Lower batch util off-peak |
| **Shared with preemption (chosen hybrid)** | Cost | Preempt complexity |
| Off-peak only batch | Simple | Latency SLO weak |

**Hybrid:** dedicated minimum batch pool + burst into preemptible interactive overflow at night.

### 3.11 Component trade-offs

| Component | Options | Choice | Deal-breaker |
|-----------|---------|--------|--------------|
| Item store | PG vs Dynamo vs queue+obj | **Metadata DB + S3 payloads** | 50M full prompts in PG |
| Work queue | Kafka vs SQS vs Redis | **Kafka/SQS-class** | In-memory only at 100× |
| Packer | Online vs periodic | **Streaming packer + flush timer** | Infinite wait for perfect B |
| Results | Single file vs partitioned | **Partitioned by job shard** | One giant file rewrite |
| Dedup | item hash | **custom_id + batch_id** | Silent double charge |

**Alternatives considered:**

- Reuse interactive API in a loop → poor packing, high overhead, costlier.  
- Spark-style CPU map before GPU → extra hop; OK for featurization, not core decode.  
- One GPU per item → destroys the thesis of this design.

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +------------------+     +---------------------+
| Developers  |---->| Batch API Edge   |---->| Job Control Plane   |
+-------------+     | auth / quota     |     | (PG metadata)       |
                    +--------+---------+     +----------+----------+
                             |                          |
                             v                          v
                    +----------------+         +--------+----------+
                    | Ingest Workers |-------->| Object Store      |
                    | expand JSONL   |         | inputs / results  |
                    +--------+-------+         +-------------------+
                             |
                             v
                    +----------------+         +-------------------+
                    | Item Queues    |-------->| Fair Share / QoS  |
                    | by model/org   |         |                   |
                    +--------+-------+         +-------------------+
                             |
                             v
                    +----------------+
                    | Packer         |  packing_key → GPUBatch
                    | length/prefix  |
                    +--------+-------+
                             |
         +-------------------+-------------------+
         v                   v                   v
+----------------+  +----------------+  +------------------+
| Safety Workers |  | Batch GPU Pool |  | Result Writers   |
| (pre/post)     |  | (preemptible+) |  | → object store   |
+----------------+  +--------+-------+  +--------+---------+
                             |                   |
                             v                   v
                      Usage events         Webhook Dispatcher
                      → Billing            → customer endpoints
```

### 4.2 Job lifecycle sequence

```text
Client          Batch API         Ingest           Packer           GPU Worker        Results
  |                |                |                |                |                 |
  | Create batch   |                |                |                |                 |
  |--------------->| persist job    |                |                |                 |
  |  batch_id      |--------------->| expand items   |                |                 |
  |<---------------|                |--------------->|                |                 |
  |                |                |                | form GPUBatch  |                 |
  |                |                |                |--------------->|                 |
  |                |                |                |                | execute         |
  |                |                |                |                |---------------->|
  |                |                |                |                | ack items       |
  | GET status     | counts         |                |                |                 |
  |--------------->|<---------------------------------------------------------------|
  | GET results    |                |                |                |                 |
  |--------------->|--------------------------------------------------------------->|
  |                | webhook on terminal                                            |
```

### 4.3 Packing data flow

```text
Items (model_version=Sonnet-X, len_bucket=2k, prefix=P)
   → packer buffer until B>=target OR wait_ms expired OR memory pressure
   → GPUBatch{items...}
   → worker executes with padding L_max in bucket
   → metrics: padding_waste, achieved_B, tok/s
```

### 4.4 Preemption flow

```text
Interactive pressure high
  → capacity controller marks batch workers preemptible
  → finish current GPUBatch micro-step / checkpoint item boundary
  → release GPUs to interactive pool
  → items remain durable pending
  → when pressure drops, packer resumes
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Durability & data loss prevention

- ACK create only after job metadata + input ref durable.  
- Item state machine with CAS: `pending→running→succeeded|errored|canceled`.  
- GPU execution at-least-once; result put is deterministic by `batch_id/item_id`.  
- Writer uses write-then-CAS status to avoid losing success on crash.

#### 5.1.2 Retries & idempotency

| Layer | Mechanism |
|-------|-----------|
| Job create | Idempotency-Key |
| Item execute | `(batch_id, item_id, attempt)` ; result immutable on success |
| Webhook | Delivery id + customer retry; at-least-once |
| Billing | Idempotent apply on item_id |

**Poison items:** after K attempts → `errored` with code; don’t block job forever.

#### 5.1.3 Rate limiting

- Items/day per org; concurrent running items; submit QPS.  
- Packer fair share so one org can’t fill all buffers.  
- Result download bandwidth fair share.

#### 5.1.4 Partial failure semantics

Job `ended` when all items terminal. Status payload includes counts. Customers must handle per-item errors (same as online API errors).

#### 5.1.5 Safety reliability

Async allows fuller output scans before customer visibility. Fail closed on high-sev. Safety outage: pause scheduling rather than emit unchecked.

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Scale | Control | Packing | Compute | Results |
|-------|---------|---------|---------|---------|
| Baseline | Single region PG | One packer/model | 100 GPUs | One bucket/job |
| **10×** | Sharded job metadata | Packer fleet by key | 1K GPUs | Partitioned outputs |
| **100×** | Cell by org | Hierarchical packers | Multi-region | Lifecycle tiers |
| **1,000×** | Global director | Specialty length/long-ctx fleets | 100K-class | Cold archive |

#### 5.2.2 Traffic ups/downs

- Nightly eval storms: autoscale packers + borrow GPUs.  
- Interactive holidays: batch finishes early (good).  
- Interactive launches: batch SLO degrades gracefully within published window.

#### 5.2.3 Storage parallelization

```text
inputs/  org/batch_id/part-000.jsonl
results/ org/batch_id/part-000.jsonl
manifest.json with part etags
```

Avoid single-object multi-TB append; write parts and compose manifest.

#### 5.2.4 Parallelization of GPUs

- Many workers pull independent GPUBatches.  
- Within worker: large B + internal continuous batching.  
- Prefix clustering: sort items by prefix hash to raise cache hits across sequential batches.

#### 5.2.5 What breaks at each jump

| Jump | Breaks | Fix |
|------|--------|-----|
| 10× | PG payloads; single result file | Object parts; metadata only in DB |
| 100× | Packer hotspot; unfair org | Shard packing_key; fair queues |
| 1,000× | Cross-region data gravity | Process in-region near inputs; replicate metadata |

### 5.3 Maintainability

#### 5.3.1 Versioning

- Freeze `model_version` resolution at job validate time (or per-item recorded).  
- Packing algorithm version in metrics for A/B.  
- Pricing version on usage events.

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| GPU util / tok/s/GPU | Core efficiency |
| padding_waste_ratio | Packing quality |
| avg_batch_B | Are we actually batching? |
| job_age_p99 | SLO |
| items_requeued | Reliability |
| preempt_count | Isolation health |
| safety_fail_rate | Policy |
| $/MTok realized | Business |

#### 5.3.3 SLOs

| SLO | Target |
|-----|--------|
| Accepted job durable | 99.99% |
| Finish within tier window (e.g. 24h) | 99% |
| Incorrect item/result mismatch | ~0 |
| Interactive impact from batch | within error budget |
| Webhook delivery eventual | 99.9% (with poll backup) |

#### 5.3.4 Config & ops

- Hot knobs: target_B, max_wait_pack, length_bucket_edges, fair_share weights.  
- Canary packing strategies on shadow traffic.  
- Runbooks: stuck jobs, result part corruption, preempt loops, safety pause.

#### 5.3.5 Maintainable packing code

Keep packing pure: `items → GPUBatch[]` function with property tests (never mix models; waste bounds; fairness).

---

## 6. Wrap-Up

### 6.1 Summary talking points

1. **Thesis:** compatible batched GPU work amortizes kernel overhead—$/tok falls when util rises and padding stays bounded.  
2. **Product:** durable async jobs with per-item results (Messages Batches style).  
3. **Packing keys** (model, params, length, prefix) matter as much as “bigger B.”  
4. **Metadata DB + object storage**—never put all prompts in Postgres.  
5. **At-least-once execution, idempotent results/billing.**  
6. **Isolate or preempt** so batch never melts Claude chat.  
7. Scale via sharded packers, partitioned results, regional fleets.

### 6.2 Risk register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Padding waste | Cost regression | Length buckets |
| Interactive interference | Chat SLO burn | Separate pools + preemption caps |
| Poison items | Job stalls | Attempt caps; quarantine |
| Result loss | Customer trust | Write-then-CAS; checksums |
| Double billing on retry | Finance risk | Idempotent item_id |
| Safety skip temptation | Brand/legal | Hard gate in packer |
| Unbounded pack wait | Latency SLO miss | Flush timers |

### 6.3 Phased rollout

| Phase | Ship |
|-------|------|
| MVP | Batch create/poll/results; single-region; basic pack by model+length; separate GPU pool |
| 1.5 | Webhooks; prefix clustering; fair share; usage discounts; cancel |
| 2 | Preemptible borrow; multi-region; partitioned mega-jobs; stricter async safety |
| 3 | Global capacity market; auto packing tuner; cold archive; eval mega-fleets |

---

## 7. Deeper / Related Interview Questions

### Q1. If a batch of 32 costs nearly the same as 1, are 32 requests free?

**A:** No. Marginal FLOPs still scale roughly with tokens×layers. The win is **amortized overhead + higher sustained util**, not zero marginal cost. Padding can erase gains.

### Q2. How do you choose length buckets?

**A:** Histogram production prompt lengths; set edges so within-bucket pad waste <10–20% and each bucket still accumulates target_B within max_wait. Too many buckets → fragmentation.

### Q3. FIFO queue vs packing buffer?

**A:** Pure FIFO underfills GPUs. Packing buffers re-order within fairness constraints. Bound reordering so no org starves (aging).

### Q4. Why not always use interactive continuous batching for batch jobs?

**A:** You can reuse the engine, but product/control plane differs: deep queues, fat target B, result durability, cheaper SKU, preemption. Scheduling policy ≠ chat policy.

### Q5. What data structure for the packer?

**A:** Map keyed by `packing_key` → buffer list/deque of items; heap of buffers by (age, size) to decide flushes; token/byte counters for memory.

### Q6. How do you avoid hot keys on a popular prefix?

**A:** Cap buffer size per prefix; schedule multiple GPUBatches with same prefix across workers; replicate cached prefix blocks.

### Q7. Consistent hashing role?

**A:** `packing_key → packer shard`; `org_id → metadata cell`; `batch_id → result partition`. Workers may hash sticky for cache warmth.

### Q8. Deal-breaker when co-batching?

**A:** Different `model_version` or incompatible precision/adapter in one kernel launch. Also unbounded wait for a perfect full batch.

### Q9. How do webhooks not become a thundering herd?

**A:** Jittered delivery; per-endpoint concurrency caps; exponential backoff; circuit breakers; poll remains source of truth.

### Q10. Memory: where do 5B items live?

**A:** Compact status in KV/DB shards; payloads in object storage; queues hold item ids + refs only.

### Q11. Algorithm for fair share across orgs?

**A:** Deficit round-robin on items or tokens scheduled; max reservation % per org; burst credits decay.

### Q12. How does preemption work cleanly?

**A:** Preempt at item or micro-batch boundaries; persist partial only if product supports; else re-queue whole item idempotently. Never tear GPU kernels without freeing KV.

### Q13. Indexing/metadata schema essentials?

**A:** `batch_id` PK; index `(org_id, created_at)`; item table `(batch_id, custom_id)` unique; status indexes for packer reclaim scans carefully (avoid hot scans—use queues).

### Q14. How do you compute padding waste?

**A:** `waste = sum_i (L_max - L_i) / (B × L_max)` on tokens padded; track per bucket; alert when > threshold.

### Q15. Batch API vs job scheduler like Airflow?

**A:** Airflow orchestrates DAGs; this system is a **GPU-aware throughput scheduler** with packing. You might trigger Airflow externally, but don’t put CUDA batching inside Airflow workers naively.

### Q16. What fails in a naive “group any 32 requests”?

**A:** Mixed lengths → pad blowup; mixed models → impossible; one giant request blocks; unfairness; safety not applied; retries double-bill.

### Q17. How do you bind billing to batch discounts?

**A:** Usage events tagged `channel=batch` + pricing_version; ledger applies batch rates; interactive events cannot be silently retagged.

### Q18. Load balancer for batch workers?

**A:** Pull-based queues better than push LB—workers take GPUBatches when they have KV headroom. Push requires accurate free-memory signaling.

### Q19. How do long-context Opus batch items change design?

**A:** Tiny B due to KV; separate pool; don’t co-schedule with short Haiku packs; price and SLO differently.

### Q20. Fanout problem sending results to many subscribers?

**A:** Usually one result object + webhook to creator. If fanout needed, use object storage notifications / customer-side bus—not the inference plane.

### Q21. What observability proves the thesis to executives?

**A:** tok/s/GPU, padding_waste, $/MTok batch vs interactive, GPU util, % time preempted, job on-time rate.

### Q22. How do you test packers?

**A:** Property tests: compatibility invariants; simulations on real length histograms; chaos worker kills; verify idempotent item success.

### Q23. DB bottleneck patterns?

**A:** Updating every item row synchronously from GPUs. Fix: chunk status updates; queue-driven state; Redis counters for progress with periodic PG rollup.

### Q24. Security for result URLs?

**A:** Signed short-lived URLs; authz on batch_id; no world-readable buckets; scan for accidental secret leakage in prompts/results if enterprise policy requires.

### Q25. How does Anthropic safety differ in batch?

**A:** Same Constitutional/policy bar; can afford stricter offline classifiers; still fail closed; document that batch isn’t a safety bypass.

### Q26. Horizontal scaling the control plane?

**A:** Shard jobs by `org_id` or `batch_id`; keep submit path light; push heavy expand to ingest workers.

### Q27. When is waiting for a bigger batch wrong?

**A:** When job deadline is near; when buffer memory pressure is high; when waste would increase by waiting for mismatched lengths; when GPUs are idle now.

### Q28. Relationship to prompt caching?

**A:** Sort/pack by prefix to maximize cache hits across the batch window; meter cache writes/reads per item; huge win for shared system prompts in eval grids.

### Q29. Classic algorithms worth naming?

**A:** Consistent hashing; deficit round-robin; bin packing / length bucketing (approx); exponential backoff; CAS state machines; Little’s Law for queue depth.

### Q30. Staff closing line?

**A:** “Batch inference is job scheduling + bin packing where the machine is a GPU: durable items, compatibility-aware packing, idempotent results, and ruthless isolation from interactive Claude—so amortized cost approaches the hardware’s real efficiency.”

---

*End of GPU Batch Inference System design.*
