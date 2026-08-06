# System Design: Search Engine

> **Focus areas:** Crawling · Indexing · Inverted index · Serving · Ranking · Freshness · Spelling/autocomplete · Multi-tier retrieval · Spam/quality · Sharding/replication · Bing-class narrative  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split crawl/index/serve QPS, explicit deal-breakers, progressive tiering, latency SLOs  
> **Interview theme:** Microsoft — **Bing / Microsoft Search / site search / enterprise search** (clarify which; this doc is web-scale with enterprise hooks)

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

Goal: design a **search engine** that discovers documents, builds a scalable inverted index, serves low-latency queries with relevance ranking, and stays fresh enough for news/sites while controlling spam, cost, and failure domains. In a Microsoft interview, clarify **web search vs enterprise/Microsoft Search vs site search**—architecture rhymes, constraints differ.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Retrieve + rank documents for queries | Full ChatGPT replacement |
| Planes | Crawl/ingest → index → serve → learn | Only Elasticsearch install |
| Success | Relevance + latency + freshness + trust | Index size vanity |
| Microsoft lens | Bing-scale thinking, Azure hosting, responsible ranking | Ignore spam |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Corpus? | Web pages (and/or enterprise docs) | Crawl vs connector ingest |
| F2 | Query types? | Keywords, phrases, site:, language | Query parser |
| F3 | Ranking? | Textual + link/quality + personalization light | Multi-stage rank |
| F4 | Freshness? | News hours; sites days; archives longer | Crawl prioritization |
| F5 | Autocomplete? | Yes | Suggest service prefix index |
| F6 | Spell correction? | Yes | Dict + log mining |
| F7 | Snippets? | Yes with highlighting | Doc store + compact |
| F8 | Safe search? | Yes | Policy filters |
| F9 | Multilingual? | Yes | Language ID + analyzers |
| F10 | Realtime docs? | Nearline for priority URLs | Streaming index updates |
| F11 | Analytics? | Query logs for relevance | Privacy-preserving |
| F12 | APIs? | Query API + ops index API | Clean contracts |

**MVP scope (web-scale narrative):**

1. Crawler with politeness, robots.txt, sitemap, URL frontier.  
2. Document processing: fetch, parse, canonicalize, lang detect, extract text/links.  
3. Build inverted index + forward/doc store.  
4. Query serving: parse → retrieve → rank → snippet.  
5. Autocomplete + spellcheck basic.  
6. Freshness tiers; recrawl scheduler.  
7. Spam/quality scoring hooks.  
8. Metrics: latency, recall proxies, index lag.

**Out of MVP:** full knowledge graph, perfect neural-only retrieval at all tiers without inverted index, real-time index of entire web, ads system (mention only), multimodal video search deep dive unless asked.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Query latency | p50 < 100ms, p99 < 300–500ms (web) |
| N2 | Availability | 99.99% query path |
| N3 | Index durability | No silent corpus loss |
| N4 | Freshness | Hot URLs minutes–hours; median days |
| N5 | Scalability | Horizontal shard by term/doc |
| N6 | Politeness | Respect robots; rate limits per host |
| N7 | Cost | $/query and $/indexed-doc budgets |
| N8 | Safety | Malware/phishing demotion/removal |

### 1.3 Cases

**Happy:** User query → parse → retrieve top candidates from index shards → scatter-gather → rank → snippets → results.

**Edges:**

| Case | Behavior |
|------|----------|
| Typos | Spell correct / reformulate |
| Zero results | Relaxation, synonyms, suggest |
| Ambiguous query | Diversify intents |
| Hot queries (viral) | Result cache / posting cache |
| Deep pagination | Cursor / limited depth |
| Fresh breaking news | News index tier / fast lane |
| Spam farm | Quality demotion; don’t rank by tricks alone |
| Soft 404 | Detect; avoid indexing junk |
| Duplicate/near-dupe | Canonical clustering |
| Robots disallow | Don’t fetch/index |
| JavaScript-heavy pages | Selective rendering budget |
| Huge postings lists | Skip lists / block max WAND |
| Shard failure | Replica serve; degraded recall policy |
| Query flood | Cache + admit control |
| Adult content | SafeSearch filter |
| Enterprise ACL | Security trimming early/late carefully |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Documents | 100M | 1B | 10B | 100B+ |
| Unique terms | 50M | 200M | 500M | 1B+ |
| Queries / day | 50M | 500M | 5B | 50B |
| Peak QPS | 2K | 20K | 200K | 2M |
| Crawl fetches / day | 50M | 500M | 5B | 50B |
| Index size (compressed) | 20 TB | 200 TB | 2 PB | 20 PB+ |
| Shards | 50 | 500 | 5K | 50K |
| Freshness hot set | 1M URLs | 10M | 100M | 1B |
| Languages | 20 | 40 | 80 | 100+ |

