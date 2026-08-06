# System Design: Video Streaming Service (Netflix-Like)

> **Focus areas:** Ingest & encode pipeline · Adaptive bitrate (ABR) · CDN origin · Manifest & segments · Playback client · DRM overview · QoE · Live vs VOD · Scale & cost  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split QPS (playback start vs segment vs encode), explicit latency budgets, deal-breakers on origin-serving all viewers, Netflix streaming 2025–26 themes  
> **Interview theme:** Design a Netflix-like video streaming platform from upload to smooth adaptive playback globally

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

Goal: **bound video streaming**—from content ingest through multi-bitrate encoding, global delivery via CDN, DRM-protected adaptive playback, and quality monitoring at Netflix-scale concurrency.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | End-to-end streaming platform | Homepage personalization |
| Content | VOD primary; live overview | Full live sports stack deep dive |
| Delivery | CDN + ABR segments | P2P-only delivery |
| Security | DRM overview (Widevine/FairPlay/PlayReady) | Full license server legal deep dive |
| Client | TV/mobile/web player behavior | UI design |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Content types? | Movies, series, trailers, previews | Title/episode model |
| F2 | Upload path? | Studio mezzanine → internal ingest | Object storage + workflow |
| F3 | Encoding? | Multi-bitrate H.264/HEVC/AV1 ladder | Transcode farm |
| F4 | Packaging? | DASH/HLS fMP4 segments | Manifest service |
| F5 | Playback start? | < 2–5s on good network | CDN + warm connections |
| F6 | ABR? | Client switches rungs on bandwidth | Multiple renditions |
| F7 | DRM? | Required for premium content | EME + license |
| F8 | Subtitles/audio? | Multi-language tracks | Sidecar / embedded |
| F9 | Resume? | Continue watching position | Playback state service |
| F10 | Download offline? | Optional encrypted offline | License persistence |
| F11 | 4K/HDR? | Premium tiers | Higher rungs + CDNs |
| F12 | Thumbnails? | Trick play / scrubbing | Sprite sheets / I-frame playlists |
| F13 | Analytics? | Startup time, rebuffer, bitrate | QoE beacons |
| F14 | Regional rights? | Geo availability | Entitlement at manifest |
| F15 | Device caps? | Max resolution per plan/device | Policy in manifest |

**MVP functional scope:**

1. Ingest mezzanine to object storage; workflow orchestrates encode.  
2. Transcode to ABR ladder (e.g. 240p–1080p); store segments in origin.  
3. Publish DASH/HLS manifests referencing CDN URLs.  
4. Client: entitlement check → manifest → ABR segment fetch from CDN → decode → render.  
5. DRM: encrypt segments; license on playback start.  
6. Resume position read/write per profile.  
7. QoE events: startup, rebuffer, error, bitrate switches.

**Out of MVP:**

- Full live linear channel origin (outline only)  
- Client-side ML super-resolution  
- Peer-assisted delivery as primary  
- Studio-side editing tools  
- Full forensic watermarking pipeline

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Startup time | Fast TTFF | p50 < 2s; p99 < 5s good network |
| N2 | Rebuffer rate | Low | < 0.5% viewing hours |
| N3 | Availability | Highly available playback | 99.99% manifest+CDN path |
| N4 | Scale | Millions concurrent | See scale table |
| N5 | Encode SLA | Hours not days for VOD | Pipeline SLAs per priority |
| N6 | Cost | CDN egress dominates | Cache hit ratio > 90% |
| N7 | Security | No clear stream for DRM titles | Encryption end-to-end |
| N8 | Global | Multi-region | Origin + CDN PoPs |
| N9 | Accessibility | Captions, audio description | Track metadata |
| N10 | Observability | Per-title QoE | Aggregated dashboards |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User presses play → entitlement OK → manifest → license → first segment → video starts.  
2. Bandwidth drops → player downgrades rung seamlessly.  
3. User scrubs → nearest keyframe segment fetched.  
4. Episode ends → autoplay next (sibling).  
5. 4K TV on premium plan → highest allowed rung.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| CDN miss on cold title | Origin fetch; slower startup |
| License server slow | Parallelize; timeout → error UX |
| Manifest stale after encode | Versioned manifest URLs |
| Device lacks codec | Offer compatible rung only |
| Geo blocked | 403 at manifest |
| Partial segment download | Retry; ABR downgrade |
| Clock skew DRM | Server time sync |
| Origin overload premiere | Pre-warm CDN; stagger release |
| Corrupt segment | Hash verify; alternate CDN path |
| Kids profile maturity | Block manifest |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Subscribers | 50M | 150M | 250M | 300M+ |
| Peak concurrent streams | 5M | 50M | 100M | 150M |
| Catalog hours | 100K | 500K | 2M | 5M |
| New hours ingested/day | 500 | 2K | 10K | 50K |
| Encode jobs/day | 5K | 50K | 200K | 1M |
| Segment requests/s (CDN) | 10M | 100M | 500M | 2B |
| Manifest requests/s | 50K | 500K | 2M | 10M |
| Avg bitrate | 5 Mbps | 6 Mbps | 8 Mbps | 10 Mbps |
| Storage (encoded) | 10 PB | 50 PB | 200 PB | 1 EB class |

