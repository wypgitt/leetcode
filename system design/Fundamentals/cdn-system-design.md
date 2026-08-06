<!-- Adapted into Fundamentals bank from Netflix/cdn-system-design.md for cross-company prep. -->

# System Design: Content Delivery Network (CDN) for ABR Video

> **Focus areas:** Open Connect · Edge POPs · Origin shield · Request coalescing · Versioned URLs · Prefetch · Multi-CDN · Tbps egress math · HIT ratio · ABR segment workloads  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct bandwidth arithmetic, split dissimilar QPS (edge GET vs shield fill vs origin egress vs control), explicit deal-breakers, Netflix streaming 2025–26 interview themes  
> **Interview theme:** Netflix CDN — deliver adaptive video segments at hundreds of Tbps with Open Connect economics and origin protection

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

Goal: **bound the CDN**—the global delivery layer that serves HTTP objects (ABR manifests, encrypted video segments, subtitles, trick-play sprites) from edge caches close to viewers, with high cache HIT ratio, low startup latency, and protected origins.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Cache & deliver bytes at edge for playback | Full encode/transcode pipeline |
| Netflix angle | Open Connect appliances + optional commercial CDN | Ads decision / homepage rank |
| Objects | fMP4 segments, manifests, text tracks, images | DRM license server (sibling) |
| Client | Player segment fetch pattern | Full player ABR algorithm deep dive |
| Control | Prefetch, purge, steering, cert rotation | Entitlement / geo-rights (manifest sibling) |
| Live | Overview hooks (segment churn) | Full live origin + low-latency packager |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What objects? | HLS/DASH manifests, 2–6s fMP4 segments, audio/text sidecars, thumbnails | Cache key = URL + range policy |
| F2 | Protocols? | HTTPS, HTTP/2, HTTP/3 (QUIC) | TLS termination at edge; 0-RTT policy |
| F3 | Cache fill? | Pull on MISS from shield → origin | Tiered hierarchy; coalescing |
| F4 | Invalidation? | **Versioned immutable URLs** primary; emergency purge secondary | No global purge on every encode fix |
| F5 | Auth? | Signed URLs / cookies tied to entitlement | Edge verify before bytes |
| F6 | Geography? | Global POPs + ISP-embedded Open Connect | Anycast / DNS steering |
| F7 | Range requests? | Whole-segment fetch typical; byte-range for some assets | Segment-sized objects preferred |
| F8 | Hot launch? | Tentpole title drops → proactive prefetch | Push API + popularity model |
| F9 | Multi-CDN? | Netflix OC primary; commercial CDN overflow in some markets | Abstract steering layer |
| F10 | Observability? | HIT/MISS, TTFB, egress Tbps, origin load | Per-POP + per-title dashboards |
| F11 | Stale-if-error? | Serve slightly stale segment on origin blip | `stale-while-revalidate` policy |
| F12 | Logging? | Sampled access logs for QoE; not full payload | Privacy + cardinality control |
| F13 | ABR ladder? | Many renditions per title (240p–4K HDR) | Long-tail key space; long TTL OK |
| F14 | DRM? | Segments encrypted (AES-128/CENC); keys via license svc | CDN carries ciphertext only |
| F15 | IPv6 / dual-stack? | Required in many ISPs | Bind + cert SAN coverage |

**MVP functional scope (lock with interviewer):**

1. Three-tier cache: **edge POP → origin shield → object origin (S3-class)**.
2. TLS termination + HTTP/2 at edge; optional HTTP/3 at 100×.
3. Signed URL validation at edge (HMAC/JWT) before cache lookup.
4. **Request coalescing** on concurrent MISS for same cache key.
5. **Versioned immutable object URLs** (`/v/{content_version}/...`) with long `Cache-Control: max-age`.
6. Prefetch API for ops/marketing launches (title + rendition set).
7. Emergency purge API (path/tag) with SLA disclaimer vs versioning.
8. Metrics: HIT ratio, fill rate, origin egress, p95 TTFB, coalesce savings.
9. Multi-CDN steering hook (even if MVP is OC-only).

**Out of MVP (explicitly defer):**

