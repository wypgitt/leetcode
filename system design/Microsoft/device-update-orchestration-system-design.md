# System Design: Device Update Orchestration (Fleet / Campaign Control Plane)

> **Focus areas:** Update campaigns · Deployment rings · Compliance policies · Staged rollout · Health signals · Halt / rollback campaigns · Fleet targeting · Audit · Multi-tenant device clouds  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Distinct from **OTA binary delivery** (CDN/chunk/A/B partitions on device); this doc owns the **orchestration control plane**—who gets what when, gates, compliance, rollback *campaigns*  
> **Interview theme:** Microsoft — Intune / Windows Update for Business / IoT Update–shaped fleet orchestration

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

Goal: **bound the product**—a **fleet update orchestration** system that creates **campaigns** to move device populations across software versions using **rings** (canary → early → broad), **compliance policies** (deadlines, grace, freeze windows), health-based **halt**, and **rollback campaigns**—while deferring raw package delivery mechanics to an OTA/delivery plane.

### 1.0 What this is / is not

| Dimension | This doc (orchestration) | Not this (OTA delivery) |
|-----------|--------------------------|-------------------------|
| Job | Who/when/policy/rollback decisions | How bytes get to flash |
| Artifacts | Version pointers, manifests, signatures refs | Chunking, delta encoding, A/B slot IO |
| Scale stress | Targeting queries, scheduling, state fan-in | CDN Tbps, resume downloads |
| Rings | First-class progressive exposure | Optional client-side |
| Compliance | Deadline, grace, admin freeze, audit | Mostly client scheduler |
| Rollback | Campaign to previous good version | Device dual-partition swap detail |
| Microsoft lens | Intune / WUfB / Autopatch-like | Pure device agent firmware blog |

**Scope statement:**

> Design a multi-tenant device-update **orchestration control plane**: inventory + grouping, campaign definition, ring-based rollout, compliance deadlines, health-gated progression, halt/rollback campaigns, and reporting—assuming an existing OTA delivery subsystem for package bytes—scaled from 1M to billions of devices via progressive 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Device types? | PCs, phones, IoT, maybe vehicles (policy similar) | Device twin / inventory abstract |
| F2 | What is an update? | Versioned release channel artifact (OS/app/fw) | Release catalog |
| F3 | Targeting? | Groups, tags, queries (OS, sku, region) | Audience service |
| F4 | Rings? | % or cohort rings with bake time | Rollout state machine |
| F5 | Compliance? | Require version by deadline; grace; digests | Compliance engine |
| F6 | User deferral? | Limited snooze within policy | Client + policy |
| F7 | Maintenance windows? | Timezone-aware windows | Scheduler |
| F8 | Health gates? | Crash rate, success %, signal thresholds | Telemetry aggregation |
| F9 | Halt? | Auto + manual stop progression | Kill switch |
| F10 | Rollback? | Campaign to last-known-good | Separate campaign type |
| F11 | Exclusions? | VIP freeze, legal hold devices | Overrides |
| F12 | Auth? | Entra tenant admin; RBAC | Audit all actions |
| F13 | Reporting? | Funnel: offered→downloading→installed→healthy | Analytics |
| F14 | Delivery? | Call OTA plane APIs | Interface boundary |

**MVP functional scope:**

1. Device inventory registration + tags/groups.  
2. Release catalog entry (version, artifact URI ref, signature metadata).  
3. Create **campaign**: target audience, rings, bake times, deadlines.  
4. Assign devices to ring exposures progressively.  
5. Emit **update directives** to devices (or to delivery plane).  
6. Ingest status: offered, downloading, installing, succeeded, failed, rolled back.  
7. Health gate: if failure rate > threshold → **halt**.  
8. Admin **rollback campaign** to previous version for exposed rings.  
9. Compliance report: % in-version by deadline.  
10. Full audit of policy/campaign changes.

**Out of MVP:**

