# System Design: Retry-Safe Idempotent Payment Processing

> **Focus areas:** Idempotency deep dive · PROCESSING · Inquiry · Rail uncertain  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** API correctness, idempotency, ledger/regional failure awareness, explicit deal-breakers, integer money where applicable  
> **Interview type:** **HLD / architecture** — Stripe emphasizes correctness, rollout, and ops—not only box diagrams

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

Goal: deep-dive **retry-safe idempotent payment processing**—idempotency store mechanics, PROCESSING, body hash, inquiry, ledger key coupling.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|---|---|---|
| F1 | Key scope? | Per merchant endpoint | Global unique OK |
| F2 | Body hash? | SHA256 canonical JSON | 409 mismatch |
| F3 | PROCESSING? | Visible state | Sweeper resolves |
| F4 | Retention? | Years captures | Not 24h |
| F5 | Client guidance? | Same key retry | Never new key same event |
| F6 | Rail timeout? | Inquiry rail | Not blind retry |
| F7 | Response cache? | Store full HTTP | Replay identical |
| F8 | Ledger key? | Match payment key | Recon link |
| F9 | Partial? | Idempotent partial capture | Amount in hash |
| F10 | Webhooks? | After commit | Stable ids |
| F11 | Metrics? | 409 rate stuck age | Alert |
| F12 | Testing? | Chaos duplicate POST | Property tests |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/resources` — idempotent where mutating.
2. `GET /v1/resources/{id}` — idempotent where mutating.
3. Domain audit trail for Retry-Safe Idempotent Payment Processing
4. Admin recon/replay hooks for Retry-Safe Idempotent Payment Processing
5. Integration with idempotency + outbox patterns

**Out of MVP (explicitly defer):**

- Multi-master active-active writers on same strong-consistency shard
- Exactly-once end-to-end without client idempotency cooperation
- Replacing all Stripe production systems in one Retry-Safe Idempotent Payment Processing design
- Ad-hoc arbitrary SQL on primary OLTP for analytics

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|---|---|---|
| N1 | Write / mutate latency | Sync where applicable | p50 < 20ms, p99 < 100ms in-region |
| N2 | Read latency | Dashboard + API | p99 < 200ms; RYW for critical reads |
| N3 | Durability | Accepted state changes | Quorum commit before ACK |
| N4 | Availability | Domain-critical paths | 99.99% home cell; degrade reads first |
| N5 | Idempotency retention | Money-adjacent if applicable | Years — not 24h-only |
| N6 | Multi-region | Global edge | Single-writer home per shard + fencing |
| N7 | Audit retention | Compliance | Hot months + cold forever |
| N8 | Scale target | 1000× headroom | See progressive scale table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Key scope? → Per merchant endpoint → durable write + audit
2. Body hash? → SHA256 canonical JSON → correct domain behavior
3. Retry with same Idempotency-Key → stored response (no double effect)
4. Read-after-write from home cell → RYW consistent state
5. Client guidance? → safe degradation documented
6. Regional failover → epoch fence → outbox replay → recon before resume

**Edge / failure cases**

| Case | Behavior |
|---|---|
| Dup key same body | 200 |
| Dup key diff body | 409 |
| Timeout after commit | Idempotent retry |
| Hot shard | Isolate |
| Regional fail | Fence+replay |
| Duplicate idempotency key, same body | 200 + stored response |
| Duplicate key, different body | 409 idempotency_error |
| Write timeout after commit | Client retry → idempotent return |
| Stuck PROCESSING idempotency | Sweeper + upstream inquiry |
| Hot tenant / shard | Isolate cell; serialize or sub-shard |
| Regional partition | Home authority; edge fail-closed for critical writes |
| Outbox worker lag | Scale workers; alert; no duplicate apply if consumer idempotent |
| Cache stale on critical read | Bypass or version check against home SoT |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|---|---|---|---|---|
| Peak write QPS | 100 | 1K | 10K | 100K |
| Peak read QPS | 1K | 10K | 100K | 1M |
| Tenants | 10K | 100K | 1M | 10M |

**Split QPS classes:** writes ≠ reads ≠ async fanout ≠ audit export. Do not lump into one number.

**What each jump forces:**

- **10×:** Idempotency+outbox+replicas  
- **100×:** Directory+cells+hot isolation  
- **1,000×:** Regional homes+partitions+archive

### 1.5 Etc. (Constraints & Assumptions)

- Integer minor units for money.
- Exactly-once effect via idempotency keys.
- Typed stable API errors.
- Regional failure: fence, replay, recon.

**Scope statement:**

> Deep-dive idempotent payments ~1K QPS retry storms safe.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
See scale table
Peak/average ratio ~3–4× for burst planning
Split classes: sync writes, sync reads, async workers, audit/export
```

