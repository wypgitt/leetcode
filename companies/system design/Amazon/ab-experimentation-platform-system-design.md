# System Design: A/B Experimentation Platform

> **Focus areas:** Sticky assignment · Layer / namespace mutual exclusion · Metrics stream & aggregation · Experiment ownership & approvals · QA overrides · Holdouts · Exposure logging · SRM detection  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes (assign vs expose vs metrics), explicit invariants, Amazon themes (practicality, reliability, ownership, business trade-offs)

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

Goal: **bound the product**—what “experiment” means at Amazon scale, how assignment sticks, how mutually exclusive experiments share traffic, how metrics become trustworthy decisions, and who owns launch/kill authority.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who is the unit of randomization? | Customer id (logged-in), cookie/device id (anon), sometimes session or seller id | Assignment key type per experiment; salt + hash; sticky mapping |
| F2 | Where does assignment happen? | Edge/BFF and mid-tier services that render treatment (homepage, search, checkout, ads) | Low-latency Assignment Service; SDK + config snapshot; not a chatty DB round-trip every render |
| F3 | Sticky assignment? | Yes for duration of experiment; same unit → same variant unless override | Deterministic hash preferred; optional persisted overrides for QA / forced |
| F4 | Mutually exclusive experiments? | Yes—overlapping UX changes must not collide (e.g. two homepage redesigns) | **Layers / namespaces** with traffic partitions; orthogonal domains can overlap |
| F5 | Metrics? | Exposure → downstream business metrics (orders, conversion, latency, returns) | Exposure log + metrics stream join; offline stats jobs + near-real-time dashboards |
| F6 | Experiment lifecycle? | Draft → review → running → paused → completed → archived | State machine in control plane; audit every transition |
| F7 | Ownership? | Owning team + oncall; secondary reviewers for customer-impacting launches | IAM + approval workflow; “two-pizza” ownership of experiment + alerts |
| F8 | QA overrides? | Force employee / test accounts into a variant without polluting analysis | Override store with TTL; analysis exclusion flags; never rely on cookie alone |
| F9 | Targeting / eligibility? | Marketplace, locale, Prime status, device, percentage rollouts | Eligibility evaluated before assignment; targeting rules versioned |
| F10 | Holdouts / long-term measurement? | Global or domain holdouts for incremental value | Reserved buckets in layer; holdout experiments as first-class |
| F11 | Ramp / kill switch? | Gradual % ramp; instant disable on guardrail breach | Config push < minutes; client SDK caches with version + TTL |
| F12 | Analysis contract? | CUPED / sequential testing optional; SRM detection required | Separate Analysis plane; assignment ≠ analysis authority |
| F13 | Multi-armed / bandits? | Nice-to-have later; classic A/B first | Defer adaptive allocation; keep assignment deterministic in MVP |
| F14 | Cross-platform consistency? | Web + mobile + Alexa should get same treatment when keyed by customer | Shared Assignment Service; same salt/layer config |
| F15 | Interaction with feature flags? | Experiments *are* a class of flags with scientific constraints | Reuse flag delivery; add exposure logging + analysis invariants |

**MVP functional scope (lock with interviewer):**

1. Create experiment with variants, traffic %, layer, targeting, primary + guardrail metrics.
2. **Assignment API/SDK**: given `(unit_id, context)` → set of active treatments (variant ids + parameters).
3. **Deterministic sticky assignment** within layer; mutually exclusive via layer traffic allocation.
4. **Exposure logging** (who saw what, when, experiment version).
5. **Metrics pipeline**: ingest business events; join to exposures; aggregate daily (and near-RT counters).
6. **QA / employee overrides** with analysis exclusion.
7. **Ownership**: owner team, approvers, oncall; audit log for config changes.
8. **Kill switch / ramp** via config version publish.
9. Basic **SRM** (sample ratio mismatch) alerts.

**Out of MVP (explicitly defer):**

- Full multi-armed bandit / contextual bandits with continuous reallocation
- Perfect real-time causal inference dashboards with CUPED for every team on day 1
- Cross-experiment interaction modeling for all pairs (combinatorial explosion)
- Client-side-only assignment without server authority for commerce-critical paths
- Exactly-once metrics with zero late data (document late-arrival windows)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Assignment latency? | On page/API critical path | p50 < 5ms in-region (cached config), p99 < 20ms; SDK local eval preferred |
| N2 | Availability of assign? | Must not take down retail | Fail-open to **control** (or last-known-good) with hard safety; never 5xx the storefront for experiment outage |
| N3 | Stickiness correctness? | Same unit → same variant for experiment life | Deterministic hash; overrides explicit |
| N4 | Mutual exclusion? | No two exclusive exps share a unit | Layer partition invariant; validated at publish |
| N5 | Metrics freshness? | Decision quality > vanity RT | Daily trusted tables T+1; guardrail near-RT < 15 min lag |
| N6 | Durability of exposures? | Needed for science + audit | At-least-once to durable log; dedupe in analysis |
| N7 | Config propagation? | Ramp/kill | p99 < 60s global for kill; < 5 min normal ramp |
| N8 | Throughput? | See scale table | Split **assign QPS**, **expose QPS**, **metric event QPS**, **config publish QPS** |
| N9 | Cost? | Amazon cares | Prefer local SDK eval over central RPC at 1M+ QPS; sample exposures if needed |
| N10 | Compliance / PII? | Customer ids in logs | Tokenize / hash where possible; retention policies; access controls |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Owner creates experiment in layer `homepage`, 50/50, targets US desktop → reviewers approve → publish → Assignment SDK evaluates → user sees treatment B → exposure logged → orders stream joins → dashboard shows lift.
2. QA forces `customer_id=alice` into variant B via override → alice sees B → exposure marked `override=true` → excluded from primary analysis.
3. Guardrail (checkout latency p99) breaches → auto or manual kill → config version N+1 disables treatment → clients refresh → traffic to control.
4. Two experiments in same layer: A gets 20%, B gets 30%, remainder control pool—no unit in both A and B.
5. Orthogonal layers: `search_ranking` and `checkout_button_color` both assign independently.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Assignment service down | SDK uses cached snapshot; default control; alert owners |
| Config publish partial (some regions old) | Version fencing; sticky within version epoch; monitor skew |
| Unit flips variant mid-experiment due to salt change | **Forbidden** without explicit restart; salt immutable after start |
| Layer over-allocated (>100%) | Publish rejected; invariant check |
| Exposure lost / duplicated | At-least-once + dedupe key `(unit, exp, day)` or event id |
| Metric events without exposure | Not in ITT population; optional intent-to-treat vs exposure-aware |
| Anonymous → login identity merge | Policy: stick to first key or re-hash with care; document; avoid silent flip |
| SRM detected | Alert; pause analysis trust; investigate bot/traffic skew / broken eligibility |
| Override forgotten | TTL on overrides; weekly sweep; owner notifications |
| Employee traffic pollutes | Auto-exclude `@amazon` / internal CIDRs via exclusion rules |
| Hot experiment on homepage (100% of traffic evaluates) | Local eval mandatory; central assign melts at retail QPS |
| Late metrics (returns after 30 days) | Analysis windows; cumulative tables; don’t close experiment day-1 forever |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Concurrent running experiments | 500 | 5K | 50K | 500K |
| Layers / namespaces | 50 | 200 | 1K | 5K |
| Peak **assignment evaluations**/s | 200K | 2M | 20M | **200M** |
| Peak **exposure events**/s | 50K | 500K | 5M | 50M |
| Peak **metric events**/s | 100K | 1M | 10M | 100M |
| Distinct units assigned / day | 50M | 200M | 500M | 1B+ |
| Config publishes / day | 1K | 10K | 50K | 200K |
| Analyst dashboard queries / day | 10K | 50K | 200K | 1M |
| Regions / marketplaces | 5 | 10 | 20 | 20+ |