- Building a global private fiber backbone
- Full edge compute / WASM transcoding at POP
- P2P-assisted delivery as primary path
- Per-viewer personalized segment URLs (breaks cache)
- Real-time per-byte billing at edge
- Client-side cache as authoritative QoE SoT

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Edge TTFB (segment HIT)? | Inside player startup budget | p50 < 20ms; p99 < 80ms same metro |
| N2 | HIT ratio | Dominates cost | **≥ 95% edge HIT** baseline; ≥ 98% at 10× with prefetch |
| N3 | Origin protection | Origin never sees full fan-out | Shield + coalesce → origin ≪ edge QPS |
| N4 | Availability | Playback-critical | 99.99% for edge GET path |
| N5 | Scale | Peak concurrent streams | See scale table (Tbps egress) |
| N6 | Consistency | Immutable versioned objects | Eventual purge propagation OK |
| N7 | Security | No unsigned premium bytes | Fail closed on bad signature |
| N8 | Cost | Egress $ dominates | Maximize HIT; embed in ISP (OC) |
| N9 | Launch spike | 10× normal on tentpole | Prefetch + shield headroom |
| N10 | Privacy | Access logs minimized | Sampled; no playback content in logs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Player requests manifest → edge HIT → sub-50ms → parser selects rung.  
2. Player requests segment `S` at 1080p → edge HIT → 4 MB delivered in one RTT.  
3. First viewer in POP for new episode → edge MISS → shield HIT → fill edge.  
4. First viewer globally for cold segment → edge MISS → shield MISS → coalesced origin fetch → both tiers fill.  
5. Bandwidth drops → player switches rung → different URL → may MISS briefly then HIT.  
6. Signed URL expires mid-playback → player refreshes URLs from app API.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Concurrent MISS storm on same segment | **Single-flight coalesce** → one origin fetch |
| Origin timeout on fill | Retry shield; serve stale if policy allows; player rebuffer |
| Bad signature / expired token | 403; no cache pollute |
| Partial range on segment object | Prefer whole-object cache; range merge or pass-through policy |
| Purge during playback | Old version URL still valid until TTL if versioned |
| POP disk full | Evict LRU/LFU weighted by title popularity |
| ISP embed OC box offline | Steer to nearby POP or commercial CDN |
| Hot key (finale episode) | Coalesce + prefetch; not “bigger origin” |
| Encode fix (bad segment) | **Bump content_version** in manifest URLs; no global purge |
| TLS cert expiry | Automated ACME; dual cert overlap window |
| DDoS on CDN hostname | Anycast absorb + rate limit + scrub center |
| Clock skew on signed URL | Short validity + client clock slack documented |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak concurrent streams | 15M | 150M | 500M | 1B+ |
| Edge segment GETs / s | 5M | 50M | 500M | 5B |
| Aggregate egress | 100 Tbps | 200 Tbps | 400 Tbps | 800 Tbps+ |
| Distinct cache keys (hot set) | 50M | 200M | 2B | 20B |
| Origin egress (after HIT) | 2 Tbps | 4 Tbps | 8 Tbps | 16 Tbps |
| Open Connect sites | 1K | 2K | 3K | 5K+ |
| Commercial CDN share | 10% | 8% | 5% | 3% |
| Prefetch titles / launch window | 500 | 2K | 10K | 50K |
| Shield POPs | 20 | 40 | 80 | 150 |

**Split classes:** edge segment GET ≠ shield fill ≠ origin egress ≠ prefetch push ≠ purge/control ≠ cert/config.

**What each jump forces:**

- **10×:** Origin shield mandatory; coalesce locks; versioned URLs enforced; prefetch orchestrator.  
- **100×:** ISP Open Connect embeds at scale; hierarchical hot-set replication; multi-CDN steering automation.  
- **1,000×:** Global key popularity tiering; edge stale tiers; dedicated shield clusters per region; control-plane sharding.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like **VOD-first** ABR with 2–6 second fMP4 segments (~2–8 MB at HD).  
- **Open Connect (OC):** Netflix-operated cache appliances inside ISP networks + regional POPs.  
- Manifest service publishes **immutable versioned URLs** after encode completes.  
- Player fetches segments in bursts (ABR buffer 15–30s ahead).  
- Sibling docs: video streaming service, entitlement, DRM license, QoE beacons.

**Scope statement:**

> Design a global CDN for Netflix-class adaptive video — edge POPs (Open Connect), origin shield, request coalescing, versioned URLs, prefetch for launches, optional multi-CDN overflow — scaling from ~100 Tbps aggregate egress through 10× / 100× / 1,000× with explicit HIT ratio and origin-protection math.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Viewing → segment QPS