### 2.2 Storage

```text
~1KB/row tiered
Idempotency records: same order as writes; retain long for money paths
Audit/log: append-only; tier hot → cold object store
Unit-check discipline: 1e9 rows × 1 KB = 1 TB (not PB)
```

### 2.3 Bandwidth

```text
Regional cells at 1000x
Internal replication (WAL/outbox) similar order to write bandwidth
```

### 2.4 Memory

```text
Sharded hot sets
Working set for hot keys: partition by hash; never single global Redis
```

### 2.5 Bottleneck ranking (interview)

Idempotency, hot keys, outbox

**Say early:** correctness and API semantics > raw QPS.

### 2.6 Domain-specific note

```text
Split read/write QPS
```

---

## 3. High-Level Design

### 3.1 Core entities

```text
Resource
  IdempotencyRecord
  AuditEnvelope
  OutboxEvent
Directory: tenant/shard → home cell (epoch)
IdempotencyRecord (key, hash, status, response)
Outbox → downstream at-least-once (consumers idempotent)
AuditEnvelope (who, when, request_id, diff)
```

### 3.2 Sacred invariant

```text
Accept implies durable commit before ACK; idempotent keys prevent double effect
```

**Deal-breaker:** acknowledging success before durable commit on money-adjacent paths.

### 3.3 Core protocol

```text
Auth validate TX idempotency domain write outbox commit ACK
```

**Ordering:** durable local state **before** external side effects (rail, webhook, third-party route).

### 3.4 API surface (product)

| API | Semantics |
|---|---|
| `POST /v1/resources` | Idempotent / typed errors / RYW where applicable |
| `GET /v1/resources/{id}` | Idempotent / typed errors / RYW where applicable |

Stripe-flavored: `Idempotency-Key`, `Request-Id`, typed errors, expandable objects.

### 3.11 Domain model (Retry-Safe Idempotent Payment Processing)

Core entities in section 3.1 compose the write path: validate invariants in TX, append audit, emit outbox.

### 3.12 Idempotency integration

All mutating APIs accept `Idempotency-Key` scoped to tenant. Body hash detects client bugs (409 conflict).

### 3.13 Async boundary

External systems (rails, routers, webhooks, third parties) invoked **after** local durable commit via outbox workers with stable external keys.

### 3.14 Retry-Safe Idempotent Payment Processing — regional home

Directory maps shard key → home cell + epoch. Failover bumps epoch; zombie writers fenced.

### 3.5 Read path

| Data class | Consistency | Mechanism |
|------------|-------------|-----------|
| Money / inventory / assignment state | Strong RYW | Home cell + version |
| Lists / dashboards / rankings | Eventual OK | Replicas + cache with SLO |
| Audit history | Strong per id | Primary or bounded-lag replica |

### 3.6 Async / integration

```text
Domain TX commits → outbox row
Worker claims with lease → external call with stable idempotency key
Timeout → inquiry, not blind new key
Ledger: journal_key = f(domain_transition_id) where applicable
```

### 3.7 Multi-region

| Plane | Mode |
|-------|------|
| API edge | Active-active |
| Durable writes | **Home cell per shard** |
| Reads | RYW via home; stale OK for analytics |
| Failover | Epoch fence + WAL/outbox replay + recon |

### 3.8 Storage trade-offs

