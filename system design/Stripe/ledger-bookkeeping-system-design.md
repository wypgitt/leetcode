# System Design: Ledger / Bookkeeping Service

> **Focus areas:** Double-entry journals · Append-only postings · Account chart · Balances via snapshots · Idempotent posting · Multi-currency · Audit · Regional single-writer · Rollout/ops  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (minor units), balanced journals, explicit deal-breakers, **single-writer money home**, Stripe-style API correctness  
> **Interview type:** **HLD / architecture** — not the Stripe integration-round coding task (JSON transform + call documented APIs)

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

Goal: **bound the money truth layer**—what a journal is, who may post, how balances are derived, and how we stay auditable under retries, regional failure, and rollout.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who posts? | Internal services (payments, payouts, fees, disputes, lending) | Authenticated service principals; no merchant direct write |
| F2 | Double-entry? | Yes — every journal balances | Constraint: sum(postings)=0 per currency (or FX pair rules) |
| F3 | Mutable entries? | Never mutate; corrections = reversing journals | Append-only; immutability is the product |
| F4 | Accounts? | Chart of accounts per merchant / platform / clearing | `account` entity with type + currency |
| F5 | Idempotency? | Mandatory — same `journal_key` posts once | Unique `(tenant, journal_key)` |
| F6 | Balance API? | Current balance + as-of time + available vs pending | Snapshot + sum(delta) or materialize carefully |
| F7 | Multi-currency? | Yes; no silent FX | Per-currency accounts; explicit FX journals |
| F8 | Pending holds? | Auth holds / reserves separate from available | Pending accounts or hold postings |
| F9 | Query patterns? | By account, by journal, by external_ref (payment_id) | Indexes + time partitions |
| F10 | Export / audit? | Full history forever (compliance) | Hot OLTP + cold archive; legal hold |
| F11 | Multi-tenant? | Merchants + platform books | `merchant_id` / `book_id` isolation |
| F12 | Consistency? | Strong for post + balance for that account | Single-writer home cell per book/account shard |

**MVP functional scope (lock with interviewer):**

1. Create **accounts** in a chart (asset, liability, revenue, expense, contra).  
2. Post **journals** with N postings; reject unbalanced.  
3. **Idempotent** post by `journal_key`.  
4. Read **balance** (available / pending) per account.  
5. List journals/postings by account and by `external_ref`.  
6. Reverse/correct via **new** journals only.  
7. Multi-currency with integer **minor units**.  
8. Audit trail: who/when/why metadata on journals.

**Out of MVP (explicitly defer):**

- Full general ledger for public company close / GAAP packages  
- Real-time FX market maker  
- Crypto rails as native ledger currency  
- Multi-master active-active balance writers  
- Merchant self-serve arbitrary journal posting (fraud/abuse)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Post latency | Sync on payment critical path | p50 < 20ms, p99 < 100ms in-region |
| N2 | Durability | Accepted journal never lost | Quorum commit before ACK |
| N3 | Exactly-once effect | Same journal_key → one economic effect | Unique constraint + response cache |
| N4 | Availability | Money path critical | 99.99% home cell; degrade reads first |
| N5 | Consistency | Linearizable post per account shard | Single-writer / serializable TX |
| N6 | Multi-region | Global API edge | AA edge; **SW ledger home** |
| N7 | Auditability | Explain every cent | Append-only + immutable blob of request |
| N8 | Scale | Through 1000× posting rate | See scale table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Payment capture → journal (Dr clearing / Cr merchant payable + fee revenue) → balances update.  
2. Partial refund → reversing-style journal against remaining payable.  
3. Auth hold → pending postings; capture releases hold + final posts.  
4. Duplicate post with same `journal_key` → return original journal.  
5. Balance read during post → RYW from home; never see partial journal.  
6. Correction for fee miscalc → new reversing journal + correct journal; audit links both.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Unbalanced journal | Reject 400; no partial write |
| Duplicate key same body | 200 + original journal |
| Duplicate key different body | 409 conflict |
| Post timeout after commit | Client retries → idempotent return |
| Crash mid multi-account post | TX rollback; nothing applied |
| Negative available (overdraft policy) | Reject or allow with overdraft flag—policy explicit |
| Currency mix without FX journal | Reject |
| Clock skew on as-of query | Server time only; document snapshot semantics |
| Hot merchant account | Serialize writers; partition by sub-account/period |
| Regional failover | Fence old writer epoch; replay outbox; recon |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Merchants / books | 10K | 100K | 1M | 10M |
| Accounts | 100K | 1M | 10M | 100M |
| Journals / day | 5M | 50M | 500M | 5B |
| Peak **post** QPS | ~200 | ~2K | ~20K | ~200K |
| Avg postings / journal | 3 | 3 | 4 | 4 |
| Peak **posting lines**/s | ~600 | ~6K | ~80K | ~800K |
| Peak **balance reads**/s | ~2K | ~20K | ~200K | ~2M |
| Open pending holds | 1M | 10M | 100M | 1B |
| Hot accounts (top) | 10 | 50 | 200 | 1K |
| Audit export jobs / day | 10 | 50 | 200 | 1K |

