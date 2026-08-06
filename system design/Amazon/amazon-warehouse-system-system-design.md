# System Design: Amazon Warehouse System

> **Focus areas:** Inbound · Storage locationing · Inventory truth · Pick/pack/ship · Waves · Robots/humans · Idempotent tasking · Capacity · Safety · Multi-FC network
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Physical + digital coupling; split planes (inventory vs tasks vs devices); deal-breakers explicit; customer promise (ship dates) sacred
> **Interview theme:** Amazon SDE III / L6 — **Fulfillment Center (FC) software** — operational excellence at Amazon logistics scale

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

Goal: design the software that runs an **Amazon warehouse / FC**—receive inventory, stow it, maintain countable truth, plan picks, execute pick/pack/ship with humans and/or robots, and meet customer ship promises under failure and peak (Prime Day).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | FC execution system (WES/WMS-class) | Entire Amazon.com retail website |
| Inventory | Bin/location-level truth inside FC | Global multi-FC ATP alone (touches it) |
| Orchestration | Work tasks, waves, device teleops | Corporate HR system |
| Amazon lens | Safety, thruput, promise, ownership | Academic OR textbook only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Inbound? | ASN → dock → receive → quality → stow | Inbound state machine |
| F2 | Storage model? | Chaotic / directed; bins, totes, pallets | Location taxonomy |
| F3 | Inventory truth? | Each each/unit trackable by SCANNABLE id where needed | Ledger-like inventory events |
| F4 | Outbound? | Order lines → pick tasks → rebin/pack → ship | Outbound pipeline |
| F5 | Batching? | Waves / batches by cutoff, aisle, SLA | Planner service |
| F6 | Robots? | Optional AMRs / drive units; human-only MVP ok | Device abstraction |
| F7 | Pack? | Box recommend, dunnage, label, SLAM/scan | Pack stations |
| F8 | Exceptions? | Damages, shorts, mis-stows, problem solve | PS queues |
| F9 | Cycle count? | Triggered + scheduled recounts | Inventory adjustment workflow |
| F10 | Safety? | Interlocks, speed zones, e-stop | Safety > thruput |
| F11 | Multi-FC? | Many FCs; this design is per-FC + network hooks | Cell per FC |
| F12 | SLA? | Ship-by / promise tied to carrier cutoff | Cutoff-aware planning |

**MVP scope:**

1. Receive against ASN; create inventory at location.  
2. Stow directed or chaotic with scan verification.  
3. Maintain inventory ledger (location quantities + events).  
4. Explode shippable order lines into **pick work**.  
5. Assign work to associates/robots; confirm picks by scan.  
6. Pack + shipping label; handoff to carrier.  
7. Exception/problem-solve paths; cycle count.  
8. Basic wallboard: thruput, backlog, SLA risk.

**Out of MVP:** full national network optimization, airborne sortation, perfect computer-vision stow without scans, active-active multi-region writes for same bin.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Scan confirmation latency | p99 < 200–300ms perceived |
| N2 | Planner replan | seconds–minutes, not hours |
| N3 | Inventory durability | No silent loss of receive/pick events |
| N4 | Availability | FC can degrade modes; hard stop only for safety |
| N5 | Consistency | Strong per bin/location ledger in FC |
| N6 | Audit | Every move explainable (who/what/where/when) |
| N7 | Safety integrity | Independent of best-effort optimizations |
| N8 | Peak elasticity | Prime Day / holiday 3–10× day |

### 1.3 Cases

**Happy:** ASN receive → stow → order allocated → wave → pick → pack → ship.  
**Edges:** short pick; damaged receive; bin mismatch; robot dead; carrier cutoff miss risk; inventory negative attempt; dual scan race; power blip; safety e-stop; Prime Day surge; toxic/hazmat rules; age-restricted items.

