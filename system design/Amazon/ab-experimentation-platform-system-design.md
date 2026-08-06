# System Design: A/B Experimentation Platform (Amazon)

> **Focus areas:** Deterministic assignment · Exposure logging · Metrics pipelines · Experiment ownership · Mutually exclusive layers · QA / override · SRM detection · Ramp & kill switches  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS types, explicit deal-breakers, ownership clarity  
> **Interview theme:** Amazon SDE III / L6 — experimentation infrastructure that product teams trust for revenue-impacting decisions

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

Goal: design Amazon-scale **A/B experimentation** so teams can define experiments, assign units consistently, log exposures, compute metrics with statistical rigor, enforce mutual exclusivity, and ship safely with clear **ownership**.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Assign → expose → measure → decide | ML feature store or full personalization |
| Unit of randomization | Usually customer/account (configurable) | Always page-view (biased) |
| Truth | Deterministic salt+hash assignment | Random each request |
| Amazon lens | Ownership, blast radius, business metrics, ops | Academic A/B only |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who runs experiments? | Product, UX, ranking, pricing, ads teams | Multi-tenant console + APIs |
| F2 | Assignment unit? | Default **customer_id**; also session, device, seller | Configurable unit + salt |
| F3 | Sticky assignment? | Yes for experiment lifetime (unless override) | Deterministic hash; persist overrides |
| F4 | Variants? | Control + N treatments; unequal weights OK | Weight → bucket ranges |
| F5 | Where evaluated? | Edge/service SDKs + server-side config | Config fanout + local eval |
| F6 | Exposure logging? | Log only when treatment **applied/seen** | Exposure ≠ assignment |
| F7 | Metrics? | Conversion, GMV, latency, returns, CS contacts | Metric registry + pipelines |
| F8 | Mutual exclusion? | Layers/namespaces; same unit can’t collide | Layer bookkeeping |
| F9 | Targeting? | Marketplace, device, Prime, percent ramp | Filter before assign |
| F10 | QA overrides? | Force variant for employee/test accounts | Override store, audited |
| F11 | Ramp / kill? | 1% → 5% → 50% → 100%; instant kill | Config version + kill switch |
| F12 | Ownership? | Named owner, oncall, approval for high-risk | Ownership metadata + gates |
| F13 | Analysis? | CUPED/guardrails; SRM alerts | Offline + nearline stats |
| F14 | Holdouts? | Long-term holdout layers | Separate layer / salt |

**MVP functional scope (lock with interviewer):**

1. Experiment CRUD with owner, hypothesis, metrics, start/end.  
2. Deterministic assignment (unit + experiment salt → variant).  
3. Layers for mutual exclusivity.  
4. Targeting + percent ramp.  
5. SDK evaluate + **exposure** events.  
6. Metric registry + daily/hourly aggregation.  
7. QA force-variant overrides with audit.  
8. Kill switch and ramp controls.  
9. Dashboard: assignment, exposure, metrics, SRM.

**Out of MVP (explicitly defer):**

- Full causal ML / uplift modeling platform  
- Multi-armed bandit as default (can be Phase 2)  
- Client-only experiments without server config  
- Replacing every service’s feature flag system overnight  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Eval latency | In request path | p99 < 1–5 ms local; config fetch async |
| N2 | Consistency | Same unit → same variant | Sticky for experiment life |
| N3 | Availability | Eval must degrade soft | Fail-open to control or last-known config |
| N4 | Correctness | No silent bias | Exposure logging integrity; SRM |
| N5 | Scale | Amazon retail + digital | See scale table |
| N6 | Audit | Who changed what | Immutable config history |
| N7 | Isolation | Bad experiment ≠ site outage | Blast-radius limits, approval |
| N8 | Privacy | Respect account deletion | Unit hashing + retention policy |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Owner creates experiment in layer “checkout-UX”, 50/50, metric = purchase_rate.  
2. Customer hits checkout → SDK evaluates → variant B → UI change → exposure logged.  
3. Purchase events join exposures → metric lifts computed with CI.  
4. QA account forced to B for screenshot validation.  
5. Ramp 1%→10%→50%; SRM green; ship to 100% or archive.  
6. Kill switch → all units get control within config TTL.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Same customer, two exclusive experiments in one layer | Assign at most one; or reject conflict at schedule time |
| Assignment logged without exposure | Analysis uses **exposure**, not mere eligibility |
| Logged-out → logged-in identity merge | Policy: sticky on customer_id after login; document bias |
| Config lag (old version on host) | Versioned configs; bounded staleness; metrics tagged |
| Bot traffic | Filter bots from analysis; optional assign skip |
| Unequal bucket weights + bad hash | Use wide bucket space (e.g. 10k); validate ranges |
| Owner leaves team | Ownership transfer required before edits |
| Metric definition drift | Metric registry version pinned per experiment |
| Peak Prime Day | Eval from local cache; analytics lag OK; kill switch hot path |
| Override forgotten | TTL + audit alerts on sticky QA overrides |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active experiments | 500 | 5K | 50K | 500K |
| Concurrent layers | 50 | 200 | 1K | 5K |
| Eval QPS (SDK calls) | 200K | 2M | 20M | 200M |
| Unique units / day | 50M | 200M | 500M | 1B+ |
| Exposure events / day | 500M | 5B | 50B | 500B |
| Metric event types | 100 | 300 | 1K | 5K |
| Config publishes / day | 200 | 2K | 20K | 100K |
| Analyst queries / day | 2K | 20K | 100K | 500K |
| Override records | 10K | 100K | 1M | 10M |

