# System Design: Parking Payment System

> **Focus areas:** Entry/exit · Ticket/session lifecycle · Pricing engines · Payments & receipts · Occupancy · Gates/IoT · Idempotency · Fraud · Multi-garage ops · Offline resilience
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Money + physical-world coupling; split QPS classes; explicit deal-breakers; single-writer session home; customer trust at the gate
> **Interview theme:** Amazon SDE III / L6 — **Physical + digital commerce** (Amazon Go / parking partnerships / workplace campus / third-party garages)

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

Goal: design a **parking-payment platform** that issues sessions at entry, prices them by policy, collects payment (prepay / postpay / account), opens gates reliably, and remains operable when the network blips—across one garage today and a national fleet tomorrow.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Session + pricing + payment + gate actuation | Full city traffic control |
| Physical | Ticket printers, LPR cameras, barriers, pay stations | Pure app-only hypothetical with no offline |
| Money | Idempotent charges, receipts, refunds, disputes | Becoming an acquiring bank |
| Amazon lens | Operational ownership, customer trust, frugality, mechanisms | Academic IoT diagram alone |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who parks? | Public + employees + subscribers + fleet | Account types; different rate cards |
| F2 | Entry credential? | Ticket QR, LPR plate, RFID/NFC, app BLE, barcode | Credential abstraction; multi-factor bind |
| F3 | Pricing model? | Time-based tiers, flat day max, early-bird, overnight, event surge, free grace | Versioned rate cards; deterministic quote |
| F4 | When pay? | Mix: pay-on-exit, pay-before-exit (kiosk/app), prepaid reserved | Session states must allow both |
| F5 | Payment methods? | Card, wallet, Amazon Pay / corporate account, cash kiosk | PSP adapter + cash reconciliation |
| F6 | Reservations? | Optional reserved spots / EV stalls | Inventory reservation plane |
| F7 | Multi-garage? | Many facilities, operators, jurisdictions | Tenant/facility cells; tax locality |
| F8 | Receipts / tax? | Email/SMS/app; VAT/sales tax where required | Immutable receipt artifacts |
| F9 | Refunds / disputes? | Lost ticket, wrong plate, gate failure, overcharge | Ops tools + ledger adjustments |
| F10 | Occupancy? | Live counts per zone / floor / stall type | Sensors + soft counters; not perfect |
| F11 | Enforcement? | Overstay after paid window; scofflaws | Hold lists; ANPR watchlists |
| F12 | Offline? | Gate must open with local rules if cloud down | Edge controller + sync |

**MVP functional scope (lock with interviewer):**

1. Create **parking session** at entry (credential → session_id).  
2. **Quote price** from rate card given enter/exit timestamps + product.  
3. **Collect payment** (app / kiosk / exit lane) with idempotency.  
4. **Authorize exit** and command gate open when paid/eligible.  
5. **Receipt** generation + basic refund path.  
6. **Occupancy** counters for garage dashboard.  
7. **Offline edge** mode: local allow-list + deferred sync.

**Out of MVP (explicitly defer):**

- Full city-wide curb parking meter network  
- Autonomous valet robot orchestration  
- Perfect stall-level computer vision inventory as sole SoT  
- Cross-border multi-acquirer treasury complexity  
- Active-active multi-region writes for the same session

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Entry latency | Driver waiting at barrier | p99 gate decision < 1–2s local; cloud assist < 3s |
| N2 | Exit + pay | Interactive | Quote < 300ms; pay depends on PSP (budget separately) |
| N3 | Availability | Garage can't soft-fail forever | Edge autonomy; cloud 99.9%+ control plane |
| N4 | Consistency | Session money strong | Single-writer home for `session_id` |
| N5 | Durability | No lost paid sessions | Quorum commit before "paid" ACK |
| N6 | Audit | Every open/close explainable | Append-only event log + receipt |
| N7 | Privacy | Plates are sensitive | Hash/tokenizeize; retention policy |
| N8 | Safety | Never trap people; fire egress | Physical fail-safe overrides software |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Drive-in → LPR match / ticket print → park → app pay → exit scan → gate opens.  
2. Pay-on-exit lane: scan → quote → tap card → capture → open.  
3. Subscriber RFID: entry/exit free within plan; soft session for analytics.  
4. Reserved EV stall: reservation hold → occupy → settle remaining.  
5. Lost ticket: plate lookup + time estimate + admin fee → pay → exit.  
6. Offline entry: edge issues local ticket; syncs when online.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double tap pay | Idempotency key → one charge |
| PSP timeout unknown | Session `PAYMENT_PENDING`; do not open until known or policy override |
| Gate open command lost | Retry with fence; sensor confirms barrier state |
| Wrong plate OCR | Manual plate correct + audit; never silent merge sessions |
| Tailgating | Occupancy drift; camera event; do not invent money sessions |
| Clock skew kiosk | Server time authoritative for pricing |
| Rate card change mid-park | Pin `rate_card_version` at entry or at first quote—pick & document |
| Power loss at controller | Battery backup; fail-safe open policy per site |
| Refund after exit | Ledger credit; no re-open needed |
| Hot garage event surge | Dynamic rate card; capacity messaging; queue UX |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Garages / facilities | 10 | 100 | 1K | 10K |
| Stalls | 5K | 50K | 500K | 5M |
| Entries / day | 50K | 500K | 5M | 50M |
| Peak entry QPS (global) | ~5 | ~50 | ~500 | ~5K |
| Peak exit/pay QPS | ~5 | ~50 | ~500 | ~5K |
| Peak quote QPS | ~20 | ~200 | ~2K | ~20K |
| IoT heartbeats / s | ~100 | ~1K | ~10K | ~100K |
| Occupancy read QPS | ~50 | ~500 | ~5K | ~50K |
| Receipt emails / day | 40K | 400K | 4M | 40M |
| Concurrent open sessions | 3K | 30K | 300K | 3M |

