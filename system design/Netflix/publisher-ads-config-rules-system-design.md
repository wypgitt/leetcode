# System Design: Publisher Ads Config Rules

> **Focus areas:** Publisher-specific policies · Rule precedence · Geo/device overrides · Brand category blocks · Emergency kill switches · Compiled rule bundles
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS, explicit deal-breakers, Netflix 2025–26 interview themes
> **Interview theme:** Netflix Ads — publisher-specific configuration rules that override global defaults safely with precedence and audit

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

Goal: **bound **publisher ads config rules**—how Netflix-as-publisher encodes market-specific ad policies (categories blocked, max pod length, interactive formats) with precedence, validation, and fast rollout.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Publisher rule layer on global config | Full trafficking intake |
| Scope | Publisher/market/device | Advertiser CRM |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Precedence? | Publisher > global default | Merge compiler |
| F2 | Rule types? | Category block, format allow, pod policy | Typed rule AST |
| F3 | Emergency? | Kill alcohol globally in market | Instant pointer override |
| F4 | Validation? | No contradict hard legal | Linter fail closed |
| F5 | Serving? | Compiled into snapshot | Not interpreted ad hoc |
| F6 | Audit? | Who changed publisher rule | Append-only |
| F7 | A/B? | Publisher experiments rare | Feature flag section |
| F8 | Multi publisher? | Future partners | publisher_id scope |
| F9 | Kids publisher mode? | No ads / strict | Hard override |
| F10 | Rollback? | Version pointer | < 30s effective |
| F11 | Testing? | Shadow evaluate | Sampled diff metrics |
| F12 | API? | Ops CRUD + publish | RBAC |

**MVP functional scope (lock with interviewer):**

1. Publisher rule CRUD with typed schema.
2. Precedence merge in compiler.
3. Emergency override pointer.
4. Shadow mode metrics.
5. Audit + RBAC.
6. Publish to config rollout.
7. Kids/market hard blocks.
8. Integration tests on compile.

**Out of MVP (explicitly defer):**

- Full legal CMS
- Per-user publisher rules

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

1. Publisher rule CRUD with typed schema.
2. Precedence merge in compiler.
3. Emergency override pointer.
4. Shadow mode metrics.
5. Audit + RBAC.
6. Publish to config rollout.

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

**Split classes:** rule CRUD ≠ compile merge ≠ snapshot publish ≠ decision eval

**What each jump forces:**

- **10×:** Compiled bundles per publisher.
- **100×:** Regional publisher cells.
- **1,000×:** Delta rule patches.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-scale progressive design (10× → 100× → 1,000×).
- Sibling docs in INDEX.md for related systems.
- State invariants before drawing boxes.

**Scope statement:**

> Design **publisher ads config rules** with precedence merging, emergency overrides, and compiled snapshots for safe global rollout.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Primary workload

```text
Publishers ~10 baseline; rules ~500/publisher
Compile merge O(rules) offline — not per request
Snapshot add ~100 KB publisher overlay
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
| Publisher | Tenant of policy |
| PublisherRule | Typed override |
| MergedSnapshot | Global+publisher |
| OverridePointer | Emergency |

### 3.3 APIs (logical)

POST /publishers/{id}/rules ; POST /publish

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
Global Config + Publisher Rules → Compiler → Merged Snapshot → Rollout
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
function compile(global, publisherRules):
  merged = global.copy()
  for r in sortByPrecedence(publisherRules): merged.apply(r)
  lintLegal(merged); return merged
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
| Merge | Offline compiler |
| Emergency | Pointer override |
| Eval | Precompiled only |

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

### 7.1 Precedence

**Q: Conflicts?**
A: Explicit ordering + linter.

### 7.X Traps

**Q: One QPS number?**
A: Split write/read/async/batch.

**Q: Skip idempotency?**
A: Retries corrupt state.

---


## 5.11 Precedence merge example

```text
Global: allow category {automotive}
Publisher JP: block category {alcohol}
Publisher JP line override: allow creative X (exception)

