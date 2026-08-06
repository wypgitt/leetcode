# System Design: Fake-Review Detection (Amazon Marketplace)

> **Focus areas:** Trust & Safety · Review integrity · Feature platform · ML scoring · Human review queues · Enforcement · Adversarial sellers · Feedback loops · Explainability · Progressive scale  
> **Style:** End-to-end marketplace integrity design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split online vs nearline vs offline planes, correct QPS/label math, precision/recall & customer-trust tradeoffs, deal-breakers for “one classifier” or “human-review everything”  
> **Interview theme:** Amazon SDE III / L6 — protect **customer trust** in ratings & reviews while owning reliability, cost, and operational accountability (two-pizza ownership)

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

Goal: **bound the product**—a **fake-review detection** platform that scores reviews (and related entities) for inauthenticity, routes uncertain cases to Trust & Safety (T&S) humans, enforces suppress/remove/seller actions with auditability, and continuously improves via labeled feedback—without destroying legitimate customer voice or seller livelihoods.

### 1.0 What this is / is not

| Dimension | **Fake-review detection (this doc)** | Not this |
|-----------|--------------------------------------|----------|
| Primary job | Detect incentivized, fabricated, coordinated, or otherwise inauthentic reviews | Moderate product quality opinions (“this broke in a week”) |
| Success | High-precision removal of fake signal; preserve helpful genuine reviews | 100% recall of every shady review |
| Entity | Review, reviewer, ASIN/product, seller/brand, order, campaign/cluster | Single keyword blocklist |
| Planes | Online score at submit + nearline graph + offline train | Nightly batch-only bans |
| Enforcement | Suppress ranking, hide, remove, throttle submit, seller/account actions | Silent permanent shadowban of all disputed reviews |
| Adversary | Review farms, seller incentives, VPN/proxy rings, AI-generated text | One-off angry customer |
| Amazon lens | Customer trust, Seller Central fairness, cost of human review, ownership | Academic NLP paper accuracy alone |

**Scope statement:** Design Amazon marketplace fake-review detection: event ingestion, feature store, multi-tier ML + rules scoring, human queues, enforcement (suppress/remove), appeals/feedback loops, adversarial robustness, explainability for T&S, progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a “fake” review? | Inauthentic: paid, incentivized without disclosure, fabricated purchase, coordinated campaigns, bot/AI farms | Multi-signal authenticity score, not sentiment |
| F2 | When do we score? | At submit (online) + continuous re-score (nearline) as new graph signals arrive | Dual-plane architecture |
| F3 | Entities beyond review text? | Reviewer account, order/Verified Purchase, ASIN, brand/seller, IP/device, social graph of reviewers | Entity-resolution + graph features |
| F4 | Verified Purchase required? | Strong signal but not sufficient (incentivized VP exists) | Soft feature, not hard gate |
| F5 | Enforcement actions? | Suppress in sort, hide from PDP, remove, block submit, seller warnings/suspension hooks | Policy engine + audit log |
| F6 | Human review? | Yes for borderline / high-impact (top ASINs, seller disputes) | Queue prioritization by risk × impact |
| F7 | Seller/customer appeals? | Yes — wrong removals destroy trust and create tickets | Decision IDs, reason codes, reversible actions |
| F8 | Real-time vs eventual? | Submit path must be fast; campaign detection can be minutes–hours | Latency tiers |
| F9 | Multi-marketplace / locale? | Start one marketplace; design for multi-locale text + policy packs | Locale-aware models; shared entity IDs |
| F10 | Explainability? | T&S needs reason codes; do not hand attackers a full feature dump | Dual explain views |
| F11 | Feedback labels? | Human verdicts, appeals overturns, seller investigations, honeypots, customer reports | Closed training loop |
| F12 | Content moderation overlap? | Hate/PII/illegal content is adjacent but separate | Call content mod; don’t conflate |
| F13 | Rating-only (no text)? | Yes — star gaming without text | Behavioral/graph features dominate |
| F14 | Images/video in reviews? | MVP: text+stars+meta; media hashing later | Extensibility hook |
| F15 | Cross-ASIN campaigns? | Yes — brand attacks / boost rings across catalog | Graph clustering |

**MVP functional scope:**

1. Ingest **review lifecycle events** (create, edit, delete, helpful votes, reports).  
2. Join **order/VP**, account, device/IP, seller/ASIN context into a feature snapshot.  
3. **Online score** at submit: rules + lightweight ML → allow / soft-suppress / hold-for-review / hard-block.  
4. **Nearline** re-score + **campaign/cluster** detection (shared devices, templates, burst patterns).  
5. **Enforcement orchestrator**: suppress ranking, hide, remove; emit audit events.  
6. **T&S human queues** with prioritization, SLAs, dual-control for high-impact.  
7. **Appeals / overturn** path feeding labels.  
8. **Metrics**: precision on removals, customer/seller complaint rate, time-to-detect campaigns, cost per review.  
9. **Explainability** packages for agents (reason codes + top features).  
10. Hooks to Seller Central investigations and account integrity.

**Out of MVP:**

