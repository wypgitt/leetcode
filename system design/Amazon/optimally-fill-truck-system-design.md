# System Design: Optimally Fill a Truck (Amazon Logistics)

> **Focus areas:** Bin packing / knapsack · Constraints · Online vs batch · Warehouse waves · Stability & axle · SLA cutoffs · Explainability · Human override  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Feasible pack beats theoretically optimal late pack; deal-breaker: unbounded MIP in the ship-path critical loop  
> **Interview theme:** Amazon SDE III / L6 — **Outbound truck loading optimization** (FC → trailer / middle-mile)

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

Goal: design a system that **selects and arranges freight to fill a truck/trailer well**—volume, weight, axle, destination compatibility, load stability, cutoffs—under Amazon FC operational reality.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Build feasible high-utilization loads | Pure TSP last-mile routing |
| Output | Load plan + pick/stage instructions | Driver turn-by-turn |
| Optimizer | Heuristics + bounded math programming | Overnight academic MIP only |
| Success | Cubes out / weighs out on time | 0.1% better fill after missed trailer |
| Amazon lens | Frugality, ownership, mechanisms | Ivory-tower optimality |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Decision unit? | Trailer / container for lane + departure | `LoadPlan` per truck departure |
| F2 | Items? | Cartons/totes/pallets with LWH, weight, stackability | Item master + handling flags |
| F3 | Objective? | Max utilization (cube/weight), min leftovers, on-time | Multi-objective with constraints first |
| F4 | Hard constraints? | Weight, volume, axle, hazmat segregate, crush limits | Feasibility layer before score |
| F5 | Destinations? | Single dest or multi-stop compatible set | Compatibility graph |
| F6 | Timing? | Wave-based; freeze before departure T−X | Online accept until freeze |
| F7 | 3D packing? | Often pallet/stack abstraction; optional 3D | Start 1.5D/2D; escalate |
| F8 | Overrides? | Supervisor can force include/exclude | Audited overrides |
| F9 | Explain? | Why item left off | Reason codes |
| F10 | Replan? | Yard delay / new hot freight | Versioned plans |
| F11 | Inputs live? | Inventory, location, readiness | Nearline snapshots |
| F12 | Downstream? | Pick, stage, load, BOL | Evented handoffs |

**MVP:** For a scheduled trailer, produce a feasible load plan maximizing fill under weight/volume/stack rules; support freeze; explain exclusions; replan until cutoff; integrate warehouse execution.

**Out of MVP:** Perfect 3D nesting of irregular SKUs; real-time robot stow pathing; global multi-day network MIP; driver routing.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Plan latency | < 5–30s typical wave; < 2–5 min hard cap |
| N2 | Feasibility | 100% of released plans pass hard constraints |
| N3 | Stability | Plans idempotent for same input snapshot+seed |
| N4 | Availability | Degrade to greedy packer if solver unhealthy |
| N5 | Audit | Every plan version stored with inputs digest |
| N6 | Scale | Thousands of concurrent trailers in peak |

### 1.3 Cases

**Happy:** Wave opens → candidate freight → optimize → pick → stage → load → depart cubes-out.  
**Edges:** Weigh-out before cube-out; hazmat conflict; crushable under heavy; late hot ASIN; trailer swap length; inventory lie; dock congestion forces early freeze; override breaks axle—reject.

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Trailers/day | 5K | 50K | 500K | 5M |
| Candidate lines/plan | 2K | 5K | 20K | 100K+ |
| Jump | Service + greedy | Shard by FC | Solver fleet + caches | Hierarchical network pack |

### 1.5 Repeat-back

“Feasible, explainable truck load plans under physical and SLA constraints—heuristics with bounded optimization—not an unbounded MIP on the critical path.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Estimate |
|-------|----------|
| Plan builds | 5K/day → ~0.1 QPS avg, peak bursts per wave |
| Candidate fetches | MB–tens MB per plan |
| Solver CPU | Seconds–tens of seconds each |
| Execution events | Higher QPS (picks/loads) |

### 2.2 Trailer math

```text
Trailer volume ~ 3,000–4,000 ft³; payload ~40–45k lbs (varies)
Utilization target: cube or weight, lane-dependent
If avg carton 1.5 ft³ → ~2,000–2,500 cartons theoretical
Practical with pallets/aisles much fewer handling units
```

