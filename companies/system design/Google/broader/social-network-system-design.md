# System Design: Social Network

> **Focus areas:** Social graph · Feed fanout · Posts · Follows · Celebrity problem · Home timeline · Notifications  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit fanout-on-write vs read tradeoffs, celebrity hybrid path, ranking vs chronology honesty, notification amplification math  
> **Interview theme:** Classic Google/Meta-style L5+ social — graph + feed at progressive DAU with hot-key celebrities

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

Goal: **bound the product**—a **Twitter/Instagram-class social network**: users follow users, publish posts, consume a home timeline/feed, handle celebrity mega-fanout, and receive notifications—for progressive scale with clear consistency and ranking tradeoffs.

### 1.0 What this is / is not

| Dimension | **Social network (this doc)** | Not this |
|-----------|-------------------------------|----------|
| Primary job | Graph + posts + home feed + notifications | Full Stories/Reels media encoding platform |
| Success | Fresh, relevant timeline; reliable publish | Perfect global ranking ML research paper |
| Graph | Directed follows (or friends) | Full People-You-May-Know ML system MVP |
| Feed | Hybrid fanout with celebrity exception | Pure search-all-posts-on-read at Google scale |
| Media | Store refs + CDN; not codec design | YouTube-scale transcode deep dive |

**Scope statement:** Design a social network with follows, posts, home timeline fanout, celebrity handling, and notifications—scaling through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Graph model? | Directed follow (Twitter-like) MVP | Adjacency lists; count denorm |
| F2 | Post types? | Text + image refs; likes/reposts Phase 1 | Post service + object store URLs |
| F3 | Home timeline? | Reverse chron MVP; ranked Phase 1.5 | Fanout + merge; ranker hook |
| F4 | User profile timeline? | User’s posts chronologically | Author index easy |
| F5 | Celebrity? | Users with huge follower counts | Hybrid fanout |
| F6 | Notifications? | Follow, like, comment, mention | Notif service + aggregation |
| F7 | Privacy? | Public posts MVP; private optional | ACL on post + graph |
| F8 | Search? | User search MVP; post search Phase 1.5 | Separate index |
| F9 | Blocks/mutes? | Yes MVP light | Filter at read/fanout |
| F10 | Counters? | Likes/followers approximate OK briefly | Eventually consistent counters |
| F11 | Media? | Upload → CDN URL on post | Image pipeline separate |
| F12 | Realtime? | Optional WS for live feed insert | Push soft real-time |

**MVP functional scope:**

1. Register/login; user profiles.  
2. Follow / unfollow; follower & following lists.  
3. Create post (text + media URLs); delete.  
4. Home timeline: posts from followed users (chronological MVP).  
5. User timeline: posts by author.  
6. Celebrity/hybrid fanout so mega-influencers don’t melt write path.  
7. Like + comment (basic); notifications for social actions.  
8. Block/mute filters.  
9. Pagination via cursors.

**Out of MVP:**

- Full TikTok For-You dense ranker (mention hooks)  
- Live streaming  
- Encrypted DMs (separate design)  
- Ads auction  
- Exact global “trending” (see trending-hashtag doc)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Publish latency | Feels instant | ACK p99 < 200–300ms; fanout async |
| N2 | Home feed read | Snappy scroll | p99 < 100–200ms |
| N3 | Durability | No lost posts after ACK | WAL/multi-AZ |
| N4 | Fanout lag | Near-real-time | p99 < 5–30s for normal users |
| N5 | Availability | Read-heavy critical | 99.9%+ feed reads |
| N6 | Consistency | Read-your-write for author; home eventual | Explicit |
| N7 | Celebrity | Must not DoS cluster | Hybrid path mandatory at scale |
| N8 | Multi-region | Global | Home-region user data; feed caches |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User A follows B → B’s new posts appear on A’s home.  
2. A posts → fans with precomputed timelines see post quickly.  
3. Celebrity C posts → not written to 80M timelines; pulled at read merge.  
4. Like → aggregated notification “X and 12 others liked…”.  
5. Unfollow → stop future fanout; optional scrub.  
6. Block → mutual invisibility in feed + notifs.  
7. Pagination: cursor of `(ts, post_id)`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| User with 50M followers posts | Celebrity path; no 50M fanout writes |
| Hot partition on celebrity ID | Shard/salt engagement; cache post |
| Fanout worker lag | Home shows slightly stale; author sees own post |
| Unfollow during in-flight fanout | Idempotent timeline insert; filter on read |
| Deleted post | Tombstone; timelines lazy-clean or filter |
| Mute word / mute user | Read-side filter |
| Mutual follow storm (spam) | Rate limits; graph anomaly |
| Counter drift | Periodic reconcile |
| Empty follow graph | Suggestions placeholder (out of deep MVP) |
| Partial media upload fail | Don’t publish until media ready / or text-only |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 10M | 100M | 1B | cell fabric |
| Peak post QPS | 2K | 20K | 200K | 2M |
| Peak feed read QPS | 50K | 500K | 5M | 50M |
| Avg follows / user | 200 | 200–300 | 300 | 400 |
| Avg followers / user | 200 | skewed | heavy skew | extreme |
| Celebrity threshold | 10K | 50K | 100K | dynamic |
| Posts / day | 50M | 500M | 5B | — |
| Fanout writes / post (avg) | ~200 | hybrid | hybrid | hybrid |
| Notifications / day | 200M | 2B | 20B | aggregate hard |
| Media objects / day | 20M | 200M | 2B | CDN |

