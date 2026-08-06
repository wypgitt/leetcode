# System Design: YouTube Distribution & Video Delivery

> **Focus areas:** Upload · Transcode ladder · ABR (HLS/DASH) · CDN · Origin shield · Live vs VOD · Chunk/segment store · Playback auth · Soft recommendations hooks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (egress PB, encode farm cores, QPS split), separate control vs media planes, deal-breakers for “proxy all video through app servers”  
> **Interview theme:** Google L5+ media distribution — DB/metadata choice, partitioning by video_id, ambiguity over Google internals (no Maglev trivia required)

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

Goal: **bound the product**—a **YouTube-scale video distribution and delivery** system: creators upload (or go live), the platform stores mezzanine/originals, produces an adaptive bitrate ladder, publishes manifests, and serves segments globally via CDN with origin shielding—plus light hooks for discovery/recommendations (not a full ranking interview).

### 1.0 What this is / is not

| Dimension | **YouTube distribution / delivery (this doc)** | Not this |
|-----------|-----------------------------------------------|----------|
| Primary job | Ingest → process → package → deliver bytes | Full For You ranker / ads auction |
| Success | Durable assets, fast start, smooth ABR, global scale | Perfect creative studio suite |
| Write path | Resumable upload + async encode farm | App server as media proxy |
| Read path | CDN + origin shield + segment cache | Origin hit every chunk |
| Metadata | Video, variants, manifests, ACL, readiness | Full comment graph as core |
| Recs | Soft hooks (watch events → feature log) | Candidate gen + LTR deep dive |

**Scope statement:** Design YouTube-style distribution: upload, transcode, ABR packaging, CDN/origin shield, live vs VOD paths, playback auth, and progressive scale—with light recommendation event hooks only.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Upload model? | Resumable chunked upload; multi-GB/TB | Session + chunk index; checksums |
| F2 | Formats in? | MP4/MOV/WebM; various codecs | Mezzanine normalize; reject bombs |
| F3 | Output? | ABR ladder (e.g. 360p–4K); HLS + DASH | Encode jobs × rungs; packager |
| F4 | Playback? | Mobile/web players; seek; quality switch | Segmented VOD; short segment TTL |
| F5 | Live? | Yes — ingest RTMP/WebRTC → low-latency HLS/DASH | Separate live pipeline + DVR window |
| F6 | Privacy? | Public / unlisted / private | Signed cookies/URLs; ACL at mint |
| F7 | Processing SLA? | SD ready in minutes; 4K longer OK | Priority queues by resolution |
| F8 | Thumbnails? | Auto thumbs + optional custom | Thumbnail worker; CDN images |
| F9 | Captions? | Auto-caption Phase 1.5; upload SRT MVP | Async ASR job; sidecar tracks |
| F10 | Geo / rights? | Geo-block some titles | Edge policy + token claims |
| F11 | Analytics? | Views, watch time for creator dashboard | Event pipeline; not billing deep dive |
| F12 | Recs hook? | Emit watch/impressions for downstream | Feature log; no full ranker MVP |

**MVP functional scope:**

1. Authenticated **resumable upload** → object store (mezzanine).  
2. **Virus/policy scan** gate before public readiness.  
3. **Transcode ladder** (e.g. 360/480/720/1080; 4K optional queue).  
4. **Package** to HLS/DASH segments + master playlist.  
5. Mark video `READY`; mint **playback tokens**; serve via **CDN**.  
6. **Origin shield** tier between CDN POP and blob/segment store.  
7. **Live** path: ingest → transmux/transcode → sliding segment window (+ optional VOD archive).  
8. Metadata API: create/list/status; soft delete.  
9. Emit **playback/watch events** to a log for recs/analytics consumers.  
10. Basic **geo/ACL** enforcement on token mint and edge.

**Out of MVP:**