**Split write classes:** journal posts ≠ balance reads ≠ snapshot compaction ≠ archive export. Do not lump into one “QPS.”

**What each jump forces:**

- **10×:** Idempotency table hardened; outbox for async consumers; snapshotter.  
- **100×:** Shard by `book_id`/`merchant_id`; cell architecture; hot-account isolation.  
- **1,000×:** Hierarchical books; period partitions; stream materialization; regional homes.

### 1.5 Etc. (Constraints & Assumptions)

- Money is **integer minor units** — never float.  
- Ledger is **internal SoT for platform accounting**; card networks/banks are rail SoT for settlement cash.  
- “Exactly-once” means one **economic journal effect**, not one HTTP request in history.  
- This round is **system design**, not writing a Stripe Elements integration or parsing webhook JSON in a coding pad.

**Scope statement:**

> Design a multi-tenant double-entry ledger/bookkeeping service: idempotent journal posting, append-only immutable postings, account balances (available/pending), multi-currency with explicit FX, strong consistency per account home, audit forever—from ~200 post QPS through 10× / 100× / 1,000× with single-writer cells and snapshot-based balance reads.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
Baseline 5M journals/day ÷ 86400 ≈ 58/s average
Peak ~3–4× ⇒ ~200 post/s (matches table)

Each journal:
  1 journal row + ~3 posting rows + idempotency upsert
  optional outbox event for webhook/read models

Balance reads ≫ posts (dashboards, authz checks, payout gates)
At 1000×: 200K post/s → 800K posting lines/s → append path is the gut
```

### 2.2 Storage

```text
Journal ~300 B metadata + postings 3×120 B ≈ 660 B
+ idempotency record ~400 B
≈ 1 KB per journal amortized hot row set

5M/day × 1 KB ≈ 5 GB/day
1000×: 5B/day × 1 KB = 5 PB/day? 
  5e9 × 1e3 = 5e12 B = **5 TB/day** (not PB)

Annual at 100× (500M/day): 500e6 × 365 × 1 KB ≈ 182 TB/year raw rows
Indexes + replicas ≈ 3–5× → plan **~1 PB/year** class at 100× with cold tiering
```

Retain forever in cold; hot OLTP months–years by regulation tier.

### 2.3 Bandwidth

```text
Post request ~2–5 KB; response ~2 KB
200K/s × 5 KB ≈ 1 GB/s API payload at 1000× → regional cells, not one VIP
Internal replication of WAL similar order
```

### 2.4 Memory

```text
Hot balance cache: top accounts + recent snapshots
200K accounts hot × 256 B ≈ 50 MB trivial
Idempotency hot set: 200K/s × 86400 ≈ 17B keys/day → **sharded KV + SQL unique**, not one Redis
```

### 2.5 Bottleneck ranking (interview)

1. Hot account serialization  
2. Idempotency uniqueness under retry storms  
3. Cross-account atomic journals  
4. Snapshot compaction lag  
5. Multi-region fencing on failover  

Correctness > raw QPS. Say it early.

### 2.6 Hold / pending economics

```text
Open holds ≈ hold_create_rate × hold_lifetime
If 50 hold-journals/s × 6h = 50 × 21600 = 1.08M open at small scale
At 1000× proportionally huge → TTL sweepers + pending account capacity
```

---

## 3. High-Level Design

### 3.1 Core entities

```text
Book (merchant_id or platform_book)
  └── Account (type, currency, status)
        └── Postings (append-only) via Journals
Journal (journal_key, external_ref, type, metadata)
  └── Postings[] (account_id, amount_minor, direction or signed amount)
BalanceSnapshot (account_id, version, available, pending, as_of)
IdempotencyRecord (book_id, journal_key, request_hash, journal_id, response)
```

### 3.2 Double-entry invariant (sacred)

Every accepted journal:

```text
∀ currency C in journal:
  sum(postings where currency=C) == 0
