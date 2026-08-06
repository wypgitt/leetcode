# System Design: Search Typeahead (Client/Server, Privacy of Query Logs)

> **Focus areas:** Trie/FST · edge cache · on-device model · differential privacy · Apple Search / Safari / App Store vibes · offline  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Apple lens:** Privacy · Authentication · APIs · Storage · Offline · On-device/server boundaries  
> **Bank:** A  
> **Quality bar:** Correct arithmetic, split load classes, explicit invariants, deal-breakers called out, honest MVP vs extreme-scale paths

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

Goal: **bound the product**—a search typeahead / autocomplete system spanning client and server with strong privacy constraints on query logs.

### 1.0 Apple interview lens (say this early)

| Dimension | Apple-weighted expectation | Anti-pattern |
|-----------|---------------------------|--------------|
| Privacy | Minimize server-visible PII; preferential on-device processing; retention & deletion are first-class | Logging raw queries/contents “for ML” without consent story |
| Auth | Strong identity (Apple ID / device attestation / app attest); least privilege API tokens | Anonymous writable endpoints with guessable IDs |
| APIs | Stable versioned contracts; idempotency; clear error taxonomy | Silent breaking changes; chatty chatty RPCs on cellular |
| Storage | Clear SoT; encryption at rest; sync tokens; conflict policy | Dual SoT without reconciliation |
| Offline | Local-first UX where product requires it; queue + replay | Assume always-online |
| On-device / server boundary | Explicit: what never leaves device vs what may sync | Accidental cloud of secrets/keys/raw health |


### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Surface? | App Store / site search box | Prefix + popularity |
| F2 | Latency? | Feels instant | Edge + client cache |
| F3 | Personalization? | Limited; privacy-preserving | On-device rank signals |
| F4 | Query logs? | Aggregate / DP; raw minimized | No forever raw logs |
| F5 | Languages? | Locale-aware | Per-locale indices |
| F6 | Offline? | Ship compact FST/trie slice | On-device model |
| F7 | Abuse? | Flood of fake queries | Auth + rate limit |
| F8 | Freshness? | Trending within minutes–hours | Nearline updater |
| F9 | Safety? | Block abusive suggestions | Deny lists |
| F10 | Client/server split? | Client filter + server enrich | Explicit boundary |
| F11 | Metrics? | Suggest CTR aggregates | Privacy budget |
| F12 | Privacy / logging? | Minimize PII; retention caps; deletion APIs | Privacy budget + scrubbing pipelines |

**MVP functional scope (lock with interviewer):**

1. Clarify actors, trust boundaries, and on-device vs server responsibilities.
2. Define primary APIs with authn/authz and idempotency.
3. Durable SoT + explicit state machine(s).
4. Happy path + critical failure/fencing behavior.
5. Baseline estimation with split load classes and unit checks.
6. Privacy: retention, deletion, log minimization.
7. Observability & audit for sensitive actions.
8. Progressive scale plan 10×/100×/1000× with the first bottleneck named.

**Out of MVP (explicitly defer):**

- Perfect global linearizability with local latency worldwide.
- Fully featured ML personalization platform (unless the question).
- Unbounded retention of raw sensitive telemetry.
- Active-active dual writers without a conflict story.
- Replacing safety/PLC/hardware interlocks with cloud SaaS.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Suggest latency? | Keystroke path | p50 < 50ms, p99 < 150ms edge |
| N2 | Durability? | No silent loss after ACK | Quorum / fsync policy explicit |
| N3 | Availability? | Degrade gracefully | 99.9%+ control plane typical |
| N4 | Privacy? | Minimization + encryption + retention | Non-negotiable Apple lens |
| N5 | Multi-region? | As product requires | Home cell / residency modes |
| N6 | Consistency? | State explicitly | Never imply stronger than built |
| N7 | Operability? | Metrics, traces, audit | Oncall-ready |
| N8 |  thruput? | Meet scale table | Split load classes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Authenticated client performs primary happy-path operation end-to-end with durable ACK.
2. Idempotent retry returns the original result without double effect.
3. Read-your-writes after mutation via home cell or sync token.
4. Privacy delete completes with verification.
5. Degraded dependency: system sheds secondary features and keeps core promise.
6. Multi-device/offline resume reconciles without silent data loss (when applicable).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate submit / retry | Idempotency key wins; single effect |
| Stale writer after failover | Fencing rejects |
| Hot key / noisy tenant | Isolation + quotas |
| Region partition | Home-cell writes fail closed; edge may serve stale reads |
| Cache stampede | Singleflight / jitter |
| Partial deploy failure | Wave halt + rollback |
| Clock skew | Server logical time for leases |
| Abuse flood | Rate limit + authn; fail-closed on abuse path |
| Privacy mis-log | Kill switch + scrub |
| Dependency timeout | Bounded retry + circuit break |
| Quota exhaustion | Clear error; no silent quality lie |
| Legal hold vs delete | Hold wins with audit |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| QPS suggest peak | 50K | 500K | 5M | 50M |
| DAU | 20M | 200M | 1B | 2B |
| Dictionary terms | 10M | 50M | 200M | 500M |
| Edge POPs | 20 | 50 | 100 | 200 |
| Index build / day | 24 | 24 | 96 | continuous |
| Raw query log retention | 0–1d sampled | DP only | DP only | DP only |

