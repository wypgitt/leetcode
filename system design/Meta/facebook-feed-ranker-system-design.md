# System Design: Facebook Feed Ranker (Single ML Ranking Stage)

> **Focus areas:** ONE ranking stage for ML candidates · Feature fetch · Model scoring · Timeout budgets · Fallback · Candidate→score→order  
> **Style:** Deep-dive on the **ranker stage** inside News Feed (not the entire Facebook product)  
> **Quality bar:** Explicit stage boundaries, feature freshness vs latency, deal-breakers for “score 10K candidates with huge models inline”  
> **Interview theme:** Meta L5+ ranking systems — given retrieved candidates, produce a ranked list under a hard latency budget

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

Goal: **bound the product**—design **one ranking stage** that takes a set of **ML candidates** (post IDs already retrieved) and returns a **scored, ordered list** for the News Feed mixer, under a strict latency SLO.

### 1.0 What this is / is not

| Dimension | **Feed ranker stage (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Score & order ~hundreds of candidates | Full FB app, graph, or CDN media |
| Input | Viewer context + candidate IDs | Raw global corpus scan |
| Output | Ranked candidates + score vector | Final pixels / ads auction (hooks) |
| Success | Relevant order within p99 budget | Perfect offline NDCG alone |
| Training | Serving features + model host | Full training platform (hooks) |

**Scope statement:** Design the **ranking stage** of Facebook News Feed: feature hydration, model inference, multi-task scores, truncation, timeouts/fallbacks—assuming retrieval already produced candidates.

**Say early:** Retrieval (light/heavy ranker cascade) may exist upstream; we own **one** scoring stage (e.g. “main ranker” / “precision ranker”).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Stage input? | `viewer_id` + ~200–1000 candidate `post_id`s | Batch score API |
| F2 | Stage output? | Ordered list + scores (P(click), P(like), …) | Multi-head score vector |
| F3 | Model type? | Neural net / GBDT ensemble; multi-task | Model hosting + feature parity |
| F4 | Features? | User, post, author, edge, context | Feature store / online fetch |
| F5 | Latency budget? | Entire ranker ~50–100ms p99 | Parallel fetch + early exit |
| F6 | Filtering? | Integrity / integrity scores applied here or pre | Policy filters in stage |
| F7 | Diversity? | Light diversity here or in mixer | Prefer mixer for strong diversity |
| F8 | Experiments? | Heavy A/B; layered configs | Experiment assignment sticky |
| F9 | Fallback? | Heuristic scores if model fails | Cached / rules fallback |
| F10 | Impression logging? | Features + scores for training | Join keys / scaffolds |
| F11 | Real-time features? | Last-N actions, counters | Online feature service |
| F12 | Ads? | Out of this stage (mixer later) | Organic-only MVP |

**MVP functional scope:**

1. `Rank(viewer, candidates[], context) → ranked[]` with multi-task scores.  
2. Hydrate features for viewer + each candidate (batched).  
3. Run model inference (GPU/CPU pool) within budget.  
4. Combine heads into final utility score with tunable weights.  
5. Truncate to top-M for mixer (`M ≤ |candidates|`).  
6. Emit training logs (sampled).  
7. Hard timeouts + deterministic fallback ordering.

**Out of MVP:**

- Candidate retrieval / friend-graph traversal  
- Final feed mixer (ads, stories trays, surveys)  
- Model training / daily trainer fleet  
- Full integrity classifier training  
- Client-side ranking

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ranker p99 latency | Scroll must not wait | ≤ 80–100ms stage budget |
| N2 | Availability | Feed critical | 99.9%+ with fallback |
| N3 | Feature freshness | Actions affect soon | Online feats seconds; embeddings minutes–hours |
| N4 | Throughput | Peak feed QPS × stage calls | Tens–hundreds of K rank QPS |
| N5 | Consistency | Experiment stickiness | Same viewer×request config |
| N6 | Privacy | Features ACL’d | No leakage across users in batching |
| N7 | Debuggability | Why ranked? | Score breakdown tools (sampled) |
| N8 | Model rollout | Safe canaries | Shadow → % traffic → default |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Feed service sends 500 candidates → features → model → top 100 ordered → mixer.  
2. Viewer liked similar posts recently → online feature boosts relevant authors.  
3. Experiment assigns model_v27 weights → sticky for session.  
4. Integrity feature low → utility down-ranked / filtered.  
5. Model cache hit on viewer tower embeddings → faster.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Feature store timeout | Partial features + default imputations; or drop to fallback |
| Model OOM / pod death | Retry other replica; else heuristic |
| Empty candidates | Return empty quickly |
| Duplicate post_ids | Dedupe preserve order |
| Missing post features (deleted) | Filter out |
| Over budget mid-score | Return partial scored + unscored heuristic tail |
| Feature skew train/serve | Monitoring; kill switch |
| Hot viewer (celeb stalking?) | Cache viewer features aggressively |
| Burst fanout after viral | Post feature cache; protect feature store |
| Bad experiment config | Guardrails; auto-disable on metric burn |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Rank requests/s | 50K | 500K | 5M | 50M |
| Candidates / request | 500 | 500 | 300–800 | cascade more stages |
| Features / candidate | 200 | 200–500 | 500+ | embeddings heavy |
| Model FLOPs / cand (order) | medium NN | larger | distilled + cascade | multi-stage mandatory |
| Feature store QPS (batched) | ~5M keys/s | ~50M | cells | hierarchical caches |
| GPU/CPU scorers | hundreds | thousands | regional fleets | per-cell |
| Training log sample rate | 10–20% | adaptive | adaptive | heavily sampled |
| p99 budget | 100ms | 80ms | 60–80ms | stricter + cascade |

**What each jump forces:**

- **10×:** Feature caching tiers; model replicas; batching; request coalescing.  
- **100×:** Regional ranker cells; viewer embedding affinity; cascade (cheap → expensive models).  
- **1,000×:** Split stage into retrieval-score / precision-score; distilled students; edge feature caches; strict per-tenant budgets.

### 1.5 Etc. (Constraints & Assumptions)

- Upstream **retrieval** already ran (friends posts, pages, groups, recommendations).  
- Downstream **mixer** owns ads, diversity hard constraints, pagination.  
- We may reference a two-tower retrieval model but do **not** design retrieval fully.  
- Focus interview depth on **features, inference, latency, failure**.

**Scope statement to repeat back:**

> Design one Facebook News Feed **ML ranking stage**: given viewer context and a few hundred candidate posts, hydrate features, run multi-task model scoring under ~100ms p99, combine into utility, truncate for the mixer, log for training, and degrade gracefully—scaling via caching, batching, regional cells, and model cascades at 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Rank RPC** | Incoming stage calls | 50K/s | Ranker frontend |
| **Feature key lookups** | viewer + posts + edges | 50K × (1+500) ≈ 25M/s naive | Feature cache / store |
| **Model inferences** | Batch per request | 50K batches/s | Inferencing fleet |
| **Log export** | Sampled feature bags | ~5–10K/s equiv | Kafka |
| **Embedding fetches** | User/post towers | subset | ANN/embedding cache |

**Anti-pattern:** counting only “50K QPS” while ignoring feature fanout.

### 2.2 Feature fanout math

```text
Naive: 50K req/s × 500 candidates × 3 entity gets = 75M gets/s
With batching + packing: 1 multi-get per entity type per request
With caching (viewer feats ~95% hit, post ~80%): effective store QPS collapses
MUST design caches first — store cannot take raw fanout
```

### 2.3 Latency budget allocation

```text
Total stage p99 ≤ 100ms
  - auth/experiment resolve: 5ms
  - feature hydrate parallel: 40ms
  - model infer: 40ms
  - combine + truncate + log enqueue: 10ms
  - slack / GC: 5ms
If feature >40ms → partial / fallback path
```

### 2.4 Payload sizes

```text
500 candidates × 8B id = 4KB inbound
Scores out: 500 × 4 heads × 4B = 8KB
Feature bag for logging (sampled): 50–200KB — async only
```

### 2.5 Model capacity

```text
If GPU batch scores 500 cands in 20ms average
Throughput per GPU ≈ 50 batches/s → 1K GPUs for 50K/s (order)
Use CPU for smaller models; GPU for large; distill to fit budget
```

### 2.6 Cache value

```text
Viewer features reused across pages/sessions: high hit rate
Post features reused across viewers: viral posts extremely hot
Edge features (viewer×author) denser / harder — cache carefully with TTL
```

### 2.7 End-to-end fanout with cache hits

```text
Assume: viewer cache 95%, post 80%, edge 60%
Per request store gets ≈
  1×(1-0.95) viewer + 500×(1-0.80) post + 500×(1-0.60) edge_author_approx
  ≈ 0.05 + 100 + 200 = ~300 backing gets/request (still high)
→ need: post feature packing (single multi-get), embedding block cache,
  and smaller candidate sets via retrieval quality
At 50K rank QPS × 300 = 15M gets/s → still requires L1/L2 caches in front
```

### 2.8 Calibration & logging bandwidth

```text
Sample 5–20% of requests for full feature bags
50K × 0.1 × 100KB ≈ 500 MB/s peak log egress — Kafka partitioned by date/model
Never sync-write bags on rank path
Calibration job daily: predicted P(engage) vs observed → temperature scaling / isotonic
Stale calibration → overconfident utility → bad ranking under distribution shift
```

### 2.9 Memory on model hosts

```text
Model weights: 100MB–2GB depending on architecture
Per-request activation workspace: tens of MB × concurrency
Embedding cache on host: 1–10GB hot entity vectors
Oversubscribe GPU → p99 latency cliffs; size for p99 batch time not avg
```

### 2.10 Progressive capacity table

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Rank QPS | 50K | 500K | cells | stricter budgets |
| Feature store QPS | cache-masked | ×10 | regional | hierarchical feats |
| GPU/CPU infer | 1K units | ×10 | cascade L1/L2 | distill |
| Log sample rate | 10% | 5% | 1–2% | smart sample |
| Candidate N | 500 | 500–1K | cascade | retrieval quality ↑ |

**Anti-patterns:** ignoring feature fanout; sync training logs; one global feature fetch per candidate SQL.

---

## 3. High-Level Design

### 3.1 API

```text
rpc RankFeedCandidates(RankRequest) returns (RankResponse);

RankRequest {
  viewer_id,
  request_id,
  candidates: [Candidate { post_id, retrieval_score, source }],
  context: { country, device, time_local, feed_session_id },
  experiment_overrides?,
  budget_ms?
}

RankResponse {
  ranked: [ScoredCandidate {
    post_id,
    utility,
    heads: { p_engage, p_hide, p_vulgar, ... },
    filtered?: bool,
    reason_codes?: []
  }],
  model_version,
  feature_version,
  degraded?: bool
}
```

### 3.2 Pipeline inside the stage

```text
1) Resolve experiment / model version
2) Dedupe & prefilter (deleted, blocked authors) via cheap flags
3) Parallel feature hydrate:
     - Viewer features / embeddings
     - Post features / embeddings (batch)
     - Author features
     - Edge features (viewer×author, viewer×post)
4) Impute missing; build model tensors
5) Inference (multi-task heads)
6) Utility = w · heads (+ retrieval_score blend)
7) Filter integrity thresholds
8) Sort + truncate top-M
9) Async training log (sample)
```

### 3.3 Feature sources — Why X over Y

| Source | Pros | Cons | Use |
|--------|------|------|-----|
| **Online feature store** (Redis/Giza-like) | Fresh counters | Hotspot risk | Last-N, counters |
| **Embedding store** | Semantic | Staleness | User/post towers |
| **Request-time context** | Free | Limited | Device, hour |
| **Join from DB per cand** | Simple | **Latency death** | Never on path |
| **Precomputed post snapshot** | Fast | Minutes stale OK for many feats | Post static/slow feats |

**Chosen:** Tiered features — snapshot + online deltas + embeddings; **no per-candidate SQL**.

### 3.4 Scoring — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Hand-tuned formula | Debuggable | Poor quality | Fallback only |
| GBDT | Strong tabular | Feature eng heavy | Medium scale |
| Neural multi-task | Quality SOTA | Latency/cost | **Main stage MVP** |
| Huge LLM rescoring | Quality? | Budget deal-breaker | Not this stage |

**Utility example:**

```text
utility = w1*P(engage) + w2*P(long_view) - w3*P(hide) - w4*P(report)
        + w5*retrieval_score_norm
```

Weights from experiments / Bayesian optimization offline.

### 3.5 Cascade context (boundary)

```text
Retrieval (not us) → light scorer (optional) → **MAIN RANKER (us)** → mixer
At 100×, we may split our stage into L1 (cheap) + L2 (precise) — still “ranking”
```

**Interview move:** Explicitly name what you own vs adjacent stages.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Feature access | Batch multi-get + caches | Fanout | Per-id SQL |
| Inferencing | Dedicated model hosts | Scale independently | Rank logic in feed monolith |
| Failure | Heuristic fallback | Availability | Empty feed on model blip |
| Diversity | Mixer-first | Separation | Overcomplicate ranker |
| Logging | Async sampled | Latency | Sync write feature bags |
| Versioning | Pin model+feature schema | Train/serve parity | Silent skew |

### 3.7 Latency deal-breakers & contracts

| Anti-pattern | Why fatal | Contract fix |
|--------------|-----------|--------------|
| Per-candidate SQL joins | p99 death | Snapshot features only |
| Unbounded candidate N | Infer timeout | Retrieval truncates; ranker caps |
| Sync feature bag write | Tail latency | Async Kafka sample |
| Cross-region feature fetch | Multi-100ms | Home-cell routing |
| Skipping integrity filters in fallback | Safety | Hard filters always |

**Ownership contract (say explicitly):**

```text
Retrieval owns: candidate coverage & retrieval_score
Ranker owns: utility heads under budget_ms
Mixer owns: diversity, ads slots, final page composition
```

### 3.8 Calibration stance (MVP)

```text
Raw model heads ≠ display utility
Apply: temperature / Platt / isotonic mapping per head (offline fit)
Utility weights w tuned by online experiments under calibrated heads
Without calibration: weight tuning fights miscalibrated probabilities
```

---

## 4. Architecture Diagram

```text
                    +------------------+
   Feed Service --> | Ranker Frontend  |  auth, experiments, budgets
                    +--------+---------+
                             |
           +-----------------+-----------------+
           |                 |                 |
           v                 v                 v
   +-------+------+  +------+-------+  +------+------+
   | Feature      |  | Embedding    |  | Integrity     |
   | Hydrator     |  | Cache        |  | Flags Cache  |
   +-------+------+  +------+-------+  +------+------+
           |                 |                 |
           +-----------------+-----------------+
                             |
                             v
                    +--------+---------+
                    | Model Inference  |  CPU/GPU replicas
                    | multi-task heads |  versioned graphs
                    +--------+---------+
                             |
                             v
                    +--------+---------+
                    | Utility + Filter |  weights, thresholds
                    | Sort / Truncate  |
                    +--------+---------+
                             |
                             +------> Kafka (sampled training logs)
                             |
                             v
                         RankResponse → Mixer
```

**Sequence (happy path):**

```text
RankRequest
  -> assign model_version from experiments
  -> parallel:
       get_viewer_features(viewer)
       multi_get_post_features(ids)
       multi_get_edge_features(viewer, authors)
  -> assemble batch tensor
  -> infer() -> heads
  -> utility / filter / sort / topM
  -> return; async log
```

**Degraded path:**

```text
if hydrate_timeout or infer_timeout:
  score = f(retrieval_score, freshness, author_affinity_cached)
  degraded=true
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Never exceed caller budget** without returning something (partial/fallback).  
2. **Model version + feature schema version** recorded on every response/log.  
3. **No cross-viewer batch pollution** — padding/masking safe; keys isolated.  
4. **Filters for hard integrity** cannot be skipped in fallback without policy.  
5. **Idempotent logging** keyed by `request_id` (at-least-once OK).

#### 5.1.2 Timeout hierarchy

```text
outbound_deadline = min(client_budget, DEFAULT_100ms)
feature_deadline = 0.4 * outbound
infer_deadline = 0.4 * outbound
always leave slack for combine
```

Cancel in-flight feature calls when deadline hit; impute.

#### 5.1.3 Fallback ladder

1. Full model  
2. Distilled / previous model  
3. Linear blend of retrieval_score + freshness + affinity  
4. Retrieval order as last resort (still apply hard filters)

#### 5.1.4 Train/serve skew

| Risk | Mitigation |
|------|------------|
| Feature missing online | Shared feature definitions; defaulting policy identical |
| Different aggregation windows | Same job specs; monitoring PSI/KL |
| Model expects feat v4, got v3 | Version gate; refuse + fallback |

**Deal-breaker:** shipping a model without a feature-availability matrix.

### 5.2 Scalability

#### 5.2.1 Caching tiers

| Cache | Key | TTL | Notes |
|-------|-----|-----|-------|
| L1 in-process | hot posts | seconds | per pod |
| L2 memcache | viewer / post | seconds–minutes | regional |
| L3 feature store | truth | — | backing |
| Embedding | entity_id | minutes–hours | update async |

**Cache correctness:** viewer features may be user-specific — never serve viewer A’s bag to B. Post features shared OK. Experiment-aware keys when feature treatment differs.

#### 5.2.2 Batching & packing

- One rank request = one inference batch (candidates as batch dim).  
- Coalesce feature multi-gets.  
- Avoid tiny GPU batches: optional micro-batch across requests **only if** latency SLO allows (usually dangerous for p99 — prefer per-request batching of candidates).

#### 5.2.3 Regional cells

```text
Viewer home cell owns ranker routing
Feature stores regionally replicated
Models deployed per region
Cross-region feature fetch is a bug at 100×
```

#### 5.2.4 Model cascade (100×+)

```text
L1 cheap model scores 1000 → keep 300
L2 heavy model scores 300 → keep 100
Total FLOPs down; quality preserved for head
```

Own this as evolution of “the ranking stage” if interviewer zooms out.

#### 5.2.5 Candidate generation boundary (deep)

```text
Ranker does NOT crawl the graph.
Inputs already truncated by retrieval sources:
  following / groups / pages
  similarity ANN
  campaigns / boosts (labeled)
  re-engagement pools
Ranker may lightly reweight by source trust but shouldn't re-retrieve
```

**Interview clarity:** if asked “how do you find posts?”, answer retrieval first, then “this stage scores a given candidate set under 100ms.”

#### 5.2.6 Feature store deep dive

| Feature class | Freshness | Store | Example |
|---------------|-----------|-------|---------|
| Static post | hours | snapshot KV | topic, media_type |
| Slow aggregate | minutes–hours | batch tables | 7d author quality |
| Online counters | seconds | Redis/Giza | last-1h clicks |
| Embeddings | minutes–days | emb cache | user/post towers |
| Edge | seconds–minutes | online KV | viewer×author affinity |
| Context | request | free | device, local hour |

**Hydration algorithm:**

```text
parallel:
  viewer = get(viewer_id)
  posts = mget(post_ids)          // packed
  authors = mget(author_ids)
  edges = mget(viewer, author_ids)
deadline hit → impute defaults per feature spec; mark degraded_features[]
```

**Deal-breaker:** N+1 feature RPCs in a loop over candidates.

#### 5.2.7 Progressive scale playbook

| Scale | Must add |
|-------|----------|
| Baseline | Ranker svc + feature store + model host |
| 10× | Multi-tier cache; autoscale infer; sampling logs |
| 100× | Regional cells; cascade; embedding affinity |
| 1,000× | Distillation; hierarchical features; stricter budgets |

### 5.3 Maintainability

#### 5.3.1 Experimentation

- Layered configs: model graph, weight vector, filter thresholds  
- Sticky by `viewer_id` + `experiment_salt`  
- Guardrail metrics: hide-rate, integrity, latency, empty-feed rate  
- Cache keys include experiment bits that change features/scores  

#### 5.3.2 Debugging “why this post?”

- Sampled score breakdown UI for employees  
- Store head scores + top features contributing (approximate attributions)  
- Never log raw sensitive features broadly  

#### 5.3.3 Observability

| Signal | Alert |
|--------|-------|
| p99 latency / deadline miss % | Page |
| Fallback rate | Page if > threshold |
| Feature null rates | Model quality |
| GPU duty / queue | Capacity |
| PSI feature drift | Model health |
| Calibration ECE | Quality |
| Head score distribution shift | Model health |

#### 5.3.4 Ownership boundaries

```text
Retrieval must provide: post_id, source, retrieval_score
Ranker provides: utility, heads, model_version
Mixer may re-order only under declared constraints (ads, diversity)
```

### 5.4 Model serving deep dive

```text
Deploy: blue/green model_version pins
Warmup: load weights + prime CUDA graphs / thread pools
Health: synthetic batch latency probe
Rollback: pointer flip < minutes
Input: fixed feature schema_version; unknown fields rejected
Output: multi-task heads tensor → utility combiner (CPU, tiny)
```

| Serving choice | When |
|----------------|------|
| CPU | Small GBDT / tiny MLP; predictable p99 |
| GPU | Large nets; batch 100–1000 cands |
| Distilled student | 1000× cost pressure |

### 5.5 Calibration & utility

```text
Train heads with proper scoring rules (logloss etc.)
Offline: fit calibrators on holdout chronologically
Online: utility = w · calibrated_heads (+ retrieval blend)
Monitor ECE / reliability diagrams per head weekly
Distribution shift → recalibrate before re-tuning weights blindly
```

**Integrity heads:** high P(hate)/P(violence) → hard filter regardless of engage head.

### 5.6 Latency budget enforcement

```text
budget_ms from caller (default 100)
t0 = now
feature_deadline = t0 + 0.4*budget
infer_deadline = t0 + 0.8*budget
on miss: fallback ladder; response.degraded=true
Never exceed budget by more than small slack (GC) — better partial than late
```

### 5.7 Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Ranker = whole feed | Split retrieve/rank/mix |
| Per-cand SQL | Snapshots + mget |
| Sync logging | Async sample |
| No fallback | Heuristic ladder |
| Silent skew | Version gates |
| Diversity inside ranker only | Mixer ownership |
| Cross-region features | Home cell |

---

## 6. Wrap-Up

### 6.1 Design summary

The Facebook feed **ranker stage** is a latency-hardened microservice: **hydrate features in parallel**, **score with a versioned multi-task model**, **combine to utility**, **filter/truncate**, and **log asynchronously**. Scale is won on **feature cache hit rates**, **batch inference**, and **cascades**, not on bigger monoliths.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Fresh features vs p99 | Tiered TTLs + deadlines | Slightly stale feats |
| Quality vs cost | Cascade + distill | More moving parts |
| Logging fidelity vs load | Sample | Sparse labels on some slices |
| Fallback simplicity vs quality | Heuristic | Temporary relevance drop |

### 6.3 Deal-breakers

1. Per-candidate synchronous DB joins on the rank path.  
2. Scoring tens of thousands of candidates with a huge model in one stage without cascade.  
3. Blocking the user on training-log writes.  
4. No fallback when the model fleet dies.  
5. Ignoring train/serve feature version skew.

### 6.4 45-minute plan

1. Clarify **one stage** boundaries vs retrieval/mixer.  
2. Fanout math → caches.  
3. Draw hydrate → infer → utility.  
4. Budgets, fallback, experiments.  
5. 10×/100×/1,000× cascade story.  
6. Deal-breakers.

### 6.5 Phase 2

- On-device feature signals blended server-side  
- Sequence models over user history compressors  
- Stronger attribution tooling  
- Integrity models co-scored  

---

## 7. Deeper / Related Interview Questions

### Q1. Why separate retrieval and ranking?

**A:** Retrieval searches a huge corpus cheaply (ANN, inverted indexes, friend firehose). Ranking applies expensive features/models to a small set. Separating lets each optimize different cost curves.

### Q2. What does multi-task learning buy you?

**A:** Shared representation predicts multiple outcomes (like, comment, hide, video view). Utility weights can change product goals without full retrain every time (within reason).

### Q3. How do you pick candidates count (500 vs 5000)?

**A:** Empirically: quality asymptotes while latency/cost grow ~linear with candidates for heavy models. Use cascade if you need larger funnels.

### Q4. Viewer features vs post features vs edge features?

**A:** Viewer: interests, last-N. Post: topic, media type, age. Edge: viewer–author strength, past eng with author. Edge often highly predictive and cache-tricky.

### Q5. How do you keep p99 under 100ms?

**A:** Parallel fetches, tight deadlines, caches, precomputed snapshots, efficient model, truncate work, avoid sync I/O, hedge replicas.

### Q6. What is train/serve skew?

**A:** Offline training used a feature definition/value that differs online (missing, different window, bug). Causes silent quality loss. Prevent with shared feature code and drift monitors.

### Q7. Should diversity live in the ranker?

**A:** Light penalties optional; hard constraints (no 5 consecutive same author) usually **mixer** responsibilities so ranker stays a scorer.

### Q8. How do experiments interact with caching?

**A:** Cache keys must include model/feature version or experiment id where values differ; don’t serve model_v1 scores from v2 cache entries.

### Q9. GPU or CPU for inference?

**A:** Large nets → GPU; small GBDT/distilled → CPU often better p99/cost. Mixed fleets common. Measure $/QPS and latency.

### Q10. How do you handle deleted posts mid-rank?

**A:** Feature miss / tombstone flag → drop candidate. Mixer should also be resilient.

### Q11. Explain utility vs raw P(click).

**A:** Optimizing only clicks encourages clickbait. Multi-head utility subtracts hide/report and values meaningful interactions / long views.

### Q12. Feature imputation strategies?

**A:** Training-time defaults; mean/median; learned missingness indicator bits. Must match serving.

### Q13. How to log features for training without killing latency?

**A:** Snapshot feature vector asynchronously after response path copies memory; sample; backpressure to drop logs before delaying RPC.

### Q14. What is a precision ranking stage?

**A:** Later cascade stage with fewer candidates and heavier model — higher cost per candidate, better ordering at the top.

### Q15. How do real-time counters update features?

**A:** Engagement pipeline increments online store keys; ranker reads with seconds TTL. Eventual consistency OK; use request-time local boosts for viewer’s own just-now actions if needed.

### Q16. Cold start posts?

**A:** Sparse engagement features; rely on content embeddings, author prior, retrieval_score; explore traffic via mixer policies.

### Q17. Cold start viewers?

**A:** Demographic/context priors; onboarding interests; stronger content models; less edge affinity.

### Q18. How do you prevent integrity bypass in fallback?

**A:** Fallback still applies hard filters from integrity flag cache; only soft quality scores are heuristic.

### Q19. Batch across users on one GPU?

**A:** Increases utilization but hurts p99 waiting for a batch. For user-facing feed, prefer intra-request candidate batching; continuous batching only with latency caps.

### Q20. How is author demotion done?

**A:** Features + heads predict negative feedback; utility weights; separate integrity/policy lists for severe cases.

### Q21. What metrics define ranker success?

**A:** Online: engage rate, hide rate, session time, integrity, latency, fallback rate. Offline: AUC/PR per head, calibration, NDCG@k on logs.

### Q22. Calibration importance?

**A:** If P(engage) miscalibrated, weight blends misbehave across slices (country/device). Monitor calibration curves.

### Q23. How to roll out a new model?

**A:** Shadow score → compare; 1% canary; ramp; auto-rollback on guardrails (latency, hide, integrity).

### Q24. Feature store vs passing features from retrieval?

**A:** Retrieval may pass cheap scores; rich features still hydrated in ranker for consistency. Avoid trusting client-provided features.

### Q25. Why request_id?

**A:** Join logs, debug, dedupe, trace across feed→ranker→mixer.

### Q26. How do you size memcache for post features?

**A:** Working set = hot posts over TTL window. Viral posts dominate; use LRU + separate tiny L1. Estimate avg feature blob × hot set × replicas.

### Q27. Can ranker be stateful per session?

**A:** Prefer stateless pods with session signals in request (seen ids, session embeddings). Sticky sessions optional for cache warmth, not correctness.

### Q28. Interaction with pagination?

**A:** Each page may re-rank remaining candidates or fetch new retrieval; pass `seen` to avoid duplicates; don’t assume global total order persisted server-side always.

### Q29. Biggest failure you’ve seen in such systems?

**A:** Feature fanout storms after cache flush; model weight misconfig flipping signs; train/serve bug on a single large-weight feature.

### Q30. 60-second pitch?

**A:** “Retrieval gives ~500 posts. Ranker batch-fetches cached features, runs a multi-task model under 100ms, blends heads into utility, filters, returns top-M. On timeout we heuristic-rank. We scale with feature caches, regional fleets, and model cascades—not with monolith SQL scoring.”

### Q31. How do you allocate the 100ms budget?

**A:** ~5ms experiment resolve, ~40ms feature hydrate, ~40ms infer, ~10ms combine/log enqueue, ~5ms slack. Enforce nested deadlines; fallback on miss.

### Q32. What is calibration vs weight tuning?

**A:** Calibration makes P(head) match frequencies; weights trade off heads into utility. Tune weights on calibrated heads or you fight bias.

### Q33. Feature store vs embedding store?

**A:** Feature store: tabular counters/flags. Embedding store: dense vectors for towers/ANN. Different TTL, update paths, and cache shapes.

### Q34. How do you prevent train/serve skew?

**A:** Shared feature definitions, same aggregation windows, version gates, PSI monitors, logged features == served features (sampled).

### Q35. Should ranker do diversity?

**A:** Light penalties optional; hard diversity/author spacing usually mixer-owned so ads/integrity policies compose cleanly.

### Q36. GPU micro-batch across users?

**A:** Tempting for utilization; dangerous for p99 if you wait to fill batches. Prefer per-request candidate batching; only micro-batch if SLO proven.

### Q37. How do deleted posts get filtered?

**A:** Cheap integrity/deleted flags in prefilter before infer; mixer also drops. Don’t spend GPU on tombstones.

### Q38. What is a precision (L2) stage?

**A:** Heavier model on a shortlist after L1 cheap scores. Cuts FLOPs while keeping quality on the head of the list.

### Q39. How do experiments interact with caches?

**A:** Cache keys must include treatment ids that change scores/features; otherwise users see wrong arm. Sticky assignment by viewer_id.

### Q40. Logging full bags on every request?

**A:** Deal-breaker for latency/cost. Sample 1–20%; always log ids + model_version for joinability.

### Q41. Cold start viewer features missing?

**A:** Impute defaults per spec; rely more on post/context features; exploration retrieval sources.

### Q42. How do you narrate ownership in interview?

**A:** “I own the ranking stage: hydrate → score → utility → truncate under budget. Retrieval and mixer are contracts.”

### Q43. What breaks at 1,000×?

**A:** Cross-region features, huge candidate N, uncached fanout, giant models without cascade/distill, sync logging.

### Q44. Integrity head vs engage head conflict?

**A:** Hard filters from integrity always win; don’t let high P(engage) override hate/violence thresholds.

### Q45. 10×/100×/1,000× one-liner?

**A:** 10× caches+autoscaling; 100× regional cells+cascade; 1,000× distillation+stricter budgets+hierarchical features.

---

### Appendix A — NFR card

```text
Ranker p99 ≤ 100ms
Fallback ≠ empty feed
Feature versions pinned
Async sampled logs
No per-cand SQL
Hard integrity in all modes
```

### Appendix B — Score heads (example)

| Head | Meaning |
|------|---------|
| p_like | Predict like |
| p_comment | Predict comment |
| p_share | Predict share |
| p_hide | Predict hide |
| p_video_complete | Watch completion |
| p_report | Severe negative |

### Appendix C — Budget spreadsheet

| Step | Budget |
|------|--------|
| Experiment | 5ms |
| Features | 40ms |
| Infer | 40ms |
| Combine | 10ms |
| Slack | 5ms |

### Appendix D — Fallback formula

```text
utility ≈ 0.6*norm(retrieval) + 0.3*freshness + 0.1*author_affinity
```

### Appendix E — Progressive scale

| Scale | Architecture |
|-------|--------------|
| Baseline | 1 region ranker |
| 10× | Cache tiers + autoscaling |
| 100× | Cells + L1/L2 cascade |
| 1,000× | Distilled students + edge feats |

### Appendix F — Contract with mixer

```text
Ranker ordering is soft preference
Mixer may insert ads / enforce diversity / apply last-second suppresses
```

### Appendix G — Logging schema (sampled)

```text
{request_id, viewer_id, post_id, features_ref, heads, utility, model_version, ts, label_join_key}
```

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| Head | Single prediction output |
| Utility | Scalar ranking score |
| Cascade | Cheap→expensive stages |
| Skew | Train/serve mismatch |
| Hydration | Fetching features for IDs |

### Appendix I — 30m checklist

1. Bound one stage.  
2. Fanout math.  
3. Hydrate→infer→utility.  
4. Timeouts/fallback.  
5. Scale + deal-breakers.

### Appendix J — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Rank in MySQL” | Fanout/latency |
| “Score all posts” | Need retrieval |
| “Use an LLM” | Budget |
| “Sync log everything” | p99 death |

### Appendix K — Feature tiering

| Tier | Examples | Freshness |
|------|----------|-----------|
| Static | media_type | days |
| Slow | topic emb | hours |
| Online | last_N likes | seconds |
| Request | device, hour | immediate |

### Appendix L — Integrity interaction

```text
if integrity_score < HARD: drop
elif integrity_score < SOFT: utility *= penalty
```

### Appendix M — Related Meta concepts

| Concept | Relation |
|---------|----------|
| TAO | Entity reads (not heavy path) |
| Feature store | Online feats |
| FBLearner-like | Training adjacent |
| Mixer | Downstream |

### Appendix N — Worked example

```text
50K rank/s × 500 cands
Post feature L2 hit 80% → 50K×500×0.2 = 5M post gets/s still large
→ raise hit rate via larger cache / longer TTL for slow feats
→ pack gets; use P90 size blobs
```

### Appendix O — Canary guardrails

| Metric | Abort if |
|--------|----------|
| p99 latency | +20% |
| hide rate | +X% relative |
| fallback rate | >2% |
| integrity | regress |

### Appendix P — Pseudocode

```text
def rank(req):
  cfg = experiments.resolve(req.viewer_id)
  cands = dedupe(req.candidates)
  feats = hydrate_parallel(cands, deadline=0.4*budget)
  if feats.degraded and critical_missing:
    return fallback(cands), degraded=True
  heads = model_infer(feats, cfg.model, deadline=0.4*budget)
  scored = [utility(h, cfg.weights) for h in heads]
  scored = integrity_filter(scored)
  ranked = sort(scored)[:cfg.M]
  log_async(sample(req, feats, ranked))
  return ranked
```

### Appendix Q — Seen-item handling

```text
mixer passes seen_ids → ranker downranks or filters
bloom in session context to save payload
```

### Appendix R — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Caches, autoscale |
| 100× | Cells, cascade |
| 1,000× | Distill, edge feature caches |

### Appendix S — Stage boundary diagram (say this)

```text
[Retrieval sources] --candidates--> [THIS RANKER STAGE] --top-M--> [Mixer]
                                         |
                                         +--> training logs (async)
Adjacent but NOT owned:
  - friend graph walk / ANN retrieval
  - ads auction
  - final diversity hard constraints (mixer)
```

### Appendix T — Interview whiteboard script

1. “I will design **one ranking stage**, not all of Feed.”  
2. Inputs/outputs + latency budget 100ms.  
3. Feature fanout math → caches mandatory.  
4. Parallel hydrate → infer → utility → truncate.  
5. Multi-task heads + weight blend.  
6. Timeout hierarchy + fallback ladder.  
7. Train/serve skew controls.  
8. Experiments + guardrails.  
9. Cascade at 100×.  
10. Deal-breakers.

### Appendix U — Feature fetch parallelism

```text
async parallel:
  viewer_f = get_viewer(viewer_id)
  posts_f = multi_get_posts(post_ids)
  authors_f = multi_get_authors(author_ids)
  edges_f = multi_get_edges(viewer_id, author_ids)
await_all(deadline)
impute_missing(...)
```

### Appendix V — Utility weight examples

| Goal shift | Weight change |
|------------|---------------|
| Less clickbait | ↑ hide/report penalties |
| More video | ↑ p_video_complete |
| Integrity push | ↑ soft integrity penalty |
| Meaningful social | ↑ comment/share vs like |

### Appendix W — Capacity worksheet

```text
rank_qps = ______
cands = ______
feature_keys_per_req ≈ 1 + cands × entities_per_cand
store_qps ≈ rank_qps × feature_keys × (1 - hit_rate)
gpus ≈ rank_qps / batches_per_gpu_per_sec
```

### Appendix X — FAQ rapid-fire

| Q | A |
|---|---|
| Rank in SQL? | No |
| Score all posts? | Retrieval first |
| Diversity here? | Light; mixer hard |
| Sync logs? | Async sample |
| No fallback? | Deal-breaker |

### Appendix Y — Shadow mode

```text
production model A serves users
model B scores in shadow (no user impact)
compare utility distributions + latency
promote B only if guardrails pass
```

---

*End of Facebook Feed Ranker (single ML stage) system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Change | Risk if skipped |
|------|--------|-----------------|
| →10× | L1/L2 feature caches; autoscale infer; sampled logs | Store melt; p99 blowups |
| →100× | Regional cells; L1/L2 model cascade; embedding affinity | Cross-region latency; GPU cost |
| →1,000× | Distillation; hierarchical features; stricter budgets | Cannot buy more GPUs linearly |

### 8.2 Latency budget card

```text
100ms stage budget (example)
  experiment/model pin: 5
  feature hydrate: 40  (parallel mget)
  inference: 40
  utility/filter/sort: 10
  slack: 5
Miss hydrate or infer → fallback ladder; degraded=true
```

### 8.3 Feature hydration checklist

```text
□ batch mget posts
□ batch mget authors
□ batch mget edges
□ viewer single get
□ impute policy identical to training
□ version gate schema
□ never per-candidate SQL
```

### 8.4 Calibration note

```text
Uncalibrated P(engage)=0.8 that is really 0.3 → weight tuning lies
Fit calibrator on chronological holdout; monitor ECE
Integrity heads: hard thresholds after calibration
```

### 8.5 Anti-patterns

1. Ranker owns whole feed graph walk  
2. N+1 feature RPCs  
3. Sync feature-bag writes  
4. Empty feed on model blip  
5. Silent train/serve skew  
6. Diversity-only-inside-ranker with ads conflicts  
7. Cross-region feature fetch at 100×  

