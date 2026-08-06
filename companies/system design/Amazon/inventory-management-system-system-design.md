# System Design: Inventory Management System

> **Focus areas:** Multi-warehouse stock · Reservations · Oversell prevention · WMS sync · Audit ledger · Availability promise · Hot SKU · Reconciliation  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes (promise vs reserve vs sync vs audit), explicit stock invariants, resolved ownership of on_hand vs reserved vs WMS

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

Goal: **bound sellable inventory**—know how many units exist across warehouses (FCs), reserve them safely at checkout, prevent oversell, sync with warehouse systems of record, and produce an auditable trail when counts disagree.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is tracked? | SKU/ASIN × warehouse quantities | Position key `(sku, warehouse_id)` |
| F2 | Quantity types? | `on_hand`, `reserved`, `available`, maybe `in_transit`, `damaged` | Explicit buckets; available derived |
| F3 | Who adjusts stock? | WMS receipts/shipments/cycle counts; checkout reserve/release; returns | Inbound event adapters + APIs |
| F4 | Reservation? | Soft hold at checkout; commit on order place; release on cancel/TTL | Reservation entity + TTL sweeper |
| F5 | Oversell? | Must not sell more than available (policy: deny) | Atomic conditional updates |
| F6 | Multi-warehouse? | Allocate across FCs; customer promise by zip/SLA | Allocator + promise API |
| F7 | Availability read? | PDP “In stock”, search coarse flag, checkout hard reserve | Split read paths by freshness need |
| F8 | Sync with WMS? | WMS often physical SoT for on_hand; commerce owns reserved | Sync protocol + conflict rules |
| F9 | Audit? | Every mutation explainable (who/what/why) | Append-only inventory ledger |
| F10 | Safety stock? | Hold buffer unsellable | `non_sellable` or raise reserve floor |
| F11 | Flash sales? | Extreme contention on hot SKUs | Isolation / token buckets |
| F12 | Transfers? | FC→FC in transit | In-transit bucket; promise rules |
| F13 | Idempotency? | Checkout retries, WMS duplicate scans | Idempotency keys everywhere |
| F14 | Marketplace FBA? | Phase 2 seller_id dimension | Schema extension hook |
| F15 | Negative stock? | Never for available; investigate if WMS says so | Break-glass adjust + alarm |

**MVP functional scope (lock with interviewer):**

1. Stock positions per SKU×FC: on_hand, reserved, available.  
2. **Promise** API (advisory availability + ETA hints).  
3. **Reserve / release / commit** APIs with idempotency + TTL.  
4. Multi-FC allocation for multi-line orders (saga-friendly).  
5. WMS event ingest: receive, ship, adjust, cycle count.  
6. **Inventory ledger** (audit) for all mutations.  
7. Reconciliation jobs: ledger vs position; commerce vs WMS snapshot.  
8. Ops tools: freeze SKU/FC, safety stock, kill switch.

**Out of MVP (explicitly defer):**

