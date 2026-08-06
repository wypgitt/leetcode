# System Design: Distributed Search over ~1 Billion Documents

> **Focus areas:** Inverted-index sharding · Hybrid BM25+ANN · Query caches · Extreme QPS · LLM re-rank / RAG · GPU efficiency · ACL/safety  
> **Style:** End-to-end AI infra design with progressive scale (10× → 100× → 1,000×)  
> **Theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — sharding, caching, backpressure, batching, cost  
> **Quality bar:** Correct QPS/storage arithmetic, split ingest vs query vs LLM loads, never melt GPUs on the interactive path

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

Goal: **bound the product**—a distributed search system over roughly **one billion documents** that serves extreme query QPS with hybrid retrieval, and optionally integrates LLM re-ranking / RAG answers without turning inference into the bottleneck. Think Anthropic-internal knowledge + API-scale retrieval substrate—not a generic web crawler.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Corpus size? | ~1B docs baseline; grow 10×–1000× | Shard from day 1; segment lifecycle |
| F2 | Doc types? | Text, HTML, PDF extracts, code, chat logs; metadata | Parser/chunker; parent doc + chunks |
| F3 | Query modes? | Keyword, semantic, hybrid; optional LLM answer | Fanout + fusion; separate gen path |
| F4 | Latency? | Interactive search snappy; answers streamed | Budgets: retrieve ≪ generate |
| F5 | Freshness? | Minutes for updates; deletes ASAP | Near-real-time indexing; tombstones |
| F6 | Multi-tenant? | Yes if productized; or internal spaces | `space_id` / tenant in shard key |
| F7 | ACL? | Users only see allowed docs | Filter before return **and** before LLM context |
| F8 | Ranking? | BM25 + vector + optional cross-encoder / LLM re-rank | Cascade re-rankers by cost |
| F9 | RAG? | Grounded answers with citations | Top-k chunks only; refuse if weak evidence |
| F10 | Languages? | EN MVP; multilingual Phase 1.5 | Analyzers + multilingual embeddings |
| F11 | Analytics? | Query logs, click, thumbs | Offline eval + online metrics |
| F12 | Admin? | Index health, reindex, shard status | Control plane separate |

**MVP functional scope (lock with interviewer):**

1. Ingest pipeline: parse → chunk → index **BM25** + **dense vectors**.
2. Query path: authz → query understand → hybrid retrieve → light re-rank → hits.
3. Optional **LLM answer** over top-k with citations (streamed).
4. Caching: query result cache + embedding cache for repeated queries.
5. Sharded index with replicas; rolling segment merge.
6. Delete/ACL revoke path with SLO.
7. Metrics: QPS, p99, recall proxies, GPU queue depth.

**Out of MVP:**

- Perfect OCR/tables
- Web-scale crawling (assume docs arrive via connectors/API)
- Personalization ML ranker v2
- Global multi-master writes

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Search p99 (no LLM)? | Interactive | < 100–300ms in-region at baseline 1B |
| N2 | Hybrid recall? | Competitive | Offline eval @k; don’t overclaim |
| N3 | Answer TTFT? | Streamed | < 1–2s including retrieve budget ≤ 200–400ms |
| N4 | Freshness | Minutes | p95 < 5 min index lag |
| N5 | Delete/ACL | Urgent | p99 < 60s visibility revoke |
| N6 | Availability | High | 99.9% search; degrade LLM first |
| N7 | Durability | Rebuildable | Object store source; index rebuildable |
| N8 | Cost | GPU scarce | Batch embed; cascade re-rank; cache |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Doc ingested → searchable within SLA → hybrid query returns ranked hits.
2. User asks NL question → retrieve → LLM cites chunks → stream answer.
3. Doc deleted → tombstone → disappears from hits and RAG context.
4. Hot query repeated → query cache hit → sub-ms metadata path.
5. Re-rank cascade: cheap L1 → cross-encoder on 50 → LLM re-rank on 10 only when needed.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Shard timeout | Partial fanout with degraded flag; or fail if ACL uncertain |
| ANN index stale vs BM25 | Accept bounded skew; version vectors |
| Query cache serves forbidden doc | **Bug**; cache keys must include ACL principal fingerprint |
| LLM re-rank queue meltdown | Skip to non-LLM ranking; serve hits |
| Huge fanout scatter-gather | Dynamic pruning; tiered replicas |
| Embedding model upgrade | Dual index / background re-embed |
| Hot tenant ingest | Fair queues; isolate noisy neighbor |
| Exact phrase + semantic | Hybrid fusion (RRF / weighted) |
| Empty retrieval | Refuse answer; suggest reformulate |
| Adversarial prompt injection in docs | Treat docs untrusted in RAG; sandwich + filters |

