# System Design: Subscription Billing for an AI Service

> **Focus areas:** Usage metering (tokens/requests) · Aggregation pipelines · Idempotent usage events · Invoicing · Proration · Dunning · Credits · Tax hooks · PSP integration · Ledger immutability · Soft/hard limits · Grace · Disputes/refunds · Multi-currency  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct money invariants, split meter vs invoice vs payment planes, explicit at-least-once + ledger uniqueness, resolved plan-change proration  
> **Interview theme:** Bill an AI API/product — measure usage, invoice subscriptions, handle plan changes and failed payments without double-charging or silent free compute

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the money + usage system**—meter AI usage (tokens/requests), aggregate into billable quanta, generate invoices for subscription + overage, handle plan changes, failed payments (dunning), credits, tax, and PSP (Stripe-like) integration with an append-only ledger.

### 1.0 What this is / is not

| Dimension | **AI subscription billing (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Meter → rate → invoice → collect | Training / inference serving internals |
| Success | Accurate bills; no double charge; enforceable limits | Perfect real-time token UI alone |
| Money SoT | Internal **ledger** + invoice objects | PSP dashboard as only books |
| Usage SoT | Append-only **usage events** → aggregates | Mutable counters without idempotency |
| PSP role | Collector / card network gateway | Full replacement for ledger |

**Scope statement:** Design subscription billing for an AI service: usage measurement, invoicing, plan changes, and failed payments—with meter pipelines, proration, dunning, and audit-grade ledger.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who is billed? | Organizations (teams) with seats + usage; optional consumer | `billing_account_id` ≠ user_id |
| F2 | Pricing model? | Base subscription + included quota + overage (tokens/requests) | Entitlements + metered dimensions |
| F3 | Meter what? | Input/output tokens, requests, tool calls; model tier multipliers | Usage event schema + rating |
| F4 | When invoice? | Monthly cycle + immediate on some plan changes | Billing periods; invoice state machine |
| F5 | Plan changes? | Upgrade immediate; downgrade end-of-period or prorate | Proration policy explicit |
| F6 | Limits? | Soft warn + hard block when delinquent / over hard cap | Entitlement service online path |
| F7 | Failed payment? | Retry dunning; grace; then suspend API | Dunning state machine |
| F8 | Credits? | Promo / support / prepaid credits apply before card | Credit ledger lines |
| F9 | Tax? | Hook to tax provider (Vertex/Avalara-class) | Tax quote at invoice finalize |
| F10 | PSP? | Stripe-like: PaymentMethods, PaymentIntents, webhooks | Adapter; verify signatures |
| F11 | Refunds/disputes? | Partial invoice refunds; chargeback webhooks | Ledger reversals; never delete |
| F12 | Multi-currency? | Account currency; presentment; FX hooks | Money decimal + currency code |
| F13 | Idempotency? | All money + usage ingest | Idempotency keys / event ids |
| F14 | Self-serve portal? | Invoices, usage charts, payment method | Read models from ledger/aggregates |

**MVP functional scope:**

1. **Meter** usage events from inference gateway (tokens in/out, request, model).  
2. **Idempotent ingest** + aggregate into billing-period buckets.  
3. **Rate** usage against plan price book (included quota + overage).  
4. **Generate invoices** for subscription fee + metered overage (+ tax hook).  
5. **Collect** via PSP; handle webhooks; post to **append-only ledger**.  
6. **Plan change** with documented proration.  
7. **Dunning** on failed payment: retries, grace, suspend entitlements.  
8. **Credits** application; soft vs hard limits mid-cycle.  
9. Customer portal: invoices, usage, payment method update.  
10. Audit: every monetary effect explainable from ledger entries.

**Out of MVP:**

- Marketplace split payments / Connect-style complex transfers  
- Full in-house tax engine (use provider hooks)  
- Crypto  
- Real-time per-token charging as separate micro-transactions (we aggregate)  
- Multi-PSP smart routing beyond primary + backup (hooks OK)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Meter durability | No silent lost billable usage after ACK to gateway | Durable event log before ACK |
| N2 | Meter lag to aggregates | Near-real-time limits; invoice accurate | Soft limits ≤ minutes; invoice finalize exact |
| N3 | Money correctness | Effectively-once postings | Ledger unique constraints |
| N4 | Invoice latency | Generate within hours of period end | Batch windows; SLA < 6h typical |
| N5 | Checkout / pay update | Interactive | p99 < 3s excl. 3DS |
| N6 | Availability | Entitlement check on API path | 99.99% entitlement cache; fail policy explicit |
| N7 | Audit | Immutable history | Append-only; no UPDATE amount |
| N8 | Compliance | PCI minimized; SOX-ish audit | PSP tokens; exportable ledger |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Inference completes → usage event → aggregate → counts toward quota.  
2. Month end → invoice draft → tax → finalize → PSP charge → paid → ledger.  
3. Upgrade mid-cycle → prorate charge now → entitlements immediate.  
4. Downgrade → schedule end-of-period; entitlement remains until then (policy).  
5. Overage accrues → appears on invoice; soft limit emails at 80/100%.  
6. Card fails → dunning retries → customer updates card → pay open invoice → restore.  
7. Support grants credit → next invoice reduces amount due.  
8. Refund → PSP refund + ledger credit/reversal; invoice status updated.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate usage event | Idempotent `event_id`; one aggregate effect |
| Gateway timeout after billable work | At-least-once retry; dedupe |
| Invoice finalize twice | Idempotent finalize; single open invoice per period |
| Partial PSP success unknown | Pending; inquire/webhook; no double Intent without guard |
| Webhook before sync response | Converge on PSP id + internal payment id |
| Plan change during dunning | Block or carefully order; don’t wipe debt |
| Hard limit race | Entitlement version; overshoot tolerance tiny; bill overshoot |
| Currency mismatch | Account currency immutable or explicit conversion event |
| Tax provider down at finalize | Hold finalize; don’t charge wrong tax |
| Chargeback | Dispute state; provisional ledger; suspend policy |
| Clock across regions | Billing period in account TZ; meter with event_time + ingest_time |
| Customer disputes tokens | Usage evidence store; adjustment credit + note |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Billing accounts | 50K | 500K | 5M | 50M |
| Billable API QPS (peak) | 20K | 200K | 2M | 20M |
| Usage events/s | 20K | 200K | 2M | 20M |
| Distinct meters/day | 100M | 1B | 10B | 100B |
| Invoices / month | 50K | 500K | 5M | 50M |
| Payment attempts / day | 10K | 100K | 1M | 10M |
| Plan changes / day | 2K | 20K | 200K | 2M |
| Ledger lines / day | 200K | 2M | 20M | 200M |
| Currencies | 5–15 | 30+ | 30+ | global |
| Entitlement checks/s | 20K | 200K | 2M | 20M |

**What each jump forces:**

- **10×:** Stream aggregation (Kafka/Flink/Beam); shard by `billing_account_id`; entitlement cache.  
- **100×:** Hot/cold usage tiers; invoice workers partitioned; PSP rate-limit queues; cell by account.  
- **1,000×:** Regional meter ingest; global billing home cell per account; rollups precomputed; strict backpressure on non-bill path first.

### 1.5 Etc. (Constraints & Assumptions)

- Inference gateway is **upstream client** of metering; billing does not serve tokens.  
- Money amounts: **integer minor units** (cents) + ISO currency; never float.  
- **At-least-once** event delivery expected; exactly-once is **ledger/effect** uniqueness.  
- Soft limit: allow with warning; hard limit: 429/402 on API.  
- Legal invoice requirements vary by country—design tax/address hooks.

**Scope statement to repeat back:**

> Design subscription + metered billing for an AI service: idempotent usage ingest, aggregation and rating, invoice generation with tax hooks, PSP collection, proration on plan changes, dunning for failed payments, credits, soft/hard limits, and an append-only ledger as money SoT—scaling meters and accounts through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Usage events** | Per request/token batch | 20K/s | 200K/s | Ingest log |
| **Entitlement checks** | Online API admit | 20K/s | 200K/s | Cache + config |
| **Aggregates** | Per account-period-dimension | continuous | ×10 | Stream jobs |
| **Invoice jobs** | Month-end burst | 50K/day | 500K/day | Workers |
| **Payments** | PSP calls | low K/day | ×10 | Money home |
| **Webhooks** | PSP async | bursty | ×10 | Verified ingest |
| **Portal reads** | Usage graphs | medium | ×10 | OLAP/rollups |

**Anti-pattern:** one database table updated with `tokens += n` on every request as SoT without an event log.

### 2.2 Event size & throughput

```text
Usage event ≈ 200–400 bytes protobuf
20K evt/s × 300 B ≈ 6 MB/s ingest (easy)
At 2M evt/s ≈ 600 MB/s → partitioned log + local aggregation
Batching: gateway emits 1 event per request (not per token) with token counts inside
```

### 2.3 Month-end invoice burst

```text
50K accounts × invoice finalize in 2h window
≈ 7 invoices/s average; peak 10× if skewed → ~70/s
Each: rate usage + tax quote + ledger draft + optional PSP charge
PSP rate limits dominate — queue charges, don’t stampede
```

### 2.4 Entitlement path budget

```text
API p99 budget: entitlement check < 5–10ms local
⇒ cache entitlements in Redis/memory with version
Async reconcile from billing; fail-open vs fail-closed by tier
  Free/trial: fail-closed on checker errors
  Paid healthy: short fail-open with overshoot billing
```

### 2.5 Cost of wrongness

```text
Under-meter 1% at $1M/day revenue ≈ $10K/day leakage
Over-meter → trust/refund cost + support load
Design for evidence: store raw events (hot TTL) + signed aggregates
```

---

## 3. High-Level Design

### 3.1 Core objects

```text
BillingAccount
  id, currency, timezone, tax_profile, psp_customer_id, status

Subscription
  id, account_id, plan_id, status, current_period_start/end, cancel_at

Plan / PriceBook
  base_cents, included_tokens, overage_per_1k, model_multipliers, soft/hard caps

UsageEvent
  event_id, account_id, project_id, ts, model, input_tokens, output_tokens, request_count, meta

UsageAggregate
  account_id, period_id, dimension_key, quantity

Invoice
  id, account_id, period, status(DRAFT|OPEN|PAID|VOID|UNCOLLECTIBLE)
  lines[], tax_cents, total_cents, currency

Payment
  id, invoice_id, psp_intent_id, status, amount

LedgerEntry (append-only)
  id, account_id, journal_id, debit_account, credit_account, amount, currency, ts, ref_type, ref_id

Credit
  id, account_id, remaining_cents, reason, expires_at

DunningCase
  account_id, invoice_id, attempt, next_retry_at, state
```

### 3.2 API (logical)

| Op | Semantics |
|----|-----------|
| `IngestUsage(event)` | Idempotent; durable ACK |
| `CheckEntitlement(account, sku)` | Allow/deny + remaining quota hint |
| `ChangePlan(account, new_plan, proration_mode)` | Upgrade/downgrade |
| `ClosePeriod / GenerateInvoice` | Draft→rate→tax→finalize |
| `PayInvoice / AttachPaymentMethod` | PSP flows |
| `ApplyCredit` | Support/promo |
| `Refund / Adjust` | Ledger-backed |
| `GetUsage / ListInvoices` | Portal |

### 3.3 Metering pipeline

```text
Inference Gateway
  on complete (or finalize stream):
    emit UsageEvent{event_id=request_id, counts, model}
    await meter ACK (or local outbox)

Meter Ingest
  validate → dedupe event_id → append usage log → ACK

Aggregator (stream)
  window by account_id + period + dimension
  update rollup store (exactly-once effect via event_id set / EOS offsets)

Rating (batch/nearline)
  quantity → cents via PriceBook
  apply included quota, then overage
```

**Gateway batching choice:** one event per **request** (with token totals) — not per token. Streaming requests: emit on terminal state; partial bill on disconnect per product policy.

### 3.4 Exactly-once vs at-least-once + ledger

| Layer | Delivery | Effect |
|-------|----------|--------|
| Usage bus | At-least-once | Dedupe `event_id` |
| Aggregates | EOS / idempotent upsert | Unique event applied set or deterministic fold |
| Invoice finalize | Idempotent by `period_id` | One invoice |
| PSP charge | At-least-once Intent create guarded | Idempotency key = `invoice_id:attempt` |
| Ledger | Append with unique `(ref_type, ref_id, entry_type)` | Effectively-once money |

**Deal-breaker:** “exactly-once pipeline” claimed without **idempotency keys** at money boundaries.

### 3.5 Invoicing & proration

**Subscription line:** base plan fee for period.  
**Metered lines:** sum(overage dimensions).  
**Credits:** apply to reduce `amount_due`.  
**Tax:** compute on taxable lines via provider.

**Plan change policies (pick & document):**

| Change | Cash | Entitlement |
|--------|------|-------------|
| **Upgrade** | Charge prorated delta now (or next invoice with immediate entitlement) | Immediate |
| **Downgrade** | Credit unused OR take effect next period | Per policy (**MVP: next period**) |
| **Cancel** | Access until period end; no refund MVP | End of period |

**Proration math (upgrade now):**

```text
remaining_fraction = remaining_seconds / period_seconds
amount = (new_base - old_base) * remaining_fraction
integer cents: banker's rounding or always round half up — pick one & test
```

### 3.6 Soft vs hard limits & grace

| Mechanism | Behavior |
|-----------|----------|
| Soft limit | Notify at 80/100% included; API continues; overage accrues |
| Hard cap | Block when `usage >= hard` or `account SUSPENDED` |
| Grace (dunning) | After fail: N days still allow API; then hard suspend |
| Prepaid credits | Consume credits before overage invoice |

**Entitlement document versioned:** `{plan, hard_caps, status, grace_until, version}`. Online path reads cache; billing updates version.

### 3.7 PSP integration (Stripe-like patterns)

| Pattern | Use |
|---------|-----|
| Customer + PaymentMethod | Store `psp_customer_id`; no PAN |
| PaymentIntent / Charge | Collect `amount_due` |
| Idempotency-Key | `pay_{invoice_id}_{attempt}` |
| Webhooks | `payment_intent.succeeded/failed`, `charge.dispute.*` |
| Customer Portal / SetupIntent | Update card |
| Retry / smart dunning | Internal scheduler + PSP |

**Internal SoT:** Invoice + Ledger. PSP is **execution**. Reconcile daily settlement files.

### 3.8 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Usage SoT | Append-only events | Replay/audit | Mutable counter only |
| Money SoT | Double-entry ledger | Disputes/recon | PSP balance alone |
| Aggregation | Stream + period rollups | Scale meters | Sync write to SQL per token |
| Limits | Cached entitlements | API latency | Billing DB join on every request |
| Proration | Explicit policy table | Predictable $ | Ad-hoc engineer math |
| Failed pay | Dunning SM + grace | Revenue + fairness | Instant wipe with no UX |
| Tax | Provider hook | Compliance | Hardcode rates in app |
| Float money | **Forbidden** | Rounding bugs | `double` dollars |

---

## 4. Architecture Diagram

```text
  +---------------------+
  | Inference Gateway   |
  | complete → usage    |
  | CheckEntitlement()  |
  +----------+----------+
             |                    +----------------------+
             | events             | Entitlement Cache    |
             v                    | plan, caps, status   |
  +----------------------+        +----------^-----------+
  | Meter Ingest API     |                   |
  | idempotent event_id  |                   | versioned updates
  +----------+-----------+                   |
             | append                        |
             v                               |
  +----------------------+      +------------+------------+
  | Usage Log (Kafka)    |----->| Aggregator / Rating     |
  +----------------------+      | rollups by account+period|
                                         |
                                         v
                                +------------------+
                                | Rollup Store     |
                                | (Bigtable/PG/OLAP)|
                                +--------+---------+
                                         |
         +-------------------------------+-----------------------------+
         |                               |                             |
         v                               v                             v
  +--------------+              +----------------+             +---------------+
  | Invoice Svc  |              | Ledger Svc     |             | Credit Svc    |
  | draft/final  |------------->| append-only    |<------------| grants/apply  |
  | tax hook     |              | journals       |             +---------------+
  +------+-------+              +--------+-------+
         |                               ^
         | pay                           | postings
         v                               |
  +--------------+     webhooks   +------+--------+
  | Payment Svc  |<---------------| PSP (Stripe)  |
  | dunning SM   |--------------->| Intents/PM    |
  +------+-------+                +---------------+
         |
         v
  +--------------+    +----------------+
  | Portal API   |    | Tax Provider   |
  | usage/invoices|   | quote/finalize |
  +--------------+    +----------------+

  Control: Plan Catalog · Subscription Svc · Dunning Worker · Recon Worker
```

**Usage happy path:**

```text
Request admitted (entitlement OK) → infer → emit event_id=request_id
→ ingest durable → aggregate → rollup++
```

**Month-end:**

```text
For each account period:
  draft invoice lines from subscription + rated rollups
  apply credits → tax quote → finalize OPEN
  PaymentIntent (idempotent) → webhook PAID → ledger journal → entitlement healthy
```

**Failed payment:**

```text
failed → DunningCase(attempt=1..N, backoff)
→ emails; grace_until set
→ exhausted → SUSPEND entitlement version++
→ card updated → pay OPEN invoices → RESTORE
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No billable inference without durable usage intent** (or explicit free tier policy with sampled audit). Prefer: admit → work → meter with outbox if needed.  
2. **`event_id` uniqueness** ⇒ one aggregate effect.  
3. **Ledger append-only**; corrections = reversing entries.  
4. **Invoice totals immutable after FINALIZED**; void + recreate if error.  
5. **Amount due in minor units** matches sum(lines)+tax−credits.  
6. **Entitlement version** monotonic; API sees clear status.  
7. **PSP idempotency** keys stable per attempt.

#### 5.1.2 Usage ingest reliability

```text
Gateway outbox pattern (strong):
  complete inference → write outbox row same DB as request record → ACK user
  async publisher to Kafka → Meter Ingest → delete/mark outbox

Simpler:
  sync IngestUsage before returning to client
  on ingest fail: retry; if unknown, retry with same event_id
```

**Late events:** accept within watermark (e.g. 48h) into period by `event_time`; after invoice finalize, create **adjustment** on next invoice or amendment credit—never silently rewrite paid invoice.

#### 5.1.3 Payment uncertainty

| Outcome | Action |
|---------|--------|
| PSP success sync | Mark payment succeeded; wait/confirm webhook |
| Timeout | Leave PENDING; retrieve Intent; do not new Intent same key body mismatch |
| Webhook dup | Idempotent by `psp_event_id` |
| Succeeded then refund | New ledger refund journal |

#### 5.1.4 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Double charge | Idempotency keys + ledger uniques |
| 10× | Aggregate lag → bad soft limits | Lag alerts; conservative remaining |
| 100× | Month-end PSP throttle | Charge queue; prioritize renewals |
| 1,000× | Hot account event spike | Per-account partition isolation; quota on emit |

### 5.2 Scalability

#### 5.2.1 Partitioning

**Primary key:** `billing_account_id` for subscriptions, invoices, ledger, dunning (single-writer money home).  
**Usage log:** partition by `account_id` (or hash) for ordered aggregates per account.

#### 5.2.2 Aggregation strategies

| Strategy | Pros | Cons | When |
|----------|------|------|------|
| Stream incremental | Fast limits | State store ops | **Default** |
| Batch hourly | Simple | Limit lag | Small scale |
| Lambda (stream+batch recon) | Correctness | Complexity | 100×+ |

**Dimension keys examples:** `model=gpt-x|input_tokens`, `model=gpt-x|output_tokens`, `requests`.

#### 5.2.3 Online entitlement

```text
CheckEntitlement:
  e = cache.get(account_id)
  if e.status in (SUSPENDED, CLOSED): deny
  if e.hard_token_cap and rollup_hint >= cap: deny
  allow (optionally return remaining)
Async: aggregator pushes rollup_hint to cache every N seconds / N events
```

At extreme QPS, gateway keeps **local** entitlement with TTL 1–5s + version check.

#### 5.2.4 Invoice generation scale

Workers claim `period_close` shards of account space. Draft computation reads rollups (not raw events). Raw events retained for dispute evidence with TTL/tiering.

### 5.3 Maintainability

#### 5.3.1 Price book & rating purity

Rating is a **pure function**:

```text
rate(plan, aggregates, credits_input) -> lines[]
```

Version the price book (`pricebook_version`) frozen onto the invoice for audit.

#### 5.3.2 Multi-currency

- Account has **one functional currency** MVP.  
- PSP presentment in that currency.  
- If expanding: FX conversion posts explicit ledger lines; never mix currencies in one balance without conversion.

#### 5.3.3 Tax hooks

```text
finalize:
  tax_quote = TaxProvider.quote(lines, customer_address, registration)
  persist tax_quote_id on invoice
  on provider timeout: leave DRAFT; alert; no charge
```

#### 5.3.4 Observability

| Metric | Why |
|--------|-----|
| `usage_ingest_qps / dup_rate` | Pipeline health |
| `aggregate_lag_seconds` | Limit accuracy |
| `invoice_finalize_failures` | Revenue ops |
| `payment_success_rate` | Dunning |
| `entitlement_deny_rate` | Customer pain / abuse |
| `ledger_imbalance` | Should be 0 always |
| `psp_webhook_lag` | Money convergence |
| `credit_balance` | Liability |

#### 5.3.5 Dispute / refund flows

```text
Customer dispute usage:
  Support reviews event samples → Issue AdjustmentCredit
  Ledger: liability decrease; note ticket_id

Card chargeback:
  Webhook dispute.created → mark Dispute; provisional ledger
  evidence submit (usage logs, ToS)
  won/lost → finalize ledger; may suspend
```

### 5.4 Dunning state machine

```text
PAST_DUE
  attempt 1: retry T+1d
  attempt 2: T+3d
  attempt 3: T+7d
  notify each attempt
GRACE: API soft-allow until grace_until
SUSPENDED: hard deny entitlement
UNCOLLECTIBLE: invoice written off (ledger); account restricted
PAID: clear dunning; restore
```

**Product choice:** during grace, allow only paid-tier minimum or full—document. AI cost abuse: grace may be **read-only** or **reduced QPS**.

### 5.5 Credits

| Type | Behavior |
|------|----------|
| Promo | Auto-apply to invoices; expiry |
| Prepaid | Balance; consume before cash overage |
| Support adjustment | Manual; reason code required |

Application order: **credits → tax rules (jurisdiction-specific) → amount_due → PSP**.

### 5.6 Append-only ledger (double-entry sketch)

```text
Invoice finalize:
  Dr AccountsReceivable  total
  Cr Revenue_subscription / Revenue_usage / TaxPayable

Payment success:
  Dr Cash/PSPClearing  total
  Cr AccountsReceivable

Refund:
  Dr Revenue (or RefundExpense) 
  Cr Cash/PSPClearing

Credit grant:
  Dr ContraRevenue or MarketingExpense
  Cr CustomerCreditLiability

Credit apply:
  Dr CustomerCreditLiability
  Cr AccountsReceivable
```

**Imbalance detector:** continuous sum(debits)=sum(credits) per journal; account balance recon.

### 5.7 Progressive scale narrative

> **Baseline:** Kafka usage log, consumer aggregators into Postgres rollups, invoice cron, Stripe, PG ledger, Redis entitlements.  
> **10×:** Stream framework stateful aggregation; shard money by account; dunning workers; tax async.  
> **100×:** Account home cells; OLAP for portal; raw event cold tier; PSP outbound queue; lambda recon.  
> **1,000×:** Regional ingest + global billing cell; pre-aggregated cubes; entitlement edge caches; write-off factories.

---

## 6. Wrap-Up

### 6.1 Decisions locked

| Area | Decision |
|------|----------|
| Usage | Idempotent events → stream aggregates |
| Money | Append-only double-entry ledger SoT |
| PSP | Executor with webhooks + recon |
| Plans | Versioned price book; explicit proration |
| Limits | Soft overage + hard suspend/caps via entitlement cache |
| Failures | Dunning + grace then suspend |
| Corrections | Reversing entries / credits — never silent UPDATE |

### 6.2 Deal-breakers

- Float for currency  
- PSP as only accounting system  
- Mutable usage counters without event ids  
- Rewriting finalized invoices in place  
- Entitlement check hitting billing primary on every inference  
- Claiming exactly-once without idempotency at pay boundary  
- Instant delete of debt on plan change  

### 6.3 30-second close

> Meter with idempotent usage events, aggregate and rate into period rollups, freeze invoices with tax hooks, collect via PSP under idempotent payment attempts, and post every monetary effect to an append-only ledger. Plan changes follow a written proration policy; failed payments enter dunning with grace then hard entitlement suspend—so we neither leak free GPU nor double-charge.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & requirements

**Q1: Seat-based vs usage-based?**  
A: Often hybrid: base sub (seats/plan) + metered tokens. Model both lines.

**Q2: Bill the user or the org?**  
A: Org `billing_account`; users consume against it.

**Q3: Real-time balance UI?**  
A: Eventually consistent rollups OK; label “updated minutes ago.”

**Q4: Free tier?**  
A: Hard caps; fail-closed; abuse isolation; still meter for analytics.

**Q5: Committed use discounts?**  
A: Price book tiers; rating function reads commitment.

### 7.2 Metering

**Q6: Per-token events?**  
A: No—per request with counts; cost explosion.

**Q7: Stream cancel mid-response?**  
A: Bill generated tokens; policy for minimum charge.

**Q8: How to choose event_id?**  
A: Stable `request_id` from gateway; never random on retry.

**Q9: Client-reported tokens?**  
A: **Never trust clients** for billable meters; server tokenizer counts.

**Q10: Multi-model multipliers?**  
A: Dimension includes model; price book multiplier.

**Q11: Tool calls / browsing?**  
A: Separate dimensions; may have unit prices.

**Q12: Backfill missing meters?**  
A: Re-emit same event_ids from gateway logs; idempotent.

**Q13: Hot partition one enterprise?**  
A: Sub-shard by project_id then merge; isolate noisy neighbors.

### 7.3 Aggregation & rating

**Q14: Flink vs consumer groups?**  
A: At 10×+ Flink/Beam helps; baseline Kafka consumers OK with care.

**Q15: Exactly-once aggregation?**  
A: Idempotent apply of event_id or transactional state+offset.

**Q16: Included quota then overage?**  
A: Rating order documented; don’t double-count.

**Q17: Rounding?**  
A: Bill per 1K tokens with fixed rounding rules; unit tests.

**Q18: Price change mid-period?**  
A: Freeze plan version at period start or on change event; no silent mutate.

### 7.4 Invoicing

**Q19: Draft vs open?**  
A: Draft mutable; open immutable amounts; paid terminal happy path.

**Q20: One invoice per period?**  
A: Yes MVP; mid-cycle upgrade may create **immediate invoice** separate.

**Q21: Void?**  
A: Only if unpaid; ledger reverse; replace.

**Q22: What if rollup late after finalize?**  
A: Next period adjustment or amendment credit—policy.

**Q23: PDF generation?**  
A: Async from immutable invoice snapshot.

**Q24: Timezones?**  
A: Account billing TZ for period boundaries.

### 7.5 Proration & plan changes

**Q25: Why downgrade at period end?**  
A: Avoid refund complexity + gaming; upgrades prepaid delta.

**Q26: Proration rounding disputes?**  
A: Publish formula; integer cents; customer-visible preview API.

**Q27: Change plan while PAST_DUE?**  
A: Block upgrades until clear debt; or allow only payment method update.

**Q28: Annual plans?**  
A: Different period; same machines; proration fraction from annual.

**Q29: Add-ons?**  
A: Separate subscription items; rate independently.

### 7.6 Payments & PSP

**Q30: Why not invoice-only without ledger?**  
A: Refunds, partials, credits, disputes need journal truth.

**Q31: Idempotency key format?**  
A: Deterministic per invoice attempt; never reuse with different amount.

**Q32: 3DS?**  
A: Off-session renewals may soft-fail → customer action link.

**Q33: Webhook signing?**  
A: Verify secret; reject otherwise; durable inbox.

**Q34: Out-of-order webhooks?**  
A: State machine; ignore stale transitions.

**Q35: Multi-PSP?**  
A: Adapter interface; sticky in-flight Intent to one PSP.

**Q36: Reconciliation?**  
A: Daily PSP settlement vs ledger clearing account; exception queue.

### 7.7 Dunning & limits

**Q37: Soft vs hard?**  
A: Soft = bill overage; hard = deny. Delinquency uses hard after grace.

**Q38: Fail-open entitlement?**  
A: Short TTL for paid-good standing; never for suspended flag.

**Q39: Abuse during grace?**  
A: Reduced caps; alert; grace not unlimited GPU.

**Q40: How many retries?**  
A: Product/legal; typical 3–8 over 1–4 weeks.

**Q41: Partial payments?**  
A: Apply to oldest OPEN invoice; ledger per payment.

### 7.8 Credits, refunds, disputes

**Q42: Credit expiry?**  
A: Job marks expired; liability release entry.

**Q43: Refund vs credit?**  
A: Refund returns cash via PSP; credit stays on account.

**Q44: Chargeback evidence?**  
A: Usage samples, IP, ToS accept, invoice PDFs.

**Q45: Goodwill?**  
A: Support credit with reason codes; budget limits.

### 7.9 Tax & multi-currency

**Q46: Why tax at finalize not estimate only?**  
A: Legal amount on invoice; estimates OK in UI.

**Q47: VAT reverse charge?**  
A: Tax provider + customer tax IDs.

**Q48: Currency conversion fees?**  
A: Explicit line or PSP FX; ledger in account currency.

**Q49: Immutable currency?**  
A: MVP yes; changing currency = close & open account carefully.

### 7.10 Ledger & audit

**Q50: Why double-entry?**  
A: Balance sheet identity; catches bugs; recon.

**Q51: Can we UPDATE a ledger row?**  
A: **Never** for amounts; reverse.

**Q52: Journal vs entry?**  
A: Journal groups balanced entries for one business event.

**Q53: Export for auditors?**  
A: Time-ordered journals with refs to invoices/payments.

**Q54: Soft delete invoice?**  
A: Status VOID; retain bytes.

### 7.11 Consistency & races

**Q55: Entitlement vs aggregator race?**  
A: Allow tiny overshoot; bill it; or pre-reserve tokens (heavier).

**Q56: Reserve/settle for tokens?**  
A: Optional: reserve estimated max on admit; settle actual on complete—reduces abuse, adds complexity.

**Q57: Double finalize?**  
A: Unique `(account_id, period_id, invoice_kind)`.

**Q58: Pay while voiding?**  
A: State locks on invoice row/account writer.

### 7.12 Scalability drills

**Q59: 20M events/s?**  
A: Regional Kafka; local aggregate; ship rollup deltas; sample raw.

**Q60: Month-end thundering herd?**  
A: Stagger period ends by account hash; queue PSP.

**Q61: Portal global usage charts?**  
A: Precomputed cubes; not scan events.

**Q62: Cell migration of account?**  
A: Rare; drain writers; move ledger partitions carefully.

### 7.13 Security & abuse

**Q63: Meter spoofing?**  
A: Only trusted gateway service auth (mTLS).

**Q64: IDOR invoices?**  
A: AuthZ by account membership.

**Q65: PCI?**  
A: No PAN; hosted fields; SAQ A/A-EP target.

**Q66: Insider tampering?**  
A: Append-only storage; dual control for manual credits above threshold.

### 7.14 Interview craft

**Q67: How to open?**  
A: Separate meter plane / invoice plane / payment plane / entitlement plane; lock pricing & proration.

**Q68: What numbers matter?**  
A: Events/s, accounts, invoice burst, entitlement QPS, PSP limits.

**Q69: Junior trap?**  
A: `UPDATE accounts SET balance=balance-x`; float money; ignore idempotency.

**Q70: L5+ signal?**  
A: Late event after finalize policy; dunning vs abuse; ledger reversals; fail-open nuance; progressive scale.

### 7.15 Alternatives & pushbacks

**Q71: Just use Stripe Billing + metered?**  
A: Valid MVP accelerator; still need entitlement, usage evidence, AI-specific rating, ledger for finance, outage behavior—own the invariants.

**Q72: Charge per request via PaymentIntent?**  
A: Absurd PSP volume/fees; aggregate.

**Q73: Blockchain ledger?**  
A: Unnecessary; append-only DB suffices.

**Q74: Strong CAP globally for billing?**  
A: Single-writer home per account; not world-wide linearizability for meters.

### 7.16 Worked examples

**Q75: Upgrade day 10 of 30-day $30→$60 plan.**  
A: `remaining=20/30`; charge `(60-30)*(20/30)=20` now; entitlements to $60 plan immediate.

**Q76: Duplicate usage event.**  
A: Second ingest 200 OK / 409 with same body; aggregate unchanged.

**Q77: Payment webhook before API return.**  
A: Payment row created PENDING; webhook marks SUCCEEDED; API return observes same.

**Q78: Hard cap race two requests.**  
A: Both admitted near cap; overshoot δ tokens billed; next checks deny; acceptable MVP.

### 7.17 Appendix — Usage event schema

```text
message UsageEvent {
  string event_id = 1;          // = request_id
  string billing_account_id = 2;
  string project_id = 3;
  int64 event_time_ms = 4;
  string model = 5;
  int64 input_tokens = 6;
  int64 output_tokens = 7;
  int64 requests = 8;           // usually 1
  string region = 9;
  map<string,string> labels = 10;
}
```

### 7.18 Appendix — Invoice state machine

```text
DRAFT -> OPEN -> PAID
OPEN -> VOID
OPEN -> UNCOLLECTIBLE
PAID -> (refunds partial; status PAID or REFUNDED)
```

### 7.19 Appendix — Entitlement record

```text
{
  "account_id": "ba_123",
  "version": 42,
  "status": "ACTIVE", // ACTIVE|GRACE|SUSPENDED
  "plan_id": "pro_v3",
  "hard_caps": {"tokens_month": 50000000},
  "soft_thresholds": [0.8, 1.0],
  "grace_until": null,
  "rollup_tokens": 1234567,
  "updated_at": "..."
}
```

### 7.20 Appendix — Dunning schedule table

| Attempt | Delay | Action |
|---------|-------|--------|
| 0 | T+0 | Initial fail email |
| 1 | T+1d | Retry charge |
| 2 | T+3d | Retry + warn suspend |
| 3 | T+7d | Final retry |
| — | T+10d | Suspend entitlements |
| — | T+60d | Uncollectible review |

### 7.21 Appendix — NFR card

```text
Integer minor units only
Idempotent usage event_id
Ledger append-only balanced journals
Invoice immutable when OPEN/PAID
Entitlement cached; versioned
Dunning + grace then hard suspend
PSP idempotency keys
Late usage → adjustment policy
```

### 7.22 Appendix — Why reserve/settle (optional deep dive)

```text
Admit:
  reserve = estimate_max_tokens * price_factor
  if reserved+used > hard: deny
Complete:
  settle actual; release unused reservation
Pros: tighter abuse control
Cons: complexity, estimate errors, sticky state on crashes
MVP: soft overshoot billing without reserve
```

### 7.23 Appendix — Aggregation pseudocode

```text
on Event e:
  if seen(e.event_id): return
  mark_seen(e.event_id)
  period = period_of(e.account_id, e.event_time)
  for dim in dimensions(e):
    rollup[e.account_id, period, dim] += qty(e, dim)
  maybe_publish_entitlement_hint(e.account_id)
```

### 7.24 Appendix — Proration preview API

```text
POST /plan_changes/preview
{ new_plan_id }
→ {
  immediate_charge_cents, credit_cents,
  next_period_base_cents, entitlement_effective_at,
  formula_explanation
}
```

Always preview before commit in self-serve UX.

### 7.25 Appendix — Reconciliation loops

| Loop | Frequency | Compare |
|------|-----------|---------|
| Usage | continuous | gateway completes vs ingested |
| Aggregate | hourly | sum(events sample) vs rollup |
| Invoice | daily | OPEN/PAID totals vs ledger AR |
| PSP | daily | settlement vs clearing |

### 7.26 Appendix — Multi-currency note

```text
account.currency = "USD"
all invoice totals USD
PSP PaymentIntent currency USD
If customer pays with FX-converted card: PSP handles presentment;
our ledger stays USD
```

### 7.27 Appendix — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Stripe Billing is enough” | Own entitlements + AI meters + ledger |
| “Exactly-once Kafka” | Effect idempotency still required |
| “Update balance column” | Use ledger |
| “Block at soft limit” | Soft means warn; hard means block |
| “Refund by deleting invoice” | Void/reverse |

### 7.28 Appendix — Data retention

| Data | Hot | Cold |
|------|-----|------|
| Raw usage events | 7–30d | 90–365d evidence |
| Rollups | years | finance |
| Invoices | years | legal |
| Ledger | years | legal |
| Webhooks raw | 30–90d | — |

### 7.29 Appendix — Service ownership map

| Service | Owns |
|---------|------|
| Meter Ingest | event durability/dedupe |
| Aggregator | rollups |
| Subscription | plan state machine |
| Invoice | draft/finalize |
| Payment/Dunning | collection |
| Ledger | money truth |
| Entitlement | online allow/deny |
| Portal | read models |

### 7.30 Appendix — 10×/100×/1,000× checklist

| Concern | 10× | 100× | 1,000× |
|---------|-----|------|--------|
| Stream agg | ✓ | ✓ | ✓ |
| Account money home | ✓ | cell | many cells |
| Entitlement edge cache | optional | ✓ | ✓ |
| Cold event tier | optional | ✓ | ✓ |
| PSP queue | ✓ | ✓ | ✓ |
| Staggered period close | optional | ✓ | ✓ |

### 7.31 Appendix — Interview whiteboard order

```text
1) Plan + meter dimensions
2) Usage event + idempotency
3) Aggregate + rate
4) Invoice + tax hook
5) Ledger postings
6) PSP + webhooks
7) Proration
8) Dunning + entitlement
9) Soft/hard limits on API path
10) Scale & deal-breakers
```

### 7.32 Appendix — Worked ledger (payment)

```text
Invoice OPEN total 11000 cents ($110)
Finalize journal J1:
  Dr AR 11000
  Cr Revenue 10000
  Cr TaxPayable 1000