```text
Peak concurrent streams (baseline)     = 15,000,000
Average segment duration               = 4 s
Segments consumed / stream / s         = 1 / 4 = 0.25

Edge segment GETs / s ≈ 15M × 0.25 = 3.75M / s  → round to ~4M / s

With overhead (manifests, audio, retries, multi-audio) × 1.25:
  Edge HTTP GETs / s ≈ 5M / s baseline
```

At **100×** concurrent (aggressive table): 500M streams → **~170M segment GETs/s** class — requires massive POP fan-out, not a bigger origin.

### 2.2 Bandwidth (Tbps)

```text
Average bitrate per stream ( blended HD ) ≈ 5 Mbps
Aggregate egress = 15M × 5 Mbps = 75 Tbps  → ~100 Tbps with 4K/HDR tail

Per-stream segment size ≈ 5 Mbps × 4 s / 8 = 2.5 MB (order-of-magnitude)

Edge egress check:
  4M segments/s × 2.5 MB ≈ 10 GB/s ≈ 80 Tbps payload class
  (aligns with ~100 Tbps headline after overhead + higher rungs)
```

**Deal-breaker:** planning origin for 100 Tbps because “CDN = cache” without HIT ratio math.

### 2.3 HIT ratio → origin load

```text
Edge HIT ratio H_e = 98%
Shield HIT ratio H_s = 90% (of edge MISS)

Edge MISS rate = 1 - H_e = 2%
Shield MISS rate = 2% × (1 - H_s) = 2% × 10% = 0.2%

Origin fetch rate ≈ 5M × 0.002 = 10,000 origin fetches / s baseline

Without shield (H_s = 0): 5M × 2% = 100,000 origin / s  → 10× worse

Origin egress ≈ 100 Tbps × 0.2% ≈ 0.2 Tbps (only edge MISS × shield MISS reach origin)
With coalesce on hot MISS: effective origin often ≪ 1 Tbps baseline
```

State explicitly: **HIT ratio is the primary cost knob.**

### 2.4 Request coalescing gain

```text
Finale episode segment S: 50,000 concurrent viewers in one POP miss together
Without coalesce: 50,000 shield/origin fetches
With single-flight: 1 fetch + 49,999 waits → fill fan-out

Coalesce collapse factor C ≈ 100–10,000 on tentpoles
Origin QPS effective = raw_miss_qps / C
```

### 2.5 Storage per POP

```text
Hot catalog working set ≈ 20 TB (popular titles × top renditions)
Long-tail spread across fleet; each OC box 100 GB – 8 TB NVMe

Keys in hot set 50M × avg 3 MB ≈ 150 TB globally deduplicated across fleet
Per POP stores subset: 1–5 TB typical embed appliance
```

Eviction: **LFU with launch boost**; pin prefetch set during launch window.

### 2.6 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Edge segment GET | 5M | 500M | 5B | cache HIT path |
| Edge manifest GET | 200K | 20M | 200M | small objects |
| Shield fill fetch | 100K | 10M | 100M | after coalesce |
| Origin object GET | 10K | 1M | 10M | S3/partitioned |
| Prefetch push ops | 1K | 10K | 100K | control burst |
| Purge API | 10 | 100 | 1K | rare; version preferred |
| Cert/config deploy | 1/min | 1/min | 1/min | global rollout |

### 2.7 Latency budget (segment HIT)

| Stage | Budget |
|-------|--------|
| DNS / steering | 0–5ms (cached) |
| TCP + TLS (H2) | 5–20ms (reuse connection: 0) |
| Edge cache lookup + disk/NVMe read | 2–15ms |
| First byte to player | **p99 < 50ms metro HIT** |
| Edge MISS → shield fill | +30–80ms one-time |
| Origin fill (cold) | +100–300ms; player buffers ahead |

### 2.8 Critical bottlenecks

1. **Origin fan-out** if HIT ratio slips 98% → 95% (origin 4×).  
2. **Thundering herd** on MISS without coalescing.  
3. **Disk / NVMe throughput** per POP during launch prefetch verify.  
4. **TLS CPU** at edge without session reuse / QUIC offload.  
5. **Long-tail key explosion** (every rendition × every segment × every audio).  
6. **Purge storms** invalidating hot keys globally.

### 2.9 Cost intuition

