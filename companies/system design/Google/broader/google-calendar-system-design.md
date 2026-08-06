# System Design: Google Calendar

> **Focus areas:** Events · RRULE recurrence expansion · Invites/RSVP · Free/busy · Notifications · Timezones · Conflict detection · Sharing/ACLs  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct recurrence semantics, timezone/DST honesty, invite consistency under concurrency, free/busy privacy, notification fanout math  
> **Interview theme:** Classic Google L5+ calendar — correctness under time, sharing, and multi-writer invites at consumer + Workspace scale

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

Goal: **bound the product**—a **Google Calendar**-class system: create/edit events (single + recurring), invite attendees with RSVP, compute free/busy, send reminders/notifications, honor timezones/DST, detect conflicts, and share calendars with ACLs—at progressive consumer/Workspace scale.

### 1.0 What this is / is not

| Dimension | **Google Calendar (this doc)** | Not this |
|-----------|--------------------------------|----------|
| Primary job | Authoritative calendars + events with time correctness | Full email (Gmail) or Meet media plane |
| Success | Correct instances, reliable invites, usable free/busy | Perfect global “find a time” ML optimizer MVP |
| Recurrence | RRULE + exceptions (EXDATE/overrides) | Store every expanded instance forever as only model |
| Sharing | Calendar ACLs + per-event visibility | Arbitrary document collab OT |
| Notifications | Reminders, invite updates, push/email | Marketing campaign platform |

**Scope statement:** Design Google Calendar: events, RRULE recurrence, invites, free/busy, notifications, timezones, conflicts, and sharing—scaling through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Core entities? | Users, calendars, events, attendees, ACLs | Relational + indexed time range store |
| F2 | Recurring events? | Yes — RRULE (daily/weekly/monthly/yearly), exceptions | Master + expansion / materialization strategy |
| F3 | Invites? | Email/identity attendees; RSVP yes/no/maybe | Attendee state machine; outbox for emails |
| F4 | Free/busy? | Query busy intervals for users in range | Privacy-safe busy blocks; not full event titles by default |
| F5 | Notifications? | Reminders (popup/email/push); invite updates | Reminder scheduler + push fanout |
| F6 | Timezones? | Per-user TZ; events float or fixed; DST | Store UTC + TZ id; ICU/tzdb updates |
| F7 | Conflicts? | Soft warn on overlap for organizer; hard optional | Conflict check API; no silent drop |
| F8 | Sharing? | Share calendar read/write/freebusy-only | ACL on calendar; event visibility overrides |
| F9 | Resources? | Rooms optional Phase 1.5 | Resource calendars same model |
| F10 | Sync? | Mobile/web incremental sync | Sync tokens / changelog |
| F11 | Attachments? | Links/Drive refs OK; large blobs out | Metadata + external store refs |
| F12 | Working hours / Find a time? | Nice-to-have Phase 1.5 | Free/busy aggregation API |

**MVP functional scope:**

1. CRUD calendars and events (timed + all-day).  
2. Recurring masters with RRULE; exceptions (cancel one, modify one, modify this-and-future).  
3. Invite attendees; track RSVP; send invite/update/cancel notifications.  
4. Free/busy query for a set of users over a time range (busy intervals only).  
5. Reminders at T−N; invite change push/email.  
6. Timezone-correct expansion and display.  
7. Soft conflict warnings for organizer’s own calendars.  
8. Share calendar with roles: owner, writer, reader, freeBusyReader.  
9. Incremental sync for clients (`syncToken`).

**Out of MVP:**

