# System Design: News Website

> **Focus areas:** CMS · Publishing workflow · CDN · Article delivery · Breaking news · Personalization (optional) · Comments (thin)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct read-heavy CDN math, explicit publish/invalidate path, deal-breakers for “all article HTML from origin DB on every pageview” or “personalized homepage fully at edge without careful cache keys”  
> **Interview theme:** Amazon SDE III / L6 — design a **news website**: editorial CMS, publish pipeline, globally fast article reads via CDN, optional personalization, breaking-news freshness, thin comments—owned with cost, reliability, and operational clarity

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

Goal: **bound the product**—a large **news website** where editors create/review/publish articles via a **CMS**, readers consume pages at global scale through a **CDN**, optional **personalization** of homepage/sections, **breaking news** with fast invalidate/update, and **thin comments**—with progressive scale and Amazon ownership (cost per pageview, SEV for wrong content, blast radius).

### 1.0 What this is / is not

| Dimension | **News website (this doc)** | Not this |
|-----------|-----------------------------|----------|
| Primary job | Publish & deliver news articles fast | Full social network / Twitter firehose |
| Success | Correct published content; low latency reads; controlled cost | Perfect ML personalization paper |
| Write path | Low QPS editorial CMS | UGC firehose primary |
| Read path | Extremely high; cacheable | Personalized every byte uncached |
| Breaking news | Fast update + purge | Exactly-once global simultaneous render |
| Comments | Thin / optional | Full Reddit-scale discussion product |
| Amazon lens | Ownership of publish bugs, CDN $, SLO | Only journalism ethics debate |

**Scope statement:** Design news site: CMS, publishing, CDN delivery, optional personalization, breaking news, thin comments—10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | CMS for editors? | Yes — draft, edit, review, publish, unpublish | Workflow + roles |
| F2 | Article types? | Text + images + embeds; video optional | Content model + media |
| F3 | Homepage / sections? | Yes — curated + automated lists | Composition service |
| F4 | CDN delivery? | Yes — mandatory | Cache hierarchy + purge |
| F5 | Breaking news? | Yes — update live; push notify optional | Low TTL / purge / live blog |
| F6 | Personalization? | Optional — topic follows / recommended rail | Edge vs origin split |
| F7 | Search? | Thin — site search | Index async |
| F8 | Comments? | Thin — post/list on article | Separate service; moderate |
| F9 | Paywall / subs? | Optional Phase 1.5 | Auth at edge; cache variants |
| F10 | Multi-language / regions? | Optional | Locale cache keys |
| F11 | Preview unpublished? | Yes — auth’d preview URLs | No CDN public cache |
| F12 | Scheduled publish? | Yes | Scheduler worker |
| F13 | Authors / bylines? | Yes | Entity refs |
| F14 | Tags / topics / sections? | Yes | Taxonomy |
| F15 | Notifications / push / email? | Breaking alerts optional | Thin |
| F16 | Ads? | Slots hooks; not ad exchange design | Placeholder |

**MVP functional scope:**

1. CMS: draft → review → publish / unpublish / schedule.  
2. Article pages + section pages + homepage composition.  
3. Media upload for article assets; CDN.  
4. Global read path via CDN with purge on publish/update.  
5. Breaking news path (live updates / short TTL).  
6. Optional personalization rail (non-blocking).  
7. Thin comments.  
8. Thin site search ingest.  
9. Preview for editors.  
10. Metrics, rollback, audit log.

**Out of MVP:**

