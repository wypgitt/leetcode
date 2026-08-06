# System Design: Instagram Stories (Mobile)

> **Focus areas:** Ephemeral 24h media · Mobile upload · Fan-out · Sticky tray ranking · Prefetch · CDN · Views/reactions · Privacy close-friends · Active ranking  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split upload vs consume planes; explicit fan-out-on-write vs read; deal-breakers for “query all friends’ media every open” at IG scale  
> **Interview theme:** Classic Meta mobile — Stories tray + fullscreen viewer with ephemeral TTL and battery/network-aware clients

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

Goal: **bound the product**—**Instagram Stories**: ephemeral photo/video segments (typically 15s video / images), 24h TTL, creator-centric rings in a tray, fullscreen tap-through viewer, views, lightweight replies/reactions, Close Friends, mobile-first upload and prefetch.

### 1.0 What this is / is not

| Dimension | **IG Stories (this doc)** | Not this |
|-----------|---------------------------|----------|
| Primary job | Publish & consume ephemeral stories | Permanent Feed posts / Reels long-form platform |
| Unit | Story item (~slide) in a day’s story | Multi-hour live (hooks only) |
| Success | Fast tray, smooth viewer, reliable upload | Perfect archival analytics |
| TTL | ~24h then gone (plus highlights Phase 1.5) | Forever CDN without expiry |
| Client | Mobile-first (iOS/Android) | Desktop-only design |

**Scope statement:** Design Instagram Stories end-to-end for mobile: capture/upload, distribute, tray ranking, viewer prefetch, ephemeral expiry, and scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Media types? | Photo, video ≤15s, text/stickers overlays | Transcode + sticker metadata |
| F2 | TTL? | 24h from publish | TTL indexes + GC; CDN signed URLs expiry |
| F3 | Audience? | Followers; Close Friends list; optional private | ACL on story |
| F4 | Tray? | Rings of users with unseen stories | Tray API ranked |
| F5 | Viewer? | Tap left/right; hold pause; vertical next user | Prefetch next N segments |
| F6 | Views? | Creator sees viewers list (non-close-friends rules) | View events aggregated |
| F7 | Replies? | Message reply via chat handoff | Integration stub |
| F8 | Reactions? | Quick reacts | Lightweight events |
| F9 | Highlights? | Phase 1.5 permanent collections | Separate store |
| F10 | Stickers/polls? | Poll/question stickers MVP lite | Interactive sticker service |
| F11 | Offline draft? | Local draft then upload | Client resumable upload |
| F12 | Notifications? | Optional friend story notifs | Push sparse |

**MVP functional scope:**

1. Mobile capture → resumable upload → process (transcode/poster) → publish story item.  
2. 24h expiry; invisible after TTL.  
3. Followers (and Close Friends) can see per ACL.  
4. Tray of active story authors ranked (unseen first, affinity).  
5. Viewer with prefetch; record views.  
6. Basic stickers metadata; poll sticker optional.  
7. Delete-by-author before TTL.  
8. CDN delivery with signed URLs.

**Out of MVP:**

- Full Live streaming  
- Stories ads auction deep dive (mention)  
- Cross-app Facebook Stories unification details  
- AR effects training pipeline  
- Perfect global ordering of concurrent publishes

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Tray latency | Instant on app open | p99 < 150–250ms |
| N2 | Time-to-first-frame | Tap ring → video | p99 < 300–500ms (cached/prefetched better) |
| N3 | Upload success | Flaky mobile nets | Resumable; background upload |
| N4 | Availability consume | Critical | 99.9%; stale tray OK briefly |
| N5 | Expiry correctness | Must disappear | TTL enforced server-side |
| N6 | Battery/data | Client-conscious | Prefetch budgets; Wi-Fi prefer |
| N7 | View privacy | Per product rules | Close Friends hidden viewers etc. |
| N8 | Scale | IG global | Fan-out strategy + CDN |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User shoots 2 clips → upload → friends see ring → tap → watch → view counted.  
2. Close Friends story → only CF list sees.  
3. Author deletes item → removed from viewers promptly.  
4. Story ages >24h → GC; tray drops author if no remaining.  
5. Poll sticker tap → counts update.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload dies at 90% | Resume from offset |
| Celebrity 50M followers | No naive fan-out-on-write to all inboxes |
| User with 0 stories left but cached tray | Refresh removes ring |
| Clock skew TTL | Server `expires_at`; client hint only |
| Prefetch over cellular expensive | Budget + user settings |
| Blocked author | Not in tray |
| Mute stories | Suppress author |
| Concurrent items order | `created_at` + id tie-break |
| CDN URL leak after expiry | Short-lived signatures; ACL check on issue |
| View flood on celebrity | Sample / aggregate; async |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 100M | — | mega IG | extreme |
| Stories published / day | 500M | 5B | 50B | cell fabric |
| Peak publish QPS | 20K | 200K | 2M | 20M |
| Tray opens / day | 2B | 20B | 200B | — |
| Peak tray QPS | 100K | 1M | 10M | 100M |
| Story video watch start QPS | 200K | 2M | 20M | — |
| Avg followers | 200–500 | skew heavy | skew | skew |
| Celebs >10M followers | many | many | many | many |
| Media stored (24h window) | tens PB churn | ×10 | ×100 | multi-cell CDN |
| View events / s peak | 1M | 10M | 100M | aggregate trees |

