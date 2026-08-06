# System Design: Search Autocomplete / Word Prediction

> **Focus areas:** Trie / prefix indexes · Ranking · Personalization · Typo tolerance · Hot prefixes · p99 < 50ms · Offline→online serving  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit latency budget, hot-prefix caching, deal-breakers for “query OLAP on each keystroke” fantasies  
> **Interview theme:** Classic Google L5+ suggest service — ultra-low latency reads, ranking freshness vs safety, personalization without blowing p99

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

Goal: **bound the product**—a **typeahead / autocomplete** service that returns top suggestions as the user types, with ranking, light personalization, typo tolerance, and strict latency (<50ms p99), at Google search scale thinking.

### 1.0 What this is / is not

| Dimension | **Autocomplete / word prediction (this doc)** | Not this |
|-----------|-----------------------------------------------|----------|
| Primary job | Prefix → top-K query suggestions fast | Full web search ranking / SERP |
| Success | Relevant suggestions; p99 < 50ms | Perfect semantic understanding MVP |
| Index | Prefix structures + scores | Live scan of all queries each keystroke |
| Personalization | Soft re-rank of candidates | Fully private model per user at 1M QPS without cache |
| Typos | Edit-distance / fuzzy within budget | Unlimited fuzzy graph search |

**Scope statement:** Design search autocomplete / word prediction: trie/prefix serving, ranking, personalization hooks, typo tolerance, hot-prefix optimization, latency <50ms—with progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Suggest what? | Full queries / phrases (not only next word) | Phrase trie or n-gram + completion |
| F2 | Top-K? | 8–10 UI; compute ~20–50 candidates | Truncate after rank |
| F3 | Ranking signal? | Popularity, freshness, CTR, contextual | Offline score + online boosts |
| F4 | Personalization? | Recent searches + locale; deep ML later | Client/recents + user profile light |
| F5 | Typos? | Yes for len≥3 within 1 edit common | Fuzzy layer / BK-tree / symspell |
| F6 | Languages? | Multi-locale indexes | Partition by locale |
| F7 | Safety? | Block NSFW / illegal / PII leaks | Policy filter before return |
| F8 | Freshness? | New viral queries in minutes–hours | Nearline updater + online cache |
| F9 | Exact prefix only? | Prefix primary; segment / word-boundary OK | Trie + normalized form |
| F10 | Empty prefix? | Trending / zero-query suggestions | Separate trending list |
| F11 | Analytics? | Impression/click logs for learning | Logging pipeline |
| F12 | Client predict? | Optional on-device for first chars | Hybrid edge |

**MVP functional scope:**

1. `GET /suggest?q=&locale=&limit=` → ranked suggestions.  
2. Offline build of prefix index from query logs + scores.  
3. Online serve from memory/trie shards with hot-prefix cache.  
4. Basic typo: normalize + fuzzy for common misspellings.  
5. Personalization: boost user’s recent queries + locale.  
6. Safety filter / blocklist.  
7. Logging impressions/clicks asynchronously.  
8. Nearline update path for spike queries (hours→minutes).

**Out of MVP:**

