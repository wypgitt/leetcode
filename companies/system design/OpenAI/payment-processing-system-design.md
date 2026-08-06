# System Design: Payment Processing Platform

> **Focus areas:** Authorize/capture/void/refund · Idempotency · Double-entry ledger · PSP routing · Holds/batching · Webhooks · Reconciliation · PCI minimization · Money invariants  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes, explicit deal-breakers, **single-writer money**, resolved exactly-once money invariants

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

Goal: **bound the money movement**—what we own vs PSP, which state machine, and how we stay reconciliable under retries and webhooks.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are merchants/users? | Platform with merchants (marketplace or SaaS billing) | Multi-tenant `merchant_id`; payout later optional |
| F2 | What payment methods? | Cards primary via **PSP** (Stripe/Adyen-class); wallets Phase 1.5 | PSP adapter interface; tokenize via PSP—minimize PCI |
| F3 | Auth/capture model? | **Auth → capture** (with holds); auto-capture option; void; refund | Explicit PaymentIntent-like state machine |
| F4 | Who is merchant of record? | We are platform; PSP settles to our/merchant accounts | Ledger must model platform fees + merchant net |
| F5 | Idempotency? | Mandatory on all money mutations | Idempotency keys with request hash |
| F6 | Holds / batching? | Auth hold funds; batch capture/settlement windows | Separate authorization lifetime vs settlement batch |
| F7 | Refunds / chargebacks? | Full/partial refunds; chargeback webhooks adjust ledger | Dispute state machine; provisional accounting |
| F8 | Routing? | Route by method/geo/MID/cost/reliability | PSP router + health scores; sticky for retries |
| F9 | Webhooks from PSP? | Source of truth for asynchronous outcomes | Verify signatures; durable ingest; reconcile |
| F10 | Merchant APIs? | Create payment, capture, refund, get status | Same invariants as internal |
| F11 | Fraud? | Hooks for risk scoring pre-auth; 3DS when required | Fraud as gate; not after irreversible capture blindly |
| F12 | Reporting? | Merchant dashboard + settlement reports | Derived from ledger, not ad-hoc counters |

**MVP functional scope (lock with interviewer):**

1. Create **Payment** with idempotency key; **authorize** via PSP (or auth+capture).  
2. **Capture** (full/partial), **void** auth, **refund** (full/partial).  
3. Internal **double-entry ledger** for all money movements.  
4. **PSP webhooks** verified + applied idempotently.  
5. **Reconciliation** jobs vs PSP settlement files/API.  
6. Fraud/risk hook before auth; 3DS redirect/challenge support stub.  
7. Minimize PCI: **no raw PAN storage**; PSP tokens / hosted fields / Elements-style.

**Out of MVP (explicitly defer):**