**What each jump forces:**

- **10×:** Hybrid fan-out; CDN; tray cache; resumable upload fleet.  
- **100×:** Celebrity pull path mandatory; view aggregation hierarchy; regional media.  
- **1,000×:** Cellized story services; edge tray assembly; aggressive prefetch intelligence.

### 1.5 Etc. (Constraints & Assumptions)

- Follow graph + mute/block exist.  
- Chat for replies exists.  
- Object storage + CDN available.  
- Highlights are optional extension of storage without TTL.

**Scope statement to repeat back:**

> Design Instagram Stories for mobile: resumable upload and processing, 24h ephemeral distribution with hybrid fan-out, ranked tray, prefetching viewer, views/stickers, Close Friends ACL, CDN delivery—scaling through celebrity-aware read paths and progressive cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Baseline | Plane |
|-------|----------|-------|
| Publish | 20K/s peak | Upload + processing |
| Tray read | 100K/s | Metadata |
| Media download | 200K+/s starts | CDN |
| View events | 1M/s | Ingest aggregate |
| Graph lookups | with tray | Graph cache |

### 2.2 Fan-out-on-write explosion

```text
Avg 300 followers × 20K publish/s = 6M inbox writes/s — painful but maybe
Celebrity 50M × 1 publish = 50M writes — DEAL-BREAKER
⇒ Hybrid: fan-out regular users; pull for celebrities / high degree
```

### 2.3 Active stories working set

```text
500M stories/day ≈ still ~500M active in 24h window (order)
Metadata ~1KB => ~500TB metadata worldwide (sharded)
Media much larger; CDN + origin object store with lifecycle delete
```

### 2.4 Tray assembly

```text
Candidate authors = following with active story flag
Hundreds of followees; need fast "who has active story"
Invert: keep bitmap/set of active story authors OR fan-in inbox of story ids
```

### 2.5 Bandwidth

```text
Video segment 1–3MB; photo 100–300KB
200K starts/s × 1MB = 200 GB/s — CDN edge absorbs
```

### 2.6 Prefetch budget

```text
Prefetch next 2 segments + next user first segment ≈ 3–6MB
Only when on Wi-Fi / user in viewer / battery OK
```

### 2.7 24h working-set churn

```text
500M stories/day enter; ~500M leave after 24h (steady state order)
GC must delete metadata + objects + inbox entries
Missed GC → cost + privacy (expired still fetchable) — deal-breaker
Signed URL TTL ≤ min(1h, time_to_expires_at)
```

### 2.8 Tray vs media QPS split

```text
Tray 100K QPS × ~2KB ≈ 200 MB/s metadata — app/edge cacheable
Media 200K starts × 1MB → 200 GB/s — CDN only
Never serve story video from Stories API origin
```

### 2.9 Viewed-state write volume

```text
Users watch ~20 items/session × sessions → view events ≫ publishes
1M view events/s → Kafka aggregate; not sync UPDATE per view on primary
Unseen ring clear: last_seen watermark per (viewer, author) eventual
```

### 2.10 Fan-out threshold worksheet

| Author degree | Strategy | Writes on publish |
|---------------|----------|-------------------|
| 200 | Fan-out inbox | ~200 |
| 10K | Fan-out | ~10K |
| 100K+ | Pull ActiveAuthor | ~1 metadata write |
| 50M | Pull only | ~1 — never 50M inbox writes |

### 2.11 Progressive Stories capacity

| Scale | Upload | Distribution | Views | Tray |
|-------|--------|--------------|-------|------|
| Base | Resumable | Hybrid L | Batch Kafka | Ranked API |
| 10× | Regional edge | CDN | Aggregators | User tray cache |
| 100× | Multi-region process | Celeb pull optimized | Hierarchy | Affinity ranker |
| 1,000× | Cell upload | Edge tray assembly | Sampled lists | Prefetch ML |

### 2.12 BOTE anti-patterns

