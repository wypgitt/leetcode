# System Design: Global Video Streaming Platform

> **Focus areas:** Upload/transcoding · Mezzanine · ABR ladder · HLS/DASH · CDN · Origin shield · Hot launches · Multi-region storage  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (TB/PB), split QPS classes, explicit deal-breakers, progressive evolution

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

Goal: **bound the product**—VOD vs live, quality ladder, global watch traffic, and what “hot launch” means for CDN/origin.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | VOD, live, or both? | **VOD primary**; live Phase 2 hooks | Upload→transcode→packager→CDN; live needs different ingest |
| F2 | Who uploads? | Creators / studios via API & web; multi-tenant | `tenant_id` + authz; per-tenant quotas |
| F3 | Source formats? | MP4/MOV/MXF; long-form + short-form | Normalize to **mezzanine** then ladder |
| F4 | Playback? | Mobile/web/TV; **ABR** via HLS and/or DASH | CMAF or dual pack; player picks bitrate/fps |
| F5 | Seeking / scrubbing? | Instant scrub with thumbnail sprites / storyboard | Precompute thumbs + VTT/JSON timeline |
| F6 | DRM? | Optional Widevine/FairPlay for premium | Packager + license service; keep MVP cleartext OK |
| F7 | Captions / multi-audio? | Sidecar WebVTT/TTML; multi-language audio later | Separate rendition groups |
| F8 | Thumbnails & previews? | Poster + scrub sprites + optional short preview clip | Async jobs in media pipeline |
| F9 | Analytics? | Starts, Quartiles, rebuffering, bitrate switches | Client beacons → pipeline; not on critical play path |
| F10 | Geo / library? | Global catalog; regional licensing later | Metadata + entitlement checks at play session start |
| F11 | Upload resume? | Yes for large files | Chunked upload + checksum compose |
| F12 | Processing notifications? | Webhook when ready / failed | Async status machine on title/asset |

**MVP functional scope (lock with interviewer):**

1. Chunked **upload** to object storage with resume.  
2. Ingest validation → **mezzanine** encode → **ABR ladder** (multiple video bitrates + audio).  
3. Package to **HLS** (DASH optional same CMAF chunks).  
4. Publish to **origin** + **CDN**; clients play with ABR.  
5. **Seeking** via standard segments + thumbnail sprites.  
6. Title metadata API; play URL / signed cookies or tokens.  
7. Basic processing status; retry failed encodes; DRM optional stub.

**Out of MVP (explicitly defer):**

- Ultra-low-latency live (<3s)  
- Client-side upload transcoding as SoT  
- Per-title neural encoding optimization (can mention)  
- Full studio DRM multi-key rotation UX  
- Social features / comments  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-first-frame (playback)? | Feels instant on warm CDN | p50 < 1s, p99 < 3s (good network) |
| N2 | Rebuffering ratio | Low | <0.5–1% of playtime (product SLO) |
| N3 | Upload durability | No silent loss | Multi-AZ object storage; checksum verify |
| N4 | Processing durability | Jobs at-least-once; outputs idempotent by asset version | Media job scheduler with leases |
| N5 | Availability (playback) | CDN-backed critical path | 99.9%+ play start; origin shielded |
| N6 | Global latency | Edge POP near users | Multi-region origins + global CDN |
| N7 | Consistency | Metadata strong in home; CDN eventual for segments | Immutable segment URLs per version |
| N8 | Hot launch | Popular title must not melt origin | Prefetch / origin shield / packer cache |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Upload completes → validate → mezzanine → ladder → package → `READY` → CDN playable.  
2. Player fetches master playlist → picks rung → segments from edge → ABR up/down.  
3. User seeks to 1:12:30 → player requests segment + shows sprite thumb.  
4. New version uploaded → new asset version; old URLs remain until invalidated/TTL.  
5. Encode failure on one rung → retry rung; don’t fail whole title if policy allows partial ladder.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload interrupted | Resume from last chunk; compose only after all parts + checksum |
| Corrupt source | Validation fail → `FAILED` with reason; no partial publish |
| Transcode worker death | Lease reclaim; rewrite same output keys idempotently |
| Hot launch thundering herd | Prefetch popular bitrates to CDN; origin shield coalesces |
| Playlist cache vs new version | Versioned paths (`/v/{assetVersion}/...`); never mutate immutable segments |
| Mid-credit bitrate spikes | ABR logic + capped ladder; cap peak bitrate for mobile plans |
| Geo-blocked title | Entitlement denial at session token mint; CDN token bound to policy |
| Audio/video drift | A/V sync in mezzanine; reject pathological sources |
| DRM license outage | Playback fails closed for protected; clear MVP unaffected |
| Short-form vs 4-hour movie | Same pipeline; cost/segment count differs; parallelize encodes |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 5M | 50M | 500M | 5B (theoretical/global) |
| DAU | 1M | 10M | 100M | 1B |
| Peak concurrent viewers | 100K | 1M | 10M | 100M |
| Avg bitrate consumed (blended) | 3 Mbps | 3 Mbps | 3–4 Mbps | 3–5 Mbps |
| Titles in catalog | 100K | 1M | 10M | 100M |
| New uploads / day | 5K | 50K | 500K | 5M |
| Avg source duration | 40 min | 40 min | 30–60 min | 30–60 min |
| Ladder outputs / title | ~8 video + 1–2 audio | same | same | +more rungs/HDR |
| Peak origin Gbps (after CDN hit) | 20 | 100 | 500 | 2–5 Tbps* |
| CDN egress (peak) | 0.3 Tbps | 3 Tbps | 30 Tbps | 300 Tbps |

