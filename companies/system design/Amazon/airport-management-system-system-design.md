# System Design: Airport Management System

> **Focus areas:** Flights · Gates · Baggage · Passengers · Resource allocation · Turnaround · Irregular ops (IROPS)  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct resource exclusivity (gates/stands), split planes (AODB vs passenger UX vs baggage), explicit IROPS deal-breakers

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

Goal: **bound an airport operating system**—flight schedules, gate/stand allocation, baggage flow, passenger processing touchpoints, and resource allocation under disruption—not building an airline PSS (Amadeus-class) or ATC.

### 1.0 What this is / is not

| Dimension | **Airport management (this doc)** | Not this |
|-----------|-----------------------------------|----------|
| Primary job | Orchestrate airport resources & situational awareness | Air traffic control / takeoff clearances |
| Success | Safe turnarounds; passengers informed; bags delivered | Perfect global airline inventory |
| Flight data | AODB integrates airline/ATC feeds | Own worldwide schedule SoT |
| Passengers | Check-in/boarding status integration | Full ticketing marketplace |
| Baggage | Tracking + carousel/transfer assignment | Build barcode hardware |

**Scope statement:** Design an airport management platform for flights, gates, baggage, passengers, and resource allocation—including IROPS—with progressive scale from one hub through multi-airport ops networks.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Single airport or group? | **One major hub MVP**; multi-airport platform Phase 1.5 | `airport_id` tenancy |
| F2 | Flight SoT? | **AODB** integrates airline messages (SSIM/API), ATC slots | Flight object + versions |
| F3 | Gates/stands? | Assign/reassign; conflicts; compatibility (size, intl) | Resource scheduler + constraints |
| F4 | Turnaround? | Arrival→cleaning→boarding→pushback milestones | Milestone state machine |
| F5 | Baggage? | Check-in → screening → sortation → make-up → claim/transfer | Bag journey events |
| F6 | Passengers? | Manifest counts, boarding progress, connection risk | PAX integration APIs |
| F7 | Resources? | Gates, stands, check-in desks, carousels, tugs, staff thin | Allocation engine |
| F8 | Displays? | FIDS (flight info), gate screens, bag claim signs | Pub/sub read models |
| F9 | IROPS? | Weather/strikes: mass delay/cancel/reassign | Bulk ops + optimization |
| F10 | Notifications? | Airline apps/FIDS/SMS partners | Event fanout |
| F11 | Security zones? | Sterile/non-sterile constraints on bag & PAX flows | Zone graph |
| F12 | Analytics? | On-time performance, bag misconnect, gate util | Warehouse from events |

**MVP functional scope (lock with interviewer):**

1. Ingest flight schedules + updates into AODB.  
2. Allocate gates/stands with conflict detection; manual override.  
3. Track turnaround milestones; publish FIDS.  
4. Baggage: ingest scan events; assign claim carousel; transfer hot bags.  
5. Passenger boarding progress integration; connection alerts thin.  
6. Resource calendars for desks/carousels.  
7. IROPS: delay blast, gate replan assist, passenger/bag impact views.  
8. Role-based ops consoles (AOCC).

**Out of MVP:**