- Full ad exchange / header bidding platform  
- Citizen journalism UGC primary  
- Exact real-time collaborative Google-Docs OT in CMS (simple locking OK)  
- Full social graph  
- Podcast/OTT streaming platform  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Article read latency | Global | p99 < 100–200 ms edge hit |
| N2 | Publish to live | Breaking critical | < 5–30 s including purge |
| N3 | Availability | Reads critical | 99.99% read; CMS 99.9% |
| N4 | Correctness | Wrong article = SEV | Versioned publish; audit |
| N5 | Durability | Don’t lose drafts/published | Multi-AZ CMS DB |
| N6 | Cache hit ratio | High | 90–99% HTML/JSON fragments |
| N7 | Cost | Dominated by egress | CDN; compress; image variants |
| N8 | Personalization | Optional degrade | Core article still cached |
| N9 | Comments | Best-effort | Isolation from article read |
| N10 | SEO | Stable URLs; fast | SSR/static-ish pages |
| N11 | Scale | Progressive | 10×/100×/1,000× |
| N12 | Operability | Rollback publish | One-click previous version |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Editor writes draft → reviewer approves → publish → artifact built → CDN warmed/purged → readers see article.  
2. Homepage curated module updated → recompose → purge homepage.  
3. Breaking story: editor updates body every minute → short TTL or targeted purge → live blog posts append.  
4. Reader hits article URL → CDN HIT → HTML/JSON.  
5. Optional: logged-in reader gets personalized “For you” rail via separate API; main article still CDN.  
6. Reader posts comment → thin service stores; appears after moderate.  
7. Scheduler publishes at embargo time.  
8. Unpublish / legal takedown → purge all surfaces.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Publish while CDN still has old | Purge/surrogate keys; version URLs for assets |
| Purge storm | Rate-limit purges; soft TTL expiry backup |
| Wrong article published | Rollback to previous immutable version; purge |
| Embargo leak via preview URL | Auth + short-lived tokens; noindex |
| Origin DB outage | CDN still serves cached articles; CMS down |
| Personalization service down | Hide rail; show popular/default |
| Comments down | Article still loads |
| Viral breaking article | Edge hit; origin shield; collapse thundering herd |
| Image hotlink | CDN referrer policies / tokens optional |
| Dual editors conflict | Locking / last-write-wins with warning |
| Scheduled job lag | Alert; manual publish |
| SEO duplicate URLs | Canonical tags; 301 policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Pageviews / day | 100M | 1B | 10B | 100B |
| Peak pageviews / s | 20K | 200K | 2M | 20M |
| Articles published / day | 2K | 20K | 200K | 2M (network) |
| Concurrent editors | 200 | 2K | 20K | 200K |
| Breaking spikes | 10× baseline | 20× | 50× | 100× |
| CDN hit ratio | 95% | 97% | 98%+ | multi-CDN |
| Personalized API QPS | 5K | 50K | 500K | edge+feature store |
| Comments / day | 1M | 10M | 100M | isolate |
| Media assets / day | 10K | 100K | 1M | lifecycle |

**What each jump forces:**

- **10×:** CDN mandatory; surrogate-key purge; origin shield; static/SSR generation; comments isolated.  
- **100×:** Multi-region origin; fragment caching; personalization sidelined; multi-CDN optional; search shards.  
- **1,000×:** Cell or brand-partitioned sites; edge compute careful; approx analytics; aggressive image CDN; API gateway tiers.

### 1.5 Etc. (Constraints & Assumptions)

| Assumption | Choice |
|------------|--------|
| Rendering | SSR or pre-rendered HTML/JSON artifacts preferred for articles |
| Personalization | Optional rail; not entire page unique MVP |
| Paywall | Phase 1.5; mention cache `Vary` complexity |
| Comments | Prefetch after article; moderation queue |
| Live blog | Append-only updates for breaking |
| Analytics | Async beacons; approximate OK |
| Auth readers | Optional accounts for comments/personalization |

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Examples | Notes |
|-------|----------|-------|
| Editorial writes | CMS save/publish | Low QPS; high correctness |
| Public reads | Article/home/section | Ultra hot; CDN |
| Breaking updates | Frequent publishes | Purge-heavy |
| Personalization | Recs API | Per-user; cache carefully |
| Comments | Post/list | Medium; isolatable |
| Media | Images | CDN egress |

### 2.2 Storage math

```text
2K articles/day × ~50 KB body+meta ≈ 100 GB/day raw text+meta (generous)
Images: 2K × 5 images × 200 KB ≈ 2 TB/day before variants policy
Version history: keep N versions per article → budget explicitly

Pageviews 100M/day × 80 KB HTML ≈ 8 PB/day theoretical egress
  → CDN hit 95% ⇒ origin egress ~0.4 PB/day still huge
  → Prefer compressed HTML; image lazy; HTTP cache; HTTP/2/3
Interview: emphasize hit ratio and artifact size control
```

