# System Design: Delivery Route Optimization

> **Focus areas:** VRP / CVRP / VRPTW · Last-mile · Dynamic reoptimization · Map & distance algorithms · SLA windows · Courier capacity · Amazon logistics last-mile flavor  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, algo+systems duality, cost vs promise tradeoffs

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

Goal: **bound last-mile routing**—assign packages (or stops) to vehicles/couriers and sequence routes under time windows, capacity, and traffic, then **reoptimize** as reality changes without thrashing drivers.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is optimized? | Last-mile from station/DSP to customer doors | Station-scoped VRP cells |
| F2 | Vehicle types? | Amazon vans, DSP vans, flex drivers, bikes (geo) | Heterogeneous fleet model |
| F3 | Constraints? | Capacity (cube/weight/stops), time windows, skills (adult signature), range | Constraint engine |
| F4 | Objective? | Min cost (time/miles/labor) s.t. promise windows; minimize lateness | Soft TW + hard capacity |
| F5 | Static vs dynamic? | Plan waves overnight + continuous reopt daytime | Batch solver + online inserter |
| F6 | Map data? | Travel times with traffic; walk last meters | Distance matrix / OSRM / GraphHopper-like |
| F7 | Inputs? | Stops with geo, window, service time, package attrs | Stop model |
| F8 | Output? | Routes: ordered stops + ETAs + navigation hints | Versioned itinerary |
| F9 | Driver UX? | Turn-by-turn; next-stop; exceptions | Mobile sync; offline tolerance |
| F10 | Exceptions? | Customer absent, access codes, weather, vehicle break | Reopt triggers |
| F11 | Pickup + delivery? | Mostly delivery; some returns/AMZL pickups | Pickup-delivery pairs optional |
| F12 | Clustering? | Territory / microhubs | Cluster-first then route |
| F13 | SLA tiers? | Prime same-day / next-day / scheduled | Priority classes |
| F14 | Human override? | Dispatchers insert/remove | Mutation + validate |
| F15 | Idempotency? | Wave rebuilds, GPS dupes | Route epoch fencing |

**MVP functional scope:**

1. Ingest stops for a station/session (wave).  
2. Build distance/time matrix (or on-demand with cache).  
3. Cluster + construct routes (heuristic VRP).  
4. Respect capacity & soft time windows.  
5. Publish itineraries with ETAs.  
6. Ingest GPS/progress events; update ETAs.  
7. Dynamic insert/cancel with bounded reshuffle.  
8. Dispatcher tools: freeze route, manual reassign.  
9. Score: miles, time, lateness, overtime.

**Out of MVP:**

- Globally optimal MIP for 10M stops/hour  
- Perfect multi-modal (drone+van) orchestration  
- Full continuous traffic digital twin worldwide  
- Driver shift HR system of record  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Overnight plan latency | Hours OK | Station wave < 30–90 min |
| N2 | Online insert latency | Seconds–minute | p99 < 30s for single insert |
| N3 | ETA quality | Useful for CX | Median abs error < 15–20 min last-mile |
| N4 | Availability | Drivers need next stop | Edge cache itinerary |
| N5 | Consistency | One active itinerary | Epoch per route |
| N6 | Scale | See table | Station sharding |
| N7 | Safety | Hours of service | HOS constraints |
| N8 | Cost | Reduce cost-to-serve | Track $/stop, miles/stop |
| N9 | Audit | Why stop on route A | Decision traces |
| N10 | Map freshness | Traffic | Periodic matrix refresh |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Overnight: 3,000 stops → 40 routes → published → drivers execute → 98% on-time.  
2. Same-day stop appears → insert into nearby route with min detour → epoch++.  
3. Customer not home → attempt policy → parcel locker / reattempt → reopt.  
4. Traffic jam → ETA refresh; if infeasible, swap later stops / helper route.  
5. Vehicle breakdown → remaining stops redistributed.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Matrix service timeout | Use cached times / Haversine×factor fallback |
| Solver timeout | Publish incumbent; improve in background |
| Thrashing inserts | Rate-limit reshuffle; freeze sequence prefix |
| Wrong geocode | Exception queue; manual pin |
| Dense apartment | Service time model; parking node |
| Time window impossible | Flag; escalate / split / delay promise |
| Duplicate stop ingest | Idempotency on stop_id |
| Clock skew driver device | Server ETAs; device for nav only |
| Station outage connectivity | Offline itinerary; sync later |
| Prime Day 3× stops | Extra flex capacity; greedy insert mode |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Stations / depots | 1K | 5K | 20K | 100K |
| Stops / day | 50M | 500M | 5B | 50B |
| Routes / day | 500K | 5M | 50M | 500M |
| Peak **stop ingest**/s | 5K | 50K | 500K | 5M |
| Peak **solve jobs**/s | 50 | 500 | 5K | 50K |
| Peak **GPS events**/s | 200K | 2M | 20M | 200M |
| Peak **reopt requests**/s | 100 | 1K | 10K | 100K |
| Avg stops / route | 100 | 120 | 140 | 150 |
| Geos | 5 | 15 | 30 | 50+ |

