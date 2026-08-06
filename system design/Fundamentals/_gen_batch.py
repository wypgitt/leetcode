#!/usr/bin/env python3
"""Generate remaining media system-design docs from structured specs."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

OUT = Path(__file__).resolve().parent

APPENDIX = dedent("""
---

## Appendix: Cross-cutting media patterns (interview ammunition)

### Encoding ladder reference

| Rung | Resolution | H.264 bitrate band | Typical role |
|------|------------|--------------------|--------------|
| L0 | 256×144 | 100–200 kbps | Extreme constrained |
| L1 | 426×240 | 300–500 kbps | Poor mobile |
| L2 | 640×360 | 600–1000 kbps | Mobile floor |
| L3 | 854×480 | 1.0–1.8 Mbps | SD |
| L4 | 1280×720 | 2.5–5 Mbps | HD |
| L5 | 1920×1080 | 4.5–9 Mbps | FHD |
| L6 | 2560×1440 | 8–14 Mbps | QHD optional |
| L7 | 3840×2160 | 12–35 Mbps | 4K (HEVC/AV1) |

Dual-codec (H.264 + AV1/HEVC); packaged ≈ 1.6–2.8× mezzanine.

### ABR loop

```text
throughput_EMA + buffer → downswitch if danger; upswitch with dwell/hysteresis
QoE: startup, rebuffer ratio, avg bitrate, switches, abandon
```

### CDN hierarchy

```text
PoP → mid-tier → origin shield → object store
Immutable versioned segments; personalization in control plane only
```

### DRM

```text
CENC packager; license = entitlement + device level; offline persistent TTL
```

### Scale jumps

| Jump | Moves |
|------|-------|
| 10× | Multi-AZ, queues, shield, caches |
| 100× | Multi-region, cells, multi-CDN, dedicated planes |
| 1,000× | Codec economics, edge experiments, compliance cells |

### Reliability checklist

Idempotent chunks/jobs; publish CAS gate; no orphan manifests; encode backpressure; poison quarantine; key rotation; immutable segments.

### Cost levers

Hit ratio; codec bits; ladder density; cold tiering; prefetch discipline.

### Consistency

Strong: ACL/publish/entitlement. Eventual: counters/search/recs. WORM: segments.

### Deal-breakers

Progressive-only MP4 globally; user-specific segment URLs; sync ML on upload path; DB BLOBs for media; skip DRM on licensed premium.

### Algorithms

Consistent hash shards; Bloom dup; fingerprints/MinHash; WFQ encode; EMA ABR; ANN recs.

### Math templates

```text
cdn_egress ≈ watch_hours * 3600 * bitrate / 8
origin ≈ cdn_egress * (1 - hit_ratio)
mezz/day ≈ uploads/day * dur_s * mezz_bitrate / 8
```

### Reusable closer

