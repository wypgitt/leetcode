# System Design: X / Twitter (Home Timeline & Posting)

> **Focus areas:** Post write path · Hybrid fanout · Celebrity / hot-key problem · Timeline cache · Follow graph · Search nearline · Idempotency · Rate limits · Multi-region  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split post/fanout/timeline/search QPS, explicit celebrity strategy, Netflix interview variant of a classic social feed  
> **Interview theme:** Design an X/Twitter-class system: post, follow, home timeline — without melting on celebrity write fanout

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

Goal: **bound a social feed**—durable posts, follow graph, low-latency home timeline, and a strategy for users with millions of followers.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Post + follow + home timeline (+ light search) | Full ads auction / Spaces live audio |
| Ranking | Chronological MVP + light rank hooks | Full “For You” research paper |
| Media | Async upload + CDN | Netflix VOD pipeline |

### 1.1 Functional Requirements

| # | Question | Answer | Implication |
|---|----------|--------|-------------|
| F1 | Post content? | Text + optional media/links | Post service + object store |
| F2 | Home timeline? | Posts from followees | Fanout / merge |
| F3 | Follow graph? | Directed edges | Graph store sharded |
| F4 | Celebrity? | Yes, millions of followers | Hybrid fanout mandatory |
| F5 | Likes/reposts? | Eventual counts OK | Counter service |
| F6 | Deletes/edits? | Tombstone / version | Propagation |
| F7 | Search? | Recent keyword Phase 1 | Nearline index |
| F8 | Blocks/mutes? | Enforce on read (+ fanout skip) | Filter layer |
| F9 | Rate limits? | Anti-spam | Token buckets |
| F10 | Notifications? | Async | Out of post ACK path |
| F11 | Idempotency? | Double-tap safe | Client keys |
| F12 | Ranking? | Chrono MVP; ML optional | Rank interface |

**MVP:** create post (idempotent), follow/unfollow, hybrid fanout, home timeline read with block/mute filters, media async, rate limits, soft delete, metrics.

**Out of MVP:** Encrypted DMs, full global search, live audio, perfect read-after-write across regions for all followers.

### 1.2 Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Post ACK p99 | < 200–300ms in-region (fanout async) |
| Timeline p99 | < 200–400ms warm cache |
| Durability posts | Quorum before ACK |
| Fanout lag | Seconds typical; celebs via pull |
| Availability | 99.9%+ read; degrade rank→chrono |
| Consistency | RYW for author; followers eventual |

### 1.3 Cases

Happy: post→async fanout→followers see; celeb post→pull on read; follow→see recent; delete→tombstone.

Edge: duplicate post; fanout lag; celeb storm; blocked user still fanned (filter); Redis timeline loss; search lag; media not ready; rate limit; hot partition.

### 1.4 Scales

| Metric | 1× | 10× | 100× | 1,000× |
|--------|----|-----|------|--------|
| DAU | 20M | 200M | 500M | 1B |
| Peak posts/s | 1K | 10K | 50K | 200K |
| Peak timeline reads/s | 50K | 500K | 2M | 10M |
| Peak fanout writes/s | 100K | 1M | hybrid | hybrid |
| Edges in graph | 2B | 20B | 100B | 500B |

**Forces:** hybrid fanout, timeline cache clusters, graph sharding, celebrity pull, regional cells.

### 1.5 Scope

> Design X/Twitter-class posting and home timeline with **hybrid fanout**, timeline caches, follow graph, and celebrity read-merge — progressive 10×/100×/1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Naive fanout trap (celebrity math)

```text
Baseline peak posts                    = 1,000 / s
Avg followers / author (median)        ≈ 200
Naive fanout writes                    = 1,000 × 200 = 200,000 / s  (manageable)

One celebrity post (50M followers):
  Write fanout                         = 50,000,000 timeline ZADD ops
  At 1 ms/write                        = 13.9 hours — deal-breaker

Even 1% of posts from authors > 100K followers at 1K posts/s:
  10 posts/s × 100K followers          = 1,000,000 fanout writes / s — melts cluster
```

**Interview crux:** hybrid fanout is mandatory, not optional optimization.