- Implementing CDN delta patch generation  
- On-device A/B slot firmware algorithms  
- ML predictive scheduling (Phase 2)  
- Active-active dual writers for same campaign state  
- Perfect offline device guarantee of deadline (best-effort when check-in)

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Control-plane availability | 99.9%+ |
| N2 | Directive freshness | Devices see assignments within minutes of exposure (online) |
| N3 | Status ingest durability | No silent loss of terminal states |
| N4 | Halt latency | p99 < 1–5 minutes from threshold breach to stop new exposures |
| N5 | Targeting query | Complex audiences without full scans every second |
| N6 | Consistency | Strong campaign config; eventual device status |
| N7 | Audit | Immutable admin actions |
| N8 | Multi-tenant isolation | Strict |
| N9 | Scale | Progressive table |
| N10 | Safety | Prefer halt on uncertainty for broad rings |

### 1.3 Cases

**Happy paths**

1. Admin creates campaign v42 → Ring0 1% → bake 24h healthy → Ring1 10% → … → RingN 100%.  
2. Device checks in → receives directive → OTA downloads → reports success → compliance green.  
3. Failure spike in Ring1 → auto-halt → admin investigates → rollback campaign for Ring1.  
4. Compliance deadline approaches → deferrals disabled → forced install window.  
5. Freeze window (holidays) → no new exposures; in-flight may finish per policy.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Device offline past deadline | Non-compliant until check-in; report separately |
| Flapping health signals | Hysteresis; min sample size before halt |
| Dual campaigns conflict | Precedence policy (higher priority / newer / channel) |
| Partial ring exposure then halt | Do not auto-widen; optional rollback |
| Wrong artifact signed | Validate signatures in catalog; halt if verify fails fleet-wide |
| Admin error broad expose | Blast-radius limits; two-person approval for RingN |
| Clock skew windows | Use device local TZ policy + server bounds |
| Status duplicates | Idempotent status by `(device_id, campaign_id, version, state)` |
| Tenant noisy telemetry | Quotas on status QPS |
| Rollback of rollback | Explicit new campaign; version graph |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants | 5K | 50K | 500K | 5M |
| Devices | 10M | 100M | 1B | 10B |
| Active campaigns | 50K | 500K | 5M | 50M |
| Rings per campaign | 4 | 4–6 | 4–8 | 4–8 |
| Status events / day | 100M | 1B | 10B | 100B |
| Peak status QPS | 5K | 50K | 500K | 5M |
| Targeting recompute / hour | 100K device-evals | 1M | 10M | 100M |
| Admin API QPS | 100 | 1K | 10K | 100K |
| Halt evaluations / min | 1K | 10K | 100K | 1M |

**What each jump forces:**

- **10×:** Audience materialization; status event bus; campaign state machine service.  
- **100×:** Shard by tenant/device; precomputed ring membership; health aggregators per campaign.  
- **1,000×:** Hierarchical orchestration (global policy → regional executors); sampled health; cell isolation.

### 1.5 Etc.

- **Delivery plane interface:** `CreateOffer(device, version, artifact_ref)` / device pull of directive.  
- Devices run agents (Windows Update / Intune / IoT) that honor maintenance windows.  
- Security: signed catalog entries; admin RBAC; just-in-time elevation for broad rings.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Status fan-in

```text
Baseline: 10M devices × ~10 status events/update × 1 update/month
≈ 100M events/month if sparse; table uses busier 100M/day enterprise churn—be explicit in interview.
Peak when campaign broadens: 10% of 10M = 1M devices enter downloading in an hour
→ ~280/s just for that transition; spikes higher with chatter
Design for bursty fan-in, not only daily averages.
```

### 2.2 Targeting cost

```text
Naïve: each campaign scans all devices every minute → impossible at 1B
Must: indexed attributes + materialized group membership + incremental eval
```

### 2.3 Health aggregation

```text
Per campaign ring: success, fail, crash signals in sliding window
Aggregate via stream processors keyed by (campaign_id, ring_id)
Sample at 1000× if needed for ultra-broad rings (with care)
```

### 2.4 Storage

```text
Device twin ~1–2 KB → 10M × 2 KB = 20 GB; 10B × 2 KB = 20 TB
Campaign assignment row ~100 B × devices exposed
Status history: retain hot 30–90d; cold archive
```

### 2.5 Critical bottlenecks

