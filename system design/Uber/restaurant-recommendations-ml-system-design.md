# System Design: Restaurant Recommendations (ML System Design)

> **Focus areas:** Two-tower / ranking models · Candidate generation · Feature store · Training/serving skew · Offline eval · Online A/B · Feedback loops · Cold start · Geo constraints  
> **Style:** End-to-end **ML system** design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — ML system design for Uber Eats restaurant recommendations (pairs with feed HLD)  
> **Quality bar:** Train/serve parity; geo eligibility not left to the model alone; metrics beyond accuracy

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

Goal: design the **ML system** that powers restaurant recommendations for Uber Eats—data → features → models → offline eval → online serving → experimentation → monitoring—under marketplace and geo constraints.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Focus | ML lifecycle + serving | Full feed caching HLD (sibling) |
| Output | Scores / ranked candidates | Courier dispatch |
| Constraints | Must respect deliverability/open | Pure Netflix non-geo recs |
| Uber lens | Marketplace feedback loops, geo | Kaggle-only modeling |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Objective? | Increase orders / GMNV with UX constraints | Multi-objective |
| F2 | Surface? | Home feed “For You”, carousels, “similar” | Multiple models/slots |
| F3 | Candidates? | Nearby eligible restaurants | Retrieval + filters |
| F4 | Labels? | Clicks, adds, orders, repeats | Attribution windows |
| F5 | Cold start? | New users & new merchants | Exploration + priors |
| F6 | Context? | Time, location, weather, device | Context features |
| F7 | Diversity? | Cuisine diversity | Re-rankers |
| F8 | Fairness? | Avoid starving new merchants | Exploration quotas |
| F9 | Explainability? | Light (“because you ordered X”) | Optional |
| F10 | Latency? | In feed budget (~tens of ms for scoring) | ANN + compact models |
| F11 | Experiments? | Continuous A/B | Exp platform |
| F12 | Human overrides? | Ops boosts / bans | Rules layer |

**MVP scope:**

1. Logging pipeline for impressions/interactions/orders.  
2. Feature store (batch + some realtime).  
3. Candidate generation (geo + ANN two-tower).  
4. Ranking model (gradient boosted trees or small NN).  
5. Offline evaluation + training jobs.  
6. Online serving path with fallbacks.  
7. A/B tests; basic monitoring (AUC, calibration, business metrics).

**Out of MVP:** fully automated multi-objective RL, generative meal planning, on-device models.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Scoring latency | p99 < 30–50ms for L2 on ~50–100 items |
| N2 | Retrieval latency | p99 < 20–40ms ANN+geo |
| N3 | Train/serve skew | Monitored; critical features validated |
| N4 | Freshness | Merchant embeddings daily; user realtime counters minutes |
| N5 | Availability | Fallback non-ML rank always |
| N6 | Compliance | Location & PII handling |

### 1.3 Cases

**Happy:** User opens feed → retrieve 500 → filter → score → top 30 → order → label improves model.  

| Case | Behavior |
|------|----------|
| New user | Popular in cell + exploration |
| New restaurant | Content priors + boost exploration |
| Position bias | Propensity logging / IPS / randomization |
| Feedback loop popularity bias | Exploration / calibration |
| Merchant suddenly closed | Filter layer not model |
| Feature delay | Stale feature defaults + monitors |
| Bad model deploy | Auto rollback on guardrail metrics |
| Sparse city | Transfer priors from similar cities |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 1M | 10M | 100M | 100M+ |
| Impressions / day | 20M | 200M | 2B | 10B |
| Orders / day | 500K | 5M | 50M | 100M+ |
| Restaurants | 50K | 500K | 5M | 20M |
| Feature compute | 1 cluster | 10× | Lakehouse | Multi-region |
| Models in prod | 1 ranker | +towers | Many slots | Platform |

**Jumps:** 10× feature platform; 100× ANN retrieval + realtime features; 1,000× multi-task multi-slot platform with automated training.

### 1.5 Scope repeat-back

> ML recommendation system for geo-constrained restaurant ranking: logged feedback → features → two-stage retrieval/rank models → offline eval → low-latency serving with filters/rules → A/B and monitoring—with explicit cold-start and bias controls.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Data volume

