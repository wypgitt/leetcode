# System Design: Ad Frequency Capping

> **Focus areas:** Real-time cap checks · Creative / line-item / campaign / category hierarchies · Impression attribution · Idempotent increments · Cross-session identity · Pacing coupling · Fail-open vs fail-closed  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar QPS (decision vs increment vs reconcile), explicit deal-breakers, Netflix Ads 2025–26 interview themes  
> **Interview theme:** Netflix Ads — enforce “don’t show this ad too often” under tight ad-decision latency without melting the control plane

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

Goal: **bound frequency capping**—the subsystem that answers “may we serve creative/line/campaign/category X to identity Y in window W?” at ad-decision time, then records impressions so future decisions stay correct.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Enforce frequency caps at decision + record impressions | Full ads auction / creative CDN |
| Caps | Count-based limits over time windows | Budget pacing (sibling: ad-pacing) |
| Identity | Profile / device / household graph for caps | Full ads data model (sibling) |
| Windows | Fixed calendar + rolling (rolling deep-dive sibling) | Pure batch overnight only |
| Cross-device | Hooks + progressive hardening | Full graph product (sibling) |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is capped? | Creative, line item, campaign, category (e.g. alcohol) — hierarchical | Multi-key counters per request |
| F2 | Cap definition? | N impressions per window (1h / 1d / 7d / flight) | Counter schema + window type |
| F3 | Who is the subject? | Viewing profile primary; device/household optional | `cap_subject_id` resolution |
| F4 | When is check? | During ad decision before select/return | Low-latency read path |
| F5 | When is increment? | On **billable / viewable impression** (policy), not on bid | Separate increment path; idempotent |
| F6 | Soft vs hard caps? | Hard for brand safety categories; soft for some advertiser prefs | Policy flag per rule |
| F7 | Over-delivery tolerance? | Prefer slight under-serve vs large over-cap | Conservative increments / reservations |
| F8 | Cross-device? | Best-effort MVP; stronger at 100× | Identity graph optional join |
| F9 | Cross-region? | User travels; counters follow subject | Global or sticky home for counters |
| F10 | Reporting? | Advertisers see delivered vs capped | Async aggregates, not decision SoT |
| F11 | Ops kill? | Pause creative / raise temporary caps | Config push + short TTL caches |
| F12 | Interaction with pacing? | Cap eligibility ∧ pacing eligibility | Both filters in decision funnel |

**MVP functional scope (lock with interviewer):**

1. Define cap rules: `(scope_type, scope_id, subject_type, N, window)`.
2. At decision time: resolve subject → **multi-get counters** → filter ineligible ads.
3. On impression: **idempotent increment** keyed by `impression_id`.
4. Support creative + line item + campaign scopes (category Phase 1.5).
5. Calendar-day and fixed flight windows in MVP; rolling-window sibling for deep dive.
6. Metrics: cap-block rate, over-cap rate, decision latency, increment lag.
7. Config version stamped on decisions; kill switch to bypass non-safety caps under outage (policy).

**Out of MVP (explicitly defer):**

