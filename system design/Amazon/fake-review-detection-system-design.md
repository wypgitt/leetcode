# System Design: Fake-Review Detection (Amazon Marketplace Trust)

> **Focus areas:** Verified purchase · Graph rings · Online/nearline ML · Progressive enforcement · Appeals · Adversarial LLM spam · Fairness/FP · Policy explainability
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Trust metrics over AUC-only; split online vs graph; human loop; marketplace cells
> **Interview theme:** Amazon SDE III / L6 — **fake-review detection** for Amazon.com / Marketplace

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

Goal: Detect and mitigate fake, incentivized, and abusive reviews while preserving legitimate critical feedback—protecting customer trust and marketplace fairness.

### 1.0 What this is / is not
| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Risk scoring + enforcement actions | Full PDP rendering |
| SoT | Reviews + orders + graph features | Replacing Orders DB |
| Amazon lens | Customer trust, seller fairness, policy | Kaggle AUC flex |

### 1.1 Functional requirements
| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Signals? | VP, text, images, velocity, device, graph, seller priors | Feature platform |
| F2 | Actions? | Allow, hold, demote, remove, label, rate-limit | State machine |
| F3 | Latency? | Online ms–s; graph minutes–hours | Dual plane |
| F4 | Appeals? | Yes with SLO | Case system |
| F5 | Explain? | Policy codes + factors | Audit store |
| F6 | Adversaries? | Farms, LLMs, slow drip | Red team |
| F7 | Marketplaces? | Multi | Cells + locales |
| F8 | Human review? | High impact | Queues |
| F9 | Metrics? | FP/FN, complaints, authenticity | Not AUC alone |
| F10 | Training? | Labeled rings/appeals | PIT features |

**MVP:** submit-time online scorer, async enrich, progressive actions, graph nearline, appeals, audit, shadow models.
**Out:** Fully automatic irreversible bans without appeal on weak scores; reading private messages as sole signal without policy.

### 1.2 NFRs
Submit path p99 budgeted; hold decision minutes; appeal SLO days; 99.9% scoring availability with fail-safe (fail-closed for risky categories); privacy compliance.

### 1.3 Cases
Happy: VP review scores clean → publish; suspicious → hold → nearline clear/remove.
Edges: review bomb; LLM spam; honest 1-star surge after defect; seller appeal; feature skew; cross-ASIN copy-paste farm.

### 1.4 Progressive scale
| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Reviews/day | 5M | 50M | 500M | 5B |
| Graph edges touched/day | 50M | 500M | 5B | 50B |
| Online score QPS | 2K | 20K | 200K | 2M |
| Appeals/day | 20K | 100K | 500K | 2M |

Jumps: stream feature platform → cell’d graph+distilled models → platformized detectors + heavier automation with guardrails.

### 1.5 Scope repeat-back
> Fake-review detection with online+nearline scoring, graph cluster detection, progressive enforcement, appeals/audit, adversarial robustness—scaled across marketplaces with explicit FP trust controls.

---
## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes
Submit scoring 2K/s peaks; async enrich 5×; graph jobs batch/nearline; PDP reads precomputed trust fields at huge QPS (not live ML).

### 2.2 Storage
Reviews text+meta PBs over years; feature store TBs; graph edges tens of billions; audit immutable.

### 2.3 Latency budget
Online score < 50–100ms; publish path including score < few hundred ms; graph enrichment SLA separate.

### 2.4 Cost
Dominant: ML compute + human review. Lever: automate high-precision removes; humans on ambiguous. Track `$/1K reviews` and appeal minutes.

---
## 3. High-Level Design

**Components:** Review API, Online Risk Scorer, Feature Store, Stream pipeline, Graph Fraud Service, Policy Engine, Enforcement State Machine, Appeals/Case, Human Review UI, Model Training/Shadow, Audit Log, Marketplace cells.

**Action state machine:**
```text
submitted -> (allow | hold)
hold -> (publish | demote | remove)
publish -> (demote | remove) via nearline
all actions -> audit + notify policy templates
```