- Full AI “schedule for me” / auto-decline  
- Video conferencing media (deep-link Meet OK)  
- Complex resource booking optimization  
- Cross-org calendar federation beyond iCal/CalDAV hooks  
- Exact Google Workspace all admin policies

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Read latency (month view) | Snappy | p99 < 100–200ms region |
| N2 | Write durability | No lost accepted event | Multi-AZ commit before ACK |
| N3 | Reminder accuracy | Near scheduled time | p99 delivery within 30–60s of target |
| N4 | Invite consistency | Attendees converge | Eventual < few seconds typical; email async |
| N5 | Availability | Consumer critical | 99.9%+ API; degraded sync OK |
| N6 | Privacy | Free/busy ≠ event detail | ACL-enforced projections |
| N7 | Correctness | DST/TZ/recurrence | Property tests; tzdb versioning |
| N8 | Multi-region | Global users | Home-region primary; replica reads |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Create 1:1 meeting → invitee gets email/push → RSVPs yes → both calendars show accepted.  
2. Create weekly standup RRULE → month view shows instances → edit one occurrence title.  
3. Share team calendar as reader → member sees events per ACL.  
4. Free/busy for 5 people next Tuesday → returns busy blocks → organizer picks slot.  
5. Reminder 10 minutes before → mobile push.  
6. User flies US→EU → UI timezone changes; absolute UTC events stay correct.  
7. Cancel series → all future instances removed; attendees notified.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| DST spring-forward gap | Document skip/shift policy; ICU rules |
| DST fall-back overlap | Ambiguous local time → store UTC + original TZ |
| “This and future” split | Split series: old master ends; new master starts |
| Concurrent edit same event | ETag / version; 412 on stale write |
| Invitee declines then re-invite | New sequence number; RSVP reset |
| External attendee (no account) | Email-only; ICS; no free/busy deep |
| Shared calendar write race | Last-writer-wins with version; audit |
| Reminder storm at :00 | Shard reminder queue; jitter |
| Deleted organizer | Transfer or cancel policy |
| Infinite RRULE expand | Cap expand window (e.g. ±2y query); lazy expand |
| Private event on shared cal | Show “Busy” to freeBusyReader |
| Clock skew client | Server time authoritative for reminders |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 50M | 500M | — | Google-scale cells |
| DAU | 10M | 100M | 1B | cell fabric |
| Calendars | 80M | 800M | 8B | sharded |
| Events created/day | 50M | 500M | 5B | hierarchical |
| Recurring masters | 20% of events | same | same | same |
| Peak event read QPS | 50K | 500K | 5M | 50M |
| Peak write QPS | 5K | 50K | 500K | 5M |
| Free/busy QPS | 10K | 100K | 1M | 10M |
| Reminders fired/min peak | 200K | 2M | 20M | 200M |
| Avg attendees / event | 3 | 3–4 | 4 | 5 |
| Sync connections | 5M | 50M | 500M | edge |

**What each jump forces:**

- **10×:** Shard by `calendar_id` / `user_id`; reminder workers; expand cache.  
- **100×:** Cell/home-region; materialized instance windows; free/busy secondary index.  
- **1,000×:** Global cells; notification multi-tier; read replicas + edge sync; hot calendar isolation.

### 1.5 Etc. (Constraints & Assumptions)

- Identity via Google accounts (OAuth); external attendees via email.  
- Primary storage strongly consistent per calendar shard.  
- iCal/ICS interoperability as import/export + email attachments.  
- “Conflict” is soft warning unless resource calendars enforce exclusive booking.  
- Notifications may be at-least-once; clients dedupe by `notification_id`.

**Scope statement to repeat back:**

> Design Google Calendar supporting single and recurring events (RRULE + exceptions), invites/RSVP, free/busy, reminders, timezone-correct display, soft conflicts, and calendar sharing ACLs—with progressive scale via sharding, bounded recurrence expansion, and a dedicated reminder/notification plane.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Event reads** | Month/week views, sync | ~50K/s | ~500K/s | API + cache |
| **Event writes** | Create/update/delete | ~5K/s | ~50K/s | Primary DB |
| **Expand / instances** | Recurrence materialize | bursty | ×10 | Expand service |
| **Free/busy** | Interval queries | ~10K/s | ~100K/s | Busy index |
| **Reminders** | Due firings | ~3K/s avg; spikes | ×10 | Scheduler |
| **Invite fanout** | Email/push per attendee | writes × attendees | ×10 | Outbox |
| **Sync long-poll/WS** | Incremental | millions conns | ×10 | Push tier |

**Anti-pattern:** one “QPS” mixing month-view reads, reminder firings, and SMTP.

### 2.2 Storage math

