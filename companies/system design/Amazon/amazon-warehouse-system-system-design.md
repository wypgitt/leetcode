# System Design: Amazon Warehouse / Fulfillment Center System

> **Focus areas:** Receiving · Stow · Pick · Pack · Ship · Inventory locations · Robotics hooks · Wave planning (high-level) · Idempotent unit moves · Operational SLAs  
> **Style:** End-to-end fulfillment design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct inventory invariants, clear digital twin vs physical world, deal-breakers for “one global qty row” or “no container genealogy”, explicit Amazon ownership / safety / cost-to-serve flavor  
> **Interview theme:** Amazon SDE III / L6 — design the **software backbone of a fulfillment center (FC)** that receives inventory, stows it to locations, picks/packs/ships customer orders, coordinates humans + robots, and plans work in waves—without lying about stock

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

Goal: **bound the FC software**—track inventory in **locations/containers**, execute **receive → stow → pick → pack → ship**, integrate **robotics** as work executors, run **wave planning** at a high level, and preserve **inventory truth** under retries, short picks, and device flakiness.

### 1.0 What this is / is not

| Dimension | **Warehouse / FC (this doc)** | Not this |
|-----------|-------------------------------|----------|
| Primary job | Move physical units through FC processes with digital tracking | Corporate ERP / full Amazon.com storefront |
| Success | Right item, right qty, right ship promise; inventoriable | Perfect ML demand forecast as MVP |
| Entities | FC, SKU, ASN, container, location, pick, pack, shipment, wave | Supplier contract negotiation system |
| Consistency | Strong for inventory reservations/moves | Eventual OK for dashboards |
| Robotics | Hooks / task interface, not building the robot OS | Designing motor controllers |
| Amazon lens | Ownership, safety, cost-to-serve, customer promise | Whiteboard-only graph theory |

**Scope statement:** Design an FC execution system: receiving, stow, pick, pack, ship, inventory locations, robotics task hooks, high-level wave planning—scaled from one FC to a network—with hard inventory invariants.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Receive? | ASN / PO against dock; blind receive optional | Inbound shipment + discrepancy |
| F2 | Stow? | Put units into storage locations / totes / shelves | Location inventory ledger |
| F3 | Pick? | Batch / discrete / zone pick to tote | Work tasks + reservations |
| F4 | Pack? | Pack station verifies & boxes | Pack completeness checks |
| F5 | Ship? | Hand off to carrier / sortation | Shipment + tracking labels |
| F6 | Inventory model? | SKU qty per location/container; serialized optional | Dual-control moves |
| F7 | Robotics? | AMR / ASRS / conveyors as executors | Task API; human fallback |
| F8 | Waves? | Plan pick waves by cutoff / affinity | Planner + release engine |
| F9 | Problem solve? | Short pick, damage, misstow | Exception workflows |
| F10 | Cycle count? | Directed counts; adjust with approval | Inventory adjustment SM |
| F11 | Multi-FC? | Network of FCs; this design is FC-local + network hooks | FC as cell |
| F12 | Hazmat / cold chain? | Attributes constrain locations | Slotting rules |
| F13 | Returns inbound? | GR (goods return) path into receive/stow | Separate reason codes |
| F14 | Labor? | Associate devices (RF/scanner/apps) | Task assignment |
| F15 | SLA / promise? | Cutoff times drive wave release | Time-aware planning |

**MVP functional scope:**

1. **Receive** against ASN; create inventory in receiving area.  
2. **Stow** to storage locations with scan verification.  
3. Maintain **inventory balances** by `(fc_id, location_id, fnsku/sku, condition)`.  
4. **Reserve** inventory for shipments/orders.  
5. Create **pick tasks** (human or robot).  
6. **Pick confirm** with short-pick handling.  
7. **Pack** verify & create packages.  
8. **Ship** confirm / carrier handoff.  
9. **Wave planning** high-level: group work by cutoff & zone.  
10. **Robotics hooks**: assign/cancel/complete tasks.  
11. Exceptions, cycle count, audit events.  
12. Metrics: units/hour, OTIF inputs, inventory accuracy proxies.

**Out of MVP:**