- Full personalized homepage / Shorts ranker  
- Multi-party live studio production  
- DRM (Widevine/FairPlay) deep integration (mention hooks)  
- Perfect global copyright Content ID (hooks + fingerprint job)  
- Client-side E2E encryption of all uploads  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Upload durability | No silent loss after complete | Multi-AZ object store; checksums |
| N2 | Time-to-first-ready (1080p) | Feels “processing…” then playable | p50 < 2–5 min; p99 < 15–30 min (length-dependent) |
| N3 | Playback start | Instant feel | p50 join < 1–2s on warm CDN; rebuffer rate SLO |
| N4 | Availability (play) | Critical | 99.9%+ via CDN; stale shield OK |
| N5 | Live latency | Interactive vs broadcast tradeoff | Standard live 10–30s; LL-HLS optional Phase 1.5 |
| N6 | Security | No private leak via CDN | Short-TTL signed tokens; HTTPS |
| N7 | Consistency | Strong metadata; immutable segments | Variant readiness flags |
| N8 | Multi-region | Global viewers | Regional upload; geo-replicated hot; CDN |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Creator resumes 2 GB upload → complete → scan OK → encode ladder → packager → READY → viewers play ABR.  
2. Viewer opens watch page → player fetches master.m3u8 → picks rung → segment hits CDN → smooth playback.  
3. Creator goes live → RTMP ingest → transmux → live playlist updates → viewers join mid-stream.  
4. Live ends → archive concat → VOD package → same watch URL mode=archive.  
5. Unlisted link → token embeds ACL → only holders play; not in public search (search out of scope).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload mid-fail | Resume from last ACK’d chunk; idempotent chunk PUT |
| Corrupt mezzanine | Transcode fail → retry; quarantine; notify creator |
| Hot video thundering herd | Origin shield + CDN; prefetch popular rungs |
| Segment origin miss storm | Shield coalescing; negative cache carefully |
| Live ingest disconnect | Reconnect window; playlist gap; optional slate |
| Geo-blocked region | Edge 403 with policy; don’t leak alternate CDN URL |
| Private video token leak | Short TTL + binding (IP optional / device); revoke |
| 8K / huge file | Quotas; async priority; storage cost alerts |
| Codec weirdness | Reject or remux-only path; support matrix |
| Partial ladder ready | Progressive availability: play 360p while 1080 encodes |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU viewers | 50M | 500M | — (global) | global peak |
| Concurrent viewers peak | 2M | 20M | 200M | 2B-scale events |
| Upload completes/day | 1M | 10M | 100M | 1B |
| Avg mezzanine size | 200 MB | 200–500 MB | 500 MB | mixed + Shorts |
| Transcode output multiplier | 3–5× | 4–6× | 5–8× | codec efficiency ↑ |
| Peak egress | 5 Tbps | 50 Tbps | 500 Tbps | multi-Pbps |
| Hot video peak | 100K conc | 1M | 10M | 100M+ live event |
| Metadata QPS (watch page) | 50K | 500K | 5M | 50M |
| Segment request QPS | 5M | 50M | 500M | edge-local |
| Encode farm (vCPU order) | 10K | 100K | 1M | cell fleets |

**What each jump forces:**

- **10×:** Mandatory origin shield; encode priority queues; CDN multi-tier; metadata cache.  
- **100×:** Regional encode cells; segment stores geo-partitioned; live dedicated POPs; shield mesh.  
- **1,000×:** Cell fabric per continent; prefetch/push for mega-events; hierarchical CDN; encode spot fleets.

### 1.5 Etc. (Constraints & Assumptions)

- We design **distribution/delivery**, not the entire Google ads or search stack.  
- Prefer **open patterns** (object storage, Kafka, HLS/DASH) over naming internal Google systems.  
- Recommendations are **event hooks only**; ranking is a sibling interview.  
- Shorts can share the same segment CDN with shorter ladder.

**Scope statement to repeat back:**

> Design a YouTube-style video distribution system: resumable upload to durable object storage, async transcode + ABR packaging (HLS/DASH), CDN delivery with origin shield, distinct live vs VOD pipelines, ACL’d playback tokens, progressive readiness, and watch-event hooks for downstream personalization—scaling through 10× / 100× / 1,000× without proxying media through app servers.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Upload control** | Create session, complete | ~1–5K/s | API |
| **Upload bytes** | Chunk PUT to blob | Multi-Gbps | Object store |
| **Encode jobs** | Ladder rungs | ~10–50 jobs/s steady | Worker fleet |
| **Metadata reads** | Watch page / status | ~50K/s | Spanner/cache |
| **Manifest GETs** | master + media playlists | ~0.5–2M/s | CDN |
| **Segment GETs** | `.ts` / `.m4s` | ~5M+/s | CDN → shield |
| **Watch events** | heartbeats / quartiles | ~0.5–5M/s | Kafka |
| **Live ingest** | RTMP/SRT connections | thousands–millions | Ingest edge |

**Anti-pattern:** one “QPS” mixing metadata, segments, and encode.

### 2.2 Storage math

