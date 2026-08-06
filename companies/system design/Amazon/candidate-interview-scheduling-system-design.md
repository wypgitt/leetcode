# System Design: Candidate Interview Scheduling Platform

> **Focus areas:** Calendars · Availability · Interview loops · Rooms / interviewers · Timezones · Reschedule · Holds & conflicts · Notifications · Fairness / load balancing interviewers  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct timezone arithmetic, explicit hold/lease semantics, split read availability vs booking transactions, deal-breakers for “just store UTC strings without zone rules” or “double-book rooms is fine”  
> **Interview theme:** Amazon SDE III / L6 — design a **candidate interview scheduling** platform used by recruiters/coordinators: multi-party availability, loops, rooms, timezone-safe scheduling, reschedule storms—own consistency and operational load

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

Goal: **bound the scheduling product**—recruiters build **interview loops** (multi-slot panels), the system finds times when **candidate + interviewers (+ rooms)** are free across **timezones**, books with calendar sync, handles **reschedules/cancels**, and notifies all parties—not a full ATS, and not generic Calendly-only 1:1.

### 1.0 What this is / is not

| Dimension | **Interview scheduling (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Schedule multi-interviewer loops with candidates | Full Workday/Greenhouse ATS |
| Success | Conflict-free bookings; low reschedule pain | Perfect AI matching of interviewer quality alone |
| Hard problem | Multi-resource availability + holds + TZ | Simple single calendar CRUD |
| Resources | People, rooms, optional equipment | Only Zoom links |
| Amazon lens | Ownership of double-book bugs; cost of calendar API; coordinator UX | “Call Google Calendar and done” |
| Integrations | Google/Outlook calendars, Zoom/Chime, ATS hooks | Replace email entirely MVP |

**Scope statement:** Design a candidate interview scheduling platform: availability, loops, rooms/interviewers, timezone-correct booking, reschedule, notifications—at SDE III depth with progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who schedules? | Recruiters / coordinators; sometimes self-serve candidates | RBAC roles |
| F2 | Loop structure? | Ordered stages: OA, phone, onsite loop of N interviews | Loop + slot templates |
| F3 | Interviewers? | Pools by skill/role; backups | Pool matching |
| F4 | Rooms? | Optional physical rooms + video links | Room resource |
| F5 | Availability? | From corporate calendars + working hours | Calendar sync |
| F6 | Candidate TZ? | Explicit; display local times | TZ engine |
| F7 | Holds? | Soft-hold while confirming | Lease/hold service |
| F8 | Reschedule? | Yes—common | Cascading updates |
| F9 | Cancel? | Yes—release resources | Compensating txns |
| F10 | Notifications? | Email/Slack/SMS; calendar invites | Notif + ICS |
| F11 | Self-serve links? | Candidate picks from proposed slots | Slot proposal UX |
| F12 | Constraints? | No back-to-backs beyond X; lunch breaks; interviewer load caps | Constraint solver / filters |
| F13 | Onsite vs virtual? | Both | Location types |
| F14 | Feedback hooks? | After interview, nudge ATS | Events out |
| F15 | Deconflict? | Never double-book interviewer/room | Strong booking txn |

**MVP functional scope:**

1. **Users/roles:** coordinator, interviewer, candidate (limited).  
2. **Loop templates:** define N slots with duration, type, interviewer pool tags.  
3. **Import availability** from Google/Outlook (OAuth) + working hours.  
4. **Propose slots** that satisfy candidate TZ + all required resources.  
5. **Hold** resources briefly; **confirm** booking → calendar events.  
6. **Rooms** and **video conference** link generation.  
7. **Reschedule / cancel** with notifications and calendar updates.  
8. **Interviewer load** basic caps (e.g. max interviews/week).  
9. **Audit log** of who changed what.  
10. Webhooks to ATS (interview scheduled/completed).

**Out of MVP:**

- Full ATS (applications, offers, scorecards deep UI)  
- Optimal constraint solver for 50-dimensional preferences (heuristics OK)  
- Automatic interviewer quality ML ranking (hooks)  
- Global airline travel booking for candidates  
- Replacing corporate calendar systems  
- Guaranteeing cross-org calendar free/busy without OAuth scopes

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Booking correctness | No double-book | Transactional holds |
| N2 | Suggest latency | Interactive coordinator UX | p99 < 2–5s for search |
| N3 | Calendar sync freshness | Free/busy reasonably fresh | < 1–5 min typical |
| N4 | Availability | Business critical during hiring spikes | 99.9% |
| N5 | Timezone correctness | DST-safe | Use proper TZ DB |
| N6 | Scale | Large employers / multi-tenant SaaS | Progressive |
| N7 | Privacy | Candidate PII minimized | ACLs; retention |
| N8 | Idempotency | Retries safe | Booking keys |
| N9 | Consistency | Hold→confirm atomic enough | Lease model |
| N10 | Operability | Debug “why slot shown” | Explainability logs |
| N11 | Rate limits | Calendar API quotas | Cache free/busy |
| N12 | Multi-region | Global candidates | Data residency options |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Coordinator creates loop for candidate → system suggests 3 days of viable onsite sequences → coordinator sends self-serve link → candidate picks → all calendars updated + room booked + Zoom created.  
2. Interviewer declines → system suggests swap from pool → coordinator confirms.  
3. Reschedule one slot → update that event; keep others if possible.  
4. Virtual loop: no room; generate meeting links per slot.  
5. Multi-TZ: candidate in `America/Los_Angeles`, interviewers in `America/New_York` & `Europe/London` — display local, store UTC instants.  
6. Hold expires → resources freed automatically.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two coordinators book same interviewer | Hold/CAS; second fails |
| Calendar API lag shows free but busy | Confirm-time recheck; rollback |
| DST spring forward gap | Slot invalid; regenerate |
| DST fall back overlap | Ambiguous local → use offset/instant |
| Interviewer OAuth revoked | Mark stale; email reconnect |
| Partial loop booking failure | Cancel compensating; don’t leave half-booked |
| Candidate no-show reschedule storm | Rate limit; keep history |
| Room capacity mismatch | Validate attendees vs capacity |
| Back-to-back buffer violated | Filter suggestions |
| Load cap exceeded | Exclude interviewer |
| Concurrent hold same room | One wins lease |
| ICS update lost | Reconciliation job vs calendar |
| Holiday calendars | Respect org holiday calendars |
| Cancel after start | Mark completed/canceled policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Companies (tenants) | 100 | 1K | 10K | 100K |
| Interviewers | 50K | 500K | 5M | 50M |
| Active candidates / week | 20K | 200K | 2M | 20M |
| Interviews booked / day | 50K | 500K | 5M | 50M |
| Peak schedule searches / s | 200 | 2K | 20K | 200K |
| Peak bookings / s | 50 | 500 | 5K | 50K |
| Calendar API calls / s | 1K | 10K | careful | aggressive cache |
| Rooms | 10K | 100K | 1M | multi-M |
| Reschedules / day | 10K | 100K | 1M | 10M |

**What each jump forces:**

- **10×:** Free/busy cache; hold service; calendar workers; TZ-correct model.  
- **100×:** Shard by tenant; slot search indexing; pool-based interviewer selection; webhook fleets.  
- **1,000×:** Cells; approximate search with refine; calendar quota brokers; event sourcing for bookings.

### 1.5 Etc. (Constraints & Assumptions)

- Store **UTC instants** + **IANA timezones** for display; never “PST” abbreviations alone.  
- Calendar providers are **rate-limited third parties**—first-class design constraint.  
- Exact global optimum for loops is NP-hard-ish—use **heuristics + human confirm**.  
- Amazon flavor: hiring surge ownership; double-book is a SEV.

**Scope statement:**

> Design an interview scheduling platform that composes multi-slot loops across candidates, interviewer pools, and rooms with timezone-safe availability, lease-based booking, calendar sync, reschedule flows, and progressive scale—without double-booking and without naive timezone math.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

| Class | Baseline peak | Notes |
|-------|---------------|-------|
| Slot search | 200/s | CPU + free/busy reads |
| Hold create | 80/s | |
| Confirm booking | 50/s | Multi-resource txn |
| Reschedule | 20/s | |
| Calendar sync workers | 1K API calls/s | Cached |
| Notifications | 150/s | Async |
| Candidate self-serve page | 500 rps read | Cacheable suggestions |

### 2.2 Free/busy amplification

```text
Search involving 5 interviewers × 3 pool candidates each = 15 calendars
Naive: 15 calendar API calls per search → 200 searches × 15 = 3K calls/s
Must cache free/busy windows (e.g. 1–5 min TTL) + batch GetFreeBusy
```

### 2.3 Storage

```text
Interviewers 50K × profile 2KB = 100 MB
Interviews 50K/day × 2KB × 365 ≈ 36 GB/year metadata
Calendar sync tokens / channel state: small
Audit logs: larger; retain per policy
```

### 2.4 Slot search CPU sketch

```text
Horizon 10 business days × 8 hours × slots of 1h = ~80 candidate starts/day-grid coarse
For sequence of 4 interviews with buffers: constrained search
Heuristic: pick day → place slots greedily by scarcest resource first
p99 few seconds with cached busy blocks
```

### 2.5 Hold math

```text
Hold TTL 5–15 minutes
Concurrent holds ≈ booking_qps × TTL ≈ 50 × 600s = 30K baseline — fine
At 100×: 3M — need sharded lease store
```

### 2.6 Notification volume

```text
Each confirm → ~N interviewers + candidate + coordinator emails/Slack
50 bookings/s × 6 msgs = 300/s — async queue
```

### 2.7 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | Calendar API quota | Free/busy cache + batch |
| 100× | Search CPU; tenant noise | Shard; index; pool prune |
| 1,000× | Global surge | Cells; approx search; quota broker |

### 2.8 Latency budgets

| Path | Budget |
|------|--------|
| Suggest slots | p99 < 2–5s |
| Hold | p99 < 300ms |
| Confirm | p99 < 1–2s (+ calendar fanout async OK) |
| Reschedule | p99 < 2–3s API; calendar eventual |

### 2.9 Critical bottlenecks

1. Calendar provider quotas.  
2. Multi-resource distributed locking.  
3. Timezone/DST bugs.  
4. Reschedule cascading failures.  
5. Stale free/busy races.

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Never double-book** interviewers/rooms (SEV-class).  
2. **Timezone-correct** by construction.  
3. **Holds** make UX race-safe.  
4. **Calendar APIs** behind cache/quota broker.  
5. **Explainable** suggestions (“excluded: overload”).  
6. **Reschedule** is a first-class state machine.  
7. **Progressive multi-tenant** isolation.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| API Gateway / BFF | Coordinator & candidate UX APIs |
| Loop / Interview Service | Loop definitions & instances |
| Availability Service | Working hours + free/busy merge |
| Slot Search / Suggest | Heuristic multi-slot search |
| Hold / Lease Service | Temporary reservations |
| Booking Service | Confirm/cancel/reschedule txns |
| Resource Service | Interviewers, pools, rooms |
| Calendar Connector | Google/Outlook sync & events |
| Meeting Link Service | Zoom/Chime/Meet |
| Notification Service | Email/Slack/SMS/ICS |
| ATS Webhooks | Outbound events |
| Audit / Explain | Why schedules changed |
| Admin / Config | Org hours, holidays, buffers |

### 3.3 Time model (critical)

```text
Store:
  - start_utc, end_utc as instants
  - candidate_tz, interviewer_tz IANA strings for display
  - floating "local working hours" as TZ rules (e.g. 09:00-17:00 America/New_York)

Never store ambiguous local without zone.
Use tzdb updates (DST rule changes).
All comparisons in UTC instants after resolving local→instant.
```

### 3.4 Resource model

| Resource | Conflicts on |
|----------|--------------|
| Interviewer | Time overlap (+ buffers) |
| Room | Time overlap; capacity |
| Candidate | Time overlap |
| Meeting link | Usually non-exclusive |

**Pool:** logical group (`Barcode interviewers`) → pick one available member under load caps.

### 3.5 Loop & slot model

```text
LoopTemplate: ordered SlotSpecs[]
SlotSpec: { type, duration_min, pool_tags[], room_required?, buffer_before/after }

LoopInstance: for candidate + req
SlotInstance: { status, start, end, interviewer_ids[], room_id, meeting_url }
Statuses: PROPOSED | HELD | BOOKED | COMPLETED | CANCELED
```

### 3.6 API sketch

```text
POST /v1/loops                          # create loop instance from template
POST /v1/loops/{id}/suggest             # body: horizon, constraints
POST /v1/loops/{id}/holds               # hold a suggested sequence
POST /v1/loops/{id}/confirm             # convert hold → booked
POST /v1/loops/{id}/reschedule
POST /v1/loops/{id}/cancel
GET  /v1/candidates/{id}/self-serve/{token}
POST /v1/interviewers/{id}/calendar:connect
GET  /v1/rooms:availability
GET  /v1/loops/{id}/explain/{suggestion_id}
```

### 3.7 Availability merge

```text
busy = union(calendar_freebusy, existing_bookings, holds_others, PTO, holidays)
free = working_hours_minus(busy) intersect org_constraints
For pools: member free sets; pick member with lowest load among free
```

**Buffers:** treat as busy extensions when checking conflicts.

### 3.8 Hold / confirm protocol

```text
1) suggest → returns suggestion_id + slot list (not reserved)
2) hold(suggestion_id, ttl=10m):
     for each resource: acquire lease if free (CAS)
     persist Hold
3) confirm(hold_id):
     revalidate free/busy (best effort)
     create Booking rows
     enqueue calendar event writes + meeting links + notifications
     release hold → booked
4) on TTL: lease cleaner frees holds
```

**Idempotency:** `Idempotency-Key` on confirm.

### 3.9 Calendar sync design

| Direction | Mechanism |
|-----------|-----------|
| Inbound free/busy | Periodic pull + push notifications (Google channels / Graph subscriptions) |
| Outbound events | Create/update/delete events with extended properties `loop_id/slot_id` |
| Reconciliation | Nightly compare bookings vs events |

**Quota broker:** global & per-tenant token buckets for provider API.

### 3.10 Reschedule state machine

```text
BOOKED → RESCHEDULE_PENDING → HOLD_NEW → BOOKED_NEW
                      ↘ cancel new hold → BOOKED (old kept)
Cancel: BOOKED → CANCELED (release + notif)
Partial reschedule: only subset of slots
```

### 3.11 Tradeoffs table

| Decision | A | B | Pick |
|----------|---|---|------|
| Search | Exact ILP solver | Heuristic greedy | Heuristic MVP |
| Holds | DB locks | Redis leases | Redis/DB leases |
| Calendar truth | Provider only | Our DB + sync | Our booking SOT + provider mirror |
| Self-serve | Open any free | Coordinator-approved options | Approved options MVP |
| Room optional | Always | Virtual skip | Skip when virtual |
| Consistency | 2PC all calendars | Book local + async calendar | Local book + async with repair |

### 3.12 Deal-breakers

1. Double-book ignoring races.  
2. Local times without IANA TZ.  
3. Uncached calendar API per search at scale.  
4. Half-booked loops on partial failure.  
5. No hold TTL (orphaned reservations).  
6. Treating Outlook+Google as identical without adapters.  
7. Silent reschedule without notifying interviewers.  
8. Single global mutex for all bookings.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
 Coordinator UX          Candidate self-serve
        │                        │
        └──────────┬─────────────┘
                   ▼
            API / BFF
                   │
     ┌─────────────┼───────────────┬──────────────┐
     ▼             ▼               ▼              ▼
 Loop Service  Slot Search   Hold/Booking    Resource Svc
     │             │               │              │
     │             ▼               ▼              │
     │        Availability ◀── Free/Busy Cache    │
     │             │               │              │
     └─────────────┴───────┬───────┴──────────────┘
                           ▼
                 Calendar Connector Workers
                     │            │
              Google/Outlook   Zoom/Chime
                           ▼
                 Notification + ATS webhooks
```

### 4.2 Sequence: suggest → hold → confirm

```text
Coord→Suggest: constraints
Search→Availability (cache): free blocks
Search→score sequences→return suggestions
Coord→Hold(suggestion)
HoldSvc leases interviewers+room+candidate
Coord→Confirm(hold)
Booking persists; enqueue calendar/meeting/notif
Workers write external systems; reconcile
```

### 4.3 Sequence: conflict on confirm

```text
Hold acquired → interviewer calendar shows new busy (external)
Confirm recheck fails → abort confirm; release hold; ask suggest again
```

### 4.4 Sequence: reschedule one slot

```text
Coord picks slot2 new time
Hold new resources
Confirm: update slot2 booking; patch calendar event; notify
Other slots unchanged
```

### 4.5 Multi-tenant cells (100×+)

```text
Cell maps tenant_id → {DB, cache, workers}
Calendar quota broker global with per-cell budgets
```

### 4.6 Onsite loop packing

```text
Same building rooms preferred
Travel buffer between rooms
Lunch blackout windows
Candidate day length caps
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. No two BOOKED/HELD overlaps on same exclusive resource (modulo replace txn).  
2. Loop confirm is all-or-nothing for required slots.  
3. Every BOOKED slot has durable audit + eventual calendar intent.  
4. Hold TTLs always expire.  
5. UTC instants ↔ TZ display conversions tested across DST.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Hold service down | Fail closed (no book) |
| Calendar write fails | Retry queue; booking remains SOT; alert |
| Split brain free/busy | Recheck on confirm; reconcile |
| Worker double-write event | Idempotent extended property keys |
| Partial multi-slot confirm | Single DB txn for booking rows; external async |
| TZDB outdated | Controlled upgrades; tests |

#### 5.1.3 Durability & backup

- Booking DB multi-AZ.  
- Outbox for calendar/notif events.  
- PITR; audit log WORM optional.

#### 5.1.4 Consistency nuances

- Booking DB is **source of truth**.  
- Calendars are **projections** (eventual).  
- Holds are **ephemeral leases**.  
- Candidate self-serve: hold on click; confirm on submit.

#### 5.1.5 Security & privacy

- OAuth tokens in vault; short scopes (`freebusy`, calendar events).  
- Candidate magic links single-use / expiring.  
- PII minimization in logs.  
- RBAC: interviewers see their schedule, not all candidates.  
- GDPR deletion flows.

### 5.2 Scalability

#### 5.2.1 Free/busy cache

```text
Key: (tenant, calendar_id, day_bucket)
Value: busy intervals compressed
TTL 1–5 min; invalidate on push notification
Batch refresh workers prefer off-peak
```

#### 5.2.2 Slot search scaling

- Prune pools early by tag + load.  
- Scarcest resource first (rooms often scarcer).  
- Precompute interviewer day free blocks.  
- Parallelize per-day searches with bound.  
- Cache suggestion results briefly per loop hash.

#### 5.2.3 Booking scaling

- Shard by `tenant_id`.  
- Lease keys `(resource_id, time_range_bucket)`.  
- Avoid large contiguous locks; interval conflict checks via overlap indexes / segment trees in memory per shard.

#### 5.2.4 Calendar quota broker

```text
Global + per-tenant + per-provider budgets
Priority: confirm writes > freebusy refresh > speculative search refresh
Shed speculative traffic first
```

#### 5.2.5 Multi-region

- Tenant home region for bookings (data residency).  
- Candidates global—display TZ only.  
- Calendar connectors near provider endpoints when helpful.

#### 5.2.6 Cost controls

- Cache aggressively.  
- Limit suggestion horizon.  
- Deduplicate notifications.  
- Virtual-first reduces room contention.

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Loop/booking correctness | Scheduling core |
| Calendar connectors | Integrations |
| Availability cache | Scheduling core |
| Notifications | Comms |
| Rooms | Workplace / resources |
| ATS webhooks | Ecosystem |
| TZ correctness | Core + SRE tests |

#### 5.3.2 Safe evolution

- Version loop templates.  
- Adapter interfaces per calendar provider.  
- Feature flags for new constraints.  
- Contract tests for DST vectors.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Zero confirmed double-books | Hard integrity KPI |
| Suggest p99 | < 5s |
| Confirm p99 | < 2s |
| Calendar sync lag | < 5 min p95 |
| Hold expire success | 100% |
| Notif delivery | 99.9% eventually |

Debug: `suggestion_explain` with exclusion reasons.

#### 5.3.4 Progressive scale checklist

**10×:** holds; free/busy cache; outbox calendar; TZ tests.  
**100×:** tenant shards; quota broker; pool prune; self-serve links.  
**1,000×:** cells; approx search; event-sourced booking log; advanced constraints service.

### 5.4 Deep dive: overlap conflict check

```text
function overlaps(a_start, a_end, b_start, b_end):
  return a_start < b_end and b_start < a_end

On hold:
  for resource in resources:
    for existing in booked_or_held(resource, day):
      if overlaps(expanded(existing), expanded(new)): reject
    CAS lease
```

### 5.5 Deep dive: timezone display

```text
instant = 2026-03-08T17:00:00Z
show for LA: 10:00 America/Los_Angeles (DST aware)
show for NY: 13:00 America/New_York
Invite ICS uses UTC with TZID where supported
```

### 5.6 Deep dive: interviewer load balancing

```text
load = interviews_booked in trailing 7d + held
Prefer min-load among eligible free
Caps: hard exclude if load >= max
Fairness optional: rotate among near-equal loads
```

### 5.7 Deep dive: outbox calendar writes

```text
txn:
  write bookings
  write outbox(event_type, payload)
worker:
  create/update calendar event idempotently
  store provider_event_id on slot
```

### 5.8 Deep dive: self-serve candidate link

```text
token binds loop_id + expiry + unused flag
shows 3–10 precomputed options (held lightly or not)
on select: hold→confirm path
prevents open-ended calendar scraping
```

### 5.9 Testing & resilience

| Test | Purpose |
|------|---------|
| DST vectors | TZ correctness |
| Concurrent holds | Mutex/lease |
| Calendar 429s | Quota broker |
| Partial worker failure | Repair |
| Reschedule races | State machine |
| OAuth revoke | UX path |
| Explain snapshots | Debugging |

### 5.10 Comparison: Calendly vs Greenhouse scheduling vs this

| | Calendly-like | Full ATS | This design |
|--|---------------|----------|-------------|
| Focus | 1:1 self-serve | Hiring suite | Multi-resource loops |
| Rooms | Rare | Sometimes | First-class |
| Pools | Limited | Yes | Yes |
| Holds | Simple | Varies | Explicit leases |

### 5.11 Amazon leadership connection (brief)

- Dive deep on double-book root causes.  
- Ownership of calendar quota incidents.  
- Frugality via caching.  
- Customer (coordinator) obsession: explainability.  
- Bias for action: heuristics over perfect solver.

---

## 6. Wrap-Up

### 6.1 30-second recap

> Model loops as ordered slots over **interviewers, pools, rooms, and candidates**. Merge **working hours + cached free/busy** into availability, search with heuristics, then **hold leases** before **confirm**. Bookings in our DB are source of truth; calendar events and meetings are async projections via outbox. All times are **UTC instants + IANA zones**. Reschedule is a state machine with notifications. Scale by caching calendar traffic, sharding tenants, and quota-brokering providers.

### 6.2 Key tradeoffs

1. Heuristic search vs exact solver.  
2. Booking SOT vs calendar SOT.  
3. Hold TTL length vs abandonment.  
4. Self-serve open calendar vs curated options.  
5. Sync confirm vs async calendar.  
6. Pool auto-pick vs coordinator pick.

### 6.3 Risks & follow-ups

- Stale free/busy races.  
- Provider API outages.  
- DST/tzdb updates.  
- Reschedule notification fatigue.  
- Cross-tenant isolation bugs.  
- Complex onsite constraints.

### 6.4 What “good” looks like

- TZ model correct early.  
- Hold/confirm protocol clear.  
- Calendar quota called out.  
- Double-book invariants.  
- Reschedule flows.  
- Progressive scale + ownership.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q14)

