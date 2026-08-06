# System Design: Mobile Autocomplete & Spell-Check (On-Device + Server Hybrid)

> **Focus areas:** On-device LM · Server long-tail · Spell correction · Typing privacy · Sync dictionaries · Latency · Battery · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split on-device vs server planes, privacy constraints, deal-breakers for “every keystroke must hit server”
> **Interview theme:** Amazon SDE III / L6 — **Amazon mobile / keyboard / app search entry** hybrid autocomplete & spell-check—privacy, battery, and offline UX with server intelligence

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

Goal: design **mobile autocomplete and spell-check** that works **on-device** for latency/offline/privacy and uses **server** for long-tail / personalization / catalog-aware corrections—hybrid.

### 1.0 What this is / is not

| Dimension | **This doc** | Not this |
|-----------|--------------|----------|
| Job | Next-word / phrase suggest + spell fix while typing | Full cloud SERP |
| Location | On-device first, server assist | Server-mandatory keystroke |
| Privacy | Minimize raw keystroke exfiltration | Log all keystrokes forever |
| Amazon lens | App search bars, Fire devices, keyboard IME | Desktop IDE autocomplete |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Suggest? | Words/phrases as user types | Local LM + dict |
| F2 | Spell-check? | Underline + corrections | Confusion sets |
| F3 | Offline? | Core works offline | On-device models |
| F4 | Server? | Long-tail / catalog terms | Hybrid API |
| F5 | Personalization? | User lexicon (local) | On-device store |
| F6 | Languages? | Multi + code-switch | Language pack |
| F7 | Privacy? | Opt-in server learn | Consent |
| F8 | Battery? | Strict CPU budget | Quantized models |
| F9 | Latency? | <16–30ms local | Soft realtime |
| F10 | Catalog names? | ASIN/brand terms | Server/catalog packs |
| F11 | Safety? | Block abusive suggestions | Filters |
| F12 | Sync? | Dictionary packs | Delta updates |
| F13 | Autocorrect aggressiveness? | User setting | Modes |
| F14 | Analytics? | Aggregated opt-in | Privacy pipeline |
| F15 | A/B? | Pack experiments | Layered |

**MVP:** on-device dictionary+LM autocomplete; spell corrections; optional server assist when online/consented; language packs; safety; battery budgets.

### 1.2 NFRs

| # | Target |
|---|--------|
| Local suggest | ≤ 16–30ms |
| Server assist | ≤ 100–150ms when used |
| Offline | Core quality OK |
| Model size | Tens of MB per language pack |
| Privacy | No raw keystroke stream by default |
| Battery | Negligible vs typing session |

### 1.3 Cases

Happy: offline typing suggestions; misspelling “recieve” → receive; catalog brand “firetvstick” corrected; opted-in server improves rare terms.

| Case | Behavior |
|------|----------|
| No network | Local only |
| Consent off | No server personalization learn |
| Code switching EN/ES | Lang-ID + mixed packs |
| Password fields | Disable learning / suggest |
| Kids | Stricter packs |
| Low storage | Smaller packs |

### 1.4 Scales

| Metric | Base | 10× | 100× |
|--------|------|-----|------|
| Devices | 100M | 1B | — |
| Server assist QPS | 200K | 2M | 20M |
| Pack updates | weekly | — | staged |
| Languages | 20 | 40 | 100 |

---

## 2. Back-of-the-Envelope Estimation

On-device: 50MB pack × 100M devices = distribution challenge—delta updates, compression, CDN.

Server assist only on uncertain local predictions → e.g. 10% of keystrokes → QPS manageable.

Battery: limit neural infer to N ms / keystroke; fallback to n-gram.

---

## 3. High-Level Design

### 3.1 Components

| Component | Where | Role |
|-----------|-------|------|
| Keyboard/IME / Search field SDK | Device | UI |
| On-device LM + Dictionary | Device | Suggest/spell |
| User Lexicon | Device | Learned words |
| Safety Filter | Device | Blocks |
| Pack Manager | Device | Downloads |
| Assist API | Server | Long-tail / catalog |
| Pack Builder | Server | Offline train |
| Privacy Aggregate | Server | Opt-in stats |
| Experiment | Both | Flags |

### 3.2 Hybrid decision

```text
on each keystroke:
  local_candidates = device_model()
  if confidence high or offline or no consent:
     return local
  else:
     server_candidates = assist_api(prefix_redacted, locale, context_type)
     merge(local, server) → safety → show
```

### 3.3 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Every keystroke server | **Hybrid / local-first** | Server-mandatory |
| Learn passwords | **Never** | Learn from secure fields |
| Model size | Quantized tens of MB | 1GB LM on phone |
| Privacy | Opt-in aggregates | Raw keystroke warehouse default |

