# System Design: Facebook News Feed

> **Focus areas:** Fan-out (write vs read) · Ranking · Multi-tier caching · Celebrity / high-fanout users · Timeline materialization  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split write/read/ranking planes, explicit hybrid fan-out, deal-breakers for “push to all 100M followers” fantasies  
> **Interview theme:** Classic Meta E4–E5 social product — news feed generation under extreme follow-graph skew, ranking latency budgets, and cache coherence  
> **Company flavor:** Meta — social graph, TAO-like graph store concepts, memcache/ODS-style caching culture, feed ranking as ML product + infra

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

Goal: **bound the product**—a personalized **News Feed** that aggregates posts from people/pages a user follows (plus optional groups/pages), ranks them for relevance, and serves a low-latency scrollable timeline. Distinct from Stories, Reels ranking, or Ads auction (mention as adjacent).

### 1.0 What this is / is not

| Dimension | **News Feed (this doc)** | Not this |
|-----------|--------------------------|----------|
| Primary job | Ranked timeline of posts from graph neighborhood | Full social network / Messenger |
| Success | Relevant, fresh, fast first paint | Perfect global chronological dump |
| Write path | Create post → fan-out / index | Chat message delivery |
| Read path | Hydrate + rank candidate posts | Ad click tracking (hooks only) |
| Hard problem | Celebrity fan-out + ranking cost | Exact global search |

**Scope statement:** Design Facebook-style News Feed: create posts, hybrid fan-out, candidate generation, ranking, caching, and progressive scale with celebrity handling.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What appears in feed? | Posts from friends/follows/pages; photos, text, links, reshare | Post entity + media refs; graph edges |
| F2 | Chronological or ranked? | Ranked relevance (ML); chronological mode optional | Ranking service; feature store |
| F3 | Create post UX? | Instant “posted”; friends see soon | Async fan-out after durable write |
| F4 | Privacy? | Audience: public / friends / custom lists | Visibility check before serve |
| F5 | Pagination? | Infinite scroll; cursor-based | Opaque cursors; stable under inserts carefully |
| F6 | Interactions? | Like/comment/share counts; comment preview | Counters + light hydration; comments separate |
| F7 | Celebrity / pages? | Millions of followers common | Hybrid fan-out; pull for celebrities |
| F8 | Soft deletes / edits? | Edit caption; delete removes | Tombstones; cache invalidation |
| F9 | Notifications? | Optional “X posted” — out of critical path | Event bus hook only |
| F10 | Groups / interest? | Phase 1.5 — groups in feed | Separate candidate sources |
| F11 | Ads? | Interleaved slots Phase 2 | Ranking slots reserved; separate auction |
| F12 | Multi-device? | Same user, consistent enough | Home region / cache; eventual OK |

**MVP functional scope:**

1. Authenticated user creates a **post** (text + optional media refs) with audience.  
2. Post is **durably stored**; creator sees it immediately (read-your-write).  
3. **Hybrid fan-out:** push to follower timelines for normal users; pull/on-read for celebrities.  
4. Feed read: **candidate generation** → **ranking** → **hydration** → paginated response.  
5. Privacy/visibility filters applied before return.  
6. Multi-tier cache for timelines, post objects, and social graph edges.  
7. Basic counters (likes/comments) with eventual consistency.  
8. Observability: fan-out lag, ranking latency, cache hit rates.

**Out of MVP:**

- Full Reels / Watch recommendation as primary surface  
- Perfect cross-region strong consistency of every like  
- Real-time collaborative editing of posts  
- Ads auction deep dive (mention slotting only)  
- Stories ephemeral product (sibling)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Feed first paint | Feels instant | p50 < 100–200ms, p99 < 500ms (cached path) |
| N2 | Post create ACK | Instant UX | p99 < 200ms durable write |
| N3 | Fan-out freshness | Friends see soon | Normal users p99 < 1–5s; celebs on-read |
| N4 | Availability | Social critical | 99.9%+ read; degrade ranking → chrono |
| N5 | Durability | No lost posts after ACK | Multi-AZ primary store |
| N6 | Ranking quality | Relevant, not random | ML ranker with fallback features |
| N7 | Privacy correctness | Never leak private posts | Filter in candidate + hydrate |
| N8 | Multi-region | Global users | Home region / cell; async replicate |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Alice posts photo → durable write → fan-out to friends’ timeline caches → Bob opens feed → ranked list includes Alice.  
2. Bob scrolls → cursor page 2 → more candidates ranked → hydrate media URLs.  
3. Celebrity with 50M followers posts → write durable; **no** push to 50M timelines; followers pull on read.  
4. Alice deletes post → tombstone → timelines/caches drop or filter.  
5. Ranking overloaded → serve chronological from materialized timeline.  
6. Like from Carol → counter +1 eventual; feed card updates on next hydrate.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit post | Idempotency-Key → one post_id |
| Fan-out worker crash | Kafka replay; idempotent timeline insert |
| Hot celebrity post storm | Pull path + sharded post cache; rate-limit hydrate |
| Privacy change mid-flight | Re-check visibility at serve time (never trust fan-out alone) |
| Graph edge churn (unfollow) | Timeline may briefly show; filter on read; async cleanup |
| Ranking model deploy bad | Feature flag; fallback heuristic ranker |
| Cache stampede on viral post | Singleflight / request coalescing; soft TTL |
| Cursor invalid after delete | Skip missing; continue with next |
| Cross-region friend | Async replicate; short lag acceptable |
| Empty feed (new user) | Seed suggestions / pages (product); infra returns empty OK |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 50M | 500M | ~Facebook-class | multi-B class |
| Peak feed reads QPS | 100K | 1M | 10M | 100M |
| Peak post creates /s | 5K | 50K | 500K | 5M |
| Avg follows / user | 200 | 200–300 | 300 | 300+ |
| Avg followers / user | 200 | skewed | heavily skewed | extreme skew |
| Celebrity threshold (followers) | 10K | 50K | 100K | dynamic |
| Posts in active timeline window | ~500–2K | same | same | same |
| Avg post size (meta) | ~2 KB | 2 KB | 2–4 KB | 2–4 KB |
| Ranking candidates / request | 500–2K | 1–3K | 2–5K | multi-source |
| Graph edge lookups / feed | hundreds | hundreds–thousands | must cache | edge cells |
| Cache hit rate target (post) | 90%+ | 95%+ | 98%+ | edge POP |

