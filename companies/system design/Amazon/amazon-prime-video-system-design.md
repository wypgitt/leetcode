# System Design: Amazon Prime Video (App + Personalized Homepage)

> **Focus areas:** Catalog · Personalized homepage rows · Metadata · Playback · CDN/streaming · Recommendations hooks · Entitlements/DRM (high-level) · Multi-device  
> **Style:** End-to-end Amazon product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (Tbps/PB), split QPS classes, explicit deal-breakers, practicality / reliability / efficiency / operational ownership / business trade-offs

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

Goal: **bound Prime Video**—homepage personalization vs playback plane, what “watch” guarantees, and which Amazon constraints (entitlements, devices, global CDN) matter in 45–60 minutes.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Scope? | **Homepage + catalog browse + start playback**; live optional Phase 2 | Split control plane vs media plane |
| F2 | Content types? | SVOD movies/series, rent/buy (TVOD), ads tier optional, live sports later | Entitlement product types |
| F3 | Homepage? | Personalized **rows** (“Continue Watching”, “Because you watched…”, Top 10, etc.) | Row assembly service + recs hooks |
| F4 | Catalog? | Titles, seasons, episodes, collections; search basic | Catalog/metadata service |
| F5 | Metadata? | Artwork, synopses, cast, maturity, locales, trailers | Localized metadata + image CDN |
| F6 | Playback? | Mobile/web/TV/Fire TV; **ABR** streaming | Session + license + CDN segments |
| F7 | DRM? | Yes for premium (Widevine/PlayReady/FairPlay class) | License service; high-level only |
| F8 | Entitlements? | Prime benefit, subscriptions, purchases, rentals, household | Entitlement check before play |
| F9 | Profiles? | Multiple profiles / kids mode | Profile-scoped rows & history |
| F10 | Continue watching? | Cross-device resume position | Playback position store |
| F11 | Downloads? | Offline on mobile Phase 1.5 | Persistent license + downloaded segments |
| F12 | Recommendations? | Personalized rows; you **hook** recs, may not train models in-room | Feature store + ranker API contract |
| F13 | Search? | Basic title search MVP | Search index async from catalog |
| F14 | Live? | Defer or thin hooks | Different ingest/latency path |

**MVP functional scope (lock with interviewer):**

1. **Catalog** of titles/episodes with localized metadata & artwork.  
2. **Personalized homepage**: ordered list of rows; each row = title cards.  
3. **Continue Watching** + basic personalized/topical rows.  
4. **Title detail** page (metadata + play CTA).  
5. **Play session**: entitlement → playback token → manifests/segments via CDN.  
6. **DRM license** high-level integration.  
7. **Resume position** sync across devices.  
8. Multi-device clients (web, mobile, CTV) against same APIs.  
9. Analytics beacons (starts, quartiles, errors)—off critical path.

**Out of MVP (explicitly defer):**

- Full live sports ultra-low-latency  
- Creator UGC upload pipeline (Prime is mostly studio ingest)  
- Building a new CDN from scratch (use Amazon CloudFront-class / multi-CDN)  
- Training deep rec models in the interview (define hooks/SLAs)  
- Social watch parties  
- Perfect global active-active for all entitlement writes  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Homepage latency | Feels instant | p50 < 150ms, p99 < 400ms edge/API (cached) |
| N2 | Time-to-first-frame | Fast start | p50 < 1s, p99 < 3s warm CDN |
| N3 | Rebuffering | Low | <0.5–1% playtime |
| N4 | Availability | Homepage + play critical | 99.9%+ play start; degrade rows before blackout |
| N5 | Personalization freshness | Minutes OK for most rows | Continue Watching seconds–minutes |
| N6 | Consistency | Entitlements strong enough to prevent theft | Home region single-writer entitlements |
| N7 | Global | Multi-region viewers | Edge CDN + regional control planes |
| N8 | Device diversity | TV apps constrained | Device capability matrix |
| N9 | Efficiency | Cost at Tbps egress | Cache hit ratio, encode ladders, row cache |
| N10 | Operability | Launch events (Thursday Night / season drops) | Prefetch, shields, on-call |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Open app → fetch homepage for `profile_id` → render rows → tap title → detail → Play.  
2. Entitlement OK → create playback session → receive signed manifest URLs → ABR play.  
3. DRM license acquired → decrypt segments.  
4. Pause on Fire TV → resume on mobile at same position.  
5. Continue Watching row updates after 30s play beacon.  
6. Non-personalized fallback rows if recs slow.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Recs timeout | Serve cached / popular / editorial fallback rows |
| Entitlement deny | 403 with reason; no license |
| DRM license outage | Fail closed for protected titles; clear trailer OK |
| CDN POP cold miss storm | Origin shield + prefetch for launches |
| Kids profile | Filter maturity; separate history |
| Concurrent streams over household limit | Enforce at session mint |
| Geo-blocked title | Entitlement/geo policy deny |
| Metadata localization missing | Fallback locale chain |
| Offline download expired license | Refresh or block |
| Hot title premiere | Prefetch + shield; control-plane cache |
| Stale Continue Watching | Eventual; last-write-wins per profile+title |
| Device can’t play 4K/HDR/DV | Capability-filtered ladder |
| Ads tier | Insert SSAI markers/path (Phase 1.5) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 50M | 500M | — | global theoretical |
| DAU | 10M | 100M | 1B | — |
| Peak concurrent viewers | 2M | 20M | 200M | 2B (absurd/stress) |
| Homepage QPS (peak) | 50K | 500K | 5M | 50M |
| Play session starts / s | 10K | 100K | 1M | 10M |
| Catalog titles (SKU-like) | 100K | 500K | 2M | 10M |
| Avg rows / homepage | 15 | 15–20 | 20 | 20+ |
| Cards / row | ~20–50 | same | same | same |
| Blended bitrate | 4 Mbps | 4 Mbps | 4–5 Mbps | 5 Mbps |
| Peak CDN egress | ~8 Tbps | ~80 Tbps | ~800 Tbps | multi-Pbps class |
| Resume position writes / s | 50K | 500K | 5M | 50M |
| Recs rank calls / s | 40K | 400K | 4M | 40M |

