# System Design: Instagram (Microsoft Interview Practice)

> **Focus areas:** Posts · Media pipeline · Follow graph · Home feed · Hybrid fanout · Celebrity hot keys · CDN · Ranking hooks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct fanout arithmetic, explicit hybrid feed strategy, deal-breakers for “JOIN follows×posts on every home scroll” fantasies  
> **Interview theme:** Microsoft loop (team may ask domain problems) — Instagram-class social is a common public-bank prompt; frame reliability, clean APIs, and scale jumps the way Azure/M365 teams expect ownership

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

Goal: **bound the product**—Instagram-class social: users **follow** creators, publish **photo/video posts**, consume a **home feed**, view profiles, and handle **celebrity mega-fanout**—with media via CDN and progressive scale. In a Microsoft interview, lock scope early: teams often care that you can say what you will *not* build (Reels research ranker, Shopping, Live) and still show a production-grade path for feed + media.

### 1.0 What this is / is not

| Dimension | **Instagram (this doc)** | Not this |
|-----------|--------------------------|----------|
| Primary job | Graph + posts + media + home feed | Full TikTok For-You research / IG Shopping mall |
| Success | Fast publish; fresh relevant feed; reliable media | Perfect global ML paper |
| Media | Upload → process → CDN | Inventing codecs |
| Feed | Hybrid fanout + ranking hooks | Pure SQL join-on-read at Meta/IG scale |
| Stories / DMs / Live | Hooks / Phase 1.5 | Full designs each |
| Microsoft lens | APIs, reliability, regional cells, abuse hooks | Azure-only product requirement |

**Scope statement:** Design Instagram-like posts, media, follows, and feed generation—scaling through 10× / 100× / 1,000× with celebrity-aware fanout.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Graph model? | Directed follow (A follows B) | Adjacency lists + follower/following counts |
| F2 | Post types? | Image + short video MVP; carousel Phase 1.5 | Media pipeline + post metadata |
| F3 | Home feed? | Ranked with chronological fallback | Fanout store + ranker hook |
| F4 | Profile grid? | User’s posts reverse chronological | Author-indexed post list |
| F5 | Celebrity / mega creators? | Accounts with millions of followers | Hybrid fanout mandatory |
| F6 | Likes / comments? | Yes, light MVP | Counter service + comment service |
| F7 | Notifications? | Follow / like / comment | Notification service (async) |
| F8 | Search? | Users MVP; hashtags Phase 1.5 | Search index separate from feed |
| F9 | Privacy? | Public + private accounts | Follow approval; ACL on read + fanout |
| F10 | Stories? | Phase 1.5 | 24h TTL store; not home feed |
| F11 | DMs? | Out of MVP | Mention only |
| F12 | Ads? | Out of MVP core | Feed injection / mixer hook |
| F13 | Explore / Discover? | Phase 1.5 | Candidate retrieval service |
| F14 | Soft delete / report? | Yes | Tombstones + Trust & Safety queue |

**MVP functional scope (lock with interviewer):**

1. Auth, profiles, follow / unfollow (public; private approve Phase 1.5).  
2. Upload media → process variants → create post.  
3. Home feed of followed accounts (hybrid fanout; ranking stub OK).  
4. Profile feed / post detail with cursor pagination.  
5. Like + comment; basic notifications.  
6. Celebrity / hybrid path so mega-creators don’t melt writes.  
7. Block / mute filters applied at merge.  
8. CDN-backed media URLs; rate limits; idempotent publish.

**Out of MVP (explicitly defer):**

