# System Design: Instagram Video Feed (Reels-style)

> **Focus areas:** Short-video ingest · Adaptive bitrate · CDN/edge · Feed ranking hooks · Prefetch · Thumbnails · QPS vs bytes  
> **Style:** End-to-end Meta product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split control-plane vs media-plane, correct bandwidth math, deal-breakers for origin-pulling every play  
> **Interview theme:** Instagram/Reels video feed — upload→process→serve, infinite scroll, personalized candidate mix, mobile-first playback

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

Goal: **bound the product**—an Instagram-style **vertical video feed** (Reels): creators upload short videos; viewers scroll an endless personalized feed with fast start, smooth ABR playback, and engagement actions.

### 1.0 What this is / is not

| Dimension | **Instagram video feed (this doc)** | Not this |
|-----------|--------------------------------------|----------|
| Primary job | Personalized short-video feed + playback | Full IG Stories, Live, or long-form TV |
| Success | Time-to-first-frame, retention, watch % | Perfect archival film grain |
| Data plane | Metadata + ranking + CDN media | Training the ranking model (hooks only) |
| Write path | Upload → transcode → publish | Editing suite / CapCut clone |
| Read path | Feed page + signed media URLs | Arbitrary video search engine MVP |

**Scope statement:** Design Instagram Reels-style video feed: upload/processing, metadata store, candidate generation hooks, feed API, CDN delivery, prefetch, progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Video length? | 15–90s MVP; up to 3 min Phase 1.5 | Transcode profiles sized for short-form |
| F2 | Feed type? | Personalized For You + Following tab | Ranker service; dual candidate sources |
| F3 | Upload? | Mobile camera/gallery; async processing | Upload service + processing queue |
| F4 | Playback? | Autoplay muted; ABR; swipe next | HLS/DASH or fMP4 fragments; prefetch N |
| F5 | Engagement? | Like, comment, share, save, rewatch | Event bus → counters + ranker features |
| F6 | Captions / audio? | Captions Phase 1.5; original audio + music | Asset references; rights checks hooks |
| F7 | Moderation? | Async + reactive; blocklist | Moderation pipeline before wide serve |
| F8 | Creator insights? | Views, watch time basic | Aggregation pipeline |
| F9 | Offline? | Prefetch limited; not full offline MVP | Client cache of next few reels |
| F10 | Regions? | Global; geo-restricted music sometimes | Edge PoPs; rights metadata |
| F11 | Ads? | Mid-feed ads Phase 1.5 | Ad slot in feed mixer |
| F12 | Live / Stories? | Out of MVP | Separate products |

**MVP functional scope:**

1. Authenticated upload of short video + cover; async transcode to multiple bitrates/resolutions.  
2. Publish reel with caption, audio ref, visibility.  
3. Personalized **For You** feed API returning ranked item IDs + playback metadata.  
4. CDN-backed adaptive streaming; signed URLs.  
5. Engagement actions + view heartbeats.  
6. Basic safety: malware/type checks, async moderation states (`pending|ok|restricted`).  
7. Following feed as simpler chronological/ranked blend.

**Out of MVP:**

- Full creative editor, effects marketplace  
- Live video, Shopping tags deep commerce  
- Exact global view counters with strong consistency  
- On-device full model ranking (hooks: lightweight client ranker)  
- DRM for studio content (mention if asked)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-first-frame | Instant feel | p50 < 300–500ms on warm CDN; p99 < 1.5s |
| N2 | Feed API latency | Scroll must not stall | p99 < 100–200ms |
| N3 | Upload durability | No silent loss after ACK | Object store multi-AZ; processing at-least-once |
| N4 | Availability | Consumer critical | 99.9%+ feed; degrade ranking → fallback |
| N5 | Bandwidth efficiency | Mobile data sensitive | ABR; prefetch budget; codec (AV1/HEVC/H.264 ladder) |
| N6 | Freshness of new reel | Creator sees soon | Process p50 < 30–60s for short clips |
| N7 | Global | Multi-region users | Edge media; regional metadata cells |
| N8 | Safety | Don’t viral-amplify violations | Distribution gates on mod state |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Creator uploads 20s video → process → publish → appears to followers / eligible for FY.  
2. Viewer opens Reels → feed page of 10 → prefetch #1–#3 → swipe → seamless.  
3. Like/comment → ack fast → async fanout to counters.  
4. Poor network → ABR drops rung; still plays.  
5. Moderation flags → remove from FY distribution; owner may still see.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Transcode fails | Retry; mark failed; notify creator |
| Partial upload | Resumable upload (TUS/multipart) |
| Viral video thundering herd | CDN; origin shielded; popular cache |
| Ranker timeout | Fallback: following + local trending + cached |
| Deleted reel mid-feed | Client tombstone; skip on next page |
| Copyright music strike | Mute / block distribution per rights |
| Duplicate swipe / double like | Idempotency keys |
| Exhausted candidates | Broaden retrieval; cold-start explore |
| Clock skew view events | Server receive time + client ts capped |
| Region block | Filter at feed mix + CDN token geo |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 50M | 500M | — (mega) | extreme global |
| Peak concurrent viewers | 2M | 20M | 200M | multi-100M |
| Feed requests/s | 100K | 1M | 10M | 100M |
| Video starts/s | 200K | 2M | 20M | 200M |
| Avg bitrate watched | 2 Mbps | 2 Mbps | 1.5–2.5 | codec-improved |
| Uploads/s (peak) | 500 | 5K | 50K | 500K |
| Videos stored | 5B | 50B | 500B | retention tiers |
| Avg mezzanine size | 20 MB | 20 MB | 15–40 | varies |
| CDN egress peak | ~400 Tbps order* | ×10 | ×100 | specialized |
| Engagement events/s | 500K | 5M | 50M | 500M |

