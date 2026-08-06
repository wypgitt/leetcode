# System Design: Bot Detection (Distributed Botnet)

> **Focus areas:** Account integrity · Botnet clustering · Device/graph signals · Real-time scoring · Nearline detection · Enforcement · Adversarial ML · Progressive scale · Trust & Safety  
> **Style:** End-to-end integrity design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split online vs nearline planes, correct QPS math, precision/recall tradeoffs, deal-breakers for “CAPTCHA everywhere” or “one classifier solves bots”  
> **Interview theme:** Meta Trust & Safety / AI Integrity L5+ — detect and disrupt **distributed botnets** abusing Facebook/Instagram surfaces (spam, fake engagement, scraping, ads fraud, influence)

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

Goal: **bound the product**—a **distributed bot-detection** platform that scores users/sessions/actions in real time, discovers botnet clusters nearline, and enforces (challenge, restrict, disable) across Meta surfaces with measurable precision.

### 1.0 What this is / is not

| Dimension | **Bot detection platform (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Detect automated / coordinated inauthentic accounts & actions | Replace all spam classifiers content-only |
| Success | Reduce bot harm (engagement fraud, spam, scraping, ads) with bounded FP | 100% bot recall with zero friction |
| Entity | Account, device, session, action, cluster | Single IP blocklist |
| Planes | Online score + nearline graph + offline train | Batch-only nightly bans |
| Enforcement | Challenge / rate-limit / disable / network takedown | Silent permanent shadowban only |
| Adversary | Adaptive botnets, residential proxies, human farms hybrid | Script kiddie from one IP |

**Scope statement:** Design Meta bot detection for distributed botnets: signal ingest, real-time action scoring, cluster detection, enforcement + appeals hooks, adversarial robustness, progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a bot? | Automated or scripted control; also coordinated fake accounts | Score automation + authenticity |
| F2 | Surfaces? | Login, signup, like/follow/comment, messaging, ads, scrape APIs | Action-typed scoring |
| F3 | Real-time needed? | Yes for write actions / signup | Online path < tens of ms |
| F4 | Botnet = cluster? | Yes — shared infra/behavior | Graph nearline |
| F5 | Signals? | Device, IP, behavior, graph, content, payment, app attestation | Feature platform |
| F6 | Enforcement? | CAPTCHA/challenge, friction, restrict, disable, cluster takedown | Ladder |
| F7 | Human farms? | Partial — behavioral + economic signals | Don’t rely on “mouse entropy” alone |
| F8 | False positives? | High cost (celeb/journalist lockouts) | Precision tiers; appeals |
| F9 | Feedback labels? | Enforcements, challenges solved, honeypots, human review | Training loops |
| F10 | Cross-app? | FB + IG (+ others) shared integrity IDs | Entity resolution |
| F11 | Explainability? | Reason codes for ops; limited for attackers | Dual views |
| F12 | Privacy? | Purpose-limited integrity processing | Access control; retention |

**MVP functional scope:**

1. Instrument **action events** (signup, login, social writes, API).  
2. **Online bot score** per action/session with rules + ML.  
3. **Challenges** (CAPTCHA, email/SMS, attestation) on medium risk.  
4. **Nearline botnet clustering** via devices, proxies, behavioral templates.  
5. **Enforcement orchestrator** with account state + rate limits.  
6. **Honeypot / decoy** signals for high-precision labels.  
7. Metrics dashboards; badness volumes; FP sampling.  
8. Hooks to ads fraud & spam systems.

**Out of MVP:**

- Perfect detection of all human click-farms  
- Client-side DRM root-of-trust on all devices  
- Replacing content spam NLP entirely  
- Public bot-score API for third parties

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Online score latency | Inline with actions | p99 < 20–40ms |
| N2 | Availability | Prefer degrade to rules | 99.99% thin path |
| N3 | Cluster detection lag | Minutes–hours | < 1h typical; < 15m for hot seeds |
| N4 | Throughput | Multi-million actions/s | Scale table |
| N5 | Precision on disable | High | Sampled ≥ target (e.g. 95%+) |
| N6 | Challenge solve UX | Friction OK if rare | Challenge rate budgets |
| N7 | Adversarial drift | Continuous | Retrain + rule hotfixes |
| N8 | Audit | Enforcement trail | decision_id immutable |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Normal user likes a post → low score → allow.  
2. Credential-stuffing burst → high login score → challenge / block.  
3. Botnet follow-train shares devices → cluster job → network disable.  
4. Scraper hits rate anomaly → API throttle + token revoke.  
5. Borderline mobile user → soft CAPTCHA once → success clears short-term risk.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Residential proxy botnet | Weak IP; lean device graph + behavior templates |
| Device reset farms | Attestation gaps; signup velocity; graph of invites |
| Compromised legit accounts (ATO bots) | Session anomaly ≠ disable account forever; session revoke |
| Viral celebrity traffic | Rate limits not bot bans; allowlist bursts with trust |
| Challenge farming (CAPTCHA solvers) | Increase cost; attestation; risk band not binary |
| Model outage | Rules-only fail-safe; higher challenge rate temporarily |
| Shared family device | Avoid hard merge on device alone; multi-user models |
| VPN journalists | Don’t equate VPN with bot; combine signals |
| Copycat behavior after takedown | Watchlists; reconstitution features |
| Poisoned training labels | Label provenance; honeypot gold set |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Actions scored / s | 2M | 20M | 200M | 2B |
| Signups / day | 2M | 20M | 200M | 2B |
| Online feature reads / s | 4M | 40M | 400M | multi-B |
| Graph edges ingested / day | 1B | 10B | 100B | 1T |
| Clusters proposed / day | 10K | 100K | 1M | 10M |
| Auto enforcements / day | 100K | 1M | 10M | 100M |
| Challenges / day | 5M | 50M | 500M | budgeted |
| Model versions served | 5 | 20 | 50 | per-surface cells |
| Label volume / day | 1M | 10M | 100M | weak+strong mix |

**What each jump forces:**

- **10×:** Tiered scoring; feature cache; stream aggregates.  
- **100×:** Cell-local online score; sharded graph; action-type models.  
- **1,000×:** Hierarchical botnet detection; edge decision tokens; privacy-preserving learning.

### 1.5 Etc. (Constraints & Assumptions)

- Bots are **economic actors** — raise cost, cut ROI, not only classify.  
- **Automation ≠ always bad** (accessibility, tests, partner APIs)—use allowlists + intent.  
- Human farms blur “bot”; detect **inauthentic coordination** too.  
- Attackers see challenges and adapt — assume **adversarial ML**.  
- Shared with ads fraud / spam / CIB via entity IDs.

**Scope statement to repeat back:**

> Design a bot-detection platform against distributed botnets: real-time action scoring with challenges, nearline cluster detection on shared infrastructure and behavioral templates, durable enforcement with precision tiers, and progressive 10×/100×/1,000× scaling—without relying on IP blocklists or universal CAPTCHA.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Action score** | Inline allow/deny/challenge | ~2M/s | ~20M/s | Online |
| **Feature fetch** | KV multi-get | ~2–4× actions | | Online FS |
| **Event log** | Analytics/train | sampled | | Stream |
| **Aggregate jobs** | Velocity counters | continuous | | Stream |
| **Graph build** | Edges | nearline | | Graph |
| **Enforcement** | State writes | 100–1K/s | | Control |
| **Challenge service** | CAPTCHA/attest | bursty | | Edge |

**Anti-pattern:** logging full feature vectors for every like at 200M/s to cold storage.

### 2.2 Latency budget

```text
Action handler total p99 100ms
Bot score budget: 20–40ms
  rule engine: 1–3ms
  feature multi-get: 5–15ms
  model inference: 3–10ms
  decision + side effects: 1–5ms
→ features must be precomputed/cached; no Hive
```

### 2.3 Feature store QPS

```text
2M actions/s × 10 keys average = 20M KV gets/s
Need: batching, locality, tiered cache (process → regional Redis → FS)
Group features into blobs per user/session to cut RTTs
```

### 2.4 Challenge cost

```text
If naive CAPTCHA on 5% of 2M/s = 100K CAPTCHA/s → UX + vendor DEAL-BREAKER
Budget challenges by risk mass: target << 0.1–1% overall; higher on signup/login
```

### 2.5 Graph math

```text
Edges/day 1B → ~12K edges/s average; peaks higher
Store: time-partitioned edge log + serving graph for hot expansion
Connected components on seeds not full 3B-user CC daily
```

### 2.6 Economic framing

```text
Botnet value ∝ successful actions (follows, spam DMs, ad clicks)
Detection success = cut successful actions × raise cost(challenge, burn accounts)
Measure: bad action rate, account survival curve, cost-per-success proxy
```

### 2.7 Integrity event math (action funnel)

```text
Baseline peak 2M actions/s mix (illustrative):
  LIKE/REACT:     60%
  FOLLOW:         5%
  COMMENT:        5%
  MESSAGE:        3%
  LOGIN:          2%
  SIGNUP:         0.1% (but critical)
  API_READ:       20%
  other:          remainder

Online score invocations ≈ 2M/s (short-circuit DISABLED cheap)
Hard-rule hits:           ~0.01–0.1%
CHALLENGE outcomes:       budget ≪ 0.1–1% overall; higher on signup/login
BLOCK_ACTION:             ~0.05%
DISABLE (auto):           tiny rate; bursty during campaigns
Nearline cluster proposes: ~10K/day → enforce subset
Honeypot hits:            high-precision gold, low volume

Label mass/day:
  gold (honeypot/review):     tens–hundreds of K
  silver (durable disables):  ~100K
  bronze (challenges):        millions — weak, down-weighted
```

### 2.8 Precision / recall economics

```text
Let harm(action) differ:
  spam DM to stranger ≫ like on public post
Optimize expected harm reduction under FP constraint:
  max recall_harm_weighted  s.t. precision@disable ≥ P_min
  use RESTRICT/CHALLENGE bands when uncertain

Example:
  1M disables/day at 90% precision → 100K FP/day — catastrophic UX
  Same at 99% → 10K FP/day — still needs appeals + soft tiers first
→ disable threshold lives in the far tail; recall from clusters + restrict
```

### 2.9 Shadow testing cost

```text
Shadow score 10% of traffic: log decision_would_have ≠ applied
Storage: 0.1 × 2M/s × 200B ≈ 40 MB/s → ~3.5 TB/day — sample further or compact
Compare: precision proxy via honeypot catch rate, challenge rate delta, bad-action proxies
Ship only if shadow beats holdout on harm metrics without blowing challenge budget
```

### 2.10 100× cell math

```text
200M scores/s → must shard by user cell; in-process models; feature blobs
Central Python RPC scorer = DEAL-BREAKER
Edge allow-tokens for low-risk sessions cut FS fetch storms another 5–20×
```

---

## 3. High-Level Design

### 3.1 API / integration

| Op | Semantics |
|----|-----------|
| `ScoreAction(action, actor, session, context)` | risk, action enum, reasons |
| `GetActorState(actor_id)` | DISABLED / RESTRICTED / OK |
| `Enforce(decision)` | apply state + fanout |
| `ReportSignal(edge/event)` | device bind, honeypot hit |
| `ChallengeVerify(token, result)` | update risk |
| `ClusterPropose(subgraph)` | nearline → case/auto |

**Action enum examples:** `SIGNUP`, `LOGIN`, `LIKE`, `FOLLOW`, `COMMENT`, `MESSAGE`, `ADS_CLICK`, `API_READ`.

**Decision:**

```text
BotDecision {
  action_id,
  actor_id, session_id,
  score: 0..1,
  outcome: ALLOW|CHALLENGE|RATE_LIMIT|BLOCK_ACTION|DISABLE_ACTOR|ESCALATE_CLUSTER,
  reasons[],
  model_ids[],
  policy_version,
  decision_id
}
```

### 3.2 Entity & graph model

| Node | Examples |
|------|----------|
| Account | FB/IG user, page |
| Device | Attestable device id, browser fingerprint lineage |
| Session | Cookie / token family |
| IP / Network | IP, ASN, /24, residential ISP tag |
| Content template | Spam text cluster, media hash |
| Phone / email | Normalized contact hashes |
| Cluster | Botnet component |

| Edge | Meaning |
|------|---------|
| USED_DEVICE | Account–device |
| SHARED_IP_BURST | Co-activity |
| SAME_TEMPLATE | Behavioral/content |
| INVITED | Growth edge |
| PAID_WITH | Ads/payment (fraud bots) |
| SOLVED_CHALLENGE | Signal (can be farmed) |

### 3.3 Why X over Y — detection approach

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **IP blocklist** | Simple | Residential proxies; CGNAT FP | Tiny complement |
| **CAPTCHA everywhere** | Raises cost | UX devastation; solvers | **Deal-breaker as default** |
| **Per-action ML only** | Fast | Misses distributed low-and-slow | Online layer |
| **Graph clusters only** | Finds botnets | Lag; misses solo bots | Nearline layer |
| **Layered: rules+ML+graph** | Defense in depth | Complexity | **Chosen** |
| **Honypots** | High precision labels | Coverage limited | Label engine |

### 3.4 Scoring model (MVP)

```text
score = calibrate(
  w_rules * rules_hit +
  w_ml * ml_score +
  w_cluster * cluster_prior +
  w_velocity * velocity_anomaly
)

outcome:
  score < t1: ALLOW
  t1..t2: ALLOW + async log / soft rate limit
  t2..t3: CHALLENGE
  t3..t4: BLOCK_ACTION
  > t4 or hard rule: DISABLE / escalate
Thresholds differ by action_type (signup stricter than like)
```

**Deal-breaker:** one global threshold for likes and signups.

### 3.5 Online features (examples)

| Feature | Notes |
|---------|-------|
| account_age | New accounts riskier for some actions |
| friend_count / graph age | Empty graph spam |
| device_trust | Attestation, seen-good history |
| ip_risk / asn_type | DC vs residential (probabilistic) |
| action_velocity_* | Per actor/device/ip windows |
| challenge_history | Recent fails/solves |
| cluster_id prior | Nearline membership |
| behavioral z-scores | Timing templates |
| app_id / client_signal | API vs app |

### 3.6 Enforcement ladder

```text
ALLOW
SOFT_FRICTION (slow mode, reduced quota)
CHALLENGE (CAPTCHA / SMS / attest)
BLOCK_ACTION (single write denied)
SESSION_REVOKE (ATO bots)
RESTRICT_ACCOUNT (no follows/DMs; read OK)
DISABLE_ACCOUNT
DISABLE_CLUSTER (+ watchlist)
```

Match **confidence × harm**. High-reach disable needs higher precision.

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Architecture | Online + nearline | QPS vs coordination | Only batch bans |
| CAPTCHA | Risk-triggered | UX / cost | Universal CAPTCHA |
| IP | Weak feature | Proxies | IP-only botnet ban |
| ATO vs bot | Session vs account | Don’t punish victims | Disable all anomalous logins forever |
| Labels | Honeypot + reviews | Precision | Feedback loop on challenged-only |
| Cross-app | Shared entity IDs | Botnet hops apps | Siloed scores only |

### 3.8 Trust, safety, and compliance angles

Bot detection is a **Meta Integrity** platform: high QPS, adversarial users, and severe FP cost (journalists, celebrities, elections-adjacent accounts).

| Angle | Design implication |
|-------|-------------------|
| **User trust / FP cost** | Precision tiers; appeals; RESTRICT before DISABLE |
| **ATO victims** | Session revoke ≠ sybil disable |
| **Accessibility / legit automation** | Partner API allowlists; don’t ban all headless |
| **Privacy** | Tokenized fingerprints; short IP retention; purpose binding |
| **Explainability** | Ops reason codes; attacker-facing generic messages |
| **Cross-pillar** | Share entity IDs with spam, ads fraud, CIB |
| **Adversarial ML** | Shadow test; honeypot gold; assume feature inversion |
| **Safety during outages** | Fail-closed-ish on signup floods; fail-open-ish on low-harm likes |

**Enforcement ethics (interview):** silent permanent shadowbans without audit are a deal-breaker for integrity ops—prefer durable `decision_id` even if user messaging stays generic.

### 3.9 Dual-plane architecture (online vs nearline)

| Plane | Job | Latency | Output |
|-------|-----|---------|--------|
| Online | Score action; challenge/block | <40ms | BotDecision |
| Stream | Velocity / sketches | seconds | Feature updates |
| Nearline | Botnet clusters | min–hours | ClusterPropose / disable |
| Offline | Train / evaluate / shadow | hours–days | model_id |

**Deal-breaker:** nightly batch bans only—distributed low-and-slow bots win the day.

---

## 4. Architecture Diagram

```text
 +-------------------+     +----------------------+     +--------------------+
 | App / API Gateway |---->| Action Interceptor   |---->| Online Score       |
 | FB/IG surfaces    |     | (sidecar/lib)        |     | rules + models     |
 +--------+----------+     +----------+-----------+     +---------+----------+
          |                           |                           |
          |                           v                           v
          |                +----------+-----------+     +---------+----------+
          |                | Outcome apply        |     | Online Feature     |
          |                | allow/challenge/deny |     | Store + caches     |
          |                +----------+-----------+     +--------------------+
          |                           |
          |                           v
          |                +----------+-----------+     +--------------------+
          |                | Challenge Service    |     | Actor State Store  |
          |                | CAPTCHA/SMS/attest   |     | (OK/RESTRICT/...)  |
          |                +----------------------+     +---------+----------+
          |                                                         ^
          v                                                         |
 +--------+----------+     +----------------------+                 |
 | Event Stream      |---->| Stream Aggregators   |--velocity------>|
 | (sampled + full   |     | windows, sketches    |                 |
 |  high-risk)       |     +----------+-----------+                 |
 +--------+----------+                |                             |
          |                           v                             |
          |                +----------+-----------+     +-----------+------+
          |                | Graph Edge Builder   |---->| Cluster Detector |
          |                | devices, templates   |     | CC / community   |
          |                +----------------------+     +---------+--------+
          |                                                         |
          |                                                         v
          |                                              +----------+----------+
          |                                              | Enforcement Orch.   |
          +--------------------------------------------->| decisions + audit   |
                                                         +----------+----------+
                                                                    |
                    +-------------------+     +---------------------+--+
                    | Model Training    |<----| Labels: honeypot,    |
                    | offline/nearline  |     | reviews, enforcements|
                    +-------------------+     +------------------------+

 Ads fraud / Spam / CIB <--- entity IDs / cluster shares ---> Bot Detection
```

**Online path:**

```text
incoming FOLLOW
  -> load ActorState (short-circuit if DISABLED)
  -> fetch feature blob (actor, device, session)
  -> rules (hard deny signup bursts etc.)
  -> model score
  -> outcome
  -> if CHALLENGE: return challenge token; pause action
  -> if ALLOW: proceed; emit event async
```

**Nearline botnet path:**

```text
edges -> seed (honeypot hit, high score density, known bad device)
  -> expand capped subgraph
  -> score community (sync rate, template overlap, low diversity graph)
  -> auto disable if precision tier else case queue
  -> watchlist fingerprints
```

**Challenge path:**

```text
CHALLENGE issued -> user solves -> ChallengeVerify
  -> update session trust↑ or fail count↑
  -> resume or block
  -> log for training (careful: solvers exist)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Disabled actors cannot perform restricted writes** (strong state check).  
2. **Every enforcement has decision_id + reasons + policy_version.**  
3. **Online path degrades to rules** if ML store fails — never fail open on signup floods without limits.  
4. **ATO response prefers session revoke** over immediate permanent disable when history is strong.  
5. **Cluster enforce is idempotent** and reconstitution-resistant via watchlists.

#### 5.1.2 Fail-open vs fail-closed

| Action class | ML down | Rationale |
|--------------|---------|-----------|
| Signup / login burst | Fail-closed-ish (stricter rules, challenges) | Integrity |
| Like / low harm | Fail-open with rate limits | UX |
| Messaging to strangers | Stricter degrade | Spam harm |
| Ads click | Fail to ads-fraud rules | Money |

**Deal-breaker:** fail-open unlimited signups during model outage.

#### 5.1.3 Consistency

```text
ActorState in strongly consistent store (per cell)
Edge caches hold actor_epoch
Bump epoch on RESTRICT/DISABLE
Action path reads state+epoch before write
```

#### 5.1.4 Poison / feedback loops

Challenges solved by farms must not automatically label “human.”

```text
label tiers:
  gold: honeypot interaction, human review, ground-truth leaks
  silver: durable disable with low appeal overturn
  bronze: challenge outcomes (weak)
Train with weights; monitor for poisoning
```

### 5.2 Scalability

#### 5.2.1 Progressive scale

| Scale | Online | Aggregates | Graph |
|-------|--------|------------|-------|
| Baseline | Central scorer | Redis counters | Daily CC seeds |
| 10× | Cached feature blobs | Streaming windows | Hourly clusters |
| 100× | Cell scorers by user shard | Hierarchical velocity | Sharded graph expand |
| 1,000× | Edge tokens for low-risk | Approximate sketches | Multi-hop hierarchy |

#### 5.2.2 Feature blob design

```text
ActorBlob {
  actor_id, epoch,
  scalars: age, strikes, cluster_prior, ...
  velocities: packed sketches
  device_trust_summary
  updated_at
}
Multi-get 1–3 keys instead of 50
TTL + async refresh
```

#### 5.2.3 Hot keys

```text
Celebrity account inbound actions → shard by edge (actor_id, salt)
Velocity counters: count-min / hierarchical counters
Never single Redis key for “global like rate of celebrity”
```

#### 5.2.4 Sampling strategy

| Event | Sample |
|-------|--------|
| Scored high risk | 100% |
| Enforcements | 100% |
| Challenges | 100% |
| Normal likes | 0.1–1% |
| Signups | 100% or high % |

### 5.3 Maintainability

#### 5.3.1 Policy & model rollout

```text
Canary by country / surface / 1% users
Watch: challenge rate, disable precision, user happiness metrics, support tickets
Rollback model_id pin
Rules hot-deploy for breaking botnet campaigns (hours matter)
```

#### 5.3.2 Reason codes

```text
VELOCITY_ACTOR
VELOCITY_DEVICE
DEVICE_DATACENTER_FARM
CLUSTER_FOLLOW_TRAIN
TEMPLATE_SPAM
HONEYPOT_HIT
ATTESTATION_FAIL
CREDENTIAL_STUFFING
...
```

Ops see details; attackers see generic friction messages.

#### 5.3.3 Adversarial robustness

- Regular red-team botnets.  
- Feature encryption / non-obvious client signals (assume reverse engineering).  
- Ensemble models; frequent retrains.  
- Economic friction (phone reputation costs).

#### 5.3.4 Privacy

- Hash/tokenize contacts.  
- Limit raw fingerprint retention.  
- Access tiers for investigators.  
- Purpose binding: integrity vs ads ranking separation where required.

### 5.4 Online scoring deep dive

#### 5.4.1 Latency budget breakdown

```text
p99 ≤ 40ms total score budget:
  actor_state lookup:     1–3ms (cached)
  feature blob multi-get: 5–15ms
  rules:                  1–3ms
  model inference:        3–10ms (in-process)
  decision write/sidefx:  1–5ms (async where possible)
```

**Deal-breaker:** synchronous Hive/warehouse feature join on the action path.

#### 5.4.2 Model topology

| Stage | Role |
|-------|------|
| Hard rules | Signup floods, honeypot, sanctions-like device bans |
| Calibrated ML | Per `action_type` head or multi-task model |
| Cluster prior | Nearline badge folded as feature |
| Thresholds | Action-specific; signup ≪ like |

```text
score = calibrate(rules, ml, cluster_prior, velocity_z)
outcome = thresholds[action_type](score, policy_v)
```

#### 5.4.3 Feature blobs

Pack actor + device + session into 1–3 KV keys; process→Redis→FS tiers; singleflight refresh. Velocities as packed sketches/CMS counts in the blob.

#### 5.4.4 Short-circuits

```text
if ActorState == DISABLED: return BLOCK (skip ML)
if low_risk_token valid: ALLOW with periodic re-score (1000×)
if RESTRICTED and action in deny_set: BLOCK
```

### 5.5 Nearline clustering deep dive

#### 5.5.1 Why nearline

Distributed botnets stay under per-account velocity; coordination appears in **shared infra + templates + sync**.

#### 5.5.2 Coordination symptoms

| Symptom | Signal |
|---------|--------|
| Sync bursts | Cross-account action timestamps alignment |
| Template | Same comment/DM structure |
| Graph poverty | Low authentic edges; dense bot-bot edges |
| Device reuse | Many accounts per device lineage |
| Growth edges | Invite pyramids |
| Content | Same media hash |
| Honeypot density | Multiple members hit decoys |

#### 5.5.3 Seeded expansion

```text
seeds = honeypot_hits ∪ bad_device_lineages ∪ intel ∪ dense high-score cells
expand capped (max_nodes, max_hops, min_edge_weight)
cluster_score = f(sync, device_conc, template, authenticity, honeypot) - agency_prior
auto disable if precision tier else case queue
```

**Deal-breaker:** daily full-graph connected components on 3B users—expensive and noisy.

#### 5.5.4 Human farms

Lower synchrony, diverse residential devices → lean on economics, content quality, report graphs, ads payment mules; admit imperfect recall.

### 5.6 Device graphs deep dive

#### 5.6.1 Lineage vs raw fingerprint

```text
DeviceNode:
  attest_id (strong when present)
  browser_lineage (salted, evolving)
  install_id / family
Edges: USED_DEVICE, CO_ACTIVITY_WINDOW
```

Raw canvas FP alone is adversarial and unstable—prefer **lineage** with attestation when available.

#### 5.6.2 Multi-user devices

Families and internet cafés share devices. Never hard-merge accounts to one sybil on device alone; require corroboration (templates, sync, invite pyramids, honeypot).

#### 5.6.3 Residential proxies

IP/ASN weak; device + behavior + graph carry. Mark ASN type as probabilistic feature, not ban list.

#### 5.6.4 Cross-app device identity

FB + IG share integrity device graph so botnets cannot hop apps cleanly—entity resolution IDs, not raw ad identifiers for ranking.

### 5.7 Adversarial ML deep dive

#### 5.7.1 Threats

| Attack | Mitigation |
|--------|------------|
| Feature inversion / mimicry | Server-observed outcomes; ensembles; hidden costs |
| CAPTCHA solver farms | Weak human labels; attestation; cluster features |
| Label poisoning via appeals | Gold tier discipline; rate-limit train influence |
| Concept drift | Continuous eval; war-room rules |
| Training-serving skew | Same feature definitions; shadow diffs |

#### 5.7.2 Label tiers

```text
gold:   honeypot, human review, confirmed intel
silver: durable disable + low overturn
bronze: challenge outcomes (weak)
Train with weights; monitor poisoning dashboards
```

#### 5.7.3 Client signals

Treat JS/sensor hints as untrusted. Never sole-rely on client “I am human.”

### 5.8 Enforcement ladder deep dive

```text
ALLOW
SOFT_FRICTION (slow mode, reduced quota)
CHALLENGE (CAPTCHA / SMS / attest)
BLOCK_ACTION
SESSION_REVOKE          # ATO-shaped
RESTRICT_ACCOUNT        # no follows/DMs; read OK
DISABLE_ACCOUNT
DISABLE_CLUSTER + watchlist
```

| Confidence × harm | Prefer |
|-------------------|--------|
| Low × low | ALLOW / log |
| Med × med | CHALLENGE / SOFT_FRICTION |
| Med × high | RESTRICT |
| High × high | DISABLE / CLUSTER |

Challenges & attestation options:

| Challenge | Pros | Cons |
|-----------|------|------|
| CAPTCHA | Cheap-ish | Solvers |
| SMS | Costly for attacker | SIM farms; UX |
| Email | Easy | Cheap emails |
| App attestation | Strong on mobile | Not all clients |
| WebAuthn / passkey | Strong | Adoption |

**Budget controller:** global + per-surface challenge caps; prefer high-harm actions when score medium.

### 5.9 Precision / recall deep dive

#### 5.9.1 Metrics that matter

| KPI | Why |
|-----|-----|
| Precision@disable (sampled) | FP control — launch gate |
| Harm-weighted recall proxy | Impact (bad DMs, fake follows) |
| Challenge rate & solve rate | Friction budget |
| Time-to-detect botnet | Speed |
| Reconstitution 30d | Durability |
| Appeal overturn | Quality |
| Cost-per-1K-actions (attacker est.) | Economics |

#### 5.9.2 Operating point

```text
Disable threshold in extreme score tail (precision-first)
Recall via: clusters, restrict bands, challenges, watchlists
Never one global threshold across LIKE and SIGNUP
```

#### 5.9.3 Sampling for precision

Daily sample N auto-disables for human label; stratify by surface and reason_code; block model ship on precision floor breach.

### 5.10 Shadow testing deep dive

#### 5.10.1 Protocol

```text
Canary model_id_B scores in shadow on X% traffic
Log: {action, score_A, score_B, outcome_A, would_B, features_hash}
Do NOT apply B until promotion criteria met
Compare: honeypot catch, proxy bad-action, challenge would-rate, FP samples
```

#### 5.10.2 Promotion gates

| Gate | Example |
|------|---------|
| Precision@would-disable | ≥ production − ε |
| Challenge would-rate | ≤ budget |
| Honeypot recall | ≥ production |
| Support ticket proxy | no regression in canary countries |

#### 5.10.3 Rules hotfixes vs models

Breaking botnet campaigns may need **rules in hours**; models retrain in days. Shadow still applies to rule packs that expand challenge volume.

### 5.11 ATO vs bot farm

| | ATO bot | Sybil bot |
|--|---------|-----------|
| Account history | Often rich | Thin |
| Device | New/weird vs history | Many new |
| Enforcement | Session kill, reauth | Disable / cluster |
| User comms | “We secured your account” | Policy disable |

**Deal-breaker:** treating all anomalies as sybils → mass legit lockouts.

### 5.12 Failure drills

| Drill | Expected behavior |
|-------|-------------------|
| Model store outage | Rules-only; stricter signup; rate limits |
| Feature store lag | Stale blobs + conservative velocity; alert |
| Challenge vendor down | Fallback friction / attest; raise restrict |
| Celebrity viral spike | Shard velocity keys; don’t disable celeb |
| Cluster job false mega-component | Fanout caps; agency priors; human gate |
| Poisoned bronze labels | Weight collapse; gold set monitoring |

### 5.13 Progressive scale narrative

| Jump | Online | Stream | Graph / ML |
|------|--------|--------|------------|
| **→10×** | Feature blobs, cache | Velocity windows | Honeypots; hourly clusters |
| **→100×** | Cell scorers | Hierarchical CMS | Sharded expand; per-surface models |
| **→1,000×** | Edge allow-tokens | Approx sketches | Hierarchical botnets; privacy-preserving learn |

---

## 6. Wrap-Up

### 6.1 What we designed

A Meta **bot-detection platform**: **inline action scoring**, **risk-based challenges**, **nearline botnet clustering**, **enforcement with epochs/audit**, and **adversarial training loops**—scaled by feature blobs, caching, and seeded graph expansion.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Layered detection | Better coverage | System complexity |
| Risk CAPTCHA not universal | UX | Some bots pass soft paths |
| Precision on disable | Trust | Slower recall → use restrict |
| Sampled logging | Cost | Less train data on normals |
| Session vs account actions | Fair ATO handling | More states |

### 6.3 Deal-breakers

1. Universal CAPTCHA as architecture.  
2. IP-only botnet detection.  
3. Full GNN on every like.  
4. Fail-open unlimited signups when ML dies.  
5. Labeling all CAPTCHA solvers as humans.  
6. Disabling ATO victims as sybils.  
7. One threshold for all action types.  
8. Training solely on challenge outcomes (poisoning / solver bias).  
9. Hard-merge family devices into one sybil cluster.

### 6.4 10× / 100× / 1,000× story

- **10×:** Feature blobs; stream velocity; honeypots.  
- **100×:** Cell scorers; sharded graph; per-surface models.  
- **1,000×:** Edge allow-tokens for low risk; hierarchical clusters; privacy-preserving learning.

### 6.5 Failure-drill one-liners

| Drill | One-liner |
|-------|-----------|
| ML down | Rules + signup fail-safe |
| Solver farms | Challenges ≠ gold human |
| ATO burst | Session revoke first |
| Distributed low-rate | Nearline clusters |
| Precision slip | Raise disable bar; use restrict |

### 6.6 Interview closing line

> “Bots are an economic distributed systems problem: score actions in milliseconds, find botnets in minutes-to-hours, raise attacker cost with precision-tiered enforcement—not a single classifier or a global CAPTCHA wall.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Threat model

**Q1: What makes a botnet “distributed”?**  
A: Many accounts/IPs/devices, often residential proxies, low per-node rate to evade velocity — requires graph/template detection beyond per-IP thresholds.

**Q2: Automation vs inauthentic?**  
A: Some automation allowed (APIs); inauthentic coordinated behavior and policy-violating automation are targets. Encode intent/surface policy.

**Q3: Human click farms?**  
A: Partially detectable via coordination, economics, quality of graph, repeated templates; pure “bot ML” insufficient—say so.

**Q4: Why economic view?**  
A: Attackers optimize ROI; challenges, phone costs, disable speed change ROI even without perfect recall.

**Q5: Scrapers vs engagement bots?**  
A: Different actions/features (read fanout vs write graphs); share device/IP risk; separate models/thresholds.

### 7.2 Signals & ML

**Q6: Best online signals?**  
A: Velocity (multi-key), device trust/attestation, account graph age, cluster prior, client integrity — fused.

**Q7: Why behavioral timing features decay?**  
A: Adversaries randomize; still useful in ensembles; don’t bet the farm.

**Q8: Graph features online?**  
A: Precomputed cluster_prior / risk badges; not live CC.

**Q9: Cold start signup?**  
A: Heavier reliance on device/IP/phone reputation, attestation, invite edge quality.

**Q10: Label leakage?**  
A: Don’t train on features only available post-enforce in a leaking way; careful time travel.

### 7.3 Systems

**Q11: How to serve 20M scores/s?**  
A: Cell sharding, in-process models, feature blob cache, short-circuit actor state, async logging.

**Q12: Where does interceptor live?**  
A: Library/sidecar in action services for latency; central service for complex flows; consistency of policy_version critical.

**Q13: Redis velocity pitfalls?**  
A: Hot keys, TTLs, memory — use hierarchical aggregation / CMS / sharded counters.

**Q14: Exactly-once enforcement?**  
A: Idempotent decision_id; at-least-once consumers OK.

**Q15: Multi-region?**  
A: Score in home cell; replicate actor state globally for login anywhere; watchlist pubsub.

### 7.4 Clustering

**Q16: Why seeded expansion?**  
A: Full-graph CC at Meta scale is expensive and noisy; seeds from high-precision events focus compute.

**Q17: Shared phone = bot?**  
A: Not alone (families, carriers); use as edge weight with other signals.

**Q18: How to handle celebrity community managers?**  
A: Allowlists / agency priors; high follow rates with authentic graph patterns.

**Q19: Temporal bots that sleep?**  
A: Long-window features; watchlists after partial detects; content template memory.

**Q20: Cross-platform botnet (FB+IG)?**  
A: Shared integrity entity graph; enforce on both.

### 7.5 Enforcement & UX

**Q21: When CAPTCHA?**  
A: Medium risk bands on meaningful actions; never as sole global gate.

**Q22: Soft restrict vs hard disable?**  
A: Restrict when uncertain but harm medium (limit follows/DMs); disable when high precision.

**Q23: Appeals?**  
A: Required for disables; feed overturns into FP analysis.

**Q24: Messaging to users?**  
A: Generic security messaging; don’t reveal exact features.

**Q25: Rate limits as bot control?**  
A: First line for bursts; insufficient alone against distributed low-rate bots.

### 7.6 Adversarial & ML ops

**Q26: CAPTCHA solving services?**  
A: Expect them; combine with attestation, costlier checks, cluster features; treat solve as weak human label.

**Q27: Feature inversion by attackers?**  
A: Assume client signals compromised; prefer server-side observed behavior + hard-to-fake costs.

**Q28: Concept drift?**  
A: Continuous evaluation sets; war-room rules; scheduled retrain.

**Q29: Honeypot design?**  
A: Attractive fake entities; interactions → gold labels; keep secret distribution.

**Q30: Poisoning via mass appeals?**  
A: Rate-limit influence of appeals on train; require review confirmation for gold.

### 7.7 Estimation drills

**Q31: Feature gets at 2M actions/s × 20 keys?**  
A: 40M gets/s — forces blobs/caching; cite as deal-breaker for naive design.

**Q32: CAPTCHA at 1% of 2M/s?**  
A: 20K/s — still huge; show need for tighter budgets and risk targeting.

**Q33: Cluster job: 100K seeds × 2K nodes?**  
A: 200M node visits/run — feasible with distributed graph if bounded; not unbounded BFS.

### 7.8 Alternatives & deal-breakers

**Q34: Only unsupervised anomaly?**  
A: Useful for discovery; weak alone for enforcement precision.

**Q35: Blockchain / PoW for every like?**  
A: UX deal-breaker; mention as extreme economic friction not viable socially.

**Q36: Central Python scorer RPC each action?**  
A: Latency/availability risk at scale — embed models in cells.

**Q37: Ban all datacenter ASNs?**  
A: Breaks cloud users/partners; use as soft feature.

### 7.9 Interview craft

**Q38: How to open?**  
A: Define bot/botnet, surfaces, harm types; online vs nearline; enforcement ladder; non-goals.

**Q39: What impresses L5+?**  
A: Latency budget math, feature blobs, ATO vs sybil, honeypot labels, reconstitution, challenge budgets, progressive cells.

**Q40: Common mistake?**  
A: IP blocklists + universal CAPTCHA, or designing only offline clustering without inline path.

**Q41: Closing metrics?**  
A: Bad action rate, precision@disable, challenge rate, time-to-detect, reconstitution.

**Q42: Tie to Meta integrity?**  
A: Shared entity IDs with spam, ads fraud, CIB; bot detection supplies automation priors to those systems and consumes payment/device reputation.

### 7.10 Online scoring, clusters, devices (extra)

**Q43: Break down a 40ms online score budget.**  
A: State check → feature blob multi-get → rules → in-process model → threshold by action_type; everything precomputed; no warehouse joins.

**Q44: How do device graphs avoid family false positives?**  
A: Device is an edge weight, not identity; require corroborating templates/sync/honeypot/invite pyramids before cluster disable; multi-user priors.

**Q45: What is seeded expansion and why not full CC?**  
A: Start from high-precision seeds (honeypot, bad devices); expand capped subgraphs; full-graph CC is costly and merges unrelated noise.

**Q46: How do you set precision vs recall for disables?**  
A: Precision-first on DISABLE (sampled gate); harm-weighted recall via RESTRICT/CHALLENGE/clusters/watchlists; separate thresholds per action_type.

### 7.11 Adversarial ML, shadow, drills

**Q47: Why shadow test before shipping a model?**  
A: Compare would-have decisions on live traffic without user harm; gate on honeypot recall, challenge would-rate, precision samples, support proxies.

**Q48: Why aren’t CAPTCHA solves gold “human” labels?**  
A: Solver services exist; treat as bronze/weak; prefer honeypots and human review for gold.

**Q49: ATO vs sybil—one sentence each on enforcement.**  
A: ATO: revoke sessions and reauth a valuable account. Sybil: disable/restrict thin coordinated accounts and their cluster.

**Q50: Give three deal-breakers for bot detection interviews.**  
A: Universal CAPTCHA; IP-only detection; fail-open unlimited signups when ML is down.

**Q51: How does edge allow-token help at 1,000×?**  
A: Low-risk sessions carry short-lived signed risk band; skip full feature fetch until expiry/re-score—cuts FS QPS dramatically.

**Q52: Meta T&S closing metrics?**  
A: Bad-action rate, precision@disable, challenge budget health, time-to-detect botnet, reconstitution 30d, appeal overturn—plus cross-pillar entity share with spam/ads fraud/CIB.

---

### Appendix A — Online score pseudocode

```text
def score_action(action):
  state = actor_state.get(action.actor_id)
  if state == DISABLED: return BLOCK_ACTION
  if state == RESTRICTED and action.type in restricted_set:
    return BLOCK_ACTION
  blob = feature_cache.get_blob(action.actor_id, action.device_id, action.session_id)
  hard = rules.eval(action, blob)
  if hard.deny: return enforce(hard)
  s = model.predict(action.type, blob, action.context)
  s = apply_cluster_prior(s, blob.cluster_prior)
  return outcome_from_thresholds(action.type, s, policy_v)
```

### Appendix B — Velocity aggregator

```text
keys:
  actor:{id}:{action}:{window}
  device:{id}:{action}:{window}
  ip:{ip}:{action}:{window}
on event: incr all keys with TTL
score uses z-score vs baseline or absolute caps
windows: 1m, 1h, 1d
```

### Appendix C — Cluster detection

```text
seeds = honeypot_hits ∪ high_disable_density_devices ∪ intel
for seed in seeds:
  g = expand(seed, max_nodes=2000, edge_types=[DEVICE, TEMPLATE, SYNC])
  if cluster_score(g) >= T_auto: disable_cluster(g)
  elif cluster_score(g) >= T_review: open_case(g)
```

### Appendix D — Feature blob schema

```json
{
  "actor_id": "u1",
  "epoch": 44,
  "account_age_h": 120,
  "graph_authenticity": 0.12,
  "device_trust": 0.4,
  "cluster_prior": 0.81,
  "vel": {"follow_1h": 35, "like_1m": 20},
  "strikes_30d": 2
}
```

### Appendix E — Outcome thresholds (example)

| Action | Challenge | Block | Disable escalate |
|--------|-----------|-------|------------------|
| LIKE | 0.90 | 0.97 | rare |
| FOLLOW | 0.80 | 0.92 | cluster |
| SIGNUP | 0.55 | 0.75 | rules |
| LOGIN | 0.70 | 0.90 | session |
| MESSAGE | 0.75 | 0.88 | restrict |

### Appendix F — Enforcement fanout

```text
disable_actor(actor_id, decision_id):
  write state DISABLED + epoch++
  revoke sessions
  invalidate feature caches
  notify spam/ads systems
  audit log
```

### Appendix G — Honeypot types

| Type | Goal |
|------|------|
| Decoy accounts | Engagement bots |
| Decoy content | Comment spam |
| Trap API URLs | Scrapers |
| Canary credentials | Stuffing |

### Appendix H — NFR card

```text
Score p99 < 40ms
Signup floods fail-safe
No universal CAPTCHA
Precision-tier disables
ATO ≠ sybil handling
Seeded graph not full CC
```

### Appendix I — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Blobs, stream velocity, honeypots |
| 100× | Cell scorers, sharded graph |
| 1,000× | Edge tokens, hierarchical botnet detect |

### Appendix J — Client signals (untrusted)

```text
Treat as hints: sensor noise, JS timing, canvas FP
Server-observed ground truth: request patterns, graph effects, payment
Never sole rely on client “I am human” flag
```

### Appendix K — Training pipeline

```text
gold labels -> daily train
silver weak labels -> semi-supervised
evaluate on delayed holdout + adversarial set
ship model_id via model store; scorers pull
```

### Appendix L — Actor state machine

```text
OK -> RESTRICTED -> DISABLED
OK -> DISABLED (high precision)
DISABLED -> OK via appeal only
SESSION_REVOKED orthogonal to account state
```

### Appendix M — Sync score idea

```text
For accounts in candidate set, compute correlation of action timestamps in buckets
High alignment + low organic diversity → bot synchrony
```

### Appendix N — Comparison table

| Method | Latency | Precision | Recall on distributed |
|--------|---------|-----------|------------------------|
| IP ban | Fast | Low | Low |
| Velocity | Fast | Med | Low-med |
| ML online | Fast | Med-high | Med |
| Graph cluster | Slow | High | High |
| Honeypot | Event-driven | Very high | Low coverage |

### Appendix O — Budget controller pseudocode

```text
def allow_challenge(surface):
  if challenges_last_min[surface] > cap[surface]: return RATE_LIMIT_INSTEAD
  return CHALLENGE
```

### Appendix P — Watchlist

```text
WatchItem { device_lineage, phone_hash, template_id, ttl, source }
On signup: elevate score / require stronger proof
```

### Appendix Q — Cross-system interfaces

| System | Exchange |
|--------|----------|
| Ads fraud | click quality prior |
| Spam | template clusters |
| CIB | entity clusters |
| Payments | mule instruments |
| Login | credential stuffing scores |

### Appendix R — Privacy notes

```text
IP retention short unless under investigation
Fingerprints salted hashes
Reviewer tools show minimized PII
```

### Appendix S — 30m interview checklist

1. Define bot/botnet + harms.  
2. Online latency budget + features.  
3. Nearline clusters + seeds.  
4. Enforcement ladder + ATO distinction.  
5. Labels/honeypots/adversaries.  
6. 10×/100×/1,000×.  
7. Deal-breakers.

### Appendix T — Worked example

```text
2M actions/s, 10% need scoring beyond short-circuit = 2M still (assume all)
Feature blob cache 95% → 100K blob loads/s from FS
Model 5µs in-process → CPU modest vs network
Challenges at 0.05% → 1K/s — operable
Cluster: 10K seeds/hour × 1K expand = 10M — OK on graph workers
```

### Appendix U — Why not block all headless browsers?

```text
Breaks accessibility tools, automation partners, test infra
Detect abuse behavior; partner allowlists for APIs
```

### Appendix V — Glossary

| Term | Meaning |
|------|---------|
| Sybil | Many fake accounts |
| ATO | Account takeover |
| Challenge | Step-up proof |
| Honeypot | Decoy for labels |
| Reconstitution | Botnet relaunch |
| Feature blob | Packed online features |
| Actor epoch | State version for cache |

### Appendix W — Rule examples

```text
R1: >20 signups/hour from same device lineage -> block signup
R2: credential stuffing bloom hit -> challenge/login lock
R3: honeypot engage -> high precision cluster seed
R4: disabled cluster watchlist device -> challenge+restrict
```

### Appendix X — Canary metrics

```text
challenge_rate
disable_rate
precision_sample
mau_retention_delta
support_contacts_auth
spam_prevalence_proxy
```

### Appendix Y — Edge allow token (1000×)

```text
For low-risk sessions issue short-lived token:
  {session, risk_band, exp, sig}
Action path trusts token until expiry; periodic re-score
Cuts feature fetch storm for heavy browsers
```

### Appendix Z — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| Gatekeeper / config | Policy flags |
| TAO/graph | Authenticity features |
| Fna / request infra | IP/ASN signals |
| Challenge platform | CAPTCHA/SMS |
| Ads fraud | Shared bots |
| Organic CIB | Clusters |
| Model store | Scorer deploy |

---

*End of Bot Detection (Distributed Botnet) system design.*
