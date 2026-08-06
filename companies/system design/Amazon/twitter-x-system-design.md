# System Design: Twitter / X

> **Focus areas:** Tweets · Home timeline · User timeline · Fanout-on-write / hybrid · Celebrities · Search (thin) · Trending (thin)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct fanout arithmetic, explicit celebrity hybrid path, deal-breakers for “JOIN follows×tweets on every home scroll” or “push every celebrity tweet to 100M timelines synchronously”  
> **Interview theme:** Amazon SDE III / L6 — design a **Twitter/X-class** microblogging system: post, follow, home/user timelines, celebrity-aware fanout, thin search & trending—owned like a product with cost, reliability, and clear blast-radius controls

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

Goal: **bound the product**—users **post tweets**, **follow** accounts, consume a **home timeline** of followed authors plus a **user timeline** of an author’s posts, handle **celebrity mega-fanout** without melting writes, and support **thin search** and **thin trending**—with progressive scale and Amazon ownership flavor (cost, SLOs, blast radius).

### 1.0 What this is / is not

| Dimension | **Twitter / X (this doc)** | Not this |
|-----------|----------------------------|----------|
| Primary job | Short posts + follow graph + timelines | Full TikTok For-You dense ranker / Bluesky ATProto research |
| Success | Fast post ACK; fresh home feed; user timeline correct | Perfect global ML paper or exact real-time analytics warehouse |
| Entities | User, follow edge, tweet, timeline entry, media ref | Nested page CMS, shopping checkout |
| Read:write | Home reads dominate; writes bursty (viral) | Symmetric CRUD app |
| Consistency | Read-your-write for author; home eventually fresh (seconds) | Strong global linearizability of every follower’s home |
| Search / trends | Thin indexes / top-K hooks | Full Lucene product or Exact global distinct-user trends |
| Amazon lens | Ownership, cost per home scroll, celebrity blast radius, abuse | Only Base62 tweet IDs trivia |

**Scope statement:** Design Twitter/X: tweets, home/user timelines, fanout with celebrity hybrid, thin search & trending—scaled 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Post tweet? | Yes — text ≤280 (or configurable); optional media | Write API + tweet store + media pipeline hook |
| F2 | Home timeline? | Reverse chrono of followed accounts MVP; ranking hook OK | Fanout or merge-on-read; ranking stub |
| F3 | User timeline? | Author’s tweets reverse chron | Author index; easy read |
| F4 | Follow / unfollow? | Directed graph | Adjacency lists + counts |
| F5 | Reply / quote / retweet? | Yes MVP light | Tweet types + pointers; counters |
| F6 | Likes? | Yes | Counter + like graph optional |
| F7 | Mentions / notifications? | Thin — mention notif Phase 1.5 | Event emit |
| F8 | Media? | Images + short video MVP | Object store + CDN |
| F9 | Celebrity accounts? | Yes — millions of followers | Hybrid fanout mandatory |
| F10 | Search? | Thin — recent tweets by keyword/hashtag | Ingest to search index async |
| F11 | Trending? | Thin — top hashtags / topics per region | Streaming top-K; not full product |
| F12 | DMs? | Out of MVP | Mention only |
| F13 | Lists / Spaces / Ads? | Out of MVP core | Feed injection hook only |
| F14 | Edit tweet? | Optional Phase 1.5 | Version + cache purge |
| F15 | Delete / takedown? | Yes | Tombstone + fanout cleanup / filters |
| F16 | Private accounts? | Optional Phase 1.5 | Follow approval; ACL on timelines |
| F17 | Mute / block? | Yes MVP | Filter on read / skip fanout |
| F18 | Pagination? | Cursor-based | Opaque cursors; no deep OFFSET |

**MVP functional scope:**

1. Auth, profiles, follow/unfollow.  
2. Create tweet (text + optional media refs); delete/tombstone.  
3. User timeline: author’s tweets reverse chron.  
4. Home timeline: followed authors (hybrid fanout; ranking stub OK).  
5. Like + retweet/quote/reply light model.  
6. Celebrity / hybrid path so mega-creators don’t melt write fanout.  
7. Block/mute filters.  
8. Thin search ingest + query.  
9. Thin trending top-K hook.  
10. Cursor pagination; CDN for media; metrics/alarms.

**Out of MVP:**