**What each jump forces:**

- **10×:** Move from central Assignment RPC to **SDK + config CDN/snapshot**; Kafka for exposures; warehouse daily jobs.
- **100×:** Layer isolation, shuffle-sharded config, exposure sampling policies, near-RT guardrails on Flink/Spark Streaming, multi-region config fanout.
- **1,000×:** Cell/marketplace partitioning, hierarchical layers, approximate unique counts, experiment metadata sharded, analysis capacity planning per org, strict cost budgets on full-fidelity logging.

### 1.5 Etc. (Constraints & Assumptions)

- Retail / Search / Ads / Devices all call the same conceptual platform with different SLAs.
- Experiment **parameters** (JSON) ship with assignment (feature values), not only variant letters.
- Business metrics owned by data domain teams; experimentation platform owns **assignment + exposure + join keys + stats framework**.
- We are not redesigning the entire data lake—we integrate.

**Scope statement:**

> Design an Amazon-scale A/B experimentation platform: sticky deterministic assignment with mutually exclusive layers, low-latency SDK evaluation, QA overrides, ownership/approvals, durable exposure + metrics pipelines, and trustworthy analysis—with explicit fail-open behavior so experiment infra never takes down the storefront—baseline ~200K assign evals/s scaling toward ~200M.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not merge)

| Class | What | Baseline | 1,000× | Latency | Notes |
|-------|------|----------|--------|---------|-------|
| **Assign evaluate** | SDK/local or RPC: which variants? | 200K/s | 200M/s | Critical path | Dominates; must be local |
| **Exposure emit** | Log that unit saw treatment | 50K/s | 50M/s | Async OK | Can sample / batch |
| **Metric events** | Orders, clicks, latency | 100K/s | 100M/s | Async | Existing commerce streams |
| **Config fetch** | SDK refresh snapshot | 5K/s | 500K/s | Soft real-time | CDN + versions |
| **Control plane CRUD** | Create/approve/publish | ~10/s | ~1K/s | Human | Strong consistency OK |
| **Analysis queries** | Dashboards / notebooks | bursty | bursty | Seconds–minutes | Warehouse |

**Anti-pattern:** designing a single “Experiment QPS = 200K” RPC that also writes exposures synchronously.

### 2.2 Why local SDK eval is mandatory

```text
Central Assignment Service at 200K QPS:
  200K × 2 KB response ≈ 400 MB/s egress — doable but wasteful
At 20M QPS (100×): 40 GB/s — absurd for “which button color?”

Local eval:
  Config snapshot ~5–50 MB compressed per app (filtered to relevant layers)
  Hash(unit_id, salt) → bucket — microseconds CPU
  Network for assign ≈ 0 on hot path
```

### 2.3 Deterministic assignment math

```text
bucket = hash64(unit_id + experiment_salt) % 10000   # 0.01% granularity
if bucket in [start, end) → treatment

Sticky without storage: same inputs → same output forever
Storage only for: overrides, holdout membership audits, debug
```

### 2.4 Layer mutual exclusion math

```text
Layer "homepage" traffic = 100% of eligible units
Experiment A: 0–1999   (20%)
Experiment B: 2000–4999 (30%)
Control pool: 5000–9999 (50%)  # may still be used by holdouts

Invariant: intervals disjoint; sum ≤ 10000
Orthogonal layer "checkout" has independent hash salt → independent assignment
```

### 2.5 Exposure storage

```text
Exposure event ~200–400 B (ids, versions, timestamps, context dims)
50K/s × 300 B ≈ 15 MB/s ≈ 1.3 TB/day
50M/s × 300 B ≈ 15 GB/s ≈ 1.3 PB/day → MUST sample / compact / tier

Strategy:
  - Full fidelity for money paths + small experiments
  - Sampled exposures for ultra-high-traffic with known power needs
  - Daily rollups keyed by (exp, variant, dims...) for dashboards
```

### 2.6 Metrics join cost

```text
Orders: say 10M/day baseline → trivial vs exposures
Clicks: 5B/day at large scale → join exposures↔clicks on unit+time window
Warehouse: partition by day; sort-merge join; late data +1–2 day buffer
```

### 2.7 Config fanout

```text
10K app hosts × refresh every 30s = ~333 fetches/s — CDN easy
Kill switch: push pub/sub invalidate → refetch within 60s p99
Version monotonic: clients never apply older version than seen (except pin)
```

### 2.8 Override store size

```text
Overrides: employees + QA + support tools
Even 10M active overrides × 100 B = 1 GB — DynamoDB/Redis fine
TTL typically hours–days; not permanent without approval
```