1. Self-serve vs coordinator-only?  
2. Onsite rooms required?  
3. Panel interviews (many-to-one)?  
4. Train interviewers / shadows?  
5. OA scheduling in scope?  
6. Multi-day loops?  
7. Travel interviews?  
8. Contractor interviewers external calendars?  
9. Compliance (recording consent)?  
10. Localization?  
11. Mobile apps?  
12. SLA for invite delivery?  
13. Integration list?  
14. Out of scope?

### 7.2 Time & availability (Q15–Q34)

15. IANA vs offset storage.  
16. DST gap handling.  
17. Working hours exceptions.  
18. Holidays.  
19. Buffer policies.  
20. Free/busy privacy (show busy only).  
21. Cache invalidation.  
22. Push vs poll sync.  
23. Recurring busy blocks.  
24. Focus time / OoO.  
25. Secondary calendars.  
26. Shared inboxes.  
27. Ambiguous ICS updates.  
28. Clock skew.  
29. Suggest horizon limits.  
30. Business days only.  
31. Lunch windows.  
32. Max day length.  
33. Cross-midnight slots.  
34. Approximate vs exact availability.

### 7.3 Booking & concurrency (Q35–Q52)

35. Hold TTL tuning.  
36. Distributed leases.  
37. Interval indexing.  
38. Confirm revalidation.  
39. Idempotency keys.  
40. Compensating transactions.  
41. Partial loop failure.  
42. Room + interviewer atomicity.  
43. Deadlock avoidance.  
44. Overload caps.  
45. Backup interviewer swap.  
46. Optimistic vs pessimistic.  
47. Outbox pattern.  
48. Reconciliation jobs.  
49. Cancel races.  
50. No-show handling.  
51. Double confirm clicks.  
52. Multi-coordinator contention.

