# System Design: Robot Room Exploration & Mapping

> **Focus areas:** Occupancy grids · Frontier exploration · SLAM-lite · Multi-robot coordination · Cloud vs on-device · Map storage/versioning · Path planning · Localization uncertainty · Coverage completeness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit sensing→map→plan loop, correct grid/memory arithmetic, cloud/edge authority model, deal-breakers for “perfect global SLAM at Wi‑Fi dropout” fantasies  
> **Interview theme:** Google L5+ robotics/infra hybrid — explore unknown indoor spaces, build shareable maps, plan paths, scale from one vacuum to fleets of warehouse/home robots

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

Goal: **bound the product**—robots **explore unknown rooms/buildings**, build and maintain an **occupancy map**, coordinate **multi-robot coverage**, and support **path planning** to goals. This is a **mapping + exploration control plane**, not a full autonomous-vehicle stack.

### 1.0 What this is / is not

| Dimension | **Robot room exploration & mapping (this doc)** | Not this |
|-----------|--------------------------------------------------|----------|
| Primary job | Explore → map → cover → plan paths in indoor spaces | Outdoor AV / city-scale HD maps |
| Map model | 2D occupancy grid (+ optional semantic layers) | Photoreal 3D NeRF as MVP |
| Localization | Pose estimate + uncertainty (SLAM-lite / lidar+IMU+wheel) | Perfect GPS (indoors fails) |
| Authority | On-device real-time control; cloud for multi-robot + persistence | Cloud closed-loop at 100Hz (deal-breaker) |
| Success | Coverage %, map consistency, safe collision-free plans | Humanoid chat / general AGI |

**Scope statement:** Design a system where robots explore rooms, build occupancy maps, share/merge maps, plan paths, and scale from single-home to multi-building fleets with explicit cloud vs on-device split.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Environment? | Indoor rooms/floors; static furniture mostly; some dynamics (people) | Dynamic obstacles as ephemeral; static map layer |
| F2 | Sensors? | Lidar and/or depth cam + IMU + wheel odometry; bump/cliff | Sensor fusion pipeline; calibration profiles |
| F3 | Map type? | 2D occupancy grid MVP; semantic labels Phase 1.5 | Grid + metadata layers |
| F4 | Exploration goal? | Maximize unknown→known coverage; optional room segmentation | Frontier-based exploration |
| F5 | Multi-robot? | Yes — same floor; avoid double-work; share map | Coordination service + map merge |
| F6 | Path planning? | Point-to-point + coverage paths; collision avoidance | Global planner + local DWA/TEB |
| F7 | Persistence? | Maps survive reboot; cloud backup per building | Versioned map store |
| F8 | Human UI? | App shows map progress, set no-go zones, goals | Map API + edit ops |
| F9 | Localization loss? | Recover via relocalization / return-to-dock | Kidnap recovery flow |
| F10 | Offline? | Continue mapping offline; sync when Wi‑Fi returns | On-device SoT short-term; cloud merge |
| F11 | Safety? | Never drive into stairs/glass policy; stop on cliff | Safety supervisor hard-stops |
| F12 | Loop closure? | Yes when revisiting areas | Pose-graph / scan match |

**MVP functional scope:**

1. Single robot explores unknown floor plan via **frontier exploration**.  
2. Maintain **2D occupancy grid** (free / occupied / unknown) with log-odds updates.  
3. Localize continuously (odometry + scan matching); detect/handle **kidnap**.  
4. Plan collision-free paths to frontiers and user goals.  
5. Persist map locally; sync to cloud when online.  
6. Multi-robot: assign frontiers, share map deltas, conflict-free regions.  
7. App: view map, set goals, mark no-go zones, see coverage %.  
8. Dock return on low battery with known map.

**Out of MVP:**

