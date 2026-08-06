# System Design: Robo-Taxi Marketplace

> **Focus areas:** Rider request · Matching · Fleet state · Routing · Safety geofence · Pricing · Payments · Multi-city cells
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Practical Amazon-style ownership; explicit deal-breakers; reliability over cleverness
> **Interview theme:** Amazon SDE III / L6 — **Autonomous vehicle ride marketplace (dispatch + marketplace + safety boundaries)**

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

Goal: design a **robo-taxi marketplace**—riders request trips, the system matches autonomous vehicles (with remote assistance fallback), prices and pays, enforces geofences/safety, and operates city-by-city at progressive scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Marketplace + dispatch + trip lifecycle | Building the full AV stack / perception ML |
| Fleet | Vehicle availability, assignment, mission | OEM factory robotics |
| Safety | Geofence, ODD, remote assist hooks | Replacing vehicle safety driver brain |
| Amazon lens | Promise, ownership, cell isolation | Sci-fi demo without ops |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Request trip? | Pickup/dropoff, party size, accessibility | Trip intent API |
| F2 | Matching? | Nearest capable AV in ODD | Matcher + constraints |
| F3 | Pricing? | Upfront fare estimate + final | Pricing engine |
| F4 | Vehicle state? | Online, charging, cleaning, enroute | Fleet state service |
| F5 | Routing? | Pickup ETA + trip route from map | Routing port |
| F6 | Safety/ODD? | Geofence, weather hold, road closure | ODD gate |
| F7 | Remote assist? | Human teleops for stuck AV | Assist queue |
| F8 | Payments? | Preauth + capture on complete | Payments |
| F9 | Multi-stop? | Optional MVP later | Itinerary model |
| F10 | Cities? | Many metros; cell per city | City cells |
| F11 | SLA? | Pickup ETA accuracy; completion | Promise metrics |
| F12 | Incidents? | Emergency stop, contact, insurance workflow | Incident plane |

**MVP scope:**

1. Rider trip request with upfront estimate.
2. Fleet heartbeat + capability tags (seats, wheelchair).
3. Match AV under ODD constraints; assign mission.
4. Track enroute pickup → in-trip → complete.
5. Payment preauth/capture; receipts.
6. Geofence deny outside ODD.
7. Remote assist ticket when AV requests help.
8. City ops dashboard: utilization, ETAs, incidents.

**Out of MVP:** full multi-city empty-vehicle rebalancing ML perfection, airborne delivery, rider social features, active-active dual dispatch writers for same vehicle.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Match latency | p99 < 2–3s |
| N2 | Fleet state freshness | < 2–5s stale for assignment |
| N3 | Durability | No lost trip/payment records |
| N4 | Safety gating | Hard deny outside ODD; independent of matcher greed |
| N5 | Availability | City cell degrade; no global brownout |
| N6 | Audit | Assignment + remote assist explainable |
| N7 | Peak | Stadium/airport surge 5–20× |
| N8 | Consistency | Single-writer per vehicle mission |

### 1.3 Cases

**Happy:** Request → estimate → match AV → pickup → trip → dropoff → pay → rate.
**Edges:** no AV in ODD; weather hold; AV stuck; rider no-show; payment fail; double request; geofence edge; charging depletion mid-trip plan; remote assist overload; GPS jitter.

| Case | Behavior |
|------|----------|
| No supply | Queue or fail estimate; suggest wait/alternate |
| Weather ODD exit | Pause matching; safe pull-over missions |
| AV stuck | Remote assist; reassign if needed |
| Rider cancel | Cancel fee policy; free vehicle |
| Double request | Idempotency; one active trip |
| Payment fail | Retry / block future; complete trip policy explicit |

### 1.4 Progressive scale

| Metric | Base (1 city) | 10× | 100× | 1,000× |
|--------|--------|--------|--------|--------|
| Cities | 1 | 10 | 100 | 1,000 |
| AVs online | 200 | 2K | 20K | 200K |
| Trips / day | 5K | 50K | 500K | 5M |
| Peak match QPS | 5 | 50 | 500 | 5K |
| Heartbeats / s | 200 | 2K | 20K | 200K |
| Remote assist seats | 10 | 50 | 200 | 1K |
| Geofence polygons | 50 | 500 | 5K | 50K |
| Pricing updates / hour | 12 | 24 | 48 | 96 |

**Jumps:** 10× = multi-city platform; 100× = surge tooling + assist scale; 1,000× = global cells, heterogeneous AV OEMs, extreme event ops.

### 1.5 Scope repeat-back

