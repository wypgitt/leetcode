# System Design: Phone Billing System

> **Focus areas:** CDR ingestion · Mediation · Rating · Invoicing · Usage caps / throttles · Optional realtime balance · Disputes · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct money + usage invariants, split ingest vs rate vs invoice planes, idempotent CDR keys, explicit late-CDR and timezone policy  
> **Amazon lens:** Reliability/ownership of billing correctness, cost of mediation at scale, practical trade-offs on realtime vs batch, customer-trust on invoices

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

Goal: **bound a telecom-style phone billing system**—ingest call/SMS/data usage records (CDRs), mediate/normalize them, rate against plans and promotions, enforce usage caps, produce invoices, optionally maintain near-realtime balances—without double-billing or silent free usage.

### 1.0 What this is / is not

| Dimension | **Phone billing (this doc)** | Not this |
|-----------|------------------------------|----------|
| Primary job | CDR -> rate -> invoice/collect | Radio access network / switching fabric |
| Success | Correct bills; enforceable caps; reconcilable | Pretty usage graphs alone |
| SoT usage | Append-only CDR + rated usage ledger | Mutable "minutes_left" without log |
| SoT money | Invoice + payment ledger | PSP dashboard alone |
| Realtime balance | Optional enhancement | Hard requirement for MVP unless asked |
| Amazon lens | Metering correctness, ownership, cost | Building a full MVNO core network |

**Scope statement:** Design phone billing: durable CDR ingestion, mediation, rating, invoicing, usage caps, optional realtime balance, disputes/adjustments—from baseline through 10x / 100x / 1,000x CDR volume.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is billed? | Voice minutes, SMS, data MB/GB; maybe roaming | Usage dimensions + unit converters |
| F2 | Who is customer? | Subscriber / account with lines (MSISDN) | account_id vs line_id |
| F3 | Plans? | Unlimited / buckets / pay-as-you-go / tiers | Plan catalog + entitlements |
| F4 | CDR sources? | Switch, SMSC, GGSN/PGW, partners | Multi-source mediation |
| F5 | Duplicate CDRs? | Retries and multi-leg common | Idempotent CDR keys |
| F6 | Late CDRs? | Hours–days late (roaming) | Reopenable billing periods / adjustments |
| F7 | Rating when? | Near-RT for balance; batch OK for invoice | Dual path optional |
| F8 | Invoices? | Monthly cycle + prorate on plan change | Invoice state machine |
| F9 | Caps? | Soft warn + hard block / throttle | Online policy enforcement hook |
| F10 | Realtime balance? | Optional prepaid / soft prepaid hybrid | Balance service + reservation |
| F11 | Taxes / fees? | Hook tax engine; regulatory fees | Tax at invoice finalize |
| F12 | Disputes? | Adjustments with audit | Credit notes |
| F13 | Roaming? | Partner TAP/RAP files delayed | Late event pipeline |
| F14 | Multi-line family? | Shared data pool | Pool entitlements |
| F15 | Payments? | Card/ACH via PSP; prepaid top-up | Dunning + top-up APIs |

**MVP functional scope:**

1. Ingest CDRs (voice/SMS/data) with idempotent IDs.  
2. Mediation: normalize, validate, enrich (plan, account).  
3. Rating engine: apply plan rates, buckets, promos.  
4. Usage ledger append-only rated records.  
5. Monthly invoicing with line items + tax hook.  
6. Usage caps (per line / account / pool) with soft/hard modes.  
7. Customer usage & invoice read APIs.  
8. Adjustments / dispute credits.  
9. Optional: near-realtime balance for prepaid-like plans.  
10. Metrics, DLQ, recon reports.

**Out of MVP:**

