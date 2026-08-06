# System Design: Trip / Marketplace Event Pipeline

> **Focus areas:** Event bus · Schema registry · Outbox · Consumers · Ordering · Idempotency · Replay · Fan-out  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — **durable marketplace event pipeline connecting trip, pricing, dispatch, notify, pay, analytics**

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

Goal: design an event pipeline for trip/marketplace domain events with producer guidelines, schema evolution, delivery guarantees, consumer patterns, replay, and progressive scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Durable event transport + contracts | Replace OLTP trip SoR |
| Truth | Producer outbox + log partitions | Best-effort metrics UDP only |
| Uber lens | Trip events → many consumers | Generic Kafka tutorial |
| Guarantee | At-least-once + idempotent consumers | Magic exactly-once everywhere |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Producers? | Trip, pricing, dispatch, pay | Outbox required |
| F2 | Schemas? | Avro/JSON + registry | Compat rules |
| F3 | Topics? | Domain streams | Naming standards |
| F4 | Ordering? | Per trip_id key | Partition key |
| F5 | Fan-out? | Many consumer groups | Independent lag |
| F6 | Replay? | Time/offset rebuild | Retention + tools |
| F7 | PII? | Tokenize/minimize | Policy |
| F8 | DLQ? | Poison messages | Quarantine |
| F9 | Sync vs async? | Critical path uses outbox async | No dual-write without outbox |
| F10 | Multi-region? | Per cell logs | Mirror carefully |
| F11 | Backfill? | From event store/lake | Jobs |
| F12 | Observability? | Lag SLOs | Per group |

**MVP functional scope (lock with interviewer):**

1. Transactional outbox on trip/payment mutations.
2. Kafka (or equivalent) topics keyed by entity id.
3. Schema registry with backward-compatible evolution.
4. Consumer library: idempotent inbox, retry, DLQ.
5. Retention for replay (e.g. 7–30d hot).
6. Lag dashboards + poison tooling.
7. Document event catalog (trip.assigned, fare.finalized, …).

**Out of MVP (explicitly defer):**

- Global total-order bus
- Active-active multi-writer same partition without home cell

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Produce latency | Outbox publish | p99 < 1–2s to bus |
| N2 | Consumer lag | Critical groups | SLO per group |
| N3 | Durability | No silent drop | RF>=3 / quorum |
| N4 | Ordering | Per key | partition key=entity |
| N5 | Schema safety | Compat | CI registry checks |
| N6 | Replayability | Rebuild projections | retention |
| N7 | Isolation | Noisy consumer | separate groups |
| N8 | Throughput | Peak trips | See scale |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Trip assign writes DB+outbox → publisher → trip.assigned → notify+analytics.
2. Consumer retries safely via inbox dedupe.
3. Schema adds optional field; old consumers fine.
4. Replay last 24h rebuilds read model.
5. DLQ holds poison; ops fix & redrive.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Dual write without outbox | Forbidden pattern |
| Hot trip_id partition | rare; monitor |
| Poison nulls | DLQ |
| Incompatible schema push | Registry blocks |
| Consumer bug replay amplifies | versioned handlers |
| PII in payload | schema linter |
| Lag during deploy | pause/drain playbooks |
| Cross-cell mirror loops | headers/source |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Events/s peak | 20K | 200K | 2M | 20M |
| Topics | 20 | 50 | 200 | many cells |
| Consumer groups | 15 | 40 | 100+ | mesh |
| Retention hot | 7d | 14d | tiered | lake |
| Cells | 1–2 | many | many | hierarchical |

**What each jump forces:**

- **10×:** More partitions; outbox batcher
- **100×:** Cell-local buses; tiered storage
- **1,000×:** Hierarchical aggregates; strict catalog governance

### 1.5 Etc. (Constraints & Assumptions)