**What each jump forces:**

- **10×:** Hybrid fan-out mandatory; timeline cache; post object cache; async fan-out workers.  
- **100×:** User/home cells; celebrity pull everywhere above threshold; ranking feature cache; graph edge cache (TAO-like).  
- **1,000×:** Multi-source candidate services; edge feed assembly; strict celebrity/hybrid policies; ranking SLO budgets with early-exit.

### 1.5 Etc. (Constraints & Assumptions)

- Social **graph** exists (follow/friend edges); we design feed, not the entire graph product.  
- Media bytes live in **blob/CDN** (URLs only in feed).  
- Ranking is a **black-box scorer** with feature retrieval — we design the infra contract, not train the model.  
- Meta flavor: think **memcache-heavy**, **graph-aware caching**, **async fan-out fleets**, **home region**.  
- Ads/Reels can consume the same candidate→rank→hydrate pipeline shape later.

**Scope statement to repeat back:**

> Design a Facebook-style News Feed: durable posts, hybrid write/read fan-out with celebrity pull, candidate generation + ML ranking + hydration, multi-tier caching, privacy filters, and progressive scale through 10× / 100× / 1,000× without ever pushing a single post to tens of millions of timelines synchronously.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Post creates** | Durable write | ~5K/s | ~50K/s | Post DB / log |
| **Fan-out inserts** | Timeline entries | creates × avg followers (capped) | ×10 | Timeline store |
| **Feed reads** | Assemble timeline | ~100K/s | ~1M/s | Cache + ranker |
| **Graph edge reads** | Followers / friends | amplified by feed | ×10 | Graph cache |
| **Post hydrates** | Get post objects | reads × page size | ×10 | Post cache |
| **Ranking QPS** | Score candidates | ≈ feed reads | ×10 | Ranker fleet |
| **Counter updates** | Likes/comments | >> creates | ×10 | Counter shards |

**Anti-pattern:** one “write QPS” that mixes post create, fan-out amplification, and like counters.

### 2.2 Fan-out amplification math

```text
Baseline peak creates: 5,000 posts/s
If NAIVE push to all followers with avg 200 followers:
  fan-out writes = 5,000 × 200 = 1,000,000 timeline inserts/s

But distribution is skewed:
  Most users: 50–500 followers → push OK
  Celebs: 1M–100M followers → NEVER full push

Hybrid:
  Push only if followers < T (e.g. 10K)
  Fraction of posts from celebs: small by count, huge by followers

Example:
  99% of posts from users < 10K followers, avg push 150
  1% celebrity posts: 50 posts/s — pull path, 0 push
  Push inserts ≈ 0.99 × 5000 × 150 ≈ 742,500 /s at peak

Still large → batch writes, async workers, sharded timelines.
```

**Deal-breaker:** proposing synchronous fan-out to all followers of a celebrity in the request path.

### 2.3 Read path math

```text
Peak feed QPS: 100K
Page size: 10 posts
Candidates before rank: 1,000 (retrieve then rank top 10–50)

If every candidate hydrate is a DB hit:
  100K × 1,000 = 100M gets/s → impossible

With post cache 95% hit:
  origin post gets ≈ 100K × 10 × 0.05 = 50K/s (hydrate only winners)
  OR hydrate after rank (correct): hydrate ~10–20 IDs / request
  origin ≈ 100K × 15 × 0.05 = 75K/s — still need cache

Graph: "who do I follow?" cached per user; fan-out lists cached.
```

### 2.4 Storage

```text
Posts: 5K/s × 86,400 ≈ 432M posts/day
× 2 KB ≈ 864 GB/day raw metadata (order)
× 365 ≈ ~300 TB/year metadata before replication/indexes
Media: separate blob plane — TBs–PBs/day; out of feed metadata math

Timeline entries (push):
  ~7.5e5 inserts/s peak; avg much lower
  Daily timeline rows: order of tens–hundreds of billions at large scale
  Retention: keep recent N per user (e.g. 1K–5K) + archive/cold

Must: TTL/trim timelines; not unbounded growth per user.
```

### 2.5 Bandwidth / payload

```text
Feed response ~20–50 KB JSON compressed for 10 posts (IDs + light fields)
100K QPS × 30 KB ≈ 3 GB/s egress edge — CDN/edge terminates TLS
Media thumbnails via CDN separately (dominant bandwidth)
```

### 2.6 Ranking latency budget

```text
Total p99 budget 500ms example split:
  Auth + routing: 10ms
  Candidate retrieval (cached timeline + pulls): 50–100ms
  Feature fetch: 50–100ms
  Model score: 20–50ms
  Hydrate + privacy: 30–50ms
  Network: remainder
Over budget → shrink candidates, cache features, early-exit, or chrono fallback.
```

