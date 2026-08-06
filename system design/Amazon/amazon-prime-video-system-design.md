# System Design: Amazon Prime Video (+ Homepage)

> **Focus areas:** Catalog & entitlements · Homepage shelves · Personalization · Open play / start stream · Adaptive bitrate (ABR) · CDN / edge · Watch history · Continue Watching · Live/linear (optional) · DRM · Scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split QPS (browse vs play vs bytes), real bandwidth math, explicit deal-breakers  
> **Interview theme:** Amazon SDE III / L6 — streaming product + Amazon homepage assembly at Prime Video scale

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

Goal: design **Prime Video** such that users open the app/site, see a personalized **homepage**, browse/search titles they are entitled to, and **start playback** with low TTFB/TTFF over CDN with DRM—reliably at Amazon event scale (e.g., Thursday Night Football / premieres).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Browse + homepage + play | Full Hollywood production pipeline |
| Homepage | Shelf assembly + ranking | Generic Amazon.com retail home |
| Playback | Manifest + ABR + DRM license | Build a new codec |
| Amazon lens | Entitlements, CX, cost/Gbps, ownership | Only CDN vendor brochure |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Clients? | TV, mobile, web, Fire Stick, consoles | Device capability profiles |
| F2 | Homepage? | Rows/shelves: Continue Watching, Prime, Tops, Personal | Home assembler service |
| F3 | Catalog? | Titles, seasons, episodes, live events | Metadata service + search |
| F4 | Entitlements? | Prime, channels, rentals, buys, freevee ads | Entitlement service |
| F5 | Playback? | Dash/HLS + ABR + DRM (Widevine/PlayReady/FairPlay) | License + packager/CDN |
| F6 | Resume? | Continue watching + exact position | Watch history store |
| F7 | Profiles? | Multiple profiles / kids | Profile-scoped personalization |
| F8 | Search? | Title/person search | Search index |
| F9 | Downloads? | Optional offline | License persistence; defer detail |
| F10 | Live? | Some live sports/events | Low-latency path optional |
| F11 | Ads? | Free tier / some content | Ad decision + SSAI optional |
| F12 | Previews? | Autoplay trailers muted | Lightweight preview CDN |
| F13 | Ratings? | Maturity / kids lock | Filter in home + play |
| F14 | Analytics? | QoE: startup, rebuffer, exit | QoE pipeline |

**MVP functional scope:**

1. Homepage shelf assembly (Continue Watching + curated + personalized).  
2. Title detail + episode lists.  
3. Entitlement check.  
4. Start playback: manifest URL + DRM license.  
5. Watch progress sync.  
6. Search basic.  
7. CDN-backed segments.  
8. QoE logging.

**Out of MVP:**

- Full creator studio tooling  
- Social watch parties (mention only)  
- Building global fiber  
- LLM chat over catalog as core path  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Homepage latency | Snappy | p99 < 200–400 ms API (edge cached parts) |
| N2 | Play start (VOD) | Fast start | TTFF p50 < 1–2s good networks |
| N3 | Rebuffer | Low | < 0.5–1% time rebuffering |
| N4 | Availability | High | 99.99% control plane; playback degrade via CDN |
| N5 | Consistency | Progress eventual OK | Seconds lag across devices |
| N6 | Security | DRM + authz | No naked mezzanine URLs |
| N7 | Cost | $/hour streamed | Cache hit ratio critical |
| N8 | Peak events | Large simultaneous audiences | Prefetch + capacity plans |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Open app → homepage shelves render → tap title → detail → Play → DRM license → ABR playback.  
2. Resume Continue Watching mid-episode on TV after mobile.  
3. Kids profile filters mature shelves.  
4. Search “Jack Ryan” → season 2 → play.  
5. Live event start → join linear manifest.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Not entitled | Show upsell / channel subscribe; don’t start play |
| DRM license fail | Clear error; retry; device cert issues |
| CDN POP miss storm | Origin shield; degrade bitrate ladder tip |
| Homepage personalization down | Fall back curated + Continue Watching |
| Watch history down | Play still works; resume degraded |
| Concurrent streams exceed policy | Enforce device limit |
| Thumbnail/preview stampede | Separate cache tier |
| Region rights differ | Title availability by marketplace |
| Clock skew license expiry | Device renew before expiry |
| Spike premiere | Prefetch manifests/segments at edge |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 50M | — | — | global class |
| DAU | 10M | 100M | — | — |
| Peak concurrent plays | 2M | 20M | 200M | 2B (theoretical extreme) |
| Homepage QPS | 50K | 500K | 5M | 50M |
| Play-start QPS | 10K | 100K | 1M | 10M |
| Search QPS | 5K | 50K | 500K | 5M |
| Avg bitrate | 5 Mbps | 5 | 5 | 5 |
| Catalog titles | 100K | 200K | 500K | 1M+ |
| Edge bandwidth peak | 10 Tbps | 100 Tbps | 1 Ebps-class* | multi-Ebps* |