**What each jump forces:**

- **10×:** Station shards; matrix cache; async solvers.  
- **100×:** Cluster-first; hierarchical territories; GPU/CPU fleets; traffic tiles.  
- **1,000×:** Approximate distance oracles; continuous insertion; regional planning; learned service times; hard isolation per station actor.

### 1.5 Etc.

- Upstream promise engine sets windows.  
- Upstream packing may constrain load order (van packing sibling).  
- Drivers/DSP apps consume itineraries.  
- Algorithmic interview may ask TSP/VRP heuristics on whiteboard.

**Scope statement:**

> Design Amazon-style last-mile route optimization: station-scoped VRP with time windows and capacity, overnight construction plus daytime dynamic reoptimization, powered by map/travel-time services—baseline ~50M stops/day scaling through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Stop ingest | 5K/s | 5M/s | Durable |
| Batch solve | 50/s | 50K/s | CPU heavy |
| Dynamic reopt | 100/s | 100K/s | Latency sensitive |
| GPS / progress | 200K/s | 200M/s | Special plane |
| ETA read (CX) | 10K/s | 10M/s | Cache |
| Dispatcher ops | 20/s | 20K/s | Interactive |

**Anti-pattern:** mixing GPS writes into route OLTP.

### 2.2 Matrix math (critical)

```text
Naïve N×N matrix for N=3,000 stops:
3,000² = 9M cells
If each cell 8 B → 72 MB per station wave — OK
If N=30,000 → 900M cells → 7.2 GB — too big; don’t build dense

Strategies:
- Cluster to 40 routes × ~100 stops → 40 × 100² = 400K cells
- Or on-demand + cache with spatial locality
- Or cell-to-cell matrix (H3) + local refinement
```

### 2.3 Solver CPU

```text
Construction heuristic for 100-stop route: ms–tens of ms
Station 3,000 stops with cluster+route: seconds–minutes
Metaheuristic improvement: time-boxed (e.g. 5–60 min overnight)

Baseline 50 solves/s × 20 CPU-s = 1,000 cores busy if heavy
→ Prefer cheap construct + limited improve; overnight longer OK
```

### 2.4 Storage

```text
Stop ~300 B; 50M/day × 7 × 300 B ≈ 105 GB
Route plan ~50 KB; 500K × 50 KB ≈ 25 GB/day
1,000× stops: 50B/day × 7 × 300 B ≈ 105 TB hot

GPS breadcrumb cold storage separate; downsample
```

**Unit check:** 50B × 300 B = 15 TB/day stops, not PB. 5e10×300=1.5e13=**15 TB/day**. ×7≈**105 TB**.

### 2.5 Cost objective sketch

```text
cost(routes) =
  w_miles * miles
+ w_time * drive_minutes
+ w_late * sum(lateness_minutes)
+ w_ot * overtime_minutes
+ w_vehicle * num_routes
+ w_flex * flex_premium
+ w_fail * expected_failed_attempts
```

### 2.6 Dynamic insert math

```text
Insert stop S into route R:
  evaluate each insertion position O(|R|)
  best detour = delta drive + lateness impact
Try k nearest routes (e.g. 10) → 10×100 = 1K evals
With cached segment times ≈ microseconds–ms each → fine
At 100K inserts/s need sharding & approx candidate routes
```

