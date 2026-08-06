# System Design: Alexa Triggering / Advertising Workflow (Voice → Intent → Ad → Measurement)

> **Focus areas:** Voice trigger · ASR/NLU · Intent · Ad decisioning · Privacy · Consent · Measurement · Brand safety
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Separate speech vs ads planes; privacy non-negotiables; deal-breaker: raw audio to advertisers
> **Interview theme:** Amazon SDE III / L6 — **Alexa / Advertising** privacy-first voice ad workflow

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

Goal: Alexa-triggering advertising workflow: wake→ASR→NLU→eligibility→decision→render→measure under privacy/consent/brand-safety.

### 1.0 What this is / is not
| Dimension | This | Not |
|-----------|------|-----|
| Job | Orchestrate voice→ad→measure | Train ASR from scratch |
| Privacy | Minimization; purpose limit | Raw audio to advertisers |
| Success | Consented, brand-safe, measurable | Max ads regardless of trust |

### 1.1 Functional requirements
Cover triggers, ASR/NLU, eligibility, ad types, decisioning, consent, measurement, kids, latency, brand safety, frequency caps, content fallback, aggregated reporting, experiments, locales.

**MVP:** voice→decide→render→measure with consent/kids/safety and content-only degrade.
**Out of MVP:** raw transcript sales; cross-home identity without consent.

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
Speech (ASR/NLU), Consent/Policy, Ads Decisioning, Render, Measurement — fail independently.

### 2.2 Latency
NLU 20–40ms; consent 5–15; decision 20–40; merge 5 → **ads additive p99 ≤ 50–100ms**. Hard deadline; content must not wait.

### 2.3 Privacy
No raw audio to advertisers. Allowlisted redacted features only. Aggregated reporting with k-thresholds.

## 3. High-Level Design

### 3.1 Workflow
Trigger → ASR → NLU → Consent/Kids/Sensitive gates → Eligibility → Decisioning → Response planner → TTS → privacy-preserving measurement.

### 3.2 Internal API
`POST /ads/decide` with redacted features → creative_ref?, disclosure, decision_id, policy_version.

### 3.3 Tradeoffs
Content > ads on failure; kids/consent fail closed; never raw audio/transcripts to advertisers; trailing ads preferred.

## 4. Architecture Diagram

```text
Device --> Speech Gateway --> ASR --> NLU --> Dialog
                                              |
                                              v
                                    Privacy/Consent Gate
                                              |
                         ineligible --> Content-only Response
                         eligible --> Policy --> Ads Decisioning --> Planner --> TTS
                                              |
                                              v
                                       Measurement (aggregates)
```

Privacy boundary: audio stays in Speech; ads see redacted features; advertisers see aggregates only.

## 5. Design Deep Dive

### 5.1 Invariants
No raw audio to ads; consent/kids non-bypassable; content succeeds if ads fail; audit decision_id+policy_version; sensitive intents suppress ads.

### 5.2 Decisioning
Retrieve → filter → score → auction/curate → disclosure → creative with deadline.

### 5.3 Measurement
Signed play events; dedupe; fraud filters; delayed k-threshold aggregates.

### 5.4 Progressive scale
10× eligibility cache/prefetch; 100× regional cells; 1,000× on-device eligibility.

### 5.5 Ownership
Speech vs Ads vs Privacy with versioned redacted feature schema.

## 6. Wrap-Up

### 6.1 What we designed
Privacy-first voice ads: trigger→ASR/NLU→consent/policy→decisioning→render→aggregated measurement; content wins if ads fail.

### 6.2 Key decisions worth defending
1. No raw audio to advertisers
2. Consent/kids/sensitive fail closed
3. Ads additive latency + content fallback
4. Aggregated measurement
5. Speech vs Ads vs Privacy ownership

### 6.3 Risks & follow-ups
- Regulatory packs
- Household identity
- Prefetch vs privacy
- Brand safety in news

### 6.4 Closer
> **Alexa Triggering / Advertising Workflow**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Alexa Advertising Workflow

**Q1. What exactly is redacted before ads?**

**A:** Allowlist feature schema: intent category, locale, device class, consented segments, content contextual category. Not audio, not full transcript, not sensitive slots.

**Q2. How do you handle shared households?**

**A:** Household token default; optional recognized voice profile with consent; kids profiles force fail-closed personalization.

**Q3. Can we personalize on health intents?**