### 2.2 Hybrid fanout steady-state math

Assume follower distribution:

```text
99% authors have < 10K followers     → write fanout
1% authors have ≥ 10K (celebrity)    → pull on read

Effective fanout writes:
  990 posts/s × 200 avg followers      ≈ 198,000 / s
  10 celeb posts/s × 0 write fanout    = 0
Total                                  ≈ 200K / s baseline (async workers)

Celebrity read amplification:
  500K timeline reads/s × 10% follow ≥1 celeb × pull 20 posts
  ≈ 500K × 0.1 × 20 = 1M post-id lookups/s (hydrate batch) — cacheable
```

### 2.3 Timeline read path

```text
Peak timeline reads (baseline)       = 50,000 / s
Cache hit rate (warm users)          ≈ 90%
Cache origin QPS                     = 5,000 / s
Entries / user timeline cap          ≈ 800 post ids × 16 B ≈ 12.8 KB
200M DAU × 12.8 KB (not all resident)  hot set ~20M users × 12.8 KB ≈ 256 GB class
With replication ×3                  ≈ 768 GB Redis/MemoryDB cluster
```

### 2.4 Post storage growth

```text
Posts / day (baseline)               = 1K/s × 86,400 ≈ 86M / day
Post metadata ~500 B                 → 43 GB / day
Media separate (object store)        → PB class lifecycle
365-day metadata hot                 ≈ 15 TB before compaction/tiering
```

### 2.5 Graph storage

```text
Edges (baseline)                     ≈ 2B follow relationships
Edge record ~32 B                    ≈ 64 GB (+ indexes ×2–3)
Shard by follower_id for home fanout iteration
Secondary index by followee_id for celebrity follower lists (optional cache)
```

### 2.6 QPS classes (split — never blend)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Post write (ACK path) | 1K/s | 10K/s | 200K/s | durable persist |
| Fanout write (async) | 200K/s | 2M/s | hybrid | workers, not ACK |
| Timeline read | 50K/s | 500K/s | 10M/s | cache fronted |
| Graph read (follow list) | 20K/s | 200K/s | 2M/s | sharded |
| Celebrity pull merge | 5K/s | 50K/s | 500K/s | on cache miss / celeb follow |
| Search index (nearline) | 1K/s ingest | 10K/s | 100K/s | CDC async |
| Hydrate post bodies | 50K/s | 500K/s | 5M/s | batch MGET |

### 2.7 Latency budget

| Stage | Budget |
|-------|--------|
| Post persist + outbox | 50–100 ms |
| Post ACK total p99 | < 200–300 ms |
| Timeline cache page | 5–20 ms |
| Celebrity merge + hydrate | 30–80 ms |
| Block/mute filter | < 5 ms |
| **Timeline p99 total** | **< 200–400 ms** |

### 2.8 Fanout worker throughput

```text
Target per worker: 5K ZADD/s
200K fanout/s ÷ 5K                     ≈ 40 workers baseline
Celeb excluded from write fanout       → bounded horizontal scale
Outbox partition by author_id          → ordering per author
```

### 2.9 Critical bottlenecks

1. **Celebrity write fanout** — single post → tens of millions of writes.  
2. **Hot graph partition** — mega-celeb follower list fetch.  
3. **Timeline cache stampede** — cold start / Redis flush.  
4. **Sync search index on write** — blocks ACK path.  
5. **Unbounded media on post ACK** — must async attach.

### 2.10 Cost intuition

```text
Dominant: timeline cache RAM + fanout write throughput + post storage
Track: $/1M timeline reads, fanout_lag_p99, celeb_pull_ratio
Cheaper to pull 50M followers on read (batched) than push 50M ZADD once
```

### 2.11 Deal-breaker

**Always fanout-on-write for all authors** — one celebrity post becomes a fleet-wide incident.

---

## 3. High-Level Design

### 3.1 Planes

```text
Write: Post API → durable store → outbox → fanout workers
Read: Timeline API → cache + celebrity pull → hydrate posts → filter
Graph: Follow service
Media: upload → object/CDN → attach
Search: CDC → index (async)
```

### 3.2 Hybrid fanout

