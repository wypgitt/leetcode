# System Design: Book Review Aggregation System

> **Focus areas:** Ingest reviews · Identity resolve · Ranking · Spam/fake · Ratings aggregates · Search · Provenance · Multi-source
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Multi-source book reviews aggregation & trust ranking (Amazon-flavored catalog adjacency)**

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

Goal: design a **book review aggregation system**—ingest reviews from multiple sources (owned + partners + user), resolve book identity, compute trustworthy ratings, rank/filter spam, and serve product/review pages at progressive catalog scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Aggregate, trust-score, serve reviews | Full bookstore checkout/OMS |
| Catalog | Book identity resolution | Entire Google Books replacement alone |
| Trust | Spam/fake detection hooks | Law enforcement system |
| Amazon lens | Customer trust, abuse, ownership | Naive average stars only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Sources? | 1P reviews, partners, imports | Ingest adapters |
| F2 | Identity? | ISBN/ASIN/work_id resolve | Entity resolution |
| F3 | Ratings? | Aggregates with Bayesian/trust weights | Agg service |
| F4 | Ranking? | Helpfulness, recency, trust | Ranker |
| F5 | Spam? | Fake review detection signals | Abuse pipeline |
| F6 | Moderation? | Report/remove/appeal | Mod workflows |
| F7 | Serve? | PDP review modules, APIs | Read models/CDN |
| F8 | Write? | Authenticated submit review | Write path |
| F9 | Votes? | Helpful votes | Vote service |
| F10 | Provenance? | Show source; license terms | Attribution |
| F11 | Editions? | Hardcover/paperback same work? | Work vs edition |
| F12 | SLA? | Freshness hours; trust > vanity stars | SLOs |

**MVP scope:**

1. Ingest+store reviews with source provenance.
2. Resolve to work/edition IDs.
3. Compute rating aggregates.
4. Serve top reviews ranked.
5. User submit + edit.
6. Helpful votes.
7. Basic spam signals + quarantine.
8. Ops: abuse dashboards.

