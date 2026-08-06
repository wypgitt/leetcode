# System Design: ChatGPT (Consumer Assistant)

> **Focus areas:** Conversation persistence · Token streaming · Model routing · Tools · Safety · Quotas · Graceful degradation  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Differentiation:** Consumer assistant product — **not** the OpenAI Playground experimentation workbench  
> **Quality bar:** Correct arithmetic, split dissimilar write/stream classes, explicit invariants, resolved streaming ownership (Option A vs B)

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

Goal: **bound the product**—ChatGPT as a **consumer assistant** (chat UX, persistence, tools, safety, quotas, degradation), distinct from Playground’s experimentation surface.

### 1.0 ChatGPT vs Playground (say this early)

| Dimension | **ChatGPT (this doc)** | **Playground** (sibling doc) |
|-----------|------------------------|------------------------------|
| Primary user | Consumers / knowledge workers chatting | Developers experimenting with prompts/APIs |
| Success metric | Helpful answer, trust, retention | Reproducibility, inspectability, compare/fork |
| Config surface | Minimal (model tier, tools toggles) | Rich sampling/schema/tools inspector |
| Compare / fork / copy-as-code | Out of MVP | MVP |
| Hidden system/safety layers | **Yes** (productized; user can’t edit) | Prefer transparent; no silent *developer* prompt mutation |
| Memory-ish features | Optional product memory | Not core |
| Abuse / free-tier quotas | First-class | Tenant/project API quotas |
| Degradation UX | “Busy, try again / lighter model” | Admission + inspector errors |

**Scope statement:** Design ChatGPT the product—not an API workbench.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who is the user? | Consumer / prosumer; free + Plus/Pro tiers | Tiered quotas; product UX not API knobs |
| F2 | Core loop? | Multi-turn chat; regenerate; edit→fork branch; stop | Conversation + Turn/Run atomic create |
| F3 | Streaming? | Yes — tokens appear live | SSE/`fetch` stream; ownership Option A/B |
| F4 | Persistence? | Chats list; reopen history; search later | Durable conversations/items/turns |
| F5 | Model routing? | Auto + user-selectable tiers (fast / smart / reasoning) | Router + capability catalog; resolve version at admit |
| F6 | Tools? | Browsing, code interpreter, file analysis stubs | Tool bus; sandbox egress; not all MVP deep |
| F7 | Safety? | Block disallowed; soft refusals; jailbreak resistance | Classifiers pre/post/stream; hidden safety layers |
| F8 | Memory? | Optional saved memories Phase 1.5 | Separate memory store; explicit user control |
| F9 | Auth / sync? | Logged-in; multi-device | Home cell by `user_id`; sync APIs |
| F10 | Quotas? | Free message caps; Plus higher; abuse limits | Reserve/settle; rate limits; fairness |
| F11 | Attachments? | Images/files Phase 1 / 1.5 | Object store + multimodal parts |
| F12 | Shared chats? | Link share Phase 2 | Snapshot ACL; strip secrets/safety internals |

**MVP functional scope (lock with interviewer):**

1. Authenticated chat: create conversation, send message, **stream** assistant reply.
2. **Atomic turn/run creation** (user input durable before inference).
3. Conversation list + open history; edit message → branch; regenerate; Stop.
4. **Model routing** across tiers (auto or user pick); resolved model frozen per turn.
5. **Safety**: input/output classifiers; hidden system/safety instructions (explain clearly ≠ silent mutation of *user-visible* custom instructions without disclosure).
6. Basic **tools stubs**: browsing and/or code-exec with sandbox (at least architecture).
7. Quotas by tier; abuse rate limits; **graceful degradation** when models overloaded.
8. Usage metering; soft reservation + settle for tokens/messages.

**Out of MVP (explicitly defer):**