- Perfect global cross-device identity as hard requirement
- Frequency caps on clicks/conversions as primary (impressions first)
- Client-trusted counter as source of truth
- Multi-master active-active conflicting increments without CRDT/merge policy
- Guaranteeing zero over-cap under all partitions (state the tolerance)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Decision check latency? | Inside ad decision budget | p99 < 10–20ms for cap check alone |
| N2 | Increment durability? | Counted impressions not lost | Quorum / replicated KV before ACK (or outbox) |
| N3 | Over-cap rate? | Very low for hard caps | < 0.1–1% depending on policy |
| N4 | Availability of decision? | Ads path critical for ads tier UX | Prefer degrade policy over blank stream |
| N5 | Consistency? | Read-your-writes within session ideal | Same-region strong; cross-region eventual OK with bounds |
| N6 | Idempotency? | Retries must not double-count | `impression_id` unique |
| N7 | Scale | Through 1000× ad decisions | See scale table |
| N8 | Privacy | Caps must not leak cross-profile | Subject keyed by authorized profile |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Decision: candidate ads → cap check → eligible set → auction/select → return pod.  
2. Player reports viewable impression → increment counters for creative/line/campaign.  
3. Cap reached mid-flight → subsequent decisions exclude that scope.  
4. New day window → counters reset (calendar) or slide (rolling).  
5. Duplicate impression beacon → idempotent no-op.  
6. Category hard cap (e.g. political) blocks even if campaign under cap.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cap store timeout at decision | Policy: fail-open for soft caps; **fail-closed for brand-safety hard caps** |
| Increment succeeds, decision cache stale | Short TTL + read repair; accept tiny over-cap budget |
| Impression before decision logged | Increment still keyed; decision may have reserved (optional) |
| Clock skew across regions | Server event time; window boundaries on server TZ policy |
| Profile switch on same device | Subject changes; no bleed of adult caps into kids (kids often ads-free) |
| Hot celebrity campaign | Shard counters; avoid single global lock |
| Replay of old beacons | Idempotency store TTL ≥ window; reject unknown late policy |
| Partial hierarchy increment failure | TX or ordered multi-key update with retry; never creative+1 campaign+0 silently for long |
| User clears cookies / new device | New device subject until identity link; over-show risk stated |
| Config cap lowered below current count | Immediately ineligible; no need to decrement |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ads-tier DAU | 5M | 50M | 200M | 500M+ |
| Peak ad decisions / s | 20K | 200K | 2M | 20M |
| Candidates checked / decision | 50 | 50 | 80 | 100 |
| Cap keys touched / decision | 150 | 150 | 240 | 300 |
| Peak impression increments / s | 5K | 50K | 500K | 5M |
| Distinct cap subjects | 10M | 100M | 1B | 5B |
| Active cap rules | 50K | 200K | 1M | 5M |
| Counter keys (working set) | 200M | 2B | 20B | 100B+ |

**Split classes:** decision multi-get ≠ impression increment ≠ batch reconcile ≠ reporting ETL.

**What each jump forces:**

- **10×:** Redis/Memconfigurable-style clustered counters; pipelined MGET; local negative cache for “at cap”.  
- **100×:** Subject home cells; hierarchical key design; optional reservation tokens; regional decisioning.  
- **1,000×:** Probabilistic structures for long-tail soft caps; edge bloom “maybe under cap”; hierarchical rollups; strict SLOs on hard-cap path only.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like **AVOD / ads plan**: mid-roll pods; server-side ad decision.  
- Impression definition locked with interviewer (e.g. 2s viewable).  
- Caps are **eligibility filters**, not the auction.  
- Sibling docs: rolling windows, cross-device, pacing, ads data model.

**Scope statement:**

> Design a real-time ad frequency-capping system that filters candidates at decision time using hierarchical counters (creative / line / campaign / category), increments idempotently on impressions, and evolves from ~20K decisions/s through 10× / 100× / 1,000× with explicit over-cap tolerance and fail-closed brand-safety policy.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Decision-path read amplification

```text
Peak decisions = 20,000 / s (baseline)
Candidates / decision ≈ 50
Scopes / candidate ≈ 3 (creative, line, campaign)
Keys / decision ≈ 50 × 3 = 150

Key lookups / s ≈ 20,000 × 150 = 3,000,000 / s
```

At **100×** → **300M lookups/s** if naive — impossible without:

1. Batching keys per decision into one pipeline,  
2. Caching “at cap” positives,  
3. Reducing candidates before cap check,  
4. Packing counters (struct of scopes) per subject+campaign.

**Deal-breaker:** one network RTT per key.

### 2.2 Packing optimization

