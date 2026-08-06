# System Design: Flawed Inference-Batching Review & Repair

> **Focus areas:** Mentorship-style design review · Throughput vs latency · Correctness bugs · Admission control · Streaming vs batch · GPU memory races · Fairness  
> **Interview type:** Directly reported for **Anthropic EM interview** — review a junior engineer’s design, diagnose, prioritize, repair  
> **Style:** (A) Flawed design → (B) Interviewer Q&A → (C) Diagnosis → (D) Repaired architecture with full deep dive  
> **Company theme:** GPU efficiency, batching, reliability, cost — ordinary distributed systems inside AI serving

---

## Table of Contents

1. [How to Use This Doc (EM Interview Framing)](#1-how-to-use-this-doc-em-interview-framing)
2. [(A) The Flawed Design Presented](#2-a-the-flawed-design-presented)
3. [(B) Interviewer Q&A / Requirements Clarification](#3-b-interviewer-qa--requirements-clarification)
4. [(C) Diagnosis — Bottlenecks & Correctness Bugs](#4-c-diagnosis--bottlenecks--correctness-bugs)
5. [(D) Repaired Architecture — Clarify → Estimates → HLD → Diagram → Deep Dive → Wrap → Questions](#5-d-repaired-architecture)
6. [EM Mentorship Angle](#6-em-mentorship-angle)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. How to Use This Doc (EM Interview Framing)

Anthropic EM loops often probe: **Can you review imperfect AI-infra designs without arrogance, find real failure modes, prioritize fixes, and still own a solid end architecture?**

Suggested live flow (45–60 min):

| Phase | Time | You do |
|-------|------|--------|
| Read junior design | 5–8 min | Restate; ask clarifying Qs |
| Requirements lock | 5 min | Latency classes, batching goals, SLOs |
| Diagnosis | 10–12 min | Rank bugs by blast radius |
| Repair sketch | 15–20 min | HLD + critical invariants |
| Metrics & mentorship | 5–10 min | How you’d coach the author |

**Tone:** Curious, precise, kind. “Here’s what breaks under load” > “This is wrong.”

---

## 2. (A) The Flawed Design Presented

*The following is the junior engineer’s design as “submitted” for review. Treat it as the interview prompt artifact.*

### 2.1 Junior’s problem statement

> “We need an inference gateway that batches requests to our LLM for better GPU utilization. Clients send prompts over HTTP; we batch them on the GPU, run `generate()`, and return completions. Streaming can be added later by just flushing tokens as they appear.”

### 2.2 Junior’s architecture narrative

1. **API servers** (stateless) accept `POST /v1/complete` with `{prompt, max_tokens, temperature, stream?: bool}`.  
2. Each API server pushes jobs into a **single global Redis list** `infer_queue`.  
3. **Batch workers** (one process per GPU) `BRPOP` as many items as possible up to `MAX_BATCH=64`, waiting up to `BATCH_TIMEOUT_MS=50`.  
4. Worker **pads** all sequences to `max(len(tokens))` in the batch, runs one forward pass loop until all sequences hit EOS or `max_tokens`.  
5. Results written to Redis hash `result:{request_id}`; API server **polls** every 10ms until present.  
6. For `stream=true`, worker publishes each token to Redis pub/sub channel `stream:{request_id}`; API server subscribes and SSE-writes to client.  
7. **Tokenization** done on GPU worker with a global Python `tokenizer` singleton; “we share it across threads for speed.”  
8. **KV cache / model** loaded once per process; “multiple threads in the worker call `model.generate` on the same module for different batches to keep GPU busy.”  
9. **No rate limits** — “Kubernetes HPA will scale API pods; queue absorbs bursts.”  
10. **Fairness:** FIFO queue — “fair enough.”  
11. Padding: “pad with tokenizer.pad_token; attention mask all ones for speed.”  
12. Stopping: “batch runs until the longest request finishes; short requests just ignore extra tokens.”

### 2.3 Junior’s diagram

```text
Client -> API Pod -> Redis List (infer_queue)
                        |
                        v
              GPU Worker (BRPOP up to 64)
                        |
                        +--> pad & generate
                        |
            +-----------+-----------+
            v                       v
     result:{id} in Redis     pubsub stream:{id}
            ^                       |
            +------- poll/SSE ------+
```

### 2.4 Junior’s claimed estimates

- “A100 can do batch 64 easily; utilization will be ~90%.”  
- “50ms batch window → +50ms latency only.”  
- “Redis can do millions of ops; no bottleneck.”  
- “HPA on API pods handles 100× traffic.”

### 2.5 Junior’s “tests”

- Unit test: single request returns “hello”.  
- Manual: two concurrent requests both return.  
- No load test; no soak; no multi-tenant test.

---

## 3. (B) Interviewer Q&A / Requirements Clarification

*Before roasting the design, lock requirements. In the EM interview, demonstrate this discipline.*

### 3.1 Functional Requirements

| # | Question | Expected answer | Implication |
|---|----------|-----------------|-------------|
| F1 | Sync complete vs stream? | Both; stream is product-critical | Separate scheduling classes |
| F2 | Multi-tenant? | Yes — free vs paid | Fairness / quotas |
| F3 | Max context / gen? | 8k ctx, 2k gen typical; bursts 32k | Memory-aware batching |
| F4 | SLO classes? | Interactive p99 TTFT vs batch jobs | Multiple queues |
| F5 | Ordered tokens? | Yes; no drops | Stream protocol correctness |
| F6 | Cancel / disconnect? | Yes | Cancel signals; free GPU |
| F7 | Idempotency? | Client retries | request_id dedupe |
| F8 | Model versions? | Pinned per request | Worker pools per model |

### 3.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | TTFT (stream) | p50 < 300ms, p99 < 1.5s under nominal |
| N2 | Completeness | No truncated-wrong due to batching bugs |
| N3 | Correctness | Attention masks correct; no cross-talk |
| N4 | GPU mem safety | No OOM kills from unbounded batch |
| N5 | Availability | Shed load vs melt |
| N6 | Fairness | No free-tier starvation of paid; no mega-prompt HOL blocking |
| N7 | Cost | High goodput tokens/s/$ |

### 3.3 Cases

**Happy:** short complete; streaming chat; mixed lengths with continuous batching.  
**Edge:** cancel mid-stream; retry storm; 32k context whale; temperature 0 vs sampling; worker crash mid-batch; Redis blip; thundering herd on deploy.

### 3.4 Scales

| Metric | 1× | 10× | 100× | 1,000× |
|--------|----|-----|------|--------|
| QPS | 50 | 500 | 5k | 50k |
| Concurrent streams | 200 | 2k | 20k | 200k |
| GPUs | 8 | 80 | 800 | 8k |
| Avg input toks | 800 | 800 | 1–2k | 1–2k |
| Avg out toks | 400 | 400 | 400–800 | 400–800 |

### 3.5 Etc.

- Continuous batching / paged attention available as design tools (vLLM-like).  
- Not designing training.  
- EM also grades **prioritization** and **coaching plan**.

**Restated scope:**

> Repair inference batching for mixed sync/stream LLM traffic with correct masking & memory safety, admission control, fairness, and measurable GPU goodput—not “Redis list + pad to max + pray.”

---

## 4. (C) Diagnosis — Bottlenecks & Correctness Bugs

Rank by **severity × likelihood**. Speak this ordered list in the interview.

### 4.1 Critical correctness bugs

| ID | Bug | Why it breaks | Symptom |
|----|-----|---------------|---------|
| C1 | **Attention mask all ones with pad** | Pads attend as real tokens | Garbage / hallucinated suffixes; safety classifiers confused |
| C2 | **Batch runs until longest finishes; short reqs “ignore extra”** | If ignore is wrong, short reqs keep decoding; if early-stop poorly implemented, wasted compute or wrong EOS handling | Latency inflation; wrong text |
| C3 | **Shared tokenizer singleton across threads without locks** | Many tokenizers are not thread-safe | Corrupt token ids; rare heisenbugs |
| C4 | **Multi-thread `model.generate` on same module/GPU** | GPU memory races; undefined concurrent CUDA use | OOM, segfaults, silent corruption |
| C5 | **Streaming via Redis pub/sub** | Pub/sub is fire-and-forget; no replay; subscriber miss = lost tokens | Broken streams on blip |
| C6 | **Poll `result:{id}` without TTL / ownership** | Orphan keys; wrong requester could guess ids if not unguessable | Leak / stuck polls |
| C7 | **No cancel path** | Disconnect leaves work running | Wasted GPU; ghost streams |
| C8 | **FIFO mixing 32k whales with 128-token chat** | Head-of-line blocking | p99 explodes for interactive |

### 4.2 Critical systemic / capacity bugs

| ID | Bug | Why | Symptom |
|----|-----|-----|---------|
| S1 | **Unbounded Redis queue** | No admission control | OOM Redis; multi-minute lag; retry storms amplify |
| S2 | **HPA on API pods only** | Queue grows; GPUs unchanged | False scalability |
| S3 | **Static `MAX_BATCH=64` by request count** | Ignores tokens × layers × KV bytes | GPU OOM at high context |
| S4 | **Fixed 50ms batch window for streams** | Adds delay every batch formation; doesn’t match continuous batching | TTFT floor; poor utilization as load varies |
| S5 | **Sync poll every 10ms × N clients** | Redis CPU melt; silly latency | API scaling cliff |
| S6 | **No memory reservation / preemption** | Large batch admits then dies | Cascading worker restarts |
| S7 | **Single global queue** | No locality, no priority, noisy neighbor | Unfairness; poor cache locality |
| S8 | **“Utilization 90%” vanity** | High SM% with padding waste ≠ goodput | Cost lie |

### 4.3 Reliability / operability gaps

- No idempotency keys.  
- No dead-letter for poison prompts.  
- No backpressure to clients (`429` / `503` with retry-after).  
- No distinct metrics for queue wait vs compute vs stream stall.  
- No load test plan.

### 4.4 What the junior got *right* (say this!)

- Batching intuition for GPU efficiency.  
- Separating API from workers.  
- Wanting a timeout to form batches.  
- Thinking about streaming as a product need.

EM signal: **credit partial correctness**; then raise the bar.

### 4.5 Priority fix order (mentorship backlog)

| Prio | Fix | Rationale |
|------|-----|-----------|
| P0 | Single-threaded / single in-flight batch per GPU context; fix masking | Correctness & crash |
| P0 | Admission control + max queue time + 429 | Stop meltdown |
| P0 | Memory-aware batching (token budgets) | Stop OOM |
| P1 | Continuous batching + separate stream scheduling | Utilization + TTFT |
| P1 | Durable stream buffer (not pure pubsub) | Stream correctness |
| P1 | Cancel + idempotency | Product + cost |
| P2 | Priority / fair queues | Multi-tenant |
| P2 | Per-model worker pools | Operability |
| P3 | Advanced: paged KV, speculative decoding | Efficiency |

---

## 5. (D) Repaired Architecture

*From here, match the standard interview structure — this is the design you “own” after the review.*

### 5.1 Clarify Requirements (locked)

See §3. MVP repair scope:

1. Memory-safe continuous batching for completions + streams.  
2. Admission control with explicit load shedding.  
3. Correct tokenize/pad/mask; safe concurrency.  
4. Priority queues (interactive vs batch).  
5. Cancel, idempotency, backpressure.  
6. Observability: TTFT, TPOT, goodput, OOM, queue wait.  
7. Hand-off notes for junior’s learning path.

Out of MVP: multi-region inference mesh, MoE expert parallelism design, custom CUDA kernels.

### 5.2 Back-of-the-Envelope

**Tokens/s capacity (order-of-magnitude):**

- Suppose 1×H100 decode ≈ 150–250 tok/s effective for large model at batch 1; continuous batching may raise **aggregate** tok/s 5–20× depending on model/memory.  
- Don’t defend fake precision; defend **memory**:

KV cache rough:

\[
\text{KV bytes} ≈ 2 × layers × kv_heads × dim × dtype × seq × batch
\]

Example (illustrative): if 1k tokens × concurrent 128 sequences exhausts HBM, `MAX_BATCH=64` by count is meaningless.

**Queueing:**

- If GPU goodput = 50k out-tok/s and arrival demands 80k, no batching trick saves you — **shed or scale GPUs**.  
- Unbounded queue only hides the inequality until Redis dies.

**Redis poll tax:**

- 5k clients × 100 poll/s = 500k Redis ops just for waiting — redesign to **push** (long poll, gRPC stream, worker→gateway callback).

**Padding waste:**

- Batch lengths `[128, 128, 8000]` with naive pad → enormous waste; continuous batching / packing essential.

### 5.3 High-Level Design (repaired)

#### 5.3.1 Components

| Component | Role |
|-----------|------|
| Edge / API Gateway | Auth, quotas, idempotency, 429 |
| Admission Controller | Token-bucket + queue deadline + GPU mem estimate |
| Scheduler | Priority WFQ; interactive vs batch; whale isolation |
| Batch Manager (per GPU worker) | Continuous batching; KV paged; in-flight page table |
| Model Runtime | Single owning thread/process for CUDA context |
| Stream Hub | Durable per-request buffer (Redis stream / NATS / in-mem + spill) |
| Control Plane | Model version pools; autoscaling on **GPU lag**, not API CPU |
| Telemetry | SLIs below |

#### 5.3.2 Request path (sync)

```text
Client → API: POST /complete (Idempotency-Key)
API → Admit: estimate tokens_in, max_out, priority
Admit: reserve slot OR 429 Retry-After
API → Scheduler: enqueue Job
Worker: continuous-batch join when mem allows
Worker → StreamHub/Result: output
API ← wait via future/long-poll (no 10ms spam)
API → Client: JSON
Admit: settle / release reservation
```

#### 5.3.3 Streaming path

```text
Admit similarly
Worker appends tokens to durable StreamHub (id, seq)
API reads from seq=0.. with XREAD / gRPC; SSE to client
On cancel: API → Scheduler cancel → worker drops sequence; free KV pages
```

**Not Redis pub/sub** as sole transport.

#### 5.3.4 Continuous batching (conceptual)

- Iteration loop on GPU: select sequences with remaining work that fit memory.  
- Prefill new prompts when decode slots free.  
- Remove finished sequences; don’t wait for batch-global max_tokens.  
- Attention masks / page tables always correct for active tokens only.

#### 5.3.5 Concurrency model (hard rule)

```text
1 CUDA context owner per GPU (process or dedicated thread)
Tokenizers: pool of immutable clones OR lock around stateful tokenizer
Never: threads concurrently calling forward on same module
```

#### 5.3.6 Admission & backpressure

```text
if queue_wait_p95 > SLO_budget: reject new low-priority
if estimated_kv + working > HBM_budget: reject or downclock max_tokens
always return Retry-After; never silent infinite queue
```

#### 5.3.7 Fairness

| Queue | Who | Notes |
|-------|-----|-------|
| Interactive | Paid chat / API latency tier | Highest |
| Standard | Default | WFQ |
| Batch | Offline eval | Separate GPU pool preferred |
| Whale lane | ctx > threshold | Isolated so not HOL |

#### 5.3.8 Trade-offs

| Topic | Options | Choice |
|-------|---------|--------|
| Static microbatch vs continuous | Static simpler | Continuous for prod streams |
| Result sync | Poll vs push | Push / long-poll |
| Stream durability | Pubsub vs log | Redis Stream / equivalent |
| Padding | Naive vs pack | Pack / paged |
| Scale signal | API CPU vs GPU queue lag | **GPU lag** |

### 5.4 Architecture Diagram

```text
+--------+    +-------------+    +------------------+
| Client |--->| API Gateway |--->| Admission + Quota|
+--------+    +------+------+    +--------+---------+
                     |                    |
                     |              +-----v-----+
                     |              | Scheduler |
                     |              | WFQ+whale |
                     |              +-----+-----+
                     |                    |
                     |         +----------+-----------+
                     |         v                      v
                     |   +-----------+          +-----------+
                     |   | GPU Pool  |          | Batch Pool|
                     |   | interactive|         | (optional)|
                     |   +-----+-----+          +-----------+
                     |         |
                     |         | tokens (seq)
                     |         v
                     |   +-----------+
                     +-->| Stream Hub|<-- cancel
                         +-----+-----+
                               |
                               v
                           SSE / JSON
```

**Worker internals:**

```text
+--------------------------------------+
| GPU Worker Process                   |
|  TokenizerPool (thread-safe)         |
|  BatchLoop thread (ONLY CUDA owner)  |
|    - page table / KV manager         |
|    - prefill / decode step           |
|  IO threads: pull jobs, push tokens  |
+--------------------------------------+
```

### 5.5 Design Deep Dive

#### 5.5.1 Reliability invariants

1. **One CUDA owner per device.**  
2. **Masks / page tables reflect real tokens only.**  
3. **Finished sequences leave the batch immediately.**  
4. **Admission rejects rather than unbounded queue growth.**  
5. **Stream tokens are sequenced and durable until ACK/TTL.**  
6. **Cancel frees KV within bounded time.**  
7. **Idempotency-Key ⇒ at-most-one billed completion** (result cached).  
8. **Poison job isolation** (max retries → DLQ).  
9. **Model version pinned** at admit.  
10. **Backpressure visible to clients** (429/503).

Failure table:

| Failure | Behavior |
|---------|----------|
| Worker crash | Jobs nack/requeue if not streaming-acked; streams error with retryable code |
| Stream hub blip | Client reconnect with `Last-Event-ID` / seq |
| OOM near miss | Admit estimator shrinks; worker never commits overcommit batch |
| Redis down | Fail closed admit; don’t pretend to queue forever |
| Retry storm | Idempotency + coherent 429 |

#### 5.5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Single pool continuous batching; Redis stream hub OK |
| 10× | Shard schedulers by model; separate interactive GPUs |
| 100× | Cell by tenant/region; hierarchical admission |
| 1,000× | Global LB to cells; spot burst pools; speculative decoding |

Autoscaling metric:

```text
scale_up if (queue_wait_p50 > X) OR (kv_pressure > Y)
scale_down if idle_decode_slots high for sustained window
NEVER scale only on API CPU
```

#### 5.5.3 Maintainability

- Golden tests: masking, EOS, cancel, idempotent retry.  
- Chaos: kill worker mid-stream.  
- Shadow traffic compare vs unbatched reference for correctness.  
- Metrics cardinality discipline.

#### 5.5.4 Correctness repairs mapped from bugs

| Bug | Repair |
|-----|--------|
| C1 | Build attention mask / use paged KV without fake pad attend |
| C2 | Per-sequence stop; continuous batch remove-on-EOS |
| C3 | Tokenizer pool / lock |
| C4 | Single CUDA owner |
| C5 | Durable stream log + resume |
| C6 | Unguessable ids + TTL + authz on read |
| C7 | Cancel channel |
| C8 | Whale lane + memory admit |
| S1–S2 | Admission + scale on GPU lag |
| S3 | Token/KV budget batching |
| S4 | Continuous batching |
| S5 | Push results |
| S8 | Report **goodput tok/s** and padding waste |

#### 5.5.5 GPU efficiency

- Prefill/decode split scheduling.  
- Avoid giant pad.  
- Track `effective_tokens / theoretical_peak`.  
- Optional: chunked prefill so interactive TTFT stays healthy when whales arrive.

#### 5.5.6 Cost

- Idle GPU from HOL and OOM restarts is pure burn.  
- 429 early is cheaper than multi-minute queues that cause client retries ×3.

#### 5.5.7 Safety interaction

- Incorrect padding/masking can change model behavior → safety eval diffs.  
- Stream partial output still needs safety policy (buffer or classifier) — note boundary; don’t ignore in EM discussion.

### 5.6 Wrap-Up (repaired system)

**We repaired** unbounded-queue, race-prone, mask-incorrect static microbatching into a **memory-aware continuous batching** serving system with **admission control**, **durable streaming**, **fair queues**, and **GPU-lag autoscaling**.

**Decisions to defend:**

1. Credit junior’s batching instinct; reject unbounded FIFO.  
2. Correctness before utilization theater.  
3. Continuous batching for mixed lengths/streams.  
4. Durable streams ≠ pubsub.  
5. One CUDA owner.  
6. Admit with KV estimates.  
7. Scale on GPU signals.  
8. Whale isolation.  
9. Cancel + idempotency.  
10. Mentorship backlog P0→P3.

**Risks:** estimator error; stream hub hotspot; over-fragmentation of priority queues.

### 5.7 Deeper questions (for the repaired design)

See also §7. Quick set:

- How does paged attention change admission math?  
- Where does speculative decoding fit?  
- Multi-LoRA batching risks?  
- Exactly-once vs at-least-once for billed tokens?

---

## 6. EM Mentorship Angle

### 6.1 How you deliver feedback

1. **Restate** their goals (utilization, simple API).  
2. **Acknowledge** what works.  
3. **Show one concrete failure** (mask all-ones demo; or concurrent CUDA).  
4. **Stack-rank** fixes with user impact.  
5. **Pair on P0**; assign P2 with design doc template.  
6. **Define done:** load test + correctness suite + dashboards.

### 6.2 Coaching prompts (Socratic)

- “What happens when Redis consumers lag and clients retry?”  
- “How many bytes is batch=64 at 8k context?”  
- “Is GPU util the metric you’d put on a career ladder doc?”  
- “Walk me through token ownership if a client disconnects.”

### 6.3 Org process upgrades

- Design review checklist for inference changes.  
- Mandatory load test harness (k6 + GPU metrics).  
- “No new queue without max depth + poison story.”  
- Incident game day: OOM storm.

### 6.4 Measurement plan you’d demand

| SLI | Why |
|-----|-----|
| TTFT p50/p99 | Product |
| TPOT p99 | Stream smoothness |
| Queue wait | Admission quality |
| Goodput tok/s | Real efficiency |
| OOM / worker restart | Correctness of mem mgmt |
| 429 rate | Capacity truth |
| Cancel free latency | Cost hygiene |
| Mask/golden mismatch | Catch regressions |

### 6.5 What “great” looks like in the EM interview

- Diagnoses **correctness before cosmetics**.  
- Uses **numbers** (HBM, queue).  
- Separates **stream and batch** classes.  
- Shows **people leadership**: growth plan for junior, not only rewrite by heroics.  
- Ties to **Anthropic values**: reliability, safety-adjacent correctness, responsible cost.

---

## 7. Deeper / Related Interview Questions

### 7.1 Diagnosis drills

1. List top 5 bugs in the junior design without notes.  
2. Is pub/sub ever OK for token fanout?  
3. Why HPA-on-API is a false god.  
4. Demonstrate HOL with a numeric example.

### 7.2 Repair drills

5. Sketch continuous batching loop pseudocode.  
6. Design KV-aware admission.  
7. Multi-tenant fair queuing with starvation floors.  
8. Exactly how cancel interacts with in-flight decode.

### 7.3 EM drills

9. Junior disagrees that pubsub is wrong — how do you convince with an experiment?  
10. Prioritize for a oncall-burning week vs a greenfield rewrite.  
11. Write a 1-page design review response email.  
12. How do you prevent this class of design from merging again?

### 7.4 Stretch

13. Compare static batching, continuous batching, and chunked prefill.  
14. Batch across LoRA adapters.  
15. Heterogeneous GPU pool scheduling.  
16. Deterministic temperature-0 batching pitfalls (batch invariance).

### 7.5 Sample strong diagnosis monologue (~90 seconds)

> “The design’s instinct to batch is right, but I’d stop production rollout. Four P0s: attention masks treating pads as real tokens; concurrent model.generate across threads on one GPU; unbounded Redis queue without admission; and streams over pub/sub that can drop tokens. Secondary: static batch-by-count ignores KV memory, FIFO lets whales block chat, and HPA on API pods won’t add GPUs. I’d fix ownership and masking first, add admission with 429s the same day, then move to continuous batching with a durable stream log. Success metrics are TTFT, goodput, OOM rate—not SM utilization alone. I’d pair with the author on P0s and turn this into a checklist so we coach, not just rewrite.”

---

## Appendix A: Junior design “code smells” checklist

- [ ] Global unbounded queue  
- [ ] Static max batch by count  
- [ ] Pad + mask ones  
- [ ] Shared mutable tokenizer  
- [ ] Multi-thread CUDA  
- [ ] Pubsub streams  
- [ ] Busy poll results  
- [ ] No cancel  
- [ ] No idempotency  
- [ ] Scale signal wrong  
- [ ] FIFO only  
- [ ] No load test  

## Appendix B: Continuous batching pseudocode

```text
active = {}
while running:
  # 1) pull new jobs that fit memory
  while mem_free() and sched.has_interactive():
    job = sched.pop()
    active[job.id] = prefill(job)
  # 2) decode one step for all active
  tokens = decode_step(active)
  for id, tok in tokens:
    stream_hub.append(id, tok)
    if finished(id): free_kv(id); del active[id]
  # 3) process cancels
  for id in cancels: free_kv(id); del active[id]
```

## Appendix C: Attention mask vignette

```text
tokens: [HELLO] [WORLD] [PAD] [PAD]
mask_wrong: 1 1 1 1   # PAD attends — BUG
mask_right: 1 1 0 0
```

Better: don’t materialize pad; use ragged / paged representations.

## Appendix D: Admission estimator sketch

```text
cost = alpha * tokens_in + beta * max_out + gamma * concurrent_kv_pressure
admit if (queue_wait_ema < T) and (cost < residual_budget)
else 429
```

Tune alpha/beta from production; start conservative.

## Appendix E: Experiment to disprove pubsub streams

1. Run 1k streams.  
2. Restart subscriber mid-flight.  
3. Count missing seq gaps.  
4. Show durable log reconnect succeeds; pubsub doesn’t.

## Appendix F: Design review email template

```text
Subject: Design review: inference batching v0 — block on P0 correctness

Thanks for the clear write-up and for pushing utilization — that’s the right north star.

Before merge, we need P0 fixes: (1) mask/pad correctness, (2) single CUDA owner,
(3) admission control with max queue deadline, (4) durable streaming.
I’ve sketched an approach in [doc] and reserved pairing time Thu.

P1 follows: continuous batching, cancel, idempotency.
Metrics for “done”: TTFT p99, goodput, OOM=0 on soak, 429 under 2x overload.

Appreciate the ownership — this will be a strong system once hardened.
```

## Appendix G: Soak test plan

| Test | Pass bar |
|------|----------|
| 2× overload 30m | Stable 429; no Redis OOM; no GPU crash loop |
| Mixed lengths | No correctness drift vs offline ref on temp 0 sample set |
| Cancel 20% | KV frees; no leak over 1h |
| Worker kill | Clients retry cleanly; no stuck bill |
| Whale+chat | Chat TTFT SLO held via isolation |

## Appendix H: Mapping to Anthropic themes

| Theme | Manifestation |
|-------|---------------|
| GPU efficiency | Continuous batching, goodput metrics |
| Reliability | Admit/shed; durable streams |
| Safety | Correct tokens; stream safety policy hooks |
| Cost | Reject early; cancel frees | 

## Appendix I: Flawed vs repaired comparison

| Area | Flawed | Repaired |
|------|--------|----------|
| Queue | Unbounded FIFO | Admitted WFQ + whale lane |
| Batch | Static pad 64 | Continuous memory-aware |
| Stream | Pubsub | Durable seq log |
| Concurrency | Racy | Single CUDA owner |
| Scale | API HPA | GPU lag |
| Client signal | Hang | 429/503 |

## Appendix J: Whiteboard order for live interview

1. Restate junior design (1 min)  
2. Ask 3 clarifying Qs (2 min)  
3. Top 5 bugs ranked (5 min)  
4. P0 fix sketch (5 min)  
5. Full repaired HLD (10 min)  
6. Metrics + mentorship (5 min)

## Appendix K: Numeric HOL example

- Whale: 30k prefill @ 5k tok/s prefill ≈ 6s exclusive if poorly scheduled.  
- 100 chat prefs arrive during whale; FIFO static batch waits → chat TTFT >> SLO.  
- Repair: chunked prefill + priority; whale on separate lane.

## Appendix L: Idempotency store

```text
Idempotency-Key + tenant -> request_id, status, result_ref, exp
TTL ≥ client retry window
On duplicate: return same result_ref / attach to same stream
```

## Appendix M: When static batching is still OK

- Offline batch eval with similar lengths.  
- Non-stream, latency-insensitive.  
- Still needs masks, mem budgets, admission.

## Appendix N: Glossary

| Term | Meaning |
|------|---------|
| TTFT | Time to first token |
| TPOT | Time per output token |
| Goodput | Useful tokens/s successfully delivered |
| HOL | Head-of-line blocking |
| Continuous batching | Dynamic join/leave of sequences each step |
| Whale | Outsized context/job |

## Appendix O: Junior growth plan (6 weeks)

| Week | Focus |
|------|-------|
| 1 | Masking + CUDA ownership fix; golden tests |
| 2 | Admission + load test harness |
| 3 | Durable streams + cancel |
| 4 | Continuous batching prototype |
| 5 | Fairness + whale lane |
| 6 | Doc + teach lunch-and-learn |

## Appendix P: Oncall runbook snippets

**Symptom:** stream gaps → check stream hub lag; not worker SM%.  
**Symptom:** OOM loop → drain traffic; roll back max context; fix admit.  
**Symptom:** Redis CPU hot → look for poll loops / giant queue.  
**Symptom:** p99 TTFT → whale HOL or batch window.

## Appendix Q: Sample interviewer pushes & responses

**Push:** “Just increase Redis memory.”  
**Response:** “That delays the meltdown and worsens retry storms; admission is the fix.”

**Push:** “Utilization dropped after your fix.”  
**Response:** “Padding waste fell; goodput and SLO rose — here’s the dashboard.”

**Push:** “Why not one giant batch always?”  
**Response:** “HBM and TTFT; continuous batching keeps utilization without pad death.”

## Appendix R: Minimal correct mask test vectors

Include empty prompt (reject), single token, max context, pad boundaries, EOS immediately, Unicode tokenization edge — all temp=0 snapshot compare.

## Appendix S: Full repaired component ownership RACI

| Component | Owner |
|-----------|-------|
| Admission | Serving team |
| Batch loop | Serving / kernels |
| Stream hub | Platform |
| Quotas | API governance |
| Eval gates | Safety (hooks) |

## Appendix T: Closing scorecard for self-eval after mock

- [ ] Did I credit the junior?  
- [ ] Did I rank by blast radius?  
- [ ] Did I lock requirements before redesign?  
- [ ] Did I use memory math?  
- [ ] Did I mention mentorship/process?  
- [ ] Did I define SLIs?

## Appendix U: Tokenization / padding bug deep dive (interview demo)

Junior claim: “pad with `pad_token`; attention mask all ones for speed.”

**What goes wrong mechanically**

1. Sequences of lengths 5, 12, 40 padded to 40.  
2. Positions 6–40 on the short sequence contain pad ids.  
3. With mask=1, queries at real positions attend to pads; pads may also attend among themselves.  
4. Logits at the real last token are polluted → wrong next-token distribution.  
5. At temperature 0, outputs become **batch-shape dependent** (non-invariant): same prompt yields different text depending on which neighbors share the batch.

**Interview gold line:** “If completions change when co-batched with a longer request, your masking is wrong—even if unit tests with batch=1 pass.”

**Repair demo test:**

```text
prompt P alone @ temp=0 → text T0
prompt P co-batched with long whale @ temp=0 → text T1
assert T0 == T1
```

## Appendix V: Shared GPU memory race vignettes

| Naive pattern | Failure mode |
|---------------|--------------|
| Thread A and B both `model.forward` | CUDA illegal access / deadlocks / silent wrong tensors |
| Two batches allocate KV without mutex | OOM killer loops |
| Tokenizer `encode` mutates global state | Cross-request token id corruption |
| Callback from async copy into Python GC’d buffer | Heisenbugs under load |

**Rule of thumb:** treat the model+KV manager as a **single-threaded actor**; IO threads only feed jobs and ship tokens.

## Appendix W: Prioritized 48-hour incident plan (EM)

*Production melted after junior design shipped to 5% traffic.*

| Hour | Action |
|------|--------|
| 0–1 | Feature-flag off streaming via pubsub path; shed with 503 |
| 1–4 | Hotfix: single CUDA owner + correct masks (cherry-pick) |
| 4–8 | Deploy admission max queue depth + 429 |
| 8–24 | Soak + compare temp=0 invariance tests |
| 24–48 | Postmortem; continuous batching project charter; checklist in CI |

People side: blameless postmortem; junior co-authors the checklist (learning, not exile).

## Appendix X: Fairness numeric vignette

- Interactive SLO: TTFT p99 < 1.5s.  
- Free tier FIFO shares GPU with paid.  
- Load: 70% free spam prompts, 30% paid.  
- Without WFQ, paid TTFT p99 → 4s+.  
- With weighted fair queue (paid weight 4×) + separate free shed first: paid recovers; free sees more 429s — **correct business behavior**.

## Appendix Y: Mapping bugs → user-visible harm

| Bug | User harm |
|-----|-----------|
| Mask all ones | Wrong/unsafe-ish answers |
| Pubsub loss | Truncated streams; broken clients |
| Unbounded queue | Multi-minute “hangs”; retry storms |
| CUDA races | 5xx / empty responses / rare wrong text |
| No cancel | Higher prices; slower for everyone |
| HOL whales | Chat feels broken at peak |

EM framing: prioritize by **user harm × frequency**, not by elegance.

## Appendix Z: Final EM interview one-pager

**Role:** Staff/EM reviewing serving design.  
**Stance:** Kind, specific, ranked.  
**P0:** correctness (mask, CUDA), meltdown (admit), stream durability.  
**P1:** continuous batching, cancel, idempotency.  
**P2:** fairness, whale lanes.  
**Success:** SLIs green under 2× soak; junior delivers week-1 fixes with pairing; process prevents recurrence.

---

*End of Flawed Inference-Batching Review & Repair system design.*