\*Unit sense-check in §2—interviewers care you don’t invent magic.

**What each jump forces:**

- **10×:** Heavy edge caching of home modules; CDN capacity; partitioned history.  
- **100×:** Cell/marketplace isolation; personalization feature stores; origin shields everywhere.  
- **1,000×:** Hierarchical home assembly; near-static shelves for mega-events; multicast-like live patterns where applicable.

### 1.5 Scope statement

> Design Prime Video **homepage + playback**: entitlements, shelf assembly, catalog/search, DRM/ABR streaming via CDN, and watch history—from tens of thousands of homepage QPS and millions of concurrent plays through progressive 10× / 100× / 1,000× with edge-heavy architecture and clear degradation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 100× | Notes |
|-------|---------------|------|-------|
| Homepage assemble | 50K | 5M | Many cacheable fragments |
| Title metadata | 30K | 3M | CDN/API cache |
| Entitlement check | 20K | 2M | Hot cache per account |
| Play-start (manifest) | 10K | 1M | Spiky at hour boundaries |
| DRM license | 10K | 1M | Correlated with play-start |
| Progress updates | 20K | 2M | Batched / sampled OK |
| Segment bytes | enormous | CDN | Not app-server QPS |

**Critical:** Never size app servers for video bytes. Size them for **control plane**; size CDN for **data plane**.

### 2.2 Bandwidth math

```text
Concurrent plays C = 2,000,000
Avg bitrate B = 5 Mbps
Throughput ≈ C × B = 10,000,000 Mbps = 10,000 Gbps = **10 Tbps**

Unit check: 2e6 × 5e6 bits/s = 1e13 bits/s = 1e13 / 1e12 = 10 Tbps ✓

100× concurrent → ~1,000 Tbps = 1 Pbps order (global CDN federation)
```

### 2.3 Homepage payload

```text
Home JSON 50–150 KB compressed with image URLs (images on CDN)
50K QPS × 100 KB = 5 GB/s control egress → must be edge-cached / regional
Personalization: cache key includes profile_id + viewport + locale
```

### 2.4 Storage

```text
Catalog metadata: 500K titles × 10 KB = 5 GB (small)
Artwork: petabytes on object storage / CDN
Mezzanine + encodes: multi-PB (media supply chain)
Watch history: 50M DAU × 200 B × events → tens of TB/year hot
```

### 2.5 DRM / license

```text
License request ~few KB; p99 < 100–200 ms
Must not become SPOF: regional license clusters + cache short-lived tokens carefully
```

### 2.6 Critical bottlenecks

1. Homepage personalization thundering herd  
2. Play-start spikes at :00  
3. Origin overload on CDN miss  
4. Entitlement storms  
5. Watch history hot accounts  
6. Live event sync starts  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Profile (account_id, profile_id, kids_flag)
Title / Edition / PlaybackID
Entitlement (account, title/channel, window)
Shelf (id, type, items[])
HomePage (profile → ordered shelves)
Manifest (Dash/HLS URL, codecs, keys)
License (DRM)
WatchPosition (profile, playback_id, position_sec, updated_at)
DeviceCapability (hdr, codec, drm system)
```

### 3.2 Control plane vs data plane

| Plane | Responsibilities |
|-------|------------------|
| Control | Home, catalog, entitlement, play auth, DRM license, progress |
| Data | Encoded segments/chunks via CDN |

**Deal-breaker:** streaming video bytes through the homepage microservice.

### 3.3 Homepage assembly

```text
HomeRequest(profile, device, locale)
  → parallel fetch modules:
      ContinueWatching
      PersonalizedRows (recsys features)
      Curated/Editorial
      TopCharts
      BecauseYouWatched
  → filter by entitlement + maturity + availability region
  → rank/order shelves
  → truncate items; return URLs to artwork