- Full dense 3D TSDF/NeRF reconstruction as primary map  
- Outdoor GPS-denied city SLAM  
- Humanoid whole-body planning  
- Perfect multi-robot centralized control at 100Hz over cloud  
- Learning-based end-to-end “drive from pixels only” as sole stack

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Control loop latency | On-device hard real-time | Local planner 10–50 Hz; cloud not in loop |
| N2 | Map sync freshness | Soft for UI; hard for multi-robot | UI < 5s; peer share < 1–2s LAN / 5–30s WAN |
| N3 | Coverage completeness | Near-full static free space | ≥ 95% reachable free cells (policy) |
| N4 | Collision safety | Primary | Hard stop on cliff/bump; planner clearance margin |
| N5 | Map durability | Survive power loss | Local flash + cloud versions |
| N6 | Multi-robot conflict | No two robots claim same frontier forever | Lease-based assignment |
| N7 | Scale (maps) | Many buildings | Sharded map store by `building_id` |
| N8 | Battery | Exploration must be energy-aware | Frontier cost includes energy-to-dock |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New home → robot undocks → explores frontiers → map completes → docks → cloud stores map v1.  
2. User sets goal “kitchen” → planner A* on inflated grid → local avoidance around person → arrives.  
3. Two robots split floor → frontier leases → merge occupancy → coverage 98%.  
4. Robot loses Wi‑Fi → continues local map → reconnect → delta upload → cloud merge.  
5. Furniture moved → cells marked dynamic → re-observe → map updates.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Kidnap / lifted robot | Detect pose jump; freeze map writes; relocalize or ask user |
| Glass / mirrors | Lidar false free; depth+bump fusion; no-go paint |
| Narrow corridors | Clearance inflation; may mark impassable for fat robots |
| Two robots collide risk | Reciprocal velocity obstacles / reserved corridors |
| Map merge conflict | Occupancy log-odds merge; pose-graph align first |
| Loop closure large jump | Deferred remapping / keyframe rewrite; don’t corrupt mid-drive |
| Full disk on robot | Evict old sensor bags; keep compressed grid |
| Cloud down | Local-only mode; sync queue grows with backpressure |
| Stairs / cliff | Cliff sensors halt; mark lethal cells |
| Dynamic crowd | Local planner treats as ephemeral obstacles; don’t bake into static map |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Robots concurrent | 1–10 | 100 | 1K | 10K |
| Buildings / maps | 10 | 100 | 1K | 10K+ |
| Floor area per map | 200 m² | 2K m² | 20K m² | campus |
| Grid resolution | 5 cm | 5 cm | 5–10 cm | multi-res |
| Map cells (200m² @5cm) | ~80K | — | — | hierarchical |
| Sensor rate (lidar) | 10–20 Hz | same | same | same |
| Cloud map sync ops/s | 10 | 100 | 1K | 10K |
| Multi-robot / floor | 1–2 | 5–10 | 20–50 | cell fleets |
| Path plan QPS (cloud assist) | 5 | 50 | 500 | 5K |
| Telemetry retention | 7d | 30d | tiered | warehouse |

**What each jump forces:**

- **10×:** Cloud map store + frontier coordinator; delta sync not full grids.  
- **100×:** Hierarchical maps (tile/chunk); multi-floor; regional coordinators.  
- **1,000×:** Map CDN/shards; on-device autonomy mandatory; cloud = orchestration only; semantic + multi-res grids.

### 1.5 Etc. (Constraints & Assumptions)

- Robots have enough onboard CPU/GPU for local SLAM-lite and planning.  
- Indoor Wi‑Fi is intermittent — **never put emergency stop or 50Hz control in cloud**.  
- Static map assumes mostly fixed walls; people/pets are dynamic.  
- Dock pose known or learnable as landmark.  
- Clock sync via NTP soft; pose-graph uses relative measurements.

**Scope statement to repeat back:**

> Design a robot room exploration and mapping system: on-device occupancy-grid SLAM-lite + frontier exploration + local planning, with cloud map persistence, multi-robot frontier leasing, and progressive scale from home robots to building fleets—without putting the real-time control loop in the cloud.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Occupancy grid memory

