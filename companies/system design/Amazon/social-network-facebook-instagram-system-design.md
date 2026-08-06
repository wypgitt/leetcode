# System Design: Social Network (Facebook / Instagram-style)

> **Focus areas:** Social graph · Feed generation · Media pipeline · Privacy / ACL · Notifications (high-level) · Celebrity hybrid · Ranking hooks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct graph+feed arithmetic, explicit privacy enforcement points, deal-breakers for “JOIN friends×posts every scroll” or “notifications inline on every like write”  
> **Interview theme:** Amazon SDE III / L6 — design a **Facebook/Instagram-class** social network: friendships/follows, posts+media, home feed, privacy, high-level notifications—owned with cost, reliability, and blast-radius discipline

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

Goal: **bound the product**—a Facebook/Instagram-style network where users maintain a **social graph** (friendship and/or follow), publish **posts with media**, consume a **home feed**, enforce **privacy**, and receive **notifications** at a high level—scaled progressively with Amazon ownership flavor.

### 1.0 What this is / is not

| Dimension | **FB/IG-style social (this doc)** | Not this |
|-----------|-----------------------------------|----------|
| Primary job | Graph + posts + media + feed + privacy | Full Messenger E2EE, Marketplace, or Reels research ranker |
| Success | Fast publish; relevant fresh feed; correct privacy; reliable media | Perfect global ML paper |
| Graph | Friends (bi-di) and/or follows (directed) — pick hybrid IG-like directed + FB private | Exact FB Groups + Events mega-suite |
| Media | Upload → process → CDN | Codec invention deep dive |
| Feed | Hybrid fanout + ranking hook | Pure SQL join-on-read at Meta scale |
| Notifications | High-level service + fanout | Exact delivery semantics of every push provider |
| Amazon lens | Ownership, privacy incidents as SEVs, cost/feed, media egress | Only UI pixel polish |

**Scope statement:** Design Facebook/Instagram-style social: graph, feed, media, privacy, notifications high-level—10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Graph model? | IG-like **follow** MVP; FB **friend request** Phase 1.5 or both | Adjacency + request states |
| F2 | Post types? | Text + image + short video | Media pipeline |
| F3 | Home feed? | Ranked with chrono fallback | Hybrid fanout + ranker hook |
| F4 | Profile / grid? | User’s posts reverse chron | Author index |
| F5 | Privacy? | Public / friends / private account | ACL on read + fanout |
| F6 | Celebrity / mega pages? | Yes | Hybrid fanout |
| F7 | Likes / comments? | Yes MVP light | Counters + comment service |
| F8 | Notifications? | Like, comment, follow, mention high-level | Notif service + channels |
| F9 | Stories? | Phase 1.5 | 24h TTL store |
| F10 | Groups / pages? | Thin — pages as celeb authors optional | Same post pipe |
| F11 | Search users? | Yes MVP | User index |
| F12 | DMs? | Out of MVP | Mention only |
| F13 | Ads? | Out of MVP core | Feed injection hook |
| F14 | Block / mute? | Yes | Filters + edge rules |
| F15 | Share / reshare? | Light | Pointer posts |
| F16 | Album / multi-photo? | Optional | Media set on post |

**MVP functional scope:**

1. Auth, profiles, follow (and optional friend-request state machine).  
2. Upload media → process variants → create post with privacy.  
3. Home feed of graph neighbors (hybrid fanout; ranking stub OK).  
4. Profile feed / post detail with ACL.  
5. Like + comment; high-level notifications.  
6. Celebrity/hybrid path.  
7. Block/mute; privacy modes.  
8. Cursor pagination; CDN media.  
9. Metrics/alarms; takedown hooks.

**Out of MVP:**

