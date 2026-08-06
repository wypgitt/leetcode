# System Design: Merchant Payment System

> **Focus areas:** Money correctness · Idempotency · Ledger · Payouts · Marketplace state · Exactly-once effects · Reconciliation · Fraud holds · Multi-party split (platform / merchant / courier)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split **authorization/capture** vs **ledger postings** vs **payouts**, explicit invariants, never confuse analytics GMV with cash  
> **Interview theme:** Uber — pay merchants (restaurants / earners) correctly from marketplace orders with auditable money movement

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

Goal: **bound the product**—a merchant payment system moves and accounts for money owed to merchants (and related parties) from customer charges, with **ledger-grade correctness**. It is not the restaurant metrics dashboard and not the card-network itself (though it integrates PSPs).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Merchant receivables, ledger, payouts | Consumer card UX deep dive alone |
| Truth | Double-entry ledger + payout states | Real-time analytics top-K |
| Parties | Customer, platform, merchant, optional courier | Full HR payroll |
| Provider | PSP (Stripe/Adyen-like) for rails | Rebuilding Visa |
| Scope | Eats/merchant marketplace payments | Rider–driver matching |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who gets paid? | Merchants (restaurants); optionally couriers split | Multi-party payment / transfer graph |
| F2 | When is merchant owed? | On order delivered / completed (policy) | Accrual event from order lifecycle |
| F3 | Payout cadence? | Daily / weekly / instant (fee) | Payout scheduler + balances |
| F4 | Fee model? | Platform commission % + fixed fees | Fee engine versioned |
| F5 | Refunds? | Full/partial; clawback from merchant balance/payout | Reversals in ledger |
| F6 | Chargebacks? | Hold / debit merchant; dispute workflow | Risk states |
| F7 | Currency? | Local currency per market | No silent FX mix |
| F8 | Idempotency? | Mandatory on all money APIs | Idempotency keys + ledger tx ids |
| F9 | Statements? | Merchant sees balance, payouts, order-level breakdown | Read models from ledger |
| F10 | Tax forms? | Hooks Phase 2 | Export pipelines |
| F11 | Holds? | Fraud / quality holds delay payout | Balance buckets: available vs pending vs held |
| F12 | PSP? | External; we orchestrate | Webhook authenticity + reconciliation |

**MVP functional scope (lock with interviewer):**

1. On **order completed**, compute merchant net (GMV − commission − fees ± adjustments).  
2. Post **double-entry ledger** entries (idempotent).  
3. Maintain merchant **balance** (pending → available per policy).  
4. **Payout** available balance to merchant bank via PSP on schedule or manual.  
5. **Refunds** reverse/adjust ledger; block or reduce payouts.  
6. Merchant APIs: balance, payout history, per-order earnings.  
7. Reconciliation job vs PSP settlements.  
8. Idempotent webhooks / retries safe.

**Out of MVP:**

- Full multi-clearinghouse global treasury  
- Complex marketplace loans / capital products  
- Real-time sub-penny FX engine  
- Perfect instant payout under all bank rails  
- Tax authority integrations complete

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Money correctness | No silent loss/create | Ledger invariant: Σ debits = Σ credits per tx |
| N2 | Idempotency | Retries safe | Exactly-once **effects** via keys |
| N3 | Payout latency | Schedule-accurate | Daily payout p99 start < 1h of window; instant separate SLO |
| N4 | Availability | Money APIs critical | 99.99% ledger accept; degrade reads |
| N5 | Auditability | Explain every cent | Immutable entries; append-only |
| N6 | Reconciliation | Breaks detectable | Daily < threshold unexplained |
| N7 | Security | PCI via PSP; least data | No raw PAN storage |
| N8 | Scale | See table | Shard by merchant/home cell |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Customer pays → order completes → accrue merchant net to **pending** → T+N available → payout batch → bank deposit → settled.  
2. Partial refund → ledger reversal → available reduced; if already paid out → negative balance / next payout clawback.  
3. Instant payout → fee line + transfer via PSP → ledger reflects.  
4. Merchant views statement tied to `ledger_tx_id`s / order_ids.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate complete event | Idempotent accrual key `order_id:accrual` |
| Complete never comes after capture | Ops/timeout policy; don't accrue |
| Refund after payout | Negative balance or receivable; block future payouts until recovered |
| PSP webhook duplicate | Idempotent `psp_event_id` |
| PSP payout fails | Payout state FAILED; funds remain available; retry with new attempt id |
| Split-brain double payout | Payout row CAS + PSP idempotency key |
| Chargeback | Hold + debit; dispute case |
| Currency mismatch | Reject posting |
| Clock skew | Event_time from order service; ledger uses server tx time for books |
| Merchant bank change mid-payout | Pin bank token at payout create |
| Hot flash sale restaurant | Shard-safe; no global lock |
| Recon mismatch | Alert; quarantine; no silent patch without journal |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Merchants | 100K | 1M | 10M | 100M |
| Orders accruing / day | 10M | 100M | 1B | 10B |
| Peak accrual postings / s | ~500 | ~5K | ~50K | ~500K |
| Ledger lines / day | ~50M | ~500M | ~5B | ~50B |
| Payouts / day | 100K | 1M | 10M | 50M |
| Refund events / day | 500K | 5M | 50M | 500M |
| Webhook QPS peak | ~1K | ~10K | ~50K | ~200K |
| Read QPS (balance) | ~1K | ~10K | ~50K | ~200K |

