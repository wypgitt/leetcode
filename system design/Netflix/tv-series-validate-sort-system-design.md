# System Design: TV Series Validate & Sort Service

> **Focus areas:** Episode graph validation · Season ordering · Metadata rules · Release date sort · Maturity consistency · Batch + streaming intake · Error reports
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS, explicit deal-breakers, Netflix 2025–26 interview themes
> **Interview theme:** Netflix Content — validate television series structure (seasons/episodes) and produce canonical sorted manifests for downstream surfaces

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

Goal: **bound **TV series validate & sort**—ingest series metadata, detect structural errors (missing episodes, bad season numbers), and emit canonical sorted episode lists for UI and playback.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Validate + sort series graph | Video encoding pipeline |
| Input | CMS metadata, partner feeds | User playback |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Validate what? | Season/episode numbering, duplicates, gaps | Rule engine |
| F2 | Sort key? | season, episode, absolute order | Stable sort |
| F3 | Specials? | Season 0 / extras bucket | Explicit rules |
| F4 | Batch? | Catalog-wide nightly + on-change | Incremental |
| F5 | Errors? | Actionable report per title | Quarantine bad titles |
| F6 | Idempotency? | Same feed version | Dedupe by hash |
| F7 | Latency? | On-change seconds; batch hours OK | Async jobs |
| F8 | Localization? | Episode titles optional | Core sort on numbers |
| F9 | Maturity? | Episode vs series consistency | Cross-field lint |
| F10 | API? | GET sorted manifest | Cached read |
| F11 | Versioning? | manifest_version | Immutable outputs |
| F12 | Downstream? | Player, browse, reco | Stable contract |

**MVP functional scope (lock with interviewer):**

1. Parse series graph from CMS.
2. Validation rule pack (gaps, dupes, orphans).
3. Canonical sort manifest output.
4. Error dashboard for content ops.
5. On-change incremental revalidate.
6. Nightly full catalog sweep.
7. Versioned manifest API.
8. Quarantine blocking publish if critical.

**Out of MVP (explicitly defer):**

- AI plot summarization
- Full rights management

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
| --- | --- | --- | --- |
| N1 | Hot path latency? | See plane | p99 per budget table |
| N2 | Durability? | No lost facts | Quorum + outbox |
| N3 | Availability? | Critical tier | 99.9–99.99% |
| N4 | Idempotency? | Retries safe | Keys on all writes |
| N5 | Scale | Through 1000× | Progressive table |
| N6 | Consistency? | Plane-appropriate | Strong OLTP; eventual agg |
| N7 | Audit? | Compliance | Append-only 7y |
| N8 | Privacy? | Min PII | Hash identifiers |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Parse series graph from CMS.
2. Validation rule pack (gaps, dupes, orphans).
3. Canonical sort manifest output.
4. Error dashboard for content ops.
5. On-change incremental revalidate.
6. Nightly full catalog sweep.

**Edge / failure cases**

| Case | Behavior |
| --- | --- |
| Duplicate client retry | Idempotent 200/409 |
| Downstream lag | Backpressure + DLQ |
| Regional outage | Failover bounded staleness |
| Hot key / shard | Isolate + partition key discipline |
| Bad deploy | Canary + rollback pointer |
| Late/arriving events | Watermark + reconcile |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
| --- | --- | --- | --- | --- |
| Peak write QPS | 100 | 1K | 10K | 100K |
| Peak read QPS | 1K | 10K | 100K | 1M |
| Distinct entities | 1M | 10M | 100M | 1B |
| Async events / s | 500 | 5K | 50K | 500K |
| Storage hot tier | 100 GB | 1 TB | 10 TB | 100 TB |

**Split classes:** intake ≠ validate ≠ sort manifest ≠ read API

**What each jump forces:**

- **10×:** Incremental validate on change.
- **100×:** Sharded by title_id.
- **1,000×:** Parallel batch with priority tiers.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-scale progressive design (10× → 100× → 1,000×).
- Sibling docs in INDEX.md for related systems.
- State invariants before drawing boxes.

**Scope statement:**

> Design **TV series validate & sort** with rule-based validation and canonical manifests for catalog titles at Netflix scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Primary workload

```text
Titles ~20K series baseline; ~10 episodes avg → 200K nodes
Validate O(n log n) sort trivial; rules O(n)
On-change ~100/s peak; batch full catalog 1×/night
```

### 2.2 Storage

```text
Hot OLTP/index: GB–TB tier
Object/log retention: PB class at 1000× with lifecycle
Idempotency TTL window drives KV size — plan explicitly
```

