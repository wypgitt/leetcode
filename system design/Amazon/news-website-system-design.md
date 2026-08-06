# System Design: News Website (Publishing + Read Scale)

> **Focus areas:** CMS/publishing · Article SoT · CDN · Breaking-news spikes · Homepage assembly · Personalization · Comments · Search · Paywall/subscriptions · Takedown/corrections · Cells
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Origin protection under Slashdot/HN spikes; fast corrections/takedowns; homepage composition; read-heavy economics
> **Interview theme:** Amazon SDE III / L6 — **news website** at Amazon operational bar (ownership, trust, cost, peak)

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

Goal: design a **news website / digital publisher**: editors publish articles & media, readers consume via homepage/sections/article pages at huge read scale (including breaking-news spikes), with search, comments (optional), personalization (optional), and subscription/paywall hooks—plus corrections and takedowns.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Publishing + global read delivery | Social network feed |
| Write path | Relatively low QPS CMS | Twitter firehose |
| Read path | CDN-heavy, spiky | Tiny intranet blog |
| Amazon lens | Peak readiness, trust (corrections), frugality | Pure editorial CMS UI polish |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Content types? | Articles, galleries, live blogs, video | Content model + templates |
| F2 | CMS? | Draft → review → publish → update | Workflow + versions |
| F3 | Homepage? | Curated modules + automated rails | Composition service |
| F4 | Sections? | World, Biz, Tech, Sports… | Taxonomy + feeds |
| F5 | Breaking news? | Fast publish + push alerts | Cache purge, spike plan |
| F6 | Personalization? | Optional Phase 1.5 | Edge + privacy |
| F7 | Comments? | Optional; moderated | Abuse isolation |
| F8 | Search? | Keyword + time | Index nearline |
| F9 | Paywall? | Metered / hard paywall optional | Auth + entitlement |
| F10 | Corrections? | Edit with note; unpublish | Versioning + purge |
| F11 | SEO/AMP/apps? | Yes typically | Multi-channel render |
| F12 | Ads? | Ad slots; not full ad exchange design | Placement hooks |

**MVP scope:**

1. CMS publish/update/unpublish with versions.  
2. Article pages + section listings + homepage composition.  
3. Media via CDN.  
4. Global CDN caching with purge on publish/update.  
5. Breaking-news spike mode (origin shield, cache TTLs).  
6. Search ingest.  
7. Basic comments **or** explicitly out—lock with interviewer.  
8. Corrections/takedown path with purge SLO.  
9. Optional simple paywall entitlement check.

**Out of MVP:** full DSP/ad auction, perfect ML homepage, entire newsletter ESP deep dive, print workflow.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Article page p99 (CDN hit) | < 100–200ms edge |
| N2 | Publish to visible | Seconds incl. purge |
| N3 | Takedown/correction purge | Tight SLO (e.g. < 1–5 min global) |
| N4 | Origin protection | Survive 100× spike via cache |
| N5 | Availability | Reads 99.99% class with static degrade |
| N6 | Durability | Published content durable; versions retained per policy |
| N7 | SEO freshness | Sitemaps/index updates |
| N8 | Cost | CDN egress dominated; minimize origin |

### 1.3 Cases

**Happy:** editor publishes → CDN warm → readers hit homepage → article → related.

**Edges:** election night spike; wrong article published; legal takedown; live blog updates every minute; paywall bypass; comment spam; personalization leak across users via shared cache; video livestream; multi-region editor desks; stale AMP cache; headline A/B.

| Case | Behavior |
|------|----------|
| Breaking spike | Cache almost everything public; shield origin; shed personalization/comments |
| Wrong publish | Unpublish + purge + correction note |
| Live blog | Short TTL or ESI fragments; careful purge |
| Paywall | Cache public shell; personalize entitlement at edge/app carefully |
| Stale after edit | Surrogate keys / purge by article id |
| Comment viral | Isolate; don't kill article path |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| MAU readers | 5M | 50M | 500M | — |
| Peak page views/s | 5K | 50K | 500K | 5M |
| Articles published/day | 500 | 5K | 50K | — |
| Editors concurrent | 50 | 200 | 1K | — |
| Media assets | 1M | 10M | 100M | — |
| Search QPS peak | 200 | 2K | 20K | — |
| Push alerts/day | 1M | 10M | 100M | — |
| Comment writes/s peak | 50 | 500 | 5K | — |