\*Origin after shield/hit-ratio; see §2.

**What each jump forces:**

- **10×:** Dedicated transcode fleet; CDN mandatory; origin shield; chunked upload service.  
- **100×:** Multi-region mezzanine storage; regional packagers; per-tenant fairness on encode; advanced prefetch for launches.  
- **1,000×:** Global multi-CDN; title placement/replication policies; encode spot fleets; cold storage tiering; cell’d metadata.

### 1.5 Etc. (Constraints & Assumptions)

- **Primary: VOD** with global CDN (Cloudfront/Fastly/Akamai-class or multi-CDN).  
- Players: HLS everywhere; DASH for some devices—prefer **CMAF** dual-manifest.  
- We **build** control plane + pipeline; may buy CDN/storage.  
- DRM optional; design packaging hooks.  
- Storage costs matter—call them out with correct TB/PB math.

**Scope statement:**

> Design a global VOD platform: resumable upload, mezzanine + ABR ladder, HLS/DASH packaging, CDN playback with seeking/thumbnails, evolving from ~100K concurrent viewers through 10× / 100× / 1,000× with origin shield, multi-region storage, and hot-launch protections.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Playback bandwidth (split from upload/encode)

```text
Baseline peak concurrent = 100,000
Blended ABR ≈ 3 Mbps = 3×10^6 bit/s

Total egress ≈ 100,000 × 3 Mbps = 300,000 Mbps = 300 Gbps = 0.3 Tbps
```

| Scale | Concurrent | Egress @ 3 Mbps | @ 4 Mbps |
|-------|------------|-----------------|----------|
| 1× | 100K | 0.3 Tbps | 0.4 Tbps |
| 10× | 1M | 3 Tbps | 4 Tbps |
| 100× | 10M | 30 Tbps | 40 Tbps |
| 1000× | 100M | 300 Tbps | 400 Tbps |

**Unit check:** 100M × 3 Mbps = 300×10^6 Mbps = 3×10^14 bit/s = **300 Tbps** (not PB/s). Correct.

CDN hit ratio target **90–99%**. Origin draw ≈ egress × (1 - hit_ratio):

```text
At 100× (30 Tbps) with 98% HIT:
Origin ≈ 30 Tbps × 0.02 = 0.6 Tbps = 600 Gbps (still huge → shield + multi-origin)
```

### 2.2 Storage (catalog)

**Mezzanine** (high-quality intermediate, e.g. ProRes/high-bitrate H.264/H.265):

```text
Assume mezzanine ≈ 20 Mbps average for planning (varies wildly)
40 min = 2400 s × 20 Mb/s = 48,000 Mb ≈ 6 GB per title mezzanine
```

**ABR ladder** (example rungs):  

| Rung | Video | Notes |
|------|-------|-------|
| 360p | 0.8 Mbps | |
| 480p | 1.5 Mbps | |
| 720p30 | 3 Mbps | |
| 720p60 | 4.5 Mbps | optional |
| 1080p30 | 6 Mbps | |
| 1080p60 | 9 Mbps | optional |
| 1440p | 12 Mbps | |
| 2160p | 20 Mbps | optional |