**Split classes:** entry events ≠ exit payments ≠ occupancy reads ≠ IoT telemetry ≠ analytics. Do not lump into one "QPS."

**What each jump forces:**

- **10×:** Edge controllers standardized; outbox to PSP; facility sharding; rate-card service.  
- **100×:** Multi-tenant operator cells; regional session homes; LPR pipeline scale; automated recon.  
- **1,000×:** Hierarchical occupancy; edge ML plate; global directory; hot-event isolation; streaming fraud.

### 1.5 Constraints & Assumptions

- Physical **fail-safe** (fire/egress) overrides any software deny.  
- Plates / tickets are PII-ish—minimize retention; encrypt at rest.  
- Pricing uses **integer minor units**; never float.  
- "Open the gate" is an **effect** that must be idempotent and observable.  
- Amazon interview angle: ownership of SEVs when drivers are stuck; frugality on camera bandwidth; clear mechanisms.

**Scope statement:**

> Design a parking-payment system that manages entry/exit sessions, deterministic pricing, idempotent payments, receipts/refunds, occupancy, and edge-offline gate control—from tens of garages through 10× / 100× / 1,000× facilities—with single-writer session homes, strong money invariants, and customer-safe physical overrides.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
Baseline 50K entries/day ÷ 86400 ≈ 0.58/s average
Peak ~8× lunch/evening ⇒ ~5 entry/s global (matches table)

Each session may produce:
  1 entry event + N occupancy updates
  1–5 quote calls (app refreshes)
  1 payment (+ webhooks)
  1 exit authorization + gate commands
  1 receipt
→ control-plane reads/quotes ≫ hard entries
```

At **1,000×**: ~5K entry/s peak globally but **highly skewed** to cities/events—design for hot facilities, not uniform averages.

### 2.2 Storage

```text
Session row ~500 B–1 KB; events ~200–500 B; receipt ~2 KB
Per session lifecycle ~3–8 KB

50K/day × 5 KB ≈ 250 MB/day
1,000×: 50M/day × 5 KB = 250 GB/day
Annual at 100× (5M/day): 5e6 × 365 × 5 KB ≈ 9.1 TB/year hot-ish
LPR images: 50–200 KB/event → dominate storage; tier to cold object store quickly
```

### 2.3 Bandwidth

```text
LPR image upload 100 KB × 5K entry/s = 500 MB/s at 1000× peak → edge crop/encode + regional ingest
Telemetry heartbeats small but chatty → batch/coalesce
```

### 2.4 Memory

```text
Open sessions 3M × 1 KB ≈ 3 GB metadata (fits); 
hot facility caches + rate cards tiny
Idempotency keys for payments: shard KV, 24–72h TTL
```

### 2.5 Bottleneck ranking (interview)

(1) Gate decision under network partition (2) payment uncertainty (3) hot-event stampede (4) LPR correctness/cost (5) occupancy drift (6) raw HTTP QPS.

### 2.6 Latency budgets

```text
Entry (online assist): edge OCR local 100–300ms + cloud session create 50–150ms → <1–2s
Exit quote: cache rate card + session fetch → <100–300ms
Pay: PSP 500ms–3s (exclude from gate SLO; show UX)
Gate command local bus: <100ms; confirm sensor <1s
```

---

## 3. High-Level Design

### 3.1 Core abstractions

| Entity | Role |
|--------|------|
| Facility | Garage site; timezone; tax; fail-safe policy |
| Zone / StallType | Level, EV, ADA, reserved |
| Credential | Plate, ticket_id, RFID, account_id |
| Session | SoT for one parking stay |
| RateCard | Versioned pricing rules |
| PaymentIntent | Money mutation for a session |
| GateCommand | Idempotent actuation intent |
| OccupancyView | Derived counts (soft) |
| Receipt | Immutable customer artifact |

### 3.2 Component list

1. **Edge Controller** (per lane/facility): local rules, ticket printer, barrier I/O, offline queue.  
2. **Session Service**: create/bind/close sessions; single-writer by `session_id`.  
3. **Pricing Engine**: pure function `(session, rate_card_version, exit_ts) → quote`.  
4. **Payment Orchestrator**: PSP + cash; idempotency; uncertainty protocol.  
5. **Access / Gate Service**: authorize exit; emit GateCommand; observe barrier state.  
6. **Credential / LPR Service**: plate normalize; bind; privacy hashing.  
7. **Occupancy Service**: counters + sensor fusion; dashboards.  
8. **Rate Card Admin**: publish versioned cards with canary.  
9. **Notification / Receipt**: email/SMS/push.  
10. **Ops Console**: lost ticket, refunds, disputes, manual open (audited).  
11. **Analytics / Fraud**: after-the-fact; not on critical gate path unless cached.

### 3.3 Primary APIs

```text
POST /v1/facilities/{fid}/entries
  → {session_id, credential, entered_at, rate_card_version}

