# System Design: Twitter / X (Amazon Interview Style)

> **Focus areas:** Post/timeline · Hybrid fan-out · Celebrity hot keys · Mentions · Search · Media CDN · Rate limits · Abuse · Cells · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct fan-out math; no naive full write-fanout for mega-celebrities; home timeline freshness vs cost explicit
> **Interview theme:** Amazon SDE III / L6 — consumer social **Twitter/X-like** feed at Amazon operational bar (ownership, abuse, cost, cells)

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

Goal: design a **Twitter/X-like** microblogging system: short posts, follow graph, home timeline, user profile timeline, likes/reposts, mentions/notifications, media, search, and abuse controls—scaled from startup through global celebrity load.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Public microblog + timelines + social graph | Private messenger (see chat designs) |
| Graph | Directed **follow** (not mutual friends) | Facebook-style bilateral friendship |
| Feed | Home timeline + user timeline + search/explore | Full FB News Feed ranking science thesis |
| Amazon lens | Ownership, cells, abuse, unit cost, degrade modes | Toy Redis-demo only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Post model? | Short text (+ media pointers), optional reply/quote/repost | Post store + engagement edges |
| F2 | Graph? | Directed follow/unfollow | Graph service; asymmetric fan-out |
| F3 | Home timeline? | Reverse-chrono MVP; ranked Phase 1.5 | Fan-out vs pull hybrid |
| F4 | User timeline? | Author's posts/replies policy | Per-author log |
| F5 | Engagements? | Like, repost, reply, quote, bookmark | Counters + edges; async |
| F6 | Mentions/notifs? | @mentions, follows, likes (sampled) | Notification service |
| F7 | Media? | Images/video/GIF via object store + CDN | Upload pipeline + scan |
| F8 | Search? | Recent + top; hashtags; people | Index pipeline separate |
| F9 | Trends? | Regional trending topics | Aggregations, abuse-resistant |
| F10 | DMs? | Optional Phase 2 | Out of MVP unless asked |
| F11 | Privacy? | Public default; protected accounts | Authz on timeline/fan-out |
| F12 | Abuse? | Rate limits, blocks, mutes, reports, spam | Mandatory at scale |

**MVP scope:**

1. Auth users; create/delete posts; media pointers.
2. Follow/unfollow; protected-account rules.
3. Home timeline (hybrid fan-out) + user timeline.
4. Like/repost/reply basics; counters eventually consistent OK if labeled.
5. Mentions → notifications; push optional.
6. Hashtag/recent search Phase 1; ranked search Phase 1.5.
7. Rate limits + block/mute + report pipeline.
8. Basic trends with anti-gaming.

**Out of MVP:** full Spaces/live audio, ads auction deep dive, perfect global ranking personalization, E2EE DMs, blockchain nonsense.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Post publish latency | p99 < 300–500ms to durable ACK |
| N2 | Home TL freshness | Celebrity exceptions documented; typical < few seconds |
| N3 | Read p99 home TL | < 200–400ms cached path |
| N4 | Availability | Read 99.99% class with degrade; write 99.9%+ |
| N5 | Consistency | Per-author post order strong; home TL eventual OK |
| N6 | Durability | ACK'd posts not lost |
| N7 | Abuse latency | Hard blocks immediate; ML spam async with kill switches |
| N8 | Cost | Fan-out amp bounded; media egress controlled |

### 1.3 Cases

**Happy:** post → fan-out to follower inboxes / pull for celebs → home TL read → like/notif.

**Edges:** celebrity 100M followers; protected account leak; delete race with CDN; bot follow farms; hashtag brigading; hot reply threads; undelete; geo trends gaming; media malware; rate-limit storms; multi-device.

| Case | Behavior |
|------|----------|
| Mega-celeb post | Do **not** write 100M inbox rows; mark celebrity; pull/merge on read |
| Protected account | Fan-out only to approved followers; enforce on read |
| Delete post | Tombstone; purge CDN; remove from inboxes async / lazy |
| Double post retry | Idempotent `client_post_id` |
| Shadowban/spam | Soft rank demotion + limits; auditability |
| Hot hashtag | Isolate index partitions; rate-limit writers |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| MAU | 10M | 100M | 1B | 10B theo |
| DAU | 2M | 20M | 200M | 2B |
| Posts/day | 20M | 200M | 2B | 20B |
| Peak post QPS | 500 | 5K | 50K | 500K |
| Peak home TL QPS | 20K | 200K | 2M | 20M |
| Avg followers / user | 200 | 200 | 250 | 300 |
| Celebrity threshold | 10K | 50K | 100K | 250K+ |
| Media objects/day | 5M | 50M | 500M | 5B |
| Notifications/day | 100M | 1B | 10B | 100B |

