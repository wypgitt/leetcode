# System Design: Multi-Question LLM Thread

> **Focus areas:** Context construction · Hierarchical summarization · Retrieval-augmented memory · Token budgets · Concurrent updates (CAS) · Streaming · Cost/GPU efficiency  
> **Style:** End-to-end AI infra design with progressive scale (10× → 100× → 1,000×)  
> **Theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — concurrency, consistency, caching, backpressure, safety  
> **Quality bar:** Explicit token accounting, leaf CAS invariants, split durable writes vs stream checkpoints, honest context-overflow behavior

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

Goal: **bound the product**—a **multi-question LLM thread** (long-lived conversation) where users ask many questions over time, the system builds model context under token limits, summarizes and retrieves past relevant turns, and correctly handles concurrent edits/tabs—without silent corruption or unbounded GPU cost.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a thread? | Ordered (DAG) conversation with many Q&A turns | Thread + Item + Turn/Run model |
| F2 | Multi-question? | User asks sequential & parallel follow-ups; revisits topics | Context ≠ naive full history dump |
| F3 | Context window? | Finite (e.g. 200K); must pack smartly | Token budgeter + policies |
| F4 | Summarization? | Auto-compact older turns with disclosure | Hierarchical summaries as items |
| F5 | Retrieval? | Pull relevant past turns/files into context | Thread memory index per thread/user |
| F6 | Streaming? | Yes | SSE; checkpoints |
| F7 | Edit/regenerate? | Edit → branch; regenerate new run | DAG + leaf pointer |
| F8 | Concurrent tabs? | Conflict detection | `expected_leaf_id` CAS |
| F9 | Tools/files? | Optional attachments & tools | Items for tool results; budget them |
| F10 | Safety? | Input/output classifiers; jailbreak resist | Pipeline around packed context |
| F11 | Sharing? | Phase 2 link share | Snapshot ACL |
| F12 | Memory across threads? | Optional user memory Phase 1.5 | Separate store; explicit |

**MVP functional scope (lock with interviewer):**

1. Create thread; post question; **stream** answer.
2. Multi-turn with **token-budgeted context construction** (system + safety + recent + retrieved + summaries).
3. **Hierarchical summarization** when nearing limits; disclose compaction.
4. **Thread-local retrieval** over past items/chunks.
5. Edit/branch/regenerate; **CAS leaf** for concurrent updates.
6. Stop/cancel; idempotent create turn.
7. Usage/quota; graceful degrade.

**Out of MVP:**

- Perfect cross-thread agent memory graph  
- Realtime multi-user collaborative editing  
- Voice  
- Guaranteed seamless stream resume (Phase 2 Option B)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT | Snappy | p50 < 500ms–1s after admit |
| N2 | Durability | No lost user Q after ACK | Durable before stream |
| N3 | Conflict UX | Clear | 409 on leaf CAS fail |
| N4 | Correctness of context | No silent wrong branch | Pin leaf + item ids in run |
| N5 | Summarization quality | Good enough + reversible | Keep raw items; summaries additive |
| N6 | Availability | High | Degrade model; keep writes |
| N7 | Cost | Bound tokens/turn | Hard budgets; cache prefixes |
| N8 | Privacy | Thread isolation | ACL on thread_id |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Long thread 200 turns → auto summaries → still answers with retrieved older fact.
2. User asks Q about turn 5’s code → retriever pulls that chunk into context.
3. Two tabs: one wins CAS; other gets 409 refresh.
4. Edit middle question → branch; summaries recomputed along branch policy.
5. Stop mid-stream → partial assistant item; retry/regenerate options.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Context overflow mid-pack | Drop lowest priority; or compact sync if needed; never exceed max |
| Summary job lagging | Pack without new summary; may drop more raw turns |
| Concurrent summarize + new turn | Versioned summary items; run pins summary_ids used |
| Retrieval returns irrelevant | Score threshold; always keep recent tail |
| Double-submit question | Idempotency-Key |
| Tool result huge | Truncate/store blob; retrieve on demand |
| Safety refusal | Terminal refused; leaf advances per policy |
| User deletes turn | Tombstone; rebuild memory index |
| Model swap mid-thread | Allowed; pin resolved model per turn |
| Prompt cache | Shared system/safety prefix per model |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 10M | 100M | 1B | multi-B |
| Concurrent streams | 100K | 1M | 10M | 100M |
| Turns/day | 100M | 1B | 10B | 100B |
| Avg thread length (turns) | 20 | 30 | 40 | 50 |
| Long-tail threads (turns) | 1K | 1K–5K | 10K | 10K+ |
| Context pack CPU QPS | ~turn rate | ×10 | cells | many cells |
| Summary jobs/day | 5M | 50M | 500M | 5B |
| Thread retrieval QPS | 50K | 500K | 5M | 50M |
| Peak out tokens/s | 1M | 10M | 100M | 1B |

