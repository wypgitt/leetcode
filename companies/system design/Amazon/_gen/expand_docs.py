#!/usr/bin/env python3
"""Expand each Amazon design doc to ~900–1100 lines with high-quality content."""
from __future__ import annotations

from pathlib import Path

OUT = Path("/Users/yingpengwang/leetcode/system design/Amazon")

COMMON_TAIL = """

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

"""


def deep_qa(title: str, pairs: list[tuple[str, str]]) -> str:
    lines = [f"\n## 16. Additional Deep Q&A — {title}\n"]
    for i, (q, a) in enumerate(pairs, 1):
        lines.append(f"### Q{i}. {q}\n\n{a}\n")
    return "\n".join(lines)


def scenarios(title: str, items: list[tuple[str, str, str]]) -> str:
    lines = [f"\n## 17. Scenario Drills — {title}\n"]
    lines.append("| Scenario | What you do | What you say |\n|-----------|-------------|--------------|")
    for s, d, say in items:
        lines.append(f"| {s} | {d} | {say} |")
    lines.append("")
    return "\n".join(lines)


def checklist(title: str, items: list[str]) -> str:
    lines = [f"\n## 18. Final Checklist — {title}\n"]
    for it in items:
        lines.append(f"- [ ] {it}")
    lines.append("")
    return "\n".join(lines)


def long_notes(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"\n## 19. Expanded Design Notes — {title}\n"]
    for h, paras in sections:
        lines.append(f"### {h}\n")
        for p in paras:
            lines.append(p)
            lines.append("")
    return "\n".join(lines)


EXPANSIONS: dict[str, str] = {}


def build_search_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "Search Autocomplete",
            [
                (
                    "How do you keep p99 stable when fuzzy rate spikes?",
                    "Cap fuzzy CPU with token bucket per shard; degrade fuzzy first; prefer precomputed misspelling maps; alarm on fuzzy_rate and fuzzy_p99 separately from exact path.",
                ),
                (
                    "How do marketplace launches work?",
                    "Bootstrap from catalog titles + translated head queries; start with higher popular-only weights; enable personalization after enough click mass; isolate cell from day one.",
                ),
                (
                    "What belongs in edge vs Redis vs shard?",
                    "Edge: ultra-hot short prefixes and trending. Redis: hot medium prefixes with safety embedded. Shards: authoritative compressed postings for long-tail and merges.",
                ),
                (
                    "How do you attribute purchases to suggestions?",
                    "Impression_id → click → search → ASIN view → purchase join with time windows; careful with last-click bias; report suggest-assisted GMV as directional.",
                ),
                (
                    "How do you fight suggestion spam farms?",
                    "Trusted session weights, purchase confirmation, device reputation, clustering of near-duplicate queries, manual/policy ops tools, and delayed admission to index.",
                ),
                (
                    "Canary metrics that matter?",
                    "CTR@K, empty_rate, reformulation_rate, p99, safety_block_rate, RAM, and complaint tickets. Auto rollback if CTR drops and empty_rate rises together.",
                ),
                (
                    "How do you version safety policy with cache?",
                    "Include policy_version in cache key or payload; bumping policy invalidates logically; eager purge for emergency blocklists via edge kill-list.",
                ),
                (
                    "Department-scoped suggest vs global?",
                    "If user is in Books, bias strongly but keep a small global escape hatch so they can still reach ‘book light’ electronics; product decision—state it.",
                ),
                (
                    "Unicode / homoglyph attacks?",
                    "NFKC normalization, confusable mapping, and safety on normalized form; store display text separately from match key.",
                ),
                (
                    "How is this different from OpenSearch completion suggester?",
                    "Managed suggesters are fine for smaller apps; Amazon scale needs custom sharding, marketplace policy packs, entity overlays, and cost/ownership controls.",
                ),
            ],
        )
        + scenarios(
            "Search Autocomplete",
            [
                ("Prime Day 10× QPS", "Pre-warm edge; freeze risky nearline; raise fuzzy shed", "Quality degrades before availability"),
                ("Bad index ships", "Canary auto-rollback to N-1", "Artifacts are versioned and reversible"),
                ("Safety incident", "Edge kill-list + invalidate", "Fail closed beats latency"),
                ("Redis outage", "Edge + shards; coalesce", "Cache is acceleration not correctness"),
            ],
        )
        + checklist(
            "Search Autocomplete",
            [
                "Scoped vs SERP with ownership split",
                "Latency budget with numbers",
                "Marketplace isolation",
                "Safety embedded in cache",
                "Offline + nearline learning",
                "Progressive scale 10×/100×/1,000×",
                "Organic vs sponsored labeled",
                "Unit cost RAM$/QPS",
            ],
        )
        + long_notes(
            "Search Autocomplete",
            [
                (
                    "19.1 Indexing pipeline detail",
                    [
                        "Daily full build computes query statistics over trailing windows (1d/7d/28d), applies k-anonymity thresholds, strips PII-like patterns, and emits shard artifacts with checksums and a shard map. Hourly micro-batches update scores for head queries without rewriting every shard. Nearline spike detectors write into a side rocksdb/redis structure merged at read time with a freshness boost, compacted on the next full build.",
                        "Artifact promotion uses a registry: uploaded → validated → canary → baked → default. Keep N prior defaults for instant rollback. Validation includes deterministic suggest golden sets (prefixes → expected members) and memory footprint ceilings per shard.",
                    ],
                ),
                (
                    "19.2 Ranking feature families",
                    [
                        "Popularity features (counts, unique shoppers), engagement (suggest CTR, post-click dwell), commerce (ATC/purchase rates), freshness (velocity), context (department, device, holiday flags), and personalization (recent query overlap, affinity hash collisions). Keep online features tiny; most signal is offline-precomputed into a base score.",
                        "Diversification uses intent clustering: lexical stems, embedding clusters for head queries, and entity-type quotas (at most N ASINs, M brands).",
                    ],
                ),
                (
                    "19.3 Personalization privacy modes",
                    [
                        "Logged-out: device-local recents only. Logged-in light: server profile of hashed recent queries and category affinities with short TTL. Strict: disable cross-category affinity. Never put raw addresses/phone-like strings into profiles.",
                    ],
                ),
                (
                    "19.4 Entity overlays",
                    [
                        "ASINs need title, image, price band, OOS bit, average rating compression. Brands/categories need ids and display names. Overlay hydration is batched and cached; critical suppressions use a push kill-list that bypasses TTLs.",
                    ],
                ),
                (
                    "19.5 Failure isolation",
                    [
                        "Fuzzy, personalization, entity hydration, and ads are optional stages with deadlines. Exact prefix retrieval + safety is the minimal path. If ads time out, organic still returns. If entity hydration times out, return query-only suggestions.",
                    ],
                ),
                (
                    "19.6 Load testing",
                    [
                        "Replay real prefix distributions. Synthetic uniform alphabet traffic under-tests hot prefixes and over-tests rare shards. Include Prime Day traces. Measure not only p99 but also cache herd behavior after deploys.",
                    ],
                ),
                (
                    "19.7 Organizational model",
                    [
                        "Suggest Serving owns online SLO and index deploy tooling. Suggest Ranking Science owns offline objective and feature definitions. Ads owns sponsored inventory. Trust owns policy packs. Written interfaces beat meetings—versioned protobuf/JSON contracts.",
                    ],
                ),
                (
                    "19.8 Evolution path",
                    [
                        "Phase 1.5: better transliteration, stronger department understanding. Phase 2: tiny on-device head dictionaries for mobile. Phase 3: LLM offline query rewriting for index enrichment—not online decode-per-keystroke.",
                    ],
                ),
            ],
        )
        + """
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
"""
    )


