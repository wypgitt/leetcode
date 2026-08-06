# System Design: Product Recommender System (Amazon Retail)

> **Focus areas:** Candidate generation · Ranking · Feature store · Personalization · Cold start · Diversity · Experiments
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Retrieve/rank/re-rank split; deal-breaker: one DNN scores entire catalog online
> **Interview theme:** Amazon SDE III / L6 — **Retail Personalization** — relevance with marketplace constraints and unit economics

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

Goal: Amazon product recommendations across homepage/PDP/cart/email with multi-stage ML, features, business rules, experimentation.

### 1.0 What this is / is not
| Dimension | This | Not |
|-----------|------|-----|
| Job | Personalized ASIN recs | Search SERP |
| Planes | Retrieve→rank→re-rank | One model over full catalog online |
| Success | Relevance+conversion+satisfaction | CTR only |

### 1.1 Functional requirements
Cover surfaces, inputs/outputs, freshness, business rules, diversity, cold start, session signals, explanations, experiments, marketplace cells, sponsored merge, latency, privacy, feedback labels.

**MVP:** PDP+homepage; retrieve+rank; OOS filter; session features; logging; A/B hooks.
**Out of MVP:** full-catalog online DNN; empty critical rails without fallback.

### 1.2 NFRs
State numeric latency/availability/freshness/cost/privacy targets for this domain. Prefer degrade-quality-before-total-outage except fail-closed trust gates (safety/privacy/kids/consent).

### 1.3 Cases
Enumerate happy paths plus storms/spikes, dependency timeouts, stale data, abuse/fraud, and trust edge cases — with explicit behavior per case (see deep Q&A and scenario runbooks below).

### 1.4 Progressive scale
| Jump | Forces |
|------|--------|
| 10× | Cache, shard, async, sample |
| 100× | Cells, distill, edge, hierarchy |
| 1,000× | On-device/approx/platform |

### 1.5 Constraints & repeat-back
Amazon themes: customer trust, ownership, frugality, mechanisms over meetings. Repeat scope in one breath.

---
## 2. Back-of-the-Envelope Estimation

### 2.1 Planes
Retrieve (ANN/CF/graph), rank 500–2000 cands, feature hydrate, nearline OOS/session, offline train + email batch.

### 2.2 PDP latency
Context 5–10 → retrieve 20–40 → features 20–40 → rank 20–40 → re-rank 5–10 → **≤100–150ms p99**.

### 2.3 Cost
Full-catalog scoring at 200K QPS is impossible. Multi-stage + cache + distillation. Track $/1K recommendations.

## 3. High-Level Design

### 3.1 Stages
Parallel CGs → union/dedup (K) → feature store → ranker → business re-rank (OOS/diversity/policy/ads) → response → async logs.

### 3.2 Channels
Co-purchase, co-view, two-tower ANN, trending, editorial — budgets + kill flags each.

### 3.3 Tradeoffs
Multi-stage not full-catalog DNN; feature store not ad-hoc joins; non-empty fallbacks; labeled ads merge.

## 4. Architecture Diagram

```text
Surface --> Recs API --> Context
                +--> CG co-purchase/co-view
                +--> CG ANN / two-tower
                +--> CG trending/editorial
                v
             Dedup(K) --> Features --> Ranker --> Re-rank --> ASINs
                --> Logs --> Training --> Registry --> Canary
```

## 5. Design Deep Dive

### 5.1 Invariants
No blocked/OOS (policy); sticky experiments; PIT feature logs; non-empty critical rails; marketplace isolation.

### 5.2 Ranking
Multi-objective LTR (CTR/CVR/contribution/satisfaction); surface calibration; position-bias handling.

### 5.3 Feature store
Long-term user, short-term session, item, context — shared definitions online/offline.

### 5.4 Progressive scale
10× caches/ANN shards; 100× marketplace cells + distilled models; 1,000× edge/on-device light models.

### 5.5 Fairness & ads
Diversity/explore for marketplace health; sponsored labeled with organic floor.

## 6. Wrap-Up

