# System Design: Claude Chat Service

> **Focus areas:** Streaming responses · Conversation state · Context-window management · Model serving · Constitutional AI / safety · Multi-device sync  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split stream/durable/safety load classes, explicit GPU and context invariants, Anthropic-flavored harmlessness pipeline

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

Goal: **bound the product**—Claude as a **consumer / prosumer chat assistant** (durable multi-turn chats, streaming, context management, safety, sync), distinct from the **developer Messages API** and from raw inference serving.

### 1.0 Claude Chat vs Developer API (say this early)

| Dimension | **Claude Chat (this doc)** | **Developer Model API** (sibling) |
|-----------|----------------------------|-----------------------------------|
| Primary user | Consumers / knowledge workers | Developers / apps via API keys |
| Success metric | Helpful, harmless, sticky UX | Latency SLOs, quotas, billing accuracy |
| Auth | User accounts / OAuth / SSO | API keys, org projects |
| Conversation UX | First-class sidebar, sync, titles | Client-owned or optional |
| Safety surface | Productized Constitutional AI + classifiers | Policy + abuse; org-configurable modes |
| Context UX | Product compaction / Projects | Explicit `messages[]` + cache_control |
| Degradation | “Busy / lighter model” banners | 529 overloaded / queue headers |

**Scope statement:** Design Claude chat the product—not the public Messages API control plane.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who is the user? | Consumer + Pro/Team; free + paid tiers | Tiered quotas; product UX not API knobs |
| F2 | Core loop? | Multi-turn chat; edit→branch; regenerate; stop | Conversation + Turn/Run atomic create |
| F3 | Streaming? | Yes — tokens appear live (SSE) | Stream gateway; ownership Option A/B |
| F4 | Persistence? | Chats list; reopen; Projects; search | Durable conversations/items/turns |
| F5 | Models? | Claude Haiku / Sonnet / Opus (tiers) | Router + capacity; resolve version at admit |
| F6 | Context window? | Large windows (100K–200K+ class); long chats | Compaction, caching hooks, overflow policy |
| F7 | Safety? | Constitutional AI principles; classifiers; refusals | Pre/post/stream safety; harmlessness first |
| F8 | Artifacts / tools? | Artifacts, browsing, code stubs Phase 1–1.5 | Tool bus; sandbox egress |
| F9 | Auth / sync? | Logged-in; web + mobile multi-device | Home cell by `user_id`; sync APIs |
| F10 | Quotas? | Free caps; Pro higher; abuse limits | Reserve/settle; fairness under load |
| F11 | Attachments? | PDFs/images/files | Object store + multimodal parts |
| F12 | Prompt caching? | Product may reuse prefix internally | Cache-aware packing; not user-visible API |

**MVP functional scope (lock with interviewer):**

1. Authenticated chat: create conversation, send message, **stream** assistant reply.
2. **Atomic turn/run creation** (user input durable before inference).
3. Conversation list + history; edit → branch; regenerate; Stop.
4. **Model routing** across Haiku/Sonnet/Opus (auto or user pick); version frozen per turn.
5. **Safety**: Constitutional AI system layers + input/output/stream classifiers; refuse harmlessly.
6. **Context-window management**: token accounting, overflow → disclosed compaction / truncate policy.
7. Multi-device sync for conversation list + messages (eventual with conflict rules).
8. Tiered quotas; graceful degradation when GPU pools overload.

**Out of MVP (explicitly defer):**