def build_leaderboard_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "Real-Time Leaderboard",
            [
                (
                    "How do you encode tie-breaks without floats?",
                    "Use integer scores (fixed point) and compose a 64-bit sort key: high bits score, middle bits inverted timestamp, low bits player hash. Document overflow limits.",
                ),
                (
                    "WAL before or after ZADD visibility?",
                    "Pick explicitly: (A) WAL quorum then ZADD (stronger durability, higher latency); (B) ZADD then async WAL with risk window. For competitive cash/prize boards prefer A or sync replication.",
                ),
                (
                    "How do approximate global ranks work?",
                    "Maintain score histograms or count-min style rank sketches per shard; estimate rank as sum of counts above score + local rank. Product labels as approximate.",
                ),
                (
                    "Friends board write amplification?",
                    "If each score update fans out to all friends’ boards, costs explode. Cap friends, batch, or compute on read for small F; for large F use aspirational sample sets.",
                ),
                (
                    "Season archive format?",
                    "Snapshot top-N + player rank samples + full cold dump to S3/Parquet; keep metadata in OLTP for ‘my final rank’ lookups.",
                ),
                (
                    "How to handle clock skew on timestamps?",
                    "Prefer server receive time for tie-break, not client clock; bound match end times via game service.",
                ),
                (
                    "Prize payout boards vs casual?",
                    "Higher durability and audit; possibly stronger consistency cell; manual freeze before payout; dual control for edits.",
                ),
                (
                    "Multi-title platform tenancy?",
                    "board_id namespaces per title; noisy neighbor limits; separate Redis cells for AAA launches.",
                ),
                (
                    "Replay after data loss?",
                    "Rebuild from WAL; verify top-K checksums vs periodic snapshots; communicate rebuild ETA if public boards pause.",
                ),
                (
                    "Why not leader-election single primary for all writes?",
                    "Single primary doesn’t scale write spikes; shard by board; use primary per shard only.",
                ),
            ],
        )
        + scenarios(
            "Leaderboard",
            [
                ("Season end write storm", "Pre-split; disable friends fanout; cache top-K", "Write path protected"),
                ("Cheater in top-10", "Quarantine + rebuild segment", "Audit + fairness messaging"),
                ("Redis shard loss", "Promote replica / replay WAL", "Durability story"),
                ("Wrong fence during season flip", "Halt writes; repair; reopen", "Fence tokens are sacred"),
            ],
        )
        + checklist(
            "Leaderboard",
            [
                "Idempotent match updates",
                "Season fence design",
                "No single global ZSET at scale",
                "Top-K spectator cache",
                "Anti-cheat hooks",
                "Durability vs latency choice explicit",
                "Exact vs approximate rank product call",
                "Archive + payout audit path",
            ],
        )
        + long_notes(
            "Leaderboard",
            [
                (
                    "19.1 Board metadata state machine",
                    [
                        "States: `warming` → `open` → `frozen` → `archived`. Writes allowed only in `open` (and optionally `warming` for tests). `frozen` used pre-payout. Transitions require Season Manager fencing with monotonic epoch.",
                    ],
                ),
                (
                    "19.2 Query patterns",
                    [
                        "Top-K is hot and cacheable. My rank is per-player and should be served from the shard owning the player’s member. Nearby needs rank position then range. Avoid scanning.",
                    ],
                ),
                (
                    "19.3 Anti-cheat layering",
                    [
                        "L0 signature + schema. L1 rate/delta bounds. L2 async anomaly models. L3 human investigation for esports. Rewinds emit compensating events rather than silent deletes when possible.",
                    ],
                ),
                (
                    "19.4 Pub/sub invalidation",
                    [
                        "On top-K membership change, publish board_id invalidate. Spectators read cache. If pub/sub drops, short TTL self-heals. Do not push full top-K over pub/sub to millions—invalidate only.",
                    ],
                ),
                (
                    "19.5 Multi-region",
                    [
                        "Regional boards authoritative in-region. Global boards either eventual aggregation or pinned home region. Cross-region synchronous ZADD is a latency/availability trap.",
                    ],
                ),
                (
                    "19.6 Testing strategy",
                    [
                        "Deterministic fixtures for ties; chaos for shard loss; load tests replaying season endings; property tests for idempotency; fence cutover rehearsals.",
                    ],
                ),
                (
                    "19.7 Product analytics",
                    [
                        "Rank-up events drive engagement notifications—emit from stream processors, not inline with ZADD ack path beyond a lightweight event.",
                    ],
                ),
                (
                    "19.8 Evolution",
                    [
                        "Add secondary objectives (wins, KD) as display overlays without changing primary sort unless versioned board type changes.",
                    ],
                ),
            ],
        )
        + """
## 20. Worked Example — Hot Global Board Split

10M players on one logical board. Shard into 16 partial ZSETs by `hash(player_id) % 16`. Each partial ~625K members ≈ 20MB+ overhead.

Top-100 global: fetch top-100 from each partial (1600 rows) and merge—cheap. Global rank for a player: local rank + estimate of how many players in other shards have higher score using per-shard score histograms (1–5KB each) refreshed every second.

---

## 21. API Error Codes (illustrative)

| Code | Meaning |
|------|---------|
| 409 idempotency conflict | Same match_id different payload |
| 423 season frozen | Fence rejects write |
| 429 rate limited | Player/server storm |
| 422 cheat reject | Gate rejection |
| 404 board unknown | Bad board_id |

---
"""
    )