```text
Baseline 20M impressions/day × 500 B log ≈ 10 GB/day raw logs
100×: 2B × 500 B ≈ 1 TB/day → columnar lake, sampling for some training
Orders 50M/day at 100× as labels (rarer positives)
```

### 2.2 Serving QPS

```text
Feed peak 20K QPS → each needs retrieval+score
ANN query 20K/s; ranker 20K/s × 100 items = 2M score-evals/s → batch matmul / tree ensembles optimized
```

### 2.3 Embedding index

```text
5M restaurants × 128-d float32 ≈ 5e6 × 512 B ≈ 2.5 GB (+ replicas)
Fits memory ANN (HNSW/IVF) sharded by city/region
```

### 2.4 Bottlenecks

1. Train/serve skew silent failures  
2. Popularity feedback loops  
3. Hot city ANN/feature store  
4. Label delay (order after browse)  
5. Feature explosion cost  

---

## 3. High-Level Design

### 3.1 Problem formulation

| Stage | Task | Typical model |
|-------|------|---------------|
| Retrieval | User×context → candidate IDs | Two-tower embeddings + geo |
| Ranking | Score P(order\|user, restaurant, context) | GBT / DNN |
| Re-rank | Diversity, business rules | Heuristics |

**Labels:** prefer **order** (or add-to-cart) over click; clicks noisy.

### 3.2 Data & labels

```text
impression_log: user, restaurant, position, context, ts, request_id
interaction: click/add
conversion: order within attribution window W
join → training examples with propensity weights if randomized
```

### 3.3 Features

| Type | Examples | Freshness |
|------|----------|-----------|
| User | cuisine affinity, AOV, order count | Batch daily + realtime counters |
| Restaurant | rating, cuisine, price_tier, embedding | Daily |
| Context | hour, weather, cell, device | Request-time |
| Cross | user×cuisine historical CTR | Batch |
| Realtime | session clicks, merchant busy | Seconds–minutes |

**Deal-breaker:** Using post-click leakage features at train that aren’t available at serve.

### 3.4 Feature store

```text
Offline: Spark/Flink jobs → Hive/Iceberg tables → training
Online: KV / Redis / specialized store keyed by user_id / restaurant_id
Point-in-time correct joins for training (avoid future leakage)
```

### 3.5 Models

**Retrieval (two-tower):**

```text
u = UserTower(user_features, context)
r = RestaurantTower(restaurant_features)
score = u · r
Train with sampled softmax / in-batch negatives (geo-hard negatives better)
Index r vectors in ANN per city
```

**Ranker:**

```text
GBT on dense+sparse features for top candidates
Calibrate to probabilities for blending with rules
```

### 3.6 Serving path (aligned with feed)

```text
geo candidates ∪ ANN candidates → union → hard filters → L1 (tower/dot) → L2 ranker → rules
```

### 3.7 Training pipeline

```text
daily/ hourly:
  generate PIT features
  build datasets
  train → evaluate vs offline suite
  if pass gates: register model → canary → ramp
```

### 3.8 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Retrieval | Two-tower + geo | Scale | Score all 5M with L2 |
| Ranker | GBT MVP | Strong tabular | Tiny net without features |
| Negatives | Geo-hard | Better than random | Random-only forever |
| Exploration | ε / bandit slots | Cold start | Pure greedy popularity |
| Objective | Primary order + guardrails | Business | CTR-only optimization |

### 3.9 Components

1. Logging / analytics lake  
2. Feature pipelines + store  
3. Training platform  
4. Model registry  
5. ANN index builders  
6. Online retrieval service  
7. Online ranker service  
8. Rules / diversity  
9. Experimentation  
10. Monitoring / drift  
11. Fallback heuristic ranker  

---

## 4. Architecture Diagram

```text
Apps --> Feed --> Filters --> Retrieval Service --> Ranker Service --> Rules --> Feed
                      ^              ^                  ^
                      |              |                  |
                 Hours/Online   ANN Indexes      Feature Store (online)
                                     ^                  ^
                                     |                  |
                              Index Builder      Feature Jobs
                                     ^                  ^
                                     +------ Lake <----- Logging
                                              ^
                                         Training / Eval
                                              v
                                         Model Registry
```