**Split classes:** encode batch ≠ manifest QPS ≠ segment QPS ≠ license QPS ≠ QoE ingest.

**What each jump forces:**

- **10×:** CDN caching discipline; encode farm autoscale; manifest edge cache.  
- **100×:** Open Connect style appliances; regional origins; ladder optimization per device class.  
- **1,000×:** Massive edge cache; per-title pre-warm; codec portfolio (AV1); cell-based origins.

### 1.5 Etc. (Constraints & Assumptions)

- **Netflix-like** subscription VOD with global rights complexity.  
- CDN sibling deep dive: `cdn-system-design.md`.  
- Playback couples to entitlement / profile (personalization sibling).  
- Ads tier may share infra with separate manifest flags (optional mention).

**Scope statement:**

> Design a Netflix-like video streaming service covering ingest, encode, manifest publishing, CDN-backed ABR delivery, DRM-protected playback, and QoE — scaling from ~5M concurrent streams through 10× / 100× / 1,000× with origin offload as the primary lever.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Concurrent streams & bandwidth

```text
Peak concurrent = 5,000,000 streams
Avg bitrate = 5 Mbps
Aggregate egress = 5M × 5 Mbps = 25 Pbps = 3.125 TB/s

Impossible from single origin — MUST be edge-cached CDN (Open Connect model)
CDN cache hit 95% → origin still 156 GB/s class at baseline — huge but manageable distributed
```

At **100×** concurrent (hypothetical stress): **625 TB/s aggregate** — edge-only architecture mandatory.

### 2.2 Segment request rate

```text
Segment duration ≈ 2–6 seconds (4s typical)
Requests per stream ≈ 0.25 / s
Segment QPS ≈ 5M × 0.25 = 1.25M / s baseline

Long tail catalog mostly cached; blockbuster premiere spikes single-title QPS
```

### 2.3 Manifest request rate

```text
One manifest per play start + periodic refresh (live/DVR)
~50K starts/s peak baseline if avg session long
Manifest tiny (~50–200 KB) but latency-critical
Edge cache manifest with short TTL
```

### 2.4 Encode pipeline

```text
1 hour mezzanine → ladder 10 rungs → ~10–40 hours CPU-GPU equivalent (parallelized)
500 new hours/day → 5K–20K GPU-hours/day baseline
Priority queue: premiere > backlog > catalog remaster
Storage per hour encoded ≈ 10–50 GB depending on rungs
500 hours × 30 GB ≈ 15 TB/day new storage
```

### 2.5 Storage totals

```text
100K catalog hours × 30 GB ≈ 3 EB? — actually 100K × 30GB = 3 PB encoded baseline class
Replication + multi-region → 3×
Cold archive mezzanine separate tier
```

### 2.6 License server QPS

```text
~1 license per playback start (renewals periodic)
≈ 50K / s baseline peak starts
Must be low-latency HA cluster; often colocated regionally
```

### 2.7 QoE event volume

```text
Events per viewing hour ≈ 10–50 (heartbeat, switches)
5M streams × 2 hr avg × 20 events/hr ≈ 200M events/hr ≈ 55K/s
Sample + aggregate; pipeline to data warehouse
```