def build_alexa_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "Alexa Advertising Workflow",
            [
                (
                    "What features can ads decisioning legally use?",
                    "Redacted intent categories, locale, device class, consent-approved segments, content contextual category—not raw audio, not unrestricted transcripts, not sensitive slot values (e.g., health details).",
                ),
                (
                    "How do you prefetch safely?",
                    "Only when policy allows speculative processing; cancel unused decisions; do not persist speculative audio-derived features beyond request TTL.",
                ),
                (
                    "Household vs personal targeting?",
                    "Default household; personal only with voice profile + consent. Kids profiles force closed personalized ads.",
                ),
                (
                    "Brand safety near breaking news?",
                    "Nearline kill-switch on contextual categories; advertiser exclusions; human ops bridge for major events.",
                ),
                (
                    "How do advertisers get reports without user paths?",
                    "Aggregated campaign metrics with k-thresholds; delayed batch; fraud-filtered; no transcript attachments.",
                ),
                (
                    "Auction vs curated?",
                    "Some Alexa surfaces curated; some auction. Architecture supports both behind Decisioning with a common eligibility layer.",
                ),
                (
                    "What if NLU intent flips after prefetch?",
                    "Bind decision to intent_id/version; discard prefetch on mismatch; never play mismatched ad.",
                ),
                (
                    "Latency hiding with TTS?",
                    "Start content TTS while ads decision finalizes only if ad is trailing; never delay critical answers for optional trailing ads.",
                ),
                (
                    "Cross-device frequency caps consistency?",
                    "Eventual consistency acceptable; prefer under-cap. Cap store keyed by household_token with short sync intervals.",
                ),
                (
                    "How to A/B ads load without harming trust?",
                    "Holdouts; guardrail on opt-out rate, barge-in, customer contacts; never remove legally required disclosures in variants.",
                ),
            ],
        )
        + scenarios(
            "Alexa Ads",
            [
                ("Ads service down", "Content-only mode", "Ads are optional guests"),
                ("Privacy complaint", "Kill personalized ads; audit", "Fail closed"),
                ("Kids profile mis-tagged", "Treat as kids; fix labeling", "Safety > revenue"),
                ("Fraudulent play events", "Signature + dedupe + anomaly", "Measurement integrity"),
            ],
        )
        + checklist(
            "Alexa Ads",
            [
                "No raw audio to advertisers",
                "Consent/kids/sensitive fail closed",
                "Content path independent of ads",
                "decision_id + policy_version audit",
                "Aggregated measurement",
                "Latency budget additive",
                "Locale policy packs",
                "Ownership Speech vs Ads vs Privacy",
            ],
        )
        + long_notes(
            "Alexa Ads",
            [
                (
                    "19.1 End-to-end sequence detail",
                    [
                        "Device streams audio to Speech Gateway after wake validation. ASR produces partials; NLU emits intent hypotheses. Dialog Manager decides if an ad slot exists (trailing audio, skill suggestion, shopping). Eligibility checks consent, profile type, intent sensitivity, frequency. Decisioning returns creative refs and disclosure. Renderer mixes directives. Measurement records play/complete without transcript payload.",
                    ],
                ),
                (
                    "19.2 Slot redaction",
                    [
                        "Slots like `medicine_name` or `account_number` never flow to ads. A redaction map is owned by Privacy and versioned. Ads feature schema is allowlist-based, not denylist-based.",
                    ],
                ),
                (
                    "19.3 Creative supply chain",
                    [
                        "Advertisers upload audio/TTS scripts; offline review; transcode; loudness normalize; store on CDN; runtime fetches by creative_id. Runtime still enforces brand safety and exclusions.",
                    ],
                ),
                (
                    "19.4 Shopping ads",
                    [
                        "Join retail catalog for product offers; reuse retail relevance models with voice-specific features (utterance category). Disclosure differs from web sponsored products but principles match: labeled, relevant, organic floor where applicable.",
                    ],
                ),
                (
                    "19.5 Internationalization",
                    [
                        "Policy packs per country; consent strings; banned categories; language of disclosure. Decision cells regional to keep latency and data residency.",
                    ],
                ),
                (
                    "19.6 Fraud",
                    [
                        "Fake devices / replayed measurement: sign events with device attestation where possible; rate limit; anomaly on completion without play; campaign-level velocity checks.",
                    ],
                ),
                (
                    "19.7 Operability",
                    [
                        "Kill switches: disable personalized ads, disable all ads, disable specific advertiser, disable speculative prefetch. Each switch tested in game days.",
                    ],
                ),
                (
                    "19.8 Evolution",
                    [
                        "On-device eligibility caches; edge decision tokens; stronger on-device privacy preserving measurement contributions.",
                    ],
                ),
            ],
        )
        + """
## 20. Latency Waterfall Example

```text
t0 wake detected
t0–t400 streaming ASR partials
t350 NLU hypothesis intent=Weather
t350–t390 eligibility (parallel)
t350–t420 ads decision prefetch
t420 dialog commits trailing ad slot
t420–t900 TTS content weather
t900–t1200 sponsored trailing audio (if any)
```

If ads decision exceeds deadline at t400, skip ad; weather still speaks on time.

---

## 21. Policy Pack Sketch

```text
PolicyPack {
  country,
  kids_rules,
  sensitive_intents[],
  consent_required_flags[],
  disclosure_templates[],
  brand_safety_lists_ref,
  retention_ttl_days
}
```

---
"""
    )


