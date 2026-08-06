# System Design: Chatbot Service (Multiple Information Kinds)

> **Focus areas:** Multi-intent routing · RAG over heterogeneous corpora · Tool / API orchestration · Streaming responses · Session & context · Guardrails · Human handoff · Multi-tenant knowledge · Observability  
> **Style:** NVIDIA-flavored enterprise chatbot interview — progressive scale on users / sessions / QPS / corpus size (10× → 100× → 1,000×)  
> **Quality bar:** Split control-plane vs retrieval vs inference vs stream fan-out; honest token/latency arithmetic; resolved ownership of “who answers what” vs generic LLM; guardrails as first-class paths

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

Goal: **bound the chatbot product**—what “multiple kinds of information” means (support, docs, HR, product status, sales), who uses it, how answers are grounded, and which safety / tenancy constraints are non-negotiable for an NVIDIA-style internal + external assistant.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Multi-source chatbot platform with routing, RAG, tools, streaming | Full foundation-model training cluster (see distributed training doc) |
| Surfaces | Web widget, Slack/Teams, developer portal, mobile | Single-purpose FAQ page with static answers only |
| Knowledge | Heterogeneous: docs, tickets, HR policy, GPU status, product catalog | One monolithic wiki dump without ACL |
| Inference | Calls GPU inference fleet / managed LLM APIs | Building a new 70B model from scratch in interview |
| NVIDIA lens | Developer + customer support for GPUs, CUDA, drivers, cloud | Consumer social chat product |

**Scope statement:**

> Design a chatbot service that accepts natural-language questions, classifies intent, retrieves from the right knowledge domain (with ACL), optionally calls tools/APIs, streams grounded answers, escalates to humans when needed, and scales from thousands to millions of daily sessions without cross-tenant leakage or “one RAG blob fits all.”

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are users? | External customers, developers, internal employees, partners | Multi-tenant auth; role-based corpus access |
| F2 | Information kinds? | Product docs, driver/CUDA support, order/status, HR/IT policy, sales SKU fit, incident status | Intent router + domain-specific retrievers/tools |
| F3 | Grounding required? | Yes for factual/support; optional for chitchat | RAG pipeline per domain; citation policy |
| F4 | Real-time data? | Order status, ticket lookup, GPU cloud capacity, incident feed | Tool/API layer; not only static index |
| F5 | Streaming? | Yes — token stream to UI | SSE/WebSocket gateway; TTFT SLO |
| F6 | Session memory? | Short-term conversation context; optional long-term prefs | Session store + summarization policy |
| F7 | Human handoff? | Escalate low-confidence / angry user / billing dispute | Queue to agent desk with transcript |
| F8 | Languages? | English MVP; i18n later | Locale in routing; translated corpora optional |
| F9 | Feedback? | Thumbs up/down, “was this helpful?”, report hallucination | Feedback loop → eval + reindex queue |
| F10 | Admin? | Curate corpora, tune prompts, view analytics, block topics | Admin console + config versioning |
| F11 | Channels? | Web, Slack, Teams, API for partners | Channel adapters normalize to core API |
| F12 | Compliance? | PII redaction, audit for HR/legal, no training on customer data without consent | Logging tiers; DLP hooks |

**MVP functional scope (lock with interviewer):**

1. Authenticated chat API (user + tenant + roles).  
2. **Intent classification** → route to domain handler (docs / support / HR / status / sales).  
3. **RAG** over at least two corpora with ACL (e.g., public developer docs + internal HR for employees only).  
4. **Tool calls** for live data (ticket status, order lookup stub).  
5. **Streaming** completion with citations where policy requires.  
6. Confidence / policy gates → **human handoff** queue.  
7. Session context (last N turns + rolling summary).  
8. Feedback capture + basic analytics (deflection, CSAT proxy).  
9. Guardrails: block jailbreak patterns, PII outbound filter, topic denylist.

**Out of MVP:**