**What each jump forces:**

- **10×:** Edge-cache homepage fragments; origin shield mandatory; session service scale-out; row personalization async.  
- **100×:** Cellularize members/catalog; multi-CDN; precomputed row materialization; strict recs budgets.  
- **1,000×:** Hierarchical edge assembly; global traffic engineering; title placement policies; extreme prefetch for mega-events.

### 1.5 Etc. (Constraints & Assumptions)

- **Amazon themes:** practical degradation (better a slightly generic homepage than a spinner), cost of egress, device zoo (Fire TV, smart TVs), Prime entitlement coupling.  
- We **buy/use** CDN & object storage; we **build** catalog, homepage, session, entitlement, position, hooks to recs/DRM.  
- Personalization is **wrong-tolerant**; entitlements/playback auth are **not**.  
- Progressive scale from “large streaming service” toward Amazon-global.

**Scope statement:**

> Design Amazon Prime Video focusing on personalized homepage row assembly, catalog/metadata, entitlement-aware playback via CDN ABR (+ DRM hooks), resume across devices, and operational readiness for premiere-scale traffic—from ~2M concurrent through 10× / 100× / 1,000× with explicit degradation and cost trade-offs.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Playback egress (media plane)

```text
Baseline peak concurrent = 2,000,000
Blended ABR ≈ 4 Mbps

Egress = 2e6 × 4 Mbps = 8e6 Mbps = 8,000 Gbps = **8 Tbps**
```

| Scale | Concurrent | @4 Mbps | @5 Mbps |
|-------|------------|---------|---------|
| 1× | 2M | 8 Tbps | 10 Tbps |
| 10× | 20M | 80 Tbps | 100 Tbps |
| 100× | 200M | 800 Tbps | 1 Pbps |
| 1000× | 2B | 8 Pbps | 10 Pbps |

**Unit check:** 2e6 × 4e6 bit/s = 8e12 bit/s = **8 Tbps**. Not “8 GB/s” as the headline unit—8 Tbps ≈ 1 TB/s order.

CDN hit ratio target **95–99%+** for popular titles:

```text
At 10× (80 Tbps) with 98% HIT:
Origin draw ≈ 80 × 0.02 = 1.6 Tbps → still needs shield + multi-origin
```

**Deal-breaker:** App servers proxying video bytes.

### 2.2 Homepage / control plane QPS

```text
DAU 10M; assume peak concurrent app users ~1M opening/refreshing home
If each refreshes home ~once / 5 min at peak cluster:
  1e6 / 300 ≈ 3.3K QPS average-ish… too low for peak bursts

Launch / app-open storms: 50K–100K QPS homepage plausible at baseline big events
Use table: **50K homepage QPS baseline peak**
Each homepage: 15 rows × ~30 ids ≈ 450 title refs + artwork URLs
Payload ~50–150 KB compressed JSON → 
50K × 100 KB = 5 GB/s egress from API/edge caches (cacheable!)
```

### 2.3 Row assembly compute

```text
50K homepages/s × 15 rows = 750K row resolutions/s
If each row hits ranker naively → recs melt.

Must: precompute / cache personalized rows; only few rows live-ranked
Assume 3 live rows × 50K = 150K rank calls/s baseline peak
```

At **100×**: 5M homepage QPS → impossible without **edge assembly + heavy materialization**.

### 2.4 Catalog & metadata storage

```text
Title metadata doc ~5–20 KB localized × locales
100K titles × 10 locales × 10 KB ≈ 10 GB metadata (small)

Artwork: many sizes; 100K titles × 20 images × 200 KB ≈ 400 TB images (order)
Trailers/previews separate

Packaged ABR library:
Avg 1.5 hours / title equiv × 25 Mbps ladder sum × … 
Use ~8–15 GB packaged / title-hour; series amplify episode count
100K title-entries (episodes heavy) → **PB-scale** object storage easily
```

Interview line: **metadata is tiny; media + artwork dominate**.