**A:** No—sensitive intent taxonomy suppresses ads. Fail closed.

**Q4. What if disclosure TTS fails?**

**A:** Do not play ad creative without disclosure directive success. Skip ad.

**Q5. How fast can we kill a bad creative?**

**A:** Creative kill-list pushed to decisioning + edge CDN purge; decision TTL short.

**Q6. Is auction mandatory?**

**A:** No. Curated sponsorships share eligibility+disclosure+measurement. Auction is one strategy behind Decisioning.

**Q7. How do we prevent ads delaying weather?**

**A:** Hard deadline; trailing-only slots for many intents; content TTS can start while optional trailing ad still finalizing only if pipeline allows cancel.

**Q8. What is the reporting delay for?**

**A:** Reduce linkage risk and allow fraud filters; advertisers get aggregates not real-time user paths.

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
- [ ] No raw audio to advertisers
- [ ] Consent/kids/sensitive fail closed
- [ ] Ads additive latency + content fallback
- [ ] Aggregated measurement
- [ ] Speech vs Ads vs Privacy ownership

## Deep Technical Notes — Alexa Advertising Workflow

### Speech↔Ads contract

Versioned protobuf/JSON: request_id, intent_category, redacted_features, consent_flags, locale, deadline_ms. Response: decision_id, creative_ref?, disclosure_id, policy_version, cache_ttl.

Compatibility tests in CI; privacy allowlist diff review required on schema changes.

### Eligibility state machine

States: not_evaluated → ineligible(reason) | eligible → decided(no_fill|fill) → rendered|skipped. Reasons logged for analytics without PII payloads.

### Brand safety operations

Lists: global banned categories, advertiser exclusions, breaking-news suppressions. Nearline updater + emergency push. Decisioning should fail closed on safety service timeout for high-risk categories.

### Creative rendering

Audio ads: CDN fetch + loudness. TTS ads: template + SSML. Skill suggestions: directive with deep link. Always attach disclosure metadata for UX layer.

### Privacy incident response

Kill personalized ads globally; freeze feature logs; preserve audit; notify privacy oncall; customer messaging as required; postmortem with data-flow diagram.

### Capacity & cost

Decision QPS follows eligible intents not all utterances. Cache contextual non-personalized decisions for popular intents. Distill bidding models. Track $/eligible-decision.

### Fraud & invalid traffic

Bot devices, replayed events, incentivized listen farms—attestation, velocity, anomaly, campaign-level caps.

### Roadmap

On-device eligibility caches; privacy-preserving measurement; tighter retail voice shopping packaging; still never weaken raw-audio boundary.

## Interview Cards — Alexa Advertising Workflow

### Card 1: What exactly is redacted before ads?

Allowlist feature schema: intent category, locale, device class, consented segments, content contextual category. Not audio, not full transcript, not sensitive slots.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: How do you handle shared households?

Household token default; optional recognized voice profile with consent; kids profiles force fail-closed personalization.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Can we personalize on health intents?

No—sensitive intent taxonomy suppresses ads. Fail closed.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: What if disclosure TTS fails?

Do not play ad creative without disclosure directive success. Skip ad.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: How fast can we kill a bad creative?

Creative kill-list pushed to decisioning + edge CDN purge; decision TTL short.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Is auction mandatory?

No. Curated sponsorships share eligibility+disclosure+measurement. Auction is one strategy behind Decisioning.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: How do we prevent ads delaying weather?

Hard deadline; trailing-only slots for many intents; content TTS can start while optional trailing ad still finalizing only if pipeline allows cancel.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: What is the reporting delay for?

Reduce linkage risk and allow fraud filters; advertisers get aggregates not real-time user paths.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: How do experiments interact with legal disclosures?

Disclosures are non-negotiable; experiments cannot remove them. Hold out ads load; measure opt-out and barge-in.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Device offline?

No cloud ads; local content skills only; no deferred personalized ad targeting from buffered audio.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: How do frequency caps fail open/closed?

If cap store down, prefer skip personalized ads (under-cap bias) rather than over-expose.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Skill sponsored suggestion vs audio ad?

Different creative types, same eligibility gate and disclosure requirements.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Data residency in EU?

Regional cells; consent packs; shorter ads feature retention; DPA considerations—mention packs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: SSRF or skill spoofing measurement?

Auth measurement events; attestation; reject unsigned completes.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: How is this different from Fire TV ads?

