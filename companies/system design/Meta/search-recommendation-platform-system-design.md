# System Design: Search & Recommendation Platform (Meta)

> **Focus areas:** Dual retrieval (search + feed rank) · Candidate generation · Multi-stage ranking · Feature store · Embedding indexes · Personalization · Integrity/spam · Freshness vs relevance  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split query/ingest/feature/training planes; explicit approx ANN vs exact filter; deal-breakers for “one giant model scores everything online” fantasies  
> **Interview theme:** Classic Meta L5+ — unified discovery surface combining keyword search and personalized recommendations at social scale

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

Goal: **bound the product**—a **Search & Recommendation Platform** that powers keyword search (people, posts, Groups, Pages, Reels) and personalized recommendation surfaces (Feed/Explore/Suggested) with shared candidate generation, ranking, and feature infrastructure.

### 1.0 What this is / is not

| Dimension | **Search + Rec platform (this doc)** | Not this |
|-----------|--------------------------------------|----------|
| Primary job | Retrieve + rank content/people for query or user context | Full social graph product, Stories, Chat |
| Success | Relevant results + engaging recs; low latency | Perfect offline IR research paper |
| Data plane | Indexing + feature pipelines + online serve | Training cluster internals (hooks only) |
| Query | Search API + Rec API with shared stages | Ad-hoc warehouse SQL |
| Correctness | Fresh enough; ranked lists approximate | Strongly consistent global index for every write |

**Scope statement:** Design Meta-style search + recommendation: ingest/index content, generate candidates (lexical + ANN + social), multi-stage rank, personalize, cache, and scale through progressive jumps.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Surfaces? | Search box + Explore/Suggested + optional Feed mix-in | Two entry APIs; shared ranking stack |
| F2 | Entities? | Posts, Reels, People, Pages, Groups, Hashtags | Typed indexes + entity routers |
| F3 | Query types? | Keyword, @people, hashtag, trending, empty-query recs | Query understanding + intent classification |
| F4 | Personalization? | Yes — social graph, interests, history | User/item features; real-time signals |
| F5 | Freshness? | New posts searchable in seconds–minutes | Near-line index + streaming features |
| F6 | Ranking goal? | Relevance (search) + engagement/quality (recs) | Multi-objective; separate loss/weights |
| F7 | Filters? | Time, type, friends-only, language | Post-filter + constrained retrieval |
| F8 | Integrity? | Spam, misinfo, NSFW demotion/removal | Integrity stage before final blend |
| F9 | Autocomplete? | Typeahead for people/hashtags/queries | Separate low-latency prefix service |
| F10 | Explainability? | Soft (“Because you follow X”) Phase 1.5 | Reason codes in ranker debug |
| F11 | A/B? | Continuous experiments | Layered holdouts; config service |
| F12 | Admin? | Suppress entity; force boost; reindex | Control plane separate |

**MVP functional scope:**

1. Keyword search across posts + people + pages (typed tabs).  
2. Personalized recommendation API for Explore-like surface (empty query / “for you”).  
3. Shared pipeline: query understanding → candidate gen (multi-source) → light rank → heavy rank → blend/diversity → integrity.  
4. Near-real-time indexing for new public posts; people graph updates.  
5. Feature store (online + offline) for user/item/context.  
6. Autocomplete for people and popular queries.  
7. Caching at edge/results for popular queries; personalized cache carefully keyed.  
8. Experimentation hooks and integrity demotion.

**Out of MVP:**

- Full ads auction integration (mention as sibling)  
- Perfect multilingual semantic search for every language  
- Training loop end-to-end (assume models exist; design serving + features)  
- Universal search over private Messenger content  
- Real-time collaborative filtering rebuild every second

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Search latency | Feels instant | p99 < 200–300ms end-to-end |
| N2 | Rec latency | Scroll-smooth | p99 < 300–500ms first page |
| N3 | Index freshness (public posts) | Near-line | p99 searchable < 60s; aspirational < 10s hot path |
| N4 | Availability | Critical path | 99.9%+ with degraded modes |
| N5 | Personalization quality | Beats non-personalized | Online metrics; offline NDCG/AUC gates |
| N6 | Privacy | Respect ACL / audience | Filter before return; never leak private |
| N7 | Cost | Ranker GPU/CPU bounded | Multi-stage; cache; limit heavy score N |
| N8 | Multi-region | Global users | Regional serve; global index shards by key |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User types “Olympics highlights” → intent=content → lexical + embedding candidates → rank → Reels/posts mix.  
2. Empty Explore open → social + interest + trending candidates → heavy rank → diversified page.  
3. Typeahead “jo” → people prefix + friends boost.  
4. New Reel posted → Kafka → indexer → ANN upsert → appears in related within freshness SLO.  
5. Integrity demotes spam farm content before blend.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Private post in inverted index | ACL filter mandatory; fail closed on ACL service errors for private |
| Celebrity query tsunami | Result cache + precompute top entities; shed heavy rank |
| Embedding index lag | Fall back lexical + social; mark degraded quality |
| Feature store timeout | Use defaults / cached user tower; never block forever |
| Filter wipes all candidates | Widen retrieval; relax filters progressively |
| Friend-only search | Constrain retrieval to author∈friends OR post-filter with posting list intersect |
| Language mismatch | Query lang detect; prefer same-lang; allow translate recall Phase 2 |
| Duplicate near-identical Reels | Diversity / clustering in blender |
| Stale personalized cache | Short TTL; key includes feature version |
| Ranker OOM / timeout | Return light-rank order; SLO burn |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 50M | 500M | — mega | extreme |
| Search QPS (peak) | 50K | 500K | 5M | 50M |
| Rec QPS (peak) | 100K | 1M | 10M | 100M |
| Documents / posts indexed | 50B | 500B | multi-T | retention tiers |
| New docs / day | 5B | 50B | 500B | cell fabric |
| Embedding dim | 64–128 | 128 | 128–256 | product quantization |
| Candidates before heavy rank | 500–2K | 1–5K | hierarchical | multi-tower |
| Heavy rank scored / request | 100–300 | 100–300 | 50–200 | distilled |
| Feature lookups / request | 200–1K | same | batched | edge features |
| ANN QPS | 50K | 500K | 5M | sharded cells |
| Index size (text+ANN) | tens PB logical | ×10 | ×100 | tiered |

