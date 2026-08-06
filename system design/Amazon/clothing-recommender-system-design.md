# System Design: Clothing Recommender System (Amazon Fashion)

> **Focus areas:** Style embeddings · Size/fit · Seasonality · Visual similarity · Returns-aware ranking
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Fit/season constraints; visual+tabular fusion; deal-breaker: generic CF only
> **Interview theme:** Amazon SDE III / L6 — **Amazon Fashion** — style, fit, seasonality, visual ML, returns-aware objectives

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

Goal: Clothing/fashion recommender accounting for style, size/fit, seasonality, visual similarity—not just co-purchase.

### 1.0 What this is / is not
| Dimension | This | Not |
|-----------|------|-----|
| Fit | Critical | Rarely for generic |
| Visual | Primary | Secondary |
| Returns | High-cost signal | Lower |

### 1.1 Functional requirements
Cover fashion surfaces, size/fit, visual ANN, seasonality, outfits, style, returns, inclusivity, trends, cold-start SKUs, careful gender/dept, marketplace, latency, safety, experiments.

**MVP:** visual+style+size filter+season+returns-aware head.
**Out of MVP:** body inference from customer photos; CTR-only ignoring returns.

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

Visual ANN ~100M×512-d ≈ 200GB+indexes. Shard by marketplace/department. Widget p99 < 150–200ms. Returns labels delayed — use delayed labels + online return-rate guardrails.

## 3. High-Level Design

### 3.1 Fashion components
Visual embeddings/ANN; Size/Fit profile; Seasonality; Outfit complement; Returns-aware rank head; Attribute normalizer — on top of generic multi-stage recs.

### 3.2 Flow
Context → visual∥CF∥trend∥outfit → fit/inventory filter → rank (style+purchase−return) → diversify.

### 3.3 Tradeoffs
Fashion ≠ generic CF; SKU feasibility; season with intent overrides; returns in objective.

## 4. Architecture Diagram

```text
Fashion Surface --> Recs API --> Size/Fit + Seasonality
                           --> Visual ANN --\
                           --> CF/Two-Tower --+--> Fit/OOS filter --> Rank --> Diversify
                           --> Outfit CG   --/
                                 --> Returns-aware training loop
```

## 5. Design Deep Dive

### 5.1 Fit
Confidence states unknown→inferred→explicit; hard filter only at high confidence; variant inventory truth.

### 5.2 Visual
Versioned embeddings; studio-first index; nearline upsert; shared with visual search platform.

### 5.3 Season & ethics
Soft demotion + hard extremes; browse intent overrides; no body inference from customer photos.

### 5.4 Objective
`P(click/purchase) - λ P(return_fit) + style + season + in_stock_size`.

### 5.5 Scale
Shard ANN; distill encoders; marketplace cells; attribute quality program.

## 6. Wrap-Up

### 6.1 What we designed
Visual ANN, style models, size/fit profiles, seasonality, outfits, returns-aware ranking on multi-stage retrieval.

### 6.2 Key decisions worth defending
1. Fashion≠generic CF
2. Variant inventory+fit filters
3. Visual CG first-class
4. Seasonality with overrides
5. Returns in objective

### 6.3 Risks & follow-ups
- Attribute quality
- Size cold start
- Trend vs fit
- Sensitive inference

### 6.4 Closer
> **Clothing Recommender System**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Clothing Recommender

**Q1. What makes clothing different in one sentence?**

**A:** Fit + visual style + seasonality + returns economics dominate, so generic product CF is insufficient.

**Q2. SKU vs style recommendation?**

**A:** Optimize style choice but enforce feasible SKU in size/color inventory for the customer.

**Q3. How do you learn size offsets across brands?**

**A:** From return reasons and keep rates; brand-garment offsets; never claim medical body precision.

**Q4. Visual embedding drift?**

**A:** Versioned spaces; dual ANN during migration; triplet eval sets; alarm on recall drops.

**Q5. Season hard filter or soft?**

**A:** Soft default; hard for extreme mismatches unless browse intent overrides.

**Q6. Outfit success metric?**

**A:** Attach rate of complementary items + human style eval + return rates—not CTR alone.

**Q7. Inclusive sizing metric?**

**A:** Coverage of recommendations with in-stock sizes across size bands for customers who need them.

**Q8. Attribute synonym pain?**

**A:** Normalize colors/materials via synonym graph + embeddings; don’t trust raw strings.

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
- [ ] Fashion≠generic CF
- [ ] Variant inventory+fit filters
- [ ] Visual CG first-class
- [ ] Seasonality with overrides
- [ ] Returns in objective

## Deep Technical Notes — Clothing Recommender

### Fit profile internals

Store per garment type distributions, confidence, last updated, source (explicit/purchase/return). Provide APIs for UX ‘my sizes’. Use in filters and features.

### Returns-aware rank head

Predict P(return_fit) with tabular features: size confidence, brand offset variance, material stretch, customer historic return rate (careful), price. Combine in score with weight λ tuned under guardrails.

### Seasonality service