**Jumps:** 10× CDN+shield; 100× multi-POP + composition edge + paywall at scale; 1,000× global mega-events, multi-brand cells, advanced personalization isolation.

### 1.5 Scope repeat-back

> News site: CMS versions as SoT, CDN-first read path with purge/takedown SLOs, homepage/section composition, spike-ready origin protection, optional comments/paywall/personalization degraded under load—Amazon ownership for trust corrections and peak.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Read vs write asymmetry

```text
Publishes: hundreds–thousands/day (tiny QPS)
Reads: thousands–millions QPS at events
Design for CDN hit ratio >> 90–99% on article pages
```

### 2.2 Spike math

```text
Baseline peak 5K pages/s → 100× = 500K/s
If origin must serve 10% = 50K/s → likely melt
Need shield + high hit ratio + request collapsing
```

### 2.3 Cache keys

```text
Risk: Authorization header / cookie variance fragments cache
Public content: cache keyed by URL (+ device class), ignore junk cookies
Personalized: separate fragment / client fetch
```

### 2.4 Storage

```text
Article body versions: MBs/day trivial vs media
Media/CDN egress: dominant cost during spikes
```

### 2.5 Homepage assembly

```text
Homepage = many modules; cache whole page briefly OR
compose from cached fragments (ESI/edge includes)
Breaking module short TTL; deep modules longer
```

### 2.6 Bottlenecks

(1) Origin on cache miss stampedes (2) purge storms (3) live blog update frequency (4) personalized cache fragmentation (5) comments (6) video.

### 2.7 Cost / frugality

CDN egress and video. Image/video ladders; don't disable cache to "make personalization easy."

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| CMS / Content SoT | Drafts, versions, publish state | Strong writes |
| Render / Template | HTML/JSON views | Derived from SoT |
| CDN / Edge | Cache & purge | Eventual with SLO |
| Composition | Home/section modules | Cached fragments |
| Search | Index | Nearline |
| Comments | UGC | Isolated |
| Entitlement | Paywall | Strong enough for access |
| Alerts | Push/email | Best-effort queues |
| Observability/Peak | Spike controls | Ops |

**Deal-breaker:** DB as the primary article page origin at scale without CDN strategy.

### 3.2 Components

1. **CMS API / Editorial UI**  
2. **Content Store** (versions, metadata, body)  
3. **Media Library** (S3 + CDN)  
4. **Publish Pipeline** (validate → snapshot → invalidate)  
5. **Renderer** (SSR/JSON for apps)  
6. **CDN + Origin Shield**  
7. **Homepage Composer**  
8. **Search Indexer**  
9. **Comments Service** (optional)  
10. **Paywall/Entitlement** (optional)  
11. **Push/Alert Service**  
12. **Moderation/Takedown**  
13. **Config / Feature flags / Spike mode**  

### 3.3 APIs (sketch)

```text
PUT  /cms/v1/articles/{id}/draft
POST /cms/v1/articles/{id}/publish
POST /cms/v1/articles/{id}/unpublish
GET  /v1/articles/{id}          # public JSON
GET  /v1/home
GET  /v1/sections/{slug}
GET  /v1/search?q=
POST /v1/articles/{id}/comments # if in scope
GET  /v1/entitlements/me
```

### 3.4 Content state machine