```text
Event row ~ 2 KB average (title, times, metadata; not attachments)
50M new events/day × 2 KB = 100 GB/day raw
Retain 5 years active-ish: 50M × 365 × 5 × 2KB ≈ 180 TB (order-of)
+ indexes (time range, attendee) ~2–3× → hundreds of TB → shard

Recurring: store master (~same size) + exceptions; do NOT store 10 years of daily instances as rows unless materialized window
```

### 2.3 Recurrence expansion cost

```text
Naive: expand RRULE for next 2 years daily = ~730 instances per master
20% of 50M events/day are masters → if expand all eagerly at write: 10M × 730 = huge write amp

Must: lazy expand on read for visible window OR materialize rolling window (e.g. −1y..+2y) async
Month view: ~42 days × events/day/user — expand only overlapping masters
```

### 2.4 Reminder spike

```text
Many reminders cluster at :00 / :30
200K reminders/min peak baseline → ~3.3K/s average in that minute
With jitter ±30s: flatten peaks
Shard by fire_at + reminder_id hash
```

### 2.5 Free/busy amplification

```text
Find-a-time UI: 8 users × 5 days × poll = heavy if scanning all event rows
Need busy-interval index or pre-aggregated busy segments per user per day
```

### 2.6 Invite fanout

```text
5K writes/s × 30% invites × 3 attendees = 4.5K notification tasks/s
Email provider rate limits → queue + backoff; push is cheaper path for app users
```

---

## 3. High-Level Design

### 3.1 API (representative)

| Op | Semantics |
|----|-----------|
| `POST /v1/calendars` | Create calendar |
| `GET /v1/calendars/{id}/events?timeMin&timeMax&singleEvents=` | List/expand events in range |
| `POST /v1/calendars/{id}/events` | Create event (optional RRULE) |
| `PATCH .../events/{eventId}` | Update; `supportsRecurrenceUpdate` modes |
| `POST .../events/{id}/instances/{ts}/exception` | Modify single occurrence |
| `GET /v1/freeBusy` | Busy intervals for calendars/users |
| `POST .../acl` | Share calendar |
| `GET /v1/sync?syncToken=` | Incremental changes |
| `POST .../events/{id}/rsvp` | Attendee response |

**Event schema (conceptual):**

```text
Event {
  event_id, calendar_id, etag/version,
  title, description, location,
  start: { utc, tz_id?, date? },  // timed vs all-day
  end:   { utc, tz_id?, date? },
  recurrence: { rrule[], exdate[], rdate[] }?,
  recurring_event_id?, original_start?,  // exception instance
  attendees: [{ email, status, optional }],
  visibility: default|public|private|confidential,
  transparency: opaque|transparent,  // busy vs free
  reminders: [{ method, minutes }],
  sequence,   // iCal sequence for updates
  status: confirmed|tentative|cancelled,
  organizer, created, updated
}
```

### 3.2 Data model

| Entity | Key | Notes |
|--------|-----|-------|
| User | `user_id` | primary TZ, settings |
| Calendar | `calendar_id` | owner, type primary/secondary |
| ACL | `(calendar_id, scope)` | role |
| Event master | `(calendar_id, event_id)` | RRULE lives here |
| Exception | `(master_id, original_start)` | override or cancel |
| Attendee | `(event_id, email)` | RSVP |
| Busy segment | `(user_id, day, seg)` | derived |
| Reminder | `(fire_at, reminder_id)` | due queue |
| Changelog | `(calendar_id, sync_id)` | syncToken stream |
| Outbox | `notification_id` | email/push |

### 3.3 Recurrence — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Store masters only; expand on read** | Compact; RRULE truth | CPU on read; harder free/busy | Sparse views; MVP OK small |
| **Materialize all instances** | Fast reads | Storage blowup; RRULE edits painful | Never unbounded |
| **Rolling materialization window** | Balanced | Need backfill job | **Strong L5 pick** |
| **Hybrid: expand cache by query window** | Flexible | Cache invalidation on edit | Hot calendars |

**Chosen MVP:**

1. Source of truth = **master + exceptions**.  
2. **On read** (`singleEvents=true`): expand RRULE into visible `[timeMin, timeMax]` with hard caps.  
3. **Async materializer** maintains instance index for free/busy + reminders for horizon (e.g. 366 days).  
4. Edits: “this event” → exception; “this and future” → split series; “all” → patch master + bump sequence.