```text
Better key design:
  HASH subject_id → field "{scope_type}:{scope_id}:{window_id}" → count

Or wide value:
  key = cap:{subject}:{campaign}:{window}
  value = {line_counts..., creative_counts..., campaign_total}

Lookups / decision ≈ 50 campaigns touched (often <<50 unique campaigns)
If 20 unique campaign keys × 1 RTT pipeline → ~20 pipeline ops not 150
```

### 2.3 Increment rate

```text
Fill rate: not every decision yields an impression
Assume 5K impressions/s baseline peak
Each impression updates ~3–5 counters
Counter writes / s ≈ 20K

At 1000×: 5M impressions/s → 20M counter writes/s → sharded KV + async where policy allows
```

### 2.4 Storage

```text
Counter entry ≈ 32–64 B metadata + value
Active keys baseline 200M × 64 B ≈ 12.8 GB raw × replication 3 ≈ ~40 GB
At 100×: ~4 TB class cluster — plan eviction of expired windows
```

**TTL:** expire counter keys when window ends (+ grace for late beacons).

### 2.5 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Cap check (decision) | 20K | 2M | 20M | pipelined multi-get |
| Counter key ops | 3M | 300M → target ≪ via packing | extreme | optimize key design |
| Impression increment | 5K | 500K | 5M | idempotent |
| Idempotency insert | 5K | 500K | 5M | TTL’d |
| Config read | 1K | 10K | 100K | cached at decision nodes |
| Reconcile / repair | 100 | 1K | 10K | async |

### 2.6 Latency budget (ad decision slice)

| Stage | Budget |
|-------|--------|
| Resolve subject | 1–2ms |
| Load rules for candidates | 1–3ms (cached) |
| Multi-get counters | 3–8ms |
| Evaluate predicates | <1ms |
| **Cap subsystem total** | **≤10–20ms p99** |

### 2.7 Critical bottlenecks

1. **Read amplification** on decision path.  
2. **Hot keys** for mega-campaigns × popular subjects still fine; hot is “global campaign aggregate” if mis-keyed.  
3. **Increment vs read race** → over-cap.  
4. **Idempotency store size** if TTL too long.  
5. **Cross-region subject** travel without home follow.

### 2.8 Cost intuition

```text
Dominant cost: memory for counters + decision CPU
Track: $/1M decisions and over-cap_ppm (parts per million)
Slight under-delivery usually cheaper than brand-safety incidents
```

---

## 3. High-Level Design

### 3.1 Placement in ads funnel

```text
Ad request → targeting → budget/pacing eligible → frequency cap filter → rank/auction → select
                                      ↑                            ↓
                              Cap Counters Store              Impression service → increment
```

Caps are a **filter stage**, not a ranker.

### 3.2 Entities

| Entity | Role |
|--------|------|
| `CapRule` | scope, N, window, hard/soft, version |
| `CapSubject` | profile_id (primary), optional device/household |
| `Counter` | subject × scope × window → count |
| `ImpressionEvent` | immutable fact; drives increment |
| `IdempotencyRecord` | impression_id → applied |

### 3.3 Window types

| Type | Semantics | MVP |
|------|-----------|-----|
| Calendar day (TZ) | Reset at midnight in policy TZ | Yes |
| Flight total | Count since campaign start / until end | Yes |
| Fixed hour buckets | Increment bucket; sum last K | Yes |
| Sliding rolling | Exact or approximate events in last T | Sibling deep dive |

### 3.4 Check API (logical)

```text
CheckCaps(subject_id, candidates[], now) → Map<candidate_id, CapDecision>
CapDecision = ALLOW | BLOCK {rule_id, scope, count, limit}
```

Implementation: batch all keys → MGET → evaluate.

### 3.5 Increment API (logical)

```text
ApplyImpression(impression_id, subject_id, scopes[], ts) → OK
Steps:
  1. Insert idempotency(impression_id) if not exists else return OK
  2. INCR each counter for window(ts)
  3. Optionally emit to log/stream for recon
```