---

## 3. High-Level Design

### 3.1 Entities

| Entity | Fields |
|--------|--------|
| Station | geo, timezone, fleet |
| Stop | lat/lng, window[a,b], service_s, demand, priority, skills |
| Vehicle/Courier | capacity, shift window, start/end depot, skills |
| Route | ordered stops, vehicle_id, epoch, score |
| Leg | from→to, travel_s, distance_m |
| MatrixCache | key→travel |
| Session/Wave | planning horizon |

### 3.2 Services

| Service | Role |
|---------|------|
| Stop Ingest | Idempotent stops |
| Geocoder / Normalizer | Snap to road / access point |
| Territory / Cluster | Partition stops |
| Matrix Service | Travel times |
| VRP Solver Workers | Construct/improve |
| Reopt Service | Inserts/swaps |
| Itinerary Store | Versioned routes |
| Driver Sync | Mobile |
| Progress / GPS Plane | Live |
| ETA Projector | Customer ETAs |
| Dispatch Control | Overrides |
| Score / Analytics | Offline eval |

### 3.3 Algorithm pipeline

```text
Stops → (optional) Territory → Clusters ≈ #vehicles
     → Seed routes (sweep / petal / CW savings)
     → Improve (2-opt, Or-opt, relocate, exchange)
     → Time-window feasibility repair
     → Publish
```

### 3.4 Progressive architecture

| Scale | Shape |
|-------|-------|
| 1× | Station service + Postgres + OSRM + heuristic |
| 10× | Kafka; worker fleet; Redis matrix cache |
| 100× | Territory hierarchy; traffic tiles; reopt actors |
| 1000× | Approx oracles; learned priors; station single-writer |

---

## 4. Architecture Diagram

### 4.1 Logical

```text
  Promise / Sortation ──stops──► Stop Ingest ──► Stop Store
                                                   │
                                            Wave Orchestrator
                                                   │
                     ┌─────────────────────────────┼────────────────┐
                     ▼                             ▼                ▼
              Cluster Service               Matrix Service    Fleet State
                     │                             │                │
                     └──────────────┬──────────────┘                │
                                    ▼                               │
                             VRP Solver Workers ◄───────────────────┘
                                    │
                                    ▼
                             Itinerary Store (epoch)
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                ▼
              Driver App      ETA Projector    Dispatch UI
                    │
                    ▼
              GPS / Progress ──► Reopt Service ──► Itinerary (epoch++)
```

### 4.2 Station cell

```text
Region
  └── Station Actor / Shard (single writer for route mutations)
        ├── overnight solver lease
        ├── daytime reopt queue
        ├── matrix cache partition
        └── itinerary edge sync
```

### 4.3 Route epoch state

```text
DRAFT → SOLVING → PUBLISHED → IN_PROGRESS → COMPLETED
PUBLISHED → SUPERSEDED (epoch++)
IN_PROGRESS → REOPT → PUBLISHED'
Any → FROZEN (dispatcher)
```

### 4.4 Dynamic reopt flow

```text
Event: new stop / cancel / breakdown / large ETA drift
  → Reopt planner (station)
  → Candidate routes via geo index
  → Evaluate insertion / relocation
  → Feasibility (capacity, HOS, windows)
  → If gain > threshold AND not thrashing: commit epoch++
  → Notify driver; patch prefix-frozen if already en route
```

---

## 5. Design Deep Dive

### 5.1 VRP family (interview fluency)

| Variant | Meaning |
|---------|---------|
| TSP | Single route all stops |
| VRP | Multiple vehicles |
| CVRP | Capacity |
| VRPTW | Time windows |
| PDPTW | Pickup-delivery |
| DVRP | Dynamic requests |

Amazon last-mile ≈ **Dynamic CVRPTW** with heterogeneous fleet.

### 5.2 Distance & map algorithms

**Graph:** road network nodes/edges with speeds; contraction hierarchies / multilevel for fast queries.

**Travel time query:**

```text
time(a,b,t_dep) → seconds accounting for traffic profile
```

**Matrix strategies:**

