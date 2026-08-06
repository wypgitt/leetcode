# System Design: Globally Distributed Travel-Query Suggestion

> **Focus areas:** Autocomplete · Geo-filter · Fuzzy match · Multilingual · Trends · Personalization · Sub-100ms · Edge/CDN · Indexes (tries/FST/n-gram) · Cache tiers · Consistency of indexes  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split **suggest QPS** vs **index build**, explicit latency budget, honest global active-active vs home-cell for writes  
> **Interview theme:** Uber — typeahead for travel queries (places / destinations / “airports near me”) with geo relevance, fuzzy multilingual matching, trending boosts, light personalization, **p99 < 100ms**

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

Goal: **bound the product**—a globally distributed **suggestion / autocomplete** service for travel-related queries. Users type a few characters; we return ranked place/query suggestions filtered by geo context, tolerant of typos, aware of language, boosted by trends, lightly personalized—under a hard latency SLO.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Query suggestion / typeahead | Full trip booking engine |
| Results | Top-N suggestions (places, query rewrites) | Full map search page with 1000 pins |
| Latency | **Sub-100ms** p99 interactive | Batch recommendations offline-only |
| Index | Search/suggest indexes + caches | OLTP ride matching |
| Personalization | Light (recents, home city, locale) | Deep ranking ML platform essay |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is suggested? | Places (POI/cities/airports) + popular query strings | Dual entity types or unified docs |
| F2 | Geo-filter? | Bias/filter by user lat/lng or city | Geo index + distance prior |
| F3 | Fuzzy? | Typos / missing chars | Edit-distance / n-gram / phonetic |
| F4 | Multilingual? | Names in many scripts; locale-aware | Normalized tokens + language fields |
| F5 | Trends? | Rising destinations / queries | Time-decay counters → boost |
| F6 | Personalization? | Recent searches, home, bookmarked | User side features at rank |
| F7 | Prefix behavior? | From 1–2 chars | Aggressive cache for short prefixes |
| F8 | N results? | 5–10 | Bound merge/heap |
| F9 | Freshness of catalog? | New POI minutes–hours OK | Nearline index build |
| F10 | Abuse? | Scraping / bot QPS | Rate limits, API keys |
| F11 | Offline? | Mobile partial cache Phase 2 | Edge bundles for top cities |
| F12 | Explainability? | Ops can see why boosted | Debug rank features |

**MVP functional scope (lock with interviewer):**

1. `GET /suggest?q=&lat=&lng=&locale=&limit=` → top 5–10 suggestions < 100ms p99 regional.  
2. **Geo bias** (not hard-only): prefer nearby / in-city entities.  
3. **Fuzzy** match for common typos (edit distance ≤1–2 on short strings via indexing tricks).  
4. **Multilingual** display names; query language detection / locale param.  
5. **Trending** boost from aggregated query logs (nearline).  
6. **Personalization**: recents + simple affinity (home city).  
7. Global serving from edge/regional; catalog updates nearline.  
8. Metrics: latency, empty rate, accept rate (click/select).

**Out of MVP:**