### 3.6 Optional reservation (reduce over-cap)

Under concurrency (many decisions before impression):

| Approach | Pros | Cons |
|----------|------|------|
| No reservation (MVP) | Simple | Over-cap under burst |
| Soft reserve + TTL | Bounds concurrent over-show | Complexity; reserve leak |
| Incremental only on impression | Matches billing | Decision races |

**Chosen MVP:** no reserve; accept small over-cap; add reserves at 100× for hard caps.

### 3.7 Store choice

| Option | Pros | Cons | Choice |
|--------|------|------|--------|
| Redis cluster | Fast INCR/MGET, TTL | Memory cost; durability config | **MVP hot path** |
| DynamoDB / Bigtable | Durable, scale | Higher latency | Durable backup / 100× hybrid |
| Pure DB | Strong TX | Too slow at decision QPS | No |
| Bloom-only | Tiny | False positives block revenue | Assist only at 1000× |

**Pattern:** Redis counters + async durable event log for rebuild/recon.

### 3.8 Identity resolution

```text
Request context → profile_id (authenticated)
Optional: device_id, household_id from identity service (budgeted timeout)
subject_keys = [profile] (+ household if hard category policy)
Evaluate UNION of caps (most restrictive wins)
```

**Kids profiles:** typically no ads; if present, fail closed.

### 3.9 Config propagation

Cap rules versioned. Decision nodes cache rules with short TTL + pub/sub invalidate. Every response includes `caps_config_version`.

### 3.10 Failure policy matrix

| Cap class | Store down | Policy |
|-----------|------------|--------|
| Soft advertiser freq | Timeout | Fail-open (allow) + alert |
| Hard category / legal | Timeout | **Fail-closed (block)** |
| Increment path down | N/A | Buffer to log; catch-up; may under-count briefly |

**Never** fail-open brand-safety category caps.

### 3.11 Consistency model

- Single-region: Redis quorum reads for checks where possible.  
- Multi-region: subject **home region** for increments; decisions remote may read replica with lag budget.  
- Rebuild: event log → recompute counters.

### 3.12 Trade-offs summary

| Topic | Decision |
|-------|----------|
| SoT for serving | Hot counters |
| SoT for audit | Impression event log |
| Over-cap | Explicit PPM budget |
| Hierarchy | Multi-scope keys / packed values |
| Cross-device | Best-effort join |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+  ad opportunity   +------------------+     +------------------+
| Player |------------------>| Ad Decision Svc  |---->| Targeting / Rank |
+--------+                   +--------+---------+     +------------------+
     |                                |
     |                                v
     |                       +--------+---------+
     |                       | Freq Cap Service |
     |                       +--------+---------+
     |                                |
     |                   +------------+------------+
     |                   v                         v
     |            +-------------+          +---------------+
     |            | Rules Cache |          | Counter Store |
     |            | (versioned) |          | (Redis/...)   |
     |            +-------------+          +---------------+
     |
     | impression beacon
     v
+------------------+     idempotent      +------------------+
| Impression Svc   |-------------------->| Counter Store    |
+--------+---------+                     +------------------+
         |
         v
+------------------+     rebuild/recon   +------------------+
| Event Log / Bus  |-------------------->| Cap Reconciler   |
+------------------+                     +------------------+
```

### 4.2 Sequence: decision check

```text
Decision→CapSvc: Check(subject, [cand...])
CapSvc→Rules: get rules for scopes (cached)
CapSvc→Redis: pipeline HGET/MGET packed keys
CapSvc: for each cand: if any hard rule violated → BLOCK
CapSvc→Decision: allow-set + debug reasons (sampled)
```

### 4.3 Sequence: impression increment

```text
Player→Impression: beacon(impression_id, ad_ids, profile)
Impression: validate auth + schema
Impression→IdemKV: SETNX impression_id
  if exists → 200 OK
