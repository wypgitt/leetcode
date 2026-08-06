# System Design: LLM-Powered Enterprise Search

> **Focus areas:** Connectors · Parsing/chunking · Embeddings · Hybrid retrieval · ACL · Reranking · Citations · Freshness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, ACL as a deal-breaker, split ingest vs query load classes, honest MVP vs extreme-scale paths

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

Goal: **bound the product**—what enterprise search surface we build, what we defer, and at which scale ACL-safe hybrid RAG must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are the users? | Knowledge workers in mid/large enterprises; multi-tenant SaaS | Everything keyed by `tenant_id` from day 1; SSO/OIDC |
| F2 | What sources? | Google Drive, Slack, Confluence/Notion, GitHub, SharePoint; email Phase 2 | Pluggable **connectors** with incremental sync cursors |
| F3 | Search modes? | Keyword + semantic + hybrid; natural-language Q&A with citations | BM25 + vector + optional LLM answer over retrieved chunks |
| F4 | ACL model? | User must only see docs they can open in source systems | **ACL filter is a deal-breaker**; sync ACLs with docs |
| F5 | Answer UX? | Ranked hits + optional grounded answer with inline citations | Retrieval path ≠ generation path; citations mandatory if generating |
| F6 | Freshness? | New/edited docs searchable within minutes; deletes/ACL revoke ASAP | Incremental sync + near-real-time indexing; revoke path is urgent |
| F7 | Document types? | Docs, slides, PDFs, HTML, chat messages, code (optional) | Parser/chunker per MIME; OCR/table later |
| F8 | Admin surfaces? | Connector setup, sync status, index health, audit logs | Control plane separate from query path |
| F9 | Multilingual? | English MVP; others Phase 1.5 | Embedding model + analyzers that support expansion |
| F10 | Feedback? | Thumbs up/down, “wrong ACL”, “stale” | Offline eval + online signals; don’t block MVP |

**MVP functional scope (lock with interviewer):**

1. Multi-tenant orgs with SSO; per-user identity mapped to source identities.
2. At least **2–3 connectors** (e.g. Drive + Slack + Confluence) with OAuth and incremental sync.
3. Parse → chunk → embed → index into **hybrid** (BM25 + dense vector) store.
4. Query: authn → expand ACL → hybrid retrieve → optional rerank → return hits **with citations**.
5. Optional grounded answer: LLM over top-k chunks only; refuse if insufficient evidence.
6. ACL sync + delete/revoke propagation with clear SLOs.
7. Admin: connector health, last sync, error queues.

**Out of MVP (explicitly defer):**

- Perfect OCR / complex table extraction
- Cross-tenant federated search
- Fine-tuned tenant-specific embedding models
- Full eDiscovery / legal hold product
- Real-time collaborative editing of index
- Agent tool-use that writes back to sources

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Query latency (retrieval only)? | Feels interactive | p50 < 300ms, p99 < 1.5s in-region (excl. LLM answer) |
| N2 | Grounded answer latency? | Acceptable if streamed | TTFT < 1–2s; full answer streamed; retrieval budget ≤ 500ms of that |
| N3 | Freshness (new/edit)? | Minutes | p95 index lag < 5 min for connected sources |
| N4 | ACL revoke / delete? | Urgent | p99 visibility revoke < 60s (harder than freshness) |
| N5 | Durability of index? | Rebuildable from sources but costly | Object store holds raw + derived; index rebuildable; RPO for sync cursors ≈ minutes |
| N6 | Availability? | Business-critical knowledge | 99.9% query path; degrade answer-gen before search hits |
| N7 | Security? | No cross-user doc leak | ACL filter **before** return and **before** LLM context; audit every answer |
| N8 | Tenancy isolation? | Soft multi-tenant OK if keyed; hard isolation for regulated | `tenant_id` on every row/index shard; optional dedicated cells |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Admin connects Drive → OAuth → initial crawl → docs appear in search within SLA.
2. User asks “Q3 roadmap risks?” → hybrid hits from slides + Slack → cited answer.
3. Doc shared with user → ACL sync → doc appears in their results.
4. Doc unshared / deleted → ACL revoke → disappears from results and cannot enter LLM context.
5. Incremental edit → chunk re-embed → updated content ranks correctly.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Connector token expired | Pause sync; alert admin; keep serving last good index |
| Partial parse failure | Quarantine doc; index what we can; surface error in admin |
| Huge PDF (500 pages) | Chunk with caps; async heavy parse; don’t block connector worker pool |
| Query returns forbidden doc due to stale ACL | **Incident**; prefer fail-closed on ACL uncertainty |
| User in 10K groups | Bound ACL expansion; use ACL bitmaps / segment posting |
| Duplicate content across Drive+Slack | Dedup by content hash optional; show source diversity |
| LLM hallucinated citation | Only cite chunk_ids actually in context; verify offsets |
| Hot tenant reindex | Isolate with tenant-fair queues; don’t starve others |
| Embedding model upgrade | Dual-write or background re-embed; version vectors |
| Source rate limits | Backoff per connector; prioritize ACL/delete events |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants | 100 | 1K | 10K | 100K |
| Seats (users) | 50K | 500K | 5M | 50M |
| Indexed documents | 50M | 500M | 5B | 50B |
| Chunks (avg 20/doc) | 1B | 10B | 100B | 1T |
| Embedding dims | 768 | 768 | 768–1536 | 768–1536 |
| Vector storage (raw fp16) | ~1.5 TB | ~15 TB | ~150–300 TB | ~1.5–3 PB |
| Query QPS (search) | 50 | 500 | 5K | 50K |
| Grounded-answer QPS | 10 | 100 | 1K | 10K |
| Ingest events/day (new/edit) | 5M | 50M | 500M | 5B |
| Peak ingest docs/s | ~100 | ~1K | ~10K | ~100K |
| Connector types | 3 | 5 | 10 | 20+ |
| Avg query → chunks retrieved | 50 → rerank 10 | same | same | same |

