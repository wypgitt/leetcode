# System Design: Visa-like Payment Routing Network

> **Focus areas:** Authorization routing · Issuer/acquirer · BIN lookup · Idempotency · Ledger · Settlement · Fraud hooks · PCI boundaries
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** API correctness, idempotency, ledger/regional failure awareness, explicit deal-breakers, integer money where applicable  
> **Interview theme:** Databricks — high-reliability payment routing network connecting merchants, issuers, and acquirers

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

Goal: bound **end-to-end payments**—PaymentIntent, rails, ledger, uncertain windows.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|---|---|---|
| F1 | Lifecycle? | Create confirm capture refund | State machine |
| F2 | Idempotency? | All mutating APIs | Long retention |
| F3 | Rails? | Card ACH etc | Orchestrator |
| F4 | 3DS? | requires_action | Async resume |
| F5 | Ledger? | Journal on capture | journal_key |
| F6 | Webhooks? | Outbox events | Merchant notify |
| F7 | Disputes? | Hook reserve | Out of MVP depth OK |
| F8 | Multi-currency? | Integer minor | No float |
| F9 | Recon? | Rail vs internal | Daily breaks |
| F10 | Partial capture? | Amount <= authorized | Multiple captures policy |
| F11 | Cancel? | Void uncaptured | Terminal state |
| F12 | Regional? | Home per payment | SW cell |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/payment_intents` — create with idempotency
2. `POST /v1/payment_intents/{id}/confirm` — handle 3DS continuation
3. `POST /v1/payment_intents/{id}/capture` — partial/full capture
4. `POST /v1/refunds` — idempotent refund against charge
5. Rail orchestration with uncertain outcome classification
6. Ledger journal on confirmed economic transition

**Out of MVP (explicitly defer):**

- Multi-master active-active writers on same strong-consistency shard
- Exactly-once end-to-end without client idempotency cooperation
- Replacing all Stripe production systems in one End-to-End Payment Processing design
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

1. Create PaymentIntent → requires_confirmation → confirm → processing → succeeded
2. 3DS requires_action → client completes → resume same intent id
3. Capture with Idempotency-Key → rail success → ledger journal → webhook
4. Duplicate capture key → 200 original charge (no double)
5. Refund idempotent → ledger reversing journal linked
6. Rail timeout → inquiry → classify → no blind retry new key

**Edge / failure cases**

| Case | Behavior |
|---|---|
| Duplicate capture key | 200 stored charge |
| Capture > authorized | 400 invalid amount |
| Confirm after cancel race | 409 state conflict TX |
| Rail timeout ambiguous | Mark requires_inquiry; worker polls rail |
| Partial capture sum > auth | Reject or policy split captures |
| 3DS abandon | Intent expires requires_action → failed/cancelled |
| Currency mismatch | 400 before rail call |
| Ledger post fails | Outbox retry; payment stays succeeded; recon |
| Regional failover | Fence home; replay outbox; pause captures policy |
| Webhook before ledger | Never — outbox ordering in TX |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|---|---|---|---|---|
| Peak payment write QPS | 1K | 10K | 100K | 1M |
| Peak status read QPS | 10K | 100K | 1M | 10M |
| Payments / day | 50M | 500M | 5B | 50B |
| Rail attempts / payment | 1.2 | 1.3 | 1.5 | 1.8 |
| 3DS step-up rate | 8% | 10% | 12% | 15% |
| Merchants | 100K | 1M | 10M | 100M |
| Home cells | 2 | 4 | 8 | 16 |

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

> Design payment processing ~1K QPS to 1000x idempotent lifecycle.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
50M payments/day peak ~1K/s
Peak/average ratio ~3–4× for burst planning
Split classes: sync writes, sync reads, async workers, audit/export
```

### 2.2 Storage

```text
Payment row ~2KB + attempts
Idempotency records: same order as writes; retain long for money paths
Audit/log: append-only; tier hot → cold object store
Unit-check discipline: 1e9 rows × 1 KB = 1 TB (not PB)
```

### 2.3 Bandwidth

```text
Rail payloads regional
Internal replication (WAL/outbox) similar order to write bandwidth
```