```text
Area A = 200 m², resolution r = 0.05 m
Cells ≈ A / r² = 200 / 0.0025 = 80,000 cells
Log-odds float32 ≈ 4 B → 320 KB raw
With metadata (2 B flags) ≈ 480 KB per floor — trivial on-device
```

Warehouse 20,000 m² @ 5 cm:

```text
Cells = 20,000 / 0.0025 = 8,000,000 → ~32 MB float32
Still OK; at campus scale use hierarchical / tiled grids
```

**Deal-breaker:** claiming you need a distributed database to store one home map — memory is tiny; the hard parts are consistency, multi-robot merge, and localization.

### 2.2 Sensor bandwidth

```text
Lidar scan: 360 beams × 8 B ≈ 3 KB @ 15 Hz ≈ 45 KB/s
Depth image (optional): 640×480×2 @ 5 Hz ≈ 3 MB/s — do NOT stream raw to cloud continuously
On-device: keep scans in ring buffer; upload keyframes + map deltas only
```

### 2.3 Frontier exploration cost

```text
Frontier cells F ≈ O(perimeter of unknown)
Each assignment: score = distance_cost + information_gain - energy_penalty
Planning A* on 80K cells: milliseconds on modern MCU/CPU
At 50 robots × 2 plans/s = 100 plans/s — fine locally; cloud coordinator only assigns goals
```

### 2.4 Map delta sync

```text
Changed cells per second of motion ≈ strip along trajectory
Robot at 0.3 m/s, width 0.3 m, 5 cm cells → ~36 cells/s updated
Delta message ~ few KB/s compressed → WAN-friendly
Full map dump 200 m² ≈ <1 MB compressed — OK occasionally, not every second
```

### 2.5 Multi-robot conflict math

```text
N robots, F frontiers
Naive all-to-all claim → O(N²) chatter
Lease coordinator: O(N) assign per round every T=2s
At N=50, messages ~25/s — LAN MQTT/gRPC fine
```

### 2.6 Path planning latency budget

| Stage | Budget |
|-------|--------|
| Global A*/JPS | < 50–100 ms |
| Local DWA | 20–50 Hz cycle < 20–50 ms |
| Safety supervisor | < 5 ms hard |
| Cloud (optional replan assist) | 200–500 ms soft, never blocks safety |

---

## 3. High-Level Design

### 3.1 Control planes (critical split)

| Plane | Where | Frequency | Responsibility |
|-------|-------|-----------|----------------|
| Safety | On-device | 50–100 Hz | Cliff, bump, e-stop |
| Local plan / control | On-device | 10–50 Hz | Follow path, avoid dynamic |
| SLAM / localization | On-device | 5–20 Hz | Pose + map update |
| Frontier exploration | On-device + coordinator | 0.5–2 Hz | Pick next frontier |
| Map sync / multi-robot | Cloud or LAN hub | 0.2–2 Hz | Merge, lease, persist |
| Human UI | Cloud API | On demand | View/edit map |

**Authority model (MVP):** On-device is **source of truth for live occupancy** while exploring; cloud holds **versioned canonical maps** per `building_id` after merge. Multi-robot uses a **coordinator** (LAN hub preferred; cloud OK if latency soft).

### 3.2 API (cloud / hub)

```text
POST   /v1/buildings/{id}/maps:uploadDelta
GET    /v1/buildings/{id}/maps/latest
POST   /v1/buildings/{id}/frontiers:lease
POST   /v1/buildings/{id}/frontiers:release
POST   /v1/buildings/{id}/goals
PATCH  /v1/buildings/{id}/nogo
GET    /v1/buildings/{id}/coverage
WS/MQTT /v1/buildings/{id}/telemetry   # pose, battery, coverage
```

Robot local APIs (gRPC on device bus):

```text
Localize(scan) -> pose, covariance
UpdateMap(scan, pose) -> changed_cells
PlanPath(start, goal, grid) -> path
SelectFrontier(grid, pose, peers) -> target
```