1. Many-to-many CH / table  
2. Cell centroid matrix + local A*  
3. Learned ETA between H3 cells  

**Fallback:** Haversine × road factor (e.g. 1.3–1.5) when map fails—mark low confidence.

**Last meters:** apartment access graphs; parking nodes ≠ rooftop lat/lng.

### 5.3 Construction heuristics

| Heuristic | Notes |
|-----------|-------|
| Sweep | Angular sort around depot |
| Clarke-Wright savings | Classic merges |
| Petal / cluster-first | Scale friendly |
| Nearest neighbor | Weak alone; seed OK |
| Insertion (cheapest) | Good for dynamic |

### 5.4 Improvement operators

```text
2-opt, 3-opt (intra-route)
Relocate, exchange (inter-route)
Or-opt
Guided local search / SA / LNS (Large Neighborhood Search)
```

Overnight: LNS with time budget. Daytime: cheap relocate/insert only.

### 5.5 Time windows

```text
Arrive_i = Depart_{i-1} + travel + service_{i-1}
if Arrive_i < a_i: wait
lateness = max(0, Arrive_i - b_i)
hard TW: infeasible if lateness > 0 (rare for Amazon CX soft)
soft TW: penalty in score
```

### 5.6 Capacity & van packing coupling

Route demand sum ≤ vehicle capacity. For tight vans, sequence may need **load order** compatibility with unload sequence (LIFO)—coordinate with packing service or enforce zone heuristics.

### 5.7 Dynamic reoptimization policy

**Freeze prefix:** stops already completed or within next K minutes immutable.

**Thrash control:**

```text
if epoch_count(route, last_15m) > threshold: only accept SLA-critical inserts
min_improvement_dollars to reshuffle
```

**Batch micro-reopt:** accumulate events 5–15s.

### 5.8 ETA projection

```text
For remaining stops: simulate along route with live traffic + driver’s progress
Publish customer-facing window; widen under uncertainty
```

Do not expose noisy second-level shifts every GPS ping—smooth.

### 5.9 Clustering / territories

```text
Geohash / K-means / capacitated clustering
Stable territories reduce driver learning cost (Amazon DSP familiarity)
Tradeoff: stability vs pure daily optimum
```

### 5.10 Storage

```text
Stops: PK STATION#id SK STOP#id
Routes: PK STATION#id SK ROUTE#id#EPOCH
Active pointer: ROUTE#id → active_epoch
Matrix cache: Redis key cellA:cellB:profile → (sec,m)
```

### 5.11 GPS plane

Same lesson as food delivery: high-QPS presence separate. Progress events (“completed stop”) are business events into reopt—not every lat/lng.

### 5.12 Consistency & fencing

- Station single-writer for route mutations (actor or lease)  
- Route epoch monotonic  
- Driver app rejects older epoch for sequence changes (nav may finish current leg)  
- Idempotent stop ingest  

### 5.13 Failure & degradation

| Failure | Mode |
|---------|------|
| Solver down | Use previous day pattern + greedy |
| Map down | Cached matrix + Haversine factor |
| Reopt storm | Freeze non-critical |
| Station partition | Local greedy insert offline |

### 5.14 Observability

| Metric | Why |
|--------|-----|
| Miles/stop | Efficiency |
| On-time % | CX |
| Reopt epochs/hour | Thrash |
| Matrix p99 | Map health |
| Insert success rate | Dynamic health |
| Overtime minutes | Cost/labor |

### 5.15 Security

- Driver only sees own routes  
- Customer address PII encrypted  
- Dispatcher authz scoped to station  
- Audit overrides  

### 5.16 Testing

- Feasibility properties (capacity never exceeded)  
- Golden station fixtures  
- Sim traffic digital twin  
- Fuzz random inserts for thrash limits  

### 5.17 10×/100×/1,000×

**10×:** shard by station; cache matrix; async waves.  
**100×:** territory hierarchy; LNS overnight; actor reopt; traffic profiles.  
**1000×:** approximate oracles; learned service times; continuous insertion at edge; multi-station load balancing for flex.

### 5.18 Amazon LP angles