> Bytes plane (CDN) ≠ control plane (entitlement/metadata/processing). Atomic publish. QoE. Egress. Idempotent pipelines. Progressive cells/shields.
""")


def hdr(title, focus, theme):
    return dedent(f"""\
    # System Design: {title}

    > **Focus areas:** {focus}
    > **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
    > **Quality bar:** Domain-specific numbers and failure modes; explicit trade-offs; deal-breakers; CDN / ABR / encoding / DRM where relevant
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
    """)


def fmt_table(headers, rows):
    line = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join(["---"] * len(headers)) + "|"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return f"{line}\n{sep}\n{body}"


def build(spec: dict) -> str:
    """Build a full doc from a spec dict."""
    s = spec
    parts = [hdr(s["title"], s["focus"], s["theme"])]

    # Section 1
    parts.append(f"## 1. Clarify Requirements (Interview Q&A)\n\nGoal: {s['goal']}\n")
    parts.append("### 1.0 What this is / is not\n")
    parts.append(fmt_table(["Dimension", "This doc", "Not this"], s["is_not"]) + "\n")
    parts.append("### 1.1 Functional Requirements\n")
    parts.append(fmt_table(["#", "Question", "Expected interviewer answer", "Design implication"], s["functional"]) + "\n")
    parts.append("**MVP scope:**\n")
    for i, x in enumerate(s["mvp"], 1):
        parts.append(f"{i}. {x}")
    parts.append("\n**Out of MVP:**\n")
    for x in s["out_mvp"]:
        parts.append(f"- {x}")
    parts.append("\n### 1.2 Non-Functional Requirements\n")
    parts.append(fmt_table(["#", "NFR", "Target"], s["nfr"]) + "\n")
    parts.append("### 1.3 Cases\n")
    parts.append(f"**Happy:** {s['happy']}  \n**Edges:** {s['edges']}\n")
    parts.append(fmt_table(["Case", "Behavior"], s["cases"]) + "\n")
    parts.append("### 1.4 Progressive scale\n")
    parts.append(fmt_table(["Metric", "Baseline", "10×", "100×", "1,000×"], s["scales"]) + "\n")
    parts.append(f"**Jumps:** {s['jumps']}\n")
    parts.append(f"### 1.5 Etc. constraints + scope repeat-back\n\nConstraints: {s.get('constraints', 'multi-region, cost/egress, device diversity, abuse, compliance.')}\n\n> {s['scope']}\n")
    parts.append("---\n")

    # Section 2
    parts.append("## 2. Back-of-the-Envelope Estimation\n")
    for i, (title, body) in enumerate(s["estimates"], 1):
        parts.append(f"### 2.{i} {title}\n\n```text\n{body.strip()}\n```\n")
    parts.append(dedent("""\
    ### 2.N Bottleneck ranking

    1. Egress / edge bandwidth and hit ratio
    2. Hot keys (viral titles, celebrity metadata)
    3. Processing fleets (encode/ASR/ML)
    4. Control-plane fanout (manifests, licenses, personalization)
    5. Cold retrieval / long-tail

    ### 2.N+1 Cost intuition

    ```text
    Storage << egress at watch scale.
    Cache hit ratio and codec efficiency are executive levers.
    Processing ($GPU/CPU-hours) matters for UGC firehose and ML pipelines.
    ```
    """))
    parts.append("---\n")

    # Section 3
    parts.append("## 3. High-Level Design\n")
    parts.append("### 3.1 Planes (critical split)\n")
    parts.append(fmt_table(["Plane", "Responsibility", "Consistency"], s["planes"]) + "\n")
    parts.append(f"**Why this split:** {s['why_split']}\n")
    parts.append("### 3.2 Components\n")
    for i, c in enumerate(s["components"], 1):
        parts.append(f"{i}. {c}")
    parts.append(f"\n### 3.3 APIs (sketch)\n\n```text\n{s['apis'].strip()}\n```\n")
    parts.append(f"### 3.4 Data model (core)\n\n```text\n{s['data_model'].strip()}\n```\n")
    parts.append("### 3.5 Trade-offs\n")
    parts.append(fmt_table(["Topic", "Choice", "Why"], s["tradeoffs"]) + "\n")
    parts.append("### 3.6 Deal-breakers\n")
    parts.append(fmt_table(["Temptation", "Failure"], s["dealbreakers"]) + "\n")
    parts.append("---\n")

    # Section 4
    parts.append("## 4. Architecture Diagram\n")
    parts.append("### 4.1 C4-ish / flow\n")
    parts.append(f"```mermaid\n{s['mermaid'].strip()}\n```\n")
    for i, (title, body) in enumerate(s["sequences"], 2):
        parts.append(f"### 4.{i} {title}\n\n```text\n{body.strip()}\n```\n")
    parts.append("---\n")

    # Section 5
    parts.append("## 5. Design Deep Dive\n")
    parts.append("### 5.1 Reliability (data loss prevention, retries, idempotency, rate limits, backpressure)\n")
    for i, x in enumerate(s["reliability"], 1):
        parts.append(f"{i}. {x}")
    parts.append("\n### 5.2 Scalability (scale up/down, sharding, storage tiers, parallelization)\n")
    parts.append(fmt_table(["Scale", "Architecture moves"], s["scalability"]) + "\n")
    parts.append("### 5.3 Maintainability (ops, observability, migrations, multi-tenant)\n")
    for x in s["maintainability"]:
        parts.append(f"- {x}")
    for i, (title, body) in enumerate(s["deep_dives"], 4):
        parts.append(f"\n### 5.{i} {title}\n\n{body.strip()}\n")
    parts.append("\n---\n")

    # Section 6
    parts.append("## 6. Wrap-Up\n")
    parts.append(f"### 6.1 Designed\n\n{s['designed']}\n")
    parts.append("### 6.2 Decisions to defend\n")
    for i, x in enumerate(s["decisions"], 1):
        parts.append(f"{i}. {x}")
    parts.append("\n### 6.3 Risks\n")
    for x in s["risks"]:
        parts.append(f"- {x}")
    parts.append("\n### 6.4 45-minute plan\n")
    parts.append(fmt_table(["Min", "Focus"], s["plan45"]) + "\n")
    parts.append(f"### 6.5 Closer\n\n> {s['closer']}\n")
    parts.append("---\n")

    # Section 7
    parts.append("## 7. Deeper / Related Interview Questions\n")
    for i, (q, a) in enumerate(s["questions"], 1):
        parts.append(f"### Q{i}. {q}\n\n{a}\n")
    parts.append("---\n")

    # Section 8
    parts.append("## 8. Appendices\n")
    parts.append(s.get("appendix_extra", "### A1. Domain notes\n\nSee deep dives; keep runbooks for viral/peak events.\n"))
    parts.append(dedent("""
    ### A-Z. Interview checklist

    - [ ] Clarified product shape and non-goals
    - [ ] Progressive scale jumps that change architecture
    - [ ] Control plane vs data/bytes plane
    - [ ] CDN / ABR / ladder / DRM called out where relevant
    - [ ] Hot-key and failure modes
    - [ ] Idempotency and publish gates
    - [ ] QoE / domain SLOs not just QPS
    - [ ] Cost levers
    - [ ] Security / abuse / compliance
    - [ ] Phased rollout + kill switches
    """))
    parts.append(APPENDIX)

    text = "\n".join(parts)
    n = 0
    while text.count("\n") + 1 < 560 and n < 6:
        text += "\n### Additional staff drill\n\n" + s.get("pad", s["deep_dives"][-1][1]) + "\n"
        n += 1
    return text


def write_spec(spec):
    text = build(spec)
    path = OUT / spec["name"]
    path.write_text(text)
    print(f"{spec['name']}\t{text.count(chr(10))+1}")


def common_media_qs(extra):
    base = [
        ("Where is strong consistency mandatory?", "ACL/publish/entitlement and private media access; not counters."),
        ("Signed URLs vs CDN cache?", "Don't put per-user uniqueness into segment cache keys; use cookies/tokens."),
        ("HLS vs DASH vs CMAF?", "Dual manifests over shared CMAF segments when possible."),
        ("#1 cost lever at watch scale?", "Edge hit ratio / offload; then codec efficiency."),
        ("Premiere stampede controls?", "Pre-warm, shield, coalesce, scale license/playback, shed noncritical work."),
        ("Idempotent jobs?", "Deterministic output keys + CAS publish."),
        ("ABR oscillation?", "Dwell + asymmetric thresholds + buffer hysteresis."),
        ("Consistent hashing where?", "Shard stateful workers/comments—not static CDN GETs."),
        ("QoE vs QPS?", "Talk rebuffer/startup/bitrate; QPS alone is weak."),
        ("Multi-CDN when?", "~100× for resilience/pricing; needs steering."),
        ("Offline + DRM?", "Persistent licenses, windows, secure storage, online renew."),
        ("Hot metadata?", "Cache + cell isolation; decouple from byte paths."),
        ("Encode backpressure?", "Priority queues; shed archival reencodes."),
        ("Manifest personalization risk?", "Can kill cache hit ratio—keep media manifests stable."),
        ("Deal-breaker example?", "Serving one giant progressive file without ABR at global scale."),
    ]
    seen = set()
    out = []
    for item in extra + base:
        if item[0] not in seen:
            out.append(item)
            seen.add(item[0])
    return out[:26]


# ---------------------------------------------------------------------------
# Specs for docs 3–22 (and regenerate helpers)
# ---------------------------------------------------------------------------

SPECS = []

SPECS.append(dict(
name="spotify-system-design.md",
title="Spotify",
focus="Music catalog · Audio CDN · Gapless playback · Playlists · Offline · Lyrics sync · Recommendations · Podcasts hook · Rights",
theme="Spotify-like audio streaming",
goal="design a **Spotify-like** audio streaming platform: huge music catalog, low-latency start, gapless playback, playlists, personalized home/radio, offline downloads, lyrics, and rights-aware delivery.",
is_not=[
["Job", "Music (+ podcast) streaming & library", "Full DAW / music creation suite"],
["Media", "Audio-first; video optional canvases", "Netflix long-form video"],
["Rights", "Label licensing & reporting", "UGC Content ID sole focus"],
["Lens", "Start latency, personalization, offline", "Live concert video SFU"],
],
functional=[
["F1", "Catalog?", "Label deliveries + metadata", "Ingest + catalog graph"],
["F2", "Playback?", "Encrypted audio segments / files via CDN", "Audio CDN + DRM/encryption"],
["F3", "Bitrates?", "96/160/320 kbps + lossless tier optional", "Ladder for audio"],
["F4", "Playlists?", "User + editorial + algo", "Playlist service"],
["F5", "Offline?", "Downloads with limits", "Persistent licenses"],
["F6", "Discovery?", "Home, radio, search, Daily Mix-like", "Recsys"],
["F7", "Queue?", "Player state cross-device", "State sync"],
["F8", "Lyrics?", "Timed lyrics", "Sync transcript plane"],
["F9", "Social?", "Following, sharing (light)", "Social graph light"],
["F10", "Podcasts?", "Episodes in same player optional", "Unified playback"],
["F11", "Accounts?", "Free vs premium entitlements", "Feature gates"],
["F12", "Scrubbing?", "Seek dense", "Segmented or ranged files"],
["F13", "Gapless/crossfade?", "Client + encoding constraints", "Encoder + player"],
["F14", "Reporting?", "Royalty events", "Accurate play events"],
],
mvp=[
"Catalog browse/search; track play via CDN",
"Premium encryption/entitlement; free tier rules",
"Playlists CRUD; liked songs",
"Basic personalized home + radio seed",
"Offline downloads for premium",
"Cross-device playback state (basic)",
"Play event pipeline for royalties",
"Gapless for encoded catalog subset",
],
out_mvp=["Full lossless hi-fi everywhere", "Complete social network", "Live audio rooms MVP optional"],
nfr=[
["N1", "Time-to-first-audio", "p50 < 200–500ms cached"],
["N2", "Stall rate", "Very low; audio intolerance high"],
["N3", "Availability", "99.95%+ play start"],
["N4", "Durability catalog", "No silent track loss"],
["N5", "Royalty correctness", "Auditable play events"],
["N6", "Offline security", "Encrypted at rest on device"],
["N7", "Global", "Multi-region catalog reads"],
["N8", "Cost", "Audio egress << video but non-zero at scale"],
],
happy="Search/home → play track → gapless next → add playlist → offline sync.",
edges="license territory; track takedown mid-play; free tier skip limits; offline expiry; lyrics desync; viral playlist spike.",
cases=[
["Takedown", "Stop newly started plays; finish policy legal-dependent"],
["Skip limit free", "Server-authoritative counters"],
["Offline expired", "Unplayable until renew"],
["Cross-device fight", "Last command wins with version"],
["Missing lyrics", "Degrade UI; don't block audio"],
],
scales=[
["MAU", "10M", "100M", "500M", "600M+"],
["Tracks", "10M", "50M", "100M", "100M+"],
["Peak concurrent plays", "100K", "1M", "10M", "50M"],
["Avg bitrate", "160 kbps", "160", "160–320", "tiered"],
["Playlist ops/s", "1K", "10K", "100K", "500K"],
["Recs QPS", "2K", "20K", "200K", "1M"],
["Play events/day", "100M", "1B", "10B", "50B+"],
["CDN hit", "90%", "95%", "98%", "99%"],
],
jumps="10× multi-region audio CDN + entitlement; 100× playlist/recs cells + royalty pipeline hardening; 1,000× catalog graph + personalization fleet.",
constraints="label reporting SLAs, territory rights, free-tier abuse, battery on mobile.",
scope="Spotify-like audio streaming: rights-aware catalog, low-latency encrypted audio CDN, playlists/library, personalization, offline, accurate play events—gapless UX and royalty correctness.",
estimates=[
("Concurrent audio math", "5M concurrent × 160 kbps ≈ 800 Gbps — large but << video Netflix numbers."),
("Catalog storage", "100M tracks × avg 5 MB ≈ 500 PB raw across qualities; dedupe encodings; lyrics small."),
("Play events", "10B events/day × 200 B ≈ 2 TB/day raw before aggregate; exactly-once-ish billing semantics matter."),
("Playlist hot keys", "Celebrity playlist edits + viral adds; shard playlist_id; cache snapshots for read."),
("Latency budget", "DNS+TLS+auth+first chunk < few hundred ms; prefetch next track aggressively."),
],
planes=[
["Catalog/rights", "Tracks, territories, takedowns", "Strong for rights"],
["Delivery", "Audio objects CDN", "Immutable"],
["Library/playlists", "User collections", "Strong per user"],
["Player state", "Queue/position", "Causal per user"],
["Personalization", "Home/radio", "Stale-OK"],
["Royalty events", "Play reporting", "Durable at-least-once + dedup"],
],
why_split="Royalty and rights correctness must not share fate with best-effort recommendations.",
components=[
"**Catalog Service** — tracks, albums, artists, territories",
"**Ingest/Encoding** — normalize loudness, multi-bitrate audio",
"**Entitlement** — free/premium/features",
"**Playback Auth** — signed access to audio",
"**Audio CDN** — global edge",
"**Playlist/Library Service** — liked, playlists",
"**Player State Service** — queue sync",
"**Search** — text + fuzzy",
"**Recs / Radio** — embeddings + rankers",
"**Lyrics Service** — timed lines",
"**Offline License** — persistent",
"**Event Pipeline** — plays for royalties",
"**Takedown/Rights** — emergency stop",
"**Podcast module** (optional unified)",
"**Notifications** — new releases",
"**Abuse** — scraping/download farms",
],
apis=dedent("""\
GET  /v1/tracks/{id}
GET  /v1/playback/{track_id} → urls[], format, license?
POST /v1/playlists
POST /v1/playlists/{id}/items
PUT  /v1/player/state
POST /v1/events/play {track_id, ts, duration_played, offline?}
GET  /v1/home
GET  /v1/search?q=
POST /v1/offline/sync
"""),
data_model=dedent("""\
Track{id, album_id, duration_ms, isrc, loudness}
Delivery{track_id, bitrate, codec, path}
Rights{track_id, country, window}
Playlist{id, owner, name, version}
PlaylistItem{playlist_id, idx, track_id, added_at}
PlayEvent{event_id, user_id, track_id, played_ms, context, ts}
"""),
tradeoffs=[
["File vs segmented audio", "Segmented or ranged", "Seek + CDN"],
["Gapless", "Encoder padding + client", "UX differentiator"],
["Play events", "Client beacons + server validate", "Royalty audits"],
["Recs", "Batch mixes + online", "Latency vs freshness"],
["Free tier", "Server-side limits", "Abuse resistance"],
],
dealbreakers=[
["Trust client for royalty duration only", "Fraudulent payouts"],
["Unencrypted offline store", "Piracy SEV"],
["Single region catalog", "Global outage"],
["Playlist full rewrite every add", "Write amp / races"],
],
mermaid=dedent("""\
flowchart TB
  Labels --> CatalogIngest --> Catalog[(Catalog)]
  CatalogIngest --> AudioEncode --> ObjectStore[(Audio Objects)]
  ObjectStore --> CDN
  Client --> Entitlement
  Client --> PlaybackAuth --> CDN
  Client --> PlaylistSvc
  Client --> Recs
  Client --> PlayerState
  Client --> Events --> RoyaltyPipe
  Rights --> Entitlement
  Rights --> PlaybackAuth
