# System Design: Google Calendar

> **Focus areas:** Recurring events · Timezones/DST · Availability · Invites/RSVP · Notifications · ACLs · Consistency · Idempotent mutations  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — calendar appears as a “classic” design; probe expansions, concurrency, and correct time handling  
> **Quality bar:** Honest recurrence expansion; no naive “store every instance forever” without a plan; conflict semantics explicit

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

Goal: design a **calendar** product—users create single and recurring events, invite others, view free/busy, get reminders, across timezones—correct under concurrent edits and extreme recurrence.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Product | Personal + shared calendars (Google Calendar-class) | Full Google Workspace admin |
| Scheduling | Events, invites, availability | Full Zoom+Meet media stack (hooks OK) |
| Rooms | Optional free/busy for rooms | Deep room-reservation LLD (see sibling doc) |
| Uber lens | Consistency, notifications, geo-time correctness | Building Gmail |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Event types? | Timed, all-day, recurring (RRULE) | Master + exceptions model |
| F2 | Calendars? | Multiple per user; share ACLs | Calendar as container |
| F3 | Invites? | Email/app invite; RSVP yes/no/maybe | Attendee records |
| F4 | Reminders? | Push/email/SMS offsets | Notification scheduler |
| F5 | Timezones? | Per-user + per-event TZ | Never store “local only” blindly |
| F6 | Free/busy? | Show busy without details (ACL) | Availability projection |
| F7 | Conflicts? | Warn; allow overlaps (MVP) | Optional hard conflict for rooms |
| F8 | Attachments? | Links / Drive pointers | Object refs |
| F9 | Search? | Title/notes search | Async index |
| F10 | Resources? | Optional rooms | Booking locks if in scope |
| F11 | External? | ICS / CalDAV Phase 2 | Import/export hooks |
| F12 | Permissions? | Owner/writer/reader/freebusy | ACL checks every read/write |

**MVP scope:**

1. Users own calendars; CRUD events.  
2. **RRULE** recurrences with **exceptions** (this/future/all).  
3. Invites + RSVP.  
4. Reminders via push/email.  
5. Multi-timezone correct display.  
6. Free/busy for sharing.  
7. Idempotent updates; concurrent edit strategy (version/ETag).

**Out of MVP:** full CalDAV federation, AI scheduling assistant, complex resource optimization across buildings (see room-reservation doc), Meet WebRTC.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Event read (day/week view) | p99 < 200–400ms |
| N2 | Durability | No lost accepted creates/updates |
| N3 | Reminder accuracy | Within seconds–low tens of seconds |
| N4 | Availability | 99.9%+; degrade search first |
| N5 | Consistency | Read-your-writes for owner; define invitee lag |
| N6 | Correctness | DST/TZ correctness non-negotiable |
| N7 | Scale | See table; expansion must not OOM |

### 1.3 Cases

**Happy:** Create weekly meeting → invite → RSVPs → reminders → exception move one instance.  

| Case | Behavior |
|------|----------|
| Edit “this event only” | Exception overrides master |
| Edit “this and following” | Split series / until |
| DST spring forward | Duration/instant rules per RFC5545 semantics you choose—**state them** |
| Inviter deletes series | Cancel notices; attendee copies update |
| Concurrent edit two devices | ETag/version conflict → reload |
| Infinite RRULE | Expand on read window; don’t materialize unbounded |
| All-day event travel TZ | Store as date, not floating instant mishandled |
| Shared calendar revoke mid-read | Authz fail subsequent |
| Reminder storm at :00 | Shard + jitter |
| Out-of-office spam | Free/busy only sharing |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 5M | 50M | 500M | 1B-class |
| Calendars | 8M | 80M | 800M | 1.5B |
| Events created / day | 20M | 200M | 2B | 5B |
| Peak event writes / s | ~1K | ~10K | ~100K | ~300K |
| Peak view reads / s | ~10K | ~100K | ~1M | ~3M |
| Reminder firings / s peak | ~5K | ~50K | ~500K | ~1M+ |
| Avg attendees / event | 3 | 3 | 4 | 5 |
| Recurring fraction | 30% | 30% | 35% | 35% |

**Jumps:** 10× = shard by `calendar_id`; 100× = reminder materializer fleet + expansion cache; 1,000× = cell isolation, cold series archival, fan-out control for huge guest lists.