- **Dive deep** on on-time regressions after map update  
- **Frugality:** don’t recompute N² matrices  
- **Bias for action:** publish incumbent before perfect  
- **Customer obsession:** soft windows that protect promise  

### 5.19 Interview coding hooks

```text
cheapestInsertion(route, stop, distFn)
twoOpt(route)
lateness(route, windows, travel)
```

Then systems: “station actor, epochs, matrix cache…”

### 5.20 Cost vs miles

Shorter miles with many late Prime packages is a bad plan. Always show lateness term on the board.

---

## 6. Wrap-Up

### 6.1 Summary

Station-scoped **dynamic CVRPTW** platform: cluster+heuristic construction, map/travel matrix service, versioned itineraries, daytime insertion with freeze/thrash controls, separate GPS plane, progressive approximation at extreme scale.

### 6.2 Tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Exact MIP vs heuristics | Heuristics + LNS budget |
| Dense matrix vs on-demand | Cluster matrices / cell oracles |
| Daily global opt vs stable territories | Hybrid |
| Continuous reshuffle vs freeze prefix | Freeze + thresholds |
| Miles vs lateness | Explicit weighted cost |

### 6.3 Risks

Geocode errors; map regressions; thrashing drivers; solver hotspots on Prime Day; under-modeled apartment service times.

---

## 7. Deeper / Related Interview Questions

### 7.1 Framing

**Q: Is last-mile just TSP?**  
A: No—multi-vehicle, capacity, windows, dynamic—VRPTW/DVRP.

**Q: Optimize miles or on-time?**  
A: Weighted cost; Amazon promise matters.

**Q: Offline only?**  
A: Overnight + daytime dynamic.

**Q: Who consumes output?**  
A: Driver app, ETA/CX, dispatch, cost analytics.

**Q: Relation to middle-mile truck fill?**  
A: Upstream; different constraints; shared cost culture.

### 7.2 Algorithms

**Q: Clarke-Wright idea?**  
A: Merge routes saving distance vs depot spokes.

**Q: Why 2-opt?**  
A: Remove crossings; local improve.

**Q: Large Neighborhood Search?**  
A: Destroy subset of stops; recreate; escape local minima.

**Q: Genetic algorithms?**  
A: Possible overnight; operational complexity—LNS often preferred.

**Q: Complexity?**  
A: VRP NP-hard; expect heuristics honesty.

**Q: How handle 30k stops matrix?**  
A: Don’t dense N²; cluster or cell oracle.

**Q: A* vs Dijkstra for road?**  
A: A* with landmarks/CH for speed; preprocessing helps.

**Q: Contraction hierarchies?**  
A: Preprocess graph for fast shortest paths—industry standard.

**Q: Time-dependent routing?**  
A: Edge speeds vary by time-of-day buckets.

**Q: Service time modeling?**  
A: By address type / historical; dominates dense urban.

### 7.3 Dynamic

**Q: Insert mid-route?**  
A: Evaluate positions after freeze prefix; pick min cost feasible.

**Q: Avoid thrashing?**  
A: Epoch rate limits; min improvement; freeze.

**Q: Cancel stop?**  
A: Remove; optional compact; notify.

**Q: Breakdown?**  
A: Reassign remaining as new inserts with high priority.

**Q: Micro-batch reopt?**  
A: Yes—amortize.

### 7.4 Systems scale

**Q: Global router monolith?**  
A: No—station cells/actors.

**Q: 200M GPS/s?**  
A: Presence plane; downsample; not VRP DB.

**Q: Solver fleet?**  
A: Queue by cutoff; autoscale; leases.

**Q: Hot station?**  
A: Split territories; more workers; flex pool.

**Q: Multi-region?**  
A: Station home region.

### 7.5 Map & data

**Q: Bad geocode?**  
A: Exception; manual; ML suggest access point.

**Q: Bridge closed?**  
A: Traffic/map incident feed → invalidate cache → reopt affected.

**Q: Rural long drive?**  
A: Different service models; range constraints EV.

**Q: Units meters vs miles?**  
A: Canonical meters/seconds internally.

### 7.6 SLA & product

**Q: Impossible window?**  
A: Surface early; renegotiate promise; don’t silently plan infeasible.