- Perfect detection of all offline cash-for-review meetings  
- Public “authenticity score” API for third-party sites  
- Replacing all content moderation (hate, NSFW, etc.)  
- Real-time global graph query on every keystroke of review drafting  
- Automatic permanent seller bans without human/policy escalation for gray cases

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Submit-path score latency | Inline with review post | p99 < 50–100ms (async enrich OK) |
| N2 | Availability of thin path | Prefer degrade to allow+nearline | 99.99% allow-path; never lose ingest |
| N3 | Nearline campaign lag | Minutes–hours | Hot campaigns < 15–60 min; bulk < 24h |
| N4 | Throughput | Marketplace review volume | See scale table |
| N5 | Precision on hard remove | Very high (customer voice) | Sampled ≥ 95–99% depending on action severity |
| N6 | Recall on known farms | Improve over time | Tiered: high-precision auto; high-recall queue |
| N7 | Human review capacity | Cost-bounded | Priority queues; auto for clear cases |
| N8 | Audit / compliance | Immutable decision trail | decision_id, actor, policy version |
| N9 | Model freshness | Adversarial drift | Weekly+ retrain; hot rule deploy < hours |
| N10 | Cost | Own unit economics | $/1K reviews scored; human minutes budget |
| N11 | Multi-AZ / region | Marketplace regional | Region-local scoring; global entity links |
| N12 | Privacy / least privilege | Reviewer PII protected | Purpose-limited access; retention TTLs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Genuine customer with VP posts review → low risk → publish immediately; appears in PDP sort.  
2. Clear template spam from known farm IPs/devices → high score → auto-remove + audit.  
3. Borderline incentivized language on mid-volume ASIN → soft-suppress from “top reviews”; enqueue T&S.  
4. Brand-attack burst (many 1★ in 2 hours, shared proxies) → nearline cluster → suppress campaign; escalate sellers/investigations as policy dictates.  
5. Seller appeals a removal → agent sees reason codes → overturn → republish + label for training.  
6. Customer reports “this looks fake” → signal into feature store; may bump priority, not sole evidence.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Viral product launch (real burst) | Fast velocity ≠ fake; calibrate by category/ASIN baselines + purchase funnel |
| Honest negative reviews on defective batch | Protect negative genuine voice; don’t over-weight seller complaints |
| Verified Purchase + cash incentive | VP is weak alone; text/incentive cues + reviewer graph |
| AI-generated fluent fakes | Style models + behavioral/graph; don’t rely on grammar fails |
| Reviewer writes 1 review/year (cold start) | Lean on order/device/IP/ASIN priors; avoid over-penalizing new reviewers |
| Shared household / family device | Soft device edges; multi-user accounts |
| VPN / corporate NAT | IP weak; combine with device + behavior |
| Edit-after-publish laundering | Re-score on edit; version history features |
| Helpful-vote manipulation | Separate vote-integrity signals feeding rank suppress |
| Model outage | Rules + allow with nearline catch-up; page “provisional” flags internal |
| Label poisoning via bad agent / malicious appeals | Dual review sampling; honeypot gold set; agent QA |
| Cross-border review farms | Locale features + global reviewer identity graph |
| High-ASIN (bestseller) impact | Raise human review threshold; dual-control for mass suppress |
| Seller self-reviews via sock puppets | Order graph + payment instrument clustering (careful privacy) |
| Competitor writing negatives | Same detection stack; investigation workflow for coordinated harm |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Reviews created / day | 5M | 50M | 500M | 5B |
| Peak review creates / s | 200 | 2K | 20K | 200K |
| Review edits / day | 1M | 10M | 100M | 1B |
| Online scores / s | 250 | 2.5K | 25K | 250K |
| Feature reads / s | 2K | 20K | 200K | 2M |
| Nearline re-scores / day | 20M | 200M | 2B | 20B |
| Clusters proposed / day | 5K | 50K | 500K | 5M |
| Auto suppress/remove / day | 50K | 500K | 5M | 50M |
| Human review tasks / day | 20K | 50K (budgeted) | 80K (heavy auto) | capacity-capped |
| Active ASINs with reviews | 100M | — | — | catalog growth |
| Model versions in prod | 5 | 15 | 40 | per-locale/category cells |
| T&S agents (global) | 500 | 800 | 1.2K | efficiency via tooling |

**What each jump forces:**

- **10×:** Stronger feature caching; async enrichment; queue prioritization by ASIN impact.  
- **100×:** Sharded feature store; category/locale model cells; auto-enforcement for high-precision bands; human review only for high impact × uncertainty.  
- **1,000×:** Hierarchical campaign detection; streaming graph approx; edge decision tokens; heavy investment in weak-label learning + active learning to keep humans constant-ish.

### 1.5 Etc. (Constraints & Assumptions)

- **Customer trust > vanity metrics:** wrong removals of genuine negatives are existential for marketplace trust.  
- **Sellers are customers too:** enforcement must be explainable enough for fair process; avoid opaque mass punishment.  
- Fake reviews are an **economic attack** — raise cost of fakery, cut ROI, not only classify text.  
- Attackers adapt (templates → paraphrases → AI → residential proxies) — assume **adversarial ML**.  
- Ownership: one service owns **decision + audit**; PDP/rankers consume enforcement state.  
- Prefer **mechanisms over meetings**: policy-as-config, measurable SLOs, clear pager ownership.

**Scope statement to repeat back:**

> Design a fake-review detection system for Amazon marketplace: ingest review and entity events, score authenticity online and nearline with features + ML + rules, detect coordinated campaigns, enforce suppress/remove with audited decisions, route uncertain high-impact cases to T&S humans, close the loop with appeals/labels, and scale 10×/100×/1,000× while optimizing for customer trust, precision, cost, and operational ownership.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| A — Online submit score | Sync path on review create/edit | 200–250 rps | 2–2.5K rps | Online |
| B — Feature hydration | KV/feature store gets per score | ~2K rps | ~20K rps | Online |
| C — Event ingest | Review + order + account + device streams | ~1–5K events/s | 10–50K/s | Streaming |
| D — Nearline re-score | Graph/campaign triggered | tens of M/day | hundreds of M/day | Nearline |
| E — Human review | Agent tasks | ~20K/day | capacity-capped | Ops |
| F — Training / batch | Features + labels daily | PB-scale logs | — | Offline |

**Interview tip:** Never quote one “QPS” number. Split **submit**, **enrichment**, **nearline**, and **human** planes—they scale differently and fail differently.

### 2.2 Storage rough math (baseline)

| Data | Volume assumption | Size | Notes |
|------|-------------------|------|-------|
| Review body | 5M/day × 500 B avg | ~2.5 TB/year raw | Compression + object store for cold |
| Review metadata | 5M/day × 300 B | ~0.5 TB/year | OLTP / KV |
| Feature snapshots | 5M/day × 2 KB | ~3.6 TB/year | Or columnar feature log |
| Decision/audit log | 5M/day × 400 B | ~0.7 TB/year | Immutable, long retention |
| Graph edges (reviewer–device–ASIN) | 50M edges/day × 50 B | ~0.9 TB/year | Nearline store |
| Model artifacts | tens of GB | small | Versioned registry |

**Hot store:** last N days of reviews + enforcement state for PDP (cache-friendly).  
**Cold:** S3/Glacier-class for raw text & training.

### 2.3 Bandwidth & fanout