```text
Sum video ≈ 0.8+1.5+3+4.5+6+9+12+20 ≈ 57 Mbps (full rich ladder)
Many titles ship thinner ladder ≈ 15–25 Mbps sum

Use 25 Mbps sum × 2400 s ≈ 60,000 Mb ≈ 7.5 GB ladder media / title
Plus audio ≈ 0.2 GB; HLS overhead small vs media
≈ 8 GB packaged / title (thin-rich blend)
Mezzanine + packaged ≈ 6 + 8 = 14 GB / title (order-of-magnitude)
```

| Catalog | Titles | Raw media order | Notes |
|---------|--------|-----------------|-------|
| Baseline | 100K | 100K × 14 GB ≈ **1.4 PB** | |
| 10× | 1M | **14 PB** | |
| 100× | 10M | **140 PB** | tier cold titles |
| 1000× | 100M | **1.4 EB** | must tier / delete / regional subset |

**Not** “1.4 TB” at baseline—**1.4 PB**. Common interview footgun.

### 2.3 Upload & transcode traffic

```text
Baseline: 5,000 uploads/day × 40 min source
Source bitrate assume 15 Mbps avg upload size:
2400 s × 15 Mb/s = 36,000 Mb ≈ 4.5 GB / upload
5,000 × 4.5 GB/day ≈ 22.5 TB/day ingest

Transcode compute (rough):
Each title → mezzanine + N rungs; CPU/GPU hours ∝ duration × ladder width
5,000 × 40 min × (say 8× realtime factor total across rungs)
→ large fleet; burst with queues
```

At **1,000×** (5M uploads/day): ingest ≈ **22.5 PB/day**—dominates pipeline cost; need aggressive validation, spam controls, tiered encoding.

### 2.4 QPS classes (split)

| Class | Baseline peak | 1000× | Notes |
|-------|---------------|-------|-------|
| Play session start / token | ~5K QPS | ~5M QPS | Control plane; cache config |
| Manifest requests | ~20K | ~20M | CDN cached heavily |
| Segment requests | ~1M+ | ~1B+ | Almost all at edge |
| Upload chunk PUTs | ~2K | ~2M | Separate path |
| Encode job complete events | ~few× uploads/day | scale with uploads | Async |
| Analytics beacons | ~50K | ~50M | Highly aggregatable |

**Deal-breaker:** Sending segment traffic to app servers (bypass CDN).

### 2.5 Memory / edge

```text
Player: few MB buffers
Edge: hot title segments in cache — popular episode can be 8 GB × many POPs
Origin shield memory/SSD: coalesce requests for same URL
```

### 2.6 Critical bottlenecks

1. **Origin melt on cold/hot launch** without shield/prefetch  
2. **Transcode backlog** after viral creator days  
3. **Storage cost** if mezzanine + all rungs kept forever for all titles  
4. **Metadata/entitlement** SPOF at session start  
5. **Single-region origin** for global audience  

---

## 3. High-Level Design

### 3.1 Pipeline stages

```text
Upload → Validate → Mezzanine → ABR Encode (parallel rungs) → Package (HLS/DASH)
      → Thumbnails/Sprites → Publish (origin) → CDN → Player ABR
Metadata/Entitlement -------------------------------↗ session token
```

### 3.2 Upload options

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| Single PUT | Simple | Large file failures | >5 GB unreliable |
| Chunked multipart | Resume, parallel | More API surface | Missing checksum compose |
| Client-side transcode | Saves server | Inconsistent quality | Trusting client as SoT for premium |

**Chosen:** Multipart chunked upload → object storage; server validates; then pipeline.

### 3.3 Mezzanine vs direct-to-ladder

| Approach | Why |
|----------|-----|
| **Mezzanine first** (chosen) | Stable source for re-ladder, thumbs, clipping; deterministic |
| Direct ladder from source | Lower cost/latency; re-encode harder; quality variance |

**Deal-breaker at product maturity:** deleting mezzanine before re-encode needs are gone—without archival policy.

### 3.4 ABR ladder design

- Offer **resolution × bitrate × frame rate** rungs (e.g. 720p30 and 720p60 as separate).  
- Audio as separate group (AAC stereo / EC-3).  
- Player switches on bandwidth + buffer (throughput/buffer-based ABR).  
- Cap max rung by device/DRM/hdcp entitlements.

**Codec:** H.264 baseline wide device; H.265/AV1 as additional codec families (duplicate ladder cost).

