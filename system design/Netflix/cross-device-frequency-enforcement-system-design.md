# System Design: Cross-Device Frequency Enforcement

> **Focus areas:** Household graph · Subject resolution · Most-restrictive union · Identity latency budget · Cross-region counter home · Cap subject federation · Graph staleness vs over-show  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct union semantics, split identity QPS from cap QPS, explicit deal-breakers, Netflix Ads 2025–26 interview themes  
> **Interview theme:** Netflix Ads — enforce frequency caps consistently when the same viewer watches on phone, TV, tablet, and travels across regions without blowing the ad-decision latency budget

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

Goal: **cross-device and cross-region frequency enforcement**—the identity and federation layer that answers “who is the cap subject?” and “what is the union of counts across linked subjects?” so frequency caps from sibling doc apply consistently when a viewer uses multiple devices, profiles, or regions.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Resolve cap subjects; federate counters across linked identities | Full frequency cap counter store (sibling: ad-frequency-capping) |
| Identity | Household graph, device links, profile hierarchy | Full Netflix account / billing identity product |
| Union | Most-restrictive merge of counts across subjects | Presentation order / pod sequencing (sibling) |
| Region | Subject home cell + cross-region read policy | CDN / creative delivery |
| Graph write path | Consume identity events; read at decision | Real-time graph ML inference |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What triggers cross-device enforcement? | Advertiser category policy, household caps, premium brand contracts | Configurable per rule: profile-only vs household |
| F2 | What is a household? | Billing account + linked devices / profiles under policy | Graph node `household_id` with membership edges |
| F3 | Subject types? | Profile (default), device (logged-out / CTV), household (union) | Multi-subject resolution per request |
| F4 | Union semantics? | **Most restrictive**: block if ANY linked subject at cap | Max(counts) or OR of BLOCK predicates |
| F5 | Increment on which subject(s)? | Primary profile + propagate to household rollup keys | Write fan-out bounded by graph degree |
| F6 | New device before link? | Best-effort; accept brief over-show until link | Stated tolerance; backfill optional |
| F7 | Profile switch same device? | Subject changes immediately; no bleed | Per-request subject from session |
| F8 | Kids profiles? | Ads-free or strict fail-closed | Short-circuit cross-device for kids |
| F9 | Travel cross-region? | Counters follow subject home; read with lag budget | Home cell routing |
| F10 | Logged-out CTV? | Device subject + weak household inference | Lower confidence tier |
| F11 | Unlink / divorce household? | Stop union immediately on read path | Versioned membership snapshot |
| F12 | GDPR / delete? | Remove subject keys; sever graph edges | Tombstone + async purge |
| F13 | Ops override? | Disable household union for incident | Feature flag per rule class |
| F14 | Reporting? | Delivered impressions deduped at household for some reports | Async; not decision SoT |

**MVP functional scope (lock with interviewer):**

1. At decision: resolve `profile_id` → optional `household_id` + linked `subject_set` within latency budget.
2. For rules with `subject_type=HOUSEHOLD`: cap check uses **union** of counters across members (most restrictive).
3. On impression: increment primary subject + household aggregate keys (packed).
4. Graph read: cached membership snapshot with `graph_version`; stale → profile-only fallback for soft rules.
5. Cross-region: subject **home region** for writes; decision reads local replica or home with timeout policy.
6. Metrics: identity latency, graph miss rate, union block rate, cross-device over-show estimate.

**Out of MVP (explicitly defer):**

