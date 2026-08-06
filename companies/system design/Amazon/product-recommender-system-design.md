# System Design: Product Recommender System (Amazon Retail)

> **Focus areas:** Candidate generation · Ranking · Feature store · Real-time personalization · Cold start · Diversity · Business rules · Experimentation · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split retrieve/rank/re-rank planes, correct QPS math, deal-breakers for “one DNN scores entire catalog online”
> **Interview theme:** Amazon SDE III / L6 — **Retail Personalization / Recommendations** ownership—customer-obsessed relevance with marketplace constraints and unit economics

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

Goal: design Amazon **product recommendations** across surfaces (homepage, PDP “customers also bought”, cart, email) with multi-stage ML, feature platforms, business rules (OOS, policy), and experimentation.

### 1.0 What this is / is not

| Dimension | **Product recommender** | Not this |
|-----------|-------------------------|----------|
| Job | Personalized ASIN recommendations | Search SERP ranking |
| Success | Relevance, conversion, satisfaction, diversity | Max CTR only |
| Planes | Retrieve → rank → re-rank | Single model over full catalog online |
| Amazon lens | Customer trust, Prime, marketplace fairness, cost | Pure academic CF |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Surfaces? | Home, PDP, cart, email | Surface-specific rankers |
| F2 | Inputs? | User history, context, item | Feature store |
| F3 | Outputs? | Ranked ASINs + explanations hooks | Response schema |
| F4 | Freshness? | OOS nearline; models hours–days | Dual freshness |
| F5 | Business rules? | OOS, blocked, age, geo | Re-rank filters |
| F6 | Diversity? | Category/brand diversity | MMR / constraints |
| F7 | Cold start? | New users/items | Content + segment popularity |
| F8 | Realtime signals? | Session clicks | Stream features |
| F9 | Explanations? | Optional “because you viewed” | Rule-based labels |
| F10 | Experiments? | Continuous A/B | Exp platform |
| F11 | Multi-marketplace? | Yes | Cells |
| F12 | Sponsored? | Optional labeled | Ads merge policy |
| F13 | Latency? | Surface-dependent | Budgets |
| F14 | Privacy? | Purpose-limited profiles | TTLs |
| F15 | Feedback? | Purchase/return/click | Label pipelines |

**MVP:** PDP + homepage widgets; 2-stage retrieve+rank; OOS filter; session features; logging; A/B hooks.

### 1.2 NFRs

| Surface | p99 |
|---------|-----|
| PDP widget | < 100–150 ms |
| Homepage module | < 200–300 ms (parallel) |
| Email (offline) | hours OK |

Availability high; degrade to popular/similar. Cost: infer $/1K recommendations.

### 1.3 Cases

Happy: view ASIN → related items; homepage personalized rail; cart cross-sell.

| Case | Behavior |
|------|----------|
| OOS | Filter/replace |
| Gift shopping | Session intent demotes personal history |
| Filter bubble | Diversity constraints |
| New ASIN | Content kNN |
| Bot traffic | Downweight training |

### 1.4 Scales

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Recs QPS | 200K | 2M | 20M | cells+edge |
| Catalog ASINs | 400M | — | — | growth |
| Candidates/request | 500–2000 | — | — | multi-channel |
| Feature reads/s | 2M | 20M | 200M | cached |

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Planes

| Plane | Work |
|-------|------|
| Online retrieve | ANN / inverted / CF recall |
| Online rank | Score 500–2000 cands |
| Feature hydrate | User/item/context |
| Nearline | Session aggregates, OOS |
| Offline | Train, batch recs for email |

### 2.2 Latency budget (PDP)

| Step | ms |
|------|----|
| Context resolve | 5–10 |
| Retrieve (parallel channels) | 20–40 |
| Feature fetch | 20–40 |
| Ranker | 20–40 |
| Business re-rank | 5–10 |
| **Total** | **≤ 100–150** |

### 2.3 Cost

Scoring 1000 cands × 200K QPS is impossible if naive—hence retrieve narrows first; cache user features; distill rankers.

---

## 3. High-Level Design

### 3.1 Components

| Component | Role |
|-----------|------|
| Recs API | Surface contracts |
| Context Service | Device, geo, session |
| Candidate Generators | CF, co-view, ANN content, graph |
| Feature Store | Online + offline |
| Ranker Fleet | GBDT/DNN | 
| Re-ranker | Diversity, business rules, ads merge |
| Experimentation | Variants |
| Log/Join | Training data |
| Model Platform | Train/deploy/shadow |
| Popularity Fallback | Degradation |

