# System Design: Clothing Recommender System (Amazon Fashion)

> **Focus areas:** Style embeddings · Size/fit · Seasonality · Visual similarity · Catalog attributes · Returns-aware ranking · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Explicit fit/season constraints, visual+tabular fusion, deal-breakers for “generic product CF only”
> **Interview theme:** Amazon SDE III / L6 — **Amazon Fashion** personalization—style & fit & seasonality with visual ML and returns-aware objectives

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

Goal: design a **clothing / fashion recommender** that accounts for **style, size/fit, seasonality, and visual similarity**, not just co-purchase patterns.

### 1.0 Differentiation vs generic product recs

| Dimension | Clothing | Generic product |
|-----------|----------|-----------------|
| Fit | Critical (size, body) | Rarely |
| Visual | Primary | Secondary |
| Season | Strong | Weak |
| Returns | High cost signal | Lower |
| Style affinity | Latent taste | Category affinity |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Surfaces? | Fashion home, PDP outfit, style match | Specialized CGs |
| F2 | Size? | Use size profile / past fit | Fit filter/boost |
| F3 | Visual? | Image embeddings | ANN visual |
| F4 | Season? | Locale + calendar + weather | Season features |
| F5 | Outfit? | Complementary items | Pair model |
| F6 | Style? | Latent style clusters | Style tower |
| F7 | Returns? | Optimize fit satisfaction | Return-aware labels |
| F8 | Inclusivity? | Size availability diversity | Inventory-aware |
| F9 | Trends? | Nearline trend spikes | Trend CG |
| F10 | Cold start? | New SKUs via visual/attributes | Content path |
| F11 | Gender/dept? | Sensitive; prefer explicit browse context | Careful features |
| F12 | Marketplace? | Localized fashion | Cells |
| F13 | Latency? | Similar to retail widgets | Multi-stage |
| F14 | Modesty/safety? | Policy filters | Safety |
| F15 | Experiment? | Yes | Exp platform |

**MVP:** visual similar + style personalization + size-aware filter + season boost + returns-aware rank head on fashion surfaces.

### 1.2 NFRs

p99 widget < 150–200ms; fit filter correctness > vanity CTR; availability of size variants checked; high return-rate guardrail.

### 1.3 Cases

Happy: view dress → visually similar in season + size available; homepage style rail; outfit “complete the look”.

| Case | Behavior |
|------|----------|
| Size unavailable | Show alt sizes or similar cut with stock |
| Off-season swimwear in winter (locale) | Demote unless tropical context / intentional browse |
| High return ASIN | Demote unless strong intent |
| Body/size cold start | Ask-friendly UX + segment priors; don’t assume |
| Counterfeit / policy | Block |

### 1.4 Scales

Similar QPS to product recs but heavier embedding traffic; image ANN indexes large; seasonality shifts peaks (Prime Day fashion, holidays).

| Metric | Base | 10× | 100× |
|--------|------|-----|------|
| Fashion recs QPS | 50K | 500K | 5M |
| Image embedding dim | 256–512 | — | — |
| ANN vectors | 100M styles | 200M | cells |

---

## 2. Back-of-the-Envelope Estimation

Visual ANN: 100M vectors × 512 × 4B ≈ 200 GB (plus indexes). Shard by marketplace/department. Ranker still scores hundreds of cands—not full catalog.

Latency budget mirrors product recs with extra visual CG parallelized.

Returns join: order line → return reason codes → training labels delayed days–weeks.

---

## 3. High-Level Design

### 3.1 Extra components beyond generic recs

| Component | Role |
|-----------|------|
| Visual Embedding Service | Image → vector |
| Visual ANN | Similar styles |
| Size/Fit Profile | Customer size graph |
| Seasonality Service | Locale calendar/weather |
| Outfit / Complement Model | Tops↔bottoms |
| Returns-aware Rank Head | P(return\|fit) |
| Attribute Normalizer | Color, material, cut |

### 3.2 Flow

```text
Request → Context (locale, season, size profile)
  → CG visual ANN ∥ CG CF ∥ CG trend ∥ CG outfit
  → Fit/inventory filter
  → Rank (style + purchase - return risk)
  → Diversity (color/brand/price)
  → Response
```

### 3.3 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| CF only | **CF + visual + fit** | CF-only fashion |
| Size | Filter when known | Ignore fit |
| Season | Soft boost + hard for extremes | None |
| Returns | In objective | CTR-only |

---

## 4. Architecture Diagram

```text
Fashion Surface --> Recs API --> Size/Fit Profile
                           --> Seasonality
                           --> Visual ANN  --\
                           --> CF/Two-Tower --+--> Filter fit/OOS --> Rank --> Diversify
                           --> Outfit CG   --/
                                 |
                                 v
                           Returns-aware training loop
```