**Score fusion:**
```text
risk = f(online_text, velocity, device, vp, seller_prior) 
risk += g(graph_cluster, near_dup, incentivized)
decision = policy(risk, category, marketplace)
```

**Tradeoffs:** precision vs recall; hold latency vs spam window; automation vs appeals cost; transparency vs gaming.

---
## 4. Architecture Diagram

```text
 Customer -> Review API -> Online Scorer -> Policy Engine -> Enforcement DB
                |               |                |
                |               +-> Feature Store
                v
         Event Stream -> Nearline Workers -> Graph Service -> Policy Engine
                                              |
                                         Appeals/Human Queue
 PDP/Ranking <--- trust features / filtered review set
 Model Ops: train/shadow/canary -> Online + Nearline models
 Audit Log << all decisions (score_version, policy_version)
```

Degrade: if scorer down → fail-closed hold for high-risk categories; fail-open publish+async for low-risk with velocity caps—**explicit choice**.

---
## 5. Design Deep Dive

### 5.1 Reliability (R)
Invariants: every action audited; policy_version+model_version stamped; appeals can restore; no silent hard-delete without record; PIT features for training; idempotent event processing.

### 5.2 Scalability (S)
| Scale | Architecture |
|-------|--------------|
| 1× | Online models + nightly graph |
| 10× | Streaming features; sharded graph |
| 100× | Marketplace cells; distilled online; ANN near-dup |
| 1,000× | Platform detectors; heavier auto with calibrated guardrails |

### 5.3 Maintainability (M)
Shadow eval gates; fairness dashboards; red-team suites; clear ownership Policy vs ML vs Serving; locale model packs.

### 5.4 Graph rings
Build reviewer–product–seller edges; device/payment clusters; connected components / community detection; score cluster risk; quarantine cluster publishing.

### 5.5 Adversarial LLM
Near-dup embeddings; entropy/style features; account age×velocity; challenge friction; continuous refresh—admit arms race.

---
## 6. Wrap-Up

### 6.1 What we designed
Amazon fake-review detection: dual-plane scoring, graph rings, progressive enforcement, appeals/audit, adversarial hardening, marketplace cells.

### 6.2 Key decisions worth defending
1. VP necessary not sufficient
2. Online + nearline planes
3. Progressive actions (hold/demote/remove)
4. Human appeals for trust
5. Policy ≠ raw model score
6. FP on honest negatives as SEV
7. Shadow before enforce
8. Cells + privacy

### 6.3 Risks & follow-ups
LLM arms race; appeal backlog; training leakage; seller gaming explanations; cross-border law.

### 6.4 Closer
> **Fake-Review Detection**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Fake-Review Detection

**Q1. Online or offline detection?**

**A:** Both: online velocity/abuse gates; offline/nearline graph+ML for rings; progressive actions.

**Q2. Is verified purchase enough?**

**A:** No—necessary signal, not sufficient. Combine with graph/behavior/content.

**Q3. How to stop review bombs?**

**A:** Velocity caps, cluster detection, temporary hold on ASIN spikes, human escalation.

**Q4. LLM-generated fakes?**

**A:** Detectors, stylometry, graph (many new accounts), challenge friction; evolving arms race.

**Q5. False positive cost?**

**A:** Honest negative reviews are sacred; track FP on calibrated sets; appeals SLO.

**Q6. Where does scoring run?**

**A:** Submit path light; async enrich; read path uses stored trust features—not full ML per PDP.

**Q7. Graph scale?**

**A:** Sharded bipartite overlays; approximate community detection; nearline hours/minutes.

**Q8. Seller retaliation?**

**A:** Policy + detection for brigading; separate customer vs seller incentives.

**Q9. Cold-start products?**

**A:** Higher scrutiny windows post-launch; prior seller risk priors.

**Q10. Explain a takedown?**

**A:** Policy code + top factors; not raw model dump to sellers; full detail internal audit.

**Q11. Training labels?**

**A:** Human audits, appeals outcomes, known rings; careful leakage and bias.

**Q12. Deal-breaker?**

**A:** Keyword blacklist as sole system, or blocking all non-VP reviews globally without nuance.

**Q13. PII in features?**