**What each jump forces:**

- **10×:** Multi-stage mandatory; result cache; ANN sharding; online feature store HA.  
- **100×:** Regional cells; two-tower retrieval; heavy rank distillation; integrity async pre-scores.  
- **1,000×:** Hierarchical retrieval; edge personalization lite; per-vertical platforms; aggressive tiering.

### 1.5 Etc. (Constraints & Assumptions)

- Social graph and auth/ACL services exist; we call them.  
- Models (two-tower, L2/L3 rankers) are trained offline; we design **serving + features + retrieval**.  
- Public vs friends vs private audiences are first-class.  
- Ads may reuse candidates later; MVP is organic discovery.

**Scope statement to repeat back:**

> Design a Meta search and recommendation platform: near-line indexing, multi-source candidate generation (lexical, ANN, social, trending), multi-stage personalized ranking with a feature store, integrity filtering, autocomplete, and progressive scale via sharding, caching, and hierarchical retrieval—respecting ACLs and freshness SLOs.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Search QPS** | Typed queries | ~50K | Online serve |
| **Rec QPS** | Explore/Feed mix | ~100K | Online serve |
| **Autocomplete** | Prefix | ~200K | Edge/specialized |
| **Index writes** | New/edits/deletes | ~50K–200K/s | Streaming index |
| **Feature updates** | User/item real-time | ~100K–1M/s | Feature stream |
| **ANN upserts** | Embedding updates | subset of docs | Vector index |
| **Training exports** | Offline logs | batch | Warehouse |

**Anti-pattern:** one “QPS” mixing typeahead, heavy rank, and index builds.

### 2.2 Latency budget (search p99 ~250ms)

```text
Gateway + auth:           10–20ms
Query understanding:      10–20ms
Candidate gen (parallel): 40–80ms
Feature fetch (batched):  20–40ms
Light rank:               10–20ms
Heavy rank (N=200):       40–80ms
Blend + integrity:        10–20ms
Packaging:                5–10ms
Cache hit short-circuits most of this for head queries
```

### 2.3 Candidate fanout math

```text
Sources in parallel:
  Lexical inverted: 300
  ANN two-tower: 300
  Social (friends-of-friends / follow): 200
  Trending / editorials: 50
  Continuations / session: 50
Union ~700–1K unique after dedup
Light rank → 200
Heavy rank → 50 return page (+ prefetch)
```

### 2.4 Index storage (order of magnitude)

```text
50B docs × 500B text/posting metadata avg ≈ 25 PB raw-ish (compressed much less)
Posting lists highly compressed; forward store columnar
ANN: 50B × 128 × 4B = 25.6 PB full precision → PQ/OPQ → ~1–3 PB practical with sharding + hot/cold
Conclusion: tiered storage + product quantization mandatory at Meta scale
```

### 2.5 Feature store

```text
Online: user embedding 128×4 + sparse IDs + counters ≈ 2–8KB / user hot
50M DAU hot set × 4KB = 200 GB — fits Redis/Memcached tier
Item features similar; cache by item_id
Real-time counters (clicks, dwell) via Kafka → feature writers
```

### 2.6 Cost control lever

```text
Heavy neural rank dominates CPU/GPU
Must bound N scored; cache head queries; distill L3; early-exit easy rejects
Deal-breaker: score 10K docs with giant model per request
```

### 2.7 Inverted index posting math

```text
Hot term "the" — never index as free posting (stopword)
Medium term: 10M docs × 8B posting ≈ 80MB compressed sparingly
Query with 3 terms: intersect/TAAT top-k; bound per-shard work
50K search QPS × 4 shard fanout = 200K shard queries — cache head terms
```

### 2.8 ANN QPS & memory

```text
IVF-PQ: 50B vectors × 32B codes ≈ 1.6 PB raw codes → sharded across cells
Query: encode 1ms + nprobe lists scan → p99 20–60ms per shard
Fanout 8 shards → need early terminate / router to cut fanout at 100×
```

### 2.9 Two-tower serving cost

```text
Online: encode query/user once per request (GPU/CPU batch)
Offline: item tower refresh hours–day + streaming upsert for new docs
Mismatch: stale item vectors OK; wrong ACL not OK
```

### 2.10 Feedback loop volume

```text
100K rec QPS × ~5 impressions logged ≈ 500K events/s → Kafka
Join with clicks/dwell → training examples; sample negatives
Online counters: click/dwell last-N-min per user/item for L3 features
```

### 2.11 Progressive score/s worksheet

| Scale | Orchestrations/s | Heavy N | Scores/s | Mitigation |
|-------|------------------|---------|----------|------------|
| Base | 100K | 200 | 20M | Multi-stage |
| 10× | 500K | 150 | 75M | Cache + distill |
| 100× | 2M | 100 | 200M | Cells + hierarchical CG |
| 1,000× | 10M+ | 50–80 | edge lite | Vertical split |