**Out of MVP:** full social network, perfect LLM review generation (no—don't), global publisher contracts all signed, active-active conflict-free edit without CRDT story.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Read PDP reviews | p99 < 200–300ms |
| N2 | Write accept | p99 < 500ms |
| N3 | Agg freshness | minutes–hours |
| N4 | Abuse reaction | quarantine fast |
| N5 | Durability | No lost accepted reviews |
| N6 | Attribution | License-safe display |
| N7 | Peak | Bestseller / Harry Potter spikes |
| N8 | Consistency | Read-your-writes for author edits eventual OK for aggs |

### 1.3 Cases

**Happy:** Submit/ingest→resolve book→visible→votes→agg updates.
**Edges:** ISBN collide; brigading; purchased-verified forge; duplicate article spam; partner feed retract; edition mismatch; celebrity bestseller thundering herd; moderation false positive.

| Case | Behavior |
|------|----------|
| Brigade votes | Rate-limit + trust graph |
| Fake burst | Quarantine source/cohort |
| ISBN ambiguity | Human/rules resolve work |
| Partner retract | Takedown pipeline |
| Dup content | SimHash/fingerprint |
| Bestseller spike | Cache+partition hot work_id |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Works in catalog | 1M | 10M | 100M | 1B |
| Reviews stored | 50M | 500M | 5B | 50B |
| Ingest / day | 100K | 1M | 10M | 100M |
| PDP QPS reviews | 1K | 10K | 100K | 1M |
| Writes / day | 50K | 500K | 5M | 50M |
| Spam checks / day | 100K | 1M | 10M | 100M |
| Sources | 5 | 20 | 50 | 100 |
| Languages | 1 | 5 | 20 | 50 |

**Jumps:** 10×=multi-source platform; 100×=abuse ML + hot-key caching; 1,000×=global catalog cells + licensing complexity.

### 1.5 Scope repeat-back

> Review aggregation with identity resolution, trust-weighted ratings, ranking, abuse controls, and fast PDP reads—trustworthy stars over vanity averages—scaled by work partitions.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
PDP reads dominate writes by 100–1000×
Aggs update async from review events
```

### 2.2 Storage

```text
Review body 1–5KB avg; billions → multi-TB
Object/CDN for media; search index separate
```

### 2.3 Latency

```text
Read: edge cache → review read model → fallback
```

### 2.4 Bottlenecks

(1) hot work_id (2) spam compute (3) identity resolution (4) search index lag (5) partner feed storms.

### 2.5 Cost

Don't re-embed all reviews constantly; cache top-N; frugal abuse features.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Ingest/Write | Accept reviews | Strong per review_id |
| Identity | Work/edition map | Eventually converging |
| Trust/Abuse | Scores/quarantine | Eventually + fast quarantine |
| Aggregates | Stars/counts | Eventual from events |
| Serve | PDP read models | Cached eventual |

**Deal-breaker:** naive average of all raw stars including known spam cohorts—trust destruction.

### 3.2 Components

1. **Review Write API** — submit/edit
2. **Ingest Adapters** — partners/imports
3. **Identity Resolver** — ISBN/ASIN/work
4. **Review Store** — SoT bodies
5. **Abuse/Fake Pipeline** — scores
6. **Aggregation Service** — ratings
7. **Ranking Service** — top-N
8. **Vote Service** — helpful
9. **Moderation Tools** — queues
10. **Read Model/CDN** — PDP
11. **Search Index** — find reviews
12. **Provenance/License** — display rules

### 3.3 Core API (sketch)

```text
POST /v1/reviews {work_id|isbn, rating, text, idempotency_key}
GET /v1/works/{work_id}/reviews?sort=&cursor=
GET /v1/works/{work_id}/aggregate
POST /v1/reviews/{id}/votes
POST /v1/ingest/partner/{source} batch
POST /v1/moderation/decisions
```

### 3.4 State machine

```text
REVIEW: RECEIVED → PUBLISHED → EDITED → REMOVED
           RECEIVED → QUARANTINED → PUBLISHED/REMOVED
AGG: stream updates from publish/remove/vote events
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Work vs edition ratings | Show both; default work with edition filter | UX |
| Sync vs async agg | Async + cache | Scale |
| Trust weights | Verified purchase + age + abuse score | Quality |
| Partner content | License gates before serve | Legal |
| Search | Secondary index | Freshness trade |

---

## 4. Architecture Diagram

```text
[Users/Partners] -> Write/Ingest -> Identity Resolver -> Review Store
                                         |
                                         v
                              Abuse Pipeline -> Quarantine
                                         |
                              Agg + Ranker -> Read Models/CDN -> PDP
                                         ^
                                      Votes/Moderation
```

### 4.1 Primary sequence

```text
Resolve identity to work_id
Persist review RECEIVED
Abuse score; auto-publish or quarantine
Emit event → update aggregates + top-N
Serve from read model with provenance
```

### 4.2 Isolation cell

```text
Partition by work_id for aggs/hot reads
User writes by user_id shard
Regional serve cells; licensing rules
Hot bestsellers isolated cache layers
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Published reviews have provenance/source.
2. Aggregates rebuildable from published set.
3. Quarantine excludes from public agg.
4. Idempotent partner ingest keys.
5. Edits versioned; display latest policy.
6. License-expired sources takedown.
7. Vote fraud rate-limited.
8. Verified attributes only if attested.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG reviews + cron aggs |
| 10× | Event stream aggs; CDN |
| 100× | Abuse ML; hot-work cache; search |
| 1000× | Global catalog; multi-license; extreme bestsellers |

### 5.3 Maintainability

- Identity rules as data.
- Abuse model canary.
- Agg rebuild tool.
- Partner contract tests.
- Ranking offline eval.

### 5.4 Progressive scale

**1×:** 1P reviews simple avg.
**10×:** Partners+provenance.
**100×:** Trust weights+abuse.
**1000×:** Global works graph; sophisticated ranking.

### 5.6 Identity resolution

Keys: ISBN13, ASIN, title+author fuzzy, publisher IDs. Merge to work_id; keep edition_id. Manual queue for conflicts; never silently merge distinct works.

### 5.7 Trust-weighted aggregates

weight = f(verified, tenure, abuse_score, helpful). Bayesian prior for low-N. Rebuildable from events—not only cached float.

### 5.8 Fake review bursts

Graph features: shared devices, burst timing, similar text. Quarantine cohort fast; human mod for borderline.

### 5.9 Hot bestseller

Cache top-N + agg; single-flight; partition; static fallback snippet if origin sick.

### 5.10 Partner retract

Tombstones propagate to store, index, CDN purge; agg rebuild delta.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Count quarantined in stars | Trust fail |
| No provenance | Legal/trust |
| Silent work merge wrong | Corrupt catalog |
| Uncached hot work origin crush | Outage |
| Unverified 'verified purchase' | Fraud |
| Irreversible hard delete without tombstone for licensed content | Can't prove takedown |

---

## 6. Wrap-Up

### 6.1 Designed

Work-partitioned review aggregation: multi-source ingest, identity resolution, abuse quarantine, trust-weighted aggs, ranked serve with provenance.

### 6.2 Decisions to defend

1. Work vs edition model
2. Async rebuildable aggs
3. Trust weights not raw avg
4. Quarantine plane
5. Provenance/license gates
6. Hot-work caching
7. Idempotent ingest
8. Versioned edits

### 6.3 Risks

- Identity errors
- Abuse arms race
- Partner license
- Cache staleness
- Bestseller storms

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope agg vs full store |
| 5–15 | Model work/review store |
| 15–25 | Agg+ranking |
| 25–35 | Abuse+identity |
| 35–45 | Serve scale+partners |

### 6.5 Closer

> **Book Review Aggregation System**: trust-weighted aggregates, identity discipline, abuse quarantine, provenance-safe serve, progressive catalog scale—never vanity stars.

---

## 7. Deeper / Related Interview Questions

### 7.1 Identity

**Q: Same book different ISBN country?**
A: Often same work; edition differs.

**Q: Audiobook vs print?**
A: Same work optional; product policy.

**Q: Author disambiguation?**
A: Person entities separate.

### 7.2 Aggregates

**Q: Median vs mean?**
A: Mean with trust weights + distribution histogram.

**Q: Recency decay?**
A: Optional for ranking not always for avg.

**Q: Low sample?**
A: Show N + prior; suppress precise avg.

### 7.3 Abuse

**Q: Review bombing?**
A: Velocity quarantine; purchase-verified boost.

**Q: AI spam text?**
A: Classifiers+fingerprint; evolving.

### 7.4 Serve

**Q: Pagination?**
A: Cursor on rank key.

**Q: Personalization?**
A: Light rerank; keep trust.

**Q: CDN purge?**
A: On remove/edit.

### 7.5 Partners

**Q: Conflicting licenses?**
A: Most restrictive display rule.

**Q: Attribution UI?**
A: Required fields.

### 7.6 Traps

**Q: Raw average only**
A: Weak

**Q: Ignore identity**
A: Corrupt

**Q: Generate fake reviews with LLM**
A: Unethical/policy fail

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| Spam precision/recall | Trust |
| Agg rebuild lag | Freshness |
| PDP p99 | UX |
| Quarantine time-to-detect | Abuse |
| Identity conflict rate | Catalog health |
| Partner takedown lag | Legal |
| Helpful vote fraud rate | Integrity |
| Hot work error rate | Scale |

### 7.8 Ownership

**Q: Who pages for review-bomb?**
A: Abuse + Reviews IC.

**Q: Who pages for wrong book merge?**
A: Identity/Catalog IC.

### 7.9 Progressive drill

**10×:** multi-source+CDN
**100×:** abuse ML+hot cache
**1,000×:** global license cells

---

## 8. Appendices

### 8.1 Schema sketches

```text
works(work_id, title, authors...)
editions(edition_id, work_id, isbn13, asin)
reviews(review_id, work_id, edition_id, user_or_source, rating, body, state, provenance, version)
review_events(event_id, review_id, type, ts)
aggregates(work_id, rating_sum_weighted, weight_total, count, hist_json, version)
votes(review_id, user_id, value) UNIQUE(user,review)
abuse_scores(review_id, score, reasons)
identity_conflicts(id, keys, state)
partner_tombstones(source_review_key)
```

### 8.2 API checklist

- [ ] Review create/edit
- [ ] Partner ingest
- [ ] Aggregate get
- [ ] Reviews list
- [ ] Vote
- [ ] Moderation decision
- [ ] Takedown
- [ ] Identity resolve

### 8.3 Oncall checklist

- [ ] Abuse burst
- [ ] Hot work 5xx
- [ ] Agg lag
- [ ] Partner feed fail
- [ ] Identity conflict spike
- [ ] CDN purge lag
- [ ] Search lag

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Work | Canonical book entity |
| Edition | ISBN/format instance |
| Provenance | Source/attribution |
| Quarantine | Hold from public |
| Trust weight | Agg coefficient |
| PDP | Product detail page |
| Brigading | Coordinated votes/reviews |

### 8.5 Deal-breaker one-liners

- Raw avg including spam
- No provenance
- Silent bad merges
- Verified badge without attestation

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Review store | Reviews Platform |
| Identity | Catalog |
| Abuse | Trust&Safety |
| Aggregates | Reviews Platform |
| Serve/CDN | Storefront |
| Partners | Content Partnerships |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | PG+cron |
| 10× | Kafka aggs+CDN |
| 100× | Abuse fleet+hot cache |
| 1000× | Regional catalog cells |

### 8.8 Failure injection

1. Bomb attack — quarantine cohort.
2. Bad merge — split tool.
3. Partner retract — tombstone purge.
4. Cache stampede — single-flight.
5. Agg drift — rebuild.
6. Search lag — serve without search sort.

---

## Interview Traps

**Trap: Only star average**
Signal: Weak L6

**Trap: Ignore legal provenance**
Signal: Risk

**Trap: LLM-generate reviews**
Signal: Policy fail

**Trap: Global unsharded hot table**
Signal: Outage

---

## Flash Cards

### Card 1: Work vs edition

Model both.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Reviews Platform

### Card 2: Trust weights

Not raw avg.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Catalog

### Card 3: Quarantine

Fast abuse.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Trust&Safety

### Card 4: Rebuildable agg

From events.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Storefront

### Card 5: Provenance

License-safe.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Partnerships

### Card 6: Hot work cache

Bestseller.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Reviews Platform

### Card 7: Idempotent ingest

Partners.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Catalog

### Card 8: Identity conflicts

Human queue.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Trust&Safety

### Card 9: Vote fraud limits

Brigades.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Storefront

### Card 10: Tombstones

Takedowns.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Partnerships

### Card 11: Verified attestation

Real only.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Reviews Platform

### Card 12: CDN top-N

PDP p99.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Catalog

### Card 13: Ranking eval

Offline.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Trust&Safety

### Card 14: Deal-breaker

Spam in stars.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Storefront

### Card 15: Metrics

Detect time; PDP p99.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Partnerships

### Card 16: Harry Potter day

Game day.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Reviews Platform

---

## Scenario Runbooks

### R1 — Review bomb
Quarantine; freeze votes; forensic features; restore ranking.

### R2 — Wrong merge
Unmerge; rebuild aggs; fix rules.

### R3 — Partner takedown SLA
Tombstone; purge CDN/index; confirm.

### R4 — Bestseller outage
Expand cache; shed sorts; static fallback.

### R5 — Agg drift
Halt stream; rebuild; resume.

---

## Extended Rapid Q&A

**Q: Star distribution?**
A: Store histogram.

**Q: Photos in reviews?**
A: Object store+moderation.

**Q: Translated reviews?**
A: Language field; optional MT with label.

**Q: Author responses?**
A: Separate entity threaded.

**Q: Incentivized reviews?**
A: Disclose+downrank/policy.

**Q: Why Bayesian prior?**
A: Stabilize low-N.

**Q: First widget?**
A: Bomb detect + hot error.

**Q: GraphQL vs REST?**
A: Either; cache keys matter.

**Q: Delete account?**
A: Anonymize per policy.

**Q: Search typos?**
A: Edition resolver fuzzy carefully.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Simple SQL AVG(*) | Spam wins |
| No identity resolution | Fragmented |
| Sync recompute all on read | Won't scale |
| Drop provenance | Legal risk |
| Client-only ranking | Abuse |

---

## LLD Touch (optional)

Classes: `Work`, `Edition`, `Review`, `ReviewVersion`, `AbuseScore`, `Aggregate`, `Vote`, `Provenance`, `Tombstone`. Patterns: Event-sourced aggs, CQRS read models, Quarantine state machine, Entity resolution, Cache single-flight.

---

## 60-second Narrative

"We resolve reviews to works/editions, store them with provenance, and keep spam out of public aggregates via quarantine and trust weights. Aggregates are rebuildable from events; PDPs read from cached rank lists. Partners can retract via tombstones. Hot bestsellers get isolation and cache. Success is trustworthy ratings customers believe—not the highest vanity average."

---

## Extra Depth: Helpfulness Ranking

Wilson score + trust; fight brigades.

## Extra Depth: Multilingual

Language detect; serve locale preferences.

## Extra Depth: Offline Eval

Abuse precision; ranking nDCG vs human.

## Extra Depth: Catalog Hooks

ASIN mapping for Amazon-like retail.

## Extra Depth: Observability

Wide events; redact PII in bodies for logs.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How show distribution of stars?**
A: Histogram in aggregate record; UI bars.

**Q: Author reply moderation?**
A: Separate entity; same abuse pipeline.

**Q: Incentivized review disclosure?**
A: Mandatory tag; downrank or exclude from agg per policy.

**Q: Translation labeling?**
A: Show original language + translated mark.

**Q: Why not let publishers delete critical reviews?**
A: Only policy/legal takedown; not vanity deletes.

**Q: ASIN vs ISBN mapping miss?**
A: Identity conflict queue; don't force.

**Q: Helpful vote Wilson score?**
A: Common ranking component; still anti-brigade.

**Q: Quarantine false positive appeal?**
A: Mod queue SLA; restore events rebuild agg.

**Q: CDN stale after remove?**
A: Versioned keys + purge; TTL short for hot.

**Q: Partner attribution requirements?**
A: Provenance fields mandatory before PUBLISHED.

**Q: Review photos virus/CSAM?**
A: Scan pipeline; block.

**Q: GraphQL complexity attacks?**
A: Query cost limits; prefer BFF for PDP.

**Q: Cold start new book?**
A: Prior + show N; suppress over-precise avg.

**Q: Multi-country storefront rules?**
A: Regional serve cells + license.

**Q: SEV for review bomb on bestseller?**
A: Abuse+Reviews IC; quarantine; public comms if needed.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT reviews | Review store |
| Stars | Trust-weighted rebuildable |
| Abuse | Quarantine fast |
| Kill | Raw avg with spam |

---

*End of Book Review Aggregation System design notes (Amazon SDE III prep).*


---

## Extra Depth Pack (Interview Expansion)

### E1: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E2: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E3: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E4: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E5: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E6: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E7: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

