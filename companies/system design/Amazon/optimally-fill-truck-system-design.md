# System Design: Optimally Fill a Truck

> **Focus areas:** Bin packing / 3D packing · Loading constraints · Multi-stop routing coupling · SLA & promise dates · Cost minimization · FC → trailer → sortation · Algorithmic + systems interview  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, Amazon logistics themes (customer promise, cost-to-serve, ownership), honest MVP vs extreme-scale paths

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

Goal: **bound the product**—what “fill a truck optimally” means when packages have dimensions/weight/hazmat, trailers have volume/axle/cube limits, stops impose LIFO/FIFO unload order, and Amazon must hit **customer promise** while minimizing **cost-to-serve** (miles, trailer count, labor, damage, missed SLAs).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is being packed? | Cartons/totes/pallets into trailers (53′ dry van, reefers, box trucks) | Unified **load unit** model: dims, weight, stackability, orientation rules |
| F2 | Optimal means? | Maximize cube/weight utilization subject to **SLA & route feasibility**; minimize total cost | Multi-objective: utilization ≠ sole objective |
| F3 | Single trailer or fleet? | Assign packages to trailers **and** sequence stops (VRP-lite coupling) | Packing + assignment + sequencing co-designed; not pure offline bin packing |
| F4 | 2D or 3D? | True **3D packing** with gravity/support; wall-building heuristics OK for MVP | Geometry engine + stability checks |
| F5 | Unload order? | Multi-stop: last-in-first-out by stop; avoid restacking | **Stop-aware packing** (zones / walls per stop) |
| F6 | Constraints? | Max weight, axle, hazmat segregation, crush limits, temperature, center of gravity | Constraint catalog + validators |
| F7 | When does packing run? | Wave planning (hours ahead), dock door assignment, dynamic replan on late packages | Batch solver + online delta reopt |
| F8 | Inputs available? | Package dims from FC, destination sort code, promise date/window, trailer type | Upstream contracts; missing dims → estimate + buffer |
| F9 | Output? | Load plan: package → trailer → (x,y,z,orientation) + load sequence + dock advice | Versioned plan artifact; scanner/WMS consume |
| F10 | Human override? | Dock leads can swap/reject; system must re-validate | Plan mutation API + audit |
| F11 | Failures? | Overweight, unstable stack, late wave cut, trailer swap | Feasibility gate; spillover trailers; SLA-priority spill |
| F12 | Cost model? | Trailer fixed cost, variable miles, labor minutes, damage risk, SLA penalty | Explicit score; configurable weights |
| F13 | Idempotency? | Wave re-runs, scanner retries | Plan version + idempotency keys |
| F14 | Cross-dock vs FC origin? | Both; same packing service with different topology | Topology-agnostic load planner service |
| F15 | Who owns? | Outbound transportation / middle-mile planning platform | Clear ownership; FC ops consume |

**MVP functional scope (lock with interviewer):**

1. Ingest **load units** (package/tote) with dims, weight, destination stop, promise timestamp, constraints tags.
2. Ingest **trailers** with capacity (volume, weight), type, scheduled depart, dock door.
3. **Assign** units to trailers under capacity + stop set constraints.
4. Produce **3D load plan** (heuristic wall-building) respecting stop unload order and basic stability.
5. **Score** plans: utilization, estimated labor, SLA risk, trailer count.
6. **Publish** plan to WMS/scanner; accept **ACK / deviation** events.
7. **Replan** on late adds/removes within cutoff (delta pack).
8. Ops APIs: freeze plan, force spillover trailer, mark trailer unavailable.

**Out of MVP (explicitly defer):**

- Perfect MILP global optimum for entire network every minute
- Full physics FEM for crush/damage
- Autonomous robotic trailer loading control loops
- Multi-modal (air/ocean) packing (different problem)
- Learning-based packing without human-auditable constraints

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Planning latency (wave)? | Minutes OK for batch; seconds for delta | Batch p99 < 5 min for 5K units; delta p99 < 30s |
| N2 | Correctness? | Never overload weight/hazmat; rare cube overshoot OK with buffer | Hard constraints vs soft objectives |
| N3 | Availability? | Planning can degrade; dock must not stall forever | Fallback greedy fill + human |
| N4 | Durability? | Accepted plan durable before dock executes | Plan store + event log |
| N5 | Throughput? | See scale table | Split **ingest**, **solve**, **publish**, **event** QPS |
| N6 | Multi-site? | Thousands of FC/sort centers | Per-site cells; no global single solver |
| N7 | Audit? | Why package on trailer A not B | Decision traces / feature dump |
| N8 | Safety? | Unstable loads → injury/damage | Stability gate; block publish if fail |
| N9 | Clock? | Depart times site-local | UTC + site TZ |
| N10 | Consistency | Plan vs physical | Version fencing; scanner validates plan_version |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Wave closes → solver assigns 2,000 packages across 3 trailers → 3D plans published → loaders scan in sequence → depart on time → SLA met.
2. Late package with tight promise → delta reopt inserts into trailer with same stop wall if cube allows; else spillover.
3. Hazmat + food segregation → constraint engine rejects co-load; second trailer opened.
4. Dock lead swaps two boxes → mutation API re-validates geometry/weight → new plan version.
5. Trailer cancelled → reassign packages to alternate with SLA-aware priority.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Missing dims | Use ASIN statistical dims + 10% buffer; flag low confidence |
| Dims wrong at dock | Scan event → reject placement → replan remainder |
| Weight near axle limit | Axle model; prefer heavy forward/aft per trailer type rules |
| Stop order conflict with cube | Leave intentional void / partial wall; cost vs restack tradeoff |
| Solver timeout | Return best incumbent + greedy completion; mark quality=HEURISTIC |
| Duplicate wave submit | Idempotency → same plan_id |
| Package cancelled after plan | Tombstone unit; fill hole optionally online |
| Extreme SKU (couch) | Special handling lane / flatbed path; exclude from dry-van 3D |
| Clock skew on cutoff | Server cutoff timestamp; site wall clock for human UX only |
| Two solvers publish | Fence with plan epoch; only higher epoch accepted |
| Network partition to WMS | Local plan cache at site; sync when healed |
| Prime Day spike | Cap solve concurrency; prioritize SLA-risk packages first |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Sites (FC/sort) | 100 | 500 | 2K | 10K |
| Trailers planned / day | 20K | 200K | 2M | 20M |
| Packages planned / day | 20M | 200M | 2B | 20B |
| Peak **ingest** events/s | 2K | 20K | 200K | 2M |
| Peak **solve jobs**/s | 20 | 200 | 2K | 20K |
| Avg packages / trailer | 800 | 900 | 1K | 1.2K |
| Concurrent active waves | 500 | 5K | 50K | 500K |
| Geos / countries | 5 | 10 | 20 | 30+ |
| Solver CPU cores (fleet) | 500 | 5K | 50K | 500K |