GET  /v1/sessions/{sid}/quote?at=...
  → {amount_minor, currency, line_items, expires_at}

POST /v1/sessions/{sid}/payments
  Idempotency-Key: ...
  → {payment_id, state}

POST /v1/sessions/{sid}/exit-authorize
  → {allowed, gate_command_id}

POST /v1/gates/{gid}/commands/{command_id}/ack
  → barrier telemetry

POST /v1/ops/sessions/{sid}/manual-open   # audited
POST /v1/ops/sessions/{sid}/refunds
```

### 3.4 Session state machine

```text
CREATED → ACTIVE → (QUOTE_LOCKED) → PAYMENT_PENDING → PAID → EXIT_AUTHORIZED → CLOSED
                 ↘ VOIDED / CANCELLED
PAID → DISPUTED → REFUNDED / CLOSED
ACTIVE → LOST_TICKET_FLOW → ...
```

Valid transitions only; CAS on `version`.

### 3.5 Key trade-offs

| Decision | Choice | Why |
|----------|--------|-----|
| Pricing purity | Pure function + pinned version | Auditability; replay |
| Gate path | Edge-first | Drivers don't wait on us-east |
| Occupancy SoT | Soft derived | Sensors lie; money sessions don't |
| Multi-region | AA reads; SW session home | Money + session integrity |
| LPR images | Object store, short hot TTL | Cost |
| Manual open | Always audited + reason codes | Trust & fraud |

### 3.6 Pricing sketch

```text
quote(session, card, exit_ts):
  duration = exit_ts - session.entered_at - grace
  apply tiers / max / early_bird / overnight / event multipliers
  apply tax rules for facility jurisdiction
  return integer minor units + line items
```

Pin either `rate_card_version` at entry (customer-friendly stability) or at first paid quote (ops flexibility)—**say which** and stick.

---

## 4. Architecture Diagram

### 4.1 Context

```text
[Car] --> [Lane: Camera/RFID/Ticket] --> [Edge Controller]
                                              |  (local decision + queue)
                                              v
                                         [Regional API Gateway]
                                              |
          +----------------+------------------+------------------+
          v                v                  v                  v
   Session Service   Pricing Engine   Payment Orchestrator   Access/Gate
          |                |                  |                  |
          +-------+--------+--------+---------+--------+---------+
                  v                 v                  v
            Session DB         Rate Card KV        PSP / Ledger
                  |
                  +--> Receipt / Notify
                  +--> Occupancy (derived)
                  +--> Data Lake (async)
```

### 4.2 Edge autonomy

```text
Online: Edge --> create session cloud --> print ticket / raise barrier
Offline: Edge --> local session UUID --> allow per policy --> outbox sync later
Degraded: Edge --> open for subscribers/allowlist; queue unknowns for pay-on-foot
```

### 4.3 Sequence: pay-on-exit

```text
Exit loop scan credential
Session Service: load ACTIVE session
Pricing: quote
Payment: authorize+capture (idempotent)
On PAID: Access emits GateCommand(open)
Edge executes; acks barrier open
Session → CLOSED; occupancy--
```

### 4.4 Sequence: payment uncertainty

```text
PSP timeout after possible charge
PaymentIntent = PENDING
Do NOT auto-open
Inquire / wait webhook
Ops override path with audit if lane jammed (customer trust > perfect money temporarily)
Reconcile later; never double-charge (idempotency)
```

### 4.5 Cells & tenancy

```text
Cell key: operator_id + region  (or facility_id hash ranges)
Directory: session_id → home cell
No cross-cell synchronous money joins on exit path
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

1. **Accept entry ⇒ durable session** (cloud or edge outbox).  
2. **Idempotent payments** — one economic charge per intent key.  
3. **Paid ⇒ receipt artifact** eventually; money journal first.  
4. **GateCommand idempotent** — same command_id does not double-bill.  
5. **Valid session transitions only**.  
6. **Server time for pricing**.  
7. **Manual open always audited**.  
8. **Physical fail-safe supersedes deny**.  
9. **PII minimization** for plates/images.  
10. **Reconciliation breaks never silently ignored**.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; PG; one PSP; per-garage edge VM/appliance |
| 10× | Session service boundary; outbox; rate-card CDN; facility shards |
| 100× | Operator cells; regional homes; LPR async pipeline; auto recon |
| 1000× | Hot-event isolation; hierarchical occupancy; edge inference; global directory |

**Hot facility (stadium night):** dedicated rate limits, pre-warmed quote caches, extra edge capacity, surge rate card published earlier, occupancy messaging to apps diverting cars.

### 5.3 Maintainability

- Rate cards as data (not code deploys) with validation + canary facilities.  
- Edge agent versioning + signed update bundles.  
- Contract tests for PSP + gate I/O simulators.  
- Deterministic pricing property tests (golden durations).  
- Ops runbooks: stuck gate, lost ticket, clock drift, occupancy reset.

### 5.4 Progressive scale deep dive

**1× (~10 garages)**

