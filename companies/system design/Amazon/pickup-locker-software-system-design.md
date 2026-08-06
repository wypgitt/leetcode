# System Design: Pickup-Locker Software (Device & Ops)

> **Focus areas:** Locker controller · Customer pickup codes · Courier drop/stow · Door/sensor telemetry · Offline modes · Security · Station agent · Cloud sync — **distinct from capacity allocation**  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes (device telemetry vs code redeem vs cloud config), explicit physical safety invariants, resolved ownership of door actuation vs capacity reservations

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

Goal: **bound the locker station software**—the device controller, customer kiosk/app pickup, courier stow flows, door/sensor hardware integration, secure codes, and **offline operation** when the network dies. This is **not** the marketplace capacity allocator (see delivery-locker capacity design); here we own **physical access control and station ops**.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What hardware? | Station with N compartments, locks, door sensors, occupancy sensors, camera optional, kiosk, barcode scanner | Device agent + HAL |
| F2 | Actors? | Customer pickup, courier drop, ops technician, remote cloud | Role-based flows + auth |
| F3 | Pickup code? | One-time / short-lived code (QR + numeric); SMS/email delivered | Code service; rate limits |
| F4 | Courier stow? | Scan package → assigned compartment opens → confirm close + occupied | Stow session state machine |
| F5 | Capacity assignment? | **Consumed from capacity service**; device executes open | Adapter; don’t re-implement allocator |
| F6 | Sensors? | Door open/closed; occupancy IR/weight; tamper; temperature later | Event stream + health |
| F7 | Offline? | Must pickup/stow for already-authorized packages when WAN down | Local auth cache + limited ops |
| F8 | Security? | Prevent code brute force; secure unlock; audit; anti-tamper | Crypto, lockout, HSM/secure element |
| F9 | Multi-package? | One code may open multiple doors sequentially | Session with remaining doors |
| F10 | Missed pickup / expire? | Cloud marks expired; local refuses new opens; ops reclaim | Sync tombstones |
| F11 | Stuck door / jam? | Alarms; ops override with dual control | Incident workflow |
| F12 | OTA updates? | Signed firmware/agent updates | Update pipeline |
| F13 | Video? | Optional on unlock events | Privacy + retention policy |
| F14 | Idempotency? | Double-tap code / duplicate scan | Session tokens |
| F15 | Accessibility? | Large UI, audio prompts, ADA height | UX constraints on kiosk |

**MVP functional scope (lock with interviewer):**

1. **Station Agent** on local PC/industrial controller talking to lock boards.  
2. **Cloud Locker Control Plane** for codes, authorizations, config, telemetry.  
3. Customer **redeem pickup code** → verify → open compartment(s) → confirm empty/closed.  
4. Courier **stow flow** with package scan + compartment open + occupancy confirm.  
5. **Sensor ingestion** and door command API with safety interlocks.  
6. **Offline mode**: honor cached grants; queue events; refuse unknown new stows if policy requires.  
7. Security: hashed codes, attempt lockout, secure device identity, audit log.  
8. Ops tools: remote reboot, compartment disable, emergency open (audited).

**Out of MVP (explicitly defer):**