- Full acquiring bank / ISO8583 switch (we’re PSP-orchestrator)  
- Crypto rails  
- Complex marketplace split settlements (design ledger hooks)  
- Instant push-to-card payouts worldwide  
- Perfect multi-region active-active money writes  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Auth latency | Interactive checkout | p50 < 1s, p99 < 3s excluding 3DS user time |
| N2 | Durability | No lost money intents once accepted | Quorum/durable commit before ACK |
| N3 | Exactly-once money | **Effectively-once** ledger postings | Idempotent keys + ledger uniqueness |
| N4 | Availability | Payments critical | 99.99% control plane goal; degrade reports first |
| N5 | Consistency | Strong for balances/ledger | Single-writer home for merchant/payment |
| N6 | Multi-region | Global checkout | AA gateways; **SW money home cell** |
| N7 | Auditability | Every transition explainable | Append-only ledger + event log |
| N8 | PCI | SAQ A / A-EP preferred | Hosted collection; no PAN in our logs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Checkout → create payment → auth success → capture → settle → merchant available balance updates.  
2. Auth then void before capture → funds released; ledger reverses hold.  
3. Partial capture → remaining auth voided per policy.  
4. Refund after capture → PSP refund + ledger entries; status `REFUNDED`/`PARTIAL`.  
5. Webhook arrives before sync response → state converges idempotently.  
6. Reconciliation matches PSP settlement to ledger; exceptions queue.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click pay | Same idempotency key → same payment; no double auth |
| Client retries with different body | `409` mismatch |
| PSP timeout unknown outcome | Persist `PENDING`; inquire/reconcile; **do not** blind re-auth without guard |
| Webhook duplicate | Idempotent apply by PSP event id |
| Webhook out of order | State machine allows only valid transitions; buffer/reject stale |
| Capture after auth expired | Fail; require new auth |
| Partial refunds exceed captured | Reject |
| Chargeback | Mark dispute; provisional debit; finalize on outcome |
| Fraud decline | Terminal `DECLINED`; no capture |
| PSP A down | Route to PSP B **only if** no uncertain in-flight auth on A for that key |
| Ledger ≠ PSP | Exception → ops tooling; never “fix” balances quietly |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Merchants | 1K | 10K | 100K | 1M |
| Payments / day | 1M | 10M | 100M | 1B |
| Peak **create/auth** QPS | ~50 | ~500 | ~5K | ~50K |
| Peak **capture/refund** QPS | ~20 | ~200 | ~2K | ~20K |
| Peak **webhook ingest** QPS | ~50 | ~500 | ~5K | ~50K |
| Peak **ledger postings**/s | ~200 | ~2K | ~20K | ~200K |
| Peak **read** (status/dashboard) | ~500 | ~5K | ~50K | ~500K |
| Avg auth hold lifetime | hours | hours | hours | hours |
| Settlement batch files / day | ~10 | ~50 | ~200 | ~1K+ |
| Fraud score calls / day | ~1M | ~10M | ~100M | ~1B |

**Split write classes:** auth attempts ≠ webhook applies ≠ ledger posts ≠ reconciliation. Do not lump into one “QPS.”

**What each jump forces:**

- **10×:** Durable outbox to PSP; webhook workers; ledger jobs; Redis idempotency cache.  
- **100×:** Merchant cells; sharded ledger; PSP multi-acquire routing; automated recon at scale.  
- **1,000×:** Hierarchical ledgers; regional checkout with home money cells; stream processing for recon; hot merchant isolation.

### 1.5 Etc. (Constraints & Assumptions)

- We **orchestrate PSPs**, not become a bank in MVP.  
- Currency: multi-currency with **minor units** integers (cents)—never float.  
- Clocks: don’t use client time for money; server + PSP timestamps.  
- “Exactly-once” = no duplicate **economic effect**, not “single HTTP call in history.”

**Scope statement:**

> Design a payment processing platform that authorizes/captures/voids/refunds via external PSPs, maintains a double-entry ledger, handles holds/batching and webhooks, reconciles settlements, minimizes PCI scope, and preserves money invariants under retries—from ~1M payments/day through 10× / 100× / 1,000× with single-writer home cells for money state.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
Baseline 1M payments/day ÷ 86400 ≈ 11.6/s average
Peak ~4× ⇒ ~50 auth/s (matches table)

Each successful pay may produce:
  1 create + 1 auth response path
  1–N webhooks (auth, capture, settle)
  2–6 ledger lines (hold, capture, fees, merchant credit, ...)
→ ledger posts ≫ payment creates
```

At **1,000×**: ~50K auth/s peak; ledger ~200K posts/s → **ledger and idempotency stores** are the hot guts, not the HTTP JSON pretty layer.

### 2.2 Storage

```text
Payment row ~1 KB; events ~500 B each; ledger lines ~200 B
Per payment lifecycle ~5–10 KB total

1M/day × 8 KB ≈ 8 GB/day
1,000×: 1B/day × 8 KB = 8 PB/day? 
  1e9 × 8e3 B = 8e12 B = **8 TB/day** (not PB)