- Full Reels For-You dense neural ranker  
- Live streaming  
- Encrypted DMs  
- Shopping / checkout  
- Exact global trending  
- Collaborative filters / close friends deep product  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Publish ACK latency? | Feels instant | p99 < 300ms metadata; media processing async |
| N2 | Feed read latency? | Snappy scroll | p99 < 100–200ms for cached timeline page |
| N3 | Media availability? | Critical UX | CDN 99.9%+; multi-AZ origin |
| N4 | Durability? | No lost posts after ACK | Durable post row + media object refs |
| N5 | Consistency? | Feed eventual OK | Read-your-writes on own profile |
| N6 | Privacy? | Private posts never leak | ACL at fetch + fanout filters |
| N7 | Multi-region? | Global users | Home cell / regional feed densification |
| N8 | Abuse? | Spam / bot follows | Rate limits + signal hooks |
| N9 | Fairness? | Hot celebrities don’t starve others | Isolate hot keys; hybrid pull |
| N10 | Maintainability? | Clear service boundaries | Post / Graph / Feed / Media / Counter planes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Upload photo → processing completes → post appears on profile → fans see in feed.  
2. Follow creator → their *new* posts appear (fanout-on-write or pull).  
3. Like post → counter++; author notification.  
4. Celebrity posts → not pushed to all timelines; pulled / ranked at read.  
5. Scroll home → cursor page of hydrated posts + signed media URLs.  
6. Unfollow → stop receiving new posts; historical timeline entries filtered or expire.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload succeeds, process fails | Retry with backoff; post stays `pending`; user notified; dead-letter after N |
| Double submit post | `Idempotency-Key` / client `post_id` → one post |
| Unfollow mid-fanout | Filters at read; best-effort delete from timelines |
| Mute / block | Exclude at feed merge; never show |
| Hot celebrity 100M followers | Hybrid pull; never full push |
| Feed cache stampede | Soft TTL; singleflight / request coalesce |
| Private account leak | ACL checks on every post fetch |
| Deleted post | Tombstone; remove from caches; counters freeze |
| Counter drift | Periodic reconcile from event log |
| Region failover | Home cell promote; feed rebuild eventual |
| Partial media variant ready | Serve available variants; progressive enhancement |
| Follow spam | Rate limit + suspicious graph signals |
| Clock skew across regions | Server timestamps; logical feed scores, not client clocks |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 100M | 1B | multi-B class | extreme |
| DAU | 50M | 500M | multi-B class | extreme |
| Peak publish QPS | 5K | 50K | 500K | 5M |
| Peak feed QPS | 200K | 2M | 20M | 200M |
| Avg follows / user | 200 | 200 | 300 | 300 |
| Posts / day | 100M | 1B | 10B | 100B |
| Celebrity threshold | 100K followers | 100K–1M | 1M+ | tiered bands |
| Media stored (order) | 50PB | 500PB | multi-EB | multi-EB |
| Naive fanout writes/s | ~1M | impossible | — | — |
| Peak like QPS | 100K | 1M | 10M | 100M |

**What each jump forces:**

- **10×:** Redis / Cassandra timelines; CDN; async fanout workers; counter service; object storage.  
- **100×:** Hybrid celebrity; feed ranker service; media processing fleet; user/home **cells**; hot-key isolation.  
- **1,000×:** Regional feed densification; candidate retrieval + rank; object storage tiers; edge feed caches; per-tenant fairness if B2B surfaces exist.

### 1.5 Etc. (Constraints & Assumptions)

- Feed ranking ML can be a **stub** that scores candidates (recency, affinity, media type).  
- Media processing is a pipeline we must architect, not ignore.  
- Stories / Reels / DMs mentioned as extensions with clear hooks.  
- Ads injection is a candidate mixer hook, not a billing system.  
- Microsoft interviewers often probe: **API clarity**, **failure modes**, **how you operate this**, and whether you confuse CDN egress with API QPS.

**Scope statement to repeat back:**

> Design an Instagram-like system: media upload/processing, follows, posts, and home feed via hybrid fanout with celebrity exceptions, CDN delivery, and progressive scale—never joining the full follow graph against posts on every scroll at large DAU. Frame APIs and cell boundaries so a Microsoft team could own and operate slices of it.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Feed reads** | Home scroll | 200K/s | 2M/s | Timeline + cache |
| **Publishes** | Create post | 5K/s | 50K/s | Post + media |
| **Fanout writes** | Push to timelines | ~1M/s naive | ×10 | Async workers |
| **Follow graph** | Follow / unfollow | 10K/s | 100K/s | Graph store |
| **Media origin** | Upload bytes | GB/s | ×10 | Object store |
| **CDN egress** | Image / video | huge | ×10 | Edge |
| **Likes** | Counter incr | 100K/s | 1M/s | Counter svc |
| **Notifs** | Light fanout | high | ×10 | Notif svc |

**Anti-pattern:** one QPS number that mixes feed GETs and image bytes.

### 2.2 Fanout arithmetic (core interview math)

```text
Avg followers (blended) = 200
Publish peak = 5_000 posts/s
Naive fanout-on-write = 5_000 × 200 = 1_000_000 timeline writes/s

Celebrity: 50_000_000 followers × 1 post = 50_000_000 writes
→ DEAL-BREAKER if synchronous or even “async but complete push”
→ Hybrid: push for normal accounts; pull for celebrities
```

**With hybrid (assume 1% of posts are celebrity / large):**

```text
Normal posts (99%): 4_950 × 200 ≈ 990K writes/s still heavy
Often also: only push to online / active followers, or trim timeline length
Celebrity posts (1%): 50 × (pull at read for followers) → 0 timeline writes
→ Still need write batching, sharding, and trim policies at 10×+
```

**Smarter baseline assumption for interviews:**

```text
Push only for accounts with followers < THRESH (e.g. 10K or 100K)
Blended effective fanout factor maybe 50–100 instead of 200
5_000 × 80 ≈ 400_000 timeline writes/s — still needs Cassandra/Redis-scale store
```

### 2.3 Feed read amplification

```text
DAU 50M; peak concurrent ~10% = 5M
Active scroll: request a page every ~10–30s
5M × (1/20) ≈ 250K feed QPS — matches table order

Each page: 20–50 post_ids from timeline → hydrate posts → return media URLs
Hydration must be batched multi-get, not N+1 to post DB
```