| Anti-pattern | Failure |
|--------------|---------|
| Fan-out all celebs | Multi-million write spikes |
| Client-only 24h timer | Expired still served if URL known |
| Sync view counter++ | Write path melt |
| Tray = walk all followees’ media tables | Graph + storage stampede |

---

## 3. High-Level Design

### 3.1 API (mobile)

| Op | Semantics |
|----|-----------|
| `POST /v1/stories/upload_session` | Start resumable upload |
| `PUT /v1/stories/upload/{id}` | Chunked bytes |
| `POST /v1/stories/publish` | Finalize metadata + stickers + audience |
| `GET /v1/stories/tray` | Ranked authors + cover + unseen |
| `GET /v1/stories/reel/{user_id}` | Items for viewer |
| `POST /v1/stories/views` | Batch view acks |
| `POST /v1/stories/{id}/sticker_interact` | Poll etc. |
| `DELETE /v1/stories/{id}` | Author delete |

### 3.2 Data model

| Entity | Key fields |
|--------|------------|
| StoryItem | story_id, author_id, media_urls, poster, duration, created_at, expires_at, audience, stickers[] |
| ActiveAuthor | author_id → latest_expires, item_count, cover_media |
| Fanout inbox (regular) | viewer_id → list of (author_id, story_ids, ts) |
| CloseFriends | owner_id → member set |
| Views | story_id → count; viewer list store (capped) |
| UploadSession | session_id, offsets, user_id |

### 3.3 Distribution — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Fan-out-on-write** | Fast tray read | Celeb write amp | Low/mid degree |
| **Fan-out-on-read** | Simple writes | Slow tray; graph stampede | Not alone |
| **Hybrid** | Best of both | Complexity | **MVP at IG** |
| **Push notify all** | — | Battery/noise | Sparse only |

**Chosen:** Write fan-out to followers’ story inboxes for authors below degree threshold L; above L mark `is_celebrity` and tray pulls active story pointer from author object.

### 3.4 Tray ranking — Why X over Y

| Signal | Role |
|--------|------|
| Unseen > seen | Product core |
| Affinity / close friends / DMs | Rank |
| Recency of latest item | Freshness |
| Mute / hide | Filter |
| Exclusive CF available | Badge |

**Deal-breaker:** chronological follow list without unseen prioritization.

### 3.5 Media pipeline — Why X over Y

| Step | Choice |
|------|--------|
| Upload | Resumable chunked (TUS-like) |
| Store | Object store original |
| Process | Transcode ABR ladder small; poster thumbnail |
| Deliver | CDN signed URL |
| Expire | Lifecycle rule + DB TTL |

**Deal-breaker:** requiring full re-upload on every network blip; storing forever without GC.

### 3.6 Why X over Y summary

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Distribution | Hybrid fan-out | Celebs | Pure write fan-out |
| TTL | Server expires_at + GC | Correctness | Client-only hide |
| Tray | Cached ranked | Latency | Live graph walk each open |
| Media | CDN | Bandwidth | Origin every byte |
| Views | Async aggregate | QPS | Sync write per view to primary |
| Upload | Resumable | Mobile | Single PUT only |

### 3.7 Expanded HLD tradeoffs

| Axis | A | B | Pick |
|------|---|---|------|
| Distribution | Always fan-out | Always pull | **Hybrid by degree L** |
| Unseen | Client-only | Server watermarks | **Server + client cache** |
| Views | Sync counter | Kafka hierarchy | **Async** |
| Expiry | Client timer | Server expires_at + signed URL | **Server** |
| Prefetch | Aggressive always | Budgeted by network/battery | **Budgeted** |

**Anti-patterns:** celeb write fan-out; forever CDN URLs; sync views; tray via full media table scan.

---

## 4. Architecture Diagram

```text
 +-------------------+         +------------------+
 | IG Mobile Client  |<------->| Edge / API GW    |
 | capture, prefetch |         | auth, rate limit |
 +---------+---------+         +--------+---------+
           |                            |
           | upload chunks              | tray / reel / views
           v                            v
 +-------------------+         +--------+---------+
 | Upload Service    |         | Stories API      |
 | resumable sessions|         | tray, reel, ACL  |
 +---------+---------+         +--------+---------+
           |                            |
           v                            |
 +-------------------+                  |
 | Object Store      |                  |
 | originals         |                  |
 +---------+---------+                  |
           |                            |
           v                            |
 +-------------------+                  |
 | Media Processor   |--> CDN origin ---+--> CDN Edges --> Client player
 | transcode, poster |                  |
 +---------+---------+                  |
           | publish                    v
           v                   +--------+---------+
 +-------------------+         | Tray / Inbox     |
 | Story Metadata DB |<------->| Fanout workers   |
 | items + expiry    |         | hybrid celebs    |
 +---------+---------+         +--------+---------+
           |                            ^
           |                            | follow graph
           v                            |
 +-------------------+         +--------+---------+
 | TTL / GC workers  |         | Graph / CF / Mute|
 +-------------------+         +------------------+

 View path: Client -> Views API -> Kafka -> Aggregators -> counts + viewer lists
```

