# System Design: High-Volume Real-Time Transaction Microservice

> **Focus areas:** Idempotency · Exactly-once economic effect · Ledger/outbox · Hot-path latency · Sharding · Multi-region single-writer · Fraud hooks · Audit · Azure-friendly cells  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes, explicit deal-breakers, **single-writer money/state**, resolved uncertainty windows  
> **Interview theme:** Microsoft — **Azure / Payments / Commerce / Xbox Store / M365 billing-adjacent** real-time transaction microservice

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

Goal: design a **stateless-looking microservice** that accepts, validates, persists, and effects **high-volume real-time transactions**—purchases, top-ups, transfers, game entitlements, subscription charges—under retries, partial failures, and global traffic, with Microsoft-grade auditability and regional compliance.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Real-time transaction API + durable effect pipeline | Full bank / card network switch |
| Plane | Accept → authorize/validate → commit ledger → notify | Batch settlement warehouse alone |
| Success | Correct balances/entitlements + low latency | Pretty dashboard only |
| Microsoft lens | Azure cells, Entra auth, regional residency, clean APIs | Academic 2PC textbook only |

### 1.1 Functional Requirements

| # | Question to ask | Typical answer | Design implication |
|---|-----------------|----------------|--------------------|
| F1 | Transaction types? | Purchase, refund, transfer, top-up, entitlement grant | Polymorphic txn envelope + type handlers |
| F2 | Synchronous response? | Client needs commit/decline in request path | Hot path must finish durable commit before ACK |
| F3 | Idempotency? | Mandatory; clients retry aggressively | Idempotency key + request hash |
| F4 | Money vs points? | Both; integer minor units / points | Never float; typed amounts |
| F5 | Ledger? | Double-entry or append-only balance journal | Single-writer home per account |
| F6 | External PSP/wallet? | Optional adapter for card/wallet | Uncertainty protocol for external calls |
| F7 | Fraud? | Pre-commit risk score; async review hooks | Fail-open vs fail-closed by class |
| F8 | Notifications? | At-least-once events to Notification bus | Outbox → Event Hub/Service Bus |
| F9 | Multi-tenant? | Tenants = apps/stores/marketplaces | `tenant_id` + quota + isolation |
| F10 | AuthN/Z? | Entra ID / managed identity / signed app tokens | mTLS + scopes; no anonymous money |
| F11 | Audit? | Immutable trail for compliance | Append-only events; WORM cold store |
| F12 | SLA classes? | Interactive checkout vs background settle | Separate queues / priority |

**MVP functional scope:**

1. `POST /v1/transactions` with idempotency key; validate schema, tenant, limits.  
2. Risk gate (sync score + rules).  
3. Reserve/commit against account ledger (CAS / optimistic version).  
4. Persist transaction + ledger lines atomically (or outbox-safe).  
5. Publish `TransactionCommitted` via transactional outbox.  
6. Read APIs: get by id, list by account (cursor).  
7. Refund/reverse with linkage to original.  
8. Admin/ops: replay outbox, freeze account, investigate.

