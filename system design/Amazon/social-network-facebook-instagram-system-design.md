# System Design: Social Network (Facebook / Instagram Style)

> **Focus areas:** Bilateral friendship · Social graph · News Feed ranking candidates · Stories/ephemeral · Photos/albums · Groups/pages · Privacy ACL · Notifications · Cells
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Privacy ACL correctness; feed candidate retrieval economics; media-heavy cost; distinguish from Twitter directed-follow
> **Interview theme:** Amazon SDE III / L6 — **Facebook/Instagram-style** social network with Amazon operational bar

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

Goal: design a **Facebook/Instagram-style** social network: profiles, bilateral friendships (FB) and/or follow graph (IG), posts with rich media, News Feed / Home, Stories, groups/pages (optional), privacy controls, notifications, and search—at progressive global scale.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Social graph + feed + media social product | Twitter-only microblog (see twitter-x doc) |
| Graph | FB: mutual friends; IG: directed follow—**pick in interview** | Chat/messenger primary |
| Feed | Ranked News Feed candidates + ranking hooks | Pure ads exchange |
| Amazon lens | Privacy, abuse, cost, cells, ownership | Academic social-graph theory only |

**Interview lock:** State whether MVP is **FB-like mutual + privacy** or **IG-like follow + public/creator**. This doc covers both with explicit branches.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Graph type? | Mutual friends (FB) and/or follow (IG) | Edge semantics + feed retrieval |
| F2 | Posts? | Text/photo/video/carousel; captions | Media pipeline central |
| F3 | Feed? | Ranked home; chrono fallback | Candidate generation + ranker |
| F4 | Stories? | 24h ephemeral | TTL, separate store, privacy |
| F5 | Profiles? | Bio, avatar, grids | Profile service + CDN |
| F6 | Groups/pages? | Optional Phase 1.5 | Separate membership ACL |
| F7 | Privacy? | Friends / friends-of-friends / public / custom | ACL on every read |
| F8 | Reactions/comments? | Reactions, threaded comments | Engagement store |
| F9 | Notifs? | Friend req, tags, comments, likes (coalesced) | Notif service |
| F10 | Search? | People, hashtags, places | Index + privacy filter |
| F11 | Messaging? | Optional separate system | Out of MVP unless asked |
| F12 | Abuse? | Report, block, restrict, underage | Mandatory |

**MVP scope:**

1. Auth + profiles.
2. Friend request accept **or** follow/unfollow (choose).
3. Create posts with photos; album/grid.
4. Home feed: candidate retrieve + simple rank (affinity+recency).
5. Stories with 24h TTL.
6. Like/comment; coalesced notifs.
7. Privacy ACL for FB-like; public/private account for IG-like.
8. Block/report + rate limits.

**Out of MVP:** full Reels/ForYou deep retrieval science, Marketplace, dating, complete ads auction, VR.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Post create ACK | p99 < 500ms metadata; media async |
| N2 | Feed p99 | < 300–500ms |
| N3 | Privacy correctness | Zero tolerance intentional leaks |
| N4 | Story expiry | Visible ≤ TTL + small bound; GC eventually |
| N5 | Availability | Feed read high; degrade ranker → chrono |
| N6 | Media durability | Object store class; processing pipelines |
| N7 | Notification lag | Seconds typical; coalesce storms |
| N8 | Scale | 100M–1B users class progressive |

### 1.3 Cases

**Happy:** friend/follow → post photo → friends see in feed → react/comment → notif.

**Edges:** viral photo; celebrity IG; custom privacy lists; story after expiry; tag non-friend; underage; revenge porn report; feed stampede after celebrity; multi-device; unfriend mid-fanout; FOAF privacy; CDN delete.