Impression→Redis: INCR hierarchy fields
Impression→Log: append durable event
```

### 4.4 Sequence: window rollover

```text
Calendar day: key suffix includes date → new keys naturally start at 0
Old keys TTL expire after grace
Rolling: maintain bucket keys minute_i; sum last N buckets (sibling doc)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Idempotent impression apply** by `impression_id`.  
2. **Hard brand-safety caps fail closed** on uncertainty.  
3. **Soft caps may fail open** with alerts when store unhealthy.  
4. **Event log is rebuildable SoT** for counters.  
5. **Config version** on decisions for debug.  
6. **No cross-profile counter bleed**.  
7. **Monotonic counts** within a window (no decrement except TTL expiry / rebuild).  
8. **Late beacon policy** explicit (accept within grace / drop).

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Redis read timeout | Soft allow / hard block per rule class |
| Redis write fail on incr | Retry → outbox; mark impression for catch-up |
| Dual increment race on same id | SETNX winner only |
| Bad rule publish | Canary + instant rollback by version |
| Reconciler detects drift | Repair counters from log; page if hard-cap under-count |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | One Redis cluster; Cap service + Impression service; PG for rules |
| 10× | Key packing; pipeline; local at-cap cache; rule CDN to nodes |
| 100× | Subject home cells; regional decision; reserve for hard caps; column counters |
| 1,000× | Hierarchical approx for soft; edge hints; separate hard-cap cluster SLOs |

**Sharding:** `hash(subject_id)` — keeps all scopes for a subject co-located for pipeline locality.

### 5.3 Maintainability

- Rule compiler: validate N>0, window known, scope exists.  
- Shadow mode: compute BLOCK but do not enforce; measure would-block rate.  
- Diff tooling: rebuild counter from log vs live.  
- Metrics: `cap_check_latency`, `cap_block_rate`, `over_cap_ppm`, `idempotent_hit_rate`, `fail_open_rate`, `fail_closed_rate`.  
- No per-subject Prometheus labels.

### 5.4 Exact algorithm: check

```text
function check(subject, candidates, now):
  rules = rulesFor(candidates)  # cached
  keys = packKeys(subject, rules, now)
  values = pipelineGet(keys)
  out = {}
  for c in candidates:
    out[c] = ALLOW
    for r in rules[c]:
      cnt = values[key(r)]
      if cnt >= r.N:
        if r.hard: out[c] = BLOCK(r); break
        else: out[c] = BLOCK(r); break  # soft still blocks eligibility
  return out
```

### 5.5 Exact algorithm: increment

```text
function apply(impression_id, subject, scopes, ts):
  if not idem.tryInsert(impression_id, ttl=window_grace):
    return DUPLICATE
  pipe = redis.pipeline()
  for scope in expandHierarchy(scopes):
    k = key(subject, scope, windowId(ts, scope.rule))
    pipe.hincrby(k, field(scope), 1)
    pipe.expire(k, ttl)
  pipe.execute()
  log.append(...)
  return OK
```

### 5.6 Hierarchy expansion

```text
Impression on creative C of line L of campaign K in category G
Increments: C, L, K, (G if category rules exist)
Decision blocks if ANY applicable scope at limit
```

### 5.7 Over-cap control

```text
over_cap_ppm = 1e6 * impressions_over_limit / impressions_total
Budget example: soft 1000 ppm; hard 10 ppm
Levers: shorter decision cache, reservations, lower parallelism per subject
```

### 5.8 Coupling to pacing

Pacing may mark campaign “go dark” for budget; caps mark “go dark” for frequency. Decision requires **both** eligible. Do not double-count responsibilities.

### 5.9 Multi-region