**What each jump forces:**

- **10×:** Timeline cache (Redis); async fanout workers; notif aggregation.  
- **100×:** Hybrid celebrity mandatory; graph service; feed ranker optional; cells.  
- **1,000×:** Multi-tier caches; regional fanout; segmented celebrities; push/pull mix everywhere.

### 1.5 Etc. (Constraints & Assumptions)

- Public-by-default posts unless private accounts enabled.  
- Feed ranking can start chronological; leave ranker interface.  
- “Exactly once” timeline insert not required — idempotent `(home_user, post_id)`.  
- Soft deletes with tombstones for sync.

**Scope statement to repeat back:**

> Design a follow-graph social network with post publish, hybrid home-timeline fanout (push for normal users, pull for celebrities), engagement notifications with aggregation, and progressive scale controls for hot keys and read QPS.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Post writes** | Create post | 2K/s | 20K/s | Post service |
| **Fanout writes** | Timeline inserts | 2K×200=400K/s | hybrid | Fanout workers |
| **Feed reads** | Home timeline | 50K/s | 500K/s | Cache + TL store |
| **Graph ops** | Follow/unfollow | 5K/s | 50K/s | Graph service |
| **Engagement** | Like/comment | 20K/s | 200K/s | Engage + notif |
| **Media** | Upload | lower | ×10 | Blob + CDN |

**Anti-pattern:** quoting only “2K post QPS” while ignoring 400K/s fanout amplification.

### 2.2 Celebrity math (deal-breaker drill)

```text
Celebrity with 50M followers posts once:
Fanout-on-write = 50M timeline inserts
At 100K inserts/s → 500 seconds (~8 min) just for one post
Also storage: 50M × 32B ≈ 1.6 GB per post in timelines

Conclusion: pure fanout-on-write for celebrities = DEAL-BREAKER
```

### 2.3 Storage

```text
Post ~ 1 KB metadata (text truncated + media refs)
50M posts/day × 1 KB = 50 GB/day
Timeline entry ~ 32–64B (post_id, ts, author)
If push to 200 followers: 50M × 200 × 48B ≈ 480 GB/day timeline writes
Retain timeline 7–30 days hot; colder archive
```

### 2.4 Read amplification

```text
Home page: 1 request → 1 timeline segment + N post fetches
With Redis timeline of IDs + post cache: mostly cache hits
Miss path: merge pull celebrities + hydrate posts
```

### 2.5 Notification amplification

```text
Like on viral post: 1M likes → 1M raw notifs to author = bad
Aggregate: “1M people liked your post” with sampled actors
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/posts` | Create post |
| `DELETE /v1/posts/{id}` | Soft delete |
| `GET /v1/timelines/home?cursor=` | Home feed page |
| `GET /v1/users/{id}/posts` | User timeline |
| `POST /v1/users/{id}/follow` | Follow |
| `DELETE /v1/users/{id}/follow` | Unfollow |
| `POST /v1/posts/{id}/likes` | Like |
| `POST /v1/posts/{id}/comments` | Comment |
| `GET /v1/notifications` | Notif inbox |
| `POST /v1/users/{id}/block` | Block |

**Post schema:**

```text
Post {
  post_id, author_id,
  text, media: [url],
  created_at, visibility,
  reply_to?, root_id?,
  stats: {likes, comments, reposts}  // denormalized approx
}
```

### 3.2 Data model

