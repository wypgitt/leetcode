# System Design: Credit-Card Cashback Promotion System

> **Focus areas:** Promotion eligibility · Accrual / earning · Category MCC mapping · Caps (daily/monthly/promo) · Settlement & statement credit · Fraud & abuse · Statementing · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct money invariants (integer cents), split authorize vs clear vs settle planes, explicit cap math under concurrency, deal-breakers for “just % of auth amount”  
> **Amazon lens:** Amazon Store Card / Amazon Prime Visa–class promotions, marketplace spend categories, trust & finance auditability, two-pizza ownership of promo correctness

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

Goal: **bound a cashback promotions platform**—decide whether a card transaction earns a promotion, accrue the correct reward under category rates and caps, settle rewards to statement credit / points / partner ledger, and stop fraud—without over-paying cashback or stranding legitimate earn.

### 1.0 What this is / is not

| Dimension | **Cashback promotion system (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Eligible spend → accrue reward → settle | Full card issuer core banking / authorization switch |
| Success | Correct earn under caps; reconcilable to finance | Pretty “5% back” marketing page alone |
| Money SoT | Accrual ledger + settlement ledger | Client-displayed pending balance alone |
| Event SoT | Auth / clear / refund / chargeback streams | Single mutable “cashback_balance” row |
| Fraud | Promo abuse, MCC gaming, synthetic spend | Full AML/KYC platform (hooks only) |
| Amazon lens | Store Card / cobrand Visa promos, Amazon.com category boosts, Prime Day flash earn | Generic bank-anywhere rewards without commerce context |

**Scope statement:** Design a credit-card cashback promotion system: versioned promo catalog, eligibility, MCC/category rates, accrual on cleared spend (with auth estimates), multi-dimensional caps, settlement to statement credit, fraud controls, and audit—from baseline through 10× / 100× / 1,000× transaction volume.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who issues the card? | Amazon-branded / cobrand with bank partner | Clear boundary: we own promo engine + ledger; bank owns auth switch |
| F2 | Reward types? | % cashback, fixed cents/txn, tiered, points | Typed earn calculators; integer minor units |
| F3 | When does earn happen? | Accrue on **clear/settle**; show pending on auth | Dual state: PENDING vs POSTED |
| F4 | Categories? | MCC + Amazon category + merchant allowlists | Category resolver service |
| F5 | Caps? | Per promo, per period (day/month/promo life), per card / household | Cap ledger with atomic reserve |
| F6 | Stacking? | Usually best-of or priority; some stack with base earn | Explicit stack policy |
| F7 | Eligibility? | Product (Prime Visa), cohort, geo, new-to-card, enroll | Rule predicates + enrollment |
| F8 | Refunds / chargebacks? | Claw back posted earn; reverse pending | Adjustment ledger entries |
| F9 | Settlement? | Monthly statement credit, or rolling | Settlement batch + partner file |
| F10 | Enrollment? | Auto for some; opt-in for others | Enrollment state machine |
| F11 | Flash promos? | “5% Amazon.com this weekend” spikes | Hot promo path; cache; caps |
| F12 | Partner bank? | Daily/near-RT files or event bus | Idempotent ingest; recon |
| F13 | Customer UX? | Pending earn, posted, remaining cap | Read APIs + projections |
| F14 | Fraud? | Manufactured spend, MCC miscode gaming, refund abuse | Risk scores; velocity; hold |
| F15 | Audit? | Why this txn earned $X | Explanation + immutable rows |

**MVP functional scope (lock with interviewer):**

1. Versioned **promo catalog** (schedule, rates, categories, caps, stack policy).  
2. **Enrollment** (auto or opt-in) with eligibility predicates.  
3. Ingest **auth**, **clear**, **refund**, **chargeback** events idempotently.  
4. **Category resolution** (MCC → category; Amazon.com → special category).  
5. **Accrue** PENDING on auth (estimate); **POST** on clear; adjust on refund.  
6. Multi-dim **caps** with atomic remaining.  
7. **Settlement** job → statement credit / bank file.  
8. Customer **balance & history** APIs.  
9. Basic **fraud** velocity + hold queue.  
10. Admin publish + audit log + kill switch.

**Out of MVP (explicitly defer):**

- Full issuer authorization decisioning (approve/decline card)  
- Cryptocurrency rewards rails  
- Perfect real-time MCC correction from merchant disputes before clear  
- Cross-issuer universal rewards marketplace  
- Arbitrary Turing-complete promo scripts on the hot path

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Accrual latency after clear | Near-real-time UX | p99 < 5–30s post-clear ingest; batch OK for settlement |
| N2 | Auth-path impact | Must not slow auth | Async after auth event; never block issuer switch |
| N3 | Correctness | No silent over-earn | Caps atomic; ledger append-only; recon |
| N4 | Availability | Accrual can lag; catalog publish HA | Prefer delay earn over wrong earn |
| N5 | Durability | Money events durable | RPO≈0 for acked ingest |
| N6 | Auditability | Finance-grade | promo_version pinned; explanation |
| N7 | Scale | See progressive table | Split ingest vs settle vs read QPS |
| N8 | Consistency | Caps strong; UX eventual OK | Cap home region / shard |
| N9 | Security | No forgeable client earn | Server authority; signed partner events |
| N10 | Multi-region | Cards regional; Amazon global spend | Cell by market; global promo care |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Customer with enrolled “5% Amazon.com” buys on Amazon → clear → accrue 5% under monthly cap → appears PENDING then POSTED → settles to statement credit.  
2. Gas MCC at 2% with $1/txn min → earn applied; category shown in app.  
3. Cap remaining $3 on 5% promo → $100 spend earns $3 not $5; explanation `CAP_HIT`.  
4. Refund of cleared txn → clawback posted earn (or pending); cap restored per policy.  
5. Flash weekend promo ends → in-flight clears after end: pin policy (event_time vs clear_time)—**pick one** (recommend **purchase/auth time** with promo version).  
6. Base 1% + category 5%: stack policy BEST_OF → 5% wins; or STACK → both if allowed.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Auth never clears | Pending expires / voids; no posted earn |
| Partial clear / multi-clear | Accrue on each clear amount; link to auth |
| Tip adjustment after restaurant auth | Recompute on final clear |
| Chargeback after settlement | Negative adjustment; may create receivable |
| MCC wrong (Amazon coded as misc) | Allowlist ASINs/merchant IDs; dispute queue |
| Two promos claim same spend | Stack policy deterministic |
| Clock skew on promo window | Server event_time; safety margins |
| Cap race two txns simultaneous | Atomic cap reserve on post |
| Partner file duplicate | Idempotency keys |
| Settlement fails mid-batch | Restartable batches; exactly-once credit keys |
| Floating point | Integer cents / millipoints |
| Household / AU (authorized user) caps | Cap key = primary or product policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active cards | 5M | 50M | 500M | 5B (theoretical) |
| Auth events / day | 20M | 200M | 2B | 20B |
| Clear events / day | 18M | 180M | 1.8B | 18B |
| Peak ingest QPS | ~2K | ~20K | ~200K | ~2M |
| Active promos | 200 | 2K | 20K | 200K |
| Accrual writes / day | ~20M | ~200M | ~2B | ~20B |
| Settlement credits / month | 5M | 50M | 500M | 5B |
| Cap updates / day | ~15M | ~150M | ~1.5B | ~15B |
| Customer balance reads QPS | ~1K | ~10K | ~100K | ~1M |
| Fraud scores / clear | ~18M/day | 10× | 100× | 1,000× |

**What each jump forces:**

- **10×:** Event bus + idempotent consumers; versioned promos; Redis/Dynamo cap shards; pending/posted states.  
- **100×:** Shard by `card_id` / `account_id`; stream processing; settlement parallelism; partner recon warehouse.  
- **1,000×:** Regional cells; hot Amazon.com promo paths; pre-aggregated read models; cap spraying for viral flash earn; offline dispute factory.

### 1.5 Etc. (Constraints & Assumptions)

- **Issuer switch is out of band**; we consume signed events.  
- Money in **integer cents** (or millipoints for points products).  
- Prefer **under-earn + adjust** over silent over-earn when ambiguous.  
- Amazon.com spend may use **internal order events** richer than MCC.  
- Partner bank remains system of record for **statement**; we are SoT for **promo earn ledger** until settlement accepted.

**Scope statement (say aloud):**

> Design cashback promotions: eligibility, category rates, pending/posted accrual, multi-dimensional caps, clawbacks, settlement to statement credit, fraud holds—correct under duplicates, partial clears, and refunds—from ~2K ingest QPS through 1,000× (~2M QPS), failing closed on cap ambiguity.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Auth ingest | 2K | 2M | Write-ahead; async accrue |
| Clear ingest | 1.5K | 1.5M | Posts earn |
| Refund / chargeback | 50 | 50K | Adjustments |
| Cap reserve/update | 1.5K | 1.5M | Strong path |
| Balance / history read | 1K | 1M | Cache projections |
| Settlement batch | nightly | nightly×cells | Throughput not QPS |
| Admin publish | 1 | 100 | Cache invalidate |
| Fraud score | 1.5K | 1.5M | Tiered sync/async |

**Critical:** Auth/clear ingest ≫ settlement. Never put settlement locks on the ingest path. Cap updates are the consistency bottleneck, not catalog reads.

### 2.2 Storage

```text
Txn event ~500 B–2 KB
20M clears/day × 1 KB = 20 GB/day raw events (baseline)
100×: 1.8B × 1 KB ≈ 1.8 TB/day → compress + tier to cold
Accrual row ~200 B; ~1 accrual / clear → similar order
Cap keys: cards × promos × periods
  50M cards × 5 active promos × 30 B = 7.5 GB hot (10×)
Promo catalog: 20K × 5 KB = 100 MB (fits everywhere)
Settlement file: 50M credits × 100 B = 5 GB/month (10×)
```

### 2.3 Cap math

```text
Monthly cap $150 cashback at 5%:
  max qualifying spend = 150 / 0.05 = $3,000
Two concurrent clears $2,000 and $2,000:
  without atomicity → both might earn $100 → $200 > cap
  with reserve: first reserves min(100, remaining); second gets remainder
```

### 2.4 Settlement math

```text
5M cards × avg $12 cashback/month = $60M statement credits
File rows 5M; generate in 1 hour → ~1.4K rows/s trivial
At 1,000× fantasy 5B cards → cell by market; never one file
```

### 2.5 Amazon.com category boost

```text
Peak Prime Day: Amazon clears dominate
Category resolver must use order_id join, not only MCC 5411/5969 noise
Cache “card → open orders” short TTL for matching
```

### 2.6 Critical bottlenecks

1. Cap hot keys on viral flash promo  
2. Duplicate partner events double-earn  
3. Refund after settlement clawback lag  
4. Category misclassification → wrong rate  
5. Catalog publish stampede  
6. Cross-region dual accrual for same txn  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
CardAccount (account_id, product_code, primary_user, status)
Promo (promo_id, version, schedule, status, stack_policy)
EarnRule (rate_bps | fixed_cents, category_selector, min_txn, max_txn)
Cap (cap_id, dimensions=[promo, account, period], limit_cents)
Enrollment (account_id, promo_id, state, enrolled_at)
TxnEvent (event_id, type=AUTH|CLEAR|REFUND|CHARGEBACK, amount_cents,
          mcc, merchant_id, amazon_order_id?, event_time, ingest_time)
CategoryDecision (txn_id, category, confidence, method)
Accrual (accrual_id, account_id, txn_id, promo_id, version,
         state=PENDING|POSTED|REVERSED|HELD, amount_cents, explain)
CapLedger (cap_key, period, remaining_cents, version)
SettlementBatch (batch_id, period, status)
SettlementItem (batch_id, account_id, amount_cents, idem_key)
```

### 3.2 Planes (lock early)

```text
1. Ingest plane     — durable event log, idempotent
2. Decision plane   — eligibility + category + rate + cap
3. Ledger plane     — accruals & adjustments (append-only)
4. Settlement plane — batch credits to bank/statement
5. Read plane       — balances, history, remaining caps
6. Control plane    — promo publish, kill switch, enrollment admin
7. Risk plane       — fraud score, holds, cases
```

### 3.3 Event timeline & earn state machine

```text
AUTH  → create PENDING accrual (estimate, soft cap check)
CLEAR → POST accrual (hard cap reserve); adjust if amount ≠ auth
VOID  → reverse PENDING
REFUND → negative POSTED adjustment; restore cap per policy
CHARGEBACK → like refund + risk flag
SETTLE → mark accruals SETTLED when included in batch
```

**Policy:** Customer-visible “pending rewards” ≠ guaranteed; posted is commitment subject to chargeback.

### 3.4 Eligibility

```text
eligible = promo.active_for(event_time)
  AND account.product in promo.products
  AND enrollment.state == ENROLLED (if required)
  AND user/account predicates (Prime, tenure, geo)
  AND not suppressed (fraud, legal, bankruptcy)
  AND category matches earn rule
  AND amount in [min,max]
  AND cap.remaining > 0 (soft)
```

### 3.5 Category resolution

| Signal | Strength | Use |
|--------|----------|-----|
| Amazon `order_id` + internal category | Strongest | Amazon.com / Whole Foods / etc. |
| Merchant ID allowlist | Strong | Strategic partners |
| MCC | Medium | Gas, grocery, dining |
| MCC + merchant name NLP | Weak | Fallback |
| Customer dispute | Manual | Ops correction |

```text
function resolveCategory(txn):
  if txn.amazon_order_id:
    return joinOrderCategory(txn.amazon_order_id)
  if allowlist(txn.merchant_id):
    return allowlist.category
  return mccMap(txn.mcc)  // with versioned MCC book
```

### 3.6 Earn calculation

```text
rate_bps = 500  // 5.00%
gross = floor(clear_amount_cents * rate_bps / 10_000)
earn = min(gross, cap_remaining, rule.max_earn_per_txn?)
```

Always **floor** in favor of consistency; document rounding. Integer only.

### 3.7 Caps

| Dimension | Example |
|-----------|---------|
| Promo × account × calendar_month | $150/mo cashback |
| Promo × account × promo_window | $50 total welcome |
| Promo × account × day | Flash $10/day |
| Product × household | Shared family cap |

**Implementation:**

```text
cap_key = hash(account_id, promo_id, period_id)
reserve(cap_key, amount):
  // optimistic CAS or atomic DECRV with floor 0
  // return granted <= requested
```

Flash promos: shard remaining if single promo is ultra-hot across many accounts—usually **per-account** caps avoid global hot keys; global budget caps need shards.

### 3.8 Stacking

```text
Modes:
  BEST_OF — pick max earn among eligible promos (common)
  PRIORITY — first matching priority wins
  STACK — sum earns (rare; cap each)
Determinism: sort by (priority desc, promo_id asc); pure function
```

### 3.9 Settlement

```text
Monthly (or cycle):
  1. Select POSTED unsettled accruals for cycle
  2. Aggregate per account net cents (earns - clawbacks)
  3. Skip / hold accounts in fraud HELD
  4. Write SettlementItems with idem_key=account+cycle+promo_set_version
  5. Emit bank file / statement-credit API
  6. On ACK: mark SETTLED; on NAK: retry / exception queue
```

**Invariant:** `sum(posted) - sum(reversed) - sum(settled) = unsettled_liability`.

### 3.10 Fraud & abuse

```text
Signals:
  - velocity: earn $/hour, distinct merchants, refund ratio
  - manufactured spend patterns (crypto, money orders MCCs)
  - new account + max cap burn in hours
  - correlated rings (shared device, funding)
Actions:
  - HELD accrual (no settle)
  - reduce rate / deny promo
  - step-up / case to risk ops
Path:
  - cheap rules sync before POST
  - ML async; can move POSTED → HELD before settlement cutoff
```

**Deal-breaker:** Settling held/fraudulent earn because batch ignored risk flags.

### 3.11 Partner integration

```text
Bank → us: auth/clear/refund events (Kafka / SFTP + CDC)
Us → bank: settlement credit file, dispute packs
Amazon retail → us: order category enrichments
Idempotency: event_id from partner UNIQUE
Schema versioning: additive; dead-letter poison
```

### 3.12 Storage trade-offs

| Store | Role |
|-------|------|
| Kafka / Kinesis | Event spine |
| DynamoDB / Cassandra | Caps, enrollments, hot accruals by account |
| Postgres / Aurora | Promo catalog, settlement batches |
| S3 + warehouse | Raw events, recon, analytics |
| Redis | Catalog cache, read projections |
| Object store | Partner files |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Issuer/Bank Auth Switch] [Amazon Order/Payments] [Admin Promo Console]
           |                      |                        |
           v                      v                        v
                 API / Ingest Gateway (TLS, auth)
                              |
                              v
                       Durable Event Log
                     /        |         \
                    v         v          v
            Category Resolver -> Accrual Engine <- Risk Scorer
                                   |
                    /--------------+--------------\
                   v               v               v
              Cap Service    Accrual Ledger   Enrollment+Catalog
                                   |
                                   v
                           Settlement Worker --> Bank / Statement Credit API
                                   |
                                   v
                           Read Models / Balance API <-- Mobile / Web
```

### 4.2 Accrual engine internals

```text
event → dedupe(event_id) → load account/enrollment
     → resolve category → list candidate promos (index)
     → filter eligibility → stack select
     → compute gross earn → cap.reserve
     → append accrual(POSTED|PENDING|HELD) + explain
     → emit projection update
```

### 4.3 Cap reserve (per account)

```text
┌ account_id shard ┐
│ cap_key rows     │  CAS remaining_cents
│ txn lock optional│  for multi-promo atomicity
└──────────────────┘
Global promo budget (optional): sharded counters + reconcilers
```

### 4.4 Settlement

```text
Warehouse snapshot → Settlement Planner → Batch Writer
  → File Emitter → Partner ACK → Mark SETTLED
  → Exception Queue → Ops
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Same `event_id` never creates two accruals.  
2. Posted earn ≤ min(gross, reserved_cap).  
3. Cap remaining ≥ 0 always.  
4. Net settle amount = sum(posted − reversed) for included set.  
5. Promo version immutable once referenced by accrual.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Consumer crash mid-accrual | Idempotent process; transactional outbox |
| Cap CAS conflict | Retry; deterministic grant |
| Partner duplicate file | event_id / file row keys |
| Settlement partial ACK | Per-item idem_key; resume |
| Catalog bad publish | Canary + kill switch; version pin |
| Poison event | DLQ; don't block partition forever |
| Clock skew | event_time bounds; quarantine |

**Degradation:** If risk service down → post with `risk_deferred` flag and hold from settlement until scored (prefer delay settle over wrong pay-out). If category enrich down → MCC-only fallback with lower confidence; may under-earn Amazon boost (document).

**Deal-breakers to call out:**

- Mutating accrual amounts in place (use adjustments).  
- Blocking card auth on our promo service.  
- Eventual-consistency caps for monthly dollar caps.  
- Floating-point earn.

### 5.2 Scalability

**Progressive tactics**

| Scale | Tactic |
|-------|--------|
| 10× | Partition Kafka by account_id; Dynamo caps; catalog cache |
| 100× | Stream autoscaling; settle by account ranges; CQRS reads |
| 1,000× | Market cells; cold event tiering; pre-agg monthly balances; flash admission |

**Hot keys:** Per-account caps are naturally sharded by account. Global “first 1M customers get bonus” needs spray counters + enrollment reservations.

**Read path:** Materialize `balance_projection(account_id)` updated async; serve from cache. History via time-ordered accrual query (paginate).

**Multi-region:** Accrual home = account region. Promo catalog global with version. Settlement per market to local bank partner.

### 5.3 Maintainability

**Ownership (two-pizza):**

- Promo Catalog & Merch tooling  
- Accrual Engine & Caps  
- Settlement & Partner Integration  
- Risk Holds  
- Customer Read APIs  

**Versioning:** Promo versions immutable; MCC maps versioned; earn calculator library semver with golden txn tests in CI.

**Observability:**

- Lag: event ingest → posted  
- Cap grant failures / remaining distribution  
- Earn by promo (dollars)  
- Settlement break $ vs partner ACK  
- Fraud hold rate + false positive tickets  
- DLQ depth  

**Testing:**

- Golden transactions per promo version  
- Concurrent cap property tests  
- Refund/chargeback sequences  
- Settlement idempotency replay  
- Chaos: kill consumer mid-CAS  

**Operability runbooks:** over-earn incident, under-earn Amazon category, settlement NAK storm, flash cap meltdown, partner schema change.

---

## 6. Wrap-Up

### 6.1 MVP build order

1. Event ingest + idempotent store  
2. Promo catalog + enrollment  
3. Category (MCC + Amazon order join)  
4. Accrual engine PENDING/POSTED + explanations  
5. Cap service atomic  
6. Balance read API  
7. Settlement batch + partner file  
8. Refund clawback  
9. Fraud holds  
10. Kill switch + admin audit  

### 6.2 Trade-offs to say aloud

| Choice | Trade-off |
|--------|-----------|
| Accrue on clear not auth | Correctness > instant gratification |
| BEST_OF stacking | Simpler UX; less “surprise stack” |
| Hold settlement if risk down | Customer delay vs overpay |
| Integer floor rounding | Tiny under-earn; consistent |
| CQRS balances | Fast reads; brief lag |

### 6.3 Risks

1. Partner event ambiguity (partial clear semantics).  
2. Category fraud / MCC laundering.  
3. Settlement mis-file → customer trust + finance restatement.  
4. Cap bug → material P&L impact.  
5. Flash promo thundering herd on catalog/caps.

### 6.4 60-second pitch

> We ingest issuer auth/clear/refund events into a durable log, resolve category (Amazon order join beats MCC), evaluate versioned promos with deterministic stack policy, atomically reserve multi-dimensional caps, append PENDING/POSTED accruals with explanations, claw back on refunds, and settle net credits in idempotent batches to the bank—fraud can hold before settlement. Auth path never blocks on us. Scale by account sharding; fail closed on caps.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & promo types

**Q: Points vs cashback?**  
A: Same ledger with `unit=CENTS|POINTS`; settlement adapter differs (statement credit vs points bank).

**Q: Tiered earn (1% then 5% after $1K)?**  
A: Progress counter on account×promo×period; rate table by threshold; careful with refunds moving tiers.

**Q: Welcome bonus “spend $X get $Y”?**  
A: Separate milestone tracker; grant once; strong idempotency; fraud-heavy.

**Q: Rotating categories each quarter?**  
A: Schedule windows on promo versions; customer enrollment of 5% cats.

### 7.2 Eligibility & enrollment

**Q: Auto-enroll vs opt-in?**  
A: Product policy; record legal basis; allow opt-out suppressions.

**Q: Authorized users?**  
A: Spend accrues to primary account caps unless product says otherwise.

**Q: Delinquent accounts?**  
A: Suppress settle; optionally still accrue for win-back policy—product call.

### 7.3 Category

**Q: Why not MCC only?**  
A: Amazon.com often miscoded; internal order linkage is the Amazon advantage.

**Q: Split tender / partial Amazon?**  
A: Earn only on Amazon-paid portion if identifiable; else policy.

**Q: Marketplace 3P seller?**  
A: Usually still Amazon.com category if paid via Amazon—confirm product.

### 7.4 Caps & concurrency

**Q: How to avoid over-cap?**  
A: Atomic reserve at POST; never trust soft check alone.

**Q: Restore cap on refund?**  
A: Yes for same period usually; document if settlement already done (adjust next cycle).

**Q: Timezone for monthly cap?**  
A: Account billing timezone or UTC—**pick one**; store period_id.

### 7.5 Auth vs clear

**Q: Show pending 5% on auth?**  
A: Yes as estimate; rebinding on clear; UX copy “pending”.

**Q: Auth $100 clear $110 (tip)?**  
A: Post on $110; reserve additional cap.

**Q: Clear without auth?**  
A: Force-post path; still idempotent on clear_id.

### 7.6 Refunds & chargebacks

**Q: Partial refund?**  
A: Proportional clawback of earn; floor/ceil policy consistent with earn rounding.

**Q: Refund after settle?**  
A: Negative settlement item next cycle or immediate debit—partner capability dependent.

**Q: Friendly fraud chargeback?**  
A: Clawback + risk case; don't auto-re-enroll bonuses.

### 7.7 Settlement

**Q: Exactly-once statement credit?**  
A: Idempotency key per account×cycle; partner ACK required.

**Q: Netting multiple promos?**  
A: Aggregate net cents one line or itemized—product/bank file format.

**Q: Recon break?**  
A: Exception queue; pause cycle for material breaks; finance ownership.

### 7.8 Fraud

**Q: Manufactured spend?**  
A: MCC denylist; velocity; merchant risk lists; hold settlement.

**Q: Refund farming?**  
A: High refund/earn ratio → hold; delayed settle for new accounts.

**Q: Insider merch promo?**  
A: Dual control publish; audit; blast-radius canaries.

### 7.9 Multi-region & DR

**Q: Active-active accrual?**  
A: Dangerous for caps; prefer single home per account.

**Q: RPO/RTO?**  
A: Event log multi-AZ; RPO≈0 acked; RTO minutes for consumers.

### 7.10 API design

```text
GET /v1/accounts/{id}/rewards/summary
GET /v1/accounts/{id}/rewards/transactions?cursor=
GET /v1/accounts/{id}/promos  // enrolled + remaining caps
POST /v1/promos/{id}/enroll
```

**Q: Idempotency for enroll?**  
A: Yes—enroll key account+promo.

### 7.11 Estimation traps

**Q: 2B clears × 1 KB = 2 PB/day?**  
A: 2B×1KB = 2 TB/day. Units matter.

**Q: Cap in Postgres single row for all users?**  
A: Won't scale; per-account keys.

### 7.12 Interview traps

**Q: “Just multiply amount × 0.05 in float.”**  
A: Integer bps; deterministic floor.

**Q: “Update balance in place.”**  
A: Ledger + projection.

**Q: “Block auth if promo service down.”**  
A: Never; card auth is sacred.

**Q: “Eventual cap is fine.”**  
A: Over-earn = real money loss.

**Q: “Settle from mutable balance.”**  
A: Settle from accrual ledger snapshot.

### 7.13 Ownership scenarios

**Q: Sev: 2× cashback paid sitewide.**  
A: Kill switch; halt settlement; estimate liability; reverse batch if not ACK'd; customer comms; root-cause rate/bps bug.

**Q: Customers angry pending never posts.**  
A: Clear lag vs bug; check DLQ; partner feed health.

**Q: Finance recon off by $1.3M.**  
A: Idempotency holes or timezone period bugs; freeze cycle.

### 7.14 Comparisons

**Q: vs coupons/discounts engine?**  
A: Coupons affect checkout price; cashback is post-purchase earn with issuer events + settlement.

**Q: vs points banks (loyalty)?**  
A: Similar ledger; cashback settlement is simpler (currency) but issuer-coupled.

### 7.15 Misc deep cuts

**Q: Foreign currency?** A: Convert with locked rate source at clear; store FX ref.  
**Q: Offline clear days later?** A: Accrue on clear; promo pin by auth time.  
**Q: Promo version change mid-month?** A: Existing accruals keep version; new txns new version.  
**Q: Statement credit vs check?** A: Adapter; same SettlementItem.  
**Q: GDPR/CCPA?** A: Access controls; retention on events; explain exports.  
**Q: Golden tests?** A: Fixture txns per promo YAML.  
**Q: Cap period DST?** A: Use absolute period boundaries in account TZ library.  
**Q: Multi-clear shipment?** A: Each clear independent; link auth_id.  
**Q: Kill switch granularity?** A: Per promo, per product, global earn halt.  
**Q: Explain API?** A: `RATE`, `CAP_HIT`, `NOT_ENROLLED`, `CATEGORY_MISS`, `HELD_RISK`.

**Eval budget sketch (post-clear path):** dedupe 2ms + cat 20ms + promos 10ms + cap 10ms + write 10ms ≈ 50–100ms offline OK.

---

## 8. Appendices

### 8.1 Schema sketches

```text
promos(promo_id, status, created_at)
promo_versions(promo_id, version, schedule_start, schedule_end,
  earn_rules_json, stack_policy, caps_json, predicates_json, published_at)
enrollments(account_id, promo_id, state, enrolled_at, UNIQUE(account_id,promo_id))
txn_events(event_id PK, account_id, type, amount_cents, currency,
  mcc, merchant_id, amazon_order_id, event_time, payload_json)
category_decisions(event_id, category, method, confidence, version)
accruals(accrual_id, account_id, event_id, promo_id, promo_version,
  state, amount_cents, explain_json, created_at,
  UNIQUE(event_id, promo_id))
cap_balances(cap_key, period_id, remaining_cents, row_version)
settlement_batches(batch_id, cycle_id, status, created_at)
settlement_items(batch_id, account_id, amount_cents, idem_key UNIQUE, status)
risk_holds(accrual_id, reason, created_at, released_at)
```

### 8.2 API sketches

```text
POST /v1/events/card  (partner mTLS)
Idempotency-Key: event_id
{ "event_id":"...", "type":"CLEAR", "account_id":"A",
  "amount_cents":5000, "mcc":"5411", "event_time":"..." }

GET /v1/accounts/A/rewards/summary
→ { "pending_cents":120, "posted_unsettle_cents":4400,
    "caps":[{"promo_id":"P5","remaining_cents":10600}] }

POST /v1/settlement/cycles/{cycle}/run  (internal)
→ { "batch_id":"B1", "accounts":123456, "total_cents":... }
```

### 8.3 Earn + cap pseudocode

```text
function onClear(event):
  if seen(event.event_id): return
  cat = resolveCategory(event)
  promos = selectStack(eligible(event, cat))
  for p in promos:
    gross = earnCents(event.amount_cents, p.rule)
    granted = caps.reserve(key(event.account_id,p), period(event), gross)
    state = HELD if risk.score(event) > T else POSTED
    writeAccrual(..., amount=granted, state, explain)
```

### 8.4 Cap reserve pseudocode

```text
function reserve(cap_key, period, request):
  for attempt in 1..N:
    row = get(cap_key, period)
    grant = min(request, row.remaining)
    if cas(row, remaining=row.remaining-grant, ver=row.ver+1):
      return grant
  throw RetryExhausted
```

### 8.5 Settlement pseudocode

```text
function settle(cycle):
  for account_shard in shards:
    net = sum(POSTED unsettle) - sum(REVERSED unsettle) where not HELD
    if net == 0: continue
    item = putIfAbsent(idem_key=account+cycle, amount=net)
    emitPartner(item)
  markBatchReady()
```

### 8.6 State machine

```text
PENDING → POSTED → SETTLED
   ↓         ↓
 VOIDED   REVERSED (adjustment)
POSTED → HELD → POSTED | REVERSED
```

### 8.7 Fraud rule examples

| Rule | Action |
|------|--------|
| Earn > $200 / 24h new account | HELD |
| Refund ratio > 40% on promo earn | HELD + case |
| MCC in manufactured-spend list | Deny promo |
| Burst 50 clears / hour same merchant | Score↑ |

### 8.8 Glossary

| Term | Meaning |
|------|---------|
| bps | Basis points; 500 = 5% |
| PENDING | Auth-time estimate |
| POSTED | Cleared committed earn |
| Cap key | Account×promo×period balance |
| Settlement | Statement credit batch |
| MCC | Merchant Category Code |
| Clawback | Negative accrual adjustment |
| Home region | Authority for account caps |

### 8.9 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Catalog, MCC map, clear accrual, monthly cap, settle file |
| 10× | Idempotent bus, pending/auth, Amazon category join, fraud holds |
| 100× | Sharded caps, CQRS reads, recon warehouse, DLQ ops |
| 1000× | Cells, cold tier, flash admission, automated recon |

### 8.10 Publish validation checklist

- [ ] Schedule + products set  
- [ ] Caps present and tested  
- [ ] Stack policy explicit  
- [ ] Category selectors non-empty  
- [ ] Rounding mode documented  
- [ ] Golden txns pass  
- [ ] Kill switch wired  
- [ ] Legal/compliance sign-off  

### 8.11 Operator runbooks

1. Over-earn / wrong rate  
2. Cap over-grant  
3. Settlement NAK / file reject  
4. Partner feed down  
5. Category miss on Amazon.com  
6. Fraud false-positive surge  

### 8.12 Worked scale (100×)

```text
Clear ~1.8B/day → ~20K average QPS, peak ~200K
Accrual writes similar; Kafka partitions by account (≥200)
Cap updates colocated with accrual consumer affinity
Settlement 500M credits/month → range by shard parallel
```

### 8.13 Worked scale (1,000×)

```text
Peak ingest ~2M QPS → many cells; per-cell event bus
Global fantasy card counts unrealistic—scale markets independently
Flash promo: ensure per-account caps; avoid one global remaining counter
```

### 8.14 Interview “say this” summary

> Durable issuer events; category with Amazon join; versioned promos; deterministic stack; atomic caps; append-only accruals; clawbacks; idempotent settlement; never block auth; prefer delayed correct earn over fast wrong earn.

### 8.15 Explanation example JSON

```text
{
  "event_id": "c1",
  "applied": [{"promo_id":"AMZ5","version":3,"rate_bps":500,
               "gross":500,"granted":300,"reason":"CAP_HIT"}],
  "rejected": [{"promo_id":"BASE1","reason":"BEST_OF_LOST"}]
}
```

### 8.16 Security checklist

- [ ] Partner mTLS + signed payloads  
- [ ] No client-trusted earn amounts  
- [ ] Admin dual-control for high-value promos  
- [ ] PII minimization in analytics  
- [ ] Audit every publish and settle  

### 8.17 Reliability test plan

1. Duplicate clear → one accrual.  
2. Concurrent clears hitting cap → sum(granted) ≤ cap.  
3. Refund sequence restores cap / nets settle.  
4. Settlement replay → same credits.  
5. Risk hold excludes from batch.  
6. Kill switch stops new posts.

### 8.18 Idempotency matrix

| API / path | Key | Replay |
|------------|-----|--------|
| Event ingest | event_id | No-op |
| Accrual | event_id+promo_id | Same row |
| Cap reserve | event_id+cap_key | Same grant |
| Settlement item | account+cycle | Same credit |
| Enroll | account+promo | Same state |

### 8.19 Final trap table

| Trap | Pushback |
|------|----------|
| Float % earn | Rounding exploits / drift |
| Block auth on promo | Availability sin |
| Eventual caps | Overpay |
| Mutable accrual | Audit nightmare |
| MCC-only Amazon | Wrong category |
| Settle ignored holds | Fraud payout |
| 2B×1KB=2PB/day | **2TB/day** |

### 8.20 Whiteboard close

Draw **Event Log → Accrual Engine → Cap Store → Ledger → Settlement**. Walk one cap race and one refund-after-settle. Emphasize integer bps and auth isolation.

> Wrong cashback is a **finance incident**—own ledger, caps, settlement ACKs, and customer communication.

### 8.21 MCC map snippet

```text
5411 → GROCERY
5541 → GAS
5812 → DINING
5964 → CATALOG_ONLINE
AMAZON_INTERNAL → AMAZON_COM
```

### 8.22 Period ID examples

```text
monthly: 2026-08@America/Los_Angeles
daily: 2026-08-06@UTC
promo_life: PROMO#P5#WINDOW
```

### 8.23 Liability query

```text
unsettled_liability =
  sum(amount where state=POSTED and not settled)
  - sum(amount where state=REVERSED and not settled)
held_excluded_from_settle = sum(HELD)
```

### 8.24 Partner file sketch

```text
HDR BATCH=B1 CYCLE=2026-08
ROW account=A amount=4400 currency=USD idem=A|2026-08
ROW account=B amount=1200 currency=USD idem=B|2026-08
TRL count=2 total=5600
```

### 8.25 Interview timing guide

| Minute | Topic |
|--------|-------|
| 0–5 | Clarify earn timing, caps, settlement |
| 5–10 | Numbers + QPS split |
| 10–25 | HLD planes + accrual flow |
| 25–40 | Caps, refunds, fraud, settle |
| 40–45 | Scale 100×/1000× + wrap |

---

*End of Amazon SDE III prep doc: Credit-Card Cashback Promotion System.*