- Global multi-node inventory optimization (network transfer planner as hook)  
- Full last-mile routing  
- Building robot firmware / SLAM  
- Perfect real-time digital twin of every millimeter  
- Supplier portal / procurement  
- Full HR workforce management (basic task assignment only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Scan latency | Associate UX | p99 < 200–300 ms for confirm |
| N2 | Inventory correctness | No silent oversell inside FC | Strong reservations + conditional updates |
| N3 | Durability | Don’t lose confirms | Durable write before ACK to device |
| N4 | Availability | FC shift continuity | Degrade planning; keep execute path |
| N5 | Throughput | Peak Prime-like days | Horizontal workers; sharded locations |
| N6 | Traceability | Each move auditable | Event log / container genealogy |
| N7 | Safety | Interlock with robotics zones | Soft constraints in software; hard in controls |
| N8 | Idempotency | Retried scans | Idempotent task completes |
| N9 | Operability | Clear ownership | Runbooks; kill switches for waves |
| N10 | Scalability | FC cell + network | Progressive table |
| N11 | Clock / cutoff | Ship promise | FC local time + UTC storage |
| N12 | Offline handheld | Brief Wi‑Fi blip | Bounded local queue with care |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Truck ASN → dock receive → pallets labeled → stow to bins → inventory available.  
2. Customer order allocated to FC → wave released → picks created → associates/robots pick to tote → pack → label → ship.  
3. Short pick → reservation released / reallocated → problem-solve → cycle count triggered.  
4. Robot AMR tasked to move tote from A to pack → complete event → human pack.  
5. Cycle count directed → variance → approved adjustment.  
6. Wave for 2pm carrier cutoff → affinity by aisle → released in pulses.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double scan confirm | Idempotent task_id + qty |
| Reserve but never pick | TTL / wave cancel releases |
| Pick confirms > reserved | Reject; investigate |
| Location full at stow | Suggest alternate; don’t overfill digital |
| Damaged unit | Condition code; quarantine location |
| Robot task fail | Reassign human; location lock policy |
| Inventory negative attempt | Conditional write fails closed |
| ASN mismatch | Discrepancy ticket; partial receive |
| Wrong item scanned | Hard fail; coaching signal |
| Network blip mid-confirm | Client retry same idem key |
| Wave over-release | Congestion; throttle by zone WIP limits |
| Pack missing item | Block ship; return to pick/PS |
| Carrier closeout early | Freeze wave; expedite path |
| Dual associate same bin | Location locking / task exclusivity |
| Serialized item (high value) | Serial capture mandatory |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 large FC) | 10× | 100× | 1,000× |
|--------|------------------------|-----|------|--------|
| FCs | 1 | 10 | 100 | 1,000 |
| Active SKUs / FC | 1M | 1M | 1–2M | 2M+ |
| Storage locations / FC | 5M | 5M | 5–10M | 10M+ |
| Units received / day / FC | 1M | 1M | 1–2M | 2M+ |
| Units shipped / day / FC | 1M | 1M | 1–2M | 2M+ |
| Peak scan confirms / s / FC | 5K | 5K | 8K | 10K+ |
| Concurrent associates + robots | 3K | 3K | 5K | 8K |
| Open pick tasks | 200K | 200K | 400K | 500K+ |
| Waves / day / FC | 50 | 50 | 80 | 100+ |
| Network orders routed / day | 1M | 10M | 100M | 1B |

**Interpretation:** 10×/100×/1,000× is primarily **more FCs (cells)** plus heavier peak days—not one database holding the world. Each FC is a **blast-radius cell**.

**What each jump forces:**

- **10× FCs:** standardized FC cell pack; network allocation service; config-as-code.  
- **100×:** multi-region control planes; per-FC data residency; robotics fleet diversity adapters.  
- **1,000×:** strong cell isolation; hierarchical network planning; chaos/ops factories; automated FC bring-up.

### 1.5 Etc. (Constraints & Assumptions)

- Physical world can disagree with software—**exception flows are features**.  
- Inventory quantities are integers; **never float**.  
- “Available” = on-hand − reserved − damaged/quarantine (policy).  
- Robotics are **unreliable executors**; software must re-plan.  
- Wave planning here is **high-level** (grouping/release), not a full OR-tools thesis.  
- Order capture / website is upstream; we consume **fulfillment requests**.

**Scope statement:**

> Design an FC execution platform covering receive, stow, pick, pack, ship, location-level inventory, robotics tasking hooks, and high-level wave planning—correct under retries and exceptions—scaling as a network of FC cells from 1 → 10 → 100 → 1,000 sites.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Scan / event throughput

```text
1M units shipped/day / FC ÷ 86400 ≈ 11.6 units/s average
But work is shift-concentrated: ~12h effective → ~23 u/s avg in shift
Peak 5–10× in bursts ⇒ thousands of scan events/s

Per unit lifecycle events (rough):
  receive scan 1
  stow scan 1–2
  pick scan 1
  pack scan 1–3
  ship scan 1
→ ~6–10 inventory-related events per unit
Peak confirms ~5K/s/FC plausible with robotics + many associates
```

### 2.2 Storage

```text
Location balance row ~100–200 B
5M locations × 200 B = 1 GB (tiny)
But history/events dominate:
1M units × 8 events × 300 B ≈ 2.4 GB/day event log per FC
Retain hot 30–90d; cold longer for loss prevention

Task rows: 200K open × 500 B = 100 MB hot
Order/shipment headers separate
```

### 2.3 Bandwidth

```text
Handheld: small JSON scans ~1 KB
5K/s × 1 KB = 5 MB/s per FC — modest
Robot telemetry higher — sample / edge aggregate; don’t mirror raw lidar to cloud
Label printing: local print bridges
```

### 2.4 Memory / hot state

```text
Active reservations + open tasks in memory/cache per FC: tens of GB max
Location index for slotting suggestions: sharded
Do NOT build one global in-mem inventory for 1000 FCs in one process
```

### 2.5 Latency budget (pick confirm)

```text
Device → edge API     20–50 ms
AuthZ + idempotency   5–10 ms
Conditional inventory 10–30 ms
Task update + events  10–20 ms
Ack                   ---
Total p99 target ≤ 200–300 ms
```

