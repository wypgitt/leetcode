# System Design: Alexa Triggering / Advertising Workflow (Voice → Intent → Ad Decisioning → Measurement)

> **Focus areas:** Voice trigger · ASR/NLU · Intent routing · Ad decisioning · Privacy · Consent · Measurement · Brand safety · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Separate voice plane from ads plane, privacy non-negotiables, deal-breakers for “send raw audio to advertisers”
> **Interview theme:** Amazon SDE III / L6 — **Alexa / Advertising** workflow ownership—privacy-first voice ad experiences with measurable outcomes and clear trust constraints

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

Goal: design the **Alexa-triggering advertising workflow**: wake/trigger → ASR → NLU/intent → eligibility → ad decisioning → TTS/response rendering → impression/outcome measurement—under strict **privacy, consent, and brand-safety** constraints.

### 1.0 What this is / is not

| Dimension | **This doc** | Not this |
|-----------|--------------|----------|
| Job | Orchestrate voice→ad decision→measure | Train foundation ASR models from scratch |
| Ads | Alexa media / sponsored skills / shopping hints | Programmatic web display ads full stack |
| Privacy | On-device/edge minimization; purpose limitation | Raw audio sharing with advertisers |
| Success | Relevant, consented, brand-safe, measurable | Max ads regardless of trust |

### 1.1 Functional Requirements

| # | Question | Answer | Implication |
|---|----------|--------|-------------|
| F1 | Triggers? | Wake word, push-to-talk, routine, skill invoke | Trigger metadata |
| F2 | Understanding? | ASR text + NLU intent/slots | Intent graph |
| F3 | When ads? | Eligible intents / content slots only | Policy engine |
| F4 | Ad types? | Audio ads, sponsored skill suggestion, shopping recommendation | Creative renderer |
| F5 | Decisioning? | Auction / curated + relevance | Ads decision service |
| F6 | Consent? | Household/user privacy settings | Consent service hard gate |
| F7 | Measurement? | Played, completed, opt-out, conversion hooks | Privacy-preserving events |
| F8 | Kids profiles? | Strict no personalized ads mode | Policy packs |
| F9 | Latency? | Keep conversational | Budget ASR∥ads prefetch |
| F10 | Brand safety? | Category blocks, keyword, contextual | Safety filters |
| F11 | Frequency cap? | Household/device caps | Cap store |
| F12 | Fallback? | Content without ad | Never block answer for ad fail |
| F13 | Advertiser reporting? | Aggregated | No user-level raw audio |
| F14 | A/B? | Experiment framework | Layer experiments |
| F15 | Multi-locale? | Yes | Locale policy packs |

**MVP:** trigger→ASR/NLU→eligibility→decision→render audio/suggestion→measure play/complete; consent+kids gates; frequency caps; brand safety; degrade to no-ad.

**Out of MVP:** selling raw transcripts to third parties; on-device full auction; cross-home identity graphs without consent.

### 1.2 NFRs

| # | Target |
|---|--------|
| N1 End-to-end response | Conversational; ads path p99 add ≤ 50–100ms beyond content |
| N2 Privacy | Purpose limitation; minimization; retention TTLs |
| N3 Availability | Ads failure never fails user answer |
| N4 Measurement integrity | Fraud-resistant aggregated reporting |
| N5 Kids / sensitive | Fail closed |
| N6 Audit | Policy version on each decision |

### 1.3 Cases

Happy: “play weather” → content + eligible trailing brand audio; shopping intent → sponsored product with disclosure; opt-out → no personalized ads.

| Case | Behavior |
|------|----------|
| Consent off | No personalized ads |
| Kids profile | No personalized ads; limited/none per policy |
| ASR low confidence | Skip ads; clarify |
| Ads timeout | Serve content only |
| Sensitive intent (medical/finance) | Suppress ads |
| Frequency exceeded | Skip |
| Household multi-user | Speaker recognition optional; default household policy |

### 1.4 Scales

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Voice requests/s | 100K | 1M | 10M | 100M |
| Ad-eligible/s | 20K | 200K | 2M | 20M |
| Decision QPS | 20K | 200K | 2M | cells |
| Measurement events/s | 50K | 500K | 5M | aggregated edge |

### 1.5 Constraints