### 7.4 Product flows (Q53–Q66)

53. Self-serve token security.  
54. Notification templates.  
55. Slack interactive reschedule.  
56. Explainability UX.  
57. Pool tagging taxonomy.  
58. DEI / fairness constraints.  
59. Interviewer preferences.  
60. Candidate preferences.  
61. Video link per slot vs one.  
62. Onsite badge/visitor hooks.  
63. Feedback reminders.  
64. ATS webhook retries.  
65. Analytics (time-to-schedule).  
66. Accessibility.

### 7.5 Scale & Amazon (Q67–Q80)

67. Tenant noisy neighbor.  
68. Calendar 429 SEV.  
69. Cell migration.  
70. Cost model.  
71. Load test design.  
72. DST regression suite ownership.  
73. Privacy review.  
74. Multi-region residency.  
75. Bar-raiser double-book story.  
76. Dive deep sync bug.  
77. Frugality caching.  
78. Cross-team connector ownership.  
79. Hiring surge playbook.  
80. 45-minute plan.

---

## 8. Appendices

### Appendix A — Slot status cheat sheet

| Status | Meaning |
|--------|---------|
| PROPOSED | Suggestion only |
| HELD | Leased |
| BOOKED | Confirmed |
| COMPLETED | Done |
| CANCELED | Released |
| RESCHEDULE_PENDING | Transition |