| Case | Behavior |
|------|----------|
| Pick short | Confirm short → PS + inventory adjust workflow; don't ship ghost |
| Double scan | Idempotent task complete |
| Stow to wrong bin type | Reject by rules (size/hazmat/temp) |
| Robot disconnect | Reassign task; location locks released carefully |
| Negative inventory | Forbidden without adjustment reason + authority |
| Cutoff approaching | Re-prioritize waves; shed low-priority work |

### 1.4 Progressive scale

| Metric | Base (1 FC) | 10× | 100× | 1,000× |
|--------|-------------|-----|------|--------|
| FCs | 1 | 10 | 100 | 1,000 |
| Active SKUs / FC | 100K | 100K–1M | 1M | 1M+ |
| Units on hand / FC | 5M | 5–20M | 20M+ | 50M+ |
| Ship units / day / FC | 100K | 300K | 1M | 3M+ |
| Peak pick confirms / s / FC | ~50 | ~150 | ~500 | ~1500 |
| Concurrent associates | 500 | 1.5K | 5K | 10K+ |
| Robots | 0–200 | 500 | 2K | 10K |
| Task events / day / FC | 5M | 20M | 50M | 150M |

**Jumps:** 10× = multi-FC platformization; 100× = network ATP coupling + cell isolation; 1,000× = heterogeneous FC types, global planning hooks, extreme peak tooling.

### 1.5 Scope repeat-back

> Per-FC warehouse execution with inventory ledger, inbound/stow, pick/pack/ship tasking, exceptions, safety, and device abstraction—scaled across many FCs via cells—optimized for thruput and customer ship promise, never at the expense of safety or inventory truth.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
100K units shipped/day ≈ 1.2/s avg; peak 5–10× ⇒ tens of picks/s
Each unit: receive, stow, pick, pack, ship scans ≈ 5–15 scan events
⇒ 0.5M–1.5M scan events/day/FC baseline
Prime Day 5× ⇒ multi-million events/day/FC
```

### 2.2 Storage

```text
Inventory balance row: location_id × asin/fnsku → qty  (~100 B)
5M locations-sparse balances → GBs
Event log: 200–500 B × 1M/day → 200–500 GB/year/FC hot→warm
Photos/video for PS: object store, aggressive TTL
```

### 2.3 Latency budget (pick confirm)

```text
Handheld → edge WiFi → Task Service authz → Inventory ledger CAS → ack
Budget: 50 + 50 + 100 + 50 = ~250ms p99 target
```

### 2.4 Bottlenecks

(1) Inventory hotspot bins (2) wave planning quality (3) WiFi/device (4) pack capacity (5) carrier cutoff synchronization (6) not "HTTP QPS" abstractly.

### 2.5 Cost / frugality

Scan path must be cheap; video always-on is expensive; optimize travel time (labor) which dominates FC cost—software that reduces walking/robot contention pays for itself.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Inventory Ledger | Quantities at locations | Strong, single-writer per location shard |
| Work / Task | Pick/stow/count tasks | Strong per task; idempotent complete |
| Device / Robot | Telemetry, assignment | Eventually; safety PLC separate |
| Planning / Waves | Optimization | Periodic replan; advisory |
| Promise / ATP hook | Reservation with retail | Exactly-once reservation semantics |

**Deal-breaker:** mixing "best effort analytics counters" with inventory ledger.

### 3.2 Components

1. **Inbound Service** — ASN, dock appointments, receive.  
2. **Inventory Service** — ledger + locations.  
3. **Stow Service** — directed putaway suggestions.  
4. **Outbound Allocation** — bind order lines to FC inventory (may sit above FC).  
5. **Wave / Batch Planner** — create pick waves by cutoff/zone.  
6. **Task Service** — assign, start, complete tasks.  
7. **Pack / Ship Service** — cartonization, labels, manifests.  
8. **Problem Solve** — exception workflows.  
9. **Device Gateway** — handhelds, scanners, AMRs, printers.  
10. **Safety Service / Interlock interface** — non-bypassable.  
11. **FC Visibility** — dashboards, SLA risk.  
12. **Config / Catalog local cache** — dims, hazmat, temp.

### 3.3 Inventory event API (sketch)

```text
POST /v1/inventory/events
  {event_id, type: RECEIVE|STOW|PICK|ADJUST|MOVE, location_id, item_id, qty_delta, actor, ts, refs}
