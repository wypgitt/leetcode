# System Design: Search Autocomplete / Typeahead (Amazon Retail)

> **Focus areas:** Prefix indexes / FST · Top-K ranking · Hot-prefix cache · Typo tolerance · Personalization · p99 latency · Offline→online · Safety/PII · Marketplace isolation
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Explicit latency budget, split suggest-read vs log-learn planes, deal-breakers for “query warehouse on each keystroke”
> **Interview theme:** Amazon SDE III / L6 — **Search & Discovery** ownership for Amazon.com typeahead under extreme QPS with customer trust, marketplace fairness, and operational accountability

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

Goal: **bound the product**—an Amazon **search autocomplete / typeahead** service that returns top-K suggestions (queries, ASINs, brands, categories, deals) as the customer types, with ranking, light personalization, typo tolerance, safety filtering, and strict latency (p99 tens of ms).

### 1.0 What this is / is not

| Dimension | **Autocomplete (this doc)** | Not this |
|-----------|-----------------------------|----------|
| Primary job | Prefix → ranked suggestions fast | Full SERP / A9 ranking |
| Success | Relevant, safe, shoppable; tight p99 | Perfect semantic NLP MVP |
| Index | Prefix structures + scores + entity overlays | Live scan of warehouse each keystroke |
| Personalization | Re-rank small candidate set | Heavy private DNN per keystroke at 100M QPS |
| Amazon lens | Conversion, discovery, seller fairness, cost/QPS | Academic IR paper alone |

**Scope statement:** Design Amazon retail search autocomplete: sharded prefix serving, multi-entity suggestions, ranking, hot-prefix cache, typos, light personalization, safety—with progressive scale and clear ownership vs SERP.

### 1.1 Functional Requirements

| # | Question | Typical answer | Design implication |
|---|----------|----------------|--------------------|
| F1 | Suggest what? | Queries, ASINs, brands, categories; optional deals | Typed candidates |
| F2 | Top-K? | 8–10 UI; compute 30–80 | Truncate after rank + diversify |
| F3 | Ranking? | Popularity, CTR, CVR, freshness, department | Offline score + online boosts |
| F4 | Personalization? | Recents + locale/marketplace + light affinity | Thin profile re-rank |
| F5 | Typos? | Yes len≥3, 1-edit common | Budgeted fuzzy layer |
| F6 | Marketplaces? | Multi-marketplace | Partition by marketplace_id |
| F7 | Safety? | Block NSFW, hate, PII, illegal | Non-bypassable filter |
| F8 | Freshness? | Viral/deal in minutes–hours | Nearline delta |
| F9 | Empty prefix? | Trending / seasonal | Separate lists |
| F10 | Analytics? | Impression/click/purchase | Async learning |
| F11 | Client cache? | First-char / session | Hybrid edge/client |
| F12 | Auth modes? | Logged-in + logged-out | Two rank modes |
| F13 | Sponsored? | Optional labeled slot | Separate ads path |
| F14 | Fire TV / Alexa search box? | Same family, different K | Shared candidates |
| F15 | OOS / suppressed ASIN? | Filter or demote | Entity status join |

**MVP scope:**

1. `GET /suggest` → ranked multi-entity suggestions.
2. Offline prefix index from logs + scores + overlays.
3. Online memory shards + hot-prefix cache.
4. Typo tolerance (normalize + common fuzzy).
5. Personalization: recent queries + marketplace/locale.
6. Safety/blocklist on serve path.
7. Async impression/click/purchase logging.
8. Nearline path for spikes/deals.
9. Diversify near-duplicate strings.

**Out of MVP:** LLM-only decode per keystroke; deep vector suggest without candidates; full ads stack; replacing SERP.

### 1.2 Non-Functional Requirements

| # | Question | Target |
|---|----------|--------|
| N1 | Latency | **p99 < 40–50ms** in-region |
| N2 | Availability | 99.99%; stale OK |
| N3 | Throughput | Millions+ QPS via cache/edge |
| N4 | Freshness | Minutes–hours |
| N5 | Consistency | Eventual with logs |
| N6 | Cost | Shard + compression + prune |
| N7 | Privacy | Aggregation thresholds |
| N8 | Safety | Filter non-bypassable |
| N9 | Multi-AZ | Region-local serve |
| N10 | Ownership | Suggest vs SERP vs Ads pager split |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths:** `wirel` → wireless earbuds + brand + ASIN; `iphon` fuzzy → iphone case; recent boost; deal nearline; empty → trending; department-scoped Books.

