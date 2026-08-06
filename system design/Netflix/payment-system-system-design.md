# System Design: Netflix Subscription Payment System

> **Focus areas:** Billing cycles · Plan changes · Payment processor integration · Idempotency · Dunning / retry · Proration · Tax · Gift cards & promos · Regional payment methods · Entitlement coupling  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Money correctness invariants, split dissimilar QPS (charge vs webhook vs entitlement), explicit deal-breakers, Netflix 2025–26 interview themes  
> **Interview theme:** Netflix Billing — design subscription payments that stay correct under retries, partial failures, and global scale without double-charging or granting free access

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

Goal: **subscription billing platform** — charge members on recurring cycles, handle plan upgrades/downgrades, payment method updates, failed payment recovery (dunning), and emit entitlements so streaming access matches payment state.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Recurring billing, invoices, dunning, plan catalog | Full general ledger / ERP |
| Payments | Card, PayPal, carrier billing, regional wallets | Crypto-only niche |
| Scope | Consumer subscriptions | Ads auction billing (sibling) |
| Processor | Stripe/Adyen-class abstraction | Build PCI vault from scratch |
| Entitlement | Emit access state to streaming | Video CDN delivery |
| Correctness | Idempotent charges; no double bill | Approximate revenue OK |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Subscription model? | Monthly recurring; some annual | Billing cycle engine |
| F2 | Plans? | Basic / Standard / Premium; regional pricing | Plan catalog + geo rules |
| F3 | Free trial? | Yes — convert or cancel at end | Trial state machine |
| F4 | Plan change mid-cycle? | Upgrade immediate + prorate; downgrade end of cycle | Proration service |
| F5 | Payment methods? | Cards primary; PayPal; iDEAL etc. | PSP token vault |
| F6 | Who stores PAN? | PSP tokenization — not Netflix PCI | Vault references only |
| F7 | Renewal timing? | Charge on anniversary; retry on fail | Scheduler + dunning |
| F8 | Failed payment? | Grace period → retries → suspend → cancel | Dunning workflow |
| F9 | Idempotency? | Same request never double-charges | Idempotency keys everywhere |
| F10 | Invoices / receipts? | Email + account history | Invoice store |
| F11 | Refunds? | Partial/full; support tooling | Credit notes |
| F12 | Promos / gift cards? | Apply balance; extend trial | Promo ledger |
| F13 | Tax / VAT? | Calculate per jurisdiction | Tax engine integration |
| F14 | Entitlement? | Active / grace / suspended / canceled | Event to entitlement svc |
| F15 | Account sharing enforcement? | Out of billing core | Mention boundary |
| F16 | Chargebacks? | Mark disputed; suspend policy | Webhook handler |

**MVP functional scope (lock with interviewer):**

1. Plan catalog with regional prices and feature flags (HD, screens).
2. Subscription lifecycle: create, active, past_due, canceled.
3. Recurring charge job on renewal date via PSP with idempotency key.
4. Webhook ingestion for async PSP events (success, fail, dispute).
5. Dunning: 3 retries over 10 days with configurable schedule.
6. Plan upgrade proration charge; downgrade at period end.
7. Payment method CRUD via PSP hosted fields / token.
8. Entitlement events on state transitions.
9. Member billing history API (read).
10. Reconciliation batch vs PSP settlement files.

**Out of MVP (explicitly defer):**