### 2.9 Analysis warehouse

```text
Trusted daily table: ~billions of exposure rows compacted
Stats job per experiment: minutes on Spark
500K experiments: can't full-scan each — index by exp_id partitions; on-demand compute
```

---

## 3. High-Level Design

### 3.1 Planes (separate concerns)

```text
┌─────────────────────────────────────────────────────────────────┐
│ CONTROL PLANE                                                    │
│  Experiment Registry · Approvals · Layers · Ownership · Audit   │
└────────────────────────────┬────────────────────────────────────┘
                             │ publish config versions
┌────────────────────────────▼────────────────────────────────────┐
│ DATA PLANE (Assignment)                                          │
│  Config CDN / Snapshots · SDK Evaluator · Override Store · Kill │
└────────────────────────────┬────────────────────────────────────┘
                             │ exposures (async)
┌────────────────────────────▼────────────────────────────────────┐
│ METRICS / ANALYSIS PLANE                                         │
│  Exposure Log · Metrics Streams · Joiner · Stats · SRM · UI     │
└─────────────────────────────────────────────────────────────────┘
```

**Amazon ownership note:** Control plane owned by Experimentation Platform team; SDKs embedded in product teams; metrics join contracts shared with Data Engineering; oncall for kill path is platform + experiment owner.

### 3.2 Core components

| Component | Responsibility | Store |
|-----------|----------------|-------|
| **Experiment Registry** | CRUD experiments, variants, metrics, targeting | SQL (Aurora) strong consistency |
| **Layer Manager** | Traffic intervals, mutual exclusion validation | SQL + versioned config |
| **Approval / Ownership Service** | Owners, reviewers, SIM/TT integration | SQL + IAM |
| **Config Builder / Publisher** | Compile running experiments → immutable snapshot | S3 + CloudFront / internal CDN; DynamoDB version pointer |
| **Assignment SDK** | Local evaluate eligibility + hash + overrides | In-process; periodic refresh |
| **Assignment Edge API** (optional) | For clients that can't embed SDK (IoT, 3P) | Stateless + Redis override cache |
| **Override Service** | QA / employee force variant | DynamoDB (`unit#exp` → variant, TTL) |
| **Exposure Collector** | Receive batched exposures | Kafka / Kinesis |
| **Metrics Ingest** | Tap existing order/click streams | Kafka |
| **Join / Feature Store jobs** | Build exposure→metric fact tables | Spark / Flink → S3 / Redshift / Lake |
| **Stats Engine** | Lift, CI, SRM, guardrails | Batch + streaming monitors |
| **Experiment Console** | UI for owners | Reads registry + analysis APIs |

### 3.3 APIs (sketch)

**Control plane**

```text
POST   /v1/layers
POST   /v1/experiments
PATCH  /v1/experiments/{id}          # draft only
POST   /v1/experiments/{id}/submit   # request approval
POST   /v1/experiments/{id}/approve
POST   /v1/experiments/{id}/publish  # allocates layer slots + builds config
POST   /v1/experiments/{id}/ramp     # { percent }
POST   /v1/experiments/{id}/pause
POST   /v1/experiments/{id}/kill     # emergency → control
GET    /v1/experiments/{id}
GET    /v1/experiments/{id}/audit
```

**Assignment / overrides**

```text
# SDK local — preferred
evaluate(unit_id, unit_type, context) → TreatmentSet

# Edge API — fallback
POST /v1/assign  { unit_id, unit_type, context, client_id }
→ { treatments: [{exp_id, variant_id, params, config_version}], exclusions? }

PUT  /v1/overrides { unit_id, exp_id, variant_id, ttl_sec, reason, requester }
DELETE /v1/overrides/{unit_id}/{exp_id}
```

**Exposure**

```text
POST /v1/exposures:batch
[
  { exposure_id, unit_id, exp_id, variant_id, config_version,
    ts, context_dims, override:bool, app, request_id }
]
```

### 3.4 Data models

**Experiment (control plane)**

```text
Experiment {
  exp_id, name, owner_team, oncall, state,
  layer_id, salt,              # salt immutable after RUNNING
  unit_type,                   # CUSTOMER | DEVICE | SELLER | ...
  targeting_rules_version,
  variants: [{ variant_id, name, params_json, traffic_weight }],
  primary_metrics[], guardrail_metrics[],
  start_at, end_at, ramp_percent,
  analysis_exclusions[],       # employees, overrides
  created_by, approved_by[], config_version
}
```

**Layer**

```text
Layer {
  layer_id, name, domain,      # homepage | search | checkout | ads
  total_buckets: 10000,
  allocations: [{ exp_id, start, end, state }],  # disjoint
  holdout_reserved: [{ name, start, end }]
}
```

**Override**

```text
Override {
  pk: unit_id, sk: exp_id,
  variant_id, reason, requester, expires_at, created_at
}
```

**Exposure event**

```text
Exposure {
  exposure_id, unit_id, unit_type, exp_id, variant_id,
  config_version, ts, marketplace, device, override,
  request_id, session_id?
}
```

### 3.5 Assignment algorithm (deterministic)

```text
function evaluate(unit, context, snapshot, overrides):
  results = []
  for layer in snapshot.layers relevant to context.app:
    if override = overrides.get(unit, layer.experiments):
       results += forced; continue

    # Independent hash per layer (or per experiment within allocated range)
    b = hash64(unit.id + layer.salt) % 10000
    exp = layer.allocation_containing(b)  # may be null → no exp in layer
    if exp is null: continue
    if not eligible(unit, context, exp.targeting): continue

    # Variant split inside experiment's bucket range (re-hash or sub-range)
    vb = hash64(unit.id + exp.salt) % exp.total_weight
    variant = exp.variant_for(vb)
    results.append(Treatment(exp, variant, exp.params))
  return results
```

**Why hash over DB mapping:** O(1), sticky, no storage melt, multi-region consistent, cheap.

**When to persist assignment:** debugging, legal holds, non-hashable custom segments, migration—not default path.

### 3.6 Mutual exclusion: layers vs global mutex