**A:** Minimize; hash devices; retention limits; cell isolation.

**Q14. A/B trust metrics?**

**A:** Complaint rate, refund correlation, perceived authenticity surveys—not only model AUC.

**Q15. Incentivized reviews?**

**A:** Detect solicitation; disclose/remove per policy; graph of coupon campaigns.

**Q16. Who pages?**

**A:** Trust/Safety eng for pipelines; Policy for threshold ethics; Marketplace for seller actions.

**Q17. Realtime PDP impact?**

**A:** Precomputed review trust scores in store; ranking merge; no heavy graph on read.

**Q18. Multi-marketplace?**

**A:** Cells; different regs (e.g., disclosure laws); no cross-leak of private signals.

**Q19. Adversarial accounts?**

**A:** Shared payment/device graphs; slow-burn reputation; purchase diversity features.

**Q20. Human-in-loop when?**

**A:** High-impact ASINs, appeals, novel attacks, legal holds.


---
## 8. Appendices

### A — Glossary
| Term | Meaning |
|------|---------|
| VP | Verified Purchase |
| Hold | Not publicly visible pending review |
| Demote | Visible but ranking suppressed |
| Ring | Coordinated fraud cluster |
| PIT | Point-in-time feature correctness |
| Policy_version | Rules stamp |
| Cell | Marketplace isolation |
| Deal-breaker | Keyword-only filter as sole defense |

### B — Oncall checklist
- [ ] Online score p99
- [ ] Hold backlog
- [ ] FP spike dashboards
- [ ] Graph lag
- [ ] Appeal SLO
- [ ] Shadow vs champion deltas

### C — Event schema sketch
```text
ReviewSubmitted{review_id, asin, customer, vp, text_ref, device_risk, ts}
RiskScored{review_id, scores..., model_version}
ActionApplied{review_id, action, policy_version, reason_codes}
```

### D — Scale checklist
Stream features → cells → platform automation with guardrails.

### E — Estimation cheat-sheet
```text
online_cpu ≈ submit_qps × model_ms
graph_edges/day ≈ reviews × avg_degree_touch
```

### F — Closer checklist
- [ ] Dual plane
- [ ] Graph rings
- [ ] FP trust
- [ ] Appeals
- [ ] Progressive scale

## Deep Technical Notes — Fake-Review Detection

### Online feature set
Text toxicity/spam, language, length, similarity-to-known-templates, account age, orders diversity, device risk, IP velocity, ASIN review velocity, seller prior.

### Near-dup ANN
Embed review text; query ANN; cluster near-duplicates across ASINs; farm signal.

### Enforcement durability
Action log is SoT for visibility; review body soft-deleted; legal retention separate.

### Training hygiene
No future edges; no appeal leakage into pre-decision features improperly; stratified FP sets including harsh legitimate reviews.

### Marketplace fairness
Thresholds per category risk; avoid systematically silencing minority locales—monitor.

### Integration with ranking
Trust score feature in helpfulness ranker; filtered sets for star aggregates; document publicly at high level.

## Interview Cards — Fake-Review Detection

### Card 1: Online or offline detection?

Both: online velocity/abuse gates; offline/nearline graph+ML for rings; progressive actions.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Is verified purchase enough?

No—necessary signal, not sufficient. Combine with graph/behavior/content.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: How to stop review bombs?

Velocity caps, cluster detection, temporary hold on ASIN spikes, human escalation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: LLM-generated fakes?

Detectors, stylometry, graph (many new accounts), challenge friction; evolving arms race.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: False positive cost?

Honest negative reviews are sacred; track FP on calibrated sets; appeals SLO.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Where does scoring run?

Submit path light; async enrich; read path uses stored trust features—not full ML per PDP.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Graph scale?

Sharded bipartite overlays; approximate community detection; nearline hours/minutes.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Seller retaliation?

Policy + detection for brigading; separate customer vs seller incentives.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Cold-start products?

Higher scrutiny windows post-launch; prior seller risk priors.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Explain a takedown?

Policy code + top factors; not raw model dump to sellers; full detail internal audit.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Training labels?

Human audits, appeals outcomes, known rings; careful leakage and bias.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Deal-breaker?