Annual at 100× (100M/day): 100e6 × 365 × 8 KB ≈ 292e12 B ≈ **292 TB/year**
```

Retain forever in cold storage for audit; hot OLTP months.

### 2.3 Bandwidth

```text
Auth to PSP ~5–20 KB each way
50K/s × 20 KB ≈ 1 GB/s peak PSP egress at 1000× → connection pools, regional PSP endpoints
Webhook ingress similar order
```

### 2.4 Memory

```text
Idempotency keys hot set for 24–72h
50K/s × 60s × 24h rough distinct ≈ billions/day keys → **sharded KV**, not one Redis
```

### 2.5 Money correctness > raw QPS

Bottleneck ranking for interviews: (1) uncertain in-flight PSP calls (2) ledger contention per merchant account (3) webhook/reorder (4) recon volume (5) throughput.

### 2.6 Holds / batching economics

```text
Auth holds: open authorizations outstanding ≈ auth_rate × hold_time
50 auth/s × 6h = 50 × 21600 = 1.08M open auths baseline peak-scale math at 1× peak
At 1000×: ~1B open? 50K/s × 21600 = 1.08B open auths — need TTL sweepers & store capacity
```

Settlement batching: net fewer bank movements; ledger still records gross economics.

---

## 3. High-Level Design

### 3.1 State machine (payment)

```text
CREATED → REQUIRES_ACTION (3DS) → AUTHORIZED → CAPTURED → (PARTIAL_)REFUNDED
              ↓                      ↓
           DECLINED               VOIDED
              ↓
           EXPIRED (auth)
Disputes can branch from CAPTURED: DISPUTE_OPEN → WON/LOST
```

**Rules:** only forward-valid transitions; money movements attach as ledger journals on transitions.

### 3.2 Double-entry ledger (sacred)

Every economic event = **Journal** with N **Postings** where `sum(postings)=0` in each currency (or balanced multi-currency with FX journal rules).

Example capture with fee:

```text
Dr  PSP Clearing / Customer Cash   100.00
Cr  Merchant Payable                97.00
Cr  Platform Fee Revenue             3.00
```

Holds often use **pending** accounts:

```text
Auth: Dr Authorization Hold  / Cr PSP Unauthorized (memo) — style varies
Capture: release hold + post final
```

**Deal-breaker:** updating a single `balance` integer without an append-only journal.

### 3.3 Idempotency

```text
Key: (merchant_id, idempotency_key)
Store: request_hash, payment_id, response snapshot, created_at
If key reused:
  same hash → return stored response
  different hash → 409
TTL: days–years per compliance (often long for money)
```

Apply similarly to **capture/refund** endpoints and **webhook event ids**.

### 3.4 Talking to PSP (uncertainty window)

```text
1. Persist local intent + outbox row (PENDING_SEND)
2. Send to PSP with Idempotency-Key
3. On known success/fail → update state + ledger
4. On timeout → leave PENDING; schedule Inquire; wait webhook
5. Never create a second PSP auth for same logical payment while PENDING uncertain
```

**Ownership of truth:** PSP for rail outcome; **our ledger** for platform accounting; recon binds them.

### 3.5 Routing

| Signal | Use |
|--------|-----|
| BIN/geo/method | Eligibility |
| Cost | Interchange-ish / PSP fee |
| Success rate | Health |
| Sticky | Same PSP for retries of same payment |

**Deal-breaker:** retrying an unknown auth on a different PSP (double charge risk) without inquiry.

### 3.6 Webhooks

```text
PSP → Verify signature/HMAC → Persist raw event (unique event_id)
   → Transition applicator (idempotent) → Ledger posts if new effect
   → ACK 200 only after durable persist (or after full apply—be consistent)
