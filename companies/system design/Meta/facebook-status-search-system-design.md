# System Design: Facebook Status Search

> **Focus areas:** Status/post full-text search · Privacy ACL · Near-line indexing · Social ranking · Typeahead · Friends-only visibility · Spam · Freshness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct privacy model first; split index/query planes; deal-breakers for “global inverted index of all private statuses”  
> **Interview theme:** Classic Meta — search over social statuses where **visibility** is as hard as **relevance**

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

Goal: **bound the product**—**Facebook Status Search**: find statuses/posts by keyword (and optional filters) while strictly respecting audience (public, friends, custom) and ranking by relevance + social affinity.

### 1.0 What this is / is not

| Dimension | **Status search (this doc)** | Not this |
|-----------|------------------------------|----------|
| Primary job | Search statuses/posts user is allowed to see | Universal web search; Messenger search |
| Success | Relevant, private-safe results | Perfect semantic IR |
| Corpus | Status updates / posts (text-first; media captions) | Full Reels ANN platform (hooks) |
| Ranking | Text + social + recency | Pure ads auction |
| Correctness | **ACL correctness > recall** | Max recall at any privacy cost |

**Scope statement:** Design Facebook status search with privacy-aware indexing, near-line updates, ranked results, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a status? | User post/status update with text; optional media | Doc = post_id + text + metadata |
| F2 | Who can search? | Logged-in users; results ⊆ visible posts | ACL on every return |
| F3 | Query? | Keywords; phrases; from:user; date | Query parser + filters |
| F4 | Rank? | Relevance, friends first, recency | Multi-signal ranker |
| F5 | Freshness? | New status searchable in seconds–minutes | Streaming index |
| F6 | People vs status tabs? | Status focus; people typeahead adjacent | Separate people suggest |
| F7 | Hashtags? | Yes as terms | Normalize #tags |
| F8 | Comments searchable? | Phase 1.5 optional | Separate doc type |
| F9 | Deleted/edited? | Reflect quickly | Version + tombstone |
| F10 | Spam? | Demote engagement bait / scams | Integrity signals |
| F11 | Analytics? | Out of MVP | Logged queries anonymized |
| F12 | Admin takedown? | Immediate suppress | Control plane |

**MVP functional scope:**

1. Keyword search over statuses the viewer may see.  
2. Filters: time range, author, media/no-media (optional).  
3. Ranking: textual relevance + social affinity + recency.  
4. Near-line index updates on create/edit/delete/visibility change.  
5. Pagination with cursors.  
6. Typeahead for “search posts by friend name / popular terms” light.  
7. Integrity demotion + takedown.

**Out of MVP:**

- Cross-product search (Marketplace, Messenger bodies)  
- Full semantic ANN (mention as extension)  
- Exact phrase search over all historical private posts with zero lag  
- Public unauthenticated scraping API

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Snappy | p99 < 200–300ms |
| N2 | Privacy | Zero leakage | ACL verified; audits |
| N3 | Freshness | Near-line | p99 < 60s; hot < 10–15s aspirational |
| N4 | Availability | High | 99.9%; degrade ranking not ACL |
| N5 | Consistency | Eventual index OK | Tombstones prioritized |
| N6 | Scale | FB-sized | Shard + cache |
| N7 | Edit/delete visibility | Fast hide | Tombstone < few seconds SLO |
| N8 | Multi-region | Global | Regional query; async index repl |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User searches “beach vacation” → friends’ matching statuses rank high.  
2. Author posts status → searchable by friends within freshness SLO.  
3. Author switches Public→Friends → non-friends stop seeing in search.  
4. Author deletes → disappears after tombstone.  
5. Query `from:Alice picnic` → author filter + text.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Custom audience list | Filter via ACL service; may constrain retrieval |
| Blocked user | Never return their statuses |
| Unfriend mid-session | Next query reflects graph; cache short |
| Visibility change race | Versioned doc; max version wins |
| Zero results | Suggest spelling / broader time |
| Hot celebrity page posts | Cache public SERPs |
| ACL service timeout | **Fail closed** for non-public candidates |
| Index lag after post | User may not self-find instantly; optional read-your-write via author shard |
| Copypasta spam | Integrity demote |
| Extremely common term (“the”) | Stopwords; require rarer terms or AND semantics |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 50M | 500M | mega | extreme |
| Statuses searchable | 20B | 200B | 2T | tiered retention |
| New statuses / day | 2B | 20B | 200B | cells |
| Peak search QPS | 30K | 300K | 3M | 30M |
| Avg query terms | 2–3 | 2–3 | 2–3 | 2–3 |
| Friends per user (avg) | 200–400 | same | same | same |
| Index write QPS | 30K | 300K | 3M | 30M |
| Tombstone QPS | 3K | 30K | 300K | 3M |
| Result cache hit | 20–40% | 40%+ | head heavy | edge |