### 2.5 Resume position

```text
Position record ~100 B
Writes: heartbeat every 10–30s while playing
2M concurrent / 15s ≈ ~130K writes/s baseline
10× → ~1.3M writes/s → sharded KV / streams + coalescing
```

### 2.6 Session / license QPS

```text
Play starts 10K/s; each → 1 session + 1–N license requests
License renewals periodic for long plays
Control plane must be horizontally scalable & cached where safe
```

### 2.7 Critical bottlenecks

1. **Homepage personalization fanout** without cache/materialization  
2. **Origin melt** on premiere without shield/prefetch  
3. **Entitlement/session SPOF** at play start  
4. **Resume write storm**  
5. **Recs latency** blocking first paint  
6. **Device-specific packaging** explosion (cost)

---

## 3. High-Level Design

### 3.1 Planes (keep separate)

| Plane | Responsibility | Scale driver |
|-------|----------------|--------------|
| **Catalog / metadata** | Titles, localization, artwork refs | Editors + ingest |
| **Discovery** | Homepage rows, search, detail | App opens |
| **Identity / entitlement** | Prime, purchases, household | Play starts |
| **Playback control** | Session, tokens, licenses | Play starts |
| **Media delivery** | CDN segments/manifests | Concurrent watch time |
| **Personalization** | Ranker / candidates | Discovery QPS |
| **Telemetry** | QoE, progress | Beacons |

### 3.2 Homepage product model

```text
Homepage = ordered [Row]
Row = { row_id, row_type, title, cards: [TitleRef], refresh_ttl, personalization_level }
TitleRef = { title_id, offer_badge?, progress?, image_variant }
```

**Row types (MVP):**

| Type | Source | Freshness | Failure fallback |
|------|--------|-----------|------------------|
| Continue Watching | Position + history | High | Hide row |
| Because You Watched X | Recs | Medium | Similar/popular |
| Top 10 / Trending | Aggregate | Medium | Editorial |
| Editorial / Collection | CMS | Low | Skip |
| New Releases | Catalog query | Medium | Cached list |
| Rent/Buy rail | Catalog + merchandising | Medium | Hide |

### 3.3 Homepage assembly strategies

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Fully online fanout | Fresh | p99 disasters | Never at peak |
| **Hybrid** (chosen) | Balance | Complexity | Default |
| Fully precomputed page | Fast | Stale / storage | Mega-scale cold start |

**Chosen hybrid:**

1. **Materialize** many rows offline / nearline per profile segment or per profile.  
2. **Online** stitch 1–3 fresh rows (Continue Watching).  
3. **Edge cache** anonymous/popular page fragments.  
4. **Budget** recs ≤ 30–50ms; else fallback.

### 3.4 Catalog & metadata

```text
Ingest (studios/partners) → Validate → Catalog Store → 
  → Localization pipeline
  → Artwork derivatives
  → Search indexer
  → Availability windows (rights)
```

**Rights/availability** are first-class: a title can exist in catalog but not be playable in a country or date window.

### 3.5 Entitlements (high-level)

```text
Play request → Entitlement Service
  inputs: customer_id, household, profile, title_id, geo, device
  outputs: ALLOW { products[], quality_cap, concurrency_token } | DENY
```

Sources: Prime membership, channel subs, TVOD purchase/rental, ads tier, bundled offers.

**Deal-breaker:** Checking entitlements only in the client.

### 3.6 Playback & CDN

```text
Client → Playback Session API (entitled)
      ← session_id, manifest URL (signed), DRM config, telemetry endpoints
Client → CDN (CloudFront-class / multi-CDN) for HLS/DASH
Client → License Service (DRM) with session auth
```

- **ABR ladder** packaged CMAF; device picks rung.  
- **Immutable versioned** segment URLs.  
- **Origin shield** + prefetch for premieres.  
- **Signed cookies/URLs** short-lived, bound to session/geo/device policy.

### 3.7 DRM (high-level only)

```text
Packager encrypts (CENC/CBCS) → key hierarchy in DRM system
Client: license challenge → License Service validates session/entitlement → keys
```

Interview depth: **where** it sits, fail-closed behavior, license QPS, not crypto math.

### 3.8 Recommendations hooks

```text
Candidate generation (collab / similarities / editorial) → 
Features (watch history, affinity) → Ranker → Row IDs
Homepage Assembly consumes Ranker API with timeout + fallback
```

Contracts matter more than model architecture:

| Contract | Example |
|----------|---------|
| Latency SLO | p99 < 40ms |
| Idempotent | same context → stable-ish |
| Fallback | popular-by-geo |
| Explanation | optional reason codes |
| Filtering | apply entitlement/maturity **after** or inside with policy |

**Business trade-off:** showing an unentitled title as “upsell” vs hiding—product policy.

### 3.9 Multi-device

| Concern | Approach |
|---------|----------|
| Capability | Device reports HDCP, codec, HDR, DRM security level |
| UI density | Rows/cards counts differ TV vs mobile |
| Input | D-pad focus vs touch—but same APIs |
| Offline | Download manager + persistent license |
| Concurrent streams | Household policy at session service |
| Clock / position | Server-authoritative position |

