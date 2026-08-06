# System Design: Delivery Route Optimization (Amazon Logistics)

> **Focus areas:** VRP / TSP variants · Time windows · Geo sharding · Real-time reopt · Map ETAs · Driver UX · Constraints · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Serviceable routes under time; deal-breaker: nightly exact VRP only with no recovery  
> **Interview theme:** Amazon SDE III / L6 — **Last-mile / middle-mile route optimization**

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

Goal: design a system that **builds and updates delivery routes** for drivers/couriers—sequencing stops under capacity, time windows, skills, SLAs—with continuous recovery as reality changes.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Sequence & assign stops to routes | Truck 3D loading (sibling) |
| Horizon | Wave + real-time reopt | Pure marketing ETA site |
| Output | Route plan + nav handoff | Warehouse pick path only |
| Success | On-time delivery + cost/km | Perfect NP-hard optimum |
| Amazon lens | Customer promise, ownership, frugality | Academic OR paper |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Entities? | Stops, vehicles/drivers, depots, routes | Clear model |
| F2 | Constraints? | Capacity, time windows, skills, max hours | Feasibility engine |
| F3 | Objective? | Min cost/time + max on-time + balance | Weighted + SLAs first |
| F4 | When plan? | Night/wave batch + intraday reopt | Dual cadence |
| F5 | Dynamic? | Traffic, new stops, returns, failures | Event-driven reopt |
| F6 | Maps? | Distance/ETA matrix | Provider + cache |
| F7 | Locked stops? | In-progress stop sticky | Partial freeze |
| F8 | Manual edit? | Dispatcher moves stops | Audited |
| F9 | Explain? | Why stop on route | Reasons |
| F10 | Multi-depot? | Yes at scale | Shard by geo |
| F11 | SLAs? | Prime windows / same-day | Hard/soft windows |
| F12 | Nav? | Export to driver app | Sequence + ETA |

**MVP:** For a station, assign stops to drivers and order stops; respect capacity/time windows; reoptimize on exceptions; publish to driver app.  
**Out:** Global single solve for a country; autonomous robot fleet control; truck loading 3D.

### 1.2 NFRs

| NFR | Target |
|-----|--------|
| Batch solve | Minutes per station wave |
| Reopt latency | Seconds–low minutes for local neighborhood |
| Feasibility | No published route violates hard constraints |
| Availability | Degrade to greedy nearest-neighbor + time check |
| Scale | Millions stops/day via geo shards |

### 1.3 Cases

Happy: wave plan → load van → execute → complete.  
Edges: traffic jam; customer not home; stop add-on; vehicle breakdown; inaccessible address; time window conflict; dispatcher override; map matrix stale; storm mass reopt.

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Stops/day | 5M | 50M | 500M | 5B |
| Stations | 1K | 10K | 100K | 1M |
| Jump | Station solvers | Region hierarchy | Continuous local search fleet | Learned proposers + edge reopt |

### 1.5 Repeat-back

“Geo-sharded VRP with batch + real-time reoptimization, hard windows first, greedy fallback—service before theoretical optimum.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Notes |
|-------|-------|
| Batch builds | Per station per wave |
| Matrix queries | O(n²) naive—must cluster/approximate |
| Reopt events | Per exception / traffic tick sampled |
| Driver location | Sampled telemetry |

### 2.2 Matrix math trap

```text
200 stops → 40k pairwise ETAs
If 50ms each naive = disaster
→ Cache tiles, contract hierarchies, cluster neighborhoods, warm matrices
```

### 2.3 Compute

```text
1K stations × 60s solve = 60K CPU-s per wave
Parallelize by station; cap stop count per route solve via clustering
```

### 2.4 Latency budgets

| Mode | Budget |
|------|--------|
| Wave solve | 1–10 min/station |
| Local reopt (± few stops) | < 5–30s |
| Driver sequence fetch | < 200ms |

### 2.5 Bottlenecks