### 1.4 Scales (Progressive)

| Metric | Baseline (~1B) | 10× | 100× | 1,000× |
|--------|----------------|-----|------|--------|
| Documents | 1B | 10B | 100B | 1T |
| Chunks (10/doc) | 10B | 100B | 1T | 10T |
| Search QPS | 10K | 100K | 1M | 10M |
| RAG answer QPS | 500 | 5K | 50K | 500K |
| Ingest docs/s | 1K | 10K | 100K | 1M |
| Embeddings dims | 768 | 768 | 768–1024 | same |
| Vector storage fp16 | ~15 TB | ~150 TB | ~1.5 PB | ~15 PB |
| Inverted index size | ~20–50 TB | ×10 | ×100 | ×1000 |
| Shards | 256 | 2K | 20K | 200K |
| Query cache hit rate | 30% | 35% | 40% | 40%+ |

**What each jump forces:**

- **10×:** More shards; disaggregated storage; dedicated embed fleet; RAG admission.
- **100×:** Hierarchical scatter-gather; PQ/OPQ vectors; aggressive caching; cell isolation.
- **1,000×:** Multi-tier cold/hot; sampled ANN; regional corpora; LLM re-rank rarer.

### 1.5 Etc. (Constraints & Assumptions)

- Corpus arrives via **ingest API/connectors**, not built as Google Web Search.
- **LLM path is optional and degradable**; keyword/hybrid hits remain useful alone.
- Single primary region writes; multi-AZ; read replicas multi-region Phase 2.
- Emphasize **not melting GPUs**: embeddings async; re-rank cascade; batch where possible.

**Scope statement:**

> Design distributed search over ~1B documents with sharded hybrid BM25+ANN indexes, ACL-safe retrieval, multi-layer caches, and optional LLM re-rank/RAG—sized for ~10K search QPS baseline scaling through 10× / 100× / 1,000×—with explicit isolation of ingest, query, and inference load classes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | Baseline peak | Notes |
|-------|---------------|-------|
| Search queries | 10K QPS | Scatter-gather CPU/ANN |
| RAG generations | 500 QPS | GPU decode |
| LLM re-rank only | 200 QPS | Shorter prompts; still GPU |
| Ingest | 1K docs/s | Parse/chunk |
| Embed | ~10K chunks/s | GPU/CPU embed |
| Cache lookups | ~10K+/s | Redis |

**Anti-pattern:** sizing GPU fleet from search QPS alone.

### 2.2 Storage math

```text
1B docs × 10 chunks = 10B vectors
768-d × 2 bytes (fp16) = 1536 B ≈ 1.5 KB / vector
10B × 1.5 KB = 15 TB raw vectors

HNSW graph overhead often 1.5–2× → ~25–30 TB order
Inverted index: posting lists — interview ~20–50 TB depending on text
Object store raw docs: 1B × 10 KB = 10 TB (varies widely)
```

### 2.3 QPS & fanout

```text
256 shards, each query hits all (broadcast) worst case:
  10K QPS × 256 = 2.56M shard-QPS aggregate
Mitigations: term-based routing for keyword-only; ANN nprobe subsets;
             replica parallelism; caching

Per-shard budget: if 40 replicas groups...
  Design: ~100–400 QPS/shard-replica sustainable for hybrid
```

### 2.4 RAG GPU math

