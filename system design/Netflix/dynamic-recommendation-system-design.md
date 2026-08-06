# System Design: Dynamic Recommendation System (After Profile Selection)

> **Focus areas:** Profile-scoped context · Multi-stage candidate generation · Ranking · Page construction · Nearline Continue Watching · Diversity / dedup · Cold start · Experiments · Non-empty fallbacks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split page/CW/feature/ANN QPS, explicit deal-breaker (no full-catalog online DNN), Netflix personalization 2025–26 themes  
> **Interview theme:** After the user picks a profile, build a personalized homepage (and related rails) under tight latency with kids/safety fail-closed

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

Goal: **bound personalization after profile selection**—assemble rows that feel instant, respect maturity/entitlements, update Continue Watching quickly, and never show a blank homepage when models brown out.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Trigger | Profile select / app open / row refresh | Search SERP ranking |
| Unit | **Profile** (+ device/session) | Account-level one list for household |
| Planes | Retrieve → filter → rank → page construct | One model scores entire catalog online |
| Ads | Orthogonal ads-tier pods unless asked | Joint ads auction inside every row |
| Dedup | Page-level title uniqueness (integrate) | Deep viewport pagination sibling |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | When compute? | On profile select + refreshes; warm cache OK | Page service + fragment cache |
| F2 | Surfaces? | Homepage rows, CW, BYW, trending, new | Row templates + CG registry |
| F3 | Profile isolation? | Hard isolation; kids separate | `profile_id` everywhere |
| F4 | Cold start? | New profile / title / region | Priors + onboarding + exploration caps |
| F5 | Session signals? | Plays, pauses, previews, search, Not Interested | Nearline features |
| F6 | Evidence? | Optional “Because you watched X” | Evidence ids; not critical path |
| F7 | Entitlements? | Country license + maturity | Filter before finalize |
| F8 | Diversity? | Avoid same title in many rows | Page constructor dedup |
| F9 | Experiments? | Algo / layout A/B | Sticky assignment + log stamp |
| F10 | Offline vs online? | Batch candidates + online rank/page | Hybrid mandatory |
| F11 | Negative feedback? | Hide / Not Interested | Suppression store |
| F12 | Degradation? | Never blank | Popular/trending fallbacks |

**MVP functional scope:**

1. Authenticated **profile-scoped homepage** with N rows (CW + personalized + popular).  
2. Multi-stage **retrieve → filter → rank → page construct**.  
3. Nearline **Continue Watching** (minutes or better).  
4. Entitlement + **kids maturity fail-closed**.  
5. Server-side **above-the-fold dedup**.  
6. Async impression/play logging; experiment hooks.  
7. Brownout → non-empty degraded page.

**Out of MVP:**

- Full page-level transformer as only path  
- Perfect household taste splitting beyond profiles  
- On-device primary ranker  
- Joint organic+ads auction (keep separate)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Homepage after profile select | Feels instant | Server p99 < 400–500ms; UX < 1s warm |
| N2 | Availability | Always a page | 99.9% with fallbacks |
| N3 | CW freshness | Near realtime | Typically < 1–5 min |
| N4 | Personalization freshness | Batch hours; nearline minutes | Tiered |
| N5 | Privacy | No cross-profile leak | Authz + cache keys |
| N6 | Cost | Sustainable globally | $/1K page builds |
| N7 | Safety | Kids never see adult | 0 tolerance violations |
| N8 | Experiment safety | Kill switches | Guardrail auto-rollback |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Pick profile → page with CW + personalized rows → play → CW updates.  
2. Finish episode → next episode appears in CW promptly.  
3. Not Interested → suppressed on later builds.  
4. Experiment model B → sticky + stamped logs.  
5. Kids profile → only allowed maturity; no adult evidence.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Feature store timeout | Defaults; still build page |
| Ranker 503 | Popular within genres; degrade flag |
| Entitlement miss | Filter; never show unplayable |
| Duplicate title across CGs | Constructor dedups above-fold |
| Premiere thundering herd | Cache fragments; protect CW path |
| Stale ANN index | Max-age; fallback co-watch/popular |
| Rapid profile switch | Cancel in-flight; cache by profile |
| Empty CG results | Expand popular; never empty shell |
| CDN caches personalized page anonymously | **Deal-breaker** — must vary by profile |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 10M | 100M | 400M | 1B |
| Peak page builds/s | 20K | 200K | 2M | 20M |
| Profiles | 80M | 800M | 3B | 10B |
| Catalog titles | 15K | 50K | 200K | 1M |
| Rows / page | 15–30 | same | same | more modules |
| Candidates pre-rank / row | 500–2K | same | distilled | ANN+filters |
| Feature keys hydrated / page | 2K–20K | same | compressed | partial/edge |