```text
Uploads/day = 1M × 200 MB = 200 PB / day raw? WAIT — 1M × 0.2 GB = 200,000 GB = 200 TB/day mezzanine
Ladder multiplier 4× → ~800 TB/day packaged (+ mezzanine keep policy)
Monthly (~30d) ≈ 24 PB packaged growth (order-of-magnitude; retention/GC matters)

At 100× uploads: ~2 PB/day mezzanine → multi-EB fleet with retention tiers
Cold storage: move rarely watched mezzanine to colder class; keep hot segments warm
```

### 2.3 Egress math

```text
Avg bitrate watch ≈ 2 Mbps
2M concurrent × 2 Mbps = 4 Tbps (order)
CDN hit ratio 95%+ → origin/shield sees 5% = 200 Gbps (still huge — shield required)

Hot live 10M × 3 Mbps = 30 Tbps — all at edge; origin must not see fanout
```

### 2.4 Encode cost

```text
1 hour 1080p source → ladder 360/480/720/1080
Rough: 4–20× realtime CPU depending on codec/settings
1M uploads/day × avg 10 min = 10M min/day source
If encode 8× realtime across ladder ≈ 80M encode-minutes/day
÷ 1440 min ≈ ~55K concurrent encode slots (order) — fleet planning
Priority: Shorts/SD first for UX; 4K best-effort queue
```

### 2.5 Segment & cache

```text
2s segments, 2 Mbps ≈ 0.5 MB/segment
Viewer watches 10 min → 300 segments; most from CDN edge after first
Popular video: working set of top rungs cached worldwide
Long-tail: shield coalescing prevents origin stampedes on first miss
```

### 2.6 Metadata

```text
100M videos × ~2 KB metadata ≈ 200 GB — fits in distributed SQL + cache
Variants index: video_id → list of renditions — hot path cached
Watch page QPS dominated by cache, not DB
```

---

## 3. High-Level Design

### 3.1 API (control plane)

| Op | Semantics |
|----|-----------|
| `POST /v1/videos` | Create video metadata; returns `upload_url` / session |
| `PUT /upload/{session}/chunk` | Resumable chunks (or GCS resumable protocol) |
| `POST /v1/videos/{id}/complete` | Finalize; enqueue process |
| `GET /v1/videos/{id}` | Metadata + readiness + playback URLs |
| `POST /v1/videos/{id}/playback` | Mint short-TTL playback token / cookie |
| `DELETE /v1/videos/{id}` | Soft delete; revoke; GC later |
| `POST /v1/live/streams` | Create live; returns ingest endpoint + stream key |
| `POST /v1/live/{id}/end` | Close live; kick archive job |
| Internal: encode/packager callbacks | Update variant status |

**Playback (data plane):** CDN URLs for `master.m3u8` / `manifest.mpd` + segments; auth via signed cookie/query.

### 3.2 Data model

| Entity | Key | Store | Notes |
|--------|-----|-------|-------|
| Video | `video_id` | Spanner / distributed SQL | owner, ACL, state, duration |
| UploadSession | `session_id` | SQL + chunk map | resumable state |
| BlobRef | `blob_id` | Object store path | mezzanine checksum |
| Rendition | `(video_id, quality, codec)` | SQL + object paths | bitrate, resolution |
| Manifest | `video_id` | Object / CDN | HLS/DASH |
| LiveStream | `stream_id` | SQL + Redis presence | ingest status |
| PlaybackGrant | token claims | signed JWT/macaroon | exp, video_id, geo |
| WatchEvent | append-only | Kafka / PubSub | analytics/recs |

**State machine (VOD):** `CREATED → UPLOADING → UPLOADED → SCANNING → PROCESSING → READY | FAILED` (+ `PARTIAL_READY`).

### 3.3 Media formats — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Progressive MP4 only** | Simple | Poor ABR; seeking cost | Tiny MVP demo |
| **HLS (MPEG-TS / fMP4)** | Ubiquitous mobile; CDN-friendly | Apple-centric history | **MVP primary** |
| **DASH** | Flexible; CMAF synergy | Client matrix | Web + parallel |
| **CMAF dual-package** | One segment set, two manifests | Packager complexity | **Strong at 10×+** |
| **WebRTC VOD** | Low latency | Not CDN-cheap at scale | Live interactive only |

**Chosen MVP:** HLS fMP4 segments + DASH optional; CMAF when scale justifies one store.

### 3.4 CDN & origin — Why X over Y

| Approach | Pros | Cons | Deal-breaker? |
|----------|------|------|---------------|
| Origin = API servers stream file | — | Melts app tier | **Yes — deal-breaker** |
| CDN → object store direct | Simple | Stampede / bill shock | OK small; weak at YouTube scale |
| **CDN → origin shield → store** | Coalesce misses; protect origin | Extra hop | **Chosen** |
| Push all videos to every POP | Fast | Impossible storage | Deal-breaker |
| Hierarchical CDN (L1/L2) | Scale | Ops complexity | 100×+ |

