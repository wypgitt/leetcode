# System Design: Instagram

> **Focus areas:** Posts · Media pipeline · Follows · Feed generation · Celebrity fanout · Ranking hooks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct fanout arithmetic, explicit hybrid feed strategy, deal-breakers for “JOIN follows×posts on every home scroll” fantasies  
> **Interview theme:** Meta L5+ social — graph + media + home feed at progressive DAU with hot-key celebrities

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

Goal: **bound the product**—Instagram-class social: users **follow** creators, publish **photo/video posts**, consume a **home feed**, view profiles, and handle **celebrity mega-fanout**—with media via CDN and progressive scale.

### 1.0 What this is / is not

| Dimension | **Instagram (this doc)** | Not this |
|-----------|--------------------------|----------|
| Primary job | Graph + posts + media + home feed | Full Reels TikTok-ranker research / IG Shopping mall |
| Success | Fast publish; fresh relevant feed; reliable media | Perfect global ML paper |
| Media | Upload → process → CDN | Codec inventing deep dive |
| Feed | Hybrid fanout + ranking hooks | Pure SQL join-on-read at Meta scale |
| Stories/DMs/Live | Hooks / Phase 1.5 | Full designs each |

**Scope statement:** Design Instagram-like posts, media, follows, and feed generation—scaling through 10× / 100× / 1,000× with celebrity-aware fanout.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Graph? | Directed follow | Adjacency lists + counts |
| F2 | Post types? | Image + short video MVP | Media pipeline |
| F3 | Home feed? | Ranked with chrono fallback | Fanout + ranker hook |
| F4 | Profile grid? | User’s posts reverse chron | Author index |
| F5 | Celebrity? | Huge follower accounts | Hybrid fanout |
| F6 | Likes/comments? | Yes MVP light | Counters + comment service |
| F7 | Notifications? | Follow/like/comment | Notif service |
| F8 | Search? | Users MVP; hashtags Phase 1.5 | Search index |
| F9 | Privacy? | Public + private accounts | Follow approval; ACL |
| F10 | Stories? | Phase 1.5 | 24h TTL store |
| F11 | DMs? | Out of MVP | Mention only |
| F12 | Ads? | Out of MVP core | Feed injection hook |

**MVP functional scope:**

1. Auth, profiles, follow/unfollow (public; private approve Phase 1.5).  
2. Upload media → process variants → create post.  
3. Home feed of followed accounts (hybrid fanout; ranking stub OK).  
4. Profile feed / post detail.  
5. Like + comment; basic notifications.  
6. Celebrity/hybrid path so mega-creators don’t melt writes.  
7. Block/mute filters.  
8. Cursor pagination; CDN media.

**Out of MVP:**

- Full Reels For-You dense ranker  
- Live streaming  
- Encrypted DMs  
- Shopping / checkout  
- Exact global trending (see other docs)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Publish ACK | Feels instant | p99 < 300ms metadata; media async |
| N2 | Feed read | Snappy | p99 < 100–200ms |
| N3 | Media availability | Critical | CDN 99.9%+; multi-AZ origin |
| N4 | Durability | No lost posts after ACK | Durable post row + media refs |
| N5 | Consistency | Feed eventual OK | Read-your-writes on profile |
| N6 | Privacy | Private posts enforced | ACL at read + fanout |
| N7 | Multi-region | Global | Home cell / regional feeds |
| N8 | Abuse | Spam/bot follows | Rate limits + signals |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Upload photo → processing → post appears on profile → fans see in feed.  
2. Follow creator → their new posts appear (fanout-on-write or pull).  
3. Like post → counter++; author notification.  
4. Celebrity posts → not pushed to all timelines; pulled/ranked at read.  
5. Scroll home → cursor page of hydrated posts + media URLs.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload succeeds, process fails | Retry; post pending; user notified |
| Double submit post | Idempotency-Key |
| Unfollow mid-fanout | Filters at read; best-effort delete from timelines |
| Mute/block | Exclude at feed merge |
| Hot celebrity 100M followers | Hybrid; never full push |
| Feed cache stampede | Soft TTL; request coalesce |
| Private account leak | ACL checks on post fetch |
| Deleted post | Tombstone; remove from caches |
| Counter drift | Periodic reconcile |
| Region failover | Home cell promote; feed rebuild eventual |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 100M | 1B | — | multi-B |
| DAU | 50M | 500M | multi-B class | extreme |
| Peak publish QPS | 5K | 50K | 500K | 5M |
| Peak feed QPS | 200K | 2M | 20M | 200M |
| Avg follows / user | 200 | 200 | 300 | 300 |
| Posts / day | 100M | 1B | 10B | 100B |
| Celebrity threshold | 100K | 100K–1M | 1M+ | tiered |
| Media stored | 50PB | 500PB | multi-EB | multi-EB |
| Fanout writes/s (naive) | huge | impossible | — | — |

**What each jump forces:**

