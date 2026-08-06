# System Design: Parking Payment System

> **Focus areas:** Entry/exit · Tariffs · Payments · Reservations (optional) · Occupancy · Receipts · Garage operators · Gate reliability · Money invariants  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct session lifecycle math, clear offline-gate degradation, deal-breakers for “single SQL table for everything” or “no reconciliation”, explicit Amazon ownership/cost/reliability flavor  
> **Interview theme:** Amazon SDE III / L6 — design a **parking-payment platform** that garage operators and drivers can trust: correct fees, durable sessions, gates that still work when the cloud blips

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

Goal: **bound the product**—a multi-garage parking platform where vehicles **enter**, **exit**, are charged by **tariff rules**, pay via app/kiosk/plate-account, optionally **reserve** spots, track **occupancy**, issue **receipts**, and give **garage operators** configuration + settlement—optimized for **gate availability**, money correctness, and progressive scale.

### 1.0 What this is / is not

| Dimension | **Parking payment (this doc)** | Not this |
|-----------|--------------------------------|----------|
| Primary job | Session lifecycle: enter → park → pay → exit | Full city traffic management / congestion pricing citywide |
| Success | Correct fee, gate opens, reconciliable money | Perfect computer-vision parking-spot detection MVP |
| Entities | Garage, gate, session, tariff, payment, reservation, occupancy | Ride-hail dispatch, EV charger billing as primary |
| Edge reality | Gates/kiosks may be offline | Always-on cloud required for every barrier move |
| Money | Authorize/capture or pay-on-exit; refunds; settlements to operators | Becoming a full bank/acquirer |
| Amazon lens | Ownership, reliability at the gate, cost per session, customer trust | Clever ANPR ML only |

**Scope statement:** Design a parking-payment system: entry/exit sessions, tariffs, payments, optional reservations, occupancy, receipts, operator tooling—scaled 10×/100×/1,000×—with offline-tolerant gates and money invariants.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Entry how? | Ticket / QR / LPR (license plate) / RFID / app pre-pay | Session create at gate; multiple identity modes |
| F2 | Exit how? | Pay then open; or account-based automatic | Payment before barrier; grace windows |
| F3 | Tariffs? | Time-based, flat day max, free periods, EV zones, special events | Rule engine versioned per garage |
| F4 | Payments? | Card (PSP), wallet, Apple/Google Pay, account billing, cash at kiosk | PSP adapter; cash as recorded tender |
| F5 | Reservations? | Optional Phase 1.5 — hold spot for time window | Inventory of reservable capacity |
| F6 | Occupancy? | Per-garage available/occupied; optional zone | Counters + sensors; eventually consistent OK |
| F7 | Receipts? | Email/SMS/PDF; tax fields; refundable | Immutable receipt after capture |
| F8 | Operators? | Multi-tenant garages; tariffs; reports; staff overrides | Tenant isolation; audit log |
| F9 | Lost ticket? | Flat max fee / plate lookup / staff resolve | Exception flows + operator tools |
| F10 | Validations? | Merchant stamps / validation codes reduce fee | Coupon-like reductions with audit |
| F11 | Permits / monthly? | Monthly pass, employee permit | Product type on account; gate allowlist |
| F12 | Multi-garage network? | Yes — one app, many operators | Platform + operator settlement |
| F13 | ANPR accuracy? | Best-effort; staff override path | Never hard-fail money on OCR alone |
| F14 | Refunds / disputes? | Partial/full within policy window | Ledger + PSP refund |
| F15 | Notifications? | Session start, low balance, reservation reminders | Async notify service |

**MVP functional scope:**

1. Create **parking session** on entry (ticket/QR/LPR/app).  
2. Compute **fee** from versioned tariff at exit (or continuous for account).  
3. **Pay** via PSP / account / kiosk; then authorize exit.  
4. Persist **receipt**; support refund within policy.  
5. **Occupancy** counter per garage (and optional zone).  
6. Operator: configure garage/gates/tariffs; view sessions/settlements.  
7. Staff override with audit (lost ticket, barrier open).  
8. Optional: **reservation** hold against capacity.  
9. Metrics, alarms, reconciliation vs PSP.  
10. Offline gate cache for permits/recent tickets.

**Out of MVP:**