ETA matrix; storm reopt thundering herd; overconstrained windows; dispatcher thrash.

---

## 3. High-Level Design

### 3.1 Abstractions

| Abstraction | Meaning |
|-------------|---------|
| `Stop` | Delivery/pickup with window, service time, size |
| `Vehicle` | Capacity, skills, shift |
| `Route` | Ordered stops for vehicle |
| `Plan` | Set of routes for station/wave |
| `Clusterer` | Geo/time partition before VRP |
| `Solver` | Heuristic VRP engine |
| `ReoptManager` | Event-triggered local search |
| `ETAService` | Distances/times |

### 3.2 Pipeline

```text
Stops arrive → Cluster(station, zones)
  → Build cost matrix (approx)
  → Seed routes (sweep/parallel insertion)
  → Improve (2-opt, relocate, exchange) within budget
  → Validate hard constraints
  → Publish plan_vN
Events → Localized reopt → patch routes → notify drivers
```

### 3.3 Algorithm strategy

1. Cluster to bound problem size.  
2. Construction heuristic.  
3. Local search with time box.  
4. Optional ALNS / genetic at batch only.  
5. Always **feasibility validator**.  
6. Greedy fallback.

### 3.4 Objective

```text
min  w1*drive_time + w2*lateness + w3*unassigned_penalty + w4*unfairness
s.t. capacity, hard windows, skills, max route duration
```

### 3.5 Trade-offs

| Choice | Why |
|--------|-----|
| Cluster then solve | Tractability |
| Local reopt not full resolve | Speed + driver UX stability |
| Soft vs hard windows | Promise hierarchy |
| Cache ETAs | Cost + latency |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Order/Stop Ingest] --> [Station Planner]
                            |
            +---------------+---------------+
            v               v               v
       Clusterer       ETA/Matrix        Solver Pool
            \               |               /
             +------+-------+------+------+
                    v
              Plan Service (versions)
                    |
        +-----------+-----------+
        v                       v
  Driver App / Nav         Dispatcher Tools
        |
   Location/Events ------> Reopt Manager