**Out of MVP:** multi-master active-active balances; crypto rails; full ISO8583 acquiring; perfect global clock ordering across regions.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Commit latency (no external PSP) | p50 < 30ms, p99 < 100ms regional |
| N2 | Commit with PSP | p50 < 800ms, p99 < 2.5s excluding 3DS |
| N3 | Durability | Quorum ACK before client success |
| N4 | Availability | 99.99% ingest in home region |
| N5 | Consistency | Strong per account; causal for reads of own writes |
| N6 | Idempotent effect | Duplicate key ⇒ same txn id + status |
| N7 | Audit retention | Years in cold; hot months |
| N8 | Regional residency | EU data stays in EU cell when required |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client → create purchase → risk OK → debit buyer / credit merchant → ACK → outbox event.  
2. Duplicate retry same key → identical response, no second debit.  
3. Refund → reverse lines linked to original; balance restored.  
4. Transfer A→B same cell → single distributed transaction or ordered two-phase within cell.  
5. Entitlement grant (Xbox content) → ledger of rights, not cash.  
6. PSP path → pending → webhook/inquire → commit/fail.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click pay | Idempotency → one effect |
| Retry with different body | 409 hash mismatch |
| Insufficient funds | Decline; no partial debit |
| Hot account contention | Shard-local lock/CAS retries; queue fairness |
| Worker crash after commit before ACK | Client retries; idempotent return committed |
| PSP timeout unknown | `PENDING_EXTERNAL`; inquire; never blind re-auth |
| Cross-region transfer | Route via home cells + async settlement bridge |
| Clock skew | Server time; Lamport/version for ordering |
| Poison message outbox | DLQ + alert; never drop money events silently |
| Fraud score timeout | Policy: soft-fail for low value; fail-closed for high |
| Partial refund exceeds captured | Reject |
| Tenant quota exceeded | 429 with retry-after |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants / apps | 50 | 500 | 5K | 50K |
| Accounts | 10M | 100M | 1B | 10B |
| Txns / day | 10M | 100M | 1B | 10B |
| Peak commit QPS | 500 | 5K | 50K | 500K |
| Peak read QPS | 2K | 20K | 200K | 2M |
| Peak outbox publish/s | 1K | 10K | 100K | 1M |
| Hot accounts (whale) | 10 | 100 | 1K | 10K |
| Regions / cells | 1–2 | 3–4 | 8+ | 20+ geo cells |
| Fraud calls / day | 10M | 100M | 1B | 10B |

**What each jump forces:**

- **10×:** Split API / ledger / outbox workers; Redis/Cosmos idempotency cache; horizontal pods.  
- **100×:** Account-key sharding; tenant cells; hot-account isolation; regional homes.  
- **1,000×:** Hierarchical ledgers; stream processing; per-tenant noisy-neighbor controls; hierarchical rate limits; specialized in-mem ledgers for hottest shards.

### 1.5 Constraints & Assumptions

- Amounts in **integer minor units**; currency ISO codes.  
- “Exactly-once” means **no duplicate economic effect**, not one network packet.  
- Prefer **Azure primitives** in interview framing: AKS, Cosmos DB / Azure SQL, Event Hubs, Service Bus, Key Vault, Entra, Front Door—but design is portable.  
- Interactive path must not depend on cold analytics store.

**Scope statement:**

> Design a high-volume real-time transaction microservice that accepts idempotent transaction requests, enforces risk and limits, commits durable ledger effects with single-writer account homes, publishes reliable downstream events, and scales from ~500 to ~500K commit QPS through 10× / 100× / 1,000× with explicit deal-breakers around money correctness and multi-region writes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
Baseline 10M txn/day ÷ 86400 ≈ 116/s average
Peak ~4–5× ⇒ ~500 commit/s (matches table)

Each commit may produce:
  1 idempotency record
  1 transaction row
  2–6 ledger lines
  1 outbox event (+ fan-out)
→ storage writes ≫ HTTP QPS
```

At **1,000×**: 500K commit/s → ledger & idempotency stores dominate; JSON API is thin.

### 2.2 Storage

```text
Txn ~800 B; ledger line ~200 B; event ~500 B
Per txn lifecycle ~3–5 KB