**What each jump forces:**

- **10×:** Row-fragment cache; ANN; batched feature hydration; CG timeouts.  
- **100×:** Profile cells; regional page builders; distilled rankers; precompute top rows.  
- **1,000×:** Edge page shells; hierarchical candidate stores; heavy precompute + light online rerank.

### 1.5 Etc. (Constraints & Assumptions)

- Global licensing + maturity ratings.  
- Ads plan may inject pods separately.  
- Sibling: homepage dedup / viewport pagination.

**Scope statement:**

> Design a profile-scoped dynamic recommendation and page-construction system that returns a personalized homepage after profile selection, with multi-stage retrieval, nearline Continue Watching, server-side dedup, kids fail-closed filters, and progressive scale through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Page-build QPS

```text
DAU 10M; ~3 homepage builds / DAU / day
Avg = 10e6 × 3 / 86400 ≈ 347 QPS
Evening peak ×5 → ~1.7K QPS average-class
Product peaks with prefetch/retry: plan **~20K page builds/s** baseline peak
```

At **100×** → **2M/s** — requires heavy fragment cache / precompute.

### 2.2 Latency budget

| Stage | Budget |
|-------|--------|
| Auth + profile context | 5–10ms |
| Parallel CG retrieve | 20–40ms |
| Feature hydrate | 20–40ms |
| Rank | 20–40ms |
| Page construct + dedup | 5–15ms |
| **Server total p99** | **≤400–500ms** |

### 2.3 Why not full-catalog scoring

```text
Catalog 50K × 200K pages/s = 10B score ops/s → absurd
Multi-stage: retrieve K≤2K per row → rank top → show ~8 arts
```

### 2.4 Logging volume

```text
20K pages/s × 20 rows × 8 titles ≈ 3.2M impressions/s peak (upper)
Sample/compact; stream to warehouse; never block response on log ACK
```

### 2.5 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Page build | 20K | 2M | 20M | cache heavily |
| CW read | 50K | 5M | 50M | hot per profile |
| Feature get | 100K | 10M | 100M | batch |
| ANN query | 40K | 4M | 40M | per CG |
| Event ingest | 200K | 20M | 200M | aggregatable |

### 2.6 Storage sketch

```text
CW: 80M profiles × ~20 entries × 64B ≈ 100GB class
Profile embeddings: 80M × 512×4B ≈ 160GB
Title embeddings: 50K × 512×4B ≈ 100MB (tiny)
```

### 2.7 Bottlenecks

1. Feature fan-out  
2. Personalized pages resisting naive CDN  
3. CG timeout cascades  
4. Feedback loops amplifying popular titles  
5. Kids filter bugs (severity-0)

### 2.8 Cost

```text
$/1K page builds = ANN + rank CPU + feature reads
Fragment cache hit can cut rank cost 5–20× on revisits
```

---

## 3. High-Level Design

### 3.1 Pipeline