- Monolith API + Postgres.  
- Edge controller talks REST.  
- Nightly cash/PSP recon.  
- Simple occupancy ++/--.

**10×**

- Split Session / Payment / Pricing.  
- Idempotency store hardened.  
- Outbox for notifications + PSP.  
- Facility-level shard key beginning.

**100×**

- Cells by operator/region.  
- LPR images to object store; async bind.  
- Streaming occupancy with correction jobs.  
- Fraud scores on lost-ticket / refund rates.

**1000×**

- Global session directory.  
- Edge-first decisions default.  
- Event-stream analytics; nearline fraud.  
- Multi-PSP routing; tax engine service.

### 5.5 Offline & sync protocol

```text
edge_create_session(local_id, credential, ts_local, ts_monotonic):
  persist local
  enqueue outbox
  actuate per policy

cloud_ingest(outbox_batch):
  upsert by (facility_id, local_id) idempotent
  resolve credential conflicts carefully
  back-pressure if cloud behind — edge continues
```

Conflict: two entries same plate overlapping → ops queue; do not auto-merge money.

### 5.6 Occupancy truth

Occupancy is **UX + planning**, not ledger:

- Prefer sensor loops / cameras as signals.  
- Reconcile with open sessions periodically.  
- Show confidence; avoid promising a stall you don't hard-reserve.  
- Reserved stalls = separate inventory plane with TTLs.

### 5.7 Fraud & abuse

| Vector | Control |
|--------|---------|
| Ticket swapping | Bind plate+ticket; exit checks |
| Lost ticket abuse | Fee + velocity limits + plate history |
| OCR spoof / covers | Confidence thresholds; manual |
| Refund fraud | Dual control above threshold |
| Insider free-open | Audited manual open; anomaly alerts |
| Payment chargeback | Evidence pack: timestamps, images refs |

### 5.8 Privacy

- Store `plate_hash` + encrypted plate; raw images short TTL.  
- Access logs for ops plate lookups.  
- Retention: sessions years for finance; images days–weeks.  
- GDPR/CCPA delete: tombstone PII; keep non-identifying financial aggregates.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Cloud round-trip required to open gate | Stadium outage chaos |
| Float money | Rounding disputes |
| Mutable rate card without version pin | "Why did I pay more?" SEV |
| Occupancy as money SoT | Wrong charges |
| Blind PSP retry new key | Double charge |
| Silent manual opens | Insider fraud |
| Active-active session writers | Divergent paid/unpaid |
| Deny exit forever on outage | Trap customers — trust nuke |

---

## 6. Wrap-Up

### 6.1 What we designed

A parking-payment platform coupling **edge gate control**, **versioned pricing**, **idempotent payments**, **session lifecycle**, **receipts/refunds**, and **soft occupancy**—with progressive scale from single-operator garages to national fleets.

### 6.2 Key decisions worth defending

1. Edge-first gate decisions with cloud sync  
2. Pure pricing function + pinned rate card version  
3. Single-writer session home for money/state  
4. Occupancy derived, not authoritative for charging  
5. Payment uncertainty protocol (no blind open / no blind re-charge)  
6. Audited manual overrides for customer trust  
7. Integer minor units + recon  
8. PII minimization for LPR

### 6.3 Risks & follow-ups

- Occupancy drift vs customer promises  
- Edge software supply chain  
- Event-day stampedes  
- Multi-operator tax complexity  
- Chargeback evidence pipeline cost

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: session + pay + gate; offline required |
| 5–12 | State machine + credentials |
| 12–20 | Pricing purity + version pin |
| 20–30 | Payments + uncertainty + receipts |
| 30–38 | Edge autonomy + occupancy |
| 38–45 | Scale jumps, fraud, privacy, ownership |

### 6.5 Closer

> **Parking Payment System**: physical fail-safes, edge autonomy, deterministic pricing, strong money invariants, progressive facility scale, and clear two-pizza ownership when a driver is stuck at the barrier.

---

## 7. Deeper / Related Interview Questions

### 7.1 Session & credentials

**Q: Ticket vs LPR as primary key?**  
A: Neither alone—`session_id` is SoT; credentials are bindable factors. LPR can create or join; tickets are bearer tokens.

**Q: Can one car have two open sessions?**  
A: Should be rare; detect overlap; block new charge paths until resolved; don't auto-close the old one without evidence.

**Q: Motorcycle shared plates / paper temps?**  
A: Lower OCR confidence → ticket fallback; ops tools.

### 7.2 Pricing

**Q: Why pure function?**  
A: Replay for disputes; A/B rate cards; unit tests; no hidden DB mutation mid-quote.

**Q: Early-bird expires at 9am—arrived 8:59 exit 5pm?**  
A: Encode calendar rules explicitly; pin timezone of facility; golden tests around DST.

**Q: Event surge announced after entry?**  
A: If version pinned at entry, customer keeps old card (trust). If business needs surge, pin at entry only for non-event products—product decision, say it aloud.

**Q: Grace period 15 minutes?**  
A: Subtract from duration; still create session for occupancy.

### 7.3 Payments

**Q: Pre-auth at entry?**  
A: Optional for some products; increases PSP auth holds; good for scofflaw reduction; bad for privacy/UX—trade-off.