- Full airline reservation / seat maps product  
- ATC trajectory prediction  
- Autonomous airside vehicles deep control  
- Perfect global multi-airport active-active writes  
- Biometric vendor deep dive (interface only)  
- Retail/parking revenue platform

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Allocation correctness | No double-book gate/stand | Strong exclusivity windows |
| N2 | FIDS freshness | Passengers see truth fast | p99 update < 5s from AODB change |
| N3 | Durability | Don’t lose flight/bag events | Quorum + replayable ingest |
| N4 | IROPS burst | Mass updates survive | Backpressure; prioritized AOCC |
| N5 | Integration reliability | Airlines flake | Idempotent ingest; reconcile |
| N6 | Availability | Hub ops critical | 99.95% AODB read; degrade public UX first |
| N7 | Audit | Who moved gate 12? | Immutable change log |
| N8 | Security | Ops vs public planes | Network zones; least privilege |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seasonal schedule load → daily flight instances → optimizer suggests gates → AOCC confirms → FIDS publish.  
2. Aircraft lands → stand occupy → bags to claim carousel → FIDS bag belt update → passengers exit.  
3. Turnaround: arrival, unload, clean, fuel, crew, boarding, doors close, pushback → gate free.  
4. Transfer bag: scanned airside → prioritized to connecting make-up.  
5. Delay +30 → ripple ETAs → possible gate keep or reassign → notify.  
6. Cancel flight → free resources; bag reclaim workflow; PAX rebooking handoff to airline.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two flights same gate overlapping | Constraint solver rejects; suggest alternates |
| Late inbound eats next turn | Detect conflict; reassign next flight early |
| Airline message duplicate/out-of-order | Version/vector; last-applicable-by-rules |
| Bag missort | Exception handling; hot bag chase workflow |
| Carousel full | Reassign claim; FIDS update |
| Boarding mismatch counts | Alert gate agents; don’t auto-close wrong |
| Weather ground stop | Bulk hold; freeze noncritical allocations |
| Stand incompatible (A380 vs stand) | Hard constraint fail closed |
| Connection < MCT | Flag PAX/bags at risk; AOCC worklist |
| FIDS client offline | Local cache + reconcile on reconnect |
| Manual override vs optimizer race | Manual wins with audit; lock window |
| Dual airport codeshare confusion | Flight keys: airline+number+std+origin/op suffix |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 hub) | 10× | 100× | 1,000× |
|--------|------------------|-----|------|--------|
| Airports | 1 | 10 | 100 | 1K (platform) |
| Flights / day | 1K | 10K | 100K | 1M |
| Peak flight updates/s | 20 | 200 | 2K | 20K |
| Gates/stands | 100 | 1K | 10K | 100K |
| Bag scans/s peak | 200 | 2K | 20K | 200K |
| FIDS devices | 500 | 5K | 50K | 500K |
| Concurrent AOCC users | 50 | 500 | 5K | 50K |
| PAX through hub/day | 100K | 1M | 10M | 100M |
| IROPS update burst | 10× | 10× | 10× | 10× |

**Split planes:** AODB writes ≠ bag scan ingest ≠ FIDS fanout ≠ public mobile scrape ≠ optimizer jobs.

**What each jump forces:**

- **10×:** Event-sourced flight timeline; resource booking service; Kafka; FIDS edge cache.  
- **100×:** Multi-airport cells; optimizer as async job; bag stream partitions; CQRS public API.  
- **1,000×:** Platform multi-tenant isolation; hierarchical ops; global reference data; chaos IROPS drills.

### 1.5 Etc. (Constraints & Assumptions)

- Airlines remain SoT for tickets/rebooking; airport orchestrates **resources & info**.  
- Times in UTC internally; display local.  
- MCT (minimum connection time) configurable by connection type.  
- Optimizer suggests; **humans confirm** for MVP contentious moves.  
- Public API is denormalized read model—not direct AODB.

**Scope statement:**

> Design an airport management system centered on AODB flight state, exclusive gate/stand allocation, baggage event journeys, passenger progress integration, FIDS publication, and IROPS replan—from one hub ~1K flights/day through multi-airport 10× / 100× / 1,000× with strict resource exclusivity and split operational planes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Flight updates** | schedule/ETA/status | 20/s | 20K/s | AODB |
| **Allocations** | gate/stand writes | 5/s | 5K/s | Resource svc |
| **Bag scans** | high churn | 200/s | 200K/s | Baggage stream |
| **FIDS fanout** | device pushes | 1K/s | 1M/s | Edge pub/sub |
| **Public query** | apps/websites | 2K/s | 2M/s | CDN read models |
| **Optimizer** | batch/heuristic | periodic | continuous | Jobs |

### 2.2 Flight day math

```text
1K flights/day ≈ 0.01/s average creations
But each flight has dozens of updates (ETA, stand, status, codeshares)
Peak banks (hub waves): updates cluster → design 20/s+

IROPS: 30% of flights delayed in 10 minutes → burst hundreds of updates
```

### 2.3 Baggage math

```text
100K PAX/day × ~1.2 bags ≈ 120K bags
Peak hour ~15% → scans at multiple points (5–10/bag) → hundreds/s peak
Partition by airport + time or bag_tag
```