### 2.4 Memory

```text
Idempotency hot set sharded
Working set for hot keys: partition by hash; never single global Redis
```

### 2.5 Bottleneck ranking (interview)

Rail timeout, idempotency, hot merchant, ledger outbox

**Say early:** correctness and API semantics > raw QPS.

### 2.6 Domain-specific note

```text
3DS adds async continuation
```

---

## 3. High-Level Design

### 3.1 Core entities

```text
PaymentIntent
  Charge
  Refund
  RailAttempt
  IdempotencyRecord
  LedgerJournalRef
Directory: tenant/shard → home cell (epoch)
IdempotencyRecord (key, hash, status, response)
Outbox → downstream at-least-once (consumers idempotent)
AuditEnvelope (who, when, request_id, diff)
```

### 3.2 Sacred invariant

```text
One business payment transition per idempotency key; ledger journal_key ties economic effect
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
| `POST /v1/payment_intents` | Idempotent / typed errors / RYW where applicable |
| `POST /v1/payment_intents/{id}/confirm` | Idempotent / typed errors / RYW where applicable |
| `POST /v1/refunds` | Idempotent / typed errors / RYW where applicable |

Stripe-flavored: `Idempotency-Key`, `Request-Id`, typed errors, expandable objects.

### 3.11 PaymentIntent state machine

```text
requires_payment_method → requires_confirmation → processing
  → succeeded | requires_action (3DS) → processing | failed | cancelled
Refunds are separate objects linked to Charge, not backward transitions on PI.
```

### 3.12 Rail orchestration layer

```text
Orchestrator calls rail with stable idempotency_key per attempt
Timeout → inquiry API with same business key
Never mint new key for same capture intent
Classify: succeeded | failed | indeterminate
```

### 3.13 Ledger coupling

### 3.14 BIN routing table

```text
bin_ranges(prefix_start, prefix_end, issuer_id, priority, protocol)
longest_prefix_match(pan_token) → RoutingDecision
health: circuit breaker per issuer_endpoint
maintenance mode → secondary route or structured decline
```

### 3.15 Auth vs capture vs settlement

```text
Auth: hold funds / approve — sync hot path p99 < 500ms
Capture: confirm amount ≤ authorized — may be async batch
Settlement: net clearing files hourly/daily — never on auth critical path
```



```text
On capture succeeded:
  journal_key = payment_intent_id + ":capture:v" + recipe_version
  PostJournal in outbox worker — local PI commit first
```

### 3.14 Reconciliation

Daily: sum(captured) vs rail settlement file vs ledger clearing account → open breaks.

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

### 4.1 End-to-end

```text
Merchant → API Gateway → Payment API → Directory → Home Cell (PI + idempotency)
                                              ↓
                                    Rail Orchestrator → Card networks
                                              ↓
                                    Outbox → Ledger / Webhooks / Recon
```

### 4.2 Confirm + 3DS

Client confirm → rail requires 3DS → 200 requires_action + next_action
Client completes 3DS → POST confirm again → processing → succeeded

### 4.3 Capture idempotent

POST capture + Idempotency-Key → TX upsert idem → rail capture → ledger outbox → 200

### 4.4 Rail timeout

Rail call timeout → mark indeterminate → inquiry worker → same external key → resolve state

### 4.5 Failover

Fence cell → promote → replay outbox captures → recon rail window before resume

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

### 5.10 Partial capture policy

Multiple captures summing to auth amount; each idempotent; final capture closes auth.

### 5.11 3DS continuation

Store rail context on PI; resume token ties client retry to same attempt.

### 5.12 Dispute hooks

On dispute.opened outbox → reserve hold journal (if in scope).

### 5.13 Idempotency across confirm/capture

Separate keys per endpoint; body hash includes amount.

### 5.14 Rail circuit breaker

Per rail health; fail fast; route backup rail if configured.

### 5.15 Merchant level home sharding

hash(merchant_id) → cell; hot merchant isolated.

### 5.6 Stand-in processing

When issuer link down, policy may allow **stand-in** approval up to floor limit using issuer-stored limits cache — high risk; document explicitly. MVP: decline unless issuer contract mandates stand-in with strict caps.

### 5.7 Settlement pipeline

```text
Hourly/daily:
  collect CAPTURED txns → net by merchant/issuer → generate clearing files
  idempotent file ingestion on both sides
  reconciliation job matches auth ↔ capture ↔ settlement