```text
DRAFT → IN_REVIEW → SCHEDULED → PUBLISHED ⇄ UPDATED
PUBLISHED → UNPUBLISHED / TAKEN_DOWN
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| SSR vs app JSON | Both via renderer | SEO + apps |
| Cache TTL | Long + purge | Spike survival |
| Personalization | Fragments not full page | Cache hit ratio |
| Comments | Separate cluster | Isolation |
| Live blog | Partial TTL | Freshness |
| Multi-region CMS | Single writer desk or CRDT carefully | Conflict avoidance |

---

## 4. Architecture Diagram

```text
Editors → CMS API → Content Store (versions)
                 \→ Media Library → CDN
                         |
                    Publish Pipeline
                         |
            +------------+-------------+
            v            v             v
        Renderer     Search Ingest   Alert Queue
            v
        Origin Shield ←── CDN Edge POPs ←── Readers
            ^
     Homepage Composer (fragment cache)

Comments/Paywall services on side paths (not blocking CDN article HTML when possible)
```

### 4.1 Publish sequence

```text
1. Editor publishes version N
2. Persist immutable snapshot
3. Render warm critical templates (optional)
4. Purge/surrogate-key invalidate article + modules referencing it
5. Update search; send alerts if breaking flag
```

### 4.2 Read sequence (article)

```text
Reader → CDN HIT → serve
MISS → Origin Shield → Renderer → Content Store → populate cache
```

### 4.3 Takedown sequence

```text
Unpublish state → purge CDN (all variants) → remove search → disable alerts →
verify probes in major POPs → incident log
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. PUBLISHED snapshot durable and addressable by version.  
2. Unpublish/takedown eventually invisible on CDN within SLO (probed).  
3. Corrections create new version; audit trail retained.  
4. Public cache must not store private personalized bodies.  
5. Spike mode never disables takedown purge.  
6. Comments/paywall failure does not 500 article content (degrade).  
7. Idempotent publish requests.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | CMS + SSR + CloudFront/Fastly + PG |
| 10× | Origin shield; surrogate keys; image CDN |
| 100× | Multi-POP; fragment composition; search fleet; spike runbooks |
| 1000× | Multi-brand cells; edge compute; mega-event war rooms |

### 5.3 Maintainability

- Template versioning  
- Canary rendering  
- Purge dry-run tools  
- Chaos: POP failure, origin kill, publish flood  
- Editorial preview environments  

### 5.4 Progressive scale

**1×:** single region origin; CDN; simple home.  
**10×:** shield; automated purge; media ladders.  
**100×:** fragment edge; paywall scale; comments isolation; peak mode.  
**1000×:** global desks with clear write affinity; brand cells; advanced personalization sandboxes.

### 5.5 Cache & purge deep dive

- Surrogate keys: `article:123`, `section:tech`, `home`  
- Soft purge / stale-while-revalidate for resilience  
- Purge storm control: batch invalidations  
- Variant matrix: language, device—keep bounded  

### 5.6 Homepage composition

- Curated slots from CMS  
- Automated "latest in section" rails from indexes  
- Cache fragments independently  
- Breaking banner short TTL  

### 5.7 Paywall without killing cache

- Cache full public article for non-metered sites OR  
- Cache teaser + client/edge entitlement fetch for body  
- Never put `Set-Cookie` unique on globally cached objects carelessly  

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| No CDN / low TTLs always | Spike outage |
| Cache personalized pages publicly | Privacy/paywall leak |
| Takedown without purge verify | Legal/trust SEV |
| Comments in article origin monolith | Coupled outage |
| Homepage single uncached SQL join | Home melt |
| Infinite live-blog purge each second globally without strategy | CDN API melt |

---

## 6. Wrap-Up

### 6.1 Designed

CMS versioned SoT, CDN-first reads, composition, purge/takedown SLOs, spike mode, optional comments/paywall/search—Amazon peak + trust bar.

### 6.2 Decisions to defend

1. Content snapshots SoT  
2. CDN + shield + high hit ratio  
3. Surrogate-key purge  
4. Fragment personalization  
5. Isolate UGC  
6. Spike degrade order  
7. Correction/version audit  
8. Probe-based takedown verify  

### 6.3 Risks

Purge lag; cache leaks; live blog cost; editor conflicts; video egress; SEO stale.

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Read-heavy news vs social |
| 5–15 | CMS versions + publish |
| 15–28 | CDN/spike/purge |
| 28–38 | Home composition + optional paywall/comments |
| 38–45 | Takedown, scale, ownership |

