# System Design: CamelCamelCamel-style Price Tracker

> **Focus areas:** Product catalog · Price crawl/ingest · Time-series price history · Alerts · Idempotent updates · Fair scraping  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct write amplification math, split crawl vs query planes, deal-breakers for “poll Amazon on every page view”  
> **Interview theme:** Meta-adjacent marketplace data systems — track third-party e-commerce prices, chart history, notify users on drops

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

Goal: **bound the product**—a **CamelCamelCamel-like** service that tracks e-commerce product prices over time, shows history charts, and alerts users when prices drop below thresholds.

### 1.0 What this is / is not

| Dimension | **Price tracker (this doc)** | Not this |
|-----------|------------------------------|----------|
| Primary job | Track prices + alert on drops | Full retailer checkout / payments |
| Data plane | Crawl/ingest + time-series + alerts | Social graph |
| Success | Accurate history, timely alerts | Sub-ms trading HFT |
| Write path | Periodic price observations | User-generated feed |
| Read path | Product page + chart + watchlist | Arbitrary retailer search engine |

**Scope statement:** Design a price-tracking product: product identity, price ingestion (APIs/crawl), historical store, watchlists, alert delivery, progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Which retailers? | Amazon MVP; more later | Adapter per source |
| F2 | Product identity? | ASIN / SKU + marketplace | Canonical `product_id` |
| F3 | Price types? | List, Amazon, 3rd-party new/used; buy-box | Multiple series per product |
| F4 | History? | Months–years of points | Time-series DB / cold storage |
| F5 | Alerts? | Price ≤ threshold; % drop; availability | Alert engine + notify |
| F6 | Chart UX? | 1w/1m/1y/all aggregations | Rollups for long ranges |
| F7 | User accounts? | Watchlists; email/push | User service + prefs |
| F8 | Ingest method? | Official APIs if available + crawl fallback | Politeness / proxies |
| F9 | Localization? | Marketplace (.com, .co.uk) | Separate product keys |
| F10 | Coupons / Lightning? | Best-effort Phase 1.5 | Event types |
| F11 | Browser extension? | Optional Phase 1.5 | Same APIs |
| F12 | Admin? | Force refresh; ban ASIN | Control plane |

**MVP functional scope:**

1. Resolve product by URL/ASIN; create tracked product.  
2. Periodically ingest prices for tracked + popular catalog.  
3. Store price observations; serve charts with rollups.  
4. Users create watchlist alerts with thresholds.  
5. On drop, deliver email/push (at-least-once, deduped).  
6. Show current price, min/avg, last updated.  
7. Respect crawl budgets / API quotas.

**Out of MVP:**

- Purchasing / affiliate checkout complexity deep dive (mention affiliate links)  
- Perfect lightning-deal capture at second granularity  
- Full multi-retailer normalization ontology  
- Price prediction ML (Phase 2)  
- Guaranteed alert within 1 second of retailer change

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Alert latency | “Soon after we see drop” | p95 < 5–15 min from observation |
| N2 | Chart latency | Interactive | p99 < 200–300ms |
| N3 | Freshness popular | Hot products | Poll every 1–5 min |
| N4 | Freshness long-tail | Watched | Poll every 1–6 h adaptive |
| N5 | Durability history | Don’t lose series | Multi-AZ TS store + backups |
| N6 | Crawl compliance | Don’t get banned | Quotas, backoff, robots/ToS posture |
| N7 | Availability | Read mostly | 99.9% charts; delayed alerts OK briefly |
| N8 | Correctness | No false alert spam | Dedup + confirmation optional |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User pastes Amazon URL → resolve ASIN → see history (if known) → set alert $X.  
2. Crawler observes price 80 → 70 → alert fired → email.  
3. User opens 1y chart → weekly rollups returned fast.  
4. Popular product auto-tracked without user.  
5. Price goes up — no alert (unless availability alert).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| ASIN delisted | Mark unavailable; alert optional |
| Price scrape parse fail | Retry; keep last_good; stale badge |
| Flash spike glitch (price $1 error) | Outlier detection; confirm next poll |
| Duplicate alerts | Dedupe key `(alert_id, price_version)` |
| User deletes alert mid-send | Best-effort cancel; idempotent |
| API quota exhausted | Prioritize watchlist products |
| Marketplace mismatch | Don’t merge .com and .de ASINs blindly |
| Currency | Store currency; don’t compare cross-currency |
| Variant products (size/color) | Track parent/child explicitly |
| Clock skew observations | Server ingest time + source ts |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tracked products | 5M | 50M | 500M | 5B |
| Active alerts | 20M | 200M | 2B | 20B |
| DAU | 1M | 10M | 100M | 1B |
| Price observations/s | 20K | 200K | 2M | 20M |
| Chart QPS | 5K | 50K | 500K | 5M |
| Alert evaluations/s | 20K | 200K | 2M | 20M |
| Notifications/s (peak) | 500 | 5K | 50K | 500K |
| Retailers | 1–2 | 5 | 20 | 50+ |
| History retention | 3–5 y | 5 y | tiered | tiered |