### 3.5 Live vs VOD

| | VOD | Live |
|---|-----|------|
| Source | Complete mezzanine | Continuous ingest |
| Encode | Offline ladder (quality) | Near-realtime ladder |
| Manifest | Static / VOD playlist | Sliding window + `#EXT-X-MEDIA-SEQUENCE` |
| Archive | N/A (is archive) | Optional DVR → VOD package |
| Scale stress | Hot catalog + long-tail | Mega-concurrent single key |

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Upload path | Direct-to-blob resumable | App servers ≠ pipes | Proxy GB through API |
| Processing | Async job queue | UX + scale | Sync encode in request |
| Delivery | CDN + shield | Egress & stampede | Origin per segment |
| Packaging | Segmented ABR | Network adapt | Single bitrate only |
| Metadata DB | Distributed SQL (Spanner-like) | Strong ACL/state | Cassandra-only without care for ACL txs |
| Hot events | Edge + prefetch | Fanout | Single origin fanout |
| Recs | Event log hooks | Scope | Full LTR in this design |

**DB choice note (interview):**  
- **Spanner / Cockroach-style:** video metadata, ACL, state transitions — strong consistency, global secondary indexes careful.  
- **Bigtable / wide-column:** chunk maps, analytics-friendly time series — not primary ACL source of truth.  
- **Object store:** mezzanine + segments — immutable blobs.  
- **Redis/Memorystore:** live presence, rate limits, hot metadata cache — ephemeral.

---

## 4. Architecture Diagram

```text
 Creators                    Viewers
    |                           |
    | control                   | playback
    v                           v
 +----------------+      +------------------+
 | Upload / Meta  |      | Playback API     |-- mint signed cookie
 | API            |      | (ACL, geo)       |
 +--------+-------+      +--------+---------+
          |                       |
          | presign               | token
          v                       v
 +----------------+      +------------------+     +----------------+
 | Object Store   |      | CDN Edge POPs    |---->| Player         |
 | mezzanine      |      | segments+manifest|     | HLS/DASH ABR   |
 +--------+-------+      +--------+---------+     +----------------+
          |                       |
          | notify                | miss
          v                       v
 +----------------+      +------------------+
 | Scan + Encode  |      | Origin Shield    |
 | + Packager     |      | (coalesce)       |
 +--------+-------+      +--------+---------+
          |                       |
          | write segments        v
          +--------------> Segment / Blob Store (regional)
          |
          v
   Metadata DB (state=READY)
          |
          v
   Watch Events --> Kafka --> Analytics / Recs feature log
```

**VOD path:**

```text
CreateVideo -> Resumable PUT chunks -> Complete
  -> Scan
  -> Encode ladder (parallel rungs)
  -> Package CMAF/HLS/DASH
  -> Update Renditions READY (progressive)
  -> Invalidate / warm CDN for thumbs + low rung
```

**Live path:**

```text
CreateLive -> Ingest Edge (RTMP/SRT) -> Transcode/Transmux
  -> Publish sliding segments to live store
  -> CDN live path (short TTL / no long cache)
  -> On end: ArchiveJob -> VOD package
```

**Playback path:**