### 6.5 Closer

> **News website**: versioned publish SoT, CDN-first spike survival, fast purge for trust, composed homepage, isolated UGC/paywall—progressive global scale with clear ownership.

---

## 7. Deeper / Related Interview Questions

### 7.1 Publishing

**Q: Scheduled publish?**  
A: Worker triggers at time; still goes through same snapshot+purge pipeline.

**Q: Concurrent editors?**  
A: Pessimistic lock or OT on draft; publish serializes on article id.

### 7.2 CDN

**Q: Stale-while-revalidate?**  
A: Serve stale on origin errors; revalidate async—great for spikes; careful with takedowns (force hard purge).

**Q: Who collapses thundering herd?**  
A: Shield + request coalescing.

### 7.3 Personalization

**Q: "Recommended for you" on home?**  
A: Edge fragment or client-side rail fed by recommendations service; don't fragment entire page cache by user id.

### 7.4 Comments

**Q: Realtime comments?**  
A: Optional websocket side channel; article HTML still static/CDN.

**Q: Moderation?**  
A: Async classifiers + queues; shadowban; fail-closed on toxic for kids sections.

### 7.5 Search

**Q: Index lag?**  
A: Seconds–minutes OK; publish path not blocked.

### 7.6 Interview traps

**Q: One giant WordPress MySQL for all readers?**  
A: Classic failure under spike.  
**Q: Personalize by disabling CDN?**  
A: Deal-breaker.  
**Q: Soft-delete only in DB leaving CDN forever?**  
A: Trust/legal failure.

### 7.7 Metrics

| Metric | Why |
|--------|-----|
|cdn_hit_ratio | Spike readiness |
| origin_qps | Protection |
| publish_to_visible_s | Editorial UX |
| purge_complete_s | Trust |
| article_p99 | Reader UX |
| home_p99 | Reader UX |
| takedown_probe_fail | Legal/trust |
| egress_$ | Frugality |

### 7.8 Ownership

Takedown miss → Content Platform + SRE peak. Origin melt → Web Platform. Wrong cache personalization → Web+Privacy. CMS cannot publish → Editorial Eng.

### 7.9 Progressive drill

10× shield; 100× fragments+peak mode; 1000× cells/multi-brand mega-events.

### 7.10 Live blog

Append-only updates; fragment TTL 5–30s; SSE/websocket optional for open articles; list pages longer TTL.

---

## 8. Appendices

### 8.1 Schema sketches

```text
articles(article_id, slug, state, primary_section, published_at)
article_versions(article_id, version, body, headline, authors[], created_by, ts)
media_assets(asset_id, type, urls, rights)
home_modules(module_id, type, config, sort)
section_rails(section_id, article_ids[], updated_at)
publish_events(event_id, article_id, version, type, ts)
comments(comment_id, article_id, user_id, text, state, ts)  -- optional
entitlements(user_id, product, expires_at)  -- optional
```

### 8.2 API checklist

- [ ] Draft/publish/unpublish  
- [ ] Article get  
- [ ] Home/section  
- [ ] Search  
- [ ] Purge trigger  
- [ ] Preview  
- [ ] Comments optional  
- [ ] Entitlement optional  

### 8.3 Oncall checklist

- [ ] CDN hit ratio  
- [ ] Origin QPS / errors  
- [ ] Purge backlog  
- [ ] Publish failures  
- [ ] Takedown probes  
- [ ] Spike mode flag  
- [ ] Comments isolation  
- [ ] Video egress alarms  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Surrogate key | Logical cache tag for purge |
| Origin shield | Mid-tier cache before origin |
| SWR | Stale-while-revalidate |
| Snapshot | Immutable published version |
| Composition | Building home from modules |
| Spike mode | Degrade + cache aggressiveness |

### 8.5 Deal-breaker one-liners

- Origin DB per page view  
- Personalized full-page CDN keys per user  
- Takedown without CDN purge  
- Comments coupled to article origin  

### 8.6 Ownership map