- Perfect probabilistic household inference for all CTV (MVP: explicit links only)
- Real-time graph recomputation on every decision
- Cross-advertiser identity (never)
- Client-side household declaration as SoT
- Sub-5ms global strongly consistent graph reads

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Identity resolution latency? | Inside ad-decision budget | p99 < 3–5ms for graph slice alone |
| N2 | End-to-end cap check (incl. union)? | Part of 10–20ms cap subsystem | p99 < 15ms with federation |
| N3 | Graph availability? | Degrade gracefully | 99.9%; fallback to profile-only for soft |
| N4 | Staleness tolerance? | Seconds to minutes OK for soft; tighter for hard | `max_staleness_ms` per rule class |
| N5 | Correctness vs availability | Hard category household caps fail closed on graph timeout | Zero fail-open on hard union |
| N6 | Privacy | No cross-profile leakage in API responses | Internal opaque ids |
| N7 | Scale | 100M+ households, 1B+ devices | See scale table |
| N8 | Increment fan-out | Bounded degree per household | Cap members considered (e.g. top 8 profiles) |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User watches ad on phone → impression increments profile + household keys → TV session blocked at household cap.  
2. Decision on TV: resolve household → MGET profile counter + household counter + member rollups → union BLOCK.  
3. User travels EU → US: read home-region counters via gateway; slight lag acceptable for soft caps.  
4. New profile added to account: next graph snapshot includes member; union applies.  
5. Rule is profile-only: graph skipped; zero added latency.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Identity service timeout | Soft caps: profile-only check; Hard household: **fail closed** |
| Stale graph (new device unlinked) | Over-show until link; metrics `unlinked_device_impressions` |
| Household with 20 profiles | Policy cap union to active viewing profiles or billing primary + secondaries |
| Simultaneous impression phone + TV | Idempotent per impression; household counter may +2 correctly (two viewings) |
| Profile deleted mid-flight | Remove from snapshot; historical counts TTL expire |
| Split household billing dispute | Ops severs edge; union stops on new version |
| Clock skew cross-region | Server event time; window keys on policy TZ |
| Graph version rollback | Decisions stamp version; recon compares |
| Malicious device spoofing household | Server-side graph only; no client claims |
| Replica lag after travel | May under-block briefly; hard caps query home |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ads-tier DAU | 5M | 50M | 200M | 500M+ |
| Peak ad decisions / s | 20K | 200K | 2M | 20M |
| Decisions needing graph | 30% | 40% | 50% | 55% |
| Graph lookups / s | 6K | 80K | 1M | 11M |
| Households (active) | 5M | 50M | 200M | 500M |
| Avg profiles / household | 3 | 3 | 4 | 4 |
| Devices / household | 4 | 5 | 6 | 7 |
| Cross-region decisions / s | 2K | 20K | 200K | 2M |
| Counter keys with household dim | +50M | +500M | +5B | +25B |

**Split classes:** identity resolve ≠ cap multi-get ≠ increment fan-out ≠ graph ingest ≠ membership CDN.

**What each jump forces:**

- **10×:** Edge-cached household snapshots; colocate identity client with decision; pack household counters.  
- **100×:** Regional graph read replicas; subject home cells; precomputed household rollup hashes.  
- **1,000×:** Tiered union (exact for hard caps on small households; approximate bloom for soft long-tail); separate identity SLO cluster.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like AVOD: authenticated profiles dominant; CTV device graph weaker.  
- Frequency cap arithmetic lives in sibling doc; **this doc owns subject set and union**.  
- **Most-restrictive union:** if profile count=2 and household count=3 with limit 3, BLOCK.  
- Identity latency budget is **non-negotiable** slice of ad decision.  
- Legal/policy may require household-level alcohol/political caps.

**Scope statement:**

> Design cross-device and cross-region frequency enforcement: resolve cap subjects via household graph, apply most-restrictive union across linked identities, route counter reads/writes through subject home cells, and stay within a 3–5ms identity latency budget at 20K–20M decisions/s.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Identity lookups on decision path

```text
Peak decisions = 20,000 / s (baseline)
Fraction requiring household union = 30%
Graph-enriched decisions = 20,000 × 0.30 = 6,000 / s

If naive: 1 RPC to identity + 1 RPC to graph service per decision
→ 6,000 × 2 = 12,000 RPC/s graph path alone
```

At **100×** → **1.2M graph-path RPC/s** — requires local snapshot cache hit rate >99%.

**Deal-breaker:** synchronous cross-service fan-out per decision without cache.

### 2.2 Union read amplification

```text
Household with M profiles, rule requires union
Naive: M counter keys per scope per candidate

Candidates / decision ≈ 50
Scopes / candidate ≈ 3
Naive union keys = 50 × 3 × M = 150 × M

M=4 → 600 keys/decision → 20K × 0.3 × 600 = 3.6M extra reads/s
```