```

**Latency tactics:**

- Fragment cache per module (CW TTL short; editorial longer)  
- Stale-while-revalidate  
- Prefetch next shelves on scroll  
- Fallback hierarchy if personalization times out (e.g., 50 ms budget)

### 3.4 Entitlements

```text
IsPlayable(account, title, at=now) ->
  Prime included OR channel OR purchase/rental active OR free ad-tier
```

Cache entitlements with short TTL + invalidation on purchase. **Play-start must revalidate** authoritative enough to prevent widespread theft (balance TTL vs load).

### 3.5 Playback start

```text
Client → PlayAuth(title, device)
  server: entitle OK → select encode package for device
  return: signed manifest URL + license server hint + playback session id
Client → fetch manifest (CDN)
Client → DRM license (license service)
Client → ABR download segments (CDN)
Client → progress beacons → Watch History
```

Signed URLs / cookies expire; anti-hotlinking.

### 3.6 ABR & CDN

- Ladder: e.g., 0.5–15 Mbps rungs  
- Player picks based on bandwidth/buffer  
- CDN: multi-tier, origin shield, midgress savings  
- Prefetch popular titles’ first segments at edge for TTFF  

### 3.7 Personalization

| Signal | Use |
|--------|-----|
| Watch history | CW + BYW |
| Implicit affinity | Genres/actors |
| Explicit thumbs | Re-rank |
| Time/context | Evening vs kids morning |
| Device | Lean-back TV vs mobile |

**Online:** light re-rank of candidates. **Offline:** candidate generation models. Don’t run giant DNN in homepage p99 critical path without strict budget.

### 3.8 Trade-offs

| Topic | Choice | Deal-breaker |
|-------|--------|--------------|
| Home | Modular parallel assembly + fallbacks | Monolith sequential RPC chain |
| Personalization | Budgeted; curated fallback | Hard fail empty home |
| Playback bytes | CDN | App servers |
| Progress | Async eventual | Sync cross-device transaction on every second |
| Entitlement | Cached + critical recheck | Trust client flags |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Devices (TV/Mobile/Web)
        |
        | HTTPS APIs
        v
+------------------+
| Edge / API GW    |
+--------+---------+
         |
         v
+------------------+     +------------------+
| Home Assembler   |---->| Shelf Modules    |
+--------+---------+     | CW / Rec / Edit  |
         |               +--------+---------+
         |                        |
         v                        v
+------------------+     +------------------+
| Catalog / Search |     | Feature / Rec    |
+------------------+     +------------------+
         |
         v
+------------------+
| Entitlements     |
+--------+---------+
         |
         | PlayAuth
         v
+------------------+     +------------------+
| Playback Service |---->| DRM License      |
+--------+---------+     +------------------+
         |
         | signed manifest
         v
+------------------------------------------+
| CDN (segments, manifests, artwork)       |
| Origin Shield → Encode Origin / Object   |
+------------------------------------------+

Watch History ← progress beacons
QoE Lake ← startup/rebuffer/bitrate events
```

### 4.2 Sequence: homepage

```text
Client → Home API
Assembler → parallel: CW (50ms), Rec (60ms), Editorial (cache hit 5ms)
Rec timeout → skip/replace with TopCharts
Filter entitlements (batch)
Return shelves JSON
Client fetches images from CDN
```

### 4.3 Sequence: start play

```text
Play → Entitlement OK → issue playback session
Return manifest URL (CDN) + license endpoint
License OK → first segments → playing
Progress every N seconds → history service
```

### 4.4 Sequence: personalization down

```text
Rec module 503 → Assembler uses last-good personalized cache OR curated only
CW still from history store (or last-good)
Home never empty if editorial cached
```

### 4.5 Live event peak