### Appendix B — Suggestion response (sample)

```json
{
  "suggestion_id": "sg_1",
  "slots": [
    {
      "type": "coding",
      "start": "2026-08-12T16:00:00Z",
      "end": "2026-08-12T17:00:00Z",
      "interviewers": ["u_42"],
      "room_id": "r_9",
      "candidate_local": "09:00–10:00 America/Los_Angeles"
    }
  ],
  "exclusions_sample": ["u_7 over weekly cap"]
}
```

### Appendix C — Hold record

```json
{
  "hold_id": "h_9",
  "loop_id": "L_1",
  "expires_at": "2026-08-06T18:10:00Z",
  "resources": [{"type":"interviewer","id":"u_42"},{"type":"room","id":"r_9"}]
}
```

### Appendix D — Error codes

| Code | Meaning |
|------|---------|
| 409 | Conflict / lease lost |
| 410 | Hold expired |
| 422 | Constraint violation |
| 429 | Calendar quota / rate limit |
| 503 | Provider outage |

### Appendix E — Anti-patterns

- Store “10am PST” strings only.  
- No holds; last-write wins calendars.  
- Sync calendar as SOT without local booking.  
- One search = dozens of live API calls uncached.  
- Ignoring DST tests.  
- Emailing without calendar repair path.  
- Global lock table.  
- Half-open loops.