- Full double-entry accounting to SAP
- Netflix-as-merchant-of-record in every country day one
- Real-time revenue recognition for finance
- Complex B2B invoicing
- Building custom fraud ML (use PSP + rules)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Money correctness | Zero duplicate charges | Idempotency + ledger |
| N2 | Charge latency (user-initiated)? | User waiting on upgrade | p99 < 3s end-to-end |
| N3 | Renewal throughput? | Spread renewals | Handle peak without stampede |
| N4 | Availability billing API? | High but not play path | 99.9% |
| N5 | Webhook processing | At-least-once from PSP | Idempotent handlers |
| N6 | Auditability | Every cent traceable | Immutable ledger entries |
| N7 | PCI scope | Minimize | SAQ-A — no raw PAN |
| N8 | Multi-currency | Local currency charge | FX at PSP or rate table |
| N9 | Compliance | PSD2 SCA in EU | 3DS flows |
| N10 | DR | Don't double-charge on failover | Strong idempotency keys persisted pre-call |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New signup: validate plan → collect PM token → create subscription → auth $0 or trial → entitlement ACTIVE.
2. Monthly renewal: scheduler fires → idempotent charge → invoice → extend period → entitlement renewed.
3. Upgrade mid-cycle: compute proration → immediate charge → new plan features now.
4. Downgrade: schedule at period end → on renewal apply new price.
5. Update card: new token → next retry succeeds.
6. Cancel: access until period end → no further renewals.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate renewal job | Idempotency key `sub_id:period_start` → PSP returns same result |
| Charge succeeds, DB write fails | Reconcile webhook / outbox ensures subscription extended |
| Webhook arrives before API response | Idempotent state machine; same terminal state |
| Partial PSP outage | Queue retries; grace period; don't suspend instantly |
| 3DS required | Return client action URL; resume charge on completion |
| Insufficient funds | Dunning retry schedule; email member |
| Proration rounding | Integer cents; document rounding policy (per line item) |
| Timezone renewal midnight | Anchor UTC stored; display local |
| Currency change (move country) | New subscription; close old per policy |
| Gift card covers partial | Apply balance ledger; charge remainder |
| Chargeback webhook | Suspend entitlement pending review |
| Clock skew on scheduler | Lease-based job execution; fencing tokens |
| Two concurrent upgrade requests | Optimistic lock on subscription version |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Paying members | 250M | 250M | 300M | 400M+ |
| Active subscriptions | 270M | 270M | 320M | 450M |
| Renewals / day | 9M | 9M | 11M | 15M |
| Peak renewals / hour | 500K | 500K | 800K | 1.2M |
| User-initiated charges / s | 50 | 500 | 2K | 10K |
| Webhooks / s | 200 | 2K | 10K | 50K |
| Invoices / month | 250M | 250M | 300M | 400M |
| Ledger entries / month | 1B | 1B | 1.2B | 1.6B |
| Dunning retries / day | 2M | 2M | 3M | 5M |

**Split classes:** renewal batch ≠ user charge ≠ webhook ≠ entitlement emit ≠ recon batch.

**What each jump forces:**

- **10×:** Renewal hour spreading; outbox pattern; read replicas for history.
- **100×:** Sharded subscription store; regional billing cells; dedicated dunning workers.
- **1,000×:** Event-sourced ledger; global idempotency store; PSP multi-home routing.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix global: different plans/prices/tax per country.
- Streaming entitlement is **downstream consumer** — billing must emit ordered state events.
- PSP (Stripe/Adyen) handles PCI; Netflix stores `payment_method_id` tokens.
- Money stored as **integer minor units** (cents).
- Interview emphasizes **idempotency** and **dunning**, not tax deep dive.

**Scope statement:**

> Design a subscription payment system with plan catalog, recurring billing, proration, PSP integration, dunning, immutable ledger, and entitlement events — correct under retries from ~9M renewals/day through 10× / 100× / 1,000× scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Renewal rate

```text
250M paying members ≈ monthly cycle majority
Renewals / day ≈ 250M / 30 ≈ 8.3M → ~9M with annual smoothing

Peak hour: many members signup evening local → assume 6% of daily in peak hour
Peak ≈ 9M × 0.06 ≈ 540K → round 500K charges/hour
≈ 139 charges/s average peak hour → burst 500/s class with jitter spread
```

**Deal-breaker:** all renewals at UTC 00:00 → thundering herd.

### 2.2 Spreading renewals

```text
Renewal window: spread ±12h around anniversary via hash(member_id)
Effective peak reduction: 10× → ~50 charges/s sustained peak class
Still need idempotency + queue workers
```

### 2.3 Storage

```text
Subscription row ≈ 2 KB
270M × 2 KB ≈ 540 GB + indexes → ~1 TB class

Ledger entry ≈ 256 B
1B entries/month retained 7 years → archival tiering
Hot ledger 90 days: 3B × 256B ≈ 768 GB

Invoice PDF metadata ≈ 1 KB; blob storage for PDFs separate
```

### 2.4 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Renewal charges | 500/s burst | 2K/s | 10K/s | worker pool |
| User-initiated charge | 50/s | 2K/s | 10K/s | upgrade path |
| Webhooks | 200/s | 10K/s | 50K/s | idempotent |
| Entitlement events | 500/s | 2K/s | 10K/s | Kafka |
| Billing history read | 5K/s | 50K/s | 200K/s | cached |
| Scheduler tick | 1K jobs/s | 10K | 50K | lease based |
| Recon batch | nightly | hourly | continuous | |

