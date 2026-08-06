# System Design: URL Connectivity / Link Graph

> **Focus areas:** Crawl/ingest · Graph storage · Connectivity queries · Ranking signals · Freshness · Politeness · Spam · Multi-tier serving
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **URL connectivity / web link-graph** — store and query the web's edges

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-q&a)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design a system that ingests URL→URL links (crawl or feeds), stores a massive directed graph, and answers connectivity / neighborhood / path-ish queries with freshness and spam controls.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Link-graph ingest+query | Full Google search ranking |
| Query | Neighbors, reachability approx, degree | Exact APSP |
| Amazon lens | Cost, abuse, operational ownership | Research paper only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Ingest? | Crawl edges + sitemap/feeds | Idempotent upserts |
| F2 | Nodes/edges? | URL ids + directed links | Canonicalization |
| F3 | Queries? | Out/in neighbors; k-hop; connectivity approx | Latency classes |
| F4 | Freshness? | Recrawl priority | Tiered |
| F5 | Spam? | Link spam detect | Trust layers |
| F6 | Politeness? | Per-host budgets | Crawl ethics |
| F7 | Serving? | Online API + batch analytics | Split planes |
| F8 | IDs? | Stable URL hashes | Collision policy |
| F9 | Deletes? | robots/takedown | Honored |
| F10 | Ranking signals? | Degree/PageRank-ish batch | Offline |
| F11 | Multi-tenant? | Internal consumers | Quotas |
| F12 | Geo? | Regional crawl cells | Legal |

**MVP scope:**

1. Canonicalize URLs
2. Ingest edges upsert
3. Get out-neighbors
4. Get in-neighbors sample
5. Degree stats
6. Batch PageRank job
7. Politeness crawl budget
8. Spam score field
9. Online cache hot nodes

**Out of MVP:** Exact shortest path on full web; Realtime global PageRank each edge; Store full HTML always.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Neighbor query | p99<50–100ms hot |
| N2 | Ingest lag | minutes–hours tiered |
| N3 | Scale | 100B+ edges progressive |
| N4 | Politeness | Hard host caps |
| N5 | Avail | 99.9% serving |
| N6 | Cost | Store compressed CSR/adj |
| N7 | Spam | Queryable filter |
| N8 | Legal | robots/takedown SLO |

### 1.3 Cases

**Happy:** crawl discovers links→canonicalize→upsert edges→API out-neighbors; nightly PR update.
**Edges:** redirect loops; explosion fanout; spam farms; host overload; ID collision; stale edges; legal removal.

| Case | Behavior |
|------|----------|
| Duplicate request | Idempotent key returns same result |
| Partial failure mid-path | Compensate or retry with fencing/CAS |
| Hot partition / noisy neighbor | Shuffle shard + fair-share quotas |
| Region / AZ loss | Cell failover; degrade non-critical |
| Clock skew | Server-side truth; opaque tokens |
| Poison input | Quarantine/DLQ; never silent drop of accepted work |
| Authz miss | Fail closed; audit |
| Traffic surge 10× | Shed by priority; preserve SLO class |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Nodes | 10B | 100B | 1T | 10T |
| Edges | 100B | 1T | 10T | 100T |
| Ingest edges/s | 50K | 500K | 5M | 50M |
| Query QPS | 10K | 100K | 1M | 10M |
| Hosts | 100M | 1B | 10B | — |
| Fresh tier A pages | 100M | 1B | 10B | 100B |

**Jumps:** 10× partitioned graph+cache; 100× cells+approx indexes; 1,000× specialized graph HW/tiering.

### 1.5 Scope repeat-back

> Web-scale link graph ingest with canonicalization, politeness, spam signals, neighbor/connectivity APIs, batch centrality.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Edge size

```text
~16–32B compressed ≈ PBs at 1T edges
```

### 2.2 QPS

```text
Hot hubs need caching
```

### 2.3 Crawl

```text
Host QPS budgets dominate discovery
```

### 2.4 PR

```text
Periodic sparse mat-vec jobs
```

### 2.X Bottlenecks

(1) Hot keys/partitions (2) synchronous fan-out (3) durable write path (4) auth/token validation (5) downstream blast radius (6) not abstract QPS alone.

### 2.Y Cost / frugality