- Citywide curb-side dynamic pricing as primary product  
- Perfect real-time camera space detection for every stall  
- In-house card acquiring / ISO8583  
- Autonomous vehicle handshake protocols  
- Full EV energy (kWh) billing as core (hook only)  
- Perfect multi-region active-active money writes

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Gate open latency | Driver waiting | p99 < 1–2 s after pay/auth (local path faster) |
| N2 | Session durability | Don’t lose entry | Durable write before barrier ACK when online; local queue offline |
| N3 | Money correctness | No double charge / silent free exit | Idempotent pay; ledger; reconcile |
| N4 | Availability | Gates critical | Local gate controller continues degraded mode |
| N5 | Occupancy freshness | Signage / app | Seconds–minutes; not money-critical |
| N6 | Consistency | Fee & payment strong; occupancy eventual | Split consistency classes |
| N7 | Multi-tenant isolation | Operators | Hard tenant boundaries; audit |
| N8 | Auditability | Disputes, tax | Append-only events + receipts |
| N9 | PCI | Minimize | PSP tokens; no PAN in our stores/logs |
| N10 | Scalability | Progressive | See scale table |
| N11 | Offline tolerance | Network blip at garage | Local allowlists + sync |
| N12 | Operability | Clear ownership | Runbooks; idempotent APIs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Driver enters → ticket/QR printed or plate captured → session `ACTIVE` → parks → pays in app → barrier opens → session `CLOSED` → receipt emailed.  
2. Account/LPR: enter → plate match → exit → auto-charge default card → open.  
3. Reserved: reserve 2h window → arrive within window → reserved capacity decremented → park → pay residual → exit.  
4. Validation: mall stamp code → fee reduced → pay remainder → exit.  
5. Monthly permit: enter/exit free within rules; occupancy still counted.  
6. Operator changes tariff at midnight → new sessions use new version; in-flight use entry-time or exit-time policy (lock with interviewer).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double pay tap | Idempotency key → one capture |
| Pay success, barrier jam | Session `PAID_PENDING_EXIT`; staff open; no re-charge |
| Barrier open without pay (tailgate) | Sensor mismatch event; exception queue; do not invent silent free policy |
| Cloud down at entry | Local ticket number from gate controller; sync later |
| Cloud down at exit with unpaid | Offline pay terminal or hold-and-bill plate; or max-fee cache |
| LPR misread | Staff correction; merge/split sessions carefully |
| Lost ticket | Max daily rate or plate search; audit override |
| Reservation no-show | Hold expires; capacity released; fee policy optional |
| Overstay after reservation | Tariff overage rules |
| Partial refund | Ledger + PSP; receipt amendment / credit note |
| Clock skew between gate and cloud | Absolute UTC; gate NTP; skew budget in grace |
| Two cars same plate (cloned) | Risk flags; do not auto-merge blindly |
| Occupancy sensor drift | Periodic recount / nightly reset with audit |
| Tariff bug overcharge | Version pin; refund tooling; feature flag rollback |
| Kiosk cash drawer mismatch | Operator reconciliation report |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Garages | 500 | 5K | 50K | 500K |
| Gates / devices | 2K | 20K | 200K | 2M |
| Sessions / day | 1M | 10M | 100M | 1B |
| Peak entry/exit events / s | 50 | 500 | 5K | 50K |
| Peak pay intents / s | 30 | 300 | 3K | 30K |
| Peak occupancy reads / s | 200 | 2K | 20K | 200K |
| Active sessions (concurrent) | 200K | 2M | 20M | 200M |
| Reservations / day | 50K | 500K | 5M | 50M |
| Operators (tenants) | 200 | 2K | 20K | 200K |
| Receipt retention | 7y | 7y | 7y | 7y+cold |

**What each jump forces:**

- **10×:** Edge gate agents; Redis occupancy; PSP webhooks; tariff service cache.  
- **100×:** Shard sessions by `garage_id` / cell; operator cells; stream analytics for occupancy; regional payment homes.  
- **1,000×:** Hierarchical cells by metro; offline-first gate OS; approximate occupancy at edge; settlement batch factories.

### 1.5 Etc. (Constraints & Assumptions)

- We **orchestrate PSP**, not become the bank.  
- Money in **minor units** integers—never float.  
- Gate controllers are first-class devices with local state.  
- “Exactly-once payment effect” ≠ single HTTP call.  
- Occupancy is **operational**, not the source of truth for money.  
- Tariff evaluation policy: lock **exit-time tariff version** or **entry-time**—state explicitly (recommend: pin `tariff_version_id` at entry for predictability; allow operator override).

**Scope statement:**

> Design a multi-tenant parking-payment platform covering entry/exit sessions, versioned tariffs, payments/refunds, optional reservations, occupancy, receipts, and operator tooling—from ~1M sessions/day through 10× / 100× / 1,000×—with offline-tolerant gates, idempotent money, and clear ownership.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
Baseline 1M sessions/day ÷ 86400 ≈ 11.6 sessions/s average
Each session ≈ 1 entry + 1 exit + 0–2 pay attempts + N occupancy updates
Peak ~4–5× average in commute windows ⇒ ~50–60 gate events/s (matches table)

Event mix (rough):
  entry           1.0×
  exit            1.0×
  payment intent  0.8×  (some permits free)
  occupancy read  heavy (apps/signage) — cacheable
  operator reads  bursty, lower volume
```

At **1,000×**: ~50K gate events/s peak → **edge aggregation** and **session shard** matter more than a single API box.

### 2.2 Storage

```text
Session row ~800 B–1.5 KB
Events (enter/exit/pay/override) ~300–500 B each; ~4–8 events/session
Receipt ~2–5 KB (PDF metadata + fields; PDF object optional)
Tariff docs small; versioned

Per session lifecycle ~5–12 KB total

1M/day × 8 KB ≈ 8 GB/day raw
Retain hot 90d; warm 2y; cold 7y for tax/dispute
100×: ~800 GB/day → object cold tier + compacted event store
1,000×: ~8 TB/day → aggressive compaction, columnar analytics separate
```

### 2.3 Bandwidth

```text
Gate heartbeats: 2K devices × 1 msg/10s = 200 msg/s baseline
Payload small (~200 B) ⇒ tens of KB/s control plane

ANPR image upload optional: 50–200 KB/image
If 30% entries upload image at 50/s peak × 100 KB = 5 MB/s — put behind async + retention policy

Pay to PSP: similar to checkout (~5–20 KB)
```

### 2.4 Memory / hot state

```text
Active sessions 200K × 1 KB = 200 MB metadata (tiny)
At 1,000×: 200M × 1 KB = 200 GB → **not one Redis**; shard by garage/cell