### 2.4 Storage

| Data | Sketch | Retention |
|------|--------|-----------|
| Flight versions | ~2–10 KB × versions | Hot 7–30d; archive |
| Resource bookings | small | 1y+ |
| Bag events | ~100–300 B | 30–90d operational |
| Audit log | medium | Long compliance |
| FIDS snapshots | derived | minutes–hours |

### 2.5 Gate exclusivity math

```text
booking interval: [on_block - buffer, off_block + buffer]
overlap(a,b) forbidden for same gate if aircraft incompatible rules fail
turnaround_min depends on aircraft type + load
```

### 2.6 FIDS bandwidth

Prefer delta patches per device group (concourse).  
Don’t push full schedule to every screen every second.

---

## 3. High-Level Design

### 3.1 Actor surfaces

| Surface | Actor | Needs |
|---------|-------|-------|
| AOCC console | Airport ops | Flights, gates, IROPS |
| Turnaround app | Ground handlers | Milestones |
| Bag control | Baggage ops | Exceptions, carousels |
| Gate agent | Airline agents | Boarding progress |
| FIDS | Public | Departures/arrivals/claims |
| Airline integration | Carriers | Messages in/out |
| Airport open API | Partners | Read-only flight status |

### 3.2 Domain model

```text
Airport(airport_id, timezone, terminals[])
Flight(flight_id, airline, number, service_date, type IN|OUT, aircraft_type,
       sched_time, estimated, actual, status, version)
Leg linkages: inbound_flight_id ↔ outbound turn
Gate / Stand(resource_id, terminal, constraints: size, schengen/intl, remote)
Allocation(resource_id, flight_id, start, end, state PROPOSED|CONFIRMED|ACTIVE)
Turnaround(flight_in, flight_out, milestones[])
Bag(bag_tag, pax_id?, owning_flight, status, last_scan, destination_carousel?)
PassengerProgress(flight_id, expected, boarded, through_security estimates)
ResourceCalendar(desk/carousel bookings)
```

**Flight status (simplified):**

```text
SCHEDULED → OPEN → BOARDING → LAST_CALL → GATE_CLOSED → DEPARTED
SCHEDULED → LANDED → ON_BLOCK → DEBOARDED → ...
CANCELLED | DIVERTED | REROUTED
```

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| Ingest Gateway | Airline/ATC adapters; idempotent |
| AODB / Flight | Flight SoT timeline |
| Resource Allocator | Gates/stands/desks/carousels |
| Turnaround | Milestone tracking |
| Baggage | Scan ingest + journey |
| PAX Integration | Boarding counts / connections |
| FIDS Publisher | Device read models |
| IROPS Orchestrator | Bulk delay/replan assist |
| Notification | Partner webhooks |
| Optimizer | Suggestions (async) |
| Audit | Who/when/why |

### 3.4 AODB & integrations

- Normalize messages to internal flight events.  
- Identity: `(airline, flight_number, ops_suffix, origin, destination, service_date)` + `flight_id`.  
- **Event versioning:** apply with business ordering rules (actuals > estimates > schedule).  
- Out-of-order: buffer by `message_ts` / sequence if provided.  
- SSIM seasonal loads vs daily ops updates separated.

### 3.5 Gate / stand allocation

**Constraints:**

- No temporal overlap on resource  
- Aircraft wingspan/ICAO code vs stand  
- International vs domestic terminal rules  
- Pier/towing time for remote stands  
- Airline preferences / alliances (soft)  
- Adjacency for transfers (soft)

**Algorithm MVP:**

1. Greedy / CP-SAT style optimizer nightly + continuous repair.  
2. On conflict: produce ranked alternatives.  
3. AOCC confirms → `CONFIRMED` booking with fencing.  
4. Manual drag-drop with validation.

**Exclusivity:** transactional booking insert with exclusion constraint / range lock.

### 3.6 Turnaround milestones

```text
ON_BLOCK → DOORS_OPEN → UNLOAD_DONE → CLEAN_DONE → CATERING_DONE
 → FUEL_DONE → CREW_READY → BOARDING_START → DOORS_CLOSE → OFF_BLOCK
```

