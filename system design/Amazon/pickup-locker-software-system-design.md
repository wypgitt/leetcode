# System Design: Pickup Locker Software System (Amazon Logistics)

> **Focus areas:** Device agent · Door/PIN lifecycle · Offline ops · Courier deposit · Customer pickup · Telemetry · Remote unlock · Compartment state machine  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Device/ops software correctness; deal-breaker: capacity-allocation math as the core of this design  
> **Interview theme:** Amazon SDE III / L6 — **Locker device & operations software** (Hub/Locker kiosk + cloud control plane)

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

Goal: design the **software that runs Amazon pickup lockers**—kiosk/controller, cloud APIs, courier deposit, customer pickup, PIN lifecycle, door actuation, offline resilience, telemetry, and ops tooling. This is **not** the network capacity-allocation planner (separate interview).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Device + ops software for locker banks | City-wide locker capacity allocation |
| Core artifact | Compartment state machine + PIN + door commands | Forecasting fill rates / site selection |
| Actors | Customer, courier, field tech, cloud control | Pure OR/optimizer team |
| Success | Safe open, correct parcel, high pickup completion | Maximize network utilization math |
| Amazon lens | Customer trust, ownership, frugality, mechanisms | Academic knapsack on lockers |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a locker site? | Bank of compartments + kiosk + controller + cameras/sensors | Site = device fleet under one agent |
| F2 | Who deposits? | Amazon courier / DSP; scan package → assigned door opens | Deposit API + scan + door command |
| F3 | Who picks up? | Customer enters code / app QR / Amazon account login | AuthN factors + short-lived unlock grants |
| F4 | PIN model? | One-time or time-bound pickup codes; rotate on events | PIN service with TTL, hash-at-rest |
| F5 | Offline? | Site must deposit/pickup for hours if WAN down | Local durable queue + local policy cache |
| F6 | Door control? | Electromechanical latches; sense open/close; jam detect | Actuator driver + sensor fusion + timeout |
| F7 | Remotes? | Ops can remote-unlock with audit; customer app remote | Privileged unlock path + two-person for bulk |
| F8 | Package identity? | Tracking ID ↔ compartment ↔ customer order | Binding table; never open wrong door |
| F9 | Overdue / reclaim? | After SLA, mark overdue; courier reclaim flow | Timers + reclaim state transitions |
| F10 | Multi-size doors? | XS–XL compartments; software tracks occupancy | Size class on compartment inventory |
| F11 | Telemetry? | Heartbeats, door events, temp, door cycles, errors | Edge metrics → cloud with backpressure |
| F12 | Ops tools? | Site health dashboard, force-close, PIN reset, firmware | Control-plane APIs + audit log |

**MVP functional scope (lock with interviewer):**

1. Cloud assigns deposit reservation → courier scan → door opens → confirm close → occupied.  
2. Customer authenticates (PIN/QR/account) → correct door opens → empty confirmed → complete.  
3. Offline: local agent honors cached reservations + issued PINs within policy window.  
4. Compartment state machine with fencing against double-open / wrong-open.  
5. Telemetry + remote unlock with full audit.  
6. Reclaim / overdue / cancel flows.  
7. Firmware/config OTA with canary and rollback.

**Out of MVP (explicitly defer):**

- Network-wide capacity allocation / site selection OR (other doc)  
- Full robotics sortation inside locker  
- Video analytics as sole unlock authority  
- Cross-country active-active mutation of the same compartment  
- Perfect unlock during total power loss without UPS

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Unlock latency | Interactive at kiosk | Door command p99 < 1–2s local; cloud grant < 500ms |
| N2 | Availability | Site usable offline | Local pickup/deposit survive WAN outage hours |
| N3 | Safety | Never open wrong customer door | Fail-closed on ambiguous binding |
| N4 | Durability | No lost deposit confirmations | Local WAL before ACK to courier app |
| N5 | Security | PINs not plaintext; anti-brute | Hash + rate limit + lockout |
| N6 | Scale | Millions of compartments | Cells by geo; site agent is unit of scale |
| N7 | Audit | Who opened what when | Immutable audit stream |
| N8 | Clock | Don't trust kiosk clock alone | Server time + signed grants with skew window |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Courier scans package → reservation match → door opens → place → close sensed → OCCUPIED + notify customer.  
2. Customer enters PIN → validate → door opens → remove → close → EMPTY → delivery complete.  
3. App QR unlock → short-lived grant → same door path.  
4. Overdue → notify → reclaim courier opens with reclaim grant → EMPTY.  
5. Cancel before deposit → reservation released; door never customer-bound.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Door jam / latch fail | Retry N; mark FAULTED; open alternate if policy; page ops |
| Customer enters wrong PIN 5× | Lockout window; escalate to account/app path |
| Two customers same PIN collision | Impossible if codes unique in space×time; detect & rotate |
| WAN down during deposit | Local agent uses cached reservation; sync later |
| Cloud says open door A, local says occupied B | Local truth for occupancy; reject stale grant |
| Power blip mid-open | On boot: reconcile sensors; don't auto-complete |
| Courier deposits wrong package | Scan binding; if mismatch refuse open |
| Remote unlock abuse | MFA + ticket + rate limit + audit + camera flag |
| Split-brain dual cloud writers | Site home cell; fencing token on commands |
| Firmware bad OTA | Canary; auto-rollback; last-known-good image |