### 3.2 Flow

```text
Request → Context → Parallel Retrieve → Union/Dedup → Features
       → Rank → Re-rank (OOS/diversity/policy/ads) → Response
       → Async logs
```

### 3.3 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Stages | Multi-stage | Score full catalog online |
| Features | Shared store | Ad-hoc DB joins online |
| Fallback | Popularity/similar | Empty widget |
| Ads | Labeled merge | Silent replace all organic |

---

## 4. Architecture Diagram

```text
Client Surface --> Recs API --> Context
                      |
                      +--> CG: Co-purchase / Co-view
                      +--> CG: ANN content embedding
                      +--> CG: Personal CF / two-tower
                      |
                      v
                   Dedup/Union (budget K)
                      |
                      v
                Feature Store hydrate
                      |
                      v
                   Ranker (model)
                      |
                      v
             Re-rank: OOS, diversity, policy, ads
                      |
                      v
                   Response ASINs
                      |
                      v async
              Logs → Training → Registry → Canary
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Never recommend blocked/illegal/OOS (per policy).
2. Experiment assignment sticky per surface rules.
3. Logging includes candidate features point-in-time.
4. Fallback non-empty for critical surfaces.
5. Marketplace isolation.

### 5.2 Candidate channels

Co-purchase graph, co-view, search→purchase, two-tower ANN, editorial, trending. Budget per channel; explore slot.

### 5.3 Ranking

Learning-to-rank with calibration per surface. Multi-objective: CTR proxy, CVR, profit contribution, satisfaction (returns-).

### 5.4 Feature store

User: long-term affinities; session: short-term intent; item: price, category, embedding; context: device/time.

### 5.5 Progressive scale

10×: cache features; ANN shards. 100×: marketplace cells; distilled models. 1,000×: edge caches for anonymous; on-device session models light.

### 5.6 Marketplace fairness

Avoid entrenching only megabrands—diversity constraints; small-seller exploration quotas as product policy.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        Amazon retail **product recommendations**: multi-channel candidate generation, feature store, rankers, business re-ranking, experimentation, fallbacks, progressive scale across surfaces.

        ### 6.2 Key decisions worth defending

        1. Multi-stage retrieve→rank→re-rank
2. Feature store with PIT logging
3. Surface-specific objectives + shared retrieval
4. Non-empty fallbacks
5. Labeled ads merge policy

        ### 6.3 Risks & follow-ups

        - Feedback loops / bias
- Cold-start catalog churn
- Multi-objective tension
- Cost at 100× QPS

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **Product Recommender** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---

## 7. Deeper / Related Interview Questions

**Q1. Why multi-stage vs one model?**

**A:** Catalog too large to score; stages specialize; ops can hotfix retrieval; latency/cost control.

**Q2. How do you handle position bias?**

**A:** Propensity scoring, inverse propensity weighting, occasional randomized exploration, eye-tracking proxies—pick pragmatic mix.

**Q3. Returns as labels?**

**A:** Purchases with quick returns are negative/weak; join order lifecycle into labels carefully.

**Q4. Gift mode?**

**A:** Session intent classifiers demote personal historical affinity; boost category from browsing.

**Q5. Deal-breaker?**

**A:** Online full-catalog DNN scoring per request; or empty homepage when ranker fails.

**Q6. Sponsored products in widget?**

**A:** Labeled, relevance threshold, reserved organic slots—Ads owns auction; Recs owns merge policy.

**Q7. Feature store vs joining production DBs?**

**A:** PIT correctness and p99; production DBs aren’t feature stores.

**Q8. Success metrics?**

**A:** Surface CTR/CVR, revenue, diversity, complaint rate, latency, model freshness, fallback rate.

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

        ### Appendix F — Response schema

```json
{"surface":"pdp_related","asins":[{"asin":"B0..","reason":"coview"}],"model_versions":{},"exp_ids":[]}
```

### Appendix G — Closer checklist

- [ ] Retrieve/rank/re-rank split
- [ ] Feature store PIT
- [ ] Fallbacks
- [ ] OOS/policy filters
- [ ] Experiments
- [ ] Progressive scale



## Extended Notes — Product Recommender

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

### E7. Surface-specific models

PDP related-items ≠ homepage for-you. Shared retrieval, divergent rank heads.

### E8. Real-time session

Clickstream → session store (Redis) with TTL; ranker reads last-N events.

### E9. Embedding training

Two-tower with in-batch negatives; ANN index rebuild cadence vs nearline partial updates.

### E10. Business value

Optimize customer long-term value not only immediate CTR—mention returns and complaint guardrails.

### E11. Catalog taxonomy

Browse nodes as features; avoid recommending incompatible product types.

### E12. International

Marketplace cells; currency/price features local; don’t leak US inventory into DE.

### E13. Email batch

Offline generate + personalize at send; cheaper than online QPS.

### E14. Model distillation

Large teacher offline; small student online for p99.

### E15. Debug tools

Explain: channels, scores, filters fired—internal only.

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


## 16. Additional Deep Q&A — Product Recommender

### Q1. How many candidate channels is too many?

Start with 3–5 high-precision channels with explicit budgets. More channels help recall but explode hydrate/rank cost and make debugging hard. Add channels when offline recall gaps justify them.

### Q2. How do you set candidate budget K?

Empirically: plot conversion vs K and p99 vs K. Typical 500–2000. Homepage can afford more latency than tiny PDP modules.

### Q3. Multi-objective ranking without collapse?

Scalarize with weights + constraints (diversity, brand caps). Use guardrail metrics in experiments. Avoid secretly optimizing profit alone.

### Q4. How do you fight filter bubbles?

Diversity constraints, explore slots, category coverage minimums, serendipity metrics.

### Q5. Training data pipeline essentials?

Join impressions→clicks→purchases→returns with PIT features; store model_version and candidate set samples; position bias handling.

### Q6. Two-tower vs CF graph?

Two-tower scales to ANN retrieval for personalization; CF graphs shine for complementary items. Use both as channels.

### Q7. How to handle exploding catalog?

ANN sharding, aggressive candidate filters (geo/marketplace), hierarchical categories, distilled rankers.

### Q8. Empty widget policy?

Fallback popularity / similar / editorial. Empty is a SEV-level customer experience bug on homepage.

### Q9. Realtime features vs batch?

Session features realtime; long-term affinities batch/nearline. Don’t pretend all features are realtime.

### Q10. Marketplace fairness to sellers?

Explore quotas, diversity, avoid pure brand entrenchment; still optimize customer value—state the tension.

## 17. Scenario Drills — Product Recs

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Ranker outage | Fallback popularity/similar | Non-empty surface |
| OOS storm | Nearline inventory filter | Trust > CTR |
| Bad model canary | Auto rollback | Guardrails |
| Gift shopping mispersonalization | Session intent demote history | Context wins |

## 18. Final Checklist — Product Recs

- [ ] Retrieve → rank → re-rank stages
- [ ] Feature store PIT logging
- [ ] Surface-specific objectives
- [ ] Fallbacks non-empty
- [ ] OOS/policy filters
- [ ] Experimentation hooks
- [ ] Ads merge policy labeled
- [ ] Unit cost $/1K recs

## 19. Expanded Design Notes — Product Recs

### 19.1 Channel design

Co-purchase: classic Amazon ‘customers also bought’. Co-view: browsing affinity. Search-purchase: intent from queries. Two-tower ANN: personalized. Trending: cold-start/seasonal. Editorial: merchandising. Each returns scored candidates with channel tags for explainability and debugging.

### 19.2 Ranker features

User affinities, item popularity, price compatibility, complementary vs substitute flags, shipping speed, Prime eligibility, review scores, session last-N ASINs, time of day. Avoid leakage from future joins.

### 19.3 Re-rank constraints

Hard: blocked, OOS, geo ineligible, age-restricted. Soft: diversity MMR, brand caps, price band spread, explore slot. Ads: labeled sponsored insertion with relevance floor.

### 19.4 Offline evaluation

AUC/NDCG insufficient alone. Use counterfactual estimators cautiously; ship decisions via A/B with guardrails on returns and latency.

### 19.5 Serving architecture

Stateless Recs API; HNSW/IVF ANN clusters; feature cache; model servers with batching; deadlines per stage; hedged requests for hot dependencies.

### 19.6 Homepage assembly

Multiple widgets each call Recs with different surface ids; page compositor applies page-level diversity so widgets don’t all repeat the same ASIN.

### 19.7 Email & notifications

Batch generate candidates offline; personalize at send; cheaper and more cacheable than online QPS.

### 19.8 Long-term evolution

Unified feature platform; generative re-rank explanations; on-device session models for apps; still keep multi-stage discipline.

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

*End of document — Product Recommender (SDE III)*