### 2.5 PSP API limits

```text
Assume PSP allows 10K req/s per merchant account
500/s peak renewals well within — but failover doubles traffic
Shard across regional merchant accounts if needed
```

### 2.6 Latency budget (upgrade charge)

| Stage | Budget |
|-------|--------|
| AuthN + load subscription | 20ms |
| Proration calc | 30ms |
| Idempotency insert | 10ms |
| PSP charge API | 500–2000ms |
| Ledger + state update | 50ms |
| Entitlement event | 20ms async |
| **User-facing p99** | **< 3s** |

### 2.7 Dunning volume

```text
Assume 5% renewal fail rate → 450K failed/day
3 retries each → 1.35M retry charges/day ≈ 15/s average
Peak retry overlap with renewals → plan separate worker pool
```

### 2.8 Cost intuition

```text
PSP fees ≈ 2% + $0.30 per txn — optimization is ops efficiency not microsecond latency
Engineering focus: avoid double charge support cost + entitlement bugs
```

### 2.9 Critical bottlenecks

1. **Thundering herd** on renewal hour.
2. **Double charge** on retry without idempotency.
3. **Split brain** subscription state vs PSP.
4. **Webhook delay** → member suspended while paid.
5. **Proration bugs** → trust loss.

---

## 3. High-Level Design

### 3.1 Component map

```text
+-------------+     +------------------+     +----------------+
| Member / UI |---->| Billing API      |---->| Subscription   |
+-------------+     +------------------+     | Service        |
                           |                 +--------+-------+
                           v                          |
                    +------+------+                   |
                    | Plan Catalog|<------------------+
                    +-------------+
                           |
          +----------------+----------------+
          v                v                v
   +-------------+  +-------------+  +-------------+
   | Payment     |  | Ledger      |  | Dunning     |
   | Orchestrator|  | Service     |  | Scheduler   |
   +------+------+  +-------------+  +-------------+
          |
          v
   +-------------+       webhooks      +-------------+
   | PSP Adapter |<--------------------| PSP (Stripe)|
   | (Stripe/    |-------------------->|             |
   |  Adyen)     |       charges       +-------------+
   +-------------+
          |
          v
   +-------------+     events      +------------------+
   | Outbox /    |---------------->| Entitlement      |
   | Kafka       |                 | Service          |
   +-------------+                 +------------------+
```

### 3.2 Entities

| Entity | Role |
|--------|------|
| `Member` | Account owner |
| `Subscription` | plan, status, period_start/end, version |
| `Plan` | price, currency, interval, features |
| `PaymentMethod` | PSP token reference |
| `Invoice` | Bill for a period or one-off charge |
| `Charge` | Attempt to collect money |
| `LedgerEntry` | Immutable debit/credit |
| `IdempotencyRecord` | key → charge result |
| `DunningCase` | retry schedule for failed renewal |

### 3.3 Subscription state machine

```text
TRIAL → ACTIVE → PAST_DUE → SUSPENDED → CANCELED
          ↑          |            |
          └──────────┘ (payment recovered)
ACTIVE → CANCELED (at period end)
```

Terminal states: CANCELED (ended), SUSPENDED (revoked access).

### 3.4 Idempotency keys

| Operation | Key pattern |
|-----------|-------------|
| Renewal charge | `{sub_id}:{period_start_iso}` |
| Upgrade charge | `{sub_id}:upgrade:{target_plan}:{effective_ts}` |
| Refund | `{charge_id}:refund:{amount_cents}` |
| Webhook | `{psp_event_id}` |
| API client request | `Idempotency-Key` header UUID |

**Rule:** persist idempotency record **before** calling PSP.

### 3.5 Payment orchestrator flow

```text
1. BEGIN TX
2. INSERT idempotency_key (unique) — if conflict return cached result
3. INSERT charge row PENDING
4. COMMIT
5. Call PSP with same idempotency key (PSP-native if supported)
6. On success: TX update charge SUCCEEDED, ledger, extend subscription, outbox event
7. On fail: mark charge FAILED, schedule dunning
```

### 3.6 Proration (upgrade)