- Full Reels For-You dense ranker  
- Live streaming  
- Encrypted DMs / calls  
- Marketplace / checkout  
- Exact global trending product  
- FB Groups full ACL + admin roles suite

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Publish ACK | Feels instant | p99 < 300 ms metadata; media async |
| N2 | Feed read | Snappy | p99 < 100–200 ms |
| N3 | Media availability | Critical | CDN 99.9%+; multi-AZ origin |
| N4 | Privacy correctness | **Hard requirement** | No unauthorized post leakage (SEV-0 class) |
| N5 | Notification latency | Near-real-time | p99 < 1–5 s typical in-app |
| N6 | Durability | Don’t lose posts | Multi-AZ |
| N7 | Freshness | Feed seconds-level | Async fanout |
| N8 | Cost | Media + feed storage dominate | CDN, trim, hybrid |
| N9 | Availability | Feed & publish critical | 99.99% read; 99.9% write |
| N10 | Abuse | Spam, fake engagement | RL, T&S hooks |
| N11 | Scale | Progressive | 10×/100×/1,000× |
| N12 | Operability | Clear ownership | Privacy test suite mandatory |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User uploads photo → processing → publishes post (friends-only) → async fanout to friends’ feeds → friends see it; non-friends cannot.  
2. Public creator posts → hybrid/celebrity path → followers’ feeds update via push or pull.  
3. User likes post → counter++; notification to author (aggregated).  
4. User comments → comment stored; notif to author / thread participants (high-level).  
5. Private account: follow request → approve → edge active → fanout begins.  
6. User blocks another → edges severed; content hidden both ways as policy dictates.  
7. Profile grid loads author posts with ACL checks.  
8. Push notification delivered for high-priority events; in-app inbox always.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Privacy change public→private | Stop fanout; revoke caches; non-followers lose access |
| Friend removed / unfollow | Filter-on-read; stop future fanout |
| Celebrity friends-only (rare) | Still ACL on read; careful pull path |
| Notification storms (viral post) | Aggregate (“100 people liked”); rate limit pushes |
| Media processing slow | Post in `processing`; client polls |
| Deleted post | Tombstone; feed filter; notif links 404 |
| Comment on deleted post | Reject |
| Cache serves friends-only to stranger | **Forbidden** — cache keys must include ACL context or be private |
| Partial fanout failure | Retry idempotent; lag SLO |
| Cross-region friend | Higher feed lag OK |
| Enumerate private post IDs | Uniform 404; no oracle |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 100M | 1B | cells | cells×geo |
| Posts / day | 200M | 2B | 20B | 200B |
| Peak post writes / s | 5K | 50K | 500K | 5M |
| Feed reads / day | 50B | 500B | 5T | 50T |
| Peak feed QPS | 1M | 10M | 100M | 1B |
| Avg graph degree | 300 | 300 | 300 | 300 |
| Max followers / friends | 50M pages | 100M+ | 200M+ | mega |
| Media objects / day | 150M | 1.5B | 15B | CDN-first |
| Notifications / day | 20B | 200B | 2T | aggregate-heavy |
| Peak notif emit / s | 200K | 2M | 20M | 200M |

**What each jump forces:**

- **10×:** Hybrid feed; Redis feed cache; Kafka; CDN media; notif aggregation; privacy-aware caches.  
- **100×:** Shard by user; multi-region; online-only fanout; notif cell isolation; media processing fleet.  
- **1,000×:** Geo/user cells; pull-first mega pages; cold media tier; aggressive aggregation; privacy policy engine.

### 1.5 Etc. (Constraints & Assumptions)

| Assumption | Choice |
|------------|--------|
| Graph | Directed follow MVP; friend-request optional module |
| Privacy | `public`, `followers/friends`, `only_me` |
| Feed ranking | Chrono + light score hook |
| Media | Images + short video ≤ 60–90s MVP |
| Notifications | In-app inbox + push high-level |
| IDs | Snowflake posts; opaque user ids |
| Comments | Separate service; eventual on feed snippet |
| Stories / Reels / Live | Hooks only |

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Examples | Notes |
|-------|----------|-------|
| Write | Post, like, comment, follow | Durable; amplify via fanout/notifs |
| Read ultra-hot | Home feed | Personalized; no public CDN |
| Read hot | Profile, post detail | ACL + cache carefully |
| Media | Bytes | CDN egress $$$ |
| Graph | Follow/friend | Adjacency scans for fanout |
| Notifications | Emit + read inbox | Extreme write amp; aggregate |