- Capacity quoting / overbooking algorithms (sibling design)  
- Last-mile courier routing optimization  
- Fridge/hazmat chain deep dive  
- Full CV package dimensioning  
- Customer-facing station selection map UX (thin client OK)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Unlock latency | After code OK | p50 < 500ms local; < 2s with cloud |
| N2 | Availability | Station usable | Offline degrade for cached grants |
| N3 | Safety | Never unlock wrong door for code | Strong binding code→compartments |
| N4 | Security | Resist casual attack | Lockout; secure boot preferred |
| N5 | Telemetry durability | Don’t lose audits | Local spool + cloud |
| N6 | Scale | Many stations | Device mesh; cloud multi-tenant |
| N7 | Clock | Code expiry | Secure time sync; offline skew bounds |
| N8 | Operability | Own pager | Door fault rate, offline %, failed opens |
| N9 | Privacy | Codes & video | Minimize retention; encrypt |
| N10 | Power loss | Safe state | Locks default secure (locked) |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Courier scans tracking → cloud assigns compartment (capacity svc) → door opens → places package → closes → occupied → customer notified.  
2. Customer enters code at kiosk → doors open one-by-one → removes packages → sensors empty → session complete.  
3. App shows QR → station scans → same redeem path.  
4. WAN down: customer code in local cache works; events queue.  
5. Ops disables broken compartment → excluded from new stows.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Wrong code / brute force | Slowdown + lockout; alarm after N |
| Code redeemed twice | Second attempt denied; audit |
| Door commanded open but sensor still closed | Retry/fault; don’t mark picked up |
| Occupancy still true after pickup claim | Prompt customer; don’t complete; ops |
| Courier opens then abandons | Timeout → alarm; compartment suspicious |
| Offline + unknown package | Deny stow or use constrained local pool (policy) |
| Clock skew offline | Reject grants outside skew window |
| Dual open request race | Per-door mutex; one command at a time |
| Power flicker mid-open | On restore: reconcile sensors; secure locked |
| Tamper switch | Alarm; optionally disable remote opens |
| OTA bad update | Signed rollback image |
| Capacity service says X but door faulty | Device rejects; capacity release hook |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Stations | 5K | 50K | 500K | 5M |
| Compartments | 500K | 5M | 50M | 500M |
| Pickup sessions / day | 2M | 20M | 200M | 2B |
| Stow sessions / day | 2M | 20M | 200M | 2B |
| Telemetry events /s | 20K | 200K | 2M | 20M |
| Code redeem QPS peak | 500 | 5K | 50K | 500K |
| Config pushes / day | 10K | 100K | 1M | 10M |
| Offline stations (concurrent) | 1% | 1% | 1–2% | regional weather spikes |
| Ops incidents / day | hundreds | thousands | auto-remediation | |

**What each jump forces:**

- **10×:** IoT message bus; device twin; regional control planes.  
- **100×:** Edge gateways; tiered telemetry; automated fault playbooks.  
- **1,000×:** Cell-based device clouds; store-and-forward hierarchies; hardware SKU fleet mgmt.

### 1.5 Etc. (Constraints & Assumptions)

- **Capacity allocation** is an upstream/sibling system; this system **executes** opens and reports occupancy.  
- Locks are **fail-secure** (stay locked on power loss).  
- Codes are **unguessable** and rate-limited.  
- Station has local persistent storage (disk/flash) + secure element for device identity.

**Scope statement:**

> Design pickup-locker **device and control-plane software** that securely opens compartments for courier stow and customer pickup, integrates door/occupancy sensors, operates under offline conditions with cached authorizations, emits auditable telemetry, and scales across thousands to millions of stations—without reinventing capacity reservation math.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Code redeem** | Customer/courier authz | 500/s | Control plane + station |
| **Door commands** | Local actuations | ~redeem | Station agent |
| **Telemetry** | Sensors/heartbeats | 20K/s | Ingest pipeline |
| **Config / OTA** | Twins, firmware | bursty | Device mgmt |
| **Capacity calls** | Assign/release | ~stow rate | External client |
| **Ops API** | Manual overrides | low | Privileged |

### 2.2 Storage

```text
Authorization grant ~300 B; cache last 7d pickups/station
5K stations × 2K grants × 300 B ≈ 3 GB total cache order
Telemetry 20K evt/s × 200 B ≈ 4 MB/s → ~350 GB/day raw
Downsample: keep raw unlock audits 90d; sensors aggregated
Video optional: dominate cost — event clips only
```

### 2.3 Offline cache sizing

```text
Per station active packages << compartments
Cache grants for packages expected PDD±window + pickup SLA days
Example: 200 active grants × 300 B ≈ 60 KB — tiny
Include revocation bloom/list daily
```

### 2.4 Unlock latency budget

```text
Local verify path (offline/cached): crypto + DB + GPIO < 500ms
Online path: kiosk → cloud verify → device command ≤ 2s p99
Prefer local verify with cloud-signed grants for resilience
```

### 2.5 Bottleneck ranking

(1) Wrong-door unlock (safety/security) (2) offline auth correctness (3) sensor lie / occupancy bugs (4) telemetry flood (5) OTA bricking.

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
Customer Kiosk / App          Courier Handheld           Ops Console
Enter code / scan QR          Scan tracking              Disable door
Open doors sequentially       Confirm stow               Emergency open
Help / wrong station          Report fault               Fleet health
```

### 3.2 Domain model

```text
Station
 ├── station_id, location, status, agent_version
 ├── compartments[]
 └── device_public_key