**What each jump forces:**

- **10×:** Central config service + CDN/edge cache; exposure Kafka; basic dashboards.  
- **100×:** Layer capacity planning; sharded analytics; nearline SRM; cell/marketplace isolation.  
- **1,000×:** Hierarchical layers; pre-aggregated metric cubes; assignment at edge; strict ownership SLAs; automated guardrail kill.

### 1.5 Etc. (Constraints & Assumptions)

- Prefer **server-authoritative config**; clients may cache.  
- Default fail mode for revenue-critical paths: **control** (fail-safe), not random.  
- Statistical significance is necessary but not sufficient—guardrail metrics matter.  
- Experimentation platform owns assignment + logging contracts; product teams own UX changes.

**Scope statement:**

> Design an Amazon A/B platform: deterministic sticky assignment, layer-based mutual exclusion, exposure-correct logging, metric pipelines, QA overrides, ramp/kill, and clear ownership—from ~200K eval QPS through 10× / 100× / 1,000× with edge config and scalable analytics.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| SDK evaluate | 200K | 200M | Local hash; almost no RPC |
| Config fetch / poll | 5K hosts × 1/min | Millions hosts | CDN + delta |
| Exposure ingest | ~10K/s avg; 50K peak | ~10M/s | Async, lossy-tolerant with care |
| Metric events | ~20K/s | ~20M/s | Shared with analytics bus |
| Console / admin | hundreds | tens of K | Strong consistency OK |
| Analysis queries | bursty | warehouse scale | Pre-agg |

**Critical:** Eval QPS is **not** the same as exposure QPS. Many evaluates never become exposures (not in experiment, filtered, not rendered).

### 2.2 Assignment compute

```text
hash(unit_id + salt) → 64-bit → bucket in [0, 9999]
Cost: ~microseconds CPU; pure function; no network

200M eval/s × 1 μs = 200 CPU-seconds/s → ~200 cores if naive single-thread
In practice: embedded in app threads already; negligible vs business logic
```

### 2.3 Exposure storage

```text
Exposure event ~200–400 B (unit_hash, exp_id, variant, ts, context)
Baseline 500M/day × 300 B ≈ 150 GB/day
1,000×: 500B/day × 300 B = 150 TB/day

Unit check: 5e11 × 300 = 1.5e14 B = **150 TB/day**
Retain hot 30–90 days; aggregate to daily facts earlier
```

### 2.4 Config fanout

```text
Active experiment config blob per layer-set: 100 KB – 5 MB compressed
1M hosts × 1 MB full refresh/day = 1 PB/day — **deal-breaker**
→ Delta publish + CDN + version polling; typical delta << 10 KB
```

### 2.5 Analytics cost sketch

```text
Join exposures × purchases:
Baseline: 500M exposures ⋈ 20M purchases → warehouse job hours
Pre-aggregate: (exp_id, variant, day, metric) facts → interactive UI
```

### 2.6 Critical bottlenecks

1. Config fanout storms after bad publish  
2. Exposure pipeline loss → biased results  
3. Layer contention / scheduling conflicts  
4. SRM from bot/CDN asymmetry  
5. Kill-switch propagation lag  
6. Metric definition disagreement across teams  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Layer (namespace, mutex policy, capacity %)
Experiment (id, layer, salt, owner, status, ramp%, targeting)
Variant (id, weight, params / feature payload)
AssignmentRule: hash(unit + salt) → variant | none
Override (unit, experiment, variant, ttl, actor, reason)
Exposure (unit, experiment, variant, ts, request_id, context)
MetricDef (id, event, aggregation, filters, owner)
Scorecard (experiment × metrics × stats)
```

### 3.2 Deterministic assignment

```text
function assign(unit, experiment):
  if override[unit, experiment]: return override.variant
  if not targeting.match(unit, context): return None
  if not in_ramp(unit, experiment.ramp%, experiment.ramp_salt): return None
  b = hash64(unit + experiment.salt) % 10000
  return variant_for_bucket(b, experiment.weights)