### 3.5 Packaging: HLS / DASH / CMAF

| Format | Role |
|--------|------|
| HLS | Apple / wide mobile |
| DASH | Android/smart TV ecosystems |
| CMAF | Common fMP4 chunks; dual manifest → one segment store |

Segment duration **2–6s** trade-off: shorter = better ABR agility / more requests; longer = fewer files / coarser seek.

### 3.6 CDN, origin, shield

```text
Player → Edge POP → (MISS) → Origin Shield → Origin Object Store
                 ↘ HIT return
```

| Technique | Purpose |
|-----------|---------|
| Origin shield | Collapse duplicate MISSes |
| Immutable versioned URLs | Cache forever (`max-age` huge) |
| Prefetch / warm | Hot launch push popular rungs |
| Multi-CDN | Capacity + ISP diversity |
| Signed URLs / cookies | Entitlement enforcement at edge |

**Deal-breaker:** Mutable segment bytes at same URL (cache poisoning / inconsistency).

### 3.7 Hot launches

1. Pre-position top ladder rungs to major POPs (or rely on multi-CDN + predictive warm).  
2. Ensure shield tier sized for simultaneous MISS coalescing.  
3. Stagger manifests if updating live-to-VOD.  
4. Rate-limit uncached trick play / obscure bitrates if needed.  
5. Control-plane cache for title metadata + tokens.

### 3.8 DRM (optional)

```text
Packager encrypts segments (CENC/CBCS) → license service issues keys
Player: request license with session auth → decrypt
```

Keep clear content path for MVP non-premium.

### 3.9 Seeking & thumbnails

- Media seek: standard media segments (keyframe-aligned).  
- UI scrub: **sprite sheets** + WebVTT/JSON mapping time → image coordinates.  
- Optional I-frame only playlist (HLS `#EXT-X-I-FRAMES-ONLY`) for trick play.

### 3.10 Multi-region storage

| Data | Strategy |
|------|----------|
| Mezzanine | Home region + async replicate OR replicate on demand |
| Packaged segments | Multi-region origins closest to audiences / CDN midgress |
| Metadata | Single-writer home cell; global read replicas |
| Hot titles | Replicate packaged assets widely; cold stay regional |

**Active-active gateways** for API; **single-writer** for title state transitions (`PROCESSING` → `READY`).

### 3.11 Trade-off tables

| Concern | Choice | Deal-breaker |
|---------|--------|--------------|
| Segment store | Object storage | Block store per node as SoT |
| Cache key | Versioned path | In-place overwrite |
| Encode queue | Priority + tenant fair share | Unbounded FIFO one tenant |
| Playback auth | Short-lived signed token | Long-lived open URLs for paid |
| Thumbs | Precomputed sprites | Generating thumbs on seek at origin |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Creators                  Viewers (global)
   |                           |
   v                           v
Upload API                Playback / Session API
   |                           |
   v                           v
Object Store (raw)        Entitlement + Token Service
   |                           |
   v                           +---- signed cookie/URL policy
Media Orchestrator                      |
   |                                    v
   +--> Mezzanine Encode          CDN Edges (multi-POP)
   +--> ABR Workers (per rung)          |
   +--> Packager (HLS/DASH)             | MISS
   +--> Thumb/Sprite Jobs               v
   |                              Origin Shield(s)
   v                                    |
Origin Buckets (packaged, versioned) <--+
   |
Metadata DB (titles, assets, versions) ── home cell
Job Scheduler (leases) for media tasks
```

### 4.2 Upload → READY sequence

```text
Client → InitiateUpload → upload_id, chunk URLs
Client → PUT chunks (parallel)
Client → CompleteUpload (checksums)
API → validate → create AssetVersion PROCESSING
Orchestrator → mezzanine job
         → parallel rung jobs (idempotent output keys)
         → package + thumbs
         → write manifests
         → CAS version READY