- PDP read path should **not** call the ML scorer. It reads **enforcement state** (cached): `visibility`, `rank_eligible`, `flags`.  
- Scoring fanout per review: ~10–30 feature gets (batchable) + 1 model infer + rules.  
- Campaign job: seed 10K suspicious reviewers → expand 2–3 hops → re-score 100K–1M reviews.

### 2.4 Latency budget (online submit)

| Step | Budget |
|------|--------|
| Auth + validate review payload | 5–10 ms |
| Feature fetch (batched, cached) | 15–40 ms |
| Rules + model inference | 5–20 ms |
| Decision write + enqueue async | 5–15 ms |
| **Total p99 target** | **≤ 50–100 ms** |

If enrichment is slow: **optimistic publish** with `provisional=true` internal flag + nearline finalize within seconds–minutes (product choice—discuss with interviewer). Amazon flavor: prefer not showing clearly fake reviews even briefly on high-impact ASINs → for those, **hold** instead of optimistic publish.

### 2.5 Human review economics

| Item | Estimate |
|------|----------|
| Agent handle time | 60–180 s / task |
| 20K tasks/day × 2 min | ~667 agent-hours/day |
| Cost pressure | Auto-resolve high-precision band; humans on uncertain × high GMV ASINs |
| 100× reviews | Humans cannot scale linearly → active learning + higher auto threshold confidence |

### 2.6 Precision / recall framing (say this out loud)

| Action | Precision need | Recall need | Rationale |
|--------|----------------|-------------|-----------|
| Rank suppress (still visible if sorted) | Medium-high | Medium | Lower customer harm |
| Hide from default PDP | High | Medium | Trust impact |
| Hard remove | Very high | Lower OK | False remove of genuine negative is severe |
| Seller suspension hook | Extreme + human | Campaign-level | Livelihood / legal |

### 2.7 Scale jump implications (math intuition)

| Jump | Reviews/day | Online rps | If naïve humans | Reality |
|------|-------------|------------|-----------------|---------|
| Base | 5M | 250 | 20K tasks | OK with triage |
| 10× | 50M | 2.5K | 200K tasks | Impossible → more auto |
| 100× | 500M | 25K | 2M tasks | Cells + hierarchical detect |
| 1,000× | 5B | 250K | — | Streaming approx graphs; humans as QA |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Customer trust first:** minimize false removals of authentic reviews, especially negatives.  
2. **Seller fairness:** audited, appealable enforcement; consistent policy versions.  
3. **Ownership:** clear service boundaries—Scoring, Enforcement, Queues, Features—each with alarms and runbooks.  
4. **Cost control:** humans are the scarce resource; maximize automated high-precision actions.  
5. **Reliability:** never drop review ingest; degrade scoring gracefully.  
6. **Adversarial durability:** rules + models + graph; expect adaptation.

### 3.2 Core components

| Component | Responsibility | Why separate |
|-----------|----------------|--------------|
| Ingest / Event bus | Review, order, account, device, report events | Decouple producers; replay |
| Entity & Feature platform | Offline/online features, point-in-time correctness | Training-serving skew kills models |
| Online Scoring Service | Sync decision at submit/edit | Latency SLO ownership |
| Nearline Workers | Re-score, clustering, campaigns | Heavy graph off the sync path |
| Policy & Enforcement Orchestrator | Map scores → actions; idempotent apply | Single writer of visibility state |
| Enforcement State Store | Per-review / per-entity flags for PDP/rank | Read-optimized, cached |
| Human Review / Case Service | Queues, SLAs, agent UI backends | Ops tooling ≠ scoring |
| Appeals Service | Overturns, seller/customer flows | Feeds labels |
| Model Platform | Train, validate, deploy, shadow, A/B | Safe rollout |
| Audit & Explain Store | decision_id, reason codes, feature top-k | Compliance + agent UX |
| Abuse Intel / Honeypot | High-precision labels | Poison-resistant gold set |

### 3.3 Primary flows

**Flow A — Review submit (online)**

1. Reviews API validates auth, rate limits, content-mod hooks.  
2. Persist review (or pending) + emit `ReviewCreated`.  
3. Scoring Service fetches features → rules → model → decision.  
4. Enforcement applies: `PUBLISH`, `PUBLISH_SUPPRESSED`, `HOLD`, `REJECT`.  
5. Async: enrich embeddings, update graphs, index for search.

**Flow B — Nearline campaign**

1. Stream aggregates detect bursts / template similarity / device cliques.  
2. Cluster proposal → score distribution → auto actions for high-precision clusters.  
3. High-impact residual → human case with cluster evidence package.

**Flow C — Human decision**

1. Agent opens case → sees explain package (not raw PII dump beyond need).  
2. Verdict → Enforcement + Label Store.  
3. QA samples agent decisions.

**Flow D — Appeal**

1. Customer/seller appeals with `decision_id`.  
2. Re-review → overturn/republish possible.  
3. Overturns are **first-class labels** (high weight for FP analysis).

### 3.4 API sketch (illustrative)

```text
POST /reviews
  → { review_id, visibility, decision_id }

POST /internal/score
  → { score, action, reason_codes[], model_version, policy_version }

POST /enforcement/apply
  { entity_type, entity_id, action, decision_id, actor }

GET  /enforcement/state/{review_id}
  → { visibility, rank_eligible, flags[] }

POST /cases
  { review_ids[], cluster_id?, priority, evidence_ref }

POST /appeals
  { decision_id, claimant, statement }
```

### 3.5 Data model (simplified)

```text
Review: review_id, asin, reviewer_id, order_id?, stars, text_ref, created_at, edit_rev
EnforcementState: review_id, visibility, rank_eligible, suppress_reason, updated_at, decision_id
Decision: decision_id, entity_id, scores{}, reason_codes[], model_version, policy_version, actor
Cluster: cluster_id, member_ids[], score, evidence_ref, status
Case: case_id, priority, queue, status, assignee, sla_at
Label: label_id, entity_id, label, source (agent|appeal|honeypot|report), ts
FeatureSnapshot: entity_id, features{}, ts, feature_version
```

### 3.6 Options & tradeoffs

