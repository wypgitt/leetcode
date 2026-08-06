# System Design: Live Comments on Popular Posts (Meta)

> **Focus areas:** Hot-post fan-out · Real-time comment delivery · Read/write amplification · Ranking & moderation · Cell isolation · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split comment-write vs live-fanout vs feed-read planes, explicit hot-key deal-breakers  
> **Interview theme:** Classic Meta L5+ social realtime — celebrity posts, live comment streams, cache coherency, and blast-radius control

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

Goal: **bound the product**—a system that supports **live comments on posts**, with special attention to **popular / viral posts** where write QPS, fan-out, and read concurrency explode.

### 1.0 What this is / is not

| Dimension | **Live comments on popular posts (this doc)** | Not this |
|-----------|-----------------------------------------------|----------|
| Primary job | Create, deliver, rank comments in near-real-time | Full Facebook/Instagram feed ranking |
| Success | Fresh comments appear quickly; hot posts stay up | Perfect global comment order across all viewers |
| Data plane | Comment writes + live push/pull + moderation | Story/Reel encoding pipeline |
| Query | List comments (ranked / chronological); live delta | Arbitrary OLAP over all comments |
| Correctness | Durable after ACK; eventual consistent live views OK | Linearizable global comment stream for every viewer |

**Scope statement:** Design live commenting for social posts, especially celebrity/viral posts, with durable storage, realtime delivery, ranking, moderation hooks, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is a comment? | Text (+ optional sticker/GIF/mention); nested replies Phase 1/1.5 | Comment entity + parent_id optional |
| F2 | Live means what? | New comments appear in seconds without full refresh | Pub/sub or long-poll/SSE/WebSocket per post |
| F3 | Ordering? | Chronological default; “Top” ranked for popular | Dual indexes: time + score |
| F4 | Nested replies? | 1-level or 2-level threads MVP | Parent→children store; collapse UX |
| F5 | Likes on comments? | Yes — like count affects Top ranking | Counter service / sharded counters |
| F6 | Moderation? | Spam, hate, NSFW filters; report/hide | Async classifiers + hide tombstones |
| F7 | Who can comment? | Friends / followers / public by post ACL | AuthZ check against post privacy |
| F8 | Edit / delete? | Soft-delete; edit within window | Version + tombstone; notify live viewers |
| F9 | Mentions / notifications? | Notify mentioned users & post author | Notification fanout bus (async) |
| F10 | Pagination? | Cursor-based infinite scroll | Opaque cursors on (score,ts,id) |
| F11 | Reactions emoji? | Optional Phase 1.5 | Separate reaction counters |
| F12 | Admin / celebrity tools? | Pin comment; slow-mode; close comments | Control plane flags on post |

**MVP functional scope:**

1. Authenticated user posts a comment on a visible post.  
2. Comment is durable before client ACK.  
3. Other viewers of that post see new comments within a few seconds (live).  
4. List comments chronological + Top for popular posts.  
5. Soft-delete / hide; basic spam rate limits.  
6. Like a comment; Top ranking uses likes + recency.  
7. Pin / close comments / slow-mode for post owner or admin.  
8. Nested replies: at least 1 level.

**Out of MVP:**

- Full ML comment ranking personalization per viewer  
- Cross-post comment search  
- Voice/video comments  
- Perfect identical order for all global viewers at the same millisecond  
- Real-time translation of every comment

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Write durability | No silent loss after ACK | Multi-AZ durable store; ack after quorum/log |
| N2 | Live freshness | Feels live | p99 end-to-end < 2–5s for visible comment |
| N3 | List latency | Smooth scroll | p99 < 100–200ms cached hot posts |
| N4 | Hot-post write ingest | Celebrity posts survive | 50K–100K+ comments/min on peak post (baseline→scale) |
| N5 | Availability | Social critical path | 99.9%+ read; degrade live to polling |
| N6 | Consistency | Author read-your-write | Session sticky / primary read for author |
| N7 | Moderation latency | Harmful content hidden quickly | Async < few seconds; sync block for egregious |
| N8 | Multi-region | Global users | Home cell by post_id or geo; replicate hot read |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User opens viral post → loads Top comments page 1 → WebSocket subscribe → sees new comments stream in.  
2. User posts comment → ACK → appears in own view immediately → others receive live event.  
3. User likes a comment → like count bumps → Top rank may change on next ranked page fetch.  
4. Post owner pins a comment → pinned slot appears above list for all viewers.  
5. User replies to a comment → nested under parent; live event includes parent_id.  
6. Slow-mode enabled → comment API returns 429 with retry-after if user too frequent.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit comment | Idempotency-Key → one comment |
| Celebrity post 100K concurrent viewers | Shard live channels; coalesced fanout; do not 1:1 socket per write globally |
| Comment storm spam | Per-user / per-post rate limits; shadowban; classifier |
| Delete while others viewing | Live `comment_deleted` event; tombstone on read |
| Hot key on single DB partition | Shard comments by post_id + bucket; write buffers |
| Live gateway dies | Client reconnect + catch-up via since_cursor |
| Moderation false positive | Appeal / undo hide; audit log |
| Closed comments | API rejects new writes; reads still work |
| Very deep reply spam | Cap depth; collapse; rate limit replies |
| Author blocked viewer | Filter comments from blocked users on read |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 100M | 1B | — | treat as multi-B class |
| Posts with comments/day | 200M | 2B | 20B | retention-capped |
| Comments created/day | 1B | 10B | 100B | 1T class |
| Peak comments/s global | 50K | 500K | 5M | 50M |
| Peak comments/s on **one** hot post | 5K | 50K | 200K+ | cell-specialized |
| Concurrent viewers on one hot post | 500K | 5M | 50M | 100M+ Super Bowl class |
| Live events fanout/s (effective) | coalesced | heavy coalesce | hierarchical | edge fanout tree |
| Comment list QPS | 200K | 2M | 20M | edge+cache |
| Avg comment size | ~200 B | 200 B | 200–400 B | 200–400 B |
| Stored comments (retained) | ~5T rows order | cells | multi-cell | cold tier |