Webhook → notify tenant
```

### 4.3 Play + ABR sequence

```text
Player → POST /play {title} → session token + master playlist URL
Player → GET master.m3u8 (CDN)
Player → pick 720p3Mbps → GET media playlist
Player → GET segments (CDN HIT≃99%)
Bandwidth drop → switch to 480p playlist/segments
Seek → jump media sequence; show sprite frame
```

### 4.4 Hot launch

```text
T-24h: identify title; ensure all rungs packaged
T-6h: prefetch top 3 rungs to top POPs / enable predictive warm
T-0: traffic spike; shield coalesces rare MISSes
Monitor: origin Gbps, 4xx/5xx, rebuffer metrics
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **No READY without complete ladder policy** (define minimum rungs).  
2. **Immutable bytes** at published segment URL/version.  
3. **Checksummed upload** compose.  
4. **Idempotent encodes** keyed by `(asset_version, rung, codec)`.  
5. **Title state CAS** for publish.  
6. **Entitlement check** before minting play token (DRM license separate).

**Failure playbook**

| Failure | Response |
|---------|----------|
| Encode backlog | Elastic GPU/CPU; degrade optional rungs; priority for premium |
| Origin outage | Multi-region origin failover; CDN serves cached |
| Bad publish | New version; rollback playlist pointer in metadata |
| CDN POP outage | DNS/GSLB to other POPs; multi-CDN |

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single-region origin + one CDN; PG metadata; MQ for jobs |
| 10× | Shield; autoscale encoders; multipart upload service |
| 100× | Regional origins; sharded metadata; fair encode queues; prefetch tooling |
| 1000× | Multi-CDN; cold tier (mezzanine to glacier-class); cell’d tenants; AV1 selective |

**Storage cost controls**

- Delete mezzanine after N days if re-encode from highest rung acceptable (quality trade).  
- Thin ladder for long-tail titles; rich ladder for head.  
- Lifecycle: infrequent access storage class for cold titles.  
- Deduplicate uploads by content hash (optional).

### 5.3 Maintainability

- Media processing as versioned **job graphs** (see job scheduler patterns).  
- Canary packager versions; A/B ladder presets per title cohort.  
- Playback QoE dashboards (startup, rebuffer, avg bitrate, exit before video start).  
- Chaos: kill encoders; block origin; revoke CDN credentials drills.

### 5.4 Progressive scale deep dive (1× → 1000×)

**1×**

- One region object storage for raw + mezzanine + packaged.  
- One CDN distribution; origin = storage website/bucket.  
- Postgres titles/assets; SQS/Kafka for encode jobs.  
- HLS only OK for MVP if device matrix allows.

**10×**

- Origin shield layer (CDN feature or self-hosted cache).  
- Autoscale GPU/CPU encode fleet with fair queues per tenant.  
- Multipart upload service with virus/malware scan async.  
- Signed cookies/URLs for playback; session service HA.

**100×**

- Packaged assets replicated to 2–3 regional origins.  
- Metadata cells by `tenant_id` / catalog shard.  
- Hot-launch tooling: prefetch API + dashboards for origin Gbps.  
- Optional DASH via CMAF; advanced ladder presets by content type (sport vs animation).  
- QoE anomaly alerts by ISP/POP.

**1000×**

- Multi-CDN switching on error/perf.  
- Mezzanine cold tier; long-tail titles thin ladder.  
- AV1/HEVC selective for capable devices (duplicate storage cost).  
- Per-title encode optimization offline for head titles.  
- Cell’d control planes; global title directory.

### 5.5 ABR ladder engineering details

**Keyframe alignment:** segment boundaries on keyframes so switches don’t need overlap decoding artifacts.

**Bitrate spacing:** roughly 1.5–2× steps; too sparse → harsh quality jumps; too dense → storage/CDN waste.

**Audio:** often constant across video switches; separate playlist/group.

**Frame rate rungs:** expose 30 vs 60 only when source and product warrant; sports benefit; talking-head less.

**Device filtering:** master playlist generated per session capabilities (codec, DRM, resolution cap, bandwidth hint).

### 5.6 Hot-launch load math worked example

```text
Title launch: 2M concurrent viewers in 10 minutes ramp
Blended 4 Mbps
Egress = 2e6 × 4 Mb/s = 8e6 Mb/s = 8 Tbps

CDN HIT 99%:
  origin = 0.01 × 8 Tbps = 80 Gbps  (still large — multi-origin + shield)

If HIT only 90% (cold/misconfig):
  origin = 0.1 × 8 = 800 Gbps → meltdown territory
→ Prefetch + long cache TTL on immutable segments is non-negotiable
```

### 5.7 Upload integrity

```text
Initiate multipart → part ETags
Complete: recompute/validate checksum (CRC64/MD5/SHA256 per cloud)
Validate container: moov atom, duration, resolution, codec
Reject if duration=0 / encrypted unsupported / policy violation
Only then enqueue PROCESSING
```