**Jumps:** 10× = async fan-out + cache TL; 100× = hybrid mandatory + cells; 1,000× = extreme celeb pipeline, multi-region homes, search/trend isolation, QoS classes.

### 1.5 Scope repeat-back

> Twitter/X-like: posts + directed follow graph + hybrid home timeline + user timeline + engagements/notifs + media CDN + search/trends hooks—scaled 10×/100×/1,000× with celebrity pull, cells, abuse, and explicit cost/freshness trade-offs at Amazon bar.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Write vs read

```text
Base peak posts ~500/s
Home TL reads often 10–50× write QPS → design for read fleet + cache
```

### 2.2 Fan-out math (critical)

```text
Naive write-fanout:
500 posts/s × 200 followers = 100,000 inbox writes/s baseline — already heavy

Celebrity trap:
1 post × 50,000,000 followers = 50M writes — impossible / absurd cost

Therefore: hybrid
- Normal users: write-fanout to follower timeline caches/inboxes
- Celebrities (followers > T): store on user timeline only; home TL merges pull
```

### 2.3 Storage

```text
Post metadata ~300–800 B
20M posts/day × 500 B ≈ 10 GB/day metadata
Engagement edges can dominate; aggregate counters + sampled edges
Media: often 10–100× metadata bytes → object store + CDN lifecycle
```

### 2.4 Timeline cache

```text
Home inbox: last K posts per user (e.g. K=800–2000 IDs)
2M DAU × 1KB inbox ≈ 2 TB class Redis/cluster memory care — shard + cold users on disk/Dynamo
```

### 2.5 Latency budget (publish)

```text
Auth → validate → write post store → enqueue fan-out → ACK
Target: durable write before ACK; fan-out async
```

### 2.6 Bottlenecks

(1) Celebrity posts (2) hot reply trees (3) home TL merge CPU (4) media egress (5) search index lag (6) notification storms (7) graph hotspot partitions.

### 2.7 Cost / frugality

Inbox write amplification and CDN video dominate. Hybrid fan-out + media bitrates + notification sampling are cost features, not afterthoughts.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Post Store | Authoritative posts/tombstones | Strong per post_id / author shard |
| Graph | Follow edges, blocks, mutes | Strong enough for authz; caches TTL |
| Timeline / Fan-out | Home inbox materialization | Eventual; freshness SLO |
| Engagement | Likes/reposts counters + edges | Eventual counters OK |
| Notification | Mentions/alerts | At-least-once; dedupe |
| Media | Blob + CDN + scan | Immutable objects |
| Search/Trends | Indexes & aggregates | Nearline lag OK if labeled |
| Abuse/Safety | Limits, reports, demotions | Fail-safe defaults |

**Deal-breaker:** using search index or analytics lake as source of truth for posts.

### 3.2 Components

1. **API Gateway / Edge** — auth, rate limits, TLS.
2. **Post Service** — create/delete/get; idempotency.
3. **Graph Service** — follow/block/mute; celebrity flags.
4. **Fan-out Workers** — write-fanout for normal authors.
5. **Timeline Service** — home merge (inbox + celeb pull); user TL.
6. **Engagement Service** — like/repost; counters.
7. **Notification Service** — mentions, follows, sampled likes.
8. **Media Service** — upload URLs, scan, CDN.
9. **Search Ingest** — stream posts → index.
10. **Trends Pipeline** — windowed aggregations + anti-gaming.
11. **Abuse Platform** — rules + ML scores + actions.
12. **Cell Directory** — user/post home cells.

### 3.3 APIs (sketch)

```text
POST /v1/posts {client_post_id, text, media_ids[], reply_to?, quote_of?}
DELETE /v1/posts/{post_id}
POST /v1/graph/follow {target_user_id}
DELETE /v1/graph/follow/{target_user_id}
GET /v1/timeline/home?cursor=
GET /v1/timeline/user/{user_id}?cursor=
POST /v1/posts/{id}/like
GET /v1/search/recent?q=
```