- Fully autonomous multi-agent research loops  
- Perfect cross-language parity on day one  
- Automatic fine-tuning pipeline from every chat (mention as evolution)  
- Voice/telephony IVR (adapter hook only)  
- Proactive outbound notifications product  
- Customer-managed encryption keys deep dive

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | TTFT (time to first token) | Interactive chat feel | p50 < 800ms, p99 < 3s (excl. heavy tool chains) |
| N2 | End-to-end latency | Short answers common | p50 < 4s for ~200 output tokens |
| N3 | Availability | Business-hours critical for support | 99.9% API; degrade to search-only before hard fail |
| N4 | Correctness / grounding | No fabricated driver versions | Citations required for support answers; abstain if low retrieval score |
| N5 | Isolation | No cross-tenant doc leakage | Tenant + role filter at retrieval, not post-hoc |
| N6 | Durability | Sessions recoverable; audit where required | Session RPO ≈ 0; audit per policy |
| N7 | Cost | GPU inference is scarce | Cache, route small talk to cheap model, cap context |
| N8 | Scale | See progressive table | Split admit / retrieve / infer / stream planes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Developer asks “How do I enable MIG on A100?” → intent=docs → retrieve CUDA docs → stream answer with doc links.  
2. Customer asks “Where is order #12345?” → intent=order_status → tool call Order API → stream status + ETA.  
3. Employee asks PTO policy → intent=HR → ACL check employee → retrieve HR handbook chunk → cite section.  
4. User asks recommended GPU for LLM inference → intent=sales → retrieve SKU matrix + tool pricing → comparative answer.  
5. Incident question “Is NVLink down in us-west?” → intent=status → StatusPage API → factual banner-style answer.  
6. Multi-turn: user clarifies GPU model → session context preserved → refined retrieval.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Low retrieval score | Abstain template + offer human / search links; don’t invent |
| ACL denies corpus | Never retrieve; respond “I can’t access that”; log attempt |
| Tool timeout | Partial answer from static docs + “live status unavailable” |
| Prompt injection in pasted log | Treat user content as untrusted; system prompt isolation |
| User requests other tenant’s data | AuthZ fail closed at tool layer |
| HR legal hold content | Corpus flag excludes from RAG; handoff only |
| Stream client disconnect | Continue generation optionally; store full reply in session |
| Duplicate message (mobile retry) | Idempotency-Key → same response replay |
| Model hallucination despite RAG | Citation-required mode; eval alerts on mismatch |
| Anger / abuse detection | De-escalation template + optional human queue |
| Stale index (doc updated yesterday) | Version tags in chunks; freshness signal in prompt |
| GPU inference queue full | Queue with deadline; fallback smaller model + banner |

### 1.4 Scales (Progressive)

Progressive axes: **DAU / concurrent sessions / messages per day / corpus chunks / retrieval QPS**.

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 50K | 500K | 5M | 50M |
| Peak concurrent sessions | 5K | 50K | 500K | 5M |
| Messages / day | 500K | 5M | 50M | 500M |
| Peak message QPS | ~50 | ~500 | ~5K | ~50K |
| Distinct corpora / domains | 6 | 12 | 30 | 100+ |
| Indexed chunks (total) | 5M | 50M | 500M | 5B |
| Embedding index size | ~30 GB | ~300 GB | ~3 TB | ~30 TB |
| Avg context tokens / turn | 4K | 6K | 8K | 8K (cap) |
| Avg output tokens / turn | 250 | 300 | 350 | 400 |
| Human handoff rate | 8% | 6% | 5% | 4% (better routing) |
| Tool calls / day | 50K | 500K | 5M | 50M |
| Feedback events / day | 100K | 1M | 10M | 100M |
| Tenants / orgs | 500 | 5K | 50K | 500K |

**What each jump forces:**

- **10×:** Dedicated retrieval tier; intent model serving; session store sharding; citation cache.  
- **100×:** Domain-specific index partitions; hierarchical routing; async index pipeline; multi-model routing.  
- **1,000×:** Regional cells; approximate retrieval + rerank farms; aggressive prompt/context compression; eval at scale.

### 1.5 Etc. (Constraints & Assumptions)

- LLM inference runs on **NVIDIA GPU fleet** or approved vendor API; this design owns orchestration, not pretraining.  
- Corpora include **public docs**, **licensed partner content**, and **internal restricted** — ACL is non-negotiable.  
- “Multiple information kinds” means **different retrieval strategies and tools**, not one prompt pretending to know everything.  
- Human agents use separate CRM/desk product; we integrate via webhook + transcript bundle.  
- Answers default to **English**; i18n adds parallel indexes, not inline translate-everything.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| **Ingress / auth** | ~50 msg/s | ~50K/s | API gateway |
| **Intent + routing** | ~50/s | ~50K/s | Small classifier + rules |
| **Retrieval** | ~150/s (×3 domains avg) | ~150K/s | Vector + keyword |
| **LLM prefill + decode** | ~50 turns/s | ~50K/s | GPU bound |
| **Tool calls** | ~5/s | ~5K/s | Sync blocking risk |
| **Stream fan-out** | ~50K events/s | ~50M/s | SSE chunks |
| **Session R/W** | ~100/s | ~100K/s | Hot KV |
| **Index ingest** | batch | continuous | Offline from chat path |

**Deal-breaker:** treating “chat QPS” as only HTTP POST rate—each message may trigger retrieval, 1–3 tool calls, and thousands of decode tokens.

### 2.2 Token arithmetic (per turn)

```text
Typical turn:
  system + policy prompt     ~800 tokens
  retrieved chunks (top-k)   ~1500 tokens (3×500)
  session summary + last turns ~1200 tokens
  user message               ~200 tokens
  ─────────────────────────────────────
  input ≈ 3.7K tokens

Output target ≈ 250 tokens

At 50 msg/s baseline:
  input  ≈ 185K tok/s prefill
  output ≈ 12.5K tok/s decode

If effective H100-class throughput ≈ 3K output tok/s/GPU (SKU + model dependent, be honest):
  decode GPUs ≈ 12.5K / 3K ≈ 5 GPUs continuous (plus prefill headroom)

Always separate prefill burst from sustained decode — TTFT sensitive to prefill queue.
```