**Optimization:** pre-aggregated `household:{hid}:{scope}:{window}` counter updated on each member impression.

```text
Union check keys ≈ same as profile-only path (household rollup + profile for conflict resolution)
Extra keys / decision ≈ 1 rollup per scope pack → ~50 keys not 600
```

### 2.3 Increment fan-out

```text
Impressions / s baseline ≈ 5,000
Household rules apply to 30% → 1,500 / s
Writes per impression: profile pack + household pack ≈ 2 pipeline ops

Increment writes / s ≈ 1,500 × 2 × 3 scopes ≈ 9K (manageable)
At 1000×: scale with sharded KV
```

### 2.4 Graph snapshot cache

```text
Active households ≈ 5M baseline
Snapshot size ≈ household_id + member_ids[≤8] + version ≈ 200 B
Working set ≈ 5M × 200 B = 1 GB

Edge cache per decision pod: LRU 50K households × 200 B ≈ 10 MB local
CDN-style memcached tier: full 5M × 200 B ≈ 1 GB replicated
```

### 2.5 Cross-region latency

```text
Same-region counter read: 1–3ms
Cross-region home read: 20–80ms (unacceptable on hot path)

Policy: replicate household rollups to regional counter replicas
Async replication lag target: p99 < 500ms soft; hard caps sync home with 5ms timeout → fail closed
```

### 2.6 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Graph snapshot read (cached) | 6K | 800K | 11M | >99% cache hit |
| Identity profile resolve | 20K | 2M | 20M | mostly session JWT |
| Union cap multi-get | 6K | 800K | 11M | packed keys |
| Household increment | 1.5K | 150K | 1.5M | fan-out 2× |
| Graph ingest events | 500 | 5K | 50K | async |
| Membership invalidation | 50 | 500 | 5K | pub/sub |

### 2.7 Latency budget (identity + union slice)

| Stage | Budget |
|-------|--------|
| Extract profile from session | <0.5ms |
| Local snapshot lookup (household_id, members) | 0.5–1ms |
| Optional identity fallback RPC (cache miss) | 2–3ms (bounded) |
| Build subject set + cap keys | <0.5ms |
| Union multi-get (incl. in cap svc) | 3–8ms |
| **Cross-device slice total** | **≤5ms p99 identity; ≤15ms with counters** |

### 2.8 Storage for graph read path

```text
Household membership (OLTP source): 5M rows × 1 KB ≈ 5 GB
Snapshot materialization in Redis: 5M × 256 B × 3 repl ≈ 4 GB
Counter household dimension: +50M keys × 64 B ≈ 3.2 GB × repl
```

### 2.9 Critical bottlenecks

1. **Per-decision graph RPC** without cache.  
2. **Naive M×member counter reads** instead of rollups.  
3. **Cross-region home reads** on every travel session.  
4. **Unbounded household size** (20+ profiles).  
5. **Stale snapshot** causing wrong union after unlink.

### 2.10 Cost intuition

```text
Dominant: counter memory for household rollups + snapshot cache fleet
Track: identity_cache_hit_rate, cross_device_over_show_ppm
Cheaper to slightly under-union than leak competitive intel via debug APIs
```

---

## 3. High-Level Design

### 3.1 Placement in ads funnel

```text
Ad request → session/profile → [Cross-Device Subject Resolver] → freq cap check (union) → rank → select
                ↑                           ↓
         Identity Platform            Household Graph Snapshot
                                                ↓
                                         Counter Store (profile + household keys)
```

This layer sits **before** cap check; cap service consumes `CapSubjectSet`.

### 3.2 Entities

| Entity | Role |
|--------|------|
| `Profile` | Primary authenticated viewing identity |
| `Device` | Hardware id for logged-out / CTV weak linking |
| `Household` | Billing / policy group for union caps |
| `MembershipEdge` | profile/device → household with effective time range |
| `GraphSnapshot` | Materialized `{household_id, member_profile_ids[], version, ttl}` |
| `CapSubjectSet` | `{primary_profile, household_id?, subject_ids[], graph_version}` |
| `HouseholdRollupCounter` | Aggregated impression counts for union checks |

### 3.3 Subject resolution API (logical)