### 2.3 Bandwidth

```text
Egress dominates for fan-out and CDN paths
Ingress spikes during bulk/backfill — queue absorb
```

### 2.4 QPS classes (split)

| Class | Baseline | 100× | 1,000× | Notes |
|-------|----------|------|--------|-------|
| Sync writes | 100/s | 10K/s | 100K/s | sharded OLTP |
| Sync reads | 1K/s | 100K/s | 1M/s | cache + replica |
| Async consume | 500/s | 50K/s | 500K/s | partitioned |
| Batch/recon | 1/min | 10/min | 100/min | off-peak |

### 2.5 Latency budget

| Stage | Budget |
|-------|--------|
| Sync API | < 100ms p99 |
| Async visibility | < 15 min p95 |
| Batch SLA | T+1 or better |

### 2.6 Critical bottlenecks

1. Single global queue without partition keys
2. Lumping all QPS into one headline number
3. Sync call to slow warehouse on hot path
4. Missing idempotency on retries
5. No canary on config/schema changes

### 2.7 Cost intuition

```text
Track $/1M events and MTTR for rollbacks
Dominant cost usually hot storage + stream compute + egress
```

### 2.8 Deal-breaker

Lumping all QPS into one headline number

---

## 3. High-Level Design

### 3.1 Planes

```text
Control Plane: config, validation, publish, audit
Data Plane: hot read/write serving path
Async Plane: logs, aggregation, recon, batch
```

### 3.2 Core entities

| Entity | Role |
|--------|------|
| Series | root |
| Season | container |
| Episode | leaf |
| Manifest | sorted output |
| ValidationReport | errors |

### 3.3 APIs (logical)

GET /series/{id}/manifest ; POST /validate

### 3.4 Store choices

| Component | Choice | Rationale |
|-----------|--------|----------|
| OLTP/config | PostgreSQL | ACID + relations |
| Hot cache | Redis | p99 reads |
| Buffer | Kafka | Spike absorb |
| Warehouse | BigQuery/Snowflake | Reporting |
| Blobs | S3 + CDN | Fan-out |

### 3.5 Consistency model

- OLTP: strong per shard
- Async: at-least-once + idempotent sinks
- Cross-region: home affinity + bounded staleness

### 3.6 Failure policy

| Failure | Policy |
|---------|--------|
| Hot store timeout | Degrade per policy; never silent money loss |
| Broker lag | Scale consumers; delay reporting banner |
| Bad deploy | Canary rollback |
| Duplicate retry | Idempotent accept |

### 3.7 Security

RBAC, scoped tokens, audit append-only, rate limits on ingress.

### 3.8 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Correctness | Idempotency + recon |
| Latency | Cache + async where safe |
| Scale | Partition discipline |
| Ops | Canary + replay |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
CMS→Intake→Validator→Manifest Store→Player/Browse
```

### 4.2 Sequence: happy path

```text
Client→API: request
API→Store: validate + persist (idempotent)
API→Async: emit event
Worker→Sink: aggregate / fan-out
Client←API: 200/202
```

### 4.3 Sequence: failure/retry

```text
Client→API: retry same idempotency key
API→IdemStore: hit → return original
No double side effect
```

### 4.4 Sequence: scale-out

```text
Load↑ → autoscale API/consumers
Partition by hash(entity_id)
Hot tenant → isolate shard/cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Idempotent writes with client keys
2. Append-only audit for money/config facts
3. Hot path never blocks on warehouse
4. Explicit failure policies per plane
5. Version stamps on all derived artifacts
6. Split QPS classes in capacity planning
7. Reconciliation detects drift
8. Privacy: minimal PII on hot path

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Duplicate client retry | Idempotent 200/409 |
| Downstream lag | Backpressure + DLQ |
| Regional outage | Failover bounded staleness |
| Hot key / shard | Isolate + partition key discipline |

### 5.2 Scalability

| Scale | Changes |
|-------|--------|
| 1× | MVP single region |
| 10× | Cache + partition + outbox |
| 100× | Regional cells + replay |
| 1,000× | Tiered storage + approx where safe |

### 5.3 Maintainability

- Structured metrics without high-cardinality labels
- Shadow/dry-run modes for risky changes
- Replay and diff tooling for async pipelines
- Runbooks linked to SLO dashboards
- Feature flags for gradual enablement

### 5.4 Core algorithms

```text
function validateAndSort(series):
  errs = lintGraph(series)
  if critical(errs): quarantine
  manifest = sort(series.episodes, key=(season, ep))
  return manifest, errs
```

### 5.5 Multi-region

