# System Design: Airport Management System

> **Focus areas:** Flights · Gates · Stands · Baggage · Passengers · Resource allocation · Disruptions · Multi-airport cells
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Airport operations software (AODB-class): schedule, resources, turns, disruptions**

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

Goal: design an **airport management system**—manage flight schedules, gate/stand allocation, turnaround tasks, baggage milestones, passenger flow hooks, and disruption recovery for one airport scaled to many.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Airport ops resource + flight day-of-ops | Full airline network revenue management |
| Airside | Gates, stands, towing, turn tasks | ATC radar replacement |
| Baggage | Milestones / reclaim integration | Building every conveyor PLC |
| Amazon lens | Thruput, promise, ownership under failure | Pretty FIDS demo only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Flight schedule? | Seasonal + day-of updates from airlines/AFTN-like feeds | Flight ledger |
| F2 | Gates/stands? | Allocate/reallocate with constraints | Resource optimizer + rules |
| F3 | Turnaround? | Clean, fuel, catering, boarding windows | Task graph per turn |
| F4 | Baggage? | Load/offload milestones, transfer bags | Baggage events |
| F5 | FIDS/displays? | Public times, gates, claims | Publish plane |
| F6 | Disruptions? | Weather, delay cascade, diversions | Irregular ops (IROPS) |
| F7 | Passengers? | Counts, connections risk (hooks) | Not full DCS |
| F8 | Security/slots? | Slot compliance, curfew | Constraint engine |
| F9 | Multi-terminal? | Yes within airport cell | Zoning |
| F10 | Integrations? | Airlines, ground handlers, ATC times | Adapter ports |
| F11 | SLA? | On-time turn, miss-connection risk | Ops metrics |
| F12 | Audit? | Who moved gate when | Strong audit |

**MVP scope:**

1. Ingest flight schedule + updates idempotently.
2. Maintain flight state (planned/airborne/landed/at-gate/departed).
3. Gate/stand inventory with constraint-based assignment.
4. Turnaround task checklist with owners/times.
5. Publish FIDS feed from flight+gate truth.
6. Baggage milestone ingest (arrived claim, loaded).
7. Disruption mode: delay blast + reallocation workflow.
8. Ops wallboard: delays, gate conflicts, turn risk.

**Out of MVP:** full airline crew rostering, national airspace redesign, perfect ML taxi-time without data, active-active dual writers for same gate.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Schedule update apply | p99 < 2s to ops UI |
| N2 | Gate assign conflict detect | immediate on write |
| N3 | Durability | No silent loss of flight updates |
| N4 | Availability | Airport day-of-ops degrade modes |
| N5 | Consistency | Strong per airport resource locks |
| N6 | Audit | Every gate change explainable |
| N7 | Peak | Bank rushes 3–5× |
| N8 | Safety/compliance | Curfew/slot constraints enforced |

### 1.3 Cases

**Happy:** Schedule ingest → gate plan → arrival → turn tasks → boarding → pushback → FIDS accurate.
**Edges:** late inbound cascade; gate double-book; tow conflict; baggage storm; weather ground stop; diversion; display wrong gate; handler no-show; curfew breach risk.

| Case | Behavior |
|------|----------|
| Gate conflict | Reject or force with authority + audit |
| Inbound delay | Replan turns; notify downstream |
| Diversion | Create/alter flight; allocate resources |
| FIDS wrong | Republish from SoT; never edit display-only |
| Duplicate feed | Idempotent update keys |
| Curfew risk | Block assign / escalate |

### 1.4 Progressive scale

| Metric | Base (1 airport) | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Airports | 1 | 10 | 100 | 1,000 |
| Flights / day | 800 | 1,200 | 1,500 | 2,000 |
| Gate/stand resources | 120 | 150 | 200 | 250 |
| Schedule updates / day | 10K | 20K | 40K | 80K |
| Turn tasks / day | 5K | 8K | 12K | 20K |
| Baggage events / day | 100K | 200K | 400K | 800K |
| FIDS endpoints | 200 | 500 | 1K | 2K |
| Concurrent ops users | 100 | 300 | 500 | 800 |

**Jumps:** 10× = multi-airport platform; 100× = IROPS tooling + handler ecosystem; 1,000× = global airport SaaS cells, extreme weather seasons.