- Full 3GPP online charging system (OCS) feature parity  
- Lawful intercept  
- Building HLR/HSS  
- Perfect real-time roaming worldwide day-1  
- Cryptocurrency top-ups  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | CDR durability after ACK | No loss | WAL/log replicated; RPO~0 |
| N2 | Ingest lag | Seconds typical | p99 mediate < few seconds domestic |
| N3 | Rating correctness | No double rate | Idempotent rate keys |
| N4 | Invoice correctness | Finance-grade | Deterministic from ledger snapshot |
| N5 | Cap enforcement latency | Optional online | p99 < 20–50ms if on call path |
| N6 | Availability | Ingest > fancy UI | Buffer at edge; degrade RT balance |
| N7 | Late CDR policy | Explicit | Adjust next invoice or reopen |
| N8 | Scale | Progressive table | Partition by account/line |
| N9 | Audit | Immutable rated usage | Append-only |
| N10 | Security | Subscriber PII | Encrypt MSISDN at rest where needed |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Domestic call CDR -> mediate -> rate from bucket -> decrement entitlement -> appear in usage -> month invoice.  
2. SMS pay-as-you-go -> rate $0.05 -> invoice line.  
3. Data session multiple interim CDRs + terminate -> aggregate session -> rate once on volume.  
4. Shared family data pool depletes -> soft warn then throttle.  
5. Prepaid optional: reserve balance on session start; settle on end.  
6. Dispute wrong roaming charge -> credit adjustment -> next invoice.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate CDR delivery | Same cdr_id -> one rated row |
| Out-of-order interim/terminate | Session stitcher; rate on complete or timeout |
| Late roaming CDR after invoice | Adjustment / reopen policy |
| Timezone / DST on period boundary | Account billing TZ; period_id absolute |
| Plan change mid-cycle | Proration policy explicit |
| Unlimited plan fair-use | Soft throttle after threshold |
| Zero-duration calls | Filter / minimum charge policy |
| Clock skew from switch | Quarantine beyond skew |
| Partial payment | Dunning; suspend data? product call |
| Multi-leg call (transfer) | Mediation correlation |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10x | 100x | 1,000x |
|--------|----------|-----|------|--------|
| Subscribers | 5M | 50M | 500M | 5B |
| Lines | 6M | 60M | 600M | 6B |
| CDRs / day | 200M | 2B | 20B | 200B |
| Peak CDR ingest QPS | ~10K | ~100K | ~1M | ~10M |
| Rated usage writes / day | ~150M | 1.5B | 15B | 150B |
| Invoices / month | 5M | 50M | 500M | 5B |
| Balance checks QPS (optional) | 5K | 50K | 500K | 5M |
| Cap / entitlement checks QPS | 5K | 50K | 500K | 5M |
| Dispute cases / day | 5K | 50K | 500K | 5M |

**What each jump forces:**

- **10x:** Kafka partitions; mediation fleet; rating horizontal scale; entitlement Redis/Dynamo.  
- **100x:** Account cells; session stitch state sharded; invoice parallelism; cold CDR lake.  
- **1,000x:** Regional billing cells; sampling for analytics; OCS-lite colocated; partner file factories.

### 1.5 Etc. (Constraints & Assumptions)

- Network elements ACK only after durable ingest (or local buffer with replay).  
- Money and rated amounts in **integer minor units**; data in bytes then billable quanta.  
- Prefer **delay invoice** over wrong invoice when ledger lag detected.  
- Online enforcement (caps) is a **separate low-latency path** from monthly invoice correctness.  
- Amazon interview: show you won't lose CDRs and won't double-bill.

**Scope statement:**

> Phone billing: idempotent CDR ingest, mediation, rating, usage ledger, caps, monthly invoices, optional realtime balance—from ~10K CDR/s through 1,000x (~10M/s), failing closed on money ambiguity.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000x | Notes |
|-------|---------------|--------|-------|
| Raw CDR ingest | 10K | 10M | Highest volume |
| Mediation | 10K | 10M | CPU + enrich |
| Rating | 8K | 8M | After filter/merge |
| Entitlement / cap update | 5K | 5M | Hot path optional |
| Balance reserve (prepaid) | 2K | 2M | Optional |
| Invoice generation | batch | batch | Monthly spike |
| Customer usage read | 1K | 1M | Cache |
| Admin / plan publish | 1 | 100 | Config |

**Critical:** CDR ingest >> invoice. Never couple monthly invoice locks to ingest. Session stitch state can hotspot busy lines.

### 2.2 Storage

```text
CDR raw ~300–800 B average after compress ~200 B
200M/day * 400 B = 80 GB/day baseline raw
100x: 20B * 400 B = 8 TB/day -> columnar lake + lifecycle

Rated usage ~150–300 B
Invoice ~2–5 KB + line items
5M invoices/month * 5 KB = 25 GB/month baseline metadata (small)
```

### 2.3 Data session math

```text
Heavy data user: many interim CDRs (every 5–15 min)
Stitch to session_id; rate on bytes_delta to avoid double count
Example: 100 interims * 1 MB = 100 MB -> one logical usage stream
```

### 2.4 Rating CPU

```text
Simple rate: O(1) plan lookup + bucket decrement
10K CDR/s * 0.2 ms = 2K cores-ms/s -> tens of cores with headroom
1M CDR/s -> need careful batching, local caches, partition affinity
```

### 2.5 Critical bottlenecks