### 2.12 BOTE anti-patterns

| Anti-pattern | Math failure |
|--------------|--------------|
| One model scores corpus | Scores/s → ∞ |
| ANN-only keyword search | Named-entity miss rate |
| Unbounded L3 N | GPU melt |
| Personalized cache key=`q` | Privacy × wrong UX |
| Batch features only (hours) | Session personalization dead |

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/search?q=&type=&cursor=` | Typed search results page |
| `GET /v1/recommend?surface=explore&cursor=` | Personalized recs |
| `GET /v1/suggest?q=` | Autocomplete |
| `POST /internal/index/upsert` | Indexer ingest (prefer bus) |
| `POST /admin/suppress` | Integrity suppress |
| `GET /v1/health` | Dependency + freshness |

**Request context (recs):**

```text
RecRequest {
  user_id, surface, session_id,
  device, locale, country,
  seen_ids[], cursor, limit,
  experiment_layers[]
}
```

### 3.2 Data model

| Store | Key | Value |
|-------|-----|-------|
| Inverted index | term → postings | doc_id, payload (author, ts, type) |
| Forward / doc store | doc_id | text, media refs, ACL bits |
| ANN index | vector | doc_id + PQ codes |
| People index | prefix / term | user_id ranked |
| Feature online | user_id / doc_id | tensors + sparse |
| Result cache | hash(q, filters, locale) | non-personalized head |
| Personalized cache | (user, surface, feature_ver) | short TTL page |
| Graph service | user | friends / follows (external) |

### 3.3 Multi-stage funnel — Why X over Y

| Stage | Job | Why not skip |
|-------|-----|--------------|
| Query understanding | Intent, entities, lang, rewrite | Wrong index otherwise |
| Candidate gen | High recall, cheap | Heavy rank can't see whole corpus |
| Light rank | Filter to hundreds | Cost |
| Heavy rank | Quality | Engagement/relevance |
| Blender | Diversity, calibration | Filter bubbles / dupes |
| Integrity | Safety | Trust |

**Deal-breaker:** single-stage “embed query, ANN top-50, done” for social search—misses keyword precision, ACL, freshness, people search.

### 3.4 Retrieval sources — Why X over Y

| Source | Pros | Cons | Use |
|--------|------|------|-----|
| **Lexical (BM25/boolean)** | Precision, exact tokens | Vocabulary mismatch | Named entities, keywords |
| **ANN two-tower** | Semantic recall | Less precise; index lag | Explore, long queries |
| **Social graph** | Strong personalization | Filter bubble | Friends content, people |
| **Trending / geo** | Fresh viral | Noise | Empty query / newsy |
| **Co-visitation** | Simple CF | Cold start | Related items |
| **Collaboration only** | — | Weak for search keywords | Not sole source |

**Chosen MVP:** parallel lexical + ANN + social + trending; union + dedup.

### 3.5 Ranking — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Hand-tuned linear | Debuggable | Caps quality | Bootstrap |
| GBDT light rank | Strong tabular | Limited semantic | L2 MVP |
| Deep L3 | Best quality | Cost/latency | Final N |
| One giant online model | — | Latency/cost deal-breaker | No |
| Offline only batch rank | Cheap | Stale | Not for interactive |

**Chosen:** L1 retrieval → L2 GBDT/small NN → L3 deep on ≤300 → blend.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Architecture | Multi-stage funnel | Cost × quality | Monolithic scorer on corpus |
| Indexes | Lexical + ANN + people | Complementary recall | ANN-only search |
| Features | Online store + stream | Personalization | Batch features only (hours lag) |
| ACL | Filter before return + constrained retrieval | Privacy | Post-hoc client filter |
| Cache | Head query + short personalized | QPS | Cache personalized forever |
| Integrity | Precomputed scores + online rules | Trust | Rank engagement only |
| Scale | Shard by doc_id / term / user cell | Growth | Single global Lucene |

### 3.7 Expanded HLD tradeoffs

| Axis | Option A | Option B | MVP | Escalate when |
|------|----------|----------|-----|---------------|
| Retrieval | Lexical-only | Lexical+ANN+social+trend | Multi-source | — |
| ANN structure | HNSW everywhere | IVF-PQ sharded | IVF-PQ + fresh HNSW niche | RAM allows more HNSW |
| Ranker | Giant L3 on 2K | Distilled L3 on ≤300 | Bound N + distill | QoE regresses |
| Feedback | Offline only | Offline + realtime counters | Both | Bandits at 100× |
| Cache | None | Head SERP + short personalized | Both | Edge push at 1,000× |

**Anti-patterns:** Elasticsearch-as-entire-platform; one transformer online; ACL in the client; exact KNN at 50B docs.

---

## 4. Architecture Diagram

```text
                         +---------------------------+
   Clients ------------> | Edge / API Gateway        |
                         | auth, ratelimit, route    |
                         +-------------+-------------+
                                       |
                 +---------------------+---------------------+
                 |                     |                     |
                 v                     v                     v
          +-------------+       +-------------+       +-------------+
          | Suggest svc |       | Search svc  |       | Rec svc     |
          | (prefix)    |       | orchestrator|       | orchestrator|
          +-------------+       +------+------+       +------+------+
                                       |                     |
                                       +----------+----------+
                                                  |
                                                  v
                                       +----------+----------+
                                       | Query Understanding |
                                       | intent, NER, rewrite|
                                       +----------+----------+
                                                  |
                  +---------------+---------------+---------------+
                  |               |               |               |
                  v               v               v               v
           +-----------+  +-----------+  +-----------+  +-----------+
           | Lexical   |  | ANN /     |  | Social /  |  | Trending  |
           | Indexers  |  | two-tower |  | Graph CG  |  | / Geo     |
           +-----------+  +-----------+  +-----------+  +-----------+
                  \               |               |               /
                   \              |               |              /
                    +-------------+---------------+-------------+
                                  |
                                  v
                       +----------+----------+
                       | Light Ranker (L2)   |
                       +----------+----------+
                                  |
                                  v
                       +----------+----------+
                       | Feature Store       |<--- stream features
                       | (online)            |<--- user/item towers
                       +----------+----------+
                                  |
                                  v
                       +----------+----------+
                       | Heavy Ranker (L3)   |
                       +----------+----------+
                                  |
                                  v
                       +----------+----------+
                       | Blender + Integrity |
                       +----------+----------+
                                  |
                                  v
                              Results page

   Ingest path (async):
   Create Post/Reel -> Kafka -> Doc parser -> Lexical index + Embedding worker
                              -> Feature writers -> Integrity scorer
