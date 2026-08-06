# System Design: Video Playlist Component

> **Focus areas:** Ordered media list · Prefetch · Seamless play · DRM handoff · Up-next logic · Client-server contract · Performance · Accessibility
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS, explicit deal-breakers, Netflix 2025–26 interview themes
> **Interview theme:** Netflix Player — design a video playlist component that manages ordered playback, prefetch, and transitions for binge sessions

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

Goal: **bound **video playlist component**—client/server contract for an ordered list of playable items with prefetch, skip, resume, and tight handoff to the streaming stack.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Playlist state + prefetch + play handoff | Full CDN/origin design |
| Scope | Component + API | Entire Netflix app |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Contents? | Episodes, trailers, recaps | Ordered list model |
| F2 | Prefetch? | Next N segments/titles | Bandwidth aware |
| F3 | Skip? | Next/prev user action | State machine |
| F4 | Resume? | Persist position | Profile scoped |
| F5 | End behavior? | Auto-play next episode | Configurable countdown |
| F6 | Errors? | Skip unavailable | Fallback item |
| F7 | Ads tier? | Ad pods between items optional | Hook to ad decision |
| F8 | Offline? | Downloaded subset | Local playlist mirror |
| F9 | A11y? | Focus order, announcements | WCAG |
| F10 | Metrics? | Start latency, abandon | Event logging |
| F11 | Server? | Playlist manifest API | Versioned JSON |
| F12 | Performance? | No main-thread jank | Virtualized UI list |

**MVP functional scope (lock with interviewer):**

1. Playlist model with ordered items + metadata.
2. Server manifest API versioned.
3. Client prefetch next title/segments.
4. Auto-play countdown UX.
5. Skip/prev state machine.
6. Resume tokens profile-scoped.
7. Error skip unavailable.
8. Metrics hooks.

**Out of MVP (explicitly defer):**

- Full offline sync platform
- Interactive branching narrative engine

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

1. Playlist model with ordered items + metadata.
2. Server manifest API versioned.
3. Client prefetch next title/segments.
4. Auto-play countdown UX.
5. Skip/prev state machine.
6. Resume tokens profile-scoped.

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

**Split classes:** manifest fetch ≠ client state ≠ prefetch ≠ player handoff

**What each jump forces:**

- **10×:** Smarter prefetch heuristics.
- **100×:** Edge manifest cache.
- **1,000×:** Personalized playlist fragments.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-scale progressive design (10× → 100× → 1,000×).
- Sibling docs in INDEX.md for related systems.
- State invariants before drawing boxes.

**Scope statement:**

> Design **video playlist component** with server manifest, client prefetch, and seamless binge transitions.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Primary workload

```text
Avg playlist 10 items; manifest ~5 KB
Prefetch 1 next title metadata + first segments
State updates 1–5/s during binge — cheap
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
| Playlist | container |
| PlaylistItem | title/episode ref |
| Manifest | server JSON |
| PlaybackState | position |

### 3.3 APIs (logical)

GET /playlists/{id}/manifest ; client events

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
Browse→Playlist API→Client Component→Player→CDN
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
onItemEnd(): if autoplay: prefetch(next); startCountdown(); play(next)
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
| Contract | Versioned manifest |
| Prefetch | Bandwidth-aware |
| UX | Countdown + skip |

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

### 7.1 Prefetch

**Q: How much?**
A: Next title + first segments; cap bandwidth.

### 7.X Traps

**Q: One QPS number?**
A: Split write/read/async/batch.

**Q: Skip idempotency?**
A: Retries corrupt state.

---


## 5.11 Client state machine

```text
States: IDLE, PLAYING, COUNTDOWN, BUFFERING, ERROR_SKIP
Events: ITEM_END, USER_NEXT, USER_PREV, MANIFEST_REFRESH, NETWORK_DOWN