- **Never** send raw audio to advertisers.
- Ads are a guest in the voice loop—content reliability first.
- Privacy legal packs differ by country.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Planes

| Plane | What |
|-------|------|
| Voice understanding | ASR/NLU |
| Policy / consent | Eligibility |
| Ads decision | Auction/retrieval |
| Render | TTS / skill directive |
| Measurement | Events → aggregate |

### 2.2 Latency budget

| Step | Budget |
|------|--------|
| Trigger + streaming ASR partial | overlapping |
| NLU intent | 20–40 ms |
| Consent + policy | 5–15 ms |
| Ad decision | 20–40 ms |
| Merge into response plan | 5 ms |
| **Ads additive p99** | **≤ 50–100 ms** |

Prefetch ads on speculative intents when safe.

### 2.3 Privacy math

Prefer on-device wake; cloud ASR with retention limits; measurement as counts with differential privacy noise for small cells.

---

## 3. High-Level Design

### 3.1 Components

| Component | Role |
|-----------|------|
| Device / Wake | Trigger, capture policy |
| Speech Plane | ASR, NLU, dialog |
| Privacy & Consent Service | Gates |
| Eligibility / Policy Engine | Intent allowlists, sensitive categories |
| Ads Decisioning | Retrieve + score + auction |
| Creative / TTS Renderer | Directives |
| Frequency Cap Store | Household caps |
| Measurement Pipeline | Play/complete/convert (aggregated) |
| Advertiser Reporting | Aggregates only |
| Experimentation | Layers |
| Audit Log | decision_id, policy_version |

### 3.2 Workflow

```text
Trigger → ASR → NLU intent
  → Consent/Policy eligibility
  → if eligible: Decisioning (retrieve → rank → auction → brand safety)
  → Response planner merges content + optional ad directive
  → Render (TTS/audio)
  → Measurement events (privacy-preserving)
```

### 3.3 API (internal)

```text
POST /ads/decide
  { request_id, intent, slots_redacted, locale, household_token, consent_flags }
→ { ad_creative_ref?, disclosure, bid_meta, decision_id, ttl }
```

Note: **redacted slots**—no unnecessary PII.

### 3.4 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Audio to advertisers | **Never** | Raw audio sharing |
| Ads vs content | Content wins on timeout | Block answer for ads |
| Identity | Household token + consent | Silent cross-home graph |
| Measurement | Aggregated + fraud checks | User-level transcript feeds |
| Kids | Fail closed | Personalized kids ads |

---

## 4. Architecture Diagram

```text
Device Wake/PTT --> Speech Gateway --> ASR --> NLU --> Dialog Manager
                                                      |
                                                      v
                                            Privacy/Consent Gate
                                                      |
                                      eligible? no --> Content-only Response
                                      yes
                                                      v
                                            Policy/Eligibility
                                                      v
                                            Ads Decisioning
                                         (retrieve/rank/auction/safety)
                                                      v
                                            Response Planner -----> TTS/Directives
                                                      |
                                                      v
                                              Measurement (agg)
```

### 4.2 Privacy boundary

