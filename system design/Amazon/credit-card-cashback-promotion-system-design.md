# System Design: Credit-Card Cashback Promotion System

> **Focus areas:** Card transactions · Offer eligibility · Accrual ledger · Caps · Fraud · Settlement · Statements · Progressive campaigns
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Card rewards / cashback promotions engine at issuer scale**

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

Goal: design a **credit-card cashback promotion system**—evaluate card transactions against offers, accrue cashback correctly with caps/tiers, expose balances, settle to statement/credit, and prevent abuse—at progressive campaign and transaction scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Rewards eligibility + accrual + settlement | Full card authorizing network / VisaNet |
| Ledger | Cashback balances & entries | Core bank ledger replacement |
| Offers | Campaign rules engine | Entire marketing cloud |
| Amazon lens | Correct money, audit, ownership | Coupon toy demo |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Txn ingest? | Authorized/cleared/settled events | Idempotent ingest |
| F2 | Offers? | Category %, merchant, MCC, time-bound, new-card | Rules engine |
| F3 | Caps? | Monthly/category/global caps | Cap counters |
| F4 | Accrual? | Cashback amount ledger entries | Rewards ledger |
| F5 | Pending vs posted? | Auth pending; clear posts | State machine |
| F6 | Redemption? | Statement credit / deposit | Settlement jobs |
| F7 | Returns? | Clawback cashback | Reversal entries |
| F8 | Stacking? | Explicit offer priority | Conflict policy |
| F9 | Fraud/abuse? | Manufactured spend signals | Risk hooks |
| F10 | Customer view? | YTD, pending, offer progress | Read models |
| F11 | Multi-product? | Many card products | Product configs |
| F12 | SLA? | Accrual freshness hours; statement correctness | Money SLOs |

**MVP scope:**

1. Ingest cleared txns idempotently.
2. Offer config with eligibility.
3. Evaluate + accrue ledger entries.
4. Enforce caps atomically.
5. Handle returns/reversals.
6. Customer balance API.
7. Statement credit settlement batch.
8. Ops: accrual drift monitors.

**Out of MVP:** real-time crypto rewards, full AML suite rebuild, personalized RL offers v1, active-active dual writers same ledger account.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Eval latency | p99 < 100–300ms online path or async < few min |
| N2 | Correctness | Cents-accurate; auditable |
| N3 | Idempotency | Duplicate txn events safe |
| N4 | Durability | No lost accruals |
| N5 | Peak | Holiday spend 5–10× |
| N6 | Audit | Explain why earned/not |
| N7 | Consistency | Strong per card rewards account |
| N8 | Cap integrity | Never exceed caps silently |

### 1.3 Cases

**Happy:** Clear txn→match offer→accrue→show pending→post→statement credit.
**Edges:** auth then clear different amount; return; MCC miscategorization; cap boundary race; duplicate events; offer overlap; fraud manufactured spend; late interchange; timezone month boundary.

| Case | Behavior |
|------|----------|
| Duplicate event | Idempotency key txn_id+type |
| Return | Negative accrual / clawback |
| Cap race | Atomic cap reservation |
| Auth≠clear | Finalize on clear; adjust |
| Offer overlap | Deterministic priority |
| Mis-MCC | Exception + manual adjust rare |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Cards | 1M | 10M | 100M | 1B |
| Txns / day | 5M | 50M | 500M | 5B |
| Offers active | 50 | 200 | 1K | 5K |
| Accrual events / day | 3M | 30M | 300M | 3B |
| Eval QPS peak | 1K | 10K | 100K | 1M |
| Settlements / month | 1M | 10M | 100M | 1B |
| Products | 5 | 20 | 50 | 100 |
| Regions | 1 | 2 | 4 | 8 |

**Jumps:** 10×=platformization; 100×=streaming eval + shard ledgers; 1,000×=global products, extreme holiday, complex offer graph.

### 1.5 Scope repeat-back

