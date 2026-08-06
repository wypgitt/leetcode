# System Design: World-Scale Website

> **Focus areas:** Global edge · Multi-region active-active reads · Single-writer / cell writes · CDN · Cache hierarchy · Deployment · Failure isolation · Personalization · Compliance · Azure Front Door  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split QPS classes (static / API / write), explicit deal-breakers, progressive cellization, SLO-first  
> **Interview theme:** Microsoft — **world-scale web property** (Bing-class portal, Microsoft.com, M365 marketing+app shell, Xbox.com, Learn)

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

Goal: design a **website that serves the world**—low latency on every continent, high availability through regional failures, safe continuous delivery, and clear separation between static content, dynamic APIs, authenticated experiences, and write paths—without pretending one global strongly consistent database powers every click.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Global web delivery + origin platform | Single-page toy blog |
| Scale problem | Latency, fan-out, blast radius, deploy safety | Only “use Kubernetes” |
| Microsoft lens | Front Door, CDN, Azure regions, Entra, sovereignty | Ignore edge |
| Success | p99 UX + error budgets + isolation | Peak QPS vanity |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Site types? | Marketing pages + logged-in app shell + APIs | Split stacks |
| F2 | Auth? | Entra ID / MSA; anonymous browse | Edge + origin auth patterns |
| F3 | Personalization? | Geo, language, light recommendations | Edge decidable vs origin |
| F4 | Content? | CMS + product catalogs + docs | CDN-friendly immutable assets |
| F5 | Search? | Site search / typeahead | Separate search system hook |
| F6 | Writes? | Comments, prefs, carts, form submits | Home-cell writes |
| F7 | SSR vs CSR? | Hybrid: SSR shell + hydrated apps | Origin compute at edge/regions |
| F8 | Media? | Images, video trailers | Object storage + CDN |
| F9 | Experiments? | A/B at edge and origin | Sticky buckets |
| F10 | SEO? | SSR/SSG critical pages | Cache HTML carefully |
| F11 | Compliance? | Cookie consent, regional laws | Edge config + CMP |
| F12 | Admin/CMS? | Publish pipeline with preview | Content workflow ≠ user traffic |

**MVP scope:**

1. Global anycast/Front Door entry; TLS; WAF.  
2. CDN for static assets + cacheable HTML.  
3. Regional origins for SSR/API.  
4. Auth integration (login redirect / tokens).  
5. Config/feature flags; basic personalization (locale/geo).  
6. Write APIs with home routing.  
7. Observability: RUM + origin metrics.  
8. Blue/green or canary deploys with kill switch.

**Out of MVP:** building full Bing index; multiplayer game backend; perfect CRDT collaborative editing; multi-master cart without home.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Edge static TTFB | p50 < 50ms near PoP |
| N2 | SSR HTML | p95 < 300–500ms regional |
| N3 | API read | p99 < 200ms in-region |
| N4 | Availability | 99.99% for browse; writes may be 99.9% |
| N5 | Global coverage | <150ms to edge for most users |
| N6 | Deploy safety | Canary <1%; auto rollback on SLO burn |
| N7 | Blast radius | Region/cell failure ≠ global outage |
| N8 | Security | WAF, DDoS, supply-chain signed artifacts |

### 1.3 Cases

**Happy:** User hits nearest PoP → cached asset/HTML → if miss, regional origin → personalized fragments → ACK. Logged-in API reads from nearby replica; writes to home.

**Edges:**