**What each jump forces:**

- **10×:** Separate ingest vs query fleets; Kafka for sync events; Redis ACL cache; GPU/CPU embed workers autoscaled.
- **100×:** Tenant cells / index shards; ANN + inverted index co-design; ACL posting lists or security trimming at segment level; rerank fleet.
- **1,000×:** Multi-region query; cold/hot chunk tiers; embedding quantization (PQ/OPQ); dedicated regulated tenants; connector federation.

### 1.5 Etc. (Constraints & Assumptions)

- **We build search + grounded Q&A**, not a full knowledge graph product.
- **Source systems remain SoT** for content and ACL; we mirror.
- **Single primary cloud**, multi-AZ; multi-region DR with tenant home region for index writes.
- **Embedding model** is a versioned dependency; plan migrations.
- **Citations** always point to `doc_id` + `chunk_id` + source URL deep link when available.

**Scope statement:**

> Design an LLM-powered enterprise search system: multi-tenant connectors ingesting Drive/Slack/wiki content, parse/chunk/embed into ACL-aware hybrid indexes, serve low-latency hybrid retrieval with optional grounded answers and citations—starting at ~50M docs / 50 QPS and evolving through 10× / 100× / 1,000× with cell isolation, ANN scaling, and hard ACL invariants.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not conflate)

| Class | Baseline peak (order) | 1,000× (order) | Notes |
|-------|------------------------|----------------|-------|
| Interactive **search queries** | ~50/s | ~50K/s | Hybrid retrieve + ACL |
| **Grounded answer** jobs | ~10/s | ~10K/s | Includes LLM tokens |
| **Ingest** (doc versions) | ~100/s | ~100K/s | Parse/chunk/embed pipeline |
| **ACL-only** updates | ~50/s | ~50K/s | Must be faster path than full re-embed |
| **Embedding** ops (chunks/s) | ~2K/s | ~2M/s | 20 chunks/doc × ingest |

### 2.2 Documents → chunks → vectors

```text
Baseline docs: 50M
Avg chunks/doc: 20  → 1B chunks
Embedding: 768-dim float16 = 768 × 2 B = 1,536 B ≈ 1.5 KB / vector
1B × 1.5 KB = 1.5 TB raw vectors (no replicas, no graph index overhead)

HNSW/graph overhead often 1.5–3× → plan ~3–5 TB for vectors+index baseline
BM25 inverted index: often 20–40% of corpus text size
Corpus text: 50M × 20 KB avg extracted ≈ 1 TB text → BM25 ~200–400 GB
```

At **1,000× (50B docs, 1T chunks):**

```text
1T × 1.5 KB = 1.5 PB raw vectors → quantization mandatory
  int8: ~0.75 PB; PQ 64B/vector: ~64 TB (lossy—tune recall)
→ shard by tenant/cell; cold tier for untouched tenants
```

### 2.3 Query path latency budget

```text
Budget p99 retrieval = 1.5s:
  Authn + tenant resolve:     10–30 ms
  ACL expansion (cached):     5–50 ms
  BM25 top-200:               20–80 ms
  ANN top-200:                20–100 ms
  Fusion (RRF):               5–10 ms
  ACL post-filter / trim:     5–40 ms
  Rerank top-50 → 10:         50–300 ms (cross-encoder)
  Assemble response:          10–20 ms
→ Keep rerank optional under load; degrade to hybrid fusion only
```

**LLM answer (separate):**

```text
Retrieve 10 chunks × ~500 tokens = 5K tokens context
Generation 500 tokens @ 50 tok/s ≈ 10s total; stream TTFT after retrieve
```

