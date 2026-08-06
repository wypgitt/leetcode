# System Design: Microsoft Teams Feature for University Students in Japan

> **Focus areas:** Education tenancy · Japan locale (ja-JP) · Entra ID / school accounts · Compliance (APPI, education data) · Class teams · Assignments/meetings · Peak exam seasons · Regional Azure reliability · Copilot boundaries · Parental/minor considerations
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Tenant isolation sacred; data residency explicit; exam-season load shed plan; deal-breaker = “one global shared DB for all universities’ class content”
> **Interview theme:** Microsoft loop — **Teams feature for university students in Japan**; show M365/Teams platform thinking, not a greenfield chat toy

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

Goal: design a **Microsoft Teams capability set for university students in Japan**—class collaboration, meetings, assignments/files, announcements, mobile-friendly ja-JP UX—running on **education tenancy** with **Japanese compliance**, and surviving **peak exam seasons** (期末試験) when concurrent usage spikes.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Education-oriented Teams feature slice + platform integration | Rebuild all of Teams chat/meetings from zero |
| Tenancy | Entra ID education tenants / school orgs | Consumer Skype/Teams personal only |
| Locale | ja-JP language, calendar, cultural UX, Japan cloud posture | English-only MVP excused forever |
| Compliance | APPI, education records, retention, residency | Ignore legal as “later” |
| Peak | Exam weeks, course registration, orientation | Average-day capacity only |
| Success | Reliable class workflows + trust + isolation | Fancy AI demo without tenancy |
| Microsoft lens | Multi-tenant cells, Graph-facing APIs, Purview hooks | Startup Firebase classroom |

### 1.1 Clarify the “feature” (interview move)

Ask: greenfield classroom product **on** Teams, or **enhancements** to Teams Education (Class Teams, Assignments, Insights)?

**Recommended framing for this doc:** Design **Campus Class Collaboration**—a Teams Education feature pack for Japanese universities:

1. Class Team lifecycle (roster sync from SIS).  
2. Channels for lectures/seminars + announcements.  
3. Assignments with file hand-in + due dates (JST).  
4. Meetings (lectures/office hours) with recording policies.  
5. Student mobile UX localized ja-JP.  
6. Exam-season reliability modes.  
7. Compliance/residency controls for Japan.

### 1.2 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Who? | Students, instructors, TAs, IT admins, (optional) parents for minors | RBAC + edu roles |
| F2 | Identity? | Entra ID campus accounts; Hokkaido–Okinawa unis | Tenant-scoped identity |
| F3 | Roster? | SIS (Student Information System) sync | Periodic + event sync |
| F4 | Class unit? | Class Team per course section | Template + lifecycle |
| F5 | Chat/channels? | Announcements, units, Q&A | Teams channel model |
| F6 | Files? | SharePoint-backed class materials / submissions | SPO storage + perms |
| F7 | Assignments? | Create, submit, grade, return | Assignments service |
| F8 | Meetings? | Scheduled lectures; breakout optional | Teams meetings + policies |
| F9 | Locale? | ja-JP strings, Era/calendar nuances, JST | LOC + time service |
| F10 | Notifications? | Mobile push, email digest; quiet hours | Prefs + JP cultural norms |
| F11 | Search? | Course content within tenant ACL | Compliance-aware search |
| F12 | Analytics? | Instructor insights (privacy-preserving) | Aggregates first |
| F13 | Admin? | Retention, external access, recording defaults | Policy packs Japan |
| F14 | Copilot? | Optional constrained edu scenarios | Data boundaries |

**MVP scope:**

1. Tenant onboarding pack for Japanese university (Japan region).  
2. SIS → roster → Class Team provision.  
3. Instructor announcements + student channel posts (policy).  
4. File materials + assignment submission.  
5. Scheduled meetings with attendance basics.  
6. ja-JP client strings + JST due dates.  
7. Admin compliance defaults (external sharing off, retention).  
8. Exam-season “study hall” scale mode (read-optimized materials, meeting capacity planning).  
9. Basic audit logs for IT.

**Out of MVP:** full national MoE reporting suite, AR classrooms, unconstrained cross-tenant student social graph, training Copilot on tenant data without controls, replacing SIS.

### 1.3 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Message/post send p99 | < 300–500ms perceived |
| N2 | Assignment submit p99 | < 1–2s excl. large upload |
| N3 | Meeting join | Teams meeting SLOs; education peak capacity |
| N4 | Availability | 99.9%+ tenant; degrade noncritical Insights first |
| N5 | Isolation | Hard tenant boundaries; no cross-uni leakage |
| N6 | Residency | Japan geography for edu content by default |
| N7 | Auditability | Admin actions + access patterns for compliance |
| N8 | Locale correctness | ja-JP; JST; no silent UTC due-date bugs |
| N9 | Peak elasticity | Exam weeks 5–20× content reads; meeting concurrency spikes |
| N10 | Accessibility | JP a11y expectations; keyboard/screen readers |
| N11 | Privacy | APPI + education ethics; minimize student profiling |
| N12 | Mobile | Offline-ish reading of cached materials (bounded) |

