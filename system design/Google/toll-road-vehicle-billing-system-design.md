# System Design: Toll-Road Vehicle Billing

> **Focus areas:** Event ingestion · Duplicate observations · Trip stitching · Pricing · Reconciliation · Late events · Privacy  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar event/charge/recon classes, explicit idempotent charge keys, resolved late-event & clock-skew policy  
> **Interview theme:** High-volume IoT-ish telemetry meets money movement — correctness under duplicates, out-of-order arrivals, and bank settlement, not “just Kafka”

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—a multi-roadway electronic tolling / vehicle billing platform that ingests gantry observations (camera OCR, RFID/transponder, optional ANPR+AVC), stitches trips or point charges, prices them, bills accounts or plate invoices, handles disputes, and reconciles with banks/PSPs. Fundamentals: **idempotent money**, **dedup under messy sensors**, **late events**.

### 1.0 What this is / is not

| Dimension | **Toll-road vehicle billing (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Observe vehicles → charge correctly → settle | Full traffic control / V2X routing |
| Success | Correct charge ≤ SLA; low dispute rate; recon matches banks | Perfect OCR alone |
| Data | Events, trips, charges, payments, disputes | Live map navigation |
| Money | Idempotent charges + ledger + PSP recon | Crypto micropayments MVP |
| Offline gantries | Store-and-forward with clock skew | Require always-online gantries |

**Scope statement:** Design **toll-road vehicle billing**: ingest gantry/camera/RFID events, deduplicate observations, stitch trips, price, bill, dispute, and reconcile with payment rails—correct under duplicates, late arrivals, and offline store-and-forward.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who pays? | Registered RFID/account holders + unregistered plate invoices | Two billing paths; plate privacy |
| F2 | Charge model? | Point tolls + optional entry/exit trip tolls | Trip stitcher + pricing engine |
| F3 | Sensors? | RFID primary when present; camera OCR fallback; AVC (axles/class) | Multi-source fusion; confidence |
| F4 | Duplicate events? | Same vehicle seen by redundant cameras / retries | Dedup windows; observation IDs |
| F5 | Late events? | Offline gantries upload hours later | Reopenable trips; charge adjustments |
| F6 | Pricing? | Tables by road, class, time-of-day, congestion | Versioned price books |
| F7 | Disputes? | Customer claims wrong plate / wrong trip | Evidence pack; adjust ledger |
| F8 | Payments? | Card/ACH via PSP; prepaid balance optional | Idempotent charge keys; recon |
| F9 | Enforcement? | Export unpaid plates to DMV/collections Phase 2 | Outbox to partners |
| F10 | Multi-operator? | One platform, many road agencies | Tenant = agency; settlement |
| F11 | Privacy? | Plates are PII; retention limits | Hash/tokenize; access audit |
| F12 | Clock skew? | Gantries NTP imperfect; offline clocks drift | Event time vs ingest time; skew bounds |

**MVP functional scope:**

1. Ingest observation events (RFID read, OCR plate+confidence, AVC class, gantry_id, event_time, device_seq).  
2. **Dedup** near-duplicate observations within spatial/temporal windows.  
3. **Identify** vehicle: RFID → account; else plate → account or guest invoice.  
4. **Trip stitch** for entry/exit roads; point charge for open gantries.  
5. **Price** via versioned tables; create **idempotent Charge** with charge key.  
6. **Bill**: debit prepaid / authorize PSP / generate plate invoice.  
7. **Dispute** workflow with evidence (images refs, observation set).  
8. **Reconcile** daily with PSP/bank files; exception queue.  
9. Offline gantry **store-and-forward** with monotonic device sequence.  
10. Metrics: charge accuracy proxies, dedup rate, late-event lag, recon break $.

**Out of MVP:**

- Real-time congestion pricing ML optimizer (hooks: price book version)  
- Cross-border EU/EETS full interoperability (hooks: agency settlement)  
- Perfect multi-camera 3D tracking  
- In-lane barrier gate control loops (assume free-flow or separate PLC)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest durability | No lost paid-path events after ACK | WAL + replicated log; RPO≈0 for acked |
| N2 | Charge latency | Not real-time barrier | Price within minutes; invoice T+1 OK |
| N3 | Dedup correctness | Prefer no double-charge | Idempotent charge keys; human review edge |
| N4 | Availability | Billing continues if one region down | Active-passive or multi-AZ; gantries buffer |
| N5 | Clock | Bounded skew | Reject / quarantine beyond skew policy |
| N6 | Privacy | Plates protected | Encrypt at rest; tokenize display; audit |
| N7 | Audit | Money & evidence immutable-ish | Append-only ledger + object evidence |
| N8 | Recon | Match PSP | Daily break <$ε or investigated |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. RFID tag read at gantry → account match → point charge → prepaid debit → receipt.  
2. Entry + exit OCR (high confidence) → trip stitch → distance/segment price → card charge.  
3. Unregistered plate → guest account → invoice mail/SMS → pay link.  
4. Offline gantry reconnects → uploads buffered events → late trip open/adjust.  
5. Customer disputes wrong plate → evidence review → credit + mark plate link suspect.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two cameras same gantry, 200ms apart | Dedup → one ObservationCluster |
| Same plate, adjacent gantries 2s apart | Likely real traversal; not dedup across points |
| OCR confidence 0.55 | Quarantine / manual or secondary model; don't auto-charge high $ |
| RFID + conflicting OCR | Prefer RFID for account; keep OCR as evidence |
| Exit without entry | Open-ended trip policy: max fare or flat miss-entry fee |
| Entry without exit (lost exit) | Timeout close with policy fare; adjust if late exit arrives |
| Late exit after trip closed | Adjustment charge/credit; never silent double full trip |
| Clock skew +2h on gantry | Quarantine stream; alert; don't price into wrong TOD bucket blindly |
| Duplicate PSP webhook | Idempotent payment intent / charge_key |
| Partial refund dispute | Ledger credit note linked to original charge |
| Plate shared / cloned | Fraud signals; hold charging; investigation |
| Device sequence gap | Hole detection; request retransmit; don't assume loss forever |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Gantries | 500 | 5K | 50K | 500K |
| Peak observations/s | 5K | 50K | 500K | 5M |
| Avg observations/day | 50M | 500M | 5B | 50B |
| Distinct plates/day | 5M | 50M | 500M | multi-B class |
| Charges created/day | 20M | 200M | 2B | 20B |
| Dispute rate | 0.1–0.5% | similar | similar | need automation |
| Image evidence retained | 30–90d | cost pressure | aggressive tiering | face/plate policy strict |
| PSP settlement files/day | tens | hundreds | thousands | batched global |
| Agencies / tenants | 5 | 50 | 500 | 5K |

**What each jump forces:**

- **10×:** Partitioned event log by gantry/region; sharded charge DB; async pricing workers.  
- **100×:** Regional ingest cells; plate tokenization service; image cold tier; recon warehouse.  
- **1,000×:** Continent cells; streaming dedup approximations; agency settlement mesh; privacy-preserving analytics.

### 1.5 Etc. (Constraints & Assumptions)

- Free-flow or barrier-adjacent; charging is **eventually correct**, not sub-100ms gate decision (gate controller may be separate with local allow-list).  
- Images stored in object store; billing DB holds pointers + hashes.  
- Plates are **PII**; treat like account identifiers with retention.  
- Money uses **ledger** (append-only entries), not update-in-place balances alone.  
- Prefer **at-least-once** ingest + **exactly-once charge effect** via idempotency keys.

**Scope statement to repeat back:**

> Design a toll-road vehicle billing platform: durable multi-source gantry event ingest with offline store-and-forward, observation dedup, vehicle identity (RFID/plate), trip stitching, versioned pricing, idempotent charges, disputes with evidence, and PSP/bank reconciliation—correct under duplicates, late events, and clock skew—scaled through regional cells at 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Raw observations** | Sensor events | ~5K/s | ~50K/s | Ingest + log |
| **Image uploads** | JPEG/HEIF evidence | ~1–2K/s objects | ×10 | Object store |
| **Dedup / cluster** | Stateful window | ~5K/s | ~50K/s | Stream jobs |
| **Trip updates** | Stitch FSM | ~2–3K/s | ×10 | Trip service |
| **Charge creates** | Ledger + outbox | ~1–2K/s peak | ×10 | Billing DB |
| **PSP calls** | Auth/capture | hundreds/s | ×10 | PSP + queue |
| **Recon batch** | Daily files | batch | larger batch | Warehouse |
| **Dispute reads** | Agent UI | low QPS | ×10 | OLTP + evidence |

**Anti-pattern:** one “event QPS” mixing 200-byte RFID reads and 200 KB images.

### 2.2 Observation → charge funnel

```text
Baseline: 50M observations/day
After dedup (~1.3–2× sensor redundancy): ~30–40M unique passages
After trip fold (entry/exit pairs): ~20M billable charges/day
Peak ≈ 5× average for rush hour → design peak not daily average
5K obs/s peak × 86400 ≈ 432M/day capacity headroom if sustained
  (real peak is hours; size for peak obs/s)
```

### 2.3 Storage

```text
Observation record ~500 B (no image) → 50M × 500 B ≈ 25 GB/day raw
+ indexes/replicas → ~75–100 GB/day hot
Images: 30% of obs keep image × 150 KB ≈ 0.3 × 50M × 150 KB ≈ 2.25 PB/day? WAIT
  Recalc: 0.3 × 50e6 × 150e3 bytes = 0.3 × 50e6 × 1.5e5 = 0.3 × 7.5e12 = 2.25e12 ≈ 2.25 TB/day
Retain 60 days images → ~135 TB (plus redundancy ~400 TB class)
Charges: 20M × 400 B ≈ 8 GB/day; years of ledger → multi-TB with indexes
```

### 2.4 Dedup window memory

```text
Window W = 5s per gantry point, keep plate/RFID fingerprints
500 gantries × ~20 vehicles in 5s × 200 B ≈ 2 MB — trivial
At 50K gantries × dense urban: still GBs — shard by gantry_id
```

### 2.5 Pricing & PSP cost sketch

```text
PSP fee ~2% + $0.10; avg toll $4 → fee matter but product constraint
Idempotent capture critical: duplicate capture = direct $ loss / support cost
Recon breaks: 0.01% of 20M × $4 = $8K/day at risk → ops investment justified
```

### 2.6 Late event lag

```text
Offline buffer 24h × 100 events/s/gantry worst → 8.64M events/gantry — unrealistic
Realistic: 10 events/s × 3600 × 8h outage = 288K events buffered per busy gantry
Disk on gantry: 288K × 1 KB ≈ 288 MB (+ images separate policy)
Ingest catch-up: 288K in 10 min → ~480/s/gantry; fleet catch-up storms need admission
```

---

## 3. High-Level Design

### 3.1 APIs

| API | Semantics |
|-----|-----------|
| `POST /v1/gantries/{id}/events` | Batch observations; device_seq range; idempotent by (gantry_id, device_seq) |
| `POST /v1/gantries/{id}/images` | Upload evidence blob; returns `image_id` |
| `GET /v1/accounts/{id}/charges` | List charges for account |
| `POST /v1/charges/{id}/dispute` | Open dispute with reason codes |
| `POST /v1/payments/webhook` | PSP callbacks; idempotent by psp_event_id |
| `GET /v1/admin/recon/breaks` | Reconciliation exceptions |
| `POST /v1/admin/price-books` | Publish versioned price book |

**Internal events (log):** `ObservationAccepted`, `ObservationClustered`, `TripOpened`, `TripClosed`, `ChargeCreated`, `PaymentCaptured`, `ChargeAdjusted`, `DisputeResolved`.

### 3.2 Domain model

```text
Gantry(gantry_id, road_id, km_marker, agency_id, timezone)
Device(device_id, gantry_id, type: RFID|CAMERA|AVC, skew_bound)
Observation(obs_id, gantry_id, device_id, device_seq, event_time, ingest_time,
            rfid?, plate_raw?, plate_token?, ocr_confidence?, vehicle_class?,
            image_id?, raw_hash)
ObservationCluster(cluster_id, gantry_id, event_time_span, member_obs[],
                    chosen_identity, confidence)
VehicleIdentity(type: RFID|PLATE, value_token, account_id?)
Trip(trip_id, agency_id, identity, entry_cluster?, exit_cluster?, state, fare_policy)
Charge(charge_id, charge_key UNIQUE, trip_id?, cluster_id?, amount, currency,
       price_book_version, state, account_id|invoice_id)
LedgerEntry(entry_id, account_id, charge_id, amount, type: DEBIT|CREDIT|CAPTURE|REFUND)
Dispute(dispute_id, charge_id, state, evidence_refs[])
PaymentIntent(intent_id, charge_id, psp_ref, state)
ReconBreak(break_id, source, amount_delta, payload_ref)
```

**Idempotent charge key (critical):**

```text
charge_key = hash(
  agency_id,
  identity_token,          # RFID or plate_token
  billable_point_or_trip,  # gantry_id+slot OR entry+exit ids
  event_time_bucket,       # coarse bucket to absorb skew within policy
  price_book_version
)
```

Re-processing the same passage **must** hit the same `charge_key` → upsert no-op.

### 3.3 Ingest & durability options

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| Sync write OLTP | Simple | Gantries blocked; spike death | Avoid |
| **Append log + ACK** | Durable, decouple | At-least-once | **MVP** |
| Direct to warehouse | Cheap analytics | Bad for charging latency/correctness | No |

**Chosen:** gantry → TLS ingest gateway → **WAL/Kafka** partitioned by `gantry_id` → ACK only after quorum persist. Images → object store first (or parallel), event carries `image_id`.

### 3.4 Dedup strategies

| Strategy | Pros | Cons |
|----------|------|------|
| Exact (gantry, device_seq) | Perfect device retries | Misses multi-camera dupes |
| Time+plate window | Catches camera pairs | False merge if two similar plates |
| RFID UID window | Strong for tags | Tags only |
| **Hybrid cluster** | Best practical | Stateful stream job |

**Chosen MVP:**  
1) Exactly-once accept per `(gantry_id, device_id, device_seq)`.  
2) Cluster observations at same gantry within **Δt** (e.g. 1–3s) with same RFID or plate_token within OCR distance (normalized).  
3) Never cluster across different gantry_ids (those are trip legs).