Compartment
 ├── compartment_id, size_class, hardware_address
 ├── status: OK|FAULTY|DISABLED|OCCUPIED|EMPTY|UNKNOWN
 ├── door_state, occupancy_state
 └── last_sensor_ts

AccessGrant
 ├── grant_id, station_id
 ├── compartment_ids[]
 ├── role: CUSTOMER_PICKUP|COURIER_STOW|OPS
 ├── package_ids[]
 ├── code_hash / offline_token
 ├── not_before, not_after
 ├── max_uses / used_count
 ├── signature (cloud)
 └── status: ACTIVE|REVOKED|CONSUMED|EXPIRED

Session
 ├── session_id, grant_id, actor
 ├── state machine steps
 └── opened_doors[], events[]

DeviceCommand
 ├── command_id, compartment_id, type OPEN|LOCK|REBOOT
 ├── issuer, deadline
 └── ack status

TelemetryEvent
 ├── event_id, station_id, type, payload, ts_device, ts_ingest
```

**Ownership (resolved):**

| Concern | Source of truth |
|---------|-----------------|
| Which compartment reserved for package | **Capacity / reservation service** |
| Whether door may open now | **AccessGrant** (cloud + cached) |
| Physical door/occupancy | **Station sensors** (device) |
| Code issuance UX notify | Notification service |
| Package logistics state | Fulfillment / tracking |
| Firmware binary | Signed OTA repo |

**Deal-breakers:**

- Unlocking from client-supplied compartment id without grant.  
- Plaintext codes in DB logs.  
- Cloud round-trip mandatory for every already-authorized pickup.  
- Trusting courier app to choose arbitrary doors.  
- Marking package picked up before door open + clear occupancy (policy).

### 3.3 Service map

| Component | Responsibility |
|-----------|----------------|
| Station Agent | Local brain: HAL, sessions, cache, spool |
| HAL / Lock Driver | GPIO/serial to lock boards |
| Kiosk UI | Customer flows |
| Courier API edge | Stow sessions |
| Access Grant Service | Issue/revoke/verify codes |
| Device Twin / Config | Desired state per station |
| Telemetry Ingest | Events, metrics, alarms |
| Command Router | Cloud→device commands (gated) |
| Capacity Adapter | Reserve/occupy/release hooks |
| Ops Portal | Fleet, incidents, overrides |
| OTA Manager | Signed updates |
| Notification | Send codes to customers |

### 3.4 Trust & code model

```text
IssuePickupCode:
  cloud creates AccessGrant {compartments, expiry, use=1}
  store code_hash = H(code || station_pepper)
  push signed grant to station twin (and SMS code to user)
  station caches grant

Redeem at station:
  prefer LOCAL verify: H(code) lookup grant; check expiry/uses/revocation
  optional ONLINE verify for high risk
  start Session → DeviceCommand OPEN for each compartment in order
  on success sensors → report PICKED_UP to cloud → capacity release
```

**Offline tokens:** cloud pre-signs grants with station public-key encryption or HMAC with device-rotated key.

### 3.5 Courier stow flow

```text
Scan tracking_id
  → Capacity.AllocateOrConfirm(station, package) // sibling system
  → AccessGrant COURIER_STOW for compartment
  → OPEN door
  → wait close + occupancy TRUE within T
  → Occupy confirm → cloud
  → failure: leave door policy + incident
```

Device does not invent allocation; if capacity API offline, policy: **deny new stow** (safer) or use small pre-provisioned overflow slots.

### 3.6 Sensor & door safety interlocks

```text
OPEN command allowed only if:
  - valid session holds grant for that compartment
  - compartment not DISABLED/FAULTY
  - no other door command in-flight (or limited parallel policy)
  - tamper not latched (unless OPS override)

After OPEN:
  expect door_open within T1
  expect door_closed within T2
  occupancy transition matches role (stow→occupied, pickup→empty)