**What each jump forces:**

- **10×:** Per-post write sharding; Redis comment list cache; dedicated live fanout; rate limits.  
- **100×:** Hot-post cells; hierarchical pub/sub; ranked index async; moderation fleet.  
- **1,000×:** Edge subscription trees; comment sampling/aggregation UI for ultra-hot; regional home cells.

### 1.5 Etc. (Constraints & Assumptions)

- Posts already exist in a Post Service; we own Comment + Live delivery.  
- AuthN/AuthZ via existing Meta identity; we enforce post ACL on write/read.  
- Clients: mobile + web; prefer WebSocket/SSE with polling fallback.  
- “Popular” means high concurrent viewers and/or high comment velocity — not only celebrity accounts.  
- Exact global total order of comments across continents is **not** required.

**Scope statement to repeat back:**

> Design live comments for social posts with durable writes, chronological and Top rankings, moderation, and realtime delivery—especially under viral hot-post load—scaling through 10× / 100× / 1,000× via comment sharding, coalesced fanout, and hot-post cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Comment writes** | Create/delete/like | ~50K/s | ~500K/s | Write API + log |
| **Hot-post writes** | Single post spike | ~5K/s | ~50K/s | Sharded write buffers |
| **List reads** | Paginated comment fetch | ~200K/s | ~2M/s | Cache + read replicas |
| **Live subscribe** | Concurrent WS | ~10M sockets order | ~100M | Live gateway fleet |
| **Live fanout msgs** | New comment → viewers | coalesced ≪ raw×viewers | hierarchical | Pub/sub tree |
| **Moderation** | Classify comment | ~50K/s | ~500K/s | Async workers |
| **Notification** | Mention/author notify | subset of writes | ×10 | Notif bus |

**Anti-pattern:** one “QPS” mixing comment INSERT, WebSocket frames, and feed ranking.

### 2.2 Hot-post amplification math

```text
Naive: 5K comments/s × 500K viewers = 2.5B messages/s  → DEAL-BREAKER

Must coalesce:
  - Batch comments every 200–500ms per post into one payload
  - Hierarchical fanout: origin → regional hubs → edge gateways → local sockets
  - Optional: sample/aggregate (“2.4K new comments”) for ultra-hot UI mode

With 500ms batching: 5K/s → ~10 batches/s × payload of ~250 comments
Fanout cost becomes O(viewers × batches/s) still large, but payload efficiency ↑
Further: gateway-local multicast; don't cross-ocean each comment individually
```

### 2.3 Storage

```text
1B comments/day × 500 B expanded (text+meta) ≈ 500 TB/day raw (upper)
With compression + cold tiering + retention (e.g. 2–5 years hot metadata):
  Plan: hot SSD/NVMe recent; blob for long text; TTL/archive policy

Index amplification:
  - Primary by (post_id, comment_id)
  - Time index (post_id, ts, id)
  - Rank index (post_id, score, id) async
  - Reply index (parent_id, ts, id)
```

### 2.4 Cache

```text
Hot post Top page (first 20–50 comments) cached in Redis:
  Key: comments:top:{post_id}:v{n}
  TTL short (1–5s) OR versioned invalidate on write batch

500K viewers polling every 10s without live:
  50K QPS just for one post — cache mandatory
With live: initial load cached; deltas via push
```

### 2.5 Write path latency budget

```text
AuthZ + rate limit     5–15ms
Append to WAL/Kafka    5–20ms
Primary durable ack    10–40ms
Return to client       total p50 < 100ms, p99 < 300ms
Live fanout            async after durable (don't block ACK on 500K viewers)
```

### 2.6 Ranking cost

```text
Score = likes * w1 + replies * w2 + recency_decay(ts)
Recompute on like events for hot posts via async ranker
Don't re-sort full comment set on every like at 100× — maintain bounded top heap + lazy
```

### 2.7 Hot-post write shard math

```text
Single post 5K writes/s into one DB partition → hotspot
Bucket split N=16: ~312 writes/s/bucket
Read merge: fan-in N buckets for newest page — OK if each returns ≤50 and merge heap
At 50K writes/s (10× hot): N=64–256 buckets or dedicated hot cell
Rule of thumb: target <1K durable writes/s per physical partition
```

### 2.8 WebSocket room economics