**What each jump forces:**

- **10×:** Ledger DB shards by `merchant_id`; async payout workers.  
- **100×:** Home-cell single-writer per merchant; immutable entry store + balance snapshots; recon fleets.  
- **1,000×:** Regional ledgers; hierarchical treasury; entry cold storage; payout netting batches.

### 1.5 Scope repeat-back

> Design a merchant payment system: idempotent accruals from completed orders, double-entry ledger with pending/available/held balances, scheduled and instant payouts via PSP, refunds/chargebacks, and reconciliation—money correctness over flashy dashboards—scaled by merchant home cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Accrual postings | 500/s | 500K/s | Strong consistency path |
| Refund postings | 50/s | 50K/s | Compensations |
| Payout creates | ~2/s avg (100K/day) | ~600/s | Bursty at window |
| PSP webhooks | 1K/s peak | 200K/s | Validate + idempotent |
| Balance reads | 1K/s | 200K/s | Cache with version |

**Critical insight:** Payout QPS ≪ accrual QPS, but **payout bugs are SEV-0**. Design for correctness and recon, not only throughput.

### 2.2 Ledger volume

```text
Per order accrual ≈ 4–8 journal lines (customer/platform/merchant/fees)
10M orders × 6 lines = 60M lines/day baseline
Line ~200 B ⇒ 12 GB/day raw
1,000× ⇒ 12 TB/day → cold tiering mandatory
```

### 2.3 Balance model memory

```text
Merchant balance row: pending, available, held, version ≈ 100 B
100K ≈ 10 MB; 100M ≈ 10 GB — fine if sharded
```

### 2.4 Payout batch

```text
Daily payout 100K merchants × ~1 transfer
Worker fleet: 1K payouts/s → ~100s window; need ramp + PSP rate limits
Netting: if policy allows, sum day then one transfer — reduces PSP calls
```

### 2.5 Latency budgets

```text
Accrual accept (from order event): p99 < 200–500ms durable
Balance read: p99 < 100ms (cached)
Instant payout initiate: p99 < 2s to PSP accept (not bank settle)
```

### 2.6 Bottlenecks

1. Hot merchant ledger partition  
2. Payout double-send  
3. Webhook storms  
4. Recon at 1000× volume  
5. Refund vs payout races  
6. Treating Redis counter as money  

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Order commerce events | Triggers (completed/refunded) | At-least-once delivery |
| Ledger | Authoritative money journal | Strong per merchant shard |
| Balance / buckets | Materialized from ledger or CAS co-committed | Strong |
| Payout orchestration | Transfers + state machine | Strong; PSP idempotent |
| PSP / rails | External movement | At-least-once webhooks |
| Analytics GMV | Sibling metrics | Eventual — **not money** |

**Deal-breaker:** accruing payout from metrics Redis.

### 3.2 Double-entry sketch (order complete)

Example: order $100, commission 30%, merchant net $70 (simplified).

```text
Tx accrual:order_123
  DR  Customer Clearing / PSP Receivable   100
  CR  Platform Revenue                      30
  CR  Merchant Payable                      70
```

On PSP capture confirmed (if separate):