```

FX journal exception: paired legs across currencies with explicit rate + fees as separate balanced parts:

```text
Dr USD Clearing 10000
Cr USD Customer 10000
Dr EUR Customer 9200
Cr EUR Clearing 9200
(+ fee journals in one currency)
```

**Deal-breaker:** updating a single `balance` integer without a journal.

### 3.3 Idempotent post protocol

```text
1. Validate authz + schema + balance policy
2. BEGIN TX
3. INSERT idempotency(book_id, journal_key, hash, status=PROCESSING)
   ON CONFLICT:
     same hash + COMPLETE → return stored journal
     same hash + PROCESSING → wait/409-retry
     different hash → 409
4. Insert journal + postings
5. Optionally update snapshot / enqueue outbox
6. Mark idempotency COMPLETE with response snapshot
7. COMMIT
8. ACK client
```

**Ordering of side effects:** durable local journal **before** emitting external webhook/read-model events (outbox).

### 3.4 Balance model

| Approach | Pros | Cons |
|----------|------|------|
| Sum all postings | Simple truth | Slow at scale |
| Snapshot + sum(delta) | Fast reads | Compaction ops |
| Materialized row updated in same TX | Fast | Hot-row contention; still need journal SoT |

**Recommended interview answer:** append-only postings are SoT; **snapshot** every K posts or T seconds; balance = snapshot + sum(after); writers serialized per account shard.

### 3.5 Available vs pending

```text
available_balance = sum(postings on available accounts)
pending_balance   = sum(postings on pending/hold accounts)
payout_gate: available - reserves - minimum_balance
```

Auth hold example (sketch):

```text
Auth:   Dr Pending Holds / Cr Auth Mirror (or liability pending)
Capture: reverse hold; Dr Clearing / Cr Merchant Payable + Fees
```

### 3.6 API surface (product)

| API | Semantics |
|-----|-----------|
| `POST /v1/journals` | Idempotent create |
| `GET /v1/journals/{id}` | Fetch |
| `GET /v1/accounts/{id}/balance` | Available/pending |
| `GET /v1/accounts/{id}/postings` | Paginated history |
| `POST /v1/journals/{id}/reverse` | Convenience reversing journal |
| `POST /v1/accounts` | Provision chart accounts |

Stripe-flavored: request IDs, idempotency keys, typed errors, expandable objects.

### 3.7 Talking to upstream money movers

Ledger does **not** call card networks. Payments service:

```text
1. Persist payment intent
2. Call rail (uncertain window handled there)
3. On known effect → PostJournal(journal_key=payment_transition_id)
4. Ledger ACK → payment marks LEDGERED
```

If payment crashes after ledger post: payment recovers by journal_key uniqueness / inquiry.

### 3.8 Multi-region (money is single-writer)

| Plane | Mode |
|-------|------|
| API edge | Active-active |
| Journal writes | **Home cell per book** |
| Balance reads | RYW via home; eventually OK for analytics |
| Failover | Epoch fence + WAL/outbox replay + recon |

**Deal-breaker:** multi-master CRDT balances for money.

### 3.9 Storage trade-offs

| Data | Store | Why |
|------|-------|-----|
| Journals/postings | Strong SQL (PG/Spanner/Cockroach) | TX + constraints |
| Idempotency | Same SQL unique + Redis cache | Correctness + speed |
| Snapshots | SQL / KV | Fast balance |
| Cold history | Object store / columnar | Audit cheap |
| Outbox | Same TX as journal | Reliable events |

### 3.10 Rollout & operations (Stripe cares)

- **Dark launch:** dual-write shadow journals, compare balances.  
- **Feature flags:** new account types, new fee recipes.  
- **Expand/contract:** add column nullable → backfill → enforce.  
- **Paging freeze:** pause payouts if recon break severity high.  
- **Journal recipe versioning:** `recipe_version` on metadata for migrations.

### 3.11 Deal-breakers (say early)

| Temptation | Failure |
|------------|---------|
| Float money | Rounding exploits |
| Update posting in place | Audit broken |
| Blind retry without journal_key | Double post |
| Active-active writers | Divergent books |
| ACK before durable | Ghost money |
| Silent “fix” balance | Fraud/loss |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Payments / Payouts / Disputes / Lending
              |
              v
        API Gateway (AA)
              |
              v
     Ledger API (edge) ── AuthN/Z (service + book ACL)
              |
              v
     Directory: book_id → home cell
              |
              v
     Ledger Home Cell
        |-- Idempotency Store
        |-- Journal TX Engine
        |-- Postings Append
        |-- Snapshotter
        |-- Outbox
              |
              +--> Read replicas (non-RYW analytics)
              +--> Archive tier
              +--> Downstream: webhooks, warehouse, recon
```