**Q: Pay-before-exit window (e.g., 15 min to exit)?**  
A: `PAID` with `exit_by`; overstay creates extension quote.

**Q: Partial validations / tips?**  
A: Usually N/A; keep line items simple.

**Q: Cash kiosk?**  
A: Kiosk posts `CASH_RECORDED` with cassette meters; recon vs counted cash; different from PSP webhooks.

### 7.4 Gates & IoT

**Q: Command vs confirmation?**  
A: Intent (`GateCommand`) separate from telemetry (`barrier_open=true`). Retry intent until confirm or timeout→ops.

**Q: Exactly-once open?**  
A: Effectively-once: idempotent command_id; opening twice is usually safe physically; charging twice is not.

**Q: How to test without hardware?**  
A: Device twin simulator; contract tests; chaos: drop acks.

### 7.5 Offline

**Q: What if offline for 24h?**  
A: Edge continues within storage/policy; subscribers work; random public may pay at exit when online or via local rate table cache.

**Q: Sync storm when reconnecting?**  
A: Backoff, batch, prioritize payments/exits over images.

### 7.6 Occupancy & reservations

**Q: Show "12 spots left" — legal risk?**  
A: Soft number; buffer; don't sell hard reservations without inventory plane.

**Q: Reservation no-show?**  
A: TTL release; fee policy; oversell strategy explicit.

### 7.7 Multi-tenancy & scale

**Q: Shard key?**  
A: `facility_id` for telemetry; `session_id` home derived from facility/region. Payments co-located with session.

**Q: Stadium 1K entries in 20 minutes?**  
A: ~0.8/s local—easy for compute; hard for lanes physically. Software: local edge, pre-issued credentials, disable heavy cloud image upload synchronously.

**Q: 10K facilities config management?**  
A: GitOps-like device config; signed; canary rings; feature flags per facility.

### 7.8 Fraud, privacy, trust

**Q: Employee parking abuse?**  
A: Account plans + anomaly (entry without badge correlation).

**Q: GDPR delete plate?**  
A: Hash tombestone; remove images; retain amount/timestamp for finance under legal basis.

**Q: Who pages at 2am for stuck gate?**  
A: Edge/IoT oncall for actuation; Payments oncall for money; Facility ops for physical—clear RACI.

### 7.9 Amazon-specific angles

**Q: How does this relate to Amazon?**  
A: Workplace parking, partnership garages near lockers/retail, Amazon Pay, operational excellence narratives—focus on SEV ownership and mechanisms.

**Q: Frugality?**  
A: Don't stream full video 24/7 by default; eventize; compress; tier storage; quote cache.

**Q: Customer obsession at the gate?**  
A: Fail open for life safety; fast manual open tooling; transparent receipts; easy dispute.

### 7.10 Interview traps

**Q: "Just put it all in Kafka and the gate reads Kafka"?**  
A: Gate path needs local determinism; Kafka is for sync/analytics.

**Q: Microservices per sensor?**  
A: Overkill; edge agent + few cloud services.

**Q: Perfect stall CV before payments?**  
A: Wrong dependency order; ship money+session first.

**Q: Active-active sessions across regions?**  
A: Split-brain paid vs unpaid—don't.

**Q: Use floats for hours × rate?**  
A: Integer cents; define rounding rules once.

### 7.11 Progressive scale drill

**Q: What breaks at 10×?**  
A: Homegrown edge snowflakes; nightly recon; single DB.

**Q: What breaks at 100×?**  
A: Cross-tenant noisy neighbors; image ingest cost; support tooling.

**Q: What breaks at 1,000×?**  
A: Hot events; global directory; fraud rings; config blast radius.

### 7.12 Metrics that matter

| Metric | Why |
|--------|-----|
| Gate decision p99 | Customer stuck |
| Payment success / uncertainty age | Money + lanes |
| Manual open rate | Ops load / fraud signal |
| Occupancy error vs audit | Trust in UX |
| Quote drift disputes | Pricing bugs |
| Edge outbox lag | Sync health |
| $/session infra | Frugality |

### 7.13 Resume / cancel semantics

**Q: Cancel reservation?**  
A: Release inventory; refund per policy; idempotent cancel key.

**Q: Exit without pay due to gate force-open?**  
A: Session `FORCE_CLOSED`; bill later / account invoice; never lose audit trail.

---

## 8. Appendices

### 8.1 Schema sketches

```text
facilities(facility_id, operator_id, tz, geo, failsafe_policy, ...)
rate_cards(rate_card_id, facility_id, version, rules_json, status)
sessions(session_id, facility_id, credential_type, credential_hash,
         entered_at, exited_at, rate_card_version, state, version, ...)
payments(payment_id, session_id, amount_minor, currency, state, psp_ref, ...)
idempotency(scope, key, request_hash, ref_id, response, created_at)
gate_commands(command_id, gate_id, session_id, type, state, ...)
occupancy_snapshots(facility_id, zone_id, ts, count, source)
receipts(receipt_id, session_id, payload_ref, created_at)
audit_ops(id, actor, action, session_id, reason, ts)
```

### 8.2 API checklist

- [ ] Entry create idempotent on `(facility, local_id)`  
- [ ] Quote deterministic + versioned  
- [ ] Payment Idempotency-Key  
- [ ] Exit authorize checks PAID/eligible  
- [ ] Gate ack / telemetry  
- [ ] Ops manual open + refund  
- [ ] Webhooks from PSP verified  