### 2.4 Media storage

```text
100M posts/day × avg 2 MB original ≈ 200 TB/day originals
Variants (thumb, feed, web, maybe HLS segments) ×2–3 → more bytes
CDN cache hit ratio is the real cost control; lifecycle to cold storage
```

At **10×:** ~2 PB/day raw order-of-magnitude if unoptimized → compression, shorter retention of originals, regional buckets.

### 2.5 Graph storage

```text
100M users × 200 follows = 20B edges
Edge ~32–64 B → ~640 GB–1.3 TB raw + indexes
Store: Cassandra / Dynamo-like / sharded SQL / graph service
Need both directions:
  following(user) → list for profile / feed sources
  followers(user) → list for fanout-on-write
```

### 2.6 Counter volume

```text
Likes 100K/s → do NOT:
  UPDATE posts SET like_count = like_count + 1  on primary row each time
Use:
  Counter service / Redis INCR + async flush
  Or CRDT-ish sharded counters with periodic reconcile
```

### 2.7 Timeline storage growth

```text
Assume 50M posts/day pushed with avg 100 effective fanouts
50e6 × 100 × 32 B ≈ 160 GB/day timeline inserts (raw)
+ indexes / replication → higher
Trim timelines to last N (e.g. 1000–5000 entries) or time window
Celebrity pull avoids writing to tens of millions of timelines
```

### 2.8 Cache footprints

```text
Home feed cache per active user: 1K post_ids × 16 B ≈ 16 KB
100M DAU × 10% hot-cached ≈ 160 GB Redis cluster order — shard by user_id

Post hydration cache: hot posts (celebrities) must be heavily cached
Counter Redis: likes/views sharded by post_id
```

### 2.9 Bandwidth

```text
Feed API response ~5–20 KB JSON per page (IDs + captions + CDN URLs)
250K QPS × 10 KB ≈ 2.5 GB/s API egress (order) — significant but not media

Media: if 5M concurrent each fetch 1 MB occasionally → CDN, not origin
Origin protected by CDN; signed URLs; short TTL cookies/tokens
```

### 2.10 Partition / shard sketch

```text
Posts:          shard by author_id (profile locality) or post_id
Timelines:      shard by viewer_id
Graph:          shard by followee_id for fanout; follower_id for following list
Kafka topics:   PostCreated by author_id; FanoutTasks by viewer shard
Media:          object key = hash / uuid; metadata in post row
```

### 2.11 Amplification factors & fixes

| Naive | Amplification | Fix |
|-------|---------------|-----|
| Push to all followers always | × follower count | Hybrid celebrity pull |
| Feed hydrates full media bytes via API | × page bandwidth | CDN URLs + thin IDs |
| Like → UPDATE post row | lock storm | Counter service |
| Fanout sync in publish API | tail latency | Async workers + outbox |
| Unlimited timeline length | storage forever | Trim + archive |
| JOIN follows × posts on read | DB death | Precomputed / hybrid |

### 2.12 Progressive scale implications (summary table)

| Concern | Baseline | 10× | 100× | 1,000× |
|---------|----------|-----|------|--------|
| Timeline store | Redis + Cassandra | multi-cluster | cells | geo cells |
| Fanout | async workers | more partitions | hybrid strict | regional densify |
| Media | multi-AZ bucket + CDN | multi-region buckets | processing fleet | edge encode |
| Ranker | stub score | feature service | dedicated rank | retrieval + rank |
| Hot keys | celebrity list | dedicated caches | isolation | shard pull paths |

---

## 3. High-Level Design

### 3.1 Product / UX surfaces

```text
+--------------------------------------------------------------------------+
| Instagram                                          [Search] [+] [♥] [☺] |
+--------------------------------------------------------------------------+
| Home | Search | Create | Reels | Profile                                 |
+--------------------------------------------------------------------------+
| Stories strip (Phase 1.5)                                                |
+--------------------------------------------------------------------------+
| ┌────┐  @alice · 2h · · ·                                      •••     |
| │img │  Caption: sunset in Seattle...                                   |
| │    │  ♥ 12.4K   💬 308                                                |
| └────┘                                                                   |
| ┌────┐  @bigceleb · sponsored/hybrid pull                               |
| │vid │  ...                                                              |
+--------------------------------------------------------------------------+
```

Client holds: session token, follow graph snapshot (optional), feed cursor, local media cache.

### 3.2 Domain model

```text
User
  ├── Profile (bio, avatar_media_id, privacy)
  ├── Following[] / Followers[]
  ├── Timeline / FeedIndex (viewer-owned post_id list)   # for push path
  └── Posts[] (author-owned)

Post
  ├── post_id, author_id, caption, created_at, visibility
  ├── media_ids[] → MediaAsset (variants, status)
  ├── like_count / comment_count (via counter svc)
  └── comments[] (separate store)

MediaAsset
  ├── original object key, variants[], processing_state
  └── CDN path / signed URL policy
```