---

## 5. Design Deep Dive

### 5.1 Fit modeling

Size profile from purchases kept + returns (“too small”). Variant-level inventory (SKU size/color). Recommend style with available size, not parent ASIN only.

### 5.2 Visual embeddings

Train on fashion catalog images; augment; domain-specific backbone; ANN HNSW/IVF; refresh on new images nearline.

### 5.3 Seasonality

Features: month, hemisphere, weather band, event calendars. Browse intent can override (customer shopping swimwear in winter intentionally).

### 5.4 Outfit recommendations

Pair compatibility model using co-purchase + visual harmony + color theory heuristics as weak priors.

### 5.5 Progressive scale

Shard ANN; distill visual encoders; cache style rails for segments; cells per marketplace.

### 5.6 Ethics / sensitivity

Avoid harmful body inference from images of customers; use declared/past purchase sizes with privacy care. Gender stereotypes: prefer contextual browse signals.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        Amazon Fashion **clothing recommendations** with visual ANN, style models, size/fit profiles, seasonality, outfit complements, and returns-aware ranking on top of multi-stage retrieval.

        ### 6.2 Key decisions worth defending

        1. Fashion ≠ generic CF
2. Variant-level inventory + fit filters
3. Visual embeddings as first-class CG
4. Seasonality with intent overrides
5. Returns in the objective

        ### 6.3 Risks & follow-ups

        - Attribute quality debt
- Size cold start UX
- Trend vs fit conflicts
- Sensitive demographic inference risks

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **Clothing Recommender** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---

## 7. Deeper / Related Interview Questions

**Q1. Why can’t we reuse the generic product recommender unchanged?**

**A:** Fit, visual style, seasonality, and returns dominate fashion economics. Pure CF recommends wrong sizes/seasons and drives returns.

**Q2. How do you encode size?**

**A:** Normalized size schemas per garment type; customer size vectors; compatibility scores; hard filter when confidence high.

**Q3. Visual similar but wrong season?**

**A:** Re-rank with season features; optional hard filter for extreme mismatches unless intent overrides.

**Q4. Optimize for returns?**

**A:** Multi-objective: P(purchase) - λ P(return) + satisfaction; guardrail max return-rate in experiments.

**Q5. Cold-start garment?**

**A:** Visual+attribute ANN; influencer/trend tags; explore quota.

**Q6. Deal-breaker?**

**A:** Ignoring size availability; or CTR-only objective that increases returns.

---

        ## 8. Appendices

        ### Appendix A — Glossary

        | Term | Meaning |
        |------|---------|
        | Two-pizza team | Ownership team with pager |
        | Cell | Failure-isolated unit |
        | Nearline | Minutes-latency path |
        | Shadow | Score without user impact |
        | Canary | Partial traffic bake |
        | Deal-breaker | Non-negotiable bad design |

        ### Appendix B — Estimation cheat-sheet

        ```text
        QPS_peak ≈ DAU × actions/day / 86400 × peak_factor
        Storage ≈ rows/day × bytes × retention
        ```

        ### Appendix C — Oncall checklist

        - [ ] SLOs green
        - [ ] Canary/rollback armed
        - [ ] Kill switches known
        - [ ] Blast radius mapped
        - [ ] Cost dashboards
        - [ ] Privacy/safety paths tested

        ### Appendix D — LP mapping

        | LP | Signal |
        |----|--------|
        | Customer Obsession | Trust + latency under failure |
        | Ownership | Clear pager |
        | Dive Deep | Correct math + invariants |
        | Frugality | Unit cost metrics |

        ### Appendix F — Size profile sketch

```text
FitProfile { customer_id, garment_type → size, confidence, updated_at }
SkuVariant { style_id, size, color, inventory }
```

### Appendix G — Closer checklist

- [ ] Visual + CF channels
- [ ] Size/fit filters
- [ ] Seasonality
- [ ] Returns-aware objective
- [ ] Variant inventory
- [ ] Sensitivity/ethics note



## Extended Notes — Clothing Recommender

### E1. Two-stage retrieval

Candidate generation (ANN/CF/graph) → ranking (GBDT/DNN) → re-rank (business rules). Defend why one giant model is a deal-breaker for ops and latency.

### E2. Training-serving skew

Feature store with point-in-time correctness; freeze feature versions in logs; shadow diffs.

### E3. Feedback loops

Exposure bias, position bias—use propensity weighting / randomized exploration carefully.

### E4. Cold start

New ASINs: content features; new users: popular in segment + contextual.

### E5. A/B & interleaving

Amazon experimentation culture—layer experiments; guardrail metrics (latency, diversity, complaints).

### E6. Ownership