Inputs locale, date, optional weather band, event calendar. Outputs season vector features and demotion multipliers. Cache heavily.

### Visual platform ownership

Embeddings as a platform shared by fashion recs and visual search. Versioning and SLA owned by embedding service; consumers pin versions.

### Taxonomy cleanup program

Ongoing data quality initiative—color, occasion, sleeve length—pays more than another 0.1% model AUC if attributes are garbage.

### Experiment guardrails

Return rate, size-related return rate, complaint rate, latency, diversity, inclusive coverage. CTR lift with return spike = fail.

### Degradation

Visual ANN down → CF+attributes. Fit service down → soft mode without hard filters. Season service down → calendar month prior only.

### Roadmap

Better outfit generation, privacy-preserving fit, AR try-on hooks, improved trend detection without return explosions.

## Interview Cards — Clothing Recommender

### Card 1: What makes clothing different in one sentence?

Fit + visual style + seasonality + returns economics dominate, so generic product CF is insufficient.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: SKU vs style recommendation?

Optimize style choice but enforce feasible SKU in size/color inventory for the customer.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: How do you learn size offsets across brands?

From return reasons and keep rates; brand-garment offsets; never claim medical body precision.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Visual embedding drift?

Versioned spaces; dual ANN during migration; triplet eval sets; alarm on recall drops.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Season hard filter or soft?

Soft default; hard for extreme mismatches unless browse intent overrides.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Outfit success metric?

Attach rate of complementary items + human style eval + return rates—not CTR alone.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Inclusive sizing metric?

Coverage of recommendations with in-stock sizes across size bands for customers who need them.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Attribute synonym pain?

Normalize colors/materials via synonym graph + embeddings; don’t trust raw strings.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: UGC images in ANN?

Prefer studio for index consistency; UGC for social proof modules separately.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Gender stereotyping risk?

Use browse context; avoid forcing binary rails; careful features.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Try-before-you-buy labels?

Separate from hard purchases if program exists; different return semantics.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Prime Day fashion spikes?

Pre-warm ANN; freeze risky untested models; watch return guardrails post-event.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Cold-start garment day-1?

Visual+attributes; explore quota; merchandising.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Privacy of size data?

Purpose-limited; sensitive; retention controls; not shared to advertisers ad hoc.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Mobile camera shop-the-look?

Shared embedding platform; separate product surface.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Deal-breaker?

Ignore size availability or CTR-only objective that spikes returns.

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

## More Interview Q&A — Clothing Recommender

**Q1. What makes clothing different in one sentence?**

**A:** Fit + visual style + seasonality + returns economics dominate, so generic product CF is insufficient.

**Q2. SKU vs style recommendation?**

**A:** Optimize style choice but enforce feasible SKU in size/color inventory for the customer.

**Q3. How do you learn size offsets across brands?**

**A:** From return reasons and keep rates; brand-garment offsets; never claim medical body precision.

**Q4. Visual embedding drift?**

**A:** Versioned spaces; dual ANN during migration; triplet eval sets; alarm on recall drops.

**Q5. Season hard filter or soft?**

**A:** Soft default; hard for extreme mismatches unless browse intent overrides.

**Q6. Outfit success metric?**

**A:** Attach rate of complementary items + human style eval + return rates—not CTR alone.

**Q7. Inclusive sizing metric?**

**A:** Coverage of recommendations with in-stock sizes across size bands for customers who need them.

**Q8. Attribute synonym pain?**

**A:** Normalize colors/materials via synonym graph + embeddings; don’t trust raw strings.

**Q9. UGC images in ANN?**

**A:** Prefer studio for index consistency; UGC for social proof modules separately.

**Q10. Gender stereotyping risk?**

**A:** Use browse context; avoid forcing binary rails; careful features.

**Q11. Try-before-you-buy labels?**

**A:** Separate from hard purchases if program exists; different return semantics.

**Q12. Prime Day fashion spikes?**

**A:** Pre-warm ANN; freeze risky untested models; watch return guardrails post-event.

**Q13. Cold-start garment day-1?**

**A:** Visual+attributes; explore quota; merchandising.

**Q14. Privacy of size data?**

**A:** Purpose-limited; sensitive; retention controls; not shared to advertisers ad hoc.

**Q15. Mobile camera shop-the-look?**

**A:** Shared embedding platform; separate product surface.

**Q16. Deal-breaker?**

**A:** Ignore size availability or CTR-only objective that spikes returns.

## Deep Technical Addenda — Clothing Recommender

### Fit profile internals

Store per garment type distributions, confidence, last updated, source (explicit/purchase/return). Provide APIs for UX ‘my sizes’. Use in filters and features.

### Returns-aware rank head

Predict P(return_fit) with tabular features: size confidence, brand offset variance, material stretch, customer historic return rate (careful), price. Combine in score with weight λ tuned under guardrails.

### Seasonality service

Inputs locale, date, optional weather band, event calendar. Outputs season vector features and demotion multipliers. Cache heavily.

### Visual platform ownership