### 3.3 Data model

**Occupancy cell**

```text
cell {
  log_odds: float16/float32
  flags: static_occ | free | unknown | nogo | lethal | dynamic
  last_obs_ts
}
```

**Map document**

```text
Map {
  map_id, building_id, floor_id
  origin (x,y,yaw), resolution
  width, height
  tiles[] or dense blob
  pose_graph_ref
  version, parent_version
  coverage_stats
}
```

**Robot state**

```text
Robot {
  robot_id, building_id
  pose, covariance
  battery, mode (explore|goto|dock|recover)
  held_frontier_lease
  map_version_applied
}
```

### 3.4 Core algorithms — Why X over Y

| Approach | Pros | Cons | Use |
|----------|------|------|-----|
| **Occupancy grid (log-odds)** | Simple, mergeable, planner-friendly | 2D bias; resolution tradeoff | MVP map |
| Feature SLAM only | Sparse, loop-closure friendly | Weak for coverage/planning | Pose graph layer |
| OctoMap / 3D | Handles height | Memory/CPU heavier | Phase 1.5 stairs/shelves |
| Frontier exploration | Information-theoretic classic | Can thrash; needs hysteresis | MVP explore |
| Random walk / lawnmower | Simple coverage | Poor in unknown open maps | Known-map cleaning only |
| Centralized cloud SLAM | Easy multi-robot theory | Latency/connectivity deal-breaker | Avoid for control |
| Decentralized map share | Robust offline | Merge harder | Preferred |

### 3.5 Exploration loop

```text
while battery_ok and coverage < target:
  localize()
  update_occupancy(scan)
  frontiers = extract_frontiers(grid)
  target = score_and_pick(frontiers)  # or leased from coordinator
  path = global_plan(pose, target)
  follow_path_with_local_avoidance()
  if loop_closure: optimize_pose_graph(); remap_affected()
sync_deltas_when_online()
```

### 3.6 Why X over Y (summary)

| Decision | Choice | Reject |
|----------|--------|--------|
| Map | 2D occupancy + pose graph | NeRF-only MVP |
| Explore | Frontier + information gain | Pure random |
| Multi-robot | Frontier leases | All robots race same cell |
| Cloud role | Persist + coordinate | Closed-loop control |
| Planning | A*/JPS + local DWA | Cloud RRT every tick |
| Merge | Align frames then log-odds fuse | Blind overwrite |

---

## 4. Architecture Diagram

### 4.1 Single-robot stack

```text
┌─────────────────────────────────────────────────────────────┐
│                        ROBOT (on-device)                      │
│  Sensors → Sync → Localization (scan match + IMU + odom)    │
│              ↓                                               │
│         Occupancy Grid Updater (log-odds)                    │
│              ↓                                               │
│  Frontier Extractor → Explorer Policy → Global Planner       │
│              ↓                       ↓                       │
│         Local Planner/DWA ←—— Safety Supervisor (hard)       │
│              ↓                                               │
│           Motor Controller                                   │
│                                                              │
│  Map Store (flash) ←→ Delta Sync Agent                       │
└─────────────────────────────┬───────────────────────────────┘
                              │ Wi‑Fi (best effort)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ CLOUD / BUILDING HUB                                         │
│  Map Service (versioned) │ Frontier Coordinator │ UI API     │
│  Object store (tiles)    │ Telemetry            │ Auth       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Multi-robot coordination

```text
Robot A ──deltas──┐
Robot B ──deltas──┼──► Map Merger ──► Canonical Map vN
Robot C ──deltas──┘         │
                            ▼
                   Frontier Coordinator
                     │ leases / releases
         ┌───────────┼───────────┐
         ▼           ▼           ▼
      Robot A     Robot B     Robot C
```

### 4.3 Map tile layout (100×+)

```text
Floor map
  ├── tile(0,0)  tile(0,1)  tile(0,2)
  ├── tile(1,0)  tile(1,1)  tile(1,2)
  └── ...