- **10×:** Redis/Cassandra timelines; CDN; async fanout workers; counter service.  
- **100×:** Hybrid celebrity; feed ranker service; media processing fleet; home cells.  
- **1,000×:** Regional feed densification; candidate retrieval + rank; object storage tiers; edge feed caches.

### 1.5 Etc. (Constraints & Assumptions)

- Feed ranking ML can be a stub that scores candidates.  
- Media processing is a pipeline we must architect, not ignore.  
- Stories/Reels/DMs mentioned as extensions.  
- Ads injection is a candidate mixer hook.  
- Meta interview loves **fanout-on-write vs fanout-on-read** discussion.

**Scope statement to repeat back:**

> Design Instagram-like social: media upload/processing, follows, posts, and home feed via hybrid fanout with celebrity exceptions, CDN delivery, and progressive scale—never joining the full follow graph against posts on every scroll at large DAU.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Feed reads** | Home scroll | 200K/s | 2M/s | Timeline + cache |
| **Publishes** | Create post | 5K/s | 50K/s | Post + media |
| **Fanout writes** | Push to timelines | variable | ×10 | Async workers |
| **Follow graph** | Follow/unfollow | 10K/s | 100K/s | Graph store |
| **Media origin** | Upload/bytes | GB/s | ×10 | Object store |
| **CDN egress** | Image/video | huge | ×10 | Edge |
| **Likes** | Counter incr | 100K/s | 1M/s | Counter svc |
| **Notifs** | Fanout light | high | ×10 | Notif svc |

**Anti-pattern:** one QPS mixing feed GETs and image bytes.

### 2.2 Fanout arithmetic (core)

```text
Avg followers = 200
Publish = 5_000 posts/s
Naive fanout-on-write = 5_000 × 200 = 1_000_000 timeline writes/s

Celebrity 50M followers × 1 post = 50_000_000 writes — DEAL-BREAKER
→ Hybrid: push for normal; pull for celebrities
```

### 2.3 Feed read amplification

```text
DAU 50M; avg 20 min session; feed page every 30s active
Rough peak fraction online 10% → 5M users
If poll/page 0.1–1 Hz during scroll → hundreds of K to M QPS
Must: cached timeline pages; hydrate posts in batch
```

### 2.4 Media storage

```text
100M posts/day × avg 2MB original = 200 TB/day originals
Variants (thumb, feed, web) ×2–3 → more
CDN cache hit ratio critical; lifecycle cold storage
```

### 2.5 Graph storage

```text
100M users × 200 follows = 20B edges
Edge ~32B → ~640GB raw + indexes — Cassandra/TAO-like / sharded SQL OK with care
```

### 2.6 Counter volume

```text
Likes 100K/s → don’t UPDATE posts SET like_count in primary row each time
Use counter service / Redis + async persist
```

### 2.7 Storage growth (media + timelines)

```text
Posts/day baseline: 50M × (meta 500B + media avg 200KB after variants careful)
Media dominates: 50M × 200KB = 10TB/day ingress to object store (+replication/EC)
10×: ~100TB/day; 100×: ~1PB/day → lifecycle, codecs, regional buckets

Timelines: push fanout writes
  50M posts/day × avg 300 followers × 32B entry ≈ 480GB/day timeline inserts
Celebrity pull avoids writing to 50M follower timelines
```

### 2.8 Memory / cache footprints

```text
Home feed cache per active user: 1K post_ids × 16B ≈ 16KB
100M DAU × 10% cached hot ≈ 160GB Redis cluster order — shard by user_id
Counter Redis: likes/views sharded; not on post row
Graph edge cache for celebrities: follower samples / bloom for mute/block
```

### 2.9 Partition counts

```text
Posts: shard by post_id or author_id (author_id helps profile)
Timelines: shard by owner_id (viewer)
Graph: shard by followee_id for fanout read of followers; follower_id for following list
Kafka PostCreated: partitions by author_id; 256→4K
```

### 2.10 Amplification factors

| Naive | Amplification | Fix |
|-------|---------------|-----|
| Push to all followers always | × follower count | Hybrid celebrity pull |
| Feed read hydrates full media | × page size bandwidth | CDN URLs + thin IDs |
| Like → UPDATE post row | lock storm | Counter service |
| Fanout sync in API | tail latency | Async workers |
| Unlimited timeline length | storage forever | Trim + archive |

### 2.11 10×/100×/1,000× implications

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Post/s | 1K | 10K | 100K | 1M |
| Fanout writes/s | ~0.3M | ~3M | cells | pull-heavier |
| Feed QPS | 100K | 1M | 10M | edge+cells |
| Media TB/day | ~10 | ~100 | ~1PB | multi-PB |

**Pitch:** “Hybrid fanout, blob media on CDN, counters aside, timelines trimmed—Instagram is write amplification managed by celebrity threshold.”


---

## 3. High-Level Design

### 3.1 APIs