### 2.6 Wave planning compute

```text
Orders in horizon H: e.g. 500K
Grouping by cutoff/zone/affinity: stream+batch every few minutes
CPU bound OK on planner workers; must not block execute path
Kill switch: stop release if pack outbound congested
```

### 2.7 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| Peak day 2× in one FC | Task DB / location hotspots | Shard location ranges; WIP caps |
| 10× FCs | Config drift / network routing | Cell template; control tower |
| 100× FCs | Ops cognitive load | Automation; standardized adapters |
| 1,000× | Organizational + data gravity | Strict cell autonomy; federated metrics |

### 2.8 Cost-to-serve sketch

```text
Cost drivers: touches/unit, walk time, rebin, exceptions, voided packs
Software lever: better batching, fewer short picks via accuracy, robot where ROI
Instrument: UPH, defect ppm, ship promise miss, inventory accuracy
```

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Inventory truth over cleverness** — conditional writes; no negative stock.  
2. **Execute path sacred** — planning can lag; scanning must work.  
3. **Human + robot interchangeable** behind task interface.  
4. **FC is a cell** — blast radius limited.  
5. **Exceptions are first-class** — short pick, damage, misstow.  
6. **Customer promise** — cutoffs drive release, not vanity utilization alone.  
7. **Safety & audit** — every adjustment attributable.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Inbound / Receiving | ASN, dock, receive confirms |
| Inventory Service | Balances, reservations, moves |
| Location / Slotting | Location master, constraints, suggestions |
| Stow Service | Stow tasks & confirms |
| Fulfillment Request | Orders/shipments allocated to FC |
| Wave Planner | Group & release work |
| Task Service | Pick/move/count tasks lifecycle |
| Pick Execution | Confirm, short pick, re-pick |
| Pack Service | Station workflows, package contents |
| Ship / Outbound | Labels, carrier handoff, closeout |
| Robotics Adapter | Translate tasks ↔ robot fleet mgr |
| Problem Solve | Exception queues |
| Device Gateway | Handhelds, scanners, printers |
| FC Config | Layout, SOPs, feature flags |
| Event Log | Immutable movement history |
| Metrics / Control Tower | Site & network views |

### 3.3 Inventory invariants (say early)

```text
For each (fc, location, sku, condition):
  on_hand >= 0
  reserved >= 0
  on_hand >= reserved
  available = on_hand - reserved - hold_qty

Moves are dual-entry:
  -qty at source (conditional)
  +qty at dest
  event_id unique
```

**Deal-breaker:** a single global `sku_qty` without location when you need pick paths.

### 3.4 Container & location model

```text
Location: aisle-bay-shelf-bin / pallet slot / buffer / pack station
Container: tote, pallet, carton (can nest)
Unit: SKU qty inside location or container
Genealogy: container_id history for traceability
```

Pick often targets **location → tote container**; pack consumes tote contents into **outbound carton**.

### 3.5 Key state machines

**InboundShipment:** `EXPECTED → ARRIVED → RECEIVING → RECEIVED / DISCREPANT → CLOSED`

**InventoryReservation:** `OPEN → CONSUMED / RELEASED / EXPIRED`

**Task:** `CREATED → ASSIGNED → IN_PROGRESS → COMPLETED / CANCELLED / FAILED`

**Wave:** `PLANNED → RELEASED → IN_PROGRESS → COMPLETED / CANCELLED`

**Package:** `OPEN → PACKED → LABELED → SHIPPED`

**Shipment:** `ALLOCATED → PICKING → PACKING → READY → SHIPPED / CANCELLED`

### 3.6 API sketch

```text
POST /v1/fc/{fc}/inbound/{asn}/receive
POST /v1/fc/{fc}/stow/confirm
POST /v1/fc/{fc}/inventory/reserve
POST /v1/fc/{fc}/inventory/move
POST /v1/fc/{fc}/waves:plan
POST /v1/fc/{fc}/waves/{wid}/release
POST /v1/fc/{fc}/tasks/{tid}/assign
POST /v1/fc/{fc}/tasks/{tid}/complete     Idempotency-Key
POST /v1/fc/{fc}/pack/confirm
POST /v1/fc/{fc}/ship/confirm
POST /v1/fc/{fc}/counts/confirm
POST /v1/fc/{fc}/robots/tasks             (adapter)
POST /v1/fc/{fc}/devices/events
```

### 3.7 Data model (logical)

| Entity | Key fields |
|--------|------------|
| FC | fc_id, region, timezone, status |
| Location | location_id, type, zone, attrs, max_cube/weight |
| Sku/Fnsku | identifiers, dims, hazards, serial_flag |
| Balance | fc, location, sku, condition, on_hand, reserved |
| Container | container_id, type, location_id?, state |
| ASN/InboundLine | expected qty, received qty |
| FulfillmentReq | fr_id, order refs, cutoff, priority |
| Reservation | res_id, fr_id, location, sku, qty |
| Wave | wave_id, cutoff, strategy, state |
| Task | task_id, type, assignee, from/to, qty, state |
| Package | pkg_id, contents[], tracking |
| Event | event_id, type, actors, before/after |

### 3.8 Allocation vs execution

