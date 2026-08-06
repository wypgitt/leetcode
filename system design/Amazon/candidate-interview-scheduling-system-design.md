# System Design: Candidate Interview Scheduling System

> **Focus areas:** Availability · Timezones · Calendar sync · Matching panels · Holds/locks · Reschedule · Notifications · Fairness · Multi-tenant recruiting
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **Candidate interview scheduling** — coordination under timezone and conflict reality

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-q&a)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design a **candidate interview scheduling system**: gather availability, match interviewers/panels, book with calendar holds, handle reschedule/cancel, notify stakeholders, and scale across orgs/timezones.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Schedule interviews end-to-end | Full ATS/HRIS suite |
| Hard part | Constraints+holds+timezones | Simple CRUD calendar |
| Amazon lens | Candidate experience, interviewer load fairness | Meeting bot spam |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Actors? | Candidate, recruiter, interviewers, coord | RBAC |
| F2 | Availability? | Calendars + manual slots | OAuth sync |
| F3 | Matching? | Skills/level/panel template | Constraints solver |
| F4 | Booking? | Atomic holds→confirm | No double book |
| F5 | Timezones? | First-class | Display local |
| F6 | Reschedule? | Policies + recompute | Notify all |
| F7 | Loops? | Multi-interview sequences | Dependencies |
| F8 | Rooms/Zoom? | Resource booking | Optional |
| F9 | Reminders? | Email/SMS/Slack | Idempotent |
| F10 | Fairness? | Interviewer load caps | Quotas |
| F11 | Multi-tenant? | Companies/orgs | Isolation |
| F12 | Audit? | Who changed schedule | Compliance |

**MVP scope:**

1. Connect calendars
2. Propose slots
3. Hold interviewer+candidate times
4. Confirm booking
5. Reschedule/cancel flows
6. Notifications
7. Panel templates
8. Timezone-correct UI
9. Basic load limits
10. Audit log

**Out of MVP:** Optimal global OR solver for all Amazon interviews; Automatic performance debriefs ML; Replace Outlook entirely.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Slot search | p99<1–2s |
| N2 | Hold integrity | No double book |
| N3 | Notify latency | seconds–minute |
| N4 | Avail freshness | minutes |
| N5 | Timezone correctness | Zero wrong-day bugs SLO |
| N6 | Avail | 99.9% |
| N7 | Privacy | Hide busy details as scoped |
| N8 | Fairness | Caps enforced |

### 1.3 Cases

**Happy:** recruiter requests panel→system finds slots→holds→candidate confirms→calendars updated→reminders.
**Edges:** partial hold fail; calendar webhook delay; DST; interviewer decline; candidate no-show; race two recruiters; room conflict; token expiry.

| Case | Behavior |
|------|----------|
| Duplicate request | Idempotent key returns same result |
| Partial failure mid-path | Compensate or retry with fencing/CAS |
| Hot partition / noisy neighbor | Shuffle shard + fair-share quotas |
| Region / AZ loss | Cell failover; degrade non-critical |
| Clock skew | Server-side truth; opaque tokens |
| Poison input | Quarantine/DLQ; never silent drop of accepted work |
| Authz miss | Fail closed; audit |
| Traffic surge 10× | Shed by priority; preserve SLO class |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Orgs/tenants | 1K | 10K | 100K | 1M |
| Interviews/day | 50K | 500K | 5M | 50M |
| Slot searches/s | 200 | 2K | 20K | 200K |
| Calendar sync events/s | 1K | 10K | 100K | 1M |
| Interviewers | 100K | 1M | 10M | 100M |
| Panel templates | 5K | 50K | 500K | 5M |

**Jumps:** 10× cache avail+async notify; 100× tenant cells; 1,000× smarter matching+global load balancing.

### 1.5 Scope repeat-back

> Constraint-aware interview scheduling with atomic holds, calendar sync, timezone correctness, reschedule, notifications, fairness caps.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Search

```text
Score windows across N interviewers; prune; cache free/busy
```

### 2.2 Holds

```text
Short TTL locks in DB
```

### 2.3 Sync

```text
Webhooks+poll fallback
```

### 2.4 Notify

```text
Outbox emails/chat
```

### 2.X Bottlenecks

(1) Hot keys/partitions (2) synchronous fan-out (3) durable write path (4) auth/token validation (5) downstream blast radius (6) not abstract QPS alone.

### 2.Y Cost / frugality