```text
Commercial CDN egress ≈ $0.02–0.08 / GB (list; varies)
Open Connect: CapEx appliances + colocation vs pure cloud egress

1 Tbps ≈ 112 TB/h ≈ 2.7 PB/day
1% HIT improvement on 100 Tbps ≈ 1 Tbps origin avoided ≈ massive $

Track: $/PB-month at edge, origin_egress_Gbps, coalesce_factor p50/p99
```

---

## 3. High-Level Design

### 3.1 Planes

```text
Data plane:  Player → Edge POP → (Shield) → Origin object store
Control plane: Steering, prefetch orchestrator, purge, cert manager, popularity
Observability: Sampled logs → QoE pipeline (sibling); HIT/MISS metrics
```

### 3.2 Cache hierarchy

| Tier | Role | HIT target |
|------|------|------------|
| Edge POP / OC appliance | Closest to viewer; largest aggregate QPS | 95–99% |
| Origin shield | Collapse regional MISS; protect origin | 85–95% of edge MISS |
| Object origin | S3-compatible durable store; authoritative bytes | 100% on fetch |

Optional **mid-regional aggregation** at 100× between edge and shield.

### 3.3 Cache key

```text
CacheKey = hash(
  canonical_url,           // includes content_version path segment
  accept_encoding?,       // if variants
  byte_range_policy       // whole-object vs range map
)

Do NOT include user_id in cache key for segments (breaks HIT)
Auth is gate BEFORE lookup, not part of key
```

### 3.4 Versioned URLs (invalidation strategy)

```text
Bad encode fixed → content_version: v42 → v43
Manifest points to .../v43/seg-00001.m4s
Old v42 objects age out via TTL; no global purge required

Emergency purge: legal takedown → purge by tag title_id=T123 across POPs
```

**Prefer immutability + pointer swap in manifest** over CDN purge.

### 3.5 Signed URL / cookie

```text
Edge validates:
  signature, expiry, title_id entitlement scope (optional claims)
Invalid → 403, do not cache negative responses long

Player refreshes URLs before expiry via Playback API (sibling)
```

### 3.6 Request coalescing (single-flight)

On Edge MISS: one winner acquires `inflight(key)`, fetches from shield, stores, releases waiters; others block until fill completes. Shield applies identical pattern toward origin.

### 3.7 Prefetch

```text
LaunchOrchestrator(title_id, renditions[], target_pops[]):
  enumerate hot segment URLs (first N minutes + top rungs)
  push to POP prefetch queue
  POP fetches from shield/origin at low priority
  verify HIT ratio before go-live
```

SteeringDNS / client config: primary Open Connect anycast; fallback commercial CDN if POP unhealthy or region gap. Per-CDN signing keys — never duplicate origin secrets blindly.

### 3.9 Eviction & TTL

| Object | TTL | Notes |
|--------|-----|-------|
| Versioned segment | 30–365 d | immutable |
| Manifest | 60–300 s | short; points to versions |
| Subtitle | 7–30 d | versioned preferred |
| Error 403/404 | 0–10 s | no cache poison |

Eviction: **SLRU or LFU** with launch pinning.

### 3.10 Open Connect specifics

Appliances in **ISP central office** offload transit; Netflix CapEx hardware, ISP provides rack/power; remote config + health via Open Connect Partner Portal.

### 3.11 Failure policy matrix

| Failure | Policy |
|---------|--------|
| Edge MISS + shield down | Try alternate shield; stale-if-error |
| Origin down | Serve stale segment if allowed; player rebuffer |
| Bad signature | Fail closed 403 |
| POP overload | Steer to neighbor POP / commercial CDN |
| Prefetch incomplete at launch | Graceful MISS + coalesce; not abort launch |

### 3.12 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Invalidation | Versioned URLs primary |
| Origin protection | Shield + coalesce |
| Segment sizing | ~2–6s whole-object cache |
| Auth | Signed URL at edge |
| Launch | Prefetch + popularity |
| Overflow | Multi-CDN minority share |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+  manifest/segment   +------------------+     +------------------+
| Player |-------------------->| Edge POP (OC)    |---->| Shield Cluster   |
+--------+   HTTPS H2/H3       +--------+---------+     +--------+---------+
                                        | HIT                      | MISS
                                        v                          v
                                 +-------------+          +------------------+
                                 | Local NVMe  |          | Origin (S3)      |
                                 | cache       |          | + encode publish |
                                 +-------------+          +------------------+