**Q: Same-day premium?**  
A: Higher priority weight; maybe dedicated flex.

**Q: Delivery attempts?**  
A: Policy engine; locker fallback; reattempt scheduling.

### 7.7 Consistency

**Q: Driver offline edits?**  
A: Server authoritative on return; conflict resolve by epoch.

**Q: Two dispatchers edit?**  
A: CAS version; station lock.

**Q: Stale matrix in solve?**  
A: Stamp matrix version; refresh if too old.

### 7.8 Observability drills

**Q: Miles/stop jumped 10%?**  
A: Map change, clustering change, window tightness, weather, geocode shift.

**Q: On-time dropped?**  
A: Traffic model, service time, insert thrash, capacity shortage.

**Q: Reopt CPU hot?**  
A: Thresholds; candidate k; station storm.

### 7.9 Comparisons

**Q: vs food delivery matching?**  
A: Longer routes, more stops, stronger overnight planning; food more continuous marketplace.

**Q: vs middle-mile?**  
A: Fewer stops per vehicle; different packing; linehaul schedules.

**Q: vs Google Maps ETA?**  
A: We sequence many stops under capacity—Maps is a subroutine.

### 7.10 Reliability

**Q: Publish failed mid-solve?**  
A: Keep prior epoch active; retry.

**Q: Poison stop crashes solver?**  
A: Quarantine; continue others.

**Q: Kafka replay?**  
A: Idempotent stop upserts.

### 7.11 Security & privacy

**Q: Address PII in logs?**  
A: Redact; tokenize.

**Q: Driver stalking risk?**  
A: Share only assigned customer details; time-bound.

### 7.12 Org

**Q: Map team breaks ETAs?**  
A: Contract SLOs; canary traffic profiles; joint IR.

**Q: Science wants 2h LNS, ops needs publish?**  
A: Anytime incumbent; improve after publish offline shadow.

### 7.13 Arithmetic traps

**Q: 3000² cells?**  
A: 9M.

**Q: 50B stops × 300 B / day?**  
A: 15 TB/day.

**Q: Claiming exact optimum daily for nation?**  
A: Unrealistic—challenge.

### 7.14 Van constraints

**Q: Weight vs cube binding?**  
A: Track both; either can bind.

**Q: Hazmat on van?**  
A: Skill/constraint flags.

**Q: Load order vs stop order?**  
A: Coordinate with packing; LIFO zones.

### 7.15 Flex / gig coupling

**Q: Surge flex hiring?**  
A: Capacity planning uses forecast; price flex separately.

**Q: Fairness among DSPs?**  
A: Business rules outside pure miles opt.

### 7.16 Edge / offline

**Q: Rural dead zone?**  
A: Prefetch next N stops; nav offline packs; sync completions later.

### 7.17 Experimentation

**Q: A/B routing algorithms?**  
A: Station-level experiments; metrics miles + on-time + CX; shadow traffic.

### 7.18 EV / range (advanced)

**Q: Add charging?**  
A: VRPTW with recharging nodes—defer unless asked; mention extension.

### 7.19 Cross links

**Q: Locker delivery stops?**  
A: Different service times; capacity at locker (sibling problem).

**Q: Food courier batching?**  
A: Same insertion ideas; shorter horizon.

### 7.20 Closing

**Q: One week to Prime Day?**  
A: Freeze thrash knobs, matrix cache warm, flex capacity, greedy insert failover, incumbent publish—not new MIP.

---

## 8. Appendices

### 8.1 Schemas

```text
Stop
  station_id, stop_id, lat, lng, window_start, window_end,
  service_s, demand_vol, demand_kg, priority, skills[], state

Route
  station_id, route_id, epoch, vehicle_id, stop_sequence[],
  score, matrix_version, state

MatrixCache
  key: h3_a:h3_b:tod_bucket → {sec, meters, conf}

ProgressEvent
  route_id, stop_id, type, ts, idem_key
```

### 8.2 Invariants

| Invariant | Rule |
|-----------|------|
| Capacity | sum demand ≤ vehicle |
| Single active epoch | one pointer |
| Prefix freeze | completed immutable |
| Feasible publish | no hard constraint break |
| Idempotent stops | unique stop_id per wave |