### 6.1 What we designed
Multi-channel CG, feature store, rankers, business re-rank, experiments, fallbacks, progressive scale.

### 6.2 Key decisions worth defending
1. Multi-stage
2. Feature store PIT
3. Surface-specific objectives
4. Non-empty fallbacks
5. Labeled ads merge

### 6.3 Risks & follow-ups
- Feedback loops
- Cold-start churn
- Multi-objective tension
- Cost at 100×

### 6.4 Closer
> **Product Recommender System**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Product Recommender

**Q1. How do you pick K candidates?**

**A:** Sweep K vs conversion and p99 offline/online; typical 500–2000; surface-specific.

**Q2. What is training-serving skew?**

**A:** Feature computed differently online vs offline or future leakage. Fix with shared definitions + PIT joins + skew monitors.

**Q3. How to add a new candidate channel safely?**

**A:** Shadow traffic; measure incremental recall and latency; flag off by default; gradual budget increase.

**Q4. Homepage empty widget SEV?**

**A:** Yes for critical rails—fallback required. Treat empty_rate as customer-facing SLO.

**Q5. Returns in labels?**

**A:** Join order lifecycle; quick returns weaken positive purchase labels; fashion even more—see clothing doc.

**Q6. How do ads merge?**

**A:** Labeled sponsored slots, relevance floor, organic floor; Ads auction; Recs merge policy ownership.

**Q7. Multi-objective collapse?**

**A:** Constraints + guardrails > secret single profit weight. Discuss diversity and satisfaction.

**Q8. Real-time session store?**

**A:** Redis/session service last-N events with TTL; ranker reads; don’t rebuild from warehouse online.

---
## 8. Appendices

### A — Glossary
| Term | Meaning |
|------|---------|
| Cell | Failure-isolated unit |
| Nearline | Minutes-latency path |
| Canary | Partial bake |
| Deal-breaker | Non-negotiable bad design |
| Two-pizza | Ownership team with pager |

### B — Oncall checklist
- [ ] SLOs green
- [ ] Rollback armed
- [ ] Kill switches known
- [ ] Cost dashboards
- [ ] Privacy/safety tested

### F — Topic closer checklist
- [ ] Multi-stage
- [ ] Feature store PIT
- [ ] Surface-specific objectives
- [ ] Non-empty fallbacks
- [ ] Labeled ads merge

## Deep Technical Notes — Product Recommender

### Retrieval channel portfolio

Maintain a balanced portfolio: complementary (co-purchase), substitute (co-view), personalized ANN, trending, editorial. Budgets prevent one channel monopolizing candidates.

Each channel exports scores in a normalized space or with channel-specific calibration before union.

### Ranker model lifecycle

Train → offline eval → shadow → interleaving/AB → bake. Keep teacher models for distillation. Rollback via model registry pointer.

### Business re-ranker

Deterministic rules after ML: OOS, block, geo, age, diversity MMR, brand caps, explore slot, ads insert. Rules are hotfixable without retrain—critical for ops.

### Logging for learning

Log impression sets (sampled), positions, features refs, model versions, experiment ids, subsequent clicks/purchases/returns. Sampling strategy explicit for cost.

### Page composition

Multiple widgets; page-level dedupe; layout constraints; ensure not all rails show same bestseller.

### Failure modes

Feature store slow → cached features / reduce features. ANN down → CF-only. Ranker down → popularity fallback. Partial degradation preferred.

### Marketplace fairness

Measure mega-brand share; consider explore for new/small sellers when customer-relevant; don’t sacrifice customer relevance for vanity fairness metrics blindly—state tension.

### Science vs serving ownership

Clear interfaces on candidate schema and deadlines. Serving can shed; science owns quality metrics next day. Joint error budgets on latency vs quality negotiated.

## Interview Cards — Product Recommender

### Card 1: How do you pick K candidates?

Sweep K vs conversion and p99 offline/online; typical 500–2000; surface-specific.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: What is training-serving skew?

