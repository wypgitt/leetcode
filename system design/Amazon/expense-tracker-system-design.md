# System Design: Expense Tracker System

> **Focus areas:** Expenses · Categories · Receipts · Budgets · Shared wallets · FX · Reports · Bank import · Idempotency
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Personal/household & SMB expense tracking platform**

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

Goal: design an **expense tracker**—capture expenses (manual, receipt OCR, bank import), categorize, budget, share households/teams, report, and keep money math correct across currencies at progressive scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Expense capture + budgets + reporting | Full bank core / ACH network |
| Money | User-facing expense ledger | Issuer cashback system |
| Sharing | Household/team splits | Full ERP/accounting suite |
| Amazon lens | Correctness, privacy, ownership | Cute charts-only demo |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Capture? | Manual, receipt photo, CSV/bank sync | Ingest paths |
| F2 | Categorize? | Rules + ML suggest + user override | Category engine |
| F3 | Budgets? | Monthly/category envelopes | Budget service |
| F4 | Split? | Household shares, IOUs | Split ledger |
| F5 | FX? | Multi-currency with rate day | FX policy |
| F6 | Receipts? | Images in object store + OCR | Async pipeline |
| F7 | Reports? | By category/time/project | Analytics read models |
| F8 | Authz? | Owner/member roles | ACL |
| F9 | Duplicates? | Same swipe + receipt | Dedupe |
| F10 | Export? | CSV/tax packs | Export jobs |
| F11 | Notify? | Budget thresholds | Notifications |
| F12 | SLA? | Capture durable; reports minutes-fresh | SLOs |

**MVP scope:**

1. CRUD expenses with idempotency.
2. Categories + rules.
3. Receipt upload + basic OCR async.
4. Budgets with alerts.
5. Household share/split.
6. Simple reports.
7. Bank CSV import.
8. Audit edits/deletes.

**Out of MVP:** full open-banking worldwide coverage, automated tax filing, corporate ERP replace, active-active dual writers same expense.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Create expense | p99 < 300ms |
| N2 | OCR complete | p95 < 30–60s |
| N3 | Durability | No lost expenses |
| N4 | Privacy | Encryption; least privilege |
| N5 | Consistency | Strong per wallet/ledger |
| N6 | Correct money | Integer cents + FX rules |
| N7 | Peak | Month-end / tax season 5–10× |
| N8 | Export | Reliable jobs |

### 1.3 Cases

**Happy:** Add expense/receipt→categorize→budget update→report→optional split settle.
**Edges:** duplicate bank+receipt; FX weekend rates; edit after split settle; OCR wrong; budget race; shared delete authz; import reprocess; offline mobile.

| Case | Behavior |
|------|----------|
| Duplicate import | Dedupe fingerprint |
| OCR wrong | User correct; learn rules |
| Budget race | Atomic counter/rebuild |
| Split edit | Versioned; recompute shares |
| Offline create | Idempotent sync |
| Unauthorized delete | ACL deny + audit |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Users | 100K | 1M | 10M | 100M |
| Expenses / day | 500K | 5M | 50M | 500M |
| Receipt OCR / day | 50K | 500K | 5M | 50M |
| Households | 30K | 300K | 3M | 30M |
| Report QPS | 50 | 500 | 5K | 50K |
| Bank imports / day | 20K | 200K | 2M | 20M |
| Categories | global+custom | → | → | → |
| Regions | 1 | 2 | 4 | 8 |

**Jumps:** 10×=multi-tenant hardening; 100×=import/OCR scale; 1,000×=global FX/privacy cells.

### 1.5 Scope repeat-back