```

**Properties:**

- Sticky without DB write for normal path  
- Ramp uses **separate salt** so increasing % expands set (monotonic inclusion)  
- Overrides short-circuit but are audited  

**Deal-breaker:** `random()` per request → unstable UX and invalid stats.

### 3.3 Layers & mutual exclusion

```text
Unit traffic in a layer is partitioned across experiments (and residual unused).
Example layer "search-ranking" capacity 100%:
  Exp A: 20%  Exp B: 30%  residual 50%

Assignment within layer:
  layer_bucket = hash(unit + layer.salt) % 10000
  map ranges → at most one experiment → then experiment variant hash
```

| Policy | Behavior | When |
|--------|----------|------|
| Mutex layer | At most one experiment | Conflicting UX/ranking |
| Parallel layers | Independent salts | Orthogonal dimensions |
| Domain layers | Checkout vs Search | Org boundaries |

**Scheduling conflict:** reject overlapping range allocation at create/ramp time (or waitlist).

**Deal-breaker:** independent coin-flips per experiment without layers → interaction confounds and unfair traffic.

### 3.4 Exposure vs assignment

| Concept | Meaning | Use in analysis |
|---------|---------|-----------------|
| Eligible | Passed targeting | Not for ITT alone |
| Assigned | Hash placed in variant | Intent-to-treat if logged carefully |
| Exposed | Treatment actually applied/seen | **Primary** for triggered analysis |

Log exposure when:

- Server renders treatment, or  
- Client confirms application (with care for loss)  

**Amazon practicality:** prefer server-side exposure when possible for integrity.

### 3.5 Config distribution

```text
Control Plane (strong consistency) → Config Store (versioned)
        → CDN / Config Edge → Host agents → in-process snapshot
Kill switch: high-priority channel / short TTL poll (e.g. 5–30s)
```

Versions are immutable; rollback = publish previous version pointer.

### 3.6 Metrics & analysis pipeline

```text
Product events (purchase, click, latency span)
    → Event Bus → Metric Enricher (join experiment exposures)
    → Fact tables (exp, variant, day, metric)
    → Stats engine (means, CI, CUPED, SRM)
    → Scorecard UI
```

**Guardrails:** latency p99, error rate, refund rate, CS contacts—auto-alert; optional auto-pause.

### 3.7 QA overrides

```text
PUT /overrides {unit_id, experiment_id, variant, ttl, reason}
- Requires authz (experiment writer or QA role)
- Audited; listed in console
- TTL required (default 24h, max 7d)
- Does not count in analysis (filter override=true) OR separate carve-out
```

**Deal-breaker:** shared “test mode” that silently changes production hashing for many users.

### 3.8 Ownership model (Amazon-critical)

| Field | Purpose |
|-------|---------|
| Owner (principal) | Accountable human/team |
| Oncall | Page for guardrail pages |
| Approvers | High-risk / pricing / trust |
| Blast radius class | Low / Medium / High |
| Rollback plan | Linked runbook |

High-blast-radius experiments require dual approval before >X% ramp.

### 3.9 Storage / system trade-offs

| Component | Choice | Deal-breaker |
|-----------|--------|--------------|
| Assignment | Deterministic hash | Per-request random or always-DB assignment at 200M QPS |
| Config | Versioned snapshots + CDN | Per-eval RPC to control plane |
| Exposures | Append log / Kafka | Synchronously write OLTP per page view |
| Analysis | Warehouse + pre-agg | Live join on serving path |
| Overrides | Small strongly consistent store | Bake into global hash (unreviewable) |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Owners (Console / API)
        |
        v
+------------------+     audit      +----------------+
| Control Plane    |-------------->| Audit Log      |
| Experiments      |               +----------------+
| Layers / Metrics |
| Overrides        |
+--------+---------+
         | publish version N
         v
+------------------+
| Config Store +   |
| CDN / Edge       |
+--------+---------+
         | poll / push delta
         v
+------------------+     evaluate      +--------------------+
| Service / Edge   | <--- SDK -------->| In-process rules   |
| (Retail, Search) |                   | hash + targeting   |
+--------+---------+                   +----------+---------+
         | exposure                                |
         v                                         | override lookup (cached)
+------------------+                               v
| Exposure Bus     |                    +------------------+
+--------+---------+                    | Override Store   |
         |                              +------------------+
         v
+------------------+     +------------------+
| Exposure Lake    |---->| Enrichment Jobs  |
+------------------+     +--------+---------+
                                  |
         Product Metric Events ---+
                                  v
                         +------------------+
                         | Scorecards/SRM   |
                         +------------------+
```