**What each jump forces:**

- **10×:** Adaptive poll scheduler; rollups; sharded TS; alert indexing by product.  
- **100×:** Regional crawl cells; tiered storage (hot TS + cold parquet); notification microservices.  
- **1,000×:** Hierarchical catalogs; per-retailer platforms; streaming alert evaluation; aggressive rollup/downsample.

### 1.5 Etc. (Constraints & Assumptions)

- We may not get perfect official firehose — design for **pull ingest** with adapters.  
- Legal/ToS constraints exist — discuss rate limiting & preferred APIs without pretending to bypass protections.  
- Affiliate revenue is business context; architecture still stands without it.  
- Charts are read-heavy; crawls are write-heavy but schedulable.

**Scope statement to repeat back:**

> Design a CamelCamelCamel-style price tracker: product identity across marketplaces, adaptive price ingestion with polite quotas, durable time-series history with rollups, user watchlists/alerts, and reliable notification—scaling through 10× / 100× / 1,000× via scheduler prioritization, sharded time-series, and alert evaluation colocated with price updates (not per-page polls).

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Crawl/API fetch** | Outbound polls | ~20K obs/s | Fetcher fleet |
| **TS writes** | Price points | ~20K/s | Time-series |
| **Chart reads** | Aggregated series | ~5K/s | Query + cache |
| **Alert eval** | On new observation | ~20K/s | Stream workers |
| **Notify send** | Email/push | spiky | Notification svc |
| **Product page** | Metadata + current | ~5–10K/s | API + cache |

**Anti-pattern:** hitting retailer on every user chart view.

### 2.2 Scheduler math

```text
5M products naive poll every 5 min = 5M / 300 ≈ 16.7K polls/s
Too flat — must prioritize:
  - watchlisted / alerted products: fast
  - popular: medium
  - cold never-watched: slow or on-demand
Adaptive scheduler reduces useless polls dramatically
```

### 2.3 Storage math

```text
5M products × 1 point / hour × 24 × 365 × 5y ≈ 2.2e11 points
If 20B raw points × 16 bytes ≈ 3.5 TB raw (order; often more with indexes)
With multiple price types ×3 → ×3
Rollups: keep raw 90d hot; hourly/daily cold forever
```

### 2.4 Alert amplification

```text
Naive: every observation scan all 20M alerts → impossible
Correct: index alerts by product_id; on observation, load alerts for that product only
Avg alerts/product skewed — cap / shard hot products (iPhone)
```

### Q2.5 Chart aggregation

```text
1y chart at raw 5-min resolution = ~100K points — too many for browser
Server returns ~200–500 buckets (e.g. daily min/avg/max)
Precompute rollups or downsample on read with caching
```

### 2.6 Notification spikes

```text
Holiday sale: 1% of alerts fire in 10 min
20M alerts × 1% / 600s ≈ 333 notifies/s average; peaks higher
Need queue + rate-limited providers + digest options
```

### 2.7 Polite crawl / API budget math

```text
Retailer quota: e.g. 10 QPS sustained / key, burst 20
With 50 keys / proxy pool: 500–1000 QPS fetch capacity
Scheduler must never exceed: Σ assigned_due ≤ capacity × safety(0.7)
Backoff on 429: multiply interval ×2–5; circuit-break retailer cell

Robots / politeness:
  per-host concurrent ≤ 2–8
  min spacing 100–500ms (crawl) 
  honor Retry-After
API preferred: predictable quotas; crawl is backup with higher fragility cost
```

### 2.8 TSDB write/read amplification

```text
20K obs/s × 50B ≈ 1 MB/s raw — easy
Compaction + indexes ×3–10 storage amp
Chart read 5K/s × 300 buckets × 16B ≈ 24 MB/s — cache rollups by (product, range, grain)
Change-detection skip (raw_hash unchanged): can drop 60–90% of writes on stable ASINs
```

### 2.9 False-alert cost model

```text
If 0.1% of observations are parse glitches and each triggers email:
  20K/s × 0.001 = 20 false alerts/s → user trust collapse
Controls: outlier gates, M-of-N confirm, re-arm hysteresis, price_type match
Target: false alert rate ≪ 0.01% of notifications sent
```