| Case | Behavior |
|------|----------|
| Unfriend | Remove edge; feed/authz must not show friends-only posts |
| Custom list privacy | ACL evaluation on read; careful caching keyed by audience |
| Story expiry | Fail closed after TTL; CDN short TTL + purge |
| Private IG account | Only approved followers |
| Hot creator | Hybrid fan-out / pull like Twitter celeb patterns |
| Comment spam on viral | Rate limits; ranking demotion; collapse |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| MAU | 20M | 200M | 2B | — |
| DAU | 8M | 80M | 800M | — |
| Posts/day | 30M | 300M | 3B | — |
| Photos/day | 20M | 200M | 2B | — |
| Peak feed QPS | 50K | 500K | 5M | — |
| Avg friends/follows | 300 | 300 | 400 | — |
| Stories created/day | 10M | 100M | 1B | — |
| Notifs/day | 200M | 2B | 20B | — |

**Jumps:** 10× media CDN + async processing; 100× feed candidate infra + cells + hybrid; 1,000× extreme retrieval/ranking isolation + multi-region privacy caches.

### 1.5 Scope repeat-back

> FB/IG-style social: graph (mutual or follow), media posts + stories, privacy ACL, feed candidate+rank with degrade-to-chrono, engagements/notifs, abuse—scaled with hybrid fan-out economics and cells at Amazon bar.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Feed read dominance

```text
DAU 8M; sessions with multiple feed refreshes
Peak feed QPS can be tens of thousands baseline → millions at 100×
```

### 2.2 Candidate generation math

```text
Naive: for each viewer, pull last K posts from each friend (300 × K)
= huge fan-in at read time

Mitigations:
- Write-fanout inbox of candidate post IDs (FB classic)
- Hybrid for celebrities/creators
- Limit leaf retrieval; use ranking to prune
```

### 2.3 Media storage

```text
20M photos/day × 200KB avg processed ≈ 4 TB/day raw-ish
Multiple renditions (thumb, feed, full) multiply
Lifecycle + CDN caching essential
```

### 2.4 Story TTL storage

```text
Stories hot for 24h; aggressive expiry reduces long-term cost
Still need takedown/audit paths
```

### 2.5 Privacy cache danger

```text
Caching feed responses without audience keys → leak after unfriend
Cache keys must include ACL version / friendship version
```

### 2.6 Bottlenecks

(1) Media processing (2) feed inbox amp (3) privacy-eval CPU (4) viral post comments (5) notif storms (6) graph hot partitions.

### 2.7 Cost

Egress + encode + inbox writes. Stories TTL and rendition ladders are frugality features.

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Identity/Profile | Users, profiles | Strong per user |
| Graph | Friends/follows, blocks | Strong edge mutations |
| Post/Media | Content + objects | Strong post meta; media immutable |
| Feed | Inboxes/candidates + rank | Eventual candidates |
| Stories | Ephemeral posts | TTL-bound visibility |
| Engagement | Reactions/comments | Eventual counts |
| Privacy/ACL | Audience evaluation | Correctness > cache |
| Notifs/Search/Abuse | Adjacent | Nearline OK |

**Deal-breaker:** caching public feed HTML for friends-only content.

### 3.2 Components

1. API Edge + auth/session  
2. Profile Service  
3. Graph Service (friend requests / follows)  
4. Post Service  
5. Media Processing (upload, encode, scan)  
6. Feed Mixer / Candidate Service  
7. Ranker (features + model hooks)  
8. Stories Service  
9. Engagement Service  
10. Notification Service  
11. Privacy/ACL library (side-car or lib)  
12. Search Indexer  
13. Abuse/Takedown  
14. Cell Directory  

### 3.3 APIs (sketch)

```text
POST /v1/friends/request | POST /v1/friends/accept
POST /v1/follow/{user_id}
POST /v1/posts  {text, media[], audience}
GET  /v1/feed/home?cursor=
POST /v1/stories {media, audience}
GET  /v1/stories/tray
POST /v1/posts/{id}/comments
POST /v1/posts/{id}/reactions
```

### 3.4 Privacy model (FB-like)