| Op | Semantics |
|----|-----------|
| `POST /v1/media/upload` | Init upload (presigned URL) |
| `POST /v1/posts` | Create post with media_ids (Idempotency-Key) |
| `DELETE /v1/posts/{id}` | Delete / tombstone |
| `GET /v1/feed/home?cursor=` | Home feed page |
| `GET /v1/users/{id}/posts?cursor=` | Profile grid |
| `POST /v1/users/{id}/follow` | Follow |
| `DELETE /v1/users/{id}/follow` | Unfollow |
| `POST /v1/posts/{id}/likes` | Like |
| `POST /v1/posts/{id}/comments` | Comment |
| `GET /v1/posts/{id}` | Detail hydrate |
| `GET /v1/notifications` | Notif inbox |

### 3.2 Schemas

```text
User { user_id, handle, is_private, is_celebrity, home_region }
FollowEdge { follower_id, followee_id, created_at, state }
Media { media_id, owner_id, status, variants[] }
Post { post_id, author_id, media_ids[], caption, created_at, visibility }
TimelineEntry { owner_id, post_id, ts, author_id, rank_score? }
Counter { post_id, likes, comments }
Comment { comment_id, post_id, user_id, text, ts }
```

### 3.3 Feed generation — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Fanout-on-write** | Fast reads | Write amp; celeb death | Normal users |
| **Fanout-on-read** | Cheap writes | Slow/complex reads | Celebs / sparse |
| **Hybrid** | Best of both | Two paths | **MVP at scale** |
| **SQL join follows×posts** | Simple | Won’t scale | **Deal-breaker** large DAU |
| **Push ranked** | Personalized early | Heavy compute write | Later |

**Chosen hybrid:**

```text
if followers < T (e.g. 10K–100K): fanout-on-write to follower timelines
else: mark author celebrity; feed read pulls recent posts from celeb index + merges
```

### 3.4 Media pipeline

```text
Client → presigned PUT to object store
  → upload complete callback
  → processing queue: virus scan, thumbnails, transcode
  → write variants; Media READY
  → Post create allowed (or post pending until READY)
CDN serves variants with cache headers; signed URLs if private
```

### 3.5 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Feed | Hybrid fanout | Celeb math | Pure write fanout for all |
| Timeline store | Cassandra/Redis-like wide rows | Append + trim | RDBMS huge joins |
| Media | Object store + CDN | Bytes | DB BLOBs |
| Counters | Separate service | Hot rows | Sync UPDATE post row |
| IDs | Snowflake/ULID | Time sortable | Random UUID only without created_at index story |
| Privacy | Check on read+fanout | Leaks | Fanout ignoring private |

### 3.6 Consistency model

| Object | Model | Notes |
|--------|-------|-------|
| Post create | Strong for author | Idempotent |
| Fanout to timelines | Eventual seconds–minutes | OK |
| Home feed read | Eventual | Ranking may reshuffle |
| Follow edge | Strong-ish / read-your-writes | Cache carefully |
| Counters | Approximate OK | Exact async |
| Media | Durable before publish | Pointer in post |

**Deal-breaker:** requiring global linearizability of all friends’ feeds.

### 3.7 API edge cases

| Case | Behavior |
|------|----------|
| Duplicate Idempotency-Key | Same post_id |
| Private account follow | Pending request |
| Block | Remove from feed candidates; deny profile |
| Delete mid-fanout | Tombstone; readers filter |
| Empty media processing | Don’t publish until ready (or soft) |
| Cursor invalid | Reset refresh |
| Celebrity threshold flip | Stop push; pull on read |

### 3.8 Indexes

```text
posts: PK (post_id); INDEX (author_id, created_at DESC)
timelines: PK (owner_id, ts, post_id); CLUSTER by owner_id
follows: PK (follower_id, followee_id); INDEX (followee_id, follower_id) -- fanout
blocks: PK (blocker, blockee)
media: PK (media_id); status processing
```

### 3.9 HLD pitch

> “Create post → store media → async fanout to non-celebrity followers’ timelines; celebrities pulled at read. Feed merge + light rank + hydrate from caches/CDN. Counters and notifications are separate planes.”


---

## 4. Architecture Diagram

