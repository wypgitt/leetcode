# System Design: Ticketing System

> **Focus areas:** Events · Venues · Seat inventory · Holds · Checkout · Payments · Transfers · Fraud · Peak onsale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Event ticketing platform (inventory + checkout at onsale scale)**

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

Goal: design a **ticketing system**—sell seats/admissions for events with correct inventory, temporary holds, checkout, payments, transfers/refunds, and survive onsale stampedes.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Ticket inventory + purchase + delivery | Full social network for fans |
| Inventory | Seat/GA holds and sales truth | Venue construction CAD |
| Payments | Checkout capture + refunds | Becoming a bank |
| Amazon lens | Correctness under peak, ownership | Pretty seat map only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Events/venues? | Venues, seat maps, GA areas | Catalog |
| F2 | Inventory? | Seat-level + GA counters | Inventory ledger |
| F3 | Holds? | Timed soft holds in cart | Hold service |
| F4 | Checkout? | Pay + convert hold→sold | Checkout saga |
| F5 | Delivery? | Mobile QR / PDF / Apple Wallet | Ticket delivery |
| F6 | Transfers? | Resale/transfer rules | Transfer service |
| F7 | Refunds? | Event cancel / user refund policy | Refund workflows |
| F8 | Fraud? | Bots, scalping signals | Fraud/risk hooks |
| F9 | Onsale? | Queue / waiting room | Admission control |
| F10 | Promos? | Presales, codes, tiers | Access codes |
| F11 | Scanning? | Entry scan at venue | Scan API idempotent |
| F12 | SLA? | No oversell; fair-ish access | Invariants |

**MVP scope:**

1. Create event + seat map / GA pool.
2. Browse availability.
3. Hold seats with TTL.
4. Checkout pay convert to sold tickets.
5. Deliver QR tickets.
6. Cancel/refund basic.
7. Entry scan once.
8. Onsale waiting room + rate limit.
9. Ops: inventory integrity dashboard.

**Out of MVP:** full secondary marketplace dynamics, dynamic pricing perfection, facial entry, active-active multi-region writers for same seat.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Hold create | p99 < 200–400ms |
| N2 | Checkout | p99 < 2–3s incl pay |
| N3 | Durability | No lost paid tickets |
| N4 | Correctness | No double-sell seat |
| N5 | Peak | 100×–1000× baseline at onsale |
| N6 | Audit | Who held/sold/transferred |
| N7 | Availability | Degrade browse; protect purchase path |
| N8 | Fairness | Queue + bot mitigation |

### 1.3 Cases

**Happy:** Browse→hold→pay→ticket issued→scan entry.
**Edges:** hold expiry mid-pay; double click; bot stampede; payment unknown; event cancel; transfer after scan; GA oversell; seat map hotspot; clock skew TTL.

| Case | Behavior |
|------|----------|
| Double sell | Prevent via seat CAS / GA atomic dec |
| Hold expiry during pay | Reconcile; prefer customer if captured |
| Bot onsale | Waiting room + puzzle + purchase limits |
| Payment unknown | Reconcile; inventory reserved until decide |
| Scan twice | Idempotent accept first |
| Refund after transfer | Block or clawback policy |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Events active | 100 | 1K | 10K | 100K |
| Seats / hot event | 20K | 20K | 50K | 100K |
| Onsale peak QPS | 500 | 5K | 50K | 500K |
| Holds / s peak | 200 | 2K | 20K | 200K |
| Tickets sold / day | 50K | 500K | 5M | 50M |
| Scan QPS peak entry | 100 | 500 | 2K | 10K |
| Waiting room users | 10K | 100K | 1M | 10M |
| Regions | 1 | 2 | 3 | 5+ |

**Jumps:** 10×=multi-event platform; 100×=onsale engineering; 1,000×=global megastar onsales + multi-region read.

### 1.5 Scope repeat-back

