#!/usr/bin/env python3
"""Generate seven Amazon SDE III system design markdown files."""
from pathlib import Path

OUT = Path("/Users/yingpengwang/leetcode/system design/Amazon")


def toc():
    return """## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---
"""


def qa_block(pairs):
    lines = []
    for i, (q, a) in enumerate(pairs, 1):
        lines.append(f"**Q{i}. {q}**")
        lines.append("")
        lines.append(f"**A:** {a}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DOC 1: Search Autocomplete
# ---------------------------------------------------------------------------
DOC1 = r'''# System Design: Search Autocomplete / Typeahead (Amazon Retail)

> **Focus areas:** Prefix indexes / trie · Top-K ranking · Hot-prefix cache · Typo tolerance · Personalization · p99 latency · Offline→online serving · Catalog + query suggest · Safety / PII  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit latency budget, split suggest-read vs log-learn planes, deal-breakers for “query warehouse on each keystroke”  
> **Interview theme:** Amazon SDE III / L6 — **Search & Discovery** ownership for Amazon.com / App Store–style typeahead under extreme QPS with customer trust, marketplace fairness, and operational accountability

---

''' + toc() + r'''
## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—an Amazon **search autocomplete / typeahead** service that returns top-K suggestions (queries, ASINs, brands, categories, deals) as the customer types, with ranking, light personalization, typo tolerance, safety filtering, and strict latency (p99 tens of ms), at Amazon retail search-box scale.

### 1.0 What this is / is not

| Dimension | **Autocomplete / typeahead (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Prefix / early tokens → ranked suggestions fast | Full A9/OpenSearch SERP ranking |
| Success | Relevant, safe, shoppable suggestions; p99 tight | Perfect semantic understanding MVP |
| Index | Prefix structures + scores + entity overlays | Live scan of catalog / query warehouse each keystroke |
| Personalization | Re-rank small candidate set (recents, locale, department) | Heavy private DNN per keystroke at 100M QPS |
| Entities | Queries + ASINs + brands + categories | Full product-detail page as response |
| Amazon lens | Conversion, discovery, seller fairness, cost/QPS, ownership | Academic IR paper alone |

**Scope statement:** Design Amazon retail search autocomplete: sharded prefix serving, multi-entity suggestions, ranking, hot-prefix cache, typos, light personalization, safety—with progressive scale and clear ownership boundaries vs SERP.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Suggest what? | Queries/phrases; ASINs; brands; categories; optional deals | Typed candidates with vertical tags |
| F2 | Top-K? | 8–10 UI; compute 30–80 candidates | Truncate after rank + diversify |
| F3 | Ranking? | Popularity, CTR, conversion, freshness, department | Offline score + online boosts |
| F4 | Personalization? | Recents + locale/marketplace + light affinity | Client recents + thin profile |
| F5 | Typos? | Yes for len≥3, 1-edit common retail terms | Fuzzy layer budgeted |
| F6 | Marketplaces? | Multi-marketplace (US, EU, JP, …) | Partition by marketplace_id |
| F7 | Safety? | Block NSFW, hate, PII leaks, illegal goods | Policy filter before return |
| F8 | Freshness? | Viral / deal queries in minutes–hours | Nearline delta updater |
| F9 | Empty prefix? | Trending / seasonal / personalized zero-state | Separate trending lists |
| F10 | Analytics? | Impression/click/purchase attribution | Async learning pipeline |
| F11 | Client cache? | First-char / session cache on app | Hybrid edge/client |
| F12 | Auth? | Logged-in personalization; logged-out global | Two modes |
| F13 | Sponsored? | Optional sponsored suggest slot (policy-gated) | Separate auction/ad path; label clearly |
| F14 | Voice / Fire TV? | Same API family; different UX K | Shared candidates, different rank features |
| F15 | Catalog churn? | New ASINs / OOS | Entity status filter on serve |

**MVP functional scope:**

1. `GET /suggest?q=&marketplace=&locale=&limit=&department=` → ranked suggestions.  
2. Offline build of prefix index from query logs + scores + entity overlays.  
3. Online serve from memory shards + hot-prefix cache.  
4. Basic typo tolerance (normalize + common fuzzy).  
5. Personalization: boost user’s recent queries + marketplace/locale.  
6. Safety/blocklist filter on serve path.  
7. Async impression/click/purchase logging.  
8. Nearline path for spike queries and deal starts.  
9. Diversify: don’t return 10 near-duplicate “iphone case …” strings.

**Out of MVP:**

- Full LLM next-token decoding per keystroke as sole path  
- Deep semantic vector suggest without candidate restriction  
- Complete sponsored marketplace with full ads stack (thin slot OK)  
- Cross-script transliteration beyond simple normalize (Phase 1.5)  
- Replacing SERP ranking

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Instant per keystroke | **p99 < 40–50ms** in-region suggest |
| N2 | Availability | Search box critical | 99.99%; stale index OK |
| N3 | Throughput | Huge read QPS | Millions+ via cache/edge |
| N4 | Freshness | New terms / deals reasonably soon | Minutes–hours MVP |
| N5 | Consistency | Suggestions may lag logs | Eventual OK |
| N6 | Cost | Memory-heavy serving | Shard + compression + prefix pruning |
| N7 | Privacy | No leaking rare PII queries | Aggregation thresholds; k-anonymity |
| N8 | Safety | No banned / illegal suggestions | Filter non-bypassable |
| N9 | Multi-AZ | Region-local serve | Active-active within marketplace region |
| N10 | Ownership | Clear pager for suggest vs SERP | Two-pizza service boundary |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Customer types `wirel` → `wireless earbuds`, brand tiles, top ASIN.  
2. `iphon` → fuzzy → `iphone 16 case`.  
3. Recent `protein powder` boosted on `prot`.  
4. Lightning deal query appears within ~5–30 min nearline.  
5. Empty query → marketplace trending / seasonal.  
6. Department scoped to Books → book-biased suggestions.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Prefix length 1 | Only precomputed head; hard CPU/memory cap |
| Rare PII-like query (`ssn 123…`) | Never suggest; aggregation threshold |
| OOS ASIN | Suppress or mark; prefer in-stock alternatives |
| Adult / NSFW | Marketplace policy filter |
| Bot keystroke storms | Edge rate limit; cache aggressively |
| Index build lag | Serve last good + nearline delta |
| Marketplace mismatch | Never leak JP suggestions into US |
| Homoglyph / unicode tricks | Normalize NFKC; safety pass |
| Duplicate phrasings | Diversify by stem / intent cluster |
| Sponsored only results | Forbidden — organic always present |
| Cold marketplace launch | Bootstrap from catalog titles + seed queries |
| Prime Day spike | Hot-prefix cache + capacity reserve |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Suggest QPS (peak) | 2M | 20M | 200M | 2B |
| Unique prefixes/day | 200M | 2B | — | edge aggregation |
| Index entries (queries) | 50M | 100M | 200M | pruned heads |
| Entity overlays (ASINs/brands) | 100M | 200M | 500M | hierarchical |
| Hot-prefix cache hit rate | 70% | 80% | 90% | 95%+ |
| Log events/day | 20B | 200B | 2T | sampled |
| Marketplaces | 20 | 20 | 20+ | more locales |
| p99 latency | 50ms | 50ms | 40ms | 30ms (edge) |

**What each jump forces:**

- **10×:** Edge/CDN suggest for head; stronger sharding; compression.  
- **100×:** Marketplace/department cells; aggressive prefix pruning; client models for head.  
- **1,000×:** Hierarchical indexes; on-device head dictionaries; server only for long-tail / personalized.

### 1.5 Etc. (Constraints & Assumptions)

- Autocomplete is a **client of logging + offline rank training**—not the SERP.  
- **Customer trust:** never suggest illegal/unsafe; never leak private rare queries.  
- **Seller fairness:** organic ranking must not silently become pay-to-play without labels.  
- Ownership: Suggest Service owns **latency + safety filter + candidate merge**; Ads owns sponsored slot.  
- Prefer **mechanisms over meetings**: capacity alarms, index freshness SLO, clear runbooks.

**Scope statement to repeat back:**

> Design Amazon retail search autocomplete: multi-entity top-K suggestions with sharded prefix indexes, hot-prefix cache, typo tolerance, light personalization, safety filters, nearline freshness, and progressive scale 10×/100×/1,000×—distinct from full SERP ranking, with explicit ownership and cost/latency tradeoffs.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| A — Suggest read | Sync keystroke → top-K | 2M QPS | 20M | Online |
| B — Hot-prefix cache | Redis/edge get | ~1.4M hits | 16M | Online |
| C — Shard trie fanout | Miss → memory shard | ~600K | 4M | Online |
| D — Log ingest | Impression/click | ~50–100K/s | 0.5–1M/s | Streaming |
| E — Offline build | Index + scores | Daily + hourly delta | — | Offline |
| F — Nearline spikes | Viral/deal prefixes | Bursty | Bursty | Nearline |

**Interview tip:** Never quote one “QPS.” Split **suggest**, **cache**, **shard**, **logs**, **build**—they scale and fail differently.

### 2.2 Latency budget (online suggest)

| Step | Budget |
|------|--------|
| Edge / API gateway | 2–5 ms |
| Auth / marketplace resolve (cached) | 1–3 ms |
| Hot-prefix cache | 1–5 ms |
| Shard lookup + candidate merge | 5–15 ms |
| Rank / diversify / personalize | 3–10 ms |
| Safety filter | 1–3 ms |
| **Total p99 target** | **≤ 40–50 ms** |

### 2.3 Memory math (baseline marketplace cell)

| Structure | Assumption | Size |
|-----------|------------|------|
| Compressed trie / FST | 50M queries, avg 20B key + 16B payload | ~2–4 TB raw → 200–800 GB compressed/sharded |
| Entity overlay | 100M ASINs lightweight | 50–150 GB |
| Hot-prefix cache | top 10M prefixes × 1 KB | ~10 GB/region |
| Per-shard RAM | 64–128 GB nodes × N shards | plan N so working set fits |

**Rule of thumb:** Prefer **FST / succinct trie** over naïve pointer-heavy tries at Amazon scale.

### 2.4 Bandwidth

- Client: ~10 keystrokes/query × 1 KB response ≈ 10 KB / search session suggest traffic.  
- At 2M QPS × 1 KB ≈ **2 GB/s** egress regionally before compression—hence edge cache.  
- Logs: sample impressions; keep full clicks/purchases for training.

### 2.5 Cost intuition

| Lever | Effect |
|-------|--------|
| Cache hit +10% | Huge CPU/RAM save on shards |
| Prefix prune rare tails | Memory ↓; rare queries fall to fuzzy/catalog |
| Edge serve head | Cross-AZ traffic ↓ |
| Client dictionary for len≤2 | Server QPS ↓ dramatically |

### 2.6 Scale jump implications

| Jump | Suggest QPS | If naïve DB | Reality |
|------|-------------|-------------|---------|
| Base | 2M | Impossible | Memory shards + cache |
| 10× | 20M | — | Edge + more cells |
| 100× | 200M | — | Client + hierarchical |
| 1,000× | 2B | — | On-device head; server long-tail |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Latency first:** search box must feel instantaneous.  
2. **Customer trust:** safety + privacy non-bypassable.  
3. **Discovery & conversion:** suggestions should be shoppable and useful.  
4. **Ownership:** clear boundaries vs SERP, Ads, Catalog.  
5. **Cost control:** memory and egress dominate; prune + cache.  
6. **Operability:** index freshness SLO, canary, rollback.

### 3.2 Core components

| Component | Responsibility | Why separate |
|-----------|----------------|--------------|
| Suggest API / BFF | Auth, marketplace, response shaping | Client contract |
| Edge / CDN cache | Hot prefixes by marketplace | Absorb head QPS |
| Hot-prefix cache (Redis) | Regional L2 | Microsecond gets |
| Prefix Shard Service | In-memory FST/trie top-K | Latency ownership |
| Fuzzy / Typo Service | Edit-distance candidates (budgeted) | Optional path |
| Entity Overlay Service | ASIN/brand/category cards | Catalog join |
| Ranker (lightweight) | Merge + score + diversify | Online features thin |
| Personalization | Recents + affinity boosts | Small candidate re-rank |
| Safety Filter | Blocklist / classifiers | Policy gate |
| Log Pipeline | Impressions/clicks/purchases | Learning |
| Offline Builder | Scores + index artifacts | Daily/hourly |
| Nearline Updater | Spikes / deals | Minutes |
| Model / Score Platform | Train CTR/CVR proxies | Safe rollout |

### 3.3 Primary flows

**Flow A — Keystroke suggest**

1. Client debounces (~30–50ms) → `GET /suggest`.  
2. Edge cache by `(marketplace, locale, normalized_prefix, department?)`.  
3. On miss: Hot-prefix Redis → Prefix shards (consistent hash on prefix).  
4. Merge query + entity candidates → rank → diversify → safety → respond.  
5. Async log impression.

**Flow B — Offline learn**

1. Aggregate query → click → purchase.  
2. Compute popularity / CTR / CVR / freshness scores.  
3. Build compressed index artifact → canary → fleet deploy.

**Flow C — Nearline spike**

1. Detect sudden query velocity (Prime Day ASIN, celebrity).  
2. Patch delta into hot cache + shard side structure.  
3. Expire when velocity decays.

### 3.4 API sketch

```text
GET /v1/suggest
  ?q=wirel
  &marketplace=ATVPDKIKX0DER
  &locale=en_US
  &department=electronics
  &limit=10
  &session_id=...
→ {
    "suggestions": [
      {"type":"query","text":"wireless earbuds","score":0.91},
      {"type":"brand","text":"Sony","id":"BRAND_..."},
      {"type":"asin","asin":"B0...","title":"...","image":"..."},
      {"type":"sponsored_query","text":"...","ad_id":"..."}  // optional, labeled
    ],
    "debug": {"index_version":"...", "cache":"HIT"}  // internal only
  }
```

### 3.5 Data model (simplified)

```text
SuggestionCandidate: type, text|entity_id, score, features{}
PrefixPosting: prefix → topK[(candidate_id, score)]
EntityOverlay: entity_id, title, image, status, department
QueryStats: query, marketplace, impressions, clicks, purchases, window
SafetyRule: pattern|model, action, marketplace_scope
IndexArtifact: version, marketplace, shard_plan, checksum
PersonalizationProfile: customer_id → recent_queries[], affinity_hashes[]
```

### 3.6 Options & tradeoffs

| Decision | Options | Choose | Why | Deal-breaker |
|----------|---------|--------|-----|--------------|
| Live SQL on keystroke | DB vs memory index | **Memory FST/trie** | p99 | DB → miss SLO |
| One global index | Global vs marketplace cells | **Marketplace cells** | Policy/catalog | Leakage + memory blowups |
| Heavy DNN online | Full model vs light re-rank | **Light re-rank** | Cost/latency | DNN@2M QPS → $$$ |
| Exact trie only | Exact vs fuzzy | **Exact + budgeted fuzzy** | Typos matter | Fuzzy always → CPU melt |
| Sponsored mixed unlabeled | Mix vs labeled slot | **Labeled / policy** | Trust | Unlabeled ads → trust incident |
| Rebuild only daily | Daily vs +nearline | **Daily + nearline** | Deals/virality | Daily-only → stale Prime Day |

### 3.7 Ranking sketch

```text
score = w1*log(pop) + w2*CTR + w3*CVR_proxy + w4*freshness
      + w5*department_match + w6*personal_recent_boost
      - diversify_penalty(near_dup)
      - safety_reject
```

Offline learns weights; online applies thin boosts only.

### 3.8 High-level component trade-offs summary

- **Read path** optimized for p99; **learn path** eventually consistent.  
- **Head** at edge; **tail** on shards; **fuzzy** optional.  
- **Safety** after candidates, before response—never skip on cache hit without embedding filter result in cached value.

---

## 4. Architecture Diagram

### 4.1 Overview

```text
                    +------------------+
   Customer App/Web |  Debounce 30ms   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Edge / CDN Cache |  (marketplace, prefix)
                    +--------+---------+
                             | miss
                             v
                    +------------------+
                    | Suggest API / BFF|
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
 +-------------+    +----------------+    +--------------+
 | Hot Prefix  |    | Prefix Shards  |    | Fuzzy (opt)  |
 | Cache Redis |    | FST / Trie TopK|    | Typo Service |
 +-------------+    +--------+-------+    +------+-------+
                             |                   |
                             +---------+---------+
                                       v
                             +-------------------+
                             | Merge + Rank +    |
                             | Diversify + Safety|
                             +---------+---------+
                                       |
                    +------------------+------------------+
                    |                                     |
                    v                                     v
           +----------------+                    +----------------+
           | Entity Overlay |                    | Personalization|
           | Catalog cards  |                    | Recents/affinity|
           +----------------+                    +----------------+
                                       |
                                       v
                                JSON suggestions
                                       |
                                       v (async)
                              +------------------+
                              | Log / Learning   |
                              | → Offline Builder|
                              +------------------+
```

### 4.2 Index build pipeline

```text
Clickstream → Aggregate (marketplace, query) → Score job
     → Prune rare / PII → Build FST shards → Validate
     → Canary 1% → Bake → Full deploy → Keep N versions rollback
```

### 4.3 Suggest sequence (happy path)

```text
Client -> Edge: GET /suggest?q=wire
Edge HIT? yes -> return
Edge MISS -> API -> Redis HIT? yes -> rank/safety -> return
Redis MISS -> Shard(prefix) -> candidates
          -> Entity hydrate (batch)
          -> Personalize boost
          -> Safety
          -> fill Redis + Edge (TTL by prefix length)
          -> return
```

### 4.4 Failure / degradation

```text
Shard timeout → serve Redis/Edge stale + reduce K
Safety service down → fail-closed on high-risk categories; fail-open head with embedded static blocklist
Personalization down → global rank only
Nearline down → daily index only (accept staleness)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Never return suggestions without safety evaluation** (cached entries must include safety verdict + policy version).  
2. **Marketplace isolation:** no cross-marketplace candidate leakage.  
3. **Last-good index:** deploy is blue/green; rollback < minutes.  
4. **Idempotent logging** with impression_id.  
5. **Degrade quality before availability** of empty box—prefer slightly stale over 5xx.

### 5.2 Scalability

**Sharding key:** `hash(marketplace_id + normalize(prefix)[:N])` or range by prefix byte.  
**Hot keys:** first characters (`a`, `i`, `p`) → replicate hot shards; edge TTL short.  
**Prefix length strategy:**

| Len | Strategy |
|-----|----------|
| 0 | Trending lists |
| 1–2 | Fully precomputed + edge |
| 3–5 | Hot cache + shards |
| 6+ | Shards; smaller posting lists |

**Compression:** FST, varint postings, front-coding.  
**Cells:** per marketplace or marketplace group.

### 5.3 Maintainability

- Index artifact schema versioned.  
- Ranker feature flags.  
- Clear ownership: Suggest Oncall vs Search Ranking (SERP) vs Ads.  
- Dashboards: p99, cache hit, safety block rate, empty rate, CTR@K.

### 5.4 Typo tolerance

1. Normalize: lower, NFKC, strip punct, map confusables.  
2. Synonym / rewrite table (`tv` ↔ `television`) offline.  
3. Fuzzy: symmetric delete / BK-tree for common misspellings constrained to dictionary.  
4. Budget: only if exact candidates < K or confidence low; cap CPU.

### 5.5 Personalization (thin)

- Client sends recent queries (hashed) or server fetches thin profile (cached).  
- Boost overlap with candidate set—**do not** retrieve personalized corpus from scratch online.  
- Privacy: profile TTLs; no raw sensitive strings in logs.

### 5.6 Safety & privacy

- Blocklists + embedding NSFW/illegal classifiers.  
- Aggregation threshold: query must appear from ≥ k distinct customers before indexable.  
- Strip emails/phone patterns from suggestions.  
- Adult marketplace rules vary by marketplace—policy packs.

### 5.7 Consistency

- Suggest is **eventually consistent** with popularity.  
- Entity status (OOS) refreshed nearline; tolerate short staleness.  
- Sponsored slot consistency owned by Ads with separate SLA.

### 5.8 Progressive scale deep dive

**10×:** Add edge; split hot shards; sample logs.  
**100×:** Marketplace cells; client head dict; hierarchical FST.  
**1,000×:** On-device models for head; server long-tail + personalization only; aggressive sampling.

### 5.9 Amazon ownership & org themes

- Two-pizza team owns Suggest Serving + Index Deploy.  
- Written ops: “index freshness > 6h” pages.  
- Cost review: RAM $/QPS as first-class metric.  
- PR/FAQ: how organic vs sponsored separated.

### 5.10 Failure injection drills

| Inject | Expect |
|--------|--------|
| Kill one shard | Consistent-hash remap; partial degrade |
| Redis flush | Edge + shard still serve; thundering herd limiter |
| Bad index push | Canary metrics drop CTR / rise empty → auto rollback |
| Safety false negative | Shadow eval + kill switch |

---

## 6. Wrap-Up

### 6.1 What we designed

Amazon retail **search autocomplete**: multi-entity top-K suggest with memory-sharded prefix indexes, edge/hot caches, budgeted fuzzy, thin personalization, non-bypassable safety, offline+nearline learning, progressive scale.

### 6.2 Key decisions worth defending

1. Memory FST/trie, not DB-on-keystroke.  
2. Marketplace cells + isolation.  
3. Thin online rank; heavy learning offline.  
4. Safety embedded in cache entries.  
5. Head at edge/client; tail on server.  
6. Clear organic vs sponsored separation.

### 6.3 Risks & follow-ups

- Memory cost growth with catalog/query diversity.  
- Adversarial SEO spam queries.  
- Personalization privacy vs gain.  
- Sponsored suggest policy complexity.  
- Cross-locale transliteration.

### 6.4 How to present in 45 minutes

| Time | Topic |
|------|-------|
| 0–5 | Scope vs SERP; requirements |
| 5–10 | Scale + latency budget |
| 10–20 | HLD + diagram |
| 20–35 | Deep dive: sharding, cache, safety, build |
| 35–45 | Tradeoffs, 100×, Q&A traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & scope

''' + qa_block([
("Why not use the full search index for autocomplete?",
 "SERP indexes optimize recall/ranking for full queries, not prefix top-K at multi-million QPS. Autocomplete needs precomputed prefix postings in memory with tiny payloads. Using OpenSearch/solr on each keystroke blows p99 and cost."),
("How do you avoid autocomplete becoming a backdoor for SEO spam?",
 "Aggregation thresholds, click/purchase quality filters, trust scores on contributing sessions, manual/policy blocklists, and demotion of suspicious query clusters in offline scoring."),
("Should suggestions be personalized strongly?",
 "Light personalization on a small candidate set only. Strong private retrieval per keystroke is rarely worth the latency, cost, and privacy risk at Amazon QPS."),
]) + r'''
### 7.2 Latency & caching

''' + qa_block([
("How do you stop thundering herds on cache expiry for prefix `a`?",
 "Stagger TTLs, probabilistic early refresh, request coalescing, replica-local hot sets, and pre-warm top prefixes after deploy."),
("Why cache safety verdicts with suggestions?",
 "If you cache raw candidates and re-run safety only sometimes, a safety outage or bug can leak blocked terms. Embed policy_version + verdict in the cached object; invalidate on policy bump."),
("Client-side dictionary: when is it worth it?",
 "For len≤2 and marketplace head terms, client dicts cut server QPS dramatically. Keep them small, versioned, and marketplace-specific; still hit server for personalization/long-tail."),
]) + r'''
### 7.3 Indexing & ranking

''' + qa_block([
("FST vs trie vs inverted index?",
 "FST/succinct tries shine for prefix→topK with great compression. Inverted indexes are better for full-text SERP. Naïve pointer tries waste RAM at Amazon scale."),
("How do you diversify suggestions?",
 "Cluster by stem/intent; MMR-style penalty; mix entity types (query/brand/ASIN); department constraints."),
("How fast must viral queries appear?",
 "Product choice: minutes for celebrity/deal spikes via nearline velocity detectors; hours OK for ordinary drift. Call the SLO explicitly."),
]) + r'''
### 7.4 Typos & languages

''' + qa_block([
("How do you handle typos without melting CPU?",
 "Normalize first; apply fuzzy only when exact is weak; restrict fuzzy dictionary to head terms; precompute common misspelling maps offline."),
("Multi-language marketplaces?",
 "Separate indexes or segments per locale; don’t mix JP and DE postings. Tokenization differs (CJK)."),
]) + r'''
### 7.5 Privacy, safety, ads

''' + qa_block([
("How do you prevent rare personal queries from becoming suggestions?",
 "k-anonymity / distinct-customer thresholds, PII regex detectors, and human review for borderline sensitive categories."),
("How should sponsored suggestions work?",
 "Separate candidate source + auction; hard labels in UI; reserve organic slots; relevance threshold so bad ads don’t dominate."),
("Fail open or closed on safety outage?",
 "Category-dependent: fail closed for regulated/adult; for benign head, static embedded blocklist fail-open. Never silent empty without metrics."),
]) + r'''
### 7.6 Multi-region & scale

''' + qa_block([
("Active-active across regions?",
 "Serve regionally near customers; indexes built per marketplace home region; replicate artifacts. Avoid cross-region on keystroke."),
("What breaks at 100×?",
 "Hot prefixes, log volume, memory footprint, and personalization fanout. Answer with cells, edge, sampling, client head dicts."),
]) + r'''
### 7.7 Operations

''' + qa_block([
("How do you roll out a bad ranker safely?",
 "Shadow traffic, canary on CTR/empty/p99, automatic rollback, versioned artifacts."),
("Who pages at 3am?",
 "Suggest Serving owns p99/availability; Ranking Science owns offline score quality with next-day analysis—don’t blur."),
]) + r'''
### 7.8 Comparison traps

''' + qa_block([
("Is this the same as Google autocomplete?",
 "Similar mechanics, different entities (ASINs, deals), marketplace isolation, and shopping conversion objectives."),
("Can LLMs replace the prefix index?",
 "Not as the sole online path at Amazon QPS today. LLMs may rewrite/rerank tiny candidate sets or help offline query understanding."),
]) + r'''
### 7.9 Failure injection

''' + qa_block([
("Redis is flushed—what happens?",
 "Shards serve; coalescing prevents herd; edge still hot; expect p99 bump; page on hit-rate cliff."),
("Catalog says ASIN suppressed—how fast?",
 "Nearline entity status invalidation; short TTL on entity cards; critical takedowns push kill-list to edge."),
]) + r'''
### 7.10 Extra interviewer traps (high value)

''' + qa_block([
("What’s your deal-breaker design?",
 "Querying a data warehouse or SERP cluster synchronously on every keystroke."),
("How do you measure success?",
 "Suggest CTR, reformulation rate, time-to-first result click, purchase attribution, p99, safety incidents, RAM $/QPS."),
("How does this interact with Alexa or Fire TV search?",
 "Shared candidate pipelines possible; different latency/UX K and modality features; don’t couple deploy freights naïvely."),
]) + r'''
---

## 8. Appendices

### Appendix A — Example schemas

```json
{
  "suggestion": {
    "type": "query|asin|brand|category|sponsored_query",
    "text": "wireless earbuds",
    "entity_id": "optional",
    "score": 0.91,
    "attrs": {"department": "electronics", "in_stock": true}
  }
}
```

```text
PrefixShardRequest { marketplace, locale, prefix, limit, dept? }
PrefixShardResponse { candidates[], index_version, leaf_stats }
```

### Appendix B — Normalization pipeline

```text
raw → unicode NFKC → lower → map confusables → strip excess punct
    → collapse whitespace → tokenize marketplace-specific → prefix keys
```

### Appendix C — Scale checklist

| Checkpoint | Base | 10× | 100× |
|------------|------|-----|------|
| Edge cache | optional | required | required |
| Shard count | tens | hundreds | cells |
| Log sampling | light | medium | heavy |
| Client dict | no | maybe | yes |
| Nearline | yes | yes | hierarchical |

### Appendix D — Glossary

| Term | Meaning |
|------|---------|
| FST | Finite state transducer — compressed prefix map |
| Posting | prefix → top-K candidates |
| Nearline | minutes-latency updater |
| Marketplace cell | isolated serving unit for a retail marketplace |
| Organic vs sponsored | unpaid vs paid suggestion inventory |

### Appendix E — Estimation cheat-sheet

```text
QPS_eff = QPS × (1 - edge_hit) × (1 - redis_hit)
RAM ≈ sum(compressed_shard) + redis + entity_cache
Egress ≈ QPS × response_bytes
```

### Appendix F — Interview closer checklist

- [ ] Scoped vs SERP  
- [ ] Latency budget numbers  
- [ ] Split planes (read vs learn)  
- [ ] Marketplace isolation  
- [ ] Safety non-bypassable  
- [ ] Progressive scale story  
- [ ] Ownership / pager  

### Appendix G — Sample rank features

| Feature | Plane |
|---------|-------|
| log(query_count_7d) | Offline |
| CTR_suggest_7d | Offline |
| purchase_rate_14d | Offline |
| is_deal_active | Nearline |
| department_match | Online |
| recent_query_boost | Online |
| oos_penalty | Online/nearline |

### Appendix H — Runbook snippets

**High p99:** check shard CPU, redis hit, edge hit, fuzzy rate, GC.  
**Bad suggestions:** freeze nearline, rollback index_version, enable kill-list.  
**Safety incident:** push emergency blocklist to edge; invalidate cache by policy_version.

### Appendix I — Related Amazon systems

- A9 / OpenSearch SERP (downstream of accepted suggestion)  
- Catalog service (entity cards)  
- Ads suggest (sponsored)  
- Clickstream platform  
- Policy / Trust & Safety

### Appendix J — Mock capacity plan (US marketplace)

| Tier | Nodes | RAM each | Notes |
|------|-------|----------|-------|
| Edge | CDN | — | head prefixes |
| Redis | 20 | 64 GB | hot prefixes |
| Shards | 60 | 128 GB | FST + postings |
| API | 40 | 16 GB | stateless |
| Fuzzy | 10 | 64 GB | budgeted |

---

*End of document — Amazon Search Autocomplete / Typeahead (SDE III)*
'''

Path("/tmp/doc1_len.txt").write_text(str(len(DOC1.splitlines())))
print("doc1 lines", len(DOC1.splitlines()))
# Continue in same script - write remaining docs as separate string builds
# For manageability, import from sibling modules if present; else define inline below.
'''
# placeholder end marker for part1 - actual file continues
'''

print("part1 scaffold loaded")
PY