Each milestone: timestamp, actor, source (auto sensor vs manual).  
Critical path visibility for delay codes.

### 3.7 Baggage journey

```text
CHECKIN → SCREENING → SORTER → MAKEUP | TRANSFER_SORT → LOADED
Arrival: UNLOAD → CLAIM_SORT → CAROUSEL → (EXIT)
Exceptions: LOST_TRACK, MISCONNECT_RISK, DAMAGED
```

- Ingest scans at-least-once; bag state projector.  
- Carousel assignment from inbound flight allocation.  
- Hot connection: priority lane flag when MCT tight.

### 3.8 Passengers

- Airport doesn’t own PNR deeply—subscribe to airline boarding feeds.  
- Track: expected PAX, security estimates (optional), boarded count, gate no-shows.  
- Connection engine: join inbound arrival ETA + outbound boarding + MCT → risk list for AOCC/airlines.

### 3.9 FIDS & public read models

- Materialize departures/arrivals boards per terminal.  
- Push deltas over fanout; CDN for mobile web.  
- Public plane **cannot** write AODB.  
- Privacy: no PAX PII on public FIDS.

### 3.10 IROPS

Triggers: weather, ATC ground delay, strikes, closure.  
Actions: bulk ETA shift, cancel marks, gate replan job, bag reclaim plans, passenger messaging partners.  
UI: impact heatmap; work queues; freeze optimizer during human storm control optional.

### 3.11 API sketch

```text
POST /v1/ingest/flights                    (partner mTLS)
GET  /v1/flights/{id}
POST /v1/allocations                       Idempotency-Key
POST /v1/allocations/{id}/confirm
POST /v1/turnarounds/{id}/milestones
POST /v1/bags/scans
GET  /v1/fids/{airport}/{board}
POST /v1/irops/bulk_delay
WS   /v1/aocc/stream
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
 Airlines/ATC/Handlers          AOCC / Agents           Public Devices
         │                           │                        │
         ▼                           ▼                        ▼
  ┌─────────────┐            ┌─────────────┐          ┌─────────────┐
  │ Ingest GW   │            │ Ops API GW  │          │ Public GW   │
  └──────┬──────┘            └──────┬──────┘          └──────┬──────┘
         ▼                          ▼                        │
      AODB/Flight ◄────── Resource Allocator                 │
         │                          │                        │
         ├──────── Turnaround       │                        │
         ├──────── Baggage ◄── scans                         │
         ├──────── PAX Integration                           │
         ▼                          ▼                        ▼
              Airport Event Bus (Kafka)
         │              │                │
         ▼              ▼                ▼
   FIDS Publisher   IROPS Jobs      Analytics WH
         │
         ▼
   Edge caches / screens
```

### 4.2 Gate assign sequence

```text
AOCC     Allocator     Constraints     AODB      Bus       FIDS
  |--propose--------▶|--validate-----▶|          |          |
  |                  |--book window--▶|          |          |
  |◀--PROPOSED-------|                |          |          |
  |--confirm--------▶|--CONFIRMED----▶|--update--▶|--delta-▶|
```

### 4.3 Bag scan path

```text
Scanner → ingest (idempotent scan_id) → bag projector →
  if claim assignment needed → carousel svc → FIDS claim board
  if transfer risk → hot bag worklist
```

### 4.4 IROPS burst