### 8.3 Rate card example (simplified)

```text
grace: 15m
tiers: [60m→300, 120m→500, day_max→2000]  # cents
early_bird: enter before 09:00 AND exit before 18:00 → 800
overnight: 18:00–08:00 add 500
tax: facility jurisdiction profile
```

### 8.4 Edge outbox record

```text
{local_id, facility_id, type, payload, ts_local, mono, checksum, retries}
```

### 8.5 Oncall checklist

- [ ] Gate p99 / stuck lane alerts  
- [ ] Payment uncertainty queue age  
- [ ] Edge outbox lag by facility  
- [ ] Occupancy absurdity (negative / over capacity)  
- [ ] PSP / cash recon breaks  
- [ ] Manual open spike  
- [ ] Rollback: rate card, edge agent, payment config  

### 8.6 Deal-breaker one-liners

- Cloud- obligatory gate open  
- Float pricing  
- Unversioned rate mutations  
- Occupancy as billing SoT  
- Unaudited free exits  

### 8.7 Glossary

| Term | Meaning |
|------|---------|
| Edge controller | On-prem lane computer |
| Rate card | Versioned pricing document |
| GateCommand | Idempotent actuation intent |
| Soft occupancy | Derived non-ledger count |
| Uncertainty protocol | Inquire, don't blind retry money |
| Cell | Failure-isolated deployment unit |
| Two-pizza | Owning team with pager |
| Fail-safe | Physical safety override |

### 8.8 Failure injection drills

1. Kill cloud API — edge must admit per policy.  
2. PSP 500 after capture — no double charge; lane runbook.  
3. Clock jump on kiosk — server time wins.  
4. Duplicate outbox delivery — idempotent upsert.  
5. Barrier ack loss — retry / ops.  
6. Bad rate card canary — auto rollback.

### 8.9 Ownership map (Amazon-style)

| Surface | Owner |
|---------|-------|
| Edge agent + device | IoT/Lane team |
| Session + access | Parking Platform |
| Pricing | Pricing/Policy |
| Payments | Payments (shared) |
| Occupancy UX | Facility Experience |
| Fraud/refunds | Trust & Ops Tools |
| SEV customer stuck | Joint — Incident Commander rotates; don't ping-pong |

### 8.10 Progressive capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | 2 API hosts, 1 PG, 10 edge agents |
| 10× | Session/Pay split, Redis idempotency, 100 edges |
| 100× | 5 cells, object store images, recon workers |
| 1000× | 50 cells, global directory, stream fraud, CDN rate cards |

### 8.11 Sample quote response

```json
{
  "session_id": "sess_123",
  "rate_card_version": 17,
  "currency": "USD",
  "amount_minor": 1250,
  "line_items": [
    {"type": "TIME", "amount_minor": 1000},
    {"type": "TAX", "amount_minor": 250}
  ],
  "exit_by_if_paid": null
}
```

### 8.12 Lost ticket flow

```text
Ops/App: plate + approximate entry
Lookup candidates by plate_hash + time window
Select session / create LOST_TICKET session
Fee policy applied
Pay → exit authorize
Audit trail mandatory
```

### 8.13 EV / reserved stall notes

- Stall inventory leases with TTL.  
- Sensor confirm occupy; no-show release.  
- Charging payment may be separate product — don't overload parking session unless scoped.

### 8.14 Security checklist

- [ ] Mutual TLS / device certs for edge  
- [ ] Signed rate cards & agent bundles  
- [ ] Least privilege ops roles  
- [ ] PII field encryption  
- [ ] Webhook signature verify  
- [ ] Rate limit payment attempts  
- [ ] Pen-test pay kiosk OS  

### 8.15 Interview closer checklist

- [ ] Scoped MVP vs out  
- [ ] Numbers for entries + storage + latency  
- [ ] State machine  
- [ ] Edge offline story  
- [ ] Pricing version pin  
- [ ] Payment uncertainty  
- [ ] Progressive 10×/100×/1000×  
- [ ] Ownership / metrics / deal-breakers  

### 8.16 Related systems

Parking LLD (stall allocation OOP), payments platform, Amazon Pay, facility access control, ANPR vendors, tax engine, notifications, data lake for forecasting.

### 8.17 Common follow-ups to prepare

1. Design the edge agent state machine in detail.  
2. Write the pricing function for overnight + event.  
3. Model multi-operator settlements.  
4. Add subscriptions / payroll deduction.  
5. Integrate Amazon locker / retail validation for free validation stamps.

### 8.18 Minimal sequence diagram (text)

```text
Driver -> Edge: approach
Edge -> Camera: plate
Edge -> Session: CreateEntry
Session -> DB: insert ACTIVE
Session -> Edge: session_id
Edge -> Barrier: open
...
Driver -> App: pay
App -> Pricing: quote
App -> Payment: charge (Idempotency-Key)
Payment -> PSP: capture
Payment -> Session: PAID
Driver -> Edge: exit
Edge -> Access: authorize
Access -> Edge: GateCommand open
Edge -> Barrier: open
Edge -> Session: CLOSED
```

### 8.19 Cost narrative (frugality)