**What each jump forces:**

- **10×:** Per-site sharding; async solve workers; plan object store; stop treating solver as request/response monolith.
- **100×:** Regional cells; GPU/CPU fleets for geometry; incumbent caching; package clustering before 3D; SLA-risk pre-sort.
- **1,000×:** Hierarchical planning (network → site → door); approximate packing for quote; exact 3D only near dock; learned priors for wall patterns; hard multi-tenant isolation per site.

### 1.5 Etc. (Constraints & Assumptions)

- Map/distance service exists for stop sequencing cost (or use sort codes / lane miles tables).
- Promise engine provides `promise_by` per package.
- Physical loading still human/robot; we produce **plans**, not motor control.
- Single cloud, multi-AZ; site edge cache for dock UX.
- Algorithmic interview may ask you to code **FFD / wall-building / score** on a whiteboard—systems design must leave hooks for that.

**Scope statement:**

> Design Amazon middle-mile / outbound **truck fill optimization**: assign and 3D-pack load units into trailers under capacity, hazmat, stability, and multi-stop unload constraints while minimizing cost-to-serve and protecting customer promise—baseline ~20M packages/day / 100 sites scaling through 10× / 100× / 1,000× with sharded site planners and progressive approximation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 1,000× | Latency | Notes |
|-------|------|----------|--------|---------|-------|
| **Unit ingest** | Package ready events | 2K/s | 2M/s | Soft real-time | Kafka by site |
| **Wave close / solve** | Batch optimization jobs | 20/s | 20K/s | Minutes | CPU heavy |
| **Delta reopt** | Late add/remove | 50/s | 50K/s | Seconds | Hot path near cutoff |
| **Plan publish** | Push to WMS | 20/s | 20K/s | Seconds | Durable |
| **Dock scan events** | Load/validate | 1K/s | 1M/s | Soft RT | Idempotent |
| **Override / mutation** | Human edits | 5/s | 5K/s | Interactive | Audit |

**Anti-pattern:** one “packing API QPS” that mixes scans with MILP solves.

### 2.2 Trailer & cube math

```text
53′ dry van approximate internal:
L ≈ 16.0 m, W ≈ 2.5 m, H ≈ 2.7 m
Volume ≈ 16 × 2.5 × 2.7 ≈ 108 m³ ≈ 3,800 ft³

Avg carton 0.04 m³ (example) → theoretical 108/0.04 = 2,700 cartons
Practical cube util 70–85% + weight limit → often ~800–1,500 units
Use 1,000 packages/trailer as planning average

Baseline: 20K trailers/day × 1,000 = 20M packages/day ✓
```

### 2.3 Solver compute

```text
Naive 3D exact pack is NP-hard; heuristics:
Wall-building ~ O(n log n + n × walls) 
For n=1,000 packages: ~10–200 ms CPU for greedy walls (good impl)
With metaheuristics / SA: 1–30 seconds per trailer
Wave of 5 trailers: seconds to a minute

Baseline peak 20 solves/s × 10 CPU-sec = 200 CPU-sec/s → ~200 cores busy
10×: ~2K cores; 100×: ~20K; 1000×: ~200K cores → must approximate + cache + hierarchy
```

**Critical insight:** At 1,000× you cannot run heavy metaheuristics for every trailer every minute. Split:

1. **Network/lane assignment** (coarse, frequent)
2. **Trailer assignment** (medium)
3. **3D geometry** (fine, near dock, cached patterns)

### 2.4 Storage