| Approach | How | Pros | Cons | When |
|----------|-----|------|------|------|
| **Layers / namespaces** | Domain partitions traffic | Simple, scalable, orthogonal overlap OK | Owners must pick correct layer | **Default (Amazon-like)** |
| Global exclusive locks | One experiment per user globally | Strong isolation | Kills parallel innovation | Almost never |
| Pairwise exclusion lists | Exp A excludes B | Flexible | Graph conflicts; hard to validate | Rare special cases |
| Traffic contracts | Team buys % of layer | Org economics | Political + metering | Large orgs at 100× |

**Deal-breaker:** allowing two homepage redesigns in the same layer without disjoint buckets—analysis becomes garbage and UX can break.

### 3.7 Metrics pipeline design

```text
App → Exposure Collector → Kafka topic `exposures`
Commerce → Kafka `orders`, `page_views`, `clicks`, `latency_samples`
                ↓
         Stream join (near-RT guardrails):
           exposure ⊕ order within attribution window
                ↓
         Lakehouse daily:
           fact_exposure_daily
           fact_metric_by_exp_variant_daily
                ↓
         Stats Engine → Experiment Console
```

**Attribution window:** e.g. order within 24h/7d/30d of first exposure—product choice; store multiple windows.

**ITT vs exposure-aware:** Intent-to-treat uses assignment (even if UI failed to show); exposure-aware uses logged exposure. Amazon interview: **call this out**—prefer ITT for decision integrity when assignment is server-side; exposure for debugging delivery.

### 3.8 Trade-off tables

| Decision | Option A | Option B | Choose | Deal-breaker if wrong |
|----------|----------|----------|--------|------------------------|
| Assignment | Central RPC | Local SDK + snapshot | **SDK** at retail QPS | Storefront coupled to experiment RPC |
| Stickiness | DB map | Deterministic hash | **Hash** | DB becomes hotspot; flips on migration |
| Mutex | Ad-hoc flags | Layers | **Layers** | Confounded experiments |
| Exposures | Sync write | Async log | **Async** | Assign latency / availability hit |
| Fail mode | Fail-closed (no page) | Fail-open control | **Fail-open control** | Retail outage from science tool |
| Analysis | Only RT counters | Trusted daily + RT guardrails | **Both** | Premature launches on noisy RT |
| Overrides | Cookie only | Server override store | **Server** | QA flakes; security holes |
| Config | Per-request SQL | Versioned immutable snapshot | **Snapshot** | Inconsistent assign mid-flight |

### 3.9 Why DynamoDB / Kafka / SQL where

| Data | Choice | Why |
|------|--------|-----|
| Experiment metadata | Aurora/Postgres | Strong transactions for layer allocation + approvals |
| Config snapshots | S3 + CDN | Huge fanout, immutable, cheap |
| Version pointer | DynamoDB / etcd | Fast `current_version` per app cell |
| Overrides | DynamoDB | TTL, key-value, multi-AZ, spiky QA |
| Exposures / metrics | Kafka/Kinesis | Durable buffer, replay, consumer fanout |
| Analysis tables | S3 + Spark/Redshift | Scan-friendly, cheap at PB |
| Hot guardrail counters | Redis / Flink state | Seconds–minutes freshness |

### 3.10 Ownership model (Amazon flavor)

```text
Experiment Owner Team
  - Creates, ramps, monitors primary metrics
  - Oncall for treatment bugs / rollback
Platform Team
  - Assignment correctness, SDK, pipeline SLOs
  - Layer governance, capacity of layers
Data Science / Decision Science (optional central)
  - Stats methodology, CUPED, review for high-risk
Approvers
  - UX / legal / privacy for customer-impacting
```

**Publish checklist (automated):** layer capacity, salt frozen, metrics registered, SRM monitors wired, kill switch tested, owner + secondary oncall present.

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                    ┌──────────────────────┐
   Owners / UI ────►│ Experiment Console   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Control Plane        │
                    │ Registry·Layers·IAM  │──► Audit Log
                    │ Approvals·Publisher  │
                    └──────────┬───────────┘
                               │ put snapshot vN
                    ┌──────────▼───────────┐
                    │ Config Store (S3)    │◄── CDN / Snap Distribution
                    └──────────┬───────────┘
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌─────────────┐     ┌─────────────┐      ┌──────────────┐
   │ Web BFF SDK │     │ Search SDK  │      │ Devices API  │
   │ evaluate()  │     │ evaluate()  │      │ (edge assign)│
   └──────┬──────┘     └──────┬──────┘      └──────┬───────┘
          │                   │                    │
          │         ┌─────────▼─────────┐          │
          └────────►│ Override Service  │◄─────────┘
                    │ (DynamoDB + cache)│
                    └─────────┬─────────┘
                              │
                         exposures
                              ▼
                    ┌───────────────────┐
                    │ Kafka exposures   │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   Near-RT Guardrails   Lake Ingest          Replay/Backfill
   (Flink + Redis)      (S3/Iceberg)         (ops)
         │                    │
         ▼                    ▼
   Alerts / Kill hook   Daily Stats Jobs ──► Console Analysis
                              ▲
                              │
                    Kafka orders/clicks/...
```

### 4.2 Layer allocation view

```text
Layer HOME_US buckets 0..9999
|--[ HOLD_OUT 0..499 ]--|--[ EXP_A 500..2499 ]--|--[ EXP_B 2500..5499 ]--|--[ FREE 5500..9999 ]--|
         5%                      20%                      30%                      45%
```

### 4.3 Request path (happy)

```text
Request → Auth (customer_id) → BFF
  → SDK.evaluate(customer_id, {mp:US, device:web})
      → load snapshot vN (memory)
      → check override cache (negative cached)
      → hash layers → treatments
  → render with params
  → async batch exposure
```

### 4.4 Kill switch path

```text
Guardrail alert / owner → POST /kill
  → Registry state=KILLED
  → Publisher builds vN+1 (exp removed / forced control)
  → Pub/sub invalidate
  → SDKs refetch ≤60s
  → Optional: edge “emergency control” flag in Redis for <5s blast radius
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants (write these on the whiteboard)

