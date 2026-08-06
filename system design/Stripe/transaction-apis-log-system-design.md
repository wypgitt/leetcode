# System Design: Transaction APIs + Transaction Log

> **Focus areas:** Public transaction APIs · Append-only log · Idempotency keys · Strong consistency · Audit trail · Regional routing · API versioning  
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

Goal: bound the **transaction API + immutable log** layer—what gets logged, who may write, how reads relate to the log, and how idempotency ties API semantics to durable history.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|---|---|---|
| F1 | Who writes? | Merchant integrations + internal services via API keys | AuthN/Z; scoped write permissions per resource type |
| F2 | What is logged? | Every state transition as append-only log entry | Log is SoT for audit; resource row is materialized view |
| F3 | Idempotency? | Mandatory on POST/PATCH that mutate money-adjacent state | `Idempotency-Key` + body hash; long retention |
| F4 | Read models? | GET by id, list with filters, cursor pagination | Stable sort key; snapshot vs live documented |
| F5 | Versioning? | Explicit API version header / URL prefix | Expand/contract migrations; deprecation window |
| F6 | Consistency? | RYW for resource after write | Route reads to home cell or version token |
| F7 | Partial updates? | PATCH with optimistic concurrency (version/etag) | Reject stale writes with 409 |
| F8 | Cancel/reverse? | Terminal transitions via dedicated endpoints | Append CANCELLED log entry; never delete |
| F9 | Multi-tenant? | Strict merchant isolation | `merchant_id` on all rows; ACL on every query |
| F10 | Export/audit? | Immutable history forever | Hot OLTP + cold archive; legal hold |
| F11 | Webhooks? | Emit on log append via outbox | Stable `event_id`; at-least-once delivery |
| F12 | Ledger tie-in? | Economic transitions post journal after log commit | `journal_key` derived from `transaction_id:transition` |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/transactions` — create with idempotency.
2. `GET /v1/transactions/{id}` — fetch current state + latest log seq.
3. `GET /v1/transactions` — cursor list by merchant, status, time.
4. `POST /v1/transactions/{id}/cancel` — idempotent terminal transition.
5. Append-only transaction log with typed transitions.
6. Audit envelope on every mutation.

**Out of MVP (explicitly defer):**

- Full payment rail orchestration (see payment-processing doc)
- Merchant dashboard UI
- Real-time analytics warehouse (batch export only MVP)
- Multi-master active-active writers on same transaction home

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|---|---|---|
| N1 | Write latency | Sync on checkout path | p50 < 25ms, p99 < 120ms in-region |
| N2 | Read latency | Dashboard + polling | p99 < 150ms RYW from home |
| N3 | Durability | Accepted write ⇒ log entry | Quorum commit before ACK |
| N4 | Availability | High for writes | 99.99% home cell; degrade list reads |
| N5 | Idempotency retention | Years for money-adjacent | Never 24h-only TTL |
| N6 | Audit retention | Compliance forever | Hot months + cold object store |
| N7 | Multi-region | AA edge, SW home | Directory + epoch fencing |
| N8 | Scale | 1000× headroom | See progressive table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Merchant POST create with Idempotency-Key → log APPEND CREATED → 200 + transaction.
2. Retry same key + body → 200 + original (no second log entry).
3. Capture transition → log APPEND CAPTURED → outbox → webhook + ledger journal.
4. GET after POST from home cell → RYW consistent status.
5. List with cursor → stable ordering by `(created_at, id)`.
6. Cancel authorized-only txn → log APPEND CANCELLED; no capture side effects.

**Edge / failure cases**

| Case | Behavior |
|---|---|
| Duplicate key, same body | 200 + stored response; single log sequence |
| Duplicate key, different body | 409 idempotency_error |
| Write timeout after commit | Client retries → idempotent return |
| PATCH with stale version | 409 conflict; client refreshes |
| Illegal state transition | 400 invalid_request; no log append |
| Regional failover mid-write | Fence epoch; replay outbox; recon window |
| Hot merchant write storm | Shard by merchant; serialize per txn id |
| Log compaction request | Reject — append-only forever; archive old partitions |
| Cross-region read without home | 503 or stale with `livemode` header — document policy |
| Ledger post fails after log commit | Outbox retry; recon break if exhausted |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|---|---|---|---|---|
| Merchants | 50K | 500K | 5M | 50M |
| Peak **write** QPS | 500 | 5K | 50K | 500K |
| Peak **read** QPS | 5K | 50K | 500K | 5M |
| Log entries / day | 10M | 100M | 1B | 10B |
| Avg log entry size | 800 B | — | — | — |
| Idempotency hot keys | 100K active | 1M | 10M | 100M |
| Audit export jobs / day | 20 | 100 | 500 | 2K |
| Regional home cells | 2 | 3 | 6 | 12+ |

**Split QPS classes:** writes ≠ reads ≠ async fanout ≠ audit export. Do not lump into one number.

**What each jump forces:**

- **10×:** Partition log by merchant_id; idempotency sharded KV + SQL unique; outbox for webhooks.  
- **100×:** Directory service; dedicated cells for top merchants; CQRS read models from log stream.  
- **1,000×:** Time+merchant log partitions; regional homes sticky; sampled debug logs; archive tier automatic.

### 1.5 Etc. (Constraints & Assumptions)

- Log entries are **immutable** — corrections are compensating append entries.
- Integer minor units on all amount fields.
- API errors typed: `invalid_request_error`, `idempotency_error`, `api_error`.
- Exactly-once **effect** via idempotency — not one HTTP request in access logs.

**Scope statement:**

> Design public-facing transaction APIs backed by an immutable transaction log: idempotent writes, typed errors, pagination, audit forever, and single-writer home cells—from ~500 write QPS through 10× / 100× / 1,000× with correct retry semantics and ledger integration.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
10M log entries/day ÷ 86400 ≈ 115/s average; peak ~500/s at baseline.
Peak/average ratio ~3–4× for burst planning
Split classes: sync writes, sync reads, async workers, audit/export
```