| Data | Strategy |
|------|----------|
| Hot path | Regional cells + home affinity where needed |
| Config | Global SoT with cached replicas |
| Async | Partitioned logs; idempotent consumers |
| DR | RPO/RTO documented per plane |

### 5.6 Security & privacy

- RBAC on control APIs
- Minimize PII on hot path; hash identifiers
- Audit append-only for money/config changes
- Rate limits and abuse detection on public ingress

### 5.7 Observability

| Metric | Use |
|--------|-----|
| p99 latency by plane | SLO tracking |
| Error rate delta post-deploy | Canary gates |
| Lag / queue depth | Async health |
| Drift / recon diff | Money & facts correctness |

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|--------|
| One database for all planes | Latency meltdown |
| Skip idempotency | Double counts / charges |
| No partition key | Hot shard |
| Sync warehouse on hot path | p99 explosion |

### 5.9 Progressive scale deep dive

**1× baseline**
Single region MVP with core invariants and metrics.

**10×**
Introduce caching, idempotency store, Kafka/outbox, autoscale consumers.

**100×**
Regional isolation, dedicated hot pools, replay tooling, recon batches.

**1,000×**
Edge pre-aggregation, HLL/approx, cold archive, sharded control plane.

### 5.10 Testing strategy

1. Unit: pure logic (validators, compilers, aggregators)
2. Integration: store + idempotency + outbox
3. Chaos: regional fail, cache cold, broker lag
4. Load: 10× burst on hottest class only
5. Recon: batch compare SoT vs derived views

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
| --- | --- |
| Validation | Rule engine fail closed on critical |
| Output | Versioned manifest |
| Scale | Incremental + batch |

### 6.2 Risks

1. Hot key tenant
2. Idempotency TTL too short
3. Canary false positive rollback
4. Cross-region staleness beyond SLA
5. Recon lag undetected

### 6.3 45-minute plan

| Min | Focus |
| --- | --- |
| 0–5 | Clarify planes + split QPS |
| 5–15 | Entities + APIs + stores |
| 15–25 | Hot path + idempotency |
| 25–35 | Async + recon |
| 35–45 | Scale table + deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Specials

**Q: Season 0?**
A: Explicit policy in rules.

### 7.X Traps

**Q: One QPS number?**
A: Split write/read/async/batch.

**Q: Skip idempotency?**
A: Retries corrupt state.

---


## 5.11 Validation rules catalog

| Rule ID | Check | Severity |
|---------|-------|----------|
| R1 | Duplicate (season, episode) | CRITICAL |
| R2 | Gap in episode sequence | WARNING |
| R3 | Orphan episode (no season) | CRITICAL |
| R4 | Specials without season 0 policy | WARNING |
| R5 | Maturity > series maturity | CRITICAL |
| R6 | Missing absolute order for specials | WARNING |

Critical → quarantine title from publish; warning → ops queue.

## 5.12 Sort manifest contract

```text
SeriesManifest {
  series_id, manifest_version,
  episodes: [{ season, episode, absolute_order, title_id, duration_ms }],
  generated_at, validation_hash
}
```

Downstream player uses `absolute_order` for binge autoplay; browse uses season grouping.

## 7.9 TV series questions

**Q: Out-of-order release (Stranger Things style)?**  
A: absolute_order explicit field; don't infer from release date alone.

**Q: Recap specials?**  
A: Tag `content_kind=RECAP`; sort policy places before season premiere.


## 8. Appendices

### A1. Core schema sketch

```text
| Entity | Role |
|--------|------|
| Series | root |
| Season | container |
| Episode | leaf |
| Manifest | sorted output |
| ValidationReport | errors |
```

### A2. Launch checklist

- [ ] Idempotency verified
- [ ] Canary rollback tested
- [ ] Recon job scheduled
- [ ] Split QPS on dashboard

### A3. Glossary

| Term | Meaning |
|------|--------|
| SoT | Source of truth |

### A4. Interviewer traps

| Trap | Pushback |
|------|----------|
| Monolith DB | Split planes |

### A5. Reliability test plan

1. Idempotent retry returns same result
2. Canary/rollback under load
3. Regional failover with bounded staleness
4. Replay job produces identical aggregates
5. Chaos on hottest dependency
6. Scale test on split QPS class

### A6. 60-second summary

> **TV Series Validate & Sort Service** — clarify planes, idempotency, progressive scale, recon.

### A7. Related systems map