```text
Network Allocation (upstream): choose FC for order
FC Execution (this system): reserve locations, pick, pack, ship
```

Interview tip: clarify where **FC selection** lives—usually upstream. This design assumes FRs already targeted to an FC.

### 3.9 Wave planning (high-level)

Objectives:

- Meet **carrier cutoffs** / customer promise.  
- Improve **affinity** (same aisle batches) to cut travel.  
- Respect **WIP limits** at pick/pack/ship.  
- Pulse release to avoid flood.

```text
Planner loop (every N seconds / minutes):
  1. Pull OPEN FRs within horizon, sorted by cutoff/priority
  2. Soft-allocate locations (read available)
  3. Cluster into waves (zone, cutoff bucket, ship method)
  4. Create reservations (strong) + tasks
  5. Release when labor/robot capacity & downstream WIP OK
```

Not solving TSP optimally in MVP—**good heuristics + WIP control** beat perfect math that ships late.

### 3.10 Robotics hooks

```text
Task Service --(canonical task)--> Robotics Adapter --(vendor API)--> Fleet Manager
                              \--(same task)--> Human Task UI
```

Canonical task fields: `move_container`, `pick_units`, `count_location`, priorities, geo hints, cancel tokens.

Adapter concerns: vendor diversity, retries, partial failure, safety zones (software advises; PLC enforces).

### 3.11 Tradeoffs table

| Decision | Option A | Option B | Choose when |
|----------|----------|----------|-------------|
| Inventory store | Per-FC DB | Shared multi-FC DB | Always prefer per-FC cell |
| Reservation | Soft then hard | Hard immediately | Hard before pick release |
| Pick model | Discrete | Batch/zone | Volume & layout |
| Robot coupling | Sync RPC | Async task events | Scale / flaky robots |
| Wave size | Huge batches | Small pulses | Congestion vs travel |
| Serial tracking | All items | High-value only | Cost vs risk |
| Source of truth | Scans | Cameras | Scans MVP |

### 3.12 Deal-breakers

1. Negative inventory allowed “temporarily” without exception state.  
2. Non-idempotent pick confirms.  
3. Planner writes that block scanning path on failure.  
4. One global inventory DB for all FCs.  
5. No short-pick workflow.  
6. Robot vendor API embedded everywhere (no adapter).  
7. Adjustments without audit/approval policy.  
8. Ignoring container contents at pack.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII (single FC cell)

```text
  Upstream Network Allocation
            |
            v
  +--------------------+
  | Fulfillment Request|
  | Ingest             |
  +---------+----------+
            |
            v
  +--------------------+     +------------------+
  | Wave Planner       |---->| Task Service     |
  +---------+----------+     +--------+---------+
            |                         |
            v                         v
  +--------------------+     +------------------+
  | Inventory Service  |<--->| Pick / Stow /    |
  | (balances+reserve) |     | Count Execution  |
  +---------+----------+     +--------+---------+
            |                         |
            |                         +------> Robotics Adapter ---> Fleet
            |                         |
            |                         +------> Device Gateway ---> RF/Apps
            v
  +--------------------+     +------------------+
  | Pack Service       |---->| Ship / Outbound  |
  +--------------------+     +------------------+
            |
            v
     Event Log / Metrics / Problem Solve

  Inbound path:
  Dock/ASN -> Receiving -> Inventory(+) receiving loc -> Stow tasks -> Storage loc
```

### 4.2 Sequence: pick confirm

```text
Associate   Device GW    Task Svc    Inventory    Event Log
   |           |            |            |            |
   |--scan---->|--complete->|            |            |
   |           |            |--cond dec->|            |
   |           |            |--ok------->|--append--->|
   |           |            |--task done-|            |
   |<--ACK-----|<-----------|            |            |
```

### 4.3 Sequence: short pick

```text
Pick complete qty < expected
Inventory: consume only picked qty; release remainder reservation
Task: COMPLETED_SHORT
FR: backorder / reallocate / cancel line (policy)
Trigger: cycle count task on location
Problem Solve work item opened
```

### 4.4 Sequence: robot move tote

```text
Task(MOVE_CONTAINER) -> Adapter -> Fleet
Fleet EVENT running/completed/failed -> Adapter -> Task Svc
On complete: Inventory move container location; event appended
On fail: Task FAILED; reassign human; optional location lock clear
```

### 4.5 Multi-FC network

```text
              +------------------------+
              | Network Control Tower  |
              | (routing, config, KPI) |
              +-----------+------------+
                          |
      +-------------------+-------------------+
      v                   v                   v
  [FC Cell A]         [FC Cell B]         [FC Cell C]
  invent/tasks        invent/tasks        invent/tasks
  local execute       local execute       local execute
```

No cross-FC synchronous inventory join on the hot path.

### 4.6 Wave release control loop