- Full team workspaces / admin SSO complexity (hooks: `workspace_id`)
- Perfect seamless stream resume across all failures (Option B Phase 2)
- Advanced long-term memory graph
- Voice/realtime multimodal as primary (design hooks)
- Third-party GPT store marketplace

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT? | Feels instant | p50 < 500ms, p99 < 2s (excl. heavy reasoning queue) |
| N2 | Streaming smoothness? | No multi-second stalls | Flush ≤ 50–100ms once tokens flow |
| N3 | Durability? | No lost sent user messages after ACK | Input durable before stream; completed turn durable; partial RPO≈1s |
| N4 | Availability? | Consumer critical | 99.9% control plane; degrade to lighter models / queues |
| N5 | Safety vs latency? | Must not ship egregious harm | Streaming safety policy explicit (buffer/classify) |
| N6 | Multi-region? | Global users | Active-active edge; **home cell** single-writer per user |
| N7 | Privacy? | Chats sensitive | Encryption, IDOR-safe IDs, retention controls |
| N8 | Fairness? | Free users don’t melt Plus under load | Tiered admission; abuse isolation |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New chat → type → stream answer → title autogen → appears in sidebar.
2. Follow-up turn with context from prior items.
3. Edit earlier user message → branch conversation; continue on new leaf.
4. Tool call (browse/code) → tool result item → model continues → final answer.
5. Model overloaded → router offers lighter model or “try again shortly” with queue position.
6. Safety refusal → typed refusal; turn completes with `safety_outcome`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit | Idempotency-Key → one turn/run |
| Disconnect mid-stream | MVP Option A: partial + Retry; Option B: resume `after_sequence` |
| Stop vs tab close | Stop cancels; tab close policy product (MVP often cancel or short grace) |
| Context overflow | Product may auto-compact **with disclosure** / summarize older turns; **do not silently rewrite user’s custom instructions**; system/safety layers remain platform-owned |
| Free tier cap hit | Clear upgrade UX; no silent quality lie |
| Jailbreak attempt | Safety pipeline; may refuse; log signals |
| Tool SSRF | Egress allowlist; block link-local/metadata |
| Concurrent tabs | `expected_leaf_id` conflict → 409 |
| Degraded model swap | User-visible notice when Auto routes down |
| Abuse spam | Quotas + anomaly; fail closed on limiter errors for free tier |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 50M | 500M | — (use 100× as mega) | treat 1,000× as extreme global |
| DAU | 10M | 100M | 1B | multi-B class |
| Peak concurrent streams | 200K | 2M | 20M | 200M |
| Turns / day | 200M | 2B | 20B | 200B |
| Avg tokens in+out / turn | ~2K | ~2K | 2–4K | 2–4K |
| Peak **output** tokens/s | ~2M | ~20M | ~200M | ~2B |
| Conversations stored | ~5B | ~50B | ~500B | retention-capped |
| Items stored (order) | ~50B | ~500B | ~5T | retention-capped |
| Read QPS (list/open) | ~50K | ~500K | ~5M | ~50M |
| Postgres durable writes peak (order) | ~5–20K | ~50–200K | cells | many cells |
| Redis checkpoint ops peak | ~50–200K | ~0.5–2M | ~5–20M | huge / regional |
| Stream events/s (batch ~20 tok) | ~100K | ~1M | ~10M | ~100M |

**Note on MAU table:** consumer ChatGPT baselines are already large—progressive scale still stresses architecture via **concurrent streams** and **token throughput**, not only user counts. Prefer defending **stream concurrency + tokens/s** in the interview.

**What each jump forces:**

- **10×:** Dedicated stream gateways; Redis checkpoints; router + multi-model pools; safety fleet.
- **100×:** User home cells; tool sandboxes regional; cold conversation tiering; fair admission.
- **1,000×:** Global edge; Option B replay if resume SLO demands; memory/safety platforms as separate products; aggressive retention.

### 1.5 Etc. (Constraints & Assumptions)

- ChatGPT is a **client of Inference Gateway** (and tool sandboxes)—not training.
- **Hidden system/safety layers exist** and are platform-controlled; distinguish from “silent mutation of user-authored prompts/custom instructions.”
- Web + mobile; sync via APIs.
- Playground-style compare/inspector **out of scope**.

**Scope statement to repeat back:**

> Design consumer ChatGPT: durable multi-turn conversations with atomic streamed turns, model-tier routing, safety classifiers + hidden safety layers, tool stubs, tiered quotas, and graceful degradation under overload—starting at large consumer concurrency and scaling through 10× / 100× / 1,000× with home cells. Distinct from Playground experimentation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Durable turn creates** | TX: items + run | ~5–20K/s | ~50–200K/s | Postgres cells |
| **Redis checkpoints** | Partial tokens ~1s | ~50–200K/s | ~0.5–2M/s | Redis |
| **Stream frames to clients** | SSE events | ~100K/s | ~1M/s | Gateway |
| **Safety classifier QPS** | Input/output | ~turns peak × k | ×10 | Safety fleet |
| **Tool invocations** | Browse/code | fraction of turns | ×10 | Sandbox pools |
| **Quota checks** | Reserve/settle | ~turn rate | ×10 | Redis limiter |
| **Analytics/Kafka** | Usage/safety | ~turn rate | ×10 | Bus |

