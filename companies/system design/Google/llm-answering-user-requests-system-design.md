# System Design: LLM Answering User Requests

> **Focus areas:** Serving · State · Safety · Capacity admission · Fallbacks · Streaming · Cost control  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split control-plane / prefill / decode / safety classes, explicit KV-cache & continuous-batching tradeoffs, honest degradation  
> **Interview theme:** Product **serving** path for an LLM answering users — **not** training, not GPU kernel trivia as the centerpiece

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

Goal: **bound the product**—a system that **answers user requests with an LLM**: authenticated API/app → prompt assembly → safety → model serving (streaming tokens) → persist conversation state → quotas/cost controls → graceful fallbacks under load. Focus on **serving architecture**, not training clusters.

### 1.0 What this is / is not

| Dimension | **LLM answering user requests (this doc)** | Not this |
|-----------|--------------------------------------------|----------|
| Primary job | Helpful, safe, streamed answers at product SLA | Train foundation models |
| Success | TTFT, tokens/s, safety, cost/answer, availability | Benchmark Elo alone |
| State | Conversations / sessions durable | Stateless one-shot only (optional mode) |
| Serving | Gateway, batching, KV-cache, routers | Custom CUDA kernels deep-dive MVP |
| Failure | Fallbacks: smaller model, cache, queue | Infinite queue holding GPUs |

**Scope statement:** Design the **serving path** for an LLM product that answers user requests—gateway, auth, prompt assembly, safety, continuous-batching inference, conversation state, admission control, multi-region, and fallbacks.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Interface? | Chat API + optional simple App UI | `sessions` + `completions` stream |
| F2 | Streaming? | Yes — token/SSE stream | Stream gateway ownership |
| F3 | History? | Multi-turn conversations | Durable session store |
| F4 | Models? | Primary + smaller fallback tier | Router + capacity pools |
| F5 | Safety? | Input/output classifiers; policy refusals | Parallel safety fleet |
| F6 | Auth? | User/API keys; per-project quotas | Gateway authn/z + limits |
| F7 | Tools? | Optional Phase 1.5 | Tool bus hooks |
| F8 | Caching? | Prompt prefix / semantic cache optional | KV-cache + answer cache |
| F9 | Idempotency? | Client retries safe | Idempotency-Key on create |
| F10 | Fallbacks? | Smaller model; cached; queue with deadline | Admission controller |
| F11 | Multi-region? | Global users | Edge + regional inference |
| F12 | Cost? | Cap per user/day; track $ | Metering + budgets |

**MVP functional scope:**

1. Authenticated `POST /v1/sessions/{id}/messages` (or `/chat/completions`) with **SSE stream**.  
2. **Durable user message** before/at admit (atomic turn).  
3. **Prompt assembly**: system + safety layers + truncated history + user message.  
4. **Input safety** classify → allow/refuse.  
5. **Router** picks model tier (primary/small) under capacity.  
6. Inference with **continuous batching** + **KV-cache**; stream tokens.  
7. **Output safety** on chunks / final (policy explicit).  
8. Finalize assistant message + usage meters; settle quota.  
9. **Fallbacks**: degrade model, serve semantic/exact cache, short queue, or 503 with Retry-After.  
10. Rate limits; abuse isolation; multi-region active-active edge with regional sticky sessions optional.

**Out of MVP:**

