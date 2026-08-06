# System Design: Book-Review Aggregation System

> **Focus areas:** Review ingest · Ranking · Helpfulness votes · Spam / abuse · Aggregation scores (avg, distribution, bayesian) · Freshness · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split write vs read planes, correct vote idempotency, explicit ranking formula trade-offs, deal-breakers for "AVG(stars) only" or "no spam plane"  
> **Amazon lens:** Bookstore / Amazon Books–class trust, PDP performance, fake-review adjacency, ownership of customer-visible ratings

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

Goal: **bound a book-review aggregation platform** for an online bookstore—ingest reviews and votes, fight spam, rank reviews for the product page, and maintain trustworthy aggregate scores (average, histogram, count)—without letting abuse dominate bestsellers or making PDP reads slow.

### 1.0 What this is / is not

| Dimension | **Book-review aggregation (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Ingest + rank + aggregate + spam filter | Full social network |
| Success | Trustworthy score + useful top reviews on PDP | Maximal review count vanity |
| Adjacent | Fake-review detection (can call out / hook) | Full T&S ML platform deep dive (see fake-review doc) |
| Write path | Review create/edit, helpful votes, reports | Author blog CMS |
| Read path | PDP summary + ranked review list | Offline literary criticism corpus |
| Amazon lens | Books PDP latency, verified purchase, helpfulness, abuse | Goodreads social graph clone (optional stretch) |

**Scope statement:** Design book-review aggregation: review lifecycle, helpfulness, spam controls, ranking, aggregate rating stats, PDP-ready read models—from baseline through 10x / 100x / 1,000x.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Entity? | Book (ASIN/ISBN) + edition issues | `book_id` canonical; edition mapping |
| F2 | Who can review? | Customers; preferably purchasers | Auth + Verified Purchase flag |
| F3 | One review per user per book? | Yes typically | Unique(user, book) |
| F4 | Stars + text? | 1-5 stars; title+body; optional media | Schema + size limits |
| F5 | Edit/delete? | Yes with history / audit | Version or mutate + event |
| F6 | Helpfulness? | Yes / no votes; ranked by helpful | Vote idempotency; score |
| F7 | Aggregates? | Avg, count, histogram 1-5 | Materialized stats |
| F8 | Ranking sorts? | Top / recent / critical (low stars) | Ranker service + indexes |
| F9 | Spam? | Ads, bots, incentivized, duplicates | Rules + ML + reports |
| F10 | Moderation? | Auto + human queue for edge | Policy actions hide/remove |
| F11 | PDP SLA? | Summary must be fast | Precomputed read model |
| F12 | International? | Locale-specific reviews optional filter | locale field + default |
| F13 | Author responses? | Nice-to-have | Separate entity |
| F14 | Import external? | Optional partner feeds | Same ingest with source tag |
| F15 | Abuse reports? | Users report review | Report -> queue |

**MVP functional scope:**

1. Create/edit/delete review (one per user per book).  
2. Star rating + text; verified purchase badge when eligible.  
3. Helpful / not helpful votes (one per user per review).  
4. Aggregate score + histogram per book.  
5. Ranked lists: top reviews, most recent.  
6. Spam/abuse: basic rules + report queue + hide.  
7. PDP APIs: summary + page of reviews.  
8. Events for search index / fake-review hook.  
9. Admin moderation actions with audit.  
10. Metrics: spam rate, vote fraud, PDP latency.

**Out of MVP:**

- Full Goodreads-style social shelves / friends feed  
- Perfect adversarial fake-review ML (hook to dedicated system)  
- Real-time collaborative filtering recommender  
- Unlimited image/video hosting complexity  
- Cross-site review syndication network  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | PDP summary latency | Critical path | p99 < 20–50ms cached |
| N2 | Review list latency | Interactive | p99 < 100–200ms |
| N3 | Write availability | High | Accept writes even if ranker lag |
| N4 | Consistency | Read-your-write for author | Summary eventual seconds OK |
| N5 | Vote correctness | No double count | Idempotent votes |
| N6 | Spam resilience | Continuous | Multi-layer defense |
| N7 | Scale | Progressive table | Shard by book_id / user_id |
| N8 | Durability | Reviews durable | Multi-AZ |
| N9 | Audit | Moderation trail | action log |
| N10 | Privacy | User identity rules | Public display name policy |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Purchaser posts 5* review -> appears after spam check -> updates aggregates -> may enter top reviews.  
2. Users mark review helpful -> helpful score rises -> rank updates.  
3. Spam link review -> auto-hide -> aggregates exclude.  
4. Author (bookstore) filters "critical reviews" sort for low-star helpful.  
5. User edits review stars 4->2 -> aggregates adjust delta; rank recompute.  
6. User deletes review -> remove from aggregates + lists.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double submit review | Unique constraint; idempotency key |
| Vote spam rings | Rate limits; trust-weighted votes; anomaly |
| Best-seller hot book | Shard aggregates; cache PDP heavily |
| Review bomb (brigade) | Velocity alerts; temporary ranking dampening |
| Verified purchase revoked (return) | Recompute badge; optional policy on eligibility |
| Empty book (0 reviews) | Show empty state; bayesian prior optional |
| Unicode / RTL / emoji spam | Normalization; filters |
| Extremely long text | Hard limit; truncate display |
| Concurrent helpful votes | Atomic counters / CRDT-ish with reconciler |
| Moderation overturn | Restore + aggregate delta |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10x | 100x | 1,000x |
|--------|----------|-----|------|--------|
| Books with reviews | 5M | 50M | 500M | 5B |
| Reviews total | 200M | 2B | 20B | 200B |
| New reviews / day | 200K | 2M | 20M | 200M |
| Peak review write QPS | ~20 | ~200 | ~2K | ~20K |
| Helpful votes / day | 2M | 20M | 200M | 2B |
| Peak vote QPS | ~200 | ~2K | ~20K | ~200K |
| PDP summary QPS | ~50K | ~500K | ~5M | ~50M |
| Review list QPS | ~20K | ~200K | ~2M | ~20M |
| Spam checks / write | ~20 | ~200 | ~2K | ~20K |
| Report queue / day | 10K | 100K | 1M | 10M |

**What each jump forces:**

- **10x:** Cached summary; async aggregation; vote service; basic spam rules.  
- **100x:** Shard by book_id; rank materialization; CDN/edge cache PDP; ML spam nearline.  
- **1,000x:** Cell by marketplace; hot-book special casing; approximate counters + periodic reconcile; dedicated fake-review platform integration.

### 1.5 Etc. (Constraints & Assumptions)

- **Aggregates exclude** hidden/removed/spam-suppressed reviews (policy).  
- PDP **never** computes AVG over all reviews on demand at 100x+.  
- Helpfulness ranking uses a **dampened** score (Wilson / Bayesian), not raw ups.  
- Verified purchase is a strong feature but not sole spam defense.  
- Distinct from—but integrable with—`fake-review-detection-system-design.md`.

**Scope statement:**

> Book-review aggregation for a bookstore: ingest reviews & votes, spam controls, ranking, precomputed aggregates for PDP—from ~50K summary QPS through 1,000x, optimizing trust and latency over naive averages.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000x | Notes |
|-------|---------------|--------|-------|
| PDP summary read | 50K | 50M | Cache / edge |
| Review list read | 20K | 20M | Per-book pages |
| Review create/edit | 20 | 20K | Write |
| Helpful vote | 200 | 200K | Write-ish |
| Report | 5 | 5K | Write |
| Aggregation updater | async | async | Event-driven |
| Spam score | 20 | 20K | Inline+async |
| Moderation actions | 1 | 1K | Low |

**Critical:** Read QPS >>> write QPS. Design for cacheable summaries. Hot books (Harry Potter / Oprah picks) dominate traffic—not average book.

### 2.2 Storage

```text
Review ~1–5 KB (text) average ~2 KB
200M reviews * 2 KB = 400 GB baseline
100x: 20B * 2 KB = 40 TB

Vote row ~50 B; 10 votes/review avg -> same order or larger than reviews
Aggregate doc per book ~200 B trivial
```

### 2.3 Hot book math

```text
Top book: 50K summary QPS at baseline peak possible during promo
Cache TTL 1-10s with stampede protection -> origin tiny
Top reviews list cached similarly; personalization light on MVP
```

### 2.4 Aggregation math

```text
Naive: each vote recomputes rank for book with 100K reviews -> too slow
Keep: per-review helpful counters; periodic top-N recompute OR streaming top-K structure
Aggregates: maintain histogram counts[5]; avg = weighted sum/count
```

### 2.5 Critical bottlenecks

1. Hot book cache stampede  
2. Vote fraud inflating helpful  
3. Review bomb on release day  
4. Aggregate drift vs ground truth  
5. Spam model latency on write  
6. Giant review text storage / scan  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Book (book_id, isbn, title, ...)
Review (review_id, book_id, user_id, stars, title, body, locale,
        verified_purchase, status, created_at, edited_at,
        helpful_up, helpful_down, spam_score)
ReviewVote (review_id, user_id, value=UP|DOWN, at) UNIQUE(review_id,user_id)
ReviewReport (report_id, review_id, reporter_id, reason, status)
BookRatingAgg (book_id, count, sum_stars, hist[5], updated_at, version)
BookReviewRank (book_id, sort_key, review_ids_page stubs / top-N list)
ModerationAction (id, review_id, action, actor, reason, at)
```

### 3.2 Planes

```text
1. Write plane     - review & vote APIs
2. Trust plane     - spam/abuse score + reports
3. Aggregation     - rating stats materialization
4. Ranking         - top/recent/critical lists
5. Read plane      - PDP summary + list APIs (cache)
6. Moderation      - human queues
7. Control         - knobs, kill switches, feature flags
```

### 3.3 Review lifecycle

```text
DRAFT (optional) -> PENDING_CHECK -> VISIBLE
                 -> HIDDEN_SPAM
                 -> REMOVED_MOD
VISIBLE -> EDITED (re-check) -> VISIBLE / HIDDEN
VISIBLE -> USER_DELETED
```

Inline: cheap rules (links, banned phrases, velocity). Async: ML spam / fake-review service. Prefer **publish then suppress** for UX unless high-risk (new accounts with links)—say trade-off.

### 3.4 Aggregation scores

```text
hist[s] = count of VISIBLE reviews with stars=s
count = sum(hist)
avg = sum(s*hist[s]) / count   // display rounded
```

**Bayesian average (optional for sorting books, not always for display):**

```text
bayesian_avg = (C * m + sum_stars) / (C + count)
m = global mean; C = confidence prior (e.g., 20)
```

**Display policy:** show raw avg + count; use bayesian for "Top rated books" lists to avoid 5* with n=1 winning.

### 3.5 Helpfulness & ranking

**Wilson score interval** (lower bound) for ranking "top reviews":

```text
Use ups, downs among votes; rank by wilson_lower_bound
Dampens low-sample noise vs raw ups
```

**Composite rank score (practical):**

```text
score = w1 * wilson(helpful)
      + w2 * verified_purchase
      + w3 * recency_decay
      + w4 * text_quality
      - w5 * spam_score
Sort KEY = score; tie-break review_id
```

**Recent sort:** `created_at desc` among VISIBLE.  
**Critical sort:** low stars + high helpful.

### 3.6 Vote path

```text
POST vote(review_id, user_id, value):
  upsert vote row UNIQUE(review_id,user_id)
  delta counters on review (handle switch UP<->DOWN)
  enqueue rank_update(book_id, review_id)
Fraud: rate limit; discard votes from new/low-trust; detect rings nearline
```

### 3.7 Spam / abuse (MVP layered)

| Layer | Examples | Action |
|-------|----------|--------|
| Rules | URL dens, banned tokens, dup body hash | Block or hide |
| Velocity | N reviews/hour/user; book review bomb | Throttle / dampen |
| Signals | Account age, VP, device | Soft score |
| Reports | User reports threshold | Queue |
| ML / fake-review svc | Hook async | Suppress |

**Deal-breaker:** aggregates that include hidden spam (inflated scores).

### 3.8 PDP read models

```text
BookRatingAgg cached at edge/CDN keyed by book_id
Review list: precomputed top-N (e.g. 100) in cache/KV
Deep pages: query storage by (book_id, sort, cursor)
```

### 3.9 Editions / ISBN

```text
Canonical book_id groups hardcover/paperback/kindle if product policy says "same reviews"
OR separate by ASIN with optional "reviews for other formats"
Lock policy early with interviewer
```

### 3.10 Storage trade-offs

| Store | Role |
|-------|------|
| DynamoDB/Cassandra | Reviews by book_id, votes |
| Postgres | Moderation, reports optional |
| Redis/CDN | Agg + top-N lists |
| OpenSearch | Search reviews (admin/user search) |
| Kafka | Review events to aggregators / fake-review |
| S3 | Media attachments |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Web/Mobile PDP]     [Review Authoring]     [Moderators]
       |                     |                    |
       v                     v                    v
   Read API              Write API            Mod API
   (cache)                   |                    |
       ^                     v                    v
       |               Review Service -----> Trust/Spam
       |                     |                  |
       |                     v                  v
       |               Vote Service         Report Queue
       |                     |                  |
       |                     +--------+---------+
       |                              v
       |                      Event Bus (Kafka)
       |                         /        \
       |                        v          v
       |                 Aggregator     Ranker
       |                        \          /
       |                         v        v
       +------------------- Read Models (Agg + Top-N)
```

### 4.2 Write path detail

```text
createReview -> authz -> unique(user,book) -> inline spam rules
  -> persist PENDING/VISIBLE -> emit ReviewCreated
  -> async spam/ML -> maybe hide -> emit ReviewVisibilityChanged
  -> aggregator applies deltas
```

### 4.3 Hot book caching

```text
Edge cache BookSummary TTL=2s + stale-while-revalidate
Singleflight origin fill
On update: async invalidate or version bump (book_id:ver)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. At most one active review per (user_id, book_id).  
2. At most one vote per (user_id, review_id).  
3. Aggregates match VISIBLE reviews within lag SLO (e.g., < 60s p99).  
4. Hidden/removed reviews do not contribute to displayed aggregates.  
5. Moderation actions audited.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Aggregator lag | Serve slightly stale; alert on lag |
| Double count vote | Unique + transactional counter update |
| Cache serve spam-hidden | Visibility version in cache key |
| Ranker down | Fallback recent sort |
| Write DB hot partition | Shard / promote hot book storage |

**Degradation:** If spam ML down -> rules-only; fail open to VISIBLE with async recheck **or** fail closed for link-heavy—product call. Prefer fail-open + fast nearline suppress for bookstore UX.

### 5.2 Scalability

| Scale | Tactic |
|-------|--------|
| 10x | Cache summaries; async agg; indexes (book_id, created_at) |
| 100x | Shard reviews by book_id; top-N materialization; CDN |
| 1000x | Marketplace cells; approximate vote counters + reconcile; hot-book tier |

**Hot keys:** Popular `book_id` aggregates—use atomic adders; cache heavily; don't put all reviews of hot book on one disk under-replicated.

**Fan-out:** Don't notify followers on MVP; keep system aggregation-centric not social-graph-centric.

### 5.3 Maintainability

**Ownership:** Review Write, Votes, Aggregation/Ranking, Trust/Spam, PDP Read, Moderation Tools.

**Ranking changes:** Version rank formulas; A/B via experimentation platform; shadow score.

**Observability:** PDP p99, agg lag, hide rate, report rate, vote fraud score, top-N freshness, drift checks (sampled recomputes).

**Testing:** Golden ranking fixtures; aggregate delta property tests; vote switch UP/DOWN; visibility exclusion.

---

## 6. Wrap-Up

### 6.1 MVP build order

1. Review CRUD + unique(user,book)  
2. BookRatingAgg deltas  
3. PDP summary API + cache  
4. Recent list  
5. Votes + helpful counters  
6. Top reviews via Wilson/composite  
7. Inline spam rules + hide  
8. Reports + mod tools  
9. Async ML/fake-review hook  
10. Histogram + bayesian for "top books" (if needed)  

### 6.2 Trade-offs

| Choice | Trade-off |
|--------|-----------|
| Publish-then-suppress | Better UX; brief spam flash |
| Wilson vs raw ups | Complexity; better quality |
| Bayesian book sort | Fairness; less intuitive than raw avg |
| Editions merged | More data; less precise format feedback |

### 6.3 Risks

1. Review bombing bestsellers.  
2. Helpful-vote rings.  
3. Aggregate drift / cache serving stale bad score.  
4. Over-moderation silencing legitimate criticism.  
5. Hot-book outages on launches.

### 6.4 60-second pitch

> Reviews sharded by book with one-per-user constraint; votes idempotent; trust plane hides spam before aggregates count them; aggregators maintain histogram/avg via event deltas; rankers materialize top-N using Wilson+verified+recency; PDP reads cached summaries at edge. Scale reads with CDN; protect hot books; hook deeper fake-review detection async.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & rules

**Q: One review per book?**  
A: Yes MVP; edits allowed; history optional.

**Q: Require purchase?**  
A: Prefer VP badge; optionally require for visibility—trade-off volume vs trust.

**Q: Star-only without text?**  
A: Allow; ranking may downweight empty text.

**Q: Syndicated publisher blurbs?**  
A: Separate from user reviews; don't mix aggregates.

### 7.2 Aggregation

**Q: Why not SELECT AVG live?**  
A: Hot PDP QPS; expensive; contention.

**Q: Floating avg?**  
A: Store integer sum_stars + count; display round half-up policy.

**Q: Exclude hidden?**  
A: Yes; on hide emit negative delta.

**Q: Bayesian on PDP?**  
A: Usually show raw avg+count; bayesian for discovery ranking.

### 7.3 Ranking

**Q: Why Wilson?**  
A: Low-sample 100% helpful shouldn't beat 10k-vote review.

**Q: Recency?**  
A: Decay so ancient reviews don't dominate forever; product knob.

**Q: Personalization?**  
A: Stretch; MVP global sorts + locale filter.

**Q: Critical reviews tab?**  
A: Filter stars<=2 sort by helpful.

### 7.4 Votes

**Q: Change vote?**  
A: Upsert; adjust counters by delta.

**Q: Self-helpful?**  
A: Disallow author voting on own review.

**Q: Vote fraud?**  
A: Trust scores; graph rings; rate limits; discount suspicious votes in rank (shadow) before hard delete.

### 7.5 Spam

**Q: Duplicate text across books?**  
A: Body hash clustering nearline.

**Q: Incentivized reviews?**  
A: Phrase rules + fake-review service; disclosure policy.

**Q: Review bomb?**  
A: Velocity per book; temporary ranking freeze / sampling; T&S alert.

**Q: Relation to fake-review doc?**  
A: This system owns aggregation/UX; fake-review owns authenticity scoring—event integration.

### 7.6 Caching

**Q: TTL vs invalidation?**  
A: Short TTL + version bump on agg change; singleflight.

**Q: Stale-while-revalidate?**  
A: Great for PDP summary.

**Q: Personalized cache?**  
A: Avoid on summary; keep summary global.

### 7.7 Editions

**Q: Kindle vs hardcover?**  
A: Ask; either share `work_id` aggregates or separate; UX copy if shared.

### 7.8 Estimation traps

**Q: 50M summary QPS all hit DB?**  
A: Impossible—edge cache mandatory.

**Q: 20B reviews * 2KB = 40PB?**  
A: 40 **TB**.

### 7.9 Interview traps

**Q: "Average stars is enough ranking."**  
A: Helpfulness + spam + recency matter for review order; bayesian for book lists.

**Q: "Compute top reviews with full table scan each request."**  
A: Materialize top-N.

**Q: "Count votes eventually without idempotency."**  
A: Double votes / lost votes.

**Q: "Include spam in average until weekly job."**  
A: Trust hole; use event-driven hide deltas.

**Q: "Global secondary index everything in one SQL."**  
A: Won't carry hot books at Amazon scale—shard + cache.

### 7.10 Ownership scenarios

**Q: Sev: bestseller stuck at 1.2 stars from bomb.**  
A: Velocity dampen; hide clusters; recompute agg; comms; root-cause acquisition.

**Q: PDP shows 4.8 but list empty.**  
A: Visibility mismatch / cache; fix exclusion rules; rebuild.

**Q: Wilson deploy tanks engagement.**  
A: Roll back rank version; A/B; explain metrics.

### 7.11 Comparisons

**Q: vs fake-review detection?**  
A: Detection scores authenticity; this aggregates & ranks visible corpus.

**Q: vs ratings-only apps?**  
A: Books need text helpfulness and long-tail trust.

### 7.12 Misc deep cuts

**Q: Media in reviews?** A: Object store; moderation; don't block text path.  
**Q: Translation?** A: Optional MT; store locale; filter.  
**Q: Author reply?** A: Child entity; not in star agg.  
**Q: Import Goodreads?** A: Source-tagged ingest; spam higher suspicion.  
**Q: GDPR delete user?** A: Anonymize reviews or delete per policy; re-agg.  
**Q: Spoiler tags?** A: Flag + UI blur; rank optional penalty.  
**Q: Crushing edit wars?** A: Rate-limit edits; freeze after N.  
**Q: Histogram animation?** A: Read model only.  
**Q: A/B rankers?** A: Score v2 shadow; experiment exposure.  
**Q: Exact vs approx counters?** A: Exact MVP; approx at extreme vote QPS with daily reconcile.

---

## 8. Appendices

### 8.1 Schema sketches

```text
reviews(
  review_id, book_id, user_id, stars, title, body, locale,
  verified_purchase BOOL, status, spam_score,
  helpful_up, helpful_down, created_at, edited_at,
  UNIQUE(user_id, book_id)
)
review_votes(review_id, user_id, value, at, PRIMARY KEY(review_id,user_id))
review_reports(report_id, review_id, reporter_id, reason, status)
book_rating_agg(
  book_id PK, count, sum_stars,
  h1,h2,h3,h4,h5, updated_at, ver
)
book_top_reviews(book_id, ranker_version, review_ids[], updated_at)
moderation_actions(id, review_id, action, actor_id, reason, at)
review_events(event_id, type, payload, at)  -- bus archive
```

### 8.2 API sketches

```text
POST /v1/books/{book_id}/reviews
Idempotency-Key: ...
{ "stars":5, "title":"Loved it", "body":"...", "locale":"en_US" }

PATCH /v1/reviews/{id}
{ "stars":4, "body":"..." }

POST /v1/reviews/{id}/votes
{ "value":"UP" }

GET /v1/books/{book_id}/rating-summary
-> { "avg":4.6, "count":12345,
     "hist":{"1":100,"2":200,"3":500,"4":3000,"5":8445} }

GET /v1/books/{book_id}/reviews?sort=top&cursor=
-> { "items":[...], "next_cursor":"..." }
```

### 8.3 Aggregate delta pseudocode

```text
function applyVisibility(review, old_status, new_status):
  if old_status == VISIBLE and new_status != VISIBLE:
    aggAdd(review.book_id, -1, -review.stars, -hist(review.stars))
  if old_status != VISIBLE and new_status == VISIBLE:
    aggAdd(review.book_id, +1, +review.stars, +hist(review.stars))

function onStarsEdit(review, old_stars, new_stars):
  if review.status != VISIBLE: return
  aggAdd(book, 0, new_stars-old_stars, hist_delta(old,new))
```

### 8.4 Wilson score snippet

```text
function wilsonLower(ups, downs, z=1.96):
  n = ups + downs
  if n == 0: return 0
  phat = ups / n
  return (phat + z*z/(2*n) - z*sqrt((phat*(1-phat)+z*z/(4*n))/n)) / (1+z*z/n)
```

### 8.5 Rank score

```text
function rankScore(r):
  return 1.0 * wilsonLower(r.up, r.down)
       + 0.15 * (1 if r.verified else 0)
       + 0.10 * recencyDecay(r.created_at)
       + 0.05 * textQuality(r)
       - 0.50 * r.spam_score
```

### 8.6 Vote upsert

```text
function vote(review_id, user_id, value):
  old = get_vote(review_id, user_id)
  if old == value: return
  begin:
    upsert vote
    apply_counter_delta(review, old, value)
  enqueue RankTouch(review.book_id, review_id)
```

### 8.7 Spam rules examples

| Rule | Action |
|------|--------|
| >3 URLs in body | Hide pending review |
| Exact body hash used >5 times / day | Hide cluster |
| New account + 10 reviews / hour | Throttle |
| Reports >= 5 and helpful_up < 2 | Queue + soft-hide |

### 8.8 Glossary

| Term | Meaning |
|------|---------|
| PDP | Product Detail Page |
| VP | Verified Purchase |
| Wilson | Confidence interval ranking for helpfulness |
| Bayesian avg | Smoothed average with prior |
| Top-N materialization | Precomputed ranked IDs |
| Review bomb | Coordinated burst of low/high stars |
| Work ID | Canonical grouping across editions |

### 8.9 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1x | CRUD, unique review, avg+count, recent list |
| 10x | Cache summary, votes, Wilson top, spam rules |
| 100x | Shards, top-N KV, CDN, async ML hook |
| 1000x | Cells, hot-book tier, vote approx+reconcile |

### 8.10 Cache key design

```text
summary:{book_id}:v{agg_ver}
top:{book_id}:{ranker_ver}:v{list_ver}
locale optional suffix :en_US
```

### 8.11 Operator runbooks

1. Review bomb on bestseller  
2. Aggregate drift detected  
3. Cache stampede  
4. Vote fraud surge  
5. False-positive spam hide wave  
6. Hot book write throttle  

### 8.12 Worked scale (100x)

```text
PDP summary 5M QPS -> edge hit rate 99%+ => origin 50K
Votes 200M/day -> ~2K avg QPS; peaks 20K
Aggregator must be partitioned by book_id
```

### 8.13 Worked scale (1,000x)

```text
Summary 50M QPS -> multi-tier CDN; regional
200M reviews/day write -> write cells by marketplace
Fake-review platform mandatory companion not DIY in this service alone
```

### 8.14 Interview "say this" summary

> Event-driven aggregates excluding hidden spam; idempotent votes; Wilson-style top reviews; heavy PDP caching; async trust; shard by book; protect hot keys; bayesian for discovery not necessarily display.

### 8.15 Sample summary JSON

```text
{
  "book_id": "B1",
  "avg": 4.57,
  "count": 12890,
  "hist": {"1":120,"2":210,"3":900,"4":3560,"5":8100},
  "as_of": "2026-08-06T10:00:00Z"
}
```

### 8.16 Security checklist

- [ ] Auth on write  
- [ ] No self-helpful  
- [ ] Rate limits  
- [ ] XSS escape review HTML (plaintext/markdown safe)  
- [ ] Moderation authz  
- [ ] PII retention on reports  

### 8.17 Reliability test plan

1. Hide review -> agg count decrements.  
2. Vote UP then DOWN -> counters correct.  
3. Double create review -> one row.  
4. Ranker version flip deterministic golden set.  
5. Cache version bump drops spam-included summary.  
6. Sampled full recompute matches agg within epsilon.

### 8.18 Idempotency matrix

| API | Key | Replay |
|-----|-----|--------|
| Create review | Idempotency-Key / (user,book) | Same review |
| Vote | (review,user) | Same value |
| Report | (review,reporter,day) optional | Dedup |
| Mod action | action_id | Same effect |

### 8.19 Final trap table

| Trap | Pushback |
|------|----------|
| Live AVG each PDP | Won't scale / hot |
| Raw helpful ups ranking | Low-n noise |
| Spam counted in avg | Trust fail |
| Non-idempotent votes | Corruption |
| 20B*2KB=40PB | **40TB** |
| No hot-book plan | Launch outage |

### 8.20 Whiteboard close

Draw **Write/Vote -> Events -> Aggregator/Ranker -> Cached PDP Read**, plus **Spam/Mod** affecting visibility deltas. Walk hide-from-aggregate and Wilson vs raw ups.

> Ratings trust is **the bookstore**—optimize for abuse-resistant aggregates and fast PDP, not clever SQL averages.

### 8.21 Recency decay example

```text
age_days = (now - created_at).days
recency = exp(-age_days / 180)  // half-life-ish ~months
```

### 8.22 Drift detector

```text
hourly sample random books:
  recompute hist from source of truth VISIBLE reviews
  compare to book_rating_agg; alert if |delta| > threshold
  autofix job if confirmed
```

### 8.23 Review bomb controls

```text
if new_reviews(book, 1h) > dynamic_threshold(book_popularity):
  flag book
  dampen rank influence of brand-new accounts
  require VP for immediate visibility (temp)
  page T&S
```

### 8.24 Edition policy examples

| Policy | Behavior |
|--------|----------|
| Work-aggregated | All formats share reviews/agg |
| ASIN-separate | Each format own reviews |
| Hybrid | Show "also for other formats" module |

### 8.25 Interview timing guide

| Minute | Topic |
|--------|-------|
| 0-5 | Review rules, VP, sorts, spam |
| 5-10 | QPS split read vs write |
| 10-25 | HLD + agg + rank |
| 25-40 | Spam, votes, cache, hot books |
| 40-45 | 100x/1000x + wrap |

### 8.26 Text quality features (light)

```text
length in range, paragraph structure, spoilers tag,
non-duplicate, language match locale, not all caps
-> small rank bonus; never sole factor
```

### 8.27 Integration with fake-review detection

```text
ReviewCreated/Edited -> FakeReview platform
callback Enforcement(suppress/remove) -> visibility change -> agg delta
Appeals overturn -> restore + delta
```

### 8.28 More rapid-fire Q&A

**Q: Should deleted users null reviews?** A: Policy: anonymize "Former Customer" or delete + reagg.  
**Q: Can publishers pay for ratings?** A: No; ads separate; integrity hard line.  
**Q: How to page top reviews stably?** A: Keyset on (score, review_id); materialize first pages.  
**Q: Negative helpful?** A: Store downs; Wilson uses both.  
**Q: Image OCR spam?** A: Media trust pipeline stretch.  
**Q: Multi-language sort?** A: Filter locale first.  
**Q: Crushing celebrity book launch?** A: Pre-warm cache; elevate hot-book tier; raise write capacity.  
**Q: Exact average display 4.573?** A: Round to 1 decimal typical; keep precise internally.  
**Q: Histogram only?** A: Still need count/avg for UX.  
**Q: GraphQL vs REST?** A: Irrelevant; discuss caching boundaries.

### 8.29 Failure injection

1. Kill aggregator -> lag alert; catch-up from bus.  
2. Duplicate hide events -> idempotent deltas via event_id.  
3. Cache poisoned with old ver -> version key forces miss.  
4. Vote DB timeout -> return 503; client retry safe.  
5. Mod accidental mass hide -> kill switch + undo tool from audit.

### 8.30 Final checklist

- [ ] Read/write QPS split stated  
- [ ] Precomputed aggregates  
- [ ] Wilson/composite ranking  
- [ ] Spam visibility excludes from avg  
- [ ] Idempotent votes  
- [ ] Hot-book caching  
- [ ] Hook to deeper fake-review system  
- [ ] Progressive scale  

---


### 8.31 Helpfulness UI copy notes

```text
"12 people found this helpful"
If downs exist, typically don't show downs publicly (Amazon-like)
Internal rank uses both ups and downs
```

### 8.32 Cursor pagination example

```text
sort=top cursor = base64(score, review_id)
query: (score < c_score) OR (score = c_score AND review_id < c_id)
LIMIT 10
Stable even if mid-list scores move slightly; accept small churn or snapshot top-N pages
```

### 8.33 Verified purchase pipeline

```text
Order fulfilled + not returned within window -> VP eligible
Review create checks orders service
If later return: emit VP revoked -> update badge; optionally leave review
```

### 8.34 Content safety vs spam

```text
Hate/PII/illegal -> content moderation service (separate)
Spam/ads/fake -> trust plane in this design
Both can hide; reason codes distinct for appeals
```

### 8.35 Metrics that matter

| Metric | Why |
|--------|-----|
| PDP summary p99 | Revenue path |
| Agg lag p99 | Trust in score freshness |
| Hide rate | Spam pressure / FP risk |
| % VP among new reviews | Quality mix |
| Ranker engagement (helpful click) | Ranking quality |
| Drift incidents | Data correctness |

### 8.36 Sample event payloads

```text
ReviewCreated {review_id, book_id, user_id, stars, status, ts}
ReviewVisibilityChanged {review_id, book_id, from, to, reason, ts}
VoteChanged {review_id, book_id, up_delta, down_delta, ts}
AggRebuilt {book_id, ver, ts}
```

### 8.37 Final interview reminders

- Split read vs write QPS first
- Precompute aggregates; exclude hidden
- Wilson not raw ups
- Hot-book caching plan
- Mention fake-review system as sibling
- Integer sum/count not float avg storage

---


### 8.38 Close

> Cache summaries, exclude spam from aggregates, rank with Wilson—not raw averages alone.


### 8.39 One more worked example

```text
Book has 100 VISIBLE reviews: hist 5,10,15,30,40 -> count=100 sum=390 avg=3.90
Hide a 1-star spam: hist1=4 count=99 sum=389 avg~3.93
Top review: 80 up 5 down -> strong Wilson; beats 3 up 0 down
```

*End of Amazon SDE III prep doc: Book-Review Aggregation System.*