else → FAULT + do not consume grant wrongly
```

### 3.7 Offline mode

| Operation | Offline behavior |
|-----------|------------------|
| Pickup with cached grant | Allow |
| Pickup unknown code | Deny (or delayed online queue) |
| New courier stow | Deny by default |
| Telemetry | Spool to disk; backpressure |
| Revocation | Periodic revocation list; TTL bound risk |
| Ops emergency open | Local dual-key / physically present tech |

**Risk bound:** max offline grant age; force online for high-value packages.

### 3.8 Security architecture

```text
Device identity: cert in secure element; mTLS to cloud
Grants: signed; hashed codes; constant-time compare
Kiosk: rate limit per keypad; exponential backoff
Courier app: short-lived tokens; station proximity optional (BLE)
Ops override: break-glass dual approval + video ping
Secure boot + signed OTA
Audit: every OPEN attempt immutable local+cloud
```

### 3.9 API sketch

```text
# Cloud
POST /v1/grants/pickup
POST /v1/grants/revoke
POST /v1/stations/{id}/commands
GET  /v1/stations/{id}/health

# Station local
POST /v1/local/redeem {code|qr}
POST /v1/local/stow/start {tracking_id}
POST /v1/local/sessions/{id}/ack-door
GET  /v1/local/compartments

# Device telemetry
POST /v1/telemetry/batch
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+------------+     +------------------+     +-------------------+
| Customer   |---->| Notification     |     | Capacity Service  |
| App/SMS    |     | (send codes)     |     | (sibling)         |
+------+-----+     +--------+---------+     +---------+---------+
       |                    |                         ^
       v                    v                         |
+------+-----+     +--------+---------+               |
| Kiosk / QR |---->| Access Grant Svc |---------------+
+------+-----+     +--------+---------+
       |                    |
       |           +--------+---------+
       |           | Device Twin / IoT|
       |           +--------+---------+
       |                    |
       v                    v
+------+--------------------+------+
|         Station Agent            |
|  Session | Grant Cache | Spool   |
|  +---------+  +--------------+   |
|  |  HAL    |--| Lock/Sensors |   |
|  +---------+  +--------------+   |
+----------------------------------+
```

### 4.2 Pickup sequence (online cached)

```text
Customer → Kiosk redeem(code)
Agent → local grant lookup OK
Agent → OPEN door 7
HAL → sensor door_open
Customer removes package
HAL → occupancy empty, door_closed
Agent → mark grant CONSUMED
Agent → enqueue telemetry PICKUP_COMPLETE
Cloud → capacity release / tracking delivered
```

### 4.3 Offline sequence

```text
WAN down
Customer redeem → local signature verify OK → OPEN
Events spool
WAN up → flush spool → cloud converges
Revocation missed? → bound by grant expiry + short offline max
```

### 4.4 Fault sequence

```text
OPEN sent → door_open timeout
→ retry once → FAULT compartment
→ session pauses; other doors may continue if policy allows
→ ops ticket; capacity may replan package
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No OPEN without valid AccessGrant** covering that compartment.  
2. **Fail-secure locks** on power loss.  
3. **Grant consumption** only after success criteria (policy explicit).  
4. **Idempotent commands** by `command_id`.  
5. **Telemetry at-least-once** with dedupe on `event_id`.  
6. **Tamper latch** blocks remote customer opens.  
7. **Clock skew bounds** enforced for expiry.  
8. **Capacity mismatch** → refuse stow; signal release.  
9. **OTA signatures** required.  
10. **Ops override fully audited**.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | MQTT/IoT hub; monolithic grant service; per-station agent |
| 10× | Regional hubs; sharded grants by station; telemetry Kafka |
| 100× | Edge aggregators; downsample sensors; automated remediation |
| 1,000× | Federation; hardware SKU pipelines; hierarchical store-and-forward |

**Telemetry policy:** unlock audits full fidelity; raw IR samples aggregated to transitions only.

### 5.3 Maintainability

- Hardware abstraction tests with simulator.  
- Station smoke test routine after OTA.  
- Schema versioning for grants.  
- Feature flags per station cohort.  
- Chaos: pull network cable during pickup.

### 5.4 Consistency spectrum

| Data | Model | Why |
|------|-------|-----|
| Door physical state | Device sensors | Reality |
| AccessGrant | Cloud SoT; cached | Authz |
| Capacity reservation | Capacity service | Sibling |
| Pickup complete business state | Cloud after sync | Logistics |
| Local spool | Durable queue | Offline |