- Training / finetune pipelines  
- Full agent tool marketplace  
- Perfect cross-region conversation multi-primary sync  
- On-device models  
- Voice realtime (hooks only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT | Snappy | p50 < 500ms–1s; p99 < 2–3s (excl. long queue) |
| N2 | Decode smoothness | Steady tokens | ≥ 20–50 tok/s user-perceived when healthy |
| N3 | Availability | Product critical | 99.9% with degradation ≠ hard down |
| N4 | Durability | No lost sent user msgs after ACK | Session DB before stream commit |
| N5 | Safety | Block egregious harm | Fail closed on high-risk classifier outage |
| N6 | Fairness | Noisy users don't melt fleet | Quotas; WFQ admission |
| N7 | Cost | GPU $ dominated | Batching, cache, smaller fallback |
| N8 | Privacy | Conversations sensitive | Encryption; tenant isolation |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New session → user asks → stream answer → persist → show in history.  
2. Follow-up turn uses prior messages in context window.  
3. Primary saturated → router uses smaller model + notice.  
4. Repeated FAQ → semantic/exact cache hit → cheap answer.  
5. Safety refusal → typed refusal; billed minimally / policy.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit | Idempotency-Key → one turn |
| Client disconnect | Cancel decode or grace; finalize partial policy |
| Context overflow | Truncate/summarize older turns with product policy |
| Safety fleet brownout | Fail closed high-risk; degrade soft checks carefully |
| Inference OOM / KV full | Reject admit or preempt low priority |
| Hot key session | Row lock / per-session serial turns |
| Prompt injection | Safety + system layer separation; tool guards later |
| Long output runaway | Max tokens; stop sequences; cost cap |
| Region inference down | Reroute or queue; don't dual-write session corruptly |
| Cache poisoned | Authz on cache keys; TTL; safety recheck outputs |
| Starvation of free tier | Separate pools / weights — document fairness |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 1M | 10M | 100M | 1B |
| Peak concurrent streams | 20K | 200K | 2M | 20M |
| Peak admits/s | 2K | 20K | 200K | 2M |
| Peak output tokens/s | 200K | 2M | 20M | 200M |
| Avg prompt tokens | 2K | 2–4K | 2–4K | 2–8K |
| Avg output tokens | 400 | 400–800 | 400–800 | 400–1K |
| Sessions stored | 50M | 500M | 5B | retention-capped |
| Safety QPS | ~admit×k | ×10 | ×100 | fleet cells |
| GPU (primary) | 256 | 2.5K | 25K | 250K class |

**What each jump forces:**

- **10×:** Dedicated stream gateways; continuous batching mandatory; Redis quotas; safety horizontal.  
- **100×:** User/session home cells; multi-model pools; semantic cache; regional inference.  
- **1,000×:** Edge PoPs; aggressive admission; distillation fallbacks; hard retention; capacity markets.

### 1.5 Etc. (Constraints & Assumptions)

- We consume an **Inference Engine** (vLLM-like / in-house) exposing generate/stream; we design **product serving** around it.  
- **Hidden system/safety layers** are platform-owned.  
- GPUs are the scarce resource — **admission control is the product**.  
- Prefer **streaming** UX; batch-only is fallback mode.

**Scope statement to repeat back:**

> Design an LLM answering system for user requests: authenticated streaming chat with durable sessions, prompt assembly, safety classifiers, continuous-batching inference with KV-cache, capacity admission, cost metering, and explicit fallbacks (smaller model, cached answers, bounded queue)—scaled through regional cells at 10× / 100× / 1,000×. Training out of scope.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Admit / turn create** | TX + quota | ~2K/s | ~20K/s | API + DB |
| **Safety classify** | In/out | ~4–12K/s | ×10 | CPU/GPU small |
| **Prefill** | Prompt ingest | bursts | ×10 | GPU compute |
| **Decode** | Token gen | ~200K tok/s | ~2M | GPU memory bw |
| **SSE frames** | Client stream | ~20–50K/s | ×10 | Gateway |
| **KV-cache memory** | Concurrent ctx | GPU HBM | ×10 | Serving |
| **Session reads/writes** | History | ~5–10K/s | ×10 | DB/cache |
| **Metering** | Usage events | ~admit rate | ×10 | Bus |

**Anti-pattern:** one “QPS” for admits, tokens, and SSE events.

### 2.2 Token & GPU sketch

```text
Peak output 200K tok/s
If one GPU decodes ~4K tok/s effective at batch (order-of; depends model)
GPUs_decode ≈ 200K / 4K ≈ 50 GPUs busy decode — plus prefill overhead
Real fleets larger: fragmentation, TTFT SLOs, multi-model, headroom (~2–4×)
Baseline 256 GPUs plausible for mixed load + headroom interview number

Concurrent streams 20K
Avg KV per stream: 2K tokens × 2 bytes × layers×heads factor
  Rough: 2K tok × 256 KB / 1K tok ≈ 512 MB? (model-dependent — state formula)
Interview move: "KV scales with concurrent × context × model; batching densifies GPU"
If KV budget per GPU 40 GB for cache → streams_per_GPU ≈ 40GB / kv_per_stream
Admission must track KV, not only request count
```

### 2.3 Continuous batching win

```text
Without batching: 1 req/GPU low util
With continuous batching: many seqs share decode steps → ↑ tok/s / GPU
Tradeoff: higher p99 TTFT if over-batch; need separate prefill/decode policies
```

### 2.4 Safety amplification

```text
Per turn: 1 input + N output chunk checks + 1 final
N=4 → ~6 × admit_rate classifier calls
At 2K admits/s → ~12K classify/s — size fleet from this
```

### 2.5 Cache savings

```text
Exact cache hit rate H_exact on FAQs
Semantic cache H_sem with similarity threshold
GPU save ≈ (H_exact + H_sem) × cost_per_answer
Risk: stale/wrong; safety must still run on cached answers (or cache post-safety)
```

### 2.6 Storage

```text
Message ~2 KB avg; 10 turns / session avg active
50M sessions × 10 × 2 KB = 1 TB raw order
+ indexes/replicas → multi-TB; retention mandatory at 100×
```

---

## 3. High-Level Design

### 3.1 APIs

| API | Semantics |
|-----|-----------|
| `POST /v1/sessions` | Create conversation |
| `POST /v1/sessions/{id}/turns` | User message; returns stream URL / SSE body; Idempotency-Key |
| `POST /v1/chat/completions` | OpenAI-style; stream=true | 
| `GET /v1/sessions/{id}` | History |
| `POST /v1/turns/{id}/cancel` | Stop generation |
| `GET /v1/usage` | Quotas / budgets |

**Turn request (logical):**

```text
{
  "input": {"role":"user","content":"..."},
  "model_tier": "auto|primary|small",
  "max_output_tokens": 1024,
  "metadata": {"client_req_id": "..."}
}
```

### 3.2 Domain model

```text
User / Project (auth, tier, budget)
Session(session_id, user_id, home_region, created_at)
Message(message_id, session_id, role, content, token_counts, safety_outcome)
Turn(turn_id, session_id, state, model_version, idempotency_key)
Run(run_id, turn_id, router_decision, fallback_reason?)
UsageEvent(turn_id, input_tokens, output_tokens, $estimate)
SafetyVerdict(subject_id, stage, labels, action)
KVCacheAffinity(optional session→worker hint)
```

**Turn state machine:** `CREATED → ADMITTED → GENERATING → COMPLETED|REFUSED|CANCELLED|FAILED`.

### 3.3 Gateway & auth

```text
Edge → API Gateway: TLS, WAF, authn (session cookie / API key), authz (session ownership),
rate limit, Idempotency-Key, request size caps → Orchestrator
```

### 3.4 Prompt assembly

```text
prompt = concat(
  platform_system_layer,
  safety_policy_layer,
  developer_instructions?,   // if API product
  conversation_window(messages, token_budget),
  user_message
)
```

**Truncation policy:** keep system/safety + latest turns; optional summary message for older (disclose in product).

### 3.5 Inference serving options

| Approach | Pros | Cons | Use |
|----------|------|------|-----|
| One req / GPU sync | Simple | Tiny util | Toy |
| **Continuous batching** | High util | Complexity; noisy neighbor | **MVP** |
| Separate prefill/decode pools | Tune TTFT vs tok/s | Ops | 10×+ |
| Speculative decoding | Faster tokens | Extra draft model | Phase 1.5 |

**Chosen:** Inference gateway → model pools with **continuous batching** and **paged KV-cache** (vLLM-style concepts).

### 3.6 KV-cache

| Topic | Stance |
|-------|--------|
| What | Cached keys/values per layer for attention; reuse across decode steps |
| Prefix cache | Reuse shared system/prompt prefixes across requests |
| Session affinity | Soft sticky to worker to reuse prefix KV — not correctness SoT |
| Eviction | LRU on GPU; admission refuses if can't fit |
| Multi-LoRA | Capacity packing constraints |

**Deal-breaker:** ignoring KV memory in admission (“just QPS limit”).

### 3.7 Safety placement

| Stage | When | Action |
|-------|------|--------|
| Input | Pre-admit / pre-inference | Block/refuse/allow |
| Output chunk | During stream | Buffer N tokens; redact/stop |
| Final | On complete | Label; audit |

**Fail closed** for violence/self-harm/etc. categories when classifiers down; soft categories degrade carefully.

### 3.8 Capacity admission & fallbacks

```text
Admission inputs: GPU KV free, queue wait ETA, user tier, cost budget, abuse score
Decisions:
  1) admit primary
  2) admit small model
  3) exact/semantic cache serve
  4) bounded queue (deadline 5–30s)
  5) 503 Retry-After
Never: unbounded queue; never silent quality lie without notice flag
```

### 3.9 State stores

| Store | Role |
|-------|------|
| Postgres (cells) | Sessions, messages, turns SoT |
| Redis | Quotas, idempotency, optional stream checkpoints |
| Object store | Large attachments Phase 1.5 |
| Kafka | Usage, safety audit, analytics |
| Cache (Redis/CDN) | Exact answer cache; semantic vector DB optional |

### 3.10 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Serving | Continuous batching | $/GPU | 1:1 sync GPUs |
| Admission | KV-aware | Prevent OOM meltdown | Count-only limits |
| State | Durable turn first | No lost user text | Stream-only ephemerality |
| Safety | Pre + stream + post | Risk coverage | Output-only |
| Fallback | Explicit ladder | UX honesty | Infinite wait |
| Cache | Post-safety preferred | Don't serve unsafe | Cache raw model junk |
| Multi-region | Home cell sessions | Consistency | Multi-primary writes |
| Cost | Reserve/settle tokens | Abuse control | Unlimited free |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
  Clients (App / API)
           |
           v
  +---------------------+
  | Edge / API Gateway  | auth, RL, WAF
  +----------+----------+
             v
  +---------------------+     +------------------+
  | Chat Orchestrator   |---->| Session DB       |
  | prompt, turn FSM    |     | (home cell)      |
  +---+----+----+-------+     +------------------+
      |    |    |
      |    |    +-------------+
      |    v                  v
      |  +-----------+   +-------------+
      |  | Safety    |   | Quota /     |
      |  | Classifiers|   | Admission   |
      |  +-----------+   +------+------+
      |                         |
      v                         v
  +---------------------+   fallback ladder
  | Model Router        |
  +----------+----------+
             v
  +---------------------+     +------------------+
  | Inference Gateway   |---->| Exact/Semantic   |
  | continuous batching |     | Answer Cache     |
  | KV-cache pools      |     +------------------+
  +----------+----------+
             |
      +------+------+
      v             v
  [Primary GPUs] [Small/fallback GPUs]
             |
             v stream tokens
  +---------------------+
  | Stream Gateway/SSE  |  (+ output safety taps)
  +---------------------+
```

### 4.2 Critical path: healthy stream

```text
Client → Gateway → Orchestrator
  TX: persist user msg + turn CREATED (Idempotency-Key)
  → reserve quota
  → input safety allow
  → admit primary (KV OK)
  → assemble prompt
  → Inference stream tokens
  → output safety taps
  → SSE to client
  → finalize message + settle usage
```

### 4.3 Critical path: overload fallback

```text
Admission: primary KV pressure high
  → try small pool
  → else semantic cache (if hit & allowed)
  → else queue with deadline + position
  → else 503 Retry-After
Client event: notice.degraded_model | notice.queued
```

### 4.4 Cancel / disconnect

```text
Client cancel → Orchestrator → Inference abort
  → turn CANCELLED; partial text policy (keep/discard)
  → settle actual tokens
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **User input durable before tokens are product-committed.**  
2. **Idempotency-Key ⇒ ≤1 turn side effect.**  
3. **Model version frozen at admit.**  
4. **Quota reserve TTL + settle by turn_id.**  
5. **Safety refuse is a completed terminal** with audit.  
6. **Fail closed** on critical safety outages.  
7. **Fallback notices** when quality tier changes.  
8. **Home-cell single-writer** for session mutations.  
9. **Max tokens / cost ceiling** enforced.  
10. **Cancel is CAS-terminal** vs complete.

#### 5.1.2 Streaming ownership

| Option | Behavior | MVP |
|--------|----------|-----|
| **A** | Client reconnect → new turn / retry; partial saved | **Yes** |
| **B** | Event log resume `after_seq` | Phase 2 |

Don't over-promise B while building A.

#### 5.1.3 Safety reliability

- Classifiers versioned; shadow eval.  
- Stream policy: buffer 20–50 tokens before flush for categories needing it; latency tradeoff.  
- Jailbreak signals → stricter policy / human review queues offline.  
- Cached answers: store **safety-approved** outputs only.

#### 5.1.4 Inference failure modes

| Failure | Behavior |
|---------|----------|
| Worker crash mid-stream | Mark FAILED/incomplete; retry once on small; reconcile quota |
| KV fragmentation | Defrag/evict; refuse large contexts first |
| Hotspot sticky | Shed affinity; rebuild prefix cache elsewhere |
| Thundering herd retry | Jitter; Idempotency-Key; Retry-After |

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | GPU OOM | KV admission |
| 10× | Stream gateway RAM | Dedicated tier; batch SSE |
| 100× | Session DB writes | Cells; async title/search |
| 1,000× | Global capacity shock | Regional shed; caches; smaller defaults |

### 5.2 Scalability

#### 5.2.1 Continuous batching

```text
Scheduler loop:
  pull admitted seqs
  pack prefill chunks into batch (chunked prefill)
  run decode step for all active seqs
  emit tokens; free finished seqs
Goals: maximize tok/s under TTFT/p99 constraints
```

**Fairness:** per-tier token budgets inside scheduler; prevent whale sessions starving others.

#### 5.2.2 Prefill vs decode

| Phase | Bottleneck | Scale tactic |
|-------|------------|--------------|
| Prefill | Compute | Chunked prefill; separate pool |
| Decode | Memory bandwidth / KV | Batch many short decodes |

Pin long-context whales carefully — they fragment batches.

#### 5.2.3 KV-cache & prefix caching

```text
Shared system prompt prefix → cached once per worker
Session follow-ups → soft sticky routing to reuse
Hash(prefix tokens) → prefix cache lookup
Evict least valuable under pressure (large unique > shared)
```

#### 5.2.4 Admission control math

```text
reject if:
  queue_eta > sla_max(tier) OR
  kv_free < kv_needed(prompt,max_out) OR
  user_budget_remaining < estimate OR
  concurrent_user_streams > cap
```

Priority ≈ f(paid_tier, latency_class, abuse_score, age_in_queue).

#### 5.2.5 Caching ladder

| Cache | Key | Risk |
|-------|-----|------|
| Exact | hash(model, prompt, params) | Low if includes safety context |
| Semantic | embedding ANN | Wrong answer; threshold high; domain-limited |
| Prompt prefix KV | token prefix | Memory; staleness of weights version |

Invalidate caches on **model_version** bump.

#### 5.2.6 Multi-region

```text
Edge active-active
Session home region = hash(user_id) or sticky create
Inference: prefer home; overflow to peer region if capacity + privacy OK
State: single-writer home; cross-region read-only replicas eventual
```

#### 5.2.7 Progressive scale

| Jump | Change |
|------|--------|
| →10× | Stream GW; Redis quotas; safety scale; batching tune |
| →100× | Cells; semantic cache; prefill/decode split; regional pools |
| →1,000× | Edge; capacity markets; aggressive small-model default; retention |

#### 5.2.8 Cost control

- Smaller model default for simple intents (classifier router).  
- Max output tokens by tier.  
- Cache FAQs.  
- Speculative decoding when ROI clear.  
- Spot/preemptible for batch non-interactive (out of chat MVP).  
- Chargeback: $/1K tokens; budget alerts.

### 5.3 Maintainability

#### 5.3.1 Orchestrator as state machine

Testable transitions; no hidden side effects outside outbox.

#### 5.3.2 Prompt/safety versioning

```text
safety_layer_version, system_layer_version stored on Turn
Rollback = point router to prior versions; don't mutate history
```

#### 5.3.3 Observability

```text
ttft, tps, admit_reject_reason, fallback_rate,
safety_refuse_rate, kv_utilization, batch_size,
queue_eta, cache_hit, finalize_lag, cancel_rate,
$/turn, model_version mix
```

No per-user_id Prometheus labels.

#### 5.3.4 Testing

- Idempotent turn create.  
- Cancel vs complete race (CAS).  
- Classifier timeout fail-closed.  
- Admission under synthetic KV pressure.  
- Cache authz (no cross-tenant hit).  
- Load test continuous batching fairness.

#### 5.3.5 Operability

- Drain worker: stop admits; finish seqs; handoff.  
- Model rollout: canary %; shadow traffic.  
- Kill switch: force small model globally.  
- Chaos: safety down; assert refuse path.

#### 5.3.6 Safe evolution

Phase 1: single primary + small fallback, Option A stream, input+final safety.  
Phase 2: chunk safety, prefix KV cache, exact answer cache.  
Phase 3: cells, semantic cache limited domains, Option B resume.  
Phase 4: tools/agents hooks with sandbox.

---

## 6. Wrap-Up

### 6.1 What we designed

An **LLM answering** serving system: durable streamed turns, prompt assembly with platform safety layers, classifier pipeline, **KV-aware admission**, continuous-batching inference, conversation state in home cells, metering/quotas, and an explicit **fallback ladder** (small model → cache → bounded queue → 503)—product focused, training out of scope.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Batching | Required for $/GPU |
| Admission | Track KV + queue ETA |
| Safety vs TTFT | Buffer policy explicit |
| Fallbacks | Visible; bounded |
| Cache | Versioned; safety-aware |
| State | Durable user input first |
| Multi-region | Home-cell writer |
| Streaming | Option A MVP honesty |

### 6.3 Closing line

> “Answering users with LLMs is an admission-controlled streaming product: protect GPUs with KV-aware batching, protect users with safety and durable turns, and degrade on a published ladder—not an unbounded queue in front of a magic model.”

---

## 7. Deeper / Related Interview Questions

### 7.1 API & product

**Q1: Chat completions vs sessions API?**  
A: Completions are stateless messages array; sessions persist server-side history. Support both; sessions reduce client trust bugs.

**Q2: Why Idempotency-Key?**  
A: Mobile retries / double-click must not double-charge tokens or duplicate assistant turns.

**Q3: How is Stop implemented?**  
A: Client calls cancel; orchestrator aborts inference; CAS terminal state.

**Q4: Regenerate?**  
A: New turn referencing parent message; don't erase history blindly—branch or replace per product.

### 7.2 Prompt assembly & memory

**Q5: How do you truncate?**  
A: Tokenize; reserve system/safety; keep newest turns; optional summary item.

**Q6: Sliding window vs summary?**  
A: Window simple/losy; summary saves tokens but can distort — disclose.

**Q7: Where do system prompts live?**  
A: Platform config versioned — not editable by end users in consumer mode.

**Q8: Long documents?**  
A: Retrieval stub Phase 1.5; don't shove 200K tokens blindly without model support.

### 7.3 KV-cache & serving

**Q9: What is paged KV?**  
A: Allocate KV in blocks to reduce fragmentation; enables higher concurrency.

**Q10: Prefix caching security?**  
A: Don't reuse across tenants; include tenant isolation in cache key namespace.

**Q11: Why sticky sessions to workers?**  
A: Performance for KV reuse only; correctness must work if sticky missed.

**Q12: Prefill-decode disaggregation?**  
A: At scale, specialized pools improve TTFT and util; adds network KV transfer complexity.

**Q13: Continuous batching vs static batching?**  
A: Continuous admits new seqs as others finish — much better for chat traffic.

**Q14: How does OOM present?**  
A: Admission failure or mid-run abort; prefer admit-time estimate.

### 7.4 Capacity & LB

**Q15: Load balance inference?**  
A: Least-KV-loaded / power-of-two; avoid pure RR with huge context variance.

**Q16: Consistent hashing users?**  
A: For session home cells and soft affinity; virtual nodes for drain.

**Q17: Herd on new model deploy?**  
A: Canary; rate limit shift; warm prefix caches; progressive traffic.

**Q18: What is a good queue?**  
A: Bounded, deadline, visible ETA; expire to 503; never infinite.

**Q19: Fairness algorithm?**  
A: Weighted fair queuing by tier; deficit counters for tok/s.

### 7.5 Safety

**Q20: Why input and output?**  
A: Input blocks disallowed asks; output catches model mistakes / jailbreaks.

**Q21: Streaming safety leakage?**  
A: Buffer or delayed classify; trade TTFT; category-specific.

**Q22: Fail open or closed?**  
A: Closed for high-risk; argue nuance for spam/soft.

**Q23: Prompt injection?**  
A: Separate trusted layers; delimiters; later tool argument checkers.

**Q24: Logging prompts?**  
A: Privacy controls; retention; access audit; redaction.

### 7.6 State & DB

**Q25: Postgres schema sketch?**  
A: sessions, messages (session_id, seq), turns unique(idempotency_key).

**Q26: Hot session writes?**  
A: Serialize turns per session (`FOR UPDATE` / occupancy lock).

**Q27: Read-your-writes?**  
A: Home region primary; edge cache invalidate on finalize.

**Q28: Search history?**  
A: Async indexer; not LIKE on primary at scale.

**Q29: Retention?**  
A: Tiered delete; export; legal hold exceptions.

### 7.7 Caching & hashing

**Q30: Exact cache key?**  
A: hash(model_version, temperature, system_hash, messages_hash, tools_hash).

**Q31: Semantic cache false positive?**  
A: High similarity threshold; restrict to FAQ domains; always show provenance optional.

**Q32: Bloom filter role?**  
A: Optional negative cache for “known non-FAQ”; not for safety decisions.

**Q33: Cache stampede?**  
A: Singleflight on key; probabilistic early expire.

### 7.8 Cost & metering

**Q34: Reserve/settle?**  
A: Reserve max_tokens × price; settle actual; release remainder; TTL cleanup.

**Q35: How to stop abuse?**  
A: RPM/TPM limits; anomaly; progressive challenges; isolate free pool.

**Q36: Cost of long context?**  
A: Prefill $ grows with prompt length — price and limit by tier.

**Q37: Why smaller model fallback saves more than queueing?**  
A: Queue still burns patience and often same GPU later; small model absorbs cheaply.

### 7.9 Multi-region & HA

**Q38: Active-active inference?**  
A: Yes for capacity; sessions still home-written.

**Q39: Data residency?**  
A: Pin home region; block overflow across sovereign borders.

**Q40: DR for sessions?**  
A: Async replicas; RPO minutes; in-flight turns incomplete.

**Q41: Edge SSE?**  
A: Terminate stream near user; orchestrator may be regional.

### 7.10 Algorithms

**Q42: Tokenization mismatch risk?**  
A: Same tokenizer for budget and model; off-by-one → OOM or truncation bugs.

**Q43: Approximate nearest neighbor for semantic cache?**  
A: HNSW/IVF; recall/latency tradeoff; version embeddings with model.

**Q44: Early exit / confidence?**  
A: Router classifier sends easy queries to small model — big $ lever.

**Q45: Backoff for 503?**  
A: Exponential + jitter; honor Retry-After.

### 7.11 Memory (process) concerns

**Q46: Gateway memory with 200K streams?**  
A: 200K × 50 KB ≈ 10 GB — need fleet; backpressure; proxy buffering limits.

**Q47: Orchestrator thread model?**  
A: Async evented; don't block on inference sockets in worker threads naively.

**Q48: Redis checkpoint size?**  
A: Bound partial text; Option A minimizes need.

### 7.12 10× / 100× / 1,000×

**Q49: First break at 10×?**  
A: TTFT under bad batching; safety fleet; Postgres turn writes.

**Q50: At 100×?**  
A: Need cells + regional capacity; cache; split prefill/decode.

**Q51: At 1,000×?**  
A: Default economics force small models + cache; hard admission; retention.

### 7.13 Deal-breakers checklist

**Q52: Name three deal-breakers.**  
A: (1) Unbounded GPU queues, (2) admission ignoring KV memory, (3) fail-open on critical safety outage / silent model downgrade without user-visible notice when quality matters.

### 7.14 Training boundary

**Q53: Where does finetune fit?**  
A: Offline pipeline publishes `model_version` artifacts to registry; serving only pulls versions — don't design training in this interview unless asked.

**Q54: Online learning from chats?**  
A: Separate consent-heavy pipeline; not in request path.

---

## Appendix A: Admission pseudocode

```text
function admit(turn, estimate):
  if !reserve_quota(turn.user, estimate): return Deny("budget")
  if safety_input(turn) == BLOCK: return Refuse(...)
  for pool in [primary, small]:
    if pool.kv_free >= estimate.kv && pool.queue_eta < sla(turn.tier):
       return Admit(pool)
  if cache = lookup_cache(turn): return ServeCache(cache)
  if turn.tier allows queue && eta < qdeadline:
       return Enqueue(eta)
  release_quota_reserve(turn)
  return Deny("capacity", retry_after=...)
```

## Appendix B: Turn row sketch

```text
turn_id | session_id | idempotency_key UNIQUE
| state | model_version | safety_layer_version
| fallback_reason NULLABLE | created_at | finalized_at
```

## Appendix C: Interview 45-minute plan

1. Scope serving≠training + requirements (6 min)  
2. Numbers: streams, tok/s, KV (6 min)  
3. Path: orchestrator, safety, router (8 min)  
4. Continuous batching + admission + fallbacks (10 min)  
5. State/multi-region/cost (7 min)  
6. Q&A  

---

*End of LLM answering user requests system design.*