### Appendix F — Capacity worksheet

```text
tenants =
interviewers =
searches_per_sec =
avg_calendars_per_search =
cache_hit_ratio =
booking_per_sec =
hold_ttl_sec =
calendar_quota_budget =
```

### Appendix G — 45-minute timebox

| Min | Topic |
|-----|-------|
| 0–5 | Roles + loop requirements |
| 5–12 | TZ + availability BOTE |
| 12–25 | Suggest/hold/confirm |
| 25–35 | Calendar sync + reschedule |
| 35–42 | Scale + quotas + ownership |
| 42–45 | Wrap |

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| Loop | Multi-slot interview plan |
| Pool | Set of eligible interviewers |
| Hold/Lease | Temporary reservation |
| Free/busy | Busy blocks without details |
| ICS | Calendar invite format |
| Outbox | Reliable async event publish |
| Buffer | Mandatory gap between meetings |

### Appendix I — Ownership RACI

| Item | R | A | C | I |
|------|---|---|---|---|
| Double-book KPI | Booking | Booking | Calendar | Coordinators |
| Free/busy cache | Availability | Scheduling | Integrations | SRE |
| OAuth connectors | Integrations | Integrations | Security | Admins |
| Notifs | Comms | Comms | Booking | Candidates |

### Appendix J — Progressive scale one-pager