**What each jump forces:**

- **10×:** Dedicated pack service; Redis checkpoints; async summary workers.
- **100×:** User home cells; per-thread memory indexes; prefix cache discipline.
- **1,000×:** Aggressive hierarchical memory; cold item tiering; retrieval-first packing.

### 1.5 Etc. (Constraints & Assumptions)

- Thread product is a **client of Inference Gateway** + safety + optional tools.
- **Do not silently rewrite user text**; compaction inserts disclosed summary items.
- Progressive scale stress: **concurrent streams + tokens + long-thread pack cost**.

**Scope statement:**

> Design a multi-question LLM thread system: durable DAG conversations with streamed turns, token-budgeted context packing using recent tail + hierarchical summaries + retrieval, concurrent leaf CAS, and cost-aware GPU use—scaling through 10× / 100× / 1,000× with home cells and async memory maintenance.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline peak | Store |
|-------|---------------|-------|
| Durable turn create | 5–15K/s | Postgres |
| Context pack | ~turn admit rate | Pack service CPU |
| Inference streams | 100K concurrent | GPU |
| Redis checkpoints | 50–200K/s | Redis |
| Summary jobs | ~async fraction | GPU/CPU batch |
| Thread retrieval | 50K/s | ANN/keyword per cell |
| Safety classify | ×k turn rate | Fleet |

### 2.2 Token budget example

```text
Model context: 200K tokens
Reserve:
  system+safety: 3K
  tools schemas: 2K
  output reserve: 4K
  working budget: 191K

Pack priority:
  1. Active user question + recent N turns (tail) ~20K
  2. Retrieved chunks ~10–30K
  3. Hierarchical summaries covering older history ~10–40K
  4. Optional files excerpts
Never exceed working budget; drop from lowest priority first
```

### 2.3 Cost of naive full history

```text
1000-turn thread × 500 tokens/turn = 500K > context
Even 200 turns × 800 tokens = 160K — burns budget + $
Summarize+retrieve aims for ~O(log T) or O(constant) tokens for old history
```

### 2.4 Summary job rate

```text
If 10% of turns trigger compact: 10M turns/day → 1M summary jobs
Batch summaries with prompt cache on rubric; cheaper model for L1 summaries
```

### 2.5 Concurrent edit rate

```text
Small fraction of turns; still must be correct
CAS on leaf is cheap Postgres update; conflicts return 409
```

---

## 3. High-Level Design

### 3.1 UX wireframe

```text
+---------------------------------------------------------------------+
| Thread: “Migrating billing service”            [Model ▾] [Share]    |
+---------------------------------------------------------------------+
| Q1: Outline the migration steps...                                  |
| A1: ...                                                             |
| ...                                                                 |
| [System: Compacted turns 1–40 into summary S3 — show]               |
| Q87: What did we decide about dual-writes?                          |
| A87: ▍ streaming...                                                 |
|                                                                     |
| [ Ask follow-up...                              ] [Stop] [Send]     |
+---------------------------------------------------------------------+
| Conflict toast: “Thread updated elsewhere — reload” (on 409)        |
+---------------------------------------------------------------------+
```