**Jumps:**

- **10×:** Sharded inverted index; replica sets; crawl frontier distributed.  
- **100×:** Tiered indexes (hot/warm/cold); multi-stage ranking; dedicated suggest cluster.  
- **1,000×:** Global serving cells; neural rerank fleet; continuous indexing fabric; web-scale spam war.

### 1.5 Scope statement

> Design a search engine covering crawl/ingest, document processing, inverted-index build/serve, multi-stage ranking, autocomplete/spell, freshness tiers, and spam/quality controls—from ~100M docs through 10× / 100× / 1,000× with explicit latency and deal-breakers.

**Clarify early:** If interviewer means **Microsoft Search in M365**, swap crawler for Graph connectors and emphasize ACL security trimming—still keep inverted index + rank stages.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Index math

```text
100M docs × 1 KB text ≈ 100 TB raw text? 
Actually avg indexed text often ~5–20 KB extracted → 
100M × 10 KB = 1 TB raw text

Inverted index compressed often ~0.3–1× raw text scale depending on postings
Say ~20 TB index structures at baseline including doc store / vectors later
```

### 2.2 Query path

```text
2K QPS × p99 300ms → concurrency ≈ 2K × 0.3 = 600 in-flight
Each query touches many shards; fan-out cost dominates
Result cache HIT for head queries saves enormous fan-out
```

### 2.3 Crawl

```text
50M fetches/day ≈ 580/s average; peak higher
Avg page 100 KB download → 50M × 100 KB = 5 PB/day raw? 
50e6 × 1e5 B = 5e12 B = **5 TB/day** (not PB)
Still large — content-seen hashing to skip unchanged
```

### 2.4 Postings

```text
Term "the" enormous — stopwords handled carefully
Rare terms tiny lists
Serving must use dynamic pruning (WAND/MaxScore), not full scan
```

### 2.5 Bottlenecks

(1) Tail latency from slow shards (2) crawl politeness vs freshness (3) index merge IO (4) spam (5) neural rerank GPU cost (6) not “JSON API.”

### 2.6 Cost

Indexing and serving storage dominate; neural rerank every query is expensive—use multi-stage: cheap retrieve → heavy rerank top-k.

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Role | Notes |
|-------|------|-------|
| Discovery/Crawl | URL frontier, fetch | Politeness |
| Processing | Parse, canonicalize, links | Dedup |
| Indexing | Build inverted + doc store | Nearline + batch |
| Serving | Query → results | Latency SLO |
| Ranking/Learning | Signals, models | Offline + online |
| Suggest | Autocomplete | Prefix structures |
| Safety/Spam | Quality | Continuous war |
| Feedback | Clicks/queries | Privacy |

**Deal-breaker:** synchronous crawl on user query path.

### 3.2 Components

1. **URL Frontier / Scheduler**  
2. **Fetcher workers** (HTTP + selective headless render)  
3. **Content store** (raw WARC-like)  
4. **Document processor**  
5. **Link graph store** (for quality signals)  
6. **Indexer** (segment builders)  
7. **Index shards + replicas**  
8. **Doc store** (snippets, titles, metadata)  
9. **Query frontend / broker**  
10. **Retrieval (DAAT/WAND)**  
11. **Ranker stages** (L1 lexical, L2 features, L3 neural)  
12. **Result cache**  
13. **Spell + Annotator**  
14. **Autocomplete service**  
15. **SafeSearch / policy**  
16. **Ops: index manager, canaries**  