### 4.2 Sequence: evaluate + expose

```text
Request → SDK.loadConfig(v)
SDK → targeting? → ramp? → layer assign → variant
Apply treatment params
SDK/server → emit exposure(exp, variant, unit_hash, request_id)
Continue business response
```

### 4.3 Sequence: kill switch

```text
Owner → Pause/Kill experiment
Control plane → publish version N+1 (status=KILLED; force control)
Edge TTL / push → hosts pick up in ≤30s (SLO)
New evaluates → control; optional “sticky kill” ignores old treatment
Alert oncall; scorecard freezes treatment ramp
```

### 4.4 Sequence: mutually exclusive scheduling

```text
Create Exp C in layer L needing 20%
Layer allocator checks free residual ≥ 20%
If yes: allocate bucket range; publish
If no: reject or waitlist; suggest other layer / reduce ramp
```

### 4.5 Multi-marketplace / cells

```text
Configs scoped by marketplace (US, UK, …)
Analysis partitioned by marketplace
Cross-marketplace experiments: explicit multi-scope + separate salts or shared salt with care
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Determinism:** same (unit, experiment salt, version rules) → same variant.  
2. **Monotonic ramp:** increasing ramp% never drops previously included units (same ramp salt).  
3. **Mutex:** unit in ≤1 experiment per mutex layer.  
4. **Exposure integrity:** analysis filters to exposed (or declared ITT policy).  
5. **Overrides audited** and excluded from default scorecards.  
6. **Kill switch** bounded propagation SLO.  
7. **Config immutability** of historical versions.  
8. **Ownership non-null** for running experiments.  
9. **Fail-safe default** for eval errors on critical paths → control.  
10. **Metric pin:** experiment references metric_def version.

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Bad config publish | Instant rollback pointer; canary hosts first |
| Exposure loss spike | Pipeline lag/drop alerts; pause decisions |
| SRM triggered | Auto-page owner; recommend pause |
| Hash library mismatch across langs | Conformance test vectors in CI |
| Override store down | Eval without overrides (document); critical QA may fail |
| Analytics delay | Decisions wait; don’t “eyeball” partial days blindly |
| Layer double-book | Allocator transactions; invariant tests |

**Degradation modes**

| Mode | Behavior |
|------|----------|
| Config stale | Use last-good; alert age |
| Bus down | Buffer locally with cap; drop with metric (bias risk!) |
| Stats delayed | UI shows “incomplete” |
| Control plane down | No new publishes; serving continues |

### 5.2 Scalability

**Eval path:** O(experiments_in_layers_touched) but typically precompiled to efficient structures; aim O(layers) + O(1) hash.

**Sharding**

| Data | Shard key |
|------|-----------|
| Exposures | unit_hash or time + exp_id |
| Overrides | unit_id |
| Scorecards | exp_id |
| Config | global with marketplace partition |

**10× / 100× / 1,000× evolution**

| Scale | Architecture move |
|-------|-------------------|
| 10× | CDN configs; Kafka exposures; nightly stats |
| 100× | Nearline SRM; pre-agg cubes; layer capacity UI |
| 1,000× | Edge assignment; hierarchical layers; auto-guardrail pause; cell-local buses |

**Hot keys:** celebrity/test accounts with many overrides—cache per host; store remains small.

### 5.3 Maintainability

- **SDK multi-language** with shared test vectors (Java, C++, JS).  
- **Metric registry** prevents “purchase” meaning 5 different things.  
- **Experiment templates** for common patterns (UI copy, ranking).  
- **Scorecard standards** so leadership trusts comparisons.  
- **Ownership transfer** workflow.  
- **Chaos:** kill-switch drills; config canary.  

**Team boundaries**

| Team | Owns |
|------|------|
| Experimentation Platform | Assignment, layers, logging contracts, scorecards |
| Product teams | Treatments, hypotheses, accept/reject |
| Metrics platform | Event taxonomy, quality |
| Security/Privacy | Unit identity, retention |

### 5.4 Statistical & product correctness (Amazon lens)

```text
SRM: assigned/exposed counts vs expected weights
  chi-square / sequential test → alert