1. Hot subscriber shared pool updates  
2. Duplicate storm from misbehaving network element  
3. Late roaming file dump (billions)  
4. Invoice month-end thundering herd  
5. Realtime balance consistency vs throughput  
6. Quarantine poison CDRs blocking partition  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Account (account_id, billing_tz, status, payment_method)
Line (line_id, account_id, msisdn, status)
Plan (plan_id, version, rates, buckets, caps, fair_use)
Subscription (line_id, plan_id, version, start, end)
CDR (cdr_id, type=VOICE|SMS|DATA, line_id, start, end, bytes, peers, ...)
Session (session_id, line_id, aggregates)  -- data/voice multi-part
RatedUsage (usage_id, cdr_id/session_id, account_id, amount_cents, units, plan_version)
Entitlement (account_or_line_or_pool, dimension, remaining, period)
Invoice (invoice_id, account_id, period_id, status, totals)
InvoiceLine (invoice_id, description, amount_cents, usage_refs)
Adjustment (adj_id, account_id, amount_cents, reason)
Balance (account_id, cents)  -- optional prepaid
Reservation (reservation_id, session_id, amount_cents, expires)
```

### 3.2 Planes

```text
1. Ingest plane       - durable CDR log
2. Mediation plane    - validate, normalize, session stitch
3. Rating plane       - price + bucket consume
4. Entitlement plane  - caps / pools (online + batch)
5. Invoice plane      - cycle close, tax, PDF/API
6. Balance plane      - optional prepaid reserve/settle
7. Control plane      - plans, publish, kill switches
8. Dispute plane      - adjustments, cases
```

### 3.3 CDR identity & idempotency

```text
cdr_id = network_element_id + record_seq + record_type + event_time_bucket
  OR vendor unique id if present
UNIQUE constraint on cdr_id in raw store
RatedUsage UNIQUE(cdr_id) or UNIQUE(session_id, quantum_index)
```

### 3.4 Mediation

```text
Steps:
  1. Schema validate / version
  2. Normalize units (bytes, seconds)
  3. Map MSISDN -> line_id -> account_id
  4. Filter zero/noise per policy
  5. Session stitch for DATA/VOICE multi-part
  6. Enrich roaming indicators
  7. Emit MediatedUsageEvent
Quarantine: bad schema, unknown MSISDN, skew
```

### 3.5 Rating

```text
function rate(mediated):
  sub = subscription_at(mediated.line_id, mediated.event_time)
  plan = load(sub.plan_id, sub.version)  // pin version
  units = to_billable_quanta(mediated)
  // consume buckets first
  from_bucket, remainder = entitlements.consume(pool_key, dimension, units)
  amount = price(remainder, plan.rates) + price_roaming(...)
  write RatedUsage(amount, units, plan.version, explain)
```

**Rounding:** always define quantum (e.g., per-second vs 60-second rounding). Integer cents.

### 3.6 Usage caps & enforcement

| Mode | Behavior |
|------|----------|
| Soft | Notify; continue |
| Throttle | Signal policy to PCEF/network (hook) |
| Hard | Deny new sessions / block SMS via policy response |

```text
Online path (optional):
  network -> Cap/Balance API: allow?
  API checks entitlement remaining + account status
  returns allow / deny / throttle_profile
Offline path:
  rating still records usage; invoice includes overage
```

**Deal-breaker:** claiming hard caps without an online enforcement hook (or accepting post-facto overage only—say it explicitly).

### 3.7 Optional realtime balance (prepaid / hybrid)

```text
Session start:
  estimate = max_cost_or_min_reserve
  reservation = balance.reserve(account, estimate, ttl)
  if fail -> deny
Session updates:
  top-up reservation if needed
Session end / timeout:
  settle actual cost; release unused
Postpaid:
  balance plane unused; credit limit optional analogous
```

### 3.8 Invoicing

```text
On cycle close (account.billing_tz):
  1. Freeze period_id
  2. Aggregate RatedUsage unsettle + Adjustments
  3. Apply recurring charges / credits
  4. Tax quote
  5. Create Invoice DRAFT -> FINALIZE
  6. Collect via PSP / apply prepaid
  7. Mark usage INVOICED
Late CDR policy:
  A) next cycle adjustment (simpler)
  B) reopen invoice if within grace (complex)