### 2.2 Storage

```text
10M × 800 B ≈ 8 GB/day baseline; 1000× ≈ 8 TB/day (unit-check: not PB).
Idempotency records: same order as writes; retain long for money paths
Audit/log: append-only; tier hot → cold object store
Unit-check discipline: 1e9 rows × 1 KB = 1 TB (not PB)
```

### 2.3 Bandwidth

```text
5 KB req/resp × 500K write/s at 1000× ≈ 2.5 GB/s → regional cells.
Internal replication (WAL/outbox) similar order to write bandwidth
```

### 2.4 Memory

```text
Hot idempotency: peak_write × 3600s window × 400 B — shard across cells.
Working set for hot keys: partition by hash; never single global Redis
```

### 2.5 Bottleneck ranking (interview)

Idempotency uniqueness · log append throughput · hot merchant shard · outbox fanout

**Say early:** correctness and API semantics > raw QPS.

### 2.6 Domain-specific note

```text
Read:write often 10:1; split list queries to read replicas with lag bound.
```

---

## 3. High-Level Design

### 3.1 Core entities

```text
Transaction
  TransactionLogEntry
  IdempotencyRecord
  Merchant
  StateTransition
  AuditEnvelope
  OutboxEvent
Directory: tenant/shard → home cell (epoch)
IdempotencyRecord (key, hash, status, response)
Outbox → downstream at-least-once (consumers idempotent)
AuditEnvelope (who, when, request_id, diff)
```

### 3.2 Sacred invariant

```text
Accept ⇒ durable log append before client ACK; same `(merchant_id, Idempotency-Key)` → one economic transition sequence
```

**Deal-breaker:** acknowledging success before durable commit on money-adjacent paths.

### 3.3 Core protocol

```text
Idempotent write: auth → validate → BEGIN → upsert idempotency PROCESSING → append log + update resource → outbox → COMPLETE → COMMIT → ACK. Reads route to home cell for RYW.
```

**Ordering:** durable local state **before** external side effects (rail, webhook, third-party route).

### 3.4 API surface (product)

| API | Semantics |
|---|---|
| `POST /v1/transactions` | Idempotent / typed errors / RYW where applicable |
| `GET /v1/transactions/{id}` | Idempotent / typed errors / RYW where applicable |
| `GET /v1/transactions` | Idempotent / typed errors / RYW where applicable |
| `POST /v1/transactions/{id}/cancel` | Idempotent / typed errors / RYW where applicable |
| `POST /v1/transactions/{id}/capture` | Idempotent / typed errors / RYW where applicable |

Stripe-flavored: `Idempotency-Key`, `Request-Id`, typed errors, expandable objects.

### 3.4 Transaction log as source of truth

```text
transactions(id, merchant_id, status, amount_minor, currency, version, ...)
transaction_log(
  seq, transaction_id, transition, payload_json, actor, request_id, created_at
)  -- append-only, monotonic seq per transaction_id

Materialized `status` on transactions row updated in same TX as log append.
Audit replay: rebuild state from log alone.
```

### 3.5 State transition rules