| Case | Behavior |
|------|----------|
| Origin region down | Fail over to secondary origin; stale cache serve if policy allows |
| Cache stampede | Collapsed forwarding / soft-lock |
| Bad deploy | Canary auto-abort; edge kill switch to last-known-good |
| Thundering login | Auth endpoints isolated; cache JWKS |
| Localized content wrong | hreflang + explicit locale cookie/path |
| Bot scrape | WAF + bot management; protect origin |
| Cookie consent denied | No non-essential tags; functional cookies only |
| Stale personalized HTML | Short TTL or fragment composition |
| Write during home failover | Fence primary; queue or fail clearly |
| DNS/PoP issues | Multi-CDN narrative optional; health probes |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 10M | 100M | 1B | multi-B |
| Peak RPS (all) | 50K | 500K | 5M | 50M |
| Peak **static** RPS | 40K | 400K | 4M | 40M |
| Peak **SSR/API read** | 8K | 80K | 800K | 8M |
| Peak **writes** | 500 | 5K | 50K | 500K |
| PoPs / edge sites | 20 | 50 | 100+ | 150+ |
| Origin regions | 2 | 4 | 8 | 15+ |
| Catalog objects | 1M | 10M | 100M | 1B+ |
| HTML routes | 1K | 10K | 50K | 200K |
| Concurrent A/B flags | 50 | 200 | 1K | 5K |

**Jumps:**

- **10×:** CDN discipline; origin shielding; regional expansion.  
- **100×:** Cell architecture; fragment caches; multi-region active-active reads.  
- **1,000×:** Edge compute composition; hierarchical caches; per-tenant/product isolation; sovereign clouds.

### 1.5 Scope statement

> Design a world-scale website platform: global edge delivery, cacheable content, regional origins, authenticated experiences, safe deploys, and cell-friendly writes—scaling browse traffic through 10× / 100× / 1,000× while keeping failure domains small and compliance explicit.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split (critical)

```text
World-scale sites are NOT one QPS number.
Typical split:
  70–90% static (JS/CSS/img/font/video segments)
  8–25% cacheable HTML / API GETs
  <2–5% authenticated dynamic
  <<1–2% true writes

Design for the split or you overbuild OLTP and underbuild CDN.
```

### 2.2 Bandwidth

```text
Avg page weight 2 MB (aggressive modern); optimized 800 KB
50K RPS × 20% full page ≈ mixed; asset HIT ratio 95%+
Origin egress should be << edge egress
At 5M RPS (100×): edge dominates; origin shielding mandatory
```

### 2.3 Cache math

```text
HIT ratio 95% on assets → origin sees 5% 
If edge 4M asset RPS → origin 200K — still huge → shield + tiered CDN
HTML HIT 70–90% for marketing; near 0 for private pages
```

### 2.4 Storage

```text
Assets: multi-PB at 1000× with video
CMS content: TBs metadata
User prefs: bytes × MAU → careful sharding
Logs/RUM: high cardinality; sample + aggregate
```

### 2.5 Latency budget

```text
User → PoP: 10–40ms
PoP cache HIT: +5–20ms
PoP MISS → shield → origin: +50–150ms
SSR origin compute: +20–100ms
Auth token validate: +1–10ms (local JWKS)
```

### 2.6 Bottlenecks

(1) Origin stampede (2) auth storms (3) bad cache keys (4) deploy regressions (5) single-region writes (6) third-party tags.

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Role | Consistency |
|-------|------|-------------|
| Edge / CDN | Terminate TLS, cache, WAF, bot | Cache semantics |
| Composition | SSR/ESI/fragments | Per-request |
| Read API | Product/content/profile reads | Timeline/eventual OK |
| Write API | Prefs, forms, carts | Strong home |
| Content publish | CMS → builds → CDN purge/put | Workflow |
| Experimentation | Assign buckets | Sticky |
| Identity | Entra/MSA | Token-based |

**Deal-breaker:** one globally mutable DB for every page render.

### 3.2 Components