| Surface | Owner |
|---------|-------|
| CMS/Content | Publishing Platform |
| CDN/Web | Web Platform / SRE |
| Composer | Homepage Eng |
| Search | Search |
| Comments | UGC |
| Paywall | Subscriptions |
| Alerts | Growth/Notifications |

### 8.7 Capacity sketch

| Scale | Sketch |
|-------|--------|
| 1× | CMS+PG+SSR+CDN |
| 10× | Shield+purge automation |
| 100× | Edge fragments+peak runbooks |
| 1000× | Brand cells+edge compute |

### 8.8 Failure injection

1. Kill origin — SWR/stale serve public pages.  
2. Publish wrong article — unpublish+purge+probe.  
3. Purge API down — emergency TTL shorten / contact CDN.  
4. Comments down — hide module.  
5. Entitlement down — policy: fail open meter vs fail closed premium (product lock).  

### 8.9 Spike mode checklist

- [ ] Disable heavy personalization  
- [ ] Disable noncritical comments realtime  
- [ ] Extend TTLs on evergreen  
- [ ] Ensure shield capacity  
- [ ] Prefetch/warm top stories  
- [ ] Freeze risky deploys  
- [ ] War room roster  

### 8.10 SEO notes

Canonical URLs; sitemap updater; structured data; careful soft-404 on unpublish.

### 8.11 Interview closer checklist

- [ ] Read/write asymmetry stated  
- [ ] CDN+shield math  
- [ ] Purge/takedown SLO  
- [ ] Homepage fragments  
- [ ] Spike degrade  
- [ ] Optional paywall cache-safe  
- [ ] Ownership  
- [ ] 10×/100×/1000×  

### 8.12 Related

Newsletter system, app backends, video streaming live events, ads placements, recommendations, archive/paywalled corpus.

### 8.13 Sample events

```text
ARTICLE_PUBLISHED, ARTICLE_UPDATED, ARTICLE_UNPUBLISHED,
CDN_PURGE_REQUESTED, CDN_PURGE_VERIFIED, HOME_RECOMPOSED,
SEARCH_UPSERT, ALERT_SENT, COMMENT_CREATED, SPIKE_MODE_ON
```

### 8.14 Multi-brand / cells

Each brand site = cell with own CDN config & content store tenancy; shared auth/subscription optional.

### 8.15 Security

CMS SSO/MFA; preview auth; XSS in embeds; SSRF in media import; admin audit; supply chain for embeds.

### 8.16 Cost narrative

Egress + video minutes. Frugality: cache hit ratio is a first-class SLO alongside latency.

### 8.17 LP hooks

Customer Obsession = corrections/takedowns; Dive Deep = cache leak; Deliver Results = election night; Frugality = hit ratio; Ownership = purge miss SEV.

### 8.18 QoS degrade order

1. Personalization rails  
2. Comments realtime  
3. Noncritical tracking  
4. Longer TTLs / more stale  
5. Keep publish, purge, core article/home longest  

### 8.19 AMP / third-party caches

Additional purge fans to Google AMP cache etc. Include in takedown runbook.

### 8.20 Archive & URLs

Stable slugs; redirects on change; archive paywall rules; cold storage for old bodies OK if metadata hot.

---

## Deep Technical Notes — News Website

### Surrogate key design

Tag every cached object with article ids and module ids touched; publish updates purge precise sets.

### Request coalescing

Concurrent MISS for same URL → single origin fetch; others wait—critical at spike start before cache fill.

### Preview vs prod

Preview site no public CDN; signed URLs; watermark optional.

### Image processor

On upload: sizes/webp/avif; never transform unbounded at edge without cache.

### Editorial conflict

`If-Match` version on draft save; publish uses latest approved snapshot id.

### Legal hold

Takedown may unpublish publicly but retain legal archive in restricted store—separate from CDN.

---

## Worked Capacity Narrative — News Website

Writes are tiny; reads are enormous and spiky. If your design centers on CMS microservices and ignores CDN hit ratio and origin shield, you will fail the scale portion. Lead with asymmetry.

## Customer-Trust Paragraph — News Website

Incorrect headlines and lingering taken-down articles are trust and legal events. Purge verification probes are not optional polish—they are the product.