Pick A for MVP; mention B.
```

### 3.9 Shared pools

```text
Pool entitlement key: account_id + dimension + period
Lines consume from pool atomically
Cap UX: show pool remaining to all members
Hot account with many lines: shard remaining with reconciler OR single-row CAS with retries
```

### 3.10 Storage trade-offs

| Store | Role |
|-------|------|
| Kafka | CDR spine |
| S3/lake | Raw CDR archive |
| Cassandra/Dynamo | Entitlements, balance, session stitch |
| Postgres | Plans, invoices, accounts |
| Warehouse | Recon, analytics |
| Redis | Hot plan cache, read models |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[MSC/SMSF/PGW] [Roaming TAP files] [Partner CDRs]
        \              |               /
         v             v              v
              CDR Ingest Gateway
                     |
                     v
               Durable CDR Log
                     |
         +-----------+-----------+
         v                       v
   Mediation Workers      Quarantine/DLQ Ops
         |
         v
   Session Stitcher
         |
         v
    Rating Engine -----> Entitlement / Cap Service
         |                        |
         v                        v
   Rated Usage Ledger      (optional) Balance Service
         |
         +------> Invoice Worker --> Tax --> PSP
         |
         +------> Usage Read APIs (customer)
```

### 4.2 Online enforcement (optional)

```text
Network PCEF/SCF --> Cap/Balance API --> allow/deny/throttle
                         |
                         +--> async CDR still arrives later for rating recon
```

### 4.3 Month-end invoice