```

**Search path:**

```text
GET /search?q=
  -> QU
  -> parallel CG
  -> ACL filter
  -> L2 -> features -> L3 -> blend
  -> cache store (if cacheable)
```

**Rec path:**

```text
GET /recommend
  -> user tower / session features
  -> CG (ANN + social + trending)
  -> seen filter
  -> L2/L3 -> diversity
  -> page + cursor
```

**Index path:**

```text
Kafka(doc_events)
  -> normalize + ACL snapshot
  -> inverted index update (near-line)
  -> embedding encode -> ANN upsert
  -> tombstones on delete/suppress
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Never return docs the viewer cannot see** (ACL fail-closed for non-public).  
2. **Heavy rank N is bounded**; timeouts degrade to L2 order.  
3. **Integrity suppress wins** over engagement score.  
4. **Cursor pagination stable enough** within a session (snapshot or tie-break).  
5. **Feature version mismatch** may serve slightly stale personalization, not wrong ACL.

#### 5.1.2 Degradation ladder

| Failure | Degraded mode |
|---------|---------------|
| ANN down | Lexical + social only |
| Feature store slow | Cached user embedding / defaults |
| L3 timeout | L2 ranking |
| Integrity service down | Conservative deny-list local cache; reduce viral boost |
| Index lag | Serve with freshness banner internally; rely on cached head |

#### 5.1.3 Idempotent indexing

```text
doc_version / updated_at on each upsert
indexer applies max-version wins
deletes = tombstones with version
ANN upsert same versioning
```

#### 5.1.4 ACL correctness

| Audience | Strategy |
|----------|----------|
| Public | Index freely; still check takedown |
| Friends | Constrain OR filter via graph bloom/bitset |
| Custom lists | Prefer not full-text MVP; fetch by id + check |
| Private | **Do not** put body in shared public shards; private index or no search |

**Deal-breaker:** indexing all private text into a world-readable shard and “filtering in the UI.”

### 5.2 Scalability

#### 5.2.1 Sharding

| Component | Shard key | Notes |
|-----------|-----------|-------|
| Lexical | term hash / doc shard | Scatter-gather top terms |
| ANN | IVF/HNSW shards by media type + id | Fanout limited |
| Features | user_id / doc_id | Consistent hash |
| Rec orchestrator | stateless | Scale horizontally |
| People search | prefix shards | Hot celebrities replicated |

#### 5.2.2 Hot keys / celebrities

```text
Precompute SERPs for top entities
Replicate posting lists for ultra-hot terms
Cache people cards at edge
```

#### 5.2.3 Hierarchical retrieval at 100×+

```text
L0: coarse ANN / category routers → cluster
L1: per-cluster ANN + lexical
L2/L3: as before
Reduces fanout vs querying all shards every time
```

#### 5.2.4 Progressive scale map

| Scale | Must add |
|-------|----------|
| Baseline | Multi-stage; Redis features; dual index |
| 10× | Result cache; ANN PQ; async integrity |
| 100× | Regional cells; distilled L3; two-tower CG |
| 1,000× | Hierarchical CG; edge lite-rank; vertical splits |

### 5.3 Maintainability

#### 5.3.1 Ownership boundaries

| Team-shaped module | Owns |
|--------------------|------|
| Indexing | Doc pipeline, lexical freshness |
| Retrieval | CG sources, ANN |
| Ranking | L2/L3 models, blender |
| Features | Schemas, online store |
| Integrity | Policies, suppress |
| Experimentation | Layer assignment |

#### 5.3.2 Feature hygiene

```text
Feature registry with owners, TTL, PII flags
Training-serving skew monitors
Schema evolution via versioned feature groups
```

#### 5.3.3 Experimentation

```text
Layered experiments: retrieval / L2 / L3 / blend
Holdouts for long-term metrics
Config service pushes model ids per layer
```

#### 5.3.4 Observability

| Signal | Why |
|--------|-----|
| p99 per stage | Find regressions |
| Recall@K proxy (logged) | CG health |
| Empty rate / filter-all rate | ACL or bug |
| Freshness watermark | Index lag |
| Integrity coverage | Safety |
| Cache hit rate | Cost |

### 5.4 Query understanding deep dive

```text
pipeline:
  normalize (unicode, case)
  language detect
  spell correct (conservative)
  entity link (people, pages, events)
  intent: people | content | hashtag | navigational
  rewrite: synonym / stemming light
  media preference: reel vs post from query cues
```

Navigational (“Instagram”) → boost official Page.  
People intent → prefer people index.  
Content intent → posts/Reels.