```text
ResolveSubjects(session, device_context, now) → CapSubjectSet

Steps:
  1. profile_id from session (required for ads tier)
  2. If rule bundle needs household: lookup snapshot(profile_id)
  3. If miss: optional Identity RPC with 2ms timeout → cache populate
  4. Return subject set capped at policy max members
```

### 3.4 Union semantics (most restrictive)

```text
For each cap rule R on scope S window W:
  counts = [ counter(subject, S, W) for subject in subject_set ]
  effective_count = max(counts)  # conservative: any member at cap blocks household

Alternatively for pre-rolled household key:
  effective_count = max(household_rollup, max(member counts))
  # Use max to catch lag on rollup; slightly over-blocks vs under-blocks
```

**Policy choice:** prefer **over-block** (under-delivery) vs **under-block** (over-show) for hard caps → use `max()`.

### 3.5 Increment path with federation

```text
ApplyImpression(impression_id, primary_profile, scopes, ts):
  1. Idempotency gate (sibling)
  2. INCR profile packed keys
  3. If household H resolved: INCR household rollup keys for same scopes
  4. Optional: INCR per-member mirror for recon (async batch, not hot path)
```

Rollup keeps union check O(1) per scope pack.

### 3.6 Graph ingestion (async)

```text
Identity events: ProfileCreated, DeviceLinked, HouseholdMerged, MemberRemoved
→ Graph Ingester → validate → update OLTP → publish snapshot invalidate
→ Snapshot Builder refreshes Redis/CDN entries
```

Decisions never block on ingest; they block on stale snapshot policy.

### 3.7 Cross-region strategy

| Data | Strategy |
|------|----------|
| Graph snapshots | Replicated globally; version monotonic |
| Profile/home region | Derived from account signup / primary locale |
| Counters | Home cell write; async replica to viewing region |
| Hard cap read abroad | 5ms home read OR fail closed |
| Soft cap read abroad | Local replica; lag OK |

### 3.8 Cache hierarchy

```text
L1: in-process LRU (50K households / pod)
L2: regional Memcached (full snapshot set, 1ms)
L3: Identity RPC (2–3ms, populate L1/L2)
```

**Never** L4 synchronous cross-region graph DB on hot path.

### 3.9 Failure policy matrix

| Scenario | Soft household rule | Hard household rule |
|----------|---------------------|---------------------|
| Snapshot miss + identity timeout | Profile-only union (weaker) | **BLOCK all candidates in category** |
| Rollup lag vs member sum | max() → safe | max() → safe |
| Graph version unknown | Treat as profile-only if soft | Fail closed |
| Replica stale 2s | Allow with metric | Home read or block |

### 3.10 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Union SoT for serving | Household rollup + max(member) for hard |
| Graph freshness | Snapshot with seconds TTL + event invalidate |
| New device | Profile/device cap until linked; stated gap |
| Cross-region | Replicate rollups; home for hard |
| Latency | Cache-first; bounded RPC |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+   session    +-------------------+     +----------------------+
| Player |------------->| Ad Decision Svc   |---->| Targeting / Auction  |
+--------+              +---------+---------+     +----------------------+
                                  |
                                  v
                        +---------+---------+
                        | Subject Resolver  |
                        +---------+---------+
                           |            |
              cache hit    |            | miss (timeout bound)
                           v            v
                  +--------+---+   +---+------------+
                  | Snapshot   |   | Identity Svc   |
                  | Cache L1/L2|   +----------------+
                  +-----+------+
                        |
                        v
                +-------+--------+
                | Freq Cap Svc   |---- union multi-get ----+
                +-------+--------+                         v
                        |                          +-------+-------+
                        v                          | Counter Store |
                +-------+--------+                 | profile+HH    |
                | Rules / Config |                 +---------------+
                +----------------+

Identity Platform --events--> Graph Ingester --> Snapshot Builder --> Snapshot Cache
```

### 4.2 Sequence: decision with household union

```text
Decision→SubjectResolver: Resolve(session)
SubjectResolver→L1Cache: get(profile_id)
  hit → CapSubjectSet(hh=H, members=[p1,p2,p3], v=991)