### 2.10 Progressive capacity table

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Products tracked | 5M | 50M | 500M | multi-retailer fabric |
| Fetch QPS | 20K | adaptive | sharded crawl cells | per-retailer platforms |
| TS points/day | billions | ×10 | cold tier | hierarchical catalog |
| Alerts | 20M | 200M | eval stream | partitioned evaluators |
| Notify peak | hundreds/s | ×10 | digest + provider mesh | regional notify |

**Anti-patterns:** scrape-on-pageview; scan all alerts every minute; send 100K-point charts; alert on single glitch price.

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/products/resolve` | URL/ASIN → product |
| `GET /v1/products/{id}` | Metadata + current prices |
| `GET /v1/products/{id}/history?range=&type=` | Chart points/buckets |
| `POST /v1/alerts` | Create threshold alert |
| `GET /v1/alerts` | User watchlist |
| `DELETE /v1/alerts/{id}` | Remove |
| `POST /admin/refresh/{id}` | Priority poll |
| `GET /v1/products/{id}/stats` | Min/avg/median |

### 3.2 Data model

| Entity | Key | Store |
|--------|-----|-------|
| Product | `product_id` (marketplace+ASIN) | SQL / KV |
| Price observation | `(product_id, price_type, ts)` | TS DB |
| Rollup | `(product_id, price_type, grain, bucket)` | TS / SQL |
| Alert | `alert_id`; GSI `product_id` | SQL |
| User | `user_id` | SQL |
| Fetch task | `product_id` + priority | Scheduler queues |
| Notification outbox | `idempotency_key` | SQL / Kafka |

**Observation:**

```text
PriceObs {
  product_id,
  price_type: AMAZON|LIST|THIRD_NEW|THIRD_USED|BUY_BOX,
  price_cents,
  currency,
  available: bool,
  source: API|CRAWL,
  ts_source,
  ts_ingest,
  raw_hash  // change detection
}
```

### 3.3 Ingest adapters — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Official API** | Stable schema | Quotas, cost, gaps | Prefer always |
| **Scheduled crawl** | Coverage | Fragility, ToS | Fallback |
| **User-extension crowdsource** | Fresh | Bias, abuse | Phase 1.5 augment |
| **Retailer webhook** | Push ideal | Rarely offered | Take if exists |
| **Scrape on pageview** | Simple | **Ban + latency** | Deal-breaker |

**Chosen:** Scheduler-driven fetch via retailer adapters; never inline scrape on user request (except optional explicit “refresh” with rate limit).

### 3.4 Alert evaluation — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Cron scan all alerts | Simple | Doesn’t scale | Tiny only |
| Eval on observation | Perfect fit | Need product→alerts index | **MVP** |
| Complex CEP engine | Powerful | Overkill | Multi-condition Phase 2 |

**Alert fire rule (MVP):**

```text
if obs.price_cents <= alert.threshold_cents
   and obs.price_type matches
   and available
   and not already_notified_for_this_valley:
     enqueue notification
```

Dedup: don’t email every poll while price stays below threshold — use state `armed|triggered` re-arm when price rises above threshold+margin.

### 3.5 History storage — Why X over Y

| Store | Pros | Cons | Use |
|-------|------|------|-----|
| Postgres alone | Simple | Series blowup | Metadata + short history |
| Purpose TS (Timestream/Victoria/Cassandra) | Write scale | Ops | **Hot raw** |
| Cold Parquet on S3 | Cheap | Higher read latency | Old raw / analytics |
| Redis | Fast | Not durable history | Current price cache |

**Chosen:** Hot TS for recent raw + continuous rollup jobs; cache current price in Redis; product metadata in SQL.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| When to fetch | Adaptive scheduler | Quotas | Scrape per view |
| Alert eval | On write by product | Fanout | Nightly full scan |
| Chart long range | Rollups | Payload | 100K raw points to client |
| Glitch prices | Outlier + confirm | Trust | Alert on single $0.01 parse error |
| Multi-market | Separate product_ids | Correctness | Merge all ASINs globally |

### 3.7 Politeness & legal posture (interview)

| Topic | Stance |
|-------|--------|
| ToS / robots | Prefer official APIs; crawl only where allowed; rate-limit hard |
| User “refresh” | Coalesced, rate-limited, never unbounded scrape-on-F5 |
| Attribution | Show source marketplace + `last_checked_at` |
| PII | Alerts are user data — encrypt, access-control, export/delete |

**Deal-breaker:** designing a botnet of scrapers as the core architecture story.

### 3.8 Alert state machine (HLD)

```text
ARMED  --(price <= threshold, pass gates)--> TRIGGERED (enqueue notify)
TRIGGERED --(price >= threshold + margin)--> ARMED
TRIGGERED --(still below)--> stay (no repeat spam)
DISABLED -- user pause / invalid product
```

---

## 4. Architecture Diagram

```text
  User App / Web
       |
       | resolve, charts, alerts
       v
 +-----+------+         +----------------+
 | Public API |-------->| Product + User |
 |            |         | Metadata SQL   |
 +--+--+------+         +--------+-------+
    |   |                        ^
    |   | watchlists             |
    |   v                        |
    | +----------+               |
    | | Alert DB |               |
    | +----+-----+               |
    |      |                     |
    |      |                     |
    v      v                     |
 +--+------+---+                 |
 | Chart Query |--> Rollups/TS --+
 | + Redis     |
 +------+------+
        ^
        | writes
 +------+-------------------------------+
 | Price Ingest Pipeline                |
 |  Scheduler → Fetch workers → Parse   |
 |       → Validate → TS write          |
 |       → Current cache                |
 |       → Alert evaluator → Outbox     |
 +------+-------------------------------+
        |
        v
 +------+------+     +----------------+
 | Retailer    |     | Notification   |
 | APIs/Sites  |     | Email / Push   |
 +-------------+     +----------------+