### 5.5 Embedding / ANN deep dive

| Choice | Why |
|--------|-----|
| Two-tower (user/query × item) | Fast ANN retrieval |
| HNSW or IVF-PQ | Latency/memory tradeoff |
| Dual indexes | Fresh small + durable large |
| Periodic full rebuild + streaming upsert | Quality + freshness |

**Deal-breaker:** claiming exact nearest neighbor over 50B vectors online.

### 5.6 Personalization signals

| Signal | Freshness | Store |
|--------|-----------|-------|
| Long-term interests | Daily | Offline → online |
| Embeddings | Hours–day | Tower publish |
| Session clicks/dwell | Seconds | Real-time feature |
| Social graph | Minutes | Graph service |
| Suppressions | Immediate | Integrity |

### 5.7 Blender / diversity

```text
MMR or determinantal / greedy diversity on embedding distance
Author diversity caps
Type mix targets (reel/post/people)
Calibration so scores comparable across CG sources
```

### 5.8 Autocomplete

Separate service: tries / finite-state transducer + popularity prior + friends boost.  
p99 < 50ms; mostly edge/cached. Do not run L3 ranker on each keystroke.

### 5.9 Multi-objective ranking

```text
score = w_rel * s_rel + w_eng * s_eng + w_qual * s_qual - w_integrity * penalty
Search: higher w_rel
Recs: higher w_eng with quality floor
```

Offline policy / Bandits can tune weights with guardrails.

### 5.10 Privacy & logging

- Log training examples with ACL-safe joins.  
- Respect deletion/GDPR: tombstone indexes + feature erase.  
- Differential access: debug tools need audited break-glass.

### 5.11 Nested deep dive — Inverted index

#### 5.11.1 Structures

```text
term → posting list: (doc_id, payload: author_id, ts, type, audience_bits)
forward store: doc_id → text/snippet fields, media refs
lexicon / term dictionary with DF for BM25 IDF
segments: near-line small + compacted durable
```

#### 5.11.2 Query execution

| Strategy | Use |
|----------|-----|
| TAAT (term-at-a-time) | Early exit top-k with WAND/BMW |
| DAAT (doc-at-a-time) | Exact boolean AND |
| Bounded per-shard k | Merge globally |

```text
parse → stopword drop → select top informative terms by IDF
scatter to term/doc shards → merge → pass candidates to L2
```

#### 5.11.3 Freshness & segments

```text
Kafka doc_event → near-line segment (seconds)
Periodic merge to medium; cold tier for aged docs
Deletes/tombstones: apply to all live segments; version wins
Dual-read during index swap (blue/green alias)
```

#### 5.11.4 Hot terms & celebrities

- Replicate ultra-hot posting lists.  
- Precompute navigational SERPs.  
- Never index pure stopwords as free terms.

#### 5.11.5 Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| One giant mutable posting file | Write contention; slow refresh |
| Skip tombstones “eventually” | Privacy/integrity bugs |
| Unbounded term fanout from rewrite | Shard overload |

### 5.12 Nested deep dive — ANN

#### 5.12.1 Index choices

| Index | Pros | Cons | Meta-like use |
|-------|------|------|---------------|
| HNSW | High recall | RAM heavy | Hot verticals |
| IVF-PQ | Memory efficient | Tune nprobe | **Broad corpus** |
| DiskANN-class | Huge corpora | Ops complexity | 100×+ |

#### 5.12.2 Dual ANN

```text
Fresh shard: streaming upserts last hours/days (smaller)
Durable shard: batch-built snapshot
Query: parallel both; merge by distance / calibrated score
```

#### 5.12.3 Product quantization

```text
128-d float32 = 512B → PQ 32–64B codes
Recall@100 target ≥ 0.9 vs exact on eval sample
Deal-breaker: claim exact KNN over 50B vectors online
```

#### 5.12.4 Ops

- Build pipeline: sample → train PQ → encode → publish → delta topic.  
- Poisoning: integrity before publish; rate-limit upserts.  
- Degradation: if ANN down → lexical + social only.

### 5.13 Nested deep dive — Two-tower retrieval

#### 5.13.1 Geometry

```text
Query/User tower(f_user, f_context, f_query) → q_vec
Item tower(f_item) → i_vec   # precomputed
score ≈ dot(q_vec, i_vec) or cosine
ANN retrieves top-K by score
```

#### 5.13.2 Serving path

```text
Rec: load user embedding from feature store (or encode online)
Search: encode rewritten query text (+ context)
ANN top-K → tag cg_source=two_tower → L2/L3
```

#### 5.13.3 Limits (say in interview)

- Cannot model fine cross features (that’s L3).  
- Item freshness depends on upsert lag.  
- Multilingual / multimodal may need separate towers.  
- Still must ACL-filter outputs.

#### 5.13.4 Training hooks (serving-aware)

```text
In-batch negatives + hard negatives from ANN
Log features as served to reduce train-serve skew
Publish item tower snapshot + streaming delta
```

### 5.14 Nested deep dive — Feedback loops

#### 5.14.1 Loop diagram

```text
Impression/click/dwell/hide/report
  → Kafka
  → (a) real-time feature writers (counters, session emb)
  → (b) training log join → offline model update
  → (c) integrity labels → suppress
New models → config service → L2/L3/CG layers
```

#### 5.14.2 Online vs offline feedback

| Loop | Latency | Use |
|------|---------|-----|
| Real-time counters | seconds | L3 features, session |
| Near-line embeddings | hours | Tower refresh |
| Offline ranker train | days | Quality jumps |
| Integrity | seconds–hours | Safety |