SubjectResolver→CapSvc: Check(subject_set, candidates)
CapSvc→Redis: pipeline MGET profile:p1:*, hh:H:* packed keys
CapSvc: for each candidate: effective = max(counts); if >= N → BLOCK
CapSvc→Decision: eligible set + graph_version stamped
```

### 4.3 Sequence: cache miss with bounded fallback

```text
SubjectResolver→L1: miss
SubjectResolver→L2 Memcached: miss
SubjectResolver→Identity: GetHousehold(profile) [2ms timeout]
  ok → populate caches → CapSubjectSet
  timeout → if hard_rules: BLOCK category; else profile-only CapSubjectSet + alert
```

### 4.4 Sequence: impression increment with rollup

```text
Impression→SubjectResolver: Resolve (same as decision, may use cached)
Impression→IdemKV: SETNX impression_id
Impression→Redis: INCR profile:p1 fields
Impression→Redis: INCR household:H fields (same scopes/windows)
Impression→Log: append {impression_id, p1, H, graph_version}
```

### 4.5 Sequence: membership change

```text
Identity→Bus: MemberRemoved(p9, H)
Ingester→OLTP: close edge effective_to=now
Ingester→Bus: InvalidateSnapshot(H, v=992)
SnapshotBuilder→Redis: rebuild H members
Decision pods: next request sees v=992; p9 excluded from union
```

### 4.6 Sequence: cross-region viewer

```text
Viewer in EU, home=US
Decision EU→CapSvc: Check subject_set
CapSvc→Redis EU replica: MGET hh:H keys
  if hard cap + replica_age > threshold:
    CapSvc→Redis US home: MGET [5ms timeout]
      ok → evaluate
      fail → BLOCK hard scopes
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Server-side graph only** — clients cannot assert household membership.  
2. **Most-restrictive union** for hard caps uses `max(counts)`.  
3. **Graph version** stamped on every decision for debug/recon.  
4. **Hard household caps fail closed** when subject set unknown.  
5. **Idempotent impressions** do not double-rollup household counters.  
6. **Unlink takes effect** on snapshot version bump, not counter decrement.  
7. **No cross-household counter bleed**.  
8. **Kids profiles** bypass household union (no ads path).

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Snapshot stale after unlink | New version excludes member; old counts TTL naturally |
| Rollup behind member | max() guards hard caps |
| Split-brain replica | Recon from log; hard caps prefer home |
| Identity outage | Soft degrade profile-only; hard block sensitive categories |
| Hot household celebrity | Shard rollup keys by household_id |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Snapshot cache colocated; single counter cluster; OLTP graph |
| 10× | Memcached snapshot tier; rollup keys mandatory; ingest Kafka |
| 100× | Regional replicas; subject home cells; cap union members at 8 |
| 1,000× | Probabilistic soft union bloom; dedicated hard-cap identity path |

**Sharding:** `hash(household_id)` for rollup counters; `hash(profile_id)` for profile counters.

### 5.3 Maintainability

- Shadow mode: compute union BLOCK but enforce profile-only; measure delta.  
- Metrics: `identity_resolve_p99`, `snapshot_hit_rate`, `union_block_rate`, `cross_device_over_show_ppm`, `graph_version_lag`.  
- Diff tool: rebuild household rollup from impression log vs live.  
- Feature flag: `household_union_enabled` per rule category.

### 5.4 Exact algorithm: resolve subjects

```text
function resolve(session, rule_bundle, now):
  profile = session.profile_id
  if session.is_kids: return KIDS_NO_ADS
  if not rule_bundle.needs_household():
    return CapSubjectSet(primary=profile, subjects=[profile])
  snap = L1.get(profile) or L2.get(profile)
  if snap == null:
    snap = identity.fetch_household(profile, timeout=2ms)
    if snap == null:
      if rule_bundle.has_hard_household(): return FAIL_CLOSED
      return CapSubjectSet(primary=profile, subjects=[profile], degraded=true)
    cache.put(snap)
  members = snap.members.take(policy.max_union_members)
  subjects = unique([profile] + members)
  return CapSubjectSet(primary=profile, household=snap.hh, subjects=subjects, version=snap.v)
```

### 5.5 Exact algorithm: union cap check