**What each jump forces:**

- **10×:** Shard hot paths; introduce caches; make idempotency and authz non-optional; split read/write planes.
- **100×:** Cells / home regions; asynchronous side paths; stronger tenancy isolation; privacy-preserving analytics only.
- **1,000×:** Hierarchical control planes; regionalization; aggressive retention/tiering; explicit degrade modes; on-device offload where Apple-relevant.

**Topic accent:** 10×: edge cache + compact FST; 100×: on-device ranker + DP logs; 1000×: per-locale cells, nearline trending without raw logs.

### 1.5 Etc. (Constraints & Assumptions)

- We design the system software/control planes—not unrelated product surfaces.
- Prefer **privacy-preserving defaults**; justify any raw server-side personal data.
- Single primary cloud/provider assumption OK unless interviewer specifies hybrid.
- Clocks are untrusted on clients for leasing/security decisions.
- “Exactly-once” means **exactly-once effects** via idempotency unless a stronger protocol is designed.

**Scope statement:**

> Design typeahead: low-latency suggestions, client cache + on-device ranker hooks, server indices, and privacy-preserving query analytics—not a full web search engine.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Keystroke amplification

```text
User types 8 chars; maybe 5 suggest calls (debounce)
50M peak QPS suggest at extreme → edge cache hit ratio critical
Target >90% edge/client hit for head queries
```

### 2.2 Index size

```text
200M terms × 20 B payload avg + FST overhead → tens of GB per locale shard
Ship on-device subset: 50–200 MB compressed per locale slice
```

### 2.3 Privacy math

```text
Never keep raw queries 1:1 forever
Sample + DP: if ε daily budget B, each query report costs ε_i; drop when exhausted
```

### 2.5 Ranked bottlenecks

1. Hottest synchronous user/API path under privacy constraints  
2. Hot keys / hot partitions / noisy tenants  
3. Cross-region chatty coordination  
4. Rebuild/backfill/migration storms  
5. Observability pipelines accidentally on the critical path  
6. Fail-open/closed misconfiguration under partial outages  

### 2.6 Cost / frugality (Apple-relevant)

Prefer on-device and edge aggregation to cut uplink and server retention. Store pointers + hashes rather than raw sensitive payloads when product allows. Cache aggressively at edge **after** authz.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| API / edge | Authn/authz, routing | Stateless |
| Control plane | Config, orchestration | Strong where needed |
| Data plane | Primary workload path | Per-key/home-cell |
| Async / index | Derived data | Eventual |
| Privacy / audit | Minimization, access logs | Append-only audit |

**Deal-breaker:** mixing best-effort analytics counters with durable source-of-truth ledgers.

### 3.2 Core components

1. **Edge / API Gateway** — TLS, authn, rate limits, routing, privacy headers.  
2. **Identity & AuthZ** — Apple ID / service accounts / device attestation hooks; scoped tokens.  
3. **Primary service(s) for Search Typeahead (Client/Server, Privacy of Query Logs)** — business state machines & APIs.  
4. **Durable stores** — OLTP + object/block as needed; encryption at rest.  
5. **Async workers / streams** — outbox, indexing, backfill, notifications.  
6. **Cache / edge data** — latency path; never sole SoT for critical truth.  
7. **Config & feature flags** — progressive rollout; residency switches.  
8. **Observability** — metrics/logs/traces with PII scrubbing.  
9. **Admin / incident tooling** — audited break-glass.  
10. **Client SDK / on-device module** — offline queues, local crypto, sync tokens (when relevant).  