- Full semantic vector search as sole path (can be Phase 2 hybrid)  
- Perfect personalization with huge model on critical path  
- Global strongly consistent instant POI update in <1s everywhere  
- Building the entire Places knowledge graph from scratch narrative

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Feels instant | **p50 < 40ms, p99 < 100ms** in-region |
| N2 | Availability | Typeahead critical | 99.99% suggest; stale index OK vs down |
| N3 | Freshness | Trends hours; POI hours | Index publish SLO |
| N4 | Correctness | Good-enough ranking | Not money ledger |
| N5 | Global | Users everywhere | Multi-region active-active **reads** |
| N6 | Cost | Short-prefix storms | Cache heavy |
| N7 | Privacy | Recents sensitive | Per-user store ACL |
| N8 | Throughput | See scale table | Edge + regional clusters |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User types `air` near SFO → SFO Airport, Airbnb HQ?, "airports near me" queries.  
2. Typo `airprot` → airport via fuzzy.  
3. Locale `ja-JP` → Japanese names preferred when available.  
4. Trending: "Olympics city X" boosted in season.  
5. Personalization: last week searched "Napa" → floats when typing `na`.  
6. Empty query / focus → recents + trending local (if product allows).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| 1-char prefix | Only ultra-hot cache; limit work |
| Hot prefix `a` | Strictly cached / constrained candidate set |
| No geo provided | Fall back IP city / last known / global popular |
| Script mix (latin query for Japanese POI) | Romanization / aliases fields |
| Index deploy bad | Versioned indexes; instant rollback pointer |
| Region down | Route to nearest region; may lose some personalization |
| Personalization store timeout | **Fail open** to non-personalized (latency sacred) |
| Trend pipeline delay | Serve without boost; don't block |
| Poison POI name | Validation; abuse queue |
| Duplicate places | Entity resolution ids; dedupe in merge |
| Bot scrape | Rate limit; CAPTCHA/API gate |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| QPS peak suggest | 50K | 500K | 5M | 50M |
| Entities (POI+) | 50M | 100M | 500M | 1B+ |
| Query log events / day | 200M | 2B | 20B | 200B |
| Regions / edges | 5 | 10 | 20 | 30+ |
| Languages | 20 | 40 | 60 | 80+ |
| Index size / region | 50 GB | 100 GB | 500 GB | multi-TB sharded |
| Personalization QPS | 50K | 500K | 5M | 50M |
| Short-prefix cache hit | 70% | 80% | 85% | 90%+ |

**What each jump forces:**

- **10×:** Edge cache for top prefixes; regional suggest clusters; separate trend job.  
- **100×:** Shard index by geo cell / segment; SIMD/FST; personalization async/cancellable.  
- **1,000×:** Heavy CDN/edge compute; language-specific analyzers fleet; hierarchical indexes; strict budget admission.

### 1.5 Scope repeat-back

> Design a globally distributed travel-query suggestion service: geo-biased, fuzzy, multilingual autocomplete with trending and light personalization, p99 < 100ms via edge caches and regional indexes—nearline index builds, fail-open personalization, progressive shard/scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Suggest reads | 50K QPS | 50M QPS | Dominates; must be cached/edged |
| Personalization reads | ≈ suggest | ≈ suggest | Budget-capped |
| Query log ingest | ~10K/s avg | ~2M+/s | Async |
| Index build | batch/nearline | continuous | Not on request path |
| Catalog updates | low QPS | low–med | Publish pipeline |

**Critical insight:** Suggest path is **read-mostly**. Never build fuzzy scans on primary DB per keystroke.

### 2.2 Latency budget (100ms p99)

```text
Edge/LB                     5–10ms
Auth/rate-limit             1–3ms
Prefix cache lookup         1–5ms   (hit → return)
Personalization fetch       5–15ms  (parallel, timeout 10–15ms)
Index retrieve candidates   5–20ms
Geo filter + rank merge     5–15ms
Response serialize          1–3ms
--------------------------------
Total budget ~40–70ms typical; p99 < 100ms with headroom
```

**Rule:** personalization **parallel + timeout**; on timeout proceed without.

### 2.3 Cache math

```text
Unique prefixes per region-hour: heavy-tailed
Top 10K prefixes may serve majority of QPS for len≤3

Cache entry ~2 KB (10 suggestions)
10K × 2 KB = 20 MB — trivial per edge
1M prefixes × 2 KB = 2 GB — still fine regionally
```

### 2.4 Index memory

```text
50M entities × 200 B doc = 10 GB raw
Inverted / FST / n-gram structures ×3–10 → 30–100 GB / full replica
⇒ shard by geography (continents/cities) or entity type
```

### 2.5 Typing amplification

```text
User types 8 chars with suggest each time → ~8 requests / query session
50K QPS suggest ⇒ ~6K sessions/s order-of-magnitude
Design for prefix patterns, not "one request per destination"
```

### 2.6 Bottlenecks