Pay success journal J2:
  Dr PSPClearing 11000
  Cr AR 11000

Settlement journal J3:
  Dr Cash 10800
  Dr Fees 200
  Cr PSPClearing 11000
```

### 7.33 Appendix — Failure injection tests

| Test | Expect |
|------|--------|
| Replay same usage 10× | Rollup +1× |
| Finalize crash mid-tax | Stays DRAFT |
| Webhook dup | Single PAID |
| Pay unknown timeout | Single Intent |
| Suspend mid-flight req | In-flight finish policy; new deny |
| Late event after PAID | Adjustment path |

### 7.34 Appendix — Glossary

| Term | Meaning |
|------|---------|
| Rating | Convert usage → money lines |
| Dunning | Retry/collection after failed pay |
| Grace | Temporary access while PAST_DUE |
| Soft limit | Warn / overage; still serve |
| Hard limit | Deny serve |
| Price book | Versioned pricing config |
| Home cell | Single-writer region for account money |
| Reversing entry | Audit-safe correction |

### 7.35 Appendix — Final seniority signals

- Split **meter / entitlement / invoice / payment / ledger** planes.  
- **Integer cents** + append-only journals.  
- **Idempotency** at usage and PSP boundaries.  
- Explicit **proration** and **late event** policies.  
- **Dunning + grace + suspend** with abuse-aware grace.  
- Progressive scale: stream agg → account cells → edge entitlement.

---

*End of Subscription Billing for an AI Service system design.*