### 3.3 API sketch (illustrative)

```text
# Authn: Bearer / session / device token; all mutations idempotent where feasible
POST   /v1/...          Idempotency-Key: ...
GET    /v1/.../{id}     Authorization + authz check
PATCH  /v1/.../{id}     If-Match / expected_version
DELETE /v1/.../{id}     Soft delete + async purge where privacy requires

# Privacy
POST   /v1/privacy/export
POST   /v1/privacy/delete
```

Version APIs; add fields only; use explicit error codes (`401/403/409/429/503`).

### 3.4 Hard invariants (customize in interview)

1. **Authz before data** — never fetch-then-filter as sole control for private objects.
2. **ACK ⇒ durable** for accepted mutations users rely on.
3. **Monotonic versions / fencing** for leadership, leases, and attach.
4. **Privacy deletes eventually remove bytes** (with legal-hold exceptions explicit).
5. **On-device safety/secrets stay on-device** unless product explicitly syncs under consent.
6. **Idempotency** for client retries on mutating APIs.

### 3.4a Client/server boundary

```text
Client: debounce, local LRU/FST, on-device personalization features
Edge: anonymized suggest for head queries
Server: complete index, safety filters, trending nearline
Logs: hashes/sketches/DP — not raw query dossiers
```

### 3.6 Trade-off tables

| Topic | Choice | Why | Deal-breaker alternative |
|-------|--------|-----|--------------------------|
| SoT | Single home-cell writer for mutable entity | Avoid split-brain | Active-active dual write without CRDT/merge |
| Cache | Edge/L1 after authz | Latency | Cache private data without authz keying |
| Queue | Durable log for async | Replay/backpressure | Drop-on-full for money/privacy deletes |
| Consistency SKU | Offer explicit modes | Honest latency | Claim linearizable + free cross-ocean |
| Offline | Local journal + sync | UX | Silent cloud overwrite without conflict policy |
| Telemetry | Aggregates / DP | Privacy | Raw user content logs by default |
| Secrets | Short-lived + HSM | Blast radius | Long-lived keys in env on disk forever |
| Multi-tenant | Shuffle shard + quotas | Noisy neighbor | One global FIFO/lru for all |

### 3.5 Deal-breakers (call out loud)

| Temptation | Why it fails at Apple-style bar |
|------------|----------------------------------|
| Log raw sensitive payloads | Privacy / legal / trust |
| ACK before durability | Silent loss |
| Guessable IDs for private objects | IDOR epidemics |
| Cross-region sync on every keystroke/IO | Latency & cost melt |
| Cloud required for safety interlocks | Physical harm / brick risk |
| Dual SoT without verifier | Divergent truth |
| Fail-open rate limits on abuse paths | Meltdown & fraud |
| “Exactly-once” without idempotency design | False confidence |

### 3.7 Multi-region / residency clarity

| Plane | Mode |
|-------|------|
| Edge APIs | Active-active globally |
| Mutable entity writes | **Single-writer home cell** (or CRDT with explicit merge) |
| Reads | Local replica / cache; read-your-writes via home or sync token |
| EU residency SKU | Data + primary processing in EU when selected |
| Telemetry | Regionally aggregated; minimize cross-region raw |

**Deal-breaker:** silent cross-region replication of restricted categories (health, payment, precise location) against policy.

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Keystrokes -> Client FST/LRU -> (miss) Edge Suggest Cache -> Suggest Service
                                      |                         |
                                 safety filter            nearline trending
                                      |
                              DP / aggregate logs (not raw forever)
 On-device personalization features stay on device
```

### 4.2 Sequence: mutation with idempotency

```text
Client                 API                   Store
  |-- POST + Idem-Key -->|                      |
  |                      |-- begin / insert --->|
  |                      |<- durable -----------|
  |<- 200 + resource ----|                      |
  |-- retry same key --->|-- lookup ----------->|
  |<- same resource -----|                      |
```

### 4.3 Sequence: offline → sync (when applicable)

```text
Device (offline) applies local mutation to journal
Online: push chunks/ops -> server validates authz/version
On conflict: policy returns conflictors; client merges or forks
Privacy delete on server must tombstone and prevent resurrection from stale device (epoch/fence)
```

### 4.4 Scale cells

```text
Global directory: entity_id/user_id -> home cell
Cell: API slice + primary store + workers
Edge: caches & gateways active-active
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants (restate with teeth)**

