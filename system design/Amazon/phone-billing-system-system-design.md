# System Design: Phone Billing System

> **Focus areas:** CDR/usage · Rating · Balances · Invoices · Payments · Disputes · Prepaid/postpaid · Mediation · Month-end
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Telecom billing / rating & invoicing platform**

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

Goal: design a **phone billing system**—mediate usage (voice/SMS/data), rate against plans, maintain balances, invoice postpaid, enforce prepaid, take payments, handle disputes—at progressive subscriber scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Mediation, rating, billing, invoicing | RAN/core network engineering |
| Money | Subscriber balances & invoices | Bank card issuer rewards |
| Plans | Catalog of tariffs | Retail handset ecommerce |
| Amazon lens | Money correctness, month-end ownership | UI-only bill presentment |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Usage? | CDRs / data sessions / SMS events | Mediation |
| F2 | Rating? | Plans, tiers, buckets, roaming | Rating engine |
| F3 | Prepaid? | Real-time balance check/debit | OCS-like hooks |
| F4 | Postpaid? | Cycle aggregate → invoice | Billing run |
| F5 | Taxes? | Jurisdiction tax lines | Tax adapter |
| F6 | Payments? | Card/ACH/carrier wallet | Payments |
| F7 | Disputes? | Adjustments with authority | Adjustment workflow |
| F8 | Proration? | Plan changes mid-cycle | Proration rules |
| F9 | Roaming? | Partner tap files | Roaming mediation |
| F10 | Notifications? | Overage, bill ready | Notify |
| F11 | Dunning? | Past-due collections | Dunning state |
| F12 | SLA? | Invoice correctness; prepaid auth latency | SLOs |

**MVP scope:**

1. Ingest usage events idempotently.
2. Rate to charge records.
3. Prepaid balance reserve/debit.
4. Postpaid cycle invoice generation.
5. Payment apply to invoice.
6. Basic adjustments.
7. Customer bill presentment API.
8. Ops: unbilled usage & drift monitors.

**Out of MVP:** full 5G network functions, worldwide roaming settlement politics, ML fraud complete suite, active-active dual balance writers.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Prepaid auth | p99 < 50–100ms |
| N2 | Mediation lag | minutes typically |
| N3 | Invoice correctness | cents; auditable |
| N4 | Idempotency | Dup CDRs safe |
| N5 | Month-end | Finish window reliably |
| N6 | Durability | No lost charge records |
| N7 | Peak | New Year / concerts data spikes |
| N8 | Consistency | Strong per subscriber balance/bill |

### 1.3 Cases

**Happy:** Usage→rate→aggregate→invoice→pay→zero balance.
**Edges:** dup CDR; late roaming tap; prepaid race; plan change mid-cycle; tax jurisdiction; dispute after pay; partial pay; billing rerun; timezone cycle boundary.

| Case | Behavior |
|------|----------|
| Dup CDR | Idempotency key |
| Prepaid concurrent | Atomic reserve |
| Late tap | Rerate/bill next or adjustment policy |
| Plan change | Proration version pin |
| Payment unknown | Reconcile |
| Invoice rerun | Idempotent bill version |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Subscribers | 1M | 10M | 100M | 1B |
| Usage events / day | 50M | 500M | 5B | 50B |
| Rate QPS peak | 2K | 20K | 200K | 2M |
| Invoices / month | 1M | 10M | 100M | 1B |
| Prepaid auths / s | 500 | 5K | 50K | 500K |
| Adjustments / day | 5K | 50K | 500K | 5M |
| Plans | 50 | 200 | 500 | 1K |
| Regions | 1 | 2 | 5 | 10 |

**Jumps:** 10×=sharding; 100×=real-time prepaid+roaming; 1,000×=global multi-brand BSS cells.

### 1.5 Scope repeat-back