10M/day × 4 KB ≈ 40 GB/day hot ingest
100×: ~4 TB/day
1000×: ~40 TB/day → tiered storage mandatory
```

### 2.3 Latency budget (in-cell commit)

```text
AuthZ + parse:        5 ms
Idempotency lookup:   5–10 ms
Risk (cached rules):  5–15 ms
Ledger CAS + commit:  10–40 ms
Outbox insert:        included in txn
Serialize response:   2 ms
----------------------------
p99 target:           < 100 ms regional
```

### 2.4 Bandwidth

```text
Request+response ~2–5 KB
500K/s × 5 KB ≈ 2.5 GB/s L7 → Front Door / regional ingress + connection pooling
```

### 2.5 Memory

```text
Hot idempotency window 24–72h
500K/s × 86400 ≈ 43B keys/day at 1000× → impossible in one Redis
⇒ sharded KV by key hash; TTL; bloom filters optional
```

### 2.6 Bottleneck ranking

(1) Hot account CAS contention (2) external PSP uncertainty (3) cross-cell transfers (4) outbox lag (5) raw HTTP QPS.

### 2.7 Cost levers

- Keep hot path to one region/cell.  
- Batch outbox publish.  
- Cache risk features; don’t call heavy ML on every micro-txn.  
- Cold tier audit blobs; don’t keep forever on OLTP SSD.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Accept API | Auth, validate, idempotency | Strong on key |
| Risk | Score/rules | Best-effort / cached; policy-bound |
| Ledger | Balances + journal | Strong, single-writer per account |
| Outbox / Events | Downstream notify | At-least-once, ordered per account |
| Read models | Lists, dashboards | Eventually consistent OK |
| Ops / Freeze | Compliance actions | Strong admin path |

**Deal-breaker:** updating a cached `balance` in Redis as system of record.

### 3.2 Components

1. **API Gateway / Front Door** — TLS, WAF, regional routing.  
2. **Transaction API** — stateless pods; Entra auth.  
3. **Idempotency Store** — key → result; request hash.  
4. **Risk Service** — rules + optional ML features.  
5. **Ledger Service** — account homes, CAS versions.  
6. **Transaction Store** — durable txn records.  
7. **Outbox Relayer** — polls/CDC → Event Hubs.  
8. **PSP Adapter** (optional) — external money.  
9. **Inquiry / Reconciler** — unresolved PENDING.  
10. **Admin / Freeze API** — break-glass.  
11. **Config / Limits** — tenant quotas, velocity.  
12. **Observability** — traces, RED metrics, audit query.

### 3.3 Transaction state machine

```text
ACCEPTED → RISK_CHECK → (DECLINED_RISK)
                     → RESERVING → COMMITTED → (REFUNDED / PARTIAL_REFUND)
                     → PENDING_EXTERNAL → COMMITTED | FAILED_EXTERNAL
Any non-terminal → FAILED (validation / insufficient funds)
```

### 3.4 Idempotency

```text
Key = (tenant_id, idempotency_key)
Store: hash(body), txn_id, status, response_snapshot, expires_at
First writer wins; conflicts on hash → 409
In-flight: wait/poll or return 409 Conflict-In-Progress with retry guidance
```

### 3.5 Ledger model

**Append-only journal + materialized balance** under single-writer:

```text
Account(account_id, currency, balance, version, status)
LedgerEntry(entry_id, account_id, txn_id, amount, side, ts, prev_version)
Unique(txn_id, account_id, entry_role) to prevent double post
```

Debit+credit must balance within a transaction (or explicit fee accounts).

### 3.6 Trade-offs

| Topic | Choice | Why | Trade-off |
|-------|--------|-----|-----------|
| Sync commit | Yes for in-cell | Client UX + correctness | Harder scale-out |
| Outbox vs dual-write | Outbox | No lost events | Slight lag |
| Cosmos vs SQL | Either with clear home | Azure familiarity | Hot partition tuning |
| Saga cross-account | Ordered local commits + bridge | Avoid 2PC world | Complexity |
| Cache balance | Read-through only | Speed | Stale reads OK for some UIs |
| Fraud sync | Soft timeout policy | Latency | Risk accept |

### 3.7 API sketch

```text
POST /v1/transactions
  Idempotency-Key: ...
  {type, tenant_id, from, to, amount, currency, metadata}

GET /v1/transactions/{id}
GET /v1/accounts/{id}/transactions?cursor=
POST /v1/transactions/{id}/refunds
POST /v1/accounts/{id}/freeze
```

### 3.8 Multi-region

- **Active-active API** at edge.  
- **Single-writer home cell** per `account_id` (and often per tenant).  
- Forward write to home; sticky routing via Front Door / app logic.  
- **Deal-breaker:** multi-master balance without consensus.

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Clients / Services]
        |
   Azure Front Door / APIM
        |
   Transaction API (AKS)
        |-- Idempotency Store (Cosmos/Redis)
        |-- Risk Service
        |-- Ledger Service ---- Account Shard DB (Azure SQL / Cosmos)
        |-- Txn Store
        |-- Outbox ---------- Relayer ---- Event Hubs ---- Consumers
        |-- PSP Adapter <--> External PSP
        |-- Key Vault (secrets)
        |-- Entra ID (authn/z)
```