- Full Team workspace admin / SSO complexity (hooks: `workspace_id`)
- Perfect seamless stream resume across all gateway failures (Option B Phase 2)
- Full Artifacts collaborative editing as a product
- Voice / realtime multimodal as primary
- Public developer API surface (sibling doc)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT? | Feels instant for Sonnet/Haiku | p50 < 500ms, p99 < 2s (excl. deep reasoning queue) |
| N2 | Streaming smoothness? | No multi-second stalls | Flush ≤ 50–100ms once tokens flow |
| N3 | Durability? | No lost ACK’d user messages | Input durable before stream; completed turn durable; partial RPO≈1s |
| N4 | Availability? | Consumer critical | 99.9% control plane; degrade to Haiku / queue |
| N5 | Safety vs latency? | Must not ship egregious harm | Streaming safety policy explicit |
| N6 | Multi-region? | Global users | Active-active edge; **home cell** single-writer per user |
| N7 | Privacy? | Chats sensitive | Encryption, IDOR-safe IDs, retention |
| N8 | Context correctness? | Never silently drop mid-turn critical instructions without policy | Explicit compaction markers |
| N9 | Sync lag? | Mobile reopen “recent” | List/metadata p99 < 1s; full history pageable |
| N10 | Cost efficiency? | GPU $ dominates | Prefix caching + batching where compatible with chat latency |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New chat → type → stream answer → title autogen → sidebar update on all devices.
2. Follow-up with full prior context (or cached prefix + delta).
3. Edit earlier user message → branch DAG; continue on new leaf.
4. Long Project chat approaches context limit → disclosed compaction → continue.
5. Model overloaded → router offers Haiku or “try again” with short queue.
6. Safety refusal → helpful refusal text; turn completes with `safety_outcome`.
7. Stop mid-stream → cancel inference lease; persist partial + `cancelled`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit | Idempotency-Key → one turn/run |
| Disconnect mid-stream | MVP Option A: partial + Retry; Option B: resume `after_sequence` |
| Stop vs tab close | Stop cancels; tab close: short grace then cancel (product policy) |
| Context overflow | Disclosed compact / summarize older turns; **never silent rewrite of user custom style prefs** |
| Free tier cap | Clear upgrade UX; no silent quality lie |
| Jailbreak / harmful ask | Constitutional + classifiers; refuse; log signals |
| Concurrent tabs | `expected_leaf_id` conflict → 409 |
| Degraded model swap | User-visible notice when Auto routes Haiku |
| Sync conflict (two devices) | Last-writer-wins on leaf with CAS; show conflict toast if needed |
| Attachment too large | Reject before admit; don’t burn GPU |
| Safety classifier brownout | Fail closed on high-severity categories |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 20M | 200M | — | extreme global |
| DAU | 5M | 50M | 500M | multi-B class |
| Peak concurrent streams | 100K | 1M | 10M | 100M |
| Turns / day | 80M | 800M | 8B | 80B |
| Avg tokens in+out / turn | ~3K | ~3K | 3–6K | 3–6K |
| Peak **output** tokens/s | ~1M | ~10M | ~100M | ~1B |
| Peak **prefill** tokens/s | ~4M | ~40M | ~400M | ~4B |
| Conversations stored | ~2B | ~20B | ~200B | retention-capped |
| Items stored (order) | ~20B | ~200B | ~2T | retention-capped |
| Read QPS (list/open) | ~30K | ~300K | ~3M | ~30M |
| Postgres durable writes peak | ~3–15K | ~30–150K | cells | many cells |
| Redis checkpoint ops peak | ~30–150K | ~0.3–1.5M | ~3–15M | regional fleets |
| Stream events/s (batch ~20 tok) | ~50K | ~500K | ~5M | ~50M |
| Safety classifier QPS | ~turn×6 | ×10 | ×100 | dedicated platform |

**What each jump forces:**

- **10×:** Dedicated stream gateways; Redis checkpoints; multi-model GPU pools; safety fleet; prompt-cache aware packing.
- **100×:** User home cells; regional inference; cold conversation tiering; fair admission by tier; context compaction service.
- **1,000×:** Global edge; Option B replay; safety/compaction as platforms; aggressive retention; cross-region sync carefully scoped.

### 1.5 Etc. (Constraints & Assumptions)

- Claude Chat is a **client of Inference Gateway**—not training.
- **Constitutional AI / hidden system+safety layers** are platform-owned.
- Distinguish platform layers from **user-authored** custom preferences (no silent rewrite).
- Web + iOS/Android; sync via APIs + optional push.
- Developer Messages API **out of scope** (sibling).

**Scope statement to repeat back:**

> Design Claude chat: durable multi-turn conversations with atomic streamed turns, Haiku/Sonnet/Opus routing, Constitutional AI + classifier safety, context-window management with disclosed compaction, multi-device sync, tiered quotas, and graceful GPU degradation—scaling through 10× / 100× / 1,000× with user home cells. Distinct from the public developer API.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Durable turn creates** | TX: items + run | ~3–15K/s | ~30–150K/s | Postgres cells |
| **Redis checkpoints** | Partial tokens ~1s | ~30–150K/s | ~0.3–1.5M/s | Redis |
| **Stream frames to clients** | SSE events | ~50K/s | ~500K/s | Gateway |
| **Safety classifier QPS** | Input/chunk/final | ~turns×6 | ×10 | Safety fleet |
| **Context assemble / tokenize** | Prefill prep | ~turn rate | ×10 | Context service |
| **Prompt-cache lookups** | Prefix hash | ~turn rate | ×10 | Cache index |
| **Quota checks** | Reserve/settle | ~turn rate | ×10 | Redis limiter |
| **Sync fanout** | Device notify | fraction of writes | ×10 | Push / poll |
| **Analytics/Kafka** | Usage/safety | ~turn rate | ×10 | Bus |