| Scale | Must |
|-------|------|
| 1× | Loops + calendar create |
| 10× | Holds + F/B cache + TZ tests |
| 100× | Shards + quota broker + pools |
| 1,000× | Cells + approx search + event sourcing |

### Appendix K — Constraint catalog

| Constraint | Type |
|------------|------|
| Working hours | Hard |
| Calendar busy | Hard |
| Weekly load cap | Hard/soft |
| Buffer | Hard |
| Room capacity | Hard |
| Skill tags | Hard |
| Pref building | Soft |
| No Friday PM | Soft config |

### Appendix L — Minimal threat model

| Threat | Control |
|--------|---------|
| Token leak self-serve | Expiry + single use |
| OAuth token theft | Vault + rotate |
| Enumerate candidates | RBAC |
| Spam bookings | Rate limits |
| Calendar spam | Verified domains |

### Appendix M — Hold pseudocode

```text
function hold(suggestion, ttl):
  resources = expand(suggestion)
  sort(resources) // deadlock avoidance
  for r in resources:
    if not try_lease(r, interval, ttl):
       rollback_acquired(); throw Conflict
  return save_hold(resources, now+ttl)
```

### Appendix N — Confirm pseudocode

```text
function confirm(hold_id, idem):
  if seen(idem): return prior
  hold = get(hold_id)
  assert hold.valid and not expired
  recheck_availability(hold) // best effort
  txn:
    write bookings from hold
    outbox calendar+notif
    delete hold
  return bookings
```