```text
Package planning row ~500 B
20M/day × 7 days hot = 140M × 500 B ≈ 70 GB

1,000×: 20B/day × 7 × 500 B ≈ 70 TB hot metadata
Plan geometry: 1,000 placements × 64 B ≈ 64 KB/trailer
20K trailers/day × 64 KB ≈ 1.3 TB/day plans → object store + metadata pointer

Events: 2–5 scans/package × 200 B
20M × 3 × 200 B ≈ 12 GB/day baseline
1,000× → 12 TB/day event stream — Kafka + cold archive
```

**Unit check:** 20B packages/day × 500 B = 10 TB/day metadata, not PB. Correct: 20e9 × 500 = 1e13 B = **10 TB/day**.

### 2.5 Cost function sketch

```text
cost(plan) =
  w_trailer * num_trailers
+ w_cube * (1 - cube_util)   # underfill penalty
+ w_weight * overweight_soft  # soft; hard reject if > max
+ w_sla * sum(risk_miss(promise_i))
+ w_labor * estimated_load_minutes
+ w_damage * instability_score
+ w_miles * lane_miles(trailer)
+ w_restack * expected_restacks
```

Interview tip: write this on the board early—shows you are not optimizing cube alone.

### 2.6 Bandwidth

```text
Scan event 300 B × 1M/s at 1000× ≈ 300 MB/s — fine with partitioned Kafka
Plan publish 64 KB × 20K/s ≈ 1.28 GB/s — bursty; use object URLs not inline everywhere
```

---

## 3. High-Level Design

### 3.1 Core entities

| Entity | Key fields | Owner |
|--------|------------|-------|
| LoadUnit | unit_id, dims, weight, stop_id, promise_by, tags, confidence | Ingest |
| Trailer | trailer_id, type, capacities, depart_at, dock_id, site_id | Fleet |
| Stop | stop_id, sequence_hint, geo/sort_code | Routing |
| Wave | wave_id, site_id, cutoff_at, state | Planning |
| LoadPlan | plan_id, trailer_id, version, placements[], score, epoch | Planner |
| Placement | unit_id, pose (x,y,z,orient), wall_id, seq | Geometry |
| Constraint | rule_id, hard/soft, predicate | Policy |

### 3.2 Service map (MVP → scale)

| Service | Responsibility | Scale evolution |
|---------|----------------|-----------------|
| Ingest Gateway | Validate units/trailers; idempotent write | Kafka producers per site |
| Unit Store | Hot metadata for open waves | Dynamo/Cassandra by site |
| Wave Orchestrator | Cutoff, freeze, trigger solve | Per-site shard |
| Assignment Solver | Units → trailers (VRP-lite) | Worker fleet |
| Geometry Solver | 3D pack per trailer | CPU pool; pattern cache |
| Constraint Engine | Hard/soft validation | Library + service |
| Plan Store | Versioned plans + fence epoch | Object + DB |
| Publish Adapter | WMS / scanner / dock UI | Site edge |
| Event Applicator | Scan/deviation → state | Idempotent consumers |
| Reopt Service | Delta inserts/removes | Priority queue |
| Score / Cost Service | Evaluate objectives | Shared lib |
| Ops Control Plane | Freeze, spillover, kill switch | Audit |

### 3.3 End-to-end flow

```text
FC scan "packed" → Unit Ingest → Wave bucket
                     │
Wave cutoff ─────────┼──► Assignment Solver ──► Geometry Solver
                     │            │                    │
                     │            ▼                    ▼
                     │      Trailer loads         Placements
                     │            └────────┬─────────┘
                     │                     ▼
                     │              Constraint Engine
                     │                     │
                     │              Plan Store (vN)
                     │                     │
                     ▼                     ▼
              Dock UI / WMS ◄────── Publish
                     │
              Scan events ──► Event Applicator ──► (optional) Reopt
```

### 3.4 Algorithmic module (interview hook)

Expose packing as a **pure function** for unit tests / whiteboard:

```text
pack(trailer, units_sorted_by_stop_desc, constraints) -> (placements, score) | Infeasible
```

Suggested MVP heuristic pipeline:

1. Cluster units by stop; order stops reverse of unload (LIFO).
2. Within stop: sort by volume descending (FFD flavor).
3. Wall-build along length; respect max height/weight per column.
4. Stability: each unit needs support ratio ≥ threshold.
5. Local search: swap within stop walls to improve cube (time-boxed).

### 3.5 Consistency model

- **Site is the consistency boundary.** No cross-site transactions.
- Plan publish uses **monotonic epoch** per trailer.
- Physical world is source of truth at dock; system reconciles via scans.
- Soft real-time: planning eventual; **safety constraints** must pass before ACK publish.

### 3.6 Progressive architecture summary

| Scale | Architecture |
|-------|--------------|
| 1× | Per-site planner monolith + Postgres + Redis; heuristic packer |
| 10× | Kafka ingest; solve workers; S3 plans; Dynamo unit store |
| 100× | Regional cells; pattern library; two-stage assign→pack; SLA risk index |
| 1000× | Hierarchical network planner; approximate quotes; site actors; learned wall priors |

---

## 4. Architecture Diagram

### 4.1 Logical architecture