```text
audience ∈ {public, friends, friends_except, only_me, custom_list, foaf?}
Evaluate viewer ∈ audience using graph snapshot version
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Mutual vs follow | Lock early | Changes ACL + product |
| Feed | Inbox candidates + rank | Classic scale path |
| Stories store | Separate TTL tables | Cheaper GC |
| Comments | Sharded by post_id | Viral isolation |
| Ranker | Optional features | Degrade to chrono |
| Cache | ACL-versioned | Prevent leaks |

---

## 4. Architecture Diagram

```text
Client → Edge → Post/Story/Graph/Profile APIs
                 |        |         |
                 v        v         v
            Post Store  Media    Graph Store
                 |      Store       |
                 +--------+---------+
                          v
                     Outbox/Kafka
                          |
          +---------------+----------------+
          v               v                v
     Feed Fan-out    Media Workers     Notif/Search
          v               v
     Feed Inbox      Renditions/CDN
          ^
          |
     Feed Mixer → Ranker → ACL filter → Client
```

### 4.1 Publish photo post

```text
1. Presign media upload; client uploads
2. Create post meta (audience, author)
3. Process renditions + scan async
4. When ready, mark ACTIVE; fan-out candidates to friends/followers (hybrid if celeb)
5. Notifs for tags
```

### 4.2 Feed read

```text
1. Load candidate inbox page
2. Fetch post metas + media pointers
3. Rank (or chrono)
4. ACL check (must)
5. Return
```

### 4.3 Unfriend sequence

```text
Delete edge → bump relationship version → invalidate ACL caches →
optional inbox scrub → future fan-out skips
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Friends-only content never served to non-friends (probe-tested).  
2. ACK post meta durable; media becomes visible per policy after scan.  
3. Story not viewable after TTL (+ bounded clock skew policy).  
4. Unfriend/block takes effect within privacy SLO.  
5. Idempotent creates and reactions.  
6. Ranker failure ⇒ chrono candidates still ACL-filtered.  
7. Takedown removes CDN + feed visibility.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Monolith; PG; Redis feed; local disk-ish media bad—use S3 even early |
| 10× | Kafka fan-out; media fleet; CDN |
| 100× | Hybrid creators; cells; comment shards; ranker fleet |
| 1000× | Multi-region; retrieval/ranking split; cold media tiers |

### 5.3 Maintainability

- Privacy policy as data + library versioning  
- Feed mixer canaries  
- Model/feature flags for ranker  
- Rebuild inboxes from graph+posts for active users  
- Chaos: claim ACL leak tests continuously  

### 5.4 Progressive scale

**1×:** write-fanout all friends; simple affinity rank.  
**10×:** media at scale; async; CDN.  
**100×:** celebrity/creator hybrid; cells; notif coalesce.  
**1000×:** specialized retrieval; regionalization; extreme viral comment isolation.

### 5.5 Feed ranking (interview-right-sized)

Candidate set from inbox/pull → features (affinity, recency, media type, completion preds) → score → diversity rules → safety filters → ACL. Keep **ACL after rank** too (defense in depth).

### 5.6 Stories deep dive

- Separate `stories` table with `expires_at`  
- Tray API aggregates active stories from friends  
- Views optional privacy-sensitive  
- GC sweeper + CDN short max-age  

### 5.7 Comments on viral posts

- Shard by `post_id`  
- Nested threads limited depth  
- Rate limits per user/post  
- Don’t live-push every comment to all viewers—refresh/paginate  

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Cache feed without ACL version | Privacy SEV |
| Ranker required for feed availability | Outage when model dies |
| Full fan-out to 100M followers | Cost death |
| Stories without TTL enforcement | Trust/product break |
| Search index as authz | Leaks via search |

---

## 6. Wrap-Up

### 6.1 Designed

Graph + posts/media + stories + privacy ACL + feed candidates/rank + engagements/notifs + abuse—hybrid economics, cells, Amazon ownership.

### 6.2 Decisions to defend

1. Lock mutual vs follow early  
2. ACL on every read + versioned caches  
3. Inbox candidates + hybrid creators  
4. Ranker optional with chrono degrade  
5. Stories separate TTL plane  
6. Viral comment sharding  
7. Media scan before wide distribution  
8. Cells for blast radius  

### 6.3 Risks