Each tile: 256×256 cells @ 5cm ≈ 12.8m × 12.8m
Sync unit = dirty tiles + pose-graph edges
```

### 4.4 Localization recovery

```text
pose jump / match score collapse
  → enter RECOVER
  → stop map writes (or mark uncertain)
  → global localization: scan vs map candidates
  → if success: resume; else: return-to-dock / user assist
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Safety supervisor can always stop** without cloud.  
2. **Map writes require localization confidence** above threshold.  
3. **Canonical cloud map versions are immutable**; updates create `vN+1`.  
4. **Frontier leases expire** (TTL); no permanent deadlocks.  
5. **No-go / lethal cells always win** over free observations.  
6. **Dynamic obstacles do not permanently carve static free→occ** without persistence rule.

#### 5.1.2 Occupancy update (log-odds)

```text
L(x) ← L(x) + L_occ(z) - L_prior   # inverse sensor model
clamp L to [L_min, L_max]          # prevent overconfidence
if flags.nogo or flags.lethal: ignore free hits
```

**Deal-breaker:** unbounded log-odds so one bad scan can never be corrected.

#### 5.1.3 Loop closure & remapping

Large pose-graph corrections can **invalidate** occupancy drawn under wrong poses.

MVP approaches:

| Approach | Tradeoff |
|----------|----------|
| Submap freeze + rewrite on closure | Correct; CPU burst |
| Elastic pose deformation of grid | Complex |
| Accept small drift; periodic rematch | Home robot OK |

At warehouse scale prefer **submaps** keyed by pose-graph nodes; on closure, remap only affected submaps.

#### 5.1.4 Multi-robot map merge

```text
1. Estimate relative transform T_AB (shared landmarks / dock / scan overlap)
2. Transform B cells into A frame
3. For each cell: L = L_A + L_B - L_prior (independent info approx)
4. Resolve flag conflicts: lethal > nogo > occ > free > unknown
5. Publish Map vN+1; robots pull and rebase local deltas
```

**Conflict:** concurrent edits to same tile — use version vectors / last-merge-wins on tile + CRDT-ish log-odds (sum evidence).

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Kidnap | Relocalize; pause writes |
| 10× | Merge skew | Tile versions; rebase |
| 100× | Coordinator SPOF | LAN + cloud standby; lease TTL |
| 1,000× | Sync storm | Dirty-tile bloom; rate limits; hierarchy |

### 5.2 Scalability

#### 5.2.1 Hierarchical maps

```text
L0: 5 cm occupancy (local planning)
L1: 20 cm coarse (frontier / long A*)
L2: room graph (topology for multi-floor)
```

Long plans on L1/L2; refine on L0 near robot.

#### 5.2.2 Frontier scoring

```text
score(f) = α·info_gain(f) - β·path_cost(pose,f) - γ·energy_to_dock_after
           - δ·proximity_penalty(other_robots)
           + hysteresis if currently committed
```

Hysteresis prevents thrashing between two frontiers.

#### 5.2.3 Path planning stack

| Layer | Algo | Notes |
|-------|------|-------|
| Global | A* / JPS on inflated grid | Clearance = robot_radius + margin |
| Coverage | Boustrophedon on known free | After explore phase |
| Local | DWA / TEB | Dynamic people |
| Multi-robot | Reserved time-space corridors or ORCA | Avoid deadlocks at doors |

#### 5.2.4 Cloud storage layout

```text
gs://maps/{building}/{floor}/v{N}/tiles/{tx}_{ty}.bin
gs://maps/{building}/{floor}/v{N}/pose_graph.json
Dynamo/Spanner: MapMeta(building, floor, latest_version, coverage)
```