| Entity | Storage | Key |
|--------|---------|-----|
| User | UserDB | `user_id` |
| Follow edge | Graph | `(follower, followee)` + reverse index |
| Post | PostDB / Bigtable | `author_id + ts + post_id` |
| Home timeline | Redis/Cassandra | `user_id → sorted post refs` |
| Celebrity flag | Graph meta | `is_celebrity` / follower_count |
| Notif inbox | NotifDB | `user_id + ts` |
| Counters | Redis | `post_id` |

### 3.3 Fanout strategies — Why X over Y

| Strategy | Pros | Cons | When |
|----------|------|------|------|
| **Fanout-on-write (push)** | Fast home read | Write amp; celebrity dies | Normal users |
| **Fanout-on-read (pull)** | Cheap write | Slow read; merge many authors | Celebrities / sparse |
| **Hybrid** | Best of both | Complexity | **Industry MVP** |
| **Ranked materialization** | Good UX | Heavy ML + cost | Phase 1.5+ |

**Chosen hybrid:**

```text
if follower_count(author) < T:
  push post_ref to each follower timeline (async)
else:
  mark as celebrity post; do not push to all
  followers pull author’s recent posts at home-read merge
```

Dynamic T (e.g. 10K–100K) based on cluster load.

### 3.4 Home timeline read merge

```text
home(user, cursor, limit):
  pushed = timeline_store.range(user, cursor, limit*2)
  celebs = following_celebrities(user)  // cached list
  pulled = merge(recent_posts(c) for c in celebs)
  filtered = apply_blocks_mutes_deletes(pushed ∪ pulled)
  ranked_or_chrono = sort(filtered)
  return page + next_cursor
```

### 3.5 Graph service

- Store forward (`follower→followee`) and reverse (`followee→followers`) indexes.  
- Follower list for fanout: iterate reverse index in chunks.  
- Cache following set for read merge (membership + celebrity subset).  
- Count denormalized with async reconcile.

### 3.6 Notifications

| Event | Sink |
|-------|------|
| New follower | Notif to followee |
| Like/comment | Aggregated notif to author |
| Mention | Notif to mentioned |
| Celebrity post (optional) | Skip or priority inbox |

Aggregation keys: `(verb, object_id, window)` → sample actors + count.

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Feed materialization | Hybrid push/pull | Scale + latency | Pure push for 50M followers |
| Timeline contents | Post IDs not bodies | Cheap fanout | Duplicate text everywhere |
| Ranking | Chrono MVP + hooks | Ship correctness first | Pretend ML without features |
| Graph | Dedicated service | Hot keys isolated | Join follows in OLTP every read |
| Notifs | Aggregate | Viral like storms | 1 row per like always |

---

## 4. Architecture Diagram

```text
  Clients (mobile/web)
           |
           v
    +------+------+
    | API Gateway |
    +--+----+-----+
       |    |
       v    v
 +-----+--+ +----+------+
 | Post   | | Graph     |
 | Service| | Service   |
 +--+--+--+ +----+------+
    |  |         |
    |  |         +---> Follower lists / celebrity flags
    |  v
    | Kafka/PubSub: post.created, engage.*, graph.*
    |        |
    |        +--> +------------------+
    |             | Fanout Workers   |-----> Timeline Store (Redis/Cass)
    |             | (skip celebs)    |
    |             +------------------+
    |        +--> +------------------+
    |             | Notif Workers    |-----> Notif Inbox
    |             | (aggregate)      |
    |             +------------------+
    v
 Post Store <-----> Media refs ---> CDN
    ^
    |
 Home API: Timeline Store + Post Cache + Celebrity Pull Merge
```

**Publish path:**

```text
POST /posts
  -> auth
  -> write Post Store (durable)
  -> ACK client (read-your-write via author timeline)
  -> emit post.created
  -> Fanout: if not celebrity, chunk followers → pipeline timeline inserts
  -> else: write celebrity recent index only
```

**Home read path:**

```text
GET /timelines/home
  -> load pushed timeline IDs
  -> merge celebrity pulls
  -> hydrate posts from cache/DB
  -> filter blocks/mutes/tombstones
  -> return
```

**Follow path:**

