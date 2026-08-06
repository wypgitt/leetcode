# System Design: Uber Eats Home Feed

> **Focus areas:** Geo-scoped restaurant retrieval · Hybrid rank (offline + online) · Availability freshness · Personalization hooks · Pagination / infinite scroll · Promotions injection · Caching · A/B experimentation · Cell isolation  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct fan-out math; split **catalog** vs **availability** vs **ranking** planes; honest MVP vs ML-heavy path; no "SELECT * FROM restaurants" at scroll time  
> **Interview theme:** Uber Eats — personalized **home feed** of restaurant cards ranked for a user at a delivery address under freshness, business, and latency constraints

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
9. [Part II — LLD / Object Model](#part-ii--lld--object-model)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the feed**—the Eats home screen is *not* the full marketplace (cart, checkout, dispatch, merchant payments). It is the subsystem that, given a **user**, **delivery location**, and **context** (time, device), returns a **paginated, ranked list of restaurant cards** with accurate **open/busy/ETA** signals and optional **promo** slots—fast enough for infinite scroll at city scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Home feed ranking + retrieval + pagination | Full order placement / courier dispatch |
| Users | Consumer browsing Eats app/web | Restaurant partner dashboard (sibling) |
| Output | Ordered restaurant cards + metadata | Menu item search deep dive (related) |
| Personalization | Reorder history, favorites, cuisine prefs | Full ML recsys research platform |
| Scope | Feed read path + supporting indexes | Payouts, inventory ERP, kitchen KDS |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Feed content? | Restaurant cards (logo, name, rating, ETA, promos, tags) | Card schema + enrich pipeline |
| F2 | Geo scope? | Only restaurants **deliverable** to user's address | Delivery polygon / radius index |
| F3 | Ranking goal? | Relevance + ETA + quality + business rules | Scoring pipeline with caps |
| F4 | Personalization? | Past orders, favorites, dietary prefs light | Feature store / recents cache |
| F5 | Availability? | Open/closed, busy, pause, out-of-zone | Fresh availability plane |
| F6 | Promos? | Sponsored / promo slots with caps | Ad insertion layer |
| F7 | Pagination? | Cursor infinite scroll ~20 cards/page | Stable cursor + tie-break |
| F8 | Filters? | Cuisine, price, dietary, rating floor | Pre-filter or post-filter carefully |
| F9 | Freshness? | ETA and open status feel live | Short TTL caches; async updates |
| F10 | Guest vs auth? | Auth gets personalization; guest geo-only | Degraded rank path |
| F11 | Multi-tab? | "Pickup" vs "Delivery" modes | Mode-specific candidate sets |
| F12 | Experiments? | A/B rank models / promo density | Experiment flags on request |

**MVP functional scope (lock with interviewer):**

1. User sets **delivery address** (or uses GPS with reverse-geocode).  
2. Resolve **deliverable restaurant candidate set** for that point (geo index).  
3. Filter **closed / out-of-zone / hard-paused** merchants.  
4. **Rank** with weighted features: ETA, distance, rating, popularity, personal reorder boost.  
5. Return **page 1** (~20 cards) + **opaque cursor** for next page.  
6. Inject **limited promo slots** (e.g. 1–2 per page) with frequency caps.  
7. Enrich cards with **cached catalog metadata** (name, image URL, cuisines).  
8. Basic **auth personalization** (recent orders); guest fallback.

**Out of MVP (explicitly defer):**

- Full two-tower deep learning ranker training loop  
- Per-user precomputed infinite feed materialization at 100M DAU  
- Real-time menu item-level feed (that's search/browse sibling)  
- Cross-marketplace (rides + eats) unified feed  
- Perfect global active-active dual writers on rank state  
- Sub-10ms p99 at first request cold start worldwide without CDN

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Feed latency | Feels instant on open | p50 < 150ms, p99 < 400ms in-region (cached path) |
| N2 | Availability accuracy | Don't show closed as open | Open/busy wrong-rate < 0.5% (product-defined) |
| N3 | Pagination stability | Scroll doesn't duplicate/skip wildly | Stable sort key + cursor |
| N4 | Availability | Feed is revenue-critical | 99.9%+ success; degrade personalization first |
| N5 | Throughput | See scale table | Split **feed QPS** vs **availability updates** vs **index rebuild** |
| N6 | Fairness | Don't bury all organic for ads | Promo caps + auction rules |
| N7 | Privacy | Location scoped; no leak across users | No shared CDN cache keys with user id |
| N8 | Cost | Rank CPU bounded | Candidate cap K before heavy scoring |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Auth user opens app → address known → feed page 1 in <200ms → scroll page 2 via cursor.  
2. Guest user → geo-only rank → still valid deliverable set.  
3. User applies cuisine filter → narrowed set → re-ranked page 1.  
4. Restaurant goes **busy** mid-session → next page or refresh reflects busy badge.  
5. Promo slot wins auction → inserted at slot 3 without breaking organic order elsewhere.  
6. User with strong reorder history sees familiar restaurants boosted (not exclusively).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Address on zone boundary | Polygon test authoritative; snap to serviceable |
| Empty deliverable set | Empty state UX + expand radius suggestion (product) |
| Stale ETA cache | TTL + background refresh; show confidence or ranges |
| Hot city dinner peak | Candidate cap + cache; shed personalization |
| Rank service timeout | Fallback simpler rank (ETA + rating) |
| Cursor replay / tamper | Signed cursor or server-side session state |
| Duplicate restaurants (chains) | Dedupe policy by brand or show all—product call |
| Sponsored over-cap | Drop promo; log auction miss |
| User blocks restaurant | Filter from candidate set |
| Clock skew midnight | Open hours computed server-side local TZ |
| Index publish lag new restaurant | Nearline visibility SLO (minutes) |
| A/B experiment mismatch | Consistent bucket per user session |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 5M | 50M | 500M | 500M+ |
| Feed requests / day | 30M | 300M | 3B | 30B |
| Peak feed QPS | ~1K | ~10K | ~100K | ~1M |
| Restaurants per city | 5K | 15K | 40K | 80K |
| Deliverable candidates per request (pre-cap) | 200–800 | 300–1.5K | 500–2K | 500–3K |
| Scored candidates (post-cap K) | 150–300 | 200–400 | 200–500 | 200–500 |
| Availability events / s | ~500 | ~5K | ~50K | ~500K |
| Personalization feature lookups / s | ~1K | ~10K | ~100K | ~1M |
| Promo auctions / s | ~200 | ~2K | ~20K | ~200K |
| Pages per session avg | 2.5 | 3 | 3.5 | 4 |

**What each jump forces:**

- **10×:** Geo index sharded by city; feed API cache on `(cell, filter_hash)`; async availability bus.  
- **100×:** Two-stage retrieve→rank; regional cells; feature store; promo served separately; cursor session store.  
- **1,000×:** Hierarchical geo (city → micro-cell pools); learned rank with strict latency budget; edge cache anonymous shells; heavy candidate pruning.

### 1.5 Etc. (Constraints & Assumptions)

- **Catalog** (name, image, cuisines) changes slowly; **availability** changes fast.  
- Delivery eligibility is **polygon-based** (or radius MVP) per restaurant.  
- We do not compute full route ETA for every candidate at 100K QPS—use approximations + top-N refine.  
- Personalization improves conversion but must **degrade gracefully**.  
- Promo is **business-critical** but must not destroy trust (caps + labeling).

**Scope statement:**

> Design Uber Eats home feed: geo-deliverable candidate retrieval, fresh availability filtering, capped online ranking with personalization hooks, stable pagination, bounded promo injection—starting at ~30M feed requests/day and scaling 10× / 100× / 1,000× with city/cell isolation. Not checkout, dispatch, or merchant payouts.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Feed page requests | ~1K/s | ~1M/s | Read-heavy; cacheable shells |
| Geo candidate lookups | ~1K/s | ~1M/s | Index read |
| Rank scoring CPU | ~1K × K scores | ~1M × K | Bound K |
| Availability reads | ~1K/s | ~1M/s | Often merged in rank path |
| Availability writes | ~500/s | ~500K/s | Merchant/ops events |
| Personalization lookups | ~1K/s | ~1M/s | Optional cache |
| Promo auctions | ~200/s | ~200K/s | Separate service |
| Catalog cache hits | ~5K/s | ~5M/s | CDN + app cache |

### 2.2 Latency budget (p99 target ~400ms)

```text
Auth + address resolve     ~20ms
Geo candidate retrieval    ~30ms
Availability batch get     ~40ms
Personalization features   ~30ms (parallel)
Rank top-K                 ~80ms
Promo injection            ~20ms
Enrich + serialize         ~30ms
Buffer                     ~150ms
```

If ETA routing called for all 800 candidates → blows budget. **Cap + approximate ETA first.**

### 2.3 Storage (order of magnitude)

```text
Restaurants global: 1M × 2 KB metadata ≈ 2 GB (fits RAM/CDN)
Per-city geo index: 10K ids × 8 B ≈ 80 KB (tiny)
Availability hot: 1M × 64 B ≈ 64 MB
User recents: 50M users × 200 B ≈ 10 GB (KV, TTL)
Feed cursor session: peak 500K sessions × 500 B ≈ 250 MB
```

### 2.4 Bandwidth

```text
Feed response ~20 cards × 1 KB ≈ 20 KB
1K QPS × 20 KB ≈ 20 MB/s baseline
1M QPS × 20 KB ≈ 20 GB/s → CDN + edge + pagination
```

### 2.5 Bottlenecks (rank ordered)

1. **Unbounded candidate set** before rank  
2. **Per-candidate routing ETA** at scale  
3. **Hot city** cache stampede at dinner  
4. **Personalization dependency** on critical path  
5. **Promo latency** blocking organic  
6. **Unstable sort** breaking pagination  
7. **Mixing catalog + availability** in one stale cache  

---

## 3. High-Level Design

### 3.1 Planes (separate concerns)

| Plane | SoT | Freshness | Scale pattern |
|-------|-----|-----------|---------------|
| Catalog | Restaurant profile DB | Minutes–hours | CDN + regional cache |
| Delivery geo | Polygon index per restaurant | Hours | Spatial index read |
| Availability | Merchant status service | Seconds | KV + pub/sub |
| ETA / distance | Routing + heuristics | Seconds–minutes | Approx + refine top-N |
| Ranking | Online scorer + weights | Per request | CPU horizontal |
| Personalization | Feature store / recents | Minutes | Cache + async |
| Promo / ads | Campaign service | Seconds | Auction + caps |
| Feed session | Cursor state | Session | KV optional |

**Deal-breaker:** One Postgres join across all restaurants per scroll at peak QPS.

### 3.2 Request path (MVP)

```text
GET /v1/feed?lat&lng&cursor&filters
  → resolve delivery point + city_cell
  → candidate_ids = GeoIndex.deliverable(point, city)
  → avail = Availability.batchGet(candidate_ids) → filter closed/paused
  → feats = Personalization.get(user_id) [timeout → {}]
  → scored = Ranker.score(filtered, feats, context) → top page_size
  → promos = Promo.select(user, point, page_context) → insert slots
  → cards = Catalog.enrich(scored + promos)
  → cursor = Cursor.next(scored, stable_key)
  → return FeedPage(cards, cursor)
```

### 3.3 Geo deliverability options

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Haversine radius per store | Simple | Wrong across rivers/zones | Dense cities with complex zones |
| B. Point-in-polygon index | Accurate | Index build cost | — preferred at scale |
| C. H3 cell prefilter + polygon refine | Fast | Two-step | — hybrid |
| D. Precompute "restaurants for tile" | Fast read | Stale when zones change | Frequent zone edits |

**Chosen path:**

- **MVP:** City shard + radius or simplified polygon.  
- **100×+:** H3 cover of delivery zones inverted index `cell → restaurant_ids` + precise polygon check on candidate subset.

### 3.4 Ranking architecture options

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. SQL ORDER BY distance | Easy | Slow at scale | 100K QPS |
| B. Precomputed feed per user | Fast read | Stale; write amp | 50M DAU |
| C. Retrieve → cap K → online score | Flexible | CPU | — preferred |
| D. Full LTR on all candidates | Best quality | Latency/cost | Without cap K |

**Two-stage retrieve + rank:**

1. **Retrieval:** geo index + hard filters → up to M candidates (M ~ 500–2000).  
2. **Prune:** cheap score (distance, open, popularity) → top K (150–300).  
3. **Refine:** ETA routing on top K only (optional async refresh).  
4. **Personalize:** boost/ demote with feature weights.  
5. **Stable sort key:** `(score desc, restaurant_id asc)` for pagination.

### 3.5 Availability model

```text
status ∈ {OPEN, CLOSED, BUSY, PAUSED}
busy_until?, pause_reason?, updated_at
source: merchant tablet, hours schedule, ops override, ML prep-time signal (later)
```

Read path: batch MGET from Redis/similar; write path: merchant events → bus → KV.

**Invariant:** Feed must not show CLOSED as OPEN—prefer false CLOSED over false OPEN if uncertain.

### 3.6 Promo injection

```text
Separate promo candidates eligible for geo/user
Auction / pacing selects 0..S slots per page
Insert at fixed positions (e.g. 2, 7) with "Sponsored" label
Organic ranks unchanged outside slots; dedupe if promo already in organic
```

### 3.7 Pagination / cursor

```text
Stable ordering for session:
  sort_key = f(features)  // deterministic given same inputs
cursor encodes: (last_score, last_restaurant_id, filter_hash, session_seed, exp_bucket)
Next page: fetch candidates, score same way, return items after cursor tuple
```

**Alternative at scale:** server-side **feed session** stores ranked id list snapshot for 5–15 min (memory cost) — trade RAM for stable scroll under changing scores.

### 3.8 Caching strategy

| Cache key | TTL | Notes |
|-----------|-----|-------|
| `(city, h3, filter_hash)` anonymous shell | 30–60s | No user id in shared key |
| User personalization overlay | 5–15 min | Private |
| Catalog card | 5–30 min | CDN |
| Availability | 5–30s | Short |
| ETA matrix cell-pair | 1–5 min | Approx |

**Deal-breaker:** Public CDN cache of personalized feed.

### 3.9 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Cap K before rank | Quality vs latency |
| Approx ETA | Speed vs accuracy |
| Session cursor store | RAM vs stable scroll |
| Promo on critical path | Revenue vs latency (async prefer) |
| Guest no personalization | Privacy/simplicity vs conversion |
| Cell isolation | Ops complexity vs blast radius |

### 3.10 Components

1. Feed API gateway  
2. Address / geocode service  
3. Geo deliverability index  
4. Catalog service + CDN  
5. Availability service  
6. ETA / routing adapter  
7. Ranker (online)  
8. Personalization / feature store  
9. Promo / ads service  
10. Feed session / cursor store  
11. Experiment assignment  
12. Observability + rank logging for training  

---

## 4. Architecture Diagram

```text
                    +------------------+
                    |   Eats Client    |
                    +--------+---------+
                             |
                             v
                    +--------+---------+
                    |   Feed API GW    |
                    +--------+---------+
                             |
     +-----------+-----------+-----------+-----------+
     |           |           |           |           |
     v           v           v           v           v
 GeoIndex   Availability  Personalization Ranker    Promo
     |           |           |           |           |
     +-----------+-----------+-----------+-----------+
                             |
                             v
                      Catalog Enricher
                             |
                             v
                      FeedPage + Cursor
```

### 4.1 City cell topology

```text
Global Edge (active-active)
        |
        v
City Cell (home for geo index shard + rank config)
  - Deliverability index
  - Local availability cache replica
  - Rank worker pool
        |
        +--> fail independently; degrade to simpler rank
```

### 4.2 Sequence: page 1

```text
Client -> FeedAPI: GET /feed (lat,lng,user)
FeedAPI -> GeoIndex: candidates(point) -> ids[M]
FeedAPI -> Availability: batch(ids) -> open subset
FeedAPI -> Personalization: features(user) [parallel]
FeedAPI -> Ranker: score(subset, features) -> ordered[K]
FeedAPI -> Promo: slots(user, point, page=1)
FeedAPI -> Catalog: enrich(card_ids)
FeedAPI -> Client: cards + cursor
```

### 4.3 Sequence: merchant closes

```text
Merchant app -> Availability: CLOSED
Availability -> Kafka -> KV update + pub/sub
FeedAPI next request: batch get sees CLOSED -> filtered
(Optional) push "refresh feed" to active clients — usually skip; TTL enough
```

### 4.4 Sequence: pagination page 2

```text
Client -> FeedAPI: GET /feed?cursor=...
If session store enabled:
  FeedAPI -> SessionKV: get ranked snapshot -> slice page 2
Else:
  Recompute candidates + rank with same session_seed + skip past cursor tuple
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Deliverability authoritative** on geo index + polygon test.  
2. **Closed restaurants excluded** even if rank score high.  
3. **Cursor tamper resistance** — signed or server session.  
4. **Promo labeled** and capped per page/session.  
5. **Personalization timeout → fallback** rank without failing feed.  
6. **Rank weights versioned** (`rank_v3`) for replay/debug.  
7. **Idempotent feed session create** on refresh spam.  
8. **Block list enforced** before rank.  
9. **Experiment bucket sticky** per session.  
10. **No PII in shared edge cache keys**.

### 5.2 Scalability

| Scale | Architecture moves |
|-------|--------------------|
| 1× | Monolith OK; Redis geo; simple weighted rank |
| 10× | City shards; batch availability; CDN catalog |
| 100× | Two-stage retrieve/rank; session cursors; promo async |
| 1000× | Micro-cell pools; approximate ETA tables; edge anonymous shell + private overlay |

### 5.3 Maintainability

- Rank weights in config service with canary.  
- Offline replay logs → training data for LTR Phase 2.  
- Golden feed fixtures per city for regression.  
- Clear ownership: catalog vs availability vs rank.  
- Shadow rank: log alt order without serving.

### 5.4 Progressive scale playbook

**Baseline (1×):** Single region; 5K restaurants/city; M=500, K=150; weighted linear rank; 60s city cache.

**10×:**  
- Shard geo index by `city_id`.  
- Personalization KV with 15ms timeout.  
- Promo service isolated thread pool.

**100×:**  
- H3 inverted deliverability index.  
- Feed session store for stable pagination.  
- Rank fleet autoscale on CPU.  
- Dinner peak: raise cache TTL slightly + shed shadow features.

**1,000×:**  
- Edge serve **anonymous shell** (popular near cell) + client-side merge private boosts (careful privacy).  
- Or: precompute **cell-level candidate pools** every 1–5 min; online only rerank top layers.  
- Strict K cap; learned rank on GPU batch if needed.

### 5.5 ETA without melting routing

```text
Stage 1: haversine or static road-graph distance table per H3 pair
Stage 2: routing API only for top 20 after cheap score
Stage 3: display cached ETA with "updated Xm ago" internally
```

### 5.6 Personalization features (MVP)

| Feature | Source | Freshness |
|---------|--------|-----------|
| Recent order restaurant ids | Orders service | Hours |
| Favorites | User profile | Minutes |
| Cuisine affinities | Aggregated history | Daily |
| Time-of-day prior | Config / simple | Static |

**Never block feed on slow ML embedding service.**

### 5.7 Filters interaction

```text
Hard filters (cuisine, price): apply before rank on candidate set
If result empty: relax filters with UX message (product)
Soft filters: demote in score rather than exclude
```

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Rank all restaurants in DB | p99 seconds |
| Route ETA for 2000 candidates | Routing bill + latency |
| Personalized CDN cache | Privacy + wrong cards |
| Unstable sort (random tie-break) | Scroll duplicates |
| Promo replaces entire page | Trust loss |
| Single global Redis GEO for earth | Hot key + RTT |
| Ignore busy/closed | Bad orders + refunds |

### 5.9 Failure modes & degradations

| Failure | Degrade |
|---------|---------|
| Personalization down | Skip boosts |
| Promo down | Organic only |
| Routing down | Haversine ETA |
| Geo index stale | Slightly smaller set; alert |
| Rank CPU high | Lower K; simpler weights |
| Availability KV lag | Shorter open confidence; prefer CLOSED |

### 5.10 Multi-region

- **Catalog:** replicated read.  
- **Geo index:** city home region.  
- **Feed request:** route to city home cell by delivery point.  
- **Availability:** regional KV with async cross-region for chains (eventual).

---

## 6. Wrap-Up

### 6.1 Designed

Uber Eats home feed with geo deliverability retrieval, fast availability filtering, capped two-stage ranking with personalization hooks, stable pagination, bounded promo injection, city-cell caching, and graceful degradation under peak.

### 6.2 Decisions to defend

1. Split **catalog / availability / geo / rank** planes  
2. **Candidate cap K** before heavy scoring  
3. **Approx ETA + refine top-N**  
4. **Stable sort + cursor** (or session snapshot at scale)  
5. **Promo caps** and async when possible  
6. **Personalization fail-open**  
7. **City cell** isolation  

### 6.3 Risks

- Zone boundary errors  
- ETA inaccuracy at peak  
- Promo trust / regulatory labeling  
- Rank feedback loops (popular gets more popular)  
- Cold-start new restaurants  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope feed vs full Eats |
| 5–12 | Estimates: QPS, K cap, latency budget |
| 12–25 | Geo retrieval + availability |
| 25–35 | Rank + pagination + promo |
| 35–45 | Scale 10×/100×/1000×, deal-breakers |

### 6.5 Closer

> **Eats feed:** deliverable geo candidates, fresh availability filter, capped online rank with personalization timeout fallback, stable pagination, promo slots with caps—scale by city cells and never route-ETA the whole city on every scroll.

---

## 7. Deeper / Related Interview Questions

### 7.1 Geo & deliverability

**Q: Radius vs polygon?**  
A: Radius MVP; polygon production; H3 inverted index for fast prefilter.

**Q: User across river?**  
A: Polygon excludes undeliverable though distance small.

**Q: Pickup vs delivery feed?**  
A: Different candidate sets and rank weights (ETA less critical pickup).

### 7.2 Ranking

**Q: How avoid popularity bias?**  
A: Explore/exploit slots; cap repeat exposure; new merchant boost window.

**Q: Learning-to-rank?**  
A: Log features + clicks/orders; train offline; serve weighted linear then GBDT/DNN with latency guard.

**Q: Real-time trend (viral restaurant)?**  
A: Short-window demand signal in score; separate from slow popularity prior.

### 7.3 Pagination

**Q: Scores change while scrolling?**  
A: Session snapshot or deterministic seed; accept slight staleness.

**Q: Infinite scroll forever?**  
A: Cursor TTL; max pages; tail is low value.

### 7.4 Caching

**Q: Cache personalized feed?**  
A: Only private per-user short TTL; shared cache for anonymous geo shells.

**Q: Thundering herd new city launch?**  
A: Warm cache; stagger marketing; prebuild geo index.

### 7.5 Promo / ads

**Q: Quality vs revenue?**  
A: Relevance threshold on promo; hide irrelevant ads.

**Q: Frequency cap?**  
A: Per user per day per campaign in promo service.

### 7.6 Availability

**Q: Scheduled hours vs manual close?**  
A: Union logic; manual override wins.

**Q: Busy vs closed?**  
A: Busy may throttle orders; still show with badge (product).

### 7.7 Comparison to siblings

**Q: vs restaurant metrics dashboard?**  
A: Metrics = stream aggregates for partners; feed = consumer retrieval/rank.

**Q: vs travel-query suggest?**  
A: Suggest = prefix retrieval; feed = ranked full cards with geo eligibility.

**Q: vs YouTube feed?**  
A: Eats feed is **geo-hard-constrained**; YouTube is global interest graph.

### 7.8 Interview traps

| Trap | Pushback |
|------|----------|
| Precompute entire feed per user nightly | Stale; write cost |
| One Elasticsearch for everything | Wrong tool for avail freshness |
| Ignore promo ethics | Label sponsored |
| SQL JOIN on scroll | Latency |
| No empty-state story | Bad UX in suburbs |

### 7.9 Metrics

| Metric | Why |
|--------|-----|
| Feed p50/p99 latency | SLO |
| Empty feed rate | Geo coverage |
| Open/closed error rate | Trust |
| CTR / order conversion | Rank quality |
| Promo fill rate | Revenue |
| Personalization timeout rate | Dependency health |
| Cache hit rate | Cost |
| Scroll depth | Engagement |

---

## 8. Appendices

### 8.1 API sketch

```text
GET /v1/eats/feed
  ?lat=37.77&lng=-122.42
  &mode=delivery
  &cursor=...
  &cuisine=thai,japanese
  &price_tier=1,2
  &limit=20
  &session_id=...

Response:
{
  "cards": [
    {
      "restaurant_id": "r_123",
      "name": "...",
      "rating": 4.7,
      "eta_min": 25,
      "distance_km": 1.2,
      "badges": ["BUSY"],
      "promo": {"text": "$0 delivery", "sponsored": false},
      "image_url": "https://..."
    }
  ],
  "cursor": "opaque...",
  "rank_version": "v3",
  "as_of": "2026-08-06T12:00:00Z"
}
```

### 8.2 Rank feature vector (debug)

```text
distance_score, eta_score, rating_score, popularity_score,
personal_reorder_boost, cuisine_match, promo_quality, new_restaurant_boost,
time_of_day_prior, exp_bucket
```

### 8.3 Schema sketches

```sql
-- restaurants (catalog)
(restaurant_id PK, city_id, name, cuisines[], price_tier,
 image_url, rating_agg, brand_id, ...)

-- delivery_zones (geo)
(restaurant_id, zone_geojson OR h3_cells[], updated_at)

-- availability (hot KV)
restaurant_id -> {status, busy_until, updated_at, source}

-- feed_sessions (optional)
(session_id, user_id, ranked_ids[], created_at, exp, filter_hash)
```

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Candidate set | Deliverable restaurants pre-rank |
| K cap | Max scored items |
| Shell cache | Anonymous geo feed template |
| Stable tie-break | restaurant_id ascending |
| Sponsored slot | Paid placement with label |
| Cell | City/micro-cell shard unit |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Geo filter, avail batch, weighted rank, cursor |
| 10× | City shard, catalog CDN, promo service |
| 100× | H3 index, session pagination, rank fleet |
| 1000× | Cell pools, approx ETA tables, edge shells |

### 8.6 Rank pseudocode

```text
function rankFeed(user, point, filters):
  ids = geo.deliverable(point, city, filters)
  ids = filter availability.open(ids)
  if ids.empty: return empty
  cheap = [(id, cheapScore(id, point)) for id in ids]
  topK = takeK(cheap, K)
  for id in topK: topK[id].eta = etaRefine(id, point)  // routing optional
  feats = personalization.get(user, timeout=15ms) or {}
  scored = [(id, finalScore(topK[id], feats)) for id in topK]
  sort stable by score desc, id asc
  return scored
```

### 8.7 Interview "say this" (60s)

> Resolve deliverable restaurants via geo index; batch-get availability and drop closed; cap to K candidates; score with distance, ETA, rating, popularity, and optional personalization with timeout fallback; inject capped labeled promos; return stable cursor pagination; cache anonymous city shells—not per-user on CDN; scale by city cells and two-stage retrieve/rank.

### 8.8 Reliability tests

1. Closed merchant never appears.  
2. Boundary address respects polygon.  
3. Page 2 no duplicates from page 1.  
4. Personalization timeout → 200 organic feed.  
5. Promo cap not exceeded.  
6. Blocked restaurant excluded.

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Feed p99 in-region | < 400ms |
| Availability wrong-open | < 0.5% |
| Empty feed (servicable areas) | < 1% |
| Promo label presence | 100% sponsored |

### 8.10 Related systems map

```text
Catalog DB --> CDN
Merchant Ops --> Availability --> Feed API
Orders History --> Personalization --> Feed API
Geo Zones --> GeoIndex --> Feed API
Campaigns --> Promo --> Feed API
Feed API --> Client infinite scroll
```

### 8.11 Cold-start restaurant

```text
Boost new ids modestly; explore slot rotation; avoid permanent bury
Index publish pipeline visible within minutes SLO
```

### 8.12 Observability

- Log rank features for 1–5% sample (privacy scrubbed).  
- Trace spans: geo, avail, rank, promo.  
- Dashboard: p99 by city, empty rate, cache hit.

---

## Part II — LLD / Object Model

### 9.1 Responsibilities

| Class / Service | Owns |
|-----------------|------|
| `FeedController` | HTTP API, auth, experiment bucket, orchestration |
| `DeliveryPoint` | Lat/lng, city_cell, normalized address |
| `GeoDeliverabilityIndex` | Restaurant ids serviceable at point |
| `AvailabilityClient` | Batch status lookup |
| `CatalogClient` | Card metadata enrichment |
| `PersonalizationProvider` | User features with timeout |
| `FeedRanker` | Scoring + stable sort |
| `PromoSelector` | Sponsored slot insertion |
| `FeedPage` | Cards + cursor response DTO |
| `FeedSessionStore` | Optional ranked snapshot for pagination |
| `CursorCodec` | Encode/decode pagination state |

### 9.2 Class diagram (ASCII)

```text
FeedController
  --> GeoDeliverabilityIndex
  --> AvailabilityClient
  --> PersonalizationProvider
  --> FeedRanker
  --> PromoSelector
  --> CatalogClient
  --> FeedSessionStore
  --> CursorCodec

FeedRanker --> ScoringStrategy (interface)
           --> EtaProvider (interface)

PromoSelector --> PromoAuctionClient
```

### 9.3 Core interfaces

```text
interface GeoDeliverabilityIndex {
  List<RestaurantId> deliverable(DeliveryPoint p, FilterSet f);
}

interface FeedRanker {
  RankedList rank(List<RestaurantId> ids, UserContext u, DeliveryPoint p);
}

interface ScoringStrategy {
  double score(RankContext ctx);
}

class RankContext {
  RestaurantId id;
  double distanceKm;
  Duration eta;
  double rating;
  double popularity;
  PersonalizationFeatures pf;
  Instant localTime;
}
```

### 9.4 Feed assembly (orchestration)

```text
class FeedService {
  FeedPage getFeed(FeedRequest req):
    point = resolvePoint(req)
    session = sessionStore.getOrCreate(req.sessionId)
    if req.cursor != null && session.hasSnapshot():
      return session.slice(req.cursor, req.limit)
    ids = geo.deliverable(point, req.filters)
    ids = availability.filterOpen(ids)
    ranked = ranker.rank(ids, req.user, point)
    ranked = promo.insertSlots(ranked, req.user, point, req.pageIndex)
    cards = catalog.enrich(ranked.ids())
    cursor = cursorCodec.next(ranked, req)
    sessionStore.saveSnapshot(session, ranked)  // optional
    return new FeedPage(cards, cursor)
}
```

### 9.5 Stable ordering

```text
class RankedRestaurant implements Comparable {
  double score;
  RestaurantId id;

  compareTo(other):
    if score != other.score: return desc(score, other.score)
    return asc(id, other.id)  // deterministic tie-break
}
```

### 9.6 Promo insertion

```text
class PromoSelector {
  List<RankedRestaurant> insertSlots(list, promos, slotPositions):
    result = copy(list)
    for pos in slotPositions:
      if promos.empty(): break
      p = promos.nextEligible(notIn(result))
      result.insertAt(pos, p.withSponsoredLabel())
    return result
}
```

### 9.7 Concurrency

- Feed request handlers stateless; horizontal scale.  
- `FeedSessionStore` keyed by `session_id` with TTL; CAS on snapshot version.  
- Ranker pure function given inputs → easy parallel per partition in batch jobs; online per request.

### 9.8 Extensibility

- `ScoringStrategy` per experiment bucket.  
- `FilterPipeline` chain for new dietary rules.  
- `CardEnricher` plugins (badges, loyalty).  
- `DeliverabilityPolicy` per market (alcohol, distance limits).

### 9.9 Testing

| Test | Assert |
|------|--------|
| Closed filtered | Never in ranked list |
| Stable sort | Same inputs → same order |
| Promo dedupe | Not twice in page |
| Personalization timeout | Feed succeeds |
| Cursor roundtrip | Page 2 contiguous |

### 9.10 Interview LLD closer

> Keep `FeedController` thin; pure ranker with strategy injection; geo and availability as ports; pagination either deterministic cursor or session snapshot—objects map cleanly to the HLD planes without a monolithic FeedGod class.

---

*End of Uber Eats home feed system design.*