**Eventual consistency:** cloud may briefly show “awaiting pickup” after local complete until spool flush—UX should use station confirmation screen as customer truth.

### 5.5 Why distinct from capacity allocation

Capacity design answers: *which station/size/date to reserve under cost/overbook*. This design answers: *how the metal opens safely, authenticates humans, and works in a tunnel with no LTE*. Integrating both via **Occupy/Release events** and **grant issuance** keeps teams decoupled.

### 5.6 Code security deep dive

```text
code: 8–10 chars from alphabet without ambiguous chars OR QR with grant_id+MAC
store only hash; pepper per station
attempts: 5 / 15 min then lockout keypad 15–60 min
alert after repeated lockouts
QR should be single-use bind to grant_id not raw door list
```

### 5.7 Offline revocation trade-off

Cannot instantly revoke if offline. Mitigations: short `not_after`, push revocations aggressively when online, high-value packages require online redeem, bloom filter of revoked grant_ids in cache.

### 5.8 Observability

| Metric / alarm | Why |
|----------------|-----|
| `unlock_success_rate` | CX |
| `wrong_sensor_sequence` | Hardware/logic bugs |
| `offline_station_ratio` | Network |
| `grant_redeem_latency` | UX |
| `brute_force_lockouts` | Security |
| `compartment_fault_count` | Ops |
| `spool_depth` / `spool_age` | Sync debt |
| `ota_fail_rate` | Fleet risk |
| `capacity_adapter_errors` | Integration |

---

## 6. Wrap-Up

### 6.1 What we designed

A **pickup-locker software system** spanning station agents (locks/sensors/sessions), cloud access grants and device twins, courier stow and customer pickup flows, offline cached authorization with event spooling, security controls, and ops/OTA—integrated with but distinct from capacity allocation.

### 6.2 Key decisions worth defending

1. **AccessGrant as unlock authority**; capacity is upstream.  
2. **Local verify of signed/cached grants** for latency + offline.  
3. **Fail-secure locks** + sensor interlocks.  
4. **Default deny new stow when offline**.  
5. **Hashed codes + lockout**.  
6. **Device mTLS identity**.  
7. **Spool telemetry**; business state converges later.  
8. **Per-door command mutex / safety checks**.  
9. **Signed OTA with rollback**.  
10. **Audited break-glass ops**.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Occupancy sensor false empty | Dual sensor; customer confirm UI |
| Offline revoke lag | Short TTL; online for high value |
| HAL driver bugs | Hardware-in-loop CI |
| Telemetry cost | Aggregation policies |
| Stolen kiosk | Tamper + cert rotation |
| Capacity desync | Reconcile jobs station↔capacity |

### 6.4 How to present in 45 minutes