- Full For-You dense ML ranker research platform  
- Encrypted DMs / Spaces live audio  
- Exact global unique-user trending with legal-grade audit  
- Ads auction marketplace  
- Permanent legal archive of every impression forever without cost controls  
- Cross-posting federation protocol

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Post ACK latency | Interactive | p99 < 200–300 ms metadata (media async) |
| N2 | Home timeline read | Snappy scroll | p99 < 100–200 ms cached path |
| N3 | User timeline read | Snappy | p99 < 100–150 ms |
| N4 | Availability | Home & post critical | 99.99% read; 99.9% write |
| N5 | Durability | Don’t lose tweets | Multi-AZ durable tweet store |
| N6 | Freshness (home) | Near-real-time | Typical < 1–5 s for non-celebrity path; celebrity pull bounded |
| N7 | Consistency | Author read-your-write | Sticky / primary read after post |
| N8 | Fanout SLA | Don’t block post on 100M writes | Async fanout; post ACK before full fanout |
| N9 | Cost | Dominated by home reads + fanout storage | Cap timeline length; hybrid celebrities |
| N10 | Abuse resilience | Spam, bots, harassment | Rate limits, trust/safety hooks |
| N11 | Scalability | Progressive | 10× / 100× / 1,000× table |
| N12 | Operability | Clear ownership | Runbooks; cell blast radius |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User posts tweet → durable write → appears on user timeline immediately → async fanout into followers’ home timelines → followers see it on next home fetch.  
2. User opens home → read precomputed timeline from cache/store → hydrate tweet bodies → return page.  
3. User opens `@celebrity` profile → user timeline from author index (no home fanout dependency).  
4. Celebrity with 50M followers posts → mark celebrity → skip full push (or push to online subset) → home merge pulls celebrity tweets on read.  
5. User searches `#topic` → thin search returns recent matching tweet IDs → hydrate.  
6. Trending API returns regional top hashtags for last 1h.  
7. User unfollows → stop future fanout; optional lazy cleanup of home entries.  
8. User deletes tweet → tombstone; home entries filtered or async removed; search/trends lag OK.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate post retry | Idempotency-Key → same tweet_id |
| Follow self | Reject |
| Block: A blocks B | B’s tweets hidden from A; no notifs; optional unfollow |
| Mute | Hide from home without unfollowing |
| Extremely hot celebrity post | Hybrid pull; cache tweet body; single-flight hydrate |
| Fanout worker lag | Post still ACK’d; home freshness SLO alerts; backpressure |
| Home timeline full | Ring buffer / trim oldest beyond N (e.g. 800–2000) |
| Deleted tweet still in home | Filter on hydrate; async GC |
| Search index lag | Accept seconds–minutes; show “recent” not “all history” MVP |
| Trending spam pump | Per-user rate limits; trust weights; approx unique users |
| Media upload slow | Post with processing state; client polls / websocket optional |
| DB outage on tweet store | Fail writes; cached home may still serve hydrated IDs carefully |
| Partial fanout failure | Retry with idempotent timeline inserts; dedupe by tweet_id |
| Clock skew ordering | Snowflake / HLCs for tweet_id time ordering |
| Private account (Phase 1.5) | Only approved followers get fanout / can read |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 50M | 500M | — (cells) | cells × regions |
| Tweets created / day | 100M | 1B | 10B | 100B |
| Peak writes / s (tweets) | 5K | 50K | 500K | 5M |
| Home timeline reads / day | 20B | 200B | 2T | 20T |
| Peak home reads / s | 500K | 5M | 50M | 500M |
| Avg follows / user | 200 | 200 | 200 | 200 |
| Max followers (celebrity) | 10M | 50M | 100M+ | 200M+ |
| Fanout writes / viral tweet (naive) | 10M | 50M | 100M | impossible sync |
| Timeline entries stored | 50B | 500B | 5T | cell-sharded |
| Search queries / s peak | 50K | 500K | 5M | edge+shards |
| Trending updates | continuous | continuous | regional merge | geo cells |
| Media objects / day | 20M | 200M | 2B | CDN-first |

**What each jump forces:**

- **10×:** Redis/timeline cache mandatory; async Kafka fanout; celebrity threshold (e.g. >100K–1M followers) hybrid; CDN media.  
- **100×:** Shard tweet & timeline stores by user_id; multi-region read; online-only fanout optimization; search/trends regionalized.  
- **1,000×:** Cell/partition by user cohort or geography; anycast edge; approx analytics only; dedicated celebrity pull service; aggressive timeline trim + cold tier.

### 1.5 Etc. (Constraints & Assumptions)

| Assumption | Choice for interview |
|------------|----------------------|
| Tweet size | ≤ 1–4 KB metadata; media out-of-band |
| Home length retained | ~800–2000 entries / user hot; older via reconstruct optional |
| Celebrity threshold | Configurable; start ~100K–1M followers or QPS-based |
| Ranking | Chrono MVP + scoring hook; not full ML platform |
| IDs | Snowflake-style 64-bit time-sortable |
| Auth | Session / JWT at edge; not deep IAM design |
| Multi-region | Active-active reads; writes regional affinity early |
| Search | Recent (days–weeks) inverted index; not full archive MVP |
| Trends | Hashtag / entity counts; regional then global merge |
| Compliance | Takedown hooks; GDPR delete async pipeline |

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Examples | Characteristics |
|-------|----------|-----------------|
| Write hot | Post tweet, like, follow | Lower QPS than home; must be durable; fanout amplification |
| Read ultra-hot | Home timeline | Highest QPS; cacheable pages; hydrate fan-out to tweet cache |
| Read hot | User timeline, tweet detail | Author-keyed; cacheable |
| Graph | Follow/unfollow, friend lists | Moderate; adjacency storage |
| Search | Keyword / hashtag query | Spiky; separate index cluster |
| Trends | Top-K read | Tiny result; highly cacheable |
| Media | Image/video bytes | CDN egress dominated |

### 2.2 Storage math (baseline)

```text
Tweets/day: 100M
Avg tweet metadata: ~500 B (text + ids + counters stub) → 50 GB/day raw
With replication ×3 → ~150 GB/day tweet meta
Year ≈ 18–55 TB meta (before compaction/cold)

Home timeline entries:
  Assume fanout-on-write for 95% tweets to avg 200 followers
  But many users inactive — effective fanout often lower; use:
  100M tweets/day × 200 = 20B timeline inserts/day (upper bound naive)
  Entry ~50–100 B → 1–2 PB/day theoretical → MUST trim + hybrid celebrities
  Practical: only fanout to recently-active users OR cap + celebrity pull
  Working assumption after optimizations: 2–5B inserts/day × 80 B ≈ 160–400 TB/day raw
  → retention trim + Redis hot set is mandatory in discussion
```