### 3.5 Identity & OCR confidence

| Signal | Trust | Action |
|--------|-------|--------|
| RFID valid crypto/MAC | High | Bind account |
| OCR ≥ 0.92 | High | Auto identity |
| OCR 0.75–0.92 | Medium | Auto if RFID absent & $ below threshold; else review |
| OCR < 0.75 | Low | Quarantine; secondary OCR; manual |
| RFID vs OCR disagree | Conflict | Prefer RFID account; flag fraud/evidence |

Plate normalization: uppercase, strip separators, jurisdiction rules; store **raw + normalized + token**.

### 3.6 Trip stitching

| Road type | Model |
|-----------|-------|
| Open gantry / barrier point | Cluster → Charge (point) |
| Closed ticket (entry/exit) | Open Trip on entry; close on exit; price segment |
| Missing exit | Timer (e.g. 24h) → close with miss-exit fare |
| Late exit after close | `ChargeAdjusted` credit/debit delta |

**FSM:** `OPEN` → `CLOSED` → `ADJUSTED*` (append-only adjustments, don't rewrite history).

### 3.7 Pricing

Versioned **price books**: `(road_segment, vehicle_class, tod_bucket, agency) → amount`.  
Congestion multipliers as published versions, not silent mutation.  
Always persist `price_book_version` on Charge for disputes.

### 3.8 Payments & reconciliation

```text
ChargeCreated (AUTHORIZED/PENDING)
  → PaymentIntent (idempotent by charge_id)
  → PSP auth/capture
  → Ledger CAPTURE
  → daily PSP settlement file vs Ledger
  → ReconBreak for mismatches
```

**Deal-breaker:** charging PSP with non-idempotent keys → double capture under retries.

### 3.9 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Ingest | Log + ACK | Decouple spikes; replay | Sync OLTP from gantry |
| Money | Ledger + charge_key | Auditable; idempotent | Update balance only |
| Dedup | Hybrid cluster | Multi-camera reality | Blind unique on plate alone |
| Late events | Adjustments | Truth arrives late | Immutable wrong final fare |
| Images | Object store + hash | Cheap; evidence | BLOBs in Postgres |
| Plates | Tokenize + encrypt | Privacy | Cleartext plates in logs |
| Offline | Store-and-forward + seq | Reality of roadside | Require online or drop |
| Clock | event_time + skew policy | TOD pricing fairness | Trust device clock blindly |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
  Roadside Gantries (RFID / Camera / AVC)
       |  store-and-forward + device_seq
       v
  +------------------+     +------------------+
  | Ingest Gateway   |---->| Object Store     |  images
  | auth, batch, ACK |     | (evidence)       |
  +--------+---------+     +------------------+
           |
           v
  +------------------+
  | Event Log       |  partition by gantry_id / region
  | (Kafka/Pulsar)   |
  +--------+---------+
           |
     +-----+------+----------------+----------------+
     v            v                v                v
 +--------+  +----------+   +------------+   +-------------+
 | Dedup/ |  | Identity |   | Trip       |   | Quarantine  |
 | Cluster|  | Resolver |   | Stitcher   |   | (low OCR)   |
 +---+----+  +----+-----+   +-----+------+   +------+------+
     |            |               |                 |
     +------+-----+-------+-------+                 |
            v             v                         v
       +--------------------+                 Manual review
       | Pricing + Charging |
       | charge_key upsert  |
       +---------+----------+
                 |
       +---------+----------+---------+
       v                    v         v
 +-----------+      +-----------+  +-------------+
 | Ledger DB |      | PSP Adapt |  | Invoice/    |
 | accounts  |      | + webhooks|  | Collections |
 +-----------+      +-----+-----+  +-------------+
                          |
                          v
                   +--------------+
                   | Recon Worker |<-- bank/PSP files
                   +--------------+
```

### 4.2 Critical path: RFID point toll

```text
Gantry → Ingest(ACK) → Log → Dedup(cluster) → Identity(RFID→acct)
  → Pricing(point) → Charge upsert(charge_key) → Ledger debit
  → (optional) receipt push
```

### 4.3 Critical path: entry/exit + late exit

```text
Entry cluster → Trip OPEN
Exit cluster → Trip CLOSED → Charge C1
... hours later late better exit / correction → ChargeAdjusted Δ linked to C1
Ledger: CREDIT/DEBIT note; PSP refund/capture delta idempotent by adjust_key
```

### 4.4 Offline catch-up storm

```text
Gantry back online → burst batches
Ingest gateway: per-gantry rate limit + global catch-up budget
Log absorbs; pricing lag increases but ACK durable
Priority lane: recent event_time first optional
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Acked observation is durable** (quorum log) and replayable.  
2. **`(gantry_id, device_id, device_seq)` unique** — device retries are no-ops.  
3. **At most one successful money effect per `charge_key`** (DB unique + upsert).  
4. **Ledger is append-only**; corrections are new entries.  
5. **Trip fare changes after close use adjustments**, not silent overwrite.  
6. **PSP side effects idempotent** (`Idempotency-Key = charge_id/adjust_id`).  
7. **Evidence images content-addressed**; charge stores hash.  
8. **Plate cleartext minimized**; tokens for joins.  
9. **Skew beyond bound → quarantine**, not quiet wrong TOD price.  
10. **Recon breaks never auto-delete money** without investigation workflow.

#### 5.1.2 Duplicate observations

```text
Layer A: transport idempotency (device_seq)
Layer B: cluster window (same gantry, Δt, same identity)
Layer C: charge_key uniqueness (money)
```

All three needed: A stops retries; B stops multi-sensor double passages; C stops double bills if stitcher bugs.

#### 5.1.3 Clock skew & event time

| Clock | Use |
|-------|-----|
| `event_time` | Pricing TOD, trip order (from device) |
| `ingest_time` | Ops lag SLIs, quarantine |
| `processing_time` | Watermarks in stream jobs |

**Watermark:** trip closer waits `max_lateness` (e.g. 2–24h by road) before miss-exit fare. Late data → adjustment path.

**NTP:** gantries report `last_sync_ok`; if unsynced, mark events `clock_suspect`.

#### 5.1.4 Offline store-and-forward

- Local disk queue encrypted; retain until ACK with log offset.  
- Monotonic `device_seq`; gateway detects gaps → `NACK gap` / retransmit API.  
- Images may be deferred (charge with lower confidence without image? policy: for high $ require image async attach).  
- **Catch-up admission control** so 5K gantries reconnecting don't melt ingest.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Double charge on retry | charge_key + PSP idempotency |
| 10× | Dedup state loss | Log replay; Rocks/state store checkpoint |
| 100× | Regional outage | Cell failover; gantries buffer |
| 1,000× | Recon volume | Automated break classification; sampling audit |

#### 5.1.6 Exactly-once illusions

Pipeline is **at-least-once**. Effects are **idempotent**. Saying “Kafka exactly-once” without charge_key uniqueness is an interview fail for money.

### 5.2 Scalability

#### 5.2.1 Partitioning

| Entity | Partition key |
|--------|---------------|
| Event log | `gantry_id` (locality of dedup) |
| Trips | `identity_token` or `account_id` |
| Charges / ledger | `account_id` (or invoice_id) |
| Images | hash / agency prefix |
| Recon | settlement_date + psp_merchant |

**Careful:** trip stitch needs entry+exit — both map to same identity partition, not gantry partition. So: dedup by gantry; **emit identity-keyed events** to trip topic.

#### 5.2.2 Stream topology

```text
topic.obs.raw        key=gantry_id
  → Cluster service (state by gantry)
topic.obs.clustered  key=identity_token
  → Trip service (state by identity+road)
topic.trip.closed    key=account_id
  → Pricing/Charging
topic.charge.outbox  → PSP workers
```

#### 5.2.3 Hot gantries / hot plates

- Hot gantry: more partitions? Better: key by `gantry_id` already isolates; scale consumer parallelism.  
- Hot plate (fleet): account-level rate; batch charges.  
- Celebrity bug: malformed plate empty string → poison key → dead-letter + guard rails.

#### 5.2.4 Progressive scale

| Jump | Change |
|------|--------|
| →10× | Kafka tiers; sharded Postgres (accounts); Redis not for money SoT |
| →100× | Regional ingest + log; charge cells by account hash; image lifecycle |
| →1,000× | Agency cells; cross-agency settlement bus; privacy analytics vault |

#### 5.2.5 Indexing & queries

| Query | Index |
|-------|-------|
| Account charge history | `(account_id, created_at DESC)` |
| Plate invoice lookup | `plate_token` + time |
| Dispute by charge | `charge_id` |
| Gantry gap detect | `(gantry_id, device_id, device_seq)` unique |
| Recon breaks | `(settlement_date, status)` |

Avoid scanning images via DB — metadata only.

#### 5.2.6 Privacy at scale

- `plate_token = HMAC(plate_normalized, agency_key)` for joins.  
- Display plate only in authorized UI with audit.  
- Retention: raw images 30–90d; charge metadata years (tax).  
- Analytics: aggregate counts; no cleartext plate export by default.

### 5.3 Maintainability

#### 5.3.1 Price book & policy as code

Publish immutable `price_book_version`; canary on one road; rollback = new version, don't mutate old.

#### 5.3.2 Observability

```text
ingest_ack_rate, device_seq_gap, dedup_ratio, ocr_confidence_histogram,
trip_open_age, late_adjustment_rate, charge_upsert_conflict,
psp_capture_success, recon_break_amount, quarantine_depth,
catchup_lag{gantry}, clock_suspect_rate
```

No high-cardinality plate labels in Prometheus.

#### 5.3.3 Testing

- Property: retry ingest N times → one observation row.  
- Property: dual camera → one cluster → one charge.  
- Late exit after close → net fare equals “as if known”.  
- Clock skew fixtures.  
- PSP webhook replay.  
- Recon synthetic breaks.

#### 5.3.4 Operability

- Quarantine console for low OCR.  
- Gantry drain/replay tools.  
- Dual-control for manual credits above threshold.  
- Chaos: kill pricing consumers — lag OK; double charge not OK.

#### 5.3.5 Safe evolution

Phase 1: point tolls + RFID + OCR guest invoices.  
Phase 2: closed-road trips + adjustments.  
Phase 3: multi-agency settlement.  
Phase 4: advanced fraud / cloned plate network analysis.

---

## 6. Wrap-Up

### 6.1 What we designed

A **toll-road vehicle billing** system: durable gantry ingest with store-and-forward, multi-layer dedup, RFID/OCR identity with confidence gates, trip stitching with late adjustments, versioned pricing, **idempotent charges + ledger**, disputes with evidence, and PSP/bank reconciliation—scaled by splitting gantry-keyed ingest from identity-keyed trips and account-keyed money.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Exactly-once | Effect idempotency > bus fairy dust |
| Dedup | device_seq + cluster + charge_key |
| Late events | Watermarks + adjustments |
| OCR | Confidence thresholds; quarantine |
| Images | Object store; hashes in OLTP |
| Plates | PII tokenize; retention |
| Offline | Buffer + catch-up admission |
| Recon | Daily breaks workflow mandatory |

### 6.3 Closing line

> “Toll billing is a money system fed by dirty sensors—you win with idempotent charge keys, layered dedup, and honest late-event adjustments, not by pretending OCR and clocks are perfect.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Ingest & buffering

**Q1: Why not write observations straight to Postgres?**  
A: Gantry bursts and catch-up storms need a durable buffer; OLTP becomes the bottleneck and coupling point. Log absorbs spikes; consumers scale independently.

**Q2: How large should ingest batches be?**  
A: Balance overhead vs latency—e.g. 50–200 events or 50–100ms flush. Images separate from thin events.

**Q3: What does ACK mean to the gantry?**  
A: Quorum persist in the log (and schema validation). Not “charged the customer.”

**Q4: How do you detect missing device_seq?**  
A: Per-device contiguous counter; gap tracker; retransmit API; alert on persistent holes.

**Q5: Backpressure when log is slow?**  
A: Gateway returns 503/429; gantries spool locally; never drop without policy + metric.

### 7.2 Dedup & windows

**Q6: Why not UNIQUE(plate, gantry, minute)?**  
A: Too coarse (collisions) or too fine (dupes remain). Use cluster Δt + identity similarity + money charge_key.

**Q7: Memory for dedup state?**  
A: Key by gantry; ring buffer of recent fingerprints; RocksDB/state store for restart; TTL ≫ window.

**Q8: Two cars same plate clone?**  
A: Dedup won't save you; fraud signals (teleportation speed), holds, investigation.

**Q9: RFID multipath double reads?**  
A: Same as camera pair—cluster by UID within Δt at gantry.

**Q10: Bloom filter for dedup?**  
A: Optional probabilistic acceleration for huge windows; money path still needs exact charge_key. Blooms false-positive → investigate, don't skip durable identity store.

### 7.3 Trip stitching & algorithms

**Q11: How do you order entry/exit with skew?**  
A: Prefer gantry topology + event_time; reject impossible sequences (exit before entry beyond skew); quarantine.

**Q12: Graph model?**  
A: Road network DAG/segments; trip is path consistent with time and max speed.

**Q13: Max speed sanity?**  
A: Distance(entry,exit)/Δt ≤ vmax + margin; else fraud/clock/OCR error.

**Q14: Multiple entries no exit?**  
A: Close oldest by timeout; or merge per policy; never unbounded OPEN trips.

**Q15: Algorithmic complexity of stitcher?**  
A: Per identity event O(1)/amortized FSM; avoid O(n²) global plate scans.

### 7.4 Pricing

**Q16: Why version price books?**  
A: Disputes months later need explainability; rollback safety.

**Q17: TOD boundary with skew?**  
A: Policy: favor customer or agency; document; use ingest watermark carefully—prefer event_time with suspect flag.

**Q18: Vehicle class from AVC wrong?**  
A: Charge with class confidence; dispute adjusts; axle sensors calibrate.

### 7.5 Money, ledger, PSP

**Q19: Why charge_key?**  
A: Retries, reprocessing, dual pipelines must not double-bill.

**Q20: Auth then capture vs auto-capture?**  
A: Auth if delay between observe and finalize; capture when trip closed. Idempotent both.

**Q21: Partial capture / refunds?**  
A: Adjustments as new ledger entries referencing original charge.

**Q22: Prepaid balance race?**  
A: Conditional debit in TX (`WHERE balance >= amount`) or ledger reservation; serialize per account.

**Q23: What if PSP succeeds and DB fails after?**  
A: Outbox/inbox pattern; recon recovers; never “fire PSP then forget.”

**Q24: Double-entry ledger?**  
A: Strong interview answer: dr/cr accounts (customer, clearing, revenue, tax).

### 7.6 Reconciliation

**Q25: What is a recon break?**  
A: Mismatch between ledger and PSP settlement (amount, missing, duplicate).

**Q26: How to match records?**  
A: Join on psp_ref / idempotency key; fuzzy amount+time only for exceptions.

**Q27: Scale of files?**  
A: Batch warehouse job; partition by merchant/day; don't OLTP-scan.

**Q28: Who wins — PSP or ledger?**  
A: Investigation; money movement reality often PSP; fix ledger with audited adjustment.

### 7.7 Privacy & security

**Q29: Are plates PII?**  
A: Yes—tokenize, encrypt, access audit, retention.

**Q30: Hash plates with unsalted SHA?**  
A: Rainbow risk; use HMAC with keyed secret per agency; key rotation plan.

**Q31: Images in analytics lake?**  
A: Separate vault; purpose limitation; face/plate blurring for non-enforcement analytics.

**Q32: Insider dispute abuse?**  
A: Dual control; reason codes; anomaly on credit volume.

### 7.8 Storage & DB

**Q33: Postgres vs Cassandra for observations?**  
A: Log is primary for raw; Postgres for accounts/charges; cold observations to object/columnar.

**Q34: Partition charges how?**  
A: Time + account hash; keep unique on charge_key global via hash shard mapping.

**Q35: Where do images live?**  
A: Object store; lifecycle to cold; legal hold flag.

**Q36: Index OCR text?**  
A: Don't full-text all plates; lookup by token; optional ES for investigation tools with ACL.

### 7.9 Load balancing & hashing

**Q37: Load balance ingest?**  
A: Sticky optional by gantry for connection reuse; correctness doesn't need sticky if seq in payload.

**Q38: Consistent hash accounts?**  
A: Yes for billing cells; migration with dual-write/lookup.

**Q39: Hot partition gantry?**  
A: Split gantry into logical subkeys only if single partition CPU-bound—rare vs identity hot keys.

### 7.10 Multi-region & DR

**Q40: Active-active charging?**  
A: Hard for money—prefer active-passive per agency/cell or CRDT-free single writer for accounts.

**Q41: RPO/RTO?**  
A: Acked events RPO≈0 in AZ; regional DR RPO seconds–minutes via async log mirror; state carefully.

**Q42: Gantry during region fail?**  
A: Local spool; alternate ingest endpoint DNS failover.

### 7.11 Disputes & product

**Q43: Evidence pack contents?**  
A: Cluster members, image hashes, price book version, device clock flags, trip FSM history.

**Q44: SLA for dispute?**  
A: Product—e.g. 5–10 business days; automation for clear OCR mismatches.

**Q45: Guest invoice deliverability?**  
A: DMV address partner; SMS if registered elsewhere; collections Phase 2.

### 7.12 10× / 100× / 1,000×

**Q46: What breaks first at 10×?**  
A: Single Postgres charges; image $.

**Q47: At 100×?**  
A: Cross-region lag vs late fees; recon ops load; privacy regulation variance.

**Q48: At 1,000×?**  
A: Need cell architecture, automated quarantine ML, settlement mesh—not a bigger monolith.

### 7.13 Algorithms misc

**Q49: Plate OCR string distance?**  
A: Normalized Levenshtein / highway-confusable sets (0/O, 1/I) inside cluster only.

**Q50: Streaming watermark library?**  
A: Flink/Spark/Beam concepts—event time + allowed lateness; know the terms in interview.

### 7.14 Deal-breakers checklist

**Q51: Name three deal-breakers.**  
A: (1) Non-idempotent PSP capture, (2) dropping offline gantry data, (3) mutable fare history without ledger adjustments / cleartext plate dumps in logs.

---

## Appendix A: Sample charge_key pseudocode

```text
normalize_plate(p) → upper, strip, jurisdiction rules
identity = rfid_uid OR hmac(plate_norm, key)
if point_toll:
  billable = ("P", gantry_id, cluster_id)
else:
  billable = ("T", entry_cluster_id, exit_cluster_id)
charge_key = sha256(agency | identity | billable | price_book_version)
```

## Appendix B: Observation accept SQL sketch

```sql
INSERT INTO device_seq_watermark(gantry_id, device_id, last_seq)
VALUES ($1,$2,$3)
ON CONFLICT (gantry_id, device_id)
DO UPDATE SET last_seq = EXCLUDED.last_seq
WHERE device_seq_watermark.last_seq + 1 = EXCLUDED.last_seq;
-- gaps handled out of band; duplicates: INSERT obs ON CONFLICT DO NOTHING
```

## Appendix C: Interview 45-minute plan

1. Scope + RFID/OCR/trip/recon (6 min)  
2. Numbers + split classes (5 min)  
3. Ingest, dedup layers, charge_key (10 min)  
4. Trip FSM + late adjust (7 min)  
5. PSP + recon + privacy (7 min)  
6. Scale cells + catch-up (5 min)  
7. Q&A  

---

*End of toll-road vehicle billing system design.*
