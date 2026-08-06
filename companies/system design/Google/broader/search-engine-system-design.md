# System Design: Search Engine

> **Focus areas:** Crawl · Index · Ranking · Serving · Sharding · Query understanding — classic Google interview  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split crawl/index/serve planes, correct posting-list math, honest freshness vs cost, deal-breakers for “one DB LIKE %query% at web scale”  
> **Interview theme:** Google L5+ web search — inverted index, MapReduce-style indexing, DAAT retrieval, ranking tiers, progressive web scale

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

Goal: **bound the product**—a **web search engine** that **crawls** documents, builds an **inverted index**, **ranks** results, and **serves** low-latency queries with **sharding** and **query understanding**. Classic Google-style interview: breadth with sharp tradeoffs—not rebuilding all of Google in 45 minutes.

### 1.0 What this is / is not

| Dimension | **Search engine (this doc)** | Not this |
|-----------|------------------------------|----------|
| Primary job | Relevant docs for queries fast | Social network / full Ads system |
| Success | Precision/recall + p99 latency | Perfect continuous crawl of entire web |
| Data plane | Crawl → index → serve | OLTP user DB |
| Query | Short text → ranked URL list | Arbitrary SQL |
| Correctness | Best-effort freshness; spam robust | Strong consistency of all replicas of web |

**Scope statement:** Design crawl, index, rank, serve for a web-scale search engine with query understanding and progressive scale 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Corpus? | Web pages (HTML) MVP; PDFs later | Fetcher + parser |
| F2 | Freshness? | Hot sites minutes–hours; long tail days | Priority crawl |
| F3 | Query types? | Keywords; phrases; site:; basic operators | Query parser |
| F4 | Results? | Top 10 blue links + snippets | Serving + snippet store |
| F5 | Ranking? | Text relevance + signals (PageRank-like, quality) | Multi-tier rank |
| F6 | Spellfix / rewrite? | Yes basic | Query understanding |
| F7 | Personalization? | Light/out of MVP | Hooks |
| F8 | Languages? | Multi; start English+unicode | Analyzers |
| F9 | Spam/abuse? | Must discuss | Quality classifiers |
| F10 | Real-time docs? | News pipeline secondary | Fast lane index |
| F11 | API? | `GET /search?q=` | Frontends + API |
| F12 | Exact phrase? | Yes | Positional postings |

**MVP functional scope:**

1. **Crawl** URLs politely with frontier priority; respect robots.txt.  
2. **Parse** HTML → text, links, title, canonical.  
3. **Index** inverted postings (term → doc list) + forward store for snippets.  
4. **Query understanding:** tokenize, normalize, spell, basic rewrite.  
5. **Retrieve** candidates via DAAT/TAAT over postings.  
6. **Rank** tier-1 cheap → tier-2 heavier features → top-K.  
7. **Serve** geographically with replicas; cache hot queries.  
8. Link graph signal (PageRank-like) batch-updated.

**Out of MVP:**

- Full ads auction  
- Complete knowledge graph answers  
- Perfect personalization  
- Universal all-file-type understanding  
- Sub-second global index of every change  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Query latency | Instant feel | p99 < 200–300ms |
| N2 | Availability | Critical | 99.99% serve |
| N3 | Index size | Web-scale path | Billions docs design |
| N4 | Freshness | Tiered | News fast; tail slower |
| N5 | Politeness | Crawl ethics | Rate limits / robots |
| N6 | Spam resilience | High | Quality scoring |
| N7 | Cost | Major constraint | Tiered storage/rank |
| N8 | Multiregion serve | Yes | Replicate index |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Query “wireless headphones” → rewrite → retrieve → rank → 10 results + snippets.  
2. Crawl discovers new URLs via links → enqueue → fetch → index.  
3. Hot news URL prioritized → fast lane appears in minutes.  
4. Spellfix “gogle” → “google”.  
5. Phrase query `"machine learning"` uses positions.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Crawl trap / infinite calendar | Cap depth, URL canonical, bloom seen |
| Soft-404 / doorway spam | Quality classifier demote |
| Query flood viral | Result cache; shed load |
| Shard down | Query degrade; replica failover |
| Posting list huge (`the`) | Skip lists / impact-ordered / ignore stopwords carefully |
| Duplicate content | Fingerprint cluster; canonical |
| JavaScript-heavy pages | Render queue subset |
| robots.txt deny | Skip |
| Index lag after site update | Freshness tier explanation |
| Ambiguous query | Diversify results / suggest |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Docs indexed | 100M | 1B | 10B | 100B |
| Unique terms | 50M | 200M | 500M | 1B+ |
| Avg terms/doc | 500 | 500 | 500–800 | 800 |
| Postings volume | 50B | 500B | 5T | 50T+ |
| QPS global | 10K | 100K | 1M | 10M |
| Crawl fetches/s | 5K | 50K | 500K | 5M |
| Index shards | 64 | 512 | 4K | 40K+ |
| Serving leaves | 100 | 1K | 10K | 100K |
| Fresh % docs < 1 day | 1% | 1–2% | tiered | multi-lane |

