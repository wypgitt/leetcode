# System Design: Search Autocomplete / Typeahead (Amazon Retail)

> **Focus areas:** Prefix indexes / FST · Top-K · Hot-prefix cache · Typos · Personalization · p99 · Safety/PII · Marketplace isolation
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Latency budget; split read vs learn; deal-breaker: warehouse-on-keystroke
> **Interview theme:** Amazon SDE III / L6 — **Search & Discovery** typeahead at Amazon.com scale

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

Goal: Amazon retail **search autocomplete** returning top-K suggestions (queries, ASINs, brands, categories, deals) with ranking, light personalization, typos, safety, p99 tens of ms.

### 1.0 What this is / is not
| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Prefix → ranked suggestions | Full SERP |
| Index | Prefix structures + overlays | Warehouse scan per keystroke |
| Personalization | Re-rank small set | Heavy DNN @ 100M QPS |
| Amazon lens | Conversion, trust, fairness, cost | Academic IR alone |

### 1.1 Functional requirements
| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Suggest what? | Queries/ASINs/brands/categories/deals | Typed candidates |
| F2 | Top-K? | 8–10 UI; 30–80 compute | Diversify |
| F3 | Ranking? | Pop/CTR/CVR/fresh/dept | Offline+online |
| F4 | Personalization? | Recents+locale+affinity | Thin re-rank |
| F5 | Typos? | len≥3 | Budgeted fuzzy |
| F6 | Marketplaces? | Multi | Cells |
| F7 | Safety? | NSFW/PII/illegal | Non-bypassable |
| F8 | Freshness? | Minutes–hours | Nearline |
| F9 | Empty? | Trending | Separate lists |
| F10 | Ads? | Optional labeled | Ads path |
| F11 | OOS? | Filter/demote | Entity status |
| F12 | Analytics? | Imp/click/purchase | Async learn |

**MVP:** suggest API, FST shards, caches, fuzzy, thin personalization, safety, logs, nearline, diversify.
**Out:** LLM-only keystroke path; replace SERP; unlabeled ads.

### 1.2 NFRs
p99 < 40–50ms; 99.99% avail; millions QPS via edge; privacy k-threshold; clear ownership vs SERP/Ads.

### 1.3 Cases
Happy: `wirel` → earbuds+brand+ASIN; fuzzy; recent boost; deal nearline; dept Books.
Edges: len-1 head only; PII never indexed; OOS demote; bot storms; marketplace isolation; Prime Day.

### 1.4 Progressive scale
| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| QPS | 2M | 20M | 200M | 2B |
| Cache hit | 70% | 80% | 90% | 95%+ |
Jumps: edge → cells+client dict → on-device head.

### 1.5 Scope repeat-back
Multi-entity top-K autocomplete with sharded prefix indexes, caches, typos, thin personalization, safety, nearline freshness—distinct from SERP.

---
## 2. Back-of-the-Envelope Estimation
### 2.1 Load classes
Suggest 2M; redis hits; shard fanout; logs 50–100K/s; offline build; nearline spikes.
### 2.2 Latency budget
Edge 2–5; resolve 1–3; redis 1–5; shard 5–15; rank 3–10; safety 1–3 → **≤40–50ms p99**.
### 2.3 Memory
FST 200–800GB sharded; entity 50–150GB; redis ~10GB/region.
### 2.4 Cost
2M×1KB≈2GB/s egress → CDN mandatory. Cache hit +10% ≫ more shard CPU.

---
## 3. High-Level Design
Components: API, Edge, Redis, Prefix Shards, Fuzzy, Entity Overlay, Ranker, Personalization, Safety, Logs, Offline Builder, Nearline.
Flows: keystroke path; offline learn; nearline spike patch.
API: `GET /v1/suggest?...`
Tradeoffs: memory FST not SQL; marketplace cells; light re-rank; labeled ads; daily+nearline.

```text
score = w1*log(pop)+w2*CTR+w3*CVR+w4*fresh+w5*dept+w6*recent - diversify
```

---
## 4. Architecture Diagram
```text
App --> Edge --> API --> Redis / Shards / Fuzzy --> Merge+Rank+Safety --> JSON
                 async --> Logs --> Offline Builder --> Canary
```
Cells per marketplace; no cross-leak. Degrade: stale cache, reduce K, static blocklist.

---
## 5. Design Deep Dive
Invariants: safety in cache; marketplace isolation; last-good rollback; stale>empty.
Shard by marketplace+prefix; hot-key replica; len strategy 0/1–2/3–5/6+.
Typos budgeted; personalization thin; k-anonymity; sponsored labeled.
Metrics: p99, hit, fuzzy_rate, safety_block, empty, CTR@K, index_age.

---
## 6. Wrap-Up

### 6.1 What we designed
    Multi-entity top-K suggest with FST shards, caches, fuzzy, thin personalization, safety, offline+nearline learning.