### 3.3 Inverted index essentials

```text
Term -> postings list of (doc_id, tf, positions?)
Doc store: doc_id -> {title, url, language, length, snippet source}
Forward index optional for some features
Segments: immutable files + merges (Lucene-like)
```

### 3.4 Query pipeline

```text
Parse/analyze → rewrite (spell, synonym) → retrieve candidates
→ L1 score → top N → L2 feature rank → top M → L3 neural rerank
→ diversity / safe filters → snippet → package response
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Term vs doc sharding | Hybrid common | Term for postings; doc for some stores |
| Positions | Store for phrases/snippets | Space cost |
| Batch vs streaming index | Both | Freshness + efficiency |
| Exact vs approximate ANN | ANN for vectors stage | Recall tradeoff |
| Render JS | Budgeted | Cost |
| Global index | Per-geo serving copies | Latency |

### 3.6 Ranking signals (interview set)

- BM25 / lexical  
- Doc quality / static rank (PageRank-like)  
- Freshness  
- Language / region match  
- Click/CTR models (careful bias)  
- Spam score  
- HTTPS / malware flags  
- Personalization light (region, language)  
- Neural semantic similarity (stage-limited)

### 3.7 APIs

```text
GET /v1/search?q=&market=&count=&offset=&safe=
GET /v1/suggest?q=
POST /v1/index/docs  (enterprise / site-search mode)
DELETE /v1/index/docs/{id}
```

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Web] <- Fetcher <- URL Frontier <- Seed/Sitemaps/Link discovery
          | raw
     Content Store -> Processor -> (Docs, Links, Spam features)
                          |
                     Index Builder -> Index Segments
                          |
                     Shard Manager -> [Shard replicas worldwide]
                                         ^
[User] -> Edge -> Query FE -> Cache -> Broker scatter-gather
                      |                 |
                   Spell/Suggest      Ranker fleet
                      |
                   Results + snippets from Doc Store
```

### 4.2 Query sequence

```text
FE: analyze q
Rewrite: spell=corrected
Broker: fanout to term shards / partitioned retrieval
Merge top candidates
L2/L3 rank
Fetch snippets
Return
```

### 4.3 Indexing sequence

```text
New/changed doc -> processor -> analyze tokens
Add to nearline segment / memory buffer
Flush segment; make searchable
Background merge segments
Update static quality asynchronously
```

### 4.4 Freshness fast lane