1. **Targeting / membership recompute**  
2. **Status ingest storms** on ring expansion  
3. **Health false positives** halting good rollouts  
4. **Conflicting policies**  
5. **Admin blast radius**  
6. **Report queries** over huge fleets  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Tenant
Device (id, attributes, last_checkin, current_versions{})
Group / Tag / DynamicQuery
Release (product, version, artifact_ref, signature, channel)
Campaign (release, audience, rings[], gates[], compliance, priority)
RingExposure (campaign, ring, % or cohort, start, bake_until, state)
DeviceAssignment (device, campaign, ring, desired_version, state)
HealthWindow / HaltDecision
RollbackCampaign (source_campaign, target_version, audience)
CompliancePolicy (deadline, grace, freeze_windows)
```

### 3.2 Options: assignment model

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Device pulls policy document | Simple offline | Slow halt | Fast halt required |
| B. Push assignments | Fast | Presence dependent | Huge offline fleets |
| C. Hybrid: versioned policy + pull + push invalidate | Best | Complexity | — |

**Chosen:** **Hybrid**—devices periodically pull **policy generation**; orchestrator bumps generation on halt/expose; optional push notify for online agents.

### 3.3 Campaign state machine

```text
DRAFT → SCHEDULED → RUNNING → (PAUSED|HALTED) → COMPLETED
                         ↘ FAILED / CANCELLED
RollbackCampaign is a first-class campaign with type=ROLLBACK
```

### 3.4 Ring progression

```text
Ring i RUNNING exposure
  wait bake_time AND health_ok AND min_sample
  → expand Ring i+1
if health_fail → HALT (no further expand); alert
admin may ROLLBACK exposed rings
```

**Invariant:** Automation never skips gates for broad rings without explicit override + audit.

### 3.5 Compliance vs campaign

| Concept | Role |
|---------|------|
| Campaign | How version rolls out (rings) |
| Compliance policy | Must be on version by deadline (ongoing) |
| Freeze | No disruptive updates in window |

A device can be **campaign-assigned** and separately **non-compliant** if past deadline.

### 3.6 Health gates

```text
metrics: install_success_rate, rollback_rate, crash_rate_delta, perf_regressions
inputs: status events + optional telemetry partner
rules: require n>=N and rate < T for bake success
halt if rate > T_halt with hysteresis
```

### 3.7 Rollback campaigns

```text
Not "instant magical undo"—create campaign desired_version = previous_good
Target: devices that moved to bad version (query assignment history)
Rings for rollback may be faster; still health-gated
Delivery plane performs downgrade if supported; else block + ticket
```

### 3.8 Precedence / conflicts

```text
Evaluate applicable campaigns/policies:
  1) emergency security campaign (pinned)
  2) explicit device override
  3) higher priority campaign
  4) channel affinity (prod/beta)
  5) default compliance
Deterministic winner; record reason on device twin
```

### 3.9 Boundary to OTA delivery

```text
Orchestrator outputs DesiredState {version, artifact_ref, deadline, window}
Delivery plane: download, verify, apply, reboot strategy
Orchestrator consumes Result {success, error_code, measurements}
```

**Deal-breaker:** Re-implementing package chunking inside orchestration interview without being asked.

### 3.10 Microsoft mapping

| Concept | Analog |
|---------|--------|
| Rings | WUfB deployment rings / Autopatch |
| Compliance | Intune compliance |
| Campaigns | Update policies / deployments |
| Halt | Autopatch pause / known issue rollback |
| Inventory | Entra + Intune device records |

---

## 4. Architecture Diagram

### 4.1 Control plane overview

```text
Admin UI/API (Entra RBAC)
        │
        ▼
┌─────────────────── Orchestration Control Plane ───────────────────┐
│ Catalog │ Audience/Targeting │ Campaign Mgr │ Compliance │ Halt   │
└───────────────┬───────────────────────┬───────────────────────────┘
                │                       │
                ▼                       ▼
        Assignment Store         Health Aggregators
                │                       │
                ▼                       ▼
        Policy Documents ◄────── Halt/Expand Decisions
                │
                ▼
        Device Check-in / Notify ──► Agents
                │
                ▼
        Status Events Bus ──► Assignment updates + Health + Reports
                │
                ▼
        OTA Delivery Plane (external) ← artifact_ref only
