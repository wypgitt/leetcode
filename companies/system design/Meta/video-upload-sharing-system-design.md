# System Design: Video Upload & Sharing Platform (Meta)

> **Focus areas:** Resumable upload · Transcoding ladders · Adaptive streaming · CDN · Sharing graph · Feed/Stories/Reels hooks · Processing async · Thumbnails · Integrity  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split upload/process/serve/share planes; correct ABR math; deal-breakers for “sync transcode in request path” and “origin serves all watch bytes”  
> **Interview theme:** Meta media platform — reliable mobile/web upload to shareable watchable video at social scale

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

Goal: **bound the product**—a **Video Upload & Sharing** system: users upload video from mobile/web, the platform processes into streaming renditions, stores & delivers via CDN, and enables sharing to feed/stories/messages/link with privacy controls.

### 1.0 What this is / is not

| Dimension | **Video upload/sharing (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Ingest → process → serve → share | Full For You recommender (hooks) |
| Success | Reliable upload; fast start play; correct ACL | Hollywood mezzanine archive |
| Processing | Async transcode + thumbs | Sync in HTTP upload |
| Delivery | ABR (HLS/DASH) over CDN | BitTorrent P2P MVP |
| Sharing | Social targets + links | Email SMTP product |

**Scope statement:** Design Meta-style video upload, processing, CDN playback, and sharing with progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Clients? | Mobile + web | Resumable upload; codec caps |
| F2 | Max size/duration? | e.g. 4GB / 60–240 min product-dependent; Reels shorter | Quotas; chunking |
| F3 | Playback? | Adaptive streaming start fast | ABR ladder + packaging |
| F4 | Sharing? | Feed post, story, DM, copy link | Share graph + ACL |
| F5 | Privacy? | Public / friends / private / unlisted link | Authz on play URL issue |
| F6 | Processing UX? | Upload then “processing…” then ready | States machine |
| F7 | Thumbnails? | Auto + user pick | Thumb pipeline |
| F8 | Edits? | Trim/cover Phase 1.5 | Re-process subset |
| F9 | Integrity? | Copyright/NSFW/malware | Async scanners |
| F10 | Analytics? | Views, watch time | Event pipeline |
| F11 | Download? | Optional per privacy | Separate authz |
| F12 | Live? | Out of MVP | Distinct system |

**MVP functional scope:**

1. Create upload session; chunked resumable upload to blob store.  
2. Async processing: validate, transcode multi-bitrate, package HLS/DASH, thumbnails.  
3. Video entity with state: `uploading|processing|ready|failed|blocked`.  
4. Playback API issues signed manifest/segment URLs after ACL.  
5. Share to feed/DM/link with audience.  
6. Delete / revoke shares.  
7. Basic integrity scanning before wide distribution.  
8. View playback events.

**Out of MVP:**

- Live streaming  
- Full creator monetization  
- Multi-audio dubbing tracks deep  
- Client-side end-to-end encrypted video that server cannot process

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Upload reliability | Bad networks OK | Resume; ≥99% eventual success |
| N2 | Processing latency | Short videos minutes | p50 < 1–3 min for Reels-length; longer proportional |
| N3 | Startup play | Fast | p99 TTFF < 1–2s with CDN |
| N4 | Availability playback | High | 99.9% via CDN |
| N5 | Durability originals | High | Multi-AZ object store |
| N6 | Security | No unauthorized watch | Signed URLs + ACL |
| N7 | Cost | Transcode+CDN dominate | Ladder wisely; cache |
| N8 | Scale | Social | Queue workers; CDN |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Mobile upload 30s → process → ready → share to Feed → friends watch ABR.  
2. Web upload resume after disconnect.  
3. Private video shared via DM only.  
4. Author deletes → playback revoked.  
5. Integrity blocks → state `blocked`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Corrupt file | Fail processing; user retry |
| Unsupported codec | Transcode from best effort / reject |
| Extremely long video | Queue priority lower; quota |
| Hot video viral | CDN cache; origin shield |
| Processing backlog | UX still “processing”; scale workers; priority for short |
| Share then later private | Re-check ACL on play |
| Link leak | Signed URL expiry; auth gate for non-public |
| Partial chunk reorder | Session assembler enforces |
| Thumbnail race | Default until ready |
| Region restriction | Manifest issue checks geo policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Uploads / day | 50M | 500M | 5B | cells |
| Peak upload Gbps | 1 Tbps | 10 | 100 | multi-region |
| Videos stored | 10B | 100B | 1T | cold tiers |
| Peak watch starts / s | 100K | 1M | 10M | 100M |
| Transcode CPU/GPU hours / day | huge | ×10 | ×100 | spot fleets |
| Avg ladder renditions | 4–6 | 4–6 | 3–7 adaptive | per class |
| Share ops / s | 20K | 200K | 2M | 20M |
| CDN egress | multi-Tbps | ×10 | ×100 | global POPs |

**What each jump forces:**

- **10×:** Upload edge regions; job queues by duration class; CDN mandatory.  
- **100×:** GPU/ASIC transcode fleet; packaging cells; hierarchical analytics.  
- **1,000×:** Per-region media planes; aggressive cold storage; title-specific caches.

### 1.5 Etc. (Constraints & Assumptions)

- Object storage + CDN exist.  
- Feed/DM systems consume share APIs.  
- Not designing full ranking of Reels For You—only upload/serve/share.  
- DRM optional Phase 2 for licensed content.

**Scope statement to repeat back:**

> Design a video upload and sharing platform: resumable ingest, async transcode/package to ABR, CDN playback with ACL-signed access, social sharing targets, integrity gates, and progressive scale across upload regions and processing fleets.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Plane |
|-------|-------|
| Upload bandwidth | Edge ingest |
| Transcode compute | Worker fleets |
| Manifest/segment reads | CDN |
| Metadata QPS | Video service |
| Share writes | Social integration |
| Analytics events | Streaming |

### 2.2 Upload math

```text
50M uploads/day × 40MB avg = 2 EB/day? Wait: 50e6 × 40e6 = 2e15 bytes = 2 PB/day
Peak factor 10× average → ingest capacity planning multi-Tbps globally
Chunk 8MB; session state in Redis/DB
```

### 2.3 Transcode amplification

```text
1 input → 5 renditions ≈ 2–3× total stored vs mezzanine carefully managed
CPU: 30s video might take 0.5–2× realtime per rendition depending on codec
Must be async; never block upload ACK on all ladders
Fast-start: produce low ladder first for early preview
```

### 2.4 Playback bandwidth

```text
100K starts/s × 1 Mbps avg = 100 Gbps (low); viral peaks much higher → CDN
```

### 2.5 Storage

```text
10B videos × 100MB avg ladder sum = 1 ZB raw fantasy → reality: size tiers, lifecycle, shorter form dominant
Plan lifecycle: hot SSD/CDN, warm object, cold glacier-like for old private
```

### 2.6 Early publish optimization

```text
Upload complete → validate → transmux/fast 360p → state ready_partial
Full ladder later → ready
Share allowed at ready_partial with limited quality
```

### 2.7 Resumable upload session math

```text
Chunk 8MB; 400MB video → 50 chunks
Mobile loss rate: expect retries on 5–20% chunks
Session state: offsets bitmap in Redis/DB; TTL days
Complete requires checksum match — else requeue missing ranges
Peak 50M uploads/day / 86400 ≈ 580/s avg; ×10 peak ≈ 6K sessions/s completing
```

### 2.8 Processing pipeline parallel width

```text
After probe: thumb + 360p serial-ish for ready_partial
Then parallel xcode 480/720/1080 (worker pool)
Package HLS/DASH per rendition
Integrity on frames can overlap late ladders
Queue lag SLO by class: short < 5 min p95
```

### 2.9 Sharing graph write amp

```text
Share by reference: 1 row ShareEdge + 1 Feed post pointer — not copy blob
Viral video: 1M shares × 100MB copy = 100 PB fantasy — deal-breaker
Playback always re-checks ACL ∩ share grant
```

### 2.10 CDN vs origin

```text
100K starts/s × 2 Mbps = 200 Gbps egress
Origin capacity maybe low Tbps shared — need HIT ratio >95% on popular
Immutable content-hash segments → long cache TTL
```

### 2.11 Progressive media plane

| Scale | Ingest | Process | Serve | Share |
|-------|--------|---------|-------|-------|
| Base | Resumable | Async queue | CDN ABR | Ref ids |
| 10× | Regional edge | Priority queues | Origin shield | Feed/DM/link |
| 100× | Multi-region | GPU fleets | Prefetch POPs | Integrity gate |
| 1,000× | Media cells | ASIC/AV1 selective | Cold lifecycle | Graph at cell |

### 2.12 BOTE anti-patterns

| Anti-pattern | Failure |
|--------------|---------|
| Sync full ladder in upload HTTP | Timeouts; battery; retries |
| Origin serves all watches | Tbps melt |
| Blob copy per share | Storage explosion |
| Forever-valid private URLs | ACL bypass |

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/videos` | Create video id + upload session |
| `PUT /v1/videos/{id}/chunks` | Resumable bytes |
| `POST /v1/videos/{id}/complete` | Close upload; enqueue process |
| `GET /v1/videos/{id}` | Metadata + state |
| `GET /v1/videos/{id}/playback` | Signed manifests if ACL ok |
| `POST /v1/videos/{id}/share` | target_type: feed\|dm\|link |
| `DELETE /v1/videos/{id}` | Tombstone + revoke |
| `POST /v1/videos/{id}/thumb` | Select thumb |

### 3.2 State machine

```text
created -> uploading -> uploaded -> processing -> ready
                              \-> failed
processing / ready -> blocked (integrity)
any -> deleted
ready -> ready (ladder upgraded)
```

### 3.3 Processing pipeline — Why X over Y

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Sync transcode in upload | Simple | Timeouts; mobile waits | Deal-breaker |
| Async queue | Scales; UX honest | Complexity | **MVP** |
| Client-only pre-encode | Saves server | Fragmentation; cheating | Assist only |
| One rendition | Cheap | Bad UX networks | No |

**Chosen:** Async multi-stage: validate → poster/fast ladder → full ABR → package → integrity → notify.

### 3.4 Delivery — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Progressive MP4 only | Simple | Poor adaptivity |
| **HLS/DASH ABR** | Industry standard | Packaging cost |
| WebRTC VOD | Low latency | Overkill VOD |
| P2P | Saves CDN | NAT/complexity MVP |

**Chosen:** HLS (mobile) + DASH (web) from same renditions; CDN cached segments.

### 3.5 Sharing — Why X over Y

| Target | Mechanism |
|--------|-----------|
| Feed | Create post referencing `video_id` |
| DM | Attach video_id in message; ACL recipients |
| Link | Unlisted token mapped to video; rate-limit |
| Download | Optional authorized bytes |

**Deal-breaker:** copying raw bytes into every share target (dedupe by reference).

### 3.6 Why X over Y summary

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Upload | Resumable chunks | Mobile | Single shot PUT |
| Process | Async staged | Latency/cost | Sync all ladders |
| Serve | CDN ABR | Scale | Origin all watches |
| Share | Reference ids | Dedupe | Duplicate blobs per share |
| ACL | Check at playback issue | Security | Public CDN forever URLs |
| Integrity | Async gate | Trust | Share unscanned forever |

### 3.7 Expanded HLD tradeoffs

| Axis | A | B | Pick |
|------|---|---|------|
| Early UX | Wait full ladder | ready_partial | **ready_partial** |
| Packaging | JIT | Pre-package | Pre-package MVP |
| Share | Copy blob | Reference video_id | **Reference** |
| Private play | Long-lived URL | Signed + acl_ver | **Signed** |
| Queues | Single FIFO | Class by duration | **Classes** |

**Anti-patterns:** sync xcode; origin-all-bytes; blob-per-share; forever private URLs.

---

## 4. Architecture Diagram

```text
  Mobile/Web Client
       |  chunks
       v
  +--------------------+         +------------------+
  | Upload Edge        |-------->| Object Store     |
  | (regional)         |         | originals        |
  +----------+---------+         +--------+---------+
             | complete                    |
             v                             v
  +--------------------+         +------------------+
  | Video Metadata Svc |         | Processing Queue |
  | state machine      |<------->| (Kafka / SQS)    |
  +----------+---------+         +--------+---------+
             |                             |
             |                             v
             |                   +------------------+
             |                   | Workers:         |
             |                   | validate, xcode, |
             |                   | package, thumbs, |
             |                   | integrity        |
             |                   +--------+---------+
             |                             |
             |                             v
             |                   +------------------+
             |                   | Rendition Store  |-----> CDN --> Players
             |                   | HLS/DASH segs    |
             |                   +------------------+
             v
  +--------------------+         +------------------+
  | Share Service      |-------> | Feed / Chat /    |
  | ACL + targets      |         | Link token store |
  +--------------------+         +------------------+

  Playback: Client -> Playback API (ACL) -> signed manifest URLs -> CDN segments
  Analytics: Player events -> Kafka -> aggregates
```

**Upload path:**

```text
create video -> upload chunks to nearest edge -> assemble/complete
  -> enqueue processing -> update state
```

**Process path:**

```text
validate codec/size
  -> extract poster + preview ladder (priority)
  -> mark ready_partial
  -> full ladders + package
  -> integrity
  -> ready / blocked
```

**Share + play path:**

```text
share(video_id, target, audience)
play: authz(viewer, video) -> sign m3u8/mpd + segment cookies -> CDN
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No playback URLs without ACL check** (except true public with still-expiring signatures).  
2. **State machine monotonic** with explicit transitions; idempotent complete.  
3. **Original durable** before processing ack.  
4. **Delete revokes** signatures via token version / denylist.  
5. **Integrity block prevents** further distribution boost (and can hard deny).

#### 5.1.2 Upload integrity

```text
checksum per chunk + whole file
retry chunk on mismatch
complete only if size/checksum match
```

#### 5.1.3 Processing retries

Poison video → DLQ after N tries; user-visible failed; ops replay tools.

#### 5.1.4 Exactly-once share?

Idempotency-Key on share creates one post/message attachment.

### 5.2 Scalability

#### 5.2.1 Regional ingest

Upload to nearest region to cut RTT; metadata global; originals may replicate asynchronously to processing region.

#### 5.2.2 Queue classes

| Queue | Priority |
|-------|----------|
| Short (<60s) | High |
| Standard | Medium |
| Long | Low |
| Reprocess | Bulk |

#### 5.2.3 CDN strategy

```text
Edge cache segments (immutable by content-hash URL)
Origin shield
Packager or pre-packaged segments in object store
Cache-Control long for hashed segments; short for manifests if needed
```

#### 5.2.4 Hot video

Prefetch popular to more POPs; higher cache TTLs; rate-limit origin.

#### 5.2.5 Progressive scale map

| Scale | Must |
|-------|------|
| 10× | Regional upload; CDN; async xcode |
| 100× | GPU fleets; priority queues; analytics hierarchy |
| 1,000× | Media cells; cold tier; codec ASICs |

### 5.3 Maintainability

- Codec capability matrix versioned.  
- Pipeline step DAGs observable.  
- Cost dashboards per minute processed.  
- Feature flags for new codecs (AV1) gradual.  
- Clear APIs for Feed/Chat consumers.

### 5.4 ABR ladder design

```text
Example short-form ladder:
  360p 600kbps
  480p 1000kbps
  720p 2500kbps
  1080p 4500kbps
Long-form may add 240p and 1440p selectively
Audio AAC 128kbps
```

Generate lowest first for preview.

### 5.5 Packaging

Pre-package HLS segments to object store (simpler CDN) vs just-in-time packager (storage savings). MVP: pre-package for popular formats; JIT optional later.

### 5.6 ACL & signed URLs

```text
playback token: {video_id, viewer_id, exp, acl_ver, sign}
manifest lists segment URLs with same token or cookie
on privacy change: bump acl_ver → old tokens fail
```

### 5.7 Sharing graph

```text
ShareEdge {video_id, target_type, target_id, sharer_id, audience_snapshot, ts}
Feed/Chat stores references; playback always re-checks current video ACL ∩ share grant
```

### 5.8 Thumbnails

Sample N frames; aesthetic score; user override; store JPEG/WebP; return in metadata.

### 5.9 Integrity pipeline

| Scanner | When |
|---------|------|
| Malware/AV | After upload |
| NSFW classifier | After preview frames |
| Copyright / matching | Async; may block later |
| Spam signals | On share velocity |

Wide Feed distribution waits for minimum integrity; DM to self might be looser—product choice.

### 5.10 Analytics

Player sends `play`, `progress`, `complete`, `quality_switch`. Aggregate watch time; never block playback on analytics.

### 5.11 Failure UX

| State | UX |
|-------|-----|
| uploading | progress bar |
| processing | placeholder scrub |
| ready_partial | play low quality |
| failed | retry upload |
| blocked | policy message |

### 5.12 Cost controls

- Limit max resolution by tier.  
- Don’t keep all originals forever.  
- AV1 for storage/CDN savings when clients allow.  
- Deduplicate identical uploads via hash (careful with privacy).

### 5.13 Nested deep dive — Resumable upload

#### 5.13.1 Session lifecycle

```text
POST /videos → {video_id, upload_session_id, chunk_size, upload_token}
PUT chunks with offset + Content-MD5
POST complete {checksum, size} → state uploaded → enqueue process
```

| State | Meaning |
|-------|---------|
| created | id minted |
| uploading | chunks arriving |
| uploaded | checksum OK; immutable original |
| abandoned | session TTL expired |

#### 5.13.2 Chunk protocol details

```text
Idempotent PUT at offset: overwrite OK if MD5 matches
Gap tracking: bitmap / list of received ranges
Resume: GET session → next missing ranges
Auth: upload_token bound to (user_id, video_id); short-lived renew
```

#### 5.13.3 Regional edge

```text
geoDNS → nearest upload edge → regional object store
Reduces RTT for mobile; processing may pull cross-region
```

#### 5.13.4 Failure UX

| Failure | Client action |
|---------|---------------|
| Chunk timeout | Retry same offset |
| Token expiry | Refresh upload token |
| Checksum fail on complete | Re-upload missing/bad ranges |
| Network offline | Local queue; OS background upload |

**Deal-breaker:** single monolithic PUT with no resume on mobile.

### 5.14 Nested deep dive — Processing pipeline

#### 5.14.1 DAG

```text
validate/probe
  -> poster + fast 360p (+ transmux) → ready_partial   # priority
  -> parallel: 480p, 720p, 1080p, ...
  -> package HLS + DASH (content-hash segment names)
  -> integrity scanners (AV, NSFW, copyright…)
  -> ready | blocked | failed
```

#### 5.14.2 Queue classes

| Queue | SLO example | Workers |
|-------|-------------|---------|
| Short (<60s) | p95 < 5 min | High priority autoscaled |
| Standard | looser | Medium |
| Long | best effort | Spot/batch |
| Reprocess | bulk | Off-peak |

#### 5.14.3 Idempotency & poison

```text
worker processes video_id at state uploaded/processing
steps checkpointed; safe retry
N fails → DLQ + state failed; ops replay
```

#### 5.14.4 Early play

`ready_partial` allows playback/share at limited quality while full ladder finishes — critical UX.

#### 5.14.5 Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| Sync full ABR in upload request | Timeouts |
| One rendition only | Bad QoE |
| No queue classes | Reels stuck behind long uploads |

### 5.15 Nested deep dive — Sharing graph

#### 5.15.1 Model

```text
Video (canonical bytes + ACL)
ShareEdge {video_id, target_type, target_id, sharer_id, audience_snapshot, ts, idempotency_key}
FeedPost / Message / LinkToken reference video_id — never duplicate blob
```

#### 5.15.2 Targets

| Target | Write | Play authz |
|--------|-------|------------|
| Feed | Create post + ShareEdge | viewer ∩ video ACL ∩ post audience |
| DM | Attach in thread | thread recipient ∩ video ACL |
| Link | Unlisted token | valid token ∧ not revoked ∧ ACL |
| Download | Optional | separate capability |

#### 5.15.3 Revocation

```text
privacy tighten OR delete OR integrity block
  → bump video.acl_ver
  → old signed URLs fail
  → shares render unavailable
```

#### 5.15.4 Viral share math

```text
1 video × 1M shares = 1M edges + feed refs OK
1 video × 1M blob copies = catastrophic
```

#### 5.15.5 Integrity vs share

Wide Feed distribution waits for minimum integrity; DM-to-self may be looser — product choice documented.

### 5.16 Nested deep dive — Scale, tradeoffs, deal-breakers

#### 5.16.1 Expanded HLD tradeoffs

| Axis | A | B | Pick |
|------|---|---|------|
| Package | Pre-package segments | JIT packager | Pre-package MVP |
| Preview | Wait full ladder | ready_partial | **ready_partial** |
| ACL | Forever CDN URL | Signed + ver | **Signed + ver** |
| Share | Copy bytes | Reference id | **Reference** |

#### 5.16.2 Progressive scale

| Scale | Must |
|-------|------|
| 10× | Regional resumable upload; CDN; async xcode |
| 100× | GPU fleets; priority queues; origin shield |
| 1,000× | Media cells; cold lifecycle; selective AV1/ASIC |

#### 5.16.3 Deal-breakers

1. Synchronous full transcode on upload HTTP.  
2. Origin serves all watch traffic.  
3. Forever-valid URLs for private video.  
4. Duplicating blobs per share.  
5. No resumable upload on mobile.

---

## 6. Wrap-Up

### 6.1 60-second pitch

> Users upload via resumable regional edge into durable object storage; async workers validate, produce fast preview then full ABR ladders, package for HLS/DASH, and run integrity checks. Playback always authorizes then signs CDN URLs. Shares reference `video_id` into Feed/DM/link systems. Scale with queues, CDN, and media cells—never sync-transcode on the upload request.

### 6.2 Deal-breakers

1. Synchronous full transcode in upload HTTP.  
2. Serving all watch traffic from origin.  
3. Forever-valid public URLs for private videos.  
4. Duplicating blob per share.  
5. No resumable upload on mobile.

### 6.3 Scale one-liner

Regional resumable ingest + async ladders → GPU fleets + CDN shields → media cells + cold lifecycle.

---

## 7. Deeper / Related Interview Questions

### Q1. Why resumable uploads?

**Answer:** Mobile networks drop; large files; chunk checksums allow continue without restarting multi-hundred MB transfers.

### Q2. Why async processing?

**Answer:** Transcoding exceeds request timeouts and user patience for waiting online; also enables prioritization and retries.

### Q3. Explain ABR.

**Answer:** Multiple bitrates; player switches based on bandwidth/buffer; improves startup and reduces rebuffer vs single high MP4.

### Q4. HLS vs DASH?

**Answer:** Both ABR; HLS ubiquitous on iOS; DASH common on web/Android stacks; generate both from same encodes.

### Q5. How do signed URLs protect private video?

**Answer:** Playback API checks ACL then issues short-lived signatures; segment URLs unusable after expiry; bump version on revoke.

### Q6. Fast publish UX?

**Answer:** Produce low-res transmux quickly → `ready_partial` → allow play/share while full ladder finishes.

### Q7. How to handle viral traffic?

**Answer:** CDN caching of immutable segments, origin shield, prefetch popular, scale metadata horizontally.

### Q8. Where does integrity sit?

**Answer:** Async after frames available; can leave `processing` or allow limited distribution until scan; block on severe findings.

### Q9. Storage lifecycle?

**Answer:** Hot for recent/viral; warm; cold for old; delete originals per policy; keep compressed ladders selectively.

### Q10. Codec strategy?

**Answer:** H.264 baseline compatibility; AAC audio; add VP9/HEVC/AV1 as enhanced renditions by client caps.

### Q11. How do Feed and Video services integrate?

**Answer:** Feed post stores `video_id` + cover; renderer calls playback API; separation of concerns.

### Q12. Idempotent complete upload?

**Answer:** `complete` with checksum; if already uploaded, return same state; workers dedupe by video_id.

### Q13. Multi-region processing?

**Answer:** Process near data; replicate renditions to CDN origins globally; metadata home cell.

### Q14. Thumbnail selection?

**Answer:** Auto candidate frames + model score; user picks; store override.

### Q15. Rebuffering metrics?

**Answer:** Client QoE: startup time, rebuffer ratio, bitrate; guide ladder and CDN.

### Q16. Copyright claims after ready?

**Answer:** Transition to `blocked` or mute audio; stop recommending; notify; shares may show unavailable.

### Q17. Why content-hash segment URLs?

**Answer:** Immutable caching; safe long TTL; updates create new hashes.

### Q18. DRM needed?

**Answer:** For licensed/premium content Phase 2; user-generated social often Widevine/FairPlay optional; MVP signed ACL often enough.

### Q19. Spam share loops?

**Answer:** Rate limits; integrity; graph anomaly; identical hash floods.

### Q20. How to prioritize Reels vs long video?

**Answer:** Separate queue classes and SLOs; short-form faster path.

### Q21. Client-side vs server transcode?

**Answer:** Client can pre-compress to save bandwidth; server still validates and produces canonical ladders for consistency.

### Q22. Manifest personalization?

**Answer:** Can filter renditions by device/network; still ACL at issue time.

### Q23. Deleting a video with existing shares?

**Answer:** Tombstone video; playback denies; Feed shows unavailable; async cleanup segments after grace.

### Q24. Exact view counts?

**Answer:** Approximate via aggregation; enough for social proof; creators may see delayed totals.

### Q25. Security scanning large files?

**Answer:** Stream scan; don’t load entire file in memory; isolate workers.

### Q26. What breaks at 100× uploads?

**Answer:** Single-region ingest, monolithic transcoder, no queue classes, origin-heavy playback.

### Q27. How to test playback ACL?

**Answer:** Matrix of audience × viewer; token expiry; revoke; link token rotation tests.

### Q28. Audio normalization / loudness?

**Answer:** Optional processing step; store loudness metadata; player applies.

### Q29. Captions?

**Answer:** ASR job Phase 1.5 → WebVTT sidecar; package into HLS.

### Q30. Cost of AV1?

**Answer:** Expensive encode, cheaper storage/egress; use for popular/long-lived; not always for ephemeral Stories.

### Q31. Upload edge authentication?

**Answer:** Short-lived upload tokens bound to video_id and user; cannot upload into others’ ids.

### Q32. Dual-write metadata?

**Answer:** Metadata DB source for state; object store source for bytes; reconcile with checksums.

### Q33. Can we stream while uploading?

**Answer:** Progressive publish for live-like but still VOD: complex; MVP wait until uploaded; live is different product.

### Q34. Observability?

**Answer:** Funnel conversion uploading→ready, queue lag, worker errors, CDN hit ratio, TTFF, ACL denies.

### Q35. Key launch risks?

**Answer:** Processing backlog, hot origin, ACL bugs on links, mobile upload failures, integrity false negatives/positives.

### Q36. How do chunk bitmaps work?

**Answer:** Session tracks received byte ranges; resume fetches missing ranges; complete asserts full coverage + checksum.

### Q37. Why content-hash segment names matter for sharing?

**Answer:** Shares reference `video_id`; CDN caches immutable hashes; ladder upgrades publish new hashes and flip pointers atomically.

### Q38. Share then make private — what happens?

**Answer:** `acl_ver++`; playback recheck fails for unauthorized; Feed/DM show unavailable; old signatures die.

### Q39. How to prioritize processing under backlog?

**Answer:** Short-form high-priority queues; age-in-queue fairness; autoscale workers; UX stays on `processing` honestly.

### Q40. Can DM share bypass integrity?

**Answer:** Product choice: limited distribution may proceed with pending scan; wide Feed should wait for minimum gates.

### Q41. Resumable upload vs multipart object store APIs?

**Answer:** Same idea — edge may map chunks to S3 multipart; client still sees offset resume and tokens.

### Q42. Deal-breaker recap?

**Answer:** No sync xcode; no origin-all-bytes; no forever private URLs; no blob-per-share; must resume on mobile.

---

## Appendix A — Video entity

```text
Video {id, owner_id, state, duration, size, checksum, audience, thumbs[], ladders[], acl_ver, created_at}
```

## Appendix B — Chunk protocol

```text
PUT /chunks?upload_id&offset&size
Header: Content-MD5
Response: next_offset
```

## Appendix C — Processing DAG

```text
validate -> probe -> thumb+360p -> package_preview -> [parallel xcode] -> package_full -> integrity -> ready
```

## Appendix D — ACL table

| Audience | Who plays |
|----------|-----------|
| private | owner |
| friends | friends |
| public | anyone logged-in/out per product |
| unlisted | token holders |

## Appendix E — Latency targets

```text
upload RTT chunk: minimized via regional edge
ready_partial: target minutes for short
TTFF: <2s CDN warm
```

## Appendix F — Queue lag alert

```text
alert if short-queue age p95 > 5 min
autoscaling workers
```

## Appendix G — Segment naming

```text
/v/{video_id}/{content_hash}/720p/seg00042.ts
```

## Appendix H — Share request

```json
{"video_id":"v1","target":"feed","audience":"friends","idempotency_key":"..."}
```

## Appendix I — NFR card

```text
Resumable upload
Async process
CDN ABR
ACL on playback
No blob duplication per share
```

## Appendix J — Failure modes

| Failure | Mode |
|---------|------|
| Worker outage | Queue backlog; upload still OK |
| CDN POP loss | Other POPs |
| Metadata DB | Read-only degrade; no new publishes |

## Appendix K — Priority formula

```text
priority = f(duration_short, creator_tier, age_in_queue, reprocess_flag)
```

## Appendix L — Geo restriction

Optional allow/deny countries at playback issue.

## Appendix M — Worked storage

```text
50M/day × 80MB ladders = 4 PB/day ingest-equivalent
lifecycle + short-form mix reduces retained volume
```

## Appendix N — Player events

```text
play, heartbeat(position), pause, end, error(code), bitrate_switch
```

## Appendix O — Glossary

| Term | Meaning |
|------|---------|
| ABR | Adaptive bitrate |
| Mezzanine | Intermediate high quality |
| Packager | Mux to HLS/DASH |
| Origin shield | Intermediate cache tier |
| ready_partial | Preview quality available |

## Appendix P — 30m checklist

1. Upload resume.  
2. Async pipeline + early preview.  
3. CDN ABR + signed ACL.  
4. Share by reference.  
5. Scale queues/regions.  
6. Deal-breakers.

## Appendix Q — Checksum strategy

Per-chunk MD5/CRC + file sha256; store on metadata.

## Appendix R — Reprocess

New codec → enqueue reprocess; keep old ladder until swap; atomic pointer update.

## Appendix S — DM share privacy

Recipients granted play; forward rules product-specific; still server ACL.

## Appendix T — Metrics

Upload success, processing p50/p99 by duration bucket, CDN HIT%, TTFF, rebuffer, block rate.

## Appendix U — Cold tier

Move rarely watched ladders to colder storage; keep low ladder hot.

## Appendix V — Progressive scale

| Scale | Must |
|-------|------|
| 10× | Regional upload, CDN |
| 100× | GPU fleets, queue classes |
| 1,000× | Media cells, ASICs |

## Appendix W — Antipatterns

| Antipattern | Why |
|-------------|-----|
| Sync xcode | Timeouts |
| Unsigned forever URLs | Leaks |
| Per-share copy | Cost |

## Appendix X — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just S3 + CloudFront” | Need social ACL, processing SLOs, queues, share graph |
| “Transcode in browser only” | Inconsistent quality/security |
| “Exact view counts sync” | Won’t scale |

## Appendix Y — Pseudocode playback

```text
def playback(viewer, video_id):
  v = db.get(video_id)
  assert v.state in (ready, ready_partial)
  assert acl.allows(viewer, v)
  token = sign(video_id, viewer, v.acl_ver, ttl=300)
  return manifests(v, token)
```

## Appendix Z — Success bar

Users can upload on flaky networks, see video ready quickly (at least preview), share safely, and the world watches via CDN without melting origin—with a clear path to 1,000×.

---


## Appendix AA — Upload edge regions

```text
Client geoDNS -> nearest upload edge
Edge buffers chunks to regional object store
Processing may pull cross-region if GPU capacity elsewhere
Renditions published to multi-CDN origins
```

## Appendix AB — State transition table

| From | Event | To |
|------|-------|-----|
| created | first chunk | uploading |
| uploading | complete+checksum | uploaded |
| uploaded | worker pickup | processing |
| processing | preview done | ready_partial |
| ready_partial | ladders done | ready |
| * | integrity fail | blocked |
| * | user delete | deleted |
| processing | fatal error | failed |

## Appendix AC — ABR selection logic (player)

```text
estimate bandwidth from recent segments
pick highest ladder with bitrate < 0.8 * bw
upswitch only with buffer > threshold
downswitch immediately on rebuffer risk
```

## Appendix AD — Share × ACL matrix

| Share target | Playback check |
|--------------|----------------|
| Feed friends | viewer friend of author OR share audience |
| DM | viewer in thread recipients |
| Public feed | public audience |
| Unlisted link | valid token + not revoked |

## Appendix AE — Cost levers card

```text
1) Early ladder only for ephemeral
2) AV1 for popular long-lived
3) Lifecycle cold storage
4) Cap max resolution by tier
5) Dedup identical uploads cautiously
```

## Appendix AF — Interview pitch (45s)

```text
"Resumable regional upload, async staged transcode with ready_partial, CDN ABR with
ACL-signed playback, shares by video_id reference—not blob copies—and integrity gates
before wide distribution."
```

## Appendix AG — QoE metrics

| Metric | Goal |
|--------|------|
| TTFF | low |
| Rebuffer ratio | <1–2% |
| Avg bitrate | network-appropriate |
| Play failures | ~0 |

## Appendix AH — Resumable upload sequence (detailed)

```text
1. Client POST /videos → video_id, session, chunk_size=8MB, upload_token
2. For each missing range: PUT chunk(offset, md5) with token
3. On network drop: GET session → resume offsets
4. POST complete(sha256, size) → uploaded
5. Enqueue processing; client polls GET /videos/{id} for state
6. On ready_partial: enable preview player + limited share
7. On ready: full ABR manifests available
```

## Appendix AI — Sharing graph invariants

```text
I1: Every play goes through playback ACL (except true public with still-expiring sigs)
I2: ShareEdge never embeds raw bytes
I3: Delete/privacy bump acl_ver → revoke
I4: Idempotency-Key on share prevents double posts
I5: Integrity block beats distribution
```

## Appendix AJ — Progressive scale card (video)

| Scale | Upload | Process | CDN | Share |
|-------|--------|---------|-----|-------|
| Base | Resume | Async DAG | ABR | Ref ids |
| 10× | Regional | Priority queues | Shield | Feed/DM/link |
| 100× | Multi-region | GPU fleets | Prefetch POPs | Integrity gates |
| 1,000× | Media cells | ASIC/AV1 | Cold tiers | Cell-local graph |

## Appendix AK — Anti-pattern → deal-breaker map

| Hear in interview | Say |
|-------------------|-----|
| “Transcode in the upload handler” | Deal-breaker — async |
| “S3 public URLs forever” | Deal-breaker — signed + acl_ver |
| “Copy file into Messenger” | Deal-breaker — reference video_id |
| “Exact sync view counts” | Won’t scale — approximate |

*End of Video Upload & Sharing system design.*