```

**Fetch cycle:**

```text
scheduler picks product by priority/due
  -> adapter.fetch(product)
  -> parse prices
  -> if raw_hash unchanged: bump last_checked; skip write
  -> else validate / outlier check
  -> append TS; update current
  -> load alerts(product_id); eval; outbox
```

**User alert create:**

```text
POST /alerts {product_id, threshold, channel}
  -> validate ownership
  -> write alert (armed)
  -> optionally boost product poll priority
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **History append-only** (corrections via new points / tombstone flags, not silent rewrite).  
2. **Alert delivery at-least-once** with idempotency keys.  
3. **Re-arm semantics** prevent inbox spam while price stays low.  
4. **Stale data visible** — `last_checked_at` always shown.  
5. **Currency/marketplace consistency** on comparisons.

#### 5.1.2 Outlier / glitch protection

```text
if price < α * rolling_median or price <= 0: mark suspect
require M-of-N confirmations OR secondary source before alert
still record suspect points with flag for debugging
```

#### 5.1.3 Parser breakage

Retailer HTML changes break crawls.

- Canary products with known expected shape  
- Parse success rate alerts  
- Automatic backoff to last_good  
- Dual parsers during migrations  

#### 5.1.4 Notification reliability

| Step | Mechanism |
|------|-----------|
| Eval | Transactional outbox with observation version |
| Send | Queue workers; provider retries |
| Dedup | `(alert_id, valley_id)` unique |
| User unread flood | Digest mode / rate limit per user |

### 5.2 Scalability

#### 5.2.1 Adaptive scheduling

```text
priority_score =
  + high if active alerts
  + medium if watchlisted
  + popular_velocity
  + recent_volatility
  - backoff if stable long time

due_at = now + interval(priority_score)
```

Hot sale items temporarily elevate poll rate.

**Token bucket per retailer:**

```text
capacity C, refill R/s
acquire(1) before fetch; on 429: freeze bucket + Retry-After
Fairness: separate buckets for API vs crawl vs user-refresh
```

#### 5.2.2 Sharding

| Data | Shard key |
|------|-----------|
| TS raw | `hash(product_id)` |
| Alerts | `product_id` for eval; `user_id` for UX listing |
| Scheduler shards | product_id ranges / consistent hash |
| Fetch proxies | retailer + geo |

#### 5.2.3 Rollup pipeline

```text
raw points → hourly min/avg/max/last
hourly → daily
Query path:
  range ≤ 7d: raw or 5-min
  ≤ 90d: hourly
  > 90d: daily
```

#### 5.2.4 Progressive scale

| Scale | Add |
|-------|-----|
| 10× | Adaptive intervals; Redis current; alert-by-product |
| 100× | TS sharding; cold S3; notify service; crawl cells |
| 1,000× | Per-retailer platforms; streaming eval; hierarchical catalog |

### 5.3 Maintainability

#### 5.3.1 Adapter SDK

```text
interface RetailerAdapter {
  resolve(url) -> ProductRef
  fetch(product) -> PriceObs[]
  normalize(raw) -> PriceObs[]
}
```

Version adapters independently; feature flags per retailer.

#### 5.3.2 Polite crawl deep dive

| Control | Mechanism |
|---------|-----------|
| Per-host concurrency | Semaphore 2–8 |
| Spacing | min delay + jitter |
| Robots.txt | cache; respect Disallow |
| Identity | stable UA; optional auth |
| Ban detection | captcha/403 spike → circuit open |
| Budget | global scheduler admits only within quota |

**User refresh:** enqueue priority task with per-user and per-product rate limits; never inline scrape in API thread.

#### 5.3.3 History TSDB deep dive