### 2.8 Latency budget (startup)

| Stage | Budget |
|-------|--------|
| Entitlement | 20–50ms |
| Manifest fetch (CDN) | 30–100ms |
| License | 100–300ms |
| First segment (CDN) | 50–200ms |
| DRM decrypt + demux | 50–100ms |
| Buffer target | 1–2s media |
| **TTFF target** | **< 2–5s p99** |

### 2.9 Critical bottlenecks

1. Origin egress without CDN  
2. Cold cache premiere thundering herd  
3. Encode backlog before launch date  
4. License latency blocking start  
5. Manifest errors wrong rungs  
6. DRM device fragmentation  

### 2.10 Cost intuition

```text
CDN egress $ dominates at scale
Encode capex/opex second
Origin storage third
Optimize: cache hit ratio, ladder efficiency (AV1), off-peak encode
```

---

## 3. High-Level Design

### 3.1 Pipeline stages

```text
Upload → Validate → Transcode → Package → Publish manifest → CDN propagate → Playback
                ↓
            QC / audio layback / subtitles
                ↓
            Metadata → Catalog service
```

### 3.2 Core entities

| Entity | Role |
|--------|------|
| `Title` / `Episode` | Catalog identity |
| `Mezzanine` | High-quality source object |
| `EncodingProfile` | Ladder definition per device class |
| `Rendition` | One bitrate/resolution rung |
| `Segment` | Fixed-duration chunk file |
| `Manifest` | MPD/m3u8 index |
| `PlaySession` | Client playback context |
| `License` | DRM keys for session |

### 3.3 Encoding ladder (example)

| Rung | Resolution | Video bitrate | Codec |
|------|------------|---------------|-------|
| 0 | 384×216 | 400 kbps | H.264 |
| 1 | 640×360 | 800 kbps | H.264 |
| 2 | 960×540 | 1.5 Mbps | H.264 |
| 3 | 1280×720 | 3 Mbps | H.264/HEVC |
| 4 | 1920×1080 | 5 Mbps | H.264/HEVC |
| 5 | 3840×2160 | 15 Mbps | HEVC/AV1 |

Separate audio rungs (64–192 kbps AAC).

### 3.4 Packaging

- **fMP4** segments + **CMAF** where possible for DASH/HLS unify.  
- Segment duration 4s common (balance startup vs switch latency).  
- **Manifest** lists segment URLs, codecs, DRM init data, subtitle tracks.

### 3.5 Playback API (logical)

```text
POST /play/start { title_id, profile_id, device_caps }
  → { manifest_url, license_url, resume_offset_ms, max_resolution }

GET manifest_url (CDN) → MPD/m3u8
GET segments (CDN) → encrypted bytes
POST license_url → content keys
```

### 3.6 ABR algorithm (client)

```text
Loop:
  measure throughput + buffer level
  if buffer low → downgrade rung
  if throughput high sustained → upgrade rung
  fetch next segment at chosen rung
Player examples: proprietary / ExoPlayer / AVPlayer / HTML5 MSE
```

### 3.7 DRM overview

| Component | Role |
|-----------|------|
| Content Key | AES-128/CTR encrypt segments |
| KMS | Store root keys; rotate |
| DRM provider | Widevine / FairPlay / PlayReady |
| License server | Exchange auth token for keys |
| Client CDM | Secure decrypt in TEE |

Flow: manifest contains `ContentProtection` → CDM creates license challenge → license server validates entitlement → returns keys → decrypt segments in hardware.

### 3.8 Resume / Continue Watching

Nearline store: `(profile_id, title_id) → position_ms, updated_at`.  
Read on play/start; write heartbeat every N seconds (debounced).

### 3.9 Origin vs CDN

**Rule:** Origin stores golden copy; **CDN serves >95% bytes**.  
Open Connect: ISP-embedded caches (see cdn-system-design sibling).

### 3.10 Trade-offs