### 2.3 Publish / purge math

```text
Publish event → purge keys: article, homepage modules, section pages, RSS, AMP…
Fanout of purge URLs can be dozens per publish
Breaking: 1 update/min × many objects → need surrogate keys / soft purge
```

### 2.4 Latency budgets

| Path | Target |
|------|--------|
| CDN HIT article | < 50–100 ms (near POP) |
| CDN MISS + origin | < 300–500 ms |
| CMS save draft | < 300 ms |
| Publish API | < 1–2 s incl. enqueue build |
| Live after purge | < 5–30 s global typical |

### 2.5 Cache math

```text
Popular articles: extremely hot at edge
Long-tail: may miss; origin shield collapses
Homepage: high QPS; revalidate often or event purge
Personalized homepage: DO NOT put full page on shared CDN key
```

### 2.6 Personalization cost (optional)

```text
If 30% users logged in request recs each session:
  extra API QPS significant but << article HTML QPS if fragmented
Feature store / candidate cache per cohort reduces cost
```

### 2.7 Scale jump worksheet

| Jump | Forced investment |
|------|-------------------|
| 10× | CDN, purge keys, shield, pre-render |
| 100× | Multi-region origin, fragment cache, isolate comments |
| 1,000× | Multi-CDN, edge careful, cells/brands, approx analytics |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Reads off origin** — CDN is the product surface.  
2. **Publish is versioned & auditable** — rollback fast.  
3. **Breaking news freshness** without melting origin.  
4. **Personalization optional & degradable** — never block core article.  
5. **Comments thin & isolated.**  
6. **Cost ownership** — egress, purge storms, image weight.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| CMS API / UI | Editors, roles, workflow |
| Content Store | Drafts, versions, published pointers |
| Media Library | Assets, crops, rights metadata |
| Publish Pipeline | Validate → build artifacts → store → purge |
| Artifact Store | Immutable HTML/JSON blobs (S3) |
| CDN / Edge | Cache, TLS, WAF, geo |
| Origin / Gateway | MISS handler; auth preview |
| Composition Service | Homepage/section modules |
| Breaking / Live Blog Svc | Rapid updates stream |
| Personalization Svc (opt) | Recs rail API |
| Comments Svc (thin) | Create/list/moderate |
| Search Ingest (thin) | Article index |
| Scheduler | Embargo publish |
| Notification (opt) | Push/email breaking |
| Audit Log | Who published what when |

### 3.3 Content model

**Article:** `article_id`, `slug`, `canonical_url`, `title`, `dek`, `body` (structured blocks), `authors[]`, `section`, `tags[]`, `hero_media`, `status`, `published_version`, `updated_at`, `embargo_at`

**Version:** immutable snapshot at publish (`version_id`, `content_hash`, `artifact_key`)

**Composition:** module list for home/section (`module_type`, `article_refs[]`, `pinned`)

### 3.4 Publishing workflow

```text
draft -> in_review -> approved -> published
                 \-> rejected
published -> unpublished (takedown)
editor can schedule approved -> scheduler fires publish
```

Roles: writer, editor, publisher, admin. Least privilege.

### 3.5 Publish pipeline (critical path)

1. Publisher clicks Publish (or schedule fires).  
2. Transaction: set `published_version` to new immutable snapshot.  
3. Enqueue build job: render HTML + JSON API artifact + AMP optional.  
4. Write artifacts to object store (versioned keys).  
5. Update “current” pointer (`slug → version`).  
6. **Purge / soft-invalidate** CDN surrogate keys: `article:{id}`, `section:{id}`, `home`, `rss`.  
7. Optional: warm cache for top URLs.  
8. Emit events → search ingest, alerts, personalization features.

**Deal-breaker:** mutating a single row and hoping anonymous edge caches expire eventually without purge strategy for breaking news.

### 3.6 Read path