```text
                    ┌─────────────────────────────────────────┐
                    │           Control Plane (Ops)           │
                    │  freeze · spillover · weights · kill    │
                    └───────────────────┬─────────────────────┘
                                        │
   FC/WMS ──events──►┌──────────────┐   │   ┌────────────────┐
                     │ Ingest GW    │───┼──►│ Unit / Trailer │
                     └──────┬───────┘   │   │    Stores      │
                            │           │   └────────┬───────┘
                            ▼           │            │
                     ┌──────────────┐   │            │
                     │ Wave Orch    │◄──┘            │
                     └──────┬───────┘                │
                            │ jobs                   │
              ┌─────────────┼─────────────┐          │
              ▼             ▼             ▼          │
        ┌──────────┐ ┌──────────┐ ┌────────────┐    │
        │ Assign   │ │ Geometry │ │ Constraint │    │
        │ Workers  │ │ Workers  │ │  Engine    │    │
        └────┬─────┘ └────┬─────┘ └─────┬──────┘    │
             └────────────┼─────────────┘           │
                          ▼                         │
                   ┌─────────────┐                  │
                   │ Plan Store  │◄─────────────────┘
                   │ + Epoch     │
                   └──────┬──────┘
                          │ publish
                          ▼
                   ┌─────────────┐     scans      ┌─────────────┐
                   │ Site Edge   │◄──────────────►│ Event Apply │
                   │ WMS/Dock UI │                └──────┬──────┘
                   └─────────────┘                       │
                                                         ▼
                                                  ┌─────────────┐
                                                  │ Reopt Queue │
                                                  └─────────────┘
```

### 4.2 Site cell diagram

```text
                Region Cell
        ┌──────────────────────────┐
        │  Site Shard Map          │
        │  site_id → planner cell  │
        └────────────┬─────────────┘
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼
  Site A          Site B           Site C
  (actor/DB)      (actor/DB)       (actor/DB)
  local solve     local solve      local solve
  local dock      local dock       local dock
```

### 4.3 Plan state machine

```text
DRAFT → SOLVING → FEASIBLE → PUBLISHED → LOADING → CLOSED
                 ↘ INFEASIBLE → (spillover / split) → SOLVING
PUBLISHED → SUPERSEDED (new epoch)
LOADING → DEVIATED → REOPT → PUBLISHED'
```

### 4.4 Data flow for delta reopt

```text
Late unit U for trailer T (plan epoch e)
  1. Check cutoff & trailer not CLOSED
  2. Try insert into stop wall of U (geometry delta)
  3. If fail → try other open trailers same lane
  4. If fail → open spillover trailer (costly)
  5. Publish epoch e+1; fence scanners on e
```

---

## 5. Design Deep Dive

### 5.1 Why this is both algo + systems

Amazon interviewers often start with “how would you pack boxes into a truck?” (FFD, shelf, guillotine, SA) then pivot to “now do this for every FC every day.” Your design must:

- Keep **algorithms pure and testable**
- Put **orchestration, fencing, scale, and ops** around them
- Make **SLA/cost** first-class—not afterthoughts

### 5.2 Constraint taxonomy

| Type | Examples | Enforcement |
|------|----------|-------------|
| Hard capacity | Max kg, max m³ | Reject plan |
| Hard safety | Hazmat segregation, unstable support | Reject publish |
| Hard process | Stop LIFO zones | Reject or restack flag |
| Soft objective | Cube util, labor | Score only |
| Soft SLA | Promise risk | Score + priority in assign |

Never let soft objectives violate hard constraints in publish path.

### 5.3 Assignment before geometry

Two-stage beats joint MILP at scale:

```text
Stage A: Set-partition / greedy assign
  - Group by destination lane / sort code
  - Bin-pack by volume+weight into trailer slots (1D/2D aggregate)
  - Respect depart windows & dock capacity

Stage B: Per-trailer 3D
  - Only units already assigned
  - Expensive geometry isolated
```

If Stage B fails feasibility, return units to Stage A (feedback loop, bounded iterations).

### 5.4 Stop-aware 3D packing

```text
Stops unload order: S1 (first unload), S2, S3 (last unload)
Load order (LIFO): pack S3 walls first (nose), then S2, then S1 (near door)

Trailer length axis x from nose(0) to door(L):
  [ WALL_S3 | WALL_S2 | WALL_S1 ]
```

Within a wall: columns/stack with support checks. Allow **intentional voids** if next stop needs access—cost them.

### 5.5 Stability model (MVP)

```text
support_ratio(unit) = supported_base_area / base_area
require support_ratio >= 0.7 (configurable)
forbid floating corners; limit overhang
optional: cog height / trailer width for tip risk
```

Good enough for interview; mention FEA as non-goal.

### 5.6 SLA coupling

```text
risk_miss(unit) ≈ f(time_to_promise, lane_transit_p95, buffer)
Priority key for assignment:
  sort by risk_miss DESC, then volume DESC
Never leave high-risk units to “next wave” if capacity exists.
```

Spillover trailer decision:

```text
if sla_penalty_saved > trailer_fixed_cost + expected_miles_cost:
    open spillover
```

### 5.7 Idempotency & fencing

| Mechanism | Use |
|-----------|-----|
| `idempotency_key` on wave solve | Avoid duplicate plans |
| `plan_epoch` per trailer | Scanners reject stale |
| Conditional writes on unit.assigned_trailer | Prevent double assign |
| Solver lease on wave_id | One active solver |

```text
CAS: unit.plan_version = v → v+1 only if still in wave and not CANCELLED
```

### 5.8 Reoptimization strategies