```text
function unionCheck(subject_set, candidate, rule, counter_store):
  if rule.subject_type == PROFILE:
    return counter_store.get(subject_set.primary, rule) < rule.N
  counts = []
  for s in subject_set.subjects:
    counts.append(counter_store.get(s, rule))
  if subject_set.household:
    counts.append(counter_store.get_hh_rollup(subject_set.household, rule))
  effective = max(counts)
  return effective < rule.N
```

### 5.6 Exact algorithm: increment with rollup

```text
function applyUnionIncrement(impression_id, subject_set, scopes, ts):
  if not idem.tryInsert(impression_id): return
  for scope in expandHierarchy(scopes):
    counter_store.incr(subject_set.primary, scope, ts)
    if subject_set.household:
      counter_store.incr_hh_rollup(subject_set.household, scope, ts)
```

### 5.7 Staleness and over-show analysis

```text
Over-show scenarios:
  1. New device unlinked: only device-level cap until link
  2. Replica lag Δt: at most impressions in Δt per region
  3. Profile-only degrade: household cap ignored → bounded by member caps only

cross_device_over_show_ppm ≈ unlinked_impressions / total_impressions × 1e6
Target: < 500 ppm soft; minimize via device heuristics at 100×
```

### 5.8 Device linking heuristics (100×)

| Signal | Weight |
|--------|--------|
| Same billing account login | Strong |
| Same IP + simultaneous stream pattern | Medium (privacy review) |
| CTV device registration | Strong |
| Cookie sync | Weak / not for MVP |

Heuristics feed **identity platform**, not ad decision directly.

### 5.9 Multi-region deep dive

- **Writes always home** to avoid split increments.  
- **EU viewer**: read EU replica; if hard cap, parallel home query.  
- **Travel detection**: optional `viewing_region` header; pre-warm replica from home on login.  
- **GDPR**: household data residency in EU cell; snapshots scoped.

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Client declares household | Fraud / cap evasion |
| Sum counts instead of max | Under-block when one member hot |
| Sync graph DB on every decision | Latency death |
| Cross-region write on impression | Split brain double count |
| Unlimited union members | Read amplification explosion |
| Fail-open hard household on timeout | Legal / brand safety |
| Separate counter systems per device | Inconsistent union |

### 5.11 Progressive scale deep dive

**1× (~20K decisions/s)**  
Single snapshot Memcached; rollup keys; identity RPC on miss only.

**10×**  
L1 per pod 99% hit; ingest pipeline; household cap member limit 8.

**100×**  
Regional counter replicas; home routing; shadow union metrics; device link backfill job.

**1,000×**  
Soft caps: bloom "maybe seen on any device"; hard caps: exact rollup cluster; edge subject hints from login JWT claims.

### 5.12 Security & privacy

- Household membership not exposed to advertisers.  
- Debug logs sampled; no member PII in cap keys.  
- Rate limit identity fallback RPC per profile.  
- Audit graph changes with operator id.

### 5.13 Rollout