**What each jump forces:**

- **10×:** Real inverted index; MapReduce/Flink build; shard by term or doc.  
- **100×:** Multi-tier rank; separate serve stacks; news lane; extensive caching.  
- **1,000×:** Geo serve cells; truncated postings; learned retrieval; massive link systems.

### 1.5 Etc. (Constraints & Assumptions)

- Web is adversarial (spam, cloaking).  
- Storage/compute cost dominates design.  
- Exact Google internals unknown — use **public classic ideas** (PageRank, MapReduce, tiers).  
- Interview success = clear planes + numbers + tradeoffs.

**Scope statement to repeat back:**

> Design a web search engine: polite prioritized crawl, inverted index with positional postings, query understanding, multi-tier ranking including link quality, and sharded low-latency serving—scaling corpus and QPS through 10× / 100× / 1,000× without pretending a single RDBMS can answer web search.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split planes (critical)

| Plane | What | Baseline | 10× |
|-------|------|----------|-----|
| **Crawl** | Fetch/s | 5K | 50K |
| **Index build** | Docs/day | tens of M | hundreds of M |
| **Query serve** | QPS | 10K | 100K |
| **Link analysis** | Graph iters | batch | continuous-ish |
| **Cache** | Hot queries | high hit | higher |

**Anti-pattern:** one QPS for crawl and search traffic.

### 2.2 Storage math

```text
100M docs × 10KB compressed stored text = 1 PB? careful:
  Raw HTML avg 50KB × 100M = 5 PB raw — store compressed + select fields
  Indexed text 5–10KB × 100M = 0.5–1 PB forward
Postings: 100M docs × 500 terms = 50B postings
  If 6B each (docid delta + payload) ≈ 300 GB — optimistic; with positions >> TB
At 10B docs: postings tens–hundreds of TB — shard + compress (FOR/PFOR/varint)
```

### 2.3 Query latency budget

```text
Query understand: 5–10ms
Fanout retrieve: 50–100ms
Tier-1 rank: 20–40ms
Tier-2 rank top-N: 20–40ms
Snippet assemble: 10–20ms
Network: 20–40ms
Total: < 200–300ms p99 with parallelism
```

### 2.4 Crawl politeness

```text
5K fetch/s across web — per host much lower (e.g. 1 QPS/host default)
Frontier must schedule by host queues
```

### 2.5 Fanout cost

```text
Query hits T terms → intersect/union postings across shards
Doc-sharded index: fanout all shards every query — merge costly at 40K shards
Term-sharded: only shards owning terms — good for rare; bad for many terms
Hybrid common: doc-partitioned replicas with local indexes (Google classic leaf)
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /search?q=&hl=&start=` | Ranked results + cursors |
| `GET /suggest?q=` | Autocomplete |
| `GET /health` | Serving |
| Internal crawl ops | Seed, priority boost, ban host |

**Result item:** `url, title, snippet, score_debug?`

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| URL/Doc | `doc_id` | url, canonical, fetch_ts, status |
| Forward index | `doc_id` | title, text body compressed, anchors |
| Inverted index | `term` | postings: `(doc_id, tf, positions[], fields)` |
| Link graph | `doc_id` | outlinks / inlink counts |
| Page quality | `doc_id` | pagerank-like, spam score |
| Crawl frontier | priority queues per host | URLs due |
| Query cache | `query_norm` | top docs |

### 3.3 Crawler — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **BFS only** | Simple | Ignores importance | Toy |
| **Priority frontier** | Fresh/important first | Complexity | **MVP** |
| **Sitemap-only** | Polite | Incomplete | Assist |
| **Buy feeds** | Easy | Coverage gaps | Vertical |

**Components:** DNS cache, robots cache, fetcher workers, renderer subset, dedupe, content store, link extractor → frontier.