| Decision | Options | Choose | Why | Deal-breaker alternative |
|----------|---------|--------|-----|--------------------------|
| Sync vs async publish | Always sync score; always async; hybrid by ASIN impact | **Hybrid** | Trust on bestsellers; UX elsewhere | Async-only → fake flashes on PDP |
| One giant model | Monolith DNN vs tiered rules+ML+graph | **Tiered** | Debugability, hotfixes, cost | One model → can’t patch farm overnight |
| Graph DB online | Neo4j-style sync vs preagg features | **Preaggregated features online** | p99 | Sync multi-hop graph on submit → miss SLO |
| Human on all suppresses | All human vs precision bands | **Bands + impact** | Cost | All human → doesn’t scale; all auto → trust incidents |
| Store text in SQL | RDBMS vs object storage | **Meta in DB, body in object store** | Cost/size | Bodies in OLTP → expensive, backup pain |
| PDP calls scorer | Live score vs stored state | **Stored enforcement state** | Reliability/latency | Live ML on PDP → outage = blank ratings |

### 3.7 Scoring architecture (tiered)

```text
Tier 0  Hard rules (blocklisted farms, legal takedown, spam regex)     → instant
Tier 1  Lightweight model (GBDT / compact net) on tabular features    → online
Tier 2  Text / embedding similarity to known fakes                   → online/nearline
Tier 3  Graph / cluster campaigns                                     → nearline
Tier 4  Human review                                                  → uncertain × impact
```

**Calibration:** map scores to actions with **different thresholds per action severity** and per ASIN tier (bestseller vs long-tail).

### 3.8 Feature groups (what interviewers expect)

| Group | Examples | Plane |
|-------|----------|-------|
| Content | n-grams, embedding, incentive phrases, language mismatch, repetition | Online |
| Reviewer | account age, review velocity, category diversity, VP ratio, helpful ratio | Online |
| Order / commerce | VP, order-to-review time, refunds, A-to-z claims, price paid | Online |
| Device / net | device_id clusters, IP rarity, proxy score, ASN | Online |
| ASIN / seller | recent review velocity vs sales, rating spike, seller age, category | Online |
| Graph | shared devices across reviewers, template cliques, burst sync | Nearline |
| Feedback | prior removals, appeal overturns, customer reports | Online/nearline |
| Cross-domain | account integrity risk, payment instrument risk (careful) | Online |

### 3.9 Enforcement ladder

| Severity | Action | Typical trigger |
|----------|--------|-----------------|
| L0 | Monitor / log only | Low score |
| L1 | Suppress from “top / most helpful” | Medium score |
| L2 | Hide from default PDP (available via filter?) | Med-high |
| L3 | Remove / tombstone | High precision |
| L4 | Submit throttle / block new reviews | Reviewer risk |
| L5 | Case for seller/account integrity | Cluster + policy |

Idempotency: enforcement apply is **retry-safe** keyed by `decision_id`.

### 3.10 Failure & degradation modes

| Failure | Degradation |
|---------|-------------|
| Model inference down | Rules-only; widen HOLD for high-impact ASINs |
| Feature store partial | Score with subset; mark `low_confidence`; nearline re-score |
| Queue backlog | Auto high-precision removes continue; raise suppress threshold for humans |
| Event bus lag | Ingest to durable log first; scoring catches up |
| Bad model deploy | Shadow → canary → auto-rollback on FP spike / appeal spike |

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
                        +------------------+
   Customers/Sellers →  |  Reviews API /   |
                        |  Seller Central  |
                        +--------+---------+
                                 |
                                 v
                        +------------------+
                        |  Ingest + Validate|
                        |  (rate limit, mod)|
                        +--------+---------+
                                 |
                 +---------------+---------------+
                 |                               |
                 v                               v
        +----------------+              +------------------+
        | Review Store   |              | Event Bus (Kinesis|
        | meta + text ref|              | / Kafka)         |
        +----------------+              +--------+---------+
                                                 |
           +-------------------------------------+----------------------------------+
           |                     |                         |                        |
           v                     v                         v                        v
   +---------------+     +---------------+        +----------------+      +----------------+
   | Feature       |     | Online Score  |        | Nearline       |      | Train / ETL    |
   | Platform      |---->| Service       |        | Cluster/Rescore|      | Feature Log    |
   | (online KV)   |     +-------+-------+        +--------+-------+      +--------+-------+
   +---------------+             |                         |                       |
                                 v                         v                       v
                        +------------------+      +----------------+      +----------------+
                        | Policy/Enforce   |<-----| Campaign Acts  |      | Model Registry |
                        | Orchestrator     |      +----------------+      | A/B / Shadow   |
                        +--------+---------+                               +----------------+
                                 |
           +---------------------+---------------------+
           |                     |                     |
           v                     v                     v
   +---------------+     +---------------+     +----------------+
   | Enforcement   |     | Audit/Explain |     | Case Queues    |
   | State (cache) |     | Store         |     | (T&S agents)   |
   +-------+-------+     +---------------+     +--------+-------+
           |                                            |
           v                                            v
   +---------------+                            +----------------+
   | PDP / Rankers |                            | Appeals + Labels|
   | read state    |                            +--------+-------+
   +---------------+                                     |
                                                         v
                                                +----------------+
                                                | Feedback to    |
                                                | training       |
                                                +----------------+
```

### 4.2 Online scoring sequence

```text
Client          Reviews API       Feature KV        Scorer           Enforcer         Bus
  |                |                 |                |                 |              |
  |--POST review-->|                 |                |                 |              |
  |                |--get features-->|                |                 |              |
  |                |<--batch feats---|                |                 |              |
  |                |--------------score-------------->|                 |              |
  |                |                 |                |--rules+ML------>|              |
  |                |                 |                |<--action--------|              |
  |                |--apply decision---------------->|--write state---->|              |
  |                |                 |                |                 |--audit------>|
  |                |                 |                |                 |--event------>|
  |<--200 + visibility-------------|                |                 |              |
```

### 4.3 Nearline campaign loop

```text
  Streams → Aggregate (velocity, templates, devices)
                 |
                 v
            Cluster Proposal
                 |
         +-------+--------+
         |                |
         v                v
   High precision     Uncertain × High GMV
   auto enforce            |
         |                 v
         |            Human Case + evidence pack
         |                 |
         +--------+--------+
                  v
            Labels / Appeals → Retrain