### 1.5 Scope repeat-back

> Multi-calendar event system with RRULE masters + exceptions, ACL’d sharing, invites/RSVP, timezone-correct views, and reliable reminders—scaled by calendar sharding and windowed expansion, with optimistic concurrency on mutations.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

| Class | Base peak | 100× | Notes |
|-------|-----------|------|-------|
| View reads | 10K/s | 1M/s | Expand window 1–50 days |
| Event writes | 1K/s | 100K/s | Versioned |
| RSVP writes | 500/s | 50K/s | Attendee rows |
| Reminder schedule ops | 1K/s | 100K/s | Materialize next fire |
| Reminder deliveries | 5K/s | 500K/s | Spiky |
| Free/busy queries | 2K/s | 200K/s | Cacheable |

### 2.2 Expansion math

```text
Week view: ~7 days × ~5 events/day visible ≈ 35 instances / calendar view
Naive expand 10-year daily RRULE to rows: 3650 instances × millions of series = disaster
→ Store master + exceptions; expand for [start,end] query window only
Cache expanded windows for hot calendars (executive / shared)
```

### 2.3 Storage

```text
Event master ~500 B–2 KB; exception ~300 B
20M creates/day × 1 KB ≈ 20 GB/day raw writes (many are updates)
Hot retain years for personal calendars → multi-PB at 100× → tier attachments; index carefully
Attendee rows: 20M × 3 × 100 B ≈ 6 GB/day
```

### 2.4 Reminder spikes

```text
Humans schedule on :00 / :30 → materializer must jitter AND precompute
500K firings/s at 100× needs partitioned due-queues (similar to job scheduler delayed wheel)
```

### 2.5 Bottlenecks

1. Unbounded recurrence materialization  
2. Reminder thundering herds  
3. Huge guest list fan-out (all-hands)  
4. Hot shared calendars (company holidays)  
5. Free/busy storms for scheduling assistants  

---

## 3. High-Level Design

### 3.1 Core model

```text
User → owns Calendars → contain EventSeries (master) + Exceptions + SingleEvents
EventInstance = virtual expansion of series in a time window
Attendee = (event_id|series_id, user, rsvp)
ACL = calendar grants
Reminder = offset rules bound to event/series
```

### 3.2 Recurrence strategies

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Materialize all instances | Simple reads | Storage bomb; long series | Daily × years × users |
| B. Master + expand on read | Compact | CPU on read; complex exceptions | Ignoring exceptions |
| C. Hybrid window materialization | Fast views | Sweeper complexity | — |

**Chosen:** **B for MVP**, **C at 100×** for hot calendars (materialize next N days).

### 3.3 Time storage

```text
Timed events: store UTC instant start/end + event_timezone (for RRULE iteration & display)
All-day: store civil date + timezone floating rules carefully
User display TZ: preference; convert at read
```

**Deal-breaker:** Storing only local wall time without TZ/offset story.

### 3.4 Concurrent edits

```text
Each event/series has etag/version
PUT/PATCH requires If-Match
Conflict → 412; client reloads
Series split operations are transactional on home shard
```

### 3.5 Invites & fan-out

```text
On invite:
  durable attendee rows
  async notify (email/push)
  each attendee may copy stub to their calendar (Google-style) OR view by reference
Pick one model and stick:
  MVP: organizer copy authoritative; attendees have pointer + RSVP; optional copy
```

### 3.6 Free/busy

```text
Projection: intervals where ACL allows freebusy|reader
Cache per user per day bucket
Scheduling assistant queries union of attendees’ busy intervals
```

### 3.7 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Recurrence SoT | Master+exceptions | Compact | Infinite rows |
| Reminders | Delayed job queues | Reliable | Cron scan all events every minute |
| ACL | Calendar-level + event exceptions | Usable | Check only client-side |
| Multi-region | Home cell per calendar | RY W | Dual writers |
| Search | Async | Don’t block write | Sync ES on write path |

### 3.8 Components

1. Calendar API (CRUD)  
2. Expansion Service  
3. ACL Service  
4. Invite / RSVP Service  
5. Reminder Scheduler + Notifier  
6. Free/Busy Service  
7. Notification Gateway  
8. Search Indexer (async)  
9. ICS Import/Export (phase)  
10. Admin / Audit  