Biggest levers: (1) don't upload raw video continuously (2) short image TTL (3) cache rate cards at edge (4) batch telemetry (5) cell isolation so event storms don't multiply global spend (6) pure pricing avoids expensive "pricing micro-calls" chains.

### 8.20 Amazon leadership-principle hooks (use sparingly, concretely)

- **Customer Obsession:** never trap; clear receipts; fast dispute.  
- **Ownership:** one IC for stuck-gate SEV; no "it's IoT vs Payments" ping-pong.  
- **Insist on Highest Standards:** deterministic pricing tests; recon.  
- **Frugality:** eventized cameras; integer math; capacity cells.  
- **Dive Deep:** when disputes spike, inspect rate-card diffs + clock skew.  
- **Bias for Action:** ship edge offline MVP before perfect CV stalls.  
- **Deliver Results:** gate p99 + payment success are the scoreboard.

---

## Deep Technical Notes — Parking Payment

### N1. Credential normalization

Plates: uppercase, strip spaces/dashes, jurisdiction templates, ambiguous char confusable sets (O/0). Store display form encrypted + normalized hash for join. Never use raw OCR string as PK.

### N2. Time and DST

Facility timezone IANA string on facility record. Store all absolute times in UTC. Pricing calendars interpreted in facility TZ. Golden tests: spring forward / fall back windows.

### N3. Idempotency scopes

| API | Key scope |
|-----|-----------|
| Entry | facility_id + local_id |
| Payment | session_id + Idempotency-Key |
| Refund | session_id + refund_key |
| GateCommand | command_id globally unique |

### N4. Ledger sketch

Even if PSP is SoT for card cash, keep internal journals: `customer_payable`, `psp_clearing`, `tax_payable`, `revenue`. Refunds reverse. Cash cassette is another clearing account.

### N5. Rate card canary

Publish `status=CANARY` to 1–2 facilities; compare dispute_rate and revenue_per_session vs control; promote or rollback. Never silent edit of active version—always new version number.

### N6. Edge security

Device identity cert; attested agent; encrypted disks; kiosk locked-down OS; tamper alerts. Assume hostile physical access for kiosks.

### N7. Data products

Forecast fill; dynamic pricing proposals (human approve); false-OCR model training from corrections—human-in-loop.

### N8. Accessibility

ADA stalls inventory; app UX for taller payment time; audio at kiosks—product requirements, mention briefly.

### N9. Multi-product sessions

Parking + EV charge + valet tip—compose as related intents sharing `session_id` parent, separate payment lines; don't explode one state machine into spaghetti without need.

### N10. SLOs

| SLO | Target |
|-----|--------|
| Edge decision availability | 99.99% local |
| Cloud session create success | 99.9% |
| Payment capture success (ex. user declines) | 99.5% |
| Uncertainty age p99 | < 2 min interactive lanes |
| Receipt eventual | < 5 min |

---

## Interview Cards — Parking Payment

### Card 1: Edge must open without cloud

Local policy engine + outbox; sync later; life-safety fail-safe.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Lane/IoT team owns agent; customer-trust failure is trapped drivers / SEV brand damage.

### Card 2: Pin rate_card_version

Choose entry vs first-quote pin; document; test.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Pricing team owns cards; trust failure is viral "gotcha charge" complaints.

### Card 3: Payment uncertainty

Pending + inquire; audited override if lane jammed.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Payments owns money path; dual control with facility ops for overrides.

### Card 4: Occupancy is soft

Never bill from loop counters alone.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Facility Experience owns UX numbers; oversell promises destroy trust.

### Card 5: LPR privacy

Short TTL images; hashed plates; access audit.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Privacy/security review; retention bugs are PR + legal events.

### Card 6: Hot stadium event

Pre-publish surge card; edge capacity; disable sync image upload on critical path.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Capacity owner pre-games; frugality + reliability.

### Card 7: Lost ticket

Plate window search + fee + audit.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Ops tools team; abuse spikes need Trust.

### Card 8: Manual open audit

Reason codes; anomaly detection on employee ids.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Insider threat is real; mechanisms > trust.

### Card 9: Shard/cell key

Facility/operator/region; session home sticky.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Platform owns directory; wrong cell = wrong money.

### Card 10: Integer money

Cents; rounding rules; recon.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Same as retail payments—no floats.

### Card 11: GateCommand vs telemetry

Separate intent and observation; retry safely.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** IoT reliability metrics distinct from HTTP 200s.

### Card 12: DST/timezone

Facility TZ; UTC storage; golden tests.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Classic SEV class; own the tests.

### Card 13: Cash vs PSP recon

Different clearing; cassette meters.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Finance ops partnership.

### Card 14: Deal-breaker

Cloud-required open; unversioned pricing; unaudited free exits.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Say deal-breakers early—L6 signal.

### Card 15: Metrics scoreboard

Gate p99, uncertainty age, manual open rate, dispute rate, $/session.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Dashboards before launch.

### Card 16: Related designs

Payments platform, parking LLD, IoT ingest, tax.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Amazon ownership angle:** Know boundaries; don't redesign PSP mid-interview unless asked.

---

## Scenario Runbooks

### R1 — Stadium inflow

Symptoms: entry p99↑, image upload errors. Actions: shed image sync, local OCR only, scale edge, postpone analytics. Verify: barrier open rate, outbox lag.

