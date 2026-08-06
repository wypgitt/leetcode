# System Design: Generic Social Media Platform

> **Focus areas:** Graph (follow/friends) · Feed ranking · Fan-out · Posts/media · Notifications · Search · Counter/read models · Abuse/integrity · Privacy · Celeb/hot keys · Cells
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Hybrid fan-out; home-timeline vs celebrity; deal-breaker = push every post to all followers’ inboxes at celebrity scale without hybrid strategy
> **Interview theme:** Microsoft public-bank — **generic social network** (Twitter/Instagram-class bones); map to Azure when asked; emphasize API clarity + safety

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

Goal: design a **generic social media platform**—users create profiles, follow others (or friend), publish posts (text/images/video), consume a personalized home feed, interact (like/comment/repost), get notifications, and search—while handling celebrities, abuse, and global scale.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Social graph + feed + media + notify | Full TikTok For You research paper |
| Graph | Follow (asymmetric) default; friends optional | Exact Facebook + IG + X clone all features |
| Feed | Home timeline + user profile timeline | Ads auction deep dive (touch lightly) |
| Success | Fresh relevant feed, integrity, cost control | QPS flexing alone |
| Microsoft | Solid distributed design; Azure mapping optional | Copilot features unless asked |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Graph? | Follow / unfollow; optional mutual friends | Graph storage + fan-out implications |
| F2 | Post? | Text, images, short video; edit/delete | Object store + processing |
| F3 | Feed? | Home (followed) + For You optional light | Fan-out / rank |
| F4 | Profile? | User timeline reverse chrono | Easy pull |
| F5 | Actions? | Like, comment, repost, share | Counters + notify |
| F6 | Notify? | In-app + push | Aggregation |
| F7 | Search? | Users, hashtags, posts | Indexes + rank |
| F8 | Privacy? | Public/followers/private | Authz on every read |
| F9 | Media? | Upload, transcode, CDN | Async pipelines |
| F10 | Block/mute? | Yes | Feed filters + authz |
| F11 | DMs? | Defer MVP optional | Separate chat system |
| F12 | Trends? | Optional | Aggregation jobs |
| F13 | Moderation? | Report, automate, human | Integrity pipeline |
| F14 | Ads? | Out / light placeholder | Auction separate |

**MVP:** signup/login, follow, text+image posts, home feed, profile, like/comment, notifications, basic search users/hashtags, block, report.

**Out:** live streaming, full Reels ML, ephemeral stories perfection, payments tipping OS, marketplace.

### 1.2 NFRs

| NFR | Target |
|-----|--------|
| Feed read p99 | < 200–400ms cached |
| Post publish ack | < 300–500ms (media async) |
| Fan-out lag | Seconds typical; celebs different path |
| Availability | 99.9%+ reads; degrade rank → reverse chrono |
| Consistency | Read-your-writes for author; feed eventual |
| Durability | Posts durable before ack |
| Integrity | Abuse controls mandatory at scale |
| Privacy | Authz enforced; GDPR export/delete |
| Peak | Cultural events / celebrity posts 100× |

### 1.3 Cases

Happy: follow → post → followers see feed → like → notify.  
Edges: celebrity 100M followers; private account; block after follow; viral post thundering herd; delete post with fan-out; counter races; bot farms; CSAM pipeline; region bans; hot partition user_id; stale feed cache after privacy change; undeleted media orphans.

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| DAU | 1M | 10M | 100M | 1B |
| Posts/day | 2M | 20M | 200M | 2B |
| Peak QPS read | 50K | 500K | 5M | 50M |
| Edges (follows) | 100M | 1B | 10B | 100B+ |
| Media stored | 100 TB | 1 PB | 10 PB | 100 PB+ |
| Jump | Single region | Multi-region read | Hybrid fan-out+ML rank | Global cells + integrity OS |

### 1.5 Repeat-back

> Social platform with **follow graph**, durable posts/media, **hybrid fan-out feed**, interactions/notifications, search, privacy/block, and integrity—scaled with celebrity exceptions and progressive cells—not naive “push to all inboxes always.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Fan-out math (heart of interview)

```text
Avg user 200 followers → push write amplification 200×
Celeb 50M followers → cannot materialize 50M inbox writes per tweet
⇒ Hybrid: push for normal; pull for celebs / high out-degree
```

### 2.2 Read vs write