---

## 4. Architecture Diagram

```text
Clients (Web/Mobile)
        |
        v
   API Gateway
        |
   +----+----+---------+----------+
   |         |         |          |
   v         v         v          v
Calendar   Expansion Free/Busy  Invite/RSVP
Service    Service   Service    Service
   |         ^         ^          |
   v         |         |          v
Calendar Store (shard by calendar_id / home cell)
   |
   +--> Outbox --> Reminder Materializer --> Notification Gateway
   +--> CDC -----> Search Index
```

### 4.1 Read week view

```text
Client GET /events?cal=X&from&to
  → authz ACL
  → fetch masters overlapping window + exceptions
  → expand RRULE clipped to window
  → merge overrides / cancels
  → return instances
```

### 4.2 Edit “this instance only”

```text
Create Exception(series_id, original_start, overridden fields | cancelled=true)
Bump series etag
Notify attendees of change for that instance
```

### 4.3 Reminder path

```text
Write event → compute next reminder fire times (bounded)
Enqueue delayed jobs (delivery_id idempotent)
Due → fanout channels → mark sent
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Accepted write durable before ACK.  
2. Idempotency keys on create (clients retry).  
3. ETag prevents silent lost updates.  
4. Exception semantics deterministic for a given `(series, original_start)`.  
5. Reminders at-least-once; client/app dedupe by `reminder_id`.  
6. ACL enforced server-side every read/write.  
7. Cancel/delete generates attendee notifications (async OK).  
8. Expansion never requires unbounded memory—windowed.  
9. Home-cell single writer for calendar mutations.  
10. DST tests in CI for RRULE iteration.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG calendars/events; expand in API; Redis reminder ZSET |
| 10× | Shard by calendar_id; async notify; free/busy cache |
| 100× | Expansion cache; reminder fleet; guest-list fan-out limits |
| 1000× | Cells; hybrid materialization; cold storage; QoS for all-hands |

### 5.3 Maintainability

- RRULE library ownership + golden DST fixtures.  
- Explicit series mutation algebra (this / future / all).  
- Feature flags for hybrid materialization.  
- Audit log for shared calendar ACL changes.  

### 5.4 Progressive scale

**1×:** Single region SQL; expand on read; email reminders.  
**10×:** Sharding; push reminders; shared calendars at company size.  
**100×:** Materializer fleets; busy-cache; invite rate limits.  
**1000×:** Global cells; secondary indexes carefully; AI scheduling as separate system.

### 5.5 Huge guest lists

All-hands 50k employees:

- Don’t synchronously write 50k attendee rows in API request—batch.  
- Notifications: topic / hierarchy, not 50k individual emails from writer.  
- Free/busy: approximate or skip individual expansion.

### 5.6 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Expand 10 years into rows on create | Storage/CPU SEV |
| Ignore TZ/DST | Wrong meetings |
| Last-write-wins without versions | Lost updates |
| Reminder = `SELECT * WHERE start≈now` | Meltdown |
| Client-only ACL | Data leaks |
| Dual-active calendar writers | Split series |

---

## 6. Wrap-Up

### 6.1 Designed

Google Calendar-class system: calendars + ACL, master/exception recurrence, windowed expansion, invites/RSVP, free/busy, reminder materializers, optimistic concurrency, home-cell scale.

### 6.2 Decisions to defend

1. Master + exceptions, not infinite instances  
2. UTC instant + event TZ  
3. ETag/version concurrency  
4. Windowed expansion (+ hybrid cache at scale)  
5. Reminder delayed queues with jitter  
6. ACL server-side  
7. Async invite fan-out  

### 6.3 Risks

- RRULE edge cases  
- Reminder spikes  
- Shared hot calendars  
- Partial attendee notify failures  
- Clock skew vs reminder (server time owns fire)

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope MVP vs rooms vs Meet |
| 5–15 | Data model + recurrence |
| 15–25 | Reads/expansion + TZ |
| 25–35 | Invites, ACL, reminders |
| 35–45 | Scale, conflicts, traps |

### 6.5 Closer

> **Calendar:** masters + exceptions, windowed expansion, TZ-correct storage, versioned writes, reminder queues with jitter, ACL’d free/busy—scaled by calendar home shards.

---

## 7. Deeper / Related Interview Questions

### 7.1 Recurrence

**Q: RRULE COUNT vs UNTIL vs infinite?**  
A: Support all; expand only in query window; for reminders materialize next fire only.

**Q: EXDATE / RDATE?**  
A: Exceptions table covers cancels/moves; RDATE as additional starts.

**Q: Split “this and future”?**  
A: Truncate old series `until`; create new series from boundary; migrate future exceptions carefully.

### 7.2 Timezones

**Q: Floating events?**  
A: Rare; all-day often floating dates; timed meetings should be instants.

**Q: TZ database updates?**  
A: Ship tzdata updates; re-evaluate future expansions; don’t rewrite past instants casually.

### 7.3 Consistency

**Q: Invitee sees update lag?**  
A: Eventual via notify; organizer read-your-writes on home cell.

**Q: Two organizers?**  
A: Single organizer MVP; co-host as ACL writer.

### 7.4 Reminders

**Q: At-least-once double notification?**  
A: Idempotent `reminder_fire_id`; client collapse.

**Q: User changes reminder 1 min before?**  
A: Cancel prior scheduled fire; enqueue new.

### 7.5 Free/busy

**Q: Privacy?**  
A: ACL freebusy shows opaque busy blocks.

**Q: Out of office?**  
A: Special event class marking busy.

### 7.6 Rooms (bridge)

**Q: Hard conflict for room?**  
A: Resource calendar with exclusive lock—see `room-reservation-system-design.md`.

### 7.7 Interview traps

| Trap | Pushback |
|------|----------|
| Materialize infinite | No |
| Store local time only | DST bugs |
| Global sequence of all events | Unnecessary |
| SQL cron every second on events table | Won’t scale |
| “Just use cron for each event” | Millions of crons |

### 7.8 Metrics

| Metric | Why |
|--------|-----|
| Expansion p99 | View UX |
| Reminder lag | Trust |
| Conflict 412 rate | Client sync health |
| Invite notify failures | Comms |
| Hot calendar QPS | Scale |

### 7.9 Uber relevance

Scheduling interviews, driver document appointments, or internal tools—same recurrence/reminder patterns; rooms variant for office.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
calendars(calendar_id, owner_id, tz_default, etag, home_cell)
acl(calendar_id, principal_id, role) -- owner|writer|reader|freebusy

event_series(
  series_id, calendar_id, title, description,
  dtstart_utc, duration_ms, event_tz,
  rrule TEXT, etag, organizer_id, created_at)

event_exceptions(
  series_id, original_start_utc,
  cancelled BOOL,
  override_patch JSONB,
  PRIMARY KEY(series_id, original_start_utc))

single_events(...) -- non-recurring

attendees(event_ref, user_id, rsvp, email)

reminders(reminder_id, event_ref, channel, offset_sec, next_fire_at)
```