```text
THRESH ≈ 10_000 followers (tune)
if followers < THRESH: fanout-on-write to follower timeline caches
else: mark celebrity; readers pull author’s recent posts when merging home
```

### 3.3 Timeline cache

Redis/MemoryDB sorted sets per user: `tweet_id → ts`, cap ~800–2000. Trim old.

### 3.4 Post ACK vs visibility

ACK after durable persist (+ outbox). Followers may see seconds later — state explicitly.

### 3.5 Filters

Blocks/mutes applied at read merge; fanout may skip known blocks best-effort.

### 3.6 Trade-offs

| Topic | Choice |
|-------|--------|
| Fanout | Hybrid |
| ACK | Durable post, async fanout |
| Counts | Eventual |
| Search | Nearline |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+   POST    +------------+   durable   +------------+
| Client |---------->| Post API   |------------>| Post Store |
+--------+           +-----+------+             +------+-----+
                         | outbox                      |
                         v                             v
                   +-----+------+                 +----+-----+
                   | Fanout Q   |---------------->| TL Cache |
                   +------------+                 +----+-----+
                                                       ^
+--------+   GET home   +------------+   merge        |
| Client |------------->| Timeline   |----------------+
+--------+              | API        |---- pull celebs
                        +-----+------+
                              v
                         Post hydrate + block filter
```

### 4.2 Celebrity path

```text
Celeb posts → Post Store only (+ celeb recent index)
Reader following celeb → merge celeb recent since watermark into home page
```

### 4.3 Follow

```text
Follow write → Graph store
Optional: backfill recent posts of followee into follower cache (bounded)
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. **Post durable before ACK**.  
2. **Idempotent create** by client key.  
3. **No full write-fanout for celebrities**.  
4. **Timeline reads filter blocks/mutes**.  
5. **Deletes tombstone**; caches converge.  
6. **Home-cell writes** per author.  
7. **Fanout at-least-once**; timeline idempotent ZADD.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG posts; Redis TL; kafka fanout |
| 10× | Graph shards; media CDN; rate limits |
| 100× | Cells; celebrity thresholds; search cluster |
| 1,000× | Active-follower bitsets; regional TL; light ranker |

### 5.3 Maintainability

Metrics: `fanout_lag`, `timeline_p99`, `celeb_pull_ratio`, `cache_hit`, `post_dup_rate`. Replay fanout from outbox.

### 5.4 Exact algorithm: hybrid fanout on post

```text
function onPostCreated(post):
  persist(post)                         // quorum before ACK
  outbox.enqueue(FanoutJob(post.id, post.author_id))

function fanoutWorker(job):
  author = loadAuthor(job.author_id)
  if author.follower_count >= THRESH:   // e.g. 10_000
    indexCelebRecent(post)              // sorted set author:recent only
    return CELEBRITY_SKIP

  followers = graph.followersOf(job.author_id, shard=job.shard)
  for batch in chunks(followers, 500):
    pipe = timelineCache.pipeline()
    for follower_id in batch:
      if not isBlocked(follower_id, job.author_id):  // best-effort skip
        pipe.zadd(tlKey(follower_id), post.id, post.ts)
        pipe.zremrangeByRank(tlKey(follower_id), 0, -801)  // cap 800
    pipe.execute()
```

At-least-once outbox → ZADD is idempotent (same post_id score unchanged).

### 5.5 Exact algorithm: home timeline merge

```text
function homeTimeline(user_id, cursor, limit):
  page = timelineCache.zrevrange(tlKey(user_id), cursor, limit)  // write-fanout ids
  celeb_followees = graph.following(user_id).filter(f -> f.followers >= THRESH)
  celeb_posts = []
  for celeb in celeb_followees:
    since = watermark(user_id, celeb.id)  // last merged celeb post ts
    celeb_posts += celebRecentIndex.range(celeb.id, since, now, limit=50)
  merged = mergeSortByTs(page, celeb_posts)
  merged = filterBlocksMutes(user_id, merged)
  posts = hydrateBatch(merged[:limit])  // MGET post store / cache
  return posts, nextCursor(merged)
```