```text
Profile select → Context (profile, geo, device, maturity, experiments)
  → Parallel CGs (CW, BYW, two-tower ANN, trending, editorial)
  → Filter (entitlement, maturity, suppressions, availability)
  → Ranker (per-row objectives)
  → Page Constructor (order, dedup, diversity, exploration)
  → Response + async logs
```

### 3.2 Candidate generators

| CG | Signal | Freshness | Killable |
|----|--------|-----------|----------|
| Continue Watching | playback position | seconds–minutes | stub only |
| Because You Watched | item-item / embeddings | hours–day | yes |
| Top Picks | profile embedding | hours | yes |
| Trending | regional velocity | minutes | yes |
| New Releases | catalog | minutes | yes |
| Editorial | human + rules | publish | yes |

Each CG: **budget**, **timeout**, **kill flag**. Slow CG dropped.

### 3.3 Ranking

Multi-task heads: P(play), P(complete), dislike risk, satisfaction proxy. Calibrate kids vs adult. Do **not** optimize artwork CTR alone.

| Approach | When |
|----------|------|
| GBDT / linear | MVP / fallback |
| Two-tower + MLP rerank | Default 10× |
| Page transformer | Above-fold selectively at 100× |

### 3.4 Page construction

Row templates define slots. Constructor enforces maturity, **title dedup**, genre diversity, series constraints, exploration slots. Deterministic given inputs (testable).

### 3.5 Precompute vs online

| Artifact | Where | TTL |
|----------|-------|-----|
| Profile embedding | feature store | hours |
| Row candidate lists | offline/nearline | hours |
| CW list | online KV | seconds–minutes |
| Final page JSON | short cache keyed by profile+versions | 30–120s |
| Title metadata/art | CDN | long |

**Deal-breaker:** CDN personalize without `Vary`/keyed by profile → cross-profile leak.

### 3.6 Cold start

- New profile: onboarding genres → geo popular priors.  
- New title: metadata embeddings + capped exploration.  
- New region: local popular + transfer embeddings.

### 3.7 Experiments

Sticky on `profile_id`. Stamp `experiment_ids`, `model_version` on logs. Guardrails: CW quality floor; kids invariants outside experiments.

### 3.8 Degradation

| Signal | Action |
|--------|--------|
| Ranker slow/down | Pre-ranked / popular |
| ANN down | Co-watch graph + trending |
| Feature store down | Defaults + CW-heavy page |
| Catalog filter uncertain (kids) | Fail closed |

### 3.9 Trade-offs

| Topic | Choice |
|-------|--------|
| Key | **profile_id** |
| Assembly | **Hybrid** precompute + online |
| Dedup | **Server** constructor |
| Logging | **Async** |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+  profile select  +----------+    +--------------+
| Client |----------------->| Edge/BFF |--->| Page Service |
+--------+                  +----+-----+    +------+-------+
                                 |                 |
                                 v                 v
                          +--------------+  +------+-------+
                          | Exp Assign   |  | Context Svc  |
                          +--------------+  +------+-------+
                                                   |
        +--------------------+---------------------+------------------+
        v                    v                     v                  v
  +-----------+        +-----------+         +-----------+      +----------+
  | CW Store  |        | CG Fanout |         | Feature FS|      | Catalog/ |
  +-----------+        | ANN/Graph |         +-----------+      | Entitle  |
                       +-----+-----+                            +----------+
                             v
                       +-----+-----+
                       | Ranker    |
                       +-----+-----+
                             v
                       +-----+-----+
                       | Page Build|--> dedup / diversity
                       +-----+-----+
                             |
                             +--> async logs --> training