| Data | Strategy |
|------|----------|
| Rules | Globally replicated, versioned |
| Counters | Home cell by subject; async replicate |
| Decisions abroad | Read local replica; bound lag; hard caps may query home with timeout→fail closed |
| Impressions | Write home via gateway; outbox if remote |

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Increment on bid/decision | Caps ≠ delivery; advertisers angry |
| Client-side only counters | Cheatable; inconsistent |
| One key per global campaign count only | Cannot enforce per-user freq |
| Fail-open all caps | Brand safety / legal risk |
| Synchronous rebuild on decision | Latency melt |
| Unlimited idempotency retention | Cost explosion |
| Mutable “fix counter” without audit | Unexplainable delivery |

### 5.11 Progressive scale deep dive

**1× (~20K decisions/s)**  
Single Redis; CapSvc co-located with decision; PG rules; nightly recon sample.

**10×**  
Pack keys; at-cap cache TTL 1–5s; separate impression workers; stream log.

**100×**  
Cell by subject hash; home write; regional decision pods; hard-cap reserve tokens with 30–60s TTL; automated drift repair.

**1,000×**  
Soft caps: count-min sketch / bloom tier for long windows; hard caps remain exact on dedicated store; edge prefilter; hierarchical campaign rollups for reporting only (not serving SoT).

### 5.12 Security & privacy

- Cap APIs internal-only; player hits Impression with auth tokens.  
- Do not expose “why blocked” detail to client.  
- Counter keys use opaque ids.  
- Retention aligned with ads policy; TTL windows.

### 5.13 Rollout

```text
Shadow enforce → % traffic enforce soft → enforce hard → default on
Compare: predicted blocks vs actual; over_cap_ppm dashboards
Instant rollback: config version revert / feature flag
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Check placement | Filter stage in ad decision |
| Hot store | Packed Redis counters keyed by subject |
| Durable SoT | Impression event log + recon |
| Idempotency | `impression_id` SETNX |
| Hard vs soft | Fail-closed vs fail-open on uncertainty |
| Hierarchy | Creative / line / campaign / category |
| Cross-device | Best-effort; most restrictive |

### 6.2 Risks

1. Over-cap under decision/impression races  
2. Read amplification regressions from bad key design  
3. Identity gaps → over-show on new devices  
4. Misclassified soft/hard rules  
5. Reconciler silent lag  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: eligibility filter; hierarchy; impression vs bid |
| 5–15 | Check + increment APIs; idempotency |
| 15–25 | Key design + latency math (3M ops trap) |
| 25–35 | Fail-open/closed; multi-region home |
| 35–45 | Scale jumps; pacing coupling; traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Product semantics

**Q: Cap on decision or impression?**  
A: Enforce using counts of **impressions** (or viewable impressions). Checking without incrementing on delivery under-enforces.

**Q: Why hierarchical?**  
A: Brand may want campaign ≤3/day while creative ≤1/day; category legal caps sit above advertisers.

**Q: Soft vs hard?**  
A: Hard = safety/legal/contract; soft = optimization preference with degrade rules.

### 7.2 Consistency

**Q: Can we over-cap?**  
A: Yes under concurrency; state PPM budget. Reservations tighten.

**Q: Exactly-once increments?**  
A: Idempotency key + single apply path; at-least-once beacons safe.

**Q: Read replica lag?**  
A: May under-block (over-show). Hard caps may force home read.

### 7.3 Windows

**Q: Calendar vs rolling?**  
A: Calendar cheap (key suffix date). Rolling needs buckets or event lists — see rolling-window sibling.

**Q: Timezone?**  
A: Policy TZ (e.g. account home or UTC). Document; don’t mix.

### 7.4 Identity

**Q: Household cap?**  
A: Optional subject; most restrictive across linked subjects for some categories.

**Q: Logged-out?**  
A: Device subject; explain weaker guarantees.

### 7.5 Store

**Q: Why not Postgres INCR?**  
A: Decision QPS and multi-get latency; use OLTP for rules/config, not hot counters.

**Q: Redis loss?**  
A: Rebuild from log; interim fail policy by class.

### 7.6 Ops

**Q: Lowering N mid-flight?**  
A: Immediate eligibility uses new N; counts unchanged.

**Q: Pause creative?**  
A: Separate from caps (inventory eligibility); both filter.

### 7.7 Privacy

**Q: Can advertisers read per-user counts?**  
A: No — aggregates only.

**Q: GDPR delete?**  
A: Delete/anonymize subject keys; rebuild exclusions.

### 7.8 Auction interaction

**Q: Does cap change bids?**  
A: Usually filter before auction; don’t silently reprice.

**Q: Empty pod after caps?**  
A: Upstream must have fallback house ads / skip pod policy — product decision.

### 7.9 Cross-region travel

**Q: User flies NY → LON?**  
A: Subject home follow or query home; short lag possible.

### 7.10 Interview traps

**Q: “Just use a Bloom filter”?**  
A: Blooms for “seen” approximate; hard caps need exact counts or known error bounds + fail-closed policy.

**Q: “Global lock per user”?**  
A: Kills decision throughput.

**Q: “Increment in the decision service synchronously for reserve forever”?**  
A: Leaked reserves starve campaigns; need TTL.

### 7.11 Metrics that matter

**Q: What do you page on?**  
A: Hard-cap fail-open rate >0; over_cap_ppm above budget; check p99 burn; idempotency store saturation.

### 7.12 Comparison

**Q: vs web cookie frequency caps?**  
A: Server-side authenticated profile caps are stronger; CTV/device graph harder.

**Q: vs email unsubscribe frequency?**  
A: Similar counters; ads path much hotter and latency-tighter.

---

## 8. Appendices

### A1. Counter key schema

```text
# Packed hash
key:  fcap:{subject_id}:{window_id}
field: {scope_type}:{scope_id} → count