### 2.3 Compute

```text
5K trailers × 20s CPU = 100K CPU-s/day ≈ 1.2 CPU-days
Peak wave 10× concurrency → need solver worker pool + queue
At 100×: must shard, cache features, tighten candidate sets
```

### 2.4 Latency budget

| Step | Budget |
|------|--------|
| Snapshot candidates | 0.5–3s |
| Feature / filter | 0.2–1s |
| Optimize | 2–25s |
| Persist + publish | 0.2–1s |

### 2.5 Bottlenecks

Candidate explosion; solver tail latency; stale inventory; dock execution drift vs plan.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| `TruckDeparture` | Trailer + lane + cutoff |
| `FreightUnit` | Carton/pallet with dims/weight/flags |
| `CandidateSet` | Eligible units for departure |
| `LoadPlan` | Ordered/stacked assignment |
| `ConstraintEngine` | Hard feasibility |
| `Scorer` | Soft objectives |
| `Optimizer` | Greedy / GA / bounded MIP / CP |
| `ExecutionBridge` | Picks/stage/load feedback |

### 3.2 Pipeline

```text
Trigger(wave|manual|replan)
  → Snapshot(inventory, locations, readiness, trailer attrs)
  → Filter(compat, hazmat, cutoff, freeze rules)
  → Optimize(feasibility-first)
  → Validate(axle/weight/volume/stack)
  → Publish(plan_vN) → Warehouse execution
  → Monitor(load events) → optional replan
```

### 3.3 Algorithm strategy (interview gold)

1. **Constraints first** (reject infeasible).  
2. **Greedy fill** by key (density, dest, stack class) as baseline.  
3. **Local search** (swap/relocate) within time budget.  
4. Optional **bounded MIP** on aggregated pallets—not raw SKUs.  
5. Always keep **greedy fallback**.

### 3.4 Objective sketch

```text
maximize  w1*cube_util + w2*weight_util + w3*priority_sla - w4*fragility_risk - w5*rehandle
subject to volume, weight, axle, stack, hazmat, dest compatibility
```

### 3.5 Online vs batch

- Pre-wave batch for predictable freight.  
- Online admit of hot packages until freeze.  
- After freeze: only swaps that preserve feasibility & time.

### 3.6 Trade-offs

| Choice | Why |
|--------|-----|
| Feasible on-time > optimal late | Amazon operational truth |
| Aggregate to pallet/layer | Tractability |
| Explain codes | Trust of floor ops |
| Human override audited | Reality of docks |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[WMS / Inventory] [Trailer Schedule] [Item Master]
        \              |               /
         +------+------+------+------+
                v
        +---------------+
        | Candidate Svc |
        +-------+-------+
                v
        +---------------+     +--------------+
        | Constraint Eng|---->| Optimizer Pool|
        +-------+-------+     +-------+------+
                v                     |
        +---------------+             |
        | Plan Service  |<------------+
        +-------+-------+
                v
        +---------------+
        | Exec Bridge   | --> Pick/Stage/Load
        +-------+-------+
                v
             Events / Metrics / Audit