**Deal-breaker:** expanding infinite RRULE into unbounded rows at write time.

### 3.4 Timezones & all-day

```text
Timed event: store start_utc, end_utc, start_tz_id (optional floating)
Display: convert with user's view TZ OR event TZ per product rule
All-day: store calendar date (YYYY-MM-DD) not UTC midnight (classic bug)
DST: use tzdb; version pin; never invent offsets by hand
```

### 3.5 Invites & RSVP

```text
Organizer creates event with attendees
  -> persist event (sequence=0)
  -> outbox InviteNotification per attendee
  -> for internal users: copy/shadow onto attendee calendar (or link view)
  -> attendee RSVP -> update attendee row -> notify organizer -> sync

External: ICS METHOD=REQUEST via email; REPLY parsed async
```

**Consistency model:** calendar shard strong for organizer event; attendee copy eventual via outbox. Use `sequence` + `etag` to ignore stale updates.

### 3.6 Free/busy

```text
GET freeBusy(users[], timeMin, timeMax)
  authorize: caller may see freeBusy for target
  for each user: merge opaque busy intervals from busy index
  return {user: [{start, end}]}  // no titles unless ACL allows
```

Privacy: `freeBusyReader` never sees titles; private events → busy only.

### 3.7 Notifications & reminders

| Type | Trigger | Path |
|------|---------|------|
| Invite/update/cancel | Event write | Outbox → Email/Push |
| Reminder | `fire_at` due | Reminder scheduler → Push/Email |
| Shared calendar change | ACL write / event write | Optional digest |

Reminder scheduler: time-sharded leasers pull due rows; at-least-once; idempotent `reminder_id`.

### 3.8 Conflict detection

```text
On write (organizer calendars):
  query overlapping opaque events in [start,end]
  if overlap: return warnings[] (soft) or 409 if resource exclusive
Never block invitee calendars silently — show conflicts in UI
```

### 3.9 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Recurrence SoT | Master + exceptions | Compact, iCal-aligned | Unbounded instance table only |
| Time storage | UTC + TZ id; dates for all-day | DST-safe | Local wall time only |
| Free/busy | Derived busy index | Privacy + speed | Scan all event bodies |
| Sync | Changelog + syncToken | Mobile battery | Full refetch always |
| Reminders | Sharded due queue | Spike-resistant | Single cron table scan |
| Multi-writer | ETag/version | Lost update prevention | Blind last-write without version |

---

## 4. Architecture Diagram

```text
  Web / Mobile / API clients
            |
            v
     +------+-------+
     |  Edge / GFE  |
     +------+-------+
            |
            v
     +------+-------+         +------------------+
     | Calendar API |-------->| ACL / AuthZ      |
     +--+-----+-----+         +------------------+
        |     |
        |     +-------------> +------------------+
        |                     | Sync / Changelog |
        |                     +------------------+
        v
 +------+-------+   expand    +------------------+
 | Event Store  |<----------->| Expand Service   |
 | (sharded)    |             | RRULE engine     |
 +--+----+------+             +------------------+
    |    |
    |    +------------------> +------------------+
    |                         | Busy Index       |
    |                         +------------------+
    v
 +--+---------+   due pull    +------------------+
 | Outbox     |               | Reminder Workers |
 | Notif bus  |               | (leased shards)  |
 +--+---------+               +--------+---------+
    |                                  |
    v                                  v
 Email / FCM / APNs <-----------------+
 ICS parser <---- inbound REPLY mail
```

**Create recurring event path:**

```text
POST event + RRULE
  -> authz calendar writer
  -> validate RRULE (reject pathological)
  -> write master + changelog
  -> enqueue materialize(horizon)
  -> enqueue invites
  -> ACK with etag
```

**Month view path:**

```text
GET events?timeMin&timeMax&singleEvents=true
  -> authz
  -> fetch masters overlapping range (indexed)
  -> expand RRULE ∩ range ∪ exceptions
  -> filter by ACL/visibility
  -> return instances
```

**Reminder path:**

```text
Materializer/writer inserts reminder rows at fire_at
Worker leases shard → claim due → send push → ack complete
On event reschedule → delete/move reminder rows
```