1. Len-1/len-2 prefix storms  
2. Cold personalization dependency  
3. Giant unsharded index  
4. Synchronous trend recompute  
5. Cross-region round trip on critical path  
6. Huge candidate sets before top-N  

---

## 3. High-Level Design

### 3.1 Request path (online)

```text
Client -> Edge/CDN/API Gateway
       -> Suggest Service (regional)
            parallel:
              A. Prefix/Trigram cache
              B. User features (recents, prefs) [timeout]
              C. Geo context normalize (H3/S2 cell)
            -> Candidate retrieval (indexes)
            -> Filter/dedupe
            -> Rank (text + geo + trend + personal)
            -> Top-N response + cache store
       -> async log query for trends
```

### 3.2 Document model

```text
SuggestionDoc {
  id, type: POI|QUERY|AIRPORT|CITY,
  names: [{lang, text, script, is_primary}],
  aliases: [],
  geo: {lat, lng, h3, city_id, country},
  popularity: static_score,
  trend_score: nearline,
  categories: [],
  status: ACTIVE
}
```

### 3.3 Indexing options

| Structure | Role | Notes |
|-----------|------|-------|
| Prefix trie / FST | Exact/prefix | Memory-efficient (Lucene FST) |
| Edge n-grams | Partial / fuzzy-ish | `"airport" → "air","airp",...` |
| Trigram inverted | Fuzzy typos | Good for edit distance |
| Geo index (H3→ids) | Geo filter/bias | Restrict candidate universe |
| Vector ANN (Phase 2) | Semantic | Not MVP critical path sole |
| Phonetic (Metaphone) | Soundex-like | Language-specific care |

**Chosen MVP stack:**  
- **OpenSearch/Elasticsearch** or in-memory **custom FST+trigram** shards per region.  
- Geo filter via `geo_distance` / H3 terms.  
- Separate **trend KV** joined at rank.  
- Edge **prefix cache**.

### 3.4 Ranking (explainable)

```text
score = w_text * text_match(q, names)
      + w_geo  * geo_affinity(user, doc)
      + w_pop  * log(1+popularity)
      + w_trend* trend_score
      + w_pers * personal_affinity
      + w_type * type_prior (airport > random POI for travel)
```

Hard filters: `ACTIVE`, optional radius max, language availability soft.

### 3.5 Fuzzy strategy (practical)

| Query len | Strategy |
|-----------|----------|
| 1–2 | Cache + popular only; limited fuzzy |
| 3–5 | Prefix + trigram OR edit≤1 |
| 6+ | Prefix/FST primary; fuzzy if low results |

**Deal-breaker:** Levenshtein against 50M names online.

### 3.6 Multilingual

- Store per-language name fields; `locale` prefers field.  
- Normalize: casefold, accent-fold (language rules), unicode NFKC.  
- Aliases: romanizations (`東京` ↔ `Tokyo`).  
- Analyzer per language at index time; don't runtime-stem poorly across scripts.

### 3.7 Trends pipeline (nearline)

```text
Suggest logs → Kafka → windowed counts by (normalized_query|entity_id, geo_cell)
 → decay score (e.g. EWMA 1h/1d)
 → publish trend_score to KV / index field refresh
```

Not on request path synchronously.

### 3.8 Personalization

| Feature | Store | Budget |
|---------|-------|--------|
| Recent queries/places | User KV / Redis | 5–15ms timeout |
| Home city / language | Profile cache | cached at edge cookie/JWT claims when possible |
| Bookmarks | User KV | same timeout |

**Fail open.** Encode coarse prefs in signed client token for zero RTT when possible (careful privacy).

### 3.9 Global distribution

| Plane | Mode |
|-------|------|
| Suggest reads | Active-active multi-region |
| Index replicas | Per region; async publish |
| Catalog writes | Home / CMS pipeline single writer |
| Trends | Regional compute + global merge for worldwide trends |
| User recents | Home region or globally replicated KV with TTL |

**Deal-breaker:** Suggest request writes to cross-region primary before respond.