---

## 4. Architecture Diagram

```text
+---------------- DEVICE ------------------+
| Field SDK --> Local LM/Dict --> Safety   |
|    |              ^                      |
|    |         User Lexicon                |
|    |         Pack Manager <--- CDN packs |
|    v                                     |
| optional Assist client                   |
+------------------+-----------------------+
                   | consented + uncertain
                   v
            +------ Server Assist ------+
            | Catalog/long-tail index   |
            | Privacy-preserving logs   |
            +---------------------------+
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Password/secure fields never contribute to learning or server assist.
2. Local-first offline path always works.
3. Safety filter on both local and server candidates.
4. Pack signatures verified.
5. Consent gates server personalization.

### 5.2 On-device models

N-gram + small transformer distilled; quantized INT8; language packs; confuse-a-tron spell lists; beam for corrections.

### 5.3 Server assist

Prefix → catalog-aware suggestions (brands, ASINs names); rate limited; redacted context types (search vs chat).

### 5.4 Spell-check

Edit-distance to dictionary + noisy-channel probabilities; contextual LM rescoring; don’t over-correct names in user lexicon.

### 5.5 Progressive scale

10×: better deltas; 100×: on-device neural default; server only rare; 1,000×: federated learning opt-in.

### 5.6 Ownership

Mobile client team owns device budgets; search suggest owns server assist; privacy owns consent UX.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        A **hybrid on-device + server** mobile autocomplete and spell-check system: quantized local LM/dictionaries, user lexicon, safety, optional consented server assist for long-tail/catalog terms, signed language packs, and strict privacy/battery budgets.

        ### 6.2 Key decisions worth defending

        1. Local-first; server assist optional
2. Never learn from secure/password fields
3. Quantized packs with delta CDN updates
4. Consent-gated privacy aggregates
5. Merge local+server through safety

        ### 6.3 Risks & follow-ups

        - Pack size vs quality tension
- Multilingual code-switch hardness
- Assist cost if over-triggered
- OS IME boundary confusion

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **Mobile Autocomplete & Spell-Check** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---

## 7. Deeper / Related Interview Questions

**Q1. Why not server-only autocomplete like desktop web?**

**A:** Mobile offline, battery, privacy, and RTT variability. Server-only feels broken on planes/subways and risks keystroke logging perceptions.

**Q2. How do you keep models small?**

**A:** Distillation, quantization, vocabulary pruning, per-language packs, delta updates, n-gram fallback.

**Q3. Federated learning?**

**A:** Phase 2 opt-in for improving packs without raw central keystrokes—complex; mention as 100×+ path.

**Q4. Catalog terms like ASIN titles?**

**A:** Server assist + periodic on-device brand dictionaries for head terms.

**Q5. Deal-breaker?**

**A:** Requiring network for every keystroke; or learning from password fields.

**Q6. Evaluating quality?**

**A:** Keystroke saved, correction acceptance, regret (undo rate), offline quality suite, battery traces.

**Q7. Abuse suggestions?**

**A:** On-device safety lists + server policy; blocklist updates via packs.

**Q8. Relation to retail search autocomplete?**

**A:** Different surface: this is typing UX hybrid; retail suggest is server search box at huge QPS. Share dictionaries carefully.

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

        ### Appendix F — Assist API sketch

```text
POST /v1/assist
  { locale, prefix, context_type, device_class, consent_token }