| Case | Behavior |
|------|----------|
| Prefix length 1 | Precomputed head only; hard cap |
| Rare PII-like query | Never suggest; k-threshold |
| OOS ASIN | Suppress/demote |
| Bot storms | Edge rate limit + cache |
| Index lag | Last-good + nearline |
| Marketplace mismatch | Hard isolation |
| Sponsored-only | Forbidden |
| Prime Day spike | Capacity reserve + hot cache |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Suggest QPS peak | 2M | 20M | 200M | 2B |
| Index queries | 50M | 100M | 200M | pruned |
| Entity overlays | 100M | 200M | 500M | hierarchical |
| Cache hit rate | 70% | 80% | 90% | 95%+ |
| Log events/day | 20B | 200B | 2T | sampled |
| p99 | 50ms | 50ms | 40ms | 30ms edge |

**Jumps:** 10× edge + shard split; 100× marketplace cells + client head dict; 1,000× on-device head + server long-tail.

### 1.5 Etc. (Constraints & Assumptions)

- Autocomplete ≠ SERP; never query warehouse on keystroke.
- Customer trust > vanity CTR (safety/privacy).
- Seller fairness: organic ≠ silent pay-to-play.
- Ownership: Suggest owns latency/safety merge; Ads owns sponsored slot.

**Repeat-back scope:** Amazon retail autocomplete with multi-entity top-K, sharded prefix indexes, caches, typos, thin personalization, safety, nearline freshness, progressive scale—distinct from SERP.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| A | Suggest read | 2M QPS | Online |
| B | Hot-prefix cache | ~1.4M hits | Online |
| C | Shard trie fanout | ~600K | Online |
| D | Log ingest | 50–100K/s | Streaming |
| E | Offline build | Daily + hourly | Offline |
| F | Nearline spikes | Bursty | Nearline |

**Tip:** Never quote one QPS—split suggest/cache/shard/logs/build.

### 2.2 Latency budget

| Step | Budget |
|------|--------|
| Edge / gateway | 2–5 ms |
| Marketplace resolve | 1–3 ms |
| Hot-prefix cache | 1–5 ms |
| Shard lookup + merge | 5–15 ms |
| Rank / diversify / personalize | 3–10 ms |
| Safety | 1–3 ms |
| **Total p99** | **≤ 40–50 ms** |

### 2.3 Memory math (US marketplace cell)

| Structure | Assumption | Size |
|-----------|------------|------|
| Compressed FST/trie | 50M queries | 200–800 GB sharded |
| Entity overlay | 100M lightweight | 50–150 GB |
| Hot-prefix Redis | 10M × 1 KB | ~10 GB/region |

Prefer **FST / succinct trie** over pointer-heavy tries.

### 2.4 Bandwidth & cost

- 2M QPS × 1 KB ≈ 2 GB/s egress before edge—hence CDN.
- Sample impressions; keep clicks/purchases denser for training.
- +10% cache hit ≫ buying more shard CPU.

### 2.5 Scale jump math

| Jump | QPS | Reality |
|------|-----|---------|
| Base | 2M | Memory shards + cache |
| 10× | 20M | Edge + cells |
| 100× | 200M | Client head dict |
| 1,000× | 2B | On-device head; server long-tail |

### 2.6 Prefix length economics

| Len | % traffic (illustrative) | Strategy |
|-----|--------------------------|----------|
| 0–1 | High | Fully precomputed + edge |
| 2–3 | High | Redis + shards |
| 4–6 | Medium | Shards |
| 7+ | Lower QPS, longer lists smaller | Shards + early exit |

---

## 3. High-Level Design

### 3.1 Design goals

1. Latency first (instant box).
2. Customer trust (safety + privacy).
3. Discovery & conversion (shoppable suggestions).
4. Clear ownership vs SERP/Ads/Catalog.
5. Cost control (RAM + egress).
6. Operability (freshness SLO, canary, rollback).

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Suggest API / BFF | Auth, marketplace, response shaping |
| Edge / CDN | Hot prefixes |
| Hot-prefix Redis | Regional L2 |
| Prefix Shard Service | In-memory FST top-K |
| Fuzzy / Typo Service | Budgeted edit-distance |
| Entity Overlay | ASIN/brand/category cards |
| Lightweight Ranker | Merge, score, diversify |
| Personalization | Recents / affinity boosts |
| Safety Filter | Blocklist + classifiers |
| Log Pipeline | Learning signals |
| Offline Builder | Artifacts |
| Nearline Updater | Spikes / deals |

### 3.3 Primary flows

**Keystroke:** debounce → edge → redis → shards → merge/rank/diversify/safety → respond → async log.

**Offline learn:** clickstream → aggregate → scores → prune PII/rare → build FST → canary → deploy.

**Nearline spike:** velocity detector → patch hot cache + side postings → decay TTL.

