# System Design: Foreign Ad Manipulation Prevention

> **Focus areas:** Ads integrity · Foreign influence · Actor clustering · Payment/KYC · Creative & targeting signals · Coordination detection · Enforcement · Appeals · Privacy · Progressive scale  
> **Style:** End-to-end integrity design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct load split (scoring vs enforcement vs investigation), explicit precision/recall tradeoffs, deal-breakers for “ban all foreign advertisers” or “100% accurate intent classification”  
> **Interview theme:** Meta Trust & Safety / Ads Integrity L5+ — prevent **foreign actors** from manipulating **domestic** political/social-issue advertising and related influence ops

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

Goal: **bound the product**—a system that **detects, prevents, and enforces** against **foreign actors** attempting to manipulate **domestic advertising** (especially elections, social issues, and covert influence), while allowing legitimate cross-border commercial ads under policy.

### 1.0 What this is / is not

| Dimension | **Foreign ad manipulation prevention (this doc)** | Not this |
|-----------|---------------------------------------------------|----------|
| Primary job | Stop covert foreign influence via ads + linked assets | Ban all international e-commerce |
| Success | Reduce manipulative reach; high-precision enforcement; auditability | Perfect geopolitical intent oracle |
| Surfaces | Ads create/review/delivery + Pages/accounts/payments | Only organic feed ranking (related but separate) |
| Actors | Networks of accounts, pages, BM, payment instruments | Single keyword filter |
| Output | Block/restrict/label/investigate + transparency | Silent shadowban without process |
| Legal | Align with regional political ad laws + Meta policies | Replace elections commissions |

**Scope statement:** Design Meta’s foreign-ad-manipulation prevention: identity/eligibility, real-time and nearline risk scoring, coordinated network detection, enforcement + appeals, transparency, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is “foreign manipulation”? | Covert foreign entity funding/targeting domestic civic ads or influence ops | Multi-signal actor+campaign graph |
| F2 | Political / social issue ads? | Yes — highest scrutiny; authorization gates | Eligibility service before delivery |
| F3 | Commercial foreign ads OK? | Yes if transparent and policy-compliant | Don’t use citizenship alone as ban |
| F4 | When to check? | Create, edit, pay method add, deliver, report | Sync gates + async detectors |
| F5 | Signals available? | KYC, payments, IP/device, creative, targeting, social graph, landers | Feature platform |
| F6 | Enforcement actions? | Block ad, disable actor, restrict targeting, label, takedown network | Enforcement orchestrator |
| F7 | Human review? | Yes for borderline / high-reach | Case management + queues |
| F8 | Appeals? | Yes with audit trail | Appeals workflow |
| F9 | Transparency? | Ad Library / paid-for-by disclosures | Public store + APIs |
| F10 | Cross-stack coordination? | Ads + Pages + IG accounts + WhatsApp where policy applies | Entity resolution graph |
| F11 | Real-time vs batch? | Hard blocks sync; graph clusters nearline | Dual plane |
| F12 | False positives? | Costly for legit global brands | Precision-first on disable; recall via restrict |

**MVP functional scope:**

1. **Advertiser eligibility** for civic/political ads: location authorization, ID, page authenticity.  
2. **Payment instrument checks**: beneficiary ownership, high-risk corridors, mule patterns.  
3. **Real-time score** at ad creation/edit/delivery authorization.  
4. **Nearline coordination detection**: shared devices, funds, creatives, landers, targeting templates.  
5. **Enforcement actions** with reasons codes + evidence bundles.  
6. **Human review** for high-impact cases.  
7. **Appeals** and restoration paths.  
8. **Transparency** exports for political ads.  
9. Metrics: prevented spend/impressions, precision sampling, time-to-detect.

**Out of MVP:**

- Full OSINT agency replacement  
- Classifying all geopolitical narratives automatically as “true/false”  
- Offline TV/radio ad monitoring  
- Replacing organic Coordinated Inauthentic Behavior (CIB) entirely (share signals)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ad creation gate latency | Must not kill Ads Manager | p99 < 200–400ms added |
| N2 | Delivery auth check | Ultra hot path | p99 < 20–50ms (cached decision) |
| N3 | Network detection lag | Hours OK for clusters | Nearline < 1–6h; urgent < 15m |
| N4 | Enforcement durability | No “zombie” re-enable without review | Strong write + audit log |
| N5 | Auditability | Legal/regulatory | Immutable evidence + decision log |
| N6 | Privacy | Minimize sensitive data exposure | Purpose limitation; access control |
| N7 | Abuse resilience | Attackers adapt | Feature drift monitoring; red teams |
| N8 | Availability | Prefer fail-safe for political eligibility | Fail closed on civic auth; fail open carefully on commercial |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Domestic authorized candidate runs political ad → KYC OK → delivers with “Paid for by”.  
2. Foreign e-commerce sneaker ad to US → commercial path → allowed with normal ads quality.  
3. Covert network: foreign cards + US proxy Pages + identical creatives → cluster detector → network disable.  
4. User reports suspicious political ad → triage → escalate to integrity.  
5. Advertiser appeals false disable → review restores with feature feedback.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Dual citizen / diaspora legit ads | Authorization + disclosure; not auto-ban |
| VPN / travel login from abroad | Weak alone; combine with payments/KYC |
| Stolen domestic IDs | Doc forensics + device/payment graph |
| Shell NGOs | Beneficial ownership + fund flow clusters |
| Creative laundering (slight edits) | Perceptual hash + text embedding near-dup |
| Targeting laundering (many micro-ads) | Aggregate by actor network not ad_id |
| Deadline election spike | Scale review + tighter automated restrict |
| Model outage | Cached eligibility; fail-closed civic |
| Collusion with domestic straw person | Payment beneficiary ≠ page owner signals |
| Ad Library scraping amplification | Rate limits; still public by design |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ad create/edit QPS | 2K | 20K | 200K | 2M |
| Delivery auth checks/s | 2M | 20M | 200M | 2B (multi-surface) |
| Active ad accounts | 10M | 50M | 200M | global SMB+ |
| Political ads / day (season) | 100K | 1M | 10M | global elections overlap |
| Features computed / day | 5B | 50B | 500B | multi-trillion events |
| Graph edges / day | 200M | 2B | 20B | 200B |
| Auto enforcements / day | 50K | 500K | 5M | 50M |
| Human review decisions / day | 5K | 20K | 50K | capacity-capped |
| Evidence retention | 2y | 2–7y | jurisdictional | multi-policy |