### 2.2 Storage math (baseline)

```text
Posts/day 200M × ~800 B meta ≈ 160 GB/day meta
Media: assume 70% posts have media, avg 200 KB stored variants after encode
  140M × 200 KB ≈ 28 PB/day raw theoretical → MUST use compression, size caps,
  lifespan, and CDN; interview: quote smaller avg (e.g. 50–100 KB) after variants policy
  Practical working set: object store + lifecycle cold/Glacier-like tiers

Feed entries naive: 200M × 300 degree = 60B/day inserts → impossible without hybrid/trim/active-only
Notifications naive: each like→notif explodes; aggregation mandatory
```

### 2.3 Fanout & privacy interaction

```text
Post privacy=friends, author degree=500 → ≤500 fanout targets
Post privacy=public, page followers=20M → celebrity hybrid, not 20M sync writes
Privacy change must invalidate authorization caches (short TTL + purge)
```

### 2.4 Notification amplification

```text
Viral post 10M likes:
  naive 10M push notifs → bad UX + cost
  aggregate: author gets rolling “X people liked your post”
  per-actor coalescing windows (e.g. 5 min)
```

### 2.5 Bandwidth & latency budgets

| Path | p99 target | Notes |
|------|------------|-------|
| Create post meta | 300 ms | media async |
| Feed page | 100–200 ms | cache IDs + hydrate |
| Media first byte | edge | CDN |
| Notif in-app | 1–5 s | async |
| Push | best effort | provider dependent |

### 2.6 Cache math

```text
feed:{user_id} → ID ZSET
post:{id} → body; TTL; NEVER put ACL-sensitive payload on shared public CDN without auth
viewer authz decisions cached briefly: authz:{viewer}:{post} carefully or recompute cheap
media URLs signed or CDN token for non-public
```

### 2.7 Scale jump worksheet

| Jump | Forced investment |
|------|-------------------|
| 10× | Hybrid feed, CDN, Kafka, notif aggregate, Redis |
| 100× | User shards, multi-region, media fleet, online fanout |
| 1,000× | Cells, pull-first mega, cold media, privacy engine |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Privacy is correctness** — leakage is a SEV, not a polish bug.  
2. **Publish fast; fanout async.**  
3. **Hybrid feed** for mega creators/pages.  
4. **Media via CDN**; origin protected.  
5. **Notifications aggregated**; never block like/comment path on push.  
6. **Cell-friendly** user ownership for blast radius.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Edge / API GW | Auth, RL, routing |
| User / Profile Service | Profiles, settings, privacy defaults |
| Graph Service | Follow/friend edges, blocks, celebrity flags |
| Post Service | CRUD posts, privacy field, tombstones |
| Media Service | Upload, process, virus scan, variants, URLs |
| Feed / Fanout Service | Hybrid timeline writes + read merge |
| Comment Service | Threaded comments light |
| Counter Service | Likes/comments counts |
| Notification Service | Inbox, aggregation, push publisher |
| AuthZ / Privacy module | Central checks for post visibility |
| Object Store + CDN | Media bytes |
| Event Bus | `post_created`, `edge_changed`, `engagement`, `privacy_changed` |
| Push providers | APNs/FCM high-level |

### 3.3 Graph model

**MVP directed follow (IG-like):**

- `following`, `followers` adjacency.  
- Private account → `follow_request` pending until approve.

**Optional FB friendship:**

- `friend_request` → accept → bi-di edge materialization.  
- Feed targets = friends set.

**Blocks:** deny edges; hide content; short-circuit notifs.

### 3.4 Privacy model (critical)

| Visibility | Who can read | Fanout targets |
|------------|--------------|----------------|
| `public` | Anyone | Followers / friends (hybrid if huge) |
| `followers` / `friends` | Accepted edges only | Those edges only |
| `only_me` | Author | None |

**Enforcement points (say all three):**

1. **Write/fanout:** only enqueue allowed targets.  
2. **Read/hydrate:** re-check ACL (race-safe against privacy changes).  
3. **Caches/CDN:** no cross-viewer shared cache of private bodies; signed URLs for media.

### 3.5 API sketch