```

### 5.8 Chargeback hook

Chargeback event links to original `txn_id`; adjust merchant settlement; optional ledger integration (see Stripe ledger doc).

### 5.9 Multi-region active-passive

Auth writes **home region** per merchant or txn_id; failover promotes secondary; fence old epoch; replay in-flight UNKNOWN txns.

### 5.10 ISO8583 vs JSON adapters

Plugin `IssuerAdapter` interface; map internal `AuthorizationRequest` to wire format; record raw message hash for disputes (not PAN).

### 5.11 Load test scenarios

| Scenario | Expect |
|----------|--------|
| Issuer 2s latency | Timeouts; circuit; no thread exhaustion |
| Duplicate auth retry | Idempotent same response |
| BIN table switch mid-day | Versioned routing; no mixed routes per txn |

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

**Q: When post ledger?**  
A: After local commit on confirmed capture/refund; journal_key ties to PI transition.

### 7.2

**Q: Rail timeout handling?**  
A: Inquiry with same idempotency key — never blind retry new key.

### 7.3

**Q: 3DS flow?**  
A: requires_action is sync API response; async completion via second confirm.

### 7.4

**Q: Partial capture?**  
A: Multiple capture calls; track captured_sum ≤ authorized.

### 7.5

**Q: Refund idempotency?**  
A: Separate key per refund request; links to charge_id.

### 7.6

**Q: Exactly-once charge?**  
A: Idempotency key + rail key + ledger unique journal.

### 7.7

**Q: Float?**  
A: Integer minor units only.

### 7.8

**Q: Active-active capture?**  
A: No — single-writer home per PI.

### 7.9

**Q: Webhook ordering?**  
A: Outbox after DB commit; at-least-once event_id stable.

### 7.10

**Q: Stuck processing?**  
A: Sweeper + rail inquiry.

### 7.11

**Q: Cancel vs refund?**  
A: Cancel voids uncaptured auth; refund reverses capture.

### 7.12

**Q: Cross-region read?**  
A: RYW from home for status; replica OK dashboard lag.

### 7.13

**Q: Recon break?**  
A: Open ticket; may pause payouts merchant-level.

### 7.14

**Q: 1000× QPS?**  
A: Shard merchants; async ledger; rail pool scaling.

### 7.15

**Q: Integration round?**  
A: Coding task — not this HLD.

### 7.16

**Q: Dispute reserve?**  
A: Ledger hold journal on dispute event.

### 7.17

**Q: Multiple rails?**  
A: Orchestrator abstraction; same PI state machine.

### 7.18

**Q: SCA regulation?**  
A: requires_action models PSD2 step-up.

### 7.19

**Q: Client retry 500?**  
A: Same Idempotency-Key mandatory.

### 7.20

**Q: Dark launch new rail?**  
A: Shadow rail call compare before cutover.

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
requires_payment_method → requires_confirmation → processing → succeeded | requires_action | failed
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
API Edge → End-to-End Payment Processing → Domain Store
                              │
                              ├─► Idempotency / Audit
                              ├─► Outbox → Workers → External / Ledger / Webhooks
                              └─► Metrics / APM / Rate limits
```

Related docs: ledger-bookkeeping, idempotent-payment-processing, webhook-delivery.

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

*End of end-to-end payment processing system design.*

### 8.19 PaymentIntent field checklist

- [ ] amount_capturable vs amount_received tracked separately  
- [ ] last_payment_error populated on failed  
- [ ] next_action for 3DS contains client_secret  
- [ ] metadata size limits enforced  

### 8.20 Rail attempt log schema

```text
rail_attempts(id, payment_intent_id, rail, external_idempotency_key,
              status, raw_response_ref, created_at)
```
*End of visa payment routing HLD prep.*