### 4.2 Sequence: idempotent post

```text
Client → POST /journals (Idempotency-Key / journal_key)
Cell → begin TX; insert idempotency
     → validate balanced + policies
     → insert journal+postings
     → update snapshot (or mark dirty)
     → outbox event
     → complete idempotency
     → commit
Client ← 200 Journal
Retry → same key → stored response (no new postings)
```

### 4.3 Sequence: balance read

```text
Client → GET balance(account)
Cell → load snapshot(version=V, bal=B)
     → sum postings where seq > V
     → return B + delta (available/pending split)
```

### 4.4 Sequence: regional failover

```text
Cell A primary fenced (epoch N)
Cell B promoted epoch N+1
Replay A's outbox / WAL gap
Recon job: compare rail vs ledger for window
Payouts paused until severity clears
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard money invariants

1. **Accept ⇒ durable journal** before client success.  
2. **Idempotent post** by `(book_id, journal_key)`.  
3. **Balanced journals** enforced in TX.  
4. **Immutable postings** — corrections are new journals.  
5. **Atomic multi-account** apply (all postings or none).  
6. **Single-writer home** per book/account shard.  
7. **Integer minor units** only.  
8. **Outbox** for downstream at-least-once; consumers idempotent.  
9. **Recon breaks** first-class; never silent balance edits.  
10. **Fencing tokens** on leader failover.

**Resolved:** “exactly-once money” = unique journal keys + durable TX + no second economic effect — not “Kafka EOS magic.”

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; one PG; snapshots nightly |
| 10× | Ledger service boundary; Redis idem cache; continuous snapshotter |
| 100× | Shard by merchant/book; cells; hot-account dedicated shards |
| 1000× | Period partitions; hierarchical books; stream balancers; regional homes |

**Hotspot:** popular merchant payable account — serialize by account; consider sub-accounts (`payable#2026-08`) for append locality; never lose global merchant balance view (rollup).

### 5.3 Maintainability

- Property tests: random journals always balance or reject.  
- Recipe catalog versioned (capture_v3, refund_v2).  
- Replay tooling: rebuild balances from postings.  
- Schema migrations expand/contract.  
- Ops runbooks: stuck PROCESSING idempotency, failover fence, recon.

### 5.4 Progressive scale deep dive

**1× (~200 post/s peak)**

- Postgres: `journals`, `postings`, `accounts`, `idempotency`.  
- TX per post; balance via snapshot table updated in TX for small scale.  
- Nightly checksum vs payments.

**10×**

- Separate ledger service.  
- Outbox → Kafka/Pulsar for read models.  
- Idempotency cache; unique constraint remains SoT.  
- Continuous snapshot every N postings.

**100×**

- Cell per shard range of `book_id`.  
- Spanner/Cockroach or sharded PG with directory.  
- Hot merchant isolation.  
- Automated recon classes.

**1000× (~200K post/s)**

- Append partitions by book+day.  
- Balance materialization pipeline with lag SLOs.  
- Regional home assignment sticky.  
- Archive tier automatic; legal hold exceptions.

### 5.5 Concurrent same-key retries

```text
T0: req A inserts PROCESSING
T1: req B conflicts → waits or gets 409 Conflict Retryable
T2: A commits COMPLETE
T3: B reads COMPLETE same hash → returns journal
If A crashes in PROCESSING:
  sweeper after TTL: inquire payment SoT OR mark failed if no side effects yet
  Never create second journal with new key for same business event
```

### 5.6 Cross-shard journals

Prefer **keep all accounts of a journal in one book/cell**. Cross-book transfers:

```text
Two local journals linked by transfer_id + outbox saga
Or hierarchical clearing accounts in a platform book
```

**Deal-breaker:** distributed TX across many cells on the checkout hot path without clear ownership.

### 5.7 Snapshot races

```text
Writer holds per-account lock / serial TX
Snapshot writer reads max(seq) under same serialization
Or: snapshot is advisory; always sum(delta) with seq watermark from TX
```

### 5.8 Rollout: dual-write / dual-read

```text
Phase 1: old balance table still authoritative; ledger shadow posts
Phase 2: compare diffs; alert on mismatch
Phase 3: ledger authoritative; old table derived
Phase 4: remove old writes
```

Feature flag per merchant cohort. Instant rollback = flag off + recon.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Float | Rounding theft |
| Mutable edits | Unexplainable books |
| Multi-master | Split-brain money |
| Skip idempotency | Double fee/post |
| Kafka exactly-once alone | Still need keys + TX |
| Fix balance quietly | Compliance nightmare |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Accounting | Double-entry append-only |
| Idempotency | `(book, journal_key)` + body hash |
| Balances | Snapshot + delta; journal SoT |
| Multi-region | AA edge; SW home cell |
| FX | Explicit journals |
| Downstream | Transactional outbox |