1. **DNS + Azure Front Door / anycast**  
2. **CDN / POP cache** (Azure CDN / Front Door cache / multi-CDN)  
3. **Origin shield**  
4. **SSR / BFF tier** (AKS / App Service / Azure Container Apps)  
5. **Static origin** (Blob Storage static website / computed assets)  
6. **API gateway**  
7. **Content service / CMS projection**  
8. **Profile/prefs service** (home cell)  
9. **Feature flag service**  
10. **Auth (Entra)**  
11. **Image/media pipeline** (resize, formats)  
12. **Observability** (RUM, synthetic, traces)  
13. **Deploy control plane** (canary, flags, purge)  
14. **WAF / DDoS / bot**  

### 3.3 Cache key design

```text
Asset: path + content-hash filename → immutable, long TTL
HTML public: path + locale + device-class (+ experiment bucket carefully)
HTML private: Cache-Control: private / no-store; fragment cache server-side
API GET: Authorization variance; prefer Authorization-aware or cookie-strip for public
```

**Deal-breaker:** caching personalized HTML under a shared key.

### 3.4 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| SSG vs SSR | SSG for marketing; SSR for dynamic shell | Cost + SEO |
| Edge compute | For geo/locale/A/B lightweight | Avoid heavy DB at edge |
| Multi-region writes | Home cell | Correctness |
| Multi-CDN | Optional at 100×+ | Complexity vs resilience |
| Purge vs versioned URLs | Prefer versioned assets | Purge is slow/error-prone |
| Monolith BFF | Per-product BFFs at scale | Blast radius |

### 3.5 Personalization strategy

1. **Edge-decided:** geo, language, cookie consent, experiment bucket.  
2. **Fragment:** “recommended” island fetched async.  
3. **Origin:** account-specific dashboards.  

Don’t SSR the entire page with 15 dependency calls on the critical path.

### 3.6 Write path

```text
Client → Front Door → Write API → Account home cell → ACK
Async: project to read models / CDN not involved for private data
```

### 3.7 Content publish

```text
Editor → CMS → Build/Validate → Artifact store (hashed)
         → Update content index → CDN warm/put
         → Progressive purge if needed
Preview environments with auth
```

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Users worldwide]
       |
   DNS / Anycast
       |
 Azure Front Door + WAF + Bot
       |
   CDN POP caches ----miss----> Origin Shield
                                   |
                    +--------------+--------------+
                    v              v              v
               Static Blob     SSR/BFF fleet   API Gateway
                    |              |              |
               Content artifacts   Content svc   Profile/Write homes
                                   Catalog      Feature flags
                                   Search hook  Identity (Entra)
```

### 4.2 Request paths

```text
Static HIT:   User -> PoP -> bytes
HTML HIT:     User -> PoP -> HTML
HTML MISS:    User -> PoP -> Shield -> SSR -> caches fragments -> HTML
API READ:     User -> PoP (opt) -> Regional API -> DB replica / cache
API WRITE:    User -> routed to home cell -> primary
```

### 4.3 Failover

```text
Region A origin unhealthy
Front Door health probe fails
Shift traffic to Region B origins
CDN continues serving cacheable content
Writes: fail or redirect to new home if planned failover with fencing
```

### 4.4 Deploy pipeline

```text
CI → signed artifacts → canary slot (1%) → RUM/SLO gate → 10% → 100%
Flag rollback < artifact rollback when possible
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Edge can serve last-known-good static/HTML under origin distress (policy).  
2. Health probes measure **user-truth** (synthetic transactions), not only TCP.  
3. Canary has automated abort on error-budget burn.  
4. Cache keys never mix users for private content.  
5. Write homes fenced on failover.  
6. Third-party JS cannot take down first paint—timeout/async.  
7. Secrets never in frontend bundles.  
8. Purge storms controlled; prefer immutable versioning.  
9. Region loss ≠ global login outage (auth resilience).  
10. Consent mode respected before non-essential beacons.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single cloud region + CDN; simple CMS |
| 10× | Multi-region origins; shield; image CDN; flags |
| 100× | Cells by product/tenant; fragment architecture; read replicas global |
| 1000× | Edge composition; sovereign stacks; multi-CDN; isolation per mega-property |