```text
Phase 1: profile-only enforce (baseline)
Phase 2: shadow union metrics
Phase 3: soft household union enforce
Phase 4: hard category household enforce
Instant rollback: disable union flag; profile-only
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Union semantics | Most restrictive = max(counts) |
| Hot path graph | Cached snapshots; bounded identity RPC |
| Rollup keys | Household aggregate on increment |
| Cross-region | Home write; regional read; hard home fallback |
| Degrade | Profile-only soft; fail closed hard |
| Latency | 3–5ms identity slice |

### 6.2 Risks

1. Unlinked devices over-show household-capped campaigns  
2. Snapshot staleness after rapid membership changes  
3. Replica lag on travel under-blocking hard caps  
4. Large households without member cap  
5. Identity outage correlated with traffic spike  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: not full caps; subject + union; sibling refs |
| 5–15 | Resolve API; most-restrictive union math |
| 15–25 | Rollup vs naive M×reads; latency budget |
| 25–35 | Cross-region home; fail closed hard |
| 35–45 | Scale cache; device link gap; metrics |

---

## 7. Deeper / Related Interview Questions

### 7.1 Union semantics

**Q: Sum or max for household union?**  
A: **Max** for conservative blocking — if any member at cap, household treated at cap. Sum would under-block.

**Q: Why rollup key if we have max(members)?**  
A: Rollup reduces reads from O(M) to O(1); max(rollup, members) catches replication lag.

### 7.2 Identity latency

**Q: Where does 3–5ms go?**  
A: ~1ms cache, ~2ms identity RPC on miss, ~0.5ms build keys — rest in cap store sibling.

**Q: Can we skip graph for all?**  
A: Yes when rules are profile-only — always classify rules first.

### 7.3 New device problem

**Q: User buys new TV, sees ad 4 times before link?**  
A: Device subject has own counters; household cap applies after link; state ppm tolerance; optional weak device inference at scale.

### 7.4 Cross-region

**Q: User watches in vacation home abroad?**  
A: Subject home unchanged; regional replica serves soft; hard queries home with timeout.

**Q: Split counters per region?**  
A: No — home SoT with replication; split writes cause union errors.

### 7.5 Privacy

**Q: Does household union reveal viewing across profiles?**  
A: Internal only; advertisers see household-level aggregates optionally, never member breakdown.

**Q: Roommates sharing account?**  
A: Product/policy: profiles separate caps; household union optional per category only.

### 7.6 Consistency

**Q: Eventually consistent graph OK?**  
A: Yes for soft; hard caps need versioned snapshots + fail closed on unknown.

**Q: Impression on two devices same second?**  
A: Two valid viewings; both increment rollup +2 if both viewable.

### 7.7 CTV logged-out

**Q: No profile?**  
A: Device subject; weak household via device registration graph; disclose weaker guarantees.

### 7.8 Ops

**Q: Emergency disable household caps?**  
A: Feature flag → profile-only; metrics alert on over-show spike.

### 7.9 vs frequency cap sibling

**Q: Overlap?**  
A: Sibling owns counters/windows/idempotency; this doc owns subject_set and union evaluation.

### 7.10 Interview traps

**Q: "Query Neo4j on every ad decision"?**  
A: Latency and ops nightmare; materialized snapshots.

**Q: "Household = IP address"?**  
A: GDPR/privacy + mobile IP churn; use billing graph.

**Q: "Union = average counts"?**  
A: Wrong semantics; allows over-show.

### 7.11 Metrics

**Q: What pages on-call?**  
A: Hard-rule profile-only degrade rate; identity timeout spike; cross_device_over_show_ppm; snapshot hit rate collapse.

### 7.12 GDPR delete

**Q: User deletes account?**  
A: Tombstone profile; remove from snapshots; TTL counters; sever edges.

---

## 8. Appendices

### A1. CapSubjectSet schema

```text
CapSubjectSet {
  primary_profile_id,
  household_id?,
  subject_ids[],        // bounded
  graph_version,
  degraded: bool,
  resolved_at_ms
}
```

### A2. GraphSnapshot schema

```text
GraphSnapshot {
  household_id,
  member_profile_ids[],  // max 8 policy
  device_ids[],          // optional weak
  version: int64,
  effective_from,
  source: BILLING|HEURISTIC|MANUAL
}
```

### A3. Household rollup counter key

```text
key: fcap:hh:{household_id}:{window_id}
field: {scope_type}:{scope_id} → count
```

### A4. Membership edge (OLTP)

```sql
CREATE TABLE household_members (
  household_id UUID NOT NULL,
  profile_id UUID NOT NULL,
  effective_from TIMESTAMPTZ NOT NULL,
  effective_to TIMESTAMPTZ,
  PRIMARY KEY (household_id, profile_id, effective_from)
);
```

### A5. Launch checklist

- [ ] Union semantics signed (max vs sum)  
- [ ] Rollup increment wired on impression path  
- [ ] Hard fail-closed on identity timeout tested  
- [ ] Snapshot invalidate on membership change  
- [ ] Cross-region replica lag measured  
- [ ] Shadow union metrics dashboard  
- [ ] Member cap policy enforced  

### A6. Glossary

| Term | Meaning |
|------|---------|
| Cap subject | Identity anchor for counters |
| Household union | Treat linked profiles as one cap pool |
| Most restrictive | Block if any member at limit |
| Rollup key | Pre-aggregated household counter |
| Graph version | Monotonic snapshot id |
| Home cell | Region owning subject writes |

### A7. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| Graph DB on hot path | Snapshots + cache |
| Sum member counts | Max for conservative |
| Client household id | Server graph only |
| Per-region write | Home cell |
| Ignore latency budget | Split cache + rollup |

### A8. 60-second summary

> Cross-device frequency enforcement **resolves a bounded subject set** from **cached household snapshots**, applies **most-restrictive union** via **max(profile, member, rollup) counts**, **increments rollups on impression**, routes **cross-region through home writes and regional replicas**, and **fails closed on hard caps** when identity is unknown — never synchronous graph traversals per ad.

### A9. Related systems map

```text
Identity Platform → Graph Ingester → Snapshot Cache
Ad Decision → Subject Resolver → Freq Cap Service → Counter Store
Impression Service → Subject Resolver → Counter Store (profile + hh rollup)
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Subject resolve p99 | < 5ms |
| Snapshot cache hit | > 99% |
| Hard cap fail-open on unknown household | 0 |
| cross_device_over_show_ppm (soft) | < 500 |
| Graph invalidate propagation | < 30s p99 |