#### 5.14.3 Failure modes of feedback

| Failure | Symptom | Guardrail |
|---------|---------|-----------|
| Clickbait loop | Eng↑ quality↓ | Quality floor + holdouts |
| Filter bubble | Diversity↓ | Blender constraints + explore |
| Spam poisoning | Bad clusters in ANN | Integrity before index |
| Train-serve skew | Offline≠online | Log-as-served; monitors |

#### 5.14.4 Exploration

```text
Reserve ε slots for explore/cold-start inventory
Log propensities for counterfactual / IPS offline eval
Never explore integrity-blocked items
```

### 5.15 Nested deep dive — HLD tradeoffs, scale, deal-breakers

#### 5.15.1 Expanded tradeoffs

| Axis | A | B | MVP pick |
|------|---|---|----------|
| CG breadth | Lexical only | Lexical+ANN+social+trend | Multi-source |
| L3 size | Huge model | Distilled | Distill under latency |
| Cache | None | Head + short personalized | Both |
| ACL | Post-filter only | Constrain + final | Constrain + final |

#### 5.15.2 Progressive scale table

| Scale | Index | CG | Rank | Feedback |
|-------|-------|----|------|----------|
| Base | Dual lexical+ANN | 4 sources | L2+L3 | Offline + stream counters |
| 10× | PQ + result cache | +session | Distill | Skew monitors |
| 100× | Regional cells | Hierarchical | GPU pools | Bandits/guardrails |
| 1,000× | Vertical platforms | Routers | Edge lite | Closed-loop platform |

#### 5.15.3 Deal-breakers

1. Score entire corpus with one online model.  
2. ANN-only for keyword/navigational search.  
3. ACL leak / private bodies in public shards.  
4. Unbounded heavy-rank N.  
5. Personalized cache keyed only by query.  
6. Engagement-only ranking without integrity.  
7. Ignoring train-serve skew until metrics tank.

---

## 6. Wrap-Up

### 6.1 What to say in 60 seconds

> Meta search + recommendations share a multi-stage funnel: understand query/context, retrieve from lexical + ANN + social + trending, filter ACL, light then heavy rank with online features, then blend and apply integrity. Indexes update near-line; features stream; heavy scoring is strictly bounded. Scale with sharding, PQ, caches, and hierarchical retrieval. Never compromise ACL for recall.

### 6.2 Top deal-breakers

1. Scoring the whole corpus with one model online.  
2. ANN-only keyword search.  
3. Ignoring ACL / private content leakage.  
4. Unbounded heavy rank N.  
5. Personalized results cached without user/feature keying.  
6. Engagement-only ranking without integrity.

### 6.3 Progressive scale one-liner

Baseline dual-index funnel → 10× cache + PQ → 100× cells + distilled L3 → 1,000× hierarchical CG + edge lite personalization.

### 6.4 Open extensions

- Ads candidate interleaving  
- Multimodal search (image query)  
- On-device retrieval lite  
- Cross-surface unified embedding space

---

## 7. Deeper / Related Interview Questions

### Q1. Why multi-stage ranking instead of one model?

**Answer:** Cost and latency. Retrieval must scan or ANN-search enormous corpora cheaply; neural L3 can only score hundreds of candidates within a 200–300ms budget. Stages specialize: recall → cheap precision → expensive re-rank.

### Q2. How do you keep search fresh for new posts?

**Answer:** Streaming ingest from Kafka into a near-line inverted index segment + embedding upsert into a “fresh” ANN shard that is searched in parallel with the durable index. Periodically merge segments. Measure watermark lag.

### Q3. Lexical vs embeddings — when does each win?

**Answer:** Lexical wins on rare tokens, exact names, navigational queries. Embeddings win on paraphrases, semantic Explore, cold vocabulary. Meta systems run both and fuse.

### Q4. How do you enforce friends-only visibility?

**Answer:** Prefer constrained retrieval (posting lists intersected with friend bitsets / posting-list of friend authors) plus final ACL check. Fail closed if graph/ACL timed out for non-public docs.

### Q5. What is training-serving skew?

**Answer:** Feature computed differently offline vs online (timing, default, timezone). Mitigate with shared feature definitions, log-as-served features, and skew monitors.

### Q6. How does two-tower retrieval work?

**Answer:** User/query tower produces a vector; item tower precomputes item vectors in ANN. Online: encode query once, ANN top-K. Limits: less expressive interactions than cross-attention L3.

### Q7. How do you paginate personalized feeds stably?

**Answer:** Cursor encodes ranker version + timestamp + last scores/ids; filter `seen_ids`; accept small duplicates across pages rather than global snapshot of the whole corpus.

### Q8. How do you handle celebrity query load?

**Answer:** Precomputed SERPs, edge cache, replicated hot posting lists, bypass heavy personalization for pure navigational intents.

### Q9. Where does integrity sit in the stack?

**Answer:** Offline/near-line scores on items + online rules. Apply before final return; suppress wins over engagement. Some signals demote rather than hard filter.

### Q10. Why not put autocomplete on the main search stack?

**Answer:** Keystroke QPS and latency (p99≪50ms) need prefix structures and heavy caching; L3 ranking is unnecessary and too slow.

### Q11. How do you diversify recommendations?

**Answer:** Blender with author/type/embedding distance constraints (MMR-like), plus business mix targets. Diversify after scoring, not instead of ranking.

### Q12. What if the feature store is down?

**Answer:** Serve cached user towers and default item features; degrade personalization, keep ACL and lexical path up. Alert on personalization quality drop.

### Q13. How are deletes propagated?