### 3.4 Post state

```text
CREATED → ACTIVE
ACTIVE → TOMBSTONED (user delete / takedown)
ACTIVE → RESTRICTED (visibility limited)
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Home TL | Hybrid fan-out | Celebrity economics |
| Ranked vs chrono | Chrono MVP | Simpler correctness; rank later |
| Counters | Eventual | Huge write amp otherwise |
| Search | Nearline | Don't block publish |
| Cells | User-home for graph/posts | Blast radius |
| Push notifs | Sampled for high-degree | Cost + spam |

---

## 4. Architecture Diagram

```text
Client → Edge/API → Post Service → Post Store (home cell)
                  \→ Graph Service
                  \→ Media (S3/CDN)
                         |
                    Outbox/Kafka
                         |
         +---------------+----------------+
         v               v                v
   Fan-out Workers   Search Ingest   Notif Workers
         |               |                |
         v               v                v
   Timeline Cache     Search Idx      Notif Store
         ^
         |
   Timeline Service ← celebrity pull from User Timeline
         ^
   Home TL read path (cache + merge + filters block/mute)
```

### 4.1 Publish sequence

```text
1. Validate auth, size, rate limit, abuse pre-check
2. Persist post (idempotent client_post_id)
3. ACK client
4. Async: fan-out OR mark celeb; search ingest; notif mentions; media finalize
```

### 4.2 Home timeline read

```text
1. Load precomputed inbox (normal follows)
2. Pull recent posts from celebrity followees (small set)
3. Merge by time/rank; apply mute/block/filter
4. Return page + cursor
```

### 4.3 Cells

```text
user_id → home_cell
Post writes go to author home cell
Fan-out consumers may cross cells via events (async)
No sync cross-cell distributed transaction for likes
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. ACK ⇒ post durable in post store.
2. Idempotent create via `(author_id, client_post_id)`.
3. Delete/takedown eventually removes public visibility (CDN purge bound).
4. Block/mute honored on read path (and ideally fan-out skip).
5. Protected posts never fan-out to non-followers.
6. Fan-out lag ≠ data loss (user TL + pull repair).
7. Search/trends never sole SoT.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; PG posts; Redis TL; sync fan-out OK small |
| 10× | Kafka fan-out; sharded TL cache; CDN media |
| 100× | Hybrid celeb pull; cells; engagement aggregation; search fleet |
| 1000× | Multi-region; QoS classes; trend isolation; extreme hot-key tooling |

### 5.3 Maintainability

- Post schema versioning; client capability flags.
- Fan-out worker canaries per cell.
- Replay from post log to rebuild inboxes.
- Feature flags for ranked TL experiments.
- Chaos: kill fan-out, partition Kafka, celeb storm drills.

### 5.4 Progressive scale deep dive

**1×:** Single region; write-fanout for all; Redis home lists; PG.

**10×:** Async workers; rate limits; media pipeline; basic celebrity threshold.

**100×:** Hybrid mandatory; cell isolation; notification sampling; search lag SLOs; abuse ML.

**1000×:** Regional read edge; cold history tiers; dedicated celeb serving; ads/ranking isolation from core post SoT.

### 5.5 Celebrity / hot keys

- Maintain `is_celebrity` or degree-based routing.
- Dynamic promotion when follower count crosses T.
- Home TL tracks celebrity followee IDs; pull last N from author TL cache.
- Optional: partial fan-out to online/active followers only.

### 5.6 Delete & GDPR-ish erasure

- Tombstone post; enqueue inbox scrubbers (lazy on read also filters tombstones).
- CDN purge; search delete; media lifecycle.
- Hard erase vs soft tombstone legal modes.

### 5.7 Engagements without melt

- Like: idempotent edge in Cassandra/Dynamo; counters Redis + periodic reconcile.
- Don't fan-out every like to all followers.
- Notifications: coalesce ("1000 likes") for high-degree authors.

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Full write-fanout for celebs | Cost/latency catastrophe |
| Home TL as only SoT | Rebuild nightmare; loss on cache wipe |
| Client time as order | Skew chaos |
| Sync search on publish | Publish latency/availability hit |
| Ignore blocks on read | Trust SEV |
| Active-active dual write same post_id | Forks |

---

## 6. Wrap-Up

### 6.1 Designed