```text
Watch page -> Playback API (ACL) -> Set-Cookie signed
  -> GET master.m3u8 (CDN)
  -> GET media playlist + segments (CDN)
  -> miss -> shield -> origin store
  -> player ABR algorithm picks rung
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Mezzanine durable** before `UPLOADED` ACK (multi-AZ, checksum).  
2. **Segments immutable** once published (new encode = new version prefix).  
3. **ACL checked at token mint**; edge enforces signature — never “security by obscure URL” alone for private.  
4. **State monotonic** for readiness flags (PARTIAL → READY); failures explicit.  
5. **Live playlist continuity** under reconnect with documented gap behavior.  
6. **Watch events at-least-once**; analytics idempotent on `event_id`.

#### 5.1.2 Upload reliability

```text
chunk_id, offset, crc32/md5
server: accept if matches expected offset OR idempotent rewrite same bytes
complete: verify full checksum / composed object
retry: client resumes; never re-upload entire file unless corrupt
```

**Deal-breaker:** no resumable story for multi-GB uploads on mobile networks.

#### 5.1.3 Encode failures & progressive readiness

| Strategy | Behavior |
|----------|----------|
| Parallel rungs | 360p finishes first → `PARTIAL_READY` playable |
| Retry with backoff | Transient worker death |
| Poison quarantine | Repeat fail → FAILED + alert |
| Versioned output | Re-encode doesn’t break in-flight viewers (old prefix) |

#### 5.1.4 CDN / shield failure modes

| Failure | Mitigation |
|---------|------------|
| Edge POP down | DNS/anycast steer; other POPs |
| Shield down | Failover shield pair; coalescing may degrade |
| Origin regional outage | Cross-region fetch (costly) for hot; degrade long-tail |
| Bad cache poison | Versioned URLs (`/v/{encode_id}/`); purge API |

#### 5.1.5 Live reliability

- Dual ingest endpoints (primary/backup).  
- GOP-aligned segment boundaries.  
- DVR buffer in Redis/object ring for late joiners.  
- On disconnect: hold last segments; mark stream unhealthy after N seconds.

#### 5.1.6 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Encode backlog | Priority queues; autoscale workers |
| 10× | Hot video origin melt | Shield + prefetch top rungs |
| 100× | Live mega-event | Dedicated event POPs; push; admission control |
| 1,000× | Global encode imbalance | Cell-local encode; follow-the-sun capacity |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| `video_id` (hash) | Metadata shards; segment prefix |
| `owner_id` | Creator library indexes |
| Geo cell | Upload region; encode near data |
| `stream_id` | Live ingest affinity |
| Time buckets | Analytics partitions |

**Hot video:** content is **read-mostly immutable** — scale with CDN replication of working set, not DB write sharding. Metadata for a viral video is tiny; bytes are everything.

#### 5.2.2 ABR ladder design

```text
Example ladder (VOD):
  360p  0.5 Mbps
  480p  1.0 Mbps
  720p  2.5 Mbps
  1080p 5.0 Mbps
  1440p / 4K optional queues

Segment duration: 2–6s (VOD); live often 2s (LL shorter partials Phase 1.5)
Codec: H.264 baseline reach; AV1/VP9 efficiency at higher scale
```

Player ABR: buffer-based / throughput-based; server provides accurate bandwidth hints in playlist.

#### 5.2.3 Origin shield coalescing

```text
Many edges miss segment S concurrently
  -> shield single-flights fetch to origin
  -> fill shield memory/disk
  -> fanout to edges