### 2.4 Ingest pipeline throughput

```text
Baseline peak ingest: 100 docs/s × 20 chunks = 2,000 embeds/s
Embed model ~500 chunks/s per A10-class GPU (order—tune to real bench)
→ ~4 GPUs baseline peak (+ headroom)
1,000×: 100K docs/s × 20 = 2M embeds/s → thousands of GPUs or heavy batching/CPU models
→ batch embed, prioritize ACL/delete, defer re-embed of cold docs
```

### 2.5 Bandwidth & storage of raw artifacts

```text
Raw blobs in object store: 50M × 200 KB avg = 10 TB
Parsed text + chunk metadata: ~1–2 TB
1,000×: 10 PB raw → lifecycle policies, dedup, tenant retention
```

### 2.6 ACL cardinality trap

```text
User in U groups; doc shared to G principals
Naïve per-query filter over 1B chunks: impossible
Need: ACL-aware retrieval (section §3.6)—prefilter, postfilter with tight candidates, or ACL segments
```

---

## 3. High-Level Design

### 3.1 Product / UX surfaces

```text
+--------------------------------------------------------------------------+
| Acme Search          [ Ask or search...                          ]  Admin|
+--------------------------------------------------------------------------+
| Sources: All v | Updated < 7d | My drive + Slack                         |
+--------------------------------------------------------------------------+
| Answer (grounded)                                                        |
|  Q3 risks center on infra hiring lag [1] and API deprecation [2].        |
|  [1] Q3 Roadmap.pptx · Drive · ACL: Engineering                          |
|  [2] #proj-api · Slack · 2026-07-12                                      |
+--------------------------------------------------------------------------+
| Results                                                                  |
|  98  Q3 Roadmap.pptx          Drive     Edited 2h ago                    |
|  91  API deprecation plan     Confluence                                |
|  87  thread: hiring freeze?   Slack                                      |
+--------------------------------------------------------------------------+
```

### 3.2 Domain model

```text
Tenant
  ├── User (idp_sub, email)
  ├── ConnectorInstance (type, oauth, cursor, status)
  ├── Principal (user/group/domain)  -- mirrored from sources
  ├── Document (source_id, path, mime, version, acl_version, content_hash)
  │     ├── Chunk (ordinal, text, tokens, embedding_ref, locators)
  │     └── ACLBinding (principals allowed: read)
  ├── IndexShard (tenant/cell assignment)
  └── QueryAudit (who asked, what returned, chunk_ids)
```

**Identity mapping:** IdP user ↔ source user IDs (Slack user, Drive email). Group expansion cached with TTL + invalidation.

### 3.3 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/connectors` | Install connector |
| POST | `/v1/connectors/{id}/sync` | Trigger sync |
| GET | `/v1/connectors/{id}/status` | Cursor, lag, errors |
| POST | `/v1/search` | Hybrid search |
| POST | `/v1/ask` | Grounded answer (SSE) |
| GET | `/v1/documents/{id}` | Metadata + ACL debug (admin) |
| POST | `/v1/feedback` | Relevance / ACL flags |

```http
POST /v1/search
Authorization: Bearer ...
{
  "q": "Q3 roadmap risks",
  "filters": {"sources": ["drive","slack"], "updated_after": "2026-01-01"},
  "top_k": 10,
  "rerank": true
}
```

```http
POST /v1/ask
{
  "q": "What are Q3 roadmap risks?",
  "cite": true,
  "max_context_chunks": 8
}
```

### 3.4 Pipeline overview

```text
Sources ──connector──► Sync Events (Kafka)
                          │
          ┌───────────────┼────────────────┐
          v               v                v
     ACL Updater    Content Fetcher    Delete Handler
          │               │                │
          │               v                │
          │          Parse/Chunk           │
          │               │                │
          │               v                │
          │          Embed Workers         │
          │               │                │
          └───────────────┴────────────────┘
                          v
                 Index Writer (BM25 + Vector + ACL meta)
                          │
                          v
                 Query Path (hybrid + ACL + rerank [+ LLM])
```

### 3.5 Connector & incremental sync

#### Responsibilities

| Component | Owns |
|-----------|------|
| Connector workers | OAuth, list/changes API, rate limits, cursor persistence |
| Content store | Raw bytes + metadata versions |
| ACL service | Principal sets per doc; group membership cache |
| Indexer | Derived chunks/vectors; idempotent by `(doc_id, content_version)` |

**Incremental patterns:**

| Source pattern | Mechanism |
|----------------|-----------|
| Drive | `changes.list` page token |
| Slack | Conversations history + events API; checkpoint `ts` |
| Confluence | CQL / content updated sync token |
| Webhooks | Push into Kafka; still reconcile with periodic full listing |