def build_product_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "Product Recommender",
            [
                (
                    "How many candidate channels is too many?",
                    "Start with 3–5 high-precision channels with explicit budgets. More channels help recall but explode hydrate/rank cost and make debugging hard. Add channels when offline recall gaps justify them.",
                ),
                (
                    "How do you set candidate budget K?",
                    "Empirically: plot conversion vs K and p99 vs K. Typical 500–2000. Homepage can afford more latency than tiny PDP modules.",
                ),
                (
                    "Multi-objective ranking without collapse?",
                    "Scalarize with weights + constraints (diversity, brand caps). Use guardrail metrics in experiments. Avoid secretly optimizing profit alone.",
                ),
                (
                    "How do you fight filter bubbles?",
                    "Diversity constraints, explore slots, category coverage minimums, serendipity metrics.",
                ),
                (
                    "Training data pipeline essentials?",
                    "Join impressions→clicks→purchases→returns with PIT features; store model_version and candidate set samples; position bias handling.",
                ),
                (
                    "Two-tower vs CF graph?",
                    "Two-tower scales to ANN retrieval for personalization; CF graphs shine for complementary items. Use both as channels.",
                ),
                (
                    "How to handle exploding catalog?",
                    "ANN sharding, aggressive candidate filters (geo/marketplace), hierarchical categories, distilled rankers.",
                ),
                (
                    "Empty widget policy?",
                    "Fallback popularity / similar / editorial. Empty is a SEV-level customer experience bug on homepage.",
                ),
                (
                    "Realtime features vs batch?",
                    "Session features realtime; long-term affinities batch/nearline. Don’t pretend all features are realtime.",
                ),
                (
                    "Marketplace fairness to sellers?",
                    "Explore quotas, diversity, avoid pure brand entrenchment; still optimize customer value—state the tension.",
                ),
            ],
        )
        + scenarios(
            "Product Recs",
            [
                ("Ranker outage", "Fallback popularity/similar", "Non-empty surface"),
                ("OOS storm", "Nearline inventory filter", "Trust > CTR"),
                ("Bad model canary", "Auto rollback", "Guardrails"),
                ("Gift shopping mispersonalization", "Session intent demote history", "Context wins"),
            ],
        )
        + checklist(
            "Product Recs",
            [
                "Retrieve → rank → re-rank stages",
                "Feature store PIT logging",
                "Surface-specific objectives",
                "Fallbacks non-empty",
                "OOS/policy filters",
                "Experimentation hooks",
                "Ads merge policy labeled",
                "Unit cost $/1K recs",
            ],
        )
        + long_notes(
            "Product Recs",
            [
                (
                    "19.1 Channel design",
                    [
                        "Co-purchase: classic Amazon ‘customers also bought’. Co-view: browsing affinity. Search-purchase: intent from queries. Two-tower ANN: personalized. Trending: cold-start/seasonal. Editorial: merchandising. Each returns scored candidates with channel tags for explainability and debugging.",
                    ],
                ),
                (
                    "19.2 Ranker features",
                    [
                        "User affinities, item popularity, price compatibility, complementary vs substitute flags, shipping speed, Prime eligibility, review scores, session last-N ASINs, time of day. Avoid leakage from future joins.",
                    ],
                ),
                (
                    "19.3 Re-rank constraints",
                    [
                        "Hard: blocked, OOS, geo ineligible, age-restricted. Soft: diversity MMR, brand caps, price band spread, explore slot. Ads: labeled sponsored insertion with relevance floor.",
                    ],
                ),
                (
                    "19.4 Offline evaluation",
                    [
                        "AUC/NDCG insufficient alone. Use counterfactual estimators cautiously; ship decisions via A/B with guardrails on returns and latency.",
                    ],
                ),
                (
                    "19.5 Serving architecture",
                    [
                        "Stateless Recs API; HNSW/IVF ANN clusters; feature cache; model servers with batching; deadlines per stage; hedged requests for hot dependencies.",
                    ],
                ),
                (
                    "19.6 Homepage assembly",
                    [
                        "Multiple widgets each call Recs with different surface ids; page compositor applies page-level diversity so widgets don’t all repeat the same ASIN.",
                    ],
                ),
                (
                    "19.7 Email & notifications",
                    [
                        "Batch generate candidates offline; personalize at send; cheaper and more cacheable than online QPS.",
                    ],
                ),
                (
                    "19.8 Long-term evolution",
                    [
                        "Unified feature platform; generative re-rank explanations; on-device session models for apps; still keep multi-stage discipline.",
                    ],
                ),
            ],
        )
        + """
## 20. Worked Latency Budget (PDP)

```text
context:      8 ms
retrieve ∥:  35 ms  (slowest channel)
features:    30 ms
rank 1K:     35 ms
rerank:       8 ms
total:      ~116 ms  (within 150 ms p99 target with headroom)
```

If rank exceeds budget, drop K from 1000→600 or switch to distilled model.

---

## 21. Label Definition Sketch

```text
label_click = 1 if click within T1
label_purchase = 1 if purchase within T2 and not returned within T3
weight = propensity_inverse(position) × trust_session_weight
```

---
"""
    )