```

### 4.4 Cell architecture at 100×+

```text
                  Global Entity Directory (reviewer/seller ids)
                                |
        +-----------------------+-----------------------+
        |                       |                       |
   Cell: NA                  Cell: EU                Cell: APAC
   score + features          score + features        score + features
   local events              local events            local events
        |                       |                       |
        +----------- cross-cell graph edges (async) ----+
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **At-least-once** event processing; enforcement apply **idempotent** on `decision_id`.  
2. Every customer-visible visibility change has an **audit record**.  
3. Online path failure must not **lose** the review write—persist first or dual-write carefully.  
4. Model rollback must be possible without PDP deploy.  
5. Human override beats model for that entity until expiry/policy says otherwise.

#### 5.1.2 Consistency model

- **Review body**: strong consistency on primary store for author read-after-write.  
- **Enforcement state**: strongly consistent per `review_id` (single writer service).  
- **Features**: read-your-writes not required globally; point-in-time snapshots for training.  
- **PDP caches**: TTL + pub/sub invalidation on enforcement change (seconds of staleness OK if bounded).

#### 5.1.3 Failure modes & runbooks

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| Spike in appeals / “my review vanished” | Bad model/threshold | Rollback model; freeze auto-remove |
| Fake campaign visible for hours | Nearline lag / missed aggregate | Page nearline; emergency rules on ASIN |
| Submit p99 blowup | Feature store hot key / model timeout | Shed to rules; cache; hold high-impact only |
| Queue SLA breach | Farm wave | Raise auto precision band; surge staffing; temp suppress-only |
| Training-serving skew | Feature bug | Shadow replay; block promote |

#### 5.1.4 Durability of trust decisions

- Audit log: WORM / append-only, retention per legal (years).  
- Policy version pinned on each decision for later dispute.  
- Soft-delete reviews with tombstones to support appeals republish.

#### 5.1.5 Security & abuse of the detector itself

- Agents: least privilege, audited access to PII.  
- Sellers must not learn exact thresholds (enumeration).  
- Rate-limit report APIs (weaponized mass reporting).  
- Separate “attacker-facing” vs “agent-facing” explanations.

### 5.2 Scalability

#### 5.2.1 Online path scaling

- Stateless scorers behind NLB; horizontal scale on rps.  
- Feature store: keyed by `reviewer_id` / `asin` / `device_id`; cache hot ASINs.  
- Avoid huge text transformer **sync**; use compact models online; large NLP nearline.  
- Batch feature multi-get; collapse to one round trip.

#### 5.2.2 Nearline / graph scaling

| Scale | Technique |
|-------|-----------|
| 10× | Stream window aggregates (Flink); daily connected components on suspect subgraph |
| 100× | Shard graph by entity hash; LSH for template text; approximate clustering |
| 1,000× | Hierarchical: local cliques → global meta-clusters; count-min / HyperLogLog sketches |

#### 5.2.3 Human scalability (the real bottleneck)

- **Priority score** = `f(model_uncertainty, asin_gmV, seller_risk, viral_velocity, customer_reports)`.  
- Active learning: sample for label value, not FIFO.  
- Specialize queues: language, category, seller appeals, brand attack.  
- Dual-control only when action ≥ L3 on tier-1 ASIN or mass cluster (>N reviews).

#### 5.2.4 Multi-tenant marketplaces

- Policy packs per marketplace (JP vs US disclosure norms).  
- Shared reviewer identity across .com/.co.uk where accounts link.  
- Locale text models; shared behavioral models.

#### 5.2.5 Cost levers

| Lever | Effect |
|-------|--------|
| Suppress vs remove | More suppress → fewer appeals, lower severity FP cost |
| Cache features | Cut KV QPS |
| Distill models | Cheaper infer |
| Cold text in S3 | OLTP savings |
| Auto high-precision | Cap headcount |

### 5.3 Maintainability & ownership

#### 5.3.1 Service ownership map (two-pizza)

| Service | Owns | Pager |
|---------|------|-------|
| Review Integrity Scoring | Online/nearline scores, model integration | Scoring SLO, FP spikes |
| Enforcement | Visibility state machine | Wrong visibility / apply bugs |
| Feature Platform | Feature defs, skew monitors | Skew / missing feats |
| T&S Case Manager | Queues, SLAs, agent API | Backlog |
| Model Platform | Deploy/rollback | Bad canary |

#### 5.3.2 Safe model lifecycle

```text
Offline train → offline eval (precision@action) → shadow on live traffic
  → canary 1% → staged % → full
Rollback triggers: appeal rate, sampled FP, seller ticket spike, metric drift
```

- **Shadow mode:** compute new score, don’t enforce; compare.  
- **Champion/challenger** per locale cell.  
- Rules engine supports **hot config** for farm IOCs (hours, not weeks).

#### 5.3.3 Training-serving skew controls

- Same feature code path library for online + offline (or generated).  
- Point-in-time joins for labels (no future leakage—classic interview gotcha).  
- Feature monitoring: null rates, distribution drift (PSI), clock skew.

#### 5.3.4 Explainability for T&S (practical)

Agents need:

1. **Reason codes** (e.g., `DEVICE_CLUSTER_KNOWN_FARM`, `INCENTIVE_LANGUAGE`, `BURST_ASIN_ANOMALY`).  
2. **Top contributing features** (SHAP-style or rule hits)—bounded, human-readable.  
3. **Cluster evidence**: “12 reviews, 3 devices, 2 ASNs, template sim 0.92”.  
4. **What we will NOT show sellers:** exact weights, full neighbor PII, threshold values.

Customer-facing message: generic policy language (“removed for community guidelines”) + appeal link—not a feature dump.

#### 5.3.5 Feedback loops (close them explicitly)

| Source | Use |
|--------|-----|
| Agent verdicts | Strong labels |
| Appeal overturns | FP mining (high priority) |
| Honeypot / purchased test buys | Gold precision set |
| Customer reports | Weak labels; priority boost |
| Re-offense after warn | Risk features |
| Seller investigation outcomes | Cluster labels |

**Poisoning defense:** rate-limit influence of any single agent; honeypot audits; separate eval sets attackers can’t touch.

#### 5.3.6 Adversarial sellers & farms (depth)

Attack patterns and counters:

| Attack | Counter |
|--------|---------|
| Template spam | Fuzzy / embedding similarity; near-dupe clusters |
| Paraphrase / AI text | Behavior + graph dominate; AI-style detectors as one feature |
| Slow drip (1 review/day/account) | Long-window graph; payment/device reuse; ROI economics |
| VP incentivized reviews | Order timing + external incentive phrases + reviewer concentration on seller |
| Competitor smear campaigns | Burst + new accounts + proxy; brand-attack playbooks |
| Helpful vote rings | Vote integrity system input |
| Adaptive threshold probing | Sticky decisions; don’t reveal score; jitter/rate-limit probes |
| Label poisoning via appeals | QA, dual review, fraud on appeal channel |

**Economic framing (Amazon loves this):** detection success = make fake reviews unprofitable vs organic growth.

#### 5.3.7 Latency vs accuracy tradeoffs (say crisply)

| Path | Latency | Accuracy tools | Use |
|------|---------|----------------|-----|
| Online | 50–100 ms | Rules, compact ML, cached aggregates | Gate publish |
| Nearline seconds–hours | Higher | Full NLP, graph, clustering | Fix mistakes, catch campaigns |
| Offline | day | Large retrain, deep analysis | Model improvement |

Product dial: **HOLD** on high-impact ASINs when online confidence low; **PUBLISH_SUPPRESSED** on long-tail to protect UX while nearline runs.

#### 5.3.8 Observability & SLOs

| SLO | Target (example) |
|-----|------------------|
| Online score availability | 99.99% |
| Online p99 latency | < 100 ms |
| Ingest durability | 99.999% (no silent drop) |
| Auto-remove sampled precision | ≥ 98% |
| Appeal overturn rate | < threshold (alarm) |
| Campaign TTD (time to detect) | p50 < 1h for large bursts |
| Queue age p95 | < SLA by queue type |

Dashboards: score distribution, action rates, FP samples, seller tickets, cost/1K reviews, drift.

#### 5.3.9 Privacy & retention

- Minimize PII in feature logs; tokenize device/IP.  
- Retention: raw IP shorter; aggregated features longer.  
- Access: T&S roles; break-glass for fraud ops.  
- Training data access audited.

#### 5.3.10 Progressive scale checklist

**10×**

- Feature cache + request coalescing  
- Async heavy NLP  
- Impact-based HOLD policy  
- Rule hotfixes for IOCs  

**100×**

- Regional cells  
- Per-category models  
- Approximate clustering  
- Humans constant via active learning  

**1,000×**

- Hierarchical campaigns  
- Streaming sketch features  
- Edge policy tokens for partners  
- Semi-supervised / weak supervision at catalog scale  

### 5.4 Deep dive: decision state machine

```text
                 +--> PUBLISHED ----------------+
                 |                              |
 SUBMITTED --> SCORED                           +--> SUPPRESSED --> HIDDEN --> REMOVED
                 |                              |
                 +--> HELD --> (human/nearline)-+
                 |
                 +--> REJECTED (never visible)

Appeals can transition REMOVED/HIDDEN → PUBLISHED (with new decision_id).
Edits create new score; may reset to HELD if substantial change.
```

### 5.5 Deep dive: online feature hydration

```text
Scorer receives review_id, reviewer_id, asin, order_id?, device_ctx
  MultiGet:
    reviewer_profile_features
    asin_velocity_features
    order_vp_features
    device_risk_features
    seller_risk_features
  Attach compact text features (local compute on text)
  Missing keys → defaults + confidence penalty
```

Hot-key mitigation: bestsellers’ ASIN features pre-aggregated in memory/Redis by nearline jobs.

### 5.6 Deep dive: cluster evidence package

Agents shouldn’t raw-query the graph DB. Package:

- Member review_ids (capped)  
- Shared device/ASN counts (aggregated)  
- Template exemplar snippets  
- Timeline histogram  
- Suggested action + confidence  
- Links to prior related cases  

### 5.7 Testing strategy

| Layer | What |
|-------|------|
| Unit | Policy mapping, idempotent apply |
| Replay | Historical campaigns; regression harness |
| Shadow | New model vs champion |
| Chaos | Feature store latency injection; bus lag |
| Red team | Internal farm simulation |
| Agent UX | Explanation quality ratings |

### 5.8 Cost narrative for SDE III

Be ready to walk:

1. Humans dominate marginal cost → invest in precision automation.  
2. Feature store QPS dominates infra → cache + preagg.  
3. Storing full text in SQL is a smell → object storage.  
4. Training daily on everything vs importance sampling.  
5. Multi-region active-active scoring only where marketplaces need it.

---

## 6. Wrap-Up

### 6.1 Recap architecture in 30 seconds

> Reviews hit an ingest API and event bus; an **online scorer** uses a **feature platform** plus rules/ML to decide publish/suppress/hold; **nearline** jobs catch campaigns via graph and templates; an **enforcement orchestrator** is the single writer of visibility state that PDP reads; **T&S queues** handle uncertain high-impact cases; **appeals and honeypots** close the label loop; we scale by cells, approximate graphs, and keeping humans on the highest EV work.

### 6.2 Key tradeoffs to restate

| Tradeoff | Choice |
|----------|--------|
| Latency vs accuracy | Compact online; deep nearline |
| Precision vs recall | Precision↑ with action severity |
| Auto vs human | Bands × ASIN impact |
| Customer voice vs fake cleanup | Err against removing genuine negatives |
| Explainability vs security | Reason codes for agents; generic for public |

### 6.3 Risks & follow-ups

- AI-generated reviews erode text-only signals → double down on commerce/graph.  
- Cross-marketplace identity gaps.  
- Legal/regulatory disclosure differences by country.  
- Tight coupling risk if PDP embeds scoring—keep state store.  
- Organizational: scoring vs catalog vs account integrity alignment.

### 6.4 What “good” looks like in the interview