- Design for retries, idempotency, and city/region isolation.
- Fail closed on authz/money; degrade intentionally on non-critical paths.
- Peak ≠ average; stadium/airport spikes are first-class.
- OLTP remains system of record; events are facts for consumers.
- At-least-once delivery; consumers must be idempotent.

**Scope statement:**

> Marketplace event pipeline: outbox producers, schema registry, keyed partitions, consumer inbox/DLQ, replay, lag SLOs, cell isolation.

---

## 2. Back-of-the-Envelope Estimation

### Volume

```text
5M trips/day × ~10 events ≈ 50M/day ≈ 580/s avg; peak 20× → ~10K/s; 100× cities compound
```

### Size

```text
1KB avg → 10MB/s peak baseline; plan compression
```

### Retention

```text
10K/s × 1KB × 86400 × 7 ≈ 6TB/week order before compression
```

### Bottlenecks (rank ordered)

1. Hot partitions
2. Slow consumers blocking? (no—per group)
3. Schema fights
4. Outbox table growth
5. Fan-out storage cost
6. Cross-region mirror

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
DomainEvent
OutboxRecord
TopicPartition
ConsumerInbox
SchemaVersion
DLQItem
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Dual write DB+Kafka | Easy | Lost events | Money/notify |
| B. DB CDC only | No app outbox | Opaque/business coupling | Need careful |
| C. Transactional outbox + bus + registry | Reliable | Ops | — chosen |
| D. HTTP webhooks only | Simple | Fan-out fragile | Many consumers |

**Chosen path:**

- Transactional outbox from SoR services → publisher → Kafka topics keyed by entity → idempotent consumers with DLQ.
- Schema registry compatibility enforced in CI.

### 3.3 Core design mechanics

**Produce:** business TX writes row + outbox row; publisher emits; marks published.

**Consume:** poll → inbox insert by event_id → handle → commit offsets carefully (or inbox-first).

**Invariant:** No business side effects without durable outbox; consumers idempotent on event_id; schemas evolve compatibly.

### 3.4 API sketch

```text
# Not primarily REST—contracts:
topic trip.events  key=trip_id  value=Envelope{type, id, ts, payload, schema_ver}
topic fare.events  key=trip_id
topic dispatch.events key=task_id
Admin: POST /internal/pipeline/redrive {dlq_id}
GET /internal/pipeline/lag
```

### 3.5 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Outbox vs CDC | Clear business events vs lower app code |
| Many topics vs few | Isolation vs ops sprawl |
| Long retention | Replay vs cost |
| Sync RPC fan-out | Avoid on critical writes |



---

## 4. Architecture Diagram