```text
See Section 4 diagram for TV Series Validate & Sort Service
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Hot p99 | < 100ms |

### A9. Worked numeric example

See Section 2 back-of-envelope for TV Series Validate & Sort Service baseline numbers.

### A10. Pseudo-SQL / DDL

```sql
-- See entity sketch in A1
```

### A11. Ownership

| Concern | Owner |
|---------|-------|
| Service | Platform team |

### A12. Progressive checklist

| Scale | Must have |
|-------|----------|
| 1× | MVP invariants + metrics |
| 10× | Idempotency + cache + partition discipline |
| 100× | Regional cells + replay tooling |
| 1,000× | Tiered hot/cold + approximations where safe |

### A13. Naive design comparison

| Naive | Why it fails |
|-------|--------------|
| One DB for everything | Wrong latency class |
| No idempotency | Retries corrupt state |
| Single global queue | Hot key meltdown |
| Skip canary/validation | Fleet-wide incidents |

### A14. On-call cheat sheet

1. Check error rate delta vs deploy
2. Check lag on async plane
3. Verify idempotency / dedupe store health
4. Roll back pointer/config if SLO breach
5. Page if money/facts drift exceeds threshold

### A15. Sample debug record

```text
{
  "trace_id": "tr_abc",
  "entity_id": "ent_xyz",
  "version": 42,
  "region": "us-west-2",
  "outcome": "OK"
}
```

### A16. Cost worksheet

```text
dominant = hot_storage + stream_compute + cross_region_egress
track $/1M events and MTTR for rollbacks
```

### A17. Explicit non-goals

- Perfect global strong consistency on all reads
- Building all sibling systems in one interview
- Client-trusted counts as billing SoT

### A18. Interview rubric

- Clarify planes and split QPS
- State invariants early
- Progressive scale table
- Deal-breaker gallery
- Wrap with risks + test plan

### A19. Migration / rollout notes

Dual-write or shadow-read when replacing SoT; never big-bang cutover without recon period.

### A20. Further reading (siblings)

See INDEX.md for catalog/streaming siblings.

### A21. Validation rules catalog

| Rule | Severity |
|------|----------|
| Unique (show_id, season, episode) | HARD |
| Air date monotonic within season (soft/hard policy) | SOFT/HARD |
| Runtime > 0 | HARD |
| Title non-empty | HARD |
| Duplicate part numbers | HARD |
| Missing season hole | WARN |

### A22. Sort keys

```text
ORDER BY show_id, season_number ASC, episode_number ASC, absolute_number ASC NULLS LAST
Special: extras/bonus flagged out of main sequence
```

### A23. API

```text
POST /v1/series/{id}/episodes:validate
GET  /v1/series/{id}/episodes?sort=canonical
POST /v1/series/{id}/episodes:bulkUpsert
```

### A24. Idempotent upsert

```text
Natural key (show, season, ep) + If-Match version
Reject conflicting renumbers without migrate job
```

### A25. Multi-edition problem

Directors cut vs broadcast: `edition` dimension; canonical sort per edition; UX picks default edition.

### A26. Pipeline placement

Ingest → validate → sort materialize → publish to catalog → streaming entitlements consume ordering for “next episode”.

### A27. Failure cases

| Case | Behavior |
|------|----------|
| Hole in episode numbers | WARN; still sort |
| Two ep #5 | HARD fail publish |
| Unsorted input | Output still canonical |
| Clock skew air dates | Prefer explicit numbers over dates |

### A28. Scale

| Metric | 1× | 100× |
|--------|----|------|
| Shows | 10K | 1M |
| Validate QPS | 50 | 5K |

CPU-bound validators; cache sorted lists per show version.

### A29. 60-second summary

> Validate TV episodes against **hard uniqueness/numbering invariants**, materialize **canonical sort**, version catalog publishes so “next episode” and UX order are deterministic — warnings vs hard fails explicit.

### A30. Tests

1. Dup ep number → reject.  
2. Shuffled input → stable sort.  
3. Bonus flag excluded from main next-ep.  
4. Concurrent upsert CAS.  
5. Edition isolation.

### A31. Metrics

`validate_fail_rate`, `publish_block_rate`, `sort_cache_hit`

### A32. Progressive checklist

| Scale | Must |
|-------|------|
| 1× | Rules + sort API |
| 10× | Bulk upsert + versions |
| 100× | Sharded catalog |
| 1,000× | Multi-edition graph |

### A33. Rubric

- Hard vs soft rules  
- Canonical sort key  
- Next-episode coupling  
- Versioned publish  

### A34. Non-goals

Full video encode; recs ranking; fan subtitle NLP.

### A35. Ownership

Catalog metadata team; playback consumes ordering.

---

*End of document — Netflix system design interview prep: TV Series Validate & Sort.*