### 1.4 Scales (Progressive)

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Sites | 50K | 500K | 5M | 50M |
| Compartments | 2M | 20M | 200M | 2B |
| Unlocks/day | 5M | 50M | 500M | 5B |
| Telemetry pts/s | 50K | 500K | 5M | 50M |
| Architecture jump | Regional APIs | Geo cells + edge | Site mesh + hierarchical telemetry | Multi-tenant locker platform |

**What breaks if you only add servers:** kiosk still needs local autonomy; telemetry floods ingest; PIN entropy & brute-force surface grows; OTA blast radius; single global command bus becomes HOL bottleneck.

### 1.5 Etc. (Constraints & Assumptions)

- Compartment physical truth is on the **site agent**; cloud is control + sync.  
- Capacity *assignment* of which site gets which order may call an allocator service—we integrate, we don't redesign OR here.  
- Amazon themes: customer trust (wrong-open is SEV), ownership (Locker Device team pages), frugality (offline UPS not infinite cloud retries), mechanisms (state machine + audit).  
- **Repeat-back:** “Device/ops software for deposit, pickup, PIN, doors, offline, telemetry—not capacity allocation.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Base estimate | Notes |
|-------|---------------|-------|
| Unlock grants | ~60–100 QPS avg, 10× peak regional | Spiky evenings |
| Deposit confirms | similar order | Courier waves |
| Heartbeats | 50K sites × 1/30s ≈ 1.7K/s | Cheap |
| Door events | 5–20× unlocks | Sensor chatter |
| Telemetry aggregates | downsample at edge | Critical |

### 2.2 Storage

```text
Compartment row ~500B × 2M ≈ 1TB with indexes/replication headroom → plan 5–10TB
Audit events 5M unlocks/day × 1KB × 90d ≈ 450TB raw → tiered/cold
PIN hashes: small; secrets in KMS/HSM path
Site local SSD: reservations + WAL days of ops (~GBs)
```

### 2.3 Bandwidth

```text
Cloud command ~1KB; telemetry must be aggregated
50K sites × 10KB/min telemetry ≈ 8MB/s → fine
At 100×: hierarchical rollup mandatory or ingest melts
```

### 2.4 Memory / edge

Site agent: compartment map in RAM (thousands of doors) + hot reservation cache. Cloud: Redis for grant/session; Dynamo/SQL for bindings.

### 2.5 Critical path latency budget (online pickup)

| Step | Budget |
|------|--------|
| Auth / PIN verify | 50–150ms |
| Binding lookup | 20–50ms |
| Signed grant issue | 20–50ms |
| Site receive + actuate | 200–800ms |
| Sensor confirm | 200–1000ms |
| **Total interactive** | **well under a few seconds** |

### 2.6 Bottlenecks

1. Wrong-open risk (correctness > QPS).  
2. Offline sync conflict resolution.  
3. Telemetry cardinality.  
4. OTA + config fanout.  
5. Hot sites (apartment buildings) command QPS.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| `Site` | Physical locker bank + agent identity |
| `Compartment` | Door with size, sensors, state |
| `Reservation` | Intent to deposit package P into size class |
| `OccupancyBinding` | Package ↔ compartment ↔ customer grant |
| `UnlockGrant` | Signed, short-lived, fenced permission to open door D |
| `SiteAgent` | On-prem controller process |
| `ControlPlane` | Cloud APIs, PIN, sync, OTA, ops |

### 3.2 Compartment state machine

```text
EMPTY → RESERVED → OPEN_FOR_DEPOSIT → OCCUPIED → OPEN_FOR_PICKUP → EMPTY
                      ↘ FAULTED ↙                 ↘ RECLAIM ↗
Any state --fault--> FAULTED (ops clear)
OCCUPIED --overdue--> OVERDUE → RECLAIM → EMPTY
```

Transitions require **CAS + event log**. Door open commands only valid from states that allow actuation.

### 3.3 Deposit path