| Topic | Decision |
|-------|----------|
| Segment length | 4s MVP |
| Codec | H.264 baseline; HEVC/AV1 premium |
| DRM | Required premium |
| Manifest | Versioned immutable URLs |
| Encode | Async workflow; SLA tiers |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Studio ──upload──> +-------------+     +----------------+
                    | Ingest API  |────>| Object Storage |
                    +------+------+     | (mezzanine)    |
                           |            +--------+-------+
                           v                     |
                    +-------------+              |
                    | Workflow    |<─────────────┘
                    | Orchestrator|
                    +------+------+
                           |
              +------------+------------+
              v            v            v
        +----------+ +----------+ +----------+
        | Transcode| | QC       | | Subtitles|
        | workers  | |          | | / audio  |
        +----+-----+ +----------+ +----------+
             |
             v
        +----------+     publish    +----------------+
        | Encoded  |---------------->| Manifest Svc   |
        | segments |                 +-------+--------+
        +----+-----+                         |
             |                               v
             +---------------------------->+ CDN / Open Connect +
                                             +--------+---------+
                                                      |
  +--------+  play start                             |
  | Client |<-----------------------------------------+
  +--------+
      |  license ──> +---------------+
      +─────────────>| License (DRM) |
                    +---------------+
      | QoE ───────> +---------------+
      +─────────────>| Analytics     |
                    +---------------+
```

### 4.2 Sequence: playback start

```text
Client→PlayAPI: start(title, profile)
PlayAPI→Entitlement: check rights
PlayAPI→Resume: get offset
PlayAPI→Client: manifest_url, license_url, offset
Client→CDN: GET manifest
Client→License: challenge + auth token
License→Client: content keys
Client→CDN: GET init + segment 0..N
Client: decrypt, buffer, render
Client→QoE: startup_ms, first_bitrate
```

### 4.3 Sequence: ABR switch

```text
Client: buffer trending low
Client: select lower rung from manifest
Client→CDN: GET segment k at lower rung
Seamless switch at segment boundary (aligned GOP)
QoE: switch_event
```

### 4.4 Encode workflow

```text
Upload complete → validate checksum
Enqueue transcode job (priority)
Workers: mezzanine → renditions → segments
QC gate: PSNR/SSIM thresholds, loudness
Publish manifest version v1
CDN pre-warm job for premiere titles
Catalog update playable=true
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Never serve unencoded mezzanine** to consumer clients.  
2. **Manifest version immutable** once published (new encode → new URL).  
3. **DRM keys never in clear** on client except inside CDM.  
4. **Entitlement before license**.  
5. **Segment integrity** — checksum/CRC verified optional.  
6. **CDN origin fallback** without melting origin (rate limits).  
7. **Resume monotonic** — don’t rewind unless user seeks.  
8. **Geo policy enforced** at play start and manifest.

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Cloud CDN + transcode cluster; single region origin |
| 10× | Multi-region origin; CDN pre-warm; encode autoscale |
| 100× | Open Connect appliances; manifest edge; license regional |
| 1,000× | AV1 ladder; cell origins; premiere isolation; QoE sampled |

### 5.3 Encode pipeline deep dive

- **Priority queues:** launch window > catalog backfill.  
- **Split jobs:** per-rung parallel transcode from mezzanine.  
- **Spot/preemptible workers** for non-urgent with checkpoint.  
- **Per-title profiles:** animation vs action different ladders.  
- **QC automation:** black frame, silence, caption sync.

### 5.4 Manifest design

```text
Manifest {
  title_id, version,
  periods[], adaptationsets[],
  video_renditions[], audio_renditions[], text_renditions[],
  content_protection[],
  segment_template: url_pattern CDN-based
}
URL: https://cdn.../title/episode/v3/manifest.mpd
```

Short TTL on dynamic live; long immutable TTL on VOD versioned path.

### 5.5 CDN coupling

- Segments named with hash/version → cache forever until re-encode.  
- **Pre-warm** before global premiere.  
- **Midnight release** stagger by timezone optional.

### 5.6 DRM deep dive (interview level)

- **Multi-DRM:** pack once with CMAF + common encryption; different PSSH boxes.  
- **License binding:** device cert, session, output protection (HDCP).  
- **Renewal:** long sessions re-license periodically.  
- **Offline:** persistent license with expiry; download encrypted file.

### 5.7 Live vs VOD (overview)

| Aspect | VOD | Live |
|--------|-----|------|
| Origin | Static segments | Rolling window DVR |
| Manifest | Static | Dynamic MPD update |
| Latency | N/A | Low-latency HLS/DASH chunks |
| Scale spike | Premiere | Event simultaneous |