### 2.3 Retrieval math

```text
5M chunks × 768-dim × 4 B ≈ 15 GB vectors (raw)
+ metadata + HNSW graph overhead → ~25–40 GB index (baseline)

50M chunks (10×) → ~250–400 GB → shard by domain/tenant

Retrieval QPS 150/s × 3 indexes avg = 450 vector queries/s baseline
At 100×: 45K vector QPS → dedicated retrieval cluster, batch where possible

Keyword/BM25 side index adds ~20–40% storage; hybrid improves support queries.
```

### 2.4 Session store

```text
5K concurrent sessions × 32 KB state ≈ 160 MB (negligible baseline)
500K concurrent (100×) × 32 KB ≈ 16 GB → Redis cluster with TTL

Write amp: ~2 writes/turn (append message + update summary pointer)
50 turns/s → 100 W/s baseline; 50K W/s at 1000× → shard by session_id
```

### 2.5 Human handoff queue

```text
500K messages/day × 8% handoff = 40K tickets/day
Peak ÷ 86400 × 10 (burst) ≈ ~50/min baseline

Agent capacity ~8 chats/agent (async) → ~7 agents peak baseline
100× handoff volume → workforce planning + async email fallback
```

### 2.6 Storage (audit + feedback)

```text
If 20% conversations logged for quality:
  500K msgs/day × 20% × 4 KB ≈ 400 MB/day baseline
  100× → 40 GB/day → tiered object storage + PII scrub pipeline
```

### 2.7 Critical bottlenecks (rank ordered)

1. **Monolithic RAG** — wrong chunks → hallucination → support debt  
2. **Tool latency** chained serially — blows TTFT  
3. **GPU prefill queue** during traffic spikes  
4. **ACL applied after retrieval** — privacy incident  
5. **Unbounded session context** — cost + latency melt  
6. **No intent routing** — HR question hits public index only  
7. **Stream gateway as app server** — connection exhaustion at 100×  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
ConversationSession  → session_id, user, tenant, channel, state, summary
Message              → turn with role, text, attachments, idempotency_key
IntentRouter         → {domain, confidence, tools_allowed, model_tier}
DomainHandler        → strategy: RAG-only | tool-first | hybrid | deny
Retriever            → hybrid search w/ ACL filter pushed down
ToolExecutor         → typed APIs (orders, tickets, status, HRIS read)
PromptComposer       → system + domain + citations + session pack
InferenceGateway     → route to model pool; stream tokens
GuardrailService     → input/output policy, PII, jailbreak
HandoffService       → enqueue agent w/ transcript + retrieval trace
FeedbackCollector    → ratings → eval warehouse
IndexPipeline        → ingest, chunk, embed, ACL tag, publish version
```

**Message processing states:**

```text
RECEIVED → AUTHZ → ROUTED → RETRIEVING → (TOOLS?) → COMPOSING
    → INFERRING → GUARDRAIL → STREAMING → PERSISTED → (HANDOFF?)
```

### 3.2 Information domains (the “multiple kinds”)

| Domain | Primary source | Strategy | Example question |
|--------|----------------|----------|------------------|
| **Developer docs** | Public CUDA/driver docs index | RAG + cite | “Enable persistent mode?” |
| **Support KB** | Tickets + resolved articles | Hybrid RAG | “Error Xid 43 on install” |
| **Product / SKU** | Catalog + compatibility matrix | RAG + rules | “Best GPU for 70B inference?” |
| **Order / account** | Order API (live) | Tool-first | “Track order 12345” |
| **Incident / status** | Status page API | Tool-first | “Outage in eu-west?” |
| **HR / IT policy** | Internal corpus (employee ACL) | RAG strict cite | “Parental leave policy?” |
| **Sales** | Pricing + entitlement API | Tools + RAG | “Quote for 8×H100?” |
| **Chitchat / oos** | None | Small model / template | “Hello” |

**Invariant:** domain choice determines **which indexes and tools are even visible** to the composer.

### 3.3 Ownership & invariants

| Concern | Owner |
|---------|-------|
| User authN/authZ | API gateway + identity service |
| Intent label | IntentRouter (model + rules) |
| Corpus ACL | IndexPipeline tags; Retriever enforces |
| Grounding quality | DomainHandler + retrieval thresholds |
| Tool side effects | ToolExecutor with per-tool auth |
| Model selection | InferenceGateway policy |
| Session truth | Session service (SoT for turns) |
| Human queue | HandoffService → external desk |

**Invariants:**

1. **Retrieve-then-filter-ACL** at index partition level; defense in depth at chunk metadata.  
2. **No tool call** without domain permission and user scope token.  
3. **Citation-required domains** cannot stream final answer without source ids.  
4. **Idempotent** message accept on same idempotency key.  
5. **Session tenant** immutable; cross-tenant session access rejected.

### 3.4 Request path (logical)

```text
POST /v1/chat/sessions/{id}/messages
  1. AuthN/Z → tenant, roles, channel policy
  2. Load session + rolling summary
  3. Input guardrail (PII inbound, jailbreak)
  4. IntentRouter → domain + confidence
  5. DomainHandler:
       a. plan retrieval queries (multi-query optional)
       b. Retriever.hybrid(top_k, filters)
       c. optional ToolExecutor parallel/serial per plan
  6. PromptComposer pack context (truncate by priority)
  7. InferenceGateway.stream(model_tier)
  8. Output guardrail (PII, policy, citation check)
  9. Persist assistant message + retrieval trace
 10. if confidence low or user requested → HandoffService
 11. Stream to client (may start at step 7)