```text
POST follow
  -> write graph edges both directions
  -> optional backfill: recent N posts of followee into follower TL (if not celeb)
  -> notif
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Post durable before ACK.**  
2. **Fanout at-least-once**; timeline inserts idempotent on `(user_id, post_id)`.  
3. **Author always sees own post** via user timeline, independent of fanout lag.  
4. **Deletes/tombstones** eventually hide from feeds.  
5. **Blocks** enforced on read (and best-effort on fanout).  
6. **Notification aggregates** monotone counts (approx OK).

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Fanout worker crash | Kafka replay; idempotent writes |
| Timeline Redis loss | Rebuild from follow graph + posts (slow) or dual-write Cassandra |
| Graph under-count | Reconcile job from edges |
| Partial backfill on follow | Cursor backfill; user may see gap briefly |
| Notif storm | Aggregate + rate limit per inbox |

#### 5.1.3 Consistency

| Path | Model |
|------|-------|
| Author profile | Read-your-write |
| Home feed | Eventual (seconds) |
| Like counter | Eventual |
| Follow edge | Strong on graph primary; caches expire |

**Deal-breaker:** claiming strong consistent global home feed for all followers at publish ACK.

### 5.2 Scalability

#### 5.2.1 Celebrity problem (deep)

```text
Threshold T:
  - Static: followers >= 10K
  - Dynamic: move users to celebrity set when fanout lag/cost high

Celebrity write path:
  - Persist post
  - Update author recent posts index (bounded)
  - Skip reverse-index fanout

Celebrity read path:
  - Each follower caches celeb IDs they follow (~tens–hundreds)
  - On home read, fan-in recent posts (cached)