```text
Feed reads dominate (10–100× writes)
Cache home timelines aggressively
Media bandwidth dominates cost (CDN egress)
```

### 2.3 Storage

```text
Post metadata 500 B–2 KB
2M posts/day × 1 KB ≈ 2 GB/day metadata
Images: 200 KB–2 MB after processing × attach rate → TBs/day
Graph edges: 8–32 B × 100M = GBs
```

### 2.4 Notification storm

```text
Viral post 1M likes → do NOT 1M push notifies to author raw
Aggregate: "8000 others liked your post"
```

### 2.5 Bottlenecks

Celebrity posts, media processing, counter hot keys, search index lag, integrity review queues, cache stampedes, graph queries for mutuals.

### 2.6 Cost

CDN + object storage + video encode >> app CPU. Design for lazy encode tiers; image size budgets; cache HIT ratios.

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Role | Consistency |
|-------|------|-------------|
| Identity / Profile | Users, sessions | Strong |
| Graph | Follow edges | Strong writes; cached reads |
| Post Service | Post CRUD | Strong per post |
| Media | Blob + processing | Eventual variants |
| Feed / Timeline | Home materialization / merge | Eventual |
| Ranker | Score candidates | Best effort |
| Interactions | Like/comment | Eventual counters; durable events |
| Notifications | Inbox + push | At-least-once aggregated |
| Search | Indexes | Eventual |
| Integrity | Score/block/remove | Sync gates + async |
| Privacy / ACL | Visibility | Strong on change path |

### 3.2 Components

1. API Gateway / BFFs  
2. User Service  
3. Graph Service  
4. Post Service  
5. Media Service + transcoder workers  
6. Feed Service (mix/merge/cache)  
7. Fan-out Workers  
8. Ranker (rules → ML)  
9. Interaction Service  
10. Counter Service (sharded)  
11. Notification Service  
12. Search Ingest/Query  
13. Integrity / Safety  
14. Admin / Mod tools  
15. Cell Directory / user home  
16. CDN / edge  

### 3.3 Post publish API

```text
POST /v1/posts
  {text, media_ids[], visibility, client_post_id}
→ {post_id, created_at}
# media pre-uploaded via POST /v1/media/uploads (signed URL)
```

### 3.4 Feed read API

```text
GET /v1/feed/home?cursor=&limit=
→ {items:[{post, author, social_proof}], next_cursor}
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Graph | Asymmetric follow | Broader product; friends mode optional |
| Fan-out | Hybrid push/pull | Celeb economics |
| Home storage | Redis/Cassandra inbox for normals | Fast read |
| Rank | Light rank MVP; ML later | Ship value |
| Counters | Approximate + reconcile | Hot keys |
| Comments | Sharded by post_id | Viral posts |
| Soft delete | Tombstones | Sync/cache |
| Active-active same user posts | Avoid multi-primary | Ordering pain |
| DMs | Separate system | Different SLOs |
| For You | Candidate + rank optional | Don’t derail MVP |

---

## 4. Architecture Diagram

### 4.1 Context

```text
Client → Edge/CDN → Gateway → Post/Graph/Feed/User...
                         │
            Media uploads → Blob → Transcode → CDN
                         │
            Post durable → Event bus → Fan-out / Search / Notify / Integrity
                         │
            Feed cache ← Fan-out workers (normal users)
            Celeb posts ← Pull merge at read time
```

### 4.2 Hybrid fan-out

```text
on PostCreated:
  followers = graph.getFollowers(author)
  if len(followers) < THRESHOLD and author not in celeb_set:
    for f in followers (sharded jobs):
      timeline.prepend(f, post_id)
  else:
    mark author as pull_source
    # readers merge celeb posts at read

on FeedRead(user):
  inbox = timeline.get(user, cursor)
  celeb_posts = pull_recent(following_celebs)
  muted/blocked filtered
  merge + rank + return