### 4.2 Sequence: in-cell purchase

```text
Client -> API: POST txn + idem key
API -> Idem: begin/reserve key
API -> Risk: score
API -> Ledger: BeginTxn; Debit buyer; Credit merchant; version++
API -> TxnStore+Outbox: commit
API -> Idem: finalize response
API -> Client: 201 COMMITTED
Relayer -> Event Hubs: TransactionCommitted
```

### 4.3 Sequence: uncertainty (PSP)

```text
API -> Ledger: soft reserve (hold)
API -> PSP: authorize
   timeout --> mark PENDING_EXTERNAL; return 202
Inquiry job -> PSP: status
   success --> commit hold; outbox
   fail --> release hold; FAILED_EXTERNAL
```

### 4.4 Sequence: duplicate retry

```text
Client retry -> Idem hit -> return stored response (same txn_id)
No second ledger post
```

### 4.5 Cell layout

```text
Cell = {API, Ledger shards, Idem, Outbox, Risk cache}
Account home_cell = hash(account_id) or directory service
Cross-cell: Transfer Bridge with durable intents
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

1. No economic effect without durable ledger journal line.  
2. Idempotency key maps to at most one effect.  
3. Balances never go negative unless overdraft product explicitly allows.  
4. Refunds cannot exceed captured/committed net.  
5. Outbox event exists iff commit succeeded (same txn).  
6. PENDING_EXTERNAL never silently forgotten—SLA’d inquiry.  
7. Frozen accounts reject new debits.  
8. Audit log immutable; corrections are reversing entries.  
9. Tenant isolation: no cross-tenant reads.  
10. Secrets only via Key Vault / MI—never in env plaintext long-lived.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular service; one SQL; Redis idem; sync commit |
| 10× | Outbox workers; read replicas; horizontal API; cache risk |
| 100× | Shard ledger by account; tenant cells; hot-key isolation |
| 1000× | In-mem ledger for hot shards; hierarchical quotas; stream recon |

### 5.3 Maintainability

- Transaction type handlers as plugins/strategy.  
- Schema versioning on envelope.  
- Contract tests for idempotency matrix.  
- Chaos: kill relayer, kill shard primary, duplicate webhooks.  
- Feature flags for risk policies; canary tenants.

### 5.4 Progressive scale deep dive

**1× — Single region product**  
Monolith-friendly module boundaries still drawn. One Azure SQL with careful indexes on `(tenant, idem_key)` and `(account, version)`. p99 easy if no hot whales.

**10× — Platformize**  
Split Ledger service. Introduce outbox relayer HPA. Add APIM policies for quotas. Metrics by tenant and txn type. Fraud feature store cached.

**100× — Cells & shards**  
Directory: `account_id → shard`. Resharding with dual-write or move protocol. Whale accounts get dedicated shards. Cross-shard transfers use intent records:

```text
Intent CREATED → debit source committed → credit dest committed → Intent DONE
Failure: compensating release; never both silent
```

**1000× — Extreme**  
- Hierarchical ledgers (wallet → sub-wallets).  
- Event Hubs partitioned by account.  
- Speculative risk; async enrichment.  
- Regional compliance cells (EU / US / CN-class isolation).  
- Per-tenant noisy neighbor automatic throttling.  
- Co-located compute+data in availability zones; failover runbooks.

### 5.5 Hot account protocol

Symptoms: CAS abort storms, p99 spikes. Mitigations:

1. Dedicated partition / compute for whale.  
2. Request coalescing for identical top-ups (careful with semantics).  
3. Token bucket per account on API.  
4. Move from row-lock SQL to specialized ledger store.  
5. Separate “balance materialization” async for non-critical reads.

### 5.6 Exactly-once illusion

```text
Producer at-least-once + Idempotency store + Unique ledger constraints
= effectively-once economic effect
```

Never promise “the network delivered once.”

### 5.7 Outbox patterns

| Pattern | Pros | Cons |
|---------|------|------|
| Table outbox same txn | Strong link | Relayer lag |
| CDC (Debezium-like) | Less app code | Ordering/ops complexity |
| Dual write API+bus | Simple | **Deal-breaker** lost events |

### 5.8 Fraud deep dive

- Sync: velocity, device, amount, denylist.  
- Async: graph features, manual review.  
- Decisioning must be **explainable** for support.  
- Timeout policy matrix by amount tier.  
- Never block refunds forever on fraud ML downtime without policy.

### 5.9 Security & compliance

- Entra / OAuth2 client credentials for services.  
- Field-level encryption for sensitive metadata.  
- PII minimization in logs (tokenized account refs).  
- Regional residency: route home by directory.  
- PCI: if card data touches you, minimize—prefer PSP tokens.  
- Key rotation via Key Vault.

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Redis balance as SoR | Lost money on restart/split brain |
| Dual-write DB + bus | Missing notifications → broken fulfillment |
| Multi-master balances | Double spend |
| Retry PSP on unknown | Double charge |
| Float money | Rounding exploits |
| Shared DB for all tenants without controls | Noisy neighbor + blast radius |
| Sync cross-region chatty 2PC | Outages cascade |
| Skip idempotency “for speed” | Duplicate charges SEVs |

---

## 6. Wrap-Up

### 6.1 What we designed

A real-time transaction microservice with idempotent accept, risk gate, single-writer ledger commit, transactional outbox, optional PSP uncertainty protocol, and progressive cell/shard scale—framed for Microsoft Azure operations and compliance.

### 6.2 Decisions to defend

1. Single-writer account home  
2. Idempotency key + body hash  
3. Journal + version CAS  
4. Outbox over dual-write  
5. PENDING_EXTERNAL inquiry  
6. Split planes (API / risk / ledger / events)  
7. Hot-account isolation path  
8. Integer minor units  

### 6.3 Risks

- Whale contention  
- Cross-cell transfer complexity  
- Fraud false positives  
- Outbox backlog → downstream SLA break  
- Regional failover of home cell  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope txn types, sync ACK, money invariants |
| 5–12 | API + idempotency + state machine |
| 12–22 | Ledger model + commit path |
| 22–32 | Outbox, PSP uncertainty, fraud |
| 32–40 | 10×/100×/1000× sharding & cells |
| 40–45 | Deal-breakers, SEVs, ownership |

### 6.5 Closer

> **Real-time transaction microservice:** idempotent ingress, strong single-writer ledger, outbox events, explicit uncertainty for external money, Azure cell isolation, progressive scale without sacrificing economic correctness.

---

## 7. Deeper / Related Interview Questions

### 7.1 Idempotency

**Q: Where is the idempotency record stored?**  
A: Durable store co-located with home cell; Redis as cache in front OK if DB authoritative.

**Q: What if two identical requests race?**  
A: Conditional insert / transaction; loser reads winner’s result.

**Q: TTL on keys?**  
A: 24–72h typical; some industries longer; document client contract.

### 7.2 Ledger

**Q: Why double-entry?**  
A: Auditable conservation of value; fees explicit; reconcilable.

**Q: Snapshotting balances?**  
A: Periodic checkpoints + replay for rebuild; don’t rewrite history.

**Q: Multi-currency?**  
A: Separate accounts per currency or explicit FX txn type with rates locked at commit.

### 7.3 Consistency

**Q: Read-your-writes?**  
A: Route reads to home or session stickiness; read models may lag—document.

**Q: Serializable vs snapshot?**  
A: Per-account serialization sufficient for many wallets; justify.

### 7.4 Multi-region

**Q: Failover home cell?**  
A: Promote secondary with fencing token; block stale primary; runbook tested.

**Q: EU residency?**  
A: Directory forces EU home; no silent re-home to US.

### 7.5 Messaging

**Q: Ordering?**  
A: Partition by account_id; consumers must still be idempotent.

**Q: Poison messages?**  
A: Retry budget → DLQ → page owner; never infinite loop.

### 7.6 LLD prompts Microsoft loves

**Q: Code the idempotency middleware.**  
A: Be ready to sketch interfaces: `IdempotencyStore.begin/commit`, hash compare, lock TTL.

**Q: Sketch CAS ledger method.**  
A: `UPDATE balance SET bal=$new, ver=ver+1 WHERE id=? AND ver=?`.

### 7.7 Fraud & abuse

**Q: Fail-open or closed?**  
A: Matrix by product: game coins micro-txn may soft-open; wire-class fail-closed.

### 7.8 Observability

**Q: Golden signals?**  
A: commit QPS, p99, CAS abort rate, outbox lag, pending_external age, decline reasons, tenant fairness.

### 7.9 Interview traps

| Trap | Better answer |
|------|---------------|
| “Kafka makes it exactly once” | Effectively-once via keys + constraints |
| “We’ll use 2PC everywhere” | Expensive; prefer single home + intents |
| “Global Redis lock” | Latency + SPOF; prefer shard-local |
| “Eventual balance OK for checkout” | Usually deal-breaker for spend |

### 7.10 Related systems

- Notification system (downstream)  
- Search/index of txns for support  
- Fraud platform  
- Ledger warehouse / finance recon  
- Entitlement/license service  

### 7.11 Refund races

**Q: Two partial refunds concurrent?**  
A: Serialize on original txn / account; check remaining refundable under row lock.

### 7.12 Entitlements vs money

**Q: Same service?**  
A: Same envelope patterns; different ledger chart of accounts; don’t mix SKU inventory into cash balance blindly.

### 7.13 Azure-specific talking points

- Cosmos DB partition key = `account_id` or `tenant+account`.  
- Zone-redundant HA.  
- Private Link to data stores.  
- Managed identity to Key Vault / Event Hubs.  
- Chaos via Azure Chaos Studio narrative.

### 7.14 Performance debugging vignette

**Symptom:** p99 800ms, CAS aborts up.  
**Investigate:** top accounts by abort; shard CPU; lock waits; risk latency; GC.  
**Mitigate:** isolate whale; raise pool; shed noncritical reads; cache risk.

### 7.15 Cancel / resume

If interviewer pivots to “make it LLD,” drop to: models for Transaction, LedgerEntry, IdemRecord; methods commit/refund; concurrency tests.

---

## 8. Appendices

### 8.1 Schema sketches

```text
IdempotencyRecord(
  tenant_id, idem_key, request_hash, txn_id,
  status, response_json, created_at, expires_at
) PK (tenant_id, idem_key)