Privacy regressions; media cost; ranker complexity; fan-out lag; underage safety.

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | FB vs IG scope lock |
| 5–15 | Graph + privacy |
| 15–28 | Feed fan-out + rank degrade |
| 28–38 | Media/stories/comments |
| 38–45 | Scale, SEVs, ownership |

### 6.5 Closer

> **FB/IG social**: privacy-correct graph+ACL, media-first posts/stories, hybrid feed economics, optional ranker with chrono fallback, cells, abuse, progressive scale.

---

## 7. Deeper / Related Interview Questions

### 7.1 Graph

**Q: Friend request spam?**  
A: Rate limits, mutual graph signals, captcha/phone for new accounts.

**Q: FOAF privacy cost?**  
A: Expensive—often avoid or precompute carefully; many products dropped FOAF.

### 7.2 Privacy

**Q: Cache invalidation on unfriend?**  
A: Relationship version token in cache key; short TTL; active purge for hot keys.

**Q: Tag approval?**  
A: Pending tag state; appears after approve per settings.

### 7.3 Feed

**Q: Why not pure pull?**  
A: High-degree viewers + many friends → heavy merges; inbox helps—but celebs need hybrid.

**Q: How many candidates?**  
A: Hundreds then rank to tens; measure.

### 7.4 Media

**Q: Multiple renditions?**  
A: Async encoders; serve size-appropriate; AV1/HEVC ladder over time.

**Q: Nude/CSAM scanning?**  
A: Mandatory pipelines; fail-closed for distribution; legal workflows.

### 7.5 Stories vs posts

**Q: Same store?**  
A: Prefer separate for TTL/GC and product semantics.

### 7.6 Interview traps

**Q: Global feed table scanned per request?**  
A: No.  
**Q: Perfect ML rank before ACL?**  
A: Wrong priority.  
**Q: Messenger embedded in same write path?**  
A: Separate system.

### 7.7 Metrics

| Metric | Why |
|--------|-----|
| feed_p99 | UX |
| acl_probe_failures | Trust |
| fanout_lag | Freshness |
| media_process_lag | Time-to-visible |
| story_expire_violations | Product/trust |
| comment_write_p99_viral | Isolation |
| notif_coalesce_rate | Cost/UX |
| egress_$ | Frugality |

### 7.8 Ownership

Privacy leak → Graph/ACL + Feed joint SEV IC. Media malware → Media+Trust. Ranker bad CTR → Feed Science but Serving owns safety/latency gates.

### 7.9 Progressive drill

10× media; 100× hybrid+cells; 1000× retrieval/rank isolation.

### 7.10 Groups (if asked)

Membership ACL separate; feed fan-out to members with hybrid for huge groups; moderation queue.

---

## 8. Appendices

### 8.1 Schema sketches

```text
users(user_id, ...)
profiles(user_id, bio, avatar_id, privacy_default)
friend_edges(user_a, user_b, state, version)  -- canonical ordered pair
follow_edges(follower, followee, state)
posts(post_id, author_id, audience, media_refs, created_at, state)
stories(story_id, author_id, audience, media_refs, created_at, expires_at)
feed_inbox(user_id, post_id, ts, author_id)
comments(comment_id, post_id, author_id, text, parent_id, ts)
reactions(post_id, user_id, type, ts)
acl_lists(list_id, owner_id, member_ids)
blocks(blocker, blocked)
```

### 8.2 API checklist

- [ ] Friend/follow APIs  
- [ ] Post create with audience  
- [ ] Feed home  
- [ ] Stories tray/view  
- [ ] Comments/reactions  
- [ ] Block/report  
- [ ] Media upload  
- [ ] Privacy settings  

### 8.3 Oncall checklist

- [ ] ACL probe suite green  
- [ ] Fan-out lag  
- [ ] Media backlog  
- [ ] Story GC lag  
- [ ] Viral comment shard hot  
- [ ] Ranker error rate / fallback  
- [ ] CDN purge  
- [ ] Cell health  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Mutual friend | Bilateral edge |
| Audience | Privacy set for content |
| Feed inbox | Materialized candidate IDs |
| Tray | Active stories list |
| Rendition | Encoded media variant |
| ACL version | Graph/privacy epoch for caches |