```

### 4.2 Ring expand sequence

```text
Campaign Runner:
  if ring.bake_elapsed and health.ok(ring):
     compute next cohort membership
     write assignments (desired_version)
     bump policy_generation
     emit metrics
```

### 4.3 Halt sequence

```text
Health Agg detects fail_rate > T (n>=N)
  → HaltService CAS campaign.state RUNNING→HALTED
  → stop expander
  → bump policy_generation (devices stop new offers if policy says)
  → page on-call / admin
  → optional auto-create rollback draft
```

### 4.4 Device check-in

```text
Device → GET /policy?gen=local
  if gen stale → return DesiredState + windows + deadline
Device applies via OTA → POST /status
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Halt correctness

**Invariant:** Once HALTED, expander must not expose new devices without explicit resume. Implement via monotonic `campaign_epoch` checked on every expand TX.

#### 5.1.2 Status idempotency

```text
UPSERT status where (device_id, campaign_id, version, from_state→to_state) with event_id dedupe
Terminal states sticky unless rollback campaign
```

#### 5.1.3 Split brain expander

Only one leader runner per campaign shard (lease). Follower expands forbidden by lease/epoch.

#### 5.1.4 Failure modes

| Failure | Degradation |
|---------|-------------|
| Health agg lag | Hold ring expansion (fail-safe) if bake ends without fresh health |
| Status bus delay | Assignments still pull-based; reports lag |
| Targeting DB down | No new expands; existing policy gens still served from cache |
| OTA plane down | Assignments queue; devices fail download—health may halt |

#### 5.1.5 Safety defaults

Broad ring expansion requires: min bake, min sample, two-person approve optional, max % step (e.g. ≤25% jump).

### 5.2 Scalability

#### 5.2.1 Sharding

| Data | Key |
|------|-----|
| Devices | `tenant_id + device_id` |
| Campaigns | `tenant_id + campaign_id` |
| Assignments | `campaign_id` or `device_id` (pick; often device for check-in locality) |
| Health | `campaign_id + ring_id` |

Check-in path must be hot-cache friendly: policy blob per device or per group with overrides.

#### 5.2.2 Audience materialization

```text
Dynamic group query → incremental index on attributes
Campaign audience = group ∩ ring_cohort ∩ not(exclusions)
Precompute membership lists for active rings; delta on device attribute change
```

#### 5.2.3 Progressive scale

| Scale | Must have |
|-------|-----------|
| 1× | Campaigns, rings, status, manual halt |
| 10× | Auto health halt, materialized groups |
| 100× | Sharded runners, event bus, reporting store |
| 1000× | Hierarchical cells, sampled health, policy CDN |

### 5.3 Maintainability

- Separate **policy compiler** (desired state) from **delivery**.  
- Versioned gate schemas.  
- Simulation mode: “what % would be hit” dry-run.  
- Strong admin UX for funnels.

### 5.4 Security & compliance

- RBAC: read-only analyst vs campaign operator vs emergency approver.  
- Dual control for >X% exposure.  
- Signed releases only.  
- Audit: who expanded/halted/rolled back.  
- Tenant isolation on all queries.  
- Regulatory: some devices cannot update (medical freeze tags).

### 5.5 Scheduling & windows

```text
maintenance_window: cron-like + TZ
busy season freeze calendars at tenant level
deadline enforcement: after grace, ignore snooze
battery / metered network constraints → agent side with policy flags
```

### 5.6 Reporting

Funnel warehouse:

```text
offered → download_started → download_finished → install_started → reboot → success/fail
slice by ring, model, geo, OS build
```

Near-real-time for health; batch for executive compliance %.

### 5.7 Emergency / out-of-band

Security patch channel with **fast rings** (minutes bake) but still haltable; separate quota for emergency vs feature updates.

---

## 6. Wrap-Up

### 6.1 What we designed

A **fleet update orchestration control plane** centered on **campaigns, rings, compliance, health-gated halt, and rollback campaigns**, integrating with—but not reimplementing—an OTA delivery plane. Devices converge via versioned policies; status fan-in drives gates and reports.

### 6.2 Key invariants

1. Expand only if health gates pass (fail-safe).  
2. Halt epoch fencing prevents late expands.  
3. Rollback is an explicit campaign, not silent mutate.  
4. Orchestration ≠ byte delivery.  
5. Admin actions audited; broad rings controlled blast radius.