**Publish path:**

```text
create session -> PUT chunks -> process -> publish metadata
  -> set ActiveAuthor
  -> if degree < L: fanout inbox entries to followers
  -> else: celebrity pointer only
```

**Tray path:**

```text
read inbox authors + pull celebrity actives among followees
  -> filter mute/block/expiry
  -> rank unseen/affinity
  -> return covers + signed thumb URLs
```

**Viewer path:**

```text
GET reel(user)
  -> ACL
  -> items not expired
  -> signed media URLs
  -> client prefetches next
  -> batch views
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Expired stories never returned** (`now < expires_at` server-side).  
2. **ACL: followers / CF / not blocked**.  
3. **Upload session belongs to user**; publish validates processed media.  
4. **Delete/tombstone wins** over lagging fan-out.  
5. **View counts approximate OK**; privacy rules for viewer lists enforced.

#### 5.1.2 Exactly-once fan-out?

At-least-once fan-out with idempotent inbox keys `(viewer, story_id)`. Dupes OK.

#### 5.1.3 Partial publish failure

If fan-out fails mid-way: retry workers from author outbox; celebrity path avoids this amp.

#### 5.1.4 Expiry

```text
expires_at = created_at + 24h
Tray filters expired
GC job deletes metadata + object lifecycle
CDN signatures expire <= remaining TTL
```

### 5.2 Scalability

#### 5.2.1 Degree threshold L

```text
L ≈ 10K–100K followers (tune)
Below L: write fan-out
Above L: tray checks ActiveAuthor store for those followees (cached)
```

#### 5.2.2 Sharding

| Store | Key |
|-------|-----|
| Metadata | story_id / author_id |
| Inbox | viewer_id |
| ActiveAuthor | author_id |
| Views aggregates | story_id |
| Upload sessions | session_id |

#### 5.2.3 View aggregation

```text
Client batches views every few seconds
Kafka topic views
Local aggregate -> regional -> global counts
Viewer list: store recent N / friends-first; celebrities see counts more than full lists
```

#### 5.2.4 Progressive scale

| Scale | Add |
|-------|-----|
| 10× | Hybrid; CDN; tray cache |
| 100× | Hierarchical views; regional upload; celeb pull optimized |
| 1,000× | Cells; edge tray; smart prefetch ML budgets |

### 5.3 Maintainability

- Clear client capability negotiation (codecs).  
- Feature flags for sticker types.  
- Media pipeline versioning.  
- Chaos tests: upload resume, expiry, celeb publish.  
- Privacy review for CF and views.

### 5.4 Mobile client architecture

```text
Capture -> local draft (encrypted at rest optional)
Background upload (OS constraints)
Prefetch manager: queue next items with bytes budget
Player: pre-buffer; tap zones; pause on hold
Optimistic tray from disk cache; refresh network
Battery: reduce prefetch on Low Power
```

### 5.5 Close Friends

```text
audience = CLOSE_FRIENDS
distribute only to CF members (fan-out subset) or ACL on pull
viewer list visibility restricted per product policy
```

### 5.6 Stickers / polls

Interactive sticker state in separate small service keyed by `story_id + sticker_id`; not in video bytes. Votes idempotent per user.

### 5.7 Ranking details

```text
score = unseen_boost + affinity + recency + CF_boost - mute
stable sort by score then author_id
```

Affinity from interactions (DMs, likes, previous story watches).

### 5.8 Prefetch strategy

| State | Prefetch |
|-------|----------|
| App cold open | Covers only |
| Tray visible | First segments of top K unseen |
| In viewer | Next 2 items + next author first |
| Cellular + low data | Covers + on-demand |

### 5.9 Security

Signed URLs with short TTL; referer/token binding optional; transform strip EXIF; malware scan on upload; rate-limit publishes.

### 5.10 Highlights (Phase 1.5)

Copy media to non-TTL highlight storage; new ids; separate API; doesn’t keep original story past 24h unless copied.

### 5.11 Nested deep dive — 24h TTL

#### 5.11.1 Source of truth

```text
expires_at = created_at + 24h   # server clock
All read APIs: WHERE now < expires_at AND status != deleted
Client countdown is UX sugar only
```

#### 5.11.2 Enforcement surfaces

| Surface | Enforcement |
|---------|-------------|
| Tray | Filter expired authors/items |
| Reel | Omit expired items |
| Signed URL | `exp ≤ min(now+TTL_sign, expires_at)` |
| Object store | Lifecycle rule delete after grace |
| Inbox entries | TTL'd keys aligned to expires_at |
| CDN | Cache cannot outlive signature |

#### 5.11.3 GC workers

```text
periodically:
  tombstone metadata expires_at < now
  delete objects after grace (e.g. +1h)
  scrub dangling inbox refs
  metrics: expired_but_still_served (should be ~0)