→ { suggestions[], corrections[], pack_hints[] }
```

### Appendix G — Closer checklist

- [ ] Local-first / offline path
- [ ] Secure fields never learn
- [ ] Consent for server assist
- [ ] Battery/model size budgets
- [ ] Safety on merge
- [ ] Progressive scale / federated mention



## Extended Notes — Mobile Autocomplete & Spell-Check

### E1. Field types

search, chat, email, password, address—policy matrix for learning/assist/autocorrect aggressiveness.

### E2. Undo UX

Autocorrect must be easily undoable; high undo rate pages quality.

### E3. Personal names

User lexicon protects uncommon names from “fixing”.

### E4. CJK / languages

Different tokenization; packs per locale; code-switch detector.

### E5. Security

Signed packs; HTTPS assist; certificate pinning optional; no plaintext lexicon backup without encryption.

### E6. Battery profiling

CI bench on mid-tier devices; reject pack if p99 infer exceeds budget.

### E7. Experimentation

Pack versions as experiments; careful with download sizes.

### E8. Server cost control

Assist only when local entropy high; cache popular prefixes at edge.

### E9. Accessibility

Suggestions compatible with screen readers; large hit targets.

### E10. Kids Fire tablets

Stricter lexicons; disable server assist by default.

### E11. Metrics privacy

Aggregate counters; differential privacy for rare n-grams if collected.

### E12. Conflict with system keyboards

If embedding in Amazon apps only, scope clearly vs replacing OS IME.

### E13. Failure mode

Pack corrupt → fall back to English tiny dict; assist timeout → local only.

### E14. Related systems

Retail search autocomplete (server), Alexa voice spelling adjacent, CDN pack distribution, privacy consent hub.

### E15. Cost narrative

USD per million assist calls + CDN egress for packs; local-first is frugality.

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


## 16. Additional Deep Q&A — Mobile Autocomplete & Spell-Check

### Q1. When do you call server assist?

When local confidence low, network available, consent allows, field type permits, and budget tokens remain. Never for password/secure fields.

### Q2. How do you measure on-device quality?

Lab harnesses with typing traces; acceptance/undo rates from opt-in telemetry; battery traces on mid-tier devices; offline suite per language.

### Q3. How aggressive should autocorrect be?

User setting: off / modest / aggressive. High undo rate → auto-dial down. Proper nouns in user lexicon protected.

### Q4. Delta pack updates?

Binary diffs + compression; staged rollout; signature verify; reject if decode fails; keep last-good pack.

### Q5. Code-switching?

Language ID on recent tokens; mixed lexicons; avoid correcting Spanish words into English lookalikes aggressively.

### Q6. Catalog brand packs?

Head brands/ASINs in on-device catalog dictionary deltas; long-tail via server assist in search fields.

### Q7. Federated learning pitfalls?

Device heterogeneity, privacy composition, attack via poisoned clients—treat as advanced phase with expert privacy review.

### Q8. Relation to server search autocomplete?

Different product: typing UX vs search suggest service. Share spell corpora carefully; don’t couple freights.

### Q9. Storage pressure on cheap devices?

Tiered packs (tiny/base/full); evict unused languages; compress.

### Q10. Accessibility?

Announce suggestions to screen readers; large targets; respect OS reduced-motion/autocorrect settings where applicable.

## 17. Scenario Drills — Mobile AC/Spell

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Airplane offline | Local packs only | Offline is a feature |
| Assist timeout | Show local | Deadline merge |
| Corrupt pack | Last-good fallback | Signed artifacts |
| Password field | Disable learn/assist | Hard invariant |

## 18. Final Checklist — Mobile AC/Spell

- [ ] Local-first offline path
- [ ] Secure fields never learn
- [ ] Consent for server assist
- [ ] Battery/latency budgets numeric
- [ ] Signed language packs + deltas
- [ ] Safety on merged candidates
- [ ] Field-type policy matrix
- [ ] Undo/regret metrics

## 19. Expanded Design Notes — Mobile AC/Spell

### 19.1 On-device architecture

SDK hooks text field changes (debounced). Local n-gram + small neural LM propose completions; spell module proposes corrections; safety filter; UI renders suggestion strip. User lexicon updates on accepted novel tokens outside deny-fields.

### 19.2 Model choices

Distilled transformer or RNN LM quantized; or classic Kneser-Ney n-grams for tiny devices. Spell: symmetric delete + noisy channel. Contextual rescoring using LM.

### 19.3 Server assist API privacy

Send prefix and coarse context_type only—not full message history by default. Rate limit. Edge cache popular prefixes. Logs aggregated/opt-in.

### 19.4 Pack pipeline

Train → evaluate → quantize → package → sign → CDN → staged device rollout. Metrics include download fail rate and post-update undo rate.

### 19.5 Field policy matrix

search: assist OK, learn OK (non-PII). chat: assist optional, learn careful. email: suggest careful. password: all off. address: suggest structured, don’t upload raw.

### 19.6 Kids devices

Fire kids profiles: stricter lexicon, no server assist default, stronger safety lists, parent controls for download packs.

### 19.7 Battery & thermal

Cap infer time; skip neural on thermal throttle; fall back to dictionary; CI benches on low-end SKUs.

### 19.8 Roadmap

Better multilingual, on-device personalization without cloud, optional federated improvements, tighter retail search field integration with catalog dictionaries.

## 20. Hybrid Merge Pseudocode

```text
local = device_suggest(prefix, k=8)
if secure_field or not consent or offline or local.conf > T:
    return safety(local)
server = assist(prefix, deadline=120ms)
return safety(merge(local, server, k=8))
```

---

## 21. Pack Manifest

```text
PackManifest {
  locale, version, min_app, size_bytes, signature,
  checksum, features: [lm, spell, safety, catalog_head]
}
```

---

*End of document — Mobile Autocomplete & Spell-Check (SDE III)*