| Trigger | Strategy |
|---------|----------|
| +1 late unit | Delta insert |
| −1 cancel | Mark hole; optional compact if time |
| Trailer breakdown | Full reassign subset |
| Massive surge | Freeze low-priority; SLA-only mode |

Bound reopt frequency (e.g. max 1 publish / trailer / 30s) to avoid thrash.

### 5.9 Pattern cache (100×+)

Many trailers look similar (same stop set, similar SKU mix). Cache:

```text
pattern_key = hash(sorted stop_ids, trailer_type, size_histogram_bucket)
→ prior wall layout skeleton
```

Warm-start geometry; often 5–20× faster.

### 5.10 Storage design

```text
DynamoDB Units
  PK: SITE#<site_id>
  SK: UNIT#<unit_id>
  GSI1: WAVE#<wave_id> → units
  attrs: dims, weight, stop, promise, state, trailer_id, plan_version

DynamoDB Plans
  PK: TRAILER#<trailer_id>
  SK: PLAN#<epoch>
  attrs: s3_uri, score, state, wave_id, hash

S3: s3://plans/<site>/<trailer>/<epoch>.pb  (placements)
```

### 5.11 Event application

```text
Scan LOAD unit U on trailer T at pose P
  if plan_epoch_scanner < current: reject STALE
  if U not in plan: DEVIATION path
  else mark LOADED; idempotent by scan_id
```

Deviations feed quality metrics (dims error rate) and may trigger partial reopt.

### 5.12 Multi-region / multi-geo

- Planning **home** = site’s region.
- Cross-region only for analytics and network-level lane balancing (separate system).
- DR: site can run **degraded local greedy** offline if region control plane dies.

### 5.13 Security & safety

- Authz: only site ops mutate plans for their site.
- Hazmat rules from compliance service; cannot be overridden without dual control.
- Audit every publish/override.
- PII minimal (addresses hashed to stop_ids).

### 5.14 Observability

| Signal | Why |
|--------|-----|
| Cube util / weight util | Efficiency |
| SLA risk units left behind | Customer |
| Solver time & incumbent gap | Algo health |
| Deviation rate | Dims / process |
| Publish thrash (epochs/hour) | Reopt too hot |
| Spillover trailer rate | Cost |

Trace id: `wave_id` / `trailer_id` / `plan_epoch` / `unit_id`.

### 5.15 Failure modes & degradation

| Failure | Degradation |
|---------|-------------|
| Geometry workers down | Publish assignment-only with human pack | 
| Kafka lag | Buffer; delay cutoff |
| Constraint service down | Fail closed on hazmat; fail open on soft scores |
| Clock wrong at site | Use server cutoff; alert |

### 5.16 Testing strategy

- Property: never exceed weight; support_ratio invariant.
- Golden loads: known trailer fixtures.
- Fuzz random dims with seed.
- Chaos: kill solver mid-wave → lease reclaim → one plan.
- Load: 10K unit wave solve latency SLO.

### 5.17 Team / ownership boundaries

| Team | Owns |
|------|------|
| Planning Platform | APIs, stores, fencing, scale |
| Packing Science | Algorithms, scores, patterns |
| Site Ops | Overrides, dock execution |
| Promise | promise_by inputs |
| Transportation | Trailer supply & lanes |

Amazon LP: **Disagree and commit** on score weights; **Dive deep** on deviation spikes; **Deliver results** measured in cost-to-serve & missed promises.

### 5.18 Interview coding companion

Be ready to implement:

```text
bool canPlace(box, position, occupied_voxels_or_skyline)
List<Placement> wallBuild(boxes, trailer)
double score(plan)
```

Then zoom out: “At Amazon scale this function runs in workers keyed by site…”

### 5.19 Cost vs utilization tension (explicit)

```text
100% cube with 5% SLA miss → BAD
90% cube with 0.1% SLA miss → GOOD
Opening trailer at 55% cube to save SLA → often GOOD near cutoff
```

Document this tradeoff in design review; executives optimize dollars + CX, not cube vanity metrics.

### 5.20 10× / 100× / 1,000× deep changes

**10×**

- Shard by `site_id`
- Async solve via queue
- S3 plan blobs
- Basic pattern cache

**100×**

- Two-stage assign/pack
- SLA risk index (Redis)
- Regional cell routing
- Solver auto-scale on wave calendar
- Continuous dim-error learning → confidence

**1,000×**

- Network hierarchical planner sets trailer budgets
- Approximate packing for early waves; refine near dock
- Site-level actors (single writer per trailer)
- Precomputed wall templates by commodity class
- Spillover exchanges across doors via market-like internal auction (optional)

---

## 6. Wrap-Up

### 6.1 What we designed

A **site-sharded truck fill platform** that:

1. Ingests load units and trailers into waves  
2. Assigns under capacity/lane/SLA constraints  
3. 3D-packs with stop-aware walls and stability gates  
4. Publishes fenced plan epochs to dock/WMS  
5. Reopts on deviations with cost-aware spillover  
6. Scales from tens of millions to tens of billions of packages/day via hierarchy and approximation  

### 6.2 Key tradeoffs

| Tradeoff | Choice | Why |
|----------|--------|-----|
| Exact MILP vs heuristics | Heuristics + time-boxed search | NP-hard; dock clocks |
| Joint vs two-stage | Two-stage assign→pack | Scale + feedback |
| Cube vs SLA | SLA-weighted cost | Amazon CX |
| Global vs site cell | Site cell | Consistency & blast radius |
| Eager 3D vs late refine | Late refine at 1000× | CPU economics |