### 4.1 Online scoring sequence

```text
request(user, loc, ctx)
  features = fs.get(user, ctx)
  geo = geo_retrieve(loc)
  ann = ann_query(user_embedding(features), city)
  cands = unique(geo ∪ ann)
  cands = hard_filter(cands)
  l1 = tower_score(cands) top 100
  feats = fs.get_many(restaurants)
  scores = ranker(l1, feats, ctx)
  return rules(scores)
```

### 4.2 Training PIT join

```text
for each impression at ts:
  user_feats = as_of(ts - ε)
  rest_feats = as_of(ts - ε)
  label = order in (ts, ts+W]
```

---

## 5. Design Deep Dive

### 5.1 Reliability / ML invariants

1. Hard geo/open filters **outside** model.  
2. Feature parity checks train vs serve.  
3. Fallback path if ranker/ANN fails.  
4. Model rollout gated on offline + online guardrails.  
5. Idempotent/robust logging (`request_id`).  
6. No leaked future labels in training.  
7. Calibration monitored (predicted vs actual order rate).  
8. Bias/popularity monitors.  
9. PII minimized in feature logs.  
10. City canaries before global ramp.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Batch features; GBT rank; geo retrieval only |
| 10× | Feature store; daily two-tower; A/B |
| 100× | ANN per city; realtime counters; multi-slot |
| 1000× | Auto-training; multi-task; bandits; multi-region indexes |

### 5.3 Maintainability

- Feature ownership catalog  
- Model cards (intended use, metrics)  
- Shadow traffic for new rankers  
- Reproducible training configs  
- Data quality alerts (null rates)

### 5.4 Progressive scale narrative

**1×:** Logistic/GBT on hand features; geo candidates; daily train.  
**10×:** Embeddings; feature store; proper offline suite.  
**100×:** Hard-negative training; realtime session features; exploration platform.  
**1000×:** Unified recs platform across carousels; automated drift response.

### 5.5 Feedback loops & bias

Popular restaurants get more impressions → more orders → more popularity.

Mitigations: propensity weighting, exploration quotas for new merchants, diversity re-rank, calibrate by segment.

### 5.6 Cold start

| Entity | Strategy |
|--------|----------|
| New user | Context popular + onboarding prefs |
| New restaurant | Content features (cuisine, price, menu text embeddings); exploration boost |
| New city | Transfer models; local fine-tune |

### 5.7 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Model decides open/closed | Wrong UX |
| Optimize CTR only | Clickbait low conversion |
| No fallback | Outage |
| Ignore position bias | Offline≠online |
| Train with serve-unavailable features | Skew SEV |
| Global ANN without city shard | Irrelevant far restaurants |

---

## 6. Wrap-Up

### 6.1 Designed

ML recsys: logging → PIT features → two-tower retrieval + GBT/DNN rank → rules → serving with filters → offline/online eval → experimentation/monitoring—geo-aware, cold-start aware, skew-aware.

### 6.2 Decisions to defend

1. Multi-stage retrieval/rank  
2. Order-centric labels  
3. Feature store + PIT joins  
4. Hard filters outside model  
5. Exploration for cold start  
6. Guardrailed rollouts + fallback  
7. City-sharded ANN  

### 6.3 Risks

- Skew  
- Feedback loops  
- Label delay  
- Marketplace gaming  
- Segment unfairness  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Objective + constraints |
| 5–15 | Labels/features/PIT |
| 15–28 | Retrieval + rank models |
| 28–38 | Serving + fallback |
| 38–45 | Eval, bias, rollout |

### 6.5 Closer

> **Restaurant recs ML:** geo-filtered multi-stage models with point-in-time features, order-based labels, exploration for cold start, and ruthless train/serve parity—business metrics and guardrails over leaderboard AUC alone.

---

## 7. Deeper / Related Interview Questions

### 7.1 Modeling

**Q: Why two-tower?**  
A: Cheap retrieval via ANN; separates user/item compute.

**Q: Why not only collaborative filtering?**  
A: Cold start + context + geo; CF as one signal.

**Q: Softmax negatives?**  
A: In-batch cheap; add geo-hard negatives for quality.

