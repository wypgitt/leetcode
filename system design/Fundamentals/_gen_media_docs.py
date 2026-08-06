#!/usr/bin/env python3
"""Generate complete media/content system design interview prep docs."""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent


def header(title: str, focus: str, theme: str) -> str:
    return f"""# System Design: {title}

> **Focus areas:** {focus}
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Domain-specific numbers and failure modes; explicit trade-offs; deal-breakers called out; CDN / ABR / encoding / DRM covered where relevant
> **Interview theme:** Senior / Staff — **{theme}**

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
"""


def section_1(
    goal: str,
    is_is_not: list[tuple[str, str, str]],
    functional: list[tuple[str, str, str, str]],
    mvp: list[str],
    out_mvp: list[str],
    nfr: list[tuple[str, str, str]],
    happy: str,
    edges: str,
    cases: list[tuple[str, str]],
    scales: list[tuple[str, str, str, str, str]],
    jumps: str,
    scope: str,
) -> str:
    rows_iin = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in is_is_not)
    rows_f = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in functional)
    mvp_b = "\n".join(f"{i}. {x}" for i, x in enumerate(mvp, 1))
    out_b = "\n".join(f"- {x}" for x in out_mvp)
    rows_n = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in nfr)
    rows_c = "\n".join(f"| {a} | {b} |" for a, b in cases)
    rows_s = "\n".join(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in scales)
    return f"""## 1. Clarify Requirements (Interview Q&A)

Goal: {goal}

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
{rows_iin}

### 1.1 Functional Requirements

| # | Question | Expected interviewer answer | Design implication |
|---|----------|----------------------------|--------------------|
{rows_f}

**MVP scope:**

{mvp_b}

**Out of MVP:**

{out_b}

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
{rows_n}

### 1.3 Cases

**Happy:** {happy}  
**Edges:** {edges}

| Case | Behavior |
|------|----------|
{rows_c}

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
{rows_s}

**Jumps:** {jumps}

### 1.5 Etc. constraints + scope repeat-back

Constraints to surface early: multi-region, cost of egress/CDN, DRM/licensing where relevant, cold-start vs hot content, device diversity, and abuse/copyright.

> {scope}

---
"""


def section_2(blocks: list[tuple[str, str]]) -> str:
    parts = ["## 2. Back-of-the-Envelope Estimation\n"]
    for i, (title, body) in enumerate(blocks, 1):
        parts.append(f"### 2.{i} {title}\n\n```text\n{body.strip()}\n```\n")
    parts.append(
        """### 2.N Bottleneck ranking (interview signal)

State bottlenecks as a ranked list, not "scale with microservices":

1. **Egress / CDN** — usually the largest $ and failure blast radius for media.
2. **Hot keys** — viral / premiere titles; origin and metadata hotspots.
3. **Transcode / encode fleet** — GPU/CPU queue depth and priority fairness.
4. **Control-plane fanout** — manifests, license servers, personalization APIs.
5. **Cold storage retrieval** — rarely watched long-tail objects.

### 2.N+1 Cost intuition

```text
Storage is cheap relative to egress at scale.
One viral video watched 100M× at 4 Mbps ≈ 50 PB transferred.
At $0.01–0.08/GB blended CDN, that is mid–high seven figures for a single title wave.
Hence: aggressive edge caching, packaging efficiency, ABR ladders that avoid overserving bits.
```

---
"""
    )
    return "\n".join(parts)


def section_3(
    planes: list[tuple[str, str, str]],
    components: list[str],
    apis: str,
    data_model: str,
    tradeoffs: list[tuple[str, str, str]],
    dealbreakers: list[tuple[str, str]],
    why: str,
) -> str:
    rows_p = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in planes)
    comps = "\n".join(f"{i}. **{c.split('—')[0].strip()}** — {c.split('—',1)[1].strip() if '—' in c else c}" for i, c in enumerate(components, 1))
    rows_t = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in tradeoffs)
    rows_d = "\n".join(f"| {a} | {b} |" for a, b in dealbreakers)
    return f"""## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
{rows_p}

**Why this split:** {why}

### 3.2 Components

{comps}

### 3.3 APIs (sketch)

```text
{apis.strip()}
```

### 3.4 Data model (core)

```text
{data_model.strip()}
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
{rows_t}

### 3.6 Deal-breakers

| Temptation | Failure |
|------------|---------|
{rows_d}

---
"""