- Clarified **fake ≠ negative**.  
- Split planes and SLOs.  
- Named **enforcement ladder** and audit.  
- Discussed **adversarial** adaptation and economics.  
- Owned **cost** of humans and **rollback** of models.  
- Progressive **10×/100×/1,000×** without hand-waving “just Kafka”.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & product (Q1–Q12)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q1 | Fake review vs unfair review? | Authenticity/incentives/coordination vs subjective quality |
| Q2 | Why not require VP for all reviews? | Coverage; still incentivized VP; policy choice |
| Q3 | Should we delay all reviews for human vetting? | Cost/latency disaster; only high-impact holds |
| Q4 | How do you measure success? | Precision@action, appeal overturn, campaign TTD, trust surveys, residual fake rate estimates |
| Q5 | What if sellers complain en masse? | Separate smear vs genuine defect; don’t let sellers veto negatives |
| Q6 | Multi-locale launch order? | Start one marketplace; isolate policy packs |
| Q7 | Images/video fakes? | Perceptual hash + reuse graph later |
| Q8 | Do we show authenticity badges? | Product risk—gaming; usually internal scores |
| Q9 | Interaction with “most helpful” rank? | Suppress flag as rank feature; separate vote integrity |
| Q10 | Cold-start reviewer? | Priors from order/device; conservative actions |
| Q11 | Employee / influencer reviews? | Disclosure policy; separate allowlisting |
| Q12 | Third-party review import? | Out of scope or trusted pipeline with provenance |

### 7.2 Architecture & APIs (Q13–Q24)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q13 | Sync or async scoring? | Hybrid by impact |
| Q14 | Why not score on PDP read? | Latency, cost, failure blast radius |
| Q15 | Event bus choice? | Kafka/Kinesis; partitioning by reviewer or asin |
| Q16 | Exactly-once enforcement? | Idempotent apply + decision_id |
| Q17 | Where does text live? | Object store + meta DB |
| Q18 | How do rankers consume decisions? | Enforcement state KV/cache |
| Q19 | Multi-region? | Region score; async global graph |
| Q20 | Schema evolution of features? | Versioned feature defs |
| Q21 | Backfill after new model? | Nearline replay by ASIN tier |
| Q22 | Partial feature outage? | Degrade confidence; rules; re-score |
| Q23 | How to avoid thundering herd on bestseller? | Preagg ASIN features |
| Q24 | API for Seller Central? | Case status + limited reason; not raw scores |

### 7.3 ML & features (Q25–Q40)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q25 | Why GBDT online? | Tabular features, speed, debuggability |
| Q26 | Deep NLP? | Nearline / distillation |
| Q27 | Training-serving skew examples? | Future leakage on joins; different tokenizers |
| Q28 | Label leakage via enforcement? | Careful with using prior removes as features |
| Q29 | Class imbalance? | Sample weight; cascade models; PR curves per action |
| Q30 | Calibration? | Platt/isotonic per action threshold |
| Q31 | Drift detection? | PSI, appeal rates, score histograms |
| Q32 | Graph features online? | Precomputed embeddings/aggregates |
| Q33 | How to detect AI text? | One signal; easy to evade alone |
| Q34 | Multilingual? | Locale models + shared behavior |
| Q35 | Active learning strategy? | Uncertainty × impact × diversity |
| Q36 | Weak supervision? | Rules as labeling functions + denoise |
| Q37 | A/B test a stricter threshold? | Guardrails on appeal/negative review rate |
| Q38 | Fairness concerns? | Monitor FP rates across locales/categories |
| Q39 | Explainability method? | Reason codes + local feature attrib |
| Q40 | Online learning? | Risky under adversaries; prefer batched + hot rules |

### 7.4 Abuse, enforcement, ops (Q41–Q56)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q41 | Coordinated brand attack overnight? | Burst detectors; emergency suppress; exec/T&S playbook |
| Q42 | Weaponized customer reports? | Report-rate features; don’t auto-remove on reports alone |
| Q43 | CAPTCHA on review submit? | Friction; use for risky reviewers only |
| Q44 | Seller sock puppets with real purchases? | Device/payment clusters; velocity; investigation |
| Q45 | Appeal flooding? | Rate limits; deposit of trust; prioritize |
| Q46 | Agent collusion / mistakes? | QA sampling; dual control; audits |
| Q47 | Public tipping of thresholds? | Sticky policies; limited disclosure |
| Q48 | Legal discovery request? | Audit log design helps |
| Q49 | When to suspend seller? | Integrity org; not auto from one review model |
| Q50 | Re-publish after appeal SLA? | Explicit state transition + notification |
| Q51 | Edit laundering? | Diff features; re-hold on large edits |
| Q52 | Vote rings boosting fakes? | Separate integrity input to rank |
| Q53 | Honeypot design? | Secret ASINs/accounts; gold labels |
| Q54 | Red team cadence? | Continuous internal farms |
| Q55 | Pager storm on Metric X? | Composite SLOs; avoid flappy FP alarms without volume |
| Q56 | Cost spike in human review? | Auto band expansion with precision guard |

### 7.5 Scale & reliability (Q57–Q68)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q57 | 100× reviews, same headcount? | Active learning + higher auto precision |
| Q58 | Hot partition asin? | Key spread; preagg; cache |
| Q59 | Model p99 timeouts? | Deadline budgets; fallback rules |
| Q60 | Poisoned training data? | Provenance; honeypot eval; agent QA |
| Q61 | Replay storm after outage? | Backpressure; priority by ASIN tier |
| Q62 | Cache inconsistency shows removed review? | Version tokens; short TTL; push invalidation |
| Q63 | Cross-cell identity? | Global ID service; async edge sync |
| Q64 | Disaster recovery? | Audit+state backups; rebuild features from log |
| Q65 | Exactly how Kafka keys chosen? | reviewer_id for affinity; asin for campaign jobs |
| Q66 | Multi-model ensemble latency? | Cascade: cheap first, expensive later |
| Q67 | SLO vs error budget for trust? | Separate “wrong remove” error budget (tinier) |
| Q68 | 1,000× graph? | Sketches, hierarchical clustering, sampling |

### 7.6 Behavioral / leadership (Amazon) (Q69–Q76)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q69 | Who do you page at 3am? | Clear ownership table |
| Q70 | Bias to action on viral fake wave? | Emergency rules with expiry + retrospective |
| Q71 | Disagree with policy on thresholds? | Data: FP samples, customer impact; escalate |
| Q72 | Frugality example? | Suppress-first; humans on EV; cold storage |
| Q73 | Earn trust of T&S agents? | Explanation quality; stable tools; listen to overrides |
| Q74 | Dive deep metric? | Overturn rate segmented by category |
| Q75 | Deliver results vs perfection? | Ship tiered MVP; iterate on farms |
| Q76 | Customer obsession conflict (seller vs buyer)? | Buyer trust in ratings is the product |