**Anti-pattern:** one “write QPS” mixing Postgres, Redis, SSE, and Kafka.

### 2.2 Token throughput

```text
Baseline peak output tokens/s ~2M (order-of interview number; tune with interviewer)
If batch 20 tokens/event → ~100K stream events/s
Gateway fan-out memory: 200K conns × 50–100 KB ≈ 10–20 GB fleet-wide
```

### 2.3 Storage

```text
Item ~2 KB avg
50B items × 2 KB = 100 TB raw baseline order
+ indexes/replicas → hundreds of TB
At extreme scale without retention → multi-PB/EB — retention mandatory
```

**Archive:** per-conversation object segments + manifest for reopen; Parquet for analytics separately.

### 2.4 Safety amplification

```text
Per turn: 1 input classify + N chunk output classifiers + final
If N=5 → classifier QPS ≈ 6 × turn_admit_QPS
Size safety fleet from that—not from DAU alone
```

### 2.5 Degradation math

```text
Smart-tier capacity C_smart, demand D
If D > C: route overflow to fast-tier (with notice) OR queue with deadline OR 503 busy
Never unbounded queue for interactive chat
```

---

## 3. High-Level Design

### 3.1 Product / UX wireframe

```text
+----------------------------------------------------------------------+
| ChatGPT          [Auto ▾]   [Tools]              [Upgrade]  [User]   |
+---------------+------------------------------------------------------+
| Chats         |  Conversation title                                  |
| Today         |                                                      |
|  Trip ideas   |  User: Plan a 3-day trip to Kyoto...                 |
|  SQL help     |                                                      |
|  * New chat   |  Assistant: Here's a balanced itinerary...           |
|               |  ▍ (streaming)                                       |
|               |                                                      |
|               |  [ Message ChatGPT...                 ] [Stop] [Send]|
+---------------+------------------------------------------------------+
| Notices: "Using faster model due to high demand" (when degraded)     |
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
User / Tier
  └── Conversation
        ├── Item[]  (DAG: user/assistant/tool_call/tool_result/system_visible?)
        └── Turn / Run   # unit of generation, billing, safety, routing
              ├── input refs + expected_leaf_id
              ├── routing decision (requested tier → resolved model version)
              ├── product_system_layers_ref (platform safety/system; not user-editable)
              ├── user_custom_instructions_ref (user-visible settings; no silent edit)
              ├── tool_choice / enabled_tools
              ├── status + termination_reason
              ├── safety_outcome
              ├── usage + quota settlement
              └── metrics (TTFT, queue_wait, degradations)
```

**Atomic turn/run create (preferred):**

Single TX creates user item(s) + run + output placeholder + idempotency + outbox dispatch.  
**No orphan user messages** without a run under normal send path.

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

### 3.3 Hidden system/safety layers vs user content (resolve contradiction)

| Layer | Editable by user? | Shown in UI? | May change without user edit? |
|-------|-------------------|--------------|-------------------------------|
| User message | yes | yes | **No silent rewrite** |
| Custom instructions | yes | settings UI | **No silent rewrite** |
| Platform system prompt | no | generally no | Yes (platform) |
| Safety policy / classifiers | no | only via refusals | Yes (platform) |
| Auto context compact | policy | **should disclose** when it happens | Yes, with notice / marker item |

**Interview line:**

> We do **not** silently mutate user-authored text or custom instructions. The product **does** apply hidden system/safety layers and may insert disclosed compaction summaries. That is different from Playground’s “never silently alter developer prompts.”

### 3.4 API shape (product BFF / internal)

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `/api/conversations` | List / create |
| GET | `/api/conversations/{id}/items` | History page |
| **POST** | **`/api/conversations/{id}/turns`** | **Atomic create-and-stream turn** |
| GET | `/api/turns/{id}` | Status + output |
| GET | `/api/turns/{id}/events?after=` | Resume (Option B) |
| POST | `/api/turns/{id}/cancel` | Stop |
| POST | `/api/turns/{id}/regenerate` | New turn from same input leaf |