```text
Write path:
  validate → append raw → update current cache → ack
  async: rollup consumers from WAL/CDC

Schema tips:
  (product_id, price_type, ts) → price_cents, flags, source
  flags: SUSPECT, OUT_OF_STOCK, CORRECTED

Retention:
  raw hot 90d → warm compressed → cold Parquet
  rollups kept years
```

**Chart API:** pick grain by range; never return unbounded raw.

#### 5.3.4 Alert matching deep dive

```text
On PriceObs committed:
  alerts = index.lookup(product_id)  // sharded
  for alert in alerts:
    if !type_match: continue
    if !available && alert.require_available: continue
    if suspect && !alert.allow_suspect: continue
    eval state machine (armed/triggered)
    if fire: outbox(idempotency=alert_id+valley_id)
```

**Valley id:** hash of (alert_id, local_min_ts_bucket) or increment when re-arm cycles — prevents duplicate emails in one dip.

#### 5.3.5 False alert control

| Gate | Rule |
|------|------|
| Outlier | vs rolling median / IQR |
| Confirm | M-of-N successive obs or dual source |
| Hysteresis | re-arm only above threshold+margin |
| Type match | Buy Box vs list price explicit |
| Currency | never compare across FX silently |
| Stock | optional require in-stock |
| Parse health | adapter success rate below bar → pause alerts |

**Deal-breaker:** emailing on a single $0.01 HTML parse glitch.

#### 5.3.6 Observability

| Metric | Why |
|--------|-----|
| Fetch success / parse rate | Ingest health |
| Obs lag vs schedule | Freshness |
| Alert eval latency | SLO |
| Notify success | User trust |
| Outlier rate | Parser glitches |
| Quota remaining | API budget |
| False-alert sample rate | Trust KPI |
| Circuit-open retailers | Crawl health |

#### 5.3.7 Privacy

- Watchlists are private.  
- Don’t expose who tracks which ASIN publicly.  
- GDPR delete user alerts/PII; product history global.

### 5.4 Notification outbox & digests

```text
outbox row: (id, alert_id, valley_id, channel, payload, status)
Unique(alert_id, valley_id) — at-least-once send, exactly-once effect
Workers: claim → send → ack; retry with backoff; DLQ after N
Digest mode: coalesce per user every T minutes during sales storms
Per-user rate limit: max emails/hour
```

### 5.5 Progressive evolution & anti-patterns

| Jump | Change |
|------|--------|
| →10× | Adaptive schedule; alert-by-product; Redis current |
| →100× | TS shards; crawl cells; notify service; cold Parquet |
| →1,000× | Per-retailer platforms; streaming eval; multi-market fabric |

| Anti-pattern | Fix |
|--------------|-----|
| Scrape on every chart view | Scheduler + cache |
| Nightly full alert scan | Eval on observation |
| 100K-point chart payloads | Rollups |
| Alert on one glitch | Outlier + M-of-N |
| Ignore 429 | Backoff + circuit |
| Merge marketplaces casually | Distinct product_ids |

---

## 6. Wrap-Up

### 6.1 Design summary

A CamelCamelCamel-style tracker **schedules polite fetches**, writes **append-only price time-series**, serves **rollup charts**, and **evaluates alerts on observation** via `product_id` indexes. Users never trigger raw scrapes by browsing charts.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Freshness vs ban risk | Adaptive priority | Long-tail slower |
| Alert speed vs false positives | Confirm glitches | Minutes delay |
| Raw retention vs cost | Tiered rollups | Less zoom fidelity old data |
| Multi-retailer | Adapters | Ontology complexity |

### 6.3 Deal-breakers

1. Scraping retailer on every product page view.  
2. Scanning all alerts on every price tick.  
3. Sending chart clients years of raw points.  
4. Alerting on every poll below threshold without re-arm.  
5. Merging different marketplaces/currencies into one series.

### 6.4 45-minute plan

1. Clarify Amazon MVP, alerts, history.  
2. Scheduler math vs flat polling.  
3. Draw adapters → TS → alert-on-write → notify.  
4. Rollups + outlier + re-arm.  
5. Scale jumps.  
6. Deal-breakers.

### 6.5 Phase 2

- Price prediction / “good deal” score  
- Browser extension crowdsourcing  
- More retailers + coupon intelligence  
- SMS / WhatsApp channels  

---

## 7. Deeper / Related Interview Questions

### Q1. Why not scrape on demand when a user opens a product?

**A:** Amplifies traffic to retailers, adds latency, burns quotas, and risks bans. Decouple UX reads from fetch schedule; optional limited manual refresh.

### Q2. How do you identify a product from a URL?

**A:** Adapter parses ASIN/SKU + marketplace host → canonical `product_id`. Store normalized URL patterns; handle redirects.

### Q3. Buy box vs list price?

**A:** Track multiple `price_type` series. Alerts specify which type (default buy-box / Amazon price). Chart UI can overlay.