### 5.3 Maintainability

- Design system + shared web platform pack.  
- Contract tests for cache headers.  
- Content as data; avoid hardcoding.  
- RUM dashboards per route.  
- Dependency budgets (JS KB, third parties).  

### 5.4 Progressive scale deep dive

**1×:** One primary region, CDN in front, Blob for assets, App Service/AKS SSR, SQL/Cosmos for prefs. Focus on correct `Cache-Control` and hashed filenames.

**10×:** Add second region active-active for reads; Front Door routing; origin shield; image transformation service; bot management; synthetic monitoring from multiple geos.

**100×:** Split into **cells** (e.g., Xbox site cell vs Learn docs cell vs corporate). Per-cell release trains. Fragment caching (Edge Side Includes or BFF composition). Global profile directory for write routing. Search and recommendations become separate platforms. Quota third-party tags.

**1000×:** Edge workers for localization/A/B. Hierarchical caches (POP → regional → shield). Per-sovereign deployments (Fairfax/Mooncake-class narrative). Traffic foresight for launches (product keynote). Capacity N+2. Chaos gamedays for region loss. HTTP/3, early hints, signed exchanges optional interview spice—only if asked.

### 5.5 Cache stampede control

- Request collapsing at shield.  
- Soft-serve stale-while-revalidate.  
- Randomized TTL jitter.  
- Pre-warm on publish for top routes.  

### 5.6 Auth at world scale

- Cache JWKS at BFF.  
- Session tokens short-lived; refresh carefully.  
- Isolate `/authorize` endpoints.  
- Avoid origin hops for every static asset (cookies on CDN host discipline).  
- Prefer cookie-less static domain.

### 5.7 SEO & locale

- Deterministic URLs per locale.  
- Avoid cloaking.  
- SSR critical content.  
- Sitemap generation pipelines.  
- Careful with experiment variants vs crawlers.

### 5.8 Security

- WAF rulesets; DDoS Standard/Protection.  
- CSP, nonce, supply-chain pinning.  
- Dependency scanning.  
- Admin CMS on separate network path.  
- Rate limit write APIs & login.  

### 5.9 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Skip CDN “we’ll scale origin” | Melts on launch |
| Cache personalized page publicly | Privacy SEV |
| Global lock DB for all writes | Latency + outages |
| Big-bang world deploy | Instant global SEV |
| Purge-everything as routine | Stampede + errors |
| Third parties on critical path | Random outages |
| One mega-repo deploy without cells | Blast radius |

### 5.10 Operability

Golden signals: edge HIT ratio, origin RPS, SSR p99, 5xx by route, RUM LCP/INP, canary SLO, WAF block rate, auth latency, write success.

Kill switches: disable fragment, disable third-party, force static mode, freeze deploys, shed personalization, region drain.

---

## 6. Wrap-Up

### 6.1 Designed

World-scale web platform with edge/CDN, shields, regional SSR/API origins, careful cache keys, home-cell writes, auth integration, safe canaries, and progressive cellization.

### 6.2 Decisions to defend

1. Split static / read / write QPS  
2. Immutable assets > purge culture  
3. Stale-while-revalidate  
4. Home-cell writes  
5. Canary + RUM abort  
6. Fragment personalization  
7. Cookie-less static domain  
8. Cells at 100×  

### 6.3 Risks

- Cache key bugs  
- Auth storms  
- Launch spikes  
- Third-party JS  
- Cross-region write complexity  
- SEO regressions from client-only renders  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Clarify site type + traffic split |
| 5–15 | Edge/CDN/cache keys |
| 15–25 | Origins, SSR/BFF, auth |
| 25–35 | Writes, multi-region, failover |
| 35–45 | Deploys, 100× cells, deal-breakers |

### 6.5 Closer

> **World-scale website:** edge-first delivery, ruthless cache discipline, regional origins, home-cell writes, canary safety, and cell isolation—so a region or bad deploy cannot take the world offline.