**Anti-pattern:** one blended “chat QPS” mixing Postgres, Redis, SSE, GPU prefill, and classifiers.

### 2.2 Token / GPU math

```text
Baseline peak concurrent streams ≈ 100K
Avg output rate ≈ 30–50 tok/s/stream when actively decoding
Not all streams decode at once (queue, tools, thinking) → effective decode concurrency < peak streams

Interview-friendly peak output tokens/s ≈ 1M
If GPU decode throughput ≈ 5K tok/s/GPU (order; model-dependent)
Decode GPUs ≈ 1M / 5K = 200 GPUs (decode-bound estimate only)

Prefill often dominates cost for long-context Claude chats:
Peak prefill tokens/s ≈ 4M
If prefill ≈ 20K tok/s/GPU → 4M / 20K = 200 prefill-equivalent GPUs
Plus KV-cache memory: long contexts → fewer concurrent sequences per GPU

Total inference fleet >> decode-only math. Say so in the interview.
```

### 2.3 Context storage & working set

```text
Item ~2–4 KB avg (text); multimodal larger
20B items × 3 KB ≈ 60 TB raw baseline
+ indexes/replicas → hundreds of TB
Projects with large attachments → object store primary; DB stores refs

Active context assembly:
100K concurrent × avg 20K tokens × 2 bytes/token (rough) ≈ 4 TB tokenized working set
→ Must not keep full tokenized contexts only in BFF RAM; use context service + cache
```

### 2.4 Prompt caching economics (product-internal)

```text
If 40% of turns share long system+project prefix:
Cached prefill cost ≈ 0.1× uncached (illustrative)
Effective prefill GPU demand ≈ 0.6×U + 0.4×0.1×U = 0.64U
→ ~36% prefill GPU savings — material at 100×
```

### 2.5 Safety amplification

```text
Per turn: 1 input + N chunk output + 1 final ≈ 1+N+1 classifiers
N=4 → ~6 × turn_admit_QPS
Size safety fleet from admit rate, not DAU.
```

### 2.6 Sync / multi-device

```text
Writes that need sync: turn create, complete, title, delete, branch
Baseline write-notify ≈ 10K/s
Devices/user ≈ 2 → fanout 20K notify/s (or poll)
At 100×: prefer cell-local change feeds + push, not global chat fanout bus
```

### 2.7 Cost implications (order)

```text
GPU $ dominates COGS. Rough:
If blended cost ≈ $0.003 / turn (illustrative blended Haiku/Sonnet)
80M turns/day × $0.003 ≈ $240K/day ≈ $7.2M/month inference-ish
Free-tier abuse and long-context Opus without caps → bankrupt the unit economics
→ Quotas + model routing + caching are product features, not ops afterthoughts
```

---

## 3. High-Level Design

### 3.1 Product / UX wireframe

```text
+----------------------------------------------------------------------+
| Claude            [Sonnet ▾]  [Projects]         [Upgrade]  [User]   |
+---------------+------------------------------------------------------+
| Recents       |  Conversation title                                  |
| Today         |                                                      |
|  Kyoto trip   |  User: Plan a 3-day trip...                          |
|  SQL help     |                                                      |
|  * New chat   |  Claude: Here's a balanced itinerary...              |
|               |  ▍ (streaming)                                       |
| Projects      |                                                      |
|  Research     |  [ Message Claude...                  ] [Stop][Send] |
+---------------+------------------------------------------------------+
| Notice: "Using Haiku due to high demand" / "Context compacted"       |
+----------------------------------------------------------------------+
```

**Client state machine:**

```text
Idle → CreatingTurn → Streaming → Idle
                    ↘ Incomplete (Retry)
                    ↘ Refused / Failed / Cancelled
```

### 3.2 Domain model

```text
User / Tier / Devices[]
  └── Conversation | Project
        ├── Item[]  (DAG: user/assistant/tool_*/compaction_summary)
        └── Turn / Run
              ├── input refs + expected_leaf_id
              ├── routing (requested → resolved model_version)
              ├── constitutional_layers_ref (platform; not user-editable)
              ├── user_preferences_ref (user-visible; no silent edit)
              ├── context_plan (full | cached_prefix+delta | compacted)
              ├── status + termination_reason
              ├── safety_outcome
              ├── usage + quota settlement
              └── metrics (TTFT, queue_wait, cache_hit, degradations)
```

**Atomic turn/run create (preferred):**

Single TX: user item(s) + run + output placeholder + idempotency + outbox.  
**Invariant:** no orphan user message without a run on the normal send path.