```text
Trip/Pay/Dispatch DBs → Outbox → Publisher → Kafka (keyed)
                                      |-> Notify CG
                                      |-> Analytics CG
                                      |-> Payments CG
                                      |-> Search/index CG
Schema Registry  DLQ/Redrive tools  Lag SLO monitors
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- Outbox poller HA with leases.
- Idempotent inbox.
- DLQ + redrive.
- Poison schema detection.
- Cell isolation on failure.

**Delivery / consistency cheat-sheet**

| Layer | Guarantee |
|-------|-----------|
| Client → API | At-least-once; idempotency keys where mutations exist |
| System of record | Single-writer per entity / partition key |
| Downstream effects | At-least-once via outbox/stream; idempotent consumers |
| Reads | Read-your-writes on primary; replicas may lag |

**Deal-breakers**

- Dual-write without outbox/CDC discipline
- Non-idempotent money consumers
- Breaking schema changes silently
- One shared consumer group for unrelated domains

### 5.2 Scalability

- Partition by entity key; cell-local clusters; compress; tier to lake; hierarchical aggregates for metrics.

**Progressive evolution**

| Scale | Architecture posture |
|-------|----------------------|
| Baseline | Single region/city; simple durable store + stream |
| 10× | Shard by city/entity; split hot paths |
| 100× | Cells, async fan-out, careful caching, hot-key splits |
| 1,000× | Hierarchical aggregation, edge where safe, strict cost/isolation |

### 5.3 Maintainability

- Event catalog owned; compatibility CI; contract tests per consumer.

- Versioned schemas/configs with rollback.
- Golden fixtures and replay tools for disputes/regressions.
- Published ownership boundaries between services.
- SLOs tied to user-visible failures; load-test stadium/airport peaks.

### 5.4 Multi-region clarity

| Plane | Mode |
|-------|------|
| Edge / API gateways | Active-active |
| Mutable entity writes | Home cell / city region single-writer |
| Caches / projections | Regional, eventually consistent |
| Analytics | Async lake / warehouse |

### 5.5 Security, privacy, abuse

- ACLs per topic; PII minimization; encrypt at rest; audit redrive.

---

## 6. Wrap-Up

**What to say in 60 seconds**

> Marketplace events leave SoR via transactional outbox onto keyed Kafka topics with schema registry, idempotent consumers, DLQ/replay, and lag SLOs—never dual-write and never assume exactly-once without inbox discipline.

**MVP → next**

1. MVP: invariants + audit/outbox + single-city correctness.
2. Next: sharding, richer consumers, degradation playbooks.
3. Later: edge optimizations, hierarchical aggregation, advanced models with caps.

**Top risks**

| Risk | Mitigation |
|------|------------|
| Hot keys / stadiums | Split shards, jitter, admission control |
| Retry storms | Idempotency, client jitter, coalescing |
| Inconsistent side effects | Outbox + consumer idempotency |
| Cost explosion | Sampling, TTL, tiered storage |
| Trust / correctness bugs | Audit, clamps, kill switches |

---

## 7. Deeper / Related Interview Questions

### Guarantees

**Q: Exactly-once?**  
A: Effectively via idempotent consumers + dedupe; bus is at-least-once.

**Q: Ordering across trips?**  
A: Not required; per trip_id yes.

### Schema

**Q: Add field?**  
A: Optional field backward compatible; CI checks.

### Scale & multi-region

**Q: How do you shard?**  
A: City/region cell first, then hash entity id within the cell.

**Q: Active-active writes for the same entity?**  
A: Avoid; home-cell single-writer with fencing on failover.

**Q: What do you shed first under load?**  
A: Non-critical analytics/marketing; protect money, safety, and trip-critical paths.

### Interview arithmetic / trap questions

**Q: When do units go wrong?**  
A: Mixing MB/GB/PB; using average instead of peak; forgetting retries amplify QPS; storing forever without sampling.

**Q: What do you defer explicitly?**  
A: Active-active multi-writer; perfect exactly-once for arbitrary side effects; unbounded history in primary OLTP.

**Q: What is the system of record?**  
A: Name it aloud—everything else is a projection/cache.

---

## 8. Appendices

### 8.1 Envelope

```json
{"event_id":"e","type":"trip.assigned","key":"trip_...","ts":"...","schema_ver":3,"payload":{}}
```

### 8.2 Catalog excerpt

trip.assigned, trip.completed, fare.finalized, dispatch.offered, payment.captured

### 8.3 SLOs

| SLO | Target |
|-----|--------|
| Outbox→bus p99 | <2s |
| Critical CG lag | <5–15s |
| Poison rate | low |

### 8.4 Anti-patterns

DB transaction + sync HTTP to 5 services; huge god-topic; payload embeds full PII blobs

### Interview checklist

- [ ] Clarified MVP vs out-of-scope
- [ ] Progressive 10×/100×/1000× impacts stated
- [ ] Estimation with peak ≠ average
- [ ] Single-writer / fencing story
- [ ] Idempotency + retries
- [ ] ASCII architecture
- [ ] Reliability / scalability / maintainability deep dive
- [ ] Explicit deal-breakers
- [ ] Deeper Q&A ready
- [ ] Audit / privacy / money hooks if relevant

---

*End of trip / marketplace event pipeline system design.*

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.