```

#### 5.11.4 Clock skew

Clients may be wrong; server decides. Highlights copy-on-write **out** of TTL path before expiry if user saves.

**Deal-breaker:** client-only hide with long-lived CDN URLs.

### 5.12 Nested deep dive — Ring tray

#### 5.12.1 Tray payload

```json
{"authors":[{"user_id":"u","unseen":true,"cover":"...","ts":0,"cf":false,"live":false}]}
```

Ranked list of **authors** (rings), not flat media grid.

#### 5.12.2 Candidate assembly

```text
from_inbox = inbox.active_authors(viewer)          # fan-out recipients
celebs = following(viewer) ∩ celebrity_active      # pull path
candidates = filter(mute, block, expiry, ACL)
return rank(candidates)
```

#### 5.12.3 Ranking

```text
primary: unseen > seen
secondary: affinity (DM/likes/watches) + CF boost + recency
stable tie-break: author_id
```

**Deal-breaker:** chronological follow list without unseen-first.

#### 5.12.4 Caching

| Cache | TTL | Invalidate |
|-------|-----|------------|
| Per-user tray | 30–60s | Publish/delete async best-effort |
| Disk client | until refresh | App open / pull-to-refresh |
| ActiveAuthor | seconds–minutes | On publish/expiry |

Cold open: serve disk tray then network refresh.

### 5.13 Nested deep dive — Viewed state

#### 5.13.1 Receipts

```text
Client batches ViewEvent {viewer, story_id, author_id, watched_ms, ts}
Flush: exit viewer / every 5s / N items
Server: idempotent keys; update last_seen; aggregate counts async
```

#### 5.13.2 Unseen computation

```text
author.unseen = exists item with created_at > viewer.last_seen[author]
             AND not expired AND ACL ok
```

Eventual consistency OK if ring clears shortly after watch.

#### 5.13.3 Creator viewer lists

- Non-celeb: store recent viewers (capped).  
- Celeb: counts + sampled/friends-first; not full 50M list.  
- Close Friends: product privacy rules on who appears.

#### 5.13.4 Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| Sync `UPDATE views++` on primary per view | QPS melt |
| Exact global viewer list for celebs | Storage/read impossible |
| Unseen only on client | Multi-device wrong rings |

### 5.14 Nested deep dive — Fanout

#### 5.14.1 Hybrid algorithm

```text
on_publish(author, item):
  active.set(author, item)
  if degree(author) < L:
    for f in followers(author):  # respect CF subset if audience=CF
      inbox.add(f, author, item.id, item.expires_at)  # idempotent
  else:
    mark_celebrity(author)  # tray pull ActiveAuthor
```

#### 5.14.2 Why L exists

```text
50M followers × 1 publish = 50M inbox writes — deal-breaker
Pull: followers’ tray checks cached ActiveAuthor among followees — O(followees)
```

#### 5.14.3 Delete / tombstone vs lagging fanout

```text
delete -> metadata tombstone wins
async inbox remove; readers filter tombstone/expiry
celebrity path: clear ActiveAuthor pointer
```

#### 5.14.4 CF fanout

Distribute only to CF membership snapshot at publish; pull path ACL checks membership.

### 5.15 Nested deep dive — Media

#### 5.15.1 Pipeline

```text
resumable upload → original object
  → transcode short ladder + poster
  → publish metadata with CDN URLs
  → lifecycle delete at expires_at+grace