**What each jump forces:**

- **10×:** Decision cache; feature store online; payment graph v1.  
- **100×:** Cell-local scoring; nearline graph platform; election “war room” mode.  
- **1,000×:** Hierarchical actor resolution; privacy-preserving aggregates; global election calendar routing.

### 1.5 Etc. (Constraints & Assumptions)

- “Foreign” is **policy-defined per country** (citizenship, residency, funding source, control)—not merely IP country.  
- Legitimate global brands must keep advertising.  
- Attackers are **adaptive** and multi-hop (straw entities).  
- Organic CIB systems share entity graph but ads money path is distinct.  
- Enforcement needs **explainability** for appeals and regulators.

**Scope statement to repeat back:**

> Design a foreign-ad-manipulation prevention system for Meta Ads: eligibility gates for civic ads, multi-signal risk scoring, coordinated network detection across accounts/payments/creatives, durable enforcement with appeals and transparency—scaling real-time delivery checks and nearline graph analytics through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Delivery auth** | Can this ad serve? | ~2M/s | ~20M/s | Edge cache + thin check |
| **Create/edit score** | Risk at write | ~2K/s | ~20K/s | Online scoring |
| **Feature logging** | Impressions/clicks/etc. | 10M+/s | 100M+/s | Streaming (sample) |
| **Graph build** | Entity links | batch/nearline | | Graph warehouse |
| **Enforcement writes** | Blocks/disables | 10–100/s | 1K/s | Control plane |
| **Review tools** | Human UI | low QPS | | Case DB |
| **Transparency API** | Ad Library | 1K–10K | | CDN + store |

**Anti-pattern:** running full GNN inference on every ad impression.

### 2.2 Decision cache math

```text
Delivery checks 2M/s with 50ms full score = impossible CPU
Must: cache immutable-ish decisions by (ad_id, policy_version, advertiser_state_version)
TTL short + invalidate on edit/enforcement
Hit rate target > 99% → origin score << 1% of delivery QPS
```

### 2.3 Feature volume

```text
If log 20 features × 10M events/s = 200M feature writes/s → DEAL-BREAKER
Sample impressions; full fidelity on creates, payments, enforcements, reports
Use sketches/aggregates for targeting similarity at scale
```

### 2.4 Graph size

```text
10M ad accounts × avg 5 payment instruments history = 50M nodes side
Edges: shared device, shared IP /24 bursts, shared creative hash, shared lander, shared beneficiary
Nearline connected components on suspicious seeds — not full FB graph each hour
```

### 2.5 Review capacity constraint

```text
Humans 5K decisions/day ≈ 0.06/s
Automation must handle 99%+; humans on high-reach / high-uncertainty / legal
Queue priority = reach × severity × election_proximity × model_uncertainty
```

### 2.6 Election spike

```text
Political ad create 10× in final 2 weeks
Review backlog explodes unless:
  - pre-authorized advertisers
  - automated restrict (no delivery) pending review for unsigned
  - surge staffing + model threshold tuning
```

### 2.7 Integrity event math (funnel)

```text
Baseline day (non-election):
  Ad create/edit events:              2K/s peak → ~50M/day mixed
  Civic-classified among creates:     ~0.5–2% (spikes in season)
  Eligibility checks:                 ≈ civic creates + auth renewals
  Online scores (create path):        ~2K/s
  Delivery authorize lookups:         ~2M/s (99%+ cache hits)
  Cache misses / thin revalidate:     ~10K/s
  Payment instrument link events:     ~100/s
  Graph edges ingested:               ~2K/s avg (bursty)
  Cluster proposals:                  ~10K/day
  Auto enforcements:                  ~50K/day
  Human review decisions:             ~5K/day  ← hard capacity cap
  Appeals opened:                     ~1–2K/day
  Transparency rows written:          political ads + amendments

Harm-weighted priority mass:
  priority ∝ reach_7d × civic_flag × foreign_funding_prior × election_proximity
Humans only see top of this mass; automation handles the long tail with RESTRICT/BLOCK ad
```

### 2.8 Precision budget vs spend leakage

```text
Suppose malicious foreign civic network spends $X before detect
Nearline lag 1h at $1K/h burn × 10 parallel actors = $10K leakage/hour worst case
Mitigations that don’t need full graph:
  L0 eligibility fail-closed
  L1 payment mule velocity → RESTRICT in seconds
  watchlists after first network disable → cut reconstitution

Precision@network_disable target ≥ 95% sampled
If precision slips to 80%: advertiser trust + regulatory risk dominates — raise threshold, use RESTRICT
```

### 2.9 Delivery CPU deal-breaker (repeat with numbers)

```text
2M delivery checks/s × 50ms ML = 100,000 CPU-s/s → ~100K cores — absurd
2M × 99.5% cache × 0.5ms lookup = feasible on edge
Design centers on decision cache + advertiser_epoch invalidation
```

### 2.10 100× election concurrence

```text
Multiple countries in elevated mode simultaneously
Review capacity does NOT scale 100× → must:
  - pre-auth civic advertisers early
  - auto-RESTRICT unsigned civic
  - share entity resolution with organic CIB
  - jurisdiction routers so US war room ≠ BRA war room queues
```

---

## 3. High-Level Design

### 3.1 API / integration points

| Op | Semantics |
|----|-----------|
| `CheckEligibility(advertiser, market, ad_type)` | Civic/political authorization |
| `ScoreAd(ad_draft, context)` | Risk score + reasons |
| `AuthorizeDelivery(ad_id)` | Cached allow/deny/restrict |
| `IngestSignal(event)` | Payments, device, report, takedown |
| `Enforce(action, entity_ids, reason, evidence)` | Control plane |
| `CreateCase(cluster)` | Human review |
| `Appeal(decision_id)` | Appeals |
| `TransparencyExport(filters)` | Ad Library |

**Decision object:**

```text
IntegrityDecision {
  entity_type: AD|ACCOUNT|PAGE|BM|PAYMENT,
  entity_id,
  action: ALLOW|LABEL|RESTRICT|BLOCK|DISABLE_NETWORK,
  score, reasons[],
  policy_version,
  evidence_refs[],
  expires_at / until_review,
  decision_id
}
```

### 3.2 Entity model

| Entity | Examples | Why |
|--------|----------|-----|
| Actor | User, Page, IG account, Business Manager | Who controls |
| Instrument | Card, bank, billing address, tax id | Who pays |
| Creative | Image/video/text, lander URL | What said |
| Campaign structure | Campaign/adset/targeting | How amplified |
| Cluster | Connected component of actors | Coordination |
| Market | Country / election jurisdiction | Domestic scope |