CUPED: variance reduction using pre-period metrics
Guardrails: no ship if latency/error guardrails fail even if primary wins
Heterogeneous effects: segment by device/marketplace carefully (pre-registered)
```

**Business trade-off:** shipping a “winning” experiment that worsens returns or CS contacts is a failure—platform must surface guardrails.

### 5.5 Security & abuse

- Authz on publish / ramp / kill / override  
- Prevent privilege escalation via targeting (“all employees” OK; “all users matching secret” reviewed)  
- Hash unit ids in logs where policy requires  
- Bot filtering documented for analysis  

### 5.6 Key metrics (platform SLOs)

| SLO | Target |
|-----|--------|
| Eval p99 local | < 5 ms |
| Kill propagate p99 | < 30–60 s |
| Exposure pipeline success | > 99.9% |
| Config canary auto-rollback | on error spike |
| Scorecard freshness | < 1–6 h nearline; daily final |

---

## 6. Wrap-Up

### 6.1 What we designed

An Amazon-grade A/B platform: **deterministic sticky assignment**, **mutex layers**, **exposure-correct logging**, **metric/scorecard pipelines**, **QA overrides**, **ramp/kill**, and **explicit ownership**—scaled from hundreds of thousands to hundreds of millions of evals/s via local evaluation and async analytics.

### 6.2 Key decisions worth defending

1. Hash assignment, not DB round-trip  
2. Layers for mutual exclusion  
3. Exposure ≠ assignment  
4. Fail-safe to control on critical paths  
5. Versioned config + fast kill channel  
6. Overrides audited & excluded from stats  
7. Ownership + blast-radius approvals  
8. Guardrail metrics equal primary metrics in ship decisions  

### 6.3 Risks & follow-ups

- Identity stitch (logged-out/in) bias  
- Client exposure loss  
- Interaction effects across parallel layers  
- Metric gaming / peeking without sequential methods  
- Bandits / personalization crossover (Phase 2)

### 6.4 Closer

> **Amazon A/B Platform:** trustworthy decisions at retail scale—deterministic assignment, mutex layers, exposure integrity, ownership, and kill switches with bounded blast radius.

---

## 7. Deeper / Related Interview Questions

**Q1. Why not assign in a central service per request?**

**A:** At 200M eval QPS, RPC cost/latency/availability dominate. Deterministic local hash with cached config is the Amazon-practical approach. Centralize **control plane**, not dataplane assignment.

**Q2. How do you ensure mutual exclusivity?**

**A:** Layers with partitioned traffic ranges under a layer salt. Allocator prevents double-booking. Orthogonal concerns go to different layers with independent salts.

**Q3. Assignment vs exposure—why care?**

**A:** Triggered analyses need units who actually saw the treatment. Counting eligibles who bounced before render dilutes or biases. Platform should define and enforce the logging point.

**Q4. How does ramp stay monotonic?**

**A:** Separate `ramp_salt`: unit included if `hash(unit+ramp_salt) % 10000 < ramp_threshold`. Raising threshold only adds units; never reshuffles existing ones into out-of-ramp.

**Q5. What if two language SDKs hash differently?**

**A:** Publish canonical test vectors (unit, salt → bucket). CI blocks SDK release on mismatch. This has caused real SRMs in industry.

**Q6. How do QA overrides work without poisoning results?**

**A:** Explicit override store; exposure tagged `override=true`; scorecards exclude by default; TTL + audit.

**Q7. Fail-open or fail-closed?**

**A:** Product-dependent. Checkout revenue path: fail to **control**. Internal tool experiment: fail-open to treatment may be OK. Make policy explicit per experiment class.

**Q8. How do you detect SRM?**

**A:** Compare observed variant counts to expected weights among exposed (or assigned) units; alert on significant deviation. Investigate bots, filtering bugs, exposure logging asymmetry.

**Q9. Long-term holdouts?**

**A:** Dedicated holdout layer with stable salt years-long; measure platform-wide incremental value; protect from casual reuse.

**Q10. How do pricing experiments differ?**

**A:** Higher blast-radius class; dual approval; tighter guardrails (margin, trust); often customer-level sticky with legal/UX review; slower ramp.

**Q11. Can users be in hundreds of experiments?**

**A:** Yes across many layers; mutex within layer. Cap layers touched per request for performance; prefer compiled rule sets.

**Q12. Real-time metrics vs next-day?**

**A:** Nearline for guardrails/SRM; finalized daily for ship decisions. Don’t let noisy hour-1 dashboards cause thrash.

**Q13. How do you handle logged-out users?**

**A:** Session/device unit with clear merge policy on login. Document that pre-login experiments may not carry over—avoid silent reassignment mid-funnel when possible.

**Q14. Interaction effects across layers?**

**A:** Accept as cost of velocity; for critical interactions, use combined experiments or factorial designs in one layer. Education + templates.

**Q15. Kill switch implementation detail?**

**A:** Experiment status in config; hosts poll fast channel; optional push. On kill, evaluate returns control; sticky assignment ignored. Measure propagation with version heartbeat metrics.

**Q16. What belongs in variant payload?**

**A:** Small params (copy keys, ranking model id, thresholds). Not megabyte assets—those live in CMS/services keyed by param.

**Q17. How do you prevent config download storms?**

**A:** CDN, jittered polls, deltas, ETags, canary percentage of hosts before fleet-wide.

**Q18. Warehouse cost blowup?**

**A:** Early pre-aggregation to (exp, variant, day, segment_id) facts; sample raw for debug; tiered retention.

**Q19. Who can ramp to 100%?**

**A:** Policy: owner + automated guardrail green + optional approver for high-risk. 100% is a **launch**, not just a ramp—ownership includes launch checklist.

**Q20. How is this different from feature flags?**

**A:** Flags focus on delivery/kill; experiments add assignment integrity, exposure, statistics, mutex layers, and decision workflows. Many companies unify—but don’t lose statistical contracts.

**Q21. CUPED in one minute?**

**A:** Use pre-experiment metric as covariate to reduce variance; faster detection of smaller effects. Platform provides standardized covariates.

**Q22. Peeking problem?**

**A:** Sequential testing or fixed horizon with pre-registered end. UI warns on continuous peeking; optional locked analysis plan.

**Q23. Bot traffic skew?**

**A:** Bot score filters in analysis; optionally exclude from assignment for content experiments. Monitor SRM after filter changes.

**Q24. Multi-marketplace experiment?**

**A:** Explicit scopes; separate or shared salts; analyze per marketplace then pooled with care (heterogeneity).

**Q25. Data deletion / GDPR?**

**A:** Prefer keyed unit hashes with unlink protocol; retention limits on raw exposures; aggregates kept.

**Q26. How to test the platform itself?**

**A:** A/A experiments continuously; measure false-positive rate; SDK conformance; pipeline replay tests.

**Q27. Unequal traffic 90/10?**

**A:** Supported via weights; power suffers on minority; UI shows expected runtime.

**Q28. Client-side flicker?**

**A:** Bootstrap config early; server-drive critical UI; accept anti-flicker techniques; log exposure after apply.

**Q29. What if residual layer traffic is exhausted?**

**A:** Scheduler rejects new experiments; encourage ending stale ones; ownership nudges for idle experiments past end date.

**Q30. Deal-breaker summary?**

**A:** Non-deterministic assignment; no layers for conflicting UX; analysis on non-exposed; unowned high-blast ramps; eval RPC at page QPS; kill switch that takes hours.

**Q31. How do you model experiment state machine?**

**A:** DRAFT → APPROVED → RUNNING → PAUSED/KILLED → SHIPPED/ARCHIVED. Illegal transitions blocked; every transition audited.

**Q32. Percent ramp vs variant weights?**

**A:** Ramp = fraction of population eligible; weights = split among variants inside eligible set. Keep salts separate.

**Q33. Sticky across salt change?**

**A:** Changing salt reshuffles—treat as new experiment. Platform should freeze salt after start.

**Q34. Exposure deduplication?**

**A:** First exposure per (unit, experiment, day) or lifetime—define; use idempotent keys for pipeline.

**Q35. Integration with CI/CD?**

**A:** Treatment code ships dark; experiment enables. Code ownership ≠ experiment ownership—but launch needs both.

**Q36. Cost attribution for platform?**

**A:** Chargeback by exposure volume / scorecard compute; incentivizes ending zombie experiments.

**Q37. How thin should SDK be?**

**A:** Hash + targeting + exposure emit. Keep statistics server-side. Thin SDK reduces version fragmentation.

**Q38. Partial network partition of config edge?**

**A:** Last-good config; divergent versions across AZs possible briefly—tag exposures with config_version for diagnosis.

**Q39. When is bandit appropriate?**

**A:** Continuous optimization with regret minimization; harder inference. Keep classic A/B for ship decisions; bandit as opt-in.

**Q40. Executive asks “did search redesign work?”**

**A:** Point to holdout + shipped experiment scorecard with primary + guardrails; don’t cherry-pick segments. Platform’s job is credible evidence.

**Q41. How do you handle schema evolution of exposure events?**

**A:** Versioned envelope; required fields unit, exp, variant, ts, config_version; forward-compatible parsers; contract tests.

**Q42. Can targeting depend on the metric you’re measuring?**

**A:** Dangerous (selection bias). Targeting should use pre-treatment covariates. Platform docs + lint rules flag suspicious targeting.

**Q43. What is a triggered experiment?**

**A:** Only users who enter a funnel step get exposed (e.g., opened gift-card modal). Power and interpretation differ from sitewide; assignment still sticky for the experiment id.

**Q44. How do you power-analyze before launch?**

**A:** Console estimates MDE given baseline rate, traffic, runtime, variant split. Block start if runtime absurd unless override reason.

**Q45. Cross-device customer?**

**A:** Prefer account_id when authenticated; accept cross-device inconsistency for anonymous. Document.

**Q46. Experiment on latency-sensitive path (ads auction)?**

**A:** Precompute assignment into request context at edge; no extra IO; minimal branches; careful binary size of config.

**Q47. How to retire experiments?**

**A:** Ship → remove flags → archive config → keep scorecard immutable. Zombie flags are reliability debt—ownership includes cleanup.

**Q48. Mutual exclusion across different randomization units?**

**A:** Hard—customer-level vs session-level layers can overlap confusingly. Standardize unit per layer domain.

**Q49. What alerts page the platform oncall vs experiment owner?**

**A:** Platform: pipeline down, kill lag, SDK panic rate. Owner: SRM, guardrail breach, scorecard anomalies.

**Q50. Summarize Amazon interview signal.**

**A:** You prioritize customer trust in decisions, operational ownership, blast radius, and practical dataplane design over academic purity—without sacrificing statistical integrity.

**Q51. How do you prevent “experiment sprawl”?**

**A:** TTL on end dates, idle detection, layer capacity quotas per team, cost showback, mandatory owners.

**Q52. Seeded randomization libraries?**

**A:** Don’t use general RNG. Use explicit hash (Murmur3/xxHash/SipHash) with fixed endian and string encoding docs.

**Q53. Can control be implicit?**

**A:** Yes—users not in ramp see default product. Still log eligibility carefully if doing ITT.

**Q54. Dual control groups?**

**A:** Useful for AA checks inside large experiments; costs traffic—template supports optional AA split.

**Q55. How fast must override reads be?**

**A:** Cached on host with short TTL (e.g. 30–60s); override store QPS tiny vs eval. Accept override propagation delay for QA.

**Q56. Marketplace legal differences?**

**A:** Targeting must include marketplace; some experiment types blocked by policy packs.

**Q57. What goes in the interview whiteboard first?**

**A:** Unit of randomization → deterministic assign → exposure → metrics → layers → kill/owner. Then scale the config + pipelines.

**Q58. Why pre-aggregate scorecards?**

**A:** Interactive UI at org scale can’t afford full raw joins per page view of dashboard.

**Q59. Handling late-arriving purchase events?**

**A:** Waterfall updates for T+1..T+7 attribution windows; scorecards show window completeness.

**Q60. Final deal-breakers list?**

**A:** Random per request; no mutex; sync DB assign at page QPS; unowned ramps; exposures optional; kill in hours; metrics undefined.

---

## 8. Appendices

### Appendix A — API sketch

```text
POST   /v1/layers
POST   /v1/experiments
POST   /v1/experiments/{id}/ramp { percent }
POST   /v1/experiments/{id}/kill
PUT    /v1/overrides
GET    /v1/scorecards/{experiment_id}
POST   /v1/metrics