### 3.10 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Latency vs personalization | Timeout fail-open | Hit 100ms | Block on user DB |
| Exact fuzzy | Trigram/FST hybrid | Scalable | Online edit vs all docs |
| Geo | Bias + soft filter | Travel UX | Hard 5km only (miss airports) |
| Trends | Nearline | Stable | Sync count on each suggest |
| Edge cache | Short TTL + long for len≤2 | QPS | Cache personalized results shared (privacy leak) |
| Vector-only | Phase 2 hybrid | Latency/ops | Replace lexical entirely MVP |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                     +-------------------+
   Mobile/Web -----> | Edge / CDN / GW   |  (TLS, rate limit, prefix cache)
                     +---------+---------+
                               |
                     +---------v---------+
                     | Suggest Service   |  (regional autoscaled)
                     |  - orchestrate    |
                     +--+------+------+--+
                        |      |      |
           +------------+      |      +-------------+
           v                   v                    v
   +---------------+   +--------------+    +------------------+
   | User Feature  |   | Search Shard |    | Trend KV         |
   | Store (Redis) |   | FST/OS/ES    |    | (nearline)       |
   | timeout 10ms  |   | geo+text     |    +------------------+
   +---------------+   +--------------+
                               ^
                               | publish
                     +---------+---------+
                     | Index Builder     | <--- Catalog / Places CMS
                     | (nearline)        | <--- Trend scores
                     +---------+---------+
                               ^
                     Kafka query_logs ----+
```

### 4.2 Sequence: cache hit

```text
Client -> Edge Cache(q,geo_bucket,locale,lang) HIT -> 10 suggestions
(async log only)
```

**Note:** cache key **excludes user_id**; personalization applied as reorder on cached candidates *or* skip cache when personalization strong (MVP: cache generic, reorder with recents).

### 4.3 Sequence: cache miss

```text
SuggestSvc:
  async personal = userStore.get(uid) with deadline
  candidates = searchShard.query(prefix/fuzzy, geo)
  boost with trends
  if personal ready: reorder
  else: continue
  return topN
  fill caches (generic key)
  emit log
```

### 4.4 Index publish

```text
CMS update -> doc queue -> builder validates
 -> build segment version V+1
 -> push to regional replicas
 -> flip alias when warm
 -> keep V for rollback
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Suggest path **read-only** w.r.t. catalog.  
2. Personalization failures **fail open**.  
3. Index versions atomic alias flip.  
4. Cache keys never include PII payloads from other users.  
5. Rate limits protect shards.  
6. Empty result ≠ 500; degrade quality.  
7. Logs async; lossy OK under overload (sample).  
8. Latency SLO > perfect ranking under stress (admission/degrade).

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single regional ES/OpenSearch; Redis recents; edge CDN |
| 10× | Multi-region active-active; prefix cache; trend Flink |
| 100× | Geo-sharded indexes; per-language analyzers; cgroup latency budgets |
| 1000× | Edge compute suggest for len≤3; hierarchical city indexes; heavy sampling logs |

### 5.3 Maintainability

- Ranker config as data (weights per market).  
- Offline eval: recall@10, MRR, latency histograms.  
- Canary index to 5% traffic.  
- Debug endpoint `explain=1` internal-only.  
- Schema for docs versioned.

### 5.4 Progressive scale playbook

**Baseline:** 50K QPS; 50M entities; 5 regions; ES + Redis + CDN.  
**10×:** Cache hit 80%+ on short prefixes; search only on miss.  
**100×:** Shard by `country`/`h3_parent`; scatter-gather top shards only (user geo ± neighbors).  
**1000×:** Most QPS answered at edge; origin for long/rare tails; ML ranker aspirational async.

### 5.5 Geo deep dive

```text
user_h3 = h3(lat,lng,res)
retrieve:
  - entities in kRing(user_h3, k) with text match
  - OR globally popular airports/cities with text match (type prior)
score geo:
  exp(-distance / d0) or city_id match bonus
```

Hard radius alone fails "SFO" typed from Oakland—or "Tokyo" typed from SF (travel intent). Use **hybrid**: local POIs + global destinations of type city/airport.

### 5.6 Fuzzy deep dive

