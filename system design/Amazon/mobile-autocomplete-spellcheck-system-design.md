# System Design: Mobile Autocomplete & Spell-Check (On-Device + Server Hybrid)

> **Focus areas:** On-device LM · Server long-tail · Spell correction · Privacy · Sync dictionaries · Battery
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** On-device vs server split; deal-breaker: every keystroke must hit server
> **Interview theme:** Amazon SDE III / L6 — **Amazon mobile** hybrid typing UX — privacy, battery, offline with server intelligence

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

Goal: Mobile autocomplete and spell-check that works on-device for latency/offline/privacy and uses server for long-tail/catalog-aware assist.

### 1.0 What this is / is not
| Dimension | This | Not |
|-----------|------|-----|
| Job | Suggest + spell while typing | Full cloud SERP |
| Location | On-device first | Server-mandatory keystroke |
| Privacy | Minimize keystroke exfil | Log all keystrokes forever |

### 1.1 Functional requirements
Cover suggest, spell, offline, server assist, local lexicon, languages, consent, battery, latency, catalog terms, safety, pack sync, autocorrect modes, opt-in analytics, experiments.

**MVP:** on-device LM/dict + spell; optional consented assist; signed packs; secure-field hard off.
**Out of MVP:** server-mandatory every keystroke; learning from passwords.

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

Local ≤16–30ms; packs tens of MB/language with deltas. Assist ~10% keystrokes when confidence low. Battery: cap neural ms/keystroke; n-gram fallback on thermal.

## 3. High-Level Design

### 3.1 Hybrid loop
```text
local = device_model()
if high_conf or offline or no_consent or secure_field: return safety(local)
return safety(merge(local, assist(prefix_redacted, deadline)))
```

### 3.2 Components
SDK, on-device LM/dict, user lexicon, safety, pack manager, assist API, pack builder, privacy aggregates.

### 3.3 Tradeoffs
Local-first; never learn passwords; quantized signed packs; consent-gated telemetry.

## 4. Architecture Diagram

```text
DEVICE: Field SDK --> Local LM/Dict --> Safety --> UI
           |            ^
           |       Lexicon / Pack Manager <--- CDN signed packs
           v
     Assist client --consented+uncertain--> Server Assist (catalog/long-tail)
```

## 5. Design Deep Dive

### 5.1 Invariants
Secure fields never learn/assist; offline path works; safety on merge; signed packs; consent gates assist.

### 5.2 Models & spell
Quantized LM + dict; noisy-channel spell; protect user lexicon names; undo-friendly autocorrect.

### 5.3 Field policy matrix
search/chat/email/password/address each define learn/assist/autocorrect/telemetry.

### 5.4 Progressive scale
Better deltas → on-device neural default → optional federated learning.

### 5.5 Ownership
Mobile client (budgets), suggest/assist service, privacy consent UX.

## 6. Wrap-Up

### 6.1 What we designed
Hybrid on-device+server autocomplete/spell-check: quantized local LM/dicts, lexicon, safety, consented assist, signed packs, battery budgets.

### 6.2 Key decisions worth defending
1. Local-first
2. Never learn secure fields
3. Quantized signed packs
4. Consent-gated aggregates
5. Merge via safety

### 6.3 Risks & follow-ups
- Pack size vs quality
- Code-switch
- Assist over-trigger cost
- OS IME boundary

### 6.4 Closer
> **Mobile Autocomplete & Spell-Check**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Mobile Autocomplete & Spell-Check

**Q1. Why local-first?**

**A:** Offline, battery, privacy, RTT jitter—mobile typing cannot require server keystrokes.

**Q2. When server assist?**

**A:** Low local confidence + online + consent + allowed field + budget.

**Q3. Password fields?**

**A:** No learn, no assist, no logging—hard invariant.

**Q4. Pack size budgets?**

**A:** Tens of MB per language; tiered tiny/base/full; deltas.

**Q5. Autocorrect aggressiveness?**

**A:** User setting + undo-rate feedback loop.

**Q6. User lexicon role?**

**A:** Protect names/slang; improve personalization locally without cloud.

**Q7. Kids Fire tablets?**

**A:** Stricter lexicon; assist off default; stronger safety.

**Q8. Code-switching?**

**A:** Lang-ID; mixed packs; careful corrections.

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
- [ ] Local-first
- [ ] Never learn secure fields
- [ ] Quantized signed packs
- [ ] Consent-gated aggregates
- [ ] Merge via safety

## Deep Technical Notes — Mobile Autocomplete & Spell-Check

### SDK integration guide

App fields register policy (search/chat/password). SDK debounces; calls local engine; optionally assist; renders suggestions; reports opt-in metrics.

### Local model stack