**Run state machine:**

```text
created → admitted → queued → in_progress
                              ├→ completed
                              ├→ incomplete
                              ├→ failed
                              ├→ cancelled
                              └→ refused (safety)
```

CAS single terminal transition.

### 3.3 Constitutional layers vs user content

| Layer | User-editable? | Shown in UI? | May change without user edit? |
|-------|----------------|--------------|-------------------------------|
| User message | yes | yes | **No silent rewrite** |
| User style / prefs | yes | settings | **No silent rewrite** |
| Constitutional / system | no | generally no | Yes (platform) |
| Safety classifiers | no | via refusals | Yes (platform) |
| Context compaction | policy | **disclose** | Yes, with marker item |

**Interview line:**

> We apply Constitutional AI and safety classifiers as platform layers. We do **not** silently mutate user-authored text. Compaction is allowed with disclosure and a persisted summary item.

### 3.4 API shape (product BFF)

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `/api/conversations` | List / create |
| GET | `/api/conversations/{id}/items` | History page |
| **POST** | **`/api/conversations/{id}/turns`** | **Atomic create-and-stream** |
| GET | `/api/turns/{id}` | Status + output |
| GET | `/api/turns/{id}/events?after=` | Resume (Option B) |
| POST | `/api/turns/{id}/cancel` | Stop |
| POST | `/api/turns/{id}/regenerate` | New turn same leaf |
| GET | `/api/sync/changes?since=` | Multi-device sync cursor |
| POST | `/api/devices` | Register device for push |

```http
POST /api/conversations/{id}/turns
Idempotency-Key: ...
{
  "expected_leaf_id": "item_...",
  "input": [{"role":"user","content":[{"type":"text","text":"..."}]}],
  "model_tier": "auto",
  "stream": true
}
```

### 3.5 Streaming ownership: Option A vs B

| | **Option A — Coupled BFF (MVP)** | **Option B — Run Service + replay** |
|---|----------------------------------|-------------------------------------|
| Who holds stream | BFF/stream GW tied to request | Run worker + event buffer |
| BFF death | Turn → incomplete; Retry | Client reconnects `after_sequence` |
| Complexity | Lower | Higher |
| Resume SLO | Honest: no seamless | Strong resume |

**Choice:** MVP **Option A** + Redis partial checkpoints; Phase-2 **Option B** if resume is a hard product promise.

### 3.6 Context-window management

```text
Assemble plan:
  1. Load leaf path items (DAG walk)
  2. Apply retention/compaction summaries already persisted
  3. Tokenize + count against model context_limit - reserve_output
  4. If overflow: compact oldest → insert compaction_summary item (disclosed)
  5. Build prompt: constitutional + prefs + messages (+ cache breakpoints)
  6. Hand to Inference GW with cache_key hints
```

| Strategy | Pros | Cons | Deal-breaker |
|----------|------|------|--------------|
| Hard truncate oldest | Simple | Loses critical early constraints | Silent loss of user rules |
| Sliding window only | Predictable | Weak for Projects | Same |
| **Disclosed compaction (chosen)** | Preserves gist | Summary errors | Must mark in transcript |
| Always full context | Best fidelity | Cost + OOM | Fails at 100× long chats |

**Invariants:**

- Token accounting before admit; reject/compact before GPU start.  
- Compaction creates an explicit item; UI can show “earlier messages summarized.”  
- Never drop the latest user message to “make room.”

### 3.7 Model routing (Haiku / Sonnet / Opus)

```text
Router inputs:
  user tier, preference (auto|haiku|sonnet|opus),
  features (tools, images, length), safety mode,
  capacity signals, latency SLO, cost budget

Router outputs:
  resolved model_version, max_tokens, degradation flags, priority
```

| Strategy | Pros | Cons |
|----------|------|------|
| User picks only | Transparent | Bad overload UX |
| Auto only | Smooth | Trust |
| **Auto + override (chosen)** | Balance | More states |
| Cascade fallback | Availability | Must notify |

**Deal-breaker:** answering with Haiku while UI still says “Opus” with no notice.

### 3.8 Safety pipeline (Constitutional AI + classifiers)

```text
User input
  → input classifiers / policy (block | refuse | allow)
  → assemble (constitutional layers + user items + tools)
  → model stream
  → chunk classifiers (lag buffer) → continue | truncate+refuse
  → final classifiers → persist safety_outcome
```

| Approach | UX | Risk |
|----------|----|------|
| Fully buffer | Safer | Slow |
| **Lag buffer N tokens (chosen)** | Balance | Residual risk |
| Raw stream + post-hoc | Fast | May flash harm |