Keyword blacklist as sole system, or blocking all non-VP reviews globally without nuance.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: PII in features?

Minimize; hash devices; retention limits; cell isolation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: A/B trust metrics?

Complaint rate, refund correlation, perceived authenticity surveys—not only model AUC.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Incentivized reviews?

Detect solicitation; disclose/remove per policy; graph of coupon campaigns.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Who pages?

Trust/Safety eng for pipelines; Policy for threshold ethics; Marketplace for seller actions.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.


## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Trust scope + FP stakes |
| 5–12 | Scale numbers + dual plane |
| 12–22 | HLD + ASCII |
| 22–35 | Graph, policy, appeals, adversarial |
| 35–45 | Tradeoffs & Q&A |

---
## 10. Operability

### Golden signals
Submit latency, hold backlog, action rates, FP proxies, graph lag, appeal age.

### Rollback ladder
Shadow off → revert model_version → loosen demote → policy freeze → postmortem trust section.

### Kill switches
Disable auto-remove; hold-only mode; category fail-closed; cell isolate.

### Security/privacy
PII minimization; access-controlled features; audit; encryption.

### Cost worksheet
ML + humans. Lever: high-precision auto-remove.

### Progressive scale
10× streaming/graph shards; 100× cells/distill; 1,000× platform detectors.

### Cross-team deps
Orders/VP, Identity risk, Catalog, Policy, Seller services, PDP ranking.

---
## More Interview Q&A — Fake-Review Detection

**Q1. Content embeddings?**

**A:** Yes for similarity farms; ANN nearline clustering of near-duplicate text.

**Q2. Image reviews?**

**A:** Reverse image / perceptual hash for stolen photos.

**Q3. Video reviews?**

**A:** Heavier async pipeline; audio transcripts.

**Q4. Calibration?**

**A:** Platt/isotonic per marketplace; threshold by risk class.

**Q5. Feature store PIT?**

**A:** Mandatory to avoid leakage from future graph edges.

**Q6. Streaming join?**

**A:** Review events + order events + login risk → feature topic.

**Q7. Rate limits?**

**A:** Per account/ASIN/day; separate from quality score.

**Q8. Shadow mode models?**

**A:** Always before enforce; compare FP/FN vs champion.

**Q9. Hard remove vs demote?**

**A:** Demote when uncertain; remove when high precision policy hit.

**Q10. Review ranking interplay?**

**A:** Helpfulness × trust; never boost suspected fakes via engagement alone.

**Q11. Seller star rating math?**

**A:** Use filtered set; document exclusion rules publicly at high level.

**Q12. Compromised accounts?**

**A:** Risk service signals; temporary hold publishing.

**Q13. International language?**

**A:** Per-locale models; shared graph features.

**Q14. Metrics cardinality?**

**A:** No raw customer_id on prom labels.

**Q15. Cost of graph?**

**A:** Sampled edges; sketch structures; tiered storage cold edges.

**Q16. Legal discovery?**

**A:** Immutable audit log of actions/scores versions.

**Q17. Red team?**

**A:** Continuous fake campaigns in staging; score robustness.

**Q18. Feedback loops?**

**A:** Removing fakes changes training—snapshot datasets.

**Q19. Coupon abuse adjacent?**

**A:** Share signals with promotions fraud—not single monolith.

**Q20. Canary ASINs?**

**A:** Synthetic inject tests in prod with labels.

**Q21. SLO for hold latency?**

**A:** Minutes for online; hours for graph enrich—state both.

**Q22. Empty reviews tab?**

**A:** Fallback to lower thresholds with banner? Prefer show honest few.

**Q23. Cross-product copy-paste?**

**A:** Near-dup across ASINs signals farm.

**Q24. Ownership boundary?**

**A:** Detection platform vs policy decision vs marketplace enforcement.


## Deep Technical Addenda — Fake-Review Detection

### Worked review-bomb example
ASIN gets 2K reviews/hour vs baseline 20. Online velocity hold triggers; graph finds 80% accounts share device cluster; policy removes cluster; legitimate VP defect complaints (diverse graph) remain after human sample.

