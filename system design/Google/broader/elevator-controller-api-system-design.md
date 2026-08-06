# System Design: Elevator Controller / Elevator API

> **Focus areas:** Scheduling (SCAN/LOOK) · Multi-elevator assignment · Control APIs · Failure handling · Fairness · Simulation vs embedded hybrid  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit control-loop vs cloud API split, deterministic scheduling invariants, deal-breakers for “cloud RPC per floor sensor tick” fantasies  
> **Interview theme:** Google L5+ algorithmic + systems hybrid — real-time constraints, safety, multi-car optimization, and operable APIs for building management

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

Goal: **bound the product**—an **elevator control system** (and optional cloud API) that assigns hall calls to cars, schedules stops with SCAN/LOOK-like policies, handles failures safely, and exposes APIs for status/ops—clarifying what runs on-prem real-time vs cloud.

### 1.0 What this is / is not

| Dimension | **Elevator controller / API (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Move cars safely & efficiently for hall/car calls | Generic robot fleet in city |
| Success | Safety first; bounded wait; fairness | Perfect globally optimal NP-hard assign each ms |
| Control | Hard RT loop on-prem / bank controller | Cloud round-trip for door close decisions |
| API | Status, summon (where allowed), analytics, config | Mobile app replaces emergency systems |
| Scale | Many buildings × banks × cars | One toy 3-floor sim only |

**Scope statement:** Design an elevator controller (algorithmic + system): scheduling SCAN/LOOK, multi-elevator assignment, APIs, failure modes, fairness—with progressive scale from single bank to city building fleet.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Inputs? | Hall call (floor, dir), car call (dest), sensors | Event model |
| F2 | Outputs? | Next commits: move, stop, door open/close | Command interface |
| F3 | Algorithms? | LOOK/SCAN variants; discuss SSTF | Scheduler module |
| F4 | Multi-car? | Yes — assign hall call to best car | Cost function |
| F5 | Zones? | Optional express / low-high rise | Partition floors |
| F6 | APIs? | Building mgmt: status, stats, mode; limited summon | API gateway |
| F7 | Modes? | Normal, fire, evacuation, maintenance, peak | Mode manager |
| F8 | Fairness? | No starvation of top floors | Aging / SCAN |
| F9 | Failures? | Sensor fault, car offline, network split | Safe defaults |
| F10 | Simulation? | Yes for testing & cloud digital twin | Same scheduler lib |
| F11 | Destination dispatch? | Phase 1.5 (keypad in lobby) | Different assigner |
| F12 | Crowds / weight? | Load sensors; skip full cars | Capacity in cost |

**MVP functional scope:**

1. Model building: floors, cars, doors, speed/accel profiles (simplified).  
2. Accept hall calls + car calls; schedule stops.  
3. Multi-car assignment with cost heuristic.  
4. LOOK (or SCAN) direction service within a car.  
5. Modes: normal + maintenance + fire recall stub.  
6. Telemetry stream to cloud; read APIs for status.  
7. Limited remote summon only if building policy allows (with auth).  
8. Failure: car out of service; reassign pending hall calls.  
9. Simulator for CI and load tests.

**Out of MVP:**

- Full SIL-rated safety certification package (mention safety PLC separate)  
- Perfect MILP optimal group control each second  
- Robotaxi-style city routing  
- Mobile “call elevator from home” without security model

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Safety | Hard interlocks local | Never cloud-dependent for safety |
| N2 | Control latency | Door/motion loop local | ms–tens ms on bank controller |
| N3 | Assignment latency | Hall button feel instant | < 100ms ack; schedule continuous |
| N4 | Availability | Elevators usable if cloud down | Island mode on-prem |
| N5 | Fairness | Bounded wait | No unbounded starvation |
| N6 | Observability | Ops dashboards | Telemetry ≤ few seconds lag |
| N7 | Determinism (sim) | Replayable | Seeded sim == traces |
| N8 | Security | API authZ | No unauth motion commands |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Hall up@5 → assign car B → LOOK serves 5 → rider car-calls 12 → continues up.  
2. Two hall calls same direction → one car sweeps both.  
3. Peak morning up-peak → bias parking / zoning.  
4. Car C fault → calls reassigned; C doors locked maintenance.  
5. Cloud API `GET /banks/{id}/status` shows positions.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Conflicting dirs same floor | Two hall buttons; serve per direction queues |
| Full car | Skip hall stop if overweight; reassign |
| Door obstruction | Reopen retries; alarm; don’t leave |
| Controller reboot | Persist active calls in NVRAM / peers |
| Clock skew cloud | Telemetry only; control uses monotonic local |
| Network split cloud↔bank | Bank continues; API shows degraded |
| Starvation top floors | SCAN/LOOK + aging cost |
| Simultaneous assign race | Single assigner thread / lock per bank |
| Fire mode | Recall to lobby; ignore normal hall |
| Misleveling | Safety stop; out-of-service |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Buildings | 100 | 1K | 10K | 100K |
| Cars total | 500 | 5K | 50K | 500K |
| Hall calls / min (fleet) | 1K | 10K | 100K | 1M |
| Telemetry points / s | 5K | 50K | 500K | 5M |
| API read QPS | 100 | 1K | 10K | 100K |
| Banks per controller | 1–2 | 2–4 | cells | regional ops |
| Sim events / s (CI) | 10K | 100K | 1M | distributed sim |

**What each jump forces:**

- **10×:** Multi-tenant cloud telemetry; bank controllers still local; device twin.  
- **100×:** Regional IoT ingest; config/push; anomaly detection.  
- **1,000×:** Hierarchical ops; edge gateways; sharded digital twins; no central assigner for all buildings.

### 1.5 Etc. (Constraints & Assumptions)

- **Critical ambiguity:** Is this embedded control design, cloud orchestration, or both? Answer: **on-prem RT control + cloud API/analytics**; never put safety in cloud.  
- Physics simplified: constant accel segments OK for interview.  
- Destination dispatch (lobby keypad) is a major variant—call out.  
- Safety PLCs / overspeed governors are out of software scope but acknowledged.

**Scope statement to repeat back:**

> Design a multi-elevator bank controller using LOOK/SCAN-style serving and cost-based hall-call assignment, with safe on-prem real-time control, failure reassignment, fairness against starvation, and a cloud API for telemetry/ops—scaling to many buildings without centralizing motion control.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Rate | Plane |
|-------|------|------|-------|
| **Sensor/control ticks** | Position, door, load | 10–100 Hz / car | On-prem RT |
| **Hall/car call events** | Human | low per bank | On-prem |
| **Assignment decisions** | On each call / idle | bursty | On-prem bank CPU |
| **Telemetry export** | State snapshots | 1–5 Hz / car | Edge → cloud |
| **Cloud API reads** | Dashboards | varies | Cloud |
| **Config push** | Rare | low | Cloud → bank |

**Anti-pattern:** one QPS for “elevator system” mixing door interlocks and REST GETs.

### 2.2 Latency budgets

```text
Door close decision: local << 50ms (safety/UX)
Hall call ack light: < 100ms local
Cloud summon (if enabled): 200–500ms + still local execute
Telemetry to dashboard: 1–5s OK
```

### 2.3 State size

```text
Car state ~256B–1KB
Bank with 8 cars + call queues ~ tens of KB
100K buildings × avg 4 cars telemetry 1 Hz × 500B ≈ 200 MB/s raw → compress, sample, regional ingest
```

### 2.4 Scheduling complexity

```text
Naive optimal assignment: exponential in calls×cars
Heuristic cost O(cars × pending) per new hall call — fine for 8 cars × 20 calls
Recompute periodically O(same)
```

### 2.5 Fairness metric

```text
Target: p95 hall wait < 60–90s normal; measure per floor
Starvation: max wait unbounded under pure SSTF → reject pure SSTF as sole policy
```

---

## 3. High-Level Design

### 3.1 API (cloud / BMS)

| Op | Semantics |
|----|-----------|
| `GET /v1/buildings/{id}/banks` | List banks/cars |
| `GET /v1/banks/{id}/status` | Positions, dirs, modes, queues |
| `GET /v1/banks/{id}/metrics` | Wait times, trips |
| `POST /v1/banks/{id}/mode` | maintenance/fire/normal (auth) |
| `POST /v1/hallcalls` | Optional remote summon `{floor,dir}` |
| `WS /v1/banks/{id}/stream` | Live telemetry |
| `POST /internal/sim/run` | Simulation jobs |

**On-prem control API (local bus):**

```text
HallCall(floor, dir)
CarCall(car_id, floor)
SetMode(mode)
OutOfService(car_id)
TelemetrySnapshot()
```

### 3.2 Data model

| Entity | Key fields |
|--------|------------|
| Building | floors, banks |
| Bank | cars[], floor range, policy |
| Car | floor, target, dir, load, door, mode, commits[] |
| HallCall | floor, dir, ts, assigned_car?, age |
| CarCall | car_id, floor, ts |
| Trip / Metric | waits, service times |
| Mode | NORMAL, FIRE, EVAC, MAINT, UP_PEAK, DOWN_PEAK |

### 3.3 Per-car scheduling — Why X over Y

| Algorithm | Behavior | Pros | Cons |
|-----------|----------|------|------|
| **FCFS** | Serve calls in order | Simple | Terrible travel |
| **SSTF** | Nearest floor | Short travel | **Starvation** |
| **SCAN** | Sweep to end, reverse | Fair-ish | Wasted ends |
| **LOOK** | Sweep to last request, reverse | Better than SCAN | Still heuristic |
| **Destination dispatch** | Batch assign by dest | High throughput | UX/hardware |

**Chosen MVP:** **LOOK** within car direction; hall calls only assigned if compatible or idle.

```text
Car direction UP:
  serve car calls & hall-UP stops above >= current in increasing order
  at highest needed: reverse to DOWN LOOK
Symmetric for DOWN
Idle: park policy (lobby / balanced)
```

**Deal-breaker:** SSTF-only in a tall building (top-floor starvation).

### 3.4 Multi-car assignment — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| **Nearest car** | Simple | Ignores direction/load |
| **Cost function** | Tunable | Heuristic |
| **Zoning** | Predictable | Underutilizes |
| **Central MILP** | Optimal-ish | Too slow / brittle |

**Cost sketch:**

```text
cost(car, hall_call) =
  ETA_to_pickup(car, call)
  + (penalty if direction mismatch / must reverse)
  + load_penalty
  + queue_length_penalty
  - aging_bonus(call.wait)
Assign argmin cost among feasible cars
```

### 3.5 Control plane vs data plane

```text
Safety & motion: on-prem bank controller (hard RT / soft RT)
Assignment & LOOK: on-prem (same process or co-located)
Cloud: telemetry, config, analytics, optional summon request forward
Digital twin: cloud sim mirrors for what-if; not authoritative
```

**Deal-breaker:** cloud service as sole scheduler for door commands.

### 3.6 Why X over Y (summary table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Safety locus | On-prem | Life safety | Cloud RPC door close |
| Serve policy | LOOK + aging | Efficiency + fairness | Pure SSTF |
| Assignment | Cost heuristic | Practical | Exact OR-Tools every 10ms |
| Cloud role | Telemetry/API | Scale ops | Required for motion |
| State | Bank leader | Consistency | Every car independent conflicting assigns |
| Sim | Shared lib | Test fidelity | Separate untested heuristic in prod |

---

## 4. Architecture Diagram

```text
                 +-------------------------+
  Hall/Car btns->|  Bank Controller        |
  Sensors ------>|  - Call Manager         |
                 |  - Assigner             |
                 |  - Per-car LOOK sched   |
                 |  - Mode Manager         |
                 |  - Safety interlocks    |
                 +----+---------+----------+
                      |         |
                      v         v
                 Car Drives   Door/Io
                      |
                      | telemetry (edge gateway)
                      v
               +------+-------+
               | Cloud Ingest |--> Time-series / Bigtable
               +------+-------+
                      |
                      v
               +------+-------+     +----------------+
               | Elevator API |<--->| Building Mgmt  |
               | AuthZ, WS    |     | Dashboards     |
               +--------------+     +----------------+

  CI Simulator --> same Assigner/LOOK library --> golden traces
```

**Hall call path:**

```text
HallCall(floor, UP)
  -> enqueue pending
  -> assigner picks car with min cost
  -> car.scheduler.addStop(floor, HALL_UP)
  -> ack light on
  -> car LOOK includes stop when direction compatible
```

**Serve loop (per car, conceptual):**

```text
loop:
  update position from sensors
  if at committed floor within tol:
    stop; open door; dwell; clear calls at floor
  else:
    choose next target from LOOK queue
    command motion
  emit telemetry tick
```

**Failure path:**

```text
Car fault -> mode OOS
  unassign its hall calls -> re-run assigner
  car calls inside: evacuate procedure / stop at nearest safe
  alert cloud + local alarm
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Safety interlocks never bypassed by cloud commands.**  
2. **At most one assigner** mutating hall assignments per bank.  
3. **Persisted calls** survive controller restart (NVRAM/peer).  
4. **Fire mode** overrides normal optimization.  
5. **Door open ⇒ motion inhibited** (interlock).  
6. **Fairness:** aging increases assignment priority.

#### 5.1.2 Failure modes

| Failure | Response |
|---------|----------|
| Position sensor disagree | Safe stop; OOS |
| Door repeated reopen | Alarm; out of service after N |
| Assigner crash | Warm standby bank controller |
| Cloud down | Island mode; local full function |
| Network flap summon | Idempotent summon ids; local dedupe |
| Power dip | Recall/park policy per code |

#### 5.1.3 Consistency of assignment

```text
Single-threaded event loop per bank (recommended MVP):
  process sensor events
  process new calls
  recompute assignments / schedules
  emit commands
Avoid distributed locks across cars for MVP
```

#### 5.1.4 Failure modes by scale (fleet)

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Bad deploy of scheduler | Sim golden tests; canary buildings |
| 10× | Telemetry flood | Sample + delta encoding |
| 100× | Config push breaks banks | Staged rollouts; local last-good config |
| 1,000× | Central API dependency creep | Hard enforce island mode tests |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| Bank | Unit of scheduling locality |
| Building | Security/tenancy |
| Region | Cloud telemetry shards |
| Car | Motion control only |

**Never** one global scheduler for 500K cars.

#### 5.2.2 Zoning & peak modes

```text
UP_PEAK: prefer lobby pickup; cars return lobby when idle
DOWN_PEAK: bias upper floors
ZONES: car A floors 1–10, car B 11–20 with overlap express
```

#### 5.2.3 Destination control (Phase 1.5)

```text
Lobby keypad: user enters dest
Batch assign group to cars
Reduces stops; changes API (no up/down hall)
```

#### 5.2.4 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Cloud twin + multi-tenant API |
| →100× | Regional ingest; anomaly; config fleet |
| →1,000× | Edge gateways; sharded ops; sim farm |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
bank.policy: {
  algorithm: "LOOK",
  aging_ms_bonus_per_s: 0.5,
  dwell_s: 3,
  capacity_kg: 1600,
  park: "LOBBY",
  remote_summon: false
}
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `hall_wait_s` p50/p95/max | UX/fairness |
| `stops_per_trip` | Efficiency |
| `reassigns` | Instability |
| `oos_cars` | Availability |
| `mode` | Safety ops |
| `cloud_lag` | Telemetry health |

#### 5.3.3 Testing

- Deterministic sim: scripted call arrivals → expected assigns.  
- Starvation tests (calls at floor 40 while lobby thrash).  
- Fault injection car OOS.  
- Fire mode compliance scripts.  
- Property: no two cars assigned conflicting exclusive claims incorrectly.

#### 5.3.4 Operability

- Shadow cost function `v2`.  
- Remote config with signed packages.  
- Blackbox replay from telemetry.

---

## 6. Wrap-Up

### 6.1 What we designed

An **elevator bank controller** that assigns hall calls via cost heuristics, serves stops with **LOOK**, enforces safety on-prem, handles OOS reassignment and modes, and exposes a **cloud API** for telemetry/ops—plus a shared simulator—not a cloud RTOS for doors.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| SCAN vs LOOK | LOOK preferred MVP |
| SSTF | Reject alone (starvation) |
| Cloud | Telemetry/API only for safety-critical |
| Assign | Heuristic cost + aging |
| Scale | Bank-local schedule |
| Destination dispatch | Phase 1.5 upgrade |

### 6.3 30-second scale narrative

> Baseline: on-prem bank event loop with LOOK + cost assigner; cloud status API. 10× adds multi-tenant telemetry. 100× regional ingest and fleet config. 1,000× edge gateways and sharded twins—motion control always island-capable.

### 6.4 Deal-breakers checklist

- Cloud-dependent door/motion safety.  
- Pure SSTF starvation.  
- Global scheduler for all buildings.  
- Unauthenticated remote summon.  
- No persistence of calls across reboot.  
- Optimality MILP as MVP blocking design.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Embedded or distributed systems interview?**  
A: Explicitly split RT on-prem vs cloud API; interviewers often want both.

**Q2: Up/down buttons vs destination keypad?**  
A: Traditional vs destination dispatch; algorithm changes.

**Q3: How many cars/floors?**  
A: Ask; 8 cars × 40 floors common stress.

**Q4: Freight vs passenger?**  
A: Separate banks/policies.

**Q5: Accessibility?**  
A: Longer dwell; priority modes.

### 7.2 Algorithms

**Q6: Explain SCAN vs LOOK.**  
A: SCAN goes to physical end; LOOK only to last request then reverse.

**Q7: Why not FCFS?**  
A: Excess travel; poor throughput.

**Q8: How does aging work?**  
A: Increase priority/cost bonus with wait time to prevent starvation.

**Q9: ETA estimation?**  
A: Distance/speed + expected stops × dwell + accel model.

**Q10: Is optimal group control NP-hard?**  
A: Variants are hard; heuristics used in industry.

**Q11: Sectoring / zoning tradeoff?**  
A: Reduces conflict; may increase wait if mis-zoned.

**Q12: Reassignment mid-flight?**  
A: Allowed for hall calls not yet picked up; avoid thrashing with hysteresis.

### 7.3 Multi-elevator assignment

**Q13: Cost features?**  
A: ETA, direction match, load, committed stops, aging.

**Q14: Can two cars serve same hall call?**  
A: No—exclusive assignment until pickup or reassign.

**Q15: Bunching problem?**  
A: Cars synchronize undesirably; anti-bunching parking/spacing.

### 7.4 Safety & reliability

**Q16: What belongs in safety PLC vs our software?**  
A: Overspeed, final limits, door locks—hardware/safety PLC; our software requests within envelope.

**Q17: Island mode?**  
A: Required—cloud optional.

**Q18: Split brain two controllers?**  
A: Leader election with hardware watchdog; dual control careful.

**Q19: Sensor fusion disagree?**  
A: Safe stop > continue optimized.

### 7.5 APIs & security

**Q20: Remote summon risks?**  
A: Prank/DoS/safety; auth, rate limit, building policy, audit.

**Q21: Tenancy?**  
A: Building-scoped tokens; no cross-building.

**Q22: Websocket fanout?**  
A: Per bank streams; don’t broadcast all cars globally to one client unless ops role.

### 7.6 Simulation

**Q23: Why sim?**  
A: CI, policy tuning, replay incidents.

**Q24: Real-time vs discrete event?**  
A: Discrete-event sim for speed; RT for HIL.

**Q25: Golden traces?**  
A: Deterministic seeds; compare metrics/assignments.

### 7.7 Estimation drills

**Q26: Telemetry at 100K buildings?**  
A: Must sample/regionally shard; can’t raw 100Hz to cloud.

**Q27: Assigner CPU?**  
A: Negligible vs motion; keep O(cars×calls).

**Q28: p95 wait target impact?**  
A: May need more cars / zoning / destination control—product not only code.

### 7.8 Alternatives & deal-breakers

**Q29: Microservices per car in cloud?**  
A: Cute; wrong for RT safety.

**Q30: Reinforcement learning scheduler MVP?**  
A: Research; not replace explainable LOOK under safety ops without huge validation.

**Q31: Central city brain?**  
A: Deal-breaker for motion; OK for energy analytics.

### 7.9 Interview craft

**Q32: How to open?**  
A: Safety locus, floors/cars, traditional vs destination, APIs, failure, fairness.

**Q33: What impresses L5+?**  
A: On-prem/cloud split, LOOK vs SSTF starvation, cost assigner, island mode, sim testing.

**Q34: Common mistake?**  
A: Jumping to cloud architecture; ignoring starvation; ignoring fire mode.

---

### Appendix A — LOOK pseudocode

```text
def next_target(car):
  if car.dir == UP:
    above = stops >= car.floor
    if above: return min(above)
    car.dir = DOWN
  if car.dir == DOWN:
    below = stops <= car.floor
    if below: return max(below)
    car.dir = UP
  return idle_park(car)
```

### Appendix B — Assign cost

```text
def cost(car, call):
  if car.mode != NORMAL: return ∞
  if car.load >= capacity: return ∞
  eta = estimate_eta(car, call.floor, call.dir)
  mismatch = reverse_penalty(car, call)
  age = now - call.ts
  return eta + mismatch + load_pen(car) - k*age
```

### Appendix C — Event loop

```text
for ev in events:
  match ev:
    HallCall: pending.add; assign()
    CarCall: car.stops.add
    Arrived: serve_floor(car)
    Fault: oos(car); reassign()
    Tick: command_motion()
```

### Appendix D — ETA sketch

```text
travel = abs(floor - car.floor) * sec_per_floor
stops = count_committed_between(...)
return travel + stops * dwell + accel_fudge
```

### Appendix E — Modes

```text
FIRE: all cars lobby recall; ignore hall; doors open lobby policy
MAINT: car OOS
UP_PEAK: idle cars park lobby; prioritize UP from lobby
```

### Appendix F — Telemetry schema

```text
{bank_id, car_id, floor_mm, dir, door, load, mode, ts_mono, ts_utc}
```

### Appendix G — Persistence

```text
NVRAM: pending hall calls, car calls, mode
On boot: reload; sanity check sensors; resume
```

### Appendix H — Progressive scale

| Scale | Control | Cloud | Sim |
|-------|---------|-------|-----|
| Baseline | 1 bank box | status API | local |
| 10× | many buildings | multi-tenant | CI |
| 100× | fleets | regional ingest | farm |
| 1,000× | edge GW | shard twins | distributed |

### Appendix I — Status JSON

```json
{
  "bank_id": "b1",
  "mode": "NORMAL",
  "cars": [{"id": "c1", "floor": 5, "dir": "UP", "load": 0.4}],
  "pending_hall": [{"floor": 9, "dir": "DOWN", "wait_s": 12}]
}
```

### Appendix J — NFR card

```text
safety local
LOOK + aging
island mode
assign <100ms ack
no SSTF-only
auth for summon
```

### Appendix K — Anti-bunching

```text
if idle: park to target spacing floors
penalize assigning second car too close same dir
```

### Appendix L — Comparison algorithms

| Algo | Throughput | Fairness | Complexity |
|------|------------|----------|------------|
| FCFS | Low | Med | Low |
| SSTF | Med | Poor | Low |
| SCAN | Med | Good | Low |
| LOOK | Good | Good | Low |
| Dest. dispatch | High | Good | Med |

### Appendix M — Security

| Threat | Control |
|--------|---------|
| Unauthorized summon | AuthZ + building policy |
| Command injection | Signed local bus |
| Telemetry PII | Minimal; floor traffic aggregates |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| Hall call | Floor request outside car |
| Car call | Destination inside car |
| LOOK | Sweep to last request |
| Bank | Group of cars sharing shaft group |
| Island mode | Operate without cloud |

### Appendix O — Worked example

```text
Cars at 1(idle), 10(UP to 15)
Hall UP@8 → cost: car1 ETA~7 floors; car2 must finish 15 then down...
Assign car1; LOOK up from 1→8
```

### Appendix P — Reassignment hysteresis

```text
only reassign if new_cost < old_cost - margin
prevents thrash
```

### Appendix Q — Consistency

| Question | Answer |
|----------|--------|
| Cloud status lag? | Seconds OK |
| Dual assigners? | No |
| Call after reboot? | Restored NVRAM |

### Appendix R — 30m checklist

1. Clarify safety locus, cars/floors, algorithm, API.  
2. Split RT vs cloud load.  
3. Draw bank controller + cloud.  
4. LOOK + cost assign + aging.  
5. Failures/modes.  
6. Scale fleet story.  
7. Deal-breakers.

### Appendix S — Dwell & door

```text
on stop:
  open; wait dwell or button; close with obstruction sensors
  clear hall/car calls for floor/dir
```

### Appendix T — Express elevators

```text
skip floors set; separate call eligibility
```

### Appendix U — Energy

```text
coalesce stops; idle power down; not safety-critical
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Cloud multi-tenant telemetry |
| 100× | Regional ingest, config fleet |
| 1,000× | Edge GW, sharded twins |

---

*End of Elevator Controller / Elevator API system design.*