Prefer cheaper read paths over linear DB growth; measure unit cost per successful customer action; sample observability firehoses.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Crawl/ingest | Discovery | Best-effort+budgets |
| Graph store | Adjacency | Partitioned |
| Online serve | Neighbor APIs | Cached |
| Batch analytics | PR/spam | Offline |
| Policy | robots/legal | Strong |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Canonicalizer** — URL normalize
2. **Crawl frontier** — Priorities
3. **Fetcher** — Polite GET
4. **Extractor** — Links
5. **Graph writer** — Upsert edges
6. **Graph store** — Sharded adj
7. **Serving API** — Neighbors
8. **Cache** — Hot hubs
9. **Spam scorer** — Batch/online
10. **PR pipeline** — Batch
11. **Takedown** — Removals
12. **Metrics** — Host budgets

### 3.3 API sketch

```text
POST /v1/edges/bulk
GET /v1/nodes/{id}/out?limit=
GET /v1/nodes/{id}/in?limit=
GET /v1/connectivity/approx?from&to
POST /v1/takedown
```

### 3.4 State machine

```text
URL: DISCOVERED→FETCHED→EXTRACTED→INDEXED→STALE
Edge: UPSERT active; soft-delete on takedown
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Exact path | Approx connectivity | Cost |
| Store HTML | Links+meta | Cost |
| In-edges | Sampled for hubs | Memory |
| Freshness | Tiered recrawl | Politeness |
| Spam | Offline+online signals | Recall/precision |

---

## 4. Architecture Diagram

```text
Frontier->Fetcher->Extractor->Canonicalize->Graph Writer->Sharded Store
API->Cache->Store; Batch PR/Spam->Store; Policy/robots->Frontier
```

### 4.1 Ingest

```text
Fetch→extract→canon→upsert out-adj + sampled in
```

### 4.2 Query

```text
Authz→cache→shard fan-in merge
```

### 4.3 Approx connect

```text
Bloom/landmark/label prop—not full BFS
```

### 4.N Cell / blast-radius model

```text
Each cell = failure domain (AZ-set or region slice)
No synchronous cross-cell locks on hot path
Control plane pushes config; data plane serves locally
Shuffle sharding for multi-tenant isolation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Canon before write
2. Host budgets never exceeded intentionally
3. Takedown removes serve path
4. Spam filter available to callers
5. Idempotent edge upsert
6. Hot hub queries bounded
7. Batch jobs don't block online
8. PII not stored from pages unnecessarily

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Few shards + Redis cache |
| 10× | CSR partitions + frontier cells |
| 100× | Approx indexes + multi-region crawl |
| 1000× | Specialized graph serving + aggressive tiering |

### 5.3 Maintainability

- Canon rule versioning
- Replay extractors
- Shadow spam models
- Shard rebalancer

### 5.4 Progressive scale narrative

**1×:** Single DC graph
**10×:** Partition+cache
**100×:** Global crawl cells
**1000×:** Approx connectivity products

### 5.5 Canonicalization

Scheme/host/slash/redirect policy; stable IDs.

### 5.6 Hub handling

Don't materialize all in-edges; samples+sketches.

### 5.7 Partitioning

By node id hash; minimize cut via host locality optional.

### 5.8 Politeness

Per-host token buckets global.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| Full BFS online | Meltdown |
| Ignore robots | Legal SEV |
| Unbounded in-edges hubs | OOM |
| No canon | Dup explosion |
| Exact PR each write | Impossible $ |
| Crawl without budget | Ban/DoS |

---

## 6. Wrap-Up

### 6.1 Designed

Link-graph platform: polite ingest, canonical IDs, sharded adjacency, bounded neighbor APIs, batch centrality/spam, legal removals.

### 6.2 Decisions to defend

1. Canon IDs
2. Sharded adj lists
3. Bounded/sampled in-edges
4. Tiered freshness
5. Approx connectivity
6. Batch PR
7. Host politeness
8. Takedown path

### 6.3 Risks

- Spam pollution
- Shard imbalance
- Extractor bugs
- Legal latency
- Cost of edges

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Query scope |
| 5–15 | Scale math |
| 15–25 | Store+canon |
| 25–35 | Crawl/spam/API |
| 35–45 | Approx+cells |

### 6.5 Closer

> **URL Connectivity / Link Graph**: polite ingest, canonical graph, bounded queries, batch signals, legal deletes—honest about exact path impossibility at web scale.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Canon rules?

Stable URL IDs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: In-edges at hubs?

Sample/sketch.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Connectivity API?

Approx not APSP.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Politeness?

Per-host budgets.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Spam farms?

Signals+filters.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Partition key?

Node hash ± host.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Freshness tiers?