### Star-rating integrity
Aggregate stars use filtered set S; publish methodology; prevent oscillation from oscillating model thresholds via hysteresis.

### Appeal economics
If appeals 5% of actions and 30% overturn, thresholds wrong—optimize for overturn rate + customer complaints jointly.

## Tradeoff Matrices — Fake-Review Detection

| Choice | Pros | Cons | Amazon pick |
|--------|------|------|-------------|
| Auto-remove all medium risk | Less spam | FP trust harm | Demote + human for medium |
| VP-only filter | Simple | Misses bought accounts | VP+graph+content |
| Fully opaque ML | Harder gaming | Appeals/legal weak | Policy codes + factors |
| One global model | Simple | Locale fail | Per-marketplace packs |

## Operability Addenda — Fake-Review Detection

Pages: scorer errors; backlog; FP spike; graph lag; appeal breach; canary divergence.

## Worked Capacity Narrative — Fake-Review Detection

PDP cannot run graph ML. Precompute trust. Interviewers fail candidates who put GNN on the read path at Amazon QPS.

## Customer-Trust Paragraph — Fake-Review Detection

Fakes mislead purchases; false removals silence real critics—both are customer-obsession failures. Say it explicitly.

## Progressive Scale Recap — Fake-Review Detection

- **10×:** streaming features, sharded graph
- **100×:** cells, distilled online, ANN
- **1,000×:** platform detectors, guarded automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Fake-Review Detection

### S1. Verified purchase signals

VP is strong but not sufficient—bought accounts and incentivized reviews exist. Combine VP with graph, behavioral, and content signals; never sole oracle.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S2. Graph fraud clusters

Reviewer–product–seller bipartite graphs; shared devices/payments/addresses; community detection for rings; nearline updates.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S3. Online vs offline scoring

Cheap online features at submit; heavy ML/graph offline/nearline; progressive enforcement (hold, demote, remove).
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S4. Human review loop

Appeals and high-impact takedowns need human queues; model assists, policy owns; audit trails.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S5. Seller abuse & incentivized

Detect solicitation patterns, coupon-for-review, brigading after launch; marketplace fairness.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S6. Adversarial robustness

Paraphrase farms, LLM-generated reviews, slow-drip accounts; red-team continuously; feature stores versioned.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S7. Fairness & false positives

Wrongly burying legitimate critical reviews destroys trust; measure FP on honest negatives; calibrated thresholds per marketplace.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S8. Explainability & policy

Actions cite policy codes; store score factors for audit; separate ML score from policy decision.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?


## Scenario Runbooks — Fake-Review Detection

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Viral fake ring launch | Hold ASIN reviews; graph quarantine | Protect customers | Ring takedown + seller action |
| Model FP spike | Revert model; loosen demote | Restore honest reviews | Shadow eval gates |
| LLM spam wave | Content detectors + rate limits | Reduce noise | Feature refresh |
| Appeal backlog SEV | Prioritize by impact; temp restore high-conf FP | Seller/customer fairness | Queue staffing |
| Feature store skew | Freeze model; PIT fix | Stop bad scores | Skew monitors |
| Cross-marketplace leak | Cell isolate scoring data | Privacy/compliance | Access audit |


## Rapid-Fire Q&A — Fake-Review Detection

**RQ1. Why does 'Verified purchase signals' matter in an L6 interview?**

**A:** VP is strong but not sufficient—bought accounts and incentivized reviews exist. Combine VP with graph, behavioral, and content signals; never sole oracle. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Verified purchase signals' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Verified purchase signals' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Graph fraud clusters' matter in an L6 interview?**

**A:** Reviewer–product–seller bipartite graphs; shared devices/payments/addresses; community detection for rings; nearline updates. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Graph fraud clusters' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Graph fraud clusters' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Online vs offline scoring' matter in an L6 interview?**

**A:** Cheap online features at submit; heavy ML/graph offline/nearline; progressive enforcement (hold, demote, remove). Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Online vs offline scoring' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Online vs offline scoring' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Human review loop' matter in an L6 interview?**