### 1.5 Scope repeat-back

> Per-airport operations system for flights, gates/stands, turns, baggage milestones, FIDS publish, and disruption recovery—scaled as airport cells—accuracy and conflict-safety over flashy optimization.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
800 flights/day; each ~20–100 updates ⇒ tens of thousands updates/day
Baggage events can dwarf flights (bags × scans)
Bank peak: many updates/minute
```

### 2.2 Storage

```text
Flight day rows small; history years retained
Resource timeline intervals critical
Baggage events high volume → hot/warm tiers
```

### 2.3 Latency budget

```text
Feed → validate → flight CAS → resource check → notify FIDS
Target ops visibility in seconds
```

### 2.4 Bottlenecks

(1) gate timeline conflicts (2) feed storms (3) IROPS replan quality (4) handler mobile connectivity (5) display fanout.

### 2.5 Cost / frugality

Wrong gate costs miss-connections and brand damage; optimize conflict correctness before ML taxi prediction.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Flight Ledger | Flight identity + times/state | Strong per flight |
| Resource Timeline | Gates/stands/tows intervals | Strong conflict-free |
| Turn Work | Handler tasks | Strong per task |
| Baggage Events | Milestones | Idempotent append |
| Publish / FIDS | Public projections | Eventually from SoT |

**Deal-breaker:** editing FIDS as source of truth instead of flight/resource ledger—displays are projections.

### 3.2 Components

1. **Flight Ingest Adapters** — airline/airport feeds
2. **Flight Service** — ledger + state machine
3. **Resource Manager** — gates/stands/bays timelines
4. **Allocation Engine** — rules + optimizer hints
5. **Turnaround Service** — task graphs
6. **Baggage Milestone Service** — events
7. **IROPS Controller** — disruption playbooks
8. **FIDS Publisher** — fanout displays/apps
9. **Notifications** — airline/handler alerts
10. **Ops UI / Wallboard** — conflicts, delays
11. **Reference Data** — aircraft types, terminal maps
12. **Audit Log** — immutable decisions

### 3.3 Core API (sketch)

```text
POST /v1/flights/updates {update_id, flight_key, fields...}  # idempotent
POST /v1/resources/allocate {flight_id, resource_id, interval, actor}
POST /v1/turns/{flight_id}/tasks/{task}/complete
POST /v1/baggage/events {event_id, bag_tag, type, ts}
GET /v1/fids/snapshot?terminal=
```

### 3.4 State machine

```text
FLIGHT: SCHEDULED → DEPARTED_OUT → AIRBORNE_IN → LANDED → AT_STAND → BOARDING → PUSHBACK → DEPARTED
              ↘ CANCELLED / DIVERTED / RETURN_TO_GATE
GATE_INTERVAL: HELD → ACTIVE → RELEASED | CONFLICT_BLOCKED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Optimizer vs rules | Rules+constraints first; optimizer advisory | Explainability |
| Auto-reassign gates | Suggest + human confirm on big moves | Ops trust |
| Baggage SoT | Handler system events; airport aggregates | Integration reality |
| Multi-airport | Hard cell isolation | Blast radius |
| Public times | Publish estimated with quality flags | Passenger trust |

---

## 4. Architecture Diagram

```text
[Airline Feeds] -> Ingest -> Flight Ledger -> Resource Manager <-> Allocation Engine
                              |                    |
                              v                    v
                         Turnaround Service   FIDS Publisher -> Displays
                              |
                         Baggage Events
                              v
                         IROPS Controller -> Ops Wallboard
```

### 4.1 Primary sequence

```text
Idempotent apply schedule update
Detect resource interval overlap
Allocate gate/stand with CAS on timeline
Generate turn tasks from aircraft/rotation template
On landing, start turn timers
Publish FIDS from ledger projection
On disruption, replan with audit
```

### 4.2 Isolation cell