**Politeness:** per-host token bucket; crawl-delay; exponential backoff.

### 3.4 Indexing — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Online update every doc** | Fresh | Hard at web scale | News lane |
| **Batch MapReduce build** | Throughput | Lag | **Main corpus MVP** |
| **Incremental segments** | Balance | Merge tax | **Production pick** |
| **SQL LIKE** | — | Impossible scale | Never |

**Pipeline:**

```text
Content store → analyze (tokenize, stem optional) → map to postings
  → sort/shuffle by term → reduce to posting lists
  → compress → publish immutable segment
  → serving leaves load segments
```

### 3.5 Retrieval & ranking

```text
Query → understand → terms
Retrieve: DAAT intersection with skip pointers / WAND / Block-Max WAND
Tier-1: BM25 + static quality
Top N (e.g. 200) → Tier-2: ML ranker features (links, freshness, clicks aggregate)
Diversity / site collapse
Return top 10
```

**Deal-breaker:** TF-IDF only with no spam/quality story at web scale.

### 3.6 Query understanding

| Stage | Example |
|-------|---------|
| Char normalize | Unicode NFKC |
| Tokenize | language-specific |
| Spell | noisy channel / edit + log priors |
| Synonym / rewrite | “nyc” → “new york city” |
| Segment Chinese | etc. |
| Intent | navigational vs informational (light) |

### 3.7 Serving topology

```text
User → Edge/DNS → Web server → Root/blender
  → fanout to index leaves (doc-sharded)
  → merge + rank
  → snippet service
  → cache
```

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Index | Inverted postings | Web IR | Relational LIKE |
| Build | Segmented batch+incremental | Cost/freshness | Fully online web |
| Shard | Doc-partitioned leaves | Predictable fanout | One giant server |
| Rank | Multi-tier | CPU $ | Deep ML on all docs |
| Crawl | Priority + polite | Coverage ethics | Hammer hosts |
| Cache | Query result cache | QPS | Uncached all queries |

---

## 4. Architecture Diagram

```text
                     +-------------------+
   Seeds / sitemaps->|  Crawl Scheduler  |
                     |  (frontier/hosts) |
                     +---------+---------+
                               |
                               v
                     +---------+---------+
                     | Fetchers/Render   |----> Content Store (GCS/S3/GFS-like)
                     +---------+---------+
                               |
                               v
                     +---------+---------+       +----------------+
                     | Parsers/Link Ext. |------>| Link Graph     |
                     +---------+---------+       | PageRank jobs  |
                               |                 +--------+-------+
                               v                          |
                     +---------+---------+                |
                     | Index Builder     |<---------------+ quality scores
                     | (MR/Flink segs)   |
                     +---------+---------+
                               |
                               v
                     +---------+---------+
                     | Index Serving     |
                     | Leaves (sharded)  |
                     +---------+---------+
                               ^
                               | fanout
   Users --> CDN/Edge --> Web --> Root/Blender --> Snippets
                               |
                               +--> Query Understanding
                               +--> Result Cache
                               +--> Spell / Suggest
```

---

## 5. Design Deep Dive

### 5.1 Crawler details

```text
Frontier: priority = f(pagerank, freshness_need, sitemap, change_rate)
Per-host queues ensure politeness
URL canonicalization: scheme/host/normalize query params
Seen: Bloom + disk key-value of fingerprints
Dedupe content: simhash / shingle
Backoff on 429/5xx
```

**Crawl traps:** session IDs, calendars — detect URL patterns; budgets per site.

### 5.2 Parsing & analysis

```text
HTML → DOM → visible text, title, meta, anchors
Boilerplate removal (nav/footer)
Language detect
Tokenize → term_ids
Store field postings: title^boost, body, anchors
```

### 5.3 Inverted index format

```text
term → [
  {doc_id_delta, tf, positions_deltas, field_mask}, ...
]
Block compression (PFOR, varint)
Skip pointers every k docs for DAAT
Impact-ordered optional for early termination
```

**Positional postings** enable phrase queries; cost more storage — selective.

### 5.4 Index sharding

| Strategy | Query path | Build | Notes |
|----------|------------|-------|-------|
| **Doc-sharded** | Fanout all leaves; merge | Natural by doc | **Classic serve** |
| **Term-sharded** | Fanout terms | Harder phrases | Mixed use |
| **Hybrid** | — | — | Global terms + doc leaves |

**Chosen MVP serve:** document-partitioned replicas; each leaf has complete local vocabulary for its docs.

