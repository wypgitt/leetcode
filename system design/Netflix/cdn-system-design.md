# System Design: Content Delivery Network (CDN)

> **Focus areas:** Edge POPs · Cache hierarchy · Origin shield · Request coalescing · Invalidation vs versioning · Hot launches · Multi-CDN · Open Connect · Streaming segment workloads  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar QPS (edge HIT vs shield fill vs origin egress vs control plane), explicit deal-breakers, Netflix 2025–26 interview themes  
> **Interview theme:** Netflix CDN — design edge delivery for ABR video segments at Tbps scale with Open Connect–aware economics

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

Goal: **bound the CDN**—edge caching and delivery of HTTP objects (especially ABR video segments and manifests) with high HIT ratio, low latency, protected origins, and global scale at Netflix-class Tbps egress.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Cache & deliver bytes at edge | Encoding / transcoding pipeline |
| Netflix angle | Open Connect + cloud CDN + ISP embeds | Ads auction / frequency capping |
| Objects | Segments, manifests, sprites, posters | User metadata / billing |
| Control plane | Steering, purge, prefetch, certs | Full entitlement catalog service |
| Origin | Object storage + packager output | Live ingest encoder |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | What objects does the CDN serve? | **ABR segments** (fMP4/CMAF), **manifests** (HLS/DASH), thumbnails/sprites | Separate cache policies per object class |
| F2 | Protocols? | **HTTPS**; HTTP/2 and HTTP/3 (QUIC) at edge | TLS termination at POP; OCSP stapling; cert rotation |
| F3 | Cache fill model? | **Pull** on MISS from origin; optional **push/prefetch** for launches | Shield tier + request coalescing |
| F4 | Invalidation strategy? | **Versioned immutable URLs** preferred; purge API for emergencies | `Cache-Control: immutable`; purge by tag/prefix |
| F5 | Auth / entitlement? | **Signed URLs or cookies** bound to profile/session; short TTL | Edge validation before HIT/MISS; fail closed |
| F6 | Geography? | Global POPs + **ISP-embedded Open Connect** appliances | Anycast / GSLB steering; regional shields |
| F7 | Range requests? | Yes — segments may be whole files or byte ranges of fMP4 | Range cache key normalization; 206 handling |
| F8 | Hot launch / tentpole? | Prefetch top rungs to major POPs/OCAs before premiere | Push API + capacity dashboards |
| F9 | Multi-CDN? | Vendor abstraction + steering by perf/error | Unified purge/prefetch API; per-CDN metrics |
| F10 | Stale-if-error? | Serve stale cached bytes if origin unhealthy | `stale-if-error` + bounded max-stale |
| F11 | Live vs VOD? | **VOD primary**; live uses shorter TTL on sliding playlists | Different cache key + TTL rules |
| F12 | DRM? | Encrypted segments cached at edge; **license is separate** | CDN caches ciphertext; no keys in logs |
| F13 | Logging / QoE? | Sampled access logs; CDN metrics to QoE pipeline | Privacy-safe; not on critical byte path |
| F14 | Multi-tenant? | Same CDN fleet serves multiple brands/regions/tenants | Tenant in cache key + SNI + signing key isolation |
| F15 | Compression? | Video already compressed; gzip/brotli for manifests only | Don't re-compress media |

**MVP functional scope (lock with interviewer):**

1. Three-tier cache: **edge POP → origin shield → origin object store**.
2. **TLS termination** at edge with automated cert lifecycle.
3. **Signed URL/cookie validation** at edge before cache lookup.
4. **Request coalescing** (single-flight) on shield/origin MISS for same cache key.
5. **Versioned immutable segment URLs** (`/v/{assetVersion}/...`) with long `max-age`.
6. **Prefetch API** for tentpole launches (push top ladder rungs).
7. **Emergency purge API** (tag/prefix/URL) with propagation SLA.
8. **HIT/MISS/TTFB metrics** per POP, ASN, title cohort (sampled).

**Out of MVP (explicitly defer):**