**Free/busy path:**

```text
GET freeBusy
  -> for each calendar: read busy segments in range
  -> merge intervals
  -> strip details
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Accepted writes durable** in multi-AZ store before client ACK.  
2. **ETag/version** required for updates; no silent clobber.  
3. **sequence** monotonic per iCal semantics for attendee updates.  
4. **Reminders at-least-once**; clients/notif idempotent.  
5. **ACL deny by default**; free/busy never leaks titles.  
6. **All-day ≠ UTC midnight**; dates are first-class.  
7. **Exception overrides master** for that `original_start`.

#### 5.1.2 Concurrent invite edits

| Scenario | Handling |
|----------|----------|
| Organizer updates while RSVP in flight | Higher `sequence` wins; stale RSVP rejected or reapplied to new sequence |
| Two organizers (shared writer) | ETag 412; client reload |
| Split “this and future” during attendee view | Attendee receives cancel+new or update per policy |

#### 5.1.3 Notification reliability

```text
Transactional outbox on same shard as event write:
  BEGIN
    write event
    write outbox row
  COMMIT
  async publisher drains outbox → Kafka/PubSub → email/push
```

**Deal-breaker:** send email before durable commit (invite to ghost event).

#### 5.1.4 Reminder exactly-once?

Aim for **exactly-once attempt semantics with at-least-once delivery**:

- Lease row with `owner, expiry`.  
- Send notification.  
- Mark `sent` with idempotency key.  
- Duplicate push OK; UI dedupes.

#### 5.1.5 Partial failure: attendee copy

Internal attendee calendar insert is async. Organizer event is source of truth. Repair job reconciles missing attendee copies from changelog.

### 5.2 Scalability

#### 5.2.1 Sharding

| Key | Pros | Cons |
|-----|------|------|
| `calendar_id` | Locality for month view | Hot shared calendars |
| `user_id` | Good for primary cal | Multi-cal user scatter |
| Cell by home region | Geo latency | Cross-cell invites |

**MVP:** shard by `calendar_id`; secondary index attendee→events async. Hot calendars (university, holidays): read replicas + CDN for public holiday cals.

#### 5.2.2 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | Horizontal API; Redis month-view cache; reminder shards |
| 100× | Busy index mandatory; materializer fleet; regional cells |
| 1,000× | Cell routing; edge sync; isolate celebrity/public calendars |

#### 5.2.3 Hot public calendars

Holidays / sports: treat as **broadcast calendars** — immutable-ish feed, edge cached, not same path as personal ACL calendar.

#### 5.2.4 Query patterns

```text
Primary index: calendar_id + time range (start/end) for masters
Instance index: calendar_id + instance_start for materialized
Attendee index: email/user_id + time (for “on my calendar”)
Busy: user_id + day → interval list (compressed)
```

### 5.3 Maintainability

#### 5.3.1 RRULE engine as library

- Single well-tested expansion library (property tests).  
- Pin **tzdb** version; staged rollout when zones change.  
- Feature flag pathological RRULE rejection (e.g. every second).

#### 5.3.2 Schema evolution

- Event protobuf/JSON versioning.  
- Changelog consumers tolerate new fields.  
- Dual-write busy index during migration.

#### 5.3.3 Observability

| Signal | Why |
|--------|-----|
| Expand latency p99 | Month view SLO |
| Reminder lag histogram | Trust |
| Outbox depth | Invite delay |
| 412 rates | Client sync bugs |
| TZ conversion errors | Data bugs |
| Busy index lag | Stale free/busy |

#### 5.3.4 Testing

- Golden RRULE vectors (RFC 5545 examples).  
- DST transition fixtures (America/Los_Angeles, Europe/Paris).  
- Concurrency tests on ETag.  
- Chaos: kill reminder worker mid-lease.

### 5.4 Security & privacy

- AuthN: OAuth2 / session.  
- AuthZ: calendar ACL + event visibility.  
- Free/busy: separate projection.  
- External ICS: sanitize; no SSRF via attachments.  
- Audit log for ACL changes.

### 5.5 Consistency cheat sheet

| Read | Consistency |
|------|--------------|
| Organizer GET after write | Read-your-write on home shard |
| Attendee view | Eventual (seconds) |
| Free/busy | Eventual from materializer |
| Sync | Monotonic per calendar changelog |

---

## 6. Wrap-Up

### 6.1 Design summary

Google Calendar is a **sharded, strongly consistent-per-calendar** event store with **RRULE masters + exceptions**, a **bounded expansion/materialization** path for views/freebusy/reminders, an **outbox-driven invite plane**, a **leased reminder scheduler**, and **ACL-aware projections** (full event vs free/busy).

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Compact recurrence vs read CPU | Master + expand/materialize | Complexity |
| Soft vs hard conflicts | Soft for people; hard for rooms | UX ambiguity |
| Immediate attendee copy vs async | Async + repair | Brief inconsistency |
| Reminder exactly-once | At-least-once + idempotency | Dup notifies |

### 6.3 Deal-breakers

1. Unbounded eager instance materialization.  
2. Storing all-day as UTC midnight.  
3. Free/busy returning private titles.  
4. Email before durable write.  
5. Blind overwrites without ETag/sequence.  
6. Single global reminder table scan at :00.

### 6.4 Progressive scale one-liner

**Baseline:** shard by calendar, expand-on-read + small horizon materialize → **10×:** caches + reminder shards → **100×:** busy index + regional cells → **1,000×:** cell fabric + edge sync + broadcast calendars.

### 6.5 Interview closing line

> “Source of truth is master + exceptions; we expand into a bounded window for UX and free/busy, drive invites through an outbox, fire reminders via leased time shards, and enforce ACL projections so free/busy never becomes a side channel.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Recurrence & time

**Q1: How do you store RRULE?**  
A: On the master event as RFC 5545 strings (+ parsed canonical form); exceptions as separate rows keyed by `original_start`.

**Q2: Expand on read vs write?**  
A: Hybrid — SoT compact; expand for visible window; async materialize for reminders/freebusy horizon.

**Q3: “Edit this and future”?**  
A: Truncate old series (`UNTIL`/`COUNT`); create new master from `original_start` with remaining rule; notify attendees with sequence semantics.

**Q4: EXDATE vs cancelled exception?**  
A: EXDATE omits; cancelled exception can still carry tombstone for sync/attendees.

**Q5: Floating times?**  
A: Rare; if product supports, store local + TZ semantics carefully—default fixed UTC instant + display TZ.

**Q6: All-day events across timezones?**  
A: Date-based; a “May 5 all-day” is that date in calendar context, not a 24h UTC interval.

**Q7: How to test DST?**  
A: Fixture suite around transitions; assert instance counts and UTC instants.

**Q8: Pathological RRULE?**  
A: Reject or cap (`INTERVAL` too small, huge `COUNT`); protect expand CPU.

### 7.2 Invites & sync

**Q9: Internal vs external attendees?**  
A: Internal: first-class user calendars + push; external: ICS email + REPLY parser.

**Q10: Why `sequence`?**  
A: iCal update ordering; clients discard stale REQUEST/REPLY.

**Q11: syncToken design?**  
A: Per-calendar monotonic changelog id; return deleted tombstones; expire old tokens → full sync.

**Q12: Attendee deleted event locally?**  
A: Hide/decline semantics; organizer master remains; don’t delete organizer copy.

**Q13: Recurring invite RSVP for one instance?**  
A: Exception with attendee status override for that `original_start`.

### 7.3 Free/busy & privacy

**Q14: Why not query events table?**  
A: Leak risk + cost; busy index holds opaque intervals only.

**Q15: Tentative vs busy?**  
A: Include tentative as busy by default; product flag.

**Q16: Working locations?**  
A: Transparent or separate layer; don’t block free/busy incorrectly.

**Q17: Cross-domain free/busy?**  
A: Policy + limited slots; Workspace trust rules; out of consumer MVP.

### 7.4 Notifications

**Q18: Reminder shard key?**  
A: `hash(reminder_id) % N` plus time buckets; workers lease buckets.

**Q19: Reschedule storm?**  
A: Batch update reminder rows; debounce notifications (“event updated”).

**Q20: Exactly-once push?**  
A: Not guaranteed by FCM/APNs; idempotency keys; accept duplicates.

**Q21: Email rate limits?**  
A: Per-recipient + global provider quotas; prioritize transactional invite over digest.

### 7.5 Conflicts & sharing

**Q22: Soft conflict algorithm?**  
A: Interval overlap on opaque events for selected calendars; return warning list.

**Q23: Resource rooms?**  
A: Exclusive booking with transaction on resource calendar; suggest alternatives Phase 2.

**Q24: ACL roles?**  
A: owner/writer/reader/freeBusyReader; event private overrides reader title.

**Q25: Domain-wide delegation?**  
A: Workspace admin — separate authz service; careful audit.

### 7.6 Scale & storage

**Q26: Hot holiday calendar?**  
A: Publish as broadcast feed; edge cache; not personal shard path.

**Q27: 1,000× reminders?**  
A: Hierarchical schedulers (wheel / time buckets), regional notify, massive jitter.

**Q28: Secondary calendars count?**  
A: Users have many; shard by calendar still; list calendars lightweight metadata store.

**Q29: Search events?**  
A: Separate search index (title/desc); eventual; not primary SoT.

### 7.7 Reliability drills

**Q30: Lost outbox publisher?**  
A: Rows remain; another publisher claims; no invite loss.

**Q31: Expand service OOM?**  
A: Cap instances; pagination; fail request with 503 rather than wrong times.

**Q32: Split-brain multi-region write?**  
A: Single home region primary per calendar; avoid multi-master writes.

**Q33: Clock jump?**  
A: TrueTime/atomic skew bounds for reminders; monitor fire lag.

### 7.8 Alternatives & deal-breakers

**Q34: Only Postgres single node?**  
A: Fine prototype; fails write/read scale and reminder spikes.

**Q35: Store every instance for 10 years?**  
A: Storage + update amp deal-breaker for daily RRULEs.

**Q36: Client-only recurrence?**  
A: Divergent ICS engines; server must own expansion for free/busy/reminders.

**Q37: CalDAV only?**  
A: Protocol gateway OK; interior design still needed.

### 7.9 Interview craft

**Q38: How to open?**  
A: Entities, RRULE, invites, free/busy privacy, reminders, TZ — then load classes.

**Q39: What numbers matter?**  
A: Events/day, read QPS, reminder peak, attendees fanout, expand window.

**Q40: What impresses L5+?**  
A: Series split semantics, all-day correctness, outbox, busy projection, hot calendar story.

**Q41: Common mistake?**  
A: Ignoring exceptions/`sequence`, or treating free/busy as “SELECT * FROM events`.