```text
                         +------------------+
   Mobile/Web ---------> | API Gateway      |
                         +--------+---------+
                                  |
     +------------+---------------+---------------+--------------+
     |            |               |               |              |
     v            v               v               v              v
 +--------+  +---------+   +-----------+   +----------+   +-----------+
 | User / |  | Post    |   | Feed      |   | Graph    |   | Notif     |
 | Profile|  | Service |   | Service   |   | Service  |   | Service   |
 +---+----+  +----+----+   +-----+-----+   +----+-----+   +-----+-----+
     |            |              |              |               |
     v            v              v              v               v
 +--------+  +---------+   +-----------+   +----------+   +-----------+
 | UserDB |  | Post DB |   | Timeline  |   | Graph    |   | Notif     |
 |        |  |         |   | Store     |   | Store    |   | Inbox     |
 +--------+  +----+----+   +-----------+   +----------+   +-----------+
                  |
                  | media_ids
                  v
           +------+-------+         +----------------+
           | Media Svc    |-------> | Object Store   |
           | process Q    |         | originals      |
           +------+-------+         +--------+-------+
                  |                          |
                  v                          v
           +------+-------+         +--------+-------+
           | Transcode /  |         | CDN / Edge     |
           | thumbs fleet |         | image/video    |
           +--------------+         +----------------+

           Fanout workers <--- PostCreated events (Kafka)
                |
                +--> Timeline store (non-celeb)
                +--> Celeb recent index (celeb path)
                +--> Ranker candidate hooks
```

**Publish path:**

```text
presign upload → PUT bytes → media processing → READY
POST /posts (idempotency)
  -> insert Post
  -> emit PostCreated
  -> async fanout / celeb index
  -> 201
```

**Home feed path:**

```text
GET /feed/home
  -> load timeline segment for user (push posts)
  -> fetch recent posts from followed celebrities (pull)
  -> merge by ts/score; filter mute/block/deleted
  -> hydrate Post + Media URLs + counters
  -> return page + cursor
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Post ACK ⇒ durable metadata** with media refs (media may still process).  
2. **Idempotent post create.**  
3. **Private/ACL enforced** on detail and feed hydrate.  
4. **Fanout at-least-once**; timeline dedup by `post_id`.  
5. **Deletes tombstone**; feeds filter tombstones.  
6. **Counters approximate short-term OK**; reconcile later.

#### 5.1.2 Data loss

| Risk | Mitigation |
|------|------------|
| Lost fanout | Kafka replay PostCreated; rebuild timelines |
| Lost media | Multi-AZ object store; checksum |
| Timeline Redis loss | Rebuild from follows×recent posts for active users |
| Notif loss | Best-effort; durable inbox preferred |

#### 5.1.3 Idempotency & retry

```text
Post create: Idempotency-Key
Fanout worker: write timeline entry idempotent (owner_id, post_id)
Like: unique (user_id, post_id)
Media process: task per media_id version
```

#### 5.1.4 Rate limits

| Limit | Why |
|-------|-----|
| Posts / day / user | Spam |
| Follows / hour | Graph abuse |
| Likes / min | Botting |
| Feed QPS / token | Scraping |
| Upload bytes / day | Cost abuse |

#### 5.1.5 Failure modes by scale

| Scale | Failure | Mitigation |
|-------|---------|------------|
| Baseline | Fanout worker crash | Kafka replay idempotent writes |
| 10× | Celebrity mistaken push | Threshold T + auto detect |
| 100× | Timeline hot partition | Shard owner; trim |
| 1,000× | Cross-region lag | Home region users; eventual |

#### 5.1.6 Retries & idempotency

```text
Fanout write key (owner_id, post_id) unique
Like: (user_id, post_id) unique; counter INCR once
Media webhook: media_id state machine
```

#### 5.1.7 Data-loss prevention

1. Post durable before ACK.  
2. Media in object store with checksum.  
3. Fanout at-least-once; timelines idempotent.  
4. Delete tombstones retained until fanout drains.

#### 5.1.8 Consistency under partition

```text
Author sees own post: read-your-writes via sticky/cache fill
Followers may lag — product OK
Split-brain follow edges: single home for user graph shard
```

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Jump | Change |
|------|--------|
| Baseline | SQL + Redis timelines; S3+CDN; Kafka fanout |
| **10×** | Cassandra/TAO graph; async fans; counter svc; CDN custom |
| **100×** | Hybrid celeb; ranker; home cells; media fleet autoscaling |
| **1,000×** | Retrieval+rank; regional densify; edge feed; cold media tiers |

#### 5.2.2 Timeline storage

```text
Cassandra: PK=user_id, CK=ts DESC, post_id
Trim to last N (e.g. 1000–5000) entries
Redis cache hot users' first pages
```

#### 5.2.3 Celebrity threshold

```text
is_celebrity if followers >= T or manual flag
Also detect sudden virality → flip to pull path
Fanout workers skip push for celebs; maintain celeb_recent posts index
```

#### 5.2.4 Feed ranking (hook)

```text
candidates = push_timeline ∪ pull_celebs ∪ (optional suggestions)
features = recency, affinity, media type, ...
score = ranker(candidates)
page = top after filters
```

MVP may sort by time; mention ranker for Meta flavor.

#### 5.2.5 Multi-region

| Data | Strategy |
|------|----------|
| User home cell | Sticky by user_id |
| Posts | Write home of author; replicate |
| Timelines | Prefer consumer home region |
| Media | Global object store + CDN |

#### 5.2.6 Hot keys

- Celebrity follower list reads → cache; shard adjacency.  
- Viral post counters → sharded counters.  
- Feed for celebs themselves still normal.

#### 5.2.7 Cache hierarchy

```text
CDN media; edge optional feed for logged-out
Redis: timeline segments, post objects, counters, sessions
Local API: request coalesce
Origin: Cassandra/MySQL shards
```

#### 5.2.8 Backpressure

```text
Fanout lag → prioritize recent posters; coalesce; degrade to pull for more authors
Feed rank timeout → chrono merge fallback
```

#### 5.2.9 Path evolution

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Write | async fanout | hybrid T↓ | cells + pull |
| Read | cache timelines | ranker fleet | edge assist |
| Media | multi-variant | regional origin | POP cache |

### 5.3 Maintainability

#### 5.3.1 Config

```text
celebrity_threshold: 100000
timeline_max_entries: 2000
fanout_workers: autoscaled
ranker_enabled: false  # MVP chrono merge
media_variants: [thumb, feed, full]
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `publish_qps` | Write load |
| `fanout_lag` | Feed freshness |
| `feed_p99_ms` | UX |
| `cdn_hit_ratio` | Cost/UX |
| `media_process_lag` | Pending posts |
| `celeb_pull_ms` | Hybrid health |
| `acl_deny_total` | Privacy |