```text
  DR  PSP Cash                              100
  CR  Customer Clearing                     100
```

On payout $70:

```text
  DR  Merchant Payable                       70
  CR  PSP Cash / Bank Out                    70
```

**Invariant:** each transaction Σ = 0; accounts typed.

### 3.3 Balance buckets

```text
pending   — accrued but not yet releasable (delivery window / risk)
available — releasable for payout
held      — fraud/quality/chargeback reserve
```

Transitions are **ledger postings**, not naked `UPDATE`.

### 3.4 State machines

**Payout:**

```text
CREATED → SUBMITTED_TO_PSP → SETTLED
                 ↘ FAILED → RETRY_WAIT → SUBMITTED...
                 ↘ CANCELLED (if not submitted)
```

**Merchant obligation (per order):**

```text
ACCRUED → PARTIALLY_REVERSED → FULLY_REVERSED
ACCRUED → PAID_OUT (via allocation in payout)
```

### 3.5 Idempotency strategy

| Operation | Key |
|-----------|-----|
| Accrue order | `accrual:{order_id}` |
| Refund | `refund:{refund_id}` |
| Create payout | `payout:{merchant_id}:{period}` or client key |
| PSP transfer | `Idempotency-Key` to PSP = `payout_attempt_id` |
| Webhook | `psp_event_id` unique |

### 3.6 Options: balance vs event-sourced ledger

| Option | Pros | Cons | When |
|--------|------|------|------|
| A. Ledger append + snap balance | Auditable | More moving parts | **Default money systems** |
| B. Balance CAS only | Simple | Weak audit | Never for MVP money at Uber scale |
| C. External PSP balances only | Less build | Poor multi-party / holds | Insufficient |

**Chosen:** append-only ledger entries + strongly consistent balance snapshot per merchant (same DB tx / same shard).

### 3.7 Payout scheduling

```text
cron/materializer: for each merchant due:
  amount = available (respect min threshold)
  create payout row CAS (period unique)
  enqueue worker
worker:
  freeze amount (move available → payout_in_flight via ledger)
  call PSP with idempotency key
  on success webhook/settle → finalize
```

**Netting window:** one payout per merchant per period reduces risk surface.

### 3.8 Refund vs in-flight payout race

```text
Serialize on merchant shard lock / row version:
- Refund posting checks payout_in_flight
- Policy: allow negative available OR block refund confirmation until adjusted
- Never both ignore the other
```

### 3.9 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| SoR | Ledger DB | Audit | Kafka as money SoR |
| Shard key | merchant_id | Localize balance | Shard by order only (cross-post pain) |
| PSP | External | PCI / rails | Store PAN |
| Instant payout | Separate product fee | Risk | Same path as daily without holds |
| Multi-region | Home cell writer | No dual spend | Active-active balance writers |
| Analytics | Async replica | Don't block ledger | Sync ES on every posting |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Order / Refund Services
        | (outbox events)
        v
+------------------+
| Accrual Workers  | --idempotent--> Ledger Service
+------------------+                    |
                                        v
                              +-------------------+
                              | Ledger Store      |
                              | entries+balances  |
                              | (shard by merch)  |
                              +---------+---------+
                                        |
           +----------------------------+----------------------------+
           v                            v                            v
   Merchant Read API              Payout Scheduler              Risk/Holds
   (balance/statements)                 |
                                        v
                                 Payout Workers ---> PSP (Transfer API)
                                        ^                |
                                        |                v
                                        +---------- Webhooks
                                        |
                                        v
                                   Recon Jobs <--> PSP Settlement Reports
```

### 4.2 Sequence: accrual

```text
OrderCompleted -> AccrualWorker
  key = accrual:order_id
  begin tx on merchant shard:
    if key exists: return prior result
    insert ledger lines
    update pending += net
    write idempotency row
  commit