### 3.10 Trade-off tables

| Concern | Choice | Deal-breaker |
|---------|--------|--------------|
| Homepage | Hybrid assemble + fallback | Recs on critical path without timeout |
| Media path | CDN only | Bytes through monolith |
| Entitlement | Server-side at session | Client-only gates |
| Personalization | Eventual | Blocking first paint indefinitely |
| Segment URLs | Versioned immutable | In-place overwrite |
| Multi-region | AA read discovery; SW entitlements home | Multi-writer entitlements without conflict story |
| Cost | Cache + thinner ladders for mobile | Unbounded 4K everywhere |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Fire TV / Mobile / Web / Living Room]
              |
              v
        Edge / API Gateway
              |
     +--------+---------+----------------+
     |                  |                |
     v                  v                v
Homepage API      Catalog/Detail    Playback Session API
     |                  |                |
     +--> Row Assembly  |                +--> Entitlement
     |       |          |                +--> DRM License
     |       +--> Recs  |                +--> Device policy
     |       +--> CW    |                |
     |       +--> CMS   v                v
     |            Metadata DB      Signed manifest policy
     v                  |                |
Cached fragments        |                v
                        |         CDN Edges ----MISS----> Shield --> Origin
                        |
                   Search Index
                        |
                   Position Store <--- beacons/telemetry
```

### 4.2 Homepage sequence

```text
Client GET /home?profile=P
  → AuthN
  → Assembly:
      (1) ContinueWatching(P) local/fast store
      (2) Fetch materialized rails for P (cache)
      (3) Optional live rank 1–2 rows budget 40ms
      (4) Entitlement-aware badges (batch)
      (5) Localization + image URL templates
  → Response rows JSON (cache-control personalized: private, short TTL)
Fallback path if assembly partial: return 200 with degraded rows + flag
```

### 4.3 Play sequence

```text
POST /playback/session {title_id, device_caps}
  → Entitlement ALLOW?
  → Concurrent stream check
  → Create session; bind quality_cap
  → Return manifests + DRM challenge endpoint + heartbeat URL
GET manifest (CDN)
GET segments (CDN)
POST license (DRM) with session token
Heartbeat progress → Position Store
```

### 4.4 Premiere / hot launch

```text
T-48h: package complete; rights active window set
T-12h: prefetch top rungs to major POPs / multi-CDN warm
T-1h: materialize “New Episode” rails; scale session fleet
T-0: watch spike; shield coalesces; homepage cache mostly editorial+CW
Monitor: origin Gbps, license errors, session p99, rebuffer
```

### 4.5 Multi-region

```text
Discovery APIs: active-active regional
Catalog read replicas global
Entitlements + purchases: home region single-writer
Position: home or CRDT/LWW per profile with regional caches
Media: global CDN; regional origins for locality
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **No playback session without entitlement ALLOW** (server-side).  
2. **No DRM license without valid session.**  
3. **Immutable media bytes** per versioned URL.  
4. **Homepage always returns something** (degraded OK)—avoid hard 5xx when recs fail.  
5. **Kids mode filters** enforced server-side.  
6. **Concurrency limits** enforced at session mint/renew.  
7. **Position writes** do not block playback.  
8. **Rights windows** respected (geo/time).

**Failure playbook**

| Failure | Response |
|---------|----------|
| Recs down | Cached / popular / editorial rails |
| Catalog partial | Stale-while-revalidate metadata |
| Entitlement store down | Fail closed on play; homepage browse may continue with uncertainty badges off |
| DRM outage | Protected play fails; communicate; trailers optional |
| CDN POP loss | GSLB / multi-CDN failover |
| Origin loss | Shield + secondary origin; cached titles survive |
| Position store down | Play continues; resume temporarily device-local |
| Bad metadata push | Version rollback; pin catalog version |

**Degradation ladder (Amazon practicality):**