```

### 3.5 Retrieval design

```text
Per domain index partition:
  - chunk_id, text, embedding, source_uri, version, acl_tags[]
  - BM25 inverted index (same partition)

Hybrid score = α * cosine + (1-α) * bm25_norm
Rerank top-50 → top-5 with cross-encoder (optional at scale)

Freshness: boost recent version; stale chunks flagged in prompt
```

**Deal-breaker:** global single vector DB with post-filter ACL — slow and leaky under load.

### 3.6 Tool orchestration

| Pattern | When | Risk |
|---------|------|------|
| **Parallel** | Independent tools (status + SKU) | Higher tail latency |
| **Serial** | Output of A needed for B | TTFT stretch |
| **Speculative** | Predict tool need from intent | Wasted calls |
| **Cached** | Status/incident relatively stable | Stale data label |

MVP: intent plan declares tool DAG; max depth 2; global tool timeout 2s.

### 3.7 Model routing & degradation

| Tier | Use | Backend |
|------|-----|---------|
| **Fast** | Intent, chitchat, query rewrite | Small GPU model |
| **Standard** | Most RAG answers | Mid LLM |
| **Reasoning** | Complex multi-doc synthesis | Large LLM (queue) |

Degradation ladder:

```text
1. Increase queue → show wait estimate
2. Switch standard → fast with shorter context
3. Retrieval-only card + doc links (no gen)
4. Hard 503 with status page link
```

### 3.8 Session & memory

```text
Keep last K turns verbatim (K=6)
Older → rolling summary updated every M turns
Hard cap total context budget:
  priority drop order: old turns → optional tools debug → lower-ranked chunks

Long-term memory (stretch): user prefs store opt-in ("always show citations")
```

### 3.9 Human handoff

```text
Triggers:
  - user asks for agent
  - confidence < τ
  - negative sentiment + support domain
  - billing/dispute class
  - guardrail escalation

Payload:
  transcript, retrieval trace, tool results, user tier, suggested queue
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Routing | Intent model + rules | Explainable; fast | One mega-prompt |
| Retrieval | Hybrid per domain | Support queries need keywords | Vector-only |
| ACL | Partition + metadata | Safety + perf | Post-filter only |
| Inference | GPU pools by tier | Cost/latency | One huge model for all |
| Streaming | Dedicated gateway | Connection scale | Block on full completion |
| Grounding | Citations required (support) | Trust | Free-form hallucination |
| Tools | Typed OpenAPI executors | Auth scope | LLM writes SQL |
| Index updates | Blue/green version pointer | No half-old answers | In-place mutate |
| Eval | Offline golden + online feedback | Quality loop | Ship without metrics |

---

## 4. Architecture Diagram

### 4.1 End-to-end platform

```text
+----------+  +----------+  +----------+
| Web UI   |  | Slack    |  | Partner  |
| Widget   |  | Adapter  |  | API      |
+----+-----+  +----+-----+  +----+-----+
     |             |             |
     +-------------+-------------+
                   v
          +--------+---------+
          | Chat API Gateway |  auth, rate limit, idempotency
          +--------+---------+
                   |
     +-------------+-------------+
     v             v             v
+----+----+  +-----+-----+  +----+----+
| Session |  | Intent    |  | Guard   |
| Service |  | Router    |  | Rails   |
+----+----+  +-----+-----+  +----+----+
     |             |
     v             v
+----+-----------------------------------+
|           Orchestrator / Domain Bus     |
|  docs | support | hr | sales | status  |
+----+-------------+----------+----------+
     |             |          |
     v             v          v
+----+----+   +----+----+  +--+---+
|Retriever|   | Tool    |  |Handoff|
| Fleet   |   | Executor|  | Svc   |
+----+----+   +----+----+  +--+---+
     |             |
     v             v
+----+----+   +----+----+
| Vector  |   | Order/  |
| + BM25  |   | Ticket/ |
| Indexes |   | Status  |
+----+----+   +----+----+
     |
     v
+----+---------+     +------------------+
| Inference    |---->| Stream Gateway   |---- clients
| Gateway (GPU)|     | (SSE / WS)       |
+----+---------+     +------------------+
     |
     v
+----+---------+     +------------------+
| Feedback &   |---->| Eval / Analytics |
| Audit Store  |     | Warehouse        |
+--------------+     +------------------+
```

### 4.2 Index pipeline (offline)