```

### 4.3 Sequence: payout

```text
Scheduler -> create payout(merchant, period, amount) unique
Worker -> ledger: available -> in_flight
Worker -> PSP.transfer(idempotency=attempt_id)
Webhook SETTLED -> ledger: in_flight clear to cash out
Webhook FAILED -> ledger: in_flight -> available; payout FAILED
```

### 4.4 Sequence: refund after payout

```text
Refund -> post DR Merchant Receivable / CR Refund liability etc.
Balance available may go negative
Next payout blocked until available >= min OR collections flow
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Double-entry** every transaction.  
2. **Idempotent** money effects.  
3. **Append-only** entries (corrections = new reversing entries).  
4. **Single-writer home cell** per merchant.  
5. **Payout uniqueness** per period / attempt fencing.  
6. **PSP idempotency keys** never reused for different amounts.  
7. **Webhook signatures** verified.  
8. **Reconciliation** closes books; unexplained breaks page humans.  
9. **No naked balance mutate** without ledger tx.  
10. Currency consistent per posting.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG ledger schema; workers; daily payout |
| 10× | Shard by merchant hash; outbox consumers |
| 100× | Cells by region; entry archival; payout netting; read replicas for statements |
| 1000× | Hierarchical treasury accounts; streaming recon; cold object store for entries |

### 5.3 Maintainability

- Versioned **fee contracts** (`fee_schedule_id` on accrual).  
- Ledger account catalog as data.  
- Immersive audit UI for support.  
- Game-day: duplicate webhook, double complete, payout retry.  
- Feature flags for instant payout markets.

### 5.4 Progressive scale

**1×:** One region PG; Stripe-like PSP; nightly payout.  
**10×:** Merchant shards; CQRS statement projections.  
**100×:** Entry partitions by month; freeze old periods.  
**1000×:** Multi-region cells; central treasury netting across cells carefully (avoid dual writers).

### 5.5 Exactly-once effects pattern

```text
at-least-once event + durable idempotency record + transactional ledger write
= exactly-once business effect
```

Do not claim transport exactly-once alone.

### 5.6 Holds & risk

```text
Risk service recommends hold_amount
Ledger: DR available/pending, CR held (or pending→held)
Release: reverse
```

Never "bool flag" without amount tracking.

### 5.7 Reconciliation

```text
Daily:
  Σ ledger PSP Cash movements
  vs PSP settlement file Σ
  vs payout SETTLED Σ
Break → ticket with amount, sample ids, owner on-call
```

### 5.8 Fee engine

```text
net = f(order_snapshot, fee_schedule_id, promotions)
store inputs + schedule version on accrual for recompute disputes
```

### 5.9 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Redis INCR balance | Lost audit / races |
| Kafka as ledger SoR | Hard invariants |
| Reuse PSP idempotency key with new amount | Wrong pay |
| Active-active multi-writer balances | Double payout |
| Silent recon "adjustment" without journal | Fraud / chaos |
| Accrue from CREATED not COMPLETED (wrong policy silent) | Pay undelivered |

---

## 6. Wrap-Up

### 6.1 Designed

Merchant payments with double-entry ledger, bucketed balances, idempotent accruals/refunds, payout state machine via PSP, holds, and reconciliation—sharded by merchant home cell.

### 6.2 Decisions to defend

1. Ledger SoR + balance snapshot  
2. Idempotency keys everywhere  
3. Payout attempt fencing + PSP keys  
4. Pending/available/held buckets  
5. Compensating entries for refunds  
6. Home-cell single-writer  
7. Recon as first-class  
8. Analytics GMV out of band  

### 6.3 Risks

- Refund after instant payout  
- PSP ambiguity (pending states)  
- Fee schedule bugs (systematic under/over pay)  
- Hot merchants  
- Operational recon debt  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Money invariants vs analytics |
| 5–15 | Ledger + buckets + accrual |
| 15–30 | Payout SM + idempotency + refunds |
| 30–40 | Recon, holds, PSP webhooks |
| 40–45 | Scale cells / deal-breakers |

### 6.5 Closer

> **Merchant payments**: double-entry, idempotent effects, bucketed balances, fenced payouts, recon—correctness first, sharded by merchant, never powered by dashboard counters.

---

## 7. Deeper / Related Interview Questions

### 7.1 Ledger theory

**Q: Why double-entry?**  
A: Conservation of money in-system; every source has destination; audit.

**Q: Can we update balances without lines?**  
A: Not for this domain—regulators/support need trails.

**Q: Mutable entry fix?**  
A: Never edit; post reversal + new entry.

### 7.2 Idempotency

**Q: Exactly-once payout?**  
A: DB unique payout period + PSP idempotency key + CAS state.

**Q: At-least-once webhook?**  
A: Store `psp_event_id`; processing transactional with state transition.

### 7.3 Consistency