Feature computed differently online vs offline or future leakage. Fix with shared definitions + PIT joins + skew monitors.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: How to add a new candidate channel safely?

Shadow traffic; measure incremental recall and latency; flag off by default; gradual budget increase.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Homepage empty widget SEV?

Yes for critical rails—fallback required. Treat empty_rate as customer-facing SLO.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Returns in labels?

Join order lifecycle; quick returns weaken positive purchase labels; fashion even more—see clothing doc.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: How do ads merge?

Labeled sponsored slots, relevance floor, organic floor; Ads auction; Recs merge policy ownership.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Multi-objective collapse?

Constraints + guardrails > secret single profit weight. Discuss diversity and satisfaction.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Real-time session store?

Redis/session service last-N events with TTL; ranker reads; don’t rebuild from warehouse online.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: ANN index rebuild vs upsert?

Periodic rebuild for quality; nearline upsert for new ASINs; version embeddings.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Cell key?

Marketplace (+ maybe category mega-cell). Avoid one global mega-model serving all policies.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: How to debug a bad recommendation?

Internal explain: channels, scores, filters; never expose full internals publicly.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Cost lever #1?

Reduce K / improve cache hit / distill ranker / drop weak channels.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Exploration ethics?

Bounded; avoid harmful categories; measure regret; product approval.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Email vs online?

Batch offline generation for email; different latency economics.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Cold start user?

Segment popularity + contextual; rapidly adapt with session features.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Deal-breaker?

Score full catalog with one DNN online per request; or empty critical surfaces without fallback.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.
## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + Amazon ownership lens |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive (reliability/scale/ML/privacy) |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact; lock MVP; split load classes; name pager owners; refuse deal-breakers.

---

## 10. Operability

### Golden signals
Latency, traffic, errors, saturation, freshness, trust incidents.

### Rollback ladder
Flag off → revert artifact → shed/reduce K → cell isolate → postmortem with trust section.

### Kill switches
Disable optional stage; freeze nearline; revert pointer; shed traffic; isolate cell.

### Security/privacy baseline
Authn/z, PII TTLs, encryption, cell isolation, signed artifacts, abuse limits.

### Cost worksheet
Dominant cost driver; fastest unit-cost lever; 10× cost with/without architectural jump.

```text
instances ≈ peak_QPS × cpu_sec / (cores × util)
```

### Progressive scale
10× cache/shard/async; 100× cells/distill/edge; 1,000× on-device/approximate/platform.

### Cross-team deps
Identity, catalog, feature store, ads, experimentation, logging — each with failure mitigation.

---

## More Interview Q&A — Product Recommender

**Q1. How do you pick K candidates?**

**A:** Sweep K vs conversion and p99 offline/online; typical 500–2000; surface-specific.

**Q2. What is training-serving skew?**

**A:** Feature computed differently online vs offline or future leakage. Fix with shared definitions + PIT joins + skew monitors.

**Q3. How to add a new candidate channel safely?**

**A:** Shadow traffic; measure incremental recall and latency; flag off by default; gradual budget increase.

**Q4. Homepage empty widget SEV?**

**A:** Yes for critical rails—fallback required. Treat empty_rate as customer-facing SLO.

**Q5. Returns in labels?**

**A:** Join order lifecycle; quick returns weaken positive purchase labels; fashion even more—see clothing doc.

**Q6. How do ads merge?**

**A:** Labeled sponsored slots, relevance floor, organic floor; Ads auction; Recs merge policy ownership.

**Q7. Multi-objective collapse?**

**A:** Constraints + guardrails > secret single profit weight. Discuss diversity and satisfaction.

**Q8. Real-time session store?**

**A:** Redis/session service last-N events with TTL; ranker reads; don’t rebuild from warehouse online.

**Q9. ANN index rebuild vs upsert?**

**A:** Periodic rebuild for quality; nearline upsert for new ASINs; version embeddings.

**Q10. Cell key?**

**A:** Marketplace (+ maybe category mega-cell). Avoid one global mega-model serving all policies.

**Q11. How to debug a bad recommendation?**