1. Allocator (external) / order system creates reservation for site+size.  
2. Courier app gets task; on scan, requests deposit open.  
3. Control plane validates package↔reservation; issues grant to site.  
4. Agent opens door; sensors confirm open/close; agent ACKs OCCUPIED.  
5. Notify customer; PIN/QR material issued/activated.

### 3.4 Pickup path

1. Customer presents PIN/QR/account proof.  
2. Verify → issue unlock grant for bound door only.  
3. Agent actuates; on successful empty sense → COMPLETE.  
4. Invalidate PIN; audit.

### 3.5 Offline path

- Agent stores signed reservation snapshots + PIN verifiers (salted hashes / bloom+HSM pattern).  
- Unlocks that can be proven locally proceed; sync to cloud as eventual.  
- Conflicts: local occupancy wins; cloud reconciles with compensating workflows.

### 3.6 Security model

- PIN: random, adequate entropy, hashed (argon2/bcrypt), TTL, single-use optional.  
- Grants: Ed25519/HMAC signed; `site_id`, `door_id`, `expires`, `fencing_token`, `purpose`.  
- Rate limits on kiosk PIN attempts; camera optional for dispute.  
- Remote unlock: IAM + ticket id + step-up auth.

### 3.7 Telemetry & ops

Edge aggregator → regional ingest → site health service. Ops console: force state, PIN reset, reboot agent, OTA.

### 3.8 Trade-offs (name in interview)

| Choice | Why |
|--------|-----|
| Local agent authority on occupancy | Physical world source of truth |
| Signed short-lived grants | Limit blast of stolen credentials |
| Hash PINs at rest | Breach resistance |
| Offline limited policy | Availability without infinite risk |
| Integrate allocator, don't own OR | Scope discipline |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Customer App/Kiosk]     [Courier App]        [Ops Console]
         |                     |                     |
         v                     v                     v
    +-----------+        +-----------+         +-----------+
    | Edge/API  |        | Edge/API  |         | Admin API |
    +-----+-----+        +-----+-----+         +-----+-----+
          |                    |                     |
          +---------+----------+----------+----------+
                    v                     v
           +----------------+    +----------------+
           | Grant/PIN Svc  |    | Binding/State  |
           +--------+-------+    +--------+-------+
                    |                     |
                    +----------+----------+
                               v
                        +-------------+
                        | Command Bus |  (per geo cell)
                        +------+------+
                               |
                    +----------+----------+
                    v                     v
             [Site Agent A]         [Site Agent B]
             - state machine        - actuators
             - local WAL            - sensors
             - offline cache        - OTA client
                    |
                    v
             Door Controllers / Latches
```

### 4.2 Sequence: happy pickup

```text
Customer -> Kiosk: PIN
Kiosk -> PIN Svc: verify
PIN Svc -> Binding: door D
PIN Svc -> Grant: sign(open D)
Grant -> SiteAgent: command
SiteAgent -> Latch: open
SiteAgent -> Binding: OCCUPIED->EMPTY (on empty sense)
SiteAgent -> Audit: event
```

### 4.3 Sequence: offline deposit

```text
Courier -> SiteAgent: scan (WAN down)
SiteAgent: validate cached reservation
SiteAgent: open door, WAL OCCUPIED
... WAN returns ...
SiteAgent -> Cloud: sync events (idempotent)
Cloud: notify customer / reconcile
```

### 4.4 Sequence: conflict

```text
Cloud grant for door 12 (stale EMPTY view)
SiteAgent local: door 12 OCCUPIED
SiteAgent: reject grant (409), request refresh
Cloud: reconcile; issue correct door or fail safe
```

### 4.5 Multi-region

- Site has **home cell**; commands only from home.  
- Customer auth global; grant issuance sticky to home.  
- DR: promote secondary with fencing generation bump.

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. At most one active customer binding per occupied compartment.  
2. Unlock grant must match `fencing_token` / generation.  
3. No transition EMPTY→OCCUPIED without deposit confirm event.  
4. PIN invalid after successful pickup (or TTL).  
5. Audit event for every actuation attempt.

**Failure handling**

| Failure | Mitigation |
|---------|------------|
| Agent crash | WAL replay; sensor reconcile on boot |
| Latch stuck | FAULTED; alternate compartment playbook |
| Clock skew | Grant skew window; prefer server `not_before/not_after` |
| Duplicate sync | Event ids idempotent |
| Poison firmware | Signed images; canary; rollback |

### 5.2 Scalability

- Shard control plane by `site_id` hash within geo cell.  
- Site agent is embarrassingly parallel unit.  
- Telemetry: aggregate counters locally; samples for traces.  
- Hot apartment site: local command coalescing; don't global-lock.

**Progressive scale**

| Jump | Change |
|------|--------|
| 10× | Regional cells, Redis grant cache, batched telemetry |
| 100× | Hierarchical ops (station→region), edge auth kits |
| 1,000× | Locker-as-platform multi-tenant cells; on-device policy packs |

### 5.3 Maintainability

- Explicit state machine table in code + property tests.  
- Device contract versioned (`agent_protocol_vN`).  
- Config as versioned bundles; no SSH snowflakes.  
- Clear ownership: Device Agent vs PIN/Grant vs Binding vs OTA vs Ops UI.

### 5.4 Security deep dive

- Brute force: exponential backoff + hardware keypad lockout.  
- QR tokens: one-time, bind to order, short TTL.  
- Insider remote unlock: break-glass with dual control for bulk opens.  
- Physical: compartment sensors defeat “claim empty while package inside” via weight/door logic where hardware allows.

### 5.5 Offline consistency model

```text
Cloud desired state  vs  Site observed state
Reconcile:
  - Occupancy: site wins
  - Reservations: cloud wins if not locally started
  - PINs: verifiers sync; revoke lists pull frequently when online