```http
POST /api/conversations/{id}/turns
Idempotency-Key: ...
{
  "expected_leaf_id": "item_...",
  "input": [{"role":"user","content":[{"type":"text","text":"..."}]}],
  "model_tier": "auto",          # auto|fast|smart|reasoning
  "tools": {"browsing": true, "code": false},
  "stream": true
}
```

### 3.5 Streaming ownership: Option A vs B

| | **Option A — Coupled BFF (MVP)** | **Option B — Run Service + replay** |
|---|----------------------------------|-------------------------------------|
| Who holds stream | BFF/stream gateway tied to request | Independent Run Worker + event buffer |
| BFF death | Turn → incomplete; user Retry | Client reconnects `after_sequence` |
| Complexity | Lower | Higher |
| Resume SLO | Honest: no seamless | Strong resume |

**Choice:** MVP **Option A** with durable partial checkpoints; Phase-2 **Option B** if product promises resume across gateway failure.

```text
Option A:
 Client → Stream GW/BFF → Inference
            └ checkpoints Redis; finalize Postgres

Option B:
 Client → Stream GW → reads replay buffer
 Run Worker → Inference → writes replay buffer + checkpoints → finalize
```

### 3.6 Model routing

```text
Router inputs:
  user tier, selected preference (auto/fast/smart/reasoning),
  conversation features (tool need, image?, length),
  safety mode, current capacity signals, latency SLOs

Router outputs:
  resolved model_version, max_tokens policy, degradation flags
```

| Strategy | Pros | Cons |
|----------|------|------|
| User picks only | Simple | Bad overload UX |
| Auto only | Smooth | Trust/transparency |
| **Auto + override (chosen)** | Balance | More UX states |
| Cascade fallback | Availability | Must **notify** on downgrade |

**Deal-breaker:** silently answering with a much weaker model while UI still shows “Smart” without notice.

### 3.7 Tools (browsing / code-exec stubs)

```text
Model --tool_call--> Tool Orchestrator
  ├── Browsing: fetch via egress proxy → extract → tool_result item
  └── Code interpreter: schedule sandbox → files in/out → tool_result
Then model continues (multi-step loop with caps)
```

**Invariants:**

- Tool args size limits; time limits; network allowlists.  
- Sandbox no host IMDS; no secret env from other users.  
- Tool loop max steps; then force final answer or error.  
- Persist tool_call/tool_result as items for replay.

### 3.8 Safety pipeline

```text
User input → input classifiers / policy → (block | transform refusal | allow)
         → assemble model input (user items + platform layers + tools schemas)
         → stream tokens → chunk classifiers → (continue | truncate+refuse)
         → final output classifiers → persist safety_outcome
```

**Streaming trade-off table:**

| Approach | UX | Risk |
|----------|----|------|
| Fully buffer then send | Safer | Feels slow |
| Stream with lag buffer (N tokens) | Balance | Residual risk |
| Stream raw + post-hoc | Fast | May show bad content briefly |

**Choice:** lag buffer / inline classifiers for consumer ChatGPT; stricter modes for sensitive categories.

### 3.9 Quotas & abuse

| Dimension | Free | Paid |
|-----------|------|------|
| Messages / windows | Tight | Higher |
| Token budgets | Tight | Higher |
| Concurrent streams | 1–2 | more |
| Heavy model access | Limited / queued | Priority |
| Tool minutes | Low | Higher |

Reserve on admit; settle on terminal; sweeper for leases.  
Limiter errors: **fail closed** on free/abuse paths; paid may fail-static with ceiling (see rate-limiter doc).

### 3.10 Graceful degradation

| Signal | Action |
|--------|--------|
| Smart pool saturation | Auto → fast model + banner |
| Regional inference outage | Reroute region; or queue with short deadline |
| Safety fleet brownout | Fail closed on highest-risk categories; degrade soft classifiers carefully |
| Tool sandbox exhausted | Disable tool with message; answer without tool |
| Checkpoint Redis down | Finalize-only mode; weaker partial resume |

**Never:** unbounded “you’re next” queues that hold GPUs forever.

### 3.11 High-level component trade-offs