### 6.3 MVP → path

Ship greedy assign + wall-build + hard constraints + plan epochs. Add pattern cache, SLA risk, hierarchical planning as scale bites.

### 6.4 Risks

| Risk | Mitigation |
|------|------------|
| Bad dims | Confidence buffers; scan feedback loop |
| Solver thrash | Epoch rate limits |
| Unsafe publish | Hard gate stability/hazmat |
| Org score fights | Versioned weight configs + experiments |

---

## 7. Deeper / Related Interview Questions

### 7.1 Problem framing

**Q: Is this bin packing or VRP?**  
A: Both—capacity packing + stop sequencing/unload order. Pure bin packing ignores door/LIFO and SLA.

**Q: Optimize cube or cost?**  
A: Cost-to-serve including SLA penalties; cube is a proxy component.

**Q: Online or offline?**  
A: Mostly wave-offline with online delta near cutoff.

**Q: What is the hard real-time boundary?**  
A: Dock safety validation & epoch fencing—not the batch MILP.

**Q: How is this different from container loading literature?**  
A: Production needs ops overrides, dims error, multi-stop Amazon network, promise coupling, and massive multi-site scale.

### 7.2 Algorithms

**Q: Why First-Fit Decreasing?**  
A: Strong 1D baseline; for 3D use as ordering prior inside walls.

**Q: Guillotine vs skyline vs wall-building?**  
A: Wall-building maps cleanly to multi-stop LIFO; skyline good for single-stop; guillotine for cutting stock—pick and justify.

**Q: How to handle rotations?**  
A: Discrete allowed orientations per SKU (usually 2–6); don’t search continuous SO(3).

**Q: Exact solver role?**  
A: Small trailers / high-value loads; time-boxed MIP on residual after heuristic.

**Q: Local search moves?**  
A: Swap within stop, translate along wall, reassign overflow unit to neighbor trailer.

**Q: Complexity class?**  
A: 3D bin packing NP-hard; interview expects heuristics + complexity honesty.

**Q: How to test packing quality?**  
A: Cube/weight util, infeasibility rate, SLA miss, deviation, vs human plans.

**Q: Reinforcement learning for packing?**  
A: Possible at 100×+ for warm starts; keep constraint validator authoritative.

### 7.3 Constraints & safety

**Q: Hazmat with food?**  
A: Hard segregation rules; fail closed if compliance service unavailable.

**Q: Axle weight?**  
A: Segment trailer length; estimate weight distribution; reject if axle exceeded.

**Q: Crushable items?**  
A: Stackability class; “do not stack” flag; limit column pressure.

**Q: Center of gravity?**  
A: Soft score + hard max height for top-heavy SKUs.

**Q: Unstable plan published—whose fault?**  
A: Geometry validator bug → packing platform page; override without validate → ops process gap.

### 7.4 Systems & scale

**Q: One global planner DB?**  
A: No—site shards / cells.

**Q: 2M ingest/s architecture?**  
A: Kafka partitions by site_id; unit store write fanout; backpressure waves.

**Q: Solver fleet scheduling?**  
A: Priority queue by cutoff proximity & SLA risk; autoscale on queue age.

**Q: How to avoid double assignment?**  
A: Conditional writes / single-writer actor per wave or unit.

**Q: Plan thrashing near cutoff?**  
A: Min interval between epochs; freeze window; only SLA-critical deltas.

**Q: Multi-region active-active plans for one site?**  
A: No—single home region writer per site.

**Q: Site offline from region?**  
A: Edge greedy packer; reconcile later; accept suboptimal cube.

### 7.5 SLA & cost

**Q: Package will miss promise unless new trailer—do it?**  
A: Compare spillover cost vs SLA penalty / CX; usually yes for Prime critical near miss.

**Q: How quantify SLA risk?**  
A: Transit time distributions + cutoff slack; not binary.

**Q: Underfill intentional?**  
A: Yes—service out a stop early or protect unload access.

**Q: Cost weights who sets?**  
A: Science + finance; platform enforces schema & experiments.

### 7.6 Data & dims

**Q: Missing dimensions?**  
A: Statistical ASIN dims + buffer; lower confidence increases void padding.

**Q: Systematic dim bias?**  
A: Feedback from scanner / cube sensors; recalibrate catalog.

**Q: Unit of measure bugs (in vs cm)?**  
A: Canonical mm + validation ranges; reject absurd dims.

### 7.7 APIs

**Q: Idempotent solve API shape?**  
A: `POST /waves/{id}/solve` with `Idempotency-Key`; returns `plan_set_id`.

**Q: Mutation API?**  
A: `POST /trailers/{id}/plans/{epoch}/mutate` with ops auth; produces epoch+1.

**Q: Read plan for scanner?**  
A: `GET /trailers/{id}/active-plan` → epoch + signed URL to placements.

### 7.8 Consistency & fencing

**Q: Scanner has epoch 5, server 7?**  
A: Reject; force refresh; do not load against stale geometry.

**Q: Two publishes race?**  
A: Conditional epoch increment; loser discarded.

**Q: Exactly-once scans?**  
A: Idempotency on `scan_id`; at-least-once delivery OK.