### 5.5 Retrieval algorithms

| Algo | Idea |
|------|------|
| **TAAT** | Term-at-a-time accumulate scores |
| **DAAT** | Doc-at-a-time intersect — good AND |
| **WAND / Block-Max** | Skip docs that can’t beat heap |

**Phrase:** check position adjacency using positional lists.

### 5.6 Ranking signals

| Signal | Type |
|--------|------|
| BM25 / fielded BM25 | Text |
| PageRank-like / TrustRank | Static |
| Spam / malware score | Quality |
| Freshness / chronos | Temporal |
| Click/CTR aggregates | Behavioral (privacy-aware) |
| HTTPS / page experience | UX |
| Exact match domain | Navigational |

**Multi-tier:** cheap on 10K–100K cands → expensive on 200 → top 10.

### 5.7 Link analysis

```text
Batch PageRank on link graph periodically
Or approximate continuous (incremental)
Spam farms: distrust seed sets; bipartite analysis
Anchors: text of inlinks strong signals
```

### 5.8 Query understanding deep dive

```text
q_raw → normalize → tokens
spell: if P(correction|q) high and rare raw → rewrite
synonyms: controlled expansion (careful recall flood)
remove stopwords optionally for retrieval but keep for phrases
locale: hl=en
```

**Autocomplete:** separate prefix index / trie / n-gram; not full search path.

### 5.9 Serving & caching

```text
Result cache key: normalize(q) + geo + lang + safe
TTL short for newsy; longer for stable
Posting lists memory-mapped on leaves
Root blender timeouts + partial results degrade
```

### 5.10 Freshness lanes

| Lane | Corpus | Index lag |
|------|--------|-----------|
| Realtime/news | small | seconds–minutes |
| Hot | medium | hours |
| Main | huge | daily/continuous segments |
| Archive | cold | rare |

**Deal-breaker:** one monolithic daily index for “breaking news” product claims.

### 5.11 Reliability

| Failure | Mitigation |
|---------|------------|
| Leaf dead | Replica; query other copies |
| Crawl outage | Serve stale index |
| Bad segment push | Version pin; canary leaves |
| Spam attack | Classifier; manual demotions |
| Cache poison | Auth results; TTL; purge |

**Reliability principles:**

1. Immutable index segments + atomic publish.  
2. N+2 leaf replicas.  
3. Degrade partial shard results with metric.  
4. Separate crawl faults from serve.  
5. Canary ranking changes.

### 5.12 Scalability

| Scale | Tactic |
|-------|--------|
| 10× | MR index; 100s shards; BM25+PR |
| 100× | Tier-2 ML; news lane; geo serve; huge caches |
| 1,000× | Truncation, learned sparse/dense retrieval, cells |

### 5.13 Maintainability

| Practice | Why |
|----------|-----|
| Golden query eval sets | NDCG regressions |
| Ranker feature platform | Safe experiments |
| Segment versioning | Rollback |
| Crawl policy as data | Ops |
| Spam review tools | War room |

### 5.14 Snippets

```text
Fetch forward store windows around match positions
Highlight terms
Cache snippet per (doc, q)
```

### 5.15 Progressive scale deep dive

**Baseline (100M docs):** batch index weekly+daily; doc shards; BM25+PageRank; single region serve.

**10× (1B):** continuous segment merge; spell; WAND; multi-region serve replicas.

**100× (10B):** dedicated news; ML tier-2; aggressive spam; autocomplete fleet.

**1,000× (100B):** multi-cluster cells; embedding retrieval assist; extreme compression; country indices.

---

## 6. Wrap-Up

### 6.1 Design summary

A **classic web search stack**: **polite prioritized crawl**, **segmented inverted indexes** with positional postings, **query understanding**, **multi-tier ranking** (BM25 + quality/link + ML), and **doc-sharded low-latency serving** with result caches and freshness lanes.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Lost |
|----------|--------|------|
| Freshness vs cost | Tiered lanes | Uniform realtime web |
| Recall vs latency | WAND/top-K | Exhaustive score all docs |
| Rank CPU | Multi-tier | Deep model on billions |
| Phrase support | Positions | Storage |

### 6.3 Deal-breakers

1. RDBMS `LIKE '%query%'` as web search.  
2. Single daily index for news claims.  
3. Ranking by TF only ignoring spam.  
4. Impolite crawl (legal/reputation).  
5. Unbounded fanout without timeouts.  
6. Claiming personalization+ads+KG depth in MVP timebox without prioritization.