### Q4. How do alerts re-arm?

**A:** State machine: `armed` → fire → `triggered`; return to `armed` when price ≥ threshold + margin (hysteresis) to avoid flap.

### Q5. Where do you shard time-series?

**A:** By `product_id` so all writes/reads for a chart go to one shard; avoids scatter-gather per chart.

### Q6. How to handle Amazon API throttling?

**A:** Token bucket per account/key; prioritize alerted ASINs; exponential backoff; cache; multiple keys with care for ToS.

### Q7. Outlier price $1 for a TV — alert?

**A:** No. Statistical guards + confirmation polls. Record but don’t notify until trusted.

### Q8. How are rollups correct for MIN price charts?

**A:** Hourly bucket stores min/max/avg/count/last. Daily min = min of hourly mins. Never average mins incorrectly for “lowest price” displays.

### Q9. Can two users share history storage?

**A:** Yes — product history is global; watchlists/alerts are per-user. That’s the main cost win.

### Q10. Hot product with 100K alerts?

**A:** Shard alert lists; parallel eval workers; notify fanout via queue; consider digest for minor drops.

### Q11. Exact vs approximate “lowest in 1 year”?

**A:** Maintain running min in rollups / side counters updated on write for O(1) stats; verify with rollup query.

### Q12. How do you backfill history?

**A:** Import jobs from dumps/APIs if available; otherwise history starts at first track. Mark chart gaps.

### Q13. Push vs pull notifications?

**A:** Email/push providers are pull from our outbox workers (we push to them). Upstream retailer rarely pushes to us.

### Q14. Consistency of current price vs history last point?

**A:** Update both in one worker after validation; if crash, idempotent rewrite current from last TS point via reconciler.

### Q15. Multi-currency alerts?

**A:** Threshold in same currency as marketplace product. Don’t auto-convert without explicit FX policy.

### Q16. How to test parsers?

**A:** Saved HTML fixtures; contract tests; canary ASINs in prod with expected ranges; shadow parsers.

### Q17. GDPR delete?

**A:** Delete user, alerts, notification PII. Keep anonymized product price series (not personal data).

### Q18. Why idempotency_key on notifications?

**A:** At-least-once pipelines retry. Key `(alert_id, valley_id)` ensures one email per price valley.

### Q19. Availability alerts vs price alerts?

**A:** Separate condition: `available` false→true. Same eval pipeline different predicates.

### Q20. How does affiliate fit architecturally?

**A:** Product URLs annotated with affiliate tags at redirect time; doesn’t change ingest/alert core.

### Q21. Long-tail product never watched — track?

**A:** Lazily: create on first resolve; slow poll until watch/alert boosts priority. Saves fetch budget.

### Q22. Data model for variants?

**A:** `parent_id` + `variant_attributes`; track prices per child ASIN; UI can aggregate “from $X”.

### Q23. Chart caching strategy?

**A:** Cache rollup responses by `(product, range, type, version)`. Invalidate/version bump on new rollup.

### Q24. Stream processing vs DB trigger for alerts?

**A:** Stream/workers on observation log preferred for scale and retries. DB triggers get painful at 100×.

### Q25. How to present “Amazon price vs 3rd party”?

**A:** Separate series; legend on chart; alert channel selection; avoid mixing in one min without labels.

### Q26. What if fetch returns partial fields?

**A:** Schema-tolerant parse; if critical price missing, count as fail; don’t overwrite current with null.

### Q27. Rate-limit user alert creation?

**A:** Yes — abuse can force priority polling. Caps per user; verify email; anomaly detection.

### Q28. Biggest scaling lever?

**A:** Adaptive scheduler + change-detection skip writes + alert-by-product indexing + rollups.

### Q29. How is this different from stock tickers?

**A:** Lower frequency, scrape/API fragility, catalog identity issues, fewer points/sec but nastier HTML and ToS constraints.

### Q30. 60-second pitch?

**A:** “We resolve ASINs, schedule adaptive fetches through retailer adapters, append validated points to a sharded time-series with rollups, and evaluate only that product’s alerts on change. Notifications use re-arm + idempotency. Charts never scrape live.”

### Q31. How do you size crawl politeness?

**A:** Per-host concurrency + min spacing + global token bucket from published quotas. On 429 honor Retry-After and freeze the bucket. Never exceed 70% of stated capacity.

### Q32. Why index alerts by product_id?

**A:** Observation-driven eval is O(alerts_for_product). Scanning 20M alerts per tick cannot work. Hot ASINs shard alert lists.

### Q33. Explain re-arm hysteresis.

**A:** After fire, stay TRIGGERED until price rises above threshold+margin, then ARMED again. Stops email spam while price remains low across polls.