```

### 4.3 Media pipeline

```text
client → signed PUT → blob raw
→ virus/CSAM scanners → encode variants → CDN
post references media_id only after scan policy ok (or staged visibility)
```

### 4.4 Notification aggregation

```text
like events → aggregate window per (owner, post) → single notify
priority: mentions > replies > follows > likes
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Post ack ⇒ durable metadata stored (media may still process).  
2. Authz checked on every post fetch (privacy/block).  
3. Fan-out failures retry; feed may lag but recover.  
4. Deletes propagate tombstones to caches/indexes.  
5. Counters never block publish path.  
6. Integrity takedown is authoritative over caches (purge).  
7. Idempotent client_post_id.  
8. User home cell sticky for writes.  
9. Notification aggregation prevents storms.  
10. Audit for mod actions.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Postgres posts; Redis feed; object storage; monolith OK |
| 10× | Split services; Cassandra/Scylla timelines; CDN; bus |
| 100× | Hybrid fan-out mandatory; multi-region reads; sharded counters; ML rank |
| 1000× | Cells; edge feed; integrity ML; sophisticated candidate systems |

### 5.3 Maintainability

- Fan-out threshold config.  
- Ranker plugin shadow traffic.  
- Schema for post types extensible.  
- Backfill tools for timeline rebuild.  
- Chaos: kill fan-out consumers.  
- Clear ownership: Feed vs Integrity vs Media.

### 5.4 Progressive scale

**1×:** 1M DAU; push fan-out all; Redis lists; Postgres; one region.  
**10×:** Media platformization; cache tiers; search cluster; basic integrity classifiers.  
**100×:** Hybrid fan-out; multi-region; counter service; privacy hardening; ads hooks.  
**1000×:** Near-global; cell isolation; advanced ranking; live features separate; government compliance packs.

### 5.5 Graph storage

```text
Edge: (follower_id, followee_id, created_at, state)
Indexes: out-edges (following), in-edges (followers) sharded
Hot celebs: followers list in object storage segments + cache samples for fan-out jobs
Mutual friends: intersect small sets carefully; precompute sparingly
```

### 5.6 Feed ranking (MVP → better)

MVP: reverse chrono merge.  
Next: score = recency * affinity * quality * -fatigue.  
Signals: author affinity, post engagement early velocity, media type, mutes.  
Degrade to chrono if ranker fails.

### 5.7 Hot keys & celebrities

- Identify celebs by follower count / write amp.  
- Pull path for their posts.  
- Cache post objects at edge.  
- Rate limit actions on celeb posts; shard comment space.  
- Protect author notification inbox with heavy aggregation.

### 5.8 Interactions & counters

Like event → durable log → async counter update → notify aggregate.  
Idempotent like (`user_id, post_id` unique).  
Count display approximate OK (`~1.2M`).  
Reconcile nightly from events if drift.

### 5.9 Comments

Shard by `post_id`; viral posts get dedicated partitions; pagination cursors; hide/remove via integrity; don’t load all for feed cards—show top/count.

### 5.10 Privacy & blocks

Private account: follows require approval; posts visible to approved followers only.  
Block: bidirectional feed/search restrictions; break graph edges or mark ignored.  
Privacy change: invalidate caches; fan-out tombstones for inboxes that shouldn’t see.

### 5.11 Search

Users: prefix/n-gram + popularity.  
Hashtags: post→tag index.  
Posts: inverted index with authz filter at query (careful).  
Ingest via events; eventual consistency seconds–minutes.

### 5.12 Integrity / safety

- Upload scanning (hash DB, ML).  
- Report → queue → escalate.  
- Spam/bot graph features.  
- Rate limits on follow/like/post.  
- Geoblocks / legal takedown workflow with audit.  
- CSAM: specialized pipeline, mandatory.

### 5.13 Multi-region

User home region for writes; secondary read replicas for feed/posts; accept RPO on failover. Cross-region follow is fine; fetch posts via IDs. Avoid multi-primary for same post_id.

### 5.14 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Always push fan-out | Celeb melts cluster |
| Cache without authz | Privacy SEV |
| Exact global counters sync | Latency / outage |
| Sync fan-out in request | Publish p99 dies |
| Ignore integrity | Platform risk |
| Single Postgres forever at 100× | Write bottleneck |
| Unbounded notify | User + cost disaster |

### 5.15 Azure mapping (optional)

| Piece | Azure |
|-------|-------|
| Gateway | Front Door + APIM |
| Posts DB | Cosmos (partition user/post) / SQL early |
| Feed cache | Redis |
| Events | Event Hubs |
| Media | Blob + Media Services / AMPQ workers |
| Search | Cognitive Search |
| CDN | Azure CDN |
| Safety | Async functions + queues |
| Identity | Entra External ID |

### 5.16 Consistency matrix