Control: +------------------+    +------------------+    +------------------+
         | Steering / DNS   |    | Prefetch Orch.   |    | Purge / Config   |
         +------------------+    +------------------+    +------------------+
```

### 4.2 Sequence: edge HIT

```text
Player→Edge: GET /v43/title/seg-001.m4s + Range: bytes=0-
Edge: validate signature/expiry
Edge: cache lookup key → HIT
Edge→Player: 200 + data (Age header)
```

### 4.3 Sequence: edge MISS with coalesce

```text
Player1..N→Edge: GET same seg-001 (MISS)
Edge: one winner acquires inflight(key)
Edge→Shield: GET seg-001
Shield: HIT → bytes
Edge: store NVMe, release waiters
Edge→Player1..N: 200 (first waits ~50ms, rest faster)
```

### 4.4 Sequence: cold path to origin

```text
Edge→Shield: MISS
Shield: coalesce inflight(key)
Shield→Origin: GET object
Origin→Shield: 200 + bytes
Shield: store, fill Edge
Edge→Player: 200
Subsequent: HIT
```

### 4.5 Sequence: tentpole prefetch

```text
Ops→PrefetchAPI: title=T, pops=[...]
PrefetchOrch→Shield: enumerate URLs
PrefetchOrch→Edge POPs: PREFETCH queue (rate limited)
Each POP: background fill, report warm_pct
Dashboard: warm_pct ≥ 95% before prime time
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No unsigned premium bytes** served from cache.  
2. **Immutable version in URL** for segment objects; fixes = new version.  
3. **Single-flight coalesce** for identical cache key on MISS path.  
4. **Shield always in front of origin** at 10×+.  
5. **Stale-if-error** only for objects with explicit policy flag.  
6. **POP failure → steering shift**, not player hard fail.  
7. **Prefetch is best-effort**; playback must survive cold MISS.  
8. **Access logs sampled**; never log signing secrets.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| NVMe read error | Treat as MISS; refetch; bad block alert |
| Coalesce leader crash | Timeout → new leader fetch; dup origin OK (idempotent GET) |
| Shield partition | Edge serves stale if allowed else neighbor shield |
| Origin slow | Player buffer absorbs; shield extends timeout |
| Bad prefetch list | MISS only; no incorrect bytes |
| Cert misdeploy | Canary POPs first; rollback cert pointer |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Cloud CDN + single shield region; basic coalesce |
| 10× | Open Connect embeds; shield per continent; prefetch service |
| 100× | Hierarchical shield; popularity-aware replication; HTTP/3 |
| 1,000× | Global hot-set tiering; multi-CDN automation; sharded control plane |

**Sharding:** POPs are naturally sharded by geography; origin by object key prefix (`title_id/hash`).

### 5.3 Maintainability

- **Remote config** to OC boxes: TTL presets, eviction weights, log sample rate.  
- **Canary POP** for cache software + cert changes.  
- Metrics without per-user labels: `pop_id`, `title_tier`, `object_class`.  
- **Simulate launch** in shadow POP with synthetic prefetch load.  
- Runbooks: HIT drop, origin spike, cert expiry, steering flap.

### 5.4 Exact algorithm: edge GET with coalesce

```text
function handleGet(req):
  if not validateSignature(req): return 403
  key = cacheKey(req.url, req.rangePolicy)
  blob = cache.get(key)
  if blob.hit: return 200(blob, age=cache.age)

  if inflight.tryAcquire(key):
    try:
      blob = shield.fetch(req.url)
      cache.put(key, blob, ttl=immutable_ttl)
    finally:
      inflight.release(key, blob)
  else:
    blob = inflight.wait(key, timeout=fill_timeout)
    if blob == TIMEOUT: blob = shield.fetch(...)  // fallback

  return 200(blob)
```

Shield tier uses the same single-flight pattern toward origin with retry/backoff.

### 5.5 HIT ratio optimization levers

| Lever | Effect |
|-------|--------|
| Versioned long TTL | Stable keys |
| Segment duration ↑ | Fewer unique GETs / hour |
| Prefetch launches | Converts MISS→HIT before peak |
| Popularity replication | Pre-position long-tail batch overnight |
| Shield tier | Second chance before origin |
| Avoid querystring auth in URL | Same key for all viewers |

