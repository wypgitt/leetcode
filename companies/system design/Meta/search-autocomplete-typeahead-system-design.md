# System Design: Search Autocomplete / Typeahead

> **Focus areas:** Prefix indexes / trie · Top-K ranking · Hot-prefix cache · Typo tolerance · Personalization · p99 latency · Offline→online serving  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit latency budget, split suggest-read vs log-learn planes, deal-breakers for “query warehouse on each keystroke”  
> **Interview theme:** Classic Meta search infra — Instagram/Facebook/Workplace-style typeahead under extreme QPS with safety and freshness

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

Goal: **bound the product**—a **typeahead / autocomplete** service that returns top-K suggestions as the user types, with ranking, light personalization, typo tolerance, safety filtering, and strict latency (p99 tens of ms), at Meta search-box scale.

### 1.0 What this is / is not

| Dimension | **Autocomplete / typeahead (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Prefix → ranked suggestions fast | Full Graph Search / SERP ranking |
| Success | Relevant, safe suggestions; p99 tight | Perfect semantic understanding MVP |
| Index | Prefix structures + scores | Live scan of all queries each keystroke |
| Personalization | Re-rank small candidate set | Heavy private model per keystroke at 100M QPS |
| Entities | Queries + optional people/pages tabs | Full social graph traversal as sole path |

**Scope statement:** Design search autocomplete/typeahead: sharded prefix serving, ranking, hot-prefix cache, typos, light personalization, safety—with progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Suggest what? | Search queries/phrases; optional people/hashtags tabs | Separate indexes per vertical or unified with type |
| F2 | Top-K? | 8–10 UI; compute 20–50 candidates | Truncate after rank |
| F3 | Ranking? | Popularity, CTR, freshness, context | Offline score + online boosts |
| F4 | Personalization? | Recents + locale/language; friends boost Phase 1.5 | Client recents + thin profile |
| F5 | Typos? | Yes for len≥3, 1-edit common | Fuzzy layer budgeted |
| F6 | Languages? | Multi-locale | Partition by locale |
| F7 | Safety? | Block NSFW, hate, PII leaks, self-harm | Policy filter before return |
| F8 | Freshness? | Viral queries in minutes–hours | Nearline delta updater |
| F9 | Empty prefix? | Trending / zero-state | Separate trending list |
| F10 | Analytics? | Impression/click logs | Async learning pipeline |
| F11 | Client cache? | Optional first-char / session | Hybrid edge/client |
| F12 | Auth? | Logged-in personalization; logged-out global | Two modes |

**MVP functional scope:**

1. `GET /suggest?q=&locale=&limit=&vertical=` → ranked suggestions.  
2. Offline build of prefix index from query logs + scores.  
3. Online serve from memory shards + hot-prefix cache.  
4. Basic typo tolerance (normalize + common fuzzy).  
5. Personalization: boost user’s recent queries + locale.  
6. Safety/blocklist filter on serve path.  
7. Async impression/click logging.  
8. Nearline path for spike queries.

**Out of MVP:**

- Full LLM next-token decoding per keystroke as sole path  
- Deep semantic vector suggest without candidate restriction  
- Complete people-search graph ranking (thin people tab OK)  
- Cross-script transliteration beyond simple normalize (Phase 1.5)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Instant per keystroke | **p99 < 50ms** in-region suggest |
| N2 | Availability | Search box critical | 99.99%; stale index OK |
| N3 | Throughput | Huge read QPS | Millions+ via cache/edge |
| N4 | Freshness | New terms reasonably soon | Minutes–hours MVP |
| N5 | Consistency | Suggestions may lag logs | Eventual OK |
| N6 | Cost | Memory-heavy serving | Shard + compression |
| N7 | Privacy | No leaking rare PII queries | Aggregation thresholds |
| N8 | Safety | No banned suggestions | Filter non-bypassable |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User types `how to b` → suggestions in <50ms.  
2. `facebok` → fuzzy → `facebook`.  
3. Recent `flights to tokyo` boosted on `fli`.  
4. Viral meme appears within ~15–60 min nearline.  
5. Empty query → locale trending.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Prefix length 1 | Only precomputed head; hard CPU cap |
| Hot prefix `how` | Precomputed top-K; no fanout walk |
| Unicode / accents | NFKC + casefold; locale rules |
| Banned term | Filtered; sanitized alts optional |
| Shard timeout | Partial/cached; never multi-second wait |
| Personalization down | Fall back to global |
| Click log delay | Ranking lag OK |
| Very long query | Cap e.g. 100–128 chars |
| Bot scrape | Rate limit; anomaly bans |
| Homoglyph attacks | Confusable normalization / block |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Suggest QPS (peak) | 100K | 1M | 10M | 100M |
| Unique prefixes/day | 50M | 500M | 5B | 50B |
| Phrases in index | 100M | 1B | 10B | 100B |
| Locales | 20 | 50 | 100 | 200+ |
| Candidates scored | 20–50 | 20–50 | 30–100 | hierarchical |
| Hot prefixes cached | 1M | 10M | 100M | edge mega-cache |
| Index memory / cell | 50GB | 200GB | TB fleets | geo cells |
| Rebuild / update | hours batch | +nearline | incremental | continuous |

**What each jump forces:**

- **10×:** Mandatory hot-prefix cache; shard locale+prefix; trim tries.  
- **100×:** Edge/POP suggest; personalization as re-rank only; nearline deltas.  
- **1,000×:** Client+edge hybrid; hierarchical language cells; approx structures.

### 1.5 Etc. (Constraints & Assumptions)

- Upstream **search query logs** exist (not designing full crawler).  
- Ambiguity: autocomplete of **queries** vs entities—lock queries MVP; people tab optional.  
- Latency budget = in-region service time; client RTT separate.  
- Quality via offline NDCG/CTR + online experiments.

**Scope statement:**

> Design a Meta-scale search autocomplete service serving top-K prefix suggestions under p99 < 50ms using sharded in-memory prefix indexes, offline+nearline ranking, hot-prefix caches, light personalization, typo tolerance, and safety filters—scaling via edge caching and hierarchical sharding.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Suggest reads** | Per keystroke | 100K QPS | 1M | Edge + suggest |
| **Hot cache hits** | Head prefixes | 70–90% | higher | Edge/Redis |
| **Trie/shard misses** | Tail prefixes | 10–30K QPS | ×10 | Suggest servers |
| **Log ingest** | Imp/click | ~same order as suggests | ×10 | Kafka |
| **Index build** | Batch/nearline | continuous low | ×10 | Offline |
| **Personalization** | Profile get | subset of QPS | ×10 | Cache |

**Anti-pattern:** one “QPS” mixing CDN hits, shard CPU, and Hadoop jobs.

### 2.2 Latency budget (p99 < 50ms)

```text
Edge routing:        1–3 ms
Hot cache lookup:    1–5 ms
Auth/context:        1–3 ms (cached)
Shard trie walk:     5–15 ms
Rank + safety:       2–5 ms
Personalize re-rank: 2–5 ms
Serialization:       1–2 ms
--------------------------------
Total budget:        ≤ 50 ms p99 in-region
```

**Deal-breaker:** remote OLAP / fanout to 20 services per keystroke.

### 2.3 Memory math

```text
100M phrases × avg 24B key+score compressed ≈ 2.4 GB raw-ish (optimistic)
With trie structure + postings overhead ×3–10 → tens of GB per locale cluster
Must shard; cannot fit “all languages all phrases” on one box at 100×
```

### 2.4 Hot prefix leverage

```text
Top 1% of prefixes may serve 70–90% of QPS
Precompute top-K for those prefixes → mostly RAM/edge hits
Tail: real trie walk on shards
```

### 2.5 Learning traffic

```text
100K suggests/s × 8 impressions ≈ 800K impression logs/s peak (or sample)
Clicks much sparser (~few %)
Store sampled features for training; don’t block suggest on log ACK
```

---


### 2.6 Trie / FST memory worksheet

```text
Naive trie: per-node pointers dominate — 100M phrases can be tens–hundreds GB
Compressed:
  FST / radix / LOUDS succinct tries: often 5–20× smaller
  Store phrase ids + scores in parallel arrays
Example target: 10–40 GB RAM per large locale shard cluster (replicated)
Must shard by locale + prefix; cannot fit all languages on one box
```

### 2.7 Edge cache sizing

```text
Hot prefixes: top 100K prefixes × 10 suggestions × 40B ≈ 40 MB payload dict
With JSON overhead / multiple locales: few GB at edge — cheap vs origin CPU
TTL 10–60s; invalidate on blocklist epoch bump (must not serve banned)
```

### 2.8 Typo expansion cost

```text
Query len 8, 1-edit candidates ≤ 32 after dictionary intersect
Each candidate trie walk ~μs–ms; budget total fuzzy ≤ 5–10ms
If exact already filled K with high scores: skip fuzzy
```

### 2.9 Progressive capacity

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Suggest QPS | 100K | 1M | edge | geo cells |
| Hot cache hit | 70–90% | higher | higher | client hybrid |
| Index RAM | tens GB | sharded | many locales | succinct + tier |
| Nearline deltas | optional | yes | yes | mandatory |

**Anti-patterns:** SQL LIKE per keystroke; unbounded fuzzy; per-user full index; safety only in training.

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/suggest?q&locale&limit&vertical` | Ranked suggestions JSON |
| `GET /v1/trending?locale` | Zero-query |
| `POST /v1/log` (or client beacon) | Imp/click events async |
| `POST /admin/block` | Policy block phrase/prefix |
| `GET /internal/health` | Index version / age |

**Response:**

```json
{
  "q": "how to b",
  "locale": "en_US",
  "index_version": 184422,
  "suggestions": [
    {"text": "how to boil eggs", "score": 0.92, "type": "query"},
    {"text": "how to build muscle", "score": 0.88, "type": "query"}
  ]
}
```

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| Phrase score | `(locale, phrase)` | popularity, CTR, freshness |
| Prefix top-K | `(locale, prefix)` | precomputed list (hot) |
| Blocklist | phrase/prefix/regex | policy action |
| User recents | `user_id` | last N queries |
| Index manifest | `shard` | version, checksum |

### 3.3 Offline → online pipeline

```text
Query logs → aggregate counts / CTR
  → score phrases (popularity × CTR × freshness × safety prior)
  → build compressed prefix index per locale shard
  → publish index artifacts to object store
  → suggest servers pull / mmap new version (blue-green)
  → nearline: spike detector → delta updates to hot cache / side index
```

### 3.4 Ranking model (MVP)

```text
score = w1*log(count+1) + w2*CTR + w3*recency + w4*personal_boost - penalties
personal_boost = hit in user recents OR locale preference
safety: if blocked → remove (not just downrank) for hard bans
```

### 3.5 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Index | In-memory prefix / trie / FST | p99 | SQL `LIKE 'q%'` per keystroke |
| Hot path | Precomputed top-K prefixes | QPS | Full walk for `a`, `th`, `how` |
| Personalization | Re-rank candidates only | Latency | Per-user full index |
| Typos | Budgeted fuzzy after exact | CPU | Unbounded edit graph |
| Freshness | Batch + nearline deltas | Cost/latency | Rebuild whole index per query |
| Safety | Serve-time filter | Compliance | Train-only filtering |
| Serving | Shards by locale+prefix | Memory | One giant global trie |

### 3.6 Typo strategy

| Layer | Technique |
|-------|-----------|
| Normalize | NFKC, casefold, strip junk |
| Keyboard | Adjacent-key map light |
| SymSpell / delete-dict | 1-edit candidates for len≥3 |
| Blend | Merge fuzzy candidates into ranker with penalty |

**Budget:** fuzzy only if exact candidates < K or confidence low; cap candidate expansions (e.g. ≤32).

---


### 3.7 Ranking & personalization deal-breakers

| Anti-pattern | Why |
|--------------|-----|
| Personalization RPC fanout to 10 services | Blow p99 |
| Per-user rebuilt trie | Memory death |
| Typo graph unbounded | CPU death |
| Cache without blocklist epoch | Serve banned |

### 3.8 Edge vs origin split

```text
Edge: TLS, rate limit, hot prefix top-K, blocklist snapshot
Origin/shard: trie walk, fuzzy, blend, personalize re-rank
Client: debounce, min chars, session cache of last answers
```

---

## 4. Architecture Diagram

```text
  Clients (web/mobile)
           |
           v
  +--------+---------+     +------------------+
  | Edge / POP       |---->| Hot Prefix Cache |
  | TLS, rate limit  |     | (top prefixes)   |
  +--------+---------+     +---------+--------+
           |                         |
           v                         v
  +--------+---------+     miss    +-+----------------+
  | Suggest API      |-----------> | Prefix Shards    |
  | normalize, auth  |             | trie/FST in RAM  |
  +--+------+--------+             +--------+---------+
     |      |                               |
     |      +---- personalize re-rank <-----+ User Recents Cache
     |      +---- safety filter <-----------+ Blocklist
     v
  JSON suggestions (index_version)

  Async:
  Imp/Click → Kafka → Join → Learning store → Offline scorer → Index builder
                                      \→ Nearline spike → Hot cache deltas
```

**Suggest path:**

```text
q → normalize → truncate
 → if empty: trending
 → edge hot cache by (locale, prefix)
 → else route shard(locale, prefix)
 → exact candidates
 → optional fuzzy expand (budget)
 → merge + rank
 → personalize re-rank
 → safety filter
 → top-K return
```

**Index publish path:**

```text
builder writes artifact vN
 → canary servers
 → health (latency + quality probes)
 → fleet switch pointer
 → keep vN-1 for rollback
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Hard safety filter cannot be skipped** (including cache).  
2. **Stale OK over timeout** — return cached/partial with `degraded`.  
3. **Index versions atomic** per shard.  
4. **Logging never blocks** suggest ACK.  
5. **p99 budget enforced** with fuzzy/personalize caps.

#### 5.1.2 Failure modes

| Failure | Behavior |
|---------|----------|
| Shard down | Edge cache; replica; fewer suggestions |
| Personalization down | Global rank only |
| Blocklist store down | Fail closed on last-known in-memory snapshot |
| Bad nearline delta | Rollback deltas; core index remains |
| Viral query | Promote to hot cache immediately |

#### 5.1.3 Consistency

Derived data; eventual with logs. Serve local cell; replicate indexes async.

### 5.2 Scalability

#### 5.2.1 Sharding

```text
shard = f(locale, prefix_bucket(first 1–3 chars))
Hot locales get more replicas; cold locales pack denser
```

#### 5.2.2 Caching layers

| Layer | What | TTL |
|-------|------|-----|
| Client | Session prefixes | session |
| Edge | Hot (locale,prefix)→topK | 10–60s |
| Server LRU | Recent prefixes | seconds–minutes |
| Recents | per user | minutes |

Cached payloads embed `index_version` + `blocklist_epoch`.

#### 5.2.3 Trie / FST deep dive

```text
Trie walk: follow normalized chars; at node, return top-K heap / precomputed
FST: maps string → output score/id with shared structure; great for static dictionaries
Segmented arrays: sorted phrases + binary search prefix range → top by score
Hybrid: FST for membership + side table scores; or radix tree + posting lists

Build offline:
  aggregate phrases → score → sort → compress artifact → checksum → publish
Blue/green: servers mmap vN; flip pointer; keep vN-1 rollback
```

**Why not SQL:** `LIKE 'q%'` cannot hit 50ms p99 at 100K QPS with ranking.

#### 5.2.4 Ranking deep dive

```text
MVP score = w1*log(count+1) + w2*CTR + w3*recency + w4*personal - penalties
penalties: adult soft, clickbait, offensive soft (hard bans removed earlier)
Blending: exact candidates first; fuzzy with edit_penalty
Dedupe near-duplicates ("how to cook" vs "how to cook ")
```

#### 5.2.5 Personalization deep dive

```text
MVP: boost if suggestion ∈ user_recents (last N) or follows creator entity
Fetch recents: single cached get by user_id — budget 2–5ms
Do NOT: build personalized trie; do NOT call friend-graph fanout on path
Privacy: recents are sensitive — TTL, encryption, deletion API
```

#### 5.2.6 Typo tolerance deep dive

```text
Normalize → if exact candidates < K or weak scores:
  generate deletes/keyboard-adjacent (SymSpell-like) capped ≤32
  intersect dictionary / FST
  rank with edit distance penalty
Budget: abort fuzzy at 5–10ms
Min length: skip fuzzy for len < 3
```

#### 5.2.7 Edge cache deep dive

```text
Key: (locale, vertical, normalized_prefix, index_major, block_epoch)
Negative cache short TTL for empty rare prefixes (careful with scanning)
Invalidation: blocklist epoch++ → key space rotates (no stale bans)
Thundering herd: singleflight per prefix at edge
```

#### 5.2.8 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | Hot cache mandatory; trim; replicas |
| 100× | Edge suggest; nearline deltas |
| 1,000× | Geo cells; client hybrid; hierarchical top-K |

### 5.3 Maintainability

- Split: offline scoring / index format / online serve / safety  
- Schema-evolved index version header  
- Shadow ranking for model changes  
- Per-locale CTR dashboards  
- Rollback index pointer <5 minutes  

### 5.4 Learning loop

```text
impressions/clicks → Kafka (sampled) → aggregate → rescore phrases
Nearline spike detector: sudden query bursts → hot cache inject
Core index: batch hours; don’t rebuild per keystroke
```

### 5.5 Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| SQL LIKE online | In-mem prefix index |
| Uncached length-1 prefixes | Precompute hot |
| Unbounded fuzzy | Cap + budget |
| Per-user trie | Recents re-rank |
| Safety train-only | Serve-time filter |
| Sync click log | Async beacon |

---

## 6. Wrap-Up

### 6.1 Summary

Typeahead is a **latency-specialized read system**: precomputed hot prefixes + sharded in-memory prefix indexes, with offline/nearline learning and a non-bypassable safety filter. Personalization and typos are **budgeted features** on a small candidate set—not an excuse to explode fanout.

### 6.2 Key trade-offs

| Trade-off | Choice |
|-----------|--------|
| Freshness vs p99 | Batch core + nearline hot |
| Quality vs CPU | Cap fuzzy / candidates |
| Personalization vs privacy/latency | Recents boost only MVP |
| Memory vs coverage | Truncate long-tail phrases |

### 6.3 Deal-breakers

1. Warehouse/`LIKE` per keystroke.  
2. Uncached full trie walk for length-1 prefixes at peak.  
3. Personalization RPC fanout on critical path without caps.  
4. Safety only in training, not serve.  
5. Blocking client on click-log write.

### 6.4 Scale one-liner

Baseline in-mem shards → 10× hot cache → 100× edge+nearline → 1,000× geo cells + client hybrid.

---

## 7. Deeper / Related Interview Questions

### 7.1 Index structures

**Q1: Trie vs ternary search tree vs FST vs segmented arrays?**  
A: Tries intuitive for prefix; FSTs (finite state transducers) compress shared prefixes better for huge dictionaries—common in production suggest. Segmented postings also work. Pick one and discuss memory.

**Q2: Why not Elasticsearch completion suggester alone?**  
A: Can work at moderate scale; at Meta QPS you often want custom in-mem serving + edge. ES is fine to mention as building block with caching.

**Q3: How do you store top-K per node?**  
A: Each trie node may keep top-M completions; or store phrases in leaf postings and heap during walk. Hot prefixes materialize full top-K.

**Q4: How to bound memory?**  
A: Min count threshold; max phrase length; prune low-score tails; compress; shard.

**Q5: Incremental updates vs full rebuild?**  
A: Full rebuild for core scores daily/hourly; nearline deltas for spikes into hot cache / side map; periodic compact into core.

### 7.2 Ranking & learning

**Q6: What features for MVP score?**  
A: log-count, CTR, recency, length prior, safety prior, personal recents boost.

**Q7: How does CTR avoid cold-start bias?**  
A: Bayesian smoothing / explore impressions for new phrases; don’t require high CTR to show if count strong.

**Q8: Position bias in clicks?**  
A: Use propensity weighting or show randomization in experiments; for MVP accept bias with caution.

**Q9: Online learning per keystroke?**  
A: No—offline/nearline. Online only light boosts (recents, context).

**Q10: How to evaluate quality?**  
A: Offline NDCG on human/proxy labels; online CTR, reformulation rate, time-to-search.

### 7.3 Latency

**Q11: Walk the 50ms budget.**  
A: See §2.2; emphasize early exits and caps.

**Q12: What if fuzzy makes p99 blow up?**  
A: Disable fuzzy under load shed; only for len≥4; cap expansions; precompute common misspellings.

**Q13: Tail latency from GC?**  
A: Off-heap/mmap indexes; pooled buffers; language runtime GC tuning; copy-free responds where possible.

**Q14: Multi-get personalization + blocklist + trie — how many hops?**  
A: Collocate blocklist in process memory; recents from local cache; ideally ≤1 remote cache hop.

### 7.4 Personalization & privacy

**Q15: Recents on client vs server?**  
A: Client-side boost avoids RPC (great); server recents help multi-device. Hybrid common.

**Q16: Risk of leaking another user’s query?**  
A: Never suggest rare queries below aggregation threshold k-anonymity; hash/tokenize PII detectors.

**Q17: Friend-aware people typeahead?**  
A: Separate vertical: graph retrieval candidates → rank; don’t stuff into query trie. Isolate latency.

**Q18: GDPR deletion?**  
A: Recents delete ASAP; aggregated counts generally non-personal; document retention.

### 7.5 Safety

**Q19: Where is blocklist enforced?**  
A: Serve path after rank, and ideally at index build. Cache entries must invalidate on blocklist epoch change.

**Q20: Adversarial prefixes?**  
A: Homoglyph normalize; rate limit; don’t autocomplete disallowed even if popular.

**Q21: Soft vs hard bans?**  
A: Hard remove; soft demote. Legal/harm = hard.

**Q22: How fast can you purge a bad suggestion?**  
A: Blocklist push to memory within seconds; edge cache TTL/epoch bust; don’t wait for full rebuild.

### 7.6 Scale & ops

**Q23: Hot shard imbalance (`en` + `t`)?**  
A: Split hot prefix ranges; more replicas; precompute heaviest prefixes.

**Q24: Multi-region active-active?**  
A: Serve local; replicate index artifacts; accept brief version skew.

**Q25: Canary a bad model?**  
A: Shadow traffic; % canary; auto-rollback on CTR/latency/safety alerts.

**Q26: Cost knob first under brownout?**  
A: Disable fuzzy → shorten K → disable personalization → serve trending only.

**Q27: 100M QPS believable?**  
A: Only with edge mega-cache + client coalescing; origin tiny fraction.

### 7.7 Typos & i18n

**Q28: CJK autocomplete differences?**  
A: Character/segment tokenization; pinyin/romanization layers optional; don’t assume space-delimited words.

**Q29: RTL languages?**  
A: Normalize carefully; UI concern mostly; index still prefix on normalized logical string.

**Q30: Emoji queries?**  
A: Policy allowlist or strip; prevent emoji-only spam suggest.

### 7.8 Alternatives & craft

**Q31: Only Redis ZSET per prefix?**  
A: Works small/medium; memory and update complexity explode at huge cardinality—OK for hot layer.

**Q32: Only LLM?**  
A: Too slow/expensive/unreliable for exclusive per-keystroke MVP; can re-rank tiny sets Phase 2.

**Q33: How to open interview?**  
A: Clarify verticals, K, latency, typos, personalization, safety—then latency budget + hot prefixes.

**Q34: What impresses?**  
A: Budget math, hot-prefix stats, safety epoch, progressive scale, clear deal-breakers.

**Q35: Common mistake?**  
A: Fancy ML diagram with no p99 plan; or forgetting safety on cached paths.

**Q36: End strong?**  
A: Restate: exact path + budgeted fuzzy; cache layers; atomic index versions; kill switches.

**Q37: How do empty-prefix trending and typeahead interact?**  
A: Separate curated/aggregated list; same safety; don’t run trie on empty.

**Q38: Should suggestions include rich entities (thumbnails)?**  
A: Optional fields; watch payload size on mobile; lazy enrich after text suggest.

**Q39: Dedup near-identical suggestions?**  
A: Normalize edit distance / stemming light; keep diversity penalty in ranker.

**Q40: Rate limiting strategy?**  
A: Per user/IP/device token buckets; bot scores; protect shards before edge saturates.

**Q41: Index compression tricks?**  
A: Front-coding, integer score quantize, FST, mmap, dictionary encoding of tokens.

**Q42: Why Meta specifically?**  
A: Multi-vertical typeahead (query/people/groups), multilingual, safety bar, insane fanout QPS from apps.

---


### 7.9 Extra deep-dive Q&As

**Q43: FST vs trie in one sentence?**  
A: FST is a compressed automaton mapping keys to outputs with maximal prefix/suffix sharing — ideal for static suggest dictionaries; tries are simpler to explain and mutate.

**Q44: How do you personalize without leaking cross-user data in caches?**  
A: Never put user_id in shared edge keys for personalized lists. Edge stores global top-K; personalize re-rank at origin/API with per-user recents cache.

**Q45: What happens when blocklist updates?**  
A: Bump block_epoch; edge keys change; in-memory filter updated; old cached payloads become unaddressable. Fail closed.

**Q46: Why debounce on client?**  
A: Cuts QPS from every keystroke to every 20–50ms; improves p99 and cost without hurting UX.

**Q47: Multilingual romanization?**  
A: Separate locale indexes; optional transliteration layer producing alternate prefixes — carefully budgeted, not unbounded fanout.

**Q48: 10×/100×/1,000× pitch?**  
A: Hot cache → edge+nearline → geo cells + client hybrid. Always: in-mem prefix index + serve-time safety.

---

### Appendix A — Normalized query pipeline

```text
1. UTF-8 validate
2. NFKC
3. Casefold (locale-aware where needed)
4. Collapse whitespace
5. Strip control chars
6. Map confusables (optional)
7. Truncate length
8. Reject empty after normalize (except zero-query path)
```

### Appendix B — Hot prefix materialization

```text
for locale in locales:
  for prefix in top_prefixes_by_qps:
    candidates = trie.completions(prefix, limit=M)
    ranked = rank(candidates)[:K]
    hot.put((locale, prefix), ranked, version)
```

### Appendix C — Suggest pseudocode

```text
def suggest(q, locale, user, limit):
  qn = normalize(q)
  if qn == "": return trending(locale)
  if hit := edge.get(locale, qn):
    return safety(personalize(hit, user))
  cands = shard(locale, qn).exact(qn, M)
  if len(cands) < limit and len(qn) >= 3:
    cands += shard.fuzzy(qn, budget=32)
  ranked = rank(cands)[:max(limit*3, 30)]
  ranked = personalize(ranked, user)
  return safety(ranked)[:limit]
```

### Appendix D — Safety filter

```text
def safety(items, block_epoch):
  out = []
  for it in items:
    if blocklist.hard_match(it.text): continue
    if toxicity_score(it) > T: continue  # optional model
    out.append(it)
  return out
```

### Appendix E — Latency SLO burn

| Condition | Action |
|-----------|--------|
| p99 > 40ms warn | disable fuzzy |
| p99 > 50ms | serve hot-only for len≤2 |
| error rate > 1% | fail to edge stale |
| safety store fail | use last snapshot fail-closed |

### Appendix F — Index artifact layout

```text
manifest.json
  locale, shard_id, version, checksum, created_at
shard_en_US_00.fst
shard_en_US_00.scores
blocklist_epoch.txt
```

### Appendix G — Nearline spike detector

```text
window = 5m counts per phrase
if zscore(count) > Z and not blocked:
  promote to hot cache with provisional score
  expire promotion after T unless confirmed by batch
```

### Appendix H — Sharding map

| Locale | Prefix | Shard |
|--------|--------|-------|
| en_US | a–m | 0–7 |
| en_US | n–z | 8–15 |
| en_US | hot `th`,`how` | dedicated replicas |
| ja_JP | … | separate cell |

### Appendix I — NFR card

```text
p99 < 50ms in-region
99.99% availability (stale OK)
Hot prefixes precomputed
Safety non-bypassable
Personalization = re-rank only
Logs async
Atomic index versions
```

### Appendix J — Progressive scale

| Scale | Serve | Learn | Cache |
|-------|-------|-------|-------|
| Base | RAM shards | Daily batch | Server LRU |
| 10× | +replicas | +hourly | Edge hot |
| 100× | Edge POP | Nearline | Mega hot |
| 1,000× | Geo cells | Continuous | Client+edge |

### Appendix K — Comparison table

| Approach | Latency | Memory | Freshness | Verdict |
|----------|---------|--------|-----------|---------|
| SQL LIKE | Poor | DB | Good | Reject |
| ES completion | Medium | Medium | Medium | OK mid |
| Custom FST+edge | Excellent | High RAM | Batch+delta | **Choose** |
| LLM only | Poor/$ | GPU | Good semantic | Reject sole |

### Appendix L — Personalization blend

```text
final = global_score * (1 + α * recent_hit + β * locale_match)
α small (e.g. 0.1–0.3) to avoid hijacking
```

### Appendix M — Client behavior

```text
debounce 20–50ms
cancel in-flight on new keystroke
cache last results per prefix
min chars = 0 for trending, 1+ for suggest
```

### Appendix N — Metrics

| Metric | Use |
|--------|-----|
| suggest_p99_ms | SLO |
| cache_hit_ratio | Scale health |
| empty_result_rate | Coverage |
| filtered_safety_rate | Policy |
| ctr_at_k | Quality |
| index_age_seconds | Freshness |

### Appendix O — Rollback

```text
pointer.current = vN
alert quality drop
pointer.current = vN-1
edge epoch bump to flush bad hot entries
```

### Appendix P — People tab sketch (optional)

```text
q → friends index + global entities retrieval → rank by affinity
timeout 20ms → return query-tab only
never block query tab on people fanout
```

### Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Typeahead | Suggestions while typing |
| Hot prefix | High-QPS prefix with materialized top-K |
| Nearline | Minutes-scale update path |
| FST | Compressed automaton index |
| Block epoch | Version of safety data |

### Appendix R — Worked QPS example

```text
Peak 1M suggest/s
85% edge hot hit → 150K to origin suggest layer
10 shards × 15K/s each — plan headroom 3–5×
Fuzzy on 10% of origin → 15K fuzzy/s CPU-heavy — cap
```

### Appendix S — 30m checklist

1. Clarify K, latency, verticals, safety, typos.  
2. Latency budget.  
3. Hot prefix + shard diagram.  
4. Offline/nearline.  
5. Failure/degrade.  
6. 10×/100×/1000×.  
7. Deal-breakers.

### Appendix T — Sample score worksheet

```text
phrase count=1e5 → log=11.5
CTR=0.08
recency=0.7
score = 0.5*11.5 + 0.3*8 + 0.2*7 = 5.75+2.4+1.4 = 9.55
recent hit → *1.2 = 11.46
```

### Appendix U — API errors

| Code | Meaning |
|------|---------|
| 200 | OK (maybe empty list) |
| 400 | q too long / bad locale |
| 429 | rate limited |
| 503 | degraded empty / retry |

### Appendix V — Why not compute top-K from logs online

```text
Scanning 100M phrases per keystroke impossible
Even approx heavy-hitters online per prefix without structure won't hit 50ms at 1M QPS
Preaggregation + index is the point of the product
```

### Appendix W — Prefix length policy

| Prefix len | Behavior |
|------------|----------|
| 0 | Trending / zero-query only |
| 1 | Hot table only; hard CPU cap; max K |
| 2–3 | Hot preferred; limited trie |
| 4+ | Full exact + optional fuzzy |
| >128 | Reject 400 |

### Appendix X — Index build DAG

```text
logs (Kafka/HDFS)
  → daily aggregate (phrase, locale, count, clicks)
  → join safety priors
  → score
  → threshold filter
  → shard split by locale+prefix
  → FST/trie compile
  → upload artifacts
  → canary → fleet switch
```

### Appendix Y — Cache key design

```text
edge_key = hash(locale + "|" + normalized_prefix + "|" + vertical + "|" + index_major + "|" + block_epoch)
Include block_epoch so safety purges bust caches without waiting TTL alone
```

### Appendix Z — Load-shed ladder

```text
L0 normal
L1 disable fuzzy
L2 disable personalization
L3 serve hot prefixes only (len<=3), empty otherwise with degraded=true
L4 trending-only mode
L5 fail closed 503 with Retry-After
```

### Appendix AA — Multilingual pitfalls

| Issue | Mitigation |
|-------|------------|
| Turkish i/İ | Locale-aware casefold |
| Accent folding | Optional per locale |
| CJK no spaces | Char n-grams / segmenter |
| Mixed script | Detect; route locale; prevent homoglyph spoof |

### Appendix AB — Experimentation hooks

```text
suggest response may include:
  exp_ids: ["ranker_v3", "fuzzy_b"]
logging joins impressions to exp_ids for CTR analysis
never fork safety path in experiments without review
```

### Appendix AC — Capacity worksheet (10×)

```text
Peak 1M QPS, 85% edge hit → 150K origin
Assume 1 core handles 5K exact suggests/s
Need ~30 cores active + 3× headroom ≈ 90 cores origin
Fuzzy 10% at 5× cost → add ~30 cores
Personalization redis: 150K gets/s with local cache 90% → 15K/s
```

### Appendix AD — Failure injection tests

1. Kill shard mid-request → partial/cached.  
2. Blocklist epoch bump → old cache not serving banned.  
3. Nearline bad promote → rollback.  
4. Artificial 100ms fuzzy delay → load-shed L1 triggers.  
5. Personalization 100% error → global fallback.

### Appendix AE — Related Meta surfaces

| Surface | Twist |
|---------|-------|
| Facebook search box | People + posts verticals |
| Instagram | Accounts/hashtags/audio |
| Workplace | Org-scoped suggest |
| Ads query tools | Different safety |

Same architecture skeleton; different indexes and authZ.

### Appendix AF — Final interview card

```text
p99 < 50ms
hot prefixes
sharded FST/trie
offline + nearline
safety epoch on all paths
personalize = re-rank
fuzzy budgeted
10×→edge 100×→cells 1000×→client hybrid
```

---

*End of Search Autocomplete / Typeahead system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Change | Why |
|------|--------|-----|
| →10× | Hot prefix materialization; replicas | Head QPS |
| →100× | Edge suggest; nearline spike deltas | Latency + freshness |
| →1,000× | Geo cells; client hybrid; succinct indexes | Memory + RTT |

### 8.2 Suggest path card

```text
normalize → edge hot cache → shard trie/FST
  → optional fuzzy (budgeted) → rank → personalize re-rank
  → safety filter → top-K
Empty q → trending
Logging async only
```

### 8.3 Index structure card

```text
Offline scored phrases → compressed prefix index (trie/FST/segments)
Hot prefixes: precomputed top-K lists
Atomic version flip; keep previous for rollback
SQL LIKE is not a serve strategy
```

### 8.4 Typo + personalization budgets

```text
Fuzzy ≤32 cands, ≤5–10ms, min len 3, skip if exact strong
Personalize: recents boost only (MVP), one cache get, no per-user trie
```

### 8.5 Anti-patterns

1. Warehouse/SQL per keystroke  
2. Uncached length-1 full walks at peak  
3. Unbounded edit-distance graphs  
4. Personalized full indexes  
5. Safety only in training  
6. Blocking on click-log ACK

### 8.6 Hot prefix materialization rule

```text
Track prefix QPS offline
If prefix in top P by traffic OR length ≤ 2 in major locales:
  materialize top-K list into edge/Redis
Rebuild with index version; atomic swap
Tail prefixes: live trie walk on shards
```

### 8.7 Safety filter order

```text
1) hard blocklist / regex (remove)
2) rank remaining
3) soft downrank penalties already in score
Never: cache hit bypasses step 1
People-tab entities: separate allowlists / abuse queues
```

### 8.8 Client UX coupling

```text
Debounce 20–50ms; min 1–2 chars (locale-dependent)
Cancel in-flight on new keystroke (sequence numbers)
Show last good suggestions if degraded
Don’t block navigation on log beacon
```

### 8.9 Nearline spike detector

```text
Windowed count of raw queries by normalized phrase
If z-score high and not blocked: inject into hot cache / side channel
Expire spike entries quickly; core batch index remains source of truth
Protects breaking-news freshness without full rebuild
```

### 8.10 Latency shed ladder

```text
1) skip personalize
2) skip fuzzy
3) return edge stale top-K
4) return trending fallback
Always keep safety filter
```

<!-- deepened in-place: BOTE + nested §5 + §7 Q&A + §8 study card -->

### 8.x Quick recall

Preserve cache-first / budgeted paths; escalate with progressive tables above.

