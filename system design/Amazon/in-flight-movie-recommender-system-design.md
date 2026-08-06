# System Design: In-Flight Movie Recommender (Duration-Constrained)

> **Focus areas:** Flight duration · Offline catalogs · Onboard cache · Sparse connectivity · Completion
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Hard duration feasibility; onboard vs ground; deal-breaker: ignore runtime vs remaining time
> **Interview theme:** Amazon SDE III / L6 — **Prime Video / Airlines** — movies that fit the flight under degraded connectivity

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

Goal: Recommend movies/shows that fit remaining flight duration with pre-staged catalogs and offline/intermittent personalization.

### 1.0 What this is / is not
| Dimension | This | Not |
|-----------|------|-----|
| Constraint | Runtime ≤ remaining−buffers | Unlimited browse |
| Connectivity | Often offline | Always-on streaming |
| Success | Completion + fit-to-flight | Clicks on too-long titles |

### 1.1 Functional requirements
Cover duration constraint, flight context, onboard catalog, pre-flight packs, episodes, kids, languages, mid-flight recompute, fallback, licensing, delayed metrics, multi-leg, optional Wi-Fi enhance.

**MVP:** hard time filter; onboard catalog; packs; popular fallback; delayed logs.
**Out of MVP:** cloud-required mid-flight inference.

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

Onboard metadata small; video via airline ops. Ground packs for ~300 pax cheap. Local re-rank <100ms.
`effective = remaining - taxi - safety - meal_opt - slack` (underestimate slightly).

## 3. High-Level Design

### 3.1 Dual planes
Ground: personalization + licensing + pack builder. Onboard: remaining-time filter, light re-rank, playback, encrypted logs.

### 3.2 Feasibility first
Hard-filter runtime/episodes ≤ effective; soft prefer 0.5–0.85×; shorts under ~25m.

### 3.3 Tradeoffs
Offline-first; Wi-Fi optional enhance only; seatback PIN/wipe; never ignore runtime.

## 4. Architecture Diagram

```text
[Ground] Profile+Catalog+ETA --> Pack Builder --> Gate sync
                                                    |
                                                    v
[Onboard] RemainingTime --> Filter/Rank --> Seatback UI --> Playback
               ^                                  |
          avionics/IFE                       Log buffer --> landing flush
```

## 5. Design Deep Dive

### 5.1 Invariants
Finishability first; kids ratings enforced onboard; privacy wipe; popular feasible fallback; licensing snapshot validity.

### 5.2 Packing & continue-watching
Re-filter as ETA moves; boost unfinished titles if leftover runtime fits.

### 5.3 Multi-tenant airlines
Configurable buffers/ratings/catalogs; clear IFE vs Amazon ownership.

### 5.4 Progressive scale
Standard sync API → segment packs → multi-tenant platform cells.

### 5.5 Metrics
Completion given start; too-long complaints; kids violations (~0); sync success.

## 6. Wrap-Up

### 6.1 What we designed
Duration-constrained in-flight recommender: ground packs, onboard feasibility filter/re-rank, offline-first, delayed measurement.

### 6.2 Key decisions worth defending
1. Hard runtime filter first
2. Ground heavy / onboard light
3. Offline-first fallback
4. Conservative buffers
5. Seatback privacy

### 6.3 Risks & follow-ups
- Airline integration variance
- Runtime metadata errors
- Licensing staleness
- Wi-Fi cloud coupling

### 6.4 Closer
> **In-Flight Movie Recommender**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — In-Flight Movie Recommender

**Q1. State the primary constraint first?**

**A:** Runtime/episodes must fit effective remaining flight time—hard filter before personalization.

**Q2. Why dual ground/onboard planes?**

**A:** Heavy ML and licensing on ground; offline constrained inference onboard; connectivity intermittent.

**Q3. What if Wi-Fi is great mid-flight?**

**A:** Optional enhance path only; core offline path remains correct.

**Q4. How to compute effective time?**

**A:** remaining - buffers(taxi, safety, meal_opt, slack); underestimate slightly.

**Q5. Series packaging?**

**A:** Max episodes that fit; prefer arcs; warn on unfinished cliffs.

**Q6. Seatback privacy?**

**A:** PIN, encrypt packs, wipe end-of-flight, no cross-seat reads.

**Q7. Kids policy enforcement location?**

**A:** Onboard must enforce even if packs stale—ratings filters local.

**Q8. Licensing expiry?**

**A:** Snapshot validity; hide expired; sync turnaround; safe classics list.

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
- [ ] Hard runtime filter first
- [ ] Ground heavy / onboard light
- [ ] Offline-first fallback
- [ ] Conservative buffers
- [ ] Seatback privacy

## Deep Technical Notes — In-Flight Movie Recommender

### Ground pack builder pipeline

Ingest flight schedule + estimated duration; resolve passenger personalization tokens where allowed; intersect with airline licensed catalog snapshot; hard-filter by planned effective time; rank; emit signed packs for gate sync.

### Onboard re-filter loop