---

## 8. Appendices

### Appendix A — Example reason codes

| Code | Meaning | Typical action |
|------|---------|----------------|
| `RULE_BLOCKLIST_DEVICE` | Device on known farm list | Remove / block |
| `NLP_INCENTIVE_LANGUAGE` | “in exchange for discount” patterns | Suppress / hold |
| `GRAPH_DEVICE_CLIQUE` | Dense shared-device cluster | Cluster suppress |
| `ASIN_VELOCITY_ANOMALY` | Reviews ≫ sales baseline | Hold / suppress |
| `REVIEWER_BURST` | Too many reviews too fast | Throttle / hold |
| `TEMPLATE_SIM_HIGH` | Near-duplicate text cohort | Remove cohort |
| `PROXY_RESIDENTIAL_SCORE` | High proxy risk + other signals | Suppress |
| `VP_INCENTIVE_SUSPECT` | VP but incentive pattern + concentration | Hold |
| `CUSTOMER_REPORT_CLUSTER` | Many reports correlated | Priority queue |
| `MODEL_SCORE_HIGH` | Calibrated ML band | Per threshold |

### Appendix B — Sample online feature vector (illustrative)

```text
reviewer_account_age_days
reviewer_reviews_7d
reviewer_vp_ratio_90d
reviewer_category_entropy
order_to_review_hours
order_refunded
asin_reviews_1h
asin_reviews_to_units_7d_zscore
asin_star_mean_shift_24h
device_account_count_30d
ip_reviews_24h
ip_proxy_score
text_incentive_lexicon_hit
text_lang_matches_marketplace
text_embedding_sim_to_known_fake
seller_review_concentration
account_integrity_risk
prior_appeal_overturn_30d
```

### Appendix C — Policy threshold sketch

| Score band | ASIN tier Long-tail | ASIN tier Bestseller |
|------------|---------------------|----------------------|
| 0.00–0.60 | PUBLISH | PUBLISH |
| 0.60–0.80 | PUBLISH_SUPPRESSED | HOLD |
| 0.80–0.92 | HIDDEN + queue | HOLD + priority queue |
| 0.92–1.00 | REMOVE if rules agree | REMOVE only with rule corroboration or human |

*(Numbers illustrative—interview for calibration process, not magic constants.)*

### Appendix D — Metrics dictionary

| Metric | Definition |
|--------|------------|
| Auto-remove precision | Sampled human agreement on auto removes |
| Overturn rate | Appeals overturned / appeals | 
| Residual fake estimate | Audits on random published reviews |
| TTD campaign | First campaign review → first enforcement |
| Scoring p99 | Submit path latency |
| Cost per 1K reviews | Infra + human minutes allocated |
| Negative-review retention | Share of genuine 1–2★ surviving (health metric) |

### Appendix E — Anti-patterns (deal-breakers)

| Anti-pattern | Why fatal |
|--------------|-----------|
| “BERT on every submit, sync” | Miss latency/cost SLO |
| “Human review all reviews” | Impossible economics |
| “Remove anything seller flags” | Extorts genuine negatives |
| “IP blocklist solves farms” | Residential proxies |
| “One global threshold” | Bestseller vs long-tail harm differs |
| “PDP calls model live” | Coupled reliability |
| “No audit log” | Can’t appeal or investigate |
| “Future features in training” | Silent offline miracle accuracy |

### Appendix F — Capacity worksheet (fill in interview)

```text
Reviews/day ________ × peak factor ________ → peak rps ________
Features/score ________ × rps → feature QPS ________
Human budget ________ hours/day → max tasks ________
Auto precision target ________ → max auto rate ________
Storage/day ________ → yearly ________
```

### Appendix G — Interview 45-minute timebox

| Minutes | Focus |
|---------|-------|
| 0–5 | Requirements: fake definition, actions, SLOs |
| 5–10 | Numbers: rps, storage, human cost |
| 10–25 | HLD + diagram + enforcement |
| 25–35 | Deep dive: graph campaigns OR ML skew OR queues |
| 35–42 | Scale 10×/100×, failures, adversarial |
| 42–45 | Metrics, ownership, wrap-up |

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| VP | Verified Purchase |
| ASIN | Amazon product identifier |
| Suppress | Demote / exclude from default ranking |
| HOLD | Not customer-visible pending decision |
| T&S | Trust & Safety |
| Campaign / ring | Coordinated inauthentic review set |
| Decision_id | Immutable ID for an enforcement decision |
| PIT join | Point-in-time feature join for training |

### Appendix I — Related systems to mention

- Account integrity / bot detection  
- Content moderation (toxicity, PII)  
- Order fraud / payment risk  
- Seller risk / brand protection  
- Review ranking (“most helpful”)  
- Customer reports platform  

### Appendix J — Sample decision JSON

```json
{
  "decision_id": "dec_01HZX...",
  "entity_type": "review",
  "entity_id": "R123",
  "action": "PUBLISH_SUPPRESSED",
  "score": 0.81,
  "reason_codes": ["ASIN_VELOCITY_ANOMALY", "TEXT_EMBEDDING_SIM_TO_KNOWN_FAKE"],
  "model_version": "fri-gbdt-2026-07-18",
  "policy_version": "pol-2026-06-01",
  "actor": "online_scorer",
  "explain_ref": "s3://explain/dec_01HZX...",
  "ts": "2026-08-06T07:22:11Z"
}
```

### Appendix K — Ownership RACI (sketch)

| Activity | Scoring | Enforcement | T&S Ops | Model Platform |
|----------|---------|-------------|---------|----------------|
| Threshold change | C | A | C | C |
| Model deploy | C | I | I | A |
| Mass suppress playbook | C | A | A | I |
| Appeal overturn | I | A | A | I |
| Feature schema | A | I | I | C |

A=accountable, C=consulted, I=informed

### Appendix L — Progressive scale one-pager

| Scale | Biggest bottleneck | Primary investment |
|-------|--------------------|--------------------|
| 10× | Feature QPS + queue load | Cache, priority queues, async NLP |
| 100× | Campaign graph compute | Sharded approx clustering, cells |
| 1,000× | Labels & humans | Weak supervision, hierarchical detect, constant-headcount ops |

---

*End of Amazon SDE III prep doc — Fake-Review Detection System Design.*