- Bin/slot-level WMS internals (aisle robotics)  
- Perfect multi-region active-active writes on same SKU  
- Full network optimization / inbound purchasing planning  
- Seller-owned multi-channel inventory sync (Phase 2)  
- Lot/serial tracking deep dive (mention hooks)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Reserve latency | Checkout critical | p50 < 20ms, p99 < 100ms in-region |
| N2 | Promise latency | PDP/search | p50 < 10ms cached; stale bound |
| N3 | Correctness | Oversell ≈ 0 | Atomic reserve; measure |
| N4 | Durability | Confirmed reserve durable | ACK after quorum/commit |
| N5 | Availability | Degrade promise before corrupting stock | Fail closed on reserve if unsure |
| N6 | Throughput | See scale | Shard by SKU (or SKU×FC) |
| N7 | Auditability | Support/finance | Ledger immutable-ish |
| N8 | Sync lag | WMS events seconds–minutes | Bound lag alarms |
| N9 | Operability | Own pager | Oversell, stuck reserves, recon diffs |
| N10 | Efficiency | Cache digests; don’t chatty WMS | Batch; CQRS read models |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Receive 100 at FC_A → on_hand+=100 → promise shows in stock → checkout reserves 2 → available 98 → ship → on_hand/reserved decrement.  
2. Multi-line order allocates SKU1@FC_A, SKU2@FC_B → two reservations.  
3. Cancel → release reserved.  
4. Cycle count adjusts on_hand with audit reason.  
5. Return restock → on_hand+=n after QC.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two buyers, one unit | One reserve wins; other `INSUFFICIENT_STOCK` |
| Double PlaceOrder | Same idempotency → one reservation set |
| Reserve then payment fail | TTL or explicit release |
| WMS ship without reserve | Create backfill / alarm; don’t silent negative |
| Cycle count < reserved | Escalation: freeze selling; cancel/reallocate excess |
| Duplicate WMS event | Idempotent by event_id |
| FC offline | Exclude from promise/alloc; existing reserves held |
| Hot SKU thundering herd | Isolate key; admission tokens |
| Clock skew TTL | Absolute `expires_at` in DB |
| Partial multi-FC reserve fail | Compensate prior reserves |
| In-transit only stock | Policy: don’t sell or sell with longer ETA |
| Replay old adjust | Version/vector checks; reject stale |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| SKUs | 10M | 50M | 200M | 500M+ |
| Warehouses (FCs) | 20 | 50 | 200 | 500+ |
| Position rows | 50M | 400M | 2B | 10B+ |
| Promise QPS (peak) | 100K | 1M | 10M | 100M |
| Reserve ops/s (peak) | 2K | 20K | 200K | 2M |
| Release/commit ops/s | 2K | 20K | 200K | 2M |
| WMS events/s | 5K | 50K | 500K | 5M |
| Ledger writes/s | 10K | 100K | 1M | 10M |
| Open reservations | 5M | 50M | 500M | 5B |
| Recon diffs / day | thousands | tens of k | more | automated |

**What each jump forces:**

- **10×:** Shard positions; Redis promise cache; Kafka WMS ingest; ledger stream.  
- **100×:** Hot-SKU service; regional cells; hierarchical promise; automatic recon.  
- **1,000×:** Cell blast radius; approximate global promise; per-FC ownership; chaos-tested sagas.

### 1.5 Etc. (Constraints & Assumptions)

- **Available = on_hand − reserved − non_sellable** (define clearly).  
- Physical truth tends to live in **WMS**; commerce system is **sellable truth** with reservations.  
- Integer quantities only.  
- Start single region writes per position; multi-region read replicas OK.

**Scope statement:**

> Design an inventory management system that maintains multi-warehouse stock, provides availability promises, atomically reserves to prevent oversell, syncs with WMS, and audits every mutation—from baseline commerce scale through 10× / 100× / 1,000× with sharded positions and hot-SKU isolation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Promise reads** | PDP/search digests | 100K/s | Cache / CQRS |
| **Reserve/release** | Checkout | 2K/s | Position OLTP shards |
| **WMS sync writes** | Receive/ship/adjust | 5K/s | Ingest + apply |
| **Ledger append** | Audit | ~2–5× mutations | Append store |
| **Recon / sweepers** | TTL, diffs | bursty | Batch jobs |

**Deal-breaker:** sizing reserve DB from homepage QPS.

### 2.2 Storage

```text
Position row ~100 B → 50M × 100 B ≈ 5 GB (+ indexes)
Reservation ~200 B × 5M open ≈ 1 GB hot
Ledger: 10K writes/s × 150 B ≈ 1.5 MB/s → ~130 GB/day
Retain ledger hot 90d; cold forever in object store
```

### 2.3 Hot key math

```text
Flash sale: 50K interested /s on 1 SKU × 1 FC
Single row CAS → bottleneck
Need: token pre-split, queue, or local shard of inventory pools
```

### 2.4 Reservation outstanding

```text
reserve_rate × hold_time = open_reservations
2K/s × 15 min × 60 = 2K × 900 = 1.8M open at baseline peak math
At 100×: ~180M → store + sweeper capacity matter
```

### 2.5 Bottleneck ranking

(1) Oversell races (2) hot SKU (3) WMS conflict when reserved > on_hand (4) ledger volume (5) cache stampede on promise.

---

## 3. High-Level Design

### 3.1 UX / consumer surfaces

```text
PDP / Search          Checkout             Ops / FC
promise() cached  →   reserve() strong  →  WMS events
“In stock”            deny if insufficient  cycle count UI
```

### 3.2 Domain model