```text
Source systems (docs git, CMS, tickets, HR PDF)
        │
        v
   Ingest + normalize (html/md/pdf)
        │
        v
   Chunker (heading-aware, max 512 tok)
        │
        v
   ACL tagger (tenant, role, sensitivity)
        │
        v
   Embedder batch job (GPU)
        │
        v
   Publish new index version (blue/green)
        │
        v
   Router picks version per domain
```

### 4.3 Sequence: support question with RAG

```text
User → Gateway → Session load → Router (support, 0.91)
  → Retriever hybrid (support_idx, acl=customer)
  → top chunks + scores
  → Composer builds prompt w/ cite ids
  → Inference stream begins (TTFT)
  → Guardrail checks outbound
  → Persist + Feedback hook
  → Client renders answer + links
```

### 4.4 Sequence: order status (tool-first)

```text
User → Router (order_status, 0.95)
  → ToolExecutor GET /orders/{id} (scoped OAuth)
  → Composer: tool JSON + short template
  → Inference paraphrase (optional) or template fill
  → Stream → Persist
```

### 4.5 Sequence: low confidence → handoff

```text
User → Router (support, 0.42)
  → Retriever low max score
  → Policy: no free generation
  → Offer buttons: agent / docs search
User picks agent
  → HandoffService enqueue + return queue position
  → Agent desk pulls bundle w/ trace
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | ACL before chunk exposure | Partition + metadata filter |
| R2 | Idempotent message accept | Idempotency-Key store |
| R3 | Citation domains blocked w/o sources | Output validator |
| R4 | Tool scope ⊆ user scope | Per-tool token exchange |
| R5 | Session tenant immutable | Session record check |
| R6 | Index reads version-pinned | Consistent snapshot per turn |

**Failure modes**

| Failure | Behavior |
|---------|----------|
| Retriever timeout | Retry once; degrade to keyword-only; abstain if empty |
| Inference GPU OOM | Retry smaller context; route fast tier |
| Tool 5xx | Partial answer + explicit unavailable |
| Stream disconnect | Complete persist; client poll session |
| Index version half-published | Traffic stays on old version until health OK |
| Router mislabel | Confidence threshold → clarify question or handoff |
| Guardrail false positive | User message + appeal path; log for tuning |

**Cancel / timeout**

- Client abort closes stream; server may cancel decode if supported.  
- Global turn deadline 30s default; tools capped at 2s each.

### 5.2 Scalability

| Scale | Architecture changes |
|-------|----------------------|
| 1× | Monolith OK with modular boundaries; single Redis; one GPU pool |
| 10× | Split retrieval + inference; shard sessions; domain index replicas |
| 100× | Regional cells; reranker farm; async ingest; intent cache |
| 1,000× | Hierarchical router; approx ANN + rerank; cell-local GPU; federated analytics |

**Retrieval scaling**

- Shard by `{domain, tenant_bucket}`  
- ANN parameters tuned per shard size  
- Hot query cache keyed by `(normalized_query, domain, acl_hash)` with short TTL  
- Avoid global k-NN at billions — partition first

**Inference scaling**

- Separate prefill and decode pools if framework supports  
- Queue admission by priority (paid support > free docs chat)  
- Batch prefill for non-stream batch jobs only — don’t batch interactive TTFT

**Stream scaling**

- Dedicated SSE/WS tier with sticky sessions  
- Backpressure: slow client → drop nonessential heartbeats, not tokens

### 5.3 Maintainability

- **Prompt templates versioned** per domain (`prompt_id@version` in logs).  
- **Golden eval sets** per domain updated on each index publish.  
- **Feature flags** for router models and retrieval α.  
- **Trace id** links: message → retrieval ids → tool calls → model version.  
- Chaos: kill retriever shard, stall tool, GPU drain, index rollback.

**Observability must-haves**

| Signal | Why |
|--------|-----|
| TTFT p50/p99 | User experience |
| Retrieval score distribution | Grounding health |
| Abstain / handoff rate | Router + RAG quality |
| Tool error rate | Integration health |
| Tokens in/out per domain | Cost allocation |
| Hallucination reports / thumbs down | Model drift |
| Index lag (source vs published) | Staleness |
| GPU queue depth | Capacity |

Cardinality policy: default **domain-level** dashboards; drill-down by tenant sampled.

### 5.4 Security & privacy

```text
Defense layers:
  1. AuthN at gateway (SSO / API keys)
  2. RBAC → allowed domains + tools
  3. Index ACL tags at ingest
  4. Retriever mandatory filter
  5. Tool OAuth on-behalf-of user
  6. Output DLP (PII, secrets)
  7. Audit tiers (HR/legal)

Prompt injection mitigations:
  - Separate system vs user channels in template
  - Retrieved text wrapped as untrusted quotes
  - Tool args validated against schema (no freeform shell)
  - Deny tools that mutate state without confirmation step
```

### 5.5 Quality & evaluation loop

```text
Offline (on index publish):
  - golden Q&A per domain → recall@k, citation match, LLM-judge score
  - regression gate blocks bad publishes