### 5.6 ABR-specific CDN behavior

Player bursts **3–8 segments** ahead (sawtooth QPS); rendition switch causes brief cold rung MISS; manifests refresh every 30–120s — small-object HIT critical.

### 5.7 Open Connect vs commercial CDN

| Aspect | Open Connect | Commercial CDN |
|--------|--------------|----------------|
| CapEx/OpEx | Hardware + ops | Per-GB egress |
| ISP relationship | Embedded | Transit |
| Control | Full cache software | Vendor API limits |
| Use case | Core markets at scale | Long tail / overflow |

### 5.8 Multi-CDN steering

`selectEdge(user)`: geo/ISP lookup → healthy OC POP if available → else commercial CDN region → else OC fallback POP (longer RTT). Health signals: HIT drop, fill errors, p99 latency, capacity headroom.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|--------|
| Origin serves all viewers directly | Instant collapse at 15M streams |
| User id in cache key | HIT → 0%; cost explosion |
| Global purge on every fix | Cache cold worldwide; rebuffer storm |
| No coalesce on tentpole | Origin DDoS from own traffic |
| Short TTL on immutable segments | needless refetch; low HIT |
| Ignore shield tier | Origin QPS ×10–50 |
| One headline QPS without split | Wrong capacity plan |
| Cache 403 errors long | Lock users out |
| Personalized segment URLs | CDN becomes dumb pipe |

### 5.10 Progressive scale deep dive

**1× (~100 Tbps, 5M GET/s):** Regional edge + shield; coalesce; versioned URLs; manual prefetch.  
**10×:** OC embeds; shield per continent; automated prefetch; HTTP/2 reuse; LFU eviction.  
**100×:** Hierarchical shield; multi-CDN overflow; HTTP/3; overnight long-tail warmer.  
**1,000×:** Sharded hot-set control plane; tier-0 titles pinned globally; origin prefix partition.

### 5.11 Security & observability

TLS 1.3; short-lived signed URLs; hardened OC appliances; sampled logs without tokens. Page on `edge_hit_ratio` drop, `origin_egress_gbps` spike, `fill_error_rate`, cert expiry.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Hierarchy | Edge → shield → origin |
| Invalidation | Versioned immutable URLs |
| Herd control | Request coalescing |
| Launch | Prefetch orchestrator |
| Economics | Open Connect primary |
| Overflow | Multi-CDN minority |
| Auth | Edge signed URL verify |
| Key design | No per-user segment keys |

### 6.2 Risks

1. HIT ratio regression (1% → large origin $)  
2. Tentpole without prefetch → coalesce stress  
3. Purge misuse instead of versioning  
4. TLS/cert operational error  
5. Steering flap during partial outage  
6. Long-tail storage exhaustion on small OC boxes  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: ABR segments; OC; not encode |
| 5–15 | Hierarchy + cache key + versioned URLs |
| 15–25 | Tbps math + HIT ratio → origin load |
| 25–35 | Coalesce + shield + prefetch launch |
| 35–45 | Multi-CDN, failure modes, deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Purge vs versioning

**Q: How update a bad segment?**  
A: Publish new `content_version` in manifest paths; old objects expire by TTL. Purge only for legal/emergency.

**Q: Why immutable URLs?**  
A: CDN caches are optimized for long HIT; global purge is slow and causes MISS storms.

### 7.2 Request coalescing

**Q: Difference vs lock?**  
A: Single-flight: concurrent MISS waiters share one fill. Distinct keys fetch independently.

**Q: Leader crash mid-fetch?**  
A: Waiters timeout; new leader refetches; duplicate origin GET safe for immutable GET.

### 7.3 HIT ratio

**Q: 98% vs 95% edge HIT impact?**  
A: MISS triples (2% → 5%); origin load and fill latency disproportionately hurt tail titles.

**Q: Measure HIT?**  
A: `1 - (fill_bytes / response_bytes)` per tier; segment-class only.

### 7.4 Open Connect

**Q: Why ship appliances to ISPs?**  
A: Moves bits closer; reduces ISP transit and Netflix commercial egress $; scales past pure cloud.

**Q: Who owns hardware?**  
A: Netflix CapEx; ISP provides rack/power/network.

### 7.5 Origin shield

**Q: Why not edge → origin directly?**  
A: Edge POP count × MISS rate would overwhelm origin and cross-region links.