**A:** Internal explain: channels, scores, filters; never expose full internals publicly.

**Q12. Cost lever #1?**

**A:** Reduce K / improve cache hit / distill ranker / drop weak channels.

**Q13. Exploration ethics?**

**A:** Bounded; avoid harmful categories; measure regret; product approval.

**Q14. Email vs online?**

**A:** Batch offline generation for email; different latency economics.

**Q15. Cold start user?**

**A:** Segment popularity + contextual; rapidly adapt with session features.

**Q16. Deal-breaker?**

**A:** Score full catalog with one DNN online per request; or empty critical surfaces without fallback.

## Deep Technical Addenda — Product Recommender

### Retrieval channel portfolio

Maintain a balanced portfolio: complementary (co-purchase), substitute (co-view), personalized ANN, trending, editorial. Budgets prevent one channel monopolizing candidates.

Each channel exports scores in a normalized space or with channel-specific calibration before union.

### Ranker model lifecycle

Train → offline eval → shadow → interleaving/AB → bake. Keep teacher models for distillation. Rollback via model registry pointer.

### Business re-ranker

Deterministic rules after ML: OOS, block, geo, age, diversity MMR, brand caps, explore slot, ads insert. Rules are hotfixable without retrain—critical for ops.

### Logging for learning

Log impression sets (sampled), positions, features refs, model versions, experiment ids, subsequent clicks/purchases/returns. Sampling strategy explicit for cost.

### Page composition

Multiple widgets; page-level dedupe; layout constraints; ensure not all rails show same bestseller.

### Failure modes

Feature store slow → cached features / reduce features. ANN down → CF-only. Ranker down → popularity fallback. Partial degradation preferred.

### Marketplace fairness

Measure mega-brand share; consider explore for new/small sellers when customer-relevant; don’t sacrifice customer relevance for vanity fairness metrics blindly—state tension.

### Science vs serving ownership

Clear interfaces on candidate schema and deadlines. Serving can shed; science owns quality metrics next day. Joint error budgets on latency vs quality negotiated.

## Tradeoff Matrices — Product Recommender

### Consistency vs latency

| Choice | Latency | Correctness | Use when |
|--------|---------|-------------|----------|
| Sync durable then serve | Higher | Stronger | Money/trust boards, enforcement |
| Serve then async durable | Lower | Risk window | Casual UX with repair |
| Cached eventual | Lowest | Stale OK | Top-K spectators, suggest head |

### Exact vs approximate

| Choice | Cost | UX risk | Use when |
|--------|------|---------|----------|
| Exact | High at scale | Low confusion | Small boards / cells |
| Approximate labeled | Lower | Need UX copy | Global 100× ranks |
| Hierarchical | Medium | Ops complexity | Multi-region global |

### Personalization strength

| Choice | Lift | Privacy/cost | Use when |
|--------|------|--------------|----------|
| None / segment | Low | Best privacy | Kids, restricted |
| Light re-rank | Medium | Good | Default |
| Heavy private retrieve | High potential | Costly/risky | Rare, budgeted |

## Operability Addenda — Product Recommender

### Deploy pipeline

```text
build artifact → static validation → shadow → canary → bake → full
                     ↓ fail              ↓ guardrail fail
                  reject              auto rollback
```

### Guardrail examples

- p99 latency regression > threshold  
- empty/fallback rate rise  
- safety/privacy denials anomaly  
- undo/regret/complaint spikes  
- unit cost spike  

### Kill switches (name them in interview)

1. Disable optional stage (fuzzy, ads, assist, personalization)  
2. Freeze nearline updates  
3. Revert artifact pointer  
4. Shed traffic / reduce K  
5. Cell isolation  

## Worked Capacity Narrative — Product Recommender

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Product Recommender

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Product Recommender

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Product Recommender
### S1. Multi-stage discipline

Retrieve narrows; rank scores hundreds–thousands; re-rank applies business rules. Full-catalog DNN online is a deal-breaker.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Feature store PIT

Shared definitions; point-in-time joins; skew monitors; don’t join production OLTP ad hoc on serve path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Channel portfolio