**Anthropic flavor:** prefer helpful *refusals* (explain limits, offer safe alternative) over terse blocks where policy allows. Highest-severity categories fail closed.

### 3.9 Multi-device synchronization

```text
Device A writes turn → home-cell commit → change_log(user_id, cursor)
Device B: push wake OR poll GET /sync/changes?since=cursor
  → fetch conversation/item deltas → merge local cache
```

| Approach | Pros | Cons | Deal-breaker |
|----------|------|------|--------------|
| Last-write-wins only | Simple | Edit races | Silent branch loss |
| **CAS leaf + 409 (chosen)** | Safe branching | Client must handle | Ignoring 409 |
| CRDT full text | Fancy | Overkill for chat DAG | Complexity |

**Home cell:** all durable writes for a user go to one cell; other regions proxy or redirect.

### 3.10 Quotas, abuse, degradation

| Dimension | Free | Pro |
|-----------|------|-----|
| Messages / windows | Tight | Higher |
| Sonnet / Opus access | Limited | Priority |
| Concurrent streams | 1–2 | more |
| Long-context turns | Capped | Higher |
| Attachments | Small | Larger |

| Signal | Action |
|--------|--------|
| Opus/Sonnet saturation | Auto → Haiku + banner |
| Regional outage | Reroute or short deadline queue |
| Safety brownout | Fail closed high-severity |
| Checkpoint Redis down | Finalize-only; weaker resume |

**Never:** unbounded interactive queues that pin GPUs forever.

### 3.11 Component trade-offs

| Component | Options | Choice | Deal-breaker if wrong |
|-----------|---------|--------|----------------------|
| Conversation DB | Postgres vs Cassandra | **Postgres cells** MVP | Global single PG primary |
| Stream | SSE vs WS | **SSE/fetch** for turns | WS-only on flaky mobile without fallback |
| Checkpoints | Redis vs DB | **Redis** + PG finalize | Checkpoint in PG every token |
| Context | BFF assemble vs service | **Context service** at 10× | Multi-MB prompts in BFF heap |
| Sync | Poll vs push+poll | **Push + cursor poll** | Global pubsub all chats |
| Cache | None vs prefix cache | **Prefix cache hooks** | Ignoring cache at long-context scale |

**Alternatives considered:**

- Store full transcripts only in object storage → poor list/search latency.  
- Client-side-only history → breaks multi-device and safety audit.  
- One global Redis for all checkpoints → hot keys / blast radius at 100×.

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +------------------+     +--------------------+
| Web/Mobile  |---->| Edge / BFF /     |---->| Chat API           |
|  devices    |     | Stream Gateway   |     | (turns, sync)      |
+-------------+     +--------+---------+     +---------+----------+
                             |                         |
                             | SSE                     v
                             |                +--------+----------+
                             |                | Conversation Svc  |
                             |                | (home cell PG)    |
                             |                +--------+----------+
                             |                         |
                             v                         v
                    +----------------+        +--------+----------+
                    | Turn / Run     |<------>| Redis: quotas,    |
                    | Orchestrator   |        | checkpoints, sync |
                    +--------+-------+        +-------------------+
                             |
     +-----------+-----------+-----------+--------------+
     v           v           v           v              v
+----------+ +--------+ +----------+ +-----------+ +-----------+
| Model    | | Safety | | Context  | | Tool Bus  | | Inference |
| Router   | | Fleet  | | + Cache  | | (optional)| | Gateway   |
+----------+ +--------+ +----------+ +-----------+ +-----+-----+
                                                           |
                                                     +-----v-----+
                                                     | GPU pools |
                                                     | H/S/O     |
                                                     +-----------+
```

### 4.2 Request lifecycle (create + stream)

```text
Client                BFF/Stream GW         Chat API / Conv         Orchestrator         Inference
  |                        |                      |                      |                    |
  | POST /turns            |                      |                      |                    |
  |----------------------->|                      |                      |                    |
  |                        | atomic create        |                      |                    |
  |                        |--------------------->|                      |                    |
  |                        |  run_id + ack        |                      |                    |
  |                        |<---------------------|                      |                    |
  |                        | dispatch             |                      |                    |
  |                        |-------------------------------------------->|                    |
  |                        |                      |   safety+context     |                    |
  |                        |                      |   reserve quota      |                    |
  |                        |                      |   route model        |                    |
  |                        |                      |--------------------->|                    |
  |                        |                      |                      |  prefill+decode    |
  |  SSE token events      |<--------------------------------------------|<-------------------|
  |<-----------------------|  checkpoint Redis ~1s                       |                    |
  |                        |                      |  finalize PG         |                    |
  |  SSE done              |                      |  settle quota        |                    |
  |<-----------------------|                      |  sync cursor bump    |                    |