**Cursor durability:** store in Postgres `(connector_id, cursor, updated_at)`. At-least-once delivery of sync events; indexer is idempotent.

**Priority lanes:**

1. **P0:** Deletes + ACL revokes  
2. **P1:** Permission grants (discoverability)  
3. **P2:** Content edits  
4. **P3:** Full re-crawl / re-embed migrations  

### 3.6 ACL-aware retrieval (deal-breaker section)

#### Problem

Returning or citing a document the user cannot open in the source system is a **security incident**, not a ranking bug.

#### Options

| Approach | How | Pros | Cons | When |
|----------|-----|------|------|------|
| **A. Post-filter** | Retrieve top-N ignoring ACL; drop unauthorized | Simple | Risk empty page; leaks via scoring side channels if careless | Tiny corpora only |
| **B. Pre-filter query rewrite** | Add `acl: principal IN user_principals` to BM25/ANN | Correct if index supports | Huge OR queries; group explosion | Medium; needs ACL indexing |
| **C. ACL segments / bitsets** | Partition index by ACL fingerprint or doc-level bitset | Fast filter | Complex writes | Large enterprise |
| **D. Per-user indexes** | Materialize each user’s view | Trivial query | Storage explosion | **Deal-breaker** at scale |

**Choice: B + C hybrid**

```text
on_query(user):
  principals = acl_service.expand(user)          # user + groups; cached
  candidates = hybrid_retrieve(q, principals)    # engine applies ACL constraint
  # Defense in depth:
  results = [c for c in candidates if acl_service.allows(user, c.doc_id)]
  # Never send non-allowed chunks to LLM
```

**Index ACL representation:**

- Store on each doc/chunk: `allowed_principal_ids` (capped) or `acl_key` → postings/bitset.
- For Google-like “anyone in domain”: encode domain principal.
- For link-shared “anyone with link”: **policy decision**—often exclude from enterprise search or require explicit org setting.

**Deal-breakers:**

- Filtering only in the UI  
- Trusting source “search API” without mirroring ACL  
- Putting unauthorized chunks into the LLM prompt “just for ranking”  
- Caching query results without ACL key in cache key  

**Revoke path:**

```text
ACL revoke event → update ACL store + index ACL field (or delete doc from index)
→ invalidate ACL caches for affected principals
→ invalidate query caches containing doc_id
SLO: p99 < 60s end-to-end
```

### 3.7 Parsing, chunking, embeddings

**Parsing:** MIME routers → text extractors (PDF, DOCX, HTML, Slack mrkdwn). Preserve structure hints (headings) for chunk boundaries.

**Chunking strategies:**

| Strategy | Pros | Cons |
|----------|------|------|
| Fixed tokens (512/1024) | Simple | Splits mid-thought |
| Heading-aware | Better semantics | Needs structure |
| Sliding window overlap | Recall | Storage↑ |
| Late chunking / doc embedding | Better context | Cost/complexity |

**MVP:** heading-aware ~400–800 tokens, 50–100 token overlap; store `locator` (page, slide, message_ts).

**Embedding pipeline:**

```text
chunk text → batch → embed model (version V) → vector
idempotency key: hash(tenant, doc_id, chunk_ord, content_hash, model_version)
```

**Model upgrade:** write `embedding_v2` async; query dual-retrieve during migration or switch after catch-up %.

### 3.8 Hybrid retrieval & reranking

**Hybrid fusion (RRF):**

```text
score(d) = Σ 1 / (k + rank_list_i(d))   # k≈60
lists: BM25, ANN (cosine/IP)
```

**Trade-offs:**

| | BM25 only | Vector only | Hybrid + rerank |
|--|-----------|-------------|-----------------|
| Exact keywords / IDs | Strong | Weak | Strong |
| Paraphrase / conceptual | Weak | Strong | Strong |
| Latency | Best | Good | Costlier |
| Ops complexity | Low | Medium | Higher |

**Reranker:** cross-encoder on top 50 → 10. **Degrade under load:** skip rerank; keep hybrid.

**Filters:** source, time, mime, folder—applied as index filters **intersected with ACL**.

### 3.9 Grounded answers & citations

```text
retrieve authorized chunks → build prompt with [n] markers
→ LLM must answer only from chunks or say "insufficient evidence"
→ response includes citations {n → chunk_id, url, offsets}
→ verify model-cited [n] ⊆ provided set (strip otherwise)
```

**Billing / cost:** answer QPS is a separate capacity class from search.

**Safety:** DLP optional on outputs; never echo secrets from chunks beyond what user could open (still ACL-bound).

### 3.10 Tenancy & multi-region

- Shard indexes by `tenant_id` (cell).  
- Query routed to tenant home cell.  
- Cross-region: active-passive index or read replicas; **ACL writes** follow home cell single-writer.