"""),
sequences=[
("Play sequence", "Resolve track → entitlement → signed URLs → stream/prefetch next → emit play event after threshold."),
("Takedown", "Rights marks track blocked → playback auth denies new sessions → CDN can purge optional → clients stop on next license refresh."),
],
reliability=[
"Play event_id idempotent; dedup store for royalty.",
"Playlist updates versioned; CAS on version.",
"Takedown propagation SLO measured in minutes or less.",
"Offline licenses expire; clock-skew tolerant.",
"Rate-limit scraping patterns on track audio.",
"Encode loudness normalize idempotently.",
"Player state sync with vector clocks / versions.",
"CDN purge hooks for critical rights emergencies.",
"Backpressure on event pipeline with durable buffer.",
"Poison track encodings quarantined without killing catalog row incorrectly.",
],
scalability=[
["1×", "Object storage + CDN; Postgres catalog; Redis player state"],
["10×", "Shard playlists; event bus; multi-region entitlement"],
["100×", "Catalog cells; ANN recs; royalty lakehouse"],
["1,000×", "Graph metadata platform; extreme personalization; global rights complexity"],
],
maintainability=[
"Territory rules as data with audit.",
"Encoder loudness policy versioned.",
"Canary player clients.",
"Royalty reconciliation dashboards with labels.",
"Feature flags for free-tier experiments.",
],
deep_dives=[
("Audio delivery specifics", "Prefer Ogg/AAC/MP3 ladders; prefetch next; keep buffers modest for skippy UX; canvas video is separate low-bitrate stream."),
("Gapless & crossfade", "Encoder delay/padding metadata; client mixes; not all catalog gapless day one."),
("Playlists at scale", "Append-friendly structures; snapshot cache for large playlist reads; collaborative playlists need OT/CRDT or lock."),
("Royalty event semantics", "Define what counts as a stream (e.g., 30s); offline upload on reconnect; fraud filters."),
("Personalization", "Embeddings for tracks/users; session features; exploration; editorial overlays."),
("Progressive scale", "1× single region → 10× multi-region CDN → 100× recs/royalty hardening → 1,000× global rights+graph."),
],
designed="Spotify-like audio: catalog/rights, encrypted CDN audio, playlists/library, player state, recs, offline, royalty-grade events.",
decisions=[
"Rights/entitlement plane separate from CDN bytes",
"Server-authoritative free-tier limits",
"Versioned playlists",
"Idempotent play events with dedup",
"Prefetch-next for UX",
"Offline encrypted + expiring licenses",
"Batch+online recs with fallbacks",
"Takedown fast path",
],
risks=["Royalty disputes", "Takedown lag", "Playlist races", "Scraping farms", "Lyrics license"],
plan45=[
["0–5", "Audio vs video; rights"],
["5–15", "Catalog + delivery"],
["15–25", "Playlists + player state"],
["25–35", "Recs + offline"],
["35–45", "Royalty events + scale"],
],
closer="**Spotify**: rights-aware catalog, low-latency audio CDN, versioned playlists, offline DRM, personalization with fallbacks, auditable play events.",
appendix_extra=dedent("""\
### A1. Spotify domain notes