1. **Determinism:** For fixed `(unit_id, exp_salt, config_version semantics)`, variant is stable for the experiment lifetime (absent explicit override).
2. **Layer disjointness:** No unit bucket belongs to two RUNNING experiments in the same layer.
3. **Salt immutability:** Changing salt after start is a **new experiment** (or explicit restart with warning).
4. **Fail-open to control:** Assignment failures must not error customer pages.
5. **Exposure at-least-once; analysis deduped.**
6. **Overrides excluded from primary analysis** by default.
7. **Kill is faster than ramp:** emergency path bypasses slow approvals (with audit).

#### 5.1.2 Data loss prevention

| Data | Loss impact | Mitigation |
|------|-------------|------------|
| Accepted publish | Wrong traffic | Multi-AZ SQL; publish TX allocates layer + writes snapshot pointer atomically |
| Snapshot | Clients stuck on old | Multi-replica S3; immutable versions; never overwrite vN |
| Exposures | Biased science | Kafka multi-AZ; acks; disk buffer on collector; replay |
| Overrides | QA confusion | DynamoDB multi-AZ; critical overrides also in snapshot side-channel if needed |

#### 5.1.3 Idempotency & dedupe

```text
exposure_id = ulid/uuid from client
Kafka key = unit_id (partition affinity)
Analytics: DROP DUPLICATE on exposure_id
Override PUT idempotent by (unit_id, exp_id)
Publish: idempotency-key on approve/publish to avoid double allocation
```

#### 5.1.4 Retries & circuit breakers

- SDK → Override Service: timeout 5–10ms, **fail skip override** (use hash), circuit break after errors; negative cache.
- Exposure collector: local disk/memory queue; drop with metric if overflow (prefer drop exposures over blocking checkout).
- Config refresh: exponential backoff; keep last-known-good forever until replaced.

#### 5.1.5 Consistency model

| Concern | Model |
|---------|-------|
| Layer allocation | Strong (SQL TX) |
| Assignment across fleet during publish | Eventual (<60s); accept brief mixed versions |
| Analysis | Eventually complete with late windows |
| Overrides | Read-after-write for setter; others eventual via cache TTL |

**Mixed versions during ramp:** two users may be on vN and vN+1 briefly—OK if each version internally consistent. Sticky hash ensures a user doesn't flip variant when version only changes ramp of *other* experiments; when *their* experiment ramps, bucket ranges change carefully (expand/contract from edges).

#### 5.1.6 Ramp without flip

```text
Safe expand: grow treatment interval into FREE pool only
Unsafe: reshuffle entire layer → mass variant flips → bad UX + invalid analysis
If must reshuffle: end experiment, start new with new salt
```

#### 5.1.7 SRM & trust

Sample Ratio Mismatch: expected 50/50 but observed 48/52 → broken eligibility, bots, logging bugs, CDN caching personalized HTML wrongly.

**Response:** auto-flag experiment untrusted; page owners; optionally auto-pause.

#### 5.1.8 Security

- Control plane: IAM, MFA for kill/publish on high-tier.
- Overrides: only privileged roles; audited; rate-limited.
- Snapshots: signed; SDK verifies signature to prevent tampering.
- PII: prefer opaque customer id; restrict raw log access.

---

### 5.2 Scalability

#### 5.2.1 Traffic ups and downs

| Pattern | Approach |
|---------|----------|
| Prime Day / holiday assign spikes | SDK local eval scales with app fleet; no central bottleneck |
| Exposure surge | Kafka autoscale; sampling; collector load shed |
| Config stampede on publish | Stagger refresh jitter; CDN; version gossip |
| Analysis stampede Monday AM | Precompute daily facts; cache console aggregates; WLM queues |

#### 5.2.2 Progressive evolution

**Baseline → 10×**

- Aurora registry; S3 snapshots; SDK in major surfaces.
- Kafka exposures; nightly Spark joins.
- DynamoDB overrides.
- Single region control plane; multi-region snapshot fetch.

**10× → 100×**

- Filter snapshots **per application** (only relevant layers) to keep size small.
- Near-RT Flink for guardrails.
- Layer capacity governance (teams reserve %).
- Exposure compaction / columnar lake (Iceberg).
- Multi-region active control with **single-writer home** for layer allocation (or per-marketplace registries).

**100× → 1,000×**

- Marketplace/cell isolation (US vs EU data residency).
- Hierarchical layers (team → domain).
- Adaptive sampling of exposures based on power analysis.
- Stats engine with experiment-partitioned compute; avoid global scans.
- Edge assignment for non-SDK clients via Anycast + heavy caching.
- Cost showback per owning team for exposure volume.

#### 5.2.3 Consistent hashing / sharding uses

| Key | Maps to |
|-----|---------|
| `unit_id` | Kafka partition for exposures (ordering per unit) |
| `exp_id` | Analysis job shard / stats partition |
| `layer_id` | Governance & config fragment |
| `marketplace` | Data residency cell |
| Override `unit_id` | DynamoDB partition key |

#### 5.2.4 Hot keys

- Celebrity customers don't hot-key assignment (hash is CPU).
- Hot **experiments** (homepage) hot-key analysis partitions → shard by `(exp_id, day, variant)` and pre-aggregate.
- Override service hot employee lists → cache in SDK snapshot for bulk “all employees in B” via rule, not per-id rows.

#### 5.2.5 Storage growth controls

```text
Raw exposures: retain 7–90 days hot; cold archive; rely on daily aggregates forever
Metric grains: keep (exp, variant, day, marketplace, device) — not per-user forever in RT store
Per-user assignment history: optional debug sample, not 100% permanent
```

---

### 5.3 Maintainability

#### 5.3.1 Multi-team ownership

- **Platform** SLOs: SDK crash-free, config freshness, exposure durability, kill latency.
- **Product team** SLOs: treatment quality, metric movement, rollback.
- Clear RACI in experiment console (Owner, Approver, Platform oncall).

#### 5.3.2 Deploy & SDK versioning

- SDK is a library—breaking changes need dual-read of config schema (`schema_version`).
- Config builder emits backward-compatible snapshots for N-1 SDK.
- Canary: publish experiment to internal employees layer first.

#### 5.3.3 Observability