> Expense ledger with capture paths, categorization, budgets, splits, FX, reports—privacy-aware and money-correct—scaled by user/wallet shards.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
500K expenses/day ≈ 6/s; peak higher month-end
OCR CPU/GPU bound separately
```

### 2.2 Storage

```text
Expense ~500B–2KB; receipts MBs in object store
100M users history → multi-TB
```

### 2.3 Latency

```text
Write path local to wallet shard; reports from rollups
```

### 2.4 Bottlenecks

(1) OCR cost (2) import storms (3) report scans (4) budget hot keys (5) mobile sync conflicts.

### 2.5 Cost

Receipt storage TTL/compression; OCR only when needed; rollups beat raw scans.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Expense Ledger | Authoritative expenses | Strong per wallet |
| Documents | Receipts/OCR | Eventually enriched |
| Budgets | Envelope counters | Strong or rebuildable |
| Splits | Shared obligations | Strong per group |
| Analytics | Reports | Eventual rollups |

**Deal-breaker:** treating OCR guesses as immutable money truth without user-confirm path.

### 3.2 Components

1. **Expense API** — CRUD idempotent
2. **Wallet/Books Service** — accounts
3. **Category/Rules** — suggest+apply
4. **Budget Service** — envelopes
5. **Split Service** — shares/settlements
6. **Receipt Pipeline** — upload/OCR
7. **Import Workers** — CSV/open banking
8. **FX Service** — rates
9. **Report/Rollup** — aggregates
10. **Notify** — budget alerts
11. **Search** — expense find
12. **Admin/Audit** — compliance

### 3.3 Core API (sketch)

```text
POST /v1/expenses {idempotency_key, wallet_id, amount_cents, currency, ts, category, ...}
POST /v1/receipts/upload → URL; POST complete
POST /v1/imports
GET /v1/reports?wallet&from&to
POST /v1/splits/{expense_id}
```

### 3.4 State machine

```text
EXPENSE: DRAFT → POSTED → (EDITED versions) → VOID
RECEIPT: UPLOADED → OCR_RUNNING → OCR_DONE → LINKED
BUDGET_PERIOD: OPEN → CLOSED
SPLIT: OPEN → PARTIALLY_SETTLED → SETTLED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| OCR auto-post | Suggest; confirm for high amounts | Accuracy |
| Budget counters | Incremental + nightly reconcile | Speed |
| Mobile offline | Queue with ids | UX |
| Reports | Rollup tables | Cost |
| FX | Store original + book currency | Clarity |

---

## 4. Architecture Diagram

```text
[Mobile/Web] -> Expense API -> Expense Ledger -> Budget Service
       |                           |
       v                           v
 Receipt Object Store -> OCR -> enrich   Split Service
 Bank Import Workers ------^
                              v
                         Rollup/Reports
```

### 4.1 Primary sequence

```text
Idempotent create POSTED expense
Apply category rules
Update budget counters
If receipt: async OCR propose fields
If split: create obligations
Rollup consumer updates reports
```

### 4.2 Isolation cell