### 1.4 Japan / education-specific cases

| Case | Behavior |
|------|----------|
| Exam week mass file download | CDN/SPO cache; rate fair-share per tenant |
| Entire lecture joins meeting | Meeting service capacity; lobby policies; overflow live event mode |
| Assignment due 23:59 JST | Store UTC instant; display JST; grace policy configurable |
| Golden Week / academic calendar | Calendar integration; reduced support staffing |
| Instructor posts at night | Student quiet hours default for push |
| External guest lecturer | Controlled guest access; watermark; expiry |
| Student graduates | Lifecycle offboarding; retention holds |
| Suspected harassment in class chat | Edu-safe reporting; eDiscovery/Purview hooks |
| Cross-university club | Separate team/tenant patterns; don’t mix SIS rosters casually |
| Minor students (if applicable) | Extra consent/guardian policies |

### 1.5 Progressive scale

| Metric | Base (1 uni) | 10× | 100× | 1,000× |
|--------|--------------|-----|------|--------|
| Universities / tenants | 1 | 10 | 100 | 1,000 |
| Students | 10K | 100K | 1M | 10M+ |
| Class Teams | 2K | 20K | 200K | 2M |
| Peak concurrent meeting joiners (JP) | 5K | 50K | 500K | multi-million |
| Assignment submits peak / min | 200 | 2K | 20K | 200K |
| Messages/day | 500K | 5M | 50M | 500M |
| Jump | Single tenant solid | Multi-tenant Japan cell | National edu scale | APAC edu platformization |

**Jumps:** 10× = multi-tenant isolation + shared Japan cell; 100× = national exam calendar peak engineering; 1,000× = cross-country education cloud with residency packs.

### 1.6 Scope repeat-back

> A **Teams Education feature pack for Japanese universities**: Entra-backed class tenancy, SIS rostering, channels/files/assignments/meetings, **ja-JP + JST**, **APPI/residency-aware** defaults, and an **exam-season reliability mode**—built as multi-tenant platform services with hard isolation, not a single shared classroom database.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 University baseline

```text
10,000 students × 5 active classes ≈ 50,000 memberships
2,000 class teams
Lectures: 100 concurrent classes × 100 students ≈ 10,000 meeting joins potential
Evenings before exams: file reads 20–50× normal
Assignment deadline cliff: 10% of students submit last 15 minutes → severe hotspot
```

### 2.2 Deadline cliff math

```text
5,000 submissions due tonight × 10% in 15 min ≈ 500 / 15 min ≈ 0.55/s average
But per popular course 400 students × 50% last 5 min ≈ 40/min ≈ burst 5–20/s on one team
Files 5–20 MB → bandwidth + antivirus scanning queues matter
```

### 2.3 Meeting spike

```text
Monday 1st period nationwide: synchronized starts
100 universities × 50 large lectures × 200 students = 1M join attempts window
Must be regionally capacity-planned; join path optimized; backlog UX
```

### 2.4 Storage

```text
Materials + submissions: 2K classes × 500 MB/semester ≈ 1 TB/tenant/semester order-of-magnitude
Recordings: dominate if enabled — policy default off/restricted for edu Japan packs
Chat: small relative to files/media
```

### 2.5 Latency budgets

```text
Announcement post: gateway → channel service authz → persist → fan-out notify
Target ~300ms exclude push
Assignment submit: upload to SPO (chunked) → submit record → receipt
UI should show upload progress; metadata commit < 500ms after upload complete
```

### 2.6 Bottlenecks

(1) Tenant-hot deadline cliffs (2) meeting join stampedes (3) SPO throttling (4) notification storms (5) roster sync storms at semester start (6) search/compliance scans (7) Copilot queries if unconstrained.

### 2.7 Cost / capacity

Recordings + video are cost magnets; exam-season CDN egress spikes. Default policies matter as much as autoscaling.

---

## 3. High-Level Design

### 3.1 Platform principle

Build on Teams/M365 primitives where possible:

| Capability | Prefer existing plane |
|------------|----------------------|
| Identity | Entra ID (Education) |
| Chat/channels | Teams chat/channel services |
| Files | SharePoint/OneDrive |
| Meetings | Teams media / meeting services |
| Compliance | Purview (retention, eDiscovery, DLP) |
| Graph | Microsoft Graph APIs for integrations |
| Device | Intune optional for campus |

**Your feature services** focus on education workflows: rostering, Class Team templates, Assignments, Japan policy packs, exam-season controls, Insights privacy.

### 3.2 Planes