```text
InventoryPosition
 ├── sku, warehouse_id
 ├── on_hand, reserved, non_sellable
 ├── available := on_hand - reserved - non_sellable
 ├── version / etag
 └── updated_at

Reservation
 ├── reservation_id
 ├── order_id / checkout_session_id
 ├── sku, warehouse_id, qty
 ├── status: OPEN|COMMITTED|RELEASED|EXPIRED
 ├── expires_at
 ├── idempotency_key
 └── version

InventoryLedgerEntry
 ├── entry_id, sku, warehouse_id
 ├── delta_on_hand, delta_reserved, delta_non_sellable
 ├── reason_code, actor, ref_type, ref_id
 ├── event_id (idempotency)
 └── ts

Warehouse
 ├── warehouse_id, region, status ONLINE|DEGRADED|OFFLINE
 └── capabilities

AllocationPlan
 ├── order_id, lines[] → [{sku, warehouse_id, qty}]
 └── strategy metadata
```

**Ownership (resolved):**

| Concern | Source of truth |
|---------|-----------------|
| Sellable reserved qty | **Inventory service** (commerce) |
| Physical on_hand (long-term) | **WMS** (+ commerce mirror) |
| Open reservations | Inventory Reservation store |
| Audit trail | Inventory Ledger |
| Customer promise digest | Derived cache (not SoT) |
| Order state | Order service (not inventory) |

**Deal-breakers:**

- Read-modify-write without atomic condition.  
- Trusting cache for reserve.  
- Dual-increment reserved in app + WMS without protocol.  
- Silent negative available.  
- No idempotency on WMS ship events.

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| Promise API | Cached availability / ETA hints |
| Reservation API | Reserve/release/commit/extend |
| Allocator | Choose FCs for order lines |
| Position Store | Sharded OLTP for quantities |
| Ledger Service | Append + query audit |
| WMS Ingest | Validate, dedupe, apply events |
| Reconciler | Diff positions vs ledger vs WMS snapshots |
| Sweeper | Expire OPEN reservations |
| HotSKU Gateway | Optional isolation lane |
| Admin / Freeze | Ops controls |
| Event Outbox | `inventory.changed` for search/PDP |

### 3.4 Quantity algebra

```text
invariants:
  on_hand >= 0
  reserved >= 0
  non_sellable >= 0
  reserved + non_sellable <= on_hand   -- soft ideal
  available = on_hand - reserved - non_sellable >= 0  -- hard for selling

reserve(q):
  require available >= q
  reserved += q

release(q):
  reserved -= q

commit_ship(q):  -- physical leave building
  on_hand -= q
  reserved -= q

receive(q):
  on_hand += q
```

When WMS adjust would break `reserved <= on_hand`, **don’t clamp quietly**—enter `CONFLICT` workflow.

### 3.5 Reservation protocol

```text
Reserve(order_id, lines[], idem_key, ttl):
  if reservation set exists for idem_key → return it
  plan = Allocate(lines, customer_ctx)
  for each planned line (sequential or parallel per key):
    CAS reserve on position
    on fail → compensate previous; return partial error
  persist Reservation rows OPEN with expires_at
  return reservation_ids

Commit(order_id): mark OPEN → COMMITTED (tied to paid order)
Release(order_id): OPEN/COMMITTED→RELEASED; reserved -= qty
Expire sweeper: OPEN and now > expires_at → Release
```

**Payment interaction:** prefer reserve before or tightly with auth; TTL ≥ payment latency; sweeper is backstop.

### 3.6 Multi-warehouse allocation

| Strategy | Pros | Cons |
|----------|------|------|
| Single FC per order | Simple packing | Lower fill |
| **Split FC (chosen)** | Higher fill | Multi-shipment |
| Regional soft pool | Smooth UX | Promise miss risk |

```text
score(fc) = distance + load + stock_fit + sla_penalty
greedy cover each line by best fc with stock
optional: DP/heuristic minimize shipment count under time budget
```

### 3.7 Promise vs reserve

```text
Promise: may use digest (sku → regional available sum) with TTL seconds
Reserve: always hits position SoT (primary)
Search in_stock boolean: eventual from inventory.changed
```

### 3.8 WMS sync

```text
WMS → event bus → Ingest:
  dedupe(event_id)
  translate to ledger deltas
  apply to Position with CAS/version
  emit inventory.changed

Snapshot recon daily/hourly:
  compare WMS on_hand vs commerce on_hand
  diffs → ops queue / auto-adjust policy
```

**Conflict policy examples:**