```text
1. Full personalized home
2. Drop live rank rows → materialized only
3. Drop personalization → geo popular + editorial
4. App shell + Continue Watching only
5. Browse-only mode if play control plane sick (rare messaging)
Never: infinite spinner because ranker timed out
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Regional APIs; Redis homepage cache; CloudFront; session fleet; PG/Dynamo catalog |
| 10× | Fragment caches; origin shield; precomputed rails; sharded position; multi-AZ DRM |
| 100× | Member cells; title cells; multi-CDN; nearline materialization per segment; edge stitch |
| 1000× | Hierarchical edge; predictive prefetch; traffic engineering; extreme cell isolation |

**Homepage caching taxonomy**

| Layer | Key | TTL | Notes |
|-------|-----|-----|-------|
| Edge CDN | anonymous / tokenized fragments | 10–60s | Careful with personalization |
| Assembly cache | `profile_id` or `segment_id` | 30–300s | Private |
| Row cache | `row_id+locale` | varies | Editorial long |
| Title metadata | `title_id+locale` | minutes–hours | Invalidate on edit |
| Negative entitlement | short | seconds | Anti-fraud careful |

**Personalization scalability trick:** cluster users into **segments** for bulky rows; keep true per-user only for Continue Watching + top few.

### 5.3 Maintainability

- Device capability matrix as data, not hardcoded ifs everywhere  
- Catalog schema versioning; backward-compatible metadata  
- Contract tests: homepage schema, playback session, license  
- QoE dashboards (startup, rebuffer, fatal errors) by device  
- Game days: kill recs, kill DRM, blackhole origin, flood premiere  
- Clear ownership: Discovery vs Playback vs Media Supply Chain  
- Cost reviews: egress, encode, DRM transactions  

### 5.4 Progressive scale deep dive

**1× (~2M concurrent, 50K home QPS)**

- Homepage API + Redis  
- Catalog Dynamo/Aurora + CloudFront images  
- Session service + entitlement  
- Single CDN + origin shield  
- Recs RPC with 40ms timeout  
- Position in Dynamo (partition `profile_id`)

**10×**

- Materialized personalization store  
- Fragmented homepage (CW separate)  
- Multi-CDN for events  
- License service autoscale + cache  
- Beacon pipeline via streams  
- Prefetch tooling for premieres  

**100×**

- Cells for customers & catalog  
- Edge assembly of cached fragments  
- Nearline row compute continuous  
- Strict priority queues for session vs browse  
- Regional origins + placement policies  
- Ads/SSAI path isolated  

**1000×**

- Global traffic director  
- Hierarchical caches  
- Pre-position media by predicted demand  
- Minimal online personalization at open  
- Entitlement snapshots at edge for known products (carefully signed)

### 5.5 Catalog & metadata deep dive

**Entities:** Show, Season, Episode, Movie, Collection, Person, Offer, Availability.

**Localization chain:** `user_locale → country_default → en-US`.

**Artwork:** store master; generate renditions; image CDN with path templates (`/art/{title}/{kind}/{w}.jpg`).

**Availability index:** query “playable in US now for Prime” efficiently—denormalized playability records.

**Ingest idempotency:** partner package IDs; versioned publishes; never mutate published media in place.

### 5.6 Personalized rows deep dive

**Continue Watching algorithm (simple, interview-solid):**

```text
Select titles with position in (0.02, 0.95) of duration
Sort by last_watched_at desc
Filter by profile maturity + still entitled / upsell policy
Limit 20–50
```

**Because You Watched:**

```text
seed = recent completes
candidates = similarity(seed) ∪ collab(profile)
rank with watch/affinity features
filter watched / disliked / unavailable
```

**Assembly pseudocode:**

```text
rows = []
rows += continue_watching(P)            # mandatory attempt
rows += fetch_materialized(P, limit=12) # cache
if budget_left: rows += live_rank(P, k=2)
rows = interleave_editorial(rows, CMS)
rows = dedupe_titles(rows)
return rows
```

### 5.7 Playback / CDN deep dive

- Segment duration 2–6s; CMAF dual HLS/DASH  
- Ladder: 360p→4K selectively; HDR/DV separate  
- Audio: stereo + atmos variants as separate  
- Captions: sidecars WebVTT/TTML  
- Thumbnails/sprites for scrubbing  
- Prefetch: top 2–3 rungs for premiere  
- Token: short TTL; refresh via session heartbeat  
- QoE: client beacons → rebuffer alerts per title/CDN  

**Origin protection:** shield, request coalescing, cache-friendly keys, bot/token abuse limits.

### 5.8 Entitlements & DRM deep dive (high-level)

**Entitlement evaluation order:** geo deny → title window → product ownership → quality caps → concurrency.

**Household:** sharing policy; device limits; detection hooks (without turning interview into fraud deep-dive).

**DRM:** license bound to session + device security level; HDCP for 4K; renewals; revoke on entitlement loss.

**TVOD rental expiry:** time-based entitlement row with TTL; session checks each start/renew.

### 5.9 Multi-device deep dive

| Device | Constraints | Design impact |
|--------|-------------|----------------|
| Mobile | Battery, networks, downloads | Lower default rung; offline package |
| Web | Browser MSE/EME variance | Capability probe |
| Fire TV / CTV | Memory, UI rows, remote | Smaller page payloads; TV layout |
| Console | DRM flavors | Alternate license path |

**Payload efficiency:** TV homepage should not download mobile-sized JSON+images; use device class in API (`device_family=ctv`).

### 5.10 Recommendations integration (operational)

| Topic | Practice |
|-------|----------|
| Timeouts | Hard budget; hedged fallback |
| Shadow traffic | Test new rankers safely |
| Bias / business rules | Pin editorial for launches |
| Feedback | Implicit (watch) / explicit (not interested) |
| Cold start | Popular + editorial |
| Entitlement filter | Don’t recommend unplayable unless upsell |

### 5.11 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Personalized homepage fully online fanout | Meltdown at peak |
| Video through app servers | Impossible cost/latency |
| Client-only entitlement | Piracy / broken business |
| Mutable segment URLs | Cache corruption |
| Recs without fallback | Blank home |
| Single region origin | Global rebuffer | 
| Position on critical play path sync write | Startup latency |
| One giant catalog DB for all writes | Launch lock contention |
| Ignoring device caps | Playback failures / support cost |
| No prefetch on premiere | Origin death |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Homepage | Hybrid materialize + short online CW/rank with fallback |
| Media | CDN ABR + shield + versioned objects |
| Security | Server entitlements + DRM licenses |
| Scale path | Cache → materialize → cells → edge stitch |
| Recs | Hook with budget; not blocking |
| Multi-device | Capability matrix + device-class payloads |
| Multi-region | AA discovery; SW entitlement home |
| Ops | Premiere runbooks; QoE + origin metrics |

### 6.2 Risks

1. Personalization cost vs latency  
2. Premiere origin/CDN misses  
3. DRM/license brownouts  
4. Resume write amplification  
5. Rights complexity bugs (geo)  
6. Device fragmentation  
7. Entitlement home-region failover pain  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: home + play; defer live |
| 5–12 | HLD planes; catalog vs CDN |
| 12–22 | Homepage rows + recs hooks + fallback |
| 22–32 | Playback session, entitlement, DRM, CDN |
| 32–40 | Multi-device, position, premiere ops |
| 40–45 | 10×/100×/1000× + trade-offs |

### 6.4 One-paragraph closer

> “Prime Video splits discovery from media delivery. The homepage hybrid-assembles a few fresh rows with materialized personalized rails and always degrades gracefully. Playback mints an entitlement-checked session, then streams ABR from CDN with DRM licenses—never proxying bytes through app servers. Resume and recs are eventually consistent hooks; entitlements are strongly gated. We scale with caches, cells, shields, and premiere prefetch, optimizing for fast start, low rebuffer, and cost-efficient egress.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & scope

**Q: Homepage only or whole Prime Video?**  
A: Clarify; usually home + play path. Don’t boil the ocean into live + ads + downloads unless asked.

**Q: How is this different from YouTube?**  
A: Rights-heavy catalog, entitlements/DRM, lean-back rows, Amazon account/Prime coupling, less UGC.

**Q: Ads-supported tier?**  
A: SSAI or client ad pods; separate path; don’t block SVOD design—mention isolation.

**Q: Why rows not a single ranked list?**  
A: UX explorable; mixed objectives (CW, trending, editorial); independent refresh/failure.

### 7.2 Homepage & personalization

**Q: What if ranker p99 is 200ms?**  
A: Timeout ~40ms; fallback; fix ranker offline; never block forever.

**Q: How personal is “personalized”?**  
A: CW truly personal; many rails segment-level; efficiency trade-off.

**Q: Dedupe titles across rows?**  
A: Yes lightly; keep CW exceptions; avoid identical first page.

**Q: Editorial vs algo conflict on premiere?**  
A: Pin editorial row; business rules beat model.

**Q: Cache personalized pages at CDN?**  
A: Risky; use short private cache or fragment caching with signed cookies; anonymous pages OK.

**Q: How fast must Continue Watching update?**  
A: Seconds–minutes; eventual OK; optimize read-your-writes after play stop.

**Q: Kids profile leakage?**  
A: Server-side maturity filters on assembly and catalog; separate history.

**Q: A/B testing rows?**  
A: Experiment framework assigns treatment; assemble accordingly; metric QoE + engagement.

### 7.3 Catalog & metadata

**Q: Source of truth for title?**  
A: Catalog service; search/recs are projections.

**Q: How do rights windows work?**  
A: Availability records with geo/time/product; playability index.

**Q: Metadata update propagation?**  
A: Versioned docs; cache invalidate; async search reindex.

**Q: Huge episode catalogs (soaps)?**  
A: Paginate; don’t put 5K episodes in homepage cards; lazy season fetch.

**Q: Artwork localization?**  
A: Per-locale art; fallback chain; image CDN.

### 7.4 Playback & CDN

**Q: HLS vs DASH?**  
A: Device-driven; CMAF common segments preferred.

**Q: Why origin shield?**  
A: Collapse thundering herd MISSes; protect object store.

**Q: Signed URL vs cookie?**  
A: Both fine; cookies nicer for manifests+segments; short TTL; bind to IP/session carefully (mobile IP changes!).

**Q: Mobile IP change breaks signatures?**  
A: Prefer session-bound tokens not strict IP bind; or wide CDN auth policies.

**Q: Hot launch prefetch cost?**  
A: Trade egress/storage at edge vs origin risk; prefetch top rungs only.

**Q: Multi-CDN?**  
A: Capacity + ISP diversity; QoE-based steering; complexity in logs/tokens.

**Q: Seeking?**  
A: Segment aligned; sprite thumbs for UI.

**Q: Live sports?**  
A: Different ingest/packaging/latency; don’t pretend VOD design covers it.

### 7.5 Entitlements & DRM

**Q: Where enforce 4K cap?**  
A: Entitlement + device security level + license policy + ladder filtering.

**Q: Concurrent stream limit race?**  
A: Atomic session registry per household; heartbeats; sticky enforcement.

**Q: Stolen manifest URL?**  
A: Short TTL signatures; license still required for DRM titles; watermarking advanced.

**Q: DRM license outage strategy?**  
A: Fail closed; status page; trailers/clear content if any; scale license horizontally.

**Q: Rental expires mid-play?**  
A: Policy: allow finish session window vs cut off; state choice; usually grace.

**Q: Household sharing abuse?**  
A: Product/policy + device checks; outside MVP deep dive.

### 7.6 Recommendations hooks

**Q: Do I design the ML model?**  
A: Usually no; design candidate→rank→filter→assemble contracts and fallbacks.

**Q: Offline vs online features?**  
A: Mostly offline aggregates; online CW/recent; feature store read in ranker.

**Q: Feedback loop delay?**  
A: Beacons → hours for heavy models; minutes for CW; nearline for trending.

**Q: Filter entitled titles before or after rank?**  
A: Cheap filters early; final entitlement pass before display/play; upsell exceptions explicit.

### 7.7 Multi-device & clients

**Q: One API for all devices?**  
A: Same resources; device-class params for density/caps; avoid wholly separate backends if possible.

**Q: Offline downloads?**  
A: Download encrypted segments + persistent license with renewal; storage limits; entitlement revoke.

**Q: Low-memory CTV?**  
A: Smaller images; fewer rows prefetch; aggressive GC-friendly pagination.

**Q: Clock skew on licenses?**  
A: Server times; client skew tolerance windows.

### 7.8 Scale & cells

**Q: How to cell Prime Video?**  
A: Customer/profile cells for position/home materialization; catalog cells by title-id; keep play session in customer cell.

**Q: Cross-cell title popularity?**  
A: Global trending aggregate pipeline; not per-cell only.

**Q: 1000× homepage QPS?**  
A: Edge fragment assembly; mostly cached; tiny personalization stub.

### 7.9 Reliability & ops

**Q: What do you page on?**  
A: Play start success, license error rate, origin Gbps, rebuffer spike, homepage 5xx—not recs alone.

**Q: Chaos test plan?**  
A: Kill recs, DRM, origin, one CDN, entitlement replica; verify degradation.

**Q: Thursday premiere checklist?**  
A: Prefetch, scale session/license, pin editorial, freeze risky deploys, watch QoE.

**Q: Cost efficiency levers?**  
A: Hit ratio, ladder caps, segment size, materialize vs online, image sizes, codec efficiency (AV1 long-term).

### 7.10 Amazon leadership-principle flavored

**Q: Customer Obsession vs cost?**  
A: Protect TTFF/rebuffer; degrade personalization first; don’t steal entitlement checks to save money.

**Q: Ownership?**  
A: Clear SEV runbooks for playback vs discovery; don’t finger-point CDN without metrics.

**Q: Dive Deep?**  
A: Break QoE by device/CDN/title; find whether control or media plane.

**Q: Bias for Action on outage?**  
A: Flip to editorial homepage; shed noncritical; protect play path.

### 7.11 Extra rapid-fire

**Q: Why not GraphQL everything?**  
A: Fine if budgets/caching clear; not magic.  
**Q: SSR homepage?**  
A: Optional for web; CTV apps native lists.  
**Q: Search ranking?**  
A: Separate; catalog text + popularity; rights filter.  
**Q: Trailers DRM?**  
A: Often lighter/clear; product choice.  
**Q: Watermarking?**  
A: Forensic for leaks; advanced topic.  
**Q: Audio description?**  
A: Separate tracks in manifest.  
**Q: Multi-language audio?**  
A: Rendition groups.  
**Q: Previews on hover?**  
A: Short clip CDN objects; don’t use full ladder.  
**Q: “Top 10” consistency?**  
A: Materialized aggregate; eventual.  
**Q: Personalization privacy?**  
A: Profile isolation; retention policies.  
**Q: Cold start new subscriber?**  
A: Popular + onboarding taste picker.  
**Q: Manifest update mid-season?**  
A: New version path; sessions stick or refresh.  
**Q: Token refresh?**  
A: Heartbeat renews signed access.  
**Q: IPv6 / HTTP3?**  
A: CDN features; clients vary.  
**Q: Logging PII?**  
A: Minimize; session ids not payloads.  
**Q: Exactly-once beacons?**  
A: At-least-once; aggregate idempotently.  
**Q: Why PB media vs GB metadata?**  
A: Arithmetic reality—plan ops/cost accordingly.  
**Q: Fail open homepage?**  
A: Yes for discovery; fail closed for play auth.  
**Q: What is your first diagram box?**  
A: Separate CDN media plane from API plane.

---

## 8. Appendices

### Appendix A — API sketches

```text
GET /v1/home?profile_id&device_family&locale
→ { rows: [{ id, type, title, cards: [{ title_id, progress?, badges[] }] }], degraded?: bool }