```text
Reader -> CDN
  HIT: return artifact
  MISS: Origin fetches current artifact from object store (or renders with cache)
      -> set Cache-Control / surrogate-control
      -> return
```

**Cache-Control sketch:**

- Standard article: `s-maxage=60–300`, stale-while-revalidate  
- Breaking / live: `s-maxage=5–15` or purge-on-write  
- Static assets hashed URLs: `immutable` long TTL  
- Preview: `private, no-store`

### 3.7 Breaking news design

Options (combine):

1. **Short TTL** on live articles.  
2. **Surrogate-key purge** on each update.  
3. **Live blog**: article shell cached; updates fetched via small JSON endpoint (short TTL or SSE).  
4. **Client polling** for live blog cursor.

Prefer: shell + updates stream so you don’t purge entire HTML every 10s globally if avoidable.

### 3.8 Personalization (optional)

**Pattern: islands / rails**

- Core article & most of homepage modules = anonymous CDN cacheable.  
- `GET /api/recs?uid=` returns personalized list (auth, `Cache-Control: private`).  
- Client hydrates rail.  
- Cohort-level cache (`recs:cohort:{id}`) if fully per-user too expensive.

**Degrade:** popular top stories if recs fail.

### 3.9 Comments (thin)

```text
POST /articles/{id}/comments  -> Comments Svc (auth, RL, moderate)
GET  /articles/{id}/comments?cursor=
```

- Stored separately; not in article artifact.  
- Moderation: spam, toxic; optional delay.  
- Cache comment list briefly; purge on new comment optional.  
- Failure must not blank the article page.

### 3.10 API sketch

```text
# CMS
POST   /cms/articles
PATCH  /cms/articles/{id}
POST   /cms/articles/{id}/submit-review
POST   /cms/articles/{id}/publish
POST   /cms/articles/{id}/unpublish
POST   /cms/articles/{id}/rollback {version_id}
GET    /cms/articles/{id}/versions
POST   /cms/media

# Public
GET    /{section}/{slug}           # HTML via CDN
GET    /api/articles/{id}          # JSON
GET    /api/home
GET    /api/live/{article_id}?since=
GET    /api/recs                   # optional personalized
GET    /api/search?q=

GET    /api/articles/{id}/comments
POST   /api/articles/{id}/comments
```

### 3.11 Tradeoffs table

| Decision | Choice | Why |
|----------|--------|-----|
| SSR vs client-only SPA | Pre-render/SSR artifacts | SEO + CDN |
| Purge vs TTL only | Purge + TTL backup | Breaking + safety |
| Full personalized HTML | No — rails | Cache hit ratio |
| Comments in artifact | No — side service | Isolation |
| Monolithic CMS DB | OK early; shard later | Write low QPS |
| Multi-CDN | At 100×+ | Resilience |

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
 Editors --> CMS UI --> CMS API --> Content DB (versions)
                           |
                           v
                    Publish Pipeline
                       |         |
                       v         v
                 Artifact Store  Purge API --> CDN Edges (POPs)
                       ^                         |
                       |                         v
 Readers ----------------------------------------+--> HIT response
                       |
                    MISS --> Origin Gateway --> Artifact Store
                       |
            +----------+----------+--------------+
            v          v          v              v
      Composition  Live Blog   Recs API     Comments Svc
            |          |       (private)         |
            +------> Event Bus --> Search / Alerts / Analytics
 Media Lib --> Object Store --> CDN (images)
```

### 4.2 Publish sequence

```text
Editor -> CMS: publish
CMS -> DB: commit version pointer
CMS -> Queue: build_artifact(version)
Worker -> render HTML/JSON -> S3
Worker -> CDN purge(surrogate keys)
Worker -> Bus: article_published
Client readers: subsequent GET sees new after purge propagate
```

### 4.3 Reader sequence (MISS)

```text
Reader -> CDN MISS
CDN -> Origin: GET article
Origin -> S3 current artifact
Origin -> CDN: store with cache headers
CDN -> Reader
```

### 4.4 Breaking live blog

```text
Editor posts live update -> Live Blog Store append
Purge or short TTL on /api/live/{id}
Article shell remains cached
Client polls / SSE for updates
```

### 4.5 Multi-region at 100×+

```text
        Global CDN
           |
   +-------+--------+
   Origin US     Origin EU   (active-active artifacts via CRR)
   CMS primary writes in home region; replicate
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. Published pointer always references an immutable artifact that exists.  
2. Rollback switches pointer + purge.  
3. Unpublished/takendown articles must not be CDN-served after purge SLO.  
4. Preview URLs never publicly cacheable.  
5. Comments/recs cannot block article HTML.