Posts + graph + hybrid timelines + engagements/notifs + media + search/trends hooks + abuse—Amazon-style cells, ownership, cost.

### 6.2 Decisions to defend

1. Hybrid fan-out with celebrity pull
2. Post store SoT; timeline cache derived
3. Async fan-out after durable ACK
4. Eventual counters with reconcile
5. Block/mute on read path
6. Cells by user home
7. Nearline search
8. Notification sampling for hot authors

### 6.3 Risks

- Celebrity storms
- Fan-out backlog → stale TL
- Abuse gaming trends
- Media cost
- Ranked TL complexity creep

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope Twitter vs FB vs chat |
| 5–15 | Post store + graph |
| 15–28 | Hybrid fan-out math |
| 28–38 | Delete, abuse, media, search |
| 38–45 | Scale jumps, ownership, metrics |

### 6.5 Closer

> **Twitter/X**: durable posts, directed follows, hybrid home timeline, celebrity pull, derived caches, abuse & cost first-class, cells, progressive 10×/100×/1,000×.

---

## 7. Deeper / Related Interview Questions

### 7.1 Fan-out

**Q: Where is threshold T chosen?**  
A: Cost model: inbox write amp vs read merge CPU; start ~10k–100k followers; measure.

**Q: What if someone becomes celeb overnight?**  
A: Flip flag; stop write-fanout; optionally backfill stop; readers pull.

**Q: Partial online fan-out?**  
A: Push to connected sessions; others pull—similar to chat hybrid.

### 7.2 Ordering

**Q: Global total order of all posts?**  
A: No—per-author order + timeline merge by timestamp/snowflake id.

**Q: Snowflake IDs?**  
A: Time-sortable unique IDs help merge without central seq.

### 7.3 Graph

**Q: Follower list for celeb fan-out?**  
A: You mostly **don't** iterate 100M for writes; pull model. For analytics, offline.

**Q: Mutual follow vs follow?**  
A: Twitter is directed; don't assume symmetric authz.

### 7.4 Search & trends

**Q: Exactly-once index?**  
A: At-least-once ingest + idempotent doc id; delete tombstones.

**Q: Trend gaming?**  
A: Reputation-weighted counts; rate limits; human review for #1 spikes.

### 7.5 Abuse

**Q: Report volume?**  
A: Priority queues; hash-similarity clusters; appeals workflow.

**Q: Rate limit keys?**  
A: user, IP/device, phone/email age, post type, mention fan-out size.

### 7.6 Media

**Q: Upload flow?**  
A: Presigned PUT → async scan → attach to post when clean; fail-closed for exec types.

### 7.7 Interview traps

**Q: Redis as only post store?**  
A: Weak durability/rebuild story.  
**Q: One Kafka topic unpartitioned?**  
A: Hot partitions.  
**Q: Ranked neural TL before hybrid fan-out?**  
A: Wrong order—economics first.

### 7.8 Metrics

| Metric | Why |
|--------|-----|
| publish_ack_p99 | Write UX |
| fanout_lag_p99 | Freshness |
| home_tl_p99 | Read UX |
| inbox_write_amp | Cost |
| celeb_pull_merge_ms | Hot path |
| abuse_action_latency | Trust |
| search_index_lag | Product |
| CDN_egress_$ | Frugality |

### 7.9 Ownership

**Q: Stale home TL pages?**  
A: Timeline/Fan-out oncall; Post store if source missing.  
**Q: Wrong user sees protected post?**  
A: SEV trust — Graph authz + Timeline.

### 7.10 Progressive drill

**10×:** async fan-out. **100×:** hybrid+cells. **1000×:** celeb serving + multi-region QoS.

---

## 8. Appendices

### 8.1 Schema sketches

```text
users(user_id, handle, created_at, flags, home_cell)
posts(post_id, author_id, created_at, text, media_refs, reply_to, quote_of, state)
follows(follower_id, followee_id, created_at, state)
blocks(blocker_id, blocked_id)
mutes(muter_id, muted_id)
home_inbox(user_id, post_id, ts, author_id)  -- cache/materialized
engagement_like(post_id, user_id, ts)
counters(post_id, likes, reposts, replies)  -- eventual
notifications(notif_id, user_id, type, refs, ts, read)
```

### 8.2 API checklist

- [ ] Idempotent post create
- [ ] Delete/takedown
- [ ] Follow/block/mute
- [ ] Home + user timeline cursors
- [ ] Like/repost
- [ ] Search recent
- [ ] Media upload session
- [ ] Report abuse