```text
500 answer QPS × 400 out tokens = 200K out tok/s
If one GPU ~2K out tok/s effective → ~100 GPUs decode alone
+ prefill on retrieved context (4K tokens) dominates!
Prefill: 500 × 4K = 2M input tok/s → often larger fleet

Caches + shorter contexts + fewer RAG QPS via admission are mandatory
Prefix cache on system+tools helps multi-tenant RAG
```

### 2.5 Embed throughput

```text
Ingest 1K docs/s × 10 chunks = 10K embeds/s
Batch size 256–1024 on GPU; continuous embed workers
Offline re-embed 10B chunks: at 100K/s → 1e10/1e5 = 1e5 s ≈ 28 hours minimally —
  reality longer; plan rolling dual-write weeks
```

### 2.6 Query cache savings

```text
30% hit rate @ 10K QPS → 3K served from cache
Reduces shard fanout and ANN cost proportionally on hit
Key must include principal ACL fingerprint
```

---

## 3. High-Level Design

### 3.1 Domain model

```text
Space / Tenant
  └── Document (doc_id, version, ACL, mime, uri)
        └── Chunk[] (chunk_id, text, offsets, embed_version)
IndexSegment (shard_id, gen, doc range or hash)
Postings + VectorGraph for segment
QueryLog / Judgment for eval
```

### 3.2 Ingest pipeline

```text
Producer → Kafka
  → Parse/Extract
  → Chunk (token-aware; overlap)
  → Embed (batched GPU)
  → Index writer (BM25 + ANN)
  → Commit / publish segment gen
ACL/Delete topic → high priority apply tombstones
```

**Idempotency:** `(doc_id, version)` upsert; chunks content-addressed.

### 3.3 Sharding strategies

| Strategy | Pros | Cons |
|----------|------|------|
| Hash(doc_id) | Balanced | Every query fans out |
| Term partition (by term) | Keyword routing | Rebalance hard; semantic hard |
| **Hybrid chosen** | Doc-hash shards for hybrid; caching + pruning | Fanout still exists |
| Tenant cells | Isolation | Skewed tenants |

**Choice:** hash document into shards; replicate; use query cache + early termination; for keyword-only optimize with term stats routing later.

### 3.4 Hybrid retrieval

```text
Query → rewrite/expand (optional)
  → BM25 top-k1 per shard → merge
  → ANN top-k2 per shard → merge
  → Fusion (RRF / weighted)
  → ACL filter (if not earlier)
  → L1 feature re-rank (CPU)
  → optional cross-encoder top 50
  → optional LLM re-rank top 10
  → return hits
```

**ACL:** prefer **security trimming** as early as possible (segment-level bitsets / ACL posting). If uncertain → exclude (fail-closed).

### 3.5 ANN index

- HNSW for MVP quality; IVF-PQ at larger memory pressure.
- `embed_version` in segment metadata; queries use matching version.
- Dual-read during migrations.

### 3.6 Caching layers

| Cache | Key | Value | TTL |
|-------|-----|-------|-----|
| Query result | hash(q, params, acl_fp, index_gen_major) | hit list | 10–60s |
| Query embedding | hash(q_text, embed_ver) | vector | hours |
| Doc snippet | chunk_id | text | long |
| RAG answer | optional strict | answer | short / off by default |

**Deal-breaker:** query cache without ACL fingerprint.

### 3.7 LLM integration without melting GPUs

```text
Admission control on RAG / LLM-re-rank queues
Cascade:
  default: hybrid + CPU re-rank
  if low confidence OR user asks answer: cross-encoder
  if still needed AND budget: LLM re-rank / generate
Batch LLM re-rank in microbatches (5–20ms windows) for throughput
Prefill cache shared system instructions
Hard caps: max context chunks, max output tokens
Degrade: return hits only with banner
```

### 3.8 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/index/docs` | Upsert docs |
| DELETE | `/v1/index/docs/{id}` | Delete |
| POST | `/v1/search` | Hybrid search |
| POST | `/v1/answer` | RAG answer stream |
| GET | `/v1/admin/shards` | Health |