| From | Allowed transitions |
|------|---------------------|
| `requires_payment_method` | `requires_confirmation`, `cancelled` |
| `requires_confirmation` | `processing`, `cancelled` |
| `processing` | `succeeded`, `requires_action`, `failed` |
| `succeeded` | `refunded` (partial/full via separate refund API) |

**Deal-breaker:** skipping validation and writing status directly without log entry.

### 3.6 Pagination & list semantics

Cursor encodes `(created_at, id)` tuple — stable under concurrent inserts when scanning backward in time.
Document whether list is snapshot-isolated or may duplicate/miss under extreme churn.

### 3.7 Ledger integration

```text
On transition → SUCCEEDED (capture):
  outbox → ledger.PostJournal(journal_key=txn_id + ":capture:v1")
If ledger returns duplicate → treat success (already posted)
Never post ledger before local log commit
```

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
| Mutate log rows in place | Audit broken; retries unsafe |
| ACK before durable log commit | Ghost transactions in API |
| Delete transaction history | Compliance failure |
| Multi-master writers per transaction home | Split-brain state transitions |
| Skip idempotency on capture/refund | Double economic effect |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Merchant SDK / Internal Services
        |
        v
   API Gateway (AA, rate limit, auth)
        |
        v
 Transaction API Service
        |
        v
 Directory → merchant_id → home cell
        |
        v
 Home Cell
   |-- transactions + transaction_log (append)
   |-- idempotency store
   |-- outbox → webhooks / ledger worker
        |
        +--> Read replicas (list/search)
        +--> Archive / warehouse export
```

### 4.2 Sequence: create transaction

```text
Client → POST /transactions (Idempotency-Key)
Home → idempotency upsert PROCESSING
     → INSERT transaction + log[CREATED]
     → outbox transaction.created
     → idempotency COMPLETE
     → COMMIT
Client ← 201 Transaction
Retry → same response, seq unchanged
```

### 4.3 Sequence: capture + ledger

```text
Client → POST /transactions/{id}/capture
Home → validate state machine
     → log[CAPTURED] + status update (same TX)
     → outbox → LedgerWorker
LedgerWorker → PostJournal(journal_key=...)
             → mark outbox published
WebhookWorker → delivery at-least-once
```

### 4.4 Sequence: regional failover

```text
Cell A fenced epoch N
Cell B promoted N+1
Replay A outbox gap
Recon: log seq vs ledger journals for window
Resume writes when break count below threshold
```

### 4.5 Sequence: list with cursor

```text
Client → GET /transactions?starting_after=txn_abc
Edge → read replica or home (policy)
     → index scan (merchant_id, created_at, id)
     ← page + has_more + next_cursor