### 8.3 Oncall checklist

- [ ] Fan-out lag dashboard
- [ ] Celebrity post storm
- [ ] Redis/TL cache memory
- [ ] Post store p99/errors
- [ ] CDN purge failures
- [ ] Trend anomaly
- [ ] Abuse false positive spike
- [ ] Cell saturation

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Home timeline | Posts from followees |
| User timeline | Author's posts |
| Write-fanout | Push post ids to follower inboxes |
| Pull/merge | Read celeb posts at request time |
| Snowflake | Time-sortable unique id |
| Protected | Follower-only visibility |
| Tombstone | Soft delete marker |

### 8.5 Deal-breaker one-liners

- Write 100M inbox rows for one celeb post
- Cache-only posts without durable store
- Skip block checks on TL merge
- Publish blocked on search index

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| Post store | Post Platform |
| Fan-out/TL | Timeline |
| Graph | Social Graph |
| Media | Media Platform |
| Search/Trends | Search |
| Abuse | Trust & Safety Eng |
| Notifs | Notifications |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | Monolith, PG, Redis TL |
| 10× | Kafka fan-out, CDN |
| 100× | Cells, hybrid, search fleet |
| 1000× | Multi-region, celeb tier, cold storage |

### 8.8 Failure injection

1. Kill fan-out consumers — lag grows; reads still show user TL pull for followed celebs; inbox stale for normals until catch-up.
2. Duplicate post create — idempotent.
3. Cache wipe — rebuild from follows + recent posts (expensive; rate-limit rebuild).
4. Graph partition — fail-closed on protected; degrade suggestions.
5. CDN origin storm — shields + collapse.

### 8.9 Cursor design

```text
cursor = (ts, post_id) or snowflake
stable pagination; skip tombstones; avoid OFFSET
```

### 8.10 Ranked timeline hook

Features: recency, affinity, engagement probability, diversity, safety score. Ranker consumes candidate set from hybrid retrieval—does not replace retrieval economics.

### 8.11 Push notifications

Device tokens; collapse keys per conversation/thread; quiet hours; sample low-value likes.

### 8.12 Interview closer checklist

- [ ] Hybrid fan-out math on board
- [ ] Post SoT vs derived TL
- [ ] Celebrity threshold
- [ ] Delete/purge story
- [ ] Block/mute
- [ ] Cells
- [ ] Metrics + ownership
- [ ] 10×/100×/1000×

### 8.13 Related systems

Ads auction, live audio, DMs, recommendations ("For You"), identity/handle service, anti-bot device attestation.

### 8.14 Sample events

```text
POST_CREATED
FOLLOW_CREATED
FANOUT_ENQUEUED
INBOX_APPENDED
POST_TOMBSTONED
LIKE_ADDED
NOTIF_MENTION
SEARCH_UPSERT
```

### 8.15 Rebuild strategy

From post log + follow graph: prioritized active users; backpressure; never block publish path on rebuild.

### 8.16 Multi-region

Author home region for writes; edge caches for TL reads; cross-region follow is async eventing.

### 8.17 Security

OAuth/session; CSRF; XSS in rendered text; media active-content scan; admin audit logs for takedowns.

### 8.18 Cost narrative

Inbox amp + video egress + notif push. Hybrid + sampling + bitrate ladders = frugality.

### 8.19 LP hooks

Customer Obsession on abuse false positives; Dive Deep on fan-out lag; Frugality on celeb writes; Ownership of SEV when protected posts leak; Bias for Action with chrono MVP before fancy ranker.

### 8.20 QoS degrade order

1. Drop typing-like ephemeral (if any) / online presence extras  
2. Delay non-mention notifs  
3. Stretch fan-out lag SLO  
4. Simplify ranker to chrono  
5. Keep publish + authz + block correctness longest  

---

## Deep Technical Notes — Twitter / X

### Snowflake / ID

64-bit time + worker + seq; avoid DB auto-increment hotspot; helps global merge sort.

### Outbox

Post commit + outbox row → Kafka; avoids dual-write loss.

### Inbox storage choices

Redis lists for hot users; Dynamo/Cassandra for durable inbox; tier by activity.

### Mute vs block

Block: stronger authz (often prevent view/follow). Mute: filter from TL but may still allow profile view per product policy—state policy explicitly.