```http
POST /v1/search
{
  "query": "throughput limits for batch API",
  "mode": "hybrid",
  "top_k": 10,
  "filters": {"space_id": "..."},
  "rerank": "auto"
}
```

### 3.9 Trade-offs

| Area | Options | Choice |
|------|---------|--------|
| Engine | ES/OpenSearch vs custom | Custom/Lucene-like shards or OpenSearch MVP + vector sidecar |
| Vectors | Separate DB vs co-located | Co-located segment files MVP; disaggregate later |
| Fusion | RRF vs learned | RRF MVP |
| RAG | Always on | Opt-in / auto with admission |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+----------+    +---------------+    +----------------------+
| Clients  |--->| Edge / API    |--->| Query Coordinator    |
+----------+    +-------+-------+    +----------+-----------+
                        |                       |
                        v                       v
               +----------------+      +--------+---------+
               | Query Cache    |      | ACL Expander     |
               | + Emb Cache    |      +--------+---------+
               +----------------+               |
                                                v
               +-----------------------------------------------+
               | Scatter → Shard Replicas (BM25 + HNSW) × N    |
               +----------------------+------------------------+
                                      |
                                      v
                               Merge / Fusion / L1 rank
                                      |
                    +-----------------+------------------+
                    v                                    v
           +----------------+                  +----------------+
           | Cross-encoder  |                  | Return hits    |
           | fleet (opt)    |                  +--------+-------+
           +--------+-------+                           |
                    v                                   v
           +----------------+                  +----------------+
           | LLM re-rank /  |<--admission------| Answer stream  |
           | RAG generate   |                  | (citations)    |
           +----------------+                  +----------------+

Ingest plane:
 Connectors → Kafka → Parse → Embed GPU → Index writers → Object store
```

### 4.2 Shard internals

```text
ShardReplica
  ├── Segment_0..N (immutable)
  │     ├── postings
  │     ├── doc values / norms
  │     ├── HNSW / IVF vectors
  │     └── ACL bitsets
  ├── Tombstone log
  └── Memtable / refresh buffer