### 6.3 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| Push vs pull policy | Hybrid | Offline + fast halt |
| Auto vs manual expand | Auto with gates | Scale + safety |
| Rollback speed | Faster rings still gated | Safety |
| Health sampling | Full then sample at extreme | Cost |
| Scope vs OTA | Hard boundary | Interview clarity |

### 6.4 60-second pitch

> We manage desired versions with ring-based campaigns and compliance deadlines. Devices pull versioned policies; an OTA plane delivers bytes. Status events feed health aggregators that auto-halt bad rollouts; rollbacks are explicit campaigns to last-known-good. Targeting uses materialized audiences, not fleet scans. At scale we shard runners and assignments, fail-safe on missing health, and tightly RBAC/audit broad exposures—Intune/WUfB-shaped, not a CDN design.

### 6.5 Risks / follow-ups

- Cross-product dependency graphs (update A before B)  
- User experience messaging  
- Predictive bake times  
- Unified app + OS orchestration  

---

## 7. Deeper / Related Interview Questions

### 7.1 Rings & gates

**Q: Percentage vs static canary group?**  
A: Both—fixed dogfood group as Ring0; percentage thereafter. Fixed group catches lab issues; % catches diversity.

**Q: What if bake time passes but sample size tiny?**  
A: Do not expand; wait for N or timeout to admin.

**Q: Can rings overlap devices?**  
A: No—exclusive membership; device in highest exposed eligible ring.

### 7.2 Halt & rollback

**Q: Halt vs rollback?**  
A: Halt stops widening; rollback actively moves exposed devices backward.

**Q: Auto-rollback?**  
A: Optional for Ring0/1; require approval for broad—product policy.

**Q: Halt latency SLO?**  
A: Minutes; policy generation bump + push invalidate for online.

### 7.3 Compliance

**Q: Campaign vs compliance?**  
A: Campaign is rollout mechanics; compliance is continuous posture by deadline.

**Q: Offline devices?**  
A: Show last_checkin; non-compliant when seen; cannot force magic while offline.

### 7.4 Conflicts

**Q: Two campaigns desire different versions?**  
A: Deterministic precedence; surface to admin; device twin records winner reason.

**Q: User deferral vs deadline?**  
A: Defer allowed until grace ends; then force on window.

### 7.5 vs OTA design

**Q: Where do deltas live?**  
A: Delivery plane. Orchestrator stores artifact refs + hashes.

**Q: A/B partition failure on device?**  
A: Device reports failure code; orchestrator health counts it; may rollback campaign.

### 7.6 Scale

**Q: 1B devices targeting?**  
A: Attribute indexes, materialized groups, incremental eval, avoid global scans.

**Q: Status 5M QPS?**  
A: Event hubs, shard aggregators, downsample heartbeats vs terminal events.

### 7.7 Safety / process

**Q: Prevent admin mistakes?**  
A: Dry-run, max step %, dual approval, simulators, change windows.

**Q: Friday broad expose?**  
A: Policy: disallow RingN expand before weekends/freezes.

### 7.8 Microsoft-specific

**Q: Intune vs Windows Update?**  
A: Intune policies/compliance + WU agent delivery; your design sits as cloud orchestrator.

**Q: Autopatch?**  
A: Managed rings + halt/rollback automation—cite as product shape.

### 7.9 Reliability drills

1. Expander leader kill → lease takeover; no double expand (epoch).  
2. Health false spike → hysteresis prevents flap; runbook.  
3. Status replay → idempotent.  
4. Halt during expand TX → CAS state wins; partial cohort OK if recorded.  

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| Design only CDN chunking | Wrong focus for this prompt |
| Instant 100% rollout | No rings/gates |
| Silent auto-downgrade all fleet | Need campaign + support matrix |
| Scan all devices every second | Won’t scale |
| Ignore offline compliance | Dishonest reporting |

### 7.11 Algorithms

**Q: Cohort selection?**  
A: Stable hash(`device_id, campaign_salt`) < threshold for % rings—sticky as % grows.

**Q: Health rate?**  
A: Bayesian or Wilson interval lower bound before expand—mention sophistication optionally.

### 7.12 Multi-region