Online:
  - thumbs + explicit "wrong" reports
  - sample human review queue
  - drift detection on abstain rate spikes

Feedback → rechunk/reindex tickets, not instant fine-tune (usually)
```

### 5.6 Multi-channel adapters

| Channel | Nuances |
|---------|---------|
| Web | Full streaming + rich citations |
| Slack | Block kit; thread session mapping; shorten links |
| Teams | Similar; tenant mapping to Entra |
| Partner API | Stricter rate limits; JSON-only; no internal domains |

Adapter translates to canonical `Message` — orchestrator stays channel-agnostic.

### 5.7 Cost controls

```text
- Cap max retrieved tokens and output tokens per tier
- Cache frequent FAQ embeddings queries
- Route obvious FAQs to retrieval-only templates (no LLM)
- Summarize session aggressively for long threads
- Off-peak batch index embed jobs
```

---

## 6. Wrap-Up

### 6.1 MVP recap (say aloud)

> I’d build a multi-tenant chatbot with an intent router that sends each question to the right **domain handler**—docs, support KB, HR, live status, orders. Each domain has its own **ACL-bound index** and optional **tools**. Answers stream from a **tiered GPU inference gateway**, with **citations** for factual domains and **abstain + handoff** when retrieval confidence is low. Sessions stay in a hot store with rolling summarization; guardrails wrap input and output. Scale by splitting retrieval, inference, and stream planes, sharding indexes by domain, and regional cells at 100×+.

### 6.2 Key trade-offs revisited

| Decision | Upside | Downside |
|----------|--------|----------|
| Domain-specific indexes | ACL + relevance | More ops moving parts |
| Hybrid retrieval | Better support queries | Two systems to tune |
| Tool-first for live data | Freshness | Latency + auth complexity |
| Citation-required | Trust | UX friction |
| Fast/standard/reasoning tiers | Cost/latency | Routing mistakes visible |

### 6.3 Top risks

1. **ACL leak** via shared index  
2. **Hallucination** when retrieval weak  
3. **Tool latency** serial chains  
4. **Prompt injection** via pasted logs  
5. **GPU queue** meltdown without admission control  
6. **Index staleness** after driver release rush  

### 6.4 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Clarify information kinds, users, grounding, handoff |
| 5–12 | Domain router + ACL model |
| 12–22 | RAG + tools + sequence diagrams |
| 22–32 | Estimation: tokens, retrieval, GPUs |
| 32–40 | Failure modes, guardrails, scale 10×/100× |
| 40–45 | MVP scope + wrap |

### 6.5 Differentiators (NVIDIA context)

- Heavy **developer docs** + **driver error codes** corpus  
- **SKU / compatibility** questions need structured product data + RAG  
- **GPU cloud status** integrates with internal capacity/incident systems  
- Inference runs on **NVIDIA GPU fleet** — tie to distributed inference sibling doc  
- Partner/partitioned access to licensed content

---

## 7. Deeper / Related Interview Questions

### 7.1 Routing & domains

**Q: One model or many?**  
A: Router can be small classifier; generation uses tiered models. Don’t fine-tune 20 models day one—domain prompts + indexes first.

**Q: User asks cross-domain question?**  
A: Multi-intent detection → sequential or fused retrieval from allowed domains only; composer merges with section headers.

**Q: What if router wrong?**  
A: Low retrieval score triggers clarify (“Did you mean driver install or order status?”) or handoff.

### 7.2 RAG

**Q: Chunk size?**  
A: ~256–512 tokens for docs; heading-aware splits; overlap 10–15% for continuity.

**Q: Vector vs keyword?**  
A: Hybrid—support queries often exact error codes (`Xid 43`, `CUDA error 999`).

**Q: How prevent stale driver doc?**  
A: Version dimension on publish; boost latest; show doc date in citation.

**Q: Reranker worth it?**  
A: Yes at moderate scale for top-50→5; batched GPU reranker service.

### 7.3 Tools

**Q: LLM calls arbitrary URLs?**  
A: No—typed tools with schema, auth, timeouts, allowlist.

**Q: Confirm before destructive action?**  
A: Yes—two-step for refunds, account changes.

**Q: Tool result too large?**  
A: Summarize server-side; pass structured subset to LLM.

### 7.4 Sessions & memory

**Q: How long retain sessions?**  
A: Hot 24–72h; archived per compliance; PII scrub in archives.

**Q: Summarization hallucination?**  
A: Summarize from stored turns only; don’t invent; mark summary as machine-generated in prompt.

### 7.5 Streaming & latency

**Q: TTFT budget breakdown?**  
A: ~50ms gateway, ~30ms router, ~150ms retrieval, ~200ms prefill, rest decode—order of magnitude.

**Q: Stream before retrieval done?**  
A: Optional “Searching docs…” status events; don’t stream final answer until retrieval completes for cite domains.

### 7.6 Safety

**Q: Jailbreak “ignore instructions”?**  
A: Layered: classifier, system prompt isolation, output policy, rate limits.

**Q: PII in logs?**  
A: Redact at ingest to audit store; tokenize order ids in logs.

**Q: HR legal questions?**  
A: Cite-only + disclaimer; escalate to human for interpretation requests.

### 7.7 Scale

**Q: 5B chunks?**  
A: Partition by domain/tenant; ANN per partition; two-stage retrieve+rerank; don’t load one graph.

**Q: Cache answers?**  
A: Careful—only non-personalized FAQs with TTL; key includes acl_hash.

**Q: Embed ingest GPU needs?**  
A: Batch offline; 5M chunks × embed cost one-time; incremental delta pipeline.

### 7.8 Human handoff

**Q: Agents need copilot too?**  
A: Agent assist sidecar with same retrieval trace + suggested replies.

**Q: Queue SLA?**  
A: Product-specific; show ETA; async email fallback.

### 7.9 Comparison traps

**Q: Is this just ChatGPT wrapper?**  
A: No—domain routing, ACL indexes, tools, citations, handoff, eval are the product.

**Q: Why not fine-tune one model on everything?**  
A: ACL, freshness, live data, citeability—RAG+tools beat monolith for enterprise support.

**Q: Elasticsearch only?**  
A: Fine MVP hybrid; vectors help paraphrase; error codes need keyword.

### 7.10 NVIDIA-flavored variants

**Q: Internal CUDA compiler team bot?**  
A: Restricted index + symbol-aware chunking + link to Nsight docs.

**Q: Datacenter ops bot?**  
A: Tool-first on telemetry + runbooks; pair with GPU telemetry doc.

**Q: Sales configurator?**  
A: Rules engine for hard constraints (power, NVLink) + RAG for narratives.

### 7.11 Estimation traps

**Q: 500M messages/day → 500M LLM calls?**  
A: No—cache, retrieval-only paths, small model for intent/chitchat reduce expensive calls.

**Q: Ignore retrieval QPS?**  
A: Each message ≈ 1–3 vector queries + BM25—often 3× message QPS.

### 7.12 Reliability drills

**Q: Index rollback?**  
A: Blue/green pointer flip; messages pin version at turn start.

**Q: GPU region down?**  
A: Failover pool if data policy allows; else queue + degrade message.

**Q: Retriever returns empty?**  
A: Abstain—not general knowledge fill for support domains.

---

## 8. Appendices

### 8.1 Example schemas

```sql
CREATE TABLE chat_sessions (
  session_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID NOT NULL,
  channel TEXT NOT NULL,
  roles TEXT[] NOT NULL,
  summary TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE chat_messages (
  message_id UUID PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES chat_sessions(session_id),
  role TEXT NOT NULL, -- user|assistant|system|tool
  content TEXT NOT NULL,
  domain TEXT,
  retrieval_trace JSONB,
  tool_calls JSONB,
  model_version TEXT,
  feedback SMALLINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (session_id, idempotency_key)
);

CREATE TABLE index_versions (
  domain TEXT NOT NULL,
  version INT NOT NULL,
  status TEXT NOT NULL, -- building|active|retired
  chunk_count BIGINT NOT NULL,
  published_at TIMESTAMPTZ,
  PRIMARY KEY (domain, version)
);

CREATE TABLE handoff_tickets (
  ticket_id UUID PRIMARY KEY,
  session_id UUID NOT NULL,
  queue TEXT NOT NULL,
  reason TEXT NOT NULL,
  payload_uri TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 8.2 API sketch

```text
POST   /v1/chat/sessions
GET    /v1/chat/sessions/{id}
POST   /v1/chat/sessions/{id}/messages     # Idempotency-Key header
GET    /v1/chat/sessions/{id}/messages/{mid}/stream
POST   /v1/chat/sessions/{id}/feedback
POST   /v1/chat/sessions/{id}/handoff

Admin:
POST   /v1/admin/domains/{d}/index:publish
GET    /v1/admin/analytics/deflection
```

### 8.3 Example message JSON

```json
{
  "content": "I'm seeing CUDA error 999 on driver 550—what should I check?",
  "idempotency_key": "m-8f3a2c",
  "attachments": []
}
```

### 8.4 Retrieval trace example

```json
{
  "domain": "support_kb",
  "index_version": 42,
  "queries": ["CUDA error 999 driver 550", "error 999 unspecified"],
  "chunks": [
    {"chunk_id": "kb:8812", "score": 0.89, "source": "https://docs.nvidia.com/..."},
    {"chunk_id": "kb:1022", "score": 0.81, "source": "https://docs.nvidia.com/..."}
  ],
  "max_score": 0.89,
  "policy": "cite_required"
}
```

### 8.5 Prompt pack priority (truncation order)

```text
1. System + safety policy          (never drop)
2. Tool results (structured)       (truncate JSON fields)
3. Top retrieval chunks            (drop lowest score first)
4. Session summary
5. Recent turns                    (drop oldest)
6. User message                    (never drop)
```

### 8.6 Glossary

| Term | Meaning |
|------|---------|
| Domain | Information kind with handler + index + tools |
| RAG | Retrieval-augmented generation |
| TTFT | Time to first token |
| ACL | Access control on corpus chunks |
| Abstain | Refuse to generate without grounding |
| Handoff | Escalation to human agent |
| Hybrid retrieval | Vector + keyword fusion |
| Blue/green index | Atomic version switch for indexes |
| Idempotency-Key | Client retry deduplication |
| Deflection | Issues resolved without human agent |

### 8.7 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Router + 2 domains, hybrid RAG, stream, sessions, basic guardrails |
| 10× | Sharded indexes, retrieval tier, model tiers, handoff metrics |
| 100× | Regional cells, reranker, index pipeline automation, eval gates |
| 1,000× | Partitioned ANN fleet, admission control, analytics federation |

### 8.8 Estimation cheat-sheet

```text
input_tok ≈ system + chunks + session + user
output_tok ≈ 200–400 typical

GPU decode_need ≈ peak_output_tok_s / eff_tok_s_per_gpu
retrieval_QPS ≈ msg_QPS × domains_per_msg
index_GB ≈ chunks × (emb_dim×4 + overhead)

handoffs/day ≈ messages × handoff_rate
session_mem ≈ concurrent × 32 KB

Never use peak brochure TFLOPS for chat — measure tok/s
```

### 8.9 Domain handler pseudocode

```text
function handle(domain, session, user_msg):
  intent = router(user_msg, session)
  if intent.confidence < T_low:
    return clarify_or_handoff()

  plan = planner(domain, user_msg)
  chunks = []
  if plan.needs_retrieval:
    chunks = retriever.hybrid(plan.queries, acl=user.acl, k=5)

  tool_results = []
  for t in plan.tools_parallel:
    tool_results.append(tools.exec(t, user.scope))

  if domain.cite_required and chunks.max_score < T_ret:
    return abstain_with_links(chunks)

  prompt = composer.pack(session, chunks, tool_results, domain.template)
  stream = inference.stream(prompt, tier=domain.model_tier)
  return guardrail(stream)
```

### 8.10 Interview “say this” summary (60 seconds)

> Multi-kind chatbot means domain-specific routing—not one RAG blob. I classify intent, retrieve from ACL-partitioned indexes with hybrid search, call typed tools for live order or status data, and stream answers from tiered GPU models with citations on support content. Low confidence abstains or hands off to humans. Scale by sharding retrieval and sessions, separating stream gateways, and blue/green index publishes with offline eval gates.

### 8.11 Reliability test plan

1. User without HR role asks PTO → zero HR chunks retrieved.  
2. Same idempotency key twice → one assistant message.  
3. Retriever killed → abstain path, no hallucinated driver version.  
4. Tool timeout → partial template + clear error.  
5. Index publish regression → eval gate blocks promotion.  
6. Prompt injection block → policy response, no tool exfil.  

### 8.12 Related systems map

```text
Channel Adapters → Chat API → Orchestrator
                              ↓
            Retriever / Tools / Handoff / Guardrails
                              ↓
            Inference Gateway (GPU) → Stream Gateway
                              ↓
            Feedback → Eval / Analytics

Offline: Sources → Index Pipeline → Vector + BM25 partitions
```

### 8.13 Extra traps

| Trap | Pushback |
|------|----------|
| Single global embedding index | ACL leak + slow filters |
| LLM-only answers for support | Hallucinated driver steps |
| Unbounded context | Cost and latency explode |
| Sync tool chains deep >2 | TTFT unacceptable |
| Log full prompts always | PII/compliance violation |
| No abstain policy | Wrong confident answers |
| Fine-tune replaces RAG | Stale on day-one driver release |
| Ignore feedback loop | Quality drifts silently |

### 8.14 Observability SLOs

| SLO | Example target |
|-----|----------------|
| TTFT p99 | < 3s interactive |
| Retrieval p99 | < 300ms |
| Tool p99 | < 2s |
| Stream availability | 99.9% |
| Citation attach rate (support) | > 95% when answered |
| ACL denial audit | 100% logged |
| Index publish eval pass | 100% golden set |

### 8.15 Channel-specific session mapping

```text
Slack: session_key = (team_id, channel_id, thread_ts)
Teams: session_key = (tenant_id, conversation_id)
Web: session_key = session_id cookie / JWT
Partner API: session_key = client_provided (UUID) + tenant
```

### 8.16 Content sensitivity tiers

| Tier | Example | Logging | Retrieval |
|------|---------|---------|-----------|
| Public | CUDA docs | Standard | All users |
| Customer | Order data via tool | Redacted audit | Auth scoped |
| Internal | HR policy | Strict audit | Employee role |
| Restricted | Legal hold | No LLM log | Handoff only |

### 8.17 Future evolution (mention briefly)

- **Agentic** multi-step debugging with sandboxed repro runners (heavy governance)  
- **Personalization** from opt-in history embeddings  
- **On-device** small model for offline FAQ on edge devices  
- **Continuous eval** from production thumbs tied to index diffs  
- **Voice** channel with ASR/TTS adapters (same orchestrator)

---

*End of document.*