**What each jump forces:**

- **10×:** Privacy-aware posting list design; result cache for public; early ACL bitsets.  
- **100×:** Author-sharded private index + public global index split; regional cells.  
- **1,000×:** Hierarchical retrieval; cold tiers; per-country cells; stronger autocomplete separation.

### 1.5 Etc. (Constraints & Assumptions)

- Graph service answers friends/blocks.  
- Status bodies stored in post service; search holds indexed projection.  
- “Status” ≈ post; Stories out of scope (sibling doc).  
- Legal holds / integrity can force suppress.

**Scope statement to repeat back:**

> Design Facebook status search: privacy-first indexing and retrieval over statuses, near-line updates, relevance+social+recency ranking, cursor pagination, and scale via public/friends index strategies—never leaking invisible content.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Baseline | Plane |
|-------|----------|-------|
| Search QPS | 30K peak | Online |
| Index writes | 30K/s | Streaming |
| Graph/ACL checks | 30K × candidates | Online |
| Cacheable public queries | subset | Edge |
| Typeahead | higher QPS | Separate |

### 2.2 Latency budget (~250ms)

```text
Gateway/auth:     10ms
Query parse:      5–10ms
Retrieval:        40–80ms
ACL filter:       20–40ms (batched)
Rank:             30–60ms
Packaging:        10ms
```

### 2.3 Naive privacy mistake (deal-breaker math)

```text
Retrieve top 10K BM25 globally, then filter to friends-visible
If only 0.1% visible → often empty pages, wasted work
Must constrain retrieval by visibility early
```

### 2.4 Storage order

```text
20B statuses × 200B text avg = 4PB raw text
Index 2–3× expansion compressed posting → multi-PB
Shard + cold archival for old statuses
```

### 2.5 Friends-constrained retrieval cost

```text
Avg friends 300; each friend 1 post/day matching rare term — small
For common terms: intersect term postings with friend-author set
Friend author set as Roaring bitmap / posting list of author_id
```

### 2.6 QPS amplification

```text
30K queries × 5 shards fanout = 150K shard QPS
Cache head queries to cut fanout
```

### 2.7 ACL check amplification

```text
30K QPS × 400 candidates = 12M ACL checks/s if naive per-doc RPC
⇒ Batched bitset: friends roaring ∩ candidate authors; final ACL only on survivors (~50–100)
Custom lists: expensive — constrain retrieval or secondary index carefully
```

### 2.8 Indexing lag budget

```text
Create → Kafka → indexer → searchable
p50 < 5–15s; p99 < 60s public path
Tombstone channel prioritized: p99 hide < 5s
Author RYOW: union primary store recent window (not wait for index)
```

### 2.9 Query rewrite fanout control

```text
Rewrite may add synonyms → term fanout↑
Cap rewritten terms; conservatively spell-correct
from: filter reduces corpus before text intersect — big win
```

### 2.10 Ranking feature fetch

```text
200 candidates × (bm25 already) + social boost from graph cache + integrity prior
Avoid per-candidate heavy NN in MVP; keep lexical+social+time
```

### 2.11 Progressive privacy cost table

| Scale | Friends path | Public path | Cache |
|-------|--------------|-------------|-------|
| Base | Global term ∩ friends bitmap | Lexical shards | Friend-set cache |
| 10× | Author-annotated postings | SERP cache public | Short personalized TTL |
| 100× | Regional index cells | Cold tier opt-in | Edge public only |
| 1,000× | Hierarchical term routing | Country cells | Strict key audit |

### 2.12 BOTE anti-patterns