def build_clothing_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "Clothing Recommender",
            [
                (
                    "How do you normalize sizes across brands?",
                    "Garment-type-specific charts; brand offset models learned from returns (‘too small/large’); store both labeled size and normalized size embedding.",
                ),
                (
                    "What if visual similar is wrong colorway season?",
                    "Visual ANN for style cut/pattern; re-rank with color seasonality and inventory; allow intent override when user browsed that color.",
                ),
                (
                    "Outfit model supervision?",
                    "Co-purchase in fashion sessions, stylist sets, and weak visual harmony scores; evaluate with human style panels not only CTR.",
                ),
                (
                    "How to avoid stereotyping?",
                    "Prefer explicit browse/context over inferred sensitive attributes; careful with gendered category forcing; offer neutral discovery rails.",
                ),
                (
                    "Inventory at SKU vs style?",
                    "Recommend style but ensure at least one feasible SKU in customer size; deep-link to available variant.",
                ),
                (
                    "Trend vs classic wardrobe?",
                    "Explore slot for trends; core rank still fit/satisfaction; don’t let TikTok velocity blow up return rates.",
                ),
                (
                    "Image embedding refresh?",
                    "New images nearline embed + ANN upsert; full reindex periodically; version embeddings to avoid mixed spaces.",
                ),
                (
                    "Returns delay in labels?",
                    "Train on delayed labels; use interim proxy (size message, early return signals); keep online model stable.",
                ),
                (
                    "Cold-start customer without size?",
                    "Ask-friendly UX; segment priors; soft constraints until confidence rises; never hallucinate body measurements from photos of the customer.",
                ),
                (
                    "Deal-breaker reminder?",
                    "Generic product CF without fit/visual/season—fashion returns will punish you.",
                ),
            ],
        )
        + scenarios(
            "Clothing Recs",
            [
                ("Winter swimwear browse", "Intent override season demotion", "Context matters"),
                ("Size OOS for popular style", "Alt sizes / similar cut in stock", "Variant truth"),
                ("Return-rate spike after model", "Rollback; raise λ on P(return)", "Guardrails"),
                ("Bad attribute color data", "Trust visual more; fix taxonomy", "Data quality"),
            ],
        )
        + checklist(
            "Clothing Recs",
            [
                "Visual ANN channel",
                "Size/fit profile + SKU inventory",
                "Seasonality with overrides",
                "Returns-aware objective",
                "Outfit complements",
                "Sensitivity/ethics constraints",
                "Attribute normalization plan",
                "Fashion ≠ generic recs stated early",
            ],
        )
        + long_notes(
            "Clothing Recs",
            [
                (
                    "19.1 Fashion taxonomy realities",
                    [
                        "Colors like ‘bordeaux’ vs ‘wine’ vs ‘dark red’ break filters. Invest in synonym graphs and embeddings over brittle exact matches. Materials and occasion tags are similarly messy.",
                    ],
                ),
                (
                    "19.2 Visual pipeline",
                    [
                        "Ingest studio images → crop/background normalize → embedding model → ANN. Use additional towers for close-up texture if needed. Protect against duplicate listings.",
                    ],
                ),
                (
                    "19.3 Fit confidence",
                    [
                        "Confidence grows with kept purchases and explicit size settings. Low confidence → soft boosts not hard filters. High confidence → hard filter unavailable sizes.",
                    ],
                ),
                (
                    "19.4 Season engines",
                    [
                        "Calendar + hemisphere + optional weather band. Event peaks (wedding season, back-to-school) as features. Tropical locales differ from northern US.",
                    ],
                ),
                (
                    "19.5 Evaluation human-in-loop",
                    [
                        "Style judges rate outfit coherence; fit specialists review size logic; combine with online AB. Pure offline AUC will greenlight ugly wrong-season bundles.",
                    ],
                ),
                (
                    "19.6 Mobile visual search synergy",
                    [
                        "Same embeddings power ‘shop the look’ camera features—platformize embeddings as a shared service with versioning.",
                    ],
                ),
                (
                    "19.7 Seller ecosystem",
                    [
                        "Private label vs 3P apparel; ensure small brands can be retrieved via visual/attribute not only sales CF entrenchment.",
                    ],
                ),
                (
                    "19.8 Roadmap",
                    [
                        "Better body-aware fit without invasive data; generative outfit visualization; try-on AR hooks—keep privacy first.",
                    ],
                ),
            ],
        )
        + """
## 20. Objective Sketch

```text
score = w1*P(click) + w2*P(purchase) - w3*P(return_fit) + w4*style_affinity
        + w5*season_match + w6*in_stock_size - diversity_penalty
```

Tune w3 high enough that return spikes fail guardrails in canary.

---

## 21. SKU Feasibility Pseudocode

```text
def feasible(style, fit_profile):
  variants = inventory(style)
  if fit_profile.confidence < T:
      return any(v.in_stock for v in variants)
  return any(v.in_stock and size_ok(v.size, fit_profile) for v in variants)
```

---
"""
    )