```text
500K viewers on one post
Gateways: 10K conns/instance → 50 gateway processes minimum just for sockets
Registry: post_id → {gateway_ids} or hierarchical relay membership
Heartbeat 30s: 500K/30 ≈ 17K msgs/s control plane — budget separately from comment events
```

### 2.9 Sampling threshold arithmetic

```text
UI mode switch when comment_rate > R or viewers > V
Example: R=1K/s or V=200K → enter “live summary” mode
Emit: {type: batch, count, samples: [3..10 comments], top_authors}
Client still can GET list for full history; live stream is sampled
Reduces fanout bytes by 10–100× vs full text every comment
```

### 2.10 Persistence vs live lag budget

```text
Durable ACK p99: 300ms
Live lag SLO: event visible p99 < 1–2s for normal posts
Hot posts: coalesce window 200–500ms dominates lag (acceptable)
Never block durable ACK on fanout completion
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/posts/{post_id}/comments` | Create comment; Idempotency-Key; returns comment |
| `GET /v1/posts/{post_id}/comments?sort=new\|top&cursor=` | Paginated list |
| `GET /v1/comments/{id}/replies?cursor=` | Nested replies |
| `DELETE /v1/comments/{id}` | Soft-delete |
| `POST /v1/comments/{id}/like` | Like / unlike |
| `POST /v1/posts/{post_id}/comments:pin` | Pin (owner/admin) |
| `POST /v1/posts/{post_id}/comments:settings` | close / slow_mode |
| `WS /v1/posts/{post_id}/live` | Subscribe to live comment events |
| `GET /v1/posts/{post_id}/comments:delta?since=` | Polling fallback |

**Comment schema:**

```text
Comment {
  comment_id,       // snowflake / ULID
  post_id,
  author_id,
  parent_id?,       // null = top-level
  text,
  created_at,
  edited_at?,
  status,           // visible|hidden|deleted
  like_count,
  reply_count,
  score,            // denormalized for Top
  mod_labels?,
  idempotency_key
}
```

### 3.2 Data model

| Entity | Key | Store |
|--------|-----|-------|
| Comment row | `comment_id` | Cassandra / MySQL-sharded / TAO-like |
| Time index | `(post_id, ts, comment_id)` | Wide-column / Redis ZSET hot |
| Rank index | `(post_id, score, comment_id)` | Async maintained ZSET / table |
| Reply index | `(parent_id, ts, comment_id)` | Same |
| Like edge | `(comment_id, user_id)` | KV / graph |
| Post comment settings | `post_id` | Config KV |
| Live cursor watermark | `(post_id, shard)` | Redis |

### 3.3 Write path

```text
Client POST comment
  -> API gateway (auth)
  -> Comment Service:
       check post ACL, closed?, slow_mode, rate limit
       allocate comment_id
       durable append (DB and/or Kafka comments.created)
       ACK client
  -> async:
       moderation classify
       update caches / indexes
       live fanout publish
       notifications
```

### 3.4 Live delivery — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Short polling** | Simple | Load; lag | Fallback only |
| **Long polling** | Simpler than WS | Connection churn | Mobile flaky nets OK |
| **SSE** | One-way easy | Unidirectional | Comment stream OK |
| **WebSocket** | Bidirectional; efficient | Stateful gateways | **MVP choice for live** |
| **MQTT / specialized push** | Scale fanout | Ops complexity | 100×+ edge tree |

**Chosen MVP:** WebSocket subscribe per `post_id` with **coalesced batches** + delta polling fallback.

**Deal-breaker:** publishing one Redis Pub/Sub message per comment to millions of individual channel subscribers without hierarchy/coalescing.

### 3.5 Hot-post write sharding — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Single partition per post | Simple order | Hot key melt | Cold posts only |
| **Shard by hash(comment_id) within post** | Write scale | Merge on read | **Hot posts** |
| Kafka partition per post | Ordered log | Partition hotspot | Need many partitions / buckets |
| Write buffer + microbatch flush | Smooth spikes | Slight visibility lag | Celebrity spikes |

**Chosen:**

- Default: comments keyed by `post_id` (single logical stream).  
- Hot detection: if write QPS > threshold, split into `N` buckets `post_id#bucket`.  
- Read merges buckets by `(ts, comment_id)` with bounded merge.  
- Live events include bucket watermark vector or single merged sequencer.

### 3.6 Ranking — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Pure chronological | Simple | Low quality on viral | Always offer “Newest” |
| Likes only | Easy | Gaming; old sticky | Weak alone |
| **Wilson / Bayesian + recency** | Stable Top | Compute | **MVP Top** |
| Personalized ML | Best UX | Cost/complexity | Phase 2 |
| Sampled Top for ultra-hot | Feasible | Incomplete | 1,000× Super Bowl |

**MVP Top score:**

```text
score = bayesian_like_ratio * W_like
      + log(1+replies) * W_reply
      + recency_boost(created_at)
pinned comments forced above
hidden/deleted excluded
```

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Durable write vs live | Durable first, fanout async | No lost comments | ACK only after 500K WS sends |
| Fanout | Hierarchical + coalesced | Amplification | Naive per-viewer emit per write |
| Hot writes | Bucket shard + merge | Hot key | One MySQL row lock per celebrity post |
| Reads | Cache first page + cursors | QPS | Full table scan per scroll |
| Moderation | Sync blocklist + async ML | Safety/latency | Sync heavy ML on every write at peak |
| Order | Per-post logical time + id | UX | Global Lamport across all posts |