**Say out loud:** Naive fanout storage is the deal-breaker that forces hybrid design and trim policies.

### 2.3 Fanout arithmetic (must nail)

```text
Celebrity: 50M followers
Sync fanout @ 10K writes/s to timeline store → 5000 s ≈ 83 minutes
→ Post ACK cannot wait; async still floods cluster

Hybrid:
  - Push to online followers only (e.g. 1–5% online) → 0.5–2.5M writes
  - OR skip push entirely; home merge pulls last N celebrity tweets
  - Cache celebrity recent tweets aggressively
```

| Approach | Post latency | Home read cost | Write amplification |
|----------|--------------|----------------|---------------------|
| Pure fanout-on-write | Bad for celebs | Cheap merge | Huge |
| Pure fanout-on-read | Fast post | Merge all followees each read | Low write amp |
| Hybrid (chosen) | Fast post | Cheap for normal; merge celebs | Bounded |

### 2.4 Bandwidth math

```text
Home reads peak 500K QPS × 20 tweets × ~2 KB hydrated JSON ≈ 20 GB/s egress theoretical
CDN/media separate; API responses need edge cache + pagination
Tweet body cache hit critical (Redis) to protect tweet store
```

### 2.5 ID space

```text
Snowflake 64-bit: time | worker | sequence
Ordering ≈ time order; good for timeline sort keys
Avoid DB autoincrement global hotspot
```

### 2.6 Latency budget (home read)

| Step | Budget |
|------|--------|
| Edge / LB / auth | 5–15 ms |
| Timeline ID page from Redis/cache | 5–20 ms |
| Tweet hydrate (mget) | 10–40 ms |
| Filter deleted/blocked + light rank | 5–15 ms |
| Serialize | 5 ms |
| **Total p99 target** | **< 100–200 ms** |

### 2.7 Cache math

```text
DAU 50M; home sessions bursty
Hot tweet bodies: viral + celebs → small working set relative to all tweets
Timeline caches: key = user_id; value = list of tweet_ids (ring)
Celebrity recent: key = author_id; ZSET of tweet_ids
Search/trends: CDN cache 10–60s for public endpoints
```

### 2.8 Scale jump worksheet

| Jump | Tweet write QPS | Home QPS | Forced investment |
|------|-----------------|----------|-------------------|
| Base | 5K | 500K | Redis timelines; Kafka fanout; CDN |
| 10× | 50K | 5M | Shard stores; celebrity hybrid; online fanout |
| 100× | 500K | 50M | Multi-region; cells; search shards; trend regions |
| 1,000× | 5M | 500M | Geo cells; pull-first celebs; approx everything non-critical |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Correctness first for posts:** durable tweet before ACK; author timeline immediate.  
2. **Home freshness without blocking post:** async fanout; SLOs on lag, not sync completeness.  
3. **Celebrity blast radius:** hybrid path; never O(followers) on request thread.  
4. **Cost ownership:** trim timelines; cache hydrates; CDN media.  
5. **Thin search/trends:** separate planes; failure isolation from post/home.  
6. **Operability:** clear ownership boundaries; cell-friendly sharding by `user_id`.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| API Gateway / Edge | Auth, rate limit, TLS, routing |
| Tweet Service | Create/delete/get tweet metadata |
| Graph Service | Follow/unfollow, follower/following lists, counts, celebrity flag |
| Fanout Service | Consume tweet events → write home timeline stores (non-celeb / online) |
| Timeline Service | Serve home & user timelines; merge celebrity pulls; hydrate |
| Tweet Cache | Redis/Memcached for tweet bodies & counters |
| Home Timeline Store | Per-user reverse-chron ID lists (Redis + Cassandra/Dynamo) |
| User Timeline Store | Per-author tweet ID index |
| Media Service | Upload, process, CDN URLs |
| Search Ingest / Query | Thin inverted index for recent tweets |
| Trending Pipeline | Windowed heavy-hitters → top-K API |
| Notification Service | Thin hooks (mention/like) Phase 1.5 |
| Object / Blob Store | Media bytes |
| Event Bus | Kafka/Kinesis: `tweet_created`, `tweet_deleted`, `follow_changed` |

### 3.3 Fanout strategy (say this clearly)

**Chosen: Hybrid fanout**

- **Normal authors** (followers < threshold): **fanout-on-write** — append `tweet_id` to each active follower’s home timeline list.  
- **Celebrities** (followers ≥ threshold OR sustained hot): **fanout-on-read** — home timeline service merges cached “recent tweets by celebrity followees” at read time.  
- Optional optimization: fanout only to **recently active** users; inactive reconstruct on login.

**Deal-breaker to call out:** “On every home scroll, JOIN all followees’ posts sorted globally” without indexes/caches — dies at scale.

### 3.4 API sketch