```text
Scheduler --> per account_shard close(period)
  snapshot usage --> aggregate --> tax --> finalize --> collect
  emit invoice PDF/API --> notify
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Same `cdr_id` never rated twice.  
2. Sum of bucket consume + overage units = billable units (within quantum rules).  
3. Invoice totals = sum(invoice lines) including tax lines per rules.  
4. Balance reservations never allow spend > balance (prepaid).  
5. Plan version pinned at rating time.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Ingest crash | Producer retry; idempotent cdr_id |
| Mediation poison | Quarantine; don't block forever without head-of-line strategy |
| Entitlement CAS conflict | Retry; deterministic |
| Invoice job partial | Restartable by account shard; idempotent invoice_id |
| Late CDR | Adjustment path |
| Balance reserve leak | TTL reaper |

**Degradation:** If balance service down for prepaid -> fail closed (deny) or limited grace—**product call, say aloud**. Postpaid rating continues from log even if read API down.

### 5.2 Scalability

| Scale | Tactic |
|-------|--------|
| 10x | Partition by line_id/account_id; cache plans; batch rating |
| 100x | Cells; lake tiering; invoice map-reduce by shard |
| 1000x | Regional billing; OCS-lite colocation; partner file parallel ingress |

**Hot pools:** family accounts with viral data usage—single entitlement row—use atomic add with high retry or hierarchical local quotas + reconcile.

**Month-end:** stagger closes by billing_day (1–28) to avoid 1st-of-month herd.

### 5.3 Maintainability

**Ownership:** Ingest/Mediation, Rating/Plans, Entitlements, Invoicing/Payments, Balance/OCS-lite, Disputes.

**Config:** Plan versions immutable; publish with simulation on golden CDR sets.

**Observability:** ingest lag, quarantine rate, duplicate rate, rating $/min, entitlement errors, invoice break vs payments, balance reservation leak.

**Testing:** golden CDR fixtures; duplicate/out-of-order; late roaming; proration; property test: no negative entitlements.

---

## 6. Wrap-Up

### 6.1 MVP build order

1. CDR ingest + idempotent store  
2. Mediation normalize + MSISDN map  
3. Plan catalog versions  
4. Rating + usage ledger  
5. Entitlements/buckets  
6. Monthly invoice  
7. Caps soft/hard hooks  
8. Adjustments  
9. Optional balance reserve/settle  
10. Customer usage APIs  

### 6.2 Trade-offs

| Choice | Trade-off |
|--------|-----------|
| Batch invoice vs RT balance | Simpler money close vs prepaid UX |
| Late CDR next cycle | Customer confusion vs ops simplicity |
| Quantum rounding | Revenue vs fairness perception |
| Fail-closed prepaid | Availability vs leakage |

### 6.3 Risks

1. Double rating from session stitch bugs.  
2. Entitlement drift vs rated usage.  
3. Month-end performance incident.  
4. Roaming file format changes.  
5. Online deny false positives (angry customers).

### 6.4 60-second pitch

> Durable idempotent CDR log, mediation with session stitching, versioned plan rating into an append-only usage ledger, atomic entitlements for buckets/caps, monthly invoices from ledger snapshots with tax hooks, adjustments for late/dispute CDRs, optional prepaid reservations. Scale by account partitioning; stagger billing days; never lose acked CDRs; never double-rate.

---

## 7. Deeper / Related Interview Questions

### 7.1 CDR & mediation

**Q: What is a CDR?**  
A: Call/Session Detail Record—usage event from network elements.

**Q: Interim vs terminate?**  
A: Partial updates vs final; stitch by session_id.

**Q: How to dedupe?**  
A: Stable cdr_id unique index; for files use row hashes.

**Q: Unknown MSISDN?**  
A: Quarantine; try enrich retries; eventually orphan report.

### 7.2 Rating

**Q: Bucket then overage?**  
A: Yes typical; explain on invoice.

**Q: Peak/off-peak?**  
A: Rate tables by local time in account TZ.

**Q: Rounding 60s?**  
A: Policy; document; integer arithmetic.

**Q: Promo "first 100 SMS free"?**  
A: Entitlement dimension SMS; consume first.

### 7.3 Caps

**Q: Soft vs hard?**  
A: Soft notify; hard needs online path.

**Q: Fair use on unlimited?**  
A: Threshold then throttle profile; still may rate $0.

**Q: Race two sessions depleting pool?**  
A: Atomic consume; one gets remainder.

### 7.4 Realtime balance

**Q: Why reservations?**  
A: Concurrent sessions; avoid overspend.

**Q: Reservation TTL?**  
A: Network crash safety; reaper releases.

**Q: Postpaid credit limit?**  
A: Analogous to balance with credit ceiling.

### 7.5 Invoicing

**Q: Proration?**  
A: Daily fraction or remaining entitlement transfer—pick one.

**Q: Tax?**  
A: External tax engine at finalize; store tax lines.

**Q: Idempotent finalize?**  
A: invoice_id = account+period unique.

**Q: Reopen vs adjust?**  
A: MVP adjust next cycle.

### 7.6 Roaming / partners

**Q: TAP files?**  
A: Batch ingest adapter; same mediation after normalize.

**Q: Huge late dump?**  
A: Backpressure; priority queues; customer comms if bill shock.

### 7.7 Disputes

**Q: Evidence?**  
A: Raw CDR refs + rated explain.

**Q: Partial credit?**  
A: Adjustment ledger; never rewrite rated rows (or mark void + replace).

### 7.8 Estimation traps

**Q: 20B CDRs * 400B = 8PB/day?**  
A: 20B*400=8e12 B = **8 TB/day**.

**Q: Invoice every CDR in OLTP join?**  
A: Aggregate from ledger / warehouse; don't N+1.

### 7.9 Interview traps

**Q: "Just UPDATE minutes_left."**  
A: Ledger + entitlement derived/atomic consume with audit.

**Q: "Float for money."**  
A: Integer cents.

**Q: "Realtime balance required for all postpaid."**  
A: Optional; postpaid invoices from ledger sufficient.

**Q: "Lose some CDRs OK."**  
A: Not after ACK—revenue leakage.

**Q: "One global invoice job on 1st."**  
A: Stagger billing_day; shard.

### 7.10 Ownership scenarios

**Q: Sev: double-billed SMS for 2M users.**  
A: Stop invoices; detect dup rate keys; credit; fix stitch/dedupe; customer notify.

**Q: Cap not enforced; bill shock.**  
A: Check online path; soft vs hard config; goodwill credits.

**Q: Month-end job 12h late.**  
A: Parallelize shards; pre-aggregate nightly; communicate.

### 7.11 Comparisons

**Q: vs AI subscription billing?**  
A: Similar meter/invoice; telco adds CDR mediation, roaming latency, online caps.

**Q: vs cashback promo system?**  
A: Cashback is rewards on card txns; phone billing is usage metering + invoices.

### 7.12 Misc deep cuts

**Q: Number portability?** A: Line history; rate by line_id at event_time.  
**Q: Multi-currency?** A: Account currency; roaming FX tables versioned.  
**Q: Lawful retention?** A: Separate compliance store; billing keeps aggregates.  
**Q: eSIM lifecycle?** A: Line provision events to billing.  
**Q: Zero-rate apps?** A: Rating exemptions by APN/service-id.  
**Q: VoLTE vs CSFB?** A: Mediation normalizes; billing shouldn't care.  
**Q: Testing at 1M QPS?** A: Shadow traffic; replay lake.  
**Q: Clock history?** A: Store switch event_time + ingest_time.  
**Q: Bundle SMS+data?** A: Multi-dimension entitlements.  
**Q: Kill switch?** A: Pause invoicing; pause online deny (fail open/closed config).

---

## 8. Appendices

### 8.1 Schema sketches

```text
accounts(account_id, billing_tz, billing_day, status, currency)
lines(line_id, account_id, msisdn_hash, status)
plans(plan_id, status)
plan_versions(plan_id, version, rates_json, buckets_json, caps_json, published_at)
subscriptions(line_id, plan_id, version, start_at, end_at)
cdr_raw(cdr_id PK, source, payload, ingest_time, event_time)
sessions(session_id, line_id, state, bytes, seconds, last_seq)
rated_usage(usage_id, account_id, line_id, cdr_id UNIQUE, session_id,
  units, amount_cents, plan_version, period_id, invoice_id NULL, explain_json)