| Plane | Responsibility | Consistency / notes |
|-------|----------------|---------------------|
| Identity / Directory | Users, groups, roles | Entra authoritative |
| Tenant Config | Japan policy pack, locale | Strong |
| Rostering | SIS sync → membership | Eventually synced; reconciler |
| Class Team Lifecycle | Create/archive teams | Strong ops |
| Collaboration | Channels/messages | Teams SLOs |
| Files / Submissions | SPO libraries | Strong perms; eventual search |
| Assignments | Assignment entities/grades | Strong per assignment |
| Meetings | Schedule/join | Meetings plane |
| Notifications | Push/email | Aggregated |
| Compliance | Retention, legal hold, DLP | Policy-driven |
| Observability | Per-tenant SLIs | Cardinality managed |
| Peak Control | Load shed / modes | Control plane |

**Deal-breaker:** storing all universities’ assignment contents in one shared unpartitioned store without tenant_id isolation and residency controls.

### 3.3 Components (feature + integration)

1. **Education Tenant Onboarding** — Japan defaults wizard.  
2. **SIS Connector** — OneRoster/LMS APIs; mapping rules.  
3. **Roster Projection Service** — course→Group/Team membership.  
4. **Class Team Provisioner** — templates (channels, apps, permissions).  
5. **Assignments Service** — create/submit/grade; due_at UTC.  
6. **Submission Storage Adapter** — SPO sites/libraries.  
7. **Announcements Helper** — cross-post policies / translation optional.  
8. **Locale & Calendar Service** — ja-JP, JST, academic calendar.  
9. **Meeting Policy Advisor** — large lecture vs normal meeting.  
10. **Peak Season Controller** — feature flags, fair-share limits.  
11. **Compliance Policy Pack (Japan)** — Purview presets, residency.  
12. **Insights Aggregator** — privacy-preserving instructor dashboards.  
13. **Admin Audit Portal**.  
14. **Graph Webhooks Handler** — membership changes.  
15. **Mobile BFF** — bandwidth-conscious for student apps.  
16. **Copilot Edu Gateway (optional)** — scoped grounding, blocked on exams if policy.

### 3.4 Core APIs (sketch)

```text
POST /edu/v1/tenants/{tid}/sis/sync
POST /edu/v1/courses/{courseId}/provisionTeam
POST /edu/v1/assignments
  {teamId, title, dueAt, resources[], gradeType}
POST /edu/v1/assignments/{id}/submissions
  {studentId, driveItemId, clientSubmitId}
GET  /edu/v1/students/me/schedule?tz=Asia/Tokyo
POST /edu/v1/admin/policyPacks/japan/apply
POST /edu/v1/ops/peakMode
  {mode: EXAM_SEASON, tenantId?}
```

Graph-facing where standard: prefer Microsoft Graph education APIs for roster/assignments when aligning with product reality; custom services for Japan peak/policy pack orchestration.

### 3.5 Class Team template (Japan uni)

```text
Team: [CourseCode] Title - Term
Channels:
  - 一般 (General)
  - お知らせ (Announcements) — students moderated
  - 第1回… (Units) optional
  - 質問 (Q&A)
Apps tabs: Assignments, Files, OneNote Class Notebook optional
Permissions: instructors full; TAs elevated; students restricted posting on お知らせ
```

### 3.6 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Build vs reuse | Reuse Teams/SPO/Meetings | Speed + compliance inheritance |
| Roster source | SIS authoritative | Truth for enrollment |
| Due dates | Store UTC; UX JST | Avoid JP midnight bugs |
| External access | Default deny in JP edu pack | Risk reduction |
| Recordings | Default off / restricted | Privacy + cost + APPI caution |
| Exam mode | Shed Insights/Copilot first | Protect submit/join |
| Multi-tenant DB | Tenant_id + cell Japan | Isolation + residency |
| Offline | Cache materials read-only | Don’t accept graded submit offline blindly |
| Copilot | Explicit opt-in scopes | Edu trust |
| Large lecture | Live event / webinar mode threshold | Meeting scale |

---

## 4. Architecture Diagram

### 4.1 Context (Microsoft ecosystem)

```text
[SIS / LMS] ──sync──► Roster Projection ──► Entra Groups ──► Class Team Provisioner
                                                      │
[Students/Instructors] → Teams Clients (ja-JP) ──► Teams Platform
                                                      │
                         ┌────────────────────────────┼─────────────────────────┐
                         ▼                            ▼                         ▼
                  Channel/Chat svc              SharePoint files           Meetings media
                         │                            │                         │
                         └─────────────── Graph / Eventing ─────────────────────┘
                                      │
                    Assignments Service (edu feature)
                                      │
                    Japan Policy Pack / Purview / Peak Controller
                                      │
                         Azure Japan regions (residency)
```

### 4.2 Assignment submit path

```text
Student → upload bytes via SPO resumable → driveItemId
→ POST submission (idempotent clientSubmitId)
→ Assignments Service validates roster membership + due policy
→ persist submission metadata (tenant_id, assignment_id, student_id)
→ outbox → notify instructor (aggregated)
→ optional plagiarism connectors (policy)
```