on ITEM_END + autoplay enabled → COUNTDOWN(5s) → prefetch(next) → PLAYING
on ERROR_SKIP → mark item failed; advance unless user cancelled
```

## 5.12 Prefetch strategy

| Signal | Prefetch |
|--------|----------|
| Wi-Fi + HD | Next title manifest + first 2 segments |
| Cellular metered | Metadata only until COUNTDOWN |
| Offline | Local manifest mirror |

Bandwidth cap: max 5 MB lookahead on cellular.

## 5.13 Server manifest API

```text
GET /profiles/{p}/playlists/{id}/manifest?version=
Response: { version, items[{title_id, episode_id, duration, entitlement_token}] }
ETag for cache; profile-scoped auth — never CDN cache anonymously
```

## 7.9 Playlist questions

**Q: Ads between episodes?**  
A: Playlist emits `BREAK` markers; ad pod inserted by ad decision sibling — playlist doesn't count ads as items unless product says so.

**Q: Interactive branch?**  
A: Out of MVP; manifest would include `branch_choices` extension.


## 8. Appendices

### A1. Core schema sketch

```text
| Entity | Role |
|--------|------|
| Playlist | container |
| PlaylistItem | title/episode ref |
| Manifest | server JSON |
| PlaybackState | position |
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

> **Video Playlist Component** — clarify planes, idempotency, progressive scale, recon.

### A7. Related systems map

```text
See Section 4 diagram for Video Playlist Component
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Hot p99 | < 100ms |

### A9. Worked numeric example

See Section 2 back-of-envelope for Video Playlist Component baseline numbers.

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

See INDEX.md for video streaming + playlist/recs siblings.

### A21. Component responsibilities

```text
PlaylistComponent:
  - Fetch / refresh ordered playable items (episode queue, my list, continue)
  - Prefetch next manifests metadata
  - Handle offline / errors / empty
  - Emit analytics (impressions, start)
  - Respect profile maturity + entitlements
```

### A22. Data contract

```text
Playlist {
  id, type, version,
  items: [{title_id, playable_id, pos, artwork, progress?}],
  cursor?, eof
}
```

### A23. Optimization techniques

| Technique | Why |
|-----------|-----|
| Windowed virtualization | Don’t mount 1000 rows |
| Image CDN + size params | Bandwidth |
| Prefetch next 1–2 items | TTFF |
| Stable keys | Avoid remount flicker |
| Dedup with page constructor | No duplicate titles |

### A24. State machine

```text
IDLE → LOADING → READY → REFRESHING
                 ↘ ERROR → RETRY
PLAYING_ITEM updates progress via CW callbacks
```

### A25. Ads tier interaction

Playlist of content items; mid-roll ads not playlist entries — player inserts pods without breaking episode order.

### A26. Performance budgets

| Metric | Target |
|--------|--------|
| First paint items | < 300ms cached |
| Scroll FPS | 60 |
| Memory | bound window |

### A27. Failure UX

Cached last playlist; skeleton rows; never blank kids with adult stubs.

### A28. Testing

1. Rapid profile switch clears state.  
2. Entitlement revoke removes item.  
3. Virtualization window correctness.  
4. Prefetch cancel on unmount.  
5. Analytics only for visible items.

### A29. 60-second summary

> A playlist UI component binds **versioned ordered playable items**, virtualizes rendering, prefetches wisely, integrates CW/entitlements, and stays orthogonal to ad pods — performance via windowing + stable keys.

### A30. Progressive scale

| Scale | Must |
|-------|------|
| 1× | Fetch+render list |
| 10× | Virtualize+prefetch |
| 100× | Edge cached playlist fragments |
| 1,000× | Personalized fragment assembly |

### A31. Metrics

`playlist_load_ms`, `prefetch_hit`, `scroll_jank`, `empty_rate`

### A32. Rubric

- Contract clarity  
- Virtualization  
- Prefetch  
- Profile safety  
- Ads orthogonality  

### A33. Non-goals

Building ABR player internals; full recs ranker.

### A34. Ownership

Client playback UI + playlist API owned by streaming client / page services.

### A35. API

```text
GET /v1/playlists/{id}?profile_id=&cursor=
```

---

*End of document — Netflix system design interview prep: Video Playlist Component.*