#### 5.2.5 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Delta sync; frontier coordinator; versioned cloud maps |
| →100× | Tiled hierarchical maps; per-building hubs; submap SLAM |
| →1,000× | Regional map shards; semantic layers; fleet schedulers; multi-res only |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
resolution_m: 0.05
l_occ: 0.9
l_free: -0.4
l_clamp: [-5, 5]
frontier_cluster_m: 0.5
lease_ttl_s: 30
inflate_m: 0.25
min_localize_score: 0.6
coverage_target: 0.95
dynamic_decay_half_life_s: 30
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `coverage_ratio` | Product success |
| `localize_score` | Map write safety |
| `frontier_count` | Exploration health |
| `map_version_lag` | Multi-robot skew |
| `lease_steal_count` | Coordinator issues |
| `collision_near_miss` | Safety |
| `loop_closures` | SLAM health |
| `sync_queue_bytes` | Offline backlog |

#### 5.3.3 Testing

- Gazebo/Habitat sims with known ground-truth maps → coverage & ADE.  
- Adversarial glass/mirror scenes.  
- Multi-robot doorway deadlock suites.  
- Kidnap + relocate integration tests.  
- Clock skew / packet loss on sync channel.

#### 5.3.4 Ops

- Map rollback to previous version if bad merge.  
- Per-robot feature flags for exploration aggressiveness.  
- Human “paint no-go” always authoritative.

---

## 6. Wrap-Up

### 6.1 What we designed

An **on-device SLAM-lite + occupancy-grid explorer** with **frontier-based coverage**, **local safety-critical planning**, and a **cloud/hub plane** for versioned maps, multi-robot frontier leases, and human map edits—scaled via tiles, hierarchy, and delta sync.

### 6.2 Memorize tradeoffs

| Topic | Tradeoff |
|-------|----------|
| Resolution | Finer = better plans, more CPU/memory |
| Cloud vs device | Device for control; cloud for share/persist |
| Merge | Evidence fusion vs overwrite |
| Exploration | Info gain vs energy vs conflict |
| Loop closure | Accuracy vs remap cost |
| Dynamic obs | Ephemeral local vs static map pollution |

### 6.3 30-second scale narrative

Baseline: one robot, dense grid, local frontiers.  
10×: cloud maps + leases.  
100×: tiles + hierarchy + submaps.  
1,000×: fleet orchestration; cloud never in the 50Hz loop.

### 6.4 Deal-breakers checklist

- Putting e-stop / local avoidance in cloud.  
- Unbounded log-odds / no confidence gate on map writes.  
- Multi-robot with no lease/assignment → duplicated work + collisions.  
- Full raw depth video to cloud as the sync design.  
- Claiming exact global multi-robot SLAM with zero relative localization story.  
- Ignoring glass/cliff as “lidar will see it.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: 2D or 3D map?**  
A: 2D occupancy MVP for floor robots; 3D/multi-layer for stairs/shelves Phase 1.5.

**Q2: What is “done exploring”?**  
A: Coverage of reachable free space ≥ threshold and frontier set empty/low value.

**Q3: Who wins: robot observation or user no-go?**  
A: User no-go / lethal always wins.

**Q4: Can robots explore without cloud?**  
A: Yes — cloud is persistence/coordination, not autonomy.

### 7.2 SLAM & mapping

**Q5: Occupancy grid vs feature map?**  
A: Grid for planning/coverage; features/pose-graph for localization & loop closure — use both.

**Q6: How do you update cells?**  
A: Inverse sensor model in log-odds with clamping.

**Q7: How to handle dynamics?**  
A: Short-half-life dynamic layer; don’t freeze people into walls.

**Q8: Loop closure remapping?**  
A: Submaps tied to pose-graph nodes; rewrite affected submaps on optimization.

**Q9: Relocalization after kidnap?**  
A: Global scan-to-map matching; degrade to dock-seeking if fail.

### 7.3 Exploration & planning

**Q10: Why frontiers?**  
A: Boundary of known-free and unknown is where information is gained.

**Q11: Frontier thrashing?**  
A: Hysteresis, clustering, commit timeout.

**Q12: Global vs local planner?**  
A: Global geometric path; local reactive avoidance.