#### 5.3.3 Testing

- Concurrent follows/unfollows during fanout.  
- Celebrity threshold flip mid-flight.  
- Tombstone visibility.  
- Idempotent likes.  
- Private post not in stranger feed.

#### 5.3.4 Operability

- Rebuild timeline tool for user.  
- Pause fanout; degrade to pull-all (slower).  
- Feature flag ranker.  
- Media poison queue.

### 5.4 Fanout algorithm deep dive

```text
on PostCreated(author, post):
  if followers(author) > T: mark celebrity; skip push (or push to online subset)
  else enqueue batches of followers → timeline.insert(owner, post_ref)
on ReadHome(user):
  candidates = timeline[user] ∪ pull(celebrities user follows)
  filter blocks/mutes/deletes; rank; hydrate
```

### 5.5 Media pipeline

```text
Presign upload → complete → transcoder variants (jpg/webp/mp4) → CDN
Publish when min variants ready; progressive image LQIP optional
```

### 5.6 Progressive evolution

| Stage | Fanout | Feed | Media |
|-------|--------|------|-------|
| MVP | push all | chrono | single size |
| Prod | hybrid | light rank | variants |
| Scale | cells | ML rank hook | multi-region |


---

## 6. Wrap-Up

### 6.1 What we designed

**Instagram-class** social: media pipeline + CDN, follow graph, posts, hybrid home feed (push normal / pull celebrity), likes/comments/notifs—with progressive cells and ranking hooks.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Fanout write vs read | Hybrid by follower count |
| Join-on-read | Deal-breaker at scale |
| Media in DB | Deal-breaker |
| Counters on post row | Hotspot — separate |
| Rank vs chron | Chron MVP; ranker hook |

### 6.3 30-second scale narrative

> Baseline: durable posts, S3+CDN media, Kafka fanout into timelines. 10× specialized graph/timeline stores and counters. 100× hybrid celebrity + home cells + ranker. 1,000× retrieval/rank and edge feed densification—never full push to 100M followers.

### 6.4 Deal-breakers checklist

- `JOIN follows WITH posts` per scroll at large DAU.  
- Fanout-on-write to 100M followers.  
- Media BLOBs in primary DB.  
- Ignoring private ACL on hydrate.  
- Synchronous fanout inside publish request.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & clarifying

**Q1: Instagram vs Twitter feed differences?**  
A: IG is media-heavy, grid profile, historically chron then ranked; more CDN/media pipeline emphasis—same hybrid fanout bones.

**Q2: Stories?**  
A: Ephemeral media with 24h TTL; separate store; feed injection as another candidate source.

**Q3: Reels / For You?**  
A: Candidate retrieval from many sources + heavy ranker; distinct from following feed—mention as Phase 2.

**Q4: Private accounts?**  
A: Follow requests; only approved followers get fanout / pull visibility.

**Q5: Ads in feed?**  
A: Mixer inserts ad candidates with pacing—out of MVP but leave slot in merge.

### 7.2 Fanout & feeds

**Q6: Exact celebrity threshold?**  
A: Tunable; based on write amp SLO; 10K–1M depending on infra.

**Q7: How merge push+pull?**  
A: k-way merge by timestamp/score; dedupe `post_id`; apply filters.

**Q8: Timeline trimming?**  
A: Keep last N; older content via pull from authors when scrolling deep (rare).

**Q9: Fanout lag SLO?**  
A: Seconds typical; show optimistic on author’s devices via read-your-writes.

**Q10: Unfollow cleanup?**  
A: Lazy filter; optional async delete from timeline.

### 7.3 Graph storage

**Q11: Store follows how?**  
A: Two indexes: following list + followers list (or TAO-like associations). Sharded by user_id.