1. Durability before ACK for accepted critical writes in Search Typeahead (Client/Server, Privacy of Query Logs).
2. Fencing tokens / epochs on leadership, leases, volume attach, deploy waves.
3. Idempotent mutation APIs; safe retries.
4. Privacy deletion & retention enforced with verification jobs.
5. Authz on every read/write path; no IDOR via sequential IDs.
6. Degrade modes documented (what sheds first).

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Node crash mid-write | WAL/quorum; client retry idempotent |
| Network partition | Home-cell single writer; avoid dual primary |
| Poison message / bad deploy | DLQ / canary / autowave halt |
| Hot partition | Re-shard, split keys, admission control |
| Clock skew | Server time / logical clocks for leases |
| Dependency outage | Circuit break; backlog; user-visible degrade |
| Privacy bug (extra logging) | Scrub pipelines; break-glass audit; kill switches |

**Cancel / drain / rollback**

- Cooperative cancel with deadlines.
- Restarts/deploys: drain → bake → promote; auto-rollback on SLO burn.
- Migrations: always keep a reverse or dual-read window until verify green.

### 5.2 Scalability

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| 1× | Modular monolith or few services; one primary DB; correct invariants |
| 10× | Shard by tenant/user; caches; async outbox; rate limits |
| 100× | Cells; separate hot planes (heartbeat/IO/redirect); shuffle sharding |
| 1000× | Hierarchical control; regionalization; on-device/edge offload; tiered storage |

**Techniques checklist**

- Split dissimilar QPS classes onto different stores.
- Batch chatty paths (heartbeats, progress, telemetry).
- Hierarchical admission control.
- Materialize read models; don't join huge graphs online.
- For Apple clients: respect battery, Wi-Fi, Low Power Mode—coalesce.

### 5.3 Maintainability

- Versioned APIs & worker protocols (`protocol_version`).
- Schema migrations expand/contract; dual-read flags.
- Feature flags with residency/privacy tags.
- Chaos drills: kill leaders, delay disks, partition cells, revoke keys.
- Privacy reviews as merge gates for log fields.
- Runbooks: “stuck job”, “divergent storage”, “auth lockout spike”, “ε budget exhaustion”.

**Observability must-haves**

- RED/USE metrics per plane; SLO dashboards.
- Trace IDs across gateway → service → worker.
- Audit for admin/PII access.
- Data quality: verifier lag, checksum fail rate, DLQ depth.

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× — correct MVP for Search Typeahead (Client/Server, Privacy of Query Logs)**

Ship the smallest design that preserves invariants: durable SoT, authz, idempotency, explicit privacy boundary, basic metrics.

**10× — shard & async**

Partition data by `user_id`/`tenant_id`/`doc_id`/`volume_id` as appropriate. Move non-critical work to streams. Add edge cache where authz-safe.

**100× — cells & plane splits**

Home cells; dedicated planes for the chatty path identified in estimation; noisy-neighbor isolation; multi-region active-active **edge** only.

**1000× — hierarchy & offload**

Regional fabrics; on-device processing for privacy/latency; aggressive tiering/retention; hierarchical schedulers/limiters; clean-room analytics.

### 5.5 Privacy of typeahead

Prefer on-device personalization; server sees truncated prefixes when possible; DP for trends; retention hours not months for any raw sample.

### 5.8 Deal-breaker gallery (quick reference)

| Temptation | Why it fails |
|------------|--------------|
| Redis-only accept for critical truth | Durability/compliance |
| Global single lock/queue | Melts & noisy neighbor |
| Cross-ocean sync on hot path | p99 death |
| Raw query/location/content logs | Privacy deal-breaker |
| Client-authoritative money/cards/safety | Fraud/harm |
| Unfenced leader failover | Split-brain writes |
| Unbounded retries without jitter | Cascades |
| Cache without invalidation story | Sticky wrongness |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Mutability | Home-cell single-writer (or explicit CRDT) |
| Durability | ACK only after durable/quorum as required |
| Privacy | Minimization, encryption, retention, on-device first where possible |
| APIs | Versioned, idempotent mutations, clear 429/409 |
| Scale path | 1× correct → 10× shard → 100× cells/planes → 1000× hierarchy/offload |
| Offline | Journal + conflict policy when product needs it |