SDK:
  evaluate(context) -> {exp_id: variant_params}
  track_exposure(exp_id, variant)
```

### Appendix B — Bucket allocation example

```text
Layer salt L, 10000 buckets
Exp A 20% → [0, 1999]
Exp B 30% → [2000, 4999]
Residual → [5000, 9999]

Within Exp A 50/50:
  vbucket = hash(unit + expA.salt) % 10000
  <5000 → control else treatment
```

### Appendix C — Exposure event schema

```json
{
  "unit_hash": "…",
  "experiment_id": "exp_123",
  "variant_id": "B",
  "config_version": 88421,
  "ts": "2026-08-06T12:01:02Z",
  "marketplace": "US",
  "request_id": "…",
  "override": false
}
```

### Appendix D — Interview checklist (45 minutes)

1. Clarify unit, exposure, mutex, ownership (5–7 min)  
2. Hash assignment + layers (8 min)  
3. Config fanout + kill (5 min)  
4. Logging + metrics pipeline (8 min)  
5. Overrides + SRM + guardrails (5 min)  
6. Scale 10×/100×/1000× (5 min)  
7. Wrap trade-offs (3 min)

### Appendix E — Ownership record

```text
experiment_id
owner_team
owner_principal
oncall_schedule
blast_radius: LOW|MED|HIGH
approvers[]
runbook_url
data_classification
```

### Appendix F — Guardrail examples

| Surface | Guardrail |
|---------|-----------|
| Search | CTR, latency p99, zero-result rate |
| Checkout | Conversion, payment errors, latency |
| Pricing | Margin, refund rate, CS contacts |
| Ads | RPM, UX complaints, policy violations |

### Appendix G — Progressive scale cheatsheet

| Scale | Eval QPS | Exposures/day | Main upgrade |
|-------|----------|---------------|--------------|
| Base | 200K | 500M | CDN config + Kafka |
| 10× | 2M | 5B | Canary publish, SRM nearline |
| 100× | 20M | 50B | Pre-agg cubes, cells |
| 1,000× | 200M | 500B | Edge compile, auto-pause |

### Appendix H — Common interviewer traps

| Trap | Solid answer |
|------|--------------|
| “Just use Redis to store assignments” | Only for overrides; not 200M QPS path |
| “Randomize page views” | Unit bias; pick customer/session deliberately |
| “Stats in the request path” | Async pipelines |
| “One global experiment list” | Layers + targeting compiled |
| “QA via changing salt” | Explicit overrides |

### Appendix I — Sample scorecard math

```text
p_c = 0.030, p_t = 0.0312, n = 5e6 per arm
lift = (p_t - p_c)/p_c = 4.0%
se ≈ sqrt(p_c(1-p_c)/n + p_t(1-p_t)/n) ≈ 0.00011
z ≈ (0.0012)/0.00011 ≈ 10.9  → highly significant
Still check guardrails and segments before ship
```

### Appendix J — Config versioning

```text
version: 88421
layers: [...]
experiments: [...]
kill_list: [exp_9, exp_41]
hash_fn: xxhash64_v1
generated_at: ...
signature: ...
```

### Appendix K — Failure injection tests

1. Publish corrupt config → canary rejects  
2. Drop 5% exposures → SRM/pipeline alert  
3. Kill experiment → version heartbeat ≤ SLO  
4. Override TTL expiry → back to hash  
5. Cross-language hash vectors  

### Appendix L — Glossary

| Term | Meaning |
|------|---------|
| Layer | Mutex traffic namespace |
| Salt | Hash namespace string |
| Ramp | % of units eligible |
| Exposure | Treatment applied/seen |
| SRM | Sample ratio mismatch |
| Guardrail | Non-primary health metric |
| Holdout | Long-run control population |

### Appendix M — Why Amazon cares

Experimentation quality directly hits **customer experience, revenue, and trust**. Interviewers listen for ownership, blast radius, and whether you protect decision quality under Prime Day load—not only for clever hashing.

### Appendix N — Minimal SDK pseudocode

```text
function evaluateAll(ctx):
  cfg = snapshot()
  out = {}
  for layer in cfg.layers:
    exp = pickExperiment(ctx.unit, layer)
    if exp is None: continue
    if overridden(ctx.unit, exp): 
      out[exp.id] = overrideVariant(...)
      continue
    if not targeted(ctx, exp): continue
    if not inRamp(ctx.unit, exp): continue
    out[exp.id] = pickVariant(ctx.unit, exp)
  return out