| Data | Store | Why |
|------|-------|-----|
| Primary domain rows | Strong SQL / Spanner | TX + constraints |
| Idempotency | SQL unique + cache | Correctness + speed |
| Outbox | Same TX as domain | Reliable async |
| Audit | Append-only log | Compliance |
| Cache | Redis with TTL | Latency — not SoT for money |

### 3.9 Rollout & operations

- **Dark launch:** shadow traffic, compare outputs.  
- **Feature flags:** per-tenant rollout; default safe on outage.  
- **Expand/contract migrations:** nullable column → backfill → enforce.  
- **Recon jobs:** compare external vs internal; open breaks as tickets.  
- **Runbooks:** stuck PROCESSING, failover, hot shard, DLQ depth.

### 3.10 Deal-breakers (say early)

| Temptation | Failure |
|---|---|
| ACK before durable | Ghost state |
| Skip idempotency | Double effect |
| Multi-master shard | Split brain |

---

## 4. Architecture Diagram

### 4.1 End-to-end (Retry-Safe Idempotent Payment Processing)

```text
Clients / Services → API Gateway (auth, rate limit)
        → Retry-Safe Idempotent Payment Processing API → Directory → Home Cell
              (domain store + idempotency + audit + outbox)
        → Async workers → External deps / Ledger / Webhooks
        → Observability (metrics, traces)
```

### 4.2 Idempotent write sequence

POST + Idempotency-Key → TX → domain mutation → outbox → commit → 200; retry → identical response.

### 4.3 Uncertain external dependency

Worker calls external API with stable idempotency key → timeout → inquiry (same key) → classify → complete or compensating action.

### 4.4 Regional failover

Detect cell failure → fence epoch → promote secondary → replay outbox gap → recon → resume traffic.

### 4.5 Read path

GET by id → route home → RYW from primary or version-checked cache; list queries may use replica with lag bound.

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable** before client success on critical writes.  
2. **Idempotent mutations** by `(tenant, idempotency_key)` + body hash.  
3. **Append-only audit** — corrections are new records, not edits.  
4. **Single-writer home** per shard for strong consistency domains.  
5. **Outbox** for async side effects; at-least-once with idempotent consumers.  
6. **Fencing tokens** on failover to prevent zombie writers.  
7. **Integer money** where applicable — no floats.  
8. **Recon breaks** visible — never silent fix.  
9. **Typed errors** — idempotent replay must not flip 200↔500 arbitrarily.  
10. **Rate limit + auth** fail closed on money paths when uncertain.

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Client retry storm | Idempotency + 409 PROCESSING policy |
| Worker crash after external success | Inquiry + stable external key |
| Hot shard | Split keyspace; isolate tenant; shed reads |
| Regional partition | Home cell authority; edge read-only degrade |
| Cache stampede | Jitter TTL; single-flight |
| Poison message | DLQ + alert |
| Schema migration error | Expand/contract; rollback flag |

**Resolved:** "exactly-once" = **idempotency keys + durable TX + no second economic effect**.

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Modular monolith; single primary DB; basic cache |
| 10× | Service boundary; outbox; idempotency cache; read replicas |
| 100× | Shards + directory; cells; hot-key isolation; cold tier |
| 1000× | Regional homes; stream processors; adaptive shed; archive tier |

**Hotspot patterns:** detect early via p99 skew; isolate; preaggregate; never weaken invariants.

### 5.3 Maintainability

- Property tests for domain invariants.  
- Contract tests for API error shapes and replay behavior.  
- Chaos drills: kill after commit, duplicate requests, failover mid-TX.  
- Versioned recipes / policies / workflow definitions.  
- Ops dashboards: idempotency age, outbox lag, recon open count.

### 5.4 Progressive scale deep dive

**1× (baseline):** Single region primary; TX per write; idempotency unique constraint; nightly recon.

**10×:** Extract service; Redis cache; outbox workers; continuous recon; feature flags.

**100×:** Directory sharding; cells; hot tenant isolation; CQRS read models.