### 8.2 API checklist

- [ ] `POST /calendars`  
- [ ] `POST /calendars/{id}/events` + Idempotency-Key  
- [ ] `PATCH /events/{id}` + If-Match  
- [ ] `GET /calendars/{id}/events?from&to`  
- [ ] `POST /events/{id}/attendees/{u}/rsvp`  
- [ ] `GET /freeBusy?users&from&to`  
- [ ] Reminder admin / test fire  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Master | Recurring series definition |
| Exception | Override/cancel for an instance |
| Expansion | Compute instances in window |
| ETag | Optimistic concurrency token |
| Free/busy | Opaque availability intervals |
| RRULE | iCalendar recurrence rule |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Master+exception, TZ, expand window, basic reminders |
| 10× | Shards, ACL, push, free/busy cache |
| 100× | Reminder fleet, expansion cache, invite batching |
| 1000× | Cells, hybrid materialization, all-hands fan-out design |

### 8.5 Expansion pseudocode

```text
expand(series, from, to):
  iter = rrule_iterator(series.dtstart, series.rrule, series.event_tz)
  for occ in iter while occ < to:
    if occ < from: continue
    if exception cancelled: skip
    elif exception override: yield override
    else yield instance(occ)
    if safety_count > MAX: break
```

### 8.6 Series edit algebra

| Mode | Effect |
|------|--------|
| This only | Upsert exception |
| This and future | Cut series + new series |
| All events | Patch master; keep exceptions policy |