### 6.2 Key decisions worth defending
    1. Memory FST not DB
2. Marketplace cells
3. Thin online rank
4. Safety in cache
5. Edge head / server tail
6. Labeled sponsored

### 6.3 Risks & follow-ups
    - Memory growth
- SEO spam
- Privacy vs personalization
- Sponsored policy

### 6.4 Closer
    > **Amazon Search Autocomplete**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Search Autocomplete

**Q1. Why not SERP on keystroke?**

**A:** QPS×latency×payload mismatch; need memory prefix postings.

**Q2. Spam control?**

**A:** k-threshold, trusted sessions, purchase confirm, demotion.

**Q3. Thundering herd?**

**A:** TTL stagger, coalesce, pre-warm.

**Q4. Safety in cache?**

**A:** Embed verdict+policy_version; invalidate on bump.

**Q5. Deal-breaker?**

**A:** Warehouse/SERP sync on every keystroke.

**Q6. Metrics?**

**A:** CTR@K, reformulation, p99, safety, RAM$/QPS.

**Q7. Who pages?**

**A:** Serving for p99; Science for offline quality.

**Q8. LLM replace index?**

**A:** Not sole online path at Amazon QPS.

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

### F — Capacity sketch
Redis 20×64GB; Shards 60×128GB; API 40.

### G — Closer
Scoped vs SERP; latency numbers; isolation; safety; scale; ownership.


## Deep Technical Notes — Search Autocomplete

### Index build

Daily full + hourly micro + nearline side postings; registry canary; golden sets; checksums; keep N rollbacks.

Admission: aggregate → k-threshold → PII → safety → score heaps → FST artifacts.

### Ranking

Offline base score dominates; online thin boosts only; diversify by intent cluster and entity quotas.

Sponsored: separate auction, relevance floor, organic floor, labels.

### Privacy/safety

k-anonymity; regex PII; policy packs per marketplace; fail-closed regulated categories.

Logged-out local recents; logged-in hashed affinities with TTL.

### Scale jumps

10× edge; 100× cells+client dict; 1,000× on-device head dictionaries.

Load test with real prefix distributions, not uniform alphabet.

### Ops

Explain tool internal-only; Prime Day pre-warm; kill-list for entity suppress; fuzzy shed under CPU.

Unit metric RAM$/QPS and USD per million suggests.

## Interview Cards — Search Autocomplete

### Card 1: Prefix posting maintenance

Bounded heaps size M; nearline side merge; compact on full build; never rewrite entire FST every minute.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Encoding tricks

Front-coding, quantized scores, dictionary-deduped display strings, varint entity ids.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Department ambiguity (`apple`)

Mix brand vs grocery using department context, affinity, diversity; seasonal awareness.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Abuse/bots

Trusted-session weights in offline aggregation—not only online rate limits.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Empty-result UX

Low-confidence fuzzy / browse chips; track empty_rate as CX SLO.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Voice vs keyboard

Shared dictionaries versioned independently; ASR errors ≠ typos.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Multi-AZ

Regional serve; artifact replicate; no cross-region keystroke dependency.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Canary metrics

CTR drop + empty rise → auto rollback; watch safety_block_rate too.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Entity hydration timeout

Return query-only suggestions; never miss safety.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Catalog emergency suppress

Push kill-list to edge; invalidate entity cards.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Normalization pipeline

NFKC → lower → confusables → punct → whitespace → locale tokens.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Cost narrative

Edge hit-rate and client dict move USD/million suggests—frugality with math.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Related systems

SERP, Catalog, Ads Suggest, Clickstream, Trust policy packs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Failure injection

Kill shard remap; redis flush herd limiter; bad index canary; safety FN kill-list.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Personalization modes

Logged-out / light / strict marketplace matrices.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Evolution

Transliteration; on-device head; LLM offline rewrite—not decode-per-keystroke.

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

## More Interview Q&A — Search Autocomplete

**Q1. Edge key design?**

**A:** marketplace+locale+prefix+dept+policy_version; TTL by len; SWR for head.

**Q2. Organic floor?**

**A:** ≥70–80% organic; label ads; fill organic on miss.

**Q3. PII admission?**

**A:** Regex+detectors+k-threshold+review for sensitive.

**Q4. Prime Day?**

**A:** Pre-warm; capacity reserve; freeze risky nearline.

**Q5. CJK?**

**A:** Locale tokenizers; separate segments.

**Q6. Diversity algo?**

**A:** Intent clusters + MMR + type quotas.

**Q7. Emoji/special?**

**A:** Normalize; safety on normalized.

**Q8. Cross-marketplace learn?**

**A:** Share code not indexes.

**Q9. Empty prefix personalization?**

**A:** Trending + affinities with thresholds.

**Q10. Fuzzy cost?**