**Q: Shield vs regional mid-tier?**  
A: Same concept; scale adds hierarchy layers.

### 7.6 ABR interaction

**Q: CDN pick bitrate?**  
A: No — player ABR chooses rung; CDN serves requested URL.

**Q: Segment length tradeoff?**  
A: Longer segments → fewer GETs higher HIT stability; longer rebuffer on loss.

### 7.7 Signed URLs

**Q: Put token in cache key?**  
A: No — same bytes for all authorized viewers; validate before lookup.

**Q: Token expiry during playback?**  
A: Player refreshes manifest/URLs via API; segments already buffered play through.

### 7.8 Multi-CDN

**Q: When use commercial CDN?**  
A: Geographic gap, burst overflow, DR, ISP without OC deal.

**Q: Consistent HIT across CDNs?**  
A: Each CDN has own cache; prefetch per vendor; versioned URLs help all tiers.

### 7.9 Live vs VOD

**Q: Live segment caching?**  
A: Very short TTL; many unique keys; origin pull or mid-tier packager push — harder HIT.

**Q: This design?**  
A: VOD-first; live needs separate segment churn discussion.

### 7.10 Prefetch

**Q: Prefetch everything?**  
A: No — top titles × top rungs × first N minutes; cost/storage bounded.

**Q: Wrong prefetch?**  
A: Wasted disk; playback still correct via MISS fill.

### 7.11 Interview traps

**Q: “CDN caches per user”?**  
A: Breaks HIT; segments are shared ciphertext objects.

**Q: “Use DNS TTL for invalidation”?**  
A: DNS is steering layer; object invalidation is URL versioning.

**Q: “One POP worldwide”?**  
A: Latency and capacity fantasy.

### 7.12 Cost & QoE

**Q: Dominant cost?**  
A: Egress bandwidth; HIT ratio and OC embeds drive margin.

**Q: CDN guarantee no rebuffer?**  
A: No — player buffer + ABR + CDN TTFB contribute; page on origin egress spike, HIT drop, fill errors.

---

## 8. Appendices

### A1. URL layout (versioned)

```text
https://oc.netflix.com/v/{content_version}/title/{title_id}/{rendition}/seg-{n}.m4s
https://oc.netflix.com/v/{manifest_version}/title/{title_id}/manifest.mpd

Query: ?sig=...&exp=...   (validated at edge, not in cache key)
```

### A2. Cache-Control templates

```text
Segment (immutable):  Cache-Control: public, max-age=31536000, immutable
Manifest (mutable):   Cache-Control: public, max-age=120, must-revalidate
Emergency takedown:   Purge-Tag: title_id=12345
```

### A3. Prefetch request schema

```text
PrefetchJob {
  job_id,
  title_id,
  content_version,
  renditions: ["1080p", "720p", ...],
  segment_range: [0, 450],     // first 450 segs (~30 min @ 4s)
  target_pops: ["pop_...", ...],
  priority: LAUNCH | BACKFILL,
  deadline_ts
}
```

### A4. Launch checklist

- [ ] Prefetch job submitted ≥ 24h before launch  
- [ ] warm_pct ≥ 95% on target POPs  
- [ ] Shield headroom 2× expected MISS  
- [ ] Coalesce baseline + cert valid ≥ 30 days  

### A5. Glossary

| Term | Meaning |
|------|---------|
| ABR | Adaptive bitrate — player selects quality rung |
| Open Connect | Netflix CDN program with ISP-embedded appliances |
| POP | Point of presence — edge cache site |
| Origin shield | Mid-tier cache protecting object store |
| Coalesce / single-flight | One fetch serves many concurrent MISS waiters |
| HIT ratio | Fraction of requests served from cache |
| fMP4 | Fragmented MP4 segment container |
| Rendition | Encoded bitrate/resolution ladder rung |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| Global purge on fix | Version bump |
| Per-user cache key | HIT collapse |
| Skip shield | Origin meltdown |
| Origin for all Tbps | HIT math mandatory |
| CDN chooses bitrate | Player ABR job |

### A7. Reliability test plan

1. Concurrent 10K MISS same key → origin QPS ≈ 1.  
2. Shield outage → stale-if-error serves if enabled.  
3. Version bump → no purge; new URLs cold then HIT.  
4. Bad signature → 403 not cached.  
5. POP failure → steering removes within SLA.  
6. Prefetch incomplete → playback succeeds via fill.  
7. Load: 10× Zipf popularity; chaos shield kill → single origin fetch.