```

Optimization: **partial push** to online/active followers only; others pull.

#### 5.2.2 Hot keys

| Hot key | Fix |
|---------|-----|
| Celebrity user_id | Cache posts; shard engagement |
| Viral post likes | Sharded counters; write buffers |
| Timeline of ultra-active user | Cap TL length; sample |

#### 5.2.3 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | Redis TL; async fanout; post cache |
| 100× | Hybrid celebs; graph service; notif aggregates; regional |
| 1,000× | Cell-per-geo; active-follower push; multi-tier ranker; edge |

#### 5.2.4 Timeline storage choice

| Store | Pros | Cons |
|-------|------|------|
| Redis ZSET | Fast | Memory $; persistence care |
| Cassandra/Bigtable | Durable scale | Higher latency |
| Dual | Redis hot + durable cold | Complexity |

**MVP:** Redis for hot TL segments + durable log/store for rebuild.

### 5.3 Maintainability

- Clear interfaces: Post, Graph, Fanout, Timeline, Notif, Media.  
- Schema evolution on post protobuf.  
- Feature flags for threshold T and ranker.  
- Shadow fanout for experiments.  
- SLOs: publish ACK, fanout lag, feed p99, notif lag.

### 5.4 Ranking hook (Phase 1.5)

```text
candidates = merge(pushed, pulled, optional soft-signals)
features = author_affinity, recency, engagement, mute
score = model(features)
return top page with diversity constraints
```

Keep chrono fallback if ranker fails (reliability).

### 5.5 Security & abuse

- AuthN sessions/OAuth.  
- Rate limit posts/follows/likes.  
- Spam/bot graph detection.  
- CSRF/XSS on web; media AV scan.  
- Private accounts: approve follows; fanout only to accepted.

### 5.6 Privacy

- Block ⇒ no fanout + read filter + no notifs.  
- Protected posts invisible outside approved set.  
- GDPR delete: tombstone posts; async scrub timelines.

---

## 6. Wrap-Up

### 6.1 Design summary

A social network at scale is a **graph service** + **post store** + **hybrid timeline materialization** (push normal, pull celebrity) + **engagement/notification plane** with aggregation, fronted by caches for feed hydration.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Push vs pull | Hybrid | Two read paths |
| Chrono vs ranked | Chrono MVP | Relevance |
| Exact counters | Approx + reconcile | Drift |
| TL memory vs durability | Redis + rebuild | Rebuild cost |

### 6.3 Deal-breakers

1. Pure fanout-on-write to tens of millions of followers.  
2. Storing full post bodies in every timeline.  
3. One notif row per like on viral content.  
4. Synchronous fanout before publish ACK.  
5. Ignoring blocks on read path.

### 6.4 Progressive scale one-liner

**Baseline:** push fanout + Redis TL → **10×:** caches/workers → **100×:** hybrid celebrity + graph service → **1,000×:** cells, active-follower push, ranked feeds.

### 6.5 Interview closing line

> “We ACK after durable post write, fan out asynchronously to normal followers’ timeline caches, pull celebrity posts at read time, and aggregate notifications so virality doesn’t turn into a write amplification death spiral.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Graph

**Q1: How are follows stored?**  
A: Edge table with two indexes: by follower and by followee; counts denormalized.

**Q2: Bidirectional friends vs follows?**  
A: Friends = mutual edges or single undirected; fanout similar but privacy differs.

**Q3: List 1M followers?**  
A: Cursor pagination on reverse index; never return unbounded arrays.

**Q4: Follow backfill?**  
A: On follow, inject recent N non-celeb posts into TL; celebs appear via pull.

**Q5: Unfollow scrub?**  
A: Best-effort delete future; optional async scrub of TL entries; read filter ASAP.

### 7.2 Fanout & celebrity

**Q6: Why hybrid?**  
A: Write amp vs read amp tradeoff under extreme skew.

**Q7: How to choose T?**  
A: Cost model: `followers × post_rate` vs read merge cost; adjust dynamically.

**Q8: Partial push?**  
A: Push to online users / high-affinity; others pull — reduces writes.

**Q9: Fanout chunking?**  
A: Process followers in pages of 1K–10K; checkpoint offsets in Kafka consumer state.

**Q10: What if mid-tier influencer (80K)?**  
A: Often celebrity path; or push to active subset.

**Q11: Home merge latency?**  
A: Cache each celeb’s recent posts; parallel fetch; bound celeb count followed.

### 7.3 Feed UX

**Q12: Cursor design?**  
A: `(created_at, post_id)` opaque; stable under inserts.

**Q13: Gaps / duplicates?**  
A: Idempotent client keys; tolerate dupes; gaps possible under lag — refresh.

**Q14: “In case you missed”?**  
A: Ranker / separate candidate source Phase 2.

**Q15: Ads injection?**  
A: Separate candidate stream merged with positions constraints.

### 7.4 Posts & media

**Q16: ID generation?**  
A: Snowflake/UUID; roughly time-ordered helps ranges.

**Q17: Media upload flow?**  
A: Get signed URL → upload → confirm → publish post with URLs; CDN.

**Q18: Delete virality?**  
A: Tombstone in post store; caches TTL; TL filter; legal force-push purge jobs.

**Q19: Edits?**  
A: Optional edit with `edited_at`; invalidate caches; no re-fanout body (IDs only).

### 7.5 Notifications

**Q20: Aggregation window?**  
A: e.g. 5–60 minutes per `(user, verb, object)`.

**Q21: Online push?**  
A: WS/SSE for badge counts; inbox still durable DB.

**Q22: Quiet hours?**  
A: User settings; defer delivery.

**Q23: Mention storms?**  
A: Rate limit mentions per post; spam detect.

### 7.6 Consistency & reliability

**Q24: Read-your-write home?**  
A: Inject author’s post into response if missing and recent; or separate “pending”.

**Q25: Dual-write TL Redis+Cass?**  
A: Redis for speed; Cass source for rebuild; accept brief divergence.

**Q26: Replay fanout after bug?**  
A: Re-emit from posts log for time range; idempotent inserts.

**Q27: Exactly-once likes?**  
A: Unique `(user, post)` constraint; retries safe.

### 7.7 Scale drills

**Q28: 400K fanout writes/s memory?**  
A: Pipeline batches; Redis pipelining; drop to durable store if needed.

**Q29: 5M feed QPS?**  
A: Multi-layer cache; edge; mostly ID lists + post CDN/cache.

**Q30: Counter shards?**  
A: `hash(post_id) % N` increments; read sums; periodic rollup.

### 7.8 Alternatives & deal-breakers

**Q31: Pure pull for everyone?**  
A: OK tiny scale; at 200 follows × huge QPS merge becomes heavy without caches.

**Q32: Pure push for everyone?**  
A: Celebrity deal-breaker.

**Q33: SQL join follows⋈posts every home read?**  
A: Won’t meet p99 at scale.

**Q34: Global secondary index all posts by time?**  
A: Hotspot; not a home feed design.

### 7.9 Interview craft

**Q35: How to open?**  
A: Follow graph, post, home feed, celebrity, notifs — then amplification math.

**Q36: What numbers matter?**  
A: Post QPS, avg followers, celebrity tail, feed QPS, notif rate.

**Q37: What impresses L5+?**  
A: Hybrid fanout detail, idempotent TL, active-follower optimization, notif aggregation.

**Q38: Common mistake?**  
A: Designing feed without celebrity exception; or sync fanout before ACK.

---

### Appendix A — Fanout pseudocode

```text
on post.created(post):
  if is_celebrity(post.author_id):
     recent_index.push(post.author_id, post)
     return
  cursor = null
  while followers = graph.followersPage(post.author_id, cursor, 5000):
    timeline.batchAdd(followers.ids, post.ref)
    cursor = followers.next