```text
function mergeSortByTs(listA, listB):
  // Two-pointer merge by (ts desc, post_id desc) — O(n+m)
  ...
```

### 5.6 Timeline cache rebuild (cold miss)

```text
function rebuildTimeline(user_id):
  if not singleflight.tryLock(user_id): return waitPeer(user_id)

  following = graph.following(user_id)
  normal = [f for f in following if f.followers < THRESH]
  recent = postStore.recentPostsForAuthors(normal, k=50 each)
  celeb = homeTimeline(user_id, ...).celeb_posts  // pull path
  merged = mergeSortByTs(recent, celeb)[:800]
  timelineCache.zaddBulk(user_id, merged)
  singleflight.release(user_id)
```

### 5.7 Snowflake IDs & ordering

```text
post_id = (timestamp_ms << 22) | (shard_id << 12) | sequence
Benefits: roughly time-ordered range scans; merge without extra index
Tie-break: higher post_id wins when ts equal (deterministic)
```

### 5.8 Scale-specific architecture

**1× (1K posts/s, 50K TL reads/s)**  
PostgreSQL/Cassandra posts; Redis timeline ZSETs; Kafka fanout; THRESH=10K; single region.

**10× (10K posts/s, 500K TL reads/s)**  
Graph shards by follower_id; fanout worker pool autoscale; celeb recent index in Redis; rate limits per user/IP.

**100× (50K posts/s, 2M TL reads/s)**  
Regional cells; timeline cache per region; active-follower bitsets to skip inactive fanout (optional 30–50% savings); search cluster via CDC.

**1,000× (200K posts/s, 10M TL reads/s)**  
Light ranker on merged slice only; fanout to **active users** in last 7d via bloom/bitset; celeb pull fully default above 50K followers; multi-tier timeline (RAM → SSD cache).

### 5.9 Active-follower optimization (100×+)

```text
function fanoutWorker(job):
  if author.follower_count >= THRESH: return CELEBRITY_SKIP
  followers = graph.followersOf(job.author_id)
  active = followers.filter(f -> lastActive(f) within 7d)  // bloom/bitset
  // fanout only to active (~20–40% of followers typically)
  // inactive users rebuild via pull on next login
```

Savings: 200K fanout/s × 0.6 inactive skip → **120K writes/s avoided** — state explicitly in interview.

### 5.10 Progressive deep dive (substantive)

**1×:** Prove hybrid math with 50M-follower example; Redis TL cap 800; async ACK.  
**10×:** Shard graph; outbound rate limits; dual index followers_of / following_of.  
**100×:** Active-follower fanout; regional TL; search nearline only.  
**1,000×:** Rank top-100 from merged pool; celeb THRESH may rise to 50K based on fanout_lag metrics.

Authn; abuse ML; URL safety scans async; private accounts enforce on read/fanout.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Fanout | Hybrid threshold |
| ACK | Durable then async |
| Celeb | Pull/merge |
| TL | Cached sorted ids |
| Search | Nearline |

### 6.2 Risks

1. Threshold mis-tune  
2. Cache loss rebuild cost  
3. Block filter bugs  
4. Fanout debt after outage  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Post/timeline/follow scope |
| 5–15 | Write path + idempotency |
| 15–25 | Hybrid fanout + celeb math |
| 25–35 | Timeline read merge |
| 35–45 | Scale, search, traps |

---

## 7. Deeper / Related Interview Questions

**Q1. Why hybrid?**  
A: Write fanout efficient for normal users; celebrities make write amplification impossible.

**Q2. Exact THRESH?**  
A: Data-driven; start 5–20K; monitor.

**Q3. RYW for author?**  
A: Author timeline reads home store, not only cache.

**Q4. Unfollow?**  
A: Remove edge; optional scrub cache; read filter until scrubbed.

**Q5. Order guarantee?**  
A: Per-user timeline roughly by ts/id; global total order not required.

**Q6. Search consistency?**  
A: Seconds–minutes lag OK if stated.

**Q7. Viral reply storms?**  
A: Rate limit; sample notifications.

**Q8. Trap: “Cassandra alone solves fanout”?**  
A: Still need product-level hybrid strategy.