```

### Appendix O — Analysis contract

```text
Primary metric pre-registered
Guardrails pre-registered
Population: exposed units (default)
Window: [start, end] in marketplace local time
Overrides excluded
Bots excluded per standard filter version
Config versions included for debugging
```

### Appendix P — Capacity planning for layers

```text
Team quotas: Search 40%, Checkout 20%, Ads 20%, Residual pool 20%
Idle reclaim: experiments PAST end_date auto-pause after grace
Emergency: platform admin can force-pause non-critical to free capacity
```

### Appendix Q — Security notes

- Sign config payloads  
- Separate read vs write IAM  
- PII minimization in exposure logs  
- Employee override access logged to security lake  

### Appendix R — Related Amazon systems

| System | Interaction |
|--------|-------------|
| Feature flags | May share delivery; keep stats contracts |
| Personalization | Treat as experiment until proven |
| Metrics platform | Event schema source of truth |
| CI/CD | Dark launch treatments |

### Appendix S — One-page architecture recap

```text
Control plane (owners, layers, overrides)
    → versioned config → CDN → SDK hash assign
    → exposures + product events → lake → scorecards
Kill & ownership wrap every ramp decision
```

### Appendix T — Closing answer template

> “I’d randomize at customer_id with deterministic salts, isolate conflicts via layers, log exposures at apply-time, compute scorecards asynchronously with SRM and guardrails, and require clear owners with a fast kill switch—local eval for scale, strong control plane for safety.”

---

*End of Amazon A/B Experimentation Platform system design.*