```text
POST   /v1/tweets
GET    /v1/tweets/{tweet_id}
DELETE /v1/tweets/{tweet_id}

POST   /v1/users/{id}/follow
DELETE /v1/users/{id}/follow
GET    /v1/users/{id}/followers?cursor=
GET    /v1/users/{id}/following?cursor=

GET    /v1/timeline/home?cursor=&limit=
GET    /v1/timeline/user/{user_id}?cursor=&limit=

POST   /v1/tweets/{id}/like
POST   /v1/tweets/{id}/retweet

GET    /v1/search/tweets?q=&cursor=          # thin
GET    /v1/trends?region=&window=            # thin

POST   /v1/media/upload                      # returns media_id
```

**Create tweet (body sketch):**

```json
{
  "text": "hello world",
  "media_ids": ["m_123"],
  "reply_to_tweet_id": null,
  "quote_tweet_id": null,
  "idempotency_key": "uuid"
}
```

### 3.5 Data model

**Tweet**

| Field | Notes |
|-------|-------|
| tweet_id | Snowflake |
| author_id | shard key companion |
| text | sanitized |
| media_ids | list |
| created_at | from id or explicit |
| reply_to / quote_of / retweet_of | optional edges |
| like_count / retweet_count | approx OK via counters |
| status | active / deleted |
| visibility | public / followers (Phase 1.5) |

**Follow edge**

| Field | Notes |
|-------|-------|
| follower_id | |
| followee_id | |
| created_at | |
| state | active / pending (private) |

**Home timeline entry**

| Field | Notes |
|-------|-------|
| user_id | home owner (partition key) |
| tweet_id | |
| author_id | denorm for celeb filters |
| ts | for sort |
| source | fanout / retweet |

**User timeline:** `(author_id, tweet_id, ts)` ordered desc.

### 3.6 Post flow (write path)

1. Auth + rate limit + spam heuristics.  
2. Validate media_ids ready (or allow processing state).  
3. Allocate `tweet_id`; durable write to Tweet Store.  
4. Append to **User Timeline**.  
5. Publish `tweet_created` to event bus.  
6. Return 201 to client (read-your-write: author timeline + get tweet).  
7. **Async:** Fanout Service checks celebrity flag:  
   - non-celeb → batch write home entries for followers (skip blocked/muted where known).  
   - celeb → update celebrity recent ZSET only (no massive push).  
8. **Async:** Search ingest; trending counters; notifications.

### 3.7 Home timeline read path

1. Auth; load `following` set (cached).  
2. Fetch precomputed home ID list page for user (Redis → durable store).  
3. Identify celebrity followees → fetch their recent tweet IDs from celeb cache / user timeline.  
4. Merge-sort by tweet_id/time; apply mute/block/delete filters.  
5. Optional light ranker stub (boost recency).  
6. Hydrate tweets via mget cache → tweet service.  
7. Return page + next cursor.

### 3.8 User timeline read path

1. Query user timeline index by `author_id` + cursor.  
2. Hydrate; enforce ACL if private.  
3. Cache pages for hot celebrities at edge/Redis.

### 3.9 Search (thin)

- Ingest pipeline: tokenize text/hashtags → inverted index (Elasticsearch/OpenSearch or custom).  
- Retention: recent window (e.g. 7–30 days) for MVP cost control.  
- Query: retrieval of tweet_ids → hydrate via Timeline/Tweet services.  
- Isolation: search cluster failure must **not** break post/home.

### 3.10 Trending (thin)

- Stream hashtag/entity events from posts.  
- Per-region sliding windows (5m, 1h, 24h).  
- Approx heavy-hitters + damping; anti-spam rate limits.  
- Materialize top-K snapshots; CDN-cache `GET /trends`.  
- Not exact distinct-global-user analytics in MVP.

### 3.11 Media

- Client uploads to media service (presigned URL to object store).  
- Async transcode/variants; virus scan hook.  
- Tweet stores `media_id` + CDN URLs when ready.  
- Serve bytes only via CDN; never origin hot path for images.

### 3.12 Tradeoffs table

| Decision | Options | Choice | Why |
|----------|---------|--------|-----|
| Home generation | Push / Pull / Hybrid | Hybrid | Celebs + cost |
| Timeline store | Redis-only / Cassandra / Dynamo | Redis hot + durable KV | Latency + durability |
| Tweet ID | UUID / Snowflake / DB seq | Snowflake | Sortable, no hotspot |
| Counters | Sync DB / Redis PNCOUNTER | Redis + periodic reconcile | Hot keys |
| Search | Sync on write / async | Async | Post latency |
| Ranker | Chrono / ML | Chrono + hook | Interview scope |
| Fanout target | All followers / active only | Active + celeb pull | Cost |

### 3.13 Abuse / spam controls (MVP+)

- Per-user / per-IP rate limits on post, follow, like, search.  
- New-account friction; phone/email trust tiers.  
- Automod hooks on text/media before or just after ACK (shadowban path).  
- Block/mute; report → trust & safety queue.  
- Trending gaming defenses (user uniqueness approx, velocity caps).

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
                     +------------------+
  Clients ---------> | Edge / API GW    |
                     | auth, RL, TLS    |
                     +--------+---------+
                              |
        +---------------------+----------------------+
        |                     |                      |
        v                     v                      v
 +-------------+      +---------------+      +---------------+
 | Tweet Svc   |      | Graph Svc     |      | Timeline Svc  |
 +------+------+      +-------+-------+      +-------+-------+
        |                     |                      |
        v                     v                      |
 +-------------+      +---------------+              |
 | Tweet Store |      | Graph Store   |              |
 | (shard u/t) |      | followers     |              |
 +------+------+      +-------+-------+              |
        |                     |                      |
        |   tweet_created     | celebrity flags      |
        v                     v                      v
 +-------------+      +---------------+      +---------------+
 | Event Bus   |----->| Fanout Workers|--->| Home TL Store |
 | (Kafka)     |      | (hybrid)      |    | + Redis       |
 +------+------+      +---------------+      +---------------+
        |                                        ^
        |                                        | celeb pull
        +-------> Celebrity Recent Cache --------+
        |
        +-------> Search Ingest -----> Search Cluster
        +-------> Trending Pipeline -> Trends Cache / API
        +-------> Media Pipeline ----> Object Store -> CDN