**Q9. Quote tweets / retweets?**  
A: New post referencing original; counts async.

**Q10. Soft vs hard delete?**  
A: Tombstone first; GC later for legal/media.

**Q11. Timeline warm after login?**  
A: Prefetch; backfill on follow.

**Q12. Graph partition key?**  
A: Shard edges by `follower_id` for home read; secondary index by followee for fanout.

**Q13. Dual indexes cost?**  
A: Yes — fanout needs followee→followers list.

**Q14. Memory of TL cache?**  
A: Cap entries; hydrate bodies separately.

**Q15. Push notifications?**  
A: Separate pipeline; never block post.

**Q16. Ads in timeline?**  
A: Inject at merge/rank with disclosure; separate system.

**Q17. Clock skew?**  
A: Server ids/timestamps.

**Q18. Partial fanout failure?**  
A: Retry workers; repair scans.

**Q19. Metrics that page?**  
A: Fanout lag SLO; post error rate; timeline p99 burn.

**Q20. Comparison Insta/FB?**  
A: Same hybrid themes; ranking heavier; media ratios differ.

### 7.21 Active-follower fanout?

**Q: Fanout to all followers or only active?**  
A: At 100×+, fanout only to users active in last 7d (bitset/bloom); inactive rebuild on login via pull. Saves ~30–50% writes — state tradeoff explicitly.

### 7.22 Timeline cap size?

**Q: Why 800 entries not unlimited?**  
A: RAM bound per user × DAU. 800 × 16B × 20M hot users ≈ 256 GB class. Older posts fall off cache but remain in post store for profile/deep scroll.

### 7.23 Outbox vs dual-write?

**Q: How guarantee fanout after post ACK?**  
A: Transactional outbox: post row + outbox row in same TX; workers consume outbox at-least-once; ZADD idempotent.

### 7.24 Hydrate vs store ids only?

**Q: Why not store full post in timeline cache?**  
A: Post bodies large (media refs, edits); cache stores ids only; batch hydrate from post store / CDN on read — separates hot timeline from fat payload.

### 7.25 Misclassified celebrity?

**Q: Author crosses THRESH after follow — what happens?**  
A: Denormalized follower_count updated async; next post uses pull path; optional scrub of bloated TL entries from prior write-fanout era (lazy).

### 7.26 Metrics that page?

**Q: Top 3 alerts?**  
A: `fanout_lag_p99` > 30s, post error rate spike, timeline p99 burn rate. Secondary: celeb misclassification (fanout writes to mega-author).

---

## 8. Appendices

### A1. Schemas

```text
Post(post_id, author_id, text, media_ids[], created_at, state, edit_version)
Follow(follower_id, followee_id, ts)
TimelineEntry(user_id, post_id, ts)  # cache
Block(blocker_id, blocked_id)
Mute(user_id, muted_id)
```

### A2. Launch checklist

- [ ] Celebrity threshold load-tested  
- [ ] Idempotent post tested  
- [ ] Block filter tests  
- [ ] Fanout lag dashboards  
- [ ] Cache rebuild runbook  

### A3. Glossary

| Term | Meaning |
|------|---------|
| Fanout-on-write | Push ids to follower caches |
| Fanout-on-read | Pull at read time |
| Hybrid | Threshold switch |
| Hydrate | Fetch post bodies for ids |
| Tombstone | Soft delete marker |

### A4. Traps

| Trap | Pushback |
|------|----------|
| Always write fanout | Celeb melt |
| One QPS | Split classes |
| Sync search | Slows write |

### A5. Tests

1. Dup idempotency key → one post.  
2. Celeb post → no 50M writes.  
3. Block hides posts.  
4. Fanout retry → no dup TL entries.  
5. Delete disappears after converge.

### A6. 60-second summary

> Persist posts durably, **fanout asynchronously** for normal authors, **pull/merge for celebrities**, serve home from **timeline caches** with **block/mute filters**, keep search nearline — the celebrity math is the interview crux.

### A7. Related map

```text
Post API → Store → Fanout → TL Cache → Timeline API
Graph ↔ Fanout + Follow
CDC → Search
Media → CDN
```