Every N minutes or on ETA jump: recompute effective time; drop infeasible titles; promote shorts rail under threshold; update UI rails without cloud calls.

### Buffer policy configuration

Airline×aircraft×route overlays. Long-haul meals differ from short-haul. Product + airline ops co-own numbers; software consumes config.

### Catalog & media metadata

title_id, runtime, episode runtimes, ratings, languages, kids_ok, license_window, asset locality. Checksums for snapshots.

### Security model

Signed catalogs/packs; encrypted PII; wipe protocols; prevent exfiltration over passenger portal Wi-Fi.

### Evaluation program

Completion rate, too-long complaints, kids violations (~0), sync success, CSAT. A/B mostly on ground builder.

### Degraded modes catalog

Enumerate modes in runbooks: no profile, no time feed, no sync, corrupt catalog, low storage onboard.

### Platform roadmap

More airlines; richer short-form; optional online enhance; still finishability-first.

## Interview Cards — In-Flight Movie Recommender

### Card 1: State the primary constraint first?

Runtime/episodes must fit effective remaining flight time—hard filter before personalization.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Why dual ground/onboard planes?

Heavy ML and licensing on ground; offline constrained inference onboard; connectivity intermittent.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: What if Wi-Fi is great mid-flight?

Optional enhance path only; core offline path remains correct.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: How to compute effective time?

remaining - buffers(taxi, safety, meal_opt, slack); underestimate slightly.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Series packaging?

Max episodes that fit; prefer arcs; warn on unfinished cliffs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Seatback privacy?

PIN, encrypt packs, wipe end-of-flight, no cross-seat reads.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Kids policy enforcement location?

Onboard must enforce even if packs stale—ratings filters local.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Licensing expiry?

Snapshot validity; hide expired; sync turnaround; safe classics list.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Metrics delay?

Encrypted buffer flush after landing; late training join OK.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Continue watching?

Boost if leftover runtime fits—highest satisfaction.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Multi-leg?

Per-leg context; don’t use total trip time for a short hop.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Airline heterogeneity?

Configurable buffers/ratings/catalogs; multi-tenant cells.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Runtime metadata wrong?

Trust incident; QA against media service; hotfix catalog.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Anonymous seatback?

Segment popularity feasible packs; no Prime profile.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Device types?

Seatback vs personal device portal share feasibility API.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Deal-breaker?

Cloud-only inference with no offline feasible fallback; or ignoring runtime.

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

## More Interview Q&A — In-Flight Movie Recommender

**Q1. State the primary constraint first?**

**A:** Runtime/episodes must fit effective remaining flight time—hard filter before personalization.

**Q2. Why dual ground/onboard planes?**

**A:** Heavy ML and licensing on ground; offline constrained inference onboard; connectivity intermittent.

**Q3. What if Wi-Fi is great mid-flight?**

**A:** Optional enhance path only; core offline path remains correct.

**Q4. How to compute effective time?**

**A:** remaining - buffers(taxi, safety, meal_opt, slack); underestimate slightly.

**Q5. Series packaging?**

**A:** Max episodes that fit; prefer arcs; warn on unfinished cliffs.

**Q6. Seatback privacy?**

**A:** PIN, encrypt packs, wipe end-of-flight, no cross-seat reads.

**Q7. Kids policy enforcement location?**

**A:** Onboard must enforce even if packs stale—ratings filters local.

**Q8. Licensing expiry?**

**A:** Snapshot validity; hide expired; sync turnaround; safe classics list.

**Q9. Metrics delay?**

**A:** Encrypted buffer flush after landing; late training join OK.

**Q10. Continue watching?**

**A:** Boost if leftover runtime fits—highest satisfaction.

**Q11. Multi-leg?**

**A:** Per-leg context; don’t use total trip time for a short hop.

**Q12. Airline heterogeneity?**

**A:** Configurable buffers/ratings/catalogs; multi-tenant cells.

**Q13. Runtime metadata wrong?**

**A:** Trust incident; QA against media service; hotfix catalog.

**Q14. Anonymous seatback?**

**A:** Segment popularity feasible packs; no Prime profile.

**Q15. Device types?**

**A:** Seatback vs personal device portal share feasibility API.

**Q16. Deal-breaker?**

**A:** Cloud-only inference with no offline feasible fallback; or ignoring runtime.

## Deep Technical Addenda — In-Flight Movie Recommender

### Ground pack builder pipeline

Ingest flight schedule + estimated duration; resolve passenger personalization tokens where allowed; intersect with airline licensed catalog snapshot; hard-filter by planned effective time; rank; emit signed packs for gate sync.

### Onboard re-filter loop

Every N minutes or on ETA jump: recompute effective time; drop infeasible titles; promote shorts rail under threshold; update UI rails without cloud calls.

### Buffer policy configuration

Airline×aircraft×route overlays. Long-haul meals differ from short-haul. Product + airline ops co-own numbers; software consumes config.

### Catalog & media metadata

title_id, runtime, episode runtimes, ratings, languages, kids_ok, license_window, asset locality. Checksums for snapshots.