**Trigram:** index all trigrams of names; query trigrams of `q`; candidates by overlap; verify edit distance.

**Symmetric delete** (for small edit): precompute deletes for dictionary of hot names—good for small dictionaries, not 50M.

**FST fuzzy automata:** Lucene supports fuzzy queries with limits—cap expansions.

### 5.7 Multilingual deep dive

- ICU normalization.  
- Separate fields `name.en`, `name.zh`, `name.ja`.  
- `name.all` with analyzers careful—or multi-field search.  
- Transliteration service offline generates aliases.  
- Locale param > Accept-Language > IP guess.

### 5.8 Trends deep dive

```text
score = log(1 + count_1h) * w1 + log(1 + count_1d) * w2
decay hourly
spike detection: count_1h / baseline
geo-scoped trends vs global trends fields
```

### 5.9 Personalization deep dive

```text
recents: LRU 20 queries/places
affinity: +score if doc_id in recents or same city as home
diversity: don't fill all 10 with recents only
privacy: TTL; user delete; encrypt at rest
```

### 5.10 Degradation ladder

1. Skip personalization  
2. Skip fuzzy (prefix only)  
3. Skip trend  
4. Serve edge stale cache only  
5. Static popular destinations JSON  

Never 5xx cascade if catalog shard slow—timeouts everywhere.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| SQL `LIKE %q%` | Latency death |
| Block on personalization | Miss 100ms |
| Cache per-user suggestions at CDN | Privacy + cardinality |
| Single global unsharded index at 1000× | Hot cluster |
| Sync write trends on request | Melts |
| Hard geo-only | Bad travel UX |

---

## 6. Wrap-Up

### 6.1 Designed

Global travel-query suggestions with regional indexes, edge prefix caches, geo-biased hybrid retrieval, fuzzy/multilingual lexical matching, nearline trends, fail-open personalization, p99 < 100ms.

### 6.2 Decisions to defend

1. Latency budget with parallel personalization timeout  
2. Edge cache on **non-personalized** keys + local reorder  
3. FST/trigram/geo hybrid indexes  
4. Hybrid local + global destination retrieval  
5. Nearline trends  
6. Active-active reads; versioned index publish  
7. Degrade ladder under load  
8. Async query logging  

### 6.3 Risks

- GPS privacy / geo spoof  
- Multilingual quality gaps  
- Cache stampede on invalidation  
- Trend manipulation (bots)  
- Over-personalization creepiness  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope suggest vs search; 100ms SLO |
| 5–12 | QPS + latency budget |
| 12–25 | Indexes + geo + fuzzy + multi-lang |
| 25–35 | Trends, personalization fail-open, cache |
| 35–45 | Global active-active + 10×/100×/1000× |

### 6.5 Closer

> **Travel-query suggestion**: edge-cached, regionally indexed autocomplete with geo bias, fuzzy multilingual text, nearline trends, and **fail-open** personalization—engineered to a **100ms p99** budget first.

---

## 7. Deeper / Related Interview Questions

### 7.1 Latency

**Q: How guarantee p99 < 100ms?**  
A: Budget every dependency; timeouts; cache short prefixes; limit candidate N; no cross-region sync; degrade features.

**Q: Tail latency from GC?**  
A: Multiple replicas; hedged requests carefully; native indexes; avoid stop-the-world paths.

### 7.2 Indexing & algorithms

**Q: Trie vs inverted index?**  
A: Trie/FST great for prefix; inverted/trigram for fuzzy/contains; production often Lucene combining both.

**Q: Why FST?**  
A: Compressed automaton for ordered string dictionaries; memory efficient autocomplete.

**Q: BK-tree?**  
A: Nice for edit distance on small sets; not primary for 50M global POIs.

### 7.3 Geo

**Q: Geohash vs H3 for filter?**  
A: Either; use cell terms to restrict. Bias distance continuous in rank.

**Q: User in airplane over ocean?**  
A: Weak geo; rely on text + global popular + last city.

### 7.4 Multilingual