### 3.3 Policy framing — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Ban all foreign advertisers** | Simple | Breaks commerce; blunt | **Deal-breaker** |
| **Citizenship only** | Clear | Dual citizens; straw persons | Insufficient |
| **Control + funding + targeting + disclosure** | Matches threat | Complex | **Chosen** |
| **Content truth police** | Stops some lies | Speech/scale/legal minefield | Not sole signal |
| **Transparency only** | Sunlight | Too weak alone | Complement |

**Chosen definition (interview-ready):**

> Flag when **foreign control or funding** covertly drives **domestic civic influence ads** (or coordinated inauthentic amplification), violating authorization/disclosure and authenticity policies.

### 3.4 Scoring layers — Why X over Y

| Layer | Latency | Method | Action strength |
|-------|---------|--------|-----------------|
| L0 Rules | ms | Eligibility, sanctions, clear KYC fail | Hard block |
| L1 Online ML | 10–100ms | Tabular features | Score / soft block |
| L2 Nearline graph | min–hours | Clusters, embeddings | Network disable |
| L3 Human + intel | hours–days | Casework OSINT | High-confidence network |

**Deal-breaker:** only keyword lists on ad text (“election”) — trivial evasion + huge FP on news.

### 3.5 Signal taxonomy

| Family | Signals | Manipulation relevance |
|--------|---------|------------------------|
| Identity | Gov ID, business registry, page authenticity | Authorization |
| Payment | BIN country, beneficiary, mule velocity | Foreign funding |
| Infra | Device lineage, data center IP, emulator | Covert ops |
| Creative | Language mismatch, template farms, deepfakes | Influence content |
| Targeting | Domestic geo + civic interests from foreign actor | Manipulation aim |
| Behavioral | Burst creates, clone campaigns | Coordination |
| Network | Shared instruments across “unrelated” Pages | Straw networks |
| Feedback | User reports, journalist tips, gov requests | Seeds |

### 3.6 Enforcement ladder

```text
ALLOW
LABEL / disclosure strengthen
RESTRICT (no civic targeting / limited delivery)
BLOCK ad
DISABLE advertiser
DISABLE network (cluster)
ESCALATE law enforcement (rare, policy/legal)
```

Prefer **precision** as actions get harsher; use RESTRICT to buy recall safely before elections.

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Foreign ≠ IP | Control/funding/auth | Straw + VPN | GeoIP-only ban |
| Delivery path | Cached decision | QPS | Full ML each impression |
| Networks | Nearline graph | Coordination | Per-ad only view |
| Civic ads | Fail-closed auth | Law/policy | Fail-open political |
| Commerce | Allow with quality | Business | Blanket foreign ban |
| Humans | High-reach / uncertain | Precision | Pure automation at network disable |

### 3.8 Compliance, legal, and trust angles

Foreign-ad integrity is as much **policy/legal product** as ML.

| Angle | Implication |
|-------|-------------|
| **Jurisdiction-specific political ad laws** | Eligibility rules keyed by `market`; not one global boolean |
| **Transparency / Ad Library** | Political ads exportable; spend/impression ranges; disclaimers |
| **Sanctions & deny lists** | Hard blocks independent of ML |
| **Due process / appeals** | Disables need reason codes + evidence retention |
| **Law-enforcement requests** | Separate channel from automated integrity; still audited |
| **Privacy (IDs, payments)** | Tokenize; least-privilege reviewer views |
| **Speech vs authenticity** | Prefer actor/funding authenticity over “truth ministry” |
| **Cross-border data** | Regional scoring cells; replicate watchlist tokens not raw IDs |

**Trust ladder for advertisers (product):**

```text
Unauthorized civic → cannot deliver
Authorized + disclosed → normal political path
Soft integrity concerns → LABEL / RESTRICT targeting
Hard integrity → BLOCK / DISABLE with appeal
Network-level → DISABLE_NETWORK + reconstitution watchlists
```

**Meta T&S flavor:** share **entity resolution** with organic CIB and **payment risk** with Ads billing—but enforcement authority for civic ads stays with Ads Integrity + Elections ops, with clear decision ownership.

**Deal-breaker:** “just ban foreign IPs during elections” — legally blunt, product-destructive, and trivially bypassed by straw persons.

### 3.9 Dual-plane decisioning (sync vs nearline)

| Plane | Trigger | Latency | Typical action |
|-------|---------|---------|----------------|
| Sync L0/L1 | Create/edit/pay-add/delivery | ms | ALLOW/LABEL/RESTRICT/BLOCK |
| Nearline L2 | Graph jobs, creative farms | min–hours | Network disable / case |
| Offline L3 | Intel, OSINT, partnerships | hours–days | High-confidence network packs |

Never block the delivery path on L2 completion—use L0/L1 to bound damage while L2 runs.

---

## 4. Architecture Diagram

```text
 +------------------+     +---------------------+     +------------------+
 | Ads Manager / API|---->| Eligibility Gateway |---->| KYC / AuthZ DB   |
 +--------+---------+     | (civic vs commerce) |     +------------------+
          |               +----------+----------+
          |                          |
          v                          v
 +--------+---------+     +----------+----------+     +------------------+
 | Ad Create/Edit   |---->| Online Score Service|---->| Online Feature   |
 | Pipeline         |     | rules + ML          |     | Store            |
 +--------+---------+     +----------+----------+     +------------------+
          |                          |
          |                          v
          |               +----------+----------+
          |               | Decision Store      |<---- invalidate ---+
          |               | (ad/account state)  |                    |
          |               +----------+----------+                    |
          |                          ^                               |
          v                          |                               |
 +--------+---------+                |                               |
 | Ads Delivery     |--Authorize---->+                               |
 | (edge/cache)     |   allow/deny/restrict                          |
 +------------------+                                                |
                                                                     |
 +------------------+     +---------------------+     +--------------+--+
 | Signal Ingest    |---->| Stream Processors   |---->| Feature /    |  |
 | pay, device,     |     | aggregate, sketch   |     | Graph Build  |  |
 | report, click    |     +----------+----------+     +------+-------+  |
 +------------------+                |                       |          |
                                     v                       v          |
                          +----------+----------+     +------+-------+  |
                          | Cluster Detector    |---->| Case Manager |  |
                          | connected components|     | human review |  |
                          +----------+----------+     +------+-------+  |
                                     |                       |          |
                                     v                       v          |
                          +----------+-----------------------+--+       |
                          | Enforcement Orchestrator              |------+
                          | block/disable/label + audit log       |
                          +----------+----------------------------+
                                     |
                                     v
                          +----------+----------------------------+
                          | Transparency / Ad Library             |
                          | Appeals Service                       |
                          +---------------------------------------+

 Threat Intel / Elections Calendar ---> threshold & queue priority configs
 Organic CIB Entity Graph <---shared---> Ads Integrity Entity Resolution
```

