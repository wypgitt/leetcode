# System Design: Online Bulletin Board with Comments (Meta)

> **Focus areas:** Threads · Comments · Ranking · Moderation · Abuse · Read-heavy boards · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split post-write vs comment-write vs board-read planes, explicit hot-thread deal-breakers  
> **Interview theme:** Classic Meta/community L5+ — forums/bulletin boards (Groups-like / campus boards) with nested comments, freshness, and trust & safety

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

Goal: **bound the product**—an **online bulletin board** (forums / campus / neighborhood / Groups-style boards) where users create posts, comment in threads, browse ranked board feeds, and moderators keep communities healthy.

### 1.0 What this is / is not

| Dimension | **Bulletin board + comments (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Boards → posts → comment threads | Global FB news feed for all friends |
| Success | Fast board browse; usable threads; safe community | Perfect personalized ML feed MVP |
| Data plane | Post/comment writes + board indexes + mod | Live video / Reels encode |
| Query | Board feed, post detail, comment pages | Cross-network search of everything Phase 2 |
| Correctness | Durable posts/comments; eventual indexes OK | Linearizable global board order |

**Scope statement:** Design a multi-board bulletin system with posts, nested comments, ranking, subscriptions, and moderation—at Meta community scale.

**Differentiation vs live-comments-on-viral-posts:** Here the primary UX is **many boards + threaded discussions**, not Super-Bowl-scale single-post live stadium fanout (mention hooks if a thread goes viral).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a board? | Named community with members/ACL | Board entity + membership |
| F2 | Posts? | Title + body + media optional | Post entity |
| F3 | Comments? | Nested threads under posts | Comment tree / parent_id |
| F4 | Board feed sort? | Hot / New / Top (time window) | Rank indexes per board |
| F5 | Membership? | Public, restricted, private | AuthZ on read/write |
| F6 | Voting? | Upvote/downvote or like | Score affects Hot |
| F7 | Moderation? | Mods remove, ban, pin, lock | Mod actions + audit |
| F8 | Notifications? | Replies, mentions, mod actions | Async notif |
| F9 | Search? | Within board Phase 1.5 | Search index secondary |
| F10 | Edit/delete? | Soft-delete; edit history optional | Tombstones |
| F11 | Anonymous? | Optional campus Mode Phase 2 | Identity policy |
| F12 | Admin tools? | Board create, rules, flairs | Control plane |

**MVP functional scope:**

1. Users join/subscribe to boards (public/restricted).  
2. Create posts on boards they can write to.  
3. Comment with 1–2 level nesting (or N with collapse).  
4. Board feeds: **New** and **Hot** (Top for 24h/week).  
5. Upvote/like posts and comments; scores update Hot.  
6. Mod: remove, lock thread, pin, ban user from board.  
7. Basic spam rate limits + report queue.  
8. Notifications for replies to your post/comment.

**Out of MVP:**

- Full personalized cross-board home ML (hooks only)  
- Realtime collaborative editing  
- End-to-end encrypted anonymous boards  
- Viral live fanout as deep as Super Bowl (cross-ref live-comments design)  
- Marketplace listings as primary

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Feed latency | Snappy scroll | p99 < 100–200ms |
| N2 | Write durability | No lost post/comment after ACK | Multi-AZ durable |
| N3 | Hot score freshness | Minutes OK | Async ranker < 1–5 min |
| N4 | Availability | Community critical | 99.9% read |
| N5 | Mod action speed | Hide fast | Tombstone visible < few seconds |
| N6 | Privacy | Private boards airtight | AuthZ every read |
| N7 | Abuse resilience | Raid / spam | Rate limits + mod + integrity |
| N8 | Multi-region | Global boards | Home cell by board_id |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User opens board → Hot feed page 1 → opens post → reads comments Newest/Top → replies.  
2. User creates post → appears in New immediately; Hot after score.  
3. Mod removes spam comment → hidden for others quickly.  
4. User upvotes → score updates → Hot rank shifts async.  
5. Locked post → no new comments; existing readable.  
6. Private board → non-members 403 on feed and post.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate submit | Idempotency-Key |
| Brigading / raid | Rate limits; mod slow-mode; integrity |
| Hot thread comment storm | Shard comments; cache; optional live hooks |
| Deleted parent comment | Show tombstone; keep children policy explicit |
| Ban evasion | Integrity device/account linking |
| Pin + Hot conflict | Pins occupy reserved slots |
| Search lag | Eventual; feed not dependent |
| Cross-board repost spam | Link detection; limits |
| Mod abuse | Audit logs; admin oversight |
| Huge comment tree | Pagination + collapse; depth cap |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Boards | 1M | 10M | 100M | 1B-class |
| MAU | 50M | 500M | — | multi-B |
| Posts/day | 20M | 200M | 2B | 20B |
| Comments/day | 100M | 1B | 10B | 100B |
| Peak post writes/s | 5K | 50K | 500K | 5M |
| Peak comment writes/s | 20K | 200K | 2M | 20M |
| Board feed QPS | 100K | 1M | 10M | 100M |
| Avg posts / board / day | Zipf | Zipf | Zipf | Zipf |
| Mod actions/day | 1M | 10M | 100M | specialized |

**What each jump forces:**

- **10×:** Board-sharded stores; feed caches; async Hot ranker.  
- **100×:** Board home cells; comment buckets on hot posts; mod platform.  
- **1,000×:** Federated cells; materialized feed pages; integrity ML fleet.

### 1.5 Etc. (Constraints & Assumptions)

- Identity, media upload, notifications platforms exist.  
- Boards are the tenancy boundary for data locality.  
- Zipfian activity: few mega-boards dominate load.  
- Not redesigning all of Facebook Groups — focused bulletin+comments architecture.

**Scope statement to repeat back:**

> Design a multi-board bulletin system with ACL-aware feeds (New/Hot), durable posts and nested comments, voting, moderation, and progressive scale via board sharding and async ranking—without requiring a global personalized feed MVP.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Board feed reads** | Hot/New pages | ~100K QPS | Cache + index |
| **Post detail reads** | Post body | high | Cache |
| **Comment list reads** | Thread pages | high | Cache |
| **Post writes** | Create/edit | ~5K/s | Write API |
| **Comment writes** | Create/delete | ~20K/s | Write API |
| **Votes** | Upsert edges | ~50K/s | Counter/ranker |
| **Mod actions** | Remove/ban | lower | Control |
| **Ranker** | Recompute Hot | continuous | Async |

### 2.2 Zipf / mega-board

```text
Top 1% boards may take ~50%+ traffic
Design for mega-board = many mid-boards in capacity
Feed cache mandatory for hot boards
```

### 2.3 Storage

```text
100M comments/day × 400 B ≈ 40 TB/day raw upper
Retention + compression + cold tier essential at 100×
Posts fewer but larger (media pointers)
```

### 2.4 Hot score compute

```text
Don't recompute all posts every second
Event-driven: on vote/comment → update post score → adjust board ZSET
Decay via formula using ts (Wilson/Reddit-like / gravity)
```

### 2.5 Cache math

```text
Hot page 1 for 10K active boards × 20 KB = 200 MB — easy
Mega-board: 100K QPS feed → cache hit ratio must be >99%
```

### 2.6 AuthZ amplification

```text
Private board feed cannot be CDN-public
Per-request membership check with cached bloom/bitset per user
```

### 2.7 Comment write amplification (worked)

```text
Baseline peak comments 20K/s
Hot post takes 5% of peak → 1K comments/s on one post_id
Single partition writer saturates ~5–20K rows/s depending on store
⇒ bucket shard comments when post crosses threshold H
Fan-in read merges K buckets by (ts, id) — K=8–32 typical
```

### 2.8 Vote → Hot update cost

```text
50K votes/s → not 50K full feed rebuilds
Per vote: O(1) counter + O(log N) ZSET score update for that post
N trimmed to ~10K hot candidates/board → cheap
Recompute-all-posts-every-minute for 1M boards = impossible
```

### 2.9 Pagination payload budget

```text
Feed page: 20 posts × (2KB meta + author card) ≈ 40–80KB
Comment page: 20 top-level × (preview 3 replies) ≈ 50–100KB
p99 < 200ms ⇒ hydrate batch get, never N+1 author fetches
Cursor opaque ≤ 256B
```

### 2.10 Moderation purge fanout

```text
Remove post → delete from New ZSET + Hot ZSET + search + caches
Mega-board page-1 blob must version-bump within seconds
SLO: public hide p99 < 5s after mod ACK
```

### 2.11 Progressive capacity worksheet

| Scale | Feed origin QPS (after cache) | Comment buckets | Mod automation |
|-------|------------------------------|-----------------|----------------|
| Base | ~1–5K | rare | manual |
| 10× | ~10–20K | hot posts | report queues |
| 100× | materialized pages | default on viral | automod ML |
| 1,000× | edge authz cache | cell-local | integrity platform |

### 2.12 Anti-patterns (BOTE lens)

| Anti-pattern | Why it fails the math |
|--------------|----------------------|
| SQL `ORDER BY hot` each scroll | 100K QPS × sort = DB death |
| Unbounded comment tree download | Multi-MB payloads; mobile kill |
| Sync Hot recompute on vote | 50K/s × board scan |
| CDN private feeds | AuthZ leak × cache poison |
| One global posts table | Hot boards contend; no cell isolation |

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/boards` | Create board |
| `POST /v1/boards/{id}/join` | Membership |
| `GET /v1/boards/{id}/feed?sort=hot\|new\|top&cursor=` | Feed |
| `POST /v1/boards/{id}/posts` | Create post |
| `GET /v1/posts/{id}` | Post detail |
| `GET /v1/posts/{id}/comments?sort=&cursor=` | Comments |
| `POST /v1/posts/{id}/comments` | Comment |
| `POST /v1/posts/{id}/vote` | Vote |
| `POST /v1/mod/...` | Mod actions |
| `POST /v1/reports` | Report |

**Entities:**

```text
Board { board_id, name, visibility, rules, settings }
Membership { board_id, user_id, role: member|mod|admin }
Post { post_id, board_id, author_id, title, body_ref, score, ts, status, locked, pinned }
Comment { comment_id, post_id, parent_id?, author_id, text, score, ts, status }
Vote { target_type, target_id, user_id, value }
```

### 3.2 Feed indexes — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **ZSET per board sort key** | Fast page 1 | Memory; mega-board size | **MVP Hot/New** |
| SQL `ORDER BY` on posts table | Simple | Hot path load | Small |
| Materialized page blobs | Ultra read | Invalidate complexity | 100× mega |
| On-read rank all posts | Flexible | Dead at scale | Never |

**Chosen:**

- `feed:new:{board_id}` → ZSET score=ts  
- `feed:hot:{board_id}` → ZSET score=hot_score  
- Trim ZSET to last N (e.g. 5K–20K); older via DB/cold  
- Pins stored separately and merged at read

**Deal-breaker:** `SELECT * FROM posts WHERE board=? ORDER BY hot DESC` on every scroll at 100K QPS.

### 3.3 Hot ranking formula (MVP)

```text
hot = log10(max(z,1)) + ts_epoch / gravity

z = ups - downs   # or likes
OR Wilson lower bound for ranking quality
```

Document gravity (~45e3 for Reddit-like hours). Recompute on vote events.

### 3.4 Comment storage — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Adjacency list by parent | Natural tree | Deep walks | **MVP** |
| Nested set / materialized path | Fast subtree | Expensive moves | Rare |
| Flatten + client indent | Simple | Weak threads | Flat forums |
| Graph DB | Flexible | Ops | Overkill |

**Chosen:** comments table keyed by `post_id`, secondary `(parent_id, ts)`, Top index by score.

For mega-threads: bucket shard comments (see live-comments doc patterns).

### 3.5 Write paths

**Create post:**

```text
AuthZ member can_post
Idempotency
Insert post durable
Outbox → indexer adds to New ZSET; ranker seeds Hot
Invalidate feed cache version
Notify followers optional (board notifs settings)
```

**Create comment:**

```text
AuthZ; check not locked
Insert comment
Incr post.comment_count
Outbox → notif parent author
Optional bump Hot (comment as engagement)
```

### 3.6 Moderation

| Action | Effect |
|--------|--------|
| Remove content | status=removed; purge indexes |
| Lock post | reject new comments |
| Pin | reserved feed slots |
| Ban user | membership role=banned |
| Slow-mode | comment rate per board |

Mod actions dual-written to **audit log**.

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Tenancy | Shard by board_id | Locality | Global posts table hotspot |
| Feed | ZSET + cache | QPS | SQL sort every read |
| Hot | Async event ranker | Cost | Sync recompute world |
| Comments | Adjacency + pages | Simplicity | Unbounded tree payload |
| Private boards | AuthZ + no public CDN | Privacy | Cache private as public |
| Viral thread | Bucket/cache hooks | Skew | Ignore mega-thread |

### 3.8 Expanded HLD tradeoffs

| Tradeoff axis | Option A | Option B | Pick for MVP | Revisit when |
|---------------|----------|----------|--------------|--------------|
| Nesting depth | Flat only | Unlimited tree | Cap 3–5 + collapse | Product demands deep forks |
| Hot formula | Raw score | Wilson + gravity | Gravity + optional Wilson | Brigading worsens |
| Feed materialization | Live ZSET hydrate | Prebuilt page blobs | ZSET + cache; blobs for mega | Top boards >50K QPS |
| Comment store | Same DB as posts | Separate comment service | Separate at 10× | Write skew on hot posts |
| Mod sync vs async hide | Sync hide | Async eventual | Sync status + async index purge | Legal SLA tighter |
| Home feed | Board-only UX | Personalized home | Board-only | Product requires home |

**Interview line:** “Indexes are derived and rebuildable; AuthZ is on every read path; Zipf mega-boards get special treatment—not average-case design.”

### 3.9 Anti-patterns at HLD level

1. **Global chronological firehose as the board feed** — wrong product and wrong shard key.  
2. **Moderation as “delete row only”** — leaves caches/ZSETs/search serving ghosts.  
3. **Votes stored without unique (user,target)** — double-count and brigading amplify.  
4. **Pins encoded as infinite Hot score** — breaks ranking and trim logic; use reserved slots.  
5. **Search as source of truth for feeds** — feeds need deterministic cursors and rebuilds.

---

## 4. Architecture Diagram

```text
 Clients
    |
    v
 +------------------+
 | API Gateway      |
 | auth, ratelimit  |
 +--------+---------+
          |
          v
 +--------+---------+       +------------------+
 | Board Service    |------>| Membership/AuthZ |
 | Post Service     |       +------------------+
 | Comment Service  |
 +--------+---------+
          |
    +-----+-------------------+
    |                         |
    v                         v
 +-------------+        +------------------+
 | Primary DB  |        | Kafka outbox     |
 | board-shard |        | posts/comments/  |
 +-------------+        | votes/mod        |
                        +--------+---------+
                                 |
          +----------------------+----------------------+
          v                      v                      v
   +-------------+       +--------------+       +--------------+
   | Feed Indexer|       | Hot Ranker   |       | Notif/Search |
   | New ZSETs   |       | Hot ZSETs    |       |              |
   +------+------+       +------+-------+       +--------------+
          |                     |
          +----------+----------+
                     v
              +-------------+
              | Feed Cache  |
              | page blobs  |
              +-------------+

 Mod Platform --> mod actions --> DB + indexes + audit
 Integrity -----> spam signals --> limits / auto-hide
```

**Feed read path:**

```text
GET feed?sort=hot
  -> AuthZ membership
  -> cache page
  -> else ZSET LRANGE + hydrate posts
  -> merge pins
  -> filter removed
  -> cursor
```

**Vote path:**

```text
POST vote
  -> upsert vote edge
  -> update counters
  -> emit vote_changed
  -> ranker adjusts hot ZSET
```

**Mod remove:**

```text
status=removed
remove from ZSETs
cache bust
audit log
optional notif author
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Durable ACK** for posts/comments.  
2. **Idempotent creates**.  
3. **Removed/banned never served** to unauthorized after action (cache TTL bounded).  
4. **Private board content never in public caches**.  
5. **Mod audit append-only**.  
6. **Feed indexes are derived** — rebuildable from DB/log.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Indexer lag | New feed may miss post briefly; author RYW via write-through |
| Ranker lag | Hot slightly stale OK |
| Cache serves removed | Short TTL + version + explicit purge |
| Shard outage | Board unavailable; other boards OK |
| Mod tool down | Fail closed on dangerous automod optional |

#### 5.1.3 Author read-your-write

Write-through author into feed cache / return entity and client prepend.

### 5.2 Scalability

#### 5.2.1 Sharding

| Entity | Shard key |
|--------|-----------|
| Board meta | board_id |
| Posts | board_id |
| Feed indexes | board_id |
| Comments | post_id (+ bucket) |
| Membership | board_id |
| User profile posts | user_id secondary index |

#### 5.2.2 Mega-board strategies

```text
1) Feed page materialization (page_1 hot blob)
2) Segment ZSETs by time (hot:board:week1)
3) Read replicas for hydrate
4) Comment buckets on viral posts
5) Dedicated mega-board cells
```

#### 5.2.3 Cross-board home feed (Phase 1.5)

```text
candidates = ∪ top from subscribed boards (fanout read)
rank lightweight
OR push on post to per-user inbox (write fanout) for low-degree users
Hybrid: celebrity boards pull; small boards push
```

MVP can skip personalized home — board-centric UX.

#### 5.2.4 Progressive scale map

| Scale | Posts/Comments | Feeds | Mod |
|-------|----------------|-------|-----|
| Baseline | Board-sharded SQL/Cass | Redis ZSET | Manual tools |
| 10× | Outbox indexers | Page cache | Report queues |
| 100× | Hot post buckets | Materialized pages | Automod ML |
| 1,000× | Cell fabric | Edge membership-aware cache | Integrity platform |

### 5.3 Maintainability

#### 5.3.1 Service boundaries

| Service | Role |
|---------|------|
| Board | Meta + membership |
| Post | CRUD posts |
| Comment | CRUD comments |
| Feed | Indexes + read APIs |
| Vote | Edges + counters |
| Mod | Actions + audit |
| Integrity | Spam signals |

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| Feed p99 per board tier | SLO |
| Indexer lag | Freshness |
| Remove purge latency | Safety |
| Vote→hot update lag | Ranking |
| Report volume spikes | Raids |
| Cache hit ratio | Scale health |

#### 5.3.3 Rebuild feeds

```text
from posts where board_id=? and status=visible
recompute scores
rewrite ZSET in shadow
atomic swap
```

### 5.4 Comment threading UX

```text
Depth cap: 3–5
Collapse low-score branches
Pagination: top-level cursor; replies "load more"
Tombstone: "[removed]" keeps structure
```

### 5.5 AuthZ details

| Visibility | Read | Write |
|------------|------|-------|
| Public | world | members |
| Restricted | world or members | members approved |
| Private | members only | members |

Cached membership with version; mod ban increments version.

### 5.6 Abuse & raids

| Defense | Layer |
|---------|-------|
| Rate limits | API |
| Captcha / friction | Suspicious |
| Automod keyword/ML | Async/sync |
| Mod slow-mode | Board |
| Integrity cluster bans | Platform |

### 5.7 Search (Phase 1.5)

CDC posts/comments → search index; ACL filter at query; never bypass private.

### 5.8 Media

Bodies reference blob store; virus scan; thumbnails; don't inline huge blobs in feed hydrate.

### 5.9 Nested deep dive — Threads & comments

#### 5.9.1 Thread model

```text
Post (thread root)
  └─ Comment (parent_id = null)     ← top-level
       └─ Reply (parent_id = c1)   ← depth 1
            └─ Reply (parent_id = c2) ← depth 2 … capped
```

| Field | Role |
|-------|------|
| `comment_id` | Snowflake/ULID; time-sortable |
| `post_id` | Shard / partition key |
| `parent_id` | Tree edge; null = top-level |
| `depth` | Denormalized for cap enforcement |
| `score` | Votes for Top sort |
| `status` | visible / removed / pending |
| `created_at` | Newest sort |

#### 5.9.2 Write path (comment)

```text
1. AuthZ: member, not banned, post not locked, board not slow-mode violated
2. Validate depth = parent.depth + 1 ≤ MAX_DEPTH
3. Idempotency-Key → durable insert
4. Incr post.comment_count (async OK with reconcile)
5. Outbox: CommentCreated → notif, search, optional Hot bump
6. Return entity for author RYW (client prepend)
```

#### 5.9.3 Read path (threaded page)

```text
GET /posts/{id}/comments?sort=top|new&cursor=
  → load top-level page (keyset on score|ts + id)
  → for each top-level: fetch preview_replies = top N by score (N=2–3)
  → “load more replies” expands one subtree with its own cursor
  → filter status=removed → tombstone JSON (keep children_count)
```

**Deal-breaker:** returning the entire tree as one nested JSON for viral posts.

#### 5.9.4 Tombstones & deleted parents

| Policy | Behavior | When |
|--------|----------|------|
| Soft tombstone | Show “[removed]”; children remain | **MVP** |
| Collapse | Hide branch if root removed and no visible descendants | Optional UX |
| Hard delete | Physical remove | Legal only; rare |

#### 5.9.5 Locking & slow-mode

- **Lock post:** reject `POST comments` with 423; reads OK.  
- **Slow-mode:** token bucket `(board_id, user_id)` → 429 + `Retry-After`.  
- **Approval queue (restricted boards):** comment `status=pending` until mod ACK.

### 5.10 Nested deep dive — Pagination

#### 5.10.1 Cursor design

| Surface | Cursor payload | Seek |
|---------|----------------|------|
| Feed New | `(ts, post_id)` | `WHERE (ts,id) < cursor ORDER BY ts DESC` |
| Feed Hot | `(hot_score, post_id)` | ZSET reverse range by score |
| Comments New | `(ts, comment_id)` | keyset on top-level |
| Comments Top | `(score, comment_id)` | secondary score index |

Opaque cursors: `base64({sort, score, id, board_ver})`. Reject tampered cursors.

#### 5.10.2 Stability under concurrent writes

```text
Keyset pagination does NOT freeze a snapshot
New inserts may appear on refresh of page 1
Deep pages may skip/dup across races — acceptable for boards
For “stable export”: snapshot_ts in cursor (Phase 1.5)
```

#### 5.10.3 Hydration batching

```text
ids = page_ids(limit=20)
posts = batch_get(ids)           # 1 RPC
authors = batch_get(author_ids)  # 1 RPC
media = batch_get(media_refs)    # optional
assemble in request order; drop missing/removed
```

#### 5.10.4 Anti-patterns

| Anti-pattern | Failure |
|--------------|---------|
| `OFFSET 10000` | Deep page O(n) scan |
| Client sends page number only | Unstable under inserts |
| Embed full bodies in feed ZSET | Memory blowup; edit invalidation hell |

### 5.11 Nested deep dive — Moderation

#### 5.11.1 Action catalog

| Action | Durable effect | Derived effect |
|--------|----------------|----------------|
| Remove content | `status=removed` | Purge ZSET/search/cache |
| Restore | `status=visible` | Re-index |
| Lock / unlock | flag on post | Write path gate |
| Pin / unpin | pins table | Feed merge slots |
| Ban / unban | membership role | AuthZ version++ |
| Slow-mode | board setting | RL config |
| Approve queue | pending→visible | Index on approve |

#### 5.11.2 Purge pipeline (must be complete)

```text
mod.remove(content_id)
  -> txn: status=removed + audit_log append
  -> outbox ModRemoved
  -> workers:
       feed_index.remove
       search.delete
       cache.purge(keys...)
       notif optional
  -> measure: time_to_public_hide
```

**Deal-breaker:** DB status flip without index/cache purge.

#### 5.11.3 Report → automod loop

```text
Report(content, reason, reporter)
  -> aggregate distinct trusted reporters
  -> if threshold: auto-hide (soft) + mod queue
  -> ML score may accelerate hide on high-confidence spam
  -> appeal path restores with audit
```

#### 5.11.4 Mod abuse & audit

- Append-only audit: `{actor, action, target, ts, prev_status}`.  
- Anomaly: mass removes, targeting one user, off-hours spikes.  
- Admin can revoke mod role; rebuild feeds if mass false removes.

#### 5.11.5 Progressive moderation scale

| Scale | Stack |
|-------|-------|
| Base | Human mod tools + keyword filters |
| 10× | Report queues, slow-mode, rate limits |
| 100× | Automod ML, board-tier policies |
| 1,000× | Integrity platform, legal takedown SLA path |

### 5.12 Nested deep dive — Hot threads

#### 5.12.1 What “hot” means

```text
hot_score ≈ sign(s) * log10(max(|s|,1)) + (ts - epoch) / gravity
s = ups - downs   # or likes-only
gravity ≈ 45000   # Reddit-like hours scaling — tune per board type
```

Wilson lower bound optional for low-sample stabilization.

#### 5.12.2 Event-driven ranker

```text
on VoteChanged | CommentCreated | PostCreated:
  recompute hot_score(post)
  ZADD feed:hot:{board} score post_id
  trim ZSET to MAX_HOT (e.g. 10K)
  bump feed_cache version for board
```

Do **not** scan all posts on a timer.

#### 5.12.3 Mega-thread / viral post escalation

| Signal | Threshold example | Action |
|--------|-------------------|--------|
| Comment write QPS | > 200/s sustained | Enable comment buckets |
| Concurrent readers | > 50K | Materialize comment page-1 |
| Vote QPS | high | Counter shard / async |

Reuse patterns from live-comments design: coalesce, cache, hierarchical fanout if realtime UX required.

#### 5.12.4 Hot vs New vs Top

| Sort | Index | Freshness |
|------|-------|-----------|
| New | ZSET score=ts | Immediate on index |
| Hot | ZSET score=hot | Seconds–minutes lag OK |
| Top | ZSET or windowed table | Window (24h/week) |

Pins: merge `min(pins, max_pins)` ahead of ZSET page on page 1 only.

#### 5.12.5 Gaming Hot

| Attack | Mitigation |
|--------|------------|
| Early upvote brigade | Wilson / delay score application |
| Sockpuppets | Integrity trust weights on votes |
| Comment spam to bump | Cap comment contribution to Hot |
| Repost farms | Similarity / link reputation |

### 5.13 Nested deep dive — Progressive scale & deal-breakers

#### 5.13.1 Scale table (expanded)

| Scale | Writes | Feeds | Comments | Mod | Cells |
|-------|--------|-------|----------|-----|-------|
| Base | Board-sharded SQL | Redis ZSET | Adjacency | Manual | 1 region |
| 10× | Outbox indexers | Page cache | Preview replies | Reports | Multi-AZ |
| 100× | Hot buckets | Materialized mega pages | Bucket merge | Automod | Board home cells |
| 1,000× | Federated write | Edge membership cache | Live hooks | Integrity | Multi-region fabric |

#### 5.13.2 Deal-breakers (interview kill shots)

1. SQL `ORDER BY hot` on every feed request at board scale.  
2. Public CDN of private/restricted board pages.  
3. Unbounded comment tree in one response.  
4. Ignoring Zipf — designing only for average board.  
5. Mod remove without cache/index/search purge.  
6. Sync world recompute of Hot on each vote.

#### 5.13.3 Failure drills

| Drill | Expect |
|-------|--------|
| Ranker down | New works; Hot stale but serving |
| Indexer lag | Author RYW; others within SLO |
| Comment bucket skew | Rebalance buckets; read merge OK |
| Raid | Slow-mode + RL + mod + integrity |
| AuthZ cache stale ban | Short TTL; version bump on ban |

---

## 6. Wrap-Up

### 6.1 Design summary

A **bulletin board with comments**:

1. **Board-centric sharding** and ACL.  
2. Durable posts/comments with outbox to **New/Hot indexes**.  
3. Async **Hot ranker** on votes/engagement.  
4. Nested comments with pagination/collapse; mega-thread buckets.  
5. **Moderation + audit** with fast purge.  
6. Progressive mega-board materialization and cells.

### 6.2 Key tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Fresh Hot vs cost | Async ranker |
| Tree completeness vs payload | Paginate/collapse |
| Personalized home vs MVP | Board feeds first |
| CDN vs privacy | No public CDN for private |

### 6.3 Deal-breakers

- SQL `ORDER BY hot` every request at scale.  
- Public caching of private board pages.  
- Unbounded comment tree download.  
- Ignoring Zipf mega-boards.  
- Mod remove without cache/index purge.

### 6.4 30-minute checklist

1. Clarify boards ACL, sorts, nesting, voting, mod.  
2. Estimate feed QPS + Zipf.  
3. Draw write → DB → outbox → ZSET → cache.  
4. Hot formula + ranker.  
5. Comments + mod purge.  
6. Scale jumps.  
7. Deal-breakers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & requirements

**Q1: How is this different from news feed?**  
A: Board-scoped communities and threads; not friend-graph ranking as MVP core.

**Q2: Hot vs Top vs New?**  
A: New=time; Top=score in window; Hot=score+gravity/time.

**Q3: Why limit nesting?**  
A: UX and abuse; deep trees hard on mobile.

**Q4: Anonymous posting?**  
A: Hard for abuse/legal; if needed, server-held unlinkable tokens with care — Phase 2.

**Q5: Board vs chat Group?**  
A: Async threaded content vs realtime messaging — different systems.

### 7.2 Feeds & ranking

**Q6: Why ZSETs?**  
A: O(log N) update and fast range for page 1; trim old.

**Q7: Hot gravity meaning?**  
A: Time decay so old content falls; tune per community.

**Q8: Wilson vs raw score?**  
A: Wilson stabilizes low-sample posts; reduces early gaming somewhat.

**Q9: How pins work?**  
A: Separate list merged before ZSET results; not infinite pins.

**Q10: Materialized pages?**  
A: Precompute JSON for mega-board page1; refresh on version.

**Q11: Indexer lag UX?**  
A: Author sees own post; others within lag SLO; show “posting…” state.

**Q12: Cross-board home fanout?**  
A: Pull top of subscriptions or hybrid push/pull — Phase 1.5.

### 7.3 Comments

**Q13: Parent deleted?**  
A: Tombstone; children remain or collapse — pick and stick.

**Q14: Sort comments by Top on large threads?**  
A: Maintain score index; don’t sort all in memory each read.

**Q15: When to apply live-comments design?**  
A: When concurrent viewers/writes on one post explode — reuse fanout/buckets.

**Q16: Comment search?**  
A: Secondary; ACL mandatory.

**Q17: Edit wars?**  
A: Edit windows; mod lock; optional history.

**Q18: Quote replies?**  
A: Store quote_ref; still parent_id for tree.

### 7.4 Votes & abuse

**Q19: Double vote?**  
A: Upsert unique (user,target); toggle.

**Q20: Vote brigading?**  
A: Rate limits; anomaly; delay score application; integrity.

**Q21: Sockpuppets?**  
A: Device/graph signals; restrict new accounts’ vote weight.

**Q22: Downvotes?**  
A: Product choice; increases abuse complexity; likes-only simpler MVP.

**Q23: Raid on board?**  
A: Slow-mode, join queue, mod tools, temporary post approval.

**Q24: Spam links?**  
A: Classifier; domain reputation; first-post moderation.

### 7.5 AuthZ & privacy

**Q25: Membership check performance?**  
A: Cache `user→boards` and `board→banned`; version on change.

**Q26: Why not CDN entire feed?**  
A: Private/restricted; personalized blocks; use private edge cache with auth.

**Q27: Banned user with old token?**  
A: Short token TTL; membership version in authz cache.

**Q28: Cross-board content share?**  
A: Copy or pointer with ACL recheck on destination.

**Q29: GDPR delete?**  
A: Tombstone user content; rebuild indexes; legal process.

**Q30: Mod visibility of removed?**  
A: Yes with audit; public no.

### 7.6 Scale & storage

**Q31: Shard by user instead of board?**  
A: Feed-by-board becomes scatter-gather — worse for this product.

**Q32: Cassandra vs MySQL?**  
A: Both OK with board partition; Cassandra good for wide time indexes; SQL good for mod tooling — justify one.

**Q33: How big can a ZSET be?**  
A: Trim; segmented by time; overflow to DB.

**Q34: Media storage cost?**  
A: Dominant vs text; lifecycle policies.

**Q35: Multi-region board?**  
A: Home region by board; secondary read replicas; writes to home.

### 7.7 Moderation systems

**Q36: Automod before or after publish?**  
A: Sync cheap filters; async ML hide; high-risk boards require approval queue.

**Q37: Report thresholds?**  
A: Auto-hide after N distinct reporters with trust weights.

**Q38: Mod abuse detection?**  
A: Audit anomalies; community strikes; admin review.

**Q39: Legal takedown SLA?**  
A: Control plane force-remove; global purge path.

**Q40: Slow-mode implementation?**  
A: Redis token bucket per (board,user).

### 7.8 Interview craft

**Q41: How to open?**  
A: Boards ACL, feed sorts, comment depth, voting, mod — then Zipf mega-boards.

**Q42: Numbers that matter?**  
A: Feed QPS, writes/s, comments/s, top-board share, cache hit, indexer lag.

**Q43: L5+ impress?**  
A: Derived rebuildable indexes, private cache rules, mega-board materialization, tombstones, progressive cells.

**Q44: Common mistake?**  
A: Designing only global newsfeed; or forgetting AuthZ on caches.

**Q45: Relation to live popular comments?**  
A: Complementary — board system owns threads; live fanout attaches when a post goes mega-viral.

---

### Appendix A — Hot score

```text
def hot(ups, downs, ts):
  s = ups - downs
  order = log10(max(abs(s),1))
  sign = 1 if s>0 else -1 if s<0 else 0
  return sign*order + (ts - epoch)/gravity
```

### Appendix B — Feed read

```text
def feed(board, sort, cursor, user):
  assert can_read(user, board)
  pins = pins_of(board) if first_page else []
  ids = zrange(feed_key(board,sort), cursor, limit)
  posts = hydrate(ids)
  return merge(pins, posts)
```

### Appendix C — Outbox

```text
txn:
  insert post
  insert outbox(PostCreated)
relay -> indexer/ranker/search/notif
```

### Appendix D — Membership cache

```text
key user:{id}:boards -> hash board_id => role, ver
on ban: ver++; delete entry
```

### Appendix E — Comment page

```text
top_level = query(post_id, parent is null, sort, cursor)
for each: preview_replies = top N by score
```

### Appendix F — Mod remove

```text
def remove(content):
  content.status = removed
  index.remove(content)
  cache.purge(content)
  audit.append(...)
```

### Appendix G — NFR card

```text
Feed p99 < 200ms
Durable writes
Hot lag < 5 min
Remove purge fast
Private never public-cached
ZSETS trimmed
```

### Appendix H — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Outbox, feed cache |
| 100× | Materialized mega pages, automod |
| 1,000× | Cells, edge authz cache |

### Appendix I — Vote upsert

```text
INSERT vote ... ON CONFLICT UPDATE
delta = new - old
counter += delta
emit VoteChanged(delta)
```

### Appendix J — Cursor

```text
New: (ts, post_id)
Hot: (hot_score, post_id)
```

### Appendix K — Board settings

```text
posting_restricted, slow_mode_sec,
require_approval, profanity_filter,
max_pins
```

### Appendix L — Worked example

```text
100K feed QPS, 50% to top 1K boards
per hot board ~50 QPS avg, peaks higher
cache TTL 2s => origin refresh 0.5/s/board => 500/s origin for 1K boards — OK
```

### Appendix M — Tombstone JSON

```json
{"id":"c1","status":"removed","children_count":3}
```

### Appendix N — Failure drill

| Drill | Expect |
|-------|--------|
| Ranker down | New works; Hot stale |
| Cache poison removed | Purge + short TTL |
| Board shard down | That board error |
| Raid | Slow-mode + limits |

### Appendix O — Search ACL

```text
query candidates
filter can_read(user, board_id)
never show removed
```

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Board | Community container |
| Hot | Gravity-ranked feed |
| ZSET | Sorted set index |
| Tombstone | Removed placeholder |
| Mega-board | Zipf heavy community |
| Outbox | Reliable event publish |

### Appendix Q — Comparison: push vs pull home

| | Push inbox | Pull subscriptions |
|--|------------|--------------------|
| Low follow | Good | OK |
| Mega board | Blowup | Better |
| Hybrid | **Best** | **Best** |

### Appendix R — Roles

| Role | Powers |
|------|--------|
| member | post/comment |
| mod | remove/lock/ban |
| admin | settings, mod grants |
| banned | no write; maybe no read |

### Appendix S — API errors

| Code | Meaning |
|------|---------|
| 403 | ACL |
| 404 | missing / hidden as missing |
| 409 | idempotency |
| 423 | locked |
| 429 | rate / slow-mode |

### Appendix T — Hydration

```text
feed returns ids → batch get posts → batch authors → filter
avoid N+1
```

### Appendix U — Integrity signals

| Signal | Use |
|--------|-----|
| New account | friction |
| Duplicate text | spam |
| Vote velocity | brigade |
| Join→spam time | raid |

### Appendix V — 30m checklist compact

```text
ACL+sorts → Zipf math → DB+outbox+ZSET+cache
→ Hot formula → Comments/mod → Scale → Deal-breakers
```

### Appendix W — Entity relationship

```text
Board 1---* Membership *---1 User
Board 1---* Post 1---* Comment
Post 1---* Vote
Comment 1---* Vote
Post 1---* ModAction
```

### Appendix X — Rebuild job

```text
for board in boards:
  shadow = compute_zsets(board)
  swap(feed_keys(board), shadow)
```

### Appendix Y — Why board_id shard

```text
Most queries are board-scoped
Joins stay local
Blast radius = board cell
Mega-boards get dedicated treatment
```

### Appendix Z — Related Meta products (conceptual)

| Product | Relation |
|---------|----------|
| Groups | Closest product analogue |
| Pages | Broadcast-ish variant |
| Integrity | Abuse |
| Notifications | Replies |
| Live comments design | Viral thread escalation |

---

*End of Online Bulletin Board with Comments system design.*