**Q: Read your balance after accrual?**  
A: Read from home cell / primary; cache with version invalidate.

**Q: Cross-merchant transfer?**  
A: Two-shard saga with clearing account; avoid 2PC when possible via platform clearing.

### 7.4 Refunds & chargebacks

**Q: Partial refund accounting?**  
A: Proportional fee clawback policy explicit; post precise lines.

**Q: Chargeback won/lost?**  
A: Separate dispute SM; final ledger posts on outcome.

### 7.5 Payout rails

**Q: Instant vs standard?**  
A: Different PSP products/fees/risk; separate attempt types.

**Q: Bank account verification?**  
A: Micro-deposits / PSP verified tokens before first payout.

### 7.6 Geo / multi-region

**Q: Merchant moves market?**  
A: Rare; migrate home cell with freeze window.

**Q: FX?**  
A: Keep book in market currency; treasury FX separate.

### 7.7 Caches & queues

**Q: Cache balances?**  
A: Yes with `version`; never cache as SoR.  
**Q: Queue for accruals?**  
A: Kafka outbox consumer; still idempotent DB.

### 7.8 Fraud

**Q: Collusive refunds?**  
A: Holds, velocity limits, risk scores delaying available.

**Q: Insider threat?**  
A: Dual control for manual adjustments; audit log.

### 7.9 Algorithms / structures

**Q: Shard map?**  
A: Consistent hash `merchant_id` → cell/shard; sticky.

**Q: Statement generation?**  
A: Period query of entries or pre-aggregated statement table nightly.

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| "Just use Stripe Connect and no ledger" | Still need platform books/holds/multi-party |
| Floating point money | Use integer cents |
| Global serial queue for all payouts | Won't scale; also bad isolation |
| Metrics GMV triggers payout | Wrong plane |
| Delete failed payout row | Breaks audit |

### 7.11 Metrics / SLOs

| Metric | Why |
|--------|-----|
| Ledger posting success | Health |
| Idempotent hit rate | Retry behavior |
| Payout fail rate | Rails |
| Recon break amount | Money risk |
| Time to available | Merchant UX |
| Negative balance count | Collections |
| Dual-payout incidents | Must be 0 |

### 7.12 Comparison

**Q: vs consumer payments product API?**  
A: Sibling—consumer authorize/capture; this doc focuses merchant side & payouts.

**Q: vs restaurant metrics?**  
A: Metrics approximate/analytics; this is cash.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
ledger_accounts(
  account_id, merchant_id NULL, type, currency)

ledger_transactions(
  tx_id UUID PK,
  idempotency_key TEXT UNIQUE,
  tx_type TEXT, -- ACCRUAL/REFUND/PAYOUT/HOLD...
  ref_type TEXT, ref_id TEXT,
  created_at)

ledger_entries(
  entry_id UUID PK,
  tx_id UUID,
  account_id,
  amount_cents BIGINT, -- signed or direction enum
  direction TEXT, -- DR/CR
  currency CHAR(3))

merchant_balances(
  merchant_id UUID PK,
  currency CHAR(3),
  pending_cents BIGINT,
  available_cents BIGINT,
  held_cents BIGINT,
  in_flight_payout_cents BIGINT,
  version BIGINT)

payouts(
  payout_id UUID PK,
  merchant_id,
  period_id TEXT,
  amount_cents BIGINT,
  state TEXT,
  psp_transfer_id TEXT NULL,
  attempt INT,
  idempotency_key TEXT UNIQUE,
  UNIQUE(merchant_id, period_id, attempt) -- policy dependent
)

idempotency_keys(
  key TEXT PRIMARY KEY,
  response_ref TEXT,
  created_at)