\*Interview-order bandwidth: `starts/s × bitrate`; refine with concurrency × bitrate.

**What each jump forces:**

- **10×:** Multi-PoP CDN mandatory; feed fanout caching; async engagement; processing fleet autoscaling.  
- **100×:** Regional metadata cells; ranker isolation; origin shield; popular vs long-tail storage tiers.  
- **1,000×:** Cell-based feed services; hierarchical candidate generation; aggressive codec/bitrate optimization; edge compute personalization lite.

### 1.5 Etc. (Constraints & Assumptions)

- Ranking model training is **out of scope**; we design serving hooks (retrieval → rank → mix).  
- Object storage + CDN exist as building blocks; we design how we use them.  
- Mobile is primary client; web secondary.  
- “Video feed” ≠ Stories ephemeral album.

**Scope statement to repeat back:**

> Design an Instagram Reels-style video feed: resumable upload, async multi-bitrate transcoding, metadata + distribution gates, personalized feed API with ranking hooks, CDN ABR playback with prefetch, engagement event pipeline—scaling through 10× / 100× / 1,000× by splitting control plane from media plane and never serving hot video from origin.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Feed API** | Page of reel metadata | ~100K/s | Stateless feed svc |
| **Media bytes** | ABR segments | ~200K starts × 2 Mb/s | CDN / edge |
| **Uploads** | Object PUTs | ~500/s | Upload + blob |
| **Transcode jobs** | CPU/GPU encode | ~uploads × ladder | Processing fleet |
| **Engagement writes** | Likes/views | ~500K/s | Kafka + counters |
| **Ranker QPS** | Score candidates | ~feed QPS | Ranker / models |

**Anti-pattern:** one “QPS” mixing feed JSON and terabits of video.

### 2.2 Bandwidth math

```text
Peak video starts/s = 200K
If average concurrent watch bitrate 2 Mbps:
  Concurrent viewers ≈ starts × avg_watch_seconds / session_mix
Simpler interview bound:
  Egress ≈ concurrent_viewers × 2 Mbps
Example: 2M concurrent × 2 Mbps = 4 Tbps (order)
CDN absorbs; origin << 1% with high hit ratio
```

### 2.3 Storage math

```text
5B videos × (assume 3 rungs × 8 MB avg served ladder retained) ≈ 120 PB raw order
+ mezzanine + thumbnails + replicas → multi-hundred PB
Cold tier / delete inactive / shorter ladder for low-view → mandatory at scale
```

### 2.4 Feed amplification

```text
Session: 30 reels viewed; feed page size 10 → ~3 feed calls + many segment GETs
Prefetch 2 ahead: segment QPS ≫ feed QPS
Design caches for media first, feed second
```

### 2.5 Transcode cost

```text
Upload 500/s × 3–6 output rungs × 0.5–2× realtime encode
Need elastic workers; priority queue for creator-visible “your reel is ready”
GPU for AV1 optional; H.264/HEVC CPU/GPU mix
```

### 2.6 Metadata QPS

```text
Feed 100K/s × 10 ids = 1M id resolutions/s if naive per-id RPC
→ batch get reel metadata; cache hot reel cards; denormalize creator snippets
```

### 2.7 ABR & segment bandwidth worksheet

```text
Segment duration 2s; ladder bitrates: 0.5 / 1 / 2 / 4 / 6 Mbps
Steady watch at 2 Mbps: 2e6/8 = 250 KB/s per viewer
Prefetch next reel: fetch init (50–150 KB) + first 2–3 segments (~0.5–1.5 MB)
Skip rate 40%: wasted prefetch ≈ 0.4 × 1 MB × starts — cap prefetch budget

Concurrent egress example:
  5M concurrent × 2 Mbps = 10 Tbps CDN — origin with 99% hit ≈ 100 Gbps shields
Interview line: “bytes dominate; feed JSON is rounding error”
```

### 2.8 Client cache & TTFF budget

```text
TTFF target p50 < 500ms, p99 < 1.5s on Wi-Fi
Budget:
  feed card already in memory: 0
  manifest GET (cached PoP): 20–80ms
  init + first media segment: 100–400ms
  decode warm: 50–150ms
Prefetch policy: keep next 1 reel fully primed; next+1 init only on Wi-Fi
On cellular Data Saver: prefetch 0–1; start at lower rung
Device cache: 50–200 MB ring of recent segments; LRU by reel_id
```

### 2.9 Transcode fleet sizing

```text
Uploads 500/s; avg mezzanine 20s video; ladder 4 rungs
CPU encode ~1× realtime per rung → 500 × 4 × 20 ≈ 40K encode-seconds/s
→ ~40K cores if CPU-only naive — hence: GPU, chunked parallel, shorter ladder for low-reach
Priority queues: creator_own_view > following_fanout > cold archive
Storage write amp: raw + mezz + 4 rungs + thumbnails ≈ 6–10× upload bytes briefly
```