### A11. Worked numeric example

```text
Household H: members p1, p2. Campaign cap 3/day household.
p1 count=2, p2 count=1, rollup=3 (lag caught up)
effective = max(2,1,3) = 3 → BLOCK
If only rollup=2: max(2,1,2)=2 → ALLOW (safe side)
```

### A12. Invalidation event types

```text
HOUSEHOLD_MEMBER_ADDED
HOUSEHOLD_MEMBER_REMOVED
HOUSEHOLD_MERGED
DEVICE_LINKED
DEVICE_UNLINKED
PROFILE_DELETED
```

### A13. Ownership

| Concern | Owner |
|---------|-------|
| Subject resolver | Ads Serving |
| Household graph OLTP | Identity Platform |
| Snapshot builder | Identity + Ads |
| Rollup counters | Ads Serving (cap store) |
| Policy on union | Ads Policy / Legal |

### A14. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Snapshot cache + rollup keys |
| 10× | L1 local + ingest pipeline |
| 100× | Regional replicas + home routing |
| 1,000× | Tiered soft union approx |

### A15. Comparison to naive design

| Naive | Why it fails |
|-------|--------------|
| Per-decision graph traverse | Latency |
| Read all member counters | Amplification |
| Client cookie household | Spoofing |
| No rollup | O(M) reads |
| Fail-open hard | Compliance risk |

### A16. On-call cheat sheet

1. Check `snapshot_hit_rate` drop → Memcached/identity.  
2. Check `degraded_profile_only_rate` for hard rules.  
3. Verify recent graph deploy / version skew.  
4. Rollback union enforce flag if over-show spike.  
5. Compare rollup vs log-rebuilt household counts.

### A17. Sample decision debug record

```text
{
  "decision_id": "...",
  "graph_version": 8841,
  "household_id": "hh_42",
  "subject_set": ["p1","p2","p3"],
  "union_blocked": [
    {"scope": "campaign:k_1", "effective_count": 3, "limit": 3, "counts": {"p1":2,"p2":3,"rollup":3}}
  ]
}
```

### A18. Interaction with presentation order

Cross-device caps limit **how often**; presentation order limits **sequencing**. Independent filters in decision funnel.

### A19. Cost worksheet

```text
snapshot_mem_GB ≈ households × 256B × repl
rollup_keys ≈ households × active_windows × scopes
identity_rpc_cost ∝ (1 - cache_hit) × decisions
```

### A20. Explicit non-goals

- Building the full Netflix household product UI  
- Cross-advertiser identity graph  
- Real-time ML household inference on decision path  
- Replacing profile-level caps entirely  

### A21. Device subject key schema

```text
key: fcap:device:{device_id}:{window_id}
field: {scope_type}:{scope_id} → count
Link event may migrate counts → profile (policy: no migrate MVP; dual count until TTL)
```

### A22. JWT embedded claims (optional 100×)

```text
ads_claims: { profile_id, household_id, graph_version }
Reduces miss rate; must match server snapshot version or ignore claim
```

---

*End of document — Netflix system design interview prep: Cross-Device Frequency Enforcement.*