```

### 4.2 Sequence: homepage build

```text
Client→BFF: GET /homepage?profile_id
BFF→Page: build(profile, device, geo)
Page→CGs: parallel retrieve (timeouts)
Page→Filters: entitlement/maturity/suppress
Page→Features: batch hydrate
Page→Ranker: score per row
Page→Constructor: dedup + layout
Page→Client: rows + model_version + exp ids
Page→Log: async impressions
```

### 4.3 Nearline Continue Watching

```text
Player ping/stop → Event bus → CW updater (idempotent by position version)
CW KV[profile] = ordered titles with position + updated_at
Page reads CW with short timeout; stale-while-revalidate OK
```

### 4.4 Cache key

```text
page_cache_key = hash(profile_id, row_set_version, model_version, locale, maturity)
Invalidate CW row fragment on CW update; short TTL on full page
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Profile isolation** — never leak CW/personalization across profiles.  
2. **Kids fail closed** on maturity/entitlement uncertainty.  
3. **Non-empty homepage** under brownout.  
4. **Unplayable titles never shown**.  
5. **Idempotent CW updates** with monotonic position versions.  
6. **Model/config versions stamped** on response + logs.  
7. **Sticky experiments** for assignment duration.  
8. **Deterministic dedup** for same inputs.

| Failure | Behavior |
|---------|----------|
| Ranker down | Popular + CW; degrade flag |
| CW store down | Omit/cached CW |
| Feature timeout | Defaults |
| Log pipeline down | Serving continues |
| Bad canary | Auto rollback on guardrails |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Page service, Redis CW, feature store, batch CG jobs |
| 10× | ANN; feature cache; row fragments; CG timeouts |
| 100× | Profile cells; regional builders; distilled rankers |
| 1,000× | Edge shells; hierarchical CGs; light online rerank |

### 5.3 Maintainability

- Row templates as data.  
- CG registry with budgets/timeouts/kills.  
- Feature schema versioning.  
- Offline page-build replay for debugging.  
- Metrics: `page_build_latency`, `cg_timeout_rate`, `fallback_rate`, `dedup_drop_rate`, `empty_row_rate`, `kids_violation_rate` (=0).

### 5.4 Training & feedback

Labels from starts/completion/dismiss. Counterfactual logging for exploration. Separate kids models. Delay-aware watch-time labels.

### 5.5 Integration with dedup siblings

Page constructor owns above-the-fold uniqueness. Viewport pagination sibling extends to infinite scroll without repeating shown titles.

### 5.6 Multi-region

Catalog/entitlement regional. Profile home cell for CW writes. Page builds near user with replicated features.

### 5.7 Security / privacy

Profile authz on every call. Personalization payloads not world-cacheable. Organic logs don’t join ads identity without policy.

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Full-catalog online DNN | Latency/cost melt |
| Anonymous CDN of pages | Profile leak |
| Client-only dedup | Inconsistent / empty UX |
| Block response on logging | Availability loss |
| Share kids/adult embeddings unfiltered | Safety incident |

### 5.9 Progressive deep dive

**1×:** Modular page service; Redis CW; nightly CG materialization; GBDT rank.  
**10×:** Two-tower ANN; fragment cache; strict CG deadlines.  
**100×:** Cells; precompute Top Picks lists hourly; online diversity only.  
**1,000×:** Edge shell with signed row fragments; on-device tiny features optional.

### 5.10 Data model sketch

```text
profiles(profile_id, account_id, maturity, prefs, home_region)
cw_entries(profile_id, title_id, position_sec, version, updated_at)
suppressions(profile_id, title_id, reason, ts)
profile_features(profile_id, vector, updated_at)
title_features(title_id, embeddings, metadata)
row_templates(row_id, cg_ids[], ranker_id, rules)
experiment_assignments(profile_id, exp_id, bucket, ts)
```

### 5.11 Ranking objective notes

```text
score = w1*P(play) + w2*P(complete) - w3*P(dislike) + exploration_bonus
kids: hard mask before score
filter unplayable before rank finalize (or as -inf)
```

### 5.12 Ownership