> City-cell robo-taxi marketplace with trip lifecycle, constrained matching, fleet state, ODD/safety gates, payments, and remote assist—scaled across cities—never optimizing match rate over safety.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event math

```text
5K trips/day ≈ 0.06/s; peak 10×
Each trip: ~20–50 events (match, route, telematics summaries)
Heartbeats: 200 AV × 1 Hz = 200/s baseline city
```

### 2.2 Storage

```text
Trip ~5–20 KB; telemetry rollups separate
Hot: active trips + fleet state in memory/Redis
Cold: trip history + telemetry object store / TSDB
```

### 2.3 Latency budget (match)

```text
Auth → geo index candidates → ODD filter → score → lease vehicle → mission
50 + 100 + 50 + 50 + 100 + 50 ≈ ~400ms–2s p99 with map calls
```

### 2.4 Bottlenecks

(1) supply in ODD (2) heartbeat storm (3) assist staffing (4) map/routing deps (5) stadium geofence edges (6) single-writer vehicle contention.

### 2.5 Cost / frugality

Vehicle idle time and assist labor dominate; matcher quality matters more than fancy UI. Downsample telemetry.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Fleet State | Vehicle pose, mode, energy | Timely eventual; assignment uses leases |
| Marketplace Match | Score & assign | Strong lease per vehicle |
| Trip Ledger | Trip + fare + pay | Strong per trip |
| ODD / Safety Gate | Allow/deny missions | Strong rules; independent |
| Remote Assist | Human help sessions | Strong per session |

**Deal-breaker:** letting matcher override ODD/safety denials for utilization—safety gate is non-bypassable.

### 3.2 Components

1. **Trip Service** — request, lifecycle, cancel
2. **Pricing Service** — estimates, surge, final fare
3. **Matcher / Dispatcher** — candidate + lease assign
4. **Fleet State Service** — heartbeats, modes
5. **ODD / Geofence Service** — polygon + weather gates
6. **Routing Adapter** — ETA/path
7. **Mission Agent** — commands to vehicle gateway
8. **Remote Assist Platform** — queue + session
9. **Payments** — preauth/capture
10. **Incident Service** — emergency workflows
11. **City Ops Console** — utilization, holds
12. **OEM Vehicle Gateway** — normalize AV vendors

### 3.3 Core API (sketch)

```text
POST /v1/trips
  {idempotency_key, rider_id, pickup, dropoff, constraints}
→ {trip_id, estimate, eta_pickup}
POST /v1/fleet/heartbeat  {vehicle_id, pose, energy, mode, ts}
POST /v1/trips/{id}/assign  internal: lease vehicle
POST /v1/assist/sessions  {vehicle_id, reason}
```

### 3.4 State machine

```text
TRIP: REQUESTED → MATCHED → ENROUTE_PICKUP → WAITING → IN_TRIP → COMPLETED
            ↘ CANCELLED / FAILED_NO_SUPPLY
            ↘ ASSIST_PAUSED → resumed/reassigned
VEHICLE: OFFLINE → ONLINE → ASSIGNED → ENROUTE → IN_TRIP → CLEANING/CHARGING
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Batch vs stream match | Continuous matching with leases | Low wait |
| Upfront vs metered fare | Upfront with tolerance band | Rider trust |
| City cell DB | Shard by city_id | Blast radius |
| Telemetry volume | Edge aggregate + sample | Cost |
| Reassign mid-trip | Rare; strict policy | Safety/UX |

---

## 4. Architecture Diagram

```text
[Rider App] -> Trip API -> Pricing -> Matcher -> Fleet State
                                   |           ^
                                   v           | heartbeats
                              ODD Gate ----deny/allow
                                   v
                            Mission Gateway -> AV OEM
                                   v
                         Remote Assist  |  Payments
                                   v
                            Incident / Ops Console
```

### 4.1 Primary sequence

```text
Validate pickup/dropoff inside ODD
Price estimate
Matcher queries geo index + constraints
Lease vehicle (TTL); write assignment
Send mission; track ETA
Rider boards (confirm) → IN_TRIP
Complete → capture payment → release vehicle
```

### 4.2 Isolation cell

```text
Each city = matching/fleet cell
No cross-city vehicle locks
National: identity, payments, config templates
Empty reposition may be intra-city only in MVP
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. At most one active mission lease per vehicle.
2. ODD deny wins over matcher score.
3. Trip state transitions validated and audited.
4. Payment preauth before dispatch when policy requires.
5. Assist sessions recorded with reason and operator.
6. Idempotent trip create.
7. Cancel releases lease with fencing token.
8. Emergency stop path does not wait on marketplace DB.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | One city modular system; Redis fleet; PG trips |
| 10× | Multi-city cells; shared identity/pay |
| 100× | Sharded geo indexes; assist pools; surge platform |
| 1000× | OEM heterogeneity; global ops; event command centers |