### 2.10 Progressive capacity table

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Feed API | 100K/s | 1M/s | regional cells | edge personalize lite |
| CDN egress | ~Tbps | ×10 | multi-CDN | hierarchical PoPs |
| Transcode | elastic | GPU pool | per-region encode | format evolution |
| Metadata | cached SQL | +TAO-like | multi-region | hierarchical cards |
| Engagement | Kafka 0.5M/s | 5M/s | sharded counters | approx + exact hot |

**Anti-patterns (BOTE):** mixing Tbps media into “API QPS”; sync transcode in upload request; prefetching 20 reels on cellular.

---

## 3. High-Level Design

### 3.1 API (control plane)

| Op | Semantics |
|----|-----------|
| `POST /v1/reels/upload_session` | Resumable upload intent → URLs |
| `POST /v1/reels/{id}/complete` | Finish upload → enqueue process |
| `POST /v1/reels/{id}/publish` | Caption, audio, visibility |
| `GET /v1/feed/reels?cursor=&tab=foryou` | Ranked page of reel cards |
| `POST /v1/reels/{id}/engagement` | like/share/skip/view_heartbeat |
| `GET /v1/reels/{id}` | Single reel metadata |
| `DELETE /v1/reels/{id}` | Owner delete / tombstone |

**Reel card (feed item) sketch:**

```text
ReelCard {
  reel_id,
  creator: {id, username, facepile},
  caption,
  duration_ms,
  playback: {manifest_url, poster_url, codecs},
  stats: {like_count_approx},
  mod_state,
  tracking_token
}
```

### 3.2 Data model

| Entity | Store | Notes |
|--------|-------|-------|
| Reel metadata | Distributed SQL / TAO-like | Author, caption, state, audio_id |
| Media pointers | Metadata + object keys | Ladder of renditions |
| User follow graph | Graph store | Following tab |
| Feed session / cursor | Opaque cursor | Avoid deep offsets |
| Counters | Redis / specialized | Eventually consistent |
| Engagement log | Kafka → warehouse | Features / analytics |
| Processing job | Queue + state machine | uploaded→processing→ready→published |

### 3.3 Media formats — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Progressive MP4 single file** | Simple | Poor ABR; wasteful | Tiny MVP demo |
| **HLS / DASH** | ABR, CDN-friendly | Latency to first segment | **Strong default** |
| **RTC / WebRTC** | Ultra-low latency | Overkill for VOD reels | Live only |
| **Custom fMP4 + JSON** | Control | Client complexity | Advanced Meta-like |

**Chosen MVP:** CMAF/fMP4 segments with HLS (and DASH if web needs). Ladder e.g. 360p/540p/720p/1080p.

### 3.4 Feed assembly — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Pure fanout-on-write** | Fast read | Explodes for celebs; bad for FY | Following-only tiny nets |
| **Fanout-on-read** | Flexible | Heavy merge | Following at scale with caps |
| **Retrieval → rank → mix** | Personalization | Ranker dependency | **For You MVP** |
| **Chronological global** | Simple | Poor UX | Not Instagram |

**Chosen:**

1. **Retrieval:** multi-source candidates (following, similarity, trending, creator affinity).  
2. **Rank:** model scores watch-probability / engage.  
3. **Mix:** diversity, author spacing, ads slots, safety filters.  
4. **Fallback:** cached exploratory inventory if ranker fails.

### 3.5 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Media delivery | Multi-PoP CDN | Bandwidth | Origin serves every play |
| Processing | Async queue | Upload UX | Sync transcode in request |
| Feed IDs vs blobs | IDs + signed URLs | Cacheability | Embed raw bytes in feed JSON |
| Counters | Async eventual | Write QPS | Sync tx on every like |
| Ranking | Separate service | Iterate models | Hardcode chronological FY |
| Prefetch | Next 1–3 reels | TTFF | Prefetch 50 (battery/data) |

### 3.6 Planes, SLOs, and deal-breakers

| Plane | SLO focus | Failure isolation |
|-------|-----------|-------------------|
| **Upload/control** | Session create p99 < 200ms | Never block on encode |
| **Processing** | Ready lag p50 < 60s | Queue backlog ≠ feed 500 |
| **Feed metadata** | p99 < 200ms | Ranker timeout → fallback inventory |
| **Media CDN** | TTFF / rebuffer | PoP miss ≠ app server meltdown |
| **Engagement** | Durable async | Counter lag OK |

**Deal-breakers:**
- Serving video bytes from feed monolith  
- Blocking publish on full ladder encode for all rungs before creator preview  
- Fanout-on-write For You to millions  
- Unsigned forever-URLs (leak / undelete failure)  

### 3.7 Feed vs media contract

```text
Feed returns: reel_id, card fields, short-lived signed manifest URL, tracking_token
Media plane: manifest → segment URLs (also signed or cookie/token)
Expiry: 1–6h typical; client refresh card if 403
Delete/tombstone: reject new signatures; CDN TTL drains residual
```

---

## 4. Architecture Diagram