```

#### 5.15.2 Delivery

- CDN edge for bytes; Stories API for metadata/ACL.  
- Prefetch budgets by network/battery.  
- Codecs: H.264 baseline; HEVC when capable.

#### 5.15.3 Security

Malware/integrity scan before wide distribution; strip EXIF; rate-limit publishes; short-lived signatures.

### 5.16 Nested deep dive — Scale & deal-breakers

#### 5.16.1 Progressive scale

| Scale | Must |
|-------|------|
| 10× | Hybrid fan-out, CDN, resumable, tray cache |
| 100× | Hierarchical views, regional upload, celeb pull |
| 1,000× | Edge tray cells, smart prefetch budgets |

#### 5.16.2 Deal-breakers

1. Pure write fan-out for all degrees.  
2. Client-only expiry.  
3. Origin-serving all video.  
4. Sync per-view DB writes.  
5. Tray via full graph walk + media listing each open.

---

## 6. Wrap-Up

### 6.1 60-second pitch

> Instagram Stories is an ephemeral mobile media system: resumable uploads, processed media on CDN, metadata with `expires_at`, hybrid fan-out for distribution, ranked tray with unseen-first, prefetching viewer, and async views. Celebrities must not write-fanout to tens of millions. Expiry and ACL are server-enforced.

### 6.2 Deal-breakers

1. Pure fan-out-on-write for all degrees.  
2. Client-only expiry.  
3. Origin-serving all video.  
4. Sync per-view DB writes at peak.  
5. Building tray via full graph + media listing each open without cache.

### 6.3 Scale one-liner

Hybrid fan-out + CDN → hierarchical views + regional media → cellized edge tray/prefetch.

---

## 7. Deeper / Related Interview Questions

### Q1. Why hybrid fan-out?

**Answer:** Average users have manageable follower counts; celebrities would generate impossible write amplification. Hybrid keeps tray reads cheap for the common case and special-cases high degree.

### Q2. How is 24h enforced?

**Answer:** Server stores `expires_at`; all read paths filter; GC deletes; signed URLs expire; client timer is UX only.

### Q3. What happens when upload fails midway?

**Answer:** Resumable sessions with chunk offsets; client retries; publish only after processing completes.

### Q4. How do you design the tray API?

**Answer:** Return ranked authors with cover URL, unseen boolean, latest timestamp, badges (CF). Paginate if needed; usually single page fits.

### Q5. How does prefetch avoid wasting data?

**Answer:** Budgets by network type, battery, user setting; prioritize unseen next; cancel on exit viewer.

### Q6. View counting at celebrity scale?

**Answer:** Batched client events, streaming aggregation, approximate counts OK; full viewer list truncated/sampled.

### Q7. Close Friends implementation?

**Answer:** Audience flag + membership set; fan-out only to members or pull with ACL; careful caching of CF set.

### Q8. Delete before expiry?

**Answer:** Tombstone metadata; remove inbox references async; purge CDN paths; views stop.

### Q9. Mute stories?

**Answer:** Filter authors in tray assembly from mute list; cached with user.

### Q10. Why not store stories in Feed ranking system?

**Answer:** Different TTL, UX (tray/viewer), distribution pattern, and consumption session—specialized store/API clearer.

### Q11. Transcoding strategy?

**Answer:** Few ladders for short video; generate poster; keep process latency low (seconds) for publish UX.

### Q12. Ordering of items in a user’s story?

**Answer:** `created_at` ascending; client taps right to newer; consistent ids.

### Q13. Cross-region story publish?

**Answer:** Metadata home region + global CDN for media; followers worldwide read via nearest edge; inbox fan-out regionalized.

### Q14. How to prevent leaked CDN URLs?

**Answer:** Short-lived signatures keyed to story_id/expiry; optional cookie/token; accept residual risk with short TTL.

### Q15. Poll sticker race conditions?

**Answer:** Per-user vote key idempotent; aggregates via CRDT/adders; show approximate totals.

### Q16. Battery impact?

**Answer:** Limit background refresh; coalesce view posts; careful prefetch; respect OS background modes.

### Q17. Story notifications?

**Answer:** Sparse; rank by affinity; rate-limit pushes; many users rely on tray not push.

### Q18. Consistency of unseen state?

**Answer:** Client sends view receipts; server stores last_seen per author/item; eventual OK if ring clears shortly after watch.

### Q19. What if Graph is slow?

**Answer:** Cached followees/mutes; degrade to last tray snapshot; never show blocked.

### Q20. Media GC correctness?

**Answer:** Lifecycle on objects aligned to `expires_at` + grace; highlights copy-on-write out of TTL path.

### Q21. Can Stories use the same object store as Feed?

**Answer:** Yes shared blob store with different namespaces/lifecycle policies.

### Q22. Abuse: spam stories?

**Answer:** Rate limits, integrity classifiers on media/text, follow spam defenses, report → tombstone.

### Q23. Why async views?

**Answer:** View QPS dwarfs publishes; synchronous durable write per view won’t scale; Kafka aggregates.

### Q24. Client disk cache?

**Answer:** Cache covers + recent segments encrypted; size capped; wipe expired.

### Q25. How do you test ephemeral correctness?

**Answer:** Time-mocked integration tests; expiry boundary; signature expiry; GC verification.

### Q26. Degree threshold tuning?

**Answer:** Measure write QPS vs tray pull latency; set L where hybrid wins; monitor celebs list.

### Q27. Multi-account / creator professional?

**Answer:** Same APIs; optional insights consume aggregates; permissions via roles.

### Q28. Live vs Stories?

**Answer:** Live is streaming protocol + longer session; different system; can deep-link from tray as special unit.

### Q29. Internationalization of stickers?

**Answer:** Metadata-driven sticker packs; client renders text; server stores IDs.

### Q30. What breaks at 100×?

**Answer:** Pure write fan-out remnants, single-region upload, non-hierarchical views, tray stampedes without cache.

### Q31. Read path caching?

**Answer:** Tray cached per user 30–60s; reel cached short; invalidate on publish/delete for author followers asynchronously.

### Q32. How big is a story item payload?

**Answer:** Metadata JSON small; media via CDN; stickers structured; keep reel payload slim.

### Q33. Author insights privacy?

**Answer:** Only author can fetch viewer lists; enforce authz; CF special cases.

### Q34. End-to-end encryption?

**Answer:** Not MVP for IG Stories (server processes media); would break stickers/CDN processing—mention tradeoff if asked.

### Q35. Launch metrics?

**Answer:** Publish success rate, processing latency, tray p99, TTFF, error rate, expiry lag, prefetch waste bytes, view pipeline lag.

### Q36. How do inbox TTLs relate to `expires_at`?

**Answer:** Inbox entries carry the same expiry; Redis/Cassandra TTL or GC scrub prevents expired rings lingering after metadata GC.

### Q37. Why prefetch covers on cold open but not all videos?

**Answer:** Bandwidth/battery — covers are tiny; full segments wait until tray visible / viewer open under budget.

### Q38. How does CF interact with celebrity pull path?

**Answer:** ActiveAuthor may exist, but reel/tray ACL still checks CF membership; non-members never get signed media URLs.

### Q39. What is the viewed-state multi-device issue?

**Answer:** Unseen must be server-side watermarks; phone watch should clear ring on tablet after sync/receipts.

### Q40. Fan-out idempotency key?

**Answer:** `(viewer_id, story_id)` inbox upsert; at-least-once workers safe.

### Q41. Why hierarchical view aggregation?

**Answer:** 100M+ view/s cannot update one global counter row; local→regional→global trees with approximate reads.

### Q42. Ephemeral vs Highlights storage split?

**Answer:** Highlights are explicit copy to non-TTL namespace; default story GC must not delete highlight bytes.

---

## Appendix A — Upload session

```text
UploadSession {id, user_id, expected_size, received, parts[], state, created_at}
```

## Appendix B — Tray JSON sketch

```json
{
  "authors": [
    {"user_id": "u1", "unseen": true, "cover": "https://cdn/...", "ts": 1710000000, "cf": false}
  ]
}
```

## Appendix C — Hybrid fan-out pseudocode

```text
def on_publish(author, item):
  active.set(author, item)
  if degree(author) < L:
    for f in followers(author):
      inbox.add(f, author, item.id, item.expires_at)
  else:
    celebrity_flag.set(author)