### 2.7 Progressive BOTE summary

| Scale | Creates/s | Naive push inserts/s | Hybrid push inserts/s | Feed QPS |
|-------|-----------|----------------------|-----------------------|----------|
| Baseline | 5K | ~1M | ~0.5–0.8M | 100K |
| 10× | 50K | ~10M | ~5–8M | 1M |
| 100× | 500K | ~100M | cells + stricter T | 10M |
| 1,000× | 5M | fantasy | geo cells + pull-heavy | 100M |

### 2.8 Memory footprints (timeline + features)

```text
Timeline entry ~24–40B (post_id, ts, flags)
Active user hot segment 2K entries × 32B ≈ 64KB
50M concurrent actives × 20% cached ≈ 640GB Redis order — sharded by viewer_id

Feature vectors for ranking (online):
  500 candidates × 1KB features = 500KB/request ephemeral
  Feature store cache hit critical — miss storm = p99 death

Graph cache: following list avg 500 ids × 8B = 4KB/user hot
```

### 2.9 Partition counts & amplification cost

```text
Kafka PostCreated: key author_id; partitions 512→8K
Timeline store: owner_id % N; N=256 baseline → 4K+
Celebrity threshold T: if 1% authors above T produce 50% impressions, pull path must be fat

Naive push inserts/s ≈ creates/s × avg_followers
  5K × 200 = 1M/s baseline already — hybrid mandatory in narrative
Cost of pure pull: read QPS × following × lookup — also death without caches
```

### 2.10 Cache stampede & payload math

```text
Viral post hydrate: 1M users request same post object
  singleflight / lease + CDN for media + object cache with soft TTL
Feed JSON page ~50 posts × 2KB hydrated ≈ 100KB — compress; don’t embed video bytes
```

### 2.11 Progressive implications card

| Jump | Forced change |
|------|---------------|
| 10× | Hybrid T, timeline cache, async fanout |
| 100× | Cells, ranker fleet, feature cache, celebrity storms playbook |
| 1,000× | Geo home cells, pull-heavier, edge media, stricter candidate caps |

**Pitch:** “Facebook feed = hybrid fan-out + ranked assemble. Push for normal; pull celebrities; never sync fanout in create API.”


---

## 3. High-Level Design

### 3.1 APIs

#### 3.1.1 Create post

```http
POST /v1/posts
Idempotency-Key: <uuid>
Authorization: Bearer ...
{
  "text": "Hello",
  "media_ids": ["m1"],
  "audience": "friends",
  "client_ts": 1720000000
}

→ 201
{
  "post_id": "p_...",
  "created_at": "...",
  "visibility": "friends"
}
```

#### 3.1.2 Get feed

```http
GET /v1/feed?limit=10&cursor=<opaque>
→ 200
{
  "items": [
    {
      "post_id": "p_...",
      "author_id": "u_...",
      "text": "...",
      "media": [...],
      "stats": {"likes": 12, "comments": 3},
      "rank_score": 0.91,
      "reason": "friend_post"
    }
  ],
  "next_cursor": "..."
}
```

#### 3.1.3 Delete / edit

```http
DELETE /v1/posts/{post_id}
PATCH /v1/posts/{post_id}  {"text": "edited"}
```

#### 3.1.4 Social graph (assumed existing)

```http
GET /v1/graph/{user_id}/followers?cursor=
GET /v1/graph/{user_id}/following?cursor=
POST /v1/graph/{user_id}/follow
```

### 3.2 Core data model / schema

**posts**

| Column | Type | Notes |
|--------|------|-------|
| post_id | snowflake | PK |
| author_id | i64 | indexed |
| text | text | |
| media_ids | json/array | blob refs |
| audience | enum/json | privacy |
| created_at | ts | |
| deleted_at | ts null | tombstone |
| version | int | edits |

**timelines** (per-user materialized inbox for push)

| Column | Type | Notes |
|--------|------|-------|
| owner_id | i64 | shard key |
| post_id | snowflake | |
| author_id | i64 | denorm for filters |
| created_at | ts | sort key |
| rank_hint | float null | optional pre-score |

PK/SK: `(owner_id, created_at DESC, post_id)`

**celebrity_posts** (pull index)

| Column | Type | Notes |
|--------|------|-------|
| author_id | i64 | shard key |
| post_id | snowflake | |
| created_at | ts | |

**counters**

| Column | Type | Notes |
|--------|------|-------|
| post_id | snowflake | |
| likes | i64 | sharded counters |
| comments | i64 | |

**Why this schema:** timeline is optimized for “recent posts for user U”; celebrity index optimized for “recent posts by author A”; posts are source of truth.

### 3.3 Why X over Y

| Decision | Choose | Over | Why | Deal-breaker if wrong |
|----------|--------|------|-----|------------------------|
| Fan-out | **Hybrid** | Pure write or pure read | Skew makes pure write explode; pure read too slow | Sync push to 100M followers |
| Timeline store | **Cassandra/Dynamo-like** | Single MySQL | Wide fan-out writes, partition by user | Global secondary scans for feed |
| Graph | **Cached graph (TAO-like)** | Join SQL every request | Edge QPS enormous | Uncached follower walk at feed QPS |
| Ranking | **Retrieve → rank → hydrate** | Rank all posts in DB | Candidate set must be bounded | Score entire social corpus online |
| Cache | **Multi-tier (post, timeline, edges)** | Only CDN HTML | Personalized; object cache critical | DB as primary read path |
| Privacy | **Filter at serve** | Trust fan-out only | Edges/audience change | Leak private post via stale timeline |
| Celebs | **Pull on read** | Push everywhere | Math | Timeline write amplification |
| Consistency | **RYW for author; eventual for others** | Global linearizability | Cost/latency | Cross-region sync create |