### Appendix O — Interview “say this” (60 seconds)

> “I’d treat bookings in our DB as source of truth with lease-based holds so we never double-book interviewers or rooms. Availability merges working hours with cached free/busy from Google/Outlook under a quota broker. Slot search is heuristic over pools and rooms, timezone-safe with UTC instants and IANA zones. Confirm fans out calendar events and meetings asynchronously via outbox, and reschedule is a first-class state machine. Scale is caching, sharding tenants, and cells—not more live calendar API calls.”

### Appendix P — Related systems map

| System | Relation |
|--------|----------|
| Google Calendar / Outlook | Free/busy + events |
| Zoom/Chime/Meet | Meeting links |
| Greenhouse/Lever | ATS |
| Calendly | Simpler cousin |
| Resource booking (rooms) | Workplace systems |
| Slack | Notifications |

### Appendix Q — Chaos drills

1. Concurrent holds same room.  
2. Calendar API 429 storm.  
3. Kill booking DB primary mid-confirm.  
4. DST transition week.  
5. OAuth revoke mid-loop.  
6. Outbox worker crash.  
7. Reschedule storms.  
8. Cache serving stale busy.

### Appendix R — Metrics catalog

- `suggest_p99`  
- `hold_conflict_rate`  
- `confirm_success_rate`  
- `double_book_count` (must be ~0)  
- `calendar_api_qps`  
- `freebusy_cache_hit`  
- `sync_lag_seconds`  
- `reschedule_rate`