| Signal | Why |
|--------|-----|
| `assign_eval_latency` | SDK CPU / override fetch |
| `config_age_seconds` | Stale treatment risk |
| `exposure_drop_rate` | Science integrity |
| `version_skew` across fleet | Publish health |
| `srm_pvalue` | Trust |
| `guardrail_breach` | Customer experience |
| `layer_utilization` | Capacity planning |
| `override_active_count` | Hygiene |

**Logs:** structured treatment decisions sampled (1/N) with `request_id` for support debug—not 100% at 200M/s.

#### 5.3.4 Testing

- Determinism tests: fixed golden vectors for hash→bucket.
- Layer allocator property tests: no overlaps, sum ≤ capacity.
- Chaos: kill Override Service → assign still works.
- Publish integration: dual-running shadow evaluation.

#### 5.3.5 Business trade-offs (say out loud)

| Trade-off | Amazon framing |
|-----------|----------------|
| Science purity vs feature velocity | Layers + approvals balance |
| Logging cost vs analysis power | Sample with power calculator |
| Fail-open control vs missing treatment | Customer experience > experiment |
| Fast RT dashboards vs trusted T+1 | Guardrails RT; decisions T+1 |
| Global consistency of config vs kill speed | Prefer fast kill; accept brief skew |

---

## 6. Wrap-Up

### 6.1 Interview narrative (2–3 minutes)

> “I'd split the system into control, assignment, and analysis planes. Assignment must be a **local SDK** with deterministic hashing inside **layers** so mutually exclusive experiments can't overlap, while orthogonal domains stay independent. Stickiness comes from immutable salts—not a giant assignment database. QA uses a DynamoDB override path excluded from analysis. Exposures and commerce metrics flow through Kafka into lakehouse joins; near-real-time is for guardrails, trusted decisions are daily with SRM checks. If assignment infra fails, we **fail open to control** so we never take down retail. Ownership is explicit: product teams own treatments and metrics; platform owns invariants, kill speed, and pipeline SLOs.”

### 6.2 What to emphasize for Amazon

1. **Customer experience first** — experiment outage ≠ website outage.
2. **Ownership** — every running experiment has a team + oncall + audit.
3. **Operational kill / ramp** — minutes matter; practice it.
4. **Cost** — don't RPC-assign at retail QPS; don't log PB/day blindly.
5. **Correctness of science** — mutex layers, SRM, exclusion of overrides.
6. **Practical MVP** — classic A/B + layers before bandits.

### 6.3 What interviewers poke

- “User logs in and flips variant?” → identity merge policy.
- “Two experiments both change checkout?” → same layer / exclusion.
- “How do you know logging is broken?” → SRM + pipeline SLOs.
- “Would you store all assignments in Redis?” → no need; hash; Redis for overrides/guardrails only.
- “Exactly-once exposures?” → at-least-once + dedupe; don't overclaim.

---

## 7. Deeper / Related Interview Questions

### 7.1 Assignment & hashing

**Q: Why not random() per request?**  
A: Not sticky; confounds metrics; UX flips. Use seeded hash.

**Q: MD5 vs SipHash vs Murmur?**  
A: Need uniform, stable, fast. Avoid cryptographic cost unless adversarial. Document chosen hash; golden tests.

**Q: 10000 buckets vs 100?**  
A: Finer ramp (0.01%). Memory negligible.

**Q: How to do 1% ramp safely?**  
A: Allocate 100 contiguous buckets from FREE; expand contiguously.

**Q: Consistent hashing for assignment?**  
A: Usually modulo buckets is enough. Consistent hashing more relevant for sharding Kafka/analysis—not variant pick.

**Q: Salt per experiment or per layer?**  
A: Layer salt for mutex bucket; experiment salt for variant split. Both immutable after start.

### 7.2 Layers & exclusion

**Q: Can search and homepage share a layer?**  
A: Only if treatments must be exclusive. Else orthogonal layers maximize velocity.

**Q: Who polices layer capacity?**  
A: Platform governance + automated reject on overbook; optional reserved quotas per org.

**Q: Interactive effects between orthogonal layers?**  
A: Real but accepted; high-risk pairs can use exclusion lists or dedicated combined experiments.

**Q: Holdout vs control?**  
A: Control is within experiment; holdout is long-running reserved bucket measuring portfolio incremental value.

### 7.3 Overrides & QA

**Q: Cookie `force_exp=B` enough?**  
A: No—spoofable, inconsistent across devices, pollutes if logged wrong. Server-side override + exclusion flag.

**Q: How do internal dogfood launches work?**  
A: Targeting rule `employee=true` or dedicated employee layer; still logged with exclusion.

**Q: Support wants to show customer their treatment?**  
A: Debug API with authz; show exp/variant/config_version; don't require raw hash knowledge.

### 7.4 Metrics & analysis

**Q: Exposure without impression (prefetch)?**  
A: Define exposure = user-visible. Log from client viewport or server render that was sent.

**Q: Triggered analysis vs intent-to-treat?**  
A: Triggered (among exposed) can bias if exposure correlates with outcome. Discuss; often ITT on assigned.

**Q: Network effects / marketplace interference?**  
A: Seller experiments may need marketplace-level randomization or careful clustering—call out bias.

**Q: CUPED?**  
A: Covariate adjustment using pre-period metrics; reduces variance; analysis-plane feature.

**Q: Sequential testing / peeking?**  
A: Peeking inflates false positives; use always-valid CIs or fixed horizons; educate owners.

**Q: Primary metric multiple?**  
A: Prefer one primary; guardrails separate; multiple primaries need multiple-testing correction.

### 7.5 Data systems

**Q: Why Kafka not write exposures to DynamoDB?**  
A: Append-heavy, replay, fanout to many consumers; Dynamo expensive and awkward for scans.

**Q: Why SQL for registry not Dynamo?**  
A: Multi-row invariants (layer intervals) need transactions; low QPS.

**Q: Redis for config?**  
A: Possible for small; S3+CDN better for large snapshots and global fanout.

**Q: Iceberg/Hive tables?**  
A: ACID-ish lake partitions for daily facts; time-travel for reprocessing.

**Q: Flink vs Spark for joins?**  
A: Flink near-RT guardrails; Spark/batch for trusted daily science.

### 7.6 Indexing & storage