# window_id examples
day:2026-08-06
flight:{campaign_id}
hour:2026-08-06T15Z
```

### A2. Rule schema

```text
CapRule {
  rule_id,
  scope_type: CREATIVE|LINE|CAMPAIGN|CATEGORY,
  scope_id,
  subject_type: PROFILE|DEVICE|HOUSEHOLD,
  limit_n,
  window: {type, length, tz},
  hardness: HARD|SOFT,
  version,
  state: ACTIVE|PAUSED
}
```

### A3. Impression event

```text
ImpressionEvent {
  impression_id, // ULID
  subject_id,
  profile_id,
  device_id?,
  creative_id, line_item_id, campaign_id,
  category_ids[],
  ts_server,
  viewability,
  decision_id,
  caps_config_version
}
```

### A4. Launch checklist

- [ ] Hard vs soft matrix signed by ads + policy  
- [ ] Idempotency TTL ≥ max window + grace  
- [ ] Rebuild from log tested  
- [ ] Fail-closed path chaos-tested  
- [ ] Over-cap PPM dashboards + pages  
- [ ] Key packing load test at 2× peak  
- [ ] Shadow enforce completed  

### A5. Glossary

| Term | Meaning |
|------|---------|
| Cap subject | Identity the counter attaches to |
| Hard cap | Must not violate; fail closed on uncertainty |
| Soft cap | Preference; may fail open |
| Packed key | Multiple scopes under one Redis hash |
| Over-cap PPM | Violations per million impressions |
| House ad | Fallback fill when paid inventory blocked |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| Cap on bid | Caps track delivery |
| One blended QPS | Split check vs incr |
| Active-active INCR without policy | Drift / double count |
| Client SoT | Abuse + inconsistency |
| Ignore hierarchy | Category legal gaps |

### A7. Reliability test plan

1. Duplicate impression_id → count +1 once.  
2. Redis timeout + hard category → block.  
3. Redis timeout + soft → allow + alert.  
4. Rebuild counters from log → match within tolerance.  
5. Lower N below current → immediate block.  
6. Burst 100 decisions / 1 impression slot → measure over-cap; add reserve if needed.

### A8. 60-second summary

> Frequency capping is a **low-latency eligibility filter** over **hierarchical counters** keyed by profile (subject). We **MGET packed keys** at decision, **idempotently INCR** on viewable impressions, keep an **event log to rebuild**, **fail closed** on brand-safety uncertainty, and scale by packing, caching at-cap, subject cells, and optional reservations — never by locking or scoring caps in SQL on the hot path.

### A9. Related systems map

```text
Ad Decision → Freq Cap Service → Counter Store
Impression Service → Counter Store + Event Log → Reconciler
Ads Config → Rules Cache
Identity → subject resolution
Pacing Service → parallel eligibility filter
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Cap check p99 | < 15ms |
| Availability (check) | 99.9% (with policy degrade) |
| Hard fail-open rate | 0 |
| Over-cap PPM (hard) | < 10 |
| Increment durability ACK | 99.99% within 1s |