```text
  Creator App                Viewer App
      |                          |
      | upload                   | feed + play
      v                          v
 +----+-----+              +-----+------+
 | Upload   |              | Feed API   |-----> Ranker / Mixer
 | Gateway  |              |            |-----> Candidate services
 +----+-----+              +-----+------+
      |                          |
      v                          v
 +----+-----+              +-----+------+
 | Object   |              | Metadata   |  reel cards, cursors
 | Store    |              | Store      |
 | (raw)    |              +-----+------+
      |                          ^
      v                          |
 +----+-----+                    |
 | Transcode|---- ready ---------+
 | Workers  |---- renditions --> Object Store (ladder)
 +----+-----+
      |
      v
 +----+------------------------------+
 |           CDN / Edge PoPs         |
 |  origin shield → popular cache    |
 +-----------------------------------+
      ^
      | segment GETs (signed)
      |
  Viewer players (ABR + prefetch)

 Engagement: App → Engagement API → Kafka → Counters / Feature log / Moderation
```

**Upload → ready:**

```text
create upload_session
  -> client PUTs chunks to object store
  -> complete -> job=processing
  -> workers: validate -> thumbnails -> ladder encode -> pack HLS
  -> write media pointers -> state=ready
  -> publish -> state=published (mod_state pending/ok)
```

**Feed → play:**

```text
GET /feed/reels
  -> auth → retrieval candidates → rank → mix → page
  -> return cards with short-lived signed manifest URLs
client:
  -> fetch manifest → segments from CDN
  -> prefetch next reel’s init + first segments
  -> send view heartbeats / skip signals
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Raw upload durable** before processing ACK to creator.  
2. **No wide distribution** unless `state=published` and `mod_state` allows.  
3. **Feed never blocks on media bytes** — metadata plane separate.  
4. **Idempotent engagement** (`like` with idempotency key).  
5. **Delete is tombstone-first** — CDN URLs expire; manifests revoked.  
6. **Ranker failure degrades**, does not 500 the whole app if fallback inventory exists.

#### 5.1.2 Processing state machine

```text
uploaded → processing → ready → published
                sync → failed → retry / dead-letter
published → restricted / deleted
```

Exactly-once processing via job id + stateful workers; at-least-once with overwrite-safe outputs.

#### 5.1.3 Playback availability

| Issue | Mitigation |
|-------|------------|
| PoP miss storm | Origin shield; pack popular to more PoPs |
| Bad encode | Health check ladder; reprocess |
| Expired signature | Client refresh card / resign endpoint |
| Partial reel delete | Return 410; client advances |

#### 5.1.4 Consistency

- Like counts: eventual; show optimistic UI.  
- “My new reel visible to me”: read-after-write via owner path / sticky region.  
- FY others: eventual after publish + indexing.

### 5.2 Scalability

#### 5.2.1 Control vs media plane

```text
Control plane QPS: feed + engagement (millions OK with caches)
Media plane: Tbps — must be CDN, never app servers
```

**Boundary rules:** feed handlers never proxy video bytes; engagement never opens object-store for media; transcode workers talk to object store + job DB only.

#### 5.2.2 Hot vs cold videos

| Tier | Policy |
|------|--------|
| Hot | Broad CDN cache; pinned PoPs |
| Warm | Standard TTL |
| Cold | Cheaper storage class; longer TTFF OK |

```text
velocity = views(last 2m) / views(prev 2m)
if velocity > τ AND absolute views > floor:
  mark hot → warm top PoPs; retain higher ladder rungs longer
```

#### 5.2.3 Feed service scale

- Stateless feed workers behind L7 LB  
- Candidate retrieval parallelized with timeouts (e.g. 40ms budget)  
- Metadata batch-get with cache (reel_id → card)  
- Cursor encodes `{session_id, exhaustion offsets, ranker_version}`  

#### 5.2.4 ABR & CDN deep dive

```text
Player: buffer_seconds, bandwidth_est, error rate
Pick highest rung with bitrate ≤ bandwidth × 0.7 and healthy buffer
Downswitch fast on rebuffer; upswitch slow (hysteresis)
CDN cache key = (asset_id, rung, segment); immutable segments → long TTL
Manifests: shorter TTL or always signed
```

| Miss storm cause | Mitigation |
|------------------|------------|
| Viral cold PoP | Predictive warm |
| Manifest churn | Separate policy from segments |
| Origin overload | Shield + coalesce |
| Geo skew | Regional origins / multi-CDN |

#### 5.2.5 Transcoding pipeline deep dive

```text
validate → mezzanine → parallel rung encodes → pack HLS/DASH
  → thumbnails → write pointers → ready