- Ship event for qty > reserved → allow ship if on_hand ok but create incident; or require reserve backfill.  
- Cycle count down below reserved → freeze SKU@FC; notify order management to cancel/repromise.

### 3.9 Audit ledger

Every mutation writes a ledger entry **in the same transaction** as position update (or transactional outbox → ledger). Support queries: “why is available 4?” → stream of deltas.

### 3.10 API sketch

```text
GET  /v1/promise?sku=&zip=&qty=
POST /v1/reservations          Idempotency-Key
POST /v1/reservations/{id}/release
POST /v1/reservations/{id}/commit
POST /v1/reservations/{id}/extend
POST /v1/wms/events            (internal)
GET  /v1/positions/{sku}/{fc}
GET  /v1/ledger?sku=&fc=&from=
POST /v1/admin/freeze
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+   +----------+   +------------------+
| PDP/BFF|-->| Promise  |-->| Digest cache     |
+--------+   +----------+   +--------+---------+
                                     ^ invalidate
+----------+  +-------------+        |
| Checkout |->| Reservation |---+    |
+----------+  | API+Alloc   |   |    |
              +------+------+   |    |
                     v          v    |
              +------+----------+----+--+
              | Position shards (SKU)   |
              +------+----------+-------+
                     |          |
                     v          v
              +------+---+  +--+--------+
              | Ledger   |  | Outbox    |--> Kafka --> search/PDP
              +------+---+  +-----------+
                     ^
+-----+   +----------+----+
| WMS |-->| WMS Ingest    |
+-----+   +---------------+
              |
              v
         Reconciler <--> WMS snapshots
```

### 4.2 Reserve sequence

```text
Checkout → ReservationAPI
  → idempotency lookup
  → Allocate FCs
  → CAS Position (sku,fc)
  → write Reservation OPEN + Ledger
  → return OK
Checkout payment fail → Release / wait TTL
Order placed → Commit reservations
Ship → WMS ship event → on_hand/reserved--
```

### 4.3 Compensate partial allocate

```text
Line1 FC_A reserved OK
Line2 FC_B fail
→ Release Line1
→ return 409 INSUFFICIENT_STOCK {sku: line2}
```

### 4.4 Conflict path

```text
CycleCount on_hand=5, reserved=8
→ mark position CONFLICT
→ freeze net-new reserves
→ emit OpsAlert
→ OrderMgmt tool reallocate/cancel 3 units
→ adjust reserved down with audit
→ clear CONFLICT
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Atomic reserve** — conditional update `available >= qty`.  
2. **Idempotent reserve** by key → same reservation set.  
3. **Every position mutation has ledger entry** (same txn/outbox).  
4. **TTL sweeper** eventually frees abandoned OPEN reserves.  
5. **WMS events idempotent** by `event_id`.  
6. **No sell from CONFLICT/FROZEN** positions.  
7. **Commit ≠ ship** — commit binds to order; ship moves physical.  
8. **Single writer per position key** (shard owner).  
9. **Compensate partial multi-line reserves**.  
10. **Oversell metric** must be ~0; page if >0.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Postgres positions + Redis promise; one FC set |
| 10× | Shard by hash(sku); Kafka WMS; ledger stream; replica reads for ops |
| 100× | HotSKU pool; regional inventory cells; digest CQRS; auto recon |
| 1,000× | Hierarchical promise (FC→region→edge); cell isolation; token inventory for deals |

**Caching:**

```text
L1: regional available digest (sku) TTL 1–5s
L2: negative cache for OOS
Reserve: bypass cache
Stampede: singleflight refresh
```

### 5.3 Maintainability

- Explicit reason codes enum.  
- State machine for reservation status.  
- Contract tests WMS event schemas.  
- Chaos: kill mid-reserve → idempotent retry + sweeper.  
- Feature flag capture/commit timing with checkout.

### 5.4 Consistency spectrum

| Data | Model | Why |
|------|-------|-----|
| Position quantities | Strong per key | Oversell |
| Reservation rows | Strong | Checkout |
| Promise digest | Eventual seconds | Scale reads |
| Search stock flag | Eventual | Scale |
| Ledger | Append-only | Audit |
| WMS physical | External SoT | Reconcile |

### 5.5 Oversell prevention deep dive

**Wrong:**

```text
read available
if available >= q: write reserved+=q   # race
```

**Right (SQL sketch):**

```sql
UPDATE inventory_positions
SET reserved = reserved + :q, version = version + 1
WHERE sku=:s AND warehouse_id=:w
  AND (on_hand - reserved - non_sellable) >= :q
  AND status = 'OK'
  AND version = :v;  -- or omit version if predicate sufficient