**Create path:**

```text
submit ad
  -> classify ad_type (civic/commerce)
  -> if civic: Eligibility (auth, location, disclosures)
  -> Online Score (payment, history, creative, targeting)
  -> ALLOW / RESTRICT / BLOCK
  -> persist Decision + evidence refs
```

**Delivery path:**

```text
impression candidate
  -> lookup Decision(ad_id) in cache
  -> if missing: thin recompute or fail-safe by ad_type
  -> if advertiser_state revoked: deny
  -> serve or skip
```

**Network detection path:**

```text
signals -> entity edges -> seed suspicious nodes
  -> expand subgraph -> score cluster
  -> if high: propose DISABLE_NETWORK + case
  -> human confirm or auto if precision tier met
  -> enforce + prevent reconstitute (same instruments)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Civic political ads cannot deliver without valid eligibility** (fail-closed).  
2. **Every enforcement has decision_id + evidence bundle + policy_version.**  
3. **Decision invalidation** on edit, payment change, actor disable.  
4. **Appeals cannot silently clear without new decision.**  
5. **Network disable applies to resolved entities**, not only the seed ad.  
6. **Audit log append-only.**

#### 5.1.2 Fail-open vs fail-closed

| Path | Outage mode | Rationale |
|------|-------------|-----------|
| Civic eligibility | Fail-closed | Legal/integrity |
| Commerce quality score | Fail-open with caps | Revenue; monitor |
| Delivery cache stale | Serve last decision + short TTL | Availability |
| Graph detector down | Keep L0/L1; alert | Degraded integrity |

**Deal-breaker:** fail-open on political authorization during election week.

#### 5.1.3 Consistency of enforcement

```text
Enforce(account_disable):
  write ActorState(DISABLED) strong
  fanout: pause all ads, invalidate caches, kill tokens
  async: related Pages/BM via entity resolution
  idempotent by decision_id
```

Use **version vectors** on advertiser_state so edge caches don’t resurrect stale ALLOW.

#### 5.1.4 Evidence durability

```text
EvidenceBundle {
  decision_id,
  feature_snapshot,   // privacy-redacted for reviewers
  creative_hashes,
  payment_refs,
  graph_cluster_id,
  model_scores,
  reviewer_notes?
}
Store in WORM/object store; index by decision_id
```

### 5.2 Scalability

#### 5.2.1 Progressive scale

| Scale | Online | Nearline | Enforcement |
|-------|--------|----------|-------------|
| Baseline | Central score svc | Nightly clusters | Manual + rules |
| 10× | Feature store + cache | Hourly CC on seeds | Auto block ads |
| 100× | Regional score cells | Streaming graph | Auto network tiers |
| 1,000× | Edge authz tokens | Hierarchical entity resolution | Jurisdiction routers |

#### 5.2.2 Delivery auth design

```text
Token/decision blob cached at delivery tier:
  ad_id -> {allow_bits, advertiser_epoch, expiry, policy_v}
On advertiser_epoch bump: mass invalidate prefix
Avoid per-impression RPC to integrity core
```

#### 5.2.3 Graph at 100×

```text
Do not build one giant daily connected component on all ads
Pipeline:
  1) high-precision seeds (sanctions, mule cards, reports)
  2) expand k-hop with capped fanout
  3) community score
  4) merge with organic CIB entities
Partition graph by market + time window; global only for payment instruments
```

#### 5.2.4 Feature store

| Store | Use |
|-------|-----|
| Online KV | Last payment country, account age, prior strikes |
| Nearline | 7d creative similarity, cluster membership |
| Offline | Training labels, counterfactuals |

**Deal-breaker:** joining raw Hive tables synchronously in Ads Manager submit path.

### 5.3 Maintainability

#### 5.3.1 Policy as config

```text
policy_version = 2026.08.civic.v3
rules yaml + model model_id
Canary by market
Rollback = pin prior policy_version + invalidate decisions optionally
```

#### 5.3.2 Reason codes

Stable enums for appeals UX and analytics (`PAYMENT_MULE_CLUSTER`, `KYC_MISMATCH`, `CREATIVE_TEMPLATE_FARM`, …). Avoid opaque “model said no” alone for disables.

#### 5.3.3 Red team / adaptive adversaries

- Continuous evasion tests (slight creative edits, new BM, fresh cards).  
- Monitor precision/recall via sampled human labels.  
- Drift alarms when feature distributions shift pre-election.

#### 5.3.4 Privacy & access

- Tiered access: automated features vs human-visible evidence.  
- Minimize government ID exposure; tokenize.  
- Retention aligned to legal holds / elections.

### 5.4 Entity verification deep dive

#### 5.4.1 What “entity” means

| Layer | Examples | Verification |
|-------|----------|--------------|
| Natural person | Gov ID, selfie liveness | KYC vendor + doc forensics |
| Organization | Business registry, nonprofit status | Registry match + beneficial ownership |
| Page / IG presence | Page authenticity, admin graph | Admin residency vs market policy |
| Business Manager | BM admins, linked Pages | Role graph; agency vs end advertiser |
| Payment beneficiary | Legal name on card/bank | Match to authorized entity |

#### 5.4.2 Beneficial ownership

Straw networks hide behind local faces. Track **control edges**: who can publish, who pays, who receives refunds, who passes KYC.

```text
strong_link = payment_beneficiary ⊕ gov_id_token ⊕ registry_id
medium_link = device_lineage ⊕ verified_phone
weak_link = IP / email domain  # never merge alone
EntityResolution.merge only on strong+ or corroborated medium
```

#### 5.4.3 Stolen / synthetic ID

Doc forensics, device reuse with many IDs, velocity of KYC attempts, mismatch between ID locale and payment/funding path → challenge or reject civic auth (fail-closed).

### 5.5 Geo / beneficiary disclosure deep dive

#### 5.5.1 Geo is not citizenship

| Signal | Use |
|--------|-----|
| IP country | Weak behavioral prior |
| Billing country | Medium funding prior |
| KYC residency | Strong for eligibility |
| Targeting geo | Defines “domestic audience” |
| Page “about” locale | Weak; easily faked |

Policy question: **Who may run civic ads targeting country C?** Encode per-market—not `if ip != C: ban`.

#### 5.5.2 Paid-for-by / beneficiary disclosure

```text
Disclaimer string bound to authorization token
Must match authorized entity display name rules
Ad Library stores disclaimer + sponsor
Mismatch (disclaimer ≠ beneficiary ≠ page owner) → RESTRICT/BLOCK
```

#### 5.5.3 Targeting × foreign control interaction

```text
if domestic_civic_targeting(ad) and foreign_control_or_funding(actor):
  require eligibility OR enforce