Output keys: (reel_id, ladder_version, rung) — overwrite-safe retries
Partial failure: serve if minimum rung OK; requeue failed rungs
Creator UX: optional fast 360p preview before full ladder
```

#### 5.2.6 Prefetch & skip waste

```text
CURRENT playing; NEXT primed (init+segs); NEXT+1 init-only on Wi-Fi
Skip: cancel NEXT+1; promote NEXT
Budget: max_prefetch_MB_per_session; pause on low battery / Data Saver
```

**Deal-breaker:** prefetching dozens of reels on cellular.

#### 5.2.7 Progressive scale

| Scale | Changes |
|-------|---------|
| 10× | CDN + ladders + async counters |
| 100× | Regional cells for metadata; ranker fleets; shield |
| 1,000× | Hierarchical retrieval; edge personalization lite; storage lifecycle |

| Jump | Forced change |
|------|---------------|
| →10× | Separate media plane; ABR mandatory |
| →100× | Viral warm; ranker cells; storage tiering |
| →1,000× | Multi-CDN; codec evolution; cold delete |

### 5.3 Maintainability

#### 5.3.1 Ladder / codec evolution

- Rendition profiles versioned (`ladder_v4`)  
- Clients declare supported codecs; server picks manifest  
- Dual-publish AV1 + HEVC + H.264 during migration  

#### 5.3.2 Observability

| Metric | SLO use |
|--------|---------|
| TTFF / rebuffer ratio | Playback quality |
| Feed p99 / ranker timeout rate | Scroll health |
| Transcode queue lag | Creator UX |
| CDN hit ratio | Cost / origin safety |
| Mod distribution gate | Safety |
| Prefetch waste ratio | Cost / battery |
| Signed URL 403 rate | Client refresh bugs |

#### 5.3.3 Client concerns (mobile)

- Bitrate capped on cellular; user Data Saver mode  
- Prefetch budget in MB/session  
- Decode warm-up for next player instance  
- Error: skip reel after N failures  

#### 5.3.4 Safety distribution gates

```text
published ∧ mod_state ∈ {ok, pending_limited}
violating → no new signatures; tombstone cards
```

### 5.4 Upload & resumable sessions

```text
upload_session → chunk PUTs → complete(hash) → enqueue process
Idempotent complete; GC abandoned multipart after TTL
```

### 5.5 Engagement & view counting

```text
Heartbeats for ≥50% visible playback; dedupe (viewer, reel, session_bucket)
Counters: Redis approx + reconcile; analytics via Kafka (sampled at scale)
Never block playback on counter durability
```

### 5.6 Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Origin serves plays | CDN + shield |
| Sync full ladder in HTTP | Async jobs |
| Feed embeds bytes | Signed manifests |
| Prefetch ∞ | Budgeted 1–3 |
| Ranker multi-second timeout | 40–80ms + fallback |
| Exact sync likes | Async eventual |
| No tombstone on delete | Revoke signatures |

---

## 6. Wrap-Up

### 6.1 Design summary

Instagram video feed splits **upload/processing/metadata** from **CDN media delivery**. Feed API runs **retrieve → rank → mix** with timeouts and fallbacks. Playback uses **ABR segments**, **signed URLs**, and **bounded prefetch**. Scale is dominated by **bytes and CDN hit ratio**, not JSON QPS.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Personalization vs reliability | Ranker + fallback | Slightly worse relevance under failure |
| Prefetch vs data | 1–3 reels | Occasional waste on skip |
| Exact counters vs QPS | Eventual | Temporary count drift |
| Encode quality vs lag | Fast ladder first | Optional HQ re-encode later |

### 6.3 Deal-breakers

1. Serving hot video from monolith origin.  
2. Synchronous transcode inside upload HTTP.  
3. Putting video bytes in feed API responses.  
4. Strongly consistent global like counters on the like path.  
5. FY feed that hard-fails when ranker is down.

### 6.4 45-minute plan

1. Clarify short-form, FY vs following, ABR, moderation.  
2. Bandwidth + storage math.  
3. Draw upload/process vs feed/CDN planes.  
4. Deep dive ranking hooks + prefetch + CDN.  
5. Scale jumps.  
6. Deal-breakers.

### 6.5 Phase 2

- Ads mixer, shopping, advanced creator analytics  
- On-device ranking features  
- Live cross-post  
- Fine-grained music rights  

---

## 7. Deeper / Related Interview Questions

### Q1. Why CDN is non-negotiable?

**A:** Video egress is Tbps-class. App origins and even single-region object stores cannot economically or latently serve global starts. CDN PoPs provide locality and cache hit absorption.

### Q2. HLS vs progressive download?

**A:** Progressive wastes bandwidth when users swipe away at 20%; poor ABR. HLS/DASH fetch small segments, adapt bitrate, and cache well at edges.

### Q3. How do signed URLs work?

**A:** Feed returns manifest URL with expiry + signature (CDN token). Limits hotlinking and makes delete/revoke feasible when keys rotate / tokens expire.

### Q4. How many videos to prefetch?

**A:** Typically next 1–3. More improves swipe smoothness but burns data/battery and wastes on skips. Tie to network class and Data Saver.

### Q5. Fanout-on-write for Reels FY?

**A:** Poor fit. FY is not a friend graph inbox; candidates come from many retrieval sources. Fanout-on-write still useful for Following tab with celebrity caps (hybrid).

### Q6. How to handle celebrity following fanout?

**A:** Cap write fanout; for megafollowers use pull on read or shared timeline segments. Hybrid push for active online followers only.

### Q7. Ranker timeout strategy?

**A:** Parallel retrieval with per-source deadlines; if ranker exceeds budget, serve lightweight heuristic score or cached exploratory mix; never blank feed.

### Q8. View counting accuracy?

**A:** Define view (e.g. ≥3s or 50% watched). Heartbeats → Kafka → aggregate. Exact real-time global count unnecessary; approximate + periodic reconcile.

### Q9. How do you prevent skipped-reel bandwidth waste?

**A:** Short first segments; don’t prefetch entire video; cancel in-flight fetches on swipe; lower prefetch on poor networks.

### Q10. Transcode ladder selection?

**A:** Cover common mobile resolutions/bitrates; include audio-only? usually A+V. Consider VP9/AV1 for efficiency with H.264 fallback for old devices.

### Q11. Cold start for new users?

**A:** Demographic/explore inventory, popular regional reels, onboarding interest picks; boost diversity until personalization signals exist.

### Q12. Cold start for new creators?

**A:** Limited initial distribution (“seed”), quality gates, similarity to creator’s niche; avoid dumping all new videos into everyone’s FY.

### Q13. Moderation vs viral amplification?

**A:** Distribution tiers: small blast while `pending`; widen when `ok`; immediate pull from indexes on `restricted`. Ranker must read mod_state.

### Q14. Metadata store choice?

**A:** Reel metadata fits distributed SQL or graph+cache. Hot cards in memcache. Media blobs never in SQL.

### Q15. Why cursors not OFFSET?

**A:** Deep OFFSET scans are expensive and unstable as new content arrives. Opaque cursors encode session ranker state / last scores.

### Q16. Rebuffering root causes?

**A:** Bad ABR estimates, tiny buffers, PoP miss, oversized segments, CPU decode stalls. Measure rebuffer ratio by network type.

### Q17. How to detect viral videos quickly?

**A:** Stream aggregate view velocity / unique viewers; when threshold crossed, push object to more PoPs and pin cache.

### Q18. Multi-region metadata?

**A:** Home region per user for writes; feed read local with cross-region candidate fetch; media global via CDN. Avoid synchronous cross-region on like path.

### Q19. Thumbnails / posters?

**A:** Generate during process; serve tiny images from CDN; critical for perceived performance before first frame.

### Q20. Audio / music rights?

**A:** Store `audio_id` with territory rights; filter at mix time; CDN cannot fix rights — control plane must strip ineligible items per viewer country.

### Q21. Client vs server ranking?

**A:** Server does heavy retrieval/rank; client may re-rank with local signals (time of day, battery) lightly. Full on-device FY is Phase 2.

### Q22. Idempotent upload complete?

**A:** `upload_session_id` unique; complete is retry-safe; processing job created once via conditional write.

### Q23. What if object store is down in one AZ?

**A:** Multi-AZ buckets; upload failover; processing reads from durable replica. CDN may still serve cached hot content.

### Q24. Engagement event schema?

**A:** `{user_id, reel_id, type, ts, watch_ms, client, tracking_token}` — token binds to feed impression for training integrity.

### Q25. How do ads fit?

**A:** Mixer inserts ad slots by policy; ads retrieved from ads candidate service with separate SLA; failure skips slot rather than blocking organic feed.

### Q26. Storage lifecycle?

**A:** Keep ladders for hot/warm; expire rarely watched renditions; preserve mezzanine selectively; legal holds separate.

### Q27. Security: IDOR on reel_id?

**A:** AuthZ on private reels; signed URLs bound to reel; do not assume obscurity of IDs; rate-limit metadata scraping.

### Q28. Why separate engagement API from feed API?

**A:** Different SLOs and scale; feeds are read-heavy personalized; engagements are write-heavy fire-and-forget with async pipelines.

### Q29. How does swipe UX drive architecture?

**A:** Optimizes for TTFF and cancel-friendly segment fetching; feed pages prepared ahead; player pool recycling on device.

### Q30. Biggest cost knob?

**A:** CDN egress + encoding. Improve hit ratio, codec efficiency, bitrate ladder, and avoid over-prefetch.

### Q31. How do signed manifests interact with CDN caching?

**A:** Signatures are usually on the URL query or cookie. Prefer signing the manifest with short TTL; segment URLs can use longer-lived tokens or path-style keys CDN can cache. Don’t put unique per-user signatures on every segment if that destroys hit ratio—use edge auth or short session tokens carefully.

### Q32. What is CMAF and why mention it?

**A:** Common Media Application Format — shared fMP4 segments usable by HLS and DASH. One encode pack serves web + mobile players; reduces storage and CDN object sprawl.

### Q33. How do you cap celebrity following fanout?

**A:** Hybrid: write fanout for normal users; for celebs, write to author timeline and read-merge / pull for followers. Cap timeline length; ranker still personalizes FY separately.

### Q34. Rebuffering: client vs CDN vs encode?

**A:** Debug triad: player ABR aggressiveness, PoP miss/RTT, missing ladder rungs / GOP size. Metrics: rebuffer ratio by ASN, rung, and reel age.

### Q35. How do ads insert into Reels?

**A:** Mixer inserts ad slots after ranking organic candidates; ads have their own auction score and frequency caps. Media still CDN; tracking tokens differ. Ranker may score organic only.

### Q36. What if transcode backlog explodes?

**A:** Shed cold/low-priority jobs; ship fast-path 360p; alert on queue lag; autoscale GPU/CPU; never block upload ACK on full ladder.

### Q37. Multi-audio / music rights?

**A:** Store audio_id separately; region-blocked audio → alternate mute or swap track; don’t distribute where license fails. Feed card may omit audio metadata.

### Q38. How does delete propagate to CDN?

**A:** Tombstone metadata first (no new signatures); short TTL drains; optional CDN purge for hot objects; clients advance on 403/410.

### Q39. Feed cursor vs page number?

**A:** Opaque cursor with session + offsets + ranker version. OFFSET pagination reshuffles under personalization and is expensive.

### Q40. Cold start new user FY?

**A:** Exploration inventory, demographic/locale priors, trending pool, onboarding interests. Ranker still scores; retrieval sources shift.

### Q41. How to test playback quality in CI?

**A:** Synthetic encode fixtures; player integration with recorded bandwidth traces; CDN cache-key unit tests; contract tests for signed URL expiry.

### Q42. Progressive 10×/100×/1,000× one-liner?

**A:** 10×: CDN+ABR+async counters. 100×: regional metadata/ranker + viral warm. 1,000×: multi-CDN, lifecycle deletion, edge lite personalization.

### Q43. Anti-patterns to recite?

**A:** Origin bytes, sync encode, feed-embedded media, unbounded prefetch, ranker without timeout fallback, strongly consistent likes on path.

### Q44. Viewability definition for a “view”?

**A:** Product: e.g. ≥3s at ≥50% visible. Heartbeats enforce; dedupe per session. Don’t count autoplay flashes.

### Q45. Why separate engagement API?

**A:** Different SLO, authz, and write amplification; protects feed read path from like storms; enables Kafka fanout cleanly.

---

### Appendix A — NFR card

```text
TTFF p50 < 500ms warm
Feed p99 < 200ms
Upload durable multi-AZ
Ranker fail → fallback mix
CDN hit ratio high for hot
No origin-served hot plays
```

### Appendix B — Rendition ladder example

| Rung | Res | Target bitrate |
|------|-----|----------------|
| r0 | 360p | 0.6 Mbps |
| r1 | 540p | 1.2 Mbps |
| r2 | 720p | 2.0 Mbps |
| r3 | 1080p | 3.5 Mbps |

### Appendix C — Feed response sketch

```json
{
  "items": [
    {
      "reel_id": "R123",
      "creator": {"id": "U9", "username": "ada"},
      "duration_ms": 22000,
      "playback": {"manifest_url": "https://cdn/.../master.m3u8?sig=...", "poster_url": "..."},
      "stats": {"likes": 12044}
    }
  ],
  "next_cursor": "eyJ..."
}
```

### Appendix D — Processing checklist

1. MIME / size validate  
2. Virus / fuzz probe  
3. Thumbnail strip  
4. Encode ladder  
5. Package HLS  
6. Write pointers  
7. Index for retrieval  

### Appendix E — Progressive scale

| Scale | Media | Feed | Process |
|-------|-------|------|---------|
| Baseline | 1 CDN | 1 region | Worker pool |
| 10× | Multi-PoP | Cache cards | Autoscale |
| 100× | Shield + tier | Cells | Regional encode |
| 1,000× | Global fabric | Hierarchical retrieval | Priority + spot |

### Appendix F — Fallback inventory

```text
if ranker_timeout:
  return mix(following_recent, local_popular, explore_seed)
  mark response degraded=true for client metrics