```text
POST   /v1/posts
GET    /v1/posts/{id}
DELETE /v1/posts/{id}
PATCH  /v1/posts/{id}/privacy

POST   /v1/users/{id}/follow
POST   /v1/users/{id}/friend-request
POST   /v1/friend-requests/{id}/accept
DELETE /v1/users/{id}/follow
POST   /v1/users/{id}/block

GET    /v1/feed/home?cursor=
GET    /v1/feed/user/{id}?cursor=

POST   /v1/posts/{id}/likes
POST   /v1/posts/{id}/comments
GET    /v1/posts/{id}/comments?cursor=

GET    /v1/notifications?cursor=
POST   /v1/notifications/ack

POST   /v1/media/upload
```

### 3.6 Data model (core)

**Post:** `post_id`, `author_id`, `caption`, `media_ids[]`, `visibility`, `created_at`, `status`, counts…

**Edge:** `from_id`, `to_id`, `type` (follow/friend), `state` (active/pending), `created_at`

**Feed entry:** `viewer_id`, `post_id`, `author_id`, `ts`, `rank_hints`

**Notification:** `notif_id`, `user_id`, `type`, `actors[]` (aggregated), `object_id`, `ts`, `read`

### 3.7 Post + media flow

1. Client requests presigned upload; PUT bytes to object store.  
2. Media service processes (decode, variants, scan) → `media_ready`.  
3. Client `POST /posts` with `media_ids` + `visibility`.  
4. Post durable write; author index append; event `post_created`.  
5. ACK client.  
6. Fanout workers respect visibility + graph + celebrity.  
7. CDN serves variants; private media uses signed URLs / cookie tokens.

### 3.8 Feed strategy

**Hybrid** (same spirit as Twitter doc, privacy-aware):

- Normal authors: fanout-on-write to eligible viewers.  
- Mega pages / celebs: fanout-on-read merge of recent public posts.  
- Ranking hook: re-order page by lightweight score (affinity, recency, media type).

**Deal-breaker:** join entire friend graph × posts table per scroll.

### 3.9 Notifications (high-level)

```text
engagement event -> Notification Service
  -> aggregate by (user, type, object) in time window
  -> write inbox store
  -> optional push if high priority & user settings allow
Client polls or websocket/inbox sync for in-app
```

**Priorities:** friend accept / mention high; bulk likes low (aggregate).  
**Settings:** per-type mute; quiet hours.  
**Failure isolation:** notif outage must not fail likes.

### 3.10 Tradeoffs table

| Decision | Choice | Why |
|----------|--------|-----|
| Graph | Follow MVP + optional friends | Covers IG/FB |
| Feed | Hybrid | Celebs + cost |
| Privacy check | Fanout + read recheck | Race safety |
| Media | Async process | Publish snappy |
| Notifs | Aggregate async | Storm control |
| Ranker | Hook not platform | Scope |

### 3.11 Abuse controls

- Rate limits on post/follow/like/comment.  
- Fake engagement detection hooks.  
- Report → T&S.  
- New account friction.  
- Media malware scanning.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
 Clients -> Edge/API GW (auth, RL)
              |
    +---------+----------+--------------+--------------+
    v         v          v              v              v
 Profile   Graph      Post Svc      Feed Svc      Notif Svc
    |         |          |              |              |
    |         |          +-> Post Store |              +-> Inbox Store
    |         +-> Graph DB              +-> Feed Store |
    |                    |              ^              |
    |                    v              |              v
    |               Event Bus --------> Fanout         Push Pub
    |                    |                              |
    |                    +-----> Media Pipeline -> S3/Blob -> CDN
    |                    +-----> Comment Svc
    +--------------------+-----> AuthZ/Privacy module (library/service)