**Resume:** client keeps `upload_id` + completed part list; server lists parts.

### 5.8 Multi-region read path vs write path

| Action | Path |
|--------|------|
| Upload | Nearest region bucket → async replicate mezzanine if needed |
| Publish READY | Home metadata cell CAS |
| Play token | Edge session service reads policy (cached) + signs |
| Segment GET | Edge CDN → regional origin |
| Title edit | Home cell only |

### 5.9 Deal-breaker gallery

| Temptation | Failure mode |
|------------|--------------|
| Mutate segment bytes in place | Cache inconsistency worldwide |
| App servers stream video | Won’t scale; kills CPU/network |
| No shield on launch | Origin death spiral |
| Infinite retention all mezzanines | Cost blowup (PB→EB) |
| Dual-region READY writers | Split-brain catalog |
| Thumbs on-demand decode | Seek UX melts origin |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Pipeline | Upload → mezzanine → ABR → CMAF/HLS(+DASH) |
| Playback | CDN-first; versioned immutable segments |
| Hot launch | Prefetch + origin shield |
| Metadata | Home-cell single-writer |
| DRM | Optional parallel path |
| Scale | Multi-region origins + multi-CDN at extreme |

### 6.2 Risks

1. Underestimating storage (PB not TB)  
2. Origin melt without shield  
3. Encode queue noisy neighbors  
4. Mutable URLs  
5. Session service overload at launch  

### 6.3 45-minute plan

| Min | Topic |
|-----|-------|
| 0–5 | VOD scope, ABR, global |
| 5–15 | Upload + pipeline |
| 15–25 | CDN/shield/hot launch |
| 25–35 | Storage math + multi-region |
| 35–45 | Seeking/DRM/QoE + traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 ABR & player

**Q: How does ABR choose bitrate?**  
A: Throughput estimate and/or buffer health; switch at segment boundaries; avoid oscillation with damping.

**Q: Why multiple frame rates?**  
A: Sports/UI may want 60fps; film 24/30; separate rungs avoid upscaling fps wastefully.

**Q: What breaks ABR?**  
A: Huge segments, missing bitrate steps (too sparse), CDN unfairness, player bugs, CAP on mobile data.

**Q: Live vs VOD ABR?**  
A: Live has sliding window playlists and latency constraints; VOD has static VODs / larger buffers.

### 7.2 Transcoding

**Q: Why mezzanine?**  
A: Consistent source for future ladders, thumbs, clipping; avoid generational loss from re-encoding a low rung.

**Q: GPU or CPU?**  
A: Both; H.264 CPU dense; live/AV1 often GPU; cost/quality trade per fleet.

**Q: How to parallelize?**  
A: Per-rung jobs; chunked encode with careful concat; shot-based for advanced systems.

**Q: Idempotent outputs?**  
A: Write to temp prefix → checksum → atomic promote to final key; job lease fencing.

### 7.3 CDN & origin

**Q: Origin shield vs more origin replicas?**  
A: Shield reduces duplicate fetches; replicas help geo and capacity—use both at scale.

**Q: Cache invalidation strategy?**  
A: Prefer versioned URLs over purge; purge for emergencies (manifest pointer).

**Q: Why signed URLs?**  
A: Bound entitlement/time/IP/path; prevent hotlinking unpaid content.

**Q: Multi-CDN complexity?**  
A: Different purge/APIs; need abstraction; steering by performance/error rate.

### 7.4 Hot launch traps

**Q: Manifest cached old?**  
A: Short TTL on master playlist pointer or version bump query param; segments long TTL.

**Q: Thundering herd on token API?**  
A: Cache policy responses; horizontal scale session service; edge-issued tokens with JWT + revocation lists carefully.

**Q: Prefetch cost?**  
A: Prefetch only head titles/top rungs; don’t warm entire catalog.

### 7.5 Storage math traps

**Q: 1M titles × 8 GB = ?**  
A: 8 PB packaged (order), not 8 TB. 1M×8GB=8M GB=8 PB.

**Q: Egress 10M × 3 Mbps?**  
A: 30 Tbps.

**Q: Keep all mezzanines forever?**  
A: Cost blowup; lifecycle policy essential at 100×+.

### 7.6 Seeking & thumbs

**Q: How do YouTube-style hover previews work?**  
A: Sprite sheets + time maps; not decoding full GOP from origin per hover.