Idempotent on event_id
CAS on location version
```

### 3.4 Task state machine

```text
CREATED → ASSIGNED → IN_PROGRESS → COMPLETED
                   ↘ CANCELLED / REQUEUED
IN_PROGRESS → EXCEPTION → PS
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Chaotic storage | Allowed with good scans | Density + thruput |
| Robot-first | Abstract devices | Heterogeneous FCs |
| Wave size | Tunable | Balance WIP vs SLA |
| Reservation | Upstream ATP + local commit | Avoid oversell |
| Offline handheld | Limited local queue | Dangerous if long—prefer degrade modes |

---

## 4. Architecture Diagram

```text
[Carrier/Truck] -> Dock -> Inbound Service -> Inventory Ledger
                                              ^
Retail Order Path -> Allocation/ATP ---------+--> Wave Planner
                                              v
                                         Task Service <--> Device Gateway <--> Associates/Robots
                                              v
                                         Pack/Ship -> Carrier
                                              v
                                         Problem Solve / Cycle Count

Safety PLC / E-stop ----------------independent------------------> Devices
```

### 4.1 Pick sequence

```text
Planner creates PickTask(location, item, qty, order_line_refs)
Assign to worker
Worker scans location → scan item → confirm qty
Task Service: idempotent complete
Inventory: PICK event (-qty) CAS
Container/tote association
Route to pack
```

### 4.2 FC cell