#### 5.1.2 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| CMS DB down | No edits | Multi-AZ; readers OK via CDN |
| Build pipeline down | Publish stuck | Alert; retry; manual artifact |
| Purge API down | Stale content | TTL safety net; replay purge |
| Origin down | MISS fail | High hit ratio; multi-origin |
| Bad publish | Wrong story | Rollback runbook |
| Recs down | Less personalization | Default modules |
| Comments down | No discussion | Article OK |
| CDN POP outage | Regional | Other POPs / multi-CDN |

#### 5.1.3 Durability

- Content DB: quorum + PITR.  
- Artifacts: multi-AZ object store; versioned.  
- Draft autosave.  
- Audit log append-only.

#### 5.1.4 Consistency

| Path | Model |
|------|-------|
| Editor preview | Read-your-write from primary |
| Global readers after publish | Eventual (purge propagation seconds) |
| Search index | Eventual |
| Comment counts on article | Approx / separate |

#### 5.1.5 Security

- CMS SSO + MFA + roles.  
- WAF at edge; bot management for scrape.  
- Sanitize article HTML (XSS).  
- Embargo: ACL + audit.  
- Signed preview links with expiry.

### 5.2 Scalability

#### 5.2.1 Read path (main game)

- Maximize CDN HIT.  
- Origin shield / request coalescing.  
- Immutable hashed assets.  
- Compress (Brotli).  
- Fragment cache for expensive modules.  
- Avoid DB on MISS — serve artifacts from object store.

#### 5.2.2 Write / publish scaling

- CMS DB write QPS low even at 10× — vertical + read replicas for lists OK.  
- Build workers autoscale on queue depth.  
- Purge batching; surrogate keys over URL spray.  
- At network scale (1,000× articles): shard content by brand/site id.

#### 5.2.3 Breaking news spikes

- Pre-warm templates.  
- Live updates endpoint tiny payloads.  
- Edge cache with very short TTL.  
- Rate limit CMS publish automation.  
- Protect origin with shield.

#### 5.2.4 Personalization scaling

- Precompute candidates offline.  
- Online rank top-N light.  
- Cohort caches.  
- Timeouts + degrade.

#### 5.2.5 Comments scaling (thin)

- Shard by `article_id`.  
- Hot article comments: cache first page; RL posters.  
- Don’t embed in HTML artifact.

#### 5.2.6 Cost controls

| Lever | Saves |
|-------|-------|
| CDN HIT | Origin + egress |
| Image variants / lazy | Egress |
| Artifact size diet | Egress |
| Purge keys not URL flood | Ops $ |
| Recs degrade | Compute |
| Analytics sample | Pipeline $ |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| CMS workflow | Editorial eng |
| Publish/artifacts | Web platform |
| CDN/purge | Edge/SRE |
| Composition | Homepage team |
| Personalization | Recs |
| Comments | Community thin team |
| Search | Search |

#### 5.3.2 Safe evolution

- Content block schema versioned.  
- Artifact format versioning.  
- Canary publish to internal POP.  
- Feature flags for new modules.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| CDN HIT ratio | > 95% |
| Publish→visible | < 30 s p95 |
| Article p99 edge | < 150 ms |
| Rollback time | < 2 min |
| Origin error rate | < 0.1% |
| Comments error isolation | article success independent |

Dashboards: purge latency, build queue, top MISS URLs, breaking article QPS, XSS/moderation.

#### 5.3.4 Progressive scale checklist

| Scale | Checklist |
|-------|-----------|
| 10× | CDN+purge+artifacts+shield+comments isolate |
| 100× | Multi-region artifacts, fragment cache, recs cohort |
| 1,000× | Multi-CDN, site cells, edge compute careful, approx BI |