```text
remaining_fraction = (period_end - now) / (period_end - period_start)
credit = old_plan_price × remaining_fraction
debit = new_plan_price × remaining_fraction
amount_due = round(debit - credit)
```

Document rounding: banker's rounding vs always up — pick one.

### 3.7 Dunning schedule (example)

| Day | Action |
|-----|--------|
| 0 | Renewal fail → PAST_DUE; entitlement grace 7 days |
| 1 | Retry #1 + email |
| 3 | Retry #2 |
| 7 | Retry #3; if fail → SUSPENDED |
| 30 | CANCELED if no recovery |

Grace: member keeps streaming during PAST_DUE per product policy.

### 3.8 Entitlement events

```text
SubscriptionStateChanged {
  member_id, subscription_id,
  old_status, new_status,
  plan_id, effective_at,
  event_id, causal_charge_id?
}
```

Entitlement service is idempotent on `event_id`.

### 3.9 PSP abstraction

```text
interface PaymentProvider {
  createCustomer(...)
  attachPaymentMethod(...)
  charge(idempotencyKey, amount, currency, pm_id)
  refund(...)
  parseWebhook(headers, body) → DomainEvent[]
}
```

Separate adapters per PSP; routing by country.

### 3.10 Reconciliation

Nightly: PSP settlement file vs ledger charges — flag mismatches.
Never auto double-charge; manual review queue for drift.

### 3.11 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Money SoT | Immutable ledger + PSP recon |
| Subscription SoT | Subscription service DB |
| Idempotency | DB unique constraint pre-PSP |
| Renewal timing | Spread via hash + jitter |
| PAN storage | PSP only |
| Entitlement | Async outbox events |

---

## 4. Architecture Diagram

### 4.1 Renewal sequence

```text
Scheduler→SubSvc: list due renewals (batched)
Worker→Orchestrator: ChargeRenewal(sub_id, period)
Orchestrator→IdemDB: INSERT idempotency key
Orchestrator→PSP: charge(key, amount, pm)
PSP→Orchestrator: success/fail
Orchestrator→Ledger: append entries
Orchestrator→SubSvc: extend period / PAST_DUE
Orchestrator→Outbox: entitlement event
Outbox→Kafka→EntitlementSvc: apply
```

### 4.2 Webhook sequence

```text
PSP→WebhookGW: POST signed event
WebhookGW: verify signature
WebhookGW→IdemStore: event_id seen?
Handler→Orchestrator: applyPaymentSucceeded(charge_ref)
Orchestrator: match charge row; if already SUCCEEDED → noop
Else: complete ledger + subscription (crash recovery path)
```

### 4.3 Upgrade sequence

```text
Member→API: upgrade(plan=premium)
API→Proration: compute amount
API→Orchestrator: charge prorated
Orchestrator→PSP: charge
On OK→SubSvc: update plan immediately, new period anchor policy
Outbox→Entitlement: PLAN_UPGRADED
```

### 4.4 Failure: charge OK, DB down

```text
PSP charged; Orchestrator crash before update
Webhook payment_intent.succeeded arrives later
Handler idempotently completes subscription extension
Member never wrongly suspended
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No PSP call without persisted idempotency key.**
2. **Ledger append-only** — corrections via reversing entries.
3. **Subscription period extended iff** charge SUCCEEDED or trial/grace policy.
4. **Webhook handlers idempotent** on PSP event id.
5. **Entitlement never ahead of payment** except explicit grace/trial.
6. **One active subscription per member per product line** (or explicit multi-sub model).
7. **Amounts in minor units integers.**
8. **Outbox pattern** for entitlement — no dual-write without it.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| PSP timeout | Charge stays PENDING; recon job queries PSP by idempotency key |
| Duplicate webhook | No-op |
| Duplicate scheduler lease | Fencing token rejects stale worker |
| Partial DB TX | Rollback; PSP may need refund if charged — rare if order correct |
| Wrong proration | Support credit note workflow |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Postgres subscriptions + ledger; SQS workers; single PSP |
| 10× | Shard subscriptions by member_id; renewal spread; read replicas |
| 100× | Regional billing cells; Cassandra ledger hot; dedicated webhook pool |
| 1,000× | Event sourcing; multi-PSP routing; continuous recon stream |

**Sharding:** `hash(member_id)` co-locates subscription + ledger + PM.

### 5.3 Maintainability

- Admin tools: view subscription timeline, charges, ledger, PSP refs.
- Feature flags for dunning schedule per region.
- Metrics: `charge_success_rate`, `duplicate_idem_hit`, `webhook_lag`, `past_due_count`, `proration_errors`.
- Runbooks: PSP outage, mass retry, stuck PENDING charges.

### 5.4 Exact algorithm: renewal charge

```text
function chargeRenewal(sub_id, period_start):
  key = f"{sub_id}:{period_start}"
  if cached = idem.get(key): return cached

  sub = loadSubscription(sub_id)
  amount = planPrice(sub.plan, sub.currency)
  idem.insertPending(key)  // unique constraint

  result = psp.charge(key, amount, sub.pm_id)
  if result.success:
    tx:
      ledger.credit(sub_id, amount, result.psp_ref)
      sub.extendPeriod()
      sub.status = ACTIVE
      outbox.emit(StateChanged)
      idem.complete(key, result)
  else:
    sub.status = PAST_DUE
    dunning.schedule(sub_id)
    idem.complete(key, result)
  return result