### 3.4 Component overview

1. **API Gateway / Feed Service** — auth, create, get feed.  
2. **Post Service + Post DB** — source of truth.  
3. **Fan-out Service** — consumes post-created events; writes timelines for non-celebs.  
4. **Celebrity Detector** — followers count / tier flags.  
5. **Timeline Store** — per-user inbox.  
6. **Candidate Service** — merge push timeline + pull celebs + optional groups.  
7. **Ranker** — ML + heuristics.  
8. **Hydration / Object Cache** — posts, users, counters, media URLs.  
9. **Graph Service + Edge Cache** — following/followers.  
10. **Privacy Filter** — audience check.  
11. **Kafka/Pulsar** — post events, invalidations.  
12. **CDN** — media only (and maybe static).

### 3.5 End-to-end flows

**Create (normal user):**

```text
Client → API → Post Service (durable) → ACK client
                 → Kafka post_created
Fan-out workers → fetch followers (paged) → batch insert timelines
                → invalidate author caches
```

**Create (celebrity):**

```text
Client → API → Post Service → ACK
                 → Kafka → write celebrity_posts index only
                 → NO per-follower timeline insert
```

**Read feed:**

```text
Client → Feed Service
  → get following list (cache)
  → read owner timeline (push candidates)
  → for celebrity followees: read celebrity_posts (pull)
  → merge/dedup → privacy filter → rank → hydrate → respond
```

### 3.6 Consistency model (explicit)

| Object | Model | Notes |
|--------|-------|-------|
| Create post | Strong author home | Idempotent |
| Timeline push | Eventual | Seconds OK |
| Ranked feed | Non-deterministic OK | Model versions |
| Privacy/delete | Must converge | Tombstone > cache |
| Counters | Approx | Side service |

**Deal-breaker:** showing deleted/blocked content because timeline cache ignored invalidation.

### 3.7 API edge cases

| Case | Behavior |
|------|----------|
| Idempotent recreate | Same post_id |
| Delete during fanout | Tombstone wins on read |
| Unfollow race | Filter graph at assemble |
| Ranker timeout | Chrono fallback |
| Empty candidate set | Follow recommendations hook |
| Cursor mash after rank change | Cursor carries opaque rank epoch |

### 3.8 Schema indexes (expanded)

```text
posts: PK(post_id); INDEX(author_id, created_at DESC); soft_delete flag
timelines: ((owner_id), ts DESC, post_id) — wide-row / clustered
fanout_cursors: (author_id, post_id, shard) for resume
privacy: audience enum on post; edges block/mute
```

### 3.9 Why X over Y expanded

| Topic | Prefer | Avoid |
|-------|--------|-------|
| Fanout | Hybrid | Pure push or pure pull alone at Meta scale |
| Rank | Candidate→features→model | Rank entire social graph |
| Cache | IDs + hydrate | Full HTML CDN |
| Privacy | Filter on read + invalidate | Trust timeline forever |
| Create API | Enqueue fanout | Sync 1M writes |

### 3.10 HLD pitch

> “Create enqueues fanout; workers push to non-celebrity followers; feed read merges push timeline + celebrity pull, ranks, privacy-filters, hydrates. Caches are layered; deletes/blocks invalidate. Scale with T, cells, and candidate caps.”


---

## 4. Architecture Diagram

```text
                        +------------------+
                        |     Clients      |
                        |  (iOS/Android/Web)|
                        +--------+---------+
                                 |
                                 v
                        +------------------+
                        |   API Gateway    |
                        +--------+---------+
                                 |
                 +---------------+---------------+
                 |                               |
                 v                               v
        +----------------+              +------------------+
        |  Post Service  |              |   Feed Service   |
        +--------+-------+              +--------+---------+
                 |                               |
                 v                               |
        +----------------+                       |
        |   Post Store   |                       |
        | (multi-AZ DB)  |                       |
        +--------+-------+                       |
                 |                               |
                 v                               v
        +----------------+              +------------------+
        |  Kafka bus     |              | Candidate Merge  |
        | post_created   |              | push∪pull∪...    |
        +--------+-------+              +--------+---------+
                 |                               |
        +--------+--------+                      v
        |                 |             +------------------+
        v                 v             | Ranker + Features|
 +-------------+   +-------------+      +--------+---------+
 | Fan-out WQ  |   | Celeb Index |               |
 | → Timelines |   | (pull path) |               v
 +------+------+   +-------------+      +------------------+
        |                               | Privacy + Hydrate|
        v                               | Post/Edge Cache  |
 +-------------+                        +--------+---------+
 | Timeline DB |                                 |
 | shard(user) |                                 v
 +-------------+                        +------------------+
                                        |   JSON Feed      |
                                        +------------------+

 Cross-cutting:
   Graph Service / Edge Cache (TAO-like)
   Counter Service (likes/comments)
   Blob/CDN for media
   Home-region / cell routing
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Post durable before client ACK** — lose fan-out OK (retry); lose ACK’d post not OK.  
2. **Privacy checked at serve time** — timeline membership ≠ authorization.  
3. **Fan-out idempotent** on `(owner_id, post_id)`.  
4. **Celebrity posts never require O(followers) sync writes**.  
5. **Degraded feed > empty feed** — chrono fallback if ranker dies.  
6. **Author read-your-write** — creator sees own post immediately (sticky cache / home).

#### 5.1.2 Fan-out delivery reliability

| Failure | Mitigation |
|---------|------------|
| Worker crash mid-followers | Checkpoint follower cursor; resume; idempotent inserts |
| Timeline shard down | Retry with backoff; quarantine shard; alert |
| Kafka lag | Expose freshness metric; product “uploading” already done |
| Poison post | DLQ; skip bad payloads |

**At-least-once** fan-out + idempotent timeline writes is the practical Meta-style answer.

#### 5.1.3 Cache coherence

Stale private post in cache is a **privacy incident**.

```text
On privacy change / delete:
  - Update Post Store (SoT)
  - Publish invalidation (post_id)
  - Caches drop or mark tombstone
  - Serve path re-fetches SoT on miss; filters deleted