Occupancy: garage → counters; 500 garages trivial; 500K garages still small if sharded
Permit allowlists per garage: cache on gate controller (MB-scale)
```

### 2.5 Latency budget (exit pay → open)

```text
App pay confirm → API  50–100 ms
PSP auth/capture      300–1500 ms  (dominant)
Session update + token 20–50 ms
Gate command           20–100 ms
-------------------------------
Target: show "authorized" fast; barrier via signed short-lived exit token
Account/LPR path can pre-auth or post-pay with risk tier
```

### 2.6 Occupancy math

```text
Garage capacity C=800; occupied O; available A=C-O
Updates on enter/exit (+sensor corrections)
Signage poll 1 Hz × 500 garages = 500 rps — serve from cache
Do NOT lock money path on occupancy correctness
```

### 2.7 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | PSP + session DB | Idempotency store; read replicas; edge cache tariffs |
| 100× | Hot downtown garages | Cell by metro; per-garage partition; gate local autonomy |
| 1,000× | Device fleet + settlements | Hierarchical ops; batch settlement; edge-first session |

### 2.8 Money volume sketch

```text
Avg ticket $12; 1M sessions/day × 0.8 paid ≈ $9.6M/day GMV baseline
Platform fee 5–15% → settlement files dominate finance ops at 100×+
```

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Customer trust:** fee explainable; receipt durable; disputes solvable.  
2. **Gate uptime > cloud purity:** degrade gracefully; never brick a garage for a deploy.  
3. **Money invariants:** idempotent pay; ledger; reconcile.  
4. **Operator ownership:** clear tenant boundaries; self-serve tariffs.  
5. **Cost awareness:** images and PDFs are cost centers—policy them.  
6. **Progressive scale:** cells when a metro becomes a hotspot.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| API Gateway / BFF | Driver app, kiosk, operator console |
| Session Service | Enter/exit lifecycle, state machine |
| Tariff Engine | Versioned rules → fee quote |
| Payment Orchestrator | PSP, account billing, cash tenders |
| Ledger / Receipts | Money postings + customer receipts |
| Reservation Service | Optional holds against capacity |
| Occupancy Service | Counters, signage feeds |
| Device / Gate Agent | Local controller, offline cache, commands |
| Operator Admin | Garages, staff, tariffs, settlements |
| Notify | Email/SMS/push |
| Recon Jobs | PSP vs ledger vs operator payouts |
| Identity | Drivers, plates, permits, staff RBAC |

### 3.3 Session state machine

```text
CREATED → ACTIVE → PAYMENT_PENDING → PAID → EXITING → CLOSED
                ↘ VOIDED / CANCELLED (never entered / operator cancel)
PAID → REFUND_PENDING → REFUNDED / PARTIAL
ACTIVE → EXCEPTION (lost ticket, misread) → resolved → CLOSED
```

**Invariant:** barrier open for paid exit requires `PAID` (or permit/`ACCOUNT_OK`) + unexpired exit authorization token.

### 3.4 Tariff model (say this clearly)

```text
TariffVersion {
  garage_id, version, effective_from, timezone,
  rules: [
    { type: FREE_MINUTES, n: 15 },
    { type: PER_HOUR, rate_cents: 400, cap_cents: 3200 },
    { type: EV_ZONE_MULTIPLIER, zone: "B", mult: 0.9 },
    { type: EVENING_FLAT, after: "18:00", rate_cents: 500 },
    ...
  ]
}
```

Evaluation inputs: `entered_at`, `exited_at`, `zone`, `vehicle_class`, `validations[]`, `product` (transient vs monthly).

**Deal-breaker:** hardcoding rates in gate firmware without cloud version pin → unfixable disputes.

### 3.5 API sketch

```text
POST   /v1/garages/{gid}/sessions:enter
POST   /v1/sessions/{sid}/quote
POST   /v1/sessions/{sid}/payments          Idempotency-Key required
POST   /v1/sessions/{sid}/exit-authorize
POST   /v1/sessions/{sid}/exit-complete
POST   /v1/reservations
DELETE /v1/reservations/{rid}
GET    /v1/garages/{gid}/occupancy
GET    /v1/receipts/{rid}
POST   /v1/operator/tariffs
POST   /v1/operator/overrides               audited
POST   /v1/devices/{did}/heartbeat
POST   /v1/devices/{did}/events             batch sync
```

### 3.6 Data model (logical)

| Entity | Key fields |
|--------|------------|
| Garage | garage_id, operator_id, timezone, capacity, status |
| Gate | gate_id, garage_id, type (entry/exit/both), device_id |
| Session | session_id, garage_id, plate?, ticket_id, entered_at, exited_at, state, tariff_version_id, fee_cents |
| Payment | payment_id, session_id, amount_cents, status, psp_refs, idem_key |
| LedgerEntry | entry_id, accounts, amount, session_id, payment_id |
| Receipt | receipt_id, session_id, payload_hash, storage_key |
| Reservation | res_id, garage_id, window, plate/user, state |
| Occupancy | garage_id, zone?, occupied, capacity, updated_at |
| Permit | permit_id, plate/user, garage_scope, valid_range |
| TariffVersion | as above |
| DeviceEvent | device_id, seq, type, payload, received_at |

**Access patterns:** get session by id; open sessions by plate+garage; payments by idem_key; occupancy by garage; operator queries by garage+time range (secondary index / analytics).

### 3.7 Payment options

| Mode | When | Notes |
|------|------|-------|
| Pay-on-exit (card) | Transient parkers | Auth+capture at exit |
| Pre-pay / extend | App while parked | Captures increments; exit validates paid-through |
| Account / LPR | Commuters | Post-pay invoice or auto-charge; risk scoring |
| Cash kiosk | Unbanked | Tender recorded; still ledger |
| Permit | Monthly | Gate allowlist; no per-exit capture |

### 3.8 Reservations (optional)

- Reserve **capacity token**, not necessarily a numbered stall (unless garage supports stall inventory).  
- Hold with TTL; convert to session on entry match.  
- No-show releases hold; optional fee.  
- Overbooking policy: operator sets buffer % for walk-ins vs reserved.

### 3.9 Occupancy

```text
enter: O += 1 (clamp 0..C)
exit:  O -= 1
sensor recount: set O with source=SENSOR, confidence
```

Serve app/signage from cache; rebuild from active sessions nightly as audit.

### 3.10 Offline gate design (critical)

Gate Agent responsibilities:

1. Local SQLite/Rocks of recent tickets, permits, signed fee schedules.  
2. Issue local ticket IDs from allocated ranges.  
3. Queue device events with monotonic `seq`.  
4. Degraded exit: allow permit; allow prepaid QR; else max-fee escrow or “pay within 24h” plate bill.  
5. Sync when online; cloud is source of truth after merge.

**Amazon interview line:** *Availability of the physical gate beats perfect online consistency.*

### 3.11 Tradeoffs table

| Decision | Option A | Option B | Choose when |
|----------|----------|----------|-------------|
| Fee pin | Entry tariff version | Exit latest | Predictability vs promo flexibility |
| LPR source of truth | Plate primary | Ticket primary, plate assist | ANPR quality |
| Occupancy | Session-derived | Sensor-primary | Capex vs accuracy |
| Money home | Per operator cell | Global ledger | Scale / compliance |
| Exit auth | Server token | Device-local after pay | Latency / offline |
| Images | Always store | Sample / dispute-only | Cost |

### 3.12 Deal-breakers

1. Single shared DB table for all sessions worldwide without shard key.  
2. Charging twice on retry without idempotency.  
3. Requiring cloud RTT before every barrier move with no degraded mode.  
4. Occupancy counter used as billing source of truth.  
5. No reconciliation between PSP and operator settlements.  
6. Staff overrides without audit trail.  
7. Float money / timezone-naive tariff math.  
8. Firmware-only tariffs with no version history.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
                    +------------------+
   Driver App ----->|     API / BFF    |<---- Operator Console
   Kiosk/POS ------->|                  |<---- Staff handheld
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
  +-------------+    +--------------+    +---------------+
  |  Session    |    |   Tariff     |    | Reservation   |
  |  Service    |<-->|   Engine     |    | Service       |
  +------+------+    +--------------+    +-------+-------+
         |                                       |
         v                                       v
  +-------------+    +--------------+    +---------------+
  |  Payment    |--->|   Ledger /   |    | Occupancy     |
  |  Orch+PSP   |    |   Receipts   |    | Service       |
  +------+------+    +------+-------+    +-------+-------+
         |                  |                    |
         v                  v                    v
     [PSP]            [Object Store]         [Cache]
                             |
                             v
                      [Notify / Email]

  Garage edge:
  +------------------+   sync/events    +------------------+
  | Gate Controller  |<---------------->| Device Gateway   |
  | (local agent)    |   commands       | (cloud)          |
  +--------+---------+                  +------------------+
           |
     Barrier / LPR / Ticket printer
```