```

### 4.2 Sequence: build plan

```text
Scheduler -> PlanService: Build(departure_id)
PlanService -> Candidate: snapshot
PlanService -> Optimizer: solve(budget=20s)
Optimizer -> PlanService: plan_v1 + reasons
PlanService -> WMS: publish pick list
```

### 4.3 Sequence: replan

```text
LoadEvent(short trailer) -> PlanService
PlanService: if before freeze -> solve delta
Else: supervisor tools only
```

### 4.4 Deployment topology

Optimizer workers pull jobs from queue; shard by `fc_id`. Feature cache per FC. Plans in durable DB + object store for large geometries.

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Released plan passes hard constraints.  
2. Plan version monotonic per departure.  
3. Execution consumes explicit `plan_version`.  
4. Overrides recorded with actor + reason.  
5. Solver timeout ⇒ greedy feasible plan or fail loud (no silent empty).

### 5.2 Scalability

- Shard by FC / sort center.  
- Candidate pruning: lane affinity, ready-only, top-N by score.  
- Result cache keyed by input digest for replans.  
- Solver pool autoscales on queue age.

### 5.3 Maintainability

- Constraint plugins versioned.  
- Golden fixtures: trailers with known packs.  
- Shadow mode: new scorer vs prod without executing.

### 5.4 Physical constraints deep dive

**Weight & axle:** model trailer as zones; distribute weight; reject rear-biased loads.  
**Stackability:** crush rating, orientation, “do not stack.”  
**Hazmat:** segregation matrix.  
**Multi-stop:** LIFO load order constraints.

### 5.5 Explainability

Every excluded unit gets reason: `WEIGHT_CAP`, `VOLUME_CAP`, `HAZMAT`, `NOT_READY`, `CUTOFF`, `STACK`, `DEST_INCOMPAT`, `SCORE_LOW`.

### 5.6 Progressive scale

| Jump | Change |
|------|--------|
| 10× | Queue + worker pool, prune candidates |
| 100× | FC cells, hierarchical pack (pallet then trailer) |
| 1,000× | Network-aware pre-grouping; learned candidate proposers |

### 5.7 Deal-breakers

| Deal-breaker | Why |
|--------------|-----|
| Unbounded MIP in ship path | Misses cutoffs |
| Optimize cube only ignore axle | Illegal/unsafe |
| No fallback greedy | Outage = stopped trailers |
| Ignore execution feedback | Paper plans |

---

## 6. Wrap-Up

### 6.1 Decisions

Feasibility-first; time-bounded optimizer + greedy fallback; pallet aggregation; explain codes; versioned plans; FC sharding.

### 6.2 Risks

Bad dims master data; inventory lies; over-constrained lanes; solver regressions; override culture bypassing safety.

### 6.3 45-minute plan

Scope → constraints → HLD → algorithm + fallback → scale/ops → traps.

### 6.4 Closer

> **Optimally Fill Truck**: time-bounded feasible packing under physical constraints, explainable exclusions, execution feedback, progressive scale—optimality is subordinate to on-time safe departure.

---

## 7. Deeper / Related Interview Questions

**Q1. Knapsack or bin packing?**  
**A:** Both flavors: select subset (knapsack) + arrange (packing). Interview: say feasibility + utilization.

**Q2. Why not exact 3D bin packing?**  
**A:** NP-hard; dims noisy; time budgets; start layered heuristics.

**Q3. Weigh-out vs cube-out?**  
**A:** Lane-dependent; track both; density-aware selection.

**Q4. Hot package after freeze?**  
**A:** Next trailer or supervised exception with constraint recheck.

**Q5. How to test optimizer?**  
**A:** Fixtures, property tests (never violate hard constraints), shadow score.

**Q6. Multi-stop LIFO?**  
**A:** Load order constraint: first delivery loaded last.

**Q7. Who owns bad axle plan that departed?**  
**A:** Load plan service + dock execution joint SEV—define RACI.

**Q8. ML to predict fill?**  
**A:** Useful for candidate proposal / time estimates; not sole feasibility.

**Q9. Difference vs route optimization?**  
**A:** This fills a truck; routing sequences stops—complementary.

**Q10. Trap: “just use CPLEX online”?**  
**A:** Bound time; aggregate; fallback.

---

## 8. Appendices

### 8.1 Schema

```text
Departure(id, fc, lane, trailer_type, cutoff, status)
FreightUnit(id, dims, weight, flags, dest, ready_at, loc)
LoadPlan(id, departure_id, version, util_cube, util_wt, status)
LoadLine(plan_id, unit_id, zone, layer, sequence)
Exclusion(plan_id, unit_id, reason)
Override(plan_id, actor, payload, ts)
```

### 8.2 Pseudocode

```text
function buildPlan(dep, budget):
  snap = snapshot(dep)
  cands = filter(snap)
  plan = greedy(cands, dep.trailer)
  plan = localSearch(plan, cands, deadline=now+budget)
  assert validate(plan)
  return persist(plan)