Priority frontier.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: robots.txt?

Honored.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Redirects?

Canon policy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Storage format?

Compressed CSR/adj.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Online PR?

No; batch.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Multi-region?

Crawl cells; query regional.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Who pages?

Crawl vs graph serve.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: HTML store?

Optional separate.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

Online full BFS.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

$/B edges stored+scanned.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

---

## 8. Appendices

### A. Glossary

| Term | Meaning |
|------|---------|
| Cell | Isolated failure domain for blast-radius control |
| Fence / fencing token | Invalidates stale writers after lease steal |
| Idempotency key | Client key making retries safe |
| Outbox | Durable event publish coupled to DB commit |
| Shuffle sharding | Map tenants to overlapping server subsets |
| SLO / error budget | Reliability contract; burn rate drives decisions |
| Unit cost | $ per successful customer action |
| DLQ | Dead-letter queue for poison / exhausted retries |
| Control vs data plane | Config/orchestration vs hot-path serving |
| Progressive scale | Explicit 10×/100×/1,000× architecture jumps |

### B. Ownership matrix

| Concern | Owns | Pages when |
|---------|------|------------|
| Hot-path latency/errors | Serving team | p99 / 5xx burn |
| Durability / data loss risk | Storage/data team | RPO/RTO alarms |
| Abuse / security | Trust & safety / AppSec | exploit or abuse spike |
| Cost regression | Serving + FinOps | unit-cost burn |
| Downstream dependency | Owning service | dependency SEV |

### C. Metrics that matter

- Success rate by criticality class
- Latency histograms (p50/p90/p99) on customer-visible path
- Queue lag / backlog age
- Retry / duplicate attempt rate
- Cache hit ratio where applicable
- Error budget burn rate
- Unit cost trend
- Cell imbalance / hot partition indicators

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope & non-goals |
| 5–12 | Back-of-envelope math |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive invariants & failures |
| 35–45 | Progressive scale, ownership, SEV |

---

## 10. Operability

### Golden signals

ingest edges/s, query p99, cache hit, host budget util, spam rate, takedown lag, store bytes/edge, frontier lag

### Rollback ladder

pause ingest→revert extractor→disable approx index→read-only serve

### Kill switches

stop crawl host; disable query type; filter spam hard; emergency takedown

### Security / privacy

robots/legal; no credentialed crawl abuse; rate limits API; PII minimization

### Cost worksheet

Storage+scan IO dominate; compress; tier cold edges; sample hubs

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Crawl infra, legal, spam/trust, serving consumers (search), capacity

---

## More Interview Q&A — URL Connectivity / Link Graph

**Q1. Neo4j?**

**A:** Unlikely at web scale; custom sharded.

**Q2. BFS depth?**

**A:** Cap k small online.

**Q3. WWW vs intranet?**

**A:** Same design; smaller.

**Q4. JavaScript links?**

**A:** Render tier costly optional.

**Q5. sitemaps?**

**A:** Frontier source.

**Q6. Change feeds?**

**A:** Priority boost.

**Q7. HTTPS upgrades?**

**A:** Canon.

**Q8. IPv6 hosts?**

**A:** Budget keys include.

**Q9. GraphQL?**

**A:** Not needed.

**Q10. What not?**

**A:** Exact all-pairs paths.

**Q11. How do you canary this?**

**A:** Percent or cell-scoped; auto-rollback on SLO burn.

**Q12. What is the SEV1 customer line?**

**A:** State impact, blast radius, mitigation, next update ETA.

**Q13. How do you test failure?**

**A:** Game day: kill AZ, dependency timeout, duplicate inject.

**Q14. What is read-your-write strategy?**

**A:** Sticky session, sync path, or version tokens as needed.

**Q15. How do you bound cardinality?**

**A:** Allowlists, quotas, deliberate metric labels.

**Q16. What is the degrade mode?**

**A:** Shed noncritical; preserve integrity/security path.

**Q17. How do you handle poison?**

**A:** Quarantine/DLQ; alert owner; capped redrive.

**Q18. What is multi-region story?**

**A:** Home cell writes; regional reads/failover documented.

**Q19. How do you prevent noisy neighbors?**

**A:** Quotas + shuffle sharding + fair queues.

**Q20. What would you not build in MVP?**

**A:** Exact shortest path on full web.

---

## Worked Capacity Narrative — URL Connectivity / Link Graph

Edge storage growth and hub query fanout dominate. Bound responses; cache hubs; partition writes.