### 8.7 Interview “say this” (60s)

> Store recurring masters with exceptions; expand only for the view window; keep timed events as UTC instants plus event timezone; versioned writes; reminders via delayed queues with jitter; ACL’d free/busy; shard by calendar home cell.

### 8.8 Reliability tests

1. DST transition weekly meeting.  
2. This-only move then this-and-future edit.  
3. Concurrent PATCH → one 412.  
4. Reminder idempotent redelivery.  
5. ACL revoke stops reads.  

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Week view p99 | < 400ms |
| Write ACK durable | RPO≈0 |
| Reminder lag p99 | < 30s |
| Expansion OOM | Never |

### 8.10 ICS snippet mental model

```text
RRULE:FREQ=WEEKLY;BYDAY=MO;UNTIL=...
EXDATE:20260309T170000Z
```

### 8.11 Reminder sharding

```text
shard = hash(reminder_id) % N
due_queue per shard with lease
jitter fire by hash(user_id) seconds
```

### 8.12 Related systems map

```text
API → Calendar Store → Expansion
                   → Outbox → Reminders → Notify
                   → Free/Busy cache
                   → Invite fan-out
```

### 8.13 Extra traps

| Trap | Pushback |
|------|----------|
| One table of instances only | Recurrence edits nightmare |
| Trust client TZ conversion | Server validates |
| Email as SoT for RSVP | Durable attendee row is SoT |

### 8.14 vs Room reservation

Calendar = soft conflicts OK; Room reservation = exclusive bookings + conflict rejection. Share event model; differ on locking.

### 8.15 Notification preference matrix

| Channel | Default | User mute |
|---------|---------|-----------|
| Push | On | Per calendar |
| Email | On for invites | Per type |
| SMS | Opt-in | Rare |

---


### 8.16 Attendee copy vs pointer model

| Model | Pros | Cons |
|-------|------|------|
| Pointer (attendee views organizer event) | Single SoT | Offline/ACL complexity |
| Copy-on-invite | Attendee autonomy | Sync divergence |
| Hybrid | Practical | Must define which fields sync |

**Interview pick:** Organizer authoritative for time/location; attendee RSVP local; copies update via notifications.

### 8.17 All-day event rules

```text
Store start_date / end_date as civil dates (exclusive end common)
Display in viewer TZ as midnight-to-midnight local **date**, not as UTC instant shift bugs
Travel across TZ should not move the calendar date unexpectedly
```

### 8.18 ACL evaluation order

```text
1. Domain/admin deny
2. Calendar ACL role
3. Event-level private override (if supported)
4. Free/busy fallback for sharing
```

### 8.19 Reminder idempotency key

```text
reminder_fire_id = hash(reminder_id, fire_at_utc_truncated)
deliver(channel); store sent(reminder_fire_id) with TTL
redelivery safe
```

### 8.20 Hot shared calendar pattern

Company holiday calendar read by 100k employees on Jan 1 morning:

- Cache expanded year instances at edge/CDN-ish API cache
- Read replicas
- Don’t expand RRULE per request from scratch under stampede

### 8.21 External ICS sync pitfalls

- Duplicate UIDs
- Clock skew on LAST-MODIFIED
- Partial failure mid-import → idempotent upsert by UID
- RRULE dialects differ—normalize

### 8.22 Scheduling assistant flow (phase)

```text
Input: attendees, duration, window
Fetch free/busy union
Find slots; suggest top K
On book: create event + invites (same write path)
Do not implement assistant as direct DB writer bypassing ACL
```

### 8.23 Data retention

| Data | Retention |
|------|-----------|
| Event bodies | Years (product) |
| Reminder send logs | 30–90d |
| ACL audit | Years |
| Expansion cache | Hours–days |

### 8.24 Unit check: reminder storm

```text
If 10% of 500M users have a :00 reminder aligned → pathological
Jitter ±0..59s + shard due queues; pre-materialize next fire at write time
```

### 8.25 Interview “trap” answers quick sheet

| Trap | Answer |
|------|--------|
| Infinite materialize | Window expand |
| No ETag | Lost update |
| Client TZ only | Server instants |
| Rooms = soft warn | Wrong for exclusive rooms |


*End of Google Calendar system design.*