---

### Appendix A — RRULE examples

```text
FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20261231T235959Z
FREQ=MONTHLY;BYMONTHDAY=1
FREQ=YEARLY;BYMONTH=11;BYDAY=4THU   # US Thanksgiving-like
```

### Appendix B — Series split pseudocode

```text
def edit_this_and_future(master, original_start, patch):
  master.rrule = with_until(master.rrule, original_start - epsilon)
  save(master)
  new_master = copy(master)
  new_master.start = original_start
  apply(patch, new_master)
  new_master.sequence = 0
  save(new_master)
  rebind_future_exceptions(master, new_master)
  notify_attendees_split(master, new_master)
```

### Appendix C — Expand algorithm

```text
def expand(master, tmin, tmax, cap):
  assert tmax - tmin <= MAX_WINDOW
  instances = rrule_between(master.rrule, tmin, tmax, cap)
  for ex in exceptions(master):
    remove or replace matching original_start
  return instances
```

### Appendix D — Busy merge

```text
def merge_busy(intervals):
  sort by start
  merged = []
  for iv in intervals:
    if merged and iv.start <= merged[-1].end:
      merged[-1].end = max(merged[-1].end, iv.end)
    else:
      merged.append(iv)
  return merged
```

### Appendix E — Outbox pattern

```text
# same DB transaction as event write
INSERT INTO outbox(id, type, payload, ts)
Publisher:
  SELECT ... FOR UPDATE SKIP LOCKED
  publish(payload)
  delete/mark done
```