### 5.8 QoE & observables

Metrics: `startup_ms`, `rebuffer_ratio`, `avg_bitrate`, `error_rate`, `exit_before_start`.  
Per-CDN PoP comparison drives routing fixes.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Origin serves all viewers | Instant death at scale |
| Single bitrate | Buffering on variable networks |
| No DRM on premium | Content theft |
| Mutable manifest URL same path | Cache poison / stale |
| License before entitlement | Geo/payment bypass |
| Huge segments (30s) | Slow startup & seek |
| Ignore device caps | Waste bandwidth / incompatibility |

### 5.10 Progressive scale deep dive

**1× (~5M concurrent)**  
Commercial CDN + origin; GPU encode farm; centralized license.

**10×**  
Regional origins; manifest CDN cache; ladder per device class; QoE pipeline.

**100×**  
Open Connect embedded caches; AV1 for mobile; cell-based premiere isolation.

**1,000×**  
Global pre-warm orchestration; edge license delegates; advanced congestion control per ISP.

### 5.11 Security

- Signed URLs optional for manifest (TTL).  
- TLS everywhere.  
- Token bound to profile/device.  
- Watermarking forensic (optional premium).

### 5.12 Multi-region

- Origin replicated cross-region async.  
- CDN local PoPs.  
- License server regional HA.  
- Metadata/catalog global read.

### 5.13 Rollout

```text
Encode → staging manifest → QA playback matrix devices → CDN pre-warm → flip catalog flag
Canary QoE on new codec ladder
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Delivery | CDN-first; origin for misses |
| Format | CMAF/fMP4 + DASH/HLS |
| ABR | Client-driven multi-rung |
| DRM | Multi-DRM license server |
| Encode | Async workflow + QC |
| Resume | Profile-scoped store |

### 6.2 Risks

1. Premiere CDN cold start  
2. Encode missing launch SLA  
3. DRM device quirks  
4. License latency  
5. Cost at 4K/AV1 adoption  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope VOD; split QPS classes |
| 5–15 | Ingest → encode → manifest |
| 15–25 | CDN + ABR + bandwidth math |
| 25–35 | DRM + license flow |
| 35–45 | Scale, premiere, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Encoding

**Q: Why multiple rungs?**  
A: Match variable bandwidth; minimize rebuffer.

**Q: Segment size tradeoff?**  
A: Shorter → faster start/switch; more requests. Longer → opposite.

**Q: AV1 vs HEVC?**  
A: AV1 better compression; higher encode cost; device support evolving.

### 7.2 Delivery

**Q: Why CDN not origin?**  
A: TB/s aggregate egress impossible centrally.

**Q: Cache hit ratio target?**  
A: >90–95% bytes from edge.

**Q: Open Connect?**  
A: ISP-local Netflix caches — see cdn doc.

### 7.3 Playback

**Q: ABR who decides?**  
A: Client algorithm using throughput + buffer.

**Q: Seek behavior?**  
A: Fetch nearest sync sample / I-frame segment.

### 7.4 DRM

**Q: Why DRM if HTTPS?**  
A: HTTPS protects transport; DRM protects content at rest on device.

**Q: License vs manifest order?**  
A: Manifest first to know PSSH; license before decrypt segments.

### 7.5 Scale

**Q: 100M concurrent?**  
A: Edge-only bytes; manifest/license scale horizontally; encode pre-position content.

### 7.6 Traps

**Q: “Store video in database”?**  
A: Object storage + CDN.

**Q: “Single MP4 file progressive download”?**  
A: Poor for ABR and seeking at scale.

**Q: “Transcode on play request”?**  
A: Latency unacceptable; offline encode.

### 7.7 Resume

**Q: How fresh CW?**  
A: Heartbeat nearline; sibling personalization doc.

### 7.8 Live

**Q: Live differences?**  
A: Rolling manifest; lower segment duration; origin push path.

---

## 8. Appendices

### A1. Segment URL pattern

```text
https://oc-cdn.example.net/video/{title}/{version}/{rendition}/seg_{n}.m4s
```

### A2. Play start response

```text
PlayStartResponse {
  manifest_url,
  license_url,
  drm_scheme: WIDEVINE|FAIRPLAY|PLAYREADY,
  resume_offset_ms,
  max_video_resolution,
  expiry_ts
}
```

### A3. Encode job schema

```text
EncodeJob {
  job_id, mezzanine_uri, profile_id, priority,
  renditions[], status, qc_status, output_prefix
}
```

### A4. Launch checklist

- [ ] Ladder QC passed  
- [ ] DRM tested device matrix  
- [ ] CDN pre-warm complete  
- [ ] Manifest immutable URL  
- [ ] Entitlement rules verified  
- [ ] QoE dashboards live  

### A5. Glossary

| Term | Meaning |
|------|---------|
| ABR | Adaptive bitrate |
| Mezzanine | High-quality source master |
| Rung | One bitrate step in ladder |
| MPD | DASH manifest |
| CDM | Content Decryption Module |
| TTFF | Time to first frame |

### A6. 60-second summary

> Upload mezzanine → **offline transcode** to multi-rung segments → **versioned manifest** on CDN → client **ABR** fetches encrypted segments → **DRM license** after entitlement → QoE telemetry. Scale by **never origin-serving mass traffic**, pre-warm premieres, and regional Open Connect caches.

### A7. Related systems

```text
Ingest → Encode → Manifest → CDN (sibling doc)
Play API → Entitlement + Resume
Client player → ABR + DRM
QoE → Data platform
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| TTFF p99 | < 5s |
| Rebuffer ratio | < 0.5% hours |
| Playback availability | 99.99% |
| Encode SLA premiere | T-24h complete |