- Full semantic vector suggest as sole path (hooks OK)  
- Complete next-token LLM decoding online for every keystroke  
- Perfect personalization with heavy user model at p99<50ms without candidate restriction  
- Cross-script transliteration beyond simple normalize (Phase 1.5)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Feels instant per keystroke | **p99 < 50ms** end-to-end suggest |
| N2 | Availability | Search box critical | 99.99% with stale index OK |
| N3 | Throughput | Huge read QPS | Millions QPS at scale via cache |
| N4 | Index freshness | New terms appear reasonably soon | Minutes–hours MVP |
| N5 | Consistency | Suggestions may lag logs | Eventual OK |
| N6 | Cost | Memory-heavy serving | Shard + prefix compression |
| N7 | Privacy | Don’t leak others’ PII queries | Aggregation thresholds |
| N8 | Safety | No banned suggestions | Filter enshrined in serve path |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User types `how to b` → suggestions `how to boil eggs`, … in <50ms.  
2. User typed `facebok` → fuzzy → `facebook`.  
3. User’s recent `flights to tokyo` boosted when typing `fli`.  
4. Viral meme query appears within ~15–60 min via nearline.  
5. Empty query → trending for locale.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Prefix length 1 (`a`) | Serve only heavily cached head; limit work |
| Hot prefix `how` | Precomputed top-K; no trie walk fanout |
| Unicode / accents | NFKC + casefold; locale rules |
| Emoji queries | Allowlist or strip policy |
| Banned term | Filtered; may show sanitized alternatives |
| Shard timeout | Return partial / cached; never 5s wait |
| Personalization store down | Fall back to global rank |
| Click log delay | Ranking lag; OK |
| Very long query | Cap input length (e.g. 100 chars) |
| Bot scrape | Rate limit; CAPTCHA rare |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Suggest QPS (peak) | 100K | 1M | 10M | 100M |
| Unique prefixes/day | 50M | 500M | 5B | 50B |
| Phrases in index | 100M | 1B | 10B | 100B |
| Locales | 20 | 50 | 100 | 200+ |
| Avg suggestion compute | 20 cand | 20 | 30 | hierarchical |
| Hot prefixes cached | 1M | 10M | 100M | edge mega-cache |
| Index memory / cell | 50GB | 200GB | TB-class fleets | geo cells |
| Rebuild time | hours | hours | incremental | continuous |

**What each jump forces:**

- **10×:** Mandatory hot-prefix cache; shard by locale+prefix; trim trie.  
- **100×:** Edge/POP suggest; personalization as re-rank only; nearline deltas.  
- **1,000×:** Client+edge hybrid; hierarchical language cells; approx top-K structures.

### 1.5 Etc. (Constraints & Assumptions)

- Upstream **search query logs** exist (we don’t design full crawl).  
- Ambiguity: autocomplete of **queries** vs **documents/titles**—lock queries MVP.  
- Latency budget includes network within region; client RTT separate.  
- Ranking quality measured offline (NDCG/CTR) + online experiments.

**Scope statement to repeat back:**

> Design a search autocomplete service that serves top-K prefix suggestions under p99 < 50ms using sharded in-memory prefix indexes, offline+nearline ranking, hot-prefix caches, light personalization and typo tolerance, with safety filters—and scales through edge caching and hierarchical sharding.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Suggest reads** | Per keystroke | 100K QPS | 1M | Edge + suggest servers |
| **Hot cache hits** | Head prefixes | 70–90% | higher | Edge/Redis |
| **Trie/miss computes** | Tail prefixes | 10–30K QPS | 100K+ | In-mem shards |
| **Personalization lookups** | User recents | subset | | User profile store |
| **Logging** | impress/click | ~read QPS | | Async bus |
| **Index build** | Offline | batch | | Dataflow |
| **Nearline upsert** | Viral | low | | Delta appliers |

**Anti-pattern:** mixing log-ingest QPS with suggest QPS in one number.

### 2.2 Latency budget (critical)

```text
Budget p99 = 50ms (service-side in-region)
  - network LB → pod: ~1–2ms
  - auth/rate limit: ~1ms
  - hot cache lookup: ~1–3ms
  - shard RPC (if miss): ~5–10ms
  - trie + rank: ~5–15ms
  - personalize re-rank: ~3–5ms
  - safety filter: ~1ms
  - serialize: ~1ms
Sum must fit; personalization CANNOT do heavy RPCs on miss path without parallel budget
```

### 2.3 Memory math

```text
Naive: 100M phrases × 40B avg string = 4GB strings
+ trie pointers overhead 3–10× → tens of GB
With RADIX/succinct trie + score: still large → shard by locale + first chars
Compressed front coding helps sequential prefixes
```

### 2.4 Keystroke amplification

