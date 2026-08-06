# System Design: Data Center on the Moon

> **Focus areas:** Earth–Moon latency (~1.3s one-way) · Power (solar/nuclear) · Thermal in vacuum · Radiation · Lunar dust · DTN / delay-tolerant networking · Storage hierarchy · Cross-link replication · Workload selection · Maintenance robotics · Progressive lunar capacity  
> **Style:** End-to-end infrastructure design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Physics constraints as **deal-breakers**, honest workload fit (batch/archive vs interactive), no hand-wavy “just run us-central1 on the Moon”  
> **Interview theme:** Unusual Google L5+ — space systems × distributed systems; light-speed, energy, and thermal dominate API design

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

Goal: **bound the product**—a **lunar data center** (compute + storage) linked to Earth, where **physics** (latency, power, thermal, vacuum, radiation, dust, launch mass) dictates architecture. Pick workloads that **benefit** from being on the Moon (or tolerate the penalties), and design networking/storage/ops accordingly.

### 1.0 What this is / is not

| Dimension | **Lunar data center (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Reliable compute/storage on Moon + Earth coordination | Drop-in GCP region with 50ms RTT fantasy |
| Success | Useful work completed under physics constraints | Beating Earth DCs on interactive web latency |
| Latency | ~1.3s one-way, ~2.6s+ RTT min (light) | “Tune TCP and it’ll feel local” |
| Power/thermal | First-class capacity planners | Infinite rack power assumed |
| Networking | DTN / scheduled links / high BER periods | Always-on fat pipe like metro fiber |
| Ops | Robotic + rare crewed; long lead times | Swap a DIMM tomorrow |
| Scale | Progressive MW-class growth over years | Instant 100k GPU cluster |

**Scope statement:** Design a Moon data center: site power/thermal, radiation-aware hardware, delay-tolerant networking to Earth, storage hierarchy with Earth replication, workload admission that respects physics, and progressive capacity scale—with maintenance robotics.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Why put a DC on the Moon at all? | Scientific archive near lunar instruments; backup off-Earth; deep-space relay compute; political/strategic diversity; low-temperature radiative cooling potential; later cislunar economy | Workload filter first |
| F2 | Who are customers? | Space agencies, lunar surface missions, Earth enterprises for **cold archive / batch**, research | Multi-tenant control plane on Earth |
| F3 | Interactive APIs from Earth browsers? | **No** as primary — min RTT kills UX | Batch jobs, async APIs, lunar-local services |
| F4 | Lunar-local clients? | Rovers, habitats, instruments with local low latency | Local fabric + Earth backhaul |
| F5 | Replication to Earth? | Yes for precious data; async, integrity-checked | DTN custody + erasure coding |
| F6 | Power source? | Mix: solar (+batteries/fuel cells) near poles; nuclear (fission) for permanence | Power budget = capacity budget |
| F7 | Cooling? | Radiators to space; no air convection | Thermal design ≫ CRAC nostalgia |
| F8 | Storage media? | Radiation-aware hierarchy: DRAM/SRAM scarce; flash/optical/tape-like cold | Tiering mandatory |
| F9 | Compute types? | CPU batch, some accel; not Earth-scale LLM training first | Admission control by joules |
| F10 | Link to Earth? | RF and/or optical (laser) via lunar orbiter relay and/or direct | Scheduled windows; weather/pointing |
| F11 | Maintenance? | Mostly robotic; spares prepositioned | Design for robot FRU swaps |
| F12 | Dust / regolith? | Sealed volumes; overpressure; connector standards | Contamination as reliability class |
| F13 | Soft/hard real-time lunar? | Habitat life support compute separate safety class | Isolate safety vs general DC |
| F14 | Multi-site on Moon? | Phase growth: one crater/pole site → secondary | Lunar WAN later |

**MVP functional scope:**

1. **Site systems:** power plant, energy storage, radiators, pressurized/sealed IT halls, dust mitigation.  
2. **IT payload:** radiation-tolerant or shielded commodity where viable; ECC everywhere; scrubbing.  
3. **Lunar fabric:** local high-speed network for lunar clients and intra-DC.  
4. **Earth–Moon network:** DTN with custody transfer; optical/RF links; orbiter relay option.  
5. **Workload classes:** lunar-local interactive OK; Earth↔Moon **async batch / archive / sync**.  
6. **Storage hierarchy** with integrity, Earth replicas, disaster durability.  
7. **Control plane:** Earth-side orchestration with delay-tolerant agent on Moon.  
8. **Ops:** robotic maintenance interfaces; telemetry; spare strategy.  
9. **Progressive capacity** roadmap tied to landed mass & power, not wishful rack count.

**Out of MVP:**

- Serving Google Search / Gmail interactive from lunar region  
- Assuming continuous multi-Tbps Earth link day-one  
- Crewed daily hardware swaps  
- Ignoring radiation SEUs  
- “Just Kubernetes with default etcd heartbeats” across Earth–Moon

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Min RTT Earth↔Moon | Physics | ≥ ~2.6s (+ protocol/queueing); often much more |
| N2 | Link availability | Not five-nines day one | Design for hours-long partitions |
| N3 | Data durability (precious science) | Extremely high | Multi-copy Moon + Earth; scrub |
| N4 | Power availability | Site-dependent | Poles: near-continuous solar; equator: 14d night → nuclear or huge storage |
| N5 | Thermal reject | Always | Radiator area sized to IT + losses |
| N6 | Radiation resilience | Continual SEUs / occasional storms | ECC, scrub, checkpoint, shielding |
| N7 | Ops response | Slow | Autonomy + robotics; Earth advise |
| N8 | Security | High (strategic asset) | Crypto, physical, supply chain |
| N9 | Lunar-local latency | Useful for surface users | << Earth RTT (local fabric µs–ms) |
| N10 | Progressive scale | Mass/power limited | Explicit 10×/100×/1,000× landed capability |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Lunar rover uploads instrument data → lunar DC stores + processes → DTN bundle to Earth archive.  
2. Earth scientist submits batch job (container + dataset ref) → DTN delivers → Moon executes near data → results return days later.  
3. Habitat runs local control dashboards against lunar DC APIs with ms latency.  
4. Night/solar outage (non-polar): nuclear baseload or batteries; IT sheds non-critical batch.  
5. Optical link window opens → custody transfer drains outbound queue at high rate.  
6. Robot swaps failed SSD tray; DC continues degraded RAID/EC.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Earth–Moon link blackout (days) | Local ops continue; queues grow; admission control |
| Solar proton event | Enter storm mode: throttle, shield doors, checkpoint flush |
| Radiator dust coating | Cleaning robots; derate IT power |
| Laser cloud-out on Earth ground station | Alternate ground sites; RF fallback; store-and-forward |
| etcd/Raft across Earth–Moon | **Don’t** — split control planes |
| Interactive Earth SSH “feel” | Bastion with async; expect multi-second pain; prefer job APIs |
| Bit flips in archival store | Scrub + EC + Earth cross-check |
| Launch loss of spare shipment | Cannibalize; degrade capacity; priority workloads |
| Vacuum leak in hall | Isolate compartment; safe shutdown procedures |
| Wrong workload admitted (chatty DB) | Reject at admission; classify by chattiness SLO |
| Time sync | Deep-space time protocols; don’t assume NTP simplicity |
| Political / ITAR / sovereignty | Data residency classes; Earth legal domain ≠ lunar |

### 1.4 Scales (Progressive)

| Metric | Baseline (pilot) | 10× | 100× | 1,000× |
|--------|------------------|-----|------|--------|
| IT power | ~50–100 kW | ~0.5–1 MW | ~5–10 MW | ~50–100 MW |
| Landed IT mass (order) | ~5–20 t | ~50–200 t | ~500–2,000 t | industrial |
| Earth link (peak) | 1–10 Gbps optical bursts | 10–100 Gbps | 0.1–1 Tbps | multi-Tbps constellation |
| Earth link (duty) | Windows / weather | More ground sites | Persistent relays | Cislunar backbone |
| Storage usable | ~1–10 PB | ~10–100 PB | ~0.1–1 EB | multi-EB |
| Compute | ~100–1k CPU cores | 10k | 100k | GPU/TPU class fleets |
| Lunar clients | Rovers/habitat pilot | Outpost | Multi-base | Settlements |
| Sites | 1 | 1 hardened | 2+ lunar sites | Lunar region fabric |
| Crew presence | Rare/none | Occasional | Rotating | Industrial ops |

**What each jump forces:**

- **10×:** Nuclear or polar power certainty; serious radiator farm; DTN ops maturity; robotic FRU.  
- **100×:** Multi-hall; Earth optical network; lunar-local ISP role; formal workload marketplace.  
- **1,000×:** True cislunar cloud; multi-site lunar replication; manufacturing/spares in-situ; still **not** Earth-interactive web region.

### 1.5 Etc. (Constraints & Assumptions)

- Distance ≈ 384,000 km → one-way light time ≈ **1.28 s** (use **~1.3 s**); RTT ≥ **~2.6 s**.  
- Vacuum: heat rejection primarily **radiation** (and conduction into structures)—no convective CRAC.  
- Lunar gravity ~1/6 g — helps structures/robots; dust is electrostatically nasty.  
- South polar peaks of eternal light / cold traps: attractive for solar + science archives.  
- Equatorial sites face ~14 Earth-day nights — **deal-breaker for solar-only MW IT** without absurd storage.  
- Launch cost/mass is the real “capex unit”; design for mass/power efficiency.  
- Earth already has cheap DCs — lunar DC must justify **why Moon**.

**Scope statement to repeat back:**

> Design a lunar data center whose capacity is gated by power, thermal rejection, radiation, dust, and landed mass; that serves lunar-local low-latency clients and Earth via delay-tolerant links (~1.3s one-way minimum); that stores/processes with a deliberate hierarchy and Earth replication; and that admits only workloads compatible with multi-second RTT and intermittent bandwidth—scaling from pilot kW to industrial MW under robotic operations.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Latency classes (critical)

| Class | Path | Min latency | Implication |
|-------|------|-------------|-------------|
| **Lunar-local** | Rover ↔ lunar DC | ms (RF/optical local) | Interactive OK |
| **Earth–Moon** | Earth DC ↔ lunar DC | ≥2.6s RTT | Async protocols |
| **Earth interactive** | Browser ↔ lunar origin | ≥2.6s + queues | **Deal-breaker UX** |

```text
TCP handshake ~1 RTT → already ≥2.6s before HTTP
TLS + app auth → usually multi-RTT → tens of seconds feel
Chatty DB (100 RTTs) → minutes — refuse
```

**Anti-pattern:** quoting “QPS of a GCP region” without a latency class split.

### 2.2 Power ↔ compute

```text
Pilot: 100 kW IT
PUE-like lunar factor: power for IT + cooling pumps/actuators + comms + losses
Radiators must reject ~IT heat (vacuum): rough q̇ = εσAT⁴
  → radiator area becomes a first-class BOM line

Example intuition (order-of-magnitude interview):
  Rejecting 100 kW at reasonable radiator T may need hundreds of m² class radiators
  (exact A depends on T, view factor, dust derate — show you know area scales with power)

Night (equator): 14 × 24 h ≈ 336 h
100 kW × 336 h = 33.6 MWh storage just for IT — enormous landed batteries
→ solar-only equatorial MW DC is a DEAL-BREAKER without nuclear
```

### 2.3 Link budget & volume

```text
Optical link burst 10 Gbps × 4 h window/day ≈ 18 TB/day raw
Science + backups may need more → queue, compress, prioritize, more windows/sites

Compare Earth metro: 10 Gbps continuous ≈ 108 TB/day — lunar is windowed

Custody queue sizing:
  blackout 3 days × ingress 5 TB/day ≈ 15 TB buffer on Moon + Earth
```

### 2.4 Storage durability math

```text
Precious lunar data: want loss rate << mission value
EC  k-of-n on Moon + async Earth replica
Scrub period short enough vs SER (soft error rate) under radiation

DRAM: expensive in joules/bits flipped — minimize; prefer checkpointed batch
Cold archive: write-once + verify + Earth copy before acknowledging “durable-to-Earth”
```

### 2.5 Mass budget thinking

```text
IT mass efficiency: PB/ton, kW/ton matter more than racks/sqft
Shielding mass can dominate — trade:
  - physical shielding (regolith berms / bury)
  - rad-hard parts (costly, slow)
  - commercial + ECC + software tolerance (common NASA/Google-y hybrid story)
```

### 2.6 Why Moon vs Earth cold archive

| Reason | Holds? | Note |
|--------|--------|------|
| Cheaper $ / GB | Usually **no** early | Launch costs dominate |
| Isolation from Earth disasters | **Yes** | True off-site |
| Near lunar instruments | **Yes** | Process in situ; send summaries |
| Lower latency to Earth users | **No** | Physics |
| Radiative cooling advantage | **Maybe** | Night/polar cold helps; dust/sun complicate |
| Legal / sovereignty diversity | **Maybe** | Policy-driven |

**Interview move:** state 2–3 concrete “why Moon” theses; reject the rest.

---

## 3. High-Level Design

### 3.1 Workload taxonomy (admit / reject)

| Workload | Lunar-local? | Earth↔Moon? | Verdict |
|----------|--------------|-------------|---------|
| Rover / habitat control assist | Yes | N/A | **Admit local** |
| Instrument pipeline near sensors | Yes | Results async to Earth | **Admit** |
| Cold archive / disaster vault | Store Moon | Async replicate Earth | **Admit** |
| Batch render / scientific HPC | Near data | Job submit async | **Admit** |
| Earth user web/API interactive | — | Chatty RTT | **Reject** |
| Cross-planet strongly consistent DB | — | CAP + RTT | **Reject** as single cluster |
| Earth training giant LLM | Power/mass | Link for gradients | Usually **reject early phases** |
| Content CDN for Earth | — | Worse than Earth PoP | **Reject** |
| DTN relay store-and-forward for deep space | Yes | Custody | **Admit** (mission fit) |

**Deal-breaker:** selling “us-moon1” as a general-purpose low-latency cloud region for Earth apps.

### 3.2 Site architecture (physics plane)

```text
Power:
  Polar solar arrays + batteries/regenerative fuel cells
  and/or Fission surface power (e.g. 40 kWe-class modules → arrays of them)
Thermal:
  Cold-plate loops → radiators (dust-tolerant design + cleaning)
  Shade / louvers; storm/thermal modes
Civil:
  Regolith berm shielding; buried or bermed halls
  Airlocks / sealed racks; overpressure against dust
Comms:
  Optical terminal(s) + RF backup; gimbal; orbiter relay pointing schedules
Robotics:
  External tenders; internal rail/arm for FRU
```

### 3.3 IT architecture (logical)

```text
Lunar Zone:
  Compute nodes (batch + local services)
  Storage: hot (flash) / warm / cold (dense)
  Lunar fabric (RoCE/Ethernet)
  DTN agents + custody stores
  Local control plane (schedulers, SDKs for surface clients)

Earth Zone:
  Customer APIs (async job + archive)
  Ground stations + DTN
  Earth replica warehouses
  Fleet ops, identity, billing
  Planning: power/thermal-aware capacity
```

### 3.4 Networking — Why X over Y

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **DTN (Bundle Protocol) + custody** | Survives partitions | Unfamiliar to web eng | **MVP backbone Earth↔Moon** |
| TCP end-to-end Earth–Moon | Familiar | Timers, stalls, chatty | Only inside tunnels carefully |
| QUIC magic | Better than naive TCP | Still light-speed bound | Local OK; not physics fix |
| Always-on VPN like metro | Simple mental model | Lies about availability | **Deal-breaker** as sole model |
| Store-and-forward via orbiter | Higher contact | Complexity | **Likely needed** |

**Chosen:**

```text
Lunar fabric: standard datacenter L3/L2, low RTT
Earth↔Moon: DTN bundles, custody transfer, priority classes
  L0: safety/telemetry
  L1: science raw
  L2: bulk archive / software images
Contact graph routing (CGR) for scheduled windows
Earth services expose async APIs: SubmitJob, GetJob, PutObject, GetObject (eventually)
```

**Deal-breaker:** Raft/Paxos quorum spanning Earth + Moon for primary control.

### 3.5 Storage hierarchy — Why X over Y

| Tier | Media (examples) | Role | Notes |
|------|------------------|------|-------|
| L0 | Rad-tolerant SRAM / protected DRAM | Working set | Small; scrub |
| L1 | Enterprise flash (shielded) | Hot lunar data | Wear + SEU scrub |
| L2 | Dense flash / future optical | Warm | |
| L3 | Ultra-cold (tape-analog / write-once) | Archive | Verify on write |
| Earth R | Multi-region object | Authoritative long-term for many datasets | Async |

**Durability protocol (precious data):**

```text
1. Write Moon EC stripe (k-of-n)
2. Scrub verify
3. Enqueue Earth replica bundles
4. ACK "Moon-durable" early if policy allows
5. ACK "Earth-durable" only after Earth custody confirm
Client chooses required durability class
```

### 3.6 Control plane — Why X over Y

| Model | Pros | Cons | Verdict |
|-------|------|------|---------|
| **Split planes** (Earth global + Moon local) | Matches RTT | Dual systems | **MVP** |
| Single global K8s | Familiar | Heartbeats die | **Deal-breaker** |
| Earth-only remote control | Simple | Blackouts halt Moon | Unsafe for local clients |
| Fully autonomous Moon | Resilient | Hard upgrades | Need both |

**Chosen:** Moon runs **autonomous local orchestrator** (scheduler, storage mgr, DTN). Earth runs **intent APIs** and desired-state that sync when contacts allow—like a device twin for a data center.

### 3.7 Cooling — Why X over Y

| Approach | Notes | Verdict |
|----------|-------|---------|
| Air CRAC like Earth | No atmosphere in vacuum outside; sealed air possible inside | Internal air OK **inside** habitat volume; still must reject heat via radiators |
| Fluid loop → radiator | Standard spacecraft | **Primary** |
| Regolith thermal sink | Slow; seasonal | Supplemental |
| Cryogenic polar advantage | Attractive for some storage | Site-dependent |

**Deal-breaker:** “vacuum is cold so servers stay cool by themselves” — vacuum is **insulation**; heat stays in the box unless radiated.

### 3.8 Power — Why X over Y

| Source | Pros | Cons | When |
|--------|------|------|------|
| **Polar solar + storage** | No fuel | Site-limited; dust on panels | Strong pilot candidate |
| **Fission surface power** | Night-proof; dense | Political/tech risk; heat rejection still needed | **Baseload for serious scale** |
| RTG | Reliable | Low power (W not MW) | Sensors, not DC |
| Earth-beamed power | Sci-fi | Hard | Out of MVP |

**Deal-breaker:** equatorial solar-only for continuous multi-100 kW IT without stating absurd battery mass.

### 3.9 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Workloads | Local interactive + async Earth | Physics | Earth web region fantasy |
| Earth link | DTN + scheduled optical/RF | Partitions | Always-on TCP WAN mental model |
| Consensus | Split planes | RTT | Cross-planet etcd |
| Power | Polar solar and/or fission | Night physics | Equatorial solar-only MW |
| Thermal | Fluid → radiators + dust plan | Vacuum | “Space cools servers for free” |
| Storage | Tier + EC + Earth replica | Radiation + value | Single unreplicated flash |
| Ops | Robotic FRU + autonomy | Rare crew | Earth-style break/fix |
| Growth | Power/mass gated | Launch reality | Rack-count roadmap only |

---

## 4. Architecture Diagram

```text
                        EARTH
  +------------------+     +---------------------+
  | Customers /      |---->| Earth Control Plane |
  | Scientists       |     | async Job/Object API|
  +------------------+     +----------+----------+
                                      |
                                      v
                           +----------+----------+
                           | Ground stations     |
                           | optical + RF        |
                           | DTN custody         |
                           +----------+----------+
                                      |
                          DTN bundles / contacts
                        (~1.3s one-way + windows)
                                      |
                                      v
                           +----------+----------+
                           | Lunar Relay Orbiter |  (optional but likely)
                           | store-and-forward   |
                           +----------+----------+
                                      |
                                      v
  ============================ MOON SITE ==============================
  |  Power: solar and/or fission  |  Radiators + dust cleaners         |
  |  Berm / buried shielded halls |  Robot tenders                     |
  |                                                                |
  |   +---------------- Lunar DTN + Edge Gateway ----------------+   |
  |   | custody store | priority queues | contact scheduler      |   |
  |   +-------------------------+--------------------------------+   |
  |                             |                                    |
  |   +-------------------------+--------------------------------+   |
  |   |              Lunar Fabric (low RTT)                      |   |
  |   |  +-------------+  +--------------+  +----------------+  |   |
  |   |  | Batch/HPC   |  | Local APIs   |  | Storage tiers  |  |   |
  |   |  | workers     |  | for habitat  |  | L1 flash / L3  |  |   |
  |   |  +-------------+  +--------------+  +--------+-------+  |   |
  |   +---------------------------------------------------------|   |
  |                             ^                                    |
  |                             | local RF/optical                   |
  |                      Rovers / Habitats / Instruments             |
  ====================================================================
```

**Job submit path (Earth → Moon):**

```text
Customer SubmitJob(image, input_refs, power_class, deadline)
  -> Earth admits (policy, $$, export control)
  -> Bundle job + missing inputs (or refs already on Moon)
  -> DTN custody across contacts
  -> Moon scheduler runs when power/thermal headroom
  -> Results bundled to Earth; GetJob polls async
```

**Science ingest path (Moon local):**

```text
Instrument -> local API PutObject
  -> Moon EC durable
  -> Index + optional process
  -> Enqueue Earth replica (priority by policy)
  -> Earth ACK later -> durability upgraded
```

**Storm / blackout path:**

```text
Space weather alert OR contact loss
  -> Pause non-critical batch
  -> Flush checkpoints
  -> Increase scrub; maybe power down unprotected racks
  -> Local clients continue on protected partition
  -> Drain queues when link returns
```

**Robot FRU path:**

```text
Node health alarm -> quarantine
  -> Earth advisory optional
  -> Robot fetches spare from magazine
  -> Hot-swap tray; rebuild EC
  -> Return to pool
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No cross-planet synchronous consensus for primary control.**  
2. **Heat rejection capacity ≥ IT heat** (plus margin) or shed load.  
3. **Power budget is a hard scheduler constraint** (joules, not only CPU).  
4. **Precious data:** EC on Moon + path to Earth durability class.  
5. **Dust barriers:** IT not exposed to unfiltered regolith.  
6. **Radiation:** ECC + scrub + checkpoint; storm mode defined.  
7. **Link down ≠ lunar DC down** for local tenants.  
8. **Time:** explicit delay-tolerant time sync; signed contacts.

#### 5.1.2 Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| SEU / bit flip | ECC, scrub mismatch | Correct; restart job from checkpoint |
| Solar storm | Space weather feeds | Storm mode; derate |
| Link loss | Contact graph miss | Custody queues; local autonomy |
| Radiator dust | Thermal telemetry rise | Clean robots; derate IT |
| Panel dust | Power drop | Electrodynamic / mechanical clean |
| Vacuum leak | Pressure sensors | Compartment isolate |
| Robot stuck | Ops telemetry | Redundant robots; safe modes |
| Ground station weather | Optical fade | Geographic diversity; RF |
| Silent data corruption | End-to-end hashes | Verify chain Earth↔Moon |
| Scheduler runaway power | Power metering | Hard shed breakers |

#### 5.1.3 CAP / consistency across planets

```text
Earth view of Moon objects: eventually consistent
Moon-local strong consistency: OK inside lunar fabric
Cross-planet "single distributed DB": choose AP + conflict rules OR CP with minutes-long ops — usually don't

Idempotent jobs + content-addressed artifacts beat distributed transactions
```

**Deal-breaker:** promising serializable multi-planet SQL with human-interactive latency.

#### 5.1.4 Checkpointing & batch reliability

```text
Jobs must be preemptible (power storms, sheds)
Checkpoint to L1 flash every T progress
Exactly-once effects via artifact CAS + job ledger
Earth retries SubmitJob with idempotency keys — DTN may dup bundles
```

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Pilot | Single radiator loop | Redundant loops; spare pump |
| 10× | Ops bottleneck on Earth | More Moon autonomy |
| 100× | Queue congestion on optical | Multi-terminal; QoS; compression |
| 1,000× | Common-mode dust/storm | Multi-site lunar; diverse power |

### 5.2 Scalability

#### 5.2.1 What “scale” means here

Not only QPS — **landed kW, radiator m², link TB/day, robot-hours, spare mass**.

| Lever | Scales |
|-------|--------|
| Power modules | IT watts |
| Radiator area | Rejectable watts |
| Shielded volume | Server count |
| Optical terminals / ground sites | Earth data movement |
| Custody storage | Blackout tolerance |
| Robots + spares | Availability |

#### 5.2.2 Admission control (joules & bits)

```text
Admit(job):
  require power_class ∈ available_forecast(horizon)
  require thermal_headroom
  require data_local or transfer_budget
  require chattiness_class ∈ {LOCAL, ASYNC}
  reject if needs cross_planet_RTT_loops > N
```

#### 5.2.3 Progressive scale narrative

| Scale | Build |
|-------|-------|
| Baseline | Polar pilot hall, 50–100 kW, RF+early optical, DTN, PB storage, 1 robot |
| 10× | Fission baseload or large solar farm; radiator fields; serious archive; robotic magazine |
| 100× | Multi-hall campus; Earth optical backbone; lunar ISP for outposts; second site seeds |
| 1,000× | Industrial cislunar cloud; in-situ spares; still async to Earth users |

#### 5.2.4 Storage scale

```text
Use content-addressed object store
EC across racks/halls
Cold tier densification > CPU glamour
Earth replica selective: not all intermediate HPC scratch
```

#### 5.2.5 Networking scale

```text
Contact Graph Routing scales with scheduled elements
Add lunar orbiters → more contact opportunities
Multiple Earth ground stations → weather diversity
Prioritize: never let bulk archive starve safety telemetry (and vice policy)
```

### 5.3 Maintainability

#### 5.3.1 Design for robotic maintenance

| Practice | Detail |
|----------|--------|
| FRU size | Robot-grasp trays, not Earth finger screws |
| Connectors | Dust-tolerant, blind-mate, tool-friendly |
| Magazines | Spares prepositioned by failure Pareto |
| Teleop assist | Earth can advise; autonomy for routine swap |
| Diagnostics | BIT, black-box logs, hash inventories |

#### 5.3.2 Software maintainability

| Concern | Approach |
|---------|----------|
| Deploy | Signed images via DTN; staged lunar rollout |
| Config | Desired state sync; large RTT → avoid flap |
| Observability | Compact telemetry; Earth reconstructs; local high-res retained |
| Schemas | Version forever; Moon may lag Earth tools by weeks |
| Chaos | Inject SEU, link loss, power shed in tests on Earth twins |

#### 5.3.3 Lunar dust (regolith)

```text
Threats: abrasion, seal failure, radiator optical property change, connector shorts
Mitigations:
  - Suitports / airlocks; magnetic/brush cleaning
  - Overpressure; labyrinth seals
  - Radiator designs tolerant or cleanable
  - No open Earth-style hot/cold aisle inhaling dust
```

**Deal-breaker:** ignoring dust as “just dirt.”

#### 5.3.4 Radiation & hardware strategy

| Strategy | Use |
|----------|-----|
| Regolith berm / bury | Lower SEE/TID on commodity |
| Spot shielding | Memory, FPGA |
| ECC / chipkill / scrub | Everywhere |
| Triple modular redundancy | Safety-critical only (mass costly) |
| Software: checkpoint, restart | Batch HPC |

#### 5.3.5 Observability metrics

| Metric | Why |
|--------|-----|
| `radiator_delta_T` / dust proxy | Thermal headroom |
| `power_available_kw` | Admission |
| `dtn_custody_queue_bytes` | Link health |
| `contact_success_ratio` | Comms |
| `scrub_correctable_rate` | Radiation environment |
| `job_preempt_rate` | Power storms |
| `earth_durable_lag` | Archive SLO |
| `robot_mttr` | Ops |
| `seu_reboots` | Hardware fitness |

### 5.4 Security & sovereignty

| Topic | Approach |
|-------|----------|
| Link | Authenticated encrypted bundles; anti-replay with delay-tolerant windows |
| Multi-tenant | Strong isolation; export control labels on data |
| Physical | Site is strategic; robot auth; tamper events |
| Supply chain | Landed hardware attestation |
| Earth legal | Contracts define jurisdiction; lunar data classes |

### 5.5 Earth–Moon protocol sketch

```text
Bundle {
  id, priority, custody_required,
  src, dst, creation_ts, expiry,
  payload_hash, chunks[]
}

OnSend: store custody until ACK from next hop
OnBlackout: hold; expire per policy; notify producer async
App API: never block Earth thread on Moon RTT — use futures/webhooks
```

### 5.6 Progressive scale story

> **Baseline:** polar pilot, DTN, async Earth APIs, EC storage, radiator-sized 100 kW, robots for FRU.  
> **10×:** baseload nuclear or big polar power, optical ops mature, archive product.  
> **100×:** lunar campus + Earth high-rate backbone; local economy tenants.  
> **1,000×:** cislunar cloud fabric — still marketed with physics-honest SLOs, not Earth-region cosplay.

---

## 6. Wrap-Up

### 6.1 Decisions locked

| Area | Decision |
|------|----------|
| Why Moon | Near-lunar data, off-Earth durability, DTN relay — not Earth web latency |
| Latency | ≥1.3s one-way; split lunar-local vs Earth-async |
| Network | DTN custody + scheduled optical/RF; orbiter relay |
| Control | Split planes; no cross-planet Raft |
| Power | Polar solar and/or fission; power-aware scheduling |
| Thermal | Fluid loops + radiators; dust cleaning; vacuum honesty |
| Storage | Tiered + EC + Earth durability classes |
| Ops | Robotic FRU; autonomous shed/storm modes |
| Scale | Gate on kW, radiator m², link TB/day, mass |

### 6.2 Deal-breakers called out

- Interactive Earth user region with “normal” cloud SLOs  
- Cross-planet etcd/Raft primary  
- Equatorial solar-only continuous MW without nuclear/absurd batteries  
- “Vacuum cools servers” without radiators  
- Ignoring dust, radiation SEUs, launch mass  
- Always-on fat TCP WAN as the only network story  
- Chatty synchronous DB between Earth and Moon  

### 6.3 30-second close

> A lunar data center is a power-, thermal-, and mass-constrained facility that offers low latency to the Moon and delay-tolerant service to Earth. We admit lunar-local and async batch/archive workloads, move bits with DTN over scheduled optical/RF contacts, protect data with EC plus Earth replicas, and operate with robotic FRUs under storm and dust modes—scaling capacity by landed energy and radiator area, not by pretending light-speed is negotiable.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & motivation

**Q1: Why not only Earth DCs?**  
A: Lunar-sourced data volume/latency to local users; true off-Earth backup; deep-space relay; strategic diversity—not cheaper Gmail.

**Q2: Why not Mars first?**  
A: Harder latency (~minutes to tens of minutes) & logistics; Moon is proving ground.

**Q3: What’s the business model?**  
A: Agency contracts, archive SLAs, lunar surface cloud, DTN transit — say which MVP.

**Q4: Who is the tenant that pays for kW?**  
A: Surface missions first; Earth archive second.

**Q5: Is this sovereign territory?**  
A: Policy-heavy; design data classes and access control regardless.

### 7.2 Latency & protocols

**Q6: Exact light time?**  
A: ~1.28s one-way average; varies with orbital geometry; quote ~1.3s / ≥2.6s RTT.

**Q7: Can QUIC fix it?**  
A: Improves loss recovery vs TCP; cannot beat c.

**Q8: Why DTN?**  
A: Custody across scheduled intermittent links; app independence from continuous path.

**Q9: What about gRPC deadlines?**  
A: Earth→Moon RPCs need minute-class timeouts or async job pattern.

**Q10: NTP?**  
A: Use delay-tolerant / deep-space time transfer ideas; bound clock error explicitly.

**Q11: Contact Graph Routing?**  
A: Route using predicted contacts (orbits, ground windows)—interview gold.

### 7.3 Workloads

**Q12: Can we run Redis for Earth apps?**  
A: Local yes; as Earth cache no — RTT.

**Q13: LLM inference for astronauts?**  
A: Local models sized to power; updates via DTN.

**Q14: Earth backup of Lunar data only?**  
A: Then Moon is sensor buffer — valid smaller design; say so.

**Q15: Blockchain between planets?**  
A: Novelty distraction; finalize locally; checkpoint hashes to Earth.

**Q16: How to classify chattiness?**  
A: Expected RTT round-trips per useful result; threshold admit.

### 7.4 Power & thermal

**Q17: Why radiators?**  
A: In vacuum, radiation (and conduction paths) reject heat; air convection outside unavailable.

**Q18: Polar vs equatorial?**  
A: Poles: solar persistence possible; equator: long nights → nuclear or huge storage.

**Q19: Does nuclear remove thermal problem?**  
A: No — still reject reactor + IT heat.

**Q20: PUE on Moon?**  
A: Redefine: IT / (IT + thermal actuators + comms + losses); not Earth CRAC copy.

**Q21: Battery sizing trap?**  
A: Show MWh for night → argue nuclear/polar.

**Q22: Dust on radiators?**  
A: Emissivity/absorptivity change → temperature rise → mandatory cleaning/derate.

### 7.5 Storage & data

**Q23: Hot/cold tiers?**  
A: Minimize rad-sensitive DRAM; flash hot; dense cold; Earth selective replica.

**Q24: When ACK durability?**  
A: Multi-class: Moon-EC vs Earth-custody — product chooses.

**Q25: Scrub frequency?**  
A: Function of SER × value; storms increase rate.

**Q26: Dedup/compression?**  
A: Saves link and mass-equivalent storage — high ROI.

**Q27: Erasure coding across Earth and Moon?**  
A: Risky for availability (link); prefer Moon-local EC + full async Earth copy.

### 7.6 Reliability & radiation

**Q28: SEU vs SEL vs TID?**  
A: Soft errors vs latchup vs total dose aging — different mitigations.

**Q29: Commodity vs rad-hard?**  
A: Hybrid: shield + ECC + software tolerance for scale; rad-hard for controllers.

**Q30: Storm mode details?**  
A: Shed batch, checkpoint, close shutters if any, boost scrub, protect memory.

**Q31: Correlated failures?**  
A: Single hall, single radiator loop, single terminal — diversity roadmap.

### 7.7 Ops & robotics

**Q32: What is a lunar FRU?**  
A: Robot-swappable compute/storage/power tray with blind-mate connectors.

**Q33: MTTR expectations?**  
A: Hours–days robotic; weeks if waiting for Earth launch spares — design redundancy.

**Q34: Telepresence robots?**  
A: High-latency teleop painful; supervised autonomy preferred.

**Q35: Spare inventory optimization?**  
A: Pareto of failures; cannibalization policy; Earth digital twin predicts.

**Q36: Software push gone bad?**  
A: A/B lunar control; offline rollback images; never brick DTN agent.

### 7.8 Networking details

**Q37: RF vs optical?**  
A: Optical: high rate, pointing/weather sensitive; RF: robust lower rate; use both.

**Q38: Why orbiter relay?**  
A: Geometry, continuous-ish contacts, smaller surface terminals.

**Q39: Bundle expiry?**  
A: Prevent custody store deadlock; producers resubmit.

**Q40: QoS classes?**  
A: Safety telemetry > command > science > bulk archive (policy configurable).

**Q41: Encryption at rest/in transit?**  
A: Yes; key management with delay-tolerant key ceremonies.

### 7.9 Estimation drills

**Q42: RTT impact on chatty API 50 sequential calls?**  
A: 50 × 2.6s ≈ 130s minimum — reject design.

**Q43: Night energy at 500 kW?**  
A: 500 kW × 336 h ≈ 168 MWh — argue impossible battery farm early.

**Q44: Window volume?**  
A: 50 Gbps × 2 h = 45 TB/contact — size queues and priorities.

**Q45: Radiator intuition?**  
A: Area scales with rejected power; dust derate; mention σT⁴ dependence qualitatively.

### 7.10 Alternatives & deal-breakers

**Q46: Only Earth processing of lunar data?**  
A: Valid if link sufficient; loses local closed-loop and autonomy during blackout.

**Q47: Data center in lunar orbit instead?**  
A: Different thermal/power/dust trade; still Earth latency similar; mention as alt.

**Q48: Default K8s multi-cluster federation Earth+Moon?**  
A: Heartbeats/assumptions break — custom eventual intent sync.

**Q49: “Free cooling in shadow”**  
A: Helpful sink but still engineering radiators/loops; not magic.

### 7.11 Interview craft

**Q50: How to open?**  
A: Latency physics → workload admit/reject → power/thermal/dust → DTN → storage durability → ops robotics → scale by kW/mass.

**Q51: What numbers matter?**  
A: 1.3s / 2.6s, kW, radiator area, TB/contact, night duration, SER/scrub, queue bytes.

**Q52: What impresses L5+?**  
A: Physics as deal-breakers, split control planes, joule-aware scheduling, durability classes, dust/radiation modes, progressive landed capacity—not Kubernetes wallpaper.

**Q53: Common mistake?**  
A: Drawing Earth VPC peering to Moon and tuning TCP keepalive.

---

### Appendix A — Latency card

```text
c = 3e8 m/s
d ≈ 3.84e8 m
t_one_way ≈ 1.28 s
t_rtt_min ≈ 2.56 s
+ encoding, queues, contacts → often >> 2.6 s
```

### Appendix B — Workload admission rubric

| Question | If yes |
|----------|--------|
| Needs <100ms to Earth user? | Reject Moon origin |
| Runs during blackout for lunar safety? | Must be Moon-local |
| Chatty cross-planet? | Redesign async |
| Worth launch mass joules? | Cost model |

### Appendix C — DTN priority queues

```text
P0 safety/command
P1 telemetry health
P2 science delivery SLO
P3 bulk archive / images
P4 best-effort
```

### Appendix D — Durability classes

| Class | Meaning |
|-------|---------|
| `moon_ec` | Survives lunar disk loss within EC |
| `earth_pending` | Bundles in custody |
| `earth_durable` | Earth verified replica |
| `multi_earth` | ≥2 Earth regions |

### Appendix E — Power modes

```text
NORMAL: full admission
CONSERVE: batch paused; local critical OK
STORM: max protect; minimal IT
NIGHT_EQUATOR: nuclear baseload or deep sleep
RADIATOR_DIRTY: derate IT to thermal limit
```

### Appendix F — Scheduler sketch

```text
while true:
  forecast = power_thermal_forecast()
  pick job from ready with max priority fitting forecast
  run with checkpoint contract
  on shed_signal: checkpoint + preempt
```

### Appendix G — Earth async API

| API | Semantics |
|-----|-----------|
| `SubmitJob` | Returns job_id immediately |
| `GetJob` | State machine: QUEUED_EARTH/IN_TRANSIT/RUNNING/DONE/FAILED |
| `PutObject` | May be Earth-staged then shipped |
| `GetObject` | May wait for next contacts |
| `SubscribeEvents` | Webhook on Earth when bundles land |

### Appendix H — Progressive scale table

| Scale | Power | Link | Storage | Ops |
|-------|-------|------|---------|-----|
| Pilot | 0.1 MW | Gbps windows | PB | 1–2 robots |
| 10× | ~1 MW | 10–100 Gbps | 10–100 PB | Magazine + autonomy |
| 100× | ~10 MW | Tbps-class goal | EB approach | Multi-hall robotics |
| 1,000× | ~100 MW | Cislunar backbone | multi-EB | Industrial |

### Appendix I — NFR card

```text
RTT Earth–Moon ≥ 2.6s (physics)
Partitions expected; DTN custody
No cross-planet Raft primary
Power/thermal hard constraints
Dust + radiation modes mandatory
Local lunar low-latency OK
Earth interactive web: out of scope
```

### Appendix J — Why vacuum ≠ free cooling

```text
Air cooling on Earth removes heat via convection to CRAC.
In vacuum, free molecular convection ~0.
Heat leaves via thermal radiation εσAT⁴ and conduction into structure.
Without radiator area / sink design, electronics cook in a thermos.
```

### Appendix K — Night battery trap

```text
E = P × T_night
P=100kW, T=336h → 33.6 MWh
At 200 Wh/kg (optimistic pack): mass ≈ 168,000 kg batteries — launch absurd
→ nuclear or polar continuous solar
```

### Appendix L — Optical vs RF cheat sheet

| | Optical | RF |
|--|---------|----|
| Rate | High | Lower |
| Pointing | Strict | Easier |
| Atmosphere | Earth weather | Robust |
| Jamming/visibility | Narrow beam | Broader |
| Role | Bulk | Control/backup |

### Appendix M — Common pushbacks

| Pushback | Response |
|----------|----------|
| “We’ll anycast Moon” | Latency |
| “TCP tuning enough” | Light time |
| “Space is cold” | Vacuum thermos |
| “Solar everywhere” | 14-day night |
| “Just use K8s” | Heartbeats/quorum |

### Appendix N — Related concepts

| Concept | Relation |
|---------|----------|
| Bundle Protocol / DTN | Earth–Moon WAN |
| Contact Graph Routing | Scheduled routing |
| Spacecraft thermal control | Radiators/loops |
| Fission surface power | Baseload |
| Erasure coding | Durability |
| Device twin | Not a robot — a whole DC |
| ECC / scrub | Radiation |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| One-way light time | ~1.3s Earth–Moon |
| Custody transfer | DTN hop reliability |
| SEU | Single-event upset |
| FRU | Field-replaceable unit |
| Regolith | Lunar dust/soil |
| Berm shielding | Regolith radiation barrier |
| EC | Erasure coding |
| CGR | Contact Graph Routing |

### Appendix P — Worked example (chatty vs batch)

```text
Chatty: 200 SQL RTTs × 2.6s ≈ 520s ≈ 8.7 min — unusable
Batch: ship 10 GB input next window; run 2h on Moon; return 100 MB summary
  user waits for contact schedule — acceptable for science
```

### Appendix Q — Worked example (link window)

```text
3 ground stations × staggered weather
Effective 6 h/day at 20 Gbps ≈ 54 TB/day
Archive ingress target 40 TB/day → OK with margin
Spike day 80 TB → backlog 1–2 days; admission throttle
```

### Appendix R — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Strong consistent lunar object store? | Yes locally |
| Linearizable Earth+Moon DB? | No MVP |
| Read-your-writes from Earth after Put to Moon? | After custody path; async |
| Local habitat RYWrites? | Yes on lunar fabric |

### Appendix S — 30m interview checklist

1. State 1.3s / 2.6s; split workload classes.  
2. Power/thermal/dust/radiation deal-breakers.  
3. DTN + optical/RF + orbiter.  
4. Storage tiers + durability classes.  
5. Split control planes; joule scheduler.  
6. Robotic FRU ops.  
7. 10×/100×/1,000× by kW/mass/link — not rack fantasy.

### Appendix T — Security sketch

```text
mTLS-analog for bundles (sign+encrypt)
Device identity for robots
Tenant isolation + export labels
Attested boot for lunar control plane
Key rotation via delayed ceremonies
```

### Appendix U — Thermal control loop

```text
IT cold plates -> pumped loop -> heat exchangers -> radiators
Sensors: loop T, radiator T, IT inlet
Controller: pump speed, louver, IT shed
Dust clean triggers on thermal model residual
```

### Appendix V — What changes at each scale (quick card)

| Scale | Must add |
|-------|----------|
| 10× | Baseload power certainty; optical ops; spare magazine |
| 100× | Multi-hall; multi-ground; lunar multi-tenant product |
| 1,000× | Multi-site lunar; cislunar backbone; ISRU spares hooks |

### Appendix W — Control plane sync

```text
Earth desired_state (jobs, quotas, images)
  --DTN--> Moon agent applies when valid
Moon reported_state (capacity, queues, health)
  --DTN--> Earth ops UI
Conflict: Moon safety shed always wins locally
```

### Appendix X — Explicit non-goals

```text
- Earth-facing CDN
- Multiplayer gaming region
- Default cloud region swap for us-central1
- Synchronous cross-planet microservices mesh
```

### Appendix Y — Site selection sketch

| Site | Pros | Cons |
|------|------|------|
| South polar peak | Solar; science cold traps nearby | Terrain; contested |
| Mid-latitude | Easier some landings | Nights brutal for solar |
| Far side | Radio quiet for astronomy | Earth link needs relay always |

### Appendix Z — One-slide physics deal-breakers

```text
1. c — latency floor
2. Vacuum — radiators or death
3. Night — energy storage or nuclear
4. Dust — seals and cleaning
5. Radiation — ECC/scrub/shield
6. Mass — launch is the budget
```

---

*End of Data Center on the Moon system design.*