### A8. 60-second summary

> Netflix CDN delivers **immutable versioned ABR segments** from **Open Connect edge POPs** with **shield + request coalescing** protecting origin. **HIT ratio** drives Tbps economics; **prefetch** handles launches; **multi-CDN** overflows gaps. Never put **user id in cache keys**; fix content by **version pointer**, not global purge.

### A9. Related systems map

```text
Encode/Publish → Origin (S3) → Shield → Edge OC → Player
Manifest Service → versioned URLs
Playback API → signed URL refresh
Entitlement → scope for signing
QoE → sampled edge logs + player beacons
Steering DNS → POP selection
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Edge HIT ratio (VOD seg) | ≥ 98% |
| Shield HIT (of edge MISS) | ≥ 90% |
| Segment TTFB p99 (HIT, metro) | < 50ms |
| Origin egress share | < 2% of edge bytes |
| Fill error rate | < 0.01% |
| Prefetch warm_pct @ launch | ≥ 95% |

### A11. Worked numeric example

```text
POP sees 100,000 GET/s for title finale segments
Edge HIT 98% → 2,000 MISS/s
Coalesce factor ~500 → ~4 effective shield GET/s for hot keys
Shield HIT 90% → 0.4 origin GET/s (plus long-tail MISS)
Without coalesce: 2,000 shield/s → 200 origin/s at 90% shield HIT
```

### A12. Ownership

| Concern | Owner |
|---------|-------|
| Open Connect hardware/software | Netflix CDN / Open Connect |
| Origin object store | Media platform |
| Manifest + versioning | Playback / packaging |
| Signing / entitlement | Security + playback API |
| Prefetch orchestration | Content ops + CDN control |
| QoE dashboards | Client + data platform |

### A13. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Edge + shield + coalesce + versioned URLs |
| 10× | OC embeds + prefetch + HIT SLO dashboards |
| 100× | Hierarchical shield + multi-CDN steering |
| 1,000× | Global hot-set tiering + sharded control plane |

### A14. Comparison to naive design

| Naive | Why it fails |
|-------|--------------|
| Origin serves player directly | Bandwidth/QPS impossible |
| Querystring auth in cache key | Zero HIT |
| 60s TTL on all segments | Constant refetch |
| No coalesce on premiere | Self-DDoS origin |
| DNS-only “CDN” | No byte caching |

### A15. On-call cheat sheet

1. Check `edge_hit_ratio` drop by pop — correlate deploy?  
2. Check `origin_egress_gbps` spike — HIT or coalesce regression?  
3. Verify manifest `content_version` rollout not partial.  
4. Cert expiry dashboard — renew if < 14 days.  
5. Steering flapping — disable bad POP manually.  
6. Launch: confirm prefetch `warm_pct`.

### A16. Sample edge access log (sampled)

```text
{
  "ts": "2026-08-06T02:15:01Z",
  "pop_id": "isp-lax-042",
  "method": "GET",
  "path": "/v44/title/t_991/1080p/seg-120.m4s",
  "status": 200,
  "bytes": 2621440,
  "cache": "HIT",
  "ttfb_ms": 8,
  "coalesce_wait_ms": 0
}
```

### A17. Cost worksheet

```text
edge_egress_pb_month ≈ aggregate_tbps × 86400 × 30 / 8 / 1e6
origin_egress_pb_month ≈ edge × (1 - H_e)
commercial_cdn_cost ≈ overflow_pb × price_per_gb
oc_capex ≈ appliances × (nvme_$ + compute_$)

savings_from_1pct_hit = edge_egress × 0.01 × price_per_gb_equiv
```

### A18. Interview rubric

Clarify split QPS; HIT → origin math; versioned URLs over purge; coalesce on tentpoles; progressive 10× / 100× / 1,000×; deal-breaker gallery.

### A19. Migration / rollout notes

Dual-steer canary POPs before fleet-wide cache software; never big-bang cert swap without overlap window; recon warm_pct vs actual HIT post-launch.

### A20. Explicit non-goals

- Replacing player ABR algorithm  
- Building studio encode farm (sibling doc)  
- DRM license issuance  
- Guaranteed zero rebuffer globally  
- Per-viewer watermark embedding at edge (forensic sibling)  

---

*End of document — Netflix system design interview prep.*