```

### 4.2 Publish sequence

```text
Client -> Media: upload
Media -> Blob: store; process async
Client -> Post: create(visibility)
Post -> Store: durable
Post -> Bus: post_created
Post -> Client: 201
Bus -> Fanout: ACL targets / celeb path
Bus -> Notif: optional (mentions)
```

### 4.3 Feed read sequence

```text
Client -> Feed: GET home
Feed -> Feed Store: ID page
Feed -> Graph: celeb followees
Feed -> merge pulls
Feed -> AuthZ: filter posts for viewer
Feed -> Post cache: hydrate
Feed -> Client: page
```

### 4.4 Notification sequence

```text
Like Svc -> Bus: liked(post, actor)
Notif: aggregate window
Notif: upsert inbox item actors[]
Notif: maybe enqueue push
Device <- APNs/FCM
```

### 4.5 Cells at 100×+

```text
Edge directory -> Cell by user_id / region
Each cell: post, feed, graph shard, notif inbox
Cross-cell edges: remote fanout topics
Media: global object store + regional CDN
Privacy: replicated policy bits with author region source of truth
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. ACK’d post durable; on author profile.  
2. Viewer never receives post body failing AuthZ.  
3. Fanout idempotent on `(viewer, post_id)`.  
4. Privacy tightening eventually hides from unauthorized (bounded).  
5. Notif loss OK more than post loss; likes don’t depend on push success.

#### 5.1.2 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Post store down | No publish | Multi-AZ; fail closed |
| Fanout lag | Stale feed | Lag SLO; expand pull |
| AuthZ bug | **Privacy SEV** | Mandatory tests; canaries; dual-check |
| Media processing down | Pending media | Placeholders |
| Notif store down | Missing badges | Retry; users still see content |
| CDN outage | Broken images | Multi-CDN optional; degrade |
| Graph down | Degraded social actions | Cached edges short TTL |

#### 5.1.3 Durability

- Posts/comments: quorum + backups.  
- Feed Redis rebuildable.  
- Media: erasure coding / multi-AZ bucket.  
- Notif inbox: best-effort durable; retention trim (30–90 days).

#### 5.1.4 Consistency

| Path | Model |
|------|-------|
| Author publish | Read-your-write |
| Friend feed | Eventual |
| Privacy change | Eventual hide + cache purge |
| Counts | Approx OK |
| Notifs | Eventual; aggregated |

#### 5.1.5 Security & privacy deep

- Uniform 404 for unauthorized post ids.  
- Signed media URLs with short TTL for non-public.  
- Feed caches **per viewer**, never global private.  
- Audit logs for privacy-sensitive admin access.  
- GDPR delete: async erase posts, media, edges, notifs.

### 5.2 Scalability

#### 5.2.1 Feed scaling

- Redis ZSET hot feeds; durable KV backup.  
- Hybrid celebs/pages.  
- Active-only push.  
- Trim feed length.  
- Ranking at read for page-local reorder only MVP.

#### 5.2.2 Media scaling

- Async worker fleets by format.  
- Adaptive bitrate variants limited set.  
- Lifecycle policies (hot → warm → cold).  
- Origin shield; image resizing at edge optional.  
- Cap upload size; virus scan queue priority.

#### 5.2.3 Graph scaling

- Shard adjacency by `user_id`.  
- Follower list chunked for fanout.  
- Counts via Redis counters.  
- Celebrity flag denormalized on profile.

#### 5.2.4 Notification scaling

- Aggregation keys reduce writes 10–1000× on viral.  
- Partition inbox by `user_id`.  
- Push via buffered publishers; backoff.  
- Prefer in-app inbox as source of truth.

#### 5.2.5 Multi-region & cells

- User home region.  
- Cross-region friends: async.  
- Mega pages: global recent cache.  
- Cells for blast radius at 1,000×.

#### 5.2.6 Cost controls

| Lever | Saves |
|-------|-------|
| Hybrid + trim | Feed storage |
| Media lifecycle | Object $ |
| Notif aggregate | Write + push $ |
| Active fanout | Wasted writes |
| Approx counts | Hot row contention |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Post + privacy field | Post team |
| AuthZ library | Privacy platform |
| Graph | Graph team |
| Feed/fanout | Feed team |
| Media | Media platform |
| Notifications | Notif team |
| T&S hooks | Trust |

#### 5.3.2 Safe evolution