```

Redis Lua acceptable for hot path **only if** DB/ledger remains authority and recon is solid—defend this carefully in Amazon interviews; many prefer DB/spanner-like primary.

### 5.6 Hot SKU strategies

1. **Shard inventory tokens** — split 1000 units into N buckets with separate keys; allocate random bucket.  
2. **Admission control** — only N checkout attempts/s enter reserve.  
3. **Pre-issued claim codes** for lightning deals.  
4. **Dedicated HotSKU service** + store isolating blast radius.

### 5.7 Sync & audit deep dive

```text
ApplyWmsEvent(e):
  if seen(e.id): return
  begin txn:
    apply deltas with checks
    write ledger(e)
    write outbox
    mark seen(e.id)
  commit
```

Recon: compute position from ledger snapshot checkpoint + replay; compare to row; repair with `RECON_ADJUST` reason.

### 5.8 Observability

| Metric / alarm | Why |
|----------------|-----|
| `oversell_count` | Critical = 0 |
| `reserve_p99` / fail rate | Checkout |
| `open_reservation_age` | Stuck holds |
| `wms_apply_lag` | Sync health |
| `conflict_positions` | Data integrity |
| `recon_diff_abs_qty` | Drift |
| `promise_cache_hit` | Cost/latency |
| `hot_sku_queue_depth` | Sale health |

---

## 6. Wrap-Up

### 6.1 What we designed

A **multi-warehouse inventory system** with clear quantity buckets, atomic reservations to prevent oversell, allocation across FCs, WMS sync with idempotent events, an append-only audit ledger, reconciliation, and progressive scaling via sharding and hot-SKU isolation.

### 6.2 Key decisions worth defending

1. **available = on_hand − reserved − non_sellable**.  
2. **Strong reserve, eventual promise**.  
3. **Inventory owns reserved; WMS owns physical long-term**.  
4. **CAS/conditional updates only**.  
5. **Ledger with every mutation**.  
6. **TTL sweeper + explicit release**.  
7. **Conflict workflow** when reserved > on_hand—no silent clamp.  
8. **Split shipments** for fill rate.  
9. **Hot-SKU isolation** before Prime Day.  
10. **Idempotency** on checkout and WMS.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Redis drift if used for reserve | DB authority; recon |
| WMS lag during receive | Promise understates briefly |
| Reservation TTL vs payment | Align SLAs |
| Mega hot key | Token sharding |
| Multi-region write | Home cell per FC/SKU |
| Marketplace multi-owner | Add seller_id dimension |

### 6.4 How to present in 45 minutes

1. Buckets + invariants (5 min)  
2. Numbers split classes (4 min)  
3. HLD + ownership (7 min)  
4. Reserve/allocate/compensate (12 min)  
5. WMS sync + conflict + ledger (10 min)  
6. Hot SKU + scale + traps (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Model & invariants

**Q: Why separate reserved vs on_hand?**  
A: Physical stock vs sellable commitments; cancels don’t wait for WMS.

**Q: Is available stored or computed?**  
A: Either; if stored, update atomically with components; CHECK constraints help.

**Q: Safety stock?**  
A: `non_sellable` or higher threshold before promise.

**Q: Can on_hand go negative?**  
A: Prefer no; break-glass adjust with alarm if WMS forces it.

### 7.2 Reservations

**Q: Soft hold at add-to-cart?**  
A: Usually no at Amazon scale—too much lock contention; advisory only until checkout.

**Q: How long TTL?**  
A: Cover payment p99 + buffer; too long starves stock.

**Q: Extend reservation?**  
A: Allowed with limits during 3DS/payment pending.

**Q: Commit vs ship?**  
A: Commit binds order; ship decrements physical when it leaves.

**Q: Idempotency key scope?**  
A: Per checkout attempt / order_id; body hash to prevent mismatch.

### 7.3 Multi-warehouse

**Q: Why not 2PC across FCs?**  
A: Latency/fragility; sequential reserve + compensate.

**Q: How minimize split shipments?**  
A: Optimizer scoring shipment count vs ETA; time-bound heuristic.

**Q: Regional pool abstraction?**  
A: Good for promise; still reserve concrete FC before commit.

### 7.4 WMS & recon

**Q: Who is SoT?**  
A: WMS physical; commerce sellable with reservations—reconcile.

**Q: Duplicate tracking scan?**  
A: event_id uniqueness.

**Q: Cycle count below reserved?**  
A: Freeze + ops; don’t hide.

**Q: Out-of-order events?**  
A: version/timestamp policies; snapshot rebuild.

### 7.5 Scale & hot SKU

**Q: Single Postgres row for Lightning Deal?**  
A: Melts; token buckets / admission / dedicated pool.

**Q: Promise at 100M QPS?**  
A: Edge digests; not OLTP.

**Q: Shard key?**  
A: `hash(sku)` common; `hash(sku, fc)` if FC-local cells.

### 7.6 Failure injection

1. Position DB primary down → fail closed reserves; serve stale promise optional.  
2. Duplicate reserve request → same ids.  
3. Sweeper bug frees COMMITTED → invariant tests prevent; page.  
4. Kafka replay WMS → idempotent.  
5. Cache shows in stock, reserve fails → UX refresh.  
6. Partial allocate crash → retry idempotent or compensate.  
7. Ledger write fails → txn abort position update.  
8. FC marked OFFLINE mid-checkout → allocator excludes.  
9. Clock jump → expiries from DB time.  
10. Recon storm → rate-limit auto-adjust; human for large diffs.

### 7.7 Amazon Leadership-flavored probes

**Q: Customer Obsession — oversell or deny?**  
A: Deny at checkout; measure promise accuracy to reduce surprise.

**Q: Ownership — oversell page?**  
A: Inventory service team; joint with checkout/WMS for conflicts.

**Q: Dive Deep — prove zero oversell?**  
A: Conditional updates + property tests + metric + ledger audits.

**Q: Frugality — cache reserves?**  
A: Never cache away correctness.

### 7.8 Comparison traps

**Q: Is this just a counter in Redis?**  
A: Multi-FC, WMS, audit, TTL, conflicts make it a platform.

**Q: Same as online store interview?**  
A: Here inventory is the center; checkout is a client.

**Q: Same as locker capacity?**  
A: Similar reservation ideas; different physical model & WMS.

### 7.9 Extra interviewer traps (high value)

- Exact available formula?  
- What is durable before reserve ACK?  
- Soft cart hold or not—why?  
- reserved > on_hand after cycle count?  
- How do you shard hot SKUs?  
- Promise stale bound?  
- Commit vs ship deltas?  
- Idempotency for WMS ship?  
- Multi-line compensate order?  
- Ledger vs position drift repair?  
- In-transit sell policy?  
- Freeze semantics?  
- How do returns restock?  
- Integer vs float qty?  
- Deal-breaker read-modify-write?

### 7.10 Progressive scale Q&A

**Q: 1×?**  
A: Single DB, careful transactions, basic sweeper.

**Q: 10×?**  
A: Shard + Kafka + promise cache.

**Q: 100×?**  
A: HotSKU path; regional cells; auto recon.

**Q: 1,000×?**  
A: Hierarchical promise; token inventory; cell isolation.

---

## 8. Appendices

## Appendix A — Example schemas

```sql
CREATE TABLE inventory_positions (
  sku TEXT NOT NULL,
  warehouse_id TEXT NOT NULL,
  on_hand INT NOT NULL CHECK (on_hand >= 0),
  reserved INT NOT NULL CHECK (reserved >= 0),
  non_sellable INT NOT NULL CHECK (non_sellable >= 0),
  status TEXT NOT NULL DEFAULT 'OK', -- OK|FROZEN|CONFLICT|OFFLINE
  version BIGINT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (sku, warehouse_id),
  CHECK (reserved + non_sellable <= on_hand OR status = 'CONFLICT')
);