**Q: Accurate frame seek?**  
A: Segment granularity + decoder; frame-accurate needs I-frame density / separate trick-play.

### 7.7 DRM & security

**Q: Where do keys live?**  
A: KMS/HSM; license service; never in CDN logs; rotate with new versions.

**Q: CDN still needed with DRM?**  
A: Yes—CDN caches encrypted segments; license is separate.

**Q: Piracy?**  
A: Watermarking (forensic), DRM, account abuse detection—layered.

### 7.8 Multi-region

**Q: Should metadata be active-active?**  
A: Dangerous for publish CAS. Home cell writer; global readers.

**Q: Where should mezzanine sit?**  
A: Upload region first; replicate if encode fleet elsewhere; avoid cross-region read during every encode if costly.

**Q: Cross-region CDN midgress?**  
A: Private interconnect / multi-region origins to cut latency and origin fees.

### 7.9 Reliability drills

**Q: Half of encoders die?**  
A: Queue lag rises; keep ingest; delay READY; optional partial ladder publish policy.

**Q: Wrong segments published?**  
A: Immutable versioning saves you—publish new version; flip pointer; purge manifests.

**Q: Clock skew on signed URLs?**  
A: Short skew leeway; NTP; use exp absolute times.

### 7.10 Formats & protocols

**Q: HLS vs DASH?**  
A: Manifest differences; CMAF unifies media. Support both if device matrix requires.

**Q: Why fMP4 over TS?**  
A: CMAF sharing, MSE cleanliness, codec agility; TS still common legacy HLS.

**Q: Caption strategy?**  
A: Sidecar VTT; in-band for some; never burn-in as only option.

### 7.11 QoE & analytics

**Q: What KPIs?**  
A: Video start failure, time-to-first-frame, rebuffer ratio, average bitrate, exits, error codes by CDN/POP.

**Q: Can analytics be lossy?**  
A: Yes—sample; don’t block playback.

### 7.12 Product edge cases

**Q: Replace a title’s video but keep URL?**  
A: New asset version; update play pointer; old version retained for in-flight viewers.

**Q: 8-hour upload on mobile?**  
A: Chunked resume; background upload; compress guidance; validate.

**Q: 4K/HDR/Dolby?**  
A: Extra rungs + metadata; device capability filtering in master playlist generation (session-specific manifests).

### 7.13 Comparison

**Q: vs plain S3 + CloudFront static files?**  
A: Missing encode ladder, packaging, entitlements, hot-launch, metadata state machine, thumbs.

**Q: Build packager or use media services?**  
A: Buy early; differentiate on workflow, QoE, catalog—revisit build at scale/cost.

### 7.14 Interview trap: ownership of work

**Q: Who decides READY?**  
A: **Orchestrator/control plane** after required artifacts exist—not a random encoder flipping status without CAS.

**Q: Cancel upload vs cancel encode?**  
A: Cancel upload aborts compose; cancel encode marks version `CANCELLED` and stops leasing new rung jobs; completed rungs GC’d by lifecycle.

---

## 8. Appendices

### 8.1 Metadata schema sketch

```text
titles(title_id, tenant_id, name, ...)
assets(asset_id, title_id, type=video)
asset_versions(version_id, asset_id, state, source_checksum, mezzanine_key, created_at)
renditions(version_id, rung_id, codec, width, height, fps, bitrate, prefix_uri)
manifests(version_id, protocol, uri)
sprites(version_id, vtt_uri, image_uris[])
play_policies(title_id, geo_rules, drm_required)
```

### 8.2 Example ladder preset (JSON-ish)

```text
rungs: [
  {name:360p, w:640, h:360, fps:30, v_bitrate_kbps:800},
  {name:720p30, w:1280, h:720, fps:30, v_bitrate_kbps:3000},
  {name:720p60, w:1280, h:720, fps:60, v_bitrate_kbps:4500},
  {name:1080p30, w:1920, h:1080, fps:30, v_bitrate_kbps:6000}
]
audio: [{codec:aac, bitrate_kbps:128}]
segment_seconds: 4
```

### 8.3 Launch checklist