| Anti-pattern | Failure |
|--------------|---------|
| Top-10K global then filter | Empty pages; wasted work; leak risk |
| Cache SERP by `q` only | Cross-user privacy bug |
| Nightly batch index only | Freshness SLO miss |
| Per-user copy of all friends’ posts index | Write amp impossible |

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/status_search?q=&cursor=&from=&since=` | Ranked statuses |
| `GET /v1/suggest?q=` | Light suggest |
| Bus: `status.events` | create/edit/delete/visibility |
| `POST /admin/suppress` | Takedown |

**Query DSL (MVP):**

```text
terms AND by default
from:user_id | @handle
since:unix until:unix
optional: "phrase"
```

### 3.2 Document model

```text
StatusDoc {
  post_id,
  version,
  author_id,
  audience: PUBLIC | FRIENDS | CUSTOM | ONLY_ME,
  custom_list_id?,
  ts,
  text_normalized,
  lang,
  has_media,
  integrity_score,
  tombstone: bool
}
```

### 3.3 Index topology — Why X over Y

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Single global index + post-filter ACL** | Simple | Waste; leakage risk if bug | Deal-breaker alone |
| **Public index + per-user inbox index** | Great RYOW | Huge storage fanout | Partial |
| **Public index + friends-author constraint** | Scalable | Custom lists harder | **MVP core** |
| **Per-viewer materialized search inbox** | Fast | Write amplification insane | No at FB scale |
| **Crypto search / SSE** | Strong privacy | Ops/latency hard | Research; not MVP |

**Chosen MVP:**

1. **Public corpus index** (audience=PUBLIC).  
2. **Friends corpus path:** retrieve candidates whose `author_id ∈ friends(viewer)` via author-sharded index or author filter postings.  
3. **ONLY_ME:** author-only shard / primary post store search path.  
4. **CUSTOM:** ACL service filter on candidates; limit recall or secondary index by list (Phase 1.5).  
5. Final ACL check always.

### 3.4 Ranking — Why X over Y

| Signal | Why |
|--------|-----|
| BM25 / text | Relevance |
| Social affinity | Friends > FoF > public strangers |
| Recency | Statuses are timely |
| Integrity | Demote spam |
| Engagement light | Optional; avoid clickbait overfit |

**Deal-breaker:** rank only by likes ignoring privacy and relevance.

### 3.5 Why X over Y summary

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Privacy | Constrain + final ACL | Safety | Post-filter only |
| Index | Split public / friends-author | Scale | One global private index |
| Freshness | Kafka near-line | SLO | Nightly batch only |
| Rank | Text+social+time | UX | Likes-only |
| Delete | Tombstone priority | Trust | Eventual delete in days |
| Suggest | Separate | Latency | Main stack per keystroke |

### 3.6 Expanded HLD tradeoffs

| Axis | A | B | Pick |
|------|---|---|------|
| Friends retrieval | Post-filter global | Constrained intersect | **Intersect** |
| Custom lists | Full per-list index | ACL filter MVP | Filter; optimize heavy lists |
| Ranking | Likes-only | BM25×social×time×integrity | **Multi-signal** |
| Cache | Key=`q` | Viewer+versions for personalized | **Correct keys** |
| RYOW | Wait for index | Union primary recent | **Union** |

**Anti-patterns:** global private corpus; fail-open ACL; nightly-only index; personalized SERP cached by query alone.

---

## 4. Architecture Diagram

```text
   Clients --> API Gateway --> Status Search Orchestrator
                                      |
           +--------------------------+--------------------------+
           |                          |                          |
           v                          v                          v
    +-------------+            +-------------+            +-------------+
    | Query Parser|            | Graph/ACL   |            | Ranker      |
    | + rewrite   |            | friends/block|            | text+social |
    +------+------+            +------+------+            +------+------+
           |                          |                          ^
           v                          v                          |
    +-------------+            +-------------+                   |
    | Public      |            | Author/     |                   |
    | Lexical Idx |            | Friends Idx |-------------------+
    +------+------+            +------+------+
           ^                          ^
           |                          |
           +------------+-------------+
                        |
                        v
                 Indexer Workers
                        ^
                        |
                   Kafka status.events
                        ^
                        |
                   Post / Status Service

   Caches: public SERP cache | friend-set cache | doc forward cache
```

**Write path:**

```text
create/edit/delete/visibility
  -> durable post store
  -> emit event (post_id, version, audience, text...)
  -> indexer applies versioned upsert/tombstone
  -> public and/or author shard updated
```

**Read path:**

```text
q + viewer
  -> parse
  -> fetch friends bitmap (cached)
  -> parallel: public retrieve | friends-author retrieve
  -> merge + ACL
  -> rank
  -> page
```

**Delete path:**

```text
delete -> version++ tombstone -> index remove + cache purge by post_id
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No invisible status in results** (blocks, audience, takedown).  
2. **Tombstones beat stale docs** (version).  
3. **ACL timeout ⇒ drop non-public candidates**.  
4. **Ranking degradation OK; privacy degradation not OK**.  
5. **Idempotent index apply** by `(post_id, version)`.

#### 5.1.2 Read-your-write

Authors often search their own words immediately:

```text
Option A: author home index shard synchronous-ish
Option B: query post service for viewer's recent posts matching q (limited N) union index results
MVP: Option B union for viewer==author recent window
```

#### 5.1.3 Visibility change

```text
PUBLIC -> FRIENDS: remove from public index; ensure friends path has doc
FRIENDS -> PUBLIC: add public index
-> ONLY_ME: remove from both; author-only
Use versioned ops; ignore stale late events
```