Dictionary + n-gram + optional quantized LM; spell noisy-channel; safety lists; lexicon store encrypted at rest on device.

### Assist service design

Stateless; edge cached prefixes; catalog-aware; deadline; privacy allowlist logging; rate limits per device.

### Pack CI benches

Quality suites per locale; latency p99 on mid-tier device farm; battery trace thresholds; unpack size; signature checks.

### Field policy matrix detail

Explicit matrix in docs: learn/assist/autocorrect/telemetry per field type. Enforce in SDK not only server.

### Failure playbooks

Assist down → local. Pack corrupt → last-good. Storage full → tiny pack. Safety list update → emergency pack push.

### Privacy design review topics

Prefixes leaving device; retention; kids; export; deletion of lexicon backups; consent UX copy.

### Roadmap

Better multilingual; smarter confidence gating; optional federated; tighter Amazon search field catalog packs.

## Interview Cards — Mobile Autocomplete & Spell-Check

### Card 1: Why local-first?

Offline, battery, privacy, RTT jitter—mobile typing cannot require server keystrokes.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: When server assist?

Low local confidence + online + consent + allowed field + budget.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Password fields?

No learn, no assist, no logging—hard invariant.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Pack size budgets?

Tens of MB per language; tiered tiny/base/full; deltas.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Autocorrect aggressiveness?

User setting + undo-rate feedback loop.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: User lexicon role?

Protect names/slang; improve personalization locally without cloud.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Kids Fire tablets?

Stricter lexicon; assist off default; stronger safety.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Code-switching?

Lang-ID; mixed packs; careful corrections.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Catalog brands?

Head on-device dictionary; long-tail assist in search fields.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Telemetry default?

Minimal; opt-in detailed; aggregate with thresholds.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Thermal throttle?

Skip neural; dictionary fallback.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Signed packs?

Yes; verify before activate; last-good fallback.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Relation to retail suggest?

Different surfaces/ownership; shared corpora carefully.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Federated learning?

Advanced opt-in phase; privacy expert review.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Accessibility?

Screen reader announcements; large targets.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Deal-breaker?

Server-mandatory every keystroke; learning from secure fields.

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

## More Interview Q&A — Mobile Autocomplete & Spell-Check

**Q1. Why local-first?**

**A:** Offline, battery, privacy, RTT jitter—mobile typing cannot require server keystrokes.

**Q2. When server assist?**

**A:** Low local confidence + online + consent + allowed field + budget.

**Q3. Password fields?**

**A:** No learn, no assist, no logging—hard invariant.

**Q4. Pack size budgets?**

**A:** Tens of MB per language; tiered tiny/base/full; deltas.

**Q5. Autocorrect aggressiveness?**

**A:** User setting + undo-rate feedback loop.

**Q6. User lexicon role?**

**A:** Protect names/slang; improve personalization locally without cloud.

**Q7. Kids Fire tablets?**

**A:** Stricter lexicon; assist off default; stronger safety.

**Q8. Code-switching?**

**A:** Lang-ID; mixed packs; careful corrections.

**Q9. Catalog brands?**

**A:** Head on-device dictionary; long-tail assist in search fields.

**Q10. Telemetry default?**

**A:** Minimal; opt-in detailed; aggregate with thresholds.

**Q11. Thermal throttle?**

**A:** Skip neural; dictionary fallback.

**Q12. Signed packs?**

**A:** Yes; verify before activate; last-good fallback.

**Q13. Relation to retail suggest?**

**A:** Different surfaces/ownership; shared corpora carefully.

**Q14. Federated learning?**

**A:** Advanced opt-in phase; privacy expert review.

**Q15. Accessibility?**

**A:** Screen reader announcements; large targets.

**Q16. Deal-breaker?**

**A:** Server-mandatory every keystroke; learning from secure fields.

## Deep Technical Addenda — Mobile Autocomplete & Spell-Check

### SDK integration guide

App fields register policy (search/chat/password). SDK debounces; calls local engine; optionally assist; renders suggestions; reports opt-in metrics.

### Local model stack

Dictionary + n-gram + optional quantized LM; spell noisy-channel; safety lists; lexicon store encrypted at rest on device.

### Assist service design

Stateless; edge cached prefixes; catalog-aware; deadline; privacy allowlist logging; rate limits per device.

### Pack CI benches

Quality suites per locale; latency p99 on mid-tier device farm; battery trace thresholds; unpack size; signature checks.

### Field policy matrix detail

Explicit matrix in docs: learn/assist/autocorrect/telemetry per field type. Enforce in SDK not only server.

### Failure playbooks

Assist down → local. Pack corrupt → last-good. Storage full → tiny pack. Safety list update → emergency pack push.

### Privacy design review topics