---

## 4. Architecture Diagram

```text
  Mobile/Web Clients
        |  HTTPS + WSS
        v
 +------------------+        +------------------+
 | API Gateway      |------->| Live Gateway     |
 | auth, ratelimit  |        | WS/SSE sessions  |
 +--------+---------+        +--------+---------+
          |                           ^
          v                           | subscribed events
 +--------+---------+                 |
 | Comment Service  |                 |
 | create/list/like |                 |
 +--------+---------+                 |
          |                           |
     +----+----+                      |
     |         |                      |
     v         v                      |
 +-------+  +-----------+    +--------+---------+
 |Comment|  | Kafka     |--->| Fanout Workers   |
 | Store |  | comments.*|    | coalesce+publish |
 |sharded|  +-----------+    +--------+---------+
 +-------+       |                    |
                 |                    v
                 |           +------------------+
                 |           | Pub/Sub Tree     |
                 |           | region → edge    |
                 |           +------------------+
                 v
          +--------------+     +----------------+
          | Ranker/Cache |     | Moderation     |
          | Redis ZSET   |     | classifiers    |
          +--------------+     +----------------+
                 |
                 v
          +--------------+
          | Notif Service|
          +--------------+
```

**Create comment path:**

```text
POST /comments
  -> AuthZ(post)
  -> rate limit (user, post)
  -> append Comment Store (quorum)
  -> produce Kafka(comment_created)
  -> return 201 Comment
  -> (async) mod, cache, fanout, notif
```

**Live path:**

```text
WS subscribe(post_id, last_event_id)
  -> Live Gateway registers interest
  -> Fanout delivers coalesced CommentBatch events
  -> on reconnect: GET delta?since=cursor then resume
```

**List Top path:**

```text
GET comments?sort=top
  -> Redis cache page1
  -> else Rank index / merge buckets
  -> filter hidden + block graph
  -> return cursor
```

**Hot-post mode:**

```text
Hot detector (writes/s, viewers)
  -> enable N write buckets
  -> enable coalesced live (200–500ms)
  -> optional UI aggregate mode
  -> pin Comment Service pods to Hot Cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Durable before ACK** — client 201 means comment will not silently vanish.  
2. **Idempotent create** — same Idempotency-Key returns same `comment_id`.  
3. **Tombstones win** — deleted/hidden never reappear as visible after mod.  
4. **Live is best-effort laggy** — missing an event is healed by delta catch-up.  
5. **Author read-your-write** — author list/live includes own comment immediately (session/cache write-through).

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Comment Store quorum loss | Multi-AZ; reject writes if cannot durable |
| Kafka down | Buffer in local spool short time OR fail write if bus required for durability design; prefer store-first |
| Live gateway mass disconnect | Clients poll delta; autoscaling |
| Ranker lag | Newest still works; Top slightly stale OK |
| Moderation pipeline down | Fail-open for low-risk + fail-closed for high-risk keywords; alert |
| Hot cell overload | Shed non-hot traffic; admission control; slow-mode auto |

#### 5.1.3 Exactly-once live?

Live delivery is **at-least-once**. Clients dedupe by `comment_id` / `event_id`.  
Catch-up cursor is monotonic per post (or per bucket vector).

**Deal-breaker:** claiming exactly-once WebSocket delivery without client idempotency.

#### 5.1.4 Delete / edit consistency

```text
delete:
  mark status=deleted in store
  emit comment_deleted
  remove from Redis ZSETs
  live clients remove bubble

edit:
  version++
  emit comment_updated
  cache invalidate
```

### 5.2 Scalability

#### 5.2.1 Partitioning

| Entity | Partition key | Notes |
|--------|---------------|-------|
| Comment | `post_id` (+ bucket if hot) | Colocate comments of a post |
| Likes | `comment_id` | High fan-in likes shard further |
| Live interest | `post_id` | Gateway owns slices of posts |
| User recent comments | `user_id` | Profile “comments” tab secondary |

#### 5.2.2 Hot-post cell

When a post crosses thresholds (viewers, write QPS):

1. Migrate / pin traffic to **Hot Post Cell**.  
2. Pre-warm caches.  
3. Increase bucket count `N`.  
4. Enable stronger rate limits / slow-mode suggestions.  
5. Switch live to hierarchical fanout + larger coalesce windows.

#### 5.2.3 Fanout tree

```text
Origin Fanout (per post shard)
  -> Regional Relays (N regions)
      -> Edge Live Gateways (M pods)
          -> Client sockets (local)

Subscription registry:
  post_id -> set(gateway_ids)  (not set of all user_ids at origin)