### 6.2 Risks

1. Hot account contention  
2. Stuck PROCESSING keys  
3. Cross-cell transfers  
4. Failover fencing bugs  
5. Recipe migration mistakes  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: internal ledger, not full bank core |
| 5–15 | Entities + balanced journal + idempotency |
| 15–25 | Balance snapshots + available/pending |
| 25–35 | Multi-region SW + failover |
| 35–45 | Scale, rollout, recon, ops |

---

## 7. Deeper / Related Interview Questions

### 7.1 Why double-entry?

**Q: Why not a single balance column?**  
A: You lose explainability; bugs hide; audits fail. Double-entry forces every movement to name both sides.

**Q: Is double-entry slower?**  
A: Slightly more writes; correctness dominates at Stripe-class interviews.

### 7.2 Idempotency

**Q: Key scope?**  
A: Per book/merchant + key; globally unique keys also fine if namespaced.

**Q: TTL?**  
A: Money keys often retained long (years) or forever; not 24h-only.

**Q: PROCESSING stuck?**  
A: Sweeper + inquire upstream; never free-retry with new key.

### 7.3 Exactly-once

**Q: How with at-least-once clients?**  
A: Unique journal_key; first commit wins; retries return stored result.

**Q: Downstream double webhook?**  
A: Outbox may redeliver; consumers key on journal_id.

### 7.4 Balances

**Q: Strong read after post?**  
A: Read from home cell; session stickiness or always route by book.

**Q: Negative balance?**  
A: Policy: reject, allow overdraft with limit, or pending settlement — make explicit.

### 7.5 Multi-currency

**Q: Can one account hold many currencies?**  
A: Prefer one currency per account; simplifies invariants.

**Q: FX gains/losses?**  
A: Explicit P&L accounts in FX journals.

### 7.6 Corrections

**Q: Wrong fee posted?**  
A: Reverse journal + correct journal; link `corrects_journal_id`.

**Q: Edit amount in place?**  
A: Never.

### 7.7 Multi-region

**Q: Why not CRDT?**  
A: Money needs linearizable account semantics.

**Q: Read in other region?**  
A: Stale OK for analytics; RYW for payout gates via home.

### 7.8 Scale

**Q: 200K posts/s?**  
A: Shard books; append partitions; batch disk; snapshot async with bounded lag.

**Q: Hot merchant?**  
A: Dedicated cell; sub-accounts; serialize; load shed noncritical reads.

### 7.9 Ops / rollout

**Q: How to migrate recipe?**  
A: Version field; dual compute in shadow; switch flag; keep old readers.

**Q: Incident: unbalanced rows slipped in?**  
A: Constraint should prevent; if bug, quarantine account; reverse; post-mortem.

### 7.10 Interview traps

**Q: Float USD?**  
A: Never — integer cents.

**Q: Active-active both regions post?**  
A: Split brain — use directory + fencing.

**Q: 5B journals × 1KB = 5PB/day?**  
A: **5TB/day**.

**Q: This is the integration round?**  
A: No — integration is coding against docs; this is HLD of a ledger service.

### 7.11 Holds & reserves

**Q: Rolling reserve for chargebacks?**  
A: Move available → reserve accounts on schedule; release after window.

**Q: Auth hold expiry?**  
A: Time-based sweeper posts expiry journals; coordinates with payments service.

### 7.12 Security

**Q: Who can post?**  
A: mTLS service identity + fine-grained book ACL; dual control for manual journals.

**Q: Insider fraudulent reverse?**  
A: Audit; maker-checker; anomaly alerts on manual posts.

---

## 8. Appendices

### 8.1 Schema sketches

```text
books(book_id, merchant_id, region_home, epoch, status)

accounts(
  account_id, book_id, type, currency, name,
  status, created_at
)

journals(
  journal_id, book_id, journal_key, journal_type,
  external_ref, recipe_version, metadata_json,
  created_at, created_by
)
UNIQUE(book_id, journal_key)

postings(
  posting_id, journal_id, book_id, account_id,
  amount_minor, currency, ordinal
)
-- TX constraint: sum(amount_minor) by currency == 0

idempotency(
  book_id, journal_key, request_hash, status,
  journal_id, response_json, created_at, updated_at
)

balance_snapshots(
  account_id, version_seq, available_minor, pending_minor, taken_at
)

outbox(
  id, book_id, payload, created_at, published_at
)

recon_breaks(
  id, book_id, day, expected, actual, status, notes
)
```