### 8.5 Deal-breaker one-liners

- Feed cache ignoring unfriend  
- Ranker hard-dependency  
- Celeb full inbox write  
- Search bypassing ACL  

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Graph/ACL | Social Graph |
| Feed mixer | Feed Serving |
| Ranker | Feed Science + Serving gates |
| Media | Media Platform |
| Stories | Stories |
| Trust | T&S |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | Modular monolith + S3 + Redis inbox |
| 10× | Kafka + media fleet + CDN |
| 100× | Cells + hybrid + ranker |
| 1000× | Multi-region + cold tiers |

### 8.8 Failure injection

1. Ranker down → chrono.  
2. Unfriend → probe other user cannot read.  
3. Media scanner down → hold distribution.  
4. Fan-out lag → stale but correct ACL.  
5. Story clock skew → expire early prefer leak-late? Prefer fail-closed after TTL.

### 8.9 Cache key sketch

```text
feed:v{acl_ver}:user:{id}:cursor:{c}
```

### 8.10 Feature flags

Ranker on/off; stories; FOAF; groups; new media codecs.

### 8.11 Interview closer checklist

- [ ] Graph model locked  
- [ ] ACL story  
- [ ] Hybrid feed math  
- [ ] Media pipeline  
- [ ] Stories TTL  
- [ ] Degrade ranker  
- [ ] Cells  
- [ ] Ownership  

### 8.12 Related

Messenger, ads, shopping tags, Reels retrieval, people-you-may-know (see find-friends doc).

### 8.13 Sample events

```text
FRIEND_ACCEPTED, POST_ACTIVATED, FEED_FANOUT, STORY_CREATED,
STORY_EXPIRED, REACTION_ADDED, COMMENT_ADDED, UNFRIENDED, TAKEDOWN
```

### 8.14 Underage / safety

Age gates; default stricter privacy; sensitive content classifiers; human review SLA.

### 8.15 Multi-region

User home cell; media global via CDN; privacy eval local with graph replicas (lag bounds).

### 8.16 Security

Session theft, CSRF, XSS captions, exif GPS stripping, admin audit for takedowns.

### 8.17 Cost narrative

Renditions×egress + inbox amp. TTL stories and hybrid creators save real $.

### 8.18 LP hooks

Customer Obsession = privacy; Dive Deep = ACL cache bug; Frugality = media ladders; Ownership = leak SEV.

### 8.19 QoS degrade order

1. Extra notifs  
2. Ranker → chrono  
3. Stretch fan-out lag  
4. Reduce rendition quality  
5. Preserve ACL + block + takedown  

### 8.20 PYMK hook

People You May Know is adjacent (find-friends service); feed should not embed heavy PYMK compute on critical path.

---

## Deep Technical Notes — FB/IG Social

### Canonical friend edge

Store ordered `(min_id, max_id)` plus state to avoid duplicates; version++ on change.

### Audience evaluation

Lib evaluated in Feed and Post-get paths; never only at write.

### Inbox scrub

Lazy filter on read + async scrubber after unfriend; both needed.

### Encoder backpressure

If encode backlog huge, delay ACTIVE visibility; show processing state.

### Comment pagination

Keyset on `(post_id, ts, comment_id)`; cache hot top-level page briefly with invalidation on new comment optional.

### Shadow copy for legal

Takedown may retain restricted legal hold copies separate from public serving path.

---

## Worked Capacity Narrative — FB/IG Social

Media bytes dwarf post metadata. Feed QPS dwarfs post QPS. Privacy bugs dwarf latency bugs in severity. Optimize interview narrative in that order: ACL → fan-out economics → media → ranker.

## Customer-Trust Paragraph — FB/IG Social

A single friends-only photo shown to the wrong viewer is a company-level trust event. Design caches and search with fear. Expiry for stories and deletes must be real, not best-effort UI hiding.

## Progressive Scale Recap — FB/IG Social

- **10×:** CDN + media workers + async fan-out  
- **100×:** hybrid creators + cells + ranker fleet  
- **1,000×:** multi-region + retrieval split + cold media  