### 4.2 Sequence: pay-on-exit

```text
Driver          App/API         Payment         Session        Gate
  |               |               |               |             |
  |--pay--------->|               |               |             |
  |               |--idem create->|               |             |
  |               |               |--PSP capture->|             |
  |               |               |--ledger------>|             |
  |               |               |               |--PAID------>|
  |               |<--exit token--|               |             |
  |--present QR-->|               |               |             |
  |               |--authorize------------------->|--open------>|
  |               |               |               |--CLOSED---->|
  |<--receipt-----|               |               |             |
```

### 4.3 Sequence: offline entry + later sync

```text
Car -> Gate Agent: allocate ticket T from local range
Gate Agent: store local session; print QR; open barrier
... network restored ...
Gate Agent -> Device Gateway: events[seq=...]
Session Service: upsert session; conflict rules by ticket_id
```

### 4.4 Sequence: reservation → session

```text
User -> Reservation: hold capacity (TTL)
User arrives -> Enter matches res_id/plate
Session links reservation; hold consumed
No-show job: expire holds; release capacity
```

### 4.5 Cell architecture at 100×+

```text
                   +-------------------+
                   | Global Directory  |
                   | (garage -> cell)  |
                   +---------+---------+
                             |
         +-------------------+-------------------+
         v                   v                   v
   [Cell Metro A]      [Cell Metro B]      [Cell Metro C]
   sessions/payments   sessions/payments   ...
   local device GW     local device GW
         |                   |
         v                   v
   Garages A*            Garages B*
```

Money and sessions for a garage are **single-home** to one cell. Cross-cell driver accounts may be global with pointers.

### 4.6 Occupancy data path