```

Prefer: durable store first, async apply, still 2xx quickly if PSP is impatient—but then **must not lose** events.

### 3.7 Holds & batch capture

- **Auth hold:** time-bounded; sweeper expires → void/expire locally + PSP.  
- **Batch capture:** merchant “capture all auths at day end” worker with rate limits.  
- **Settlement:** PSP batches payouts; we record settlement deposits and allocate.

### 3.8 Reconciliation

| Layer | Compare |
|-------|---------|
| Intent vs PSP payment objects | Status/amount |
| Ledger vs PSP balance txns | Sums per day/MID |
| Settlement file vs expected | Exceptions |

Exceptions are first-class: `recon_breaks` table + ops UI. Auto-fix only for known safe classes.

### 3.9 PCI scope minimization

| Do | Don't |
|----|-------|
| Hosted fields / PSP.js tokens | Store PAN/CVV |
| Pass tokens to PSP | Log card numbers |
| Truncate / last4 + brand only | Build DIY crypto for PAN |
| Segment network | Broad employee access to card data |

### 3.10 Fraud hooks

```text
Create payment → Risk score (sync budget ~50–150ms)
  high risk → challenge 3DS / decline
  low → proceed auth
Async ML enrich doesn’t block if policy allows—but capture may re-check
```

### 3.11 Multi-region (money is single-writer)

| Plane | Mode |
|-------|------|
| Checkout API edge | Active-active |
| Payment + ledger writes | **Home cell per merchant** (or per payment) |
| Webhooks | Land globally → forward to home cell |
| Reads | RYW via home; dashboards eventually OK |

**Deal-breaker:** multi-master ledger balances without consensus.

### 3.12 Storage trade-offs

| Data | Store | Why |
|------|-------|-----|
| Payments/state | Strong SQL (Postgres/Spanner) | TX + constraints |
| Ledger | SQL append-only; partition by merchant/time | Audit |
| Idempotency | SQL unique + Redis cache | Correctness + speed |
| Raw webhooks | Object store + DB index | Replay |
| Recon files | Object storage | Bulk |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Merchant / Checkout Client
          |
          v
   API Gateway (AA)
          |
          v
   Payments API ── Fraud/Risk ── 3DS redirect flows
          |
          v
   Payment Orchestrator (home cell)
      |           |
      |           +--> Idempotency Store
      |           +--> Payment State DB
      |           +--> Ledger Service
      v
   PSP Outbox Worker --> PSP Router --> PSP A / PSP B
                              ^
                              |
   Webhook Ingress --> Verify --> Event Store --> Applicator --> Ledger
                              |
                              v
                        Inquiry / Reaper (pending)
                              |
                              v
                     Reconciliation Workers <--> PSP Reports
                              |
                              v
                     Merchant Balances / Payout (phase)
```

### 4.2 Sequence: auth + capture

```text
Client → CreatePayment(idem_key, amount)
Orchestrator → persist CREATED; risk OK
Outbox → PSP Auth (idempotent)
PSP → authorized
Orchestrator → AUTHORIZED; ledger hold posts; return client
...
Client → Capture(payment_id, idem_key2)
Orchestrator → PSP Capture
→ CAPTURED; ledger capture/fee/payable posts
Webhook may confirm settlement later
```

### 4.3 Sequence: timeout uncertainty

```text
Outbox → PSP Auth
   X timeout
State remains AUTH_PENDING
Inquiry loop / webhook:
  if success → AUTHORIZED
  if fail → DECLINED
  if unknown → keep pending; alert if aged
NO second auth unless PSP confirms absence / new payment id policy
```

### 4.4 Sequence: refund