```

### 5.5 Exact algorithm: webhook apply

```text
function onPaymentSucceeded(psp_event):
  if idem.seen(psp_event.id): return
  charge = findChargeByPspRef(psp_event.payment_ref)
  if charge.status == SUCCEEDED: idem.mark(psp_event.id); return
  tx:
    charge.status = SUCCEEDED
    ledger.ensureEntry(charge)
    subscription.applySuccess(charge)
    outbox.emit(...)
  idem.mark(psp_event.id)
```

### 5.6 Dunning worker

```text
poll dunning_cases where next_retry_at <= now
for each case:
  lease(case_id)
  chargeRenewal(case.sub_id, case.period)  // same idempotency key
  if success: close case
  else: increment attempt; schedule next or SUSPEND
```

### 5.7 Multi-region

| Data | Strategy |
|------|----------|
| Subscription | Home region by member signup |
| Ledger | Home region; audit export global |
| PSP | Route to regional merchant account |
| Webhooks | Geo endpoint; forward to home if needed |
| Entitlement | Global Kafka; ordering per member_id partition |

### 5.8 Tax integration

```text
TaxQuoteService.compute(sub.plan, member.address, amount)
Add line items to invoice; store tax audit fields
Do not block interview on tax — mention Avalara/Vertex integration
```

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Call PSP before idempotency persist | Double charge on retry |
| Extend subscription before charge succeeds | Free Netflix |
| Float dollars | Rounding lawsuits |
| Mutable ledger rows | Audit failure |
| Ignore webhooks | Stuck PENDING forever |
| All renewals midnight UTC | PSP + DB outage |
| Suspend immediately on first fail | Churn spike |
| Store PAN in Netflix DB | PCI nightmare |
| Entitlement sync write in charge TX | Coupling; play path risk |
| Refund without ledger reversal | Books wrong |

### 5.10 Progressive scale deep dive

**1×**
Postgres; cron scheduler with lease; Stripe; outbox to Kafka.

**10×**
Renewal spread; 50 worker pods; idempotency Redis cache fronting DB.

**100×**
Member sharding; separate dunning cluster; webhook autoscale 10× baseline.

**1,000×**
Event-sourced subscription projections; ledger in column store; multi-active cells with conflict resolution on member home.

### 5.11 Security & compliance

- PCI: hosted fields / tokenization only.
- Webhook HMAC verification.
- PII minimized in logs; no full card numbers.
- PSD2: trigger 3DS when required; resume token flow.

### 5.12 Rollout

```text
New dunning schedule → shadow mode metrics → region canary → global
PSP migration → dual-write tokens; cutover per country
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Money correctness | Idempotency pre-PSP + immutable ledger |
| Renewal | Spread scheduler + worker pool |
| Failed pay | Dunning with grace entitlement |
| Proration | Immediate upgrade charge; deferred downgrade |
| PSP | Adapter pattern; token vault external |
| Entitlement | Outbox Kafka events |
| Recon | Nightly PSP settlement match |

### 6.2 Risks

1. Double charge incidents without idempotency discipline
2. Thundering herd renewal outages
3. Webhook/API race leaving PENDING charges
4. Proration rounding disputes
5. Cross-region member moves complexity
6. Chargeback abuse vs member experience

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: subscription not ads billing |
| 5–15 | State machine + plan change + proration |
| 15–25 | Charge flow + **idempotency** deep |
| 25–35 | Webhooks + dunning + entitlement |
| 35–45 | Scale renewals; recon; traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Idempotency