### A8. SLO

| SLO | Target |
|-----|--------|
| Post durability ACK | 99.99% |
| Timeline p99 | < 300ms |
| Fanout lag p95 | < 5s normal |

### A9. Worked numeric example (celebrity post)

```text
Author @Star has 50,000,000 followers; THRESH = 10,000
Post at t=0:

Write path:
  persist post → ACK in 120 ms
  fanoutWorker: follower_count >= THRESH → CELEBRITY_SKIP
  fanout writes = 0

Read path (follower @Fan follows @Star + 200 normal accounts):
  TL cache page: 800 ids from write-fanout (normal accounts)
  celeb pull: recent 20 posts from @Star since watermark
  merge + filter + hydrate 20 posts
  Extra latency vs pure cache: ~15–40 ms — within p99 budget

If we had write-fanout @Star:
  50M ZADD × 1 ms = 13.9 hours — SEV-1
```

### A10. Fanout worker sizing

```text
fanout_workers = peak_fanout_zadd_per_s / worker_throughput
Baseline: 200,000 / 5,000 = 40 workers (+ 2× headroom) ≈ 80 pods
100× with active-follower 40% skip: 2M × 0.6 = 1.2M/s → 480 workers before headroom
```

### A10. Ownership

| Concern | Owner |
|---------|-------|
| Post/TL | Social core |
| Graph | Social graph |
| Fanout | Delivery workers |
| Search | Search team |
| Abuse | Safety |

### A11. Progressive checklist

| Scale | Must |
|-------|------|
| 1× | Hybrid + Redis TL |
| 10× | Graph shards |
| 100× | Cells + search |
| 1,000× | Active-bit fanout + rank |

### A12. API

```text
POST /v1/posts
GET  /v1/home?cursor=
POST /v1/users/{id}/follow
DELETE /v1/posts/{id}
```

### A13. On-call

1. Fanout lag → scale workers / shed inactive.  
2. Timeline miss storm → cache warming.  
3. Hot author misclassified → fix threshold.

### A14. Naive comparison

| Naive | Failure |
|-------|---------|
| Read join always | Too slow |
| Write always | Celeb melt |

### A15. Backfill on follow

Push last K posts of followee into follower cache asynchronously with cap.

### A16. Cost

Fanout writes and TL memory dominate; celebrity pull CPU secondary.

### A17. Non-goals

DMs; Spaces; full ads; global linearizability.

### A18. Rubric

- Hybrid fanout  
- Celeb math  
- Async ACK  
- Filters  
- Split QPS  

### A19. Edit policy

New `edit_version`; clients show “edited”; search updates async.

### A20. Private accounts

Fanout only to approved followers; read path authz.

---


### A41. Load-test scenarios

1. 10× post QPS with 1% celebrity authors — verify write amplification bounded.  
2. Timeline read 10× with 20% cold cache — singleflight rebuilds.  
3. Fanout worker kill mid-batch — at-least-once ZADD safe.  
4. Graph shard blackhole — degrade fanout; page.  
5. Search lag 1h — timeline still healthy.

### A42. Privacy notes

Private accounts: fanout only to approved followers; search excludes or gates. GDPR delete: tombstone + async purge from caches/indexes.

### A43. Comparison table

| System | Fanout bias |
|--------|-------------|
| Early Twitter | Write-heavy |
| This design | Hybrid |
| Instagram-like | More media rank |

### A44. Final checklist

- [ ] Hybrid threshold documented  
- [ ] Celeb pull path coded  
- [ ] Idempotent posts  
- [ ] Block filters  
- [ ] Fanout lag SLO  

### A45. Numeric celebrity example

```text
Post by user with 50,000,000 followers
Write-fanout cost ≈ 5e7 timeline inserts — reject this path
Pull path: each reader costs O(1) celeb recent fetch (cached) + merge
At 100K concurrent readers of home feeds including that celeb: cache celeb recent list heavily
```

### A46. Closing line

> Hybrid fanout is not an optimization footnote — it is the difference between a working social network and a self-DDoS on every celebrity tweet.

---

*End of document — Netflix system design interview prep: X / Twitter.*