```text
Metrics: pack WIP, ship dock queue, picker utilization
   |
   v
Release Controller --throttle--> Wave Planner
   |
   +--> pause release if pack WIP > L_high
   +--> resume if pack WIP < L_low
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Conditional inventory updates** — never decrement below reserved/on_hand constraints.  
2. **Idempotent task completion** — same key ⇒ same effect.  
3. **Reservation conservation** — reserved qty always backed by on_hand.  
4. **Event immutability** — corrections via compensating events.  
5. **Pack contents ⊆ picked contents** for the FR (policy).  
6. **Ship only packed & labeled packages**.  
7. **Adjustments audited** with reason codes.

#### 5.1.2 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Inventory DB blip | Scans fail | Multi-AZ; local retry; freeze planner |
| Duplicate confirms | Double dec risk | Idempotency records |
| Robot lost tote | Virtual/physical diverge | Timeout → PS; cycle count |
| Hot location row | Latency spike | Split SKUs across locations; shard |
| Planner bug over-release | Congestion | WIP kill switch |
| Clock skew cutoffs | Miss promise | NTP; cutoff margin |
| Poison message | Worker crash loop | DLQ; quarantine |
| Mis-slot hazmat | Safety risk | Hard constraints; block stow |

#### 5.1.3 Durability & backup

- Per-FC multi-AZ data plane.  
- Event log streamed to cold store.  
- PITR for balances.  
- Rebuild projections from events for disaster (rare, practiced).

#### 5.1.4 Consistency nuances

| Path | Consistency |
|------|-------------|
| Reserve / move / confirm | Strong, single FC |
| Wave planning reads | Snapshot / slightly stale OK before hard reserve |
| Control tower KPIs | Eventual |
| Cross-FC transfers | Explicit transfer orders; two-phase receive |

#### 5.1.5 Security & safety

- Device auth; associate identity on every confirm.  
- Privilege for inventory adjust.  
- Robotics geofence coordination with site safety systems.  
- PII minimal (shipment addresses in outbound subsystem with controls).

### 5.2 Scalability

#### 5.2.1 FC cell as unit of scale

Scale-out = more cells. Scale-up inside FC:

- Shard balances by `hash(location_id)` or zone.  
- Task queues partitioned by zone.  
- Pack stations stateful sticky sessions optional.  
- Event log partitioned by time + zone.

#### 5.2.2 Hot SKU / hot bin

```text
Popular SKU stowed in many locations (dispersal)
Pick tasks spread; avoid single-row hotspot
Dynamic slotting suggestions for fast movers near pack
```

#### 5.2.3 Execute vs plan isolation

Separate thread pools / services / DB prioritization so a heavy plan job cannot starve confirms. Use separate clusters if needed at peak.

#### 5.2.4 Robotics scale

Thousands of robots ⇒ event-driven; backpressure; don’t RPC-sync each wheel tick into inventory.

#### 5.2.5 Multi-region network

FC data stays regional near the site. Network services (allocation, promise) are regional/global with caches. Avoid chatty cross-region inventory.

#### 5.2.6 Cost controls

| Lever | Mechanism |
|-------|-----------|
| Touches | Batch picks; fewer rebin |
| Exceptions | Accuracy programs; directed counts |
| Robot ROI | Adapter metrics hours saved |
| Storage | Event compaction; sampling telemetry |
| Compute | Planner cadence adaptive |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Team |
|---------|------|
| Inventory primitives | Inventory Platform |
| Inbound | Inbound Eng |
| Pick/Pack/Ship execute | Outbound Eng |
| Wave planner | Planning Eng |
| Robotics adapters | Robotics Integration |
| Devices | Device Platform |
| FC bring-up / config | FC Soft Launch |
| Promise inputs | Capacity & Promise (partner) |

#### 5.3.2 Safe evolution

- Task schema versioned.  
- Additive event types.  
- Compatibility matrix for handheld app versions.  
- Shadow planning before new wave strategies.  
- Feature flags per FC.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Confirm API availability | 99.9%+ during shift |
| Confirm p99 | ≤ 300 ms |
| Reservation commit p99 | ≤ 100 ms |
| Inventory inconsistency incidents | near-zero; page on negative attempts |
| Wave release adherence to cutoff | tracked % |
| Robot task success rate | vendor SLO + reassign latency |

Dashboards: UPH, short-pick rate, pack defect ppm, dock-to-stock hours, ship misses.

#### 5.3.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1 FC | Full execute path; inventory invariants; basic waves |
| 10 FCs | Cell template; network FR ingest; config promotion |
| 100 FCs | Adapter marketplace; federated KPIs; chaos drills |
| 1,000 FCs | Automated bring-up; strict cell autonomy; hierarchical ops |

### 5.4 Deep dive: reservation & pick math

```text
reserve(fr, sku, qty):
  choose locations via strategy (FIFO, closest, partial OK)
  for each slice:
    conditional: reserved' = reserved + slice WHERE on_hand - reserved >= slice
  persist Reservation slices

complete_pick(task, qty_picked):
  assert qty_picked <= reserved_slice
  on_hand -= qty_picked
  reserved -= qty_picked
  container_contents += ...
  if qty_picked < expected: release residual; SHORT flow
