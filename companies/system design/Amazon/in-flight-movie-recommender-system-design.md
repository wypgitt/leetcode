# System Design: In-Flight Movie Recommender (Duration-Constrained)

> **Focus areas:** Flight duration constraints · Offline catalogs · Onboard caching · Personalization under sparse connectivity · Watch-completion · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Hard duration feasibility constraints, onboard vs ground planes, deal-breakers for “ignore runtime vs remaining flight time”
> **Interview theme:** Amazon SDE III / L6 — **Prime Video / Airlines partnership**-style in-flight recommender—movies that **fit the flight** with degraded connectivity

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

Goal: recommend **movies/shows that fit remaining flight duration** (and attention context), with catalogs that may be **pre-staged onboard**, personalization that works **offline/intermittently**, and measurement on completion.

### 1.0 What this is / is not

| Dimension | **In-flight recommender** | Not this |
|-----------|---------------------------|----------|
| Constraint | Runtime ≤ remaining flight − buffers | Unlimited catalog browse only |
| Connectivity | Often offline / portal Wi‑Fi | Always-on Prime streaming assumptions |
| Catalog | Airline-licensed subset + cached | Full Prime catalog everywhere |
| Success | Completion, satisfaction, fit-to-flight | Max clicks on too-long titles |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Constraint? | runtime + episodes fit remaining time | Hard filter |
| F2 | Inputs? | Flight leg, remaining time, profile (optional), device | Context schema |
| F3 | Catalog? | Onboard cached titles | Catalog snapshot |
| F4 | Personalization? | Prefs synced pre-flight; onboard light | Hybrid |
| F5 | Episodes? | Suggest episode counts that fit | Packing logic |
| F6 | Kids? | Profile / seat context | Policy |
| F7 | Languages? | Audio/subtitle availability onboard | Filter |
| F8 | Updates mid-flight? | Remaining time updates | Recompute |
| F9 | Fallback? | Popular fitting titles | Non-empty |
| F10 | Licensing? | Airline window | Catalog validity |
| F11 | Metrics? | Start, completion, abandon | Onboard logs flush later |
| F12 | Ground personalization? | Precompute top packs | Before departure |
| F13 | Multi-leg? | Per leg remaining | Leg_id |
| F14 | Live TV? | Optional | Separate |
| F15 | Ads? | Airline policy | Optional |

**MVP:** remaining-time hard filter; onboard catalog; pre-flight personalization pack; popular fallback; completion logging with delayed sync.

### 1.2 NFRs

Onboard recommend p99 < 100ms local; ground precompute OK minutes; storage on aircraft limited; privacy of profiles on shared seatback.

### 1.3 Cases

Happy: 6h flight → recommend 2h movie + series pack; 45m short-haul → sitcoms/episodes; kids profile → G/PG fitting.

| Case | Behavior |
|------|----------|
| Turbulence pause | Don’t over-penalize abandon |
| Wrong remaining time | Conservative buffer (taxi/safety videos) |
| Catalog miss | Ground sync next turnaround |
| Shared seatback | Privacy pin / anonymous mode |
| Multi-stop | Reset per leg |

### 1.4 Scales

| Metric | Base | 10× | 100× |
|--------|------|-----|------|
| Flights/day | 50K | 500K | — |
| Seat sessions/day | 5M | 50M | 500M |
| Onboard titles | 500–5K | — | richer caches |
| Precompute packs | per flight/user segment | — | —

---

## 2. Back-of-the-Envelope Estimation

Onboard catalog 2K titles × metadata 2KB = small. Video assets separate (TBs) staged by airline ops—not recommender’s store.

Pre-flight: for 300 passengers, generate personalized lists of 50 fitting titles—trivial compute on ground; push to aircraft systems.

Mid-flight re-rank local: milliseconds on embedded service.

Buffers: `effective = remaining - taxi_buffer - meal_buffer_optional`.

---

## 3. High-Level Design

### 3.1 Dual plane

| Plane | Where | Role |
|-------|-------|------|
| Ground | Cloud | Personalization, licensing, pack build, heavy ML |
| Onboard | Aircraft server / seatback | Duration filter, local re-rank, playback, logs |

### 3.2 Components

Ground: Profile Service, Catalog/Licensing, Duration Pack Builder, Sync to airline content system.
Onboard: Local Catalog Index, RemainingTime Service, Local Ranker, Playback, Log Buffer.

### 3.3 Feasibility filter

```text
feasible(title) = runtime_minutes <= effective_remaining
for series: n_episodes * ep_runtime <= effective_remaining
```

Soft prefer titles with runtime in [0.5, 0.85] × remaining (finishable, not tiny).

### 3.4 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Constraint | Hard filter first | Ignore runtime |
| ML onboard | Light re-rank | Cloud calls mid-flight required |
| Profile on seatback | Pin/anonymous | Dump full profile plaintext |
| Sync | Pre-flight packs | Assume always-online streaming |