**Q: Same renewal retried — what happens?**
A: Same key → PSP returns existing payment; DB returns cached outcome; period extended once.

**Q: Client retries upgrade with new Idempotency-Key?**
A: New key = new charge attempt — client should reuse key on retry.

**Q: Idempotency TTL?**
A: Forever for money keys tied to period; or min 30 days post period.

### 7.2 Dunning

**Q: Stream during past_due?**
A: Product grace — yes during grace window; entitlement svc encodes policy.

**Q: Retry same amount or include late fee?**
A: Policy; usually same subscription amount.

**Q: Card updater services?**
A: PSP network updates; reduce false fails — mention optional.

### 7.3 Proration

**Q: Downgrade mid-cycle refund?**
A: Often credit next invoice vs immediate refund — product choice.

**Q: Annual to monthly?**
A: Complex — defer or treat as plan change with policy table.

### 7.4 Trials

**Q: Trial end charge fail?**
A: Move to PAST_DUE or CANCELED without ever ACTIVE paid — state diagram branch.

**Q: Trial abuse?**
A: Payment method required upfront; fingerprint at PSP — brief mention.

### 7.5 Entitlement coupling

**Q: Strong consistency with playback?**
A: Eventually consistent OK with grace; kill switch cache at edge for suspend.

**Q: Event ordering?**
A: Partition Kafka by member_id; monotonic version on subscription.

### 7.6 Multi-currency

**Q: Member travels?**
A: Billing country on account; doesn't change daily with travel.

**Q: FX rates?**
A: Locked at invoice time from rate table.

### 7.7 Gift cards

**Q: Apply before charge?**
A: Ledger balance applied; charge remainder to PM.

### 7.8 Finance

**Q: Revenue recognition?**
A: Deferred revenue ledger — sibling finance systems consume events.

### 7.9 PSP outage

**Q: Can't charge renewals?**
A: Queue; extend grace; do not mass suspend day one.

### 7.10 Interview traps

**Q: "Use Stripe Billing and done"?**
A: Still need entitlement, dunning policy, global catalog, recon at Netflix scale.

**Q: "Sync call entitlement in charge TX"?**
A: Outbox; decouple failure domains.

**Q: "Double-entry DB in interview"?**
A: Mention append ledger; don't draw T-accounts for 45 min.

### 7.11 Metrics

**Q: Page on what?**
A: duplicate_charge_reports, webhook lag, PENDING > 1h, renewal success drop, idempotency conflict rate anomaly.

### 7.12 Comparison

**Q: vs e-commerce one-time cart?**
A: Recurring state machine + dunning + period anchor — harder lifecycle.

---

## 8. Appendices

### A1. Subscription schema

```text
Subscription {
  subscription_id, member_id,
  plan_id, currency,
  status: TRIAL|ACTIVE|PAST_DUE|SUSPENDED|CANCELED,
  current_period_start, current_period_end,
  cancel_at_period_end: bool,
  payment_method_id,
  version: int  // optimistic lock
}
```

### A2. Charge schema

```text
Charge {
  charge_id, subscription_id,
  idempotency_key UNIQUE,
  amount_cents, currency,
  status: PENDING|SUCCEEDED|FAILED|REFUNDED,
  psp_reference,
  invoice_id,
  created_at
}
```

### A3. Ledger entry

```text
LedgerEntry {
  entry_id, member_id,
  type: CHARGE|REFUND|CREDIT|PRORATION,
  amount_cents, currency,
  charge_id?, invoice_id?,
  immutable_ts
}
```

### A4. Launch checklist

- [ ] Idempotency before PSP in all code paths
- [ ] Webhook signature verification
- [ ] Outbox + entitlement consumer idempotent
- [ ] Renewal spread verified in load test
- [ ] Recon job alerts configured
- [ ] Dunning emails localized
- [ ] 3DS flow E2E tested EU
- [ ] Chargeback suspend policy signed

### A5. Glossary

| Term | Meaning |
|------|---------|
| Dunning | Failed payment retry workflow |
| Proration | Partial period price adjustment |
| PSP | Payment service provider |
| Grace | Streaming allowed while past_due |
| Outbox | Reliable event publish pattern |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| Charge before idempotency | Double bill |
| No webhook path | Stuck states |
| Midnight renewals | Herd |
| Float money | Use cents |
| Netflix stores PAN | PCI scope |