Co-purchase, co-view, ANN personalization, trending, editorial—with budgets and kill flags per channel.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Deadlines & shedding

Per-stage budgets; drop weak channels; reduce K; distilled model; popularity fallback—never empty critical rails.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Bias & feedback loops

Position propensities; limited exploration; don’t train only on top-1 feedback.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Surface specialization

PDP related ≠ homepage for-you; shared retrieval, divergent rank heads; page-level dedupe across widgets.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Ads merge

Labeled sponsored, relevance floor, organic floor; Ads auction; Recs merge ownership.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Unit economics

$/1K recommendations; ANN CPU; ranker cost; cache hit; distillation.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — Product Recommender

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Ranker outage | Popularity/similar fallback | Preserve trust/UX | Postmortem + guardrail |
| OOS storm | Nearline inventory filter | Preserve trust/UX | Postmortem + guardrail |
| Bad model | Canary rollback | Preserve trust/UX | Postmortem + guardrail |
| Gift shopping | Session intent demotes history | Preserve trust/UX | Postmortem + guardrail |
| Feature store slow | Cached features; reduce set | Preserve trust/UX | Postmortem + guardrail |
| ANN down | CF-only channels | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — Product Recommender

**RQ1. Why does 'Multi-stage discipline' matter in an L6 interview?**

**A:** Retrieve narrows; rank scores hundreds–thousands; re-rank applies business rules. Full-catalog DNN online is a deal-breaker. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Multi-stage discipline' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Multi-stage discipline' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Feature store PIT' matter in an L6 interview?**

**A:** Shared definitions; point-in-time joins; skew monitors; don’t join production OLTP ad hoc on serve path. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Feature store PIT' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Feature store PIT' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Channel portfolio' matter in an L6 interview?**

**A:** Co-purchase, co-view, ANN personalization, trending, editorial—with budgets and kill flags per channel. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Channel portfolio' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Channel portfolio' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Deadlines & shedding' matter in an L6 interview?**

**A:** Per-stage budgets; drop weak channels; reduce K; distilled model; popularity fallback—never empty critical rails. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Deadlines & shedding' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Deadlines & shedding' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Bias & feedback loops' matter in an L6 interview?**

**A:** Position propensities; limited exploration; don’t train only on top-1 feedback. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Bias & feedback loops' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Bias & feedback loops' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Surface specialization' matter in an L6 interview?**

**A:** PDP related ≠ homepage for-you; shared retrieval, divergent rank heads; page-level dedupe across widgets. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Surface specialization' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Surface specialization' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Ads merge' matter in an L6 interview?**

**A:** Labeled sponsored, relevance floor, organic floor; Ads auction; Recs merge ownership. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Ads merge' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Ads merge' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Unit economics' matter in an L6 interview?**

**A:** $/1K recommendations; ANN CPU; ranker cost; cache hit; distillation. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Unit economics' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Unit economics' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Product Recommender

### Walkthrough beat 1

In beat 1, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through Product Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Product Recommender

- [ ] Can explain **Multi-stage discipline** with numbers and a deal-breaker
- [ ] Can explain **Feature store PIT** with numbers and a deal-breaker
- [ ] Can explain **Channel portfolio** with numbers and a deal-breaker
- [ ] Can explain **Deadlines & shedding** with numbers and a deal-breaker
- [ ] Can explain **Bias & feedback loops** with numbers and a deal-breaker
- [ ] Can explain **Surface specialization** with numbers and a deal-breaker
- [ ] Can explain **Ads merge** with numbers and a deal-breaker
- [ ] Can explain **Unit economics** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Ranker outage**
- [ ] Has a 30-second runbook for **OOS storm**
- [ ] Has a 30-second runbook for **Bad model**
- [ ] Has a 30-second runbook for **Gift shopping**
- [ ] Has a 30-second runbook for **Feature store slow**
- [ ] Has a 30-second runbook for **ANN down**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Product Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

*End of document — Product Recommender System (Amazon Retail) (SDE III)*