```

At 100×, origin only knows gateways interested, not 50M user ids.

#### 5.2.4 Cache strategy

| Cache | Contents | TTL / invalidation |
|-------|----------|--------------------|
| Page-1 Newest | last 50 comments JSON | 1–2s or version bump |
| Page-1 Top | top 50 | 2–5s; async refresh |
| Comment entity | by id | longer; invalidate on edit |
| Like count | cached counter | write-behind / CRDT-ish |
| ACL / settings | post flags | strong-ish on change |

#### 5.2.5 Progressive scale map

| Scale | Writes | Live | Reads |
|-------|--------|------|-------|
| Baseline | Sharded store by post | Redis pub/sub + WS | Redis page cache |
| 10× | Hot buckets | Coalesce + multi gateway | CDN for static assets only; API cache |
| 100× | Hot cells | Regional relays | Rank indexes dedicated |
| 1,000× | Ultra-hot sampling UI | Edge fanout fabric | Aggressive aggregation |

### 5.3 Maintainability

#### 5.3.1 Service boundaries

| Service | Responsibility |
|---------|----------------|
| Comment Service | CRUD, ACL, rate limit |
| Live Gateway | Sessions, catch-up |
| Fanout Worker | Coalesce, publish tree |
| Ranker | Top score maintenance |
| Moderation | Classify, hide |
| Counter Service | likes/replies |

Keep Post Service separate; Comment calls it for ACL/settings.

#### 5.3.2 Observability

| Signal | Why |
|--------|-----|
| Write QPS per post_id (top-N) | Hot detection |
| Durable ack latency | SLO |
| Live lag (event_ts → socket send) | Freshness SLO |
| Fanout drop / queue depth | Overload |
| Cache hit ratio page-1 | Read health |
| Mod hide rate | Spam/quality |
| Slow-mode trigger count | Celebrity ops |

#### 5.3.3 Schema evolution

- Soft fields in JSON for client experimental UI.  
- Rank formula versioned (`score_v2`) with dual-write during migrate.  
- Event schema with `schema_ver` on Kafka.

#### 5.3.4 Testing hot paths

- Load test single `post_id` to 10× expected write.  
- Chaos: kill live gateways mid-event; verify catch-up.  
- Idempotency fuzz on create.  
- Moderation shadow mode before enforce.

### 5.4 Moderation & safety deep dive

```text
Sync path (cheap):
  - regex/blocklist
  - user ban check
  - link spam heuristics

Async path:
  - ML text classifier
  - spam graph features
  - report aggregation