```

### Appendix B — Home merge

```text
def home(user, cursor, n):
  a = tl.scan(user, cursor, n)
  b = []
  for c in cache.following_celebs(user):
    b.extend(recent_index.scan(c, since=cursor_ts))
  posts = hydrate(unique(merge_sort(a,b)))
  return filter(posts)[:n]
```

### Appendix C — Idempotent TL write

```text
ZADD user:{id}:tl score=ts member=post_id
# Redis set semantics; dup member updates score only
```

### Appendix D — Notif aggregate

```text
key = (to_user, verb, object_id, window_bucket)
agg.count += 1
agg.sample.add(actor)  # cap sample size 3
upsert notif_inbox
```

### Appendix E — Backfill on follow

```text
if not celebrity(followee):
  for post in recent(followee, N=50):
    tl.add(follower, post.ref)
```

### Appendix F — Block filter

```text
if author in blocks[user] or user in blocks[author]:
  hide
```

### Appendix G — Sharded counter

```text
incr counter:{post_id}:{shard}
get: sum shards
```

### Appendix H — Progressive scale table

| Scale | Fanout | TL | Graph | Notif |
|-------|--------|----|-------|-------|
| Base | Push all | Redis | DB | Direct |
| 10× | Async workers | Redis cluster | Cache | Queue |
| 100× | Hybrid | Dual store | Graph svc | Aggregate |
| 1,000× | Active push | Regional | Cell graph | Priority inbox |

### Appendix I — API cursor

```text
cursor = base64({ts, post_id})
next page WHERE (ts, post_id) < cursor ORDER BY ts DESC, post_id DESC
```

### Appendix J — NFR card

```text
Publish ACK p99 < 300ms
Fanout lag normal p99 < 30s
Home read p99 < 200ms
No sync fanout before ACK
Celebrity hybrid enforced
```

### Appendix K — Hot post cache

```text
post:{id} → JSON in Redis TTL
CDN for media
negative cache for deletes
```

### Appendix L — Celebrity promotion job

```text
if follower_count > T or fanout_cost > budget:
  mark celebrity
  stop push
  optionally trim pushed history reliance
```

### Appendix M — Soft delete

```text
post.status = deleted
emit post.deleted
caches invalidate
TL entries filtered on hydrate
```

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Kafka fanout is enough” | Still need celebrity exception |
| “Cassandra timeline only” | Latency; often + Redis |
| “Ranked feed MVP” | Need candidate gen first; chrono honest MVP |
| “Strong consistency home” | Conflicts with async fanout scale |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Fanout | Distribute post refs to follower TLs |
| Hybrid | Push normal + pull celebrity |
| Hydrate | ID → post body |
| Reverse index | followee → followers |
| Tombstone | Deleted marker |

### Appendix P — Worked example

```text
2K posts/s × 200 followers = 400K TL writes/s
1% celebrity posts skipped → save huge tail
Feed 50K QPS × 20 posts = 1M hydrations/s → 95%+ post cache hit ⇒ 50K DB
Likes 20K/s → aggregates reduce notif writes ~10–100×
```

### Appendix Q — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Do all followers see post at ACK? | No |
| Does author? | Yes (user timeline) |
| Unfollow immediate? | Stop future; read filter |
| Like count exact? | No, eventual |

### Appendix R — 30m interview checklist

1. Clarify graph, feed, celebrity, notifs.  
2. Do fanout amplification math.  
3. Draw post → bus → fanout → TL; home merge.  
4. Deep dive hybrid + idempotency.  
5. Walk scale jumps.  
6. Deal-breakers.

### Appendix S — Ranker features (Phase 2)

| Feature | Signal |
|---------|--------|
| Affinity | Historical engage |
| Recency | Time decay |
| Velocity | Early likes |
| Mute/block | Hard filter |
| Diversity | Author spacing |

### Appendix T — Related systems (conceptual)

| System | Relation |
|--------|----------|
| Bigtable/Cassandra | Posts / TL durable |
| Memcache/Redis | Hot TL + posts |
| Pub/Sub | Fanout bus |
| TAO-like graph | Social graph |
| FCM | Notif push |

### Appendix U — Private account rules

```text
follow request pending → no fanout
accept → backfill + future push
reject → no edges
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Async fanout, Redis TL, caches |
| 100× | Hybrid celebrity, graph svc, notif agg |
| 1,000× | Cells, active push, ranker, edge |

---

*End of Social Network system design.*