### A7. Reliability test plan

1. Retry renewal API 10× → one charge.
2. Webhook before API response → correct final state.
3. DB fail after PSP success → webhook heals.
4. Concurrent upgrade → one wins via version lock.
5. Dunning success → ACTIVE restored + entitlement.
6. Recon detects orphan PSP charge → alert.

### A8. 60-second summary

> Netflix billing is a **subscription state machine** with **spread renewals**, **PSP token charges**, and an **immutable ledger**. Correctness hinges on **idempotency keys persisted before PSP calls**, **idempotent webhooks**, and **outbox entitlement events**. Failed renewals enter **dunning** with grace streaming; upgrades **prorate immediately**, downgrades at **period end**. Scale by sharding on member_id, separate renewal/dunning/webhook pools, and continuous PSP recon — never by skipping idempotency.

### A9. Related systems map

```text
Billing API → Subscription Service → Payment Orchestrator → PSP
Payment Orchestrator → Ledger Service
Scheduler → Dunning → Payment Orchestrator
PSP Webhooks → Webhook GW → Orchestrator
Outbox → Kafka → Entitlement Service → Playback / CDN auth
Plan Catalog → Subscription Service
Tax Service → Invoice generation
Finance ETL ← Ledger export
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Duplicate charge rate | 0 per idempotent key |
| User upgrade p99 | < 3s |
| Webhook processing lag p99 | < 30s |
| Renewal job completion | 99% within 24h window |
| Billing API availability | 99.9% |

### A11. Worked proration example

```text
Plan Standard $15/mo → Premium $20/mo
Period 30 days; 15 days remain
Credit = 15 × (15/30) = $7.50
Debit  = 15 × (20/30) = $10.00
Due now = $2.50 (250 cents)
```

### A12. Pseudo-SQL

```sql
CREATE TABLE idempotency_keys (
  key TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  response_json JSONB,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE charges (
  charge_id UUID PRIMARY KEY,
  idempotency_key TEXT UNIQUE NOT NULL,
  amount_cents BIGINT NOT NULL,
  status TEXT NOT NULL
);
```

### A13. Ownership

| Concern | Owner |
|---------|-------|
| Billing platform | Commerce Eng |
| Entitlement | Membership |
| PSP relationship | Payments + Finance |
| Dunning policy | Product + Finance |
| Tax | Finance + Vendor |

### A14. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Idempotency, ledger, dunning, webhooks |
| 10× | Renewal spread, sharding plan |
| 100× | Regional cells, webhook scale |
| 1,000× | Event sourcing, multi-PSP |

### A15. Naive vs production

| Naive | Why it fails |
|-------|--------------|
| Cron all at midnight | Outage |
| No idempotency | Double charge |
| Update subscription before PSP | Free access |
| Delete ledger rows | Audit |
| Sync entitlement | Fragile coupling |

### A16. On-call cheat sheet

1. Spike PENDING charges → check PSP status + webhook lag.
2. duplicate_charge tickets → trace idempotency key collisions.
3. Renewal success drop → PSP or PM expiry batch.
4. Entitlement drift → replay outbox events from offset.
5. Stuck dunning → verify worker lease / queue depth.

### A17. Sample entitlement event

```json
{
  "event_id": "evt_01H...",
  "member_id": "m_123",
  "subscription_id": "sub_456",
  "old_status": "PAST_DUE",
  "new_status": "ACTIVE",
  "plan_id": "premium_us",
  "effective_at": "2026-08-06T12:00:00Z"
}
```

### A18. Invoice line items

```text
SUBSCRIPTION_FEE  1599 USD
TAX_VAT           128  USD
PRORATION_CREDIT -250  USD
TOTAL            1477 USD
```

### A19. Cost worksheet

```text
psp_fees_monthly ≈ successful_charges × (0.02 × avg_ticket + 0.30)
support_cost ∝ billing_incidents — invest in idempotency
compute modest vs streaming CDN — still shard for reliability
```

### A20. Explicit non-goals

- Ads billing / CPM invoicing
- In-app purchase Apple/Google bypass flows (mention separate)
- Full ERP replacement
- Real-time fraud graph (use PSP)

---

*End of document — Netflix system design interview prep: Subscription Payment System.*