Transaction(
  txn_id, tenant_id, type, status, amount, currency,
  from_account, to_account, risk_score, external_ref,
  created_at, updated_at, metadata
)

LedgerEntry(
  entry_id, txn_id, account_id, amount, side, -- DEBIT|CREDIT
  balance_after, version_after, created_at
)

Outbox(
  id, aggregate_id, event_type, payload, created_at, published_at
)

Account(
  account_id, tenant_id, currency, balance, version,
  status, home_cell, updated_at
)
```

### 8.2 API checklist

- [ ] Idempotency-Key required on mutating APIs  
- [ ] 201 vs 200 replay semantics documented  
- [ ] 409 body mismatch  
- [ ] 402/400 insufficient funds mapping  
- [ ] 429 tenant/account limits  
- [ ] 202 PENDING_EXTERNAL  
- [ ] Cursor pagination on lists  
- [ ] Correlation / trace ids  

### 8.3 State transition checklist

| From | To | Guard |
|------|----|-------|
| NEW | COMMITTED | Risk OK + funds + CAS |
| NEW | DECLINED_RISK | Rules |
| NEW | FAILED | Validation |
| NEW | PENDING_EXTERNAL | PSP invoked |
| PENDING_EXTERNAL | COMMITTED | Inquiry success |
| PENDING_EXTERNAL | FAILED_EXTERNAL | Inquiry fail |
| COMMITTED | PARTIAL_REFUND | Refund < remaining |
| COMMITTED | REFUNDED | Full |

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Home cell | Region/shard owning writes for an account |
| Outbox | Durable events co-committed with state |
| CAS | Compare-and-set version update |
| Effectively-once | No duplicate economic effect |
| Whale | Extremely hot account |
| Hold | Temporary reservation before capture |
| Deal-breaker | Non-negotiable bad design |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Idempotency, ledger journal, sync commit |
| 10× | Outbox workers, quotas, risk cache |
| 100× | Shards, cells, hot isolation, transfer intents |
| 1000× | Hierarchical ledgers, residency cells, stream recon |

### 8.6 Latency recipes

| Path | Recipe |
|------|--------|
| In-cell micro-txn | Co-locate API+DB AZ; prepared statements; pool |
| Read status | Point get by txn_id; cache committed |
| List history | Keyset pagination; avoid OFFSET |
| Admin search | Secondary index store async |

### 8.7 Uncertainty pseudocode

```text
function authorizeWithPsp(txn):
  writeHold(txn)
  try:
    resp = psp.auth(txn, timeout=T)
  catch Timeout:
    markPENDING(txn)
    return 202
  if resp.ok: commitHold(txn); return 201
  else: releaseHold(txn); return declined