```

### 4.2 Sequence: wave

```text
Scheduler -> Planner: Build(station, wave)
Planner -> Cluster -> Matrix -> Solver
Solver -> PlanService: plan_v1
PlanService -> Drivers: sync routes
```

### 4.3 Sequence: exception reopt

```text
Driver -> Event: access_problem(stop)
Reopt -> freeze completed prefix
Reopt -> local search neighborhood
Reopt -> publish plan_v2 diff
Driver -> receives updated tail
```

### 4.4 Sharding

Primary shard: `station_id` / geo cell. Avoid continent-wide single VRP.

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Published routes pass hard constraints.  
2. Completed stops never reshuffled.  
3. Plan versions monotonic; drivers pin version.  
4. Unassigned stops visible (not silent drop).  
5. Reopt respects service-in-progress freeze.

### 5.2 Scalability

- Station shards; zone subclusters.  
- Matrix cache with traffic epochs.  
- Reopt coalescing: debounce events 5–15s.  
- Storm mode: prioritize SLA-critical reopts.

### 5.3 Maintainability

- Constraint plugins.  
- Golden stations fixtures.  
- Shadow scoring new heuristics.

### 5.4 Time windows

Hard: must; Soft: penalty. Amazon Prime windows often hard for promise. Service time buffers included.

### 5.5 Driver UX stability

Minimize stop churn; prefer relocating unstarted stops; score churn penalty in reopt.

### 5.6 Progressive scale

| Jump | Change |
|------|--------|
| 10× | More solver workers; better caches |
| 100× | Hierarchical zones; continuous optimization service |
| 1,000× | Learned cluster/seed; on-device micro-reopt |

### 5.7 Deal-breakers

| Deal-breaker | Why |
|--------------|-----|
| Exact VRP nightly only | No recovery |
| O(n²) live matrix no cache | Melts |
| Global single solve | Impossible scale |
| Silent unassigned | Broken promise |

---

## 6. Wrap-Up

### 6.1 Decisions

Geo/station shard; cluster→construct→improve; batch+reopt; freeze prefix; ETA cache; churn-aware; greedy fallback.

### 6.2 Risks

Map bias; overconstrained density; dispatcher fights solver; reopt oscillation; labor rules mis-modeled.

### 6.3 45-minute plan

Scope VRP vs loading → constraints → HLD → algorithms/reopt → scale/maps → traps.

### 6.4 Closer

> **Delivery Route Optimization**: sharded VRP, time-bounded heuristics, real-time local reopt with frozen prefixes, ETA caches, explicit unassigned—on-time service over paper optimality.

---

## 7. Deeper / Related Interview Questions

**Q1. TSP vs VRP?**  
**A:** TSP one tour; VRP multi-vehicle + capacities—we need VRP.

**Q2. How bound n?**  
**A:** Cluster by zone/time; limit stops per solve.

**Q3. Traffic?**  
**A:** ETA epochs; trigger reopt on major deltas.

**Q4. Pickup+delivery pairs?**  
**A:** Precedence constraints; keep same route.

**Q5. Returns / attempt-again?**  
**A:** New stop or reinsert with window.

**Q6. Oscillation reopt?**  
**A:** Damping, churn penalty, min interval.

**Q7. Who pages missed SLAs mass?**  
**A:** Routing + Station ops joint; define SEV.

**Q8. ML for route?**  
**A:** Sequence models as proposers; still validate constraints.

**Q9. Vs fill-truck doc?**  
**A:** Loading vs sequencing stops.

**Q10. Trap: Dijkstra per pair online?**  
**A:** Precompute/cache/hierarchy.

---

## 8. Appendices

### 8.1 Schema

```text
Stop(id, lat, lng, window, service_s, size, skills, sla_class)
Vehicle(id, cap, shift, skills, station_id)
Route(id, vehicle_id, plan_version, stops[])
Plan(id, station_id, wave, version, status)
Unassigned(stop_id, reason)
ReoptEvent(id, type, payload, ts)
```

### 8.2 Pseudocode

```text
function reopt(route, events):
  prefix = freezeCompleted(route)
  tail = route.stops[prefix:]
  neigh = expandNeighborhood(tail, nearbyRoutes)
  best = localSearch(neigh, budget=15s)
  assert validate(best)
  return publishDiff(best)