---

## 7. Deeper / Related Interview Questions

### 7.1 Caching

**Q: stale-while-revalidate vs stale-if-error?**  
A: SWR for freshness UX; SIE for resilience—use both thoughtfully.

**Q: How to personalize with CDN?**  
A: Vary on few dimensions or compose fragments; don’t Vary: Cookie blindly.

**Q: Negative caching?**  
A: Cache 404s briefly to protect origin from missing asset storms.

### 7.2 Multi-region

**Q: Active-active vs active-passive?**  
A: Reads AA; writes home/AP. State it clearly.

**Q: Session affinity?**  
A: Prefer JWT stateless; avoid sticky unless needed.

### 7.3 Deploy

**Q: Blue/green vs canary?**  
A: Canary with RUM for world-scale; blue/green for some origins.

**Q: Feature flags vs code deploy?**  
A: Flags for risk isolation; still need artifact rollback.

### 7.4 Performance

**Q: LCP optimization levers?**  
A: Hero image CDN, preload, SSR text, defer third parties, HTTP/2+/3.

**Q: How measure true user latency?**  
A: RUM with geo/device dimensions; synthetics for control.

### 7.5 Security & abuse

**Q: DDoS layers?**  
A: Network + protocol + WAF + app rate limits + cache absorb.

**Q: Scraping?**  
A: Bot management; legal/robots; don’t rely on obscurity.

### 7.6 Data

**Q: Where does CMS live?**  
A: Publish-time projection to edge-friendly store; runtime shouldn’t query heavy CMS DB.

**Q: User prefs storage?**  
A: Home cell KV/SQL; read-through cache with short TTL.

### 7.7 Microsoft-specific

**Q: Why Front Door?**  
A: Global anycast, WAF, routing, certs, health probes—good interview anchor.

**Q: Sovereign clouds?**  
A: Separate deployments; no silent data export; mention at 1000×.

### 7.8 Interview traps

| Trap | Better |
|------|--------|
| “Put site in one huge Kubernetes cluster” | Edge + multi-region |
| “Redis solves world latency” | Physics; need PoPs |
| “Strong consistency globally for HTML” | Unnecessary |
| “Invalidate all caches on publish” | Versioned assets |

### 7.9 Related designs

- Notification system for email/push from site events  
- Search engine for site search  
- Experimentation platform  
- Identity platform  
- Image pipeline  

### 7.10 LLD pivot

Be ready to sketch: cache key builder function; middleware for locale; BFF aggregator with timeouts/budgets; circuit breakers.

### 7.11 Cost

Edge egress is huge—image formats (AVIF/WebP), compression, cache HIT, regionalize origins to cut mid-tier egress.

### 7.12 Accessibility & client diversity

Don’t assume broadband Western desktops; progressive enhancement matters at world scale.

### 7.13 Incident vignette

**Symptom:** global 5xx spike after deploy.  
**Steps:** freeze deploys; revert flag; shift Front Door to previous origin; check canary gates why failed; postmortem on missing RUM abort.

### 7.14 Cookie consent

Gate analytics/ads tags; document functional vs essential; regional law differences (EU).

### 7.15 HTTP cache header cheatsheet

```text
immutable assets: Cache-Control: public, max-age=31536000, immutable
HTML marketing:   public, max-age=60, stale-while-revalidate=600
Private app:      private, no-store
```

---

## 8. Appendices

### 8.1 Route classification matrix

| Route class | Cache | Origin | Auth |
|-------------|-------|--------|------|
| Marketing landing | CDN HTML | SSG | No |
| Docs article | CDN HTML | SSG | No |
| Product detail | CDN + fragments | SSR/BFF | Optional |
| Account home | no-store | SSR/API | Yes |
| Prefs write | no | Write API home | Yes |
| Assets | CDN long TTL | Blob | No |