#### 5.1.4 Dual-write safety

Post store is source of truth; index is derived. Rebuild from post store + event log if corruption.

### 5.2 Scalability

#### 5.2.1 Sharding

| Index | Shard key | Notes |
|-------|-----------|-------|
| Public lexical | term hash / doc id | Scatter-gather |
| Author index | author_id | Friends path: fanout to friend authors’ shards carefully |
| Forward store | post_id | Snippets |

**Friends path optimization:**

```text
Do NOT fanout to 300 author shards naively for every query.
Techniques:
  1) Global posting list for term containing author_id in payload → intersect author_id ∈ friends
  2) Maintain "friends' public+friends posts" posting via term postings with author attribute
  3) For rare terms, retrieve global candidates then intersect friends (OK if candidate set small)
  4) For common terms, require intersection early / posting lists sorted by author
```

#### 5.2.2 Hot terms

Stopwords removed; phrase/AND; cache. Celebrity authors replicated.

#### 5.2.3 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | Bitset intersect; SERP cache; versioned tombstones |
| 100× | Regional index cells; cold tier >1y |
| 1,000× | Country cells; hierarchical term routing; ANN optional side |

### 5.3 Maintainability

- Schema for `StatusDoc` versioned.  
- Indexer DLQ for poison events.  
- Privacy audit logs (sampled).  
- Golden privacy test suite (must pass in CI).  
- Clear ownership: indexing vs ranking vs ACL.

### 5.4 Ranking details

```text
score = bm25 * social_boost * recency_decay * integrity_mult

social_boost:
  author == viewer: high
  friend: high
  followed page: medium
  public stranger: low

recency_decay: exp(-λ Δt) with floor
```

### 5.5 Snippets & highlighting

Forward store holds text; generate snippets with term offsets; escape HTML; respect character limits.

### 5.6 Spam & integrity

Signals: URL redirects, copy-paste clusters, engagement anomalies, reported content. Demote or tombstone.

### 5.7 Pagination

Cursor: `(score, post_id, ts, index_gen)`. Filter already-seen ids. Explain possible duplicates on index gen change.

### 5.8 Caching

| Cache | Key | TTL | Risk |
|-------|-----|-----|------|
| Public SERP | hash(q, locale) | 30–120s | OK if public-only docs |
| Friend set | viewer_id | 1–5 min | Invalidate on friend change event |
| Doc | post_id | minutes | Purge on edit/delete |
| Personalized SERP | viewer+q | ≤15–30s | Privacy-sensitive |

**Deal-breaker:** caching personalized results keyed only by `q`.

### 5.9 Custom audiences (Phase 1.5)

```text
Retrieve with friends/public heuristics then ACL check custom membership
OR index post_id under list_id posting (write amp)
Start with filter; optimize lists that are huge
```

### 5.10 Multi-region

Query in region; indexes replicate async. Cross-region friend posts may lag seconds–minutes; acceptable if tombstones prioritized via faster channel.

### 5.11 Nested deep dive — Privacy ACL

#### 5.11.1 Audience model

| Audience | Index placement | Retrieval constraint |
|----------|-----------------|----------------------|
| PUBLIC | Public lexical index | Global term retrieve + block filter |
| FRIENDS | Author-annotated / friends path | `author ∈ friends(viewer)` |
| ONLY_ME | Author-only shard / primary | `viewer == author` |
| CUSTOM | Limited index or filter | ACL service membership |

#### 5.11.2 Mandatory final check

```text
candidates = retrieve(...)
visible = []
for c in candidates:
  if blocked(viewer, c.author): continue
  decision = acl.evaluate(viewer, c)  # fail closed on timeout for non-public
  if decision.allow: visible.append(c)
return visible
```

**Deal-breaker:** UI-only filtering; public shard containing friends-only body text without constraints.

#### 5.11.3 Graph inputs

```text
friends_bitmap(viewer)  # Roaring; cached 1–5 min
block_set(viewer)
follow_pages(viewer)    # optional boost, not visibility for friends-only
```

Invalidate friend cache on friend/unfriend; short TTL bounds leak window.

#### 5.11.4 Cache key rules

| Cache | Allowed key | Forbidden |
|-------|-------------|-----------|
| Public SERP | `q + locale + public_only` | viewer-mixed results |
| Personalized | `viewer + q + friend_ver + acl_epoch` | `q` alone |
| Doc forward | `post_id + version` | — |

#### 5.11.5 Privacy test matrix (CI)

| Author audience | Viewer | Expect |
|-----------------|--------|--------|
| FRIENDS | friend | hit |
| FRIENDS | stranger | miss |
| PUBLIC | stranger | hit (modulo block) |
| ONLY_ME | friend | miss |
| deleted | author | miss within tombstone SLO |