Prefixes leaving device; retention; kids; export; deletion of lexicon backups; consent UX copy.

### Roadmap

Better multilingual; smarter confidence gating; optional federated; tighter Amazon search field catalog packs.

## Tradeoff Matrices — Mobile Autocomplete & Spell-Check

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

## Operability Addenda — Mobile Autocomplete & Spell-Check

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

## Worked Capacity Narrative — Mobile Autocomplete & Spell-Check

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Mobile Autocomplete & Spell-Check

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Mobile Autocomplete & Spell-Check

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Mobile Autocomplete & Spell-Check
### S1. Local-first manifesto

If offline breaks typing, it’s not a mobile product. Server assist is enhancement.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Secure fields

Password/OTP/payment: no learn, no assist, no logs—hard invariant in SDK.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Confidence gating

Assist only when local confidence low + consent + network + field allows + budget tokens.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Pack pipeline

Train→eval→quantize→sign→CDN→staged rollout; undo/battery guardrails; last-good fallback.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Spell UX

Underline + chip; easy undo; protect lexicon names; don’t ping-pong corrections.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Field policy matrix

search/chat/email/password/address each with learn/assist/autocorrect/telemetry rules.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Kids Fire

Stricter lexicon; assist off default; stronger safety lists.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Battery/thermal

Cap infer ms; skip neural when hot; CI benches on mid-tier devices.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — Mobile Autocomplete & Spell-Check

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Airplane offline | Local packs only | Preserve trust/UX | Postmortem + guardrail |
| Assist timeout | Show local | Preserve trust/UX | Postmortem + guardrail |
| Corrupt pack | Last-good fallback | Preserve trust/UX | Postmortem + guardrail |
| Password field | Disable learn/assist | Preserve trust/UX | Postmortem + guardrail |
| Storage pressure | Tiny pack tier | Preserve trust/UX | Postmortem + guardrail |
| Thermal throttle | Dictionary fallback | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — Mobile Autocomplete & Spell-Check

**RQ1. Why does 'Local-first manifesto' matter in an L6 interview?**

**A:** If offline breaks typing, it’s not a mobile product. Server assist is enhancement. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Local-first manifesto' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Local-first manifesto' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Secure fields' matter in an L6 interview?**

**A:** Password/OTP/payment: no learn, no assist, no logs—hard invariant in SDK. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Secure fields' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Secure fields' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Confidence gating' matter in an L6 interview?**

**A:** Assist only when local confidence low + consent + network + field allows + budget tokens. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Confidence gating' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Confidence gating' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Pack pipeline' matter in an L6 interview?**

**A:** Train→eval→quantize→sign→CDN→staged rollout; undo/battery guardrails; last-good fallback. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Pack pipeline' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Pack pipeline' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Spell UX' matter in an L6 interview?**

**A:** Underline + chip; easy undo; protect lexicon names; don’t ping-pong corrections. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Spell UX' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Spell UX' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Field policy matrix' matter in an L6 interview?**

**A:** search/chat/email/password/address each with learn/assist/autocorrect/telemetry rules. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Field policy matrix' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Field policy matrix' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Kids Fire' matter in an L6 interview?**

**A:** Stricter lexicon; assist off default; stronger safety lists. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Kids Fire' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Kids Fire' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Battery/thermal' matter in an L6 interview?**

**A:** Cap infer ms; skip neural when hot; CI benches on mid-tier devices. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Battery/thermal' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Battery/thermal' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Mobile Autocomplete & Spell-Check

### Walkthrough beat 1

In beat 1, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through Mobile Autocomplete & Spell-Check: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Mobile Autocomplete & Spell-Check

- [ ] Can explain **Local-first manifesto** with numbers and a deal-breaker
- [ ] Can explain **Secure fields** with numbers and a deal-breaker
- [ ] Can explain **Confidence gating** with numbers and a deal-breaker
- [ ] Can explain **Pack pipeline** with numbers and a deal-breaker
- [ ] Can explain **Spell UX** with numbers and a deal-breaker
- [ ] Can explain **Field policy matrix** with numbers and a deal-breaker
- [ ] Can explain **Kids Fire** with numbers and a deal-breaker
- [ ] Can explain **Battery/thermal** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Airplane offline**
- [ ] Has a 30-second runbook for **Assist timeout**
- [ ] Has a 30-second runbook for **Corrupt pack**
- [ ] Has a 30-second runbook for **Password field**
- [ ] Has a 30-second runbook for **Storage pressure**
- [ ] Has a 30-second runbook for **Thermal throttle**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Mobile Autocomplete & Spell-Check to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

*End of document — Mobile Autocomplete & Spell-Check (On-Device + Server Hybrid) (SDE III)*