**A:** Appeals and high-impact takedowns need human queues; model assists, policy owns; audit trails. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Human review loop' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Human review loop' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Seller abuse & incentivized' matter in an L6 interview?**

**A:** Detect solicitation patterns, coupon-for-review, brigading after launch; marketplace fairness. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Seller abuse & incentivized' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Seller abuse & incentivized' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Adversarial robustness' matter in an L6 interview?**

**A:** Paraphrase farms, LLM-generated reviews, slow-drip accounts; red-team continuously; feature stores versioned. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Adversarial robustness' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Adversarial robustness' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Fairness & false positives' matter in an L6 interview?**

**A:** Wrongly burying legitimate critical reviews destroys trust; measure FP on honest negatives; calibrated thresholds per marketplace. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Fairness & false positives' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Fairness & false positives' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Explainability & policy' matter in an L6 interview?**

**A:** Actions cite policy codes; store score factors for audit; separate ML score from policy decision. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Explainability & policy' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Explainability & policy' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Fake-Review Detection

### Walkthrough beat 1

Customer submits review: authz + VP check + online scorer (text, velocity, device risk) → provisional publish or hold. Metric: hold_rate, submit_p99.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Nearline graph job links reviewer to cluster; score updates; demote/remove with policy code. Degradation: if graph lag, rely on online + velocity caps.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

PDP read path: ranking uses trust-adjusted scores; never show removed; label incentivized when policy requires. Watch complaint_rate.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Seller appeals: case system pulls explanation features; human decision writes durable override with expiry; model learns via labeled outcomes carefully (bias).

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

10×: stream features + sharded graph. 100×: marketplace cells + distilled online models. 1,000×: on-device signals light; platform multi-tenant detectors.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Precision/recall tradeoff: for health/safety categories fail-closed hold; for ordinary, prefer demote over delete when uncertain.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Trust SEV: leaving fake 5-stars on medical devices—or mass-removing legitimate 1-stars—both catastrophic.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

Unit economics: $ per review scored; human minutes per appeal; fraud prevented GMV proxy.

Call out one tradeoff you are making (precision vs recall, latency vs depth, automation vs human review) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Fake-Review Detection

- [ ] Can explain **Verified purchase signals** with numbers and a deal-breaker
- [ ] Can explain **Graph fraud clusters** with numbers and a deal-breaker
- [ ] Can explain **Online vs offline scoring** with numbers and a deal-breaker
- [ ] Can explain **Human review loop** with numbers and a deal-breaker
- [ ] Can explain **Seller abuse & incentivized** with numbers and a deal-breaker
- [ ] Can explain **Adversarial robustness** with numbers and a deal-breaker
- [ ] Can explain **Fairness & false positives** with numbers and a deal-breaker
- [ ] Can explain **Explainability & policy** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Viral fake ring launch**
- [ ] Has a 30-second runbook for **Model FP spike**
- [ ] Has a 30-second runbook for **LLM spam wave**
- [ ] Has a 30-second runbook for **Appeal backlog SEV**
- [ ] Has a 30-second runbook for **Feature store skew**
- [ ] Has a 30-second runbook for **Cross-marketplace leak**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Fake-Review Detection to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


*End of document — Fake-Review Detection (Amazon Marketplace Trust) (SDE III)*


## Whiteboard Numeric Drills — Fake Review Detection

### Drill A — 10× jump
State the baseline bottleneck metric, the mechanism that breaks first when traffic rises 10×, and the concrete architectural jump (not “add servers”). Name the dashboard panel that confirms the jump worked.

### Drill B — 100× jump
Explain which consistency/freshness/accuracy ε you accept at 100× and how the customer is informed or protected. Tie to a kill switch.

### Drill C — 1,000× jump
Describe cell isolation, approximate algorithms, or edge offload. Call the unit-cost metric (`$/M requests` or equivalent) and what linear scaling would have cost.

### Drill D — Ownership one-liner
Who pages for latency vs correctness vs policy? What artifact (config pointer, model version, ring map) do you revert?

### Drill E — Deal-breaker refusal
In one sentence, refuse the classic bad design for this topic and replace it with the Amazon-bar alternative.