Commerce targeting without civic topics → normal ads quality path
```

Micro-geos and lookalikes on civic interests raise scrutiny when funding priors are foreign.

### 5.6 Payment rails deep dive

#### 5.6.1 Why payments are central

Covert influence needs **spend**. Payment graph often outlives throwaway Pages.

| Signal | Manipulation tell |
|--------|-------------------|
| BIN / issuer country | Funding origin |
| Beneficiary legal name | Who receives value |
| Mule velocity | Many BMs, short-lived cards |
| Corridor risk | High-risk cross-border patterns |
| Refund / chargeback loops | Disposable instruments |
| Shared instrument across “unrelated” Pages | Coordination |

#### 5.6.2 Civic payment policy

```text
Civic ads may require:
  - payment method owned by authorized entity
  - ban certain corridors for civic (policy)
  - cooler on brand-new instruments near elections
Commerce: allow international cards with normal fraud checks
```

#### 5.6.3 Shared graph with Payments Risk

Integrity consumes `payment_risk_score`, `mule_cluster_id` as online features; may **freeze billing** for civic without being the ledger owner. Finance owns money movement; Integrity owns eligibility.

### 5.7 Graph signals & coordination deep dive

#### 5.7.1 Edge types (weighted)

| Edge | Weight intuition |
|------|------------------|
| Same payment beneficiary | Very high |
| Same device lineage | High |
| Same creative pHash | High |
| Same lander domain | Medium-high |
| Same targeting template | Medium |
| Same /24 IP burst | Low-medium |
| Same agency BM (legit) | Needs allowlist |

#### 5.7.2 Seeded expansion (not full CC)

```text
seeds = mule_payments ∪ sanctions ∪ high_risk_reports ∪ creative_farms
expand k-hop with fanout caps
require: foreign_funding_prior ∧ domestic_civic_targeting (for this threat)
score_cluster → auto vs human tier
merge entity IDs with organic CIB graph via platform API
```

#### 5.7.3 Creative & targeting laundering

Perceptual hash + text embeddings for near-dup creatives; aggregate spend/reach by **cluster** not `ad_id` so micro-ad flooding doesn’t evade review.

#### 5.7.4 Reconstitution prevention

After network disable, fingerprint instruments (cards, devices, landers, tax tokens) into **watchlists** with TTL; soft-block or elevate score on new accounts linking them—especially civic intent.

### 5.8 Enforcement deep dive

#### 5.8.1 Ladder × confidence

```text
ALLOW
LABEL / strengthen disclosure
RESTRICT (no civic targeting / limited delivery)
BLOCK ad
DISABLE advertiser
DISABLE network (cluster)
ESCALATE law enforcement (rare, legal)
```

| Action | Precision bar | Typical owner |
|--------|---------------|---------------|
| LABEL | Medium | Auto |
| RESTRICT | Medium | Auto (election mode lower bar) |
| BLOCK ad | Medium-high | Auto + rules |
| DISABLE actor | High | Auto if tiered else human |
| DISABLE network | Highest | Human or ultra-high precision auto |

#### 5.8.2 Fanout & epoch

```text
disable_network:
  write ActorState DISABLED + advertiser_epoch++
  pause ads; invalidate delivery caches
  watchlist instruments
  transparency events
  appeals surface notify
idempotent on decision_id
```

#### 5.8.3 Partial disable (mixed agencies)

Agency BMs may mix legit clients and bad actors—disable **resolved bad entities**, not necessarily entire agency without evidence; product/ops nuance.

### 5.9 Appeals deep dive

#### 5.9.1 State machine

```text
OPEN -> IN_REVIEW -> UPHELD | OVERTURNED | PARTIAL
OVERTURNED -> re-score + optional restore
All transitions audited; cannot silent-clear
```

#### 5.9.2 Evidence for reviewers

Privacy-redacted feature snapshot, creative hashes, payment refs (tokenized), cluster diagram, policy citations. Not raw gov ID images in default UI.

#### 5.9.3 Feedback loop

Overturns stratified by `reason_code` and market → threshold/model fixes. Rate-limit using appeals as gold labels (poisoning risk).

### 5.10 Legal constraints deep dive

| Constraint | Design response |
|------------|-----------------|
| Political ad eligibility laws differ by country | `policy_version` × market config |
| Transparency mandates | Ad Library pipelines; immutable-ish records |
| Sanctions | L0 hard block lists |
| Government takedown requests | Legal queue ≠ auto integrity; dual audit |
| Data localization | Regional feature stores; tokenized global watchlists |
| Defamation / speech pressure | Authenticity & eligibility focus; careful content-only bans |
| Retention / legal hold | Evidence WORM; longer under investigation |

**Deal-breaker:** one global “foreignness” score used as sole legal justification without market policy_version.

### 5.11 Civic authorization flow

```text
Advertiser requests political ad in country C:
  1) Prove eligible identity/residency/organization per C policy
  2) Bind to Page + disclaimer string
  3) Payment method eligible (not prohibited corridor for civic)
  4) Issue authorization token with expiry + scope
  5) Each ad must reference token; Ad Library indexed