## Progressive Scale Recap — News Website

- **10×:** CDN + shield + purge automation  
- **100×:** fragments + peak mode + isolation  
- **1,000×:** cells/brands + edge + mega-event ops  

## Supplemental Depth Pack — News Website

### S1. Versioned content SoT

Immutable published snapshots; CMS workflow.
**Invariant:** ACK publish ⇒ durable version.
**Metric:** publish_fail, version_gaps.
**Ownership:** Publishing Platform.

### S2. CDN-first reads

High TTLs + purge; origin shield; coalescing.
**Invariant:** Spike traffic mostly served from edge.
**Metric:**cdn_hit_ratio, origin_qps.
**Ownership:** Web Platform.

### S3. Takedown purge SLO

Unpublish + multi-POP purge + probes (+ AMP).
**Invariant:** Content gone within SLO.
**Metric:** purge_complete_s, probe_fail.
**Ownership:** Web + Publishing joint SEV.

### S4. Homepage fragments

Compose cached modules; short TTL breaking.
**Invariant:** Home does not require giant uncached SQL.
**Metric:** home_p99, fragment_hit_ratio.
**Ownership:** Homepage Eng.

### S5. Personalization isolation

User-specific rails out of band; don't fragment global article cache.
**Invariant:** No cross-user content leak via shared cache.
**Metric:** cache_privacy_probes.
**Ownership:** Web + Privacy.

### S6. Comments isolation

Separate service; degrade hide.
**Invariant:** Comment outage ≠ article outage.
**Metric:** article_success_when_comments_down.
**Ownership:** UGC.

### S7. Paywall cache-safe

Entitlement side path; teaser caching strategy explicit.
**Invariant:** Paid body not in public cache.
**Metric:** paywall_leak_probes.
**Ownership:** Subscriptions + Web.

### S8. Spike mode

Flags to shed noncritical; warm top URLs; deploy freeze.
**Invariant:** Takedown still works in spike mode.
**Metric:** spike_origin_qps, purge_success.
**Ownership:** SRE + Web.

## Scenario Runbooks — News Website

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|-----------|
| Origin melt | Spike mode; extend TTL; scale shield | Possible stale | Capacity |
| Wrong article live | Unpublish; purge; correction | Trust | Editorial process |
| Takedown lag | Emergency purge; POP probes | Legal/trust | Automation |
| Home slow | Serve last good home fragment | Stale modules | Composer |
| Paywall leak | Disable bad cache path | Billing/trust | Patch |
| Comments spam | Rate limit; freeze thread | UX | Moderation |
| Live blog stampede | Fragment TTL tune; coalesce | Latency | Design |
| Search lag | Label UI; scale indexers | Search stale | Lag SLO |

## Rapid-Fire Q&A — News Website

**RQ1. Why CDN-first?**  
**A:** Read/write asymmetry and spikes make origin-per-hit impossible.

**RQ2. Test CDN readiness?**  
**A:** Load tests with warm/cold; chaos origin kill.

**RQ3. 100× without CDN strategy?**  
**A:** Outage on first big story.

**RQ4. Why snapshots?**  
**A:** Audit, rollback, consistent render.

**RQ5. Test publish?**  
**A:** Version fixtures; canary templates.

**RQ6. Regression?**  
**A:** Lost edits / inconsistent pages.

**RQ7. Why purge probes?**  
**A:** CDN APIs can partially fail; trust requires verify.

**RQ8. Test takedown?**  
**A:** Synthetic articles across POPs.

**RQ9. Regression?**  
**A:** Legal/trust SEV.

**RQ10. Why fragments on home?**  
**A:** Different TTLs; reduce origin work.

**RQ11. Test home?**  
**A:** Module kill tests; p99.

**RQ12. Regression?**  
**A:** Homepage coupled outage.

**RQ13. Why isolate comments?**  
**A:** UGC volatility vs publishing SLA.

**RQ14. Test isolation?**  
**A:** Kill comments; articles OK.

**RQ15. Regression?**  
**A:** Coupled 500s on big stories.