### A9. Bandwidth worked example

```text
5M streams × 5 Mbps = 25 Pbps aggregate
95% CDN hit → origin 1.25 Pbps still large → requires thousands of edge nodes
```

### A10. Device matrix (sample)

| Device | Max rung | DRM |
|--------|----------|-----|
| Web Chrome | 1080p | Widevine |
| iOS | 4K HDR | FairPlay |
| Smart TV 2018 | 1080p HEVC | Widevine L1 |
| Basic plan phone | 480p cap | Widevine L3 |

### A11. Ownership

| Concern | Owner |
|---------|-------|
| Encode pipeline | Media platform |
| CDN/Open Connect | CDN engineering |
| Play API | Streaming services |
| DRM | Security + partners |
| Player | Client teams |

### A12. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | ABR + CDN + DRM basics |
| 10× | Pre-warm + regional origin |
| 100× | Open Connect + AV1 partial |
| 1,000× | Premiere isolation cells |

### A13. On-call

1. Rebuffer spike → CDN PoP / ISP issue.  
2. Startup spike → license or manifest.  
3. Single title errors → bad encode/manifest version.  
4. Geo leak → entitlement bug.

### A14. Naive comparison

| Naive | Failure |
|-------|---------|
| One MP4 progressive | No ABR |
| Origin only | Bandwidth collapse |
| Runtime transcode | Latency |
| Clear segments | Piracy |

### A15. Cost worksheet

```text
cdn_egress_cost ≈ total_TB × $/TB × (1 - hit_ratio_improvement)
encode_cost ≈ GPU_hours × $/hr
storage ≈ PB × $/PB/month
```

### A16. Non-goals

- Full live sports production  
- In-player social features  
- Server-side ABR (SABR) deep dive  

### A17. Subtitle architecture

```text
WebVTT/TTML sidecar tracks in manifest
Separate segments or muxed in fMP4
Importers from studio TTML
```

### A18. Interviewer rubric

- [ ] Split segment vs manifest QPS  
- [ ] Bandwidth math  
- [ ] CDN not origin  
- [ ] DRM flow  
- [ ] Encode offline  
- [ ] Premiere pre-warm  

### A19. Autoplay next episode

Sibling: playback hands off to next manifest URL; encode already done; CW updated via heartbeat.

### A20. Sample QoE event

```text
{
  "event": "startup",
  "title_id": "...",
  "startup_ms": 1800,
  "first_bitrate_kbps": 3000,
  "cdn_pop": "lax-47",
  "device_class": "tv"
}
```

---

*End of document — Netflix system design interview prep: Video Streaming Service.*