```

**Deal-breaker:** allowing “boosted civic posts” to bypass Ads authorization.

### 5.12 Human review & elections mode

| Mode | Changes |
|------|---------|
| Normal | Standard thresholds |
| Election elevated | Lower auto-restrict bar; more humans; 24/7 |
| Crisis | Kill-switch playbooks; partner channels |

Queue ranking:

```text
priority = reach_7d * severity * election_proximity * uncertainty * virality
```

### 5.13 Metrics & integrity KPI

| KPI | Meaning |
|-----|---------|
| Prevented civic impressions by enforced foreign networks | Impact |
| Precision@disable (sampled) | Safety for legit |
| Time-to-detect cluster from first spend | Speed |
| Reconstitution rate 30d | Durability |
| Appeal overturn rate | FP quality |
| Authorization coverage | Process health |

### 5.14 Failure drills

| Drill | Expected behavior |
|-------|-------------------|
| Decision store outage | Civic fail-closed for new; cached delivery short TTL |
| ML scorer down | L0 rules only; commerce capped fail-open |
| Graph job lag 12h | L0/L1 still bound spend; alert elections ops |
| Cache serves stale ALLOW after disable | advertiser_epoch mismatch → deny |
| Mass false disables | Kill-switch pin prior policy_version; appeals surge staffing |
| Ad Library pipeline down | Buffer transparency events; don’t skip recording political ads |

### 5.15 Progressive scale narrative

| Jump | Online | Nearline | Ops |
|------|--------|----------|-----|
| **→10×** | Decision cache, online FS, payment graph v1 | Hourly seeded CC | Auto block ads |
| **→100×** | Regional score cells | Streaming graph | Election mode + war rooms |
| **→1,000×** | Edge authz tokens | Hierarchical entity resolution | Jurisdiction routers; privacy aggregates |

---

## 6. Wrap-Up

### 6.1 What we designed

A Meta Ads integrity system that **authorizes civic advertisers**, **scores ads online**, **detects foreign-funded coordinated networks nearline**, **enforces with audit/appeals**, and **publishes transparency**—without banning legitimate global commerce.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Precision on network disable | Fewer mass FPs | Some delayed recall |
| Fail-closed civic | Integrity/legal | Rare legit friction |
| Cached delivery decisions | Scale | Invalidation complexity |
| Graph nearline not realtime | Feasible CPU | Hours of malicious spend possible → mitigate with L0/L1 |
| Disclosure + auth | Policy clarity | UX burden on advertisers |

### 6.3 Deal-breakers

1. GeoIP-only “foreign” classifier as sole control.  
2. Full ML on every impression.  
3. Fail-open political eligibility.  
4. Blanket ban on all foreign commercial advertisers.  
5. Enforcement without audit/evidence.  
6. Civic boosts bypassing authorization.  
7. Per-ad view without payment/device graph (misses straw networks).  
8. Network disable without precision tier / human path.  
9. Using raw government IDs in online scoring path.

### 6.4 10× / 100× / 1,000× story

- **10×:** Decision cache + online feature store + payment graph.  
- **100×:** Streaming cluster detection; regional score cells; election mode.  
- **1,000×:** Hierarchical entity resolution across surfaces; jurisdiction routers; privacy-preserving aggregates for transparency.

### 6.5 Failure-drill one-liners

| Drill | One-liner |
|-------|-----------|
| Election week scorer down | Fail-closed civic auth |
| Stale ALLOW after ban | advertiser_epoch |
| Straw person KYC | Beneficial ownership + payments |
| Micro-ad flood | Cluster aggregate not ad_id |
| Appeal storm | Audit + reason codes; don’t silent clear |

### 6.6 Interview closing line

> “We don’t ban ‘foreign’—we stop **covert foreign control/funding** of **domestic civic influence** using eligibility gates, layered scoring, and network enforcement you can audit and appeal.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Threat & policy

**Q1: Define foreign ad manipulation in one sentence.**  
A: Covert use of foreign control or funding to influence a domestic civic audience via ads (and linked assets), bypassing authorization/disclosure/authenticity rules.

**Q2: Why not ban all non-domestic advertisers?**  
A: Breaks legitimate trade; attackers use domestic straw persons anyway; policy precision matters for product and law.

**Q3: How is this different from organic CIB?**  
A: Shared entity graphs, but ads add **money, targeting, authorization, Ad Library** constraints and delivery-time enforcement.

**Q4: What about state actors using local marketers?**  
A: Focus on **control and funds** (beneficial ownership, unusual payment paths), not just passport of the media buyer.

**Q5: Disinformation vs manipulation via ads?**  
A: Content authenticity is a signal; the system’s core is **actor authenticity + eligibility + coordination**, not being a supreme truth engine.

### 7.2 Signals & ML

**Q6: Strongest signals for foreign funding?**  
A: Payment beneficiary chains, instrument provenance, mismatch between claimed business locale and funding, mule-like velocity.

**Q7: Why is IP weak?**  
A: VPNs, traveling execs, cloud egress; useful in aggregate, dangerous alone.

**Q8: How to detect creative laundering?**  
A: Perceptual hashes, embedding near-dup, template cluster IDs, shared lander screenshots.

**Q9: Online vs batch labels?**  
A: Online: rules + tabular ML; batch: graph labels for training; careful leakage.

**Q10: Class imbalance?**  
A: Rare positives; use trained cascades, human-confirmed networks as gold, precision-targeted sampling.

### 7.3 Systems & scale

**Q11: How to hit delivery QPS?**  
A: Cache decisions keyed by ad_id + advertiser_epoch; invalidate on enforcement; no heavy RPC inline.

**Q12: What is advertiser_epoch?**  
A: Monotonic version bumped on any integrity state change; caches include epoch to prevent stale ALLOW.

**Q13: Graph explosion?**  
A: Seeded expansion with fanout caps; drop low-weight edges; partition by market.

**Q14: Feature store freshness SLO?**  
A: Payment features seconds–minutes; cluster membership minutes–hours; document per feature.

**Q15: Multi-region scoring?**  
A: Cells by market; global payment watchlist replicated; decisions local with global fanout for disables.

### 7.4 Enforcement & ops

**Q16: Ladder of actions?**  
A: Label → restrict → block ad → disable actor → disable network; match severity to confidence × harm.

**Q17: How to stop reconstitution?**  
A: Watchlist instruments/devices/landers; link new signups; velocity limits on new BM near elections.

**Q18: Appeals overturn high — what do you do?**  
A: Threshold tuning, better reasons, reviewer guidelines, feature bugs; don’t just “turn model off.”

**Q19: Election war room?**  
A: Calendar-driven capacity, lower restrict thresholds, faster SLAs, cross-functional playbooks.

**Q20: Govtakdown requests vs integrity detection?**  
A: Separate legal channel; still need Meta policy evaluation; audit both.

### 7.5 Privacy, legal, transparency

**Q21: Ad Library requirements?**  
A: Political ads stored with disclaimer, spend ranges, targeting summary per jurisdiction rules.

**Q22: Can models use sensitive attributes?**  
A: Follow privacy/policy; prefer behavioral/payment/graph features; legal review for special categories.

**Q23: Data retention?**  
A: Longer for enforcement evidence under legal hold; minimize raw ID copies.

**Q24: Cross-border data?**  
A: Scoring may need regionalization; replicate only necessary watchlist tokens.

### 7.6 Product edge cases

**Q25: Diaspora fundraising ads?**  
A: May be allowed with authorization/disclosure—policy-specific; system encodes rules per market, not hard-coded xenophobia.

**Q26: News publishers?**  
A: Different product surfaces; still need authenticity; careful FP management.

**Q27: Lookalike targeting of civic interests?**  
A: Extra scrutiny when combined with foreign control signals; possible restrict.

**Q28: A/B many micro-ads to evade review?**  
A: Aggregate by actor/cluster spend and reach, not per creative.

### 7.7 Estimation drills

**Q29: Why not score every impression with 5ms ML?**  
A: 2M/s × 5ms CPU = 10,000 CPU-seconds/s → ~10K cores busy solely for inference, before fanout—cache decisions.

**Q30: Reviewers needed if 1% of 1M political ads/day need humans?**  
A: 10K reviews/day; at 50 reviews/person-day → 200 people — shows automation necessity.

**Q31: Cache hit rate target?**  
A: ≥99% on delivery; compute budget on the 1% misses + writes.

### 7.8 Alternatives & deal-breakers

**Q32: Only disclosure, no blocking?**  
A: Too weak against covert networks; disclosure is necessary but not sufficient.

**Q33: Only human review?**  
A: Fails scale and speed; humans for precision tier.

**Q34: Central mega-model for “foreignness”?**  
A: Fragile/unexplainable; prefer layered rules+ML+graph with reason codes.

**Q35: Share raw IDs to all reviewers?**  
A: Privacy deal-breaker; tokenize + least privilege.

### 7.9 Interview craft

**Q36: How to open?**  
A: Define threat (covert foreign civic influence), non-goals (ban commerce), then dual planes: sync gates + nearline networks.

**Q37: What impresses L5+?**  
A: Delivery cache/epoch invalidation, fail-closed civic, payment graph, reconstitution, precision ladder, election mode.

**Q38: Common mistake?**  
A: Building a giant real-time GNN on impressions, or GeoIP bans.

**Q39: Closing metrics?**  
A: Prevented reach, precision@disable, time-to-detect, reconstitution, appeal overturn.

**Q40: Related systems to cite?**  
A: Ads quality, payment risk, organic CIB, KYC, Ad Library, abuse feature store.

**Q41: How do organic and ads integrity share data?**  
A: Entity resolution IDs and cluster membership via platform APIs; separate enforcement authorities with shared evidence refs.

**Q42: What if interviewer pushes for 100% detection?**  
A: State irreducible uncertainty; optimize harm-weighted recall with precision constraints and human escalation.

### 7.10 Entity, payments, disclosure (extra)

**Q43: How do you verify an advertiser entity for civic ads?**  
A: Market-specific KYC/registry, bind Page + disclaimer, verify payment beneficiary matches authorized party, issue scoped authorization token; fail-closed if incomplete.

**Q44: Why beneficiary disclosure matters beyond “Paid for by” text?**  
A: Attackers put fake disclaimer strings; system must bind disclaimer to verified entity and payment beneficiary, not free-text honor system alone.

**Q45: Walk payment-rail signals for a straw network.**  
A: Shared beneficiary across Pages, mule velocity, BIN country vs claimed locale, short-lived cards, refund loops—seed graph expansion.

**Q46: When is RESTRICT better than DISABLE?**  
A: Medium confidence or election speed needs: stop civic harm quickly with lower FP cost; escalate to disable as evidence accumulates.

### 7.11 Appeals, legal, drills

**Q47: What must an appeal packet contain?**  
A: decision_id, policy_version, reason codes, redacted evidence refs, cluster id if any, reviewer notes trail—immutable audit.

**Q48: How do legal takedown requests differ from integrity detection?**  
A: Separate intake/legal evaluation; may still enforce under Meta policy; both audited; integrity models don’t auto-execute every gov request.

**Q49: Name three deal-breakers specific to this problem.**  
A: GeoIP-only foreign ban; fail-open civic eligibility; full ML on every impression without decision cache.

**Q50: Election-night failure drill?**  
A: Scorer outage → rules + fail-closed civic; cache epoch still honors disables; graph lag accepted if L0/L1 bound spend; war-room dashboard on UNKNOWN/legacy allow rates.

**Q51: How do you stop reconstitution after DISABLE_NETWORK?**  
A: Watchlist payment/device/lander/tax tokens; elevate or block new entities linking them; velocity limits on new BMs in elevated markets.

**Q52: Meta-specific angle vs generic ad platform?**  
A: Cross-surface entity resolution (Pages/IG/BM), shared CIB graph, huge delivery QPS demanding epoch’d decision cache, Ad Library + Elections ops, Integrity Feature Store shared with other T&S pillars.

---

### Appendix A — Online score pseudocode

```text
def score_ad(ad, advertiser, market):
  if is_civic(ad):
    elig = eligibility.check(advertiser, market)
    if !elig.ok: return BLOCK(elig.reasons)
  feats = feature_store.get_online(advertiser, ad)
  rule = rules.eval(feats, ad, market)
  if rule.hard_block: return BLOCK(rule.reasons)
  ml = model.predict(feats)
  action = calibrate(ml, market, election_mode)
  return Decision(action, ml, rule.reasons, policy_v)