**RQ16. Why paywall side path?**  
**A:** Preserve public cache economics & prevent leaks.

**RQ17. Test paywall?**  
**A:** Leak probes; entitlement fail modes.

**RQ18. Regression?**  
**A:** Revenue/trust incidents.

**RQ19. Why spike mode?**  
**A:** Predictable degrade beats random melt.

**RQ20. Test spike mode?**  
**A:** Game days before elections/sports.

**RQ21. Regression?**  
**A:** Ad-hoc panic changes.

**RQ22. Why SWR careful with takedown?**  
**A:** Stale serve conflicts with legal removal—hard purge path.

**RQ23. Test SWR vs takedown?**  
**A:** Explicit force-bypass flags in runbook.

**RQ24. Regression?**  
**A:** "Deleted" content still served.

## Narrative Walkthrough — News Website

### Beat 1
Editor publishes snapshot → purge tags → CDN. Tradeoff: TTL length vs purge dependency.

### Beat 2
Reader article HIT at edge. Tradeoff: variant explosion vs hit ratio.

### Beat 3
Homepage composed from fragments. Tradeoff: curation freshness vs cache.

### Beat 4
Breaking spike → spike mode → shield. Tradeoff: personalization off vs availability.

### Beat 5
Correction/unpublish → purge+probe. Tradeoff: speed vs global consistency bounds.

### Beat 6
Optional comments/paywall side paths. Tradeoff: features vs isolation.

### Beat 7
10×/100×/1000× ops evolution. Tradeoff: edge complexity.

### Beat 8
Deal-breakers: origin-heavy; personalized full-page cache; purge-less takedown. Economics: egress/hit ratio.

## Pre-Onsite Checklist — News Website

- [ ] Asymmetry narrative
- [ ] CDN+shield+coalesce
- [ ] Surrogate purge
- [ ] Takedown probes
- [ ] Home fragments
- [ ] Spike mode
- [ ] Paywall cache-safe story
- [ ] Comments isolation
- [ ] Metrics + owners
- [ ] Progressive scale
- [ ] Live blog strategy
- [ ] AMP/third-party purge
- [ ] SDM trust-first pitch
- [ ] Election-night game day
- [ ] Kill switches named

### Extra drill

Whiteboard the takedown sequence including CDN, AMP, search, apps, and verification probes.

### Extra drill

Explain in 60s why `Cache-Control: no-store` on all pages "to be safe" is an availability anti-pattern for news.

---

*End of document — News Website (Amazon Interview Style) (SDE III)*

## Extra Interview Drills — News Website

### Extra Interview Drills — News Website — item 1

**Prompt:** 60s drill #1: breaking-news spike handling for this subsystem.

**Strong answer shape:**
- CDN/cache topology change vs origin protection
- What stays correct (article SoT, takedown) vs what degrades (personalization, comments)
- Metric + kill switch + owner

**Trap:** Origin DB reads for every page view during theme 1 event.


### Extra Interview Drills — News Website — item 2

**Prompt:** 60s drill #2: breaking-news spike handling for this subsystem.

**Strong answer shape:**
- CDN/cache topology change vs origin protection
- What stays correct (article SoT, takedown) vs what degrades (personalization, comments)
- Metric + kill switch + owner

**Trap:** Origin DB reads for every page view during theme 2 event.


### Extra Interview Drills — News Website — item 3

**Prompt:** 60s drill #3: breaking-news spike handling for this subsystem.

**Strong answer shape:**
- CDN/cache topology change vs origin protection
- What stays correct (article SoT, takedown) vs what degrades (personalization, comments)
- Metric + kill switch + owner

**Trap:** Origin DB reads for every page view during theme 3 event.


### Extra Interview Drills — News Website — item 4

**Prompt:** 60s drill #4: breaking-news spike handling for this subsystem.

**Strong answer shape:**
- CDN/cache topology change vs origin protection
- What stays correct (article SoT, takedown) vs what degrades (personalization, comments)
- Metric + kill switch + owner

**Trap:** Origin DB reads for every page view during theme 4 event.