CREATE TABLE reservations (
  reservation_id UUID PRIMARY KEY,
  order_id UUID NOT NULL,
  sku TEXT NOT NULL,
  warehouse_id TEXT NOT NULL,
  qty INT NOT NULL CHECK (qty > 0),
  status TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version BIGINT NOT NULL
);

CREATE UNIQUE INDEX reservations_idem_idx
  ON reservations (idempotency_key, sku, warehouse_id);

CREATE TABLE inventory_ledger (
  entry_id UUID PRIMARY KEY,
  sku TEXT NOT NULL,
  warehouse_id TEXT NOT NULL,
  delta_on_hand INT NOT NULL DEFAULT 0,
  delta_reserved INT NOT NULL DEFAULT 0,
  delta_non_sellable INT NOT NULL DEFAULT 0,
  reason_code TEXT NOT NULL,
  actor TEXT NOT NULL,
  ref_type TEXT,
  ref_id TEXT,
  event_id TEXT UNIQUE,
  ts TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE wms_events_seen (
  event_id TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE warehouses (
  warehouse_id TEXT PRIMARY KEY,
  region TEXT NOT NULL,
  status TEXT NOT NULL,
  timezone TEXT NOT NULL
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Positions, atomic reserve, TTL, ledger, WMS idempotent apply |
| 10× | Shards, Kafka, promise cache, outbox digests |
| 100× | HotSKU, regional cells, auto recon, conflict tooling |
| 1,000× | Hierarchical promise, token pools, cell blast radius |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| FC | Fulfillment center / warehouse |
| on_hand | Units physically counted sellable+held |
| reserved | Units promised to checkouts/orders |
| available | Sellable remainder |
| Promise | Advisory availability read |
| Commit | Bind reserve to placed order |
| WMS | Warehouse management system |
| Ledger | Append-only stock mutation log |
| Hot SKU | Extreme contention item |
| CONFLICT | Invariant broken; selling frozen |

## Appendix D — Estimation cheat-sheet

```text
promise_QPS >> reserve_QPS
open_reservations ≈ reserve_rate × ttl
ledger_writes ≈ 2–5 × stock_mutations
shard_count ≈ peak_reserve_keys × target_per_shard
Never size OLTP from PDP QPS
```

## Appendix E — Reservation state machine

```text
        +------+
        | OPEN |----TTL/cancel----→ RELEASED
        +--+---+
           |
        commit
           v
       COMMITTED ----cancel before ship----→ RELEASED
           |
         ship (WMS)
           v
        (qty leave; reservation closed / consumed)
```

## Appendix F — Reason codes

```text
RECEIVE, SHIP, ADJUST_CYCLE, ADJUST_DAMAGE, RESERVE, RELEASE,
EXPIRE, COMMIT, RETURN_RESTOCK, RECON_ADJUST, TRANSFER_OUT,
TRANSFER_IN, FREEZE, UNFREEZE
```

## Appendix G — Allocate pseudocode

```text
allocate(lines, zip):
  plan = []
  for line in lines:
    fcs = candidates(zip) ranked by score
    need = line.qty
    for fc in fcs:
      take = min(need, available(line.sku, fc))
      if take > 0: plan.add(...); need -= take
    if need > 0: return INSUFFICIENT
  return plan
```

## Appendix H — Compensation matrix

| Failure | Action |
|---------|--------|
| Alloc finds no stock | Return error; no writes |
| Mid-plan CAS fail | Release earlier lines |
| DB timeout unknown | Idempotent retry by key; read state |
| Payment fail | Release or TTL |
| WMS duplicate | No-op |
| Recon small diff | Auto RECON_ADJUST |
| Recon large diff | Ops queue |

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Two concurrent reserves qty=1 stock=1 | One win |
| Duplicate idempotent reserve | Same reservation |
| TTL expiry | reserved restored |
| Ship idempotent | Single apply |
| Cycle count < reserved | CONFLICT + freeze |
| Partial multi-line fail | Full compensate |
| Promise stale in stock | Reserve may still fail safely |
| Ledger sum | Equals position deltas from checkpoint |
| Frozen FC | Allocator skips |
| Hot token shards sum | Equals total sellable |

## Appendix J — Prime Day runbook

1. Pre-split deal inventory into token buckets.  
2. Enable admission control on reserve path.  
3. Freeze nonessential adjusts during peak if needed.  
4. Watch `oversell_count`, `reserve_p99`, hot shard CPU.  
5. Disable wide cache TTLs that hide OOS too long.  
6. Staff conflict ops queue.

## Appendix K — Evolution hooks

```text
seller_id on position for FBA
serial/lot tables referencing reservation lines
in_transit bucket with ETA-aware promise
multi-channel reservations (store + online)
```

---

*End of design doc. Open with §1 quantity buckets + oversell invariant; whiteboard §3.5–3.8 reserve + WMS conflict; close with §5.1 and traps §7.9.*