### 3.4 API sketch

```text
GET /v1/suggest?q=wirel&marketplace=ATVPDKIKX0DER&locale=en_US&limit=10
→ { suggestions: [ {type, text|asin, score, attrs...} ], index_version }
```

### 3.5 Data model

```text
PrefixPosting: prefix → topK[(candidate_id, score)]
EntityOverlay: entity_id, title, image, status, department
QueryStats: query, marketplace, imps, clicks, purchases, window
SafetyRule: pattern|model, action, scope
IndexArtifact: version, marketplace, shard_plan, checksum
Profile: customer_id → recent_queries[], affinity_hashes[]
```

### 3.6 Options & tradeoffs

| Decision | Choose | Why | Deal-breaker alt |
|----------|--------|-----|------------------|
| Store | Memory FST | p99 | Live SQL |
| Isolation | Marketplace cells | policy/catalog | One global index |
| Rank | Light online re-rank | cost | Heavy DNN every keystroke |
| Typos | Exact + budgeted fuzzy | CPU | Fuzzy always |
| Ads | Labeled slot | trust | Unlabeled mix |
| Freshness | Daily + nearline | deals | Daily only |

### 3.7 Ranking sketch

```text
score = w1*log(pop) + w2*CTR + w3*CVR_proxy + w4*fresh
      + w5*dept_match + w6*recent_boost - diversify_penalty
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
App/Web --debounce--> Edge/CDN Cache --miss--> Suggest API
     |                                         |
     |                         +---------------+---------------+
     |                         v               v               v
     |                   Hot Prefix      Prefix Shards     Fuzzy(opt)
     |                     Redis           FST/Trie
     |                         \             |             /
     |                          \            v            /
     |                           Merge + Rank + Diversify + Safety
     |                                    |
     |                     +--------------+--------------+
     |                     v                             v
     |               Entity Overlay                Personalization
     |                     \                             /
     |                      +----------- JSON -----------+
     v (async)
  Log/Learning --> Offline Builder --> Canary Deploy
```

### 4.2 Index build

```text
Clickstream → Aggregate → Score → Prune → Build shards → Validate
           → Canary 1% → Bake → Full → Keep N rollbacks
```

### 4.3 Degradation

```text
Shard timeout → stale cache + reduce K
Safety down → fail-closed regulated; static blocklist head
Personalization down → global only
Nearline down → accept daily staleness
```

### 4.4 Multi-marketplace cells

