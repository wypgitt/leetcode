# System Design: TinyURL / URL Shortener

> **Focus areas:** Encode · Redirect · Analytics (optional) · Custom aliases · Expiry · High QPS redirects · Hot keys · Cache · Abuse  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct ID-space math, clear read/write split, deal-breakers for “hash(url) as only key” or “no cache for redirects”, explicit Amazon ownership/cost/reliability flavor  
> **Interview theme:** Amazon SDE III / L6 — design a **URL shortener** that creates short links, redirects at very high QPS, supports custom aliases & expiry, optionally analytics—cheap, correct, hard to abuse

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

Goal: **bound the product**—users **create** short URLs mapping to long destinations, clients **redirect** with minimal latency at massive QPS, optionally set **custom aliases** and **expiry**, optionally collect **analytics**, with strong **abuse** controls and progressive scale.

### 1.0 What this is / is not

| Dimension | **TinyURL / shortener (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | `short → 302/301 → long` at huge read QPS | Full link-in-bio social CMS |
| Success | Fast correct redirects; durable mappings; low cost | Perfect real-time BI warehouse on every click |
| Entities | Link, code/alias, owner, TTL, click events | Nested page builders, A/B landing editors MVP |
| Read:write | Extremely high (often 100:1–1000:1+) | Symmetric CRUD app |
| Consistency | Read-your-write after create; redirects eventually consistent OK if bounded | Strong global linearizability for every click |
| Amazon lens | Ownership, cost per redirect, reliability, trust/abuse | Base62 trivia only |

**Scope statement:** Design TinyURL: encode, redirect, optional analytics, custom aliases, expiry—optimized for high-QPS redirects—scaled 10×/100×/1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Create short link? | Yes — long URL in, short code out | Write API + unique code |
| F2 | Redirect? | Yes — primary UX; 302 default | Ultra-hot read path |
| F3 | Custom alias? | Optional — user-chosen slug if available | Reservation + abuse |
| F4 | Expiry? | Optional TTL or absolute expiry | Enforce on read; GC |
| F5 | Update destination? | Optional; often immutable MVP | Cache invalidation if mutable |
| F6 | Delete / disable? | Owner/admin | Tombstone + purge |
| F7 | Analytics? | Optional — click counts, referrer, geo coarse | Async events; approx OK |
| F8 | Accounts? | Optional MVP; anon with limits | Auth for aliases/analytics |
| F9 | Preview / interstitial? | Optional safety interstitial for suspicious | Trust path |
| F10 | QR codes? | Nice-to-have derived asset | Not on hot path |
| F11 | Password / gated? | Optional | AuthZ before redirect |
| F12 | Bulk create? | API for partners | Idempotency; rate limits |
| F13 | Brand domains? | Custom domains Phase 1.5 | Host-based routing |
| F14 | 301 vs 302? | 302 default (flexibility); 301 opt-in | Cache semantics |
| F15 | Unicode / IDN long URLs? | Validate & normalize carefully | SSRF / open-redirect safety |

**MVP functional scope:**

1. `POST /links` — create short link (auto code or custom alias).  
2. `GET /{code}` — redirect to long URL if active & unexpired.  
3. Unique codes; collision handling.  
4. Optional expiry enforcement.  
5. Optional click event emit (async).  
6. Rate limits + malware/phishing URL checks (hooks).  
7. Owner delete/disable.  
8. Metrics/alarms; cache for redirects.  
9. Read-your-write after create.  
10. Admin takedown.

**Out of MVP:**

- Full marketing suite / A/B multi-destination rules engine  
- Guaranteed exactly-once analytics  
- Global public search of all URLs  
- Real-time collaborative link editing  
- Serving as open redirector for arbitrary unvalidated schemes  
- Permanent legal archive of every click forever without cost controls

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Redirect latency | Global users | p99 < 50–100 ms at edge; origin p99 < 20–50 ms cached |
| N2 | Create latency | Interactive | p99 < 200–300 ms |
| N3 | Availability | Redirects critical | 99.99% redirect; 99.9% create |
| N4 | Durability | Don’t lose mappings | Multi-AZ durable store |
| N5 | Read:write | Very high | Design for cache hit ≫ miss |
| N6 | Consistency | Create then redirect works | Primary read / sticky / cache fill |
| N7 | Expiry correctness | Must not redirect past TTL | Check `expires_at` on serve |
| N8 | Enumeration | Hard to brute private links | Long codes + rate limit |
| N9 | Cost | Dominated by redirects/egress | Edge cache; tiny payloads |
| N10 | Abuse resilience | Spam, phishing, malware | Limits, scanners, blocklists |
| N11 | Scalability | Progressive | Scale table |
| N12 | Operability | Clear ownership | Idempotent creates; runbooks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User posts long URL → gets `https://short.example/aB3xY9` → shares → millions of 302 redirects via edge cache.  
2. User chooses custom alias `my-sale` → reserved if free → redirects.  
3. Link expires in 24h → after TTL, 404/410; analytics stop.  
4. Owner disables link → tombstone; caches purged.  
5. Optional analytics dashboard shows approximate clicks over time.  
6. Partner bulk API creates 10K links with idempotency keys.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate create retry | Idempotency-Key → same code |
| Custom alias taken | 409 conflict |
| Extremely hot code (celebrity) | Edge cache + origin shield; single-flight fill |
| Expired but cached | `Cache-Control` max-age ≤ remaining TTL; purge job |
| Update destination (if allowed) | Version bump; purge cache |
| Malicious javascript: URL | Scheme allowlist `http/https` only |
| SSRF to metadata IP | Block private/link-local ranges on create validation |
| Phishing URL | Async scan; disable; interstitial |
| Code enumeration | Rate limit 404; CAPTCHA; ban |
| Unicode input | Normalize; reject weird whitespace |
| Extremely long URL | Max length enforce (e.g. 2–8 KB) |
| Redirect loop short→short | Hop limit / detect own host cycles |
| DB outage | Cached redirects still serve; creates fail |
| Analytics pipeline down | Redirects unaffected (async) |
| Clock skew expiry | Absolute `expires_at`; skew budget |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Links created / day | 10M | 100M | 1B | 10B |
| Peak writes / s | 500 | 5K | 50K | 500K |
| Redirects / day | 10B | 100B | 1T | 10T |
| Peak redirects / s | 500K | 5M | 50M | 500M |
| Read:write | ~1000:1 | similar | similar | similar |
| Active links stored | 5B | 50B | 500B | 5T |
| Custom alias creates / day | 1M | 10M | 100M | 1B |
| Hot keys (viral) | 10K | 100K | 1M | 10M |
| Edge cache hit ratio | 90–95% | 95%+ | 95%+ | edge+shield |
| Analytics events / s peak | 500K | 5M | 50M | 500M |

**What each jump forces:**

- **10×:** CDN/edge mandatory; Redis/mem cache; Dynamo-style metadata; async analytics.  
- **100×:** Shard by code; multi-region read; origin shields; alias registry careful design.  
- **1,000×:** Cell/partition by keyspace; anycast edge; approx analytics only; aggressive expiry defaults; dedicated hot-key service optional.

### 1.5 Etc. (Constraints & Assumptions)

- Short codes are **capability URLs** unless gated.  
- Prefer **302** unless user opts into 301 (browser caches 301 aggressively).  
- Analytics are **best-effort** unless explicitly paid-accurate.  
- “Encode” means generate unique short code—not cryptographic encryption of the URL.  
- Open redirect / phishing liability is a **first-class** product risk.

**Scope statement:**

> Design a URL shortener that creates unique short codes (and optional custom aliases), redirects at very high QPS with caching, enforces expiry/tombstones, optionally emits analytics asynchronously, resists abuse—and scales 10× / 100× / 1,000× with clear ownership of cost and trust.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
Baseline 10M creates/day ÷ 86400 ≈ 116/s average
Peak ~4× ⇒ ~500 writes/s

Redirects 10B/day ÷ 86400 ≈ 115K/s average
Peak ~4× ⇒ ~500K/s (matches table)

At edge hit ratio 95%:
  origin redirect QPS ≈ 5% × 500K = 25K/s baseline peak
Still substantial — metadata store + app caches must be ready
```

At **1,000×**: 500M redirects/s peak is an **edge CDN problem** first; origin sees a slice.

### 2.2 Storage

```text
Link metadata ~200–500 B (code, long URL, owner, timestamps, flags)
10M/day × 300 B ≈ 3 GB/day new metadata
Retain years → baseline years × 3 GB/day ≈ multi-PB eventually with growth

Analytics raw events ~100–200 B each
10B redirects/day × 150 B = 1.5 PB/day raw — **impossible to keep raw naively**
⇒ sample, aggregate, or tier ruthlessly at scale
```

### 2.3 Bandwidth

```text
Redirect response tiny: 300–800 B (status + Location + headers)
500K/s × 600 B ≈ 300 MB/s edge egress baseline peak
1,000×: 500M/s × 600 B = 300 GB/s — only viable at global edge
```

### 2.4 ID space math (critical interview)

```text
Base62 alphabet [A-Za-z0-9] = 62 chars
Length 7: 62^7 ≈ 3.5e12 (~3.5 trillion)
Length 8: 62^8 ≈ 2.2e14

Birthday collision approximation:
For n random codes in space S, collision ~ n^2 / 2S

At 10M/day for 10 years ≈ 3.65e10 codes
With length 7: n^2/2S ≈ (3.65e10)^2 / (7e12) ≈ huge? 
  (3.65e10)^2 = 1.33e21
  2S ≈ 7e12
  1.33e21 / 7e12 ≈ 1.9e8 → collisions expected if pure random without uniqueness check

Conclusion: **always check uniqueness** (or use coordinated unique allocation).
Length 7–8 OK with DB unique constraint / conditional put.
For unlisted/secret links, prefer longer (10+) against enumeration.
```

### 2.5 Memory / cache

```text
Hot working set: top 1M codes × 400 B ≈ 400 MB — fits Redis easily
At 100×: top 10–50M keys → sharded cache
Negative cache for 404s: short TTL; careful with create races
```

### 2.6 Latency budget (redirect)

```text
Edge HIT:   < 10–30 ms (geo)
Edge MISS → Origin shield → App cache → DB
Budget origin path p99: 20–50 ms
Analytics MUST NOT be on synchronous redirect path
```

### 2.7 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | Origin on viral links | CDN + shield + singleflight |
| 100× | Metadata partitions / alias hotspot | Shard; alias registry; multi-region |
| 1,000× | Analytics volume + edge cost | Approx aggregates; sampling; cells |

### 2.8 Cost owner sketch

```text
Cost ≈ edge requests + origin misses + storage + analytics ingest
Optimize: cache hit ratio SLO, 302 small headers, TTL expiry GC, sample clicks
```

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Redirect path is sacred** — never block on analytics, scanning, or fancy features.  
2. **Correctness** — unique codes; expiry/tombstone honored.  
3. **Cost** — hit ratio is a product metric.  
4. **Trust** — phishing/malware controls; takedown path.  
5. **Progressive scale** — cells/keyspace partitions when needed.  
6. **Simple APIs** — create & redirect excellence first.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| API / Create Service | Validate URL; allocate code; persist |
| Redirect Service | Resolve code → Location; enforce state/TTL |
| Metadata Store | Link records; unique constraints |
| Alias Registry | Custom slug uniqueness (optional separate) |
| Cache (Redis/Mem) | Hot mappings |
| Edge CDN / Anycast | Global redirect acceleration |
| ID Allocator | Unique code generation |
| Analytics Ingest | Async click events |
| Analytics Aggregate | Rollups / dashboards |
| Abuse / Safety | URL scan, blocklists, rate limits |
| Admin / Takedown | Disable + purge |
| Auth | Owners, API keys |

### 3.3 Encode options (say clearly)

| Approach | How | Pros | Cons |
|----------|-----|------|------|
| Counter + Base62 | Snowflake/Redis INCR → encode | Unique, short | Predictable if sequential; shard counters |
| Random + Unique put | RNG code; conditional insert | Harder enumerate | Retries on collision |
| Hash(URL) | SHA→Base62 truncate | Deterministic dedup | Leaks cross-user; collision; can’t two shorts same dest |
| Hybrid | Random public; hash optional dedup per owner | Flexible | Complexity |

**Recommendation:** **random (or counter-sharded) unique allocation** + uniqueness check. Hash-only as global ID is a **deal-breaker** for privacy/multi-link needs.

### 3.4 API sketch

```text
POST   /v1/links
  body: { url, custom_alias?, expires_at?, redirect_type?, metadata? }
  headers: Idempotency-Key?

GET    /{code}                  → 302/301 Location
GET    /v1/links/{code}         → metadata (authz)
DELETE /v1/links/{code}         → tombstone
GET    /v1/links/{code}/stats   → analytics (optional)
POST   /v1/admin/takedown
```

### 3.5 Data model

| Field | Notes |
|-------|-------|
| code | PK; short id or alias |
| long_url | Normalized destination |
| owner_id | Optional |
| created_at | UTC |
| expires_at | Nullable |
| status | ACTIVE / DISABLED / DELETED |
| redirect_type | 302/301 |
| version | For mutable destinations |
| flags | password, interstitial, etc. |
| created_via | api/web/partner |

**Alias vs auto code:** store both in same table with `code` unique, or separate alias→code map. Prefer **one unique keyspace** with reserved alias charset rules.

### 3.6 Create flow

```text
1. Authenticate / rate limit
2. Validate URL (scheme, length, block private IPs, unicode normalize)
3. Resolve code:
     - custom: check reserved/profanity/taken
     - auto: allocate unique
4. Conditional put metadata
5. Optionally warm cache
6. Return short URL
7. Async: enqueue safety scan
```

### 3.7 Redirect flow

```text
1. Edge cache lookup by host+code
2. On miss: origin redirect service
3. App cache → metadata store
4. If missing/expired/disabled → 404/410 (cache negative briefly)
5. Else return 302/301 with Location
6. Async emit click event (fire-and-forget / queue)
7. Single-flight on miss to prevent stampedes
```

### 3.8 Expiry & GC

- **Serve path** checks `expires_at <= now` → gone.  
- **Cache** `max-age` ≤ min(policy, remaining TTL).  
- **GC**: Dynamo TTL / sweeper for storage reclaim; grace ok if serve enforces.  
- Extend expiry = owner update + cache purge.

### 3.9 Custom aliases

Rules:

- Charset: e.g. `[a-zA-Z0-9_-]{3,32}`  
- Reserved words: `admin`, `api`, `www`, brand trademarks list  
- Profanity/abuse filters  
- Authenticated-only recommended  
- Higher rate limits scrutiny  
- Optional fee / account age gates (business)

### 3.10 Analytics (optional)

```text
Redirect --> event {code, ts, country?, ua_hash?, ref_hash?} --> stream
         --> real-time counters (Redis HINCR approx)
         --> batch warehouse aggregates
```

**Never** wait on analytics IO in the redirect handler.

Accuracy tiers:

| Tier | Method |
|------|--------|
| MVP | Approximate counters; sampled events |
| Growth | Exact daily rollups async |
| Huge | HyperLogLog uniques; stratified sampling |

### 3.11 Tradeoffs table

| Decision | Option A | Option B | Choose when |
|----------|----------|----------|-------------|
| 302 vs 301 | 302 default | 301 permanent | Mutability / SEO |
| ID gen | Random unique | Counter encode | Enum resistance vs density |
| Dedup by URL | No | Yes per owner | Product choice |
| Mutable destination | Immutable MVP | Update + purge | Marketing needs |
| Analytics sync | Forbidden | Async only | Always async |
| Metadata DB | Dynamo | MySQL/PG | Access patterns |
| Edge compute | CDN only | Edge workers rewrite | Custom logic at edge |

### 3.12 Deal-breakers

1. Putting analytics Dynamo writes on the redirect critical path.  
2. Hash(URL) as the only global short code.  
3. No uniqueness constraint / collision plan.  
4. Ignoring cache for redirects.  
5. Allowing `javascript:` / internal IP destinations.  
6. Sequential short codes without rate limits (enumeration + scraping).  
7. 301 everything while still wanting destination edits.  
8. One global unsharded SQL table at 100×+.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
  Creators -----> API Gateway -----> Create Service -----> Metadata Store
                       |                  |                    ^
                       |                  v                    |
                       |             ID Allocator              |
                       |                  |                    |
                       |                  +-----> Safety Scan (async)
                       |
  Clickers -----> Edge CDN / Anycast
                       |
                 (HIT) return 302
                       |
                 (MISS) Origin Shield --> Redirect Service --> Cache --> Metadata
                                              |
                                              +--> Analytics Queue --> Aggregators
                                              +--> (no blocking IO)
```

### 4.2 Sequence: create

```text
Client        Create API       Allocator      Metadata       Cache
  |              |                |              |             |
  |--POST------>|                |              |             |
  |              |--next code--->|              |             |
  |              |--cond put------------------->|             |
  |              |<--ok-------------------------|             |
  |              |--SET optional-------------->|------------>|
  |<--short url--|                |              |             |
```

### 4.3 Sequence: redirect (miss)

```text
Browser      Edge       Shield      Redirect     Cache      DB
  |           |           |            |           |         |
  |--GET----->|--miss---->|--miss----->|--get----->|--miss-->|
  |           |           |            |<----------|<--------|
  |           |           |            |--SET----- >|         |
  |           |           |            |--302------->|--cache-|
  |<--302-----|<----------|<-----------|           |         |
  |           |           |            |--event async        |
```

### 4.4 Sequence: expiry

```text
Redirect path: if now >= expires_at → 410; set negative cache short
Sweeper: delete/tombstone expired rows in batches
CDN: purge or natural max-age expiry
```

### 4.5 Cell architecture at 100×+

```text
code space partitioned by prefix/hash range
   [Cell 0: a-f*] [Cell 1: g-n*] [Cell 2: o-z*] ...
Global directory optional if code embeds cell hint
Edge routes by key hash to origin pool
Alias registry may be global with careful sharding
```

### 4.6 Hot-key path

```text
Viral code --> Edge POP HIT (primary)
           --> if miss herd: singleflight coalescing at shield
           --> pinned replica / static edge object optional for mega-hot
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Unique `code`** among non-tombstoned (policy on reuse after long grace).  
2. **Create success ⇒ redirect success** (same region) until expiry/disable.  
3. **Expired/disabled ⇒ no redirect** to destination.  
4. **Idempotent create** with Idempotency-Key.  
5. **Redirect never depends on analytics success.**  
6. **Safety disable wins** over cache within purge SLA.

#### 5.1.2 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Metadata outage | Misses fail; edge HITs OK | Multi-AZ; cache TTL balance |
| Cache outage | Load to DB | Bypass; protect with shed |
| CDN outage | Origin absorbs | Autoscaling; load shed; static disaster mode |
| Allocator failure | Creates fail | Multi counter shards / random fallback |
| Stampede | DB melt | Singleflight; shield |
| Poison long_url | Open redirect abuse | Validation; scanning |
| Bad deploy | Wrong redirects | Rapid rollback; canaries |

#### 5.1.3 Durability & backup

- Multi-AZ metadata; PITR.  
- Cross-region replica for DR (async).  
- Test restore of link table samples.  
- Tombstones retained enough for abuse forensics.

#### 5.1.4 Consistency nuances

| Case | Approach |
|------|----------|
| Read-your-write create | Return code; read primary; warm cache; optional sticky |
| Cross-region redirect | Async replication lag ⇒ edge may 404 briefly—minimize via cache fill on create globally or accept rare miss |
| Disable | Conditional update + purge API to CDN + short cache TTL for mutable flags |
| Alias create race | Conditional put; loser retries/409 |

#### 5.1.5 Security

- HTTPS only; HSTS.  
- Scheme allowlist.  
- Block RFC1918/link-local/metadata IPs on create (and re-validate on resolve optional).  
- Rate limit creates & 404s.  
- Phishing reports → takedown SLO.  
- Optional interstitial for new/untrusted links.  
- Referrer-Policy considerations for secret codes.  
- Admin actions audited.

### 5.2 Scalability

#### 5.2.1 Redirect scaling (main game)

```text
DNS anycast → Edge POPs → Origin Shield → Redirect fleet → Cache → Metadata shards
```

Techniques:

- Aggressive caching for immutable ACTIVE links.  
- Tiny responses.  
- Connection coalescing / HTTP/2-3 at edge.  
- Partition metadata by `code`.  
- Hot-key detection → longer edge TTL / pinned objects.  
- Separate create fleet from redirect fleet (noisy neighbor).

#### 5.2.2 Write path scaling

- Stateless create autoscaling.  
- Unique put with retry backoff on collision.  
- Counter shards if using counter IDs: `shard_id | seq`.  
- Alias creates: protect popular dictionary words (hot partitions)—use random salt in internal storage key if needed while serving friendly alias.

#### 5.2.3 Metadata store choice

| Option | When | Tradeoff |
|--------|------|----------|
| DynamoDB | High scale GetItem by code | GSI for “my links” |
| Cassandra | Wide write | Ops |
| Aurora/MySQL | Smaller; rich queries | Shard at growth |
| KV + object for huge URLs | Rare | Complexity |

**Amazon flavor:** DynamoDB `pk=code` + TTL attribute is a natural interview answer; defend with access patterns.

#### 5.2.4 Analytics at scale

| Scale | Approach |
|-------|----------|
| 10× | Kafka/Kinesis + Redis counters |
| 100× | Sample 1–10%; rollup jobs; HLL uniques |
| 1,000× | Edge partial aggregate; tiered storage; drop fields |

**Ownership line:** if analytics threatens redirect SLO, you cut analytics fidelity first.

#### 5.2.5 Multi-region

| Mode | Pattern |
|------|---------|
| MVP | Single-region write; global CDN |
| Growth | Metadata global table / multi-region; regional origins |
| 1,000× | Cells by key hash; create routed to owning cell |

Conflict avoidance: **single-writer home** per code.

#### 5.2.6 Cost controls

| Driver | Control |
|--------|---------|
| Edge requests | Necessary; negotiate; compress headers |
| Origin misses | Hit ratio SLO; shield |
| Storage | Expiry defaults; GC |
| Analytics | Sample; aggregate; retention |
| Scanning | Async; cache reputation by domain |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Team |
|---------|------|
| Redirect path | Edge Link Runtime |
| Create / metadata | Links API |
| ID allocation | Links API |
| Analytics | Measurement |
| Safety / phishing | Trust & Safety |
| Custom domains | Brands (Phase 1.5) |
| Cost / capacity | Owning service team |

#### 5.3.2 Safe evolution

- Immutable codes; additive metadata fields.  
- Redirect header policy versioned.  
- Feature flags for interstitial %.  
- Cache key includes version if destinations mutable.  
- Contract tests for 302 shape.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Redirect availability | 99.99% |
| Redirect edge p99 | < 100 ms |
| Origin miss p99 | < 50 ms |
| Create p99 | < 300 ms |
| Cache hit ratio | > 90–95% |
| Takedown purge | e.g. < 5–15 min global |

Alarms: hit ratio drop, origin 5xx, create collision rate, scan backlog, disable lag, analytics lag (separate).

#### 5.3.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Unique codes; redirect; cache; basic validate |
| 10× | CDN; async analytics; safety hooks; idempotent create |
| 100× | Shards/cells; multi-region reads; alias hardening; shield |
| 1,000× | Keyspace cells; approx analytics; hot-key service; aggressive TTL defaults |

### 5.4 Deep dive: ID allocation designs

**Random unique**

```text
for attempt in 1..K:
  code = base62(random(bits))
  if cond_put(code, record): return code
fail temporary
```

Bits sized for low collision probability under expected n.

**Sharded counter**

```text
code = base62( shard << N | incr(shard) )
```

Add salt/permutation layer to avoid obvious sequences if needed.

### 5.5 Deep dive: cache policy matrix

| State | Edge cache | Notes |
|-------|------------|-------|
| ACTIVE, no expiry | long max-age (e.g. hours) + revalidate | Immutable dest |
| ACTIVE, expiry T | max-age ≤ remaining | Critical |
| DISABLED | negative short / purge | Safety |
| PASSWORD gated | no shared cache | Private |
| 301 | browsers cache hard | Prefer 302 if edits |

### 5.6 Deep dive: URL validation

```text
parse URL
require scheme in {http, https}
reject credentials in URL optional policy
resolve host → block private ranges (careful with DNS rebinding: validate at create; optional safe fetch)
max length; charset normalize
optional: IDNA encode host
```

DNS rebinding: don’t SSRF-fetch the destination on create unless needed for scanning—and if you do, use a locked-down fetcher.

### 5.7 Deep dive: custom alias contention

Popular aliases (`love`, `covid`, `amzn`) are hot:

- Pre-reserve brand trademarks.  
- For availability check, use cached bloom/negative + conditional put.  
- Throttle unauthenticated alias probes (enumeration of dictionary).

### 5.8 Deep dive: mutable destinations

If product requires edits:

```text
record.version++
long_url = new
cache key includes version OR purge on update
prefer 302
analytics continue on same code
```

Immutable MVP is simpler—say so.

### 5.9 Testing & resilience

- Uniqueness under parallel creates.  
- Expiry boundary tests (± skew).  
- Chaos: kill analytics; redirects healthy.  
- Stampede test on single code.  
- Property: disabled never redirects.  
- Fuzz URL validator.  
- Load test origin miss path separately from edge HIT.

### 5.10 Comparison: TinyURL vs Pastebin (pivot)

| | TinyURL | Pastebin |
|--|---------|----------|
| Payload | URL string small | Text body large |
| Hot path | Redirect | Fetch body |
| Storage | Metadata KV | Metadata + object store |
| Cache | Location header | Body bytes |
| Abuse | Phishing redirects | Malware content hosting |

Shared: short IDs, expiry, CDN, abuse, read-heavy.

### 5.11 Amazon leadership connection (brief)

- **Customer Obsession:** fast redirects; don’t break shared links.  
- **Ownership:** hit ratio, phishing SLAs, cost/1M redirects.  
- **Frugality:** sample analytics before buying more warehouses.  
- **Are Right, A Lot:** 302 default vs 301 debate with data.  
- **Deliver Results:** viral event is an expected load test.

---

## 6. Wrap-Up

### 6.1 30-second recap

URL shortener = **unique code allocation** + **metadata KV** + **edge-cached redirects** as the sacred path. Custom aliases are a contended namespace with auth/abuse rules. Expiry/tombstones enforced on serve with cache TTL alignment. Analytics are **async and approximate at scale**. Scale via CDN first, then sharded metadata/cells; never let measurement or scanning block redirects.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Why |
|----------|--------|-----|
| ID strategy | Unique random/counter | Not hash-only |
| 302 vs 301 | 302 default | Flexibility |
| Analytics fidelity | Async approx | Protect SLO |
| Immutable vs edit | Immutable MVP | Cache simplicity |
| Alias freedom | Auth + filters | Abuse |

### 6.3 Risks & follow-ups

- Phishing liability & legal takedown  
- Custom domains / SSL at scale  
- Exact analytics SKU  
- Password-gated links  
- Geo-routed destinations  
- QR & campaign tooling

### 6.4 What “good” looks like

- Solid **ID space math** and uniqueness story  
- **Redirect path** isolation from analytics  
- **Cache/TTL/expiry** coherence  
- Progressive **10×/100×/1,000×** without magic  
- Abuse & ownership called out

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q1 | 301 or 302? | 302 default; 301 opt-in |
| Q2 | Idempotent create? | Yes with key |
| Q3 | Dedup same long URL? | Product choice; not global forced |
| Q4 | Max URL length? | Hard cap |
| Q5 | Unicode aliases? | Careful; often ASCII only MVP |
| Q6 | Preview pages? | Optional safety |
| Q7 | Bulk API? | Partner tier |
| Q8 | QR? | Derived; not hot path |
| Q9 | Password links? | AuthZ before 302 |
| Q10 | Teams/orgs? | Later ACL |
| Q11 | Vanity domains? | Phase 1.5 |
| Q12 | SLA on purge? | Explicit minutes |

### 7.2 IDs & aliases (Q13–Q28)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q13 | Why not auto-increment web-visible? | Enumeration |
| Q14 | Base62 vs Base64 URL? | Prefer URL-safe alphabet |
| Q15 | How long codes? | Birthday + uniqueness; 7–8 typical |
| Q16 | Hash(URL)? | Cross-user issues; collisions |
| Q17 | Snowflake IDs? | Good; encode to Base62 |
| Q18 | Collision handling? | Retry / conditional put |
| Q19 | Custom alias races? | Conditional put 409 |
| Q20 | Reserved words? | Blocklist |
| Q21 | Can codes be reused after delete? | Long grace; prefer never for abuse |
| Q22 | Predictable counters? | Permute / salt |
| Q23 | Separate alias table? | Optional; unique keyspace simpler |
| Q24 | Case sensitivity? | Decide; often case-sensitive codes |
| Q25 | Homoglyph aliases? | Reject confusables |
| Q26 | Length limits alias? | Yes |
| Q27 | Brand trademark squatting? | Policy + takedown |
| Q28 | Secret unlisted links? | Longer entropy codes |

### 7.3 Redirect & caching (Q29–Q44)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q29 | What’s on critical path? | Resolve + 302 only |
| Q30 | Where to cache? | Edge + app |
| Q31 | Stampede? | Singleflight + shield |
| Q32 | Negative caching? | Short TTL |
| Q33 | Cache vs expiry? | max-age bound |
| Q34 | Hot key? | Edge HIT; pin |
| Q35 | Header size? | Keep Location clean |
| Q36 | HSTS/HTTPS? | Yes |
| Q37 | HTTP/3 benefits? | Edge connections |
| Q38 | Origin shield role? | Collapse misses |
| Q39 | Multi-CDN? | Optional enterprise |
| Q40 | Cache purge API? | On disable/update |
| Q41 | ETag? | Less relevant for 302 |
| Q42 | Browser 301 cache pain? | Why 302 default |
| Q43 | Geo latency? | Anycast POPs |
| Q44 | Fail open or closed on DB miss? | Closed for unknown; edge HIT still open |

### 7.4 Expiry, mutation, GC (Q45–Q56)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q45 | Who enforces expiry? | Serve path first |
| Q46 | Dynamo TTL lag? | Still check expires_at |
| Q47 | Extend TTL? | Update + purge |
| Q48 | Mutable destination? | Version + purge; 302 |
| Q49 | Soft delete? | Tombstone status |
| Q50 | GC orphans? | Batch jobs |
| Q51 | Legal hold? | status=hold |
| Q52 | Clock skew? | Absolute UTC |
| Q53 | Default TTL business? | Cost control lever |
| Q54 | Never-expire tier? | Paid |
| Q55 | Cache poison after update? | Purge + version |
| Q56 | Bulk expire campaign? | Admin job |

### 7.5 Analytics (Q57–Q64)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q57 | Exact click count? | Costly; approx MVP |
| Q58 | Unique visitors? | HLL |
| Q59 | Real-time dashboard? | Redis counters |
| Q60 | Lossy events OK? | Yes if stated |
| Q61 | Privacy? | Hash UA; careful IP retention |
| Q62 | Bot traffic? | Filter heuristics |
| Q63 | Backfill? | From sampled raw if kept |
| Q64 | Analytics outage? | Redirects continue |

### 7.6 Abuse, safety, scale (Q65–Q76)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q65 | Phishing? | Scan + report + takedown |
| Q66 | Malware URLs? | Blocklists; disable |
| Q67 | Open redirector reputation? | Interstitial; partner reputation |
| Q68 | SSRF? | Scheme + IP checks |
| Q69 | Spam create farms? | Rate limit; captcha; reputation |
| Q70 | Shard key? | code |
| Q71 | Multi-region write? | Single home per code |
| Q72 | Cell migration? | Dual read; freeze range |
| Q73 | Cost explosion viral? | Edge absorbs; celebrate HIT |
| Q74 | Metadata hot partition? | High cardinality codes |
| Q75 | Alias hot keys? | Cache; reserved list |
| Q76 | Observability top codes? | Privacy-aware sampling |

### 7.7 Behavioral / Amazon (Q77–Q80)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q77 | Viral link melts origin | Shield/singleflight; raise edge TTL; postmortem hit ratio |
| Q78 | Phishing on your domain | Fast takedown; interstitial expand; partner with Trust |
| Q79 | Analytics vs latency conflict | Cut fidelity; protect redirect SLO |
| Q80 | 301 vs 302 debate with PM | Explain browser cache; recommend 302 unless permanent |

---

## 8. Appendices

### Appendix A — Status cheat sheet

| Status | Redirect? |
|--------|-----------|
| ACTIVE | Yes if unexpired |
| DISABLED | No (410/404) |
| DELETED | No |
| PENDING_SCAN | Policy: allow with interstitial or hold |

### Appendix B — Example metadata item

```json
{
  "code": "aB3xY9",
  "long_url": "https://example.com/path?q=1",
  "owner_id": "u_123",
  "status": "ACTIVE",
  "redirect_type": 302,
  "created_at": "2026-08-06T01:00:00Z",
  "expires_at": "2026-09-06T01:00:00Z",
  "version": 1,
  "flags": {"interstitial": false}
}
```

### Appendix C — HTTP redirect example

```text
HTTP/2 302 Found
Location: https://example.com/path?q=1
Cache-Control: public, max-age=300
Referrer-Policy: no-referrer
```

### Appendix D — Create request/response

```json
// POST /v1/links
{
  "url": "https://example.com/very/long",
  "custom_alias": "my-sale",
  "expires_at": "2026-09-06T00:00:00Z"
}

// 201
{
  "code": "my-sale",
  "short_url": "https://short.example/my-sale",
  "expires_at": "2026-09-06T00:00:00Z"
}
```

### Appendix E — ID length worksheet

```text
alphabet = 62
length = ?
S = 62^length
expected n = creates_per_day * days
ensure uniqueness via cond_put regardless
enumeration hardness ≈ S for secret links
```

### Appendix F — Error codes

| Code | Meaning |
|------|---------|
| INVALID_URL | Validation fail |
| ALIAS_TAKEN | 409 |
| ALIAS_RESERVED | 403 |
| IDEMPOTENCY_MISMATCH | 409 |
| NOT_FOUND | Unknown code |
| GONE | Expired/disabled |
| RATE_LIMITED | 429 |
| UNSAFE_URL | Blocked by policy |

### Appendix G — Anti-patterns

1. Sync analytics before 302.  
2. Hash-only global IDs.  
3. No uniqueness check.  
4. Caching expired links for hours.  
5. Allowing non-http(s) schemes.  
6. Sequential public IDs without controls.  
7. Shared DB with Pastebin bodies (wrong abstraction).  
8. 301 + frequent destination edits.

### Appendix H — Capacity worksheet

```text
creates/day = ____
redirects/day = ____
peak redirect QPS = ____
edge hit ratio = ____
origin QPS = peak * (1 - hit)
metadata size/day = ____
analytics sample rate = ____
code length = ____
```

### Appendix I — 45-minute timebox

| Min | Focus |
|-----|-------|
| 0–5 | FR/NFR; 302; abuse |
| 5–12 | QPS + ID space math |
| 12–25 | HLD; create vs redirect |
| 25–35 | Cache/expiry/hot key OR IDs |
| 35–42 | Analytics async; 10×/100×/1,000× |
| 42–45 | Wrap ownership/trust |

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| Code / slug | Short path key |
| Alias | Custom code |
| Tombstone | Disabled/deleted marker |
| Origin shield | Intermediate cache collapsing misses |
| Singleflight | Coalesce concurrent fills |
| HLL | HyperLogLog approximate uniques |
| Open redirect | Abuse of redirector trust |
| Capability URL | Knowledge of URL grants access |

### Appendix K — Ownership RACI

| Activity | Redirect | Links API | Measurement | Trust |
|----------|----------|-----------|-------------|-------|
| 302 latency | A/R | C | I | I |
| Create uniqueness | C | A/R | I | C |
| Click pipeline | C | I | A/R | I |
| Phishing takedown | R | C | I | A |
| Cost hit ratio | A | C | C | I |

### Appendix L — Progressive scale one-pager

| Scale | Snapshot |
|-------|----------|
| 1× | API + DB + Redis; one region |
| 10× | CDN; async analytics; safety |
| 100× | Sharded metadata; multi-region; shield |
| 1,000× | Cells; approx analytics; hot-key platform |

### Appendix M — Cache key sketch

```text
key = "redir:v1:" + host + ":" + code
val = { status, location, exp, redir_type, version }
```

### Appendix N — Minimal threat model

| Threat | Mitigation |
|--------|------------|
| Phishing | Scan, report, takedown, interstitial |
| Malware | Blocklists |
| Enumeration | Long codes; 404 rate limits |
| SSRF | Validation |
| Spam SEO | Rate limits; account reputation |
| Cache poisoning | Signed origin; TLS |

### Appendix O — Redirect pseudocode

```text
function redirect(code):
  rec = cache.get(code) or db.get(code)
  if rec is None: return 404
  if rec.status != ACTIVE: return 410
  if rec.expires_at and now >= rec.expires_at: return 410
  emit_async_click(code)
  return Response(rec.redirect_type, Location=rec.long_url)
```

### Appendix P — Allocator pseudocode

```text
function alloc_code():
  for i in 1..8:
    c = base62(random(48 bits))  # tune bits
    if db.cond_put(c, draft): return c
  throw TemporaryFailure
```

### Appendix Q — Analytics event (sample)

```json
{
  "code": "aB3xY9",
  "ts": "2026-08-06T01:02:03Z",
  "country": "US",
  "ua_bucket": "mobile",
  "sample": true
}
```

### Appendix R — Interview “say this” (60 seconds)

> “I’d split **create** and **redirect** fleets. Codes come from **random or sharded counters** with **conditional puts**—not global hash(URL). Redirects are served from **edge cache** with TTL bounded by expiry; origin misses go cache→KV with **singleflight**. Analytics are **async and lossy-tolerant**. Custom aliases need auth, blocklists, and uniqueness. At scale we shard by code, add shields, and cut analytics fidelity before ever risking redirect SLO. Success is unique correct mappings, fast 302s, and a trust path for takedowns.”

### Appendix S — Related systems map

```text
Create API --> Metadata KV --> (optional) Alias rules
Redirect <-- Edge CDN <-- Metadata + Cache
   |
   +--> Analytics stream --> Counters / Warehouse
   +--> Trust & Safety
```

### Appendix T — Chaos drill list

1. Kill analytics cluster during viral event.  
2. Metadata AZ failure.  
3. Stampede on one code (cache flush).  
4. Disable link; measure purge lag.  
5. Collision storm on short code length (misconfig).  
6. CDN POP outage.  
7. Clock skew near expiry.  
8. Safety scanner backlog spike.

### Appendix U — Create validation checklist

- [ ] Scheme http/https  
- [ ] Length cap  
- [ ] Normalize  
- [ ] Private IP block  
- [ ] Alias charset + reserved  
- [ ] Rate limit  
- [ ] Idempotency  
- [ ] Unique put  

### Appendix V — Comparison checklist vs common designs

| Topic | Weak answer | Strong answer |
|-------|-------------|---------------|
| IDs | MD5 truncate | Unique alloc + math |
| Scale | “add Redis” | Edge → shield → shard cells |
| Analytics | “store every click in SQL” | Async approx + sampling |
| Expiry | “cron only” | Serve-path enforce |
| Abuse | shrug | validation + takedown SLO |

---

*End of TinyURL / URL shortener system design (Amazon SDE III style).*
