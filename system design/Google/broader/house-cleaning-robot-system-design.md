# System Design: House-Cleaning Robot (Fleet + Cloud)

> **Focus areas:** SLAM / home maps · Coverage path planning · Docking & battery · Multi-floor · Dirt detection · Fleet scheduling · OTA · Map privacy · Edge autonomy + cloud orchestration  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit edge vs cloud authority, physics/robotics constraints as deal-breakers, honest offline-home behavior, privacy of floor plans as first-class  
> **Interview theme:** Unusual Google L5+ — cyber-physical fleet: real-time autonomy on-device, cloud for fleet ops / ML / scheduling, not “remote-control Roomba over RPC”

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

Goal: **bound the product**—a **house-cleaning robot** fleet with **on-device autonomy** (map, plan, clean, dock) and a **cloud control plane** (accounts, schedules, OTA, fleet analytics, optional map sync). Clarify what must work with **Wi‑Fi down** vs what cloud enhances.

### 1.0 What this is / is not

| Dimension | **House-cleaning robot (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Cover floors, avoid obstacles, dock, report status | Telepresence / remote joystick cleaning as MVP |
| Success | Clean coverage %, safe navigation, reliable dock, user trust | Perfect global map consistency across homes |
| Authority | **Robot is SoT for live navigation**; cloud orchestrates policy/schedule | Cloud path-planning every wheel tick |
| Connectivity | Home Wi‑Fi flaky; cleaning must continue | Always-online assumption |
| Privacy | Home maps are sensitive PII-like | Upload raw cameras forever by default |
| Scale | Millions of homes × robots | Single robot toy demo |

**Scope statement:** Design the robot + cloud system for autonomous floor cleaning: mapping, coverage planning, docking, scheduling, multi-floor, dirt detection, OTA, map privacy, and failure recovery—at progressive fleet scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What does the robot clean? | Hard floors + short carpet; vacuums debris; mop optional Phase 1.5 | Coverage planner + surface modes |
| F2 | Sensors? | Lidar and/or depth cam + IMU + cliff + bump + dirt/optical; mic optional | Sensor fusion; not vision-only MVP |
| F3 | Mapping? | Persistent home map; update as furniture moves | SLAM + map versioning |
| F4 | Coverage goal? | Clean “whole floor” or selected rooms; resume after charge | Coverage completeness tracking |
| F5 | Docking? | Auto-return when low battery / job done; resume | Dock localization + resume state |
| F6 | Multi-floor? | Yes — user carries between floors or stair-aware forbid | Per-floor maps; floor ID |
| F7 | Scheduling? | App/cloud schedules; quiet hours; no-go zones | Cloud schedule + on-device calendar cache |
| F8 | Dirt detection? | Spot-clean high-dirt; optional re-pass | Dirt map layer + planner bias |
| F9 | App features? | Start/stop, map edit (rooms, no-go), history, OTA status | Device twin / command channel |
| F10 | Multi-robot home? | Optional Phase 1.5 (2 robots same home) | Partition coverage; conflict zones |
| F11 | Privacy? | Maps stay local by default; opt-in cloud backup | Encryption, consent, retention |
| F12 | Failures? | Stuck, cliff, dock miss, Wi‑Fi loss, wheel slip | Recovery FSM + user alert |
| F13 | OTA? | Signed firmware; staged rollout; rollback | Fleet OTA pipeline |
| F14 | Who controls live path? | Robot onboard | Never RPC each pose from cloud |

**MVP functional scope:**

1. Onboard SLAM builds/updates a 2D occupancy map per floor.  
2. Coverage path planner cleans rooms / whole floor with completeness tracking.  
3. Obstacle avoidance + cliff/bump safety stops.  
4. Auto-dock on low battery; **resume** unfinished coverage after charge.  
5. App: start/pause/dock, view map, set no-go / rooms, schedules.  
6. Dirt detection biases re-coverage of hot spots.  
7. Multi-floor: separate maps; user selects or auto-detects floor.  
8. Offline cleaning with last-known schedule/map; sync when online.  
9. Signed OTA with canary → staged → rollback.  
10. Map privacy: local-first; encrypted opt-in cloud backup.

**Out of MVP:**

- Humanoid manipulation / picking up socks as primary  
- Perfect semantic scene understanding of every object  
- Cloud-remote teleop cleaning as the main mode  
- Multi-home robot sharing without re-mapping  
- Real-time cloud SLAM (deal-breaker latency/privacy)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Autonomy offline | Clean without cloud | Full mission with cached map/plan |
| N2 | Safety | No stairs plunge; pinches minimized | Hard real-time safety on MCU/SoC |
| N3 | Coverage quality | “Looks clean” / measurable | ≥90–95% free-space coverage when unobstructed |
| N4 | Dock success | Rare user rescue | ≥99% dock success when dock visible/reachable |
| N5 | Command latency (app) | Feels responsive when online | p99 < 2–5s command ACK (not path ticks) |
| N6 | Map privacy | Default local | Opt-in sync; E2E or server-side encrypt at rest |
| N7 | OTA safety | No brick fleet | Staged + health gates + rollback image |
| N8 | Battery / mission | Typical apartment 1–2 charges | Explicit multi-trip resume |
| N9 | Fleet availability | Cloud ops 99.9% | Cleaning continues if cloud down |
| N10 | Observability | Support debug without raw video dump | Structured logs + optional privacy-safe snapshots |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. First-run mapping → user labels rooms → scheduled clean → coverage complete → dock.  
2. Mid-clean low battery → dock → charge → resume remaining cells → done.  
3. User draws no-go around pet bowl → planner respects; next mission uses map vN+1.  
4. Dirt sensor spikes in kitchen → local re-pass; dirt heatmap updated.  
5. User carries robot upstairs → selects Floor 2 map → cleans → docks on Floor 2 dock.  
6. OTA night window → canary 1% → promote → robot reboots at dock only.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Wi‑Fi down mid-mission | Continue; queue telemetry; app shows last sync |
| Furniture moved | Local replan; mark stale regions; optional remap pass |
| Stuck under couch | Escape behaviors → if fail, pause + notify; pin location |
| Dock IR/fiducial occluded | Spiral search / last-known dock pose; escalate to user |
| Cliff sensor false positive | Debounce + cross-check; don’t disable cliffs |
| Wheel slip / kidnap | Detect pose jump; recovery localization or pause |
| Crawl space / dark under sofa | Conservative unknown-space policy; don’t invent free space |
| Kid lifts robot (kidnap) | Relocalize or ask “where am I?” / new map session |
| Two robots collide path | Phase 1.5: reserved zones / time slots |
| Map uploaded without consent | **Blocked** — privacy gate |
| Bad OTA crashes nav | Rollback partition; safe mode → dock |
| Full bin / tangled brush | Pause job; notify; preserve coverage state |
| Multi-floor wrong map | Floor fingerprint mismatch → don’t trust; remap prompt |
| Schedule during party | Quiet hours / presence integration optional; honor suppress |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active robots (fleet) | 100K | 1M | 10M | 100M |
| Concurrent online | 20K | 200K | 2M | 20M |
| Missions / day | 150K | 1.5M | 15M | 150M |
| Telemetry events/s (fleet) | 50K | 500K | 5M | 50M |
| Map backup opt-in % | 20% | 20% | 25% | 30% |
| Avg map size (compressed) | 0.5–2 MB | same | same | +semantics |
| OTA package size | 50–150 MB | same | delta packages | delta + A/B |
| Support tickets / day | 1K | 10K | 100K | 1M |
| Homes with 2+ robots | rare | 1% | 5% | 10% |
| Cloud regions | 1–2 | 3 | 5+ | cell/geo fabric |

**What each jump forces:**

- **10×:** Device twin + IoT hub sharding; telemetry sampling; OTA canary automation.  
- **100×:** Regional device cells; map backup object store tiering; privacy-preserving analytics; support tooling at scale.  
- **1,000×:** Extreme edge autonomy (cloud optional); hierarchical fleet planes; differential OTA; on-device ML only for dirt/obstacle; map never required in cleartext server-side.

### 1.5 Etc. (Constraints & Assumptions)

- Homes are GPS-poor indoors; localization is **map-relative**, not lat/lon.  
- Wi‑Fi is best-effort; cellular optional on premium SKU (hooks).  
- Robot compute: mid-tier SoC (e.g. NPU for vision) + MCU for safety.  
- Dock provides charging + optional room beacon / fiducial.  
- Users may lie about floor plans; trust onboard sensing over app drawings for obstacles.  
- “Google” framing: treat as consumer device + Google Account linking, Home app integration optional.

**Scope statement to repeat back:**

> Design a house-cleaning robot system where the robot autonomously maps, plans coverage, cleans, docks, and recovers from failures offline; the cloud provides identity, scheduling, map backup (privacy-preserving), fleet OTA, and analytics—scaling from 100K to 100M devices without making the cloud the real-time navigation brain.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **On-device control** | 10–50 Hz pose/plan | per robot | per robot | Edge (not cloud) |
| **Command / RPC** | start/stop/schedule | ~few/robot/day | ×10 robots | IoT command |
| **Telemetry** | status, battery, errors | 0.1–1 Hz sampled | ×10 | Ingest bus |
| **Map sync** | opt-in backup | rare; MBs | ×10 | Object store |
| **OTA** | download windows | bursty | staged | CDN |
| **App reads** | map/status | interactive | CDN + twin | API |

**Anti-pattern:** one “QPS” that includes 50 Hz lidar scans uploaded to cloud.

### 2.2 Home geometry & mission time

```text
Apartment free floor area ~ 60–100 m²
Robot coverage rate ~ 0.5–1.0 m²/min effective (with overlap, obstacles)
Mission time ~ 1–2.5 hours → often needs mid-mission dock on small battery

Coverage grid cell 0.1 m × 0.1 m → 100 m² → 10,000 cells
Bitmap / occupancy: tens of KB–few MB with compression + layers (rooms, dirt, no-go)
```

### 2.3 Telemetry at fleet scale

```text
Naive: 1M robots × 1 Hz × 500 B = 500 MB/s = nightmare
MVP: state reports every 30–60s when idle; 5–10s when cleaning; events on transitions
1M robots × 20% cleaning × 0.2 Hz × 300 B ≈ 12 MB/s — manageable with sampling + regional ingest

Error events: sparse but must be durable (stuck, cliff, OTA fail)
```

### 2.4 Map backup storage

```text
1M robots × 20% opt-in × 2 MB × 3 versions ≈ 1.2 TB — cheap
100M × 30% × 5 MB × 5 versions ≈ 750 TB — still object-store OK
Deal-breaker: storing continuous raw camera video for all homes
  1M × 1 Mbps × continuous → multi-Tbps — refuse by default
```

### 2.5 OTA bandwidth

```text
10M robots × 100 MB full image simultaneous = 1 EB download — impossible as thundering herd
Need: CDN + delta patches (5–20 MB) + staged waves + dock-only apply + regional caches
Wave of 1%: 100K × 20 MB = 2 TB — fine over days
```

### 2.6 On-device compute budget

```text
SLAM + local planner on SoC: must sustain 10+ Hz localization
Cloud RTT even on good Wi‑Fi: 20–100ms — too slow/jittery for bumper reaction
Safety stop: <10–20 ms on MCU — cloud cannot be in loop
```

**Deal-breaker arithmetic:** any design that requires cloud round-trip before obstacle stop fails basic physics of moving robots.

---

## 3. High-Level Design

### 3.1 Domain model

```text
Home
  home_id, owner_account, timezone, quiet_hours, robots[]

Robot
  robot_id, home_id, sku, firmware_ver, capability_flags
  battery, bin_full, mode (IDLE|CLEANING|DOCKING|CHARGING|ERROR|OTA)
  current_floor_id, pose_confidence

FloorMap
  floor_id, home_id, map_version, occupancy, rooms[], no_go[], docks[]
  dirt_layer, coverage_layer, created_at, source (LOCAL|RESTORED)

Mission
  mission_id, robot_id, floor_id, goal (WHOLE|ROOMS|SPOT)
  schedule_id?, state, coverage_pct, resume_checkpoint, started_at

DeviceTwin
  desired: {schedule, no_go, rooms, power_mode, map_prefs}
  reported: {status, map_version, mission, errors}

OTARelease
  release_id, version, artifact_hash, rollout_pct, health_gates
```

### 3.2 API (logical)

| Op | Semantics |
|----|-----------|
| `StartMission(robot, goal)` | Desired twin → device; ACK when accepted onboard |
| `Pause / DockNow / Resume` | Commands with idempotency keys |
| `UpdateMapEdit(rooms, no_go)` | Versioned map edit; device merges |
| `SetSchedule(cron, goals)` | Cloud calendar; device caches next N |
| `GetStatus / SubscribeStatus` | Twin + event stream |
| `OptInMapBackup / RestoreMap` | Consent-gated encrypted blob |
| `ReportTelemetry(events)` | Device → ingest (batched) |
| `OTACheck / OTAApply` | Device pulls policy; apply at dock |

**Not an API:** `SetWheelVelocity(v, ω)` from cloud every 20 ms.

### 3.3 Authority model (critical interview fork)

| Model | Pros | Cons | Verdict |
|-------|------|------|---------|
| **A. Robot SoT navigation + cloud SoT policy** | Safe offline; clear | Map merge conflicts need rules | **MVP default** |
| **B. Cloud SoT live path** | Easy “central brain” story | Latency, outage, privacy | **Deal-breaker** |
| **C. Pure offline no cloud** | Max privacy | No OTA/fleet/schedule sync | Niche SKU |

**Chosen:**  
- **Robot:** pose, local map, live planner, safety, mission execution FSM.  
- **Cloud:** identity, schedules, consent, OTA, analytics, encrypted backups, support.  
- **Device twin:** desired/reported reconciliation; never block cleaning on twin lag.

**Deal-breaker:** dual equal map SoT without version vectors / last-writer rules → split-brain no-go zones.

### 3.4 Mapping & localization — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **2D lidar SLAM** | Mature, robust indoors | Cost; pets/glass | **Strong MVP** |
| Visual SLAM only | Cheap sensors | Lighting/texture fail | Budget SKU + care |
| Cloud SLAM | Big compute | Privacy + RTT | **Reject for live** |
| Pure odometry | Simple | Drift | Short spot cleans only |
| Prebuilt floorplan import | Nice UX | Wrong often | Assist, not trust |

**Chosen MVP:** onboard **lidar (or depth) SLAM** → occupancy grid + pose graph; optional visual loop-closure assist. Cloud may run **offline** map cleanup ML on **opt-in** encrypted uploads—not in the control loop.

### 3.5 Coverage path planning — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Boustrophedon / cellular decomposition** | Good coverage | Weak dynamic obstacles | Open rooms |
| Grid wavefront / lawnmower on free cells | Simple completeness | Inefficient | MVP rooms |
| TSP on room graph + local coverage | Multi-room natural | Needs room seg | **MVP compose** |
| Random bounce (old robots) | Simple | Poor completeness | Reject as primary |
| Cloud OR-Tools each mission | Optimal-ish | Needs connectivity | Optional offline replan assist |

**Chosen:**

```text
1. Segment rooms (user + auto).
2. Order rooms (heuristic TSP / user order).
3. Within room: boustrophedon on coverage grid.
4. Dynamic obstacle → local replan (D* lite / timed elastic band style).
5. Dirt hotspots → insert re-cover passes.
6. Checkpoint coverage bitmap every N cells / on dock.
```

**Deal-breaker:** random walk as the completeness story for a modern product interview.

### 3.6 Docking & energy

```text
Battery SOC → thresholds:
  WARN: finish current cell group
  RETURN: plan path to dock
  CRITICAL: best-effort dock / stop safe

Dock detection: fiducial / IR / lidar signature near last dock pose
Dock approach: precision controller; abort & retry with offset
Resume: load coverage checkpoint; continue uncovered cells
```

Multi-dock homes (Phase 1.5): nearest reachable dock with charge.

### 3.7 Multi-floor

| Approach | Notes |
|----------|-------|
| Manual floor select | MVP reliable |
| Floor fingerprint (Wi‑Fi RSSI + map match) | Auto suggest |
| Barometer / stair detect | Hint only; robot usually can’t climb |

**Invariant:** never apply Floor A no-go to Floor B. Maps keyed by `floor_id`.

### 3.8 Dirt detection

```text
Optical / piezoelectric dirt sensor → dirt_score along trajectory
Update dirt_layer (EMA decay over days)
Planner: weight uncovered cells by dirt_score for re-pass
App: heatmap (local); cloud aggregate only anonymized stats if consented
```

### 3.9 Privacy of home maps

| Control | MVP |
|---------|-----|
| Default storage | On robot flash encrypted |
| Cloud backup | Opt-in; encrypt with key hierarchy |
| Support access | Time-boxed, audited, preferably user-share token |
| Analytics | Derived metrics (coverage %, error codes)—not raw maps |
| Cameras | No continuous upload; optional short privacy-blurred clip on stuck (opt-in) |
| Deletion | Wipe device + cloud objects on account delete |

**Deal-breaker:** “maps are just telemetry” without consent UX and retention policy.

### 3.10 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Nav authority | On-robot | Latency + offline + safety | Cloud closed-loop control |
| Map default | Local-first | Privacy | Mandatory cleartext cloud maps |
| Coverage | Room TSP + boustrophedon + checkpoints | Completeness + resume | Random bounce only |
| Connectivity | Twin + eventual sync | Flaky Wi‑Fi | Require online to clean |
| OTA | Signed A/B + staged | Fleet safety | Force update while driving |
| Telemetry | Sampled + events | Cost | 50 Hz cloud lidar |
| Multi-floor | Separate maps | Safety | One blended map |
| Dirt | Local layer + planner bias | Product value | Cloud dirt inference from video only |

---

## 4. Architecture Diagram

```text
  +------------------+         +------------------+
  | Mobile App       |         | Web / Home App   |
  | map edit, sched  |         | support (gated)  |
  +--------+---------+         +--------+---------+
           | HTTPS                      |
           v                            v
  +------------------------------------------------+
  |              Cloud Control Plane               |
  |  Account · ACL · Device Twin · Schedule        |
  |  OTA Policy · Consent · Support Tokens         |
  +------+-------------+-------------+-------------+
         |             |             |
         v             v             v
  +------------+ +-----------+ +------------------+
  | Twin Store | | Object     | | Telemetry Bus    |
  | (desired/  | | Store     | | (status, errors) |
  | reported)  | | map bak   | +--------+---------+
  +------------+ | OTA arts  |          |
                 +-----------+          v
                                   Analytics / Fleet
                                   Health (aggregated)

         MQTT/IoT / WebSocket (commands + twin)
                         |
                         v
  +------------------------------------------------+
  |                 Robot (edge)                   |
  | +-------------+  +--------------+  +---------+ |
  | | Safety MCU  |  | Nav SoC      |  | Wi‑Fi   | |
  | | cliffs/bump |  | SLAM/planner |  | agent   | |
  | | e-stop      |  | mission FSM  |  | twin    | |
  | +-------------+  +------+-------+  +----+----+ |
  |                         |                   |  |
  |         motors / vac / brush / dock IR      |  |
  +------------------------------------------------+
                         ^
                         | charge + fiducial
                    +-----+-----+
                    |   Dock    |
                    +-----------+
```

**Mission path (online start):**

```text
App StartMission
  -> Cloud sets twin.desired.mission
  -> Device pulls/pushes twin
  -> Onboard Mission FSM accepts
  -> Planner uses local FloorMap
  -> Execute coverage; publish reported status
  -> Complete / Dock; checkpoint clear
```

**Offline path:**

```text
Wi‑Fi down
  -> Use cached schedule / last desired
  -> Full clean with local map
  -> Queue telemetry + twin reported
  -> On reconnect: sync; resolve map edits (version vector)
```

**Dock-resume path:**

```text
SOC < RETURN
  -> Save coverage_checkpoint + pose
  -> Navigate to dock; charge
  -> On wake: Relocalize; load checkpoint; continue uncovered
```

**Stuck recovery path:**

```text
Escape behaviors (back out, wiggle, alternate)
  -> if fail: ERROR_STUCK; notify user with map pin
  -> optional opt-in snapshot (blurred)
  -> user Rescue -> Relocalize or continue
```

**OTA path:**

```text
Cloud rollout policy -> device OTACheck
  -> Download from CDN (delta) while docked/charging
  -> Verify signature + hash
  -> Apply to inactive slot; reboot
  -> Health gates; else rollback slot
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Safety MCU can stop motors without SoC/cloud.**  
2. **Mission progress is checkpointed** before dock/reboot.  
3. **Map edits are versioned**; device rejects older no-go that would reopen stairs.  
4. **OTA only applies when docked** (or explicit safe state).  
5. **Cloud outage ≠ mission abort.**  
6. **Consent gates** all map/camera uploads.  
7. **Pose confidence below threshold ⇒ slow/stop**, don’t clean blind at speed.

#### 5.1.2 Mission FSM

```text
IDLE -> CLEANING -> (DOCKING -> CHARGING -> CLEANING)* -> DOCKING -> IDLE
                 \-> PAUSED -> CLEANING
                 \-> ERROR -> (user) -> IDLE|CLEANING
CLEANING -> OTA only if forced critical security & docked (rare)
```

#### 5.1.3 Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Soft kidnap | Pose jump / lidar mismatch | Recovery localization; else pause |
| Hard kidnap (carried) | IMU freefall + mismatch | New session / floor prompt |
| Dock miss | Approach timeout | Retry offsets; expand search; notify |
| Wheel stall | Current + no odom | Reverse escape; ERROR |
| Cliff | IR/ToF | Hard stop; replane away |
| Glass wall | Lidar may miss | Bump fusion; careful models |
| Map corruption | Checksum / sanity | Restore backup; remap |
| Twin split | Version conflict | CRDT-lite on no-go polygons; LWW on schedule |
| OTA brick risk | Boot health | A/B partition rollback |
| Telemetry storm | Rate | Backpressure; sample |

#### 5.1.4 Coverage correctness under resume

```text
coverage_bitmap C[cells]
on clean cell: C[i]=1
on dock: persist C + room_queue + map_version
on resume:
  if map_version changed incompatibly:
    revalidate no-go; keep C if geometry compatible else conservative replan
  continue argmin path over C==0 free cells
```

**Deal-breaker:** losing coverage state on charge cycle → user sees endless re-clean or skipped rooms.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Device twin monolith | HA pair; robot offline-OK |
| 10× | OTA herd | Waves + CDN + jitter |
| 100× | Telemetry hot partitions | Regional ingest; device_id hash |
| 1,000× | Support cannot SSH 100M homes | Autodiagnose packs; privacy-safe bundles |

### 5.2 Scalability

#### 5.2.1 Shard keys

| Plane | Key |
|-------|-----|
| Device twin | `robot_id` (home_id secondary) |
| Telemetry | `hash(robot_id)` → regional bus |
| Map objects | `home_id/floor_id/version` |
| OTA | release × cohort (sku, region, % ) |
| App API | `account_id` |

Robots do **not** shard planning across cloud workers for a single home in MVP.

#### 5.2.2 Telemetry pipeline

```text
Device batch (protobuf) -> IoT Hub / MQTT
  -> Pub/Sub
  -> Stream: realtime status for app (twin update)
  -> Batch: BigQuery/warehouse for fleet KPIs
PII policy: strip lat/lon if any; maps not in default stream
```

#### 5.2.3 Map sync protocol

```text
Device Map v12 (local)
Cloud backup v11 (encrypted)
App edit no-go -> cloud desired map_edit v13
Device merges polygons; bumps to v13; ack
Conflict: concurrent device remap vs app edit
  -> spatial merge; overlapping unknown -> prefer stricter (more obstacle/no-go)
```

#### 5.2.4 Progressive scale narrative

| Scale | Mechanism |
|-------|-----------|
| Baseline | Single region IoT + PG twins + GCS maps + CDN OTA |
| 10× | Shard twins; sampled telemetry; OTA canary automation |
| 100× | Multi-region home cell (data residency); edge MQTT PoPs |
| 1,000× | Cell fabric; on-device ML packs via delta; anonymous fleet learning |

#### 5.2.5 Multi-robot same home (Phase 1.5)

```text
Partition rooms between robots (static or auction)
Keep-out bubbles around each robot pose (local broadcast / cloud coordination slow OK)
Dock assignment exclusive
Never require sub-100ms cloud coordination — use spatial reservations
```

### 5.3 Maintainability

#### 5.3.1 Software layers on robot

```text
Safety MCU firmware (rare OTA, tiny surface)
Nav stack (SLAM, planner, controllers)
Application FSM (mission, twin, OTA agent)
Perception models (dirt, obstacle) — versioned NPU blobs
```

Contract: **capability flags** in twin; cloud never sends commands the SKU can’t run.

#### 5.3.2 Observability

| Metric / signal | Why |
|-----------------|-----|
| `coverage_pct_final` | Product quality |
| `dock_success_rate` | Hardware + planner |
| `stuck_rate` / escape success | Nav health |
| `pose_confidence_p50` | SLAM health |
| `mission_interrupt_wifi` | Should be ~0 impact |
| `ota_fail_rate` by cohort | Rollout gate |
| `map_backup_consent_rate` | Privacy UX |
| `twin_lag_seconds` | Cloud health |
| `bin_full_pause_rate` | Consumables UX |

**Support pack (user-approved):** recent error codes, map version, coverage image **rendered**, not raw lidar dump by default.

#### 5.3.3 OTA maintainability

| Practice | Detail |
|----------|--------|
| Signed artifacts | Hardware root of trust |
| A/B slots | Instant rollback |
| Health gates | dock success, crash-free hours |
| Feature flags | Server-side kill switches for new planner |
| Delta encoding | bsdiff / custom for flash limits |
| Critical security | Faster waves but still dock-only apply |

#### 5.3.4 Privacy engineering

```text
Key hierarchy:
  User passphrase / account-bound key → wraps map DEK
  Cloud stores ciphertext; optional client-side E2E (stronger story)

Analytics path:
  Robot computes coverage_pct, stuck_code counters
  Upload aggregates only

Training path (Phase 2):
  Federated learning for dirt/obstacle optional
  Or opt-in dataset with explicit consent + retention
```

#### 5.3.5 Configuration vs code

Room names, schedules, no-go → **data** in twin/map.  
Planner algorithms → **firmware**.  
Don’t ship per-home custom firmware.

### 5.4 Scheduling

```text
Cloud: RRULE / cron in account TZ
Device: materialize next K missions; honor quiet hours locally
Presence: optional phone-home / Nest signals → skip if occupied (Phase 1.5)
Conflict: user StartMission preempts schedule; mark skipped instance
```

### 5.5 Security

| Threat | Mitigation |
|--------|------------|
| Rogue OTA | Sign + secure boot |
| Neighbor Wi‑Fi attack | Device creds; TLS; rotate |
| Stolen robot | Account unlink; wipe on re-pair |
| Map leak | Encrypt; consent; audit |
| Command injection | AuthZ on twin; schema allowlist |
| Malicious no-go removal exposing stairs | Stricter-merge + cliff sensors always on |

**Deal-breaker:** unsigned firmware “for convenience.”

### 5.6 Progressive scale story

> **Baseline:** robot-local SLAM/coverage/dock; cloud twin + schedules; opt-in map backup; signed OTA.  
> **10×:** telemetry sampling, OTA waves, support packs, dirt layer.  
> **100×:** regional cells, residency, multi-robot homes, federated analytics hooks.  
> **1,000×:** cloud becomes pure control-plane commodity; autonomy + privacy hardened so cleartext home geometry never needs to be a core dependency.

---

## 6. Wrap-Up

### 6.1 Decisions locked

| Area | Decision |
|------|----------|
| Authority | Robot SoT for nav/mission; cloud SoT for policy/OTA/schedule |
| Mapping | Onboard SLAM; per-floor maps; versioned edits |
| Coverage | Room order + boustrophedon + dirt bias + checkpoints |
| Docking | Threshold return + resume from coverage bitmap |
| Privacy | Local-first maps; opt-in encrypted backup |
| Connectivity | Twin eventual consistency; offline clean OK |
| OTA | Signed A/B, staged, dock-only, health-gated |
| Scale | Don’t upload the control loop; shard twins/telemetry |

### 6.2 Deal-breakers called out

- Cloud closed-loop motor control  
- Mandatory cleartext cloud maps  
- Random-walk coverage as the design  
- OTA while undocked driving  
- Losing resume state on charge  
- One map for all floors  
- Continuous raw video upload as telemetry  

### 6.3 30-second close

> The robot is a real-time autonomous system that owns mapping, coverage, safety, and docking; the cloud is a fleet control plane for identity, schedules, privacy-preserving backup, and OTA. We scale by keeping high-rate sensing on-device, syncing twins and encrypted maps infrequently, and treating home geometry as sensitive data—not just another JSON blob in the data warehouse.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & product

**Q1: Why not remote-control cleaning from the phone?**  
A: Latency, attention, Wi‑Fi holes; autonomy is the product. Teleop is emergency/support only.

**Q2: What’s “done” for a mission?**  
A: Coverage threshold of free cells + rooms requested; or user stop; expose % honestly.

**Q3: Mopping?**  
A: Separate tool path / water tank FSM; keep out of MVP unless interviewer insists—note carpet detection.

**Q4: Pets?**  
A: Dynamic obstacles; no-go litter; don’t chase; pause on tangle.

**Q5: Renters / multi-user?**  
A: Home ACL roles; guest can start but not export maps.

### 7.2 SLAM & maps

**Q6: 2D vs 3D maps?**  
A: 2D occupancy MVP; 3D/height for under-sofa clearance Phase 1.5.

**Q7: How to handle glass?**  
A: Sensor fusion with bump; ultrasonic optional; conservative unknown.

**Q8: Loop closure failures?**  
A: Pose confidence; remap regions; don’t assert global consistency falsely.

**Q9: Map size growth?**  
A: Bound resolution; prune transient obstacles; compress; version GC.

**Q10: Can cloud improve maps?**  
A: Offline cleanup on opt-in uploads; push as suggestions; device accepts.

**Q11: Semantic rooms?**  
A: Auto-segment + user rename; planner uses room graph.

### 7.3 Planning & coverage

**Q12: Incomplete coverage causes?**  
A: Blocked cells, no-go, cliff borders, time budget—surface in app.

**Q13: Why checkpoints?**  
A: Multi-trip cleans; power loss; OTA; crash recovery.

**Q14: Dynamic replanning cost?**  
A: Local window expensive sensors; global room order cheap.

**Q15: Optimal coverage NP-hard — what do you do?**  
A: Heuristics with completeness tracking; optimality not required.

**Q16: Spot clean after spill?**  
A: App pin → local spiral / bounded coverage.

### 7.4 Docking & power

**Q17: How localize dock?**  
A: Last pose prior + IR/fiducial + lidar template.

**Q18: What if dock moved?**  
A: Search behavior; user confirmation; update dock pose on map.

**Q19: Battery model?**  
A: SOC + predicted consumption by mode; return with margin.

**Q20: Charge partial then resume?**  
A: Yes—threshold resume SOC configurable.

### 7.5 Multi-floor & multi-robot

**Q21: Stairs?**  
A: Cliff sensors mandatory; no-go at stairs; never “learn” stairs as free.

**Q22: Elevators?**  
A: Out of scope for home MVP.

**Q23: Two robots same floor?**  
A: Partition rooms; reserved radius; dock mutex.

**Q24: Floor auto-detect wrong?**  
A: Fingerprint confidence; ask user; don’t clean with low confidence.

### 7.6 Privacy & security

**Q25: Are maps PII?**  
A: Treat as sensitive—reveal lifestyle, valuables layout, absence patterns.

**Q26: E2E vs server-side encrypt?**  
A: E2E stronger; server-side enables support/ML—product choice with consent tiers.

**Q27: Lawful access?**  
A: Follow policy; minimize retention; prefer device-local.

**Q28: Open-source nav stack risk?**  
A: Supply chain pin; signed builds; SBOM.

**Q29: Can support see my house?**  
A: Only with user-issued time-boxed token; audit log.

### 7.7 OTA & fleet

**Q30: How fast to patch critical CVE?**  
A: Accelerated waves still dock-gated; measure uptake; remind users undocked.

**Q31: Schema change in twin?**  
A: Versioned protobuf; backward compatible reads.

**Q32: Canary bad planner?**  
A: Health gates on stuck/dock metrics; auto pause rollout.

**Q33: Delta OTA failure?**  
A: Fall back to full image; verify hash; don’t brick.

### 7.8 Reliability & recovery

**Q34: Kidnapped robot algorithm?**  
A: Global localization / particle filter; else user places on dock.

**Q35: Infinite stuck loop?**  
A: Escape budget; then ERROR; don’t drain battery forever.

**Q36: Clock skew for schedules?**  
A: Device NTP when online; local TZ rules cached; cloud sends UTC + TZ id.

**Q37: Partial map sync?**  
A: Content-addressed chunks; resume upload; encrypt chunks.

### 7.9 Estimation drills

**Q38: Why not stream lidar to cloud?**  
A: 1M robots × ~10–100 Mbps peaks → impossible + private.

**Q39: Telemetry sampling math?**  
A: Show 1 Hz vs 0.1 Hz cost; event-driven errors.

**Q40: OTA herd?**  
A: 10M × 100 MB; must stage + delta + CDN.

### 7.10 Alternatives & deal-breakers

**Q41: Pure cloud brain?**  
A: Fails offline, safety RTT, privacy—reject.

**Q42: Only bump-and-go?**  
A: Misses modern completeness / map product bar.

**Q43: Store all videos for ML?**  
A: Cost + privacy deal-breaker without strict opt-in sampling.

**Q44: GPS for indoors?**  
A: Unreliable; map-relative poses.

### 7.11 Interview craft

**Q45: How to open?**  
A: Edge vs cloud authority, offline, privacy, docking resume, multi-floor—then sensors/SKU.

**Q46: What numbers matter?**  
A: Fleet size, telemetry rate, map size, OTA package, mission duration vs battery, coverage cell count.

**Q47: What impresses L5+?**  
A: Safety MCU invariant, resume checkpoints, stricter map merge, consent tiers, OTA health gates, progressive fleet scale without centralizing nav.

**Q48: Common mistake?**  
A: Drawing only cloud microservices and forgetting the robot is the system.

---

### Appendix A — Coverage checkpoint schema

```text
CoverageCheckpoint {
  mission_id,
  map_version,
  floor_id,
  bitmap_compressed,    // free cells cleaned
  room_queue_remaining,
  dirt_targets_remaining,
  pose_last,
  saved_at
}
```

### Appendix B — Twin desired/reported

```text
desired:
  mission_cmd, schedule, no_go_edit, rooms_edit,
  ota_target_version, privacy_prefs
reported:
  mode, battery, map_version, mission_id, coverage_pct,
  error_code, firmware_ver, docked, consent_flags
```

### Appendix C — Escape behavior sketch

```text
onStuck:
  for pattern in [reverse, left_arc, right_arc, spiral_out]:
    try pattern for T ms
    if free: return RECOVERED
  enter ERROR_STUCK; notify; await user
```

### Appendix D — Stricter map merge

```text
merged_occupancy = max(obstacle_severity(a), obstacle_severity(b))
merged_nogo = union(nogo_a, nogo_b)
merged_free only if both agree free (or high-confidence sensor)
```

### Appendix E — Dirt layer EMA

```text
dirt[cell] = α * sample + (1-α) * dirt[cell]
decay daily: dirt *= β
planner_cost(cell) = base + w * dirt[cell] if not cleaned_this_mission
```

### Appendix F — OTA health gates

| Gate | Threshold example |
|------|-------------------|
| Crash-free boot | >99% cohort |
| Dock success | no regression >0.5pp |
| Stuck rate | no spike >20% relative |
| Battery anomalies | no thermal trip spike |

### Appendix G — Telemetry event types

```text
STATUS_PERIODIC, MISSION_START, MISSION_END,
DOCK_SUCCESS, DOCK_FAIL, STUCK, CLIFF, BIN_FULL,
MAP_VERSION_BUMP, OTA_RESULT, CONSENT_CHANGE
```

### Appendix H — Progressive scale table

| Scale | Twin | Telemetry | Maps | OTA |
|-------|------|-----------|------|-----|
| Baseline | 1 region PG | MQTT→bus | GCS | CDN full |
| 10× | Sharded | Sampling | Version GC | Canary waves |
| 100× | Geo cells | Regional | Residency | Delta |
| 1,000× | Fabric | Edge aggregate | E2E default | P2P/regional cache |

### Appendix I — NFR card

```text
Offline clean: required
Safety stop: on-device only
Dock success ≥99% when reachable
Coverage resume across charges
Maps local-first + consent
OTA signed A/B dock-only
Cloud down ≠ robots down
```

### Appendix J — Room graph planner

```text
rooms = nodes; doorways = edges
order ≈ nearest-neighbor TSP from dock
for room in order:
  cover(room)
  update C
return dock
```

### Appendix K — Pose confidence policy

```text
if confidence > T_high: normal speed
elif confidence > T_low: slow + relocalize
else: stop; recovery; user prompt
```

### Appendix L — Privacy tiers

| Tier | Maps cloud | Cameras | Analytics |
|------|------------|---------|-----------|
| 0 Default | None | None | Aggregates |
| 1 Backup | Encrypted | None | Aggregates |
| 2 Support | Time-boxed | Optional clip | — |
| 3 Research | Opt-in dataset | Opt-in | Contractual |

### Appendix M — Multi-floor fingerprint

```text
features = WiFi BSSID set + RSSI sketch + map hash
match score -> suggest floor_id
if score < T: ask user
```

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Cloud SLAM is fine” | RTT + outage + privacy |
| “Just upload everything” | Bandwidth × fleet + sensitive layout |
| “Random walk works” | Completeness & product expectations |
| “Maps aren’t sensitive” | They are—layout + routines |

### Appendix O — Related systems (conceptual)

| System | Relation |
|--------|----------|
| IoT Core / MQTT | Device channel |
| Device twin | Desired/reported |
| GCS / S3 | Map backup, OTA |
| Pub/Sub | Telemetry |
| CDN | OTA artifacts |
| Home app | UX surface |
| Federated learning | Optional model improve |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| SLAM | Simultaneous localization and mapping |
| Coverage bitmap | Which free cells cleaned |
| Twin | Cloud desired vs device reported |
| Kidnap | Robot moved without odometry |
| No-go | User forbidden region |
| A/B OTA | Dual firmware slots |
| Boustrophedon | Lawn-mower coverage pattern |

### Appendix Q — Worked example (mission)

```text
100 m² apartment, 10k cells @ 0.1m
Robot cleans 70% → SOC low → checkpoint 7k bits set
Dock 30 min → resume → clean remaining 3k
Dirt layer triggers +5 min kitchen re-pass
Total: 2 trips; app shows 96% coverage (blocked cells explained)
```

### Appendix R — Worked example (fleet telemetry)

```text
1M robots, 15% cleaning
Reports @ 0.2 Hz, 250 B
0.15 × 1e6 × 0.2 × 250 = 7.5 MB/s average ingest
Peak evening ×3 → ~22 MB/s — one regional pipeline
```

### Appendix S — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Live pose in cloud? | Soft, lagged, not authoritative |
| No-go strong consistency? | Device applies before clean near zone |
| Schedule exact second? | Best-effort; local TZ |
| Map backup freshness? | Eventual; after mission/edit |

### Appendix T — 30m interview checklist

1. Clarify edge vs cloud authority, offline, privacy.  
2. Sensors → SLAM → coverage → dock resume.  
3. BOTE: reject lidar streaming; size OTA/telemetry.  
4. Draw robot stack + twin + OTA + encrypted maps.  
5. Failure: stuck, kidnap, dock miss, bad OTA.  
6. Multi-floor + dirt layer.  
7. 10×/100×/1,000× fleet story + deal-breakers.

### Appendix U — Safety requirements (non-negotiable)

```text
Cliff stop independent of planner
Bumper stop independent of Wi‑Fi
Thermal / motor overcurrent limits
Pinch mitigation via torque + geometry
Child lock / app auth for start
```

### Appendix V — What changes at each scale (quick card)

| Scale | Must add |
|-------|----------|
| 10× | Sampling, canary OTA, twin shard |
| 100× | Regional cells, residency, support packs |
| 1,000× | E2E maps default, edge aggregate, multi-robot norms |

### Appendix W — Command idempotency

```text
StartMission(cmd_id)
device: if cmd_id seen: return prior accept
else: accept -> mission_id
cloud: retries safe
```

### Appendix X — Why not ROS-in-cloud

```text
ROS graphs assume local high-bandwidth, low-latency bus.
Stretching ROS topics across Internet breaks safety and SLAM.
Use ROS/onboard middleware locally; cloud = product APIs.
```

---

*End of House-Cleaning Robot system design.*