> Billing domain: mediate usage, rate, balances, invoices, payments, adjustments—money-correct under peak—not the radio network.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
50M events/day ≈ 600/s; peaks 10×
Prepaid auths may be higher than CDRs
```

### 2.2 Storage

```text
CDR hot→warm→cold tiers
Charge records & invoices retained years
```

### 2.3 Latency

```text
Prepaid path: cache balances + atomic debit local shard
```

### 2.4 Bottlenecks

(1) hot subscriber (2) month-end fanout (3) roaming late files (4) tax calls (5) rerates.

### 2.5 Cost

Store raw CDRs tiered; aggregate early; frugal reprocessing.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Mediation | Normalize/dedupe usage | Idempotent |
| Rating | Usage→charges | Deterministic versioned |
| Balance/OCS | Prepaid reserves | Strong per sub |
| Billing/Invoice | Cycle statements | Strong per bill |
| Payments/Dunning | Cash application | Idempotent |

**Deal-breaker:** non-deterministic rating or non-idempotent CDR apply—unbillable chaos.

### 3.2 Components

1. **Mediation Service** — ingest/validate/dedupe
2. **Rating Engine** — plans/tariffs
3. **Balance Service** — prepaid/postpaid buckets
4. **Billing Scheduler** — cycle runs
5. **Invoice Service** — presentment+PDF
6. **Tax Adapter** — jurisdiction
7. **Payments Adapter** — apply cash
8. **Adjustments** — disputes
9. **Dunning** — collections
10. **Roaming Ingest** — TAP/RAP-like
11. **Customer Bill API** — UX
12. **Ops Reconcile** — drift tools

### 3.3 Core API (sketch)

```text
POST /v1/usage/events {event_id, msisdn, type, qty, ts, meta}
POST /v1/prepaid/authorize {sub_id, qty, service} → reservation
POST /v1/billing/runs {cycle_id}
GET /v1/invoices/{id}
POST /v1/payments {invoice_id, amount, idem_key}
POST /v1/adjustments
```

### 3.4 State machine

```text
USAGE: RECEIVED → RATED → BILLED
RESERVE: OPEN → COMMITTED / RELEASED
INVOICE: DRAFT → ISSUED → PARTIALLY_PAID → PAID / IN_DISPUTE / WRITTEN_OFF
SUB: ACTIVE → PAST_DUE → BARRED → ACTIVE
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Realtime vs batch rate | Hybrid: prepaid realtime; postpaid microbatch | Scale |
| Balance store | Sharded strong store | Latency |
| Invoice immutability | Issued immutable; credit notes | Audit |
| Rerate | Guided windows not infinite | Cost |
| Tax sync | Adapter with cache | Deps |

---

## 4. Architecture Diagram

```text
[Network/CDF] -> Mediation -> Rating Engine -> Charge Records
                     |                |
                     v                v
              Prepaid Balance     Billing Aggregator -> Invoices
                     |                |
                     +------ Payments/Dunning/Adjustments
```

### 4.1 Primary sequence

```text
Dedupe usage event_id
Lookup plan version at event ts
Rate → charge record
Prepaid: reserve/commit buckets
Cycle: aggregate unbilled → DRAFT invoice → tax → ISSUE
Payment applies; dunning if late
```

### 4.2 Isolation cell