### 7.2 Evaluation

**Q: Offline metrics?**  
A: AUC/PR, logloss, NDCG@K, calibration; sliced by city/new users.

**Q: Why offline≠online?**  
A: Position bias, UI, delayed labels, non-stationarity.

**Q: Counterfactual?**  
A: IPS/SNIPS if propensities logged; otherwise online A/B.

### 7.3 Features

**Q: Realtime vs batch?**  
A: Session affinity realtime; long-term taste batch.

**Q: Leakage examples?**  
A: Using “ordered_at” before impression; post-order rating at browse time.

### 7.4 Serving

**Q: How to hit latency?**  
A: Precompute restaurant towers; cache user tower short TTL; batch ranker.

**Q: Feature store down?**  
A: Defaults + fallback ranker.

### 7.5 Marketplace

**Q: Boost paid placement?**  
A: Separate auction/slot with disclosure; don’t silently corrupt organic model labels—or model explicitly.

**Q: Courier constraints?**  
A: Eligibility/ETA features; still filter undeliverable.

### 7.6 Ethics / fairness

**Q: Minority cuisines starved?**  
A: Diversity constraints; slice metrics.

### 7.7 Interview traps

| Trap | Pushback |
|------|----------|
| Only discuss model architecture | Need data+serve+eval |
| Ignore geo | Product fail |
| “Accuracy 99%” without definition | Vague |
| No A/B plan | Incomplete |
| Train on clicks only | Weak objective |

### 7.8 Metrics (online)

| Metric | Why |
|--------|-----|
| Order conversion | Primary |
| GMNV / contribution profit | Economics |
| Latency p99 | UX |
| New merchant share | Health |
| Refund/cancel after order | Quality |
| Fallback rate | Systems |

### 7.9 Feed sibling

Serving integration details in `uber-eats-feed-system-design.md`.

---

## 8. Appendices

### 8.1 Label definition

```text
label = 1 if exists order with same user, restaurant,
              order_time in (impression_ts, impression_ts + 24h]
              and request attribution matches (last touch / click)
else 0
```

### 8.2 Feature catalog (sample)

| Name | Entity | Type |
|------|--------|------|
| user_orders_30d | user | int |
| user_cuisine_hist | user | map |
| rest_rating | restaurant | float |
| rest_price_tier | restaurant | enum |
| ctx_local_hour | context | int |
| ctx_h3_cell | context | id |
| session_clicks | session | list |
| eta_bucket | cross | int |

### 8.3 API (internal scoring)

```text
POST /score
{user_id, context, candidate_ids[]}
→ {scores: [{id, p_order, model_version}]}
```

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| PIT | Point-in-time correct features |
| ANN | Approximate nearest neighbors |
| Two-tower | Separate user/item encoders |
| IPS | Inverse propensity scoring |
| Guardrail | Metric that blocks rollout |
| Skew | Train/serve mismatch |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Logs, GBT, geo candidates, A/B |
| 10× | Feature store, PIT, embeddings |
| 100× | ANN, realtime feats, exploration |
| 1000× | Multi-slot platform, auto train, drift |

### 8.6 Offline gate example

```text
must_improve: NDCG@20 on holdout city mix ≥ +0.5%
must_not_regress: calibration ECE < threshold
slice_gates: new_user NDCG not worse by >X
```

### 8.7 Hard negatives

```text
Sample restaurants in same H3 parent cell user didn’t order
Better than random worldwide negatives
```

### 8.8 Interview “say this” (60s)

> Log impressions with positions; build point-in-time features; retrieve with geo plus two-tower ANN; rank with a calibrated model optimizing orders under diversity/business rules; enforce open/ETA filters outside the model; ship via offline gates and online A/B with fallbacks; fight popularity bias with exploration and propensity-aware training.

### 8.9 Reliability tests

1. Feature missing → default path works.  
2. ANN index lag → geo-only still OK.  
3. Bad model canary → auto rollback.  
4. Closed restaurant never scored into feed as open.  
5. PIT checker catches leakage job bug.  

### 8.10 SLOs