```text
User query avg 15 chars → ~15 suggest calls (debounced to ~5–8 if client smart)
100K QPS suggests ≈ ~10–20K active typers / sec order-of-magnitude (rough)
Debounce 30–50ms client-side reduces load significantly — mention in interview
```

### 2.5 Hot prefix concentration

```text
Top 1% prefixes may serve 50%+ traffic ("how", "face", "yout"...)
Precompute top-K for all prefixes with QPS > threshold
This is THE scalability lever alongside edge TTL
```

### 2.6 Offline training volume

```text
Query logs 10B/day → aggregate to phrase counts
Store only phrases with count ≥ threshold (privacy + noise)
e.g. ≥50 globally or ≥10 in locale over 7–28d window
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/suggest?q=&locale=&limit=&device=` | `{suggestions:[{text, score, source}]}` |
| `GET /v1/suggest/zero` | Trending / zero-query |
| `POST /internal/index/delta` | Nearline upsert phrases |
| `POST /v1/log/impressions` | Client beacons (or server-side log) |
| `GET /v1/health` | Index version / age |

**Response schema:**

```text
SuggestResponse {
  q_normalized,
  index_version,
  latency_ms,
  suggestions: [
    {text, score, type: "global"|"personal"|"fuzzy"|"trending"}
  ]
}
```

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| Phrase score | `(locale, phrase)` | popularity, CTR, freshness |
| Prefix top-K | `(locale, prefix)` | precomputed list |
| Trie shard | `(locale, shard)` | compressed prefix tree |
| Blocklist | `phrase/pattern` | policy |
| User recents | `user_id` | last N queries |
| Index version | `locale` | epoch / generation |

### 3.3 Index structures — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **In-memory trie** | Fast prefix walk | Memory; update hard | Classic MVP serve |
| **Ternary search tree** | Balanced-ish | Complex | Alternative |
| **Sorted array + binary search** | Compact; good cache | Harder fuzzy | Strong at scale |
| **Finite state transducer (FST)** | Very compact (Lucene) | Build cost | **Strong production pick** |
| **Redis ZSET per prefix** | Simple | Huge key count | Small corpus only |
| **SQL `LIKE 'pre%'`** | Easy | Latency/deal-breaker | Never at Google scale |

**Chosen MVP:**

1. Offline build **FST or radix trie** per locale shard.  
2. Each terminal holds top completions or pointer to postings.  
3. **Precomputed top-K** for hot prefixes.  
4. Online: cache → shard trie → merge → re-rank → filter.

**Deal-breaker:** `SELECT ... WHERE query LIKE 'prefix%'` on each keystroke at 100K QPS.

### 3.4 Ranking — Why X over Y

| Signal | Role |
|--------|------|
| Popularity (count, unique users) | Base |
| CTR of suggestion | Quality |
| Freshness / velocity | News/viral |
| Length / specificity | Prefer useful completions |
| Context (time, device, geo) | Light boost |
| Personal recents / frequent | Re-rank |
| Safety score | Hard filter |

```text
score = pop^α * ctr^β * freshness^γ * context_boost * personal_boost
MVP: offline static score; online * personal_boost * freshness_bit
```

### 3.5 Typo tolerance — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Normalize only** | Free | Misses typos | Always |
| **SymSpell / delete dict** | Fast 1-edit | Memory | **MVP fuzzy** |
| **BK-tree** | Flexible distance | Slower | Secondary |
| **Keyboard distance** | Mobile typos | Complexity | Phase 1.5 |
| **Neural spell** | Quality | Latency | Offline candidate gen |

**Chosen:** normalize + SymSpell candidate generation capped (e.g. 3 variants) then prefix lookup; skip fuzzy for len<3 or when exact has enough results.

### 3.6 Personalization strategy

```text
Candidate gen (global, cacheable) → top C (e.g. 50)
Fetch user recents (parallel, budget 5ms, soft fail)
Re-rank: boost prefix-matching recents; demote seen-dismissed
Return top K
```