```text
Refund request (idempotent)
Validate captured_remaining >= refund
PSP Refund
Ledger: Dr Merchant Payable / Cr PSP Clearing (etc.)
State PARTIAL_REFUNDED / REFUNDED
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard money invariants

1. **Accept ⇒ durable payment record** before client success.  
2. **Idempotent mutations** for create/capture/void/refund.  
3. **Ledger journals balanced**; immutable posts (corrections = new journals).  
4. **No double economic auth** for one idempotency key.  
5. **Valid state transitions only** (CAS / row version).  
6. **Webhook event_id unique apply**.  
7. **Uncertainty protocol** for PSP timeouts (inquire, don’t blind retry).  
8. **Recon breaks never silently ignored**.  
9. **Single-writer home** for payment/ledger.  
10. **Integer minor units** only.

**Cancel vs capture vs void (resolved):**

- **Void:** cancel outstanding **auth** (not captured).  
- **Refund:** return after **capture**.  
- **Cancel checkout:** if only CREATED → terminal cancel locally; if AUTH_PENDING → follow uncertainty protocol; if AUTHORIZED → void.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; PG; one PSP; cron recon |
| 10× | Outbox workers; webhook fleet; ledger service boundary |
| 100× | Shard by merchant_id; cell; multi-PSP router; automated exception classes |
| 1000× | Ledger partitioning; stream recon; hot-merchant isolation; regional cells |

**Ledger hotspot:** popular merchant balance row—use **event-sourced balance** snapshots + append posts; serialize posts per account via partition key.

### 5.3 Maintainability

- PSP adapter contract tests  
- Deterministic money property tests (balance invariants)  
- Webhook replay tooling  
- Feature flags for new PSP rails  
- Audit log distinct from app logs  

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× (~1M pays/day)**

- Modular monolith; Postgres payments + ledger tables.  
- One PSP integration; synchronous auth mostly.  
- Nightly recon CSV.  
- Hosted fields for PCI.

**10×**

- Outbox worker for PSP calls; webhook consumer fleet.  
- Idempotency store hardened (unique constraints + hashed bodies).  
- Fraud scoring service RPC with tight timeout + fail policy.  
- Basic multi-MID support.

**100×**

- Shard/cell by `merchant_id`.  
- Multi-PSP router with health stats.  
- Streaming recon + automated break classes.  
- Ledger service API boundary; snapshots for balances.  
- Hot merchant dedicated DB.

**1000× (~1B pays/day)**

- Regional home cells for merchants; global edge checkout.  
- Ledger append partitions by merchant+day.  
- Real-time risk feature platform.  
- Settlement allocation at massive batch scale.  
- Read replicas / warehouses for analytics—not OLTP.

### 5.5 Uncertainty protocol (full)

```text
send_psp():
  persist local state PENDING_* with psp_idempotency_key
  try response = psp.call(timeout=T)
  if response.ok: apply_success
  if response.declined: apply_decline
  if timeout/network/ambiguous:
     schedule inquire(backoff)
     wait webhooks
     alert if age > SLA (e.g. 2 minutes interactive, longer for capture batch)

inquire():
  r = psp.get_by_idempotency_or_ref(...)
  if found success/fail: apply
  if not found AND age > threshold AND PSP semantics allow: mark failed OR safe-retry SAME key only
```

**Safe retry:** same PSP + same idempotency key only. **Unsafe:** new key / other PSP while unknown.

### 5.6 Ledger snapshotting

```text
For account A:
  posts append-only (journal_id, amount)
  snapshot every K posts or T minutes: (account, version, balance)
  read balance = snapshot + sum(posts after version)