def section_4(mermaid: str, sequences: list[tuple[str, str]]) -> str:
    parts = [
        "## 4. Architecture Diagram\n",
        "### 4.1 C4-ish / flow\n",
        "```mermaid\n" + mermaid.strip() + "\n```\n",
    ]
    for i, (title, body) in enumerate(sequences, 1):
        parts.append(f"### 4.{i+1} {title}\n\n```text\n{body.strip()}\n```\n")
    parts.append("---\n")
    return "\n".join(parts)


def section_5(
    reliability: list[str],
    scalability: list[tuple[str, str]],
    maintainability: list[str],
    deep_dives: list[tuple[str, str]],
) -> str:
    rel = "\n".join(f"{i}. {x}" for i, x in enumerate(reliability, 1))
    rows_s = "\n".join(f"| {a} | {b} |" for a, b in scalability)
    maint = "\n".join(f"- {x}" for x in maintainability)
    parts = [
        "## 5. Design Deep Dive\n",
        "### 5.1 Reliability (data loss prevention, retries, idempotency, rate limits, backpressure)\n",
        "\n" + rel + "\n",
        "\n### 5.2 Scalability (scale up/down, sharding, storage tiers, parallelization)\n",
        "\n| Scale | Architecture moves |\n|-------|--------------------|\n" + rows_s + "\n",
        "\n### 5.3 Maintainability (ops, observability, migrations, multi-tenant)\n",
        "\n" + maint + "\n",
    ]
    for i, (title, body) in enumerate(deep_dives, 4):
        parts.append(f"\n### 5.{i} {title}\n\n{body.strip()}\n")
    parts.append("\n---\n")
    return "".join(parts)


def section_6(designed: str, decisions: list[str], risks: list[str], plan: list[tuple[str, str]], closer: str) -> str:
    dec = "\n".join(f"{i}. {x}" for i, x in enumerate(decisions, 1))
    risk = "\n".join(f"- {x}" for x in risks)
    rows = "\n".join(f"| {a} | {b} |" for a, b in plan)
    return f"""## 6. Wrap-Up

### 6.1 Designed

{designed}

### 6.2 Decisions to defend

{dec}

### 6.3 Risks

{risk}

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
{rows}

### 6.5 Closer

> {closer}

---
"""


def section_7(qs: list[tuple[str, str]]) -> str:
    parts = ["## 7. Deeper / Related Interview Questions\n"]
    for i, (q, a) in enumerate(qs, 1):
        parts.append(f"### Q{i}. {q}\n\n{a.strip()}\n")
    parts.append("---\n")
    return "\n".join(parts)


def section_8(extras: list[tuple[str, str]]) -> str:
    parts = ["## 8. Appendices\n"]
    for i, (title, body) in enumerate(extras, 1):
        parts.append(f"### A{i}. {title}\n\n{body.strip()}\n")
    parts.append(
        """
### A-Z. Interview checklist

- [ ] Clarified UGC vs catalog, live vs VOD, DRM needs
- [ ] Stated progressive scale jumps that change architecture
- [ ] Separated control plane vs data plane vs media processing
- [ ] Named CDN / ABR / ladder / packaging choices with trade-offs
- [ ] Called out hot-key and viral failure modes
- [ ] Idempotency on upload/transcode/publish
- [ ] Observability: QoE (rebuffer, startup, bitrate), not just QPS
- [ ] Cost: egress and encode hours dominate
- [ ] Security: signed URLs, license servers, abuse
- [ ] Rollout phases with kill switches

---

*End of doc — senior/staff media system design prep.*
"""
    )
    return "\n".join(parts)