```

### 5.6 Integration with capacity allocator (boundary)

```text
Orders Service -> Allocator (other system) -> Reservation created
Pickup Locker Software consumes reservations; reports occupancy & faults
Allocator reads occupancy signals; does NOT open doors
```

Deal-breaker in *this* interview: spending the hour on bin-packing sites instead of door/PIN/offline.

### 5.7 Deal-breaker gallery

| Deal-breaker | Why |
|--------------|-----|
| Cloud as sole authority with no offline | Sites dark → stranded packages |
| Plaintext PIN table | Breach = mass theft |
| Open door by package scan without binding check | Wrong-open |
| Global mutex for all unlocks | Latency + blast radius |
| Capacity OR as the design center | Wrong interview |

---

## 6. Wrap-Up

### 6.1 Decisions

1. Site agent owns physical occupancy truth.  
2. Signed short-lived unlock grants with fencing.  
3. Hashed, rate-limited PINs / QR.  
4. Offline WAL + policy-limited autonomy.  
5. Explicit compartment state machine + audit.  
6. Hard boundary vs capacity-allocation system.

### 6.2 Risks

- Sensor lying / hardware faults → wrong COMPLETE.  
- Sync conflicts after long partition.  
- Insider remote unlock.  
- Telemetry cost at 100×.  
- OTA regressions bricking sites.

### 6.3 45-minute plan

| Time | Focus |
|------|-------|
| 0–5 | Scope: device/ops NOT capacity allocation |
| 5–12 | Actors, state machine, NFRs |
| 12–22 | HLD + diagram + deposit/pickup |
| 22–35 | Offline, grants, failures, scale |
| 35–45 | Security, ops, deal-breakers, Q&A |

### 6.4 Closer

> **Pickup Locker Software**: site agent + cloud control plane, compartment state machine, signed unlock grants, offline WAL, PIN/QR security, telemetry/OTA—customer-trust fail-closed on ambiguous opens; capacity allocation is a sibling system.

---

## 7. Deeper / Related Interview Questions

### 7.1 State machine

**Q1. Why CAS on compartment state?**  
**A:** Prevent double deposit / double pickup races between courier and sync.

**Q2. Can OCCUPIED go to EMPTY without open?**  
**A:** Only via controlled reclaim/ops with audit—not silently.

### 7.2 PIN / auth

**Q3. Offline PIN verification?**  
**A:** Sync verifiers (hashes) + revocation bloom; limited offline issuance window.

**Q4. Account login at kiosk vs PIN?**  
**A:** Stronger UX; needs cached session tokens / online; fallback PIN.

### 7.3 Offline

**Q5. How long offline?**  
**A:** Policy hours–days; after that fail-closed new deposits; allow pickup if verifier present.

**Q6. Conflict: cloud cancelled, local deposited?**  
**A:** Physical OCCUPIED wins; create exception workflow for customer/ops.

### 7.4 Security

**Q7. Remote unlock SEV?**  
**A:** Treat as privileged; MFA; ticket; rate limit; camera; anomaly detection.

**Q8. PIN entropy?**  
**A:** Enough against online guessing given lockout; avoid 4-digit if attack surface high—use 6–8 or alphanumeric.

### 7.5 Scale / ops

**Q9. Telemetry at 100×?**  
**A:** Edge aggregate; exemplar traces; tiered storage.

**Q10. OTA strategy?**  
**A:** Signed images; canary by site cohort; automatic rollback on health SLO.

### 7.6 Boundaries

**Q11. Difference vs capacity allocation doc?**  
**A:** That doc: where/how many compartments to reserve in network. This doc: software to operate doors safely.

**Q12. Who pages for wrong-open?**  
**A:** Locker Device/Binding oncall—customer-trust SEV.

### 7.7 Hardware

**Q13. Sensor says closed but latch open?**  
**A:** FAULTED; don't mark EMPTY; dispatch tech.

**Q14. Multi-package one door?**  
**A:** Usually 1:1 binding MVP; multi requires explicit model—don't invent silently.

### 7.8 Interview traps

| Trap | Pushback |
|------|----------|
| Design city OR allocator | Wrong scope |
| SQL as door controller | Need edge agent |
| Exactly-once unlock without fencing | Duplicates happen |
| Infinite offline trust | Revocation lag risk |
| Video-only auth | Privacy + reliability |

---

## 8. Appendices

### 8.1 Schema sketches

```text
Compartment(site_id, door_id, size, state, gen, package_id?, updated_at)
Reservation(res_id, site_id, size, package_id, status, expires)
Binding(package_id, site_id, door_id, customer_id, state)
UnlockGrant(grant_id, site_id, door_id, purpose, exp, fence, sig)
PinVerifier(order_id, pin_hash, exp, attempts)
Audit(event_id, site_id, door_id, actor, type, ts, prev_state, new_state)
```

### 8.2 Grant payload

```text
{site, door, purpose: PICKUP|DEPOSIT|RECLAIM|OPS,
 not_before, not_after, fence, package_id?, sig}