Serialize writers per account shard to avoid snapshot races
```

### 5.7 Fee & tax hooks

- Platform fee computed at capture (or auth estimate + capture true-up).  
- Tax may be separate line items; still balanced journals.  
- Fee refund policies: proportional vs non-refundable—encode explicitly.

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Float money | Rounding exploits |
| Blind retry other PSP | Double charge |
| Mutable ledger edits | Audit nightmare |
| Ignore recon | Silent loss/overpay |
| Store PAN | PCI explosion |
| Multi-master balances | Divergent money |
| ACK before durable intent | Lost/ghost charges |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Rails | External PSPs + router |
| Accounting | Double-entry ledger SoT internally |
| Retries | Idempotency + uncertainty inquire |
| Webhooks | Verify, durable, idempotent apply |
| PCI | Token/hosted—no PAN |
| Multi-region | AA edge; SW money cell |

### 6.2 Risks

1. Double charge on naïve retry  
2. Webhook/state races  
3. Float money  
4. Active-active ledger  
5. Silent recon drift  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: PSP orchestrator, auth/capture |
| 5–15 | State machine + idempotency + uncertainty |
| 15–25 | Ledger model |
| 25–35 | Webhooks + recon |
| 35–45 | PCI, fraud, multi-region, scale |

---

## 7. Deeper / Related Interview Questions

### 7.1 Exactly-once money

**Q: How exactly-once with at-least-once webhooks?**  
A: Unique `event_id` + deterministic journal keys (`payment_id, transition, event_id`); first apply wins.

**Q: Client retries create payment?**  
A: Merchant idempotency key returns same payment.

**Q: Is PSP idempotency enough alone?**  
A: No—need local state + ledger + key mapping before calling PSP.

### 7.2 Auth / capture / void / refund

**Q: Difference void vs refund?**  
A: Void cancels auth; refund reverses capture.

**Q: Partial capture?**  
A: Capture amount ≤ authorized; remainder voided per network rules.

**Q: Auth expired?**  
A: Cannot capture; new auth required.

**Q: Multiple refunds?**  
A: Track `captured - refunded`; reject overflow.

### 7.3 Ledger

**Q: Why double-entry?**  
A: Every movement explained; balances auditable; errors surface as breaks.

**Q: Mutable balance field?**  
A: Optional cache of sum(posts); never SoT without journal.

**Q: Corrections?**  
A: New reversing journal—don’t edit old posts.

**Q: Multi-currency?**  
A: Balance per currency account; FX as explicit journal pair.

### 7.4 PSP timeout

**Q: What if HTTP 500 after charge succeeded?**  
A: Classic. Persist pending; inquire by idempotency/PSP reference; webhook converges; never new charge casually.

**Q: Retry immediately?**  
A: Only with same PSP idempotency key; still may need inquire if unknown.

### 7.5 Webhooks

**Q: Out-of-order webhooks?**  
A: Applicator checks current state; ignore stale or queue until prerequisite state.

**Q: Signature verification?**  
A: HMAC/public key per PSP; reject failures; alert spikes.

**Q: ACK timing?**  
A: Durable receive minimum; full apply preferred if latency allows.

### 7.6 Reconciliation

**Q: Daily totals don’t match?**  
A: Break into MID/currency/time buckets; find missing webhooks/pending; open tickets; don’t auto-adjust merchant cash without rules.

**Q: Who wins PSP or ledger?**  
A: Rail cash movement is PSP/bank reality; ledger must be adjusted via controlled journals once understood.

### 7.7 Routing & multi-PSP

**Q: When to failover PSP?**  
A: Hard declines/outages; not during uncertain pending of another PSP for same payment.

**Q: Cost-based routing risks?**  
A: Approval rate may dominate cost; measure net revenue.

### 7.8 Fraud & 3DS

**Q: Where does 3DS sit?**  
A: Before hard auth completion; `REQUIRES_ACTION` until challenge done.

**Q: False positives?**  
A: Challenge vs block trade-off; merchant risk preferences.

### 7.9 PCI & security

**Q: Are last4 + brand PAN data?**  
A: Generally limited data; still protect; never store CVV (forbidden post-auth).

**Q: Logs?**  
A: Redact; tokenize; structured field denylist.

**Q: Insider threat?**  
A: Least privilege; audit access to refund APIs; dual control for large payouts.

### 7.10 Multi-region

**Q: Why not CRDT balances?**  
A: Money needs linearizable account semantics; use single-writer.

**Q: Webhook hits wrong region?**  
A: Forward to home by `payment_id`/`merchant_id` directory.

**Q: DR failover?**  
A: Fence old writer epoch; replay outbox carefully; expect recon after.

### 7.11 Scale & sharding

**Q: Shard key?**  
A: `merchant_id` (or `payment_id` with merchant secondary). Keep payment + its journals together.

**Q: Hot merchant?**  
A: Sub-accounts / period partitions; dedicated cell; serialize per account shard.

**Q: 200K ledger posts/s?**  
A: Append-only partitioned logs; snapshot balances async; batch writes.

### 7.12 Holds & batching

**Q: Why auth-hold not instant capture?**  
A: Merchants verify fulfillment (e.g. rides, hotels); reduce refunds.

**Q: Batch capture stampede?**  
A: Jitter + rate limit per MID; prioritize aging auths.

### 7.13 Marketplace (optional depth)

**Q: Split payments?**  
A: On capture, journal to multiple merchant payables + platform fee; payouts later from payables.

**Q: Seller gets paid before chargeback?**  
A: Rolling reserves; delay payouts; risk of negative balance.

### 7.14 Interview traps

**Q: Float for USD?**  
A: Never—use integer cents.

**Q: “Kafka exactly-once saves us”?**  
A: Helps processing; still need ledger uniqueness & PSP uncertainty protocol.

**Q: Active-active both regions auth same cart?**  
A: Double auth risk—directory + fencing.

**Q: 1B payments/day × 8 KB = 8 PB/day?**  
A: **8 TB/day**. 1e9×8e3=8e12 B=8 TB.

### 7.15 Cancel / resume (resolved)

**Q: Resume a stuck PENDING auth?**  
A: Inquiry/webhook resume—not a second create. Terminal only when rail known or policy expires with explicit void attempt + recon.

**Q: Idempotent refund vs replay attack?**  
A: Authn/authz + idempotency key + user confirmation for large amounts; keys don’t bypass authz.

---

## 8. Appendices

### 8.1 Schema sketches

```text
payments(payment_id, merchant_id, amount, currency, state, psp, psp_ref,
         auth_expires_at, captured_amount, refunded_amount, version, ...)