```text
Shard by subscriber_id hash
Brand/region billing cells
Roaming files processed in region
No cross-sub synchronous locks
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Idempotent usage apply.
2. Rating deterministic given plan version+event.
3. Issued invoices immutable; adjustments via credit/debit notes.
4. Prepaid cannot go negative without policy credit.
5. Payment idempotent.
6. Cycle boundaries explicit TZ.
7. Every money change has reason/source.
8. Rerate produces auditable deltas.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Batch rate nightly OK small |
| 10× | Stream mediation; shard balances |
| 100× | Realtime prepaid; roaming; month-end parallelism |
| 1000× | Multi-brand global cells; extreme event spikes |

### 5.3 Maintainability

- Tariff as versioned data with golden tests.
- Canary plan on cohort.
- Billing run dry-run.
- CDR replay tools.
- Month-end game days.

### 5.4 Progressive scale

**1×:** Simple postpaid + batch.
**10×:** Prepaid+shards.
**100×:** Roaming+complex tiers.
**1000×:** Global brands; huge mediation.

### 5.6 Mediation dedupe

Network retries. Keys: event_id or (node, call_id, seq). Late duplicates after bill → adjustment path not silent second charge.

### 5.7 Prepaid reserve

Authorize reserves qty/money with TTL; commit on success usage; release on fail. CAS balance.

### 5.8 Month-end parallelism

Partition subscribers; ISSUED invoices immutable; checkpoint runs; rerun safe.

### 5.9 Plan version pin

Event rated with plan effective at ts; changes create new version; proration explicit.

### 5.10 Roaming late taps

Hold estimated; finalize on TAP; or bill estimate+true-up—policy product decision.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Non-idempotent CDRs | Double bill |
| Mutable issued invoices | Audit fail |
| Float rating | Cents drift |
| Dual-active balance writers | Split brain |
| Infinite silent rerate | Support chaos |
| Prepaid best-effort negative | Revenue leakage |

---

## 6. Wrap-Up

### 6.1 Designed

Subscriber-sharded billing: mediation, deterministic rating, prepaid balances, immutable invoices, payments, adjustments—month-end safe.

### 6.2 Decisions to defend

1. Idempotent mediation
2. Versioned tariffs
3. Strong prepaid CAS
4. Immutable invoices + credit notes
5. Shard by sub
6. Hybrid realtime/batch
7. Explicit proration
8. Month-end checkpoints

### 6.3 Risks

- Late roaming
- Tariff misconfig
- Month-end overrun
- Tax adapter outage
- Hot celebrity MSISDN

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope billing vs network |
| 5–15 | Mediation+rating |
| 15–25 | Prepaid balances |
| 25–35 | Invoices+pay+adjust |
| 35–45 | Scale/month-end/roaming |

### 6.5 Closer

> **Phone Billing System**: idempotent mediation, deterministic rating, strong prepaid, immutable invoices, progressive subscriber scale, calm month-ends.

---

## 7. Deeper / Related Interview Questions

### 7.1 Mediation

**Q: Incomplete sessions?**
A: Interim CDRs + final; rating policy.

**Q: Clock skew nodes?**
A: Accept skew bound; bill by event ts rules.

### 7.2 Rating

**Q: Unlimited plans?**
A: Still mediate for fair use thresholds.

**Q: Family buckets?**
A: Shared balance accounts.

**Q: Zero-rate content?**
A: Special rating groups.

### 7.3 Prepaid

**Q: What if balance service down?**
A: Fail closed for paid services; emergency dial policy.

**Q: Thundering herd top-ups?**
A: Shard+queue.

### 7.4 Invoices

**Q: PDF generation?**
A: Async; store object.

**Q: Rebill?**
A: Credit note + new invoice.

**Q: Multi-line accounts?**
A: Account hierarchy.

### 7.5 Disputes

**Q: Goodwill credit?**
A: Authority limits.

**Q: Fraud usage?**
A: Risk + adjust.

### 7.6 Traps

**Q: Build HLR/AUC**
A: Scope

**Q: Mutable bills**
A: Fail

**Q: Float**
A: Fail

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| Unbilled usage age | Leakage risk |
| Prepaid auth p99 | UX/network |
| Invoice error rate | Quality |
| Dupe suppress count | Mediation health |
| Month-end duration | Ops |
| Payment apply lag | Cash |
| Adjustment volume | Process |
| Rerate volume | Stability |

### 7.8 Ownership

**Q: Who pages for double billing?**
A: Rating/Mediation IC.

**Q: Who pages for month-end stuck?**
A: Billing Run IC + finance liaison.

### 7.9 Progressive drill

**10×:** stream+shard
**100×:** prepaid realtime+roaming
**1,000×:** global multi-brand month-end

---

## 8. Appendices

### 8.1 Schema sketches

```text
subscribers(sub_id, account_id, plan_version, msisdn)
usage_events(event_id PK, sub_id, type, qty, ts, meta)
charge_records(charge_id, event_id, amount_cents, plan_version, state)
balances(sub_id, bucket_id, amount, version)
reservations(res_id, sub_id, amount, exp, state)
invoices(invoice_id, account_id, cycle_id, state, total_cents, version)
invoice_lines(...)
payments(pay_id, invoice_id, amount, idem_key UNIQUE)
adjustments(adj_id, reason, amount, authority)
plan_versions(plan_id, version, tariff_json, effective_from)
```

### 8.2 API checklist

- [ ] Usage ingest
- [ ] Prepaid auth/commit
- [ ] Billing run
- [ ] Invoice get
- [ ] Payment
- [ ] Adjustment
- [ ] Plan change

### 8.3 Oncall checklist

- [ ] Unbilled backlog
- [ ] Prepaid latency/errors
- [ ] Billing run lag
- [ ] Payment reconcile
- [ ] Tariff canary
- [ ] Roaming file late
- [ ] Drift reconcile

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| CDR | Call Detail Record |
| Mediation | Normalize/dedupe usage |
| Rating | Price usage |
| OCS | Online charging system |
| TAP | Roaming transfer file |
| Dunning | Collections process |
| Credit note | Invoice reverse doc |

### 8.5 Deal-breaker one-liners

- Dup CDRs bill twice
- Edit issued invoice in place
- Float money
- Best-effort prepaid

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Mediation | Usage Platform |
| Rating | Billing Eng |
| Balances | OCS/Balance |
| Invoices | Billing Ops Eng |
| Payments | Cash App |
| Roaming | Wholesale |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | Batch PG |
| 10× | Kafka+shards |
| 100× | Realtime balance cluster |
| 1000× | Regional BSS cells |

### 8.8 Failure injection

1. Dup CDR — dedupe.
2. Balance CAS fail — retry.
3. Tax down — queue issue with policy.
4. Billing crash — resume checkpoint.
5. Pay timeout — reconcile.
6. Bad tariff — pause plan version.

---

## Interview Traps

**Trap: Design cell towers**
Signal: Scope

**Trap: Skip idempotency**
Signal: Fail

**Trap: Rerate forever online**
Signal: Cost

**Trap: Global lock all subs**
Signal: No scale

---

## Flash Cards

### Card 1: Idempotent CDR

event_id.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Usage Platform

### Card 2: Plan version pin

Deterministic.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Billing Eng

### Card 3: Prepaid CAS

Reserve/commit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** OCS

### Card 4: Invoice immutable

Credit notes.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Billing Ops

### Card 5: Month-end checkpoint

Restartable.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Cash

### Card 6: Proration rules

Explicit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Wholesale

### Card 7: Late roaming

True-up policy.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Usage Platform

### Card 8: Payment idempotent

Keys.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Billing Eng

### Card 9: Unbilled age SLO

Leakage.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** OCS

### Card 10: Shard by sub

Scale.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Billing Ops

### Card 11: Tariff tests

Golden CDR fixtures.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Cash

### Card 12: Dunning states

Lifecycle.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Wholesale

### Card 13: Fail closed prepaid

When down.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Usage Platform

### Card 14: Deal-breaker

Double bill; mutable invoice.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Billing Eng

### Card 15: Metrics

Unbilled age; auth p99.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** OCS

### Card 16: NYE spike

Pre-scale.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Billing Ops

---

## Scenario Runbooks

### R1 — Double bill reports
Freeze rating for segment; credit notes; fix dedupe.

### R2 — Prepaid outage
Fail closed; emergency voice; restore balances.

### R3 — Month-end overrun
Parallelize remaining partitions; delay presentment messaging.

### R4 — Roaming file late
Estimate policy; true-up later.

### R5 — Bad tariff canary
Rollback version; rerate window dry-run.

---

## Extended Rapid Q&A

**Q: SMS vs data rating?**
A: Different unit types in tariff.

**Q: Family plan?**
A: Shared buckets on account.

**Q: Number portability?**
A: Sub identity ≠ MSISDN forever.

**Q: eSIM churn?**
A: Account continuity.

**Q: Bill shock?**
A: Threshold notifies+caps.

**Q: Why credit note?**
A: Immutability/audit.

**Q: First widget?**
A: Unbilled age + prepaid errors.

**Q: MVNO?**
A: Same planes; wholesale configs.

**Q: Taxes inclusive?**
A: Product/tax engine rules.

**Q: Offline charging only?**
A: Possible MVP; prepaid needs online.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Excel billing | No |
| Mutable invoices | Audit fail |
| Single global balance DB | Hotspot |
| No mediation dedupe | Double charge |
| Rate in network elements only | Inflexible |

---

## LLD Touch (optional)

Classes: `UsageEvent`, `PlanVersion`, `ChargeRecord`, `BalanceBucket`, `Reservation`, `Invoice`, `CreditNote`, `Payment`, `Adjustment`. Patterns: Idempotent consumers, CAS balances, Versioned tariffs, Checkpointed batch, Immutable documents + compensating notes.

---

## 60-second Narrative

"We mediate usage idempotently, rate with versioned tariffs, and keep strong prepaid balances with reserve/commit. Postpaid cycles produce immutable invoices; mistakes become credit notes. Payments and adjustments are audited. Scale by subscriber shards and practice month-end. Success is cents-correct bills, fast prepaid auths, and no surprise double charges."

---

## Extra Depth: Fair Use

Threshold counters; notify; throttle hooks to network policy.

## Extra Depth: Partner Settlement

Wholesale separate from retail invoice.

## Extra Depth: Bill Presentment

PDF+itemization from issued snapshot.

## Extra Depth: Game Day Month-End

Inject late CDRs; crash mid-run; prove resume.

## Extra Depth: Observability

Wide events; protect MSISDN cardinality.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How do family shared data buckets debit?**
A: Account-level bucket with member charge attribution.

**Q: What is a credit note vs adjustment?**
A: Credit note ties to issued invoice immutability; adjustment may be pre-issue.

**Q: Number portability identity?**
A: sub_id stable; MSISDN history table.

**Q: How bill zero-rated content partners?**
A: Rating groups; wholesale settlement separate.

**Q: Prepaid loan / emergency credit?**
A: Policy bucket with recovery rules.

**Q: Why fail closed on prepaid auth outage?**
A: Revenue + fairness; emergency numbers exception.

**Q: Multi-cycle backlog unbilled?**
A: SLO on unbilled age; escalate leakage.

**Q: Tax inclusive vs exclusive plans?**
A: Tax adapter + product flags.

**Q: Dunning bar data but allow voice?**
A: Service policy matrix to network PCRF/PCF hooks.

**Q: How test tariff change?**
A: Golden CDR fixtures; canary cohort.

**Q: MVNO billing separation?**
A: Wholesale invoice distinct from retail presentment.

**Q: Partial payment application order?**
A: FIFO invoices or policy; documented.

**Q: Rerate storm after bug?**
A: Windowed; customer messaging; credit notes.

**Q: Clock at month boundary TZ?**
A: Account billing TZ explicit.

**Q: SEV for mass wrong invoices?**
A: Halt presentment; credit notes; Billing IC + finance.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT charges | Charge records+invoices |
| Prepaid | CAS reserve |
| Kill | Dup bill; mutable invoice |

---

*End of Phone Billing System design notes (Amazon SDE III prep).*


---

## Extra Depth Pack (Interview Expansion)

### E1: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E2: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E3: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E4: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E5: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E6: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

### E7: Drill scenario

**Setup:** At a progressive scale jump, a rare failure becomes frequent.

**Symptoms:** Latency, backlog, inconsistency, or customer-visible errors rise.

**Diagnosis steps:**
1. Check golden signals for the owning plane.
2. Confirm idempotency / dedupe keys are working.
3. Verify cell isolation has not been violated.
4. Correlate with last config/deploy; roll back if needed.

**Mitigation:** Shed load, freeze risky features, staff exception queues, communicate SLA risk.

**Prevention:** Game-day inject this scenario; add metric + runbook; clear ownership.

**10× note:** Platformize the fix; **100×:** automate detection; **1,000×:** multi-cell command center.