```

### 8.3 Operator checklist

- [ ] Site heartbeat fresh  
- [ ] Faulted doors known  
- [ ] OTA cohort healthy  
- [ ] PIN lockout alerts  
- [ ] Unlock error budget  
- [ ] Audit pipeline lag  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Site agent | On-prem locker controller software |
| Grant | Signed unlock permission |
| Fence | Generation token preventing stale commands |
| Reclaim | Courier removes overdue package |
| Cell | Geo failure domain for control plane |
| WAL | Local write-ahead log |

### 8.5 Progressive scale checklist

- [ ] 10×: regional cells + telemetry batching  
- [ ] 100×: hierarchical ops + edge verifiers  
- [ ] 1,000×: platform multi-tenant locker cells  

### 8.6 Reliability test plan

1. Kill agent mid-open → reconcile, no false COMPLETE.  
2. WAN down 6h → deposit+pickup still work within policy.  
3. Stale grant → rejected by fence.  
4. Brute PIN → lockout.  
5. Bad OTA canary → auto rollback.

### 8.7 Related systems map

```text
Order/Delivery → Allocator (capacity) → Reservation
                      ↓
              Locker Control Plane ↔ Site Agent ↔ Doors
                      ↓
              Notify / Trace / Ops / OTA
```

### 8.8 Pseudocode: pickup

```text
function pickup(site, credential):
  binding = verifyAndGetBinding(credential)  // fail-closed
  grant = signGrant(site, binding.door, PICKUP, fence=binding.gen)
  ok = siteAgent.actuate(grant)
  if ok and siteAgent.senseEmpty(binding.door):
     cas(binding, OCCUPIED→COMPLETE, gen++)
     invalidateCredential(credential)
     audit(...)
  else:
     markSuspect(binding); page if repeated