| SLO | Target |
|-----|--------|
| Ranker p99 | < 50ms |
| Skew alert | page within minutes |
| Guardrail breach rollback | < 15 min |
| Fallback availability | > 99.9% feed |

### 8.11 Training schedule

```text
Hourly: realtime counter aggs
Daily: full train ranker + towers
Weekly: hyperparam search / larger retrain
```

### 8.12 Related systems map

```text
Logs → Lake → Features → Train → Registry
                     ↓
                 Online FS / ANN
                     ↓
            Retrieval → Ranker → Feed Rules
```

### 8.13 Position bias note

```text
Log propensity if randomized exploration
Else use position as feature carefully + online tests
```

### 8.14 Multi-objective blending

```text
score' = w1*p_order + w2*expected_margin - w3*eta_penalty + exploration_bonus
tune w via Bayesian opt / online
```

### 8.15 Extra traps

| Trap | Pushback |
|------|----------|
| Embeddings without geo filter | Long-distance junk |
| Daily batch only forever | Session intent missed |
| One global model metric | Hides city regressions |

### 8.16 Menu-item extensions

Same architecture; item towers denser; more cold start—phase 2 carousel “dishes for you.”

### 8.17 Fraud / gaming

Merchants gaming ratings/orders: trust signals as features; don’t let paid traffic pollute organic labels without flags.

### 8.18 Unit checks

```text
5M × 128-d float32 ≈ 2.5 GB restaurant index
20K QPS user tower: cache user embedding 30–60s
```

### 8.19 Model card checklist

- [ ] Objective  
- [ ] Training data window  
- [ ] Known failure slices  
- [ ] Latency budget  
- [ ] Owner oncall  

### 8.20 Brownout for ML

```text
1. Disable exploration
2. Disable L2 → L1/heuristic
3. Keep filters
4. Freeze training deploys during SEV
```

---


### 8.21 Logging taxonomy

| Event | Required fields | Notes |
|-------|-----------------|-------|
| impression | request_id, user, rest, pos, ctx | Always |
| click | request_id, rest | Optional |
| add_to_cart | request_id, rest | Stronger |
| order | order_id, rest, gmnv | Label |
| discard | reason | Filter analytics |

### 8.22 Feature parity test

```text
For sampled online requests, persist feature vector hash
Later join offline PIT recompute
Alert if mismatch rate > ε
```

### 8.23 ANN index build pipeline

```text
daily:
  export restaurant embeddings (version V)
  build HNSW/IVF per city_shard
  smoke query recall@K vs brute on sample
  swap pointer atomically (blue/green index)
```

### 8.24 Realtime counters

```text
session_clicks: Redis list / HyperLog / counter with TTL 30–120m
user_orders_today: incr on order events
merchant_busy_score: from prep-time signals
Defaults to 0 if missing—model trained with missingness indicators
```

### 8.25 Offline/online metric dictionary

| Name | Definition |
|------|------------|
| NDCG@20 | Ranking quality vs labeled orders |
| AUC | Pairwise order vs non-order |
| ECE | Calibration error |
| OPV | Orders per view (online) |
| CTR | Clicks/impressions (guardrail only) |

### 8.26 Exploration policies

| Policy | Mechanism |
|--------|-----------|
| ε-greedy | Random eligible in slot with p=ε |
| Thompson | Beta on new merchants |
| Quotas | Reserve top-N slots for new/low-impression |

Log propensity for each explored impression.

### 8.27 Failure: embedding drift

```text
Symptom: recall drops; online conversion dips on ANN path
Mitigation: fall back geo-only; rebuild index; compare embedding norms/distributions
```

### 8.28 Interview “layers” quick draw

```text
Data → Features → Models → Eval → Serve → Experiment → Monitor → (loop)
Filters & rules wrap serve; marketplace constraints wrap filters
```

### 8.29 Sample training config

```yaml
model: two_tower
dim: 128
negatives: in_batch + geo_hard:20
optimizer: adam
lr: 1e-3
batch: 4096
city_sample_cap: true
```

### 8.30 Guardrail rollback example

```text
if online_orders_per_viewer drops > 2% relative vs control for 30m
   AND not explained by demand shock metric
then: halt ramp; revert to previous model_version
```


*End of restaurant recommendations ML system design.*