### 8.2 API sketches

```text
POST /v1/journals
Headers: Idempotency-Key / Authorization
{
  "book_id": "book_123",
  "journal_key": "pay_456:capture:v1",
  "type": "capture",
  "external_ref": "pay_456",
  "postings": [
    {"account": "psp_clearing", "amount": -10000, "currency": "usd"},
    {"account": "merchant_payable", "amount": 9700, "currency": "usd"},
    {"account": "fee_revenue", "amount": 300, "currency": "usd"}
  ]
}

GET /v1/accounts/{account_id}/balance
→ { "available": 9700, "pending": 0, "currency": "usd", "as_of": "..." }

POST /v1/journals/{journal_id}/reverse
{ "journal_key": "pay_456:capture:v1:reverse", "reason": "..." }
```

### 8.3 Journal recipes (common)

**Capture $100.00 with $3 fee:**

```text
Dr  PSP Clearing           10000
Cr  Merchant Payable        9700
Cr  Platform Fee Revenue     300
```

**Partial refund $40.00 (fee policy net):**

```text
Dr  Merchant Payable        3880
Dr  Platform Fee Revenue     120
Cr  PSP Clearing            4000
```

**Auth hold sketch:**

```text
Dr  Authorization Holds    10000
Cr  Auth Liability Mirror  10000
```

### 8.4 State / status checklist

- [ ] Account: active / frozen / closed  
- [ ] Idempotency: PROCESSING / COMPLETE / FAILED  
- [ ] Book epoch monotonic on failover  
- [ ] Journal types enumerated + versioned recipes  

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Double-entry TX, idempotency, integer money, basic balance |
| 10× | Outbox, snapshotter, service boundary |
| 100× | Cells by book, hot account isolation, automated recon |
| 1000× | Partitions, regional homes, archive tier, stream materialization |

### 8.6 Pseudocode: post journal

```text
function postJournal(req):
  home = directory.home(req.book_id)
  return home.exec(tx):
    idemp = upsertIdempotency(req.book_id, req.journal_key, hash(req))
    if idemp.complete: return idemp.response
    validateBalanced(req.postings)
    validatePolicies(req)
    j = insertJournal(req)
    insertPostings(j, req.postings)
    bumpSnapshots(req.postings)
    outbox.emit(JournalPosted(j))
    idemp.complete(j)
    return j
```

### 8.7 Reliability / chaos drills

1. Kill pod after rail success before ledger → payment retries → one journal.  
2. Duplicate client posts → one journal.  
3. Unbalanced payload → reject.  
4. Failover mid-post → fence + no duplicate.  
5. Snapshot lag spike → reads still correct via delta sum.  

### 8.8 Glossary

| Term | Meaning |
|------|---------|
| Journal | Balanced set of postings |
| Posting | Single account leg |
| Book | Tenant ledger boundary |
| Snapshot | Cached balance watermark |
| Home cell | Single-writer region/shard |
| Recipe | Versioned posting template |
| Minor unit | Integer cents / yen / etc. |
| Outbox | Durable event in same TX |

### 8.9 Interview “say this” (60 seconds)

> We expose an idempotent journal API over a double-entry, append-only ledger. Postings are immutable; balances are derived from snapshots plus deltas. Money writes are single-writer per book home cell even if the API edge is global. Retries use journal keys and body hashes; corrections are reversing journals. Downstream systems consume via transactional outbox. We never use floats, never edit history, and we treat reconciliation breaks as first-class ops objects.

### 8.10 Related systems map

```text
Payments Orchestrator ──► Ledger API ──► Journals/Postings
Payouts / Lending / Disputes ──┘         │
                                         ▼
                                   Snapshots / Balances
                                         │
                              Outbox ──► Webhooks / Warehouse / Recon
```

### 8.11 HLD vs integration round

| Round | What you do |
|-------|-------------|
| **System design (this)** | APIs, data model, invariants, failure, scale, rollout |
| **Integration coding** | Parse docs, call Stripe APIs, transform JSON, combine local+remote data |

Do not spend design time writing Elements boilerplate.

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| Float dollars | Integer minor units |
| CRDT balances | Not for money SoT |
| Mute old posting | Append reverse |
| One Redis for all idempotency at 1000× | Shard + SQL unique |
| 5B×1KB=5PB/day | **5TB/day** |
| Skip recon | Silent drift |

### 8.13 Ops metrics