```

### 4.3 Multi-device sync data flow

```text
Device A --write--> Home Cell PG --append--> change_log(user, cursor)
                         |
                         +--> Push notifier --> Device B wake
Device B --GET /sync?since=cursor--> apply deltas --> local SQLite/Room cache
Conflict: CAS on expected_leaf_id; loser refreshes and retries / branches
```

### 4.4 Context + cache path

```text
Items (PG) → Context Service → tokenize/count → compact if needed
                              → build prompt with cache breakpoints
                              → Inference GW (prefix cache hit/miss metrics)
                              → decode stream → Orchestrator → client
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Data-loss prevention

| Asset | Durability strategy |
|-------|---------------------|
| User message | Durable in TX before SSE starts |
| Partial assistant | Redis checkpoint ~1s; promote on complete |
| Completed turn | Postgres + CAS terminal state |
| Sync cursor | Monotonic per user in home cell |
| Safety outcome | Stored with turn; immutable after terminal |

**Invariant:** ACK to client for “message sent” ⇒ row exists with run. Client may retry with same Idempotency-Key.

#### 5.1.2 Retries & idempotency

- Client: Idempotency-Key on POST `/turns` (UUID).  
- Server: keyed by `(user_id, key)` → same `run_id`.  
- Inference: `run_id` as generation idempotency; cancel on duplicate workers via lease.  
- Settle quota: idempotent by `run_id`.

#### 5.1.3 Rate limiting & abuse

| Layer | Mechanism |
|-------|-----------|
| Edge | IP / device burst limits |
| Account | Tier RPM + daily messages + concurrent streams |
| Model | Per-tier fair share into GPU queues |
| Safety | Escalating friction on jailbreak signals |
| Attachments | Size/type/virus scan before admit |

Limiter errors on free tier: **fail closed**. Pro: static ceiling fail-open only with hard cap (interview discussion).

#### 5.1.4 Cancellation & Stop

```text
Stop → cancel flag on run → Inference GW abort lease → persist partial + cancelled
Tab close → grace period T (e.g. 5–15s) then same as cancel (MVP)
```

GPU workers must heartbeat leases; orphan generations abort to free KV memory.

#### 5.1.5 Streaming safety reliability

- Lag buffer of N tokens before flush to client.  
- On classifier “block”: truncate stream, emit refusal continuation or stop with `refused`.  
- Classifier timeout: policy by severity — high-severity fail closed; low-severity may fail open with logging (make explicit).

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Scale | Control plane | Data | Inference | Sync |
|-------|---------------|------|-----------|------|
| Baseline | Regional BFF + API | Single-region PG primary + replicas | Regional GPU pools H/S/O | Poll + light push |
| **10×** | Stream GW fleet; orchestrator workers | PG vertical + read replicas; Redis cluster | Separate prefill/decode pools; cache | Push mandatory |
| **100×** | Cell routing by user | **Home cells**; cold object tier for old chats | Multi-region GPU; admission control | Cell-local change feeds |
| **1,000×** | Global edge anycast | Many cells; retention caps | Capacity markets / priority classes | Cross-region read replicas of metadata only |

#### 5.2.2 Traffic ups and downs

- Autoscale stream GW on concurrent connections + event rate.  
- GPU scale slower — use **admission control** and model downgrade before thrashing KV cache.  
- Daily peaks: reserve Pro capacity pools; free tier absorbs elasticity first.

#### 5.2.3 Storage parallelization

```text
Hot conversations: PG row + recent items
Warm: PG + cached item pages
Cold: object segments (conversation packs) + manifest; hydrate on open
Search index: async (Phase 1.5)
```

#### 5.2.4 Context & GPU parallelization

- Prefill batching only when TTFT SLO allows (chat is latency-sensitive).  
- Decode: continuous batching inside Inference GW (sibling deep-dive).  
- Prompt cache: sticky routing to cache-holding GPU workers when possible (consistent hash on `cache_key`).

#### 5.2.5 What breaks at each jump

| Jump | Breaks first | Fix |
|------|--------------|-----|
| 10× | BFF memory (long contexts), single PG | Context service; PG scale-up; Redis checkpoints |
| 100× | Cross-user noisy neighbor on GPUs; sync fanout | Fair queues; home cells; cell change logs |
| 1,000× | Global single-writer illusions; retention cost | Cells everywhere; aggressive cold tier; Option B |

### 5.3 Maintainability

#### 5.3.1 Versioning