| Component | Options | Choice |
|-----------|---------|--------|
| Conversation DB | Postgres vs wide-column | Postgres cells MVP → tiered storage |
| Stream | SSE fetch vs WS | SSE/`fetch` for turns; WS optional for mobile push |
| Memory | None / explicit memories | Optional Phase 1.5 explicit |
| Title gen | Sync vs async | Async after first turn |
| Search chats | Like/ilike vs index | Async search indexer Phase 1.5 |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +------------------+     +--------------------+
| Web/Mobile  |---->| Edge / BFF /     |---->| Chat API           |
+-------------+     | Stream Gateway   |     | (turns, convos)    |
                    +--------+---------+     +---------+----------+
                             |                         |
                             | stream                  v
                             |                +--------+----------+
                             |                | Conversation Svc  |
                             |                | (home cell PG)    |
                             |                +--------+----------+
                             |                         |
                             v                         v
                    +----------------+        +--------+----------+
                    | Run / Turn     |<------>| Redis quotas +    |
                    | Orchestrator   |        | checkpoints       |
                    +--------+-------+        +-------------------+
                             |
         +-------------------+-------------------+----------------+
         v                   v                   v                v
+----------------+  +----------------+  +----------------+  +--------------+
| Model Router   |  | Safety Fleet   |  | Tool Bus       |  | Inference GW |
+--------+-------+  +----------------+  +--------+-------+  +------+-------+
         |                                       |                 |
         +---------------------------------------+-----------------+
                                                 v
                                          Model Serving Pools
                                          (fast/smart/reasoning)
```

### 4.2 Atomic turn + stream (Option A)

```text
Client          ChatAPI           Orchestrator        Safety      Inference
 |--POST turn---->|                  |                  |            |
 |                |--TX durable----->|                  |            |
 |                |--reserve quota-->|                  |            |
 |                |--classify in---------------------->|            |
 |                |<--allow/refuse---------------------|            |
 |                |--route model---->|                  |            |
 |                |--start stream---------------------------------->|
 |<--SSE events---| <-----tokens-----|<----chunk class--|------------|
 |                |--checkpoint Redis|                  |            |
 |                |--finalize PG---->|                  |            |
 |                |--settle quota--->|                  |            |
```

### 4.3 Tool loop sequence

```text
Orchestrator→Inference: generate
Inference→Orchestrator: tool_call(browse)
Orchestrator→Safety: check tool args
Orchestrator→Browse Sandbox: fetch
Sandbox→Orchestrator: tool_result
Orchestrator: persist items; continue generation
Inference→Orchestrator: final text
```

### 4.4 Degradation sequence

```text
Router: smart_pool utilization 95%
 → decision: downgrade_to_fast + flag
 → client event: notice.model_degraded
 → stream proceeds on fast model
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **User input durable before inference / before first streamed token is “committed.”**  
2. **Atomic turn create** with Idempotency-Key.  
3. **`response.completed` / turn completed only after finalize + usage durable.**  
4. **CAS terminal states** (cancel vs complete).  
5. **Resolved model version frozen** at admit.  
6. **No silent rewrite of user-authored content / custom instructions.**  
7. **Platform safety layers may apply**; outcomes persisted.  
8. **Quota reservation TTL + settle idempotent by turn_id.**  
9. **Tool sandboxes isolated; egress controlled.**  
10. **Home-cell single-writer** for a user’s conversations.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Inference 503 | Queue short / downgrade / fail incomplete; reconcile quota |
| BFF crash (A) | incomplete + Retry; partial from checkpoint if any |
| Redis down | fail closed quotas (free); degrade checkpoints |
| Safety down | fail closed high-risk; don’t “fail open” to unconstrained |
| Tool timeout | tool error result; model may continue or apologize |
| Cell primary down | promote per RPO; in-flight → incomplete |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Modular monolith BFF, PG, Redis, router, safety, inference GW |
| 10× | Stream gateway tier; safety horizontal; tool pools; Kafka usage |
| 100× | User cells; cold storage; per-tier admission; regional tools |
| 1,000× | Edge PoPs; Option B replay; retention hard; memory/safety platforms |

**Fair admission:**

```text
priority = f(tier, cost_budget_remaining, abuse_score)
weighted fair queues into model pools
free tier sheds first under overload
```

### 5.3 Maintainability