Related ads platform ideas, different modality/UX interruptions; don’t assume identical policy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Deal-breaker?

Raw audio/transcripts to advertisers, or failing user answers when ads are down.

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

## More Interview Q&A — Alexa Advertising Workflow

**Q1. What exactly is redacted before ads?**

**A:** Allowlist feature schema: intent category, locale, device class, consented segments, content contextual category. Not audio, not full transcript, not sensitive slots.

**Q2. How do you handle shared households?**

**A:** Household token default; optional recognized voice profile with consent; kids profiles force fail-closed personalization.

**Q3. Can we personalize on health intents?**

**A:** No—sensitive intent taxonomy suppresses ads. Fail closed.

**Q4. What if disclosure TTS fails?**

**A:** Do not play ad creative without disclosure directive success. Skip ad.

**Q5. How fast can we kill a bad creative?**

**A:** Creative kill-list pushed to decisioning + edge CDN purge; decision TTL short.

**Q6. Is auction mandatory?**

**A:** No. Curated sponsorships share eligibility+disclosure+measurement. Auction is one strategy behind Decisioning.

**Q7. How do we prevent ads delaying weather?**

**A:** Hard deadline; trailing-only slots for many intents; content TTS can start while optional trailing ad still finalizing only if pipeline allows cancel.

**Q8. What is the reporting delay for?**

**A:** Reduce linkage risk and allow fraud filters; advertisers get aggregates not real-time user paths.

**Q9. How do experiments interact with legal disclosures?**

**A:** Disclosures are non-negotiable; experiments cannot remove them. Hold out ads load; measure opt-out and barge-in.

**Q10. Device offline?**

**A:** No cloud ads; local content skills only; no deferred personalized ad targeting from buffered audio.

**Q11. How do frequency caps fail open/closed?**

**A:** If cap store down, prefer skip personalized ads (under-cap bias) rather than over-expose.

**Q12. Skill sponsored suggestion vs audio ad?**

**A:** Different creative types, same eligibility gate and disclosure requirements.

**Q13. Data residency in EU?**

**A:** Regional cells; consent packs; shorter ads feature retention; DPA considerations—mention packs.

**Q14. SSRF or skill spoofing measurement?**

**A:** Auth measurement events; attestation; reject unsigned completes.

**Q15. How is this different from Fire TV ads?**

**A:** Related ads platform ideas, different modality/UX interruptions; don’t assume identical policy.

**Q16. Deal-breaker?**

**A:** Raw audio/transcripts to advertisers, or failing user answers when ads are down.

## Deep Technical Addenda — Alexa Advertising Workflow

### Speech↔Ads contract

Versioned protobuf/JSON: request_id, intent_category, redacted_features, consent_flags, locale, deadline_ms. Response: decision_id, creative_ref?, disclosure_id, policy_version, cache_ttl.

Compatibility tests in CI; privacy allowlist diff review required on schema changes.

### Eligibility state machine

States: not_evaluated → ineligible(reason) | eligible → decided(no_fill|fill) → rendered|skipped. Reasons logged for analytics without PII payloads.

### Brand safety operations

Lists: global banned categories, advertiser exclusions, breaking-news suppressions. Nearline updater + emergency push. Decisioning should fail closed on safety service timeout for high-risk categories.

### Creative rendering

Audio ads: CDN fetch + loudness. TTS ads: template + SSML. Skill suggestions: directive with deep link. Always attach disclosure metadata for UX layer.

### Privacy incident response

Kill personalized ads globally; freeze feature logs; preserve audit; notify privacy oncall; customer messaging as required; postmortem with data-flow diagram.

### Capacity & cost

Decision QPS follows eligible intents not all utterances. Cache contextual non-personalized decisions for popular intents. Distill bidding models. Track $/eligible-decision.

### Fraud & invalid traffic

Bot devices, replayed events, incentivized listen farms—attestation, velocity, anomaly, campaign-level caps.

### Roadmap

On-device eligibility caches; privacy-preserving measurement; tighter retail voice shopping packaging; still never weaken raw-audio boundary.

## Tradeoff Matrices — Alexa Advertising Workflow

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

## Operability Addenda — Alexa Advertising Workflow

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

## Worked Capacity Narrative — Alexa Advertising Workflow

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Alexa Advertising Workflow

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Alexa Advertising Workflow

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Alexa Advertising Workflow
### S1. Hard privacy boundary