```text
Bulk delay request → IROPS orchestrator
  → batch flight updates (chunked)
  → conflict detector for gates
  → suggestion set for AOCC
  → on confirm: allocations + FIDS + partner webhooks
Public API reads CQRS; AODB protected by write rate limits
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No overlapping CONFIRMED allocations** on same gate/stand.  
2. **Flight updates idempotent** by message id / version rules.  
3. **FIDS derived from AODB**, not free-edited public truth.  
4. **Bag scan exactly-effect** by `scan_id` uniqueness.  
5. **Manual override audited** and conflict-checked.  
6. **Actual times immutable** once set (corrections = new events).  
7. **Public plane read-only.**  
8. **IROPS bulk = many small transactional updates**, not one mega txn.  
9. **Airport cell single-writer** for allocations.  
10. **Fail closed on hard compatibility constraints.**

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; PG exclusion constraints; Redis FIDS |
| 10× | Kafka; baggage partitions; allocator service; edge FIDS |
| 100× | Multi-airport cells; async optimizer; CQRS public |
| 1000× | Platform tenancy; regional ops; reference data mesh |

### 5.3 Maintainability

- Adapter contract tests per airline feed  
- Allocation property tests (no overlap)  
- Flight timeline UI  
- Feature flags: freeze auto-assign, public board delay banner  
- Simulation mode for IROPS drills  

### 5.4 Progressive scale (1× → 1000×)

**1× — single hub**

- Postgres AODB + allocations with `tstzrange` exclusion.  
- REST ingest; websocket AOCC.  
- Nightly gate optimizer script.  
- FIDS from Redis snapshots.

**10×**

- Event bus; baggage stream processors.  
- Continuous conflict repair.  
- Device edge agents for screens.  
- Partner webhook delivery with retries.

**100×**

- Airport cells; shared platform control plane.  
- Optimizer service (OR-tools/CP-SAT) async.  
- Connection risk scoring at scale.  
- Multi-tenant IAM.

**1000×**

- Global airport SaaS; strict noisy-neighbor isolation.  
- Hierarchical disruption management.  
- Cross-airport passenger/bag visibility (privacy-heavy).  
- Chaos: feed poison, clock skew, mass cancel.

### 5.5 Allocation deep dive

```sql
-- conceptual exclusion
EXCLUDE USING gist (
  resource_id WITH =,
  time_range WITH &&
) WHERE (state IN ('CONFIRMED','ACTIVE'));
```

Overrides: short lock `resource_id` during drag operations to prevent lost updates.  
Soft constraints scored; hard constraints boolean.

### 5.6 Flight update ordering

```text
apply(msg):
  if msg.id seen: ignore
  if msg.version < current AND not actual-correction: ignore/queue
  merge fields by authority matrix (ATC ground > airline estimate > schedule)
  emit FlightUpdated