### 5.3 Maintainability

- ODD polygons as versioned data.
- Matcher scoring plugins with canary city.
- OEM gateway adapters behind interface.
- Simulation replay for matcher changes.
- Contract tests for mission commands.

### 5.4 Progressive scale

**1×:** One city, simple nearest-AV match, manual assist.
**10×:** Packaged city deploy; central rider accounts.
**100×:** Surge pricing, predictive positioning, assist tiers.
**1000×:** Global brand, multi-OEM, extreme event playbooks.

### 5.6 Vehicle lease & fencing

Assignment uses lease_id + fencing token so stale matcher cannot steal vehicle after expiry. Heartbeat must renew lease. Lost heartbeat → reclaim with grace.

### 5.7 ODD & weather gates

Geofence service evaluates pickup, path corridor, dropoff. Weather provider can flip city mode to HOLD. Matcher never sees denied candidates.

### 5.8 Remote assist scale

Assist is scarce. Prioritize stuck blocking lanes over cosmetic. Queue SLAs; if assist saturated, stop new dispatches in zone—utilization second to safety.

### 5.9 Heartbeat storm

At 200K vehicles, 1 Hz raw is huge. Edge aggregate; send deltas; city partition consumers; backpressure without marking fleet ghost-online.

### 5.10 Stadium surge

Pre-position; geofence pickup lots; batch matching waves; dynamic meeting points; communicate walking ETAs honestly.

### 5.11 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Bypass ODD for utilization | Safety SEV |
| Two matchers assign same AV | Split-brain collision risk |
| Marketplace owns e-stop | Wrong layer |
| Global lock all cities | Outage blast |
| Infinite telemetry archive hot | Cost death |
| Silent reassign with rider in car | Trust/safety |

---

## 6. Wrap-Up

### 6.1 Designed

City-cell robo-taxi marketplace: trips, pricing, leased matching, fleet state, ODD gates, missions, assist, payments—safety non-negotiable.

### 6.2 Decisions to defend

1. City cell isolation
2. Vehicle single-writer leases
3. Non-bypassable ODD gate
4. Planes split marketplace vs safety vs assist
5. Upfront fare with audit
6. OEM gateway abstraction
7. Assist scarcity policies
8. Idempotent trips + payment

### 6.3 Risks

- Heartbeat freshness
- Assist staffing
- Map dependency
- ODD edge cases
- OEM API variance

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope marketplace vs AV stack |
| 5–15 | Trip + fleet + lease assign |
| 15–25 | ODD/safety + assist |
| 25–35 | Pricing/pay + surge |
| 35–45 | Multi-city scale + incidents |

### 6.5 Closer

> **Robo-Taxi Marketplace**: city cells, leased single-writer vehicles, ODD over utilization, assist scarcity honesty, progressive fleet scale, clear incident ownership.

---

## 7. Deeper / Related Interview Questions

### 7.1 Matching

**Q: Score function?**
A: ETA, energy, capability match, idle fairness—subject to hard constraints.

**Q: Pool vs nearest?**
A: Hybrid: k-nearest then score.

**Q: Deadheading cost?**
A: Include empty travel in score.

**Q: Fairness to waiting riders?**
A: Wait-time weight; starvation caps.

### 7.2 Safety

**Q: Who can override geofence?**
A: Not matcher; controlled ops with audit in emergencies only.

**Q: Rider opens door into bike lane?**
A: Vehicle/ops policy; incident workflow.

**Q: Connectivity loss mid-trip?**
A: On-vehicle safe stop; assist; trip state ASSIST_PAUSED.

### 7.3 Payments

**Q: No-show fee?**
A: Policy timed wait; capture partial.

**Q: Dispute damage?**
A: Incident + claims system separate.

**Q: Surge transparency?**
A: Show multiplier in estimate.

### 7.4 Fleet

**Q: Charging policy?**
A: Energy threshold removes from match; charger reservation optional.

**Q: Cleaning turn?**
A: Mode CLEANING after messy trip flag.

**Q: Multi-OEM pose formats?**
A: Normalize in gateway.

### 7.5 Scale

**Q: Shard key?**
A: city_id then geohash for fleet index.

**Q: Cross-city trip?**
A: Out of ODD MVP; airport cells special.

**Q: Canary matcher?**
A: Percent traffic in one city zone.

### 7.6 Traps