| Data | Model |
|------|-------|
| Post create | Strong durable ack |
| Home feed | Eventual |
| RYOW author profile | Session sticky / read primary |
| Likes | Eventual counters |
| Follow edge | Strong write |
| Search | Eventual |
| Takedown | Strong override + purge |

### 5.17 Cursor pagination

Opaque cursor `(ts, post_id)`; stable under inserts; avoid OFFSET. Feed merge preserves ordering keys.

### 5.18 Delete & GDPR

Soft delete post → remove from timelines asynchronously → wipe media per retention → search delete → export tools for user data. Backups governed by policy.

### 5.19 Observability

SLIs: publish success, feed latency, fan-out lag, media process time, notify aggregate latency, integrity queue age, cache hit rate. Cardinality care on `post_id` metrics.

### 5.20 Viral event runbook

1. Detect velocity spike.  
2. Protect origin post cache.  
3. Expand counter shards.  
4. Aggregate notifies harder.  
5. Shed noncritical rank features.  
6. Integrity priority sampling.  
7. Scale CDN / origin shields.

---

## 6. Wrap-Up

### 6.1 Designed

Social graph + posts/media + hybrid fan-out feeds + interactions/counters + notifications + search + privacy/block + integrity—progressively scaled with celebrity exceptions and multi-region cells.

### 6.2 Decisions to defend

1. Hybrid fan-out threshold  
2. Durable post before fan-out  
3. Authz on every read  
4. Async media + safety scan gates  
5. Aggregated notifications  
6. Approximate counters  
7. Soft delete/tombstones  
8. Ranker degrade to chrono  
9. User home cell writes  
10. Integrity as first-class plane

### 6.3 Risks

- Fan-out lag UX  
- Integrity false positives/negatives  
- Cache privacy bugs  
- Media cost  
- Hot partitions  
- Regulatory fragmentation  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Product MVP; follow vs friends |
| 5–12 | Fan-out math |
| 12–22 | Publish + hybrid feed |
| 22–30 | Media + interactions |
| 30–38 | Notify, privacy, integrity |
| 38–45 | Scale/celebs/closer |

### 6.5 Closer

> **Generic social media:** durable posts, hybrid push/pull fan-out so celebrities don’t melt writes, authz-aware feed merge, async media with safety gates, aggregated notifications, and progressive multi-region scale—with integrity as a plane, not an afterthought.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product

**Q: Twitter vs Instagram vs Facebook?**  
A: Pick a default (follow + media + home feed). Mention stories/groups as extensions. Don’t boil the ocean.

**Q: Friends mutual vs follow?**  
A: Follow simpler for fan-out explanation; mutual adds edge state `pending`.

### 7.2 Fan-out

**Q: Threshold value?**  
A: Tunable e.g. 10K–100K followers; based on write amp vs read merge cost.

**Q: User crosses threshold?**  
A: Stop pushing; mark celeb; optional rebuild leave old inbox.

**Q: Delete after push?**  
A: Tombstone + async scrub inboxes / cache; pull path checks deleted flag.

### 7.3 Feed

**Q: Missing posts?**  
A: Eventual; repair via pull of author recent; cursor refresh.

**Q: Why not compute feed fully on read always?**  
A: Heavy for large following; hybrid balances.

**Q: Ranking fairness/blocking?**  
A: Filters before rank; integrity labels; mute lists.

### 7.4 Graph

**Q: Store followers for celeb?**  
A: Segmented files / wide rows; never full scan on request path for publish—use celeb pull instead.

**Q: Recommend friends?**  
A: Separate graph ML; defer.

### 7.5 Media

**Q: When is post visible?**  
A: Policy: text immediate; media after scan or with placeholders.

**Q: Video cost?**  
A: Adaptive bitrate; lazy higher rungs; hot/cold storage tiers.

### 7.6 Counters

**Q: Exact likes?**  
A: Unnecessary for display; exact for “user liked?” via edge table.

**Q: Hot counter?**  
A: Shard by hash strips; write aggregation.

### 7.7 Notifications

**Q: Million likes?**  
A: Aggregate windows; badge counts; collapse.

**Q: Push vs in-app?**  
A: In-app inbox durable; push best-effort coalesced.

### 7.8 Privacy

**Q: Change public→private?**  
A: Future follows need approval; historical content visibility shrink; cache purge.