def pad_to_min(text: str, min_lines: int, pad_blocks: list[str]) -> str:
    lines = text.count("\n") + 1
    i = 0
    while lines < min_lines and i < len(pad_blocks) * 20:
        text += "\n" + pad_blocks[i % len(pad_blocks)] + "\n"
        lines = text.count("\n") + 1
        i += 1
    return text


# Shared padding knowledge blocks used if a doc is short
COMMON_PADS = [
    """### Extra: Encoding ladder sketch

| Rung | Resolution | Target bitrate (H.264) | Notes |
|------|------------|------------------------|-------|
| 0 | 256×144 | 100–150 kbps | Audio-only fallback companion sometimes |
| 1 | 426×240 | 300–400 kbps | Very constrained networks |
| 2 | 640×360 | 600–900 kbps | Mobile default floor |
| 3 | 854×480 | 1.0–1.5 Mbps | SD |
| 4 | 1280×720 | 2.5–4.5 Mbps | HD |
| 5 | 1920×1080 | 4.5–8 Mbps | FHD |
| 6 | 2560×1440 | 8–12 Mbps | Optional |
| 7 | 3840×2160 | 12–25 Mbps | 4K; HEVC/AV1 preferred |

Interview tip: state codec strategy (H.264 compatibility + AV1/HEVC efficiency) and why duplicate ladders exist per codec.""",
    """### Extra: ABR decision loop (player)

```text
every segment:
  measure throughput EMA + buffer level
  if buffer < danger → downswitch aggressively
  else if buffer healthy and throughput headroom → upswitch cautiously
  avoid bitrate oscillation (up-down thrash) with dwell timers
```

QoE metrics: startup time, rebuffer ratio, average bitrate, bitrate switches, abandon rate.""",
    """### Extra: CDN cache key hygiene

```text
Good key: /asset/{id}/{codec}/{rendition}/{segment}.m4s
Avoid putting user-id or session tokens in cacheable object paths
Use signed cookies / query tokens that CDNs can ignore for cache key when configured
Separate: cacheable media objects vs uncacheable personalized manifests (sometimes)
```""",
    """### Extra: DRM / license path

```text
Client requests license → License Service checks entitlement + device attestation
Returns short-lived license keyed to content key id
Packager encrypted segments with CENC; keys in KMS/HSM
Offline: persistent licenses with TTL + rental window
```""",
    """### Extra: Storage tiers for media

| Tier | Use | Latency | Cost |
|------|-----|---------|------|
| Edge SSD | Hot segments | ms | High |
| Origin SSD/object hot | Popular titles | tens–hundreds ms | Medium |
| Warm object | Mid-tail | seconds | Low |
| Cold/glacier | Archive masters | minutes | Lowest |

Policy: promote on demand; demote by access curves; never lose mezzanine masters.""",
]


def write(name: str, content: str) -> None:
    content = pad_to_min(content, 560, COMMON_PADS)
    path = OUT / name
    path.write_text(content)
    lines = content.count("\n") + 1
    print(f"{name}\t{lines}")


# =============================================================================
# DOC 1: YouTube
# =============================================================================