### 6.2 Top risks for Search Typeahead (Client/Server, Privacy of Query Logs)

1. Underestimating the hottest plane from §2  
2. Privacy logging accidents  
3. Split-brain across regions  
4. Missing fencing on leadership/leases  
5. Migration/cutover without verifier  
6. Fail-open on abuse-sensitive paths  

### 6.3 45–60 minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Clarify FR/NFR; Apple privacy/offline boundary |
| 5–12 | APIs + invariants + state machines |
| 12–22 | HLD planes + diagram |
| 22–35 | Deep dive reliability + scale jumps |
| 35–45 | Trade-offs, deal-breakers, wrap |
| +15 | Extra: migration/security/chaos if senior |

### 6.4 60-second summary

> Design Search Typeahead (Client/Server, Privacy of Query Logs) with explicit planes, durable ACK semantics, authz-before-data, privacy-minimized telemetry, and a progressive path from correct MVP to cell-based scale—calling out on-device/server boundaries and residency where Apple interviewers probe.

---

## 7. Deeper / Related Interview Questions

### 7.1 Correctness & SoT

**Q: What is your source of truth?**  
A: Name one SoT per entity class; caches/indexes are derived. Dual-write only during migrations with a verifier.

**Q: How do you prevent IDOR?**  
A: Unpredictable IDs + authz check on every access keyed by resource; never rely on obscurity alone.

**Q: Fail-open or fail-closed?**  
A: Abuse/authz/privacy paths fail-closed; some read-only best-effort features may fail-open with local defaults—say which.

**Q: How do you handle multi-region?**  
A: Active-active edge; single-writer home cell for mutations; residency SKUs explicit.

### 7.2 Privacy, auth, offline

**Q: What PII leaves the device?**  
A: List fields. Prefer on-device aggregation. Justify each server-bound category with consent.

**Q: How do you delete data?**  
A: API → tombstone → async purge → verify zero; legal hold gate; prevent offline resurrection via epochs.

**Q: How do you version APIs?**  
A: Additive changes; deprecation windows; client capability negotiation.

**Q: What is your degrade mode?**  
A: Shed secondary features first (recs, analytics, non-critical sync); keep auth and primary read/write if possible.

**Q: How do you test disaster?**  
A: Game days: kill leader, partition cell, replay DLQ, revoke certs, burst 10× traffic.

### 7.3 APIs, rollouts, capacity

**Q: Where is encryption?**  
A: TLS in transit; envelope encryption at rest; optional E2EE; key rotation & custody story.

**Q: How do you stop thundering herds?**  
A: Jitter, singleflight, staggered cron, admission control, cache early refresh.

**Q: What's the biggest unit-check mistake?**  
A: TB vs PB on storage math; correct it aloud.

**Q: Offline conflict policy?**  
A: Pick: LWW with caution, conflict copies, CRDT merge, or server sequencer reject—match file/doc type.

**Q: How are secrets handled?**  
A: Short-lived credentials via identity federation; HSM for signing; never log tokens.

### 7.4 Operability & degrade

**Q: How do you ensure idempotency?**  
A: Idempotency keys with durable map; natural keys for ledger entries; fencing for leases.

**Q: Observability without privacy violations?**  
A: Scrubbers, allowlisted fields, aggregate dashboards, separate audited break-glass raw access.

**Q: How do you capacity-plan?**  
A: From §2 load classes; provision on p99; include rebuild/migration bandwidth reservations.

**Q: What would you defer from MVP?**  
A: Be explicit; keep invariants; defer fancy global optimization / perfect E2EE if not required.

**Q: How does authn relate to authz?**  
A: Authn establishes principal; authz checks relation tuples/ACLs per action; don't conflate.

**Q: How do you roll out dangerous changes?**  
A: Canary → staged → full; automatic halt on SLO; dual-read flags for storage/auth migrations.

### 7.5 Search Typeahead (Client/Server, Privacy of Query Logs)-specific

**Q: Personalization without server profiles?**  
A: On-device features; server rank generic.

**Q: Trending without raw logs?**  
A: DP sketches / counts with delay.

### 7.6 Comparison traps

**Q: Why not put everything in Kafka?**  
A: Great as buffer/bus; awkward as mutable lease/ACL/balance SoT.