```

## Appendix D — Tray assembly

```text
def tray(viewer):
  from_inbox = inbox.list_active(viewer)
  celebs = intersect(following(viewer), celebrity_active_cache)
  authors = filter_mute_block_expiry(from_inbox + celebs)
  return rank(authors, unseen=viewer_seen_state)
```

## Appendix E — TTL GC

```text
periodically:
  delete metadata where expires_at < now - grace
  object store lifecycle mirrors
```

## Appendix F — View event

```text
ViewEvent {viewer_id, story_id, author_id, ts, watched_ms}
```

## Appendix G — Prefetch state machine

```text
IDLE -> TRAY_PREFETCH -> VIEWER_PREFETCH -> CANCEL on navigate away
```

## Appendix H — Codecs

Prefer H.264/AAC wide support; HEVC when client capability; server produces compatible renditions.

## Appendix I — NFR card

```text
Tray p99 < 250ms
TTFF < 500ms
Resumable upload
expires_at enforced
Hybrid fan-out
CDN for media
```

## Appendix J — Failure injection

| Inject | Expect |
|--------|--------|
| Fanout worker down | Celebrity OK; regular retry outbox |
| CDN POP down | Other POPs; origin shield |
| Views Kafka lag | Counts lag; watch UX OK |

## Appendix K — Close Friends cache

```text
CF set cached; invalidate on membership change
Publish CF story uses snapshot membership for fan-out
```

## Appendix L — Watermark / screenshot

Product policy; optional server-side flags; not cryptographically preventable on general purpose OS.

## Appendix M — Worked celeb math

```text
1 celeb publish × 50M fanout writes = disaster
Pull model: 50M followers each tray pull checks cached ActiveAuthor bit — cheap if bloom/batch
```

## Appendix N — Ranking signals

| Signal | Source |
|--------|--------|
| Affinity | Edge rank / interactions |
| Unseen | Receipts |
| Recency | latest item ts |
| Mute | settings |

## Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Tray | Top author rings |
| Reel | One author’s story items sequence |
| Hybrid fan-out | Write for small; pull for large |
| TTFF | Time to first frame |
| CF | Close Friends |

## Appendix P — 30m checklist

1. Ephemeral + mobile constraints.  
2. Hybrid distribution math.  
3. Upload pipeline.  
4. Tray + prefetch.  
5. Views async.  
6. Scale + deal-breakers.

## Appendix Q — Delete propagation

```text
tombstone -> metadata
async: inbox remove, CDN purge, views stop
```

## Appendix R — Security scan

```text
upload -> async AV/malware + integrity classifier before wide distribution
```

## Appendix S — Regional upload

Users upload to nearest region; metadata global logical; media replicated to CDN POPs.

## Appendix T — Metrics dashboard

Publish funnel, processing time, tray latency, TTFF, expiry GC age, view lag, prefetch MB/user/day.

## Appendix U — Highlights schema

```text
Highlight {id, owner, title, cover, item_ids[]} // no TTL
```

## Appendix V — Progressive scale

| Scale | Must |
|-------|------|
| 10× | Hybrid, CDN, resume |
| 100× | View hierarchy, regional |
| 1,000× | Edge tray cells |

## Appendix W — Inbox entry

```text
InboxEntry {author_id, story_id, expires_at, unseen}
TTL'd with expires_at
```

## Appendix X — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Always fan-out” | Celeb math |
| “Always pull” | Tray latency + graph load |
| “Store forever” | Cost + product ephemeral |

## Appendix Y — Client view batching

```text
buffer views; flush on exit / every 5s / N items
idempotent server keys
```

## Appendix Z — Success bar

Smooth mobile watch UX, reliable uploads on bad networks, correct expiry/ACL, and distribution that survives celebrity publish spikes.

---


## Appendix AA — Mobile network classes

| Class | Upload | Prefetch |
|-------|--------|----------|
| Wi-Fi | Full resume | Aggressive within budget |
| 5G/LTE | Full | Moderate |
| Low data mode | Compressed | Covers only |
| Offline | Queue local | None |

## Appendix AB — Celebrity publish sequence

```text
1. Upload+process media
2. Write StoryItem + ActiveAuthor
3. Skip follower inbox fan-out (degree ≥ L)
4. Followers discover via tray pull of ActiveAuthor among followees
5. Views aggregate hierarchically
```

## Appendix AC — Tray ranking worked example

```text
candidates: 40 followees with active stories
unseen=22 → sort unseen first
within unseen: affinity score then recency
return top ~30 rings; rest overflow page rare
```

## Appendix AD — Media object lifecycle

```text
upload://session/... -> originals://stories/{id}/src
 -> renditions://stories/{id}/{q}
 -> CDN URL signed until min(now+1h, expires_at)
 -> GC deletes after expires_at + grace