```

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| VRP | Vehicle Routing Problem |
| Time window | Arrive between [a,b] |
| Reopt | Re-optimize after change |
| Churn | Stop order changes |
| Matrix | Pairwise ETA table |

### 8.4 Progressive checklist

10× workers/cache; 100× hierarchy; 1,000× learned+edge.

### 8.5 Reliability tests

1. Solver timeout → greedy feasible.  
2. Reopt cannot move completed stop.  
3. Hard window violation rejected.  
4. Mass events coalesce.

### 8.6 60s closer

> We shard by station, cluster stops, build cached ETA matrices, construct and improve routes under time budgets, publish versioned plans, and run churn-aware local reopt on exceptions with frozen prefixes—unassigned stops are explicit.

---

## Deep Technical Notes — Delivery Route Optimization

### Clustering

Geohash + time window similarity; target 50–150 stops per micro-problem; merge thin clusters.

### Construction heuristics

Sweep algorithm; parallel insertion by cheapest feasible insert; Clarke-Wright savings for mid-size.

### Improvement

2-opt intra-route; relocate inter-route; cross-exchange; ruin-and-recreate bounded.

### ETA cache key

`(from_tile, to_tile, departure_bucket, profile)` with TTL; invalidate on traffic epoch.

### Service times

Include parking/walking uncertainty by area archetype (apartment vs suburban).

### Locked vs flexible

`IN_SERVICE` locked; `EN_ROUTE_NEXT` soft-locked; future flexible.

### Dispatcher tools

Drag-drop with live validate; show delta drive time & risk.

## Interview Cards — Delivery Route Optimization

### Card 1: Why not exact solver?

NP-hard; use heuristics + budget; validate.

### Card 2: Matrix explosion?

Tiles, caches, clusters—not all-pairs live.

### Card 3: Reopt scope?

Local neighborhood; freeze prefix; churn penalty.

### Card 4: Hard windows?

Feasibility first; unassigned if needed.

### Card 5: Shard key?

Station/geo cell.

### Card 6: Fallback?

Nearest feasible insertion / NN + validate.

### Card 7: ML role?

Propose; never skip constraints.

### Card 8: Deal-breaker?

Nightly-only exact; silent drops; global solve.

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | VRP scope |
| 5–12 | Matrix math + scale |
| 12–22 | HLD |
| 22–35 | Heuristics + reopt |
| 35–45 | UX churn, traps |

## 10. Operability

### Golden signals

On-time %, unassigned count, solve time, reopt latency, churn/stop, ETA error, driver adherence.

### Rollback ladder

Revert heuristic weights → greedy mode → freeze auto-reopt → manual dispatch.

### Kill switches

Disable inter-route moves; disable traffic reopt; lock plans; isolate station.

### Security/privacy

Driver location ACL; customer address minimization in logs; partner DSP boundaries.

### Cost worksheet

```text
Maps ETA $ + CPU solvers
Lever: tile cache hit rate; cluster size tuning
+1% on-time may dwarf CPU cost
```

### Cross-team deps

Stops ingest, Maps, Driver app, Station ops, Promise/SLA, Fill-truck (load), Notify.

---

## More Interview Q&A — Delivery Route Optimization

**Q1. Capacity in volume or weight?**  
**A:** Both; vehicle profile.

**Q2. Lunch breaks / labor?**  
**A:** Shift constraints as time blocks.

**Q3. Multi-depot?**  
**A:** Assign stop→depot first; then route.

**Q4. Bike vs van?**  
**A:** Skills + speed profile + capacity.

**Q5. Customer GPS noise?**  
**A:** Geocode confidence; photo/pin; wide service time.

**Q6. Same building many stops?**  
**A:** Cluster service; elevator models.

**Q7. Predictive densification?**  
**A:** Demand forecast seeds clusters—not hard assign early.

**Q8. Offline driver?**  
**A:** Cached route tail; sync on reconnect.

**Q9. How to A/B routing?**  
**A:** Station canaries; guard on-time & hours.

**Q10. Broken promise SEV?**  
**A:** Unassigned/late critical; customer messaging path.

**Q11. 2-opt enough?**  
**A:** Baseline; add relocate for VRP.

**Q12. Stochastic windows?**  
**A:** Buffers; chance constraints light version.

**Q13. Electric van range?**  
**A:** Energy constraint plugin.

**Q14. Middle-mile vs last-mile?**  
**A:** Same engine different profiles/frequencies.

**Q15. Difference vs food dispatch?**  
**A:** Food: continuous matching; this: planned routes denser parcel.

**Q16. First unit test?**  
**A:** Validator rejects capacity breach.

---

## Deep Technical Addenda

### Debounce reopt

```text
onEvent: buffer[station].add(e)
after quiet 10s or maxWait 30s: solveLocal(buffer)
```

### Plan diff protocol

Send only changed tails + checksum; driver merges if version+1.

### Unassigned reasons

`NO_CAPACITY`, `WINDOW`, `SKILL`, `MAX_HOURS`, `ISOLATED_GEO`, `SCORE`.

### Warm start

Seed from yesterday’s similar wave; improve—faster than cold.

### Traffic epoch

Bucket day into epochs; matrices versioned; major delta triggers selective reopt.

## Tradeoff Matrices — Delivery Route Optimization

### Stability vs optimality

| Choice | On-time | Churn | Use |
|--------|---------|-------|-----|
| Aggressive reopt | Potentially better | High | Storms only |
| Damped reopt | Good | Low | **Default** |
| Frozen after start | Simple | Missed saves | Sparse areas |

### Matrix fidelity

| Choice | Cost | Quality |
|--------|------|---------|
| Live OSRM all pairs | Huge | High |
| Tile cache + hierarchy | Low | Good | **Prefer** |
| Haversine | Tiny | Poor | Degrade only |

### Cluster size

| Size | Solve ease | Boundary error |
|------|------------|----------------|
| Tiny | Easy | More handoffs |
| Medium | Balanced | **Sweet spot** |
| Huge | Slow/timeout | Fewer boundaries |

## Operability Addenda

### Deploy pipeline

```text
solver build → fixtures → shadow station → canary → bake → fleet
```

### Guardrails

- Hard violation publish = 0  
- Unassigned spike  
- Churn spike  
- Solve timeout rate  
- On-time regression  

### Kill switches

1. Greedy mode  
2. Disable auto-reopt  
3. Freeze plans  
4. Disable traffic triggers  
5. Isolate station  

## Worked Capacity Narrative

Stops/station × matrix approx cost × solve seconds → workers; show clustering bends O(n²); 100× needs hierarchy not one fat solver.

## Customer-Trust Paragraph

Missed delivery windows and silent unassigned stops are promise breaches. Prefer surfacing unassigned early for recovery over a “pretty” route that hides failures. Honest ETAs beat optimistic sequences.

## Progressive Scale Recap

- **10×:** workers + ETA cache  
- **100×:** zone hierarchy + continuous local search  
- **1,000×:** learned seeds + edge micro-reopt  

---

## Supplemental Depth Pack — Delivery Route Optimization

### S1. Prefix freeze

Completed immutable.
**Metric:** `reopt_moved_completed`.

### S2. Hard validate

Before publish.
**Metric:** `infeasible_published`.

### S3. Matrix cache

Tile hit rate.
**Metric:** `eta_cache_hit`.

### S4. Churn penalty

In objective.
**Metric:** `avg_stop_churn`.

### S5. Unassigned visible

Queue + pages.
**Metric:** `unassigned_stops`.

### S6. Debounce

Coalesce storms.
**Metric:** `reopt_batch_size`.

### S7. Greedy fallback

Always.
**Metric:** `fallback_rate`.

### S8. Unit economics

Cost per stop / on-time.
**Metric:** `$/stop`, `on_time_%`.

## Scenario Runbooks

| Scenario | Action |
|----------|--------|
| Snowstorm | Inflate ETA; widen soft; prioritize SLAs |
| Map outage | Haversine degrade; freeze major reopt |
| Van breakdown | Reassign remaining stops ASAP |
| Solver outage | Greedy; page |
| Dispatcher thrash | Rate-limit edits; show costs |
| Density spike Prime Day | Smaller clusters; more vehicles; overtime rules |

## Rapid-Fire Q&A — Delivery Route Optimization

**Q:** Problem class? **A:** VRP with windows.  
**Q:** Exact? **A:** No, heuristics.  
**Q:** Shard? **A:** Station.  
**Q:** Matrix? **A:** Cached tiles.  
**Q:** Reopt? **A:** Local+freeze prefix.  
**Q:** Fallback? **A:** Greedy feasible.  
**Q:** Unassigned? **A:** Explicit.  
**Q:** Churn? **A:** Penalize.  
**Q:** ML? **A:** Propose only.  
**Q:** TSP? **A:** Special case.  
**Q:** Fill truck? **A:** Sibling.  
**Q:** Food dispatch? **A:** Related continuous.  
**Q:** 2-opt? **A:** Intra improve.  
**Q:** Soft window? **A:** Penalty.  
**Q:** Hard window? **A:** Feasibility.  
**Q:** Service time? **A:** Per stop+area.  
**Q:** Debounce? **A:** 10–30s.  
**Q:** Diff sync? **A:** Tail patches.  
**Q:** Warm start? **A:** Yes.  
**Q:** Deal-breaker? **A:** Nightly-only exact.  
**Q:** 10×? **A:** Cache/workers.  
**Q:** 100×? **A:** Hierarchy.  
**Q:** Oscillation? **A:** Damping.  
**Q:** Skills? **A:** Constraint.  
**Q:** Capacity? **A:** Vol+wt.  
**Q:** Multi-depot? **A:** Assign then route.  
**Q:** Offline nav? **A:** Cached tail.  
**Q:** Who pages? **A:** Routing oncall.  
**Q:** Promise SEV? **A:** Mass late/unassigned.  
**Q:** ALNS? **A:** Batch optional.  
**Q:** Traffic epoch? **A:** Matrix version.  
**Q:** Building cluster? **A:** Shared service.  
**Q:** E-van range? **A:** Plugin.  
**Q:** A/B? **A:** Station canary.  
**Q:** Labor break? **A:** Shift blocks.  
**Q:** Pickup-delivery? **A:** Precedence.  
**Q:** Cost lever? **A:** Cache hit.  
**Q:** Validator first test? **A:** Yes.  
**Q:** Silent drop? **A:** Forbidden.  
**Q:** Global solve? **A:** No.  
**Q:** Driver sticky? **A:** Prefix freeze.  
**Q:** Dispatcher? **A:** Audited edits.  
**Q:** On-time metric? **A:** Primary.  
**Q:** CPU math? **A:** Stations×seconds.

## Narrative Walkthrough — Delivery Route Optimization

### Beat 1

Clarify VRP ≠ truck fill ≠ food matching alone.

### Beat 2

Show O(n²) trap; introduce cluster+cache.

### Beat 3

Draw planner, solver pool, reopt, driver app.

### Beat 4

Construction + local search + validate.

### Beat 5

Exception reopt with prefix freeze + churn.

### Beat 6

Hard/soft windows; unassigned explicit.

### Beat 7

Scale jumps; storm debounce.

### Beat 8

Close: promise + fallback + deal-breakers.

## Pre-Onsite Checklist — Delivery Route Optimization

- [ ] VRP definition  
- [ ] Matrix strategy  
- [ ] Batch vs reopt  
- [ ] Prefix freeze  
- [ ] Progressive scale  
- [ ] Deal-breakers  
- [ ] 60s closer  
- [ ] Sibling boundaries  

### Extra drill

O(n²) numeric example.

### Extra drill

List local search moves.

### Extra drill

Unassigned reason codes.

### Extra drill

Reopt debounce design.

### Extra drill

ETA cache key fields.

### Extra drill

Hard vs soft windows.

### Extra drill

Churn penalty rationale.

### Extra drill

Greedy fallback outline.

### Extra drill

Station canary metrics.

### Extra drill

Storm mode prioritization.

### Extra drill

Pickup-delivery precedence.

### Extra drill

Multi-depot split.

### Extra drill

Map outage degrade.

### Extra drill

Plan diff protocol.

### Extra drill

Warm start benefits.

### Extra drill

Electric range constraint.

### Extra drill

Dispatcher UX validate.

### Extra drill

Service time apartments.

### Extra drill

Kill switches.

### Extra drill

1000× edge reopt vision.

### Extra drill

Compare to classic TSP interview.

### Extra drill

SEV mass lateness.

### Extra drill

Shadow heuristic eval.

### Extra drill

Cluster size tradeoff.

### Extra drill

Labor shift modeling.

### Extra drill

Bike vs van profiles.

### Extra drill

Returns reinsert.

### Extra drill

Interview trap: nightly MIP only.

### Extra drill

60s closer memorization.

### Extra drill

Cost vs on-time speech.

### Extra drill

Ownership boundary.

---

*End of delivery route optimization system design.*