Actions:
  - hide (author sees; others don't)
  - delete
  - shadowban (author sees; not fanout)
  - rate limit
```

Shadowban is powerful for spam on live posts: attacker thinks they succeeded; victims spared.

### 5.5 Counter & like path

```text
like:
  write like edge (idempotent)
  incr counter shard
  emit like_changed
  ranker may update score asynchronously

Don't:
  rewrite full comment row lock for every like on hot comment
```

### 5.6 Cursor design

```text
Newest cursor: base64({ts, comment_id, dir})
Top cursor:    base64({score, comment_id, dir})
Bucket merge cursor: vector of per-bucket offsets OR merged key

Rules:
  - cursors opaque
  - stable under inserts behind cursor (document semantics)
  - deleted items may create holes — skip tombstones
```

### 5.7 Privacy & ACL

| Check | When |
|-------|------|
| Can view post? | list + subscribe + create |
| Can comment? | create (may differ from view) |
| Block graph | filter list/live |
| Ghost / restricted | product-specific filter |

Subscribe must re-validate ACL periodically (token expiry / block changes).

### 5.8 Hot-post fanout deep dive

#### 5.8.1 Amplification identity

```text
fanout_msgs/s ≈ (unique_batches/s) × (subscribers)
NOT comments/s × subscribers  (if coalesced)
Control: lower batches/s (coalesce) AND hierarchical multicast
```

#### 5.8.2 Coalesce worker

```text
per post_id buffer:
  on comment_durable → append to buffer
  flush every T ms OR when buffer size ≥ B
  publish BatchEvent { comments[], watermark, dropped_count? }
ultra-hot: flush summary mode with samples only
```

#### 5.8.3 Hierarchical tree

```text
Origin fanout (post cell)
  → Regional relays (subscribe to post)
    → Edge WS gateways (local socket sets)
Don't: origin opens 500K TCP sends
```

#### 5.8.4 Drop policy under overload

| Priority | Keep |
|----------|------|
| P0 | Player… n/a — here: author + pinned + mod actions |
| P1 | Sampled comments for live UI |
| P2 | Full text batches |
| Shed | Redundant clock-like heartbeats; duplicate likes coalesced |

Expose `live_degraded=true` so clients can poll deltas.

### 5.9 WebSocket rooms deep dive

#### 5.9.1 Room join

```text
WS auth → ACL can_view(post)
 → register conn in room post_id on this gateway
 → send snapshot hint (fetch REST page-1) + since_watermark
 → stream batches with watermarks
```

#### 5.9.2 Registry

```text
Room directory: post_id → relay set / gateway bloom
Hot rooms pinned to dedicated relay pods
Cold rooms: lazy create on first subscriber
```

#### 5.9.3 Catch-up

```text
Client provides last_watermark
Server: if within retained live buffer → replay
Else: instruct REST list + set watermark to now
Retain buffer: last N minutes or M events per post (bounded memory)
```

### 5.10 Sampling & persistence

#### 5.10.1 When to sample

```text
if comment_rate > R or watchers > V:
  live channel switches to SampledLiveEvent
persistence STILL stores every durable comment
sampling is delivery UX, not durability loss
```

#### 5.10.2 Persistence layout

```text
comments_bucket(post_id, bucket) → ordered by (ts, id)
tombstones for deletes
outbox/kafka for live + mod + ranker
cold tier: move old comments off hot SSD by age
```

#### 5.10.3 Read-your-write

Creator’s own comment should appear immediately in UI via optimistic + durable ACK body even if live coalesce delays broadcast.

### 5.11 Progressive scale (10× / 100× / 1,000×)

| Jump | Writes | Live | Reads |
|------|--------|------|-------|
| →10× | Hot buckets | Coalesce + multi-GW | Page-1 Redis |
| →100× | Hot cells | Regional relays | Dedicated rank indexes |
| →1,000× | Ultra-hot sampling UI | Edge fanout fabric | Aggressive aggregates |

**Narrative:** celebrity posts force bucketed writes and coalesced hierarchical live; never scale by “more replicas of a single hot partition” alone.

### 5.12 Failure drills

| Drill | Expected |
|-------|----------|
| Fanout worker down | Durable OK; live lag ↑; clients poll delta |
| One bucket down | Partial newest; degrade banner; repair |
| Gateway drain | Sticky reconnect; catch-up watermark |
| Mod classifier lag | Sync filters still on; async hide later |

---

## 6. Wrap-Up

### 6.1 Design summary

We designed **live comments** as a dedicated plane beside posts:

1. **Durable-first writes** with idempotency and post ACL.  
2. **Sharded storage** by `post_id`, with **bucket split** under hot-post detection.  
3. **Dual indexes** for Newest and Top; async ranker.  
4. **Live delivery** via WebSocket gateways, **coalesced** events, and **hierarchical fanout** — never O(viewers) work on the write critical path.  
5. **Moderation** sync cheap filters + async classifiers; shadowban for spam.  
6. **Progressive scale** to hot cells and edge fanout trees.

### 6.2 Key tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Freshness vs write latency | Fanout async after durable |
| Exact global order vs scale | Per-post order; cross-region eventual |
| Complete Top vs cost | Approx/async Top; sampled at extreme |
| Safety vs latency | Cheap sync + async ML |

### 6.3 Deal-breakers recalled

- ACK after full global fanout.  
- Single DB partition for celebrity posts.  
- Naive Redis Pub/Sub to millions of user channels per comment.  
- Full ML ranking sync on every write.  
- Exact identical world-order of comments.

### 6.4 30-minute interview checklist

1. Clarify live SLO, nested replies, Top vs New, moderation.  
2. Estimate hot-post write × viewers → reject naive fanout.  
3. Draw write → store → Kafka → fanout tree → WS.  
4. Deep dive hot buckets + coalesce.  
5. Ranking + cache.  
6. Walk 10×/100×/1,000×.  
7. List deal-breakers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & product

**Q1: Why not put comments in the Post document?**  
A: Unbounded growth, write contention, and independent scale/live needs. Comments are a high-churn child entity.

**Q2: Chronological vs Top — which is default on viral posts?**  
A: Product choice; often Top for celebrity posts, Newest for small threads. Support both; don’t couple storage to one.

**Q3: How deep should nesting go?**  
A: MVP 1–2 levels. Deep trees hurt UX and amplify abuse; collapse and “view more replies.”

**Q4: Do we need strong consistency across regions for comment order?**  
A: No. Per-post home region / cell with eventual replica reads is enough; author RYW via sticky/primary.

**Q5: What’s the live freshness SLO you’d commit to?**  
A: p99 < 2–5s visible for non-ultra-hot; ultra-hot may coalesce to 0.5–1s batches.

### 7.2 Storage & indexing

**Q6: Cassandra vs MySQL for comments?**  
A: Cassandra/wide-column excels at `(post_id, ts)` append + TTL; MySQL OK with careful sharding. Meta historically TAO/graph + MySQL shards — discuss tradeoffs; pick one and shard correctly.

**Q7: How do you generate `comment_id`?**  
A: Snowflake/ULID for time-sortable ids; avoids central bottleneck.

**Q8: How to paginate under concurrent inserts?**  
A: Keyset cursors on `(ts, id)`. Document that “newest page” may miss/duplicate across refreshes without live; live fills gaps.

**Q9: Where is comment text stored if very long?**  
A: Inline up to N KB; overflow to blob store with pointer; CDN not for private text.

**Q10: How do secondary indexes stay correct?**  
A: Async indexers from Kafka; version fields; repair jobs; read-time filter for status.

### 7.3 Hot posts & fanout

**Q11: Walk the math that kills naive fanout.**  
A: 5K writes/s × 500K viewers = 2.5B msgs/s. Must coalesce, hierarchy, and registry of gateways not users.

**Q12: How do you detect a hot post?**  
A: Sliding window write QPS, concurrent subscribers, cache miss storms; hysteretic thresholds to avoid flip-flop.

**Q13: Explain write buckets.**  
A: Split `post_id` into `N` write partitions; each accepts subset of comments; list merges by sort key; live uses batch merge.

**Q14: How does hierarchical pub/sub reduce load?**  
A: Origin publishes once per region/gateway interest; each edge multiplexes to local sockets. Complexity moves to subscription management.

**Q15: When would you show “12K new comments” instead of each line?**  
A: Ultra-hot (1,000×) when even coalesced lists overwhelm UX/bandwidth; provide sampled stream + count.

**Q16: Redis Pub/Sub vs Kafka for fanout?**  
A: Kafka for durable async processing; Redis/pubsub or specialized push for ephemeral live. Don’t use Kafka as per-socket delivery bus.

### 7.4 Ranking & likes

**Q17: Why not sort by raw likes?**  
A: Early comments dominate; gaming; need recency and Bayesian smoothing.

**Q18: How fast must Top update after a like?**  
A: Seconds OK; not on the like ACK path. Newest unaffected.

**Q19: Counter correctness under retries?**  
A: Idempotent like edges; counters derived or PN-counter/CRDT; periodic reconcile.

**Q20: Pin vs Top?**  
A: Pins are control-plane overrides occupying reserved slots; not pure score.

### 7.5 Reliability & clients

**Q21: Client disconnected for 30s — what happens?**  
A: On resume, `delta?since=cursor` then WS continue; dedupe by id.

**Q22: Duplicate comment events on WS?**  
A: At-least-once; client set of seen ids.

**Q23: Store succeeded, Kafka produce failed?**  
A: Outbox pattern: write outbox row in same store transaction/log; relay to Kafka; or CDC.

**Q24: How to guarantee author sees own comment immediately?**  
A: Write-through author cache / return entity in POST response and merge into local list; sticky read to primary.

**Q25: Slow-mode implementation?**  
A: Per `(post_id, user_id)` token bucket in Redis; 429 + Retry-After; owners exempt optionally.

### 7.6 Safety & abuse

**Q26: How do spam bots attack live comments?**  
A: High-rate low-quality text, copy-paste links, newly created accounts. Defend with rate limits, trust scores, shadowban, ML.

**Q27: Shadowban vs hide?**  
A: Shadowban: author sees, others don’t / no fanout. Hide: neither public nor sometimes author depending on product.

**Q28: Report comment flow?**  
A: Report → queue → aggregate → auto or human; threshold hide.

**Q29: Block graph on live stream?**  
A: Filter at edge with user’s block bloom/cache; refresh periodically.

**Q30: Legal takedown?**  
A: Control plane force-hide; durable audit; replicate tombstone globally ASAP.

### 7.7 Scale drills

**Q31: Memory for 5M concurrent WS?**  
A: ~few KB state/socket → tens of TB if naive one fleet — shard gateways; each holds subset; use efficient event loops.

**Q32: Storage for 10B comments/day × 300B?**  
A: 3 PB/day raw — retention, compression, cold tier mandatory; interview should call this out.

**Q33: Cache size for page-1 of 1M active posts?**  
A: 1M × 20 KB ≈ 20 GB — fits Redis cluster; hot subset much smaller (Zipf).

**Q34: What breaks first at 100×?**  
A: Usually live fanout and hot-key writes, not average cold-post CRUD.

### 7.8 Alternatives & deal-breakers

**Q35: Single global Redis ZSET per post for all comments?**  
A: Works small/medium; memory + single-thread hot key fails celebrity scale; shard/bucket.

**Q36: Store comments only in Kafka?**  
A: Kafka is log/transport, not serving store for random pagination.

**Q37: GraphQL subscription per comment field?**  
A: Fine abstraction; still need same fanout backend — don’t pretend GraphQL solves amplification.

**Q38: CRDT comments for multi-region active-active writes?**  
A: Possible but hard for moderation/ordering UX; prefer home cell single-writer per post.

### 7.9 Interview craft

**Q39: How to open this interview?**  
A: Clarify live SLO, Top/New, nesting, peak viewers on one post, moderation — then split write/live/read load classes.

**Q40: What impresses L5+?**  
A: Amplification math, coalesced hierarchical fanout, hot buckets, outbox, author RYW, explicit deal-breakers, progressive hot cells.

**Q41: Common mistake?**  
A: Designing beautiful WS API then putting synchronous fanout on the write path; or ignoring single-post skew.

**Q42: How related to news feed?**  
A: Feed ranks posts; this ranks/delivers comments inside a post. Different fanout problem (post→viewers vs comment→post viewers).

**Q43: Would you use Cloudflare Durable Objects / similar?**  
A: Reasonable for per-post coordination at edge; still need durable store of record and moderation.

**Q44: Multi-tenant celebrity “war room” tools?**  
A: Slow-mode, keyword mute, mod queue, pin — control plane flags consumed by Comment Service + Live.

**Q45: How do you test catch-up correctness?**  
A: Inject gaps; ensure delta ∪ live is complete/idempotent; property test cursors.

---

### Appendix A — Event schemas

```text
CommentCreated { event_id, comment, post_id, ts }
CommentDeleted { event_id, comment_id, post_id, ts }
CommentUpdated { event_id, comment_id, fields, ver, ts }
CommentBatch   { post_id, events[], coalesce_ts, watermark }
LikeChanged    { comment_id, like_count, ts }
```

### Appendix B — Rate limit policy (example)

| Key | Limit | Window |
|-----|-------|--------|
| user global comments | 60 | 1 min |
| user per post | 10 | 1 min |
| user likes | 120 | 1 min |
| slow_mode per post | 1 | N sec (config) |
| new account factor | ×0.2 | until trust↑ |

### Appendix C — Hot detection pseudocode

```text
on_write(post_id):
  qps = meters[post_id].incr()
  subs = registry.subscribers(post_id)
  if qps > W || subs > S:
    if state[post_id] != HOT:
      enable_hot_mode(post_id, buckets=N)
```

### Appendix D — Coalesce worker

```text
buffer[post_id].append(event)
every 200ms:
  batch = drain(buffer[post_id])
  if batch:
    publish_tree(post_id, CommentBatch(batch))
```

### Appendix E — Bucket merge read

```text
def list_newest(post_id, cursor, limit):
  buckets = bucket_ids(post_id)
  heads = [peek(b, cursor) for b in buckets]
  out = []
  while len(out) < limit:
    b = min(heads, key=sort_key)
    out.append(pop(b))
  return out, new_cursor
```

### Appendix F — Score function

```text
def score(c):
  if c.pinned: return INF_PIN
  likes = c.like_count
  n = likes + c.dislike_count # if any
  conf = bayesian_lower_bound(likes, n)
  recency = exp(-(now - c.ts)/tau)
  return α*conf + β*log(1+c.reply_count) + γ*recency
```

### Appendix G — Outbox pattern

```text
txn:
  insert comment
  insert outbox(event)
commit
relay:
  publish outbox to Kafka
  mark sent
```

### Appendix H — Client reconciliation

```text
local = map(comment_id -> comment)
on POST response: local.add
on Batch: for e in events: apply upsert/delete
on gap: fetch delta(since) then continue
```

### Appendix I — NFR card

```text
Durable ACK before 201
Live p99 < 5s (coalesced)
List p99 < 200ms hot
Never fanout on write critical path
Hot posts bucketed
Idempotent create
```

### Appendix J — Progressive scale card

| Scale | Must add |
|-------|----------|
| 10× | Cache, coalesce, rate limits |
| 100× | Hot cells, regional relays, async ranker fleet |
| 1,000× | Edge fanout fabric, aggregate UI, sampling |

### Appendix K — ACL checklist

```text
view_post?
comment_allowed?
not_blocked(author, viewer)?
not_closed?
slow_mode_ok?
```

### Appendix L — Moderation states

| Status | Author | Others | Live fanout |
|--------|--------|--------|-------------|
| visible | yes | yes | yes |
| hidden | yes/limited | no | no |
| deleted | tombstone | tombstone | delete event |
| shadow | yes | no | no |

### Appendix M — Gateway registry

```text
Interest index:
  post_id -> {gateway_id: refcount}

On subscribe: INCR refcount; if 0→1 subscribe upstream
On last unsubscribe: DEC; if 0 unsubscribe upstream
```

### Appendix N — Capacity worked example

```text
Baseline peak 50K comments/s global
Hot post 5K/s, 500K viewers
Coalesce 250ms => 4 batches/s
Assume 200 regional gateways interested:
  origin publishes ~800 gateway-msgs/s for that post
Each gateway locally serves 2500 viewers avg
Much better than 2.5B
```

### Appendix O — Comparison: pull vs push

| | Push (WS) | Pull (poll) |
|--|-----------|-------------|
| Freshness | Best | TTL-bound |
| Server cost | Stateful | Stateless easier |
| Mobile battery | Better if quiet | Worse if frequent |
| Fallback | — | Required |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Hot post | High viewers and/or write QPS |
| Coalesce | Batch events over short window |
| Bucket | Write shard within a post |
| Tombstone | Soft-delete marker |
| Shadowban | Visible to author only |
| Home cell | Primary region/cluster for a post |

### Appendix Q — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| TAO / social graph | ACL, blocks, friendships |
| Feed | Surfaces posts that attract comments |
| Pub/Sub / folsom-like | Live delivery guts |
| Async consistency | Index maintenance |
| Integrity/spam | Moderation |

### Appendix R — Failure drill table

| Drill | Expected |
|-------|----------|
| Kill 10% live gateways | Auto reconnect + delta |
| Pause ranker 10 min | Newest OK; Top stale |
| Kafka lag spike | Writes OK if store-first; live lag alerts |
| Blocklist deploy bad | Kill switch revert |

### Appendix S — API error codes

| Code | Meaning |
|------|---------|
| 401/403 | AuthZ |
| 404 | post/comment missing |
| 409 | idempotency conflict mismatched body |
| 429 | rate / slow_mode |
| 503 | durable store unavailable |

### Appendix T — 30m checklist (compact)

```text
Clarify → Estimate amplification → Store+Kafka+Fanout diagram
→ Hot buckets → Top rank → Mod → Scale jumps → Deal-breakers
```

### Appendix U — Why async fanout (sequence)

```text
t0 durable commit
t1 ACK client
t2 outbox relay
t3 coalesce window
t4 publish tree
t5 client render
```

### Appendix V — Ultra-hot UX modes

| Mode | Behavior |
|------|----------|
| Full live | Each coalesced batch listed |
| Sampled | Show random/quality sample |
| Aggregate | Counts + highlighted comments only |
| Slow-mode | Restrict writes |

---

*End of Live Comments on Popular Posts system design.*