### 8.2 API checklist

- [ ] Cache headers reviewed per route  
- [ ] Locale/URL strategy  
- [ ] Auth redirect loops prevented  
- [ ] Write home routing  
- [ ] Pagination/cursors  
- [ ] Idempotency on writes  
- [ ] Rate limits  
- [ ] CORS tight  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| PoP | Point of presence / edge site |
| Origin shield | Intermediate cache protecting origin |
| Cell | Isolated deploy + data failure domain |
| RUM | Real user monitoring |
| SWR | Stale-while-revalidate |
| BFF | Backend for frontend |
| Anycast | Single IP, many locations |
| Sovereign cloud | Isolated national/compliance cloud |

### 8.4 Progressive scale checklist

| Scale | Must |
|-------|------|
| 1× | CDN + correct cache headers |
| 10× | Multi-region origins + shield + synthetics |
| 100× | Cells + fragments + write homes |
| 1000× | Edge composition + sovereign + launch capacity |

### 8.5 Failover runbook (sketch)

1. Detect via probes + RUM burn.  
2. Drain region in Front Door.  
3. Confirm cache HIT absorbing.  
4. Writes: promote home with fence or fail soft.  
5. Comms to status page.  
6. Post-incident capacity review.

### 8.6 Canary abort criteria

- Edge 5xx +X%  
- LCP regression > threshold  
- JS error rate +Y%  
- Auth failure +Z%  
- Origin CPU saturation  

### 8.7 Cache key pseudocode

```text
def cache_key(req):
  if is_immutable_asset(req.path): return req.path
  if is_private(req): return None  # do not store shared
  return (req.path, req.locale, req.device_class, experiment_bucket(req))
```

### 8.8 SSR dependency budget

```text
Total SSR budget 250ms
Each dependency: timeout 50–100ms
Fail partial fragments; never block whole page on recommendations
```

### 8.9 Security header baseline

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

### 8.10 Media pipeline

```text
Upload -> virus scan -> transcode/resize -> AVIF/WebP/JPEG ladder
       -> hashed object -> CDN
On-the-fly transform at edge optional with abuse caps
```

### 8.11 Observability dictionary

| Signal | Use |
|--------|-----|
| HIT ratio | Cost + resilience |
| Origin RPS | Capacity |
| SSR p99 | UX |
| RUM LCP | Real UX |
| Canary delta | Deploy safety |
| WAF blocks | Attack awareness |
| Consent rates | Legal + analytics quality |

### 8.12 Deal-breaker gallery (extended)

1. Shared cache for authenticated HTML  
2. No health probes (DNS TTL hope)  
3. Synchronously calling 20 services in SSR  
4. Global mutable session DB in one region only without cache  
5. Unsigned frontend artifacts  
6. Purge-all as publish step  

### 8.13 Interview “say this” (60s)

> I’d split traffic into static, cacheable HTML, dynamic reads, and home-cell writes. Put the world on Front Door/CDN with immutable assets, protect origins with shields and SWR, compose personalization as fragments, and ship via canaries tied to RUM. Scale jumps are about cells and edge composition—not one magical global database.

### 8.14 Cost worksheet

| Lever | Effect |
|-------|--------|
| HIT ratio +1% | Large egress save |
| Image compression | Bandwidth |
| SSG vs SSR | Compute |
| Third-party reduction | Perf + cost |
| Region count | Fixed cost vs latency |

### 8.15 Chaos drills

- Disable origin region  
- Inject SSR latency  
- Poison cache key (test detection)  
- Deploy bad JS to 1%  
- Expire cert (should never—monitor)  
- Flood bots  

### 8.16 Cell topology example

```text
Cell_Corp_Marketing
Cell_Docs_Learn
Cell_Xbox_Storefront
Cell_Identity_Shared (careful coupling)
Each: own release train, dashboards, error budget
```

### 8.17 Write home directory