### Appendix F — Reminder lease

```text
UPDATE reminders
SET lease_owner=:w, lease_until=now()+30s
WHERE fire_at <= now() AND (lease_until IS NULL OR lease_until < now())
  AND shard=:s
LIMIT 100
```

### Appendix G — ACL matrix

| Role | See details | Write | See free/busy |
|------|-------------|-------|---------------|
| owner | Y | Y | Y |
| writer | Y | Y | Y |
| reader | Y (unless private) | N | Y |
| freeBusyReader | N | N | Y |

### Appendix H — Event visibility

| Visibility | freeBusyReader | reader |
|------------|----------------|--------|
| default | busy | details |
| private | busy | busy/hidden per policy |
| public | details if public cal | details |

### Appendix I — Changelog entry

```text
Change {
  sync_id, calendar_id, event_id,
  op: upsert|delete,
  etag, ts, truncated?
}
```

### Appendix J — NFR card

```text
Month view p99 < 200ms
Write durable multi-AZ
Reminder lag p99 < 60s
Free/busy no title leak
ETag on updates
RRULE expand capped
```

### Appendix K — Pathological RRULE guard

```text
reject if:
  INTERVAL seconds < 60 for FREQ=SECONDLY
  estimated instances in 2y > 50_000
  unknown BY* combo that explodes
```