- Additive privacy enums carefully (default-deny unknown).  
- Event schema compat.  
- Dark launch ranking hooks.  
- Privacy regression suite in CI.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Post p99 | < 300 ms |
| Feed p99 | < 200 ms |
| Unauthorized access rate | ~0 (alert on any) |
| Fanout lag | < 5–15 s |
| Notif inbox p99 write | < 1–2 s |
| Media ready p95 | < 10–30 s images |

#### 5.3.4 Progressive scale checklist

| Scale | Checklist |
|-------|-----------|
| 10× | Hybrid, CDN, Kafka, notif aggregate, privacy dual-check |
| 100× | Shards, multi-region, media fleet, online fanout |
| 1,000× | Cells, pull-first mega, cold media, privacy engine |

### 5.4 Deep dive: privacy change workflow

```text
PATCH visibility public -> friends
  1. Update post record (source of truth)
  2. Publish privacy_changed
  3. Purge CDN/signed URL capability if any
  4. Fanout scrub OR rely on read AuthZ (must)
  5. Short TTL on any authz caches
```

**Read path always AuthZ** — never trust feed store alone after privacy changes.

### 5.5 Deep dive: feed merge with ACL

```text
page = merge(pushed_ids, celeb_pulled_ids)
for post in hydrate(page):
  if not authz.allow(viewer, post): drop
return page
```

### 5.6 Deep dive: notification aggregation

```text
key = (recipient, type, object_id)
window = 5 minutes
on event: actors.add(actor); count++; refresh updated_at
render: "Alice and 99 others liked your photo"
push: at most once per window per key (or silent badge)
```

### 5.7 Deep dive: friend request state machine

```text
none -> requested -> (accept -> friends) | (reject -> none) | (cancel -> none)
block from any state -> blocked (terminal until unblock)
```

Materialize bi-di friend edges on accept for fast feed targeting.

### 5.8 Deep dive: media URL auth

- Public posts: CDN cacheable URLs (or still signed with long TTL).  
- Friends-only: short-lived signed URL minted after AuthZ.  
- Prevent hotlinking private media by token binding to viewer session optional.

### 5.9 Testing & resilience

- Property tests: random visibility × graph × viewer ⇒ authz oracle.  
- Load: celebrity page publish.  
- Chaos: kill fanout; verify AuthZ still holds on pull path.  
- Notif storm drills.

### 5.10 Amazon leadership connection

- **Customer Trust:** privacy bugs trump feature velocity.  
- **Ownership:** feed lag + media errors have runbooks.  
- **Frugality:** aggregation and hybrid beat infinite hardware.  
- **Dive Deep:** show AuthZ enforcement points on the diagram.

---

## 6. Wrap-Up

### 6.1 30-second recap

FB/IG-style social is **graph + post/media + hybrid feed + privacy dual-enforcement + aggregated notifications**. Publish ACK after durable post; fanout async to ACL-eligible viewers; celebrities/pages pull-merged; media on CDN with signed URLs for private; notifications never block engagement writes; scale shards → regions → cells.

### 6.2 Key tradeoffs

| Tradeoff | Pick |
|----------|------|
| Follow vs friends | Follow MVP; friends module optional |
| Push vs pull feed | Hybrid |
| Trust feed store vs AuthZ | Always recheck AuthZ |
| Exact notifs vs aggregate | Aggregate |
| Infinite media retention vs $ | Lifecycle tiers |

### 6.3 Risks & follow-ups

- AuthZ performance if naive per-post RPC — use library + cached graph bits.  
- Privacy change races with CDN.  
- Users following thousands of mega pages.  
- Notif inbox storage growth.  
- Cross-cell graph correctness.

### 6.4 What “good” looks like

- Privacy enforcement called out explicitly.  
- Hybrid feed math.  
- Media pipeline separated.  
- Notifications high-level with aggregation.  
- Scale path and ownership clear.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. Follow vs friendship — which MVP?  
2. Default post visibility?  
3. Are comments public if post is friends-only?  
4. Stories TTL design?  
5. Share to feed vs copy?  
6. Page vs user identity?  
7. Ranked feed requirements?  
8. Notification channel matrix?  
9. Ads injection?  
10. Multi-photo posts?  
11. Edit caption later?  
12. Save/bookmark?