```text
profile_id -> {cell, primary, replicas, epoch/fence}
On move: dual-read/dual-write window or freeze writes briefly
```

### 8.18 Third-party governance

Allowlist tags; async load; budget KB; kill switch; contractual SLOs for critical vendors.

### 8.19 SEO pipeline

Build sitemaps; monitor index coverage; ensure SSR parity; hreflang validation jobs.

### 8.20 Accessibility checklist (interview-ready)

Keyboard paths; contrast; semantic HTML SSR; don’t rely on client-only content for critical info.

### 8.21 Capacity narrative

At 5M RPS with 85% edge HIT, origin sees 750K RPS. If SSR costs 50ms CPU-equivalent, you need enormous horizontal SSR fleets unless HTML is mostly cached. Hence SSG/SWR emphasis.

### 8.22 Related Microsoft products narrative

Framing examples: Microsoft.com launches, Xbox storefront traffic spikes, Learn docs global read, Teams web app shell—pick one and stay consistent.

### 8.23 Kill switches list

- `force_static_mode`  
- `disable_recommendations`  
- `disable_third_party`  
- `freeze_deploys`  
- `region_drain_<name>`  
- `disable_edge_experiments`  

### 8.24 Oncall first five minutes

1. Edge or origin?  
2. One region or global?  
3. Deploy/flag change?  
4. HIT ratio collapse?  
5. Auth dependency?  
6. Upstream content publish?  

### 8.25 Comparison: SSG / SSR / CSR

| Mode | Pros | Cons |
|------|------|------|
| SSG | Fast, cheap, SEO | Less dynamic |
| SSR | Fresh, SEO | Origin cost |
| CSR | App-like | SEO/TTFB risks |

Hybrid wins world-scale sites.

### 8.26 Header/policy snippets worth saying

- Separate static domain cookie-less  
- `Vary` minimally  
- Compression + Brotli  
- Early hints for critical assets  

### 8.27 Progressive enhancement philosophy

Core content works without niche APIs; progressive apps hydrate—protects resilience and a11y.

### 8.28 Supplemental Q&A

**Q: Do we need multi-CDN day one?**  
A: No—earn complexity at 100× when single CDN PoP issues hurt error budget.

**Q: How to handle product launch spike?**  
A: Pre-warm caches; loadtest; scale SSR; feature flag queue room; static fallback pages.

**Q: GraphQL at edge?**  
A: Careful—cacheability suffers; prefer BFF REST/JSON for public GETs.

**Q: WebSockets for site?**  
A: Separate realtime tier; don’t couple to marketing CDN path.

### 8.29 Topic closer checklist

- [ ] Traffic class split stated  
- [ ] Cache key deal-breaker named  
- [ ] Multi-region model clear  
- [ ] Deploy safety story  
- [ ] 10×/100×/1000× jumps  
- [ ] Azure anchors (Front Door, CDN, Entra)  

### 8.30 One-breath closer

> Edge-first, cache-correct, region-resilient, cell-isolated, canary-safe—world scale is physics plus blast-radius control.

### 8.31 Extra operability addenda

**Rollback ladder:** flag → traffic shift → prior artifact → static emergency site.  
**Status page:** separate infrastructure.  
**Dependency inventory:** identity, CMS, search, recommendations, payments iframes.  
**Load tests:** not only average—launch shapes.  
**Doc:** cache runbook for oncall.

### 8.32 Worked example: localized homepage

```text
URL: /en-us /fr-fr /ja-jp
Edge sets locale from path
SSG pages per locale in Blob/CDN
Fragment: signed-in hello bar via BFF no-store
Experiment bucket cookie with short entropy
Consent gate before analytics fragment
```

### 8.33 Final reminder

Microsoft interviewers often ask you to **draw the request path** and then **break a region**—practice narrating failover without hand-waving “the cloud handles it.”

---

*End of document — World-Scale Website*