### 5.12 Nested deep dive — Indexing lag

#### 5.12.1 Lag SLO bands

| Event | p99 target | Priority |
|-------|------------|----------|
| Create public | < 60s | Normal |
| Create friends | < 60s | Normal |
| Edit | < 60s | Normal |
| Delete / visibility tighten | < 5s | **High** |
| Integrity suppress | < 5s | **High** |

#### 5.12.2 Pipeline

```text
Post store commit
  -> outbox/CDC StatusEvent(version)
  -> Kafka (tombstone topic higher priority / separate consumer group)
  -> Indexer: max-version wins
  -> Public and/or friends path update
  -> Cache purge by post_id on delete/visibility↓
```

#### 5.12.3 Read-your-write

```text
if query.viewer may match author recent:
  union( primary.search_recent(viewer, q, window=5m), index_results )
dedupe by post_id preferring higher version
```

#### 5.12.4 Lag UX

- Degraded freshness banner internal only.  
- Never fail open on ACL because index is stale.  
- Late stale events ignored via version.

### 5.13 Nested deep dive — Query rewrite

#### 5.13.1 Pipeline

```text
normalize unicode/case
extract operators: from:, since:, until:, "phrase", #tag
language detect
conservative spell correction (high confidence or zero-results path)
synonym expand capped (e.g. +2 terms max)
hashtag normalize (#NYC → nyc token)
stopword drop unless phrase
```

#### 5.13.2 Examples

| Input | Rewrite |
|-------|---------|
| `from:alice beach` | `author_id=alice AND beach` |
| `"spring break"` | positional phrase |
| `#nyc pizza` | `tag:nyc AND pizza` |
| `teh beach` | `the beach` only if confident |

#### 5.13.3 Safety

- Over-correction hurts names/brands — gate by confidence.  
- Synonym blowups increase shard fanout — hard cap.  
- Operator `from:` applied before expensive text retrieve.

### 5.14 Nested deep dive — Ranking

#### 5.14.1 Score

```text
score = bm25(terms, doc)
        * (1 + α * social_affinity(viewer, author))
        * exp(-λ * age_hours)   # floor at ε
        * integrity_mult
```

| Affinity | Example mult |
|----------|--------------|
| Self | 3.0 |
| Friend | 2.0 |
| Followed page | 1.4 |
| Public stranger | 1.0 |

#### 5.14.2 Why not likes-only

Viral public spam would drown friends’ relevant statuses; social+text first. Light engagement optional with cap.

#### 5.14.3 Blending public + friends paths

```text
Merge candidate lists; dedupe post_id
Rank once with features including cg_source
Page with cursor (score, post_id, ts, index_gen)
```

#### 5.14.4 Integrity in rank

Demote or hard-filter; suppress wins. Copy-paste clusters and scam URLs penalized.

### 5.15 Nested deep dive — Scale, anti-patterns, deal-breakers

#### 5.15.1 Progressive scale

| Scale | Must |
|-------|------|
| 10× | Bitset intersect; versioned tombstones; SERP cache public |
| 100× | Regional cells; cold tier; author-annotated postings |
| 1,000× | Hierarchical term routing; country cells; optional ANN side |

#### 5.15.2 Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| Post-filter-only ACL | Empty pages + leak risk |
| Per-user inbox of all posts | Write amp |
| Personalized cache key=`q` | Cross-user leak |
| Slow deletes | Trust/legal failure |

#### 5.15.3 Deal-breakers

1. Global private text index without constraints.  
2. Fail-open ACL on timeout.  
3. Ranking ignores blocks.  
4. Modulo “search all then filter.”  
5. Client-trusted visibility.

---

## 6. Wrap-Up

### 6.1 60-second pitch

> Facebook status search is a privacy-first retrieval problem. We maintain derived indexes from status events, split public vs friends-author retrieval, always ACL-check, and rank by text + social + time. Deletes and visibility changes are versioned tombstones. Scale with sharding, bitset intersection, and careful caching—never by scanning the world and filtering late.

### 6.2 Deal-breakers

1. Global index of private texts without constraints.  
2. Post-filter-only ACL with huge candidate sets.  
3. Personalized cache keyed by query alone.  
4. Slow deletes.  
5. Ranking that ignores blocks.

### 6.3 Scale one-liner

Bitsets + public/friends split → regional cells → cold tiers + hierarchical term routing.

---

## 7. Deeper / Related Interview Questions

### Q1. Why is status search harder than web search?

**Answer:** Documents have per-viewer visibility; social ranking; rapid edits/deletes; graph dependence. Privacy bugs are product-fatal.