```

### 5.7 Baggage misconnect prevention

- Predicted unload + sorter latency + transfer time vs outbound makeup close.  
- Worklist ranked by risk.  
- Don’t promise airline rebooking—surface risk only.

### 5.8 Observability

| SLO | Signal |
|-----|--------|
| AODB ingest success | poison messages quarantined |
| Allocation conflict rate | optimizer quality |
| FIDS lag | p99 from flight update |
| Bag last-scan freshness | sorter health |
| Turnaround milestone completeness | handler adoption |
| IROPS batch duration | storm readiness |

**Kill switches:** freeze auto-realloc; pause public push; ingest dark-mode (buffer only).

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Double-book gates | Airside chaos |
| Public write to AODB | Vandalism |
| One giant IROPS transaction | Outage |
| Bag state = latest scan only without timeline | Lost debugging |
| Optimizer auto-moves without audit | Safety/trust |
| Active-active gate writes | Split brain |
| Polling DB for every FIDS screen | Meltdown |

---

## 6. Wrap-Up

### 6.1 What we designed

An airport ops platform: AODB flight timeline, exclusive resource allocations, turnaround milestones, baggage journey projection, passenger connection risk, FIDS CQRS, and IROPS bulk replan—with humans confirming contentious moves.

### 6.2 Key decisions

| Topic | Decision |
|-------|----------|
| SoT | AODB for airport flight ops state |
| Gates | Exclusion-constrained bookings |
| Optimizer | Suggest; AOCC confirm MVP |
| Baggage | Event-sourced scans | 
| Public | Read models only |
| Scale | Airport cells |

### 6.3 Risks

1. Dirty airline feeds  
2. IROPS human overload  
3. Stand constraint data wrong  
4. Bag infrastructure gaps  
5. Over-automation without audit  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: airport ops not ATC/PSS |
| 5–15 | AODB + flight identity/versioning |
| 15–25 | Gate exclusivity + turnaround |
| 25–35 | Baggage + FIDS |
| 35–45 | IROPS, scale, deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Flight identity

**Q: Codeshares?**  
A: Operating flight primary; marketing flights as views linked to operating `flight_id`.

**Q: Next-day arrivals past midnight?**  
A: `service_date` + UTC instants; display local carefully.

### 7.2 Gates & resources

**Q: Tow to remote stand mid-turn?**  
A: Split allocations with tow window; aircraft position state.

**Q: Why not only optimizer?**  
A: Politics, broken constraints data, safety—human confirm.

**Q: Buffer times?**  
A: Per aircraft + historical taxi; too tight → thrash.

### 7.3 Baggage

**Q: Exactly-once scans?**  
A: Unique `scan_id`; projector idempotent.

**Q: No scan gaps?**  
A: Timers + exception workflows; can’t invent truth.

### 7.4 Passengers

**Q: GDPR on manifests?**  
A: Minimize; purpose limitation; airline remains controller often.

**Q: Connection MCT?**  
A: Configurable matrix by terminal pair / international.

### 7.5 IROPS

**Q: Rebook passengers?**  
A: Airline responsibility; airport provides resource/info impact.

**Q: Mass gate change storm?**  
A: Chunk confirms; prioritize next 2 hours; freeze far-tail.

### 7.6 FIDS

**Q: Consistency vs speed?**  
A: Slight lag OK; wrong gate worse—transactional confirm before public push.

### 7.7 Scale

**Q: Multi-airport single DB?**  
A: OK early; cell by airport when noisy neighbor/IROPS bursts hit.

### 7.8 Failure injection

| Inject | Expect |
|--------|--------|
| Airline feed poison | Quarantine; AODB stable |
| Allocator DB failover | No overlapping books |
| FIDS edge down | Local last frame + stale banner |
| Bag scan spike 20× | Partition lag; AOCC alert; no AODB death |

### 7.9 Amazon-flavored probes

**Q: Customer obsession?**  
A: Accurate FIDS + proactive delay banners; reduce passenger anxiety.

**Q: Ownership?**  
A: Clear pager: ingest vs allocator vs FIDS.

**Q: Dive deep?**  
A: Flight timeline shows every message & gate move.

### 7.10 Comparison traps

| Trap | Better |
|------|--------|
| “It’s Uber for planes” | Resource exclusivity + integrations dominate |
| “Eventual gate booking” | Hard no for CONFIRMED overlaps |
| “ML assigns all gates” | Assist; don’t remove AOCC |
| “Public Kafka access” | No—CQRS API |

### 7.11 Extra traps

**Q: Who wins: airline request vs airport allocate?**  
A: Policy matrix; safety/compatibility airport-hard; preferences soft.

**Q: Sensor says on-block but airline disagrees?**  
A: Authority rules + human resolve; record both.

### 7.12 Progressive scale Q&A

**Q: First bottleneck?**  
A: FIDS polling and allocation conflicts under IROPS.  
**Q: 100×?**  
A: Multi-airport isolation + optimizer runtime.  
**Q: 1000×?**  
A: Tenant isolation and feed diversity.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
flights(
  flight_id PK,
  airport_id,
  airline,
  flight_number,
  service_date,
  direction, -- IN/OUT
  aircraft_type,
  status,
  sched_ts,
  est_ts,
  act_ts,
  version,
  updated_at
);

resources(
  resource_id PK,
  airport_id,
  type, -- GATE/STAND/CAROUSEL/DESK
  terminal,
  constraints_json
);

allocations(
  allocation_id PK,
  resource_id,
  flight_id,
  time_range tstzrange,
  state,
  UNIQUE/EXCLUDE overlap constraint
);

flight_events(
  event_id PK,
  flight_id,
  source,
  payload_json,
  received_at
);

bags(
  bag_tag PK,
  airport_id,
  owning_flight_id,
  status,
  carousel_id NULL,
  updated_at
);

bag_scans(
  scan_id PK,
  bag_tag,
  location,
  scanned_at
);

turnaround_milestones(
  flight_id,
  milestone,
  ts,
  actor,
  PRIMARY KEY(flight_id, milestone)
);
```

### 8.2 API checklist

| API | Idempotent | Strong? |
|-----|------------|---------|
| Ingest flight msg | Yes | Yes |
| Propose allocation | Yes | Yes |
| Confirm allocation | Yes | Yes |
| Bag scan | Yes | Yes (effect) |
| Milestone post | Yes | Yes |
| FIDS read | N/A | Eventual OK |