```

### 8.9 Interview “say this” (60s)

> We run a site agent as source of truth for doors, with a cloud control plane for PIN/QR grants, bindings, and ops. Deposit and pickup are state-machine transitions driven by signed short-lived grants and sensor confirms. Offline, the agent uses a WAL and cached verifiers. Wrong-open is fail-closed. Telemetry and OTA are canaried. Capacity allocation is a separate system we integrate via reservations.

### 8.10 Extra traps

| Trap | Pushback |
|------|----------|
| Global Kafka as door loop | Too much latency/variance |
| Customer trust = availability only | Wrong-open worse than downtime |
| Store PINs in app logs | PII/secret leak |

---

## Deep Technical Notes — Pickup Locker Software

### Local WAL design

Append-only events: `DoorCommandIssued`, `DoorOpened`, `DoorClosed`, `OccupancySet`, `FaultSet`. Cloud sync sends contiguous sequences with site epoch. Idempotency key = `(site_id, seq)`.

### Sensor fusion

Debounce open/close; require stable closed N ms before OCCUPIED/EMPTY commit. Weight sensor optional enhancement—never sole signal without hardware confidence.

### PIN space management

Allocate from site-scoped or global space with collision checks; rotate on notify resend; separate deposit courier credentials from customer PINs.

### Kiosk UI states

Idle → Auth → Unlocking → Remove package → Confirm → Thank you. Accessibility: large fonts, language packs, audio prompts. No dead-end without help code.

### Camera / privacy

If used for disputes, retention TTL, encryption, access audit; not required for MVP unlock.

### Power & UPS

Agent distinguishes clean shutdown vs dirty; on dirty boot run reconcile playbook before accepting cloud grants.

### Multi-bank sites

One logical site may have multiple controllers; aggregate under site master elected locally with lease.

### Timeouts

Deposit open timeout → auto-relock + alarm if package not sensed; pickup timeout similar.

## Interview Cards — Pickup Locker Software

### Card 1: Site vs cloud truth?

Occupancy: site. Reservations/PIN policy: cloud with cached slice offline.

**Follow-ups:** Partition 24h? Who pages? Metric?

**Amazon ownership:** Device agent team owns wrong-open SEVs.

### Card 2: Signed grants?

Prevent forged kiosk commands; bind door+purpose+expiry+fence.

**Follow-ups:** Key rotation? Stolen kiosk?

### Card 3: Offline pickup?

Cached verifiers + local state; sync later; revoke lag bounded by policy.

### Card 4: Wrong-open SEV?

Fail-closed; incident; binding audit; customer notification; root cause on CAS/race.

### Card 5: Capacity boundary?

Reservations in; occupancy out; no OR solver here.

### Card 6: Telemetry flood?

Edge aggregate; exemplars; dynamic sampling when healthy.

### Card 7: OTA brick?

Canary + health SLO + last-good rollback; dual-bank image.

### Card 8: Remote unlock abuse?

Step-up auth, tickets, rate limits, anomaly detection, dual control bulk.

### Card 9: Door jam?

FAULTED; alternate compartment if deposit not yet done; tech dispatch.

### Card 10: Deal-breaker?

Designing allocator OR as this system; or cloud-only with no offline.

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + not capacity allocation |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Offline, security, state machine |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact (stranded package / wrong-open); lock MVP; name pager owners.

---

## 10. Operability

### Golden signals

Unlock success rate, grant latency, faulted door count, offline site count, audit lag, OTA failure rate, PIN lockouts.

### Rollback ladder

Flag off risky remote features → revert agent protocol → pin cohort to last-good firmware → cell isolate → postmortem with trust section.

### Kill switches

Disable remote unlock; freeze OTA; force online-only mode; shed telemetry verbosity; isolate site.

### Security/privacy baseline

Hash PINs; encrypt grants in transit; least-privilege ops IAM; PII minimization in logs; camera TTL.

### Cost worksheet

```text
Dominant: cellular backhaul + cloud ingest + field tech dispatches
Lever: edge aggregation, reduce false FAULTED, OTA efficiency
10× without arch jump: linear SIM + ingest cost → bad
```

### Progressive scale

10× cells/batching; 100× hierarchical telemetry; 1,000× platform cells.

### Cross-team deps

Orders, Allocator, Notify, Identity, Maps/Sites, Firmware, Loss Prevention — each with failure mitigation.

---

## More Interview Q&A — Pickup Locker Software

**Q1. Why not open door from cloud TCP directly to latch?**  
**A:** Need local safety, offline, sensor fusion, and fencing—agent is mandatory.

**Q2. How do you prevent double pickup?**  
**A:** CAS on binding generation; single-use PIN; grant fence.

**Q3. Package too big for assigned door?**  
**A:** Courier rejects; re-reserve larger; allocator interaction.

**Q4. Customer code sharing?**  
**A:** Risk accepted like package codes; optional app auth step-up for high value.

**Q5. How is reclaim authorized?**  
**A:** Courier role grant bound to overdue package list.

**Q6. Multi-marketplace lockers?**  
**A:** Tenant isolation on bindings; visual branding secondary.

**Q7. Clock rewind on kiosk?**  
**A:** Grants carry absolute expiry from cloud; agent uses trusted time source when possible.

**Q8. Idempotent sync?**  
**A:** Monotonic site seq + event UUIDs.

**Q9. Hot site apartment?**  
**A:** Local actuation doesn't need global lock; cloud rate-limits grant issuance per site.

**Q10. What metric for customer trust?**  
**A:** Wrong-open count (target ~0), pickup success, time-to-unlock, complaint rate.

**Q11. Can AI vision replace PIN?**  
**A:** Optional assist; not sole MVP authority.

**Q12. DR test?**  
**A:** Cell failover with generation bump; in-flight grants may expire—acceptable.

**Q13. Why hash PIN if offline needs verify?**  
**A:** Store hash verifiers, not plaintext; online and offline both verify hashes.

**Q14. Field tech opens all doors?**  
**A:** Maintenance mode with physical key + software maintenance role; audited.

**Q15. Deal-breaker again?**  
**A:** Skipping state machine; or merging this with capacity OR interview.

**Q16. How to demo in interview whiteboard?**  
**A:** Draw agent+cloud, 5-state machine, grant box, offline WAL—then scale.

---

## Deep Technical Addenda — Pickup Locker Software

### Protocol versioning

Agent advertises `protocol=3`; cloud speaks min/max. New door command fields optional with defaults. Breaking changes require dual-run.

### Reservation cache pack

Signed bundle: `{res_id, package_id, size, exp, sig}`. Agent rejects expired. Refresh when online every N minutes.

### Empty sensing policy

If hardware lacks weight, use door cycle + courier/customer confirm button + timeout suspicion queue for ops.

### Abuse: PIN spraying across sites

Global risk engine correlates attempts; block account; uncommon for random 8-char codes.

### Data retention

Audit hot 90d; warm 1y; cold legal hold. PIN hashes deleted after complete+TTL.

## Tradeoff Matrices — Pickup Locker Software

### Consistency vs availability

| Choice | Pros | Cons | Use |
|--------|------|------|-----|
| Cloud authoritative always | Simple | Offline fails | Bad for lockers |
| Site occupancy authority | Works offline | Sync complexity | **Default** |
| Quorum cloud+site | Safer abstractly | Not practical for latch | Avoid |

### Auth factors

| Choice | UX | Risk | Use |
|--------|----|------|-----|
| PIN only | Fast | Shareable | MVP common |
| QR one-time | Fast | Device needed | App path |
| Account login | Strong | Online dependency | Step-up |

### Telemetry richness

| Choice | Cost | Debug | Use |
|--------|------|-------|-----|
| Raw every sensor tick | Huge | Great | Lab only |
| Aggregates + on-fault traces | Low | Enough | **Prod** |

## Operability Addenda — Pickup Locker Software

### Deploy pipeline

```text
agent build → sign → canary sites → bake → cohort rollout → full
                     ↓ health fail
                  auto rollback