**Identifiers:**

| Field | Role |
|-------|------|
| `user_id` | Snowflake / ULID |
| `post_id` | Snowflake (time-sortable helps) |
| `media_id` | UUID |
| `client_post_id` | Idempotency |
| `feed_cursor` | opaque `(score, post_id)` or `(ts, post_id)` |

### 3.3 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/media/upload_sessions` | Get upload URL / session |
| PUT | client → object store (direct) | Upload bytes |
| POST | `/v1/media/{id}/complete` | Kick processing |
| POST | `/v1/posts` | Create post (idempotent) |
| GET | `/v1/feed/home?cursor=` | Home feed page |
| GET | `/v1/users/{id}/posts` | Profile grid |
| GET | `/v1/posts/{id}` | Post detail |
| POST | `/v1/users/{id}/follow` | Follow |
| DELETE | `/v1/users/{id}/follow` | Unfollow |
| POST | `/v1/posts/{id}/likes` | Like |
| POST | `/v1/posts/{id}/comments` | Comment |
| GET | `/v1/notifications` | Notif inbox |

**Publish sequence (preferred):**

```text
1) Client requests upload session → signed PUT URL
2) Client uploads to object store directly (not through app servers)
3) Client POST /posts { media_id, caption, client_post_id }
4) Post service validates media owned + processed (or allow pending)
5) Persist post; emit PostCreated outbox
6) Fanout workers / ranker hooks async
7) Return post_id quickly
```

**Deal-breaker:** proxying multi-GB video through the API tier.

### 3.4 High-level architecture options

| Option | Description | Pros | Cons | Verdict |
|--------|-------------|------|------|---------|
| **A. Monolith + SQL** | One DB, JOIN follows×posts for feed | Simple | Dies at scale | MVP toy only |
| **B. Fanout-on-write only** | Push every post to all follower timelines | Fast reads | Celebrity meltdown | Incomplete |
| **C. Fanout-on-read only** | Merge latest posts from followees at read | Simple writes | Slow / heavy at read | Incomplete alone |
| **D. Hybrid (chosen)** | Push for normal; pull for celebrities; rank merge | Practical | Complexity | **Choose** |

**Choice D deal-breakers if skipped:**

- Synchronous push to 50M followers in publish path  
- No celebrity exception list / follower-count threshold  
- Hydrating feed with per-post SQL round trips  

### 3.5 Component architecture

```text
Clients (iOS / Android / Web)
        |
        v
   Edge / CDN (media)  +  API Gateway (JSON APIs)
        |                        |
        |                        +--> Auth
        |                        +--> Post Service
        |                        +--> Feed Service
        |                        +--> Graph Service
        |                        +--> Counter Service
        |                        +--> Notification Service
        |
   Object Storage <--> Media Processing Workers
                              |
                         PostCreated bus (Kafka)
                              |
              +---------------+---------------+
              v               v               v
         Fanout Workers   Ranker Features   Search/Notif
              |
              v
         Timeline Store (Cassandra/Redis)
```

### 3.6 Feed generation strategy (heart of the interview)

#### Problem

Reading home feed by joining “everyone I follow × their posts” at request time does not scale. Writing every post into every follower’s inbox does not scale for celebrities.

#### Hybrid algorithm

```text
THRESH = 100_000 followers (tune; maybe 10K early)

on_PostCreated(post):
  author = post.author_id
  follower_count = graph.count_followers(author)
  if follower_count < THRESH:
      enqueue FanoutPush(post, followers_iterator)
  else:
      mark author as celebrity / pull-source
      # optionally push to online active viewers sample only
      cache post in celebrity recent posts index

on_HomeFeed(viewer, cursor):
  pushed = timeline_store.get_page(viewer, cursor)          # post_ids
  celebs = graph.celebrities_followed(viewer)               # cached
  pulled = celebrity_posts_index.recent(celebs, since)
  candidates = merge(pushed, pulled)
  candidates = apply_mute_block_filters(viewer, candidates)
  ranked = ranker.score(viewer, candidates)                 # stub OK
  page = hydrate(ranked[:page_size])
  return page + next_cursor
```

#### Options comparison