**Q: Block semantics?**  
A: No views either way; comments hidden; search suppress.

### 7.9 Integrity

**Q: Report flow?**  
A: Idempotent report → score → auto action thresholds → human mod → appeal.

**Q: Spam follows?**  
A: Rate limits; anomaly; challenge.

### 7.10 Scale / cells

**Q: Partition key?**  
A: `user_id` home for profile/graph out; posts by `author_id`; feed inbox by `viewer_id`.

**Q: Multi-region post?**  
A: Write home; replicate; read local if fresh enough.

### 7.11 Microsoft-flavored

**Q: Azure Cosmos design?**  
A: Careful partition keys (`viewer_id` for inbox, `post_id` for comments); hot partition mitigation for celebs via pull path.

**Q: API versioning?**  
A: Clean REST/GraphQL BFF; idempotency keys on post.

### 7.12 Rapid-fire

| Q | A |
|---|---|
| Always push? | No |
| Celeb path? | Pull merge |
| Authz skip cache? | Never |
| Exact counters? | No need |
| Fan-out sync in HTTP? | No |
| DMs in MVP? | Optional defer |
| Soft delete? | Yes |
| RYOW? | Author yes |
| Threshold? | Tunable |
| Notify storm? | Aggregate |
| Search leak private? | Filter authz |
| CSAM? | Specialized pipeline |
| Ranker down? | Chrono |
| Hot comments? | Shard |
| GDPR? | Export/delete tooling |
| Ads? | Separate later |
| Stories? | TTL feature later |
| Live? | Separate system |
| Graph DB mandatory? | No |
| Kafka post truth? | No — DB truth |

### 7.13 Traps

- Ignoring celebrity math.  
- Feed cache without privacy.  
- Synchronous fan-out.  
- Exact global like counts.  
- Building For You ML entire interview.  
- Forgetting takedown cache purge.  
- Single DB at hypothetical 1B DAU without staging jumps.  
- OFFSET pagination.  
- Putting media bytes in SQL.  
- Notification per like.

---

## 8. Appendices

### Appendix A — Schemas

```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  handle TEXT UNIQUE NOT NULL,
  visibility TEXT NOT NULL, -- public|private
  home_cell TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE follows (
  follower_id UUID NOT NULL,
  followee_id UUID NOT NULL,
  state TEXT NOT NULL, -- active|pending|blocked
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (follower_id, followee_id)
);
CREATE INDEX follows_followee ON follows(followee_id, created_at);

CREATE TABLE posts (
  post_id UUID PRIMARY KEY,
  author_id UUID NOT NULL,
  text TEXT,
  visibility TEXT NOT NULL,
  media_ids UUID[],
  created_at TIMESTAMPTZ NOT NULL,
  deleted_at TIMESTAMPTZ
);
CREATE INDEX posts_author_time ON posts(author_id, created_at DESC);

CREATE TABLE likes (
  post_id UUID NOT NULL,
  user_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (post_id, user_id)
);
```

```text
Timeline inbox (Cassandra-ish):
  PK = viewer_id, clustering = (ts, post_id) → payload stub
```

### Appendix B — Fan-out pseudocode

```python
THRESHOLD = 50_000

def on_post_created(post):
    n = graph.follower_count(post.author_id)
    if n >= THRESHOLD or is_celeb(post.author_id):
        celeb_index.add(post)
        return
    for shard in follower_shards(post.author_id):
        enqueue_fanout(shard, post.post_id)

def read_home(user_id, cursor, limit):
    pushed = inbox.page(user_id, cursor, limit)
    pulled = celeb_pull(following_celebs(user_id), cursor, limit)
    merged = merge_desc(pushed, pulled)
    filtered = apply_blocks_mutes_privacy(user_id, merged)
    return rank_or_chrono(filtered)[:limit]
```

### Appendix C — Media states

`UPLOADED → SCANNING → SAFE → VARIANTS_READY`  
`SCANNING → REJECTED`  
Post may reference and show placeholder until `VARIANTS_READY`.

### Appendix D — SLIs

| SLI | SLO |
|-----|-----|
| Publish success | 99.9% |
| Feed p99 | < 400ms |
| Fan-out lag p95 (normal) | < 5s |
| Media ready p95 image | < 30s |
| Takedown purge | < 60s critical |

### Appendix E — Kill switches