### Security model

Signed catalogs/packs; encrypted PII; wipe protocols; prevent exfiltration over passenger portal Wi-Fi.

### Evaluation program

Completion rate, too-long complaints, kids violations (~0), sync success, CSAT. A/B mostly on ground builder.

### Degraded modes catalog

Enumerate modes in runbooks: no profile, no time feed, no sync, corrupt catalog, low storage onboard.

### Platform roadmap

More airlines; richer short-form; optional online enhance; still finishability-first.

## Tradeoff Matrices — In-Flight Movie Recommender

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

## Operability Addenda — In-Flight Movie Recommender

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

## Worked Capacity Narrative — In-Flight Movie Recommender

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — In-Flight Movie Recommender

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — In-Flight Movie Recommender

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — In-Flight Movie Recommender
### S1. Finishability first

A personalized 3h film on a 90m hop is a failed design. Hard filter runtime before rank.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Dual planes

Ground: heavy ML + licensing + packs. Onboard: filter/re-rank/playback/logs. Online Wi-Fi optional only.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Effective time

remaining - taxi - safety - meal_opt - slack; underestimate slightly; recompute as ETA moves.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Series packaging

Max episodes that fit; prefer arcs; warn on cliffs you can’t finish.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Seatback privacy

PIN, encrypt packs, wipe end-of-flight, no cross-seat profile reads.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Licensing snapshots

Validity windows; hide expired; turnaround sync; safe classics list.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Kids enforcement onboard

Local ratings filters even if packs stale—policy non-bypassable.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Airline multi-tenant

Configurable buffers/ratings/catalogs; clear IFE hardware vs Amazon software ownership.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — In-Flight Movie Recommender

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| 45m short-haul | Episodes/shorts rails | Preserve trust/UX | Postmortem + guardrail |
| Red-eye long haul | Calm priors + long movies feasible | Preserve trust/UX | Postmortem + guardrail |
| No personalization | Popular feasible list | Preserve trust/UX | Postmortem + guardrail |
| No time feed | Scheduled block minus elapsed | Preserve trust/UX | Postmortem + guardrail |
| Shared seatback | PIN + wipe | Preserve trust/UX | Postmortem + guardrail |
| License expired | Hide; safe classics | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — In-Flight Movie Recommender

**RQ1. Why does 'Finishability first' matter in an L6 interview?**

**A:** A personalized 3h film on a 90m hop is a failed design. Hard filter runtime before rank. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Finishability first' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Finishability first' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Dual planes' matter in an L6 interview?**

**A:** Ground: heavy ML + licensing + packs. Onboard: filter/re-rank/playback/logs. Online Wi-Fi optional only. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Dual planes' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Dual planes' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Effective time' matter in an L6 interview?**

**A:** remaining - taxi - safety - meal_opt - slack; underestimate slightly; recompute as ETA moves. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Effective time' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Effective time' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Series packaging' matter in an L6 interview?**

**A:** Max episodes that fit; prefer arcs; warn on cliffs you can’t finish. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Series packaging' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Series packaging' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Seatback privacy' matter in an L6 interview?**

**A:** PIN, encrypt packs, wipe end-of-flight, no cross-seat profile reads. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Seatback privacy' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Seatback privacy' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Licensing snapshots' matter in an L6 interview?**

**A:** Validity windows; hide expired; turnaround sync; safe classics list. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Licensing snapshots' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Licensing snapshots' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Kids enforcement onboard' matter in an L6 interview?**

**A:** Local ratings filters even if packs stale—policy non-bypassable. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Kids enforcement onboard' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Kids enforcement onboard' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Airline multi-tenant' matter in an L6 interview?**

**A:** Configurable buffers/ratings/catalogs; clear IFE hardware vs Amazon software ownership. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Airline multi-tenant' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Airline multi-tenant' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — In-Flight Movie Recommender

### Walkthrough beat 1

In beat 1, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through In-Flight Movie Recommender: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — In-Flight Movie Recommender

- [ ] Can explain **Finishability first** with numbers and a deal-breaker
- [ ] Can explain **Dual planes** with numbers and a deal-breaker
- [ ] Can explain **Effective time** with numbers and a deal-breaker
- [ ] Can explain **Series packaging** with numbers and a deal-breaker
- [ ] Can explain **Seatback privacy** with numbers and a deal-breaker
- [ ] Can explain **Licensing snapshots** with numbers and a deal-breaker
- [ ] Can explain **Kids enforcement onboard** with numbers and a deal-breaker
- [ ] Can explain **Airline multi-tenant** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **45m short-haul**
- [ ] Has a 30-second runbook for **Red-eye long haul**
- [ ] Has a 30-second runbook for **No personalization**
- [ ] Has a 30-second runbook for **No time feed**
- [ ] Has a 30-second runbook for **Shared seatback**
- [ ] Has a 30-second runbook for **License expired**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining In-Flight Movie Recommender to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

*End of document — In-Flight Movie Recommender (Duration-Constrained) (SDE III)*