**Q13: Narrow door deadlock (2 robots)?**  
A: Priority rules, one-way leases, ORCA + door mutex.

**Q14: Energy-aware explore?**  
A: Score includes path-to-frontier + path-to-dock cost vs battery.

### 7.4 Multi-robot & cloud

**Q15: How to assign work?**  
A: Coordinator auctions/leases frontiers by score with anti-collision penalty.

**Q16: Map merge without shared frame?**  
A: Find overlap / shared landmark (dock); estimate T; then fuse.

**Q17: WAN multi-robot same room?**  
A: Prefer LAN hub; WAN only for soft sync — warn latency.

**Q18: CRDT for maps?**  
A: Log-odds evidence roughly commutative; flags need lattice merge rules.

### 7.5 Reliability & safety

**Q19: What must never depend on Wi‑Fi?**  
A: Safety stop, cliff, local collision avoidance, motor limits.

**Q20: Corrupted map deploy?**  
A: Version pin; rollback; robots validate checksum + localize score before adopt.

**Q21: Sensor failure?**  
A: Fail-safe stop; degraded mode (slow bump-follow) only if policy allows.

### 7.6 Estimation drills

**Q22: Memory for 10,000 m² @ 5 cm float32?**  
A: Cells=10,000/0.0025=4e6 → 16 MB — fine; argue hierarchy for campuses.

**Q23: Why not stream all lidars to cloud SLAM?**  
A: 45KB/s×10K robots + RTT; control loop dies; cost explodes; privacy.

**Q24: Delta vs full upload?**  
A: Dirty tiles ≪ full map; full snapshot periodic for repair.

### 7.7 Alternatives & deal-breakers

**Q25: Only lawnmower pattern?**  
A: Needs known map bounds; bad for unknown exploration.

**Q26: Pure end-to-end RL exploration?**  
A: Research; hard safety/cert; keep classical MVP + ML assists.

**Q27: Centralized tick simulation in cloud?**  
A: Cool demo; production indoor Wi‑Fi makes it a deal-breaker for safety.

### 7.8 Interview craft

**Q28: How to open?**  
A: Sensors, map model, single vs multi, cloud role, safety — then draw on-device loop.

**Q29: What impresses L5+?**  
A: Explicit plane split, lease-based multi-robot, merge math, hierarchical scale story, deal-breakers.

**Q30: Common mistake?**  
A: Designing fancy cloud microservices while leaving localization & safety hand-wavy.

---

### Appendix A — Log-odds cheat sheet

```text
p = 1 - 1/(1+exp(L))
L = logit(p)
update: L += L_sensor
clamp to avoid ±∞
```

### Appendix B — Frontier extraction

```text
for each free cell c:
  if any neighbor unknown:
    mark c frontier
cluster frontiers (DBSCAN / adjacent)
centroid = cluster representative
```

### Appendix C — Inverse sensor model (lidar ray)

```text
for cells along ray until hit:
  L += L_free
cell at hit:
  L += L_occ
beyond hit: unchanged
```

### Appendix D — Lease protocol

```text
robot -> coordinator: RequestFrontier(pose, candidates)
coordinator: pick argmax score not leased; lease_id, ttl
robot: Heartbeat / Release / Complete
on ttl expiry: frontier free again
```

### Appendix E — A* inflation

```text
inflate occupied by ceil(radius/resolution) cells
lethal if distance < radius
cost = distance + soft cost near obstacles
```

### Appendix F — Delta sync message

```json
{
  "robot_id": "r42",
  "base_version": 118,
  "pose": {"x":1.2,"y":3.4,"yaw":0.2},
  "tiles": [{"tx":3,"ty":5,"cells_rle": "..."}],
  "pose_graph_edges": []
}
```

### Appendix G — Progressive scale table

| Scale | On-device | Coord | Map store |
|-------|----------|-------|-----------|
| Baseline | Full stack | Optional | Local + simple cloud |
| 10× | Full stack | Leases | Versioned maps |
| 100× | Submaps | Per-building hub | Tiles |
| 1,000× | Multi-res | Regional fleet mgr | Sharded CDN |