```

### 5.5 Deep dive: slotting constraints

Location attrs ∩ SKU attrs must pass:

- Hazmat class compatibility  
- Temp zone  
- Weight/cube remaining  
- Velocity class (fast movers forward)  
- High-value cage

Stow suggestion API returns ranked candidates; associate may override within policy.

### 5.6 Deep dive: idempotency keys

```text
key = hash(device_id, task_id, scan_payload, client_seq)
result stored with response
retries return stored result
mismatched body → 409
```

### 5.7 Deep dive: digital vs physical divergence

Sources: theft, damage not scanned, robot drop, software bug.

Controls:

- Directed cycle counts  
- Random audits  
- Variance thresholds auto-hold location  
- Cameras as secondary (not MVP SoT)  
- Shrink accounting workflows

### 5.8 Deep dive: pack verification

```text
expected = sum(picked for FR)
scanned into carton must match expected set
overscan → block
underscan → block ship
substitutions → explicit policy only
```

### 5.9 Testing & resilience

- Property tests: inventory never negative.  
- Fault injection: duplicate completes, robot fail mid-move.  
- Wave simulator with WIP limits.  
- Handheld offline bounded queue tests.  
- FC failover drill (rare): read-only mode + paper SOP (acknowledge reality).

### 5.10 Amazon leadership connection (brief)

- **Customer Obsession:** promise/cutoff first-class.  
- **Ownership:** inventory accuracy & ship misses are your metrics.  
- **Invent & Simplify:** task interface unifies human/robot.  
- **Dive Deep:** short-pick rates tell the truth.  
- **Deliver Results:** Prime day is an architecture requirement, not a surprise.

---

## 6. Wrap-Up

### 6.1 30-second recap

FC software is a **cell** with a strong **inventory ledger** (location-level), **idempotent execution** for stow/pick/pack/ship, **wave planning** that releases work under WIP/cutoff constraints, and a **robotics adapter** so fleets are swappable. Exceptions (short pick, damage, counts) keep the digital twin honest. Scale = more FC cells + peak hardening, not one mega-DB.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Why |
|----------|--------|-----|
| Soft vs hard allocate | Hard reserve before release | Prevents oversell |
| Optimal vs heuristic waves | Heuristics + WIP | Promise reliability |
| Coupled robots | Async adapter | Vendor flakiness |
| Global vs per-FC inventory | Per-FC | Blast radius |
| Camera SoT | No (MVP) | Cost/complexity |

### 6.3 Risks & follow-ups

- Cross-FC transfer orchestration  
- Advanced OR wave optimization  
- Tighter digital twin / CV  
- Returns complexity  
- Labor gamification ethics  
- Hazardous materials edge cases

### 6.4 What “good” looks like

- Interviewer hears **invariants**, **idempotency**, **FC cell**, **WIP-controlled waves**, **robot adapter**  
- Clear execute vs plan isolation  
- Progressive network scale story  
- Ownership of accuracy & promise

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q1 | Is FC selection in scope? | Usually upstream; clarify |
| Q2 | Each/each vs case pack? | Model units; case as container |
| Q3 | Lot/expiry tracking? | Attr on balance for grocery |
| Q4 | Returns? | Inbound with reason codes |
| Q5 | Kitting? | Work orders; BOM explode |
| Q6 | Cross-dock? | Fast path skip stow |
| Q7 | Multi-shipment orders? | Split FRs |
| Q8 | Gift wrap? | Pack attributes |
| Q9 | Dangerous goods? | Slotting + label rules |
| Q10 | Cold chain? | Zone constraints |
| Q11 | Vendor-owned inventory? | Condition/owner attributes |
| Q12 | What is MVP cut? | Single FC happy path + short pick |

### 7.2 Inventory (Q13–Q28)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q13 | Why location-level? | Pick path & accuracy |
| Q14 | How prevent negatives? | Conditional updates |
| Q15 | Soft reservation? | Only inside planner before commit |
| Q16 | Reservation TTL? | Yes; release on cancel |
| Q17 | Partial reservations? | Multi-location slices |
| Q18 | Container nest depth? | Bound depth; events |
| Q19 | Serial numbers? | Mandatory capture when flagged |
| Q20 | Adjustments approval? | Threshold-based |
| Q21 | Rebuild from events? | Possible; expensive; practiced |
| Q22 | Quarantine? | Hold qty / special locations |
| Q23 | Damaged vs sellable? | Condition enum |
| Q24 | Idempotent moves? | event_id unique |
| Q25 | Concurrent stow/pick same bin? | Locks or conditional qty |
| Q26 | Inventory accuracy metric? | Count variance / audit |
| Q27 | Ghost inventory? | Counts + process discipline |
| Q28 | Float quantities? | Never |

### 7.3 Pick / pack / ship (Q29–Q44)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q29 | Discrete vs batch pick? | Volume dependent |
| Q30 | Zone picking? | Handoffs via containers |
| Q31 | Short pick cascade? | Recount + reallocate |
| Q32 | Pick to light? | Device class under same tasks |
| Q33 | Pack verification depth? | Scan each vs weight check |
| Q34 | Overbox / underbox? | Cube algorithm assist |
| Q35 | Label failure? | Reprint; package state |
| Q36 | Carrier sortation? | Outbound subsystem |
| Q37 | Cancel after pick? | Restow flow |
| Q38 | Split package? | Multi-pkg shipment |
| Q39 | Single item / SIPP? | Fast path |
| Q40 | Quality audit sampling? | Random pack audits |
| Q41 | Address PII? | Scoped outbound service |
| Q42 | End-of-day closeout? | Wave freeze + dock schedule |
| Q43 | Manifesting? | Carrier integration |
| Q44 | Mis-ship cost? | Defect ppm ownership |

### 7.4 Waves & planning (Q45–Q56)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q45 | What is a wave? | Batch of work with shared intent |
| Q46 | Optimize travel perfectly? | No; heuristics + WIP |
| Q47 | Pulse vs big bang release? | Pulse preferred |
| Q48 | Priority rush orders? | Jump queue with caps |
| Q49 | Labor shortage? | Shrink release; OT tools outside |
| Q50 | Planner bug? | Kill switch; shadow mode |
| Q51 | Affinity key? | Aisle/zone/ship method |
| Q52 | Replan mid-wave? | Cancel unstarted tasks carefully |
| Q53 | Cutoff miss prediction? | Control tower signals |
| Q54 | Backlog explosion? | Cap open tasks |
| Q55 | Multi-cutoff horizons? | Buckets |
| Q56 | Why isolate planner CPU? | Protect confirm latency |

### 7.5 Robotics (Q57–Q68)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q57 | Why adapter? | Vendor diversity |
| Q58 | Human fallback? | Same task schema |
| Q59 | Partial robot failure? | FAILED + reassign |
| Q60 | Telemetry volume? | Edge aggregate |
| Q61 | Safety in software? | Advise; hardware interlocks own safety |
| Q62 | Container handoff? | Explicit states |
| Q63 | Map changes? | Location master versioning |
| Q64 | Latency robot events? | Async; timeouts |
| Q65 | Multi-agent contention? | Fleet manager; software WIP |
| Q66 | Simulate robots? | Digital twin for tests |
| Q67 | Battery charging tasks? | Fleet-owned; not inventory |
| Q68 | ROI tracking? | Task time metrics |

### 7.6 Scale & ops (Q69–Q76)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q69 | Shard key inside FC? | Zone/location hash |
| Q70 | Hot SKU strategy? | Multi-location dispersal |
| Q71 | FC outage mode? | Stop new FRs; finish in-flight carefully |
| Q72 | Bring up new FC? | Cell template automation |
| Q73 | Data residency? | Keep FC local |
| Q74 | Peak day prep? | Load tests; WIP configs; staffing inputs |
| Q75 | Cross-cell query? | Federated metrics only |
| Q76 | Migration of location schema? | Versioned layout maps |

### 7.7 Behavioral / Amazon (Q77–Q80)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q77 | Inventory went negative in prod | Page; freeze adjustments; replay events; fix conditional path |
| Q78 | Prime day pack congestion | Kill switch on release; surge pack labor; postmortem |
| Q79 | Robot vendor misses SLA | Reassign humans; dual-source adapters |
| Q80 | Disagree with ops on wave size | Data: ship misses vs UPH; experiment per FC flag |

---

## 8. Appendices

### Appendix A — Balance fields

| Field | Meaning |
|-------|---------|
| on_hand | Physically believed present |
| reserved | Committed to open work |
| hold_qty | QA/quarantine |
| available | on_hand − reserved − hold |

### Appendix B — Example balance record

```json
{
  "fc_id": "FC-ABE2",
  "location_id": "A-12-3-4",
  "sku": "FNSKU123",
  "condition": "NEW",
  "on_hand": 7,
  "reserved": 2,
  "hold_qty": 0,
  "version": 8841
}
```

### Appendix C — Conditional update pseudocode

```text
UPDATE balances
SET on_hand = on_hand - :q,
    reserved = reserved - :q,
    version = version + 1