```

### Appendix B — Delivery authorize

```text
def authorize_delivery(ad_id):
  d = cache.get(ad_id)
  if d and d.advertiser_epoch == actor.epoch(ad.advertiser):
    return d.action
  d = decision_store.get(ad_id) or thin_recompute(ad_id)
  cache.put(ad_id, d, ttl=short)
  return d.action
```

### Appendix C — Cluster detection sketch

```text
seeds = mule_payments ∪ sanctions ∪ high_risk_reports
for s in seeds:
  nodes = expand(s, max_hops=3, max_nodes=5000, min_edge_weight=w)
  if civic_domestic_targeting(nodes) and foreign_funding_prior(nodes):
    cscore = score_cluster(nodes)
    if cscore >= auto_disable_threshold: enforce_network(nodes)
    elif cscore >= review_threshold: open_case(nodes)
```

### Appendix D — Edge weight table (example)

| Edge | Weight |
|------|--------|
| Same beneficiary | 0.9 |
| Same device | 0.8 |
| Creative pHash | 0.75 |
| Lander domain | 0.7 |
| Targeting template | 0.55 |
| IP /24 | 0.25 |

### Appendix E — Decision reason codes

```text
ELIGIBILITY_MISSING
KYC_MISMATCH
PAYMENT_FOREIGN_BENEFICIARY
PAYMENT_MULE_VELOCITY
DEVICE_DATACENTER_FARM
CREATIVE_TEMPLATE_FARM
TARGETING_CIVIC_DOMESTIC
CLUSTER_FOREIGN_CONTROL
SANCTIONS_HIT
DISCLOSURE_MISSING
```

### Appendix F — Enforcement fanout

```text
disable_network(cluster_id):
  entities = resolve(cluster_id)
  for e in entities:
    write_state(e, DISABLED, decision_id)
  invalidate_caches(entities)
  pause_ads(entities)
  watchlist_instruments(entities)
  export_transparency_events(entities)
  notify_appeals_surface(entities)