- [ ] Minimum rungs encoded & packaged  
- [ ] Manifests versioned & validated  
- [ ] Tokens/entitlements configured  
- [ ] CDN path cached/prefetched for top rungs  
- [ ] Origin shield healthy  
- [ ] QoE dashboards & pages ready  
- [ ] Rollback pointer tested  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Mezzanine | High-quality intermediate master |
| ABR | Adaptive bitrate streaming |
| Rendition / rung | One quality encoding |
| CMAF | Common Media Application Format (fMP4) |
| Origin shield | Intermediate cache coalescing origin fetches |
| VODs playlist | Static complete HLS playlist |
| Scrubbing | UI seek preview via sprites |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Chunked upload, ladder, HLS, CDN, metadata states |
| 10× | Shield, autoscale encode, signed playback |
| 100× | Multi-region origin, fair encode, prefetch launches |
| 1000× | Multi-CDN, storage tiering, cell’d metadata, codec expansion |

### 8.6 Cost model sketch (order-of-magnitude)

```text
Assume blended CDN egress price ~$0.02/GB (varies widely; use for interview sense)
Baseline peak 0.3 Tbps sustained for 1 hour of “peak evening”:
  0.3e12 bit/s ÷ 8 = 37.5e9 B/s ≈ 37.5 GB/s
  × 3600 s ≈ 135 TB / peak-hour
  × $0.02 ≈ $2.7K for that hour (illustrative)

At 100× (30 Tbps): ×100 → ~$270K / similar peak-hour — why hit ratio & multi-CDN deals matter.

Storage at 14 PB (10× catalog rough):
  $0.02/GB-month × 14e9 GB = enormous → tiering mandatory (not all on hot SSD/S3 std).
```

### 8.7 Encode job graph (ownership resolved)

```text
AssetVersion created PROCESSING
  Orchestrator owns state CAS (not individual encoders)
  Jobs:
    J_mezz → outputs mezzanine_key
    J_rung[i] for each ladder entry (parallel; depends on J_mezz or source policy)
    J_package depends on all required J_rung
    J_thumbs parallel with package
  Only Orchestrator marks READY when required artifacts present
Cancel encode: Orchestrator sets CANCELLED; workers observe cancel token / lease not renewed
```

**Deal-breaker:** encoder worker flips `READY` without verifying sibling rungs.

### 8.8 Manifest examples (conceptual)

```text
# Master playlist (HLS)
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360,FRAME-RATE=30
v/360p30/prog.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1280x720,FRAME-RATE=30
v/720p30/prog.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=4500000,RESOLUTION=1280x720,FRAME-RATE=60
v/720p60/prog.m3u8
```

Session-specific masters may filter rungs by device DRM/hdcp/plan.

### 8.9 Interview “say this” summary (60 seconds)

> Upload to object storage with multipart resume; validate; encode a mezzanine then an ABR ladder; package CMAF with HLS/DASH manifests under **versioned immutable URLs**; play through a global CDN with origin shield; mint short-lived play tokens after entitlement checks; precompute sprites for scrubbing; scale metadata as single-writer home cells; for hot launches prefetch top rungs and watch origin Gbps. Storage is **PB-scale** at serious catalogs—lifecycle tiering is part of the design, not an afterthought.

### 8.10 Extra interviewer traps (quick)

| Trap | Correct pushback |
|------|------------------|
| “Store all qualities as one progressive MP4 on S3” | Breaks ABR & CDN segment caching efficiency |
| “Purge CDN on every publish” | Prefer versioned paths; purge is emergency |
| “Active-active both regions mark READY” | Dual publish races; home CAS |
| “Thumbnails generated on seek at origin” | Origin melt; precompute sprites |
| “Average bitrate 50 Mbps for planning” | Blended living-room ABR often ~3–5 Mbps; know your product mix |
| “1M titles × 8 GB = 8 TB” | **8 PB** |

### 8.11 Reliability test plan

1. Kill packager mid-write → no partial READY; retry idempotent promote.  
2. Origin region down → CDN serves HIT; MISS fails over to secondary origin.  
3. Corrupt mezzanine checksum → fail version; alert.  
4. Token service overload at launch → cache policy; shed noncritical reads.  
5. Wrong ladder published → flip pointer to previous version; purge master manifests.  

### 8.12 Related systems map

```text
Upload Service → Object Storage
Media Orchestrator → Job Scheduler (leases) → GPU/CPU fleets
Packager → Origin buckets
Session/Entitlement → Edge tokens
CDN / Multi-CDN → Players
QoE pipeline → Analytics warehouse
DRM license service (optional) → Players
```

---

*End of global video streaming system design.*