**Q12: Count denormalization?**  
A: `follower_count` cached; async accurate; accept brief drift.

**Q13: Mutual friends?**  
A: Intersection algorithms; expensive—cache for PYMK Phase 2.

**Q14: Block vs mute?**  
A: Block stronger ACL; mute feed filter only.

### 7.4 Media & CDN

**Q15: Why presigned upload?**  
A: Bypass API for bytes; API stays control plane.

**Q16: Processing order?**  
A: Validate → thumbs first (feed ready) → larger transcodes async.

**Q17: Hot video bandwidth?**  
A: CDN + adaptive streaming; origin shield; cache keys by variant.

**Q18: Private media?**  
A: Signed URLs short TTL; or cookie-auth at CDN edge.

**Q19: Image sizes math?**  
A: Always serve resized variants; never ship 12MP to mobile feed.

### 7.5 DB, indexing, IDs

**Q20: Post ID design?**  
A: Time-sortable IDs help range scans; snowflake style.

**Q21: Profile grid query?**  
A: `(author_id, created_at DESC)` index / cluster.

**Q22: Feed cursor?**  
A: `(ts, post_id)` opaque cursor; stable under inserts.

**Q23: Search users?**  
A: Prefix index / search service; separate from feed path.

**Q24: Sharding posts?**  
A: By `post_id` or `author_id`; profile queries prefer author_id shard.

### 7.6 Caching & LB

**Q25: What to cache?**  
A: First feed page, post hydrate, user stubs, celebrity recent, CDN media.

**Q26: Cache invalidation?**  
A: Delete post → purge keys; like counts may be slightly stale.

**Q27: Thundering herd?**  
A: Singleflight / request coalescing for viral post hydrate.

**Q28: Edge feed cache?**  
A: Hard for personalized feeds; cache fragments (post bodies) not whole home.

### 7.7 Counters & notifications

**Q29: Like counter sharding?**  
A: `hash(post_id) % N` strips; sum on read; or Redis INCR + flush.

**Q30: Notification amplification?**  
A: Celebrity like storms → aggregate (“1000 others liked”); don’t write 50M notif rows.

**Q31: Exactly-once like?**  
A: Unique constraint; idempotent POST.

### 7.8 Consistency & multi-region

**Q32: Read-your-writes after post?**  
A: Read author profile from primary / session stickiness.

**Q33: Cross-region follow?**  
A: Graph updates to home of both users or async replicate with lag.

**Q34: Feed eventual consistency OK?**  
A: Yes—seconds lag acceptable; explain UX.

### 7.9 Algorithms

**Q35: Ranking features (high level)?**  
A: Affinity, recency, engagement probability, content type diversity, seen filters.

**Q36: Seen filter?**  
A: Bloom or stored seen set per user with TTL—avoid reshown posts.

**Q37: Hashtag index?**  
A: Post→tags emit; tag timelines similar to user timelines with abuse controls.

### 7.10 Estimation & deal-breakers

**Q38: Fanout 50K posts/s × 300 followers?**  
A: 15M writes/s—need batching, trimming, hybrid.

**Q39: Pure pull for everyone?**  
A: Read CPU explodes: each feed merges hundreds of author indexes—works small, fails Meta DAU without heavy caching/retrieval stack.

**Q40: Closing Meta line?**  
A: “I’d upload media via presigned URLs and CDN, store posts durably, and build home feed with hybrid fanout—push for normal accounts, pull for celebrities—then hydrate through caches, leaving a ranker slot for relevance.”

---

### 7.11 Extra depth

**Q41: Album / multi-image posts?**  
A: Post has ordered `media_ids`; carousel client-side.

**Q42: Edit caption?**  
A: Update post row; timelines keep id; hydrate sees new caption.

**Q43: Soft delete vs hard?**  
A: Tombstone first for fanout correctness; GC later.

**Q44: GDPR delete?**  
A: Delete/anonymize posts & media; purge CDN; graph edges.

**Q45: Abuse spam follow?**  
A: Rate limits; graph anomaly; challenge.

**Q46: Feed diversity?**  
A: MMR/diversity rerank so one creator doesn’t dominate page.

**Q47: Offline timeline densification?**  
A: Precompute for active users; lazy for dormant.

**Q48: Why Kafka for PostCreated?**  
A: Multiple consumers: fanout, search index, notifs, counters, ML features.

**Q49: Can timelines live only in Redis?**  
A: Cache yes; durable store needed for restart/rebuild—dual write or Redis+AOF with care.

**Q50: Scope cut for interview?**  
A: Nail hybrid feed + media pipeline + graph; defer DMs, Shopping, Live.

---

## Appendix A — End-to-end sequence (publish + fanout)