> Rewards accrual platform: idempotent txn evaluation, deterministic offers/caps, cashback ledger, reversals, settlement—money-correct under peak—not the payment network itself.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
5M txn/day ≈ 60/s avg; peak 10×
Each txn may touch multiple offers but posts few ledger lines
```

### 2.2 Storage

```text
Ledger entries ~100–300B each; billions/year at scale
Hot balances per card; cold entry history
```

### 2.3 Latency

```text
Async eval OK if customer sees pending soon; statement path batch
Online quote 'will this earn?' optional cache
```

### 2.4 Bottlenecks

(1) cap hot keys (2) offer explosion (3) reprocessing storms (4) month-end settlement (5) explainability store.

### 2.5 Cost

Reprocessing all history is expensive; design replay carefully; frugal storage tiers.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Txn Ingest | Canonical spend events | Idempotent |
| Offer Config | Rules/versions | Versioned publish |
| Eval | Eligibility decisions | Deterministic |
| Rewards Ledger | Balances/entries | Strong per account |
| Settlement | Statement credits | Exactly-once-ish jobs |

**Deal-breaker:** mutating balances without ledger entries / losing idempotency—money bugs.

### 3.2 Components

1. **Txn Ingest** — normalize auth/clear/return
2. **Offer Manager** — CRUD + version
3. **Eligibility Engine** — rules exec
4. **Cap Service** — period counters
5. **Rewards Ledger** — accounts/entries
6. **Explain Store** — decision traces
7. **Settlement Worker** — credits
8. **Customer Read API** — balances/progress
9. **Risk Hooks** — abuse
10. **Reprocess/Replay** — controlled
11. **Ops Console** — campaign health
12. **Product Config** — card SKUs

### 3.3 Core API (sketch)

```text
POST /v1/txns/events {event_id, card_id, amount, mcc, merchant, type, ts}
POST /v1/offers  (admin)
GET /v1/cards/{id}/rewards
GET /v1/cards/{id}/txns/{txn_id}/explanation
POST /v1/settlements/run {period}
```

### 3.4 State machine

```text
ACCRUAL: PENDING (auth) → POSTED (clear) → SETTLED
           PENDING → VOID
           POSTED → CLAWED_BACK (return)
OFFER: DRAFT → LIVE → PAUSED → ENDED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Sync vs async eval | Async post-clear + fast read model | Scale |
| Rules DSL vs code | DSL/config for marketers | Speed vs safety |
| Cap store | Per card+period atomic counters | Hot keys |
| Explain every txn | Sample + on-demand recompute | Cost |
| Stacking | Priority list not additive free-for-all | Margin |

---

## 4. Architecture Diagram

```text
[Card Processor Events] -> Ingest -> Eligibility Engine -> Cap Service
                                         |
                                         v
                                   Rewards Ledger -> Read Models
                                         |
                                   Settlement -> Statement Credit
 Offer Manager --------versioned--------^
```

### 4.1 Primary sequence

```text
Dedupe event_id
Load LIVE offers for product/time
Match MCC/merchant/category rules
Reserve cap capacity atomically
Write ledger entry PENDING/POSTED
Update read model
Settlement job sums POSTED→credit
```

### 4.2 Isolation cell