**1000×:** Multi-region homes; time partitions; adaptive concurrency; archive tier; load shed reads first.

### 5.5 Concurrent same-key retries

```text
T0: Request A inserts idempotency PROCESSING
T1: Request B conflicts → 409 Retry-After or short poll
T2: A commits COMPLETE
T3: B reads COMPLETE → returns same response
Sweeper resolves stuck PROCESSING via inquiry — never new business key
```

### 5.6 Cross-shard operations

Prefer **single-shard TX**. Cross-shard: saga + outbox + compensating steps; document eventual completion.

### 5.7 Cache coherency

Money/inventory reads: short TTL + version OR bypass cache. Hint caches OK when stale SLO documented.

### 5.8 Rollout: dark launch

Shadow compare → cohort flag ON → authoritative cutover → remove legacy. Instant rollback = flag OFF + recon.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Float money | Rounding exploits |
| Edit audit history | Compliance failure |
| Multi-master same shard | Split brain |
| Skip idempotency | Double effect |
| ACK before durable | Ghost state |

### 5.10 Domain reliability

Invariants and outbox.

### 5.11 Domain scale

Shard and isolate hot keys.

### 5.12 Domain ops

Recon and runbooks.

### 5.13 Domain multi-region

Home cell fencing.

### 5.14 Domain cache

Version check money reads.

### 5.15 Domain rollout

Dark launch flags.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|---|---|
| Consistency | Single-writer home |
| Idempotency | Key+hash |
| Async | Outbox |

### 6.2 Risks

1. Hot shard
2. Stuck PROCESSING
3. Failover bugs

### 6.3 45-minute interview plan

| Min | Focus |
|---|---|
| 0-5 | Scope |
| 5-15 | API+entities |
| 15-25 | Idempotency |
| 25-35 | Multi-region |
| 35-45 | Scale |

---

## 7. Deeper / Related Interview Questions

### 7.1

**Q: Idempotency TTL?**  
A: Years for money.

### 7.2

**Q: Fail open?**  
A: Closed for money paths.

### 7.3

**Q: Float?**  
A: Never.

### 7.4

**Q: Exactly-once?**  
A: Effect via keys.

### 7.5

**Q: 1000x?**  
A: Shard+partition.

### 7.6

**Q: Ledger?**  
A: journal_key ties transition.

### 7.7

**Q: Regional?**  
A: SW home.

### 7.8

**Q: Recon?**  
A: First-class breaks.

### 7.9

**Q: Dark launch?**  
A: Shadow compare.

### 7.10

**Q: Integration round?**  
A: Coding not HLD.

### 7.11

**Q: Hot tenant?**  
A: Isolate cell.

### 7.12

**Q: Outbox?**  
A: Same TX.

### 7.13

**Q: Cache money?**  
A: Version or bypass.

### 7.14

**Q: PROCESSING?**  
A: Sweeper.

### 7.15

**Q: Webhook?**  
A: Stable event_id.

### 7.16

**Q: Pagination?**  
A: Cursor.

### 7.17

**Q: Delete history?**  
A: Append-only.

### 7.18

**Q: ABAC?**  
A: If auth topic.

### 7.19

**Q: Rate limit?**  
A: Edge first.

### 7.20

**Q: Trap float?**  
A: Minor units.

---

## 8. Appendices

### 8.1 Schema sketches

```text
resources(id,tenant_id,status,...); idempotency(...); outbox(...)
```

### 8.2 API request/response sketch

```text
POST /v1/resources → 201
```

### 8.3 State machine

```text
created → active → terminal
```

### 8.4 State / status checklist

- [ ] Resource lifecycle states enumerated  
- [ ] Idempotency: PROCESSING / COMPLETE / FAILED  
- [ ] Home cell epoch monotonic on failover  
- [ ] Outbox published_at null until worker ack  
- [ ] Audit actor + request_id on every mutation  

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Idempotency TX, integer money if applicable, basic audit |
| 10× | Outbox, cache, service split, recon jobs |
| 100× | Sharding, directory, hot isolation, CQRS reads |
| 1000× | Regional homes, partitions, archive tier, load shed |