- Turn orchestrator as explicit state machine (testable).  
- Prompt/safety layer versioning with audit.  
- Shadow routing experiments.  
- Metrics: TTFT, degradation_rate, refusal_rate, tool_success, quota_deny, stream_disconnect, finalize_lag.  
- No per-turn_id Prometheus labels.

### 5.4 Context management (consumer-honest)

| Policy | Behavior |
|--------|----------|
| Fit in window | Send recent leaf path + pinned system layers |
| Overflow | Compact older turns into summary **item** marked `compaction` OR truncate with notice |
| User custom instructions | Always included as user settings dictate; not silently edited |
| Tool groups | Keep call/result pairs atomic when compacting |

### 5.5 Memory-ish (optional)

```text
Explicit Memory Store: user-approved facts
Retrieve top-k relevant → inject as platform-side context with disclosure in settings
Not a silent rewrite of past messages
```

### 5.6 Consistency

- Read-your-writes in home region.  
- Sidebar list eventual via cache + invalidate on turn finalize.  
- Search index async.

---

## 6. Wrap-Up

### 6.1 What we designed

**Consumer ChatGPT**: durable conversations with **atomic streamed turns**, **model-tier routing** with visible degradation, **safety classifiers + hidden platform layers** (without silent mutation of user-authored content), tool stubs with sandboxed egress, tiered quotas, and Option A streaming MVP with Option B resume path—scaled via user home cells and fair admission. Explicitly **not** Playground.

### 6.2 Key decisions worth defending

1. **ChatGPT ≠ Playground** — productized assistant vs experimentation workbench.  
2. **Atomic `POST .../turns`**.  
3. **Option A vs B** streaming ownership—honest MVP.  
4. **Hidden safety/system layers OK; silent user-text mutation not OK.**  
5. **Router + visible degrade** under overload.  
6. **Split write/stream/safety/tool load classes.**  
7. **Reserve/settle quotas; fail closed on free abuse path.**  
8. **Tool loop caps + SSRF controls.**  
9. **CAS terminals + frozen model version.**  
10. **Home-cell single-writer; edge active-active.**

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Safety vs TTFT | Tune lag buffer; category-specific policies |
| Over-degradation trust | Clear UX; metrics on surprise downgrades |
| Storage growth | Retention, archive manifests |
| Tool abuse | Quotas, egress, sandboxes |
| Resume expectations | Don’t over-promise on Option A |

### 6.4 How to present in 45 minutes

1. ChatGPT vs Playground + requirements (7 min)  
2. Numbers: streams + tokens + split classes (5 min)  
3. Domain + atomic turns + safety/system layers (8 min)  
4. Streaming Option A/B (7 min)  
5. Routing + degradation + quotas (7 min)  
6. Tools + scale cells (5 min)  
7. Q&A (remaining)

---

## 7. Deeper / Related Interview Questions

### 7.1 Product differentiation

**Q: Why not reuse Playground design as-is?**  
A: Different UX goals (assist vs experiment), hidden safety layers, degradation/quotas for free tier, no compare/inspector MVP, different context policies.

**Q: Is ChatGPT just a UI on the API?**  
A: Shares inference; adds conversation SoT, routing, safety productization, tools UX, consumer quotas, multi-device sync.

**Q: Where do custom GPTs / store fit?**  
A: Phase 2: versioned tool+instruction packs with authz—still not Playground compare.

### 7.2 Streaming & durability

**Q: SSE vs WebSocket?**  
A: `fetch` + SSE for one-shot turns; WS for bidirectional voice/realtime later. Native `EventSource` is GET-only.

**Q: What is durable before first token?**  
A: User item, turn row, routing snapshot, safety input outcome, quota reservation—not assistant text.

**Q: Option A vs B—when upgrade?**  
A: When resume-across-gateway is an SLO / mobile backgrounding demands it.

**Q: Stop vs disconnect?**  
A: Stop cancels inference; disconnect MVP may cancel or grace—state the policy.

**Q: Slow client?**  
A: Bound buffers; disconnect; Option B catch-up via events.

### 7.3 Safety & layers

**Q: Do you silently change user prompts?**  
A: No for user-authored content/custom instructions. Platform injects system/safety layers separately.

**Q: How stream safely?**  
A: Chunk classifiers / lag buffer; refuse mid-stream with typed event; persist outcome.

**Q: Jailbreaks?**  
A: Layered classifiers + model alignment + policy; telemetry; no silver bullet—defense in depth.