```

### 4.2 Post sequence

```text
Client -> API: POST /tweets
API -> Tweet Svc: create
Tweet Svc -> Tweet Store: put durable
Tweet Svc -> User TL: append
Tweet Svc -> Bus: tweet_created
Tweet Svc -> Client: 201 {tweet_id}
Bus -> Fanout: if not celeb: batch home writes
Bus -> Search/Trends/Notif: async
```

### 4.3 Home sequence

```text
Client -> Timeline Svc: GET /timeline/home
Timeline -> Home Store/Redis: page of tweet_ids
Timeline -> Graph: celebrity followees (cached)
Timeline -> Celeb Cache / User TL: recent celeb tweets
Timeline: merge + filter mute/block/deleted
Timeline -> Tweet Cache: mget bodies
Timeline -> Client: page + cursor
```

### 4.4 Celebrity path

```text
tweet_created(author=celeb)
  -> update ZSET celeb:{author_id} (recent N)
  -> optional: push to online followers subset
  -> DO NOT enqueue 50M home writes

home_read(user)
  -> precomputed IDs ∪ pull celeb followees' recent
  -> merge-sort
```

### 4.5 Cell architecture at 100×+

```text
                Global Edge / Directory
                        |
        +---------------+---------------+
        | Cell A        | Cell B        | Cell C
        | users 0-N     | users N-M     | region EU
        | tweet+TL+graph| ...           | ...
        +---------------+---------------+
Cross-cell follow: federation via graph stubs + remote fanout topics
Celebrity: global hot service or replicated celeb caches
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. A successfully ACK’d tweet exists durably and appears on author user timeline.  
2. Deleted/tombstoned tweets must not be returned after hydrate filter (bounded lag OK for search).  
3. Home may be briefly stale; must not show tweets from users you don’t follow (except ads hook out of scope).  
4. Block/mute must be enforced on read path even if fanout raced.  
5. Fanout inserts are idempotent on `(home_user_id, tweet_id)`.

#### 5.1.2 Failure modes

| Failure | User impact | Mitigation |
|---------|-------------|------------|
| Tweet store down | Cannot post/get miss | Multi-AZ; fail closed on write |
| Fanout lag | Stale home | Lag metrics; scale workers; degrade to pull for more authors |
| Redis TL flush | Home miss storm | Warm from Cassandra/Dynamo; request coalescing |
| Graph store down | Follow broken; home degrade | Cached following sets; read-only mode |
| Search down | Search 503 | Home/post unaffected |
| Trends down | Empty trends | Cached last snapshot |
| Media pipeline down | Tweets without media ready | Show processing placeholder |
| Partial cell outage | Cohort impacted | Cell isolation; don’t cascade |

#### 5.1.3 Durability & backup

- Tweet store: quorum writes; PITR / backups.  
- Timeline durable tier: replicated KV.  
- Redis = cache/accelerator; rebuildable from durable + replay (accept rebuild cost).  
- Event bus retention long enough for fanout replay (hours–days).

#### 5.1.4 Consistency nuances

| Path | Model |
|------|-------|
| Author post → user TL | Read-your-write (primary / sync append) |
| Follower home | Eventual (seconds typical) |
| Like counters | Eventual / approximate |
| Search | Eventual |
| Trends | Approximate + delayed |

#### 5.1.5 Security & trust

- Authn at gateway; authz on private accounts.  
- SSRF/XSS: sanitize text; media type allowlists; CSP on web.  
- Credential stuffing / spam: adaptive RL + device reputation.  
- Takedown: tombstone + purge caches + search delete-by-query.

### 5.2 Scalability

#### 5.2.1 Home read scaling (the main game)

- Cache home ID pages in Redis.  
- Tweet body mget with local/remote cache; single-flight.  
- Pagination short pages (20–50).  
- Edge cache **not** for personalized home (private); only public user TL / trends / static.  
- At 100×+: region-local timeline service; sticky sessions optional.

#### 5.2.2 Write path & fanout scaling

- Shard tweet store by `tweet_id` or `author_id` (author_id helps user TL locality).  
- Fanout workers partitioned by `author_id` or follower hash ranges.  
- Batch writes to home store (pipeline).  
- Backpressure: if fanout lag > SLO, widen celebrity pull set dynamically.  
- Follow graph: store followers list optimized for sequential fanout reads (chunked).

#### 5.2.3 Celebrity threshold tuning

| Signal | Use |
|--------|-----|
| Follower count | Static threshold |
| Recent fanout lag | Dynamic promote to celeb |
| Tweet QPS of author | Hot author pull |
| Online follower estimate | Online-only push |