```

Short TTL alone is **not** enough for deletes/privacy — need active invalidation.

#### 5.1.4 Ranking failures

| Mode | Behavior |
|------|----------|
| Ranker timeout | Heuristic: recency × affinity |
| Feature store down | Use cached features / defaults |
| Bad model | Kill switch → previous model or chrono |

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Fan-out lag | More workers; batch inserts |
| 10× | Hot timeline shards | Re-shard; request coalescing |
| 100× | Celeb pull storms | Celebrity post cache; early materialize top posts |
| 1,000× | Global thundering herds | Edge aggregation; home cells; adaptive celebrity threshold |

#### 5.1.6 Idempotency, retries, backoff

```text
Fanout task key: (post_id, follower_shard)
Retry with jitter; poison shard → DLQ + alert
Create API returns after durable post + outbox, not after fanout complete
```

#### 5.1.7 Data-loss prevention

1. Post + outbox atomic.  
2. Timeline writes idempotent.  
3. Tombstones retained.  
4. Redis cache never sole store.

#### 5.1.8 Consistency under partition

```text
Author home vs follower cell lag: eventual — OK
Privacy service down: fail closed (hide) not open
Ranker down: chrono
```

### 5.2 Scalability

#### 5.2.1 Hybrid fan-out deep dive

```text
on_post_created(post):
  n = follower_count(author)
  if n < T:
    enqueue_push(post, followers_pages)
  else:
    write_celebrity_index(post)
    maybe_partial_push(online_friends_sample)  # optional optimization

on_feed_read(user):
  push = read_timeline(user, limit=M)
  celebs = following_celebs(user)
  pull = ∪ read_celebrity_index(c, since)
  candidates = merge(push, pull, other_sources)
```

**Choosing T:**

- Too low → too much pull latency.  
- Too high → timeline write amplification.  
- Dynamic T by region/load is advanced E5 answer.

**Partial push optimization:** push to currently-online followers or “close friends” subset; others pull — reduces perceived lag without full O(N).

#### 5.2.2 Timeline storage

- Partition by `owner_id`.  
- Keep last N entries (e.g. 1000); trim async.  
- Wide rows / time-series OK (Cassandra pattern).  
- Secondary: cold archive rarely needed for feed UX.

#### 5.2.3 Candidate generation at scale

Sources:

1. Push timeline (friends).  
2. Celebrity pull.  
3. Groups / pages (Phase 1.5).  
4. Suggested / inventory (later).

Merge with **dedup by post_id**, soft time bounds (e.g. last 7–30 days for backfill).

#### 5.2.4 Ranking pipeline

```text
candidates (IDs)
  → fetch lightweight features (author affinity, edge type, post age, CTR priors)
  → score (model or GBDT)
  → diversity rules (not 10 from same author)
  → top K for page
  → hydrate heavy fields