Prefer cheaper read paths over linear DB growth; measure unit cost per successful customer action; sample observability firehoses.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Availability | Free/busy cache | Eventual minutes |
| Matching | Slot search | Compute |
| Booking | Holds/confirm | Strong |
| Calendar sync | External providers | Best-effort+reconcile |
| Notify | Messages | At-least-once |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Scheduling API** — Search/book
2. **Availability service** — Free/busy
3. **Matcher** — Constraints
4. **Hold service** — Atomic locks
5. **Calendar connectors** — Google/MS
6. **Notification** — Email/Slack
7. **Template service** — Panels
8. **Load/fairness** — Caps
9. **ATS adapter** — Jobs/candidates
10. **Audit** — Changes
11. **Admin** — Policies
12. **Webhook workers** — Sync

### 3.3 API sketch

```text
POST /v1/searches {candidate,panel,window}
POST /v1/holds {slots[]}
POST /v1/holds/{id}/confirm
POST /v1/interviews/{id}/reschedule
GET /v1/availability/{user}
```

### 3.4 State machine

```text
SEARCHED→HELD→CONFIRMED→COMPLETED|CANCELLED|RESCHEDULED
Hold expires→RELEASED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Optimizer | Heuristic search MVP | Speed |
| Hold TTL | 2–15 min | UX vs lock |
| Busy detail | Free/busy only | Privacy |
| Sync | Webhook+reconcile | Truth |
| Auto-book | Semi-auto confirm | Candidate experience |

---

## 4. Architecture Diagram

```text
Recruiter/Candidate UI->Scheduling API->Matcher->Availability Cache
API->Hold Service->Calendars via Connectors
Confirm->Notify Outbox; Webhooks->Availability
```

### 4.1 Book

```text
Search→rank slots→create holds CAS→candidate confirm→write calendars→notify
```

### 4.2 Partial fail

```text
Compensate release holds; don't confirm
```

### 4.3 Reschedule

```text
Cancel old with policy; new search; notify delta
```

### 4.N Cell / blast-radius model

```text
Each cell = failure domain (AZ-set or region slice)
No synchronous cross-cell locks on hot path
Control plane pushes config; data plane serves locally
Shuffle sharding for multi-tenant isolation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. No overlapping confirmed interviews per interviewer
2. Holds expire
3. UTC storage
4. Notifications idempotent
5. Tenant isolation
6. Audit mutations
7. Calendar write after confirm only
8. Privacy of busy details

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG+Redis free/busy |
| 10× | Shard tenants; async notify |
| 100× | Cells; connector pools |
| 1000× | Smarter global matching; predictive slots |

### 5.3 Maintainability

- DST test corpus
- Connector cert rotation
- Hold TTL metrics
- Template versioning

### 5.4 Progressive scale narrative

**1×:** One company
**10×:** Multi-tenant SaaS
**100×:** Global cells
**1000×:** Marketplace interviewers

### 5.5 Atomic holds

DB txn locks interviewer intervals; detect overlap.

### 5.6 DST/timezones

Store UTC instants; render tz; test suites.

### 5.7 Fairness

Rolling load scores; exclude over cap.

### 5.8 Webhook races

Reconcile job is source of truth periodically.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| Double book interviewer | Trust SEV |
| Wrong timezone email | Candidate miss |
| Hold forever | Capacity freeze |
| Sync only poll daily | Stale conflicts |
| Ignore load caps | Burnout/unfairness |
| Confirm before all holds | Partial panels |

---

## 6. Wrap-Up

### 6.1 Designed

Interview scheduling with free/busy, constraint matching, atomic multi-party holds, calendar sync, tz-safe confirms, reschedule, fairness.

### 6.2 Decisions to defend

1. UTC instants
2. Atomic multi-hold
3. Short hold TTL
4. Free/busy privacy
5. Webhook+reconcile
6. Idempotent notify outbox
7. Panel templates
8. Load caps

### 6.3 Risks

- Connector outages
- DST bugs
- Hold stampedes
- Fairness disputes
- Notification spam

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Actors+constraints |
| 5–15 | Hold integrity |
| 15–25 | Matcher+tz |
| 25–35 | Sync+notify+reschedule |
| 35–45 | Fairness+scale |

### 6.5 Closer

> **Candidate Interview Scheduling System**: timezone-correct holds that never double-book, fair interviewer load, reliable notify/reschedule—candidate experience as the SLO.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Why holds?

Prevent double book races.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Hold TTL?

Minutes; UX tradeoff.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: TZ storage?

UTC + display tz.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: DST tests?

Corpus mandatory.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Matcher?