```

### 8.8 Relayer pseudocode

```text
loop:
  batch = outbox.fetchUnpublished(limit=500)
  for e in batch:
    bus.publish(e.partitionKey, e.payload)
    outbox.markPublished(e.id) // idempotent publish key
```

### 8.9 Idempotency matrix

| Client behavior | Server |
|-----------------|--------|
| Same key, same body | Same result |
| Same key, different body | 409 |
| Different key, same body | Second txn (client bug) |
| Network lost after commit | Retry → replay |

### 8.10 Chaos drills

1. Kill API pod mid-commit.  
2. Kill DB primary.  
3. Pause relayer 30 minutes.  
4. Duplicate PSP webhooks.  
5. Split-brain fake: two primaries (should fence).  
6. Clock jump ±5 minutes.  
7. Hot account 10× traffic.

### 8.11 SEV definitions (examples)

| SEV | Example |
|-----|---------|
| SEV0 | Double spend / money creation bug |
| SEV1 | Commit path down in major region |
| SEV2 | Outbox lag > SLA; fulfillment delayed |
| SEV3 | Single tenant unfairness |

### 8.12 Interview “say this” (60 seconds)

> We treat transactions as durable state-machine commits against a single-writer ledger home, with idempotency for retries, an outbox for downstream, and an explicit PENDING protocol for external PSPs. Scale is account sharding and cells—not multi-master balances. Correctness beats clever cross-region writes.

### 8.13 Related systems map

```text
Txn Microservice → Notification · Fulfillment · Entitlements
                 → Fraud · Finance Recon · Support Search
                 → Limits/Config · Identity (Entra)