```text
Enter/Exit events --> Occupancy Service --> Redis counters
Sensor recount   --> Occupancy Service --> reconcile job
App/Signage <----- cached reads (CDN/edge for public)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Every barrier entry creates a durable session** (cloud or local-then-sync).  
2. **No double economic capture** for the same idempotency key / session pay intent.  
3. **Paid exit authorization is signed & short-lived** (e.g. 5–15 minutes).  
4. **Receipt hash matches ledger capture** for the charged amount.  
5. **Staff override always audited** with actor, reason, before/after.  
6. **Tariff version used is recorded** on the session.  
7. **Occupancy never silently “fixes” unpaid exits.**

#### 5.1.2 Failure modes

| Failure | User impact | Mitigation |
|---------|-------------|------------|
| PSP timeout unknown | Driver waits | PENDING + inquire; do not double auth |
| Cloud outage | Gates degrade | Local permits/tickets; sync queue |
| Gate agent crash | Lane down | Watchdog; redundant controller optional |
| Session DB partition | Writes fail online | Fail closed for new cloud sessions; local tickets |
| Occupancy wrong | Bad signage | Nightly rebuild; sensor fusion |
| Clock skew | Wrong fee | NTP; grace minutes; UTC storage |
| Poison device flood | Cloud melt | Per-device rate limits; batching |
| Bad tariff deploy | Overcharge | Version pin; instant rollback; refund job |

#### 5.1.3 Durability & backup

- Sessions/payments: multi-AZ DB; PITR.  
- Device event log: append-only, replayable.  
- Receipts: object store with immutability / WORM optional for tax.  
- Test restore of settlement day packs quarterly.

#### 5.1.4 Consistency nuances

| Data | Consistency |
|------|-------------|
| Payment + session state | Strong / single writer per session |
| Ledger | Strong append; unique constraints |
| Occupancy | Eventual; monotonic clamps |
| Permit allowlist on gate | TTL cache; periodic refresh |
| Operator reports | Eventually consistent analytics |

#### 5.1.5 Security

- Device mutual TLS / signed tokens; rotate credentials.  
- RBAC for operator staff; least privilege for overrides.  
- PCI: hosted fields / PSP tokens only.  
- Plate PII: encrypt at rest; retention policy; access audit.  
- Signed exit tokens (Ed25519) with garage scope.  
- Fraud: cloned plates, repeated lost-ticket pattern.

### 5.2 Scalability

#### 5.2.1 Partitioning

| Entity | Partition key | Notes |
|--------|---------------|-------|
| Session | `garage_id` or `hash(session_id)` with garage secondary | Operator queries by garage+time |
| Payment | `session_id` home | Idempotency table sharded by key |
| Occupancy | `garage_id` | Hot downtown OK—single counter row |
| Device events | `device_id` | Ordered by seq |
| Driver account | `user_id` | Global directory |

Hot garage: isolate on dedicated shards; do not let one stadium crush others.

#### 5.2.2 Device fleet scale

```text
2M devices @ 1,000×:
  heartbeat every 30s → ~67K msg/s
  → MQTT/IoT hub style fan-in
  → aggregate locally; cloud sees batches