### 7.9 Observability drills

**Q: Debug sudden cube util drop?**  
A: Dim confidence, new constraint, stop mix change, solver timeout → greedy, weight binding.

**Q: Debug SLA misses despite open cube?**  
A: Assignment priority bug; wrong promise; lane transit model; freeze too early.

**Q: Debug hazmat incident?**  
A: Trace constraint versions; override audit; data tag missing on unit.

### 7.10 Comparisons

**Q: vs classic bin packing homework?**  
A: Same core; plus stops, SLA, ops, fencing, multi-site, bad data.

**Q: vs airline cargo loaders?**  
A: Similar stability/weight; Amazon has huge SKU diversity & last-mile promise coupling.

**Q: vs warehouse slotting?**  
A: Slotting is storage; this is transport loading with depart clocks.

**Q: vs last-mile van packing?**  
A: Same family; van has tighter multi-stop and dynamic reopt (see related designs).

### 7.11 Reliability

**Q: Solver OOM on weird wave?**  
A: Isolate; mark wave degraded; greedy fallback; size limits.

**Q: Poison unit crashes geometry?**  
A: Sandbox; per-unit try/catch; quarantine SKU.

**Q: Kafka replay storm?**  
A: Idempotent applicators; compact unit state.

### 7.12 Security & abuse

**Q: Malicious override to overload trailer?**  
A: Hard constraints still enforced; dual-control for force-publish unsafe.

**Q: Enumerate plans across sites?**  
A: Authz site scope; UUIDs.

### 7.13 Org / LP

**Q: Science wants 30-min SA, ops needs 2-min?**  
A: Time-boxed anytime algorithm; publish incumbent; A/B quality vs delay.

**Q: Who is paged on Prime Day packing backlog?**  
A: Planning platform for queue lag; science if quality cliff; site ops if labor.

### 7.14 Arithmetic traps

**Q: 20B pkgs/day × 500 B = ?**  
A: 10 TB/day metadata.

**Q: 20 solves/s × 10 CPU-s = ?**  
A: 200 cores busy (plus overhead).

**Q: 53′ van volume order of magnitude?**  
A: ~100 m³ / ~3,800 ft³.

**Q: Claiming 99% cube every trailer?**  
A: Unrealistic with multi-stop + weight + dims error—challenge it.

### 7.15 Dynamic reopt specifics

**Q: Insert into packed wall without reshuffle?**  
A: Find residual free spaces (skyline holes); else reshuffle within stop if time.

**Q: Compact after cancel?**  
A: Optional; often leave hole if near depart.

**Q: Batch deltas?**  
A: Micro-batch 5–10s to reduce epochs.

### 7.16 Map / routing coupling

**Q: Do we compute road routes here?**  
A: Consume lane miles / stop sequence from transportation; don’t rebuild Google Maps inside packer.

**Q: Stop sequence unknown?**  
A: Use sort code geography heuristics; refine when route frozen.

### 7.17 Edge compute

**Q: Why site edge?**  
A: Dock UX latency; survive WAN blip; local scan validation.

**Q: How sync edge?**  
A: Active plan snapshot + epoch; event upload async.

### 7.18 Future / 1,000×

**Q: What breaks first at 1000×?**  
A: Solver CPU and global coordination fantasies—force hierarchy & approximation.

**Q: Market-based trailer opening?**  
A: Internal shadow price for spillover; optional advanced cost control.

**Q: Digital twin?**  
A: Useful for sim; not required for online publish path.

### 7.19 Cross-problem links

**Q: Relation to locker capacity?**  
A: Both allocate scarce physical capacity under promise dates with soft/hard holds—different geometry.

**Q: Relation to last-mile route optimization?**  
A: Downstream; van packing is sibling problem with more dynamic stops.

### 7.20 Closing probe

**Q: If you had one more week before peak?**  
A: Freeze window tuning, SLA priority sort, pattern cache for top lanes, spillover autoscale, dim confidence buffers—not a new MILP solver rewrite.

---

## 8. Appendices

### 8.1 Schema sketches

```text
DynamoDB Units
  PK: SITE#<site_id>
  SK: UNIT#<unit_id>
  attrs: l,w,h,mm, weight_g, stop_id, promise_by, tags[],
         state, wave_id, trailer_id, confidence, version, idem_key

DynamoDB Trailers
  PK: SITE#<site_id>
  SK: TRAILER#<trailer_id>
  attrs: type, max_kg, max_m3, depart_at, dock_id, state, active_epoch

DynamoDB Waves
  PK: SITE#<site_id>
  SK: WAVE#<wave_id>
  attrs: cutoff_at, state, solver_lease, stats

S3 PlanBlob
  placements: [{unit_id, x,y,z, orient, wall_id, seq}]
  score: {...}
  constraints_hash: ...
```

```sql
-- policy / catalog
trailer_types(type_id, l,w,h, max_kg, axle_json)
constraint_rules(rule_id, hard bool, expr_json, version)
score_weights(config_id, weights_json, status)
```

### 8.2 State machines

```text
Unit:  READY → ASSIGNED → PLANNED → LOADED → DEPARTED
                 ↘ CANCELLED
                 ↘ SPILLED → ASSIGNED

Wave:  OPEN → FROZEN → SOLVING → PUBLISHED → CLOSED
Plan:  DRAFT → FEASIBLE → PUBLISHED → SUPERSEDED / CLOSED
```