**Interview line:** Threshold is an **operational dial**, not a moral category.

#### 5.2.4 Timeline trim & cold storage

- Hot Redis: last N IDs.  
- Durable: last N' (larger) in KV.  
- Beyond: optional reconstruct from followees’ user timelines (expensive; rare).  
- Cost control is part of the design, not an afterthought.

#### 5.2.5 Multi-region

- Users affinity to home region.  
- Cross-region follows: async replicate fanout events; accept higher lag.  
- Celebrities: replicate recent tweet ZSETs globally.  
- Search/trends: regional indexes; global trends merge.

#### 5.2.6 Cost controls (talk like an owner)

| Lever | Effect |
|-------|--------|
| Hybrid celebs | Cuts PB-scale fanout |
| Active-only fanout | Cuts writes to dormant homes |
| Trim N | Caps storage |
| Media CDN + variants | Cuts origin egress |
| Thin search retention | Caps index $ |
| Approx counters | Cuts sync write load |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Tweet API + store | Tweet team |
| Graph | Graph team |
| Fanout + home store | Timeline team |
| Search | Search team |
| Trends | Trends / data streaming |
| Media | Media platform |
| Trust & safety hooks | T&S eng |

#### 5.3.2 Safe evolution

- Version APIs; additive tweet fields.  
- Fanout event schema evolution (Avro/Protobuf compat).  
- Feature flags for celebrity threshold and pull vs push experiments.  
- Dark-read new merge algorithms before cutover.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Post success | 99.9% |
| Post p99 | < 300 ms |
| Home p99 | < 200 ms |
| Fanout lag p99 (non-celeb) | < 5–15 s |
| Search freshness | < 30–60 s typical |
| Trends freshness | < 1–5 min |

Metrics: fanout queue depth, celeb pull merge time, hydrate miss rate, trim rate, block filter count.

#### 5.3.4 Progressive scale checklist

| Scale | Checklist |
|-------|-----------|
| 10× | Redis home; Kafka fanout; CDN; celeb threshold live |
| 100× | Sharded stores; multi-region; online fanout; search shards |
| 1,000× | Cells; dynamic celeb; pull-first default for mega; cold tier |

### 5.4 Deep dive: hybrid merge algorithm

```text
function home_page(user, cursor, limit):
  following = cache_following(user)  # includes celeb flags
  pushed = home_store.scan(user, cursor, limit * 2)
  celeb_ids = [f for f in following if f.is_celeb]
  pulled = []
  for c in celeb_ids:
    pulled += celeb_recent(c, since=cursor_ts_window)
  merged = merge_desc_by_tweet_id(pushed, pulled)
  merged = filter_blocked_muted_deleted(user, merged)
  page = merged[:limit]
  return hydrate(page), next_cursor(page)
```

**Pitfalls:** pulling too many celebs (users following 5K celebs) → cap pull set; sample; or require lists. Star topology users need special handling.

### 5.5 Deep dive: unfollow & delete

- **Unfollow:** stop future fanout; leave old home entries (filter by following set on read) OR async scrub. Prefer filter-on-read for simplicity.  
- **Delete tweet:** tombstone in tweet store; user TL remove; search delete async; home entries filtered on hydrate; optional async fanout `tweet_deleted` for eager removal.

### 5.6 Deep dive: counters & hot keys

- Viral tweet like_count is a hot key.  
- Use Redis counters / sharded counters; periodic reconcile to durable.  
- Never do `UPDATE tweets SET likes=likes+1` on single row at 1,000×.

### 5.7 Deep dive: thin search indexing

```text
tweet_created -> enrich tokens/hashtags -> index doc {tweet_id, author_id, ts, text}
Query -> retrieve top tweet_ids by recency/BM25 -> hydrate -> ACL filter
```

Out of scope: full archive search across decade — mention cold tier / batch index.

### 5.8 Deep dive: thin trending

```text
hashtag events -> regional count-min / HeavyKeeper -> candidate heap
-> periodic snapshot top-K -> Redis/CDN
Anti-gaming: per-user tag rate limit; account age weight; decline retweet farms
```

### 5.9 Testing & resilience

- Load test fanout with synthetic celebs.  
- Chaos: kill fanout workers; verify post ACK + lag alerts.  
- Property tests: idempotent home inserts; cursor stability.  
- Shadow traffic for merge algorithm changes.

### 5.10 Amazon leadership connection (brief)

- **Ownership:** fanout lag is *your* pager, not “Kafka’s problem.”  
- **Frugality:** hybrid + trim beats buying infinite disk for naive push.  
- **Bias for action:** ship chrono+hybrid; leave ML ranker hook.  
- **Dive deep:** do the celebrity arithmetic on the whiteboard.

---

## 6. Wrap-Up

### 6.1 30-second recap

Twitter/X is a **durable tweet store + graph + hybrid timeline system**: ACK posts after durable write and user-timeline append; **async fanout** for normal authors; **celebrity pull-merge** on home read; caches for hydrate; **thin search/trends** isolated; scale via sharding → regions → cells, with trim and active-only fanout for cost.

### 6.2 Key tradeoffs

| Tradeoff | Pick |
|----------|------|
| Fresh home vs post latency | Async fanout; don’t block ACK |
| Push vs pull | Hybrid by celebrity/hotness |
| Exact trends vs cost | Approx top-K |
| Infinite home history vs $ | Trim + optional reconstruct |
| Ranked vs chrono | Chrono MVP + hook |