### 6.4 Progressive scale one-liner

> **Batch inverted index → continuous segments & geo serve → news lane + ML tier → cells, truncation, learned retrieval.**

### 6.5 Reliability / Scalability / Maintainability

```text
Reliability: segment atomicity, leaf replicas, degrade partial, canary rank
Scalability:  doc shards, WAND, caches, freshness lanes, compression
Maintainability: golden evals, feature platform, policy-as-data
```

---

## 7. Deeper / Related Interview Questions

### 7.1 Crawl

**Q1: How avoid overwhelming a site?**  
A: Per-host queues and rate limits; robots.txt.

**Q2: Crawl priority?**  
A: Importance × staleness × change rate.

**Q3: Discover new URLs?**  
A: Outlinks, sitemaps, feeds, submissions.

**Q4: Handle JS sites?**  
A: Selective headless render budget.

**Q5: Dedupe?**  
A: URL canon + content fingerprint clusters.

### 7.2 Index

**Q6: Why inverted index?**  
A: Terms sparse; postings enable fast candidate find.

**Q7: How build at scale?**  
A: MapReduce/sort postings; immutable segments; merges.

**Q8: Incremental vs full?**  
A: Incremental segments + periodic optimize merge.

**Q9: Stopwords?**  
A: Sometimes omit from index; careful with “the who”.

**Q10: Store positions?**  
A: Phrase/proximity; storage tradeoff.

### 7.3 Ranking

**Q11: BM25 vs TF-IDF?**  
A: BM25 length normalization typically better baseline.

**Q12: Why PageRank?**  
A: Query-independent quality from link graph.

**Q13: Why multi-tier?**  
A: $$$ CPU; deep features only on survivors.

**Q14: Click signals bias?**  
A: Position bias models; privacy aggregation.

**Q15: Freshness vs authority?**  
A: Intent-dependent; news intents weight time.

### 7.4 Serving

**Q16: Doc vs term sharding?**  
A: Doc-sharding common for serve fanout predictability.

**Q17: How merge leaf results?**  
A: Root heap merge by score; then global rerank optional.

**Q18: Cache key?**  
A: Normalized query + locale + safe search.

**Q19: Tail latency?**  
A: Hedged requests; timeouts; partial.

### 7.5 Query understanding

**Q20: Spell correction source?**  
A: Query logs + dictionary + edit distance.

**Q21: Synonym danger?**  
A: Over-expansion kills precision — controlled lists / learned.

**Q22: Navigational queries?**  
A: Strong domain/prior boosts.

### 7.6 Estimation drills

**Q23: Postings for 10B docs × 500 terms × 4B?**  
A: 10B×500×4 = 2e13 bytes ≈ 20 PB raw — compress/shard/truncate story mandatory.

**Q24: Leaves for 1M QPS if each leaf 1K QPS?**  
A: Order 1000+ leaves × replicas × regions.

### 7.7 Alternatives & deal-breakers

**Q25: Elasticsearch as whole web?**  
A: Good vertical; web needs crawl+spam+link+cost engineering.

**Q26: Dense embeddings only?**  
A: Complementary; lexical still critical for exact/rare.

**Q27: Online learning rank every query from scratch?**  
A: Too slow; use offline trained models.

### 7.8 Interview craft

**Q28: How to open?**  
A: Planes crawl/index/rank/serve; ask corpus size, QPS, freshness; draw.

**Q29: L5+ signals?**  
A: Postings math, WAND, tiered rank, politeness, segment publish, deal-breakers.

**Q30: Common mistake?**  
A: Only UML of microservices; no index structure or numbers.

---

### Appendix A — BM25 sketch

```text
score(q,d) = Σ_t IDF(t) * (tf*(k1+1))/(tf + k1*(1-b+b*|d|/avgdl))
```

### Appendix B — DAAT intersect

```text
def intersect(lists):
  # advance pointers on sorted doc_ids using skips
  ...
```

### Appendix C — Index build MR

```text
map(doc):
  for term in analyze(doc):
    emit(term, doc_id, pos)
reduce(term, postings):
  sort by doc_id; delta-code; write list
```

### Appendix D — Frontier

```text
host_queues[host].push(url, priority)
scheduler: pick host with available token → fetch
```

### Appendix E — Segment publish

```text
build segment S_n offline
push to leaves staging
atomic switch alias from S_{n-1} to include S_n
keep old for rollback
```