### Reply spam

Rate-limit replies to hot posts; require verified phone for high-velocity; collapse low-quality replies.

### Hashtag index

Tokenize; partition by tag hash; hot tags get dedicated shards / rate limits.

### Bot detection signals

Graph velocity, content similarity, device farms, clickstream improbability—async scorers with appeals.

---

## Worked Capacity Narrative — Twitter / X

Reads dominate QPS; writes dominate amplification risk. If you optimize only for post QPS and ignore follower-weighted write amp, you fail the L6 interview. Show the celeb equation early.

## Customer-Trust Paragraph — Twitter / X

Leaked protected posts, failed deletes that remain on CDN, and abuse mis-actions are trust SEVs. Freshness is important; **authz correctness** is sacred.

## Progressive Scale Recap — Twitter / X

- **10×:** async fan-out, CDN, rate limits
- **100×:** hybrid celeb pull, cells, search fleet
- **1,000×:** multi-region, celeb serving tier, QoS, cold history

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Twitter / X

### S1. Hybrid fan-out

Write-fanout for normal degree; pull/merge for celebrities; threshold from cost model.
**Invariant:** No unbounded O(followers) sync write on publish for mega accounts.
**Metric:** `inbox_write_amp`, `fanout_lag_p99`, `celeb_merge_ms`.
**10× note:** Async helps; hybrid becomes mandatory near 100×.
**Ownership:** Timeline oncall.

### S2. Post store SoT

Durable posts/tombstones per author shard; TL caches derived and rebuildable.
**Invariant:** Cache wipe must not lose ACK'd posts.
**Metric:** `post_durability_errors`, rebuild backlog.
**Ownership:** Post Platform.

### S3. Graph authz

Follows/blocks/mutes/protected flags enforced on fan-out skip + read merge.
**Invariant:** Protected visibility never relies on obscurity.
**Metric:** authz_deny, sealed-test probes.
**Ownership:** Graph + Timeline joint.

### S4. Engagement counters

Eventual counters + idempotent edges; coalesce notifications.
**Invariant:** Like retry does not multiply count unbounded.
**Metric:** counter_drift, like_idempotency_conflicts.
**Ownership:** Engagement.

### S5. Media pipeline

Presigned upload, async scan, CDN; attach clean assets only.
**Invariant:** Malware not publicly served when scanner policy fail-closed.
**Metric:** scan_lag, block_rate, egress_$.
**Ownership:** Media.

### S6. Search nearline

Consume post stream; lag SLO separate from publish ACK.
**Invariant:** Index lag does not block publish availability.
**Metric:** index_lag_p99.
**Ownership:** Search.

### S7. Trends anti-gaming

Reputation-weighted windows; anomaly alerts; human escalate.
**Invariant:** Raw volume alone cannot crown trends.
**Metric:** trend_flip_rate, gaming_score.
**Ownership:** Trends + Trust.

### S8. Cells & blast radius

User home cells; no cross-cell sync transactions for likes; async eventing.
**Invariant:** Cell outage ≠ global write outage.
**Metric:** cell_error_budget, failover_time.
**Ownership:** Platform Foundation + Post.

## Scenario Runbooks — Twitter / X

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|-----------|
| Fan-out lag spike | Scale consumers; shed noncritical notifs | Stale home TL | Hot partition audit |
| Celeb post storm | Ensure pull path; protect write-fanout | Availability | Threshold tune |
| Protected post leak | Patch authz; invalidate caches; SEV | Trust | Probe tests |
| Delete not on CDN | Hard purge | Trust | TTL policy |
| Trend brigading | Freeze topic; raise thresholds | Integrity | Anti-game model |
| Redis TL OOM | Evict cold; fail to durable inbox store | Latency | Capacity |
| Search lag | Scale indexers; partial degrade UI | Search stale | Lag SLO |
| Abuse FP spike | Kill switch demotions; appeals surge | Trust | Model rollback |

## Rapid-Fire Q&A — Twitter / X

**RQ1. Why hybrid fan-out?**  
**A:** Mega-followee write amp is economically impossible; pull/merge fixes it.

**RQ2. How to test hybrid in staging?**  
**A:** Synthetic celeb accounts, inbox amp metrics, canary cells, rollback flag.

**RQ3. What regresses at 100× if ignored?**  
**A:** Publish latency, cost explosion, or silent drop of fan-out.