## Supplemental Depth Pack — FB/IG Social

### S1. Privacy ACL

Audience evaluation on every read; ACL/relationship version in caches.
**Invariant:** Unfriend ⇒ non-access within privacy SLO.
**Metric:** acl_probe_fail=0.
**Ownership:** Graph + Feed.

### S2. Feed inbox + hybrid

Write-fanout candidates; pull for celebrities/creators.
**Invariant:** No O(100M) sync writes.
**Metric:** inbox_write_amp, fanout_lag.
**Ownership:** Feed.

### S3. Ranker degrade

Features+model optional; chrono fallback ACL-safe.
**Invariant:** Ranker outage ≠ blank feed.
**Metric:** fallback_rate.
**Ownership:** Feed Serving.

### S4. Media processing

Presign, scan, renditions, CDN.
**Invariant:** Unsafe media not broadly distributed when fail-closed.
**Metric:** scan_lag, block_rate.
**Ownership:** Media.

### S5. Stories TTL

Separate plane; expire fail-closed; short CDN TTL.
**Invariant:** Post-TTL visibility ≈ 0.
**Metric:** expire_violations.
**Ownership:** Stories.

### S6. Viral comments

Shard by post; rate limit; paginate; avoid global push.
**Invariant:** One viral post cannot melt whole comment cluster.
**Metric:** comment_p99_hot.
**Ownership:** Engagement.

### S7. Notifications coalesce

Aggregate likes/reactions; respect mute/block silently.
**Invariant:** Blocked user cannot notify.
**Metric:** notif_send_qps, suppress_rate.
**Ownership:** Notifications.

### S8. Cells

User-home cells; async cross-cell; blast radius.
**Invariant:** Cell death ≠ global social outage.
**Metric:** cell_availability.
**Ownership:** Platform + product surfaces.

## Scenario Runbooks — FB/IG Social

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|-----------|
| ACL probe fail | Disable bad cache layer; SEV | Trust | Patch + tests |
| Ranker bad | Force chrono | Ranking quality ↓ | Rollback model |
| Media backlog | Scale encoders; gate ACTIVE | Slow visibility | Capacity |
| Story visible late | Purge CDN; fix TTL | Trust | Clock/TTL audit |
| Fan-out lag | Scale workers | Stale feed | Hot keys |
| Comment melt | Isolate shard; rate limit | Partial UX | Reshard |
| Unfriend lag | Purge ACL caches | Privacy | SLO tighten |
| Search leak | Filter/remove docs | Trust | Authz in search |

## Rapid-Fire Q&A — FB/IG Social

**RQ1. Why ACL on read?**  
**A:** Write-time audience can change (unfriend); read is source of enforcement.

**RQ2. Test ACL?**  
**A:** Continuous sealed probes + canary users.

**RQ3. 100× ignore ACL caching rules?**  
**A:** Privacy SEVs explode with cache hit rate.

**RQ4. Why hybrid feed?**  
**A:** Creator degree breaks pure write-fanout.

**RQ5. Test hybrid?**  
**A:** Synthetic mega-creators; amp dashboards.

**RQ6. Regression?**  
**A:** Cost/latency catastrophe or dropped distribution.

**RQ7. Why chrono fallback?**  
**A:** Availability over perfect ranking.

**RQ8. Test fallback?**  
**A:** Kill ranker in staging; measure feed success.

**RQ9. Regression?**  
**A:** Hard outage coupled to model.

**RQ10. Why separate stories?**  
**A:** TTL/GC and product semantics differ.

**RQ11. Test stories expiry?**  
**A:** Time fixtures; CDN purge checks.

**RQ12. Regression?**  
**A:** Expired content lingering / trust.

**RQ13. Why shard comments by post?**  
**A:** Viral isolation.

**RQ14. Test comments?**  
**A:** Hot-key load tests.

**RQ15. Regression?**  
**A:** Cluster-wide melt.

**RQ16. Why media scan async?**  
**A:** Protect upload UX; gate distribution.

**RQ17. Test media?**  
**A:** Malicious fixtures; fail-closed.