```

**Deal-breaker:** hydrating full post bodies for 2K candidates before ranking.

#### 5.2.5 Caching tiers (Meta flavor)

| Tier | What | TTL / invalidation |
|------|------|--------------------|
| L1 in-process | Hot post IDs, user following | seconds; singleflight |
| L2 memcache/redis | Post objects, timelines, edges | seconds–minutes; pub invalidation |
| L3 regional | Replicated hot objects | |
| CDN | Media binaries | long; cache-busted URLs |

**TAO-like graph cache:** association lists (`following`, `followers`) with lease/version; feed never walks MySQL at QPS.

#### 5.2.6 Celebrity storms

When a mega-celebrity posts:

- Pull index is one write.  
- Millions of feeds concurrently pull same post → **post object cache** must hold; use **request coalescing**.  
- Optionally **push to leaf caches** / edge for that post_id.  
- Ranker features for that post cached aggressively.

#### 5.2.7 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Hybrid fan-out; async workers; post+timeline cache |
| →100× | Home cells; graph edge cache; celebrity pull default above T; feature cache |
| →1,000× | Multi-source candidates; edge feed; adaptive T; ranking early-exit; counter fleets |

#### 5.2.8 Queue backpressure

```text
Fanout lag SLO burn → increase workers; raise effective T (more pull); drop low-priority densify jobs
Never block create API on fanout depth
```

#### 5.2.9 Read/write evolution table

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Create | outbox | sharded posts | home cell |
| Fanout | hybrid | online subset push | geo cells |
| Read | cache+rank | feature cache | candidate caps+edge |
| Inval | pubsub | buffered | cell bus |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
celebrity_threshold_followers: 10000
timeline_retain: 2000
candidate_limit: 1500
ranker_timeout_ms: 80
fallback: chronological
fanout_batch_size: 500
privacy_recheck: true
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `post_create_qps` | Write load |
| `fanout_lag_seconds` | Freshness |
| `fanout_inserts_per_s` | Amplification |
| `feed_p99_ms` | UX |
| `ranker_p99_ms` | Budget |
| `cache_hit_ratio{object}` | DB protection |
| `celebrity_pull_qps` | Hot path |
| `privacy_filter_drops` | Correctness / abuse |
| `timeline_trim_lag` | Storage health |

#### 5.3.3 Safe evolution

Phase 1: chronological push-only for small graph.  
Phase 2: hybrid + heuristic rank.  
Phase 3: ML ranker + feature store.  
Phase 4: cells + multi-source + ads slots.

#### 5.3.4 Testing

- Fan-out idempotency fixtures.  
- Privacy regression suite (must-not-leak).  
- Celebrity threshold load tests.  
- Ranker canary with offline AUC + online A/B.  
- Chaos: kill fan-out, kill ranker — feed still serves.

### 5.4 Ranking pipeline deep dive

```text
retrieve K1 from timeline + pulls
light rank → K2
heavy model → K3
diversity/rules → page
hydrate posts/users/counters
privacy last chance filter
```

**Latency:** miss budgets → skip heavy model.

### 5.5 Privacy & invalidation

```text
Events: delete, edit audience, block, unfollow, report-remove
Invalidate: post object, timeline entries (tombstone), feed caches by viewers best-effort
Read path must re-check block/delete even if timeline has id
```

### 5.6 Progressive architecture evolution

| Stage | Fanout | Rank | Cache |
|-------|--------|------|-------|
| MVP | push | chrono | Redis timeline |
| Prod | hybrid | 2-stage | +post objects |
| Meta-scale | cells | ML + rules | TAO-like graph cache |


---

## 6. Wrap-Up

### 6.1 What we designed

A **Facebook-style News Feed** with durable posts, **hybrid fan-out** (push for normal users, pull for celebrities), candidate merge, ML ranking with latency budgets, multi-tier caching (posts/timelines/edges), serve-time privacy checks, and progressive scale via home cells and adaptive celebrity thresholds.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Fan-out | Hybrid; never sync push megafollowers |
| Ranking | Retrieve → rank → hydrate |
| Privacy | Always re-check at serve |
| Cache | Objects + edges + timelines; invalidate deletes |
| Scale | Amplification math first, then boxes |

### 6.3 Closing line

> “Feed is a fan-out and caching problem first, a ranking problem second—if you push every celebrity post to 100M timelines, no ranker will save you.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Fan-out

**Q1: Write fan-out vs read fan-out?**  
A: Write (push) materializes per-follower timelines at create time — fast reads, expensive writes. Read (pull) gathers from followees at read time — cheap writes, expensive reads. Hybrid uses push below threshold T and pull above.

**Q2: Why not always push?**  
A: Celebrity posts create O(followers) writes; 100M followers → impossible sync amplification and huge storage churn.

**Q3: Why not always pull?**  
A: Users following 500 accounts → 500 recent-post fetches per feed open; p99 explodes without heavy caching and still hurts.

**Q4: How do you pick threshold T?**  
A: Balance push write QPS vs pull read fan-in; start ~10K followers; tune with metrics; make dynamic under load.

**Q5: Is fan-out synchronous in the create API?**  
A: No — durable post + ACK, then async workers. UX “posted” ≠ “all friends materialized.”

**Q6: Idempotency of fan-out?**  
A: Key timeline inserts by `(owner_id, post_id)`; resume follower pagination cursors on retry.

**Q7: Partial push optimization?**  
A: Push to online users or high-affinity subset; others see via pull — improves perceived freshness without full O(N).

### 7.2 Ranking

**Q8: Where does ranking run?**  
A: After candidate retrieval, before heavy hydration; bounded candidate set (hundreds–thousands).

**Q9: What if ranker is slow?**  
A: Timeout → heuristic/chrono fallback; never block forever; track SLO burn.

**Q10: Feature retrieval cost?**  
A: Prefetch/cache user affinity and post priors; avoid per-candidate remote calls without batching.

**Q11: Diversity rules?**  
A: Post-score re-rank: limit consecutive same author, similar media, etc.

**Q12: Offline vs online models?**  
A: Train offline; serve online with versioned models; canary + kill switch.

### 7.3 Caching

**Q13: What do you cache?**  
A: Post objects, timeline pages/IDs, following lists, celebrity recent posts, counters, ranking features.

**Q14: Cache stampede on viral post?**  
A: Singleflight/coalescing; hot-key replication; soft TTL + probabilistic early refresh.

**Q15: Invalidation on delete?**  
A: SoT delete + pub/sub invalidation + tombstone; serve filters deleted_at.

**Q16: Why not CDN the feed HTML?**  
A: Highly personalized; CDN media and maybe anonymous edges; feed JSON from app caches.

### 7.4 Privacy & correctness

**Q17: Can timeline contain a post the viewer shouldn’t see?**  
A: Yes briefly — always enforce audience at serve; treat timeline as hint/index.

**Q18: Unfollow race?**  
A: May still show until cleanup; filter following set on read; async remove from timeline.

**Q19: Edit post text?**  
A: Bump version; invalidate post cache; timelines keep ID only so body updates on hydrate.

### 7.5 Storage & schema

**Q20: Why partition timeline by owner_id?**  
A: All reads for a user hit one shard set; write fan-out spreads across many owners (expected).

**Q21: How large is a timeline?**  
A: Cap to last N posts (e.g. 1K–5K); trim; feed doesn’t need infinite history in hot store.

**Q22: Counters consistency?**  
A: Eventual; sharded adders; display approximate OK; reconcile async.

### 7.6 Scale & Meta flavor

**Q23: What is TAO-like thinking here?**  
A: Graph edges are association lists with aggressive caching; feed depends on cached `following` not SQL joins.

**Q24: Home region / cells?**  
A: User stickiness to a region/cell for RYW and cache locality; cross-region friends via async replication.

**Q25: 10× vs 100× biggest shift?**  
A: 10× introduces hybrid+cache; 100× forces cells, edge caches, and pull-dominant celebs as default architecture.

**Q26: Deal-breakers list?**  
A: Sync celebrity push; hydrate-before-rank; trust fan-out for privacy; uncached graph walks; unbounded timelines.

**Q27: How do likes appear on feed cards?**  
A: Counter service; batch get on hydrate; cache with short TTL; not on critical create path.

**Q28: Pagination cursors?**  
A: Opaque `(rank_ts, post_id)` or offset into ranked session; handle deletes by skipping missing IDs.

**Q29: Groups in feed?**  
A: Separate candidate source with its own fan-out/pull; merge in candidate service; ranking weights source.

**Q30: Ads slots?**  
A: Reserve positions in final list; ads auction separate; enforce min gaps; failure → organic-only.

**Q31: Soft vs hard delete?**  
A: Soft delete/tombstone for cache races; GC later; hard delete media via blob lifecycle.

**Q32: Measuring fan-out lag?**  
A: `now - post.created_at` when timeline insert completes for sampled followers; alert on p99.

**Q33: Hot shard from celebrity’s close friends?**  
A: Still pull for celeb content; friends’ own timelines unaffected; post cache absorbs hydrate load.

**Q34: Chronological mode?**  
A: Skip ML ranker; merge candidates by `created_at`; still privacy filter + hydrate.

**Q35: Multi-media posts?**  
A: Store media_ids; CDN signed URLs at hydrate; feed meta stays small.

### 7.7 Quick-fire tradeoffs

**Q36: Redis vs Cassandra for timelines?**  
A: Redis for hot recent IDs; Cassandra/Dynamo for durable longer timelines — often both (hot + warm).

**Q37: Push notifications vs feed fan-out?**  
A: Different systems; notification is sampled/priority; don’t couple to full timeline materialization.

**Q38: Exactly-once fan-out?**  
A: Prefer at-least-once + idempotent inserts; exactly-once frameworks optional, not required for MVP story.

---

### 7.8 Algorithms & memory

**Q39: How do you bound candidate set size?**  
A: Cap K1 from timeline (e.g. 500–2000) + celebrity pulls capped; diversity later.

**Q40: Skip list vs Cassandra wide row for timeline?**  
A: Both OK; key is owner_id clustering + trim; Redis as cache layer.

**Q41: Consistent hashing for timeline shards?**  
A: Yes for owner_id; virtual nodes; reshard with dual-read/write.

**Q42: How to compute online/offline push subset?**  
A: Presence service sample; push only recently active; others pull densify later.

### 7.9 Failure modes & LB

**Q43: Load balancer for feed API?**  
A: L7; stickiness not required if session in token; cell routing by user home.

**Q44: Hot partition from viral author close friends?**  
A: Salt fanout shards; separate celebrity path entirely.

**Q45: What if invalidation bus drops deletes?**  
A: Read-time delete check against source of truth; TTL caches short.

### 7.10 Estimation extras

**Q46: Memory for 1B users × 1KB feed cache?**  
A: 1PB — impossible; cache only active cohort segments.

**Q47: Pure push at 500K creates/s × 300 followers?**  
A: 150M inserts/s — deal-breaker; hybrid/cells.

### 7.11 Meta interview closer Qs

**Q48: What would you cut in 30 minutes?**  
A: ML rank details; keep hybrid fanout + privacy + cache + scale jumps.

**Q49: TAO analogy?**  
A: Graph association reads cached; feed is association + ranked objects.

**Q50: Deal-breaker list again?**  
A: Sync fanout; pure push celebrities; HTML CDN feed; no tombstones; counters on post PK row.


### Appendix A — Celebrity decision pseudocode

```text
def on_post_created(post):
  n = graph.follower_count(post.author_id)
  if n >= CELEB_T:
    celeb_index.write(post.author_id, post)
    metrics.celeb_posts.inc()
  else:
    fanout.enqueue(post, page_size=500)