**Q: Regional rings?**  
A: Audience filter by geo; or regional campaigns; health localized to avoid one bad region blocking all.

### 7.13 Data model puzzles

**Q: Store per-device desired state always?**  
A: For overrides yes; else compute from group policy + ring threshold to save storage—hybrid.

### 7.14 Comparison

**Q: vs feature flags?**  
A: Similar progressive exposure; updates are heavier, reversible differently, compliance deadlines matter more.

**Q: vs job scheduler?**  
A: Scheduler runs tasks; orchestrator manages fleet desired versions + gates.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- devices(device_id, tenant_id, attrs_json, last_checkin, policy_gen_ack)
-- groups(group_id, tenant_id, query_json)
-- group_members(group_id, device_id) -- materialized
-- releases(release_id, product, version, artifact_ref, sig, channel)
-- campaigns(campaign_id, tenant_id, release_id, type, state, priority, epoch, config_json)
-- rings(campaign_id, ring_id, ordinal, target_pct, bake_seconds, state)
-- assignments(device_id, campaign_id, ring_id, desired_version, state, updated_at)
-- status_events(event_id, device_id, campaign_id, version, state, ts, error_code)
-- health_agg(campaign_id, ring_id, window_start, success, fail, crash)
-- compliance_policies(policy_id, tenant_id, product, min_version, deadline, grace)
-- audit(event_id, actor, action, entity, ts, details)
```

### 8.2 API checklist

- [ ] CRUD releases / campaigns / rings  
- [ ] Start / pause / resume / halt  
- [ ] Create rollback campaign  
- [ ] Device: get policy, post status  
- [ ] Compliance reports  
- [ ] Dry-run targeting  
- [ ] Audit query  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Ring | Progressive exposure cohort |
| Bake time | Wait + observe health before widen |
| Halt | Stop expansion (and possibly offers) |
| Rollback campaign | Explicit move to prior version |
| Compliance | Deadline-driven posture |
| Policy generation | Monotonic config version devices pull |
| Directive / desired state | What version device should seek |
| Delivery plane | OTA bytes path |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Campaigns, rings, status, manual halt |
| 10× | Auto health gates, groups, audit |
| 100× | Sharded runners, event bus, reporting |
| 1000× | Cells, sampled health, policy edge cache |

### 8.5 Ring example

| Ring | Cohort | Bake |
|------|--------|------|
| 0 | Dogfood group 1K | 48h |
| 1 | 1% | 24h |
| 2 | 10% | 24h |
| 3 | 50% | 24h |
| 4 | 100% | — |

### 8.6 Halt rules (example)

```text
halt if fail_rate > 2% with n >= 500 in 2h window
or crash_delta > 5% vs baseline
hysteresis: resume requires fail_rate < 0.5% for bake
```

### 8.7 Precedence example

```text
EmergencySec > DevicePin > CampaignPriority > ChannelDefault > ComplianceMin
```

### 8.8 Interview “say this” summary

> Orchestrate fleet desired versions with ring campaigns, compliance deadlines, health-gated halt, and explicit rollback campaigns—delivery bytes stay in the OTA plane; we own exposure, gates, and audit.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| % ring unstable membership | Use sticky hash |
| Expand on wall clock only | Need health + sample size |
| Store all status forever hot | Tier/archive |
| One global campaign runner | Shard by campaign |

### 8.10 Reliability test plan

1. Halt epoch fencing under dual runners.  
2. Status at-least-once replay.  
3. Offline device compliance reporting accuracy.  
4. Rollback targets only upgraded devices.  
5. Freeze window blocks expands.

### 8.11 Observability SLOs

| SLO | Target |
|-----|--------|
| Halt decision latency | < 5 min p99 |
| Policy freshness (online) | < 5 min |
| Status durability | ACK after durable |
| Incorrect auto-expand after halt | **0** |

### 8.12 Related systems map

```text
Admin → Campaign/Compliance → Assignments/Policy Gen → Device Agent
             ↑                         ↓
          Health Agg ← Status Bus ← OTA Results
             ↓
          Halt / Rollback / Reports