---

## 4. Architecture Diagram

### 4.1 System context

```text
+-------------+     +------------------+     +-------------------+
| IdP (SSO)   |     | Source Systems   |     | Admins / Users    |
+------+------+     | Drive/Slack/...  |     +---------+---------+
       |            +--------+---------+               |
       |                     | OAuth/API               | HTTPS
       v                     v                         v
+------+---------------------+-------------------------+------+
|                     Enterprise Search Platform               |
|  Control Plane │ Ingest Plane │ Index │ Query │ Answer Gen   |
+----------------------+------------------+--------------------+
                       |                  |
                       v                  v
              Object Store (raw)   Observability / Audit
```

### 4.2 Detailed component diagram

```text
                    +-----------------------+
                    | API Gateway / BFF     |
                    +------+--------+-------+
                           |        |
              +------------+        +-------------+
              v                                   v
     +----------------+                  +----------------+
     | Search Service |                  | Ask Service    |
     | (hybrid+ACL)   |                  | (RAG+stream)   |
     +--------+-------+                  +--------+-------+
              |                                   |
              v                                   v
     +----------------+                  +----------------+
     | Query Engine   |                  | LLM Gateway    |
     | BM25 + ANN     |                  | (quotas)       |
     +--------+-------+                  +----------------+
              |
              v
     +----------------+     +----------------+
     | ACL Service    |<--->| Principal Cache|
     +--------+-------+     +----------------+
              ^
              | sync
     +--------+-------------------------------+
     | Ingest: Connectors → Kafka → Workers   |
     | Parse | Chunk | Embed | Index Writer   |
     +----------------------------------------+
```

### 4.3 Sequence: search query

```text
User → API: POST /v1/search
API → Auth: validate token → user_id, tenant_id
API → ACL: expand principals (cache hit)
API → QueryEngine: hybrid(q, filters, principals)
QueryEngine → BM25 + ANN (ACL constrained)
QueryEngine → fuse RRF → optional rerank
API → ACL: defense-in-depth allow check
API → User: hits + snippets + source links
```

### 4.4 Sequence: ACL revoke

```text
Source → Connector webhook/poll: permission removed
Connector → Kafka: acl_revoke(doc_id, principals-)
ACL Worker → ACL Store update + Index ACL update/delete
ACL Worker → Cache invalidate(principals, doc_id)
Subsequent queries cannot retrieve doc
In-flight Ask: chunk allow-check fails → drop chunk
```

### 4.5 Sequence: grounded ask