> Ticketing inventory with holds, atomic sell, checkout, delivery, scan, and onsale admission control—never overselling seats—scaled via event/inventory partitions.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
Hot onsale: 100K users → waiting room
Checkout attempts 1–5K/s briefly
Each seat: hold/renew/sell/release events
```

### 2.2 Storage

```text
Seat rows 20K–100K per event small
Orders/tickets dominate long-term
QR secrets in KMS-backed store
```

### 2.3 Latency

```text
Hold: cache/inventory CAS path must be local to partition
```

### 2.4 Bottlenecks

(1) hot event partition (2) payment (3) waiting room (4) seat map read storm (5) fraud checks.

### 2.5 Cost

CDN for maps; protect DB; waiting room cheap vs oversell lawsuits.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Catalog | Events/venues/maps | Strong publish |
| Inventory | Holds/sold truth | Strong per seat/GA shard |
| Checkout/Order | Payment+ticket issue | Strong per order |
| Admission Control | Waiting room | Eventually fair-enough |
| Entry Scan | Redeem | Strong idempotent |

**Deal-breaker:** optimistic UI that marks sold without inventory CAS—oversell is existential.

### 3.2 Components

1. **Catalog Service** — events, maps
2. **Inventory Service** — seats/GA + holds
3. **Hold Service** — TTL renew
4. **Checkout Service** — saga
5. **Payments Adapter** — auth/capture
6. **Ticket Issuer** — QR/secure payload
7. **Transfer/Refund** — policies
8. **Waiting Room** — queue tokens
9. **Fraud/Risk** — signals
10. **Scan Gateway** — entry
11. **Notification** — email/push
12. **Ops Integrity** — oversell monitors

### 3.3 Core API (sketch)

```text
POST /v1/holds {event_id, seats[]|ga_qty, idempotency_key} → hold_id, exp
POST /v1/checkout {hold_id, pay_method, idempotency_key}
POST /v1/tickets/{id}/transfer
POST /v1/scan {ticket_id, venue_gate, ts} idempotent
GET /v1/availability/{event_id}
```

### 3.4 State machine

```text
SEAT: AVAILABLE → HELD → SOLD → (TRANSFERRED) → SCANNED
           HELD → AVAILABLE on TTL
ORDER: CREATED → PAID → TICKETS_ISSUED → COMPLETE / REFUNDED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Hold TTL | 2–10 min tunable | Cart abandonment vs lock |
| GA counters | Atomic Redis/DB dec with rebuild | Speed |
| Waiting room | Token buckets + lottery/FIFO hybrid | Fairness vs conversion |
| Seat map reads | CDN snapshots + invalidate | Peak |
| Multi-region | Primary inventory region per event | Correctness |

---

## 4. Architecture Diagram

```text
[Fans] -> Waiting Room -> Browse/CDN Map -> Hold/Inventory
                                      v
                               Checkout -> Payments
                                      v
                               Ticket Issuer -> Wallet/PDF
                                      v
                               Scan Gateway (venue)
```

### 4.1 Primary sequence

```text
Issue queue token if onsale
Create hold with CAS seat state + TTL
Checkout locks hold; payment
On capture: mark SOLD; issue tickets; release hold key
On fail: release hold
Scan: CAS unscanned→scanned
```

### 4.2 Isolation cell