```text
Preposition: push manifests + init segments to POPs
Play-start: sticky session tokens
Scale license horizontally
QoE dashboards on rebuffer; ladder tip if origins hurt
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **No play without entitlement** (server-side).  
2. **DRM required** for premium content.  
3. **Homepage degrades ≠ blank**.  
4. **Control/data plane separation**.  
5. **Signed playback URLs** expire.  
6. **Kids profile constraints** non-bypassable.  
7. **Region availability** enforced.  
8. **Stream concurrency policy** enforced.  
9. **Watch progress** eventually consistent across devices.  
10. **QoE monitored** with alerts on startup/rebuffer.

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Recsys down | Curated fallback |
| History down | Hide CW / use device local |
| License down | Regional failover; pause new plays |
| CDN POP down | DNS/geo steer |
| Origin overload | Shield + popular pack cache |
| Entitlement store down | Short negative/positive cache carefully; fail closed on play |

### 5.2 Scalability

| Scale | Move |
|-------|------|
| 10× | Edge cache home fragments; CDN commit; history partition by account |
| 100× | Marketplace cells; personalized candidate materialization; origin shields |
| 1,000× | Event mode (static mega-shelves); live-specific pipelines; tiered QoE sampling |

**Cache keys (home):**

```text
home:{marketplace}:{profile}:{device_class}:{locale}:{app_ver}:{module}
```

Personal modules short TTL (30–120s); editorial 5–30 min; with purge on publish.

### 5.3 Maintainability

- Clear ownership: **Home/Discovery**, **Playback/CDN**, **Entitlements/Commerce**, **Media supply chain**, **QoE**.  
- Device capability matrix versioned.  
- Catalog schema evolution with compatibility.  
- Chaos: kill rec module, verify fallback.  
- Cost reviews: cache hit ratio, encode ladder economics.

### 5.4 Continue Watching

```text
Update: best-effort beacon every 10–30s + pause/exit flush
Read: last M titles by updated_at for profile
Merge: server wins with timestamp; device local cache for offline UI
Privacy: per profile isolation
```

### 5.5 Search

- Inverted index on titles/people  
- Availability + entitlement filters at query or post-filter  
- Typeahead optional (separate system)  
- Don’t couple search outage to homepage (independent)

### 5.6 Ads (if in scope)

- Ad decision service for free tier  
- SSAI (server-side ad insertion) vs CSAI  
- Keep play-start SLO; ads failure shouldn’t brick playback of ad-free entitled content  

### 5.7 Security & abuse

- Token binding to account/device  
- Detect credential stuffing → stream limits  
- Watermarking optional for leak tracing  
- Kids PIN  

### 5.8 Key metrics

| Metric | Why |
|--------|-----|
| Home p99 | Browse CX |
| TTFF / startup error | Play CX |
| Rebuffer ratio | QoE |
| DRM error rate | Play blockers |
| CDN hit ratio | Cost/QoE |
| Entitlement deny accuracy | Trust |
| Fallback rate | Personalization health |
| Concurrent streams | Capacity |

---

## 6. Wrap-Up

### 6.1 What we designed

Prime Video **discovery + playback**: modular homepage assembly with personalization fallbacks, entitlements, DRM/ABR streaming over CDN, and watch history—sized as a **control plane + CDN data plane** system under progressive scale.

### 6.2 Key decisions worth defending

1. Split control vs video bytes  
2. Modular home with timeouts/fallbacks  
3. Entitlement server-side at play  
4. CDN + origin shield for segments  
5. Budgeted personalization (not hard dependency)  
6. Eventual progress sync  
7. Explicit ownership across discovery/playback/media  

### 6.3 Risks & follow-ups

- Device fragmentation  
- Live latency  
- Personalization cost vs lift  
- Rights complexity by country  
- Offline downloads  

### 6.4 Closer

> **Prime Video:** fast homepage that always renders, entitled play that starts quickly, CDN for bits, DRM for rights—and degradation paths that keep customers watching when personalization or a POP misbehaves.

---

## 7. Deeper / Related Interview Questions

**Q1. Why can’t homepage servers stream video?**

**A:** Bandwidth math (Tbps) and caching economics. App fleets handle JSON/auth; CDNs handle segments.

**Q2. How do you keep homepage fast with personalization?**

**A:** Parallel modules, strict budgets, caches, stale-while-revalidate, curated fallbacks on timeout.

**Q3. Walk through play start.**

**A:** Entitlement → playback session → signed manifest on CDN → DRM license → ABR segments → progress beacons.

**Q4. DRM systems?**

**A:** Widevine, PlayReady, FairPlay depending on device; license service abstracts; packaging issues multiple keys.

**Q5. Continue Watching across devices?**

**A:** Server watch history keyed by profile; eventual consistency; conflict by latest timestamp; local cache for UX.

**Q6. Peak event strategy?**

**A:** Prefetch at POPs, scale license, simplify home modules, QoE-based ladder tip, capacity war-room automation.

**Q7. Entitlement caching danger?**

**A:** Stolen/long TTL caches cause unauthorized play; use short TTL + signed play tokens with expiry; revoke paths.

**Q8. Personalization vs editorial?**

**A:** Mix: editorial for brand moments; personal for engagement; always filter rights/maturity.

**Q9. Search outage impact?**

**A:** Isolated—home/play continue. Search degrade to trending or cached queries.

**Q10. Kids mode enforcement?**

**A:** Profile flag filters shelves and blocks play of mature titles server-side—not only UI hide.

**Q11. Adaptive bitrate basics?**

**A:** Multi-rung encodes; player switches on bandwidth/buffer; goal continuity over max quality.

**Q12. Origin shield?**

**A:** CDN tier collapses misses so origin sees fewer requests—critical at premiere spikes.

**Q13. How to estimate CDN cost?**

**A:** Concurrent × bitrate × hours × $/GB with cache hit ratio; improve hit ratio before buying origin.

**Q14. Manifest vs segments caching?**

**A:** Manifests shorter TTL (esp. live); VOD segments long TTL immutable by URL version.

**Q15. What if watch history is lossy?**

**A:** Play still works; CW degraded; QoE may lose resume accuracy—buffer locally and retry ingest.

**Q16. Multi-marketplace rights?**

**A:** Availability service by country; home/play filter; separate catalogs logically.

**Q17. Concurrent stream limits?**

**A:** Session registry per account; new play may kick oldest or deny—policy product call.

**Q18. Thumbnails/previews load?**

**A:** Separate CDN path; lower quality; don’t block home JSON on images.

**Q19. Live vs VOD architecture differences?**

**A:** Live: short segments, low latency knobs, DVR windows, sharper peaks; VOD: long-tail cache friendly.

**Q20. Deal-breakers?**

**A:** Video through monolith; personalization hard-dependency blank home; client-only entitlement; no DRM on premium; no fallbacks.

**Q21. How does Fire Stick differ from iOS?**

**A:** Codec/DRM/capability profiles change packaging choice; same control APIs.

**Q22. Catalog updates propagation?**

**A:** Pub/sub invalidation of metadata caches; home module purge for editorial changes.

**Q23. QoE pipeline?**

**A:** Client emits startup_ms, rebuffer_ms, bitrate switches; aggregate by CDN POP/device; alert regressions.

**Q24. Why signed URLs?**

**A:** Prevent hotlink/CDN freeloading; bind to session/expiry.

**Q25. Personalization features store?**

**A:** Offline embeddings / affinity vectors per profile; online fetch < budget; fallback defaults.

**Q26. A/B on homepage?**

**A:** Use experimentation platform for shelf ranking; guardrails: play starts, exit rate—not only clicks.

**Q27. Cold start new profile?**

**A:** Popular + onboarding genres; avoid empty.

**Q28. Audio dubs / subs?**

**A:** Manifest lists renditions; preference from profile; packaging multi-language.

**Q29. 4K/HDR eligibility?**

**A:** Device capability + entitlement tier + bandwidth; don’t offer rung device can’t play.

**Q30. Summarize control plane components.**

**A:** Home assembler, catalog, search, entitlements, playback auth, DRM license, watch history, rec modules.

**Q31. Data plane components?**

**A:** Encoders/packagers, origin storage, shields, CDN POPs, artwork CDN.

**Q32. Failure: license service regional outage?**

**A:** Steer to another region; cache valid licenses until expiry; pause affected devices with clear UX.

**Q33. How to secure keys?**

**A:** Key management service; license servers HSM-backed; never put raw content keys in client binaries.

**Q34. Homepage pagination?**

**A:** First viewport shelves first; fetch below-fold async; reduces TTI.

**Q35. Bot scraping catalog?**

**A:** Rate limits, auth, anomaly; don’t let bots crowd play-start capacity.

**Q36. Episodes lists huge?**

**A:** Paginate seasons; cache per season; don’t inline all into home.

**Q37. Why not GraphQL everything?**

**A:** Fine if budgets/IO disciplined; still need module-level timeouts and caching—GraphQL doesn’t remove fanout risk.

**Q38. Session fixation / token theft?**

**A:** Short-lived playback tokens; device binding; refresh flows; revoke on password change.

**Q39. Cost vs quality ladder?**

**A:** Cap top rung on congested networks; business policy for cellular data modes.

**Q40. Ownership who pages on TTFF regression?**

**A:** Playback/QoE owns TTFF; CDN if hit ratio; media if encode; home if play button unreachable.

**Q41. Manifest personalization?**

**A:** Usually device/account independent media; ads may personalize SSAI manifests carefully.

**Q42. Pre-roll ads delaying start?**

**A:** Measure TTFF including ads; timeout ad calls; hard-geate entitled ad-free paths.

**Q43. How to test homepage fallbacks?**

**A:** Chaos kill rec/CW; assert non-empty editorial; latency SLO.

**Q44. Metadata translation?**

**A:** Locale fields in catalog; home locale key; fallback language chain.

**Q45. Why cells/marketplaces?**

**A:** Rights, latency, blast radius, compliance.

**Q46. Progress update storm?**

**A:** Client batching; server sample; coalesce per (profile, title).

**Q47. Canedge compute assemble home?**

**A:** Yes for cached fragments; personalized assembly often regional; hybrid.

**Q48. Interaction with Amazon retail account?**

**A:** Shared identity; Prime entitlement signal from account/subscription systems.

**Q49. What’s unique vs generic Netflix-style answer?**

**A:** Call out Amazon identity/Prime bundling, marketplace cells, ownership, Freevee/ads options, device ecosystem (Fire TV).

**Q50. 60-second pitch.**

**A:** Modular edge-cached homepage with budgeted personalization; server entitlements; CDN DRM playback; async history; degrade to curated; scale control plane separate from Tbps data plane.

**Q51. Encode ladder storage blowup?**

**A:** Many rungs × titles = PB; use popular-first encode, long-tail on-demand transcode policies.

**Q52. Thumbnail timelines (trick play)?**

**A:** Separate sprite sheets on CDN; generated offline.

**Q53. Geo-blocked travel user?**

**A:** Availability by current region; messaging; VPN abuse detection policy.

**Q54. Homepage SEO for web?**

**A:** SSR/edge for marketing pages; logged-in home still API-driven.

**Q55. Multi-profile privacy?**

**A:** Strict partition of history/recs; lock kids; don’t leak other profile CW.

**Q56. What goes in LLD?**

**A:** Protobuf schemas, cache keys, license RPC, player state machine—keep HLD at modules/SLOs.

**Q57. How do you know personalization helps?**

**A:** A/B on play rate, hours, satisfaction; watch guardrails (diversity, kids safety).

**Q58. Event “mode” for Super Bowl-scale?**

**A:** Feature toggle: simplify shelves, freeze rec, max CDN preposition, license scale-out, dedicated status page.

**Q59. Biggest business trade-off?**

**A:** Personalization compute/$ vs engagement; bitrate quality vs CDN cost; rights complexity vs UX simplicity.

**Q60. Final deal-breakers list?**

**A:** Bytes via app; blank home on rec fail; client entitlement; no DRM; sync progress every second globally; single origin without shield.

---

## 8. Appendices

### Appendix A — API sketch

```text
GET  /v1/home?profile_id&device
GET  /v1/titles/{id}
GET  /v1/search?q=
POST /v1/playback/start {title_id, device}
POST /v1/playback/license (DRM)
POST /v1/progress {playback_id, position}
GET  /v1/continue-watching
```

### Appendix B — Home module budgets

| Module | Timeout | Fallback |
|--------|---------|----------|
| Editorial | 50 ms | last-good |
| Continue Watching | 80 ms | hide row |
| Personalized | 60 ms | top charts |
| Top charts | 50 ms | static |

### Appendix C — Bandwidth table

| Concurrent | Bitrate | Tbps |
|------------|---------|------|
| 2M | 5 Mbps | 10 |
| 20M | 5 Mbps | 100 |
| 200M | 5 Mbps | 1,000 |

### Appendix D — Playback session token claims

```text
account_id, profile_id, title_id, device_id, exp, max_res, drm_systems[]
```

### Appendix E — Interview 45-min checklist

1. Clarify browse vs play vs bytes (5 min)  
2. Homepage assembly (8 min)  
3. Entitlement + play start (8 min)  
4. CDN/ABR/DRM (8 min)  
5. History + scale peaks (6 min)  
6. Failures/fallbacks (5 min)  
7. Close metrics/ownership (5 min)

### Appendix F — Progressive scale cheatsheet

| Scale | Home QPS | Concurrent | Upgrade |
|-------|----------|------------|---------|
| Base | 50K | 2M | Edge fragment cache |
| 10× | 500K | 20M | Shields + history shards |
| 100× | 5M | 200M | Cells + event mode |
| 1,000× | 50M | extreme | Hierarchical static+dynamic |

### Appendix G — QoE event schema

```json
{"session":"...","ttff_ms":1200,"rebuffer_ms":0,"bitrate_kbps":4200,"pop":"IAD","device":"FireTV"}
```

### Appendix H — Degradation matrix

| Dependency | Degrade |
|------------|---------|
| Rec | Curated |
| History | No CW |
| Search | Trending |
| License | Can’t start new plays |
| CDN POP | Steer |

### Appendix I — Ownership map

| Area | Owner |
|------|-------|
| Home/Discovery | PV Discovery |
| Playback/DRM | PV Playback |
| CDN | Video Delivery |
| Entitlements | PV Commerce |
| Encode | Media Pipeline |
| QoE | Playback UX |

### Appendix J — Cache TTL guidance

| Object | TTL |
|--------|-----|
| Editorial shelf | 5–30 min |
| Personalized shelf | 30–120 s |
| Title metadata | minutes–hours |
| VOD segment | days–immutable |
| Live segment | seconds |
| Entitlement | tens of seconds |

### Appendix K — Device capability matrix (sample)

| Device | DRM | HDR | Max |
|--------|-----|-----|-----|
| iOS | FairPlay | Dolby/HDR10 | 4K* |
| Fire TV | Widevine/PlayReady | HDR10 | 4K |
| Web Chrome | Widevine | varies | 1080/4K |

### Appendix L — Common traps

| Trap | Solid answer |
|------|--------------|
| Store videos in MySQL | Object+CDN |
| Personalize synchronously 12 RPCs | Budgets+parallel+fallback |
| Trust client “isPrime” | Server entitle |
| Global lock on progress | Per-profile async |

### Appendix M — Worked TTFF budget

```text
PlayAuth 50–100 ms
Manifest CDN 50–100 ms
License 50–150 ms
Init+first media 300–800 ms
Total ~0.5–1.5 s on good path
```

### Appendix N — Related systems

| System | Link |
|--------|------|
| A/B platform | Home ranking experiments |
| Identity/Prime | Entitlement source |
| CDN platform | Bytes |
| Recsys | Shelves |

### Appendix O — Live event extras

- Shorter GOP/segments  
- Prefetch join  
- DVR from time-shift buffer  
- Commentary language tracks  
- Sudden concurrency cliffs at kickoff  

### Appendix P — Privacy notes

- Profile isolation  
- Kids logging limits  
- Retention on watch history  
- Ads personalization controls  

### Appendix Q — Cost levers

1. CDN hit ratio  
2. Bitrate caps  
3. Encode ladder pruning  
4. QoE-driven not max-quality default  
5. Preview autoplay limits  

### Appendix R — One-page recap

```text
Home: parallel modules + caches + fallbacks
Play: entitle → sign manifest → DRM → CDN ABR
History: async progress
Scale: control plane QPS ≠ Tbps data plane
```

### Appendix S — Sample scorecard (product)

| KPI | Notes |
|-----|-------|
| Daily plays | Engagement |
| Hours streamed | Consumption |
| TTFF | UX |
| % home play | Discovery quality |
| Churn | Business |

### Appendix T — Closing template

> “I’d split control from CDN data plane, assemble the homepage from timed modules with curated fallbacks, enforce entitlements and DRM at play-start, stream via ABR on a shielded CDN, and sync continue-watching asynchronously—optimizing TTFF and rebuffer while keeping Prime Video operable under premiere-scale peaks.”

---

*End of Amazon Prime Video (+ Homepage) system design.*