### 5.4 Deep dive: surrogate keys & purge

```text
Article page tags: article:123 section:world home rss:world
On publish(123): purge tag article:123 (+ compose dependents)
CDN maps tag -> cached objects
Better than listing 50 URLs manually
```

Soft purge / stale-while-revalidate reduces thundering herds.

### 5.5 Deep dive: artifact generation

```text
Input: version snapshot JSON blocks
Render: HTML template + JSON API doc
Store: s3://artifacts/{article_id}/{version_id}/index.html
Pointer: current/{slug} -> version_id
Safe rollback: flip pointer to previous version_id; purge
```

### 5.6 Deep dive: cache key & personalization

```text
GOOD: /world/story-slug           Cache-Control public (anonymous article)
GOOD: /api/recs                   private, per-user or cohort
BAD:  /home?user_id=123           as globally shared CDN key
BAD:  Vary: Cookie on all HTML    fragments cache hierarchy
```

If paywall: `Vary: Authorization` or separate cookie bucketing (`subscriber` vs `anon`) with care (cache explosion).

### 5.7 Deep dive: embargo & preview

- `status=embargo` until `embargo_at`.  
- Scheduler publishes atomically.  
- Preview: `/preview/{token}` authZ; `Cache-Control: private, no-store`.  
- Risk: third-party embeds leaking — block external until live.

### 5.8 Deep dive: SEO & URLs

- Stable canonical slugs; updates don’t change URL without 301.  
- SSR/pre-render for crawlers.  
- XML sitemaps generated from publish events.  
- AMP/alternate links optional.

### 5.9 Testing & resilience

- Purge integration tests in staging CDN.  
- Chaos: origin down — HIT still serves.  
- Load: viral article spike.  
- CMS permissions tests.  
- XSS fuzz on body blocks.  
- Rollback game days.

### 5.10 Amazon leadership connection

- **Ownership:** wrong headline is a SEV with rollback runbook.  
- **Frugality:** CDN HIT and image diets beat bigger origins.  
- **Dive Deep:** purge vs TTL, cache keys with personalization.  
- **Bias for action:** ship rails personalization, not uncacheable home.

---

## 6. Wrap-Up

### 6.1 30-second recap

A news website is a **low-QPS versioned CMS + artifact publish pipeline + CDN-first read path**. Publish commits immutable versions, builds HTML/JSON artifacts, purges by surrogate keys; breaking news uses short TTL/live-update endpoints; optional personalization is a degradable private rail; comments are thin and isolated; scale is mostly edge, shields, and multi-region artifacts—not bigger monolithic DB reads per pageview.

### 6.2 Key tradeoffs

| Tradeoff | Pick |
|----------|------|
| Dynamic origin render vs artifacts | Artifacts + CDN |
| TTL vs purge | Both |
| Personalized full page vs rails | Rails |
| Comments in page vs service | Service |
| Exact global simultaneous update | Seconds OK |

### 6.3 Risks & follow-ups

- Purge propagation variance by POP.  
- Cache key explosion with paywall variants.  
- Build pipeline backlog during elections.  
- Embargo process leaks.  
- Editor locking UX.

### 6.4 What “good” looks like

- Clear CMS workflow + versioning.  
- Publish/purge sequence explicit.  
- CDN math & HIT ratio.  
- Breaking news approach.  
- Personalization without destroying cache.  
- Isolation of comments.  
- Ownership & rollback.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. SSR vs SPA tradeoffs for news?  
2. How many versions retained?  
3. Live blog vs editing same article?  
4. Paywall in MVP?  
5. Mobile apps same API?  
6. Multi-brand newsroom?  
7. Embargo legal requirements?  
8. Video hosting in-house vs YouTube embed?  
9. Newsletter generation?  
10. AMP still needed?  
11. Offline reading?  
12. Accessibility requirements?

### 7.2 CMS & publish (Q13–Q28)