```text
[Device audio] -> Speech Plane (purpose: understand)
        \-> NOT to Advertisers
[Redacted intent features] -> Ads Decisioning
[Aggregates] -> Advertiser Reporting
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Ads never receive raw audio.
2. Consent/kids gates non-bypassable.
3. Content response succeeds if ads fail.
4. Every ad decision has decision_id + policy_version.
5. Sensitive intents suppress ads.

### 5.2 Decisioning internals

Retrieve campaigns by locale/intent category → filter consent/brand safety/frequency → score relevance → auction → choose creative → return directive.

### 5.3 Measurement & fraud

Client/device play signals signed; dedupe; bot detection; report aggregates with thresholds; delay reports to reduce linkage.

### 5.4 Progressive scale

10×: cache eligibility; speculative prefetch. 100×: regional decision cells. 1,000×: on-device eligibility + edge decision tokens.

### 5.5 Ownership

Speech owns ASR/NLU SLOs; Ads owns decision/measurement; Privacy owns policy packs; shared contract on redacted feature schema.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        A privacy-first **voice advertising workflow**: trigger→ASR/NLU→consent/policy eligibility→ads decisioning→render→aggregated measurement, with content always winning on ads failure.

        ### 6.2 Key decisions worth defending

        1. Hard privacy boundary (no raw audio to advertisers)
2. Consent/kids/sensitive-intent fail closed
3. Ads additive latency budget + content fallback
4. Aggregated measurement + fraud controls
5. Clear ownership split Speech vs Ads vs Privacy

        ### 6.3 Risks & follow-ups

        - Regulatory pack complexity
- Household identity edge cases
- Speculative prefetch vs privacy
- Brand safety in breaking news

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **Alexa Triggering / Advertising Workflow** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---

## 7. Deeper / Related Interview Questions

**Q1. Why separate speech and ads planes?**

**A:** Different trust boundaries, SLOs, and failure modes. Speech outage is existential; ads must be optional. Privacy minimization requires a hard boundary.

**Q2. Can advertisers target by transcript keywords?**

**A:** Only via redacted, policy-approved features/categories—not raw transcripts dumps. Prefer contextual intent categories.

**Q3. How do frequency caps work across devices in a home?**

**A:** Household graph with consent; caps store keyed by household_token; eventual consistency OK if slightly under-cap.

**Q4. Kids mode?**

**A:** Fail closed on personalized ads; follow marketplace/legal packs; separate profile flag from NLU.

**Q5. Ads timeout strategy?**

**A:** Hard deadline; return content-only; measure ads_timeout_rate.

**Q6. How is this different from retail sponsored products?**

**A:** Modality (audio), disclosure UX, privacy sensitivity of microphones, household identity, and conversational interruption costs.

**Q7. Measurement without stalking?**

**A:** Aggregates, cohort thresholds, limited retention, no raw audio, fraud filters, optional on-device contribution.

**Q8. Deal-breaker?**

**A:** Sending raw audio or full transcripts to advertisers, or failing user answers when ads are down.

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

        ### Appendix F — Event schema (privacy-preserving)

```text
AdDecision { decision_id, request_id, eligible, campaign_id?, policy_version, ts }
AdMeasure  { decision_id, event: played|complete|skip|error, ts }  # no transcript
```

### Appendix G — Runbooks

**Ads p99 high:** serve content-only; scale decision cells; disable heavy models.
**Privacy incident:** kill personalized ads globally; invalidate feature caches; notify privacy oncall.

### Appendix H — Closer checklist

- [ ] Privacy boundary explicit
- [ ] Content > ads on failure
- [ ] Consent/kids fail closed
- [ ] Measurement aggregated
- [ ] Latency budget
- [ ] Progressive scale



## Extended Notes — Alexa Advertising Workflow

### E1. Disclosure UX

Voice disclosure must be clear (“from a sponsor”) without wrecking UX. Product + legal co-own copy; system carries disclosure flags mandatorily.

### E2. Speculative prefetch

When partial ASR suggests high probability of eligible intent, prefetch ads decision with cancel-on-miss to hide latency—only if privacy policy allows speculative processing.

### E3. Brand safety lists

Global + advertiser exclusions + contextual blocks (news tragedies, etc.). Nearline update kill-lists.

### E4. Skill sponsored suggestions

Different creative type; still through eligibility + disclosure; don’t hijack user-requested skill without policy.

### E5. Shopping through Alexa

Sponsored product cards/voice offers need retail catalog join; reuse retail ads relevance with voice features.

### E6. Data retention

ASR retention vs ads feature retention differ; document TTLs; advertising features store less.

### E7. Multi-locale policy

EU consent differs from US; pack engine selects rules by country.

### E8. Experimentation ethics

Holdouts for ads load; never experiment away legally required disclosures.

### E9. Security

Decision API auth between speech and ads; prevent skill spoofing measurement events.

### E10. Cost

Decision QPS × model cost; cache non-personalized contextual ads for popular intents.

### E11. Outage storytelling

L6 answer: ads down → conversation continues; speech down → device local errors; measurement lag OK.

### E12. Identity

Prefer household tokens over advertising IDs familiar from mobile; microphone context is more sensitive.

### E13. Audio creative supply

Transcoded TTS vs pre-recorded; loudness norms; cache creatives at edge CDN.

### E14. Human review

Ads creatives reviewed offline; runtime still enforces brand safety.

### E15. Related systems

Alexa Speech, Privacy Hub, DSP/advertiser portal, Retail Catalog, Experimentation platform.

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


## 16. Additional Deep Q&A — Alexa Advertising Workflow

### Q1. What features can ads decisioning legally use?

Redacted intent categories, locale, device class, consent-approved segments, content contextual category—not raw audio, not unrestricted transcripts, not sensitive slot values (e.g., health details).

### Q2. How do you prefetch safely?

Only when policy allows speculative processing; cancel unused decisions; do not persist speculative audio-derived features beyond request TTL.

### Q3. Household vs personal targeting?

Default household; personal only with voice profile + consent. Kids profiles force closed personalized ads.

### Q4. Brand safety near breaking news?

Nearline kill-switch on contextual categories; advertiser exclusions; human ops bridge for major events.

### Q5. How do advertisers get reports without user paths?

Aggregated campaign metrics with k-thresholds; delayed batch; fraud-filtered; no transcript attachments.

### Q6. Auction vs curated?

Some Alexa surfaces curated; some auction. Architecture supports both behind Decisioning with a common eligibility layer.

### Q7. What if NLU intent flips after prefetch?

Bind decision to intent_id/version; discard prefetch on mismatch; never play mismatched ad.

### Q8. Latency hiding with TTS?

Start content TTS while ads decision finalizes only if ad is trailing; never delay critical answers for optional trailing ads.

### Q9. Cross-device frequency caps consistency?

Eventual consistency acceptable; prefer under-cap. Cap store keyed by household_token with short sync intervals.

### Q10. How to A/B ads load without harming trust?

Holdouts; guardrail on opt-out rate, barge-in, customer contacts; never remove legally required disclosures in variants.

## 17. Scenario Drills — Alexa Ads

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Ads service down | Content-only mode | Ads are optional guests |
| Privacy complaint | Kill personalized ads; audit | Fail closed |
| Kids profile mis-tagged | Treat as kids; fix labeling | Safety > revenue |
| Fraudulent play events | Signature + dedupe + anomaly | Measurement integrity |

## 18. Final Checklist — Alexa Ads

- [ ] No raw audio to advertisers
- [ ] Consent/kids/sensitive fail closed
- [ ] Content path independent of ads
- [ ] decision_id + policy_version audit
- [ ] Aggregated measurement
- [ ] Latency budget additive
- [ ] Locale policy packs
- [ ] Ownership Speech vs Ads vs Privacy

## 19. Expanded Design Notes — Alexa Ads

### 19.1 End-to-end sequence detail

Device streams audio to Speech Gateway after wake validation. ASR produces partials; NLU emits intent hypotheses. Dialog Manager decides if an ad slot exists (trailing audio, skill suggestion, shopping). Eligibility checks consent, profile type, intent sensitivity, frequency. Decisioning returns creative refs and disclosure. Renderer mixes directives. Measurement records play/complete without transcript payload.

### 19.2 Slot redaction

Slots like `medicine_name` or `account_number` never flow to ads. A redaction map is owned by Privacy and versioned. Ads feature schema is allowlist-based, not denylist-based.

### 19.3 Creative supply chain

Advertisers upload audio/TTS scripts; offline review; transcode; loudness normalize; store on CDN; runtime fetches by creative_id. Runtime still enforces brand safety and exclusions.

### 19.4 Shopping ads

Join retail catalog for product offers; reuse retail relevance models with voice-specific features (utterance category). Disclosure differs from web sponsored products but principles match: labeled, relevant, organic floor where applicable.

### 19.5 Internationalization

Policy packs per country; consent strings; banned categories; language of disclosure. Decision cells regional to keep latency and data residency.

### 19.6 Fraud

Fake devices / replayed measurement: sign events with device attestation where possible; rate limit; anomaly on completion without play; campaign-level velocity checks.

### 19.7 Operability

Kill switches: disable personalized ads, disable all ads, disable specific advertiser, disable speculative prefetch. Each switch tested in game days.

### 19.8 Evolution

On-device eligibility caches; edge decision tokens; stronger on-device privacy preserving measurement contributions.

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

*End of document — Alexa Triggering / Advertising Workflow (SDE III)*