entitlements(key, period_id, dimension, remaining, row_ver)
invoices(invoice_id, account_id, period_id UNIQUE(account_id,period_id),
  status, subtotal_cents, tax_cents, total_cents)
invoice_lines(invoice_id, line_no, amount_cents, desc, usage_agg_ref)
adjustments(adj_id, account_id, amount_cents, reason, period_id)
balances(account_id, cents, row_ver)  -- optional
reservations(res_id, account_id, session_id, cents, expires, state)
```

### 8.2 API sketches

```text
POST /v1/cdrs  (network mTLS)
{ "cdr_id":"NE1-12345", "type":"VOICE", "msisdn":"...",
  "start":"...", "end":"...", "seconds":73 }

GET /v1/accounts/{id}/usage?period=2026-08
GET /v1/accounts/{id}/invoices
GET /v1/accounts/{id}/invoices/{inv}

POST /v1/online/authorize  (optional)
{ "line_id":"L", "dimension":"DATA", "estimate_units":1048576 }
-> { "allow": true, "throttle": null, "reservation_id":"R1" }

POST /v1/online/settle
{ "reservation_id":"R1", "actual_units":524288 }
```

### 8.3 Rating pseudocode

```text
function rate(mediated):
  if exists_rated(mediated.cdr_id): return
  sub = sub_at(mediated.line_id, mediated.event_time)
  plan = plan_ver(sub)
  units = quantize(mediated, plan.quantum)
  got = entitlement.consume(key(sub), plan.dimension, units)
  over = units - got
  amount = over * plan.rate_cents_per_unit
  write_rated(...)
```

### 8.4 Entitlement consume

```text
function consume(key, dim, units):
  for attempt in 1..N:
    row = get(key, dim, period)
    grant = min(units, max(row.remaining, 0))
    if cas(remaining=row.remaining-grant, ver+1): return grant
  throw
```

### 8.5 Session stitch

```text
on DATA interim/terminate:
  sess = load_or_create(session_id)
  if seq <= sess.last_seq: ignore dup
  delta = bytes - sess.bytes_reported  // or use incremental field
  sess.update(bytes, last_seq)
  emit mediated usage delta
  if terminate: close session
```

### 8.6 Invoice pseudocode

```text
function close(account, period):
  if invoice_exists: return
  usages = select rated where account and period and invoice_id is null
  subtotal = sum(amount) + recurring + sum(adjustments)
  tax = tax_engine.quote(account, subtotal, lines)
  inv = insert FINALIZED unique(account,period)
  mark usages invoiced
  collect(inv)
```

### 8.7 Balance reserve/settle

```text
reserve(account, cents, ttl):
  cas balance -= cents if balance >= cents
  write reservation EXPIRES
settle(res, actual):
  release = reserved - actual
  balance += release
  mark reservation SETTLED
reaper:
  expired -> release remaining
```

### 8.8 State machines

```text
Invoice: DRAFT -> FINALIZED -> PAID
                 -> PAST_DUE -> SETTLED_PARTIAL / CHARGED_OFF
Reservation: OPEN -> SETTLED
                 -> EXPIRED