**Q: Design full perception stack?**
A: Out of scope.

**Q: Eventually consistent double assign OK?**
A: Deal-breaker.

**Q: Kafka as vehicle lock?**
A: Need fencing lease store.

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| Pickup ETA error | Promise |
| Match p99 | UX |
| Utilization % | Economics |
| Assist queue wait | Safety ops |
| ODD deny rate | Coverage honesty |
| Trip completion % | Reliability |
| Heartbeat stale % | Fleet health |
| Incident rate | Safety |

### 7.8 Ownership

**Q: Who pages for double-assign?**
A: Matcher/Fleet IC immediately.

**Q: Who pages for assist saturation?**
A: City ops + Assist platform; pause zone matching.

### 7.9 Progressive drill

**10×:** multi-city package
**100×:** surge + assist pools + shard indexes
**1,000×:** global OEM heterogeneity + event CC

---

## 8. Appendices

### 8.1 Schema sketches

```text
cities(city_id, odd_version)
vehicles(vehicle_id, city_id, oem, capabilities)
fleet_state(vehicle_id, pose, energy, mode, lease_id, version, ts)
trips(trip_id, city_id, rider_id, state, fare, idem_key UNIQUE)
assignments(trip_id, vehicle_id, lease_id, fencing_token)
geofences(id, city_id, polygon, rules)
assist_sessions(id, vehicle_id, operator, state)
payments(intent_id, trip_id, state)
incidents(id, trip_id, type, state)
```

### 8.2 API checklist

- [ ] Trip create idempotent
- [ ] Heartbeat ingest
- [ ] Assign/lease
- [ ] ODD check
- [ ] Assist open/close
- [ ] Pay capture
- [ ] Cancel/release

### 8.3 Oncall checklist

- [ ] Stale heartbeat spike
- [ ] Match latency
- [ ] Assist queue
- [ ] ODD hold mode
- [ ] Payment fail rate
- [ ] Incident open
- [ ] Rollback matcher

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| ODD | Operational Design Domain |
| Lease | Exclusive temporary vehicle assignment |
| Fencing token | Prevents stale assign |
| Deadhead | Empty travel |
| Assist | Remote human help |
| Cell | City isolation |

### 8.5 Deal-breaker one-liners

- Matcher bypasses ODD
- Two active leases one vehicle
- Software mute vehicle e-stop
- Global multi-city lock

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Matcher | Marketplace Dispatch |
| Fleet state | Fleet Platform |
| ODD | Safety Eng |
| Assist | Teleops |
| Trips/pay | Trip + Payments |
| Incidents | Safety Ops |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | PG+Redis one city |
| 10× | Cell per city |
| 100× | Geo index shards, assist tiers |
| 1000× | Multi-OEM gateways, global CC |

### 8.8 Failure injection

1. Duplicate assign — fencing rejects.
2. Heartbeat storm — sample + shed.
3. Map API down — cached routes / pause.
4. Assist full — zone HOLD.
5. Payment timeout — reconcile.
6. Bad geofence publish — rollback version.

---

## Interview Traps

**Trap: Build SLAM in interview**
Signal: Scope control

**Trap: Ignore assist scarcity**
Signal: Unsafe ops model

**Trap: Global ACID fleet**
Signal: Won't scale

**Trap: Optimize utilization over ODD**
Signal: Fail signal

---

## Flash Cards

### Card 1: Vehicle lease

Single-writer fencing token.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Dispatch

### Card 2: ODD gate

Non-bypassable.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Safety

### Card 3: City cell

No cross-city locks.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Fleet

### Card 4: Heartbeat freshness

Stale ⇒ reclaim.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Teleops

### Card 5: Assist scarcity

Pause zone before unsafe.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Payments

### Card 6: Upfront fare

Trust + audit.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** City Ops

### Card 7: Stadium surge

Meeting points + honesty.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Dispatch

### Card 8: OEM gateway

Normalize vendors.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Safety

### Card 9: Cancel release

Lease free with token.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Fleet

### Card 10: Incident plane

Separate from matcher.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Teleops

### Card 11: Telemetry cost

Aggregate/sample.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Payments

### Card 12: Canary matcher

One zone first.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** City Ops

### Card 13: Weather HOLD

Mode flip citywide.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Dispatch

### Card 14: Deal-breaker

Double assign; bypass ODD.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Safety

### Card 15: Metrics

ETA error; assist wait; stale %.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Fleet

### Card 16: Game day

Pre-position; freeze risky.

**Follow-ups:** 10× break? Pager? Fallback? Metric?
**Ownership:** Teleops

---

## Scenario Runbooks