### 7.2 Graph & privacy (Q13–Q28)

13. Enforce privacy at fanout only — why insufficient?  
14. Signed URL leakage via screenshot — product vs eng.  
15. Block semantics both directions.  
16. Private account approval queue scale.  
17. Mutual friends index.  
18. Graph partition strategy.  
19. Celebrity private account weirdness.  
20. Privacy change purge design.  
21. Uniform 404 rationale.  
22. Field-level privacy (phone/email).  
23. Minors / age-gated content hooks.  
24. Admin impersonation audit.  
25. GDPR delete ordering.  
26. Friend list visibility settings.  
27. Edge cache poisoning.  
28. Cross-region ACL source of truth.

### 7.3 Feed & media (Q29–Q44)

29. Hybrid threshold dials.  
30. Feed trim vs reconstruct.  
31. Ranking features offline vs online.  
32. Media virus scan blocking publish?  
33. Variant set selection.  
34. Thumbnail vs full res feed.  
35. Hot video post egress spike.  
36. Origin shield.  
37. Processing backlog UX.  
38. Idempotent upload.  
39. EXIF stripping / PII in photos.  
40. Multi-CDN failover.  
41. Comment snippet on feed card.  
42. Deleted media references.  
43. Live photo formats.  
44. Cost per DAU media.

### 7.4 Notifications (Q45–Q56)

45. Aggregation key design.  
46. Push vs in-app source of truth.  
47. Quiet hours.  
48. Unread badge correctness.  
49. Storm during viral celebrity post.  
50. Preference sync multi-device.  
51. Email digests Phase 1.5.  
52. Notif for private post engagement only to allowed.  
53. Dedup retries from bus.  
54. Retention & GDPR.  
55. Websocket fanout for inbox.  
56. Isolation from Like service failures.

### 7.5 Scale & ops (Q57–Q70)

57. 10× first bottleneck?  
58. Cell migration live users.  
59. Hot author partition.  
60. SLO dashboard.  
61. Chaos for privacy?  
62. Capacity worksheet.  
63. Multi-region active-active posts.  
64. Counter reconciliation.  
65. Search users index.  
66. Takedown SLA.  
67. Cost review narrative for VP.  
68. Schema evolution visibility enum.  
69. Blue/green feed workers.  
70. When pull-first default?

### 7.6 Behavioral / Amazon (Q71–Q76)

71. Privacy SEV story structure.  
72. Frugality: cut push volume.  
73. Disagree: PM wants public CDN for all images.  
74. Ownership of AuthZ library adoption.  
75. Dive deep: whiteboard friends-only + celebrity pull.  
76. Customer obsession: missing notif vs wrong notif.

---

## 8. Appendices

### Appendix A — Visibility × cache matrix

| visibility | Feed cache | CDN media | Notes |
|------------|------------|-----------|-------|
| public | per-viewer still for feed IDs | cacheable | body can be widely cached carefully |
| followers/friends | per-viewer only | signed URL | AuthZ on mint |
| only_me | author only | signed | no fanout |

### Appendix B — Example post record

```json
{
  "post_id": "P_987",
  "author_id": "U_42",
  "caption": "sunset",
  "media_ids": ["M_1"],
  "visibility": "friends",
  "created_at": 1754470000,
  "like_count": 20,
  "comment_count": 3,
  "status": "active"
}
```

### Appendix C — Feed Redis sketch

```text
feed:{user_id} ZSET score=ts member=post_id
celeb_recent:{author_id} ZSET
post:{id} JSON TTL
trim to ~1000–2000
```

### Appendix D — Notification types

| Type | Aggregate? | Push default |
|------|------------|--------------|
| follow / friend accept | no | yes |
| like | yes | soft/badge |
| comment | limited | yes |
| mention | no | yes |
| system | no | yes |

### Appendix E — Rate limits

| Action | New user | Normal |
|--------|----------|--------|
| Post | 20/day | 100/day |
| Follow | 50/day | 400/day |
| Like | 500/day | 5K/day |
| Comment | 50/day | 500/day |