Heuristics+constraints.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Calendar truth?

Webhook+reconcile.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Partial panel?

All-or-nothing confirm.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Fairness?

Load caps/scores.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Privacy?

Free/busy not details.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Reschedule storms?

Policy+rate limits.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Rooms?

Resource as participant.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Who pages?

Scheduling vs connector.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Idempotent notify?

Outbox keys.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Multi-tenant?

Org isolation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

Double-book or wrong tz.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

$/confirmed interview.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

---

## 8. Appendices

### A. Glossary

| Term | Meaning |
|------|---------|
| Cell | Isolated failure domain for blast-radius control |
| Fence / fencing token | Invalidates stale writers after lease steal |
| Idempotency key | Client key making retries safe |
| Outbox | Durable event publish coupled to DB commit |
| Shuffle sharding | Map tenants to overlapping server subsets |
| SLO / error budget | Reliability contract; burn rate drives decisions |
| Unit cost | $ per successful customer action |
| DLQ | Dead-letter queue for poison / exhausted retries |
| Control vs data plane | Config/orchestration vs hot-path serving |
| Progressive scale | Explicit 10×/100×/1,000× architecture jumps |

### B. Ownership matrix

| Concern | Owns | Pages when |
|---------|------|------------|
| Hot-path latency/errors | Serving team | p99 / 5xx burn |
| Durability / data loss risk | Storage/data team | RPO/RTO alarms |
| Abuse / security | Trust & safety / AppSec | exploit or abuse spike |
| Cost regression | Serving + FinOps | unit-cost burn |
| Downstream dependency | Owning service | dependency SEV |

### C. Metrics that matter

- Success rate by criticality class
- Latency histograms (p50/p90/p99) on customer-visible path
- Queue lag / backlog age
- Retry / duplicate attempt rate
- Cache hit ratio where applicable
- Error budget burn rate
- Unit cost trend
- Cell imbalance / hot partition indicators

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope & non-goals |
| 5–12 | Back-of-envelope math |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive invariants & failures |
| 35–45 | Progressive scale, ownership, SEV |

---

## 10. Operability

### Golden signals

search p99, hold success, confirm success, double-book=0, notify lag, connector errors, tz incidents, load cap hits, $/interview

### Rollback ladder

pause confirms→revert matcher→extend hold release→disable connector writes

### Kill switches

disable auto-confirm; freeze tenant; stop reminders; release all expired holds now

### Security / privacy

OAuth least scope; encrypt tokens; RBAC; audit; hide event details

### Cost worksheet

Calendar API quotas + compute search; cache free/busy; bound search windows

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Calendar providers, ATS, notify/email, identity, recruiting ops

---

## More Interview Q&A — Candidate Interview Scheduling System

**Q1. OR-Tools?**

**A:** Optional later; heuristics first.

**Q2. CalDAV?**

**A:** Connector dependent.

**Q3. Focus time?**

**A:** Treat busy.

**Q4. Loop debrief?**

**A:** Separate event type.

**Q5. Scorecards?**

**A:** Out of scheduling MVP.

**Q6. Self-schedule link?**

**A:** Yes common UX.

**Q7. Buffer times?**

**A:** Template constraints.

**Q8. Holidays?**

**A:** Calendar + policy.

**Q9. VIP interviewers?**

**A:** Weighted fairness.

**Q10. What not?**

**A:** Replace corporate calendar.

**Q11. How do you canary this?**

**A:** Percent or cell-scoped; auto-rollback on SLO burn.

**Q12. What is the SEV1 customer line?**

**A:** State impact, blast radius, mitigation, next update ETA.

**Q13. How do you test failure?**

**A:** Game day: kill AZ, dependency timeout, duplicate inject.

**Q14. What is read-your-write strategy?**

**A:** Sticky session, sync path, or version tokens as needed.

**Q15. How do you bound cardinality?**

**A:** Allowlists, quotas, deliberate metric labels.

**Q16. What is the degrade mode?**

**A:** Shed noncritical; preserve integrity/security path.

**Q17. How do you handle poison?**

**A:** Quarantine/DLQ; alert owner; capped redrive.

**Q18. What is multi-region story?**

**A:** Home cell writes; regional reads/failover documented.

**Q19. How do you prevent noisy neighbors?**

**A:** Quotas + shuffle sharding + fair queues.

**Q20. What would you not build in MVP?**

**A:** Optimal global OR solver for all Amazon interviews.

---

## Worked Capacity Narrative — Candidate Interview Scheduling System