13. Optimistic locking for editors.  
14. Workflow state machine.  
15. Artifact immutability benefits.  
16. Rollback vs unpublish.  
17. Scheduled publish exactly-once.  
18. Partial module publish on homepage.  
19. Schema evolution for body blocks.  
20. Media rights expiry.  
21. Audit log requirements.  
22. Preview token theft.  
23. Multi-language variants.  
24. Breaking news dual control approval.  
25. Canary publish.  
26. Build failure mid-publish.  
27. Content checksum verification.  
28. Large election night publish volume.

### 7.3 CDN & caching (Q29–Q44)

29. Surrogate keys design.  
30. Soft vs hard purge.  
31. Stale-while-revalidate.  
32. Origin shield.  
33. Thundering herd on MISS.  
34. Cache key for A/B tests.  
35. Cookie `Vary` dangers.  
36. Multi-CDN invalidation.  
37. Negative caching 404.  
38. Image CDN transforms.  
39. HTTP/3 impact.  
40. GEO restrictions.  
41. Bot scrape vs HIT ratio.  
42. Signed cookies for subscribers.  
43. Purge storm protection.  
44. Measuring true global visibility time.

### 7.4 Personalization & comments (Q45–Q56)

45. Why rails pattern?  
46. Cohort vs per-user cache.  
47. Cold start recs.  
48. Privacy of reading history.  
49. Comment moderation SLA.  
50. Hot article comment QPS.  
51. Spam defenses.  
52. Ranking comments thin.  
53. PII in comments GDPR.  
54. Websockets for live comments?  
55. Isolate failure UX.  
56. Ads personalization vs news recs conflict.

### 7.5 Scale & ops (Q57–Q68)

57. First bottleneck at 10×?  
58. Origin sizing worksheet.  
59. Multi-region CMS writes.  
60. Election day runbook.  
61. Cost per 1000 pageviews.  
62. Search index lag.  
63. Analytics sampling.  
64. Chaos tests.  
65. SLO burn alerts.  
66. Cell by brand.  
67. Image lifecycle.  
68. When edge compute for SSR?

### 7.6 Behavioral / Amazon (Q69–Q74)

69. SEV: wrong article live — first 15 minutes.  
70. Frugality: image weight budget fight with design.  
71. Disagree: PM wants fully personalized SSR homepage.  
72. Dive deep: whiteboard purge dependency graph.  
73. Ownership: CDN vendor vs app team during stale content.  
74. Customer obsession: breaking news freshness vs accuracy workflow.

---

## 8. Appendices

### Appendix A — Cache policy matrix

| Surface | CDN | TTL | Purge |
|---------|-----|-----|-------|
| Article HTML | public | 60–300s | on publish |
| Live updates JSON | public | 5–15s | on update |
| Homepage | public | 30–60s | on compose |
| Hashed assets | public | 1y immutable | rename |
| Recs API | private | short | n/a |
| Preview | no-store | — | — |
| Comments list | public/private | 10–30s | optional |

### Appendix B — Example article version JSON

```json
{
  "article_id": "A_100",
  "version_id": "V_9",
  "slug": "world/markets-open",
  "title": "Markets open mixed",
  "body_blocks": [{"type": "paragraph", "text": "…"}],
  "section": "business",
  "tags": ["markets"],
  "content_hash": "sha256:…",
  "published_at": 1754470000
}
```

### Appendix C — Surrogate keys example

```text
Surrogate-Key: article:A_100 section:business home rss:business
Cache-Control: public, s-maxage=120, stale-while-revalidate=600
```

### Appendix D — Rate limits

| Subject | Comment posts | CMS publish | Search |
|---------|---------------|-------------|--------|
| Anon | 0 | 0 | 60/hour |
| User | 20/day | — | 300/hour |
| Editor | — | workflow | — |
| Break-glass admin | audited | high | — |

### Appendix E — Error codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created draft/comment |
| 401 | Auth required |
| 403 | CMS forbidden / embargo |
| 404 | Missing / unpublished |
| 409 | Edit conflict |
| 429 | Rate limited |
| 503 | Origin/dependency |