```

#### 5.2.3 Payment path scaling

- Stateless payment workers.  
- Idempotency KV sharded.  
- PSP connections pooled per region.  
- Webhook ingest durable queue; applicator workers.  
- Single-writer session updates via optimistic locking / conditional writes.

#### 5.2.4 Tariff engine scaling

- Tariffs change rarely → cache aggressively at API and gate.  
- Deterministic pure function: `(tariff_version, context) → quote`.  
- Property tests for fee math; golden files per operator.

#### 5.2.5 Multi-region

| Mode | Pattern |
|------|---------|
| MVP | Regional cloud + global CDN for app |
| Growth | Metro cells; garage pinned |
| 1,000× | Edge-heavy; cell autonomous for sessions |

Avoid active-active writers for the same session.

#### 5.2.6 Cost controls (owner talk)

| Driver | Control |
|--------|---------|
| ANPR images | Sample, compress, short retention unless dispute |
| SMS receipts | Email default; SMS opt-in |
| PSP fees | Account/LPR batching where risk allows |
| Hot shards | Stadium events capacity planning |
| Operator analytics | Batch warehouse, not OLTP scans |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owning team |
|---------|-------------|
| Session + gate protocol | Parking Sessions |
| Tariff engine | Pricing |
| Payments + ledger | Payments |
| Device agent / IoT | Edge Fleet |
| Occupancy / signage | Garage Experience |
| Operator console | Operator Product |
| Recon / settlements | FinOps eng + Finance |
| Fraud / plate abuse | Trust |

#### 5.3.2 Safe evolution

- Tariff versions immutable once effective.  
- Device protocol versioned (`proto_v`).  
- Session state machine additive transitions only.  
- Feature flags for reservation rollout per operator.  
- Contract tests between gate agent and cloud.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Exit authorize success (online) | 99.9% |
| Gate command p99 | < 500 ms after authorize |
| Payment capture success (excl. issuer decline) | track separately from declines |
| Device sync lag p95 | < 60 s when online |
| Occupancy staleness p95 | < 30 s |
| Recon exception rate | < 0.1% of captures |

Alarms: sync lag, unknown PSP pending age, override spike, occupancy clamp hits, tariff eval errors.

#### 5.3.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Session SM, tariff versions, PSP+idempotency, receipts, basic occupancy |
| 10× | Gate agent offline, webhooks, Redis occupancy, operator audit |
| 100× | Metro cells, sharded sessions, settlement automation, device batching |
| 1,000× | Edge-first sessions, hierarchical ops, approx occupancy edge fanout |

### 5.4 Deep dive: fee quotation & disputes

```text
quote = TariffEngine.eval(version, enter, exit, extras)
persist QuoteSnapshot { lines[], total_cents, version, hash }
payment.amount MUST equal snapshot.total (or explicit override)
dispute → show line items: free window, hourly, validation, tax
```

Never recompute a historical fee with “today’s” engine without the snapshot.

### 5.5 Deep dive: LPR merge/split

| Scenario | Action |
|----------|--------|
| Misread creates orphan session | Staff merge tool; keep audit |
| Two cars share plate string | Require ticket secondary factor |
| Exit plate ≠ entry | Exception lane; do not auto-charge wrong session |

### 5.6 Deep dive: reservation inventory

```text
capacity C
reservable R = floor(C * reserve_ratio)
walk_in W = C - R
holds H(t) active
on reserve: if H < R and O + H < C - walk_in_buffer → accept
```

Stadium event: dynamic `reserve_ratio` via operator config with change windows.

### 5.7 Deep dive: reconciliation

Daily loop:

1. Import PSP settlement.  
2. Match `payment_id` / PSP ids to ledger.  
3. Compute operator net: captures − refunds − platform fee − chargebacks.  
4. Exceptions queue with aging SLO.  
5. Payout file / transfer initiation (banking partner).

**Never** “fix” operator balances by silently adjusting without ticketed exception.

### 5.8 Deep dive: exit token

```text
ExitToken {
  session_id, garage_id, gate_scope?, amount_cents,
  exp, nonce, sig
}
Gate verifies sig with garage public key; checks exp; marks nonce used (local LRU)
```

### 5.9 Testing & resilience

- Fee engine golden tests per tariff fixture.  
- Chaos: drop cloud link during entry/exit.  
- Idempotency fuzz on pay API.  
- Clock skew tests ±5 minutes.  
- Load: commute peak simulation on hot garage.  
- Device replay: duplicate `seq` must be ignored.

### 5.10 Amazon leadership connection (brief)

- **Customer Obsession:** explainable fees, fast gates, clear receipts.  
- **Ownership:** you own recon exceptions and gate fleet health, not just API latency.  
- **Bias for Action:** offline degraded mode shipping > waiting for perfect connectivity.  
- **Frugality:** don’t store every ANPR frame forever.  
- **Deliver Results:** settlement correctness is a product metric.

---

## 6. Wrap-Up

### 6.1 30-second recap

Multi-tenant parking platform: **session state machine** at the core, **versioned tariffs**, **idempotent payments + ledger**, **edge gate agents** for offline, **occupancy** as a separate eventually-consistent feed, optional **reservations**, durable **receipts**, operator admin + **reconciliation**. Scale by **garage/metro cells**, not one global session table.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Why |
|----------|--------|-----|
| Online purity vs gate uptime | Edge degraded mode | Physical world |
| Sensor vs session occupancy | Session primary + sensor audit | Money safety |
| Entry vs exit tariff pin | Pin at entry (default) | Predictability |
| Stall-level vs capacity reserve | Capacity tokens MVP | Simpler inventory |
| Pre-pay vs post-pay LPR | Risk-tiered | Fraud vs UX |

### 6.3 Risks & follow-ups

- ANPR accuracy and privacy regulation  
- Chargeback / plate dispute workflows  
- EV charging add-on billing  
- Dynamic event pricing  
- Cross-operator roaming accounts  
- Stronger stall-level guidance

### 6.4 What “good” looks like

- Interviewer hears **idempotency**, **tariff versions**, **offline gates**, **recon**, **cell sharding**  
- Clear split: money strong / occupancy eventual  
- Progressive 10×/100×/1,000× without hand-waving  
- Ownership and cost called out like an L6

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q1 | Ticket or plate primary? | Support both; ticket more reliable for disputes |
| Q2 | When is fee finalized? | At exit quote snapshot; pin tariff version |
| Q3 | Cash support? | Kiosk tender + ledger; still need digital receipt option |
| Q4 | Monthly permits in MVP? | Allowlist product; yes if commute-heavy |
| Q5 | Multi-currency? | Per garage currency; minor units |
| Q6 | Tax? | Line items; jurisdiction config |
| Q7 | Valet mode? | Separate flow; same session/payment backbone |
| Q8 | Airports vs malls? | Same core; different tariff + reservation ratios |
| Q9 | Accessibility grace? | Tariff rules / overrides |
| Q10 | Fleet cards? | Account billing product |
| Q11 | Who is merchant of record? | Platform vs operator—lock for settlement |
| Q12 | SLA for gate open? | Local path SLO separate from cloud pay SLO |

### 7.2 Sessions & gates (Q13–Q24)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q13 | Offline entry ID allocation? | Pre-allocated ranges per device |
| Q14 | Duplicate event delivery? | device_id+seq unique |
| Q15 | Barrier open timeout? | Retry command; staff path |
| Q16 | Tailgating? | Loop detectors; exception events |
| Q17 | Anti-passback? | Policy per garage; soft vs hard |
| Q18 | Long-term parkers? | State remains ACTIVE; quote grows |
| Q19 | Session without exit? | Aging job; plate bill / max fee |
| Q20 | Clock failure on gate? | Refuse money-critical local eval beyond skew budget |
| Q21 | Firmware update strategy? | Staged; never brick; dual-partition |
| Q22 | How to test gate in CI? | Protocol contract + emulator |
| Q23 | Multiple entries one ticket? | Reject / anti-passback |
| Q24 | Nested garages? | Parent/child occupancy + tariff zones |

### 7.3 Tariffs & fees (Q25–Q36)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q25 | How to avoid float errors? | Integer cents; tested rules |
| Q26 | DST / timezone? | Garage TZ; store UTC instants |
| Q27 | Cap vs cumulative? | Explicit rule ordering |
| Q28 | Free minutes stacking with validation? | Deterministic precedence table |
| Q29 | Event surge pricing? | New tariff version with effective window |
| Q30 | Can staff edit fee? | Override with reason + ceiling policy |
| Q31 | Quote then price change? | Snapshot binding for N minutes |
| Q32 | Tax inclusive vs exclusive? | Config per operator |
| Q33 | Rounding? | Document banker’s vs half-up; golden tests |
| Q34 | EV discount? | Vehicle class / zone attribute |
| Q35 | Grace after pay? | Exit token TTL |
| Q36 | Why version immutability? | Dispute replay |

### 7.4 Payments & money (Q37–Q52)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q37 | Idempotency key scope? | Per driver device + session pay intent |
| Q38 | Auth vs capture? | Auth at quote; capture on confirm—or auto-capture |
| Q39 | Partial capture? | Rare; prefer re-quote |
| Q40 | Refund window? | Policy; credit note |
| Q41 | PSP webhook vs sync response? | Converge idempotently |
| Q42 | Unknown timeout? | PENDING inquire job |
| Q43 | Double-entry needed? | Yes for platform-grade settlement |
| Q44 | Cash over/short? | Operator recon report |
| Q45 | Chargeback? | Dispute SM; provisional accounting |
| Q46 | Account post-pay unpaid? | Collections; gate deny list |
| Q47 | Split tender cash+card? | Multiple tenders; one session |
| Q48 | Tips? | Out of MVP |
| Q49 | Foreign cards? | PSP handles; FX fees surfaced |
| Q50 | Receipt legal fields? | Operator legal entity on receipt |
| Q51 | Exactly-once? | Exactly-once **effect** via idempotency + ledger uniqueness |
| Q52 | Why not pay in SQL trigger? | Orchestration + PSP uncertainty |

### 7.5 Reservations & occupancy (Q53–Q64)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q53 | Reserve specific stall? | Later; capacity token first |
| Q54 | Overbooking? | Buffer config; business choice |
| Q55 | No-show fee? | Capture hold authorization |
| Q56 | Occupancy > capacity? | Clamp + alert; investigate sensors |
| Q57 | Public API for availability? | Cached; rate limited |
| Q58 | Zone occupancy? | Child counters |
| Q59 | Real-time map of empty stalls? | CV system optional; separate |
| Q60 | Reservation + monthly permit? | Precedence rules |
| Q61 | Cancel reservation? | Release hold; refund policy |
| Q62 | Walk-in vs reserved starvation? | reserve_ratio |
| Q63 | Rebuild occupancy? | Count ACTIVE sessions |
| Q64 | Signage offline? | Last-known + “may be inaccurate” |

### 7.6 Scale, multi-tenant, ops (Q65–Q76)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q65 | Shard key? | garage_id / metro cell |
| Q66 | Hot stadium garage? | Dedicated shard + edge autonomy |
| Q67 | Noisy neighbor operator? | Per-tenant rate limits |
| Q68 | Multi-region driver account? | Global identity; local sessions |
| Q69 | Analytics vs OLTP? | Event stream → warehouse |
| Q70 | PII retention? | Policy by jurisdiction |
| Q71 | GDPR delete driver? | Anonymize; keep money records as required |
| Q72 | Device credential leak? | Rotate; revoke; anomaly detect |
| Q73 | Blue/green API? | Yes; device protocol careful |
| Q74 | Cost of 1,000× images? | Don’t default store all |
| Q75 | On-call ownership? | Follow the sun by cell optional |
| Q76 | Migration of garage to new cell? | Dual-write window; freeze; cutover |

### 7.7 Behavioral / Amazon (Q77–Q80)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q77 | Gate down during peak—what do you do? | Local mode; staff SOP; postmortem; capacity |
| Q78 | Overcharge incident | Stop rollout; refund job; root cause on tariff version |
| Q79 | Tradeoff speed vs correctness | Never sacrifice money invariants; occupancy can lag |
| Q80 | How do you know you’re done for MVP? | Enter/pay/exit/receipt/recon path demoable + offline entry |

---

## 8. Appendices

### Appendix A — Session status cheat sheet

| Status | Meaning |
|--------|---------|
| CREATED | Reserved id / pre-entry |
| ACTIVE | Vehicle in garage |
| PAYMENT_PENDING | Quote issued |
| PAID | Money captured / permit OK |
| EXITING | Barrier authorized |
| CLOSED | Completed |
| EXCEPTION | Needs staff |
| REFUNDED / PARTIAL | Money reversed |

### Appendix B — Example session record (Dynamo-ish)

```json
{
  "pk": "GARAGE#g_123",
  "sk": "SESSION#s_9f...",
  "session_id": "s_9f...",
  "ticket_id": "T-2026-88421",
  "plate": "enc:...",
  "state": "ACTIVE",
  "entered_at": "2026-08-06T16:02:11Z",
  "tariff_version_id": "tv_77",
  "zone": "A",
  "reservation_id": null,
  "fee_cents": null,
  "gsi1pk": "PLATE#hash",
  "gsi1sk": "ACTIVE#g_123"
}
```

### Appendix C — Quote snapshot sketch

```json
{
  "session_id": "s_9f...",
  "tariff_version_id": "tv_77",
  "currency": "USD",
  "lines": [
    {"code": "FREE_MIN", "cents": 0},
    {"code": "HOURLY", "minutes": 97, "cents": 800},
    {"code": "VALIDATION", "cents": -200},
    {"code": "TAX", "cents": 48}
  ],
  "total_cents": 648,
  "hash": "sha256:..."
}
```

### Appendix D — Exit token (logical)

```text
base64url(payload).sig
payload = {sid, gid, amt, exp, nonce}
```

### Appendix E — Device event types

| type | payload |
|------|---------|
| ENTRY | ticket_id, plate?, lane, ts |
| EXIT_REQUEST | ticket_id / token |
| EXIT_COMPLETE | barrier result |
| HEARTBEAT | versions, queue_depth |
| OVERRIDE | staff_id, reason |
| SENSOR | loop/occupancy raw |

### Appendix F — Error codes

| Code | Meaning |
|------|---------|
| SESSION_NOT_FOUND | Unknown ticket/plate |
| ALREADY_PAID | Idempotent success |
| IDEMPOTENCY_MISMATCH | Same key, different body |
| QUOTE_EXPIRED | Re-quote required |
| TARIFF_EVAL_ERROR | Fail closed |
| GATE_UNREACHABLE | Paid but pending exit |
| CAPACITY_FULL | Reservation/entry deny policy |
| PERMIT_INVALID | Allowlist miss |
| OFFLINE_DEGRADED | Limited methods only |

### Appendix G — Anti-patterns (deal-breakers)

1. Global auto-increment ticket ids without garage scope.  
2. Recomputing historical fees without snapshots.  
3. Using occupancy to decide whether payment existed.  
4. Storing PAN.  
5. Unlimited staff free-exit without audit.  
6. One Redis for 200M active sessions.  
7. Blocking barrier on analytics warehouse.  
8. Ignoring PSP pending states.

### Appendix H — Capacity worksheet

```text
sessions/day = ____
peak multiplier = ____
gates = ____
avg fee = ____
image % = ____
retention hot/warm/cold = ____ / ____ / ____
cell count = ____
```

### Appendix I — 45-minute timebox

| Min | Focus |
|-----|-------|
| 0–5 | FR/NFR; offline + money |
| 5–12 | Estimation; commute peaks |
| 12–25 | HLD; session SM; components |
| 25–35 | Deep dive: pay + gate offline OR tariff |
| 35–42 | Scale 10×/100×/1,000×; cells |
| 42–45 | Wrap risks/ownership |

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| LPR/ANPR | License plate recognition |
| Exit token | Signed short-lived barrier auth |
| Tariff version | Immutable priced ruleset |
| Cell | Blast-radius / shard unit (often metro) |
| Tender | Payment method instance applied |
| Anti-passback | Prevent credential reuse patterns |
| Occupancy | Operational fill level |
| Recon | Match money across systems |

### Appendix K — Ownership RACI (sample)

| Activity | Sessions | Payments | Edge | Operator | Finance |
|----------|----------|----------|------|----------|---------|
| Gate protocol | A/R | C | R | C | I |
| Capture/refund | C | A/R | I | I | C |
| Tariff config | C | I | I | A/R | C |
| Settlement | I | R | I | C | A |
| Occupancy UX | C | I | C | A/R | I |

### Appendix L — Progressive scale one-pager

| Scale | Architecture snapshot |
|-------|----------------------|
| 1× | Monolith-ok services; one region; PSP; Postgres/Dynamo sessions |
| 10× | Gate agents; webhook workers; Redis occupancy |
| 100× | Metro cells; sharded sessions; automated settlement |
| 1,000× | Edge-first; IoT fan-in; hierarchical operator ops |

### Appendix M — Comparison vs tolling / EV charging

| | Parking | Road toll | EV charge |
|--|---------|-----------|-----------|
| Duration | Hours | Seconds | Hours + kWh |
| Inventory | Spaces | Gantries | Connectors |
| Offline | Critical | Critical | Critical |
| Fee inputs | Time/zone | Gantries/miles | kWh + time |

Shared: device edge, payments, recon. Different: inventory semantics.

### Appendix N — Minimal threat model

| Threat | Mitigation |
|--------|------------|
| Stolen exit token | Short TTL; nonce; mTLS gate |
| Plate cloning | Risk scores; secondary factor |
| Fraudulent validation codes | Single-use; merchant auth |
| Insider free exits | Audit + anomaly |
| Device spoofing | Provisioned identity |
| Receipt tampering | Hash + WORM store |

### Appendix O — Fee engine pseudocode

```text
function quote(version, ctx):
  lines = []
  minutes = floor((ctx.exit - ctx.enter) / 60)
  minutes = apply_free(version, minutes, lines)
  cents = apply_rates(version, minutes, ctx, lines)
  cents = apply_validations(ctx.validations, cents, lines)
  cents = apply_tax(version, cents, lines)
  return Snapshot(lines, cents, hash(version, lines))