```

### 8.14 Cost worksheet

| Item | Driver |
|------|--------|
| OLTP SSD | txn + ledger write amp |
| Event Hubs | publish fan-out |
| Risk ML | feature compute |
| Cross-region | egress—avoid on hot path |
| Audit cold | blob GRS |

### 8.15 Kill switches

- Disable tenant  
- Disable txn type  
- Fail-closed risk  
- Shed reads  
- Pause nonessential relayer consumers (not outbox write)  
- Freeze account  

### 8.16 Oncall first five minutes

1. Is commit success rate down globally or one cell?  
2. CAS abort / DB CPU?  
3. Dependency: risk, PSP, identity?  
4. Outbox lag?  
5. Recent deploy / flag flip?  
6. Whale tenant?  

### 8.17 Microsoft leadership / culture hooks

- **Customer obsession via trust:** money correctness.  
- **One engineering system:** clean API contracts.  
- **Operational excellence:** runbooks + chaos.  
- **Inclusive design:** multi-region residency.

### 8.18 LLD class sketch

```text
class TransactionService:
  def create(self, req, idem_key): ...
class Ledger:
  def apply(self, entries, expected_versions): ...
class IdempotencyStore:
  def begin(self, key, body_hash): ...
  def complete(self, key, response): ...
class Outbox:
  def enqueue(self, event): ...