def build_inflight_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "In-Flight Movie Recommender",
            [
                (
                    "What buffers do you subtract from remaining time?",
                    "Taxi-in/out, safety demos, meal service optional, customer pause slack. Airline-configurable. Underestimate remaining time slightly to protect finishability.",
                ),
                (
                    "How do you recommend series?",
                    "Compute max episodes that fit; prefer complete story arcs tagged in metadata; warn on cliffhangers if next episode won’t fit.",
                ),
                (
                    "Personal device vs seatback?",
                    "Same feasibility API; personal device may stream if Wi-Fi; seatback usually local cache. Personalization auth differs (Prime login vs seat session PIN).",
                ),
                (
                    "How do packs sync at the gate?",
                    "Prioritize small metadata+rank lists; bulk video via airline content ops. Packs keyed by flight_id + segment + passenger token hash.",
                ),
                (
                    "What if avionics time feed fails?",
                    "Fall back to scheduled block time minus elapsed; widen buffers; still hard-filter.",
                ),
                (
                    "Kids traveling?",
                    "Seat/profile flags; airline rating rules; ignore adult personalization packs.",
                ),
                (
                    "Metric delay after landing?",
                    "Buffer logs onboard encrypted; flush via gate Wi-Fi/cellular; late-join training. Don’t block UX on flush.",
                ),
                (
                    "Why not use full Prime cloud recommender onboard?",
                    "Connectivity and catalog licensing differ; runtime constraint dominates; must work offline.",
                ),
                (
                    "Multi-leg trips?",
                    "Separate contexts per leg; don’t recommend 3h movie before 1h hop even if total travel is 10h unless layover viewing supported.",
                ),
                (
                    "Licensing expiry mid-day?",
                    "Snapshot validity window; hide expired; sync on turnaround; never show unlicensed titles.",
                ),
            ],
        )
        + scenarios(
            "In-Flight Recs",
            [
                ("Short-haul 45m", "Episode/short rails", "Finishability first"),
                ("Red-eye long haul", "Calm genres prior + long movies", "Context priors"),
                ("Personalization missing", "Popular feasible list", "Offline fallback"),
                ("Shared seatback privacy", "PIN + wipe", "No leftover profile"),
            ],
        )
        + checklist(
            "In-Flight Recs",
            [
                "Hard duration feasibility",
                "Ground vs onboard planes",
                "Offline-first fallback",
                "Buffers explicit",
                "Kids/rating policy onboard",
                "Seatback privacy wipe",
                "Delayed metrics flush",
                "Licensing snapshot validity",
            ],
        )
        + long_notes(
            "In-Flight Recs",
            [
                (
                    "19.1 Effective time formula",
                    [
                        "`effective = max(0, remaining_reported - buffer_taxi - buffer_safety - buffer_meal_opt - buffer_slack)`. Recompute on interval or on significant ETA change. As effective shrinks, refilter lists and switch rails to shorts.",
                    ],
                ),
                (
                    "19.2 Ground pack builder",
                    [
                        "Inputs: passenger affinities (if consented/Prime), catalog onboard snapshot, flight duration estimate, locale/languages, kids flag. Outputs: ranked title_ids with reasons. Build closer to departure for fresher ETAs.",
                    ],
                ),
                (
                    "19.3 Onboard service constraints",
                    [
                        "CPU/memory limited. No GPU inference. Use precomputed scores + light boosts (language match, unfinished continue watching if cached). p99 local < 100ms.",
                    ],
                ),
                (
                    "19.4 Continue watching",
                    [
                        "If passenger has mid-movie progress cached and remaining time fits leftover runtime, boost strongly—highest satisfaction path.",
                    ],
                ),
                (
                    "19.5 Airline multi-tenant platform",
                    [
                        "Amazon provides personalization as a service to multiple airlines with cell isolation, different licensed catalogs, and brand UX. Don’t hardcode one airline’s buffers.",
                    ],
                ),
                (
                    "19.6 Evaluation",
                    [
                        "Completion within flight, start rate, abandon after 5m, survey thumbs, complaint rate about ‘movie too long’. Offline ranking metrics secondary.",
                    ],
                ),
                (
                    "19.7 Security",
                    [
                        "Encrypt profile packs at rest onboard; wipe after flight; sign catalogs; prevent seat-to-seat profile reads.",
                    ],
                ),
                (
                    "19.8 Evolution",
                    [
                        "Optional online enhance when portal Wi-Fi strong; still never require it. Short-form catalogs grow; interactive maps etc. out of scope.",
                    ],
                ),
            ],
        )
        + """
## 20. Feasibility Examples

| Remaining | Buffer | Effective | OK titles |
|-----------|--------|-----------|-----------|
| 360m | 40m | 320m | runtime ≤ 320 |
| 90m | 25m | 65m | episodes/shorts ≤ 65 |
| 25m | 10m | 15m | shorts only |

Soft preference band: runtime ∈ [0.5, 0.85] × effective for primary movie suggestion.

---

## 21. Onboard Log Record

```text
PlayEvent { flight_id, seat_session, title_id, t_start, t_end, effective_remaining_at_start, completed_bool }
```

Flush after landing; scrub seat_session mapping on wipe.

---
"""
    )