```text
1. Client requests presigned upload; PUT original to object store
2. Upload-complete → Media PROCESSING (scan + variants)
3. Media READY → client POST /posts {media_ids, caption} + Idempotency-Key
4. Post Service inserts Post; emits PostCreated to Kafka
5. Fanout workers:
     if author.followers < T: push TimelineEntry to each follower
     else: write CelebRecent index only
6. Counters/search/notifs consumers react
7. Author profile read-your-writes shows post immediately
8. Followers see post via timeline push or celeb pull on next feed fetch
```

## Appendix B — Home feed merge pseudocode

```text
def home_feed(user, cursor, n):
  pushed = timeline_store.page(user, cursor, n)
  celebs = following_celebs(user)
  pulled = concat([celeb_recent(c, since=cursor_ts) for c in celebs])
  candidates = dedupe(pushed + pulled)
  candidates = filter_blocked_muted_deleted_private(user, candidates)
  ranked = ranker_or_chrono(candidates)
  page = ranked[:n]
  hydrate = posts_batch(page) + media_urls + counters
  return hydrate, next_cursor
```

## Appendix C — Fanout worker batching

```text
consume PostCreated
followers = graph.followers(author)  # paginated
skip if is_celebrity(author)
for chunk in followers.chunks(1000):
  bulk_write timeline entries (author_filter already applied)
  backoff on hot partitions
trim timelines exceeding MAX_ENTRIES asynchronously
```

## Appendix D — Celebrity flip

```text
on follower_count crossing T:
  mark is_celebrity=true
  stop push fanout
  ensure celeb_recent index warm
optional: do not rewrite historical timelines
feed read path already merges pull
```

## Appendix E — Media variant matrix

| Variant | Use | Typical |
|---------|-----|---------|
| `thumb` | Grid | ~200px webp |
| `feed` | Home | ~1080px webp |
| `full` | Detail zoom | large |
| `video_poster` | Video | frame |
| `hls_360/720` | Video play | ABR |

Feed should prefer `feed`/`hls_auto`; never original.

## Appendix F — Privacy / ACL checklist

```text
private account ⇒ only approved followers
blocked ⇒ bidirectional hide
deleted ⇒ tombstone
close-friends lists (Phase 1.5) ⇒ separate allowset
signed media URLs for non-public
hydrate path re-checks ACL (never trust timeline alone)
```

## Appendix G — Counter service sketch

```text
LIKE(user, post):
  if sifadd(like_set): redis.incr(like_count); enqueue durable
READ: redis.get + fallback DB
RECONCILE: daily recount samples / anomaly repair
SHARD: like_count#{post%N} strips for viral posts
```

## Appendix H — Notification aggregation

```text
if author.is_celebrity and event=like:
  aggregate buffer → "X and N others liked your post"
else:
  per-event inbox item (rate limited)
never 1:1 notif row per like at mega scale
```

## Appendix I — Capacity worksheet

```text
publish_qps = ______
avg_followers_non_celeb = ______
fanout_write_qps ≈ publish_qps × avg_followers × (1 - celeb_post_fraction)
feed_qps = ______
hydrate_miss_ratio = ______
cdn_egress_gbps = ______
graph_edges ≈ users × avg_follows
```

## Appendix J — Progressive scale checklist

| Scale | Must say |
|-------|----------|
| Baseline | Kafka fanout, Redis/SQL timelines, S3+CDN |
| 10× | Graph store, counter svc, async fans, CDN |
| 100× | Hybrid celeb, home cells, ranker hook |
| 1,000× | Retrieval+rank, edge fragment caches, media tiers |

## Appendix K — Deal-breaker checklist

1. Join follows×posts on every home scroll at large DAU  
2. Push fanout to 100M followers  
3. Media BLOBs in primary DB  
4. Sync fanout inside publish request  
5. Trust timeline entry without ACL hydrate  
6. Like counter UPDATE on hot post row  

## Appendix L — Read-your-writes tactics

```text
sticky session to author home for profile
or "recent_posts" cache in user session after create
feed may lag seconds for others — OK
```

## Appendix M — Failure matrix

| Failure | Effect | Mitigation |
|---------|--------|------------|
| Fanout lag | Stale follower feeds | Scale workers; pull fallback |
| Media process down | Pending posts | Retry; thumbs-first |
| Timeline cache loss | Rebuild / pull densify | Durable timeline store |
| Graph outage | Follow fails | Fail write; feed degraded |
| CDN origin hot | Slow media | shields; more replicas |

## Appendix N — Ranking hook features (verbal)

```text
P(engage | user, post) ≈ f(affinity, recency, media_type, unseen, author_quality)
diversity penalty for same author
light exploration slot optional
MVP: chrono merge still acceptable if stated
```

## Appendix O — Meta interview closing

> “I’d treat Instagram as media + graph + hybrid feed: presigned uploads to object storage and CDN, durable posts with async fanout for normal accounts, pull paths for celebrities, and a hydrate layer that enforces ACL and serves counters from a separate hot path—leaving a ranker slot for relevance.”

## Appendix P — 30-minute interview checklist