**Q: Safety service down?**  
A: Fail closed for high-risk; don’t open unconstrained generation.

### 7.4 Routing & degradation

**Q: How does Auto choose models?**  
A: Features + tier + capacity; prefer cheapest meeting quality bar; fallback with notice.

**Q: Can you hide a downgrade?**  
A: Shouldn’t—trust issue; emit notice event.

**Q: Reasoning models with long TTFT?**  
A: Separate UX (thinking indicators); separate queues; quotas.

**Q: Thundering herd on new model launch?**  
A: Lottery / percent rollout / per-tier caps.

### 7.5 Tools

**Q: Browse SSRF?**  
A: Egress proxy allowlist; block RFC1918/link-local/metadata; size/time caps.

**Q: Code exec escape?**  
A: microVM sandbox; no creds; network off or proxy; CPU/mem/time limits; fresh FS.

**Q: Multi-tool loops forever?**  
A: Max steps/tokens; then stop with message.

**Q: Persist tool results?**  
A: Yes as items—needed for reopen/regenerate consistency.

### 7.6 Quotas, abuse, billing

**Q: Message caps vs token caps?**  
A: Both; messages UX-simple; tokens protect cost; concurrency protects GPUs.

**Q: Reservation vs settle?**  
A: Reserve estimate; settle actual; sweeper TTL; ledger by turn_id.

**Q: Free tier limiter Redis down?**  
A: Fail closed.

**Q: Shared family accounts abuse?**  
A: Device/payment signals; soft anomaly—not only user_id.

### 7.7 Data model & storage

**Q: Branching chats?**  
A: Item DAG + active_leaf_id; edit forks sibling path.

**Q: Title generation?**  
A: Async turn after first exchange; don’t block stream.

**Q: Delete chat GDPR?**  
A: Soft delete + staged purge (DB, cache, search, backups policy).

**Q: Vitess?**  
A: MySQL tool—not Postgres. Use PG cell sharding / Citus-like / directory.

### 7.8 Multi-region

**Q: Active-active chats?**  
A: No multi-writer same conversation. Edge global; home cell single-writer.

**Q: Traveling user?**  
A: Nearest edge; RPC home; accept latency or optional migrate.

**Q: DR?**  
A: Fence, promote, incomplete in-flight turns, directory update.

### 7.9 Algorithms & structures

**Q: Idempotency map?**  
A: `(user_id, key) → turn_id` + body hash.

**Q: Context packing?**  
A: Token estimate; keep system/safety + recent leaf; compact older with marker.

**Q: Router?**  
A: Rules + capacity signals; optional ML ranker later; start with rules.

**Q: Fair queues?**  
A: Weighted fair by tier; separate pools per model class.

### 7.10 Failure injection

1. Inference storm → degrade + shed free.  
2. BFF kill mid-stream → incomplete (A).  
3. Redis checkpoint loss → partial RPO hole; terminal still PG.  
4. Safety brownout → fail closed risky.  
5. Tool sandbox OOM → tool error item.  
6. Duplicate Send → idempotent same turn.  
7. Cell failover → reconnect; some incomplete.  
8. Quota sweeper lag → temporary under-admit; not infinite free.  
9. Kafka down → chat still works if outbox local.  
10. Prompt layer bad deploy → version rollback; canary.

### 7.11 Comparison traps

**Q: ChatGPT vs API playground?**  
A: Covered in §1.0—assistant product vs experimentation.

**Q: ChatGPT vs character.ai / open webui?**  
A: Similar chat bones; emphasize safety, routing, quotas, tools sandbox, cells.

**Q: Why not only client-side history?**  
A: Multi-device, safety audit, tools, quota, model routing need server SoT.

### 7.12 Extra interviewer traps (high value)

- What exactly is atomic in turn creation?  
- Option A vs B—what do you promise users?  
- Hidden safety layer vs silent user prompt mutation—difference?  
- When do you show “using a faster model”?  
- What is durable at `completed`?  
- How do free users get shed before paid?  
- How do tool results reappear on regenerate?  
- What’s the classifier QPS multiplier?  
- How do you prevent SSRF from browsing?  
- Home cell vs edge stream gateway roles?  
- Can custom instructions be changed by safety? (No silent change—refusal instead)  
- How do you compact context without lying about history?  
- What fails first at peak—and what’s the degradation order?  
- Why split Postgres vs Redis vs SSE in estimates?  
- How is this design wrong for Playground users? (No compare/inspect/fork-as-first-class)