### Appendix F — Progressive scale table

| Scale | Docs | Index | Serve | Rank |
|-------|------|-------|-------|------|
| Baseline | 100M | Batch daily | 1 region | BM25+PR |
| 10× | 1B | Segments | Multi-region | +WAND |
| 100× | 10B | Multi-lane | Cells | +ML tier2 |
| 1,000× | 100B | Trunc/learned | Global fabric | Hybrid dense |

### Appendix G — NFR card

```text
p99 search < 300ms
Polite crawl
Atomic segment publish
Spam-aware ranking
Tiered freshness
```

### Appendix H — Query rewrite example

```text
"nyc pizza" → tokens [nyc, pizza] + expand nyc→"new york city" (weighted)
```

### Appendix I — Spam features

| Feature | Hint |
|---------|------|
| Link farm density | Spam |
| Cloaking detect | Spam |
| Keyword stuffing | Spam |
| Malware flags | Drop |
| User complaints | Demote |

### Appendix J — Snippet selection

```text
choose window maximizing query term coverage + early position
highlight
```

### Appendix K — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Use Postgres FTS” | Scale/spam/crawl |
| “Only embeddings” | Exact rare terms, cost |
| “Realtime whole web” | Cost lanes |
| “PageRank enough” | Need text match |

### Appendix L — Related systems (conceptual)

| System | Relation |
|--------|----------|
| MapReduce / Flume | Index build |
| Bigtable/GFS | Content / postings storage analogs |
| Lucene | Segment ideas |
| Borg/K8s | Serving leaves |

### Appendix M — Glossary

| Term | Meaning |
|------|---------|
| Posting | Doc occurrence of a term |
| DAAT | Doc-at-a-time retrieval |
| WAND | Weak AND early exit |
| Segment | Immutable index piece |
| Frontier | URLs waiting to crawl |
| Blender | Root merge/rank service |

### Appendix N — Worked query

```text
q = "wireless headphones"
terms rare→common: wireless, headphones
DAAT intersect → 2M cands too many → WAND keep heap 10K
Tier1 → 200; ML tier2 → 10
snippets; return
p50 ~80ms cached; uncached ~180ms
```

### Appendix O — Consistency

| Question | Answer |
|----------|--------|
| Index strongly consistent with web? | No — lagged view |
| Replica same scores? | Same segment version yes |
| Crawl exactly-once? | At-least-once fetch; idempotent index |

### Appendix P — 30m checklist

1. Clarify corpus, QPS, freshness, languages.  
2. Four planes diagram.  
3. Postings + shard math.  
4. Crawl politeness.  
5. Multi-tier rank + spam.  
6. Serve fanout + cache.  
7. 10×/100×/1,000×.  
8. Deal-breakers.

### Appendix Q — Autocomplete

```text
Prefix index from query logs
Not same as full retrieval
Heavy cache at edge
```

### Appendix R — SafeSearch

```text
Adult score on docs; filter/demote by preference
```

### Appendix S — Internationalization

```text
Per-language analyzers
Country indices or strong geo rank signals
hl + gl parameters
```

### Appendix T — Truncation

```text
At extreme scale keep top postings by impact / quality
Risk recall — compensate with additional retrieval paths
```

### Appendix U — Evaluation

```text
NDCG@10 on human-rated sets
Online A/B on engagement (careful)
Spam escape evals
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Real postings MR, WAND, geo replicas |
| 100× | News lane, ML tier, spam platform |
| 1,000× | Cells, truncation, hybrid retrieval |

### Appendix W — Robots & legal

```text
Fetch robots.txt; cache; honor Disallow
Crawl-delay; user-agent identify
Takedown pipeline
```

### Appendix X — Feature extraction for tier-2

| Feature | Source |
|---------|--------|
| bm25_title | text |
| pr | link job |
| spam | classifier |
| age_hours | crawl ts |
| url_len | url |
| click_prior | logs |

### Appendix Y — Opening script

> “I'll split search into crawl, index, rank, and serve. We'll use a polite priority crawler, segmented inverted indexes with doc-sharded leaves, query understanding, and multi-tier ranking with link quality—scaling with freshness lanes and geo serving. Out of scope: full ads and KG.”

### Appendix Z — Whiteboard order

```text
1) User → blender → leaves
2) Postings box
3) Crawl → content → index build
4) Rank tiers
5) Numbers on docs/QPS
6) Scale arrows + deal-breakers
```

---

*End of Search Engine system design.*