```

### Appendix B — Feed assemble pseudocode

```text
def get_feed(user, cursor, limit):
  following = graph.following_cached(user)
  celebs, normals = split_by_tier(following)
  push = timeline.read(user, cursor_hint=cursor, limit=CAND_N)
  pull = []
  for c in celebs:
    pull.extend(celeb_index.recent(c, since=window))
  cands = dedup(push + pull)
  cands = privacy.filter(user, cands)
  ranked = ranker.score(user, cands, timeout=80ms) or chrono(cands)
  page = ranked[:limit]
  return hydrate(page), next_cursor(ranked, limit)
```

### Appendix C — Latency budget card

```text
p99 500ms:
  route 10 | candidates 100 | features 100 | score 50 | privacy+hydrate 80 | misc 160
```

### Appendix D — Progressive scale table

| Scale | Fan-out | Store | Rank | Cache |
|-------|---------|-------|------|-------|
| Baseline | Hybrid | Timeline+Post | Heuristic | Memcache |
| 10× | Async fleets | Trim N | ML v1 | + features |
| 100× | Cells | Per-cell Kafka | Feature store | Edge hot posts |
| 1,000× | Adaptive T | Multi-source | Early-exit | POP assemble |

### Appendix E — Privacy matrix

| Audience | Who can see |
|----------|-------------|
| public | anyone |
| friends | edge friends |
| friends_except | friends − list |
| only_me | author |
| custom | list membership |

Always evaluate against **current** graph + audience, not fan-out-time snapshot alone.

### Appendix F — Invalidation events

| Event | Action |
|-------|--------|
| post_deleted | tombstone + invalidate post + optional timeline scrub |
| audience_changed | invalidate post; filter on read |
| user_blocked | filter author on read; async cleanup |
| unfollow | filter; async timeline delete |

### Appendix G — BOTE worked example

```text
5K posts/s, 99% push avg 150 followers:
  push = 0.99*5000*150 ≈ 742.5K inserts/s