Retrieval team vs ranker team vs surface owners (homepage/PDP/email); clear contracts on candidate budgets.

### E7. Attribute quality

Fashion taxonomy messiness (color aliases)—invest in attribute normalization; garbage attributes wreck filters.

### E8. UCG images vs studio

Embeddings should be robust; prefer studio for index, UGC for social proof separately.

### E9. Plus-size / inclusive inventory

Diversity constraints ensuring available inclusive sizes aren’t drowned by majority stock.

### E10. Counterfeit & brand

Trust signals in re-rank; policy blocks.

### E11. Weather partnership

Optional weather API as context feature with cache.

### E12. Mobile visual search adjacent

Same embeddings can power camera search—shared embedding platform ownership.

### E13. Prime try-before-you-buy

If exists, labels differ from hard purchases—model separately.

### E14. Trend detection

Nearline velocity on styles; don’t let trends violate fit filters.

### E15. Evaluation

Offline AUC insufficient—fashion needs fit proxy metrics + human style eval panels.

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


## 16. Additional Deep Q&A — Clothing Recommender

### Q1. How do you normalize sizes across brands?

Garment-type-specific charts; brand offset models learned from returns (‘too small/large’); store both labeled size and normalized size embedding.

### Q2. What if visual similar is wrong colorway season?

Visual ANN for style cut/pattern; re-rank with color seasonality and inventory; allow intent override when user browsed that color.

### Q3. Outfit model supervision?

Co-purchase in fashion sessions, stylist sets, and weak visual harmony scores; evaluate with human style panels not only CTR.

### Q4. How to avoid stereotyping?

Prefer explicit browse/context over inferred sensitive attributes; careful with gendered category forcing; offer neutral discovery rails.

### Q5. Inventory at SKU vs style?

Recommend style but ensure at least one feasible SKU in customer size; deep-link to available variant.

### Q6. Trend vs classic wardrobe?

Explore slot for trends; core rank still fit/satisfaction; don’t let TikTok velocity blow up return rates.

### Q7. Image embedding refresh?

New images nearline embed + ANN upsert; full reindex periodically; version embeddings to avoid mixed spaces.

### Q8. Returns delay in labels?

Train on delayed labels; use interim proxy (size message, early return signals); keep online model stable.

### Q9. Cold-start customer without size?

Ask-friendly UX; segment priors; soft constraints until confidence rises; never hallucinate body measurements from photos of the customer.

### Q10. Deal-breaker reminder?

Generic product CF without fit/visual/season—fashion returns will punish you.

## 17. Scenario Drills — Clothing Recs

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Winter swimwear browse | Intent override season demotion | Context matters |
| Size OOS for popular style | Alt sizes / similar cut in stock | Variant truth |
| Return-rate spike after model | Rollback; raise λ on P(return) | Guardrails |
| Bad attribute color data | Trust visual more; fix taxonomy | Data quality |

## 18. Final Checklist — Clothing Recs

- [ ] Visual ANN channel
- [ ] Size/fit profile + SKU inventory
- [ ] Seasonality with overrides
- [ ] Returns-aware objective
- [ ] Outfit complements
- [ ] Sensitivity/ethics constraints
- [ ] Attribute normalization plan
- [ ] Fashion ≠ generic recs stated early

## 19. Expanded Design Notes — Clothing Recs

### 19.1 Fashion taxonomy realities

Colors like ‘bordeaux’ vs ‘wine’ vs ‘dark red’ break filters. Invest in synonym graphs and embeddings over brittle exact matches. Materials and occasion tags are similarly messy.

### 19.2 Visual pipeline

Ingest studio images → crop/background normalize → embedding model → ANN. Use additional towers for close-up texture if needed. Protect against duplicate listings.

### 19.3 Fit confidence

Confidence grows with kept purchases and explicit size settings. Low confidence → soft boosts not hard filters. High confidence → hard filter unavailable sizes.

### 19.4 Season engines

Calendar + hemisphere + optional weather band. Event peaks (wedding season, back-to-school) as features. Tropical locales differ from northern US.

### 19.5 Evaluation human-in-loop

Style judges rate outfit coherence; fit specialists review size logic; combine with online AB. Pure offline AUC will greenlight ugly wrong-season bundles.

### 19.6 Mobile visual search synergy

Same embeddings power ‘shop the look’ camera features—platformize embeddings as a shared service with versioning.

### 19.7 Seller ecosystem

Private label vs 3P apparel; ensure small brands can be retrieved via visual/attribute not only sales CF entrenchment.

### 19.8 Roadmap

Better body-aware fit without invasive data; generative outfit visualization; try-on AR hooks—keep privacy first.

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

*End of document — Clothing Recommender (SDE III)*