### R1 — Double-assign suspected
Freeze matcher; inspect leases; fence revoke; page Safety.

### R2 — Assist saturation
HOLD new trips in zone; pull AVs to safe idle; surge staff.

### R3 — Weather ODD exit
City HOLD; complete in-progress carefully; message riders.

### R4 — Payment outage
Policy: finish trips; queue capture; block new if required.

### R5 — OEM gateway flap
Mark vehicles unverified offline; don't ghost assign.

---

## Extended Rapid Q&A

**Q: Why lease TTL?**
A: Recover from matcher crash.

**Q: Rider multi-stop?**
A: Itinerary later; MVP single drop.

**Q: Shared rides?**
A: Different product; constraints explode.

**Q: Airport queues?**
A: Special geofence + staging lots.

**Q: Who computes route?**
A: Routing vendor/port; vehicle may replan locally.

**Q: Cleanliness?**
A: Rider report → CLEANING mode.

**Q: Lost item?**
A: Ops workflow + vehicle hold.

**Q: Pricing ML?**
A: After rules/surge basics.

**Q: First widget?**
A: Active incidents + stale fleet %.

**Q: Why city cell?**
A: Blast radius + regulations.

---

## Alternatives to Kill

| Alt | Why kill |
|-----|----------|
| Central global matcher locking all AVs | Latency/outage |
| No ODD service | Unsafe |
| Assign without lease | Double dispatch |
| Store all lidar hot | Cost |
| Marketplace e-stop | Wrong layer |

---

## LLD Touch (optional)

Classes: `Trip`, `Vehicle`, `FleetState`, `Lease`, `Geofence`, `Mission`, `AssistSession`, `FareQuote`, `PaymentIntent`, `Incident`. Patterns: Lease/fencing, State machine, Strategy (scoring), Ports (OEM, routing, pay), Circuit breaker (deps).

---

## 60-second Narrative

"We run marketplace matching inside city cells with single-writer vehicle leases. ODD/safety gates are non-bypassable. Trips and payments are durable and idempotent. Remote assist is a scarce safety resource—we pause zones before we pretend. Scale by cities, shard geo indexes, normalize OEMs, and practice stadium surges. Success is safe completed trips, honest ETAs, and zero double-assigns."

---

## Extra Depth: Empty Repositioning

Optional optimizer suggests deadheads; never violates ODD; canary before citywide.

## Extra Depth: Regulatory Modes

City configs for data retention, audio recording, incident reporting SLAs.

## Extra Depth: Simulation

Replay heartbeats + demand; stress matcher; regress double-assign.

## Extra Depth: Observability

Wide events trip_id/vehicle_id; cardinality controls on pose.

## Extra Depth: Partner Airports

Staging loops; curb API integration; separate promise SLOs.

---


---

## Additional Interview Q&A (40+ bank)

**Q: How do you fence a stale matcher assign?**
A: lease_id + fencing token; vehicle rejects lower epoch.

**Q: Accessibility wheelchair AVs?**
A: Capability tag hard filter before score.

**Q: Airport staging loop design?**
A: Special geofence + queue spots; human traffic marshals ops mode.

**Q: How price waiting time?**
A: Policy in fare quote; show in estimate breakdown.

**Q: Can rider change dropoff mid-trip?**
A: Allowed if new route still in ODD; reprice policy explicit.

**Q: Vehicle OEM sends duplicate heartbeats?**
A: Idempotent last-write per ts; monotonic merge rules.

**Q: What if map says road closed after assign?**
A: Reroute; if impossible, cancel with communication + reassign.

**Q: Shared rider identity across cities?**
A: Global identity; city cells for fleet.

**Q: How train matcher without production risk?**
A: Sim + shadow scoring + canary zone.

**Q: Insurance incident packet?**
A: Incident service bundles telemetry summaries + trip trail.

**Q: Why not optimize only utilization?**
A: Safety/ODD and ETA honesty dominate; dead utilization is secondary.

**Q: Remote assist recording retention?**
A: Policy by city regulation; encrypt; access audited.

**Q: Low energy mid-trip?**
A: Mission abort to charger/safe stop; replace AV.

**Q: Surge ethics messaging?**
A: Show multiplier; cap extremes; never silent.

**Q: Who owns stadium event playbook?**
A: City Ops IC with Marketplace + Fleet.

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| SoT trip | Trip ledger |
| Assign | Fenced lease |
| Safety | ODD > match |
| Scale | City cells |
| Kill | Double assign; bypass ODD |

---

*End of Robo-Taxi Marketplace design notes (Amazon SDE III prep).*


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