```text
Shard rewards accounts by card_id/hash
Campaign config global versioned
Region cells for data residency
No cross-card synchronous locks
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Ledger entry per accrual/clawback; balance = sum.
2. Idempotent event_id processing.
3. Caps never exceeded beyond epsilon with reservation.
4. Offer version pinned on decision.
5. Returns clawback ≤ original accrual.
6. Settlement idempotent period keys.
7. Explainability reconstructable.
8. Money adjustments require authority reason codes.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Batch nightly eval OK |
| 10× | Streaming eval; sharded PG |
| 100× | Ledger partitions; cap service; DSL sandbox |
| 1000× | Global residency; complex campaigns; holiday CC |

### 5.3 Maintainability

- Offer DSL with test fixtures.
- Canary offers on % cards.
- Replay tool with dry-run.
- Schema evolution for ledger.
- Month-end rehearsals.

### 5.4 Progressive scale

**1×:** Simple % categories nightly.
**10×:** Multiple offers+caps streaming.
**100×:** Merchant lists, tiers, partner funded.
**1000×:** Global products, real-time UX, sophisticated abuse.

### 5.6 Cap reservation

Increment cap_used with CAS where used+amt<=cap; on failure partial earn or zero per policy. Hot categories (gas) shard by card.

### 5.7 Auth vs clear

Optional pending accrual on auth; finalize/adjust on clear; void on auth expire.

### 5.8 Deterministic stacking

Sort offers by priority/specificity; apply until policy stops; never random.

### 5.9 Reprocess storms

Versioned offers; rebuild by time windows; rate-limit replay; dual-run compare.

### 5.10 Partner-funded offers

Separate liability accounts; settlement to partners; audit.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Balance field without ledger | Unexplainable money |
| Non-idempotent ingest | Double earn |
| Silent cap breach | Margin loss |
| Random offer pick | Customer support hell |
| Active-active dual ledger writers | Split brain |
| Irreversible settle without reverse path | Broken returns |

---

## 6. Wrap-Up

### 6.1 Designed

Cashback promotions: idempotent txn ingest, versioned offers, deterministic eligibility, atomic caps, rewards ledger, clawbacks, settlement—money-correct.

### 6.2 Decisions to defend

1. Ledger+entries SoT
2. Idempotent events
3. Atomic caps
4. Offer version pin
5. Deterministic stack
6. Async eval OK
7. Settlement idempotency
8. Explain reconstruct

### 6.3 Risks

- MCC data quality
- Hot cap keys
- Offer misconfig
- Reprocess cost
- Abuse manufactured spend

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope rewards vs network |
| 5–15 | Ledger+idempotent ingest |
| 15–25 | Offers+caps |
| 25–35 | Returns+settlement |
| 35–45 | Scale/abuse/ops |

### 6.5 Closer

> **Credit-Card Cashback Promotion System**: ledger-first cashback, deterministic offers and caps, idempotent ingest, safe settlement, progressive campaign scale, cents-level ownership.

---

## 7. Deeper / Related Interview Questions

### 7.1 Ledger

**Q: Why entries not just balance?**
A: Audit/idempotency/rebuild.

**Q: Multi-currency?**
A: Account currency; FX policy.

**Q: Pending show to user?**
A: Yes with clear labeling.

### 7.2 Offers

**Q: MCC lists huge?**
A: Sets/indexes; merchant IDs.

**Q: New card 5% 3 months?**
A: Eligibility window on product open date.

**Q: Bonus thresholds?**
A: Progress counters separate from caps.

### 7.3 Caps

**Q: Month timezone?**
A: Card product TZ or UTC policy explicit.

**Q: Race two txns?**
A: Atomic reservation.

**Q: Lifetime cap?**
A: Counter without period reset.

### 7.4 Returns

**Q: Partial return?**
A: Proportional clawback.

**Q: After settlement?**
A: Negative adjust next period / receivable.

### 7.5 Abuse

**Q: Manufactured spend?**
A: Risk scores; merchant blocks; velocity.

**Q: Collusive merchants?**
A: Partner monitoring.

### 7.6 Traps

**Q: Eval in card auth critical path always**
A: Latency risk—async OK.

**Q: Float money math**
A: Use decimal/cents.

**Q: Marketer edits LIVE SQL**
A: Need versioned publish.

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| Accrual lag | Freshness |
| Cap breach attempts | Integrity |
| Explain mismatch rate | Quality |
| Settlement fail | Money ops |
| Double-earn detects | Idempotency |
| Offer attach rate | Biz |
| Clawback lag | Returns |
| Reprocess drift | Correctness |

### 7.8 Ownership

**Q: Who pages for double cashback?**
A: Rewards Ledger IC.

**Q: Who pages for wrong offer attach?**
A: Offers + Eval; marketing liaison.

### 7.9 Progressive drill

**10×:** streaming+shards
**100×:** cap service+DSL
**1,000×:** global holiday+residency

---

## 8. Appendices

### 8.1 Schema sketches

```text
cards(card_id, product_id, opened_ts)
txn_events(event_id PK, card_id, type, amount_cents, mcc, merchant_id, ts)
offers(offer_id, version, rules_json, priority, state)
cap_counters(card_id, offer_id, period, used_cents, version)
ledger_accounts(account_id, card_id, currency)
ledger_entries(entry_id PK, account_id, txn_event_id, offer_version, amount_cents, state)
settlements(id, period, account_id, amount, idem_key UNIQUE)
decision_traces(txn_event_id, offer_id, result, reasons_json)
```

### 8.2 API checklist

- [ ] Txn event ingest
- [ ] Offer publish
- [ ] Balance get
- [ ] Explanation get
- [ ] Settlement run
- [ ] Manual adjust
- [ ] Reprocess dry-run

### 8.3 Oncall checklist

- [ ] Double-earn alerts
- [ ] Cap CAS fails spike
- [ ] Settlement job
- [ ] Eval lag
- [ ] Offer publish bad canary
- [ ] Risk blocks
- [ ] Drift reconciler

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| MCC | Merchant Category Code |
| Accrual | Earned rewards entry |
| Clawback | Reverse earn |
| Cap | Earn limit |
| Statement credit | Apply to card balance |
| DSL | Offer rules language |

### 8.5 Deal-breaker one-liners

- Non-idempotent earn
- Balance-only SoT
- Random stacking
- Float for money
- Dual-active ledger writers

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Ledger | Rewards Platform |
| Offers | Rewards Product Eng |
| Caps | Rewards Platform |
| Settlement | Money Movement |
| Risk | Abuse |
| Ingest | Card Data Platform |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | Nightly batch PG |
| 10× | Kafka+workers |
| 100× | Sharded ledger+cap |
| 1000× | Regional cells |

### 8.8 Failure injection

1. Dup event — dedupe.
2. Cap CAS fail — policy earn.
3. Bad offer canary — pause.
4. Settlement partial — resume idempotent.
5. Return after settle — adjust.
6. Reprocess drift — halt+compare.

---

## Interview Traps

**Trap: Build VisaNet**
Signal: Scope

**Trap: Ignore cents math**
Signal: Fail

**Trap: Sync auth path only**
Signal: Brittle

**Trap: No clawback story**
Signal: Incomplete

---

## Flash Cards

### Card 1: Ledger entries

SoT money.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Rewards Platform

### Card 2: Idempotent ingest

event_id.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Offers

### Card 3: Cap CAS

No silent breach.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Settlement

### Card 4: Offer version pin

Explainable.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Risk

### Card 5: Stack priority

Deterministic.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Card Data

### Card 6: Auth/clear

Adjust path.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Rewards Platform

### Card 7: Clawback

Returns.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Offers

### Card 8: Settlement idempotent

period keys.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Settlement

### Card 9: Explain store

Support.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Risk

### Card 10: Async eval

Scale.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Card Data

### Card 11: Canary offer

% cards.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Rewards Platform

### Card 12: Abuse hooks

Manufactured spend.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Offers

### Card 13: Decimal/cents

No float.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Settlement

### Card 14: Deal-breaker

Double earn.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Risk

### Card 15: Metrics

Drift; lag.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Card Data

### Card 16: Holiday

Pre-scale partitions.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Rewards Platform

---

## Scenario Runbooks

### R1 — Double earn spike
Pause eval; dedupe fix; clawback tool.

### R2 — Cap breach
Freeze offer; patch CAS; notify finance.

### R3 — Settlement fail
Stop credits; repair; rerun idempotent.

### R4 — Bad offer live
Pause offer version; reprocess window dry-run.

### R5 — Ingest lag
Scale workers; backlog SLO; customer messaging if needed.

---

## Extended Rapid Q&A

**Q: Points vs cash?**
A: Same ledger different unit/product.

**Q: Foreign txn?**
A: FX + MCC local rules.

**Q: Family cards?**
A: Household caps optional.

**Q: Statement timing?**
A: Batch calendar.

**Q: Why DSL sandbox?**
A: Prevent marketer outage.

**Q: Partner funded?**
A: Liability split accounts.

**Q: First widget?**
A: Drift+lag.

**Q: Manual goodwill adjust?**
A: Authority+reason.

**Q: Year boundary?**
A: Period keys explicit.

**Q: Offline merchant delayed clear?**
A: Finalize on clear.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Update balance in place only | No audit |
| Eval non-deterministically | Support hell |
| Recompute all forever online | Cost |
| Store rules in app code only | Slow marketing |
| Ignore returns | Margin leak / customer debt |

---

## LLD Touch (optional)

Classes: `TxnEvent`, `OfferVersion`, `EligibilityDecision`, `CapCounter`, `LedgerAccount`, `LedgerEntry`, `SettlementBatch`, `Adjustment`. Patterns: Idempotent consumer, CAS counters, Event-sourced lite ledger, Versioned config, Outbox to read models.

---

## 60-second Narrative

"We ingest card events idempotently, evaluate versioned offers deterministically, reserve caps atomically, and write a rewards ledger that can be explained and rebuilt. Returns claw back; settlements are idempotent. Scale by sharding accounts and streaming eval—never by weakening money invariants. Success is cents-correct cashback, clear explanations, and quiet month-ends."

---

## Extra Depth: Offer DSL Safety

Static analysis; fixture tests; max complexity budgets.

## Extra Depth: Read Models

Materialize YTD/category progress; rebuildable.

## Extra Depth: Finance Reconcile

Compare ledger vs statement credits daily.

## Extra Depth: Privacy

Minimize merchant PII in traces; retain policy.

## Extra Depth: Game Day Month-End

Rehearse settlement; inject dup events.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How handle statement credit vs deposit redemption?**
A: Product config; settlement worker different rails; same ledger.

**Q: What about disputed original card txn?**
A: Chargeback events clawback rewards if policy says.

**Q: Merchant allowlist offers at scale?**
A: Sharded sets / Bloom+exact; versioned lists.

**Q: How prevent marketer from publishing broken DSL?**
A: Sandbox + fixtures + canary % + auto-pause on anomaly.

**Q: YTD display vs ledger?**
A: Read model; rebuild from entries if drift.

**Q: Household / authorized user caps?**
A: Cap key includes household_id when configured.

**Q: Foreign MCC mapping quality?**
A: Partner data SLAs; exception queues.

**Q: Why pin offer version on entry?**
A: Explainability months later.

**Q: Accelerator tiers (1% then 5% after $X)?**
A: Progress counters + threshold rules.

**Q: Partner-funded liability miss?**
A: Finance reconcile daily; alert.

**Q: Rounding 0.5 cents?**
A: Banker's or always-down policy documented; integer math.

**Q: Real-time 'will I earn?' API?**
A: Cache eligibility; not always final until clear.

**Q: Reprocess last 90 days cost control?**
A: Windowed; rate-limited; dual-run compare.

**Q: Privacy of merchant names in traces?**
A: Minimize; retain policy; support tooling access audited.

**Q: SEV for mass over-earn?**
A: Freeze offer; clawback tool; finance+rewards IC.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT | Rewards ledger |
| Caps | Atomic reserve |
| Eval | Deterministic versions |
| Kill | Double earn; float math |

---

*End of Credit-Card Cashback Promotion System design notes (Amazon SDE III prep).*


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

