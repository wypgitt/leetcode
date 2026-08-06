# System Design: TikTok-Style Google News

> **Focus areas:** Vertical swipe UX · Candidate generation · LTR ranking · Personalization · Cold start · Freshness vs engagement · Video/image CDN · Session features · Exploration/exploitation · Safety/misinfo · Push vs pull materialization · Fanout tradeoffs · A/B hooks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split retrieval/rank/serve/media planes, explicit freshness–engagement tradeoff, resolved timeline materialization (push vs pull)  
> **Interview theme:** Google L5+ — personalized **vertical news feed** (For You–style) for news cards/short video, not a generic social network or classic headline list alone

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

Goal: **bound the product**—**TikTok-style Google News**: a personalized, vertically swiped feed of news stories and short news video, with strong freshness, media delivery, ranking, and safety — distinct from desktop News headlines-only or YouTube long-form.

### 1.0 What this is / is not

| Dimension | **TikTok-style Google News (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary UX | Full-bleed vertical swipe cards / short video | Infinite classic blue-link list only |
| Success | Informed + engaged sessions; trust; retention | Pure watch-time maximization |
| Content | Publisher news + short video explainers | UGC dance/social graph first |
| Ranking | Freshness × personalization × quality/safety | Engagement-only TikTok clone |
| Graph | Weak follow; topical affinity | Fanout-on-write follow graph core |
| Identity | Signed-in + privacy-safe signed-out | Require social profile |

**Scope statement:** Design a **personalized vertical news feed** with candidate generation, LTR ranking, media CDN, cold start, misinfo safety, and progressive scale — Google News product values (freshness, authority, diversity) inside a TikTok-like interaction model.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | UX? | Vertical swipe; autoplay short video; tap for article | Session stream API; prefetch N |
| F2 | Content types? | Text cards, image, short video ≤60–90s, live later | Polymorphic item schema |
| F3 | Personalization? | Interests, location, language, history | Profile + real-time session |
| F4 | Freshness? | Breaking news must surface fast | Recency channels + boosts |
| F5 | Ranking? | Multi-objective LTR | Retrieval → rank → re-rank |
| F6 | Cold start? | Signed-out + new users | Context (geo/lang/trending) + explore |
| F7 | Follow publishers? | Optional; not only source | Hybrid affinity |
| F8 | Safety? | Misinfo, violence, medical, election | Classifiers + policy tiering |
| F9 | Notifications? | Breaking push optional Phase 1.5 | Separate notify ranker |
| F10 | Offline? | Prefetch next few items | Client buffer + CDN |
| F11 | A/B? | First-class experiments | Layered experimentation |
| F12 | Monetization? | Light ads Phase 2 | Ad slot in re-rank; don’t poison trust |

**MVP functional scope:**

1. Authenticated + signed-out **For You** vertical feed (`GetFeed` page).  
2. **Candidate generation** from multiple retrievers (fresh, topical, collaborative, trending, explore).  
3. **LTR ranker** + **re-rank** (diversity, freshness, safety, publisher caps).  
4. **Media delivery** via CDN (images + short video); adaptive bitrate.  
5. **Engagement events**: impression, watch time, swipe-away, open article, share, not-interested.  
6. **Cold start** via geo/lang/trending + short onboarding interests.  
7. **Safety**: drop/demote policy-violating and low-authority medical/election.  
8. **Session personalization** mid-session (topic stickiness + fatigue).  
9. Experimentation hooks (retrieval mix, ranker model, UI).  
10. Prefetch next K cards for swipe fluidity.

**Out of MVP:**

- Full live TV / long-form YouTube replacement  
- Social comments as primary graph  
- Perfect global election integrity suite (hooks + baseline classifiers)  
- Heavy ads optimization  
- Publisher CMS (ingest exists; tools deferred)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-first-card | Instant feel | p50 < 300ms, p99 < 1s (edge cached meta) |
| N2 | Swipe fluidity | Next card ready | Prefetch hit ≥95% |
| N3 | Video start | Fast start | p50 TTFF < 500ms on warm CDN |
| N4 | Freshness | Breaking | Eligible in feed < 1–3 min after publish ingest |
| N5 | Availability | Consumer | 99.9% feed; degrade to trending |
| N6 | Privacy | Sensitive interests | On-device signals optional; purpose limitation |
| N7 | Safety | High severity | Fail closed on election/medical policy paths |
| N8 | Fairness / diversity | Avoid rabbit holes | Re-rank constraints; explore quota |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Open app → first card from prefetch/cache → swipe → personalized next.  
2. Breaking alert story enters fresh retriever → boosted into feed within minutes.  
3. User watches sports video 40s → session affinity upweights sports candidates.  
4. “Not interested” → negative signal; suppress cluster.  
5. Signed-out in FR-fr → localized trending + language pack.  
6. Experiment bucket B gets new ranker → metrics via exo.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Ranker timeout | Serve retrieval-only / cached mix; mark degraded |
| CDN video miss | Lower quality ladder; image poster fallback |
| Misinfo claim spike | Safety hold; demote unverified; show context panel |
| Filter bubble | Diversity re-rank; explore slots |
| Publisher spam flood | Publisher caps; quality prior |
| Clickbait high CTR | Multi-objective: penalize short dwell / backswipe |
| Cold device | Trending + geo; prompt light interests |
| Duplicate story cluster | Cluster_id collapse; pick best format |
| Region block | License/geo filter at retrieve + serve |
| Mid-session topic fatigue | Decay affinity; inject diversify |
| Push vs pull inconsistency | Feed stampede control; versioned feed tokens |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 20M | 200M | 2B | multi-B class |
| Peak QPS `GetFeed` | 50K | 500K | 5M | 50M |
| Cards / session | ~30 | ~30–50 | ~50 | ~50 |
| Candidate pool / req | ~1–2K | ~2–5K | ~5–10K | approx + stages |
| Ranked items returned / page | 10 | 10 | 10 | 10 |
| Events / day | 5B | 50B | 500B | 5T |
| Catalog active items (hot) | 5M | 50M | 500M | cells |
| Short videos stored | 10M | 100M | 1B | selective + lifecycle |
| CDN egress | 5 Tbps peak | 50 | 500 | multi-region huge |
| Breaking ingest → feed | <3 min | <2 min | <1 min | seconds-class |
| Experiments concurrent | 50 | 200 | 1K | platform |

**What each jump forces:**

- **10×:** Multi-stage retrieval; feature cache; regional CDN; session store.  
- **100×:** Feed cells; approximate ANN; two-tower + LTR fleet; safety platform.  
- **1,000×:** On-device ranking assists; aggressive materialization for head; global edge decisioning.

### 1.5 Etc. (Constraints & Assumptions)

- Content comes from **publisher ingest + News corpus + short video pipeline** (existing Google News DNA).  
- Interaction model is **TikTok-like**; objective function is **not** pure watch time — news trust/freshness constraints.  
- **Home timeline fanout-on-write** (Twitter classic) is a poor primary fit for news personalization — prefer **pull-time ranking** with selective push for breaking/head.  
- A/B and privacy reviews are mandatory for ranking changes.

**Scope statement to repeat back:**

> Design TikTok-style Google News: vertical personalized feed with multi-retriever candidate generation, multi-objective LTR, session-aware re-ranking, CDN media, cold start, misinfo safety, and push/pull materialization tradeoffs — scaling 10×/100×/1,000× with experimentation hooks — optimizing informed engagement, not pure addiction metrics.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Plane |
|-------|------|------------------------|-----|-------|
| **Feed request** | `GetFeed` pages | ~50K/s | ~500K/s | Edge + mixer |
| **Retrieval fanout** | N retrievers × req | ~50K × 5 = 250K calls/s | ×10 | Retrievers |
| **Ranker** | Score 1–2K cands | ~50K rank jobs/s | ×10 | GPU/CPU fleet |
| **Feature fetch** | User/item/session | ~hundreds of K reads/s | ×10 | Feature store / cache |
| **Event ingest** | Imp / watch / swipe | ~200K–1M/s peak | ×10 | Kafka |
| **Media** | Video chunks | Tbps | ×10 | CDN |
| **Ingest publish** | New stories | ~100–1K/s | ×10 | News pipeline |
| **Safety score** | Item + claim | Fraction of ingest + query | ×10 | Safety |

**Anti-pattern:** one QPS covering feed, ANN, LTR, CDN, and events.

### 2.2 Bandwidth (video-heavy)

```text
Assume 40% cards are video; avg watch 12s; bitrate 1.5 Mbps effective
Peak concurrent watchers = f(DAU, session concurrency)
Interview sketch: 2M concurrent video viewers × 1.5 Mbps ≈ 3 Tbps
Design CDN + midgress; never origin-fetch per swipe
```

### 2.3 Ranking compute

```text
50K feed/s × 1500 candidates × 50ns-ish feature touch → need multi-stage
Stage A: cheap model / ANN retrieve 2000
Stage B: LTR on 200–500
Stage C: re-rank constraints top 50 → return 10
```

**Deal-breaker:** full deep model on 10K candidates per request at 50K QPS without staging.

### 2.4 Event volume

```text
20M DAU × 40 impressions/day = 800M impressions
+ watches/swipes/clicks → ~2–5B events/day baseline order
10× → tens of billions; log sampling for training OK; billing-quality events kept
```

### 2.5 Catalog & freshness

```text
Hot corpus: last 48h news + evergreen explainers
5M hot items × features 2 KB = 10 TB feature cache fleet-wide (replicated)
Breaking: must enter ANN/fresh indexes in <1–3 min
```

### 2.6 Cost sketch

```text
Dominated by: CDN egress, ranker fleet, event storage
Save: adaptive bitrate, prefetch discipline, candidate truncation, on-device lite rank assist at extreme scale
```

---

## 3. High-Level Design

### 3.1 Client UX & API

| API | Semantics |
|-----|-----------|
| `GetFeed(user, session, cursor, limit)` | Next page of ranked items |
| `PrefetchHints` | CDN URLs + codecs for next K |
| `LogEvents(batch)` | Imp, watch_ms, swipe, open, dismiss |
| `NotInterested(item_id, reason?)` | Negative feedback |
| `UpdateInterests(topics)` | Explicit cold-start |

**Feed item:**

```text
Item {
  item_id, cluster_id, type (article|video|gallery)
  title, publisher_id, published_at
  media: { poster, hls/dash urls, duration }
  safety_tier, topics[], geo_allow
  debug_explanations? (internal)
}
```

### 3.2 Multi-stage funnel

```text
Ingest → Index/ANN/Fresh
GetFeed → Retrievers (parallel) → Union/dedup
      → LTR rank → Diversity/safety/freshness re-rank
      → Attach media URLs → Client
Events → Join features → Train / online learning
```

### 3.3 Candidate generation (retrieval)

| Retriever | Signal | Why |
|-----------|--------|-----|
| **Fresh / breaking** | Recency + authority | News non-negotiable |
| **Topical ANN** | User embedding × item | Personalization |
| **Collaborative** | Co-engagement | Serendipity |
| **Publisher affinity** | Follow / dwell history | Loyalty |
| **Trending / local** | Geo + velocity | Cold start + community |
| **Explore** | ε-slots / bandit arms | Escape filter bubble |
| **Subscriptions** | Explicit follows | User control |

**Union size:** ~1–2K unique after dedup/cluster collapse.

### 3.4 Ranking (LTR) & objectives

| Objective | Proxy | Tension |
|-----------|-------|---------|
| Engagement | watch_ms, open, share | Clickbait |
| Freshness | age decay, breaking boost | May cut watch time |
| Quality / authority | publisher prior, claims | May cut virality |
| Satisfaction | long dwell, less backswipe | Hard to measure |
| Diversity | topic/publisher entropy | Short-term engagement |
| Safety | policy scores | Fail closed |

**Chosen:** multi-task / multi-objective LTR with **constrained re-rank** (hard safety filters; soft diversity/freshness).

### 3.5 Push vs pull feed materialization

| Approach | Pros | Cons | News fit |
|----------|------|------|----------|
| **Pull (rank at read)** | Fresh + personalized | CPU at QPS | **Primary MVP** |
| **Push fanout-on-write** | Fast read | Write amp; stale personalization | Poor for global news |
| **Hybrid** | Push breaking/head to caches; pull rank rest | Complexity | **10×+ chosen** |
| Precompute per-user timelines | Low read latency | Storage explosion; stale | Only celebrity/head segments |

**Deal-breaker for news:** pure Twitter-style fanout-on-write of every story to every follower — wrong graph, wrong freshness/personalization mix.

**Home timeline note:** if product has “Following” tab, **small** fanout or pull-merge for followed publishers; **For You** remains pull-ranked.

### 3.6 Cold start

| User state | Strategy |
|------------|----------|
| Signed-out | Geo, lang, device, trending, explore |
| New signed-in | Optional 5–10 topic chips; transfer signed-out session |
| Sparse history | Rely on content-based + trending; higher explore rate |
| Returning | User tower embedding + session |

### 3.7 Media delivery

```text
Ingest video → transcode ladder → origin packager → Google CDN / mid-tier
Client: HLS/DASH; start with poster + init segment prefetch
Images: responsive sizes; AVIF/WebP
```

### 3.8 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Feed build | Pull + hybrid cache | Fresh personalization | Pure push fanout |
| Retrieval | Multi-retriever | Coverage of news needs | Single collab model |
| Rank | Multi-objective LTR + constraints | Trust ≠ CTR | Watch-time only |
| Cold start | Context + explore + chips | No history | Empty feed |
| Media | CDN ABR | Swipe UX | Origin per view |
| Safety | Pre-rank filters + demote | Harm | Rank-only soft scores |
| Dup stories | Cluster collapse | UX | Six angles same swipe |
| Experiments | Layered exo | Velocity | One global model forever |

---

## 4. Architecture Diagram

```text
  +------------------+     +-------------------+
  | Publishers /     | --> | News Ingest       |
  | Video studio     |     | parse, cluster,   |
  +------------------+     | safety, media     |
                           +---------+---------+
                                     |
                     +---------------+---------------+
                     v               v               v
              +-----------+   +-----------+   +-------------+
              | Doc/Meta  |   | ANN/Index |   | Media Origin|
              | Store     |   | Fresh idx |   | + Transcode |
              +-----------+   +-----+-----+   +------+------+
                                    |                |
                                    |                v
                                    |         +-------------+
                                    |         | CDN Edge    |
                                    |         +------+------+
 +-----------+                      |                |
 | Clients   | <--------------------+----------------+
 | swipe UX  |
 +-----+-----+
       | GetFeed / events
       v
 +-----+-------+     +----------------+
 | Edge API    | --> | Feature Service|
 | auth, exo   |     | user/session   |
 +-----+-------+     +--------+-------+
       |                      |
       v                      v
 +-----+----------------------+----+
 | Mixer / Orchestrator            |
 | parallel retrievers → LTR →     |
 | re-rank (fresh, diversity,      |
 | safety, publisher caps)         |
 +-----+---------------------------+
       |
       +--> Fresh Retriever
       +--> Two-Tower ANN
       +--> Trending / Local
       +--> Explore Bandit
       +--> Following merge (optional)
       |
       v
 +------------------+     +------------------+
 | Event Pipeline   | --> | Train / Bandit   |
 | Kafka → join     |     | model publish    |
 +------------------+     +------------------+

  Safety platform sits on ingest + pre-serve filters
  Experimentation assigns arms at Edge API
```

**GetFeed path:**

```text
client -> edge (exo assign) -> features
  -> retrieve parallel -> dedupe/cluster
  -> LTR -> constrained re-rank -> media signed URLs
  -> response + prefetch hints
```

**Breaking path:**

```text
publish -> safety -> cluster
  -> fresh index + optional push to regional head caches
  -> next GetFeed pulls into candidates with boost
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Safety fail-closed** for blocked tiers (violence, egregious medical/election policy).  
2. **No empty feed** if catalog alive — degrade to trending/local.  
3. **Cluster_id uniqueness in page** — don’t show near-dup story back-to-back.  
4. **Experiment assignment sticky** per session/user layer.  
5. **Media URLs** time-limited / signed; rotate without breaking prefetch window.

#### 5.1.2 Degradation ladder

```text
1. Full retrieve + LTR + re-rank
2. Skip expensive retrievers; keep fresh + trending
3. Cached For You page (short TTL) per cohort
4. Global trending pack (edge)
Never: spin forever on ranker
```

#### 5.1.3 Freshness vs engagement (reliability of product promise)

| Control | Mechanism |
|---------|-----------|
| Fresh slots | Reserve M positions in top N for age < T |
| Breaking boost | Multiplicative score × authority |
| Engagement penalty | Short dwell + high skip → downweight clickbait |
| Authority floor | Min publisher score for YMYL topics |

**Deal-breaker:** optimizing swipe CTR alone — turns Google News into junk viral feed.

#### 5.1.4 Safety / misinfo

| Stage | Action |
|-------|--------|
| Ingest | Claim detection; publisher reputation; demote/hold |
| Retrieve | Filter `safety_tier` |
| Re-rank | Context panels; diversity of viewpoints for contested |
| Feedback | Report → human/queue; training labels |
| Crisis | Kill switches by topic/geo |

Election/medical: **higher bar**; prefer authoritative sources; reduce explore for those queries/topics.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Ranker blip | Cohort cache |
| 10× | Feature store hotspot | Cache + keysplit |
| 100× | ANN freshness lag | Dual fresh inverted + ANN |
| 1,000× | CDN cost / thundering breakings | Mid-tier; pack popular |

### 5.2 Scalability

#### 5.2.1 Retrieval scaling

- Two-tower ANN sharded by language/geo cells.  
- Fresh index: time-sharded inverted / realtime postings for news text.  
- Trending: pre-agg counters in Redis/BT with decay.  
- Explore: epsilon or contextual bandit with arm catalog.

#### 5.2.2 Ranking fleet

| Stage | Candidates | Model |
|-------|------------|-------|
| A | 2K | Dot product / shallow |
| B | 300 | LTR (GBDT/DNN) |
| C | 50 | Constraints + light objective mix |

Batch features; avoid per-candidate RPCs (side inputs / embedding tables).

#### 5.2.3 Session features

```text
session: last_topics[], watch_histogram, skip_rate, dwell_ema, device, network
update: event stream -> session store (Redis) TTL hours
use: next GetFeed reads session vector (soft state OK)
```

Mid-session personalization critical for TikTok-like UX; **don’t wait for day-scale batch profile only**.

#### 5.2.4 Push vs pull at scale

| Scale | Materialization |
|-------|-----------------|
| Baseline | Pure pull |
| 10× | Edge cache cohort feeds (geo×lang×interest coarse) TTL 30–60s |
| 100× | Push breaking into regional head queues; personal pull merge |
| 1,000× | On-device candidate re-rank of prefetched packs |

**Fanout tradeoff for news:** followed publishers (small N) can use light push-into-user-inbox; **global For You cannot**.

#### 5.2.5 Media CDN

- Multi-tier CDN; packager origin shielded.  
- Prefetch next 1–2 videos’ init segments only (not whole file).  
- Abrupt viral story: pre-warm top edges by geo.  
- Image-first cards when bandwidth poor.

#### 5.2.6 Progressive scale

| Jump | Change |
|------|--------|
| →10× | Multi-stage rank; session Redis; regional CDN; exo |
| →100× | Cells; hybrid push breaking; safety platform; ANN cells |
| →1,000× | Device-side re-rank; massive midgress; catalog lifecycle |

#### 5.2.7 Exploration / exploitation

| Mechanism | Role |
|-----------|------|
| ε-greedy slots | Force explore positions |
| Thompson / LinUCB | Topic/publisher arms |
| Uncertainty boost | New items cold-start |
| Constraint | Cap explore in YMYL |

Track **regret** vs pure exploit offline; online guardrails on safety.

### 5.3 Maintainability

#### 5.3.1 Experimentation hooks

```text
Layers: retrieval_mix | ranker_model | re-rank_weights | ui_chrome | safety_threshold
Assignment: user_id hash sticky; session overrides rare
Logging: arm ids on every impression for join
```

**Holdouts** for long-term retention / trust metrics — not only short-term watch time.

#### 5.3.2 Observability

`feed_p99`, `ranker_timeout_rate`, `retriever_latency{r}`, `freshness_coverage@10`, `duplicate_cluster_rate`, `safety_drop_rate`, `cdn_ttff`, `prefetch_hit`, `explore_slot_fill`, `skip_rate`, `broken_media_rate`, `exo_balance`.

#### 5.3.3 Training & publish

- Daily / hourly LTR train; online learning optional for explore.  
- Model canary → shadow score → % traffic.  
- Feature skewer detection; training-serving skew monitors.

#### 5.3.4 Privacy & compliance

- Purpose-limited interest profiles; retention limits.  
- Signed-out personalization weaker; clear controls.  
- Region licensing filters tested per market.

#### 5.3.5 Operability phases

Phase 1: pull feed, fresh+ANN+trending, LTR, CDN, events.  
Phase 2: session features, explore bandits, following tab.  
Phase 3: hybrid breaking push, cells, advanced safety.  
Phase 4: on-device assist; ads re-rank slots.

---

## 6. Wrap-Up

### 6.1 What we designed

A **TikTok-style Google News** system: vertical swipe feed powered by **multi-retriever candidate generation**, **multi-objective LTR + constrained re-rank**, **session-aware personalization**, **CDN media**, **cold start**, **misinfo safety**, and **hybrid pull/push materialization** — with A/B hooks and progressive scale — optimizing for informed engagement under freshness and trust constraints.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Push vs pull | Pull For You; hybrid breaking; tiny follow fanout |
| Engagement vs freshness | Reserved fresh slots + multi-objective |
| Single vs multi retrieve | Multi mandatory for news |
| Cold start | Geo/lang/trending/explore + chips |
| Safety | Fail closed YMYL |
| Fanout-on-write | Wrong primary for news FYP |
| Prefetch | Meta + init segments, not whole catalog |

### 6.3 Closing line

> “It’s a multi-stage recommender with a news conscience — TikTok interaction, Google News constraints: pull-time ranking, reserved freshness, safety fail-closed, and CDN-backed swipe fluidity.”

---

## 7. Deeper / Related Interview Questions

### 7.1 UX & API

**Q1: Why vertical swipe changes the system?**  
A: Prefetch + TTFF + session features dominate; page size small; abandonment = skip.

**Q2: What is a feed cursor?**  
A: Opaque token with page history / seed / exo arms to avoid dupes and enable resume.

**Q3: How avoid repeating items?**  
A: Bloom/recent-seen store per user/session; cluster-level suppression.

**Q4: Offline mode?**  
A: Prefetch K items + media; expire quickly for news.

**Q5: Article vs video mix?**  
A: Re-rank quota by type and bandwidth.

### 7.2 Candidate generation

**Q6: Why multiple retrievers?**  
A: Freshness, personalization, trend, explore optimize different recalls.

**Q7: ANN stale for breaking?**  
A: Dual-write fresh inverted/realtime index; ANN catch-up async.

**Q8: How size candidate pool?**  
A: Latency budget; stage until p99 OK; typically 1–2K → 300.

**Q9: Collaborative vs content?**  
A: Collab needs data; content/geo for cold; blend.

**Q10: Publisher following?**  
A: Separate retriever; merge with cap so FYP ≠ only follows.

### 7.3 Ranking & LTR

**Q11: Pointwise vs pairwise vs listwise?**  
A: Pointwise scoring common at serve; listwise losses offline; re-rank listwise constraints.

**Q12: Multi-objective how?**  
A: Scalarization weights + constraints; or Pareto tuning via exo.

**Q13: Clickbait?**  
A: Penalize short dwell / quick skip; authority features; title quality models.

**Q14: Calibration?**  
A: Score meaning differs by type; calibrate before blend.

**Q15: Position bias?**  
A: Propensity weighting in train; randomize explore slots.

### 7.4 Personalization & session

**Q16: Long-term vs session?**  
A: Profile embedding + real-time session vector; session wins short-term intent.

**Q17: Topic fatigue?**  
A: Decay counts; diversity penalty after k similar.

**Q18: Not interested?**  
A: Hard suppress cluster/publisher short window; train negative.

**Q19: Cross-device?**  
A: User-level profile; session device-local.

**Q20: Privacy-preserving personalization?**  
A: Cohorts, on-device, limited retention — product/legal choice.

### 7.5 Cold start

**Q21: Signed-out quality?**  
A: Strong trending/local; contextual bandits; language pack.

**Q22: New publisher/video?**  
A: Explore boost with uncertainty; authority ramp.

**Q23: Onboarding chips?**  
A: Seed affinities; cheap and effective.

**Q24: Sparse markets?**  
A: Fallback languages; regional packs; more explore.

### 7.6 Freshness & news specifics

**Q25: Breaking news injection?**  
A: Fresh retriever + score boost + optional edge head cache.

**Q26: Story clustering?**  
A: URL canonical + title/simhash + entity overlap → `cluster_id`.

**Q27: Update story as facts evolve?**  
A: Same cluster; replace hero item; invalidate caches.

**Q28: Evergreen vs breaking?**  
A: Separate inventories; different age decays.

**Q29: Time zones / locality?**  
A: Local rankers; geo entitlements.

### 7.7 Media & CDN

**Q30: ABR choice?**  
A: HLS/DASH ladders; start low on cellular.

**Q31: Prefetch policy?**  
A: Next 1–2 items init+poster; cancel on fast skips.

**Q32: Origin shield?**  
A: Mid-tier caches; packager behind shield.

**Q33: Cost spike on viral?**  
A: Pre-warm; lower default bitrate; image fallback mode.

**Q34: DRM?**  
A: Rare for news clips; licensed partners optional.

### 7.8 Exploration / exploitation

**Q35: Why explore in news?**  
A: Avoid bubbles; learn new interests; surface important civic info carefully.

**Q36: Bandit vs ε slots?**  
A: Slots simple; bandits better allocation; both need safety caps.

**Q37: Measure explore success?**  
A: Long-term retention, diversity, calibrated regret — not only immediate CTR.

### 7.9 Safety & misinfo

**Q38: Where to enforce?**  
A: Ingest + retrieve filter + re-rank + UI context; defense in depth.

**Q39: Fail open or closed?**  
A: Closed for severe; soft demote for borderline.

**Q40: Medical/election?**  
A: Authority floors; reduced engage-only boosts; human queues.

**Q41: User reports?**  
A: Priority by severity/virality; feedback to training.

**Q42: Deepfakes?**  
A: Media authenticity signals; publisher trust; labels.

### 7.10 Push vs pull / fanout

**Q43: Why not fanout-on-write FYP?**  
A: Every user different; news volume high; write amp insane; stale personalization.

**Q44: When push helps?**  
A: Breaking to regional cohort caches; followed publishers’ inboxes.

**Q45: Inbox storage cost?**  
A: Cap per user; TTL; only subscription tab.

**Q46: Consistency across tabs?**  
A: Following vs For You different generators; OK.

### 7.11 Events, training, exo

**Q47: Event schema?**  
A: imp, watch_ms, skip, open_article, share, not_interested, + context.

**Q48: Training-serving skew?**  
A: Same feature log as serve; monitor deltas.

**Q49: Online learning?**  
A: Careful; use for explore arms; batch for core LTR stability.

**Q50: Experiment layers?**  
A: Orthogonal layers with interaction monitoring.

**Q51: Holdouts?**  
A: Long-term trust/retention holdout essential for news.

**Q52: Counterfactual?**  
A: Logged policies with propensities for OPE.

### 7.12 Scalability & cells

**Q53: Cell by what?**  
A: Geo/lang first; user home cell for profile writes.

**Q54: Hot item features?**  
A: Replicate embeddings globally; shard cold.

**Q55: 5M QPS feed?**  
A: Heavy cohort caching + device re-rank; cannot full LTR every time.

**Q56: Multi-region active-active?**  
A: Edge everywhere; home for profile; catalog regionalized by license.

### 7.13 Reliability drills

**Q57: Ranker outage?**  
A: Degrade ladder; alert on degraded_rate.

**Q58: Bad model ship?**  
A: Canary + auto-rollback on skip_rate/safety/freshness regressions.

**Q59: CDN outage region?**  
A: Failover POP; image mode; reduce video mix.

**Q60: Misinfo crisis?**  
A: Topic kill switch; authority-only mode; incident runbook.

### 7.14 Product / interview meta

**Q61: How different from TikTok?**  
A: Publisher authority, freshness SLOs, misinfo, multi-objective trust.

**Q62: How different from classic Google News?**  
A: Session video UX, continuous swipe ranker, stronger session features.

**Q63: L5 signals?**  
A: Multi-stage funnel math, push/pull honesty, freshness constraints, safety fail-closed, exo layers.

**Q64: Metrics dashboard?**  
A: TTFF, freshness@10, diversity, skip, dwell, safety incidents, retention — not CTR alone.

**Q65: Ads later?**  
A: Re-rank slots with separation; brand safety; don’t train organic solely on ad CTR.

**Q66: Copyright / scrapes?**  
A: Licensed ingest; snippet policies; media rights metadata.

**Q67: Live news?**  
A: Separate low-latency path; chatty updates; Phase 2.

**Q68: Comments?**  
A: Optional; moderation cost; out of MVP.

**Q69: Accessibility?**  
A: Captions mandatory for video; screen reader labels on cards.

**Q70: Closing tradeoff?**  
A: Personalization and watch time are bounded by freshness, authority, and safety — say the constraints before the neural net.

---

## Appendix A: Example `GetFeed` response (shape)

```text
{
  "cursor": "opaque...",
  "items": [
    {
      "item_id": "...",
      "cluster_id": "...",
      "type": "video",
      "title": "...",
      "publisher": "Reuters",
      "published_at": 1710000000,
      "media": {"poster": "https://cdn/...", "playlist": "https://cdn/.../master.m3u8"},
      "topics": ["world", "elections"],
      "safety_tier": "ok"
    }
  ],
  "prefetch": ["item2_init", "item3_init"],
  "exo": {"ranker": "ltr_v3", "explore": 0.08}
}
```

## Appendix B: Re-rank constraints (examples)

```text
- Max 2 items per publisher per page
- Max 3 items per topic cluster per page
- ≥1 item with age < 2h in top 10 when breaking active (market-dependent)
- safety_tier ∈ {ok, labeled}; block {remove}
- YMYL: publisher_authority ≥ threshold
- Explore: exactly k slots in positions {4, 8} unless crisis mode
```

## Appendix C: Event → feature join

```text
event(user, item, type, ts, watch_ms, exo_arms, position)
  join item_features_asof
  join user_features_asof
  -> training row / session update
```

## Appendix D: Deal-breaker checklist

| If you hear… | Push back |
|--------------|-----------|
| “Fanout like Twitter timeline” | Wrong for FYP news |
| “Rank by watch time only” | Junk / misinfo |
| “Single ANN retriever” | Misses breaking |
| “Personalize signed-out heavily” | Privacy |
| “Full deep model on 10K cands” | Won’t meet p99 |
| “Prefetch full videos” | Cost / waste |

## Appendix E: Progressive narrative

**Baseline:** Pull mixer; fresh+ANN+trending; LTR; CDN; events; basic safety.  
**10×:** Session store; multi-stage; exo layers; cohort edge cache.  
**100×:** Cells; hybrid breaking push; bandits; safety platform; ANN freshness dual path.  
**1,000×:** Device re-rank; global midgress; lifecycle catalog; authority crisis modes.

## Appendix F: Following tab vs For You

```text
For You: pull multi-retriever + LTR (primary)
Following: merge latest from subscribed publishers (pull or light inbox push)
Shared: cluster store, media CDN, safety, event schema
Do not force one materialization for both
```

## Appendix G: Score sketch (illustrative)

```text
s = w_e * P(engage) + w_f * freshness + w_q * quality - w_b * clickbait
then re-rank with constraints (not pure sort by s)
```

## Appendix H: Cold-start decision tree

```text
if explicit_interests: seed affinities
else if geo/lang known: local trending + world head
else: global head + explore
always: safety filters
raise explore_rate until N engagements
```

## Appendix I: Breaking news sequence

```text
ingest T0 -> safety T0+30s -> fresh index T0+60s
optional: push cohort cache T0+90s
users GetFeed: fresh retriever returns item with boost
re-rank may force position ≤ 3 if authority high
```

## Appendix J: Interview math talking points

```text
Feed QPS × candidates × features ≈ why staging is mandatory
Video concurrent × bitrate ≈ CDN Tbps
Events/day ≈ log infra + sampling strategy
Hot catalog × embedding dim × replica ≈ memory money
```