**Q: One analyzer for all?**  
A: No—language-specific + ICU; aliases for cross-script.

**Q: Detect language of query?**  
A: Heuristic / CLD; fallback locale; search multiple fields with weights.

### 7.5 Caching

**Q: Cache key design?**  
A: `norm(q)|geo_bucket|locale|limit|index_gen` — not `user_id`.

**Q: Invalidation?**  
A: Short TTL (30–120s) + generation counter on index flip.

**Q: Thundering herd?**  
A: Singleflight / request coalescing per key.

### 7.6 Trends & logs

**Q: Bot inflation?**  
A: Auth rate limits; filter unauthenticated; anomaly on prefix.

**Q: Real-time trends?**  
A: Minutes–hours enough; true real-time rarely needed for travel suggest.

### 7.7 Personalization & privacy

**Q: GDPR delete?**  
A: Wipe user recents; caches TTL naturally expire; don't put user data in shared CDN objects.

**Q: Cross-device recents?**  
A: User home KV; may add latency—timeout fail-open.

### 7.8 Consistency

**Q: New airport not appearing?**  
A: Nearline publish lag; state SLO (e.g. <15m). Not transactional with airline DB.

**Q: Different regions different results?**  
A: Expected briefly during publish; versions converge.

### 7.9 Queues & pipelines

**Q: Kafka for suggest path?**  
A: No—only logs/builds. Online path RPC/cache/index.

**Q: Index build from CDC?**  
A: Yes—Places DB CDC → builder.

### 7.10 Ranking / ML

**Q: Learning-to-rank?**  
A: Phase 2; start with weighted linear; log features for training.

**Q: Vector search?**  
A: Hybrid retrieve semantic recall then lexical filter; watch latency.

### 7.11 Interview traps

| Trap | Pushback |
|------|----------|
| Postgres `LIKE` | Miss SLO |
| Must personalize always | Miss SLO / outage |
| Global single ES | Geo RTT + blast radius |
| Cache personalized at CDN | Privacy SEV |
| Exact edit distance all docs | CPU death |
| 50K QPS ⇒ 50K DB writes | Confused read path |

### 7.12 Metrics

| Metric | Why |
|--------|-----|
| Suggest p50/p99 | SLO |
| Cache hit rate | Scale |
| Empty rate | Quality |
| Select rate / MRR | Relevance |
| Personalization timeout rate | Dependency health |
| Index publish lag | Freshness |
| Fuzzy fallback rate | Cost |

### 7.13 Comparison

**Q: vs Google Places autocomplete?**  
A: Similar; emphasize travel types, Uber geo contexts, marketplace integrations.

**Q: vs restaurant metrics Top-K?**  
A: Different—online low-latency retrieval vs stream windows.

---

## 8. Appendices

### 8.1 API sketch

```text
GET /v1/suggest
  ?q=airp
  &lat=37.77&lng=-122.42
  &locale=en-US
  &limit=8
  &session_token=...

Response:
{
  "suggestions": [
    {"id":"poi_sfo","type":"AIRPORT","title":"San Francisco International Airport",
     "subtitle":"San Francisco, CA","distance_m":18000,"score":12.3}
  ],
  "server_ms": 18,
  "index_gen": 1042
}
```

### 8.2 Cache key

```text
sg:{index_gen}:{locale}:{h3_res4}:{norm_q}:{limit}
```

### 8.3 Rank feature vector (debug)

```text
text_score, geo_score, pop_score, trend_score, personal_score, type_prior
```

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| FST | Finite state transducer dictionary |
| Trigram | 3-char overlapping tokens for fuzzy |
| Fail open | Skip feature on timeout |
| Index gen | Monotonic publish version |
| Geo bucket | Coarse H3 for cache key |
| Nearline | Minutes-latency offline/online hybrid |
| Romanization | Phonetic latin form of non-latin names |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | ES/FST, geo bias, Redis recents, CDN cache |
| 10× | Multi-region, trends pipeline, coalescing |
| 100× | Geo shards, language fields, degrade ladder |
| 1000× | Edge answers short prefixes; hierarchical indexes |