```text
Shard by wallet_id / user_hash
Household group shard colocated when possible
Regional cells for residency
OCR workers shared elastic pool
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Amounts in integer minor units.
2. Idempotent create/import keys.
3. Edits versioned; audit trail.
4. Budget never silently corrupts—reconcilable from expenses.
5. ACL on every read/write.
6. FX conversion policy explicit (rate date).
7. Void/delete soft with restore window policy.
8. Split settlements don't invent money.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith PG |
| 10× | Shard wallets; object store receipts |
| 100× | OCR fleet; import pipelines; rollups |
| 1000× | Regional cells; tax-season CC |

### 5.3 Maintainability

- Category rule tests.
- OCR model canary.
- Rollup rebuild tools.
- Privacy deletion workflows.
- Import connector contracts.

### 5.4 Progressive scale

**1×:** Manual+CSV, simple budgets.
**10×:** Households+receipt OCR.
**100×:** Open banking; ML categorize.
**1000×:** Global FX/privacy; SMB features.

### 5.6 Dedupe fingerprints

Hash amount+ts window+merchant normalized; probabilistic link receipt↔bank line; user merge UI.

### 5.7 Budget integrity

Increment on post; rebuild from expenses if drift; alerts on thresholds with hysteresis.

### 5.8 Split math

Store shares as rationals/cents with remainder assignment rule; settlements reference obligations.

### 5.9 OCR pipeline

Virus scan; PII; async; confidence thresholds; never overwrite user fields blindly.

### 5.10 Offline sync

Client ids; vector clocks/version; server wins money fields with conflict UI for category notes.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Float money | Rounding chaos |
| OCR overwrites user silently | Trust loss |
| No idempotent import | Duplicates |
| Report-only without ledger | Lies |
| Cross-wallet unrestricted access | Privacy SEV |
| Hard delete without audit | Compliance |

---

## 6. Wrap-Up

### 6.1 Designed

Wallet-sharded expense ledger with capture/OCR/import, categories, budgets, splits, FX, rollups—privacy and cents correctness first.

### 6.2 Decisions to defend

1. Integer cents ledger
2. Idempotent ingest
3. OCR as suggestion
4. Rebuildable budgets
5. Versioned edits
6. Wallet shards
7. Rollup reports
8. Explicit FX policy

### 6.3 Risks

- OCR cost/accuracy
- Import connector fragility
- Budget drift
- Privacy incidents
- Tax-season load

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope tracker vs banking |
| 5–15 | Ledger+idempotency |
| 15–25 | Budgets+categories |
| 25–35 | OCR/import/splits |
| 35–45 | Scale/privacy/reports |

### 6.5 Closer

> **Expense Tracker System**: cents-correct expense ledger, idempotent capture, OCR as suggestion, rebuildable budgets, privacy-aware shards, progressive scale.

---

## 7. Deeper / Related Interview Questions

### 7.1 Ledger

**Q: Soft delete?**
A: Void state + retention.

**Q: Attachments limit?**
A: Quota per plan.

**Q: Recurring expenses?**
A: Templates generating posts.

### 7.2 Budgets

**Q: Rollover unused?**
A: Policy flag.

**Q: Shared budget?**
A: Household envelope with authz.

### 7.3 Splits

**Q: Uneven pennies?**
A: Remainder to payer rule.

**Q: Settle via Venmo?**
A: External; mark settled.

### 7.4 FX

**Q: Which rate?**
A: Book rate on expense date from FX service.

**Q: Crypto?**
A: Out of MVP.

### 7.5 Privacy

**Q: GDPR delete?**
A: Workflow erase PII; legal hold exceptions.

**Q: Employees admin access?**
A: Break-glass audited.

### 7.6 Traps

**Q: Build full QuickBooks**
A: Scope

**Q: Float doubles**
A: Fail

**Q: OCR as SoT**
A: Fail

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| Create p99 | UX |
| OCR lag | Pipeline |
| Dedupe precision/recall | Quality |
| Budget drift | Integrity |
| Import fail rate | Connectors |
| Report freshness | Analytics |
| Authz denials | Security |
| Storage $ / user | Frugality |

### 7.8 Ownership

**Q: Who pages for duplicate storm?**
A: Import + Ledger IC.

**Q: Who pages for budget wrong totals?**
A: Budget service; rebuild from ledger.

### 7.9 Progressive drill

**10×:** shard+object store
**100×:** OCR/import scale
**1,000×:** regional privacy cells

---

## 8. Appendices

### 8.1 Schema sketches

```text
wallets(wallet_id, owner, currency_book)
expenses(expense_id, wallet_id, amount_cents, currency, book_amount_cents, ts, category_id, version, idem_key UNIQUE)
expense_versions(...)
receipts(receipt_id, wallet_id, object_key, ocr_json, state)
budgets(budget_id, wallet_id, period, category_id, limit_cents)
budget_counters(budget_id, used_cents, version)
splits(split_id, expense_id, state)
split_legs(split_id, user_id, amount_cents)
imports(import_id, source, state)
rollups(wallet_id, period, category_id, total_cents)
```

### 8.2 API checklist

- [ ] Expense create/update/void
- [ ] Receipt upload
- [ ] Import
- [ ] Budget CRUD
- [ ] Split/settle
- [ ] Report get
- [ ] Export
- [ ] Share invite

### 8.3 Oncall checklist

- [ ] Import backlog
- [ ] OCR backlog
- [ ] Budget drift
- [ ] Authz incidents
- [ ] Rollup lag
- [ ] Disk/object cost spike
- [ ] Bad FX feed

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Wallet | Books/account container |
| Book amount | Normalized currency amount |
| Envelope | Budget category limit |
| OCR | Receipt text extract |
| Dedupe | Duplicate detection |
| Rollup | Preaggregated report |

### 8.5 Deal-breaker one-liners

- Float money
- OCR silent overwrite
- Non-idempotent import
- Reports without ledger rebuild path

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Ledger | Expenses Platform |
| OCR | Docs ML |
| Budgets | Budgets Eng |
| Imports | Connectivity |
| Splits | Sharing |
| Reports | Analytics |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | PG monolith |
| 10× | Wallet shards |
| 100× | OCR fleet + rollups |
| 1000× | Regional cells |

### 8.8 Failure injection

1. Dup import — dedupe.
2. OCR poison — quarantine.
3. Budget drift — rebuild.
4. FX feed down — freeze book convert; keep original.
5. Offline conflict — UI resolve.
6. Authz bug — revoke+audit.

---

## Interview Traps

**Trap: ERP scope creep**
Signal: Control

**Trap: Ignore privacy**
Signal: SEV

**Trap: Scan all expenses for every report**
Signal: Cost

**Trap: Shared DB without ACL tests**
Signal: Fail

---

## Flash Cards

### Card 1: Cents ledger

No float.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Expenses Platform

### Card 2: Idempotent create

Client keys.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Docs ML

### Card 3: OCR suggest

User confirms.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Budgets

### Card 4: Budget rebuild

From expenses.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Connectivity

### Card 5: Dedupe

Fingerprint+UI.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Sharing

### Card 6: Split remainder

Explicit rule.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Analytics

### Card 7: FX policy

Rate date.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Expenses Platform

### Card 8: Wallet shard

Scale.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Docs ML

### Card 9: Rollups

Cheap reports.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Budgets

### Card 10: ACL always

Privacy.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Connectivity

### Card 11: Void not purge

Audit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Sharing

### Card 12: Import connectors

Contracts.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Analytics

### Card 13: Offline sync

Versioned.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Expenses Platform

### Card 14: Deal-breaker

Dup money; OCR SoT.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Docs ML

### Card 15: Metrics

Drift; OCR lag.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Budgets

### Card 16: Tax season

Pre-scale.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Connectivity

---

## Scenario Runbooks

### R1 — Duplicate expenses spike
Pause importer; fix fingerprint; merge tool.

### R2 — OCR backlog
Scale workers; degrade to manual.

### R3 — Budget complaints
Rebuild counters; patch increment path.

### R4 — Privacy incident
Rotate keys; audit access; notify.

### R5 — Report lag
Rebuild rollups; shed heavy exports.

---

## Extended Rapid Q&A

**Q: Projects/tags?**
A: Dimensions on expense.

**Q: Mileage?**
A: Special expense type.

**Q: Corporate approvals?**
A: Workflow later.

**Q: Attachments virus?**
A: Scan before index.

**Q: Search?**
A: Per-wallet index.

**Q: Why soft void?**
A: Audit/tax.

**Q: First widget?**
A: Budget burn + drift.

**Q: SMB vs consumer?**
A: Same ledger; authz richer.

**Q: CSV mapping?**
A: Templates per bank.

**Q: ML category?**
A: Suggest with override.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Only spreadsheets export SoT | Not product |
| Float totals | Bugs |
| Global unsharded table | Hotspot |
| Auto-post all OCR | Trust loss |
| No audit edits | Support hell |

---

## LLD Touch (optional)

Classes: `Wallet`, `Expense`, `ExpenseVersion`, `Receipt`, `Budget`, `Split`, `ImportBatch`, `FxRate`, `Rollup`. Patterns: Idempotency keys, Outbox to rollups, Saga(split settle), CQRS read models, Object store + async OCR.

---

## 60-second Narrative

"We keep a cents-accurate expense ledger sharded by wallet. Captures are idempotent across manual, import, and receipt paths—OCR suggests, users confirm. Budgets are incremental yet rebuildable. Splits and FX have explicit policies. Reports use rollups. Privacy ACL is everywhere. Scale OCR and imports elastically; never sacrifice ledger truth. Success is trusted books, low dupes, and calm tax season."

---

## Extra Depth: Open Banking

Webhooks+reconciliation; connector SLOs.

## Extra Depth: Tax Packs

Export jobs with consistent snapshots.

## Extra Depth: ML Category

Features from merchant; feedback loop; canary.

## Extra Depth: Retention

Cold tier old receipts; legal holds.

## Extra Depth: Observability

Wide events; careful PII redaction.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How do you merge duplicate expenses safely?**
A: UI merge keeps one POSTED; voids other with link; budgets rebuild.

**Q: Corporate expense policy engine?**
A: Rules on category/amount; approval workflow later tier.

**Q: Mileage IRS rates?**
A: Configurable rate tables by year; distance input.

**Q: Shared household invite abuse?**
A: Invite tokens; role least privilege; audit.

**Q: Export consistency for tax?**
A: Snapshot isolation at job start.

**Q: Receipt in wrong wallet?**
A: Move with authz; audit.

**Q: Why book_amount and original currency?**
A: Reports stable; originals preserved.

**Q: Bank webhook retries?**
A: Idempotent import keys.

**Q: Offline photo then connect?**
A: Receipt links when expense syncs via client ids.

**Q: Budget alert spam?**
A: Hysteresis + daily caps.

**Q: Search PII leakage in logs?**
A: Redact; per-wallet index only.

**Q: SMB projects + clients?**
A: Dimensions; report filters.

**Q: Hard currency crypto?**
A: Out of MVP; don't float.

**Q: GDPR right to access?**
A: Export pack job.

**Q: SEV for cross-tenant data leak?**
A: Sev-1 privacy; revoke; notify.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT | Expense ledger |
| OCR | Suggestion |
| Budgets | Rebuildable |
| Kill | Float; silent OCR overwrite |

---

*End of Expense Tracker System design notes (Amazon SDE III prep).*


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