**RQ4. Why post store SoT?**  
**A:** Rebuild and delete correctness; cache is derived.

**RQ5. How to test SoT?**  
**A:** Cache wipe drill; verify posts remain; measure rebuild.

**RQ6. 100× regression without SoT?**  
**A:** Data loss SEVs / unrebuildable TL.

**RQ7. Why enforce blocks on read?**  
**A:** Fan-out skip races; read path is last line.

**RQ8. Test blocks?**  
**A:** Sealed user probes; integration suites.

**RQ9. Regression?**  
**A:** Trust SEV; legal/regulatory heat.

**RQ10. Why eventual counters?**  
**A:** Exact global count on every like doesn't scale; reconcile.

**RQ11. Test counters?**  
**A:** Idempotent retry storms; drift dashboards.

**RQ12. Regression?**  
**A:** Wrong counts / notif storms / DB melt.

**RQ13. Why async media scan?**  
**A:** Don't block publish on heavy AV; policy for visibility gating.

**RQ14. Test media?**  
**A:** Malware fixtures; fail-closed modes.

**RQ15. Regression?**  
**A:** Safety incidents or upload latency fire drills.

**RQ16. Why nearline search?**  
**A:** Protect publish ACK latency/availability.

**RQ17. Test search?**  
**A:** Inject lag; UI labels; indexer canaries.

**RQ18. Regression?**  
**A:** Coupled outage of post+search.

**RQ19. Why cells?**  
**A:** Blast radius and independent scaling.

**RQ20. Test cells?**  
**A:** Game-day cell kill; directory failover.

**RQ21. Regression?**  
**A:** Global brownout from local hotspot.

**RQ22. Why sample notifs?**  
**A:** Hot authors generate impossible push QPS.

**RQ23. Test notifs?**  
**A:** Coalescing correctness; collapse keys.

**RQ24. Regression?**  
**A:** Push provider bans / cost melt / user spam.

## Narrative Walkthrough — Twitter / X

### Walkthrough beat 1

User posts: auth → validate → durable post → ACK → async fan-out/search/notifs. Tradeoff: ACK before fan-out completes (freshness lag vs availability).

### Walkthrough beat 2

Normal followee post lands in follower inboxes via workers. Tradeoff: write amp vs read CPU.

### Walkthrough beat 3

Celebrity post: no mega inbox write; followers merge pull on home read. Tradeoff: slightly heavier reads for celeb-heavy users.

### Walkthrough beat 4

Home TL read: inbox + celeb pulls + filters. Tradeoff: ranked complexity deferred.

### Walkthrough beat 5

Delete: tombstone + async scrub + CDN purge. Tradeoff: lazy vs eager scrub cost.

### Walkthrough beat 6

Like: idempotent edge + counter incr; coalesce notifs. Tradeoff: exactness vs scale.

### Walkthrough beat 7

10× async; 100× hybrid+cells; 1000× multi-region/QoS. Tradeoff: each jump changes bottlenecks.

### Walkthrough beat 8

Deal-breakers: celeb full fan-out; cache-only SoT; authz skip. Unit economics: amp + egress.

## Pre-Onsite Checklist — Twitter / X

- [ ] Hybrid fan-out equation rehearsed with numbers
- [ ] Celebrity threshold story
- [ ] Post SoT vs TL cache
- [ ] Delete/CDN purge
- [ ] Block/mute/protected
- [ ] Cells blast radius
- [ ] Search lag decoupled
- [ ] Abuse kill switches
- [ ] Metrics + pager ownership
- [ ] 10×/100×/1000× what-breaks
- [ ] Runbook: fan-out lag
- [ ] Runbook: protected leak
- [ ] Runbook: celeb storm
- [ ] Frugality: media + notif sampling
- [ ] SDM pitch: trust then SLO then kill switch

### Extra drill

Rehearse explaining Twitter/X to a skeptical SDM: start from customer trust (authz/abuse), then fan-out math, then one architecture box that owns freshness, then kill switches. Mention what you would not build (neural ranker before hybrid economics).

### Extra drill

Whiteboard only: posts/s × followers = inbox writes/s; mark where hybrid cuts the product.

### Extra drill

Explain rebuild after Redis loss without panicking publish path.

---

*End of document — Twitter / X (Amazon Interview Style) (SDE III)*