---

## Appendix A — Example schemas

```sql
CREATE TABLE conversations (
  id             UUID PRIMARY KEY,
  user_id        UUID NOT NULL,
  title          TEXT NOT NULL DEFAULT 'New chat',
  status         TEXT NOT NULL DEFAULT 'active',
  active_leaf_id UUID,
  item_seq       BIGINT NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX conversations_user_updated
  ON conversations (user_id, updated_at DESC)
  WHERE status = 'active';

CREATE TABLE items (
  id              UUID PRIMARY KEY,
  user_id         UUID NOT NULL,
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  parent_item_id  UUID,
  sequence        BIGINT NOT NULL,
  type            TEXT NOT NULL, -- message|tool_call|tool_result|compaction
  role            TEXT,
  content_parts   JSONB NOT NULL,
  visibility      TEXT NOT NULL DEFAULT 'user', -- user|internal_marker
  turn_id         UUID,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (conversation_id, sequence)
);

CREATE TABLE turns (
  id                 UUID PRIMARY KEY,
  user_id            UUID NOT NULL,
  conversation_id    UUID NOT NULL,
  status             TEXT NOT NULL,
  termination_reason TEXT,
  expected_leaf_id   UUID,
  model_tier_requested TEXT NOT NULL,
  model_snapshot     JSONB NOT NULL, -- resolved version
  degradation_json   JSONB,
  system_layers_ref  TEXT NOT NULL,  -- platform layer version
  custom_instr_ref   TEXT,          -- user settings version
  safety_outcome     JSONB,
  usage_json         JSONB,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE idempotency_keys (
  user_id    UUID NOT NULL,
  key        TEXT NOT NULL,
  body_hash  TEXT NOT NULL,
  turn_id    UUID NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, key)
);

CREATE TABLE usage_ledger (
  id          UUID PRIMARY KEY,
  user_id     UUID NOT NULL,
  turn_id     UUID NOT NULL UNIQUE,
  usage_json  JSONB NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Appendix B — Stream event types (illustrative)

```text
turn.created
notice.model_degraded
message.delta
tool_call
tool_result
safety.refusal
turn.completed | turn.incomplete | turn.cancelled | turn.failed
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Atomic turns, SSE streams Option A, PG+Redis, router, safety, quotas, tool stubs |
| 10× | Stream GW fleet, Kafka usage/safety, autoscale pools, degradation banners |
| 100× | User cells, regional tools, cold archives, fair admission |
| 1,000× | Edge PoPs, Option B replay if required, hard retention, separate safety/memory platforms |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Turn / Run | Unit of assistant generation + billing + safety |
| Item | Conversation DAG node |
| Model tier | Productized fast/smart/reasoning/auto |
| Platform system layers | Hidden system/safety prompts (not user-editable) |
| Custom instructions | User-visible settings (no silent mutation) |
| Option A / B | Coupled stream vs Run Service + replay |
| Degradation | Visible fallback under capacity |
| Compaction item | Disclosed summary replacing older turns |
| Home cell | Single-writer shard for user data |

## Appendix E — Estimation cheat-sheet

```text
Split: PG writes ≠ Redis checkpoints ≠ SSE events ≠ safety QPS ≠ tool QPS

output_tokens/s → events/s ≈ tokens/s / batch_size
classifier_QPS ≈ admit_QPS × (1 + chunk_checks + final)

Gateway RAM ≈ conns × 50–100 KB fleet-wide

Storage without retention at extreme consumer scale is not serious—always pair TTL/archive
```

## Appendix F — Playground contrast checklist (interview closer)

| Ask yourself | ChatGPT answer |
|--------------|----------------|
| Is compare side-by-side MVP? | No |
| Do users edit raw system prompts? | No |
| Hidden safety layers? | Yes |
| Auto model downgrade UX? | Yes, with notice |
| Copy-as-code? | No (not MVP) |
| Atomic turn create? | Yes |
| Stream ownership honesty? | Option A MVP / B later |

---

*End of design doc. Open with §1.0 ChatGPT vs Playground; whiteboard atomic turns + Option A/B + routing/safety; close with invariants in §5.1 and traps in §7.*