### 3.2 Domain model

```text
User
 └── Thread
       ├── leaf_item_id
       ├── Item[] DAG
       │     types: user | assistant | tool_call | tool_result
       │            | summary | system_visible_notice
       ├── Turn/Run[]
       │     expected_leaf_id, status, model_version,
       │     context_manifest, safety_outcome, usage
       └── ThreadMemoryIndex (chunks of items + embeddings)
```

**Run state machine:**

```text
created → packing → admitted → in_progress
                                ├→ completed
                                ├→ incomplete
                                ├→ failed
                                ├→ cancelled
                                └→ refused
```

**Leaf CAS:**

```text
UPDATE threads SET leaf_item_id = $new, version = version+1
WHERE id = $t AND leaf_item_id = $expected AND version = $v
```

### 3.3 Context construction pipeline

```text
pack(thread, leaf, question):
  budget = Budget(model)
  take system+safety+tools
  take current question
  take recent tail until soft cap
  retrieve top-m chunks from ThreadMemoryIndex (exclude already in tail)
  take hierarchical summaries covering gaps
  if still over: drop retrieved lowest score → drop older tail → emergency summarize
  emit ContextManifest {item_ids, summary_ids, chunk_ids, token_counts}
  persist manifest on Run (reproducibility)
```

**Invariant:** packing is **deterministic given pinned inputs** (retriever ANN approximate—pin chunk ids after retrieval for the run).

### 3.4 Hierarchical summarization

```text
L0: raw items
L1: every ~10–20 turns → summary item (cheap model)
L2: summaries of L1 → higher summary
L3: thread abstract

Trigger: projected_tokens(tail+raw) > threshold OR scheduled
Summary item points to covered item_id range + branch id
Disclose via notice item or UI marker
Never delete raw until retention policy
```

### 3.5 Retrieval-augmented thread memory

```text
On item finalize → chunk → embed → upsert thread index
Query: embed(question + optional hints) → top-m within thread_id
Filter by branch visibility (ancestor set from leaf)
Hybrid: BM25 on thread text for IDs/errors
```

**Branch visibility:** only items on path from root → leaf (plus summaries covering that path).

### 3.6 Concurrent updates

| Scenario | Behavior |
|----------|----------|
| Two sends on same leaf | One CAS wins; loser 409 |
| Send vs edit | Same CAS |
| Summarizer commits summary | Additive item; doesn’t move leaf unless policy; runs pin IDs |
| Streaming + second send | Block or queue per thread mutex/lease |

**Thread lease (optional):** short exclusive lease for in_progress run to reduce races; still CAS on commit.

### 3.7 Streaming ownership

| | Option A | Option B |
|---|----------|----------|
| MVP | BFF holds stream; Redis checkpoint | Run worker + replay |
| Disconnect | Incomplete + retry | Resume after_sequence |

**Choice:** MVP A; durable user question first.

### 3.8 Safety & prompt layers

```text
Assemble:
  platform system/safety (hidden)
  user custom instructions (no silent edit)
  summaries + retrieved (untrusted-ish historical)
  recent turns
  current user question
Classifiers on input and streamed output
History injection: treat retrieved/summary as data
```

### 3.9 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/threads` | Create |
| POST | `/threads/{id}/turns` | Atomic turn + stream |
| GET | `/threads/{id}/items` | Page history |
| POST | `/threads/{id}/items/{id}/edit` | Branch |
| POST | `/turns/{id}/cancel` | Stop |
| GET | `/turns/{id}/events` | Resume Phase 2 |

```http
POST /threads/{id}/turns
Idempotency-Key: ...
{
  "expected_leaf_id": "item_...",
  "input": [{"role":"user","content":[{"type":"text","text":"Q?"}]}],
  "stream": true
}
```

409 body includes current `leaf_item_id` for client refresh.

### 3.10 Trade-offs