```

### 8.13 Distinct from OTA delivery doc

| Topic | Orchestration | OTA delivery |
|-------|---------------|--------------|
| Rings/compliance | Central | Peripheral |
| CDN/chunks/delta | Ref only | Central |
| A/B slots | Result codes | Mechanism |
| Fleet targeting | Central | Minimal |
| Rollback campaign | Central | Apply downgrade |

### 8.14 Policy document sketch

```json
{
  "policy_gen": 84521,
  "desired": [{"product":"os","version":"42.1","artifact_ref":"...", "deadline":"2026-09-01T00:00:00Z"}],
  "window":{"tz":"America/Los_Angeles","cron":"0 2 * * *"},
  "campaign_id":"c-123","ring":2
}
```

### 8.15 Status event sketch

```json
{"event_id":"e1","device_id":"d","campaign_id":"c","version":"42.1","state":"SUCCEEDED","ts":"..."}
```

### 8.16 Dry-run targeting

```text
POST /campaigns/{id}/dry-run → {ringCounts, sampleDevices, exclusions}
No assignments written
```

### 8.17 Capacity cheat-sheet

```text
expand_write_rate ≈ newly_exposed_devices / expand_interval
status_qps_peak ≈ exposed_devices × chatter_rate
health_keys ≈ active_campaigns × rings
```

### 8.18 Approval workflow

```text
Ring expand > 25% → require second admin approval
Emergency channel bypass with break-glass audit
```

### 8.19 Version graph

```text
releases form DAG: 41.0 → 42.0 → 42.1
rollback edges allowed only if delivery supports downgrade
else: remediation campaign (reimage / support)
```

### 8.20 Final deal-breakers

1. No health gate before broad expose  
2. Expand after halt without epoch check  
3. Mixing CDN chunk design as the core answer  
4. Silent fleetwide downgrade without campaign  
5. Targeting via repeated full fleet scans  

### 8.21 Extra depth — cohort stickiness math

```text
u = hash(device_id + campaign_salt) / 2^64   # uniform [0,1)
in_ring_pct(p) if u < p
As p grows from 0.01 → 0.10, previous members remain (sticky)
```

### 8.22 Fail-safe expand checklist

- [ ] campaign.state == RUNNING  
- [ ] epoch unchanged during TX  
- [ ] health window fresh < SLA  
- [ ] n_sample >= N  
- [ ] fail_rate <= T  
- [ ] freeze window not active  
- [ ] approval recorded if required  

### 8.23 Regional executor pattern (1000×)

```text
Global Campaign Manager: ring decisions, halt, audit
Regional Executors: materialize assignments for regional devices, serve policy
Status: regional ingest → global health rollup for gates (or regional gates)
```

### 8.24 Interaction with user deferral

```text
desired_version set → agent offers update
user snooze count < max → defer until window
compliance grace expired → snooze disabled → force install
```

### 8.25 Known-issue badges

```text
Catalog can mark release as known_issue → auto-halt campaigns on that release
Communicate to admins; suggest rollback targets
```

### 8.26 Multi-product campaigns

```text
Bundle: OS + agent versions with dependency order
Orchestrator stages desired states; delivery applies in order
Failure mid-bundle → halt + remediation playbook
```

### 8.27 Cost controls

- Sampled telemetry for health on ultra-broad rings  
- Terminal status events prioritized over heartbeats  
- Policy CDN caching identical group policies  

### 8.28 Threat model

| Threat | Mitigation |
|--------|------------|
| Malicious admin broad malware version | Dual control, signed catalog, channel protections |
| Compromised device false fail storm | Auth device identity; anomaly detection on status |
| Cross-tenant campaign read | Authz on every API |
| Artifact spoof | Signatures verified before catalog publish |

### 8.29 SLO dashboard (campaign)

| Panel | Meaning |
|-------|---------|
| Exposure % | How far rings progressed |
| Success funnel | Where drop-offs are |
| Halt history | Safety interventions |
| Compliance % | Deadline posture |
| Oldest non-checkin | Offline risk |

### 8.30 Say-vs-OTA reminder (interview closer)

> If interviewer drifts into delta encoding and dual-partition swap, acknowledge delivery plane briefly, then steer back: **rings, gates, compliance, halt, rollback campaigns, targeting scale**—that is the orchestration problem.

---

*End of device update orchestration system design.*