### Appendix L — Materializer job

```text
on master write:
  enqueue MaterializeJob(calendar_id, event_id, horizon)
worker:
  expand to horizon
  upsert instance_index
  upsert busy_segments
  upsert reminder rows
```

### Appendix M — ICS map

| Method | Meaning |
|--------|---------|
| REQUEST | Invite/update |
| REPLY | RSVP |
| CANCEL | Cancel |
| REFRESH | Re-request |

### Appendix N — Progressive scale table

| Scale | Store | Expand | Reminders | Notif |
|-------|-------|--------|-----------|-------|
| Base | Shard cal | On read + short horizon | DB due scan sharded | Outbox |
| 10× | Replicas | Cache expansions | Many workers | Kafka |
| 100× | Cells | Fleet materializer | Time wheels | Regional |
| 1,000× | Cell fabric | Broadcast special-case | Hierarchical | Edge push |

### Appendix O — Conflict soft-check

```text
overlaps = query_opaque(calendar_ids, start, end)
warnings = [e for e in overlaps if e.id != self.id]
return 200 + warnings  # or 409 for resources
```

### Appendix P — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just use cron for reminders” | Peak clumping; need leased shards |
| “Expand everything at write” | Daily RRULE storage amp |
| “Free/busy = events API” | Privacy + overfetch |
| “Client expands RRULE” | Divergent engines; server SoT |

### Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Master | Recurring series definition |
| Exception | Override/cancel single occurrence |
| Sequence | iCal update counter |
| Opaque | Counts as busy |
| syncToken | Changelog cursor |
| Horizon | Materialization lookahead |

### Appendix R — Worked example

```text
Baseline 5K writes/s, 30% with 3 attendees → 4.5K invite tasks/s
Month view 50K QPS; 95% cache hit → 2.5K expand/DB
Reminders 200K/min peak → ~3.3K/s; 64 shards → ~50/s/shard
Busy index: 10M DAU × 3 busy segs/day written async — fine
```

### Appendix S — 30m interview checklist

1. Clarify RRULE, invites, free/busy privacy, reminders, TZ.  
2. Estimate events/day, read QPS, reminder peaks.  
3. Draw API → sharded store → expand → outbox → reminder workers.  
4. Deep dive series split + all-day + ACL projections.  
5. Walk 10×/100×/1,000×.  
6. List deal-breakers.

### Appendix T — ETag flow

```text
If-Match: "v12"
if event.etag != v12: return 412
else: apply patch; etag=v13; changelog++
```

### Appendix U — Related Google systems (conceptual)

| System | Relation |
|--------|----------|
| Spanner / Megastore | Sharded consistent calendars |
| Pub/Sub | Outbox drain |
| FCM | Mobile push |
| Gmail | ICS email |
| TrueTime | Time bounds |
| Chubby/locks | Optional lease coordination |

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Caches, reminder shards, outbox bus |
| 100× | Busy index, cells, materializer fleet |
| 1,000× | Broadcast cals, edge sync, hierarchical notify |

---

*End of Google Calendar system design.*