```text
News/hot hosts -> high priority frontier
-> low-latency processor -> hot index tier
Serving queries may union hot + main tiers
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Query path does not depend on crawler liveness.  
2. Index replicas exist; single shard loss ≠ total outage.  
3. Published segment is immutable; swaps atomic.  
4. robots.txt and legal takedowns enforced.  
5. SafeSearch not bypassable via trivial operators for restricted modes.  
6. ACL trimming (enterprise) cannot leak via snippets/autocomplete.  
7. Canary ranking models with automatic rollback.  
8. Deduped canonical URLs prevent index bloat.  
9. Query logs privacy controls.  
10. Malware URLs demoted/removed quickly.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Few shards; Lucene-like; single region |
| 10× | Many shards/replicas; distributed frontier; result cache |
| 100× | Hot/warm/cold indexes; multi-stage rank; geo serving |
| 1000× | Web-scale continuous indexing; neural fleets; spam arms race |

### 5.3 Maintainability

- Analyzer pipelines versioned.  
- Rank feature platform.  
- Offline evaluation (nDCG) before ship.  
- Query understanding dictionaries as data.  
- Chaos: kill shard, delay index publish, spam injection tests.  

### 5.4 Progressive scale deep dive

**1× — Site search / small web vertical**  
Single cluster, nightly full index + incremental updates, BM25 + simple static rank, Postgres doc metadata, Redis result cache.

**10× — Large vertical / early web**  
Shard by hash(doc_id) with term-partitioned postings strategy clarified; crawl politeness distributed by host hash; spell correction from query logs; autocomplete trie/FST; monitoring index lag.

**100× — Multi-tier Bing-like**  
- **Hot index:** news + trending.  
- **Main web index:** sharded massively.  
- **Cold/archive:** rarer terms/docs.  
Multi-stage ranking with GBDT L2 and neural L3 on top-50. Geo-replicated serving cells. Dedicated suggest service. Link graph batch jobs for quality. Render farm for important JS sites only.

**1000× — Planet scale**  
Continuous crawling of 100B+ URLs with sophisticated priority; per-language analyzers; massive spam/adversarial ML; ANN vector indexes for semantic recall fused with lexical; edge result cache; per-market relevance; sovereign serving; cost-aware rerank admission control; experiment platform tightly coupled.

### 5.5 Retrieval algorithms (say in interview)

- **DAAT** document-at-a-time with WAND / MaxScore pruning  
- **TAAT** less common at scale for large OR  
- **Conjunctive** vs disjunctive modes  
- **Phrase** via positions or next-doc skipping  
- **Two-tower / ANN** for semantic candidates fused via reciprocal rank fusion / learned fusion  

### 5.6 Sharding strategies

| Strategy | Pros | Cons |
|----------|------|------|
| Doc-partitioned | Natural crawl map | Query fanout all shards |
| Term-partitioned | Less fanout for rare | Hard joins; hot terms |
| Hybrid | Common in practice | Complexity |

Web search often **doc-sharded** with broker fan-out + aggressive pruning + caching.

### 5.7 Freshness vs cost

Priority score = f(churn, traffic, page importance, staleness). Recrawl important hosts often; deep web rarely. Conditional GET / etags. **Deal-breaker:** equal-priority BFS crawl forever.

### 5.8 Spam & quality

- Link spam detection  
- Content spam / doorway pages  
- Cloaking detection  
- Malware/phishing feeds  
- Ranking wars → continuous evaluation  
Never trust a single signal.

### 5.9 Autocomplete & spell

- Prefix FST / n-gram index from popular queries  
- Personalization light (region)  
- Spell: edit distance + log likelihood  
- Do not suggest banned/illegal queries (policy)

### 5.10 Enterprise / Microsoft Search variant

Replace crawler with **connectors** (SharePoint, OneDrive, email). Critical: **security trimming**—filter docs by ACL. Options: early (query rewriting with ACL) vs late (retrieve then filter)—late can leak via timing/counts if careless; prefer safe patterns. Tenants isolated.

### 5.11 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Crawl in request path | Timeouts / abuse |
| No replicas | Shard death = outage |
| Rank only by TF-IDF at web scale | Spam wins |
| Neural rerank entire corpus | Impossible cost |
| Ignore robots/takedowns | Legal SEV |
| Global mutable index without versions | Corrupt swaps |
| Autocomplete without ACL (enterprise) | Data leak |
| Unbounded pagination into deep corpus | Cost / bad UX |

---

## 6. Wrap-Up

### 6.1 Designed

Search engine with crawl/ingest, processing, inverted index tiers, scatter-gather serving, multi-stage ranking, suggest/spell, freshness fast lanes, and spam/safety controls—scaled by sharding and geo serving cells.

### 6.2 Decisions to defend

1. Async crawl ≠ query path  
2. Immutable segments + atomic publish  
3. Multi-stage retrieval/rank  
4. Hot/main/cold tiers  
5. Result cache for head queries  
6. Doc quality + spam signals  
7. WAND-style pruning  
8. Offline nDCG gating for rank changes  

### 6.3 Risks

- Tail latency stragglers  
- Spam evolution  
- Index lag / freshness complaints  
- Analyzer bugs (tokenization)  
- ACL leaks in enterprise mode  
- Cost blowups from render + neural  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Web vs enterprise; scale targets |
| 5–15 | Crawl + processing + index |
| 15–25 | Query serve + ranking stages |
| 25–35 | Freshness, spam, suggest |
| 35–45 | 10×/100×/1000×, deal-breakers |

### 6.5 Closer

> **Search engine:** crawl async, index in immutable segments, serve via pruned scatter-gather, rank in stages, tier for freshness, fight spam continuously—scale with shards and cells, not a bigger single box.

---

## 7. Deeper / Related Interview Questions

### 7.1 Crawling

**Q: How politeness?**  
A: Per-host token buckets; respect crawl-delay; shared host queues.

**Q: Canonicalization?**  
A: Normalize scheme/host/path/query params; rel=canonical; duplicate clusters.

**Q: Infinite spaces?**  
A: URL budgets; parameter blocking; sitemap prioritization.

### 7.2 Indexing

**Q: How incremental?**  
A: Soft deletes + new postings; segment merges; tombstones.

**Q: Near-real-time?**  
A: In-memory buffer searchable; refresh interval tradeoff.

**Q: Why immutable segments?**  
A: Simple concurrency; crash safety; cache friendliness.

### 7.3 Serving

**Q: How beat p99 stragglers?**  
A: Hedged requests, good replicas, limit fanout, caching, load balanced shards.

**Q: Deep paging?**  
A: Search-after cursors; discourage page 1000; re-query quality drops.

### 7.4 Ranking

**Q: Offline vs online metrics?**  
A: nDCG/ERR offline; online interleaving/A/B; watch satisfaction & abuse.

**Q: Position bias?**  
A: Propensity scoring; randomization in training data collection carefully.

### 7.5 Neural search

**Q: Replace BM25?**  
A: Usually fuse; lexical still strong for exact matches (SKUs, names).

**Q: Latency?**  
A: ANN retrieve top-k cheap; cross-encoder only on tiny set.

### 7.6 Microsoft angles

**Q: Bing vs Google talking points?**  
A: Focus on your design; mention markets, safe search, freshness news vertical.

**Q: Azure Cognitive Search?**  
A: Managed inverted index + enrichment; good for enterprise/site; web-scale is custom.

### 7.7 Interview traps

| Trap | Better |
|------|--------|
| “Just use Elasticsearch” | Explain shards, rank, crawl still |
| “Store all docs in SQL LIKE” | Won’t scale |
| “PageRank online per query” | Precompute static features |
| “Return perfect recall always” | Prune; approximate OK |

### 7.8 Security trimming

**Q: Autocomplete leak?**  
A: Suggestions must be ACL-aware or only public corpus.

**Q: Count leak?**  
A: Don’t return exact total hits across unauthorized docs.

### 7.9 Multilingual

Language detection; per-language analyzers; market-specific rank; cross-language search optional.

### 7.10 Snippets

Store compressed text or positional hits to reconstruct highlights; respect paywall/robots for show.

### 7.11 Related systems

Notification (saved search alerts), world-scale website (site search), LLM enterprise search (RAG) as evolution.

### 7.12 LLD pivot

Implement tokenizer + inverted index map + BM25 scorer + top-k heap; or URL frontier priority queue with host politeness.

### 7.13 Evaluation

Golden query sets; human judges; spam regression suites; latency SLOs in CI for ranker.

### 7.14 Incident vignette

**Symptom:** p99 2s.  
**Checks:** slow shards, GC, cache HIT collapse, ranker timeout, bad deploy, viral query skew.  
**Mitigate:** shed L3, raise cache, rebalance, hedge reads.

### 7.15 Freshness complaint

Increase crawl priority for impacted hosts; check indexer lag; hot tier health; CDN of news partners.

---

## 8. Appendices

### 8.1 Schema / structure sketches

```text
URLRecord(url, canonical_id, host, priority, last_fetched, etag, status)
Document(doc_id, canonical_url, lang, title, text_hash, static_rank, spam_score, fetched_at)
Posting(term_id, doc_id, tf, payload)
Segment(segment_id, term_dict, postings, doc_meta, created_at, state)
QueryLog(query, market, ts, results, clicks) // privacy constrained
```

### 8.2 API checklist

- [ ] Query + market + safe  
- [ ] Suggest  
- [ ] Spell altered query signal  
- [ ] Latency budgets / timeouts  
- [ ] Enterprise ACL context  
- [ ] Ops index APIs idempotent  
- [ ] Takedown API  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Inverted index | term → postings |
| Postings | docs containing term |
| DAAT | document-at-a-time retrieval |
| WAND | Weak AND dynamic pruning |
| Static rank | Query-independent quality |
| Segment | Immutable index piece |
| Frontier | URLs waiting to crawl |
| Security trimming | ACL filter for enterprise |
| nDCG | Ranking quality metric |
| ANN | Approximate nearest neighbor |

### 8.4 Progressive scale checklist

| Scale | Must |
|-------|------|
| 1× | Inverted index + BM25 + crawl/ingest |
| 10× | Shards/replicas + cache + spell/suggest |
| 100× | Tiers + multi-stage rank + geo serve |
| 1000× | Continuous web fabric + neural fusion + spam war |

### 8.5 BM25 reminder (speakable)

```text
score(q,d) = Σ IDF(t) * tf_norm(t,d) * length_norm(d)
Good baseline L1; still used beneath fancy models
```

### 8.6 Broker pseudocode

```text
def search(q):
  q2 = rewrite(q)
  if cache.get(q2): return
  parts = fanout(q2, shards, timeout=T)
  cands = merge_top(parts, K1)
  ranked = l2_l3(cands, q2)
  return snippets(ranked)