- `model_version` frozen on run at admit (reproducibility / support).  
- Constitutional layer version id stored on run.  
- API BFF versioned; mobile clients tolerate unknown SSE event types.

#### 5.3.2 Observability

| Signal | Why |
|--------|-----|
| TTFT, TPS, queue_wait | UX + capacity |
| cache_hit_rate | Cost |
| safety_refuse_rate by category | Policy health |
| compaction_rate | Context pressure |
| sync_lag_p99 | Multi-device trust |
| incomplete_rate / cancel_rate | Reliability |
| GPU util / KV memory | Serving health |

**Cardinality discipline:** avoid per-prompt raw labels in metrics; sample traces.

#### 5.3.3 SLOs (examples)

| SLO | Target |
|-----|--------|
| Turn create success | 99.9% |
| TTFT Sonnet (non-queued) | p99 < 2s |
| Stream stall > 2s | < 0.5% of streams |
| Durable user message after ACK | 99.99% |
| Sync cursor lag | p99 < 5s for online devices |
| Harmful output escape (high-sev) | ~0 (measured via red-team + online eval) |

#### 5.3.4 Config & ops

- Feature flags for compaction, Option B resume, model rollout.  
- Shadow traffic for new Claude versions.  
- Runbooks: GPU region drain, safety brownout, PG cell failover, Redis checkpoint degradation mode.

#### 5.3.5 Privacy / retention ops

- User delete conversation → soft delete + async purge items/objects.  
- Export on request (Phase).  
- Training opt-out flags never leak into product inference path incorrectly.

---

## 6. Wrap-Up

### 6.1 Summary talking points

1. **Atomic turn create** before stream — durability and idempotency first.  
2. **Split load classes** — PG vs Redis vs SSE vs GPU prefill vs safety.  
3. **Context is a first-class subsystem** — tokenize, compact with disclosure, cache prefixes.  
4. **Constitutional AI + classifiers** with lag-buffered streaming safety.  
5. **Home-cell sync** for multi-device; CAS leaf conflicts.  
6. **Route Haiku/Sonnet/Opus** with visible degradation under GPU pressure.  
7. Scale story: stream GW → cells → global edge; GPU admission before thrash.

### 6.2 Risk register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Long-context cost explosion | Unit economics | Caps, caching, Haiku routing, compaction |
| Safety miss on stream | Harm / trust | Lag buffer; fail closed high-sev |
| Sync conflicts | User confusion | CAS + clear UX |
| Single-region PG | Outage | Cells + replicas; backups |
| Cache sticky routing imbalance | Hot GPUs | Rebalance; cache replication |
| Compaction hallucinations | Wrong advice | Keep recent full fidelity; mark summaries |
| Checkpoint Redis loss | Weaker resume | PG finalize path; Option B later |

### 6.3 Phased rollout

| Phase | Ship |
|-------|------|
| MVP | Option A streaming, Sonnet+Haiku, basic safety, quotas, single region, sync poll |
| 1.5 | Projects, attachments, compaction UI, push sync, Opus tier, prompt cache |
| 2 | Home cells, Option B resume, multi-region inference, search, Artifacts deeper |
| 3 | Global cell mesh, advanced memory, realtime multimodal hooks |

---

## 7. Deeper / Related Interview Questions

### Q1. Why not put conversation state only in the client?

**A:** Multi-device sync, abuse forensics, safety audit, and reopening after reinstall all need server durability. Client cache is an optimization, not source of truth.

### Q2. How do you prevent lost messages on double-tap Send?

**A:** Idempotency-Key + atomic TX creating item+run. Retries return the same `run_id` and reconnect to stream or show completed output.

### Q3. SSE vs WebSocket for Claude chat?

**A:** SSE/`fetch` streaming fits request/response turns, proxies, and simple auth. WebSocket helps bidirectional cancel/sync but adds connection state complexity. MVP: SSE; optional WS for push.

### Q4. How does context compaction differ from prompt caching?

**A:** Compaction **changes** the logical transcript (summary item). Prompt caching **reuses** KV/prefix computation for unchanged bytes. Use both: cache constitutional+project prefix; compact only when over limit.

### Q5. Where do you store the KV cache?

**A:** On GPU workers (Inference plane), not in Chat PG. Chat stores `cache_key` / breakpoints and routing hints. Sticky consistent hashing improves hit rates.

### Q6. What’s the deal-breaker for silent model downgrades?

**A:** Trust. Auto routing to Haiku under load is fine **with user-visible notice**. Silently labeling Haiku as Opus is not.

### Q7. How do you bound GPU memory with 200K-context chats?