| Approach | Write cost | Read cost | Freshness | Celebrity |
|----------|------------|-----------|-----------|-----------|
| Push only | O(followers) | O(1) page | High | Breaks |
| Pull only | O(1) | O(followees × k) | Medium | OK writes |
| Hybrid | O(small) | O(1 + #celebs) | High | OK |
| Push online-only | O(online) | +pull offline | High | Still careful |

**Online-only optimization (10×+):** push timeline entries only for recently active users; cold users rebuild on next login via pull merge.

### 3.7 Media pipeline

```text
Upload → Object Store (original)
      → Queue MediaJob
      → Workers: validate, virus scan hook, transcode, thumbs
      → Write variants metadata
      → Mark media ready
      → (optional) notify Post if waiting
```

| Concern | Approach |
|---------|----------|
| Large files | Direct-to-storage signed upload |
| Idempotency | media_id + job id |
| Failure | Retry; DLQ; user-visible failed state |
| Hot encode | Separate GPU/CPU pools for video |
| CDN | Purge on delete; signed URLs for private |

### 3.8 Graph service

```text
follow(a, b):
  authz / rate limit
  if b.private: create FollowRequest
  else: write edges both directions; incr counts; emit Followed

unfollow(a, b):
  delete edges; best-effort remove future fanout; timeline GC optional
```

**Storage options:**

| Store | Pros | Cons |
|-------|------|------|
| Cassandra / wide-column | Scale, fanout iteration | Operational skill |
| Sharded MySQL | Familiar | Reshard pain |
| Graph DB | Nice queries | Often overkill / ops |

**Microsoft framing:** prefer boring sharded stores with clear ownership APIs over exotic graph DBs unless the team already runs them.

### 3.9 Consistency model (feed)

| Surface | Model |
|---------|-------|
| Own profile after post | Read-your-writes (sticky / primary read) |
| Follower home feed | Eventual (seconds typical) |
| Like counts | Eventual; may tick up late |
| Privacy / block | **Stronger** — must not leak; fail closed on ACL |

**Invariant:** After ACK of create post, post is durable. Fanout lag is visible but bounded with monitoring.

---

## 4. Architecture Diagram

### 4.1 End-to-end publish + feed

```text
┌────────────┐   signed PUT    ┌─────────────────┐
│   Client   │───────────────►│ Object Storage  │
└─────┬──────┘                └────────┬────────┘
      │ POST /posts                    │ event
      v                                v
┌────────────┐                  ┌─────────────────┐
│ Post Svc   │──outbox────────►│ Kafka PostCreated│
└─────┬──────┘                  └────────┬────────┘
      │                                  │
      v                    ┌─────────────┼─────────────┐
┌────────────┐             v             v             v
│ Post DB    │      Fanout Workers  Media Workers  Notif/Search
└────────────┘             │
                           v
                    ┌──────────────┐
                    │ Timeline Store│
                    └──────┬───────┘
                           │
┌────────────┐             │
│ Feed Svc   │◄────────────┘  + celebrity pull index
└─────┬──────┘
      │ hydrate
      v
┌────────────┐     ┌──────────────┐
│ Post Cache │     │ Counter Svc  │
└────────────┘     └──────────────┘
      │
      v
   Client ◄──── CDN URLs for media
```

### 4.2 Hybrid fanout detail

```text
                    PostCreated
                         |
          +--------------+--------------+
          | follower_cnt < THRESH?      |
         yes                           no
          |                             |
   iterate followers             write celebrity
   (paged) async                 recent-posts index
          |                             |
   timeline.zadd(viewer, post)    (readers pull)
          |
   optional WS/push wake
```

### 4.3 Cell / region sketch (100×+)

```text
                  Global Directory (user → home cell)
                           |
         +-----------------+-----------------+
         v                 v                 v
      Cell USW          Cell USE          Cell EU
   (users home)      (users home)      (users home)
         |                 |                 |
   local timeline     local timeline    local timeline
   local post write   ...               ...

Cross-cell follow: fanout tasks hop via async bus to follower home cells
Media: multi-region buckets + global CDN
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Failure modes & mitigations**

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Post DB primary down | Cannot publish | Multi-AZ; failover; dual-write outbox carefully |
| Kafka lag | Feed freshness delay | Partition scaling; alert on lag; degrade ranker |
| Fanout worker crash | Partial timelines | Idempotent timeline writes; replay from offset |
| Object store outage | Upload fail | Multi-AZ; retry; regional failover |
| CDN miss storm | Origin overload | Origin shield; cache TTLs; soft 404 for deleted |
| Counter Redis loss | Wrong counts | Rebuild from like events; accept brief drift |
| Graph store hot partition | Celebrity follow storms | Cache follower counts; rate limit; shard |

**Idempotency keys**

- `client_post_id` for create post  
- `fanout_task_id = post_id + viewer_shard + epoch`  
- Like: `(user_id, post_id)` unique  

**Outbox pattern:** Post service writes DB + outbox row in one transaction; publisher relays to Kafka. Avoids “DB yes / event no.”

**Degradation order (Microsoft-style ownership story):**

1. Drop noncritical notifs  
2. Serve chronological merge without ML ranker  
3. Serve cached feed pages stale-while-revalidate  
4. Block publishes only if durability cannot be guaranteed  
5. Never serve private content on ACL uncertainty  

**SLOs (example):**

| SLO | Target |
|-----|--------|
| Publish success (ACK durable) | 99.9% |
| Feed p99 latency | < 200ms |
| Fanout lag p99 (normal accounts) | < 5–15s |
| Media processing p99 (image) | < 30s |

### 5.2 Scalability

**Horizontal scaling levers**

| Component | Scale key | Notes |
|-----------|-----------|-------|
| API | stateless | autoscale on CPU / QPS |
| Post DB | shard by author_id | profile locality |
| Timeline | shard by viewer_id | Redis cluster / Cassandra |
| Graph | dual indexes | careful with celebrities |
| Media workers | queue depth | separate image/video pools |
| CDN | edge PoPs | hit ratio KPI |

**Hot-key playbook**

```text
Celebrity author:
  - pull index with recent posts (Redis ZSET / per-author log)
  - hydrate cache always warm
  - never iterate 50M followers on publish path
  - optional: push to "online now" subset via presence if product wants instant

Viral post:
  - cache post entity aggressively
  - counters in Redis with shard striping (like_count:{post}:{slot})
  - rate limit abusive scrapers
```

**Feed read path optimizations**

1. Timeline cache (post_id list) in Redis  
2. Multi-get hydrate with post cache  
3. Client-side media via CDN  
4. Cursor pagination; no deep OFFSET  
5. Request coalescing for same user stampedes  

**Write path optimizations**

1. Direct upload  
2. Async fanout  
3. Batch timeline writes (pipeline)  
4. Trim old timeline entries  
5. Backpressure when Kafka lag high (slow publishes? or shed fanout to pull-only temporarily)

### 5.3 Maintainability

**Service boundaries (ownable by teams)**

| Service | Owns | API |
|---------|------|-----|
| Post | Post metadata lifecycle | CRUD posts |
| Media | Assets + processing | upload session, status |
| Graph | Follow edges / privacy | follow APIs |
| Feed | Timeline + merge + rank hook | home feed |
| Counter | Likes/views | incr/get |
| Notif | Delivery prefs | inbox / push |
| T&S | reports, takedowns | admin |

**Why this matters in Microsoft interviews:** they often care that you can draw **team-operable** slices with clear contracts, versioning, and on-call boundaries—not a single “social microservice” blob.

**Schema evolution**

- Soft fields / protobuf for events  
- Expand-contract for API fields  
- Feed ranker behind interface: `score(viewer, candidates) -> scores`  

**Observability**

| Signal | Why |
|--------|-----|
| Fanout lag by author tier | Detect celebrity misclassification |
| Timeline write error rate | Data loss risk |
| Feed empty rate | Bug or over-filtering |
| Media job age | Processing backlog |
| ACL deny rate | Privacy / abuse |
| Cache hit ratio | Cost / latency |

**Testing strategy**

- Contract tests on feed merge (mute/block/private)  
- Load test fanout with synthetic celebrity  
- Chaos: kill fanout workers, verify replay  
- Property: idempotent timeline insert  

### 5.4 Privacy & ACL deep dive

```text
on_hydrate(viewer, post_ids):
  posts = post_store.multi_get(post_ids)
  return [p for p in posts if can_view(viewer, p)]

can_view(viewer, post):
  if post.deleted: return false
  if blocked(either way): return false
  if post.author.public: return true
  if viewer == author: return true
  if approved_follower(viewer, author): return true
  return false
```

**Fail closed.** Cached feed IDs may be stale after unfollow / block → filter at hydrate.

### 5.5 Ranking hooks (keep light)

MVP ranker features:

- Recency  
- Affinity (like/comment/DM history — coarse)  
- Media type preference  
- Already-seen penalty  

```text
score = w1*recency + w2*affinity + w3*media_pref - w4*seen
```

At 100×, split **candidate generation** (timeline + celebrity pull + explore) from **ranking**. Ads mixer injects sponsored candidates with constraints.

### 5.6 Delete / GDPR-style erasure

```text
delete_post:
  tombstone post
  enqueue RemoveFromTimelines (best-effort, bounded)
  delete/ban media objects per policy
  emit to search/notif to drop

delete_user:
  cascade jobs; long-running; track job state
```

Do not promise instantaneous global purge in interview; promise **bounded, tracked erasure workflow**.

### 5.7 Multi-region

| Approach | Pros | Cons |
|----------|------|------|
| Single region active | Simple | Latency / DR |
| Home cell per user | Clear write locality | Cross-cell fanout |
| Active-active posts | Low latency writes | Conflict hell — avoid |

**Chosen:** user home cell for writes (posts, timeline ownership); media multi-region; CDN global; cross-cell async fanout.

---

## 6. Wrap-Up

### 6.1 What we designed

An Instagram-like system with:

1. Direct-to-storage media upload + processing pipeline  
2. Follow graph with privacy hooks  
3. Hybrid home feed (push for normal, pull for celebrities)  
4. Counter / notification / CDN planes separated from publish path  
5. Progressive scale path 10× → 100× → 1,000× via cells and hot-key isolation  

### 6.2 Key trade-offs revisited

| Decision | Chose | Rejected | Why |
|----------|-------|----------|-----|
| Feed | Hybrid | Pure join-on-read | Scale |
| Publish | Async fanout | Sync push all | Latency / celebrity |
| Media | Direct upload | Proxy through API | Bandwidth |
| Counts | Counter svc | Row UPDATE | Hot posts |
| Region | Home cell | Dual-active writes | Consistency |

### 6.3 Risks & follow-ups

- Ranker quality (product)  
- Celebrity threshold tuning  
- Timeline storage cost  
- Abuse / bots  
- Stories / Reels as separate retrieval systems  

### 6.4 60-second pitch

> “I’d split media, graph, posts, and feed. Publish ACKs after durable metadata; fanout async. Normal accounts push into follower timelines; celebrities are pull sources merged at read with mute/block filters. Hydration is batched; media is CDN. We scale with sharded timeline/graph stores and user home cells, and we never JOIN the world on every scroll.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Feed fanout

**Q1. Walk through hybrid fanout with numbers.**  
Show 5K posts/s × 200 followers = 1M writes/s; 50M-follower celebrity as deal-breaker; threshold + pull index.

**Q2. Should we push only to online users?**  
Reduces writes; cold users rebuild via pull. Trade freshness vs cost. Need presence or “last active” signal.

**Q3. How do you trim timelines?**  
Keep last N IDs; archive cold; on miss, regenerate from followees’ recent posts (expensive — rate limit).

**Q4. Ordering in home feed?**  
Not global linearizability. Rank score + tie-break `post_id`. Cursor must be stable for pagination.

**Q5. Unfollow consistency?**  
Best-effort delete; mandatory filter at read. Eventual removal from materialized timeline OK.

### 7.2 Media & CDN

**Q6. Why signed upload URLs?**  
Offload bytes; authz via short-lived signature; API tier stays thin.

**Q7. Processing failure after post create?**  
Allow `pending` posts or require media ready before post ACK — product choice. Prefer: post visible to author immediately; followers when ready.

**Q8. Hot video / thundering herd?**  
CDN; origin shield; adaptive bitrate; separate from metadata path.

### 7.3 Graph & privacy

**Q9. Private account follow approval?**  
`FollowRequest` state machine; only approved edges fanout / read.

**Q10. Block vs mute?**  
Block: bidirectional restriction; mute: viewer-side filter only.

**Q11. Graph shard for celebrity followers?**  
Followers list sharded; never full-scan on publish; use pull path instead.

### 7.4 Consistency & correctness

**Q12. Read-your-writes for author?**  
Read from primary / version token / sticky routing after write.

**Q13. Like double-tap?**  
Unique constraint; idempotent POST.

**Q14. Counter drift acceptable?**  
Yes for social counts; reconcile; don’t use counts for authz.

### 7.5 Geo / Microsoft-flavored ops

**Q15. User travels to another continent?**  
Home cell writes still home; read latency higher; optional read replicas / regional feed cache; media via CDN OK.

**Q16. How would this map to Azure?**  
API Management / Front Door, Blob Storage + CDN, Event Hubs/Kafka, Cosmos DB or Cassandra-like, Redis Cache, Functions/AKS workers — mention as mapping, not requirement.

**Q17. Multi-tenant abuse fairness?**  
Per-user rate limits; isolate scrapers; bot detection hooks.

**Q18. Cell migration?**  
User move job: drain writes, copy graph/posts/timeline, flip directory — rare, careful.

### 7.6 Ranking & product extensions

**Q19. Where do ads inject?**  
Mixer stage after candidates, before final page; constraints (no two ads in a row).

**Q20. Stories vs feed?**  
Separate TTL store; ring UI; not the same timeline table.

**Q21. Explore page?**  
Candidate retrieval (ANN / inverted) + rank; different from following feed.

**Q22. Notifications at celebrity scale?**  
Collapse (“1000 others liked”); sample; never create 50M notif rows synchronously.

### 7.7 Trap questions (answer briefly)

| Trap | Good answer |
|------|-------------|
| “Just use MySQL JOIN” | Fine for homework; fails at our QPS |
| “Push to everyone always” | Celebrity |
| “Strongly consistent global feed” | Unnecessary; define per-surface |
| “Store images in Postgres” | Object store |
| “We need GraphQL federation first” | Not the bottleneck |

---

## 8. Appendices

### Appendix A — Glossary

| Term | Meaning |
|------|---------|
| Fanout-on-write | Materialize post into follower timelines at publish |
| Fanout-on-read | Merge followees’ posts at read time |
| Hybrid feed | Combine both with celebrity threshold |
| Timeline | Per-viewer ordered list of post_ids |
| Home cell | Region/cluster that owns a user’s writes |
| Hydration | Expand post_ids → post entities + media URLs |
| Tombstone | Soft-delete marker |
| Origin shield | CDN tier protecting object storage |

### Appendix B — Example schemas (sketch)

```sql
-- logical relational sketch (physical = sharded / wide-column)
users(user_id, handle, privacy, created_at)
follows(follower_id, followee_id, state, created_at)  -- PK (follower, followee)
posts(post_id, author_id, caption, visibility, media_ids, created_at, state)
media(media_id, owner_id, status, variants_json, created_at)
timeline(viewer_id, score, post_id, author_id)  -- PK (viewer_id, score, post_id)
likes(user_id, post_id, created_at)  -- PK (user_id, post_id)
comments(comment_id, post_id, author_id, body, created_at)
```

```text
Cassandra timeline example:
  PK = viewer_id
  CK = (score DESC, post_id)
  columns: author_id, created_at
```

### Appendix C — Event contracts

```json
{
  "type": "PostCreated",
  "post_id": "p_123",
  "author_id": "u_9",
  "created_at": 1735689600,
  "visibility": "public",
  "media_ready": true,
  "follower_count_snapshot": 1520
}
```

```json
{
  "type": "FanoutTask",
  "post_id": "p_123",
  "viewer_shard": 42,
  "follower_page_token": "..."
}
```

### Appendix D — Celebrity threshold tuning

| Followers | Strategy |
|-----------|----------|
| < 10K | Always push |
| 10K–100K | Push; watch write amp |
| 100K–1M | Default pull; optional online push sample |
| > 1M | Pull + warm cache; strict isolation |

Track misclassified authors (high lag / high write amp) and flip tiers dynamically.

### Appendix E — Capacity cheatsheet (baseline)

| Resource | Order-of-magnitude |
|----------|--------------------|
| Feed QPS | 200K |
| Publish QPS | 5K |
| Timeline writes/s | 0.4M–1M (hybrid dependent) |
| Edges | 20B |
| Media ingress | ~200 TB/day originals |
| Redis feed cache | ~100–200 GB hot |

### Appendix F — Interview checklist (Microsoft)

- [ ] Clarified MVP vs Stories/DMs/Reels/ads  
- [ ] Stated NFRs with numbers  
- [ ] Did fanout math aloud  
- [ ] Chose hybrid with threshold  
- [ ] Separated media plane from API  
- [ ] Named deal-breakers  
- [ ] Covered failure + degradation  
- [ ] Mentioned cells / multi-region without overcomplicating  
- [ ] Clean API sketch  
- [ ] Observability / ownership boundaries  

### Appendix G — Related prompts in this bank

- Generic social-media platform  
- Notification system  
- File-sharing / cloud storage (media adjacent)  
- Search engine (hashtags / users)  

### Appendix H — Sample feed merge pseudocode

```text
function home_feed(viewer, cursor, n):
  push_page = timeline.get(viewer, cursor, n*2)
  celebs = cache.celebs_followed(viewer)
  pull_page = []
  for c in celebs:
      pull_page += celeb_index.recent(c, limit=k)
  merged = unique_by_post_id(push_page + pull_page)
  merged = filter(can_view(viewer), merged)
  merged = filter(not_muted_blocked(viewer), merged)
  scored = rank(viewer, merged)
  page = scored[:n]
  return hydrate(page), next_cursor(page)
```

### Appendix I — Mute/block filter notes

Filters must run **after** candidate merge and **before** return. Caching rendered HTML/JSON pages per viewer is hard when mute lists change — prefer cache post entities globally and timelines as IDs; apply filters per request (cheap if mute list small and cached).

### Appendix J — Progressive enhancement roadmap

| Phase | Deliver |
|-------|---------|
| MVP | Photo posts, follow, hybrid feed, likes/comments |
| 1.5 | Stories, hashtags, private approve, video |
| 2 | Ranker v2, Explore, ads mixer |
| 3 | Reels surface, live hooks, shopping hooks |

### Appendix K — Common math slips to avoid

1. Using average QPS without peak factor (use 5–10×).  
2. Forgetting fanout amplification.  
3. Counting CDN GB as “API server capacity.”  
4. Assuming 100% of DAU simultaneous.  
5. Storing full media in timeline rows.

### Appendix L — On-call runbooks (sketch)

| Alert | Action |
|-------|--------|
| Fanout lag high | Scale workers; temporary pull-only for large accounts |
| Media queue old | Scale transcoder pool; pause noncritical variants |
| Feed p99 high | Check cache hit; hydrate batch size; DB slow queries |
| Origin bandwidth high | CDN config; shield; hot object replication |

### Appendix M — Security notes

- Signed URLs for private media; short TTL  
- Rate limit follow/like/post  
- CSRF / token auth for web  
- Scrub EXIF as policy  
- T&S takedown must stop CDN serving (cache purge)

### Appendix N — Why Microsoft teams ask this

Even if you are interviewing for Azure, M365, or gaming, Instagram exercises: **fanout**, **hot keys**, **async pipelines**, **CDN vs origin**, **eventual consistency UX**, and **service ownership**. Map your answers to how you’d build a similar feed inside Microsoft (e.g., enterprise social, Store recommendations, Xbox activity).

---

*End of Instagram system-design prep doc (Microsoft interview practice).*