```

### Appendix G — Delete flow

```text
tombstone metadata → remove from indexes → expire signatures
CDN TTL drains; optional purge API for viral deletes
```

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| ABR | Adaptive bitrate streaming |
| TTFF | Time to first frame |
| Ladder | Set of encoded renditions |
| Mixer | Policy layer after rank scores |
| Origin shield | Cache tier protecting storage |

### Appendix I — 30m checklist

1. Clarify Reels MVP scope.  
2. Bytes vs QPS math.  
3. Draw dual planes.  
4. Retrieval-rank-mix + CDN.  
5. Scale + deal-breakers.

### Appendix J — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Store videos in DB” | Blobs in object store |
| “Rank in SQL ORDER BY” | Not personalized FY |
| “Exact likes sync” | Won’t take write QPS |
| “Prefetch 50” | Data/battery blowup |

### Appendix K — Client player state

```text
current playing
prefetched next (init+seg0)
cancel on swipe
report watch_ms on leave
```

### Appendix L — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| CSDS / object storage | Blobs |
| TAO-like | Social metadata |
| CDN (FB CDN / external) | Media |
| Ranking platform | FY scores |

### Appendix M — Worked bandwidth example

```text
5M concurrent × 1.8 Mbps ≈ 9 Tbps egress order
At 95% CDN hit, origin 5% → still huge; shields + popular push critical
```

### Appendix N — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Like count exact? | No, eventual |
| Owner sees own reel? | Yes, RYW path |
| Global FY same reel order? | No, personalized |

### Appendix O — Safety distribution gates

| mod_state | Following | FY |
|-----------|-----------|-----|
| pending | limited | limited seed |
| ok | yes | yes |
| restricted | no | no |

### Appendix P — Cursor contents

```text
{session_id, ranker_version, seen_bloom_or_hash, source_offsets, ts}
```

### Appendix Q — Upload resumable

```text
POST session → chunk PUT with offsets → complete
Retry safe; checksum per chunk
```

### Appendix R — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | CDN multi-PoP, async counters |
| 100× | Cells, shield, viral push |
| 1,000× | Hierarchical retrieval, lifecycle tiering |

### Appendix S — Interview whiteboard script

1. Clarify Reels length, FY vs Following, ABR, moderation.  
2. Split **control plane** (feed JSON) vs **media plane** (Tbps).  
3. Bandwidth: concurrent × bitrate.  
4. Upload → object store → async ladder → publish.  
5. Feed: retrieve → rank → mix → signed manifests.  
6. Prefetch 1–3; cancel on swipe.  
7. Engagement async; counters eventual.  
8. Ranker timeout → fallback inventory.  
9. Viral → edge push / shield.  
10. 10×/100×/1,000× + deal-breakers.

### Appendix T — Client prefetch state machine

```text
states: IDLE, LOADING_CURRENT, PREFETCH_NEXT, ERROR_SKIP
on_swipe_up:
  cancel unused prefetches for previous
  promote prefetched next -> current
  start prefetch for new next