def build_mobile_extra() -> str:
    return (
        COMMON_TAIL
        + deep_qa(
            "Mobile Autocomplete & Spell-Check",
            [
                (
                    "When do you call server assist?",
                    "When local confidence low, network available, consent allows, field type permits, and budget tokens remain. Never for password/secure fields.",
                ),
                (
                    "How do you measure on-device quality?",
                    "Lab harnesses with typing traces; acceptance/undo rates from opt-in telemetry; battery traces on mid-tier devices; offline suite per language.",
                ),
                (
                    "How aggressive should autocorrect be?",
                    "User setting: off / modest / aggressive. High undo rate → auto-dial down. Proper nouns in user lexicon protected.",
                ),
                (
                    "Delta pack updates?",
                    "Binary diffs + compression; staged rollout; signature verify; reject if decode fails; keep last-good pack.",
                ),
                (
                    "Code-switching?",
                    "Language ID on recent tokens; mixed lexicons; avoid correcting Spanish words into English lookalikes aggressively.",
                ),
                (
                    "Catalog brand packs?",
                    "Head brands/ASINs in on-device catalog dictionary deltas; long-tail via server assist in search fields.",
                ),
                (
                    "Federated learning pitfalls?",
                    "Device heterogeneity, privacy composition, attack via poisoned clients—treat as advanced phase with expert privacy review.",
                ),
                (
                    "Relation to server search autocomplete?",
                    "Different product: typing UX vs search suggest service. Share spell corpora carefully; don’t couple freights.",
                ),
                (
                    "Storage pressure on cheap devices?",
                    "Tiered packs (tiny/base/full); evict unused languages; compress.",
                ),
                (
                    "Accessibility?",
                    "Announce suggestions to screen readers; large targets; respect OS reduced-motion/autocorrect settings where applicable.",
                ),
            ],
        )
        + scenarios(
            "Mobile AC/Spell",
            [
                ("Airplane offline", "Local packs only", "Offline is a feature"),
                ("Assist timeout", "Show local", "Deadline merge"),
                ("Corrupt pack", "Last-good fallback", "Signed artifacts"),
                ("Password field", "Disable learn/assist", "Hard invariant"),
            ],
        )
        + checklist(
            "Mobile AC/Spell",
            [
                "Local-first offline path",
                "Secure fields never learn",
                "Consent for server assist",
                "Battery/latency budgets numeric",
                "Signed language packs + deltas",
                "Safety on merged candidates",
                "Field-type policy matrix",
                "Undo/regret metrics",
            ],
        )
        + long_notes(
            "Mobile AC/Spell",
            [
                (
                    "19.1 On-device architecture",
                    [
                        "SDK hooks text field changes (debounced). Local n-gram + small neural LM propose completions; spell module proposes corrections; safety filter; UI renders suggestion strip. User lexicon updates on accepted novel tokens outside deny-fields.",
                    ],
                ),
                (
                    "19.2 Model choices",
                    [
                        "Distilled transformer or RNN LM quantized; or classic Kneser-Ney n-grams for tiny devices. Spell: symmetric delete + noisy channel. Contextual rescoring using LM.",
                    ],
                ),
                (
                    "19.3 Server assist API privacy",
                    [
                        "Send prefix and coarse context_type only—not full message history by default. Rate limit. Edge cache popular prefixes. Logs aggregated/opt-in.",
                    ],
                ),
                (
                    "19.4 Pack pipeline",
                    [
                        "Train → evaluate → quantize → package → sign → CDN → staged device rollout. Metrics include download fail rate and post-update undo rate.",
                    ],
                ),
                (
                    "19.5 Field policy matrix",
                    [
                        "search: assist OK, learn OK (non-PII). chat: assist optional, learn careful. email: suggest careful. password: all off. address: suggest structured, don’t upload raw.",
                    ],
                ),
                (
                    "19.6 Kids devices",
                    [
                        "Fire kids profiles: stricter lexicon, no server assist default, stronger safety lists, parent controls for download packs.",
                    ],
                ),
                (
                    "19.7 Battery & thermal",
                    [
                        "Cap infer time; skip neural on thermal throttle; fall back to dictionary; CI benches on low-end SKUs.",
                    ],
                ),
                (
                    "19.8 Roadmap",
                    [
                        "Better multilingual, on-device personalization without cloud, optional federated improvements, tighter retail search field integration with catalog dictionaries.",
                    ],
                ),
            ],
        )
        + """
## 20. Hybrid Merge Pseudocode

```text
local = device_suggest(prefix, k=8)
if secure_field or not consent or offline or local.conf > T:
    return safety(local)
server = assist(prefix, deadline=120ms)
return safety(merge(local, server, k=8))
```

---

## 21. Pack Manifest

```text
PackManifest {
  locale, version, min_app, size_bytes, signature,
  checksum, features: [lm, spell, safety, catalog_head]
}
```

---
"""
    )


def main():
    mapping = {
        "search-autocomplete-system-design.md": build_search_extra(),
        "realtime-game-leaderboard-system-design.md": build_leaderboard_extra(),
        "alexa-triggering-advertising-workflow-system-design.md": build_alexa_extra(),
        "product-recommender-system-design.md": build_product_extra(),
        "clothing-recommender-system-design.md": build_clothing_extra(),
        "in-flight-movie-recommender-system-design.md": build_inflight_extra(),
        "mobile-autocomplete-spellcheck-system-design.md": build_mobile_extra(),
    }
    for name, extra in mapping.items():
        path = OUT / name
        base = path.read_text()
        # Insert expansion before final end marker if present
        marker = "*End of document"
        if marker in base:
            head, tail = base.split(marker, 1)
            new_content = head.rstrip() + "\n" + extra + "\n" + marker + tail
        else:
            new_content = base.rstrip() + "\n" + extra
        path.write_text(new_content)
        print(f"{name}: {new_content.count(chr(10))+1} lines")


if __name__ == "__main__":
    main()