Merge order (lowest wins for restrictions):
  1. Global defaults
  2. Publisher rules
  3. Emergency kill pointer (legal)
  4. Line-level exceptions (explicit allow only)

Compiler emits merged eligibility bitmap + audit trace of applied rules.
```

## 5.12 Emergency kill switch

```text
POST /publishers/{id}/overrides { category: ALCOHOL, action: BLOCK, ttl: 24h }
→ OverridePointer CAS
→ Invalidate decision fleet within 30s
→ Audit actor + legal ticket id required
```

## 5.13 Shadow evaluation

Sample 1% decisions: evaluate both global-only and merged rules; diff block rates; page if divergence > threshold without approved publish.

## 7.9 Publisher rules questions

**Q: Who wins on conflict?**  
A: Documented precedence table; most restrictive for brand-safety categories unless legal exception.

**Q: Per-user publisher rules?**  
A: Out of scope — publisher/market/device only.


## 8. Appendices

### A1. Core schema sketch

```text
| Entity | Role |
|--------|------|
| Publisher | Tenant of policy |
| PublisherRule | Typed override |
| MergedSnapshot | Global+publisher |
| OverridePointer | Emergency |
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

> **Publisher Ads Config Rules** — clarify planes, idempotency, progressive scale, recon.

### A7. Related systems map

```text
See Section 4 diagram for Publisher Ads Config Rules
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Hot p99 | < 100ms |

### A9. Worked numeric example

See Section 2 back-of-envelope for Publisher Ads Config Rules baseline numbers.

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

See INDEX.md ads data model, config rollout, frequency capping.

### A21. Why publisher-specific rules

Even within one streaming service, “publishers” may mean app surfaces, regions, content partners, or ad pod placements with different brand-safety and product policies.

### A22. Rule types

| Type | Example |
|------|---------|
| Allow/deny category | No alcohol on kids surface |
| Pod structure | Max 2 ads / pod |
| Priority | House ads fill policy |
| Creative length | ≤15s on mobile |
| Targeting overlay | Force geo include |

### A23. Compilation

```text
Rules OLTP → compile to deterministic bytecode/JSON bundle per publisher_id
Decision nodes pin bundle version (see config rollout sibling)
```

### A24. Evaluation order

```text
hard safety → publisher constraints → advertiser targeting → caps → pacing → rank
```

### A25. Conflict resolution

Most restrictive wins for safety; explicit priority integers for product rules; validate on publish.

### A26. Schema

```text
PublisherRule {
  rule_id, publisher_id, priority, predicate, effect, hardness, version, state
}
```

### A27. Failure policy

Missing bundle → fail closed on safety-sensitive publishers; else last-known good version.

### A28. Scale

| Metric | 1× | 100× |
|--------|----|------|
| Publishers | 50 | 5K |
| Rules | 5K | 500K |
| Bundle push | 10/day | 1K/day |

### A29. 60-second summary

> Publisher rules are **versioned, compiled constraints** applied before auction—safety fail-closed, restrictive merge semantics, rolled out via config snapshots.

### A30. Tests

1. Kids publisher blocks alcohol.  
2. Conflicting rules → restrictive.  
3. Bundle rollback instant.  
4. Invalid predicate reject publish.  
5. Decision p99 unaffected (local eval).

### A31. Metrics

`rule_block_rate`, `bundle_age`, `compile_fail`, `fail_closed_rate`

### A32. Progressive checklist

| Scale | Must |
|-------|------|
| 1× | CRUD + local eval |
| 10× | Compiled bundles |
| 100× | Cells + canary |
| 1,000× | Delta patches |

### A33. Rubric

- Compilation  
- Restrictive merge  
- Fail closed safety  
- Version pin  

### A34. Non-goals

Full auction ML; creative CDN.

### A35. Ownership

Ads product config + serving runtime.

---

*End of document — Netflix system design interview prep: Publisher Ads Config Rules.*