Embeddings as a platform shared by fashion recs and visual search. Versioning and SLA owned by embedding service; consumers pin versions.

### Taxonomy cleanup program

Ongoing data quality initiative—color, occasion, sleeve length—pays more than another 0.1% model AUC if attributes are garbage.

### Experiment guardrails

Return rate, size-related return rate, complaint rate, latency, diversity, inclusive coverage. CTR lift with return spike = fail.

### Degradation

Visual ANN down → CF+attributes. Fit service down → soft mode without hard filters. Season service down → calendar month prior only.

### Roadmap

Better outfit generation, privacy-preserving fit, AR try-on hooks, improved trend detection without return explosions.

## Tradeoff Matrices — Clothing Recommender

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

## Operability Addenda — Clothing Recommender

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

## Worked Capacity Narrative — Clothing Recommender

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Clothing Recommender

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Clothing Recommender

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Clothing Recommender
### S1. Fashion ≠ generic CF

Fit, visual style, seasonality, returns dominate economics. Say this in minute one.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. SKU feasibility

Recommend style but ensure in-stock size variant for customer; deep-link available SKU.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Fit confidence states

unknown → inferred_low → inferred_high → explicit; hard filters only at high confidence.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Visual platform

Versioned embeddings; dual ANN during upgrades; studio images for index; shared with visual search.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Seasonality overrides

Soft demotion default; hard for extremes; browse intent can override (vacation swimwear in winter).
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Returns-aware objective

P(purchase) - λ P(return_fit) + style; guardrail experiments on return rate.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Attribute quality

Color/material synonym graphs often beat +0.1 AUC; invest in taxonomy.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Ethics

No body inference from customer photos; careful gender stereotyping; declared/browse signals preferred.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — Clothing Recommender

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Winter swimwear browse | Intent overrides season demotion | Preserve trust/UX | Postmortem + guardrail |
| Size OOS | Alt sizes / similar cut in stock | Preserve trust/UX | Postmortem + guardrail |
| Return spike after model | Rollback; raise λ | Preserve trust/UX | Postmortem + guardrail |
| Bad color attributes | Trust visual; fix taxonomy | Preserve trust/UX | Postmortem + guardrail |
| Visual ANN down | CF+attributes | Preserve trust/UX | Postmortem + guardrail |
| Fit service down | Soft mode no hard filters | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — Clothing Recommender

**RQ1. Why does 'Fashion ≠ generic CF' matter in an L6 interview?**

**A:** Fit, visual style, seasonality, returns dominate economics. Say this in minute one. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Fashion ≠ generic CF' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Fashion ≠ generic CF' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'SKU feasibility' matter in an L6 interview?**

**A:** Recommend style but ensure in-stock size variant for customer; deep-link available SKU. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'SKU feasibility' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'SKU feasibility' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Fit confidence states' matter in an L6 interview?**

**A:** unknown → inferred_low → inferred_high → explicit; hard filters only at high confidence. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Fit confidence states' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Fit confidence states' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Visual platform' matter in an L6 interview?**

**A:** Versioned embeddings; dual ANN during upgrades; studio images for index; shared with visual search. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Visual platform' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Visual platform' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Seasonality overrides' matter in an L6 interview?**

**A:** Soft demotion default; hard for extremes; browse intent can override (vacation swimwear in winter). Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Seasonality overrides' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Seasonality overrides' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Returns-aware objective' matter in an L6 interview?**

**A:** P(purchase) - λ P(return_fit) + style; guardrail experiments on return rate. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Returns-aware objective' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Returns-aware objective' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Attribute quality' matter in an L6 interview?**

**A:** Color/material synonym graphs often beat +0.1 AUC; invest in taxonomy. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Attribute quality' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Attribute quality' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Ethics' matter in an L6 interview?**

**A:** No body inference from customer photos; careful gender stereotyping; declared/browse signals preferred. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Ethics' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Ethics' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Clothing Recommender

### Walkthrough beat 1

In beat 1, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through Clothing Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Clothing Recommender

- [ ] Can explain **Fashion ≠ generic CF** with numbers and a deal-breaker
- [ ] Can explain **SKU feasibility** with numbers and a deal-breaker
- [ ] Can explain **Fit confidence states** with numbers and a deal-breaker
- [ ] Can explain **Visual platform** with numbers and a deal-breaker
- [ ] Can explain **Seasonality overrides** with numbers and a deal-breaker
- [ ] Can explain **Returns-aware objective** with numbers and a deal-breaker
- [ ] Can explain **Attribute quality** with numbers and a deal-breaker
- [ ] Can explain **Ethics** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Winter swimwear browse**
- [ ] Has a 30-second runbook for **Size OOS**
- [ ] Has a 30-second runbook for **Return spike after model**
- [ ] Has a 30-second runbook for **Bad color attributes**
- [ ] Has a 30-second runbook for **Visual ANN down**
- [ ] Has a 30-second runbook for **Fit service down**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Clothing Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

*End of document — Clothing Recommender System (Amazon Fashion) (SDE III)*