- post_success / post_conflict_409 / post_unbalanced  
- idempotency_processing_age_p99  
- snapshot_lag_seq  
- balance_rebuild_time  
- recon_break_open_count  
- cell_epoch / failover_count  

### 8.14 Manual journal controls

```text
POST /v1/admin/journals  (dual control)
- requires two approvers above threshold
- reason code mandatory
- pages on-call + audit sink
```

### 8.15 Account types (chart sketch)

| Type | Examples |
|------|----------|
| Asset | PSP clearing, cash |
| Liability | Merchant payable, customer balance |
| Revenue | Platform fees |
| Expense | Network fees, dispute losses |
| Contra/pending | Auth holds, reserves |

### 8.16 As-of balance semantics

```text
GET /balance?as_of=T
= snapshot at T'≤T + postings with committed_at ≤ T
Only committed journals; PROCESSING invisible
```

---


### 8.A Stripe interview emphasis (map to this problem)

| Theme | How it shows up here |
|-------|----------------------|
| API correctness | Explicit request/response contracts, typed errors, idempotency where mutations exist |
| Data models | Normalized entities, constraints, append-only where audit matters |
| Idempotency | Keys, request hashes, in-flight states, replay safety |
| Double-entry / money | If money touches the design, journals/balances—not float counters |
| Regional failure | Home cell / fencing / directory; what is AA vs single-writer |
| Rollout | Shadow, canary, expand/contract, flags, rollback |
| Operations | SLOs, freezes, runbooks, recon, hot-key isolation |

### 8.B Clarify questions you should always ask

1. What is the consistency requirement (money vs metrics)?  
2. Who is the client (merchant, internal, browser)?  
3. What is the failure domain (AZ, region, dependency)?  
4. What is MVP vs phase 2?  
5. What QPS classes exist (write/read/async)?  
6. What is the audit/compliance need?  
7. What is the rollback story?  

### 8.C Estimation hygiene worked example

```text
avg = daily / 86400
peak = avg * peak_factor (often 3–5×; on-call 10× for launches)
amplification = fanout * retries * postings_per_event
storage_day = events/day * bytes * replicas_factor
Watch unit errors: 1e9 * 1e3 B = 1e12 B = 1 TB (not PB)
```

### 8.D Reliability deep template

1. Durability before ACK for accepted side effects  
2. Idempotent mutations  
3. Valid state transitions only  
4. Timeout uncertainty protocol for external calls  
5. Single-writer homes for critical state  
6. Fencing on leader/region failover  
7. Recon / drift detection  
8. Load shedding order (what degrades first)  
9. Auditability  
10. Security fail-closed on sensitive paths  

### 8.E Scalability deep template

| Lever | When |
|-------|------|
| Vertical | Early |
| Cache | Read-heavy stale-tolerant |
| Shard by tenant | Multi-tenant OLTP |
| Queue + workers | Async fanout |
| Cell architecture | Blast radius |
| Hierarchy | Hot keys / global counters |
| Cold tier | Audit/history |

### 8.F Maintainability deep template

- Schema expand/contract  
- Contract tests  
- Deterministic simulators  
- Feature flags  
- Ownership + SLIs  
- Replay tooling  
- Documentation of invariants  

### 8.G Progressive scale narrative

**1×:** Correctness in a modular monolith; one primary datastore; metrics basic; single region with DR story sketched.  

**10×:** Separate hot path workers; harden idempotency; add outbox; dashboards/alerts; shadow new components.  

**100×:** Shard/cell by tenant; isolate hot tenants; automate recon/exception queues; multi-region edge with home writes.  

**1000×:** Hierarchical aggregation; regional homes; stream materialization; archive tiers; dedicated incident tooling; capacity forecasting.

### 8.H Regional failure playbook

```text
1. Detect (health, quorum loss, error burn)
2. Fence old writer epoch
3. Promote home / redirect directory
4. Replay outbox/WAL safely
5. Freeze risky money ops if recon uncertain
6. Reconcile gaps
7. Postmortem + game day update
```

### 8.I Rollout playbook

```text
design → dual write/shadow → compare → canary → ramped GA → remove old path
Rollback: flag off / pin previous bundle / re-point directory
```

### 8.J Ops metrics starter pack

- success_rate / explicit error classes  
- latency p50/p99 by QPS class  
- lag (outbox, replication, snapshot)  
- pending_age for uncertain money  
- throttle/deny rates  
- recon_break_count  
- hot_key saturation  
- config_version / epoch  

### 8.K Deal-breaker gallery (global)