1. Clarify posts/media, follow model, feed ranking, private accounts, celebs.  
2. BOTE: fanout writes/s and feed QPS; media TB/day.  
3. Draw upload → post → Kafka → fanout/celeb index → feed merge → CDN.  
4. Deep dive hybrid fanout + ACL hydrate.  
5. Scale 10×/100×/1,000×.  
6. Deal-breakers.

## Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Fanout-on-write | Push post ids into follower timelines |
| Fanout-on-read | Pull authors’ recent posts at read |
| Hybrid | Thresholded mix of push + pull |
| Timeline | Per-user ordered post-id list |
| Hydrate | Fetch post/media/counter bodies |
| Celeb | High-follower account on pull path |
| Tombstone | Soft-delete marker |

## Appendix R — Stories extension (pointer)

```text
media with expires_at = now+24h
story ring API separate from home feed
fanout lighter (active viewers) or pull
GC job deletes media after expiry
```

## Appendix S — Comparison: push-all vs hybrid vs pull-all

| | Push-all | Hybrid | Pull-all |
|--|----------|--------|----------|
| Write amp | Worst | Bounded | Best |
| Read cost | Best | Medium | Worst |
| Celeb OK? | No | Yes | Yes |
| Meta choice | No | **Yes** | Only small |

## Appendix T — What to draw first on the whiteboard

```text
1) Client → API → Post DB
2) Media → S3 → CDN
3) Kafka PostCreated
4) Fanout workers → Timeline store
5) Celeb recent index
6) Feed service merge → hydrate → client
```

## Appendix U — NFR card (say in 20 seconds)

```text
Publish ACK p99 < 300ms (fanout async)
Feed p99 < 100–200ms (cached timeline + batch hydrate)
Media via CDN; origin shielded
Private ACL re-checked at hydrate
Celebrity never full push fanout
Counters eventually consistent OK
```

## Appendix V — Common interviewer pushbacks

| Pushback | Response |
|----------|----------|
| “Just use Postgres timelines” | OK tiny; fails write amp + celeb |
| “Pull everyone always” | Read CPU / fan-in explodes at DAU |
| “Ranker is the whole design” | Still need candidate gen + media + graph |
| “Store images in MySQL” | Deal-breaker for bytes |
| “Sync fanout in request” | Publish latency + failure coupling |

---

## Appendix W — Anti-patterns (deepened)

| Anti-pattern | Why | Instead |
|--------------|-----|---------|
| Push to 50M followers sync | Meltdown | Hybrid pull |
| Timelines only Redis | Data loss | Durable store + cache |
| Counters on post row | Hotspot | Counter service |
| Feed HTML on CDN | Personalized | JSON IDs + CDN media |
| Ignore delete tombstones | Ghost posts | Filter + invalidate |
| Global linearizable feed | Impossible UX cost | Eventual OK |
| Unbounded fanout lag silent | Trust break | SLO + degrade pull |

## Appendix X — 90s pitch

> “Instagram: media to blob/CDN, hybrid fanout with celebrity pull, thin timeline IDs, rank+hydrate on read, counters aside. Scale is managing write amplification and hot keys—not a single MySQL feed table.”




## Appendix Y — Numeric drills & deal-breakers card

```text
50M posts/day × 300 followers × 32B ≈ 480GB/day timeline writes (push)
Celebrity 50M followers: push = DEAL-BREAKER → pull on read
Media 50M × 200KB ≈ 10TB/day
Like counter: 100K/s → Redis INCR not SQL row
DEAL-BREAKERS: sync fanout in API; Redis-only timelines; ignore tombstones; CDN HTML feed
```

### Extra: read/write path evolution detail

| Jump | Write change | Read change |
|------|--------------|-------------|
| →10× | Batch fanout workers | Timeline cache mandatory |
| →100× | Lower T; online-only push subset | Ranker timeout fallback |
| →1,000× | Cell fanout; pull-heavy | Home cells + edge media |



## Appendix Z — Failure modes by scale (quick card)

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Duplicate posts | Idempotency-Key |
| 10× | Fanout lag | More workers; batch |
| 100× | Celebrity misclass | Adaptive T + metrics |
| 1,000× | Cell imbalance | Rebalance home users |

## Appendix AA — Consistency under partition (feed)

```text
Author region vs follower region: eventual fanout OK
Block edge must be checked on read even if timeline has entry
Media origin down: serve CDN cached variants; delay new publishes
```



## Appendix AB — Interview “what to say” (Instagram)

> “Hybrid fanout with celebrity pull, media on CDN, thin timeline IDs, counters aside, privacy/tombstones on read. BOTE the write amplification first—if you can’t explain why push-all fails at 50M followers, you haven’t started.”

### Extra BOTE: notification amplification

```text
Like notify author: coalesce (N likes → 1 push “and 40 others”)
Follow requests: rate limit; don’t fan notify graph
At 100K likes/s global, naive per-like push = deal-breaker
```


*End of Meta system design: Instagram.*