```

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

### 5.10 Log immutability & compensating entries

Corrections never UPDATE log rows. A mistaken capture is reversed by appending `REVERSED` with link to original seq.
Recon replays log to verify materialized status matches derived state.
Property test: ∀ txn, fold(log entries) == resource.status.

### 5.11 Optimistic concurrency on PATCH

Clients send `If-Match: version` or `version` field.
Server rejects if version stale — prevents lost updates on metadata fields (description, metadata map).
Money fields may be immutable after create — policy explicit.

### 5.12 API versioning & expand/contract

Add nullable fields first → backfill → enforce.
Old clients ignore unknown fields; new clients require new version header.
Deprecation: sunset header + metric on old version usage.

### 5.13 Hot merchant isolation

Top merchants get dedicated home cell or sub-shard.
Per-transaction_id serialization prevents cross-txn ordering issues while allowing parallel txns.

### 5.14 Read replica lag policy

Money status checks for payout gates: RYW from primary.
Dashboard lists: OK up to 30s lag with `as_of` timestamp in response.

### 5.15 Log export for warehouse

CDC stream from log table → Kafka → warehouse.
Ordering key = transaction_id; consumers idempotent on seq.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|---|---|
| Log model | Append-only transaction_log + materialized resource |
| Idempotency | Merchant-scoped key + body hash; long retention |
| Reads | RYW via home; replica for lists with lag bound |
| Async | Transactional outbox to webhooks + ledger |
| Multi-region | AA edge; SW home per merchant shard |

### 6.2 Risks

1. Log/table drift if materialized update bugs
2. Stuck PROCESSING idempotency under crash
3. Hot merchant shard contention
4. Ledger outbox lag causing recon breaks
5. API version migration mistakes

### 6.3 45-minute interview plan

| Min | Focus |
|---|---|
| 0–5 | Scope: API + log, not full payments rail |
| 5–15 | Entities, state machine, idempotency protocol |
| 15–25 | Log immutability, outbox, ledger tie-in |
| 25–35 | Multi-region, failover, read paths |
| 35–45 | Scale table, pagination, deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1

**Q: Why append-only log vs update row?**  
A: Audit and replay; disputes need history; corrections are explicit transitions.

### 7.2

**Q: How long retain idempotency keys?**  
A: Years or forever for capture/refund — not 24h.

### 7.3

**Q: Same key different body?**  
A: 409 — client bug; never silently merge.

### 7.4

**Q: Can list API miss new txns?**  
A: Possible under replica lag — document; use RYW GET for critical checks.

### 7.5

**Q: When post to ledger?**  
A: After local log commit on economic transition; journal_key ties to txn id.

### 7.6

**Q: Exactly-once webhooks?**  
A: No — at-least-once with stable event_id; merchant dedupes.

### 7.7

**Q: How handle 1000× write QPS?**  
A: Shard by merchant; partition log; async ledger via outbox.

### 7.8

**Q: PATCH vs POST for transitions?**  
A: POST for state transitions (explicit); PATCH for metadata only.

### 7.9

**Q: Float amounts?**  
A: Never — integer minor units.

### 7.10

**Q: Integration round vs this?**  
A: Integration = code against docs; this = HLD of API+log service.

### 7.11

**Q: PROCESSING stuck?**  
A: Sweeper + inquiry whether log seq committed; never new key.

### 7.12

**Q: Cross-region read?**  
A: Analytics OK stale; payout gates need home RYW.

### 7.13

**Q: Delete GDPR request?**  
A: Pseudonymize metadata; retain log hash chain for audit policy — legal review.

### 7.14

**Q: Cursor pagination vs offset?**  
A: Cursor — offset breaks under concurrent inserts.

### 7.15

**Q: Dark launch?**  
A: Shadow compare log-derived status vs legacy table before cutover.

### 7.16

**Q: What breaks first at 10×?**  
A: Idempotency store — shard + SQL unique backing.

### 7.17

**Q: Log compaction?**  
A: Never delete — archive to cold tier with legal hold.

### 7.18

**Q: Typed errors on retry?**  
A: Same outcome must return same HTTP status on idempotent replay.

---

## 8. Appendices

### 8.1 Schema sketches

```text
transactions(
  id, merchant_id, status, amount_minor, currency, version,
  metadata_json, created_at, updated_at
)
transaction_log(
  seq BIGSERIAL, transaction_id, transition, payload_json,
  actor, request_id, created_at
)
UNIQUE(transaction_id, seq)
idempotency(merchant_id, key, request_hash, status, response_json, ...)
outbox(id, topic, payload, created_at, published_at)
```

### 8.2 API request/response sketch

```text
POST /v1/transactions
Headers: Idempotency-Key, Stripe-Version: 2024-06-20
{ "amount": 2000, "currency": "usd", "capture_method": "manual" }
→ 201 { "id": "txn_1", "status": "requires_confirmation", ... }

POST /v1/transactions/txn_1/capture
→ 200 { "status": "succeeded", ... }
```

### 8.3 State machine

```text
requires_payment_method → requires_confirmation → processing → succeeded | failed | cancelled
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
function createTransaction(req):
  return home(merchant).tx:
    idem = upsertIdempotency(req.key, hash(req.body))
    if idem.complete: return idem.response
    txn = insertTransaction(req)
    appendLog(txn.id, CREATED, req)
    outbox.emit(transaction.created, txn)
    return completeIdempotency(txn)
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
| Transaction log | Append-only sequence of state transitions per transaction |
| RYW | Read-your-writes — GET after POST sees own write |
| Transition | Named state change appended to log |
| Materialized status | Cached current state derived from log |

### 8.9 Interview "say this" (60 seconds)

> We expose Stripe-style APIs with mandatory idempotency on mutations, durable commit before ACK, and typed errors. Strong-consistency domains use single-writer home cells with directory routing. Async work uses transactional outbox; external calls use stable idempotency keys and inquiry on timeout. Failover uses epoch fencing and recon before resuming money paths. We never use floats for money, never mutate audit history, and treat reconciliation breaks as first-class ops objects.

### 8.10 Related systems map

```text
API Edge → Transaction APIs + Transaction Log → Domain Store
                              │
                              ├─► Idempotency / Audit
                              ├─► Outbox → Workers → External / Ledger / Webhooks
                              └─► Metrics / APM / Rate limits
```

Related docs: payment-processing, idempotent-payment-processing, ledger-bookkeeping, webhook-delivery.

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

*End of transaction apis + transaction log system design.*