### 8.3 Authority matrix (sketch)

| Field | Highest authority |
|-------|-------------------|
| Actual on/off block | Airport sensors / handler |
| Schedule | Airline SSIM |
| Estimated time | Airline / ATC mix |
| Gate | Airport allocator |
| Aircraft type swap | Airline message |

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| AODB | Airport Operational Database |
| FIDS | Flight Information Display System |
| IROPS | Irregular operations |
| MCT | Minimum connection time |
| AOCC | Airport Operations Control Center |
| Stand | Aircraft parking position |
| Make-up | Departure bag staging |
| Turnaround | Arrival to next departure process |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | AODB, exclusion allocations, basic FIDS |
| 10× | Event bus, bag projector, edge FIDS |
| 100× | Multi-airport cells, async optimizer |
| 1000× | SaaS isolation, global ref data, chaos drills |

### 8.6 Conflict detection pseudocode

```text
function assign(gate, flight, window):
  if not compatible(gate, flight.aircraft): return HARD_FAIL
  if exists confirmed overlap(gate, window): return CONFLICT(alternatives())
  insert PROPOSED/CONFIRMED with exclusion
```

### 8.7 IROPS runbook (interview gold)

1. Declare disruption mode; optional freeze auto-assign.  
2. Ingest ATC/airline delay programs.  
3. Run conflict detection next N hours.  
4. AOCC applies gate plan in chunks.  
5. Publish FIDS + partner notifications.  
6. Bag reclaim / transfer exception staffing.  
7. Post-event: OTP and misconnect metrics.

### 8.8 FIDS delta message

```json
{
  "board": "DEP.T1",
  "flight_id": "f_1",
  "fields": {"gate": "B12", "status": "BOARDING", "est": "18:40"},
  "version": 17
}
```

### 8.9 Reliability / chaos drills

| Drill | Pass |
|-------|------|
| Feed replay storm | Idempotent; stable boards |
| Allocator failover | No overlap |
| Cancel 200 flights | Chunked; resources freed |
| Clock skew adapters | Quarantine oddities |

### 8.10 Interview “say this” (60s)

> Airport management centers on AODB flight timelines and exclusive gate/stand bookings with hard compatibility constraints. Optimizer suggests, AOCC confirms. Baggage is scan event-sourced; FIDS is a CQRS read plane. IROPS uses chunked bulk updates and conflict repair—not one giant transaction. Scale by airport cells; never let public clients write AODB.

### 8.11 Extra traps

- Using passenger mobile app as SoT for gate  
- Mutable overwriting flight history without events  
- Soft-only constraints for wingspan  
- Coupling bag DB transactions to FIDS HTTP fanout  

### 8.12 Related systems map

| System | Overlap |
|--------|---------|
| Robo-taxi | Resource exclusivity / dispatch |
| Ticketing | Passenger counts integration |
| Job scheduler | Optimizer jobs |
| Webhook delivery | Airline partner notify |
| Warehouse | OTP analytics |

### 8.13 Estimation cheat-sheet

```text
updates/s ≈ flights_in_bank × updates_per_flight / bank_seconds
bag_scans/s ≈ pax_peak/hour × bags/pax × scans/bag / 3600
fids_msgs/s ≈ flight_updates/s × devices_factor (with multicast groups << devices)
```

### 8.14 Leadership mapping

| Principle | Move |
|-----------|------|
| Customer Obsession | Correct gates/times on FIDS |
| Ownership | AOCC tools + clear pagers |
| Dive Deep | Event timeline per flight |
| Frugality | Greedy+human before mega MIP day one |
| Deliver Results | IROPS drills with measurable OTP |

### 8.15 Connection risk sketch

```text
risk if eta_in + transfer_time + buffer > boarding_close_out
rank by pax_count × risk_seconds
```

### 8.16 Multi-airport platform note

Control plane: identity, ref data, billing.  
Data plane: per-airport cell.  
No cross-airport join in MVP hot path.

---

*End of airport-management system design — Amazon SDE III prep artifact.*