### R2 — PSP outage

Symptoms: payments fail. Actions: allow pay-later account charge for members; cash lanes; freeze noncritical refunds. Verify: uncertainty queue; no double charges on recovery.

### R3 — Occupancy negative

Symptoms: dashboard -3. Actions: freeze UX number, recompute from open sessions + sensors, postmortem counter bugs (missed exit acks).

### R4 — Dispute spike after rate change

Actions: diff rate card versions, check pin policy, rollback card, issue refunds batch with idempotent refund keys.

### R5 — Edge certificate expiry

Symptoms: edges can't auth. Actions: emergency renew; local offline mode; post-incident cert monitoring SLO.

---

## Extended Q&A Drill (Rapid Fire)

**Q: Why not bill by camera minutes alone?**  
A: Evidence ≠ session SoT; OCR gaps; legal weak.

**Q: How do you A/B pricing?**  
A: Facility-level canary cards; not per-car random without disclosure/ethics review.

**Q: Mobile app offline pay?**  
A: Signed offline tokens carefully or defer; easy to get wrong—prefer online pay + offline exit grace for known PAID.

**Q: How to represent ADA free parking?**  
A: Product on rate card or credential entitlement; still session for occupancy.

**Q: Fleet monthly invoicing?**  
A: Aggregate sessions to invoice; payment intent at invoice level; sessions `BILLED`.

**Q: Why CAS version on session?**  
A: Prevent pay/exit races stomping state.

**Q: Can quoting mutate state?**  
A: Prefer read-only; optional `QUOTE_LOCKED` if legal needs freeze.

**Q: SMS receipt PII?**  
A: Minimize plate; deep link auth.

**Q: Multi-currency tourist garage?**  
A: Facility currency SoT; display FX optional cosmetic.

**Q: What's the first metric on your dashboard?**  
A: Stuck-lane / gate decision failures—then money.

---

## Design Alternatives (Name and Kill)

| Alternative | Why kill / defer |
|-------------|------------------|
| Fully cloud gate decisions | Outage = gridlock |
| Blockchain parking tickets | Ops & latency theater |
| One global SQL table forever | 100× tenancy pain |
| Soft real-time occupancy as ledger | Wrong charges |
| Microservice per sensor type | Death by RPC at the lane |
| ML dynamic price per car without policy | Trust / fairness / regulation |

---

## LLD Touch Points (if interviewer pivots)

Classes: `Facility`, `Lane`, `EdgeAgent`, `Session`, `Credential`, `RateCard`, `PricingEngine`, `PaymentIntent`, `Gate`, `GateCommand`, `OccupancyProjector`, `OpsAudit`.

Patterns: State machine, Strategy (pricing rules), Outbox, Idempotency store, Device twin.

Avoid 45-minute Class Explosion—sketch only if asked.

---

## Final Interview Narrative (60 seconds)

"We model a parking **session** as the source of truth, pin a **rate card version** for deterministic quotes, take **idempotent payments** with an uncertainty protocol, and keep **gate actuation edge-first** so drivers aren't hostage to the cloud. Occupancy is a derived signal, not a billing ledger. We'll scale by facility/operator cells, harden offline sync, and measure gate p99, payment uncertainty age, and dispute rate. Manual opens are always audited. Deal-breakers are cloud-obligatory opens, float money, and silent free exits."

---

## Extra Depth: Event Sourcing Option

Session as event stream (`Entered`, `CredentialBound`, `Quoted`, `PaymentSucceeded`, `ExitAuthorized`, `Closed`) with snapshots for hot paths. Great for audit; don't pay the complexity tax at 1× unless dispute volume demands it. At 100× disputes, event sourcing + receipt projections shine.

---

## Extra Depth: Tax Engine

Tax determined by facility jurisdiction + product type (parking vs EV). Pricing engine calls tax module pure function; store tax line items on receipt. Rate changes independent of parking tiers.

---

## Extra Depth: Partner Operators

Marketplace-like: Amazon Pay as tender; facility operator as merchant of record or platform of record—**clarify**. Ledger must reflect fees. Settlement reports daily. Support tooling scoped by operator_id (no cross-tenant data leaks).

---

## Extra Depth: Load Test Plan

- Replay production-shaped entry curves (not uniform).  
- Include OCR confidence distributions.  
- Inject PSP latency.  
- Validate edge memory under outbox buildup.  
- Verify idempotency under duplicate producers.  
- Chaos: partition cloud 30 minutes mid-event.

---

## Extra Depth: Observability

Structured logs with `session_id`, `facility_id`, `lane_id`, `command_id`. Trace entry→exit. Metrics RED for APIs; custom: `gate_open_fail`, `outbox_lag_seconds`, `payment_uncertain_age`. Wide events > high-cardinality label explosion on plates (hash).

---

## Closing Appendix — One-Page Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT | session_id |
| Money | integer + idempotency + recon |
| Price | pure + version pin |
| Gate | edge-first + fail-safe |
| Occupancy | soft |
| Scale | facility/operator cells |
| Privacy | hash + short image TTL |
| SEV | stuck gate / double charge |
| Kill | cloud-required open |

---

*End of Parking Payment System design notes (Amazon SDE III prep).*