| Area | Options | Choice |
|------|---------|--------|
| Compaction | Sync blocking vs async | Async preferred; sync emergency |
| Memory index | Per-thread vs user-global | Per-thread MVP |
| Conflict | OT/CRDT vs CAS leaf | **CAS leaf** MVP |
| Summary model | Same as chat vs small | Small for L1 |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+----------+    +------------------+    +--------------------+
| Clients  |--->| Edge / Stream GW |--->| Thread API         |
+----------+    +--------+---------+    +---------+----------+
                         |                        |
                         |                        v
                         |               +--------+----------+
                         |               | Thread Service    |
                         |               | (home cell PG)    |
                         |               +--------+----------+
                         |                        |
                         v                        v
                +----------------+       +--------+----------+
                | Run Orchestrator|------| Redis checkpoints |
                +--------+-------+       | + leases/quotas   |
                         |               +-------------------+
         +---------------+---------------+------------------+
         v               v               v                  v
+--------------+ +--------------+ +--------------+ +---------------+
| Context Pack | | Safety Fleet | | Inference GW | | Memory Index  |
| Service      | |              | | + PromptCache| | (thread ANN)  |
+------+-------+ +--------------+ +--------------+ +-------+-------+
       |                                                   ^
       v                                                   |
+--------------+                                   +-------+-------+
| Summary      |---------------------------------->| Chunk/Embed   |
| Workers      |                                   | on finalize   |
+--------------+                                   +---------------+
```

### 4.2 Pack data flow

```text
Run created (leaf CAS reserved)
  → Pack(manifest)
  → Safety input
  → Admit inference
  → Stream + checkpoint
  → Finalize assistant item
  → Advance leaf CAS
  → Enqueue memory index + maybe summarize