**Deal-breaker:** blocking on cold user-profile RPC that takes 40ms alone.

### 3.7 Why X over Y (summary table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Serve store | In-mem FST/trie shards | <50ms | Per-request OLAP |
| Hot prefixes | Precomputed top-K | QPS concentration | Full trie walk for `a`/`the` |
| Personalization | Re-rank only | Latency | Candidate gen from full user corpus online |
| Typos | Capped fuzzy | Budget | Unbounded edit graph |
| Updates | Offline + nearline delta | Freshness | Full rebuild every minute globally |
| Safety | Last-mile filter | Compliance | Filter only in offline build (stale holes) |

---

## 4. Architecture Diagram

```text
  Clients (debounce) ---> Edge / CDN / POP suggest cache (hot prefixes)
                              |
                              v
                      +-------+--------+
                      | Suggest API    |  rate limit, normalize
                      +-------+--------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
       +------------+  +------------+  +--------------+
       | Hot Prefix |  | Trie Shard |  | User Recents |
       | Cache      |  | Servers    |  | (soft)       |
       +------------+  +------+-----+  +--------------+
                              ^
                              | load index
                              |
       +----------------------+----------------------+
       | Offline Builder (logs → scores → FST)       |
       | Nearline Delta Applier (viral / news)       |
       | Safety / Blocklist Service                  |
       +---------------------------------------------+
                              ^
                              |
                       Query logs / clicks
```

**Request path:**

```text
q raw -> NFKC/casefold/truncate
-> if |q|==0: trending
-> if hot_cache hit: candidates
-> else: route shard(locale, prefix) -> trie.top(q, C)
-> optional fuzzy variants if |candidates|<K
-> parallel user recents
-> rank merge
-> safety filter
-> return K + log impression async
```

**Offline path:**

```text
Query logs (7–28d)
  -> aggregate counts / CTR
  -> threshold filter (privacy)
  -> score phrases
  -> build FST/trie per locale shard
  -> publish index version to GCS
  -> Suggest servers blue/green reload
```

**Nearline path:**

```text
Spike detector (velocity)
  -> promote phrase into delta store
  -> applier patches hot-prefix lists / side hash map
  -> next full build absorbs
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Serve never blocks on logging.**  
2. **Safety filter always applied** on response path.  
3. **Index version exposed**; can pin/rollback.  
4. **p99 latency SLO** with load shedding (shorter K, skip fuzzy/personal).  
5. **Privacy threshold:** rare queries never suggested if below aggregate threshold.

#### 5.1.2 Degradation ladder

```text
1) Skip personalization
2) Skip fuzzy
3) Serve hot-cache only / shorter K
4) Return stale trending
Never: hang waiting for all shards
```

#### 5.1.3 Index reload

| Strategy | Notes |
|----------|-------|
| Blue/green | New version load → atomic swap pointer |
| Memory double | Need headroom |
| Mmap FST | Faster reload; OS page cache |
| Delta side map | Small viral overlays |

#### 5.1.4 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Single shard hot | Split by prefix ranges |
| 10× | Cache stampede | Request coalescing; stale-while-revalidate |
| 100× | Cross-AZ latency | Sticky regional serve |
| 1,000× | Global fanout | POP-local indexes |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| `locale` | Language/culture corpora |
| `prefix range` (first 1–2 chars) | Shard trie |
| User recents by `user_id` | Personalization store |
| Logs by time | Batch jobs |

**Routing:**

```text
shard = hash(locale + prefix[:2]) % N   // or range-based for locality
careful: uneven unicode; use frequency-aware shard bounds
```

#### 5.2.2 Hot prefix precompute

```text
for each prefix with traffic > T:
  store topK(prefix) in Redis/edge