```text
Each airport = cell for resources & day-of-ops
No cross-airport gate locks
Platform: identity, config templates, analytics
Connections across airports are airline problem; we expose risk hooks
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Gate intervals conflict-free unless override authority.
2. Flight updates idempotent on update_id.
3. FIDS never authoritative for ops decisions.
4. Every forced allocation audited.
5. Turn critical path visible; can't mark departed with required tasks open without override.
6. Curfew/slot constraints enforced in allocate path.
7. Baggage event deduped.
8. IROPS mode changes are explicit state.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Monolith AODB; PG timelines; one airport |
| 10× | Multi-airport SaaS cells; shared adapters |
| 100× | IROPS automation; handler apps; feed storm hardening |
| 1000× | Global portfolio; sim; weather season command |

### 5.3 Maintainability

- Resource constraints as data.
- Adapter contract tests per airline feed.
- Canary allocation rules per terminal.
- Replay feeds in sim.
- FIDS contract snapshot tests.

### 5.4 Progressive scale

**1×:** Single airport, manual gate plan, basic FIDS.
**10×:** Packaged airport deploy; central ref data.
**100×:** Bank-aware allocation; transfer bag risk; IROPS playbooks.
**1000×:** Portfolio ops; heterogeneous airport sizes; extreme chaos drills.

### 5.6 Resource timeline CAS

Model gate as interval tree / booking rows with exclusion constraints (aircraft wingspan, international hardstand, Schengen, etc.). Allocate with version CAS; detect tow-path conflicts as secondary resources.

### 5.7 Delay cascade

Inbound late → turn compression → outbound risk. Surface critical path; auto-suggest gate moves only within rules; humans confirm mass changes during IROPS.

### 5.8 FIDS projection

Materialize public view asynchronously from ledger. Poison message handling; monotonic gate display rules to reduce ping-pong unless forced.

### 5.9 Feed idempotency

Airlines retransmit. update_id / (flight_key, version, source) uniqueness. Last-write with source priority matrix.

### 5.10 Bank rush

Precompute allocations; freeze minor optimizers; staff IROPS; protect allocate API latency.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| FIDS as SoT | Ops lies |
| Soft gate double-book | Collisions/chaos |
| Silent auto mass reassign | Trust loss |
| Global multi-airport lock | Outage |
| Drop flight updates | SEV |
| Ignore curfew | Fines/safety |

---

## 6. Wrap-Up

### 6.1 Designed

Airport-cell AODB: flight ledger, conflict-free resources, turns, baggage milestones, FIDS projection, IROPS—scaled across airports.

### 6.2 Decisions to defend

1. Airport cell isolation
2. Conflict-free resource timelines
3. FIDS as projection
4. Idempotent feeds
5. Rules-first allocation
6. Audited overrides
7. Turn critical path
8. IROPS explicit mode

### 6.3 Risks

- Feed quality
- Handler adoption
- IROPS human overload
- Display fanout bugs
- Constraint misconfig

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope airport ops vs airline network |
| 5–15 | Flight ledger + feeds |
| 15–25 | Gates/resources conflicts |
| 25–35 | Turns/baggage/FIDS |
| 35–45 | IROPS + multi-airport scale |

### 6.5 Closer

> **Airport Management System**: airport cells, conflict-free gates, flight ledger SoT, FIDS projection, audited IROPS, progressive multi-airport scale.

---

## 7. Deeper / Related Interview Questions

### 7.1 Flights

**Q: What is flight_key?**
A: Airline + flight no + origin-date + operational suffix rules.

**Q: Codeshares?**
A: Operating flight primary; marketing as aliases.

**Q: Tow to remote?**
A: Stand change as resource move + tasks.

### 7.2 Resources

**Q: International gate constraints?**
A: Ref data flags; allocator rejects.

**Q: Remote hardstand + bus?**
A: Resource bundle assignment.

**Q: Optimizer objective?**
A: Minimize tows/miss-connect risk; constraints hard.

### 7.3 IROPS

**Q: Ground stop?**
A: Mode flag; hold outbound; communicate.

**Q: Mass reassign UX?**
A: Batch suggestions + confirm.

**Q: Who overrides curfew?**
A: Rare authority + audit + legal.

### 7.4 Baggage

**Q: Transfer hot bags?**
A: Milestone SLA alerts to handlers.

**Q: Claim carousel assign?**
A: Publish from flight+terminal rules.

### 7.5 Integrations

**Q: Airline DCS?**
A: Adapter; don't rewrite DCS.

**Q: ATC actual times?**
A: Ingest as authoritative actuals when present.

### 7.6 Traps

**Q: Build ATC**
A: Out of scope.

**Q: Eventually consistent gates**
A: Deal-breaker.

**Q: ML before conflict rules**
A: Wrong order.

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| On-time turn % | Ops |
| Gate conflict rate | Correctness |
| Update apply p99 | Freshness |
| FIDS accuracy samples | Passenger trust |
| Miss-connect risk flags | Quality |
| Override rate | Process health |
| Baggage milestone lag | Transfers |
| IROPS recovery time | Resilience |

### 7.8 Ownership

**Q: Who pages for gate double-book?**
A: Resource Manager oncall + Airport Ops IC.

**Q: Who pages for FIDS wrong gate?**
A: Publish pipeline; verify ledger first.

### 7.9 Progressive drill

**10×:** multi-airport package
**100×:** IROPS automation + feed hardening
**1,000×:** global portfolio command

---

## 8. Appendices

### 8.1 Schema sketches

```text
airports(airport_id)
flights(flight_id, airport_id, key, state, times_json, version)
flight_updates(update_id PK, flight_id, source, payload, ts)
resources(resource_id, type, constraints)
allocations(id, resource_id, flight_id, start_ts, end_ts, version)
turn_tasks(id, flight_id, type, state, due_ts)
baggage_events(event_id PK, bag_tag, flight_id, type, ts)
fids_snapshots(terminal, payload, ts)
audits(id, actor, action, ref, ts)
```

### 8.2 API checklist

- [ ] Idempotent flight update
- [ ] Allocate/release resource
- [ ] Turn task complete
- [ ] Baggage event
- [ ] FIDS snapshot
- [ ] IROPS mode
- [ ] Override allocate

### 8.3 Oncall checklist

- [ ] Gate conflict alerts
- [ ] Feed lag
- [ ] FIDS drift
- [ ] Turn breach risk
- [ ] IROPS mode
- [ ] Handler app errors
- [ ] Rollback allocation rules

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| AODB | Airport Operational Database |
| FIDS | Flight Information Display System |
| IROPS | Irregular Operations |
| Stand | Aircraft parking position |
| Turn | Arrival-to-departure ground time |
| Slot | Time permission |
| Cell | Airport isolation |

### 8.5 Deal-breaker one-liners

- Soft double-book gates
- FIDS as SoT
- Drop idempotency on feeds
- Cross-airport resource locks

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Flight ledger | AODB Platform |
| Resources | Airside Systems |
| Turns | Ground Ops Eng |
| Baggage | Baggage IT |
| FIDS | Passenger Info |
| IROPS | Airport Ops |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | PG+redis one airport |
| 10× | Cell per airport |
| 100× | Feed storm partitions |
| 1000× | Portfolio CC + sim |

### 8.8 Failure injection

1. Duplicate feed — idempotent.
2. Gate CAS conflict — retry/replan.
3. FIDS fanout down — queue; ops UI still true.
4. Handler offline — paper degrade checklist.
5. Bad constraint publish — rollback.
6. Weather ground stop — IROPS mode.

---

## Interview Traps

**Trap: Design airline RM**
Signal: Scope

**Trap: Ignore conflict-free intervals**
Signal: Fail

**Trap: Auto-move all gates silently**
Signal: Ops revolt

**Trap: Global DB all airports**
Signal: Blast radius

---

## Flash Cards

### Card 1: Flight ledger SoT

Displays project.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** AODB

### Card 2: Gate CAS

Conflict-free intervals.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Airside

### Card 3: Idempotent feeds

Retransmit safe.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Ops

### Card 4: IROPS mode

Explicit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** FIDS

### Card 5: Turn critical path

Visible blockers.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Baggage

### Card 6: FIDS monotonicity

Reduce ping-pong.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** IROPS

### Card 7: Curfew enforce

Hard constraint.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** AODB

### Card 8: Audit overrides

Money/safety adjacent.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Airside

### Card 9: Bank rush

Freeze risky optimizers.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Ops

### Card 10: Baggage dedupe

event_id.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** FIDS

### Card 11: Airport cell

Isolation.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Baggage

### Card 12: Adapter contracts

Per airline.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** IROPS

### Card 13: Diversion workflow

First-class.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** AODB

### Card 14: Deal-breaker

Double-book; FIDS SoT.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Airside

### Card 15: Metrics

Conflicts; FIDS accuracy.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Ops

### Card 16: Game day weather

Practice IROPS.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** FIDS

---

## Scenario Runbooks

### R1 — Gate conflict alert
Freeze auto-alloc; inspect timelines; fix; audit.

### R2 — Feed storm
Backpressure; prioritize actuals; lag banner.

### R3 — Wrong FIDS gate
Check ledger; republish; disable bad transformer.

### R4 — Ground stop
IROPS mode; hold pushbacks; communicate.

### R5 — Turn task collapse
Surge handlers; compress checklist carefully.

---

## Extended Rapid Q&A

**Q: Remote stand buses?**
A: Bundle resources.

**Q: Schengen vs non?**
A: Constraint flags.

**Q: Cargo flights?**
A: Same ledger different templates.

**Q: Noise curfew?**
A: Hard deny allocate.

**Q: Who sets TOBT?**
A: Airline/handler updates via adapters.

**Q: ML taxi times?**
A: After rules/data quality.

**Q: First widget?**
A: Conflicts + delay blast.

**Q: Multi-terminal bags?**
A: Milestones + transfer SLAs.

**Q: Why not CRUD gate field?**
A: Need intervals + history.

**Q: Codeshare display?**
A: Marketing fields on projection.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Excel as SoT | Not scalable/auditable |
| Eventual gate bookings | Collisions |
| Rebuild ATC | Wrong scope |
| One global airport DB | Outage blast |
| Display-only system | Ops useless |

---

## LLD Touch (optional)

Classes: `Flight`, `FlightUpdate`, `Resource`, `AllocationInterval`, `TurnTask`, `BaggageEvent`, `FidsProjection`, `IropsMode`, `AuditEntry`. Patterns: Idempotent ingest, CAS intervals, Projection, State machine, Strategy (allocation scoring).

---

## 60-second Narrative

"We treat each airport as a cell. Flight ledger is source of truth; gates are conflict-free timelines with CAS; FIDS is a projection. Turns and baggage milestones keep the ground machine honest. During IROPS we switch explicit modes, suggest reallocations, and audit overrides. Scale airport-by-airport with hardened feeds. Success is conflict-free resources, accurate public info, and fast disruption recovery."

---

## Extra Depth: TOBT/TSAT Hooks

Integrate target times; don't own ATC sequencing.

## Extra Depth: Constraint Catalog

Wingspan, jetbridge, customs, ADA—data not code.

## Extra Depth: Simulation

Replay bank + weather; test allocator.

## Extra Depth: Observability

Wide events flight_id/resource_id; careful cardinality.

## Extra Depth: Handler Mobile

Offline checklist sync with conflict rules.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How model tow tractors as resources?**
A: Secondary resource intervals; conflict with path windows.

**Q: What is a bank?**
A: Wave of banks of arrivals/departures; allocator peak.

**Q: Codeshare display vs ops flight?**
A: Ops uses operating flight_key; FIDS may show marketing numbers.

**Q: How prevent FIDS gate ping-pong?**
A: Monotonic publish rules + minimum dwell before change unless forced.

**Q: Deicing queue integration?**
A: Optional resource; turn critical path includes deice when winter mode.

**Q: Who can force override gate conflict?**
A: Named authority roles; dual control for high-risk; audit.

**Q: Cargo vs passenger flights same ledger?**
A: Yes; different turn templates.

**Q: How handle missing actual ON/IN times?**
A: Estimates flagged; quality metric.

**Q: Baggage system down?**
A: Ops continues flights; baggage milestones degrade; risk alerts up.

**Q: Slot coordination airport vs airline?**
A: Airport enforces local constraints; airline owns network slots.

**Q: Curfew with emergency medical inbound?**
A: Override authority + audit + regulator rules.

**Q: Multi-airport portfolio view?**
A: Read-only analytics across cells; no cross locks.

**Q: Why rules before ML allocator?**
A: Explainability and safety constraints first.

**Q: Ground handler app offline?**
A: Local checklist cache; sync with conflict PS.

**Q: SEV for wrong gate boarded passengers?**
A: Sev-1 passenger ops; joint airline+airport IC.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT | Flight ledger |
| Gates | CAS intervals |
| FIDS | Projection |
| Scale | Airport cells |
| Kill | Double-book; FIDS SoT |

---

*End of Airport Management System design notes (Amazon SDE III prep).*


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