### Q2. How do you avoid leaking friends-only posts?

**Answer:** Constrain retrieval; final ACL; fail closed; no public cache of non-public docs; privacy tests; audited debug tools.

### Q3. Explain versioned indexing.

**Answer:** Each change increments `version`. Indexer applies only if `version ≥ current`. Tombstones remove docs. Late stale events ignored.

### Q4. How do friends bitmaps work?

**Answer:** Roaring bitmap of friend author ids cached per viewer; intersect with candidate author ids or author-annotated postings.

### Q5. What if a user has 5,000 friends?

**Answer:** Cap naive fanout; rely on term∩author intersection; sample/priority friends for CG if needed; still final ACL.

### Q6. Read-your-write for authors?

**Answer:** Union recent posts from primary store matching query with index results for `author==viewer`.

### Q7. How fast must deletes propagate?

**Answer:** Product/legal often want seconds. Dedicated tombstone path + cache purge; search may show stale until then—measure SLO.

### Q8. Stopwords strategy?

**Answer:** Drop extremely common terms; require at least one informative term; support phrases.

### Q9. How do you rank?

**Answer:** BM25 × social boost × recency × integrity. Tune via online experiments.

### Q10. Can we use embeddings?

**Answer:** Yes as side CG for semantic recall on public content; privacy still applies; MVP can be lexical-first.

### Q11. Blocked users?

**Answer:** Exclude authors in block sets both ways per product rules; treat like ACL.

### Q12. Index rebuild strategy?

**Answer:** Batch MapReduce/Spark from source of truth; dual-write new cluster; swap alias; streaming catch-up.

### Q13. Handling edits?

**Answer:** New version upsert replaces terms; old term postings removed via update semantics or delete+add.

### Q14. Why separate typeahead?

**Answer:** Ultra-low latency prefix load; different index structure.

### Q15. Geo/language?

**Answer:** Language field + prefer same lang; geo optional boost; don’t hide friends’ other languages by default.

### Q16. Pagination stability?

**Answer:** Cursor with scores/ids; tolerate minor reshuffle after index gen change.

### Q17. Custom privacy lists at scale?

**Answer:** Hard write amp if fully indexed per list; MVP ACL filter; optimize heavy lists.

### Q18. What is fail-closed?

**Answer:** On ACL uncertainty, omit doc rather than include. Opposite of fail-open.

### Q19. Hot query caching safety?

**Answer:** Only cache result sets that are identical for all viewers (true public navigational) or key by viewer.

### Q20. How do you test privacy?

**Answer:** Fixture graph/audiences; assert inclusion/exclusion matrix; fuzz visibility transitions; canary audits.

### Q21. Scatter-gather timeout?

**Answer:** Per-shard budget; partial results with degraded flag; prefer correct incomplete over late leaky complete.

### Q22. Spam copy-paste statuses?

**Answer:** Near-dup clustering; integrity scores; rate limits on distribution.

### Q23. Multi-region inconsistency example?

**Answer:** Friend’s new post searchable in us-east before eu; OK. Deleted post must not reappear via lagged replica—tombstone channel + version checks.

### Q24. Storage tiering?

**Answer:** Hot recent index; warm; cold archive with slower search or time-bounded default (e.g., last 2 years) + “search older” opt-in.

### Q25. Difference from general Meta search platform?

**Answer:** Narrower corpus (statuses), deeper privacy/friends ranking focus; less Explore ANN; tighter tombstone SLOs.

### Q26. Phrase queries?

**Answer:** Positional postings or next-doc approximations; costlier; use for quoted queries.

### Q27. Rate limiting?

**Answer:** Per-user search QPS; scraping detection; CAPTCHA/anomaly for abusive patterns.

### Q28. Snippet privacy?

**Answer:** Snippets only for returned ACL-ok docs; never prefetch snippets for rejected candidates into client logs.

### Q29. Graph cache stampede?

**Answer:** Soft TTL + singleflight; serve stale friend set briefly with short bound; refresh async.

### Q30. What breaks at 100×?

**Answer:** Naive per-friend shard fanout; giant uncompressed bitmaps; uncached head queries; single-region index.

### Q31. ONLY_ME search?

**Answer:** Author-only index or primary DB prefix search; never global.

### Q32. How do hashtags work?

**Answer:** Token `#tag` normalized; can boost exact tag matches.

### Q33. Observability for leakage?

**Answer:** Rare but critical: diff sampled results vs independent ACL oracle; secure logging; privacy incident playbooks.

### Q34. Can search use engagement?

**Answer:** Light signal OK; don’t let viral public spam dominate friends’ relevant posts.