- Disable fan-out push (pull-only mode)  
- Disable ranker  
- Disable pushes  
- Freeze follows  
- Force image-only (no new video encode)  
- Integrity lockdown mode  

### Appendix F — Narrative beats

1. Choose product shape.  
2. Fan-out math.  
3. Publish + storage.  
4. Hybrid feed read.  
5. Media/safety.  
6. Notify/counters.  
7. Scale + celebs.  
8. Closer.

### Appendix G — Pre-onsite checklist

- [ ] Hybrid fan-out story  
- [ ] Threshold rationale  
- [ ] Authz on read  
- [ ] Media pipeline  
- [ ] Celeb pull merge  
- [ ] Notify aggregate  
- [ ] Progressive scale  
- [ ] 60s closer  

### Appendix H — Extra drills

1. Fan-out amplification math.  
2. Draw hybrid diagram.  
3. Cursor design.  
4. Privacy change purge.  
5. Counter sharding.  
6. Comment hot partition.  
7. CSAM high-level (no illegal detail).  
8. Delete propagation.  
9. Multi-region RYOW.  
10. Rank degrade.  
11. Block semantics.  
12. Search authz.  
13. Timeline rebuild job.  
14. Idempotent post.  
15. CDN cost levers.  
16. Viral runbook.  
17. Graph index choices.  
18. Soft vs hard delete.  
19. Ads boundary.  
20. 60s closer.

### Appendix I — Glossary

| Term | Meaning |
|------|---------|
| Fan-out on write | Push post IDs to follower inboxes |
| Fan-out on read | Pull posts from followed authors at read |
| Hybrid | Push normal / pull celebs |
| Inbox/timeline | Materialized home list |
| Tombstone | Delete marker |
| RYOW | Read-your-own-writes |
| Integrity | Trust & safety systems |

### Appendix J — Sample rank features

Recency, affinity, edge type, media quality, early engagement velocity, content length, mutes, seen-state, time spent proxies (later).

### Appendix K — Event types

`PostCreated`, `PostDeleted`, `Followed`, `Unfollowed`, `Liked`, `Commented`, `MediaReady`, `MediaRejected`, `Takedown`, `UserSuspended`.

### Appendix L — Security checklist

- IDOR tests on post/profile  
- Signed media URLs TTL  
- Rate limits  
- Link unfurl SSRF protections  
- Admin SSO + audit  
- Secrets in vault  

### Appendix M — Comparison

| System | Shared | Different |
|--------|--------|-----------|
| Slack/Teams | Fan-out, notify | Workspace ACL vs public graph |
| YouTube | Media pipeline | Sub graph / long video |
| News site | Feed | Weaker graph |
| Chat | Messages | Smaller fan-out |

### Appendix N — 60s closer

> We persist posts first, then fan out asynchronously. Normal users get push into timeline inboxes; celebrities are pull-merged at read time so write amplification stays bounded. Every feed item is authorization-checked against privacy and blocks. Media is scanned and transcoded off the request path. Likes and notifications are aggregated so virality can’t page-flood. We scale through caching, sharding, and regional cells—and we degrade ranking before we lose the ability to read a chronological feed.

### Appendix O — Common mistakes

1. Push-only forever.  
2. Sync fan-out.  
3. Cache skipping authz.  
4. Exact counters obsession.  
5. ML rabbit hole.  
6. DMs derail.  
7. No delete plan.  
8. OFFSET pages.  
9. Media in DB.  
10. Ignoring safety.

### Appendix P — Counter shard sketch

```text
likes_count[post_id][shard] += 1
display = sum(shards)  # or cached aggregate with lag
```

### Appendix Q — Privacy matrix

| Visibility | Viewer |
|------------|--------|
| public | anyone except blocked |
| followers | approved followers |
| private | approved only |
| self | author |

### Appendix R — Ownership

| Area | Owner |
|------|-------|
| Feed/Fan-out | Feed team |
| Graph | Social graph team |
| Media | Media platform |
| Integrity | T&S eng |
| Notify | Notifications |

### Appendix S — Stretch: For You

Candidate generators (graph, trending, embeddings) → rank → filters (integrity/blocks) → diversity. Separate from following feed; heavy ML platform.

### Appendix T — Sibling prompts

Instagram feed; Twitter/X; live comments; stories; chat/DM systems; ad click aggregator.

---

*End of Generic social media system design prep doc.*