```text
Each FC = failure/isolation cell
No synchronous cross-FC bin locks
Network layer chooses FC; FC executes
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Inventory changes only via idempotent events.  
2. No negative qty without explicit adjustment authority.  
3. Task complete ⇒ matching inventory event (transactional outbox).  
4. Safety interlocks not software-optional.  
5. Ship only packed & scanned contents (trust but verify).  
6. Every adjustment has reason code + actor.  
7. Replan never deletes in-progress work silently—cancel protocol.  
8. Device clocks skew-tolerant; server order for ledger.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith per FC; PG ledger; human picks |
| 10× | Task/inventory split; device gateway; multi-FC clones |
| 100× | Location sharding; planner fleets; robot fleets; ATP tight coupling |
| 1000× | Heterogeneous archetypes (sortable/non-sortable/AMZL); sim platform; global peak command center |

### 5.3 Maintainability

- Location taxonomy config as data.  
- Task type plugins.  
- Simulation digital twin for planner changes.  
- Canary planner in one zone.  
- Golden path integration tests with scan fixtures.

### 5.4 Progressive scale

**1×:** Single FC, humans, simple waves by aisle, nightly cycle counts.  
**10×:** Standardized FC software package; shared device protocols; central config.  
**100×:** Hot SKU isolation, advanced batching, robot contention scheduling, predictive PS staffing.  
**1000×:** Multi-archetype; cross-FC rebalancing suggestions; extreme observability; chaos drills before Prime Day.

### 5.5 Inventory hotspots

Popular ASIN in few bins → pick contention. Mitigate: spread stow, dynamic re-slotting, pick from multiple locations, serialize per location shard with high throughput store (in-memory + WAL) for hottest bins.

### 5.6 Exactly-once work

`event_id` / `task_id` unique; handheld retries safe; "complete" returns same result. Outbox to downstream shipping.

### 5.7 Safety deep dive

- E-stop and light curtains are PLC-owned.  
- WES may request slow/stop zones; cannot suppress e-stop.  
- Software deploy cannot skip safety certification gates.  
- Interview signal: say this early.

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Eventually consistent bin qty | Oversell / empty picks cascade |
| Ship without scan verify | Wrong item SEVs |
| Optimize thruput over e-stop | Injuries — unforgivable |
| Global lock across FC | Deadlocks / outages |
| Planner writes inventory directly | God-service corruption |
| Float dimensions blindly | Cartonization fails |

---

## 6. Wrap-Up

### 6.1 Designed

Per-FC execution: inbound, inventory ledger, stow, wave planning, tasking, pack/ship, PS, device abstraction, safety boundary—scaled by FC cells.

### 6.2 Decisions to defend

1. Inventory event ledger with CAS  
2. Planes split (inventory / tasks / devices / planning)  
3. Idempotent task completion  
4. Safety PLC independence  
5. FC cell isolation  
6. Cutoff-aware waves  
7. Simulation before planner changes  
8. Scan verification culture

### 6.3 Risks

- WiFi / device reliability  
- Hot SKU contention  
- ATP ↔ FC reservation races  
- Labor/robot mix complexity  
- Peak novelty failure modes

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope FC execution vs retail.com |
| 5–15 | Inventory ledger + scans |
| 15–25 | Pick tasking + waves |
| 25–35 | Exceptions, pack/ship, safety |
| 35–45 | Multi-FC scale, Prime Day, ownership |

### 6.5 Closer

> **Amazon Warehouse System**: inventory truth via events, idempotent work, cutoff-aware planning, device abstraction, safety non-negotiable, FC cells, progressive peak scale, clear SEV ownership when promises break.

---

## 7. Deeper / Related Interview Questions

### 7.1 Inventory truth

**Q: Bin qty vs serial/each tracking?**  
A: Depends on item class. Many units are quantity-at-location; high value may be each-ID. Model both.

**Q: How to prevent negative?**  
A: CAS check `qty + delta >= 0` unless ADJUST with privilege.

**Q: Two picks same bin concurrent?**  
A: Serialize on location shard; or optimistic retry; measure hotspot.

**Q: Mis-stow discovered later?**  
A: Cycle count + adjust; possibly quarantine location.

### 7.2 Planning

**Q: Wave vs continuous streaming picks?**  
A: Waves simplify packing/sort; streaming lowers WIP. Many FCs hybrid. State trade-off vs cutoff batches.

**Q: Objective function?**  
A: Minimize SLA misses, then travel, then labor cost—constraints for hazmat/temp.

**Q: Replan storm?**  
A: Version waves; don't thrash in-progress; hysteresis.

### 7.3 Devices & robots

**Q: Who owns robot collision avoidance?**  
A: On-robot / fleet manager; WES assigns goals not wheel ticks.

**Q: Handheld offline 5 minutes?**  
A: Dangerous for ledger—limit cached tasks; block completes requiring CAS if disconnected beyond threshold; park mode.

### 7.4 Promise & ATP

**Q: When is inventory reserved?**  
A: At retail checkout allocation (network) + FC hard commit when work released—define cancel paths.

**Q: Oversell?**  
A: Reservation leases with TTL; reconcile; customer messaging if break— mechanize.

### 7.5 Pack/ship

**Q: Cartonization?**  
A: Bin-pack heuristics with dim weight; ship-API constraints; measure damage rate.

**Q: Label reprint?**  
A: Idempotent label id; void protocols with carrier.

### 7.6 Prime Day

**Q: What do you pre-scale?**  
A: Task/inventory partitions, WiFi surveys, pack stations, PS staffing models, carrier capacity, feature freeze, game-day ROSTER.

**Q: Feature freeze?**  
A: Yes for risky planner changes; allow config toggles.

### 7.7 Safety & people

**Q: Software asks robot to move into blocked zone?**  
A: Device rejects; WES must handle NACK; never assume.

**Q: Ergonomics?**  
A: Task design max reach/weight; not only thruput.

### 7.8 Multi-FC

**Q: Cross-FC transfer?**  
A: Separate transfer orders; each FC ledger local; in-transit state network-level.

**Q: Shard key inside FC?**  
A: `location_id` for inventory; `task_id` for tasks; workers by zone.

### 7.9 Interview traps

**Q: One mega ER diagram replaces event thinking?**  
A: Weak—show events + invariants.  
**Q: Microservices per SKU?**  
A: Absurd.  
**Q: ML pick path before scan truth?**  
A: Wrong order.  
**Q: Eventually consistent inventory "because Kafka"?**  
A: Deal-breaker for bin qty.

### 7.10 Metrics

| Metric | Why |
|--------|-----|
| Units/labor-hour | Efficiency |
| SLA miss rate | Customer |
| Short pick rate | Inventory health |
| Task confirm p99 | UX/thruput |
| Safety incidents | Non-negotiable |
| Replan frequency | Stability |
| PS backlog age | Exceptions |

### 7.11 Ownership

**Q: Who pages for empty pick spike?**  
A: Inventory integrity oncall + FC ops; planner if wave bug. Clear IC.

**Q: Who pages for robot pileup?**  
A: Fleet + WES assignment; safety if near-miss.

### 7.12 Progressive drill

**10×:** packaging FC software; config.  
**100×:** hotspot tech; ATP races.  
**1000×:** archetypes; sim; peak command.

---

## 8. Appendices

### 8.1 Schema sketches

```text
locations(location_id, fc_id, zone, type, attrs)
inventory_balances(location_id, item_id, qty, version)
inventory_events(event_id PK, type, location_id, item_id, qty_delta, actor, ts, refs)
tasks(task_id, type, state, assignee, payload, version)
waves(wave_id, fc_id, cutoff_ts, state)
containers(container_id, type, state, location_or_holder)
shipments(shipment_id, order_id, tracking, state)
adjustments(adj_id, reason, authority, event_id)
```

### 8.2 API checklist

- [ ] Idempotent inventory events  
- [ ] Task assign/complete  
- [ ] Wave create/cancel  
- [ ] Receive/stow  
- [ ] Pack/ship label  
- [ ] PS workflows  
- [ ] Device heartbeat / NACK  

### 8.3 Oncall checklist

- [ ] SLA risk wallboard  
- [ ] Short-pick spike  
- [ ] Ledger CAS fail rate  
- [ ] Device connectivity  
- [ ] Safety alerts independent  
- [ ] Carrier cutoff clocks  
- [ ] Rollback planner/config  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| FC | Fulfillment Center |
| ASN | Advanced Ship Notice |
| Wave | Batch of pick work |
| PS | Problem Solve |
| Chaotic storage | Random stow densification |
| CAS | Compare-and-set version |
| ATP | Available to Promise |
| PLC | Safety controller |

### 8.5 Deal-breaker one-liners

- Kafka-as-inventory-truth without CAS balances  
- Bypass scans to "go faster"  
- Software mute e-stop  
- Cross-FC synchronous bin locks  

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Inventory ledger | Inventory Platform FC |
| Tasks/waves | Work Execution |
| Robots | Fleet |
| Pack/ship | Outbound |
| Safety | Safety Eng + Ops |
| Promise breaks | Joint IC with Retail |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | Monolith, 1 PG, 500 handhelds |
| 10× | Service split, Redis device sess, 10 FC clones |
| 100× | Sharded ledger, planner fleet, AMR integration |
| 1000× | Archetype variants, sim CI, global peak CC |

### 8.8 Failure injection

1. Kill inventory partition — zone shed.  
2. Duplicate task complete — idempotent.  
3. Robot NACK loop — reassign.  
4. Clock skew handheld — server order.  
5. Planner bad canary — rollback zone.  
6. Carrier API down — queue labels; don't invent tracking.

### 8.9 Cartonization sketch

```text
score(box) = waste + dim_weight_cost + damage_risk
constraints: item dims, hazmat separation, max weight
```

### 8.10 Cycle count

Trigger on variance, age, hotspot; freeze location or allow careful picks; adjust with dual control if large.

### 8.11 Hazmat / temp

Rules engine at stow and pack; hard reject; never "warn and continue" for forbidden pairs.

### 8.12 Interview closer checklist

- [ ] Planes split  
- [ ] Ledger CAS  
- [ ] Idempotent tasks  
- [ ] Safety boundary  
- [ ] Waves + cutoff  
- [ ] FC cells  
- [ ] Prime Day story  
- [ ] Metrics + ownership  

### 8.13 Related systems

Retail order service, ATP, transportation, last-mile, catalog dims, locker/ship options, inventory management (network).

### 8.14 Sample events

```text
RECEIVE +10 itemA dock_loc
STOW -10 dock_loc; +10 bin_X
PICK -1 bin_X → tote_T
PACK tote_T → carton_C
SHIP carton_C
```

### 8.15 Digital twin

Replay scans; evaluate planner A/B offline; required before peak.

### 8.16 WiFi reality

Map coverage; captive portals bad; QoS for scan traffic; measure disconnects as SEV precursors.

### 8.17 Labor management hook

Tasks feed staffing; don't build full HR—interfaces only.

### 8.18 Security

Associate auth on devices; privileged adjust roles; audit; physical device attestation where possible.

### 8.19 Cost narrative

Labor travel >> CPU. Optimize picks/hour and reduce PS. Software correctness prevents expensive truck rolls / reships.

### 8.20 LP hooks

Ownership of promise breaks; Dive Deep on short-pick spikes; Frugality on video; Safety Highest Standards; Bias for Action with scan-MVP before CV dream.

---

## Deep Technical Notes — Warehouse

### Location taxonomy

`fc/floor/aisle/bay/shelf/bin` plus virtual (dock, tote, pack_station). Moves are events between locations. Totes are mobile locations.

### Outbox pattern

Task complete in DB transaction + outbox row → pack notification. Avoid dual-write drift.

### Idempotency

Handheld generates `client_event_id` UUID per scan confirm; server dedupe.

### Priority / SLA

Each task has `ship_by`; scheduler is deadline-aware, not pure FIFO.

### Robot contention

Zones, traffic control reserved by fleet mgr; WES should not micro-manage paths.

### Cold path analytics

Stream events to lake for slotting science; never reverse-dependency online path on lake.

### Versioned config

Pick rules, stow constraints, carton tables—config service with canary zones.

### Backpressure

If pack clogged, slow pick assignment (WIP caps). Explicit.

### Multi-each picks

Partial completes with remaining qty; don't force all-or-nothing if policy allows split.

### Damage handling

Quarantine location; remove from ATP quickly via network hook.

---

## Interview Cards — Warehouse

### Card 1: Inventory event ledger

CAS qty; idempotent event_id; audit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Inventory Platform; trust failure = oversell/empty picks.

### Card 2: Planes split

Inventory ≠ planner ≠ devices.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Clear interfaces; god-service is anti-pattern.

### Card 3: Idempotent task complete

Safe handheld retries.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Work Execution.

### Card 4: Safety PLC independent

Non-negotiable.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Safety Eng; career-limiting to dismiss.

### Card 5: Wave vs stream

Cutoff batches vs WIP.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Planning.

### Card 6: Hot bin contention

Spread stow; shard; multi-loc picks.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Slotting + Inventory.

### Card 7: Short pick

PS + adjust; no ghost ship.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** FC Ops + Inventory.

### Card 8: FC cell

No cross-FC bin locks.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Network allocation separate.

### Card 9: Prime Day freeze

Config on; risky code off.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Game day IC.

### Card 10: ATP reservation

Leases + FC commit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Joint retail/FC.

### Card 11: Device NACK

Reassign; don't assume motion.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Fleet + WES.

### Card 12: Cartonization

Dims truth; measure damage.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Outbound.

### Card 13: Cycle count

Triggered; authority on adjusts.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Inventory integrity.

### Card 14: Deal-breaker

Eventually consistent bins; mute e-stop; ship without scan.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** L6 says these early.

### Card 15: Metrics

SLA miss, shorts, picks/hour, confirm p99, safety.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Wallboards before peak.

### Card 16: Sim before planner

Digital twin replay.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Planning science + eng.

---

## Scenario Runbooks

### R1 — Short-pick spike
Freeze affected ASIN ATP if severe; cycle count hot locations; check stow bugs; IC if promise risk.

### R2 — WiFi brownout zone
Reassign labor; enable limited degrade; fix AP; don't "guess completes".

### R3 — Pack clog
WIP cap picks; surge pack staff; divert sort path.

### R4 — Robot deadlock
Fleet replan; WES pause assignments to zone; safety clear.

### R5 — Carrier API outage
Queue manifests; print fallback labels if contract allows; communicate promise risk upward.

---

## Extended Rapid Q&A

**Q: Why scan location then item?**  
A: Prevent wrong-bin picks; foundational Amazon FC practice.

**Q: Can we skip stow direction?**  
A: Chaotic works with discipline; directed helps constraints.

**Q: How model kits/bundles?**  
A: Virtual BOM explode at allocation/pick.

**Q: Expiry lots?**  
A: FEFO rules in allocation + stow separation.

**Q: Returns processing inbound?**  
A: Separate grading workflow → sellable/refurb/destroy.

**Q: Why not CRUD qty field only?**  
A: Need event audit + idempotency.

**Q: Exactly-once Kafka to ledger?**  
A: Kafka helps deliver; ledger uniqueness still required.

**Q: Who sets ship_by?**  
A: Promise engine upstream; FC consumes.

**Q: Multi-item tote integrity?**  
A: Container contents ledger; scan associations.

**Q: First dashboard widget?**  
A: SLA risk + safety; then thruput.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Soft inventory from forecasts | Oversell |
| Central global bin DB | Latency/outage blast |
| CV-only without scans MVP | Accuracy not ready |
| Planner monolith mutating qty | Corruption |
| Unlimited WIP | Pack chaos |

---

## LLD Touch (optional)

Classes: `Location`, `InventoryLedger`, `InventoryEvent`, `Task`, `Wave`, `Assignee`, `Container`, `Shipment`, `DeviceAgent`, `SafetyInterlock`. Patterns: Event sourcing lite, Outbox, State machine, Strategy (stow scoring).

---

## 60-second Narrative

"We split **inventory ledger**, **work tasks**, **devices**, and **planning**. Every quantity change is an idempotent event with CAS—no negative ghosts. Waves respect carrier cutoffs; handhelds confirm with scans; pack verifies before ship. Safety PLCs are independent. Each FC is a cell. For Prime Day we scale partitions, freeze risk, and staff PS. Success is SLA hit rate, short-pick rate, confirm p99, and zero safety compromises."

---

## Extra Depth: Slotting Science

Offline optimize item-location affinity from affinity graphs; apply as stow suggestions; measure travel reduction; never hard-block FC if science job fails—fallback chaotic.

---

## Extra Depth: Heterogeneous FC Archetypes

Sortable smalls, non-sortable bulky, specialty (apparel), AMZL injection—share ledger/task primitives; specialize planner and devices. Avoid fake uniformity.

---

## Extra Depth: Observability

Wide events: task_id, location_id, item_id, associate_id hash, latency. Metrics: complete_rate, CAS_conflict, device_disconnect. Trace pick→pack. High cardinality item_id: careful aggregation.

---

## Extra Depth: Load Test / Game Day

Replay peak scan traces; inject device loss; canary planner on off-peak zone first; practice IC communications; verify ATP cancel paths.

---

## Extra Depth: Problem Solve Taxonomy

Damaged, missing, unscanable, distribution error, customer cancel mid-pick—each with state machine and inventory effects documented.

---

## Extra Depth: Shipping Manifest

Idempotent manifest posting; carrier acceptance async; shipment state machine separate from inventory (inventory already decremented at pick/pack per policy—**state when qty leaves sellable**: clarify pick vs ship; Amazon often decrements earlier with container accountability).

---

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT qty | inventory events + balances |
| Work | idempotent tasks |
| Plan | cutoff-aware waves |
| Safety | PLC > software |
| Scale | FC cells |
| Peak | freeze + partitions + PS |
| Kill | eventual bin qty; skip scans |

---

*End of Amazon Warehouse System design notes (Amazon SDE III prep).*