| Concern | Owner |
|---------|-------|
| Page service / constructor | Personalized page |
| CGs / rankers | Algo / ML |
| CW store | Playback + personalization |
| Entitlement/maturity | Catalog / kids safety |
| Experiments | Experimentation platform |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Key | profile_id isolation |
| Architecture | multi-stage retrieve→rank→page |
| CW | nearline KV, monotonic versions |
| Dedup | server page constructor |
| Degradation | popular/trending non-empty |
| Kids | fail closed |

### 6.2 Risks

1. Popularity feedback loops  
2. Feature staleness after travel  
3. Over-aggressive dedup → sparse pages  
4. Impression log cost at peak  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Profile vs account; kids; surfaces |
| 5–15 | Multi-stage HLD + CGs |
| 15–25 | Page construct, dedup, latency |
| 25–35 | CW, features, scale jumps |
| 35–45 | Failures, experiments, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Product

**Q: Why profile not account?**  
A: Households share accounts; taste and maturity differ.

**Q: Empty page prevention?**  
A: CG timeouts, mandatory fallback CGs, last-good fragments, degrade flags.

**Q: Where is dedup?**  
A: Server constructor for above-fold; client assist OK but server SoT in interview.

### 7.2 ML

**Q: Online full-catalog DNN?**  
A: Deal-breaker. Retrieve+rank.

**Q: Cold start title?**  
A: Metadata embeddings + capped exploration + editorial.

**Q: Offline evaluation?**  
A: Replay + counterfactual; online A/B on starts/completion/satisfaction.

### 7.3 Systems

**Q: Cut p99?**  
A: Fragment cache, batch features, slim ranker, CG budgets, precompute.

**Q: Logging exactly-once?**  
A: At-least-once + dedupe; serving independent of log ACK.

**Q: Multi-region licensing?**  
A: Filter entitlements before finalize.

### 7.4 Safety

**Q: Kids see adult row?**  
A: Sev-0; fail closed; independent audit tests; invariant outside experiments.

**Q: Evidence leakage?**  
A: Don’t cite adult titles on kids profiles.

### 7.5 Experiments

**Q: Sticky how?**  
A: Assignment service keyed by profile; duration policy; stamp logs.

**Q: Guardrails?**  
A: Auto-disable on CW collapse / kids violation / error spike.

### 7.6 Ads interaction

**Q: Ads in rows?**  
A: Usually separate decisioning; organic ranker shouldn’t secretly optimize ad CTR.

### 7.7 Device

**Q: TV vs mobile?**  
A: Device-class features and row counts; same profile embeddings.

### 7.8 Search vs recs

**Q: Shared infrastructure?**  
A: Shared embeddings/features; different objectives and triggers.

### 7.9 Fraud

**Q: Bot plays?**  
A: Filter training labels; don’t let bots shape rankers.

### 7.10 Traps

| Trap | Pushback |
|------|----------|
| CDN homepage globally | Profile leak |
| One QPS number | Split classes |
| CTR-only objective | Hurts completion |
| Synchronous training | Not needed for MVP serving |

### 7.11 Continue Watching specifics

**Q: Idempotent position?**  
A: Version/timestamp monotonic; ignore regressions from stale players.

**Q: Series next-episode?**  
A: Catalog rules + progress; CW can show next logical episode.

### 7.12 Diversity

**Q: vs relevance?**  
A: Constrained re-rank with quotas; measure both offline and online.

---

## 8. Appendices

### A1. Row template example

```text
row:
  id: top_picks
  cgs: [two_tower, pvr_batch]
  ranker: multitask_v4
  rules: {dedup:true, min_titles:6, exploration:0.05}
```

### A2. Launch checklist

- [ ] Kids maturity filters tested  
- [ ] CG timeouts + fallbacks verified  
- [ ] Dedup unit tests for viewport  
- [ ] Model rollback armed  
- [ ] CW monotonic version tested  
- [ ] p99 dashboards + fallback_rate  

### A3. Glossary