```text
Event inventory partition = cell
Hot event isolated from others
Global: users, pay methods, fraud models
No cross-event seat locks
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Seat never SOLD twice.
2. GA sold+held <= capacity always.
3. Paid order always issues tickets or auto-refund path.
4. Hold expiry monotonic; renew extends carefully.
5. Scan once (or policy re-entry).
6. Idempotent checkout/scan.
7. Waiting room cannot be bypassed for protected onsale.
8. Refund restores inventory only if policy allows and not scanned.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single region PG+Redis holds |
| 10× | Event sharding; CDN maps |
| 100× | Waiting room; inventory hot path specialized |
| 1000× | Mega onsale playbooks; multi-region reads; bot war |

### 5.3 Maintainability

- Seat map versioning.
- Policy engine for transfer/refund.
- Loadtest onsale continuously.
- Canary fraud rules.
- Inventory reconciler job.

### 5.4 Progressive scale

**1×:** Small venues, simple holds.
**10×:** Many events, shared platform.
**100×:** Serious onsale engineering.
**1000×:** Global megastars, bot arms race.

### 5.6 Seat CAS & GA atomics

Seat row version CAS AVAILABLE→HELD→SOLD. GA: atomic decrement remaining; periodic reconcile against sold ledger.

### 5.7 Hold TTL races

Expiry worker vs checkout: use compare hold_id+version; payment unknown keeps reservation fence until reconcile.

### 5.8 Onsale waiting room

Issue signed queue tokens; admit rate to hold API; separate browse. FIFO with jitter + bot score.

### 5.9 Payment unknown

Inventory remains fenced; reconcile with PSP; prefer not punishing successful capture.

### 5.10 Entry scan offline

Venue cache allowlist of ticket hashes; sync scans up; conflict = manual PS.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Oversell | SEV/legal |
| Lose paid ticket | SEV |
| Bypass queue for bots | Trust |
| Multi-primary seat writers | Split brain |
| Scan without idempotency | Entry chaos |
| Silent inventory mutate in promo | Corruption |

---

## 6. Wrap-Up

### 6.1 Designed

Event-partitioned ticketing: catalog, strong inventory holds/sells, checkout saga, tickets, scan, waiting room—no oversell.

### 6.2 Decisions to defend

1. Event inventory cells
2. Seat CAS / GA atomics
3. Timed holds
4. Checkout saga + pay reconcile
5. Waiting room
6. Ticket cryptographic IDs
7. Idempotent scan
8. Primary region per hot event

### 6.3 Risks

- Bot scalpers
- PSP latency
- Hot partition
- Clock skew TTL
- Refund policy complexity

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope inventory+checkout |
| 5–15 | Holds+CAS |
| 15–25 | Checkout/pay/tickets |
| 25–35 | Onsale/waiting room/fraud |
| 35–45 | Scan/transfers/scale |

### 6.5 Closer

> **Ticketing System**: strong inventory, fenced holds, payment-safe checkout, onsale admission control, progressive peak scale, never oversell.

---

## 7. Deeper / Related Interview Questions

### 7.1 Inventory

**Q: GA vs reserved seating?**
A: Counters vs seat rows.

**Q: Companion seats?**
A: Bundle constraints in hold.

**Q: Kill seats for production?**
A: Admin blocks with audit.

### 7.2 Checkout

**Q: 3D Secure latency?**
A: Extend hold TTL on challenge.

**Q: Partial cart fail?**
A: All-or-nothing hold convert.

**Q: Idempotency key lost?**
A: Client must persist; support lookup.

### 7.3 Onsale

**Q: Lottery vs FIFO?**
A: Hybrid; state trade-off.

**Q: Presale codes?**
A: Token entitlements before hold.

**Q: CDN stampede?**
A: Cache maps; protect APIs.

### 7.4 Fraud/transfer

**Q: Transfer storm scalping?**
A: Cooldown + identity + price caps optional.

**Q: VPN bots?**
A: Device/risk scores + purchase limits.

### 7.5 Scan

**Q: Phone dead?**
A: PDF backup / box office reissue.

**Q: Multiple gates?**
A: Scan service centralized with venue cache.

### 7.6 Traps

**Q: Kafka as seat lock**
A: Need CAS store.

**Q: Eventually consistent sold**
A: Oversell.

**Q: Design StubHub first**
A: Secondary later.

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| Oversell count | Must be ~0 |
| Hold→pay conversion | Funnel |
| Checkout p99 | UX |
| Queue wait | Fairness |
| Bot block rate | Abuse |
| Scan fail rate | Entry |
| Refund lag | Trust |
| Inventory reconcile drift | Integrity |

### 7.8 Ownership

**Q: Who pages for oversell?**
A: Inventory IC sev-1.

**Q: Who pages for onsale meltdown?**
A: Admission control + Checkout IC.

### 7.9 Progressive drill

**10×:** shard events + CDN
**100×:** waiting room + hot path
**1,000×:** global mega onsale

---

## 8. Appendices

### 8.1 Schema sketches

```text
events(event_id, venue_id, state)
seats(event_id, seat_id, state, hold_id, version)
ga_pools(event_id, pool_id, capacity, held, sold)
holds(hold_id, exp_ts, user_id, version)
orders(order_id, state, pay_intent, idem_key UNIQUE)
tickets(ticket_id, order_id, event_id, seat_or_ga, secret_hash, state)
scans(ticket_id, ts, gate) UNIQUE ticket_id
queue_tokens(token, event_id, exp)
```

### 8.2 API checklist

- [ ] Hold create/renew/release
- [ ] Checkout
- [ ] Ticket get
- [ ] Transfer
- [ ] Refund
- [ ] Scan
- [ ] Waiting room admit

### 8.3 Oncall checklist

- [ ] Oversell monitor
- [ ] Hold expiry lag
- [ ] Pay error rate
- [ ] Queue size
- [ ] Scan errors
- [ ] Fraud spike
- [ ] Rollback onsale config

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Hold | Temporary reservation |
| GA | General admission |
| Onsale | Public sale open |
| Waiting room | Admission control |
| CAS | Compare-and-set |
| PSP | Payment service provider |

### 8.5 Deal-breaker one-liners

- Optimistic sell without CAS
- Multi-primary same seat
- No payment reconcile path
- Disable queue under load for 'conversion'

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Inventory | Ticketing Inventory |
| Checkout | Purchases |
| Waiting room | Edge/Admission |
| Tickets | Issuance |
| Scan | Venue Entry |
| Fraud | Risk |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | PG+Redis |
| 10× | Shard by event |
| 100× | Hot event specialized store |
| 1000× | Mega playbooks multi-region read |

### 8.8 Failure injection

1. Double hold — CAS loses one.
2. Pay timeout — reconcile fence.
3. Expiry vs pay race — versioned decide.
4. Scan offline conflict — PS.
5. Waiting room overload — shed browse.
6. Map CDN poison — version pin.

---

## Interview Traps

**Trap: Ignore oversell**
Signal: Instant fail

**Trap: Microservices before invariants**
Signal: Wrong

**Trap: Global lock all seats**
Signal: Won't scale

**Trap: Skip waiting room**
Signal: Meltdown

---

## Flash Cards

### Card 1: Seat CAS

No double sell.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Inventory

### Card 2: Hold TTL

Fenced expiry.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Checkout

### Card 3: Checkout saga

Pay+issue atomic outcome.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Admission

### Card 4: Waiting room

Protect inventory.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Risk

### Card 5: GA atomics

capacity invariant.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Venue

### Card 6: Pay unknown

Keep fence.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Issuance

### Card 7: Scan once

Idempotent.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Inventory

### Card 8: Event cell

Hot isolation.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Checkout

### Card 9: Ticket secret

KMS/HMAC.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Admission

### Card 10: Transfer rules

Policy engine.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Risk

### Card 11: Refund restore

Only if allowed.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Venue

### Card 12: Bot limits

Per identity.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Issuance

### Card 13: CDN maps

Read path.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Inventory

### Card 14: Deal-breaker

Oversell.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Checkout

### Card 15: Metrics

Oversell=0; checkout p99.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Admission

### Card 16: Mega onsale

Game day.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Risk

---

## Scenario Runbooks

### R1 — Oversell detected
Freeze event sales; reconcile; customer make-good; root cause CAS.

### R2 — Onsale meltdown
Tighten admit rate; scale hold partitions; static fallback pages.

### R3 — Payment outage
Pause checkout; keep holds policy; message.

### R4 — Scan outage
Manual list degrade; queue scans.

### R5 — Fraud storm
Tighten rules; challenge; purchase caps.

---

## Extended Rapid Q&A

**Q: Why not long holds?**
A: Inventory starvation.

**Q: Wheelchair seats?**
A: Constraint attributes.

**Q: Season tickets?**
A: Different product inventory class.

**Q: Paper tickets?**
A: Issuance format flag.

**Q: Comp tickets?**
A: Zero-price order audited.

**Q: Clock skew?**
A: Server expiry only.

**Q: First widget?**
A: Oversell+drift.

**Q: Secondary market?**
A: Later; primary invariants first.

**Q: Why shard by event?**
A: Hotspot isolation.

**Q: Mobile wallet?**
A: Passkit adapter.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Soft inventory counts only | Oversell |
| Single global seat DB without partitions | Hotspot death |
| No holds just pay | Poor UX races |
| Client-side seat locks | Trivial bypass |
| Skip idempotent scan | Double entry |

---

## LLD Touch (optional)

Classes: `Event`, `Seat`, `GaPool`, `Hold`, `Order`, `Ticket`, `Scan`, `QueueToken`, `PaymentIntent`. Patterns: CAS state, TTL holds, Saga, Idempotency keys, Admission control, Reconciler.

---

## 60-second Narrative

"We isolate inventory per event with CAS seats and atomic GA counters. Timed holds fence capacity through checkout. Payments reconcile safely so paid fans get tickets. Waiting rooms protect onsales from bots and stampedes. Scans are idempotent. Scale by partitioning hot events and practicing mega onsales. Success is zero oversell, durable paid tickets, and controlled peaks."

---

## Extra Depth: Seat Map Versions

Immutable published layouts; in-flight holds pin version.

## Extra Depth: Reconciler

Nightly/continuous compare holds/sold vs ledger.

## Extra Depth: Bot Arms Race

Device attestation, velocity, puzzle—measure false positives.

## Extra Depth: Venue Offline

Signed ticket cache; sync scans.

## Extra Depth: Observability

Wide events; avoid seat_id unbounded metrics.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How do companion seats work in holds?**
A: Atomic multi-seat hold; all-or-nothing CAS.

**Q: What if useful bots for accessibility purchasers?**
A: Verified channels + purchase limits + human support lanes.

**Q: Season ticket vs single event inventory?**
A: Separate inventory classes; season may allocate entitlements.

**Q: Paper will-call pickup?**
A: Issuance mode; ID check workflow at box office.

**Q: How rotate QR secrets?**
A: Reissue invalidates old tokens; scan checks version.

**Q: Partial refund after event postpone?**
A: Policy engine; inventory may not restore.

**Q: Why primary region for inventory?**
A: Avoid dual-write oversell; reads can be multi-region.

**Q: Flash onsale lottery fairness?**
A: Publish algorithm; audit seeds; bot score gated.

**Q: GA oversell detect after fact?**
A: Reconciler alert; make-good; sev.

**Q: Transfer to foreign user?**
A: KYC/limits by jurisdiction; fraud checks.

**Q: Venue entry offline conflict two scans?**
A: First sync wins; second PS.

**Q: Promo code inventory?**
A: Entitlement tokens before hold.

**Q: How loadtest onsale?**
A: Synthetic waiting room+holds against staging inventory.

**Q: Child/infant tickets?**
A: Seat constraints + age rules.

**Q: Who owns oversell SEV?**
A: Inventory platform IC immediately.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT | Inventory CAS |
| Peak | Waiting room |
| Pay | Reconcile fence |
| Kill | Oversell |

---

*End of Ticketing System design notes (Amazon SDE III prep).*


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