Session: OPEN -> CLOSED
```

### 8.9 Glossary

| Term | Meaning |
|------|---------|
| CDR | Call/Session Detail Record |
| Mediation | Normalize/validate/correlate usage |
| Rating | Price usage against plan |
| Entitlement | Bucket/cap remaining |
| Quantum | Billable unit rounding |
| OCS | Online Charging System |
| TAP | Transferred Account Procedure (roaming) |
| PCEF | Policy enforcement point in network |

### 8.10 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1x | Ingest, mediate, rate, invoice, basic buckets |
| 10x | Idempotent bus, session stitch, entitlements CAS |
| 100x | Cells, lake, staggered billing_day, quarantine ops |
| 1000x | Regional cells, online path colocation, file factories |

### 8.11 Publish validation (plans)

- [ ] Rates integer  
- [ ] Quanta defined  
- [ ] Buckets + caps consistent  
- [ ] Golden CDR suite green  
- [ ] Proration rules documented  
- [ ] Kill switch wired  

### 8.12 Operator runbooks

1. Double-rate incident  
2. Ingest lag / disk  
3. Quarantine spike  
4. Month-end slow close  
5. Entitlement negative (bug)  
6. Prepaid reservation leak  
7. Roaming bill shock  

### 8.13 Worked scale (100x)

```text
20B CDR/day -> ~230K average QPS; peak ~1M
Lake 8 TB/day; compress 3-5x -> still multi-TB
Invoice 500M/month -> ~20 days * shards; billing_day stagger critical
```

### 8.14 Worked scale (1,000x)

```text
200B CDR/day -> specialized ingest; regional cells mandatory
Cannot one global Kafka without celling
Online authorize at 5M QPS -> edge caches of entitlement snapshots + async reconcile
```

### 8.15 Interview "say this" summary

> Idempotent CDRs; mediate and stitch sessions; pin plan versions; rate to append-only ledger; atomic entitlements; invoices from snapshots; late CDRs as adjustments; optional prepaid reservations; scale by account cells; stagger billing days.

### 8.16 Explain JSON example

```text
{
  "cdr_id": "NE1-9",
  "units_billable": 120,
  "from_bucket": 100,
  "overage_units": 20,
  "rate_cents": 2,
  "amount_cents": 40,
  "plan_version": 4
}
```

### 8.17 Security checklist

- [ ] mTLS from network elements  
- [ ] MSISDN hashing/tokenization in analytics  
- [ ] Admin plan publish audited  
- [ ] Customer authz on invoices  
- [ ] PII retention limits  

### 8.18 Reliability test plan

1. Duplicate CDR 10k times -> one rated.  
2. Out-of-order interims -> correct bytes.  
3. Concurrent pool consume -> never negative.  
4. Invoice finalize replay -> one invoice.  
5. Reservation TTL releases.  
6. Late CDR creates adjustment not second full bill silently wrong.

### 8.19 Idempotency matrix

| Path | Key | Replay |
|------|-----|--------|
| CDR ingest | cdr_id | No-op |
| Rated usage | cdr_id | Same row |
| Entitlement consume | cdr_id+dimension | Same grant |
| Invoice finalize | account+period | Same invoice |
| Reserve | session_id | Same reservation |
| Settle | reservation_id | Same settle |

### 8.20 Final trap table

| Trap | Pushback |
|------|----------|
| Mutable minutes_left only | No audit / races |
| Float money | Drift |
| Drop CDRs after ACK | Revenue loss |
| Double session rate | Stitch bugs |
| Single billing_day herd | Month-end outage |
| 20B*400B=8PB/day | **8TB/day** |

### 8.21 Whiteboard close

Draw **CDR Log -> Mediation/Stitch -> Rating -> Ledger -> Invoice**, plus **Entitlement/Balance** side path for caps/prepaid. Walk duplicate CDR and late roaming adjustment.

> Billing bugs are **customer-trust + finance** incidents—own idempotency, ledgers, and month-end operations.

### 8.22 Quantum examples

```text
VOICE: ceil(seconds/60) minutes  OR per-second
SMS: 1 per message (concatenated SMS policy?)
DATA: ceil(bytes / 1MB) or per-KB; store bytes raw always
```

### 8.23 Proration example

```text
Plan $30/30-day month; change day 11 -> 10 days used
charge = floor(30_00 * 10/30) = 1000 cents old
new plan charge for remaining 20 days similarly
Pin calendar: use account billing period length
```

### 8.24 Recon queries

```text
rated_univoiced = sum(amount) where invoice_id is null and period<=P
invoice_subtotal should equal rated + recurring + adjustments for P
entitlement_consumed + remaining = granted_for_period
```

### 8.25 Online vs offline charging

| Mode | Pros | Cons |
|------|------|------|
| Offline (CDR batch) | Simple, durable | Bill shock; weak hard caps |
| Online (OCS) | Hard caps, prepaid | Latency, availability coupling |
| Hybrid | Best practical | Two paths to keep consistent |

MVP: offline + soft caps; add online for prepaid/hard caps when required.

### 8.26 Family pool example

```text
Pool DATA 10 GB for account
Line A consumes 7 GB; Line B tries 5 GB -> grant 3 GB + overage/throttle 2 GB
UX shows 0 remaining to both
```

### 8.27 Quarantine reasons

| Code | Action |
|------|--------|
| SCHEMA_INVALID | Fix producer; replay |
| UNKNOWN_MSISDN | Wait port/provision; retry |
| SKEW_EXTREME | Manual |
| DUP_PAYLOAD_DIFF | Conflict review (same id different body) |

### 8.28 Interview timing guide

| Minute | Topic |
|--------|-------|
| 0-5 | CDR types, invoice vs RT balance |
| 5-10 | Numbers + QPS split |
| 10-25 | HLD planes + stitch/rate |
| 25-40 | Caps, prepaid, late CDR, invoice |
| 40-45 | 100x/1000x + wrap |

### 8.29 Sample plan JSON

```text
{
  "plan_id": "FAMILY_UNL",
  "version": 3,
  "buckets": [{"dim":"DATA","units_bytes":10737418240,"period":"CYCLE"}],
  "rates": [{"dim":"DATA_OVER","cents_per_mb":2}],
  "caps": [{"dim":"DATA","soft":10737418240,"throttle":16106127360}],
  "voice": "UNLIMITED_FAIR_USE",
  "sms": "UNLIMITED"
}
```

### 8.30 Payment / dunning sketch

```text
FINALIZED -> charge PSP idempotent key invoice_id
fail -> PAST_DUE -> retry schedule -> suspend online allow?
partial pay -> allocate; remain due
```

### 8.31 More Q&A rapid fire

**Q: How do you handle clock rollback at switch?** A: Quarantine negative duration; monitor.  
**Q: Should rating be streaming SQL?** A: Possible; often microservices with deterministic libs easier to audit.  
**Q: PDF generation?** A: Async; store in object storage; don't block finalize.  
**Q: Multi-tenant MVNO?** A: tenant_id on all rows; cells per large MVNO.  
**Q: How to test proration?** A: Golden timelines with fixed clocks.  
**Q: Data residency?** A: Regional CDR lakes; invoice region pinned.  
**Q: Can customers download CDR itemization?** A: Paginated; sampled for unlimited; privacy.  
**Q: Bundle with device installment?** A: Separate ledger lines on invoice.  
**Q: What if entitlement Redis loses data?** A: Rebuild from rated_usage + grants; Redis not SoT.  
**Q: SoT for entitlements?** A: Durable store with CAS; cache optional.

### 8.32 Failure injection list

1. Kill rating mid-write -> restart idempotent.  
2. Duplicate authorize for same session -> one reservation.  
3. Billing_day job overlap -> unique guard.  
4. Tax engine timeout -> invoice stays DRAFT; alert.  
5. Lake outage -> ingest still on hot log; archive async lag OK.

### 8.33 Final checklist

- [ ] Split ingest/rate/invoice planes  
- [ ] Idempotent cdr_id  
- [ ] Session stitch deltas  
- [ ] Integer money + quanta  
- [ ] Entitlement CAS  
- [ ] Late CDR policy spoken  
- [ ] Optional RT balance clearly optional  
- [ ] Staggered billing_day  

---


### 8.34 CDR field dictionary (sample)

| Field | Meaning |
|-------|---------|
| cdr_id | Globally unique record id |
| record_type | VOICE / SMS / DATA_INTERIM / DATA_TERM |
| msisdn | Subscriber number |
| other_party | Called/calling party when applicable |
| start_ts / end_ts | Event times from switch |
| duration_sec | Voice duration |
| bytes_in / bytes_out | Data volumes |
| session_id | Correlate multi-part sessions |
| location / cell_id | Optional enrich |
| roaming_partner | Partner id if inbound TAP |

### 8.35 Rating explain for invoice UX

```text
"Data overage: 240 MB x $0.02 = $4.80 (after 10 GB bucket)"
"Roaming SMS Italy: 12 x $0.25 = $3.00"
Store machine codes + localized templates
```

### 8.36 Backpressure strategy

```text
If mediation lag > SLO:
  1. Autoscale consumers
  2. Shed non-critical enrichments
  3. Priority lane for domestic vs roaming batch
  4. Never drop acked CDRs; spill to cold buffer topic
```

### 8.37 Multi-MVNO tenancy note

```text
billing_tenant_id on all rows
Plan catalogs isolated
Online authorize routed by tenant
Large MVNO gets dedicated cell
```

### 8.38 Final interview reminders

- Say late-CDR policy early
- Draw planes, not one box "billing service"
- Integer quanta + cents
- Entitlement SoT durable not only Redis
- Stagger billing_day
- Optional RT balance clearly scoped

---

*End of Amazon SDE III prep doc: Phone Billing System.*