| Term | Meaning |
|------|---------|
| CG | Candidate generator |
| PVR | Personalized video ranker / top picks style |
| Nearline | Seconds–minutes async path |
| Page constructor | Assembles rows + dedup |
| Fragment cache | Cached partial rows |

### A4. Interviewer traps

| Trap | Pushback |
|------|----------|
| Score all titles online | Multi-stage only |
| Anonymous page CDN | Key by profile |
| Client-only dedup | Server SoT |
| Block on logging | Async |

### A5. Reliability tests

1. Kill ranker → non-empty fallback.  
2. Inject adult into kids candidates → filtered.  
3. Duplicate title in 3 CGs → one above-fold.  
4. CW retry → no position regression.  
5. Feature 100% timeout → HTTP 200 pages.

### A6. 60-second summary

> After profile selection, a **page service** fans out to timed **candidate generators**, filters entitlements/maturity, hydrates features, **ranks**, then **constructs a deduplicated page** with non-empty fallbacks. Continue Watching is nearline; heavy personalization is hybrid; scale via caches, cells, distillation — never full-catalog online scoring.

### A7. Related systems

```text
Client → BFF → Page Service → CGs/ANN + CW + Features + Catalog
Page → Ranker → Constructor → Client
Events → CW updater + Train warehouse
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Page build p99 | < 500ms |
| Availability | 99.9% |
| Kids violations | 0 |
| CW freshness p95 | < 5 min |
| Fallback rate | visible but bounded |

### A9. Feature groups

```text
User: affinity genres, language, device class, tenure
Context: time-of-day, country, session depth
Item: genre, embedding, popularity, novelty
Cross: past interacts with item/similar
```

### A10. Ownership RACI

| Concern | Owner | Consulted |
|---------|-------|-----------|
| Serving correctness | Page team | Client |
| Model quality | Algo | Page |
| Kids safety | Kids + Catalog | Page |
| Cost | Page | FinOps |

### A11. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Multi-stage, CW, filters, fallbacks |
| 10× | ANN, fragment cache, CG deadlines |
| 100× | Cells, distillation, precompute |
| 1,000× | Edge shells, hierarchical CGs |

### A12. Pseudo APIs

```text
GET /v1/homepage?profile_id=&device=&locale=
POST /v1/suppressions {profile_id, title_id, reason}
GET /v1/cw?profile_id=
```

### A13. Event schemas

```text
PlayEvent {profile_id, title_id, position, version, ts}
ImpressionEvent {request_id, profile_id, row_id, title_id, rank, model_version, exp_ids[]}
```

### A14. On-call cheat sheet

1. Check fallback_rate and page p99 by region.  
2. Verify model_version / kill switches.  
3. CG timeout heatmap — disable bad CG.  
4. Kids violation alert → immediate fail-closed mode.  
5. CW lag → check event bus / updater lag.

### A15. Comparison naive

| Naive | Failure |
|-------|---------|
| Single collaborative filter nightly | Stale CW; slow iteration |
| Client sorts catalog | Incomplete catalog; cheat; battery |
| One DNN all titles | Won’t meet latency |

### A16. Worked example

```text
Profile P kids maturity=7
CGs return titles including mature M
Filter drops M before rank
Constructor fills row from remaining + popular kids
```

### A17. Cache poisoning note

Fragment cache must include maturity and experiment versions or risk wrong-profile content.

### A18. Cost worksheet

```text
page_pods ∝ peak_qps × latency_ms / (1000 × cores × util)
ann_nodes ∝ ann_qps × cost_per_query
feature_cache_mem ∝ hot_profiles × bytes
```

### A19. Explicit non-goals

- Replacing search  
- Being ads serving  
- Perfect causal explanations UI  

### A20. Scoring rubric (self-check)

- Clarified profile vs account  
- Rejected full-catalog online scoring  
- Named kids fail-closed  
- Split QPS classes  
- Showed 10×/100×/1000× path  

---

*End of document — Netflix system design interview prep: Dynamic Recommendation System.*