```

### 8.7 Frontier priority

```text
priority = importance * churn * staleness_factor * (1 - robots_block)
pop highest under per-host rate constraint
```

### 8.8 Segment publish

```text
build segment offline/nearline
validate checksums + smoke queries
atomic alias swap to make live
keep previous for rollback
```

### 8.9 Metrics dictionary

| Metric | Why |
|--------|-----|
| `query_p99_ms` | SLO |
| `cache_hit_ratio` | Cost/latency |
| `index_lag_seconds` | Freshness |
| `crawl_success_rate` | Supply |
| `spam_ratio_indexed` | Quality |
| `zero_result_rate` | UX |
| `nDCG_offline` | Relevance |
| `shard_straggler_rate` | Tail latency |

### 8.10 Kill switches

- Disable L3 neural  
- Disable personalization  
- Serve cache-only mode  
- Freeze index publish  
- Block host / domain  
- SafeSearch force on  

### 8.11 Chaos drills

1. Kill shard primary  
2. Inject slow replica  
3. Publish bad segment (should fail validation)  
4. Spam outbreak simulation  
5. Query flood  
6. Frontier deadlock  
7. Dictionary/analyzer bug canary  

### 8.12 Deal-breakers extended

1. Query-time web fetch  
2. No takedown path  
3. Rank-only-clicks without anti-spam  
4. Single global mutable posting list file  
5. Ignoring language/market  
6. Enterprise search without ACL  

### 8.13 Interview “say this” (60s)

> I’d split crawl, index, and serve. Build immutable inverted-index segments with replicas, serve via scatter-gather with dynamic pruning and multi-stage ranking, and keep a hot tier for freshness. Autocomplete/spell sit beside the main path. Scale is sharding plus geo cells; relevance is continuous evaluation—not a one-time BM25 choice.

### 8.14 Cost worksheet

| Item | Driver |
|------|--------|
| Storage | postings + doc store + vectors |
| Crawl egress | fetches / render |
| Serving CPU | fanout + score |
| GPU | L3 rerank |
| Human judge | eval sets |

### 8.15 Oncall first five minutes

1. Latency or relevance?  
2. One market/shard or global?  
3. Index publish recent?  
4. Cache HIT collapsed?  
5. Ranker model flip?  
6. Crawl/indexer backlog (if freshness SEV)?  

### 8.16 Analyzer pipeline

```text
Unicode normalize -> tokenize -> lowercase -> stop/stem (lang-specific)
-> synonyms (careful) -> term IDs
Same analyzer at index and query (with query-only expansions)
```

### 8.17 Result cache keys

```text
(q_normalized, market, safe, featureset_version, index_generation)
Short TTL; purge on generation bump for critical
```

### 8.18 News vertical

Separate ingestion from partners; ultra-fresh index; UI tab; rank with time decay; careful duplication across outlets.

### 8.19 Vector / hybrid search addendum

```text
Lexical candidates ∪ ANN candidates -> fusion -> L2/L3
Keep lexical for exact match precision
```

### 8.20 Spam feature examples

- Link farm neighborhoods  
- Keyword stuffing ratios  
- Cloaking mismatches  
- Domain age / cert anomalies  
- Redirect chains  
- User reports  

### 8.21 Capacity narrative

At 200K QPS with fan-out to 2,000 shards without pruning/cache, broker messaging alone explodes. Hence caching head queries, early termination, and replica-local execution are mandatory talking points at 100×.

### 8.22 Enterprise connector sketch

```text
Connector sync -> change log -> process -> index with ACL payload
Query principal -> expand groups -> filter docs
Audit access
```

### 8.23 SafeSearch

Separate adult scores; filter/demote; image/video stricter; log policy decisions.

### 8.24 Ranking experiment discipline

- Feature freeze windows  
- Interleaving  
- Guardrail metrics (spam, latency, diversity)  
- Auto rollback  

### 8.25 URL dedup / simhash

Near-duplicate detection via simhash/minhash; keep canonical; cluster mirrors.

### 8.26 Failure injection catalog

- Corrupt segment checksum  
- robots suddenly disallow major host  
- Ranker timeout storm  
- Suggest dictionary poison  
- Clock skew on freshness  

### 8.27 Topic closer checklist

- [ ] Clarified web vs enterprise  
- [ ] Planes split  
- [ ] Index segment model  
- [ ] Multi-stage rank  
- [ ] Progressive scale  
- [ ] Deal-breakers (crawl-on-query, ACL)  

### 8.28 One-breath closer

> Async crawl, immutable indexes, pruned scatter-gather, staged ranking, freshness tiers—search is a relevance factory with an SLO.

### 8.29 Supplemental Q&A

**Q: How do you handle site:example.com?**  
A: Postings filtered by site inverted structure / doc domain attributes; dedicated postings optional.

**Q: Image search?**  
A: Separate index with visual embeddings + text alt; different spam.

**Q: Voice queries?**  
A: ASR text → same engine; rewrite conversational filler.

**Q: Knowledge cards?**  
A: Parallel verticals / entity lookup; not core inverted replace.

**Q: How much to implement in 45m?**  
A: Prefer strong crawl→index→serve story + ranking stages over naming 50 Google papers.

### 8.30 Comparison: site search vs web vs enterprise

| | Site | Web | Enterprise |
|--|------|-----|------------|
| Ingest | Feed/CMS | Crawl | Connectors |
| Scale | M docs | 100B URLs | Per-tenant |
| ACL | Rare | Public | Critical |
| Spam | Low | Extreme | Insider threat / docs |
| Freshness | Publish-driven | Crawl priority | Sync-driven |

### 8.31 Worked example query

```text
q = "azure front door wfh"
analyze -> tokens
spell ok
retrieve BM25 candidates
static rank + freshness for docs.microsoft.com
L2 features (url depth, click model)
L3 neural semantic confirm
snippet highlight "Front Door"
safe ok
return
```

### 8.32 Related Microsoft products narrative

Bing web search, Bing Webmaster crawl signals, Microsoft Search in M365, Azure AI Search for app builders—pick one framing and be consistent.

### 8.33 Final reminder

Microsoft may ask you to **code a mini inverted index** after HLD. Keep a simple `dict[str, list[Posting]]` + BM25 ready, plus discuss how it becomes segmented/sharded in production.

### 8.34 Extra operability

**Index rollback:** point alias to previous generation.  
**Shard rebalance:** copy segments; avoid query downtime.  
**Host banhammer:** frontier + index delete pipeline.  
**Query understanding freeze:** dictionaries versioned with index.  
**SLO burn:** shed rerank first, then expand timeouts carefully.

### 8.35 Progressive scale recap

| Jump | Slogan |
|------|--------|
| 10× | Shards + cache |
| 100× | Tiers + multi-stage |
| 1000× | Geo cells + neural fusion + spam war |

### 8.36 Responsible search notes

- Child safety  
- Misinformation demotion policies (careful, transparent)  
- Copyright / DMCA takedown SLAs  
- Privacy in query logs (hashing, retention)  

### 8.37 End checklist for interview whiteboard

1. Draw three planes  
2. Walk one query  
3. Walk one document ingest  
4. Name pruning + ranking stages  
5. Show 100× tiering  
6. List deal-breakers  

---

*End of document — Search Engine*