```

### Appendix G — Feature list (MVP)

| Feature | Plane |
|---------|-------|
| account_age_days | online |
| gov_id_status | online |
| payment_bin_country | online |
| beneficiary_country | online |
| prior_integrity_strikes | online |
| creative_phash_cluster_size | nearline |
| shared_device_component_id | nearline |
| % targeting civic interests | online |
| disclaimer_present | online |
| spend_velocity_24h | online |

### Appendix H — Election calendar config

```yaml
market: US
election_day: 2026-11-03
elevated_start: 2026-09-01
auto_restrict_threshold: 0.62  # lower than normal 0.75
review_sla_hours: 4
```

### Appendix I — Appeals state machine

```text
OPEN -> IN_REVIEW -> UPHELD | OVERTURNED | PARTIAL
OVERTURNED -> re-score with human label feedback
All transitions audited
```

### Appendix J — NFR card

```text
Delivery auth p99 < 50ms cached
Create score p99 < 400ms
Civic eligibility fail-closed
Network disable audited
No GeoIP-only foreign ban
Transparency for political ads
```

### Appendix K — Sampling for precision

```text
Each day sample N auto-disables for human label
Track precision by reason_code and market
Gate new model ship on precision floors
```

### Appendix L — Watchlist entry

```text
WatchItem { type: CARD_FP|DEVICE|LANDER|TAX_ID_TOKEN, hash, ttl, source_decision }
On signup/bill: soft challenge or restrict if hit + civic intent
```

### Appendix M — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Decision cache, online FS, payment graph |
| 100× | Streaming clusters, cells, election mode |
| 1,000× | Hierarchical entity resolution, jurisdiction routers |

### Appendix N — Fail modes matrix

| Component down | Civic | Commerce |
|----------------|-------|----------|
| Eligibility | Block new civic | N/A |
| ML scorer | Rules only | Fail-open + caps |
| Graph | L0/L1 only | L0/L1 only |
| Decision store | Fail-closed deny new; cached delivery short | Cached |

### Appendix O — Comparison: rules vs ML vs graph

| | Rules | ML | Graph |
|--|-------|----|-------|
| Latency | Best | Good | Slow |
| Explain | Best | Medium | Medium |
| Evasion | Easy | Medium | Harder |
| Coordination | Weak | Weak | Strong |

### Appendix P — Ad Library record

```json
{
  "ad_id": "123",
  "paid_for_by": "Committee X",
  "pages": ["..."],
  "spend_range": {"min": 1000, "max": 1999},
  "impressions_range": {"min": 50000, "max": 59999},
  "targeting_summary": {"geo": ["US-CA"], "age": "18+"},
  "currency": "USD"
}
```

### Appendix Q — Entity resolution keys

```text
Strong: payment beneficiary token, gov id token, business registry id
Medium: device lineage, verified phone
Weak: IP, email domain
Never merge on weak alone
```

### Appendix R — Threat scenarios checklist

1. Foreign card → domestic Page political ads  
2. Stolen KYC → straw candidate booster  
3. Creative farm + microtargeting  
4. NGO shell funding  
5. Reconstitution after takedown  
6. Agency with mixed legit/illegit clients (partial disable)

### Appendix S — 30m interview checklist

1. Define threat + non-goals.  
2. Dual plane: sync vs nearline.  
3. Eligibility + score + graph + enforce.  
4. Delivery cache/epoch.  
5. Precision ladder + appeals.  
6. 10×/100×/1,000×.  
7. Deal-breakers.

### Appendix T — Worked example

```text
Baseline delivery 2M checks/s
Cache 99.5% hit → 10K misses/s thin lookups
Create score 2K/s × 100ms = 200 CPU-s/s → ~200 cores (OK with pool)
Cluster job: 10K seeds × 1K node expand = 10M edge exams/hour — batch OK
```

### Appendix U — Interaction with payments risk

```text
Payments risk score is an input feature
Integrity can freeze billing for civic
Finance still owns chargebacks; integrity owns ad eligibility
Shared mule instrument graph
```

### Appendix V — Glossary

| Term | Meaning |
|------|---------|
| Civic/political ad | Regulated issue/election ad |
| Straw person | Local front for foreign control |
| Reconstitution | Relaunch after takedown |
| Advertiser epoch | Integrity state version |
| CIB | Coordinated Inauthentic Behavior |
| Beneficial ownership | Who truly controls funds/entity |

### Appendix W — Reason → user messaging map

| Code | Advertiser message class |
|------|--------------------------|
| ELIGIBILITY_MISSING | Complete authorization |
| PAYMENT_* | Update billing / verification |
| CLUSTER_* | Reserved / high-level policy citation |
| CREATIVE_* | Edit creative / lander |

### Appendix X — Canary & rollback

```text
Ship model to 5% markets
Watch precision, advertiser support tickets, spend loss
Rollback policy_version pin
Optionally re-score active ads async
```

### Appendix Y — What NOT to store in online path

```text
Full government ID images
Raw card PAN
Unredacted OSINT dossiers
(Use tokens + offline vault)
```

### Appendix Z — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| Ads delivery | Authorize |
| Ads Manager | Create gates |
| Payment risk | Instruments |
| Organic CIB | Entity graph |
| KYC platform | Eligibility |
| Ad Library | Transparency |
| Appeals | Due process |
| Feature store | Scores |

---

*End of Foreign Ad Manipulation Prevention system design.*