**Normalization:** replay gain / loudness (-14 LUFS class) for consistent UX.  
**ISRC/UPC:** identity for rights.  
**Free tier:** skip caps, shuffle constraints—server enforced.  
**Podcasts:** longer files, different royalty; same player shell.
"""),
pad="Discuss collaborative playlist concurrency and offline play event upload storms after flights.",
questions=common_media_qs([
("Why audio still needs CDN hierarchy?", "Global start latency + peak fanout on viral tracks/playlists; origin protection."),
("How to count a 'stream'?", "Policy threshold (e.g. 30s) + fraud filters; offline reconcile."),
("Lossless tier impact?", "Much higher egress/storage; entitlement gated; separate encodes."),
("Crossfade server or client?", "Client with encoder metadata; server doesn't remix per listen."),
("Radio vs playlist?", "Radio is endless generator; playlist is finite editable list."),
("Lyrics sync correctness?", "Timed lines with offsets; user-reported fixes; don't block audio."),
("Celebrity playlist hotspot?", "Read snapshots cached; shard writes; eventual item order repair."),
("Why not store audio in DB?", "Object store + CDN; DB for metadata only."),
("Territory mismatch mid-travel?", "Re-check entitlement periodically; GPS spoofing heuristics."),
("Embedding index ops?", "Rebuild/alias swap; dual read during migration."),
]),
))


def main():
    for sp in SPECS:
        write_spec(sp)


if __name__ == "__main__":
    main()