```

### 8.2 API checklist

- [ ] `GET /merchants/{id}/balances`  
- [ ] `GET /merchants/{id}/ledger?cursor=`  
- [ ] `GET /merchants/{id}/payouts`  
- [ ] `POST /merchants/{id}/payouts/instant` + Idempotency-Key  
- [ ] Internal: accrue/refund commands (from workers)  
- [ ] Webhook `/psp/webhooks`  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Accrual | Recognize merchant earnings |
| Double-entry | DR/CR balanced transaction |
| Available | Eligible to pay out |
| Hold | Risk-restricted funds |
| Recon | Match books to PSP |
| Home cell | Single-writer region/shard for merchant |
| Clawback | Recover funds after refund/chargeback |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Ledger+balances, idempotency, daily payout, recon |
| 10× | Shards, statement projections |
| 100× | Cells, archival, risk holds automation |
| 1000× | Regional ledgers, netting, streaming recon |

### 8.5 Fee schedule sketch

```json
{
  "fee_schedule_id": "eats_us_v3",
  "commission_bps": 3000,
  "flat_cents": 0,
  "instant_payout_fee_bps": 150
}
```

### 8.6 Interview “say this” (60s)

> Merchant payments are a **ledger problem**: idempotent accruals from completed orders, double-entry with pending/available/held, fenced payouts using PSP idempotency, compensating refunds, and daily reconciliation. Shard by merchant home cell; never pay from analytics counters; never mutate balances without journal lines.

### 8.7 Reliability test plan

1. Duplicate order complete → one accrual.  
2. Duplicate payout worker → one PSP transfer.  
3. Duplicate webhook → one settle.  
4. Refund after payout → negative/block.  
5. PSP fail → funds restored available.  
6. Recon synthetic break → alert.  
7. Home cell failover → epoch fence; no double pay.

### 8.8 Related systems map

```text
Orders → Accrual → Ledger/Balances → Payouts → PSP → Bank
                      ↓
                 Statements API
                      ↓
                   Recon
Analytics Metrics (sibling) — parallel, non-authoritative
```

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| FLOAT dollars | Use cents INT |
| Soft delete payout | Audit fail |
| Shared mutable "wallet" row without version | Lost update |
| Weekend skip recon | Breaks accumulate |

### 8.10 Unit checks

```text
10M orders/day × 6 lines = 60M lines/day
100K payouts/day ≈ 1.16/s avg — bursty at 00:00 local
```

### 8.11 Manual adjustment protocol

```text
require dual_approval
post ADJUSTMENT tx with reason_code + ticket_id
never edit historical entries
```

### 8.12 Instant payout extra controls

- Higher fee  
- Min account age  
- Max velocity / day  
- Risk score gate  
- Same idempotency + ledger in_flight pattern  

### 8.13 Multi-party split example (Eats)

Order $100 food, $5 delivery fee, $8 tip to courier, 30% commission on food:

```text
Customer charge total = 100 + 5 + 8 = 113 (simplified)

Accrual tx:
  DR PSP Receivable                 113
  CR Merchant Payable                70   # 100 - 30 commission
  CR Platform Commission Revenue     30
  CR Platform Delivery Revenue        5   # or courier pass-through policy
  CR Courier Payable                  8   # tip
```

Courier payouts may be a **sibling earner-payment** system sharing ledger patterns; say so in interview—don't invent two incompatible money models.

### 8.14 Payout allocation to orders

Merchants want "which orders paid in this deposit?":

```text
When creating payout of amount A from available:
  select accrued order obligations FIFO / by available_at
  mark allocation rows (payout_id, order_id, amount)
  statement join via allocations
```

Allocations are **derived bookkeeping**, still backed by ledger totals.

### 8.15 Webhook authenticity

```text
verify HMAC signature with PSP secret
reject skew > N minutes (replay window)
idempotent upsert by psp_event_id
never trust client-supplied settle without signature
```

### 8.16 Negative balance state machine

```text
AVAILABLE >= 0 → normal
AVAILABLE < 0 → COLLECTIONS
  - block instant payout
  - allow standard payout only if net positive after period (policy)
  - dunning notifications
  - optional reserve % on future accruals → held until recovered
```

### 8.17 Observability dashboards (money)

| Panel | Signal |
|-------|--------|
| Accrual lag | order complete → ledger tx time |
| Payout success % | by rail / country |
| Recon break $ | absolute + bps of volume |
| Idempotent retries | hit rate |
| Held balance total | risk exposure |
| Instant payout velocity | fraud |

### 8.18 Interview closer card

| Say | Don't say |
|-----|-----------|
| Integer cents + double-entry | "Redis wallet++" |
| Idempotency + PSP keys | "Kafka exactly-once payouts" |
| Home-cell merchant writer | "Multi-master balance" |
| Recon closes the loop | "Trust PSP UI" |
| Analytics ≠ books | "Pay from GMV dashboard" |

---

*End of merchant payment system design.*