### Appendix H — Coverage metric

```text
coverage = known_free_reachable / estimated_reachable
estimate_reachable via flood-fill from dock on free∪unknown with clearance
```

### Appendix I — Modes state machine

```text
IDLE → EXPLORE → GOTO_GOAL → DOCK
         ↓
      RECOVER → (success) EXPLORE
              → (fail) AWAIT_USER / DOCK_BLIND
```

### Appendix J — NFR card

```text
Safety & local plan on-device only
Localize score gate on map writes
Frontier lease TTL
Map versions immutable
Coverage ≥ 95% target policy
Sync deltas, not raw video
```

### Appendix K — Semantic layer (Phase 1.5)

```text
room_id, type (kitchen, hall)
objects: chair, table (bounding boxes)
used for: UX labels, better goals — not required for occupancy MVP
```

### Appendix L — Multi-floor

```text
floor graphs connected by elevator/stair nodes
robot asks human/elevator API for floor change
separate occupancy per floor_id
```

### Appendix M — Common pushbacks

| Pushback | Answer |
|----------|--------|
| “Just use ROS Nav2” | Fine components; still design ownership, sync, multi-robot, scale |
| “Cloud SLAM is simpler” | Until Wi‑Fi drops mid-staircase |
| “Grid is outdated” | Still best MVP for planners; add learned layers later |

### Appendix N — Related Google systems (conceptual)

- Indoor Maps / building models  
- Warehouse robotics orchestration patterns  
- Edge + cloud IoT device sync  

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Frontier | Free cell adjacent to unknown |
| Kidnap | Unexpected pose discontinuity |
| Log-odds | Logit occupancy belief |
| Inflation | Grow obstacles for robot radius |
| Submap | Local grid pinned to pose-graph node |

### Appendix P — Worked example

```text
Living room 50 m², r=5cm → 20K cells
Robot explores 10 min @ 0.25 m/s effective
Frontier clusters ~8 → picks farthest info-gain
Coverage 96% → dock → upload map v1 (200 KB)
Second robot joins → downloads v1 → leases remaining frontiers
```

### Appendix Q — Consistency cheatsheet

| Data | Consistency |
|------|-------------|
| Live local grid | Strong on device |
| Cloud canonical | Versioned eventual |
| Leases | Linearizable at coordinator |
| UI view | Eventually consistent OK |

### Appendix R — 30m interview checklist

1. Clarify indoor, sensors, multi-robot, cloud role.  
2. Draw on-device loop vs cloud.  
3. Occupancy + frontiers + planning.  
4. Numbers: cells, bandwidth, sync.  
5. Multi-robot leases + merge.  
6. Scale 10×/100×/1,000×.  
7. List deal-breakers (cloud control loop).  

### Appendix S — Pseudocode explore

```text
def explore_tick(robot):
  pose, ok = localize(robot.scan)
  if not ok: return recover()
  update_grid(robot.grid, pose, robot.scan)
  if robot.lease is None or expired(robot.lease):
    robot.lease = coordinator.acquire(robot)
  path = plan(pose, robot.lease.target)
  local_follow(path)
```

### Appendix T — What changes at each scale (quick card)

| Scale | Key change |
|-------|------------|
| 10× | Coordinator + cloud versions |
| 100× | Tiles/submaps |
| 1,000× | Hierarchy + fleet mgr; autonomy hardened |

### Appendix U — Calibration & profiles

```text
robot_model → extrinsics, inverse sensor params, radius, max_speed
wrong calibration → systematic map shear (detect via loop closure residuals)
```

### Appendix V — Privacy

- Raw cameras optional; prefer lidar + on-device feature extraction.  
- Cloud stores maps + telemetry, not continuous home video by default.  
- User can wipe building maps.

---

*End of robot room exploration & mapping system design.*