**Q: Why not one global strongly consistent DB?**  
A: Latency and blast radius; cells + explicit SKUs scale better.

**Q: Why not pure on-device?**  
A: Collaboration, multi-device, anti-fraud, and some availability need server—bound it.

---

## 8. Appendices

### 8.1 Schema / record sketches

```text
# Generic durable record
id: UUID
home_cell: str
version: int
created_at / updated_at
deleted_at: optional tombstone
acl / owner_id
payload_ref: optional object pointer
content_hash: optional
```

Topic accents for **Search Typeahead (Client/Server, Privacy of Query Logs)** live in interview whiteboarding—map fields to your entities (Job, Volume, File, Hand, RouteRequest, etc.).

### 8.2 API checklist

- [ ] Authn + authz on every route
- [ ] Idempotency-Key on creates
- [ ] Conditional updates (If-Match / expected_version)
- [ ] Rate-limit headers / 429
- [ ] Privacy export/delete
- [ ] Admin audit
- [ ] Health/readiness separation
- [ ] Pagination cursors
- [ ] Error taxonomy documented
- [ ] Compatibility versioning

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Home cell | Single-writer region/cell for an entity |
| Fencing token | Epoch/lease id preventing stale writers |
| SoT | Source of truth |
| Tombstone | Deletion marker preventing resurrection |
| DP | Differential privacy |
| CAS | Content-addressed storage |
| Shuffle sharding | Map tenant to random subset of shards |
| Outbox | Durable events in same TX as state change |
| E2EE | End-to-end encryption |
| ABR | Adaptive bitrate streaming |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Correct invariants, authz, durable ACK, privacy boundary |
| 10× | Shards, cache, async, rate limits |
| 100× | Cells, plane splits, isolation, residency |
| 1000× | Hierarchy, edge/on-device offload, tiering, clean-room analytics |

### 8.5 Privacy review checklist (Apple-weighted)

- [ ] Data inventory per field
- [ ] Consent / purpose binding
- [ ] Retention + deletion verification
- [ ] Log scrubbers
- [ ] On-device alternatives considered
- [ ] Residency constraints
- [ ] Third-party sharing none-by-default
- [ ] Break-glass access audited

### 8.6 Reliability test plan

1. Kill primary/leader → fence + elect → no split-brain writes.  
2. Inject duplicate client retries → idempotent outcomes.  
3. Partition home cell → edge read-only degrade.  
4. Poison deploy → canary halt.  
5. Privacy delete → bytes gone; stale device cannot resurrect.  
6. Hot key / noisy tenant → isolation holds.  

### 8.7 Observability SLOs (templates)

| SLO | Example |
|-----|---------|
| API availability | 99.9% monthly |
| Critical path latency | p99 within budget |
| Durability | 0 acknowledged loss |
| Privacy delete completeness | 99.99% within T days |
| Mismatch rate (migrations) | < 1e-8 sampled |
| DLQ / error rate | Burn-rate alerts |


## 9. Extended Deep Dive — Search Typeahead

### 9.1 Apple platform context

Apple interviewers expect explicit treatment of **privacy** (what is logged/stored), **authentication** (human SSO + service mTLS), **offline/degraded behavior**, and **on-device vs server** boundaries. This section maps those lenses onto search typeahead.

### 9.2 Auth model

```text
Human operator → SSO + MFA → control plane RBAC (least privilege)
Service caller  → mTLS SPIFFE → scoped JWT (tenant, role, aud)
End-user device → Apple ID session + device trust (if applicable)
Break-glass     → time-boxed elevation + mandatory audit ticket
```

Never fail open on auth uncertainty — especially for admin or data-export paths.

### 9.3 Privacy & data minimization

| Artifact | Retention | Logged? |
|----------|-----------|---------|
| Request payloads | Process-only or TTL | Never raw in prod logs |
| User identifiers | Opaque hashes in metrics | Hash only |
| Audit records | 1–7 years policy | Actor + action + resource id |
| Debug captures | Staging only | Scrubbed |

For search typeahead, classify every field before adding to schemas (public / internal / confidential / restricted).

### 9.4 On-device vs server split

| Concern | On-device (if any) | Server |
|---------|-------------------|--------|
| Primary UX | Local cache, optimistic UI | Authoritative state |
| Secrets | Secure Enclave / Keychain | Vault + HSM |
| Heavy compute | When privacy-critical | Fleet scale |
| Sync | Bounded offline queue | Home-cell writer |