### A11. Worked numeric example

```text
Campaign K: limit 3 impressions / profile / day
User u has count 2
Decision includes creative C under K → ALLOW
Impression fires → count 3
Next decision same day → BLOCK at campaign scope
Creative-level limit 1 would have blocked earlier if creative already shown
```

### A12. Pseudo-SQL for rules (config only)

```sql
CREATE TABLE cap_rules (
  rule_id UUID PRIMARY KEY,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  subject_type TEXT NOT NULL,
  limit_n INT NOT NULL CHECK (limit_n >= 0),
  window_type TEXT NOT NULL,
  window_length_sec INT,
  tz TEXT,
  hardness TEXT NOT NULL,
  version BIGINT NOT NULL,
  state TEXT NOT NULL
);
```

### A13. Ownership

| Concern | Owner |
|---------|-------|
| Cap service + counters | Ads Serving |
| Impression definition | Ads Measurement |
| Hard category taxonomy | Policy / Legal + Ads |
| Identity links | Identity Platform |
| Reporting aggregates | Ads Data |

### A14. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Check + incr + idempotency + hard/soft policy |
| 10× | Packed keys, pipelines, at-cap cache |
| 100× | Subject homes, recon, optional reserve |
| 1,000× | Approx soft tier, edge prefilter, hard-cap isolation |

### A15. Comparison to naive design

| Naive | Why it fails |
|-------|--------------|
| SQL `UPDATE counts` | Latency + contention |
| Global campaign counter only | Not per-user frequency |
| Cookie on device only | Cross-device / CTV gaps; spoofing |
| Nightly batch cap update | Multi-hour over-show |

### A16. On-call cheat sheet

1. Check `fail_open_rate` for HARD rules (must be ~0).  
2. Check Redis CPU/memory and pipeline p99.  
3. Verify latest `caps_config_version` rollout.  
4. If over_cap_ppm spike: enable reserves / cut decision concurrency / freeze bad clients.  
5. If under-delivery: watch fail-closed too aggressive or sticky at-cap cache.

### A17. Sample decision debug record (sampled)

```text
{
  "decision_id": "...",
  "subject_id": "p_123",
  "caps_config_version": 8841,
  "blocked": [
    {"candidate": "cr_9", "scope": "campaign:k_1", "count": 3, "limit": 3, "rule": "r_77"}
  ]
}
```

### A18. Interaction with presentation order

Frequency caps ≠ creative sequencing. Sibling: presentation-order tracking. Both may apply: e.g. max 3/day and not twice back-to-back.

### A19. Cost worksheet

```text
mem_GB ≈ active_keys × 64B × repl / 1e9
redis_nodes ≈ max(mem/mem_per_node, peak_pipeline_ops / ops_per_node)
cap_svc_pods ≈ peak_decisions × cpu_ms_per_dec / (1000 × cores × util)
```

### A20. Explicit non-goals

- Replacing brand safety classifiers  
- Being the billing system of record (measurement sibling owns money truth)  
- Guaranteeing 0 over-cap under network partitions without availability tradeoffs  

---

*End of document — Netflix system design interview prep: Ad Frequency Capping.*