Without shield: origin QPS ≈ edge_miss_qps → outage
```

#### 5.2.4 Live fanout

```text
Never: ingest node unicast to all viewers
Always: ingest -> packager -> CDN multicast tree (logical)
Admission control for free-for-all mega-events
Optional: separate “events” CDN property with higher TTLs on media? (live = low TTL)
```

#### 5.2.5 Encode farm scaling

| Technique | Why |
|-----------|-----|
| Job queue by priority | UX: SD before 4K |
| Chunked encode (parallel GOP ranges) | Long VOD wall-clock ↓ |
| Spot/preemptible + checkpoint | Cost |
| Cell-local workers | Data gravity |
| Codec capability matrix | Hardware accel (NVENC) where available |

#### 5.2.6 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Shield mandatory; CDN tiers; metadata cache; progressive READY |
| →100× | Regional cells; CMAF; live event mode; encode GPU pools |
| →1,000× | Hierarchical CDN; push for events; EB storage tiers; AV1 ladder efficiency |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
ladders:
  default: [360,480,720,1080]
  shorts: [360,720]
segment_duration_s: 2
packager: cmaf
cdn_ttl:
  vod_segment: 1d
  live_segment: 2s
  manifest_vod: 60s
shield: { coalesce: true, peers: 2 }
encode_priority: { partial_sd: 100, hd: 50, uhd: 10 }
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `upload_complete_rate` | Creator UX |
| `time_to_partial_ready` | Playability |
| `encode_queue_depth` | Capacity |
| `cdn_hit_ratio` | Cost/perf |
| `origin_qps` / `shield_coalesce_ratio` | Stampede |
| `rebuffer_ratio` | QoE |
| `live_ingest_bitrate` / `gap_count` | Live health |
| `playback_403_rate` | Auth bugs |

#### 5.3.3 Testing

- Golden mezzanine → expected ladder bitrates.  
- Chaos: kill encode workers mid-job.  
- Load: hot video segment miss stampede with/without shield.  
- Live reconnect & archive correctness.  
- ACL: private URL without token must fail at edge.

#### 5.3.4 Operability

- Dual-write new packager version under `/v2/` prefix; cut traffic.  
- Canary CDN config.  
- Re-encode campaigns for codec migrations (AV1) as batch fleets.  
- Storage GC: soft-delete → retain → cold → purge with legal hold flags.

#### 5.3.5 Soft recommendations hooks

```text
WatchHeartbeat { video_id, user_id?, ts, position_s, quality, rebuffer_ms }
QuartileEvent { video_id, quartile, session_id }
→ Kafka topic watch.events
→ Feature generation overnight / streaming for ranking sibling system
Do NOT block playback path on recs consumers
```

---

## 6. Wrap-Up

### 6.1 What we designed

A **YouTube-style distribution & delivery** platform: resumable direct upload, async scan/encode/package to ABR segments, CDN delivery protected by **origin shield**, distinct **live vs VOD** pipelines, ACL’d playback tokens, progressive readiness, and watch-event hooks—not a homepage ranker and not media through app servers.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| App proxy upload/play | Deal-breaker |
| ABR segments | Required for QoE |
| Origin shield | Required before viral scale |
| Progressive READY | Ship SD first |
| Live ≠ VOD | Separate latency & cache TTLs |
| Metadata DB | Strong consistency for ACL/state |
| Recs | Events only in this interview |

### 6.3 30-second scale narrative

> Baseline: resumable blob upload, encode ladder, HLS to CDN. 10× forces origin shield and progressive readiness. 100× splits regional encode/segment cells and live event mode. 1,000× is hierarchical CDN plus push for mega-events—egress is an edge problem; origin must never see fanout.

### 6.4 Deal-breakers checklist

- Proxying video bytes through monolithic API servers.  
- Single bitrate progressive download as the only mode at scale.  
- No shield/coalescing under hot-video stampedes.  
- Caching private content without signed access.  
- Coupling playback availability to recommendations ranker uptime.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: VOD vs live first?**  
A: Ask. Often VOD core + live Phase 1.5; architecture should leave ingest edge hooks.

**Q2: How many qualities?**  
A: Lock a ladder; show cost vs QoE. Shorts may use fewer rungs.

**Q3: DRM?**  
A: Mention Widevine/FairPlay license server; segments encrypted; MVP often signed URL only.

**Q4: Comments / likes?**  
A: Separate services; eventual consistency OK; don’t put in media path.

**Q5: 4K/HDR?**  
A: Separate queue; storage/egress cost; device capability signaling.

### 7.2 Upload & storage

**Q6: Why resumable upload?**  
A: Mobile networks fail; multi-GB without resume is product-breaking.

**Q7: Where is source of truth for bytes?**  
A: Object store; metadata DB points to `blob_id` + checksum.

**Q8: Dedup uploads?**  
A: Hash optional; privacy/ownership careful; per-owner easier than global.

**Q9: Retention of mezzanine?**  
A: Keep for re-encode; tier cold; legal holds.

**Q10: Chunk size?**  
A: e.g. 8–32 MB; balance overhead vs retry waste.

### 7.3 Transcode & packaging

**Q11: Transcode vs transmux?**  
A: Transmux changes container; transcode changes codec/resolution — live often transmux+limited transcode.

**Q12: Why fMP4/CMAF?**  
A: One media, multiple manifests; better cache sharing.

**Q13: Segment duration tradeoff?**  
A: Shorter → lower latency, more requests/overhead; longer → efficient, slower switch/seek startup.

**Q14: How to parallelize long encodes?**  
A: Split by time ranges/GOPs; stitch; watch A/V sync.

**Q15: When is video playable?**  
A: When minimum rung + manifest exist (`PARTIAL_READY`).

### 7.4 CDN & ABR

**Q16: What does ABR need from server?**  
A: Multiple aligned renditions + accurate bandwidth/codecs in master playlist.

**Q17: Why origin shield?**  
A: Collapse duplicate misses; protect origin; improve cache fill efficiency.

**Q18: Cache TTL for live vs VOD?**  
A: Live segments seconds; VOD hours–days with versioned paths.

**Q19: How to handle cache purge after re-encode?**  
A: New version prefix; old TTL expires; avoid global purge storms.

**Q20: Anycast vs DNS CDN?**  
A: Both exist; discuss POP selection & failover — avoid vendor trivia.

### 7.5 Live

**Q21: Ingest protocols?**  
A: RTMP common; SRT/RIST resilient; WebRTC for ultra-low-latency interactive.

**Q22: Latency budget breakdown?**  
A: Encode GOP + packager + playlist refresh + player buffer — dominate vs pure network RTT.

**Q23: How do late joiners work?**  
A: Sliding window playlist; DVR depth product decision.

**Q24: Live to VOD?**  
A: Archive job concatenates; may re-package higher quality offline.

**Q25: Mega-event readiness?**  
A: Prefetch, admission, dedicated shields, load tests, circuit breakers.

### 7.6 Security & ACL

**Q26: Unlisted vs private?**  
A: Unlisted: secret URL + optional token; private: authz required. Don’t rely on secrecy alone for private.

**Q27: Signed URL vs cookie?**  
A: Cookie better for many segment GETs (not putting query sig on each); URL fine for simple.

**Q28: Geo-blocking where?**  
A: At mint + edge; token carries allowed countries.

**Q29: Hotlink protection?**  
A: Referrer weak; signatures strong; short TTL.

**Q30: Stream key leak (live)?**  
A: Rotate keys; bind ingest IP optional; detect duplicate publishers.

### 7.7 Data stores & partitioning

**Q31: Why not put segments in SQL?**  
A: Blobs ≠ relational rows; size/IOPS wrong tool.

**Q32: Spanner vs sharded MySQL?**  
A: Global metadata + transactions vs ops-heavy sharding; either OK if you own rebalancing story.

**Q33: Hot `video_id` partition?**  
A: Reads cached; writes rare after READY; not a write hotspot.

**Q34: How to index creator library?**  
A: Secondary index `(owner_id, created_at DESC)` — watch hotspot creators with careful pagination.

**Q35: Analytics store?**  
A: Kafka → warehouse/streams; separate from online metadata.

### 7.8 Estimation drills

**Q36: Egress for 20M concurrent at 2 Mbps?**  
A: 40 Tbps order — argue CDN.

**Q37: Storage for 10M uploads/day × 300 MB × 4× ladder?**  
A: 10M × 1.2 GB ≈ 12 PB/day packaged order — retention critical.

**Q38: Origin QPS with 99% CDN hit and 100M segment QPS?**  
A: 1M QPS to shield/origin path — still needs coalesce & tiers.

### 7.9 Recommendations hooks

**Q39: What events matter?**  
A: Impression, start, heartbeat, completion, skip, quality, rebuffer — privacy scrubbed.

**Q40: Can delivery wait on recs?**  
A: Never; async log only.

### 7.10 Alternatives & deal-breakers

**Q41: Only progressive download?**  
A: Fails mobile networks & large files QoE.

**Q42: Peer-to-peer CDN?**  
A: Possible assist; legal/NAT complexity; not MVP core.

**Q43: Transcode in the client upload app?**  
A: Helps; servers still need authoritative ladder for device diversity.

**Q44: Store one 4K and transcode on the fly at edge?**  
A: Cost/latency bomb at YouTube scale — precompute ladder.

### 7.11 Interview craft

**Q45: How to open?**  
A: Clarify VOD/live, ladder, ACL, scale, then split control vs media planes.

**Q46: What numbers matter?**  
A: Concurrent viewers, bitrate, CDN hit%, upload PB/day, encode parallelism, time-to-ready.

**Q47: What impresses L5+?**  
A: Progressive readiness, shield coalescing, live≠VOD TTLs, explicit deal-breakers, DB roles split.

**Q48: Common mistake?**  
A: Designing only microservices boxes without byte math; or deep-diving Maglev instead of ABR+CDN.

---

### Appendix A — Video state machine

```text
CREATED -> UPLOADING -> UPLOADED -> SCANNING
  -> PROCESSING -> PARTIAL_READY -> READY
  -> FAILED
  -> DELETED (soft)