```

### 4.3 Branching

```text
Root
 ├─ U1─A1─U2─A2─U3─A3   ← leaf L
 └─ (edit U2')─A2'─...  ← new branch leaf L'
Summaries tagged with branch coverage
```

---

## 5. Design Deep Dive

### 5.1 Reliability

| Failure | Mitigation |
|---------|------------|
| Crash after user durable before stream | Run incomplete; retry |
| Pack service timeout | Fail turn; user retry; no leaf advance |
| Summary wrong | Raw retained; user can expand; re-summary job |
| CAS lost updates | Impossible for leaf; 409 |
| Duplicate Idempotency-Key | Same turn returned |
| Memory index lag | Retrieve slightly stale; tail still exact |

**Reproducibility:** store `ContextManifest` on each run.

### 5.2 Scalability

- **Home cell by user_id** for thread metadata.
- Cold threads: items in object store segments; hot in PG.
- Memory index per cell; shard by `thread_id`.
- Prefix cache for system/safety across turns.
- Summary workers on batch/spot pools; interactive turns on reserved GPUs.

**100×:** pack service autoscaling; hierarchical memory default for long threads.  
**1,000×:** retrieval-first packing; multi-level summaries mandatory; retention.

### 5.3 Maintainability

- Pack policy as versioned config (`pack_policy_vN` pinned on run).
- Feature flags for retrieval on/off.
- Offline eval: “question about turn k” accuracy with/without retrieval.
- Clear metrics: tokens_packed, drop_reasons, conflict_rate, summary_lag.

### 5.4 Token budgeter detail

```text
class Budget:
  hard_max, reserves, priorities[]

allocate():
  for lane in priorities:
    fill lane until lane_cap or budget left
  while over_hard:
    drop from drop_order
  assert total <= hard_max
```

Lanes example: `safety`, `tail`, `retrieval`, `summaries`, `files`.

### 5.5 Hierarchical summary algorithms

| Strategy | Notes |
|----------|-------|
| Fixed window | Simple; map-reduce summaries |
| Token-triggered | When raw > T |
| Semantic clustering | Group related turns; better but complex |
| Incremental | Update rolling summary each turn (risk drift) |

**Choice:** fixed hierarchical windows + disclosure; rolling summary only as L3 abstract with periodic rebuild.

### 5.6 Concurrent summary vs turns

```text
Summaries are append-only items with {covers: [start,end], branch_head}
Pack selects latest summaries that cover gaps and are ancestors-compatible
If overlap conflict, prefer finer L1 over stale L2
```

### 5.7 CAS leaf protocol (full)

```text
Begin TX:
  read thread.leaf, version
  if leaf != expected: abort 409
  insert user item parent=leaf
  insert run + assistant placeholder
  insert outbox
  update leaf = assistant_placeholder OR update leaf only on finalize
Commit
```

**Two schools:**

- **A:** leaf advances to user item at create; assistant fills.  
- **B:** leaf advances only on terminal assistant.  

Pick one; document. Prefer **advance on create with placeholder** so concurrent sends conflict early—or lease.

### 5.8 Streaming checkpoints

```text
Every ~1s or N tokens: Redis SET turn:{id}:partial
Finalize: write full assistant item to PG; delete partial
Client retry: show partial + continue/regenerate
```

### 5.9 Safety specifics for long threads

- Re-classify current input every turn; don’t trust old allow.
- Summaries might omit safety-relevant nuance—**don’t summarize away refusals** incorrectly; keep refusal items in tail longer.
- Retrieved old jailbreak attempts shouldn’t weaken policy (platform layers win).

### 5.10 Cost & GPU efficiency

| Lever | How |
|-------|-----|
| Prefix cache | Stable system/safety/tools |
| Smaller summary model | L1/L2 compaction |
| Retrieve not replay | O(m) chunks vs O(T) turns |
| Cap max_output | Bound |
| Degrade model under load | Router |
| Batch summary jobs | Throughput |

---

## 6. Wrap-Up

### 6.1 What we designed

A **multi-question LLM thread** system: DAG-ordered durable turns with streaming, **token-budgeted packing** (tail + hierarchical summaries + thread retrieval), **leaf CAS** for concurrent tabs, async memory indexing, and GPU-aware inference—without silent user-text mutation.

### 6.2 Progressive scale

| Scale | Change |
|-------|--------|
| Baseline | PG + pack + Redis + async summaries |
| 10× | Dedicated pack/memory; prompt cache |
| 100× | Home cells; cold tier; stronger hierarchy |
| 1,000× | Retrieval-first; retention; many cells |

### 6.3 Deal-breakers

1. Exceeding context hard max.  
2. Silent rewrite of user messages.  
3. Lost updates without CAS/409.  
4. RAG/memory crossing threads/users.  
5. Summaries deleting raw without retention policy.  
6. Packing nondeterminism without pinned manifest.

### 6.4 Closing line

> Pack a budgeted context from recent tail, summaries, and retrieved thread memory; pin what you used; CAS the leaf so concurrent questions don’t clobber each other.

---

## 7. Deeper / Related Interview Questions

### 7.1 Why not always send full history?

**A:** Exceeds context, costs $, hurts quality with noise. Summarize + retrieve.

### 7.2 How do you avoid summary drift?

**A:** Hierarchy with periodic rebuild; keep raw; pin summary ids on runs; eval factuality of summaries.

### 7.3 CAS vs CRDT for chats?

**A:** Chat is usually single-writer UX; CAS leaf is simpler and matches product. CRDT overkill for MVP.

### 7.4 What goes in ContextManifest?

**A:** Policy version, item ids, summary ids, retrieved chunk ids, token counts per lane, model version.

### 7.5 Retrieval across branches?

**A:** Filter to ancestor path from current leaf; don’t leak parallel branch secrets into context.

### 7.6 Sync vs async compaction?

**A:** Async for UX; sync emergency only when otherwise can’t pack. Disclose both.

### 7.7 How to handle 10K-turn threads?

**A:** Deep hierarchy, retrieval-first, cold storage, maybe archive cutoffs with user notice.

### 7.8 Idempotency vs CAS?

**A:** Idempotency dedupes retries of same request; CAS serializes distinct concurrent updates.

### 7.9 Where do tool results live in budget?

**A:** Tail if recent; else retrieve truncated; full blob in object store.

### 7.10 Prompt caching interaction?

**A:** Keep system/safety/tools stable at prefix; put dynamic pack after breakpoint.

### 7.11 What if retriever misses the key fact?

**A:** Hybrid BM25; user pin/quote; expand m; offline eval; keep longer tail for recent topics.

### 7.12 Streaming safety with long context?

**A:** Same lag-buffer classifiers; cost grows with output not input primarily for stream checks.

### 7.13 Multi-user collaboration?

**A:** Out of MVP; would need presence, richer OT, ACLs—much harder than leaf CAS.

### 7.14 Regenerate semantics?

**A:** New run from same parent user item; may replace leaf or fork per product; CAS accordingly.

### 7.15 Should summaries be editable?

**A:** Prefer regenerate summary job; user edits create notice but careful—usually platform-owned with disclosure.

### 7.16 Home cell benefits?

**A:** Single-writer affinity for thread rows; simpler CAS; lower cross-region latency.

### 7.17 Measuring pack quality?

**A:** Tokens used, drop rates, human ratings on long-thread tasks, needle-in-haystack tests.

### 7.18 Failure during leaf advance after stream?

**A:** Reconcile job: if assistant complete but leaf stale, CAS forward; idempotent finalize.

### 7.19 PII in summaries?

**A:** Summaries inherit sensitivity; same ACL as thread; retention policies apply.

### 7.20 Output token reserve why?

**A:** Prevent prefill packing that leaves zero room to generate; hard reserve.

### 7.21 Can pack be cached?

**A:** Partially: for same leaf+question hash rare; usually new each turn. Cache embeddings of items heavily.

### 7.22 Model version change mid-thread?

**A:** Allowed; each run pins version; summaries still usable as text.

### 7.23 How do you test CAS?

**A:** Concurrent send load tests; expect one 200-stream and rest 409; no duplicate leaf children races.

### 7.24 Emergency summarize latency?

**A:** Use small model; summarize only oldest raw; timeout → drop with notice “limited history”.

### 7.25 Thread memory vs product Memory?

**A:** Thread memory is local RAG over this conversation. Product Memory is user-curated cross-thread facts—separate consent.

### 7.26 Cost blowup from retrieval+tail overlap?

**A:** Dedup by item_id; exclude tail from retriever results.

### 7.27 Stop button?

**A:** Cancel inference; finalize partial; leaf policy explicit (keep partial as leaf or not).

### 7.28 Quota reservation?

**A:** Reserve on admit after pack estimates tokens; settle on terminal with actual usage.

### 7.29 Why disclose compaction?

**A:** Trust; debugging; Anthropic-leaning honesty UX—users should know history was compacted.

### 7.30 One-liner

**A:** Budgeted pack = tail + summaries + retrieve; pin manifest; CAS leaf; stream with checkpoints.

### 7.31 DAG storage in Postgres?

**A:** Items table with parent_id; indexes (thread_id, created); path materialization optional.

### 7.32 Pagination of huge threads?

**A:** Keyset pagination; don’t load full DAG to client; fetch window around leaf.

### 7.33 Embedding privacy?

**A:** Thread-scoped index; encrypt at rest; delete on thread delete.

### 7.34 When to skip retrieval?

**A:** Short threads; pack_policy says off; latency overload; question is pure chitchat classifier.

### 7.35 Interaction with eval platform?

**A:** Long-thread eval suites measure needle recall after compaction—ship gates for pack_policy changes.

### 7.36 Fairness under load?

**A:** Per-tier concurrent stream limits; summary backlog deprioritized vs interactive.

### 7.37 Partial tool loops in context?

**A:** Include truncated tool_call/result pairs needed for coherence; cap steps.

### 7.38 Clock skew and summary covers?

**A:** Cover by item sequence numbers not wall clock.

### 7.39 Client optimistic UI?

**A:** Show pending; reconcile on 409; don’t invent assistant text client-side.

### 7.40 Whiteboard checklist

1. Thread/Item/Run + leaf CAS  
2. Token budget lanes  
3. Hierarchical summaries disclosed  
4. Thread retrieval + branch filter  
5. ContextManifest pin  
6. Stream Option A/B  
7. Safety layers  
8. Scale 10×/100×/1,000×  

---

## Appendix A: Pack policy YAML (illustrative)

```yaml
pack_policy_v3:
  context_limit: 200000
  reserves: {system: 3000, tools: 2000, output: 4000}
  lanes:
    - {name: tail, cap: 24000}
    - {name: retrieval, cap: 24000, min_score: 0.25}
    - {name: summaries, cap: 32000}
    - {name: files, cap: 8000}
  drop_order: [files, retrieval, summaries, tail]
```

## Appendix B: ContextManifest schema

```json
{
  "pack_policy": "v3",
  "model_version": "claude-X",
  "token_counts": {"system": 2800, "tail": 18000, "retrieval": 12000, "summaries": 9000},
  "item_ids": ["..."],
  "summary_ids": ["..."],
  "chunk_ids": ["..."],
  "dropped": [{"lane": "retrieval", "reason": "budget"}]
}
```

## Appendix C: Leaf CAS SQL sketch

```sql
UPDATE threads
SET leaf_item_id = $new_leaf, version = version + 1, updated_at = now()
WHERE thread_id = $tid AND leaf_item_id = $expected AND version = $ver;
-- rowcount 0 => 409
```

## Appendix D: Summary item payload

```json
{
  "type": "summary",
  "level": 1,
  "covers": {"from_seq": 120, "to_seq": 139},
  "branch_key": "...",
  "text": "...",
  "model_version": "summarizer-S",
  "disclosure": true
}
```

## Appendix E: Conflict response

```json
{
  "error": "leaf_conflict",
  "current_leaf_item_id": "item_...",
  "version": 46
}
```

## Appendix F: Memory index record

```text
chunk_id, thread_id, item_id, seq, branch_key, text, embedding, embed_ver
```

## Appendix G: Metrics

| Metric | Why |
|--------|-----|
| `pack_tokens` | Cost/quality |
| `pack_drop_total` | Pressure |
| `leaf_conflict_total` | UX races |
| `summary_lag_ms` | Memory freshness |
| `retrieve_hit_useful_rate` | Eval proxy |
| `ttft_ms` | UX |

## Appendix H: State machine (client)

```text
Idle → Sending → Streaming → Idle
                 ↘ ConflictRefresh
                 ↘ IncompleteRetry
                 ↘ Refused
```

## Appendix I: Emergency pack

```text
if pack fails budget even after drops:
  try sync_summarize_oldest(window)
  if still fail: truncate tail hardest + notice "limited history"
  never call inference over limit
```

## Appendix J: Retention

| Data | Hot | Cold | Delete |
|------|-----|------|--------|
| Items | 90d active | object archive | user/policy |
| Embeddings | with thread | rebuildable | with thread |
| Partials Redis | minutes | — | on finalize |

## Appendix K: Failure injection

| Chaos | Expect |
|-------|--------|
| Kill stream GW | incomplete + retry |
| Pack timeout | no leaf lie |
| Dual send | one win |
| Summary poison | quarantine; raw OK |
| ANN down | tail+summaries only |

## Appendix L: Branch visibility algorithm

```text
path = ancestors(leaf)
visible = items in path ∪ summaries whose covers ⊆ path seqs
retrieve only from visible
```

## Appendix M: Quota settle

```text
reserve(estimate_pack + max_out)
settle(actual_usage)
sweeper releases expired reserves
```

## Appendix N: Interview “honesty” lines

- Compaction disclosed  
- No silent user rewrite  
- Manifest pinned  
- 409 on conflict  
- Fail closed on over-context  

## Appendix O: Closing capacity note

```text
Long threads shift load from GPU prefill of raw history
  → CPU/ANN retrieval + cheap summarizer GPUs
That's the architectural win—say it explicitly
```

---

*End of document — Multi-Question LLM Thread (Anthropic interview prep)*