## Customer-Trust Paragraph — URL Connectivity / Link Graph

Ignoring robots/takedowns and returning toxic spam neighborhoods destroys partner trust.

## Progressive Scale Recap — URL Connectivity / Link Graph

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — URL Connectivity / Link Graph

### S1. URL canonicalization

Stable IDs before graph write.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Polite crawl

Hard per-host budgets.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Sharded adjacency

Partitioned out-edges.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Hub-safe in-edges

Samples/sketches.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Approx connectivity

Landmarks/Blooms not APSP.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Batch centrality

Periodic PR-like jobs.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Spam/trust layers

Filterable scores.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Takedown/legal

Serve-path removal SLO.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — URL Connectivity / Link Graph

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Host ban risk | Cut crawl rate | Coverage lag | Diplomat/fix |
| Shard hot | Rebalance/split | Query latency | Rehash |
| Spam spike | Tighten filters | Quality | Model update |
| Extractor bug | Pause write; replay | Stale | Version fix |
| Takedown lag | Emergency purge | Legal risk | SLO fix |
| Cache stampede hubs | Request coalesce | CPU | TTL tune |


## Rapid-Fire Q&A — URL Connectivity / Link Graph

**RQ1. Why does 'URL canonicalization' matter in an L6 interview?**

**A:** Stable IDs before graph write. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'URL canonicalization' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'URL canonicalization' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Polite crawl' matter in an L6 interview?**

**A:** Hard per-host budgets. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Polite crawl' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Polite crawl' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Sharded adjacency' matter in an L6 interview?**

**A:** Partitioned out-edges. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Sharded adjacency' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Sharded adjacency' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Hub-safe in-edges' matter in an L6 interview?**

**A:** Samples/sketches. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Hub-safe in-edges' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Hub-safe in-edges' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Approx connectivity' matter in an L6 interview?**

**A:** Landmarks/Blooms not APSP. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Approx connectivity' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Approx connectivity' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Batch centrality' matter in an L6 interview?**

**A:** Periodic PR-like jobs. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Batch centrality' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Batch centrality' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Spam/trust layers' matter in an L6 interview?**

**A:** Filterable scores. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Spam/trust layers' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Spam/trust layers' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Takedown/legal' matter in an L6 interview?**

**A:** Serve-path removal SLO. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Takedown/legal' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Takedown/legal' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — URL Connectivity / Link Graph

### Walkthrough beat 1

Fetch page; extract links; canonicalize.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Upsert out-edges; update degrees.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

API returns out-neighbors from cache/shard.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Hub in-neighbor query returns sample.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Nightly PR job updates scores.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Spam score filters API results.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Takedown removes node from serve.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× partitions; 100× crawl cells; 1,000× approx indexes.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — URL Connectivity / Link Graph

- [ ] Can explain **URL canonicalization** with numbers and a deal-breaker
- [ ] Can explain **Polite crawl** with numbers and a deal-breaker
- [ ] Can explain **Sharded adjacency** with numbers and a deal-breaker
- [ ] Can explain **Hub-safe in-edges** with numbers and a deal-breaker
- [ ] Can explain **Approx connectivity** with numbers and a deal-breaker
- [ ] Can explain **Batch centrality** with numbers and a deal-breaker
- [ ] Can explain **Spam/trust layers** with numbers and a deal-breaker
- [ ] Can explain **Takedown/legal** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Host ban risk**
- [ ] Has a 30-second runbook for **Shard hot**
- [ ] Has a 30-second runbook for **Spam spike**
- [ ] Has a 30-second runbook for **Extractor bug**
- [ ] Has a 30-second runbook for **Takedown lag**
- [ ] Has a 30-second runbook for **Cache stampede hubs**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining URL Connectivity / Link Graph to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for URL Connectivity / Link Graph: 1× → 10× break → 100× cells → 1,000× specialization.

### Extra drill

Name three wallboard metrics before a peak event and the action each triggers.

### Extra drill

Write the SEV1 one-liner: impact, blast radius, mitigation, next update ETA.

### Extra drill

Defend your consistency choice: what is lost if weakened, and who notices first.

### Extra drill

Cost challenge: cut 30% without violating the top SLO—what do you shed first?

### Extra drill

Security challenge: compromised credential—how do least privilege, fencing, and audit limit damage?

### Extra drill

Multi-tenant challenge: one tenant sends 100×—show fair-share math and protected queues.


*End of document — URL Connectivity / Link Graph (SDE III)*

