# System Design: Trending-Hashtag Service

> **Focus areas:** Rolling top-K · Sliding/tumbling windows · Approximate counters · Regional → global merge · Spam/gaming · Decay · Geo shards  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split ingest vs query planes, explicit approx vs exact, deal-breakers for “exact global top-K at 1M events/s” fantasies  
> **Interview theme:** Classic Google L5+ streaming + aggregation — freshness SLOs, heavy hitters under adversarial traffic, regional correctness then global merge

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

Goal: **bound the product**—a real-time **trending hashtag** service that computes **rolling top-K** over several time windows, both **globally** and **regionally**, with defenses against spam/gaming and clear approx/exact tradeoffs.

### 1.0 What this is / is not

| Dimension | **Trending-hashtag service (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Rank hashtags by recent activity → top-K | Full social graph / feed ranking |
| Success | Fresh, stable, hard-to-game trends | Perfect historical analytics warehouse |
| Data plane | Event ingest + continuous aggregation | Batch-only nightly MapReduce (hooks OK) |
| Query | Read top-K for window × scope | Arbitrary ad-hoc SQL over all tags |
| Correctness | Approx heavy-hitters OK if bounded error | Exact distinct-user counts for every tag MVP |

**Scope statement:** Design a trending-hashtag service: multi-window top-K, global + regional scopes, streaming pipeline, spam resistance, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a “trend” signal? | Mentions/posts containing `#tag`; optionally weighted by likes/reposts | Event stream with `tag`, `user`, `ts`, `region`, `weight` |
| F2 | Time windows? | Several: 5m, 1h, 24h, 7d (lock 3–4) | Parallel window state; different freshness SLOs |
| F3 | Top-K size? | K=50–100 display; maintain larger candidate set (e.g. 1K) | Heap / sorted structure per window×scope |
| F4 | Global and regional? | Yes — region = country or metro; global merge | Two-stage aggregate: region then global |
| F5 | Exact counts? | Approx OK if error bounded; exact for tiny candidate set | CMS / HeavyKeeper + exact for hot set |
| F6 | Dedup? | Same user spam-pumping same tag should not dominate | Per-user rate limits; unique-user approx (HLL) optional |
| F7 | Query API? | `GET /trends?window=&region=` (+ optional category) | Cacheable read path; CDN/edge for public |
| F8 | Freshness? | Minutes for 5m/1h; hours OK for 7d | Streaming for short; micro-batch OK for long |
| F9 | History? | Snapshots for charts Phase 1.5 | Periodic snapshot store |
| F10 | Blacklist / NSFW? | Yes — policy tags suppressed | Policy filter before publish |
| F11 | Personalized trends? | Out of MVP | Hooks only (`user_affinity` later) |
| F12 | Admin ops? | Pin/suppress tag; force recompute | Control plane separate from ingest |

**MVP functional scope:**

1. Ingest hashtag events (from posts/comments) into a durable log.  
2. Maintain rolling top-K for windows: **5m, 1h, 24h** (7d Phase 1.5 or cheap tumbling).  
3. Scopes: **global** + **per-region** (country-level MVP).  
4. Query API returns ranked list with score/count and optional delta (“rising”).  
5. Spam/gaming: rate limits, bot signals, velocity caps, blacklist.  
6. Approximate heavy-hitters with bounded error; exact counters for top candidates.  
7. Publish results to a low-latency read store; edge/CDN cache for public GETs.

**Out of MVP:**

- Personalized / follow-graph-aware trends  
- Exact distinct users for every hashtag worldwide  
- Real-time sub-second global consistency  
- Full ML trend prediction (mention as Phase 2)  
- Cross-language tag clustering (`#olympics` ≡ `#奥运会`) beyond simple normalize

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest durability | No silent event loss after ACK | Kafka/Pulsar multi-AZ; at-least-once |
| N2 | Query latency | Feels instant | p99 < 50–100ms (cached); origin < 20ms |
| N3 | Freshness (5m window) | Near-real-time | End-to-end lag p99 < 30–60s |
| N4 | Freshness (24h) | Tolerant | Lag < 2–5 min OK |
| N5 | Availability (read) | Public homepage critical | 99.9%+ via cache; stale-if-error |
| N6 | Approx error | Bounded, documented | ε-relative or count error for non-heavies |
| N7 | Spam resilience | Trends not trivially bought | Multi-signal score; anomaly quarantine |
| N8 | Multi-region | Global users | Regional process + global merge |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User posts with `#WorldCup` → event → region aggregate → global merge → appears in rising 5m.  
2. Client `GET /trends?window=1h&region=US` → edge cache hit → JSON top-K.  
3. Tag cools off → decay / window slide → drops out of top-K.  
4. Admin suppresses spam tag → removed from published board within one publish cycle.  
5. Flash event in KR → KR regional board spikes; global board reflects after merge.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Bot farm repeats `#BuyNow` | Rate limit + unique-user damping + quarantine |
| Hot tag cardinality storm | Exact map only for candidates; CMS for long tail |
| Clock skew on events | Event-time + watermark; late events into side buffer |
| Region offline | Global uses last good regional snapshot + mark degraded |
| Kafka lag spike | Query serves last publish; SLO burn alert; scale consumers |
| Tag normalization (`#AI` vs `#ai`) | Casefold + unicode NFKC; emoji policy explicit |
| Tie scores | Deterministic tie-break (`tag` lex + prior rank hysteresis) |
| Oscillation / flicker | Hysteresis / sticky rank; EMA smoothing |
| Blacklisted substring | Policy filter at publish; still count internally optional |
| Replay after bugfix | Idempotent keyed state; versioned job; rebuild from log |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak hashtag events/s | 50K | 500K | 5M | 50M |
| Avg tags / event | 1.5 | 1.5 | 1.5–2 | 2 |
| Distinct tags / day | 20M | 200M | 2B | 20B |
| Regions (scopes) | 50 | 50–100 | 200 | 200+ metros |
| Windows | 3 | 3–4 | 4–5 | 5+ |
| Query QPS (global board) | 10K | 100K | 1M | 10M |
| Query QPS (all regional) | 50K | 500K | 5M | 50M |
| Top-K (display) | 100 | 100 | 100 | 100 |
| Candidate set maintained | 1K–5K | 5K–20K | 20K+ | hierarchical |
| Publish interval | 5–10s | 5s | 2–5s | 1–2s + delta |
| Flink/consumer cores (order) | 100 | 1K | 10K | cell fleets |

**What each jump forces:**

- **10×:** Partition by region+hash(tag); CMS/HeavyKeeper mandatory for long tail; read cache mandatory.  
- **100×:** Regional aggregator cells; global merger only sees regional top-C; separate hot-tag exact path.  
- **1,000×:** Geo cells + hierarchical merge (metro→country→global); approx everywhere except pinned hot set; query fully edge-served.

### 1.5 Etc. (Constraints & Assumptions)

- Events arrive from an upstream social/post service (we are not designing the entire social network).  
- **Event-time** semantics preferred; processing-time OK for MVP if interviewer agrees.  
- Regions derived from user profile or IP→geo at emit time (frozen on event).  
- Trending ≠ “most popular all-time”; **recency + velocity** matter.  
- Public boards are cacheable; personalized boards out of scope.

**Scope statement to repeat back:**

> Design a trending-hashtag service that maintains rolling top-K over multiple time windows, regionally and globally, via a streaming aggregation pipeline with approximate heavy-hitters, exact candidate refinement, spam/gaming controls, and a cacheable query path—scaling through 10× / 100× / 1,000× with regional aggregation then hierarchical global merge.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Ingest events** | Post→tag expand | ~50K/s | ~500K/s | Kafka |
| **Tag observations** | events × tags/event | ~75K/s | ~750K/s | Stream job |
| **State updates** | Counter / sketch upserts | ~75K/s | ~750K/s | Flink state / Redis |
| **Publish writes** | Board snapshots | ~regions×windows / interval | ×10 | Redis/Spanner |
| **Query reads** | Top-K GET | ~50–60K/s | ~0.5–1M/s | Edge + Redis |
| **Admin / policy** | Suppress/pin | low | low | Control plane |

**Anti-pattern:** one “QPS” mixing Kafka produce, Flink rocksdb, and CDN GETs.

### 2.2 Cardinality & memory

```text
Naive exact: 20M distinct tags/day × 8B count = 160 MB just counts (too optimistic)
+ per window × per region → 20M × 3 windows × 50 regions = 3B keys → tens of TB if exact everywhere

Conclusion: exact global maps for all tags × all regions × all windows = DEAL-BREAKER at scale
Must use: sketches / heavy-hitters + exact only for candidates / hot tags
```

### 2.3 Window math

```text
5m sliding window, slide 10s:
  buckets = 5m / 10s = 30 buckets per key scope
  Maintaining per-tag 30 buckets exact → memory explodes
  Prefer: tumbling micro-batches OR Count-Min per bucket + heap of heavies

24h window:
  Can use hourly tumbling rolls + sum of 24 hours
  Or exponential decay approximating recency
```

### 2.4 Query amplification

```text
Homepage polls every 30s × 10M DAU online = huge if uncached
With CDN/edge TTL 5–10s on global board: origin QPS ≈ regions×windows×(1/TTL)
Example: 50 regions × 3 windows × 0.2 Hz = 30 writes/s publish; reads absorbed at edge
```

### 2.5 Merge cost (regional → global)

```text
Each region publishes top-C candidates (C=1000) per window every T seconds
Global merge input = regions × C = 50 × 1000 = 50K rows / T
Trivial CPU; network tiny vs raw events
This is the key scalability idea: never ship all tag counts globally
```

### 2.6 Spam amplification

```text
Without limits: 1 botnet × 10K accounts × 1 tag/s = 10K/s fake trend
Need: per-user emit caps, account trust score, unique-user approx, velocity z-score
Score = f(mentions, unique_users, trust, velocity) — not raw count
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /v1/trends?window={5m\|1h\|24h}&region={GLOBAL\|CC}` | Top-K list: `{tag, score, rank, delta_rank?}` |
| `GET /v1/trends/{tag}?window=` | Tag detail / sparkline (Phase 1.5) |
| `POST /internal/events` (or bus only) | Prefer bus ingest; HTTP only for backfill |
| `POST /admin/suppress` | Policy suppress tag |
| `POST /admin/pin` | Pin tag to rank slot (editorial) |
| `GET /v1/health/freshness` | Lag / last publish watermark |

**Event schema (ingest):**

```text
HashtagEvent {
  event_id,           // idempotency
  post_id,
  user_id,
  tags: [string],     // normalized
  region: "US",
  ts_event,           // event time
  weight: 1.0,        // optional engagement weight
  trust: 0.0..1.0,    // account trust at emit
  source: "post"|"repost"|"comment"
}
```

### 3.2 Data model (read side)

| Entity | Key | Value |
|--------|-----|-------|
| Board snapshot | `(window, region, version)` | sorted top-K JSON |
| Tag score (hot) | `(window, region, tag)` | exact count / score |
| Watermark | `(job, region)` | last event-time processed |
| Policy | `tag` | suppress / NSFW / pin |
| Snapshot history | `(window, region, ts)` | for charts |

### 3.3 Scoring model (MVP)

```text
raw = Σ weight_i over window  (approx or exact)
unique_factor = approx_unique_users (HLL) or capped per-user contribution
trust_factor = avg/trust-weighted
velocity = score_now - score_prev_bucket
score = raw^α × unique_factor^β × trust_factor^γ × (1 + δ·velocity_norm)

MVP simpler:
  score = min(per_user_cap_sum, mentions) with trust damping
  rising = rank(score) improved vs previous publish
```

**Deal-breaker:** ranking solely by raw mention count under open registration.

### 3.4 Counter algorithms — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Exact hashmap** | Precise | Memory; cardinality blowup | Hot candidate set only |
| **Count-Min Sketch (CMS)** | Fixed memory; mergeable | Over-estimate; no identity of heavies alone | Long-tail frequency |
| **CMS + heap / SpaceSaving** | Finds heavies | Error on near-threshold | Classic heavy-hitters |
| **HeavyKeeper** | Better accuracy for heavies | Slightly more complex | **Strong MVP pick** |
| **HyperLogLog** | Uniques | Not frequency | Unique-user feature |
| Redis `ZINCRBY` everywhere | Simple | Won’t scale all tags×regions×windows | Hot tags / small deployments |

**Chosen MVP:**

1. **Per-region stream job:** HeavyKeeper (or CMS+SpaceSaving) for observations.  
2. Maintain **exact counters** for current top-C candidates + any tag crossing threshold.  
3. **Global merge:** exact merge of regional candidate lists (not sketches of everything).  
4. Optional **HLL** per candidate for unique users.

### 3.5 Windowing — Why X over Y

| Mode | Semantics | Pros | Cons |
|------|-----------|------|------|
| **Tumbling** | Fixed non-overlap buckets | Simple; cheap | Boundary artifacts |
| **Sliding** | Overlap; smooth | Better UX | More state (buckets) |
| **Session** | Gap-based | Good for bursts | Not for global boards |
| **Decay (EMA)** | Continuous half-life | No hard window | Harder to explain “24h” |

**Chosen:**

| Window | Implementation |
|--------|----------------|
| 5m | Sliding with 10–30s tumbling sub-buckets; sum last N buckets |
| 1h | Sliding with 1m buckets OR 12×5m rolls |
| 24h | Tumbling hourly rolls + sum; or decay with advertised half-life |
| 7d | Hourly/daily rolls; batch-friendly |

**Deal-breaker:** claiming true per-event sliding windows for all tags at 5M events/s without bucketing/approx.

### 3.6 Pipeline topology

```text
Client posts → Post Service → emit HashtagEvents → Kafka
  → Regional Flink jobs (keyed by region, subkeyed by tag hash)
  → Regional candidate store + board
  → Global merger (consume regional boards / candidate deltas)
  → Global board store
  → Edge/CDN cache → Trend API → Clients
```

### 3.7 Why X over Y (summary table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Storage of all counts | Sketches + candidate exact | Cardinality | Exact Redis ZSET for all tags globally |
| Aggregation | Region first, then merge | Ship top-C not all keys | Central counter for every event |
| Stream engine | Flink (or equivalent) | Event-time, state, exactly-once opts | Cron-only at 5m freshness SLO |
| Query path | Snapshot + CDN | Read QPS | Live compute top-K on each GET |
| Spam | Multi-signal score | Gaming | Raw count trends |
| Hot tags | Exact sidecar | Accuracy where it matters | One CMS for `#TaylorSwift` and long tail alike without refinement |

---

## 4. Architecture Diagram

```text
                    +------------------+
   Users/Apps --->  |   Trend API      |-----> Edge / CDN cache (public boards)
                    +--------+---------+
                             |
                             v
                    +--------+---------+
                    | Board Store      |  Redis / Memorystore / Spanner
                    | (window,region)  |  snapshots + hot exact scores
                    +--------+---------+
                             ^
                             | publish
          +------------------+------------------+
          |                                     |
          v                                     v
 +------------------+                 +------------------+
 | Global Merger    |<-- candidates --| Regional Aggs    |
 | merge top-C      |                 | Flink / Dataflow |
 +--------+---------+                 +--------+---------+
          |                                     ^
          |                                     | consume
          |                            +--------+---------+
          |                            | Kafka topics     |
          |                            | events.enriched  |
          |                            | by region (or    |
          |                            | key=region)      |
          |                            +--------+---------+
          |                                     ^
          |                                     |
          |                            +--------+---------+
          |                            | Post / Emit svc  |
          |                            | normalize tags   |
          |                            | trust, geo       |
          |                            +------------------+
          |
          v
   Policy / Admin (suppress, pin) ---> filter at publish
   Spam / Anomaly service ----------> quarantine tags / users
```

**Ingest path:**

```text
Post created
  -> extract hashtags (normalize)
  -> enrich trust + region
  -> produce Kafka(event_id, tags[], ...)
  -> ACK post path independent of trend lag
```

**Regional aggregate path:**

```text
Kafka -> Flink keyBy(region, tagBucket)
  -> update HeavyKeeper / exact candidate map
  -> per-user contribution cap (keyed state TTL)
  -> every T sec: extract top-C -> write Regional Board + Candidate topic
```

**Global merge path:**

```text
All regional candidate snapshots
  -> outer join by tag
  -> score_global = Σ score_region (or recompute)
  -> top-K heap
  -> apply policy / hysteresis
  -> publish Global Board version++
```

**Query path:**

```text
GET /trends?window=1h&region=US
  -> CDN if public & TTL valid
  -> else Board Store
  -> stale-if-error if merger lagging
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **At-least-once ingest** after Kafka ACK; processing idempotent on `event_id`.  
2. **Published boards are versioned**; readers never see partial JSON (atomic swap).  
3. **Policy suppress always wins** over score.  
4. **Freshness watermark exposed**; never silently claim live when lag > SLO.  
5. **Regional failure ≠ empty global** — serve last good + degraded flag.

#### 5.1.2 Exactly-once vs at-least-once

| Mode | Approach | Tradeoff |
|------|----------|----------|
| At-least-once + idempotent | Dedup `event_id` in short TTL state | Simpler; small overcount if dedup miss |
| Flink exactly-once | Checkpoint + transactional sink | Heavier; great for correctness |
| MVP recommendation | At-least-once + idempotent dedup window (e.g. 24h) for events; sinks atomic | Practical L5 answer |

**Deal-breaker:** double-counting the same viral post into a trend without any dedup story.

#### 5.1.3 Late events & watermarks

```text
watermark = max_event_ts - allowed_lateness (e.g. 2m)
late but in lateness: update correct bucket
too late: side output -> optional correction job / drop with metric
```

For 5m boards, large lateness increases state; bound it.

#### 5.1.4 Oscillation / rank flicker

Users hate rank jumping 3↔7 every publish.

Mitigations:

- **Hysteresis:** require score margin to steal rank.  
- **EMA smooth** displayed score.  
- **Sticky pins** for editorial.  
- Publish diffs less frequently than internal compute.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Consumer crash | Kafka replay; keyed state checkpoint |
| 10× | Hot partition (`#news`) | Key salt for hot tags; local aggregate then combine |
| 100× | Regional cell down | Global degraded mode; multi-AZ jobs |
| 1,000× | Merge thundering | Hierarchical merge tree; delta publishes |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| Kafka: `hash(region)` or region topic | Locality for regional jobs |
| Flink: `keyBy(region, tag)` | Correct per-tag state |
| Hot tag: `keyBy(region, tag, salt)` | Avoid single-key hotspot; reduce salting |

**Hot hashtag path:**

```text
Detect tag QPS > threshold
  -> enable salting (N partial counters)
  -> periodic combine to exact candidate
  -> bypass sketch; use sharded exact
```

#### 5.2.2 Approximate structures deep dive

**Count-Min Sketch**

```text
CMS(ε, δ): width=⌈e/ε⌉, depth=⌈ln(1/δ)⌉
Estimate(tag) ≥ true; error ≤ ε·‖stream‖ with prob 1-δ
Mergeable across shards — but merging CMS then taking top-K is NOT the same as
top-K of merged regional heavy-hitter candidate lists
```

**Interview nuance (deal-breaker to miss):**  
Merging sketches then taking top-K ≠ merging regional top-K lists. Prefer **merge candidates** for global board; use CMS inside a region for discovery of heavies.

**HeavyKeeper**

- Fingerprint + count with exponential decay on collisions.  
- Better precision for true heavies than naive CMS+heap under same memory.  
- Still pair with exact map once a tag is “promoted.”

**Space-Saving / Misra-Gries**

- Classic heavy-hitters; good teaching answer; memory O(K/ε).

#### 5.2.3 Sliding window implementation

**Bucketed sliding window (recommended):**

```text
window = 5m, bucket = 10s → 30 buckets
For each candidate tag:
  counts[30] ring buffer
  score = sum(counts)
On bucket roll: subtract expired bucket; advance index
```

Long-tail tags: don’t allocate 30 buckets each — only for candidates; sketches hold coarse window or use decay.

**Decay alternative:**

```text
score *= 0.5 every half_life
On event: score += weight
Approximates recency without storing buckets
Explain to users as “trending heat” not “exact 24h count”
```

#### 5.2.4 Regional → global merge

```text
for each window:
  input = ∪_r TopC(region r)
  aggregate scores by tag
  compute TopK
  attach provenance (which regions contribute)
```

Correctness property:

- Any tag in global top-K with score S must appear in some region’s top-C if C is large enough **relative to score distribution**.  
- Pathological case: many regions with tiny equal counts → may miss; mitigate with larger C, random samples, or lower-threshold “honorable mentions” channel.

**Threshold rule of thumb:** choose C so that min score in regional top-C is below expected global top-K cutoff / num_regions (heuristic; validate offline).

#### 5.2.5 Read path scale

| Scale | Mechanism |
|-------|-----------|
| Baseline | Redis GET snapshot |
| 10× | + local API cache; CDN for GLOBAL |
| 100× | Edge POP caches all public region boards |
| 1,000× | Precompute + push to edge; clients rarely hit origin |

#### 5.2.6 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Sketches; candidate exact; CDN; hot-key salting |
| →100× | Regional cells; candidate topic; merger fleet; anomaly service |
| →1,000× | Metro→country→global tree; per-cell Kafka; approx uniques; board push |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
windows: [5m, 1h, 24h]
K_display: 100
C_candidates: 1000
bucket_sizes: {5m:10s, 1h:1m, 24h:1h}
per_user_cap: {5m:3, 1h:10, 24h:30}
publish_interval_ms: 5000
cms: {ε: 0.001, δ: 1e-4}   # if used
suppress_list: ref
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `ingest_events_per_s` | Load |
| `kafka_lag` | Freshness risk |
| `watermark_delay` | Event-time health |
| `board_publish_age` | User-visible freshness |
| `approx_error_sample` | Offline vs exact audit |
| `quarantined_tags` | Spam efficacy |
| `hot_tag_salt_active` | Hotspot control |
| `rank_flicker_rate` | UX stability |

#### 5.3.3 Offline audit (trust but verify)

Daily job: sample tags, compute exact counts from log for last 1h, compare to sketch/candidate estimates; alert if error exceeds budget for tags above threshold.

#### 5.3.4 Testing

- Deterministic event fixtures → expected top-K.  
- Adversarial bot traffic tests.  
- Hot-key chaos (single tag 80% traffic).  
- Region kill → degraded global.  
- Replay rebuild matches (within approx bounds).

#### 5.3.5 Operability

- Dual-run new scoring (`score_v2`) shadow → compare boards.  
- Feature flag hysteresis params.  
- Rebuild from Kafka with new job version into shadow store; atomic cutover.

---

## 6. Wrap-Up

### 6.1 What we designed

A **trending-hashtag service** that ingests enriched tag events, aggregates **regionally** with heavy-hitter sketches + exact candidates across **multiple rolling windows**, merges to **global** top-K, publishes versioned boards to a cacheable read path, and resists spam via caps, trust, and quarantine—not a giant exact global counter.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Exact vs approx | Exact candidates; approx long tail |
| Sliding vs tumbling | Bucketed sliding short windows; rolls for long |
| CMS merge vs candidate merge | **Candidate merge** for global top-K |
| Raw counts | Insufficient — unique/trust/velocity |
| Central aggregator | Deal-breaker at scale — regional first |
| Query compute | Snapshot boards; never per-request top-K scan |

### 6.3 30-second scale narrative

> Baseline: Kafka + Flink per region, HeavyKeeper + exact top-C, publish boards to Redis, CDN for GETs. 10× forces hot-tag salting and strict candidate discipline. 100× splits regional cells and a global merger on top-C only. 1,000× uses hierarchical geo merge and edge push—freshness from watermarks, not from pretending every tag has an exact global counter.

### 6.4 Deal-breakers checklist

- Exact counts for all tags × regions × windows in Redis.  
- Global top-K by merging CMS sketches only.  
- Trends = raw mention count under bots.  
- Computing top-K on every API request.  
- Single unpartitioned hot key for `#viral`.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Trending vs popular?**  
A: Trending emphasizes recent velocity/recency; popular may be all-time or long-window volume. Product should label windows clearly.

**Q2: Do reposts count?**  
A: Product call — if yes, weight differently; always apply per-user caps.

**Q3: Multi-tag posts?**  
A: Emit one observation per tag; consider total weight split to avoid multi-tag spam.

**Q4: Localized language boards?**  
A: Phase 2 — another scope dimension (`region × lang`); same merge patterns.

**Q5: Should NSFW tags appear?**  
A: Policy filter at publish; may still track internally for abuse.

### 7.2 Algorithms

**Q6: Explain Count-Min Sketch.**  
A: `d` hash rows × `w` counters; incr all rows; estimate = min of rows; overestimates; memory independent of cardinality.

**Q7: Why overestimate is OK?**  
A: Heavies still rank high; combine with exact verification for displayed top-K.

**Q8: How does HeavyKeeper differ?**  
A: Uses fingerprints and probabilistic decay on collisions → fewer false heavies under same memory.

**Q9: Misra-Gries / Space-Saving?**  
A: Maintain K counters; on unseen & full, decrement all; survivors are heavy-hitter candidates.

**Q10: How to get unique users cheaply?**  
A: HLL per candidate tag; or “count-distinct” approx; or cap each `user` to N counted mentions.

**Q11: Exact top-K with limited memory?**  
A: Impossible in general for arbitrary streams without approx or multi-pass; cite heavy-hitters theory.

**Q12: Decay vs sliding window?**  
A: Decay is continuous and cheap; sliding matches user-facing “last 1 hour” literally via buckets.

### 7.3 Windows & time

**Q13: Tumbling vs sliding?**  
A: Tumbling non-overlap; sliding overlap. Sliding needs buckets or rewindable state.

**Q14: Event-time vs processing-time?**  
A: Event-time correct under lag; needs watermarks. Processing-time simpler, wrong under backlog.

**Q15: Allowed lateness tradeoff?**  
A: Larger lateness → more corrective accuracy, more state and delay before window closes.

**Q16: How do you implement a 7-day window?**  
A: Daily/hourly rolls + sum; don’t keep 7 days of per-event state.

### 7.4 Distributed systems

**Q17: Why regional then global?**  
A: Data locality, blast radius, and merge input size O(regions × C) not O(all tags).

**Q18: Hot partition fix?**  
A: Salting, local pre-agg, split hot tag to dedicated operators.

**Q19: Exactly-once end-to-end?**  
A: Flink checkpoints + idempotent/transactional sinks; still need dedup at emit for upstream duplicates.

**Q20: How to rebuild after bad deploy?**  
A: Replay Kafka from timestamp into shadow stores; atomic board pointer swap.

**Q21: Multi-region active-active reads?**  
A: Boards are derived data — replicate snapshots globally; compute home-region per geo cell.

### 7.5 Spam & integrity

**Q22: How do bots game trends?**  
A: Many accounts, same tag, synchronized bursts. Defend with signup trust, device signals, graph features, velocity z-scores, human/engagement quality.

**Q23: Why per-user caps aren’t enough?**  
A: Sybil farms bypass caps; need account quality and cluster detection.

**Q24: Quarantine vs suppress?**  
A: Quarantine temporary while reviewing anomaly; suppress is policy/legal permanent for boards.

**Q25: Can we use ML classifiers?**  
A: Yes Phase 2 on user/post spam; keep MVP rules + stats explainable.

### 7.6 API & UX

**Q26: How to avoid flicker?**  
A: Hysteresis, EMA, slower display publish than internal compute.

**Q27: Rising vs top?**  
A: Rising sorts by delta rank/velocity; top by score; offer both tabs.

**Q28: Caching authenticity?**  
A: Short TTL; `Last-Published` header; stale-if-error better than empty.

**Q29: Personalized trends?**  
A: Offline affinity × tag embeddings; online retrieve candidate union — out of MVP but extend scopes.

### 7.7 Estimation drills

**Q30: Memory if exact 2B tags × 50 regions × 3 windows × 16B?**  
A: 2B×50×3×16 ≈ 4.8e12 bytes ≈ **4.8 PB** — argue approx immediately.

**Q31: Merge QPS math?**  
A: 200 regions × 2K candidates / 5s ≈ 80K row updates/s — easy vs 5M event/s ingest.

**Q32: CDN origin QPS?**  
A: With TTL 5s and 600 board keys: ~120 origin refreshes/s plus misses — fine.

### 7.8 Alternatives & deal-breakers

**Q33: Only Redis ZINCRBY + ZREVRANGE?**  
A: Fine at small scale / hot tags; fails on cardinality and multi-window multi-region memory.

**Q34: Only batch every hour?**  
A: Misses 5m freshness product requirement.

**Q35: Single global Flink job?**  
A: Works until hot keys and blast radius hurt; regional cells preferred at 100×.

**Q36: Store every event in OLAP and query top-K?**  
A: Great for analytics; too slow/expensive for 5m homepage board as sole design.

### 7.9 Interview craft

**Q37: How to open?**  
A: Clarify windows, K, global+regional, approx OK?, spam bar, freshness SLO — then load classes.

**Q38: What numbers matter?**  
A: Events/s, distinct tags, regions × windows, candidate C, query QPS, lag SLO.

**Q39: What impresses L5+?**  
A: Candidate merge correctness caveat, hot-key salting, hysteresis, explicit deal-breakers, progressive scale story.

**Q40: Common mistake?**  
A: Designing fancy sketches then computing top-K on every read; or ignoring gaming.

---

### Appendix A — Normalization rules

```text
1. Unicode NFKC
2. Casefold
3. Strip leading '#'
4. Map confusables (optional)
5. Max length 64; drop otherwise
6. Emoji tags: allowlist policy
```

### Appendix B — Heavy-hitter + exact promotion

```text
onObservation(tag, w):
  sketch.add(tag, w)
  if tag in exactMap OR sketch.estimate(tag) >= promoteThreshold:
    exactMap[tag] += w
    maybeShrinkExactMap()  // demote cold

every publish:
  candidates = topC(exactMap) ∪ sketch.heavies()
  refine exact for candidates
  board = topK(candidates)
```

### Appendix C — Bucketed sliding window

```text
class SlidingCounter:
  buckets[B]
  idx
  add(w):
    buckets[idx] += w
  roll():
    idx = (idx+1) % B
    buckets[idx] = 0
  sum():
    return Σ buckets
```

### Appendix D — Global merge pseudocode

```text
def merge(regional_boards):
  scores = defaultdict(float)
  for board in regional_boards:
    for tag, score in board.candidates:
      scores[tag] += score
  return heap_top_k(scores, K)
```

### Appendix E — Per-user contribution cap

```text
key = (window_bucket, region, tag, user)
if contrib[key] < CAP:
  add = min(weight, CAP - contrib[key])
  contrib[key] += add
  observe(tag, add * trust)
else:
  drop / metric
```

### Appendix F — Hot tag salting

```text
salt = hash(event_id) % N
partial_key = (region, tag, salt)
# periodic:
exact[tag] = Σ_s exact[(tag,s)]
```

### Appendix G — Progressive scale table

| Scale | Ingest | Agg | Merge | Read |
|-------|--------|-----|-------|------|
| Baseline | 1 Kafka cluster | 1 Flink region pool | Single merger | Redis |
| 10× | Partition surge | Sketch+exact | Merger HA | CDN global |
| 100× | Regional Kafka | Cells per geo | Hierarchical | Edge all boards |
| 1,000× | Cell fabric | Metro aggs | Tree merge | Push to POP |

### Appendix H — Scoring versions

| Version | Formula | Notes |
|---------|---------|-------|
| v1 | capped mentions | MVP |
| v2 | v1 × unique^β | HLL |
| v3 | v2 × velocity | Rising |
| v4 | ML anomaly downweight | Phase 2 |

### Appendix I — Board JSON schema

```json
{
  "window": "1h",
  "region": "US",
  "version": 184422,
  "published_at": "2026-08-06T03:00:05Z",
  "watermark": "2026-08-06T02:59:40Z",
  "degraded": false,
  "items": [
    {"rank": 1, "tag": "worldcup", "score": 912345.5, "delta_rank": 2}
  ]
}
```

### Appendix J — NFR card

```text
Ingest durable (Kafka multi-AZ)
5m board lag p99 < 60s
Query p99 < 100ms cached
Approx error audited for heavies
Suppress wins
No raw-count-only ranking
```

### Appendix K — Comparison: CMS vs HeavyKeeper vs Exact

| Property | CMS | HeavyKeeper | Exact map |
|----------|-----|-------------|-----------|
| Memory | Fixed | Fixed-ish | O(cardinality) |
| Error | Overcount | Better on heavies | None |
| Identify heavies | Needs heap helper | Built-in better | Trivial |
| Merge | Easy | Possible | Easy |
| Use | Long tail | Regional heavies | Candidates / hot |

### Appendix L — Flink job sketch

```text
env.addSource(kafka)
  .assignTimestampsAndWatermarks(...)
  .flatMap(expandTags)
  .keyBy(e -> e.region + "|" + e.tag)
  .process(new HeavyHittersFunction())
  .keyBy(e -> e.region)
  .window(TumblingProcessingTimeWindows.of(Duration.ofSeconds(5)))
  .apply(publishRegionalBoard)
```

### Appendix M — Anomaly features

| Feature | Signal |
|---------|--------|
| Velocity z-score | Burst vs baseline |
| Unique/mention ratio | Low → spam |
| New account fraction | Sybil |
| Graph cluster density | Coordinated |
| Cross-region sync | Botnet |

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just use Redis” | Cardinality × scopes |
| “Exact is required” | Exact for displayed K after promotion |
| “Batch is fine” | Conflicts with 5m freshness |
| “Merge the sketches” | Wrong for global top-K guarantee story |

### Appendix O — Related Google systems (conceptual)

| System | Relation |
|--------|----------|
| Pub/Sub / Kafka | Ingest bus |
| Dataflow / Flink | Aggregators |
| Memorystore / Bigtable | Boards / hot scores |
| Mesa / analytical stores | Historical trends |
| Edge CDN | Query scale |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Heavy hitter | Key with frequency ≥ threshold |
| Candidate set C | Tags eligible for board refinement |
| Watermark | Event-time progress marker |
| Hysteresis | Rank change resistance |
| Salting | Split hot key into N partials |
| Board | Published top-K snapshot |

### Appendix Q — Worked example

```text
Baseline 50K events/s × 1.5 tags = 75K observations/s
50 regions — assume uneven; top region 20% = 15K obs/s
HeavyKeeper memory ~ few MB / operator × shards — fine
Publish every 5s: 50 regions × 3 windows × 1KB board ≈ 150 KB / 5s trivial
Global merge 50 × 1000 = 50K rows / 5s
Query 10K QPS global hit CDN — origin ~ board keys / TTL
```

### Appendix R — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Are boards strongly consistent globally? | No — derived, versioned, eventual |
| Read-your-write for poster? | Not required for trends UX |
| Cross-region same second? | May differ briefly; OK |
| Suppress latency | Next publish ≤ interval |

### Appendix S — 30m interview checklist

1. Clarify windows, K, region, approx, spam, freshness.  
2. Estimate events/s & cardinality → reject all-exact.  
3. Draw Kafka → regional Flink → merge → Redis → CDN.  
4. Deep dive sketches + candidate exact + hot-key.  
5. Spam scoring + hysteresis.  
6. Walk 10×/100×/1,000×.  
7. List deal-breakers.

### Appendix T — Pseudocode score

```text
def score(tag, window, region):
  mentions = exact_or_est(tag)
  capped = apply_user_caps(mentions)
  uniq = hll.cardinality(tag) if candidate else None
  trust = trust_ema(tag)
  vel = capped - prev_bucket(tag)
  base = capped
  if uniq: base *= (uniq / max(capped,1)) ** β
  base *= trust ** γ
  base *= (1 + δ * norm(vel))
  return base
```

### Appendix U — Editorial pins

```text
pins[(window,region)] = [tagA, tagB]
publish:
  board = computed_top_k
  insert pins at reserved ranks
  shift others; mark editorial=true
```

### Appendix V — What changes at each scale (quick card)

| Scale | Must add |
|-------|----------|
| 10× | Sketches, CDN, salting |
| 100× | Regional cells, anomaly, candidate bus |
| 1,000× | Hierarchical merge, edge push, cell fabric |

---

*End of Trending-Hashtag Service system design.*