**Q: Index for console “my experiments”?**  
A: SQL `(owner_team, state, updated_at)`.

**Q: Partition exposures how?**  
A: By `day` then `exp_id` (or marketplace first for residency).

**Q: Cardinality explosion in dashboards?**  
A: Pre-aggregate allowed dims; block arbitrary high-cardinality group-bys in UI.

### 7.7 Load balancing & edge

**Q: Edge assignment API LB?**  
A: Anycast/RLB to regional cells; sticky not required (deterministic). Cache overrides at edge with short TTL.

**Q: SDK in browser?**  
A: Possible for UI; commerce-critical may still server-evaluate to prevent tampering.

### 7.8 Failure modes

**Q: Snapshot poison (bad config)?**  
A: Signed + schema validate + canary fleet + instant rollback to vN-1 pointer.

**Q: Clock skew on exposure ts?**  
A: Prefer server receive time + client ts; analysis uses receive_day with late buffers.

**Q: Partial marketplace publish?**  
A: Per-marketplace version pointers; don't require global atomicity.

**Q: Duplicate publish allocates twice?**  
A: Idempotency key + conditional TX on layer version.

### 7.9 Algorithms

**Q: How to detect SRM?**  
A: Chi-square / binomial test on observed vs expected variant counts; alert below threshold.

**Q: Power analysis for sample size?**  
A: Based on baseline rate, MDE, significance, traffic; platform can estimate runtime.

**Q: Stratified assignment?**  
A: Hash within strata or post-stratify in analysis; keep it simple in MVP.

**Q: Thompson sampling bandits?**  
A: Adaptive allocation breaks classic fixed-horizon stats; separate product mode with different guarantees.

### 7.10 Amazon business / org

**Q: Who gets paged for SRM?**  
A: Experiment owner primary; platform if systemic pipeline SRM across many exps.

**Q: Cost of a bad experiment?**  
A: Customer experience regression, revenue loss—hence guardrails + kill > perfect science latency.

**Q: Why not one mega-experiment framework in Excel?**  
A: Scale, mutex, audit, SDK distribution, trust—platform pays for itself in avoided foot-guns.

### 7.11 Identity

**Q: Guest checkout then login?**  
A: Policy matrix: keep guest assignment for session; post-login use customer_id going forward; analysis may segment. Don't silently rewrite history.

**Q: Household shared device?**  
A: Device id experiments blur users; prefer customer id when authenticated.

**Q: GDPR deletion?**  
A: Exposures keyed by customer id subject to deletion pipelines; aggregates retained.

### 7.12 API / SDK design

**Q: Return all experiments or only matching?**  
A: Only relevant treatments + params needed to render; avoid huge payloads.

**Q: Param packing?**  
A: JSON params in snapshot; SDK returns merged config for variant.

**Q: Feature flag unification?**  
A: Flags without science; experiments with exposure+metrics. Same delivery rails, different constraints.

### 7.13 Multi-region

**Q: Active-active registry?**  
A: Risky for layer TX. Prefer home-region writer + global snapshot replicas; or shard by marketplace.

**Q: Cross-region user travel?**  
A: Assignment follows unit_id hash—same worldwide if same snapshot salts; targeting may exclude.

### 7.14 Performance budgeting

**Q: Override check every request too slow?**  
A: Bloom filter / negative cache; bulk employee rules in snapshot; override path only when bit set.

**Q: Hash CPU at 200M evals/s?**  
A: Trivial vs JSON parse / render; microbenchmark anyway.

### 7.15 Interview traps

**Q: “Store assignment in MySQL for every user”**  
A: At 1B units × many exps → insane write/read. Hash.

**Q: “Analysis in the assign path”**  
A: Never block checkout on science.

**Q: “100% exact real-time lift”**  
A: Late data, returns, attribution—be honest.

**Q: “Mutex by checking Redis set of experiments per user”**  
A: Hot key + consistency pain; layers are cleaner.

**Q: Units arithmetic**  
A: 50K exp/s × 300 B = 15 MB/s ≈ **1.3 TB/day**, not PB—know when sampling becomes mandatory (closer to 50M/s).

### 7.16 Reliability drills

**Q: GameDay ideas?**  
A: (1) Poison snapshot rollback (2) Kafka exposure delay → SRM? (3) Override service down (4) Kill switch timing under load (5) Layer double-allocate attempt rejected.

### 7.17 Comparison

**Q: vs LaunchDarkly / internal feature flags?**  
A: Flags optimize delivery; experimentation adds layers, exposures, stats, SRM, analysis exclusions, scientific lifecycle.

**Q: vs Google Analytics experiments / client-only?**  
A: Client-only weaker for Amazon commerce integrity; server/SDK authority preferred.

### 7.18 Memory & footprint

**Q: Snapshot memory per host?**  
A: Filter to app-needed layers; e.g. 5–20 MB. Full global 500K exps may be hundreds of MB—don't ship all to every host.

**Q: How to filter?**  
A: Publisher builds `app_id → snapshot` fragments; hosts subscribe to their fragment.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- layers
CREATE TABLE layers (
  layer_id UUID PRIMARY KEY,
  name TEXT UNIQUE,
  domain TEXT,
  total_buckets INT NOT NULL DEFAULT 10000,
  row_version BIGINT NOT NULL
);

-- layer_allocations
CREATE TABLE layer_allocations (
  layer_id UUID,
  exp_id UUID,
  start_bucket INT,
  end_bucket INT, -- exclusive
  state TEXT,
  PRIMARY KEY (layer_id, exp_id),
  CHECK (start_bucket >= 0 AND end_bucket <= 10000 AND start_bucket < end_bucket)
);

-- experiments
CREATE TABLE experiments (
  exp_id UUID PRIMARY KEY,
  layer_id UUID REFERENCES layers,
  name TEXT,
  owner_team TEXT,
  oncall TEXT,
  state TEXT,
  unit_type TEXT,
  salt TEXT NOT NULL,
  ramp_percent INT,
  targeting_json JSONB,
  primary_metrics JSONB,
  guardrail_metrics JSONB,
  config_version BIGINT,
  created_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ
);

-- variants
CREATE TABLE variants (
  exp_id UUID,
  variant_id TEXT,
  name TEXT,
  weight INT,
  params JSONB,
  PRIMARY KEY (exp_id, variant_id)
);