### Q34. Raw vs rollup for a 2-year chart?

**A:** Daily (or weekly) rollups — hundreds of points. Raw 5-minute samples would be ~200K points — unusable in browsers and expensive to query.

### Q35. How do you detect parser breakage?

**A:** Canary ASINs with expected shape; parse success rate SLO; dual parsers; automatic pause of alerts when retailer cell unhealthy.

### Q36. Multi-marketplace same product?

**A:** Separate product_ids; optional catalog links for UX comparison — never silently merge currencies/markets in one series.

### Q37. What is valley_id?

**A:** Idempotency key for one price-dip notification cycle so at-least-once outbox workers don’t double-email.

### Q38. Should user pageviews trigger scrapes?

**A:** No as default path. Optional coalesced refresh with strict rate limits. Charts read TS/cache only.

### Q39. How do flash sales affect scheduler?

**A:** Volatility and watchlist signals raise priority; still clamped by retailer quotas. Digests absorb notify storms.

### Q40. GDPR delete of a user?

**A:** Delete alerts, notify prefs, account PII. Global price history remains (not personal data).

### Q41. Third-party vs Amazon price types?

**A:** Explicit price_type on observations and alerts. Users choose Buy Box / Amazon / 3P new — mismatch is a false-alert source.

### Q42. Progressive scale pitch?

**A:** 10× adaptive intervals + alert-by-product; 100× TS shards + crawl cells; 1,000× per-retailer platforms + streaming eval.

### Q43. Top anti-patterns?

**A:** Scrape-on-view, full alert scans, giant raw charts, single-glitch alerts, ignoring 429, merging markets casually.

### Q44. Where does change detection help?

**A:** `raw_hash` unchanged → skip TS write and alert eval; saves majority of work on stable products.

### Q45. Official API vs crawl — say what in interview?

**A:** Prefer API for schema/quotas; crawl as constrained fallback with politeness and legal awareness — not a botnet fantasy.

---

### Appendix A — NFR card

```text
No scrape-on-view
Alert p95 < 15m from observation
Chart p99 < 300ms
Re-arm hysteresis
Stale badge if last_checked old
Marketplace/currency safe
```

### Appendix B — Alert state machine

```text
armed --(price<=thr trusted)--> triggered --(price>=thr+margin)--> armed
```

### Appendix C — Scheduler intervals (example)

| Tier | Interval |
|------|----------|
| Active alerts | 1–5 min |
| Watchlisted | 15–60 min |
| Popular | 5–30 min |
| Cold | 6–24 h |
| On-demand refresh | user rate-limited |

### Appendix D — History API

```json
{
  "product_id": "ATVPDKIKX0DER:B00EXAMPLE",
  "price_type": "AMAZON",
  "grain": "day",
  "points": [{"t": "2026-01-01", "min": 1999, "avg": 2100, "max": 2500}]
}
```

### Appendix E — Progressive scale

| Scale | Fetch | TS | Alerts |
|-------|-------|----|--------|
| Baseline | 1 pool | 1 TS | SQL index |
| 10× | Priority queues | shard | eval workers |
| 100× | Crawl cells | hot+cold | notify svc |
| 1,000× | Per retailer | lakehouse | streaming CEP |

### Appendix F — Outlier rules

```text
reject if price_cents <= 0
suspect if price < 0.5 * median_30d
confirm with next fetch before notify
```

### Appendix G — Glossary

| Term | Meaning |
|------|---------|
| ASIN | Amazon product id |
| Buy box | Winning offer price |
| Rollup | Pre-aggregated buckets |
| Re-arm | Alert ready after price recovers |
| Valley | Continuous period below threshold |

### Appendix H — 30m checklist

1. Clarify alerts + history + Amazon MVP.  
2. Scheduler vs flat poll math.  
3. Draw ingest → TS → alert-on-write.  
4. Rollups, outliers, re-arm.  
5. Scale + deal-breakers.

### Appendix I — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just scrape in the API” | Ban + latency |
| “Cron all alerts nightly” | Misses drops; won’t scale |
| “Store all points in Postgres rows forever” | Need TS/rollups |
| “Email every poll” | Spam; re-arm |

### Appendix J — Idempotency

```text
idempotency_key = hash(alert_id, valley_id)
valley_id = first_obs_id when crossing below threshold
```

### Appendix K — Product resolve flow

```text
URL → marketplace detect → ASIN regex → upsert product → return id
if unknown: enqueue high-priority first fetch
```

### Appendix L — Related systems

| System | Relation |
|--------|----------|
| Kafka | Obs + outbox |
| TS DB | History |
| SES/FCM | Notify |
| Redis | Current price |

### Appendix M — Worked example

```text
20M alerts across 5M products → avg 4 alerts/product
Hot product 50K alerts → special fanout path
Observation 20K/s → eval only matching alerts ≪ 20M
```