```

## Appendix AE — Client state machine

```text
APP_OPEN -> fetch tray (cache then network)
TAP_AUTHOR -> open viewer -> prefetch next
EXIT_VIEWER -> flush views -> update unseen local
BACKGROUND -> pause prefetch; optional light tray refresh
```

## Appendix AF — Interview closing lines

```text
"Hybrid fan-out for distribution, server expires_at for ephemerality, CDN for bytes,
async views, and mobile prefetch budgets—that's the IG Stories architecture."
```

## Appendix AG — Stickers data plane

| Sticker | Server state |
|---------|--------------|
| Location | metadata only |
| Poll | votes aggregate |
| Question | response list capped |
| Music | track id ref |

## Appendix AH — TTL correctness checklist

```text
[ ] expires_at set at publish
[ ] tray/reel filter server-side
[ ] signed URL exp ≤ expires_at
[ ] object lifecycle configured
[ ] inbox TTL / GC scrub
[ ] metric expired_but_served ≈ 0
[ ] highlights are copy-on-write out of path
```

## Appendix AI — Fanout decision table

| degree(author) | audience | Action |
|----------------|----------|--------|
| < L | followers | inbox fan-out all followers |
| < L | CF | inbox fan-out CF members only |
| ≥ L | followers | ActiveAuthor pull |
| ≥ L | CF | ActiveAuthor + ACL on reel |

## Appendix AJ — Viewed-state multi-device

```text
Phone watches item → receipt → last_seen[author] updates
Tablet tray refresh → unseen false
Eventual: seconds OK; don’t require sync clock
```

## Appendix AK — Prefetch budget worksheet

```text
Wi-Fi viewer: next 2 items + next author first ≈ 3–6MB
LTE: next 1 item
Low data: covers only
Cancel all on exit viewer / app background
```

*End of Instagram Stories system design.*