WHERE fc=:fc AND loc=:loc AND sku=:sku
  AND on_hand >= reserved
  AND reserved >= :q
  AND version = :v
```

### Appendix D — Task types

| type | from → to |
|------|-----------|
| STOW | receive → storage |
| PICK | storage → tote |
| MOVE_CONTAINER | loc → loc |
| COUNT | location |
| REBIN | tote → shelf |
| PACK_ASSIST | station |

### Appendix E — Event types (sample)

`RECEIVE_CONFIRM`, `STOW_CONFIRM`, `RESERVE`, `RESERVE_RELEASE`, `PICK_CONFIRM`, `PICK_SHORT`, `PACK_CONFIRM`, `SHIP_CONFIRM`, `ADJUST`, `COUNT_RESULT`, `ROBOT_TASK_FAILED`

### Appendix F — Error codes

| Code | Meaning |
|------|---------|
| INSUFFICIENT_AVAILABLE | Reserve fail |
| VERSION_CONFLICT | Retry |
| IDEMPOTENCY_HIT | Return prior result |
| IDEMPOTENCY_MISMATCH | 409 |
| TASK_NOT_ASSIGNED | Illegal complete |
| SCAN_MISMATCH | Wrong SKU/loc |
| SHORT_PICK | Partial path |
| WIP_CAP_EXCEEDED | Release denied |
| HAZMAT_CONSTRAINT | Stow blocked |
| WAVE_FROZEN | Cutoff/ops freeze |

### Appendix G — Anti-patterns

1. Global qty without locations.  
2. Planner in the scan request path.  
3. Embedding vendor robot SDK in pick service.  
4. Silent auto-adjust to fix negatives.  
5. Unbounded open tasks.  
6. Shared mutable tote without ownership.  
7. Float kilos as inventory counts for eaches.  
8. Cross-FC synchronous reserve on hot path.

### Appendix H — Capacity worksheet

```text
FC count = ____
locations/FC = ____
peak confirms/s = ____
open tasks target = ____
pack WIP L_high/L_low = ____ / ____
event retention days = ____
robot count = ____
```

### Appendix I — 45-minute timebox

| Min | Focus |
|-----|-------|
| 0–5 | Scope FC vs network; FR/NFR |
| 5–12 | Estimation; events/unit |
| 12–25 | HLD; inventory + flows |
| 25–35 | Deep dive: reserve/pick OR waves |
| 35–42 | Robotics hooks; scale cells |
| 42–45 | Wrap ownership/risks |

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| FC | Fulfillment Center |
| ASN | Advanced Shipping Notice |
| FR | Fulfillment Request |
| Fnsku | Fulfillment network SKU id |
| Wave | Planned batch of work |
| WIP | Work in progress |
| Short pick | Found less than expected |
| Slotting | Where to stow |
| AMR | Autonomous Mobile Robot |
| ASRS | Automated Storage/Retrieval |
| UPH | Units per hour |
| OTIF | On-time in-full (input) |

### Appendix K — Ownership RACI (sample)

| Activity | Inventory | Outbound | Planning | Robotics | Inbound |
|----------|-----------|----------|----------|----------|---------|
| Balance correctness | A/R | C | C | C | C |
| Pick confirm API | C | A/R | I | C | I |
| Wave release | C | C | A/R | I | I |
| Robot adapter | C | C | I | A/R | I |
| Receive | C | I | I | I | A/R |

### Appendix L — Progressive scale one-pager

| Scale | Snapshot |
|-------|----------|
| 1 FC | Single cell; full execute; basic waves |
| 10 FCs | Templated cells; network FR; config trains |
| 100 FCs | Adapter ecosystem; federated KPI; chaos |
| 1,000 FCs | Autonomous cells; automated launch; hierarchy |

### Appendix M — Human vs robot matrix

| Work | Human | Robot |
|------|-------|-------|
| Complex pick | Strong | Limited |
| Tote moves | OK | Strong |
| Pack aesthetic | Strong | Weak |
| Count | Strong | Emerging |
| Hazmat judgment | Strong | Constrained |

### Appendix N — Minimal threat model

| Threat | Mitigation |
|--------|------------|
| Fraudulent adjust | Approvals + audit |
| Device spoof | mTLS / device identity |
| Insider theft | Counts; cameras; dual control high value |
| Malicious task flood | AuthZ + rate limits |
| Vendor API abuse | Adapter credentials scoped |

### Appendix O — Wave strategy examples

1. **Cutoff buckets** — all single-SKU SIPP before 2pm truck.  
2. **Zone affinity** — multi-item clustered by aisle.  
3. **Ship method** — Next Day vs Standard separation.  
4. **Robot-first moves** — create MOVE tasks ahead of human picks.

### Appendix P — Short-pick flowchart

```text
expected=5, scanned=3
→ confirm 3
→ release reserve 2
→ open COUNT on location
→ attempt re-reserve elsewhere
→ if fail: delay promise / cancel line / split ship
```

### Appendix Q — Sample complete response

```json
{
  "task_id": "t_123",
  "status": "COMPLETED",
  "qty_confirmed": 2,
  "container_id": "TOTE9",
  "inventory_version": 8842,
  "idempotency_replay": false
}
```

### Appendix R — Interview “say this” (60 seconds)

> “I’d treat each FC as a **cell** with a **location-level inventory ledger** using **conditional updates** and **dual-entry moves**. Upstream sends fulfillment requests; a **wave planner** groups by cutoff and zone but a **WIP controller** throttles release so pack doesn’t drown. Execution is **idempotent tasks** for humans and robots behind one schema, with a **robotics adapter**. Short picks and counts are first-class so the digital twin can re-converge. Scale-out is **more FC cells**, not one global stock counter.”

### Appendix S — Related systems map

```text
Website/Orders → Promise/Allocation → FC Execution (this)
                                      ├── Inventory
                                      ├── Waves/Tasks
                                      ├── Pack/Ship
                                      └── Robotics/Devices
Carriers ← Outbound manifests
Network Control Tower ← metrics
```

### Appendix T — Chaos drill list

1. Duplicate pick confirm storm.  
2. Inventory DB failover mid-shift.  
3. Robot fleet manager outage.  
4. Planner over-release (disable throttle).  
5. Clock jump near cutoff.  
6. Hot SKU single-bin contention.  
7. Event log pipeline delay.  
8. Handheld offline queue replay.

### Appendix U — Dock-to-stock simple SLA

```text
receive_time → stow_complete
Target hours by inbound class (sortable/non)
Measure p50/p90; exceptions separate
```

### Appendix V — Layout versioning

```text
LayoutVersion { zones, locations, blockers }
Devices pin min layout version
Moves validate location exists & active
```

---

*End of Amazon warehouse / fulfillment center system design (Amazon SDE III style).*