GET /v1/titles/{id}?locale
→ metadata, offers, seasons summary

POST /v1/playback/sessions
{ title_id, profile_id, device: { family, drm, hdcp, codecs[] } }
→ { session_id, manifests: { hls, dash }, drm: { license_url }, heartbeat_url, expires_at }

POST /v1/playback/sessions/{id}/heartbeat
{ position_ms, bitrate, cdn_id, events[] }

GET /v1/continue-watching?profile_id
```

### Appendix B — Data model sketch

```text
Title{ title_id, kind, default_locale, maturity, genres[] }
LocalizedMeta{ title_id, locale, name, synopsis, art_refs[] }
Availability{ title_id, country, product, start, end }
Offer{ offer_id, title_id, type: PRIME|RENT|BUY|CHANNEL, price? }
Entitlement{ customer_id, offer_ref, state, expires_at }
Profile{ profile_id, customer_id, kids_mode, locale }
Position{ profile_id, title_id, position_ms, updated_at }
PlaybackSession{ session_id, customer_id, title_id, caps, expires_at }
RowMaterialization{ profile_or_segment, row_id, title_ids[], built_at }
```

### Appendix C — Homepage latency budget

```text
Total p99 assembly = 400ms (API)
  auth           10ms
  CW fetch       20ms
  materialized   30ms
  live rank      40ms (hard timeout)
  entitlement batch badges 30ms
  pack JSON      10ms
  margin/queue   rest