```

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Cube-out | Volume limited |
| Weigh-out | Weight limited |
| Freeze | No auto replan |
| Wave | Batch planning window |
| Axle | Weight distribution constraint |

### 8.4 Progressive checklist

10× workers; 100× FC cells + hierarchy; 1,000× learned proposers + network pregroup.

### 8.5 Reliability tests

1. Solver kill → greedy plan.  
2. Axle violation attempt → reject.  
3. Replan version bump.  
4. Stale inventory → execution exception path.

### 8.6 60s closer

> We snapshot ready freight, filter hard constraints, run a time-bounded optimizer with greedy fallback, validate axle/weight/volume/stack, publish versioned plans with exclusion reasons, and replan until freeze while listening to load events.

---

## Deep Technical Notes — Optimally Fill Truck

### Candidate pruning

Score proxy: `priority * density * readiness * dest_fit`. Keep top K plus all SLA-critical. Guarantees critical freight considered.

### Layered packing model

Represent trailer as floor slots × layers. Place pallets/stacks into slots; much faster than SKU polyomino.

### Axle model (simplified)

```text
sum(weight_i) <= Wmax
sum(weight_i * position_i) in [Mmin, Mmax]  // moment
```

### Hazmat matrix

Pairwise incompatibility; pre-check before search; hard fail.

### Dimensional data quality

Outliers trigger manual measure workflow; trust scores on dims.

### Execution drift

If loaded ≠ planned, capture delta; feed learning; don’t silently “fix” departed trailer.

### Idempotency

`Build(departure, input_digest)` returns same plan version if unchanged.

## Interview Cards — Optimally Fill Truck

### Card 1: Feasible vs optimal?

Feasible on-time wins. Bound CPU; fallback greedy.

### Card 2: Cube vs weight?

Track both; density selection; lane priors.

### Card 3: Algorithm choice?

Greedy + local search; optional bounded MIP on aggregates.

### Card 4: Freeze semantics?

Cutoff clock; after freeze only supervised.

### Card 5: Explainability?

Exclusion reason codes for every left-behind unit.

### Card 6: Axle safety?

Zone moments; validate before release.

### Card 7: Scale jump?

FC shard; prune N; hierarchy pallet→trailer.

### Card 8: Deal-breaker?

Unbounded exact 3D MIP online; ignore axle.

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope fill ≠ route |
| 5–12 | Constraints + estimates |
| 12–22 | HLD + pipeline |
| 22–35 | Algo, fallback, axle |
| 35–45 | Scale, overrides, traps |

## 10. Operability

### Golden signals

Plan success rate, solver p99, utilization cube/weight, freeze breach count, constraint violation attempts, replan rate, execution match %.

### Rollback ladder

Revert scorer weights → force greedy → disable auto-replan → manual load lists.

### Kill switches

Disable ML proposer; disable local search; freeze all auto plans; FC isolate.

### Security/privacy

Internal system; IAM on overrides; audit; no customer PII required in packer.

### Cost worksheet

```text
CPU_solver dominates; lever = prune candidates + aggregate units
Utilization +1% may beat many CPU $ — measure both
```

### Cross-team deps

WMS, Trailer Schedule, Item Master, Yard, Transportation, Safety Compliance.

---

## More Interview Q&A — Optimally Fill Truck

**Q1. What if dims missing?**  
**A:** Default conservative class; demote priority; measure queue.

**Q2. Pallet vs carton mix?**  
**A:** Normalize to handling units; separate constraints.

**Q3. Soft priority SLA packages?**  
**A:** Must-include set first; fill remainder for util.

**Q4. Can GA beat greedy?**  
**A:** Sometimes; keep time budget; never ship without validate.

**Q5. Multi-FC?**  
**A:** Plans local to FC; network assignment upstream.

**Q6. Cold chain?**  
**A:** Compatibility + time-temp constraints; separate trailers often.

**Q7. How to present util metrics?**  
**A:** Cube, weight, and “effective” considering both.

**Q8. Dock workers ignore plan?**  
**A:** UX + scan enforcement; measure adherence.

**Q9. Determinism?**  
**A:** Seeded RNG; sorted inputs; digest.

**Q10. Failure: published infeasible?**  
**A:** SEV; block; hotfix validator; postmortem.

**Q11. 10× wave spike?**  
**A:** Queue + degrade to greedy for low priority lanes.

**Q12. Learned utilization model?**  
**A:** Predict final util / time; assist candidate cut—not replace physics.

**Q13. Container vs 53' trailer?**  
**A:** Trailer profile plugins.

**Q14. International?**  
**A:** Customs holds as readiness flags.

**Q15. Vs classic knapsack interview?**  
**A:** Elevate to system: data, time, execution, safety.

**Q16. What’s the unit test you write first?**  
**A:** Validator rejects overweight plan.

---

## Deep Technical Addenda

### Search neighborhoods

Swap two units; relocate unit to other zone; eject low score for high SLA. Cap iterations by clock.

### Feature cache

Per unit: density, crush, hazmat class, dest cluster id—computed nearline.

### Plan diff for replan

Compute symmetric difference; minimize pick list churn if picks already started.

### Shadow evaluation

Nightly: re-solve historical snapshots; compare util and constraint slack.

## Tradeoff Matrices — Optimally Fill Truck

### Exactness vs time

| Choice | Util | Risk | Use |
|--------|------|------|-----|
| Greedy only | Good enough | Suboptimal | Fallback / peak |
| Greedy+local | Better | CPU | **Default** |
| Long MIP | Best paper | Miss cutoff | Offline research |

### Aggregation level

| Choice | Speed | Fidelity |
|--------|-------|----------|
| SKU 3D | Slow | High |
| Carton | Medium | Medium |
| Pallet/layer | Fast | Good ops | **MVP lean** |

### Replan aggressiveness

| Choice | Util | Floor chaos |
|--------|------|-------------|
| Continuous | High | High |
| Until freeze | Balanced | **Prefer** |
| Once | Low churn | Missed hot freight |

## Operability Addenda

### Deploy pipeline

```text
scorer/constraint build → fixtures → shadow → canary FC → bake → fleet
```

### Guardrails

- Infeasible release = 0  
- Solver p99 budget  
- Util regression  
- Override spike  
- Execution match drop  

### Kill switches

1. Force greedy  
2. Disable replan  
3. Disable ML propose  
4. Lock freeze early  
5. Isolate FC  

## Worked Capacity Narrative

Trailers/day × CPU-s/plan → worker count × headroom; show prune reducing candidates 5× bends curve; 100× needs FC cells not one global solver.

## Customer-Trust / Safety Paragraph

Unsafe axle or hazmat mix is not an optimization miss—it is a safety incident. Validators are fail-closed. Overrides cannot bypass hard safety without elevated role + capture.

## Progressive Scale Recap

- **10×:** worker pool, pruning, greedy degrade  
- **100×:** FC cells, pallet hierarchy, plan caching  
- **1,000×:** network pregroup + learned proposers  

---

## Supplemental Depth Pack — Optimally Fill Truck

### S1. Feasibility gate

Hard validate before publish.
**Metric:** `infeasible_published=0`.

### S2. Time budget

Wall clock kills search.
**Metric:** `solver_deadline_hit_rate`.

### S3. Greedy fallback

Always available.
**Metric:** `fallback_plan_rate`.

### S4. Exclusion reasons

100% coverage.
**Metric:** `lines_missing_reason`.

### S5. Versioning

Monotonic plan versions.
**Metric:** `stale_exec_plan_version`.

### S6. Axle model

Zone moments enforced.
**Metric:** `axle_reject_count`.

### S7. Data quality

Dims trust score.
**Metric:** `missing_dims_rate`.

### S8. Unit economics

`$ / trailer` and util %.
**Metric:** cube/weight util dashboards.

## Scenario Runbooks

| Scenario | Action |
|----------|--------|
| Solver outage | Greedy mode; page optimizer |
| Mass bad dims | Conservative defaults; measure blitz |
| Yard trailer swap | Rebuild with new profile |
| Hazmat rule change | Config push; shadow; bake |
| Dock backlog | Earlier freeze; smaller plans |
| Util collapse | Check prune K; scorer weights; readiness |

## Rapid-Fire Q&A — Optimally Fill Truck

**Q:** Primary objective? **A:** Feasible util under constraints.  
**Q:** Algorithm? **A:** Greedy+local±bounded MIP.  
**Q:** Fallback? **A:** Greedy.  
**Q:** Freeze? **A:** Stop auto replan.  
**Q:** Axle? **A:** Hard validate.  
**Q:** Explain? **A:** Reason codes.  
**Q:** Shard key? **A:** FC.  
**Q:** 3D exact? **A:** Out of MVP path.  
**Q:** Hot freight? **A:** Before freeze admit.  
**Q:** Override? **A:** Audited.  
**Q:** Weigh-out? **A:** Density select.  
**Q:** Multi-stop? **A:** LIFO order.  
**Q:** Hazmat? **A:** Matrix.  
**Q:** Idempotent? **A:** Input digest.  
**Q:** Drift? **A:** Execution events.  
**Q:** ML role? **A:** Propose/predict not physics.  
**Q:** Deal-breaker? **A:** Unbounded MIP / no axle.  
**Q:** 10×? **A:** Workers+prune.  
**Q:** 100×? **A:** Cells+hierarchy.  
**Q:** Metric? **A:** Util + on-time + zero unsafe.  
**Q:** Knapsack? **A:** Subset select yes.  
**Q:** Bin pack? **A:** Arrangement yes.  
**Q:** CPU math? **A:** trailers×seconds.  
**Q:** Shadow? **A:** Yes before bake.  
**Q:** Cold chain? **A:** Compat constraints.  
**Q:** Who pages? **A:** Load plan oncall.  
**Q:** Empty plan? **A:** Fail loud.  
**Q:** Sorted inputs? **A:** Determinism.  
**Q:** Pallet aggregate? **A:** Tractability.  
**Q:** Route opt? **A:** Sibling system.  
**Q:** Safety override bypass? **A:** No.  
**Q:** Cutoff miss? **A:** Worse than -1% util.  
**Q:** Inventory lie? **A:** Exception workflow.  
**Q:** Container profile? **A:** Plugin.  
**Q:** GA? **A:** Optional in budget.  
**Q:** Must-include? **A:** Place first.  
**Q:** Cost lever? **A:** Prune+aggregate.  
**Q:** SEV unsafe load? **A:** Fail-closed culture.  
**Q:** Fixtures? **A:** Golden packs.  
**Q:** Version consume? **A:** Exec pins version.

## Narrative Walkthrough — Optimally Fill Truck

### Beat 1

Clarify fill truck ≠ route; list hard constraints first.

### Beat 2

Estimate trailers and CPU; show need for budgets.

### Beat 3

Draw candidate → constrain → optimize → validate → publish.

### Beat 4

Detail greedy+local search; fallback.

### Beat 5

Axle/hazmat/stack; exclusion reasons.

### Beat 6

Freeze/replan/execution feedback.

### Beat 7

Scale jumps; shadow deploy.

### Beat 8

Close: safety + on-time over paper optimality.

## Pre-Onsite Checklist — Optimally Fill Truck

- [ ] Constraints list from memory  
- [ ] Greedy+local+fallback story  
- [ ] Axle one-liner  
- [ ] Freeze semantics  
- [ ] Progressive scale  
- [ ] Deal-breakers  
- [ ] 60s closer  
- [ ] Difference vs routing doc  

### Extra drill

Write objective function with weights.

### Extra drill

Name 8 exclusion reason codes.

### Extra drill

CPU capacity narrative in 30s.

### Extra drill

Design validator tests.

### Extra drill

Explain pallet aggregation.

### Extra drill

Multi-stop LIFO example.

### Extra drill

Hazmat segregation example.

### Extra drill

Replan diff to reduce churn.

### Extra drill

Override RACI.

### Extra drill

Shadow mode metrics.

### Extra drill

Weigh-out lane strategy.

### Extra drill

Trailer profile plugin API.

### Extra drill

Deterministic seeding.

### Extra drill

Execution match dashboard.

### Extra drill

100× hierarchy pack.

### Extra drill

ML proposer boundary.

### Extra drill

Kill switch list.

### Extra drill

SEV for infeasible publish.

### Extra drill

Interview trap: pure MIP.

### Extra drill

60s closer memorization.

### Extra drill

Compare to classic knapsack.

### Extra drill

Dock adherence incentives.

### Extra drill

Cold chain aside.

### Extra drill

Yard swap replan.

### Extra drill

Input digest fields.

### Extra drill

Queue age SLO.

### Extra drill

Must-include placement order.

### Extra drill

Fragility risk term.

### Extra drill

Network pregroup at 1000×.

### Extra drill

Ownership two-pizza boundary.

---

*End of optimally fill truck system design.*