### 8.3 Invariants

| Invariant | Assert |
|-----------|--------|
| Weight | sum(loaded) ≤ max_kg |
| Volume soft | sum(vol) ≤ max_m3 × buffer |
| Single assign | unit on ≤1 active trailer |
| Epoch monotonic | trailer epochs increase |
| Hazmat | no forbidden pairs co-loaded |
| Support | each placement support_ratio ≥ θ |
| Stop zones | unload order respected in x-order |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Wave assign, wall-build, hard constraints, plan publish |
| 10× | Site shard, async workers, S3 plans, scan idempotency |
| 100× | Two-stage, SLA risk, pattern cache, regional cells |
| 1000× | Hierarchy, approx early pack, site actors, learned priors |

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| Load unit | Package/tote/pallet being planned |
| Wave | Batch of units with shared cutoff |
| Wall | Contiguous load section for a stop |
| Epoch | Monotonic plan version per trailer |
| Spillover | Extra trailer opened for feasibility/SLA |
| Cube util | Used volume / trailer volume |
| Cost-to-serve | Fully loaded logistics cost incl. SLA |
| LIFO | Last loaded near door unloaded first |

### 8.6 Estimation cheat-sheet

```text
Packages/day ≈ trailers/day × pkgs/trailer
Solver cores ≈ solves/s × cpu_sec_per_solve
Hot metadata ≈ pkgs/day × days × bytes/row
Plan bytes/day ≈ trailers/day × placements × bytes/placement
```

### 8.7 Sample cost weights (illustrative)

```text
w_trailer = 400     # $ fixed
w_miles = 2.0       # $/mile
w_sla = 50          # $/expected miss
w_labor = 0.8       # $/minute
w_damage = 100      # $/risk unit
w_cube = 20         # underfill penalty
```

### 8.8 API sketch

```text
POST /v1/sites/{site}/units          # ingest
POST /v1/sites/{site}/waves/{id}/close
POST /v1/sites/{site}/waves/{id}/solve
GET  /v1/trailers/{id}/plan
POST /v1/trailers/{id}/plan/mutate
POST /v1/scans                       # dock events
POST /v1/trailers/{id}/reopt
```

### 8.9 Decision log (interview)

| Decision | Options | Pick | Rationale |
|----------|---------|------|-----------|
| Packing model | Exact MIP / Heuristic / RL | Heuristic + optional MIP residual | Latency |
| Consistency | Global / Site | Site | Scale |
| Objective | Max cube / Min cost | Min cost w/ SLA | Amazon |
| Reopt | Continuous / Windowed | Windowed epochs | Stability |
| Dims | Trust catalog / Sense | Catalog + confidence + feedback | Reality |

### 8.10 Related Amazon systems

- Promise engine (inputs)
- Transportation management (lanes, trailer supply)
- WMS / warehouse execution
- Last-mile route optimization (downstream)
- Damage / claims analytics (feedback)

### 8.11 Whiteboard packing pseudocode

```text
function wallBuild(trailer, stops_desc, units_by_stop):
  x = 0
  placements = []
  for stop in stops_desc:  # pack last unload first
    wall_units = sort_volume_desc(units_by_stop[stop])
    cursor = new Skyline(trailer.w, trailer.h)
    for u in wall_units:
      pose = cursor.findPosition(u)
      if pose is null: return Infeasible or spill u
      if not stable(pose, placements): try next pose
      placements.add(u, pose, stop)
      cursor.occupy(pose, u)
    x += wall_thickness(cursor)
    if x > trailer.l: return Infeasible
  return placements
```

### 8.12 Risks register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Dim errors | High | Med | Buffers, feedback |
| Solver timeout | Med | Med | Anytime incumbent |
| Override unsafe | Low | High | Hard gates |
| Thrash epochs | Med | Med | Rate limit |
| Regional outage | Low | High | Edge greedy |

### 8.13 SLO examples

| SLO | Target |
|-----|--------|
| Wave solve before cutoff | 99% complete ≥ 10 min before depart |
| Delta reopt | p99 < 30s |
| Stale plan load attempts | < 0.1% |
| Hard constraint violations published | **0** |
| SLA-priority left-behind with open capacity | < 0.01% |

### 8.14 Amazon interview narrative (2 minutes)

> “I’d treat optimally filling a truck as a **cost-and-SLA constrained packing system**, not a puzzle to max cube. We shard by site, batch into waves, assign to trailers with promise-aware priority, then run stop-aware 3D wall-building with hard safety gates. Plans publish with epochs so docks never use stale geometry. At scale we split assignment from geometry, cache patterns, and eventually add hierarchical network planning—because 1,000× is a CPU and coordination problem as much as an algorithm problem.”

### 8.15 Checkpoint questions for yourself

1. Did I separate hard vs soft constraints?  
2. Did I couple packing to unload order & SLA?  
3. Did I shard by site?  
4. Did I fence plan versions?  
5. Did my math units check out?  
6. Did I give a degradation path?  

### 8.16 Optional extensions

- Robotic loader interface (pose stream)
- Carbon cost in objective
- Cross-dock adjacency packing
- Live cube scanning digital twin
- Multi-trailer door scheduling co-optimization

---

*End of document — Optimally Fill a Truck (Amazon SDE III system design)*