### Appendix F — Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| Public CDN for friends-only originals | Privacy SEV |
| AuthZ only at fanout | Privacy change races |
| Sync push on every like | Melts |
| SQL join friends×posts | No scale |
| Global shared feed cache key | Wrong viewer leakage |
| Block post on notif failure | Poor isolation |

### Appendix G — Capacity worksheet

```text
DAU _____ posts/day _____ degree _____ → fanout inserts _____
media/day _____ × avgMB _____ = object growth _____
notif events _____ × aggregate factor _____ = inbox writes _____
feed QPS _____ × page bytes _____ = API egress _____
```

### Appendix H — 45-minute timebox

| Min | Focus |
|-----|-------|
| 0–5 | Graph, privacy, feed, media, notifs scope |
| 5–12 | Estimates + fanout/notif amp |
| 12–25 | HLD components + AuthZ points |
| 25–35 | Privacy change OR notif aggregate OR hybrid |
| 35–42 | Scale + cost + failures |
| 42–45 | Wrap-up |

### Appendix I — Glossary

| Term | Meaning |
|------|---------|
| AuthZ | Authorization check for visibility |
| Hybrid fanout | Push normal + pull mega |
| Signed URL | Time-bound media capability |
| Aggregation | Collapse many actors into one notif |
| Tombstone | Soft delete marker |
| Private account | Follow requires approval |

### Appendix J — Sample feed response

```json
{
  "items": [
    {
      "post_id": "P_987",
      "author_id": "U_42",
      "caption": "sunset",
      "media": [{"url": "https://cdn/.../thumb.jpg"}],
      "like_count": 20,
      "visibility": "friends"
    }
  ],
  "next_cursor": "…"
}
```

### Appendix K — Ownership RACI

| Activity | Post | Graph | Feed | Media | Notif | Privacy |
|----------|------|-------|------|-------|-------|---------|
| Visibility enum change | A | C | C | C | C | A |
| Celebrity threshold | C | C | A | I | I | C |
| Signed URL policy | C | I | C | A | I | A |
| Aggregate window | I | I | I | I | A | C |
| Takedown | C | I | C | C | C | A |

### Appendix L — Progressive scale one-pager

| Scale | Bottleneck | Investment |
|-------|------------|------------|
| 10× | Feed writes + media egress | Hybrid, CDN, Kafka, aggregate |
| 100× | Shards + processing fleet | User shards, regions, online fanout |
| 1,000× | Cells + privacy+mega | Cells, pull-first, cold tier |

### Appendix M — Comparison

| Topic | This design |
|-------|-------------|
| vs Twitter/X | Stronger privacy; heavier media; notifs more central |
| vs pure IG | Optional friendship module |
| vs Messenger | No E2EE DMs MVP |
| vs TikTok FYP | Not interest-graph first |

### Appendix N — Threat model

| Asset | Threat | Control |
|-------|--------|---------|
| Private posts | Unauthorized read | Dual AuthZ, signed media, uniform 404 |
| Attention | Fake engagement | RL, anomaly, T&S |
| $ | Media/fanout abuse | Quotas, hybrid, lifecycle |
| Users | Harassment | Block/mute/report |

### Appendix O — AuthZ pseudocode

```text
function allow(viewer, post):
  if post.status != active: return false
  if viewer == post.author_id: return true
  if blocked(viewer, post.author_id): return false
  switch post.visibility:
    case public: return true
    case followers:
      return graph.active_follow(viewer, post.author_id)
    case friends:
      return graph.friends(viewer, post.author_id)
    case only_me: return false
```

### Appendix P — Event sketches

```json
{"type":"post_created","post_id":"P","author_id":"U","visibility":"friends","ts":0}
{"type":"privacy_changed","post_id":"P","from":"public","to":"friends","ts":0}
{"type":"engagement","kind":"like","post_id":"P","actor":"U2","ts":0}
```

### Appendix Q — Friend request pseudocode

```text
function accept(request):
  assert request.state == pending
  write_edge(a,b,friend,active); write_edge(b,a,friend,active)
  delete pending; emit edge_changed
```

---

*End of Amazon SDE III prep doc — Social Network (Facebook / Instagram-style) System Design.*