Worker batch 500 → ~1.5K batch writes/s meta — still need many workers/shards
Feed 100K QPS × 15 hydrates × 5% miss = 75K post DB QPS → size caches for >95% hit
```

### Appendix H — Deal-breaker checklist

1. Sync push to megafollowers  
2. Hydrate-before-rank  
3. Privacy only at fan-out  
4. Uncached following walk  
5. Unbounded timeline retention  
6. Single global SQL for all timelines  

### Appendix I — Ranking features (examples)

| Feature | Source |
|---------|--------|
| viewer–author affinity | interactions |
| post age decay | created_at |
| media type | post meta |
| like velocity | counters |
| viewer interests | profile |
| edge type (friend vs follow) | graph |

### Appendix J — NFR card

```text
Create p99 < 200ms durable
Feed p99 < 500ms
Fan-out normal < 5s p99
Celebrity: pull, no O(N) push
Privacy: serve-time enforce
Degrade: chrono if ranker down
```

### Appendix K — Comparison: pure push vs pure pull vs hybrid

| Property | Pure push | Pure pull | Hybrid |
|----------|-----------|-----------|--------|
| Create cost | O(followers) | O(1) | O(min(followers,T)) |
| Read cost | O(page) | O(following) | O(page + celebs) |
| Celebrity | Breaks | OK | OK |
| Normal users | Great | OK-ish | Great |
| Meta choice | — | — | **Yes** |

### Appendix L — Timeline trim

```text
retain last N=2000 per owner
async scanner / write-time drop oldest
never rely on infinite hot history
```

### Appendix M — Graph cache sketch

```text
assoc (user_id, ASSOC_FOLLOWING) -> [ids...] with version
on follow/unfollow: update SoT + bump version + invalidate cache key
feed reads: get cached list; if version mismatch, refresh
```

### Appendix N — Home cell routing

```text
user_id → cell = hash(user_id) % N  or geo home
create/read sticky to home for RYW
cross-cell friends: async replicate posts needed for pull indexes
```

### Appendix O — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just use Redis timelines” | Durability + size; Redis hot layer OK |
| “Pull everything” | p99 with 500 followees |
| “Push everything” | Celebrity math |
| “SQL JOIN friends×posts” | Won’t survive QPS |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Fan-out | Propagating a post to followers’ indexes |
| Hybrid | Push small, pull celebs |
| Hydration | Fetch full objects for IDs |
| Timeline | Per-user materialized inbox |
| Celebrity threshold T | Followers above → pull path |
| TAO-like | Cached graph association store |

### Appendix Q — 30m interview checklist

1. Clarify ranked vs chrono, privacy, celebs.  
2. BOTE: create × followers amplification.  
3. Draw hybrid fan-out + candidate→rank→hydrate.  
4. Deep dive celebrity + cache + privacy.  
5. Walk 10×/100×/1,000×.  
6. List deal-breakers.

### Appendix R — Soft delete flow

```text
DELETE post → set deleted_at
publish invalidate(post_id)
caches drop
feed hydrate sees deleted → skip
optional: scrub timelines async
```

### Appendix S — Counter sharding

```text
likes[post_id] = Σ likes[post_id#shard]
increment random shard; read sums (cached)
```

### Appendix T — Cursor design

```text
cursor = base64(last_score, last_post_id, session_id)
next page continues; if session expired, re-rank from fresh candidates
```

### Appendix U — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Hybrid, async fan-out, object cache |
| 100× | Cells, graph cache, feature cache |
| 1,000× | Adaptive T, edge assemble, multi-source |

### Appendix V — Meta interview closing

> “I’d start hybrid fan-out with serve-time privacy, cache posts and edges aggressively, and keep ranking behind a tight latency budget with chronological fallback—then scale with user cells and adaptive celebrity thresholds.”

---


## Appendix W — Anti-patterns (deepened)

| Anti-pattern | Why | Instead |
|--------------|-----|---------|
| Sync fanout in create | Latency/availability | Outbox+workers |
| Pure push mega-celeb | Write amp death | Pull |
| Rank all friends every request | CPU death | Candidate caps |
| Cache without privacy recheck | Leaks | Filter on read |
| Redis-only timeline | Loss | Durable+cache |
| Ignore fanout lag | Stale social | SLO+degrade |

## Appendix X — 90s pitch

> “Hybrid fan-out feed: durable post, async push to normal followers, pull celebrities at read, rank with bounded candidates, privacy filter always-on, layered caches. 10× forces hybrid+cache; 100× cells+feature cache; 1,000× geo homes and pull-heavy.”


*End of Facebook News Feed system design.*