### 8.6 Pseudocode

```text
handle: upsertIdem→apply→outbox→complete
```

### 8.7 Reliability / chaos drills

1. Duplicate POST same key → one resource.  
2. Kill pod after commit before response → client retry → same 200.  
3. Failover mid-TX → fence → no duplicate outbox side effect.  
4. External timeout → inquiry path → no double external call.  
5. Hot key storm → rate limit + isolate shard.  

### 8.8 Glossary

| Term | Meaning |
|---|---|
| Home cell | Single-writer shard region |
| Outbox | Durable async queue in TX |

### 8.9 Interview "say this" (60 seconds)

> We expose Stripe-style APIs with mandatory idempotency on mutations, durable commit before ACK, and typed errors. Strong-consistency domains use single-writer home cells with directory routing. Async work uses transactional outbox; external calls use stable idempotency keys and inquiry on timeout. Failover uses epoch fencing and recon before resuming money paths. We never use floats for money, never mutate audit history, and treat reconciliation breaks as first-class ops objects.

### 8.10 Related systems map

```text
API Edge → Retry-Safe Idempotent Payment Processing → Domain Store
                              │
                              ├─► Idempotency / Audit
                              ├─► Outbox → Workers → External / Ledger / Webhooks
                              └─► Metrics / APM / Rate limits
```

Related docs: ledger-bookkeeping, payment-processing.

### 8.11 HLD vs integration round

| Round | What you do |
|-------|-------------|
| **System design (this)** | APIs, data model, invariants, failure, scale, rollout |
| **Integration coding** | Parse Stripe docs, call APIs, transform JSON |

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| Float dollars | Integer minor units |
| CRDT for money/inventory SoT | Single-writer + TX |
| 24h idempotency TTL on payments | Retain for years |
| Global queue for all tenants | Per-tenant shuffle shard |
| Exactly-once HTTP marketing | At-least-once + idempotent consumers |

### 8.13 Ops metrics

- write_success / write_conflict_409 / write_latency_p99  
- idempotency_processing_age_p99  
- outbox_lag_seconds  
- recon_break_open_count  
- cell_epoch / failover_count  
- cache_hit_rate / stale_read_blocked  

### 8.14 Manual override controls

```text
POST /v1/admin/...  (dual control, reason code, audit sink)
```

### 8.15 Failure mode summary

| Component | Failure | User-visible | Mitigation |
|-----------|---------|--------------|------------|
| Home DB | Primary down | Write errors fail closed | Failover + fence |
| Idempotency | Stuck PROCESSING | 409 retry | Sweeper + inquiry |
| Outbox worker | Lag | Delayed side effects | Scale workers; alert |
| External API | Timeout | Pending state | Inquiry |
| Cache | Stale | Wrong read if misused | Version check |
| Edge region | Partition | 503 or route home | Directory health |

### 8.16 Sharding key selection

```text
Good: tenant_id, merchant_id, geo_cell, resource_id hash
Bad: status alone, country alone — hotspots
Reshard: dual-write + directory epoch bump + backfill verify
```

### 8.17 Compliance & audit

Immutable audit with retention tiers; legal hold; PII minimization; break-glass access with ticket.

### 8.18 Sample recon query

```text
daily: compare sum(internal) vs sum(external) per tenant
if |delta| > threshold → open recon_break
block automated money movement if severity=critical (policy)
```

---

*End of retry-safe idempotent payment processing system design.*

### 8.19 Retry-Safe Idempotent Payment Processing — rollout checklist

- [ ] Idempotency replay tests in CI  
- [ ] Failover runbook with epoch fencing  
- [ ] Recon job covers external dependencies  
- [ ] Feature-flag default safe on outage  
- [ ] Load test with 5% retry injection  

### 8.20 Retry-Safe Idempotent Payment Processing — load test profile

```text
warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak
inject: 5% duplicate idempotency keys, 1 regional failover at t=30m
assert: zero duplicate domain effects, recon breaks < threshold
```