```text
User → Ask: POST /v1/ask (SSE)
Ask → Search path (authorized chunks only)
Ask → LLM Gateway: prompt + chunks
LLM → stream tokens
Ask → citation verify → audit log
Ask → User: streamed answer + citations
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | No unauthorized doc in results or LLM context | ACL constraint + post-check; fail closed |
| R2 | Deletes/revokes eventually invisible within SLO | P0 lane; alerts on lag |
| R3 | Idempotent indexing by content/ACL version | Deterministic keys; upserts |
| R4 | Source remains SoT; index is derived | Rebuild tooling; cursors durable |
| R5 | Citations ⊆ provided chunks | Server-side verify |
| R6 | Audit who saw what | Query/ask audit logs |
| R7 | Tenant isolation | `tenant_id` on every key; cell routing |

**Failure modes & degradations:**

| Failure | Degrade |
|---------|---------|
| Embed fleet down | Serve BM25-only; queue embeds |
| ANN down | BM25-only |
| Rerank down | Hybrid fusion only |
| LLM down | Search hits without answer |
| Connector down | Serve stale with banner; P0 ACL via webhooks if possible |
| ACL store uncertain | **Fail closed** for affected docs |

### 5.2 Scalability — progressive

**1×:** Monolith OK; OpenSearch/Elastic + vector plugin or pgvector for small tenants; few connector workers.

**10×:** Kafka; separate embed GPU pool; Redis ACL; horizontal query replicas.

**100×:**

- Tenant cells (index + ACL + cursors).  
- Sharded ANN (by tenant or doc hash within large tenants).  
- Security trimming / ACL bitsets.  
- Fair queues per tenant for ingest.

**1,000×:**

- Quantized vectors; hot/cold indexes.  
- Multi-region query replicas; home-region writes.  
- Connector mesh with regional egress for data residency.  
- Per-tenant dedicated cells for whales / regulated.

**Ownership resolution (avoid contradictions):**

| Concern | Single owner |
|---------|--------------|
| Cursor / sync progress | Connector control plane (Postgres) |
| Raw bytes | Object store + metadata DB |
| ACL truth (mirror) | ACL service |
| Lexical index | Query engine BM25 store |
| Vector index | ANN store (may co-locate) |
| Query authz decision | Search/Ask services (never connectors) |

### 5.3 Maintainability

- **Connector SDK:** interface `list_changes`, `fetch`, `normalize_acl`.  
- **Eval harness:** recall@k, nDCG, ACL leak tests (must be zero), citation precision.  
- **Embedding version** in every vector row.  
- **Feature flags:** rerank on/off, answer on/off per tenant.  
- **Rebuild playbooks:** from object store without re-fetching sources when possible.  
- **Schemas:** evolve chunk metadata with version field.

### 5.4 Freshness vs cost

| Policy | Mechanism |
|--------|-----------|
| Hot docs (recently queried) | Prioritize re-embed |
| Cold corpus | Longer sync interval |
| ACL | Always hot path |
| Slack floods | Collapse edits; sample threads |

### 5.5 Snippet & citation integrity

- Snippets generated from **authorized** chunk text only.  
- Deep links use source URLs; if link would 404 due to ACL, still OK—user shouldn’t have seen it.  
- Highlight terms carefully to avoid leaking neighboring confidential tokens from bad chunk boundaries—tune chunking.

### 5.6 Cost model (interview talking point)

```text
Cost ≈ embed_compute + vector_storage + query_compute + LLM_tokens + connector_egress
LLM tokens often dominate Ask QPS; retrieval dominates Search QPS
Charge tenants for Ask separately; cache nothing across users
```

---


### 5.7 Query-time ranking features (beyond fusion)

Hybrid RRF is a strong MVP. At 10×–100×, add lightweight features before/after rerank:

| Feature | Signal |
|---------|--------|
| Recency | `exp(-λ Δt)` |
| Source prior | Drive wiki > random Slack noise (tunable) |
| Click / like EMA | Online feedback |
| Title match boost | Lexical overlap |
| Owner proximity | Docs in user’s team drives |

Keep ACL orthogonal—**never** use “user can’t click so downrank” as a substitute for exclusion.

### 5.8 Slack & Drive specific connector notes

**Drive:** changes.list + files.get; export Google Docs to text/PDF; shared drives vs My Drive ACL differences; shortcuts/aliases.

**Slack:** public channels vs private; DMs often **out of scope** unless explicitly enabled; thread chunking (`thread_ts`); rate limits tiered; edit/delete events.

**Confluence/Notion:** space-level permissions; archived pages; comment bodies optional.

### 5.9 Multi-hop / agentic retrieval (Phase 2)

```text
plan → retrieve → read → retrieve again → answer
```

Each hop must re-apply ACL. Bound hops (e.g. 3) and total tokens. Prefer MVP single-shot with good hybrid+rerank before agents.

### 5.10 Incident: ACL leak response

1. Page search/ask.  
2. Invalidate all query caches.  
3. Find first bad commit / sync bug.  
4. Reindex ACL fields from SoT.  
5. Audit logs for exposed `doc_id`s; notify per policy.  
6. Add regression test from the incident.

Treat as Sev-1 security, not relevance.

---

## 6. Wrap-Up

### 6.1 What to draw first in an interview

1. Connectors → Kafka → parse/chunk/embed → hybrid index.  
2. Query path with **ACL expand → retrieve → post-check**.  
3. Optional Ask path with citation verification.  
4. Call out P0 revoke lane and fail-closed behavior.

### 6.2 MVP → scale path

| Phase | Ship |
|-------|------|
| MVP | 2–3 connectors, hybrid search, ACL post+pre filter, citations, basic Ask |
| 10× | Kafka, embed fleet, rerank, admin lag SLOs |
| 100× | Cells, ACL bitsets/segments, fair ingest |
| 1,000× | Quantization, multi-region, dedicated tenants |

### 6.3 Top risks

1. ACL bugs (security).  
2. Index lag mistaken for “search is bad”.  
3. Embedding migration downtime.  
4. Noisy Slack data drowning Drive signal—need source weights / filters.  
5. LLM answers without evidence.

### 6.4 One-sentence design

> Mirror enterprise content and ACLs into a tenant-sharded hybrid index, serve ACL-constrained retrieval with optional grounded generation over verified citations, and scale ingest/query as separate fleets with revoke-first freshness.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & product

**Q: Keyword search vs RAG—what’s the difference?**  
A: Keyword/hybrid retrieval returns documents; RAG adds LLM synthesis over retrieved chunks. Enterprise search must nail retrieval+ACL even if Ask is off.

**Q: Why not only use each source’s native search API?**  
A: Federated fan-out is high latency, inconsistent ranking, hard hybrid/LLM, rate limits; mirroring enables unified relevance—but ACL sync becomes your problem.

**Q: How do you handle “I know the doc exists but can’t find it”?**  
A: Separate: (1) not synced, (2) ACL excludes, (3) ranking miss. Admin sync status + “request access” UX; never show titles of unauthorized docs.

### 7.2 ACL & security

**Q: What’s the #1 deal-breaker?**  
A: Serving unauthorized content (including to the LLM). Fail closed; defense in depth; audit.

**Q: How do you encode Drive ACLs?**  
A: Normalize to principals (user/group/domain); expand user groups at query; store allow sets or ACL keys on docs; map IdP ↔ Drive identities.

**Q: Cache search results?**  
A: Only with cache key including `user_id` or `acl_version` + query; short TTL; prefer no shared cross-user cache.

**Q: Side-channel via latency or result counts?**  
A: Avoid “0 results vs filtered” distinctions that reveal existence if product forbids; often enterprise accepts existence opacity only for titles—you never show forbidden titles.

**Q: Group explosion (user in 10K groups)?**  
A: Cap expansion; use bloom/bitset of user’s principals; ACL segment posting; monitor pathological users.

### 7.3 Indexing & embeddings

**Q: Chunk size trade-off?**  
A: Smaller → precise citations, more vectors; larger → more context, noisier retrieval. 400–800 tokens common starting point.

**Q: When to re-embed?**  
A: Content hash change or model version change. ACL-only changes must **not** require re-embed.

**Q: BM25 vs embeddings for code / IDs?**  
A: Lexical wins for identifiers; hybrid covers both.

**Q: How to migrate embedding models?**  
A: Dual index or background re-embed with version field; cut over when coverage threshold met; keep old until rollback window ends.

**Q: Quantization impact?**  
A: PQ/OPQ cuts memory; may drop recall—compensate with re-ranker and slightly larger candidate sets.

### 7.4 Query path

**Q: Why RRF over weighted score sum?**  
A: Avoids brittle score calibration across BM25 and cosine; robust default. Learned fusion later.

**Q: Where does reranking sit?**  
A: After fusion, before response; optional; biggest latency cost after LLM.

**Q: How to guarantee citation correctness?**  
A: Only allow citations to provided chunk markers; strip others; optionally entailment check.

**Q: Multi-hop questions?**  
A: MVP single-shot RAG; Phase 2 agentic retrieve loops with ACL on every hop.

### 7.5 Connectors & freshness

**Q: At-least-once sync causing duplicates?**  
A: Idempotent upserts on `(doc_id, version)`; deletes tombstone by `source_id`.

**Q: How fast must ACL revoke be vs content freshness?**  
A: Revoke faster (seconds–minute); content minutes OK.

**Q: Slack message edits/deletes?**  
A: Event-driven update/tombstone; thread chunking strategy must update parent aggregates carefully.

**Q: Rate limited by Google?**  
A: Per-connector token buckets; exponential backoff; prioritize changes API over full fetch.

**Q: Initial crawl of 10M docs?**  
A: Snapshot + backlog queue; progressive search quality; show sync % to admin.

### 7.6 Scale & tenancy

**Q: One big cluster vs cell per tenant?**  
A: Shared cells with tenant-keyed shards for SMB; dedicated cells for whales/regulated. Avoid noisy-neighbor embed backlogs.

**Q: How to shard ANN?**  
A: By tenant first; within mega-tenant by doc_id hash with scatter-gather (bound fanout).

**Q: Hot tenant reindex melting the fleet?**  
A: Fair scheduling; separate priority queues; admission control.

**Q: Multi-region residency?**  
A: Keep raw + index in-region; query stays regional; no cross-region chunk shipping for Ask without policy.

### 7.7 Reliability drills

**Q: ANN cluster loses a shard?**  
A: Degrade to BM25; alert; rebuild shard from vectors in object store.

**Q: Kafka down?**  
A: Buffer connector side; risk freshness lag; keep query up.

**Q: Poison document crashes parser?**  
A: Quarantine + DLQ; don’t block partition; circuit-break that MIME parser version.

**Q: Embedding drift / bad model deploy?**  
A: Version pin; canary tenants; rollback to previous vector space (keep old index).

### 7.8 Evaluation

**Q: How do you know search is good?**  
A: Golden query sets per tenant vertical; nDCG; ACL leak suite (must be 0); online CTR/thumbs; citation precision for Ask.

**Q: Offline vs online?**  
A: Offline for regressions; online for ranking tweaks; never ship ACL changes without leak tests.

### 7.9 Comparison traps

**Q: How is this different from web search?**  
A: ACL, connectors, smaller corpora per tenant, stronger citation/compliance needs, less link graph.

**Q: How is this different from Slack search alone?**  
A: Cross-source unified index + semantic + grounded answers; Slack is one connector.

**Q: Why not put all text into the LLM context?**  
A: Context limits, cost, latency, and ACL—retrieval is mandatory.

### 7.10 Extra interviewer traps (high value)

- What is in the cache key for search?  
- Does ACL change re-embed? (No.)  
- Can the LLM see a chunk the user can’t? (No.)  
- How do you handle “anyone with the link”?  
- What’s the P0 ingest lane?  
- How do you rebuild an index without re-OAuth to sources?  
- What’s the latency budget split for hybrid vs rerank vs LLM?  
- How do you prevent tenant A’s embed backlog from delaying tenant B’s ACL revoke?  
- How do you version prompts for Ask separately from embedding models?  
- What fails first under load—and what do you degrade intentionally?  
- How do you prove no ACL leak in CI?  
- When is federated search better than mirroring?  
- How do you represent a Slack thread as chunks?  
- What is your idempotency key for chunk vectors?  
- How do you estimate vector memory at 100× with HNSW overhead?

---

## Appendix A — Example schemas

```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  home_cell TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE connectors (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  type TEXT NOT NULL, -- drive|slack|confluence|...
  status TEXT NOT NULL,
  cursor JSONB NOT NULL DEFAULT '{}',
  cursor_updated_at TIMESTAMPTZ,
  UNIQUE (tenant_id, type, id)
);