### 6.3 Risks & follow-ups

- Users following thousands of celebrities → merge CPU; need caps.  
- Fanout backlog poison during viral events → dynamic celeb promotion.  
- Search/T&S lag vs legal takedown SLAs.  
- Cross-region follow lag UX.  
- Counter drift reconciliation.

### 6.4 What “good” looks like

- Nails fanout math and hybrid rationale.  
- Clear data model + APIs.  
- Separates user TL vs home TL.  
- Isolates search/trends.  
- Speaks cost, SLOs, failure modes, ownership.  
- Progressive 10×/100×/1,000× without handwaving.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. Chrono vs ranked home — what do you ship first?  
2. Are retweets copies or pointers?  
3. Soft delete vs hard delete?  
4. Do muted words filter fanout or read?  
5. What’s the celebrity definition?  
6. Private accounts — impact on fanout?  
7. Edit tweet — cache invalidation?  
8. How long is home history?  
9. Exact like counts required?  
10. Global vs regional trends?  
11. Idempotency for mobile retries?  
12. Ads injection point without redesign?

### 7.2 Fanout & timelines (Q13–Q28)

13. Show math for 50M-follower fanout.  
14. Online-only fanout — how detect online?  
15. Inactive user login storm — cold home rebuild.  
16. Cursor design for merge(push, pull).  
17. Unfollow filter-on-read vs scrub.  
18. Home store Redis + Cassandra roles.  
19. Ordering: tweet_id vs created_at.  
20. Hot key celebrity user timeline.  
21. Fanout idempotency key.  
22. Backpressure strategy when lag spikes.  
23. Dynamic threshold promotion.  
24. Lists as separate timelines.  
25. Quote tweet fanout rules.  
26. Reply visibility (conversation).  
27. Timeline trim eviction policy.  
28. Multi-device read-your-write for author.

### 7.3 Graph (Q29–Q40)

29. Follower list storage layout for fanout scans.  
30. Count accuracy for 100M followers.  
31. Follow rate limits / follow-churn abuse.  
32. Block vs mute vs unfollow.  
33. Bi-directional friends vs directed follow.  
34. Graph shard by follower vs followee.  
35. Celebrities’ following list UX.  
36. Pending follow requests queue.  
37. Secondary indexes for “mutuals”.  
38. Graph cache invalidation.  
39. Infer celebrity from edge QPS.  
40. Cross-cell follow edges.

### 7.4 Search & trends thin (Q41–Q52)

41. Why async index?  
42. Hashtag vs full-text schema.  
43. Abuse of search (enumeration).  
44. Takedown latency in index.  
45. Trend spam defenses.  
46. Regional merge for global top-K.  
47. Exact vs approx counts.  
48. CDN caching trends safely.  
49. Query suggestion / typeahead (out of scope pointer).  
50. Archive search cold path.  
51. Multi-lingual tokenization.  
52. Isolating search GC from tweet GC.

### 7.5 Scale & ops (Q53–Q68)

53. What breaks first at 10×?  
54. Cell routing directory design.  
55. Multi-region active-active conflicts.  
56. Cost per 1000 home scrolls.  
57. SLO for fanout lag — product vs eng.  
58. Hot partition author_id.  
59. Media egress bill control.  
60. Chaos test plan.  
61. Schema migration for tweet entities.  
62. Blue/green fanout workers.  
63. Data retention / GDPR delete.  
64. Observability red dashboard.  
65. Capacity planning worksheet.  
66. When to prefer pull-first globally.  
67. Counter reconciliation job.  
68. Search cluster sizing vs tweet rate.

### 7.6 Behavioral / Amazon (Q69–Q75)

69. Tell me about a time fanout lag would page you — what’s the runbook?  
70. How do you justify hybrid complexity to a skeptical TPM?  
71. Frugality: cut timeline retention — how persuade stakeholders?  
72. Dive deep: whiteboard celebrity merge edge cases.  
73. Disagree & commit: PM wants sync fanout for “consistency”.  
74. Ownership: search outage blamed on tweet team — how clarify?  
75. Customer obsession: stale home after celebrity post — UX copy vs eng fix.

---

## 8. Appendices

### Appendix A — Push / pull / hybrid matrix

| Author type | Write path | Home read |
|-------------|------------|-----------|
| Normal | Push to followers’ homes | Read home list |
| Celebrity | Update recent ZSET | Merge pull |
| Newly viral | Dynamic promote | Mix |

### Appendix B — Example tweet record

```json
{
  "tweet_id": "1844674407370955161",
  "author_id": "U_42",
  "text": "shipping hybrid fanout",
  "media_ids": [],
  "created_at": 1754470000,
  "reply_to": null,
  "quote_of": null,
  "retweet_of": null,
  "like_count": 1204,
  "retweet_count": 88,
  "status": "active"
}
```

### Appendix C — Home timeline Redis sketch

```text
Key: home:{user_id}  → ZSET score=tweet_id/ts member=tweet_id
Cap: ZREMRANGEBYRANK trim to last 1000
celeb:{author_id} → ZSET recent tweets
tweet:{id} → HASH/JSON body cache TTL
```

### Appendix D — Rate limit sketch