---

## 4. Architecture Diagram

```text
[Ground - Amazon Cloud]
Profile + History --> Pack Builder --> Personalized feasible lists
Licensing Catalog -/                 |
Flight schedule remaining estimate -/ 
                |
              Sync at gate / content loader
                |
                v
[Onboard]
RemainingTime --> Local Filter/Rank --> Seatback UI --> Playback
      ^                                     |
      clock/avionics feed                   v
                                      Log Buffer --> flush on landing Wi-Fi
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Never primarily recommend titles exceeding effective remaining time.
2. Kids policy enforced onboard even if packs stale.
3. Logs privacy-safe on shared devices.
4. Playback works if personalization missing (popular feasible).

### 5.2 Packing algorithm

Precompute ranked feasible set; onboard adjust as remaining shrinks; suggest “finishable tonight” packs (movie + short).

### 5.3 Personalization under sparse data

Use pre-synced embeddings/affinities; avoid heavy cold cloud retrieval aloft.

### 5.4 Progressive scale

10× airlines: standardize sync API. 100×: segment packs + device models. 1,000×: global airline platform multi-tenant cells.

### 5.5 Ownership

Amazon video personalization owns models; airline IFE owns onboard hardware SLOs; clear contract on catalog snapshots + time remaining API.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        A **duration-constrained in-flight movie recommender** with ground personalization packs, onboard feasibility filtering/re-ranking, offline-first operation, and delayed measurement sync.

        ### 6.2 Key decisions worth defending

        1. Hard runtime feasibility before rank
2. Ground heavy ML / onboard light re-rank
3. Offline-first with popular fallback
4. Conservative time buffers
5. Seatback privacy controls

        ### 6.3 Risks & follow-ups

        - Airline integration variance
- Runtime metadata errors
- Licensing snapshot staleness
- Wi-Fi temptation to couple cloud

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **In-Flight Movie Recommender** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---

## 7. Deeper / Related Interview Questions

**Q1. Why hard-filter runtime instead of only ranking soft penalty?**

**A:** Recommending a 3h movie on a 90m flight destroys trust. Soft penalties still surface infeasible titles. Hard filter first, soft preference second.

**Q2. How do you get remaining flight time?**

**A:** Airline IFE/avionics integration; conservative buffers; update as flight progresses; fall back to scheduled ETA.

**Q3. What if Wi-Fi works mid-flight?**

**A:** Optional enhancement path to cloud—but core must work offline. Don’t make online required.

**Q4. Series recommendations?**

**A:** Pack number of episodes that fit; prefer complete arcs if tagged; don’t start long unfinished seasons without warning.

**Q5. Deal-breaker?**

**A:** Design that requires cloud inference per seatback request mid-flight with no offline fallback.

**Q6. Privacy on seatback?**

**A:** Session PIN, auto-logout, minimal profile cached, wipe on end-of-flight.

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

        ### Appendix F — Schemas

```text
FlightContext { flight_id, leg_id, remaining_min, buffers, locale }
Title { title_id, runtime_min, rating, langs[], kids_ok }
Pack { passenger_token?, title_ids[], model_version, built_at }
```

### Appendix G — Closer checklist

- [ ] Hard duration filter
- [ ] Ground vs onboard planes
- [ ] Offline fallback
- [ ] Kids/privacy on seatback
- [ ] Completion metrics delayed sync



## Extended Notes — In-Flight Movie Recommender

### E1. Buffer policy

Taxi, safety demos, meals—product-configured buffers by airline/route. Underestimate remaining time slightly.

### E2. Content rating

Locale/airline rules; kids seat detection if available.

### E3. Licensing windows

Catalog snapshot expires; onboard must not show expired licenses after turnaround sync fail—fail safe hide.

### E4. Evaluation

Completion rate within flight, rewatch, survey CSAT; not only click-through.

### E5. Multi-passenger households

Seat profiles differ; don’t share personalization across seats without auth.

### E6. Short-form vs long

As remaining drops below 25m, switch rails to shorts/episodes/magazines.

### E7. Device heterogeneity

Seatback vs personal device streaming portal—same feasibility API.

### E8. Sync bandwidth at gate

Prioritize metadata+packs first; large video assets via airline ops channels.

### E9. Amazon differentiation

Prime tastes pre-flight sync is a plus vs generic IFE popularity lists—call this out.

### E10. Failure mode storytelling

Personalization missing → popular feasible; time feed missing → scheduled duration; catalog corrupt → safe mode classics list.

### E11. A/B testing

Mostly on ground pack builder; onboard flags limited; flush metrics after landing.

### E12. Related systems

Prime Video recommender, airline IFE CMS, identity, experimentation.

### E13. Runtime metadata quality

Wrong runtimes break trust—QA catalog; prefer source-of-truth from video asset service.

### E14. Attention context

Red-eye vs daytime flights change genre priors—optional context feature.

### E15. Cost

Ground precompute cheap; onboard CPU constrained—keep models tiny.

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


## 16. Additional Deep Q&A — In-Flight Movie Recommender

### Q1. What buffers do you subtract from remaining time?

Taxi-in/out, safety demos, meal service optional, customer pause slack. Airline-configurable. Underestimate remaining time slightly to protect finishability.

### Q2. How do you recommend series?

Compute max episodes that fit; prefer complete story arcs tagged in metadata; warn on cliffhangers if next episode won’t fit.

### Q3. Personal device vs seatback?

Same feasibility API; personal device may stream if Wi-Fi; seatback usually local cache. Personalization auth differs (Prime login vs seat session PIN).

### Q4. How do packs sync at the gate?

Prioritize small metadata+rank lists; bulk video via airline content ops. Packs keyed by flight_id + segment + passenger token hash.

### Q5. What if avionics time feed fails?

Fall back to scheduled block time minus elapsed; widen buffers; still hard-filter.

### Q6. Kids traveling?

Seat/profile flags; airline rating rules; ignore adult personalization packs.

### Q7. Metric delay after landing?

Buffer logs onboard encrypted; flush via gate Wi-Fi/cellular; late-join training. Don’t block UX on flush.

### Q8. Why not use full Prime cloud recommender onboard?

Connectivity and catalog licensing differ; runtime constraint dominates; must work offline.

### Q9. Multi-leg trips?

Separate contexts per leg; don’t recommend 3h movie before 1h hop even if total travel is 10h unless layover viewing supported.

### Q10. Licensing expiry mid-day?

Snapshot validity window; hide expired; sync on turnaround; never show unlicensed titles.

## 17. Scenario Drills — In-Flight Recs

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Short-haul 45m | Episode/short rails | Finishability first |
| Red-eye long haul | Calm genres prior + long movies | Context priors |
| Personalization missing | Popular feasible list | Offline fallback |
| Shared seatback privacy | PIN + wipe | No leftover profile |

## 18. Final Checklist — In-Flight Recs

- [ ] Hard duration feasibility
- [ ] Ground vs onboard planes
- [ ] Offline-first fallback
- [ ] Buffers explicit
- [ ] Kids/rating policy onboard
- [ ] Seatback privacy wipe
- [ ] Delayed metrics flush
- [ ] Licensing snapshot validity

## 19. Expanded Design Notes — In-Flight Recs

### 19.1 Effective time formula

`effective = max(0, remaining_reported - buffer_taxi - buffer_safety - buffer_meal_opt - buffer_slack)`. Recompute on interval or on significant ETA change. As effective shrinks, refilter lists and switch rails to shorts.

### 19.2 Ground pack builder

Inputs: passenger affinities (if consented/Prime), catalog onboard snapshot, flight duration estimate, locale/languages, kids flag. Outputs: ranked title_ids with reasons. Build closer to departure for fresher ETAs.

### 19.3 Onboard service constraints

CPU/memory limited. No GPU inference. Use precomputed scores + light boosts (language match, unfinished continue watching if cached). p99 local < 100ms.

### 19.4 Continue watching

If passenger has mid-movie progress cached and remaining time fits leftover runtime, boost strongly—highest satisfaction path.

### 19.5 Airline multi-tenant platform

Amazon provides personalization as a service to multiple airlines with cell isolation, different licensed catalogs, and brand UX. Don’t hardcode one airline’s buffers.

### 19.6 Evaluation

Completion within flight, start rate, abandon after 5m, survey thumbs, complaint rate about ‘movie too long’. Offline ranking metrics secondary.

### 19.7 Security

Encrypt profile packs at rest onboard; wipe after flight; sign catalogs; prevent seat-to-seat profile reads.

### 19.8 Evolution

Optional online enhance when portal Wi-Fi strong; still never require it. Short-form catalogs grow; interactive maps etc. out of scope.

## 20. Feasibility Examples

| Remaining | Buffer | Effective | OK titles |
|-----------|--------|-----------|-----------|
| 360m | 40m | 320m | runtime ≤ 320 |
| 90m | 25m | 65m | episodes/shorts ≤ 65 |
| 25m | 10m | 15m | shorts only |

Soft preference band: runtime ∈ [0.5, 0.85] × effective for primary movie suggestion.

---

## 21. Onboard Log Record

```text
PlayEvent { flight_id, seat_session, title_id, t_start, t_end, effective_remaining_at_start, completed_bool }
```

Flush after landing; scrub seat_session mapping on wipe.

---

*End of document — In-Flight Movie Recommender (SDE III)*