```text
+---------------- US Cell ----------------+
| Edge | Redis | Shards | API | Safety    |
+-----------------------------------------+
+---------------- DE Cell ----------------+
| Edge | Redis | Shards | API | Safety    |
+-----------------------------------------+
         (no cross-cell candidate leak)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. No suggestions without safety evaluation (cache embeds verdict + policy_version).
2. Marketplace isolation hard.
3. Last-good index rollback in minutes.
4. Idempotent impression_id logging.
5. Prefer slightly stale over empty/5xx for the search box.

### 5.2 Scalability

**Shard key:** hash(marketplace + normalize(prefix)[:N]) or prefix ranges.

**Hot keys:** replicate first-character shards; short edge TTL; coalescing.

| Len | Strategy |
|-----|----------|
| 0 | Trending |
| 1–2 | Precomputed + edge |
| 3–5 | Redis + shards |
| 6+ | Shards; smaller lists |

Compression: FST, varints, front-coding. Cells per marketplace.

### 5.3 Maintainability

Versioned artifacts; feature flags; dashboards for p99, hit rate, safety blocks, empty rate, CTR@K; clear ownership docs.

### 5.4 Typo tolerance

Normalize NFKC → synonyms offline → fuzzy only if exact weak → CPU cap.

### 5.5 Personalization

Boost within candidate set only; profile TTLs; no raw sensitive strings in logs.

### 5.6 Safety & privacy

Blocklists + classifiers; k-anonymity for index inclusion; PII regex; marketplace policy packs.

### 5.7 Consistency

Eventually consistent popularity; entity OOS nearline; ads separate SLA.

### 5.8 Progressive scale

10× edge; 100× cells + client dict; 1,000× on-device head.

### 5.9 Ownership themes

Two-pizza Suggest Serving; RAM $/QPS metric; organic vs sponsored FAQ; index freshness pages.

### 5.10 Failure drills

| Inject | Expect |
|--------|--------|
| Kill shard | Remap; partial degrade |
| Redis flush | Edge+shard; herd limiter |
| Bad index | Canary rollback |
| Safety FN | Kill-list + invalidate |

### 5.11 Sponsored suggest (thin)

Separate candidate source; relevance floor; labeled UI; never replace all organic; Ads owns auction; Suggest owns merge position policy.

### 5.12 Observability

Traces on miss path; metrics: `suggest_p99`, `cache_hit`, `fuzzy_rate`, `safety_block_rate`, `empty_rate`, `ctr_at_k`, `index_age_seconds`.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        Amazon retail **search autocomplete**: multi-entity top-K suggest with memory-sharded prefix indexes, edge/hot caches, budgeted fuzzy, thin personalization, non-bypassable safety, offline+nearline learning, progressive scale.

        ### 6.2 Key decisions worth defending

        1. Memory FST/trie, not DB-on-keystroke
2. Marketplace cells + isolation
3. Thin online rank; heavy learning offline
4. Safety embedded in cache entries
5. Head at edge/client; tail on server
6. Clear organic vs sponsored separation

        ### 6.3 Risks & follow-ups

        - Memory cost vs query diversity
- Adversarial SEO spam
- Personalization privacy vs lift
- Sponsored policy complexity
- Cross-locale transliteration

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, Amazon ownership lens |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive (reliability, scale, ML/ops) |
        | 35–45 | Tradeoffs, failure modes, interviewer Q&A |

        ### 6.5 One-sentence closer

        > We designed **Amazon Search Autocomplete** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer trust while controlling cost and operational load.

        ---

## 7. Deeper / Related Interview Questions

### 7.1 Product & scope

**Q1. Why not use the full search index for autocomplete?**

**A:** SERP optimizes recall for full queries, not prefix top-K at multi-million QPS. Autocomplete needs precomputed prefix postings in memory. Hitting OpenSearch each keystroke blows p99 and cost.

**Q2. How do you stop SEO spam from polluting suggestions?**

**A:** k-thresholds, click/purchase quality filters, session trust scores, blocklists, and demotion of suspicious clusters in offline scoring.

**Q3. Strong personalization per keystroke?**

**A:** No—light re-rank of a small candidate set. Private retrieval every keystroke loses on latency, cost, and privacy at Amazon QPS.

### 7.2 Latency & caching

**Q4. Thundering herd on prefix `a` expiry?**

**A:** Stagger TTLs, probabilistic early refresh, request coalescing, pre-warm after deploy.

**Q5. Why embed safety in cache entries?**

**A:** Cached raw candidates + best-effort safety can leak blocked terms during outages. Store verdict + policy_version; invalidate on policy bump.

**Q6. When is client dictionary worth it?**

**A:** Len≤2 head terms cut server QPS a lot. Versioned, marketplace-specific; server still handles long-tail/personalization.

### 7.3 Indexing & ranking

**Q7. FST vs trie vs inverted index?**

**A:** FST for compressed prefix→topK; inverted for SERP; naïve tries waste RAM.

**Q8. How to diversify?**

**A:** Stem/intent clusters, MMR penalty, mix entity types, department constraints.

**Q9. Viral query freshness SLO?**

**A:** Minutes for celebrity/deal spikes via nearline; hours OK for ordinary drift—state the SLO.

### 7.4 Typos, privacy, ads, ops

**Q10. Typos without melting CPU?**

**A:** Normalize; fuzzy only when exact weak; dictionary-limited; precomputed misspelling maps.

**Q11. Prevent rare personal queries becoming suggestions?**

**A:** Distinct-customer thresholds, PII detectors, category review.

**Q12. Sponsored suggestions?**

**A:** Separate auction, UI labels, organic floor, relevance threshold.

**Q13. Who pages at 3am?**

**A:** Suggest Serving owns p99/availability; Ranking Science owns offline score quality next day.

**Q14. Deal-breaker design?**

**A:** Synchronously querying a warehouse or SERP cluster on every keystroke.

**Q15. Success metrics?**

**A:** CTR@K, reformulation rate, time-to-click, purchase attribution, p99, safety incidents, RAM$/QPS.

### 7.5 Extra traps

**Q16. LLMs replace prefix index?**

**A:** Not as sole online path at Amazon QPS. Maybe offline understanding or tiny-set rewrite.

**Q17. Active-active across regions?**

**A:** Serve near customers; build per marketplace home; no cross-region keystroke dependency.

**Q18. Catalog emergency suppress?**

**A:** Push kill-list to edge; invalidate entity cards; nearline status.

**Q19. How related to Alexa search?**

**A:** Shared candidate pipelines possible; different modality/latency; don’t couple freights blindly.

---

        ## 8. Appendices

        ### Appendix A — Glossary (shared Amazon interview terms)

        | Term | Meaning |
        |------|---------|
        | Two-pizza team | Small ownership team with pager + roadmap |
        | Cell | Failure-isolated serving shard (marketplace/region/game) |
        | Nearline | Minutes-latency processing between online and batch |
        | Shadow deploy | New model/path scores without affecting users |
        | Canary | Small % traffic exposure before full bake |
        | Deal-breaker | Design choice that fails SLO/trust/cost non-negotiables |
        | Progressive scale | Explicit 10× / 100× / 1,000× architecture jumps |

        ### Appendix B — Estimation cheat-sheet

        ```text
        QPS_peak ≈ DAU × sessions/day × actions/session / 86400 × peak_factor
        Storage ≈ rows/day × bytes × retention_days
        Fanout_cost ≈ QPS × deps_per_request × p99_dep_latency
        ```

        ### Appendix C — Oncall checklist

        - [ ] SLOs green (latency, availability, freshness, error budget)
        - [ ] Canary/auto-rollback armed
        - [ ] Kill switches documented
        - [ ] Dependency blast radius known
        - [ ] Cost dashboards linked
        - [ ] Privacy/safety non-bypassable paths tested

        ### Appendix D — Failure-injection matrix (generic)

        | Inject | Expect |
        |--------|--------|
        | Kill one AZ | Cell continues; elevated latency OK within SLO |
        | Cache flush | Coalescing + serve from origin; no thundering herd melt |
        | Model/registry outage | Fallback model or rules; no 100% empty UX |
        | Poison deploy | Canary catches; auto rollback |
        | Dependency timeout | Bulkheads + deadlines; degrade mode |

        ### Appendix E — Leadership principles mapping (use sparingly)

        | LP | Design signal |
        |----|---------------|
        | Customer Obsession | Trust, latency, correct UX under failure |
        | Ownership | Clear pager boundaries; no orphan data plane |
        | Dive Deep | Correct QPS math; explicit invariants |
        | Frugality | Cost per request / per recommendation as metric |
        | Bias for Action | Kill switches, canaries, nearline patches |
        | Insist on Highest Standards | Safety/privacy non-bypassable |

        ### Appendix F — Sample schemas

```json
{
  "type": "query|asin|brand|category|sponsored_query",
  "text": "wireless earbuds",
  "score": 0.91,
  "attrs": {"department": "electronics", "in_stock": true}
}
```

### Appendix G — Normalization

```text
raw → NFKC → lower → confusables → punct → whitespace → locale tokens → prefixes
```

### Appendix H — Mock US capacity

| Tier | Nodes | RAM | Notes |
|------|-------|-----|-------|
| Redis | 20 | 64 GB | hot prefixes |
| Shards | 60 | 128 GB | FST |
| API | 40 | 16 GB | stateless |
| Fuzzy | 10 | 64 GB | budgeted |

### Appendix I — Related systems

SERP/OpenSearch, Catalog, Ads Suggest, Clickstream, Trust & Safety policy packs.

### Appendix J — Runbooks

**High p99:** shard CPU, redis/edge hit, fuzzy rate, GC.
**Bad suggestions:** freeze nearline, rollback index_version, kill-list.
**Safety incident:** emergency blocklist to edge; invalidate by policy_version.

### Appendix K — Rank features

| Feature | Plane |
|---------|-------|
| log(query_count_7d) | Offline |
| CTR_suggest_7d | Offline |
| purchase_rate_14d | Offline |
| is_deal_active | Nearline |
| department_match | Online |
| recent_query_boost | Online |

### Appendix L — Interview closer checklist

- [ ] Scoped vs SERP
- [ ] Latency budget numbers
- [ ] Split planes
- [ ] Marketplace isolation
- [ ] Safety non-bypassable
- [ ] Progressive scale
- [ ] Ownership / pager


## Extended Notes (Interview Gold)

### E1. Why autocomplete is a different service from SERP

Interviewers sometimes push “just call search with a wildcard.” Defend with: (1) QPS multiplier from keystrokes, (2) tiny payload/top-K vs document retrieval, (3) different relevance objective (predict next query / entity), (4) memory locality, (5) failure isolation—SERP outage shouldn’t blank the typeahead if cached.

### E2. Prefix posting list maintenance

Each prefix stores a bounded heap of size M (e.g. 50). On offline build, compute global scores then push into heaps. For nearline inserts, push into a side structure merged at read with a freshness boost, then compact on next build. This avoids rewriting entire FSTs every minute.

### E3. Encoding tricks

- Front-code shared prefixes inside blocks.
- Quantize scores to 8–16 bits.
- Store entity ids as delta varints.
- Keep display strings in a separate dictionary keyed by id to avoid duplicating “iphone 16 case” across prefixes.

### E4. Personalization privacy modes

| Mode | Mechanism |
|------|-----------|
| Logged-out | Marketplace + device local recents only |
| Logged-in light | Server profile hashes, short TTL |
| Strict marketplace | Disable cross-category affinity |

### E5. Abuse & bots

Bots inflate popularity. Use trusted-session weights, purchase confirmation, device reputation, and downweight headless patterns in offline aggregation—not only online rate limits.

### E6. Empty-result UX

Prefer low-confidence fuzzy / category browse chips over zero suggestions. Track `empty_rate` as a customer-experience SLO, not only infrastructure p99.

### E7. Multi-department ambiguous prefixes

For `apple`, mix brand + fruit grocery carefully using department context, user affinity, and diversity. Hard-coding one winner feels broken seasonally (Apple events vs produce).

### E8. Consistency with voice

If Alexa and retail web share rewrite dictionaries, version them independently; voice ASR errors differ from keyboard typos.

### E9. Cost narrative for L6

Bring a unit metric: **USD per million suggests**. Show how edge hit-rate and client dict move that number. Leadership likes frugality grounded in math.

### E10. Rollout of new entity type (e.g., “stores”)

Feature-flag entity type in merge; start shadow; measure CTR; gated marketplace launch; keep payload schema backward compatible.

### E11. Data retention

Raw keystroke streams are sensitive. Aggregate quickly; retain raw samples briefly for debugging; training uses aggregated counters + sampled events.

### E12. Comparison with Meta-style typeahead

Meta emphasizes people/graph; Amazon emphasizes ASIN/brand/deal commerce entities and marketplace law/policy packs. Say this differentiation early.

### E13. Debugging a bad suggestion live

Tools: prefix explain (candidates + scores + safety), index_version, cache layer provenance, nearline patch presence. Never give attackers full model weights—guard internal tools.

### E14. Load test strategy

Replay production prefix distributions (not uniform alphabet). Hot prefixes dominate; synthetic uniform traffic under-tests cache and over-tests rare shards.

### E15. SLO error budgets

Separate budgets: latency, safety incidents (near zero), privacy leaks (zero), freshness. Don’t burn safety budget for latency wins.

---


## 9. Interview Walkthrough Script (35–45 min)

### 9.1 Opening (2 min)

Restate the problem in Amazon terms: customer impact, ownership boundary, what is explicitly out of scope. Ask clarifying questions from §1 before drawing boxes.

### 9.2 Requirements lock (5 min)

Lock MVP vs out-of-scope. State NFRs as numbers. Mention progressive scale early so the interviewer knows you will not design only for today’s QPS.

### 9.3 Estimation (5 min)

Split load classes. Show latency budget table. Call out the unit-cost metric you will optimize (RAM$/QPS, $/1K inferences, etc.).

### 9.4 HLD + diagram (10 min)

Draw the ASCII architecture. Narrate primary happy path. Name owning teams for each box.

### 9.5 Deep dive (10–12 min)

Pick 2–3 sharp topics: failure modes, consistency, scale jump, privacy/safety. Avoid laundry-listing every component again.

### 9.6 Close (3 min)

Risks, metrics, pager ownership, and the single deal-breaker design you refused.

---

## 10. Metrics, Alarms, and Runbooks

### 10.1 Golden signals

| Signal | Example metrics | Alarm intuition |
|--------|-----------------|-----------------|
| Latency | p50/p99 by endpoint | Burn error budget |
| Traffic | QPS, bytes, fanout | Sudden cliffs/spikes |
| Errors | 5xx, dependency timeouts | Page on rate |
| Saturation | CPU, RAM, queue depth | Predictive scale |
| Freshness | Index/model age | Product SLO |
| Trust | Safety blocks, privacy denials | Near-zero incidents |

### 10.2 Dashboard rows (minimum)

1. Customer-facing SLO panel  
2. Dependency health panel  
3. Data/ML freshness panel  
4. Cost panel  
5. Experiment guardrails panel  

### 10.3 Incident severity guide

| Sev | Example | Response |
|-----|---------|----------|
| SEV-1 | Safety/privacy leak OR total outage of critical path | Immediate war room |
| SEV-2 | Elevated p99 / partial degrade | Page; mitigate via fallback |
| SEV-3 | Stale models / elevated fallback rate | Business hours + ticket |
| SEV-4 | Cosmetic / tooling | Backlog |

### 10.4 Generic rollback ladder

```text
1) Feature flag OFF / kill switch
2) Canary revert / last-good artifact
3) Traffic shed / reduce K / disable optional stage
4) Cell isolation if blast radius regional
5) Postmortem with customer-trust section
```

---

## 11. Consistency, Correctness, and Data Contracts

### 11.1 Contract checklist

- Request/response schema versioned  
- Idempotency keys where writes exist  
- Policy/model/index versions stamped on decisions  
- Point-in-time features for ML training joins  
- Explicit freshness SLOs for nearline  

### 11.2 Poison-pill protection

Bad deploys, bad dictionaries, bad campaigns, bad embeddings: always have shadow → canary → bake → automatic rollback on guardrail breach.

### 11.3 Replay & audit

For trust-impacting systems (ads, safety, leaderboards, recommendations enforcement), keep enough audit to answer: “Why did the customer see X at time T?”

---

## 12. Security & Privacy Baseline (Amazon interview expectation)

| Control | Expectation |
|---------|-------------|
| Authn/z | Service-to-service auth; least privilege |
| PII | Purpose limitation; retention TTLs; access reviews |
| Encryption | In transit everywhere; at rest for stores |
| Tenancy | Marketplace/cell isolation where required |
| Secrets | No secrets in artifacts/logs |
| Abuse | Rate limits, bot controls, fraud hooks |
| Supply chain | Signed model/index/pack artifacts |

---

## 13. Cost & Capacity Planning Worksheet

### 13.1 Questions to answer aloud

1. What is the dominant cost driver (RAM, GPU, egress, human review, CDN)?  
2. What lever moves unit cost fastest (cache hit, candidate budget, sampling)?  
3. What is the 10× cost if you do nothing architectural?  
4. What is the 10× cost after the designed jump?  

### 13.2 Capacity formula templates

```text
online_instances ≈ peak_QPS × cost_per_req_cpu_sec / (cores × util_target)
cache_memory    ≈ hot_keys × bytes_per_key × overhead
train_budget    ≈ samples × epochs × $/GPU-hour
egress_monthly  ≈ QPS_avg × resp_bytes × 2.6e6
```

### 13.3 Frugality narrative

L6 candidates who only chase latency without unit economics miss Amazon’s bar. Tie every luxury (heavy DNN online, exact global rank, unsampled logs) to a cost and a customer benefit.

---

## 14. Progressive Scale Playbook (reuse verbally)

| Jump | Typical moves |
|------|----------------|
| 10× | Caching, shard split, async offload, sampling |
| 100× | Cells, hierarchical aggregation, distilled models, edge |
| 1,000× | On-device/edge intelligence, approximate algorithms, platformization |

Always pair each jump with **what breaks if you only scale vertically**.

---

## 15. Cross-Team Interfaces

Document the APIs you do *not* own but depend on. Interviewers listen for blast-radius thinking.

| Dependency | Failure mode | Your mitigation |
|------------|--------------|-----------------|
| Identity / auth | Outage | Cached tokens / degrade personalization |
| Catalog | Stale/OOS | Nearline status + kill list |
| Feature store | Slow | Budgets + cached features + fallback |
| Ads | Timeout | Organic-only path |
| Experimentation | Mis-assign | Sticky assignment cache |
| Logging | Backpressure | Sample + local buffer |

---


## 16. Additional Deep Q&A — Search Autocomplete

### Q1. How do you keep p99 stable when fuzzy rate spikes?

Cap fuzzy CPU with token bucket per shard; degrade fuzzy first; prefer precomputed misspelling maps; alarm on fuzzy_rate and fuzzy_p99 separately from exact path.

### Q2. How do marketplace launches work?

Bootstrap from catalog titles + translated head queries; start with higher popular-only weights; enable personalization after enough click mass; isolate cell from day one.

### Q3. What belongs in edge vs Redis vs shard?

Edge: ultra-hot short prefixes and trending. Redis: hot medium prefixes with safety embedded. Shards: authoritative compressed postings for long-tail and merges.

### Q4. How do you attribute purchases to suggestions?

Impression_id → click → search → ASIN view → purchase join with time windows; careful with last-click bias; report suggest-assisted GMV as directional.

### Q5. How do you fight suggestion spam farms?

Trusted session weights, purchase confirmation, device reputation, clustering of near-duplicate queries, manual/policy ops tools, and delayed admission to index.

### Q6. Canary metrics that matter?

CTR@K, empty_rate, reformulation_rate, p99, safety_block_rate, RAM, and complaint tickets. Auto rollback if CTR drops and empty_rate rises together.

### Q7. How do you version safety policy with cache?

Include policy_version in cache key or payload; bumping policy invalidates logically; eager purge for emergency blocklists via edge kill-list.

### Q8. Department-scoped suggest vs global?

If user is in Books, bias strongly but keep a small global escape hatch so they can still reach ‘book light’ electronics; product decision—state it.

### Q9. Unicode / homoglyph attacks?

NFKC normalization, confusable mapping, and safety on normalized form; store display text separately from match key.

### Q10. How is this different from OpenSearch completion suggester?

Managed suggesters are fine for smaller apps; Amazon scale needs custom sharding, marketplace policy packs, entity overlays, and cost/ownership controls.

## 17. Scenario Drills — Search Autocomplete

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Prime Day 10× QPS | Pre-warm edge; freeze risky nearline; raise fuzzy shed | Quality degrades before availability |
| Bad index ships | Canary auto-rollback to N-1 | Artifacts are versioned and reversible |
| Safety incident | Edge kill-list + invalidate | Fail closed beats latency |
| Redis outage | Edge + shards; coalesce | Cache is acceleration not correctness |

## 18. Final Checklist — Search Autocomplete

- [ ] Scoped vs SERP with ownership split
- [ ] Latency budget with numbers
- [ ] Marketplace isolation
- [ ] Safety embedded in cache
- [ ] Offline + nearline learning
- [ ] Progressive scale 10×/100×/1,000×
- [ ] Organic vs sponsored labeled
- [ ] Unit cost RAM$/QPS

## 19. Expanded Design Notes — Search Autocomplete

### 19.1 Indexing pipeline detail

Daily full build computes query statistics over trailing windows (1d/7d/28d), applies k-anonymity thresholds, strips PII-like patterns, and emits shard artifacts with checksums and a shard map. Hourly micro-batches update scores for head queries without rewriting every shard. Nearline spike detectors write into a side rocksdb/redis structure merged at read time with a freshness boost, compacted on the next full build.

Artifact promotion uses a registry: uploaded → validated → canary → baked → default. Keep N prior defaults for instant rollback. Validation includes deterministic suggest golden sets (prefixes → expected members) and memory footprint ceilings per shard.

### 19.2 Ranking feature families

Popularity features (counts, unique shoppers), engagement (suggest CTR, post-click dwell), commerce (ATC/purchase rates), freshness (velocity), context (department, device, holiday flags), and personalization (recent query overlap, affinity hash collisions). Keep online features tiny; most signal is offline-precomputed into a base score.

Diversification uses intent clustering: lexical stems, embedding clusters for head queries, and entity-type quotas (at most N ASINs, M brands).

### 19.3 Personalization privacy modes

Logged-out: device-local recents only. Logged-in light: server profile of hashed recent queries and category affinities with short TTL. Strict: disable cross-category affinity. Never put raw addresses/phone-like strings into profiles.

### 19.4 Entity overlays

ASINs need title, image, price band, OOS bit, average rating compression. Brands/categories need ids and display names. Overlay hydration is batched and cached; critical suppressions use a push kill-list that bypasses TTLs.

### 19.5 Failure isolation

Fuzzy, personalization, entity hydration, and ads are optional stages with deadlines. Exact prefix retrieval + safety is the minimal path. If ads time out, organic still returns. If entity hydration times out, return query-only suggestions.

### 19.6 Load testing

Replay real prefix distributions. Synthetic uniform alphabet traffic under-tests hot prefixes and over-tests rare shards. Include Prime Day traces. Measure not only p99 but also cache herd behavior after deploys.

### 19.7 Organizational model

Suggest Serving owns online SLO and index deploy tooling. Suggest Ranking Science owns offline objective and feature definitions. Ads owns sponsored inventory. Trust owns policy packs. Written interfaces beat meetings—versioned protobuf/JSON contracts.

### 19.8 Evolution path

Phase 1.5: better transliteration, stronger department understanding. Phase 2: tiny on-device head dictionaries for mobile. Phase 3: LLM offline query rewriting for index enrichment—not online decode-per-keystroke.

## 20. Sample Numerical Worked Example

Assume US marketplace peak 2M suggest QPS, edge hit 60%, Redis hit 50% of remainder, shard hit for the rest.

```text
edge_hits = 0.60 × 2M = 1.2M
redis_hits = 0.50 × 0.40 × 2M = 0.4M
shard_qps  = 0.50 × 0.40 × 2M = 0.4M
```

If each shard node sustains 20K QPS of trie lookups, you need ≥ 20 nodes before headroom; with hot-key replication and seasonal peaks, plan ~2–3× that and rely on edge growth to bend the curve.

Egress: 2M × 800 bytes ≈ 1.6 GB/s before compression/CDN caching—economic justification for edge alone.

---

## 21. Glossary (Autocomplete-specific)

| Term | Definition |
|------|------------|
| Posting list | prefix → top-K candidates |
| FST | Compressed automaton mapping |
| Nearline patch | Minutes-latency side index |
| k-threshold | Min distinct users before indexable |
| Organic floor | Minimum non-sponsored slots |
| Policy pack | Marketplace safety ruleset |

---

*End of document — Amazon Search Autocomplete / Typeahead (SDE III)*