-- approvals / audit
CREATE TABLE experiment_audit (
  id BIGSERIAL PRIMARY KEY,
  exp_id UUID,
  actor TEXT,
  action TEXT,
  payload JSONB,
  at TIMESTAMPTZ
);
```

```text
DynamoDB Overrides
  PK: UNIT#<unit_id>
  SK: EXP#<exp_id>
  attrs: variant_id, reason, requester, expires_at
  TTL: expires_at
```

### 8.2 Exposure & metrics topics

```text
exposures.v1          key=unit_id
orders.v1             key=order_id / customer_id
page_views.v1
guardrail_metrics.v1  # pre-aggregated latency etc.
config_versions.v1    # pub/sub invalidation
```

### 8.3 Invariants tests

| Test | Assert |
|------|--------|
| Layer allocate | No overlapping intervals; sum ≤ total |
| Salt freeze | Update salt on RUNNING → rejected |
| Determinism | 100k random units stable across SDK versions N/N+1 for unchanged exps |
| Kill | Within 60s >99% hosts on version without treatment |
| Override exclude | Analysis job drops `override=true` |
| Fail-open | Override timeout → hash path; no exception to caller |
| Idempotent publish | Same idempotency key → same allocation |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Registry + hash assign SDK + Kafka exposures + daily join + overrides |
| 10× | CDN snapshots, app-filtered config, SRM, approvals |
| 100× | Near-RT guardrails, layer quotas, lakehouse compaction, multi-marketplace |
| 1000× | Cells, sampling policies, cost showback, hierarchical governance |

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| Layer / namespace | Mutual exclusion domain with bucketized traffic |
| Salt | Immutable hash seed for sticky assignment |
| Exposure | Record that a unit actually saw a treatment |
| Holdout | Long-running reserved traffic for incremental measurement |
| SRM | Sample Ratio Mismatch — observed ≠ expected traffic split |
| Guardrail | Non-primary metric that can block/kill (latency, defect rate) |
| ITT | Intent-to-treat analysis based on assignment |
| Fail-open control | On errors, serve default/control experience |
| Config version | Monotonic snapshot id applied by SDKs |

### 8.6 Estimation cheat-sheet

```text
Assign eval @ retail: MUST be local (CPU hash)
Exposure bytes/day ≈ QPS × 86400 × avg_bytes
50K × 86400 × 300 ≈ 1.3e12 B ≈ 1.3 TB/day
Config hosts × refresh_hz ≈ fetch QPS (use CDN)
Override active size ≈ count × 100 B
Kill SLO: pointer flip + pubsub + refetch ≤ 60s p99
```

### 8.7 Assignment SDK pseudocode

```text
class ExperimentSdk:
  snapshot: Snapshot
  override_cache: Cache

  def refresh():
    v = fetch_pointer()
    if v > snapshot.version:
      snapshot = fetch_and_verify(v)

  def evaluate(unit, ctx):
    try:
      return _eval(unit, ctx)
    except Exception:
      metrics.increment("assign_failopen")
      return TreatmentSet.control_only()

  def _eval(unit, ctx):
    out = []
    for layer in snapshot.layers_for(ctx):
      o = override_cache.get(unit.id, layer)
      if o: out.append(o); continue
      b = hash64(unit.id + layer.salt) % 10000
      exp = layer.find(b)
      if not exp or not exp.eligible(unit, ctx): continue
      var = exp.pick_variant(unit.id)
      out.append(Treatment(exp.id, var.id, var.params, snapshot.version))
    return out
```

### 8.8 Analysis exclusion rules

```text
exclude if any:
  - override == true
  - employee / internal traffic tag
  - bot score > threshold
  - marketplace not in experiment target (logging bug)
  - config_version < experiment.start_version (pre-start noise)
```

### 8.9 Kill / ramp state machine

```text
DRAFT → IN_REVIEW → APPROVED → RUNNING ⇄ PAUSED → COMPLETED → ARCHIVED
                         ↘ KILLED (terminal-ish; can clone to new exp)
```

### 8.10 Interview “say this” (60 seconds)

> Local SDK deterministic assignment in mutually exclusive layers; S3 versioned config; DynamoDB QA overrides excluded from analysis; Kafka exposures joined to commerce metrics; RT guardrails + T+1 trusted stats with SRM; fail-open to control; clear owner/oncall for every experiment; kill in under a minute.

### 8.11 Related systems map

```text
Feature Flags ──shared delivery──► Experimentation Platform
Commerce Event Bus ──metrics──► Analysis Plane
Identity Service ──unit_id──► Assignment SDK
Observability ──guardrails──► Kill Switch
IAM / Approvals ──control──► Registry
```

### 8.12 Business decision log (examples)

| Decision | Choice | Cost / risk acknowledged |
|----------|--------|---------------------------|
| Fail-open | Control | Miss treatment during outages |
| Async exposures | Prefer UX | Some loss under extreme shed |
| Daily trusted stats | Not RT decisions | Slower iteration |
| Layers | Manual domain choice | Mis-layered interactions |

### 8.13 Reliability test plan

1. Double-allocate layer → TX fail.  
2. Override service blackhole → assign continues.  
3. Poison snapshot → signature fail → stay on LKG.  
4. Duplicate exposure ids → analysis counts once.  
5. SRM injection (drop 10% variant B logs) → alert fires.  
6. Kill under Prime-Day-like eval rate → p99 < 60s.  

### 8.14 Observability SLOs

| SLO | Target |
|-----|--------|
| SDK eval p99 (local) | < 5ms |
| Config freshness p99 | < 60s (kill), < 5m (normal) |
| Exposure durable success | > 99.9% (pre-sampling) |
| Guardrail pipeline lag | < 15 min |
| Trusted daily table | Ready by 08:00 local |

### 8.15 FAQ quick hits

| Question | Answer |
|----------|--------|
| Persist all assignments? | No—hash |
| Central assign service? | Only for non-SDK clients |
| Bandits in MVP? | No |
| Who owns kill? | Owner can; platform can force |
| Cross-device sticky? | Needs customer_id login |

---

*End of A/B experimentation platform system design.*