```

### Appendix P — Offline policy matrix

| Scenario | Allowed |
|----------|---------|
| Permit valid locally | Open |
| Prepaid QR unexpired | Open |
| Unknown transient | Issue local ticket; bill later OR max cache | 
| Exit unpaid + no local pay | Hold lane / plate invoice |
| Sync conflict | Cloud wins money; merge events by seq |

### Appendix Q — Sample enter response

```json
{
  "session_id": "s_9f...",
  "ticket_id": "T-2026-88421",
  "garage_id": "g_123",
  "entered_at": "2026-08-06T16:02:11Z",
  "tariff_version_id": "tv_77",
  "qr": "https://park.example/t/T-2026-88421"
}
```

### Appendix R — Interview “say this” (60 seconds)

> “I’d model parking as a **session state machine** per garage, with **immutable tariff versions** and a **quote snapshot** bound to payment. Payments are **idempotent** through a PSP with a **ledger and daily recon**. Gates run an **edge agent** with offline ticket ranges and permit caches because **lane availability beats cloud chattiness**. Occupancy is **eventually consistent** and never sources money. At scale we **cell by metro**, shard sessions by garage, and treat device fan-in as an IoT problem. Success is correct fees, open gates, and settlements finance trusts.”

### Appendix S — Related systems map

```text
Parking Sessions ── Payments/Ledger ── PSP
       │                 │
       ├── Occupancy     ├── Notify
       ├── Reservations  └── Settlements
       └── Edge Devices
Identity / Permits / Operator Admin
```

### Appendix T — Chaos drill list

1. Kill cloud API during entry rush.  
2. Duplicate webhook capture.  
3. Replay device events out of order.  
4. Deploy bad tariff version.  
5. Fill occupancy counter past capacity artificially.  
6. PSP 15s latency spike.  
7. Gate agent disk full.  
8. DST transition evening peak.

---

*End of parking-payment system design (Amazon SDE III style).*