Edge cache hits skip most of the above.
```

### Appendix D — Playback start budget

```text
Session API p99 = 150ms (excl. DRM UI)
CDN manifest = 50–100ms warm
First segments = 200–500ms
License = 100–300ms
TTFF target < 1–3s combined on good network
```

### Appendix E — Progressive scale one-pager

| Scale | Concurrent | Homepage peak | Must-have |
|-------|------------|---------------|-----------|
| 1× | 2M | 50K QPS | CDN+shield, recs timeout, session entitlement |
| 10× | 20M | 500K | Materialized rails, multi-CDN, prefetch |
| 100× | 200M | 5M | Cells, edge fragments, nearline compute |
| 1000× | 2B | 50M | Hierarchical edge, predictive placement |

### Appendix F — Premiere runbook (short)

1. Confirm packaging/rights  
2. Prefetch top rungs  
3. Pin editorial rows  
4. Scale session + license  
5. Watch origin Gbps & 403/5xx  
6. Disable risky personalization experiments  
7. Comms channel with CDN/media supply chain  
8. Rollback pointers ready  

### Appendix G — Degradation matrix

| Dependency down | Browse | Play |
|-----------------|--------|------|
| Recs | Fallback rails | OK |
| Position | Hide CW | OK |
| Catalog read | Stale cache | May fail detail |
| Entitlement | Limited badges | Fail closed |
| DRM | Trailers only | Fail closed protected |
| CDN | Broken watch | Broken watch |
| Origin | Cached titles OK | New/cold titles fail |

### Appendix H — Cheat sheet

| Area | One-liner |
|------|-----------|
| Planes | Discovery ≠ media bytes |
| Home | Hybrid + always fallback |
| Play | Entitlement → session → CDN + DRM |
| Scale | Cache → materialize → cell → edge |
| Amazon | Practical degrade; cost-aware egress |
| Deal-breaker | Recs without timeout; bytes via API |

### Appendix I — Sample 90s opener

> “I’d design Prime Video as two planes: discovery and media. Discovery serves a personalized homepage via hybrid row assembly—Continue Watching live, other rails materialized—with hard timeouts and editorial fallback. Catalog holds metadata and rights; entitlements gate a playback session that returns signed manifests for CDN ABR and a DRM license path. Resume positions sync asynchronously across devices. For premieres we prefetch and origin-shield. At 10× we materialize more; at 100× we cell and stitch at the edge. Personalization can degrade; entitlements cannot.”

### Appendix J — Comparison: Prime Video vs generic “Netflix design”

| Topic | Emphasize at Amazon |
|-------|---------------------|
| Entitlements | Prime bundling + Amazon account |
| Devices | Fire TV / living-room prominence |
| Business | Upsell rent/buy rails |
| Ops | Efficiency of egress; ownership across orgs |
| Scope control | Practical MVP vs boiling ocean |

### Appendix K — Arithmetic quick reference

```text
Egress Tbps ≈ concurrent × bitrate_Mbps / 1e6
2e6 × 4 / 1e6 = 8 Tbps

Origin ≈ egress × (1 - hit_ratio)
80 Tbps × 0.02 = 1.6 Tbps

Homepage bandwidth ≈ QPS × response_KB
50K × 100KB = 5 GB/s  (cache!)
```

### Appendix L — Glossary

| Term | Meaning |
|------|---------|
| ABR | Adaptive bitrate streaming |
| CMAF | Common media format chunks |
| SSAI | Server-side ad insertion |
| TTFF | Time to first frame |
| SW home | Single-writer home region/cell |
| Materialization | Precomputed personalized rails |
| Origin shield | Intermediate cache coalescing MISSes |
| QoE | Quality of experience metrics |

---

*End of prep doc — Amazon Prime Video / Personalized Homepage. Practice with a timer; lead with plane separation, fallbacks, and real Tbps math.*