```

### 4.3 Degradation path

```text
LLM overload → disable answer & LLM re-rank
Cross-encoder overload → CPU L1 only
Shard partial → degraded results flag
Cache down → direct query
Embed down → keyword-only mode
```

---

## 5. Design Deep Dive

### 5.1 Reliability

| Concern | Approach |
|---------|----------|
| Write durability | Kafka + object store canonical; index derived |
| Replica loss | Re-replicate segments; stay serving if RF-1 |
| Split brain gens | Epoch per shard; coordinator reads quorum gen |
| Exactly-once ingest | Idempotent upsert by doc version |
| Poison docs | Quarantine; DLQ |
| RAG hallucination | Cite only provided chunk_ids; verify |

**Rebuild:** from object store + embeddings (if stored) or re-embed.

### 5.2 Scalability

**Scatter-gather optimizations:**

- Speculative replica hedging on slow shard.
- Adaptive `k` per shard.
- WAND / block-max WAND for BM25.
- ANN: efSearch tradeoff knobs under load.
- Coordinator deadlines with partials policy.

**Disaggregation (100×):**

- Separate vector serving from inverted text.
- Cold segments on object store + page cache.
- Tenant cells for noisy neighbors.

**1,000×:**

- Hierarchical indexes (cluster centroids → shards).
- Aggressive PQ; re-rank fewer docs.
- Regional corpus splits.

### 5.3 Maintainability

- Segment format versioning.
- Offline recall@k eval continuous.
- Canary shards for ranking changes.
- Clear ownership: ingest vs query vs inference teams.

### 5.4 Indexing details

```text
Refresh: near-real-time searchable buffer every ~1s
Flush: memtable → segment
Merge: tiered merges; throttle under query load
Deletes: soft tombstones until merge; ACL revoke updates bitsets fast path
```

### 5.5 Fusion & ranking cascade

```text
RRF score(d) = Σ 1/(k + rank_i(d))
Then L1: features (BM25, ANN dist, freshness, click priors)
Cross-encoder: pairwise query-doc relevance (batch)
LLM re-rank: listwise top-10 with short rationales optional (costly)
```

**GPU batching for cross-encoder / LLM re-rank:** microbatch across queries carefully for interactive (trade latency) or only on RAG path.

### 5.6 ACL deep dive

```text
Principal → expand groups → ACL fingerprint
Per segment: bitset of allowed doc ords for principal (cached)
Filter postings/ANN candidates through bitset
Cache key includes fingerprint
On revoke: invalidate bitset cache + query cache for principal; update doc ACL
```

**Fail-closed** if expansion service down for that request.

### 5.7 Query understanding

- Spell correction, synonym expand (careful with precision).
- HyDE optional (expensive)—usually offline or rare.
- Embed query once; cache vector.

### 5.8 RAG safety

- Docs are **untrusted content**; wrap with delimiters; instruct model to ignore instructions in docs.
- Strip active injection patterns best-effort.
- No tool execution from retrieved text alone.
- Log cited IDs for audit.

### 5.9 Extreme QPS tactics

| Tactic | Effect |
|--------|--------|
| Query cache | Cuts fanout |
| Replica scale-out | Linearish read scale |
| Hedged requests | Tail latency |
| Admission / 429 | Protect |
| Static rank cut | Less scoring |
| Keyword-only fallback | Survive ANN brownout |
| Edge regional caches | Geo QPS |

### 5.10 Cost controls

- Embed async with spot for backfill.
- LLM answer admission + shorter contexts.
- Prefix cache on RAG system prompts.
- Store vectors quantized.
- Don’t LLM-re-rank every query.

---

## 6. Wrap-Up

### 6.1 What we designed

A **billion-document hybrid search** system: Kafka ingest, chunk/embed, sharded BM25+HNSW segments with ACL bitsets, coordinator scatter-gather with caches, and a **cost-aware cascade** into cross-encoder / LLM re-rank / RAG that degrades cleanly under GPU pressure.

### 6.2 Progressive scale

| Scale | Change |
|-------|--------|
| 1B / 10K QPS | 256 shards; Redis caches; embed fleet |
| 10× | Disaggregate; more replicas; RAG admission |
| 100× | PQ; cells; hierarchical fanout reduction |
| 1,000× | Multi-tier cold; regional corpora; rare LLM |

### 6.3 Deal-breakers

1. ACL leak via cache or RAG context.  
2. Sizing GPUs as if every search is an LLM call.  
3. Unbounded scatter without deadlines.  
4. Blocking ingest on interactive query pools.  
5. Answering without citations when claiming grounded.

### 6.4 Closing line

> Shard hybrid indexes for a billion docs, cache aggressively with ACL in the key, and treat LLMs as a scarce re-rank/answer tier—not the retrieval engine itself.

---

## 7. Deeper / Related Interview Questions

### 7.1 Why hybrid not vector-only?

**A:** Exact tokens, IDs, rare terms still need BM25; vectors shine on paraphrase. Fusion beats either alone for many corpora.

### 7.2 How many shards for 1B docs?

**A:** Target shard size (e.g. 2–10M docs) → hundreds of shards; tune for memory and fanout. 256 is a reasonable interview default.

### 7.3 Broadcast fanout expensive—alternatives?

**A:** Caching, term routing for keyword, centroid routing for ANN, hierarchical indexes, early termination.

### 7.4 HNSW vs IVF-PQ?

**A:** HNSW: latency/recall great, memory heavy. IVF-PQ: smaller, more tune knobs, slight recall loss. Migrate as memory bites.

### 7.5 How to integrate LLM re-rank cheaply?

**A:** Only top-10–20; microbatch; admission; skip when hybrid confidence high; distilled re-rankers first.

### 7.6 Query cache + personalization/ACL?

**A:** Include ACL fingerprint (and user/tier if personalized) in key; short TTL; invalidate on revoke.

### 7.7 Delete SLO harder than add—why?

**A:** Must not serve disallowed content; touches caches, replicas, bitsets, RAG. Prioritize tombstone path.

### 7.8 How do you measure recall at billion scale?

**A:** Labeled sets + proxy online metrics (CTR); neighbor overlap tests; never full exhaustive except samples.

### 7.9 Embedding model change?

**A:** Dual index spaces; background re-embed; switch queries when coverage threshold met; keep old for rollback.

### 7.10 What if one shard is hot?

**A:** Split shard; rebalance; cache; check hash skew; isolate tenant if tenant-hot.

### 7.11 RAG prompt injection from docs?

**A:** Untrusted delimiters, instructions hierarchy, filters, cite-only, refuse tool side effects.

### 7.12 Coordinators stateful?

**A:** Mostly stateless; caches aside; session affinity optional.

### 7.13 Consistency of hybrid scores across replicas?

**A:** Same segment gen; approximate ANN OK; version in response for debugging.

### 7.14 Why not put all vectors in a single specialized DB?

**A:** Viable (FAISS/Milvus/ScaNN service). Trade-op complexity vs co-located segments. At 1B either works if sharded; operational preference.

### 7.15 Tail latency killers?

**A:** Slow shard, GC, merge storms, ANN ef too high, cache stampede, LLM queue. Hedge + throttle merges + admission.

### 7.16 Multi-region reads?

**A:** Replicate segments async; accept lag; writes home region; cache at edge.

### 7.17 How does Anthropic-style prompt cache help search?

**A:** RAG system prompts + tool schemas cache; repeated answer templates; not a substitute for doc index cache.

### 7.18 Fair multi-tenant ingest?

**A:** Per-tenant quotas/queues; weighted fair scheduling; noisy neighbor cells.

### 7.19 Exact phrase queries?

**A:** Positional postings; hybrid still runs but BM25/phrase dominates ranking features.

### 7.20 When to refuse an answer?

**A:** Top score below threshold; conflicting evidence; ACL empty; policy risk—return hits only.

### 7.21 Cross-encoder batching vs latency?

**A:** Tiny microbatches (0–5ms) or per-query for strict latency; batch harder on interactive.

### 7.22 Index merge storms?

**A:** Tiered merge policy; throttle with query load signal; prefer off-peak.

### 7.23 How to capacity-plan GPUs?

**A:** Separate embed vs re-rank vs generate pools; use tokens/s and QPS×context; never one pooled free-for-all.

### 7.24 Click privacy?

**A:** Aggregate; retention limits; ACL on logs; careful with enterprise contracts.

### 7.25 Canary ranking changes?

**A:** Shadow rank; interleaving; offline eval gates; gradual % traffic.

### 7.26 Document updates frequency high?

**A:** Incremental segment updates; chunk-level re-embed only changed; versioning.

### 7.27 Memory vs disk for postings?

**A:** Hot postings memory-mapped; cold on NVMe; page cache friendliness.

### 7.28 Failure of ACL service?

**A:** Fail-closed queries; alert; cached expansions short TTL only if revoke path still solid—be careful.

### 7.29 Why RRF?

**A:** Robust fusion without score calibration between BM25 and ANN; simple MVP.

### 7.30 One-liner

**A:** Shard hybrid search for a billion docs; cache with ACL; cascade LLMs as scarce polish—not the index.

### 7.31 Scatter deadline policies?

**A:** Wait for quorum of shards; fill partial; mark degraded; never wait forever.

### 7.32 How big is top-k per shard?

**A:** `ceil(K * multiplier / shards)` with floor—tune via offline recall.

### 7.33 Snippet generation cost?

**A:** Precompute or cheap highlight; don’t call LLM for snippets at 10K QPS.

### 7.34 Vector store quantization quality?

**A:** Eval recall@k after PQ; re-rank with full precision vectors for top candidates if stored sidecar.

### 7.35 Ingest exactly-once vs at-least-once?

**A:** At-least-once + idempotent upsert is standard.

### 7.36 Search vs answer SLA relationship?

**A:** Answer SLA includes retrieve budget; protect retrieve from answer GPUs via isolation.

### 7.37 Cold start new shard replica?

**A:** Copy segments from peer/object store; catch up tombstones; join when gen caught up.

### 7.38 Eval for RAG faithfulness?

**A:** Citation accuracy, groundedness judges, human sample; block launches on regressions.

### 7.39 Why separate Kafka topics for ACL deletes?

**A:** Priority and independent scaling; faster path than full re-index.

### 7.40 Whiteboard checklist

1. 1B → shards/storage math  
2. Split ingest/query/LLM loads  
3. Hybrid + RRF  
4. ACL fail-closed + cache key  
5. Cascade re-rank  
6. Admission on RAG  
7. Degrade paths  
8. 10×/100×/1,000× story  

---

## Appendix A: Coordinator algorithm (sketch)

```text
function search(q, principal):
  acl_fp = expand(principal)
  if cache = get(q, acl_fp): return cache
  qv = embed_cached(q)
  deadlines = now + 150ms
  parallel for shard in shards:
    hits += shard.search(q, qv, k_i, acl_fp)
  merged = fuse(hits)
  ranked = l1_rank(merged)
  maybe_rerank(ranked)
  cache.put(...)
  return top_k