### 8.6 Normalization sketch

```text
function norm(q):
  NFKC
  casefold
  strip punct
  collapse space
  optional accent fold per locale
```

### 8.7 Interview “say this” (60s)

> Travel suggest is a **global read path** engineered to **100ms p99**: edge caches for short prefixes, regional lexical+geo indexes (FST/trigram), hybrid local POI + global destinations, nearline trends, and personalization fetched in parallel with a tight timeout and **fail-open**. Index builds are nearline with versioned rollback—not on the keystroke path.

### 8.8 Reliability test plan

1. Kill user feature Redis → still <100ms, non-personalized.  
2. Bad index publish → rollback alias.  
3. Hot prefix `a` → served from cache; origin protected.  
4. Typo query → fuzzy returns airport.  
5. Locale ja → Japanese title when present.  
6. Region failover → requests routed; quality OK.  
7. Bot QPS → rate limited.

### 8.9 Related systems map

```text
Places CMS → Index Builder → Regional Shards ← Suggest Service ← Edge Cache ← Client
Query Logs → Trend Jobs → Trend KV ----^
User Recents Store ---------------------^
```

### 8.10 Extra traps

| Trap | Pushback |
|------|----------|
| Personalized CDN objects | Leakage |
| Sync ML model 200ms | Break SLO |
| One language analyzer | Multilingual fail |
| Hard 1km filter | Miss airports |

### 8.11 Unit checks

```text
p99 budget components must sum < 100ms with parallelization
50M × 200 B = 10 GB docs raw — indexes larger; shard
Top 10K prefix cache × 2 KB = 20 MB
```

### 8.12 Session token

- Client session groups keystrokes for logging/analytics without forcing auth.  
- Dedup logs client-side when possible.

### 8.13 Empty query behavior

```text
if q empty:
  return recents (if auth) + local trending + popular airports
  still <100ms; heavily cached per geo_bucket
```

### 8.14 Security

- Auth optional for suggest; stricter for recents write.  
- Input length cap (e.g. 64 chars).  
- Strip control chars.  
- Partner API keys with quotas.

### 8.15 Offline eval harness

```text
dataset: (q, geo, locale) -> clicked_id
metrics: MRR, Recall@5, latency replay against candidate index gen
gate: no ranker ship if MRR regresses > X without latency win
```

### 8.16 Scatter-gather geo shards

```text
user cell → primary shard S0
also query neighbor shards S1..Sk (k small)
each returns top M
merge heap → top N
deadline: cancel slow shards after 20ms; degrade with partial
```

Never wait on all continents for a local typeahead.

### 8.17 Prefix storm controls

```text
if len(q) <= 2:
  serve only from edge cache / static popular
  origin QPS hard capped per prefix
if origin overloaded:
  return stale cache even past TTL (stale-while-revalidate)
```

### 8.18 Alias & entity resolution

```text
POI duplicates ("SFO" vs "San Francisco Intl") → canonical entity_id
suggestions dedupe by entity_id before return
aliases point to canonical for indexing
```

### 8.19 Client UX contract

- Debounce 50–100ms; cancel in-flight on new keystroke.  
- `session_token` groups requests.  
- Show distance / city subtitle for disambiguation.  
- Preserve last good list on error (don't flash empty).

### 8.20 Interview closer card

| Say | Don't say |
|-----|-----------|
| 100ms budget with timeouts | "Personalize at all costs" |
| Edge cache non-personalized keys | "CDN cache per user" |
| FST/trigram + geo hybrid | "`LIKE %q%`" |
| Nearline trends | "INCR trend on request path" |
| Fail-open features | "500 if Redis down" |
| Versioned index rollback | "Mutate index in place live" |

### 8.21 Related Uber systems

| System | Relationship |
|--------|--------------|
| Places / POI catalog | Document source |
| Rider destination entry | Primary client |
| Heat map / demand | Optional trend signals (not critical path) |
| Matching | Consumes selected place as pickup/dropoff — after suggest |

---

*End of travel-query suggestion system design.*