### Appendix N — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Chart strongly consistent global? | Read your writes on same replica policy optional |
| Alert exactly once? | At-least-once + idempotent |
| Current vs history | Reconcile job |

### Appendix O — Security

| Topic | Approach |
|-------|----------|
| Scraping credentials | Secret manager; rotate |
| User data | AuthN/Z on alerts |
| Admin refresh | Privileged |

### Appendix P — Pseudocode eval

```text
def on_obs(obs):
  if not trusted(obs): return
  update_current_and_ts(obs)
  for alert in alerts_by_product[obs.product_id]:
    if alert.state == ARMED and obs.price <= alert.thr and match_type(obs, alert):
      valley = start_valley(alert, obs)
      enqueue_notify(idem=key(alert, valley))
      alert.state = TRIGGERED
    elif alert.state == TRIGGERED and obs.price >= alert.thr + margin:
      alert.state = ARMED
```

### Appendix Q — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Adaptive scheduler, rollups |
| 100× | TS shards, cold tier, notify svc |
| 1,000× | Retailer cells, streaming eval |

### Appendix R — Legal posture (interview)

```text
Prefer official APIs; rate limit; cache; don’t frame design as “bypass blocks.”
Discuss risk as operational constraint on fetch rate.
```

### Appendix S — Interview whiteboard script

1. Clarify Amazon MVP, price types, alerts, history ranges.  
2. Flat poll math → adaptive scheduler.  
3. Adapters → validate → TS → current cache.  
4. Alert-on-observation via `product_id` index.  
5. Re-arm + idempotent notify.  
6. Rollups for long charts.  
7. Outlier confirmation.  
8. Never scrape-on-view.  
9. 10×/100×/1,000×.  
10. Deal-breakers.

### Appendix T — Change detection

```text
raw_hash = hash(price_cents, currency, available, price_type)
if raw_hash == last_hash:
  touch(last_checked_at); return
else:
  append_obs(); evaluate_alerts()
```

Saves TS write amplification on stable products.

### Appendix U — Rollup correctness examples

```text
hourly buckets: [10am min=20, 11am min=18] → daily min=18
never compute daily_min as min(hourly_avg)
for “last price”: take last of last hourly bucket
```

### Appendix V — Priority queue pseudo

```text
heap of (due_at, product_id)
worker loop:
  p = pop_due()
  fetch(p)
  next_interval = f(priority, volatility, alerts)
  push(now + next_interval, p)
```

### Appendix W — Capacity worksheet

```text
products = ______
alerts = ______
polls_per_sec ≈ sum(1/interval_tier)
ts_writes_per_sec ≈ polls × change_rate
chart_qps = ______
notify_peak ≈ sale_fraction × alerts / window_sec
```

### Appendix X — FAQ rapid-fire

| Q | A |
|---|---|
| Scrape on pageview? | No |
| Scan all alerts nightly? | No — eval on write |
| One series all markets? | No |
| Email every poll below? | No — re-arm |
| All points to browser? | No — rollups |

### Appendix Y — Multi-retailer roadmap

| Phase | Retailers | Challenge |
|-------|-----------|-----------|
| MVP | Amazon | ASIN + buy box |
| 1.5 | +1–2 majors | Identity mapping |
| 2 | Many | Ontology / GTIN joins |

---

*End of CamelCamelCamel-style Price Tracker system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Change | Failure if skipped |
|------|--------|--------------------|
| →10× | Adaptive intervals; Redis current; alert-by-product | Quota bans; alert scan death |
| →100× | TS shards; crawl cells; notify service; cold Parquet | Storage + fetch bottlenecks |
| →1,000× | Per-retailer platforms; streaming eval; multi-market fabric | One-size scheduler collapses |

### 8.2 Polite fetch card

```text
prefer official API
else crawl with:
  per-host concurrency ≤ 2–8
  spacing + jitter
  robots respect
  token bucket ≤ 0.7 * quota
  circuit on captcha/403 storms
never scrape inline on chart GET
```

### 8.3 Alert correctness card

```text
index alerts by product_id
on obs: outlier → confirm M-of-N → type/currency/stock gates
state: ARMED ↔ TRIGGERED with hysteresis margin
outbox unique(alert_id, valley_id)
digest under sale storms
```

### 8.4 History card

```text
raw hot 90d; hourly/daily rollups forever
chart grain by range; ~200–500 points to client
raw_hash skip writes when unchanged
```

### 8.5 Anti-patterns

1. Scrape on every pageview  
2. Nightly scan all alerts  
3. Ship 100K raw points  
4. Email on one glitch price  
5. Ignore HTTP 429  
6. Merge marketplaces/currencies silently  