| Temptation | Failure mode |
|------------|--------------|
| Float for money | Rounding exploits |
| Blind retry external side effect | Double charge / double dispatch |
| Active-active multi-master balances | Split brain |
| Fail-open authZ on money | Fraud |
| Mute historical ledgers/logs | Unauditable |
| OFFSET pagination | Dup/skip |
| Single global Redis as SoT | Hotspot / loss |
| “Kafka exactly-once” as only control | Still need app keys |
| Ignoring recon | Silent drift |
| Treating HLD like integration coding | Wrong skills demonstrated |

### 8.L API sketch conventions

```text
POST /v1/...   Idempotency-Key for mutations
GET /v1/.../{id}
GET /v1/...?starting_after=...&limit=...
Errors: { type, code, message, request_id }
Money: integer minor units + currency
```

### 8.M Schema conventions

```text
*_id (string snowflake)
created_at (server)
version / epoch (fencing)
request_hash (idempotency)
amount_minor (bigint)
UNIQUE constraints for invariants
```

### 8.N Chaos drill catalog

1. Kill process after external success before local commit  
2. Duplicate client retries  
3. Duplicate webhooks/events  
4. Region partition  
5. Dependency timeout  
6. Hot key stampede  
7. Bad config canary  
8. Clock skew  

### 8.O 45-minute plan template

| Min | Focus |
|-----|-------|
| 0–5 | Scope + invariants |
| 5–15 | Core API + data model |
| 15–25 | Failure + idempotency/uncertainty |
| 25–35 | Scale 10×/100×/1000× |
| 35–45 | Rollout, ops, multi-region |

### 8.P HLD vs integration round (reminder)

**HLD:** architecture, trade-offs, deal-breakers, progressive scale.  
**Integration:** implement against documented external APIs in a coding environment.  
Do not waste HLD time writing client SDK boilerplate.

### 8.Q “Say this” closer template

> Start from invariants and APIs. Put correctness-critical writes in a single-writer home cell. Make side effects idempotent and reconcilable. Roll out with shadow/canary and freeze switches. Scale by naming which QPS class and partition breaks first—not by drawing every possible box.

### 8.R Related reading (mental models)

- Stripe idempotency blog mental model (keys + stored responses)  
- Double-entry bookkeeping basics  
- Outbox pattern  
- Cell-based architecture  
- Token bucket rate limiting  
- Synchronous vs asynchronous coupling  

### 8.S Load-shedding order (example)

1. Debug/admin expansive exports  
2. Analytics/materialization lag OK  
3. Dashboard expensive lists  
4. Non-critical webhooks delay  
5. Last: accept money intents (buffer) / authZ decisions  

### 8.T Multi-tenant isolation checklist

- [ ] Per-tenant authz  
- [ ] Per-tenant rate limits  
- [ ] Data partition key includes tenant  
- [ ] No cross-tenant cache key collisions  
- [ ] Hot tenant cell move runbook  

### 8.U Consistency cheat sheet

| Data | Model |
|------|-------|
| Ledger balances | Linearizable home |
| Idempotency records | Linearizable home |
| Feature flags | Bounded staleness + pins |
| Metrics | Eventual |
| APM traces | Eventual |
| Cache LRU values | Best-effort |

### 8.V Security cheat sheet

- mTLS service identity  
- Least privilege  
- Redaction middleware  
- SSRF egress allowlists for webhooks  
- Dual control manual money  
- Secrets rotation  

### 8.W Data retention cheat sheet

| Class | Hot | Cold |
|-------|-----|------|
| Money journals | years | forever |
| Idempotency | policy years | archive |
| Metrics raw | days | rollups forever |
| Traces | days | sampled cold |
| Rate counters | hours | aggregates |

### 8.X Interview traps about numbers

- Peak vs average  
- Retry amplification  
- Fanout amplification  
- Replica storage multiplier  
- TB vs PB mistakes  
- Forgetting secondary indexes storage  

### 8.Y Cross-links inside Stripe prep bank

Ledger ↔ payment processing ↔ idempotent payments ↔ merchant ledger ↔ third-party routing.  
Webhooks ↔ transaction APIs ↔ async financial workflows.  
Rate limiter ↔ API gateway concerns in authZ.  
Metrics/APM/counters share ingestion patterns but different correctness.  
Feature flags ↔ rollout of every other system.

### 8.Z Final whiteboard checklist

- [ ] Invariants stated  
- [ ] ER/API sketched  
- [ ] Deal-breakers named  
- [ ] Uncertainty/retry protocol  
- [ ] Home cell / AA split  
- [ ] Scale table used  
- [ ] Ops/rollout mentioned  
- [ ] Integration round explicitly distinguished if relevant  


*End of ledger bookkeeping system design.*