```

### Guardrail examples

- Wrong-open > 0  
- Unlock success drop  
- Faulted door % spike  
- OTA fail rate  
- Audit lag  

### Kill switches

1. Disable remote unlock  
2. Freeze OTA  
3. Online-only grants  
4. Shed verbose telemetry  
5. Isolate site / cell  

## Worked Capacity Narrative — Pickup Locker Software

Speak: (1) sites × doors, (2) unlocks/day, (3) grant QPS peak, (4) telemetry with edge aggregate, (5) 10× needs cells not bigger monolith, (6) 100× hierarchical ops, (7) wrong-open invariant unchanged at any scale.

## Customer-Trust Paragraph — Pickup Locker Software

Wrong-open, lost package after false COMPLETE, or leaked PINs are trust incidents—not “just bugs.” Prefer temporary inability to unlock (with support path) over opening the wrong door. Auditable remote unlock. Clear ownership and SEV definitions.

## Progressive Scale Recap — Pickup Locker Software

- **10×:** geo cells, grant cache, telemetry batching  
- **100×:** hierarchical rollup, edge verifier packs, cohort OTA  
- **1,000×:** multi-tenant locker platform, policy packs on device  

For each jump: **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Pickup Locker Software

### S1. Fencing tokens

Every occupancy generation increments on bind/complete; grants carry fence; stale rejected.
**Invariant:** stale grant never actuates.  
**Metric:** `grant_reject_stale` .  
**10× note:** still local check.  
**Ownership:** Device agent.

### S2. WAL before courier ACK

Deposit confirm durable locally before UX success.
**Invariant:** no ACK without WAL.  
**Metric:** `ack_without_wal` = 0.

### S3. PIN attempt budget

Per-kiosk and per-credential budgets.
**Invariant:** lockout triggers.  
**Metric:** `pin_lockout_count`.

### S4. Offline revoke lag

Bound max offline hours vs fraud risk.
**Invariant:** policy documented.  
**Metric:** `sites_offline_hours`.

### S5. OTA dual image

A/B bank; confirm boot health.
**Invariant:** rollback path exists.  
**Metric:** `ota_rollback_rate`.

### S6. Audit completeness

Actuate ⇒ audit event.
**Invariant:** mismatch alert.  
**Metric:** `actuate_minus_audit`.

### S7. Allocator boundary

No OR in this service.
**Invariant:** API only reservations.  
**Metric:** n/a—design review gate.

### S8. Unit economics

Cost per successful pickup; field dispatch cost.
**Metric:** `$ / completed_pickup`.

## Scenario Runbooks — Pickup Locker Software

| Scenario | Detect | Mitigate | Follow-up |
|----------|--------|----------|-----------|
| WAN outage city | Heartbeats miss | Offline mode | Capacity of SIM? |
| Wrong-open report | SEV channel | Freeze site grants | Forensic audit |
| OTA brick cohort | Bootloop metric | Rollback image | Fix canary gates |
| PIN spray | Attempt spike | Lockout + block | Entropy review |
| Latch epidemic SKU | Fault SKU tag | Maintenance mode | Hardware RMA |
| Sync storm after outage | Ingest lag | Backpressure / replay throttle | |

## Rapid-Fire Q&A — Pickup Locker Software

**Q:** Site truth? **A:** Occupancy yes.  
**Q:** Cloud truth? **A:** Identity, policy, reservations.  
**Q:** Grant TTL? **A:** Seconds–minutes.  
**Q:** PIN store? **A:** Hash.  
**Q:** Offline? **A:** WAL + verifiers.  
**Q:** Allocator? **A:** Sibling system.  
**Q:** Wrong-open? **A:** SEV fail-closed.  
**Q:** Telemetry? **A:** Aggregate.  
**Q:** OTA? **A:** Canary+rollback.  
**Q:** Fence? **A:** Generation on binding.  
**Q:** Reclaim? **A:** Role grant.  
**Q:** Jam? **A:** FAULTED.  
**Q:** Dual cloud writers? **A:** Home cell.  
**Q:** Camera required? **A:** No for MVP.  
**Q:** Multi-package door? **A:** Out of MVP.  
**Q:** Cost lever? **A:** Edge aggregate + fewer false faults.  
**Q:** 10× break? **A:** Monolith command bus.  
**Q:** 100× break? **A:** Telemetry cardinality.  
**Q:** 1000×? **A:** Platformize cells.  
**Q:** Deal-breaker? **A:** Capacity-OR-as-core or cloud-only.  
**Q:** Ownership? **A:** Device agent oncall.  
**Q:** Idempotent sync? **A:** seq+UUID.  
**Q:** Brute PIN? **A:** Lockout.  
**Q:** Dirty boot? **A:** Reconcile sensors.  
**Q:** Customer notify? **A:** After OCCUPIED durable.  
**Q:** QR vs PIN? **A:** Both; QR one-time.  
**Q:** Bulk open? **A:** Dual control.  
**Q:** Clock skew? **A:** Skew window.  
**Q:** Size class? **A:** On compartment + reservation.  
**Q:** Cancel reserved? **A:** Cloud wins if not started.  
**Q:** Audit lag SLO? **A:** Minutes.  
**Q:** Help broken kiosk? **A:** App unlock + support.  
**Q:** DSP courier auth? **A:** Courier identity + task bind.  
**Q:** Encryption? **A:** TLS + at-rest.  
**Q:** PII in logs? **A:** Minimize/tokenize.  
**Q:** State machine tests? **A:** Property + chaos.  
**Q:** Hot path store? **A:** Site RAM+SSD; cloud Dynamo/SQL.  
**Q:** Why not blockchain? **A:** Irrelevant frugality fail.  
**Q:** Success metric? **A:** Pickup completion + zero wrong-open.

## Narrative Walkthrough — Pickup Locker Software

### Walkthrough beat 1

Interviewer: “Design Amazon locker software.” You: clarify device/ops vs capacity allocation; lock MVP deposit/pickup/offline.

### Walkthrough beat 2

Sketch actors; define compartment states; write invariants on board.

### Walkthrough beat 3

Draw site agent + control plane; grants; bindings; audit.

### Walkthrough beat 4

Walk courier deposit sequence with sensors and WAL.

### Walkthrough beat 5

Walk customer PIN pickup; mention fail-closed.

### Walkthrough beat 6

Offline: cached reservations/verifiers; sync conflicts; site wins occupancy.

### Walkthrough beat 7

Scale 10×/100×; telemetry aggregation; cells; OTA canary.

### Walkthrough beat 8

Close with trust: wrong-open SEV, ownership, deal-breakers, allocator boundary.

## Pre-Onsite Checklist — Pickup Locker Software

- [ ] Say out loud: not capacity allocation  
- [ ] State machine from memory  
- [ ] Grant fields from memory  
- [ ] Offline conflict rule  
- [ ] Progressive scale jumps  
- [ ] Wrong-open as trust SEV  
- [ ] OTA rollback  
- [ ] Telemetry aggregation  
- [ ] 60-second closer  
- [ ] Two deal-breakers  

### Extra drills (rapid)

State machine 60s · grant fields · site-vs-cloud truth · offline 6h playbook · PIN lockout · OTA canary · remote unlock · allocator boundary · latency budget · idempotent sync · FAULTED UX · home cell · audit schema · cost/pickup · 100× telemetry · sensor debounce · dirty boot · QR one-time · dual-control bulk · wrong-open SEV · reservation cache sig · wrong-package scan · reclaim · accessibility · no cloud GPIO · fence vs lease · PIN retention · cell failover · OR-allocator trap · 60s closer.

---

*End of pickup locker software system design.*