### 4.3 Exam-season control plane

```text
Academic calendar / admin trigger → Peak Controller
  - raise capacity targets (meetings, SPO)
  - enable fair-share throttles per tenant
  - disable noncritical Insights jobs
  - Copilot exam lockdown optional
  - prioritize Assignments + Files + Meetings join
  - status banner in ja-JP clients
```

### 4.4 Tenant isolation cell

```text
Japan Education Cell:
  - compute stamps multi-tenant with tenant_id keys
  - data partitions by tid
  - SPO sites in JP geo
  - keys in Key Vault managed HSM postures as required
  - compliance boundaries audited
No query path may omit tenant filter (automated tests).
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Tenant isolation** on every data access (`tenant_id` mandatory).  
2. Roster membership checked on submit/join-sensitive ops.  
3. Assignment submit idempotent by `clientSubmitId`.  
4. Due-time comparisons use absolute instants; UI in `Asia/Tokyo`.  
5. Compliance policies (retention/sharing) enforced server-side, not only UI.  
6. Peak mode never disables audit logging.  
7. Meeting recording follows tenant policy; default safe.  
8. Cross-tenant content sharing requires explicit guest model.  
9. SIS sync reconciler is source for enrollment truth (with override audit).  
10. Failures degrade Insights/Copilot before Assignments/Meetings.

### 5.2 Scalability playbook

| Scale | Moves |
|-------|-------|
| 1× | One uni tenant; standard Teams; Assignments service + SIS CSV/API |
| 10× | Multi-tenant Japan cell; policy pack automation; shared peak calendar |
| 100× | National exam-week capacity program; hierarchical throttles; dedicated SPO/meeting headroom |
| 1000× | Multi-geo education packs; federated campuses; platform SLOs by country |

### 5.3 Maintainability

- Policy packs as versioned config (Japan v1/v2).  
- SIS connector plugin interface (OneRoster, univ-specific).  
- Contract tests for Graph webhooks.  
- Locale freeze process with JP linguistic QA.  
- Chaos drills before 期末.  
- Feature flags per tenant.  
- Clear SEV ownership: Teams core vs edu feature vs SPO.

### 5.4 Progressive scale narratives

**1×:** Single university, one Entra tenant, Class Teams manual + CSV roster, JP locale on, recordings off, assignments in-region.

**10×:** ISV/platform onboarding many private unis; automated policy pack; shared Japan cell; central peak calendar; SIS connectors library.

**100×:** Nearly all major JP universities; Monday 1st-period meeting stampedes; national support war room; fair-share to prevent noisy neighbor; Insights privacy review board.

**1000×:** APAC education cloud; country packs (JP/KR/…); sovereign variations; exam calendars multiple; advanced DL / Copilot edu with grounding controls.

### 5.5 Identity & roles (Entra Education)

| Role | Capabilities |
|------|--------------|
| Student | View materials, post per policy, submit, join |
| Instructor | Manage team, assign, grade, meet, announce |
| TA | Limited grading/moderation |
| IT Admin | Policies, retention, external access, audit |
| SIS Bot | App-only roster sync permissions |

Use education user attributes; group-based licensing; Conditional Access for campus/risky sign-ins.

### 5.6 Rostering deep dive

```text
SIS events: Enroll / Drop / TermEnd
→ Roster Projection maps to Entra security group / Team membership
→ Provisioner ensures Class Team exists for section
→ Reconcile nightly diff to catch missed webhooks
Idempotent membership ops; delay drops slightly if grace period (campus policy)
```

Semester start storm: batch provision; prioritize courses meeting today; backoff Graph throttling.

### 5.7 Locale & time (Japan)

- All server timestamps UTC.  
- Default display `Asia/Tokyo`.  
- Assignment `dueAt` example: `2026-07-31T14:59:59Z` ↔ 23:59 JST (watch DST—Japan has no DST, still use TZ DB).  
- First-day-of-week, name order (family name), furigana fields optional in profile extensions.  
- Push quiet hours default e.g. 21:00–08:00 JST for students.  
- Language packs: Teams client ja-JP; your feature strings CAT/T9n pipeline.

### 5.8 Compliance (APPI + education)

| Control | Approach |
|---------|----------|
| Residency | Japan geo for content/SPO; document exceptions |
| Minimization | Insights aggregates; avoid raw surveillance |
| Purpose limitation | Edu use only; block unsafe exports |
| Retention | Purview retention labels for class content |
| eDiscovery | Legal/admin paths audited |
| DLP | Prevent PII/exams leakage to external |
| Breach process | Tenant admin + Microsoft processes |
| Third parties | SIS connectors under DPA |

Interview signal: name **APPI**, residency, retention, and **tenant isolation** early.

### 5.9 Exam-season reliability mode

**Triggers:** academic calendar proximity; admin enable; predictive load.

**Protections:**

1. Capacity pre-scale meetings + SPO.  
2. Fair-share RPS per tenant / per user.  
3. Disable noncritical background (deep Insights training jobs).  
4. Optional Copilot lockdown during exam windows (anti-cheat + load).  
5. Assignment submit path priority queues.  
6. Announcement of degraded UX (ja-JP banner).  
7. Read-through CDN for popular material.  
8. Meeting overflow: suggest Live Event for >N attendees.  
9. Freeze risky schema deploys.  
10. War room runbooks + status page.

### 5.10 Assignments consistency

```text
Submission unique (assignment_id, student_id, attempt_no)
Late submit: policy allow/deny/penalize
Grade release: instructor action → student visibility
Files permissions: student private submission folder; instructor read
```

Virus scan on upload; block executables per policy.

### 5.11 Meetings for lectures

- Threshold advisor: if roster > 300, recommend webinar/live.  
- Lobby for external.  
- Attendance reports privacy-scoped.  
- Recording consent + retention.  
- Dial-in less common but keep.  
- Exam oral defenses: breakout + recording policy special-case.

### 5.12 Notifications

Class announcement → push to members with quiet hours.  
Assignment due soon digests (JST batches).  
Avoid notifying on every file save.  
Exam mode: raise priority for schedule changes; suppress gamification.

### 5.13 Copilot / AI boundaries (Microsoft theme)

If interviewer asks Copilot:

- Ground only on class content student is authorized to see.  
- Tenant admin opt-in; data residency for prompts/logs.  
- Exam lockdown: disable generative assist on assignment pages if policy.  
- No training on tenant customer content without contractual posture.  
- Audit Copilot accesses in edu contexts.

### 5.14 Security

- Hard `tenant_id` filters; automated cross-tenant tests.  
- Graph app permissions least privilege for SIS bot.  
- Student cannot read others’ submissions (IDOR tests).  
- Antimalware on uploads.  
- Guest access time-boxed.  
- Conditional Access / MFA for instructors/admins.  
- Keys in Key Vault; secrets never in SIS sync configs plaintext.

### 5.15 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Shared global classroom DB | Cross-uni leakage SEV |
| UTC displayed as local without TZ | Mass wrong due dates |
| Recordings default on | Privacy + cost + APPI risk |
| No peak plan | Exam week outage PR crisis |
| Copilot without ACL grounding | Data leak |
| Offline graded submit without sync rules | Lost/duplicated grades |
| Ignoring SPO throttles | Submit failures |
| Building new chat instead of Teams | Wasted interview + compliance gap |

### 5.16 Consistency matrix

| Data | Model |
|------|-------|
| Enrollment | SIS → eventual projection + reconcile |
| Assignment metadata | Strong |
| Submission files | SPO durability + metadata strong |
| Channel messages | Teams guarantees |
| Insights | Eventual aggregates |
| Policies | Strong admin reads |

### 5.17 Multi-region / DR

- Primary: Japan regions (e.g. Japan East/West pairing patterns).  
- Failover playbooks for education tenants.  
- RPO/RTO communicated to university IT.  
- Avoid “failover to US” silently for edu content.

### 5.18 Observability

Per-tenant SLIs: submit success, join success, roster sync lag, SPO 429 rates, notify latency, cross-tenant authz failures (should be ~0). Avoid high-cardinality student_id metrics. Exam-season dashboards.

### 5.19 Accessibility & devices

Students on mixed Android/iOS/PC in JP; low bandwidth transit scenarios—mobile BFF compresses thumbnails; offline read cache for syllabi. WCAG + JP a11y practices.

### 5.20 Semester lifecycle

```text
TermStart → provision teams → roster fill → teach → exam mode → grade → archive teams
Archive: read-only; retention keeps; next term new teams (or reuse patterns)
```

---

## 6. Wrap-Up

### 6.1 Designed

Teams Education feature pack for Japanese universities: Entra identity, SIS rostering, Class Team templates, assignments/files/meetings reuse, ja-JP/JST locale, Japan compliance/residency policy pack, exam-season peak controller, optional Copilot boundaries—multi-tenant isolated on Azure Japan cells.

### 6.2 Decisions to defend

1. Reuse Teams/SPO/Meetings planes  
2. Hard tenant isolation + Japan residency  
3. SIS as enrollment authority  
4. UTC storage / JST UX  
5. Safe defaults (sharing/recording)  
6. Exam-season degrade order  
7. Idempotent submissions  
8. Policy packs versioned  
9. Copilot ACL grounding / lockdown  
10. Fair-share noisy neighbor controls  

### 6.3 Risks

- Graph/SPO throttling under peaks  
- SIS data quality  
- Meeting stampedes Mondays  
- Privacy perception of Insights/AI  
- Locale defects around deadlines  
- Operational coordination with university IT  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Feature pack vs rebuild Teams; Japan edu scope |
| 5–12 | Tenancy, residency, APPI |
| 12–20 | Roster → Class Team → assignments |
| 20–28 | Locale/JST; files/meetings reuse |
| 28–38 | Exam-season peak controller |
| 38–45 | Copilot boundaries, scale, closer |

### 6.5 Closer

> **Teams for Japanese university students:** build on Teams/M365 with education tenancy and Japan policy packs—hard isolation and residency, SIS-rostered Class Teams, JST-correct assignments, and an exam-season mode that protects submit/join while shedding noncritical AI/insights. Compliance and peak reliability are product features, not footnotes.

---

## 7. Deeper / Related Interview Questions

### 7.1 Scope & Microsoft reality

**Q: Do we redesign chat?**  
A: No—reuse Teams channel/chat. Focus on edu workflows + JP pack + peak.

**Q: Why not a separate student app ignoring Teams?**  
A: Identity, compliance, meetings, files already solved; interview expects platform leverage.

### 7.2 Tenancy

**Q: One tenant per university?**  
A: Typical yes. Multi-campus may be one tenant with groups; don’t merge unrelated unis.

**Q: How prevent cross-tenant leakage?**  
A: `tenant_id` on all rows; authz middleware; automated tests; separate SPO site collections; encryption/key postures as required.

### 7.3 Rostering

**Q: SIS outage during add/drop?**  
A: Serve last projection; queue sync; instructors manual override audited; reconcile later.

**Q: Student drops course after submitting?**  
A: Policy: retain submission under retention; revoke channel access.

### 7.4 Timezones

**Q: Why UTC storage?**  
A: Absolute instant; Japan currently no DST but still use TZ DB; overseas exchange students may view other TZs.

**Q: Due date bug class?**  
A: Storing local wall time without offset; fixing with `Asia/Tokyo` conversions everywhere.

### 7.5 Peak / exams

**Q: What do you shed first?**  
A: Insights compute, noncritical notify, Copilot, fancy previews—never audit, never authz, prefer keeping submit/join.

**Q: Noisy neighbor tenant?**  
A: Fair-share throttles; per-tenant quotas; meeting capacity reservations for large unis.

**Q: Deadline cliff mitigation?**  
A: Encourage early submit UX; staggered due times optional; autoscaled submit path; resumable upload; idempotency.

### 7.6 Compliance

**Q: What is APPI relevance?**  
A: Personal data protection obligations; minimize; secure processing; breach duties—pair with Microsoft Purview + contractual geo.

**Q: Recordings?**  
A: Default restricted; consent; retention; access logs; avoid auto public.

**Q: Parental access?**  
A: Rare in uni vs K-12; if minors present, separate guardian model—don’t expose full chat by default.

### 7.7 Assignments

**Q: Large file submit on mobile?**  
A: Chunked resumable upload; background transfer; commit submission when hash completes.

**Q: Plagiarism tools?**  
A: Optional connectors; data processing agreements; student notice.

**Q: Gradebook export?**  
A: SIS writeback connector; idempotent grade sync.

### 7.8 Meetings

**Q: 1000-student lecture?**  
A: Don’t use interactive meeting defaults blindly—Live Events / structured modes; Q&A channel sidechat.

**Q: Proctoring?**  
A: Sensitive; usually out of MVP; if asked, separate compliance-heavy system.

### 7.9 Copilot

**Q: Can Copilot summarize class chat for a student?**  
A: Only content in ACL scope; admin policy; citations; exam lockdown.

**Q: Prompt logs residency?**  
A: Must follow tenant commitments; discuss storage geography.

### 7.10 Scale jumps

**Q: 10×?** Multi-tenant Japan cell + packs. **100×?** National exam capacity program. **1000×?** Multi-country education packs.

### 7.11 Failure drills

**Q: Japan East impact?**  
A: Failover strategy to paired region if contractual; communicate; readonly materials mode if needed; prevent silent geo escape.

**Q: Graph 429 storms at semester start?**  
A: Token bucket provisioner; prioritize; exponential backoff; human-progress UI for IT.

### 7.12 Rapid-fire

| Q | A |
|---|---|
| Rebuild chat? | No |
| Tenant isolation? | Hard requirement |
| Residency? | Japan default |
| Due date TZ? | UTC store / JST UI |
| Recordings default? | Off/restricted |
| SIS truth? | Enrollment yes |
| Peak shed first? | Insights/Copilot |
| Submit idempotent? | Yes |
| External sharing? | Default deny |
| Live lecture scale? | Webinar/live mode |
| Quiet hours? | Default student pushes |
| APPI? | Name early |
| Cross-uni DB? | Never |
| Offline grade submit? | Avoid / careful |
| Policy pack? | Versioned config |
| Audit in peak? | Always on |
| Guest lecturer? | Time-boxed guest |
| Archive term? | Read-only retention |
| Metrics cardinality? | Careful |
| Ownership? | Edu feature + Teams SRE |

### 7.13 Interviewer traps

- Designing greenfield chat/video ignoring Teams.  
- No tenant_id story.  
- Storing JP due dates wrong.  
- No exam-season plan.  
- Enabling Copilot on all tenant data casually.  
- Recordings everywhere.  
- Single global DB “for simplicity.”  
- Ignoring SPO throttling.  
- Treating Insights as free to log all student messages forever.  
- Forgetting ja-JP as requirement.  
- No SIS reconcile.  
- Meeting for 2000 students without mode change.  
- Silent US failover for edu data.  
- OFFSET paging for submissions.  
- Feature flag without audit.

---

## 8. Appendices

### Appendix A — Example schemas (Assignments feature store)

```sql
CREATE TABLE assignments (
  tenant_id UUID NOT NULL,
  assignment_id UUID NOT NULL,
  team_id UUID NOT NULL,
  title TEXT NOT NULL,
  due_at TIMESTAMPTZ NOT NULL,
  late_policy TEXT NOT NULL,
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (tenant_id, assignment_id)
);