```

### Appendix B — Upload session pseudocode

```text
createSession(video_id, size, checksum_algo):
  return {session_id, chunk_size, upload_urls}

putChunk(session, idx, bytes, crc):
  assert crc
  if already have idx with same crc: ACK
  store part
  ack(next_expected)

complete(session):
  compose object
  verify total checksum
  enqueue ScanJob(video_id)
```

### Appendix C — Encode job graph

```text
Scan OK
  -> fanout Encode(rung) for rung in ladder
  -> each success: write segments under /v/{encode_id}/{rung}/
  -> when min_rungs ready: PARTIAL_READY
  -> when all required: READY + publish master playlist
```

### Appendix D — HLS master sketch

```text
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
360p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
720p.m3u8
```

### Appendix E — Playback token claims

```text
{
  "vid": "vid_123",
  "uid": "user_9",
  "acl": "private",
  "geo": ["US","CA"],
  "exp": 1710001234,
  "enc": "v/enc_42"
}
```

### Appendix F — Origin shield single-flight

```text
onMiss(key):
  if inflight[key]: wait
  else:
    inflight[key] = fetchOrigin(key)
    cache.put(key, val)
    clear inflight
    return val
```

### Appendix G — Live playlist window

```text
window = last N segments (e.g. 3–5 for low latency, more for DVR)
on new segment:
  append
  drop oldest if > DVR_DEPTH
  bump media sequence