```

## Appendix B: RRF parameters

```text
k = 60 typical
Use ranks from BM25 list and ANN list
Optional third list: popularity
```

## Appendix C: Segment file layout

```text
segment/
  meta.json          # gen, embed_version, doc_count
  postings/
  vectors/hnsw.bin
  acl/bitset.u64
  tombstones.log
  checksums
```

## Appendix D: Capacity worksheet

```text
search_qps =
shards =
fanout_factor =
shard_qps = search_qps * fanout_factor / shards_hit_policy
rag_qps =
out_tok_s = rag_qps * avg_out
in_tok_s = rag_qps * avg_ctx
gpus_decode ≈ out_tok_s / gpu_out_tps
gpus_prefill ≈ in_tok_s / gpu_in_tps
```

## Appendix E: Degradation matrix

| Signal | Action |
|--------|--------|
| GPU queue ↑ | disable LLM re-rank → disable answer |
| Shard p99 ↑ | reduce efSearch / k; serve cache more |
| Embed lag ↑ | keyword-only for new docs banner |
| ACL down | fail closed |

## Appendix F: Cache key fields

```text
q_text, locale, mode, top_k, filters,
acl_fp, embed_version, index_gen_major, ranker_version
```

## Appendix G: Ingest priorities

```text
P0: ACL revoke / delete
P1: security-sensitive space updates
P2: normal upserts
P3: bulk backfill
```

## Appendix H: Offline eval suite hooks

- Recall@10 vs human qrels  
- Hybrid vs BM25 delta  
- ACL leak tests (must be zero)  
- RAG citation precision  
- p99 regress gates  

## Appendix I: Hedged request policy

```text
Send to primary replica; if no response in p95*0.5 send hedge to secondary; cancel loser
Cap hedge rate to 5–10%
```

## Appendix J: Token budgeting for RAG

```text
system + safety ≤ 1K
chunks ≤ 3K
user question ≤ 0.5K
reserve output 0.5–1K
drop lowest-rank chunks first
```

## Appendix K: Noisy neighbor controls

- Per-tenant QPS limits  
- Separate overwhelm queues  
- Dedicated cell for huge tenants  

## Appendix L: Re-embed rollout

```text
1. Write new vectors to side index
2. Backfill to X% coverage
3. Dual-read compare
4. Switch
5. GC old vectors
```

## Appendix M: Error codes (API)

| Code | Meaning |
|------|---------|
| 429 | Admission |
| 409 | Version conflict upsert |
| 424 | ACL service unavailable (fail closed) |
| 206 | Degraded partial search (if used) |

## Appendix N: What “1B docs” means in interview

Clarify avg size, chunks/doc, writable vs read-only archive mix, and whether 1B is parent docs or chunks—**math changes a lot**.

## Appendix O: Closing math sanity

```text
10K QPS × 256 shards = 2.56M shard-qps aggregate if naive broadcast
That's why caches, pruning, and replicas exist—call this out proactively
```

---

*End of document — Distributed Search over ~1B Documents (Anthropic interview prep)*