TTL minutes; invalidate on delta
For prefix len ≤ 2: ALWAYS precompute (fanout otherwise huge)
```

#### 5.2.3 Compression & memory

- Front coding / radix compression.  
- FST (Lucene-like) common industry answer.  
- Store phrase IDs + dictionary.  
- Quantize scores to 8–16 bits.

#### 5.2.4 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Hot cache; FST; shard; debounce guidance |
| →100× | Edge POP indexes; nearline deltas; degrade ladder |
| →1,000× | On-device head + edge; hierarchical locale cells; vector hybrid Phase 2 |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
limit_default: 8
candidate_C: 40
fuzzy_max_edits: 1
fuzzy_min_len: 3
hot_prefix_qps_threshold: 50
privacy_min_count: 50
p99_budget_ms: 50
personalization_timeout_ms: 5
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `suggest_latency_ms` | SLO |
| `cache_hit_rate` | Scale health |
| `fuzzy_attach_rate` | Cost/quality |
| `personalization_timeouts` | Budget |
| `safety_filtered` | Policy |
| `index_age_seconds` | Freshness |
| `ctr_by_position` | Ranking |

#### 5.3.3 Testing & eval

- Golden prefix → expected suggestions.  
- Latency soak with production prefix distro.  
- Adversarial banned terms.  
- Offline NDCG on holdout sessions.  
- Chaos: kill personalization store.

#### 5.3.4 Operability

- Shadow ranker `score_v2`.  
- Index canary by locale %.  
- Instant blocklist push (side channel).

---

## 6. Wrap-Up

### 6.1 What we designed

A **search autocomplete** system that builds locale-sharded in-memory prefix indexes (FST/trie), serves via hot-prefix caches under a **50ms p99** budget, applies capped fuzzy matching and soft personalization re-ranking, filters unsafe content, and updates via offline builds plus nearline deltas—not SQL LIKE and not an LLM per keystroke.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Structure | FST/trie in memory |
| Hot prefixes | Precompute mandatory |
| Personalization | Re-rank with timeout |
| Fuzzy | Capped, len-gated |
| Freshness | Offline + nearline |
| Safety | Online filter |

### 6.3 30-second scale narrative

> Baseline: offline FST per locale shard, Redis hot prefixes, soft personalization. 10× leans harder into cache and short-prefix precompute. 100× pushes indexes to edge POPs with degrade ladders. 1,000× adds on-device heads and cell-local corpora—latency budget always drives architecture.

### 6.4 Deal-breakers checklist

- OLAP/SQL LIKE per keystroke.  
- Unbounded fuzzy search.  
- Heavy personalization RPC on critical path.  
- No hot-prefix strategy for len≤2.  
- Safety only offline.  
- Blocking on click logging.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Autocomplete vs search?**  
A: Autocomplete suggests queries; search retrieves documents. Different indexes and SLOs.

**Q2: Word prediction vs phrase completion?**  
A: Word = next token; phrase = full query. Product usually wants phrases.

**Q3: How many suggestions?**  
A: UI 8–10; compute more candidates for re-rank.

**Q4: Mobile vs desktop?**  
A: Different ranking; mobile more typo-prone; tighter latency.

**Q5: Zero-query?**  
A: Trending / contextual (time of day, location coarse).

### 7.2 Algorithms & data structures

**Q6: Explain trie for autocomplete.**  
A: Path = prefix; node stores top completions or children; walk to node; collect top-K.

**Q7: Why FST?**  
A: Compact representation of sorted dictionary with shared prefixes/suffixes; fast lookup.

**Q8: How to store top-K at each node?**  
A: Precompute offline; or beam search online with child heaps—precompute for hot.

**Q9: SymSpell idea?**  
A: Pre-delete dictionary; generate deletes of query; lookup candidates at edit distance 1 cheaply.

**Q10: How does Lucene suggest?**  
A: Often FST-based analyzers; good reference architecture.

**Q11: Beam search on trie?**  
A: Expand most promising nodes by score bound; keep beam width W.

**Q12: Approximate top-K?**  
A: OK if displayed quality high; exactness not required.

### 7.3 Ranking

**Q13: Popularity alone?**  
A: Biases short head queries; need CTR and usefulness.

**Q14: Freshness?**  
A: Time-decay counts; velocity boost for news.

**Q15: Position bias in CTR?**  
A: Use click models / randomized exploration carefully.

**Q16: Online learning?**  
A: Bandits on candidates Phase 2; keep MVP offline scores.

### 7.4 Personalization & privacy

**Q17: What personal data?**  
A: Recents, frequent, locale, coarse geo—not full browsing history MVP.

**Q18: Privacy threshold?**  
A: Don’t suggest queries that only one user typed (aggregation).

**Q19: Cross-device?**  
A: Account-linked recents with sync delay OK.

**Q20: Latency conflict?**  
A: Budget + soft fail; never miss SLO for +2% CTR.

### 7.5 Typos & i18n

**Q21: CJK?**  
A: Character n-grams / segmenter; separate analyzers per locale.

**Q22: Transliteration?**  
A: Phase 1.5; expensive online.

**Q23: When to skip fuzzy?**  
A: Short prefixes; enough exact results; CPU shed.

### 7.6 Distributed systems

**Q24: Shard strategy?**  
A: Locale + prefix range; avoid hot first-letter shards by frequency-aware splits.

**Q25: Multi-region?**  
A: Replicate indexes; local serve; build centrally or per region.

**Q26: Cache invalidation?**  
A: Versioned keys; short TTL; delta bump version.

**Q27: Thundering herd on viral?**  
A: Coalesce singleflight; pre-warm hot list.

### 7.7 Safety & abuse

**Q28: How do bad suggestions appear?**  
A: Spam query floods → need trust, thresholds, demotion.

**Q29: Blocklist ops?**  
A: Side channel push with immediate serve filter.

**Q30: Legal takedowns?**  
A: Same as blocklist with audit.

### 7.8 Estimation drills

**Q31: Memory for 1B phrases?**  
A: Naive tens of TB; with FST/sharding/thresholding much less; still cell fleets.

**Q32: Why p99 50ms hard?**  
A: Keystroke UX; multi-hop kills; forces in-mem + cache.

**Q33: Cache hit target?**  
A: Aim ≥80% at edge for mature systems.

### 7.9 Alternatives & deal-breakers

**Q34: LLM next-token for all?**  
A: Quality tempting; cost/latency/deal-breaker at 10M QPS; maybe hybrid for long tail.

**Q35: Elasticsearch completion suggester only?**  
A: Valid building block; still need hot cache, personalization, safety, scale story.

**Q36: Client-only trie?**  
A: Good for tiny head; can’t hold global corpus.

### 7.10 Interview craft

**Q37: How to open?**  
A: Clarify suggest type, K, latency, locales, typos, personalization, safety.

**Q38: What impresses L5+?**  
A: Latency budget breakdown, hot-prefix strategy, FST, degrade ladder, privacy thresholds.

**Q39: Common mistake?**  
A: Deep ML personalization first; ignoring len-1 prefixes; SQL LIKE.

---

### Appendix A — Normalize

```text
1. Unicode NFKC
2. Casefold
3. Collapse whitespace
4. Truncate 100 chars
5. Optional punct strip policy
```

### Appendix B — Trie node (logical)

```text
Node {
  children: map[rune]*Node
  top: []PhraseRef  // precomputed
  is_hot: bool
}
```

### Appendix C — Serve pseudocode

```text
def suggest(q, locale, user, limit):
  q = normalize(q)
  if cached := hot.get(locale, q):
    cands = cached
  else:
    cands = shard(locale, q).complete(q, C)
  if len(cands) < limit and allow_fuzzy(q):
    for v in fuzzy_variants(q):
      cands |= shard.complete(v, C')
  recents = user_recents.get(user, timeout=5ms) or []
  ranked = rank(cands, recents, context)
  return safety_filter(ranked)[:limit]
```

### Appendix D — SymSpell sketch

```text
build: for each phrase, store deletes of distance≤1 → phrase
query: generate deletes of q; lookup union; filter edit≤1; score
```

### Appendix E — Hot prefix builder

```text
from logs: compute prefix_qps
for p in prefixes where qps>=T or len(p)<=2:
  topk[p] = best_phrases(p, K)
publish to edge
```

### Appendix F — Ranking formula

```text
base = log(1+count) * (0.2 + ctr)
fresh = exp(-age/half_life)
pers = 1 + 0.5 if in recents else 1
score = base * fresh * pers * context
```

### Appendix G — Latency shed

```text
if deadline_left < 10ms:
  skip fuzzy; skip personal; return cache or partial
```

### Appendix H — Progressive scale table

| Scale | Serve | Cache | Build | Personal |
|-------|-------|-------|-------|----------|
| Baseline | Trie shards | Redis | Daily | Recents |
| 10× | FST | Edge | Daily+delta | +timeout |
| 100× | POP indexes | Mega hot | Continuous | Features |
| 1,000× | Client+edge | Global | Streaming | On-device |

### Appendix I — Response JSON

```json
{
  "q": "how to b",
  "index_version": "2026-08-05t22",
  "suggestions": [
    {"text": "how to boil eggs", "type": "global", "score": 0.91}
  ]
}
```

### Appendix J — NFR card

```text
p99 < 50ms
hot cache for short prefixes
safety filter online
privacy min_count
soft personalization
```

### Appendix K — Index build pipeline

```text
logs -> filter bots -> aggregate -> threshold -> score -> shard -> FST -> GCS -> loaders
```

### Appendix L — Comparison structures

| Structure | Memory | Lookup | Update |
|-----------|--------|--------|--------|
| Trie | High | Fast | Hard |
| FST | Low | Fast | Rebuild |
| Sorted arr | Low | log n | Rebuild |
| ZSET prefix | High keys | Fast | Easy | 

### Appendix M — Abuse controls

| Signal | Action |
|--------|--------|
| Query flood | Rate limit IP/account |
| Suggestion spam phrases | Demote / threshold |
| Click fraud | CTR confidence |

### Appendix N — Logging schema

```text
SuggestLog {request_id, q, locale, shown[], clicked?, ts, index_version, user_hash}
```

### Appendix O — Zero-query

```text
trending(locale, hour_bucket)
contextual: sports if game day (editorial)
```

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Hot prefix | High-QPS prefix with precomputed top-K |
| FST | Finite state transducer dictionary |
| Nearline | Minutes-level update path |
| Re-rank | Reorder fixed candidates |
| Privacy threshold | Min aggregate count to suggest |

### Appendix Q — Worked latency

```text
Edge hit: 5ms → OK
Edge miss + local shard: 8+12+5+3 = 28ms → OK
+ fuzzy 15ms → 43ms → OK
+ slow personal 20ms → 63ms FAIL → timeout personal
```

### Appendix R — Consistency

| Question | Answer |
|----------|--------|
| Same suggestions worldwide? | No — locale/index lag |
| Read-your-new-viral? | Eventually via nearline |
| Personal recent immediate? | Yes if recents store local |

### Appendix S — 30m checklist

1. Clarify suggest type, latency, K, fuzzy, personal, safety.  
2. Latency budget.  
3. Draw edge cache → shard FST → re-rank → filter.  
4. Hot prefixes + degrade.  
5. Offline/nearline build.  
6. Scale 10×/100×/1,000×.  
7. Deal-breakers.

### Appendix T — Client debounce

```text
onInput: wait 30–50ms quiet OR on every 2nd char after 3
cancel in-flight if superseded
```

### Appendix U — Canary ranking

```text
score_v2 shadow; log both; compare CTR offline; % ramp
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Hot cache, FST shards |
| 100× | Edge indexes, nearline |
| 1,000× | Client hybrid, cells |

---

*End of Search Autocomplete / Word Prediction system design.*