1. Scope vs capacity allocation (4 min)  
2. Actors + offline requirement (5 min)  
3. Grant + agent HLD (8 min)  
4. Pickup/stow sequences + sensors (12 min)  
5. Security + offline trade-offs (8 min)  
6. Scale/ops/traps (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Device & HAL

**Q: Where does agent run?**  
A: Fanless industrial PC / compute module at station; not only cloud.

**Q: How talk to locks?**  
A: Serial/CAN/GPIO boards behind HAL; never expose raw addresses to kiosk UI.

**Q: One board fails?**  
A: Mark affected compartments FAULTY; rest operate.

**Q: Simulator?**  
A: Essential for CI without hardware.

### 7.2 Grants & codes

**Q: Why not open with tracking number alone?**  
A: Guessable/leaked; use unguessable codes + authz grants.

**Q: Numeric PIN entropy?**  
A: Long enough + rate limit; prefer QR for entropy.

**Q: Multi-compartment one code?**  
A: Grant lists doors; sequential open.

**Q: When consume grant?**  
A: After successful pickup criteria—not on first keypress.

### 7.3 Offline

**Q: Can courier stow offline?**  
A: Default no; optional pre-authorized overflow with strict caps.

**Q: How sign grants for offline?**  
A: Cloud signs; device verifies with embedded public key; or per-device MAC keys rotated.

**Q: Time sync lost?**  
A: Use last trusted time + max offline skew; refuse if uncertain.

### 7.4 Sensors & safety

**Q: Customer closes door with package still inside?**  
A: Occupancy still true → don’t complete; prompt retry/help.

**Q: Door open stuck?**  
A: Alarm; disable compartment; ops.

**Q: Parallel opens?**  
A: Limit; accessibility may want one at a time.

### 7.5 Security

**Q: mTLS enough?**  
A: Necessary not sufficient; also grant authz, lockout, physical tamper.

**Q: Insider ops abuse?**  
A: Dual control; audits; anomaly detection on override rate.

**Q: Camera privacy?**  
A: Event-triggered; retention limits; signage.

### 7.6 Integration

**Q: How related to capacity system?**  
A: Capacity reserves; we occupy/release and enforce physical access.

**Q: Double occupy?**  
A: Capacity + local occupancy both checked; recon.

**Q: Package at wrong station?**  
A: Grant won’t be on device; deny; redirect logistics.

### 7.7 Failure injection

1. Pull WAN mid-pickup → finish on cache; spool.  
2. Cloud grant revoke while offline → bound by expiry.  
3. Sensor flap open/close → debounce; don’t loop unlock.  
4. Duplicate redeem → second denied.  
5. Capacity timeout on stow → deny open.  
6. OTA installs bad HAL → rollback partition.  
7. Disk full spool → preserve audits over raw IR; alarm.  
8. Clock jump forward → grants expire; alarm.  
9. Brute force PIN → lockout.  
10. Power loss mid-open → on boot reconcile; lock.

### 7.8 Amazon Leadership-flavored probes

**Q: Customer Obsession — offline pickup?**  
A: Cached grants so rainstorm outages don’t strand customers.

**Q: Ownership — wrong door opens?**  
A: Locker software SEV; joint with hardware; invariant tests.

**Q: Frugality — stream all sensor samples?**  
A: No; transitions + audits.

**Q: Dive Deep — prove code can’t open other doors?**  
A: Grant binding + HAL deny + penetration tests.

### 7.9 Comparison traps

**Q: Is this just IoT door locks?**  
A: Logistics grants, courier flows, capacity integration, offline commerce SLAs.

**Q: Same as capacity allocation interview?**  
A: No—execute vs allocate; mention interface events.

**Q: Same as warehouse WMS?**  
A: Smaller, public-facing, security-critical kiosk environment.

### 7.10 Extra interviewer traps (high value)

- Who authorizes an OPEN?  
- Fail-secure vs fail-open?  
- When is grant consumed?  
- Offline stow policy?  
- How are codes stored?  
- Sensor sequence for pickup complete?  
- How does capacity release happen?  
- Tamper behavior?  
- OTA signing?  
- Clock skew offline?  
- Multi-package session UX?  
- Ops emergency open controls?  
- Telemetry vs audit fidelity?  
- Kiosk brute force?  
- Deal-breaker: client picks compartment_id?

### 7.11 Progressive scale Q&A

**Q: 1×?**  
A: Agent + central grant API + MQTT.

**Q: 10×?**  
A: Regional device clouds; Kafka telemetry.

**Q: 100×?**  
A: Edge aggregators; auto fault playbooks.

**Q: 1,000×?**  
A: Federated cells; SKU fleet factory pipelines.

---

## 8. Appendices

## Appendix A — Example schemas

```sql
CREATE TABLE stations (
  station_id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  agent_version TEXT,
  device_cert_fingerprint TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE compartments (
  station_id TEXT NOT NULL,
  compartment_id TEXT NOT NULL,
  size_class TEXT NOT NULL,
  hw_address TEXT NOT NULL,
  status TEXT NOT NULL,
  door_state TEXT NOT NULL,
  occupancy_state TEXT NOT NULL,
  PRIMARY KEY (station_id, compartment_id)
);

CREATE TABLE access_grants (
  grant_id UUID PRIMARY KEY,
  station_id TEXT NOT NULL,
  role TEXT NOT NULL,
  compartment_ids TEXT[] NOT NULL,
  package_ids TEXT[] NOT NULL,
  code_hash TEXT NOT NULL,
  not_before TIMESTAMPTZ NOT NULL,
  not_after TIMESTAMPTZ NOT NULL,
  max_uses INT NOT NULL,
  used_count INT NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  signature TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX grants_code_hash_active
  ON access_grants (station_id, code_hash)
  WHERE status = 'ACTIVE';

CREATE TABLE sessions (
  session_id UUID PRIMARY KEY,
  grant_id UUID NOT NULL,
  station_id TEXT NOT NULL,
  state TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE device_commands (
  command_id UUID PRIMARY KEY,
  station_id TEXT NOT NULL,
  compartment_id TEXT NOT NULL,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  issued_at TIMESTAMPTZ NOT NULL,
  acked_at TIMESTAMPTZ
);

CREATE TABLE telemetry_events (
  event_id UUID PRIMARY KEY,
  station_id TEXT NOT NULL,
  type TEXT NOT NULL,
  payload JSONB NOT NULL,
  ts_device TIMESTAMPTZ NOT NULL,
  ts_ingest TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Agent+HAL, grants, redeem/stow, sensors, spool, basic ops |
| 10× | IoT twin, regional control, Kafka telemetry, OTA |
| 100× | Edge aggregate, auto remediation, high-value online redeem |
| 1,000× | Federated device cells, SKU pipelines, hierarchical store-forward |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| Station Agent | On-prem controller software |
| HAL | Hardware abstraction for locks/sensors |
| AccessGrant | Signed authorization to open doors |
| Stow | Courier deposit package |
| Redeem | Customer code/QR exchange for opens |
| Fail-secure | Lock stays locked on power loss |
| Twin | Desired/reported device state in cloud |
| Spool | Local durable outbound queue |
| Occupy | Capacity/business state: compartment filled |
| Break-glass | Audited emergency unlock |

## Appendix D — Estimation cheat-sheet

```text
telemetry_QPS >> redeem_QPS
cache_grants_per_station ≈ active_packages
unlock_budget_local < 500ms
video dominates cost if always-on — avoid
```

## Appendix E — Session state machines

```text
CUSTOMER_PICKUP:
  START → VERIFY_OK → OPENING → DOOR_OPEN → REMOVING
       → DOOR_CLOSED_EMPTY → NEXT_DOOR | COMPLETE
       ↘ FAULT / ABORT

COURIER_STOW:
  START → ALLOCATED → OPENING → DOOR_OPEN → PLACING
       → DOOR_CLOSED_OCCUPIED → COMPLETE
       ↘ FAULT / ABORT
```

## Appendix F — Sensor debounce rules

```text
door_open: stable HIGH 200ms
door_closed: stable LOW 300ms
occupancy: require stable 1s before accept
ignore flaps during motor actuation window
```

## Appendix G — Capacity adapter events

```text
Capacity → Device: StowAuthorized(package, compartment, grant_hints)
Device → Capacity: StowOccupied(package, compartment)
Device → Capacity: PickupCleared(package, compartment)
Device → Capacity: CompartmentFault(compartment) / ReleaseRequest
```

## Appendix H — Offline policy matrix

| Package class | Offline pickup | Offline stow |
|---------------|----------------|--------------|
| Standard | Cached grant OK | Deny |
| High value | Online required | Deny |
| Ops reclaim | Local dual auth | n/a |

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Redeem opens only grant doors | No other hw_address toggled |
| Double redeem | Second deny |
| WAN down cached grant | Opens |
| WAN down unknown code | Deny |
| Occupancy still true | No COMPLETE |
| Power loss | Locked on restore |
| Revoked grant online | Deny |
| Unsigned OTA | Reject |
| Duplicate telemetry id | Dedupe |
| Capacity fault compartment | No stow open |

## Appendix J — Incident runbook

1. Spike fault doors → freeze OTA; roll HAL.  
2. Brute force wave → tighten lockout; SOC alert.  
3. Spool explosion → check WAN; prioritize audit flush.  
4. Wrong-door SEV → disable remote opens fleet-wide flag; bisect agent version.  
5. Weather offline region → ensure caches warm; staff ops reclaim.

## Appendix K — Evolution hooks

```text
BLE proximity for courier
Biometric assist (careful privacy)
Smart temp-controlled compartments
Computer vision occupancy backup
Customer app unlock without kiosk (challenge: last-meter auth)
```

---

*End of design doc. Open with §1 scope split vs capacity allocation; whiteboard §3.4 grants + §3.6 sensors + §3.7 offline; close with invariants §5.1 and traps §7.10.*