```

### Appendix H — Progressive scale table

| Scale | Upload | Encode | Deliver | Live |
|-------|--------|--------|---------|------|
| Baseline | 1 region blob | 1 queue | CDN | Basic |
| 10× | Multi-AZ | Priority | Shield | Dual ingest |
| 100× | Geo upload | Cells + GPU | L2 CDN | Event mode |
| 1,000× | Cell fabric | Spot fleets | Hierarchical + push | Global events |

### Appendix I — QoE metrics

| Metric | Target idea |
|--------|-------------|
| Join time | < 2s p50 |
| Rebuffer ratio | < 1–2% watch time |
| Fatal errors | << 0.1% sessions |
| Bitrate ladder waste | Avoid over-download |

### Appendix J — NFR card

```text
Durable mezzanine multi-AZ
PARTIAL_READY fast
CDN hit >> origin
Shield coalesce on
Private via signed access
Live gaps observable
Playback ⟂ recs consumers
```

### Appendix K — Content safety hooks

```text
ScanJob: malware + basic NSFW/policy classifiers
FingerprintJob (Phase 2): match against reference DB
Hold public READY until policy clears if high risk
```

### Appendix L — Storage tiers

| Tier | Content | TTL/policy |
|------|---------|------------|
| Hot SSD/edge | Popular segments | Working set |
| Standard object | Segments + recent mezz | Months |
| Cold/archive | Old mezzanine | Years / legal |

### Appendix M — Shorts vs long-form

| | Shorts | Long |
|---|--------|------|
| Duration | < 60–180s | minutes–hours |
| Ladder | Fewer rungs | Full |
| Encode SLO | Seconds–minutes | Minutes+ |
| Prefetch | Aggressive next-up | On demand |

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just put videos on S3+CloudFront” | Necessary but not sufficient — encode, ACL, live, shield, QoE |
| “Transcode on the fly” | Cost/latency at scale |
| “One global NFS” | Deal-breaker |
| “Recs in playback path” | Coupling outage domains |

### Appendix O — Related systems (conceptual)

| System | Role |
|--------|------|
| Object storage | Mezzanine/segments |
| Pub/Sub/Kafka | Jobs + watch events |
| Distributed SQL | Metadata/ACL |
| CDN | Delivery |
| Dataflow | Analytics |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Mezzanine | High-quality source retained for processing |
| Rendition / rung | One bitrate/resolution in ladder |
| ABR | Adaptive bitrate switching |
| Origin shield | Intermediate cache coalescing tier |
| CMAF | Common media format for HLS+DASH |
| GOP | Group of pictures — encode/segment boundary |

### Appendix Q — Worked example

```text
Baseline: 2M concurrent × 2 Mbps = 4 Tbps egress
CDN hit 97% → 120 Gbps toward shields
10 shields × regional → ~12 Gbps each — planned capacity
Hot video 5% of watch time → ensure top titles pre-warmed in major POPs
Encode: 1M uploads/day × 10 min × 8× ≈ capacity planning as in §2.4
```

### Appendix R — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Strong metadata? | Yes for ACL/state |
| Segments mutable? | No — version prefix |
| Global playlist same second? | CDN eventual; versioned |
| Delete latency | Soft delete + token expiry + GC |

### Appendix S — 30m interview checklist

1. Clarify VOD/live, ladder, ACL, scale.  
2. Split control vs media planes; byte math.  
3. Draw upload → encode → CDN/shield → player.  
4. Progressive READY + live window.  
5. DB roles: SQL meta, object bytes, Kafka events.  
6. 10×/100×/1,000× narrative.  
7. Deal-breakers.

### Appendix T — Player ABR (server-relevant)

```text
Provide:
  - accurate BANDWIDTH in master
  - aligned segment boundaries across rungs
  - optional CODECS, FRAME-RATE
Avoid:
  - missing rung gaps that force rebuffer on switch
```

### Appendix U — Geo / rights

```text
token.geo_allowlist
edge: if client_country not in allowlist -> 403
metadata: rights windows (start/end) checked at mint
```

### Appendix V — What changes at each scale (quick card)

| Scale | Must add |
|-------|----------|
| 10× | Shield, priority encode, meta cache |
| 100× | Regional cells, event live mode, CMAF |
| 1,000× | Hierarchical CDN, push, EB tiers |

---

*End of YouTube Distribution & Video Delivery system design.*