### Q35. Launch checklist?

**Answer:** Privacy tests green; freshness/tombstone SLOs; p99 latency; fail-closed drills; cache key audit; rank offline eval.

### Q36. How do you prioritize tombstones over creates in the indexer?

**Answer:** Separate high-priority consumer/topic or priority queue; apply deletes/visibility-tighten before backlog of creates; measure hide latency independently.

### Q37. Why is `from:` a retrieval win?

**Answer:** It constrains author early, shrinking posting intersection and ACL work — especially important for common terms.

### Q38. What social ranking mistake loses trust?

**Answer:** Surfacing blocked users’ statuses or friends-only posts to strangers due to cache key bugs or fail-open ACL.

### Q39. How does indexing lag interact with RYOW?

**Answer:** Index lag is OK for others within SLO; authors union primary recent posts so self-search works immediately.

### Q40. Phrase queries vs term queries at scale?

**Answer:** Phrases need positions (costlier); use for quoted queries only; default AND terms with BM25.

### Q41. When add ANN to status search?

**Answer:** As side CG for semantic public content after lexical+ACL core is correct; never as privacy bypass.

### Q42. Progressive scale one-liner?

**Answer:** Bitsets + public/friends split → regional cells + cold tier → hierarchical term routing (+ optional ANN side).

---

## Appendix A — Event schema

```text
StatusEvent {post_id, version, op, author_id, audience, text, ts, lang, integrity}
```

## Appendix B — ACL decision table

| Audience | Viewer relationship | Visible? |
|----------|---------------------|----------|
| PUBLIC | anyone (modulo block) | yes |
| FRIENDS | friend | yes |
| FRIENDS | stranger | no |
| ONLY_ME | author | yes |
| CUSTOM | in list | yes |

## Appendix C — Latency card

```text
parse 10 | retrieve 60 | acl 30 | rank 40 | pack 10 ≈ 150ms + jitter
```

## Appendix D — Friend intersect pseudocode

```text
cands = index.search(terms, k=2000, fields=[author_id])
friends = graph.friends_bitmap(viewer)
visible = [c for c in cands if c.author_id in friends or c.audience==PUBLIC]
visible = acl.verify(viewer, visible)
```

## Appendix E — Tombstone SLO

```text
emit -> index apply p99 < 5s
cache purge < 2s
measure hide latency end-to-end
```

## Appendix F — Cache key antipatterns

| Bad key | Why |
|---------|-----|
| `q` only for mixed results | Leaks across users |
| `user` without version | Stale privacy |

## Appendix G — Rank formula v1

```text
score = bm25 * (1+α social) * exp(-λ age_hours) * integrity
```

## Appendix H — Indexer state machine

```text
APPLY if event.version > stored.version
if tombstone: delete postings
else upsert postings + forward
```

## Appendix I — Cold tier

| Age | Storage | Query |
|-----|---------|-------|
| 0–90d | SSD hot | default |
| 90d–2y | warm | default |
| >2y | cold | opt-in |

## Appendix J — Failure modes

| Failure | Mode |
|---------|------|
| Graph down | Public-only results + warning OR fail search (product choice); never friends guess |
| Index shard down | Partial; degraded |
| Ranker down | BM25 only |

## Appendix K — Security

- Encrypt index disks  
- Restrict raw dump access  
- Audit high-privilege search tools  

## Appendix L — Suggest dictionary

```text
friend names + prior queries + trending public terms
```

## Appendix M — Worked QPS

```text
30K QPS × 40% cache hit = 18K orchestrations
× 4 shard fanout = 72K shard queries
ACL batch 18K × 200 cands = manageable with bitset
```

## Appendix N — NFR card

```text
p99 < 300ms
tombstone hide fast
ACL fail-closed
no cross-user cache
freshness < 60s
```

## Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Tombstone | Delete marker |
| Posting list | term → docs |
| Roaring | Compressed bitmap |
| RYOW | Read your own write |
| SERP | Results page |

## Appendix P — 30m checklist

1. Lock privacy model.  
2. Kill post-filter-only design.  
3. Draw events → indexer → split retrieve → ACL → rank.  
4. Freshness + tombstones.  
5. Scale jumps.  
6. Deal-breakers.

## Appendix Q — Comparison table

| Design | Privacy | Cost | MVP? |
|--------|---------|------|------|
| Post-filter global | Risky/wasteful | High waste | No |
| Public+friends intersect | Strong | Medium | Yes |
| Per-user inbox index | Strong | Very high writes | No |

## Appendix R — Author shard fanout control

```text
if idf(term) high (rare): global retrieve then intersect friends
if idf low (common): use author-annotated postings + bitmap intersect; cap K
```