```

### 8.19 Transfer intent states

```text
CREATED → SOURCE_DEBITED → DEST_CREDITED → COMPLETED
CREATED → CANCELLED
SOURCE_DEBITED → COMPENSATED (on dest failure)
```

### 8.20 Metrics dictionary

| Metric | Why |
|--------|-----|
| `txn_commit_p99_ms` | UX + SLO |
| `ledger_cas_abort_ratio` | Hot key health |
| `outbox_lag_seconds` | Downstream risk |
| `pending_external_age_p99` | Money stuck |
| `idem_replay_ratio` | Client retry health |
| `decline_rate_by_reason` | Product + fraud |

### 8.21 Failure injection catalog

- Inject 500s from risk  
- Inject PSP latency  
- Drop 10% outbox publishes (relayer must retry)  
- Corrupt request hash collision attempt  
- Full disk on shard  

### 8.22 One-breath closer

> Idempotent sync commits to a single-writer ledger, outbox for side effects, PENDING for external uncertainty, cells for scale and residency—never multi-master money.

### 8.23 Extra Q&A bullets

**Q: Why not saga orchestration UI for every purchase?**  
A: Overkill in-cell; use for cross-cell/cross-system only.

**Q: Why not store procedure god-object?**  
A: Hard to evolve; keep ledger logic testable in service with tight txn boundaries.

**Q: Can Event Hubs be SoR?**  
A: No for balances; yes for analytics/notify.

**Q: How do you test?**  
A: Property tests on ledger conservation; concurrency stress; contract tests for idempotency.

**Q: GDPR delete?**  
A: Careful—financial retention laws may override; minimize PII in txn metadata; separate profile store.

### 8.24 Worked capacity narrative

At 50K commit/s (100× peak), with 4 KB write amp, you need ~200 MB/s durable write bandwidth before replication factor. With 3× replication ≈ 600 MB/s cluster-wide. That alone forces sharding and kills “one big Azure SQL.” Interviewers listen for this arithmetic.

### 8.25 Topic closer checklist

- [ ] Stated invariants  
- [ ] Drew planes  
- [ ] Walked commit sequence  
- [ ] Named deal-breakers  
- [ ] Explained 10×/100×/1000×  
- [ ] Mentioned Azure ops primitives  
- [ ] Offered LLD dive if asked  

### 8.26 Supplemental edge cases

| Edge | Handling |
|------|----------|
| Zero-amount txn | Reject or allow authorization probe—product decision |
| Negative amount | Reject at schema |
| Future-dated txn | Separate scheduled pipeline; not hot path |
| Bulk batch API | Chunk + per-item idempotency |
| Clock from client | Ignore for ledger time |
| Duplicate refund keys | Idempotent refund records |

### 8.27 Comparison table: patterns

| Pattern | Use |
|---------|-----|
| Sync ledger | Interactive spend |
| Async settle | Batch fees, FX |
| Hold/capture | Card-like flows |
| Entitlement grant | Digital goods |
| Transfer intent | Cross-shard |

### 8.28 Recap progressive scale

| Jump | Slogan |
|------|--------|
| 10× | Workers + quotas |
| 100× | Shards + cells |
| 1000× | Hierarchies + residency + specialized ledgers |

### 8.29 Final reminder for Microsoft loops

Be ready to **switch to code**: implement CAS loop, idempotency map, and a pure function `apply_entries(balance, entries) -> Result`. HLD without willingness to LLD is a common Microsoft failure mode.

---

*End of document — High-Volume Real-Time Transaction Microservice*