**Answer:** Versioned tombstones to lexical + ANN + doc store; CDN/result cache purge by id; feature erase async with SLA.

### Q14. Exact vs approximate nearest neighbor?

**Answer:** Exact NN is impossible at tens of billions under latency budgets. Use HNSW/IVF-PQ with recall SLOs (e.g., recall@100 ≥ 0.9 vs exact on sample).

### Q15. How do you A/B test a new retrieval source?

**Answer:** Experiment layer on CG membership; hold out users; metrics: engagement, integrity, latency, empty rate; gate on regression guards.

### Q16. Cold-start for new users?

**Answer:** Demographic/geo/trending priors + onboarding interests + explore/exploit; rely less on long-term embedding until enough events.

### Q17. Cold-start for new Reels?

**Answer:** Content embeddings from media/text, creator affinity, limited explore inventory, integrity checks; boost exploration quota briefly.

### Q18. How do you prevent filter bubbles?

**Answer:** Diversity constraints, serendipity / explore slots, integrity quality, avoid over-weighting short-term clicks.

### Q19. Scatter-gather search cost?

**Answer:** Each query may hit many term shards; bound fanout via term selection, caching, and per-shard top-k with merge. Hot terms replicated.

### Q20. How do real-time counters work?

**Answer:** Client events → Kafka → aggregate writers → online feature keys with TTL. Ranker reads recent click/dwell rates; eventually consistent OK.

### Q21. Search vs Rec — same ranker?

**Answer:** Shared infrastructure and many features; different objective weights and CG mix. Navigational search ≠ Explore engagement.

### Q22. How do you capacity-plan L3?

**Answer:** `QPS × N_scored × cost_per_score`; reduce N, distill models, cache, early exits, GPU batching. Track utilization and p99.

### Q23. What is a deal-breaker for privacy?

**Answer:** Returning another user’s private post due to missing ACL or indexing private bodies into public shards.

### Q24. How do you monitor recall of CG?

**Answer:** Offline: labeled sets / retrieval eval. Online proxies: re-ranker score distributions, exploration logs, side-by-side human eval, counterfactual.

### Q25. Why product quantization?

**Answer:** Compress vectors to fit RAM/SSD and increase QPS; trade small recall loss for 10–20× memory reduction—mandatory at Meta doc scale.

### Q26. How would you add video-query search?

**Answer:** Multimodal encoder → video embedding index; parallel CG source; heavy rank with cross-modal features; larger latency budget.

### Q27. Consistency of index and features?

**Answer:** Eventual. Doc may rank with slightly stale features; versions help debugging. ACL/tombstones prioritized over feature freshness.

### Q28. How do you fight embedding index poisoning/spam?

**Answer:** Integrity before ANN publish; rate-limit upserts; anomaly on embedding clusters; human/policy review for viral clusters.

### Q29. Multi-region active-active?

**Answer:** Serve regionally; replicate indexes asynchronously; users pinned or routed by geo; accept brief cross-region freshness skew.

### Q30. What changes from baseline to 100×?

**Answer:** Cells, hierarchical CG, distilled L3, stronger caching, PQ everywhere, integrity precompute, stricter budgets—architecture pattern stays multi-stage.

### Q31. Why separate people search?

**Answer:** Different ranking (graph proximity, name match, social signals), prefix access patterns, and privacy; dedicated index wins.

### Q32. How do session signals enter ranking?

**Answer:** Real-time feature service updates session embedding / last-N clicked topics; orchestrator passes session_id; short TTL.

### Q33. Can we use LLM re-rankers?

**Answer:** Possibly for tiny N (e.g., top 20) in Phase 2; too slow/expensive for default path at Meta QPS without extreme distillation/speculative decoding.

### Q34. Empty result recovery?

**Answer:** Progressive relaxation: drop filters, spelling looser, broaden media types, fall back to recs for the query topic.

### Q35. Key metrics for launch?

**Answer:** Latency p99, empty rate, engagement (CTR/dwell), integrity incident rate, freshness lag, cache hit, train-serve skew, ACL error rate.

### Q36. How do inverted index segments interact with ANN freshness?

**Answer:** Lexical near-line segments and a fresh ANN shard both consume the same doc events; dual-read merges. Tombstones must hit both. Measure separate watermarks but one privacy SLO.

### Q37. What breaks two-tower quality in production?

**Answer:** Train-serve skew, stale item towers, embedding poisoning, and over-reliance without lexical precision for navigational queries.

### Q38. How do you stop engagement feedback loops from promoting spam?

**Answer:** Integrity before blend, quality floors, holdout metrics, demote clusters, rate-limit distribution — never optimize CTR alone.

### Q39. When is hierarchical retrieval mandatory?

**Answer:** When shard fanout × QPS exceeds ANN/lexical budgets (typically 100×); routers pick clusters/verticals before fine retrieval.

### Q40. Why log features as served?

**Answer:** Offline training must see the same feature values the online ranker used; otherwise models look great offline and fail online.

### Q41. Can GraphQL be the search orchestrator?

**Answer:** It can be an API facade; the orchestrator still needs multi-stage CG/rank/ACL internals — GraphQL doesn’t replace the funnel.

### Q42. Deal-breaker checklist to recite?

**Answer:** No corpus-wide online scoring; no ANN-only search; no ACL leaks; bounded L3 N; correct cache keys; integrity wins; watch skew.

---

## Appendix A — Stage latency card

```text
QU 15 | CG 60 | Feat 30 | L2 15 | L3 60 | Blend 15 ≈ 195ms + gateway
```

## Appendix B — Cache policy