| Subject | Posts | Follows | Home reads | Search |
|---------|-------|---------|------------|--------|
| New user | 50/day | 50/day | bursty OK | 100/hour |
| Normal | 240/day | 400/day | high | 300/hour |
| Trusted | higher | higher | high | higher |
| Celebrity | higher posts | — | — | — |

### Appendix E — Error codes

| Code | Meaning |
|------|---------|
| 201 | Tweet created |
| 200 | OK |
| 401 | Auth required |
| 403 | Blocked / private forbidden |
| 404 | Missing / deleted (uniform) |
| 409 | Idempotency conflict mismatch |
| 413 | Tweet/media too large |
| 429 | Rate limited |
| 503 | Dependency outage |

### Appendix F — Anti-patterns (deal-breakers)

| Anti-pattern | Why |
|--------------|-----|
| Sync fanout to 50M followers on request thread | Melts p99 |
| SQL join follows×tweets each home scroll | Cannot scale |
| Single global RDBMS for all tweets | Hotspot / capacity |
| Personalized home on public CDN | Privacy leak / wrong content |
| Exact global unique trends at peak write | Costly; gamed |
| Unbounded home lists | Infinite storage bill |
| Search failure blocks posting | Poor isolation |

### Appendix G — Capacity worksheet

```text
Tweets/day _____ × meta _____ = tweet storage _____
Avg followers _____ × active fraction _____ = fanout inserts _____
Home QPS _____ × page size _____ × bytes _____ = egress _____
Celebrity threshold _____ ; #celebs _____ ; pull merge cost _____
Search retention days _____ ; index size _____
```

### Appendix H — 45-minute timebox

| Minutes | Focus |
|---------|-------|
| 0–5 | Requirements: home/user TL, celebs, search/trends thin |
| 5–12 | Estimates: QPS, fanout math, storage |
| 12–25 | HLD: services, hybrid, APIs, model |
| 25–35 | Deep dive: celebrity merge OR fanout failure |
| 35–42 | Scale 10×/100×/1,000×, cost, SLOs |
| 42–45 | Wrap-up ownership |

### Appendix I — Glossary

| Term | Meaning |
|------|---------|
| Fanout-on-write | Push tweet id into followers’ homes at write time |
| Fanout-on-read | Merge followees’ posts at read time |
| Hybrid | Push normal + pull celebrities |
| User timeline | Author’s posts index |
| Home timeline | Viewer inbox of followed content |
| Celebrity threshold | Operational cutoff for pull path |
| Hydrate | Expand IDs → full tweet objects |
| Tombstone | Deleted marker |

### Appendix J — Sample home response

```json
{
  "items": [
    {"tweet_id": "…", "author_id": "U_1", "text": "…", "like_count": 10}
  ],
  "next_cursor": "eyJ0cyI6Li4ufQ",
  "server_time": "2026-08-06T07:22:11Z"
}
```

### Appendix K — Ownership RACI

| Activity | Tweet | Graph | Timeline | Search | T&S |
|----------|-------|-------|----------|--------|-----|
| Celebrity threshold change | C | C | A | I | C |
| Takedown | C | I | C | C | A |
| Fanout lag SLO | C | I | A | I | I |
| Index mapping | C | I | I | A | C |
| Rate limit tiers | C | C | C | C | A |

### Appendix L — Progressive scale one-pager

| Scale | Bottleneck | Investment |
|-------|------------|------------|
| 10× | Home QPS + naive fanout $ | Redis, Kafka, hybrid, CDN |
| 100× | Shard hotspots, regions | User sharding, online fanout, search shards |
| 1,000× | Cells, mega-celebs, egress | Geo cells, pull-first, cold tier, approx counters |

### Appendix M — Comparison checklist

| Topic | Twitter/X answer |
|-------|------------------|
| vs Instagram | Shorter text; similar hybrid feed; less media-heavy MVP |
| vs Facebook | Directed follow vs friendship; weaker privacy MVP |
| vs TikTok For-You | Not dense interest graph ranker first |
| vs email inbox | Fanout similar; social graph + public ids |

### Appendix N — Minimal threat model

| Asset | Threat | Control |
|-------|--------|---------|
| Attention / trends | Spam gaming | RL, trust weights, approx uniques |
| Users | Harassment | Block/mute, report, filters |
| Platform $ | Fanout/storage abuse | Hybrid, trim, quotas |
| Integrity | Botnets | Device reputation, anomaly detection |

### Appendix O — Celebrity decision pseudocode

```text
function is_celebrity(author):
  if author.followers >= FOLLOWER_THRESHOLD: return true
  if author.recent_fanout_lag_p99 > LAG_SLO: return true
  if author.tweet_qps > HOT_QPS: return true
  return false
```

### Appendix P — Event schemas (sketch)

```json
{"type":"tweet_created","tweet_id":"…","author_id":"…","ts":0,"is_celeb":false}
{"type":"tweet_deleted","tweet_id":"…","author_id":"…","ts":0}
{"type":"follow_changed","follower":"…","followee":"…","op":"follow"}
```

### Appendix Q — Read authz pseudocode

```text
function authorize_tweet_read(tweet, viewer):
  if tweet.status != active: deny(404)
  if tweet.visibility == public: allow
  if tweet.visibility == followers:
    if graph.is_follower(viewer, tweet.author_id): allow else deny(403)
  if graph.is_blocked(tweet.author_id, viewer): deny(404)
```

---

*End of Amazon SDE III prep doc — Twitter / X System Design.*