CREATE TABLE submissions (
  tenant_id UUID NOT NULL,
  assignment_id UUID NOT NULL,
  student_id UUID NOT NULL,
  attempt INT NOT NULL,
  drive_item_id TEXT NOT NULL,
  submitted_at TIMESTAMPTZ NOT NULL,
  client_submit_id UUID NOT NULL,
  state TEXT NOT NULL, -- submitted|returned|excused
  PRIMARY KEY (tenant_id, assignment_id, student_id, attempt),
  UNIQUE (tenant_id, client_submit_id)
);

CREATE TABLE roster_memberships (
  tenant_id UUID NOT NULL,
  course_id TEXT NOT NULL,
  user_id UUID NOT NULL,
  role TEXT NOT NULL, -- student|instructor|ta
  source_version BIGINT NOT NULL,
  PRIMARY KEY (tenant_id, course_id, user_id)
);

CREATE TABLE peak_modes (
  tenant_id UUID NOT NULL,
  mode TEXT NOT NULL,
  enabled_at TIMESTAMPTZ NOT NULL,
  config JSONB NOT NULL,
  PRIMARY KEY (tenant_id, mode)
);
```

### Appendix B — SIS sync pseudocode

```python
def apply_sis_delta(tenant_id, delta):
    for enroll in delta.enrolls:
        upsert_membership(tenant_id, enroll.course_id, enroll.user_id, enroll.role, delta.version)
        ensure_team_membership(tenant_id, enroll.course_id, enroll.user_id)
    for drop in delta.drops:
        schedule_drop(tenant_id, drop, grace=tenant_policy.grace)
    reconcile_if_needed(tenant_id, delta.snapshot_marker)