Search fanout and calendar API quotas dominate. Cache free/busy; bound panel sizes.

## Customer-Trust Paragraph — Candidate Interview Scheduling System

Double-booking and timezone mistakes destroy candidate and interviewer trust—measure both as SEVs.

## Progressive Scale Recap — Candidate Interview Scheduling System

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Candidate Interview Scheduling System

### S1. Atomic multi-party holds

All-or-nothing booking.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Timezone correctness

UTC storage; local render.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Availability sync

Webhook + reconcile.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Constraint matching

Panel templates + skills.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Fair interviewer load

Caps and scoring.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Idempotent notifications

Outbox delivery.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Reschedule protocols

Compensate + rebook.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Tenant isolation

Org-scoped data.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Candidate Interview Scheduling System

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Double-book detected | Cancel conflicting; page | Trust risk | Hold bugfix |
| Connector outage | Read-only holds; manual | Slow scheduling | Failover |
| DST incident | Freeze sends; patch | Missed interviews | Corpus expand |
| Hold pileup | Shorten TTL; release | Capacity free | Client UX |
| Notify flood | Dedupe; pause type | Spam stopped | Template fix |
| Fairness complaint | Report loads; rebalance | Perception | Cap tune |


## Rapid-Fire Q&A — Candidate Interview Scheduling System

**RQ1. Why does 'Atomic multi-party holds' matter in an L6 interview?**

**A:** All-or-nothing booking. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Atomic multi-party holds' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Atomic multi-party holds' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Timezone correctness' matter in an L6 interview?**

**A:** UTC storage; local render. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Timezone correctness' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Timezone correctness' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Availability sync' matter in an L6 interview?**

**A:** Webhook + reconcile. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Availability sync' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Availability sync' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Constraint matching' matter in an L6 interview?**

**A:** Panel templates + skills. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Constraint matching' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Constraint matching' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Fair interviewer load' matter in an L6 interview?**

**A:** Caps and scoring. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Fair interviewer load' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Fair interviewer load' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Idempotent notifications' matter in an L6 interview?**

**A:** Outbox delivery. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Idempotent notifications' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Idempotent notifications' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Reschedule protocols' matter in an L6 interview?**

**A:** Compensate + rebook. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Reschedule protocols' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Reschedule protocols' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Tenant isolation' matter in an L6 interview?**

**A:** Org-scoped data. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Tenant isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Tenant isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Candidate Interview Scheduling System

### Walkthrough beat 1

Recruiter searches panel in window; ranked slots returned.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

System places holds on interviewers+candidate.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Candidate confirms; calendars written; invites sent.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

One calendar reject→compensate; offer new slots.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Interviewer load cap excludes overused.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Reschedule cancels old; books new; notifies delta.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Webhook updates free/busy cache.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× cache/async; 100× cells; 1,000× smarter matching.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Candidate Interview Scheduling System

- [ ] Can explain **Atomic multi-party holds** with numbers and a deal-breaker
- [ ] Can explain **Timezone correctness** with numbers and a deal-breaker
- [ ] Can explain **Availability sync** with numbers and a deal-breaker
- [ ] Can explain **Constraint matching** with numbers and a deal-breaker
- [ ] Can explain **Fair interviewer load** with numbers and a deal-breaker
- [ ] Can explain **Idempotent notifications** with numbers and a deal-breaker
- [ ] Can explain **Reschedule protocols** with numbers and a deal-breaker
- [ ] Can explain **Tenant isolation** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Double-book detected**
- [ ] Has a 30-second runbook for **Connector outage**
- [ ] Has a 30-second runbook for **DST incident**
- [ ] Has a 30-second runbook for **Hold pileup**
- [ ] Has a 30-second runbook for **Notify flood**
- [ ] Has a 30-second runbook for **Fairness complaint**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Candidate Interview Scheduling System to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Candidate Interview Scheduling System: 1× → 10× break → 100× cells → 1,000× specialization.

### Extra drill

Name three wallboard metrics before a peak event and the action each triggers.

### Extra drill

Write the SEV1 one-liner: impact, blast radius, mitigation, next update ETA.

### Extra drill

Defend your consistency choice: what is lost if weakened, and who notices first.

### Extra drill

Cost challenge: cut 30% without violating the top SLO—what do you shed first?

### Extra drill

Security challenge: compromised credential—how do least privilege, fencing, and audit limit damage?

### Extra drill

Multi-tenant challenge: one tenant sends 100×—show fair-share math and protected queues.


*End of document — Candidate Interview Scheduling System (SDE III)*