on_bandwidth_poor:
  reduce prefetch depth to 1; cap max rung
```

### Appendix U — Manifest signing

```text
manifest_url = cdn_host + path + "?" +
  "exp=" + epoch +
  "&reel_id=" + id +
  "&sig=" + hmac(server_secret, exp|reel_id|path)
TTL short (e.g. 1–6h); refresh via feed card reload
```

### Appendix V — Engagement event types

| Type | Meaning |
|------|---------|
| impression | Card shown |
| video_start | Playback began |
| watch_heartbeat | Every N seconds |
| skip | Swiped away early |
| like / share / comment | Social |
| video_complete | Finished / looped |

### Appendix W — Capacity worksheet

```text
peak_concurrent_viewers = ______
avg_bitrate_mbps = ______
egress_tbps ≈ concurrent × bitrate / 1e6
feed_qps = ______
metadata_gets ≈ feed_qps × page_size × (1 - cache_hit)
uploads_per_sec = ______
transcode_workers ≈ uploads × ladder × encode_seconds / parallel_efficiency
```

### Appendix X — FAQ rapid-fire

| Q | A |
|---|---|
| Store video in SQL? | No — object store |
| Fanout-on-write FY? | No — retrieval/rank |
| Exact likes? | Eventual |
| Prefetch 50? | Wasteful |
| Sync transcode? | No |

### Appendix Y — Failure inject tests

| Inject | Expect |
|--------|--------|
| Ranker 100% timeout | Fallback mix, non-empty |
| CDN PoP down | Failover PoP / origin shield |
| Transcode DLQ growth | Alert; creator notify |
| Manifest sig expired | Client refresh card |

---

*End of Instagram Video Feed system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Architecture change | What you measure |
|------|---------------------|------------------|
| →10× | CDN mandatory; ABR ladder; async engagement; signed URLs | TTFF, CDN hit %, encode lag |
| →100× | Regional metadata/ranker cells; origin shield; viral warm path | Cross-AZ miss storms, ranker timeout % |
| →1,000× | Multi-CDN; storage lifecycle/delete; edge lite personalization; codec evolution | $/watch-hour, cold TTFF, safety gate lag |

### 8.2 Feed plane vs media plane (recap)

```text
Feed plane: auth, retrieve, rank, mix, cursors, cards, tracking tokens
Media plane: manifests, segments, ABR, CDN, signatures, PoPs
Never couple request threads across planes
Engagement plane: likes/views → Kafka → counters (eventual)
Processing plane: upload → validate → encode → ready → publish
```

### 8.3 ABR decision cheatsheet

```text
if buffer < 2s: downswitch urgently
elif buffer > 10s and bandwidth_est > next_rung / 0.7: upswitch
else: hold
On Data Saver: cap max rung; prefetch ≤ 1
On Wi-Fi + charging: allow NEXT+1 init prefetch
```

### 8.4 Interview anti-pattern rapid list

1. Monolith origin video bytes  
2. Sync transcode in upload handler  
3. Fanout-on-write For You  
4. Prefetch 20 reels on LTE  
5. Ranker without deadline/fallback  
6. Strongly consistent global like counter on write path  
7. Forever unsigned CDN URLs after delete  

### 8.5 Worked TTFF example

```text
Card in memory: 0ms
Manifest edge hit: 40ms
Init+seg0 at 2Mbps, 400KB: ~1.6s on weak link → choose lower rung (~150KB) ≈ 0.6s
Decode: 80ms
Total ~0.7–1.0s when ABR picks correctly; p99 dominated by misses + high RTT
```

### 8.6 Control-plane API latency vs media TTFF

```text
Feed p99 200ms can still feel broken if TTFF is 3s — separate SLOs
Own dashboards: feed_latency, ranker_timeout_rate, ttff, rebuffer_ratio, cdn_hit
Capacity plans must list both JSON QPS and Gbps egress
Creator path SLO: upload complete → ready p50, not only viewer TTFF
```

### 8.7 Following vs For You retrieval note

```text
Following: graph pull / hybrid fanout with celeb carve-outs
For You: multi-source retrieval → rank → mix (this doc’s center)
Don’t design FY as chronological global firehose
Safety/mod gates apply before wide distribution, not after viral CDN warm
```

### 8.8 Signed URL refresh

```text
On 403/expired: re-fetch reel card or /resign endpoint
Do not infinite-loop resign; advance to next reel after N fails
Delete/tombstone → 410; client removes from session playlist
```