## Appendix S — Edit race example

```text
v3 friends text A in index
late v2 public text B arrives -> ignore
v4 delete -> tombstone
```

## Appendix T — Metrics

| Metric | Type |
|--------|------|
| Leakage audit fails | Counter (should be 0) |
| Freshness lag | Histogram |
| Empty rate | Ratio |
| p99 | Latency |

## Appendix U — Related systems

| System | Role |
|--------|------|
| Post service | Source of truth |
| Graph | Friends/blocks |
| Kafka | Events |
| Integrity | Spam/takedown |

## Appendix V — Progressive scale

| Scale | Must |
|-------|------|
| 10× | Bitsets, caches, versions |
| 100× | Cells, cold tier |
| 1,000× | Hierarchical routing |

## Appendix W — Phrase posting

```text
store positions; phrase: positional next-doc
```

## Appendix X — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Elasticsearch with filtered aliases” | Still need FB-scale privacy + social rank story |
| “Search all then filter” | Empty pages + cost + risk |
| “Encrypt client-side only” | Breaks ranking/UX for MVP |

## Appendix Y — Pseudocode orchestrator

```text
def search(viewer, q, cursor):
  terms = parse(q)
  friends = cached_friends(viewer)
  pub = public_idx.search(terms, k=500)
  fr = friends_idx.search(terms, friends, k=500)
  cands = dedup(pub+fr)
  cands = acl_filter(viewer, cands)  # fail closed
  ranked = rank(viewer, cands, terms)
  return page(ranked, cursor)
```

## Appendix Z — Success bar

Correct privacy under transitions, fast enough UX, durable deletes, and a scaling path that keeps intersection-based retrieval rather than per-user copy of the internet.

---


## Appendix AA — Interview opening script

```text
"I'd design Facebook status search as privacy-first retrieval: derived indexes from status events,
split public vs friends-author paths, always ACL-check fail-closed, rank by BM25 × social × recency,
and versioned tombstones for delete/visibility. Caching is keyed carefully so we never serve another
user's private SERP. At scale we use bitset intersection and regional cells—not post-filter-only."
```

## Appendix AB — Visibility transition tests

| From | To | Index actions |
|------|----|---------------|
| PUBLIC | FRIENDS | Delete public postings; ensure friends path |
| FRIENDS | PUBLIC | Upsert public postings |
| ANY | ONLY_ME | Remove shared indexes |
| ANY | deleted | Tombstone all |

## Appendix AC — Social boost table

| Relationship | Multiplier (example) |
|--------------|----------------------|
| Self | 3.0 |
| Friend | 2.0 |
| Followed page | 1.4 |
| Public stranger | 1.0 |
| Blocked | 0 (filtered) |

## Appendix AD — Query rewrite examples

| Input | Rewrite |
|-------|---------|
| `from:alice beach` | author_id=alice AND terms[beach] |
| `"spring break"` | phrase |
| `#nyc` | tag token nyc |

## Appendix AE — End-to-end privacy drill

```text
1. Create friends-only status with unique token string
2. Search as stranger → 0 results
3. Search as friend → hit
4. Switch to only-me → friend search → 0
5. Delete → author search → 0 within tombstone SLO
```

## Appendix AF — What interviewers listen for

- Privacy before recall
- Versioned index apply
- Friends intersect strategy
- Cache key correctness
- Progressive scale without rewriting the model

## Appendix AG — Indexing lag runbook

```text
Symptom: freshness lag p99 > 60s
1. Check Kafka consumer lag on status.events
2. Check indexer DLQ / poison docs
3. Check segment merge backlog
4. Shed noncritical rewrites; prioritize tombstone topic
5. Communicate degraded search freshness; ACL path unchanged
```

## Appendix AH — Query rewrite safety card

```text
spell: only high confidence OR zero-results path
synonyms: hard cap (+2)
operators: apply from:/since: before text fanout
stopwords: drop unless phrase
never rewrite away privacy operators
```

## Appendix AI — Ranking ablation (interview)

| Ablation | Expected UX harm |
|----------|------------------|
| Remove social | Strangers drown friends |
| Remove recency | Stale statuses dominate |
| Remove integrity | Spam rises |
| Likes-only | Clickbait / privacy-irrelevant |

## Appendix AJ — Progressive privacy scale

| Scale | Friends path tech | Tombstone | Cache |
|-------|-------------------|-----------|-------|
| 10× | Roaring intersect | Priority channel | Public SERP only |
| 100× | Author-annotated postings | <5s hide | Personalized short TTL |
| 1,000× | Hierarchical terms | Global purge | Strict key audit |

*End of Facebook Status Search system design.*