### 8.3 Scale checklist

| Scale | Must |
|-------|------|
| 1× | Heuristic VRP, matrix, publish, basic insert |
| 10× | Station shard, cache, async solve |
| 100× | Territories, LNS, actors, traffic |
| 1000× | Approx oracles, learned service, edge insert |

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| VRPTW | VRP with time windows |
| LNS | Large neighborhood search |
| Freeze prefix | Immutable head of route |
| Detour | Extra time/miles to insert |
| CH | Contraction hierarchies |
| Territory | Stable geographic partition |
| Incumbent | Best plan so far |
| Soft window | Lateness allowed with penalty |

### 8.5 Estimation cheat-sheet

```text
matrix_cells ≈ routes * (stops_per_route)^2  (clustered)
OR ≈ N^2 (avoid large N)
insert_evals ≈ k_routes * route_len
storage ≈ stops/day * days * bytes
```

### 8.6 API sketch

```text
POST /v1/stations/{id}/stops
POST /v1/stations/{id}/waves/{id}/solve
GET  /v1/routes/{id}
POST /v1/routes/{id}/insertStop
POST /v1/routes/{id}/progress
POST /v1/stations/{id}/reopt
GET  /v1/stops/{id}/eta
```

### 8.7 Pseudocode cheapest insertion

```text
function cheapestInsert(routes, stop, dist):
  best = ∞; choice = null
  for r in candidateRoutes(stop, k):
    for i in insertPositions(r):  # after freeze
      d = deltaCost(r, i, stop, dist)
      if feasible(r, i, stop) and d < best:
        best = d; choice = (r,i)
  return choice
```

### 8.8 Score weights (illustrative)

```text
w_miles=1.0 w_time=0.5 w_late=5.0 w_ot=3.0 w_vehicle=50 w_fail=20
```

### 8.9 Risks

| Risk | Mitigation |
|------|------------|
| Thrash | Freeze + thresholds |
| Map outage | Cache + Haversine |
| Geocode | Exception queues |
| Solver timeout | Incumbent |
| Peak surge | Flex + greedy mode |

### 8.10 SLOs

| SLO | Target |
|-----|--------|
| Wave publish before dispatch | 99% on time |
| Insert p99 | < 30s |
| Hard infeasible published | 0 |
| On-time delivery | business target e.g. 95%+ |
| Epoch thrash / route / hour | < 6 typical |

### 8.11 Decision log

| Decision | Pick | Why |
|----------|------|-----|
| Boundary | Station | Scale |
| Solver | Heuristic+LNS | NP-hard |
| Matrix | Cluster/cell | N² blowup |
| Dynamic | Insert+freeze | Driver UX |
| Objective | Cost+lateness | Amazon CX |

### 8.12 Related systems

- Truck fill / van pack  
- Promise engine  
- Locker capacity  
- Driver app / navigation  
- Traffic / maps platform  

### 8.13 Narrative (2 min)

> “Last-mile route optimization is **dynamic CVRPTW at station scope**. We cluster stops, build routes with savings/insertion heuristics, improve overnight with LNS, and publish versioned itineraries. Daytime we insert with a frozen prefix and thrash controls. Travel times come from a matrix/oracle service—never naive N² at city scale. GPS is a separate plane. At 1,000× we approximate distance oracles and keep a single writer per station.”

### 8.14 Checkpoint

1. VRP variant named?  
2. Matrix strategy non-N²?  
3. Soft vs hard windows?  
4. Epoch + freeze?  
5. GPS separated?  
6. Cost includes lateness?  

### 8.15 Extensions

- EV charging  
- Multi-depot  
- Drone assist  
- Joint packing+routing  
- Carbon objective  

### 8.16 Operator runbook (excerpt)

```text
On-time drop:
  1) traffic tile freshness
  2) service time model drift
  3) insert thrash metrics
  4) capacity shortfall
  5) geocode defect rate
```

### 8.17 Whiteboard TSP vs systems

Always bridge: “TSP 2-opt is the kernel; Amazon needs station sharding, fencing, and map SLOs around it.”

---

*End of document — Delivery Route Optimization (Amazon SDE III system design)*