**RQ18. Regression?**  
**A:** Safety incidents.

**RQ19. Why coalesce notifs?**  
**A:** Storm control for viral posts.

**RQ20. Test notifs?**  
**A:** Reaction floods; collapse correctness.

**RQ21. Regression?**  
**A:** Push provider pain + user spam.

**RQ22. Why cells?**  
**A:** Blast radius / scale independence.

**RQ23. Test cells?**  
**A:** Game day kill cell.

**RQ24. Regression?**  
**A:** Global brownouts.

## Narrative Walkthrough — FB/IG Social

### Beat 1
Friend accept / follow → graph edge + version++. Tradeoff: mutual vs directed.

### Beat 2
Photo post → media upload → process → ACTIVE → fan-out. Tradeoff: visibility vs scan completeness.

### Beat 3
Feed read → inbox + rank + ACL. Tradeoff: ranking lift vs complexity/availability.

### Beat 4
Unfriend → version++ → cache purge → authz deny. Tradeoff: eager scrub cost vs lazy filter.

### Beat 5
Story create → 24h TTL → tray → expire. Tradeoff: CDN cache vs expiry tightness.

### Beat 6
Viral comments → sharded write → paginated read. Tradeoff: realtime push vs cost.

### Beat 7
10× media; 100× hybrid/cells; 1000× multi-region. Tradeoff: each jump.

### Beat 8
Deal-breakers: ACL-blind cache; celeb full fan-out; ranker hard-dep. Economics: egress+amp.

## Pre-Onsite Checklist — FB/IG Social

- [ ] Mutual vs follow locked
- [ ] ACL versioning story
- [ ] Hybrid feed math
- [ ] Media scan/renditions
- [ ] Stories TTL
- [ ] Ranker degrade
- [ ] Comment hot keys
- [ ] Cells
- [ ] Runbooks rehearsed
- [ ] SDM trust-first pitch
- [ ] Metrics + owners
- [ ] Progressive scale what-breaks
- [ ] PYMK not on critical path
- [ ] Search authz
- [ ] Kill switches named

### Extra drill

Explain a privacy SEV from bad feed caching in 90 seconds with root cause, blast radius, fix, and tests.

### Extra drill

Compare this design to Twitter/X in 60 seconds: graph semantics + privacy + media weight.

---

*End of document — Social Network Facebook/Instagram (Amazon Interview Style) (SDE III)*

## Extra Interview Drills — FB/IG Social

### Extra Interview Drills — FB/IG Social — item 1

**Prompt:** In 60 seconds, explain failure mode #1 and the degrade/kill-switch story.

**Strong answer shape:**
- Name the plane (graph, feed, media, cache, CDN, abuse, search).
- State invariant that must not break.
- Give metric + owner + progressive-scale jump.

**Trap:** Scaling only stateless app tiers for theme 1 while the data model stays naive.


### Extra Interview Drills — FB/IG Social — item 2

**Prompt:** In 60 seconds, explain failure mode #2 and the degrade/kill-switch story.

**Strong answer shape:**
- Name the plane (graph, feed, media, cache, CDN, abuse, search).
- State invariant that must not break.
- Give metric + owner + progressive-scale jump.

**Trap:** Scaling only stateless app tiers for theme 2 while the data model stays naive.


### Extra Interview Drills — FB/IG Social — item 3

**Prompt:** In 60 seconds, explain failure mode #3 and the degrade/kill-switch story.

**Strong answer shape:**
- Name the plane (graph, feed, media, cache, CDN, abuse, search).
- State invariant that must not break.
- Give metric + owner + progressive-scale jump.

**Trap:** Scaling only stateless app tiers for theme 3 while the data model stays naive.


### Extra Interview Drills — FB/IG Social — item 4

**Prompt:** In 60 seconds, explain failure mode #4 and the degrade/kill-switch story.

**Strong answer shape:**
- Name the plane (graph, feed, media, cache, CDN, abuse, search).
- State invariant that must not break.
- Give metric + owner + progressive-scale jump.

**Trap:** Scaling only stateless app tiers for theme 4 while the data model stays naive.