### Appendix F — Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| DB render every pageview | Melts; costly |
| No purge strategy | Breaking news stale |
| Personalized full HTML at edge shared key | Wrong content / low HIT |
| Comments in artifact rebuild | Slow + coupled |
| Unversioned overwrite publish | Weak rollback |
| Infinite preview links | Embargo leaks |
| Purge all site on each edit | CDN thrash |

### Appendix G — Capacity worksheet

```text
PV/day _____ × avgKB _____ = theoretical egress _____
HIT ratio _____ → origin egress _____
Peak PV/s _____ ; MISS% _____ → origin QPS _____
Publishes/day _____ × artifacts _____ × purge objects _____
Image GB/day _____
```

### Appendix H — 45-minute timebox

| Min | Focus |
|-----|-------|
| 0–5 | CMS, CDN, breaking, personalization?, comments thin |
| 5–12 | PV math, egress, HIT ratio |
| 12–25 | HLD publish pipeline + read path |
| 25–35 | Breaking OR personalization cache OR rollback |
| 35–42 | 10×/100×/1,000× + failures |
| 42–45 | Wrap-up SLOs |

### Appendix I — Glossary

| Term | Meaning |
|------|---------|
| Artifact | Immutable rendered output of a version |
| Surrogate key | CDN tag for group purge |
| Origin shield | Intermediate cache collapsing MISSes |
| Live blog | Append-only updates on a story |
| Embargo | Pre-publish hold until time |
| Soft purge | Mark stale; revalidate |
| Rail / island | Partial personalized component |

### Appendix J — Sample public article API

```json
{
  "id": "A_100",
  "version_id": "V_9",
  "title": "Markets open mixed",
  "section": "business",
  "body_html": "<p>…</p>",
  "updated_at": "2026-08-06T07:22:11Z",
  "authors": [{"name": "Jane Doe"}]
}
```

### Appendix K — Ownership RACI

| Activity | CMS | Publish | CDN | Recs | Comments |
|----------|-----|---------|-----|------|----------|
| Cache TTL change | C | C | A | C | C |
| Rollback | A | A | C | I | I |
| Homepage module | A | C | C | C | I |
| Recs degrade policy | I | I | I | A | I |
| Takedown | A | A | A | C | C |

### Appendix L — Progressive scale one-pager

| Scale | Bottleneck | Investment |
|-------|------------|------------|
| 10× | Origin MISS / egress $ | CDN, artifacts, purge, shield |
| 100× | Global freshness + spikes | Multi-region, live endpoints, multi-CDN prep |
| 1,000× | Brand cells + paywall variants | Cells, careful Vary, approx analytics |

### Appendix M — Comparison

| Topic | Answer |
|-------|--------|
| vs blog (WordPress monolith) | Explicit artifacts+CDN+purge |
| vs Twitter | Editorial write-low; read-high cacheable |
| vs Netflix homepage | News more CDN-HTML; less dense ML MVP |
| vs Reddit | Comments thin not core |

### Appendix N — Threat model

| Asset | Threat | Control |
|-------|--------|---------|
| Published truth | Unauthorized publish | Roles, MFA, audit |
| Embargo | Leak | Preview ACL, logs |
| Readers | XSS in article | Sanitize, CSP |
| Platform $ | Scrape/egress | WAF, bot mgmt, CDN |
| Comments | Spam/abuse | RL, moderation |

### Appendix O — Publish pseudocode

```text
function publish(article_id, actor):
  assert can_publish(actor, article_id)
  version = snapshot(article_id)
  write_immutable(version)
  tx: set current_pointer(article_id, version.id); audit(actor)
  enqueue build_and_purge(version)
  return accepted
```

### Appendix P — Rollback pseudocode

```text
function rollback(article_id, version_id, actor):
  assert exists(version_id) and belongs(article_id)
  set current_pointer(article_id, version_id)
  purge keys for article + dependents
  audit(actor, "rollback")
```

### Appendix Q — Reader MISS pseudocode

```text
function origin_get(slug):
  version = pointer(slug)
  if not version or unpublished: return 404
  return artifact_store.get(version) with cache headers
```

---

*End of Amazon SDE III prep doc — News Website System Design.*