```

### Appendix C — Japan policy pack (defaults)

| Setting | Default |
|---------|---------|
| External sharing | Off / existing guests only |
| Recording | Restricted / consent required |
| Retention class materials | Term + N years (uni choice) |
| Student posting in Announcements | Off |
| Guest expiry | 30–90 days |
| Copilot | Admin opt-in |
| Data region | Japan |
| Quiet hours pushes | 21:00–08:00 JST |
| DLP exam content | High sensitivity labels |

### Appendix D — Exam-season checklist

- [ ] Capacity reserved (meetings/SPO)  
- [ ] Peak mode flag ready  
- [ ] Deploy freeze window  
- [ ] Fair-share throttles validated  
- [ ] Status banner ja-JP strings  
- [ ] Copilot lockdown optional  
- [ ] Oncall / war room staffing  
- [ ] Known large lectures converted to live mode  
- [ ] Assignment submit load test replay  
- [ ] Rollback plan  

### Appendix E — SLIs / SLOs

| SLI | SLO example |
|-----|-------------|
| Assignment submit success | 99.5% exam week |
| Meeting join success | per Teams + edu overlay targets |
| Roster sync lag | < 15 min p95 normal; < 2 h semester start |
| Cross-tenant authz fail | ~0 true leaks |
| Locale deadline incidents | 0 SEVs |

### Appendix F — Kill switches

- Peak mode enable  
- Disable Copilot edu  
- Disable Insights  
- Disable noncritical bots  
- Force read-only materials (emergency)  
- Pause new team provisioning  
- Block external guests globally in tenant  

### Appendix G — Narrative beats

1. Frame as Teams Education feature pack for JP unis.  
2. Tenancy + APPI/residency.  
3. SIS → roster → Class Team.  
4. Assignments + SPO + JST.  
5. Meetings scale modes.  
6. Exam-season controller.  
7. Copilot boundaries.  
8. Closer.

### Appendix H — Pre-onsite checklist

- [ ] Reuse vs rebuild stance  
- [ ] Tenant isolation  
- [ ] Japan policy pack  
- [ ] JST due date story  
- [ ] SIS reconcile  
- [ ] Exam shed order  
- [ ] Meeting threshold  
- [ ] Copilot ACL  
- [ ] Progressive scale  
- [ ] 60s closer  

### Appendix I — Extra drills

1. Draw ecosystem diagram.  
2. Due date UTC↔JST conversion example.  
3. Deadline cliff math.  
4. Peak shed order list.  
5. IDOR test cases for submissions.  
6. SIS drop grace policy.  
7. Live event threshold rationale.  
8. Quiet hours design.  
9. Purview retention mapping.  
10. Graph 429 backoff.  
11. Archive term flow.  
12. Guest lecturer path.  
13. Copilot exam lockdown.  
14. Fair-share throttle.  
15. Japan East DR narrative.  
16. Furigana/name display note.  
17. Mobile resumable upload.  
18. Insights privacy aggregates.  
19. Policy pack versioning.  
20. 60s closer.

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| Entra ID | Microsoft identity platform (Azure AD) |
| Class Team | Team template for a course |
| SIS | Student Information System |
| APPI | Japan Act on Protection of Personal Information |
| Purview | Microsoft compliance suite |
| SPO | SharePoint Online |
| Graph | Microsoft Graph API |
| Peak mode | Exam-season reliability configuration |
| OneRoster | Common rostering standard |
| Live Event | Large-scale broadcast-style meeting mode |

### Appendix K — Role/permission matrix (simplified)

| Action | Student | TA | Instructor | Admin |
|--------|---------|----|------------|-------|
| Read materials | Y | Y | Y | Y |
| Post in Q&A | Y | Y | Y | Y |
| Post announcements | N | opt | Y | Y |
| Create assignment | N | opt | Y | Y |
| Submit | Y | N | N | N |
| Grade | N | Y | Y | Y |
| Apply policy pack | N | N | N | Y |
| Enable peak mode | N | N | N | Y (+ops) |

### Appendix L — Event types

`RosterEnrolled`, `RosterDropped`, `TeamProvisioned`, `AssignmentCreated`, `SubmissionReceived`, `GradeReleased`, `PeakModeEnabled`, `PolicyPackApplied`, `MeetingLargeLectureRecommended`, `GuestExpired`.

### Appendix M — Security checklist

- [ ] Cross-tenant tests  
- [ ] Submission IDOR tests  
- [ ] App-only SIS permissions least privilege  
- [ ] Malware scanning  
- [ ] Guest expiry jobs  
- [ ] Key Vault secrets  
- [ ] Admin MFA / CA  
- [ ] Audit immutability  

### Appendix N — Comparison

| Approach | When |
|----------|------|
| Teams Education pack | Default Microsoft answer |
| Standalone LMS | If interviewer forces greenfield—still reuse identity/meetings if possible |
| Moodle-like self-host | Different compliance ops; not typical Teams interview |

### Appendix O — 60s closer

> We ship this as a Teams Education feature pack for Japanese universities, not a new chat stack. Entra tenants stay isolated in Japan-region cells with APPI-aware policy packs—external sharing and recordings restricted by default. SIS remains enrollment truth projected into Class Teams. Assignments store UTC instants and render in JST so 期末 deadlines don’t drift. At exam season, a peak controller pre-scales and fair-shares, protecting submit and meeting join while shedding Insights and Copilot. Copilot, if enabled, is ACL-grounded and optionally locked down during exams.

### Appendix P — Common mistakes

1. Rebuilding Teams chat/video.  
2. No residency story.  
3. Naive local-time storage.  
4. No exam plan.  
5. Copilot overreach.  
6. Recordings default on.  
7. Shared multi-uni tables without isolation.  
8. Ignoring Graph/SPO throttles.  
9. Insights that feel like surveillance.  
10. Forgetting ja-JP quiet hours.

### Appendix Q — Academic calendar hooks

```text
学期開始 term_start
履修登録 course_reg_window
授業期間 teaching
試験期間 exam_window  ← peak mode
成績確定 grading
学期終了 archive
```

### Appendix R — Ownership (SEV)

| Symptom | Primary |
|---------|---------|
| Can’t submit assignment | Assignments + SPO |
| Can’t join lecture | Meetings |
| Wrong roster | SIS connector / Roster |
| Cross-tenant incident | Security + platform |
| Locale deadline SEV | Assignments + Locale |
| Peak brownout | Peak controller + SRE |

### Appendix S — Stretch: national entrance exam content

Different product; higher stakes; usually isolated assessment systems—don’t mix casually with collaborative class chat.

### Appendix T — Sibling prompts

Chat/messaging system; Azure regional failover; notification system; presence API; Microsoft health app (compliance cousin); Key Vault (secrets cousin).

---

*End of Teams university Japan system design prep doc.*