Audio for speech understanding only. Ads get allowlisted redacted features. Reports get aggregates. Raw audio/transcripts to advertisers is an instant fail.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Content > ads

Ads timeouts never fail weather/timers/critical answers. Trailing slots preferred. Disclosure required before creative play.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Consent & kids

Consent service and kids profiles fail closed for personalized ads. Cap store outage biases to under-exposure.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Eligibility engine

Intent category, locale pack, frequency, brand safety, experiments → eligible bool + reason codes.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Decisioning

Retrieve→filter→score→auction/curate→disclosure→creative ref with deadline from dialog manager.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Measurement integrity

Signed events, dedupe, bots, k-thresholds, delayed aggregates, no transcript attachments.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Brand safety ops

Global lists, advertiser exclusions, breaking-news kill switches, fail closed on safety timeout for high-risk.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Regional residency

Decision cells and policy packs by country; shorter ads feature retention where required.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — Alexa Advertising Workflow

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Ads down | Content-only mode | Preserve trust/UX | Postmortem + guardrail |
| Privacy complaint | Kill personalized ads; audit | Preserve trust/UX | Postmortem + guardrail |
| Kids mistag | Treat as kids; fix labeling | Preserve trust/UX | Postmortem + guardrail |
| Fraud completes | Attestation + anomaly | Preserve trust/UX | Postmortem + guardrail |
| Breaking news | Category suppress push | Preserve trust/UX | Postmortem + guardrail |
| Consent store down | Fail closed personalized | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — Alexa Advertising Workflow

**RQ1. Why does 'Hard privacy boundary' matter in an L6 interview?**

**A:** Audio for speech understanding only. Ads get allowlisted redacted features. Reports get aggregates. Raw audio/transcripts to advertisers is an instant fail. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Hard privacy boundary' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Hard privacy boundary' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Content > ads' matter in an L6 interview?**

**A:** Ads timeouts never fail weather/timers/critical answers. Trailing slots preferred. Disclosure required before creative play. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Content > ads' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Content > ads' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Consent & kids' matter in an L6 interview?**

**A:** Consent service and kids profiles fail closed for personalized ads. Cap store outage biases to under-exposure. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Consent & kids' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Consent & kids' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Eligibility engine' matter in an L6 interview?**

**A:** Intent category, locale pack, frequency, brand safety, experiments → eligible bool + reason codes. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Eligibility engine' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Eligibility engine' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Decisioning' matter in an L6 interview?**

**A:** Retrieve→filter→score→auction/curate→disclosure→creative ref with deadline from dialog manager. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Decisioning' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Decisioning' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Measurement integrity' matter in an L6 interview?**

**A:** Signed events, dedupe, bots, k-thresholds, delayed aggregates, no transcript attachments. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Measurement integrity' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Measurement integrity' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Brand safety ops' matter in an L6 interview?**

**A:** Global lists, advertiser exclusions, breaking-news kill switches, fail closed on safety timeout for high-risk. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Brand safety ops' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Brand safety ops' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Regional residency' matter in an L6 interview?**

**A:** Decision cells and policy packs by country; shorter ads feature retention where required. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Regional residency' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Regional residency' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Alexa Advertising Workflow

### Walkthrough beat 1

In beat 1, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through Alexa Advertising Workflow: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Alexa Advertising Workflow

- [ ] Can explain **Hard privacy boundary** with numbers and a deal-breaker
- [ ] Can explain **Content > ads** with numbers and a deal-breaker
- [ ] Can explain **Consent & kids** with numbers and a deal-breaker
- [ ] Can explain **Eligibility engine** with numbers and a deal-breaker
- [ ] Can explain **Decisioning** with numbers and a deal-breaker
- [ ] Can explain **Measurement integrity** with numbers and a deal-breaker
- [ ] Can explain **Brand safety ops** with numbers and a deal-breaker
- [ ] Can explain **Regional residency** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Ads down**
- [ ] Has a 30-second runbook for **Privacy complaint**
- [ ] Has a 30-second runbook for **Kids mistag**
- [ ] Has a 30-second runbook for **Fraud completes**
- [ ] Has a 30-second runbook for **Breaking news**
- [ ] Has a 30-second runbook for **Consent store down**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Alexa Advertising Workflow to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

*End of document — Alexa Triggering / Advertising Workflow (Voice → Intent → Ad → Measurement) (SDE III)*