idempotency(merchant_id, key, request_hash, payment_id, response_body, created_at)

ledger_journals(journal_id, merchant_id, payment_id, type, created_at)
ledger_postings(journal_id, account_id, amount_minor, currency)  -- sum=0

psp_events(event_id PK, psp, payload_ref, received_at, applied_at)

recon_breaks(id, day, mid, currency, expected, actual, status)

accounts(account_id, merchant_id, type, currency)  -- payable, fee_revenue, clearing, ...
```

### 8.2 API checklist

- [ ] `POST /v1/payments` + Idempotency-Key  
- [ ] `POST /v1/payments/{id}/capture`  
- [ ] `POST /v1/payments/{id}/void`  
- [ ] `POST /v1/payments/{id}/refunds`  
- [ ] `GET /v1/payments/{id}`  
- [ ] Webhook endpoints per PSP  
- [ ] Internal recon admin  

### 8.3 State transition checklist

- [ ] CREATED → AUTHORIZED / DECLINED / REQUIRES_ACTION / CANCELLED  
- [ ] AUTHORIZED → CAPTURED / VOIDED / EXPIRED  
- [ ] CAPTURED → PARTIAL_REFUNDED / REFUNDED / DISPUTE_*  
- [ ] Each transition has ledger recipe or explicit none  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| PSP | Payment service provider |
| Auth | Reserve funds |
| Capture | Take reserved funds |
| Void | Cancel auth |
| Journal | Balanced set of postings |
| Clearing | In-transit money account |
| Recon | Compare internal vs PSP/bank |
| MID | Merchant ID at acquirer/PSP |
| Uncertainty window | After send, before known outcome |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | State machine, idempotency, ledger, one PSP, basic recon |
| 10× | Outbox, webhook workers, fraud hook |
| 100× | Merchant cells, multi-PSP routing, automated breaks |
| 1000× | Sharded ledger, regional homes, stream recon |

### 8.6 Ledger recipes (common transitions)

**Authorize $100.00 (hold-style sketch):**

```text
Dr  Authorization Holds (asset contra / memo accounts per your chart)
Cr  Customer Obligation / PSP Auth Mirror
(amounts in minor units: 10000)
```

**Capture $100.00 with $3 fee:**

```text
Dr  PSP Clearing                     10000
Cr  Merchant Payable                  9700
Cr  Platform Fee Revenue               300
(+ release hold journals)
```

**Partial refund $40.00:**

```text
Dr  Merchant Payable                  3880   (if fee policy net)
Dr  Platform Fee Revenue               120   (fee unwind policy-dependent)
Cr  PSP Clearing                      4000
```

Exact chart-of-accounts varies; interviews care that you **balance** and **don’t mutate old posts**.

### 8.7 Uncertainty state detail

```text
AUTH_PENDING / CAPTURE_PENDING / REFUND_PENDING
Fields: psp_request_id, idempotency_key_to_psp, sent_at, last_inquire_at, inquire_count
Transitions out only when:
  - sync response definitive, OR
  - webhook definitive, OR
  - inquire definitive, OR
  - policy timeout + recon procedure (ops-heavy; rare)