State explicitly what **never leaves the device** vs what may sync — interviewers reward crisp boundaries.

### 9.5 Offline & degraded modes

```text
Online:     full feature set; strong auth checks
Degraded:   read-only or cached responses; writes spooled (cap 100 ops / 10MB)
Offline:    local-only operations documented; no silent data loss
Reconnect:  idempotent replay; merge conflicts per documented policy
```

Security-sensitive operations (auth migration, PII export, cutover flags) require online step-up auth.

### 9.6 Reliability invariants

1. Durable writes acknowledged only after replication/quorum.
2. Idempotency keys on all client mutations (24h+ dedupe window).
3. Single home writer per entity shard (cell model) — no dual writers.
4. Epoch/generation fences after failover to reject stale operations.
5. Rollback path for every production flag change.

### 9.7 Failure mode matrix

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Hot key / shard | Latency SLO burn | Split shard; isolate tenant |
| Region outage | Health checks | Failover to DR cell; epoch bump |
| Auth provider down | 401 spike | Fail closed; cached read-only if safe |
| Queue backlog | Depth alert | Scale consumers; shed low priority |
| Bad deploy | Error rate canary | Auto rollback; feature flag off |
| Privacy leak in logs | Scanner | Scrub pipeline; incident response |

### 9.8 Progressive scale (10× → 100× → 1,000×)

| Jump | Architectural change |
|------|------------------------|
| 10× | Horizontal shard; separate read replicas; regional deployment |
| 100× | Cell isolation; async pipelines; hot-key cells |
| 1,000× | Hierarchical aggregation; approximate structures; edge caching |

Name the **first bottleneck** you expect for search typeahead (usually hot keys, write QPS, or cross-region latency).

### 9.9 Back-of-envelope refresher

```text
Peak QPS ≈ average QPS × (3 to 10)
Storage/year ≈ daily_new_records × record_size × retention_days × replica_factor
Memory_working_set ≈ active_entities × object_size × hot_fraction
Cross-region RTT ≈ 80–150ms — design avoids sync cross-ocean on hot path unless required
```


### 9.20 Open questions to ask interviewer

1. Is Advanced Data Protection / E2E required?
2. Multi-region active-active or home cell?
3. On-device component in scope?
4. Exact consistency requirements per operation?
5. Compliance regime (GDPR, hiring law for ATS)?




---


## 9. Extra deep dive — Typeahead privacy

### 9.1 Client/server split
Client: debounce, FST/LRU, on-device personalization.
Edge: head-query cache.
Server: full index + safety.
Logs: DP/aggregates—not raw dossiers.

### 9.2 Latency budget
```text
keystroke → local <10ms; edge p99 <100–150ms; server enrich optional
```

### 9.3 Ranking
prefix popularity + language + on-device features − safety penalty.

### 9.4 Freshness
Nearline trending via sketches; deny-lists for abuse.

### 9.5 Offline
Ship compact locale FST slice (tens–hundreds MB).

### 9.6 Privacy math
ε budgets; short TTL samples if any; prefer zero raw retention.

### 9.7 Abuse
Auth + rate limits; poison query injection filtered.

### 9.8 Deal-breakers
Forever raw query logs; server-side personalization profiles by default; blocking UI on server RTT.

### 9.9 60s summary
> Edge+on-device typeahead, privacy-preserving analytics, safety filters, progressive indices—not a full search engine.

## 9. Forced depth appendix (interview ammo)

### 9.1 Drill card 1

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.2 Drill card 2

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.3 Drill card 3

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.4 Drill card 4

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.5 Drill card 5

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.6 Drill card 6

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.7 Drill card 7

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.8 Drill card 8

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.9 Drill card 9

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.10 Drill card 10

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.11 Drill card 11

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.12 Drill card 12

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.13 Drill card 13

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.14 Drill card 14

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


### 9.15 Drill card 15

| Prompt | Answer sketch |
|--------|---------------|
| Hottest plane? | Name QPS/bytes class from §2 |
| Privacy boundary? | On-device vs server fields |
| Failure? | Fence + idempotent retry |
| 10× move? | Shard/batch/cache |
| 100× move? | Cells + plane split |
| Deal-breaker? | Dual-write SoT / raw PII logs / unfenced leader |

**Say:** invariants first, then scale, then Apple offline/privacy boundary.


---

*End of document.*