### Appendix S — ICS / event extended props

```text
X-SCHED-LOOP-ID: L_1
X-SCHED-SLOT-ID: S_2
X-SCHED-IDEMPOTENCY: idem_abc
```

### Appendix T — Room search notes

```text
Filter by building, capacity, equipment (whiteboard AV)
Prefer contiguous room for multi-slot same day
Lock room leases same as people
```

### Appendix U — Notification matrix

| Event | Candidate | Interviewers | Coordinator |
|-------|-----------|--------------|-------------|
| Confirm | Yes | Yes | Yes |
| Reschedule | Yes | Yes | Yes |
| Cancel | Yes | Yes | Yes |
| Hold expire | No | No | Optional |

### Appendix V — Comparison checklist

| Checkpoint | Covered? |
|------------|----------|
| TZ model | Yes |
| Holds | Yes |
| Multi-resource | Yes |
| Calendar quota | Yes |
| Reschedule SM | Yes |
| Progressive scale | Yes |
| Deal-breakers | Yes |

### Appendix W — Explainability record

```json
{
  "suggestion_id": "sg_1",
  "considered_interviewers": 12,
  "excluded": [{"id":"u_7","reason":"weekly_cap"}],
  "scorer": "scarce_room_first_v1"
}
```

### Appendix X — Provider adapter interface

```text
getFreeBusy(calendars, window) -> Busy[]
createEvent(cal, event) -> provider_id
updateEvent(...)
deleteEvent(...)
watch(calendar) / renewChannel()
```

### Appendix Y — Data residency

```text
Tenant home region stores PII + bookings
Calendar tokens region-local
Cross-region only anonymized metrics
```

### Appendix Z — Final SDE III checklist

- [ ] Loop/pool/room model  
- [ ] UTC + IANA TZ  
- [ ] Hold/confirm protocol  
- [ ] Free/busy cache + quotas  
- [ ] Reschedule state machine  
- [ ] Outbox calendar projection  
- [ ] Double-book invariant  
- [ ] Ownership/SLOs  
- [ ] 10×/100×/1,000×  
- [ ] Deal-breakers  

---

*End of candidate interview scheduling system design (Amazon SDE III).*