**A:** Meter and shed under pressure.

**Q11. Deal-breaker reminder?**

**A:** Warehouse/SERP on keystroke.

**Q12. Price on cards?**

**A:** Omit or short TTL; PDP truth.

**Q13. Voice typing?**

**A:** Different error maps if shared with Alexa.

**Q14. Bot inflation?**

**A:** Trusted weights + purchases.

**Q15. Memory explosion?**

**A:** Prune, FST, dict dedupe, cells.

**Q16. Sponsored threshold ownership?**

**A:** Joint Ads+Suggest; Suggest enforces merge.

## Deep Technical Addenda — Search Autocomplete

### Prefix admission pipeline

Aggregate → threshold → PII → safety → score → heaps → artifact.

### Hot-key playbook

Replicate; TTL jitter; coalesce; client dict.

### Marketplace cells

Own edge/redis/shards/policy; shared control plane.

### Science loop

Logs → train → eval → registry → canary; Serving owns promotion gates.

### Worked QPS math

edge 60%, redis 50% of remainder → shard_qps=0.4M; size nodes with 2–3× headroom.

### Encoding

Front-code, quantize scores, shared string dictionary.

### Personalization privacy

Three modes; never raw phones/emails in profiles.

### Failure isolation

Optional stages deadline; exact+safety minimal path.

## Tradeoff Matrices — Search Autocomplete

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

## Operability Addenda — Search Autocomplete

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

## Worked Capacity Narrative — Search Autocomplete

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Search Autocomplete

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Search Autocomplete

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## More Interview Q&A — Search Autocomplete

**Q1. How do you explain a suggestion internally?**

**A:** Tools show prefix, cache layer, index_version, candidate sources, scores, safety verdict—authenticated internal only.

**Q2. What is the organic floor with ads?**

**A:** Policy percent of slots; always label sponsored; relevance threshold; fill organic on ads miss.

**Q3. How do you pre-warm for Prime Day?**

**A:** Top prefixes per marketplace loaded to edge/Redis; capacity reserves; freeze risky nearline experiments.

**Q4. CJK tokenization?**

**A:** Locale-specific tokenizers; separate segments; don’t reuse whitespace English assumptions.

**Q5. Suggestion diversity algorithm?**

**A:** Intent clustering + MMR + entity type quotas.

**Q6. How to handle emoji / special chars?**

**A:** Normalize; strip; keep display separately if needed; safety on normalized.

**Q7. Cross-marketplace learning?**

**A:** Careful—policy and language differ; share science code not raw indexes.

**Q8. Empty prefix personalization?**

**A:** Trending + light personalized zero-state from profile affinities with privacy thresholds.

**Q9. Cost of fuzzy at scale?**

**A:** Meter fuzzy_rate; precompute common errors; shed fuzzy under CPU pressure.

**Q10. Deal-breaker reminder?**

**A:** Warehouse/SERP on keystroke path.

**Q11. How do entity cards stay fresh for price?**

**A:** Optional; often omit live price in suggest or cache short TTL; deep link to PDP for truth.

**Q12. Voice typing typos vs keyboard?**

**A:** Different error distributions; separate rewrite maps if sharing pipelines with Alexa.

**Q13. Bot inflation of popularity?**

**A:** Trusted weights + purchase confirmation + reputation.

**Q14. Index memory explosion mitigations?**

**A:** Prune tails, FST compression, dictionary de-dupe strings, marketplace cells.

**Q15. Canary population?**

**A:** Sticky sessions by account/device hash; measure CTR/empty/p99/safety.

**Q16. Ownership of sponsored relevance threshold?**

**A:** Joint Ads+Suggest policy; Suggest enforces merge; Ads owns auction.

## Deep Technical Addenda — Search Autocomplete

### Prefix admission pipeline

Aggregate → threshold → PII detect → safety prefilter → score → heap postings → artifact. Rare sensitive categories to human review.

### Hot-key operational playbook

Detect first-char overload; replicate shards; shorten edge TTL jitter; coalescing; optional client dict push for those prefixes.

### Multi-tenant marketplace cells

Cell brings its own edge config, Redis, shards, policy pack. No candidate cross-read. Shared control plane for deploy tooling.

### Science loop

Logs → training → offline eval → registry → canary. Suggest Serving owns promotion gates on latency/safety.

## Tradeoff Matrices — Search Autocomplete

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

## Operability Addenda — Search Autocomplete

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

## Worked Capacity Narrative — Search Autocomplete

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Search Autocomplete

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Search Autocomplete

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Search Autocomplete
### S1. Latency isolation

Treat fuzzy, personalization, entity hydration, and ads as deadline-bound optional stages. Exact prefix + safety is the minimal viable path. Missed optional stages must not 5xx the search box.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Index artifact science