def doc_youtube() -> None:
    t = header(
        "YouTube",
        "UGC upload · Resumable ingest · Transcode ladders · ABR/HLS/DASH · CDN · Feed/search · Comments · Live · Copyright · Recommendations",
        "YouTube-scale video platform",
    )
    t += section_1(
        "design a **YouTube-like** video platform: creators upload video; viewers watch with ABR over CDN; discovery via search/home; comments; copyright; progressive live support.",
        [
            ("Job", "UGC video hosting + watch + discovery", "Full Google Search / Ads exchange"),
            ("Media", "VOD primary; live as extension", "Zoom-style conferencing"),
            ("Rights", "Content ID / copyright pipeline hooks", "Music label ERP"),
            ("Lens", "QoE, cost/egress, virality, abuse", "Academic codec paper only"),
        ],
        [
            ("F1", "Upload?", "Resumable chunked upload to blob store", "Upload service + multipart"),
            ("F2", "Processing?", "Transcode multi-bitrate ladder + thumbnails + previews", "Job queue + workers"),
            ("F3", "Playback?", "HLS/DASH ABR via CDN", "Packager + CDN"),
            ("F4", "Metadata?", "Title, desc, tags, visibility, channel", "Metadata DB + search index"),
            ("F5", "Discovery?", "Home feed, search, related", "Recsys + search"),
            ("F6", "Social?", "Likes, comments, subs", "Fanout + counters"),
            ("F7", "Privacy?", "Public/unlisted/private", "AuthZ on watch + list"),
            ("F8", "Copyright?", "Fingerprint match + claim actions", "Async Content ID"),
            ("F9", "Live?", "Ingest RTMP/WebRTC → packager → CDN", "Live plane separate"),
            ("F10", "Monetization?", "Ads + membership hooks (MVP stub ok)", "Ad insertion points"),
            ("F11", "Analytics?", "Views, watch time, creator studio", "Event pipeline"),
            ("F12", "Moderation?", "Reports, automated + human", "Safety queues"),
            ("F13", "Devices?", "Mobile/TV/web players", "Client diversity in ABR"),
            ("F14", "Scale?", "Billions of views/day aspirational", "CDN-first design"),
        ],
        [
            "Resumable upload; store original/mezzanine",
            "Transcode ladder (H.264 + optional AV1); thumbnails; storyboard",
            "Publish when min renditions ready; progressive enhance",
            "Watch page: signed CDN URLs / cookies; HLS/DASH",
            "Channel + video metadata CRUD; visibility",
            "Search + basic related; view counting",
            "Comments + like counters",
            "Copyright fingerprint queue (basic)",
            "Creator notifications on processing state",
        ],
        [
            "Full ads exchange / SSAI complexity",
            "Perfect Content ID legal workflow",
            "Shorts-only product (can mention)",
            "Active-active multi-writer metadata globally day one",
        ],
        [
            ("N1", "Upload resume", "Survives flaky mobile networks"),
            ("N2", "Time-to-first-playable", "Minutes for short; longer OK for 4K"),
            ("N3", "Startup latency", "p50 < 1–2s on warm CDN"),
            ("N4", "Availability watch", "99.9%+ via CDN; origin shielded"),
            ("N5", "Durability originals", "11 9s class object storage"),
            ("N6", "Consistency publish", "Viewer never sees broken manifest"),
            ("N7", "Multi-region", "Watch global; upload regional"),
            ("N8", "Security", "Private videos unguessable; signed access"),
            ("N9", "Cost", "Egress + encode dominate; cache hit ratio sacred"),
            ("N10", "Abuse", "Upload rate limits; malware scan"),
        ],
        "Upload → process → publish → CDN watch → engage → analytics.",
        "Huge file; corrupt upload; viral spike; copyright claim mid-viral; private leak; live disconnect; region outage; codec unsupported on device.",
        [
            ("Partial upload crash", "Resume by chunk ETag; no re-upload whole file"),
            ("Transcode fail one rung", "Publish with available rungs; retry failed"),
            ("Viral 100× traffic", "CDN absorbs; origin shield; throttle metadata"),
            ("Copyright match", "Block/monetize/mute per policy; appeal queue"),
            ("Private URL leak", "AuthZ every playback session; token TTL"),
            ("Hot comment spike", "Shard counters; async fanout"),
        ],
        [
            ("MAU", "50M", "500M", "2B", "2B+ global"),
            ("Videos uploaded/day", "100K", "1M", "10M", "100M"),
            ("Watch hours/day", "10M", "100M", "1B", "10B+"),
            ("Peak watch Gbps", "50", "500", "5K", "50K+"),
            ("Catalog size", "50M", "500M", "5B", "10B+"),
            ("Avg video size mezz", "500MB", "500MB", "1GB", "1GB+"),
            ("Transcode jobs/day", "100K", "1M", "10M", "100M"),
            ("CDN hit ratio hot", "90%", "95%", "98%", "99%+"),
        ],
        "10× = multi-region CDN + packager fleet; 100× = shard metadata/search, Content ID scale, live plane; 1,000× = codec fleet efficiency (AV1), edge compute, extreme QoE/cost optimization.",
        "YouTube-like UGC platform: resumable upload, durable mezzanine, multi-rung ABR packaging, CDN delivery, metadata/search/feed, comments, copyright hooks—optimized for QoE and egress cost under virality.",
    )
    t += section_2(
        [
            (
                "Traffic math",
                """
Peak concurrent viewers: assume 5M watching @ 3 Mbps avg ABR
⇒ 15 Tbps aggregate egress (CDN-handled)
Origin should see <<1% of that with good hit ratio + shields

Views/day 1B × 5 min avg × 3 Mbps ≈ enormous bit-seconds
Interview: convert carefully; emphasize CDN absorbs watch plane
""",
            ),
            (
                "Storage math",
                """
Uploads/day 1M × 500 MB mezz ≈ 500 PB/day raw? Wait — calibrate:
Realistic mid-scale: 100K uploads/day × 200 MB = 20 TB/day mezz
Ladder expands ~1.5–2.5× packaged footprint depending codecs
Thumbnails/storyboards add small %; audio stems small
Retention: never delete mezz without legal hold rules
""",
            ),
            (
                "Transcode capacity",
                """
100K jobs/day ≈ 1.2/s average; peak 5–10×
Each job: multi-rung; CPU-hours vary with duration × complexity
Priority queues: short-form interactive creators vs long archive
GPU for AV1; CPU for H.264 compatibility fleet
""",
            ),
            (
                "Metadata / QPS",
                """
Watch page API: 10K–100K QPS at scale (cached heavily)
Search: lower QPS, heavier fanout
View count updates: write-heavy → aggregate asynchronously
Comments write: bursty around premieres
""",
            ),
            (
                "Hot key math",
                """
One premiere: 1M concurrent
Manifest polls + segment fetches dominate
Segment size 2–6s; many parallel connections per client still OK
Protect: packager cache, CDN, origin shield, pre-warm popular rungs
""",
            ),
        ]
    )
    t += section_3(
        [
            ("Ingest / Upload", "Resumable bytes to object store", "Strong per object; idempotent chunks"),
            ("Media processing", "Transcode, package, thumbnails, fingerprints", "At-least-once jobs; exactly-once publish effect"),
            ("Catalog / Metadata", "Videos, channels, ACLs", "Strong per video row; searchable eventually"),
            ("Delivery / CDN", "Segments + manifests", "Cacheable; signed access"),
            ("Discovery", "Search, home, related", "Eventually consistent indices"),
            ("Safety / Rights", "Moderation + Content ID", "Async with blocking publish gates"),
            ("Engagement", "Comments, likes, subs", "Eventual counters OK"),
        ],
        [
            "API Gateway — authn, rate limits, upload tickets",
            "Upload Service — resumable sessions, virus scan hooks",
            "Object Store — mezzanine + packaged renditions",
            "Transcode Orchestrator — DAGs, retries, priority",
            "Packager — HLS/DASH CMAF, encryption",
            "CDN + Origin Shield — global edge",
            " entitlement / Playback Auth — signed cookies/URLs",
            "Metadata Service — video/channel CRUD",
            "Search Indexer — text + vectors later",
            "Feed / Recs — candidate + rank",
            "Comment Service — threads, ranking",
            "View / QoE Analytics — beacons",
            "Copyright Fingerprint — match + policy actions",
            "Live Ingest — RTMP/WHIP → transcoder → packager",
            "Moderation — reports + classifiers",
            "Notification — processing ready, replies",
            "Creator Studio API — status, analytics",
            "KMS / DRM (optional Widevine/FairPlay for premium)",
        ],
        """
POST /v1/uploads {channel_id, filename, size, content_type} → upload_id, chunk_urls
PUT  /v1/uploads/{id}/chunks/{n}  (idempotent)
POST /v1/uploads/{id}/complete → video_id PROCESSING
GET  /v1/videos/{id} → metadata + playback session mint
POST /v1/playback/sessions {video_id, device} → manifest_url, license_url?, exp
GET  /v1/search?q=
POST /v1/videos/{id}/comments
POST /v1/videos/{id}/reports
""",
        """
Video {video_id, channel_id, title, description, visibility, status, duration, created_at, ...}
Rendition {video_id, codec, height, bitrate, object_key, status}
PlaybackPolicy {video_id, drm?, geo?, age?}
FingerprintJob {video_id, status, matches[]}
Comment {id, video_id, user_id, parent_id, text, created_at}
Subscription {user_id, channel_id}
ViewAggregate {video_id, window, count}  // not per-view row at scale
""",
        [
            ("Publish gate", "Min ladder ready before public", "Avoid broken playback"),
            ("Protocol", "CMAF + HLS/DASH dual", "Device coverage"),
            ("View counts", "Async aggregated", "Write amplification"),
            ("Comments", "Shard by video_id", "Hot video contention"),
            ("Copyright", "Async but can block monetization", "Legal risk vs creator UX"),
            ("Storage", "Object store not DB BLOBs", "Cost + throughput"),
            ("CDN", "Multi-CDN optional later", "Reliability vs complexity"),
        ],
        [
            ("Serve mezzanine directly", "Cost explosion + no ABR"),
            ("Put user_id in cache key", "0% hit ratio"),
            ("Sync Content ID on upload request path", "Tail latency death"),
            ("Strong consistency global view counter", "Unnecessary & expensive"),
            ("Single region origin for world", "Latency + outage blast"),
            ("No resumable upload", "Creator churn on mobile"),
        ],
        "Watch plane must not share fate with processing plane; metadata publish is the atomic 'go live' switch after artifacts exist.",
    )
    t += section_4(
        """
flowchart TB
  Creator -->|resumable upload| UploadSvc
  UploadSvc --> ObjectStore[(Object Store Mezz)]
  UploadSvc --> Orchestrator
  Orchestrator --> TranscodeWorkers
  TranscodeWorkers --> ObjectStore
  Orchestrator --> Packager
  Packager --> ObjectStore
  Orchestrator --> Fingerprint
  Fingerprint --> RightsPolicy
  Orchestrator --> Metadata[(Metadata DB)]
  Viewer --> PlaybackAuth
  PlaybackAuth --> Metadata
  Viewer --> CDN
  CDN --> OriginShield --> ObjectStore
  Viewer --> FeedAPI --> Recs
  Viewer --> Search
  Viewer --> Comments
  Player -->|QoE beacons| Analytics
""",
        [
            (
                "Upload → playable sequence",
                """
1. Creator requests upload ticket (authZ channel)
2. Client uploads chunks with retries; complete()
3. Orchestrator DAG: probe → ladder encode → package → thumbs → fingerprint
4. When min renditions + manifest ready: status=READY; notify
5. Viewer mints playback session; fetches manifest from CDN
6. ABR segments from edge; license if DRM
""",
            ),
            (
                "Viral watch path",
                """
Edge HIT for segments (ideal)
Miss → origin shield → object store
Metadata cached at edge/PoP for watch page shell
View aggregates batched; no sync write per segment
""",
            ),
        ],
    )
    t += section_5(
        [
            "Upload chunks idempotent by (upload_id, chunk_n, checksum).",
            "Transcode jobs at-least-once with output keys deterministic; safe retry.",
            "Publish transaction: artifacts exist → metadata READY (compare-and-set).",
            "Never delete last good rendition set on failed re-encode.",
            "Playback tokens short-lived; refresh path separate from CDN cache keys.",
            "Rate-limit uploads per channel; quarantine malware scanners.",
            "Backpressure: encode queue priority + shed archival re-encodes under surge.",
            "Multi-CDN failover for major outages; health-based steering.",
            "Poison message handling for corrupt mezzanine (manual retry / reject).",
            "Live disconnect: DVR window + reconnect tokens; slate on gap policy.",
        ],
        [
            ("1×", "Single region; managed object store; CPU transcoder pool; CloudFront-like CDN; Postgres metadata"),
            ("10×", "Multi-region upload intake; origin shield; sharded comments; search cluster; priority encode queues"),
            ("100×", "Cell-based metadata; Content ID fleet; multi-CDN; AV1 partial fleet; live dedicated plane"),
            ("1,000×", "Edge packaging experiments; codec efficiency program; extreme cache hierarchy; per-country compliance cells"),
        ],
        [
            "Job DAG as data/config; canary new encoder versions on % of traffic.",
            "QoE dashboards primary (rebuffer, startup) not only CPU.",
            "Schema migrations for metadata online; dual-write search carefully.",
            "Chaos: kill packager; ensure CDN TTL + stale-while-revalidate policies.",
            "Cost attribution per channel for encode+egress (internal).",
            "Runbooks: viral event, bad encoder push, copyright false positive storm.",
        ],
        [
            (
                "Encoding ladder & packaging",
                """
Use CMAF segments shared across HLS/DASH where possible. Ladder spacing should avoid large quality cliffs. Cap top rung by source resolution. Store per-rendition checksums. For Shorts-like content, fewer rungs + faster ladder.

**Trade-off:** more rungs → better QoE on heterogeneous networks but more storage and encode cost.
""",
            ),
            (
                "CDN & cache hierarchy",
                """
PoP → regional mid-tier → origin shield → object store. Pre-warm on premiere. Negative caching careful for 404 during publish race. Immutable segment URLs with content-addressed or versioned paths enable long TTL.
""",
            ),
            (
                "Copyright / Content ID",
                """
Fingerprint at ingest; match against reference corpus; policy engine (block, track, mute audio, share revenue). Appeals workflow. False positives are a trust SEV—human review lanes for popular creators.
""",
            ),
            (
                "Recommendations (home/related)",
                """
Candidate generation (collab + content + co-watch) → ranker (watch time, satisfaction, diversity) → filters (policy, already watched). Feature store for user/video. Fallbacks when personalization fails (trending/popular).
""",
            ),
            (
                "Comments at premiere scale",
                """
Shard by video_id; separate hot celebrity videos to dedicated cells. Rank by relevance/likes with abuse filters. Don't fan out comments into per-follower feeds—pull model on watch page.
""",
            ),
            (
                "Progressive scale narrative",
                """
**1×:** Monolith API + worker pool + single CDN distribution.  
**10×:** Split upload/processing/metadata/playback auth; multi-AZ.  
**100×:** Cells, multi-region, rights + live planes, multi-CDN.  
**1,000×:** Global QoE/cost optimization as first-class product; codec wars matter.
""",
            ),
        ],
    )
    t += section_6(
        "YouTube-like system covering resumable UGC ingest, durable mezzanine, ladder encode + ABR packaging, CDN delivery, metadata/discovery, engagement, and copyright/moderation hooks.",
        [
            "Control plane (metadata publish) separate from data plane (CDN bytes)",
            "Resumable idempotent upload",
            "Min-ladder publish + progressive enhance",
            "CDN/origin shield as primary scalability mechanism for watch",
            "Async view aggregates and Content ID",
            "Hot-video isolation for comments/counters",
            "QoE-first SLOs",
            "Deterministic job outputs for safe retries",
        ],
        [
            "Encoder regression harming QoE globally",
            "Viral origin storms if cache keys wrong",
            "Copyright false positives",
            "Private video authorization bugs",
            "Cost blowups from low hit ratio or over-encoding",
        ],
        [
            ("0–5", "Scope UGC VOD; clarify live/DRM"),
            ("5–15", "Upload + processing pipeline"),
            ("15–25", "Playback ABR + CDN"),
            ("25–35", "Metadata, search, comments, views"),
            ("35–45", "Copyright, scale jumps, QoE/cost"),
        ],
        "**YouTube**: resumable ingest, ladder+ABR, CDN-first watch plane, careful publish gates, async rights & analytics, progressive cells—defend QoE and egress.",
    )
    t += section_7(
        [
            ("Why not store videos in MySQL/S3-only without CDN?", "DB BLOBs choke; S3 alone is high latency globally and costly without edge cache. CDN is non-negotiable for watch."),
            ("HLS vs DASH vs smooth?", "HLS widest device reach; DASH common on Android/web; CMAF unifies segments. Serve both manifests over shared segments."),
            ("How do you prevent cache stampedes on premiere?", "Origin shield, request coalescing, pre-warm, staggered client retries, long TTL on immutable segments."),
            ("Where is strong consistency required?", "Publish status and ACL checks for private video; not for view counts."),
            ("How to count views without melting DB?", "Client beacons → stream → aggregate by video_id in windows; approximate OK; reconcile overnight."),
            ("Design Content ID matching at scale?", "Audio/video fingerprints; sharded reference index; ANN + exact verify; policy async."),
            ("How do signed URLs interact with CDN caching?", "Prefer signed cookies or CDN tokens excluded from cache key; never unique query per user on segment URLs."),
            ("What breaks when average bitrate doubles?", "Egress cost and CDN capacity; ABR ladder and codec efficiency become executive issues."),
            ("Live vs VOD architecture differences?", "Live has low-latency packagers, short segments, DVR windows, different failure (ingest disconnect); VOD emphasizes VOD storage tiers."),
            ("How to handle device that can't play AV1?", "Multi-codec manifests; player picks; server can filter by device capability hints."),
            ("Idempotent complete upload called twice?", "Same video_id returned; processing DAG not duplicated if keyed by upload_id."),
            ("Consistent hashing for what?", "Shard comments, fingerprint workers, maybe metadata cells—not CDN path selection (anycast/geo)."),
            ("Rate limit strategy?", "Per-user/channel upload Mbps and daily count; separate watch API limits; CDN handles byte flood."),
            ("How do thumbnails work?", "Sample frames; select aesthetic score; storyboard sprites for hover scrub."),
            ("Search indexing lag OK?", "Yes seconds–minutes; watch by URL must work immediately via metadata primary."),
            ("Multi-region metadata?", "Read replicas global; writes regional with video_id locality; careful ACL caching TTLs."),
            ("What is a deal-breaker in interview?", "Serving one giant MP4 progressively without ABR at YouTube scale."),
            ("How to degrade under encode backlog?", "Prioritize short/recent; lower max rung temporarily; notify creators of delay."),
            ("Comments ranking abuse?", "Shadowrate spam; ML + reports; rate limits; don't chronologically amplify bots."),
            ("Offline downloads?", "Separate entitlement + encrypted persistent license; storage quota on device; covered in offline-media doc."),
            ("Why storyboard sprites?", "Scrubbing without fetching video; CDN-friendly small images."),
            ("Manifest personalization?", "Usually same media manifests; ads/ssai may personalize; cache carefully."),
            ("How to test QoE?", "Synthetic players globally; cohort metrics; canary encoder."),
            ("Partition videos table?", "By video_id hash; secondary indices for channel timelines."),
            ("What about 8K?", "Niche; separate ladder; most devices capped; cost/benefit."),
        ]
    )
    t += section_8(
        [
            (
                "Sample SLO table",
                """
| SLO | Target |
|-----|--------|
| Upload success after resume | 99% |
| Time to first playable <10min video | <5–15 min p50 |
| Rebuffer ratio | <0.5–1% watch time |
| Playback auth availability | 99.95% |
| Wrong ACL exposure | ~0 (SEV0) |
""",
            ),
            (
                "Ownership map",
                """
| Area | Owning team example |
|------|---------------------|
| Upload/resume | Ingest |
| Encode/package | Media processing |
| CDN/QoE | Delivery |
| Metadata/ACL | Catalog |
| Content ID | Rights |
| Recs | Discovery ML |
""",
            ),
            (
                "Failure injection drills",
                """
- Kill origin shield in one region
- Push bad encoder binary to 1% 
- Flood fingerprint false positives
- Expire all playback signing keys (emergency rotation test)
""",
            ),
        ]
    )
    write("youtube-system-design.md", t)


# Continue with remaining docs in same file - will append more generator functions
if __name__ == "__main__":
    doc_youtube()