```

**Never** open a second PSP charge for the same local `payment_id` while `*_PENDING`.

### 8.8 Webhook applicator pseudocode

```text
onPSPEvent(e):
  if seen(e.event_id): return OK
  durably_store(e)
  p = load_payment(e.payment_ref) under home cell
  if !valid_transition(p.state, e.type): 
      record_out_of_order(e); return OK  # or retry later
  apply_state(p, e)
  post_ledger_journals_idempotent(journal_key=e.event_id)
  mark_applied(e.event_id)
```

### 8.9 Reconciliation daily loop

```text
1. Pull PSP settlement / balance transactions for day D
2. Aggregate internal ledger by MID/currency for day D
3. Diff → recon_breaks rows
4. Classify: missing webhook | pending aged | fee mismatch | FX | unknown
5. Auto-safe fixes only for known classes; else human queue
6. Merchant reports freeze until high-severity breaks cleared (policy)
```

### 8.10 PCI boundary diagram

```text
[Browser] --PAN--> [PSP Hosted Fields / iframe]
[Browser] --token--> [Our Checkout Backend] --token--> [PSP API]
[Our vault] stores: customer_id, psp_payment_method_token, last4, brand
Logs: redaction middleware strips PAN-like patterns
```

### 8.11 Interview “say this” summary (60 seconds)

> We’re a PSP orchestrator: PaymentIntent-style state machine with authorize/capture/void/refund; every mutation is idempotent; we persist before calling the PSP and treat timeouts as **uncertainty** to inquire—not a free retry to a second charge; webhooks are signature-verified and applied once by event id; a **double-entry ledger** is the accounting SoT; reconciliation binds ledger to PSP settlements; PCI scope minimized via hosted tokenization; money writes are **single-writer home cell** even if checkout edge is global.

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| Float dollars | Integer minor units |
| Retry auth on other PSP while pending | Double charge risk |
| Kafka EOS = correct money | Still need ledger keys + inquire protocol |
| Update balance in place only | No audit trail |
| Active-active both regions capture | Split brain money |
| Ignore recon breaks overnight | Silent drift → merchant distrust |
| 1B pays × 8KB = 8PB/day | **8TB/day** |

### 8.13 Reliability / chaos drills

1. Blackhole PSP after send → pending + inquire recovers.  
2. Duplicate webhooks → one ledger apply.  
3. Out-of-order capture webhook before auth webhook → buffer/ignore until valid.  
4. Partial deploy double-writers → fencing epoch prevents.  
5. Refund exceeds remaining → reject with clear error.  

### 8.14 Related systems map

```text
Checkout → Payments API → Fraud → Orchestrator → PSP Router → PSPs
                              ↓
                           Ledger
PSP Webhooks → Verify → Applicator → Ledger
Recon Workers ↔ PSP Reports ↔ Breaks UI
Payouts (phase) ← Merchant Payable balances
Merchant Portal ← read models from ledger/payments
```

### 8.15 Chargeback sketch (Phase 1.5)

```text
DISPUTE_OPEN: provisional Dr Merchant Payable / Cr Dispute Reserve
Evidence upload deadlines (ops)
WON: reverse provisional
LOST: finalize; fee journals; notify merchant
```

Keep disputes out of MVP happy path but mention accounts.

### 8.16 Idempotency matrix

| API | Key scope | PSP key |
|-----|-----------|---------|
| Create payment | merchant + key | derived sticky |
| Capture | merchant + key | capture idem key |
| Refund | merchant + key | refund idem key |
| Webhook | psp event_id | n/a |

---

*End of payment processing system design.*