**A:** Cap concurrent long-context slots per GPU; separate pools for long vs short; pre-admit token estimates; reject/queue when KV headroom insufficient; prefer Haiku/short for free tier.

### Q8. Home cell vs multi-master sync for chats?

**A:** Chat DAG with branching wants a single writer per user/conversation to avoid divergent leaves. Home cell is the pragmatic staff answer; CRDTs are usually overkill.

### Q9. How do classifiers keep up at 100×?

**A:** Separate safety fleet; smaller distilled classifiers for stream chunks; async final heavier models; scale from `admit_QPS × classifiers_per_turn`, not DAU.

### Q10. Fail open or closed when safety is down?

**A:** High-severity categories fail closed. Soft tone classifiers may degrade. Never fail open the whole stack for consumer chat without an explicit exec decision.

### Q11. How do you index chats for search without killing PG?

**A:** Async indexer (OpenSearch/MEILISEARCH-class) fed by outbox. PG remains source of truth; search is eventually consistent.

### Q12. What data structure is the conversation?

**A:** A **DAG of items** with `parent_id` / `leaf_id`, not only a linear array—needed for edit-branch and regenerate.

### Q13. How does Stop interact with continuous batching?

**A:** Cancel token checked between decode steps; remove sequence from batch; free KV slot; orchestrator finalizes `cancelled`. Leases prevent zombie sequences.

### Q14. Why Redis checkpoints instead of PG per token?

**A:** Token write amplification would melt Postgres. Redis absorbs high-frequency partials; PG stores terminal durable state.

### Q15. How do you estimate tokens before the model runs?

**A:** Tokenizer service approximating model tokenizer; reserve `input + max_output`; settle actual usage on completion. Slight mis-estimates OK if bounded.

### Q16. Consistent hashing — where?

**A:** (1) User → home cell. (2) `cache_key` → GPU worker set for prefix cache. (3) Idempotency key → API shard. Different rings, same idea.

### Q17. How do you handle fanout to many devices?

**A:** Don’t broadcast full messages globally. Bump per-user cursor; devices pull deltas. Push is a wake signal, not the payload bus at scale.

### Q18. What’s different because this is Anthropic?

**A:** Constitutional AI principles in platform layers; emphasis on harmlessness and helpful refusals; long-context product pressure; Claude model tiers; careful disclosure ethics around compaction and system layers.

### Q19. How do Projects change the architecture?

**A:** Shared knowledge files → object store + indexed chunks; prefix cache across turns in a Project; access control per project membership; compaction across long research threads.

### Q20. Load balancer strategy for stream gateways?

**A:** Connection-aware LBs; idle timeouts tuned for long SSE; draining with connection shedding; sticky optional for Option A cancel path.

### Q21. How do you test streaming safety lag buffers?

**A:** Red-team suites that place disallowed content after N tokens; measure escape rate vs UX latency; canary new classifier versions.

### Q22. Memory vs conversation history?

**A:** History is per-conversation items. Optional “memory” is a cross-conversation store with explicit user control—separate service, not stuffed invisibly into every prompt without policy.

### Q23. What happens when Opus queue depth explodes?

**A:** Deadline queues (e.g. 10–30s); then degrade Auto to Sonnet/Haiku with notice, or 503 busy. No infinite wait holding user attention without feedback.

### Q24. How do you shard Postgres?

**A:** Shard by `user_id` (home cell). Conversations inherit user shard. Avoid sharding by `conversation_id` alone if sync is per-user.

### Q25. Cost vs quality knobs you’d show execs?

**A:** Cache hit rate, Auto routing mix, compaction rate, free-tier abuse reject rate, GPU util, $ per active user. Chat quality evals alongside.

### Q26. Algorithm for choosing what to compact?

**A:** Prefer summarizing oldest turns beyond a keep-recent window; protect system-critical prefs; use hierarchical summaries (map-reduce style) for very long Projects; measure QA regression.

### Q27. Why not store embeddings for every message in MVP?

**A:** Cost and complexity. Search can start with lexical index; embeddings later for semantic retrieval inside Projects.

### Q28. How do you prevent IDOR on conversation IDs?

**A:** Unguessable IDs + authz check every read/write; never trust client-owned user_id; cell router still enforces auth.

### Q29. What’s the invariant tying quota to streaming?

**A:** Reserve on admit; settle on terminal; TTL sweeper releases abandoned reservations so streams can’t leak budget forever.

### Q30. If you only had 30 more minutes in the interview, what next?

**A:** Deep-dive Inference continuous batching + KV memory admission (sibling docs), and a crisp story for Constitutional streaming safety under overload.

---

*End of Claude Chat Service system design.*