CREATE TABLE documents (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  source_type TEXT NOT NULL,
  source_doc_id TEXT NOT NULL,
  version BIGINT NOT NULL,
  content_hash TEXT NOT NULL,
  acl_version BIGINT NOT NULL,
  mime TEXT,
  title TEXT,
  source_url TEXT,
  updated_at TIMESTAMPTZ NOT NULL,
  deleted_at TIMESTAMPTZ,
  UNIQUE (tenant_id, source_type, source_doc_id)
);

CREATE TABLE chunks (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  document_id UUID NOT NULL,
  ordinal INT NOT NULL,
  text TEXT NOT NULL,
  token_count INT NOT NULL,
  locator JSONB NOT NULL,
  content_hash TEXT NOT NULL,
  embedding_model TEXT NOT NULL,
  UNIQUE (document_id, ordinal, content_hash, embedding_model)
);

CREATE TABLE document_acl (
  document_id UUID NOT NULL,
  principal_id TEXT NOT NULL, -- user:|group:|domain:
  PRIMARY KEY (document_id, principal_id)
);

CREATE TABLE query_audit (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID NOT NULL,
  q TEXT NOT NULL,
  mode TEXT NOT NULL, -- search|ask
  returned_doc_ids UUID[] NOT NULL,
  returned_chunk_ids UUID[] NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Appendix B — Event envelopes

```json
{
  "event_id": "evt_01J...",
  "type": "document_upsert",
  "tenant_id": "t_...",
  "connector_id": "c_...",
  "source_type": "drive",
  "source_doc_id": "file:123",
  "version": 42,
  "acl_version": 7,
  "priority": "P2"
}
```

```json
{
  "event_id": "evt_01J...",
  "type": "acl_revoke",
  "tenant_id": "t_...",
  "source_doc_id": "file:123",
  "principal_ids_removed": ["user:u_9"],
  "priority": "P0"
}
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Connectors, parse/chunk/embed, hybrid index, ACL filter, search API |
| 10× | Kafka lanes, embed autoscaling, ACL cache, rerank, admin lag SLOs |
| 100× | Tenant cells, ACL bitsets/segments, fair ingest, dual embed migration tools |
| 1,000× | Quantization, multi-region residency, dedicated cells, hot/cold tiers |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Hybrid retrieval | BM25 + dense vector fused (e.g. RRF) |
| ACL principal | User, group, or domain identity that may read a doc |
| Chunk | Retrieval unit with locator into source |
| Grounded answer | LLM output constrained to retrieved chunks |
| Connector cursor | Incremental sync checkpoint |
| Fail closed | On ACL uncertainty, deny rather than serve |
| ANN | Approximate nearest neighbor vector search |
| Reranker | Cross-encoder reordering of candidates |
| Cell | Tenant-scoped deployment shard |
| Citation | Mapping from answer span to chunk/doc |

## Appendix E — Estimation cheat-sheet (correctness)

```text
Chunks ≈ docs × chunks_per_doc
Vector bytes ≈ chunks × dims × bytes_per_dim
  fp16 768-dim ≈ 1.5 KB/vector
HNSW overhead often multiplies memory—do not quote raw vectors as cluster size

Ingest docs/s ≠ embed chunks/s
  embed_chunks/s ≈ ingest_docs/s × chunks_per_doc

Search QPS ≠ Ask QPS (Ask includes LLM)

ACL updates must be a separate faster lane from content re-embed

1,000× vector memory without quantization is a petabyte-class problem
```

---

*End of design doc. Open with §1 ACL + connectors scope; whiteboard §3.6 ACL retrieval + §3.8 hybrid; close with invariants in §5.1 and traps in §7.*