Artifacts carry marketplace, shard_map, checksum, policy_version, and created_at. Promotion is registry-driven. Golden prefix sets gate canaries. Keep N rollback versions always.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Marketplace law packs

Safety and product rules differ by marketplace. Packs select blocklists and adult rules. Never mix JP and US postings in one serve cell.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Head/tail economics

Head prefixes dominate QPS and belong at edge/client. Tail needs shards but lower QPS. Design capacity around head; design relevance around tail.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Learning loop integrity

Bots inflate popularity. Use trusted session weights and purchase confirmation in offline aggregation. Sample impressions; keep clicks/purchases denser.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Sponsored honesty

Labeled slots, organic floor, relevance threshold, ads timeout → organic fill. Suggest owns merge policy; Ads owns auction.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Operational excellence

Dashboards for p99, hit rates, empty_rate, safety_block_rate, index_age, RAM$/QPS. Prime Day runbooks pre-warm and freeze risky nearline.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Privacy thresholds

k-anonymity before index admission; PII detectors; no rare personal strings as suggestions; dual explain views for internal tools.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — Search Autocomplete

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Prime Day | Pre-warm, shed fuzzy, freeze risky nearline | Preserve trust/UX | Postmortem + guardrail |
| Bad canary | Auto rollback index_version | Preserve trust/UX | Postmortem + guardrail |
| Safety FN | Edge kill-list + invalidate | Preserve trust/UX | Postmortem + guardrail |
| Redis flush | Coalesce; edge+shards serve | Preserve trust/UX | Postmortem + guardrail |
| Catalog suppress | Kill-list bypass TTL | Preserve trust/UX | Postmortem + guardrail |
| Hot prefix `a` | Replica shards + client dict | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — Search Autocomplete

**RQ1. Why does 'Latency isolation' matter in an L6 interview?**

**A:** Treat fuzzy, personalization, entity hydration, and ads as deadline-bound optional stages. Exact prefix + safety is the minimal viable path. Missed optional stages must not 5xx the search box. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Latency isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Latency isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Index artifact science' matter in an L6 interview?**

**A:** Artifacts carry marketplace, shard_map, checksum, policy_version, and created_at. Promotion is registry-driven. Golden prefix sets gate canaries. Keep N rollback versions always. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Index artifact science' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Index artifact science' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Marketplace law packs' matter in an L6 interview?**

**A:** Safety and product rules differ by marketplace. Packs select blocklists and adult rules. Never mix JP and US postings in one serve cell. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Marketplace law packs' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Marketplace law packs' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Head/tail economics' matter in an L6 interview?**

**A:** Head prefixes dominate QPS and belong at edge/client. Tail needs shards but lower QPS. Design capacity around head; design relevance around tail. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Head/tail economics' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Head/tail economics' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Learning loop integrity' matter in an L6 interview?**

**A:** Bots inflate popularity. Use trusted session weights and purchase confirmation in offline aggregation. Sample impressions; keep clicks/purchases denser. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Learning loop integrity' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Learning loop integrity' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Sponsored honesty' matter in an L6 interview?**

**A:** Labeled slots, organic floor, relevance threshold, ads timeout → organic fill. Suggest owns merge policy; Ads owns auction. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Sponsored honesty' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Sponsored honesty' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Operational excellence' matter in an L6 interview?**

**A:** Dashboards for p99, hit rates, empty_rate, safety_block_rate, index_age, RAM$/QPS. Prime Day runbooks pre-warm and freeze risky nearline. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Operational excellence' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Operational excellence' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Privacy thresholds' matter in an L6 interview?**

**A:** k-anonymity before index admission; PII detectors; no rare personal strings as suggestions; dual explain views for internal tools. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Privacy thresholds' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Privacy thresholds' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Search Autocomplete

### Walkthrough beat 1

In beat 1, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through Search Autocomplete: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Search Autocomplete

- [ ] Can explain **Latency isolation** with numbers and a deal-breaker
- [ ] Can explain **Index artifact science** with numbers and a deal-breaker
- [ ] Can explain **Marketplace law packs** with numbers and a deal-breaker
- [ ] Can explain **Head/tail economics** with numbers and a deal-breaker
- [ ] Can explain **Learning loop integrity** with numbers and a deal-breaker
- [ ] Can explain **Sponsored honesty** with numbers and a deal-breaker
- [ ] Can explain **Operational excellence** with numbers and a deal-breaker
- [ ] Can explain **Privacy thresholds** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Prime Day**
- [ ] Has a 30-second runbook for **Bad canary**
- [ ] Has a 30-second runbook for **Safety FN**
- [ ] Has a 30-second runbook for **Redis flush**
- [ ] Has a 30-second runbook for **Catalog suppress**
- [ ] Has a 30-second runbook for **Hot prefix `a`**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

*End of document — Amazon Search Autocomplete / Typeahead (SDE III)*