| Key | TTL | Notes |
|-----|-----|-------|
| Head SERP non-personalized | 30–120s | Celebrity/news |
| Suggest | 60–300s | Popular prefixes |
| Personalized page | 5–30s | Include feature_ver |
| Item features | 1–10m | Invalidate on update |

## Appendix C — Doc event schema

```text
DocEvent {doc_id, version, op, author_id, audience, ts, text, media[], lang, surface_hints[]}
```

## Appendix D — Rank debug (internal)

```text
per candidate: cg_sources[], l2, l3, integrity, blend_penalty, acl_ok
```

## Appendix E — ANN build pipeline

```text
sample → train PQ → encode items → publish snapshot → streaming delta topic → dual-read switch
```

## Appendix F — Graph CG ideas

| Idea | Description |
|------|-------------|
| Friends’ posts | Authors ∈ friends |
| FoF | Restricted hop |
| Follow graph | Pages/creators |
| Interactions | People you message/react |

## Appendix G — Integrity actions

| Action | Effect |
|--------|--------|
| Hard remove | Tombstone |
| Demote | Score penalty |
| Label | UI interstitial |
| Rate limit distribution | Inventory throttle |

## Appendix H — Failure injection tests

| Inject | Expect |
|--------|--------|
| ANN 100% err | Lexical+social OK |
| Feature 500ms delay | Defaults; p99 may shed L3 |
| ACL timeout | No non-public docs |

## Appendix I — Capacity worksheet

```text
Rec QPS 100K × heavy N 200 = 20M scores/s
If 1 GPU does 50K scores/s → 400 GPUs (+headroom)
Distill to 100K scores/s → 200 GPUs
Cut N to 100 → another 2× win
```

## Appendix J — Why not Elasticsearch alone?

Works for startup lexical search; fails Meta needs: social CG, multi-stage NN rank, feature store, integrity, ANN at billions, multi-region cells.

## Appendix K — Cursor design

```text
cursor = b64({ts, last_id, last_score, model_ver, seed})
next page: request candidates not in seen; stable tie-break id
```

## Appendix L — Spell correction caution

Over-correction hurts brands/names; only correct when confidence high or zero-results path.

## Appendix M — Multi-objective conflict example

Clickbait high eng / low quality → quality floor + integrity; long-term holdout metrics catch ranking abuse.

## Appendix N — Index segment merge

```text
small near-line segments → merge to medium → cold tiers
search: N segments in parallel with caching
```

## Appendix O — Glossary

| Term | Meaning |
|------|---------|
| CG | Candidate generation |
| L2/L3 | Light/heavy rank stages |
| ANN | Approximate nearest neighbor |
| PQ | Product quantization |
| Tower | Dual-encoder half |
| Blender | Diversity + calibration |
| SERP | Search engine results page |

## Appendix P — 30m checklist

1. Clarify surfaces, entities, freshness, ACL, personalization.  
2. Estimate QPS + score/s → force multi-stage.  
3. Draw orchestrator + CG + features + L2/L3 + integrity.  
4. Deep dive ACL + ANN + feature skew.  
5. Walk 10×/100×/1,000×.  
6. List deal-breakers.

## Appendix Q — Sample merge of CG sources

```text
union by doc_id
prefer max(cg_priority) tags
pass to L2 with source features (from_ann, from_lexical,...)
```

## Appendix R — NFR card

```text
Search p99 < 300ms
Rec p99 < 500ms
Freshness < 60s public
ACL fail-closed non-public
Integrity suppress wins
Heavy N bounded
```

## Appendix S — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| TAO / social graph | Social CG + ACL |
| Memcached / cache | Features + pages |
| Kafka / Scribe | Events |
| Twine / feed ranker family | Ranking cousin |
| Unicorn (historically) | Graph search ideas |

## Appendix T — Offline evaluation

| Task | Metric |
|------|--------|
| Search | NDCG, MRR |
| Recs | AUC, NE, recall |
| Integrity | Precision of demotions |
| Latency | p99 stage breakdown |

## Appendix U — Seen filter

```text
Bloom/Roaring of recent impressions per user
Apply post-CG; refresh asynchronously
```

## Appendix V — Progressive scale table

| Scale | Index | CG | Rank | Cache |
|-------|-------|----|------|-------|
| Base | Dual | 4 sources | L2+L3 | Redis |
| 10× | PQ | +session | distill | Edge SERP |
| 100× | Cells | hierarchical | GPU pools | Personalized short |
| 1,000× | Verticals | routers | edge lite | POP push |

## Appendix W — Worked example

```text
50K search QPS × 20% cache miss = 40K orchestrations/s
Each scores 200 L3 → 8M scores/s
Plus 100K rec QPS × 50% miss × 200 = 10M scores/s
Total ~18M/s → plan GPU/CPU + reduce via cache/distill
```

## Appendix X — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just use Elasticsearch” | Missing social/ANN/rank/features at scale |
| “One transformer” | Latency/cost |
| “Filter ACL in client” | Privacy deal-breaker |
| “Exact KNN” | Impossible at corpus size |

## Appendix Y — Author diversity pseudocode

```text
selected = []
author_count = {}
for c in sorted_by_score:
  if author_count[c.author] >= cap: continue
  if too_similar(c, selected): continue
  selected.append(c); author_count[c.author]+=1
  if len(selected)==page: break
```

## Appendix Z — What success looks like

Low latency, high relevance/engagement, zero ACL leaks, integrity under control, affordable score/s, and a clear story from baseline to 1,000× without rewriting the funnel abstraction.

---

*End of Search & Recommendation Platform system design.*