- Building a global private fiber backbone
- Full edge compute / WASM transcoding at POP
- Per-viewer personalized segment bytes (same URL for all viewers of a rendition)
- Client-side P2P offload
- Custom OCA hardware design (mention conceptually only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
| --- | --- | --- | --- |
| N1 | Edge latency (warm HIT)? | Feels instant for segment fetch | p50 TTFB < 20ms, p99 < 80ms (same metro) |
| N2 | Shield fill latency (MISS)? | Acceptable once per POP cold start | p99 < 200–500ms depending on origin distance |
| N3 | Availability (playback bytes)? | CDN is critical path | 99.99% for edge serving; multi-POP failover |
| N4 | Cache HIT ratio? | Dominate cost and origin protection | **95–99%** blended; **98%+** for head titles |
| N5 | Origin egress after CDN | Must stay bounded at 100× | See §2 — shield + HIT ratio math |
| N6 | Purge propagation | Emergency only; bounded | 95% POPs < 60s for tag purge |
| N7 | Consistency | **Immutable bytes** at URL; eventual purge | Never mutate segment at same URL |
| N8 | Scale | Through 1,000× concurrent viewers | Progressive table §1.4 |
| N9 | Security | No unsigned premium delivery | Fail closed on bad/expired sig |
| N10 | Cost | Egress $ dominates at scale | HIT ratio + Open Connect offload |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Player requests signed segment URL → nearest POP → **HIT** → 200/206 with `Age` header → buffer fills.
2. POP **MISS** → shield HIT → fill POP → respond; shield warmed from prior viewer in metro.
3. Shield **MISS** → single-flight fetch from origin → populate shield + edge → respond.
4. Tentpole **prefetch** completes T-6h → premiere traffic → **99%+ HIT** → origin stays quiet.
5. New asset version published → new URL path → old version ages out naturally; no purge needed.
6. ABR switches 720p → 480p → different cache keys → independent HIT/MISS behavior.

**Edge / failure cases**

| Case | Behavior |
| --- | --- |
| Thundering herd on cold segment | Shield **request coalescing** — 10K concurrent MISS → 1 origin fetch |
| Origin 503 / timeout | Serve **stale-if-error** if cached; else 502 to player with retry |
| Bad signature / expired token | **403** at edge; do not pass to origin; no cache pollution |
| Range request on uncached object | Normalize range key or fetch full object per product policy |
| Partial POP outage | Anycast/GSLB steers to sibling POP; clients retry |
| Purge typo hits wrong prefix | Tag-based purge with dry-run; audit trail; rate limits |
| Hot title on small ISP OCA | OCA fills from regional shield; may MISS more until warm |
| Manifest points to new version mid-playback | Short TTL on master playlist; segments still immutable |
| TLS cert expiry | Automated ACME rotation; dual cert overlap window |
| QUIC vs TCP fallback | HTTP/3 preferred; degrade to H2/TLS 1.3 transparently |
| DRM license outage | Segments may HIT but player can't decrypt — license path separate |
| Multi-tenant key leak | Per-tenant signing keys; cache namespace isolation |
| Cache poisoning attempt | Strict cache key; ignore attacker `Host`/`X-Forwarded-*` abuse |
| Very long tail title (1 viewer) | Cold MISS acceptable; don't prefetch entire catalog |

### 1.4 Scales (Progressive)

| Metric | Baseline (1×) | 10× | 100× | 1,000× |
| --- | --- | --- | --- | --- |
| Peak concurrent viewers | 100K | 1M | 10M | 100M |
| CDN egress (peak) | 0.3 Tbps | 3 Tbps | 30 Tbps | 300 Tbps |
| Origin egress after HIT (98%) | 6 Gbps | 60 Gbps | 600 Gbps | 6 Tbps |
| Edge segment req / s | ~1M | ~10M | ~100M | ~1B |
| Manifest req / s | ~20K | ~200K | ~2M | ~20M |
| Distinct segment objects (catalog) | 500M | 5B | 50B | 500B |
| Edge POPs + OCA sites | ~50 | ~200 | ~1K | ~5K+ |
| Hot set in edge cache (unique objects) | ~500K | ~2M | ~10M | ~50M |
| Prefetch jobs / launch | 10 / mo | 50 / mo | 200 / mo | 1K / mo |
| Purge API calls / day | 100 | 500 | 2K | 10K |
| Tenants on shared fleet | 1 | 3 | 10 | 50+ |

**Split classes:** edge segment GET ≠ manifest GET ≠ shield fill ≠ origin egress ≠ purge/prefetch control ≠ cert rotation.

**What each jump forces:**

- **10×:** Dedicated **origin shield** layer; **single-flight coalescing**; per-object-class TTL policy; signed URL validation at edge.
- **100×:** **Open Connect / ISP embeds**; regional shield clusters; **multi-CDN** steering; prefetch automation for launches; hot-set tracking.
- **1,000×:** Hierarchical **L1/L2/L3** cache; global anycast optimization; **cell'd control plane**; OCA peer fill; regional origin replicas; tenant isolation at scale.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like **ABR VOD** is the primary workload; live is Phase 2 with shorter playlist TTL.
- Segments are **4–6 seconds**; ~4 MB average per segment at blended quality (order-of-magnitude).
- Origin is **object storage** (S3-compatible) fronted by packager output paths — we don't re-encode at CDN.
- We may **buy** commercial CDN capacity **and** operate **Open Connect**-style appliances — design abstracts both.
- **Immutable versioning** is the default cache invalidation story.
- Storage and egress costs matter — show correct Tbps/Gbps arithmetic.

**Scope statement:**

> Design a **CDN** for Netflix-class ABR segment traffic — three-tier cache hierarchy, request coalescing, versioned immutable objects, prefetch for launches, TLS at edge, signed URL auth — scaling from ~0.3 Tbps to 300 Tbps egress with 98%+ HIT ratio and bounded origin draw.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Playback egress (CDN-facing)

```text
Baseline peak concurrent viewers = 100,000
Blended ABR bitrate ≈ 3 Mbps = 3×10^6 bit/s

Total CDN egress ≈ 100,000 × 3 Mbps
                 = 300,000 Mbps
                 = 300 Gbps
                 = 0.3 Tbps
```

| Scale | Concurrent | Egress @ 3 Mbps | @ 4 Mbps (launch night) |
| --- | --- | --- | --- |
| 1× | 100K | **0.3 Tbps** | 0.4 Tbps |
| 10× | 1M | **3 Tbps** | 4 Tbps |
| 100× | 10M | **30 Tbps** | 40 Tbps |
| 1000× | 100M | **300 Tbps** | 400 Tbps |

**Unit check:** 100M × 3 Mbps = 300×10⁶ Mbps = 3×10¹⁴ bit/s = **300 Tbps**. Correct (not PB/s).

### 2.2 Segment request rate

```text
Segment duration ≈ 4 s
Each concurrent viewer ≈ 1 segment request / 4 s = 0.25 req/s

Segment GET rate ≈ concurrent × 0.25
Baseline: 100,000 × 0.25 = 25,000 req/s

ABR switching + manifest fetches + retries + audio tracks → plan ~40× overhead
Round planning number: ~1M segment-class HTTP req/s at 1×
```

| Scale | Concurrent | Raw segment rate (÷4s) | Planning QPS (~40× overhead) |
| --- | --- | --- | --- |
| 1× | 100K | 25K/s | **~1M/s** |
| 10× | 1M | 250K/s | **~10M/s** |
| 100× | 10M | 2.5M/s | **~100M/s** |
| 1000× | 100M | 25M/s | **~1B/s** |

**Deal-breaker:** Terminating 1B/s on application servers — must be **edge cache native**.

### 2.3 Cache HIT ratio → origin egress

```text
Origin draw ≈ CDN_egress × (1 - hit_ratio)

At 1× (0.3 Tbps) with 98% HIT:
  Origin ≈ 0.3 × 0.02 = 0.006 Tbps = 6 Gbps

At 100× (30 Tbps) with 98% HIT:
  Origin ≈ 30 × 0.02 = 0.6 Tbps = 600 Gbps

At 1000× (300 Tbps) with 98% HIT:
  Origin ≈ 300 × 0.02 = 6 Tbps  ← still enormous; need multi-origin + shield + OCAs
```

| HIT ratio | Origin @ 30 Tbps (100×) | Comment |
| --- | --- | --- |
| 90% | 3 Tbps | Launch disaster without prefetch |
| 95% | 1.5 Tbps | Marginal for single origin |
| 98% | 600 Gbps | Target with shield + versioning |
| 99% | 300 Gbps | Tentpole with prefetch |

**Shield benefit (coalescing):** If 10K edge POPs MISS same object simultaneously before any fill completes, without coalescing origin sees 10K fetches; with shield **single-flight**, origin sees **1 fetch**.

### 2.4 Origin shield fill bandwidth

```text
Cold launch: 1M viewers in 10 min on same title, 4 Mbps blended
CDN-side egress = 1e6 × 4 Mbps = 4 Tbps

If prefetch missed and HIT starts at 0%:
  First segment per viewer ≈ 4 MB
  Origin burst ≈ 1e6 × 4 MB = 4 TB in first segment wave
  Time spread 10 min → avg 4 TB / 600 s ≈ 6.7 GB/s ≈ 54 Gbps minimum
  (Real burst sharper → shield must absorb 100+ Gbps spikes)

With 98% HIT after warm (minutes):
  Origin ≈ 4 Tbps × 0.02 = 80 Gbps sustained
```

### 2.5 Edge cache storage (hot set)

```text
Average segment size ≈ 4 MB (720p–1080p blended)
Hot title ≈ 8 GB full ladder per asset version (all rungs, ~2 hr film)

If edge keeps top 100 titles fully warm × 50 POPs:
  100 × 8 GB × 50 = 40 TB per POP average if naive full copy

Realistic: each POP caches **working set** not full catalog
  Hot set per POP ≈ 2–10 TB SSD/NVMe at 100×
  Long tail served from shield/origin on MISS

Catalog segment objects:
  100K titles × ~2000 segments/title ≈ 200M objects (1× baseline catalog)
  At 100× catalog → 20B objects in origin; edge never holds all
```

### 2.6 QPS classes (split — never blend)

| Class | Baseline peak | 100× | 1,000× | Notes |
| --- | --- | --- | --- | --- |
| Edge segment GET | ~1M/s | ~100M/s | ~1B/s | Almost all HIT at steady state |
| Edge manifest GET | ~20K/s | ~2M/s | ~20M/s | Shorter TTL |
| Shield fill (MISS) | ~20K/s | ~200K/s | ~2M/s | 1% of edge if 99% HIT |
| Origin fetch | ~2K/s | ~20K/s | ~200K/s | After coalescing |
| Signed URL verify | ~1M/s | ~100M/s | ~1B/s | Local at edge — crypto budget |
| Purge/prefetch API | ~10/s | ~100/s | ~1K/s | Control plane |
| Cert renewal jobs | ~100/day | ~1K/day | ~10K/day | Automated |

### 2.7 Latency budget (segment HIT path)

| Stage | Budget |
| --- | --- |
| DNS / anycast resolution | 5–20ms (cached locally) |
| TCP + TLS handshake (new conn) | 20–50ms (session reuse helps) |
| HTTP/3 0-RTT (where enabled) | 0–10ms |
| Edge auth verify (HMAC/JWT) | <1ms |
| Cache lookup + disk/SSD read | 1–10ms |
| First byte to client | **p99 < 80ms** same region |

MISS path adds shield RTT + origin RTT — target **not on critical steady-state path**.

### 2.8 Critical bottlenecks

1. **Origin melt** on cold launch without prefetch + coalescing.
2. **Lumping all QPS** into one number (ignore HIT ratio).
3. **Mutable URLs** → cache inconsistency + purge storms.
4. **Missing shield tier** → N POPs × same MISS = N origin fetches.
5. **Signing at origin** instead of edge → origin becomes app server.
6. **Full-object fetch on every Range** → bandwidth waste.
7. **Unbounded purge fan-out** → control plane overload.

### 2.9 Deal-breaker

**Serving segment traffic from stateful app servers** instead of edge cache — won't reach 1M+ req/s per region.

---

## 3. High-Level Design

### 3.1 Cache tier model

```text
Player → L1 Edge POP (commercial CDN or OCA)
              ↓ MISS
         L2 Regional Origin Shield (cluster per region)
              ↓ MISS
         L3 Origin (object storage + optional origin proxy)
```

| Tier | Role | Storage | TTL policy |
| --- | --- | --- | --- |
| L1 Edge | Closest to user; highest QPS | NVMe/SSD 1–20 TB | Long for segments; short for manifests |
| L2 Shield | Coalesce MISS; protect origin | SSD 50–500 TB | Same as edge; single-flight |
| L3 Origin | Authoritative bytes | Object store (PB+) | N/A — source of truth |

**Open Connect angle:** ISP-embedded appliance = **L1 (or L1.5)** inside ISP network; reduces ISP transit costs and improves HIT locality.

### 3.2 Cache key design

**Normalized cache key components:**

```text
cache_key = hash(
  tenant_id,               # multi-tenant isolation
  canonical_url_path,      # includes /v/{assetVersion}/...
  origin_host,
  query_string_normalized, # strip tracking params NOT in signature
  accept_encoding,         # br/gzip for manifests only
  range_normalized,        # policy-dependent — see below
)
```

**Segment objects (preferred):** one whole segment file per URL → **no Range in key** → simpler HIT.

**Range policy options:**

| Policy | When | Key |
| --- | --- | --- |
| Whole-object caching | Small segments (~4 MB) | URL only — **chosen for ABR** |
| Range-as-subkey | Large objects / progressive MP4 | `(url, byte-range)` |
| Merge ranges | CDN normalizes overlapping ranges | Complex; avoid for segments |

**Range on HIT (whole-file policy):** player sends `Range: bytes=0-4194303`; CDN cache key ignores Range; on HIT edge slices cached object → **206 Partial Content** with `Content-Range`. On MISS, shield fetches whole segment once.

**Vary headers:** Do not cache on `Cookie` unless signed cookie is part of auth model; prefer **URL signature** so cache key stays stable.

**Deal-breaker:** Including `Authorization: Bearer` in cache key → zero HIT rate.

### 3.3 Versioned immutable URLs vs purge

| Mechanism | When | Pros | Cons |
| --- | --- | --- | --- |
| **Version flip** | Normal publish | No global fan-out; old bytes still valid for in-flight viewers | New metadata must point to new path |
| **Purge API** | Legal takedown, bad bytes, corruption | Immediate eviction | Slow propagation; error-prone; multi-CDN inconsistency |

```text
# Version flip (preferred)
/v/{assetVersion}/720p/seg_001.m4s
Cache-Control: public, max-age=31536000, immutable

# Publish v43 → new path; v42 ages out via LRU/TTL — no purge storm
```

**Purge when version flip is impossible:** emergency legal removal, cryptographic compromise, manifest pointing at wrong version with long TTL mistake.

### 3.4 TTL and cache-control policy

| Object | Cache-Control | TTL | Invalidation |
| --- | --- | --- | --- |
| Media segment (fMP4) | `public, max-age=31536000, immutable` | 1 year | New version path |
| Media playlist | `public, max-age=60` | 1–5 min | Version bump or short TTL |
| Master playlist | `public, max-age=30` | 30–120 s | Session/manifest rewrite |
| Sprites / thumbs | `immutable` | Long | Version path |
| Error responses | Do not cache long | ≤10 s | N/A |

**stale-if-error:** `stale-if-error=86400` on segments — serve cached if origin 5xx.

### 3.5 Request coalescing (single-flight)

```text
onEdgeMISS(key):
  forward to shield

onShieldMISS(key):
  if acquire_coalesce_lock(key):
    fetch from origin → store → release → notify waiters
  else:
    wait on in-flight fill (poll/subscribe) with timeout
    return shared object or retry peer shield
```

Coalescing scope:

- **Per-shield-cluster** minimum (all edges in region share one flight).
- Optional **global coalesce** for ultra-hot objects (careful with latency).

### 3.6 TLS termination at edge

- Terminate TLS at POP; re-encrypt to origin (optional mTLS) on MISS path.
- **SNI** routes to correct cert / tenant.
- Automated rotation (Let's Encrypt / internal PKI).
- **TLS 1.3** preferred; session tickets for resumption.
- **HTTP/3** on UDP 443 where supported; fallback H2.

**Deal-breaker:** Plain HTTP to end user for premium content.

### 3.7 Signed URLs / cookies

```text
signed_url = base_url + "?exp=...&sig=HMAC(secret, canonical_path + exp + policy)"
```

Edge validates:

1. Signature match (constant-time compare).
2. `exp` not passed (clock skew leeway ±60s).
3. Optional: IP prefix, country, max-bitrate policy embedded in token.

On failure → **403** without origin contact.

### 3.8 Prefetch / push API

```text
POST /prefetch
{
  "asset_version": "av_123",
  "paths": [".../720p/seg_*.m4s"],
  "targets": ["pop:us-east-*", "oca:comcast-*"],
  "priority": "launch",
  "deadline": "2026-08-06T00:00:00Z"
}
```

Control plane fans out to POPs/OCAs; edges pull from shield/origin asynchronously; **does not block** premiere traffic. Monitor `prefetch_coverage_pct` per target.

### 3.9 Purge API (emergency)

```text
POST /purge
{ "tags": ["title:t_99"], "type": "prefix|url|tag", "dry_run": false }
```

Propagation: gossip + central coordinator; **rate-limited**; audit logged. Prefer **version flip** for normal publishes.

### 3.10 Multi-CDN steering

```text
Steering inputs: RTT, packet loss, HIT ratio, cost, contractual commit
Decision: per-session or per-request CDN selection + automatic failover
Abstraction: unified hostnames (CNAME flattening) or RUM-based SDK
```

Challenges: inconsistent purge APIs, different cache key behaviors, log schema normalization.

### 3.11 Multi-tenant isolation

| Layer | Isolation |
| --- | --- |
| DNS / SNI | Per-tenant hostname → cert |
| Cache namespace | `tenant_id` in cache key hash |
| Signing keys | Per-tenant HMAC secret in KMS |
| Metrics | Tenant label on aggregates (not per-user) |
| Prefetch/purge | RBAC scoped to tenant tags |
| Rate limits | Per-tenant WAF quotas |

Shared hardware, logically separate cache partitions — one tenant's purge must not evict another's unrelated keys.

### 3.12 Anycast / GSLB

- **Anycast IP** announces from many POPs; BGP routes client to nearest.
- Health checks withdraw bad POPs.
- **Geo DNS** alternative for fine-grained steering (compliance regions).

### 3.13 Store / component choices

| Component | Choice | Rationale |
| --- | --- | --- |
| Origin | S3 / GCS / Azure Blob | Durability, cost, multi-region |
| Shield | Custom Varnish/Nginx/Envoy + SSD | Coalescing + high MISS throughput |
| Edge | Commercial CDN + OCA fleet | Scale, ISP relationships |
| Control plane DB | PostgreSQL (config, audit) | ACID for purge/prefetch jobs |
| Metrics | Time-series + columnar (ClickHouse) | High-cardinality aggregates |
| Config bus | Kafka / pub-sub | Cert/policy propagation |

### 3.14 Trade-offs summary

| Topic | Decision | Deal-breaker |
| --- | --- | --- |
| Invalidation | Versioned URLs | In-place overwrite |
| Segment size | 4s fMP4 files | Progressive MP4 single URL |
| Auth | Signed URL at edge | Origin session lookup per segment |
| Cold launch | Prefetch + coalesce | Hope for HIT |
| Range | Whole-file segment URLs | Range-heavy caching complexity |
| Purge | Emergency-only | Purge on every publish |

---

## 4. Architecture Diagram

### 4.1 End-to-end overview

```text
                         +------------------ Control Plane ------------------+
                         |  Config API | Purge/Prefetch | Certs | Steering   |
                         +--------+-----------+-------------+--------+--------+
                                  |           |             |
                                  v           v             v
+----------+    signed URL    +---+-----------------------------+    +----------+
|  Player  |----------------->|  L1 Edge POP / Open Connect OCA |--->| Metrics  |
|  (ABR)   |<-----------------|  TLS terminate · auth · cache   |    | QoE pipe |
+----------+    200/206       +---+-----------------------------+    +----------+
                                  | MISS (single-flight upstream)
                                  v
                         +--------+------------------------+
                         |  L2 Regional Origin Shield      |
                         |  coalesce · SSD · peer fill     |
                         +--------+------------------------+
                                  | MISS
                                  v
                         +--------+------------------------+
                         |  L3 Origin Object Storage       |
                         |  versioned segment prefixes     |
                         +---------------------------------+
                                  ^
                                  | write once (packager)
                         +--------+------------------------+
                         |  Media pipeline / packager      |
                         +---------------------------------+

     License path (DRM, separate):  Player ---> License Server (not through byte cache)
```

### 4.2 Data-plane sequences

```text
HIT:     Player → Edge (verify sig) → cache HIT → 200 (~15ms p50)

MISS→shield HIT:
  Player → Edge MISS → Shield HIT → fill Edge → Player

MISS→coalesce:
  Edge1,2,3 → Shield all MISS same key → one origin GET → notify waiters → Origin saw 1 fetch

Prefetch: T-6h Control → Prefetch API → POPs/OCAs warm top rungs → T-0 >99% HIT

Version flip (normal publish):
  Packager writes /v/43/... → play API points to v_43; /v/42/ ages out; no purge

Emergency purge: Ops → Purge API (tag) → rate-limited POP fan-out → 95% ack < 60s
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Immutable bytes** at a given versioned URL — never overwrite in place.
2. **Auth before cache** — unsigned requests never populate cache.
3. **Single-flight coalescing** on shield for identical keys.
4. **stale-if-error** for origin failures on cached segments.
5. **Multi-POP redundancy** — no single POP is hard dependency.
6. **Purge auditable** — who/when/what prefix; dry-run mode.
7. **Cert overlap** — two valid certs during rotation window.
8. **Split QPS planning** — edge vs shield vs origin capacity independent.
9. **Tenant isolation** — purge/prefetch scoped; cache keys namespaced.

**Failure behaviors:**

| Failure | Behavior |
| --- | --- |
| Origin 5xx | Serve stale if available; else 502 + client retry |
| Shield overload | Shed to alternate shield; widen coalesce timeout |
| POP hard down | Anycast withdraw; clients reconnect elsewhere |
| Bad signature | 403; no cache write |
| Purge storm | Rate limit; prioritize tag over full prefix |
| Prefetch incomplete at T-0 | Accept higher MISS; rely on coalesce; page ops |
| TLS cert misconfig | Fail closed on that POP; rotate back |
| Multi-CDN partial purge | Retry failed vendors; alert; version flip unaffected |

### 5.2 Scalability

| Scale | Changes |
| --- | --- |
| 1× | Single commercial CDN + one shield region; manual prefetch |
| 10× | Multi-shield per continent; automated coalesce; signed URL at edge |
| 100× | Open Connect ISP embeds; multi-CDN steering; launch prefetch playbooks |
| 1,000× | OCA peer fill; hierarchical hot-set tracking; cell'd control plane; regional origin replicas |

**Horizontal scaling axes:**

- **More POPs** → linear edge QPS capacity.
- **More shield clusters** → partition by region + hash(url).
- **More origin replicas** → multi-region buckets; CRDT not needed (immutable).

### 5.3 Maintainability

- **Dashboards:** HIT ratio by POP/ASN/title cohort; origin Gbps; coalesce efficiency; prefetch coverage %.
- **Runbooks:** launch checklist; purge drill; cert rotation; POP drain.
- **Feature flags:** steering weights; stale-if-error duration; HTTP/3 rollout.
- **Synthetic probes:** continuous segment fetch from global vantage points.
- **No per-user metric labels** — cardinality explosion.

### 5.4 Core algorithms

**Edge request handler:**

```text
function handle(request):
  if not verify_signature(request): return 403
  key = normalize_cache_key(request)
  obj = local_cache.get(key)
  if obj: return 200(obj)

  resp = shield.fetch(key)  # internal
  if resp.ok:
    local_cache.put(key, resp.body, ttl=LONG)
    return resp
  if local_cache.stale_available(key):
    return 200(stale, header="X-Cache: STALE")
  return 502
```

**Shield coalescing:**

```text
function shield_fetch(key):
  if cache.hit(key): return HIT
  if lock.try_acquire(key):
    try:
      body = origin.get(key)
      cache.put(key, body)
      return body
    finally:
      lock.release(key)
      waiters.notify_all(key)
  else:
    wait waiters[key] timeout=500ms
    return cache.get(key) or retry_peer_shield(key)
```

**Prefetch scheduler:** expand prefixes → resolve target POPs/OCAs → enqueue background fills → track `prefetch_coverage_pct`.

### 5.5 Hot content strategy

| Tier | Detection | Action |
| --- | --- | --- |
| Head (top 100 titles) | QoE + viewership | Permanent warm in all major POPs |
| Launch (tentpole) | Editorial calendar | Prefetch T-6h; monitor warm % |
| Viral spike | Real-time view delta | Auto-prefetch next N segments |
| Long tail | Default | MISS acceptable |

**Hot key isolation:** Ultra-hot object benefits from **peer fill** (OCA-to-OCA) to avoid single shield bottleneck.

### 5.6 Open Connect / ISP embed considerations

- Appliance sits **inside ISP network** → saves ISP transit + improves user RTT.
- Capacity planning per ISP subscriber count.
- Fill path: OCA ← regional shield ← origin (not every OCA hits origin).
- **Off-peak fill** for catalog replication to OCAs (optional background).
- Ops: ISP-specific maintenance windows; remote diagnostics.

### 5.7 Multi-region origin

| Pattern | Use |
| --- | --- |
| Single bucket + cross-region replication | Simpler; higher MISS latency from distant POPs |
| Regional origin buckets | Lower latency MISS; packager writes to all regions for head titles |
| CRDT / multi-writer | **No** — immutable new version per publish |

Failover: shield tries primary origin region → secondary on 5xx/latency.

### 5.8 Security & privacy

- **TLS 1.3** everywhere; HSTS.
- **WAF / rate limit** on unsigned paths.
- **Log sampling** — no PII in URL query if avoidable.
- **mTLS** shield ↔ origin.
- **Key rotation** for signing secrets via KMS; edge caches public verify keys only.

### 5.9 Observability

| Metric | Use |
| --- | --- |
| `edge_hit_ratio` by POP | SLO; launch monitoring |
| `shield_coalesce_saved_fetches` | Proves coalescing value |
| `origin_egress_gbps` | Capacity; launch war room |
| `ttfb_p99` by ASN | ISP issues |
| `prefetch_coverage_pct` | Launch readiness |
| `purge_ack_latency` | Emergency ops |
| `sig_verify_errors` | Attack or clock skew |

### 5.10 Progressive scale deep dive

| Scale | Egress | Key moves |
| --- | --- | --- |
| 1× | 0.3 Tbps | Commercial CDN + one shield; versioned URLs; manual prefetch |
| 10× | 3 Tbps | Multi-shield continents; coalesce service; prefetch API; HTTP/3 pilot |
| 100× | 30 Tbps | Open Connect ISP embeds; multi-CDN steering; regional origin replicas; OCA peer fill |
| 1,000× | 300 Tbps | Hot-set registry; cell'd control plane; BGP traffic engineering; multi-tenant at scale |

### 5.11 Deal-breaker gallery

| Temptation | Failure |
| --- | --- |
| App servers stream video | CPU/network meltdown at 1M+ QPS |
| One headline QPS without HIT ratio | Origin capacity wrong by 50–100× |
| Mutable segment URL | Global cache poison / stale bytes |
| No shield tier | Origin duplicate fetches per POP |
| Purge on every publish | Ops incidents + low effective TTL |
| Cache on Cookie header | Zero HIT rate |
| Ignore Open Connect at 100× | Egress cost and ISP congestion |
| Range-as-subkey on 4 MB segments | HIT ratio collapse |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
| --- | --- |
| Tiering | L1 edge → L2 shield → L3 origin |
| Invalidation | Versioned immutable segment URLs; purge emergency-only |
| Origin protection | Shield + single-flight coalesce |
| Launch | Prefetch top rungs to major POPs/OCAs |
| Auth | Signed URLs validated at edge |
| HIT target | 98%+ steady state; 99%+ tentpoles |
| Range | Whole-object cache; 206 slice on HIT |
| DRM | Encrypted bytes on CDN; license off-path |
| Multi-tenant | Tenant in cache key + signing key isolation |
| Scale-out | Multi-CDN + Open Connect at 100×+ |

### 6.2 Risks

1. **Cold launch** without prefetch → origin meltdown despite coalescing.
2. **HIT ratio regression** from cache key mistakes (Vary headers, Range subkeys).
3. **Purge bug** evicting hot global set.
4. **Multi-CDN inconsistency** after partial purge.
5. **Cert rotation** mishap → POP hard down.
6. **Underestimating origin** at 1000× even with 98% HIT (6 Tbps).

### 6.3 45-minute interview plan

| Min | Focus |
| --- | --- |
| 0–5 | Clarify objects (segments/manifests), scale, auth |
| 5–15 | Three-tier diagram; cache key + TTL policy |
| 15–25 | Back-of-envelope: 0.3→300 Tbps; HIT ratio → origin |
| 25–35 | Coalescing, prefetch, version flip vs purge |
| 35–45 | TLS, anycast, Range, DRM, multi-tenant, traps |

### 6.4 Closer

> **CDN for ABR video:** three-tier cache (edge/shield/origin), versioned immutable URLs, signed auth at edge, coalesce on MISS, prefetch for launches, 98%+ HIT to bound origin — scale with Open Connect and multi-CDN, not app servers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Cache invalidation & versioning

**Q: Purge vs versioned URLs — which do you prefer?**  
A: **Versioned URLs** for segments (`/v/{assetVersion}/...`) with `immutable` — new publish gets new path; old cache ages out naturally. **Purge** only for emergencies (legal, bad bytes). Purge is slow, error-prone, and doesn't propagate instantly globally.

**Q: How invalidate master playlist without purging all segments?**  
A: Short TTL on master/media playlists (30–120s) or version query param on manifest only; segments stay long TTL.

**Q: Tag-based purge vs URL purge?**  
A: Tags (`title:t_99`) map to key sets; faster ops than million-URL lists. Requires tag metadata at ingest; dry-run + audit mandatory.

### 7.2 TLS, HTTP/3, anycast

**Q: Where do you terminate TLS?**  
A: At **edge POP** close to user. Shield/origin use mTLS on private network. Terminating at origin wastes RTT.

**Q: HTTP/3 benefits for video?**  
A: QUIC reduces head-of-line blocking on lossy mobile; 0-RTT resumption for repeat segment fetches. Fallback to H2 required.

**Q: Anycast vs Geo DNS?**  
A: **Anycast** — same IP everywhere, BGP picks nearest POP; fast failover. **Geo DNS** — different IP per region; finer compliance/cost policy. Often **both**.

**Q: What is Open Connect in one sentence?**  
A: Netflix-operated **caching appliances inside ISP networks** to localize traffic and reduce transit costs.

### 7.3 Hot content, shield, cache keys

**Q: How prepare for 2M concurrent premiere?**  
A: Prefetch first N segments × top bitrates to top POPs/OCAs T-6h; verify warm %; shield 10× headroom; monitor origin Gbps.

**Q: Thundering herd math?**  
A: 2M × 4 Mbps = **8 Tbps** CDN; at 99% HIT origin ≈ 80 Gbps; at 90% HIT ≈ **800 Gbps** — prefetch non-negotiable.

**Q: Shield vs more origin replicas?**  
A: **Both**. Shield collapses simultaneous MISS; replicas add geo capacity and HA.

**Q: Cache Range requests separately?**  
A: For **small whole segment files**, cache entire object — **no Range in key**; serve **206** by slicing on HIT. Progressive MP4 uses range-as-subkey.

**Q: Vary: Accept-Encoding / query string?**  
A: Manifests yes (gzip/br); video segments no. Include only signed params in cache key; strip tracking params.

### 7.4 DRM hooks & multi-CDN

**Q: Does DRM break CDN caching?**  
A: **No** for standard SVOD — same encrypted bytes for all subscribers of that asset version; CDN caches ciphertext.

**Q: Where do keys live?**  
A: **License server + KMS/HSM** — never edge cache, never access logs.

**Q: Per-user watermarking?**  
A: Different bytes per user → different cache keys → separate forensic pipeline, not mass segment path.

**Q: Why multiple CDNs? Hardest part?**  
A: Capacity, ISP negotiation, failover. Hardest: unified purge/prefetch, normalized metrics, cache-key consistency across vendors.

### 7.5 Reliability, cost traps, multi-tenant

**Q: Origin down — can users keep watching?**  
A: If segments **HIT or stale** cached — yes. Cold MISS fails until origin returns.

**Q: 100M viewers × 3 Mbps egress?**  
A: **300 Tbps** (not 300 Gbps).

**Q: 98% HIT on 30 Tbps — origin?**  
A: 30 × 0.02 = **0.6 Tbps = 600 Gbps**.

**Q: Multi-tenant shared CDN fleet?**  
A: Namespace `tenant_id` in cache key; per-tenant signing keys and SNI certs; purge RBAC scoped by tenant tag.

**Q: Peer fill between OCAs?**  
A: One OCA fetches; peers on same ISP pull locally — reduces shield load.

### 7.6 Interview traps (quick)

| Trap | Pushback |
| --- | --- |
| "Purge on every encode" | Version paths; purge is emergency |
| "Origin serves every viewer" | Edge HIT 98%+; origin is MISS path |
| "One QPS number for CDN" | Split edge/shield/origin/control |
| "Cache on Authorization header" | Zero HIT; use URL signature |
| "100M × 3 Mbps = 300 Gbps" | **300 Tbps** — 1000× error |
| "DRM prevents CDN cache" | Encrypted bytes cache fine |
| "Skip shield — S3 scales" | MISS storm duplicates; coalesce needed |
| "Range-as-subkey on 4 MB segments" | HIT ratio collapse |

---

## 8. Appendices

### 8.1 Cache key schema

```text
key = SHA256("v1", tenant_id, origin_id, path, normalized_query, encoding_identity)
# path: /catalog/t_1/v/42/720p/seg_001.m4s
# encoding: "identity" for video; "gzip" for manifests
# Range NOT in key for whole-file segment policy
```

### 8.2 Control-plane schemas

```text
PrefetchJob { job_id, tenant_id, asset_version, path_prefixes[], target_selector, deadline_ts, coverage_pct }
PurgeJob    { purge_id, tenant_id, type: URL|PREFIX|TAG, value, dry_run, ack_pop_count }
```

### 8.3 TTL policy (YAML)

```yaml
policies:
  - match: "**/*.m4s"
    cache_control: "public, max-age=31536000, immutable"
    stale_if_error: 86400
  - match: "**/master.m3u8"
    cache_control: "public, max-age=30"
  - match: "**/media.m3u8"
    cache_control: "public, max-age=60"
```

### 8.4 Launch checklist

- [ ] Asset version packaged; versioned URLs in play API
- [ ] Prefetch T-6h; coverage > 95% POPs/OCAs
- [ ] Shield 2× headroom; origin Gbps alerts armed
- [ ] Manifest short TTL; segments immutable
- [ ] Multi-CDN steering validated; rollback pointer tested

### 8.5 Worked launch example

```text
5M concurrent × 4 Mbps = 20 Tbps CDN egress
No prefetch, 95% HIT → origin 1 Tbps (outage risk)
Prefetch + 99% HIT → origin 200 Gbps (manageable)
Cold first segment + coalesce only → ~200 origin fetches (not 5M) but shield fan-out heavy
```

### 8.6 Pseudocode — Range on HIT

```text
function serve_segment(request):
  key = normalize_key(request)  # no Range in key
  obj = cache.get(key) or fill_from_shield(request)
  if request.has_range():
    return 206(obj.bytes[range], Content-Range=...)
  return 200(obj)
```

### 8.7 Metrics & SLOs

```text
edge_hit_ratio{pop, tenant}          # target ≥ 98% steady, ≥ 99% tentpole
shield_coalesce_saved_fetches
origin_egress_gbps                   # target < 700 Gbps at 100× normal
ttfb_p99{pop, asn}                   # target < 80ms HIT same metro
prefetch_coverage_pct                # target ≥ 95% @ T-0
purge_ack_latency_ms                 # target p95 < 60s
```

### 8.9 Glossary

| Term | Meaning |
| --- | --- |
| POP | Point of Presence — edge data center |
| OCA | Open Connect Appliance — ISP-embedded cache |
| Origin shield | Mid-tier cache coalescing origin fetches |
| HIT / MISS | Cache found / not found |
| Single-flight | One in-flight fetch per key; waiters share result |
| Anycast | Same IP from multiple sites; BGP routes nearest |
| Tentpole | Major scheduled launch (finale, film premiere) |
| Version flip | Publish new immutable URL path instead of purge |

### 8.10 Reliability test plan

1. 10K concurrent MISS same key → ≤1 origin fetch per shield cluster.  
2. Origin 503 → edge serves stale segment.  
3. Bad signature → 403; no cache pollution.  
4. Prefetch job → coverage ≥ 95% before deadline.  
5. Tag purge → keys evicted within SLA.

### 8.11 Interview "say this" (60 seconds)

> Design a **three-tier CDN** for ABR segments: **edge POP/Open Connect** → **regional origin shield** → **object storage**. **Versioned immutable URLs** for segments; short TTL manifests. **Signed URLs at edge**. On MISS, **coalesce** N requests → 1 origin fetch. **Prefetch** top rungs T-6h for tentpoles. Plan with **split QPS** and **98% HIT** — 30 Tbps egress → **600 Gbps** origin. Cache **whole segments**; **206** from cached object on Range. **Version flip** beats purge. At 100×+: **multi-CDN** + **Open Connect** + **multi-tenant** isolation.

---

*End of Netflix system design interview prep: Content Delivery Network (CDN).*
